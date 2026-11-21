"""The method registry: documentation + implementation, joined and validated.

The registry is the single source of truth for what the 100 methods are. Import
time validates that every documented method has an executable runner and that
every runner corresponds to a documented method - so a typo cannot silently drop
a method from the report.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.core.logging import get_logger
from src.mathematics import (
    advanced_statistics,
    frequency,
    machine_learning,
    markov,
    number_theory,
    randomness,
    recurrence,
    time_series,
)
from src.mathematics.catalog_ab import METHODS_AB
from src.mathematics.catalog_cd import METHODS_CD
from src.mathematics.catalog_ef import METHODS_EF
from src.mathematics.catalog_gh import METHODS_GH
from src.mathematics.types import MethodOutput, MethodSpec

log = get_logger(__name__)

CATEGORY_NAMES = {
    "A": "Frequency and Probability",
    "B": "Recency and Occurrence",
    "C": "Transitions and Dependencies",
    "D": "Time Series",
    "E": "Number Theory and Transformations",
    "F": "Randomness and Statistical Structure",
    "G": "Machine Learning",
    "H": "Advanced Probability, Ensembles and Validation",
}

_MODULES = {
    "src.mathematics.frequency": frequency,
    "src.mathematics.recurrence": recurrence,
    "src.mathematics.markov": markov,
    "src.mathematics.time_series": time_series,
    "src.mathematics.number_theory": number_theory,
    "src.mathematics.randomness": randomness,
    "src.mathematics.machine_learning": machine_learning,
    "src.mathematics.advanced_statistics": advanced_statistics,
}


@dataclass(frozen=True)
class RegisteredMethod:
    spec: MethodSpec
    runner: Callable

    @property
    def id(self) -> str:
        return self.spec.id

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def category(self) -> str:
        return self.spec.category

    def run(self, ctx) -> MethodOutput:
        return self.runner(ctx)


def _build_registry() -> dict[str, RegisteredMethod]:
    specs = {m.id: m for m in (METHODS_AB + METHODS_CD + METHODS_EF + METHODS_GH)}
    registry: dict[str, RegisteredMethod] = {}
    for method_id, spec in specs.items():
        module_name, func_name = spec.implementation.split("::")
        module = _MODULES.get(module_name)
        if module is None:
            raise RuntimeError(f"{method_id}: unknown implementation module '{module_name}'")
        runner = getattr(module, func_name, None)
        if runner is None:
            raise RuntimeError(f"{method_id}: '{func_name}' not found in {module_name}")
        registry[method_id] = RegisteredMethod(spec=spec, runner=runner)
    return registry


METHOD_REGISTRY: dict[str, RegisteredMethod] = _build_registry()

#: Methods 91 and 92 are meta-analyses and must run last.
META_METHODS = ["M091", "M092"]
ORDERED_METHOD_IDS = [f"M{i:03d}" for i in range(1, 101)]


def get(method_id: str) -> RegisteredMethod:
    if method_id not in METHOD_REGISTRY:
        raise KeyError(f"unknown method '{method_id}'")
    return METHOD_REGISTRY[method_id]


def all_methods() -> list[RegisteredMethod]:
    return [METHOD_REGISTRY[m] for m in ORDERED_METHOD_IDS if m in METHOD_REGISTRY]


def methods_for_category(letter: str) -> list[RegisteredMethod]:
    return [m for m in all_methods() if m.category.startswith(letter)]


def validate_registry() -> dict:
    """Assert completeness: 100 documented, 100 implemented, ids contiguous."""
    problems: list[str] = []
    ids = list(METHOD_REGISTRY)
    expected = [f"M{i:03d}" for i in range(1, 101)]
    missing = [i for i in expected if i not in METHOD_REGISTRY]
    extra = [i for i in ids if i not in expected]
    if missing:
        problems.append(f"methods documented but not implemented: {missing}")
    if extra:
        problems.append(f"methods implemented but not documented: {extra}")
    for method_id, entry in METHOD_REGISTRY.items():
        if not entry.spec.formula or not entry.spec.variables or not entry.spec.steps:
            problems.append(f"{method_id}: incomplete documentation record")
    by_category: dict[str, int] = {}
    for entry in METHOD_REGISTRY.values():
        letter = entry.category[0]
        by_category[letter] = by_category.get(letter, 0) + 1
    return {
        "n_documented": len({m.id for m in (METHODS_AB + METHODS_CD + METHODS_EF + METHODS_GH)}),
        "n_implemented": len(METHOD_REGISTRY),
        "missing": missing,
        "extra": extra,
        "by_category": by_category,
        "problems": problems,
        "ok": not problems,
    }


def summary_table() -> list[dict]:
    return [
        {
            "id": entry.id,
            "name": entry.name,
            "category": entry.category,
            "implementation": entry.spec.implementation,
            "formula": entry.spec.formula,
        }
        for entry in all_methods()
    ]
