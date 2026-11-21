"""Migration runner.

SQLite has no ``ALTER TABLE ... IF NOT EXISTS``, so migrations are applied
idempotently by recording each version in ``database_migrations`` and skipping
versions already present. Applying migrations twice must be a no-op - the test
suite asserts this.
"""

from __future__ import annotations

import sqlite3

from src.core.logging import get_logger
from src.storage.schema import MIGRATIONS, SCHEMA_VERSION, VIEWS

log = get_logger(__name__)

_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS database_migrations (
    version     INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    applied_at  TEXT NOT NULL
)
"""


def current_version(conn: sqlite3.Connection) -> int:
    conn.execute(_TABLE_DDL)
    row = conn.execute("SELECT MAX(version) FROM database_migrations").fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def apply_migrations(conn: sqlite3.Connection, target: int = SCHEMA_VERSION) -> list[int]:
    """Apply every pending migration up to ``target``. Returns applied versions."""
    from src.core.provenance import utcnow

    conn.execute(_TABLE_DDL)
    applied = current_version(conn)
    newly: list[int] = []
    for version, description, sql in MIGRATIONS:
        if version <= applied or version > target:
            continue
        log.debug("applying migration v%d: %s", version, description)
        conn.executescript(sql)
        conn.execute(
            "INSERT INTO database_migrations (version, description, applied_at) VALUES (?, ?, ?)",
            (version, description, utcnow()),
        )
        conn.commit()
        newly.append(version)
    conn.executescript(VIEWS)
    conn.commit()
    if newly:
        log.info("migrations applied: %s (now v%d)", newly, current_version(conn))
    return newly


def assert_schema_current(conn: sqlite3.Connection) -> None:
    version = current_version(conn)
    if version < SCHEMA_VERSION:
        raise RuntimeError(
            f"database schema is v{version}, expected v{SCHEMA_VERSION}; run `init --all`"
        )


def table_names(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    return [r[0] for r in rows]
