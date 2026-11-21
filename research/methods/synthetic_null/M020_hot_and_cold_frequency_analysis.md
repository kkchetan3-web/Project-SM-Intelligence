# M020 - Hot and Cold Frequency Analysis

**Category:** B - Recency and Occurrence  
**Implementation:** `src.mathematics.recurrence::run_020`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `z_k = \frac{n_k - N/K}{\sqrt{N \cdot \frac{1}{K}(1-\frac{1}{K})}}`

---

## 1. Definition and mathematical foundation

Standardising counts converts 'hot' and 'cold' from impressions into z-scores. The critical question is not whether a category is currently hot but whether hotness persists: a genuinely biased die produces persistent z-scores, while a fair die produces a rotating cast of temporarily extreme categories.

## 2. Objective

Identify statistically extreme categories and test whether extremeness persists.

## 3. Complete formula

```
z_k = \frac{n_k - N/K}{\sqrt{N \cdot \frac{1}{K}(1-\frac{1}{K})}}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `z_k` | standardised deviation |
| `N` | total observations |
| `K` | categories |

## 5. Statistical assumptions

- Counts are multinomial
- The z-score is a large-sample approximation

## 6. Required input data

Expected count >= 5 per category.

## 7. Step-by-step manual calculation

1. Compute z per category
2. Split the sample into consecutive periods
3. Correlate hotness in one period with hotness in the next

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Standardised count for outcome 3: z = (4 - 1)/sqrt(10 x 0.1 x 0.9) = 3/0.9487 = 3.162. On ten draws a z of 3 is entirely ordinary; the persistence test needs two long periods, not ten draws.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `hotness_persistence_correlation` | -0.07478 | n/a | 0.83733 | 0.95048 | n/a | 10.0 |
| `n_extreme_categories_period1` | 0.00000 | n/a | n/a | n/a | n/a | 10.0 |
| `same_hot_category_both_periods` | 1.00000 | n/a | n/a | n/a | n/a | 10.0 |

**Interpretation.** Standardised deviations in the first half identify 5 as hottest (z=+1.47); in the second half the hottest is 5 (z=+1.30). The correlation between the two halves' z-scores across categories is -0.075 (p = 0.837). Hot categories do not stay hot: apparent temperature is period-specific noise. 0 categories exceed |z|>1.96 in the first half against 0.5 expected under uniformity.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `hotness_persistence_correlation` | -0.05849 | n/a | 0.87250 | 0.95768 | n/a | 10.0 |
| `n_extreme_categories_period1` | 0.00000 | n/a | n/a | n/a | n/a | 10.0 |
| `same_hot_category_both_periods` | 0.00000 | n/a | n/a | n/a | n/a | 10.0 |

**Interpretation.** Standardised deviations in the first half identify 3 as hottest (z=+1.64); in the second half the hottest is 6 (z=+1.47). The correlation between the two halves' z-scores across categories is -0.058 (p = 0.873). Hot categories do not stay hot: apparent temperature is period-specific noise. 0 categories exceed |z|>1.96 in the first half against 0.5 expected under uniformity.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `hotness_persistence_correlation` | -0.05849 |
| Close | computed | `hotness_persistence_correlation` | -0.07478 |

Open produced hotness_persistence_correlation=-0.05849; Close produced hotness_persistence_correlation=-0.07478. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Suited to markets with long continuous histories; it degrades when the calendar has many gaps, because 'missing' and 'not drawn' become hard to separate.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Predictive claims are limited to what a causal forecast can show: hot/cold persistence is measured between two disjoint periods, and hazard/recency tests compare against a permutation or geometric null.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Z-scores computed on the full sample cannot be used to predict that same sample; the persistence test uses only forward-looking splits.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
