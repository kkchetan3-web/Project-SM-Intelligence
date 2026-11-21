# M085 - Bayesian Model Averaging

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_085`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(Y\mid D)=\sum_m P(Y\mid M_m,D)P(M_m\mid D)`

---

## 1. Definition and mathematical foundation

BMA weights models by their posterior probability, which penalises complexity through the evidence term. It is the principled alternative to picking a single winner, and it degrades gracefully when no model is clearly best.

## 2. Objective

Combine models by posterior model probability.

## 3. Complete formula

```
P(Y\mid D)=\sum_m P(Y\mid M_m,D)P(M_m\mid D)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `M_m` | model m |
| `P(M_m|D)` | posterior model probability |

## 5. Statistical assumptions

- The model space is enumerable
- Posterior probabilities are estimable

## 6. Required input data

Several candidate models with out-of-sample predictions.

## 7. Step-by-step manual calculation

1. Compute each model's marginal likelihood approximation
2. Normalise to posterior weights
3. Average the predictive distributions

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

The arithmetic is the ensemble/metric formula stated above; the substantive question is always whether the held-out comparison clears its uncertainty band, which is what the computed section reports.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `bma_log_loss_holdout` | 2.20986 | n/a | n/a | n/a | n/a | 1366.0 |
| `best_baseline_log_loss` | 2.18979 | n/a | n/a | n/a | n/a | 1366.0 |
| `bma_minus_baseline` | 0.02007 | n/a | n/a | n/a | n/a | 1366.0 |
| `effective_n_models` | 1.00000 | n/a | n/a | n/a | n/a | 10.0 |
| `top_model_weight` | 1.00000 | n/a | n/a | n/a | n/a | 10.0 |

**Interpretation.** BIC-approximated posterior model probabilities (fitted on the first half of the out-of-sample window, scored on the second) concentrate 1.000 of the mass on random_forest; the effective number of models is 1.00 of 10. The averaged forecast scores 2.20986 against 2.18979 for the strongest baseline (markov1). Averaging cannot manufacture accuracy from models that are all near-random; it only reduces variance around the same wrong answer. Note the BIC evidence approximation is crude for these non-nested models and is labelled as an approximation wherever reported.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `bma_log_loss_holdout` | 2.11937 | n/a | n/a | n/a | n/a | 1366.0 |
| `best_baseline_log_loss` | 2.09933 | n/a | n/a | n/a | n/a | 1366.0 |
| `bma_minus_baseline` | 0.02004 | n/a | n/a | n/a | n/a | 1366.0 |
| `effective_n_models` | 1.00000 | n/a | n/a | n/a | n/a | 10.0 |
| `top_model_weight` | 1.00000 | n/a | n/a | n/a | n/a | 10.0 |

**Interpretation.** BIC-approximated posterior model probabilities (fitted on the first half of the out-of-sample window, scored on the second) concentrate 1.000 of the mass on catboost; the effective number of models is 1.00 of 10. The averaged forecast scores 2.11937 against 2.09933 for the strongest baseline (markov1). Averaging cannot manufacture accuracy from models that are all near-random; it only reduces variance around the same wrong answer. Note the BIC evidence approximation is crude for these non-nested models and is labelled as an approximation wherever reported.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `bma_log_loss_holdout` | 2.11937 |
| Close | computed | `bma_log_loss_holdout` | 2.20986 |

Open produced bma_log_loss_holdout=2.11937; Close produced bma_log_loss_holdout=2.20986. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The BIC approximation to the evidence is crude for non-nested models, so the weights are an approximation and are labelled as one.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
