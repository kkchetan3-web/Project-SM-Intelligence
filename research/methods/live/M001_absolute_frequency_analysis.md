# M001 - Absolute Frequency Analysis

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_001`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `n_k = \sum_{t=1}^{N} \mathbf{1}[X_t = k]`

---

## 1. Definition and mathematical foundation

In a categorical sequence the vector of counts (n_1..n_K) is a sufficient statistic for the empirical distribution: no other feature of the sample adds information about relative category occurrence. Counts therefore anchor every later method, and any claim about a 'hot' number must ultimately be a claim about n_k.

## 2. Objective

Establish the raw empirical support of every outcome before any modelling.

## 3. Complete formula

```
n_k = \sum_{t=1}^{N} \mathbf{1}[X_t = k]
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `n_k` | count of outcome k |
| `X_t` | outcome at observation t |
| `N` | number of valid observations |
| `K` | size of the outcome space |

## 5. Statistical assumptions

- Each draw is assigned to exactly one category
- Observations are counted within a declared, fixed outcome space

## 6. Required input data

Any non-empty sequence; K is fixed by the market's declared outcome space.

## 7. Step-by-step manual calculation

1. Scan the chronological series and tally each outcome
2. Order categories by descending count
3. Report counts alongside N so proportions can be derived

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Counts per outcome: [1, 1, 1, 5, 0, 0, 0, 1, 0, 1]. Outcome 3 occurs 4 times, so n_3 = 4 and the count for every other observed outcome is 1.

```
n_3 = sum_t 1[X_t = 3] = 4
N   = 10
```

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `max_count` | 465.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `min_count` | 388.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `max_min_ratio` | 1.19845 | n/a | n/a | n/a | n/a | 4143.0 |
| `count_range` | 77.00000 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** 4143 draws over 10 outcomes, so the expected count under uniformity is 414.3. Most frequent: 1 with 465; least frequent: 7 with 393. A ratio of 1.20 between extremes looks large but is the normal consequence of multinomial variation: for N=4143 and K=10 the standard deviation of a count is about 19.3, so a spread of a few standard deviations across 10 categories is expected, not remarkable.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `max_count` | 450.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `min_count` | 376.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `max_min_ratio` | 1.19681 | n/a | n/a | n/a | n/a | 4143.0 |
| `count_range` | 74.00000 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** 4143 draws over 10 outcomes, so the expected count under uniformity is 414.3. Most frequent: 9 with 450; least frequent: 4 with 402. A ratio of 1.20 between extremes looks large but is the normal consequence of multinomial variation: for N=4143 and K=10 the standard deviation of a count is about 19.3, so a spread of a few standard deviations across 10 categories is expected, not remarkable.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `max_count` | 450.00000 |
| Close | computed | `max_count` | 465.00000 |

Open produced max_count=450.00000; Close produced max_count=465.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Counts are descriptive. A large n_k does not make k more likely next; that inference requires the distributional tests in M009-M010.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
