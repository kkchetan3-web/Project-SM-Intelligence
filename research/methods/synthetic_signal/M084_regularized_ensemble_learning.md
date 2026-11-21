# M084 - Regularized Ensemble Learning

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_084`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{p} = \sum_m w_m \hat{p}_m,\quad w \in \Delta^{M-1}`

---

## 1. Definition and mathematical foundation

Combining predictors with non-negative weights summing to one constrains the ensemble to the convex hull of its members, which bounds its worst case by its best member. The weights are fitted on validation predictions only.

## 2. Objective

Test whether a regularised combination beats the best single model.

## 3. Complete formula

```
\hat{p} = \sum_m w_m \hat{p}_m,\quad w \in \Delta^{M-1}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `w_m` | ensemble weight |
| `Delta` | the probability simplex |

## 5. Statistical assumptions

- Base predictions are out of sample
- Weights are fitted on a separate slice

## 6. Required input data

Out-of-fold predictions from at least three models.

## 7. Step-by-step manual calculation

1. Collect out-of-sample predictions from the base models
2. Fit simplex-constrained weights on an earlier slice
3. Evaluate the combination on a later slice

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

A multinomial logistic model with d features and K=10 classes has 10(d+1) coefficients. With, say, d=60 that is 610 parameters; the smallest sample in this study (n=3131, of which 400 are used for the first fit) is the binding constraint, which is why regularisation and refit cadence are part of the specification rather than tuning knobs.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `stack_log_loss` | 2.20348 | n/a | n/a | n/a | n/a | 1366.0 |
| `best_single_model_log_loss` | 2.20859 | n/a | n/a | n/a | n/a | 1366.0 |
| `improvement_over_best_single` | 0.00512 | n/a | n/a | n/a | n/a | 1366.0 |
| `best_baseline_log_loss` | 2.18979 | n/a | n/a | n/a | n/a | 1366.0 |
| `beats_strongest_baseline` | 0.00000 | n/a | n/a | n/a | n/a | 1366.0 |

**Interpretation.** Simplex-constrained stacking over 10 base models, with weights fitted on the first half of the out-of-sample window and scored on the second. The stack scores 2.20348; the best individual model (catboost) scores 2.20859, an improvement of +0.00512. Fitted weights: random_forest=0.651, catboost=0.206, xgboost=0.092, lightgbm=0.045. The strongest single baseline (markov1) scores 2.18979, so the ensemble is still worse than the simple baseline. A convex combination cannot beat its best member by much, and when all members are guessing, combining them just averages the guesses.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `stack_log_loss` | 2.11850 | n/a | n/a | n/a | n/a | 1366.0 |
| `best_single_model_log_loss` | 2.11937 | n/a | n/a | n/a | n/a | 1366.0 |
| `improvement_over_best_single` | 0.00086 | n/a | n/a | n/a | n/a | 1366.0 |
| `best_baseline_log_loss` | 2.09933 | n/a | n/a | n/a | n/a | 1366.0 |
| `beats_strongest_baseline` | 0.00000 | n/a | n/a | n/a | n/a | 1366.0 |

**Interpretation.** Simplex-constrained stacking over 10 base models, with weights fitted on the first half of the out-of-sample window and scored on the second. The stack scores 2.11850; the best individual model (catboost) scores 2.11937, an improvement of +0.00086. Fitted weights: catboost=0.587, random_forest=0.280, lightgbm=0.094, xgboost=0.040. The strongest single baseline (markov1) scores 2.09933, so the ensemble is still worse than the simple baseline. A convex combination cannot beat its best member by much, and when all members are guessing, combining them just averages the guesses.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `stack_log_loss` | 2.11850 |
| Close | computed | `stack_log_loss` | 2.20348 |

Open produced stack_log_loss=2.11850; Close produced stack_log_loss=2.20348. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Needs thousands of observations per fold to be meaningful; below that the parameter count dominates and every model converges on the marginal.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending on cost) on an expanding window, never tuned on the evaluation window, and promoted only if it beats the strongest baseline by more than 0.002 nats with a bootstrap interval excluding zero and stable across folds.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

A convex combination cannot exceed the best member's expected performance except through variance reduction, which is small when the members are highly correlated.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
