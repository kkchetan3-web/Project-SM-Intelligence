# Measured results - `live`

Generated **2026-11-07T15:31:30+00:00** by `scripts/summarise_results.py` directly from `/home/user/Project-SM-Intelligence/data/databases`. Nothing here is hand-written.

_Real extracted market records. Populated only by the ingestion pipeline._

---

## 1. Method execution

### kalyan

| Status | Methods |
|---|---|
| computed | 100 |
| not_applicable | 1 |

| Category | Methods | Metric rows |
|---|---|---|
| A - Frequency and Probability | 12 | 120 |
| B - Recency and Occurrence | 10 | 96 |
| C - Transitions and Dependencies | 12 | 118 |
| D - Time Series | 12 | 126 |
| E - Number Theory and Transformations | 14 | 118 |
| F - Randomness and Statistical Structure | 12 | 124 |
| G - Machine Learning | 12 | 200 |
| H - Advanced Probability, Ensembles and Validation | 16 | 182 |

- Findings carrying a p-value: **210**
- In the multiple-testing family (tests of 'no structure'): **166**
- Excluded from that family as magnitude comparisons, unit-root tests or invalid-for-discrete-data tests: **44** (their raw p-value and the reason are stored)
- Raw p < 0.05 **within the family**: **35**
- Surviving Benjamini-Hochberg FDR at 0.05: **17**

Largest surviving effects:

| Method | Target | Metric | Value | p (FDR) | Effect | n |
|---|---|---|---|---|---|---|
| M058 | close | chi2_pos0_1 | 2512 | 0 | 0.2598 | 4136 |
| M058 | open | chi2_pos1_2 | 2805 | 0 | 0.2746 | 4134 |
| M058 | open | chi2_pos0_1 | 2709 | 0 | 0.2698 | 4134 |
| M058 | close | chi2_pos1_2 | 2726 | 0 | 0.2871 | 4136 |
| M059 | open | hamming_chi2 | 590.4 | 3.27e-126 | nan | 4133 |
| M059 | close | hamming_chi2 | 571.9 | 3.438e-122 | nan | 4135 |
| M058 | open | chi2_pos0_2 | 750.7 | 8.391e-108 | 0.142 | 4134 |
| M058 | close | chi2_pos0_2 | 660.8 | 1.08e-94 | 0.1413 | 4136 |
| M062 | open | ljungbox_parity_lag10 | 35.73 | 0.001282 | nan | 4143 |
| M049 | open | digit_sum_chi2 | 60.44 | 0.001282 | nan | 4134 |
| M062 | open | ljungbox_parity_lag20 | 49.32 | 0.003244 | nan | 4143 |
| M035 | open | correlation_MA50 | -0.0499 | 0.01281 | nan | 4093 |
| M043 | open | month_parity_chi2 | 30.6 | 0.01281 | 0.08594 | 4143 |
| M013 | open | most_overdue_hit_rate | 0.08585 | 0.01474 | nan | 4112 |
| M062 | open | ljungbox_parity_lag5 | 18.84 | 0.01474 | nan | 4143 |
| M057 | open | repeat_rate | 0.1147 | 0.01474 | nan | 4142 |
| M037 | open | correlation_EMA5 | -0.04723 | 0.01489 | nan | 4142 |

### main_bazar

| Status | Methods |
|---|---|
| computed | 100 |
| not_applicable | 1 |

| Category | Methods | Metric rows |
|---|---|---|
| A - Frequency and Probability | 12 | 120 |
| B - Recency and Occurrence | 10 | 96 |
| C - Transitions and Dependencies | 12 | 118 |
| D - Time Series | 12 | 126 |
| E - Number Theory and Transformations | 14 | 118 |
| F - Randomness and Statistical Structure | 12 | 124 |
| G - Machine Learning | 12 | 200 |
| H - Advanced Probability, Ensembles and Validation | 16 | 182 |

- Findings carrying a p-value: **210**
- In the multiple-testing family (tests of 'no structure'): **166**
- Excluded from that family as magnitude comparisons, unit-root tests or invalid-for-discrete-data tests: **44** (their raw p-value and the reason are stored)
- Raw p < 0.05 **within the family**: **13**
- Surviving Benjamini-Hochberg FDR at 0.05: **8**

Largest surviving effects:

| Method | Target | Metric | Value | p (FDR) | Effect | n |
|---|---|---|---|---|---|---|
| M058 | close | chi2_pos1_2 | 1799 | 0 | 0.2907 | 2660 |
| M058 | open | chi2_pos1_2 | 1672 | 1.351e-299 | 0.2803 | 2660 |
| M058 | close | chi2_pos0_1 | 1501 | 1.736e-258 | 0.2504 | 2660 |
| M058 | open | chi2_pos0_1 | 1456 | 3.11e-249 | 0.2466 | 2660 |
| M059 | open | hamming_chi2 | 363.8 | 4.182e-77 | nan | 2659 |
| M059 | close | hamming_chi2 | 275.9 | 4.59e-58 | nan | 2659 |
| M058 | close | chi2_pos0_2 | 428.2 | 9.563e-51 | 0.1418 | 2660 |
| M058 | open | chi2_pos0_2 | 407.7 | 4.7e-47 | 0.1384 | 2660 |

## 2. Walk-forward backtests

### kalyan

**close** - six best configurations by out-of-sample log loss

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30624 | 0.90072 | 0.10713 | 0.30804 | 0.50414 |
| catboost | 2.32020 | 0.90361 | 0.10393 | 0.31151 | 0.50494 |
| random_forest | 2.32664 | 0.90501 | 0.09618 | 0.30003 | 0.49773 |
| knn | 2.39704 | 0.91310 | 0.10820 | 0.29548 | 0.48704 |
| xgboost | 2.44406 | 0.93346 | 0.09885 | 0.30136 | 0.50334 |
| logistic | 2.47056 | 0.93718 | 0.09591 | 0.29495 | 0.50601 |

**open** - six best configurations by out-of-sample log loss

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30733 | 0.90095 | 0.10286 | 0.30831 | 0.50655 |
| catboost | 2.32356 | 0.90440 | 0.10126 | 0.30083 | 0.50013 |
| random_forest | 2.33783 | 0.90709 | 0.08870 | 0.28266 | 0.48410 |
| knn | 2.36310 | 0.91104 | 0.09564 | 0.30617 | 0.51777 |
| xgboost | 2.45060 | 0.93563 | 0.09939 | 0.30671 | 0.50174 |
| logistic | 2.46415 | 0.93465 | 0.10019 | 0.29923 | 0.50975 |

Uniform floor: log loss 2.30259, Brier 0.90000, accuracy 0.1000, top-3 0.3000, top-5 0.5000.

### main_bazar

**close** - six best configurations by out-of-sample log loss

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30910 | 0.90132 | 0.10133 | 0.29292 | 0.50619 |
| catboost | 2.32934 | 0.90525 | 0.10752 | 0.29779 | 0.49292 |
| random_forest | 2.33453 | 0.90642 | 0.08540 | 0.29248 | 0.48584 |
| knn | 2.36217 | 0.91060 | 0.09602 | 0.30000 | 0.50177 |
| xgboost | 2.50000 | 0.94804 | 0.08363 | 0.28009 | 0.49380 |
| logistic | 2.51861 | 0.94477 | 0.10133 | 0.29956 | 0.49380 |

**open** - six best configurations by out-of-sample log loss

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30619 | 0.90069 | 0.10177 | 0.30708 | 0.51549 |
| catboost | 2.33185 | 0.90580 | 0.10089 | 0.29690 | 0.49292 |
| random_forest | 2.33692 | 0.90660 | 0.09380 | 0.29823 | 0.49911 |
| knn | 2.37284 | 0.91234 | 0.10354 | 0.29203 | 0.48628 |
| xgboost | 2.49585 | 0.94364 | 0.09557 | 0.29513 | 0.50133 |
| logistic | 2.53417 | 0.94919 | 0.09469 | 0.29735 | 0.49956 |

Uniform floor: log loss 2.30259, Brier 0.90000, accuracy 0.1000, top-3 0.3000, top-5 0.5000.

## 3. Cross-market

- Lag tests: **28**, significant after Holm: **0**
- Conditional-model tests: **4**, demonstrated improvements: **0**

### kalyan vs main_bazar

| Market | Target | Domestic LL | With foreign LL | Improvement | Verdict |
|---|---|---|---|---|---|
| kalyan | open | 2.45293 | 2.46415 | -0.01122 | no improvement: foreign features do not help this market |
| kalyan | close | 2.45787 | 2.47056 | -0.01270 | no improvement: foreign features do not help this market |
| main_bazar | open | 2.52275 | 2.53417 | -0.01143 | no improvement: foreign features do not help this market |
| main_bazar | close | 2.49885 | 2.51861 | -0.01976 | no improvement: foreign features do not help this market |

**No cross-market relationship produced a demonstrable out-of-sample predictive improvement for either market. Markets are therefore modelled independently, and the cross-market layer remains an analytical overlay rather than an input to prediction.**

## 4. Prediction ledger

- **kalyan**: 2 forecast(s), 0 resolved
- **main_bazar**: 2 forecast(s), 0 resolved

