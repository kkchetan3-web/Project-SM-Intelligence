"""Time alignment across markets - the precondition for every cross-market claim.

Two markets do not share a calendar. This module joins them on actual result
dates, and - crucially - records *when* each value became available. The
availability rule used throughout:

* a market's **Open** for date ``t`` is available before its own **Close**;
* a foreign market's result for date ``t`` may only be used for a target on date
  ``t`` if that foreign component is published strictly earlier. We cannot verify
  publication timestamps from historical chart pages, so the conservative default
  is: **only lag-1-or-earlier foreign values are admissible same-day predictors.**

Anything stricter would be a guess dressed up as a feature.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.core.configuration import Config
from src.core.logging import get_logger
from src.preprocessing.cleaning import clean_target

log = get_logger(__name__)

#: Conservative admissibility: a foreign component at lag 0 is only admitted if
#: the configuration asserts it is published earlier (it does not, by default).
DEFAULT_MIN_LAG = 1


@dataclass
class Alignment:
    market_a: str
    market_b: str
    component_a: str
    component_b: str
    frame: pd.DataFrame
    n_matched: int
    n_a_only: int
    n_b_only: int
    n_conflicting_dates: int

    def summary(self) -> dict[str, Any]:
        return {
            "market_a": self.market_a, "market_b": self.market_b,
            "component_a": self.component_a, "component_b": self.component_b,
            "n_matched": self.n_matched, "n_a_only": self.n_a_only,
            "n_b_only": self.n_b_only, "first": self.first_date(), "last": self.last_date(),
        }

    def first_date(self) -> str | None:
        return str(self.frame.index.min().date()) if len(self.frame) else None

    def last_date(self) -> str | None:
        return str(self.frame.index.max().date()) if len(self.frame) else None


def series_for(config: Config, market_id: str, component: str) -> pd.Series:
    result = clean_target(config, market_id, component)
    if result.frame.empty:
        return pd.Series(dtype="Int64")
    return result.frame.set_index("result_date")["y"]


def align(config: Config, market_a: str, market_b: str,
          component_a: str = "open", component_b: str = "open") -> Alignment:
    """Inner-join two markets on shared result dates."""
    a = series_for(config, market_a, component_a)
    b = series_for(config, market_b, component_b)
    if a.empty or b.empty:
        empty = pd.DataFrame(columns=["a", "b"])
        return Alignment(market_a, market_b, component_a, component_b, empty, 0, len(a), len(b), 0)

    frame = pd.concat([a.rename("a"), b.rename("b")], axis=1, join="inner").dropna()
    return Alignment(
        market_a=market_a, market_b=market_b,
        component_a=component_a, component_b=component_b,
        frame=frame, n_matched=len(frame),
        n_a_only=int(len(a.index.difference(b.index))),
        n_b_only=int(len(b.index.difference(a.index))),
        n_conflicting_dates=0,
    )


def lagged_pairs(alignment: Alignment, lag: int) -> tuple[pd.Series, pd.Series, pd.Index]:
    """Pairs ``(a[t], b[t+lag])`` with positive lag meaning b leads a.

    ``lag > 0``  -> ``a[t]`` paired with ``b[t + lag]``: a's value precedes b's,
    so the pair tests whether **a leads b**.
    ``lag < 0``  -> ``a[t]`` paired with ``b[t + lag]`` where ``t + lag < t``:
    b's value precedes a's, so the pair tests whether **b leads a**.

    The returned index is the *target* date, so a caller can check availability
    against it.
    """
    a, b = alignment.frame["a"], alignment.frame["b"]
    if lag == 0:
        return a, b, a.index
    if lag > 0:
        return a.iloc[:-lag], b.iloc[lag:], a.index[:-lag]
    return a.iloc[-lag:], b.iloc[:lag], a.index[-lag:]


def available_at(alignment: Alignment, lag: int, *, conservative: bool = True) -> bool:
    """Whether a foreign value at ``lag`` is guaranteed to precede the target.

    ``lag == 0`` compares two results published on the same date and is
    inadmissible unless the caller can prove one was published first. Any
    non-zero lag is chronologically ordered and therefore admissible: it either
    leads (``lag > 0``: the foreign value is later in time, so it predicts the
    foreign market) or lags (``lag < 0``: the foreign value is earlier, so it may
    predict this one).
    """
    if not conservative:
        return True
    return abs(lag) >= DEFAULT_MIN_LAG


def calendar_diagnostics(alignment: Alignment) -> dict[str, Any]:
    """Coverage and calendar differences that could manufacture correlation."""
    frame = alignment.frame
    if frame.empty:
        return {"n_matched": 0}
    gaps = frame.index.to_series().diff().dt.days.dropna()
    return {
        "n_matched": int(len(frame)),
        "market_a_records": int(alignment.n_a_only + alignment.n_matched),
        "market_b_records": int(alignment.n_b_only + alignment.n_matched),
        "a_only_dates": int(alignment.n_a_only),
        "b_only_dates": int(alignment.n_b_only),
        "matched_span_days": int((frame.index.max() - frame.index.min()).days),
        "mean_gap_days": float(gaps.mean()) if len(gaps) else None,
        "max_gap_days": float(gaps.max()) if len(gaps) else None,
        "weekday_mix": frame.index.dayofweek.value_counts().sort_index().to_dict(),
        "warning": ("substantial calendar mismatch: a shared weekday effect could masquerade as "
                    "cross-market dependence" if max(alignment.n_a_only, alignment.n_b_only)
                    > 0.1 * max(len(frame), 1) else None),
    }
