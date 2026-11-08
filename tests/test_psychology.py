"""Tests for the player-psychology channel and its opt-in wiring.

The channel describes what players *bet on* (heat, cold streaks, coverage),
not what will happen. The tests therefore pin the two things that matter:
the features are causal, and they only appear when a run opts in.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.preprocessing.feature_engineering import FeatureConfig, build_features
from src.preprocessing.psychology import (PsychologyConfig, jodi_psychology_features,
                                          psychology_features)


def _shifted(y: list[int]) -> np.ndarray:
    """The convention build_features uses: row t holds draw t-1, -1 for warm-up."""
    return np.concatenate([[-1], np.asarray(y, dtype=int)[:-1]])


# ---------------------------------------------------------------------------
# causality
# ---------------------------------------------------------------------------
def test_psychology_channel_is_causal():
    rng = np.random.default_rng(11)
    y = rng.integers(0, 10, size=400)
    cfg = PsychologyConfig()
    full = psychology_features(_shifted(y.tolist()), cfg)
    cut = 250
    partial = psychology_features(_shifted(y[:cut].tolist()), cfg)
    common = [c for c in full.columns if c in partial.columns]
    # Rows computed from truncated history must equal the full-history prefix.
    a = full.loc[: cut - 1, common].to_numpy(dtype=float)
    b = partial.loc[: cut - 1, common].to_numpy(dtype=float)
    assert np.allclose(a, b, equal_nan=True, atol=1e-12)


def test_psychology_channel_off_by_default():
    rng = np.random.default_rng(3)
    y = rng.integers(0, 10, size=300)
    shifted = _shifted(y.tolist())
    X_off = build_features(np.asarray(y), FeatureConfig())
    X_on = build_features(np.asarray(y),
                          FeatureConfig(include_psychology=True,
                                        psychology=PsychologyConfig()))
    psych_cols = [c for c in X_on.columns if c not in X_off.columns]
    assert len(psych_cols) > 20
    assert not [c for c in X_off.columns if c.startswith("heat_")]
    assert X_on.shape[1] > X_off.shape[1]


# ---------------------------------------------------------------------------
# semantics
# ---------------------------------------------------------------------------
def test_heat_features_track_recent_frequency():
    # Draws 0-9 once each, then a long run of 7s. Row 10 (before the 7-run)
    # should show 7 with heat near zero; row 20 should show it hot.
    y = list(range(10)) + [7] * 10
    feats = psychology_features(_shifted(y), PsychologyConfig())
    # heat_w30_7 is the 7-column excess over 0.1 at the last row.
    last = feats["heat_w30_7"].iloc[-1]
    assert last > 0.2  # ten 7s in a 30-window of 20 draws: freq 0.5
    early = feats["heat_w30_7"].iloc[10]
    assert abs(early) < 0.05


def test_overdue_count_rises_when_an_ank_is_absent():
    y = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] * 5  # every ank appears regularly
    feats = psychology_features(_shifted(y), PsychologyConfig())
    regular = float(feats["overdue_count"].iloc[-1])
    y2 = y + [0] * 40  # ank 9 absent for 40 draws
    feats2 = psychology_features(_shifted(y2), PsychologyConfig())
    assert float(feats2["overdue_count"].iloc[-1]) > regular


def test_coverage_is_fraction_of_anks_seen():
    y = [1, 1, 1, 1, 1] * 20  # only ank 1 ever appears
    feats = psychology_features(_shifted(y), PsychologyConfig())
    assert float(feats["coverage_w30"].iloc[-1]) == pytest.approx(0.1)


# ---------------------------------------------------------------------------
# jodi formation
# ---------------------------------------------------------------------------
def test_jodi_formation_open_then_close():
    # open 5, close 1 -> jodi 51 (the market's own formation rule).
    opens = [5, 5, 5, 5, 5, 5]
    closes = [1, 1, 1, 1, 1, 1]
    feats = jodi_psychology_features(_shifted(opens), _shifted(closes),
                                     PsychologyConfig())
    assert "jodi_heat_w30_top1_id" in feats.columns
    assert int(feats["jodi_heat_w30_top1_id"].iloc[-1]) == 51


def test_jodi_repetition_rate_is_one_when_the_jodi_repeats():
    opens = [3] * 20
    closes = [7] * 20
    feats = jodi_psychology_features(_shifted(opens), _shifted(closes),
                                     PsychologyConfig())
    assert float(feats["jodi_repeat_rate"].iloc[-1]) == pytest.approx(1.0)
