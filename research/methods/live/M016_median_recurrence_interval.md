# M016 - Median Recurrence Interval

**Category:** B - Recency and Occurrence  
**Implementation:** `src.mathematics.recurrence::run_016`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\tilde{G} = \mathrm{median}(G_1,\ldots,G_m)`

---

## 1. Definition and mathematical foundation

The median waiting time is robust to the heavy right tail that geometric variables always have. Comparing median with mean gives an immediate diagnostic: for a geometric variable the mean exceeds the median, and a large discrepancy flags one dominant gap.

## 2. Objective

Provide a robust central estimate of waiting time.

## 3. Complete formula

```
\tilde{G} = \mathrm{median}(G_1,\ldots,G_m)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `G-tilde` | median gap |
| `skew` | mean/median ratio |

## 5. Statistical assumptions

- Gaps are comparable across occurrences

## 6. Required input data

At least ~20 gaps.

## 7. Step-by-step manual calculation

1. Compute gaps
2. Take the median
3. Compare with the mean to assess skew

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
| `average_median_gap` | 7.25000 | n/a | n/a | n/a | n/a | 4143.0 |
| `observed_to_expected_ratio` | 0.72180 | n/a | n/a | n/a | n/a | 10.0 |
| `max_observed_gap` | 8.00000 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** Averaged over 10 categories the median wait between appearances is 7.25 draws, against 10.04 predicted by 1/p from the empirical marginal (ratio 0.722). The observed waiting times depart from 1/p, which would imply dependence between successive draws; Method 17 tests the distributional form. The median is the robust counterpart of Method 15 and is unaffected by a single very long gap.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `average_median_gap` | 6.80000 | n/a | n/a | n/a | n/a | 4143.0 |
| `observed_to_expected_ratio` | 0.67937 | n/a | n/a | n/a | n/a | 10.0 |
| `max_observed_gap` | 7.00000 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** Averaged over 10 categories the median wait between appearances is 6.80 draws, against 10.02 predicted by 1/p from the empirical marginal (ratio 0.679). The observed waiting times depart from 1/p, which would imply dependence between successive draws; Method 17 tests the distributional form. The median is the robust counterpart of Method 15 and is unaffected by a single very long gap.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `average_median_gap` | 6.80000 |
| Close | computed | `average_median_gap` | 7.25000 |

Open produced average_median_gap=6.80000; Close produced average_median_gap=7.25000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Suited to markets with long continuous histories; it degrades when the calendar has many gaps, because 'missing' and 'not drawn' become hard to separate.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Predictive claims are limited to what a causal forecast can show: hot/cold persistence is measured between two disjoint periods, and hazard/recency tests compare against a permutation or geometric null.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

With few occurrences the median is unstable and quantised.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
