# `research/` - generated outputs

Everything in this directory is produced by the code, not written by hand. It is
safe to delete and regenerate (the `.gitignore` keeps the directory but not the
large artefacts):

| Path | Produced by | Contents |
|---|---|---|
| `methods/` | `python -m src.cli.main methods --write --market <m>` | One fifteen-section dossier per method, populated with the numbers actually stored in that market's database |
| `cross_market/` | `cross-market` | Lead-lag sweep, dependency battery, leakage validation and the conditional-model comparison |
| `backtests/` | `backtest --market <m>` | Full model-vs-baseline tables with promotion verdicts |
| `extraction/` | `discover` | Per-source reachability report (all sources were unreachable here) |
| `runs/` | `scripts/run_full_pipeline.py`, `update-all` | Stage-by-stage run records with timings, status counts and failures |
| `reports/` | `report` | `SECTION_22_REPORT_<dataset>.md` (parts A–G) and `MANIFEST_<dataset>.json` |

## Reading a dossier

Each `methods/M0xx_*.md` file contains: definition and mathematical foundation,
objective, formula, variable-by-variable explanation, assumptions, input
requirements, manual calculation steps, a **hypothetical** worked example clearly
labelled as such, the **actual** computed results, separate Open and Close
findings, suitability, stability, interpretation, limitations and conclusion.

If a method could not run, section 9 says why (`insufficient_data`,
`dependency_unavailable`, `not_applicable`, `failed`) instead of showing a number.

## A note on the numbers

All figures derive from the synthetic control datasets (`synthetic_null`,
`synthetic_signal`) unless the dataset banner says `live`. No real market history
was obtained - see `../docs/DATA_SOURCES.md`.
