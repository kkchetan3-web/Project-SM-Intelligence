# M050 - Digit Difference Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_050`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `D = |d_1 - d_2|,\ldots`

---

## 1. Definition and mathematical foundation

Differences between digit positions summarise the internal geometry of a panel. Under uniform independent digits the difference distribution is exactly computable, so systematic deviations indicate non-uniform or dependent digits.

## 2. Objective

Test whether inter-digit differences match the independent-uniform prediction.

## 3. Complete formula

```
D = |d_1 - d_2|,\ldots
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `D` | absolute difference between positions |
| `d_i` | digit at position i |

## 5. Statistical assumptions

- Digits are exchangeable under the null
- Panels are three digits

## 6. Required input data

Panels available.

## 7. Step-by-step manual calculation

1. Compute the six pairwise absolute differences per panel
2. Tabulate their distribution
3. Compare with the exact theoretical distribution

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Digital roots of (3,1,3,7,0,3,9,3,2,3) are (3,1,3,7,0,3,9,3,2,3) because every value is a single digit. Digit sums are therefore the values themselves - the method becomes informative only on 3-digit panels.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_abs_difference` | 3.30565 | n/a | n/a | n/a | n/a | 3131.0 |
| `difference_chi2` | 4.60024 | n/a | 0.83721 | n/a | n/a | 3131.0 |
| `n_zero_differences` | 320.00000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Absolute difference between panel positions averages 3.306 (independent uniform digits give 3.3). Exactly equal digits occur 10.220% of the time against 10.0% under independence. The chi-square of the difference distribution against the exact null is 4.60 (p = 0.8372). Digit differences match the independence prediction.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_abs_difference` | 3.36442 | n/a | n/a | n/a | n/a | 3131.0 |
| `difference_chi2` | 9.33557 | n/a | 0.38538 | n/a | n/a | 3131.0 |
| `n_zero_differences` | 305.00000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Absolute difference between panel positions averages 3.364 (independent uniform digits give 3.3). Exactly equal digits occur 9.741% of the time against 10.0% under independence. The chi-square of the difference distribution against the exact null is 9.34 (p = 0.3854). Digit differences match the independence prediction.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `mean_abs_difference` | 3.36442 |
| Close | computed | `mean_abs_difference` | 3.30565 |

Open produced mean_abs_difference=3.36442; Close produced mean_abs_difference=3.30565. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Differences are highly dependent within a panel, so the tests are not independent and must be interpreted jointly.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
