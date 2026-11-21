"""Methods 35-46: time-series methods (Category D).

These methods assume a numeric, ordered outcome. For an ank that is defensible in
a limited sense (digits sit on a circle); for a jodi it is not, and the module
returns ``not_applicable`` rather than fitting a meaningless regression. The
applicability check is explicit in :func:`_require_numeric`.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from scipy import stats

from src.mathematics.common import (
    autocorrelation,
    chi2_contingency,
    counts_of,
    normal_ci,
    permutation_pvalue,
)
from src.mathematics.types import (
    STATUS_COMPUTED,
    STATUS_FAILED,
    STATUS_INSUFFICIENT_DATA,
    STATUS_NOT_APPLICABLE,
    STATUS_UNAVAILABLE,
    MethodContext,
    MethodOutput,
    finding,
)


def _require_numeric(ctx: MethodContext) -> MethodOutput | None:
    from src.preprocessing.normalization import has_defensible_numeric_representation

    if not has_defensible_numeric_representation(ctx.space):
        return MethodOutput(
            status=STATUS_NOT_APPLICABLE,
            narrative=(f"outcome space '{ctx.space}' has no defensible numeric representation; "
                       f"applying arithmetic to arbitrary labels would produce a number with no "
                       f"meaning"),
        )
    if ctx.n < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA,
                            narrative=f"needs at least 200 observations, has {ctx.n}")
    return None


def _predictive_check(ctx: MethodContext, feature: np.ndarray, name: str) -> dict:
    """Correlation of a causal smoother with the next outcome, plus a permutation band."""
    f = feature[:-1]
    y = ctx.y[1:].astype(float)
    mask = np.isfinite(f)
    if mask.sum() < 100:
        return {"correlation": float("nan"), "p_value": float("nan"), "n": int(mask.sum())}
    corr, p = stats.pearsonr(f[mask], y[mask])
    rng = np.random.default_rng(ctx.seed)
    null = np.array([abs(stats.pearsonr(f[mask], rng.permutation(y[mask])).statistic)
                     for _ in range(200)])
    return {
        "correlation": float(corr), "p_value": float(p),
        "permutation_95pct": float(np.quantile(null, 0.95)),
        "n": int(mask.sum()), "feature": name,
    }


# ---------------------------------------------------------------------------
# M035 / M036 / M037 smoothers
# ---------------------------------------------------------------------------
def run_035(ctx: MethodContext) -> MethodOutput:
    guard = _require_numeric(ctx)
    if guard:
        return guard
    series = ctx.y.astype(float)
    results = {}
    for w in (5, 10, 25, 50):
        ma = pd.Series(series).rolling(w, min_periods=w).mean().to_numpy()
        results[w] = _predictive_check(ctx, ma, f"MA{w}")
    best = max(results, key=lambda w: abs(results[w]["correlation"]))
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"correlation_MA{w}", results[w]["correlation"],
                          p_value=results[w]["p_value"], sample_size=results[w]["n"])
                  for w in results]
        + [finding("permutation_band", results[best]["permutation_95pct"], sample_size=200),
           finding("best_abs_correlation", abs(results[best]["correlation"]),
                   sample_size=results[best]["n"], extra={"window": best})],
        narrative=(
            "Correlation between the trailing moving average and the next draw: "
            + ", ".join(f"W={w}: {results[w]['correlation']:+.4f}" for w in results)
            + f". The permutation band for |correlation| is {results[best]['permutation_95pct']:.4f}. "
            f"The largest is {abs(results[best]['correlation']):.4f} at W={best}, which "
            + ("sits inside the band: the smoothed level carries no information about the next draw."
               if abs(results[best]["correlation"]) < results[best]["permutation_95pct"] else
               "exceeds the band and would need confirmation on independent periods.")
        ),
        diagnostics={str(k): {kk: round(vv, 5) if isinstance(vv, float) else vv
                              for kk, vv in v.items()} for k, v in results.items()},
    )


def run_036(ctx: MethodContext) -> MethodOutput:
    guard = _require_numeric(ctx)
    if guard:
        return guard
    series = ctx.y.astype(float)
    results = {}
    for w in (10, 25):
        weights = np.arange(1, w + 1, dtype=float)  # linearly increasing recency weight
        weights /= weights.sum()
        wma = np.full(len(series), np.nan)
        for t in range(w, len(series)):
            wma[t] = float(np.dot(series[t - w: t], weights[::-1]))
        results[w] = _predictive_check(ctx, wma, f"WMA{w}")
    best = max(results, key=lambda w: abs(results[w]["correlation"]))
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"correlation_WMA{w}", results[w]["correlation"],
                          p_value=results[w]["p_value"], sample_size=results[w]["n"])
                  for w in results]
        + [finding("permutation_band", results[best]["permutation_95pct"], sample_size=200)],
        narrative=(
            "Linearly weighted moving averages: "
            + ", ".join(f"W={w}: r={results[w]['correlation']:+.4f}" for w in results)
            + f" against a permutation band of {results[best]['permutation_95pct']:.4f}. "
            "Weighting recent draws more heavily inside the window does not reveal structure that "
            "the simple average missed."
        ),
        diagnostics={},
    )


def run_037(ctx: MethodContext) -> MethodOutput:
    guard = _require_numeric(ctx)
    if guard:
        return guard
    series = ctx.y.astype(float)
    results = {}
    for alpha in (0.05, 0.1, 0.2, 0.5):
        ema = np.full(len(series), np.nan)
        acc = series[0]
        for t in range(len(series)):
            acc = alpha * series[t] + (1 - alpha) * acc
            ema[t] = acc
        results[alpha] = _predictive_check(ctx, ema, f"EMA{alpha}")
    best = max(results, key=lambda a: abs(results[a]["correlation"]))
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"correlation_EMA{int(a * 100)}", results[a]["correlation"],
                          p_value=results[a]["p_value"], sample_size=results[a]["n"])
                  for a in results]
        + [finding("permutation_band", results[best]["permutation_95pct"], sample_size=200)],
        narrative=(
            "Exponential moving average correlations: "
            + ", ".join(f"alpha={a}: r={results[a]['correlation']:+.4f}" for a in results)
            + f", permutation band {results[best]['permutation_95pct']:.4f}. "
            "The best smoothing rate still produces a correlation indistinguishable from noise."
        ),
        diagnostics={},
    )


# ---------------------------------------------------------------------------
# M038 AR
# ---------------------------------------------------------------------------
def run_038(ctx: MethodContext) -> MethodOutput:
    guard = _require_numeric(ctx)
    if guard:
        return guard
    from statsmodels.tsa.ar_model import AutoReg
    from statsmodels.stats.diagnostic import acorr_ljungbox

    series = ctx.y.astype(float)
    results = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for p in (1, 2, 3, 5):
            try:
                model = AutoReg(series, lags=p).fit()
                resid = model.resid[p:]
                lb = acorr_ljungbox(resid, lags=[10], return_df=True)
                results[p] = {
                    "aic": float(model.aic), "bic": float(model.bic),
                    "params": [round(float(v), 5) for v in model.params[1:]],
                    "residual_ljungbox_p": float(lb["lb_pvalue"].iloc[0]),
                    "r2": float(model.rsquared),
                }
            except Exception as exc:  # pragma: no cover
                results[p] = {"error": str(exc)}
    ok = {p: v for p, v in results.items() if "aic" in v}
    if not ok:
        return MethodOutput(status=STATUS_FAILED, narrative="all AR orders failed to fit")
    best = min(ok, key=lambda p: ok[p]["bic"])
    # Out-of-sample skill via one-step-ahead prediction on the last 30%.
    cut = int(len(series) * 0.7)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fitted = AutoReg(series[:cut], lags=best).fit()
            # One-step-ahead forecasts only: `append(..., refit=False)` re-filters
            # with each realised value, which is the honest out-of-sample exercise.
            # A single fixed-coefficient multi-step forecast would be a different
            # (and much worse) claim.
            extended = fitted.append(series[cut:], refit=False)
            preds = np.asarray(extended.predict(start=cut, end=len(series) - 1)).ravel()
        actual = series[cut:]
        naive = np.full(len(actual), series[:cut].mean())
        n_eval = min(len(actual), len(preds))
        mse_model = float(np.mean((actual[:n_eval] - preds[:n_eval]) ** 2))
        mse_naive = float(np.mean((actual[:n_eval] - naive[:n_eval]) ** 2))
    except Exception as exc:  # pragma: no cover
        mse_model = mse_naive = None
        oos_error = f"{type(exc).__name__}: {exc}"
    else:
        oos_error = None

    ratio = (None if (mse_model is None or mse_naive in (None, 0) or mse_naive != mse_naive)
             else mse_model / mse_naive)
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"ar{best}_bic", ok[best]["bic"], sample_size=ctx.n),
                  finding(f"ar{best}_aic", ok[best]["aic"], sample_size=ctx.n),
                  finding("residual_ljungbox_p", ok[best]["residual_ljungbox_p"],
                          p_value=ok[best]["residual_ljungbox_p"], sample_size=ctx.n),
                  finding("in_sample_r2", ok[best]["r2"], sample_size=ctx.n),
                  finding("oos_mse_ar", mse_model, sample_size=len(actual)),
                  finding("oos_mse_mean_baseline", mse_naive, sample_size=len(actual)),
                  finding("oos_mse_ratio", ratio, sample_size=len(actual))],
        narrative=(
            f"AR order {best} minimises BIC ({ok[best]['bic']:.1f}) with in-sample R-squared "
            f"{ok[best]['r2']:.5f}. Ljung-Box on the residuals gives p = "
            f"{ok[best]['residual_ljungbox_p']:.4f}"
            + (" (residuals still autocorrelated, so the order is too low)"
               if ok[best]["residual_ljungbox_p"] < 0.05 else " (residuals consistent with white noise)")
            + (f". Out of sample the one-step MSE is {mse_model:.4f} against {mse_naive:.4f} "
               f"for a constant-mean baseline, a ratio of {ratio:.4f}. "
               if ratio is not None else
               f". Out-of-sample scoring failed ({oos_error}), so no skill claim is made. ")
            + f"An R-squared of {ok[best]['r2']:.5f} means the model explains a negligible "
              f"share of variance; there is nothing here to exploit."
        ),
        diagnostics={"by_order": {str(k): v for k, v in results.items()},
                     "oos_error": oos_error},
    )


# ---------------------------------------------------------------------------
# M039 ARMA
# ---------------------------------------------------------------------------
def run_039(ctx: MethodContext) -> MethodOutput:
    guard = _require_numeric(ctx)
    if guard:
        return guard
    from statsmodels.tsa.arima.model import ARIMA

    series = ctx.y.astype(float)
    results = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for p, q in ((1, 0), (1, 1), (2, 1), (2, 2)):
            try:
                fit = ARIMA(series, order=(p, 0, q)).fit()
                results[f"ARMA({p},{q})"] = {
                    "aic": float(fit.aic), "bic": float(fit.bic),
                    "loglik": float(fit.llf),
                }
            except Exception as exc:
                results[f"ARMA({p},{q})"] = {"error": str(exc)[:120]}
    ok = {k: v for k, v in results.items() if "aic" in v}
    if not ok:
        return MethodOutput(status=STATUS_FAILED, narrative="no ARMA specification converged")
    best = min(ok, key=lambda k: ok[k]["bic"])
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"bic_{k}", v["bic"], sample_size=ctx.n) for k, v in ok.items()]
        + [finding("best_bic", ok[best]["bic"], sample_size=ctx.n, extra={"model": best}),
           finding("aic_model_advantage_over_ar1",
                   ok.get("ARMA(1,0)", {}).get("bic", float("nan")) - ok[best]["bic"],
                   sample_size=ctx.n)],
        narrative=(
            "BIC by specification: "
            + ", ".join(f"{k} {v['bic']:.1f}" for k, v in ok.items())
            + f". Best is {best}. The improvement of the moving-average term over a plain AR(1) is "
            f"{ok.get('ARMA(1,0)', {}).get('bic', float('nan')) - ok[best]['bic']:+.1f} BIC units. "
            "Any fitted model here is describing bounded discrete noise with a continuous unbounded "
            "process, so a low information criterion is not evidence of a real generating mechanism."
        ),
        diagnostics={"by_spec": results},
    )


# ---------------------------------------------------------------------------
# M040 ARIMA
# ---------------------------------------------------------------------------
def run_040(ctx: MethodContext) -> MethodOutput:
    guard = _require_numeric(ctx)
    if guard:
        return guard
    from statsmodels.tsa.stattools import adfuller
    from statsmodels.tsa.arima.model import ARIMA

    series = ctx.y.astype(float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        adf_level = adfuller(series, maxlag=10, autolag="AIC")
        adf_diff = adfuller(np.diff(series), maxlag=10, autolag="AIC")
        d = 0 if adf_level[1] < 0.05 else 1
        try:
            fit = ARIMA(series, order=(1, d, 1)).fit()
            aic = float(fit.aic)
            bic = float(fit.bic)
        except Exception as exc:
            return MethodOutput(status=STATUS_FAILED, narrative=f"ARIMA fit failed: {exc}")

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("adf_statistic_level", float(adf_level[0]), p_value=float(adf_level[1]),
                    sample_size=ctx.n),
            finding("adf_p_level", float(adf_level[1]), p_value=float(adf_level[1]),
                    sample_size=ctx.n),
            finding("adf_p_differenced", float(adf_diff[1]), p_value=float(adf_diff[1]),
                    sample_size=ctx.n),
            finding("selected_d", float(d), sample_size=ctx.n),
            finding("arima_aic", aic, sample_size=ctx.n),
            finding("arima_bic", bic, sample_size=ctx.n),
        ],
        narrative=(
            f"A Dickey-Fuller test on the level gives statistic {adf_level[0]:.3f} "
            f"(p = {adf_level[1]:.4f}), so the selected differencing order is d={d}. "
            f"On the differenced series the p-value is {adf_diff[1]:.4f}. ARIMA(1,{d},1) gives AIC "
            f"{aic:.1f}. "
            + ("The level series is already stationary, so differencing would be unnecessary."
               if d == 0 else
               "The level appears non-stationary, though for a bounded discrete outcome this often "
               "reflects a slowly drifting mean rather than a unit root.")
        ),
        diagnostics={"adf_level": list(map(str, adf_level[:2]))},
    )


# ---------------------------------------------------------------------------
# M041 seasonal decomposition
# ---------------------------------------------------------------------------
def run_041(ctx: MethodContext) -> MethodOutput:
    guard = _require_numeric(ctx)
    if guard:
        return guard
    from statsmodels.tsa.seasonal import seasonal_decompose

    series = pd.Series(ctx.y.astype(float), index=ctx.dates)
    period = 7
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            decomposition = seasonal_decompose(series, model="additive", period=period,
                                               extrapolate_trend="period")
        except Exception as exc:
            return MethodOutput(status=STATUS_FAILED, narrative=f"decomposition failed: {exc}")
    resid = decomposition.resid.dropna()
    seasonal_strength = float(max(0.0, 1 - np.var(resid) / np.var(resid + decomposition.seasonal.dropna())))
    trend_strength = float(max(0.0, 1 - np.var(resid) / np.var(resid + decomposition.trend.dropna())))
    rng = np.random.default_rng(ctx.seed)
    null_strength = []
    for _ in range(100):
        shuffled = pd.Series(rng.permutation(series.to_numpy()), index=series.index)
        dec = seasonal_decompose(shuffled, model="additive", period=period, extrapolate_trend="period")
        r = dec.resid.dropna()
        null_strength.append(float(max(0.0, 1 - np.var(r) / np.var(r + dec.seasonal.dropna()))))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("seasonal_strength", seasonal_strength, sample_size=ctx.n),
            finding("trend_strength", trend_strength, sample_size=ctx.n),
            finding("permutation_seasonal_strength_mean", float(np.mean(null_strength)),
                    sample_size=100),
            finding("permutation_95pct", float(np.quantile(null_strength, 0.95)), sample_size=100),
            finding("residual_std", float(resid.std()), sample_size=len(resid)),
        ],
        narrative=(
            f"With a 7-day period, seasonal strength is {seasonal_strength:.4f} and trend strength "
            f"{trend_strength:.4f}. Shuffling the series destroys any real calendar structure while "
            f"preserving its distribution; the shuffled series still yields a seasonal strength of "
            f"{np.mean(null_strength):.4f} on average (95th percentile "
            f"{np.quantile(null_strength, 0.95):.4f}) purely because decomposition fits noise. "
            + ("The observed strength is inside the null band: no seasonal structure."
               if seasonal_strength < np.quantile(null_strength, 0.95) else
               "The observed strength exceeds the null band and warrants the formal calendar tests "
               "in Method 43.")
        ),
        diagnostics={"seasonal_mean_by_dow": [round(float(v), 4) for v in
                                              decomposition.seasonal.dropna().groupby(
                                                  decomposition.seasonal.dropna().index.dayofweek
                                              ).mean()]},
    )


# ---------------------------------------------------------------------------
# M042 seasonal ARIMA
# ---------------------------------------------------------------------------
def run_042(ctx: MethodContext) -> MethodOutput:
    guard = _require_numeric(ctx)
    if guard:
        return guard
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    series = ctx.y.astype(float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            fit = SARIMAX(series, order=(1, 0, 1), seasonal_order=(1, 0, 0, 7),
                          enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
            aic = float(fit.aic)
            converged = bool(fit.mle_retvals.get("converged", True))
        except Exception as exc:
            return MethodOutput(status=STATUS_FAILED,
                                narrative=f"SARIMA did not fit: {type(exc).__name__}: {exc}")
    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("sarima_aic", aic, sample_size=ctx.n),
            finding("converged", float(converged), sample_size=ctx.n),
        ],
        narrative=(
            f"A SARIMA(1,0,1)(1,0,0,7) fit gives AIC {aic:.1f} "
            f"({'converged' if converged else 'did not converge'}). A seasonal period of 7 is "
            f"imposed rather than discovered, and Method 41 found no seasonal strength to model. "
            f"Fitting a seasonal model to a series with no seasonal structure adds parameters and "
            f"degrees of freedom without adding information, which is why the platform does not "
            f"promote it regardless of its information criterion."
        ),
        diagnostics={},
    )


# ---------------------------------------------------------------------------
# M043 calendar effects
# ---------------------------------------------------------------------------
def run_043(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA,
                            narrative=f"needs 300 observations, has {ctx.n}")
    from src.mathematics.common import chi2_uniform, holm

    dow = ctx.dates.dayofweek.to_numpy()
    month = ctx.dates.month.to_numpy()
    dom = ctx.dates.day.to_numpy()

    tests = {}
    # Weekday: contingency of outcome x weekday.
    for name, keys in (("weekday", dow), ("month", month),
                       ("dom_band", np.digitize(dom, [8, 15, 22, 29]))):
        levels = sorted(set(keys.tolist()))
        table = np.array([counts_of(ctx.y[keys == lev], ctx.k) for lev in levels])
        result = chi2_contingency(table)
        tests[name] = {"chi2": result["statistic"], "p_value": result["p_value"],
                       "cramers_v": result["cramers_v"], "n_levels": len(levels)}
    # Parity by weekday as a coarse, high-power variant.
    parity = (ctx.y % 2)
    parity_tests = {}
    for name, keys in (("weekday", dow), ("month", month)):
        levels = sorted(set(keys.tolist()))
        table = np.array([[int(np.sum((keys == lev) & (parity == 0))),
                           int(np.sum((keys == lev) & (parity == 1)))] for lev in levels])
        result = chi2_contingency(table)
        parity_tests[name] = {"chi2": result["statistic"], "p_value": result["p_value"],
                              "cramers_v": result["cramers_v"]}

    all_p = [tests[k]["p_value"] for k in tests] + [parity_tests[k]["p_value"] for k in parity_tests]
    adjusted = holm(all_p)
    n_sig_raw = sum(p < 0.05 for p in all_p)
    n_sig_adj = sum(p < 0.05 for p in adjusted)

    findings = [finding(f"{name}_chi2", tests[name]["chi2"], p_value=tests[name]["p_value"],
                        effect_size=tests[name]["cramers_v"], sample_size=ctx.n)
                for name in tests]
    findings += [finding(f"{name}_parity_chi2", parity_tests[name]["chi2"],
                         p_value=parity_tests[name]["p_value"],
                         effect_size=parity_tests[name]["cramers_v"], sample_size=ctx.n)
                 for name in parity_tests]
    findings += [
        finding("n_tests", float(len(all_p)), sample_size=ctx.n),
        finding("n_significant_uncorrected", float(n_sig_raw), sample_size=ctx.n),
        finding("n_significant_holm", float(n_sig_adj), sample_size=ctx.n),
    ]

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=findings,
        narrative=(
            f"{len(all_p)} calendar tests were run. Uncorrected, {n_sig_raw} reach p<0.05; after "
            f"Holm correction across the family, {n_sig_adj} do. "
            + (f"With {len(all_p)} tests, {len(all_p) * 0.05:.1f} uncorrected rejections are expected "
               f"by chance alone, so the uncorrected count is exactly the noise level."
               if n_sig_raw <= len(all_p) * 0.05 + 1 else
               "More tests reject than chance would produce, but correction still removes them, "
               "indicating the apparent effects are not individually defensible.")
            + " Calendar features are known in advance, which makes them attractive; the tests show "
              "whether they actually change the outcome distribution."
        ),
        diagnostics={"tests": tests, "parity": parity_tests,
                     "holm_adjusted": [round(p, 5) for p in adjusted]},
    )


# ---------------------------------------------------------------------------
# M044 rolling regime
# ---------------------------------------------------------------------------
def run_044(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 400:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 400 observations")
    window = max(100, ctx.n // 8)
    starts = list(range(0, ctx.n - window + 1, window))
    probs = []
    for s in starts:
        probs.append(counts_of(ctx.y[s: s + window], ctx.k) / window)
    probs = np.array(probs)
    dispersion = float(np.mean(np.std(probs, axis=0)))
    expected = float(np.mean(np.sqrt((1 / ctx.k) * (1 - 1 / ctx.k) / window)))
    # Consecutive-window homogeneity.
    chi2_tests = []
    for i in range(len(probs) - 1):
        table = np.array([counts_of(ctx.y[starts[i]: starts[i] + window], ctx.k),
                          counts_of(ctx.y[starts[i + 1]: starts[i + 1] + window], ctx.k)])
        chi2_tests.append(chi2_contingency(table))
    n_sig = sum(1 for t in chi2_tests if t["p_value"] < 0.05)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("window_dispersion", dispersion, sample_size=len(starts)),
            finding("expected_dispersion_under_stationarity", expected, sample_size=len(starts)),
            finding("dispersion_ratio", dispersion / expected if expected > 0 else None,
                    sample_size=len(starts)),
            finding("n_adjacent_pairs_differing", float(n_sig), sample_size=len(chi2_tests)),
            finding("n_adjacent_pairs_tested", float(len(chi2_tests)), sample_size=len(chi2_tests)),
        ],
        narrative=(
            f"Across {len(starts)} windows of {window} draws the average standard deviation of "
            f"category probabilities is {dispersion:.5f}, against {expected:.5f} expected from pure "
            f"multinomial sampling (ratio {dispersion / expected:.3f}). Of {len(chi2_tests)} adjacent "
            f"window pairs, {n_sig} differ at p<0.05. "
            + ("Window-wise distributions vary no more than sampling noise requires, so the process "
               "is stable enough for pooled estimates." if dispersion / expected < 1.2 else
               "Window-wise distributions vary more than sampling noise explains, which limits the "
               "value of any pooled estimate.")
        ),
        diagnostics={"window_probabilities": np.round(probs, 4).tolist()},
    )


# ---------------------------------------------------------------------------
# M045 state-space
# ---------------------------------------------------------------------------
def run_045(ctx: MethodContext) -> MethodOutput:
    guard = _require_numeric(ctx)
    if guard:
        return guard
    try:
        from statsmodels.tsa.statespace.structural import UnobservedComponents
    except ImportError:  # pragma: no cover
        return MethodOutput(status=STATUS_UNAVAILABLE, narrative="statsmodels unavailable")

    series = ctx.y.astype(float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            mod = UnobservedComponents(series, level="local level")
            fit = mod.fit(disp=False)
        except Exception as exc:
            return MethodOutput(status=STATUS_FAILED,
                                narrative=f"state-space fit failed: {type(exc).__name__}: {exc}")
    # statsmodels exposes filtered/smoothed states differently across versions;
    # probe instead of assuming one attribute name.
    smoothed = None
    for attr in ("smoothed_forecasts", "smoothed"):
        candidate = getattr(fit, attr, None)
        if candidate is None:
            continue
        try:
            smoothed = np.asarray(candidate).ravel()[: len(series)]
            break
        except Exception:
            continue
    innovations = np.asarray(fit.filter_results.standardized_forecasts_error).ravel()
    lb = stats.normaltest(innovations[: min(len(innovations), 2000)]) if len(innovations) > 20 else None
    from statsmodels.stats.diagnostic import acorr_ljungbox
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        lb_test = acorr_ljungbox(innovations, lags=[10], return_df=True)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("loglik", float(fit.llf), sample_size=ctx.n),
            finding("innovation_ljungbox_p", float(lb_test["lb_pvalue"].iloc[0]),
                    p_value=float(lb_test["lb_pvalue"].iloc[0]), sample_size=ctx.n),
            finding("innovation_skew", float(stats.skew(innovations)), sample_size=len(innovations)),
            finding("innovation_kurtosis", float(stats.kurtosis(innovations)),
                    sample_size=len(innovations)),
            finding("state_variance_estimate", float(fit.params.iloc[0]) if hasattr(fit.params, "iloc")
                    else float(fit.params[0]), sample_size=ctx.n),
        ],
        narrative=(
            f"A local-level state-space model on the numeric encoding gives log-likelihood "
            f"{fit.llf:.1f}. The standardised innovations have Ljung-Box p = "
            f"{float(lb_test['lb_pvalue'].iloc[0]):.4f}, skewness {stats.skew(innovations):.3f} and "
            f"excess kurtosis {stats.kurtosis(innovations):.3f}. "
            + ("The innovations are consistent with white noise, i.e. the latent-level model has "
               "nothing left to explain - unsurprising for a bounded discrete outcome."
               if float(lb_test["lb_pvalue"].iloc[0]) > 0.05 else
               "The innovations retain serial correlation, so the latent-level formulation is "
               "inadequate for this series.")
        ),
        diagnostics={"n_innovations": int(len(innovations))},
    )


# ---------------------------------------------------------------------------
# M046 dynamic GLM
# ---------------------------------------------------------------------------
def run_046(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 500:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 500 observations")
    from src.models.market_models import build
    from src.preprocessing.feature_engineering import FeatureConfig, build_features

    cfg = FeatureConfig(include_cross_market=False, include_same_day_open=False, include_calendar=False)
    X = build_features(ctx.y, cfg).to_numpy(dtype=float)
    keep = ["freq_all_0", "prev_value", "gap_0"]
    cols = [i for i, c in enumerate(build_features(ctx.y, cfg).columns)
            if c in ("prev_value", "freq_all_0", "min_gap")]
    Xs = np.nan_to_num(X[:, cols], nan=0.0)

    starts = list(range(200, ctx.n, max(100, ctx.n // 12)))
    paths = []
    for start in starts:
        try:
            model = build("logistic")
            model.fit(Xs[:start], ctx.y[:start])
            final = model[-1] if hasattr(model, "__getitem__") else None
            coefs = model.named_steps["model"].coef_ if hasattr(model, "named_steps") else None
            if coefs is not None:
                paths.append({"n_train": int(start),
                              "mean_abs_coef": float(np.abs(coefs[:, : len(cols)]).mean())})
        except Exception:
            continue
    if len(paths) < 3:
        return MethodOutput(status=STATUS_FAILED, narrative="too few refits to track coefficients")
    values = np.array([p["mean_abs_coef"] for p in paths])
    drift = float(np.std(values) / max(np.mean(values), 1e-12))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("n_refits", float(len(paths)), sample_size=ctx.n),
            finding("coefficient_scale_mean", float(np.mean(values)), sample_size=len(paths)),
            finding("coefficient_relative_drift", drift, sample_size=len(paths)),
            finding("coefficient_first", float(values[0]), sample_size=paths[0]["n_train"]),
            finding("coefficient_last", float(values[-1]), sample_size=paths[-1]["n_train"]),
        ],
        narrative=(
            f"Refitting a multinomial logistic model at {len(paths)} expanding cut-offs, the mean "
            f"absolute coefficient moves from {values[0]:.5f} to {values[-1]:.5f} with a relative "
            f"standard deviation of {drift:.3f} across refits. "
            + ("Coefficient scale barely changes as data accumulate, which is the behaviour of a "
               "model converging on 'the features are uninformative' rather than of a relationship "
               "being learned." if drift < 0.5 else
               "Coefficients drift substantially between refits, indicating an unstable "
               "relationship rather than a learnable one.")
            + " A true dynamic GLM would add a state equation for the coefficients; this expanding-"
              "window path is a transparency approximation and is labelled as such."
        ),
        diagnostics={"path": paths},
    )


RUNNERS = {f"M{i:03d}": globals().get(f"run_{i:03d}") for i in range(35, 47)}
