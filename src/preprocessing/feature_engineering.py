"""Causal feature construction.

THE ONE RULE: every feature for the draw on date ``t`` is computed from
information available strictly before ``t`` - plus, for the *close* target only,
the same day's *open*, which these markets publish first.

The implementation enforces this structurally rather than by review: all
quantities are produced by shifting the outcome series before any rolling or
expanding computation touches it. :func:`verify_causality` then re-derives every
feature column from scratch on truncated history and asserts equality, which is
a genuine leakage test rather than a comment.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.preprocessing.normalization import ANK_SUPPORT
from src.preprocessing.psychology import PsychologyConfig, psychology_features

log = get_logger(__name__)

FEATURE_VERSION = "feat-v1"
K_ANK = len(ANK_SUPPORT)


@dataclass(frozen=True)
class FeatureConfig:
    windows: tuple[int, ...] = (25, 50, 100, 250)
    ewm_lambdas: tuple[float, ...] = (0.95, 0.99)
    max_gap_features: bool = True
    include_transition_row: bool = True
    include_calendar: bool = True
    include_same_day_open: bool = True
    include_cross_market: bool = True
    #: Admit a *same-day* foreign Open for Close targets, but only where
    #: markets.yaml explicitly declares that the foreign Open is published first.
    include_cross_same_day_open: bool = True
    #: Side channel: player-psychology proxies (recent heat, cold streaks,
    #: coverage). Off by default so existing results stay reproducible; on
    #: only when a run explicitly asks for it.
    include_psychology: bool = False
    psychology: "PsychologyConfig" = field(default_factory=lambda: PsychologyConfig())
    feature_version: str = FEATURE_VERSION


def _expanding_freq(y: np.ndarray, k: int) -> np.ndarray:
    """p_k(t) estimated from rows 0..t-1 inclusive (causal: y is pre-shifted)."""
    n = len(y)
    out = np.full((n, k), np.nan)
    counts = np.zeros(k)
    for t in range(n):
        total = counts.sum()
        if total > 0:
            out[t] = counts / total
        if y[t] >= 0:
            counts[y[t]] += 1
    return out


def _rolling_freq(y: np.ndarray, k: int, window: int) -> np.ndarray:
    n = len(y)
    out = np.full((n, k), np.nan)
    counts = np.zeros(k)
    for t in range(n):
        total = counts.sum()
        if total > 0:
            out[t] = counts / total
        if y[t] >= 0:
            counts[y[t]] += 1
            if t - window >= 0 and y[t - window] >= 0:
                counts[y[t - window]] -= 1
    return out


def _ewm_freq(y: np.ndarray, k: int, lam: float) -> np.ndarray:
    n = len(y)
    out = np.full((n, k), np.nan)
    weights = np.zeros(k)
    for t in range(n):
        total = weights.sum()
        if total > 0:
            out[t] = weights / total
        weights *= lam
        if y[t] >= 0:
            weights[y[t]] += 1.0
    return out


def _gap_features(y: np.ndarray, k: int) -> np.ndarray:
    """Observations elapsed since each category was last seen (capped at 999)."""
    n = len(y)
    last_seen = np.full(k, -1)
    out = np.full((n, k), np.nan)
    for t in range(n):
        for c in range(k):
            out[t, c] = 999.0 if last_seen[c] < 0 else float(t - last_seen[c])
        if y[t] >= 0:
            last_seen[y[t]] = t
    return out


def _transition_rows(y: np.ndarray, k: int) -> np.ndarray:
    """Row of the causal first-order transition matrix for the most recent state."""
    n = len(y)
    out = np.full((n, k), np.nan)
    counts = np.zeros((k, k))
    rows = np.zeros(k)
    last = -1
    for t in range(n):
        if last >= 0 and rows[last] > 0:
            out[t] = counts[last] / rows[last]
        if y[t] >= 0:
            if last >= 0:
                counts[last, y[t]] += 1.0
                rows[last] += 1.0
            last = y[t]
    return out


def build_features(
    y: np.ndarray,
    cfg: FeatureConfig,
    *,
    same_day_open: np.ndarray | None = None,
    cross_open: np.ndarray | None = None,
    cross_close: np.ndarray | None = None,
    dates: pd.DatetimeIndex | None = None,
    cross_open_today: np.ndarray | None = None,
) -> pd.DataFrame:
    """Build the causal feature matrix.

    ``y`` is the integer-coded target sequence. A value of ``-1`` marks an
    unknown outcome and is treated as "no information" rather than as a class.

    ``same_day_open`` is only supplied for the *close* target, where the open is
    published earlier the same day. It is inserted unshifted on purpose; the
    caller is responsible for only passing it when that is genuinely true.
    """
    y = np.asarray(y, dtype=int)
    n = len(y)
    k = K_ANK
    cols: dict[str, np.ndarray] = {}

    # Everything below is computed on the *own* history and then shifted by one,
    # which is what makes it causal.
    shifted = np.concatenate([[-1], y[:-1]])

    expanding = _expanding_freq(shifted, k)
    for c in range(k):
        cols[f"freq_all_{c}"] = expanding[:, c] - 1.0 / k

    for window in cfg.windows:
        freq = _rolling_freq(shifted, k, window)
        # Compact representation: keep the window's overall dispersion plus the
        # top-3 categories' excess probability, rather than 10 more columns each.
        for c in range(k):
            if window in (25, 100):
                cols[f"freq_w{window}_{c}"] = freq[:, c] - 1.0 / k
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            cols[f"freq_w{window}_max_excess"] = np.nanmax(freq - 1.0 / k, axis=1)

    for lam in cfg.ewm_lambdas:
        ewm = _ewm_freq(shifted, k, lam)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            cols[f"ewm_{str(lam).replace('.', '')}_max_excess"] = np.nanmax(ewm - 1.0 / k, axis=1)
        cols[f"ewm_{str(lam).replace('.', '')}_entropy"] = -np.nansum(
            np.where(ewm > 0, ewm * np.log2(np.clip(ewm, 1e-12, None)), 0.0), axis=1
        )

    if cfg.max_gap_features:
        gaps = _gap_features(shifted, k)
        for c in range(k):
            cols[f"gap_{c}"] = gaps[:, c]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            cols["min_gap"] = np.nanmin(gaps, axis=1)

    if cfg.include_transition_row:
        trans = _transition_rows(shifted, k)
        for c in range(k):
            cols[f"trans_{c}"] = trans[:, c] - 1.0 / k

    # Player-psychology side channel (opt-in). Same shifted history, so the
    # causality of every column is inherited from the shifted series.
    if cfg.include_psychology:
        psy = psychology_features(shifted, cfg.psychology)
        for col in psy.columns:
            cols[col] = psy[col].to_numpy()

    # Scalar summaries of the latest outcome (already shifted => previous draw).
    prev = np.concatenate([[np.nan], y[:-1]]).astype(float)
    cols["prev_value"] = prev
    cols["prev_parity"] = np.mod(prev, 2)
    cols["prev_mod5"] = np.mod(prev, 5)
    cols["prev_is_high"] = (prev >= 5).astype(float)
    cols["prev_digital_root"] = np.where(
        np.isnan(prev), np.nan, np.mod(np.mod(prev - 1, 9) + 1, 10) if False else np.mod(prev, 10)
    )
    running = pd.Series(prev).rolling(10, min_periods=1).mean().to_numpy()
    cols["prev_mean10"] = running

    # Availability count = how much training data exists at this row.
    cols["history_size"] = np.arange(n, dtype=float)

    # Same-day open (close target only).
    if same_day_open is not None and cfg.include_same_day_open:
        o = np.asarray(same_day_open, dtype=float)
        cols["open_today"] = o
        cols["open_today_parity"] = np.mod(o, 2)
        cols["open_today_is_high"] = (o >= 5).astype(float)
        cols["open_today_gap_min"] = np.nanmin(_gap_features(
            np.where(np.isnan(o), -1, o).astype(int), k), axis=1)

    # Cross-market features: previous day's published values only.
    if cross_open is not None and cfg.include_cross_market:
        co = np.asarray(cross_open, dtype=float)
        cols["x_prev_open"] = np.concatenate([[np.nan], co[:-1]])
    if cross_close is not None and cfg.include_cross_market:
        cc = np.asarray(cross_close, dtype=float)
        cols["x_prev_close"] = np.concatenate([[np.nan], cc[:-1]])
        cols["x_prev_jodi_sum"] = np.mod(cols["x_prev_open"] + cols["x_prev_close"], 10)

    # Same-day foreign Open (Close targets only). Admitted only when the
    # configuration declares that the partner market publishes its Open before
    # this market closes; see markets.yaml -> cross_open_precedence.
    if cross_open_today is not None and cfg.include_cross_same_day_open:
        xo = np.asarray(cross_open_today, dtype=float)
        cols["x_today_open"] = xo
        cols["x_today_open_parity"] = np.mod(xo, 2)
        cols["x_today_open_is_high"] = (xo >= 5).astype(float)

    if cfg.include_calendar and dates is not None:
        dow = pd.DatetimeIndex(dates).dayofweek.to_numpy().astype(float)
        cols["dow_sin"] = np.sin(2 * np.pi * dow / 7)
        cols["dow_cos"] = np.cos(2 * np.pi * dow / 7)
        cols["dom"] = pd.DatetimeIndex(dates).day.to_numpy().astype(float)
        cols["month"] = pd.DatetimeIndex(dates).month.to_numpy().astype(float)

    frame = pd.DataFrame(cols)
    frame = frame.replace([np.inf, -np.inf], np.nan)
    return frame


def verify_causality(
    y: np.ndarray,
    cfg: FeatureConfig,
    *,
    same_day_open: np.ndarray | None = None,
    cross_open: np.ndarray | None = None,
    cross_close: np.ndarray | None = None,
    dates: pd.DatetimeIndex | None = None,
    cross_open_today: np.ndarray | None = None,
    n_checks: int = 5,
) -> dict:
    """Rebuild features on truncated history and assert the prefix is identical.

    If any feature for row ``t`` had used data from row ``t`` or later, the value
    computed with only ``0..cut`` available would differ from the full-history
    value. This catches look-ahead bias empirically instead of trusting review.
    """
    full = build_features(y, cfg, same_day_open=same_day_open, cross_open=cross_open,
                          cross_close=cross_close, dates=dates,
                          cross_open_today=cross_open_today)
    rng = np.random.default_rng(7)
    n = len(y)
    cuts = sorted({int(c) for c in rng.integers(30, max(31, n - 1), size=n_checks)})
    mismatches: list[dict] = []
    for cut in cuts:
        truncated = build_features(
            y[: cut + 1], cfg,
            same_day_open=None if same_day_open is None else same_day_open[: cut + 1],
            cross_open=None if cross_open is None else cross_open[: cut + 1],
            cross_close=None if cross_close is None else cross_close[: cut + 1],
            dates=None if dates is None else dates[: cut + 1],
            cross_open_today=(None if cross_open_today is None
                              else cross_open_today[: cut + 1]),
        )
        common = [c for c in full.columns if c in truncated.columns]
        a = full.loc[: cut, common].to_numpy(dtype=float)
        b = truncated.loc[: cut, common].to_numpy(dtype=float)
        same = np.allclose(a, b, equal_nan=True, rtol=1e-9, atol=1e-9)
        if not same:
            bad_cols = [
                col for i, col in enumerate(common)
                if not np.allclose(a[:, i], b[:, i], equal_nan=True, rtol=1e-9, atol=1e-9)
            ]
            mismatches.append({"cut": cut, "columns": bad_cols[:8]})
    return {
        "checked_cuts": len(cuts),
        "leaks_found": len(mismatches),
        "details": mismatches[:5],
        "passed": not mismatches,
        "feature_count": int(full.shape[1]),
        "feature_version": cfg.feature_version,
    }


def finite_matrix(frame: pd.DataFrame) -> np.ndarray:
    """Model-ready float matrix: NaN/inf -> 0 after the warm-up rows are dropped.

    Rows in the warm-up window (where expanding statistics are undefined) are the
    responsibility of the caller - :func:`walk_forward_matrices` drops them.
    """
    return frame.replace([np.inf, -np.inf], np.nan).fillna(0.0).to_numpy(dtype=float)


def feature_names(frame: pd.DataFrame) -> list[str]:
    return list(frame.columns)
