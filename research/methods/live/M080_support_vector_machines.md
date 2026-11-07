# M080 - Support Vector Machines

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_080`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\min_{w,b}\tfrac{1}{2}\|w\|^2 + C\sum_i \xi_i`

---

## 1. Definition and mathematical foundation

An SVM finds the maximum-margin separating boundary, optionally in a kernel-induced space. Probabilities require an extra calibration step (Platt scaling), which is fitted internally and is therefore a source of additional variance worth reporting.

## 2. Objective

Evaluate a maximum-margin classifier with calibrated probabilities.

## 3. Complete formula

```
\min_{w,b}\tfrac{1}{2}\|w\|^2 + C\sum_i \xi_i
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `C` | regularisation strength |
| `xi` | slack variables |
| `gamma` | RBF kernel width |

## 5. Statistical assumptions

- Classes are separable to some degree in feature space
- The kernel bandwidth is appropriate

## 6. Required input data

Several thousand observations.

## 7. Step-by-step manual calculation

1. Standardise features inside each fold
2. Fit the kernel SVM on the expanding window
3. Convert decision values to probabilities and evaluate

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Worked arithmetic for tree/kernel/neural models on a ten-point sequence is not meaningful - they would memorise it. The out-of-sample log-loss comparison in the computed section is the operative evidence, and it is reported against the strongest baseline with a dependence-aware confidence interval.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 2.30624 | n/a | n/a | n/a | n/a | 3743.0 |
| `brier` | 0.90072 | n/a | n/a | n/a | n/a | 3743.0 |
| `accuracy` | 0.10713 | n/a | n/a | n/a | n/a | 3743.0 |
| `top3_accuracy` | 0.30804 | n/a | n/a | n/a | n/a | 3743.0 |
| `log_loss_difference_vs_baseline` | 0.00366 | n/a | 0.01200 | n/a | n/a | 3743.0 |
| `calibration_slope` | -2.32300 | n/a | n/a | n/a | n/a | 3743.0 |
| `expected_calibration_error` | 0.00983 | n/a | n/a | n/a | n/a | 3743.0 |
| `folds_beaten` | 1.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** Support vector machine (RBF kernel): out-of-sample log loss 2.30624 against 2.30259 for the best baseline (uniform), a difference of +0.00366 (positive is worse; paired block-bootstrap 95% CI +0.00109 to +0.00667). Accuracy 0.1071, top-3 0.3080, Brier 0.90072, ECE 0.0098, calibration slope -2.323. It beats the baseline in 1 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.30624 vs 2.30259); paired block-bootstrap 95% CI [0.00090, 0.00649] includes zero Probabilities come from an internal Platt calibration, which adds variance on top of the classifier itself - visible in the refit cadence.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 2.30733 | n/a | n/a | n/a | n/a | 3743.0 |
| `brier` | 0.90095 | n/a | n/a | n/a | n/a | 3743.0 |
| `accuracy` | 0.10286 | n/a | n/a | n/a | n/a | 3743.0 |
| `top3_accuracy` | 0.30831 | n/a | n/a | n/a | n/a | 3743.0 |
| `log_loss_difference_vs_baseline` | 0.00475 | n/a | 0.00000 | n/a | n/a | 3743.0 |
| `calibration_slope` | -1.64320 | n/a | n/a | n/a | n/a | 3743.0 |
| `expected_calibration_error` | 0.01306 | n/a | n/a | n/a | n/a | 3743.0 |
| `folds_beaten` | 2.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** Support vector machine (RBF kernel): out-of-sample log loss 2.30733 against 2.30259 for the best baseline (uniform), a difference of +0.00475 (positive is worse; paired block-bootstrap 95% CI +0.00180 to +0.00800). Accuracy 0.1029, top-3 0.3083, Brier 0.90095, ECE 0.0131, calibration slope -1.6432. It beats the baseline in 2 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.30733 vs 2.30259); paired block-bootstrap 95% CI [0.00121, 0.00823] includes zero Probabilities come from an internal Platt calibration, which adds variance on top of the classifier itself - visible in the refit cadence.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `log_loss` | 2.30733 |
| Close | computed | `log_loss` | 2.30624 |

Open produced log_loss=2.30733; Close produced log_loss=2.30624. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Needs thousands of observations per fold to be meaningful; below that the parameter count dominates and every model converges on the marginal.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending on cost) on an expanding window, never tuned on the evaluation window, and promoted only if it beats the strongest baseline by more than 0.002 nats with a bootstrap interval excluding zero and stable across folds.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

SVM probability calibration is itself a fitted model, adding a layer of variance; and kernel SVMs scale poorly beyond a few thousand observations.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Cortes & Vapnik (1995)
