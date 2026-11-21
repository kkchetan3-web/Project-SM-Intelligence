#!/usr/bin/env python3
"""Assemble the entire SM Intelligence project into a single markdown document.

Reads all config files, source code, scripts, docs, and research artifacts,
then writes them into one self-contained file for use in other AI chatbots.
"""

import json
from pathlib import Path

REPO = Path("/home/user/Project-SM-Intelligence")
OUT = REPO / "SM_INTELLIGENCE_PROJECT_DOCUMENT.md"

# Files to include, in order, grouped by section.
# (section_title, list_of_paths_or_globs)

sections = []

# 1. Project overview
sections.append(("Project Overview", [
    "README.md",
]))

# 2. Configuration
sections.append(("Configuration Files", [
    "config/markets.yaml",
    "config/project.yaml",
    "config/research.yaml",
    "config/sources.yaml",
]))

# 3. Documentation
sections.append(("Documentation", [
    "docs/DATA_SNAPSHOT_2026-11-07.md",
    "docs/DATA_SOURCES.md",
    "docs/DESIGN_DECISIONS.md",
    "docs/METHOD_CATALOGUE.md",
    "docs/PSYCHOLOGY_AND_BIDDING.md",
    "docs/RESULTS_live.md",
    "docs/RESULTS_synthetic_null.md",
    "docs/RESULTS_synthetic_signal.md",
]))

# 4. Core source code
sections.append(("Core Source Code", [
    "src/core/configuration.py",
    "src/core/logging.py",
    "src/core/provenance.py",
    "src/core/validation.py",
]))

# 5. Storage layer
sections.append(("Storage Layer", [
    "src/storage/schema.py",
    "src/storage/database_manager.py",
    "src/storage/migrations.py",
    "src/storage/market_database.py",
    "src/storage/backups.py",
]))

# 6. Ingestion layer
sections.append(("Ingestion Layer", [
    "src/ingestion/chart_snapshot.py",
    "src/ingestion/extraction.py",
    "src/ingestion/snapshot_loading.py",
    "src/ingestion/historical_archive.py",
    "src/ingestion/incremental_updates.py",
    "src/ingestion/pagination.py",
    "src/ingestion/website_discovery.py",
    "src/ingestion/bidding.py",
    "src/ingestion/synthetic_control.py",
]))

# 7. Preprocessing
sections.append(("Preprocessing", [
    "src/preprocessing/cleaning.py",
    "src/preprocessing/feature_engineering.py",
    "src/preprocessing/normalization.py",
    "src/preprocessing/quality_checks.py",
    "src/preprocessing/psychology.py",
]))

# 8. Mathematics (the 100-method framework)
sections.append(("Mathematics (100-Method Framework)", [
    "src/mathematics/types.py",
    "src/mathematics/registry.py",
    "src/mathematics/engine.py",
    "src/mathematics/common.py",
    "src/mathematics/frequency.py",
    "src/mathematics/recurrence.py",
    "src/mathematics/markov.py",
    "src/mathematics/time_series.py",
    "src/mathematics/number_theory.py",
    "src/mathematics/randomness.py",
    "src/mathematics/machine_learning.py",
    "src/mathematics/advanced_statistics.py",
    "src/mathematics/dossier.py",
    "src/mathematics/model_panel.py",
    "src/mathematics/catalog_ab.py",
    "src/mathematics/catalog_cd.py",
    "src/mathematics/catalog_ef.py",
    "src/mathematics/catalog_gh.py",
]))

# 9. Backtesting
sections.append(("Backtesting", [
    "src/backtesting/baselines.py",
    "src/backtesting/metrics.py",
    "src/backtesting/validation.py",
    "src/backtesting/walk_forward.py",
]))

# 10. Models
sections.append(("Model Layer", [
    "src/models/market_models.py",
    "src/models/open_models.py",
    "src/models/close_models.py",
    "src/models/calibration.py",
    "src/models/ensembles.py",
]))

# 11. Cross-market analysis
sections.append(("Cross-Market Analysis", [
    "src/cross_market/conditional_models.py",
    "src/cross_market/cross_market_validation.py",
    "src/cross_market/dependency_analysis.py",
    "src/cross_market/lead_lag_analysis.py",
    "src/cross_market/market_alignment.py",
]))

# 12. Predictions
sections.append(("Predictions", [
    "src/predictions/prediction_engine.py",
    "src/predictions/prediction_ledger.py",
    "src/predictions/reporting.py",
]))

# 13. Reporting
sections.append(("Reporting", [
    "src/reporting/report.py",
]))

# 14. CLI
sections.append(("CLI", [
    "src/cli/main.py",
]))

# 15. Scripts
sections.append(("Scripts", [
    "scripts/run_full_pipeline.py",
    "scripts/run_backtest_predict.py",
    "scripts/summarise_results.py",
    "scripts/export_catalogue.py",
    "scripts/make_manifest.py",
    "scripts/psychology_channel_eval.py",
    "scripts/psychology_signal_check.py",
    "scripts/record_synthetic_provenance.py",
]))

# 16. Research results (JSON summaries)
sections.append(("Research Run Results", [
    "research/runs/backtest_predict_live.json",
    "research/runs/full_pipeline_live.json",
    "research/cross_market/cross_market_live.json",
    "research/psychology_channel_eval.json",
    "research/psychology_signal_check.json",
]))

# 17. Research reports
sections.append(("Research Reports", [
    "research/reports/SECTION_22_REPORT_live.md",
]))

# 18. Extraction reconciliation records
sections.append(("Extraction Reconciliation Records", [
    "research/extraction/snapshot_import.json",
    "research/extraction/discovery_report.json",
    "research/extraction/reconciliation_kalyan.json",
    "research/extraction/reconciliation_main_bazar.json",
    "research/extraction/reconciliation_kalyan_morning.json",
    "research/extraction/reconciliation_milan_morning.json",
    "research/extraction/reconciliation_sridevi.json",
]))

# 19. Method documentation (100 methods, live)
sections.append(("Method Documentation (Live, 100 methods)", []))

# 20. Project metadata files
sections.append(("Project Metadata", [
    "pyproject.toml",
    "requirements.txt",
    "Makefile",
    ".github/workflows/ci.yml",
    "LICENSE",
]))


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"<!-- ERROR reading {path}: {e} -->"


def main():
    out_lines: list[str] = []
    out_lines.append("# SM Intelligence — Complete Project Document")
    out_lines.append("")
    out_lines.append('> **Purpose:** This document contains the entire SM Intelligence (Satta Matka Quantitative Research Platform) project in a single file. It is designed to be pasted into any AI chatbot so the chatbot can understand the full project architecture, methodology, data sources, and results — and use them to help determine "the number" (next draw predictions for satta matka markets).')
    out_lines.append("")
    out_lines.append("> **Project version:** 0.3.0  ")
    out_lines.append("> **Date compiled:** 2026-11-06  ")
    out_lines.append("> **Source repo:** `kkchetan3-web/Project-SM-Intelligence`  ")
    out_lines.append("> **Branch:** `arena/5efcdec7-project-sm-intelligence`")
    out_lines.append("")
    out_lines.append("---")
    out_lines.append("")
    out_lines.append("## Table of Contents")
    out_lines.append("")
    for i, (title, _) in enumerate(sections, 1):
        out_lines.append(f"{i}. {title}")
    out_lines.append("")
    out_lines.append("---")
    out_lines.append("")

    for section_title, paths in sections:
        out_lines.append(f"## {section_title}")
        out_lines.append("")

        if section_title == "Method Documentation (Live, 100 methods)":
            # Read all 100 method docs from research/methods/live/
            method_dir = REPO / "research" / "methods" / "live"
            method_files = sorted(method_dir.glob("*.md"))
            for mf in method_files:
                out_lines.append(f"### {mf.stem}")
                out_lines.append("")
                out_lines.append(read_file(mf))
                out_lines.append("")
        else:
            for path_str in paths:
                fpath = REPO / path_str
                out_lines.append(f"### `{path_str}`")
                out_lines.append("")
                content = read_file(fpath)
                # For large JSON files, include them fully
                out_lines.append(content)
                out_lines.append("")

        out_lines.append("---")
        out_lines.append("")

    out_lines.append("## How to Use This Document")
    out_lines.append("")
    out_lines.append('This document contains the complete SM Intelligence project. To use it in an AI chatbot to find "the number" (predict the next draw):')
    out_lines.append("")
    out_lines.append("1. **Data sources:** The project ingests historical satta matka results from dpbossss.com for 5 markets: Kalyan, Main Bazar, Kalyan Morning, Milan Morning, and Sridevi. Each market has a panel chart (open panna / jodi / close panna) and a jodi chart (jodi numbers only).")
    out_lines.append("")
    out_lines.append("2. **Data structure:** Each market result has an `open_ank` (0-9, digit sum of open panna mod 10), `close_ank` (0-9, digit sum of close panna mod 10), and `jodi` (two-digit open+close, e.g. `07` means open=0, close=7). The panna is a 3-digit panel (000-999).")
    out_lines.append("")
    out_lines.append("3. **100-method framework:** The `src/mathematics/` directory implements 100 statistical/ML methods across 8 categories (A-H): Frequency & Probability, Recency & Occurrence, Transitions & Dependencies, Time Series, Number Theory, Randomness, Machine Learning, and Advanced Probability/Ensembles/Validation. Each method is documented in `research/methods/live/M001-M100_*.md`.")
    out_lines.append("")
    out_lines.append("4. **Baselines:** Every model is compared against 7 online baselines: uniform, frequency (Laplace-smoothed), rolling (window=50), bayes (Dirichlet-multinomial), bayes_jeffreys, recency (EWM decay=0.95), and markov1. No model may be promoted unless it beats the best baseline on walk-forward log loss by at least 0.002.")
    out_lines.append("")
    out_lines.append("5. **Key finding:** On real market data, **no model beats the uniform baseline** on any target (open or close) in any market. All 100 methods were tested; none showed predictive edge after multiple-testing correction (Benjamini-Hochberg FDR and Holm FWER). This is the scientifically honest result: satta matka draws appear statistically indistinguishable from uniform random draws.")
    out_lines.append("")
    out_lines.append("6. **Cross-market analysis:** 196 lead-lag tests across 7 market pairs found 0 surviving after Holm correction. No cross-market predictive relationship was detected.")
    out_lines.append("")
    out_lines.append("7. **Synthetic control validation:** The framework was validated on two surrogate datasets: `synthetic_null` (i.i.d. uniform — framework correctly reports NO edge) and `synthetic_signal` (planted first-order Markov dependence — framework correctly DETECTS edge). This proves the methodology works when signal exists.")
    out_lines.append("")
    out_lines.append("8. **Practical prediction:** When no model has predictive edge, the pipeline falls back to the `uniform` baseline (top3=[0,1,2] at 0.1 probability each). A frequency-based heuristic can also be computed from historical jodi data as a descriptive (not predictive) tool.")
    out_lines.append("")
    out_lines.append("## Key Configuration Parameters")
    out_lines.append("")
    out_lines.append("- **Markets:** kalyan, main_bazar, kalyan_morning, milan_morning, sridevi")
    out_lines.append("- **Outcome spaces:** `ank` (0-9, categorical), `jodi` (00-99, categorical), `panna` (000-999, string)")
    out_lines.append("- **Walk-forward:** expanding scheme, min_train_size=400, embargo=1, final_holdout_fraction=0.20")
    out_lines.append("- **Primary metric:** log_loss (with brier, accuracy, top3, top5 as secondary)")
    out_lines.append("- **Multiple testing:** alpha=0.05, Benjamini-Hochberg (FDR) + Holm (FWER)")
    out_lines.append("- **Model selection:** min_log_loss_improvement=0.002, calibration slope in [0.80, 1.25]")
    out_lines.append("- **Random seed:** 20250101")
    out_lines.append("- **Database:** SQLite, one file per market, WAL mode")
    out_lines.append("")
    out_lines.append("## Data Sources (dpbossss.com)")
    out_lines.append("")
    out_lines.append("| Market | Jodi Chart URL | Panel Chart URL |")
    out_lines.append("|--------|---------------|-----------------|")
    out_lines.append("| Kalyan | https://dpbossss.com/jodi-chart-record/kalyan.php | https://dpbossss.com/panel-chart-record/kalyan.php |")
    out_lines.append("| Main Bazar | https://dpbossss.com/jodi-chart-record/main-bazar.php | https://dpbossss.com/panel-chart-record/main-bazar.php |")
    out_lines.append("| Kalyan Morning | https://dpbossss.com/jodi-chart-record/kalyan-morning.php | https://dpbossss.com/panel-chart-record/kalyan-morning.php |")
    out_lines.append("| Milan Morning | https://dpbossss.com/jodi-chart-record/milan-morning.php | https://dpbossss.com/panel-chart-record/milan-morning.php |")
    out_lines.append("| Sridevi | https://dpbossss.com/jodi-chart-record/sridevi.php | https://dpbossss.com/panel-chart-record/sridevi.php |")
    out_lines.append("")
    out_lines.append("## Running the Pipeline")
    out_lines.append("")
    out_lines.append("```bash")
    out_lines.append("# Install dependencies")
    out_lines.append("pip install -r requirements.txt")
    out_lines.append("")
    out_lines.append("# Run the full pipeline (init → ingest → analyse → backtest → predict)")
    out_lines.append("python -m src.cli.main run --dataset live")
    out_lines.append("")
    out_lines.append("# Or run a targeted backtest+predict (skips init/ingest/analyse)")
    out_lines.append("python scripts/run_backtest_predict.py")
    out_lines.append("")
    out_lines.append("# Run on synthetic control datasets")
    out_lines.append("python -m src.cli.main run --dataset synthetic_null")
    out_lines.append("python -m src.cli.main run --dataset synthetic_signal")
    out_lines.append("```")
    out_lines.append("")
    out_lines.append("---")
    out_lines.append("")
    out_lines.append("*End of project document.*")

    OUT.write_text("\n".join(out_lines), encoding="utf-8")
    size_kb = OUT.stat().st_size / 1024
    print(f"Written: {OUT} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
