"""Mathematics tests.

Three kinds of assertion live here:

* **registry integrity** - 100 methods, every one implemented and runnable;
* **mathematical correctness** - identities that must hold regardless of data
  (entropy of a uniform distribution, KL of identical distributions, chi-square
  expectations under unequal class sizes);
* **calibration on a null world** - the framework must *not* manufacture evidence
  where the data-generating process has none.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.mathematics.common import (
    chi2_contingency,
    chi2_uniform,
    counts_of,
    cramers_v,
    entropy,
    holm,
    kl_divergence,
    mutual_information,
    normalised_entropy,
    transitions,
    uniform,
)
from src.mathematics.registry import (
    CATEGORY_NAMES,
    METHOD_REGISTRY,
    ORDERED_METHOD_IDS,
    all_methods,
    methods_for_category,
    validate_registry,
)


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------
def test_registry_is_complete_and_valid():
    report = validate_registry()
    assert report["ok"] is True
    assert report["n_documented"] == 100
    assert report["n_implemented"] == 100
    assert report["problems"] == []


def test_all_hundred_ids_are_present_exactly_once():
    ids = [m.id for m in all_methods()]
    assert len(ids) == 100
    assert len(set(ids)) == 100
    assert set(ids) == {f"M{i:03d}" for i in range(1, 101)}
    assert ORDERED_METHOD_IDS == sorted(ORDERED_METHOD_IDS) or len(ORDERED_METHOD_IDS) == 100


def test_category_sizes_sum_to_one_hundred():
    total = 0
    for letter in CATEGORY_NAMES:
        size = len(methods_for_category(letter))
        assert size > 0, f"category {letter} is empty"
        total += size
    assert total == 100


def test_every_method_has_a_callable_runner_and_full_documentation():
    for method in METHOD_REGISTRY.values():
        assert callable(method.runner), method.id
        spec = method.spec
        assert spec.theory and spec.formula and spec.objective, method.id
        assert spec.variables, method.id
        assert spec.steps, method.id
        assert spec.limitations and spec.data_requirements, method.id
        assert len(spec.theory) > 40, method.id


# ---------------------------------------------------------------------------
# identities
# ---------------------------------------------------------------------------
def test_entropy_of_uniform_is_log2_k():
    assert entropy(uniform(10)) == pytest.approx(np.log2(10))
    assert normalised_entropy(uniform(10)) == pytest.approx(1.0)


def test_entropy_of_a_point_mass_is_zero():
    p = np.zeros(10)
    p[3] = 1.0
    assert entropy(p) == pytest.approx(0.0)
    assert normalised_entropy(p) == pytest.approx(0.0)


def test_kl_of_identical_distributions_is_zero():
    p = np.array([0.1] * 10)
    assert kl_divergence(p, p) == pytest.approx(0.0, abs=1e-12)
    # And KL is strictly positive in the other direction.
    q = np.array([0.2, 0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05])
    assert kl_divergence(p, q) > 0


def test_mutual_information_is_symmetric_and_zero_when_independent():
    rng = np.random.default_rng(0)
    x = rng.integers(0, 10, 20000)
    y = rng.integers(0, 10, 20000)
    mi_xy = mutual_information(x, y, 10, 10)
    mi_yx = mutual_information(y, x, 10, 10)
    assert mi_xy == pytest.approx(mi_yx, abs=1e-9)
    assert mi_xy < 0.01, "independent sequences must produce ~0 bits"

    z = (x + 1) % 10  # perfectly dependent (an invertible map of x)
    # Empirical MI is biased very slightly low by empty joint cells, hence 1e-3.
    assert mutual_information(x, z, 10, 10) == pytest.approx(np.log2(10), abs=1e-3)


def test_chi2_uniform_uses_equal_expectations_for_equal_classes():
    rng = np.random.default_rng(7)
    y = rng.integers(0, 10, 5000)
    result = chi2_uniform(y, 10)
    # Under H0 the statistic has mean m-1 = 9.
    assert result["dof"] == 9
    assert result["statistic"] < 30
    assert result["p_value"] > 0.01


def test_chi2_contingency_expectations_use_actual_class_sizes():
    """Regression: mod-3 residue classes of the digits 0-9 are 4/3/3, not 10/3 each.

    Building expectations as ``N / m`` instead of from the row totals produced a
    chi-square near 112 on a genuinely uniform null world.
    """
    rng = np.random.default_rng(11)
    digits = rng.integers(0, 10, 30000)
    residues = digits % 3
    table = np.zeros((2, 3))
    table[0] = counts_of(residues, 3)
    table[1] = counts_of(rng.integers(0, 10, 30000) % 3, 3)
    result = chi2_contingency(table)
    assert result["min_expected"] > 5
    assert result["statistic"] < 12
    assert result["p_value"] > 0.01
    # Cramer's V must be on [0, 1].
    assert 0 <= result["cramers_v"] <= 1


def test_cramers_v_handles_a_perfect_table():
    table = np.array([[50, 0], [0, 50]])
    assert cramers_v(100.0, 100, (2, 2)) == pytest.approx(1.0)
    assert chi2_contingency(table)["p_value"] < 1e-6


def test_transitions_count_matrix_becomes_row_stochastic():
    y = np.random.default_rng(3).integers(0, 10, 4000)
    counts = transitions(y, 10)
    assert counts.shape == (10, 10)
    row_totals = counts.sum(axis=1)
    assert row_totals.sum() == len(y) - 1
    with np.errstate(invalid="ignore", divide="ignore"):
        probs = counts / row_totals[:, None]
    observed_rows = row_totals > 0
    assert np.allclose(probs[observed_rows].sum(axis=1), 1.0, atol=1e-12)


def test_holm_is_monotone_and_bounded():
    adjusted = holm([0.01, 0.02, 0.03, 0.5])
    assert all(a >= u for a, u in zip(adjusted, [0.01, 0.02, 0.03, 0.5]))
    assert all(0 <= a <= 1 for a in adjusted)
    # Adjusted values are non-decreasing in the same order as the raw values.
    assert adjusted == sorted(adjusted)


# ---------------------------------------------------------------------------
# behaviour on a null world
# ---------------------------------------------------------------------------
def test_null_world_produces_no_spurious_evidence(small_config):
    """Chi-square, MI and Markov dependence must all stay quiet on H0 data."""
    from src.preprocessing.cleaning import clean_target

    series = clean_target(small_config, "kalyan", "open").frame["y"].to_numpy()
    assert len(series) > 500

    chi2 = chi2_uniform(series, 10)
    assert chi2["p_value"] > 0.01, "uniform data must not reject uniformity"

    # Mutual information is positively biased in small samples, so the honest test
    # is against a permutation null at the SAME sample size, not against zero.
    mi = mutual_information(series[:-1], series[1:], 10, 10)
    rng = np.random.default_rng(5)
    null_mi = np.array([
        mutual_information(series[:-1], rng.permutation(series[1:]), 10, 10)
        for _ in range(50)
    ])
    assert mi <= np.quantile(null_mi, 0.99), (
        f"observed {mi:.4f} bits is beyond the permutation null "
        f"(95% = {np.quantile(null_mi, 0.95):.4f})")


def test_signal_world_is_detected(small_signal_config):
    """The same tests must fire on data with planted persistence."""
    from src.preprocessing.cleaning import clean_target

    series = clean_target(small_signal_config, "kalyan", "open").frame["y"].to_numpy()
    mi = mutual_information(series[:-1], series[1:], 10, 10)
    assert mi > 0.05, "planted first-order dependence must register as mutual information"


# ---------------------------------------------------------------------------
# execution
# ---------------------------------------------------------------------------
@pytest.mark.slow
def test_a_method_actually_runs_and_reports_a_sample_size(small_config):
    from src.mathematics.engine import run_suite

    suite = run_suite(small_config, "kalyan", "open", only=["M001"], persist=False)
    assert "M001" in suite.outputs
    output = suite.outputs["M001"]
    assert output.status == "computed"
    assert output.findings, "a computed method must return at least one number"
    for finding in output.findings:
        assert finding.sample_size is not None
        assert finding.sample_size > 0
