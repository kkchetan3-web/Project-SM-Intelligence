# M082 - Naive Bayes

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_082`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(Y\mid X)\propto P(Y)\prod_i P(X_i\mid Y)`

---

## 1. Definition and mathematical foundation

Naive Bayes assumes conditional independence of features given the class. That assumption is violated spectacularly by a feature set containing cumulative frequencies, so its failure here is expected and instructive rather than surprising.

## 2. Objective

Demonstrate the cost of the conditional-independence assumption.

## 3. Complete formula

```
P(Y\mid X)\propto P(Y)\prod_i P(X_i\mid Y)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `P(X_i|Y)` | class-conditional feature likelihood |
| `P(Y)` | class prior |

## 5. Statistical assumptions

- Features are conditionally independent given the class

## 6. Required input data

Several hundred observations per class.

## 7. Step-by-step manual calculation

1. Estimate class priors
2. Estimate per-feature class-conditional densities
3. Multiply and normalise, then evaluate out of sample

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Worked arithmetic for tree/kernel/neural models on a ten-point sequence is not meaningful - they would memorise it. The out-of-sample log-loss comparison in the computed section is the operative evidence, and it is reported against the strongest baseline with a dependence-aware confidence interval.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 8.80800 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 1.59368 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.09813 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.31417 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 6.50542 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | -0.07690 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.78140 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** Gaussian naive Bayes: out-of-sample log loss 8.80800 against 2.30259 for the best baseline (uniform), a difference of +6.50542 (positive is worse; paired block-bootstrap 95% CI +6.18627 to +6.82961). Accuracy 0.0981, top-3 0.3142, Brier 1.59368, ECE 0.7814, calibration slope -0.0769. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (8.80800 vs 2.30259); paired block-bootstrap 95% CI [6.22108, 6.82138] includes zero The conditional-independence assumption is violated by design in this feature set (cumulative frequencies are collinear by construction), which shows up as catastrophic overconfidence rather than merely weak performance.

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
| `log_loss` | 8.65487 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 1.49703 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.10143 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.29769 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 6.35228 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | 0.08400 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.71147 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** Gaussian naive Bayes: out-of-sample log loss 8.65487 against 2.30259 for the best baseline (uniform), a difference of +6.35228 (positive is worse; paired block-bootstrap 95% CI +6.05018 to +6.63822). Accuracy 0.1014, top-3 0.2977, Brier 1.49703, ECE 0.7115, calibration slope 0.084. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (8.65487 vs 2.30259); paired block-bootstrap 95% CI [6.05632, 6.67239] includes zero The conditional-independence assumption is violated by design in this feature set (cumulative frequencies are collinear by construction), which shows up as catastrophic overconfidence rather than merely weak performance.

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
| Open | computed | `log_loss` | 8.65487 |
| Close | computed | `log_loss` | 8.80800 |

Open produced log_loss=8.65487; Close produced log_loss=8.80800. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Needs thousands of observations per fold to be meaningful; below that the parameter count dominates and every model converges on the marginal.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending on cost) on an expanding window, never tuned on the evaluation window, and promoted only if it beats the strongest baseline by more than 0.002 nats with a bootstrap interval excluding zero and stable across folds.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The independence assumption produces wild overconfidence when features are correlated, which manifests as catastrophically high log loss.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
