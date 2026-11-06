"""Backup and snapshot helpers.

The rule "never destroy original data" is only credible if there is a copy.
``snapshot`` uses SQLite's online backup API, which is safe while a writer holds
the database.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from src.core.logging import get_logger
from src.core.provenance import utcnow
from src.storage.database_manager import connect_path

log = get_logger(__name__)


def snapshot(db_path: Path, backup_dir: Path, label: str = "manual") -> Path:
    """Copy a database to ``backup_dir`` using the SQLite backup API."""
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(db_path)
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = utcnow().replace(":", "").replace("-", "")
    dest = backup_dir / f"{db_path.stem}-{label}-{stamp}.db"
    src = connect_path(db_path, read_only=True)
    dst = sqlite3.connect(str(dest))
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    log.info("snapshot %s -> %s (%.2f MB)", db_path.name, dest.name,
             dest.stat().st_size / 1_048_576)
    return dest


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(db_paths: dict[str, Path], manifest_path: Path,
                   extra: dict[str, Any] | None = None) -> Path:
    """Commit-able record of exactly which data snapshot produced the results.

    Databases themselves are git-ignored (they are large and re-derivable); the
    manifest is what makes a reported number reproducible.
    """
    payload: dict[str, Any] = {"generated_at": utcnow(), "databases": {}, "extra": extra or {}}
    for market_id, path in db_paths.items():
        path = Path(path)
        entry: dict[str, Any] = {"path": str(path), "exists": path.exists()}
        if path.exists():
            entry["sha256"] = file_digest(path)
            entry["bytes"] = path.stat().st_size
            conn = connect_path(path, read_only=True)
            try:
                for table in ("historical_results", "predictions", "method_results",
                              "backtest_results"):
                    try:
                        entry[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    except sqlite3.Error:
                        entry[table] = None
            finally:
                conn.close()
        payload["databases"][market_id] = entry

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    log.info("wrote manifest %s", manifest_path)
    return manifest_path
