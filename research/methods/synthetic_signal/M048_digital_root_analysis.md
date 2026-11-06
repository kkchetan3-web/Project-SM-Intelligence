# M048 - Digital Root Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_048`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\mathrm{dr}(n) = 1 + ((n-1) \bmod 9)`

---

## 1. Definition and mathematical foundation

The digital root is the iterated digit sum, collapsing any integer to 1-9. It is the base-10 manifestation of modular arithmetic mod 9, so its distribution is tightly constrained and easy to test - and any departure from the constraint signals a parsing or data error rather than a market phenomenon.

## 2. Objective

Characterise the digital-root distribution and use it as a data-integrity probe.

## 3. Complete formula

```
\mathrm{dr}(n) = 1 + ((n-1) \bmod 9)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `dr(n)` | digital root in 1-9 |
| `n` | integer value |

## 5. Statistical assumptions

- Values are stated in base 10
- Digital root is deterministic given the value

## 6. Required input data

Any non-empty sample.

## 7. Step-by-step manual calculation

1. Compute the iterated digit sum for each outcome
2. Tabulate the distribution
3. Compare with the theoretical distribution implied by the outcome space

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Digital roots of (3,1,3,7,0,3,9,3,2,3) are (3,1,3,7,0,3,9,3,2,3) because every value is a single digit. Digit sums are therefore the values themselves - the method becomes informative only on 3-digit panels.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `digital_root_chi2` | 34.05589 | n/a | 8.733e-05 | 0.00035 | n/a | 3131.0 |
| `most_common_root` | 0.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `least_common_root` | 8.00000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Digital roots of the outcomes against the uniform expectation give chi-square 34.06 on 9 df (p = 0.0001). The most frequent root is 0 with 350 observations, the least frequent 8 with 259. On a single digit the digital root is almost the identity map (only 0 and 9 behave distinctly), so this method's main value here is as a check that the digit space is being read correctly rather than as an independent test.

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
| `digital_root_chi2` | 41.91920 | n/a | 3.400e-06 | 1.394e-05 | n/a | 3131.0 |
| `most_common_root` | 1.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `least_common_root` | 7.00000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Digital roots of the outcomes against the uniform expectation give chi-square 41.92 on 9 df (p = 0.0000). The most frequent root is 1 with 356 observations, the least frequent 7 with 256. On a single digit the digital root is almost the identity map (only 0 and 9 behave distinctly), so this method's main value here is as a check that the digit space is being read correctly rather than as an independent test.

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
| Open | computed | `digital_root_chi2` | 41.91920 |
| Close | computed | `digital_root_chi2` | 34.05589 |

Open produced digital_root_chi2=41.91920; Close produced digital_root_chi2=34.05589. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 2 survive Benjamini-Hochberg control at q=0.05 (close:digital_root_chi2, open:digital_root_chi2). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Digital roots of a uniform 0-9 draw are not uniform themselves because 0 maps to 0 and 9 maps to 9; the theoretical comparison must account for that.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
