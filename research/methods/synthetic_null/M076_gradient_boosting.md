# M076 - Gradient Boosting

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_076`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `log_loss` | 2.65690 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 0.97763 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.09630 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.29000 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 0.35431 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | 0.06530 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.19015 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** Gradient boosting: out-of-sample log loss 2.65690 against 2.30259 for the best baseline (uniform), a difference of +0.35431 (positive is worse; paired block-bootstrap 95% CI +0.31886 to +0.39204). Accuracy 0.0963, top-3 0.2900, Brier 0.97763, ECE 0.1901, calibration slope 0.0653. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.65690 vs 2.30259); paired block-bootstrap 95% CI [0.32156, 0.39028] includes zero Boosting spends its capacity fitting noise in the noisy frequency features; the result is worse than a bagged forest despite the more sophisticated optimiser.

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
| `log_loss` | 2.62744 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 0.97113 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.09960 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.30282 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 0.32486 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | 0.13010 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.18340 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** Gradient boosting: out-of-sample log loss 2.62744 against 2.30259 for the best baseline (uniform), a difference of +0.32486 (positive is worse; paired block-bootstrap 95% CI +0.29001 to +0.36115). Accuracy 0.0996, top-3 0.3028, Brier 0.97113, ECE 0.1834, calibration slope 0.1301. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.62744 vs 2.30259); paired block-bootstrap 95% CI [0.29294, 0.35921] includes zero Boosting spends its capacity fitting noise in the noisy frequency features; the result is worse than a bagged forest despite the more sophisticated optimiser.

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
| Open | computed | `log_loss` | 2.62744 |
| Close | computed | `log_loss` | 2.65690 |

Open produced log_loss=2.62744; Close produced log_loss=2.65690. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

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
