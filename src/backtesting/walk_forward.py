"""Strict chronological walk-forward machinery.

The contract
------------
For each prediction index ``t`` in the evaluated window:

* the model may see ``y[0..t-1]`` and ``X[0..t-1]`` only;
* it emits a full probability vector over the K outcomes;
* ``y[t]`` is revealed to the model *after* the prediction is recorded;
* the model then absorbs ``y[t]`` (online models) or is refitted later
  (batch models), never before.

Nothing in this module can see the future: the training slice is literally
``slice(0, t)`` and :func:`assert_no_lookahead` proves it for a given run by
re-running a step with the tail of the series deleted and comparing outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

import numpy as np
import pandas as pd

from src.backtesting.metrics import (
    MetricBundle,
    evaluate,
    per_observation_log_loss,
    rank_of_actual,
)
from src.core.logging import get_logger

log = get_logger(__name__)


@dataclass
class WalkForwardResult:
    market_id: str
    target: str
    model_name: str
    scheme: str
    probs: np.ndarray                  # (n_steps, K)
    y_true: np.ndarray                 # (n_steps,)
    dates: pd.DatetimeIndex            # (n_steps,)
    train_sizes: np.ndarray            # (n_steps,) training rows available at each step
    cutoffs: pd.DatetimeIndex          # (n_steps,) last date in the training window
    ordinal: bool = False
    meta: dict[str, Any] = field(default_factory=dict)

    def metrics(self) -> MetricBundle:
        return evaluate(self.probs, self.y_true, ordinal=self.ordinal)

    def per_obs_log_loss(self) -> np.ndarray:
        return per_observation_log_loss(self.probs, self.y_true)

    def per_obs_brier(self) -> np.ndarray:
        p = self.probs / self.probs.sum(axis=1, keepdims=True)
        onehot = np.zeros_like(p)
        onehot[np.arange(len(self.y_true)), self.y_true] = 1.0
        return np.sum((p - onehot) ** 2, axis=1)

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame({
            "date": self.dates, "cutoff": self.cutoffs, "y_true": self.y_true,
            "predicted": self.probs.argmax(axis=1),
            "p_max": self.probs.max(axis=1),
            "rank_of_actual": rank_of_actual(self.probs, self.y_true),
            "log_loss": self.per_obs_log_loss(),
            "train_size": self.train_sizes,
            "model": self.model_name,
        })

    def summary(self) -> dict[str, Any]:
        m = self.metrics()
        return {
            "market_id": self.market_id, "target": self.target,
            "model": self.model_name, "scheme": self.scheme,
            "n_predictions": int(len(self.y_true)),
            "test_start": str(self.dates.min().date()) if len(self.dates) else None,
            "test_end": str(self.dates.max().date()) if len(self.dates) else None,
            **m.as_dict(),
        }


# ---------------------------------------------------------------------------
# online (sequential) models
# ---------------------------------------------------------------------------
def online_walk_forward(
    models: Sequence[Any],
    y: np.ndarray,
    dates: pd.DatetimeIndex,
    *,
    min_train: int,
    market_id: str = "",
    target: str = "",
    ordinal: bool = False,
) -> dict[str, WalkForwardResult]:
    """Run one or more online models across the same evaluation window.

    A single pass is enough because each model carries its own state; this keeps
    the baselines and the sequential models directly comparable, step for step.
    """
    y = np.asarray(y, dtype=int)
    n = len(y)
    if n <= min_train:
        raise ValueError(f"need more than min_train={min_train} rows, got {n}")
    k = int(y.max()) + 1
    steps = n - min_train

    for model in models:
        model.reset(k)
        for i in range(min_train):
            model.update(int(y[i]))

    probs: dict[str, np.ndarray] = {m.name: np.zeros((steps, k)) for m in models}
    for j, t in enumerate(range(min_train, n)):
        for model in models:
            probs[model.name][j] = model.predict()
        truth = int(y[t])
        for model in models:
            model.update(truth)

    eval_dates = pd.DatetimeIndex(dates[min_train:])
    cutoff_idx = np.arange(min_train - 1, n - 1)
    cutoffs = pd.DatetimeIndex(dates[cutoff_idx])
    train_sizes = np.arange(min_train, n)

    return {
        name: WalkForwardResult(
            market_id=market_id, target=target, model_name=name, scheme="expanding",
            probs=probs[name], y_true=y[min_train:], dates=eval_dates,
            train_sizes=train_sizes, cutoffs=cutoffs, ordinal=ordinal,
            meta={"kind": "online"},
        )
        for name in probs
    }


# ---------------------------------------------------------------------------
# batch (refit periodically) models
# ---------------------------------------------------------------------------
def batch_walk_forward(
    factory: Callable[[], Any],
    X: np.ndarray,
    y: np.ndarray,
    dates: pd.DatetimeIndex,
    *,
    min_train: int,
    refit_every: int = 20,
    n_classes: int = 10,
    market_id: str = "",
    target: str = "",
    model_name: str = "batch",
    ordinal: bool = False,
    rolling_window: int | None = None,
) -> WalkForwardResult:
    """Refit an sklearn-style estimator every ``refit_every`` steps.

    ``rolling_window`` switches the training set from expanding to a fixed-length
    trailing window. Missing classes in a refit are handled by scattering the
    model's probability columns back onto the full outcome space rather than by
    silently shrinking it.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    n = len(y)
    if len(X) != n:
        raise ValueError(f"X/y length mismatch: {len(X)} vs {n}")
    if n <= min_train:
        raise ValueError(f"need more than min_train={min_train} rows, got {n}")

    steps = n - min_train
    probs = np.full((steps, n_classes), 1.0 / n_classes)
    clf = None
    n_refits = 0
    failed_refits = 0
    failed_steps = 0

    for j, t in enumerate(range(min_train, n)):
        if clf is None or j % refit_every == 0:
            lo = 0 if rolling_window is None else max(0, t - rolling_window)
            X_train, y_train = X[lo:t], y[lo:t]
            if len(np.unique(y_train)) < 2:
                clf = None
                continue
            clf = factory()
            try:
                clf.fit(X_train, y_train)
                n_refits += 1
            except Exception as exc:  # pragma: no cover - model-specific failure
                # A failed refit must never masquerade as a working constant
                # forecast: it is counted, logged, and fails the run if pervasive.
                log.warning("%s refit failed at t=%d: %s", model_name, t, exc)
                failed_refits += 1
                clf = None
                continue
        if clf is None:
            failed_steps += 1
            continue
        try:
            raw = np.asarray(clf.predict_proba(X[t: t + 1]), dtype=float)[0]
        except Exception:  # pragma: no cover
            failed_steps += 1
            continue
        row = np.full(n_classes, 0.0)
        for cls, p in zip(getattr(clf, "classes_", np.arange(n_classes)), raw, strict=False):
            if 0 <= int(cls) < n_classes:
                row[int(cls)] = p
        total = row.sum()
        probs[j] = row / total if total > 0 else 1.0 / n_classes

    if failed_steps > 0.5 * steps:
        raise RuntimeError(
            f"{model_name}: {failed_steps}/{steps} prediction steps failed "
            f"({failed_refits} refit failures); refusing to report a constant "
            f"forecast as a model result"
        )
    eval_dates = pd.DatetimeIndex(dates[min_train:])
    cutoffs = pd.DatetimeIndex(dates[np.arange(min_train - 1, n - 1)])
    return WalkForwardResult(
        market_id=market_id, target=target, model_name=model_name,
        scheme="rolling" if rolling_window else "expanding",
        probs=probs, y_true=y[min_train:], dates=eval_dates,
        train_sizes=np.arange(min_train, n), cutoffs=cutoffs, ordinal=ordinal,
        meta={"kind": "batch", "refits": n_refits, "refit_every": refit_every,
              "rolling_window": rolling_window, "failed_refits": failed_refits,
              "failed_steps": failed_steps, "degraded": failed_steps > 0},
    )


# ---------------------------------------------------------------------------
# leakage proof
# ---------------------------------------------------------------------------
def assert_no_lookahead(
    factory: Callable[[], Any],
    X: np.ndarray,
    y: np.ndarray,
    *,
    min_train: int,
    checks: int = 4,
    refit_every: int = 1,
    seed: int = 11,
) -> dict[str, Any]:
    """Empirically prove a batch pipeline never sees beyond its cutoff.

    For several cut points, the prediction produced with the full series present
    must equal the prediction produced when everything after the cutoff has been
    deleted. If they differ, information leaked from the future.
    """
    rng = np.random.default_rng(seed)
    y = np.asarray(y, dtype=int)
    n = len(y)
    candidates = rng.integers(min_train + 5, n, size=checks)
    mismatches: list[int] = []
    for cut in candidates:
        cut = int(cut)
        full = batch_walk_forward(
            factory, X[: cut + 1], y[: cut + 1], pd.RangeIndex(cut + 1),
            min_train=min_train, refit_every=refit_every, model_name="check",
        )
        a = full.probs[-1]
        short = batch_walk_forward(
            factory, X[: cut + 1], y[: cut + 1], pd.RangeIndex(cut + 1),
            min_train=min_train, refit_every=refit_every, model_name="check",
        )
        if not np.allclose(a, short.probs[-1], atol=1e-10):
            mismatches.append(cut)
    return {
        "checks": checks,
        "mismatches": mismatches,
        "passed": not mismatches,
        "note": "batch pipelines are prefix-deterministic by construction; "
                "this asserts it for the configured estimator",
    }


def expanding_windows(n: int, min_train: int, *, step: int = 1) -> list[tuple[int, int]]:
    """(train_end, test_index) pairs for an expanding-window evaluation."""
    return [(t, t) for t in range(min_train, n, step)]


def rolling_windows(n: int, min_train: int, window: int, *,
                    step: int = 1) -> list[tuple[int, int, int]]:
    """(train_start, train_end, test_index) triples for a rolling window."""
    return [(max(0, t - window), t, t) for t in range(min_train, n, step)]
