# M073 - Logistic Regression

**Category:** G - Machine Learning  
**Implementation:** `src.mathematics.machine_learning::run_073`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(Y=1\mid X)=\frac{1}{1+e^{-(\beta_0+\beta^{T}X)}}`

---

## 1. Definition and mathematical foundation

Binary logistic regression models log-odds as a linear function of features. Here the binary task is deliberately the coarsest useful one - predicting parity - because a linear model cannot represent a cyclic dependence over ten categories but can handle a two-class split honestly.

## 2. Objective

Fit a binary logistic model and evaluate its probabilities chronologically.

## 3. Complete formula

```
P(Y=1\mid X)=\frac{1}{1+e^{-(\beta_0+\beta^{T}X)}}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `beta` | coefficient vector |
| `X` | feature vector |
| `p` | event probability |

## 5. Statistical assumptions

- Log-odds are linear in the features
- Observations are conditionally independent

## 6. Required input data

Several hundred observations per fold.

## 7. Step-by-step manual calculation

1. Assemble causal features
2. Fit on an expanding window with L2 regularisation
3. Score out of sample against the parity-frequency baseline

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

A multinomial logistic model with d features and K=10 classes has 10(d+1) coefficients. With, say, d=60 that is 610 parameters; the smallest sample in this study (n=3131, of which 400 are used for the first fit) is the binding constraint, which is why regularisation and refit cadence are part of the specification rather than tuning knobs.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `binary_log_loss` | 0.71965 | n/a | n/a | n/a | n/a | 2349.0 |
| `parity_base_rate` | 0.48721 | n/a | n/a | n/a | n/a | 2349.0 |
| `log_loss_difference_vs_base_rate` | 0.02534 | n/a | 0.00000 | n/a | n/a | 2349.0 |
| `parity_accuracy` | 0.50021 | n/a | n/a | n/a | n/a | 2349.0 |
| `uniform_parity_log_loss` | 0.69315 | n/a | n/a | n/a | n/a | 2349.0 |

**Interpretation.** Binary logistic regression for parity, refitted 30 times over 2349 out-of-sample predictions, scores 0.71965 nats against 0.69431 for the fixed base rate (0.4872) and 0.69315 for a coin flip. Accuracy is 0.5002. Difference from the base-rate forecast is +0.02534 (bootstrap 95% CI +0.01543 to +0.03550). Framing the task as binary does not rescue it: parity is not predictable from the feature set.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `binary_log_loss` | 0.71810 | n/a | n/a | n/a | n/a | 2349.0 |
| `parity_base_rate` | 0.51662 | n/a | n/a | n/a | n/a | 2349.0 |
| `log_loss_difference_vs_base_rate` | 0.02529 | n/a | 0.00000 | n/a | n/a | 2349.0 |
| `parity_accuracy` | 0.50490 | n/a | n/a | n/a | n/a | 2349.0 |
| `uniform_parity_log_loss` | 0.69315 | n/a | n/a | n/a | n/a | 2349.0 |

**Interpretation.** Binary logistic regression for parity, refitted 30 times over 2349 out-of-sample predictions, scores 0.71810 nats against 0.69281 for the fixed base rate (0.5166) and 0.69315 for a coin flip. Accuracy is 0.5049. Difference from the base-rate forecast is +0.02529 (bootstrap 95% CI +0.01558 to +0.03440). Framing the task as binary does not rescue it: parity is not predictable from the feature set.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `binary_log_loss` | 0.71810 |
| Close | computed | `binary_log_loss` | 0.71965 |

Open produced binary_log_loss=0.71810; Close produced binary_log_loss=0.71965. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Needs thousands of observations per fold to be meaningful; below that the parameter count dominates and every model converges on the marginal.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending on cost) on an expanding window, never tuned on the evaluation window, and promoted only if it beats the strongest baseline by more than 0.002 nats with a bootstrap interval excluding zero and stable across folds.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Linear log-odds capture only monotone effects; the cyclic structure of digit sequences is invisible to it.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
