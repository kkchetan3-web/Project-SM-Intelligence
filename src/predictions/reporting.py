"""Human-readable prediction outputs.

Two hard rules, both enforced here rather than trusted to callers:

1. **One market per report.** :func:`render_forecast` renders exactly the market it
   was given and refuses to include any other. A multi-market view exists only as
   :func:`render_comparison`, which is a separate, explicitly-requested function.
2. **No advice.** Every report states the measured accuracy and the fact that these
   draws are not known to be predictable. Probabilities are described as model
   output, never as a recommendation to stake money.
"""

from __future__ import annotations

import math
from typing import Iterable

from src.predictions.prediction_engine import Forecast

DISCLAIMER = (
    "> This is a statistical research output, not a prediction service or betting advice. "
    "No method in this platform has demonstrated a reliable out-of-sample edge. "
    "Past frequencies do not imply future probabilities, and chasing losses is never rational."
)


def _bar(p: float, width: int = 24) -> str:
    filled = int(round(p * width * 4))  # 0.25 is the uniform level
    return "#" * min(filled, width) + "-" * max(width - filled, 0)


def render_forecast(forecast: Forecast) -> str:
    """Single-market forecast report."""
    lines: list[str] = []
    model_note = ("a model that passed walk-forward promotion"
                  if forecast.has_demonstrated_edge else
                  "a baseline distribution (no candidate model passed promotion)")
    lines.append(f"# {forecast.market_id.replace('_', ' ').title()} - {forecast.target.title()} forecast")
    lines.append("")
    lines.append(f"- **Draw date:** {forecast.target_date}")
    lines.append(f"- **Data cutoff:** {forecast.cutoff_date} "
                 f"({forecast.n_history} observed draws)")
    lines.append(f"- **Forecaster:** `{forecast.model_name}` - {model_note}")
    dataset_note = (
        "real published results imported from the 2026-11-07 chart snapshots "
        "(single-provider, unverified_scrape)"
        if forecast.dataset == "live" else
        "synthetic control data - not real historical results")
    lines.append(f"- **Dataset:** `{forecast.dataset}` ({dataset_note})")
    lines.append(f"- **Feature version:** `{forecast.feature_version}`")
    lines.append("")
    lines.append("## Probability by outcome")
    lines.append("")
    lines.append("| Outcome | Probability | vs uniform (0.1000) | |")
    lines.append("|---:|---:|---:|:--|")
    for label, p in forecast.ranked:
        lines.append(f"| {label} | {p:.4f} | {p - 0.1:+.4f} | `{_bar(p)}` |")
    lines.append("")
    total = sum(forecast.probs.values())
    lines.append(f"Probabilities sum to {total:.6f}. Uniform would give 0.1000 for every outcome; "
                 f"the spread above uniform is the model's entire claimed information content.")
    lines.append("")
    lines.append("## What this number means")
    lines.append("")
    edge = forecast.edge_evidence.get("selection", {})
    best_ll = edge.get("baseline_log_loss")
    lines.append(
        f"The best baseline available for this market and target has a walk-forward log loss of "
        f"{best_ll:.5f} against a uniform floor of {math.log(10):.5f}. Any forecast that cannot "
        f"beat that baseline is, for practical purposes, a slightly shaped version of "
        f"'every outcome is equally likely'."
        if best_ll is not None else
        "No baseline comparison is recorded for this forecast."
    )
    lines.append("")
    if forecast.notes:
        lines.append("## Method notes")
        lines.append("")
        for note in forecast.notes:
            lines.append(f"- {note}")
        lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    if forecast.has_demonstrated_edge:
        lines.append("The forecaster passed the promotion rule on historical walk-forward data. "
                     "That is a statement about the past, on this dataset, under this feature set; "
                     "it is not a guarantee about this draw.")
    else:
        lines.append("No model demonstrated a predictive edge for this market and target, so no "
                     "model is being used. The reported vector is the best-performing naive rule. "
                     "It should be read as 'the market's recent empirical distribution', not as a "
                     "forecast with information.")
    lines.append("")
    lines.append(DISCLAIMER)
    return "\n".join(lines)


def render_ledger(summary: dict) -> str:
    market = summary.get("market", "unknown").replace("_", " ").title()
    lines = [f"# {market} - prediction ledger", ""]
    if not summary.get("available"):
        lines.append(f"No ledger available: {summary.get('reason', 'unknown reason')}.")
        return "\n".join(lines)

    lines.append(f"- Forecasts recorded: **{summary['n_forecasts']}**")
    lines.append(f"- Resolved: **{summary['n_resolved']}** "
                 f"(pending: {summary['n_pending']})")
    if "log_loss" not in summary:
        lines.append("")
        lines.append(f"{summary.get('reason', 'Nothing to score yet.')}")
        return "\n".join(lines)

    lines += [
        "",
        "| Metric | Realised | Uniform floor | Difference |",
        "|---|---:|---:|---:|",
        f"| Log loss | {summary['log_loss']:.5f} | {summary['uniform_log_loss']:.5f} "
        f"| {summary['edge_vs_uniform_log_loss']:+.5f} |",
        f"| Brier | {summary['brier']:.5f} | {summary['uniform_brier']:.4f} "
        f"| {summary['edge_vs_uniform_brier']:+.5f} |",
        f"| Exact hit rate | {summary['exact_hit_rate']:.4f} | 0.1000 "
        f"| {summary['edge_vs_uniform_hit_rate']:+.4f} |",
        f"| Top-3 rate | {summary['top3_rate']:.4f} | 0.3000 | - |",
        "",
        f"Hit-rate z-score against 0.1: {summary.get('hit_rate_z_vs_uniform')}",
        "",
        f"**Verdict:** {summary['verdict']}",
        "",
        DISCLAIMER,
    ]
    return "\n".join(lines)


def render_comparison(forecasts: Iterable[Forecast]) -> str:
    """Side-by-side view - only for an explicit multi-market request."""
    forecasts = list(forecasts)
    if len(forecasts) < 2:
        raise ValueError("a comparison needs at least two forecasts; "
                         "single-market output must use render_forecast")
    lines = ["# Cross-market forecast comparison (explicitly requested)", ""]
    lines.append("| Market | Target | Forecaster | Top outcome | P(top) | Mode |")
    lines.append("|---|---|---|---|---:|---|")
    for f in forecasts:
        top_label, top_p = f.ranked[0]
        display = f.market_id.replace("_", " ").title()
        lines.append(f"| {display} | {f.target} | `{f.model_name}` | {top_label} "
                     f"| {float(top_p):.4f} | {f.mode} |")
    lines.append("")
    lines.append("Markets are modelled independently. This table places their outputs next to "
                 "each other; it does not combine them, and no cross-market signal was found to "
                 "justify blending.")
    lines.append("")
    lines.append(DISCLAIMER)
    return "\n".join(lines)
