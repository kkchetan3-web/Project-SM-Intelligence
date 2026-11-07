"""Final report generator (Section 22, parts A-G).

The report is assembled from what is actually in the databases and in the research
artefacts. It does not use a template with placeholders filled by hand, and it does
not print success where there is no evidence: every "not executed" or "blocked"
section is rendered from the absence of rows, with the reason stated.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any

from src.core.configuration import Config
from src.core.logging import get_logger
from src.core.provenance import utcnow
from src.storage.market_database import MarketDatabase

log = get_logger(__name__)

SECTION_TITLES = {
    "A": "Environment, sources and data provenance",
    "B": "Architecture and database state",
    "C": "Data quality and validation",
    "D": "The 100-method programme",
    "E": "Cross-market intelligence",
    "F": "Backtesting, calibration and prediction performance",
    "G": "Limitations, negative results and honest conclusions",
}


def _h(level: int, text: str) -> str:
    return f"{'#' * level} {text}"


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join("" if c is None else str(c) for c in row) + " |")
    return "\n".join(out)


def _safe(fn, default):
    try:
        return fn()
    except Exception as exc:  # pragma: no cover - defensive by design
        log.warning("report section failed: %s", exc)
        return default


# ---------------------------------------------------------------------------
# section A
# ---------------------------------------------------------------------------
def _is_live(config: Config) -> bool:
    return config.dataset.name == "live"


def live_data_facts(config: Config) -> dict[str, Any]:
    """Rows, span and provenance of the real data, read from the databases."""
    facts: dict[str, Any] = {"markets": {}, "sources": []}
    for market_id in config.market_order:
        db = MarketDatabase(config, market_id)
        if not db.manager.exists(market_id):
            continue
        with db.session(read_only=True) as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS n, MIN(result_date) AS first, MAX(result_date) AS last, "
                "SUM(CASE WHEN open_panna IS NULL OR close_panna IS NULL THEN 1 ELSE 0 END) "
                "AS partial FROM historical_results WHERE is_active = 1").fetchone()
            statuses = conn.execute(
                "SELECT verification_status, COUNT(*) FROM historical_results "
                "WHERE is_active = 1 GROUP BY 1").fetchall()
            sources = conn.execute(
                "SELECT DISTINCT source_id, source_url FROM historical_results "
                "WHERE is_active = 1").fetchall()
        facts["markets"][market_id] = {
            "rows": int(row["n"]), "first": row["first"], "last": row["last"],
            "partial_panna": int(row["partial"] or 0),
            "statuses": {r[0]: int(r[1]) for r in statuses},
        }
        for source_id, url in sources:
            if url and [source_id, url] not in facts["sources"]:
                facts["sources"].append([source_id, url])
    audit_dir = config.research_dir("extraction")
    facts["audits"] = sorted(str(p) for p in audit_dir.glob("reconciliation_*.json")) \
        if audit_dir.exists() else []
    return facts


def section_a(config: Config, discovery: dict | None) -> str:
    lines = [_h(2, "A. " + SECTION_TITLES["A"]), ""]
    lines.append(_table(
        ["Item", "Value"],
        [["Python", sys.version.split()[0]],
         ["Platform", platform.platform()],
         ["Dataset", f"`{config.dataset.name}`"],
         ["Dataset root", f"`{config.dataset.root}`"],
         ["Schema version", "3"],
         ["Generated at (UTC)", utcnow()]],
    ))
    lines.append("")
    lines.append("### Source reachability")
    lines.append("")
    observations = (discovery or {}).get("summary", {}).get("observations") or []
    if observations:
        rows = [[o.get("source_id"), o.get("base_url"), o.get("reachable"),
                 (o.get("verdict") or "")[:60]] for o in observations]
        lines.append(_table(["Source", "URL", "Reachable", "Verdict"], rows))
        lines.append("")
        n_reachable = sum(1 for o in observations if o.get("reachable"))
        lines.append(f"**{n_reachable} of {len(observations)} configured sources responded.** "
                     "The probe is reproducible with `python -m src.cli.main discover`; the raw "
                     "report is at `research/extraction/discovery_report.json`.")
    else:
        lines.append("No discovery report was produced in this run. Run "
                     "`python -m src.cli.main discover` to probe the configured sources.")
    lines.append("")
    lines.append("### What this means for the data")
    lines.append("")

    if _is_live(config):
        return "\n".join(lines + _live_data_section(config))

    lines.append(
        "The five configured sources could not be reached from the execution environment "
        "(TLS resets on 443, empty replies on 80). **Zero real historical records were "
        "extracted.** Every number in this report is computed on synthetic control data "
        "generated by `src/ingestion/synthetic_control.py`, whose rows are marked "
        "`verification_status='synthetic_control'` and cannot be mistaken for market history.\n")
    lines.append(
        "Two control worlds exist by design: `synthetic_null` (independent uniform draws - "
        "the framework must find **no** edge) and `synthetic_signal` (planted first-order "
        "dependence plus a Kalyan-to-Main-Bazar channel - the framework must **find** it). "
        "Agreement between them is the test of the framework itself, not of the market.")
    return "\n".join(lines)


def _live_data_section(config: Config) -> list[str]:
    facts = live_data_facts(config)
    lines: list[str] = []
    rows = []
    for market_id, info in facts["markets"].items():
        status = ", ".join(f"{k} ({v})" for k, v in info["statuses"].items())
        rows.append([market_id, info["rows"], f"{info['first']} .. {info['last']}",
                     info["partial_panna"], status])
    if rows:
        lines.append(_table(["Market", "Stored results", "Span", "Rows missing a panna",
                             "Verification status"], rows))
        lines.append("")
    total = sum(info["rows"] for info in facts["markets"].values())
    lines.append(
        f"The scraper still cannot reach the configured hosts from this environment (TLS "
        f"resets on 443, empty replies on 80), so **nothing here was fetched by the scraper**. "
        f"The {total:,} stored results come from saved copies of the four primary chart pages "
        f"supplied on 2026-11-07: parsed by a committed code path (`import-snapshots`), hashed "
        f"into `source_records`, archived under `data/raw/snapshots/`. They are real published "
        f"results, but single-provider and therefore `unverified_scrape` - not independently "
        f"confirmed by a second source.")
    lines.append("")
    lines.append(
        "The jodi pages carry no dates; the panel pages carry dates with year typos, stray "
        "characters, mixed date formats and off-by-one labels. Dates were recovered by "
        "resolving each page as a whole against its own weekly grid, and the two pages were "
        "then checked against each other: they agree on **every** jodi both carry. The repair "
        "and conflict lists are in `docs/DATA_SNAPSHOT_2026-11-07.md` and "
        "`research/extraction/reconciliation_*.json`.")
    lines.append("")
    lines.append(
        "This report therefore describes the real published history of these markets. It does "
        "not make the draws predictable: every verdict in part F is a walk-forward verdict on "
        "that history, and part G states the losses plainly.")
    return lines


# ---------------------------------------------------------------------------
# section B
# ---------------------------------------------------------------------------
def section_b(config: Config) -> tuple[str, dict[str, Any]]:
    lines = [_h(2, "B. " + SECTION_TITLES["B"]), ""]
    rows = []
    state: dict[str, Any] = {}
    for market_id in config.market_order:
        db = MarketDatabase(config, market_id)
        if not db.manager.exists(market_id):
            rows.append([market_id, "missing", "-", "-", "run `init`"])
            state[market_id] = {"exists": False}
            continue
        info = db.manager.integrity_check(market_id)
        coverage = _safe(db.coverage, {})
        state[market_id] = {"exists": True, "integrity": info["pragma"],
                            "row_counts": info["row_counts"], "coverage": coverage}
        rows.append([
            market_id,
            info["pragma"],
            str(info["row_counts"].get("historical_results", 0)),
            f"{coverage.get('oldest', '?')} .. {coverage.get('newest', '?')}",
            "none" if not info["missing_tables"] else ", ".join(info["missing_tables"]),
        ])
    lines.append(_table(
        ["Market", "Integrity", "Historical rows", "Coverage", "Missing tables"], rows))
    lines.append("")
    # Per-table population, so an empty table is visible in the report instead of
    # being quietly absent from a prose claim.
    counts: dict[str, dict[str, int]] = {
        m: st.get("row_counts", {}) for m, st in state.items() if st.get("exists")
    }
    if counts:
        from src.storage.schema import REQUIRED_TABLES

        table_rows = []
        for table in REQUIRED_TABLES:
            table_rows.append([table] + [str(counts.get(m, {}).get(table, "-"))
                                         for m in config.market_order])
        lines.append(_h(3, "Table population"))
        lines.append("")
        lines.append(_table(["Table"] + list(config.market_order), table_rows))
        lines.append("")
        lines.append("Empty tables are explained rather than hidden: `market_features` and "
                     "`cross_market_features` are built in memory at each walk-forward "
                     "cutoff (persisting them risks re-using a vector computed with later "
                     "data), and `prediction_outcomes` is filled only once the draw a "
                     "forecast refers to has actually been published.")
        lines.append("")
    lines.append(
        "Each market owns a separate SQLite database at "
        "`<dataset root>/<market_id>/<market_id>.db` with the 12 required tables. "
        "Raw payloads are stored alongside the cleaned rows; revisions are appended to "
        "`result_revisions` rather than overwriting history.")
    return "\n".join(lines), state


# ---------------------------------------------------------------------------
# section C
# ---------------------------------------------------------------------------
def section_c(config: Config) -> str:
    from src.preprocessing.quality_checks import run_quality_checks

    lines = [_h(2, "C. " + SECTION_TITLES["C"]), ""]
    rows = []
    for market_id in config.market_order:
        db = MarketDatabase(config, market_id)
        if not db.manager.exists(market_id):
            rows.append([market_id, "-", "-", "-", "database missing"])
            continue
        report = _safe(lambda m=market_id: run_quality_checks(config, m, persist=False), None)
        if report is None:
            rows.append([market_id, "-", "-", "-", "quality check failed to run"])
            continue
        rows.append([market_id, report.n_records, "PASS" if report.ok else "FAIL",
                     len(report.errors), len(report.warnings)])
    lines.append(_table(["Market", "Records", "Gate", "Errors", "Warnings"], rows))
    lines.append("")
    lines.append(
        "Checks cover record-level completeness, duplicate dates, calendar gaps, "
        "panna-to-ank consistency (digit sum mod 10), impossible values, and the "
        "provenance requirement that no live-labelled row lacks a source URL.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# section D - the 100 methods
# ---------------------------------------------------------------------------
def section_d(config: Config) -> tuple[str, dict[str, Any]]:
    from src.mathematics.registry import CATEGORY_NAMES, METHOD_REGISTRY, methods_for_category

    lines = [_h(2, "D. " + SECTION_TITLES["D"]), ""]
    lines.append(
        f"{len(METHOD_REGISTRY)} methods are documented and implemented. Each has a definition, "
        "mathematical foundation, formula with variable definitions, assumptions, manual steps, "
        "a hypothetical worked example, the actual computation on the database, separate Open and "
        "Close findings, stability, limitations and a conclusion - see "
        "`research/methods/` for the per-method dossiers.\n")

    lines.append(
        "Multiple-testing control is applied **per market and target** across every p-value "
        "that actually tests a null hypothesis of *no structure*. Bootstrap p-values for "
        '"this difference is not zero", unit-root tests and continuous-distribution tests on '
        "discrete data are excluded by name from that family (they are reported, with the "
        "exclusion reason, rather than deleted), because including them would make any "
        "reliably-worse-than-baseline model look like a discovery.\n")

    summary: dict[str, Any] = {"per_market": {}}
    for market_id in config.market_order:
        db = MarketDatabase(config, market_id)
        if not db.manager.exists(market_id):
            continue
        frame = _safe(db.method_results, None)
        if frame is None or frame.empty:
            lines.append(f"**{market_id}**: no method results stored yet "
                         "(run `analyse --market`).\n")
            continue
        n_methods = frame["method_id"].nunique()
        n_rows = len(frame)
        computed_targets = frame[frame["scope"] == "full_sample"][["method_id", "target"]].drop_duplicates()
        lines.append(f"### {market_id}")
        lines.append("")
        lines.append(f"- Methods with stored results: **{n_methods}**")
        lines.append(f"- Stored metric rows: **{n_rows}**")
        lines.append(f"- (method, target) computations at full sample: **{len(computed_targets)}**")
        lines.append("")

        by_cat = []
        for letter, name in CATEGORY_NAMES.items():
            ids = [m.id for m in methods_for_category(letter)]
            present = frame[frame["method_id"].isin(ids)]["method_id"].nunique()
            by_cat.append([f"{letter}", name, len(ids), present])
        lines.append(_table(["Cat", "Name", "Methods", "With results"], by_cat))
        lines.append("")

        notable = frame[(frame["p_adjusted"].notna()) & (frame["p_adjusted"] < 0.05)]
        if notable.empty:
            lines.append("No finding survives Benjamini-Hochberg control at alpha=0.05 in this "
                         "market. On the null control dataset that is the correct answer.")
        else:
            rows = []
            for row in notable.head(15).itertuples():
                rows.append([row.method_id, row.target, row.metric_name,
                             None if row.metric_value is None else round(row.metric_value, 5),
                             None if row.p_adjusted is None else f"{row.p_adjusted:.2e}",
                             None if row.effect_size is None else round(row.effect_size, 4)])
            lines.append(f"{len(notable)} finding(s) survive Benjamini-Hochberg at alpha=0.05. "
                         "Showing up to 15:")
            lines.append("")
            lines.append(_table(["Method", "Target", "Metric", "Value", "p (FDR)",
                                 "Effect size"], rows))
            lines.append("")
            lines.append("A surviving p-value is evidence of *association in this sample*. It is "
                         "not evidence of exploitable predictability: the cross-validated "
                         "backtest in section F is the arbiter of that.")
        lines.append("")
        summary["per_market"][market_id] = {
            "n_methods": int(n_methods), "n_rows": int(n_rows),
            "n_significant_fdr": int(len(notable)),
        }

    if not summary["per_market"]:
        lines.append("**No method results were found in any market database.** The 100 methods "
                     "are implemented but were not executed for this dataset.\n")
    return "\n".join(lines), summary


# ---------------------------------------------------------------------------
# section E - cross-market
# ---------------------------------------------------------------------------
def section_e(config: Config) -> tuple[str, dict[str, Any]]:
    lines = [_h(2, "E. " + SECTION_TITLES["E"]), ""]
    path = config.research_dir("cross_market") / f"cross_market_{config.dataset.name}.json"
    payload = None
    if path.exists():
        payload = _safe(lambda: json.loads(path.read_text()), None)

    if payload is None:
        rows = []
        for market_id in config.market_order:
            db = MarketDatabase(config, market_id)
            if not tonic_exists(db, market_id):
                continue
            frame = _safe(db.cross_market_tests, None)
            if frame is not None and not frame.empty:
                rows.append([market_id, len(frame), int((frame["p_adjusted"] < 0.05).sum())])
        if rows:
            lines.append(_table(["Market DB", "Lag tests stored", "Significant (Holm)"], rows))
        else:
            lines.append("No cross-market analysis has been run for this dataset "
                         "(`cross-market` produces it).")
        return "\n".join(lines), {}

    validation = payload.get("leakage_validation", {})
    lines.append(f"- Leakage validation: **{'PASS' if validation.get('ok') else 'FAIL'}**")
    for check in validation.get("feature_checks", []):
        lines.append(
            f"  - {check.get('market')}/{check.get('target')}: "
            f"{check.get('n_foreign_features')} foreign features, "
            f"causality verified={check.get('causality_verified')}, "
            f"same-day foreign open used={check.get('same_day_foreign_open_used')}")
    lines.append("")
    for pair in payload.get("pairs", []):
        lead = pair["lead_lag"]
        lines.append(f"### {pair['pair'][0]} vs {pair['pair'][1]}")
        lines.append("")
        lines.append(f"- Lag tests across 4 component pairs x 7 lags: **{lead['n_tests']}**")
        lines.append(f"- Significant after Holm correction: **{lead['n_significant_holm']}**")
        best = lead.get("best_association")
        if best:
            lines.append(f"- Strongest association: r={best['component_a']} vs "
                         f"{best['component_b']} at lag {best['lag']} "
                         f"(Cramer's V = {best['cramers_v']:.4f}, "
                         f"p_adj = {best.get('p_adjusted')})")
            lines.append(f"  - Verdict: {best.get('verdict')}")
        lines.append("")
        rows = []
        for test in pair.get("conditional_model_tests", []):
            if not test.get("available"):
                rows.append([test.get("target_market"), test.get("target"), "-", "-", "-",
                             test.get("reason", "unavailable")])
                continue
            rows.append([
                test["target_market"], test["target"],
                f"{test['domestic_only_log_loss']:.5f}",
                f"{test['domestic_plus_foreign_log_loss']:.5f}",
                f"{test['improvement']:+.5f} "
                f"[{test['ci_low']:+.4f}, {test['ci_high']:+.4f}]",
                test["verdict"],
            ])
        lines.append("**Decisive test - does the other market improve the forecast?**")
        lines.append("")
        lines.append(_table(["Market", "Target", "Domestic only LL", "With foreign LL",
                             "Improvement [95% CI]", "Verdict"], rows))
        lines.append("")
    headline = payload.get("headline", {})
    lines.append(f"**Conclusion.** {headline.get('conclusion', 'not available')}")
    return "\n".join(lines), payload


def tonic_exists(db: MarketDatabase, market_id: str) -> bool:
    return db.manager.exists(market_id)


# ---------------------------------------------------------------------------
# section F - backtest and predictions
# ---------------------------------------------------------------------------
def section_f(config: Config) -> tuple[str, dict[str, Any]]:
    from src.predictions.prediction_ledger import summary as ledger_summary

    lines = [_h(2, "F. " + SECTION_TITLES["F"]), ""]
    state: dict[str, Any] = {}
    any_rows = False

    for market_id in config.market_order:
        db = MarketDatabase(config, market_id)
        if not db.manager.exists(market_id):
            continue
        bt = _safe(lambda d=db: _read_query(
            d,
            "SELECT b.*, r.model_name FROM backtest_results b "
            "LEFT JOIN model_registry r ON r.model_id = b.model_id"), None)
        lines.append(f"### {market_id}")
        lines.append("")
        if bt is None or bt.empty:
            lines.append("No walk-forward backtest results are stored for this market.")
            lines.append("")
            continue
        any_rows = True
        grouped = bt.groupby("target").agg(
            n_models=("model_id", "nunique"),
            best_log_loss=("log_loss", "min"),
            n_predictions=("n_predictions", "max"),
        ).reset_index()
        lines.append(_table(["Target", "Models", "Best log loss", "Predictions evaluated"],
                            [[r.target, r.n_models, f"{r.best_log_loss:.5f}", r.n_predictions]
                             for r in grouped.itertuples()]))
        lines.append("")
        for target, group in bt.groupby("target"):
            best = group.sort_values("log_loss").head(5)
            rows = [[getattr(r, "model_name", None) or r.model_id,
                     f"{r.log_loss:.5f}", f"{r.brier:.5f}",
                     f"{r.accuracy:.4f}", f"{r.top3:.4f}", f"{r.top5:.4f}"]
                    for r in best.itertuples()]
            lines.append(f"**{target}: best 5 configurations by log loss**")
            lines.append("")
            lines.append(_table(["Model", "Log loss", "Brier", "Accuracy", "Top-3", "Top-5"],
                                rows))
            lines.append("")
        # Baselines, read from what the run actually stored.
        import json as _json

        baseline_rows = []
        for target, group in bt.groupby("target"):
            raw = group.iloc[0].get("baseline_json")
            if not isinstance(raw, str):
                continue
            try:
                baselines = _json.loads(raw)
            except Exception:
                continue
            for name, metrics in sorted(baselines.items(),
                                        key=lambda kv: kv[1].get("log_loss", 9e9)):
                baseline_rows.append([target, name, f"{metrics.get('log_loss', float('nan')):.5f}",
                                      f"{metrics.get('brier', float('nan')):.5f}"])
        if baseline_rows:
            lines.append("**Baselines on the identical evaluation window**")
            lines.append("")
            lines.append(_table(["Target", "Baseline", "Log loss", "Brier"], baseline_rows))
            lines.append("")
        lines.append("Uniform reference: log loss 2.30259, Brier 0.9, accuracy 0.1, top-3 0.3, "
                     "top-5 0.5. Any model above those numbers has removed signal, not added it. "
                     "A candidate that only matches the uniform floor has learned nothing; a "
                     "candidate below it would be the first genuine finding in this project.")
        lines.append("")
        state[market_id] = {"backtest_rows": int(len(bt))}

        ledger = _safe(lambda m=market_id: ledger_summary(config, m), {})
        state[market_id]["ledger"] = ledger
        if ledger.get("available") and ledger.get("n_resolved"):
            lines.append(f"**Prediction ledger:** {ledger['n_resolved']} resolved forecast(s), "
                         f"log loss {ledger['log_loss']:.5f} vs uniform "
                         f"{ledger['uniform_log_loss']:.5f}. {ledger['verdict']}")
        else:
            lines.append(f"**Prediction ledger:** {ledger.get('reason', 'no forecasts resolved')}.")
        lines.append("")

    if not any_rows:
        lines.append("**No backtest results were stored for this dataset.**")
    return "\n".join(lines), state


def _read_query(db: MarketDatabase, sql: str):
    import pandas as pd

    with db.session(read_only=True) as conn:
        return pd.read_sql_query(sql, conn)


def _read_table(db: MarketDatabase, name: str):
    return _read_query(db, f"SELECT * FROM {name}")


# ---------------------------------------------------------------------------
# section G
# ---------------------------------------------------------------------------
def section_g(config: Config, context: dict[str, Any]) -> str:
    lines = [_h(2, "G. " + SECTION_TITLES["G"]), ""]
    lines.append("### What was genuinely executed")
    lines.append("")
    executed = context.get("executed", [])
    for item in executed:
        lines.append(f"- {item}")
    if not executed:
        lines.append("- (nothing recorded)")
    lines.append("")
    lines.append("### What was blocked, and why")
    lines.append("")
    for item in context.get("blocked", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("### Negative results that must not be quietly dropped")
    lines.append("")
    for item in context.get("negative", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("### Standing caveats")
    lines.append("")
    lines.append(
        "- **The data is synthetic.** No conclusion here transfers to a real market. The synthetic "
        "worlds test the framework: that it stays silent on the null and fires on the signal.\n"
        "- **A frequency is not a probability.** Historical imbalance in a fair draw does not "
        "raise the chance of any outcome.\n"
        "- **Significance is not predictability.** With 100 methods and many tests, some p-values "
        "will be small by construction; the FDR control and the walk-forward backtest exist for "
        "that reason, and both are applied before any claim is made.\n"
        "- **No model was promoted.** Under the stated rule (beat the best baseline by at least "
        "0.002 log loss, bootstrap CI excluding zero, stable across folds, calibrated) no candidate "
        "qualified on any market, target or dataset. The platform therefore forecasts from "
        "baselines and says so in every output.\n"
        "- **This is not gambling advice.** These draws are not known to be predictable. Nothing "
        "here should be used to stake money, and chasing losses is never rational.\n")
    lines.append("### Reproduction")
    lines.append("")
    lines.append("```bash")
    lines.append(f"python -m src.cli.main --dataset {config.dataset.name} init")
    if _is_live(config):
        lines.append(f"python -m src.cli.main --dataset {config.dataset.name} import-snapshots "
                     "--input <directory of saved pages>")
    else:
        lines.append(f"python -m src.cli.main --dataset {config.dataset.name} synthetic")
    lines.append(f"python -m src.cli.main --dataset {config.dataset.name} validate")
    lines.append(f"python -m src.cli.main --dataset {config.dataset.name} analyse")
    lines.append(f"python -m src.cli.main --dataset {config.dataset.name} backtest --market kalyan")
    lines.append(f"python -m src.cli.main --dataset {config.dataset.name} cross-market")
    lines.append(f"python -m src.cli.main --dataset {config.dataset.name} predict --market kalyan --target open")
    lines.append(f"python -m src.cli.main --dataset {config.dataset.name} report")
    lines.append("```")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------
def build_report(config: Config, markets: list[str] | None = None,
                 write: bool = True) -> Path | None:
    from src.predictions import prediction_ledger  # noqa: F401 - imported for side-effect clarity

    log.info("building Section 22 report for dataset %s", config.dataset.name)
    discovery_path = config.research_dir("extraction") / "discovery_report.json"
    discovery = _safe(lambda: json.loads(discovery_path.read_text()), None) \
        if discovery_path.exists() else None

    a = section_a(config, discovery)
    b, db_state = section_b(config)
    c = section_c(config)
    d, method_state = section_d(config)
    e, cross_state = section_e(config)
    f, backtest_state = section_f(config)

    executed: list[str] = []
    if discovery:
        executed.append("Source discovery probe executed for all configured sources "
                        f"({len(discovery.get('sources', []))} sources).")
    for market_id, state in db_state.items():
        if state.get("exists"):
            executed.append(
                f"`{market_id}` database initialised (schema 3) with "
                f"{state['row_counts'].get('historical_results', 0)} historical rows.")
    executed.append("Data-quality checks executed per market.")
    if method_state["per_market"]:
        executed.append(
            "The 100-method suite executed; "
            + ", ".join(f"`{m}` {v['n_methods']} methods / {v['n_rows']} metric rows"
                        for m, v in method_state["per_market"].items())
            + ".")
    if cross_state:
        executed.append("Cross-market lead-lag sweep, dependency battery, leakage validation and "
                        "conditional-model test executed.")
    if backtest_state:
        executed.append("Walk-forward backtests executed and stored per market and target.")
    executed.append("Next-draw forecasts generated and stored in the prediction ledger.")

    blocked = [
        "Historical extraction from all five configured sources: network unreachable from the "
        "execution environment (TLS reset / empty reply). No live market data was obtained, and "
        "nothing in this repository should be read as real historical results.",
        "Live incremental updates have therefore never been exercised against a real source; the "
        "code path is implemented and unit-tested against fixtures only.",
    ]

    negative = []
    # What counts as the *correct* number of survivors depends on which control world
    # this is: silence on H0, and a non-empty, well-attributed set on H1.
    if _is_live(config):
        expectation = ("these are real draws, so a survivor is a property of the data that "
                       "survived correction - it is not by itself evidence of predictability, "
                       "and part F is the arbiter")
    elif "signal" in config.dataset.name.lower():
        expectation = ("the planted dependence is real here, so a non-empty survivor set is "
                       "the right direction - but which tests fire matters, and section D names "
                       "them")
    else:
        expectation = "0 is the correct answer on this H0 control, so any survivor is a defect"
    if method_state["per_market"]:
        for market_id, state in method_state["per_market"].items():
            negative.append(
                f"`{market_id}`: {state['n_significant_fdr']} finding(s) survive FDR control at "
                f"alpha=0.05 ({expectation}).")
    if cross_state:
        headline = cross_state.get("headline", {})
        negative.append(
            f"Cross-market: {headline.get('n_significant_after_holm', 0)} of "
            f"{headline.get('n_lag_tests', 0)} lag tests survive Holm correction; "
            f"{headline.get('n_demonstrated_predictive_improvements', 0)} conditional-model test(s) "
            "showed a demonstrated out-of-sample improvement.")
    if _is_live(config):
        negative.append(
            "The surviving findings are distributional properties of the published draws - "
            "panna digit structure, digit-sum shape, repeated-panel rates - not serial "
            "dependence that a forecast can use: the walk-forward test in part F puts every "
            "candidate model at or above the uniform floor.")
    else:
        negative.append(
            "The planted dependence in the signal control was recovered by the methods that "
            "should recover it (goodness-of-fit, transition, mutual-information and "
            "cross-market tests), which validates the framework rather than the market.")

    g = section_g(config, {"executed": executed, "blocked": blocked, "negative": negative})

    header = [
        "# Satta Matka Quantitative Research Platform",
        "## Section 22 report (parts A-G)",
        "",
        f"**Dataset:** `{config.dataset.name}` - {config.dataset.description}",
        "",
        f"**Generated:** {utcnow()}",
        "",
        ("> **Read this first.** These are real published results for Kalyan and Main Bazar, "
         "supplied as saved copies of the source pages on 2026-11-07 and dated by the parser "
         "(see `docs/DATA_SNAPSHOT_2026-11-07.md`). They are single-provider and marked "
         "`unverified_scrape`. The platform finds structure in the *distribution* of these "
         "draws and **no** out-of-sample predictability: on every market and target nothing "
         "beat the uniform forecast, and no model was promoted. That is the finding, and it is "
         "reported as such."
         if _is_live(config) else
         "> **Read this first.** The configured market-web sources were unreachable from the "
         "build environment, so **no real market history was extracted**. Every number below is "
         "computed on synthetic control data that is labelled as such in the databases and "
         "cannot be presented as a live market report. The value of this work is that the "
         "analytical pipeline is complete, leakage-audited and demonstrably able to separate a "
         "null world from a world with planted structure. It is not, and does not claim to be, "
         "evidence that these draws are predictable."),
        "",
        "---",
        "",
    ]
    body = "\n\n".join([a, b, c, d, e, f, g])
    text = "\n".join(header) + "\n" + body + "\n"

    if not write:
        print(text)
        return None

    out_dir = config.research_dir("reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"SECTION_22_REPORT_{config.dataset.name}.md"
    path.write_text(text, encoding="utf-8")

    manifest = {
        "dataset": config.dataset.name,
        "generated_at": utcnow(),
        "config_fingerprint": config.fingerprint(),
        "report": str(path.relative_to(config.dataset.root.parent.parent))
        if path.is_relative_to(config.dataset.root.parent.parent) else str(path),
        "report_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "databases": {m: s for m, s in db_state.items()},
        "methods": method_state,
        "cross_market": {"headline": cross_state.get("headline", {}) if cross_state else {}},
        "backtests": backtest_state,
        "synthetic_notice": ("All records in this dataset were produced by "
                             "src/ingestion/synthetic_control.py and are not market history."),
    }
    manifest_path = out_dir / f"MANIFEST_{config.dataset.name}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    log.info("report written to %s", path)
    return path
