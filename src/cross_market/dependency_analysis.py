"""Distributional and structural dependency between markets.

Association between individual draws (``lead_lag_analysis``) is only one kind of
dependency. Two markets can also share a *distribution*, a *drift*, a *calendar
effect*, or a *structural break* without any draw-level coupling. All four are
tested here, because any of them would change how the markets should be modelled -
and none of them would be caught by a lag sweep.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from src.core.logging import get_logger
from src.cross_market.market_alignment import align
from src.mathematics.common import chi2_contingency, counts_of, holm, mutual_information

log = get_logger(__name__)


def distribution_similarity(config, market_a: str, market_b: str,
                            component: str = "open") -> dict:
    """Are the two markets' marginal distributions the same?"""
    alignment = align(config, market_a, market_b, component, component)
    if alignment.n_matched < 200:
        return {"available": False, "n_matched": alignment.n_matched}
    a = alignment.frame["a"].astype(int).to_numpy()
    b = alignment.frame["b"].astype(int).to_numpy()
    table = np.array([counts_of(a, 10), counts_of(b, 10)])
    test = chi2_contingency(table)
    return {
        "available": True, "component": component, "n_matched": int(len(a)),
        "chi2": test["statistic"], "p_value": test["p_value"],
        "cramers_v": test["cramers_v"],
        "max_probability_difference": float(
            np.max(np.abs(counts_of(a, 10) / len(a) - counts_of(b, 10) / len(b)))),
        "interpretation": ("distributions are statistically indistinguishable"
                           if test["p_value"] > 0.05 else
                           "distributions differ; the markets are not interchangeable"),
    }


def shared_calendar_effects(config, market_a: str, market_b: str,
                            component: str = "open") -> dict:
    """Do both markets respond to the same calendar partition?"""
    alignment = align(config, market_a, market_b, component, component)
    if alignment.n_matched < 200:
        return {"available": False}
    results = {}
    for name, keys in (("weekday", alignment.frame.index.dayofweek),
                       ("month", alignment.frame.index.month)):
        levels = sorted(set(keys.tolist()))
        for market in ("a", "b"):
            values = alignment.frame[market].astype(int).to_numpy()
            table = np.array([counts_of(values[keys == lev], 10) for lev in levels])
            results[f"{name}_{market}"] = chi2_contingency(table)["p_value"]
    p_values = list(results.values())
    adjusted = holm(p_values)
    return {
        "available": True,
        "raw_p_values": {k: round(v, 5) for k, v in results.items()},
        "holm_p_values": {k: round(v, 5) for k, v in zip(results, adjusted, strict=True)},
        "both_markets_show_effect": all(
            adjusted[list(results).index(f"{name}_a")] < 0.05
            and adjusted[list(results).index(f"{name}_b")] < 0.05
            for name in ("weekday", "month")
        ),
    }


def shared_change_points(config, market_a: str, market_b: str,
                         component: str = "open") -> dict:
    """Do the two markets break at the same time? Independent CUSUM per market."""
    alignment = align(config, market_a, market_b, component, component)
    if alignment.n_matched < 400:
        return {"available": False}

    def cusum_breaks(values: np.ndarray) -> list[int]:
        centered = values - values.mean()
        path = np.cumsum(centered)
        threshold = 2.5 * np.std(path)
        raw = [i for i in range(1, len(path)) if abs(path[i]) > threshold]
        breaks: list[int] = []
        for r in raw:
            if not breaks or r - breaks[-1] > 30:
                breaks.append(r)
        return breaks[:5]

    breaks_a = cusum_breaks(alignment.frame["a"].astype(float).to_numpy())
    breaks_b = cusum_breaks(alignment.frame["b"].astype(float).to_numpy())
    tolerance = 10
    matched = [
        (a, b) for a in breaks_a for b in breaks_b if abs(a - b) <= tolerance
    ]
    expected_matches = (len(breaks_a) * len(breaks_b) * 2 * tolerance) / max(len(alignment.frame), 1)
    return {
        "available": True,
        "n_breaks_a": len(breaks_a),
        "n_breaks_b": len(breaks_b),
        "n_coincident_within_10": len(matched),
        "expected_coincidences_by_chance": round(float(expected_matches), 3),
        "coincident_pairs": matched,
        "interpretation": ("more coincident breaks than chance would give"
                           if len(matched) > max(expected_matches * 2, 2) else
                           "no evidence that the two markets break together"),
    }


def frequency_correlation(config, market_a: str, market_b: str,
                          component: str = "open") -> dict:
    """Correlation of the two markets' category frequencies over time windows.

    A high correlation here means the markets' *marginals* move together, which is
    a different claim from draw-level coupling and is reported separately.
    """
    alignment = align(config, market_a, market_b, component, component)
    if alignment.n_matched < 400:
        return {"available": False}
    window = max(100, len(alignment.frame) // 20)
    rows = []
    for start in range(0, len(alignment.frame) - window, window):
        chunk = alignment.frame.iloc[start: start + window]
        rows.append((counts_of(chunk["a"].astype(int).to_numpy(), 10) / window,
                     counts_of(chunk["b"].astype(int).to_numpy(), 10) / window))
    if len(rows) < 3:
        return {"available": False}
    a_mat = np.stack([r[0] for r in rows])
    b_mat = np.stack([r[1] for r in rows])
    corr = float(np.corrcoef(a_mat.ravel(), b_mat.ravel())[0, 1])
    rank_corr = float(stats.spearmanr(a_mat.ravel(), b_mat.ravel()).statistic)
    return {
        "available": True, "n_windows": len(rows), "window_size": window,
        "pearson": corr, "spearman": rank_corr,
        "interpretation": ("window-wise marginal frequencies co-move more than independence would "
                           "suggest" if corr > 0.5 else
                           "window-wise marginal frequencies do not co-move"),
    }


def run(config, market_a: str, market_b: str, component: str = "open") -> dict:
    results = {
        "pair": [market_a, market_b], "component": component,
        "distribution_similarity": distribution_similarity(config, market_a, market_b, component),
        "calendar_effects": shared_calendar_effects(config, market_a, market_b, component),
        "change_points": shared_change_points(config, market_a, market_b, component),
        "frequency_correlation": frequency_correlation(config, market_a, market_b, component),
    }
    # Jodi-level coupling as a further check, where both markets publish jodi.
    try:
        jodi_alignment = align(config, market_a, market_b, "jodi", "jodi")
        if jodi_alignment.n_matched >= 200:
            from src.preprocessing.normalization import encode_categorical, support_for

            labels = [str(v) for v in support_for("jodi")]
            a = encode_categorical(jodi_alignment.frame["a"].astype(str).tolist(), labels)
            b = encode_categorical(jodi_alignment.frame["b"].astype(str).tolist(), labels)
            results["jodi_mutual_information"] = {
                "n_matched": int(jodi_alignment.n_matched),
                "mutual_information_bits": float(mutual_information(a, b, 100, 100)),
            }
    except Exception as exc:  # pragma: no cover - jodi not published everywhere
        results["jodi_mutual_information"] = {"available": False, "reason": str(exc)[:120]}
    return results
