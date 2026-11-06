"""Data-quality checks.

The checks are the gate between "records exist" and "records may be modelled".
These tests verify that the gate actually closes on bad data, not merely that it
opens on good data.
"""

from __future__ import annotations

import sqlite3

from src.preprocessing.quality_checks import gate, run_quality_checks
from src.storage.market_database import MarketDatabase


def test_clean_control_world_passes(small_config):
    report = run_quality_checks(small_config, "kalyan", persist=False)
    assert report.ok, [f"{i.check}: {i.detail}" for i in report.errors]
    assert report.n_records > 500


def test_gate_returns_actionable_summary(small_config):
    result = gate(small_config, "main_bazar")
    assert result["ok"] is True
    assert result["errors"] == []
    assert result["n_records"] > 0


def test_panna_ank_inconsistency_is_reported(small_config):
    """A panna whose digit sum contradicts the stored ank is a warning, never silent."""
    db = MarketDatabase(small_config, "kalyan")
    row = db.results().iloc[5]
    with db.session() as conn:
        conn.execute(
            "UPDATE historical_results SET open_panna = ? WHERE record_id = ?",
            ("999", int(row["record_id"])),
        )
        conn.commit()
    report = run_quality_checks(small_config, "kalyan", persist=False)
    checks = {i.check: i for i in report.issues}
    assert checks["open_panna_ank_consistent"].passed is False
    assert checks["open_panna_ank_consistent"].severity == "warning"
    assert checks["open_panna_ank_consistent"].value == 1


def test_schema_refuses_impossible_values(small_config):
    """Impossible values are rejected by the schema before quality checks see them."""
    import sqlite3

    import pytest

    db = MarketDatabase(small_config, "kalyan")
    row = db.results().iloc[7]
    with pytest.raises(sqlite3.IntegrityError):
        with db.session() as conn:
            conn.execute(
                "UPDATE historical_results SET close_ank = 12 WHERE record_id = ?",
                (int(row["record_id"]),),
            )
    report = run_quality_checks(small_config, "kalyan", persist=False)
    assert report.ok


def test_duplicate_dates_cannot_be_inserted_twice(small_config):
    import sqlite3

    import pytest

    db = MarketDatabase(small_config, "main_bazar")
    row = db.results().iloc[3]
    with pytest.raises(sqlite3.IntegrityError):
        with db.session() as conn:
            conn.execute(
                """INSERT INTO historical_results
                   (market_id, result_date, open_ank, close_ank, jodi, source_id,
                    extraction_timestamp, verification_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (row["market_id"], str(row["result_date"])[:10], int(row["open_ank"]),
                 int(row["close_ank"]), row["jodi"], "duplicate_test",
                 str(row["extraction_timestamp"]), row["verification_status"]),
            )
            conn.commit()
    report = run_quality_checks(small_config, "main_bazar", persist=False)
    checks = {i.check: i for i in report.issues}
    assert checks["unique_dates"].passed is True


def test_quality_rows_are_persisted(small_config):
    db = MarketDatabase(small_config, "kalyan")
    run_quality_checks(small_config, "kalyan", persist=True)
    stored = db.latest_quality()
    assert not stored.empty
    assert "check_name" in stored.columns
