"""Backtesting tests.

The most important test in this file is :func:`test_walk_forward_ignores_future_values`:
if predictions for early steps change when later data changes, the walk-forward is
not walk-forward and every number it produces is worthless.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.backtesting.baselines import make_baselines
from src.backtesting.metrics import (
    accuracy,
    brier,
    evaluate,
    log_loss,
    per_observation_log_loss,
    rank_of_actual,
    uniform_reference,
)
from src.backtesting.validation import best_baseline, decide
from src.backtesting.walk_forward import batch_walk_forward, online_walk_forward

K = 10


def _uniform(n: int) -> np.ndarray:
    return np.full((n, K), 1.0 / K)


def test_log_loss_of_uniform_is_log_ten():
    y = np.random.default_rng(0).integers(0, K, 500)
    assert log_loss(_uniform(500), y) == pytest.approx(np.log(K))
    assert brier(_uniform(500), y) == pytest.approx(0.9, abs=1e-12)
    assert accuracy(_uniform(500), y) == pytest.approx(0.1, abs=0.05)


def test_duplicate_dates_argument_and_per_observation_shapes():
    y = np.random.default_rng(1).integers(0, K, 300)
    probs = _uniform(300)
    per_obs = per_observation_log_loss(probs, y)
    assert per_obs.shape == (300,)
    assert per_obs.mean() == pytest.approx(log_loss(probs, y))
    assert per_obs.min() > 0


def test_rank_of_actual_is_one_based_and_correct():
    probs = np.array([[0.1] * K, [0.5] + [0.5 / 9] * 9])
    ranks = rank_of_actual(probs, np.array([0, 0]))
    assert ranks[0] >= 1
    assert ranks[1] == 1


def test_evaluate_matches_uniform_reference():
    y = np.random.default_rng(2).integers(0, K, 1000)
    metrics = evaluate(_uniform(1000), y).as_dict()
    reference = uniform_reference(K)
    assert metrics["log_loss"] == pytest.approx(reference["log_loss"], abs=1e-6)
    assert metrics["brier"] == pytest.approx(reference["brier"], abs=1e-6)
    assert metrics["ece"] <= 0.05


def test_baselines_produce_normalised_distributions():
    for model in make_baselines():
        model.reset(K)
        for value in np.random.default_rng(3).integers(0, K, 200):
            model.update(int(value))
        probs = model.predict()
        assert probs.shape == (K,)
        assert probs.sum() == pytest.approx(1.0)
        assert (probs >= 0).all(), model.name


def test_online_walk_forward_uses_only_past_data():
    rng = np.random.default_rng(4)
    y = rng.integers(0, K, 400)
    dates = pd.date_range("2020-01-01", periods=400, freq="D")
    before = online_walk_forward(make_baselines(), y, dates, min_train=100,
                                 market_id="t", target="open")
    tampered = y.copy()
    tampered[250:] = (tampered[250:] + 3) % K  # change only "future" outcomes
    after = online_walk_forward(make_baselines(), tampered, dates, min_train=100,
                                market_id="t", target="open")
    cut = 250 - 100  # index within the prediction window
    assert before.keys() == after.keys()
    for name in before:
        assert np.allclose(before[name].probs[:cut], after[name].probs[:cut]), (
            f"{name}: predictions for steps before the change were affected by later data")


def test_batch_walk_forward_ignores_future_values():
    from src.models.market_models import build

    rng = np.random.default_rng(5)
    X = rng.normal(size=(300, 6))
    y = rng.integers(0, K, 300)
    dates = pd.date_range("2020-01-01", periods=300, freq="D")
    before = batch_walk_forward(lambda: build("logistic"), X, y, dates,
                                min_train=150, refit_every=50, model_name="logistic")
    X2, y2 = X.copy(), y.copy()
    X2[220:] += 5.0
    y2[220:] = (y2[220:] + 4) % K
    after = batch_walk_forward(lambda: build("logistic"), X2, y2, dates,
                               min_train=150, refit_every=50, model_name="logistic")
    cut = 220 - 150
    assert np.allclose(before.probs[:cut], after.probs[:cut], atol=1e-12)
    assert before.probs.shape[1] == K
    assert np.allclose(before.probs.sum(axis=1), 1.0, atol=1e-9)


def test_decide_rejects_a_model_that_only_matches_its_baseline():
    rng = np.random.default_rng(6)
    y = rng.integers(0, K, 300)
    dates = pd.date_range("2020-01-01", periods=300, freq="D")
    results = online_walk_forward(make_baselines(), y, dates, min_train=100,
                                  market_id="t", target="open")
    name = best_baseline(results)
    verdict = decide(results[name], results, min_improvement=0.002)
    assert verdict.promoted is False
    assert verdict.reasons


def test_missing_classes_do_not_shrink_the_probability_vector():
    """A refit on a subset that never saw some outcomes must still output K columns."""
    rng = np.random.default_rng(7)
    y = rng.integers(0, K, 300)
    y[:200] = np.where(y[:200] > 4, y[:200] % 5, y[:200])  # top classes only appear later
    X = rng.normal(size=(300, 4))
    dates = pd.date_range("2020-01-01", periods=300, freq="D")
    from src.models.market_models import build

    result = batch_walk_forward(lambda: build("logistic"), X, y, dates,
                                min_train=150, refit_every=200, model_name="logistic")
    assert result.probs.shape[1] == K
