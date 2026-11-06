# M077 - XGBoost

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_077`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `log_loss` | 2.34864 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 0.90874 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.18528 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.40608 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 0.15885 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | 0.53620 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.08886 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** XGBoost: out-of-sample log loss 2.34864 against 2.18979 for the best baseline (markov1), a difference of +0.15885 (positive is worse; paired block-bootstrap 95% CI +0.13327 to +0.18564). Accuracy 0.1853, top-3 0.4061, Brier 0.90874, ECE 0.0889, calibration slope 0.5362. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (markov1) on out-of-sample log loss (2.34864 vs 2.18979); paired block-bootstrap 95% CI [0.13308, 0.18321] includes zero Regularisation and second-order optimisation do not create signal.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 2.24901 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 0.87708 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.26401 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.47309 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 0.14968 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | 0.59050 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.05318 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** XGBoost: out-of-sample log loss 2.24901 against 2.09933 for the best baseline (markov1), a difference of +0.14968 (positive is worse; paired block-bootstrap 95% CI +0.12484 to +0.17338). Accuracy 0.2640, top-3 0.4731, Brier 0.87708, ECE 0.0532, calibration slope 0.5905. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (markov1) on out-of-sample log loss (2.24901 vs 2.09933); paired block-bootstrap 95% CI [0.12456, 0.17163] includes zero Regularisation and second-order optimisation do not create signal.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `log_loss` | 2.24901 |
| Close | computed | `log_loss` | 2.34864 |

Open produced log_loss=2.24901; Close produced log_loss=2.34864. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

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
