# M081 - K-Nearest Neighbours

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_081`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{P}(Y=k\mid x)=\frac{1}{K}\sum_{i \in N_K(x)}\mathbf{1}[y_i=k]`

---

## 1. Definition and mathematical foundation

KNN predicts from the outcomes of the most similar historical feature vectors. It makes no global parametric assumption, so it can capture local structure - but in a high-dimensional feature space distances concentrate and neighbourhoods stop being meaningful.

## 2. Objective

Test whether local similarity in feature space predicts the next outcome.

## 3. Complete formula

```
\hat{P}(Y=k\mid x)=\frac{1}{K}\sum_{i \in N_K(x)}\mathbf{1}[y_i=k]
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `N_K(x)` | the K nearest neighbours |
| `K` | neighbourhood size |

## 5. Statistical assumptions

- Similar feature vectors imply similar outcome distributions
- The distance metric is meaningful

## 6. Required input data

Several thousand observations.

## 7. Step-by-step manual calculation

1. Standardise features inside each fold
2. Find the K nearest historical rows
3. Average their outcomes into a probability vector

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Worked arithmetic for tree/kernel/neural models on a ten-point sequence is not meaningful - they would memorise it. The out-of-sample log-loss comparison in the computed section is the operative evidence, and it is reported against the strongest baseline with a dependence-aware confidence interval.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 2.39049 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 0.91247 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.09777 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.30245 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 0.08791 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | -0.17130 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.06310 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** K-nearest neighbbours: out-of-sample log loss 2.39049 against 2.30259 for the best baseline (uniform), a difference of +0.08791 (positive is worse; paired block-bootstrap 95% CI +0.05942 to +0.11727). Accuracy 0.0978, top-3 0.3025, Brier 0.91247, ECE 0.0631, calibration slope -0.1713. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.39049 vs 2.30259); paired block-bootstrap 95% CI [0.06247, 0.12046] includes zero With ~60 standardised features, distances concentrate and neighbourhoods stop being meaningful; that is a dimensionality finding, not an implementation issue.

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
| `log_loss` | 2.39723 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 0.91076 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.09813 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.31417 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 0.09465 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | -0.49780 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.06054 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** K-nearest neighbbours: out-of-sample log loss 2.39723 against 2.30259 for the best baseline (uniform), a difference of +0.09465 (positive is worse; paired block-bootstrap 95% CI +0.05983 to +0.13497). Accuracy 0.0981, top-3 0.3142, Brier 0.91076, ECE 0.0605, calibration slope -0.4978. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.39723 vs 2.30259); paired block-bootstrap 95% CI [0.05990, 0.14123] includes zero With ~60 standardised features, distances concentrate and neighbourhoods stop being meaningful; that is a dimensionality finding, not an implementation issue.

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
| Open | computed | `log_loss` | 2.39723 |
| Close | computed | `log_loss` | 2.39049 |

Open produced log_loss=2.39723; Close produced log_loss=2.39049. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Needs thousands of observations per fold to be meaningful; below that the parameter count dominates and every model converges on the marginal.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending on cost) on an expanding window, never tuned on the evaluation window, and promoted only if it beats the strongest baseline by more than 0.002 nats with a bootstrap interval excluding zero and stable across folds.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

With 60+ dimensions the curse of dimensionality dominates, which is itself the finding.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
