# M088 - Isotonic Probability Calibration

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_088`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `log_loss_before` | 2.21764 | n/a | n/a | n/a | n/a | 1639.0 |
| `log_loss_after` | 2.38979 | n/a | n/a | n/a | n/a | 1639.0 |
| `log_loss_change` | 0.17215 | n/a | 0.00000 | n/a | n/a | 1639.0 |
| `ece_before` | 0.06731 | n/a | n/a | n/a | n/a | 1639.0 |
| `ece_after` | 0.03388 | n/a | n/a | n/a | n/a | 1639.0 |
| `slope_before` | 0.44950 | n/a | n/a | n/a | n/a | 1639.0 |
| `slope_after` | 0.50460 | n/a | n/a | n/a | n/a | 1639.0 |

**Interpretation.** Isotonic calibration applied to random_forest, fitted on the first 40% of the out-of-sample window and scored on the remaining 60%. Log loss moves from 2.21764 to 2.38979 (+0.17215, bootstrap p = 0.000); ECE from 0.0673 to 0.0339; calibration slope from 0.4495 to 0.5046. Calibration improves the probability quality, which matters if the numbers are read as probabilities rather than as a ranking. It does not and cannot improve accuracy - recalibration is a monotone reshaping, so the predicted ordering is unchanged. Isotonic regression is fitted one-vs-rest then renormalised, which makes it flexible but prone to overfitting on short calibration samples.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss_before` | 2.11223 | n/a | n/a | n/a | n/a | 1639.0 |
| `log_loss_after` | 2.12901 | n/a | n/a | n/a | n/a | 1639.0 |
| `log_loss_change` | 0.01678 | n/a | 0.25200 | n/a | n/a | 1639.0 |
| `ece_before` | 0.08511 | n/a | n/a | n/a | n/a | 1639.0 |
| `ece_after` | 0.01724 | n/a | n/a | n/a | n/a | 1639.0 |
| `slope_before` | 0.44690 | n/a | n/a | n/a | n/a | 1639.0 |
| `slope_after` | 0.53390 | n/a | n/a | n/a | n/a | 1639.0 |

**Interpretation.** Isotonic calibration applied to catboost, fitted on the first 40% of the out-of-sample window and scored on the remaining 60%. Log loss moves from 2.11223 to 2.12901 (+0.01678, bootstrap p = 0.252); ECE from 0.0851 to 0.0172; calibration slope from 0.4469 to 0.5339. Calibration improves the probability quality, which matters if the numbers are read as probabilities rather than as a ranking. It does not and cannot improve accuracy - recalibration is a monotone reshaping, so the predicted ordering is unchanged. Isotonic regression is fitted one-vs-rest then renormalised, which makes it flexible but prone to overfitting on short calibration samples.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `log_loss_before` | 2.11223 |
| Close | computed | `log_loss_before` | 2.21764 |

Open produced log_loss_before=2.11223; Close produced log_loss_before=2.21764. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

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
