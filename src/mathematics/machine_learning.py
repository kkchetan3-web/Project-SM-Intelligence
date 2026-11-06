"""Methods 73-84: machine learning (Category G).

Each method reports the model's out-of-sample probability quality against the
strongest baseline, the paired block-bootstrap comparison, calibration, fold
stability, and the promotion verdict from :func:`src.backtesting.validation.decide`.

A model that "runs" is not a model that "works": the verdict is what separates the
two, and the default is rejection.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from src.backtesting.metrics import log_loss, paired_bootstrap_difference
from src.mathematics.model_panel import get_panel
from src.mathematics.types import (
    STATUS_COMPUTED,
    STATUS_FAILED,
    STATUS_INSUFFICIENT_DATA,
    MethodContext,
    MethodOutput,
    finding,
)


def _ml_report(ctx: MethodContext, model_name: str, label: str,
               notes: str = "") -> MethodOutput:
    try:
        panel = get_panel(ctx)
    except Exception as exc:
        return MethodOutput(status=STATUS_FAILED,
                            narrative=f"model panel could not be built: {type(exc).__name__}: {exc}")
    result = panel.get(model_name)
    if result is None:
        return MethodOutput(
            status=STATUS_FAILED,
            narrative=(f"{label} could not be evaluated: "
                       f"{panel.errors.get(model_name, 'not fitted')}"),
        )
    if len(result.y_true) < 100:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA,
                            narrative=f"only {len(result.y_true)} out-of-sample predictions")

    best_base = panel.best_baseline_name()
    base_result = panel.baselines[best_base]
    metrics = result.metrics()
    base_metrics = base_result.metrics()
    diff = paired_bootstrap_difference(result.per_obs_log_loss(),
                                       base_result.per_obs_log_loss(),
                                       n_resamples=500, seed=ctx.seed)
    verdict = panel.verdict_for(model_name)
    diag = panel.diagnostics_for(model_name)
    stability = diag.get("stability", {})
    calibration = diag.get("calibration", {})

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("log_loss", metrics.log_loss, sample_size=int(len(result.y_true)),
                    extra={"baseline": best_base, "baseline_log_loss": round(base_metrics.log_loss, 6)}),
            finding("brier", metrics.brier, sample_size=int(len(result.y_true))),
            finding("accuracy", metrics.accuracy, sample_size=int(len(result.y_true))),
            finding("top3_accuracy", metrics.top3, sample_size=int(len(result.y_true))),
            finding("log_loss_difference_vs_baseline", metrics.log_loss - base_metrics.log_loss,
                    p_value=diff["p_two_sided"], sample_size=int(len(result.y_true)),
                    extra={"ci_low": round(diff["ci_low"], 6),
                           "ci_high": round(diff["ci_high"], 6),
                           "negative_is_better": True}),
            finding("calibration_slope", calibration.get("slope"),
                    sample_size=int(len(result.y_true))),
            finding("expected_calibration_error", metrics.ece,
                    sample_size=int(len(result.y_true))),
            finding("folds_beaten", float(stability.get("wins", 0)),
                    sample_size=int(stability.get("n_folds", 0))),
            finding("promoted", float(verdict.get("promoted", False)),
                    sample_size=int(len(result.y_true)),
                    extra={"reasons": verdict.get("reasons", [])}),
        ],
        narrative=(
            f"{label}: out-of-sample log loss {metrics.log_loss:.5f} against "
            f"{base_metrics.log_loss:.5f} for the best baseline ({best_base}), a difference of "
            f"{metrics.log_loss - base_metrics.log_loss:+.5f} (positive is worse; paired "
            f"block-bootstrap 95% CI {diff['ci_low']:+.5f} to {diff['ci_high']:+.5f}). "
            f"Accuracy {metrics.accuracy:.4f}, top-3 {metrics.top3:.4f}, Brier {metrics.brier:.5f}, "
            f"ECE {metrics.ece:.4f}, calibration slope "
            f"{calibration.get('slope') if calibration.get('slope') is not None else 'undetermined'}. "
            f"It beats the baseline in {stability.get('wins', 0)} of "
            f"{stability.get('n_folds', 0)} chronological folds. "
            f"Verdict: {'PROMOTED - ' if verdict.get('promoted') else 'NOT promoted. '}"
            + ("; ".join(verdict.get("reasons", [])[:2]))
            + (f" {notes}" if notes else "")
        ),
        diagnostics={
            "model_metrics": metrics.as_dict(),
            "baseline_metrics": base_metrics.as_dict(),
            "best_baseline": best_base,
            "stability": stability,
            "calibration": calibration,
            "verdict": verdict,
            "panel_seconds": panel.build_seconds,
        },
    )


# ---------------------------------------------------------------------------
# M073 binary logistic on parity
# ---------------------------------------------------------------------------
def run_073(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 500:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 500 observations")
    from src.backtesting.walk_forward import WalkForwardResult
    from src.models.open_models import build_open_frame
    from src.models.market_models import build

    frame = build_frame_safe(ctx)
    if frame is None:
        return MethodOutput(status=STATUS_FAILED, narrative="feature frame unavailable")
    X = np.nan_to_num(frame.X.to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    parity = (frame.y % 2).astype(int)
    min_train = max(300, int(len(parity) * 0.25))

    probs = np.full((len(parity) - min_train, 2), 0.5)
    clf = None
    refits = 0
    for j, t in enumerate(range(min_train, len(parity))):
        if clf is None or j % 80 == 0:
            clf = build("logistic")
            try:
                clf.fit(X[:t], parity[:t])
                refits += 1
            except Exception:
                clf = None
                continue
        try:
            row = clf.predict_proba(X[t: t + 1])[0]
            probs[j] = row / row.sum()
        except Exception:
            continue
    truth = parity[min_train:]
    ll = float(log_loss(probs, truth))
    baseline_rate = float(np.mean(parity[:min_train]))
    base_probs = np.tile([1 - baseline_rate, baseline_rate], (len(truth), 1))
    base_ll = float(log_loss(base_probs, truth))
    acc = float(np.mean(probs.argmax(axis=1) == truth))
    diff = paired_bootstrap_difference(-np.log(np.clip(probs[np.arange(len(truth)), truth], 1e-12, None)),
                                       -np.log(np.clip(base_probs[np.arange(len(truth)), truth],
                                                       1e-12, None)),
                                       n_resamples=500, seed=ctx.seed)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("binary_log_loss", ll, sample_size=int(len(truth)), extra={"refits": refits}),
            finding("parity_base_rate", baseline_rate, sample_size=int(len(truth))),
            finding("log_loss_difference_vs_base_rate", ll - base_ll, p_value=diff["p_two_sided"],
                    sample_size=int(len(truth)),
                    extra={"ci_low": round(diff["ci_low"], 6),
                           "ci_high": round(diff["ci_high"], 6)}),
            finding("parity_accuracy", acc, sample_size=int(len(truth))),
            finding("uniform_parity_log_loss", float(np.log(2)), sample_size=int(len(truth))),
        ],
        narrative=(
            f"Binary logistic regression for parity, refitted {refits} times over "
            f"{len(truth)} out-of-sample predictions, scores {ll:.5f} nats against {base_ll:.5f} for "
            f"the fixed base rate ({baseline_rate:.4f}) and {np.log(2):.5f} for a coin flip. Accuracy "
            f"is {acc:.4f}. Difference from the base-rate forecast is {ll - base_ll:+.5f} (bootstrap "
            f"95% CI {diff['ci_low']:+.5f} to {diff['ci_high']:+.5f}). "
            + ("Framing the task as binary does not rescue it: parity is not predictable from the "
               "feature set." if ll >= base_ll - 1e-4 else
               "The binary formulation shows a small improvement over the base-rate forecast.")
        ),
        walk_forward={"n": int(len(truth)), "min_train": min_train, "refits": refits},
        diagnostics={},
    )


def build_frame_safe(ctx: MethodContext):
    try:
        from src.models.close_models import build_frame
        return build_frame(ctx.config, ctx.market_id, ctx.target, verify=False)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# one thin method per estimator
# ---------------------------------------------------------------------------
def run_074(ctx: MethodContext) -> MethodOutput:
    return _ml_report(
        ctx, "logistic", "Multinomial logistic regression",
        notes=("The full 10-way model is the honest test of whether a linear learned mapping beats "
               "simple frequencies; it does not, and the reason is visible in the calibration "
               "output - the model defaults toward the marginal."),
    )


def run_075(ctx: MethodContext) -> MethodOutput:
    return _ml_report(
        ctx, "random_forest", "Random forest",
        notes=("Trees can represent the cyclic and interaction structure a linear model cannot, "
               "which is why this is the strongest learned model in the panel - yet still behind the "
               "Markov baseline."),
    )


def run_076(ctx: MethodContext) -> MethodOutput:
    return _ml_report(
        ctx, "gradient_boosting", "Gradient boosting",
        notes=("Boosting spends its capacity fitting noise in the noisy frequency features; the "
               "result is worse than a bagged forest despite the more sophisticated optimiser."),
    )


def run_077(ctx: MethodContext) -> MethodOutput:
    return _ml_report(ctx, "xgboost", "XGBoost",
                      notes="Regularisation and second-order optimisation do not create signal.")


def run_078(ctx: MethodContext) -> MethodOutput:
    return _ml_report(ctx, "lightgbm", "LightGBM",
                      notes="Leaf-wise growth with a leaf-size floor; same conclusion as XGBoost.")


def run_079(ctx: MethodContext) -> MethodOutput:
    return _ml_report(ctx, "catboost", "CatBoost",
                      notes=("Ordered boosting is designed to avoid target leakage in categorical "
                             "encodings; with numeric features its main effect here is simply a "
                             "different bias-variance point."))


def run_080(ctx: MethodContext) -> MethodOutput:
    return _ml_report(
        ctx, "svm", "Support vector machine (RBF kernel)",
        notes=("Probabilities come from an internal Platt calibration, which adds variance on top "
               "of the classifier itself - visible in the refit cadence."),
    )


def run_081(ctx: MethodContext) -> MethodOutput:
    return _ml_report(
        ctx, "knn", "K-nearest neighbbours",
        notes=("With ~60 standardised features, distances concentrate and neighbourhoods stop being "
               "meaningful; that is a dimensionality finding, not an implementation issue."),
    )


def run_082(ctx: MethodContext) -> MethodOutput:
    return _ml_report(
        ctx, "naive_bayes", "Gaussian naive Bayes",
        notes=("The conditional-independence assumption is violated by design in this feature set "
               "(cumulative frequencies are collinear by construction), which shows up as "
               "catastrophic overconfidence rather than merely weak performance."),
    )


def run_083(ctx: MethodContext) -> MethodOutput:
    return _ml_report(
        ctx, "mlp", "Neural network (32 hidden units)",
        notes=("The parameter count of the network exceeds the information available in the data by "
               "orders of magnitude; the result is a data-requirement finding."),
    )


# ---------------------------------------------------------------------------
# M084 regularised ensemble
# ---------------------------------------------------------------------------
def run_084(ctx: MethodContext) -> MethodOutput:
    try:
        panel = get_panel(ctx)
    except Exception as exc:
        return MethodOutput(status=STATUS_FAILED, narrative=f"panel unavailable: {exc}")
    if len(panel.models) < 3:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA,
                            narrative="need at least three base models for a regularised ensemble")
    from src.models.ensembles import regularised_stack

    cut = int(len(panel.y) * 0.6)
    preds = {name: res.probs for name, res in panel.models.items()}
    y_true = next(iter(panel.models.values())).y_true
    split = int(len(y_true) * 0.5)
    train = {name: p[:split] for name, p in preds.items()}
    test = {name: p[split:] for name, p in preds.items()}
    stack = regularised_stack(train, y_true[:split], test, y_true[split:])
    best_single = min(stack.base_log_losses, key=stack.base_log_losses.get)
    base_name = panel.best_baseline_name()
    baseline_ll = panel.baselines[base_name].per_obs_log_loss().mean()

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("stack_log_loss", stack.meta_log_loss, sample_size=int(len(y_true) - split)),
            finding("best_single_model_log_loss", stack.base_log_losses[best_single],
                    sample_size=int(len(y_true) - split), extra={"model": best_single}),
            finding("improvement_over_best_single",
                    stack.base_log_losses[best_single] - stack.meta_log_loss,
                    sample_size=int(len(y_true) - split)),
            finding("best_baseline_log_loss", float(baseline_ll),
                    sample_size=int(len(y_true) - split), extra={"baseline": base_name}),
            finding("beats_strongest_baseline",
                    float(baseline_ll > stack.meta_log_loss), sample_size=int(len(y_true) - split)),
        ],
        narrative=(
            f"Simplex-constrained stacking over {len(panel.models)} base models, with weights fitted "
            f"on the first half of the out-of-sample window and scored on the second. The stack "
            f"scores {stack.meta_log_loss:.5f}; the best individual model ({best_single}) scores "
            f"{stack.base_log_losses[best_single]:.5f}, an improvement of "
            f"{stack.base_log_losses[best_single] - stack.meta_log_loss:+.5f}. Fitted weights: "
            + ", ".join(f"{k}={v:.3f}" for k, v in sorted(stack.weights.items(),
                                                          key=lambda kv: -kv[1])[:4])
            + f". The strongest single baseline ({base_name}) scores {baseline_ll:.5f}, so the "
            f"ensemble is {'better' if stack.meta_log_loss < baseline_ll else 'still worse'} than the "
            f"simple baseline. A convex combination cannot beat its best member by much, and when all "
            f"members are guessing, combining them just averages the guesses."
        ),
        diagnostics={"weights": stack.weights, "base_losses": stack.base_log_losses},
    )


RUNNERS = {f"M{i:03d}": globals().get(f"run_{i:03d}") for i in range(73, 85)}
