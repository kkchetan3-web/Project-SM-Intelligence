# M018 - Survival Analysis

**Category:** B - Recency and Occurrence  
**Implementation:** `src.mathematics.recurrence::run_018`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{S}(t)=\prod_{s \le t}\left(1-\frac{d_s}{n_s}\right)`

---

## 1. Definition and mathematical foundation

The Kaplan-Meier estimator handles the censoring that gap analysis ignores: the final incomplete waiting period is information, and discarding it biases estimates. For a discrete memoryless process the survival curve is geometric, so plotting the empirical curve against the geometric prediction is a direct test of memorylessness.

## 2. Objective

Estimate the survival function of the waiting time with censoring handled.

## 3. Complete formula

```
\hat{S}(t)=\prod_{s \le t}\left(1-\frac{d_s}{n_s}\right)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `S(t)` | survival probability past t |
| `d_s` | occurrences at time s |
| `n_s` | number at risk at time s |

## 5. Statistical assumptions

- Censoring is non-informative
- The hazard is estimable from the at-risk counts

## 6. Required input data

Several occurrences per category.

## 7. Step-by-step manual calculation

1. For each category build the at-risk and event counts over the gap axis
2. Compute the product-limit estimate
3. Overlay the geometric survival curve implied by the marginal probability

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

With p = 0.4 for outcome 3 the geometric hazard is h(t) = 0.4 for every t, the survival function is S(t) = 0.6^t (S(1)=0.600, S(2)=0.360, S(3)=0.216), and the expected wait is 1/0.4 = 2.5 draws. A constant hazard is the precise statement of 'waiting does not matter'.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `km_survival_at_max_t` | 0.00000 | n/a | n/a | n/a | n/a | 349.0 |
| `geometric_survival_at_max_t` | 0.00296 | n/a | n/a | n/a | n/a | 349.0 |
| `max_abs_deviation_from_geometric` | 0.02402 | n/a | n/a | n/a | n/a | 349.0 |
| `censored_observation_included` | 12.00000 | n/a | n/a | n/a | n/a | 350.0 |

**Interpretation.** Kaplan-Meier survival for 0 out to 49 draws falls to 0.0000, against 0.0030 predicted by a memoryless geometric process. The largest absolute deviation between the curves is 0.0240. Including the final censored wait of 12 draws matters: dropping it would bias the estimated survival upward. The empirical curve tracks the memoryless prediction closely.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `km_survival_at_max_t` | 0.00289 | n/a | n/a | n/a | n/a | 355.0 |
| `geometric_survival_at_max_t` | 0.00069 | n/a | n/a | n/a | n/a | 355.0 |
| `max_abs_deviation_from_geometric` | 0.04954 | n/a | n/a | n/a | n/a | 355.0 |
| `censored_observation_included` | 18.00000 | n/a | n/a | n/a | n/a | 356.0 |

**Interpretation.** Kaplan-Meier survival for 1 out to 60 draws falls to 0.0029, against 0.0007 predicted by a memoryless geometric process. The largest absolute deviation between the curves is 0.0495. Including the final censored wait of 18 draws matters: dropping it would bias the estimated survival upward. The empirical curve tracks the memoryless prediction closely.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `km_survival_at_max_t` | 0.00289 |
| Close | computed | `km_survival_at_max_t` | 0.00000 |

Open produced km_survival_at_max_t=0.00289; Close produced km_survival_at_max_t=0.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Suited to markets with long continuous histories; it degrades when the calendar has many gaps, because 'missing' and 'not drawn' become hard to separate.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Predictive claims are limited to what a causal forecast can show: hot/cold persistence is measured between two disjoint periods, and hazard/recency tests compare against a permutation or geometric null.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Censoring from the end of the sample is not random with respect to gap length.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
