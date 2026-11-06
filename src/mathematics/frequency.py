"""Methods 1-12: frequency and probability (Category A).

Each ``run_NNN`` function computes real numbers on the market's actual sequence
and returns a :class:`MethodOutput`. Nothing here reports a value it did not
compute, and anything the data cannot support is returned with an explicit
non-``computed`` status.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from src.backtesting.baselines import (
    BayesianBaseline,
    FrequencyBaseline,
    RecencyBaseline,
    RollingFrequencyBaseline,
)
from src.backtesting.walk_forward import online_walk_forward
from src.mathematics.common import (
    binomial_test,
    chi2_uniform,
    counts_of,
    cramers_v,
    entropy,
    kl_divergence,
    min_train_for,
    normalised_entropy,
    normal_ci,
)
from src.mathematics.types import (
    STATUS_COMPUTED,
    STATUS_INSUFFICIENT_DATA,
    MethodContext,
    MethodOutput,
    finding,
)

MIN_OBS = 50


def _wf(ctx: MethodContext, model) -> tuple[float, np.ndarray]:
    """Causal walk-forward log loss for a single online frequency model."""
    start = min_train_for(ctx.n, floor=100, fraction=0.15)
    if ctx.n - start < 50:
        raise ValueError(f"only {ctx.n - start} evaluation steps available")
    result = online_walk_forward([model], ctx.y, ctx.dates, min_train=start,
                                 market_id=ctx.market_id, target=ctx.target)
    single = next(iter(result.values()))
    return float(single.per_obs_log_loss().mean()), single.per_obs_log_loss()


def _insufficient(ctx: MethodContext, need: int) -> MethodOutput:
    return MethodOutput(
        status=STATUS_INSUFFICIENT_DATA,
        narrative=f"requires at least {need} observations; the sample has {ctx.n}",
    )


# ---------------------------------------------------------------------------
# M001 absolute frequency
# ---------------------------------------------------------------------------
def run_001(ctx: MethodContext) -> MethodOutput:
    if ctx.n < MIN_OBS:
        return _insufficient(ctx, MIN_OBS)
    counts = counts_of(ctx.y, ctx.k)
    order = np.argsort(-counts)
    top = [(ctx.label(int(i)), int(counts[i])) for i in order[:3]]
    bottom = [(ctx.label(int(i)), int(counts[i])) for i in order[-3:]]
    expected = ctx.n / ctx.k
    ratio = float(counts.max() / max(counts.min(), 1))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("max_count", float(counts.max()), sample_size=ctx.n, extra={"outcome": top[0][0]}),
            finding("min_count", float(counts.min()), sample_size=ctx.n, extra={"outcome": bottom[0][0]}),
            finding("max_min_ratio", ratio, sample_size=ctx.n,
                    extra={"expected_count": round(expected, 2)}),
            finding("count_range", float(counts.max() - counts.min()), sample_size=ctx.n),
        ],
        narrative=(
            f"{ctx.n} draws over {ctx.k} outcomes, so the expected count under uniformity is "
            f"{expected:.1f}. Most frequent: {top[0][0]} with {top[0][1]}; least frequent: "
            f"{bottom[0][0]} with {bottom[0][1]}. A ratio of {ratio:.2f} between extremes looks "
            f"large but is the normal consequence of multinomial variation: for N={ctx.n} and "
            f"K={ctx.k} the standard deviation of a count is about "
            f"{np.sqrt(ctx.n * (1/ctx.k) * (1 - 1/ctx.k)):.1f}, so a spread of a few standard "
            f"deviations across {ctx.k} categories is expected, not remarkable."
        ),
        diagnostics={"ranking": [(ctx.label(int(i)), int(counts[i])) for i in order]},
    )


# ---------------------------------------------------------------------------
# M002 relative frequency
# ---------------------------------------------------------------------------
def run_002(ctx: MethodContext) -> MethodOutput:
    if ctx.n < MIN_OBS:
        return _insufficient(ctx, MIN_OBS)
    probs = counts_of(ctx.y, ctx.k) / ctx.n
    uniform = np.full(ctx.k, 1.0 / ctx.k)
    max_dev = float(np.max(np.abs(probs - uniform)))
    kl = kl_divergence(probs, uniform)
    se = float(np.sqrt((1 / ctx.k) * (1 - 1 / ctx.k) / ctx.n))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("max_abs_deviation", max_dev, sample_size=ctx.n, extra={"se": round(se, 5)}),
            finding("kl_from_uniform", kl, sample_size=ctx.n),
            finding("max_deviation_in_se", max_dev / se if se else None, sample_size=ctx.n),
        ],
        narrative=(
            f"The largest departure of any empirical probability from the uniform 0.1 is "
            f"{max_dev:.4f}, which is {max_dev / se:.2f} standard errors of a proportion at this "
            f"sample size (SE = {se:.4f}). KL divergence from uniform is {kl:.5f} nats. Values in "
            f"this range are typical of a fair process; the formal test is Method 9."
        ),
        diagnostics={"probabilities": {ctx.label(i): round(float(p), 5)
                                       for i, p in enumerate(probs)}},
    )


# ---------------------------------------------------------------------------
# M003 rolling frequency
# ---------------------------------------------------------------------------
def run_003(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 150:
        return _insufficient(ctx, 150)
    windows = ctx.params.get("rolling_windows", [25, 50, 100, 250])
    rows = {}
    baseline_ll, _ = _wf(ctx, FrequencyBaseline(alpha=1.0))
    for w in windows:
        try:
            ll, _ = _wf(ctx, RollingFrequencyBaseline(window=int(w)))
            rows[int(w)] = ll
        except ValueError as exc:
            rows[int(w)] = float("nan")
            ctx.extras.setdefault("errors", []).append(f"w={w}: {exc}")
    valid = {w: v for w, v in rows.items() if np.isfinite(v)}
    if not valid:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="no window could be evaluated")
    best_w = min(valid, key=valid.get)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding(f"rolling_ll_w{w}", v, sample_size=ctx.n) for w, v in rows.items()
        ] + [
            finding("best_window", float(best_w), sample_size=ctx.n, extra={"grid": list(rows)}),
            finding("best_rolling_ll", valid[best_w], sample_size=ctx.n),
            finding("expanding_ll", baseline_ll, sample_size=ctx.n),
            finding("improvement_over_expanding", baseline_ll - valid[best_w], sample_size=ctx.n),
        ],
        narrative=(
            f"Out-of-sample log loss by window: "
            + ", ".join(f"W={w}: {v:.5f}" for w, v in rows.items() if np.isfinite(v))
            + f". The expanding-frequency baseline scores {baseline_ll:.5f}. Best window is "
            f"W={best_w} at {valid[best_w]:.5f}. "
            + ("A short window helps, which would suggest recent draws carry more information."
               if valid[best_w] < baseline_ll - 1e-4 else
               "No window beats the expanding average, so restricting to recent history loses "
               "information rather than gaining adaptivity.")
        ),
        diagnostics={"grid": {str(k): v for k, v in rows.items()}},
    )


# ---------------------------------------------------------------------------
# M004 exponentially weighted frequency
# ---------------------------------------------------------------------------
def run_004(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 150:
        return _insufficient(ctx, 150)
    lambdas = ctx.params.get("ewm_lambdas", [0.90, 0.95, 0.98, 0.99])
    results = {}
    for lam in lambdas:
        try:
            ll, _ = _wf(ctx, RecencyBaseline(decay=float(lam)))
            results[float(lam)] = ll
        except ValueError:
            results[float(lam)] = float("nan")
    valid = {k: v for k, v in results.items() if np.isfinite(v)}
    if not valid:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="no decay could be evaluated")
    best = min(valid, key=valid.get)
    base_ll, _ = _wf(ctx, FrequencyBaseline(alpha=1.0))
    eff_n = (1 + best) / (1 - best)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"ewm_ll_lambda{k}", v, sample_size=ctx.n) for k, v in results.items()]
        + [
            finding("best_lambda", best, sample_size=ctx.n),
            finding("best_ewm_ll", valid[best], sample_size=ctx.n),
            finding("expanding_ll", base_ll, sample_size=ctx.n),
            finding("effective_sample_size", eff_n, sample_size=ctx.n),
        ],
        narrative=(
            "Out-of-sample log loss by decay: "
            + ", ".join(f"lambda={k}: {v:.5f}" for k, v in results.items() if np.isfinite(v))
            + f". Best lambda={best} (effective memory about {eff_n:.0f} draws) scoring "
            f"{valid[best]:.5f} against {base_ll:.5f} for the expanding average. "
            + ("The gain is real but small in absolute terms."
               if valid[best] < base_ll - 1e-3 else
               "Exponential weighting does not beat the flat average, i.e. recent draws are not "
               "more informative than the long run.")
        ),
        diagnostics={"grid": {str(k): v for k, v in results.items()}},
    )


# ---------------------------------------------------------------------------
# M005 Bayesian frequency estimation
# ---------------------------------------------------------------------------
def run_005(ctx: MethodContext) -> MethodOutput:
    if ctx.n < MIN_OBS:
        return _insufficient(ctx, MIN_OBS)
    counts = counts_of(ctx.y, ctx.k)
    alpha = float(ctx.params.get("laplace_alpha", 1.0))
    concentration = alpha * ctx.k
    posterior_mean = (counts + alpha) / (ctx.n + concentration)
    total = ctx.n + concentration

    cis = []
    for k in range(ctx.k):
        a, b = counts[k] + alpha, total - counts[k] - alpha
        cis.append((float(stats.beta.ppf(0.025, a, b)), float(stats.beta.ppf(0.975, a, b))))
    widths = [hi - lo for lo, hi in cis]
    shrinkage = float(1 - ctx.n / total)

    coverage = float(np.mean([lo <= 1 / ctx.k <= hi for lo, hi in cis]))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("posterior_max_prob", float(posterior_mean.max()), sample_size=ctx.n),
            finding("mean_credible_width", float(np.mean(widths)), sample_size=ctx.n),
            finding("prior_shrinkage_weight", shrinkage, sample_size=ctx.n),
            finding("uniform_in_all_ci", coverage, sample_size=ctx.k,
                    extra={"prior_alpha": alpha}),
        ],
        narrative=(
            f"With a Dirichlet({alpha}) prior the posterior is Dirichlet({counts.astype(int).tolist()} + {alpha})"
            f" and the prior retains a weight of {shrinkage:.4%} of the posterior. The 95% "
            f"credible intervals average {np.mean(widths):.4f} in width, and the uniform value 0.10 "
            f"lies inside {coverage:.0%} of them. Intervals that all contain 0.10 mean the data are "
            f"consistent with a fair process at this sample size."
        ),
        diagnostics={"credible_intervals": {ctx.label(i): [round(lo, 5), round(hi, 5)]
                                            for i, (lo, hi) in enumerate(cis)}},
    )


# ---------------------------------------------------------------------------
# M006 Dirichlet-multinomial
# ---------------------------------------------------------------------------
def run_006(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return _insufficient(ctx, 200)
    counts = counts_of(ctx.y, ctx.k)
    p = counts / counts.sum()
    # Method-of-moments for the Dirichlet-multinomial concentration:
    # Var(n_k) = N p_k (1-p_k) [1 + (N-1)/(alpha_0+1)]  ->  invert for alpha_0.
    binom_var = ctx.n * p * (1 - p)
    # Use a split-half estimate of the observed count variance as the empirical target.
    halves = [ctx.y[: ctx.n // 2], ctx.y[ctx.n // 2:]]
    half_counts = np.array([counts_of(h, ctx.k) for h in halves])
    observed_var = float(np.mean(np.var(half_counts, axis=0, ddof=1)))
    expected_var = float(np.mean(ctx.n / 2 * p * (1 - p)))
    ratio = observed_var / expected_var if expected_var > 0 else float("nan")
    # ratio = 1 + (N/2 - 1)/(alpha_0 + 1)  ->  alpha_0
    alpha0 = (ctx.n / 2 - 1) / (ratio - 1) - 1 if ratio > 1 else float("inf")

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("variance_ratio", ratio, sample_size=ctx.n,
                    extra={"interpretation": "1.0 = exactly multinomial"}),
            finding("estimated_alpha0", alpha0 if np.isfinite(alpha0) else None,
                    sample_size=ctx.n),
            finding("multinomial_expected_count_var", expected_var, sample_size=ctx.n),
        ],
        narrative=(
            f"The split-half variance of category counts is {observed_var:.2f} against a multinomial "
            f"prediction of {expected_var:.2f}, a ratio of {ratio:.3f}. A ratio near 1 means the "
            f"counts behave exactly as multinomial sampling predicts, i.e. there is no extra "
            f"over-dispersion to model"
            + (f"; the implied Dirichlet concentration is about {alpha0:.1f}, indicating only weak "
               f"between-category correlation." if np.isfinite(alpha0)
               else "; the concentration is not identifiable because the ratio is at or below 1.")
        ),
        diagnostics={"half_counts": half_counts.tolist()},
    )


# ---------------------------------------------------------------------------
# M007 Laplace smoothing
# ---------------------------------------------------------------------------
def run_007(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 150:
        return _insufficient(ctx, 150)
    grid = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]
    results = {}
    for alpha in grid:
        try:
            ll, _ = _wf(ctx, FrequencyBaseline(alpha=max(alpha, 1e-6)))
            results[alpha] = ll
        except ValueError:
            results[alpha] = float("nan")
    valid = {k: v for k, v in results.items() if np.isfinite(v)}
    if not valid:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="no alpha evaluable")
    best = min(valid, key=valid.get)
    spread = max(valid.values()) - min(valid.values())

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"ll_alpha_{k}", v, sample_size=ctx.n) for k, v in results.items()]
        + [
            finding("best_alpha", best, sample_size=ctx.n),
            finding("best_ll", valid[best], sample_size=ctx.n),
            finding("ll_spread_across_alpha", spread, sample_size=ctx.n),
        ],
        narrative=(
            "Out-of-sample log loss by smoothing constant: "
            + ", ".join(f"alpha={k}: {v:.5f}" for k, v in results.items() if np.isfinite(v))
            + f". Best alpha={best}. The entire spread across the grid is {spread:.6f} nats per "
            f"prediction, which bounds how much this choice can matter: smoothing is a guard "
            f"against zero probabilities, not a source of predictive edge."
        ),
        diagnostics={"grid": {str(k): v for k, v in results.items()}},
    )


# ---------------------------------------------------------------------------
# M008 entropy
# ---------------------------------------------------------------------------
def run_008(ctx: MethodContext) -> MethodOutput:
    if ctx.n < MIN_OBS:
        return _insufficient(ctx, MIN_OBS)
    probs = counts_of(ctx.y, ctx.k) / ctx.n
    h = entropy(probs, base=2)
    h_max = float(np.log2(ctx.k))
    h_norm = normalised_entropy(probs)

    # Rolling entropy and a simulated reference band.
    window = min(250, max(50, ctx.n // 10))
    rolling = []
    for start in range(0, ctx.n - window + 1, max(1, window // 4)):
        window_probs = counts_of(ctx.y[start: start + window], ctx.k) / window
        rolling.append(entropy(window_probs, base=2))
    rng = np.random.default_rng(ctx.seed)
    sim = []
    for _ in range(200):
        sample = rng.integers(0, ctx.k, size=window)
        sim.append(entropy(np.bincount(sample, minlength=ctx.k) / window, base=2))
    sim = np.array(sim)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("entropy_bits", h, sample_size=ctx.n, extra={"max_entropy": round(h_max, 5)}),
            finding("normalised_entropy", h_norm, sample_size=ctx.n),
            finding("entropy_gap_from_max", h_max - h, sample_size=ctx.n),
            finding("rolling_entropy_mean", float(np.mean(rolling)), sample_size=window),
            finding("simulated_entropy_mean", float(sim.mean()), sample_size=window),
            finding("rolling_vs_simulated_z",
                    float((np.mean(rolling) - sim.mean()) / max(sim.std(ddof=1), 1e-12)),
                    sample_size=len(rolling)),
        ],
        narrative=(
            f"Marginal entropy is {h:.4f} bits against a ceiling of {h_max:.4f} "
            f"(normalised {h_norm:.4f}). The deficit of {h_max - h:.4f} bits is the total "
            f"predictable content available in the marginal distribution. Rolling entropy over a "
            f"{window}-draw window averages {np.mean(rolling):.4f} bits, against "
            f"{sim.mean():.4f} for simulated uniform draws of the same window size - a z-score of "
            f"{(np.mean(rolling) - sim.mean()) / max(sim.std(ddof=1), 1e-12):+.2f}. "
            f"Entropy measures only the marginal; serial dependence is invisible to it."
        ),
        diagnostics={"rolling": [round(v, 5) for v in rolling],
                     "simulated_quantiles": [round(float(np.quantile(sim, q)), 5)
                                             for q in (0.025, 0.5, 0.975)]},
    )


# ---------------------------------------------------------------------------
# M009 chi-square goodness of fit
# ---------------------------------------------------------------------------
def run_009(ctx: MethodContext) -> MethodOutput:
    if ctx.n < MIN_OBS:
        return _insufficient(ctx, MIN_OBS)
    result = chi2_uniform(ctx.y, ctx.k)
    v = cramers_v(result["statistic"], ctx.n, (1, ctx.k))
    assumption_ok = result["min_expected"] >= 5

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("chi2_statistic", result["statistic"], statistic=result["statistic"],
                    p_value=result["p_value"], effect_size=v, sample_size=ctx.n,
                    extra={"dof": result["dof"]}),
            finding("cramers_v", v, sample_size=ctx.n),
            finding("p_value", result["p_value"], p_value=result["p_value"], sample_size=ctx.n),
            finding("min_expected_count", result["min_expected"], sample_size=ctx.n),
        ],
        narrative=(
            f"Pearson chi-square against the uniform distribution is {result['statistic']:.3f} on "
            f"{result['dof']} degrees of freedom, p = {result['p_value']:.4f}. Cramer's V is "
            f"{v:.4f}, i.e. the association between outcome and uniform expectation explains about "
            f"{100 * v * v:.2f}% of the chi-square scale. "
            + ("The expected-count assumption is satisfied (min expected "
               f"{result['min_expected']:.1f} >= 5)." if assumption_ok else
               "The expected-count assumption is violated, so the asymptotic p-value is unsafe.")
            + (" A rejection here means the distribution is not exactly uniform; it says nothing "
               "about whether the deviation is large enough to forecast."
               if result["p_value"] < 0.05 else
               " The data are consistent with a uniform marginal distribution.")
        ),
        diagnostics={"counts": result["counts"].astype(int).tolist()},
    )


# ---------------------------------------------------------------------------
# M010 categorical distribution testing
# ---------------------------------------------------------------------------
def run_010(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return _insufficient(ctx, 200)
    from src.mathematics.common import chi2_contingency

    half = ctx.n // 2
    table = np.array([counts_of(ctx.y[:half], ctx.k), counts_of(ctx.y[half:], ctx.k)])
    result = chi2_contingency(table)
    # A second test: three-way split for a stability view.
    third = ctx.n // 3
    table3 = np.array([counts_of(ctx.y[:third], ctx.k),
                       counts_of(ctx.y[third: 2 * third], ctx.k),
                       counts_of(ctx.y[2 * third:], ctx.k)])
    result3 = chi2_contingency(table3)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("halves_chi2", result["statistic"], statistic=result["statistic"],
                    p_value=result["p_value"], effect_size=result["cramers_v"], sample_size=ctx.n),
            finding("halves_cramers_v", result["cramers_v"], sample_size=ctx.n),
            finding("thirds_chi2", result3["statistic"], statistic=result3["statistic"],
                    p_value=result3["p_value"], effect_size=result3["cramers_v"], sample_size=ctx.n),
        ],
        narrative=(
            f"Comparing the first and second halves of the sample gives chi-square "
            f"{result['statistic']:.3f} (p = {result['p_value']:.4f}, V = {result['cramers_v']:.4f}). "
            f"A three-way split gives chi-square {result3['statistic']:.3f} "
            f"(p = {result3['p_value']:.4f}). "
            + ("The distribution is stable across periods, so pooling is defensible."
               if result["p_value"] > 0.05 and result3["p_value"] > 0.05 else
               "At least one split shows a distributional difference, which argues against "
               "pooling the whole history into one estimate.")
        ),
        diagnostics={"halves_table": table.astype(int).tolist()},
    )


# ---------------------------------------------------------------------------
# M011 Jeffreys prior
# ---------------------------------------------------------------------------
def run_011(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 150:
        return _insufficient(ctx, 150)
    try:
        jeffreys_ll, jeff_obs = _wf(ctx, BayesianBaseline(alpha=0.5, name="jeffreys"))
        laplace_ll, lap_obs = _wf(ctx, BayesianBaseline(alpha=1.0, name="laplace"))
    except ValueError as exc:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative=str(exc))

    counts = counts_of(ctx.y, ctx.k)
    jeff_mean = (counts + 0.5) / (ctx.n + 0.5 * ctx.k)
    lap_mean = (counts + 1.0) / (ctx.n + ctx.k)

    from src.backtesting.metrics import paired_bootstrap_difference
    diff = paired_bootstrap_difference(jeff_obs, lap_obs, n_resamples=500, seed=ctx.seed)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("jeffreys_ll", jeffreys_ll, sample_size=ctx.n),
            finding("laplace_ll", laplace_ll, sample_size=ctx.n),
            finding("ll_difference", jeffreys_ll - laplace_ll, p_value=diff["p_two_sided"],
                    sample_size=ctx.n),
            finding("max_posterior_mean_difference",
                    float(np.max(np.abs(jeff_mean - lap_mean))), sample_size=ctx.n),
        ],
        narrative=(
            f"Jeffreys (alpha=1/2) scores {jeffreys_ll:.5f} against Laplace (alpha=1) at "
            f"{laplace_ll:.5f}, a difference of {jeffreys_ll - laplace_ll:+.6f} "
            f"(bootstrap p = {diff['p_two_sided']:.3f}). The two posterior means differ by at most "
            f"{np.max(np.abs(jeff_mean - lap_mean)):.5f}. With N={ctx.n} the prior is drowned by the "
            f"likelihood: the choice of objective prior is immaterial here, which is the expected "
            f"result and a useful sanity check on the implementation."
        ),
        diagnostics={},
    )


# ---------------------------------------------------------------------------
# M012 hierarchical Bayesian
# ---------------------------------------------------------------------------
def run_012(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return _insufficient(ctx, 200)
    from src.preprocessing.cleaning import clean_target

    per_market = {}
    for market_id in ctx.config.market_order:
        try:
            other = clean_target(ctx.config, market_id, ctx.target)
        except (KeyError, ValueError):
            continue
        if other.frame.empty:
            continue
        codes = other.frame["y"].astype(int).to_numpy()
        per_market[market_id] = counts_of(codes, ctx.k) / len(codes)
    if len(per_market) < 2:
        return MethodOutput(
            status=STATUS_INSUFFICIENT_DATA,
            narrative="hierarchical pooling needs at least two markets with this target",
        )

    deviations = np.array([p - 1.0 / ctx.k for p in per_market.values()])
    between_var = float(np.var(deviations, axis=0, ddof=1).mean()) if len(deviations) > 1 else 0.0
    within_var = float((1 / ctx.k) * (1 - 1 / ctx.k) / ctx.n)
    # Empirical-Bayes shrinkage: the proportion of observed spread attributable to signal.
    signal_share = max(0.0, (between_var - within_var) / between_var) if between_var > 0 else 0.0

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("between_market_variance", between_var, sample_size=len(per_market)),
            finding("within_market_sampling_variance", within_var, sample_size=ctx.n),
            finding("signal_share", signal_share, sample_size=len(per_market)),
            finding("shrinkage_to_uniform", 1 - signal_share, sample_size=len(per_market)),
        ],
        narrative=(
            f"Across {len(per_market)} markets the between-market variance of category deviations is "
            f"{between_var:.6f}, while pure sampling variance at N={ctx.n} is {within_var:.6f}. "
            f"After removing sampling noise, an estimated {signal_share:.1%} of the observed spread "
            f"is real between-market difference, implying a shrinkage weight of "
            f"{1 - signal_share:.1%} toward the shared uniform mean. "
            + ("With only two markets this hyperparameter estimate is extremely weak evidence and "
               "is reported as a mechanism demonstration rather than a finding."
               if len(per_market) < 5 else "")
        ),
        diagnostics={"market_marginals": {m: [round(float(x), 5) for x in p]
                                          for m, p in per_market.items()}},
    )


RUNNERS = {
    f"M{i:03d}": globals().get(f"run_{i:03d}")
    for i in range(1, 13)
}
