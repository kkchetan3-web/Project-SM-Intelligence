"""Pagination and archive traversal.

Two mechanisms cover the supplied sites:

1. **In-page pagination** - ``?page=N`` / ``?p=N`` style links, or "next" links.
   :func:`discover_pagination` reads the page and records which convention the
   site actually uses instead of guessing.
2. **Calendar pagination** - one page per year or per month (the common
   ``*-chart-record`` layout, where a year page lists twelve months).

Both are bounded by the page budget in the HTTP configuration, and neither
follows a link off the source's own origin.
"""

from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass

from bs4 import BeautifulSoup

from src.core.logging import get_logger
from src.ingestion.extraction import same_origin

log = get_logger(__name__)

YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
NEXT_TEXT = {"next", "next page", "older", "previous", "prev", ">>", ">"}


@dataclass
class PaginationPlan:
    base_url: str
    style: str                      # 'none' | 'query' | 'path' | 'calendar'
    parameter: str | None = None    # e.g. 'page'
    max_seen: int = 0
    next_links: list[str] = None
    year_links: list[str] = None
    month_links: list[str] = None
    notes: list[str] = None

    def __post_init__(self) -> None:
        self.next_links = self.next_links or []
        self.year_links = self.year_links or []
        self.month_links = self.month_links or []
        self.notes = self.notes or []

    def as_dict(self) -> dict:
        return {
            "base_url": self.base_url, "style": self.style, "parameter": self.parameter,
            "max_seen": self.max_seen, "n_next": len(self.next_links),
            "n_year_links": len(self.year_links), "n_month_links": len(self.month_links),
            "notes": self.notes,
        }


def discover_pagination(base_url: str, html: str) -> PaginationPlan:
    """Detect the pagination convention a page uses."""
    soup = BeautifulSoup(html, "lxml")
    plan = PaginationPlan(base_url=base_url, style="none")

    for anchor in soup.find_all("a", href=True):
        href = urllib.parse.urljoin(base_url, anchor["href"])
        if not same_origin(href, base_url):
            continue
        text = (anchor.get_text(" ", strip=True) or "").lower()
        target = href.lower()

        if text in NEXT_TEXT or "next" in target:
            if href not in plan.next_links:
                plan.next_links.append(href)
        if YEAR_RE.search(href):
            numeric = int(YEAR_RE.search(href).group(0))
            if 2005 <= numeric <= 2100 and href not in plan.year_links:
                plan.year_links.append(href)

    query = urllib.parse.parse_qs(urllib.parse.urlparse(base_url).query)
    for param in ("page", "p", "pg", "start", "offset"):
        if param in query:
            plan.style = "query"
            plan.parameter = param
            try:
                plan.max_seen = max(int(v[0]) for v in [query[param]])
            except (TypeError, ValueError):
                plan.max_seen = 1
            break

    if plan.style == "none" and plan.year_links:
        plan.style = "calendar"
        plan.notes.append("year links found; treating this as a calendar archive")
    elif plan.style == "none" and plan.next_links:
        plan.style = "path"
        plan.notes.append("relative next-links found; following them sequentially")
    return plan


def enumerate_pages(plan: PaginationPlan, *, max_pages: int, highest_page: int | None = None) -> list[str]:
    """Deterministic page list for one archive traversal."""
    if plan.style == "query" and plan.parameter:
        top = highest_page or plan.max_seen or 1
        urls: list[str] = []
        for page_no in range(1, top + 1):
            parts = urllib.parse.urlparse(plan.base_url)
            query = dict(urllib.parse.parse_qsl(parts.query))
            query[plan.parameter] = str(page_no)
            urls.append(urllib.parse.urlunparse(parts._replace(query=urllib.parse.urlencode(query))))
        return urls[:max_pages]
    if plan.style == "calendar" and plan.year_links:
        return plan.year_links[:max_pages]
    if plan.style == "path" and plan.next_links:
        return [plan.base_url, *plan.next_links][:max_pages]
    return [plan.base_url]


def year_url_candidates(base_url: str, years: list[int]) -> list[str]:
    """Year-suffixed candidates for sites whose charts are per-year pages."""
    parts = urllib.parse.urlparse(base_url)
    stem = parts.path.rsplit(".", 1)[0]
    ext = "." + parts.path.rsplit(".", 1)[1] if "." in parts.path else ""
    out = []
    for year in years:
        out.append(urllib.parse.urlunparse(
            parts._replace(path=f"{stem}-{year}{ext}")))
    return out
