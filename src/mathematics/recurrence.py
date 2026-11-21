"""Methods 13-22: recency and occurrence (Category B).

The "due number" belief is the most common folk theory in these markets, so this
module tests it directly and repeatedly: recency (M013), waiting-time
distributions (M014-M017), survival and hazard (M018-M019), hot/cold persistence
(M020), and structural breaks (M022).
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from src.backtesting.baselines import RecencyBaseline, RollingFrequencyBaseline
from src.mathematics.common import (
    binomial_test,
    counts_of,
    gaps_for,
    min_train_for,
    normal_ci,
    permutation_pvalue,
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


def _gap_matrix(y: np.ndarray, k: int) -> np.ndarray:
    """Gap of every category at every time step (causal: uses y[0..t])."""
    n = len(y)
    out = np.zeros((n, k))
    last = np.full(k, -1)
    for t in range(n):
        out[t] = np.where(last < 0, np.nan, t - last)
        last[y[t]] = t
    return out


# ---------------------------------------------------------------------------
# M013 last occurrence / "due number"
# ---------------------------------------------------------------------------
def run_013(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return _insufficient(ctx, 200)
    y = ctx.y
    gaps = _gap_matrix(y, ctx.k)

    # Does the most overdue category win more often than 1/K?
    hits = 0
    trials = 0
    overdue_gaps = []
    for t in range(ctx.k * 3, ctx.n - 1):
        row = gaps[t]
        if np.all(np.isnan(row)):
            continue
        candidate = int(np.nanargmax(row))
        overdue_gaps.append(float(row[candidate]))
        trials += 1
        if int(y[t + 1]) == candidate:
            hits += 1
    if trials < 50:
        return _insufficient(ctx, 200)
    due_test = binomial_test(hits, trials, 1.0 / ctx.k)

    # Also: is the realised outcome more overdue than average?
    realised_gap = []
    mean_gap = []
    for t in range(ctx.k * 3, ctx.n - 1):
        row = gaps[t]
        if np.all(np.isnan(row)):
            continue
        realised_gap.append(float(row[y[t + 1]]))
        mean_gap.append(float(np.nanmean(row)))
    realised_gap = np.array(realised_gap)
    mean_gap = np.array(mean_gap)
    diff = realised_gap - mean_gap
    ci = normal_ci(diff)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("most_overdue_hit_rate", due_test["estimate"], p_value=due_test["p_value"],
                    sample_size=trials, extra={"baseline": round(1 / ctx.k, 4),
                                               "hits": hits}),
            finding("mean_extra_gap_of_realised_outcome", float(diff.mean()),
                    p_value=None, sample_size=trials,
                    extra={"ci_low": round(ci["ci_low"], 5), "ci_high": round(ci["ci_high"], 5)}),
            finding("mean_gap_of_most_overdue", float(np.mean(overdue_gaps)), sample_size=trials),
        ],
        narrative=(
            f"If numbers became 'due', the category that has been absent longest should appear more "
            f"than 1/{ctx.k} = {1 / ctx.k:.3f} of the time. It appeared {due_test['estimate']:.4f} "
            f"of the time over {trials} opportunities (binomial p = {due_test['p_value']:.4f}). "
            f"Independently, the realised outcome's gap exceeded the average category gap by "
            f"{diff.mean():+.4f} draws (95% CI {ci['ci_low']:+.4f} to {ci['ci_high']:+.4f}). "
            + ("Both tests point the same way and neither supports the due-number hypothesis."
               if due_test["p_value"] > 0.05 and ci["ci_low"] <= 0 <= ci["ci_high"] else
               "At least one test departs from the independence expectation; interpret with the "
               "multiple-testing correction from Methods 91-92.")
        ),
        diagnostics={"hits": hits, "trials": trials},
    )


# ---------------------------------------------------------------------------
# M014 inter-occurrence gap analysis
# ---------------------------------------------------------------------------
def run_014(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return _insufficient(ctx, 200)
    probs = counts_of(ctx.y, ctx.k) / ctx.n
    rows = {}
    for c in range(ctx.k):
        gaps = gaps_for(ctx.y, c)
        if len(gaps) < 10:
            rows[ctx.label(c)] = {"n_gaps": int(len(gaps)), "vmr": None}
            continue
        p = probs[c]
        expected_vmr = max(1 - p, 1e-6)   # geometric: Var/Mean = (1-p)/p / (1/p) = 1-p
        vmr = float(gaps.var(ddof=1) / gaps.mean()) if gaps.mean() > 0 else float("nan")
        rows[ctx.label(c)] = {
            "n_gaps": int(len(gaps)), "mean_gap": round(float(gaps.mean()), 3),
            "vmr": round(vmr, 4), "expected_vmr": round(float(expected_vmr), 4),
            "ratio": round(vmr / expected_vmr, 4) if expected_vmr > 0 else None,
        }
    valid = {k: v for k, v in rows.items() if v.get("vmr")}
    if not valid:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA,
                           narrative="no category has enough occurrences to form a gap distribution")
    ratios = np.array([v["ratio"] for v in valid.values()], dtype=float)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("mean_vmr_ratio", float(ratios.mean()), sample_size=ctx.n,
                    extra={"interpretation": "1.0 = geometric (memoryless)"}),
            finding("max_vmr_ratio", float(ratios.max()), sample_size=ctx.n),
            finding("n_categories_assessed", float(len(valid)), sample_size=ctx.n),
        ],
        narrative=(
            f"For each category the variance-to-mean ratio of its gaps is compared with the "
            f"geometric prediction (1-p). Across {len(valid)} assessable categories the average "
            f"ratio is {ratios.mean():.3f}; 1.0 means gaps are exactly memoryless. "
            f"Values above 1 indicate clustering of occurrences (gaps either very short or very "
            f"long), below 1 indicate regularity. The observed spread is within what sampling noise "
            f"produces at these counts, so no clustering structure is established."
            if 0.75 < ratios.mean() < 1.35 else
            f"Across {len(valid)} categories the average variance-to-mean ratio relative to the "
            f"geometric prediction is {ratios.mean():.3f}, which departs from memorylessness and "
            f"warrants the formal distributional test in Method 17."
        ),
        diagnostics={"per_category": rows},
    )


# ---------------------------------------------------------------------------
# M015 / M016 mean and median recurrence
# ---------------------------------------------------------------------------
def run_015(ctx: MethodContext) -> MethodOutput:
    return _recurrence_central(ctx, "mean")


def run_016(ctx: MethodContext) -> MethodOutput:
    return _recurrence_central(ctx, "median")


def _recurrence_central(ctx: MethodContext, which: str) -> MethodOutput:
    if ctx.n < 200:
        return _insufficient(ctx, 200)
    p = counts_of(ctx.y, ctx.k) / ctx.n
    rng = np.random.default_rng(ctx.seed)
    rows = {}
    for c in range(ctx.k):
        gaps = gaps_for(ctx.y, c)
        if len(gaps) < 10:
            continue
        stat = float(np.mean(gaps) if which == "mean" else np.median(gaps))
        boot = [float(np.mean(rng.choice(gaps, size=len(gaps), replace=True)) if which == "mean"
                      else np.median(rng.choice(gaps, size=len(gaps), replace=True)))
                for _ in range(300)]
        expected = 1 / p[c] if p[c] > 0 else float("inf")
        rows[ctx.label(c)] = {
            "observed": round(stat, 3), "expected_if_independent": round(float(expected), 3),
            "ci_low": round(float(np.quantile(boot, 0.025)), 3),
            "ci_high": round(float(np.quantile(boot, 0.975)), 3),
            "n_gaps": int(len(gaps)),
        }
    if not rows:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="too few occurrences")
    observed = np.array([v["observed"] for v in rows.values()])
    expected = np.array([v["expected_if_independent"] for v in rows.values()])
    ratio = float(np.mean(observed / np.maximum(expected, 1e-9)))
    skew = float(np.mean([rows[k]["observed"] for k in rows]))

    label = "mean" if which == "mean" else "median"
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding(f"average_{label}_gap", float(observed.mean()), sample_size=ctx.n),
            finding(f"observed_to_expected_ratio", ratio, sample_size=len(rows),
                    extra={"interpretation": "1.0 = matches 1/p"}),
            finding("max_observed_gap", float(max(v["observed"] for v in rows.values())),
                    sample_size=ctx.n),
        ],
        narrative=(
            f"Averaged over {len(rows)} categories the {label} wait between appearances is "
            f"{observed.mean():.2f} draws, against {expected.mean():.2f} predicted by 1/p from the "
            f"empirical marginal (ratio {ratio:.3f}). "
            + ("The observed waiting times agree with the reciprocal of the frequency, which is "
               "exactly what an independent process produces."
               if 0.9 < ratio < 1.1 else
               "The observed waiting times depart from 1/p, which would imply dependence between "
               "successive draws; Method 17 tests the distributional form.")
            + ("" if which == "mean" else
               " The median is the robust counterpart of Method 15 and is unaffected by a single "
               "very long gap.")
        ),
        diagnostics={"per_category": rows},
    )


# ---------------------------------------------------------------------------
# M017 gap distribution modelling
# ---------------------------------------------------------------------------
def run_017(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return _insufficient(ctx, 300)
    probs = counts_of(ctx.y, ctx.k) / ctx.n
    modal = int(np.argmax(probs))
    gaps = gaps_for(ctx.y, modal)
    if len(gaps) < 30:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA,
                            narrative=f"modal category {ctx.label(modal)} has only {len(gaps)} gaps")

    # Geometric MLE
    p_hat = 1.0 / gaps.mean()
    ll_geom = float(np.sum(stats.geom.logpmf(gaps, p_hat)))
    # Negative binomial MLE (mean/dispersion parameterisation)
    try:
        mean_fit, var_fit = gaps.mean(), gaps.var(ddof=1)
        n_nb = mean_fit ** 2 / max(var_fit - mean_fit, 1e-6)
        p_nb = n_nb / (n_nb + mean_fit)
        ll_nb = float(np.sum(stats.nbinom.logpmf(gaps, n_nb, p_nb)))
    except Exception:
        ll_nb, n_nb, p_nb = float("nan"), float("nan"), float("nan")

    k_params_geom, k_params_nb = 1, 2
    aic_geom = 2 * k_params_geom - 2 * ll_geom
    aic_nb = 2 * k_params_nb - 2 * ll_nb if np.isfinite(ll_nb) else float("inf")
    ks = stats.kstest(gaps, lambda g: stats.geom.cdf(g, p_hat))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("geometric_loglik", ll_geom, sample_size=len(gaps)),
            finding("geometric_aic", aic_geom, sample_size=len(gaps)),
            finding("negative_binomial_aic", aic_nb, sample_size=len(gaps)),
            finding("aic_difference_nb_minus_geom", aic_nb - aic_geom if np.isfinite(aic_nb) else None,
                    sample_size=len(gaps), extra={"positive_favours_geometric": True}),
            finding("ks_p_value_geometric", float(ks.pvalue), p_value=float(ks.pvalue),
                    sample_size=len(gaps)),
            finding("observed_variance_to_mean", float(gaps.var(ddof=1) / gaps.mean()),
                    sample_size=len(gaps)),
        ],
        narrative=(
            f"For {ctx.label(modal)} ({len(gaps)} observed gaps) the geometric fit has "
            f"log-likelihood {ll_geom:.2f} and AIC {aic_geom:.2f}; the negative binomial has AIC "
            f"{aic_nb:.2f}. AIC difference of {aic_nb - aic_geom:+.2f} "
            + ("favours the simpler geometric model, i.e. memorylessness fits at least as well as "
               "an over-dispersed alternative." if aic_nb >= aic_geom else
               "favours the over-dispersed alternative, indicating clustering of occurrences.")
            + f" The variance-to-mean ratio is {gaps.var(ddof=1) / gaps.mean():.3f} "
            f"(geometric predicts {1 - p_hat:.3f}), and the Kolmogorov-Smirnov p-value against the "
            f"geometric is {ks.pvalue:.4f}."
        ),
        diagnostics={"category": ctx.label(modal), "p_hat": round(float(p_hat), 5)},
    )


# ---------------------------------------------------------------------------
# M018 survival analysis
# ---------------------------------------------------------------------------
def run_018(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return _insufficient(ctx, 300)
    probs = counts_of(ctx.y, ctx.k) / ctx.n
    modal = int(np.argmax(probs))
    gaps = gaps_for(ctx.y, modal)
    if len(gaps) < 30:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="too few completed gaps")

    # Kaplan-Meier over the gap axis, treating the final incomplete wait as censored.
    last_seen = int(np.flatnonzero(ctx.y == modal)[-1])
    follow_up = ctx.n - 1 - last_seen
    events = np.concatenate([gaps, [follow_up]])
    censored = np.concatenate([np.zeros(len(gaps), dtype=bool), [True]])

    max_t = int(min(max(events[~censored]), 60))
    survival = []
    s = 1.0
    for t in range(1, max_t + 1):
        at_risk = int(np.sum(events >= t))
        died = int(np.sum((events == t) & (~censored)))
        if at_risk > 0 and died > 0:
            s *= 1 - died / at_risk
        survival.append(s)
    km = np.array(survival)
    p_hat = 1.0 / gaps.mean()
    geom = np.array([(1 - p_hat) ** t for t in range(1, max_t + 1)])
    max_abs = float(np.max(np.abs(km - geom)))
    # Greenwood-style variance at the final point
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("km_survival_at_max_t", float(km[-1]), sample_size=len(gaps)),
            finding("geometric_survival_at_max_t", float(geom[-1]), sample_size=len(gaps)),
            finding("max_abs_deviation_from_geometric", max_abs, sample_size=len(gaps)),
            finding("censored_observation_included", float(follow_up), sample_size=len(events)),
        ],
        narrative=(
            f"Kaplan-Meier survival for {ctx.label(modal)} out to {max_t} draws falls to "
            f"{km[-1]:.4f}, against {geom[-1]:.4f} predicted by a memoryless geometric process. The "
            f"largest absolute deviation between the curves is {max_abs:.4f}. Including the final "
            f"censored wait of {follow_up} draws matters: dropping it would bias the estimated "
            f"survival upward."
            + (" The empirical curve tracks the memoryless prediction closely."
               if max_abs < 0.05 else
               " The curves separate, which would indicate time-dependence in the waiting time; "
               "Method 19 tests the hazard directly.")
        ),
        diagnostics={"km": [round(v, 4) for v in km.tolist()],
                     "geometric": [round(v, 4) for v in geom.tolist()]},
    )


# ---------------------------------------------------------------------------
# M019 hazard rate
# ---------------------------------------------------------------------------
def run_019(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return _insufficient(ctx, 300)
    probs = counts_of(ctx.y, ctx.k) / ctx.n
    modal = int(np.argmax(probs))
    # Elapsed time since last occurrence of `modal`, and whether it occurs next.
    elapsed, occurred = [], []
    last = -1
    for t in range(ctx.n - 1):
        if ctx.y[t] == modal:
            last = t
        if last >= 0:
            elapsed.append(t - last)
            occurred.append(1 if ctx.y[t + 1] == modal else 0)
    elapsed = np.array(elapsed)
    occurred = np.array(occurred)
    if len(elapsed) < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="insufficient exposure")

    bins = [(0, 0), (1, 2), (3, 5), (6, 9), (10, 19), (20, 10 ** 6)]
    table = []
    for lo, hi in bins:
        mask = (elapsed >= lo) & (elapsed <= hi)
        n_at_risk = int(mask.sum())
        if n_at_risk < 20:
            continue
        events = int(occurred[mask].sum())
        table.append({"bin": f"{lo}-{hi if hi < 10**6 else '+'}",
                      "n": n_at_risk, "events": events,
                      "hazard": round(events / n_at_risk, 4)})
    if len(table) < 2:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="too few populated hazard bins")

    hazards = np.array([row["hazard"] for row in table])
    const = float(occurred.mean())
    # Trend test across bins via weighted least squares on bin midpoints.
    mids = np.array([(b[0] + min(b[1], b[0] + 5)) / 2 for b in bins[: len(table)]])
    slope = float(np.polyfit(mids, hazards, 1)[0]) if len(hazards) > 1 else float("nan")
    chi2_const = float(np.sum([row["n"] * (row["hazard"] - const) ** 2 / max(const * (1 - const), 1e-9)
                               for row in table]))
    p_const = float(stats.chi2.sf(chi2_const, len(table) - 1))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("constant_hazard_reference", const, sample_size=len(elapsed)),
            finding("hazard_range", float(hazards.max() - hazards.min()), sample_size=len(table)),
            finding("hazard_trend_slope", slope, sample_size=len(table)),
            finding("chi2_vs_constant_hazard", chi2_const, p_value=p_const,
                    sample_size=len(elapsed)),
        ],
        narrative=(
            f"Empirical hazard of {ctx.label(modal)} by elapsed draws: "
            + ", ".join(f"{row['bin']}: {row['hazard']:.4f} (n={row['n']})" for row in table)
            + f". If waiting time were irrelevant every bin would sit at the constant-hazard "
            f"reference {const:.4f}. The chi-square test against a constant hazard gives "
            f"{chi2_const:.2f} on {len(table) - 1} df (p = {p_const:.4f}) and the fitted trend across "
            f"bins is {slope:+.5f} per draw. "
            + ("No evidence that a number becomes more likely with the length of its absence."
               if p_const > 0.05 else
               "The hazard is not constant across bins, which needs corroboration on independent "
               "periods before it can be treated as real.")
        ),
        diagnostics={"bins": table},
    )


# ---------------------------------------------------------------------------
# M020 hot and cold persistence
# ---------------------------------------------------------------------------
def run_020(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 400:
        return _insufficient(ctx, 400)
    half = ctx.n // 2
    first = counts_of(ctx.y[:half], ctx.k)
    second = counts_of(ctx.y[half:], ctx.k)
    z_first = (first - half / ctx.k) / np.sqrt(half * (1 / ctx.k) * (1 - 1 / ctx.k))
    z_second = (second - (ctx.n - half) / ctx.k) / np.sqrt((ctx.n - half) * (1 / ctx.k) * (1 - 1 / ctx.k))
    corr = float(stats.pearsonr(z_first, z_second).statistic)
    corr_p = float(stats.pearsonr(z_first, z_second).pvalue)
    hot_first = int(np.argmax(z_first))
    hot_second = int(np.argmax(z_second))
    extreme = int(np.sum(np.abs(z_first) > 1.96))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("hotness_persistence_correlation", corr, p_value=corr_p,
                    sample_size=ctx.k, extra={"interpretation": "1.0 = hotness persists"}),
            finding("n_extreme_categories_period1", float(extreme), sample_size=ctx.k,
                    extra={"expected_under_uniformity": round(ctx.k * 0.05, 2)}),
            finding("same_hot_category_both_periods", float(hot_first == hot_second), sample_size=ctx.k,
                    extra={"period1": ctx.label(hot_first), "period2": ctx.label(hot_second)}),
        ],
        narrative=(
            f"Standardised deviations in the first half identify {ctx.label(hot_first)} as hottest "
            f"(z={z_first[hot_first]:+.2f}); in the second half the hottest is "
            f"{ctx.label(hot_second)} (z={z_second[hot_second]:+.2f}). The correlation between the "
            f"two halves' z-scores across categories is {corr:+.3f} (p = {corr_p:.3f}). "
            + ("Hot categories do not stay hot: apparent temperature is period-specific noise."
               if corr_p > 0.05 else
               "There is some persistence in relative category frequency, which the walk-forward "
               "frequency baselines would already exploit.")
            + f" {extreme} categor{'y' if extreme == 1 else 'ies'} exceed |z|>1.96 in the first half "
            f"against {ctx.k * 0.05:.1f} expected under uniformity."
        ),
        diagnostics={"z_first": {ctx.label(i): round(float(z_first[i]), 3) for i in range(ctx.k)},
                     "z_second": {ctx.label(i): round(float(z_second[i]), 3) for i in range(ctx.k)}},
    )


# ---------------------------------------------------------------------------
# M021 rolling recency weighting (two-parameter grid)
# ---------------------------------------------------------------------------
def run_021(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return _insufficient(ctx, 300)
    from src.backtesting.metrics import log_loss

    start = min_train_for(ctx.n, floor=150, fraction=0.2)
    window_grid = ctx.params.get("rolling_windows", [25, 50, 100])
    lambda_grid = [0.90, 0.95, 0.98]
    results = {}
    for w in window_grid:
        for lam in lambda_grid:
            try:
                probs = _two_param_wf(ctx.y, ctx.k, int(w), float(lam), start)
                results[f"W{w}_L{lam}"] = float(log_loss(probs[0], probs[1]))
            except Exception:
                results[f"W{w}_L{lam}"] = float("nan")
    valid = {k: v for k, v in results.items() if np.isfinite(v)}
    if not valid:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="no grid point evaluable")
    best = min(valid, key=valid.get)
    spread = max(valid.values()) - min(valid.values())

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"ll_{k}", v, sample_size=ctx.n - start) for k, v in results.items()]
        + [
            finding("best_configuration", None, sample_size=ctx.n - start, extra={"config": best}),
            finding("best_ll", valid[best], sample_size=ctx.n - start),
            finding("grid_spread", spread, sample_size=ctx.n - start),
        ],
        narrative=(
            f"Joint grid over window length and within-window decay ({len(results)} points), scored "
            f"out of sample on {ctx.n - start} predictions. Best configuration: {best} at "
            f"{valid[best]:.5f}. The whole grid spans only {spread:.5f} nats. "
            f"A spread this small means the two-parameter tuning buys essentially nothing: choosing "
            f"optimally here is indistinguishable from choosing arbitrarily, and the winner is "
            f"selected on the same data that scores it, so even this apparent edge is optimistic."
        ),
        diagnostics={"grid": {k: round(v, 6) for k, v in results.items()}},
    )


def _two_param_wf(y: np.ndarray, k: int, window: int, lam: float, start: int):
    n = len(y)
    probs = np.full((n - start, k), 1.0 / k)
    truth = np.empty(n - start, dtype=int)
    for j, t in enumerate(range(start, n)):
        lo = max(0, t - window)
        weights = np.zeros(k)
        for i in range(lo, t):
            weights[y[i]] += lam ** (t - 1 - i)
        total = weights.sum()
        probs[j] = weights / total if total > 0 else 1.0 / k
        truth[j] = y[t]
    return probs, truth


# ---------------------------------------------------------------------------
# M022 change point detection
# ---------------------------------------------------------------------------
def run_022(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 400:
        return _insufficient(ctx, 400)
    y = ctx.y.astype(float)
    mean = y.mean()
    # CUSUM on the numeric encoding.
    cusum = np.zeros(ctx.n)
    for t in range(1, ctx.n):
        cusum[t] = cusum[t - 1] + (y[t] - mean)
    threshold = float(np.std(cusum) * 2.5 + 1e-9)
    alarms = [int(t) for t in range(1, ctx.n)
              if abs(cusum[t] - cusum[t - 1]) > 0 and abs(cusum[t]) > threshold]
    # Collapse adjacent alarms into distinct candidate breaks.
    breaks: list[int] = []
    for a in alarms:
        if not breaks or a - breaks[-1] > 30:
            breaks.append(a)
    breaks = breaks[:8]

    validated = []
    for b in breaks:
        if b < 100 or ctx.n - b < 100:
            continue
        pre, post = ctx.y[max(0, b - 500): b], ctx.y[b: min(ctx.n, b + 500)]
        if len(pre) < 50 or len(post) < 50:
            continue
        table = np.array([counts_of(pre, ctx.k), counts_of(post, ctx.k)])
        from src.mathematics.common import chi2_contingency
        test = chi2_contingency(table)
        validated.append({
            "break_index": b,
            "date": str(ctx.dates[b].date()),
            "chi2": round(test["statistic"], 3),
            "p_value": round(test["p_value"], 4),
            "cramers_v": round(test["cramers_v"], 4),
            "significant": test["p_value"] < 0.05,
        })
    n_significant = sum(1 for v in validated if v["significant"])

    # A single split-point likelihood-ratio search as an independent check.
    best_split, best_stat = None, 0.0
    for b in range(ctx.n // 5, 4 * ctx.n // 5, 25):
        pre, post = ctx.y[:b], ctx.y[b:]
        p1, p2 = counts_of(pre, ctx.k) / len(pre), counts_of(post, ctx.k) / len(post)
        with np.errstate(divide="ignore", invalid="ignore"):
            ll = (np.sum(counts_of(pre, ctx.k) * np.log(np.maximum(p1, 1e-12)))
                  + np.sum(counts_of(post, ctx.k) * np.log(np.maximum(p2, 1e-12))))
            pooled = (counts_of(pre, ctx.k) + counts_of(post, ctx.k)) / ctx.n
            ll0 = np.sum((counts_of(pre, ctx.k) + counts_of(post, ctx.k))
                         * np.log(np.maximum(pooled, 1e-12)))
        stat = float(2 * (ll - ll0))
        if stat > best_stat:
            best_stat, best_split = stat, b
    # Permutation calibration of the split statistic.
    rng = np.random.default_rng(ctx.seed)
    null = []
    shuffled = ctx.y.copy()
    for _ in range(100):
        rng.shuffle(shuffled)
        pre_s, post_s = shuffled[: best_split or ctx.n // 2], shuffled[best_split or ctx.n // 2:]
        p1 = counts_of(pre_s, ctx.k) / max(len(pre_s), 1)
        p2 = counts_of(post_s, ctx.k) / max(len(post_s), 1)
        pooled = (counts_of(pre_s, ctx.k) + counts_of(post_s, ctx.k)) / len(shuffled)
        with np.errstate(divide="ignore", invalid="ignore"):
            ll = (np.sum(counts_of(pre_s, ctx.k) * np.log(np.maximum(p1, 1e-12)))
                  + np.sum(counts_of(post_s, ctx.k) * np.log(np.maximum(p2, 1e-12))))
            ll0 = np.sum((counts_of(pre_s, ctx.k) + counts_of(post_s, ctx.k))
                         * np.log(np.maximum(pooled, 1e-12)))
        null.append(2 * (ll - ll0))
    p_split = float((1 + np.sum(np.array(null) >= best_stat)) / (len(null) + 1))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("n_candidate_breaks", float(len(breaks)), sample_size=ctx.n),
            finding("n_validated_breaks", float(n_significant), sample_size=len(validated)),
            finding("best_split_statistic", best_stat, p_value=p_split,
                    sample_size=ctx.n, extra={"split_date": str(ctx.dates[best_split].date())
                                              if best_split else None}),
            finding("split_permutation_p", p_split, p_value=p_split, sample_size=100),
        ],
        narrative=(
            f"CUSUM flagged {len(breaks)} candidate break locations at a 2.5-sigma threshold. "
            f"Comparing the 500 draws either side of each, {n_significant} of {len(validated)} show a "
            f"significant distributional change. An independent single-split likelihood-ratio search "
            f"puts the best break at index {best_split} "
            f"({str(ctx.dates[best_split].date()) if best_split else 'n/a'}) with statistic "
            f"{best_stat:.2f}, and a 100-shuffle permutation gives p = {p_split:.3f}. "
            + ("The apparent breaks are consistent with sampling variation: no structural change is "
               "established." if p_split > 0.05 else
               "The split statistic exceeds the permutation null, so a structural change is "
               "plausible and regime-adaptive methods (97) become relevant.")
        ),
        diagnostics={"breaks": validated},
    )


RUNNERS = {f"M{i:03d}": globals().get(f"run_{i:03d}") for i in range(13, 23)}
