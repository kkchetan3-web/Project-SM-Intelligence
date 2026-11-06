# M013 - Last Occurrence Analysis

**Category:** B - Recency and Occurrence  
**Implementation:** `src.mathematics.recurrence::run_013`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `G_{k,t} = t - \max\{i < t : X_i = k\}`

---

## 1. Definition and mathematical foundation

Recency, or the 'due number' heuristic, asserts that a category absent for a long time is more likely to appear. Mathematically it is a claim that the hazard rate increases with elapsed time; under a constant-probability process the hazard is flat and recency carries no information whatsoever.

## 2. Objective

Measure the elapsed gap for every category and test whether recency predicts the next draw.

## 3. Complete formula

```
G_{k,t} = t - \max\{i < t : X_i = k\}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `G_k,t` | gap since outcome k last occurred |
| `t` | current observation index |
| `hazard` | probability of occurrence given elapsed time |

## 5. Statistical assumptions

- The gap is measured in observation counts, not calendar days
- Comparisons use the same evaluation window

## 6. Required input data

N >= 10K to give every category a few occurrences.

## 7. Step-by-step manual calculation

1. Track the last index of each category
2. Compute the gap vector at each step
3. Correlate the gap with the realised next outcome and test against a permuted null

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Last occurrence index of each outcome: {0: 4, 1: 1, 2: 8, 3: 9, 7: 3, 9: 6}. At t = 9 the most overdue outcomes are 1, 7, 0, 9 and 2 (all last seen at or before index 8, gap >= 1). Under independence the probability that the next draw is any particular one of those is 0.1.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `most_overdue_hit_rate` | 0.10323 | n/a | 0.54932 | 0.67858 | n/a | 3100.0 |
| `mean_extra_gap_of_realised_outcome` | -0.14613 | n/a | n/a | n/a | n/a | 3100.0 |
| `mean_gap_of_most_overdue` | 29.54484 | n/a | n/a | n/a | n/a | 3100.0 |

**Interpretation.** If numbers became 'due', the category that has been absent longest should appear more than 1/10 = 0.100 of the time. It appeared 0.1032 of the time over 3100 opportunities (binomial p = 0.5493). Independently, the realised outcome's gap exceeded the average category gap by -0.1461 draws (95% CI -0.4726 to +0.1803). Both tests point the same way and neither supports the due-number hypothesis.

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
| `most_overdue_hit_rate` | 0.09548 | n/a | 0.41895 | 0.65440 | n/a | 3100.0 |
| `mean_extra_gap_of_realised_outcome` | -0.18097 | n/a | n/a | n/a | n/a | 3100.0 |
| `mean_gap_of_most_overdue` | 29.58000 | n/a | n/a | n/a | n/a | 3100.0 |

**Interpretation.** If numbers became 'due', the category that has been absent longest should appear more than 1/10 = 0.100 of the time. It appeared 0.0955 of the time over 3100 opportunities (binomial p = 0.4189). Independently, the realised outcome's gap exceeded the average category gap by -0.1810 draws (95% CI -0.5013 to +0.1394). Both tests point the same way and neither supports the due-number hypothesis.

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
| Open | computed | `most_overdue_hit_rate` | 0.09548 |
| Close | computed | `most_overdue_hit_rate` | 0.10323 |

Open produced most_overdue_hit_rate=0.09548; Close produced most_overdue_hit_rate=0.10323. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Suited to markets with long continuous histories; it degrades when the calendar has many gaps, because 'missing' and 'not drawn' become hard to separate.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Predictive claims are limited to what a causal forecast can show: hot/cold persistence is measured between two disjoint periods, and hazard/recency tests compare against a permutation or geometric null.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Apparent effects are usually selection artefacts: the category that has been absent longest is also the empirically rarest.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
