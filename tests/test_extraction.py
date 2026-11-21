"""Parsing and record-merging tests.

The parsers are the only part of the ingestion pipeline that can be tested without
network access, and they are also where silent corruption would begin, so they are
tested against fixed HTML fixtures rather than against the live sites.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.ingestion.extraction import (
    ParsedRecord,
    extract_date,
    find_merge_conflicts,
    merge_records,
    parse_jodi_chart,
    parse_panel_chart,
    parse_panna_token,
)


def test_jodi_chart_parses_dates_and_both_digits(fixture_dir):
    html = (fixture_dir / "jodi_chart.html").read_text()
    records = parse_jodi_chart(html)
    assert len(records) == 5
    first = records[0]
    assert first.result_date == date(2020, 1, 1)
    assert first.jodi == "57"
    # The two digits of the jodi ARE the open and close ank.
    assert (first.open_ank, first.close_ank) == (5, 7)


def test_jodi_parser_does_not_read_the_date_as_the_jodi(fixture_dir):
    """Regression: a bare day cell ("03") is a valid 2-digit jodi pattern."""
    html = (fixture_dir / "jodi_chart.html").read_text()
    records = parse_jodi_chart(html)
    assert [r.jodi for r in records[:3]] == ["57", "13", "00"]
    for record in records:
        assert record.jodi == f"{record.open_ank}{record.close_ank}"


def test_month_header_sets_the_year(fixture_dir):
    records = parse_jodi_chart((fixture_dir / "jodi_chart.html").read_text())
    assert {r.result_date.year for r in records} == {2020}
    assert {r.result_date.month for r in records} == {1, 2}


def test_panel_chart_parses_panna_and_consistent_ank(fixture_dir):
    records = parse_panel_chart((fixture_dir / "panel_chart.html").read_text())
    assert len(records) == 2
    first = records[0]
    assert first.open_panna == "128"
    assert first.open_ank == 1
    assert first.close_panna == "450"
    assert first.close_ank == 9
    assert first.jodi == "19"
    # panna -> ank is the digit sum mod 10; the parser must not invent an ank.
    for record in records:
        assert record.open_ank == sum(int(c) for c in record.open_panna) % 10
        assert record.close_ank == sum(int(c) for c in record.close_panna) % 10


@pytest.mark.parametrize("token,expected", [
    ("128-1", ("128", 1)),
    ("128", ("128", 1)),          # derived from the digit sum
    ("000-0", ("000", 0)),
    ("999", ("999", 7)),
])
def test_parse_panna_token(token, expected):
    assert parse_panna_token(token) == expected


@pytest.mark.parametrize("cell", ["01/02/2020", "1-2-2020", "01 Feb 2020"])
def test_extract_date_accepts_common_formats(cell):
    assert extract_date(cell) == date(2020, 2, 1)


def test_merge_fills_gaps_and_flags_conflicts():
    jodi_records = [
        ParsedRecord(result_date=date(2020, 1, 1), jodi="57", open_ank=5, close_ank=7),
        ParsedRecord(result_date=date(2020, 1, 2), jodi="13", open_ank=1, close_ank=3),
    ]
    panel_records = [
        ParsedRecord(result_date=date(2020, 1, 1), open_panna="128", open_ank=1,
                     close_panna="450", close_ank=9, jodi="19"),
    ]
    merged = merge_records(jodi_records, panel_records)
    assert len(merged) == 2
    # Both sources describe 1 January and they disagree -> flagged, not averaged.
    conflicts = find_merge_conflicts(merged)
    assert conflicts, "a jodi/panel disagreement must be reported, never silently resolved"
