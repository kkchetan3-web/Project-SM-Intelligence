"""Open-target model assembly.

The Open of date ``t`` is drawn before anything else about date ``t`` is known,
so its feature set is strictly the history of past draws. Nothing from the same
day is admissible - not the close, not another market's same-day result (those
are published later).

Cross-market features are permitted because they are all lagged by at least one
day, which makes them available before the open is announced.
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

log = get_logger(__name__)


@dataclass
class ModelFrame:
    market_id: str
    target: str
    X: pd.DataFrame
    y: np.ndarray
    labels: list[str]
    dates: pd.DatetimeIndex
    feature_version: str
    causality: dict[str, Any]
    dataset: str

    @property
    def n(self) -> int:
        return len(self.y)

    def head(self, k: int = 5) -> pd.DataFrame:
        out = self.X.head(k).copy()
        out.insert(0, "date", self.dates[:k])
        out.insert(1, "y", self.y[:k])
        return out


def _aligned_series(config: Config, market_id: str, target: str,
                    dates: pd.DatetimeIndex) -> pd.Series:
    result = clean_target(config, market_id, target)
    if result.frame.empty:
        return pd.Series(index=dates, dtype=float)
    series = result.frame.set_index("result_date")["y"]
    return series.reindex(dates)


def _cross_market_arrays(config: Config, market_id: str, target: str,
                         dates: pd.DatetimeIndex) -> tuple[np.ndarray | None, np.ndarray | None]:
    """Previous-day open/close of each paired market, aligned onto ``dates``.

    Only *lagged* values are ever returned: the cross-market engine may not use a
    same-day foreign result for an Open, because that result is published later.
    """
    partners = [b if a == market_id else a for a, b in config.cross_market_pairs
                if market_id in (a, b)]
    if not partners:
        return None, None
    partner = partners[0]
    try:
        open_series = _aligned_series(config, partner, "open", dates).astype(float)
        close_series = _aligned_series(config, partner, "close", dates).astype(float)
    except KeyError:
        return None, None
    if open_series.isna().all():
        return None, None
    return open_series.to_numpy(), close_series.to_numpy()


def same_day_foreign_open(config: Config, market_id: str, dates: pd.DatetimeIndex,
                           ) -> tuple[np.ndarray | None, str | None]:
    """The partner market's *same-day* Open, if the configuration admits it.

    Returns ``(values, partner_market_id)`` or ``(None, None)``. The channel exists
    only where ``markets.yaml`` declares ``cross_open_precedence: [[partner, market]]``
    meaning the partner's Open is published before this market closes.
    """
    for partner, target_market in config.cross_open_precedence:
        if target_market != market_id:
            continue
        try:
            series = _aligned_series(config, partner, "open", dates).astype(float)
        except KeyError:
            continue
        if series.isna().all():
            continue
        return series.to_numpy(dtype=float), partner
    return None, None


def build_open_frame(config: Config, market_id: str, *, verify: bool = True,
                     feature_cfg: FeatureConfig | None = None) -> ModelFrame:
    market = config.market(market_id)
    spec = market.target("open")
    result = clean_target(config, market_id, "open")
    if result.frame.empty:
        raise ValueError(f"market '{market_id}' has no open results")

    dates = pd.DatetimeIndex(result.frame["result_date"])
    y_labels = result.frame["y"].tolist()
    y = encode_categorical(y_labels, list(range(10)))

    cross_open, cross_close = _cross_market_arrays(config, market.market_id, "open", dates)
    cfg = feature_cfg or FeatureConfig()

    X = build_features(
        y, cfg, same_day_open=None, cross_open=cross_open, cross_close=cross_close,
        dates=dates,
    )
    causality = (
        verify_causality(y, cfg, cross_open=cross_open, cross_close=cross_close, dates=dates)
        if verify else {"passed": None, "note": "verification skipped"}
    )
    if verify and not causality["passed"]:
        raise AssertionError(f"causality verification failed for {market_id}/open: {causality}")

    return ModelFrame(
        market_id=market.market_id, target="open", X=X, y=y,
        labels=[str(i) for i in range(10)], dates=dates,
        feature_version=FEATURE_VERSION, causality=causality, dataset=config.dataset.name,
    )
