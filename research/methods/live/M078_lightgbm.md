# M078 - LightGBM

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_078`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\text{leaf-wise growth with histogram binning}`

---

## 1. Definition and mathematical foundation

LightGBM grows trees leaf-wise and bins continuous features into histograms, which makes it fast and able to find deep interactions in large data. On modest samples the leaf-wise growth can overfit unless leaf size is constrained.

## 2. Objective

Evaluate histogram-based boosting with explicit leaf-size control.

## 3. Complete formula

```
\text{leaf-wise growth with histogram binning}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `num_leaves` | maximum leaves per tree |
| `min_data_in_leaf` | minimum observations per leaf |

## 5. Statistical assumptions

- Histogram binning preserves the relevant feature information
- Leaf constraints prevent overfitting

## 6. Required input data

Several thousand observations.

## 7. Step-by-step manual calculation

1. Configure leaf-wise growth with a leaf-size floor
2. Train chronologically
3. Evaluate out of sample against the other boosted model

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Worked arithmetic for tree/kernel/neural models on a ten-point sequence is not meaningful - they would memorise it. The out-of-sample log-loss comparison in the computed section is the operative evidence, and it is reported against the strongest baseline with a dependence-aware confidence interval.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 2.62137 | n/a | n/a | n/a | n/a | 3743.0 |
| `brier` | 0.97447 | n/a | n/a | n/a | n/a | 3743.0 |
| `accuracy` | 0.10286 | n/a | n/a | n/a | n/a | 3743.0 |
| `top3_accuracy` | 0.30270 | n/a | n/a | n/a | n/a | 3743.0 |
| `log_loss_difference_vs_baseline` | 0.31879 | n/a | 0.00000 | n/a | n/a | 3743.0 |
| `calibration_slope` | -0.06430 | n/a | n/a | n/a | n/a | 3743.0 |
| `expected_calibration_error` | 0.18567 | n/a | n/a | n/a | n/a | 3743.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** LightGBM: out-of-sample log loss 2.62137 against 2.30259 for the best baseline (uniform), a difference of +0.31879 (positive is worse; paired block-bootstrap 95% CI +0.28887 to +0.34563). Accuracy 0.1029, top-3 0.3027, Brier 0.97447, ECE 0.1857, calibration slope -0.0643. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.62137 vs 2.30259); paired block-bootstrap 95% CI [0.29183, 0.34579] includes zero Leaf-wise growth with a leaf-size floor; same conclusion as XGBoost.

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
| `log_loss` | 2.63621 | n/a | n/a | n/a | n/a | 3743.0 |
| `brier` | 0.97918 | n/a | n/a | n/a | n/a | 3743.0 |
| `accuracy` | 0.09698 | n/a | n/a | n/a | n/a | 3743.0 |
| `top3_accuracy` | 0.30190 | n/a | n/a | n/a | n/a | 3743.0 |
| `log_loss_difference_vs_baseline` | 0.33363 | n/a | 0.00000 | n/a | n/a | 3743.0 |
| `calibration_slope` | -0.29010 | n/a | n/a | n/a | n/a | 3743.0 |
| `expected_calibration_error` | 0.19398 | n/a | n/a | n/a | n/a | 3743.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** LightGBM: out-of-sample log loss 2.63621 against 2.30259 for the best baseline (uniform), a difference of +0.33363 (positive is worse; paired block-bootstrap 95% CI +0.30550 to +0.36320). Accuracy 0.0970, top-3 0.3019, Brier 0.97918, ECE 0.1940, calibration slope -0.2901. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.63621 vs 2.30259); paired block-bootstrap 95% CI [0.30485, 0.36436] includes zero Leaf-wise growth with a leaf-size floor; same conclusion as XGBoost.

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
| Open | computed | `log_loss` | 2.63621 |
| Close | computed | `log_loss` | 2.62137 |

Open produced log_loss=2.63621; Close produced log_loss=2.62137. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Needs thousands of observations per fold to be meaningful; below that the parameter count dominates and every model converges on the marginal.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending on cost) on an expanding window, never tuned on the evaluation window, and promoted only if it beats the strongest baseline by more than 0.002 nats with a bootstrap interval excluding zero and stable across folds.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Speed is not accuracy: the same lack of signal caps every boosted implementation.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Ke et al. (2017)
