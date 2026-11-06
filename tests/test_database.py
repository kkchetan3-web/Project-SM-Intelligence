"""Storage tests: isolation, idempotency, revisions, provenance, integrity."""

from __future__ import annotations

import pytest

from src.core.validation import ValidationError
from src.storage.database_manager import DatabaseManager
from src.storage.market_database import MarketDatabase
from src.storage.schema import REQUIRED_TABLES


def test_each_market_gets_its_own_file(small_config):
    manager = DatabaseManager(small_config)
    paths = {m: manager.path_for(m) for m in small_config.market_order}
    assert len(set(paths.values())) == len(paths)
    for market_id, path in paths.items():
        assert path.exists()
        assert path.parent.name == market_id
        assert path.name == f"{market_id}.db"


def test_all_required_tables_exist(small_config):
    for market_id in small_config.market_order:
        info = DatabaseManager(small_config).integrity_check(market_id)
        assert info["missing_tables"] == []
        assert info["pragma"] == "ok"
        assert set(REQUIRED_TABLES).issubset(set(info["row_counts"]))


def test_market_ids_never_mix(small_config):
    for market_id in small_config.market_order:
        frame = MarketDatabase(small_config, market_id).results()
        assert not frame.empty
        assert set(frame["market_id"]) == {market_id}


def test_upsert_is_idempotent(small_config):
    db = MarketDatabase(small_config, "kalyan")
    before = len(db.results())
    existing = db.results().iloc[0].to_dict()
    row = {
        "result_date": existing["result_date"],
        "open_panna": existing["open_panna"], "open_ank": existing["open_ank"],
        "close_panna": existing["close_panna"], "close_ank": existing["close_ank"],
        "jodi": existing["jodi"], "source_id": existing["source_id"],
        "verification_status": existing["verification_status"],
    }
    outcome = db.upsert_results([row])
    assert outcome.inserted == 0
    assert outcome.unchanged == 1
    assert len(db.results()) == before


def test_changed_value_is_revised_not_overwritten(small_config):
    db = MarketDatabase(small_config, "main_bazar")
    existing = db.results().iloc[-1].to_dict()
    revised_close = (int(existing["close_ank"]) + 1) % 10
    row = {
        "result_date": existing["result_date"],
        "open_panna": existing["open_panna"], "open_ank": existing["open_ank"],
        "close_panna": existing["close_panna"], "close_ank": revised_close,
        "source_id": "correction_test",
        "verification_status": existing["verification_status"],
        "notes": "fixture revision",
    }
    outcome = db.upsert_results([row])
    assert outcome.revised == 1
    log = db.revision_log()
    assert not log.empty
    # The original value is preserved in the audit log, not lost.
    previous = str(log.iloc[-1]["old_value"])
    assert str(existing["jodi"]) in previous or str(existing["close_ank"]) in previous


def test_record_without_any_component_is_rejected(small_config):
    db = MarketDatabase(small_config, "kalyan")
    outcome = db.upsert_results([{"result_date": "2020-06-01",
                                  "verification_status": "synthetic_control"}])
    assert outcome.rejected == 1
    assert outcome.errors


def test_live_status_is_refused_inside_a_synthetic_dataset(small_config):
    """The isolation guard is the single most important safety property."""
    from src.core.validation import assert_dataset_isolation

    db = MarketDatabase(small_config, "kalyan")
    outcome = db.upsert_results([{
        "result_date": "2020-06-02", "open_ank": 3, "close_ank": 4,
        "verification_status": "unverified_scrape", "source_url": "https://example.invalid/x",
    }])
    assert outcome.rejected == 1, "a live-labelled row must not enter a synthetic tree"
    with pytest.raises(ValidationError):
        assert_dataset_isolation("synthetic_null", "unverified_scrape")
    with pytest.raises(ValidationError):
        assert_dataset_isolation("live", "synthetic_control")


def test_synthetic_status_is_refused_inside_the_live_tree():
    from src.core.validation import assert_dataset_isolation

    with pytest.raises(ValidationError):
        assert_dataset_isolation("live", "synthetic_control")


def test_dataset_identity_is_recorded(small_config):
    identity = MarketDatabase(small_config, "kalyan").identity()
    assert identity["market_id"] == "kalyan"
    assert identity["dataset"] == "synthetic_null"
    assert identity["schema_version"] == "3"


def test_coverage_reports_span_and_gaps(small_config):
    coverage = MarketDatabase(small_config, "kalyan").coverage()
    assert coverage["n_records"] > 500
    assert coverage["oldest"] <= coverage["newest"]
    assert coverage["by_component"]["open_ank"] == coverage["n_records"]
    assert coverage["duplicate_dates"] == 0
    assert 0 < coverage["coverage_pct"] <= 100


def test_generation_provenance_is_recorded_and_idempotent(small_config):
    """The control data's audit trail must say *generated*, and must not duplicate."""
    from src.ingestion.synthetic_control import NULL_SPEC, record_generation_provenance

    db = MarketDatabase(small_config, "kalyan")

    def counts() -> tuple[int, int]:
        with db.session(read_only=True) as conn:
            return (
                conn.execute("SELECT COUNT(*) FROM extraction_runs "
                             "WHERE source_id = 'synthetic_generator'").fetchone()[0],
                conn.execute("SELECT COUNT(*) FROM source_records "
                             "WHERE source_id = 'synthetic_generator'").fetchone()[0],
            )

    before = counts()
    first = record_generation_provenance(small_config, "kalyan", NULL_SPEC,
                                        n_rows=10, inserted=10, when="2020-01-01T00:00:00Z")
    assert first is not None
    second = record_generation_provenance(small_config, "kalyan", NULL_SPEC,
                                         n_rows=10, inserted=10, when="2020-01-01T00:00:00Z")
    assert second is None, "a repeated backfill of the same spec must not append a run"

    after = counts()
    assert after[0] == before[0] + 1, "exactly one new run"
    assert after[1] == before[1] + 1, "exactly one new source record"

    with db.session(read_only=True) as conn:
        run = conn.execute(
            "SELECT status, records_inserted FROM extraction_runs "
            "WHERE source_id = 'synthetic_generator' "
            "ORDER BY run_id DESC LIMIT 1").fetchone()
        page = conn.execute(
            "SELECT url, parse_status FROM source_records "
            "WHERE source_id = 'synthetic_generator' "
            "ORDER BY source_record_id DESC LIMIT 1").fetchone()
    assert run[0] == "ok"
    assert run[1] == 10
    assert page[0].startswith("synthetic://")
    assert page[1] == "generated"
