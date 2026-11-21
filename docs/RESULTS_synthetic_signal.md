# Measured results - `synthetic_signal`

Generated **2026-11-06T18:55:41+00:00** by `scripts/summarise_results.py` directly from `/home/user/Project-SM-Intelligence/data/databases/_synthetic_signal`. Nothing here is hand-written.

_H1 control: planted first-order Markov dependence. Framework must DETECT edge._

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
- Raw p < 0.05 **within the family**: **79**
- Surviving Benjamini-Hochberg FDR at 0.05: **69**

Largest surviving effects:

| Method | Target | Metric | Value | p (FDR) | Effect | n |
|---|---|---|---|---|---|---|
| M023 | open | transition_chi2 | 2261 | 0 | 0.2833 | 3131 |
| M023 | close | transition_chi2 | 1320 | 3.017e-221 | 0.2165 | 3131 |
| M057 | open | step_chi2 | 1042 | 7.097e-217 | nan | 3130 |
| M057 | close | step_chi2 | 561.4 | 1.681e-113 | nan | 3130 |
| M061 | open | parity_runs | 2008 | 6.591e-55 | nan | 3131 |
| M053 | open | runs_z_statistic | 15.78 | 6.591e-55 | nan | 3131 |
| M071 | open | z_statistic | 15.78 | 6.591e-55 | nan | 3131 |
| M062 | open | ljungbox_parity_lag5 | 263.8 | 8.018e-54 | nan | 3131 |
| M062 | open | ljungbox_parity_lag10 | 265.3 | 3.762e-50 | nan | 3131 |
| M062 | open | ljungbox_parity_lag20 | 271.1 | 6.226e-45 | nan | 3131 |
| M062 | close | ljungbox_parity_lag5 | 161.1 | 1.605e-31 | nan | 3131 |
| M053 | close | runs_z_statistic | 11.79 | 6.257e-31 | nan | 3131 |
| M071 | close | z_statistic | 11.79 | 6.257e-31 | nan | 3131 |
| M061 | close | parity_runs | 1896 | 6.257e-31 | nan | 3131 |
| M062 | close | ljungbox_parity_lag10 | 170.7 | 2.424e-30 | nan | 3131 |
| M062 | close | ljungbox_parity_lag20 | 185.7 | 7.631e-28 | nan | 3131 |
| M061 | open | median_runs | 1266 | 1.978e-19 | nan | 3131 |
| M061 | close | median_runs | 1339 | 3.923e-15 | nan | 3131 |
| M057 | open | repeat_rate | 0.06965 | 2.788e-08 | nan | 3130 |
| M062 | close | ljungbox_numeric_lag5 | 44.45 | 1.58e-07 | nan | 3131 |

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
- Raw p < 0.05 **within the family**: **80**
- Surviving Benjamini-Hochberg FDR at 0.05: **71**

Largest surviving effects:

| Method | Target | Metric | Value | p (FDR) | Effect | n |
|---|---|---|---|---|---|---|
| M023 | open | transition_chi2 | 2477 | 0 | 0.2965 | 3131 |
| M057 | open | step_chi2 | 1103 | 3.541e-230 | nan | 3130 |
| M023 | close | transition_chi2 | 821.1 | 6.035e-121 | 0.1707 | 3131 |
| M057 | close | step_chi2 | 367.4 | 5.091e-72 | nan | 3130 |
| M062 | open | ljungbox_parity_lag5 | 282.8 | 1.366e-57 | nan | 3131 |
| M053 | open | runs_z_statistic | 15.91 | 7.467e-56 | nan | 3131 |
| M061 | open | parity_runs | 2011 | 7.467e-56 | nan | 3131 |
| M071 | open | z_statistic | 15.91 | 7.467e-56 | nan | 3131 |
| M062 | open | ljungbox_parity_lag10 | 288.6 | 4.73e-55 | nan | 3131 |
| M062 | open | ljungbox_parity_lag20 | 316 | 4.474e-54 | nan | 3131 |
| M061 | close | parity_runs | 1845 | 3.99e-22 | nan | 3131 |
| M053 | close | runs_z_statistic | 9.956 | 3.99e-22 | nan | 3131 |
| M071 | close | z_statistic | 9.956 | 3.99e-22 | nan | 3131 |
| M062 | close | ljungbox_parity_lag5 | 110.7 | 4.054e-21 | nan | 3131 |
| M062 | close | ljungbox_parity_lag10 | 112.4 | 2.08e-18 | nan | 3131 |
| M061 | open | median_runs | 1272 | 1.102e-17 | nan | 3131 |
| M062 | close | ljungbox_parity_lag20 | 122 | 1.302e-15 | nan | 3131 |
| M057 | open | repeat_rate | 0.06837 | 5.238e-09 | nan | 3130 |
| M061 | close | median_runs | 1367 | 1.807e-07 | nan | 3131 |
| M062 | open | ljungbox_numeric_lag5 | 35.13 | 1.058e-05 | nan | 3131 |

## 2. Walk-forward backtests

### kalyan

**close** - six best configurations by out-of-sample log loss

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| random_forest | 2.23073 | 0.88051 | 0.24167 | 0.43317 | 0.60125 |
| catboost | 2.23615 | 0.88203 | 0.23471 | 0.42915 | 0.60308 |
| svm | 2.27158 | 0.89282 | 0.17356 | 0.39583 | 0.58806 |
| knn | 2.29659 | 0.89592 | 0.16551 | 0.38045 | 0.57891 |
| xgboost | 2.34864 | 0.90874 | 0.18528 | 0.40608 | 0.59502 |
| logistic | 2.42082 | 0.92431 | 0.16111 | 0.38008 | 0.58074 |

**open** - six best configurations by out-of-sample log loss

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| catboost | 2.13751 | 0.84991 | 0.32186 | 0.48590 | 0.63493 |
| random_forest | 2.15340 | 0.85383 | 0.32442 | 0.47785 | 0.62797 |
| svm | 2.23206 | 0.88190 | 0.23069 | 0.45112 | 0.61809 |
| xgboost | 2.24900 | 0.87708 | 0.26401 | 0.47309 | 0.62907 |
| knn | 2.27658 | 0.88798 | 0.20469 | 0.42109 | 0.60088 |
| logistic | 2.35691 | 0.90493 | 0.21091 | 0.43391 | 0.61809 |

Uniform floor: log loss 2.30259, Brier 0.90000, accuracy 0.1000, top-3 0.3000, top-5 0.5000.

### main_bazar

**close** - six best configurations by out-of-sample log loss

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| catboost | 2.24310 | 0.88537 | 0.20395 | 0.42475 | 0.60674 |
| random_forest | 2.25374 | 0.88758 | 0.18528 | 0.41120 | 0.60674 |
| svm | 2.26863 | 0.89222 | 0.16075 | 0.38887 | 0.59209 |
| knn | 2.31913 | 0.89944 | 0.14390 | 0.36983 | 0.57195 |
| xgboost | 2.31964 | 0.90422 | 0.18491 | 0.41780 | 0.61333 |
| logistic | 2.42017 | 0.92522 | 0.15892 | 0.38155 | 0.58330 |

**open** - six best configurations by out-of-sample log loss

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| catboost | 2.11899 | 0.84500 | 0.33944 | 0.50860 | 0.64372 |
| random_forest | 2.13961 | 0.85087 | 0.33577 | 0.49506 | 0.64152 |
| svm | 2.22339 | 0.87897 | 0.22849 | 0.45991 | 0.62212 |
| xgboost | 2.24589 | 0.87673 | 0.26840 | 0.48041 | 0.63420 |
| knn | 2.26058 | 0.88547 | 0.20945 | 0.42329 | 0.61296 |
| logistic | 2.35664 | 0.90317 | 0.20432 | 0.43903 | 0.61479 |

Uniform floor: log loss 2.30259, Brier 0.90000, accuracy 0.1000, top-3 0.3000, top-5 0.5000.

## 3. Cross-market

- Lag tests: **28**, significant after Holm: **3**
- Conditional-model tests: **4**, demonstrated improvements: **1**

### kalyan vs main_bazar

| Market | Target | Domestic LL | With foreign LL | Improvement | Verdict |
|---|---|---|---|---|---|
| kalyan | open | 2.34834 | 2.35691 | -0.00857 | no improvement: foreign features do not help this market |
| kalyan | close | 2.41179 | 2.42082 | -0.00902 | no improvement: foreign features do not help this market |
| main_bazar | open | 2.35291 | 2.35664 | -0.00373 | no improvement: foreign features do not help this market |
| main_bazar | close | 2.44820 | 2.42017 | 0.02803 | out-of-sample predictive improvement demonstrated |

**1 conditional-model tests showed a demonstrated out-of-sample improvement; those features are eligible for the prediction engine subject to re-confirmation on untouched periods.**

## 4. Prediction ledger

- **kalyan**: 2 forecast(s), 0 resolved
- **main_bazar**: 2 forecast(s), 0 resolved

