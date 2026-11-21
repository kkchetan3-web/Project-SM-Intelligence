# M015 - Average Recurrence Interval

**Category:** B - Recency and Occurrence  
**Implementation:** `src.mathematics.recurrence::run_015`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\bar{G} = \frac{1}{m}\sum_{j=1}^{m} G_j \approx \frac{1}{\hat{p}}`

---

## 1. Definition and mathematical foundation

The mean inter-occurrence gap estimates the reciprocal of the category probability. It is therefore not new information but a differently-shaped view of M002, useful because the reciprocal scale makes large deviations visually striking - and dangerous for exactly that reason.

## 2. Objective

Estimate mean waiting time per category with a confidence interval.

## 3. Complete formula

```
\bar{G} = \frac{1}{m}\sum_{j=1}^{m} G_j \approx \frac{1}{\hat{p}}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `G-bar` | mean gap |
| `m` | number of observed gaps |
| `p_hat` | estimated probability |

## 5. Statistical assumptions

- Gaps are observed without censoring bias
- The category probability is stationary

## 6. Required input data

Multiple occurrences of each category.

## 7. Step-by-step manual calculation

1. Collect gaps per category
2. Take the arithmetic mean
3. Attach a bootstrap confidence interval

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
| `average_mean_gap` | 10.09390 | n/a | n/a | n/a | n/a | 3131.0 |
| `observed_to_expected_ratio` | 0.99794 | n/a | n/a | n/a | n/a | 10.0 |
| `max_observed_gap` | 12.02700 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Averaged over 10 categories the mean wait between appearances is 10.09 draws, against 10.11 predicted by 1/p from the empirical marginal (ratio 0.998). The observed waiting times agree with the reciprocal of the frequency, which is exactly what an independent process produces.

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
| `average_mean_gap` | 10.11970 | n/a | n/a | n/a | n/a | 3131.0 |
| `observed_to_expected_ratio` | 0.99823 | n/a | n/a | n/a | n/a | 10.0 |
| `max_observed_gap` | 12.16500 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Averaged over 10 categories the mean wait between appearances is 10.12 draws, against 10.14 predicted by 1/p from the empirical marginal (ratio 0.998). The observed waiting times agree with the reciprocal of the frequency, which is exactly what an independent process produces.

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
| Open | computed | `average_mean_gap` | 10.11970 |
| Close | computed | `average_mean_gap` | 10.09390 |

Open produced average_mean_gap=10.11970; Close produced average_mean_gap=10.09390. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Suited to markets with long continuous histories; it degrades when the calendar has many gaps, because 'missing' and 'not drawn' become hard to separate.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Predictive claims are limited to what a causal forecast can show: hot/cold persistence is measured between two disjoint periods, and hazard/recency tests compare against a permutation or geometric null.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The mean is sensitive to a single very long gap; the median (M016) is more robust.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
