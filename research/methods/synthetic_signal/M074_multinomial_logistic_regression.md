# M074 - Multinomial Logistic Regression

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_074`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `log_loss` | 2.42082 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 0.92431 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.16111 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.38008 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 0.23103 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | -0.02460 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.10142 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** Multinomial logistic regression: out-of-sample log loss 2.42082 against 2.18979 for the best baseline (markov1), a difference of +0.23103 (positive is worse; paired block-bootstrap 95% CI +0.20282 to +0.25996). Accuracy 0.1611, top-3 0.3801, Brier 0.92431, ECE 0.1014, calibration slope -0.0246. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (markov1) on out-of-sample log loss (2.42082 vs 2.18979); paired block-bootstrap 95% CI [0.19988, 0.26095] includes zero The full 10-way model is the honest test of whether a linear learned mapping beats simple frequencies; it does not, and the reason is visible in the calibration output - the model defaults toward the marginal.

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
| `log_loss` | 2.35691 | n/a | n/a | n/a | n/a | 2731.0 |
| `brier` | 0.90493 | n/a | n/a | n/a | n/a | 2731.0 |
| `accuracy` | 0.21091 | n/a | n/a | n/a | n/a | 2731.0 |
| `top3_accuracy` | 0.43391 | n/a | n/a | n/a | n/a | 2731.0 |
| `log_loss_difference_vs_baseline` | 0.25758 | n/a | 0.00000 | n/a | n/a | 2731.0 |
| `calibration_slope` | 0.28780 | n/a | n/a | n/a | n/a | 2731.0 |
| `expected_calibration_error` | 0.07374 | n/a | n/a | n/a | n/a | 2731.0 |
| `folds_beaten` | 0.00000 | n/a | n/a | n/a | n/a | 5.0 |
| `promoted` | 0.00000 | n/a | n/a | n/a | n/a | 2731.0 |

**Interpretation.** Multinomial logistic regression: out-of-sample log loss 2.35691 against 2.09933 for the best baseline (markov1), a difference of +0.25758 (positive is worse; paired block-bootstrap 95% CI +0.22723 to +0.28912). Accuracy 0.2109, top-3 0.4339, Brier 0.90493, ECE 0.0737, calibration slope 0.2878. It beats the baseline in 0 of 5 chronological folds. Verdict: NOT promoted. does not beat the best baseline (markov1) on out-of-sample log loss (2.35691 vs 2.09933); paired block-bootstrap 95% CI [0.22955, 0.28880] includes zero The full 10-way model is the honest test of whether a linear learned mapping beats simple frequencies; it does not, and the reason is visible in the calibration output - the model defaults toward the marginal.

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
| Open | computed | `log_loss` | 2.35691 |
| Close | computed | `log_loss` | 2.42082 |

Open produced log_loss=2.35691; Close produced log_loss=2.42082. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

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
