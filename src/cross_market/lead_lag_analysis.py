"""Lead-lag investigation between markets.

For every component pair and every lag in a fixed, pre-declared window, this
module computes a categorical association (Cramer's V), a chi-square test and
mutual information, then corrects across the whole family.

Three disciplines are enforced:

1. **The lag grid is declared before looking.** It is ``-3..+3``; it is not
   expanded because nothing showed up, and it is not narrowed because something
   did.
2. **Availability is checked, not assumed.** A lag-0 foreign value is inadmissible
   for a same-day target because the platform cannot verify publication times.
3. **Association is not causation and not usefulness.** Every surviving hit is
   still handed to the conditional-model stage, which asks the only question that
   matters: does it improve the target market's out-of-sample forecast?
"""

from __future__ import annotations

import numpy as np

from src.core.logging import get_logger
from src.cross_market.market_alignment import Alignment, align, available_at
from src.mathematics.common import chi2_contingency, holm, mutual_information

log = get_logger(__name__)

LAG_GRID = (-3, -2, -1, 0, 1, 2, 3)
COMPONENTS = ("open", "close")


def _association(x: np.ndarray, y: np.ndarray, k: int) -> dict:
    if len(x) < 100:
        return {"cramers_v": None, "p_value": None, "n": len(x), "mi": None}
    table = np.zeros((k, k))
    np.add.at(table, (x, y), 1.0)
    test = chi2_contingency(table)
    return {
        "cramers_v": float(test["cramers_v"]),
        "p_value": float(test["p_value"]),
        "chi2": float(test["statistic"]),
        "n": int(len(x)),
        "mi": float(mutual_information(x, y, k, k)),
        "min_expected": test["min_expected"],
    }


def investigate_pair(config, market_a: str, market_b: str, *,
                     lag_grid: tuple[int, ...] = LAG_GRID,
                     components: tuple[str, ...] = COMPONENTS) -> dict:
    """Full lead-lag sweep for one market pair."""
    rows: list[dict] = []
    alignments: dict[tuple[str, str], Alignment] = {}

    for component_a in components:
        for component_b in components:
            alignment = align(config, market_a, market_b, component_a, component_b)
            if alignment.n_matched < 200:
                log.info("skipping %s.%s vs %s.%s: only %d common dates",
                         market_a, component_a, market_b, component_b, alignment.n_matched)
                continue
            alignments[(component_a, component_b)] = alignment
            a_values = alignment.frame["a"].astype(int).to_numpy()
            b_values = alignment.frame["b"].astype(int).to_numpy()
            k = 10
            for lag in lag_grid:
                if lag == 0:
                    x, y = a_values, b_values
                    n = len(x)
                elif lag > 0:
                    x, y = a_values[:-lag], b_values[lag:]
                    n = len(x)
                else:
                    x, y = a_values[-lag:], b_values[:lag]
                    n = len(x)
                result = _association(x, y, k)
                rows.append({
                    "market_a": market_a, "market_b": market_b,
                    "component_a": component_a, "component_b": component_b,
                    "lag": int(lag), "n_obs": result["n"],
                    # lag > 0: a's value comes first, so the pair tests a -> b.
                    # lag < 0: b's value comes first, so the pair tests b -> a.
                    "direction": (f"{market_a}.{component_a}[t] -> "
                                  f"{market_b}.{component_b}[t+{lag}]"
                                  if lag > 0 else
                                  f"{market_b}.{component_b}[t{lag}] -> "
                                  f"{market_a}.{component_a}[t]"
                                  if lag < 0 else "same date (publication order unknown)"),
                    "admissible_same_day": available_at(alignment, lag),
                    "cramers_v": result["cramers_v"],
                    "chi2": result.get("chi2"),
                    "p_value": result["p_value"],
                    "mutual_information": result["mi"],
                    "min_expected": result.get("min_expected"),
                })

    # A same-date association is admissible only where markets.yaml declares that
    # the leading market's Open is published before the lagging market's Close.
    declared = set(config.cross_open_precedence)
    for row in rows:
        row["admissible_by_declaration"] = bool(
            row["lag"] == 0 and (
                (row["market_a"], row["market_b"]) in declared
                and row["component_a"] == "open" and row["component_b"] == "close"
                or (row["market_b"], row["market_a"]) in declared
                and row["component_b"] == "open" and row["component_a"] == "close"
            ))

    # Holm correction across every test in this pair.
    p_values = [r["p_value"] if r["p_value"] is not None else 1.0 for r in rows]
    adjusted = holm(p_values) if p_values else []
    for row, adj in zip(rows, adjusted, strict=False):
        row["p_adjusted"] = adj
        row["significant_holm"] = bool(adj < 0.05) if adj is not None else False
        row["verdict"] = _verdict(row)

    return {
        "market_a": market_a, "market_b": market_b,
        "n_tests": len(rows),
        "n_significant_holm": sum(1 for r in rows if r.get("significant_holm")),
        "best_association": max(
            (r for r in rows if r["cramers_v"] is not None),
            key=lambda r: r["cramers_v"], default=None),
        "alignments": {f"{a}_{b}": al.summary() for (a, b), al in alignments.items()},
        "tests": rows,
    }


def _verdict(row: dict) -> str:
    if row["p_value"] is None:
        return "insufficient overlap"
    if not row.get("significant_holm"):
        return "no meaningful evidence detected"
    if not row.get("admissible_same_day"):
        if row.get("admissible_by_declaration"):
            leading, lagging = (row["market_a"], row["market_b"]) \
                if row["component_a"] == "open" else (row["market_b"], row["market_a"])
            return (f"statistically supported; the same-date association is admissible ONLY "
                    f"because markets.yaml declares {leading}.open published before "
                    f"{lagging}.close - an assumption, not a verified timestamp")
        return ("statistically supported but chronologically inadmissible "
                "(same-date publication order unknown - leakage risk)")
    if row["cramers_v"] is not None and row["cramers_v"] < 0.05:
        return "statistically supported association, negligible effect size"
    return "statistically supported association (usefulness not yet established)"


def all_pairs(config) -> list[dict]:
    results = []
    for market_a, market_b in config.cross_market_pairs:
        log.info("lead-lag sweep %s vs %s", market_a, market_b)
        results.append(investigate_pair(config, market_a, market_b))
    return results
