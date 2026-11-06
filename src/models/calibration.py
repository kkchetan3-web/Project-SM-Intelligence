"""Probability calibration.

A model can rank well and still be badly calibrated, which is fatal for any use
that reads the probabilities rather than just the ordering. Three calibrators are
implemented, all fitted **only on a chronological calibration slice** that
precedes the data they are applied to:

``IsotonicCalibrator``   one-vs-rest isotonic regression, renormalised
``PlattCalibrator``      per-class logistic rescaling (a.k.a. temperature+bias)
``DirichletCalibrator``  vector scaling: p' ~ softmax(W log p + b)

All expose ``fit(probs, y)`` and ``transform(probs)`` and preserve the simplex.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from sklearn.isotonic import IsotonicRegression

EPS = 1e-12


def _safe_log(p: np.ndarray) -> np.ndarray:
    return np.log(np.clip(p, 1e-6, 1.0))


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


@dataclass
class IsotonicCalibrator:
    name: str = "isotonic"
    models: list[Any] = field(default_factory=list)
    n_classes: int = 0

    def fit(self, probs: np.ndarray, y: np.ndarray) -> "IsotonicCalibrator":
        probs = np.asarray(probs, dtype=float)
        y = np.asarray(y, dtype=int)
        self.n_classes = probs.shape[1]
        self.models = []
        for c in range(self.n_classes):
            target = (y == c).astype(float)
            if len(np.unique(target)) < 2:
                self.models.append(None)
                continue
            iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
            iso.fit(probs[:, c], target)
            self.models.append(iso)
        return self

    def transform(self, probs: np.ndarray) -> np.ndarray:
        probs = np.asarray(probs, dtype=float)
        out = np.empty_like(probs)
        for c, model in enumerate(self.models):
            if model is None:
                out[:, c] = probs[:, c]
            else:
                out[:, c] = np.clip(model.predict(probs[:, c]), 1e-6, 1.0)
        return out / out.sum(axis=1, keepdims=True)


@dataclass
class PlattCalibrator:
    """Per-class ``a * logit(p) + b`` fitted by regularised logistic regression."""

    name: str = "platt"
    weights: np.ndarray = field(default_factory=lambda: np.zeros((0, 2)))
    n_classes: int = 0

    def fit(self, probs: np.ndarray, y: np.ndarray, *, l2: float = 1.0) -> "PlattCalibrator":
        from sklearn.linear_model import LogisticRegression

        probs = np.clip(np.asarray(probs, dtype=float), 1e-6, 1 - 1e-6)
        y = np.asarray(y, dtype=int)
        self.n_classes = probs.shape[1]
        self.weights = np.zeros((self.n_classes, 2))
        for c in range(self.n_classes):
            target = (y == c).astype(int)
            if len(np.unique(target)) < 2:
                self.weights[c] = [0.0, 1.0]
                continue
            x = np.log(probs[:, c] / (1 - probs[:, c])).reshape(-1, 1)
            lr = LogisticRegression(C=1.0 / max(l2, EPS), max_iter=500)
            lr.fit(x, target)
            self.weights[c] = [float(lr.intercept_[0]), float(lr.coef_[0][0])]
        return self

    def transform(self, probs: np.ndarray) -> np.ndarray:
        probs = np.clip(np.asarray(probs, dtype=float), 1e-6, 1 - 1e-6)
        out = np.empty_like(probs)
        for c in range(probs.shape[1]):
            a, b = self.weights[c] if c < len(self.weights) else (0.0, 1.0)
            out[:, c] = 1.0 / (1.0 + np.exp(-(a + b * np.log(probs[:, c] / (1 - probs[:, c])))))
        return out / out.sum(axis=1, keepdims=True)


@dataclass
class DirichletCalibrator:
    """Vector scaling: ``softmax(W @ log p + b)``, with ``W`` initialised to ``I``.

    Fitted by gradient descent on the multinomial log loss with L2 shrinkage
    towards the identity, which is what makes it safe on the modest calibration
    samples these markets provide.
    """

    name: str = "dirichlet"
    W: np.ndarray | None = None
    b: np.ndarray | None = None
    n_classes: int = 0

    def fit(self, probs: np.ndarray, y: np.ndarray, *, l2: float = 0.05,
            lr: float = 0.05, n_iter: int = 400) -> "DirichletCalibrator":
        probs = np.asarray(probs, dtype=float)
        y = np.asarray(y, dtype=int)
        n, k = probs.shape
        self.n_classes = k
        logp = _safe_log(probs)
        W = np.eye(k)
        b = np.zeros(k)
        onehot = np.zeros((n, k))
        onehot[np.arange(n), y] = 1.0
        for _ in range(n_iter):
            z = logp @ W.T + b
            p = _softmax(z)
            grad_z = (p - onehot) / n
            grad_W = grad_z.T @ logp + l2 * (W - np.eye(k))
            grad_b = grad_z.sum(axis=0)
            W -= lr * grad_W
            b -= lr * grad_b
        self.W, self.b = W, b
        return self

    def transform(self, probs: np.ndarray) -> np.ndarray:
        if self.W is None or self.b is None:
            return np.asarray(probs, dtype=float)
        return _softmax(_safe_log(np.asarray(probs, dtype=float)) @ self.W.T + self.b)


@dataclass
class TemperatureCalibrator:
    """Single-parameter power scaling: ``p' ~ p ** (1/T)``, renormalised."""

    name: str = "temperature"
    temperature: float = 1.0

    def fit(self, probs: np.ndarray, y: np.ndarray) -> "TemperatureCalibrator":
        probs = np.asarray(probs, dtype=float)
        y = np.asarray(y, dtype=int)
        grid = np.linspace(0.5, 2.5, 41)
        best_ll, best_t = np.inf, 1.0
        for t in grid:
            scaled = np.clip(probs, 1e-12, None) ** (1.0 / t)
            scaled = scaled / scaled.sum(axis=1, keepdims=True)
            ll = -np.mean(np.log(np.clip(scaled[np.arange(len(y)), y], 1e-12, None)))
            if ll < best_ll:
                best_ll, best_t = ll, float(t)
        self.temperature = best_t
        return self

    def transform(self, probs: np.ndarray) -> np.ndarray:
        scaled = np.clip(np.asarray(probs, dtype=float), 1e-12, None) ** (1.0 / self.temperature)
        return scaled / scaled.sum(axis=1, keepdims=True)


def make_calibrator(name: str) -> Any:
    if name == "isotonic":
        return IsotonicCalibrator()
    if name == "platt":
        return PlattCalibrator()
    if name == "dirichlet":
        return DirichletCalibrator()
    if name == "temperature":
        return TemperatureCalibrator()
    raise ValueError(f"unknown calibrator '{name}'")


def chronological_calibration_split(n: int, fraction: float = 0.3) -> tuple[np.ndarray, np.ndarray]:
    """Early slice for fitting the calibrator, later slice for judging it."""
    cut = max(10, int(n * fraction))
    cut = min(cut, n - 5)
    return np.arange(0, cut), np.arange(cut, n)


def evaluate_calibration(probs: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    from src.backtesting.metrics import (
        calibration_slope,
        calibration_table,
        expected_calibration_error,
        log_loss,
    )

    slope = calibration_slope(probs, y)
    return {
        "log_loss": round(log_loss(probs, y), 6),
        "ece": round(expected_calibration_error(probs, y), 6),
        "slope": None if slope is None else round(slope["slope"], 4),
        "intercept": None if slope is None else round(slope["intercept"], 4),
        "table": calibration_table(probs, y),
    }
