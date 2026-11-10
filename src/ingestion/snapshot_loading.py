"""Load user-supplied chart snapshots into the LIVE market databases.

The parsing and reconciliation live in :mod:`src.ingestion.chart_snapshot`; this
module is the part that touches storage, and it is deliberately strict:

* every row is attributed to the URL the snapshot was saved from, with the snapshot's
  own `Date:` header as the observation timestamp and the MHTML file's SHA-256 in the
  provenance ledger;
* the raw snapshots are copied into `data/raw/snapshots/<market>/` so the database can
  be rebuilt from them, and a SHA-256 manifest of those files is written;
* nothing is silently dropped: missing days, repaired week labels and panna-vs-jodi
  contradictions are written to `data_quality` and to a reconciliation audit file.

The resulting rows carry ``verification_status = "unverified_scrape"`` - single-source
scraped records that have not been independently confirmed against a second provider.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.core.configuration import Config
from src.core.logging import get_logger
from src.core.provenance import ExtractionLedger, utcnow
from src.ingestion.chart_snapshot import (
    Day,
    SnapshotFile,
    parse_jodi_html,
    parse_panel_html,
    read_snapshot,
    reconcile,
)
from src.storage.market_database import MarketDatabase

log = get_logger(__name__)

#: keywords that identify each page inside a directory of saved snapshots
KIND_KEYWORDS = {
    "jodi": ("jodi",),
    "panel": ("panel",),
}


def discover_snapshots(directory: str | Path) -> dict[str, dict[str, Path]]:
    """Find the four snapshots in ``directory`` and group them by market and kind."""
    directory = Path(directory)
    found: dict[str, dict[str, Path]] = {}
    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".txt", ".html", ".mhtml", ".mht"}:
            continue
        lowered = path.name.lower()
        kind = next((k for k, words in KIND_KEYWORDS.items()
                     if any(word in lowered for word in words)), None)
        if kind is None:
            continue
        if "main" in lowered and "bazar" in lowered:
            market = "main_bazar"
        elif "kalyan morning" in lowered:
            market = "kalyan_morning"
        elif "milan morning" in lowered:
            market = "milan_morning"
        elif "sridevi" in lowered:
            market = "sridevi"
        elif "kalyan" in lowered:
            market = "kalyan"
        else:
            continue
        found.setdefault(market, {})[kind] = path
    return found


@dataclass
class ImportReport:
    market_id: str
    dataset: str
    rows_built: int
    inserted: int
    revised: int
    unchanged: int
    rejected: int
    errors: list[str]
    missing_days: int
    conflicts: int
    audit_path: str | None = None
    raw_paths: list[str] = field(default_factory=list)
    run_ids: list[int] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "market_id": self.market_id, "dataset": self.dataset,
            "rows_built": self.rows_built, "inserted": self.inserted,
            "revised": self.revised, "unchanged": self.unchanged,
            "rejected": self.rejected, "errors": self.errors[:20],
            "missing_days": self.missing_days, "jodi_conflicts": self.conflicts,
            "audit_path": self.audit_path, "raw_paths": self.raw_paths,
            "run_ids": self.run_ids,
        }


def _copy_raw(snapshot: SnapshotFile, raw_dir: Path, market_id: str) -> Path:
    """Keep the snapshot itself next to the database, named by its hash."""
    target_dir = raw_dir / market_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{snapshot.kind}_{snapshot.sha256[:12]}.mhtml"
    if not target.exists():
        shutil.copy2(snapshot.path, target)
    return target


def _row_from_day(day: Day, *, market_id: str, source_id: str, panel: SnapshotFile,
                  jodi: SnapshotFile, label: str) -> dict[str, Any]:
    flags: list[str] = []
    if day.open_panna is None or day.close_panna is None:
        flags.append("panna_missing")
    if day.panel_jodi and day.jodi and day.panel_jodi != day.jodi:
        flags.append("printed_jodi_contradicts_panna")
    if day.jodi_chart_jodi and day.jodi and day.jodi_chart_jodi != day.jodi:
        flags.append("jodi_chart_contradicts_panna")
    if not day.jodi_chart_jodi:
        flags.append("jodi_chart_silent")

    payload = {
        "week_label": label,
        "panel_cells": {"open": day.open_panna, "jodi": day.panel_jodi,
                        "close": day.close_panna},
        "jodi_chart_cell": day.jodi_chart_jodi,
        "panna_arithmetic": day.jodi,
        "status": day.status,
        "notes": day.notes,
        "panel_snapshot": {"url": panel.url, "saved_at": panel.saved_at,
                           "sha256": panel.sha256},
        "jodi_snapshot": {"url": jodi.url, "saved_at": jodi.saved_at,
                          "sha256": jodi.sha256},
    }
    return {
        "market_id": market_id,
        "result_date": day.date.isoformat(),
        "open_panna": day.open_panna,
        "close_panna": day.close_panna,
        "open_ank": day.open_ank,
        "close_ank": day.close_ank,
        "jodi": day.jodi,
        "source_id": source_id,
        "source_url": panel.url,
        "source_timestamp": panel.saved_at,
        "verification_status": "unverified_scrape",
        "raw_payload": json.dumps(payload, separators=(",", ":"), sort_keys=True),
        "notes": ";".join(flags) if flags else None,
    }


def import_market(config: Config, market_id: str, *, jodi_path: str | Path,
                  panel_path: str | Path, raw_dir: str | Path | None = None,
                  audit_dir: str | Path | None = None,
                  rebuild: bool = False) -> ImportReport:
    """Reconcile the two snapshots of ``market_id`` and store the result."""
    if config.dataset.name != "live":
        raise ValueError("snapshots hold real records and may only be loaded into the "
                         "live dataset, not into a control world")

    panel_snap = read_snapshot(panel_path, kind="panel")
    jodi_snap = read_snapshot(jodi_path, kind="jodi")
    panel = parse_panel_html(panel_snap.html)
    jodi = parse_jodi_html(jodi_snap.html)
    days, audit = reconcile(market_id, panel, jodi)
    audit["sources"] = [
        {"kind": "panel", "path": str(panel_snap.path), "url": panel_snap.url,
         "saved_at": panel_snap.saved_at, "sha256": panel_snap.sha256,
         "byte_size": panel_snap.byte_size, "title": panel_snap.title},
        {"kind": "jodi", "path": str(jodi_snap.path), "url": jodi_snap.url,
         "saved_at": jodi_snap.saved_at, "sha256": jodi_snap.sha256,
         "byte_size": jodi_snap.byte_size, "title": jodi_snap.title},
    ]

    source_id = str(config.market(market_id).primary_source)
    db = MarketDatabase(config, market_id)
    db.manager.initialise(market_id, rebuild=rebuild)

    label_by_date = {}
    for week in panel.weeks:
        for index, _cell in enumerate(week.cells):
            label_by_date[week.start + dt.timedelta(days=index)] = week.label_raw

    rows = [
        _row_from_day(day, market_id=market_id, source_id=source_id, panel=panel_snap,
                      jodi=jodi_snap, label=label_by_date.get(day.date, ""))
        for day in days if day.usable
    ]

    raw_paths: list[str] = []
    if raw_dir is not None:
        for snapshot in (panel_snap, jodi_snap):
            raw_paths.append(str(_copy_raw(snapshot, Path(raw_dir), market_id)))

    outcome = db.upsert_results(rows)

    run_ids: list[int] = []
    with db.session() as conn:
        for snapshot, kind in ((panel_snap, "panel"), (jodi_snap, "jodi")):
            with ExtractionLedger(conn, market_id, source_id, config.fingerprint()) as run:
                run.record_page(
                    snapshot.url, None, True,
                    byte_size=snapshot.byte_size,
                    parse_status="parsed",
                    raw_path=raw_paths[0 if kind == "panel" else 1] if raw_paths else None,
                    body=snapshot.html,
                    notes=(f"user-supplied MHTML snapshot ({kind} chart) saved at "
                           f"{snapshot.saved_at}; sha256={snapshot.sha256}"),
                )
                run.finish("ok", pages_requested=1, pages_ok=1, pages_failed=0,
                           records_seen=(panel.n_cells if kind == "panel"
                                         else len(jodi.rows) * len(jodi.weekdays)),
                           records_inserted=len(rows), records_revised=outcome.revised)
                if run.run_id is not None:
                    run_ids.append(run.run_id)

    # Quality rows: the reconciliation itself is a check, and it is recorded even when
    # everything agrees, so a later report can show the rate rather than assert it.
    quality = [
        {"check_name": "snapshot_source_agreement", "severity": "info", "passed": True,
         "metric_name": "days_with_both_pages",
         "metric_value": float(audit["n_usable"]),
         "detail": f"panel and jodi pages agree on "
                   f"{audit['n_usable'] - audit['n_conflicts']} of {audit['n_usable']} usable days"},
        {"check_name": "snapshot_panna_jodi_conflict", "severity": "warning",
         "passed": audit["n_conflicts"] == 0,
         "metric_name": "conflicting_days", "metric_value": float(audit["n_conflicts"]),
         "detail": "printed jodi disagrees with the panna arithmetic; pannas retained, "
                   "flagged in historical_results.notes"},
        {"check_name": "snapshot_missing_days", "severity": "info", "passed": True,
         "metric_name": "days_without_result", "metric_value": float(audit["n_missing"]),
         "detail": "days the source pages leave blank (* * *); no row is written for them"},
        {"check_name": "snapshot_week_label_repairs", "severity": "warning", "passed": True,
         "metric_name": "repaired_week_labels",
         "metric_value": float(len(audit["week_repairs"])),
         "detail": "week labels that needed a month/year correction to fit the weekly grid"},
        {"check_name": "snapshot_weekday_alignment", "severity": "error",
         "passed": len(audit["weekday_mismatch"]) == 0,
         "metric_name": "weekday_mismatches",
         "metric_value": float(len(audit["weekday_mismatch"])),
         "detail": "every dated cell must fall on the weekday its column names"},
    ]
    db.record_quality(quality, run_id=run_ids[0] if run_ids else None)
    db.record_update("snapshot_import", "ok", utcnow(),
                     new_records=outcome.inserted, new_watermark=rows[-1]["result_date"])

    audit_path = None
    if audit_dir is not None:
        target = Path(audit_dir)
        target.mkdir(parents=True, exist_ok=True)
        audit_path = str(target / f"reconciliation_{market_id}.json")
        payload = dict(audit)
        payload["import"] = {"rows_built": len(rows), "inserted": outcome.inserted,
                             "revised": outcome.revised, "rejected": outcome.rejected,
                             "rejected_examples": outcome.errors[:10],
                             "source_id": source_id, "raw_paths": raw_paths,
                             "run_ids": run_ids, "at": utcnow()}
        Path(audit_path).write_text(json.dumps(payload, indent=1, default=str))

    return ImportReport(
        market_id=market_id, dataset=config.dataset.name, rows_built=len(rows),
        inserted=outcome.inserted, revised=outcome.revised,
        unchanged=outcome.unchanged, rejected=outcome.rejected,
        errors=list(outcome.errors), missing_days=audit["n_missing"],
        conflicts=audit["n_conflicts"], audit_path=audit_path,
        raw_paths=raw_paths, run_ids=run_ids)


def write_snapshot_manifest(raw_dir: str | Path) -> Path:
    """SHA-256 manifest of the raw snapshots (the parsers' only input)."""
    raw_dir = Path(raw_dir)
    entries = []
    for path in sorted(raw_dir.rglob("*")):
        if path.is_file() and path.suffix in {".mhtml", ".html", ".mht", ".txt"}:
            data = path.read_bytes()
            entries.append({
                "path": str(path.relative_to(raw_dir.parent.parent)),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
    manifest = {
        "generated_at": utcnow(),
        "note": ("Raw snapshots supplied by the user (saved pages of dpbossss.com). "
                 "They are kept out of version control by the data policy; this "
                 "manifest is committed so every stored row can be traced to the exact "
                 "file that produced it."),
        "files": entries,
    }
    target = raw_dir / "MANIFEST.json"
    target.write_text(json.dumps(manifest, indent=1))
    return target
