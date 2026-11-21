"""Tests for the user-supplied chart snapshots: dating, reconciliation, provenance.

The fixtures here are hand-written HTML in the same shape as the saved pages
(``<td>`` cells split by ``<br>``, one ``DD/MM/YYYY to DD/MM/YYYY`` label per week,
three cells per day: open panna, jodi, close panna). They are deliberately small and
deliberately broken in the same ways the real pages are broken, so the repairs are
tested rather than assumed.
"""

from __future__ import annotations

import datetime as dt
import json

import pytest

from src.ingestion.chart_snapshot import (
    ank_of,
    jodi_of,
    parse_jodi_html,
    parse_panel_html,
    reconcile,
    read_snapshot,
)


def _panna(digits: str) -> str:
    return "<br> ".join(digits)


def _panel_html(weeks: list[tuple[str, list[tuple[str, str, str]]]], days=("Mon", "Tue", "Wed", "Thu", "Fri", "Sat")) -> str:
    head = "".join(f'<th colspan="3">{d}</th>' for d in days)
    body = []
    for label, cells in weeks:
        cells_html = "".join(
            f"<td>{_panna(o)}</td><td>{j}</td><td>{_panna(c)}</td>" for o, j, c in cells
        )
        body.append(f"<tr><td> {label} </td>{cells_html}</tr>")
    return (f"<table><thead><tr><th>Date</th>{head}</tr></thead>"
            f"<tbody>{''.join(body)}</tbody></table>")


def _jodi_html(rows: list[list[str]], days=("Mon", "Tue", "Wed", "Thu", "Fri", "Sat")) -> str:
    head = "".join(f"<th>{d}</th>" for d in days)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


# ---------------------------------------------------------------------------
# arithmetic
# ---------------------------------------------------------------------------
def test_ank_and_jodi_are_arithmetic():
    assert ank_of("123") == 6           # 1+2+3
    assert ank_of("000") == 0
    assert ank_of("799") == 5           # 25 -> 5
    assert jodi_of("799", "155") == "51"
    assert jodi_of(None, "155") is None


# ---------------------------------------------------------------------------
# panel parsing and dating
# ---------------------------------------------------------------------------
def test_panel_cells_are_dated_from_the_week_label():
    html = _panel_html([
        ("02/01/2023 to 07/01/2023", [
            ("123", "65", "456"),      # Mon -> 1+2+3=6, 4+5+6=15->5, jodi 65
            ("789", "43", "111"),      # Tue -> 7+8+9=24->4, 1+1+1=3, jodi 43
            ("", "", ""),
        ]),
    ])
    panel = parse_panel_html(html)
    assert panel.weekdays[:3] == ["Mon", "Tue", "Wed"]
    week = panel.weeks[0]
    assert week.start == dt.date(2023, 1, 2)
    assert week.cells[0].open_panna == "123"
    assert week.cells[0].jodi == "65"
    assert week.cells[1].open_panna == "789"
    assert week.cells[2].missing is True


def test_missing_marker_is_not_turned_into_a_value():
    html = _panel_html([("02/01/2023 to 07/01/2023", [("* * *", "**", "* * *")])])
    panel = parse_panel_html(html)
    cell = panel.weeks[0].cells[0]
    assert cell.open_panna is None and cell.jodi is None and cell.close_panna is None
    assert cell.missing is True


def test_year_typo_in_a_label_is_repaired_by_the_weekly_grid():
    """``07/01/2018`` for the week of 2019-01-07 is a real defect on the Kalyan page."""
    html = _panel_html([
        ("31/12/2018 to 05/01/2019", [("111", "22", "333")]),
        ("07/01/2018 to 12/01/2018", [("222", "33", "444")]),   # wrong year
        ("14/01/2019 to 19/01/2019", [("333", "44", "555")]),
    ])
    panel = parse_panel_html(html)
    starts = [w.start for w in panel.weeks]
    assert starts == [dt.date(2018, 12, 31), dt.date(2019, 1, 7), dt.date(2019, 1, 14)]
    assert any("year+1" in repair for repair in panel.weeks[1].repairs)


def test_a_closed_week_is_a_gap_not_a_shift():
    """A market closure must leave a hole; the parser must not slide 40 weeks back."""
    html = _panel_html([
        ("13/01/2020 to 18/01/2020", [("111", "22", "333")]),
        ("10/02/2020 to 15/02/2020", [("222", "33", "444")]),   # 4 weeks missing
        ("17/02/2020 to 22/02/2020", [("333", "44", "555")]),
    ])
    panel = parse_panel_html(html)
    starts = [w.start for w in panel.weeks]
    assert starts == [dt.date(2020, 1, 13), dt.date(2020, 2, 10), dt.date(2020, 2, 17)]
    assert any("gap" in repair for repair in panel.weeks[1].repairs)


def test_first_week_without_a_previous_week_uses_its_own_label():
    html = _panel_html([("31/12/2012 to 05/01/2013", [("799", "51", "155")])])
    panel = parse_panel_html(html)
    assert panel.weeks[0].start == dt.date(2012, 12, 31)


# ---------------------------------------------------------------------------
# reconciliation
# ---------------------------------------------------------------------------
def test_matching_pages_agree_and_nothing_is_flagged():
    panel = parse_panel_html(_panel_html([
        ("02/01/2023 to 07/01/2023", [("123", "65", "456"), ("789", "43", "111")]),
    ]))
    jodi = parse_jodi_html(_jodi_html([["65", "43", ""]]))
    days, audit = reconcile("kalyan", panel, jodi)
    assert [d.jodi for d in days[:2]] == ["65", "43"]
    assert all(d.status == "agrees" for d in days[:2])
    assert audit["n_conflicts"] == 0


def test_panna_arithmetic_beats_a_contradicting_printed_jodi():
    """Real defect: pannas 368 / 339 print jodi 79, but 3+6+8=17->7 and 3+3+9=15->5."""
    panel = parse_panel_html(_panel_html([
        ("11/02/2013 to 16/02/2013", [("368", "79", "339")]),
    ]))
    jodi = parse_jodi_html(_jodi_html([["79", ""]]))
    days, audit = reconcile("kalyan", panel, jodi)
    day = days[0]
    assert day.panel_jodi == "79"
    assert day.jodi == "75"                     # arithmetic, and self-consistent
    assert day.open_ank == 7 and day.close_ank == 5
    assert audit["n_conflicts"] == 1
    assert "panna arithmetic" in day.notes[0]


def test_the_two_pages_disagreeing_is_recorded_not_hidden():
    panel = parse_panel_html(_panel_html([
        ("02/01/2023 to 07/01/2023", [("123", "65", "456")]),
    ]))
    jodi = parse_jodi_html(_jodi_html([["99"]]))
    days, audit = reconcile("kalyan", panel, jodi)
    assert days[0].jodi_chart_jodi == "99"
    assert days[0].jodi == "65"                 # panel wins: it carries the pannas
    assert days[0].status == "jodi_chart_differs"


def test_row_alignment_uses_the_tail_when_counts_differ():
    panel = parse_panel_html(_panel_html([
        ("02/01/2023 to 07/01/2023", [("123", "65", "456")]),
        ("09/01/2023 to 14/01/2023", [("111", "22", "333")]),
    ]))
    jodi = parse_jodi_html(_jodi_html([["22"]]))     # only the newest week
    days, audit = reconcile("kalyan", panel, jodi)
    assert audit["alignment"]["matched_by"] == "tail"
    by_date = {d.date: d for d in days}
    assert by_date[dt.date(2023, 1, 9)].jodi_chart_jodi == "22"
    assert by_date[dt.date(2023, 1, 2)].jodi_chart_jodi is None


# ---------------------------------------------------------------------------
# files and loading
# ---------------------------------------------------------------------------
PANEL_MHTML = """From: <Saved by Blink>
Snapshot-Content-Location: https://dpbossss.com/panel-chart-record/kalyan.php?full_chart
Subject: Kalyan Panel Chart
Date: Sat, 07 Nov 2026 03:38:42 GMT

<html><head><title>Kalyan Panel Chart</title></head><body>
<table><thead><tr><th>Date</th><th colspan="3">Mon</th><th colspan="3">Tue</th></tr></thead>
<tbody>
<tr><td> 02/11/2026<br> to<br> 07/11/2026</td>
  <td>7<br> 8<br> 9</td><td>46</td><td>1<br> 5<br> 0</td>
  <td>6<br> 7<br> 8</td><td>17</td><td>1<br> 2<br> 4</td></tr>
</tbody></table></body></html>
"""

JODI_MHTML = """From: <Saved by Blink>
Snapshot-Content-Location: https://dpbossss.com/jodi-chart-record/kalyan.php
Subject: Kalyan Jodi Chart
Date: Sat, 07 Nov 2026 03:38:33 GMT

<html><head><title>Kalyan Jodi Chart</title></head><body>
<table><thead><tr><th>Mon</th><th>Tue</th></tr></thead>
<tbody><tr><td>46</td><td>17</td></tr></tbody></table></body></html>
"""


def test_snapshot_headers_name_the_real_url(tmp_path):
    path = tmp_path / "kalyan panel chart.txt"
    path.write_text(PANEL_MHTML)
    snap = read_snapshot(path)
    assert snap.kind == "panel"
    assert snap.url.endswith("panel-chart-record/kalyan.php?full_chart")
    assert snap.saved_at.startswith("Sat, 07 Nov 2026")
    assert len(snap.sha256) == 64


def test_import_writes_rows_provenance_and_is_idempotent(tmp_path):
    from src.core.configuration import load_config
    from src.ingestion.snapshot_loading import import_market
    from src.storage.market_database import MarketDatabase

    panel = tmp_path / "kalyan panel chart.txt"
    jodi = tmp_path / "kalyan jodi chart.txt"
    panel.write_text(PANEL_MHTML)
    jodi.write_text(JODI_MHTML)

    config = load_config(dataset="live", database_root=tmp_path / "dbs")
    report = import_market(config, "kalyan", jodi_path=jodi, panel_path=panel,
                           raw_dir=tmp_path / "raw", audit_dir=tmp_path / "audit")
    assert (report.rows_built, report.inserted, report.rejected) == (2, 2, 0)

    db = MarketDatabase(config, "kalyan")
    frame = db.results()
    assert len(frame) == 2
    assert set(frame["verification_status"]) == {"unverified_scrape"}
    assert all(str(u).startswith("https://dpbossss.com/") for u in frame["source_url"])
    assert frame["open_panna"].tolist() == ["789", "678"]
    assert frame["jodi"].tolist() == ["46", "17"]

    with db.session(read_only=True) as conn:
        pages = conn.execute("SELECT url, parse_status FROM source_records").fetchall()
        runs = conn.execute("SELECT status, records_inserted FROM extraction_runs").fetchall()
    assert len(pages) == 2 and {p[1] for p in pages} == {"parsed"}
    assert len(runs) == 2 and {r[0] for r in runs} == {"ok"}

    # A second import of the same snapshots must not duplicate anything.
    again = import_market(config, "kalyan", jodi_path=jodi, panel_path=panel,
                          raw_dir=tmp_path / "raw", audit_dir=tmp_path / "audit")
    assert again.inserted == 0
    assert len(MarketDatabase(config, "kalyan").results()) == 2
    with db.session(read_only=True) as conn:
        assert conn.execute("SELECT COUNT(*) FROM source_records").fetchone()[0] == 4

    audit = json.loads((tmp_path / "audit" / "reconciliation_kalyan.json").read_text())
    assert audit["n_days"] == 2
    assert audit["n_conflicts"] == 0


def test_live_import_refuses_a_synthetic_dataset(tmp_path):
    from src.core.configuration import load_config
    from src.ingestion.snapshot_loading import import_market

    panel = tmp_path / "kalyan panel chart.txt"
    jodi = tmp_path / "kalyan jodi chart.txt"
    panel.write_text(PANEL_MHTML)
    jodi.write_text(JODI_MHTML)
    config = load_config(dataset="synthetic_null", database_root=tmp_path / "dbs")
    with pytest.raises(ValueError, match="live dataset"):
        import_market(config, "kalyan", jodi_path=jodi, panel_path=panel)


def test_report_uses_the_live_wording_when_the_data_is_real(tmp_path):
    """The live report must not carry the 'no real data was extracted' banner."""
    from src.core.configuration import load_config
    from src.ingestion.snapshot_loading import import_market
    from src.reporting.report import build_report

    panel = tmp_path / "kalyan panel chart.txt"
    jodi = tmp_path / "kalyan jodi chart.txt"
    panel.write_text(PANEL_MHTML)
    jodi.write_text(JODI_MHTML)

    config = load_config(dataset="live", database_root=tmp_path / "dbs")
    import_market(config, "kalyan", jodi_path=jodi, panel_path=panel)
    text = build_report(config, markets=["kalyan"], write=False)
    # build_report(write=False) prints; assert on the rendered artefact instead
    path = build_report(config, markets=["kalyan"], write=True)
    rendered = path.read_text()
    assert "These are real published results" in rendered
    assert "no real market history was extracted" not in rendered
    assert "unverified_scrape" in rendered
    assert "Stored results" in rendered
