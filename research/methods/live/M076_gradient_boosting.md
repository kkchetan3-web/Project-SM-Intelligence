# M076 - Gradient Boosting

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_076`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `F_m(x)=F_{m-1}(x)+\nu h_m(x)`

---

## 1. Definition and mathematical foundation

Gradient boosting fits successive weak learners to the negative gradient of the loss, with a shrinkage factor controlling each step. Its strength is bias reduction on structured data; its weakness is that it will happily fit noise if the loss curve is not monitored out of sample.

## 2. Objective

Evaluate boosted trees and check for the overfitting that this family invites.

## 3. Complete formula

```
F_m(x)=F_{m-1}(x)+\nu h_m(x)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `h_m` | weak learner at step m |
| `nu` | learning rate |
| `M` | number of boosting rounds |

## 5. Statistical assumptions

- The loss is differentiable
- Weak learners can be fitted to pseudo-residuals

## 6. Required input data

Several thousand observations.

## 7. Step-by-step manual calculation

1. Initialise with the base rate
2. Iteratively fit to pseudo-residuals with a small learning rate
3. Evaluate out of sample and compare with the simpler models

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Worked arithmetic for tree/kernel/neural models on a ten-point sequence is not meaningful - they would memorise it. The out-of-sample log-loss comparison in the computed section is the operative evidence, and it is reported against the strongest baseline with a dependence-aware confidence interval.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 2.56445 | n/a | n/a | n/a | n/a | 3743.0 |
| `brier` | 0.96013 | n/a | n/a | n/a | n/a | 3743.0 |
| `accuracy` | 0.10259 | n/a | n/a | n/a | n/a | 3743.0 |
| `top3_accuracy` | 0.30938 | n/a | n/a | n/a | n/a | 3743.0 |
| `log_loss_difference_vs_baseline` | 0.26186 | n/a | 0.00000 | n/a | n/a | 3743.0 |
| `calibration_slope` | -0.03250 | n/a | n/a | n/a | n/a | 3743.0 |
| `expected_calibration_error` | 0.16718 | n/a | n/a | n/a | n/a | 3743.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** Gradient boosting: out-of-sample log loss 2.56445 against 2.30259 for the best baseline (uniform), a difference of +0.26186 (positive is worse; paired block-bootstrap 95% CI +0.23462 to +0.28637). Accuracy 0.1026, top-3 0.3094, Brier 0.96013, ECE 0.1672, calibration slope -0.0325. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.56445 vs 2.30259); paired block-bootstrap 95% CI [0.23522, 0.28934] includes zero Boosting spends its capacity fitting noise in the noisy frequency features; the result is worse than a bagged forest despite the more sophisticated optimiser.

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
| `log_loss` | 2.62107 | n/a | n/a | n/a | n/a | 3743.0 |
| `brier` | 0.97076 | n/a | n/a | n/a | n/a | 3743.0 |
| `accuracy` | 0.09511 | n/a | n/a | n/a | n/a | 3743.0 |
| `top3_accuracy` | 0.29068 | n/a | n/a | n/a | n/a | 3743.0 |
| `log_loss_difference_vs_baseline` | 0.31848 | n/a | 0.00000 | n/a | n/a | 3743.0 |
| `calibration_slope` | 0.13470 | n/a | n/a | n/a | n/a | 3743.0 |
| `expected_calibration_error` | 0.18401 | n/a | n/a | n/a | n/a | 3743.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** Gradient boosting: out-of-sample log loss 2.62107 against 2.30259 for the best baseline (uniform), a difference of +0.31848 (positive is worse; paired block-bootstrap 95% CI +0.28637 to +0.34768). Accuracy 0.0951, top-3 0.2907, Brier 0.97076, ECE 0.1840, calibration slope 0.1347. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.62107 vs 2.30259); paired block-bootstrap 95% CI [0.28901, 0.34659] includes zero Boosting spends its capacity fitting noise in the noisy frequency features; the result is worse than a bagged forest despite the more sophisticated optimiser.

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
| Open | computed | `log_loss` | 2.62107 |
| Close | computed | `log_loss` | 2.56445 |

Open produced log_loss=2.62107; Close produced log_loss=2.56445. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Needs thousands of observations per fold to be meaningful; below that the parameter count dominates and every model converges on the marginal.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending on cost) on an expanding window, never tuned on the evaluation window, and promoted only if it beats the strongest baseline by more than 0.002 nats with a bootstrap interval excluding zero and stable across folds.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Boosting is prone to overfitting on noisy features; the configuration here uses shallow trees and explicit L2 regularisation for that reason.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Friedman (2001)
