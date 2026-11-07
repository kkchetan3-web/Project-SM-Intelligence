# M075 - Random Forest

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_075`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{P}(Y=k\mid x)=\frac{1}{B}\sum_{b=1}^{B}\hat{P}_b(Y=k\mid x)`

---

## 1. Definition and mathematical foundation

A random forest averages many decorrelated trees, each grown on a bootstrap sample with a random feature subset at every split. The averaging reduces variance without much bias, and it captures interactions and threshold effects that a linear model cannot.

## 2. Objective

Test whether a bagged tree ensemble extracts more from the feature set than a linear model.

## 3. Complete formula

```
\hat{P}(Y=k\mid x)=\frac{1}{B}\sum_{b=1}^{B}\hat{P}_b(Y=k\mid x)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `B` | number of trees |
| `P_b` | probability from tree b |

## 5. Statistical assumptions

- Trees are grown on exchangeable training samples
- Averaging reduces variance

## 6. Required input data

Several thousand observations.

## 7. Step-by-step manual calculation

1. Grow trees on bootstrap samples with random feature subsets
2. Average their class probabilities
3. Evaluate chronologically and inspect feature importance

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Worked arithmetic for tree/kernel/neural models on a ten-point sequence is not meaningful - they would memorise it. The out-of-sample log-loss comparison in the computed section is the operative evidence, and it is reported against the strongest baseline with a dependence-aware confidence interval.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 2.32664 | n/a | n/a | n/a | n/a | 3743.0 |
| `brier` | 0.90501 | n/a | n/a | n/a | n/a | 3743.0 |
| `accuracy` | 0.09618 | n/a | n/a | n/a | n/a | 3743.0 |
| `top3_accuracy` | 0.30003 | n/a | n/a | n/a | n/a | 3743.0 |
| `log_loss_difference_vs_baseline` | 0.02406 | n/a | 0.00000 | n/a | n/a | 3743.0 |
| `calibration_slope` | -0.51640 | n/a | n/a | n/a | n/a | 3743.0 |
| `expected_calibration_error` | 0.04402 | n/a | n/a | n/a | n/a | 3743.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** Random forest: out-of-sample log loss 2.32664 against 2.30259 for the best baseline (uniform), a difference of +0.02406 (positive is worse; paired block-bootstrap 95% CI +0.01668 to +0.03129). Accuracy 0.0962, top-3 0.3000, Brier 0.90501, ECE 0.0440, calibration slope -0.5164. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.32664 vs 2.30259); paired block-bootstrap 95% CI [0.01670, 0.03109] includes zero Trees can represent the cyclic and interaction structure a linear model cannot, which is why this is the strongest learned model in the panel - yet still behind the Markov baseline.

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
| `log_loss` | 2.33783 | n/a | n/a | n/a | n/a | 3743.0 |
| `brier` | 0.90709 | n/a | n/a | n/a | n/a | 3743.0 |
| `accuracy` | 0.08870 | n/a | n/a | n/a | n/a | 3743.0 |
| `top3_accuracy` | 0.28266 | n/a | n/a | n/a | n/a | 3743.0 |
| `log_loss_difference_vs_baseline` | 0.03524 | n/a | 0.00000 | n/a | n/a | 3743.0 |
| `calibration_slope` | 0.49370 | n/a | n/a | n/a | n/a | 3743.0 |
| `expected_calibration_error` | 0.05390 | n/a | n/a | n/a | n/a | 3743.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** Random forest: out-of-sample log loss 2.33783 against 2.30259 for the best baseline (uniform), a difference of +0.03524 (positive is worse; paired block-bootstrap 95% CI +0.02822 to +0.04245). Accuracy 0.0887, top-3 0.2827, Brier 0.90709, ECE 0.0539, calibration slope 0.4937. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.33783 vs 2.30259); paired block-bootstrap 95% CI [0.02800, 0.04305] includes zero Trees can represent the cyclic and interaction structure a linear model cannot, which is why this is the strongest learned model in the panel - yet still behind the Markov baseline.

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
| Open | computed | `log_loss` | 2.33783 |
| Close | computed | `log_loss` | 2.32664 |

Open produced log_loss=2.33783; Close produced log_loss=2.32664. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Needs thousands of observations per fold to be meaningful; below that the parameter count dominates and every model converges on the marginal.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending on cost) on an expanding window, never tuned on the evaluation window, and promoted only if it beats the strongest baseline by more than 0.002 nats with a bootstrap interval excluding zero and stable across folds.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Tree ensembles are stable but cannot extrapolate, and with limited signal they mostly reproduce the marginal distribution.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Breiman (2001)
