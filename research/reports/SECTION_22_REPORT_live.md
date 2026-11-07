# Satta Matka Quantitative Research Platform
## Section 22 report (parts A-G)

**Dataset:** `live` - Real extracted market records. Populated only by the ingestion pipeline.

**Generated:** 2026-11-07T15:32:08+00:00

> **Read this first.** These are real published results for Kalyan and Main Bazar, supplied as saved copies of the source pages on 2026-11-07 and dated by the parser (see `docs/DATA_SNAPSHOT_2026-11-07.md`). They are single-provider and marked `unverified_scrape`. The platform finds structure in the *distribution* of these draws and **no** out-of-sample predictability: on every market and target nothing beat the uniform forecast, and no model was promoted. That is the finding, and it is reported as such.

---

## A. Environment, sources and data provenance

| Item | Value |
|---|---|
| Python | 3.11.2 |
| Platform | Linux-6.1.158+-x86_64-with-glibc2.36 |
| Dataset | `live` |
| Dataset root | `/tmp/pytest-of-user/pytest-2/test_report_uses_the_live_word0/dbs` |
| Schema version | 3 |
| Generated at (UTC) | 2026-11-07T15:32:08+00:00 |

### Source reachability

| Source | URL | Reachable | Verdict |
|---|---|---|---|
| dpbossss_kalyan | https://dpbossss.com/ | False | unreachable |
| dpbossss_main_bazar | https://dpbossss.com/ | False | unreachable |
| dpbossss_root | https://dpbossss.com/ | False | unreachable |
| sattamatka_sale | https://www.sattamatka.sale/ | False | unreachable |
| sattadpbossmatka | https://sattadpbossmatka.com/ | False | unreachable |

**0 of 5 configured sources responded.** The probe is reproducible with `python -m src.cli.main discover`; the raw report is at `research/extraction/discovery_report.json`.

### What this means for the data

| Market | Stored results | Span | Rows missing a panna | Verification status |
|---|---|---|---|---|
| kalyan | 2 | 2026-11-02 .. 2026-11-03 | 0 | unverified_scrape (2) |

The scraper still cannot reach the configured hosts from this environment (TLS resets on 443, empty replies on 80), so **nothing here was fetched by the scraper**. The 2 stored results come from saved copies of the four primary chart pages supplied on 2026-11-07: parsed by a committed code path (`import-snapshots`), hashed into `source_records`, archived under `data/raw/snapshots/`. They are real published results, but single-provider and therefore `unverified_scrape` - not independently confirmed by a second source.

The jodi pages carry no dates; the panel pages carry dates with year typos, stray characters, mixed date formats and off-by-one labels. Dates were recovered by resolving each page as a whole against its own weekly grid, and the two pages were then checked against each other: they agree on **every** jodi both carry. The repair and conflict lists are in `docs/DATA_SNAPSHOT_2026-11-07.md` and `research/extraction/reconciliation_*.json`.

This report therefore describes the real published history of these markets. It does not make the draws predictable: every verdict in part F is a walk-forward verdict on that history, and part G states the losses plainly.

## B. Architecture and database state

| Market | Integrity | Historical rows | Coverage | Missing tables |
|---|---|---|---|---|
| kalyan | ok | 2 | 2026-11-02 .. 2026-11-03 | none |
| main_bazar | missing | - | - | run `init` |

### Table population

| Table | kalyan | main_bazar |
|---|---|---|
| historical_results | 2 | - |
| source_records | 2 | - |
| extraction_runs | 2 | - |
| data_quality | 5 | - |
| market_features | 0 | - |
| method_results | 0 | - |
| model_registry | 0 | - |
| backtest_results | 0 | - |
| predictions | 0 | - |
| prediction_outcomes | 0 | - |
| cross_market_features | 0 | - |
| cross_market_tests | 0 | - |
| result_revisions | 0 | - |
| update_history | 1 | - |
| database_migrations | 3 | - |

Empty tables are explained rather than hidden: `market_features` and `cross_market_features` are built in memory at each walk-forward cutoff (persisting them risks re-using a vector computed with later data), and `prediction_outcomes` is filled only once the draw a forecast refers to has actually been published.

Each market owns a separate SQLite database at `<dataset root>/<market_id>/<market_id>.db` with the 12 required tables. Raw payloads are stored alongside the cleaned rows; revisions are appended to `result_revisions` rather than overwriting history.

## C. Data quality and validation

| Market | Records | Gate | Errors | Warnings |
|---|---|---|---|---|
| kalyan | 2 | PASS | 0 | 0 |
| main_bazar | - | - | - | database missing |

Checks cover record-level completeness, duplicate dates, calendar gaps, panna-to-ank consistency (digit sum mod 10), impossible values, and the provenance requirement that no live-labelled row lacks a source URL.

## D. The 100-method programme

100 methods are documented and implemented. Each has a definition, mathematical foundation, formula with variable definitions, assumptions, manual steps, a hypothetical worked example, the actual computation on the database, separate Open and Close findings, stability, limitations and a conclusion - see `research/methods/` for the per-method dossiers.

Multiple-testing control is applied **per market and target** across every p-value that actually tests a null hypothesis of *no structure*. Bootstrap p-values for "this difference is not zero", unit-root tests and continuous-distribution tests on discrete data are excluded by name from that family (they are reported, with the exclusion reason, rather than deleted), because including them would make any reliably-worse-than-baseline model look like a discovery.

**kalyan**: no method results stored yet (run `analyse --market`).

**No method results were found in any market database.** The 100 methods are implemented but were not executed for this dataset.


## E. Cross-market intelligence

- Leakage validation: **PASS**
  - kalyan/open: 3 foreign features, causality verified=True, same-day foreign open used=False
  - kalyan/close: 3 foreign features, causality verified=True, same-day foreign open used=False
  - main_bazar/open: 3 foreign features, causality verified=True, same-day foreign open used=False
  - main_bazar/close: 6 foreign features, causality verified=True, same-day foreign open used=True

### kalyan vs main_bazar

- Lag tests across 4 component pairs x 7 lags: **28**
- Significant after Holm correction: **0**
- Strongest association: r=close vs close at lag 0 (Cramer's V = 0.0665, p_adj = 0.9815940759299747)
  - Verdict: no meaningful evidence detected

**Decisive test - does the other market improve the forecast?**

| Market | Target | Domestic only LL | With foreign LL | Improvement [95% CI] | Verdict |
|---|---|---|---|---|---|
| kalyan | open | 2.45293 | 2.46415 | -0.01122 [+0.0052, +0.0171] | no improvement: foreign features do not help this market |
| kalyan | close | 2.45787 | 2.47056 | -0.01270 [+0.0063, +0.0189] | no improvement: foreign features do not help this market |
| main_bazar | open | 2.52275 | 2.53417 | -0.01143 [+0.0056, +0.0173] | no improvement: foreign features do not help this market |
| main_bazar | close | 2.49885 | 2.51861 | -0.01976 [+0.0110, +0.0274] | no improvement: foreign features do not help this market |

**Conclusion.** No cross-market relationship produced a demonstrable out-of-sample predictive improvement for either market. Markets are therefore modelled independently, and the cross-market layer remains an analytical overlay rather than an input to prediction.

## F. Backtesting, calibration and prediction performance

### kalyan

No walk-forward backtest results are stored for this market.

**No backtest results were stored for this dataset.**

## G. Limitations, negative results and honest conclusions

### What was genuinely executed

- Source discovery probe executed for all configured sources (0 sources).
- `kalyan` database initialised (schema 3) with 2 historical rows.
- Data-quality checks executed per market.
- Cross-market lead-lag sweep, dependency battery, leakage validation and conditional-model test executed.
- Next-draw forecasts generated and stored in the prediction ledger.

### What was blocked, and why

- The scraper cannot reach any of the five configured sources from this environment (TLS reset on 443, empty reply on 80). The real history in this report therefore arrived as saved copies of the four primary pages supplied on 2026-11-07 - parsed, dated and cross-checked by `import-snapshots`, not fetched.
- Single provider. Nothing here has been confirmed against a second source, so every row is `unverified_scrape` rather than verified.
- The snapshot ends at the last published result it contains (2026-11-05). It cannot report draws published after it was saved, and no later page has been compared against it yet.
- 40 days (Kalyan 35, Main Bazar 5) print a jodi that contradicts their own pannas. The pannas were kept and the rows flagged; which of the three printed numbers is mistyped cannot be recovered from the page.

### Negative results that must not be quietly dropped

- Cross-market: 0 of 28 lag tests survive Holm correction; 0 conditional-model test(s) showed a demonstrated out-of-sample improvement.
- The surviving findings are distributional properties of the published draws - panna digit structure, digit-sum shape, repeated-panel rates - not serial dependence that a forecast can use: the walk-forward test in part F puts every candidate model at or above the uniform floor.

### Standing caveats

- **The data is real but single-source.** Kalyan and Main Bazar results as published by dpbossss.com, saved on 2026-11-07 and dated by the parser; `unverified_scrape`, because no second provider has ever been reachable to confirm them.
- **A frequency is not a probability.** Historical imbalance in a fair draw does not raise the chance of any outcome.
- **Significance is not predictability.** With 100 methods and many tests, some p-values will be small by construction; the FDR control and the walk-forward backtest exist for that reason, and both are applied before any claim is made.
- **No model was promoted.** Under the stated rule (beat the best baseline by at least 0.002 log loss, bootstrap CI excluding zero, stable across folds, calibrated) no candidate qualified on any market, target or dataset. The platform therefore forecasts from baselines and says so in every output.
- **The uniform forecast won.** On this real history the best baseline is `uniform` (log loss 2.30259) and every learned model scored above it - the empirical statement that these draws carry no exploitable next-draw information.
- **This is not gambling advice.** These draws are not known to be predictable. Nothing here should be used to stake money, and chasing losses is never rational.

### Reproduction

```bash
python -m src.cli.main --dataset live init
python -m src.cli.main --dataset live import-snapshots --input <directory of saved pages>
python -m src.cli.main --dataset live validate
python -m src.cli.main --dataset live analyse
python -m src.cli.main --dataset live backtest --market kalyan
python -m src.cli.main --dataset live cross-market
python -m src.cli.main --dataset live predict --market kalyan --target open
python -m src.cli.main --dataset live report
```
