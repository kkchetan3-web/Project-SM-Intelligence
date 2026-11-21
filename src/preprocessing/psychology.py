"""Player-psychology proxies derived from published history.

These features model what players *bet on* - not what will happen. They are
side-channel proxies for three documented biases:

* **availability / hot hand**: recent winners attract attention and money, so
  recent frequency is a proxy for where the public is looking;
* **gambler's fallacy**: numbers that have not appeared for a while are
  believed to be "due", so the gap since each ank last appeared proxies the
  pressure to bet on it;
* **engagement / coverage**: how many distinct anks the recent window has
  touched - a crude measure of how "alive" the market feels to players.

A jodi channel (open and close combined) is provided separately because the
jodi needs both series. Nothing here is claimed to predict the next draw: the
channel is a *description of public attention*, and whether attention moves
the result is an empirical question the backtest answers.

All features are causal: row ``t`` is computed from draws strictly before
``t``, exactly like the main feature matrix.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd

K_ANK = 10
_JODI = 100
_GAP_CAP = 999.0


@dataclass
class PsychologyConfig:
    """Knobs for the psychology channel. Defaults are deliberately compact."""

    heat_windows: tuple[int, ...] = (30, 90)
    include_momentum: bool = True
    include_cold_streak: bool = True
    include_coverage: bool = True
    include_jodi_heat: bool = True
    feature_version: str = "psych-v1"


# ---------------------------------------------------------------------------
# ank-level channel (usable inside build_features)
# ---------------------------------------------------------------------------
def _rolling_freq(y: np.ndarray, k: int, window: int) -> np.ndarray:
    """Causal rolling frequency; row ``t`` uses the last ``window`` draws."""
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


def _gap_since_last(y: np.ndarray, k: int) -> np.ndarray:
    """Draws elapsed since each ank was last seen (capped at 999)."""
    n = len(y)
    last_seen = np.full(k, -1)
    out = np.full((n, k), np.nan)
    for t in range(n):
        for c in range(k):
            out[t, c] = _GAP_CAP if last_seen[c] < 0 else float(t - last_seen[c])
        if y[t] >= 0:
            last_seen[y[t]] = t
    return out


def psychology_features(y_shifted: np.ndarray, cfg: PsychologyConfig) -> pd.DataFrame:
    """Build the ank-level psychology channel from a *shifted* history.

    ``y_shifted`` follows the main feature matrix convention: row ``t`` holds
    the outcome of draw ``t-1`` (with ``-1`` as the warm-up sentinel), so row
    ``t`` describes the world a bettor would have seen before draw ``t``.
    """
    y = np.asarray(y_shifted, dtype=int)
    n = len(y)
    cols: dict[str, np.ndarray] = {}

    heat = {}
    for w in cfg.heat_windows:
        heat[w] = _rolling_freq(y, K_ANK, w)
        for c in range(K_ANK):
            cols[f"heat_w{w}_{c}"] = heat[w][:, c] - 1.0 / K_ANK

    if cfg.include_momentum and len(cfg.heat_windows) >= 2:
        small, large = cfg.heat_windows[0], cfg.heat_windows[-1]
        for c in range(K_ANK):
            cols[f"heat_mom_{c}"] = heat[small][:, c] - heat[large][:, c]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            cols["heat_concentration"] = np.nanmax(
                heat[small] - 1.0 / K_ANK, axis=1)

    if cfg.include_cold_streak:
        gaps = _gap_since_last(y, K_ANK)
        expected = np.arange(1, n + 1, dtype=float) / K_ANK  # draws per ank so far
        expected = np.maximum(expected, 1.0)
        gaps_nn = np.nan_to_num(gaps, nan=0.0)
        cols["cold_max_norm"] = np.nanmax(gaps, axis=1) / expected
        cols["overdue_count"] = np.sum(
            np.maximum(gaps_nn - 1.5 * expected[:, None], 0) > 0, axis=1).astype(float)

    if cfg.include_coverage:
        for w in cfg.heat_windows:
            freq = _rolling_freq(y, K_ANK, w)
            cols[f"coverage_w{w}"] = np.sum(freq > 0, axis=1) / K_ANK

    frame = pd.DataFrame(cols)
    return frame.replace([np.inf, -np.inf], np.nan)


# ---------------------------------------------------------------------------
# jodi-level channel (needs both the open and the close series)
# ---------------------------------------------------------------------------
def _jodi_rolling_freq(seq: np.ndarray, window: int) -> np.ndarray:
    """Rolling frequency of each of the 100 jodis; ``-1`` entries are ignored."""
    n = len(seq)
    out = np.full((n, _JODI), np.nan)
    counts = np.zeros(_JODI)
    for t in range(n):
        total = counts.sum()
        if total > 0:
            out[t] = counts / total
        j = seq[t]
        if 0 <= j < _JODI:
            counts[j] += 1
            if t - window >= 0 and 0 <= seq[t - window] < _JODI:
                counts[seq[t - window]] -= 1
    return out


def jodi_psychology_features(open_shifted: np.ndarray, close_shifted: np.ndarray,
                             cfg: PsychologyConfig) -> pd.DataFrame:
    """Jodi-level heat channel. ``open_shifted``/``close_shifted`` are aligned.

    The jodi is formed exactly as the market forms it: open digit followed by
    close digit (open ``5`` + close ``1`` -> jodi ``51``).
    """
    o = np.asarray(open_shifted, dtype=int)
    c = np.asarray(close_shifted, dtype=int)
    valid = (o >= 0) & (c >= 0)
    j = np.where(valid, o * 10 + c, -1)
    n = len(j)
    cols: dict[str, np.ndarray] = {}

    for w in cfg.heat_windows:
        freq = _jodi_rolling_freq(j, w)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            cols[f"jodi_heat_w{w}_top1"] = np.nanmax(freq - 1.0 / _JODI, axis=1)
        freq_nn = np.nan_to_num(freq, nan=0.0)
        cols[f"jodi_heat_w{w}_top1_id"] = np.argmax(freq_nn, axis=1).astype(float)

    # repetition pressure: how often the last window repeats the previous one
    if cfg.include_jodi_heat and len(cfg.heat_windows) >= 1:
        w = cfg.heat_windows[0]
        freq = _jodi_rolling_freq(j, w)
        recent = np.where(freq > 0, 1, 0)
        prior = np.roll(recent, 1, axis=0)
        prior[0] = 0
        both = np.sum(recent * prior, axis=1)
        total = np.sum(recent, axis=1)
        cols["jodi_repeat_rate"] = np.where(total > 0, both / np.maximum(total, 1), np.nan)

    frame = pd.DataFrame(cols)
    return frame.replace([np.inf, -np.inf], np.nan)
