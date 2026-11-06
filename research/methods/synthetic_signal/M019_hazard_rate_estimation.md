# M019 - Hazard Rate Estimation

**Category:** B - Recency and Occurrence  
**Implementation:** `src.mathematics.recurrence::run_019`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `h(t) = P(T=t \mid T \ge t) = \frac{d_t}{n_t}`

---

## 1. Definition and mathematical foundation

The hazard rate answers the only question the 'due number' idea actually poses: does the probability of an outcome depend on how long it has been absent? A memoryless process has a constant hazard equal to the category probability; an increasing hazard means numbers do become 'more due', a decreasing one means clustering.

## 2. Objective

Estimate the empirical hazard as a function of elapsed time.

## 3. Complete formula

```
h(t) = P(T=t \mid T \ge t) = \frac{d_t}{n_t}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `h(t)` | hazard at elapsed time t |
| `d_t` | events at t |
| `n_t` | at risk at t |

## 5. Statistical assumptions

- The at-risk set is correctly defined
- Hazards are comparable across elapsed-time bins

## 6. Required input data

Enough occurrences to populate several hazard bins.

## 7. Step-by-step manual calculation

1. Bin elapsed time since last occurrence
2. Count events and exposures in each bin
3. Divide and compare with the constant-hazard expectation

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

With p = 0.4 for outcome 3 the geometric hazard is h(t) = 0.4 for every t, the survival function is S(t) = 0.6^t (S(1)=0.600, S(2)=0.360, S(3)=0.216), and the expected wait is 1/0.4 = 2.5 draws. A constant hazard is the precise statement of 'waiting does not matter'.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `constant_hazard_reference` | 0.11161 | n/a | n/a | n/a | n/a | 3127.0 |
| `hazard_range` | 0.04740 | n/a | n/a | n/a | n/a | 6.0 |
| `hazard_trend_slope` | 0.00140 | n/a | n/a | n/a | n/a | 6.0 |
| `chi2_vs_constant_hazard` | 6.28519 | n/a | 0.27945 | 0.44290 | n/a | 3127.0 |

**Interpretation.** Empirical hazard of 0 by elapsed draws: 0-0: 0.0914 (n=350), 1-2: 0.1158 (n=596), 3-5: 0.1052 (n=675), 6-9: 0.1286 (n=591), 10-19: 0.1000 (n=670), 20-+: 0.1388 (n=245). If waiting time were irrelevant every bin would sit at the constant-hazard reference 0.1116. The chi-square test against a constant hazard gives 6.29 on 5 df (p = 0.2794) and the fitted trend across bins is +0.00140 per draw. No evidence that a number becomes more likely with the length of its absence.

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
| `constant_hazard_reference` | 0.11349 | n/a | n/a | n/a | n/a | 3128.0 |
| `hazard_range` | 0.06510 | n/a | n/a | n/a | n/a | 6.0 |
| `hazard_trend_slope` | 0.00060 | n/a | n/a | n/a | n/a | 6.0 |
| `chi2_vs_constant_hazard` | 11.45350 | n/a | 0.04309 | 0.09711 | n/a | 3128.0 |

**Interpretation.** Empirical hazard of 1 by elapsed draws: 0-0: 0.0646 (n=356), 1-2: 0.1228 (n=627), 3-5: 0.1132 (n=689), 6-9: 0.1221 (n=598), 10-19: 0.1297 (n=609), 20-+: 0.1004 (n=249). If waiting time were irrelevant every bin would sit at the constant-hazard reference 0.1135. The chi-square test against a constant hazard gives 11.45 on 5 df (p = 0.0431) and the fitted trend across bins is +0.00060 per draw. The hazard is not constant across bins, which needs corroboration on independent periods before it can be treated as real.

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
| Open | computed | `constant_hazard_reference` | 0.11349 |
| Close | computed | `constant_hazard_reference` | 0.11161 |

Open produced constant_hazard_reference=0.11349; Close produced constant_hazard_reference=0.11161. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Suited to markets with long continuous histories; it degrades when the calendar has many gaps, because 'missing' and 'not drawn' become hard to separate.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Predictive claims are limited to what a causal forecast can show: hot/cold persistence is measured between two disjoint periods, and hazard/recency tests compare against a permutation or geometric null.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Late bins rest on few at-risk observations and are extremely noisy.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
