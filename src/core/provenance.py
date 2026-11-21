"""Provenance: what we knew, when we knew it, and where it came from.

Three rules this module enforces:

1. **Never lose an original value.** Arbitrary fixes to a historical record go
   through :func:`record_revision`, which writes the old value, the new value,
   the observation time and the source of the change. Nothing is silently
   rewritten in place.
2. **Never present a claim without a source.** :class:`Provenance` is attached
   to every extracted record, feature snapshot and reported result.
3. **Never confuse synthetic with real.** The database layer refuses to write a
   synthetic-status row into the live tree (see ``src.core.validation``).
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Mapping

from src.core.validation import ValidationError


def utcnow() -> str:
    """ISO-8601 UTC timestamp with second resolution - the platform's clock."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def content_hash(payload: Any) -> str:
    """Deterministic hash of any JSON-serialisable payload."""
    blob = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Provenance:
    """Where a datum came from and how much we trust it."""

    source_id: str
    source_url: str | None
    fetched_at: str
    dataset: str
    verification_status: str
    authority: int = 0
    http_status: int | None = None
    content_hash: str | None = None
    notes: str = ""

    def validate(self) -> None:
        if self.dataset == "live" and not self.source_url:
            raise ValidationError(
                f"live record from source '{self.source_id}' has no source_url; "
                "provenance is mandatory for real data"
            )
        if self.dataset != "live" and not self.verification_status.startswith("synthetic"):
            raise ValidationError(
                f"synthetic provenance required for dataset '{self.dataset}', "
                f"got '{self.verification_status}'"
            )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Revision:
    """An observed change to an already-stored historical value."""

    record_id: str
    field_name: str
    old_value: Any
    new_value: Any
    observed_at: str
    source_id: str
    source_url: str | None
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


FAILED_STATUSES = {"blocked", "error", "unreachable", "blocked_egress"}
OK_STATUSES = {"ok", "verified", "unverified_scrape", "synthetic_control", "partial"}


def record_revision(conn, revision: Revision) -> None:
    """Persist a revision row. Callers must pass an open SQLite connection."""
    conn.execute(
        """
        INSERT INTO result_revisions
            (record_id, field_name, old_value, new_value, observed_at,
             source_id, source_url, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            revision.record_id,
            revision.field_name,
            json.dumps(revision.old_value, default=str),
            json.dumps(revision.new_value, default=str),
            revision.observed_at,
            revision.source_id,
            revision.source_url,
            revision.reason,
        ),
    )


def environment_fingerprint() -> dict[str, Any]:
    """Runtime description stamped into every research report.

    A result produced on a different Python/NumPy version is not, strictly, the
    same result; recording this makes that impossible to overlook.
    """
    versions: dict[str, str] = {"python": sys.version.split()[0], "platform": platform.platform()}
    for mod_name in ("numpy", "pandas", "scipy", "sklearn", "statsmodels", "matplotlib"):
        try:
            module = __import__(mod_name)
            versions[mod_name] = getattr(module, "__version__", "unknown")
        except ImportError:  # pragma: no cover
            versions[mod_name] = "not-installed"
    return versions


def stamp(record: Mapping[str, Any], **extra: Any) -> dict[str, Any]:
    """Add provenance fields to a record without mutating the input."""
    out = dict(record)
    out.update({"recorded_at": utcnow(), **extra})
    return out


class ExtractionLedger:
    """Tracks what each extraction attempt actually achieved.

    Deliberately blunt: a failed fetch records the failure, the exception type
    and the URL. Reports read from this ledger rather than from prose.
    """

    def __init__(self, conn, market_id: str, source_id: str, config_fingerprint: str):
        self.conn = conn
        self.market_id = market_id
        self.source_id = source_id
        self.config_fingerprint = config_fingerprint
        self.run_id: int | None = None

    def __enter__(self) -> "ExtractionLedger":
        cur = self.conn.execute(
            """
            INSERT INTO extraction_runs
                (market_id, source_id, started_at, status, config_fingerprint)
            VALUES (?, ?, ?, 'running', ?)
            """,
            (self.market_id, self.source_id, utcnow(), self.config_fingerprint),
        )
        self.run_id = int(cur.lastrowid)
        self.conn.commit()
        return self

    def record_page(self, url: str, http_status: int | None, ok: bool,
                    byte_size: int = 0, parse_status: str = "pending",
                    raw_path: str | None = None, body: str | None = None,
                    notes: str = "") -> None:
        self.conn.execute(
            """
            INSERT INTO source_records
                (run_id, source_id, market_id, url, fetched_at, http_status,
                 content_hash, byte_size, parse_status, raw_path, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.run_id, self.source_id, self.market_id, url, utcnow(), http_status,
                content_hash(body) if body is not None else None, byte_size,
                parse_status, raw_path, notes,
            ),
        )
        self.conn.commit()

    def finish(self, status: str, *, pages_requested: int = 0, pages_ok: int = 0,
               pages_failed: int = 0, records_seen: int = 0, records_inserted: int = 0,
               records_revised: int = 0, error_text: str = "") -> None:
        self.conn.execute(
            """
            UPDATE extraction_runs
               SET finished_at = ?, status = ?, pages_requested = ?, pages_ok = ?,
                   pages_failed = ?, records_seen = ?, records_inserted = ?,
                   records_revised = ?, error_text = ?
             WHERE run_id = ?
            """,
            (
                utcnow(), status, pages_requested, pages_ok, pages_failed,
                records_seen, records_inserted, records_revised, error_text, self.run_id,
            ),
        )
        self.conn.commit()

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is not None:
            self.finish("error", error_text=f"{exc_type.__name__}: {exc}")
            return False
        if self.run_id is not None:
            row = self.conn.execute(
                "SELECT status FROM extraction_runs WHERE run_id = ?", (self.run_id,)
            ).fetchone()
            if row and row[0] == "running":
                self.finish("ok")
        return False
