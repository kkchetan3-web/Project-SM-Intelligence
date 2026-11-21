"""Website reconnaissance.

Answers, per source, the questions Section 5.1 of the brief asks for: is it
reachable, what does it serve, is the content server-rendered HTML or a JS
application, are there year/month archive links, is there a public JSON
endpoint, is there a downloadable file.

Everything here is observational and polite: it requests the configured entry
points at a throttled rate, honours ``robots.txt``, never submits a form, never
solves a challenge and never retries a blocked host in a tight loop. Results are
written to ``source_records`` so the report can state exactly what happened
rather than what was hoped for.
"""

from __future__ import annotations

import re
import urllib.parse
import urllib.robotparser
from dataclasses import dataclass, field
from typing import Any

from bs4 import BeautifulSoup

from src.core.configuration import Config, SourceSpec
from src.core.logging import get_logger
from src.core.provenance import utcnow
from src.ingestion.extraction import FetchResult, HttpClient

log = get_logger(__name__)

ARCHIVE_HINT_PATTERNS = [
    r"\d{4}", r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
    r"record", r"chart", r"result", r"panel", r"jodi", r"archive", r"old", r"previous",
]
ASSET_EXTENSIONS = (".csv", ".xlsx", ".xls", ".json", ".zip", ".txt")


@dataclass
class PageProbe:
    url: str
    reachable: bool
    http_status: int | None
    error: str | None
    content_type: str | None = None
    byte_size: int = 0
    is_html: bool = False
    is_json: bool = False
    title: str = ""
    table_count: int = 0
    row_count: int = 0
    script_count: int = 0
    looks_js_rendered: bool = False
    status: str = "unknown"

    def as_dict(self) -> dict[str, Any]:
        return {
            "url": self.url, "reachable": self.reachable, "http_status": self.http_status,
            "error": self.error, "content_type": self.content_type,
            "byte_size": self.byte_size, "is_html": self.is_html, "is_json": self.is_json,
            "title": self.title, "table_count": self.table_count, "row_count": self.row_count,
            "script_count": self.script_count, "looks_js_rendered": self.looks_js_rendered,
            "status": self.status,
        }


@dataclass
class SourceReport:
    source_id: str
    market_id: str | None
    kind: str
    base_url: str
    reachable: bool = False
    probes: list[PageProbe] = field(default_factory=list)
    archive_links: dict[str, list[str]] = field(default_factory=dict)
    asset_links: list[str] = field(default_factory=list)
    structured_data_blocks: int = 0
    robots_allows: bool | None = None
    verdict: str = "unprobed"
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id, "market_id": self.market_id, "kind": self.kind,
            "base_url": self.base_url, "reachable": self.reachable,
            "robots_allows": self.robots_allows, "verdict": self.verdict,
            "structured_data_blocks": self.structured_data_blocks,
            "archive_link_groups": {k: v[:25] for k, v in self.archive_links.items()},
            "n_archive_links": sum(len(v) for v in self.archive_links.values()),
            "asset_links": self.asset_links[:40],
            "probes": [p.as_dict() for p in self.probes],
            "notes": self.notes,
        }


def _looks_js_rendered(soup: BeautifulSoup, html: str) -> bool:
    """Heuristic: almost no text, but scripts and a framework root element."""
    text = soup.get_text(" ", strip=True)
    scripts = len(soup.find_all("script"))
    framework_markers = (
        '__NEXT_DATA__', 'id="root"', 'id="app"', "ng-app", "data-reactroot",
        "vue.js", "vite", "/static/js/",
    )
    marker_hit = any(m in html for m in framework_markers)
    return (len(text) < 400 and scripts > 2) or (marker_hit and len(text) < 1500)


def probe_page(client: HttpClient, url: str) -> tuple[PageProbe, FetchResult | None]:
    result = client.get(url)
    probe = PageProbe(
        url=url,
        reachable=result.ok,
        http_status=result.status_code,
        error=result.error,
        content_type=result.content_type,
        byte_size=len(result.body or ""),
    )
    probe.status = "reachable" if result.ok else "unreachable"
    if not result.ok:
        return probe, result

    body = result.body or ""
    probe.is_html = "<html" in body[:2000].lower() or "<table" in body[:4000].lower()
    probe.is_json = body.lstrip().startswith(("{", "["))
    if probe.is_html:
        soup = BeautifulSoup(body, "lxml")
        probe.title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""
        tables = soup.find_all("table")
        probe.table_count = len(tables)
        probe.row_count = sum(len(t.find_all("tr")) for t in tables)
        probe.script_count = len(soup.find_all("script"))
        probe.looks_js_rendered = _looks_js_rendered(soup, body)
        probe.status = "html_tables" if probe.table_count else "html_no_tables"
    elif probe.is_json:
        probe.status = "json"
    return probe, result


def _extract_links(base_url: str, html: str) -> tuple[dict[str, list[str]], list[str], int]:
    soup = BeautifulSoup(html, "lxml")
    archive: dict[str, list[str]] = {}
    assets: list[str] = []
    for anchor in soup.find_all("a", href=True):
        href = urllib.parse.urljoin(base_url, anchor["href"])
        if not href.startswith(("http://", "https://")):
            continue
        lower = href.lower()
        if lower.endswith(ASSET_EXTENSIONS):
            if href not in assets:
                assets.append(href)
            continue
        if not any(re.search(p, lower) for p in ARCHIVE_HINT_PATTERNS):
            continue
        # Group by first path segment so the report shows archive *families*.
        path = urllib.parse.urlparse(href).path.strip("/")
        if not path:
            continue
        segments = [s for s in path.split("/") if s]
        group = "external" if urllib.parse.urlparse(href).netloc != urllib.parse.urlparse(base_url).netloc else (
            segments[0] if len(segments) > 1 else "root"
        )
        archive.setdefault(group, [])
        if href not in archive[group]:
            archive[group].append(href)
    structured = len(soup.find_all("script", type="application/ld+json"))
    return archive, assets, structured


def check_robots(client: HttpClient, base_url: str) -> bool | None:
    """Return True/False if robots.txt is readable, None if it is not."""
    robots_url = urllib.parse.urljoin(base_url, "/robots.txt")
    result = client.get(robots_url)
    if not result.ok:
        return None
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(result.body.splitlines())
    try:
        return bool(parser.can_fetch(client.user_agent, base_url))
    except Exception:  # pragma: no cover - malformed robots
        return None


def investigate_source(client: HttpClient, source: SourceSpec) -> SourceReport:
    """Probe one source thoroughly enough to justify an extraction decision."""
    report = SourceReport(
        source_id=source.source_id,
        market_id=source.market_id,
        kind=source.kind,
        base_url=source.base_url,
    )
    report.robots_allows = check_robots(client, source.base_url)
    if report.robots_allows is False:
        report.verdict = "disallowed_by_robots"
        report.notes.append("robots.txt disallows fetching the base URL; no extraction attempted")
        return report

    pages = dict(source.pages)
    pages.setdefault("home", source.base_url)
    for page_name, url in pages.items():
        probe, result = probe_page(client, url)
        report.probes.append(probe)
        if result is not None and result.ok and probe.is_html:
            archive, assets, structured = _extract_links(url, result.body or "")
            for group, links in archive.items():
                existing = report.archive_links.setdefault(group, [])
                for link in links:
                    if link not in existing:
                        existing.append(link)
            report.asset_links.extend(a for a in assets if a not in report.asset_links)
            report.structured_data_blocks += structured

    report.reachable = any(p.reachable for p in report.probes)
    if not report.reachable:
        errors = {p.error for p in report.probes if p.error}
        report.verdict = "unreachable"
        report.notes.append(
            "no page could be fetched from this environment; errors observed: "
            + "; ".join(sorted(e for e in errors if e)[:4])
        )
    elif not any(p.table_count for p in report.probes):
        report.verdict = "reachable_no_tables"
        report.notes.append("pages served but no HTML tables found; content may be JS-rendered")
    else:
        report.verdict = "reachable_with_tables"
    return report


def investigate_all(config: Config, client: HttpClient | None = None) -> list[SourceReport]:
    client = client or HttpClient(config.http)
    reports: list[SourceReport] = []
    for source in config.sources.values():
        if not source.base_url:
            continue
        log.info("probing source %s (%s)", source.source_id, source.base_url)
        reports.append(investigate_source(client, source))
    return reports


def observed_at() -> str:
    return utcnow()


def summarise(reports: list[SourceReport]) -> dict[str, Any]:
    return {
        "observed_at": observed_at(),
        "n_sources": len(reports),
        "n_reachable": sum(1 for r in reports if r.reachable),
        "verdicts": {r.source_id: r.verdict for r in reports},
        "observations": [r.as_dict() for r in reports],
    }
