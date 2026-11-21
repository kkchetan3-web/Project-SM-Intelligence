# M059 - Hamming Distance Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_059`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `d_H(x,y)=\sum_{i}\mathbf{1}[x_i \neq y_i]`

---

## 1. Definition and mathematical foundation

Hamming distance counts positional disagreements between two equal-length digit strings. For consecutive panels it measures how much the panel changes, and its distribution under independence is exactly computable for uniform digits.

## 2. Objective

Characterise how consecutive panels differ.

## 3. Complete formula

```
d_H(x,y)=\sum_{i}\mathbf{1}[x_i \neq y_i]
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `d_H` | number of differing positions |
| `x, y` | two equal-length strings |

## 5. Statistical assumptions

- Strings are equal length with fixed positions
- Positions are comparable across panels

## 6. Required input data

Panels available.

## 7. Step-by-step manual calculation

1. Take consecutive panel pairs
2. Count differing positions
3. Compare with the independence prediction

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

No worked example is defined for this category.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_hamming_distance` | 2.71118 | n/a | n/a | n/a | n/a | 3130.0 |
| `hamming_chi2` | 2.85388 | n/a | 0.41471 | 0.57107 | n/a | 3130.0 |
| `identical_consecutive_panels` | 1.00000 | n/a | n/a | n/a | n/a | 3130.0 |
| `all_positions_differ_share` | 0.73866 | n/a | n/a | n/a | n/a | 3130.0 |

**Interpretation.** Consecutive panels differ in 2.711 of their 3 positions on average (independent uniform digits predict 2.7). All three positions differ 73.866% of the time against 72.9%, and panels are identical 1 times against 3.1 expected. The chi-square against the independence prediction is 2.85 (p = 0.4147). Consecutive panels are as different as independent draws require.

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
| `mean_hamming_distance` | 2.70958 | n/a | n/a | n/a | n/a | 3130.0 |
| `hamming_chi2` | 2.94329 | n/a | 0.40045 | 0.65440 | n/a | 3130.0 |
| `identical_consecutive_panels` | 3.00000 | n/a | n/a | n/a | n/a | 3130.0 |
| `all_positions_differ_share` | 0.73355 | n/a | n/a | n/a | n/a | 3130.0 |

**Interpretation.** Consecutive panels differ in 2.710 of their 3 positions on average (independent uniform digits predict 2.7). All three positions differ 73.355% of the time against 72.9%, and panels are identical 3 times against 3.1 expected. The chi-square against the independence prediction is 2.94 (p = 0.4005). Consecutive panels are as different as independent draws require.

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
| Open | computed | `mean_hamming_distance` | 2.70958 |
| Close | computed | `mean_hamming_distance` | 2.71118 |

Open produced mean_hamming_distance=2.70958; Close produced mean_hamming_distance=2.71118. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Hamming distance treats all positions as equally meaningful, which the panel ranking convention may not support.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
