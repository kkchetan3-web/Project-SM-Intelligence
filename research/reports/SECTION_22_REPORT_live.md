# Satta Matka Quantitative Research Platform
## Section 22 report (parts A-G)

**Dataset:** `live` - Real extracted market records. Populated only by the ingestion pipeline.

**Generated:** 2026-11-10T05:11:15+00:00

> **Read this first.** These are real published results for Kalyan and Main Bazar, supplied as saved copies of the source pages on 2026-11-07 and dated by the parser (see `docs/DATA_SNAPSHOT_2026-11-07.md`). They are single-provider and marked `unverified_scrape`. The platform finds structure in the *distribution* of these draws and **no** out-of-sample predictability: on every market and target nothing beat the uniform forecast, and no model was promoted. That is the finding, and it is reported as such.

---

## A. Environment, sources and data provenance

| Item | Value |
|---|---|
| Python | 3.11.2 |
| Platform | Linux-6.1.158+-x86_64-with-glibc2.36 |
| Dataset | `live` |
| Dataset root | `/home/user/Project-SM-Intelligence/data/databases` |
| Schema version | 3 |
| Generated at (UTC) | 2026-11-10T05:11:14+00:00 |

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
| kalyan | 4192 | 2012-12-31 .. 2026-11-05 | 104 | unverified_scrape (4192) |
| main_bazar | 2711 | 2015-12-28 .. 2026-11-05 | 51 | unverified_scrape (2711) |
| kalyan_morning | 1401 | 2023-01-02 .. 2026-11-09 | 0 | unverified_scrape (1401) |
| milan_morning | 2657 | 2019-04-22 .. 2026-11-09 | 7 | unverified_scrape (2657) |
| sridevi | 3109 | 2018-03-05 .. 2026-11-09 | 7 | unverified_scrape (3109) |

The scraper still cannot reach the configured hosts from this environment (TLS resets on 443, empty replies on 80), so **nothing here was fetched by the scraper**. The 14,070 stored results come from saved copies of the four primary chart pages supplied on 2026-11-07: parsed by a committed code path (`import-snapshots`), hashed into `source_records`, archived under `data/raw/snapshots/`. They are real published results, but single-provider and therefore `unverified_scrape` - not independently confirmed by a second source.

The jodi pages carry no dates; the panel pages carry dates with year typos, stray characters, mixed date formats and off-by-one labels. Dates were recovered by resolving each page as a whole against its own weekly grid, and the two pages were then checked against each other: they agree on **every** jodi both carry. The repair and conflict lists are in `docs/DATA_SNAPSHOT_2026-11-07.md` and `research/extraction/reconciliation_*.json`.

This report therefore describes the real published history of these markets. It does not make the draws predictable: every verdict in part F is a walk-forward verdict on that history, and part G states the losses plainly.

## B. Architecture and database state

| Market | Integrity | Historical rows | Coverage | Missing tables |
|---|---|---|---|---|
| kalyan | ok | 4192 | 2012-12-31 .. 2026-11-05 | none |
| main_bazar | ok | 2711 | 2015-12-28 .. 2026-11-05 | none |
| kalyan_morning | ok | 1401 | 2023-01-02 .. 2026-11-09 | none |
| milan_morning | ok | 2657 | 2019-04-22 .. 2026-11-09 | none |
| sridevi | ok | 3109 | 2018-03-05 .. 2026-11-09 | none |

### Table population

| Table | kalyan | main_bazar | kalyan_morning | milan_morning | sridevi |
|---|---|---|---|---|---|
| historical_results | 4192 | 2711 | 1401 | 2657 | 3109 |
| source_records | 2 | 2 | 2 | 2 | 2 |
| extraction_runs | 2 | 2 | 2 | 2 | 2 |
| data_quality | 107 | 107 | 107 | 107 | 107 |
| market_features | 0 | 0 | 0 | 0 | 0 |
| method_results | 1084 | 1084 | 1084 | 1084 | 1084 |
| model_registry | 60 | 60 | 40 | 40 | 40 |
| backtest_results | 60 | 60 | 40 | 40 | 40 |
| predictions | 2 | 2 | 2 | 2 | 2 |
| prediction_outcomes | 0 | 0 | 0 | 0 | 0 |
| cross_market_features | 0 | 0 | 0 | 0 | 0 |
| cross_market_tests | 112 | 28 | 84 | 84 | 84 |
| result_revisions | 0 | 0 | 0 | 0 | 0 |
| update_history | 1 | 1 | 1 | 1 | 1 |
| bidding_quotes | 0 | 0 | 0 | 0 | 0 |
| database_migrations | 4 | 4 | 4 | 4 | 4 |

Empty tables are explained rather than hidden: `market_features` and `cross_market_features` are built in memory at each walk-forward cutoff (persisting them risks re-using a vector computed with later data), and `prediction_outcomes` is filled only once the draw a forecast refers to has actually been published.

Each market owns a separate SQLite database at `<dataset root>/<market_id>/<market_id>.db` with the 12 required tables. Raw payloads are stored alongside the cleaned rows; revisions are appended to `result_revisions` rather than overwriting history.

## C. Data quality and validation

| Market | Records | Gate | Errors | Warnings |
|---|---|---|---|---|
| kalyan | 4192 | PASS | 0 | 1 |
| main_bazar | 2711 | PASS | 0 | 1 |
| kalyan_morning | 1401 | PASS | 0 | 0 |
| milan_morning | 2657 | PASS | 0 | 0 |
| sridevi | 3109 | PASS | 0 | 0 |

Checks cover record-level completeness, duplicate dates, calendar gaps, panna-to-ank consistency (digit sum mod 10), impossible values, and the provenance requirement that no live-labelled row lacks a source URL.

## D. The 100-method programme

100 methods are documented and implemented. Each has a definition, mathematical foundation, formula with variable definitions, assumptions, manual steps, a hypothetical worked example, the actual computation on the database, separate Open and Close findings, stability, limitations and a conclusion - see `research/methods/` for the per-method dossiers.

Multiple-testing control is applied **per market and target** across every p-value that actually tests a null hypothesis of *no structure*. Bootstrap p-values for "this difference is not zero", unit-root tests and continuous-distribution tests on discrete data are excluded by name from that family (they are reported, with the exclusion reason, rather than deleted), because including them would make any reliably-worse-than-baseline model look like a discovery.

### kalyan

- Methods with stored results: **100**
- Stored metric rows: **1084**
- (method, target) computations at full sample: **199**

| Cat | Name | Methods | With results |
|---|---|---|---|
| A | Frequency and Probability | 12 | 12 |
| B | Recency and Occurrence | 10 | 10 |
| C | Transitions and Dependencies | 12 | 12 |
| D | Time Series | 12 | 12 |
| E | Number Theory and Transformations | 14 | 14 |
| F | Randomness and Statistical Structure | 12 | 12 |
| G | Machine Learning | 12 | 12 |
| H | Advanced Probability, Ensembles and Validation | 16 | 16 |

17 finding(s) survive Benjamini-Hochberg at alpha=0.05. Showing up to 15:

| Method | Target | Metric | Value | p (FDR) | Effect size |
|---|---|---|---|---|---|
| M013 | open | most_overdue_hit_rate | 0.08435 | 5.87e-03 | nan |
| M035 | open | correlation_MA50 | -0.04176 | 4.91e-02 | nan |
| M043 | open | month_parity_chi2 | 33.74428 | 4.08e-03 | 0.0897 |
| M049 | open | digit_sum_chi2 | 61.18574 | 1.17e-03 | nan |
| M057 | open | repeat_rate | 0.11501 | 1.26e-02 | nan |
| M058 | close | chi2_pos0_1 | 2502.78429 | 0.00e+00 | 0.2606 |
| M058 | close | chi2_pos0_2 | 651.08979 | 8.25e-93 | 0.141 |
| M058 | close | chi2_pos1_2 | 2693.49818 | 0.00e+00 | 0.2867 |
| M058 | open | chi2_pos0_1 | 2691.84094 | 0.00e+00 | 0.2703 |
| M058 | open | chi2_pos0_2 | 743.39441 | 2.23e-106 | 0.142 |
| M058 | open | chi2_pos1_2 | 2786.46894 | 0.00e+00 | 0.275 |
| M059 | close | hamming_chi2 | 568.22911 | 2.18e-121 | nan |
| M059 | open | hamming_chi2 | 602.13073 | 9.51e-129 | nan |
| M062 | close | ljungbox_parity_lag10 | 28.69011 | 2.35e-02 | nan |
| M062 | open | ljungbox_parity_lag5 | 16.76023 | 3.71e-02 | nan |

A surviving p-value is evidence of *association in this sample*. It is not evidence of exploitable predictability: the cross-validated backtest in section F is the arbiter of that.

### main_bazar

- Methods with stored results: **100**
- Stored metric rows: **1084**
- (method, target) computations at full sample: **199**

| Cat | Name | Methods | With results |
|---|---|---|---|
| A | Frequency and Probability | 12 | 12 |
| B | Recency and Occurrence | 10 | 10 |
| C | Transitions and Dependencies | 12 | 12 |
| D | Time Series | 12 | 12 |
| E | Number Theory and Transformations | 14 | 14 |
| F | Randomness and Statistical Structure | 12 | 12 |
| G | Machine Learning | 12 | 12 |
| H | Advanced Probability, Ensembles and Validation | 16 | 16 |

8 finding(s) survive Benjamini-Hochberg at alpha=0.05. Showing up to 15:

| Method | Target | Metric | Value | p (FDR) | Effect size |
|---|---|---|---|---|---|
| M058 | close | chi2_pos0_1 | 1500.6901 | 1.74e-258 | 0.2504 |
| M058 | close | chi2_pos0_2 | 428.16481 | 9.56e-51 | 0.1418 |
| M058 | close | chi2_pos1_2 | 1798.52592 | 0.00e+00 | 0.2907 |
| M058 | open | chi2_pos0_1 | 1455.77441 | 2.90e-249 | 0.2465 |
| M058 | open | chi2_pos0_2 | 408.03905 | 4.10e-47 | 0.1384 |
| M058 | open | chi2_pos1_2 | 1672.55014 | 1.02e-299 | 0.2803 |
| M059 | close | hamming_chi2 | 275.89203 | 4.59e-58 | nan |
| M059 | open | hamming_chi2 | 364.54903 | 2.88e-77 | nan |

A surviving p-value is evidence of *association in this sample*. It is not evidence of exploitable predictability: the cross-validated backtest in section F is the arbiter of that.

### kalyan_morning

- Methods with stored results: **100**
- Stored metric rows: **1084**
- (method, target) computations at full sample: **199**

| Cat | Name | Methods | With results |
|---|---|---|---|
| A | Frequency and Probability | 12 | 12 |
| B | Recency and Occurrence | 10 | 10 |
| C | Transitions and Dependencies | 12 | 12 |
| D | Time Series | 12 | 12 |
| E | Number Theory and Transformations | 14 | 14 |
| F | Randomness and Statistical Structure | 12 | 12 |
| G | Machine Learning | 12 | 12 |
| H | Advanced Probability, Ensembles and Validation | 16 | 16 |

38 finding(s) survive Benjamini-Hochberg at alpha=0.05. Showing up to 15:

| Method | Target | Metric | Value | p (FDR) | Effect size |
|---|---|---|---|---|---|
| M009 | close | chi2_statistic | 33.2541 | 7.79e-04 | 0.1541 |
| M009 | close | p_value | 0.00012 | 7.79e-04 | nan |
| M019 | open | chi2_vs_constant_hazard | 26.71263 | 6.65e-04 | nan |
| M023 | open | transition_chi2 | 124.46869 | 8.66e-03 | 0.0994 |
| M027 | close | joint_chi2 | 134.30142 | 1.10e-03 | 0.1032 |
| M027 | close | mutual_information_bits | 0.0707 | 1.75e-02 | nan |
| M031 | open | mutual_information_bits | 0.07122 | 6.83e-03 | nan |
| M031 | open | excess_over_null | 0.02911 | 6.83e-03 | nan |
| M035 | close | correlation_MA5 | 0.07119 | 3.53e-02 | nan |
| M037 | open | correlation_EMA50 | -0.06951 | 4.48e-02 | nan |
| M045 | close | innovation_ljungbox_p | 3e-05 | 4.73e-04 | nan |
| M047 | close | chi2_mod7 | 24.4247 | 2.44e-03 | nan |
| M048 | close | digital_root_chi2 | 33.2541 | 7.79e-04 | nan |
| M049 | close | digit_sum_chi2 | 97.25799 | 7.01e-10 | nan |
| M049 | open | digit_sum_chi2 | 74.74118 | 2.58e-06 | nan |

A surviving p-value is evidence of *association in this sample*. It is not evidence of exploitable predictability: the cross-validated backtest in section F is the arbiter of that.

### milan_morning

- Methods with stored results: **100**
- Stored metric rows: **1084**
- (method, target) computations at full sample: **199**

| Cat | Name | Methods | With results |
|---|---|---|---|
| A | Frequency and Probability | 12 | 12 |
| B | Recency and Occurrence | 10 | 10 |
| C | Transitions and Dependencies | 12 | 12 |
| D | Time Series | 12 | 12 |
| E | Number Theory and Transformations | 14 | 14 |
| F | Randomness and Statistical Structure | 12 | 12 |
| G | Machine Learning | 12 | 12 |
| H | Advanced Probability, Ensembles and Validation | 16 | 16 |

35 finding(s) survive Benjamini-Hochberg at alpha=0.05. Showing up to 15:

| Method | Target | Metric | Value | p (FDR) | Effect size |
|---|---|---|---|---|---|
| M009 | close | chi2_statistic | 29.03312 | 5.37e-03 | 0.1045 |
| M009 | close | p_value | 0.00064 | 5.37e-03 | nan |
| M010 | open | halves_chi2 | 23.83331 | 2.61e-02 | 0.0947 |
| M013 | open | most_overdue_hit_rate | 0.07959 | 4.04e-03 | nan |
| M027 | close | joint_chi2 | 114.53476 | 4.42e-02 | 0.0692 |
| M027 | close | mutual_information_bits | 0.03243 | 4.00e-02 | nan |
| M035 | open | correlation_MA5 | 0.07201 | 2.83e-03 | nan |
| M035 | open | correlation_MA10 | 0.06823 | 4.04e-03 | nan |
| M036 | open | correlation_WMA10 | 0.05388 | 2.85e-02 | nan |
| M037 | open | correlation_EMA10 | 0.05475 | 2.61e-02 | nan |
| M037 | open | correlation_EMA20 | 0.06817 | 4.04e-03 | nan |
| M037 | open | correlation_EMA50 | 0.05099 | 4.14e-02 | nan |
| M045 | open | innovation_ljungbox_p | 0.00315 | 2.15e-02 | nan |
| M047 | close | chi2_mod7 | 27.23033 | 2.20e-03 | nan |
| M048 | close | digital_root_chi2 | 29.03312 | 5.37e-03 | nan |

A surviving p-value is evidence of *association in this sample*. It is not evidence of exploitable predictability: the cross-validated backtest in section F is the arbiter of that.

### sridevi

- Methods with stored results: **100**
- Stored metric rows: **1084**
- (method, target) computations at full sample: **199**

| Cat | Name | Methods | With results |
|---|---|---|---|
| A | Frequency and Probability | 12 | 12 |
| B | Recency and Occurrence | 10 | 10 |
| C | Transitions and Dependencies | 12 | 12 |
| D | Time Series | 12 | 12 |
| E | Number Theory and Transformations | 14 | 14 |
| F | Randomness and Statistical Structure | 12 | 12 |
| G | Machine Learning | 12 | 12 |
| H | Advanced Probability, Ensembles and Validation | 16 | 16 |

42 finding(s) survive Benjamini-Hochberg at alpha=0.05. Showing up to 15:

| Method | Target | Metric | Value | p (FDR) | Effect size |
|---|---|---|---|---|---|
| M009 | close | chi2_statistic | 33.40913 | 9.52e-04 | 0.1037 |
| M009 | close | p_value | 0.00011 | 9.52e-04 | nan |
| M013 | close | most_overdue_hit_rate | 0.0835 | 1.37e-02 | nan |
| M013 | open | most_overdue_hit_rate | 0.08155 | 2.87e-03 | nan |
| M022 | close | best_split_statistic | 29.38923 | 4.42e-02 | nan |
| M022 | close | split_permutation_p | 0.0099 | 4.42e-02 | nan |
| M023 | open | transition_chi2 | 115.72791 | 3.19e-02 | 0.0643 |
| M028 | close | cramers_v_lag1 | 0.0716 | 2.36e-02 | nan |
| M031 | open | mutual_information_bits | 0.02648 | 4.28e-02 | nan |
| M031 | open | excess_over_null | 0.00753 | 4.28e-02 | nan |
| M035 | open | correlation_MA10 | 0.0468 | 3.95e-02 | nan |
| M037 | open | correlation_EMA5 | 0.04928 | 3.07e-02 | nan |
| M037 | open | correlation_EMA10 | 0.04945 | 3.07e-02 | nan |
| M047 | close | chi2_mod7 | 23.08106 | 5.88e-03 | nan |
| M048 | close | digital_root_chi2 | 33.40913 | 9.52e-04 | nan |

A surviving p-value is evidence of *association in this sample*. It is not evidence of exploitable predictability: the cross-validated backtest in section F is the arbiter of that.


## E. Cross-market intelligence

- Leakage validation: **PASS**
  - kalyan/open: 3 foreign features, causality verified=True, same-day foreign open used=False
  - kalyan/close: 6 foreign features, causality verified=True, same-day foreign open used=True
  - main_bazar/open: 3 foreign features, causality verified=True, same-day foreign open used=False
  - main_bazar/close: 6 foreign features, causality verified=True, same-day foreign open used=True
  - kalyan_morning/open: 3 foreign features, causality verified=True, same-day foreign open used=False
  - kalyan_morning/close: 3 foreign features, causality verified=True, same-day foreign open used=False
  - milan_morning/open: 3 foreign features, causality verified=True, same-day foreign open used=False
  - milan_morning/close: 3 foreign features, causality verified=True, same-day foreign open used=False
  - sridevi/open: 3 foreign features, causality verified=True, same-day foreign open used=False
  - sridevi/close: 3 foreign features, causality verified=True, same-day foreign open used=False

### kalyan vs main_bazar

- Lag tests across 4 component pairs x 7 lags: **28**
- Significant after Holm correction: **0**
- Strongest association: r=close vs close at lag 0 (Cramer's V = 0.0650, p_adj = 1.0)
  - Verdict: no meaningful evidence detected

**Decisive test - does the other market improve the forecast?**

| Market | Target | Domestic only LL | With foreign LL | Improvement [95% CI] | Verdict |
|---|---|---|---|---|---|
| kalyan | open | 2.44431 | 2.45870 | -0.01439 [+0.0081, +0.0213] | no improvement: foreign features do not help this market |
| kalyan | close | 2.46895 | 2.51126 | -0.04231 [+0.0281, +0.0599] | no improvement: foreign features do not help this market |
| main_bazar | open | 2.51015 | 2.52119 | -0.01104 [+0.0058, +0.0172] | no improvement: foreign features do not help this market |
| main_bazar | close | 2.48432 | 2.50173 | -0.01742 [+0.0104, +0.0245] | no improvement: foreign features do not help this market |

### kalyan vs kalyan_morning

- Lag tests across 4 component pairs x 7 lags: **28**
- Significant after Holm correction: **0**
- Strongest association: r=close vs close at lag -1 (Cramer's V = 0.0990, p_adj = 1.0)
  - Verdict: no meaningful evidence detected

**Decisive test - does the other market improve the forecast?**

| Market | Target | Domestic only LL | With foreign LL | Improvement [95% CI] | Verdict |
|---|---|---|---|---|---|
| kalyan | open | 2.44431 | 2.45870 | -0.01439 [+0.0081, +0.0213] | no improvement: foreign features do not help this market |
| kalyan | close | 2.46895 | 2.51126 | -0.04231 [+0.0281, +0.0599] | no improvement: foreign features do not help this market |
| kalyan_morning | open | 2.59497 | 2.61033 | -0.01536 [+0.0032, +0.0281] | no improvement: foreign features do not help this market |
| kalyan_morning | close | 2.62591 | 2.64937 | -0.02346 [+0.0102, +0.0367] | no improvement: foreign features do not help this market |

### kalyan vs milan_morning

- Lag tests across 4 component pairs x 7 lags: **28**
- Significant after Holm correction: **0**
- Strongest association: r=open vs open at lag 2 (Cramer's V = 0.0710, p_adj = 1.0)
  - Verdict: no meaningful evidence detected

**Decisive test - does the other market improve the forecast?**

| Market | Target | Domestic only LL | With foreign LL | Improvement [95% CI] | Verdict |
|---|---|---|---|---|---|
| kalyan | open | 2.44431 | 2.45870 | -0.01439 [+0.0081, +0.0213] | no improvement: foreign features do not help this market |
| kalyan | close | 2.46895 | 2.51126 | -0.04231 [+0.0281, +0.0599] | no improvement: foreign features do not help this market |
| milan_morning | open | 2.55393 | 2.56129 | -0.00736 [+0.0021, +0.0123] | no improvement: foreign features do not help this market |
| milan_morning | close | 2.52841 | 2.53859 | -0.01018 [+0.0026, +0.0180] | no improvement: foreign features do not help this market |

### kalyan vs sridevi

- Lag tests across 4 component pairs x 7 lags: **28**
- Significant after Holm correction: **0**
- Strongest association: r=close vs close at lag -1 (Cramer's V = 0.0716, p_adj = 0.11825468898195877)
  - Verdict: no meaningful evidence detected

**Decisive test - does the other market improve the forecast?**

| Market | Target | Domestic only LL | With foreign LL | Improvement [95% CI] | Verdict |
|---|---|---|---|---|---|
| kalyan | open | 2.44431 | 2.45870 | -0.01439 [+0.0081, +0.0213] | no improvement: foreign features do not help this market |
| kalyan | close | 2.46895 | 2.51126 | -0.04231 [+0.0281, +0.0599] | no improvement: foreign features do not help this market |
| sridevi | open | 2.47081 | 2.48133 | -0.01052 [+0.0049, +0.0164] | no improvement: foreign features do not help this market |
| sridevi | close | 2.49579 | 2.50539 | -0.00959 [+0.0049, +0.0146] | no improvement: foreign features do not help this market |

### kalyan_morning vs milan_morning

- Lag tests across 4 component pairs x 7 lags: **28**
- Significant after Holm correction: **0**
- Strongest association: r=open vs open at lag -1 (Cramer's V = 0.0913, p_adj = 1.0)
  - Verdict: no meaningful evidence detected

**Decisive test - does the other market improve the forecast?**

| Market | Target | Domestic only LL | With foreign LL | Improvement [95% CI] | Verdict |
|---|---|---|---|---|---|
| kalyan_morning | open | 2.59497 | 2.61033 | -0.01536 [+0.0032, +0.0281] | no improvement: foreign features do not help this market |
| kalyan_morning | close | 2.62591 | 2.64937 | -0.02346 [+0.0102, +0.0367] | no improvement: foreign features do not help this market |
| milan_morning | open | 2.55393 | 2.56129 | -0.00736 [+0.0021, +0.0123] | no improvement: foreign features do not help this market |
| milan_morning | close | 2.52841 | 2.53859 | -0.01018 [+0.0026, +0.0180] | no improvement: foreign features do not help this market |

### kalyan_morning vs sridevi

- Lag tests across 4 component pairs x 7 lags: **28**
- Significant after Holm correction: **0**
- Strongest association: r=close vs open at lag -1 (Cramer's V = 0.0946, p_adj = 0.363629760285619)
  - Verdict: no meaningful evidence detected

**Decisive test - does the other market improve the forecast?**

| Market | Target | Domestic only LL | With foreign LL | Improvement [95% CI] | Verdict |
|---|---|---|---|---|---|
| kalyan_morning | open | 2.59497 | 2.61033 | -0.01536 [+0.0032, +0.0281] | no improvement: foreign features do not help this market |
| kalyan_morning | close | 2.62591 | 2.64937 | -0.02346 [+0.0102, +0.0367] | no improvement: foreign features do not help this market |
| sridevi | open | 2.47081 | 2.48133 | -0.01052 [+0.0049, +0.0164] | no improvement: foreign features do not help this market |
| sridevi | close | 2.49579 | 2.50539 | -0.00959 [+0.0049, +0.0146] | no improvement: foreign features do not help this market |

### milan_morning vs sridevi

- Lag tests across 4 component pairs x 7 lags: **28**
- Significant after Holm correction: **0**
- Strongest association: r=close vs open at lag -2 (Cramer's V = 0.0695, p_adj = 0.2582157469869909)
  - Verdict: no meaningful evidence detected

**Decisive test - does the other market improve the forecast?**

| Market | Target | Domestic only LL | With foreign LL | Improvement [95% CI] | Verdict |
|---|---|---|---|---|---|
| milan_morning | open | 2.55393 | 2.56129 | -0.00736 [+0.0021, +0.0123] | no improvement: foreign features do not help this market |
| milan_morning | close | 2.52841 | 2.53859 | -0.01018 [+0.0026, +0.0180] | no improvement: foreign features do not help this market |
| sridevi | open | 2.47081 | 2.48133 | -0.01052 [+0.0049, +0.0164] | no improvement: foreign features do not help this market |
| sridevi | close | 2.49579 | 2.50539 | -0.00959 [+0.0049, +0.0146] | no improvement: foreign features do not help this market |

**Conclusion.** No cross-market relationship produced a demonstrable out-of-sample predictive improvement for either market. Markets are therefore modelled independently, and the cross-market layer remains an analytical overlay rather than an input to prediction.

## F. Backtesting, calibration and prediction performance

### kalyan

| Target | Models | Best log loss | Predictions evaluated |
|---|---|---|---|
| close | 30 | 2.30738 | 3792 |
| open | 30 | 2.30772 | 3792 |

**close: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30738 | 0.90096 | 0.1047 | 0.3035 | 0.5061 |
| svm | 2.30738 | 0.90096 | 0.1047 | 0.3035 | 0.5061 |
| svm | 2.30738 | 0.90096 | 0.1047 | 0.3035 | 0.5061 |
| catboost | 2.32138 | 0.90381 | 0.1084 | 0.3051 | 0.5061 |
| catboost | 2.32138 | 0.90381 | 0.1084 | 0.3051 | 0.5061 |

**open: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30772 | 0.90103 | 0.1063 | 0.3128 | 0.5071 |
| svm | 2.30772 | 0.90103 | 0.1063 | 0.3128 | 0.5071 |
| svm | 2.30772 | 0.90103 | 0.1063 | 0.3128 | 0.5071 |
| catboost | 2.32450 | 0.90465 | 0.0957 | 0.3014 | 0.5092 |
| catboost | 2.32450 | 0.90465 | 0.0957 | 0.3014 | 0.5092 |

**Baselines on the identical evaluation window**

| Target | Baseline | Log loss | Brier |
|---|---|---|---|
| close | uniform | 2.30259 | 0.90000 |
| close | frequency | 2.30431 | 0.90034 |
| close | bayes | 2.30431 | 0.90034 |
| close | bayes_jeffreys | 2.30434 | 0.90034 |
| close | markov1 | 2.32794 | 0.90481 |
| close | rolling | 2.37888 | 0.91339 |
| close | recency | 2.44343 | 0.92315 |
| open | uniform | 2.30259 | 0.90000 |
| open | frequency | 2.30591 | 0.90065 |
| open | bayes | 2.30591 | 0.90065 |
| open | bayes_jeffreys | 2.30595 | 0.90066 |
| open | markov1 | 2.32714 | 0.90466 |
| open | rolling | 2.37037 | 0.91227 |
| open | recency | 2.43060 | 0.92058 |

Uniform reference: log loss 2.30259, Brier 0.9, accuracy 0.1, top-3 0.3, top-5 0.5. Any model above those numbers has removed signal, not added it. A candidate that only matches the uniform floor has learned nothing; a candidate below it would be the first genuine finding in this project.

**Prediction ledger:** forecasts exist but none has been resolved yet.

### main_bazar

| Target | Models | Best log loss | Predictions evaluated |
|---|---|---|---|
| close | 30 | 2.30870 | 2311 |
| open | 30 | 2.30697 | 2311 |

**close: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30870 | 0.90119 | 0.0982 | 0.3025 | 0.4955 |
| svm | 2.30870 | 0.90119 | 0.0982 | 0.3025 | 0.4955 |
| svm | 2.30870 | 0.90119 | 0.0982 | 0.3025 | 0.4955 |
| catboost | 2.33047 | 0.90569 | 0.0939 | 0.2986 | 0.4937 |
| catboost | 2.33047 | 0.90569 | 0.0939 | 0.2986 | 0.4937 |

**open: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30697 | 0.90083 | 0.1051 | 0.3051 | 0.4972 |
| svm | 2.30697 | 0.90083 | 0.1051 | 0.3051 | 0.4972 |
| svm | 2.30697 | 0.90083 | 0.1051 | 0.3051 | 0.4972 |
| catboost | 2.32922 | 0.90533 | 0.0978 | 0.2934 | 0.4976 |
| catboost | 2.32922 | 0.90533 | 0.0978 | 0.2934 | 0.4976 |

**Baselines on the identical evaluation window**

| Target | Baseline | Log loss | Brier |
|---|---|---|---|
| close | uniform | 2.30259 | 0.90000 |
| close | frequency | 2.30643 | 0.90076 |
| close | bayes | 2.30643 | 0.90076 |
| close | bayes_jeffreys | 2.30647 | 0.90077 |
| close | markov1 | 2.33814 | 0.90663 |
| close | rolling | 2.37538 | 0.91324 |
| close | recency | 2.44644 | 0.92417 |
| open | uniform | 2.30259 | 0.90000 |
| open | frequency | 2.30637 | 0.90073 |
| open | bayes | 2.30637 | 0.90073 |
| open | bayes_jeffreys | 2.30641 | 0.90074 |
| open | markov1 | 2.33973 | 0.90684 |
| open | rolling | 2.37093 | 0.91278 |
| open | recency | 2.43812 | 0.92234 |

Uniform reference: log loss 2.30259, Brier 0.9, accuracy 0.1, top-3 0.3, top-5 0.5. Any model above those numbers has removed signal, not added it. A candidate that only matches the uniform floor has learned nothing; a candidate below it would be the first genuine finding in this project.

**Prediction ledger:** forecasts exist but none has been resolved yet.

### kalyan_morning

| Target | Models | Best log loss | Predictions evaluated |
|---|---|---|---|
| close | 20 | 2.30598 | 1051 |
| open | 20 | 2.31050 | 1051 |

**close: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30598 | 0.90076 | 0.1018 | 0.3378 | 0.5395 |
| svm | 2.30598 | 0.90076 | 0.1018 | 0.3378 | 0.5395 |
| random_forest | 2.32777 | 0.90553 | 0.1047 | 0.3226 | 0.5157 |
| random_forest | 2.32777 | 0.90553 | 0.1047 | 0.3226 | 0.5157 |
| catboost | 2.33580 | 0.90732 | 0.1161 | 0.3045 | 0.5128 |

**open: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.31050 | 0.90162 | 0.1113 | 0.3130 | 0.5138 |
| svm | 2.31050 | 0.90162 | 0.1113 | 0.3130 | 0.5138 |
| catboost | 2.32646 | 0.90505 | 0.1056 | 0.3273 | 0.5328 |
| catboost | 2.32646 | 0.90505 | 0.1056 | 0.3273 | 0.5328 |
| random_forest | 2.33653 | 0.90639 | 0.1142 | 0.3226 | 0.5195 |

**Baselines on the identical evaluation window**

| Target | Baseline | Log loss | Brier |
|---|---|---|---|
| close | frequency | 2.29962 | 0.89946 |
| close | bayes | 2.29962 | 0.89946 |
| close | bayes_jeffreys | 2.29971 | 0.89948 |
| close | uniform | 2.30259 | 0.90000 |
| close | markov1 | 2.34030 | 0.90671 |
| close | rolling | 2.35585 | 0.90927 |
| close | recency | 2.43180 | 0.92067 |
| open | uniform | 2.30259 | 0.90000 |
| open | frequency | 2.30406 | 0.90028 |
| open | bayes | 2.30406 | 0.90028 |
| open | bayes_jeffreys | 2.30414 | 0.90030 |
| open | markov1 | 2.32938 | 0.90434 |
| open | rolling | 2.36118 | 0.91079 |
| open | recency | 2.42974 | 0.92179 |

Uniform reference: log loss 2.30259, Brier 0.9, accuracy 0.1, top-3 0.3, top-5 0.5. Any model above those numbers has removed signal, not added it. A candidate that only matches the uniform floor has learned nothing; a candidate below it would be the first genuine finding in this project.

**Prediction ledger:** forecasts exist but none has been resolved yet.

### milan_morning

| Target | Models | Best log loss | Predictions evaluated |
|---|---|---|---|
| close | 20 | 2.30970 | 2257 |
| open | 20 | 2.30763 | 2257 |

**close: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30970 | 0.90138 | 0.1086 | 0.3177 | 0.5264 |
| svm | 2.30970 | 0.90138 | 0.1086 | 0.3177 | 0.5264 |
| catboost | 2.32866 | 0.90568 | 0.1006 | 0.3159 | 0.5166 |
| catboost | 2.32866 | 0.90568 | 0.1006 | 0.3159 | 0.5166 |
| random_forest | 2.33480 | 0.90662 | 0.1103 | 0.3101 | 0.5024 |

**open: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30763 | 0.90098 | 0.1006 | 0.3106 | 0.5135 |
| svm | 2.30763 | 0.90098 | 0.1006 | 0.3106 | 0.5135 |
| random_forest | 2.33293 | 0.90604 | 0.1028 | 0.3048 | 0.5135 |
| random_forest | 2.33293 | 0.90604 | 0.1028 | 0.3048 | 0.5135 |
| catboost | 2.33683 | 0.90726 | 0.1010 | 0.2964 | 0.5038 |

**Baselines on the identical evaluation window**

| Target | Baseline | Log loss | Brier |
|---|---|---|---|
| close | uniform | 2.30259 | 0.90000 |
| close | frequency | 2.30428 | 0.90035 |
| close | bayes | 2.30428 | 0.90035 |
| close | bayes_jeffreys | 2.30435 | 0.90036 |
| close | markov1 | 2.33642 | 0.90632 |
| close | rolling | 2.36761 | 0.91157 |
| close | recency | 2.42898 | 0.92049 |
| open | uniform | 2.30259 | 0.90000 |
| open | frequency | 2.30466 | 0.90040 |
| open | bayes | 2.30466 | 0.90040 |
| open | bayes_jeffreys | 2.30470 | 0.90041 |
| open | markov1 | 2.32848 | 0.90463 |
| open | rolling | 2.36890 | 0.91143 |
| open | recency | 2.41001 | 0.91671 |

Uniform reference: log loss 2.30259, Brier 0.9, accuracy 0.1, top-3 0.3, top-5 0.5. Any model above those numbers has removed signal, not added it. A candidate that only matches the uniform floor has learned nothing; a candidate below it would be the first genuine finding in this project.

**Prediction ledger:** forecasts exist but none has been resolved yet.

### sridevi

| Target | Models | Best log loss | Predictions evaluated |
|---|---|---|---|
| close | 20 | 2.30321 | 2709 |
| open | 20 | 2.30817 | 2709 |

**close: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30321 | 0.90006 | 0.1141 | 0.3385 | 0.5312 |
| svm | 2.30321 | 0.90006 | 0.1141 | 0.3385 | 0.5312 |
| catboost | 2.31905 | 0.90340 | 0.1026 | 0.3119 | 0.5172 |
| catboost | 2.31905 | 0.90340 | 0.1026 | 0.3119 | 0.5172 |
| random_forest | 2.32978 | 0.90514 | 0.1137 | 0.3145 | 0.5127 |

**open: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30817 | 0.90109 | 0.1052 | 0.3034 | 0.5150 |
| svm | 2.30817 | 0.90109 | 0.1052 | 0.3034 | 0.5150 |
| catboost | 2.32395 | 0.90470 | 0.1015 | 0.2949 | 0.5120 |
| catboost | 2.32395 | 0.90470 | 0.1015 | 0.2949 | 0.5120 |
| random_forest | 2.32532 | 0.90483 | 0.0997 | 0.3116 | 0.5175 |

**Baselines on the identical evaluation window**

| Target | Baseline | Log loss | Brier |
|---|---|---|---|
| close | uniform | 2.30259 | 0.90000 |
| close | frequency | 2.30315 | 0.90007 |
| close | bayes | 2.30315 | 0.90007 |
| close | bayes_jeffreys | 2.30320 | 0.90008 |
| close | markov1 | 2.33547 | 0.90631 |
| close | rolling | 2.37774 | 0.91272 |
| close | recency | 2.43651 | 0.92172 |
| open | uniform | 2.30259 | 0.90000 |
| open | frequency | 2.30487 | 0.90046 |
| open | bayes | 2.30487 | 0.90046 |
| open | bayes_jeffreys | 2.30491 | 0.90047 |
| open | markov1 | 2.32523 | 0.90424 |
| open | rolling | 2.36539 | 0.91170 |
| open | recency | 2.42217 | 0.91925 |

Uniform reference: log loss 2.30259, Brier 0.9, accuracy 0.1, top-3 0.3, top-5 0.5. Any model above those numbers has removed signal, not added it. A candidate that only matches the uniform floor has learned nothing; a candidate below it would be the first genuine finding in this project.

**Prediction ledger:** forecasts exist but none has been resolved yet.


## G. Limitations, negative results and honest conclusions

### What was genuinely executed

- Source discovery probe executed for all configured sources (0 sources).
- `kalyan` database initialised (schema 3) with 4192 historical rows.
- `main_bazar` database initialised (schema 3) with 2711 historical rows.
- `kalyan_morning` database initialised (schema 3) with 1401 historical rows.
- `milan_morning` database initialised (schema 3) with 2657 historical rows.
- `sridevi` database initialised (schema 3) with 3109 historical rows.
- Data-quality checks executed per market.
- The 100-method suite executed; `kalyan` 100 methods / 1084 metric rows, `main_bazar` 100 methods / 1084 metric rows, `kalyan_morning` 100 methods / 1084 metric rows, `milan_morning` 100 methods / 1084 metric rows, `sridevi` 100 methods / 1084 metric rows.
- Cross-market lead-lag sweep, dependency battery, leakage validation and conditional-model test executed.
- Walk-forward backtests executed and stored per market and target.
- Next-draw forecasts generated and stored in the prediction ledger.

### What was blocked, and why

- The scraper cannot reach any of the five configured sources from this environment (TLS reset on 443, empty reply on 80). The real history in this report therefore arrived as saved copies of the four primary pages supplied on 2026-11-07 - parsed, dated and cross-checked by `import-snapshots`, not fetched.
- Single provider. Nothing here has been confirmed against a second source, so every row is `unverified_scrape` rather than verified.
- The snapshot ends at the last published result it contains (2026-11-05). It cannot report draws published after it was saved, and no later page has been compared against it yet.
- 40 days (Kalyan 35, Main Bazar 5) print a jodi that contradicts their own pannas. The pannas were kept and the rows flagged; which of the three printed numbers is mistyped cannot be recovered from the page.

### Negative results that must not be quietly dropped

- `kalyan`: 17 finding(s) survive FDR control at alpha=0.05 (these are real draws, so a survivor is a property of the data that survived correction - it is not by itself evidence of predictability, and part F is the arbiter).
- `main_bazar`: 8 finding(s) survive FDR control at alpha=0.05 (these are real draws, so a survivor is a property of the data that survived correction - it is not by itself evidence of predictability, and part F is the arbiter).
- `kalyan_morning`: 38 finding(s) survive FDR control at alpha=0.05 (these are real draws, so a survivor is a property of the data that survived correction - it is not by itself evidence of predictability, and part F is the arbiter).
- `milan_morning`: 35 finding(s) survive FDR control at alpha=0.05 (these are real draws, so a survivor is a property of the data that survived correction - it is not by itself evidence of predictability, and part F is the arbiter).
- `sridevi`: 42 finding(s) survive FDR control at alpha=0.05 (these are real draws, so a survivor is a property of the data that survived correction - it is not by itself evidence of predictability, and part F is the arbiter).
- Cross-market: 0 of 196 lag tests survive Holm correction; 0 conditional-model test(s) showed a demonstrated out-of-sample improvement.
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
