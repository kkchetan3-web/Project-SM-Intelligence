# M049 - Digit Sum Distribution

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_049`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `S = d_1 + d_2 + d_3,\quad d_i \in \{0,\ldots,9\}`

---

## 1. Definition and mathematical foundation

For a three-digit panel the digit sum ranges over 0-27 with a triangular-ish distribution concentrated near the middle, exactly the convolution of three uniform discrete variables. Comparing the empirical sum distribution with that convolution tests whether panel digits are independently and uniformly generated.

## 2. Objective

Test whether panel digit sums match the theoretical convolution.

## 3. Complete formula

```
S = d_1 + d_2 + d_3,\quad d_i \in \{0,\ldots,9\}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `S` | digit sum 0-27 |
| `d_i` | i-th digit of the panel |

## 5. Statistical assumptions

- Panel digits are independent and uniform under the null
- The panel is exactly three digits

## 6. Required input data

Panels must be available for the market.

## 7. Step-by-step manual calculation

1. Extract the three digits of every open and close panel
2. Compute the sum
3. Compare the empirical distribution with the exact convolution

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Digital roots of (3,1,3,7,0,3,9,3,2,3) are (3,1,3,7,0,3,9,3,2,3) because every value is a single digit. Digit sums are therefore the values themselves - the method becomes informative only on 3-digit panels.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `digit_sum_chi2` | 42.78652 | n/a | 0.01477 | 0.17725 | n/a | 4136.0 |
| `observed_mean_sum` | 13.63298 | n/a | n/a | n/a | n/a | 4136.0 |
| `observed_std_sum` | 4.86750 | n/a | n/a | n/a | n/a | 4136.0 |
| `n_panels` | 4136.00000 | n/a | n/a | n/a | n/a | 4136.0 |

**Interpretation.** Across 4136 panels the digit sum has mean 13.633 (theoretical 13.5) and standard deviation 4.868 (theoretical 4.975). The chi-square against the exact convolution of three uniform digits is 42.79 on 25 df, p = 0.0148. The sum distribution departs from the independent-uniform convolution, which points at dependence between digit positions or a non-uniform digit marginal.

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
| `digit_sum_chi2` | 60.44377 | n/a | 9.080e-05 | 0.00128 | n/a | 4134.0 |
| `observed_mean_sum` | 14.02298 | n/a | n/a | n/a | n/a | 4134.0 |
| `observed_std_sum` | 4.90823 | n/a | n/a | n/a | n/a | 4134.0 |
| `n_panels` | 4134.00000 | n/a | n/a | n/a | n/a | 4134.0 |

**Interpretation.** Across 4134 panels the digit sum has mean 14.023 (theoretical 13.5) and standard deviation 4.908 (theoretical 4.975). The chi-square against the exact convolution of three uniform digits is 60.44 on 25 df, p = 0.0001. The sum distribution departs from the independent-uniform convolution, which points at dependence between digit positions or a non-uniform digit marginal.

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
| Open | computed | `digit_sum_chi2` | 60.44377 |
| Close | computed | `digit_sum_chi2` | 42.78652 |

Open produced digit_sum_chi2=60.44377; Close produced digit_sum_chi2=42.78652. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 1 survive Benjamini-Hochberg control at q=0.05 (open:digit_sum_chi2). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Panna conventions can include repeated or 'double' panels that some operators weight differently; the theoretical baseline assumes plain uniform digits.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
