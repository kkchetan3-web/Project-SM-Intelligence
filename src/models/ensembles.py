"""Ensembles: averaging, weighting, stacking and diversity.

The rule from Section 14 that this module enforces: **weights are fitted on
validation predictions, never on the test set**. Every function here takes
already-generated out-of-sample predictions and returns a combination rule; none
of them can reach back into the data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np

from src.backtesting.metrics import log_loss


def _stack(prob_dict: Mapping[str, np.ndarray]) -> tuple[list[str], np.ndarray]:
    names = list(prob_dict)
    if not names:
        raise ValueError("no probability matrices supplied")
    mats = [np.asarray(prob_dict[n], dtype=float) for n in names]
    shapes = {m.shape for m in mats}
    if len(shapes) != 1:
        raise ValueError(f"mismatched shapes in ensemble: {shapes}")
    return names, np.stack(mats, axis=0)  # (M, n, K)


def combine(prob_dict: Mapping[str, np.ndarray], weights: Sequence[float] | None = None) -> np.ndarray:
    """Weighted arithmetic mean of probability vectors, renormalised."""
    names, stack = _stack(prob_dict)
    if weights is None:
        w = np.full(len(names), 1.0 / len(names))
    else:
        w = np.asarray(weights, dtype=float)
        if len(w) != len(names):
            raise ValueError(f"{len(w)} weights for {len(names)} models")
        w = np.clip(w, 0, None)
        if w.sum() <= 0:
            w = np.full(len(names), 1.0 / len(names))
        else:
            w = w / w.sum()
    out = np.tensordot(w, stack, axes=(0, 0))
    return out / out.sum(axis=1, keepdims=True)


def geometric_combine(prob_dict: Mapping[str, np.ndarray],
                      weights: Sequence[float] | None = None) -> np.ndarray:
    """Weighted geometric mean - sharpens agreement, tolerates one confident dissenter."""
    names, stack = _stack(prob_dict)
    w = (np.full(len(names), 1.0 / len(names)) if weights is None
         else np.asarray(weights, dtype=float) / max(np.sum(weights), 1e-12))
    logs = np.tensordot(w, np.log(np.clip(stack, 1e-12, None)), axes=(0, 0))
    out = np.exp(logs - logs.max(axis=1, keepdims=True))
    return out / out.sum(axis=1, keepdims=True)


def performance_weights(prob_dict: Mapping[str, np.ndarray], y: np.ndarray,
                        *, temperature: float = 1.0) -> dict[str, float]:
    """Weights from validation log loss: ``w_m ∝ exp(-(LL_m - LL_min) / T)``."""
    names, _ = _stack(prob_dict)
    losses = np.array([log_loss(prob_dict[n], y) for n in names])
    scaled = (losses - losses.min()) / max(temperature, 1e-9)
    raw = np.exp(-scaled)
    raw = np.clip(raw, 1e-12, None)
    return {n: float(w) for n, w in zip(names, raw / raw.sum(), strict=True)}


def bayesian_model_averaging(prob_dict: Mapping[str, np.ndarray], y: np.ndarray,
                             *, n_parameters: Mapping[str, int] | None = None) -> dict[str, float]:
    """BMA weights from a BIC-style approximation to the model evidence.

    ``log P(M|D) ∝ n * LL_m + log(n) * k_m`` with LL the mean log likelihood, so
    the penalty grows with parameter count. It is an approximation, and it is
    labelled as one wherever it is reported.
    """
    names, _ = _stack(prob_dict)
    n = len(y)
    log_evidence = []
    for name in names:
        ll = -log_loss(prob_dict[name], y) * n
        k = (n_parameters or {}).get(name, 10)
        log_evidence.append(ll - 0.5 * np.log(max(n, 2)) * k)
    log_evidence = np.array(log_evidence, dtype=float)
    log_evidence -= log_evidence.max()
    weights = np.exp(log_evidence)
    weights = weights / weights.sum()
    return {n_: float(w) for n_, w in zip(names, weights, strict=True)}


def diversity_matrix(prob_dict: Mapping[str, np.ndarray]) -> dict[str, Any]:
    """Correlation of model *errors* and of their top-1 choices.

    Two models with the same accuracy but uncorrelated errors ensemble better
    than two near-identical ones - which is the whole point of Method 98.
    """
    names, stack = _stack(prob_dict)
    if len(names) < 2:
        return {"names": names, "correlation": [], "mean_correlation": 1.0}
    flat = stack.reshape(len(names), -1)
    corr = np.corrcoef(flat)
    upper = corr[np.triu_indices(len(names), k=1)] if len(names) > 1 else np.array([1.0])
    picks = [stack[i].argmax(axis=1) for i in range(len(names))]
    agreement = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            agreement[f"{names[i]}~{names[j]}"] = float(np.mean(picks[i] == picks[j]))
    return {
        "names": names,
        "correlation": np.round(corr, 4).tolist(),
        "mean_correlation": float(np.mean(upper)),
        "top1_agreement": agreement,
        "mean_agreement": float(np.mean(list(agreement.values()))) if agreement else 1.0,
    }


@dataclass
class StackResult:
    weights: dict[str, float]
    combined: np.ndarray
    meta_log_loss: float
    base_log_losses: dict[str, float]
    improved: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "weights": {k: round(v, 4) for k, v in self.weights.items()},
            "meta_log_loss": round(self.meta_log_loss, 6),
            "base_log_losses": {k: round(v, 6) for k, v in self.base_log_losses.items()},
            "improved_over_best_base": self.improved,
        }


def regularised_stack(train: Mapping[str, np.ndarray], y_train: np.ndarray,
                      test: Mapping[str, np.ndarray], y_test: np.ndarray) -> StackResult:
    """Fit convex combination weights on a *training* split, score on a *test* split.

    Constrained non-negative least squares on the probability simplex is a
    regularised (non-negative, sum-to-one) meta-learner: it cannot extrapolate,
    it cannot assign negative weights, and it has M-1 free parameters rather than
    a full K x M matrix, which is what keeps it stable on short samples.
    """
    names = [n for n in train if n in test]
    if not names:
        raise ValueError("no common models between train and test")

    y_train = np.asarray(y_train, dtype=int)
    y_test = np.asarray(y_test, dtype=int)
    for name in names:
        if train[name].shape[0] != len(y_train):
            raise ValueError(
                f"stacking split mismatch for {name}: train predictions "
                f"{train[name].shape[0]} vs train outcomes {len(y_train)}")
        if test[name].shape[0] != len(y_test):
            raise ValueError(
                f"stacking split mismatch for {name}: test predictions "
                f"{test[name].shape[0]} vs test outcomes {len(y_test)}")

    train_stack = np.stack([train[n] for n in names], axis=0)  # (M, n_train, K)
    # Target matrix must match the TRAIN slice; the previous version shaped it
    # from the test slice, which silently broke whenever the split was uneven.
    onehot = np.zeros_like(train_stack[0])
    onehot[np.arange(len(y_train)), y_train] = 1.0

    def objective(w: np.ndarray) -> float:
        combined = np.tensordot(w, train_stack, axes=(0, 0))
        return float(np.sum((combined - onehot) ** 2))

    from scipy.optimize import minimize

    x0 = np.full(len(names), 1.0 / len(names))
    result = minimize(objective, x0, method="SLSQP",
                      bounds=[(0.0, 1.0)] * len(names),
                      constraints=[{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}])
    weights = result.x if result.success else x0
    weights = np.clip(weights, 0, None)
    weights = weights / weights.sum()

    combined_test = combine({n: test[n] for n in names}, weights)
    base_losses = {n: log_loss(test[n], y_test) for n in names}
    meta_loss = log_loss(combined_test, y_test)
    return StackResult(
        weights={n: float(w) for n, w in zip(names, weights, strict=True)},
        combined=combined_test, meta_log_loss=meta_loss,
        base_log_losses=base_losses,
        improved=meta_loss < min(base_losses.values()),
    )


def rolling_performance_weights(prob_dict: Mapping[str, np.ndarray], y: np.ndarray,
                                *, window: int = 250, decay: float = 0.99) -> np.ndarray:
    """Weights that adapt through time, computed causally for every step.

    Returns an (n, M) weight matrix where row ``t`` depends only on data before
    ``t`` - the property that makes Method 96 legitimate rather than a
    retrospective curve-fit.
    """
    names, stack = _stack(prob_dict)
    n, k = stack.shape[1], stack.shape[2]
    losses = np.empty((len(names), n))
    for i, name in enumerate(names):
        p = np.clip(prob_dict[name], 1e-12, None)
        losses[i] = -np.log(p[np.arange(n), y])

    weights = np.full((n, len(names)), 1.0 / len(names))
    for t in range(1, n):
        lo = max(0, t - window)
        if t - lo < 5:
            continue
        recent = losses[:, lo:t].mean(axis=1)
        scaled = (recent - recent.min()) / max(decay, 1e-9)
        w = np.exp(-scaled)
        weights[t] = w / w.sum()
    return weights


def apply_weights(prob_dict: Mapping[str, np.ndarray], weights: np.ndarray) -> np.ndarray:
    """Apply a per-step weight matrix produced by :func:`rolling_performance_weights`."""
    names, stack = _stack(prob_dict)
    if weights.shape != (stack.shape[1], len(names)):
        raise ValueError(f"weight matrix shape {weights.shape} does not match "
                         f"({stack.shape[1]}, {len(names)})")
    out = np.einsum("nm,mnk->nk", weights, stack)
    return out / out.sum(axis=1, keepdims=True)
