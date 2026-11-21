"""Scoring rules and their uncertainty.

Exact-match accuracy is a terrible metric for a 10- or 100-way categorical
forecast: 90% of the information in a probability forecast is thrown away, and
accuracy moves in steps of 1/n. The primary metric here is therefore **log
loss** (strictly proper, punishes overconfidence), with the multiclass Brier
score and the ranked probability score as companions, and accuracy/top-k
reported only because they are interpretable.

All metrics take ``probs`` of shape (n, K) and integer ``y`` of shape (n,).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

EPS = 1e-12


def _prepare(probs: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    p = np.asarray(probs, dtype=float)
    t = np.asarray(y, dtype=int)
    if p.ndim != 2:
        raise ValueError(f"probs must be 2-D (n, K), got shape {p.shape}")
    if len(p) != len(t):
        raise ValueError(f"length mismatch: {len(p)} probs vs {len(t)} outcomes")
    if len(p) == 0:
        raise ValueError("cannot score an empty prediction set")
    k = p.shape[1]
    if np.any(t < 0) or np.any(t >= k):
        raise ValueError(f"outcome outside [0, {k})")
    return p, t, k


def row_normalise(p: np.ndarray) -> np.ndarray:
    p = np.clip(np.asarray(p, dtype=float), 0.0, None)
    sums = p.sum(axis=1, keepdims=True)
    sums[sums <= 0] = 1.0
    return p / sums


def log_loss(probs: np.ndarray, y: np.ndarray) -> float:
    """Mean negative log-likelihood of the realised outcome."""
    p, t, _ = _prepare(probs, y)
    p = row_normalise(p)
    picked = p[np.arange(len(t)), t]
    return float(-np.mean(np.log(np.clip(picked, EPS, None))))


def per_observation_log_loss(probs: np.ndarray, y: np.ndarray) -> np.ndarray:
    p, t, _ = _prepare(probs, y)
    p = row_normalise(p)
    return -np.log(np.clip(p[np.arange(len(t)), t], EPS, None))


def brier(probs: np.ndarray, y: np.ndarray) -> float:
    """Multiclass Brier score: mean squared error of the full probability vector."""
    p, t, k = _prepare(probs, y)
    p = row_normalise(p)
    onehot = np.zeros_like(p)
    onehot[np.arange(len(t)), t] = 1.0
    return float(np.mean(np.sum((p - onehot) ** 2, axis=1)))


def accuracy(probs: np.ndarray, y: np.ndarray) -> float:
    p, t, _ = _prepare(probs, y)
    return float(np.mean(np.argmax(p, axis=1) == t))


def top_k_accuracy(probs: np.ndarray, y: np.ndarray, k: int) -> float:
    p, t, _ = _prepare(probs, y)
    if k >= p.shape[1]:
        return 1.0
    order = np.argsort(-p, axis=1)[:, :k]
    return float(np.mean(np.any(order == t[:, None], axis=1)))


def ranked_probability_score(probs: np.ndarray, y: np.ndarray) -> float:
    """RPS for ordinal outcomes - meaningful only when the classes are ordered."""
    p, t, k = _prepare(probs, y)
    p = row_normalise(p)
    cum_p = np.cumsum(p, axis=1)[:, : k - 1]
    cum_o = np.zeros_like(cum_p)
    for i, cls in enumerate(t):
        if cls > 0:
            cum_o[i, : min(cls, k - 1)] = 1.0
    return float(np.mean(np.sum((cum_p - cum_o) ** 2, axis=1) / (k - 1)))


def expected_calibration_error(probs: np.ndarray, y: np.ndarray, n_bins: int = 10) -> float:
    """ECE over the top-1 prediction, plus maximum calibration error."""
    p, t, _ = _prepare(probs, y)
    p = row_normalise(p)
    confidence = p.max(axis=1)
    correct = (np.argmax(p, axis=1) == t).astype(float)
    return float(_ece(confidence, correct, n_bins)[0])


def calibration_table(probs: np.ndarray, y: np.ndarray, n_bins: int = 10) -> list[dict[str, Any]]:
    """Bin-wise reliability data (used by the calibration plots/report)."""
    p, t, _ = _prepare(probs, y)
    p = row_normalise(p)
    confidence = p.max(axis=1)
    correct = (np.argmax(p, axis=1) == t).astype(float)
    return _ece(confidence, correct, n_bins)[1]


def _ece(confidence: np.ndarray, correct: np.ndarray, n_bins: int) -> tuple[float, list[dict]]:
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(confidence, bins[1:-1], right=True), 0, n_bins - 1)
    total = len(confidence)
    ece = 0.0
    table: list[dict] = []
    for b in range(n_bins):
        mask = idx == b
        if not mask.any():
            continue
        conf_b = float(confidence[mask].mean())
        acc_b = float(correct[mask].mean())
        weight = float(mask.sum()) / total
        ece += weight * abs(conf_b - acc_b)
        table.append({
            "bin": b, "bin_lower": float(bins[b]), "bin_upper": float(bins[b + 1]),
            "n": int(mask.sum()), "mean_confidence": round(conf_b, 4),
            "empirical_accuracy": round(acc_b, 4), "gap": round(acc_b - conf_b, 4),
        })
    return ece, table


def calibration_slope(probs: np.ndarray, y: np.ndarray) -> dict[str, float] | None:
    """Fit ``y = sigmoid(a + b * logit(p_top))`` as a one-number calibration check.

    A well-calibrated forecast has ``b ~= 1`` and ``a ~= 0``. ``b < 1`` means the
    model is over-confident; ``b > 1`` means under-confident. Fitted by simple
    Newton iterations so no extra dependency is required.
    """
    p, t, _ = _prepare(probs, y)
    p = row_normalise(p)
    p_top = np.clip(p.max(axis=1), 1e-6, 1 - 1e-6)
    correct = (np.argmax(p, axis=1) == t).astype(float)
    if correct.min() == correct.max():
        return None
    x = np.log(p_top / (1 - p_top))
    design = np.column_stack([np.ones_like(x), x])
    beta = np.zeros(2)
    for _ in range(50):
        eta = design @ beta
        mu = 1.0 / (1.0 + np.exp(-eta))
        w = np.clip(mu * (1 - mu), 1e-9, None)
        grad = design.T @ (correct - mu)
        hess = design.T @ (design * w[:, None])
        try:
            step = np.linalg.solve(hess + 1e-9 * np.eye(2), grad)
        except np.linalg.LinAlgError:  # pragma: no cover
            break
        beta = beta + step
        if np.max(np.abs(step)) < 1e-8:
            break
    return {"intercept": float(beta[0]), "slope": float(beta[1])}


def rank_of_actual(probs: np.ndarray, y: np.ndarray) -> np.ndarray:
    """1-based rank of the realised outcome in each forecast (1 = top pick)."""
    p, t, _ = _prepare(probs, y)
    order = np.argsort(-p, axis=1)
    ranks = np.empty(len(t), dtype=int)
    for i in range(len(t)):
        ranks[i] = int(np.where(order[i] == t[i])[0][0]) + 1
    return ranks


# ---------------------------------------------------------------------------
# uncertainty
# ---------------------------------------------------------------------------
def moving_block_bootstrap_indices(n: int, block: int, n_resamples: int,
                                   rng: np.random.Generator) -> np.ndarray:
    """Index matrix of moving-block bootstrap resamples (preserves local dependence)."""
    block = max(1, min(block, n))
    n_blocks = int(np.ceil(n / block))
    starts = rng.integers(0, n - block + 1, size=(n_resamples, n_blocks))
    offsets = np.arange(block)
    idx = (starts[:, :, None] + offsets[None, None, :]).reshape(n_resamples, -1)[:, :n]
    return idx


def bootstrap_ci(sample: np.ndarray, confidence: float = 0.95, block: int = 5,
                 n_resamples: int = 1000, seed: int = 0) -> dict[str, float]:
    """Moving-block bootstrap confidence interval for the mean of ``sample``."""
    sample = np.asarray(sample, dtype=float)
    n = len(sample)
    if n < 5:
        return {"mean": float(np.mean(sample)) if n else float("nan"),
                "ci_low": float("nan"), "ci_high": float("nan"),
                "se": float("nan"), "n": n}
    rng = np.random.default_rng(seed)
    idx = moving_block_bootstrap_indices(n, block, n_resamples, rng)
    means = sample[idx].mean(axis=1)
    alpha = (1 - confidence) / 2
    return {
        "mean": float(np.mean(sample)),
        "ci_low": float(np.quantile(means, alpha)),
        "ci_high": float(np.quantile(means, 1 - alpha)),
        "se": float(np.std(means, ddof=1)),
        "n": n,
        "n_resamples": n_resamples,
    }


def paired_bootstrap_difference(a: np.ndarray, b: np.ndarray, confidence: float = 0.95,
                                block: int = 5, n_resamples: int = 1000,
                                seed: int = 0) -> dict[str, float]:
    """Bootstrap CI for ``mean(a) - mean(b)`` on paired per-observation scores.

    Used to ask the only question that matters: is the difference between a model
    and its baseline distinguishable from zero given dependence in the sequence?
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("paired comparison requires equal-length arrays")
    diff = a - b
    n = len(diff)
    rng = np.random.default_rng(seed)
    idx = moving_block_bootstrap_indices(n, block, n_resamples, rng)
    means = diff[idx].mean(axis=1)
    alpha = (1 - confidence) / 2
    return {
        "mean_diff": float(diff.mean()),
        "ci_low": float(np.quantile(means, alpha)),
        "ci_high": float(np.quantile(means, 1 - alpha)),
        "se": float(np.std(means, ddof=1)),
        "p_two_sided": float(2 * min(np.mean(means <= 0), np.mean(means >= 0))),
        "n": n,
        "significant": bool(np.quantile(means, alpha) > 0 or np.quantile(means, 1 - alpha) < 0),
    }


@dataclass
class MetricBundle:
    log_loss: float
    brier: float
    accuracy: float
    top3: float
    top5: float
    rps: float
    ece: float
    n: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "log_loss": round(self.log_loss, 6), "brier": round(self.brier, 6),
            "accuracy": round(self.accuracy, 6), "top3": round(self.top3, 6),
            "top5": round(self.top5, 6), "rps": round(self.rps, 6),
            "ece": round(self.ece, 6), "n": self.n,
        }


def evaluate(probs: np.ndarray, y: np.ndarray, *, ordinal: bool = False) -> MetricBundle:
    """All headline metrics in one call."""
    return MetricBundle(
        log_loss=log_loss(probs, y),
        brier=brier(probs, y),
        accuracy=accuracy(probs, y),
        top3=top_k_accuracy(probs, y, 3),
        top5=top_k_accuracy(probs, y, 5),
        rps=ranked_probability_score(probs, y) if ordinal else float("nan"),
        ece=expected_calibration_error(probs, y),
        n=len(y),
    )


def uniform_reference(k: int) -> dict[str, float]:
    """What a naive uniform forecast scores - the floor any model must clear."""
    return {"log_loss": float(np.log(k)), "brier": float((k - 1) / k), "accuracy": 1.0 / k}


def geometric_skill_score(model_ll: float, baseline_ll: float) -> float:
    """1 - model/baseline on log loss; <= 0 means no skill at all."""
    if baseline_ll <= 0:
        return float("nan")
    return float(1.0 - model_ll / baseline_ll)
