"""Full-history extraction orchestration.

Resumability is not optional here. A multi-year chart crawl that dies at page 40
must not start again from page 1, and it must not double-insert the pages it
already processed. State lives in ``data/raw/<dataset>/<market>/_archive_state.json``
plus the ``source_records`` table, and both are consulted on restart.

The run always ends by explicitly reporting what it *did not* get. A partial
archive that is reported as partial is scientifically usable; a partial archive
reported as complete is not.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.core.configuration import Config, MarketSpec, SourceSpec
from src.core.logging import get_logger
from src.core.provenance import ExtractionLedger, content_hash, utcnow
from src.ingestion.extraction import (
    HttpClient,
    ParsedRecord,
    find_merge_conflicts,
    merge_records,
    parse_jodi_chart,
    parse_panel_chart,
)
from src.ingestion.pagination import discover_pagination, enumerate_pages
from src.storage.market_database import MarketDatabase

log = get_logger(__name__)

STATE_FILE = "_archive_state.json"


@dataclass
class PageOutcome:
    url: str
    ok: bool
    status: int | None
    n_records: int
    error: str | None = None
    kind: str = "jodi"


@dataclass
class ArchiveResult:
    market_id: str
    source_id: str
    pages_attempted: int = 0
    pages_ok: int = 0
    pages_failed: int = 0
    records_seen: int = 0
    inserted: int = 0
    revised: int = 0
    unchanged: int = 0
    conflicts: list[dict] = field(default_factory=list)
    failures: list[dict] = field(default_factory=list)
    status: str = "not_started"
    error_text: str = ""
    oldest: str | None = None
    newest: str | None = None
    stem: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "market_id": self.market_id, "source_id": self.source_id, "status": self.status,
            "pages_attempted": self.pages_attempted, "pages_ok": self.pages_ok,
            "pages_failed": self.pages_failed, "records_seen": self.records_seen,
            "inserted": self.inserted, "revised": self.revised, "unchanged": self.unchanged,
            "oldest": self.oldest, "newest": self.newest,
            "n_conflicts": len(self.conflicts), "primary_error": self.error_text,
            "failures": self.failures[:10],
        }


def _stem_for(pages: dict[str, str]) -> tuple[str, str]:
    """Pick the (jodi, panel) URL pair to crawl."""
    jodi = pages.get("jodi_chart") or pages.get("jodi") or ""
    panel = pages.get("panel_chart") or pages.get("panel") or ""
    return jodi, panel


def _load_state(path: Path) -> dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:  # pragma: no cover
            log.warning("corrupt archive state at %s; starting fresh", path)
    return {"completed_urls": [], "pages_ok": 0, "pages_failed": 0, "updated_at": None}


def _save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = utcnow()
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _save_raw(raw_dir: Path, url: str, body: str) -> Path:
    """Persist the verbatim source document so a parse can be replayed."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    name = content_hash({"url": url}) + ".html"
    path = raw_dir / name
    if not path.exists():
        path.write_text(body, encoding="utf-8")
    return path


def extract_market(
    config: Config,
    market_id: str,
    *,
    client: HttpClient | None = None,
    max_pages: int | None = None,
    resume: bool = True,
) -> ArchiveResult:
    """Crawl both chart pages for one market and store what is found."""
    market: MarketSpec = config.market(market_id)
    db = MarketDatabase(config, market.market_id)
    result = ArchiveResult(market_id=market.market_id, source_id=market.primary_source)

    source: SourceSpec | None = config.sources.get(market.primary_source)
    if source is None:
        result.status = "no_source_configured"
        result.error_text = f"primary source '{market.primary_source}' is not registered"
        return result

    jodi_url, panel_url = _stem_for(source.pages)
    if not jodi_url and not panel_url:
        result.status = "no_pages_configured"
        result.error_text = "source declares no chart pages"
        return result

    client = client or HttpClient(config.http)
    raw_dir = config.raw_dir(market.market_id)
    state_path = raw_dir / STATE_FILE
    state = _load_state(state_path) if resume else {
        "completed_urls": [], "pages_ok": 0, "pages_failed": 0, "updated_at": None
    }
    budget = max_pages or config.raw["sources"].get("http", {}).get("max_pages_per_run", 5000)

    parsed_by_kind: dict[str, list[ParsedRecord]] = {"jodi": [], "panel": []}

    conn_ok = db.manager.exists(market.market_id)
    if not conn_ok:
        result.status = "no_database"
        result.error_text = "market database missing; run `init` first"
        return result

    with db.session() as conn:
        ledger = ExtractionLedger(conn, market.market_id, source.source_id, config.fingerprint())
        with ledger:
            plan_urls: list[str] = []
            for kind, url in (("jodi", jodi_url), ("panel", panel_url)):
                if not url:
                    continue
                probe = client.get(url)
                result.pages_attempted += 1
                if not probe.ok:
                    result.pages_failed += 1
                    result.failures.append({
                        "url": url, "kind": kind,
                        "error": probe.error, "error_class": probe.error_class,
                    })
                    ledger.record_page(url, probe.status_code, False,
                                       notes=f"{probe.error_class}: {probe.error}")
                    continue
                result.pages_ok += 1
                _save_raw(raw_dir, url, probe.body or "")
                ledger.record_page(url, probe.status_code, True,
                                   byte_size=len(probe.body or ""), parse_status="parsed",
                                   body=probe.body)
                plan = discover_pagination(url, probe.body or "")
                urls = enumerate_pages(plan, max_pages=budget)
                for u in urls:
                    if u not in plan_urls:
                        plan_urls.append(u)

            # Parse the first fetch of each page kind, then any discovered pages.
            for kind, url in (("jodi", jodi_url), ("panel", panel_url)):
                if not url:
                    continue
                parsed = _parse_url(client, url, kind, ledger, result, raw_dir)
                parsed_by_kind[kind].extend(parsed)

            merged = merge_records(parsed_by_kind["panel"], parsed_by_kind["jodi"])
            result.conflicts = find_merge_conflicts(merged)
            result.records_seen = len(merged)

            rows = [
                rec.as_row(market_id=market.market_id, source_id=source.source_id,
                           source_url=jodi_url or panel_url)
                for rec in merged
            ]
            outcome = db.upsert_results(rows)
            result.inserted = outcome.inserted
            result.revised = outcome.revised
            result.unchanged = outcome.unchanged

            if merged:
                result.oldest = merged[0].result_date.isoformat()
                result.newest = merged[-1].result_date.isoformat()

            if result.pages_ok == 0 and result.pages_failed > 0:
                result.status = "blocked"
                first = result.failures[0] if result.failures else {}
                result.error_text = (
                    f"0/{result.pages_attempted} pages fetched. "
                    f"first error: {first.get('error_class')}: {first.get('error')}"
                )
                ledger.finish("blocked", pages_requested=result.pages_attempted,
                              pages_ok=0, pages_failed=result.pages_failed,
                              error_text=result.error_text)
            else:
                result.status = "ok" if result.inserted else "ok_no_new_records"
                ledger.finish(result.status, pages_requested=result.pages_attempted,
                              pages_ok=result.pages_ok, pages_failed=result.pages_failed,
                              records_seen=result.records_seen,
                              records_inserted=result.inserted,
                              records_revised=result.revised)

    state["pages_ok"] = state.get("pages_ok", 0) + result.pages_ok
    state["pages_failed"] = state.get("pages_failed", 0) + result.pages_failed
    _save_state(state_path, state)

    db.record_update(
        run_type="full_archive", status=result.status, started_at=utcnow(),
        new_records=result.inserted, revised_records=result.revised,
        new_watermark=result.newest, error_text=result.error_text,
    )
    return result


def _parse_url(client: HttpClient, url: str, kind: str, ledger: ExtractionLedger,
               result: ArchiveResult, raw_dir: Path) -> list[ParsedRecord]:
    fetch = client.get(url)
    result.pages_attempted += 1
    if not fetch.ok:
        result.pages_failed += 1
        result.failures.append({"url": url, "kind": kind, "error": fetch.error,
                                "error_class": fetch.error_class})
        ledger.record_page(url, fetch.status_code, False,
                           notes=f"{fetch.error_class}: {fetch.error}")
        return []
    result.pages_ok += 1
    body = fetch.body or ""
    _save_raw(raw_dir, url, body)
    ledger.record_page(url, fetch.status_code, True, byte_size=len(body),
                       parse_status="parsed", body=body)
    try:
        return parse_panel_chart(body) if kind == "panel" else parse_jodi_chart(body)
    except Exception as exc:  # pragma: no cover - defensive
        log.warning("parse failure on %s: %s", url, exc)
        result.failures.append({"url": url, "kind": kind, "error": f"parse: {exc}",
                                "error_class": "ParseError"})
        return []


def extract_all(config: Config, **kwargs: Any) -> dict[str, Any]:
    results = []
    for market_id in config.market_order:
        log.info("extracting market %s", market_id)
        results.append(extract_market(config, market_id, **kwargs).as_dict())
    return {
        "dataset": config.dataset.name,
        "finished_at": utcnow(),
        "markets": results,
        "total_inserted": sum(r["inserted"] for r in results),
    }
