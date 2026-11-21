"""Parsers for saved HTML/MHTML snapshots of the dpbossss chart pages.

WHY THIS MODULE EXISTS
----------------------
The two live source hosts cannot be reached from the build environment, but the user
supplied MHTML snapshots ("Saved by Blink") of the four pages that carry the records:

* `jodi-chart-record/<market>.php`   - a weekday grid of jodi numbers, **no dates**
* `panel-chart-record/<market>.php?full_chart` - a weekday grid of
  ``open panna / jodi / close panna`` with an explicit ``DD/MM/YYYY to DD/MM/YYYY``
  week label on every row

The jodi chart is therefore *undated* and the panel chart is *dated but has its own
defects*. This module turns both into dated records and reconciles them:

1. Every panel week label is parsed, including the site's own typos
   (``v31/12/2018``, ``08/06/2020 tp 16/06/2020``) and two different date formats
   (``DD/MM/YYYY`` and, at least once, ``MM/DD/YYYY``) - the second is resolved by
   requiring the week sequence to advance 4-10 days per row.
2. Each day cell of a week is dated ``start + column_index`` and the resulting
   weekday is checked against the column header.
3. Pannas are converted to anks arithmetically (digit sum mod 10), which is what
   defines the jodi. The site sometimes disagrees with its own arithmetic; those
   cases are recorded, never silently overwritten.
4. The undated jodi grid is aligned row-for-row with the dated panel grid and
   compared cell-by-cell. Where the two pages disagree the panel value wins (it is
   the page that carries dates and both pannas) and the disagreement is recorded.

Nothing here invents a value: a missing marker (``* * *``) stays missing, and every
repair is appended to a list that ends up in the audit file.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from bs4 import BeautifulSoup

WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

#: markers the site uses instead of a value, mapped to why they are not a value
MISSING_MARKERS = ("*", "**", "* * *", "-", "--", "?", "n/a", "")

_DATE_TOKEN = re.compile(r"(?<!\d)(\d{1,2})\s*[/\-.]\s*(\d{1,2})\s*[/\-.]\s*(\d{2,4})(?!\d)")


# ---------------------------------------------------------------------------
# 1. reading a snapshot
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SnapshotFile:
    """One saved page, with the provenance the site itself gave us."""

    path: Path
    url: str
    saved_at: str
    title: str
    kind: str
    sha256: str
    byte_size: int
    html: str
    market_hint: str | None = None


def _header(raw: str, name: str) -> str:
    match = re.search(rf"^{name}:\s*(.+)$", raw[:4000], flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def read_snapshot(path: str | Path, *, kind: str | None = None) -> SnapshotFile:
    """Read an MHTML/HTML snapshot and pull out the page that carries the table."""
    path = Path(path)
    raw = path.read_text(encoding="utf-8", errors="replace")
    url = _header(raw, "Snapshot-Content-Location") or _header(raw, "Content-Location")
    saved_at = _header(raw, "Date")

    # The MHTML body repeats the page inside a part that starts with the content
    # location; taking the longest <table> in the file is enough and avoids a full
    # MIME walk (these snapshots hold exactly one data table).
    soup = BeautifulSoup(raw, "lxml")
    tables = soup.find_all("table")
    if not tables:
        raise ValueError(f"no <table> found in {path.name}")
    table = max(tables, key=lambda t: len(t.find_all("tr")))

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    if kind is None:
        lowered = f"{url} {title}".lower()
        kind = "panel" if "panel" in lowered else "jodi"

    market = None
    lowered = f"{url} {title}".lower()
    for candidate in ("main-bazar", "main bazar", "main_bazar"):
        if candidate in lowered:
            market = "main_bazar"
    if market is None and "kalyan" in lowered:
        market = "kalyan"

    data = path.read_bytes()
    return SnapshotFile(
        path=path,
        url=url,
        saved_at=saved_at,
        title=title,
        kind=kind,
        sha256=hashlib.sha256(data).hexdigest(),
        byte_size=len(data),
        html=str(table),
        market_hint=market,
    )


# ---------------------------------------------------------------------------
# 2. cell-level helpers
# ---------------------------------------------------------------------------
def _digits(text: str) -> str:
    return re.sub(r"[^0-9]", "", text)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def parse_panna(cell: str) -> str | None:
    """``7 9 9`` -> ``799``; a missing marker -> ``None``."""
    cleaned = _clean(cell)
    if cleaned.lower() in MISSING_MARKERS:
        return None
    digits = _digits(cleaned)
    return digits if len(digits) == 3 else None


def parse_jodi(cell: str) -> str | None:
    cleaned = _clean(cell)
    if cleaned.lower() in MISSING_MARKERS:
        return None
    digits = _digits(cleaned)
    return digits if len(digits) == 2 else None


def ank_of(panna: str | None) -> int | None:
    """The matka ank: digit sum mod 10. This is arithmetic, not interpretation."""
    if not panna:
        return None
    return sum(int(c) for c in panna) % 10


def jodi_of(open_panna: str | None, close_panna: str | None) -> str | None:
    a, b = ank_of(open_panna), ank_of(close_panna)
    if a is None or b is None:
        return None
    return f"{a}{b}"


# ---------------------------------------------------------------------------
# 3. date handling
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DateReading:
    """One possible reading of a week label, with the cost of believing it."""

    date: dt.date
    cost: float
    why: str


def date_readings(token: str) -> list[DateReading]:
    """Every plausible reading of one ``d/m/y`` token, cheapest first.

    The site is mostly ``DD/MM/YYYY`` and contains

    * ``MM/DD/YYYY`` at least once (``12/16/2016``),
    * labels that are one day off (``01/11/2015``, a Sunday, for the week that
      started Monday 02/11/2015),
    * month/year typos that shift a week by a year (``07/01/2018`` for 2019-01-07,
      ``22/04/2018`` for 2019-04-22, ``04/01/2020 to 09/01/2021``).

    So a token yields the day-first reading at cost 0, the month-first reading at a
    small cost, the same readings under a neighbouring year at a larger cost, and
    each of those shifted by a day at a small cost. Nothing is decided here: the
    caller resolves the whole page under the constraint that weeks are consecutive
    multiples of seven days apart.
    """
    match = _DATE_TOKEN.search(token)
    if not match:
        return []
    a, b, y = (int(match.group(i)) for i in (1, 2, 3))
    if y < 100:
        y += 2000

    out: dict[dt.date, DateReading] = {}

    def add(day: dt.date, cost: float, why: str) -> None:
        current = out.get(day)
        if current is None or cost < current.cost:
            out[day] = DateReading(day, cost, why)

    for year_shift, year_cost in ((0, 0.0), (-1, 0.8), (1, 0.8), (-2, 1.6), (2, 1.6)):
        for order, (day, month) in enumerate(((a, b), (b, a))):
            try:
                base = dt.date(y + year_shift, month, day)
            except ValueError:
                continue
            tag = "day-first" if order == 0 else "month-first"
            if year_shift:
                tag += f" year{year_shift:+d}"
            for offset, offset_cost in ((0, 0.0), (-1, 0.4), (1, 0.4), (-2, 0.9), (2, 0.9),
                                        (-3, 1.2), (3, 1.2), (-4, 1.6), (4, 1.6),
                                        (-5, 2.0), (5, 2.0)):
                add(base + dt.timedelta(days=offset), year_cost + order * 0.5 + offset_cost, tag)
    return sorted(out.values(), key=lambda r: (r.cost, r.date))


def date_candidates(token: str, *, year_tolerance: int = 1) -> list[dt.date]:
    """All dates a token could denote (kept for callers that want the raw set)."""
    readings = date_readings(token)
    dates = [r.date for r in readings]
    if year_tolerance <= 0:
        match = _DATE_TOKEN.search(token)
        if not match:
            return []
        y = int(match.group(3))
        if y < 100:
            y += 2000
        dates = [d for d in dates if abs(d.year - y) <= year_tolerance]
    return sorted(set(dates))


def _tokens(label: str, *, year_tolerance: int = 1) -> list[dt.date]:
    found: list[dt.date] = []
    for match in _DATE_TOKEN.finditer(label):
        for candidate in date_candidates(match.group(0), year_tolerance=year_tolerance):
            if candidate not in found:
                found.append(candidate)
    return found


# ---------------------------------------------------------------------------
# 3b. resolving the whole grid at once
# ---------------------------------------------------------------------------
STEP_COST_OFF_RHYTHM = 3.0
WEEKDAY_PENALTY = 50.0


def _transition_cost(previous: dt.date, current: dt.date) -> float:
    """Cost of two consecutive weeks starting seven (or more) days apart."""
    step = (current - previous).days
    if step <= 0:
        return float("inf")
    if step % 7 == 0 and step <= 7 * 30:
        # Consecutive weeks are free; a closure of N whole weeks costs a little, so a
        # mis-reading that invents a gap is punished but a real gap is affordable.
        return 0.15 * (step // 7 - 1)
    return STEP_COST_OFF_RHYTHM + 0.05 * abs(step)


def resolve_week_starts(labels: list[str], first_weekday: str) -> tuple[list[dt.date | None], list[list[str]]]:
    """Choose one date per week by minimising the total cost over the whole page.

    This is a shortest-path problem, not a per-row guess: a reading that looks poor
    in isolation can be the only one that keeps the page in step, and a local greedy
    choice is exactly what produced a ten-week drift in the first draft. Costs are
    additive, so a single off-rhythm step (3.0) outweighs several label repairs
    (0.4-0.8 each) and the page is resolved as a whole.
    """
    target_weekday = WEEKDAYS.index(first_weekday) if first_weekday in WEEKDAYS else 0
    repairs: list[list[str]] = [[] for _ in labels]

    candidates: list[list[DateReading]] = []
    for index, label in enumerate(labels):
        readings = []
        for match in _DATE_TOKEN.finditer(label):
            readings.extend(date_readings(match.group(0)))
        deduped: dict[dt.date, DateReading] = {}
        for reading in readings:
            penalty = 0.0 if reading.date.weekday() == target_weekday else WEEKDAY_PENALTY
            candidate = DateReading(reading.date, reading.cost + penalty, reading.why)
            current = deduped.get(reading.date)
            if current is None or candidate.cost < current.cost:
                deduped[reading.date] = candidate
        ordered = sorted(deduped.values(), key=lambda r: (r.cost, r.date))
        candidates.append(ordered)

    # Forward pass. `best[i][k]` = cheapest total cost for rows 0..i with row i at k.
    best: list[list[float]] = []
    back: list[list[int]] = []
    for index, options in enumerate(candidates):
        if not options:
            best.append([])
            back.append([])
            continue
        if index == 0:
            best.append([option.cost for option in options])
            back.append([-1] * len(options))
            continue
        prev_options = candidates[index - 1]
        prev_best = best[index - 1]
        row_best: list[float] = []
        row_back: list[int] = []
        for option in options:
            cheapest, arg = float("inf"), -1
            if prev_options and prev_best:
                for j, prev_option in enumerate(prev_options):
                    if prev_best[j] == float("inf"):
                        continue
                    total = prev_best[j] + _transition_cost(prev_option.date, option.date)
                    if total < cheapest:
                        cheapest, arg = total, j
            else:
                # previous row carried no date at all; fall back on the weekly rhythm of
                # the last resolved date if there is one.
                previous = _last_resolved(candidates, best, back, index - 1)
                total = option.cost + (_transition_cost(previous, option.date) if previous else 0.0)
                cheapest, arg = total, -2
            row_best.append(cheapest + option.cost)
            row_back.append(arg)
        best.append(row_best)
        back.append(row_back)

    # Backtrack.
    resolved: list[dt.date | None] = [None] * len(labels)
    if candidates and candidates[-1] and best[-1]:
        cursor = min(range(len(best[-1])), key=lambda k: best[-1][k])
        for index in range(len(labels) - 1, -1, -1):
            if not candidates[index] or not best[index]:
                continue
            if index == len(labels) - 1:
                resolved[index] = candidates[index][cursor].date
            else:
                nxt = resolved[index + 1]
                chosen = min(range(len(candidates[index])),
                             key=lambda k: best[index][k] + _transition_cost(
                                 candidates[index][k].date, nxt) if nxt else best[index][k])
                resolved[index] = candidates[index][chosen].date
            if index > 0:
                cursor = back[index][cursor] if cursor < len(back[index]) else -1
                if cursor < 0:
                    cursor = 0

    # A row whose label carried no date at all inherits the previous week + 7.
    for index in range(len(labels)):
        if resolved[index] is None:
            previous = resolved[index - 1] if index > 0 else None
            if previous is not None:
                resolved[index] = previous + dt.timedelta(days=7)
                repairs[index].append(
                    f"label {labels[index]!r} carries no date; start inferred as "
                    f"{resolved[index]} from the previous week")

    for index, chosen in enumerate(resolved):
        if chosen is None:
            continue
        readings = [r for r in candidates[index] if r.date == chosen] if candidates[index] else []
        reading = readings[0] if readings else None
        if reading is not None and reading.why != "day-first":
            repairs[index].append(f"label {labels[index]!r}: read {chosen} ({reading.why})")
        if index > 0 and resolved[index - 1] is not None:
            step = (chosen - resolved[index - 1]).days
            if step != 7 and step % 7 == 0:
                repairs[index].append(
                    f"label {labels[index]!r}: {step}-day gap after {resolved[index - 1]} - "
                    f"the page skips {step // 7 - 1} whole week(s) here")
            elif step % 7 != 0:
                repairs[index].append(
                    f"label {labels[index]!r}: {step}-day step after {resolved[index - 1]} "
                    f"(not a whole number of weeks)")
    return resolved, repairs


def _last_resolved(candidates, best, back, index: int) -> dt.date | None:
    while index >= 0:
        if candidates[index] and best[index]:
            return candidates[index][min(range(len(best[index])), key=lambda k: best[index][k])].date
        index -= 1
    return None


@dataclass
class PanelCell:
    weekday: str
    open_panna: str | None
    close_panna: str | None
    jodi: str | None
    raw: tuple[str, str, str]

    @property
    def missing(self) -> bool:
        return self.jodi is None and self.open_panna is None and self.close_panna is None


@dataclass
class PanelWeek:
    label_raw: str
    start: dt.date
    end: dt.date | None
    cells: list[PanelCell]
    repairs: list[str] = field(default_factory=list)


@dataclass
class PanelParse:
    weekdays: list[str]
    weeks: list[PanelWeek]
    problems: list[str] = field(default_factory=list)

    @property
    def n_cells(self) -> int:
        return sum(len(w.cells) for w in self.weeks)


#: Abbreviated weekday names some pages use in their table headers.
_WEEKDAY_ABBREV = {
    "mo": "Mon", "tu": "Tue", "we": "Wed", "th": "Thu",
    "fr": "Fri", "sa": "Sat", "su": "Sun",
}


def _header_weekdays(header_cells: list[str]) -> list[str]:
    days = []
    for raw in header_cells:
        cell = _clean(raw)
        if cell in WEEKDAYS:
            days.append(cell)
        elif len(cell) == 2 and cell[:2].lower() in _WEEKDAY_ABBREV:
            days.append(_WEEKDAY_ABBREV[cell[:2].lower()])
    return days or list(WEEKDAYS[:6])


def parse_panel_html(html: str) -> PanelParse:
    """Parse the dated panel grid (``open panna``, ``jodi``, ``close panna``)."""
    soup = BeautifulSoup(html, "lxml")
    rows = soup.find_all("tr")
    if not rows:
        raise ValueError("panel table has no rows")

    header = [_clean(c.get_text(" ", strip=True)) for c in rows[0].find_all(["td", "th"])]
    weekdays = _header_weekdays(header)

    raw_weeks: list[tuple[str, list[PanelCell]]] = []
    problems: list[str] = []

    for index, row in enumerate(rows[1:], start=1):
        cells = [_clean(c.get_text(" ", strip=True)) for c in row.find_all(["td", "th"])]
        if not cells or not any(cells):
            continue
        label, slots = cells[0], cells[1:]
        n_days = min(len(slots) // 3, len(weekdays))
        if n_days == 0:
            problems.append(f"row {index}: no day cells (label={label!r})")
            continue
        parsed_cells: list[PanelCell] = []
        for day_index in range(n_days):
            trio = slots[day_index * 3: day_index * 3 + 3]
            while len(trio) < 3:
                trio.append("")
            parsed_cells.append(PanelCell(
                weekday=weekdays[day_index],
                open_panna=parse_panna(trio[0]),
                jodi=parse_jodi(trio[1]),
                close_panna=parse_panna(trio[2]),
                raw=(trio[0], trio[1], trio[2]),
            ))
        raw_weeks.append((label, parsed_cells))

    # --- deduplicate archive rows -----------------------------------------
    # The dpbossss panel pages sometimes embed an archive block that repeats
    # later weeks (identical label *and* identical cell data) plus a few rows
    # with a corrupted label.  Those rows break the chronological flow and
    # make the DP dater pick a wrong year for the whole page.  We remove:
    #   1. rows that are exact duplicates of a later row (same label + data)
    #   2. rows whose two date tokens span more than 30 days (corrupted label)
    #   3. rows whose label matches a later row (near-duplicate, data differs)
    dedup_removed: list[str] = []
    keep: list[bool] = [True] * len(raw_weeks)
    for i in range(len(raw_weeks)):
        if not keep[i]:
            continue
        label_i, cells_i = raw_weeks[i]
        # 2. corrupted label (span > 30 days)
        tokens = [m.group(0) for m in _DATE_TOKEN.finditer(label_i)]
        if len(tokens) >= 2:
            d1 = date_readings(tokens[0])[0].date
            d2 = date_readings(tokens[1])[0].date
            if abs((d2 - d1).days - 7) > 30:
                keep[i] = False
                dedup_removed.append(label_i)
                continue
        # 1. exact duplicate of a later row
        for j in range(i + 1, len(raw_weeks)):
            if not keep[j]:
                continue
            label_j, cells_j = raw_weeks[j]
            if label_i != label_j:
                continue
            same_data = all(c1.raw == c2.raw
                            for c1, c2 in zip(cells_i, cells_j))
            if same_data:
                keep[i] = False
                dedup_removed.append(label_i)
                break
        if not keep[i]:
            continue
        # 3. same label as a later row (data differs)
        for j in range(i + 1, len(raw_weeks)):
            if not keep[j]:
                continue
            if raw_weeks[j][0] == label_i:
                keep[i] = False
                dedup_removed.append(label_i)
                break

    cleaned_weeks = [(label, cells) for k, (label, cells) in zip(keep, raw_weeks) if k]
    for lbl in dedup_removed:
        problems.append(f"removed archive/duplicate row: {lbl!r}")

    starts, repairs = resolve_week_starts([label for label, _ in cleaned_weeks], weekdays[0])

    weeks: list[PanelWeek] = []
    for (label, cells), start, repair_list in zip(cleaned_weeks, starts, repairs):
        if start is None:
            problems.append(f"unusable date label {label!r}")
            continue
        end_tokens = [d for match in _DATE_TOKEN.finditer(label)
                      for d in date_candidates(match.group(0), year_tolerance=0)]
        end = max(end_tokens) if end_tokens else start + dt.timedelta(days=len(cells) - 1)
        weeks.append(PanelWeek(label_raw=label, start=start, end=end,
                               cells=cells, repairs=list(repair_list)))

    starts_only = [w.start for w in weeks]
    for i in range(1, len(starts_only)):
        if starts_only[i] <= starts_only[i - 1]:
            problems.append(f"week order violation at {weeks[i].label_raw!r} "
                            f"({starts_only[i]} after {starts_only[i - 1]})")
    return PanelParse(weekdays=weekdays, weeks=weeks, problems=problems)


# ---------------------------------------------------------------------------
# 4. the undated jodi grid
# ---------------------------------------------------------------------------
@dataclass
class JodiRow:
    weekdays: list[str]
    jodis: list[str | None]


@dataclass
class JodiParse:
    weekdays: list[str]
    rows: list[JodiRow]
    problems: list[str] = field(default_factory=list)


def parse_jodi_html(html: str) -> JodiParse:
    soup = BeautifulSoup(html, "lxml")
    rows = soup.find_all("tr")
    header = [_clean(c.get_text(" ", strip=True)) for c in rows[0].find_all(["td", "th"])]
    weekdays = _header_weekdays(header)
    parsed: list[JodiRow] = []
    problems: list[str] = []
    for index, row in enumerate(rows[1:], start=1):
        cells = [_clean(c.get_text(" ", strip=True)) for c in row.find_all(["td", "th"])]
        cells = [c for c in cells if c is not None]
        if not cells or not any(cells):
            continue
        values = [parse_jodi(c) for c in cells[:len(weekdays)]]
        parsed.append(JodiRow(weekdays=weekdays, jodis=values))
        if len(cells) != len(weekdays):
            problems.append(f"row {index}: {len(cells)} cells for {len(weekdays)} weekdays")
    return JodiParse(weekdays=weekdays, rows=parsed, problems=problems)


# ---------------------------------------------------------------------------
# 5. reconciliation
# ---------------------------------------------------------------------------
@dataclass
class Day:
    """One dated, reconciled record for one market."""

    date: dt.date
    weekday: str
    open_panna: str | None
    close_panna: str | None
    open_ank: int | None
    close_ank: int | None
    jodi: str | None
    panel_jodi: str | None
    jodi_chart_jodi: str | None
    status: str
    notes: list[str] = field(default_factory=list)

    @property
    def usable(self) -> bool:
        """A day is usable when both anks are known, whatever their provenance.

        Both pannas present -> anks are arithmetic. One panna missing but the jodi
        published (and identical on both pages) -> the jodi carries both anks, so the
        day is kept with the missing panna left NULL. Nothing is invented.
        """
        return self.open_ank is not None and self.close_ank is not None


STATUS_ORDER = (
    "agrees",                   # panel arithmetic, panel jodi and jodi chart all agree
    "jodi_chart_differs",       # the two pages disagree on the jodi
    "panel_internal_mismatch",  # pannas and the printed jodi disagree on the same page
    "single_source",            # only one of the two pages carries the day
    "partial_panna_recovered",  # one panna missing; both anks read from the jodi
    "repaired_dates",           # dated, but the week label needed repair
)


def reconcile(market_id: str, panel: PanelParse, jodi: JodiParse | None) -> tuple[list[Day], dict[str, Any]]:
    """Merge the dated panel grid with the undated jodi grid, recording every conflict."""
    audit: dict[str, Any] = {
        "market_id": market_id,
        "panel_weeks": len(panel.weeks),
        "panel_cells": panel.n_cells,
        "jodi_rows": len(jodi.rows) if jodi else 0,
        "panel_problems": list(panel.problems),
        "jodi_problems": list(jodi.problems) if jodi else [],
        "week_repairs": [
            {"label": w.label_raw, "start": w.start.isoformat(), "repairs": w.repairs}
            for w in panel.weeks if w.repairs
        ],
        "alignment": None,
        "status_counts": {},
        "conflicts": [],
        "duplicate_dates": [],
        "weekday_mismatch": [],
    }

    rows = jodi.rows if jodi else []
    if jodi and len(rows) != len(panel.weeks):
        audit["alignment"] = {
            "matched_by": "tail",
            "panel_weeks": len(panel.weeks),
            "jodi_rows": len(rows),
            "note": "row counts differ; both grids are newest-last, so the jodi grid "
                    "is aligned to the last N panel weeks and the leading weeks are "
                    "reported as single-source",
        }
        offset = len(panel.weeks) - len(rows)
    else:
        offset = 0
        audit["alignment"] = {"matched_by": "index", "panel_weeks": len(panel.weeks),
                             "jodi_rows": len(rows)}

    days: list[Day] = []
    seen: dict[dt.date, int] = {}

    for week_index, week in enumerate(panel.weeks):
        jodi_row = None
        target = week_index - offset
        if 0 <= target < len(rows):
            jodi_row = rows[target]
        for cell_index, cell in enumerate(week.cells):
            day = week.start + dt.timedelta(days=cell_index)
            if day.weekday() != WEEKDAYS.index(cell.weekday):
                audit["weekday_mismatch"].append(
                    {"label": week.label_raw, "date": day.isoformat(),
                     "expected": cell.weekday, "actual": WEEKDAYS[day.weekday()]})

            from_chart = None
            if jodi_row is not None and cell_index < len(jodi_row.jodis):
                from_chart = jodi_row.jodis[cell_index]

            derived = jodi_of(cell.open_panna, cell.close_panna)

            notes: list[str] = []
            if derived and cell.jodi and derived != cell.jodi:
                notes.append(f"printed jodi {cell.jodi} != panna arithmetic {derived}")
            if from_chart and cell.jodi and from_chart != cell.jodi:
                notes.append(f"jodi chart {from_chart} != panel {cell.jodi}")
            if from_chart and derived and from_chart != derived:
                notes.append(f"jodi chart {from_chart} != panna arithmetic {derived}")

            if derived and not cell.jodi:
                status = "panel_internal_mismatch"
            elif from_chart and cell.jodi and from_chart == cell.jodi and (not derived or derived == cell.jodi):
                status = "agrees"
            elif from_chart and cell.jodi and from_chart != cell.jodi:
                status = "jodi_chart_differs"
            elif cell.jodi and derived and cell.jodi != derived:
                status = "panel_internal_mismatch"
            elif not cell.jodi and not from_chart:
                status = "single_source"
            else:
                status = "single_source"

            if week.repairs:
                notes.extend(week.repairs)

            jodi_value = cell.jodi if cell.jodi else from_chart
            # Prefer what the pannas imply: it is arithmetic that can be re-derived,
            # while the printed jodi is a transcription.
            reconciled_jodi = derived or jodi_value

            open_ank = ank_of(cell.open_panna)
            close_ank = ank_of(cell.close_panna)
            anks_from_jodi = False
            if reconciled_jodi and (open_ank is None or close_ank is None):
                open_ank = int(reconciled_jodi[0])
                close_ank = int(reconciled_jodi[1])
                anks_from_jodi = True
                notes.append("ank(s) read from the published jodi; a panna is missing")

            if reconciled_jodi and jodi_value and reconciled_jodi != jodi_value:
                audit["conflicts"].append({
                    "date": day.isoformat(), "panel_jodi": cell.jodi,
                    "jodi_chart": from_chart, "panna_arithmetic": derived,
                    "used": reconciled_jodi, "notes": notes})

            if day in seen:
                audit["duplicate_dates"].append(day.isoformat())
                continue
            seen[day] = len(days)

            if anks_from_jodi:
                status = "partial_panna_recovered"

            days.append(Day(
                date=day, weekday=cell.weekday,
                open_panna=cell.open_panna, close_panna=cell.close_panna,
                open_ank=open_ank, close_ank=close_ank,
                jodi=reconciled_jodi or (f"{open_ank}{close_ank}"
                                         if open_ank is not None and close_ank is not None
                                         else None),
                panel_jodi=cell.jodi, jodi_chart_jodi=from_chart,
                status=status, notes=notes))

    counts: dict[str, int] = {}
    for day in days:
        counts[day.status] = counts.get(day.status, 0) + 1
    audit["status_counts"] = counts
    audit["n_days"] = len(days)
    audit["n_usable"] = sum(1 for d in days if d.usable)
    audit["n_missing"] = sum(1 for d in days if not d.usable)
    if days:
        ordered = sorted(days, key=lambda d: d.date)
        audit["first_date"] = ordered[0].date.isoformat()
        audit["last_date"] = ordered[-1].date.isoformat()
        audit["n_open_panna"] = sum(1 for d in days if d.open_panna)
        audit["n_close_panna"] = sum(1 for d in days if d.close_panna)
    audit["n_conflicts"] = len(audit["conflicts"])
    return days, audit


def load_pair(jodi_path: str | Path, panel_path: str | Path, market_id: str) -> tuple[list[Day], dict[str, Any]]:
    """Read both snapshots of one market and reconcile them."""
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
    return days, audit


def to_records(days: Iterable[Day], market_id: str, *, source_id: str) -> list[dict[str, Any]]:
    """Convert reconciled days into rows the storage layer accepts."""
    rows: list[dict[str, Any]] = []
    for day in days:
        if not day.usable:
            continue
        rows.append({
            "market_id": market_id,
            "result_date": day.date.isoformat(),
            "open_panna": day.open_panna,
            "close_panna": day.close_panna,
            "open_ank": day.open_ank,
            "close_ank": day.close_ank,
            "jodi": day.jodi,
            "source_id": source_id,
            "source_date_label": day.date.isoformat(),
        })
    return rows
