"""SQLite connection management.

Why SQLite: one file per market gives hard physical isolation, the whole
database is a single copyable artefact, and the workload (tens of thousands of
rows, single-writer batch jobs) is exactly what SQLite is good at. PostgreSQL
would add operational cost with no analytical benefit at this scale; the
:class:`DatabaseManager` interface is the seam where such a swap would happen.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from src.core.configuration import Config
from src.core.logging import get_logger
from src.core.provenance import utcnow
from src.storage.migrations import apply_migrations
from src.storage.schema import REQUIRED_TABLES

log = get_logger(__name__)


def _connect(path: Path, *, read_only: bool = False) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    if read_only:
        uri = f"file:{path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, timeout=15.0)
    else:
        conn = sqlite3.connect(str(path), timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 15000")
    if not read_only:
        # WAL gives us crash-safe concurrent readers next to the batch writer.
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
    return conn


class DatabaseManager:
    """Owns connection lifecycle, schema creation and integrity checks."""

    def __init__(self, config: Config):
        self.config = config
        self.dataset = config.dataset.name

    # -- paths ------------------------------------------------------------
    def path_for(self, market_id: str) -> Path:
        return self.config.database_path(market_id)

    def all_paths(self) -> dict[str, Path]:
        return {m: self.path_for(m) for m in self.config.market_order}

    # -- creation ---------------------------------------------------------
    def initialise(self, market_id: str, *, rebuild: bool = False) -> Path:
        """Create (or migrate) one market database. Idempotent."""
        market = self.config.market(market_id)
        path = self.path_for(market.market_id)
        if rebuild and path.exists():
            backup = path.with_suffix(f".db.bak-{utcnow().replace(':', '')}")
            path.rename(backup)
            log.warning("rebuild requested: moved existing %s to %s", path.name, backup.name)
        conn = _connect(path)
        try:
            apply_migrations(conn)
            self._record_market_identity(conn, market.market_id)
        finally:
            conn.close()
        log.info("initialised %s at %s", market.market_id, path)
        return path

    def initialise_all(self, *, rebuild: bool = False) -> dict[str, Path]:
        return {m: self.initialise(m, rebuild=rebuild) for m in self.config.market_order}

    def _record_market_identity(self, conn: sqlite3.Connection, market_id: str) -> None:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS database_identity ("
            " key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL)"
        )
        rows = {
            "market_id": market_id,
            "dataset": self.dataset,
            "schema_version": "3",
            "project_version": str(self.config.project.get("code_version", "")),
            "config_fingerprint": self.config.fingerprint(),
        }
        for key, value in rows.items():
            conn.execute(
                "INSERT INTO database_identity (key, value, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                (key, value, utcnow()),
            )
        conn.commit()

    # -- sessions ---------------------------------------------------------
    @contextmanager
    def session(self, market_id: str, *, read_only: bool = False) -> Iterator[sqlite3.Connection]:
        path = self.path_for(market_id)
        if not read_only and not path.exists():
            raise FileNotFoundError(
                f"database for market '{market_id}' does not exist at {path}. "
                f"Run: python -m src.cli.main init --dataset {self.dataset}"
            )
        if read_only and not path.exists():
            raise FileNotFoundError(f"database for market '{market_id}' not found at {path}")
        conn = _connect(path, read_only=read_only)
        try:
            yield conn
            if not read_only:
                conn.commit()
        except Exception:
            if not read_only:
                conn.rollback()
            raise
        finally:
            conn.close()

    # -- diagnostics ------------------------------------------------------
    def integrity_check(self, market_id: str) -> dict[str, object]:
        with self.session(market_id, read_only=True) as conn:
            pragma = conn.execute("PRAGMA integrity_check").fetchone()[0]
            tables = {
                r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            missing = [t for t in REQUIRED_TABLES if t not in tables]
            counts = {}
            for table in REQUIRED_TABLES:
                if table in tables:
                    counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        return {
            "market_id": market_id,
            "path": str(self.path_for(market_id)),
            "pragma": pragma,
            "missing_tables": missing,
            "row_counts": counts,
            "ok": pragma == "ok" and not missing,
        }

    def exists(self, market_id: str) -> bool:
        return self.path_for(market_id).exists()


def connect_path(path: Path, *, read_only: bool = False) -> sqlite3.Connection:
    """Direct connection helper for tooling that manages its own paths."""
    return _connect(path, read_only=read_only)
