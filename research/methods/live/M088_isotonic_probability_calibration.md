# M088 - Isotonic Probability Calibration

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_088`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{p}_{\text{iso}} = \arg\min_{g \text{ monotone}} \sum_i (g(\hat{p}_i)-y_i)^2`

---

## 1. Definition and mathematical foundation

Isotonic regression fits the best monotone mapping from raw scores to observed frequencies. It is nonparametric and flexible, which is both its strength and its overfitting risk on small calibration samples.

## 2. Objective

Recalibrate probabilities with a monotone mapping fitted on a separate slice.

## 3. Complete formula

```
\hat{p}_{\text{iso}} = \arg\min_{g \text{ monotone}} \sum_i (g(\hat{p}_i)-y_i)^2
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `g` | monotone mapping |
| `y_i` | binary outcome of class membership |

## 5. Statistical assumptions

- The calibration relation is monotone
- The calibration sample is large enough

## 6. Required input data

Several hundred calibration observations.

## 7. Step-by-step manual calculation

1. Fit one-vs-rest isotonic models on the calibration slice
2. Apply to later predictions and renormalise
3. Evaluate log loss and the calibration slope

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Calibration: a forecast of 0.30 that is right 30% of the time is calibrated; the same forecast right 15% of the time needs a downward map. Isotonic fits a monotone step function, Platt fits sigmoid(A logit(p) + B), Dirichlet fits a linear map in log-probability space. All three preserve the ordering of predictions, which is why they can improve log loss but never accuracy.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss_before` | 2.30512 | n/a | n/a | n/a | n/a | 2246.0 |
| `log_loss_after` | 2.34995 | n/a | n/a | n/a | n/a | 2246.0 |
| `log_loss_change` | 0.04483 | n/a | 0.00000 | n/a | n/a | 2246.0 |
| `ece_before` | 0.01228 | n/a | n/a | n/a | n/a | 2246.0 |
| `ece_after` | 0.02509 | n/a | n/a | n/a | n/a | 2246.0 |
| `slope_before` | -3.38290 | n/a | n/a | n/a | n/a | 2246.0 |
| `slope_after` | -0.00130 | n/a | n/a | n/a | n/a | 2246.0 |

**Interpretation.** Isotonic calibration applied to svm, fitted on the first 40% of the out-of-sample window and scored on the remaining 60%. Log loss moves from 2.30512 to 2.34995 (+0.04483, bootstrap p = 0.000); ECE from 0.0123 to 0.0251; calibration slope from -3.3829 to -0.0013. Calibration does not improve the reliability of these predictions on held-out data; the miscalibration here is not of a form this family can correct. Isotonic regression is fitted one-vs-rest then renormalised, which makes it flexible but prone to overfitting on short calibration samples.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss_before` | 2.30635 | n/a | n/a | n/a | n/a | 2246.0 |
| `log_loss_after` | 2.47435 | n/a | n/a | n/a | n/a | 2246.0 |
| `log_loss_change` | 0.16800 | n/a | 0.00000 | n/a | n/a | 2246.0 |
| `ece_before` | 0.01667 | n/a | n/a | n/a | n/a | 2246.0 |
| `ece_after` | 0.03380 | n/a | n/a | n/a | n/a | 2246.0 |
| `slope_before` | -0.66530 | n/a | n/a | n/a | n/a | 2246.0 |
| `slope_after` | -0.43890 | n/a | n/a | n/a | n/a | 2246.0 |

**Interpretation.** Isotonic calibration applied to svm, fitted on the first 40% of the out-of-sample window and scored on the remaining 60%. Log loss moves from 2.30635 to 2.47435 (+0.16800, bootstrap p = 0.000); ECE from 0.0167 to 0.0338; calibration slope from -0.6653 to -0.4389. Calibration does not improve the reliability of these predictions on held-out data; the miscalibration here is not of a form this family can correct. Isotonic regression is fitted one-vs-rest then renormalised, which makes it flexible but prone to overfitting on short calibration samples.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `log_loss_before` | 2.30635 |
| Close | computed | `log_loss_before` | 2.30512 |

Open produced log_loss_before=2.30635; Close produced log_loss_before=2.30512. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

14 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Isotonic maps can be non-monotone in the multiclass setting after renormalisation, and they cannot extrapolate beyond the calibration range.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
