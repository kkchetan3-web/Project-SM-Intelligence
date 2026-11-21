# M014 - Inter-Occurrence Gap Analysis

**Category:** B - Recency and Occurrence  
**Implementation:** `src.mathematics.recurrence::run_014`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `G_j = T_j - T_{j-1}`

---

## 1. Definition and mathematical foundation

The sequence of waiting times between successive appearances of one category is a renewal process. If draws are independent with probability p, the gaps are geometric with mean 1/p and variance (1-p)/p^2. The variance-to-mean ratio is therefore a direct test of the i.i.d. assumption: it should be near 1-p.

## 2. Objective

Characterise the waiting-time distribution and test it against the geometric null.

## 3. Complete formula

```
G_j = T_j - T_{j-1}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `T_j` | index of the j-th occurrence |
| `G_j` | j-th gap |
| `VMR` | variance-to-mean ratio of gaps |

## 5. Statistical assumptions

- Successive gaps are the object of study
- The probability of the category is constant

## 6. Required input data

At least ~20 occurrences of the category.

## 7. Step-by-step manual calculation

1. Extract occurrence indices for the category
2. Form consecutive differences
3. Compare the observed dispersion with the geometric prediction

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Outcome 3 occurs at indices [0, 2, 5, 7, 9], so the gaps are [2, 3, 2, 2].

```
mean gap = 2.250
median gap = 2.0
1/p = 1/0.4 = 2.5
```

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_vmr_ratio` | 9.93703 | n/a | n/a | n/a | n/a | 3131.0 |
| `max_vmr_ratio` | 12.90690 | n/a | n/a | n/a | n/a | 3131.0 |
| `n_categories_assessed` | 10.00000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Across 10 categories the average variance-to-mean ratio relative to the geometric prediction is 9.937, which departs from memorylessness and warrants the formal distributional test in Method 17.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_vmr_ratio` | 9.54431 | n/a | n/a | n/a | n/a | 3131.0 |
| `max_vmr_ratio` | 14.97780 | n/a | n/a | n/a | n/a | 3131.0 |
| `n_categories_assessed` | 10.00000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Across 10 categories the average variance-to-mean ratio relative to the geometric prediction is 9.544, which departs from memorylessness and warrants the formal distributional test in Method 17.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `mean_vmr_ratio` | 9.54431 |
| Close | computed | `mean_vmr_ratio` | 9.93703 |

Open produced mean_vmr_ratio=9.54431; Close produced mean_vmr_ratio=9.93703. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Suited to markets with long continuous histories; it degrades when the calendar has many gaps, because 'missing' and 'not drawn' become hard to separate.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Predictive claims are limited to what a causal forecast can show: hot/cold persistence is measured between two disjoint periods, and hazard/recency tests compare against a permutation or geometric null.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Gaps to the first and last occurrence are censored; ignoring that biases the mean downward.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
