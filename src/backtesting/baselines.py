"""Baselines.

Every model must beat the strongest of these before it may be called useful. All
of them are *online*: at each step they predict from state built only from
previously revealed outcomes, then absorb the new outcome. That makes them
naturally leak-free and cheap enough to run over the whole timeline.

Baselines implemented
---------------------
``uniform``      Uniform over the declared outcome space (the null model).
``frequency``    Expanding empirical frequency (Laplace-smoothed).
``rolling``      Frequency over a fixed trailing window.
``bayes``        Dirichlet-multinomial posterior mean (Jeffreys / Laplace priors).
``recency``      Exponentially-weighted frequency.
``markov1``      First-order Markov chain, Laplace-smoothed transition rows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np


class OnlineModel(Protocol):
    name: str

    def reset(self, k: int) -> None: ...
    def predict(self) -> np.ndarray: ...
    def update(self, y: int) -> None: ...


def _normalise(v: np.ndarray) -> np.ndarray:
    v = np.clip(np.asarray(v, dtype=float), 1e-12, None)
    return v / v.sum()


@dataclass
class UniformBaseline:
    name: str = "uniform"
    k: int = 10

    def reset(self, k: int) -> None:
        self.k = k

    def predict(self) -> np.ndarray:
        return np.full(self.k, 1.0 / self.k)

    def update(self, y: int) -> None:  # noqa: ARG002 - uniform ignores data
        return


@dataclass
class FrequencyBaseline:
    """Expanding relative frequency with additive smoothing."""

    name: str = "frequency"
    alpha: float = 1.0
    counts: np.ndarray = field(default_factory=lambda: np.zeros(10))

    def reset(self, k: int) -> None:
        self.counts = np.zeros(k)

    def predict(self) -> np.ndarray:
        return _normalise(self.counts + self.alpha)

    def update(self, y: int) -> None:
        self.counts[y] += 1.0


@dataclass
class RollingFrequencyBaseline:
    """Frequency in the trailing ``window`` draws."""

    name: str = "rolling"
    window: int = 50
    alpha: float = 1.0
    history: list[int] = field(default_factory=list)
    k: int = 10

    def reset(self, k: int) -> None:
        self.history = []
        self.k = k

    def predict(self) -> np.ndarray:
        recent = self.history[-self.window:]
        counts = np.full(self.k, self.alpha)
        for value in recent:
            counts[value] += 1.0
        return _normalise(counts)

    def update(self, y: int) -> None:
        self.history.append(int(y))


@dataclass
class BayesianBaseline:
    """Dirichlet-multinomial posterior mean: ``(alpha + n) / (sum(alpha) + N)``.

    ``alpha=0.5`` gives the Jeffreys prior, ``alpha=1`` the Laplace prior.
    """

    name: str = "bayes"
    alpha: float = 0.5
    counts: np.ndarray = field(default_factory=lambda: np.zeros(10))

    def reset(self, k: int) -> None:
        self.counts = np.zeros(k)

    def predict(self) -> np.ndarray:
        return _normalise(self.counts + self.alpha)

    def update(self, y: int) -> None:
        self.counts[y] += 1.0

    def credible_interval(self, level: float = 0.95) -> list[tuple[float, float]]:
        """Beta marginal credible intervals, i.e. Beta(a_k, A0-a_k)."""
        from scipy.stats import beta as beta_dist

        total = self.counts.sum() + self.alpha * len(self.counts)
        out = []
        lo, hi = (1 - level) / 2, 1 - (1 - level) / 2
        for count in self.counts:
            a, b = count + self.alpha, total - count - self.alpha
            out.append((float(beta_dist.ppf(lo, a, b)), float(beta_dist.ppf(hi, a, b))))
        return out


@dataclass
class RecencyBaseline:
    """Exponentially-weighted frequency; ``decay`` close to 1 = long memory."""

    name: str = "recency"
    decay: float = 0.95
    weights: np.ndarray = field(default_factory=lambda: np.zeros(10))

    def reset(self, k: int) -> None:
        self.weights = np.zeros(k)

    def predict(self) -> np.ndarray:
        if self.weights.sum() <= 0:
            return np.full(len(self.weights), 1.0 / len(self.weights))
        return _normalise(self.weights + 1e-3)  # tiny ridge keeps unseen classes alive

    def update(self, y: int) -> None:
        self.weights *= self.decay
        self.weights[y] += 1.0


@dataclass
class Markov1Baseline:
    """First-order Markov chain with Laplace-smoothed transition rows."""

    name: str = "markov1"
    alpha: float = 1.0
    counts: np.ndarray = field(default_factory=lambda: np.zeros((10, 10)))
    last: int = -1
    k: int = 10

    def reset(self, k: int) -> None:
        self.counts = np.zeros((k, k))
        self.last = -1
        self.k = k

    def predict(self) -> np.ndarray:
        if self.last < 0 or self.counts[self.last].sum() == 0:
            return np.full(self.k, 1.0 / self.k)
        return _normalise(self.counts[self.last] + self.alpha)

    def update(self, y: int) -> None:
        if self.last >= 0:
            self.counts[self.last, y] += 1.0
        self.last = int(y)


BASELINE_FACTORIES = {
    "uniform": lambda **kw: UniformBaseline(**kw),
    "frequency": lambda **kw: FrequencyBaseline(**kw),
    "rolling50": lambda **kw: RollingFrequencyBaseline(window=50, **kw),
    "bayes_jeffreys": lambda **kw: BayesianBaseline(alpha=0.5, **kw),
    "recency_095": lambda **kw: RecencyBaseline(decay=0.95, **kw),
    "markov1": lambda **kw: Markov1Baseline(**kw),
}


def make_baselines(alpha: float = 1.0) -> list[OnlineModel]:
    """The standard baseline panel every model is measured against."""
    return [
        UniformBaseline(),
        FrequencyBaseline(alpha=alpha),
        RollingFrequencyBaseline(window=50),
        BayesianBaseline(alpha=1.0),
        BayesianBaseline(alpha=0.5, name="bayes_jeffreys"),
        RecencyBaseline(decay=0.95),
        Markov1Baseline(alpha=1.0),
    ]
