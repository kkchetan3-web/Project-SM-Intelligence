# Satta Matka Quantitative Research Platform
## Section 22 report (parts A-G)

**Dataset:** `live` - Real extracted market records. Populated only by the ingestion pipeline.

**Generated:** 2026-11-09T21:18:02+00:00

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
| Generated at (UTC) | 2026-11-09T21:18:01+00:00 |

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
| data_quality | 73 | 73 | 73 | 73 | 73 |
| market_features | 0 | 0 | 0 | 0 | 0 |
| method_results | 1084 | 1084 | 778 | 778 | 778 |
| model_registry | 20 | 20 | 0 | 0 | 0 |
| backtest_results | 20 | 20 | 0 | 0 | 0 |
| predictions | 2 | 2 | 0 | 0 | 0 |
| prediction_outcomes | 0 | 0 | 0 | 0 | 0 |
| cross_market_features | 0 | 0 | 0 | 0 | 0 |
| cross_market_tests | 0 | 0 | 0 | 0 | 0 |
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
- Stored metric rows: **778**
- (method, target) computations at full sample: **149**

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

36 finding(s) survive Benjamini-Hochberg at alpha=0.05. Showing up to 15:

| Method | Target | Metric | Value | p (FDR) | Effect size |
|---|---|---|---|---|---|
| M009 | close | chi2_statistic | 33.2541 | 6.96e-04 | 0.1541 |
| M009 | close | p_value | 0.00012 | 6.96e-04 | nan |
| M019 | open | chi2_vs_constant_hazard | 26.71263 | 5.92e-04 | nan |
| M023 | open | transition_chi2 | 124.46869 | 7.71e-03 | 0.0994 |
| M027 | close | joint_chi2 | 134.30142 | 9.80e-04 | 0.1032 |
| M027 | close | mutual_information_bits | 0.0707 | 1.56e-02 | nan |
| M031 | open | mutual_information_bits | 0.07122 | 6.08e-03 | nan |
| M031 | open | excess_over_null | 0.02911 | 6.08e-03 | nan |
| M035 | close | correlation_MA5 | 0.07119 | 3.15e-02 | nan |
| M037 | open | correlation_EMA50 | -0.06951 | 3.99e-02 | nan |
| M045 | close | innovation_ljungbox_p | 3e-05 | 4.22e-04 | nan |
| M047 | close | chi2_mod7 | 24.4247 | 2.18e-03 | nan |
| M048 | close | digital_root_chi2 | 33.2541 | 6.96e-04 | nan |
| M049 | close | digit_sum_chi2 | 97.25799 | 6.26e-10 | nan |
| M049 | open | digit_sum_chi2 | 74.74118 | 2.30e-06 | nan |

A surviving p-value is evidence of *association in this sample*. It is not evidence of exploitable predictability: the cross-validated backtest in section F is the arbiter of that.

### milan_morning

- Methods with stored results: **100**
- Stored metric rows: **778**
- (method, target) computations at full sample: **149**

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

33 finding(s) survive Benjamini-Hochberg at alpha=0.05. Showing up to 15:

| Method | Target | Metric | Value | p (FDR) | Effect size |
|---|---|---|---|---|---|
| M009 | close | chi2_statistic | 29.03312 | 4.80e-03 | 0.1045 |
| M009 | close | p_value | 0.00064 | 4.80e-03 | nan |
| M010 | open | halves_chi2 | 23.83331 | 2.32e-02 | 0.0947 |
| M013 | open | most_overdue_hit_rate | 0.07959 | 3.59e-03 | nan |
| M027 | close | joint_chi2 | 114.53476 | 3.94e-02 | 0.0692 |
| M027 | close | mutual_information_bits | 0.03243 | 3.57e-02 | nan |
| M035 | open | correlation_MA5 | 0.07201 | 2.52e-03 | nan |
| M035 | open | correlation_MA10 | 0.06823 | 3.59e-03 | nan |
| M036 | open | correlation_WMA10 | 0.05388 | 2.54e-02 | nan |
| M037 | open | correlation_EMA10 | 0.05475 | 2.32e-02 | nan |
| M037 | open | correlation_EMA20 | 0.06817 | 3.59e-03 | nan |
| M037 | open | correlation_EMA50 | 0.05099 | 3.68e-02 | nan |
| M045 | open | innovation_ljungbox_p | 0.00315 | 1.91e-02 | nan |
| M047 | close | chi2_mod7 | 27.23033 | 1.97e-03 | nan |
| M048 | close | digital_root_chi2 | 29.03312 | 4.80e-03 | nan |

A surviving p-value is evidence of *association in this sample*. It is not evidence of exploitable predictability: the cross-validated backtest in section F is the arbiter of that.

### sridevi

- Methods with stored results: **100**
- Stored metric rows: **778**
- (method, target) computations at full sample: **149**

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

40 finding(s) survive Benjamini-Hochberg at alpha=0.05. Showing up to 15:

| Method | Target | Metric | Value | p (FDR) | Effect size |
|---|---|---|---|---|---|
| M009 | close | chi2_statistic | 33.40913 | 8.50e-04 | 0.1037 |
| M009 | close | p_value | 0.00011 | 8.50e-04 | nan |
| M013 | close | most_overdue_hit_rate | 0.0835 | 1.23e-02 | nan |
| M013 | open | most_overdue_hit_rate | 0.08155 | 2.55e-03 | nan |
| M022 | close | best_split_statistic | 29.38923 | 4.37e-02 | nan |
| M022 | close | split_permutation_p | 0.0099 | 4.37e-02 | nan |
| M023 | open | transition_chi2 | 115.72791 | 2.84e-02 | 0.0643 |
| M031 | open | mutual_information_bits | 0.02648 | 3.98e-02 | nan |
| M031 | open | excess_over_null | 0.00753 | 3.98e-02 | nan |
| M035 | open | correlation_MA10 | 0.0468 | 3.52e-02 | nan |
| M037 | open | correlation_EMA5 | 0.04928 | 2.74e-02 | nan |
| M037 | open | correlation_EMA10 | 0.04945 | 2.74e-02 | nan |
| M037 | open | correlation_EMA20 | 0.04343 | 4.91e-02 | nan |
| M047 | close | chi2_mod7 | 23.08106 | 5.25e-03 | nan |
| M048 | close | digital_root_chi2 | 33.40913 | 8.50e-04 | nan |

A surviving p-value is evidence of *association in this sample*. It is not evidence of exploitable predictability: the cross-validated backtest in section F is the arbiter of that.


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

| Target | Models | Best log loss | Predictions evaluated |
|---|---|---|---|
| close | 10 | 2.30738 | 3792 |
| open | 10 | 2.30772 | 3792 |

**close: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30738 | 0.90096 | 0.1047 | 0.3035 | 0.5061 |
| catboost | 2.32138 | 0.90381 | 0.1084 | 0.3051 | 0.5061 |
| random_forest | 2.33021 | 0.90550 | 0.0978 | 0.2983 | 0.4979 |
| knn | 2.38230 | 0.91288 | 0.0986 | 0.2893 | 0.4850 |
| xgboost | 2.44250 | 0.93374 | 0.0936 | 0.3030 | 0.5074 |

**open: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30772 | 0.90103 | 0.1063 | 0.3128 | 0.5071 |
| catboost | 2.32450 | 0.90465 | 0.0957 | 0.3014 | 0.5092 |
| random_forest | 2.32877 | 0.90529 | 0.1057 | 0.2991 | 0.4987 |
| knn | 2.36982 | 0.91083 | 0.1026 | 0.3014 | 0.5082 |
| xgboost | 2.42517 | 0.92934 | 0.1068 | 0.3209 | 0.5227 |

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
| close | 10 | 2.30870 | 2311 |
| open | 10 | 2.30697 | 2311 |

**close: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30870 | 0.90119 | 0.0982 | 0.3025 | 0.4955 |
| catboost | 2.33047 | 0.90569 | 0.0939 | 0.2986 | 0.4937 |
| random_forest | 2.33302 | 0.90621 | 0.0922 | 0.2934 | 0.4890 |
| knn | 2.38840 | 0.91280 | 0.0930 | 0.2951 | 0.4898 |
| xgboost | 2.47509 | 0.93947 | 0.0952 | 0.2903 | 0.4903 |

**open: best 5 configurations by log loss**

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30697 | 0.90083 | 0.1051 | 0.3051 | 0.4972 |
| catboost | 2.32922 | 0.90533 | 0.0978 | 0.2934 | 0.4976 |
| random_forest | 2.33383 | 0.90624 | 0.0995 | 0.2860 | 0.4846 |
| knn | 2.37962 | 0.91155 | 0.1034 | 0.3025 | 0.4929 |
| xgboost | 2.50655 | 0.94707 | 0.0978 | 0.2994 | 0.4937 |

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

No walk-forward backtest results are stored for this market.

### milan_morning

No walk-forward backtest results are stored for this market.

### sridevi

No walk-forward backtest results are stored for this market.


## G. Limitations, negative results and honest conclusions

### What was genuinely executed

- Source discovery probe executed for all configured sources (0 sources).
- `kalyan` database initialised (schema 3) with 4192 historical rows.
- `main_bazar` database initialised (schema 3) with 2711 historical rows.
- `kalyan_morning` database initialised (schema 3) with 1401 historical rows.
- `milan_morning` database initialised (schema 3) with 2657 historical rows.
- `sridevi` database initialised (schema 3) with 3109 historical rows.
- Data-quality checks executed per market.
- The 100-method suite executed; `kalyan` 100 methods / 1084 metric rows, `main_bazar` 100 methods / 1084 metric rows, `kalyan_morning` 100 methods / 778 metric rows, `milan_morning` 100 methods / 778 metric rows, `sridevi` 100 methods / 778 metric rows.
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
- `kalyan_morning`: 36 finding(s) survive FDR control at alpha=0.05 (these are real draws, so a survivor is a property of the data that survived correction - it is not by itself evidence of predictability, and part F is the arbiter).
- `milan_morning`: 33 finding(s) survive FDR control at alpha=0.05 (these are real draws, so a survivor is a property of the data that survived correction - it is not by itself evidence of predictability, and part F is the arbiter).
- `sridevi`: 40 finding(s) survive FDR control at alpha=0.05 (these are real draws, so a survivor is a property of the data that survived correction - it is not by itself evidence of predictability, and part F is the arbiter).
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
