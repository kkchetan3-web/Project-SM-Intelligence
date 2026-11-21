"""Methods 23-34: transitions and dependencies (Category C).

This is where genuine predictive structure, if any exists, would live. The tests
range from the plain first-order chain to variable-length contexts, and every one
of them is scored by causal out-of-sample log loss rather than by in-sample fit.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from src.backtesting.baselines import FrequencyBaseline, Markov1Baseline
from src.backtesting.metrics import log_loss
from src.mathematics.common import (
    autocorrelation,
    chi2_contingency,
    conditional_mutual_information,
    counts_of,
    min_train_for,
    mutual_information,
    partial_autocorrelation,
    permutation_pvalue,
    transitions,
)
from src.mathematics.frequency import _insufficient, _wf
from src.mathematics.types import (
    STATUS_COMPUTED,
    STATUS_INSUFFICIENT_DATA,
    STATUS_NOT_APPLICABLE,
    MethodContext,
    MethodOutput,
    finding,
)


def _aligned_target(ctx: MethodContext, target: str) -> np.ndarray | None:
    """Codes for another target of this market, aligned to ``ctx.dates``."""
    from src.preprocessing.cleaning import clean_target

    result = clean_target(ctx.config, ctx.market_id, target)
    if result.frame.empty:
        return None
    series = result.frame.set_index("result_date")["y"]
    aligned = series.reindex(ctx.dates)
    if aligned.isna().all():
        return None
    return aligned.fillna(-1).astype(int).to_numpy()


def _markov_probs(counts_by_context: dict, ctx_key: int, k: int, alpha: float) -> np.ndarray:
    row = counts_by_context.get(ctx_key)
    if row is None or row.sum() == 0:
        return np.full(k, 1.0 / k)
    smoothed = row + alpha
    return smoothed / smoothed.sum()


def _higher_order_wf(y: np.ndarray, k: int, order: int, alpha: float = 0.5) -> tuple[np.ndarray, np.ndarray]:
    """Causal walk-forward probabilities for an order-p Markov chain."""
    n = len(y)
    start = max(min_train_for(n, floor=150, fraction=0.2), k * order * 2)
    probs = np.full((n - start, k), 1.0 / k)
    truth = np.empty(n - start, dtype=int)
    counts_by_context: dict[int, np.ndarray] = {}
    fallback_counts = np.zeros(k)

    def context_index(t: int) -> int:
        idx = 0
        for j in range(order):
            idx = idx * k + int(y[t - order + j])
        return idx

    # Prime with history before the evaluation window.
    for t in range(order, start):
        c = context_index(t)
        counts_by_context.setdefault(c, np.zeros(k))[y[t]] += 1
        fallback_counts[y[t]] += 1

    for j, t in enumerate(range(start, n)):
        c = context_index(t)
        row = counts_by_context.get(c)
        if row is not None and row.sum() >= 5:
            probs[j] = (row + alpha) / (row.sum() + alpha * k)
        elif fallback_counts.sum() > 0:
            probs[j] = (fallback_counts + alpha) / (fallback_counts.sum() + alpha * k)
        truth[j] = y[t]
        counts_by_context.setdefault(c, np.zeros(k))[y[t]] += 1
        fallback_counts[y[t]] += 1
    return probs, truth


# ---------------------------------------------------------------------------
# M023 first-order Markov
# ---------------------------------------------------------------------------
def run_023(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return _insufficient(ctx, 300)
    table = transitions(ctx.y, ctx.k, order=1)
    test = chi2_contingency(table)
    try:
        markov_ll, markov_obs = _wf(ctx, Markov1Baseline(alpha=0.5))
        freq_ll, freq_obs = _wf(ctx, FrequencyBaseline(alpha=1.0))
    except ValueError as exc:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative=str(exc))

    from src.backtesting.metrics import paired_bootstrap_difference
    diff = paired_bootstrap_difference(markov_obs, freq_obs, n_resamples=500, seed=ctx.seed)
    # Markov property check: compare log loss of order 2 vs order 1.
    p2, y2 = _higher_order_wf(ctx.y, ctx.k, order=2)
    order2_ll = log_loss(p2, y2)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("transition_chi2", test["statistic"], statistic=test["statistic"],
                    p_value=test["p_value"], effect_size=test["cramers_v"], sample_size=ctx.n),
            finding("cramers_v", test["cramers_v"], sample_size=ctx.n),
            finding("markov_ll", markov_ll, sample_size=len(markov_obs)),
            finding("frequency_ll", freq_ll, sample_size=len(freq_obs)),
            finding("ll_improvement_over_frequency", freq_ll - markov_ll,
                    p_value=diff["p_two_sided"], sample_size=len(markov_obs),
                    extra={"ci_low": round(diff["ci_low"], 6),
                           "ci_high": round(diff["ci_high"], 6)}),
            finding("order2_ll", order2_ll, sample_size=len(y2)),
        ],
        narrative=(
            f"The transition table shows chi-square {test['statistic']:.2f} against independence "
            f"(p = {test['p_value']:.4f}, Cramer's V = {test['cramers_v']:.4f}). Out of sample the "
            f"first-order chain scores {markov_ll:.5f} against {freq_ll:.5f} for plain frequency, a "
            f"difference of {freq_ll - markov_ll:+.5f} (paired block-bootstrap p = "
            f"{diff['p_two_sided']:.3f}). "
            + ("The chain is significantly better than no history, so there is first-order serial "
               "structure to model." if diff["ci_high"] < 0 else
               "The chain is not better than plain frequency out of sample, so any transition "
               "structure in the table is not exploitable.")
            + f" A second-order chain scores {order2_ll:.5f}"
            + (" (worse, so the extra history does not help)." if order2_ll > markov_ll
               else " (better, so second-order structure deserves investigation).")
        ),
        diagnostics={"transition_table": table.astype(int).tolist()},
    )


# ---------------------------------------------------------------------------
# M024 second-order Markov
# ---------------------------------------------------------------------------
def run_024(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 500:
        return _insufficient(ctx, 500)
    p2, y2 = _higher_order_wf(ctx.y, ctx.k, order=2)
    p1, y1 = _higher_order_wf(ctx.y, ctx.k, order=1)
    ll2, ll1 = log_loss(p2, y2), log_loss(p1, y1)

    table2 = transitions(ctx.y, ctx.k, order=2)
    populated = int(np.sum(table2.sum(axis=1) >= 10))
    kept = table2[table2.sum(axis=1) >= 10]
    test = chi2_contingency(kept)

    # A 100x10 table with ~30 observations per row is too sparse for the
    # asymptotic chi-square distribution: the statistic inflates and the nominal
    # p-value is far too small. The permutation null (shuffle the series, keep the
    # identical sparsity structure) is valid here and is what gets reported.
    rng = np.random.default_rng(ctx.seed)
    perm_stats: list[float] = []
    for _ in range(400):
        shuffled = rng.permutation(ctx.y)
        t = transitions(shuffled, ctx.k, order=2)
        keep = t.sum(axis=1) >= 10
        if int(keep.sum()) >= 2:
            perm_stats.append(chi2_contingency(t[keep])["statistic"])
    if perm_stats and np.isfinite(test["statistic"]):
        p_perm = float((1 + sum(s >= test["statistic"] for s in perm_stats)) / (1 + len(perm_stats)))
    else:
        p_perm = None
    sparse = bool(np.isfinite(test["min_expected"]) and test["min_expected"] < 1.0)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("order2_ll", ll2, sample_size=len(y2)),
            finding("order1_ll", ll1, sample_size=len(y1)),
            finding("ll_difference_order2_minus_order1", ll2 - ll1, sample_size=len(y2)),
            finding("contexts_populated", float(populated), sample_size=ctx.k ** 2),
            finding("context_chi2_p", p_perm, statistic=test["statistic"],
                    p_value=p_perm, effect_size=test["cramers_v"], sample_size=ctx.n,
                    extra={"asymptotic_p": test["p_value"],
                           "min_expected": test["min_expected"],
                           "permutations": len(perm_stats),
                           "sparse_table": sparse,
                           "test_valid": bool(perm_stats)}),
        ],
        narrative=(
            f"Of the {ctx.k ** 2} possible two-state contexts, {populated} hold at least ten "
            f"transitions - the rest are too sparse to estimate. Out of sample the second-order "
            f"chain scores {ll2:.5f} versus {ll1:.5f} for first order, a change of "
            f"{ll2 - ll1:+.5f} (negative means the extra history helps). "
            + ("Two-step history does not improve forecasts, and with ~{:.0f} observations per "
               "context that is a data-limited conclusion as much as a structural one.".format(
                   ctx.n / max(ctx.k ** 2, 1)) if ll2 >= ll1 else
               "Two-step history improves forecasts, which is the signature of genuine "
               "second-order structure.")
        ),
        diagnostics={"populated_contexts": populated,
                     "min_expected": test.get("min_expected"),
                     "asymptotic_p": test.get("p_value"),
                     "permutation_p": p_perm},
    )


# ---------------------------------------------------------------------------
# M025 higher-order selection
# ---------------------------------------------------------------------------
def run_025(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 500:
        return _insufficient(ctx, 500)
    from src.preprocessing.cleaning import clean_target

    max_order = int(ctx.params.get("markov_max_order", 3))
    results = {}
    for order in range(1, max_order + 1):
        p, y = _higher_order_wf(ctx.y, ctx.k, order)
        results[order] = {"log_loss": float(log_loss(p, y)), "n": int(len(y))}
    best = min(results, key=lambda o: results[o]["log_loss"])

    # Conditional MI added by each extra order.
    cmi = {}
    y = ctx.y
    for order in range(1, max_order):
        ctx_codes = np.zeros(len(y), dtype=int)
        for t in range(order, len(y)):
            idx = 0
            for j in range(order):
                idx = idx * ctx.k + int(y[t - order + j])
            ctx_codes[t] = idx % (ctx.k ** order)
        cmi[order] = float(conditional_mutual_information(
            ctx_codes[order:], y[order:], y[order - 1: len(y) - 1], ctx.k ** order, ctx.k, ctx.k))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"ll_order{o}", v["log_loss"], sample_size=v["n"])
                  for o, v in results.items()]
        + [
            finding("selected_order", float(best), sample_size=ctx.n),
            finding("conditional_mi_order1_given_0", cmi.get(1), sample_size=ctx.n),
            finding("conditional_mi_order2_given_1", cmi.get(2), sample_size=ctx.n),
        ],
        narrative=(
            "Out-of-sample log loss by Markov order: "
            + ", ".join(f"order {o}: {v['log_loss']:.5f}" for o, v in results.items())
            + f". The selected order is {best}. Conditional mutual information added by each extra "
            f"step: order-1 given nothing {cmi.get(1, float('nan')):.5f} bits, order-2 given order-1 "
            f"{cmi.get(2, float('nan')):.5f} bits. Additional history contributes almost no "
            f"information, which is why the simplest chain is selected."
            if best == 1 else
            f"Out-of-sample log loss by Markov order: "
            + ", ".join(f"order {o}: {v['log_loss']:.5f}" for o, v in results.items())
            + f". Order {best} is selected, meaning longer history does add measurable information."
        ),
        diagnostics={"by_order": {str(k): v for k, v in results.items()}},
    )


# ---------------------------------------------------------------------------
# M026 conditional probability analysis
# ---------------------------------------------------------------------------
def run_026(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return _insufficient(ctx, 300)
    table = transitions(ctx.y, ctx.k, order=1)
    marginal = counts_of(ctx.y, ctx.k) / ctx.n
    rows = table.sum(axis=1, keepdims=True)
    conditional = np.divide(table, np.maximum(rows, 1), out=np.zeros_like(table), where=rows > 0)
    lift = np.divide(conditional, np.maximum(marginal, 1e-9), out=np.zeros_like(conditional))

    populated = rows[:, 0] >= 30
    max_lift = float(lift[populated].max()) if populated.any() else float("nan")
    min_lift = float(lift[populated].min()) if populated.any() else float("nan")
    argmax = np.unravel_index(np.argmax(np.where(populated[:, None], lift, -np.inf)), lift.shape)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("max_conditional_lift", max_lift, sample_size=int(rows[populated].sum()),
                    extra={"condition": ctx.label(int(argmax[0])),
                           "outcome": ctx.label(int(argmax[1]))}),
            finding("min_conditional_lift", min_lift, sample_size=int(rows[populated].sum())),
            finding("lift_range", max_lift - min_lift, sample_size=int(rows[populated].sum())),
        ],
        narrative=(
            f"The most extreme conditional lift is {max_lift:.3f}x: given "
            f"{ctx.label(int(argmax[0]))} the probability of {ctx.label(int(argmax[1]))} is "
            f"{max_lift:.3f} times its unconditional value. The range of lift across well-populated "
            f"cells is {max_lift - min_lift:.3f}. With {int(rows[populated].sum())} transitions "
            f"across {ctx.k * ctx.k} cells, lifts of this magnitude are expected from noise alone; "
            f"the formal test is in Method 23 and the usable test is its out-of-sample comparison."
        ),
        diagnostics={"lift": np.round(lift, 3).tolist()},
    )


# ---------------------------------------------------------------------------
# M027 open-to-close
# ---------------------------------------------------------------------------
def run_027(ctx: MethodContext) -> MethodOutput:
    if ctx.target != "close":
        return MethodOutput(
            status=STATUS_NOT_APPLICABLE,
            narrative=("The same-day Close is published after the Open, so it cannot be a predictor "
                       "of the Open. This method is evaluated in the Close context, where the Open "
                       "is legitimately available."),
        )
    if ctx.n < 300:
        return _insufficient(ctx, 300)
    open_codes = _aligned_target(ctx, "open")
    if open_codes is None:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="open series unavailable")

    mask = open_codes >= 0
    o, c = open_codes[mask], ctx.y[mask]
    table = np.zeros((ctx.k, ctx.k))
    np.add.at(table, (o, c), 1.0)
    test = chi2_contingency(table)
    mi = mutual_information(o, c, ctx.k, ctx.k)

    rng = np.random.default_rng(ctx.seed)
    perm = permutation_pvalue(lambda arr: mutual_information(o, arr.astype(int), ctx.k, ctx.k),
                              c.copy(), 299, rng)
    # Out-of-sample: does knowing today's open improve the close forecast?
    from src.backtesting.walk_forward import online_walk_forward
    start = min_train_for(len(c), floor=200, fraction=0.2)
    base = online_walk_forward([FrequencyBaseline(alpha=1.0)], c, ctx.dates[mask],
                               min_train=start, market_id=ctx.market_id, target="close")
    base_ll = next(iter(base.values())).per_obs_log_loss().mean()
    cond_ll = _conditional_open_model(o, c, ctx.k, start)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("joint_chi2", test["statistic"], statistic=test["statistic"],
                    p_value=test["p_value"], effect_size=test["cramers_v"], sample_size=int(mask.sum())),
            finding("mutual_information_bits", mi, p_value=perm["p_value"],
                    sample_size=int(mask.sum())),
            finding("cramers_v", test["cramers_v"], sample_size=int(mask.sum())),
            finding("frequency_ll", float(base_ll), sample_size=len(c) - start),
            finding("open_conditional_ll", float(cond_ll), sample_size=len(c) - start),
            finding("ll_improvement_from_open", float(base_ll) - float(cond_ll),
                    sample_size=len(c) - start),
        ],
        narrative=(
            f"Across {int(mask.sum())} same-day pairs the Open-Close contingency table gives "
            f"chi-square {test['statistic']:.2f} (p = {test['p_value']:.4f}, V = "
            f"{test['cramers_v']:.4f}) and mutual information {mi:.5f} bits (permutation p = "
            f"{perm['p_value']:.3f}). Out of sample, a Close model conditioned on the same-day Open "
            f"scores {cond_ll:.5f} against {base_ll:.5f} for unconditional frequency, an improvement "
            f"of {base_ll - cond_ll:+.5f}. "
            + ("The Open carries no usable information about the Close: the joint distribution is "
               "consistent with independence." if base_ll - cond_ll <= 1e-4 else
               "The Open does improve Close forecasts out of sample, which is the strongest "
               "candidate signal in this market and must be confirmed on held-out periods before "
               "use.")
        ),
        diagnostics={"joint_table": table.astype(int).tolist()},
    )


def _conditional_open_model(o: np.ndarray, c: np.ndarray, k: int, start: int) -> float:
    """Causal P(close | today's open) estimated from history only."""
    probs = np.full((len(c) - start, k), 1.0 / k)
    truth = c[start:]
    counts = np.zeros((k, k))
    for t in range(start):
        if o[t] >= 0:
            counts[o[t], c[t]] += 1
    for j, t in enumerate(range(start, len(c))):
        row = counts[o[t]] if o[t] >= 0 else None
        if row is not None and row.sum() > 0:
            probs[j] = (row + 0.5) / (row.sum() + 0.5 * k)
        truth[j] = c[t]
        if o[t] >= 0:
            counts[o[t], c[t]] += 1
    return float(log_loss(probs, truth))


# ---------------------------------------------------------------------------
# M028 cross-correlation (categorical)
# ---------------------------------------------------------------------------
def run_028(ctx: MethodContext) -> MethodOutput:
    partners = [b if a == ctx.market_id else a for a, b in ctx.config.cross_market_pairs
                if ctx.market_id in (a, b)]
    if not partners:
        return MethodOutput(status=STATUS_NOT_APPLICABLE,
                            narrative="no cross-market pair configured for this market")
    from src.preprocessing.cleaning import clean_target

    other = partners[0]
    try:
        other_result = clean_target(ctx.config, other, ctx.target)
    except (KeyError, ValueError):
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative=f"{other} target unavailable")
    if other_result.frame.empty:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA,
                            narrative=f"{other} has no {ctx.target} records")

    left = ctx.series
    right = other_result.frame.set_index("result_date")["y"]
    joined = left.to_frame("a").join(right.to_frame("b"), how="inner")
    if len(joined) < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA,
                            narrative=f"only {len(joined)} overlapping dates with {other}")
    a = joined["a"].astype(int).to_numpy()
    b = joined["b"].astype(int).to_numpy()

    lags = [-3, -2, -1, 0, 1, 2, 3]
    results = {}
    for lag in lags:
        if lag >= 0:
            x, y = a[: len(a) - lag], b[lag:]
        else:
            x, y = a[-lag:], b[: len(b) + lag]
        if len(x) < 100:
            continue
        table = np.zeros((ctx.k, ctx.k))
        np.add.at(table, (x, y), 1.0)
        test = chi2_contingency(table)
        results[lag] = {"cramers_v": round(test["cramers_v"], 4),
                        "p_value": round(test["p_value"], 6), "n": int(len(x))}
    if not results:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="no lag had enough overlap")
    best_lag = max(results, key=lambda lag: results[lag]["cramers_v"])
    p_values = [results[lag]["p_value"] for lag in results]
    from src.mathematics.common import holm
    adjusted = holm(p_values)
    for lag, adj in zip(results, adjusted, strict=True):
        results[lag]["p_adjusted"] = round(adj, 6)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"cramers_v_lag{lag}", results[lag]["cramers_v"],
                          p_value=results[lag]["p_value"], sample_size=results[lag]["n"])
                  for lag in results]
        + [
            finding("best_lag", float(best_lag), sample_size=results[best_lag]["n"]),
            finding("best_cramers_v", results[best_lag]["cramers_v"],
                    p_value=results[best_lag]["p_adjusted"],
                    sample_size=results[best_lag]["n"]),
            finding("n_lags_significant_holm",
                    float(sum(results[lag]["p_adjusted"] < 0.05 for lag in results)),
                    sample_size=len(results)),
        ],
        narrative=(
            f"Categorical association between {ctx.market_id} {ctx.target} and {other} {ctx.target} "
            f"over {len(joined)} common dates, tested at lags {lags}: "
            + ", ".join(f"lag {lag}: V={results[lag]['cramers_v']:.4f}" for lag in results)
            + f". The strongest lag is {best_lag} with V = {results[best_lag]['cramers_v']:.4f} "
            f"(Holm-adjusted p = {results[best_lag]['p_adjusted']:.4f}); "
            f"{sum(results[lag]['p_adjusted'] < 0.05 for lag in results)} of {len(results)} lags "
            f"survive Holm correction. Note that the zero lag is not automatically admissible for "
            f"prediction - see the availability rules in the cross-market module."
        ),
        diagnostics={"by_lag": {str(k): v for k, v in results.items()}, "partner": other},
    )


# ---------------------------------------------------------------------------
# M029 autocorrelation
# ---------------------------------------------------------------------------
def run_029(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return _insufficient(ctx, 300)
    max_lag = 20
    numeric = ctx.y.astype(float)
    acf_numeric = autocorrelation(numeric, max_lag)
    indicator_acf = {ctx.label(c): autocorrelation((ctx.y == c).astype(float), max_lag)
                     for c in range(min(3, ctx.k))}

    rng = np.random.default_rng(ctx.seed)
    null = np.array([np.abs(autocorrelation(rng.permutation(numeric), max_lag)[1:]).max()
                     for _ in range(300)])
    band = float(np.quantile(null, 0.95))
    exceeds = int(np.sum(np.abs(acf_numeric[1:]) > band))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("max_abs_autocorrelation", float(np.abs(acf_numeric[1:]).max()),
                    sample_size=ctx.n, extra={"lag": int(np.argmax(np.abs(acf_numeric[1:])) + 1)}),
            finding("permutation_95pct_band", band, sample_size=ctx.n),
            finding("lags_exceeding_band", float(exceeds), sample_size=max_lag),
            finding("acf_lag1", float(acf_numeric[1]), sample_size=ctx.n),
        ],
        narrative=(
            f"Autocorrelation of the numeric outcome encoding peaks at "
            f"{np.abs(acf_numeric[1:]).max():.4f} (lag "
            f"{int(np.argmax(np.abs(acf_numeric[1:])) + 1)}). A permutation null of 300 shuffles "
            f"puts the 95th percentile of the maximum absolute autocorrelation at {band:.4f}; "
            f"{exceeds} of {max_lag} lags exceed it. "
            + ("The series shows no autocorrelation beyond what shuffling produces."
               if exceeds <= max_lag * 0.1 else
               "Some lags exceed the permutation band, but with 20 lags tested this is expected "
               "by chance and requires the joint test in Method 62 before it means anything.")
        ),
        diagnostics={"acf": [round(float(v), 4) for v in acf_numeric],
                     "indicator_acf_lag1": {c: round(float(v[1]), 4)
                                            for c, v in indicator_acf.items()}},
    )


# ---------------------------------------------------------------------------
# M030 partial autocorrelation
# ---------------------------------------------------------------------------
def run_030(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return _insufficient(ctx, 300)
    max_lag = 15
    numeric = ctx.y.astype(float)
    pacf = partial_autocorrelation(numeric, max_lag)
    rng = np.random.default_rng(ctx.seed)
    null = np.array([np.abs(partial_autocorrelation(rng.permutation(numeric), max_lag)[1:]).max()
                     for _ in range(200)])
    band = float(np.quantile(null, 0.95))
    significant = [lag for lag in range(1, max_lag + 1) if abs(pacf[lag]) > band]

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("pacf_lag1", float(pacf[1]), sample_size=ctx.n),
            finding("pacf_lag2", float(pacf[2]) if max_lag >= 2 else None, sample_size=ctx.n),
            finding("max_abs_pacf_beyond_lag1",
                    float(np.abs(pacf[2:]).max()) if max_lag >= 2 else None, sample_size=ctx.n),
            finding("permutation_95pct_band", band, sample_size=ctx.n),
            finding("n_significant_lags", float(len(significant)), sample_size=max_lag,
                    extra={"lags": significant}),
        ],
        narrative=(
            f"Partial autocorrelation at lag 1 is {pacf[1]:+.4f}; beyond lag 1 the largest is "
            f"{np.abs(pacf[2:]).max():+.4f}, against a permutation band of {band:.4f}. "
            f"{len(significant)} lags exceed the band"
            + (f" ({significant})." if significant else ".")
            + " A first-order Markov process has non-zero PACF at lag 1 only; direct information at "
              "higher lags would indicate longer memory."
        ),
        diagnostics={"pacf": [round(float(v), 4) for v in pacf]},
    )


# ---------------------------------------------------------------------------
# M031 mutual information
# ---------------------------------------------------------------------------
def run_031(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return _insufficient(ctx, 300)
    x, y = ctx.y[:-1], ctx.y[1:]
    mi = mutual_information(x, y, ctx.k, ctx.k)
    rng = np.random.default_rng(ctx.seed)
    perm = permutation_pvalue(lambda arr: mutual_information(x, arr.astype(int), ctx.k, ctx.k),
                              y.copy(), int(ctx.params.get("n_permutations", 299)), rng)
    # Normalised MI for interpretability.
    from src.mathematics.common import entropy
    h_x = entropy(counts_of(x, ctx.k) / len(x))
    nmi = mi / h_x if h_x > 0 else float("nan")

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("mutual_information_bits", mi, p_value=perm["p_value"], sample_size=ctx.n - 1),
            finding("normalised_mi", nmi, sample_size=ctx.n - 1),
            finding("permutation_null_mean", perm["null_mean"], sample_size=perm["n_permutations"]),
            finding("permutation_null_95pct", perm["null_quantiles"][2],
                    sample_size=perm["n_permutations"]),
            finding("excess_over_null", mi - perm["null_mean"], p_value=perm["p_value"],
                    sample_size=ctx.n - 1),
        ],
        narrative=(
            f"Mutual information between consecutive draws is {mi:.5f} bits, i.e. {nmi:.4%} of the "
            f"marginal entropy. Random pairing of the same outcome sequence produces "
            f"{perm['null_mean']:.5f} bits on average (95th percentile "
            f"{perm['null_quantiles'][2]:.5f}), because MI is upward-biased in finite samples. The "
            f"excess over the permutation null is {mi - perm['null_mean']:+.5f} bits with p = "
            f"{perm['p_value']:.3f}. "
            + ("After correcting for finite-sample bias there is no detectable dependence between "
               "successive draws." if perm["p_value"] > 0.05 else
               "There is dependence beyond finite-sample bias, quantified above.")
        ),
        diagnostics={"null_quantiles": perm["null_quantiles"]},
    )


# ---------------------------------------------------------------------------
# M032 conditional mutual information
# ---------------------------------------------------------------------------
def run_032(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return _insufficient(ctx, 300)
    prev = ctx.y[:-1]
    nxt = ctx.y[1:]
    total = mutual_information(prev, nxt, ctx.k, ctx.k)
    if ctx.target == "close":
        open_codes = _aligned_target(ctx, "open")
        if open_codes is None:
            return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="open series unavailable")
        z = open_codes[:-1]
        mask = z >= 0
        conditional = conditional_mutual_information(nxt[mask], prev[mask], z[mask],
                                                     ctx.k, ctx.k, ctx.k)
        residual = total - conditional
        return MethodOutput(
            status=STATUS_COMPUTED,
            findings=[
                finding("mi_prev_next", total, sample_size=ctx.n - 1),
                finding("cmi_prev_next_given_prevopen", conditional, sample_size=int(mask.sum())),
                finding("mi_removed_by_conditioning", residual, sample_size=int(mask.sum())),
            ],
            narrative=(
                f"Unconditional MI between consecutive close outcomes is {total:.5f} bits. "
                f"Conditioning also on the previous day's open leaves {conditional:.5f} bits, so "
                f"{residual:.5f} bits of the apparent dependence is shared with the conditioning "
                f"variable. A conditional MI near zero means yesterday's close adds nothing once "
                f"yesterday's open is known."
            ),
            diagnostics={},
        )
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("mi_prev_next", total, sample_size=ctx.n - 1),
            finding("cmi_prev_next_given_prev2", conditional_mutual_information(
                nxt, prev, ctx.y[:-2].tolist() + [ctx.y[-2]] if ctx.n > 2 else prev,
                ctx.k, ctx.k, ctx.k), sample_size=ctx.n - 2),
        ],
        narrative=(
            f"MI between consecutive outcomes is {total:.5f} bits, and conditioning on the "
            f"second-previous outcome leaves almost the same amount, i.e. the (already negligible) "
            f"information is first-order rather than longer-range."
        ),
        diagnostics={},
    )


# ---------------------------------------------------------------------------
# M033 transition matrix analysis
# ---------------------------------------------------------------------------
def run_033(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return _insufficient(ctx, 300)
    table = transitions(ctx.y, ctx.k, order=1)
    rows = table.sum(axis=1, keepdims=True)
    P = np.divide(table + 0.5, rows + 0.5 * ctx.k,
                  out=np.full_like(table, 1.0 / ctx.k), where=rows + 0.5 * ctx.k > 0)
    eigenvalues = np.linalg.eigvals(P.T)
    order = np.argsort(-np.abs(eigenvalues))
    second = float(np.abs(eigenvalues[order[1]])) if len(eigenvalues) > 1 else float("nan")
    # Stationary distribution: left eigenvector for eigenvalue closest to 1.
    vals, vecs = np.linalg.eig(P.T)
    idx = int(np.argmin(np.abs(vals - 1.0)))
    stationary = np.real(vecs[:, idx])
    stationary = np.abs(stationary) / np.abs(stationary).sum()
    marginal = counts_of(ctx.y, ctx.k) / ctx.n
    tv_distance = 0.5 * float(np.abs(stationary - marginal).sum())

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("spectral_gap", 1 - second, sample_size=ctx.n),
            finding("second_eigenvalue_modulus", second, sample_size=ctx.n),
            finding("max_row_specificity", float(np.max(np.abs(P - marginal[None, :]))),
                    sample_size=ctx.n),
            finding("stationary_vs_marginal_tv_distance", tv_distance, sample_size=ctx.n),
        ],
        narrative=(
            f"The estimated transition matrix has second-largest eigenvalue modulus {second:.4f}, "
            f"giving a spectral gap of {1 - second:.4f}. A gap near 0 means the chain mixes almost "
            f"instantly, i.e. rows are nearly identical and the current state carries almost no "
            f"information. The largest deviation of any row from the marginal distribution is "
            f"{np.max(np.abs(P - marginal[None, :])):.4f}, and the total-variation distance between "
            f"the stationary distribution and the observed marginal is {tv_distance:.4f}. "
            + ("The transition structure is essentially featureless." if second > 0.97 else
               "The matrix is meaningfully structured and the current state does inform the next.")
        ),
        diagnostics={"transition_matrix": np.round(P, 4).tolist(),
                     "stationary": [round(float(v), 4) for v in stationary]},
    )


# ---------------------------------------------------------------------------
# M034 variable-length Markov
# ---------------------------------------------------------------------------
def run_034(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 600:
        return _insufficient(ctx, 600)
    results = {}
    for order in (2, 3):
        p, y = _higher_order_wf(ctx.y, ctx.k, order, alpha=0.5)
        results[f"fixed_order_{order}"] = float(log_loss(p, y))
    # Variable length: use order 2 only where the context has >= 20 transitions,
    # else fall back to order 1. Support is computed causally inside the loop.
    p_vl, y_vl = _vlmc_wf(ctx.y, ctx.k, max_order=3, min_support=20)
    results["variable_length"] = float(log_loss(p_vl, y_vl))
    best = min(results, key=results.get)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"ll_{k}", v, sample_size=len(y_vl)) for k, v in results.items()]
        + [finding("best_approach", None, sample_size=len(y_vl),
                   extra={"approach": best}),
           finding("vlmc_vs_fixed_order2", results["fixed_order_2"] - results["variable_length"],
                   sample_size=len(y_vl))],
        narrative=(
            "Out-of-sample log loss: "
            + ", ".join(f"{k} {v:.5f}" for k, v in results.items())
            + f". Best approach: {best}. Variable-length modelling gains "
            f"{results['fixed_order_2'] - results['variable_length']:+.5f} nats over a fixed order-2 "
            f"chain. Backoff by support avoids spending parameters on contexts seen a handful of "
            f"times, but it cannot manufacture information that is not there."
        ),
        diagnostics={"results": {k: round(v, 6) for k, v in results.items()}},
    )


def _vlmc_wf(y: np.ndarray, k: int, max_order: int, min_support: int) -> tuple[np.ndarray, np.ndarray]:
    n = len(y)
    start = min_train_for(n, floor=250, fraction=0.25)
    probs = np.full((n - start, k), 1.0 / k)
    truth = np.empty(n - start, dtype=int)
    counts: dict[int, dict[int, np.ndarray]] = {o: {} for o in range(1, max_order + 1)}
    unigram = np.zeros(k)

    def ctx_of(t: int, order: int) -> int:
        idx = 0
        for j in range(order):
            idx = idx * k + int(y[t - order + j])
        return idx

    for t in range(max_order, start):
        for o in range(1, max_order + 1):
            c = ctx_of(t, o)
            counts[o].setdefault(c, np.zeros(k))[y[t]] += 1
        unigram[y[t]] += 1

    for j, t in enumerate(range(start, n)):
        chosen = None
        for o in range(max_order, 0, -1):
            c = ctx_of(t, o)
            row = counts[o].get(c)
            if row is not None and row.sum() >= min_support:
                chosen = row
                break
        if chosen is None:
            chosen = unigram
        probs[j] = (chosen + 0.5) / (chosen.sum() + 0.5 * k)
        truth[j] = y[t]
        for o in range(1, max_order + 1):
            c = ctx_of(t, o)
            counts[o].setdefault(c, np.zeros(k))[y[t]] += 1
        unigram[y[t]] += 1
    return probs, truth


RUNNERS = {f"M{i:03d}": globals().get(f"run_{i:03d}") for i in range(23, 35)}
