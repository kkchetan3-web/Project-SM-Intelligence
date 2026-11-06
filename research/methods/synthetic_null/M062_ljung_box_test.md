# M062 - Ljung-Box Test

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_062`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `Q=n(n+2)\sum_{k=1}^{h}\frac{\hat{\rho}_k^2}{n-k}`

---

## 1. Definition and mathematical foundation

Ljung-Box jointly tests whether the first h autocorrelations are zero. It is more powerful than examining each lag separately, and it is the standard residual diagnostic for whether a fitted model has absorbed the dependence.

## 2. Objective

Jointly test autocorrelation up to a chosen lag.

## 3. Complete formula

```
Q=n(n+2)\sum_{k=1}^{h}\frac{\hat{\rho}_k^2}{n-k}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `Q` | Ljung-Box statistic |
| `rho_k` | lag-k autocorrelation |
| `h` | maximum lag tested |
| `n` | series length |

## 5. Statistical assumptions

- The series is stationary
- The chi-square approximation with h degrees of freedom is adequate

## 6. Required input data

Several hundred observations.

## 7. Step-by-step manual calculation

1. Choose the lag horizon
2. Compute autocorrelations
3. Form Q and compare with the chi-square distribution on h degrees of freedom

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Parity sequence: [1, 1, 1, 1, 0, 1, 1, 1, 0, 1]. Number of runs = 5. With n1 = 8 odd and n0 = 2 even, E[R] = 2 x 8 x 2/10 + 1 = 4.20.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ljungbox_numeric_lag5` | 10.31601 | n/a | 0.06676 | 0.72772 | n/a | 3131.0 |
| `ljungbox_numeric_lag10` | 14.11325 | n/a | 0.16789 | 0.84380 | n/a | 3131.0 |
| `ljungbox_numeric_lag20` | 20.34947 | n/a | 0.43627 | 0.85225 | n/a | 3131.0 |
| `ljungbox_indicator_modal_lag5` | 6.77089 | n/a | 0.23824 | 0.85225 | n/a | 3131.0 |
| `ljungbox_indicator_modal_lag10` | 10.50589 | n/a | 0.39728 | 0.85225 | n/a | 3131.0 |
| `ljungbox_indicator_modal_lag20` | 16.76911 | n/a | 0.66791 | 0.89312 | n/a | 3131.0 |
| `ljungbox_parity_lag5` | 7.66828 | n/a | 0.17549 | 0.84380 | n/a | 3131.0 |
| `ljungbox_parity_lag10` | 13.60414 | n/a | 0.19183 | 0.84807 | n/a | 3131.0 |
| `ljungbox_parity_lag20` | 18.18017 | n/a | 0.57554 | 0.89312 | n/a | 3131.0 |
| `simulated_null_95pct_at_max_lag` | 31.02143 | n/a | n/a | n/a | n/a | 200.0 |

**Interpretation.** Ljung-Box statistics for numeric, modal-indicator and parity series at lags [5, 10, 20]. The smallest p-value across all nine tests is 0.0668, and the numeric series at lag 20 gives Q = 20.35. A simulated i.i.d. series of the same length and alphabet gives a 95th percentile of 31.02 for that statistic, which is the correct reference: the asymptotic chi-square approximation is optimistic for a categorical series that has been numerically encoded. No lag horizon shows joint autocorrelation beyond the simulated random reference.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 10,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ljungbox_numeric_lag5` | 5.54230 | n/a | 0.35333 | 0.94116 | n/a | 3131.0 |
| `ljungbox_numeric_lag10` | 9.57650 | n/a | 0.47840 | 0.94116 | n/a | 3131.0 |
| `ljungbox_numeric_lag20` | 19.42670 | n/a | 0.49427 | 0.94116 | n/a | 3131.0 |
| `ljungbox_indicator_modal_lag5` | 1.66024 | n/a | 0.89387 | 0.96444 | n/a | 3131.0 |
| `ljungbox_indicator_modal_lag10` | 4.52192 | n/a | 0.92075 | 0.98054 | n/a | 3131.0 |
| `ljungbox_indicator_modal_lag20` | 30.94667 | n/a | 0.05590 | 0.83640 | n/a | 3131.0 |
| `ljungbox_parity_lag5` | 12.57297 | n/a | 0.02773 | 0.65418 | n/a | 3131.0 |
| `ljungbox_parity_lag10` | 13.49907 | n/a | 0.19709 | 0.89786 | n/a | 3131.0 |
| `ljungbox_parity_lag20` | 17.16535 | n/a | 0.64221 | 0.94116 | n/a | 3131.0 |
| `simulated_null_95pct_at_max_lag` | 31.02143 | n/a | n/a | n/a | n/a | 200.0 |

**Interpretation.** Ljung-Box statistics for numeric, modal-indicator and parity series at lags [5, 10, 20]. The smallest p-value across all nine tests is 0.0277, and the numeric series at lag 20 gives Q = 19.43. A simulated i.i.d. series of the same length and alphabet gives a 95th percentile of 31.02 for that statistic, which is the correct reference: the asymptotic chi-square approximation is optimistic for a categorical series that has been numerically encoded. No lag horizon shows joint autocorrelation beyond the simulated random reference.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 10,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `ljungbox_numeric_lag5` | 5.54230 |
| Close | computed | `ljungbox_numeric_lag5` | 10.31601 |

Open produced ljungbox_numeric_lag5=5.54230; Close produced ljungbox_numeric_lag5=10.31601. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

20 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Applied to a categorical indicator the statistic is only approximately chi-square; permutation calibration is used alongside for safety.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Ljung & Box (1978)
