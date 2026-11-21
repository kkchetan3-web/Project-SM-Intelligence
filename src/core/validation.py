"""Data integrity rules.

Every rule here exists because a specific, common failure mode would otherwise
silently corrupt a research result:

======================  ====================================================
Failure mode            Guard
======================  ====================================================
``"07"`` -> ``7``       :func:`validate_result_value` keeps fixed-width
                        strings and checks leading zeros explicitly.
Duplicate dates         :func:`find_duplicate_dates`.
Out-of-order timelines  :func:`validate_chronology`.
Synthetic data leaking  :func:`assert_dataset_isolation`.
Probability drift       :func:`normalise_probabilities` +
                        :func:`assert_probability_simplex`.
Feature leakage         :func:`assert_no_future_information`.
======================  ====================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

ANK_SUPPORT: tuple[int, ...] = tuple(range(10))
JODI_SUPPORT: tuple[str, ...] = tuple(f"{i:02d}" for i in range(100))


class ValidationError(ValueError):
    """Raised when data violates a hard integrity rule."""


# ---------------------------------------------------------------------------
# result-value rules
# ---------------------------------------------------------------------------
def validate_result_value(value: Any, space: str) -> str | int:
    """Validate and canonicalise a single result component.

    Leading zeros are preserved for fixed-width spaces (``jodi``, ``panna``):
    ``"07"`` stays ``"07"`` and never becomes ``7``.
    """
    if value is None:
        raise ValidationError("result value is None")
    if isinstance(value, float):
        if not np.isfinite(value) or not float(value).is_integer():
            raise ValidationError(f"non-integer float result value: {value!r}")
        value = int(value)

    if space == "ank":
        try:
            ivalue = int(str(value).strip())
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"ank result is not an integer: {value!r}") from exc
        if ivalue not in ANK_SUPPORT:
            raise ValidationError(f"ank result out of range 0-9: {value!r}")
        return ivalue

    if space == "jodi":
        text = str(value).strip()
        if not text.isdigit() or len(text) > 2:
            raise ValidationError(f"jodi must be 1-2 numeric chars: {value!r}")
        text = text.zfill(2)  # canonical form is always 2 chars
        if text not in JODI_SUPPORT:
            raise ValidationError(f"jodi out of range 00-99: {value!r}")
        return text

    if space == "panna":
        text = str(value).strip()
        if not text.isdigit() or len(text) != 3:
            raise ValidationError(f"panna must be exactly 3 digits: {value!r}")
        return text

    raise ValidationError(f"unknown outcome space '{space}'")


def leading_zero_preserved(original: str, stored: str) -> bool:
    """Assert a fixed-width value round-tripped without losing its zero pad."""
    return len(str(original).strip()) == len(str(stored)) and str(original).strip() == str(stored)


def panna_to_ank(panna: Any) -> int:
    """Jodi arithmetic: the single digit is the panel's digit sum mod 10."""
    text = validate_result_value(panna, "panna")
    return int(sum(int(c) for c in text) % 10)


def anks_to_jodi(open_ank: Any, close_ank: Any) -> str:
    o = validate_result_value(open_ank, "ank")
    c = validate_result_value(close_ank, "ank")
    return f"{o}{c}"


# ---------------------------------------------------------------------------
# record-set rules
# ---------------------------------------------------------------------------
@dataclass
class QualityIssue:
    check: str
    severity: str  # "error" | "warning" | "info"
    passed: bool
    metric: str
    value: Any
    detail: str = ""


@dataclass
class QualityReport:
    market_id: str
    n_records: int = 0
    issues: list[QualityIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[QualityIssue]:
        return [i for i in self.issues if not i.passed and i.severity == "error"]

    @property
    def warnings(self) -> list[QualityIssue]:
        return [i for i in self.issues if not i.passed and i.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def add(self, check: str, passed: bool, metric: str, value: Any,
            severity: str = "error", detail: str = "") -> None:
        self.issues.append(
            QualityIssue(check=check, severity=severity, passed=bool(passed),
                         metric=metric, value=value, detail=detail)
        )

    def to_rows(self) -> list[dict[str, Any]]:
        return [
            {
                "check_name": i.check,
                "severity": i.severity,
                "passed": int(i.passed),
                "metric_name": i.metric,
                "metric_value": _stringify(i.value),
                "detail": i.detail,
            }
            for i in self.issues
        ]


def _stringify(value: Any) -> str:
    if isinstance(value, (int, float, bool, str)) or value is None:
        return str(value)
    if isinstance(value, (list, tuple)):
        return ",".join(map(str, value))[:500]
    return str(value)[:500]


def find_duplicate_dates(dates: Sequence[Any]) -> list[Any]:
    seen: set[Any] = set()
    dups: set[Any] = set()
    for d in dates:
        if d in seen:
            dups.add(d)
        seen.add(d)
    return sorted(dups)


def validate_chronology(dates: Sequence[Any]) -> bool:
    """True when dates are strictly increasing."""
    return all(a < b for a, b in zip(dates, dates[1:]))


def assert_dataset_isolation(dataset_name: str, verification_status: str | None) -> None:
    """Prevent synthetic control rows from being reported as live market results.

    This is the single most important guard in the repository: the synthetic
    fixtures exist to prove the framework is calibrated, and they must never be
    mistaken for Kalyan or Main Bazar history.
    """
    synthetic = {"synthetic_control", "synthetic"}
    if dataset_name != "live":
        if verification_status not in synthetic:
            raise ValidationError(
                f"dataset '{dataset_name}' rows must carry a synthetic verification status, "
                f"got {verification_status!r}"
            )
    else:
        if verification_status in synthetic:
            raise ValidationError(
                "refusing to store a synthetic-status row in the LIVE dataset tree"
            )


def assert_no_future_information(
    cutoff_index: int,
    used_indices: Iterable[int],
    *,
    context: str = "features",
) -> None:
    """Leakage guard used by the feature builder and the walk-forward engine."""
    bad = [i for i in used_indices if i > cutoff_index]
    if bad:
        raise ValidationError(
            f"future-information leak in {context}: used indices {bad[:5]} "
            f"beyond cutoff {cutoff_index}"
        )


# ---------------------------------------------------------------------------
# probability rules
# ---------------------------------------------------------------------------
def normalise_probabilities(weights: Mapping[Any, float] | Sequence[float]) -> dict[Any, float]:
    values = np.asarray(list(weights.values()) if isinstance(weights, Mapping) else weights, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise ValidationError("probability vector must be a non-empty 1-D sequence")
    if not np.all(np.isfinite(values)):
        raise ValidationError("probability vector contains non-finite values")
    if np.any(values < 0):
        raise ValidationError("probability vector contains negative values")
    total = float(values.sum())
    if total <= 0:
        # Degenerate input: fall back to uniform rather than returning NaNs.
        values = np.full(values.size, 1.0 / values.size)
    else:
        values = values / total
    keys = list(weights.keys()) if isinstance(weights, Mapping) else list(range(values.size))
    return {k: float(v) for k, v in zip(keys, values, strict=True)}


def assert_probability_simplex(probs: Mapping[Any, float], tolerance: float = 1e-9) -> None:
    values = np.asarray(list(probs.values()), dtype=float)
    if np.any(values < -tolerance):
        raise ValidationError("negative probability in distribution")
    if abs(float(values.sum()) - 1.0) > tolerance * max(1, len(values)):
        raise ValidationError(f"probabilities do not sum to 1 (sum={values.sum():.12f})")
