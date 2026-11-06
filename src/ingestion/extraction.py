"""HTTP fetching and HTML table parsing.

Extraction is deliberately the *least* intrusive mechanism that works: a plain
HTTP GET of a server-rendered page, throttled, with retries only for transient
failures. No headless browser, no CAPTCHA handling, no authentication bypass,
no scraping of endpoints the site has not published.

Honesty note
------------
The chart parsers below were written against the published URL structure and the
conventional layout of ``*-chart-record`` pages (a month/date table whose cells
hold a jodi or an open/close panna pair). They have been exercised against the
local markup fixtures in ``tests/fixtures/``, **not** against a live response,
because this build environment cannot reach the source hosts. Until
``python -m src.cli.main extract-all`` has been run somewhere with egress, the
parsers must be treated as unvalidated against production markup; the platform
records that status rather than assuming success.
"""

from __future__ import annotations

import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, Sequence

from bs4 import BeautifulSoup

from src.core.configuration import HttpSpec
from src.core.logging import get_logger

log = get_logger(__name__)

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}

TRANSIENT_STATUS = {408, 425, 429, 500, 502, 503, 504}


# ---------------------------------------------------------------------------
# fetch
# ---------------------------------------------------------------------------
@dataclass
class FetchResult:
    url: str
    ok: bool
    status_code: int | None = None
    body: str | None = None
    error: str | None = None
    attempts: int = 1
    elapsed_ms: int = 0
    content_type: str | None = None
    error_class: str | None = None


class RobotsDisallowed(RuntimeError):
    """Raised when robots.txt forbids the request. Never retried."""


class HttpClient:
    """Rate-limited, retrying HTTP client with an explicit politeness budget."""

    def __init__(self, spec: HttpSpec, *, sleeper=time.sleep, clock=time.monotonic):
        self.spec = spec
        self.user_agent = spec.user_agent
        self._sleeper = sleeper
        self._clock = clock
        self._last_request_at = 0.0
        self.request_count = 0
        self.consecutive_failures = 0

    # -- politeness ------------------------------------------------------
    def _throttle(self) -> None:
        elapsed = self._clock() - self._last_request_at
        wait = self.spec.min_delay_seconds - elapsed
        if wait > 0:
            self._sleeper(wait)
        self._last_request_at = self._clock()

    def _backoff(self, attempt: int, retry_after: float | None = None) -> None:
        if retry_after is not None:
            delay = min(retry_after, self.spec.backoff_max_seconds)
        else:
            delay = min(self.spec.backoff_base_seconds * (2 ** (attempt - 1)),
                        self.spec.backoff_max_seconds)
        self._sleeper(delay)

    # -- request ---------------------------------------------------------
    def get(self, url: str) -> FetchResult:
        if self.request_count >= self.spec.max_pages_per_run:
            return FetchResult(url=url, ok=False, error="page budget exhausted",
                               error_class="BudgetExhausted")
        if self.consecutive_failures >= self.spec.max_consecutive_failures:
            return FetchResult(url=url, ok=False,
                               error=f"circuit breaker: {self.consecutive_failures} consecutive failures",
                               error_class="CircuitOpen")

        last = FetchResult(url=url, ok=False)
        for attempt in range(1, self.spec.max_retries + 1):
            self._throttle()
            self.request_count += 1
            started = self._clock()
            retry_after: float | None = None
            try:
                request = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": self.user_agent,
                        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
                        "Accept-Language": "en-IN,en;q=0.8",
                    },
                )
                with urllib.request.urlopen(request, timeout=self.spec.timeout_seconds) as resp:
                    charset = resp.headers.get_content_charset() or "utf-8"
                    body = resp.read().decode(charset, errors="replace")
                    last = FetchResult(
                        url=url, ok=True, status_code=resp.status, body=body,
                        attempts=attempt,
                        elapsed_ms=int((self._clock() - started) * 1000),
                        content_type=resp.headers.get("Content-Type"),
                    )
                self.consecutive_failures = 0
                return last
            except urllib.error.HTTPError as exc:
                retry_after_hdr = exc.headers.get("Retry-After") if exc.headers else None
                if retry_after_hdr and retry_after_hdr.strip().isdigit():
                    retry_after = float(retry_after_hdr.strip())
                last = FetchResult(
                    url=url, ok=False, status_code=exc.code, error=f"HTTP {exc.code}",
                    attempts=attempt, error_class="HTTPError",
                    elapsed_ms=int((self._clock() - started) * 1000),
                )
                if exc.code not in TRANSIENT_STATUS:
                    self.consecutive_failures += 1
                    return last
            except Exception as exc:  # URLError, ssl, timeout, socket
                last = FetchResult(
                    url=url, ok=False, error=f"{type(exc).__name__}: {exc}",
                    attempts=attempt, error_class=type(exc).__name__,
                    elapsed_ms=int((self._clock() - started) * 1000),
                )
            self.consecutive_failures += 1
            if attempt < self.spec.max_retries:
                self._backoff(attempt, retry_after)
        return last


# ---------------------------------------------------------------------------
# parsed record
# ---------------------------------------------------------------------------
@dataclass
class ParsedRecord:
    result_date: date
    open_panna: str | None = None
    open_ank: int | None = None
    close_panna: str | None = None
    close_ank: int | None = None
    jodi: str | None = None
    raw: str = ""

    def as_row(self, *, market_id: str, source_id: str, source_url: str,
               published_at: str | None = None) -> dict:
        return {
            "market_id": market_id,
            "result_date": self.result_date.isoformat(),
            "open_panna": self.open_panna,
            "open_ank": self.open_ank,
            "close_panna": self.close_panna,
            "close_ank": self.close_ank,
            "jodi": self.jodi,
            "source_id": source_id,
            "source_url": source_url,
            "source_timestamp": published_at,
            "verification_status": "unverified_scrape",
            "raw_payload": self.raw[:2000],
        }


# ---------------------------------------------------------------------------
# parsing primitives
# ---------------------------------------------------------------------------
_DATE_SLASH = re.compile(r"\b(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})\b")
_DATE_TEXT = re.compile(
    r"\b(\d{1,2})\s*[\-\s]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
    r"(?:\s*[\-,]?\s*(\d{4}))?\b",
    re.IGNORECASE,
)
_MONTH_HEADER = re.compile(
    r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s*[\-]?\s*(\d{4})\b",
    re.IGNORECASE,
)
_JODI_CELL = re.compile(r"^\d{2}$")
_PANNA_PAIR = re.compile(r"\b(\d{3})\s*-\s*(\d)\b")
_PANNA_ONLY = re.compile(r"\b(\d{3})\b")


def _full_year(two_digit: str) -> int:
    year = int(two_digit)
    if len(two_digit) <= 2:
        # Matka charts never predate 2000; 20xx is the only sane reading.
        return 2000 + year
    return year


def _safe_date(day: int, month: int, year: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def extract_date(text: str, *, default_year: int | None = None,
                 default_month: int | None = None) -> date | None:
    """Pull a date out of a cell or header, tolerating the usual formats."""
    text = text.strip()
    match = _DATE_SLASH.search(text)
    if match:
        day, month, year = match.groups()
        return _safe_date(int(day), int(month), _full_year(year))
    match = _DATE_TEXT.search(text)
    if match:
        day, month_name, year = match.groups()
        month = MONTHS.get(month_name.lower()[:4]) or MONTHS.get(month_name.lower()[:3])
        if month is None:
            return None
        resolved_year = int(year) if year else default_year
        if resolved_year is None:
            return None
        return _safe_date(int(day), month, resolved_year)
    return None


def parse_panna_token(token: str) -> tuple[str | None, int | None]:
    """``'128-5'`` -> ``('128', 5)``; ``'128'`` -> ``('128', 8)``."""
    token = token.strip()
    pair = _PANNA_PAIR.search(token)
    if pair:
        panna, ank = pair.group(1), int(pair.group(2))
        expected = sum(int(c) for c in panna) % 10
        return (panna, ank) if ank == expected else (panna, expected)
    solo = _PANNA_ONLY.search(token)
    if solo:
        panna = solo.group(1)
        return panna, sum(int(c) for c in panna) % 10
    return None, None


def _cell_texts(row) -> list[str]:
    return [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]


def parse_jodi_chart(html: str, *, default_year: int | None = None) -> list[ParsedRecord]:
    """Parse a monthly *jodi* chart.

    The layout is a table of ``date | jodi`` cells grouped under month headers.
    The parser tracks the most recent month header so that cells containing only
    ``DD`` (common in these charts) still resolve to a full date.
    """
    soup = BeautifulSoup(html, "lxml")
    records: list[ParsedRecord] = []
    seen: set[date] = set()

    for table in soup.find_all("table"):
        current_month: int | None = None
        current_year: int | None = default_year
        for row in table.find_all("tr"):
            cells = _cell_texts(row)
            if not cells:
                continue
            joined = " | ".join(cells)

            header = _MONTH_HEADER.search(joined)
            if header and len(cells) <= 3:
                current_month = MONTHS.get(header.group(1).lower()[:4]) or MONTHS.get(
                    header.group(1).lower()[:3])
                current_year = int(header.group(2))
                continue

            parsed_date = None
            date_idx: int | None = None
            for i, cell in enumerate(cells):
                parsed_date = extract_date(cell, default_year=current_year,
                                           default_month=current_month)
                if parsed_date:
                    date_idx = i
                    break
            if parsed_date is None:
                # Bare day number in the first cell + a known month context.
                first = cells[0].strip()
                if first.isdigit() and len(first) <= 2 and current_month and current_year:
                    parsed_date = _safe_date(int(first), current_month, current_year)
                    date_idx = 0

            # The date cell itself often looks like a two-digit number ("03"), so it
            # must be excluded or it would be read as the jodi.
            jodi = None
            candidates = [c.strip() for i, c in enumerate(cells) if i != date_idx]
            for candidate in reversed(candidates):
                if _JODI_CELL.fullmatch(candidate):
                    jodi = candidate
                    break
            if jodi is None:
                # Some charts write the jodi as a run-together pair inside a
                # cell that also contains the panna; take the last 2-digit group.
                tokens = re.findall(r"\b\d{2}\b", joined)
                if len(tokens) >= 1 and parsed_date is not None:
                    jodi = tokens[-1]

            if parsed_date is None or jodi is None:
                continue
            if parsed_date in seen:
                continue
            seen.add(parsed_date)
            records.append(ParsedRecord(
                result_date=parsed_date,
                jodi=f"{int(jodi):02d}",
                open_ank=int(jodi[0]),
                close_ank=int(jodi[1]),
                raw=joined[:400],
            ))
    records.sort(key=lambda r: r.result_date)
    return records


def parse_panel_chart(html: str, *, default_year: int | None = None) -> list[ParsedRecord]:
    """Parse a monthly *panel* (panna) chart: ``open panna/ank ... close panna/ank``."""
    soup = BeautifulSoup(html, "lxml")
    records: list[ParsedRecord] = []
    seen: set[date] = set()

    for table in soup.find_all("table"):
        current_month: int | None = None
        current_year: int | None = default_year
        for row in table.find_all("tr"):
            cells = _cell_texts(row)
            if not cells:
                continue
            joined = " | ".join(cells)

            header = _MONTH_HEADER.search(joined)
            if header and len(cells) <= 3:
                current_month = MONTHS.get(header.group(1).lower()[:4]) or MONTHS.get(
                    header.group(1).lower()[:3])
                current_year = int(header.group(2))
                continue

            parsed_date = None
            for cell in cells:
                parsed_date = extract_date(cell, default_year=current_year,
                                           default_month=current_month)
                if parsed_date:
                    break
            if parsed_date is None:
                first = cells[0].strip()
                if first.isdigit() and len(first) <= 2 and current_month and current_year:
                    parsed_date = _safe_date(int(first), current_month, current_year)
            if parsed_date is None or parsed_date in seen:
                continue

            tokens = _PANNA_PAIR.findall(joined)
            if len(tokens) < 2:
                solo = _PANNA_ONLY.findall(joined)
                if len(solo) >= 2:
                    tokens = [(solo[0], ""), (solo[1], "")]
                else:
                    continue
            open_panna, open_ank = parse_panna_token(f"{tokens[0][0]}-{tokens[0][1]}"
                                                     if tokens[0][1] else tokens[0][0])
            close_panna, close_ank = parse_panna_token(f"{tokens[-1][0]}-{tokens[-1][1]}"
                                                       if tokens[-1][1] else tokens[-1][0])
            if open_panna is None or close_panna is None:
                continue
            seen.add(parsed_date)
            records.append(ParsedRecord(
                result_date=parsed_date,
                open_panna=open_panna, open_ank=open_ank,
                close_panna=close_panna, close_ank=close_ank,
                jodi=f"{open_ank}{close_ank}",
                raw=joined[:400],
            ))
    records.sort(key=lambda r: r.result_date)
    return records


PARSERS = {
    "dpbossss_jodi_chart": parse_jodi_chart,
    "dpbossss_panel_chart": parse_panel_chart,
    "index_links": lambda html, **_kw: [],
    "default": parse_jodi_chart,
}


def merge_records(*record_sets: Sequence[ParsedRecord]) -> list[ParsedRecord]:
    """Combine jodi-chart and panel-chart parses of the same market.

    Both sources describe the same draw. The panel chart carries panna + ank;
    the jodi chart carries the jodi. Merging fills gaps and *flags* rather than
    hides disagreements (``merge_conflicts``).
    """
    merged: dict[date, ParsedRecord] = {}
    for records in record_sets:
        for rec in records:
            existing = merged.get(rec.result_date)
            if existing is None:
                merged[rec.result_date] = ParsedRecord(**vars(rec))
                continue
            for field_name in ("open_panna", "open_ank", "close_panna", "close_ank", "jodi"):
                new_val = getattr(rec, field_name)
                old_val = getattr(existing, field_name)
                if new_val is None:
                    continue
                if old_val is None:
                    setattr(existing, field_name, new_val)
                elif str(old_val) != str(new_val):
                    existing.raw = (existing.raw + f" || CONFLICT {field_name}: "
                                    f"{old_val} vs {new_val}")[:1500]
    return [merged[d] for d in sorted(merged)]


def find_merge_conflicts(records: Iterable[ParsedRecord]) -> list[dict]:
    conflicts = []
    for rec in records:
        if "CONFLICT" in rec.raw:
            conflicts.append({"date": rec.result_date.isoformat(), "detail": rec.raw[-300:]})
    return conflicts


def build_archive_urls(pages: dict[str, str], years: Sequence[int],
                       *, pattern: str | None = None) -> list[str]:
    """Generate candidate year/month archive URLs.

    Only URL *shapes* the site itself advertises via links are enumerated; this
    function never guesses an endpoint that discovery has not observed. It is
    used with the link groups found by :mod:`website_discovery`.
    """
    urls: list[str] = []
    for _, url in pages.items():
        if not pattern:
            urls.append(url)
            continue
        for year in years:
            urls.append(pattern.format(base=url, year=year))
    return list(dict.fromkeys(urls))


def same_origin(url: str, base: str) -> bool:
    return urllib.parse.urlparse(url).netloc == urllib.parse.urlparse(base).netloc
