# `research/` - generated outputs

Everything in this directory is produced by the code, not written by hand. It is
safe to delete and regenerate (the `.gitignore` keeps the directory but not the
large artefacts):

| Path | Produced by | Contents |
|---|---|---|
| `methods/<dataset>/` | `python -m src.cli.main methods --write --market <m>` | One sixteen-section dossier per method per control world (100 files each), populated with the numbers actually stored in that market's database |
| `cross_market/` | `cross-market` | Lead-lag sweep, dependency battery, leakage validation and the conditional-model comparison |
| `backtests/` | `backtest --market <m>` | Full model-vs-baseline tables with promotion verdicts |
| `extraction/` | `discover`, `import-snapshots` | Per-source reachability report, plus the snapshot reconciliation audit (`reconciliation_<market>.json`) and the import summary. The audit is the record of every date repair, every panna/jodi contradiction and every blank day. |
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

## Which tables are empty, and why

`python -m src.cli.main status` prints row counts per database. Two tables are
legitimately empty in the records above, and neither is a silent failure:

| Table | Why it is empty |
|---|---|
| `market_features`, `cross_market_features` | Both feature sets are built inside the walk-forward panel in memory, at each fold's cutoff, and never persisted as rows - persisting them would risk re-using a feature vector computed with later data. The leakage audit that checks this is `verify_causality`, reported in section E. |
| `prediction_outcomes` | It is filled by `update-all` once the draw a prediction refers to has actually been published. The synthetic controls end on 2025-12-31, so the two pending ledger entries have no outcome to score yet, and none was invented. |

`source_records` and `extraction_runs` are not empty: for a control dataset the act
that produced the rows is *generation*, and it is recorded as such - one run per
market, one source record with URL `synthetic://<dataset>/<market>` and notes holding
the seed and every generator parameter. `scripts/record_synthetic_provenance.py`
backfills that record for databases generated before the generator wrote it itself;
it is idempotent and refuses to stamp a database whose rows and distinct dates differ.

Everything else in the twelve required tables holds real rows for the control
datasets; the counts are printed by `status` and tabulated in section B of the
report ("Table population").

## A note on the numbers

Three datasets live side by side, and every artefact names the one it came from:

| Dataset | Rows | Source | File naming |
|---|---|---|---|
| `live` | Kalyan 4,143 · Main Bazar 2,660 (2012-12-31 / 2015-12-28 → 2026-11-05) | real chart pages saved on 2026-11-07, imported by `import-snapshots` | `*_live.*` |
| `synthetic_null` | 3,131 per market | generator, H0 (i.i.d. uniform) | `*_synthetic_null.*` |
| `synthetic_signal` | 3,131 per market | generator, H1 (planted persistence) | `*_synthetic_signal.*` |

The live numbers come from the user's saved copies of the source pages - see
`../docs/DATA_SNAPSHOT_2026-11-07.md` for how they were dated and reconciled, and
`../docs/DATA_SOURCES.md` for why the automated scraper has never touched the live site.
