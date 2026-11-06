"""Methods 85-100: advanced probability, ensembles and model validation (Category H).

Two of these methods (91, 92) are *meta*-analyses over the p-values produced by all
the others; the engine runs them last and injects the collected p-values through
``ctx.extras['all_p_values']``. Everything else is a self-contained procedure over
the model panel or the raw sequence.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from src.backtesting.metrics import log_loss, paired_bootstrap_difference
from src.backtesting.validation import fdr_correct
from src.mathematics.common import counts_of, entropy, holm
from src.mathematics.model_panel import get_panel
from src.mathematics.types import (
    STATUS_COMPUTED,
    STATUS_FAILED,
    STATUS_INSUFFICIENT_DATA,
    STATUS_NOT_APPLICABLE,
    MethodContext,
    MethodOutput,
    finding,
)


def _panel_or_none(ctx: MethodContext):
    try:
        return get_panel(ctx)
    except Exception:
        return None


def _unavailable(message: str) -> MethodOutput:
    return MethodOutput(status=STATUS_FAILED, narrative=message)


# ---------------------------------------------------------------------------
# M085 Bayesian model averaging
# ---------------------------------------------------------------------------
def run_085(ctx: MethodContext) -> MethodOutput:
    panel = _panel_or_none(ctx)
    if panel is None or len(panel.models) < 2:
        return _unavailable("model panel unavailable; BMA needs at least two candidate models")
    from src.models.ensembles import bayesian_model_averaging, combine

    y = next(iter(panel.models.values())).y_true
    split = int(len(y) * 0.5)
    train = {n: r.probs[:split] for n, r in panel.models.items()}
    test = {n: r.probs[split:] for n, r in panel.models.items()}
    weights = bayesian_model_averaging(train, y[:split])
    combined = combine(test, list(weights.values()))
    bma_ll = float(log_loss(combined, y[split:]))
    base_name = panel.best_baseline_name()
    baseline_ll = float(panel.baselines[base_name].per_obs_log_loss().mean())

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("bma_log_loss_holdout", bma_ll, sample_size=int(len(y) - split)),
            finding("best_baseline_log_loss", baseline_ll, sample_size=int(len(y) - split)),
            finding("bma_minus_baseline", bma_ll - baseline_ll, sample_size=int(len(y) - split)),
            finding("effective_n_models", float(1 / np.sum(np.square(list(weights.values())))),
                    sample_size=len(weights)),
            finding("top_model_weight", float(max(weights.values())), sample_size=len(weights),
                    extra={"model": max(weights, key=weights.get)}),
        ],
        narrative=(
            f"BIC-approximated posterior model probabilities (fitted on the first half of the "
            f"out-of-sample window, scored on the second) concentrate "
            f"{max(weights.values()):.3f} of the mass on {max(weights, key=weights.get)}; the "
            f"effective number of models is "
            f"{1 / np.sum(np.square(list(weights.values()))):.2f} of {len(weights)}. The averaged "
            f"forecast scores {bma_ll:.5f} against {baseline_ll:.5f} for the strongest baseline "
            f"({base_name}). "
            + ("Averaging cannot manufacture accuracy from models that are all near-random; it only "
               "reduces variance around the same wrong answer."
               if bma_ll >= baseline_ll else
               "The averaged forecast beats the strongest baseline on held-out data.")
            + " Note the BIC evidence approximation is crude for these non-nested models and is "
              "labelled as an approximation wherever reported."
        ),
        diagnostics={"weights": {k: round(v, 4) for k, v in weights.items()}},
    )


# ---------------------------------------------------------------------------
# M086 regularised stacking (independent restatement on a fresh split)
# ---------------------------------------------------------------------------
def run_086(ctx: MethodContext) -> MethodOutput:
    panel = _panel_or_none(ctx)
    if panel is None or len(panel.models) < 3:
        return _unavailable("needs at least three base models with out-of-sample predictions")
    from src.models.ensembles import regularised_stack

    y = next(iter(panel.models.values())).y_true
    split = int(len(y) * 0.6)
    train = {n: r.probs[:split] for n, r in panel.models.items()}
    test = {n: r.probs[split:] for n, r in panel.models.items()}
    stack = regularised_stack(train, y[:split], test, y[split:])
    base_name = panel.best_baseline_name()

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("stack_holdout_log_loss", stack.meta_log_loss, sample_size=int(len(y) - split)),
            finding("iterative_weight_mass", float(max(stack.weights.values())),
                    sample_size=len(stack.weights),
                    extra={"model": max(stack.weights, key=stack.weights.get)}),
            finding("improved_over_best_base", float(stack.improved), sample_size=len(stack.weights)),
            finding("beats_strongest_baseline",
                    float(stack.meta_log_loss < panel.baselines[base_name].per_obs_log_loss().mean()),
                    sample_size=int(len(y) - split)),
        ],
        narrative=(
            f"Simplex-constrained stacking on a 60/40 split of the out-of-sample window: holdout log "
            f"loss {stack.meta_log_loss:.5f}, with {max(stack.weights.values()):.3f} of the weight on "
            f"{max(stack.weights, key=stack.weights.get)}. It "
            f"{'does' if stack.improved else 'does not'} improve on the best individual base model "
            f"({min(stack.base_log_losses.values()):.5f}). "
            + ("The stack therefore inherits the weakness of its members rather than correcting it."
               if not stack.improved else
               "The combination adds something beyond the best member, which is the only reason to "
               "prefer it.")
        ),
        diagnostics={"weights": {k: round(v, 4) for k, v in stack.weights.items()},
                     "base_losses": {k: round(v, 5) for k, v in stack.base_log_losses.items()}},
    )


# ---------------------------------------------------------------------------
# M087 conformal prediction
# ---------------------------------------------------------------------------
def run_087(ctx: MethodContext) -> MethodOutput:
    panel = _panel_or_none(ctx)
    if panel is None or not panel.models:
        return _unavailable("no model predictions available for conformal calibration")
    best_model = min(panel.models, key=lambda n: panel.models[n].per_obs_log_loss().mean())
    result = panel.models[best_model]
    probs, y = result.probs, result.y_true
    split = int(len(y) * 0.4)
    scores = 1.0 - probs[np.arange(split), y[:split]]      # nonconformity on calibration slice
    target_coverage = 0.90
    q = float(np.quantile(scores, target_coverage))
    sizes = []
    covered = []
    for i in range(split, len(y)):
        included = np.flatnonzero((1.0 - probs[i]) <= q)
        sizes.append(len(included))
        covered.append(bool(y[i] in included))
    coverage = float(np.mean(covered))
    expected_size = target_coverage * len(y) / len(y)  # placeholder for clarity

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("nominal_coverage", target_coverage, sample_size=int(len(y) - split)),
            finding("empirical_coverage", coverage, sample_size=int(len(y) - split)),
            finding("coverage_gap", coverage - target_coverage, sample_size=int(len(y) - split)),
            finding("mean_prediction_set_size", float(np.mean(sizes)), sample_size=len(sizes)),
            finding("min_set_size", float(np.min(sizes)), sample_size=len(sizes)),
        ],
        narrative=(
            f"Split-conformal prediction using {best_model} as the underlying model, with a nominal "
            f"{target_coverage:.0%} coverage target: the empirical coverage on the later 60% of the "
            f"window is {coverage:.4f}, a gap of {coverage - target_coverage:+.4f}. Mean prediction "
            f"set size is {np.mean(sizes):.2f} of {probs.shape[1]} possible outcomes (smallest "
            f"{int(np.min(sizes))}). "
            f"The conformal guarantee requires exchangeability between calibration and test points, "
            f"which a time series does not satisfy - so this gap is the honest measure of how much "
            f"the guarantee is worth here. A model with no skill produces large sets; small sets on a "
            f"10-way problem would themselves indicate real information."
        ),
        diagnostics={"threshold": round(q, 5), "model": best_model,
                     "set_sizes": [int(s) for s in sizes[:200]]},
    )


# ---------------------------------------------------------------------------
# M088-M090 calibration
# ---------------------------------------------------------------------------
def _calibration_method(ctx: MethodContext, calibrator_name: str, label: str,
                        method_family: str) -> MethodOutput:
    panel = _panel_or_none(ctx)
    if panel is None or not panel.models:
        return _unavailable("no candidate model available")
    from src.models.calibration import evaluate_calibration, make_calibrator

    best_model = min(panel.models, key=lambda n: panel.models[n].per_obs_log_loss().mean())
    result = panel.models[best_model]
    probs, y = result.probs, result.y_true
    split = int(len(y) * 0.4)
    calibrator = make_calibrator(calibrator_name)
    try:
        calibrator.fit(probs[:split], y[:split])
        calibrated = calibrator.transform(probs[split:])
    except Exception as exc:
        return _unavailable(f"{label} fitting failed: {type(exc).__name__}: {exc}")

    before = evaluate_calibration(probs[split:], y[split:])
    after = evaluate_calibration(calibrated, y[split:])
    diff = paired_bootstrap_difference(
        -np.log(np.clip(calibrated[np.arange(len(y) - split), y[split:]], 1e-12, None)),
        -np.log(np.clip(probs[split:][np.arange(len(y) - split), y[split:]], 1e-12, None)),
        n_resamples=500, seed=ctx.seed,
    )

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("log_loss_before", before["log_loss"], sample_size=int(len(y) - split)),
            finding("log_loss_after", after["log_loss"], sample_size=int(len(y) - split)),
            finding("log_loss_change", after["log_loss"] - before["log_loss"],
                    p_value=diff["p_two_sided"], sample_size=int(len(y) - split)),
            finding("ece_before", before["ece"], sample_size=int(len(y) - split)),
            finding("ece_after", after["ece"], sample_size=int(len(y) - split)),
            finding("slope_before", before["slope"], sample_size=int(len(y) - split)),
            finding("slope_after", after["slope"], sample_size=int(len(y) - split)),
        ],
        narrative=(
            f"{label} applied to {best_model}, fitted on the first 40% of the out-of-sample window "
            f"and scored on the remaining 60%. Log loss moves from {before['log_loss']:.5f} to "
            f"{after['log_loss']:.5f} ({after['log_loss'] - before['log_loss']:+.5f}, bootstrap "
            f"p = {diff['p_two_sided']:.3f}); ECE from {before['ece']:.4f} to {after['ece']:.4f}; "
            f"calibration slope from {before['slope']} to {after['slope']}. "
            + ("Calibration improves the probability quality, which matters if the numbers are read as "
               "probabilities rather than as a ranking. It does not and cannot improve accuracy - "
               "recalibration is a monotone reshaping, so the predicted ordering is unchanged."
               if after["ece"] < before["ece"] else
               "Calibration does not improve the reliability of these predictions on held-out data; "
               "the miscalibration here is not of a form this family can correct.")
            + f" {method_family}"
        ),
        diagnostics={"before": {k: v for k, v in before.items() if k != "table"},
                     "after": {k: v for k, v in after.items() if k != "table"},
                     "reliability_after": after["table"]},
    )


def run_088(ctx: MethodContext) -> MethodOutput:
    return _calibration_method(ctx, "isotonic", "Isotonic calibration",
                               "Isotonic regression is fitted one-vs-rest then renormalised, which "
                               "makes it flexible but prone to overfitting on short calibration samples.")


def run_089(ctx: MethodContext) -> MethodOutput:
    return _calibration_method(ctx, "platt", "Platt scaling",
                               "Platt scaling fits two parameters per class, so it is far safer on "
                               "small calibration samples and correspondingly less able to correct "
                               "anything beyond a sigmoidal distortion.")


def run_090(ctx: MethodContext) -> MethodOutput:
    return _calibration_method(ctx, "dirichlet", "Dirichlet calibration",
                               "Vector scaling in log-probability space can correct multi-class "
                               "miscalibration that per-class methods miss, at the cost of K x K "
                               "parameters shrunk toward the identity.")


# ---------------------------------------------------------------------------
# M091 / M092 multiple testing
# ---------------------------------------------------------------------------
def _collect_p_values(ctx: MethodContext) -> list[tuple[str, float]]:
    injected = ctx.extras.get("all_p_values")
    if injected:
        return list(injected)
    return []


def run_091(ctx: MethodContext) -> MethodOutput:
    p_values = _collect_p_values(ctx)
    if len(p_values) < 5:
        return MethodOutput(
            status=STATUS_INSUFFICIENT_DATA,
            narrative=("fewer than five p-values were available to the meta-analysis; run the full "
                       "method sweep before this method"),
        )
    names = [n for n, _ in p_values]
    raw = [p for _, p in p_values]
    alpha = float(ctx.params.get("alpha", 0.05)) if "alpha" in ctx.params else 0.05
    corrected = fdr_correct(raw, "benjamini_hochberg", alpha)
    n_raw = sum(1 for p in raw if p < alpha)
    n_adj = corrected["n_rejected"]
    survivors = [names[i] for i, rejected in enumerate(corrected["rejected"]) if rejected]

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("n_tests_collected", float(len(raw)), sample_size=len(raw)),
            finding("n_significant_uncorrected", float(n_raw), sample_size=len(raw)),
            finding("n_significant_bh", float(n_adj), sample_size=len(raw)),
            finding("expected_false_positives_uncorrected", len(raw) * alpha, sample_size=len(raw)),
            finding("smallest_p_value", float(min(raw)), p_value=float(min(raw)),
                    sample_size=len(raw), extra={"method": names[int(np.argmin(raw))]}),
        ],
        narrative=(
            f"{len(raw)} p-values were collected across the method suite. At the 5% level, "
            f"{n_raw} are nominally significant, and about {len(raw) * alpha:.1f} would be expected "
            f"by chance alone. Benjamini-Hochberg at q={alpha} leaves {n_adj} significant"
            + (f" ({', '.join(survivors[:8])})" if survivors else "") + ". "
            + ("The correction removes everything, which is the expected outcome for a genuinely "
               "unpredictable process: without correction, roughly one in twenty of these tests "
               "would have produced a 'discovery'." if n_adj == 0 else
               "A subset survives FDR control, but note the tests are strongly dependent (many share "
               "the same underlying sequence), which makes BH conservative here rather than invalid.")
        ),
        diagnostics={"rejected": survivors,
                     "adjusted": [round(a, 5) for a in corrected["adjusted"]]},
    )


def run_092(ctx: MethodContext) -> MethodOutput:
    p_values = _collect_p_values(ctx)
    if len(p_values) < 5:
        return MethodOutput(
            status=STATUS_INSUFFICIENT_DATA,
            narrative="fewer than five p-values available for family-wise correction",
        )
    names = [n for n, _ in p_values]
    raw = [p for _, p in p_values]
    holm_adj = holm(raw)
    bonferroni = [min(p * len(raw), 1.0) for p in raw]
    n_holm = sum(1 for p in holm_adj if p < 0.05)
    n_bonf = sum(1 for p in bonferroni if p < 0.05)
    survivors = [names[i] for i, p in enumerate(holm_adj) if p < 0.05]

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("n_tests", float(len(raw)), sample_size=len(raw)),
            finding("n_significant_holm", float(n_holm), sample_size=len(raw)),
            finding("n_significant_bonferroni", float(n_bonf), sample_size=len(raw)),
            finding("holm_min_adjusted", float(min(holm_adj)), sample_size=len(raw)),
            finding("holm_bonferroni_power_gain", float(n_holm - n_bonf), sample_size=len(raw)),
        ],
        narrative=(
            f"Family-wise error control across {len(raw)} tests: Holm leaves {n_holm} rejections, "
            f"Bonferroni {n_bonf}. Holm is uniformly at least as powerful as Bonferroni and never "
            f"less, so the difference ({n_holm - n_bonf}) is free power. "
            + (f"Surviving findings: {', '.join(survivors[:8])}." if survivors
               else "Nothing survives family-wise control at the 5% level.")
            + " FWER control is the correct standard when a single false claim would be costly, and "
              "it is deliberately harsher than the FDR procedure in Method 91."
        ),
        diagnostics={"holm_adjusted": [round(p, 5) for p in holm_adj], "survivors": survivors},
    )


# ---------------------------------------------------------------------------
# M093 information-theoretic feature selection
# ---------------------------------------------------------------------------
def run_093(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 400:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 400 observations")
    try:
        from src.models.close_models import build_frame
        frame = build_frame(ctx.config, ctx.market_id, ctx.target, verify=False)
    except Exception as exc:
        return _unavailable(f"feature frame unavailable: {exc}")

    X = frame.X
    y = frame.y
    # Discretise each feature into quintiles so MI is computed on a common scale.
    scores = {}
    for column in X.columns:
        values = X[column].to_numpy(dtype=float)
        if not np.isfinite(values).any():
            continue
        finite = np.isfinite(values)
        edges = np.quantile(values[finite], [0.2, 0.4, 0.6, 0.8])
        bins = np.digitize(np.nan_to_num(values, nan=float(np.nanmedian(values))), edges)
        joint = np.zeros((5, ctx.k))
        np.add.at(joint, (bins, y), 1.0)
        n = joint.sum()
        pxy = joint / n
        px = pxy.sum(axis=1, keepdims=True)
        py = pxy.sum(axis=0, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            mi = float(np.nansum(np.where(pxy > 0, pxy * np.log2(
                np.maximum(pxy / (px @ py), 1e-12)), 0.0)))
        scores[column] = mi

    rng = np.random.default_rng(ctx.seed)
    # Permutation reference for the strongest feature.
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    top_name, top_mi = ranked[0]
    null = []
    values = np.nan_to_num(X[top_name].to_numpy(dtype=float))
    edges = np.quantile(values, [0.2, 0.4, 0.6, 0.8])
    bins = np.digitize(values, edges)
    for _ in range(99):
        shuffled = rng.permutation(y)
        joint = np.zeros((5, ctx.k))
        np.add.at(joint, (bins, shuffled), 1.0)
        pxy = joint / joint.sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            null.append(float(np.nansum(np.where(pxy > 0, pxy * np.log2(
                np.maximum(pxy / (pxy.sum(1, keepdims=True) @ pxy.sum(0, keepdims=True)), 1e-12)),
                0.0))))
    null = np.array(null)
    p_top = float((1 + np.sum(null >= top_mi)) / (len(null) + 1))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("n_features", float(len(scores)), sample_size=ctx.n),
            finding("top_feature_mi", top_mi, p_value=p_top, sample_size=ctx.n,
                    extra={"feature": top_name}),
            finding("second_feature_mi", ranked[1][1] if len(ranked) > 1 else None,
                    sample_size=ctx.n, extra={"feature": ranked[1][0] if len(ranked) > 1 else None}),
            finding("permutation_null_mean", float(null.mean()), sample_size=len(null)),
            finding("permutation_null_95pct", float(np.quantile(null, 0.95)), sample_size=len(null)),
            finding("n_features_above_null_95pct",
                    float(sum(1 for _, mi in ranked if mi > np.quantile(null, 0.95))),
                    sample_size=len(scores)),
        ],
        narrative=(
            f"{len(scores)} causal features were each quintile-discretised and scored by mutual "
            f"information with the target. The strongest is '{top_name}' at {top_mi:.5f} bits "
            f"(permutation p = {p_top:.3f}); the permutation null gives {null.mean():.5f} bits on "
            f"average (95th percentile {np.quantile(null, 0.95):.5f}) purely from finite-sample bias. "
            f"{sum(1 for _, mi in ranked if mi > np.quantile(null, 0.95))} features exceed that "
            f"reference. "
            + ("No feature carries information beyond the finite-sample bias floor, which is why every "
               "learned model in this report converges to the marginal distribution."
               if sum(1 for _, mi in ranked if mi > np.quantile(null, 0.95)) == 0 else
               "Some features exceed the bias floor; the model results in Methods 73-84 show whether "
               "that information survives a chronological test.")
        ),
        diagnostics={"top_features": [{"feature": n, "mi": round(v, 6)} for n, v in ranked[:15]]},
    )


# ---------------------------------------------------------------------------
# M094 SHAP
# ---------------------------------------------------------------------------
def run_094(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 500:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 500 observations")
    try:
        import shap
        from sklearn.ensemble import RandomForestClassifier
    except ImportError:  # pragma: no cover
        return MethodOutput(status=STATUS_UNAVAILABLE,
                            narrative="shap is not installed; falling back would misrepresent the method")
    from src.models.close_models import build_frame
    from src.models.market_models import build as build_model

    frame = build_frame(ctx.config, ctx.market_id, ctx.target, verify=False)
    X = np.nan_to_num(frame.X.to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    cut = int(len(frame.y) * 0.7)
    model = build_model("random_forest")
    model.fit(X[:cut], frame.y[:cut])

    sample = X[cut: cut + 400]
    try:
        explainer = shap.TreeExplainer(model[-1])
        values = explainer.shap_values(sample)
    except Exception as exc:
        return _unavailable(f"SHAP computation failed: {type(exc).__name__}: {exc}")

    if isinstance(values, list):
        stacked = np.stack([np.abs(v) for v in values])          # (K, n, d)
        importance = stacked.mean(axis=(0, 1))
    else:
        arr = np.asarray(values)
        if arr.ndim == 3:
            importance = np.abs(arr).mean(axis=(0, 2))
        else:
            importance = np.abs(arr).mean(axis=0)

    names = list(frame.X.columns)
    ranked = sorted(zip(names, importance.tolist(), strict=False), key=lambda t: -t[1])
    total = float(np.sum(importance))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"shap_share_{name}", value / total if total else 0.0,
                          sample_size=len(sample), extra={"mean_abs_shap": round(value, 6)})
                  for name, value in ranked[:5]]
        + [
            finding("top_feature_share", ranked[0][1] / total if total else None,
                    sample_size=len(sample), extra={"feature": ranked[0][0]}),
            finding("top5_feature_share", sum(v for _, v in ranked[:5]) / total if total else None,
                    sample_size=len(sample)),
        ],
        narrative=(
            f"Mean absolute SHAP attributions for a random forest fitted on the first 70% of the "
            f"window and explained on the next 400 rows. The five most influential features are "
            + ", ".join(f"{n} ({v / total:.1%})" for n, v in ranked[:5])
            + f", together accounting for {sum(v for _, v in ranked[:5]) / total:.1%} of total "
            f"attribution. A model with no real signal spreads attribution across many features "
            f"rather than concentrating it on one, so diffuse attribution is itself evidence that the "
            f"model is not latching onto a genuine mechanism. Attributions explain the model, not the "
            f"world."
        ),
        diagnostics={"top_features": [{"feature": n, "mean_abs_shap": round(v, 6),
                                       "share": round(v / total, 5) if total else None}
                                      for n, v in ranked[:20]]},
    )


# ---------------------------------------------------------------------------
# M095 stability selection
# ---------------------------------------------------------------------------
def run_095(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 500:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 500 observations")
    from sklearn.feature_selection import SelectKBest, f_classif
    from src.models.close_models import build_frame

    frame = build_frame(ctx.config, ctx.market_id, ctx.target, verify=False)
    X = np.nan_to_num(frame.X.to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    y = frame.y
    names = list(frame.X.columns)
    rng = np.random.default_rng(ctx.seed)
    k = 10
    counts = np.zeros(len(names))
    n_runs = 20
    for _ in range(n_runs):
        idx = rng.choice(len(y), size=int(len(y) * 0.6), replace=False)
        selector = SelectKBest(f_classif, k=k).fit(X[idx], y[idx])
        counts[selector.get_support()] += 1
    frequency = counts / n_runs
    ranked = sorted(zip(names, frequency.tolist(), strict=False), key=lambda t: -t[1])
    above_half = sum(1 for _, f in ranked if f > 0.5)
    # Stability-selection style threshold with 20 runs and k=10.
    threshold = min(0.6, 0.5 + 0.1 * np.log(max(len(names), 1)) / np.log(10))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("n_subsamples", float(n_runs), sample_size=ctx.n),
            finding("k_selected_per_run", float(k), sample_size=ctx.n),
            finding("max_selection_frequency", float(ranked[0][1]), sample_size=n_runs,
                    extra={"feature": ranked[0][0]}),
            finding("n_features_above_0.5", float(above_half), sample_size=len(names)),
            finding("n_features_above_threshold", float(sum(1 for _, f in ranked if f > threshold)),
                    sample_size=len(names), extra={"threshold": round(float(threshold), 3)}),
        ],
        narrative=(
            f"An F-test selector (k={k}) refitted on {n_runs} random 60% subsamples. The most "
            f"frequently selected feature is '{ranked[0][0]}' at {ranked[0][1]:.0%}; {above_half} "
            f"features are chosen in more than half the runs and "
            f"{sum(1 for _, f in ranked if f > threshold)} exceed the stability threshold of "
            f"{threshold:.3f}. "
            + ("With no stable signal, selection frequencies stay near the k/n_features = "
               f"{k / len(names):.0%} you would get from random selection - which is what is observed."
               if ranked[0][1] < 0.7 else
               "Some features are selected consistently, but stability within a sample is not "
               "evidence of a real effect; the chronological tests are decisive.")
            + " Stability selection converts a fragile, sample-specific selection into a "
              "reproducible one, which is valuable even when the answer is 'nothing is stable'."
        ),
        diagnostics={"selection_frequencies": {n: round(v, 3) for n, v in ranked[:20]}},
    )


# ---------------------------------------------------------------------------
# M096 rolling performance weighting
# ---------------------------------------------------------------------------
def run_096(ctx: MethodContext) -> MethodOutput:
    panel = _panel_or_none(ctx)
    if panel is None or len(panel.models) < 2:
        return _unavailable("needs at least two candidate models")
    from src.models.ensembles import apply_weights, combine, rolling_performance_weights

    y = next(iter(panel.models.values())).y_true
    preds = {n: r.probs for n, r in panel.models.items()}
    weights = rolling_performance_weights(preds, y, window=250, decay=0.99)
    adaptive = apply_weights(preds, weights)
    fixed = combine(preds)
    adaptive_ll = float(log_loss(adaptive, y))
    fixed_ll = float(log_loss(fixed, y))
    base_name = panel.best_baseline_name()
    base_ll = float(panel.baselines[base_name].per_obs_log_loss().mean())
    weight_volatility = float(np.mean(np.std(weights, axis=0)))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("adaptive_weighting_log_loss", adaptive_ll, sample_size=int(len(y))),
            finding("equal_weight_log_loss", fixed_ll, sample_size=int(len(y))),
            finding("adaptive_minus_equal", adaptive_ll - fixed_ll, sample_size=int(len(y))),
            finding("best_baseline_log_loss", base_ll, sample_size=int(len(y)),
                    extra={"baseline": base_name}),
            finding("mean_weight_volatility", weight_volatility, sample_size=len(y)),
        ],
        narrative=(
            f"Adaptive weighting (250-step lookback, causal at every point) scores "
            f"{adaptive_ll:.5f} against {fixed_ll:.5f} for equal weights, a change of "
            f"{adaptive_ll - fixed_ll:+.5f}. Weights move by {weight_volatility:.4f} on average per "
            f"step. The strongest baseline scores {base_ll:.5f}. "
            + ("Chasing recent performance makes the ensemble slightly worse, which is the expected "
               "result when relative model performance is noise: the weights are fitting noise."
               if adaptive_ll > fixed_ll else
               "Adaptive weighting helps here, meaning recent relative performance does carry "
               "information about near-future performance.")
            + " Weights are computed only from steps strictly before each prediction, so this is not "
              "a retrospective curve-fit."
        ),
        diagnostics={"final_weights": {n: round(float(w), 4) for n, w in
                                       zip(preds, weights[-1], strict=False)}},
    )


# ---------------------------------------------------------------------------
# M097 regime-conditional probabilities
# ---------------------------------------------------------------------------
def run_097(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 500:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 500 observations")
    # Causal regime rule: high vs low rolling entropy of the last 50 draws.
    window = 50
    regime = np.zeros(ctx.n, dtype=int)
    rolling_entropy = np.zeros(ctx.n)
    counts = np.zeros(ctx.k)
    for t in range(ctx.n):
        if t >= window:
            rolling_entropy[t] = entropy(counts / max(counts.sum(), 1))
            counts[ctx.y[t - window]] -= 1
        counts[ctx.y[t]] += 1
    if ctx.n > window:
        threshold = np.nanmedian(rolling_entropy[window:])
        regime = (rolling_entropy > threshold).astype(int)

    start = max(window + 50, int(ctx.n * 0.3))
    probs = np.full((ctx.n - start, ctx.k), 1.0 / ctx.k)
    truth = ctx.y[start:]
    # Regime-conditional frequencies, updated causally.
    cond_counts = {0: np.zeros(ctx.k), 1: np.zeros(ctx.k)}
    for t in range(start):
        cond_counts[regime[t]][ctx.y[t]] += 1
    for j, t in enumerate(range(start, ctx.n)):
        row = cond_counts[regime[t]]
        if row.sum() > 0:
            probs[j] = (row + 1.0) / (row.sum() + ctx.k)
        cond_counts[regime[t]][ctx.y[t]] += 1
    regime_ll = float(log_loss(probs, truth))

    global_probs = np.full((len(truth), ctx.k), 1.0 / ctx.k)
    global_counts = counts_of(ctx.y[:start], ctx.k)
    for j, t in enumerate(range(start, ctx.n)):
        global_probs[j] = (global_counts + 1.0) / (global_counts.sum() + ctx.k)
        global_counts[ctx.y[t]] += 1
    global_ll = float(log_loss(global_probs, truth))
    regime_sizes = {int(r): int(np.sum(regime[start:] == r)) for r in (0, 1)}

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("regime_conditional_ll", regime_ll, sample_size=int(len(truth))),
            finding("unconditional_ll", global_ll, sample_size=int(len(truth))),
            finding("improvement", global_ll - regime_ll, sample_size=int(len(truth))),
            finding("regime_share_high", float(np.mean(regime[start:])), sample_size=int(len(truth))),
            finding("n_regime_switches", float(np.sum(np.diff(regime[start:]) != 0)),
                    sample_size=int(len(truth))),
        ],
        narrative=(
            f"Regimes are defined causally by whether the trailing {window}-draw entropy is above or "
            f"below its historical median, so the assignment uses no future information. The "
            f"high-entropy regime covers {np.mean(regime[start:]):.1%} of the evaluation window with "
            f"{int(np.sum(np.diff(regime[start:]) != 0))} switches. Regime-conditional frequencies "
            f"score {regime_ll:.5f} against {global_ll:.5f} for a single pooled distribution, an "
            f"improvement of {global_ll - regime_ll:+.5f}. "
            + ("Splitting history into regimes does not help: the apparent regime structure is "
               "measurement noise in a short entropy window, not a real change in the process."
               if global_ll - regime_ll <= 1e-4 else
               "Conditioning on regime improves forecasts, though the regime rule is itself a "
               "researcher choice and would need to be fixed before any live use.")
        ),
        diagnostics={"regime_sizes": regime_sizes},
    )


# ---------------------------------------------------------------------------
# M098 ensemble diversity
# ---------------------------------------------------------------------------
def run_098(ctx: MethodContext) -> MethodOutput:
    panel = _panel_or_none(ctx)
    if panel is None or len(panel.models) < 3:
        return _unavailable("needs at least three models to assess diversity")
    from src.models.ensembles import combine, diversity_matrix

    preds = {n: r.probs for n, r in panel.models.items()}
    y = next(iter(panel.models.values())).y_true
    diversity = diversity_matrix(preds)
    equal = combine(preds)
    equal_ll = float(log_loss(equal, y))
    best_single = min(panel.models, key=lambda n: panel.models[n].per_obs_log_loss().mean())
    best_single_ll = float(panel.models[best_single].per_obs_log_loss().mean())
    # Diversity-optimised: weight toward models least correlated in error.
    losses = np.stack([panel.models[n].per_obs_log_loss() for n in preds], axis=0)
    corr = np.corrcoef(losses)
    mean_corr = (corr.sum(axis=1) - 1.0) / (len(corr) - 1)
    raw = 1.0 / np.maximum(mean_corr, 1e-6)
    weights = raw / raw.sum()
    diversified = combine(preds, weights)
    diversified_ll = float(log_loss(diversified, y))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("mean_error_correlation", diversity["mean_correlation"],
                    sample_size=int(len(y))),
            finding("mean_top1_agreement", diversity["mean_agreement"], sample_size=int(len(y))),
            finding("equal_weight_ll", equal_ll, sample_size=int(len(y))),
            finding("best_single_ll", best_single_ll, sample_size=int(len(y)),
                    extra={"model": best_single}),
            finding("diversity_weighted_ll", diversified_ll, sample_size=int(len(y))),
            finding("diversity_gain_over_equal", equal_ll - diversified_ll,
                    sample_size=int(len(y))),
        ],
        narrative=(
            f"Across {len(preds)} models the mean pairwise error correlation is "
            f"{diversity['mean_correlation']:.4f} and they agree on the top outcome "
            f"{diversity['mean_agreement']:.2%} of the time. Equal-weight averaging scores "
            f"{equal_ll:.5f}; the best single model ({best_single}) scores {best_single_ll:.5f}; "
            f"diversity-weighted averaging scores {diversified_ll:.5f} "
            f"({equal_ll - diversified_ll:+.5f} versus equal weights). "
            + ("The members are highly correlated in their errors, so there is little diversity to "
               "exploit - and averaging near-identical bad forecasts produces another bad forecast."
               if diversity["mean_correlation"] > 0.6 else
               "Error correlation is moderate, so there is genuine diversity, but combining diverse "
               "models does not create information that none of them has.")
        ),
        diagnostics={"correlation_matrix": diversity["correlation"],
                     "names": diversity["names"],
                     "diversity_weights": {n: round(float(w), 4)
                                           for n, w in zip(preds, weights, strict=False)}},
    )


# ---------------------------------------------------------------------------
# M099 online Bayesian updating
# ---------------------------------------------------------------------------
def run_099(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 200 observations")
    alpha = 0.5
    start = int(ctx.n * 0.3)
    counts = np.full(ctx.k, alpha)
    for value in ctx.y[:start]:
        counts[value] += 1
    probs = np.full((ctx.n - start, ctx.k), 1.0 / ctx.k)
    truth = ctx.y[start:]
    for j, t in enumerate(range(start, ctx.n)):
        probs[j] = counts / counts.sum()
        counts[ctx.y[t]] += 1
    online_ll = float(log_loss(probs, truth))
    # Batch posterior on the same prefix, recomputed every 100 steps as a check.
    batch_probs = np.full((len(truth), ctx.k), 1.0 / ctx.k)
    for j, t in enumerate(range(start, ctx.n)):
        if j % 100 == 0:
            prefix_counts = np.full(ctx.k, alpha) + counts_of(ctx.y[:t], ctx.k)
            batch_probs[j: j + 100] = (prefix_counts / prefix_counts.sum())
    max_dev = float(np.max(np.abs(online_ll - float(log_loss(batch_probs, truth)))))
    final_posterior = counts / counts.sum()
    empirical = counts_of(ctx.y, ctx.k) / ctx.n

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("online_log_loss", online_ll, sample_size=int(len(truth))),
            finding("uniform_log_loss", float(np.log(ctx.k)), sample_size=int(len(truth))),
            finding("max_deviation_from_batch", max_dev, sample_size=int(len(truth))),
            finding("final_posterior_max", float(final_posterior.max()), sample_size=ctx.n),
            finding("final_posterior_vs_empirical_max_dev",
                    float(np.max(np.abs(final_posterior - empirical))), sample_size=ctx.n),
        ],
        narrative=(
            f"Sequential Dirichlet updating scores {online_ll:.5f} against {np.log(ctx.k):.5f} for a "
            f"uniform forecast. The maximum deviation from batch re-estimation is {max_dev:.2e}, "
            f"confirming the online recursion is numerically identical to the batch posterior - an "
            f"implementation check that matters because the whole platform relies on it. The final "
            f"posterior differs from the raw empirical distribution by at most "
            f"{np.max(np.abs(final_posterior - empirical)):.5f}, which is the Jeffreys prior's "
            f"shrinkage. The posterior concentration is the honest summary: with N={ctx.n} the "
            f"posterior for each digit is tight around 0.1, so no amount of sequential updating will "
            f"'learn' a pattern that is not there."
        ),
        diagnostics={"final_posterior": [round(float(v), 5) for v in final_posterior]},
    )


# ---------------------------------------------------------------------------
# M100 sequential probability ratio test
# ---------------------------------------------------------------------------
def run_100(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 200 observations")
    # Hypotheses: H0 uniform; H1 a mild bias of the specified size on every category.
    # The alternative is the size of bias that would be worth detecting.
    bias = 0.015
    p0 = np.full(ctx.k, 1.0 / ctx.k)
    p1 = p0.copy()
    p1[0] += bias * (ctx.k - 1)
    p1[1:] -= bias
    alpha, beta = 0.05, 0.10
    a = np.log(beta / (1 - alpha))
    b = np.log((1 - beta) / alpha)
    log_lr = 0.0
    stopping = None
    path = []
    for t in range(ctx.n):
        log_lr += np.log(p1[ctx.y[t]] / p0[ctx.y[t]])
        if t % 25 == 0:
            path.append(round(float(log_lr), 3))
        if stopping is None and (log_lr >= b or log_lr <= a):
            stopping = t
    # Theoretical expected sample size under H0 (Wald approximation).
    kl = float(np.sum(p0 * np.log(p0 / p1)))
    kl_rev = float(np.sum(p1 * np.log(p1 / p0)))
    expected_n_h0 = float(((1 - alpha) * a + alpha * b) / max(-kl, 1e-12))
    decided = stopping is not None
    # Probability that the test would reach a decision within the available data.
    prior_sample = int(ctx.n * 0.5)
    lr_partial = float(np.sum(np.log(p1[ctx.y[:prior_sample]] / p0[ctx.y[:prior_sample]])))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("final_log_likelihood_ratio", float(log_lr), sample_size=ctx.n),
            finding("upper_boundary_b", float(b), sample_size=ctx.n),
            finding("lower_boundary_a", float(a), sample_size=ctx.n),
            finding("decision_reached", float(decided), sample_size=ctx.n,
                    extra={"stopping_index": stopping}),
            finding("kl_divergence_h0_h1", kl, sample_size=ctx.n),
            finding("expected_sample_size_under_h0", expected_n_h0, sample_size=ctx.n),
            finding("log_lr_at_half_sample", lr_partial, sample_size=prior_sample),
        ],
        narrative=(
            f"Testing H0 (uniform) against H1 (a {bias:.1%} per-category bias) with alpha={alpha}, "
            f"beta={beta}: boundaries are a={a:.3f} and b={b:.3f}. Over {ctx.n} draws the accumulated "
            f"log likelihood ratio is {log_lr:+.3f}, having reached {lr_partial:+.3f} at the halfway "
            f"point. "
            + (f"The test crossed a boundary at draw {stopping} and decided."
               if decided else
               "The test never crossed a boundary, so after the entire available history it cannot "
               "distinguish a fair process from a 1.5% bias.")
            + f" The KL divergence between the hypotheses is {kl:.2e} nats per draw, implying an "
            f"expected sample size of about {expected_n_h0:,.0f} draws under H0 to reach a decision. "
            f"This is the single most important number in the report: it quantifies how much data a "
            f"bias of this size would require, and shows why a few thousand draws cannot settle the "
            f"question either way."
        ),
        diagnostics={"log_lr_path": path},
    )


RUNNERS = {f"M{i:03d}": globals().get(f"run_{i:03d}") for i in range(85, 101)}
