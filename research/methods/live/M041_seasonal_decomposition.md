# M041 - Seasonal Decomposition

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_041`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `X_t = T_t + S_t + R_t`

---

## 1. Definition and mathematical foundation

Classical decomposition splits a series into trend, seasonal and residual components. It is a diagnostic that makes an anticipated seasonality visible - and, crucially, lets the residual be tested for the dependence that seasonality cannot explain.

## 2. Objective

Test for periodic structure and isolate the residual.

## 3. Complete formula

```
X_t = T_t + S_t + R_t
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `T_t` | trend |
| `S_t` | seasonal |
| `R_t` | residual |

## 5. Statistical assumptions

- The seasonal period is known a priori
- Seasonal amplitude is stable across periods

## 6. Required input data

At least two full cycles.

## 7. Step-by-step manual calculation

1. Detect the dominant period from the autocorrelation
2. Decompose the series
3. Test the residual for remaining dependence

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

On a ten-point discrete sequence no AR/ARMA/ARIMA model is identified: with n=10 there are fewer observations than parameters, so the design matrix is rank-deficient and the fit is not determined. The worked arithmetic for the actual data is in the computed-results section, where n is 3131.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `seasonal_strength` | 0.00231 | n/a | n/a | n/a | n/a | 4143.0 |
| `trend_strength` | 0.14869 | n/a | n/a | n/a | n/a | 4143.0 |
| `permutation_seasonal_strength_mean` | 0.00165 | n/a | n/a | n/a | n/a | 100.0 |
| `permutation_95pct` | 0.00352 | n/a | n/a | n/a | n/a | 100.0 |
| `residual_std` | 2.63265 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** With a 7-day period, seasonal strength is 0.0023 and trend strength 0.1487. Shuffling the series destroys any real calendar structure while preserving its distribution; the shuffled series still yields a seasonal strength of 0.0016 on average (95th percentile 0.0035) purely because decomposition fits noise. The observed strength is inside the null band: no seasonal structure.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `seasonal_strength` | 0.00599 | n/a | n/a | n/a | n/a | 4143.0 |
| `trend_strength` | 0.14595 | n/a | n/a | n/a | n/a | 4143.0 |
| `permutation_seasonal_strength_mean` | 0.00163 | n/a | n/a | n/a | n/a | 100.0 |
| `permutation_95pct` | 0.00304 | n/a | n/a | n/a | n/a | 100.0 |
| `residual_std` | 2.65249 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** With a 7-day period, seasonal strength is 0.0060 and trend strength 0.1459. Shuffling the series destroys any real calendar structure while preserving its distribution; the shuffled series still yields a seasonal strength of 0.0016 on average (95th percentile 0.0030) purely because decomposition fits noise. The observed strength exceeds the null band and warrants the formal calendar tests in Method 43.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `seasonal_strength` | 0.00599 |
| Close | computed | `seasonal_strength` | 0.00231 |

Open produced seasonal_strength=0.00599; Close produced seasonal_strength=0.00231. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

With a weekly cycle and only ~3100 daily observations there are ~520 cycles, but the draw calendar omits Sundays, which distorts naive periodicity.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
