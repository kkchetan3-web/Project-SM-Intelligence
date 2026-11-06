"""Validation: splits, significance, stability, and the final verdict logic.

The point of this module is to make it hard to fool yourself. A model is only
promoted if it:

1. beats the strongest baseline on **out-of-sample log loss**, by a margin that
   survives a moving-block bootstrap (dependence-aware) confidence interval;
2. is **calibrated** (slope near 1, ECE small);
3. is **stable** - the improvement appears in a majority of chronological folds,
   not one lucky stretch;
4. is **reproducible** - re-running with the same seed and window gives the same
   numbers.

Anything else is recorded as a negative result. Negative results are a
first-class deliverable here, not a failure to be hidden.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from src.backtesting.metrics import (
    calibration_slope,
    geometric_skill_score,
    paired_bootstrap_difference,
)
from src.backtesting.walk_forward import WalkForwardResult
from src.core.logging import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# splits
# ---------------------------------------------------------------------------
def chronological_holdout(n: int, fraction: float = 0.2) -> tuple[np.ndarray, np.ndarray]:
    """Split indices into (development, untouched holdout), time-ordered."""
    if not 0 < fraction < 1:
        raise ValueError("holdout fraction must be in (0, 1)")
    cut = int(round(n * (1 - fraction)))
    cut = max(1, min(cut, n - 1))
    return np.arange(0, cut), np.arange(cut, n)


def expanding_folds(n: int, n_folds: int = 5, min_train: int = 100) -> list[tuple[np.ndarray, np.ndarray]]:
    """Contiguous time-ordered folds; each fold's training set precedes its test set."""
    if n_folds < 2:
        raise ValueError("need at least 2 folds")
    remaining = n - min_train
    if remaining < n_folds:
        raise ValueError("not enough observations for the requested folds")
    size = remaining // n_folds
    folds = []
    for f in range(n_folds):
        test_start = min_train + f * size
        test_end = n if f == n_folds - 1 else test_start + size
        folds.append((np.arange(0, test_start), np.arange(test_start, test_end)))
    return folds


# ---------------------------------------------------------------------------
# comparison
# ---------------------------------------------------------------------------
@dataclass
class Comparison:
    model: str
    baseline: str
    model_log_loss: float
    baseline_log_loss: float
    mean_diff: float
    ci_low: float
    ci_high: float
    p_value: float
    n: int
    significant: bool
    skill: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "model": self.model, "baseline": self.baseline,
            "model_log_loss": round(self.model_log_loss, 6),
            "baseline_log_loss": round(self.baseline_log_loss, 6),
            "mean_diff": round(self.mean_diff, 6),
            "ci_low": round(self.ci_low, 6), "ci_high": round(self.ci_high, 6),
            "p_value": round(self.p_value, 6), "n": self.n,
            "significant": self.significant,
            "skill_score": round(self.skill, 6),
        }


def compare_to_baseline(model: WalkForwardResult, baseline: WalkForwardResult,
                        *, block: int = 5, n_resamples: int = 1000) -> Comparison:
    """Paired, dependence-aware comparison on per-observation log loss.

    Lower log loss is better, so a *negative* mean_diff means the model wins.
    """
    if len(model.y_true) != len(baseline.y_true) or not np.array_equal(model.y_true, baseline.y_true):
        raise ValueError("paired comparison requires identical evaluation windows")
    m = model.per_obs_log_loss()
    b = baseline.per_obs_log_loss()
    boot = paired_bootstrap_difference(m, b, block=block, n_resamples=n_resamples)
    return Comparison(
        model=model.model_name, baseline=baseline.model_name,
        model_log_loss=float(m.mean()), baseline_log_loss=float(b.mean()),
        mean_diff=boot["mean_diff"], ci_low=boot["ci_low"], ci_high=boot["ci_high"],
        p_value=boot["p_two_sided"], n=boot["n"],
        significant=bool(boot["ci_high"] < 0),   # model strictly better
        skill=geometric_skill_score(float(m.mean()), float(b.mean())),
    )


def best_baseline(results: Mapping[str, WalkForwardResult]) -> str:
    return min(results, key=lambda name: results[name].per_obs_log_loss().mean())


# ---------------------------------------------------------------------------
# stability
# ---------------------------------------------------------------------------
def fold_stability(model: WalkForwardResult, baseline: WalkForwardResult,
                   *, n_folds: int = 5) -> dict[str, Any]:
    """Fraction of chronological folds in which the model beats the baseline."""
    n = len(model.y_true)
    edges = np.linspace(0, n, n_folds + 1).astype(int)
    per_fold = []
    for i in range(n_folds):
        lo, hi = edges[i], edges[i + 1]
        if hi - lo < 10:
            continue
        m = model.per_obs_log_loss()[lo:hi].mean()
        b = baseline.per_obs_log_loss()[lo:hi].mean()
        per_fold.append({
            "fold": i, "n": int(hi - lo),
            "model_log_loss": round(float(m), 6),
            "baseline_log_loss": round(float(b), 6),
            "model_better": bool(m < b),
        })
    wins = sum(1 for f in per_fold if f["model_better"])
    return {
        "n_folds": len(per_fold), "wins": wins,
        "fraction_wins": round(wins / max(len(per_fold), 1), 4),
        "stable": wins > len(per_fold) / 2,
        "per_fold": per_fold,
    }


def calibration_report(result: WalkForwardResult) -> dict[str, Any]:
    from src.backtesting.metrics import calibration_table, expected_calibration_error

    slope = calibration_slope(result.probs, result.y_true)
    return {
        "slope": None if slope is None else round(slope["slope"], 4),
        "intercept": None if slope is None else round(slope["intercept"], 4),
        "ece": round(expected_calibration_error(result.probs, result.y_true), 4),
        "table": calibration_table(result.probs, result.y_true),
        "interpretation": (
            "well calibrated" if slope and 0.8 <= slope["slope"] <= 1.25
            else "miscalibrated (over-confident)" if slope and slope["slope"] < 0.8
            else "miscalibrated (under-confident)" if slope else "undetermined"
        ),
    }


# ---------------------------------------------------------------------------
# the verdict
# ---------------------------------------------------------------------------
@dataclass
class Verdict:
    model: str
    market: str
    target: str
    promoted: bool
    reasons: list[str]
    evidence: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "model": self.model, "market": self.market, "target": self.target,
            "promoted": self.promoted, "reasons": self.reasons, "evidence": self.evidence,
        }


def decide(model: WalkForwardResult, baselines: Mapping[str, WalkForwardResult],
           *, min_improvement: float = 0.002, require_stability: bool = True,
           block: int = 5) -> Verdict:
    """Apply the promotion rule; default to rejecting."""
    name = best_baseline(baselines)
    base = baselines[name]
    comparison = compare_to_baseline(model, base, block=block)
    stability = fold_stability(model, base)
    calibration = calibration_report(model)

    reasons: list[str] = []
    improvement = base.per_obs_log_loss().mean() - model.per_obs_log_loss().mean()
    if improvement <= 0:
        reasons.append(
            f"does not beat the best baseline ({name}) on out-of-sample log loss "
            f"({model.per_obs_log_loss().mean():.5f} vs {base.per_obs_log_loss().mean():.5f})"
        )
    elif improvement < min_improvement:
        reasons.append(
            f"improvement {improvement:.5f} is below the {min_improvement} practical-significance floor"
        )
    if not comparison.significant:
        reasons.append(
            f"paired block-bootstrap 95% CI [{comparison.ci_low:.5f}, {comparison.ci_high:.5f}] "
            "includes zero"
        )
    if require_stability and not stability["stable"]:
        reasons.append(
            f"improvement does not hold across folds ({stability['wins']}/{stability['n_folds']})"
        )
    slope = calibration["slope"]
    if slope is not None and not (0.8 <= slope <= 1.25):
        reasons.append(f"calibration slope {slope:.3f} is outside [0.80, 1.25]")

    promoted = not reasons
    if promoted:
        reasons.append(
            f"beats {name} by {improvement:.5f} log loss with a bootstrap CI excluding zero "
            f"and stable across {stability['wins']}/{stability['n_folds']} folds"
        )

    return Verdict(
        model=model.model_name, market=model.market_id, target=model.target,
        promoted=promoted, reasons=reasons,
        evidence={
            "comparison": comparison.as_dict(),
            "stability": stability,
            "calibration": {k: v for k, v in calibration.items() if k != "table"},
            "model_metrics": model.metrics().as_dict(),
            "best_baseline": name,
        },
    )


def summarise_results(results: Mapping[str, WalkForwardResult],
                      baseline_names: Sequence[str]) -> pd.DataFrame:
    """One tidy row per model, ready for a report table."""
    rows = []
    for name, res in results.items():
        m = res.metrics()
        rows.append({
            "model": name, "kind": "baseline" if name in baseline_names else "candidate",
            **{k: round(v, 5) if isinstance(v, float) else v for k, v in m.as_dict().items()},
        })
    return pd.DataFrame(rows).sort_values("log_loss").reset_index(drop=True)


def fdr_correct(p_values: Sequence[float], method: str = "benjamini_hochberg",
                alpha: float = 0.05) -> dict[str, Any]:
    """Multiple-testing correction - essential when 100 methods all test something."""
    p = np.asarray([1.0 if v is None or (isinstance(v, float) and np.isnan(v)) else float(v)
                    for v in p_values], dtype=float)
    n = len(p)
    if n == 0:
        return {"adjusted": [], "rejected": [], "n": 0, "method": method}
    order = np.argsort(p)
    ranked = p[order]
    if method == "benjamini_hochberg":
        adjusted_sorted = ranked * n / np.arange(1, n + 1)
        adjusted_sorted = np.minimum.accumulate(adjusted_sorted[::-1])[::-1]
    elif method == "holm":
        adjusted_sorted = np.maximum.accumulate((n - np.arange(n)) * ranked)
    elif method == "bonferroni":
        adjusted_sorted = np.minimum(ranked * n, 1.0)
    else:
        raise ValueError(f"unknown correction method: {method}")
    adjusted_sorted = np.clip(adjusted_sorted, 0.0, 1.0)
    adjusted = np.empty(n)
    adjusted[order] = adjusted_sorted
    return {
        "adjusted": adjusted.tolist(),
        "rejected": (adjusted <= alpha).tolist(),
        "n": n, "method": method, "alpha": alpha,
        "n_rejected": int((adjusted <= alpha).sum()),
    }


def reproducibility_check(run_a: WalkForwardResult, run_b: WalkForwardResult) -> dict[str, Any]:
    """Two runs with identical settings must produce identical probabilities."""
    same = (
        np.allclose(run_a.probs, run_b.probs, atol=1e-12)
        and np.array_equal(run_a.y_true, run_b.y_true)
    )
    return {
        "identical": bool(same),
        "max_abs_diff": float(np.max(np.abs(run_a.probs - run_b.probs)))
        if run_a.probs.shape == run_b.probs.shape else float("nan"),
        "checked": "probabilities and outcomes",
    }
