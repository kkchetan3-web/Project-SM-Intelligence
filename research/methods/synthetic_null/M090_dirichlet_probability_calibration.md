# M090 - Dirichlet Probability Calibration

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_090`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{p}' = \mathrm{softmax}(W \log \hat{p} + b)`

---

## 1. Definition and mathematical foundation

Dirichlet calibration applies a full linear map in log-probability space, which can correct multi-class miscalibration that per-class methods cannot. With K=10 it has 110 parameters, which is dangerous on small samples - hence the L2 shrinkage toward the identity.

## 2. Objective

Recalibrate the full probability vector and evaluate on later data.

## 3. Complete formula

```
\hat{p}' = \mathrm{softmax}(W \log \hat{p} + b)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `W` | calibration matrix |
| `b` | bias vector |
| `l2` | shrinkage toward identity |

## 5. Statistical assumptions

- The miscalibration is approximately log-linear
- The calibration sample supports K x K parameters

## 6. Required input data

At least a few thousand calibration observations for the full map.

## 7. Step-by-step manual calculation

1. Fit W and b on the calibration slice by gradient descent
2. Apply to later predictions
3. Evaluate log loss, ECE and the calibration slope

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Calibration: a forecast of 0.30 that is right 30% of the time is calibrated; the same forecast right 15% of the time needs a downward map. Isotonic fits a monotone step function, Platt fits sigmoid(A logit(p) + B), Dirichlet fits a linear map in log-probability space. All three preserve the ordering of predictions, which is why they can improve log loss but never accuracy.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss_before` | 2.30621 | n/a | n/a | n/a | n/a | 1639.0 |
| `log_loss_after` | 2.31158 | n/a | n/a | n/a | n/a | 1639.0 |
| `log_loss_change` | 0.00537 | n/a | 0.04800 | n/a | n/a | 1639.0 |
| `ece_before` | 0.00868 | n/a | n/a | n/a | n/a | 1639.0 |
| `ece_after` | 0.02236 | n/a | n/a | n/a | n/a | 1639.0 |
| `slope_before` | -0.46700 | n/a | n/a | n/a | n/a | 1639.0 |
| `slope_after` | -1.28530 | n/a | n/a | n/a | n/a | 1639.0 |

**Interpretation.** Dirichlet calibration applied to svm, fitted on the first 40% of the out-of-sample window and scored on the remaining 60%. Log loss moves from 2.30621 to 2.31158 (+0.00537, bootstrap p = 0.048); ECE from 0.0087 to 0.0224; calibration slope from -0.467 to -1.2853. Calibration does not improve the reliability of these predictions on held-out data; the miscalibration here is not of a form this family can correct. Vector scaling in log-probability space can correct multi-class miscalibration that per-class methods miss, at the cost of K x K parameters shrunk toward the identity.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `log_loss_before` | 2.30578 | n/a | n/a | n/a | n/a | 1639.0 |
| `log_loss_after` | 2.31092 | n/a | n/a | n/a | n/a | 1639.0 |
| `log_loss_change` | 0.00514 | n/a | 0.02400 | n/a | n/a | 1639.0 |
| `ece_before` | 0.00464 | n/a | n/a | n/a | n/a | 1639.0 |
| `ece_after` | 0.02073 | n/a | n/a | n/a | n/a | 1639.0 |
| `slope_before` | -1.13010 | n/a | n/a | n/a | n/a | 1639.0 |
| `slope_after` | -0.50750 | n/a | n/a | n/a | n/a | 1639.0 |

**Interpretation.** Dirichlet calibration applied to svm, fitted on the first 40% of the out-of-sample window and scored on the remaining 60%. Log loss moves from 2.30578 to 2.31092 (+0.00514, bootstrap p = 0.024); ECE from 0.0046 to 0.0207; calibration slope from -1.1301 to -0.5075. Calibration does not improve the reliability of these predictions on held-out data; the miscalibration here is not of a form this family can correct. Vector scaling in log-probability space can correct multi-class miscalibration that per-class methods miss, at the cost of K x K parameters shrunk toward the identity.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `log_loss_before` | 2.30578 |
| Close | computed | `log_loss_before` | 2.30621 |

Open produced log_loss_before=2.30578; Close produced log_loss_before=2.30621. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

14 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The parameter count is large relative to typical calibration samples; shrinkage toward the identity is essential and is part of the specification rather than a tuning detail.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
