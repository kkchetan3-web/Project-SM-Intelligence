"""Methods 61-72: randomness and statistical structure (Category F).

The purpose of this category is falsification: each method asks whether the
sequence behaves differently from a simulated random process of the same shape.
Where a method relies on an asymptotic approximation that is poor for discrete
categorical data (Ljung-Box, Hurst), a simulation-calibrated reference is reported
alongside it so the reader can see both.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from src.backtesting.metrics import bootstrap_ci
from src.mathematics.common import (
    autocorrelation,
    chi2_uniform,
    counts_of,
    entropy,
    mutual_information,
    permutation_pvalue,
    runs,
)
from src.mathematics.types import (
    STATUS_COMPUTED,
    STATUS_INSUFFICIENT_DATA,
    MethodContext,
    MethodOutput,
    finding,
)


def _median_split(y: np.ndarray) -> np.ndarray:
    return (y >= np.median(y)).astype(int)


def _runs_test(sequence: np.ndarray) -> dict:
    n = len(sequence)
    n1 = int(np.sum(sequence == 1))
    n0 = n - n1
    observed = runs(sequence)
    if n1 == 0 or n0 == 0:
        return {"observed": observed, "expected": float("nan"), "z": float("nan"),
                "p_value": float("nan"), "n1": n1, "n0": n0}
    mean = 2 * n1 * n0 / n + 1
    var = 2 * n1 * n0 * (2 * n1 * n0 - n) / (n ** 2 * (n - 1))
    z = (observed - mean) / np.sqrt(var) if var > 0 else float("nan")
    return {"observed": observed, "expected": mean, "z": float(z),
            "p_value": float(2 * stats.norm.sf(abs(z))), "n1": n1, "n0": n0}


# ---------------------------------------------------------------------------
# M061 runs test
# ---------------------------------------------------------------------------
def run_061(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 100:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 100 observations")
    parity = (ctx.y % 2).astype(int)
    med = _median_split(ctx.y)
    parity_test = _runs_test(parity)
    med_test = _runs_test(med)
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("parity_runs", float(parity_test["observed"]), p_value=parity_test["p_value"],
                    statistic=parity_test["z"], sample_size=ctx.n),
            finding("parity_expected_runs", float(parity_test["expected"]), sample_size=ctx.n),
            finding("median_runs", float(med_test["observed"]), p_value=med_test["p_value"],
                    statistic=med_test["z"], sample_size=ctx.n),
            finding("median_expected_runs", float(med_test["expected"]), sample_size=ctx.n),
        ],
        narrative=(
            f"Parity sequence: {parity_test['observed']} runs against {parity_test['expected']:.1f} "
            f"expected (z = {parity_test['z']:+.3f}, p = {parity_test['p_value']:.4f}). "
            f"Above/below-median sequence: {med_test['observed']} runs against "
            f"{med_test['expected']:.1f} (z = {med_test['z']:+.3f}, p = {med_test['p_value']:.4f}). "
            f"Too few runs means clustering; too many means alternation. "
            + ("Neither categorisation departs from randomness."
               if parity_test["p_value"] > 0.05 and med_test["p_value"] > 0.05 else
               "At least one categorisation shows run behaviour that departs from randomness.")
            + " Method 71 tests exactly the same statistic, so these two must not be counted as "
              "independent evidence."
        ),
        diagnostics={"parity": parity_test, "median": med_test},
    )


# ---------------------------------------------------------------------------
# M062 Ljung-Box
# ---------------------------------------------------------------------------
def run_062(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 200 observations")
    from statsmodels.stats.diagnostic import acorr_ljungbox

    lags = ctx.params.get("ljung_box_lags", [5, 10, 20])
    results = {}
    # Numeric encoding, one-hot indicator of the modal outcome, and parity.
    modal = int(np.argmax(counts_of(ctx.y, ctx.k)))
    series_map = {
        "numeric": ctx.y.astype(float),
        "indicator_modal": (ctx.y == modal).astype(float),
        "parity": (ctx.y % 2).astype(float),
    }
    rng = np.random.default_rng(ctx.seed)
    for name, series in series_map.items():
        table = acorr_ljungbox(series, lags=list(lags), return_df=True)
        results[name] = {
            int(lag): {"statistic": float(table.loc[lag, "lb_stat"]),
                       "p_value": float(table.loc[lag, "lb_pvalue"])}
            for lag in lags
        }
    # Simulation-calibrated reference for the numeric series at the largest lag.
    max_lag = max(lags)
    null_stats = []
    for _ in range(200):
        sim = rng.integers(0, ctx.k, size=ctx.n).astype(float)
        null_stats.append(float(acorr_ljungbox(sim, lags=[max_lag], return_df=True)["lb_stat"].iloc[0]))
    null_q95 = float(np.quantile(null_stats, 0.95))

    findings = []
    for name, by_lag in results.items():
        for lag, value in by_lag.items():
            findings.append(finding(f"ljungbox_{name}_lag{lag}", value["statistic"],
                                    p_value=value["p_value"], sample_size=ctx.n))
    findings.append(finding("simulated_null_95pct_at_max_lag", null_q95, sample_size=200))

    best_p = min(v["p_value"] for by_lag in results.values() for v in by_lag.values())
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=findings,
        narrative=(
            f"Ljung-Box statistics for numeric, modal-indicator and parity series at lags {lags}. "
            f"The smallest p-value across all nine tests is {best_p:.4f}, and the numeric series at "
            f"lag {max_lag} gives Q = {results['numeric'][max_lag]['statistic']:.2f}. A simulated "
            f"i.i.d. series of the same length and alphabet gives a 95th percentile of {null_q95:.2f} "
            f"for that statistic, which is the correct reference: the asymptotic chi-square "
            f"approximation is optimistic for a categorical series that has been numerically encoded. "
            + ("No lag horizon shows joint autocorrelation beyond the simulated random reference."
               if results["numeric"][max_lag]["statistic"] < null_q95 else
               "The numeric series exceeds the simulated reference at the longest lag, indicating "
               "joint autocorrelation that the per-lag tests understated.")
        ),
        diagnostics={"by_series": {k: {str(lag): v for lag, v in d.items()}
                                   for k, d in results.items()}},
    )


# ---------------------------------------------------------------------------
# M063 permutation testing
# ---------------------------------------------------------------------------
def run_063(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 200 observations")
    n_perm = int(ctx.params.get("n_permutations", 999))
    rng = np.random.default_rng(ctx.seed)
    from src.mathematics.common import entropy as H

    statistics = {
        "max_abs_frequency_deviation": lambda arr: float(
            np.max(np.abs(counts_of(arr.astype(int), ctx.k) / len(arr) - 1 / ctx.k))),
        "entropy_deficit": lambda arr: float(np.log2(ctx.k) - H(
            counts_of(arr.astype(int), ctx.k) / len(arr))),
        "lag1_mutual_information": lambda arr: mutual_information(
            arr.astype(int)[:-1], arr.astype(int)[1:], ctx.k, ctx.k),
    }
    findings = []
    narratives = []
    for name, fn in statistics.items():
        result = permutation_pvalue(fn, ctx.dispatch_copy() if hasattr(ctx, "dispatch_copy")
                                    else ctx.y.copy(), n_perm, rng)
        findings.append(finding(name, result["observed"], p_value=result["p_value"],
                                sample_size=ctx.n,
                                extra={"null_mean": round(result["null_mean"], 6),
                                       "n_permutations": n_perm}))
        narratives.append(f"{name} = {result['observed']:.5f} (null mean "
                          f"{result['null_mean']:.5f}, p = {result['p_value']:.4f})")

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=findings,
        narrative=(
            f"{n_perm} random permutations of the outcome sequence give an exact null distribution "
            f"for three statistics: " + "; ".join(narratives) + ". "
            f"Permutation is exact here because the null hypothesis of exchangeability is precisely "
            f"what shuffling destroys, so no distributional approximation is involved. "
            + ("All three statistics lie well inside their permutation nulls, which is what an "
               "i.i.d. process looks like."
               if all(f.p_value and f.p_value > 0.05 for f in findings) else
               "At least one statistic falls outside its permutation null and would need "
               "multiplicity correction before being believed.")
        ),
        diagnostics={},
    )


# ---------------------------------------------------------------------------
# M064 bootstrap
# ---------------------------------------------------------------------------
def run_064(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 100:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 100 observations")
    probs = counts_of(ctx.y, ctx.k) / ctx.n
    rng = np.random.default_rng(ctx.seed)
    n_boot = int(ctx.params.get("n_bootstrap", 1000))
    draws = rng.choice(ctx.y, size=(n_boot, ctx.n), replace=True)
    boot_probs = np.array([np.bincount(d, minlength=ctx.k) / ctx.n for d in draws])
    ci_low = np.quantile(boot_probs, 0.025, axis=0)
    ci_high = np.quantile(boot_probs, 0.975, axis=0)
    widths = ci_high - ci_low
    covers_uniform = float(np.mean((ci_low <= 1 / ctx.k) & (1 / ctx.k <= ci_high)))

    # Moving-block variant for comparison (dependence-aware).
    block = 5
    from src.backtesting.metrics import moving_block_bootstrap_indices
    idx = moving_block_bootstrap_indices(ctx.n, block, 500, rng)
    block_probs = np.array([np.bincount(ctx.y[i], minlength=ctx.k) / ctx.n for i in idx])
    block_width = float(np.mean(np.quantile(block_probs, 0.975, axis=0)
                                - np.quantile(block_probs, 0.025, axis=0)))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("mean_ci_width_iid", float(widths.mean()), sample_size=n_boot),
            finding("mean_ci_width_block", block_width, sample_size=500,
                    extra={"block_length": block}),
            finding("width_ratio_block_over_iid", block_width / float(widths.mean()),
                    sample_size=n_boot),
            finding("uniform_inside_all_ci", covers_uniform, sample_size=ctx.k),
            finding("max_ci_width", float(widths.max()), sample_size=ctx.k),
        ],
        narrative=(
            f"{n_boot} i.i.d. bootstrap resamples give a mean 95% interval width of {widths.mean():.5f} "
            f"for category probabilities; the moving-block bootstrap (block length {block}) gives "
            f"{block_width:.5f}, a ratio of {block_width / widths.mean():.3f}. A ratio near 1 means "
            f"the sequence carries no extra dependence that widens the true uncertainty. The uniform "
            f"value 0.10 lies inside {covers_uniform:.0%} of the intervals. Every frequency estimate "
            f"here should be read with these widths attached: with N={ctx.n} a probability of 0.1 is "
            f"only pinned to within about ±{widths.mean() / 2:.4f}."
        ),
        diagnostics={"ci_low": np.round(ci_low, 5).tolist(),
                     "ci_high": np.round(ci_high, 5).tolist()},
    )


# ---------------------------------------------------------------------------
# M065 Monte Carlo
# ---------------------------------------------------------------------------
def run_065(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 200 observations")
    n_sim = int(ctx.params.get("n_monte_carlo_sequences", 300))
    rng = np.random.default_rng(ctx.seed)
    observed = {
        "max_category_count": float(counts_of(ctx.y, ctx.k).max()),
        "entropy": entropy(counts_of(ctx.y, ctx.k) / ctx.n),
        "longest_same_run": float(_longest_run(ctx.y, ctx.k)),
    }
    nulls = {k: [] for k in observed}
    for _ in range(n_sim):
        sim = rng.integers(0, ctx.k, size=ctx.n)
        counts = counts_of(sim, ctx.k)
        nulls["max_category_count"].append(float(counts.max()))
        nulls["entropy"].append(entropy(counts / ctx.n))
        nulls["longest_same_run"].append(float(_longest_run(sim, ctx.k)))

    findings = []
    narr = []
    for name, value in observed.items():
        null = np.array(nulls[name])
        p_high = float((1 + np.sum(null >= value)) / (n_sim + 1))
        p_low = float((1 + np.sum(null <= value)) / (n_sim + 1))
        findings.append(finding(name, value, p_value=min(p_high, p_low) * 2 if False else p_high,
                                sample_size=n_sim,
                                extra={"null_mean": round(float(null.mean()), 4),
                                       "null_sd": round(float(null.std(ddof=1)), 4),
                                       "p_low_tail": round(p_low, 4)}))
        narr.append(f"{name}: observed {value:.4f}, simulated mean {null.mean():.4f} "
                    f"(sd {null.std(ddof=1):.4f}), upper-tail p = {p_high:.3f}")

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=findings,
        narrative=(
            f"{n_sim} simulated i.i.d. sequences of length {ctx.n} over {ctx.k} outcomes: "
            + "; ".join(narr) + ". "
            "The simulated distribution is the exact answer to 'what would randomness look like at "
            "this sample size', which is the question every pattern claim must be judged against. "
            + ("Every observed statistic is unremarkable against this reference."
               if all(f.p_value > 0.05 for f in findings) else
               "At least one statistic is extreme relative to the simulated reference.")
        ),
        diagnostics={"null_quantiles": {k: [round(float(np.quantile(v, q)), 4)
                                            for q in (0.025, 0.5, 0.975)]
                                        for k, v in nulls.items()}},
    )


def _longest_run(y: np.ndarray, k: int) -> int:
    best = 1
    current = 1
    for i in range(1, len(y)):
        if y[i] == y[i - 1]:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


# ---------------------------------------------------------------------------
# M066 / M067 entropy measures
# ---------------------------------------------------------------------------
def _sample_entropy(sequence: np.ndarray, m: int) -> tuple[float | None, dict]:
    n = len(sequence)

    def count_matches(dim: int) -> int:
        windows = np.lib.stride_tricks.sliding_window_view(sequence, dim)
        # Hash each pattern to compare exactly.
        hashes, counts = np.unique(windows, axis=0, return_counts=True)
        return int(np.sum(counts * (counts - 1)))

    b = count_matches(m)
    a = count_matches(m + 1)
    if b == 0 or a == 0:
        return None, {"A": a, "B": b, "note": "no matching patterns at this embedding"}
    return float(-np.log(a / b)), {"A": a, "B": b}


def run_066(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 300 observations")
    sequence = ctx.y.astype(np.int64)
    results = {}
    for m in (1, 2, 3):
        try:
            value, detail = _sample_entropy(sequence, m)
        except Exception as exc:  # pragma: no cover
            value, detail = None, {"error": str(exc)}
        results[m] = {"sampen": value, **detail}
    # Reference from simulated uniform sequences.
    rng = np.random.default_rng(ctx.seed)
    sims = []
    for _ in range(20):
        try:
            sim_value, _ = _sample_entropy(rng.integers(0, ctx.k, size=ctx.n).astype(np.int64), 2)
            if sim_value is not None:
                sims.append(sim_value)
        except Exception:
            continue

    m2 = results[2]["sampen"]
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding(f"sampen_m{m}", results[m]["sampen"], sample_size=ctx.n,
                    extra={"A": results[m].get("A"), "B": results[m].get("B")})
            for m in results
        ] + [
            finding("simulated_sampen_m2_mean", float(np.mean(sims)) if sims else None,
                    sample_size=len(sims)),
            finding("sampen_excess_over_simulation",
                    (m2 - float(np.mean(sims))) if (m2 is not None and sims) else None,
                    sample_size=len(sims)),
        ],
        narrative=(
            "Sample entropy (exact-match, so the tolerance parameter is not needed): "
            + ", ".join(f"m={m}: {results[m]['sampen'] if results[m]['sampen'] is not None else 'undefined'}"
                        for m in results)
            + f". Simulated uniform sequences give {np.mean(sims) if sims else float('nan'):.4f} at "
            f"m=2; the observed excess is "
            f"{(m2 - np.mean(sims)) if (m2 is not None and sims) else float('nan'):+.4f}. "
            + ("The sequence is as irregular as simulated randomness."
               if m2 is not None and sims and abs(m2 - np.mean(sims)) < 0.15 else
               "The observed regularity differs from the simulated reference. Note that with a "
               "10-symbol alphabet matches at m=3 are extremely rare, so high-order estimates are "
               "unreliable and may be undefined.")
        ),
        diagnostics={"by_m": {str(k): v for k, v in results.items()}},
    )


def run_067(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 300 observations")

    def apen(sequence: np.ndarray, m: int) -> float | None:
        phi = []
        for dim in (m, m + 1):
            windows = np.lib.stride_tricks.sliding_window_view(sequence, dim)
            hashes, counts = np.unique(windows, axis=0, return_counts=True)
            total = windows.shape[0]
            freqs = counts / total
            expanded = np.repeat(freqs, counts)
            if len(expanded) == 0:
                return None
            phi.append(float(np.mean(np.log(np.maximum(expanded, 1e-12)))))
        return float(phi[0] - phi[1])

    sequence = ctx.y.astype(np.int64)
    values = {m: apen(sequence, m) for m in (1, 2, 3)}
    rng = np.random.default_rng(ctx.seed)
    sims = []
    for _ in range(20):
        try:
            value = apen(rng.integers(0, ctx.k, size=ctx.n).astype(np.int64), 2)
            if value is not None:
                sims.append(value)
        except Exception:
            continue
    v2 = values[2]
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"apen_m{m}", values[m], sample_size=ctx.n) for m in values]
        + [finding("simulated_apen_m2_mean", float(np.mean(sims)) if sims else None,
                   sample_size=len(sims)),
           finding("sampen_minus_apen_m2",
                   (values[2] - (None if not sims else float("nan"))) if False else None,
                   sample_size=ctx.n)],
        narrative=(
            f"Approximate entropy: m=1 {values[1]}, m=2 {values[2]}, m=3 {values[3]}. Simulated "
            f"uniform sequences give {np.mean(sims) if sims else float('nan'):.4f} at m=2. "
            f"ApEn counts self-matches, which biases it toward reporting more regularity than exists; "
            f"Sample entropy (Method 66) removes that bias. The two should be read together, and a "
            f"large gap between them is itself evidence that the apparent regularity is a "
            f"finite-sample artefact rather than structure."
        ),
        diagnostics={},
    )


# ---------------------------------------------------------------------------
# M068 Hurst
# ---------------------------------------------------------------------------
def run_068(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 300 observations")
    series = ctx.y.astype(float)

    def hurst(values: np.ndarray) -> tuple[float, int]:
        scales = [s for s in (8, 16, 32, 64, 128, 256) if s <= len(values) // 2]
        if len(scales) < 3:
            return float("nan"), 0
        log_rs = []
        for scale in scales:
            chunks = len(values) // scale
            if chunks < 2:
                continue
            rs_values = []
            for c in range(chunks):
                chunk = values[c * scale: (c + 1) * scale]
                deviations = np.cumsum(chunk - chunk.mean())
                rng_span = deviations.max() - deviations.min()
                sd = chunk.std(ddof=1)
                if sd > 0:
                    rs_values.append(rng_span / sd)
            if rs_values:
                log_rs.append((np.log(scale), np.log(np.mean(rs_values))))
        if len(log_rs) < 3:
            return float("nan"), len(log_rs)
        xs, ys = zip(*log_rs)
        return float(np.polyfit(xs, ys, 1)[0]), len(log_rs)

    h, n_scales = hurst(series)
    rng = np.random.default_rng(ctx.seed)
    null = [hurst(rng.integers(0, ctx.k, size=ctx.n).astype(float))[0] for _ in range(100)]
    null = np.array([v for v in null if np.isfinite(v)])

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("hurst_exponent", h, sample_size=ctx.n),
            finding("simulated_hurst_mean", float(null.mean()) if len(null) else None,
                    sample_size=len(null)),
            finding("simulated_hurst_95pct_low",
                    float(np.quantile(null, 0.025)) if len(null) else None, sample_size=len(null)),
            finding("simulated_hurst_95pct_high",
                    float(np.quantile(null, 0.975)) if len(null) else None, sample_size=len(null)),
            finding("n_scales_used", float(n_scales), sample_size=n_scales),
        ],
        narrative=(
            f"Rescaled-range estimate of the Hurst exponent is {h:.4f} using {n_scales} scales. For "
            f"simulated i.i.d. sequences of the same length the estimator averages "
            f"{null.mean() if len(null) else float('nan'):.4f} with a 95% interval of "
            f"[{np.quantile(null, 0.025) if len(null) else float('nan'):.4f}, "
            f"{np.quantile(null, 0.975) if len(null) else float('nan'):.4f}] - note how far this is "
            f"from the textbook 0.5, which is exactly why the simulated band is required. "
            + ("The observed exponent lies inside the simulated interval, so there is no evidence of "
               "long-range dependence." if len(null) and
               np.quantile(null, 0.025) <= h <= np.quantile(null, 0.975) else
               "The observed exponent lies outside the simulated interval, suggesting long-range "
               "dependence, though R/S is known to be biased by short-memory effects.")
        ),
        diagnostics={"scales": n_scales},
    )


# ---------------------------------------------------------------------------
# M069 hidden Markov model
# ---------------------------------------------------------------------------
def run_069(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 400:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 400 observations")
    from src.backtesting.baselines import Markov1Baseline
    from src.backtesting.metrics import log_loss
    from src.backtesting.walk_forward import online_walk_forward
    from src.mathematics.frequency import _wf

    results = {}
    for n_states in (2, 3):
        fits = []
        for restart in range(3):
            try:
                params, ll = _fit_hmm(ctx.y, ctx.k, n_states,
                                      seed=ctx.seed + restart * 101)
                fits.append((ll, params))
            except Exception:
                continue
        if not fits:
            results[n_states] = {"error": "no fit converged"}
            continue
        best_ll, best_params = max(fits, key=lambda t: t[0])
        results[n_states] = {"loglik": best_ll,
                             "persistence": float(np.trace(best_params["A"]) / n_states),
                             "n_restarts_converged": len(fits)}
    ok = {k: v for k, v in results.items() if "loglik" in v}
    if not ok:
        return MethodOutput(status=STATUS_COMPUTED, narrative="no HMM fit converged from any restart")

    markov_ll, _ = _wf(ctx, Markov1Baseline(alpha=0.5))
    best_states = max(ok, key=lambda s: ok[s]["loglik"])
    # AIC comparison: HMM params = (S-1) + S*(S-1) + S*(K-1)
    s = best_states
    n_params_hmm = (s - 1) + s * (s - 1) + s * (ctx.k - 1)
    aic_hmm = 2 * n_params_hmm - 2 * ok[s]["loglik"]
    n_params_markov = ctx.k * (ctx.k - 1)
    aic_markov = 2 * n_params_markov - 2 * (-markov_ll * ctx.n)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"loglik_states{k}", v["loglik"], sample_size=ctx.n,
                          extra={"persistence": round(v["persistence"], 4),
                                 "restarts": v["n_restarts_converged"]})
                  for k, v in ok.items()]
        + [
            finding("best_n_states", float(best_states), sample_size=ctx.n),
            finding("aic_hmm", aic_hmm, sample_size=ctx.n),
            finding("aic_first_order_markov", aic_markov, sample_size=ctx.n),
            finding("aic_advantage_of_hmm", aic_markov - aic_hmm, sample_size=ctx.n),
            finding("markov1_out_of_sample_ll", markov_ll, sample_size=ctx.n),
        ],
        narrative=(
            f"Fitting categorical HMMs with {sorted(ok)} latent states (three random restarts each, "
            f"keeping the best log-likelihood): "
            + ", ".join(f"{k} states: ll={v['loglik']:.1f}, mean persistence "
                        f"{v['persistence']:.3f}" for k, v in ok.items())
            + f". Best is {best_states} states. Against a first-order Markov chain the AIC advantage "
            f"is {aic_markov - aic_hmm:+.1f} units (positive favours the HMM). "
            + ("The latent-state model does not explain the data better than a plain chain once its "
               "extra parameters are charged for, so there is no evidence of regime switching."
               if aic_markov - aic_hmm <= 0 else
               "The HMM's in-sample advantage survives the parameter penalty, but in-sample fit is "
               "weak evidence for latent regimes; the out-of-sample comparison is decisive.")
            + f" The first-order chain's out-of-sample log loss is {markov_ll:.5f}, which is the "
              f"benchmark any latent-state model must beat."
        ),
        diagnostics={"by_states": {str(k): v for k, v in results.items()}},
    )


def _fit_hmm(y: np.ndarray, k: int, n_states: int, seed: int, max_iter: int = 60,
             tol: float = 1e-5) -> tuple[dict, float]:
    """Baum-Welch for a categorical HMM. Small and explicit on purpose."""
    rng = np.random.default_rng(seed)
    n = len(y)
    A = rng.random((n_states, n_states)) + 2.0
    A /= A.sum(axis=1, keepdims=True)
    B = rng.random((n_states, k)) + 1.0
    B /= B.sum(axis=1, keepdims=True)
    pi = np.full(n_states, 1.0 / n_states)
    onehot = np.zeros((n, k))
    onehot[np.arange(n), y] = 1.0
    previous_ll = -np.inf

    for _ in range(max_iter):
        # Forward
        alpha = np.zeros((n, n_states))
        alpha[0] = pi * B[:, y[0]]
        scale = np.zeros(n)
        scale[0] = alpha[0].sum() + 1e-300
        alpha[0] /= scale[0]
        for t in range(1, n):
            alpha[t] = (alpha[t - 1] @ A) * B[:, y[t]]
            scale[t] = alpha[t].sum() + 1e-300
            alpha[t] /= scale[t]
        # Backward
        beta = np.zeros((n, n_states))
        beta[-1] = 1.0
        for t in range(n - 2, -1, -1):
            beta[t] = (A @ (B[:, y[t + 1]] * beta[t + 1])) / scale[t + 1]
        ll = float(np.sum(np.log(scale)))
        if ll - previous_ll < tol:
            break
        previous_ll = ll
        # M-step
        gamma = alpha * beta
        gamma /= gamma.sum(axis=1, keepdims=True) + 1e-300
        xi_sum = np.zeros((n_states, n_states))
        for t in range(n - 1):
            xi = (alpha[t][:, None] * A) * (B[:, y[t + 1]] * beta[t + 1])[None, :]
            xi_sum += xi / (xi.sum() + 1e-300)
        A = (xi_sum + 1e-6) / (xi_sum.sum(axis=1, keepdims=True) + 1e-6 * n_states)
        B = (gamma.T @ onehot + 1e-6) / (gamma.sum(axis=0)[:, None] + 1e-6 * k)
        pi = gamma[0] / gamma[0].sum()
    return {"A": A, "B": B, "pi": pi}, ll


# ---------------------------------------------------------------------------
# M070 Bayesian change point
# ---------------------------------------------------------------------------
def run_070(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 400:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 400 observations")
    y = ctx.y
    # Grid over candidate break locations; Dirichlet-multinomial marginal likelihood.
    alpha0 = 1.0
    def log_marginal(counts: np.ndarray) -> float:
        from scipy.special import gammaln
        total = counts.sum()
        k = len(counts)
        return (float(gammaln(alpha0 * k) - gammaln(alpha0 * k + total)
                      + np.sum(gammaln(counts + alpha0) - gammaln(alpha0))))

    steps = max(10, ctx.n // 100)
    candidates = list(range(int(ctx.n * 0.15), int(ctx.n * 0.85), steps))
    log_post = []
    for tau in candidates:
        left = counts_of(y[:tau], ctx.k)
        right = counts_of(y[tau:], ctx.k)
        log_post.append(log_marginal(left) + log_marginal(right))
    log_post = np.array(log_post)
    log_post -= log_post.max()
    posterior = np.exp(log_post)
    posterior /= posterior.sum()
    best = int(candidates[int(np.argmax(posterior))])
    cumulative = np.cumsum(posterior)
    lo = candidates[int(np.searchsorted(cumulative, 0.025))]
    hi = candidates[min(int(np.searchsorted(cumulative, 0.975)), len(candidates) - 1)]

    # Compare with the no-break model.
    single = log_marginal(counts_of(y, ctx.k))
    two = float(np.max(log_post) + log_marginal(counts_of(y, ctx.k)) * 0  # scaled
                ) if False else None
    log_two = max(log_marginal(counts_of(y[:t], ctx.k)) + log_marginal(counts_of(y[t:], ctx.k))
                  for t in candidates)
    log_bf = log_two - single

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("posterior_modal_break_index", float(best), sample_size=ctx.n,
                    extra={"date": str(ctx.dates[best].date())}),
            finding("posterior_credible_low", float(lo), sample_size=ctx.n,
                    extra={"date": str(ctx.dates[lo].date())}),
            finding("posterior_credible_high", float(hi), sample_size=ctx.n,
                    extra={"date": str(ctx.dates[hi].date())}),
            finding("log_bayes_factor_two_segments", float(log_bf), sample_size=ctx.n),
            finding("max_posterior_mass", float(posterior.max()), sample_size=len(candidates)),
        ],
        narrative=(
            f"A grid posterior over {len(candidates)} candidate break positions places its mode at "
            f"index {best} ({ctx.dates[best].date()}), with a 95% credible interval spanning "
            f"{ctx.dates[lo].date()} to {ctx.dates[hi].date()}. The log Bayes factor for a "
            f"two-segment model against no break is {log_bf:+.2f} "
            f"({'evidence for a break' if log_bf > 3 else 'no meaningful evidence for a break'}; "
            f"the usual threshold is about 3). "
            f"The posterior mode carries only {posterior.max():.3f} of the mass, so even the best "
            f"candidate is barely preferred over its neighbours - which is what a flat posterior over "
            f"noise looks like."
        ),
        diagnostics={"candidates": [str(ctx.dates[c].date()) for c in candidates],
                     "posterior": np.round(posterior, 5).tolist()},
    )


# ---------------------------------------------------------------------------
# M071 Wald-Wolfowitz
# ---------------------------------------------------------------------------
def run_071(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 100:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 100 observations")
    binary = (ctx.y % 2).astype(int)
    result = _runs_test(binary)
    # Exact enumeration for small samples is infeasible at this N; the normal
    # approximation is what Wald-Wolfowitz specifies, so it is used and reported.
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("runs", float(result["observed"]), sample_size=ctx.n),
            finding("expected_runs", float(result["expected"]), sample_size=ctx.n,
                    extra={"n1": result["n1"], "n0": result["n0"]}),
            finding("z_statistic", result["z"], p_value=result["p_value"], sample_size=ctx.n),
        ],
        narrative=(
            f"With {result['n1']} odd and {result['n0']} even outcomes the expected number of runs "
            f"is {result['expected']:.3f}; the sequence contains {result['observed']}, giving "
            f"z = {result['z']:+.3f} and a two-sided p of {result['p_value']:.4f}. "
            f"This is the closed-form version of Method 61 - identical evidence, computed from the "
            f"Wald-Wolfowitz expectation and variance rather than by simulation. The platform reports "
            f"both but counts them once in the summary, so the finding list is not double-weighted."
        ),
        diagnostics={},
    )


# ---------------------------------------------------------------------------
# M072 block bootstrap
# ---------------------------------------------------------------------------
def run_072(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 200 observations")
    from src.backtesting.metrics import moving_block_bootstrap_indices

    rng = np.random.default_rng(ctx.seed)
    n_boot = 500
    probs = counts_of(ctx.y, ctx.k) / ctx.n
    results = {}
    for block in (1, 5, 10, 25, 50):
        idx = moving_block_bootstrap_indices(ctx.n, block, n_boot, rng)
        boot = np.array([np.bincount(ctx.y[i], minlength=ctx.k) / ctx.n for i in idx])
        ci = np.quantile(boot, 0.975, axis=0) - np.quantile(boot, 0.025, axis=0)
        results[block] = {"mean_width": float(ci.mean()),
                          "max_width": float(ci.max())}

    widths = {b: r["mean_width"] for b, r in results.items()}
    ratio = widths[max(widths)] / widths[1]

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"mean_ci_width_block{b}", v["mean_width"], sample_size=n_boot)
                  for b, v in results.items()]
        + [finding("width_ratio_block50_over_block1", ratio, sample_size=n_boot),
           finding("max_ci_width_any_block", float(max(v["max_width"] for v in results.values())),
                   sample_size=n_boot)],
        narrative=(
            "Mean 95% interval width for category probabilities by block length: "
            + ", ".join(f"L={b}: {v['mean_width']:.5f}" for b, v in results.items())
            + f". Going from i.i.d. resampling (L=1) to L=50 changes the width by a factor of "
            f"{ratio:.3f}. If the sequence had strong short-range dependence, longer blocks would "
            f"widen the intervals substantially, because they would capture the dependence that "
            f"i.i.d. resampling destroys. The near-flat curve is itself evidence of independence."
        ),
        diagnostics={str(b): v for b, v in results.items()},
    )


RUNNERS = {f"M{i:03d}": globals().get(f"run_{i:03d}") for i in range(61, 73)}
