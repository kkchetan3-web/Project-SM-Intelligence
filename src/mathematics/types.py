"""Shared types for the 100-method research framework.

A *method* is a documented statistical procedure plus an executable
implementation. The framework's contract with every method is:

* it receives a :class:`MethodContext` containing only validated, cleaned data
  and the resolved research parameters;
* it returns a :class:`MethodOutput` carrying real computed numbers, the sample
  size those numbers came from, and a plain-language interpretation;
* if the data cannot support the method, it says so via ``status`` rather than
  emitting a fabricated number.

``status`` values are deliberately narrow so the report can count them exactly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
import pandas as pd


STATUS_COMPUTED = "computed"
STATUS_NOT_APPLICABLE = "not_applicable"
STATUS_INSUFFICIENT_DATA = "insufficient_data"
STATUS_UNAVAILABLE = "dependency_unavailable"
STATUS_FAILED = "failed"


@dataclass
class MethodContext:
    """Everything a method is allowed to see."""

    config: Any                       # resolved Config
    market_id: str
    market: Any                       # MarketSpec
    target: str                       # 'open' | 'close'
    space: str                        # 'ank' | 'jodi' | 'panna'
    k: int                            # size of the outcome space
    y: np.ndarray                     # integer-coded outcomes, chronological
    labels: list[str]                 # label for each code
    dates: pd.DatetimeIndex
    results: pd.DataFrame             # cleaned result table (active rows)
    series: pd.Series                 # date-indexed outcome series
    params: dict[str, Any]            # research.yaml 'methods' section
    seed: int
    dataset: str
    features: pd.DataFrame | None = None   # causal feature frame for this target
    model_panel: Any = None                # lazily built WalkForwardPanel
    extras: dict[str, Any] = field(default_factory=dict)

    @property
    def n(self) -> int:
        return len(self.y)

    def rng(self, offset: int = 0) -> np.random.Generator:
        """Deterministic per-method generator so results reproduce exactly."""
        return np.random.default_rng(self.seed + offset)

    def label(self, code: int) -> str:
        if 0 <= code < len(self.labels):
            return self.labels[code]
        return str(code)

    def describe(self) -> dict[str, Any]:
        return {
            "market": self.market_id, "target": self.target, "space": self.space,
            "k": self.k, "n": self.n, "dataset": self.dataset,
            "first_date": str(self.dates[0].date()) if self.n else None,
            "last_date": str(self.dates[-1].date()) if self.n else None,
        }


@dataclass
class Finding:
    """One number, with the sample size that produced it."""

    metric_name: str
    metric_value: float | None
    statistic: float | None = None
    p_value: float | None = None
    effect_size: float | None = None
    sample_size: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def as_row(self, method: "MethodSpec", ctx: MethodContext | None,
               scope: str = "full_sample") -> dict[str, Any]:
        return {
            "method_id": method.id,
            "method_name": method.name,
            "category": method.category,
            "market_id": ctx.market_id if ctx else None,
            "target": ctx.target if ctx else None,
            "scope": scope,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "effect_size": self.effect_size,
            "sample_size": self.sample_size if self.sample_size is not None
            else (ctx.n if ctx else None),
            "extra": self.extra or None,
        }


@dataclass
class MethodOutput:
    status: str
    findings: list[Finding] = field(default_factory=list)
    narrative: str = ""
    walk_forward: dict[str, Any] | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == STATUS_COMPUTED


@dataclass(frozen=True)
class MethodSpec:
    """Documentation record for one of the 100 methods."""

    id: str
    name: str
    category: str
    formula: str
    theory: str
    objective: str
    assumptions: tuple[str, ...]
    variables: tuple[tuple[str, str], ...]
    steps: tuple[str, ...]
    limitations: str
    data_requirements: str
    implementation: str
    references: str = ""

    @property
    def number(self) -> int:
        return int(self.id[1:])

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "category": self.category,
            "formula": self.formula, "theory": self.theory, "objective": self.objective,
            "assumptions": list(self.assumptions),
            "variables": [{"symbol": s, "meaning": m} for s, m in self.variables],
            "steps": list(self.steps), "limitations": self.limitations,
            "data_requirements": self.data_requirements,
            "implementation": self.implementation, "references": self.references,
        }


Runner = Callable[[MethodContext], MethodOutput]


def finding(metric_name: str, metric_value: float | None, **kwargs: Any) -> Finding:
    """Convenience constructor that also sanitises numpy scalars."""
    def _f(v: Any) -> Any:
        if v is None:
            return None
        if isinstance(v, (np.floating, np.integer)):
            v = v.item()
        if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
            return None
        return v

    return Finding(
        metric_name=metric_name, metric_value=_f(metric_value),
        statistic=_f(kwargs.get("statistic")), p_value=_f(kwargs.get("p_value")),
        effect_size=_f(kwargs.get("effect_size")),
        sample_size=kwargs.get("sample_size"), extra=kwargs.get("extra", {}),
    )


def note(condition: bool, text: str) -> str:
    return f"{'[yes]' if condition else '[no]'} {text}"
