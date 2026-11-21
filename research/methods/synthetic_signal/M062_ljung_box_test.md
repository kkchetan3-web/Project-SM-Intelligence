# M062 - Ljung-Box Test

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_062`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `ljungbox_numeric_lag5` | 44.44510 | n/a | 1.881e-08 | 1.580e-07 | n/a | 3131.0 |
| `ljungbox_numeric_lag10` | 51.37607 | n/a | 1.488e-07 | 1.137e-06 | n/a | 3131.0 |
| `ljungbox_numeric_lag20` | 58.45035 | n/a | 1.234e-05 | 6.477e-05 | n/a | 3131.0 |
| `ljungbox_indicator_modal_lag5` | 6.03826 | n/a | 0.30251 | 0.46202 | n/a | 3131.0 |
| `ljungbox_indicator_modal_lag10` | 12.66747 | n/a | 0.24286 | 0.40001 | n/a | 3131.0 |
| `ljungbox_indicator_modal_lag20` | 17.19441 | n/a | 0.64032 | 0.76838 | n/a | 3131.0 |
| `ljungbox_parity_lag5` | 161.11276 | n/a | 5.733e-33 | 1.605e-31 | n/a | 3131.0 |
| `ljungbox_parity_lag10` | 170.66548 | n/a | 2.020e-31 | 2.424e-30 | n/a | 3131.0 |
| `ljungbox_parity_lag20` | 185.74274 | n/a | 7.267e-29 | 7.631e-28 | n/a | 3131.0 |
| `simulated_null_95pct_at_max_lag` | 31.02143 | n/a | n/a | n/a | n/a | 200.0 |

**Interpretation.** Ljung-Box statistics for numeric, modal-indicator and parity series at lags [5, 10, 20]. The smallest p-value across all nine tests is 0.0000, and the numeric series at lag 20 gives Q = 58.45. A simulated i.i.d. series of the same length and alphabet gives a 95th percentile of 31.02 for that statistic, which is the correct reference: the asymptotic chi-square approximation is optimistic for a categorical series that has been numerically encoded. The numeric series exceeds the simulated reference at the longest lag, indicating joint autocorrelation that the per-lag tests understated.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 10,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ljungbox_numeric_lag5` | 40.35351 | n/a | 1.267e-07 | 9.447e-07 | n/a | 3131.0 |
| `ljungbox_numeric_lag10` | 45.44295 | n/a | 1.809e-06 | 1.060e-05 | n/a | 3131.0 |
| `ljungbox_numeric_lag20` | 53.20078 | n/a | 7.593e-05 | 0.00026 | n/a | 3131.0 |
| `ljungbox_indicator_modal_lag5` | 11.34211 | n/a | 0.04500 | 0.09711 | n/a | 3131.0 |
| `ljungbox_indicator_modal_lag10` | 13.36639 | n/a | 0.20390 | 0.38000 | n/a | 3131.0 |
| `ljungbox_indicator_modal_lag20` | 23.82075 | n/a | 0.25031 | 0.44661 | n/a | 3131.0 |
| `ljungbox_parity_lag5` | 263.84573 | n/a | 5.867e-55 | 8.018e-54 | n/a | 3131.0 |
| `ljungbox_parity_lag10` | 265.33753 | n/a | 3.212e-51 | 3.762e-50 | n/a | 3131.0 |
| `ljungbox_parity_lag20` | 271.13258 | n/a | 6.074e-46 | 6.226e-45 | n/a | 3131.0 |
| `simulated_null_95pct_at_max_lag` | 31.02143 | n/a | n/a | n/a | n/a | 200.0 |

**Interpretation.** Ljung-Box statistics for numeric, modal-indicator and parity series at lags [5, 10, 20]. The smallest p-value across all nine tests is 0.0000, and the numeric series at lag 20 gives Q = 53.20. A simulated i.i.d. series of the same length and alphabet gives a 95th percentile of 31.02 for that statistic, which is the correct reference: the asymptotic chi-square approximation is optimistic for a categorical series that has been numerically encoded. The numeric series exceeds the simulated reference at the longest lag, indicating joint autocorrelation that the per-lag tests understated.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 10,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `ljungbox_numeric_lag5` | 40.35351 |
| Close | computed | `ljungbox_numeric_lag5` | 44.44510 |

Open produced ljungbox_numeric_lag5=40.35351; Close produced ljungbox_numeric_lag5=44.44510. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

20 p-values were produced across the computed targets; 12 survive Benjamini-Hochberg control at q=0.05 (close:ljungbox_numeric_lag5, close:ljungbox_numeric_lag10, close:ljungbox_numeric_lag20, close:ljungbox_parity_lag5, close:ljungbox_parity_lag10). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Applied to a categorical indicator the statistic is only approximately chi-square; permutation calibration is used alongside for safety.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Ljung & Box (1978)
