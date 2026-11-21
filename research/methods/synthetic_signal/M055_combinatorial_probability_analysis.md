# M055 - Combinatorial Probability Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_055`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `|\Omega| = K,\quad P(A) = \frac{|A|}{|\Omega|}`

---

## 1. Definition and mathematical foundation

Combinatorial probability derives a distribution from the structure of the sample space rather than from observation. For a single digit the space is ten equally likely outcomes; for a panel it is a thousand. These theoretical distributions are the reference against which every empirical result here is measured.

## 2. Objective

Derive theoretical distributions and compare them with observation.

## 3. Complete formula

```
|\Omega| = K,\quad P(A) = \frac{|A|}{|\Omega|}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `Omega` | sample space |
| `|A|` | number of favourable outcomes |

## 5. Statistical assumptions

- Each elementary outcome is equally likely under the null
- The sample space is fully enumerated

## 6. Required input data

A fully specified sample space.

## 7. Step-by-step manual calculation

1. Enumerate the sample space
2. Count the outcomes satisfying the event
3. Compare the theoretical probability with the empirical frequency

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

No worked example is defined for this category.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `total_variation_distance` | 0.04612 | n/a | n/a | n/a | n/a | 3131.0 |
| `chi2_vs_theoretical` | 34.05589 | n/a | 8.733e-05 | 0.00035 | n/a | 3131.0 |
| `max_abs_z` | 3.22300 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** With 10 equiprobable outcomes the theoretical probability of each is 0.1000. The observed distribution is a total-variation distance of 0.04612 from that ideal, with the largest single-category z-score at 3.22. The chi-square against the enumerated theoretical distribution is 34.06 (p = 0.0001). This method supplies the null hypothesis; it can reject it but cannot by itself tell you whether a departure is exploitable.

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
| `total_variation_distance` | 0.05318 | n/a | n/a | n/a | n/a | 3131.0 |
| `chi2_vs_theoretical` | 41.91920 | n/a | 3.400e-06 | 1.394e-05 | n/a | 3131.0 |
| `max_abs_z` | 3.40200 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** With 10 equiprobable outcomes the theoretical probability of each is 0.1000. The observed distribution is a total-variation distance of 0.05318 from that ideal, with the largest single-category z-score at 3.40. The chi-square against the enumerated theoretical distribution is 41.92 (p = 0.0000). This method supplies the null hypothesis; it can reject it but cannot by itself tell you whether a departure is exploitable.

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
| Open | computed | `total_variation_distance` | 0.05318 |
| Close | computed | `total_variation_distance` | 0.04612 |

Open produced total_variation_distance=0.05318; Close produced total_variation_distance=0.04612. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 2 survive Benjamini-Hochberg control at q=0.05 (close:chi2_vs_theoretical, open:chi2_vs_theoretical). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The assumed equiprobability is exactly the hypothesis under test, so this method supplies the null and cannot confirm it.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
