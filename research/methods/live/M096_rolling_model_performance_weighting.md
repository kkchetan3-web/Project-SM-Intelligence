# M096 - Rolling Model Performance Weighting

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_096`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `w_{m,t} = \frac{\exp(-\gamma \bar{L}_{m,t-W:t})}{\sum_j \exp(-\gamma \bar{L}_{j,t-W:t})}`

---

## 1. Definition and mathematical foundation

Adaptive weighting shifts ensemble mass toward models that have recently performed well. It helps when relative performance is persistent and hurts when it is noise - which is precisely the regime these markets inhabit.

## 2. Objective

Test whether adaptive weighting improves on fixed weights.

## 3. Complete formula

```
w_{m,t} = \frac{\exp(-\gamma \bar{L}_{m,t-W:t})}{\sum_j \exp(-\gamma \bar{L}_{j,t-W:t})}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `w_m,t` | weight for model m at time t |
| `gamma` | sharpness |
| `W` | lookback window |

## 5. Statistical assumptions

- Recent performance predicts near-future performance
- Weights are computed causally

## 6. Required input data

A long out-of-sample window.

## 7. Step-by-step manual calculation

1. Compute rolling per-model log loss using only past steps
2. Convert to weights with a softmax
3. Apply to the next step and evaluate the resulting ensemble

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

The arithmetic is the ensemble/metric formula stated above; the substantive question is always whether the held-out comparison clears its uncertainty band, which is what the computed section reports.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `adaptive_weighting_log_loss` | 2.34534 | n/a | n/a | n/a | n/a | 3743.0 |
| `equal_weight_log_loss` | 2.36611 | n/a | n/a | n/a | n/a | 3743.0 |
| `adaptive_minus_equal` | -0.02077 | n/a | n/a | n/a | n/a | 3743.0 |
| `best_baseline_log_loss` | 2.30259 | n/a | n/a | n/a | n/a | 3743.0 |
| `mean_weight_volatility` | 0.00702 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** Adaptive weighting (250-step lookback, causal at every point) scores 2.34534 against 2.36611 for equal weights, a change of -0.02077. Weights move by 0.0070 on average per step. The strongest baseline scores 2.30259. Adaptive weighting helps here, meaning recent relative performance does carry information about near-future performance. Weights are computed only from steps strictly before each prediction, so this is not a retrospective curve-fit.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `adaptive_weighting_log_loss` | 2.34988 | n/a | n/a | n/a | n/a | 3743.0 |
| `equal_weight_log_loss` | 2.37267 | n/a | n/a | n/a | n/a | 3743.0 |
| `adaptive_minus_equal` | -0.02279 | n/a | n/a | n/a | n/a | 3743.0 |
| `best_baseline_log_loss` | 2.30259 | n/a | n/a | n/a | n/a | 3743.0 |
| `mean_weight_volatility` | 0.00752 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** Adaptive weighting (250-step lookback, causal at every point) scores 2.34988 against 2.37267 for equal weights, a change of -0.02279. Weights move by 0.0075 on average per step. The strongest baseline scores 2.30259. Adaptive weighting helps here, meaning recent relative performance does carry information about near-future performance. Weights are computed only from steps strictly before each prediction, so this is not a retrospective curve-fit.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `adaptive_weighting_log_loss` | 2.34988 |
| Close | computed | `adaptive_weighting_log_loss` | 2.34534 |

Open produced adaptive_weighting_log_loss=2.34988; Close produced adaptive_weighting_log_loss=2.34534. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

In a world where all models perform equally, adaptive weighting adds pure noise to the combination.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
