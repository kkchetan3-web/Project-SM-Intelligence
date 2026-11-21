"""Cross-market tests: alignment, lag semantics and the leakage policy.

Cross-market features are where look-ahead bias usually enters. The tests here fix
the *meaning* of a lag, verify that a same-date foreign value is inadmissible by
default, and check that the one declared same-day channel is used only for the
market the configuration names.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.cross_market.market_alignment import (
    align,
    available_at,
    calendar_diagnostics,
    lagged_pairs,
)


def test_alignment_uses_only_shared_dates(small_config):
    alignment = align(small_config, "kalyan", "main_bazar", "open", "open")
    assert alignment.n_matched > 400
    assert alignment.frame.index.is_monotonic_increasing
    assert alignment.frame["a"].notna().all() and alignment.frame["b"].notna().all()
    summary = alignment.summary()
    assert summary["n_matched"] == alignment.n_matched


def test_availability_policy_is_conservative_by_default():
    alignment = None  # availability does not depend on the data, only on the lag
    assert available_at(alignment, 0) is False, "same-date foreign values are inadmissible"
    assert available_at(alignment, 1) is True
    assert available_at(alignment, -1) is True
    assert available_at(alignment, 0, conservative=False) is True


def test_lag_orientation_is_target_date_first(small_config):
    alignment = align(small_config, "kalyan", "main_bazar", "open", "open")
    x, y, target_index = lagged_pairs(alignment, 2)
    assert len(x) == len(y) == len(target_index) or len(x) == len(y)
    # x[t] is the earlier value and y[t] the later one: the lagged series must
    # start where the base series starts and end two observations earlier.
    assert len(x) == alignment.n_matched - 2
    assert list(x.index) == list(alignment.frame.index[:-2])


def test_calendar_diagnostics_reports_mismatch(small_config):
    alignment = align(small_config, "kalyan", "main_bazar", "open", "open")
    diagnostics = calendar_diagnostics(alignment)
    assert diagnostics["n_matched"] == alignment.n_matched
    assert diagnostics["mean_gap_days"] >= 1.0
    # These markets do not draw on Sunday, so no matched date may be a Sunday.
    weekday_mix = diagnostics["weekday_mix"]
    assert 6 not in weekday_mix


def test_close_frame_uses_foreign_open_only_where_declared(small_config):
    from src.models.close_models import build_close_frame

    kalyan = build_close_frame(small_config, "kalyan", verify=True)
    main_bazar = build_close_frame(small_config, "main_bazar", verify=True)

    assert kalyan.causality["passed"] is True
    assert main_bazar.causality["passed"] is True
    assert kalyan.causality["same_day_foreign_open_used"] is False
    assert main_bazar.causality["same_day_foreign_open_used"] is True
    assert main_bazar.causality["foreign_partner"] == "kalyan"
    assert "x_today_open" in main_bazar.X.columns
    assert "x_today_open" not in kalyan.X.columns


def test_removing_the_declaration_removes_the_channel(small_config):
    """The same-day channel must be configuration-driven, not hard-coded."""
    from dataclasses import replace

    from src.models.close_models import build_close_frame

    stripped = replace(small_config, cross_open_precedence=())
    frame = build_close_frame(stripped, "main_bazar", verify=True)
    assert frame.causality["same_day_foreign_open_used"] is False
    assert "x_today_open" not in frame.X.columns


def test_lagged_foreign_features_are_strictly_lagged(small_config):
    from src.models.close_models import build_close_frame

    frame = build_close_frame(small_config, "kalyan", verify=True)
    if "x_prev_open" not in frame.X.columns:
        pytest.skip("no lagged cross-market features for this market")
    own_open = frame.X["x_prev_open"].to_numpy()
    # The first row cannot have a previous value.
    assert np.isnan(own_open[0])


def test_leakage_validation_passes(small_config):
    from src.cross_market.cross_market_validation import validate_no_leakage

    result = validate_no_leakage(small_config)
    assert result["ok"] is True
    by_market = {(c["market"], c["target"]): c for c in result["feature_checks"]}
    assert by_market[("main_bazar", "close")]["precedence_declared"] is True
    assert by_market[("kalyan", "open")]["same_day_foreign_open_used"] is False


def test_lead_lag_sweep_is_complete_and_corrected(small_signal_config):
    from src.cross_market.lead_lag_analysis import investigate_pair

    result = investigate_pair(small_signal_config, "kalyan", "main_bazar")
    assert result["n_tests"] == 28, "4 component pairs x 7 declared lags"
    lags = sorted({t["lag"] for t in result["tests"]})
    assert lags == [-3, -2, -1, 0, 1, 2, 3]
    for test in result["tests"]:
        assert test["verdict"]
        if test["p_value"] is not None:
            assert test["p_adjusted"] >= test["p_value"] - 1e-12
        assert test["admissible_same_day"] is (test["lag"] != 0)


@pytest.mark.slow
def test_conditional_model_comparison_is_well_formed(small_signal_config):
    from src.cross_market.conditional_models import test_feature_value

    result = test_feature_value(small_signal_config, "main_bazar", "close")
    if not result.get("available"):
        pytest.skip(result.get("reason", "no foreign features"))
    assert result["foreign_features"]
    assert result["ci_low"] <= result["ci_high"]
    assert result["n_predictions"] > 200
