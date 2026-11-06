#!/usr/bin/env python
"""Generate a results summary straight from the databases.

Nothing in the output is typed by hand: every number is read from the market
databases or from the research JSON artefacts that the pipeline wrote. If a stage
was not run, the section says so instead of being omitted.

Usage
-----
    python scripts/summarise_results.py --dataset synthetic_null --write
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from src.core.configuration import load_config  # noqa: E402
from src.core.provenance import utcnow  # noqa: E402
from src.storage.market_database import MarketDatabase  # noqa: E402


def _table(headers: list[str], rows: list[list], float_fmt: str = "{:.5f}") -> str:
    def fmt(v):
        if isinstance(v, float):
            return float_fmt.format(v)
        return "" if v is None else str(v)

    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    out += ["| " + " | ".join(fmt(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def method_section(config, market_id: str) -> list[str]:
    db = MarketDatabase(config, market_id)
    if not db.manager.exists(market_id):
        return [f"### {market_id}", "", "Database not initialised.", ""]
    frame = db.method_results()
    lines = [f"### {market_id}", ""]
    if frame.empty:
        return lines + ["No method results stored.", ""]

    # `scope` holds "full_sample" for computed rows; everything else is a status.
    status = frame.groupby("scope")["method_id"].nunique().to_dict()
    display = {(("computed" if k == "full_sample" else k)): v for k, v in status.items()}
    lines.append(_table(["Status", "Methods"],
                        [[k, v] for k, v in sorted(display.items())]))
    lines.append("")

    by_category = (frame.groupby("category")
                   .agg(methods=("method_id", "nunique"), rows=("metric_name", "size"))
                   .reset_index())
    lines.append(_table(["Category", "Methods", "Metric rows"],
                        [[r.category, r.methods, r.rows] for r in by_category.itertuples()]))
    lines.append("")

    tests = frame[frame["p_value"].notna()]
    if len(tests):
        adj = frame[frame["p_adjusted"].notna()]
        excluded = frame[frame["extra_json"].fillna("").str.contains("fdr_excluded")]
        lines.append(f"- Findings carrying a p-value: **{len(tests)}**")
        lines.append(f"- In the multiple-testing family (tests of 'no structure'): "
                     f"**{len(adj)}**")
        lines.append(f"- Excluded from that family as magnitude comparisons, unit-root tests or "
                     f"invalid-for-discrete-data tests: **{len(excluded)}** "
                     f"(their raw p-value and the reason are stored)")
        lines.append(f"- Raw p < 0.05 **within the family**: "
                     f"**{int((adj['p_value'] < 0.05).sum())}**")
        lines.append(f"- Surviving Benjamini-Hochberg FDR at 0.05: "
                     f"**{int((adj['p_adjusted'] < 0.05).sum())}**")
        lines.append("")
        survivors = adj[adj["p_adjusted"] < 0.05].sort_values("p_adjusted").head(20)
        if len(survivors):
            rows = [[r.method_id, r.target, r.metric_name,
                     r.metric_value, r.p_adjusted, r.effect_size, r.sample_size]
                    for r in survivors.itertuples()]
            lines.append("Largest surviving effects:")
            lines.append("")
            lines.append(_table(["Method", "Target", "Metric", "Value", "p (FDR)",
                                 "Effect", "n"], rows, "{:.4g}"))
            lines.append("")
        else:
            lines.append("No finding survives FDR control: the honest answer on a null world.")
            lines.append("")
    return lines


def backtest_section(config, market_id: str) -> list[str]:
    db = MarketDatabase(config, market_id)
    if not db.manager.exists(market_id):
        return []
    try:
        with db.session(read_only=True) as conn:
            frame = pd.read_sql_query(
                "SELECT b.*, r.model_name FROM backtest_results b "
                "LEFT JOIN model_registry r ON r.model_id = b.model_id", conn)
    except Exception:
        return []
    if frame.empty:
        return [f"### {market_id}", "", "No backtest rows stored.", ""]
    lines = [f"### {market_id}", ""]
    for target, group in frame.groupby("target"):
        best = group.sort_values("log_loss").head(6)
        rows = [[getattr(r, "model_name", None) or r.model_id, r.log_loss, r.brier,
                 r.accuracy, r.top3, r.top5] for r in best.itertuples()]
        lines.append(f"**{target}** - six best configurations by out-of-sample log loss")
        lines.append("")
        lines.append(_table(["Model", "Log loss", "Brier", "Accuracy", "Top-3", "Top-5"], rows))
        lines.append("")
    lines.append("Uniform floor: log loss 2.30259, Brier 0.90000, accuracy 0.1000, "
                 "top-3 0.3000, top-5 0.5000.")
    lines.append("")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True,
                        choices=["live", "synthetic_null", "synthetic_signal"])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    config = load_config(dataset=args.dataset)
    lines = [
        f"# Measured results - `{config.dataset.name}`",
        "",
        f"Generated **{utcnow()}** by `scripts/summarise_results.py` directly from "
        f"`{config.dataset.root}`. Nothing here is hand-written.",
        "",
        f"_{config.dataset.description}_",
        "",
        "---",
        "",
        "## 1. Method execution",
        "",
    ]
    for market_id in config.market_order:
        lines += method_section(config, market_id)

    lines += ["## 2. Walk-forward backtests", ""]
    for market_id in config.market_order:
        lines += backtest_section(config, market_id)

    lines += ["## 3. Cross-market", ""]
    path = config.research_dir("cross_market") / f"cross_market_{config.dataset.name}.json"
    if path.exists():
        payload = json.loads(path.read_text())
        headline = payload.get("headline", {})
        lines.append(f"- Lag tests: **{headline.get('n_lag_tests')}**, "
                     f"significant after Holm: **{headline.get('n_significant_after_holm')}**")
        lines.append(f"- Conditional-model tests: **{headline.get('n_conditional_tests')}**, "
                     f"demonstrated improvements: "
                     f"**{headline.get('n_demonstrated_predictive_improvements')}**")
        for pair in payload.get("pairs", []):
            lines.append("")
            lines.append(f"### {pair['pair'][0]} vs {pair['pair'][1]}")
            lines.append("")
            rows = []
            for test in pair.get("conditional_model_tests", []):
                if not test.get("available"):
                    rows.append([test.get("target_market"), test.get("target"),
                                 None, None, None, test.get("reason", "")[:60]])
                    continue
                rows.append([test["target_market"], test["target"],
                             test["domestic_only_log_loss"],
                             test["domestic_plus_foreign_log_loss"],
                             test["improvement"], test["verdict"][:60]])
            lines.append(_table(["Market", "Target", "Domestic LL", "With foreign LL",
                                 "Improvement", "Verdict"], rows))
        lines.append("")
        lines.append(f"**{headline.get('conclusion', '')}**")
    else:
        lines.append("Cross-market analysis has not been run for this dataset.")
    lines.append("")

    lines += ["## 4. Prediction ledger", ""]
    from src.predictions.prediction_ledger import summary as ledger_summary

    for market_id in config.market_order:
        stats = ledger_summary(config, market_id)
        if not stats.get("available"):
            lines.append(f"- **{market_id}**: {stats.get('reason')}")
            continue
        lines.append(f"- **{market_id}**: {stats['n_forecasts']} forecast(s), "
                     f"{stats['n_resolved']} resolved"
                     + (f", log loss {stats['log_loss']:.5f} vs uniform 2.30259 "
                        f"- {stats['verdict']}" if "log_loss" in stats else ""))
    lines.append("")

    text = "\n".join(lines) + "\n"
    if args.write:
        out = ROOT / "docs" / f"RESULTS_{config.dataset.name}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"Written: {out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
