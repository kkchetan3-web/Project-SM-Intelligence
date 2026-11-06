"""Incremental maintenance.

A daily update must do four things and no more: fetch the recent pages, insert
genuinely new dates, detect revisions to already-stored dates, and leave an
auditable trace either way. It must not re-crawl history, and it must not
"repair" a stored value because a source page rendered differently today.

The watermark is the newest stored date. Anything strictly newer is new;
anything at or before it is checked for revision (which lands in
``result_revisions`` and keeps the old row).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from src.core.configuration import Config
from src.core.logging import get_logger
from src.core.provenance import utcnow
from src.ingestion.extraction import (
    HttpClient,
    find_merge_conflicts,
    merge_records,
    parse_jodi_chart,
    parse_panel_chart,
)
from src.storage.market_database import MarketDatabase

log = get_logger(__name__)


@dataclass
class UpdateResult:
    market_id: str
    status: str
    watermark_before: str | None = None
    watermark_after: str | None = None
    new_records: int = 0
    revised_records: int = 0
    pages_ok: int = 0
    pages_failed: int = 0
    error_text: str = ""
    conflicts: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "market_id": self.market_id, "status": self.status,
            "watermark_before": self.watermark_before,
            "watermark_after": self.watermark_after,
            "new_records": self.new_records, "revised_records": self.revised_records,
            "pages_ok": self.pages_ok, "pages_failed": self.pages_failed,
            "error_text": self.error_text, "n_conflicts": len(self.conflicts),
        }


def _watermark(db: MarketDatabase) -> str | None:
    df = db.results()
    if df.empty:
        return None
    return df["result_date"].max().date().isoformat()


def update_market(config: Config, market_id: str,
                  client: HttpClient | None = None) -> UpdateResult:
    market = config.market(market_id)
    db = MarketDatabase(config, market.market_id)
    started = utcnow()
    wm_before = _watermark(db)
    result = UpdateResult(market_id=market.market_id, status="not_started",
                          watermark_before=wm_before)

    source = config.sources.get(market.primary_source)
    if source is None:
        result.status = "no_source"
        result.error_text = "primary source not registered"
        db.record_update("incremental", result.status, started, error_text=result.error_text)
        return result

    client = client or HttpClient(config.http)
    parsed_sets = []
    for page_name, parser in (("panel_chart", parse_panel_chart),
                              ("jodi_chart", parse_jodi_chart)):
        url = source.pages.get(page_name)
        if not url:
            continue
        fetch = client.get(url)
        if not fetch.ok:
            result.pages_failed += 1
            result.error_text = (result.error_text + " | " if result.error_text else "") + \
                                f"{page_name}: {fetch.error}"
            continue
        result.pages_ok += 1
        try:
            parsed_sets.append(parser(fetch.body or ""))
        except Exception as exc:  # pragma: no cover
            result.error_text = f"{page_name} parse error: {exc}"

    merged = merge_records(*parsed_sets)
    result.conflicts = find_merge_conflicts(merged)

    # Only insert records at or after the watermark window; older pages are
    # handled by the full archive, not by the daily job.
    if wm_before is not None:
        window_start = wm_before
        merged = [r for r in merged if r.result_date.isoformat() >= window_start]

    rows = [
        rec.as_row(market_id=market.market_id, source_id=source.source_id,
                   source_url=source.pages.get("jodi_chart", ""))
        for rec in merged
    ]
    outcome = db.upsert_results(rows)
    result.new_records = outcome.inserted
    result.revised_records = outcome.revised
    result.watermark_after = _watermark(db)

    if result.pages_ok == 0:
        result.status = "blocked"
    elif result.new_records == 0 and result.revised_records == 0:
        result.status = "up_to_date"
    else:
        result.status = "updated"

    db.record_update("incremental", result.status, started,
                     new_records=result.new_records,
                     revised_records=result.revised_records,
                     new_watermark=result.watermark_after,
                     error_text=result.error_text)
    log.info("update %s: %s (+%d new, %d revised)", market.market_id,
             result.status, result.new_records, result.revised_records)
    return result


def update_all(config: Config, client: HttpClient | None = None) -> dict[str, Any]:
    client = client or HttpClient(config.http)
    results = [update_market(config, m, client=client).as_dict() for m in config.market_order]
    return {
        "dataset": config.dataset.name,
        "finished_at": utcnow(),
        "markets": results,
        "total_new": sum(r["new_records"] for r in results),
        "total_revised": sum(r["revised_records"] for r in results),
    }


def staleness_days(config: Config, market_id: str) -> int | None:
    """Age of the newest record in days - drives the freshness warning."""
    from datetime import date

    db = MarketDatabase(config, market_id)
    wm = _watermark(db)
    if wm is None:
        return None
    return (date.today() - date.fromisoformat(wm)).days


def wait_for_politeness(config: Config) -> None:
    time.sleep(config.http.min_delay_seconds)
