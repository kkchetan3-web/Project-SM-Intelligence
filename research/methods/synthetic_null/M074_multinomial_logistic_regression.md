# M074 - Multinomial Logistic Regression

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_074`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(Y=k\mid X)=\frac{e^{\beta_k^{T}X}}{\sum_j e^{\beta_j^{T}X}}`

---

## 1. Definition and mathematical foundation

Multinomial logistic regression produces a full probability distribution over ten outcomes with a shared linear structure. It is the honest baseline for 'can a learned model beat simple frequencies', and the coefficient count (K x d) makes its data appetite clear.

## 2. Objective

Produce a complete 10-way distribution and compare it with frequency baselines.

## 3. Complete formula

```
P(Y=k\mid X)=\frac{e^{\beta_k^{T}X}}{\sum_j e^{\beta_j^{T}X}}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `beta_k` | coefficient vector for class k |
| `K` | number of classes |

## 5. Statistical assumptions

- The log-odds are linear in the features
- The outcome space is complete

## 6. Required input data

Several thousand observations for a stable fit.

## 7. Step-by-step manual calculation

1. Assemble causal features
2. Fit with multinomial loss and L2 penalty
3. Evaluate log loss, Brier score and calibration out of sample

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

A multinomial logistic model with d features and K=10 classes has 10(d+1) coefficients. With, say, d=60 that is 610 parameters; the smallest sample in this study (n=3131, of which 400 are used for the first fit) is the binding constraint, which is why regularisation and refit cadence are part of the specification rather than tuning knobs.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss` | 2.52432 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 0.94816 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.08971 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.28781 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 0.22174 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | -0.21990 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.14315 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** Multinomial logistic regression: out-of-sample log loss 2.52432 against 2.30259 for the best baseline (uniform), a difference of +0.22174 (positive is worse; paired block-bootstrap 95% CI +0.19554 to +0.25106). Accuracy 0.0897, top-3 0.2878, Brier 0.94816, ECE 0.1431, calibration slope -0.2199. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.52432 vs 2.30259); paired block-bootstrap 95% CI [0.19443, 0.24938] includes zero The full 10-way model is the honest test of whether a linear learned mapping beats simple frequencies; it does not, and the reason is visible in the calibration output - the model defaults toward the marginal.

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
| `log_loss` | 2.48126 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 0.93873 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.10143 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.31051 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 0.17867 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | 0.18580 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.13168 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** Multinomial logistic regression: out-of-sample log loss 2.48126 against 2.30259 for the best baseline (uniform), a difference of +0.17867 (positive is worse; paired block-bootstrap 95% CI +0.15210 to +0.20573). Accuracy 0.1014, top-3 0.3105, Brier 0.93873, ECE 0.1317, calibration slope 0.1858. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (uniform) on out-of-sample log loss (2.48126 vs 2.30259); paired block-bootstrap 95% CI [0.15243, 0.20574] includes zero The full 10-way model is the honest test of whether a linear learned mapping beats simple frequencies; it does not, and the reason is visible in the calibration output - the model defaults toward the marginal.

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
| Open | computed | `log_loss` | 2.48126 |
| Close | computed | `log_loss` | 2.52432 |

Open produced log_loss=2.48126; Close produced log_loss=2.52432. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Needs thousands of observations per fold to be meaningful; below that the parameter count dominates and every model converges on the marginal.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending on cost) on an expanding window, never tuned on the evaluation window, and promoted only if it beats the strongest baseline by more than 0.002 nats with a bootstrap interval excluding zero and stable across folds.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

With 60+ features and 10 classes the parameter count is large relative to the sample; regularisation strength is the binding constraint.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
