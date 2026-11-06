# M089 - Platt Probability Calibration

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_089`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(y=1\mid s)=\frac{1}{1+e^{As+B}}`

---

## 1. Definition and mathematical foundation

Platt scaling fits a two-parameter logistic transformation to raw scores. It is far more constrained than isotonic regression, which makes it safer on small calibration samples and unable to correct non-monotone miscalibration.

## 2. Objective

Recalibrate with a parametric sigmoid fitted on a separate slice.

## 3. Complete formula

```
P(y=1\mid s)=\frac{1}{1+e^{As+B}}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `A` | slope parameter |
| `B` | intercept parameter |
| `s` | raw score |

## 5. Statistical assumptions

- The miscalibration is approximately sigmoidal
- The calibration sample is representative

## 6. Required input data

Several hundred calibration observations.

## 7. Step-by-step manual calculation

1. Fit the logistic transformation per class on the calibration slice
2. Apply and renormalise
3. Compare calibrated and uncalibrated log loss

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Calibration: a forecast of 0.30 that is right 30% of the time is calibrated; the same forecast right 15% of the time needs a downward map. Isotonic fits a monotone step function, Platt fits sigmoid(A logit(p) + B), Dirichlet fits a linear map in log-probability space. All three preserve the ordering of predictions, which is why they can improve log loss but never accuracy.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss_before` | 2.21764 | n/a | n/a | n/a | n/a | 1639.0 |
| `log_loss_after` | 2.22539 | n/a | n/a | n/a | n/a | 1639.0 |
| `log_loss_change` | 0.00775 | n/a | 0.01200 | n/a | n/a | 1639.0 |
| `ece_before` | 0.06731 | n/a | n/a | n/a | n/a | 1639.0 |
| `ece_after` | 0.05211 | n/a | n/a | n/a | n/a | 1639.0 |
| `slope_before` | 0.44950 | n/a | n/a | n/a | n/a | 1639.0 |
| `slope_after` | 0.58190 | n/a | n/a | n/a | n/a | 1639.0 |

**Interpretation.** Platt scaling applied to random_forest, fitted on the first 40% of the out-of-sample window and scored on the remaining 60%. Log loss moves from 2.21764 to 2.22539 (+0.00775, bootstrap p = 0.012); ECE from 0.0673 to 0.0521; calibration slope from 0.4495 to 0.5819. Calibration improves the probability quality, which matters if the numbers are read as probabilities rather than as a ranking. It does not and cannot improve accuracy - recalibration is a monotone reshaping, so the predicted ordering is unchanged. Platt scaling fits two parameters per class, so it is far safer on small calibration samples and correspondingly less able to correct anything beyond a sigmoidal distortion.

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
| `log_loss_after` | 2.11865 | n/a | n/a | n/a | n/a | 1639.0 |
| `log_loss_change` | 0.00641 | n/a | 0.05600 | n/a | n/a | 1639.0 |
| `ece_before` | 0.08511 | n/a | n/a | n/a | n/a | 1639.0 |
| `ece_after` | 0.07466 | n/a | n/a | n/a | n/a | 1639.0 |
| `slope_before` | 0.44690 | n/a | n/a | n/a | n/a | 1639.0 |
| `slope_after` | 0.41920 | n/a | n/a | n/a | n/a | 1639.0 |

**Interpretation.** Platt scaling applied to catboost, fitted on the first 40% of the out-of-sample window and scored on the remaining 60%. Log loss moves from 2.11223 to 2.11865 (+0.00641, bootstrap p = 0.056); ECE from 0.0851 to 0.0747; calibration slope from 0.4469 to 0.4192. Calibration improves the probability quality, which matters if the numbers are read as probabilities rather than as a ranking. It does not and cannot improve accuracy - recalibration is a monotone reshaping, so the predicted ordering is unchanged. Platt scaling fits two parameters per class, so it is far safer on small calibration samples and correspondingly less able to correct anything beyond a sigmoidal distortion.

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

Two parameters cannot fix arbitrary miscalibration, and the renormalisation step distorts the fitted per-class maps.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Platt (1999)
