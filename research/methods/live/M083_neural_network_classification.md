# M083 - Neural Network Classification

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_083`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `h^{(l)}=\sigma(W^{(l)}h^{(l-1)}+b^{(l)})`

---

## 1. Definition and mathematical foundation

A small multilayer perceptron learns nonlinear feature combinations through hidden layers. On a few thousand noisy observations the parameter count is large relative to the signal, so the regularisation and early-stopping configuration dominates the result.

## 2. Objective

Evaluate a nonlinear learned representation under strict chronological validation.

## 3. Complete formula

```
h^{(l)}=\sigma(W^{(l)}h^{(l-1)}+b^{(l)})
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `W` | weight matrices |
| `sigma` | activation function |
| `alpha` | L2 penalty |

## 5. Statistical assumptions

- The architecture is adequate
- Regularisation prevents memorisation

## 6. Required input data

Tens of thousands of observations for this architecture to be well determined.

## 7. Step-by-step manual calculation

1. Standardise features inside each fold
2. Fit a small MLP with L2 regularisation
3. Evaluate against the linear model and the baselines

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Worked arithmetic for tree/kernel/neural models on a ten-point sequence is not meaningful - they would memorise it. The out-of-sample log-loss comparison in the computed section is the operative evidence, and it is reported against the strongest baseline with a dependence-aware confidence interval.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 2.73977 | n/a | n/a | n/a | n/a | 3743.0 |
| `brier` | 0.99527 | n/a | n/a | n/a | n/a | 3743.0 |
| `accuracy` | 0.10152 | n/a | n/a | n/a | n/a | 3743.0 |
| `top3_accuracy` | 0.29816 | n/a | n/a | n/a | n/a | 3743.0 |
| `log_loss_difference_vs_baseline` | 0.43718 | n/a | 0.00000 | n/a | n/a | 3743.0 |
| `calibration_slope` | -0.04920 | n/a | n/a | n/a | n/a | 3743.0 |
| `expected_calibration_error` | 0.21448 | n/a | n/a | n/a | n/a | 3743.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** Neural network (32 hidden units): out-of-sample log loss 2.73977 against 2.30259 for the best baseline (uniform), a difference of +0.43718 (positive is worse; paired block-bootstrap 95% CI +0.40387 to +0.47047). Accuracy 0.1015, top-3 0.2982, Brier 0.99527, ECE 0.2145, calibration slope -0.0492. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.73977 vs 2.30259); paired block-bootstrap 95% CI [0.40141, 0.47106] includes zero The parameter count of the network exceeds the information available in the data by orders of magnitude; the result is a data-requirement finding.

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
| `log_loss` | 2.77484 | n/a | n/a | n/a | n/a | 3743.0 |
| `brier` | 0.99919 | n/a | n/a | n/a | n/a | 3743.0 |
| `accuracy` | 0.10526 | n/a | n/a | n/a | n/a | 3743.0 |
| `top3_accuracy` | 0.30029 | n/a | n/a | n/a | n/a | 3743.0 |
| `log_loss_difference_vs_baseline` | 0.47225 | n/a | 0.00000 | n/a | n/a | 3743.0 |
| `calibration_slope` | -0.05110 | n/a | n/a | n/a | n/a | 3743.0 |
| `expected_calibration_error` | 0.21742 | n/a | n/a | n/a | n/a | 3743.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** Neural network (32 hidden units): out-of-sample log loss 2.77484 against 2.30259 for the best baseline (uniform), a difference of +0.47225 (positive is worse; paired block-bootstrap 95% CI +0.43117 to +0.51045). Accuracy 0.1053, top-3 0.3003, Brier 0.99919, ECE 0.2174, calibration slope -0.0511. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.77484 vs 2.30259); paired block-bootstrap 95% CI [0.43282, 0.51095] includes zero The parameter count of the network exceeds the information available in the data by orders of magnitude; the result is a data-requirement finding.

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
| Open | computed | `log_loss` | 2.77484 |
| Close | computed | `log_loss` | 2.73977 |

Open produced log_loss=2.77484; Close produced log_loss=2.73977. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Needs thousands of observations per fold to be meaningful; below that the parameter count dominates and every model converges on the marginal.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending on cost) on an expanding window, never tuned on the evaluation window, and promoted only if it beats the strongest baseline by more than 0.002 nats with a bootstrap interval excluding zero and stable across folds.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Neural networks need far more data than these markets provide; the result is a data-requirement finding as much as a modelling one.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
