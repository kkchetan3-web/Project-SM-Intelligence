"""Tests for the bidding-quotes loader and pressure channel.

The feed format, the upsert semantics and the pressure channel are pinned
here with fixtures. No test touches the repository's real databases.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from src.core.configuration import load_config
from src.ingestion.bidding import (bidding_pressure_features, import_bidding,
                                   read_feed)


@pytest.fixture()
def live_config(tmp_path):
    return load_config(dataset="live", database_root=tmp_path / "db")


# ---------------------------------------------------------------------------
# feed reading
# ---------------------------------------------------------------------------
def test_read_feed_csv(fixture_dir):
    rows = read_feed(fixture_dir / "bidding_feed_kalyan.csv")
    assert len(rows) == 8
    assert rows[0]["result_date"] == "2026-11-04"
    assert rows[0]["quote_side"] == "open"
    assert rows[0]["ank"] == 5
    assert rows[0]["rate"] == pytest.approx(0.85)


def test_read_feed_json(tmp_path):
    feed = [
        {"date": "2026-11-05", "side": "open", "ank": 5, "rate": 0.82, "volume": 15000},
        {"date": "2026-11-05", "side": "close", "ank": 1, "rate": 0.86},
    ]
    path = tmp_path / "feed.json"
    path.write_text(json.dumps(feed))
    rows = read_feed(path)
    assert rows[0]["quote_side"] == "open"
    assert rows[1]["volume"] is None  # absent volume stays absent


def test_read_feed_rejects_bad_rows(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("date,side,ank,rate\n2026-11-05,side,5,0.9\n")  # side not open/close
    with pytest.raises(ValueError, match="open/close"):
        read_feed(path)

    path.write_text("date,side,ank,rate\n2026-11-05,open,12,0.9\n")  # ank out of range
    with pytest.raises(ValueError, match="0..9"):
        read_feed(path)

    path.write_text("date,side,ank,rate\n2026-11-05,open,5,1.5\n")  # rate > 1 rupee
    with pytest.raises(ValueError, match="rupees"):
        read_feed(path)


# ---------------------------------------------------------------------------
# import
# ---------------------------------------------------------------------------
def test_import_bidding_inserts_and_audits(live_config, fixture_dir):
    report = import_bidding(live_config, "kalyan",
                            fixture_dir / "bidding_feed_kalyan.csv",
                            source_url="https://example.com/rates")
    assert report.rows_read == 8
    assert report.inserted == 8
    assert report.updated == 0
    assert report.run_id is not None

    db = live_config.database_path("kalyan")
    import sqlite3

    conn = sqlite3.connect(db)
    quotes = conn.execute("SELECT COUNT(*) FROM bidding_quotes").fetchone()[0]
    assert quotes == 8
    runs = conn.execute("SELECT rows_read, rows_inserted FROM bidding_feed_runs").fetchall()
    assert runs == [(8, 8)]


def test_reimport_updates_quotes(live_config, tmp_path):
    feed = tmp_path / "feed.csv"
    feed.write_text("date,side,ank,rate\n2026-11-05,open,5,0.90\n")
    report = import_bidding(live_config, "kalyan", feed)
    assert report.inserted == 1

    feed.write_text("date,side,ank,rate\n2026-11-05,open,5,0.78\n")
    report2 = import_bidding(live_config, "kalyan", feed)
    assert report2.updated == 1
    assert report2.inserted == 0

    import sqlite3

    conn = sqlite3.connect(live_config.database_path("kalyan"))
    rate = conn.execute(
        "SELECT rate FROM bidding_quotes WHERE result_date='2026-11-05' "
        "AND quote_side='open' AND ank=5").fetchone()[0]
    assert rate == pytest.approx(0.78)


def test_import_refuses_control_world(tmp_path):
    from src.ingestion.synthetic_control import ControlSpec, build_dataset
    from datetime import date

    config = load_config(dataset="synthetic_null", database_root=tmp_path / "synth")
    build_dataset(config, ControlSpec(name="synthetic_null", start=date(2024, 1, 1),
                                      end=date(2024, 3, 31),
                                      open_persistence=0.0, close_persistence=0.0,
                                      marginal_tilt=0.0, cross_market_strength=0.0,
                                      seed=7))
    feed = tmp_path / "feed.csv"
    feed.write_text("date,side,ank,rate\n2026-11-05,open,5,0.90\n")
    with pytest.raises(ValueError, match="live dataset"):
        import_bidding(config, "kalyan", feed)


# ---------------------------------------------------------------------------
# pressure channel
# ---------------------------------------------------------------------------
def test_pressure_channel_is_inverse_rate_and_aligned():
    quotes = pd.DataFrame({
        "result_date": pd.to_datetime(["2026-11-04", "2026-11-05"]),
        "quote_side": ["open", "open"],
        "ank": [5, 5],
        "rate": [0.80, 0.50],  # lower quote = more pressure
    })
    dates = pd.DatetimeIndex(pd.to_datetime(
        ["2026-11-01", "2026-11-04", "2026-11-05", "2026-11-06"]))
    out = bidding_pressure_features(quotes, dates)
    assert out["bid_press_open_5"].iloc[1] == pytest.approx(1.0 / 0.80 - 1.0)
    assert out["bid_press_open_5"].iloc[2] == pytest.approx(1.0 / 0.50 - 1.0)
    assert pd.isna(out["bid_press_open_5"].iloc[0])  # before any quotes
    assert pd.isna(out["bid_press_open_5"].iloc[3])  # after the last quote
    assert np.isnan(out["bid_max_open"].iloc[0])


def test_pressure_channel_empty_feed_is_all_nan():
    dates = pd.DatetimeIndex(pd.to_datetime(["2026-11-05"]))
    out = bidding_pressure_features(pd.DataFrame(), dates)
    assert len(out.columns) == 20  # one per-ank column per side
    assert out.isna().all().all()
