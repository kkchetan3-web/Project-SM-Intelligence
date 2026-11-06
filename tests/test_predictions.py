"""Prediction-layer tests.

The hard requirements are: probabilities sum to one, a report never silently
includes another market, and a forecast that was not earned is labelled as such.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from src.predictions.prediction_engine import (
    OUTCOME_LABELS,
    Forecast,
    _align,
    latest_result_date,
    next_draw_date,
)


def _forecast(**overrides) -> Forecast:
    probs = {label: 0.1 for label in OUTCOME_LABELS}
    ranked = sorted(probs.items(), key=lambda kv: -kv[1])
    payload = dict(
        market_id="kalyan", target="open", target_date="2021-01-02",
        cutoff_date="2020-12-31", model_name="uniform", model_version="uniform-test",
        mode="baseline_fallback", probs=probs, ranked=[[k, float(v)] for k, v in ranked],
        n_history=627, train_size=627, feature_version="feat-v1",
        dataset="synthetic_null", baseline_name="uniform",
        edge_evidence={"selection": {"baseline_log_loss": 2.3026}},
        notes=["fixture"],
    )
    payload.update(overrides)
    return Forecast(**payload)


def test_next_draw_date_skips_sunday(small_config):
    # 2020-12-31 is a Thursday; +1 = Friday, +2 = Saturday, +3 would be Sunday.
    assert next_draw_date(small_config, "kalyan", "open",
                          after=pd.Timestamp("2020-12-31").date()) == pd.Timestamp("2021-01-01").date()
    assert next_draw_date(small_config, "kalyan", "open",
                          after=pd.Timestamp("2021-01-01").date()) == pd.Timestamp("2021-01-02").date()
    # From Saturday, the next draw is Monday - never Sunday.
    assert next_draw_date(small_config, "kalyan", "open",
                          after=pd.Timestamp("2021-01-02").date()) == pd.Timestamp("2021-01-04").date()


def test_latest_result_date_matches_the_database(small_config):
    from src.storage.market_database import MarketDatabase

    last = latest_result_date(small_config, "kalyan", "open")
    frame = MarketDatabase(small_config, "kalyan").results()
    assert last == frame["result_date"].max().date()


def test_probability_alignment_scatters_missing_classes():
    probs = np.array([0.6, 0.4])
    classes = np.array([2, 7])
    aligned = _align(probs, classes)
    assert aligned.shape == (10,)
    assert aligned.sum() == pytest.approx(1.0)
    assert aligned[2] == pytest.approx(0.6)
    assert aligned[7] == pytest.approx(0.4)
    assert aligned[0] == pytest.approx(0.0)


def test_forecast_probabilities_are_a_distribution():
    forecast = _forecast()
    assert sum(forecast.probs.values()) == pytest.approx(1.0)
    assert len(forecast.ranked) == 10
    values = [p for _, p in forecast.ranked]
    assert values == sorted(values, reverse=True)
    assert forecast.has_demonstrated_edge is False


def test_report_is_single_market_and_states_the_disclaimer():
    from src.predictions.reporting import render_forecast

    report = render_forecast(_forecast())
    assert "Kalyan" in report
    assert "Main Bazar" not in report
    assert "not a prediction service or betting advice" in report
    assert "no candidate model passed promotion" in report


def test_comparison_requires_an_explicit_multi_market_request():
    from src.predictions.reporting import render_comparison

    with pytest.raises(ValueError):
        render_comparison([_forecast()])

    other = _forecast(market_id="main_bazar")
    rendered = render_comparison([_forecast(), other])
    assert "Kalyan" in rendered and "Main Bazar" in rendered
    assert "explicitly requested" in rendered


def test_ledger_scores_a_resolved_forecast_exactly(small_config):
    from src.predictions.prediction_ledger import resolve, summary
    from src.storage.market_database import MarketDatabase

    db = MarketDatabase(small_config, "kalyan")
    frame = db.results()
    row = frame.iloc[-1]
    actual = str(int(row["open_ank"]))
    target_date = str(row["result_date"])[:10]

    probs = {label: 0.1 for label in OUTCOME_LABELS}
    probs[actual] = 0.55
    others = [l for l in OUTCOME_LABELS if l != actual]
    for label in others:
        probs[label] = 0.45 / len(others)
    ranked = sorted(probs.items(), key=lambda kv: -kv[1])

    db.save_predictions([{
        "target": "open", "target_date": target_date,
        "model_version": "ledger-test", "cutoff_date": "2020-01-01",
        "train_size": 100, "feature_version": "feat-v1",
        "probs": probs, "ranked": ranked,
    }])

    result = resolve(small_config, "kalyan", "open")
    assert result["resolved"] >= 1

    ledger = db.ledger()
    row_ledger = ledger[ledger["model_version"] == "ledger-test"].iloc[0]
    assert row_ledger["actual_value"] == actual
    assert row_ledger["rank_of_actual"] == 1
    assert row_ledger["log_loss_i"] == pytest.approx(-math.log(0.55), abs=1e-9)
    assert row_ledger["correct_exact"] == 1

    stats = summary(small_config, "kalyan", "open")
    assert stats["available"] is True
    assert stats["n_resolved"] >= 1
    assert "verdict" in stats
