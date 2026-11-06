# Measured results - `synthetic_null`

Generated **2026-11-06T18:51:24+00:00** by `scripts/summarise_results.py` directly from `/home/user/Project-SM-Intelligence/data/databases/_synthetic_null`. Nothing here is hand-written.

_H0 control: i.i.d. uniform draws. Framework must report NO predictive edge._

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
- Raw p < 0.05 **within the family**: **9**
- Surviving Benjamini-Hochberg FDR at 0.05: **0**

No finding survives FDR control: the honest answer on a null world.

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
- Raw p < 0.05 **within the family**: **5**
- Surviving Benjamini-Hochberg FDR at 0.05: **0**

No finding survives FDR control: the honest answer on a null world.

## 2. Walk-forward backtests

### kalyan

**close** - six best configurations by out-of-sample log loss

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30862 | 0.90118 | 0.10216 | 0.30172 | 0.50201 |
| catboost | 2.32478 | 0.90452 | 0.09996 | 0.29659 | 0.49432 |
| random_forest | 2.33121 | 0.90578 | 0.09960 | 0.30172 | 0.51044 |
| knn | 2.39049 | 0.91246 | 0.09777 | 0.30245 | 0.50201 |
| xgboost | 2.47149 | 0.93940 | 0.09996 | 0.30062 | 0.49652 |
| logistic | 2.52432 | 0.94815 | 0.08971 | 0.28781 | 0.48773 |

**open** - six best configurations by out-of-sample log loss

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30782 | 0.90102 | 0.10802 | 0.28707 | 0.49359 |
| catboost | 2.32676 | 0.90503 | 0.10399 | 0.29220 | 0.50677 |
| random_forest | 2.33282 | 0.90580 | 0.09703 | 0.30904 | 0.50604 |
| knn | 2.39723 | 0.91076 | 0.09813 | 0.31417 | 0.50165 |
| xgboost | 2.46695 | 0.93957 | 0.09191 | 0.29623 | 0.50604 |
| logistic | 2.48126 | 0.93873 | 0.10143 | 0.31051 | 0.50238 |

Uniform floor: log loss 2.30259, Brier 0.90000, accuracy 0.1000, top-3 0.3000, top-5 0.5000.

### main_bazar

**close** - six best configurations by out-of-sample log loss

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30827 | 0.90111 | 0.10472 | 0.29842 | 0.48810 |
| catboost | 2.32573 | 0.90494 | 0.09484 | 0.30099 | 0.51520 |
| random_forest | 2.32706 | 0.90494 | 0.10472 | 0.29513 | 0.49542 |
| knn | 2.36054 | 0.91019 | 0.10472 | 0.31124 | 0.51080 |
| xgboost | 2.45800 | 0.93658 | 0.10472 | 0.30538 | 0.51629 |
| logistic | 2.52672 | 0.94849 | 0.09777 | 0.29513 | 0.48810 |

**open** - six best configurations by out-of-sample log loss

| Model | Log loss | Brier | Accuracy | Top-3 | Top-5 |
|---|---|---|---|---|---|
| svm | 2.30875 | 0.90125 | 0.09923 | 0.30428 | 0.51556 |
| catboost | 2.33055 | 0.90589 | 0.09520 | 0.29257 | 0.50348 |
| random_forest | 2.33540 | 0.90657 | 0.09960 | 0.30795 | 0.49762 |
| knn | 2.38572 | 0.91124 | 0.10546 | 0.30319 | 0.49103 |
| xgboost | 2.47905 | 0.93996 | 0.09594 | 0.29220 | 0.49323 |
| logistic | 2.52087 | 0.94836 | 0.09630 | 0.29476 | 0.49286 |

Uniform floor: log loss 2.30259, Brier 0.90000, accuracy 0.1000, top-3 0.3000, top-5 0.5000.

## 3. Cross-market

- Lag tests: **28**, significant after Holm: **0**
- Conditional-model tests: **4**, demonstrated improvements: **0**

### kalyan vs main_bazar

| Market | Target | Domestic LL | With foreign LL | Improvement | Verdict |
|---|---|---|---|---|---|
| kalyan | open | 2.47152 | 2.48126 | -0.00973 | no improvement: foreign features do not help this market |
| kalyan | close | 2.51517 | 2.52432 | -0.00915 | no improvement: foreign features do not help this market |
| main_bazar | open | 2.51192 | 2.52087 | -0.00895 | no improvement: foreign features do not help this market |
| main_bazar | close | 2.50243 | 2.52672 | -0.02430 | no improvement: foreign features do not help this market |

**No cross-market relationship produced a demonstrable out-of-sample predictive improvement for either market. Markets are therefore modelled independently, and the cross-market layer remains an analytical overlay rather than an input to prediction.**

## 4. Prediction ledger

- **kalyan**: 2 forecast(s), 0 resolved
- **main_bazar**: 2 forecast(s), 0 resolved

