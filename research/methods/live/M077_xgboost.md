# M077 - XGBoost

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_077`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\mathcal{L}=\sum_i \ell(y_i,\hat{y}_i)+\sum_m\Omega(h_m)`

---

## 1. Definition and mathematical foundation

XGBoost adds explicit regularisation and second-order loss approximations to gradient boosting. The objective exposes the complexity penalty directly, which makes the bias-variance trade-off a tunable quantity rather than an emergent property.

## 2. Objective

Evaluate a regularised boosted-tree implementation.

## 3. Complete formula

```
\mathcal{L}=\sum_i \ell(y_i,\hat{y}_i)+\sum_m\Omega(h_m)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `Omega` | tree complexity penalty |
| `lambda` | L2 leaf penalty |
| `eta` | shrinkage |

## 5. Statistical assumptions

- The regularised objective is correctly specified
- Training is strictly chronological

## 6. Required input data

Several thousand observations.

## 7. Step-by-step manual calculation

1. Configure the regularised objective
2. Train on the expanding window
3. Evaluate the full probability distribution out of sample

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Worked arithmetic for tree/kernel/neural models on a ten-point sequence is not meaningful - they would memorise it. The out-of-sample log-loss comparison in the computed section is the operative evidence, and it is reported against the strongest baseline with a dependence-aware confidence interval.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 2.44406 | n/a | n/a | n/a | n/a | 3743.0 |
| `brier` | 0.93346 | n/a | n/a | n/a | n/a | 3743.0 |
| `accuracy` | 0.09885 | n/a | n/a | n/a | n/a | 3743.0 |
| `top3_accuracy` | 0.30136 | n/a | n/a | n/a | n/a | 3743.0 |
| `log_loss_difference_vs_baseline` | 0.14147 | n/a | 0.00000 | n/a | n/a | 3743.0 |
| `calibration_slope` | -0.05830 | n/a | n/a | n/a | n/a | 3743.0 |
| `expected_calibration_error` | 0.12208 | n/a | n/a | n/a | n/a | 3743.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** XGBoost: out-of-sample log loss 2.44406 against 2.30259 for the best baseline (uniform), a difference of +0.14147 (positive is worse; paired block-bootstrap 95% CI +0.12381 to +0.15839). Accuracy 0.0989, top-3 0.3014, Brier 0.93346, ECE 0.1221, calibration slope -0.0583. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.44406 vs 2.30259); paired block-bootstrap 95% CI [0.12375, 0.15971] includes zero Regularisation and second-order optimisation do not create signal.

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
| `log_loss` | 2.45060 | n/a | n/a | n/a | n/a | 3743.0 |
| `brier` | 0.93563 | n/a | n/a | n/a | n/a | 3743.0 |
| `accuracy` | 0.09939 | n/a | n/a | n/a | n/a | 3743.0 |
| `top3_accuracy` | 0.30671 | n/a | n/a | n/a | n/a | 3743.0 |
| `log_loss_difference_vs_baseline` | 0.14802 | n/a | 0.00000 | n/a | n/a | 3743.0 |
| `calibration_slope` | -0.05740 | n/a | n/a | n/a | n/a | 3743.0 |
| `expected_calibration_error` | 0.12390 | n/a | n/a | n/a | n/a | 3743.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** XGBoost: out-of-sample log loss 2.45060 against 2.30259 for the best baseline (uniform), a difference of +0.14802 (positive is worse; paired block-bootstrap 95% CI +0.12730 to +0.16575). Accuracy 0.0994, top-3 0.3067, Brier 0.93563, ECE 0.1239, calibration slope -0.0574. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.45060 vs 2.30259); paired block-bootstrap 95% CI [0.12897, 0.16722] includes zero Regularisation and second-order optimisation do not create signal.

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
| Open | computed | `log_loss` | 2.45060 |
| Close | computed | `log_loss` | 2.44406 |

Open produced log_loss=2.45060; Close produced log_loss=2.44406. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Needs thousands of observations per fold to be meaningful; below that the parameter count dominates and every model converges on the marginal.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending on cost) on an expanding window, never tuned on the evaluation window, and promoted only if it beats the strongest baseline by more than 0.002 nats with a bootstrap interval excluding zero and stable across folds.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Implementation differences between boosting libraries are second-order compared with the effect of the data having no signal.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Chen & Guestrin (2016)
