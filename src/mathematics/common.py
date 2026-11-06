"""Shared statistical utilities for the method implementations.

Kept deliberately dependency-light (numpy + scipy) so a method's mathematics is
readable in one place rather than scattered across library calls.
"""

from __future__ import annotations

from typing import Callable, Sequence

import numpy as np
from scipy import stats

EPS = 1e-12


# ---------------------------------------------------------------------------
# distributions
# ---------------------------------------------------------------------------
def uniform(k: int) -> np.ndarray:
    return np.full(k, 1.0 / k)


def empirical(y: np.ndarray, k: int) -> np.ndarray:
    counts = np.bincount(np.asarray(y, dtype=int), minlength=k)[:k].astype(float)
    total = counts.sum()
    return counts / total if total > 0 else uniform(k)


def counts_of(y: np.ndarray, k: int) -> np.ndarray:
    return np.bincount(np.asarray(y, dtype=int), minlength=k)[:k].astype(float)


def _as_probabilities(p: np.ndarray) -> np.ndarray:
    """Non-negative, sums to 1. Exact zeros stay exact zeros."""
    arr = np.clip(np.asarray(p, dtype=float), 0.0, None)
    total = arr.sum()
    return arr / total if total > 0 else uniform(len(arr))


def entropy(p: np.ndarray, base: float = 2.0) -> float:
    """Shannon entropy, with 0 * log 0 taken as 0 (the limiting value)."""
    arr = _as_probabilities(p)
    nz = arr > 0
    return float(-np.sum(arr[nz] * np.log(arr[nz])) / np.log(base))


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    p_arr, q_arr = _as_probabilities(p), _as_probabilities(q)
    nz = p_arr > 0
    # q = 0 where p > 0 is genuinely infinite divergence; the floor keeps the
    # number finite and is stated in the method dossier rather than hidden.
    q_safe = np.maximum(q_arr[nz], EPS)
    return float(np.sum(p_arr[nz] * np.log(p_arr[nz] / q_safe)))


def normalised_entropy(p: np.ndarray) -> float:
    k = len(p)
    return entropy(p) / np.log2(k)


# ---------------------------------------------------------------------------
# contingency tests
# ---------------------------------------------------------------------------
def chi2_uniform(y: np.ndarray, k: int) -> dict:
    counts = counts_of(y, k)
    expected = np.full(k, counts.sum() / k)
    stat = float(np.sum((counts - expected) ** 2 / np.maximum(expected, EPS)))
    dof = k - 1
    p = float(stats.chi2.sf(stat, dof)) if dof > 0 else float("nan")
    return {"statistic": stat, "p_value": p, "dof": dof, "counts": counts,
            "expected": expected, "min_expected": float(expected.min())}


def cramers_v(chi2: float, n: float, shape: tuple[int, int]) -> float:
    r, c = shape
    denom = n * max(min(r - 1, c - 1), 1)
    return float(np.sqrt(chi2 / denom)) if denom > 0 else float("nan")


def chi2_contingency(table: np.ndarray) -> dict:
    table = np.asarray(table, dtype=float)
    keep_r = table.sum(axis=1) > 0
    keep_c = table.sum(axis=0) > 0
    trimmed = table[np.ix_(keep_r, keep_c)]
    if trimmed.shape[0] < 2 or trimmed.shape[1] < 2:
        return {"statistic": float("nan"), "p_value": float("nan"), "dof": 0,
                "cramers_v": float("nan"), "min_expected": 0.0}
    stat, p, dof, expected = stats.chi2_contingency(trimmed, correction=False)
    return {
        "statistic": float(stat), "p_value": float(p), "dof": int(dof),
        "cramers_v": cramers_v(stat, trimmed.sum(), trimmed.shape),
        "min_expected": float(expected.min()),
    }


def mutual_information(x: Sequence, y: Sequence, kx: int, ky: int) -> float:
    x = np.asarray(x, dtype=int)
    y = np.asarray(y, dtype=int)
    joint = np.zeros((kx, ky))
    np.add.at(joint, (x, y), 1.0)
    n = joint.sum()
    if n == 0:
        return 0.0
    pxy = joint / n
    px = pxy.sum(axis=1, keepdims=True)
    py = pxy.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(pxy > 0, pxy / (px @ py), 1.0)
        return float(np.nansum(np.where(pxy > 0, pxy * np.log2(np.maximum(ratio, EPS)), 0.0)))


def conditional_mutual_information(x, y, z, kx: int, ky: int, kz: int) -> float:
    x, y, z = (np.asarray(v, dtype=int) for v in (x, y, z))
    total = 0.0
    for level in range(kz):
        mask = z == level
        if mask.sum() < 2:
            continue
        weight = mask.mean()
        total += weight * mutual_information(x[mask], y[mask], kx, ky)
    return float(total)


# ---------------------------------------------------------------------------
# inference helpers
# ---------------------------------------------------------------------------
def permutation_pvalue(statistic_fn: Callable[[np.ndarray], float], y: np.ndarray,
                       n_perm: int, rng: np.random.Generator,
                       *, alternative: str = "greater") -> dict:
    """Empirical p-value for an arbitrary statistic under random shuffling."""
    y = np.asarray(y)
    observed = float(statistic_fn(y))
    null = np.empty(n_perm)
    shuffled = y.copy()
    for i in range(n_perm):
        rng.shuffle(shuffled)
        null[i] = float(statistic_fn(shuffled))
    if alternative == "greater":
        p = (1 + np.sum(null >= observed)) / (n_perm + 1)
    elif alternative == "less":
        p = (1 + np.sum(null <= observed)) / (n_perm + 1)
    else:
        p = (1 + np.sum(np.abs(null) >= abs(observed))) / (n_perm + 1)
    return {
        "observed": observed, "p_value": float(p), "null_mean": float(null.mean()),
        "null_std": float(null.std(ddof=1)), "n_permutations": n_perm,
        "null_quantiles": [float(np.quantile(null, q)) for q in (0.025, 0.5, 0.975)],
    }


def binomial_test(successes: int, trials: int, p0: float) -> dict:
    if trials == 0:
        return {"p_value": float("nan"), "estimate": float("nan")}
    result = stats.binomtest(int(successes), int(trials), p0, alternative="two-sided")
    return {"p_value": float(result.pvalue), "estimate": successes / trials,
            "ci_low": float(result.proportion_ci().low),
            "ci_high": float(result.proportion_ci().high)}


def normal_ci(values: np.ndarray, level: float = 0.95) -> dict:
    values = np.asarray(values, dtype=float)
    n = len(values)
    if n < 2:
        return {"mean": float(values.mean()) if n else float("nan"),
                "se": float("nan"), "ci_low": float("nan"), "ci_high": float("nan")}
    se = values.std(ddof=1) / np.sqrt(n)
    crit = stats.norm.ppf(1 - (1 - level) / 2)
    return {"mean": float(values.mean()), "se": float(se),
            "ci_low": float(values.mean() - crit * se),
            "ci_high": float(values.mean() + crit * se)}


def holm(p_values: Sequence[float]) -> list[float]:
    p = np.asarray([1.0 if v is None else float(v) for v in p_values], dtype=float)
    n = len(p)
    order = np.argsort(p)
    adjusted = np.empty(n)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (n - rank) * p[idx])
        adjusted[idx] = min(running, 1.0)
    return adjusted.tolist()


# ---------------------------------------------------------------------------
# sequence helpers
# ---------------------------------------------------------------------------
def transitions(y: np.ndarray, k: int, order: int = 1) -> np.ndarray:
    """Count matrix of order-``order`` transitions."""
    y = np.asarray(y, dtype=int)
    if order == 1:
        table = np.zeros((k, k))
        np.add.at(table, (y[:-1], y[1:]), 1.0)
        return table
    states = k ** order
    table = np.zeros((states, k))
    for t in range(order, len(y)):
        ctx = 0
        for j in range(order):
            ctx = ctx * k + int(y[t - order + j])
        table[ctx, y[t]] += 1.0
    return table


def encode_contexts(y: np.ndarray, order: int, k: int) -> np.ndarray:
    """Context index for each position t (uses y[t-order..t-1])."""
    y = np.asarray(y, dtype=int)
    n = len(y)
    out = np.full(n, -1, dtype=int)
    for t in range(order, n):
        ctx = 0
        for j in range(order):
            ctx = ctx * k + int(y[t - order + j])
        out[t] = ctx
    return out


def runs(sequence: np.ndarray) -> int:
    seq = np.asarray(sequence)
    if len(seq) == 0:
        return 0
    return int(1 + np.sum(seq[1:] != seq[:-1]))


def indicator(y: np.ndarray, category: int) -> np.ndarray:
    return (np.asarray(y, dtype=int) == int(category)).astype(int)


def gaps_for(y: np.ndarray, category: int) -> np.ndarray:
    idx = np.flatnonzero(np.asarray(y, dtype=int) == int(category))
    return np.diff(idx) if len(idx) > 1 else np.array([], dtype=int)


def autocorrelation(x: np.ndarray, max_lag: int) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    x = x - x.mean()
    denom = float(np.dot(x, x))
    if denom <= 0:
        return np.zeros(max_lag)
    return np.array([float(np.dot(x[:-k], x[k:]) / denom) if k > 0 else 1.0
                     for k in range(max_lag + 1)])


def partial_autocorrelation(x: np.ndarray, max_lag: int) -> np.ndarray:
    """Durbin-Levinson recursion on the sample autocorrelations."""
    acf = autocorrelation(x, max_lag)
    pacf = np.zeros(max_lag + 1)
    pacf[0] = 1.0
    if max_lag < 1:
        return pacf
    pacf[1] = acf[1]
    phi = np.zeros((max_lag + 1, max_lag + 1))
    phi[1, 1] = acf[1]
    for k in range(2, max_lag + 1):
        num = acf[k] - sum(phi[k - 1, j] * acf[k - j] for j in range(1, k))
        den = 1.0 - sum(phi[k - 1, j] * acf[j] for j in range(1, k))
        phi[k, k] = num / den if abs(den) > EPS else 0.0
        for j in range(1, k):
            phi[k, j] = phi[k - 1, j] - phi[k, k] * phi[k - 1, k - j]
        pacf[k] = phi[k, k]
    return pacf


def min_train_for(n: int, floor: int = 100, fraction: float = 0.2) -> int:
    """Evaluation window start: enough history to estimate, enough left to test."""
    return int(max(min(floor, n // 3), min(int(n * fraction), n // 2)))


def safe_divide(a: float, b: float) -> float:
    return float(a / b) if b else float("nan")
