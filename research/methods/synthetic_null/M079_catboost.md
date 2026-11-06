# M079 - CatBoost

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_079`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\text{ordered target statistics for categorical splits}`

---

## 1. Definition and mathematical foundation

CatBoost targets categorical features with ordered target statistics, designed to avoid the target leakage that naive encoding introduces. Even where features are numeric, its ordered boosting scheme is a useful robustness check on the other boosted models.

## 2. Objective

Evaluate ordered boosting and target-statistic handling.

## 3. Complete formula

```
\text{ordered target statistics for categorical splits}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `ordered statistics` | leak-free categorical encoding |
| `depth` | tree depth |

## 5. Statistical assumptions

- Ordered boosting reduces target leakage
- Categorical handling is consistent

## 6. Required input data

Several thousand observations.

## 7. Step-by-step manual calculation

1. Configure ordered boosting
2. Train chronologically
3. Evaluate out of sample and compare with XGBoost and LightGBM

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Worked arithmetic for tree/kernel/neural models on a ten-point sequence is not meaningful - they would memorise it. The out-of-sample log-loss comparison in the computed section is the operative evidence, and it is reported against the strongest baseline with a dependence-aware confidence interval.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 2.32478 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 0.90452 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.09996 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.29659 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 0.02220 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | 0.60350 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.03970 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** CatBoost: out-of-sample log loss 2.32478 against 2.30259 for the best baseline (uniform), a difference of +0.02220 (positive is worse; paired block-bootstrap 95% CI +0.01543 to +0.02983). Accuracy 0.1000, top-3 0.2966, Brier 0.90452, ECE 0.0397, calibration slope 0.6035. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.32478 vs 2.30259); paired block-bootstrap 95% CI [0.01457, 0.03051] includes zero Ordered boosting is designed to avoid target leakage in categorical encodings; with numeric features its main effect here is simply a different bias-variance point.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 2.32676 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 0.90503 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.10399 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.29220 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 0.02418 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | 0.05870 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.03738 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** CatBoost: out-of-sample log loss 2.32676 against 2.30259 for the best baseline (uniform), a difference of +0.02418 (positive is worse; paired block-bootstrap 95% CI +0.01522 to +0.03234). Accuracy 0.1040, top-3 0.2922, Brier 0.90503, ECE 0.0374, calibration slope 0.0587. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.32676 vs 2.30259); paired block-bootstrap 95% CI [0.01614, 0.03349] includes zero Ordered boosting is designed to avoid target leakage in categorical encodings; with numeric features its main effect here is simply a different bias-variance point.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `log_loss` | 2.32676 |
| Close | computed | `log_loss` | 2.32478 |

Open produced log_loss=2.32676; Close produced log_loss=2.32478. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Needs thousands of observations per fold to be meaningful; below that the parameter count dominates and every model converges on the marginal.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending on cost) on an expanding window, never tuned on the evaluation window, and promoted only if it beats the strongest baseline by more than 0.002 nats with a bootstrap interval excluding zero and stable across folds.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The library's advantages concentrate on categorical feature engineering, which is only indirectly relevant here.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Prokhorenkova et al. (2018)
