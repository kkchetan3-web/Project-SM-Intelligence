"""Close-target model assembly.

The Close is drawn after the same day's Open. In these markets the Open is
published first, so the Open *is* legitimately available to a Close model - and
that is the single most plausible route to real predictive information
(Method 27, Open-to-Close conditional modelling).

Two things this module refuses to do:

* use the same-day Open when the source's publication order says the close is
  published at the same time or earlier (``publication_order`` in markets.yaml);
* use another market's same-day close, which is published after this market's
  close. Only lagged foreign values are admitted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from src.core.configuration import Config
from src.core.logging import get_logger
from src.preprocessing.cleaning import clean_target
from src.preprocessing.feature_engineering import (
    FEATURE_VERSION,
    FeatureConfig,
    build_features,
    verify_causality,
)
from src.preprocessing.normalization import encode_categorical
from src.models.open_models import (
    ModelFrame,
    _cross_market_arrays,
    same_day_foreign_open,
)

log = get_logger(__name__)


def same_day_open_available(config: Config, market_id: str) -> bool:
    """Whether the open is published strictly before the close for this market."""
    market = config.market(market_id)
    order = list(market.publication_order)
    if "open" not in order or "close" not in order:
        return False
    return order.index("open") < order.index("close")


def build_close_frame(config: Config, market_id: str, *, verify: bool = True,
                      feature_cfg: FeatureConfig | None = None) -> ModelFrame:
    market = config.market(market_id)
    result = clean_target(config, market_id, "close")
    if result.frame.empty:
        raise ValueError(f"market '{market_id}' has no close results")

    dates = pd.DatetimeIndex(result.frame["result_date"])
    y = encode_categorical(result.frame["y"].tolist(), list(range(10)))

    open_result = clean_target(config, market_id, "open")
    open_series = (open_result.frame.set_index("result_date")["y"].reindex(dates)
                   if not open_result.frame.empty else pd.Series(index=dates, dtype=float))
    use_open = same_day_open_available(config, market_id)
    same_day_open = open_series.astype(float).to_numpy() if use_open else None
    if not use_open:
        log.warning("%s: publication order does not put open before close; "
                    "same-day open excluded from close features", market_id)

    cross_open, cross_close = _cross_market_arrays(config, market.market_id, "close", dates)
    # Same-day foreign Open: admissible only where markets.yaml declares the
    # partner publishes its Open before this market closes.
    cross_open_today, foreign_partner = same_day_foreign_open(
        config, market.market_id, dates)
    cfg = feature_cfg or FeatureConfig()

    X = build_features(
        y, cfg, same_day_open=same_day_open, cross_open=cross_open,
        cross_close=cross_close, dates=dates, cross_open_today=cross_open_today,
    )
    causality = (
        verify_causality(y, cfg, same_day_open=same_day_open, cross_open=cross_open,
                         cross_close=cross_close, dates=dates,
                         cross_open_today=cross_open_today)
        if verify else {"passed": None, "note": "verification skipped"}
    )
    if verify and not causality["passed"]:
        raise AssertionError(f"causality verification failed for {market_id}/close: {causality}")

    frame = ModelFrame(
        market_id=market.market_id, target="close", X=X, y=y,
        labels=[str(i) for i in range(10)], dates=dates,
        feature_version=FEATURE_VERSION, causality=causality, dataset=config.dataset.name,
    )
    frame.causality["same_day_open_used"] = bool(use_open)
    frame.causality["same_day_foreign_open_used"] = bool(cross_open_today is not None)
    frame.causality["foreign_partner"] = foreign_partner
    return frame


def build_frame(config: Config, market_id: str, target: str, **kwargs: Any) -> ModelFrame:
    """Dispatch to the right assembly function for a target."""
    if target == "open":
        from src.models.open_models import build_open_frame
        return build_open_frame(config, market_id, **kwargs)
    if target == "close":
        return build_close_frame(config, market_id, **kwargs)
    raise ValueError(f"unsupported target '{target}' (expected 'open' or 'close')")


def feature_documentation(frame: ModelFrame) -> list[dict[str, Any]]:
    """Every feature with its meaning - required by Section 16.

    Grouped by prefix so the documentation stays readable at 60+ features.
    """
    groups = {
        "freq_all": ("Expanding relative frequency of each outcome, centred on 1/K. "
                     "Tests whether long-run imbalance carries over."),
        "freq_w": ("Rolling-window relative frequency. W25/W100 expose recent imbalance; "
                   "the *_max_excess variants keep the strongest deviation only."),
        "ewm": ("Exponentially weighted frequency, dispersion and entropy. Recency-sensitive "
                "view of the marginal."),
        "gap": ("Draws elapsed since each outcome last appeared (999 = never seen). "
                "The 'due number' hypothesis, made measurable."),
        "min_gap": ("Shortest current gap across outcomes."),
        "trans": ("Row of the causal first-order transition matrix for the last outcome, "
                  "centred on 1/K. Feeds the Markov hypotheses into the learned models."),
        "prev_": ("Properties of the previous draw: value, parity, mod-5 residue, high/low, "
                  "short-run mean."),
        "open_today": ("Same-day Open (Close models only; the Open is published first). "
                       "Direct encoding of the Open-to-Close hypothesis."),
        "x_prev": ("Lagged values from the paired market (previous day only - never same day)."),
        "dow_/dom/month": ("Calendar position, known in advance. Tests calendar effects."),
        "history_size": ("Number of observations available at this row; lets models "
                         "learn how much to trust the rest."),
    }

    def group_of(name: str) -> str:
        for prefix in ("freq_all", "freq_w", "ewm", "min_gap", "gap", "trans",
                       "open_today", "x_prev", "dow_", "dom", "month", "prev_"):
            if name.startswith(prefix):
                return prefix
        return "history_size"

    out = []
    for name in frame.X.columns:
        grp = group_of(name)
        description = groups.get(grp, ("",))[0]
        out.append({
            "feature": name, "group": grp, "description": description,
            "target": frame.target, "causal": True,
            "feature_version": frame.feature_version,
        })
    return out
