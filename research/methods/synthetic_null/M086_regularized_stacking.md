# M086 - Regularized Stacking

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_086`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `w^{*}=\arg\min_{w \in \Delta^{M-1}}\| \sum_m w_m \hat{p}_m - y \|^2`

---

## 1. Definition and mathematical foundation

Stacking learns a second-level combiner from out-of-fold predictions. The simplex constraint is the regularisation: it prevents negative weights and extrapolation, which are the main ways stacking overfits.

## 2. Objective

Fit a constrained meta-learner on out-of-fold predictions.

## 3. Complete formula

```
w^{*}=\arg\min_{w \in \Delta^{M-1}}\| \sum_m w_m \hat{p}_m - y \|^2
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `w` | meta-weights |
| `p_m` | base probability matrix |

## 5. Statistical assumptions

- Base predictions are genuinely out of fold
- The meta-sample is disjoint from the test

## 6. Required input data

Out-of-fold predictions from at least three models.

## 7. Step-by-step manual calculation

1. Generate strictly out-of-fold base predictions
2. Fit simplex-constrained weights
3. Evaluate the stack on untouched later data

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

The arithmetic is the ensemble/metric formula stated above; the substantive question is always whether the held-out comparison clears its uncertainty band, which is what the computed section reports.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `stack_holdout_log_loss` | 2.30717 | n/a | n/a | n/a | n/a | 1093.0 |
| `iterative_weight_mass` | 0.77577 | n/a | n/a | n/a | n/a | 10.0 |
| `improved_over_best_base` | 0.00000 | n/a | n/a | n/a | n/a | 10.0 |
| `beats_strongest_baseline` | 0.00000 | n/a | n/a | n/a | n/a | 1093.0 |

**Interpretation.** Simplex-constrained stacking on a 60/40 split of the out-of-sample window: holdout log loss 2.30717, with 0.776 of the weight on svm. It does not improve on the best individual base model (2.30656). The stack therefore inherits the weakness of its members rather than correcting it.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `stack_holdout_log_loss` | 2.30436 | n/a | n/a | n/a | n/a | 1093.0 |
| `iterative_weight_mass` | 0.86017 | n/a | n/a | n/a | n/a | 10.0 |
| `improved_over_best_base` | 0.00000 | n/a | n/a | n/a | n/a | 10.0 |
| `beats_strongest_baseline` | 0.00000 | n/a | n/a | n/a | n/a | 1093.0 |

**Interpretation.** Simplex-constrained stacking on a 60/40 split of the out-of-sample window: holdout log loss 2.30436, with 0.860 of the weight on svm. It does not improve on the best individual base model (2.30388). The stack therefore inherits the weakness of its members rather than correcting it.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `stack_holdout_log_loss` | 2.30436 |
| Close | computed | `stack_holdout_log_loss` | 2.30717 |

Open produced stack_holdout_log_loss=2.30436; Close produced stack_holdout_log_loss=2.30717. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The meta-sample is small relative to the number of base models, and any leakage in the base predictions is amplified at this level.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
