"""Does a foreign market's history actually improve this market's forecast?

This is the decisive cross-market test. An association can be real, stable and
statistically significant and still be useless, because the target market's own
history may already contain the same information. The only way to know is to run
the *same* model, with the *same* refit schedule, on the *same* evaluation window,
twice: once with only domestic features and once with domestic plus lagged foreign
features.

Features are never allowed to see a foreign value published at or after the target
date (see :mod:`market_alignment`), so the comparison cannot be won by leakage.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.backtesting.metrics import paired_bootstrap_difference
from src.backtesting.walk_forward import batch_walk_forward
from src.core.logging import get_logger
from src.models.market_models import REFIT_SCHEDULE, build
from src.models.close_models import build_frame

log = get_logger(__name__)

CROSS_PREFIXES = ("x_prev",)


def cross_market_columns(frame: pd.DataFrame) -> list[str]:
    return [c for c in frame.columns
            if any(c.startswith(p) for p in CROSS_PREFIXES) or c.startswith("x_")]


def test_feature_value(config, target_market: str, target: str,
                       model_name: str = "logistic",
                       *, refit_every: int | None = None) -> dict:
    """Compare domestic-only versus domestic+foreign feature sets."""
    frame = build_frame(config, target_market, target, verify=False)
    foreign_columns = cross_market_columns(frame.X)
    if not foreign_columns:
        return {"available": False,
                "reason": "no cross-market features were constructed for this market"}

    X_full = np.nan_to_num(frame.X.to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    X_reduced = np.nan_to_num(frame.X.drop(columns=foreign_columns).to_numpy(dtype=float),
                              nan=0.0, posinf=0.0, neginf=0.0)
    y = frame.y
    dates = pd.DatetimeIndex(frame.dates)
    min_train = int(config.research.get("walk_forward", {}).get("min_train_size", 400))
    min_train = min(min_train, max(200, int(len(y) * 0.25)))
    cadence = refit_every or REFIT_SCHEDULE.get(model_name, 80)

    common = dict(min_train=min_train, refit_every=cadence, model_name=model_name,
                  market_id=target_market, target=target)
    reduced = batch_walk_forward(lambda: build(model_name), X_reduced, y, dates, **common)
    full = batch_walk_forward(lambda: build(model_name), X_full, y, dates, **common)

    reduced_ll = float(reduced.per_obs_log_loss().mean())
    full_ll = float(full.per_obs_log_loss().mean())
    diff = paired_bootstrap_difference(full.per_obs_log_loss(), reduced.per_obs_log_loss(),
                                       n_resamples=1000, seed=config.seed())

    return {
        "available": True,
        "target_market": target_market, "target": target, "model": model_name,
        "foreign_features": foreign_columns,
        "n_predictions": int(len(reduced.y_true)),
        "domestic_only_log_loss": round(reduced_ll, 6),
        "domestic_plus_foreign_log_loss": round(full_ll, 6),
        "improvement": round(reduced_ll - full_ll, 6),
        "ci_low": round(diff["ci_low"], 6), "ci_high": round(diff["ci_high"], 6),
        "p_value": round(diff["p_two_sided"], 6),
        "significant_improvement": bool(diff["ci_high"] < 0),
        "verdict": _verdict(reduced_ll - full_ll, diff),
    }


def _verdict(improvement: float, diff: dict) -> str:
    if improvement <= 0:
        return "no improvement: foreign features do not help this market"
    if diff["ci_high"] < 0:
        return "out-of-sample predictive improvement demonstrated"
    return "descriptive improvement only; not distinguishable from zero"


def test_all_pairs(config, model_name: str = "logistic") -> list[dict]:
    results = []
    for market_a, market_b in config.cross_market_pairs:
        for market in (market_a, market_b):
            for target in ("open", "close"):
                log.info("cross-market feature test: %s/%s", market, target)
                try:
                    results.append(test_feature_value(config, market, target, model_name))
                except Exception as exc:  # pragma: no cover
                    results.append({"available": False, "target_market": market,
                                    "target": target, "reason": str(exc)[:200]})
    return results
