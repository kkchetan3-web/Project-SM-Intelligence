# M038 - Autoregressive Models

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_038`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `X_t = c + \sum_{i=1}^{p}\phi_i X_{t-i} + \varepsilon_t`

---

## 1. Definition and mathematical foundation

An AR(p) model represents the series as a linear function of its own past plus noise. Applying it to a categorical outcome requires a numeric encoding, which is defensible for anks on a circle but not for jodis; the method therefore declares its applicability instead of forcing a fit.

## 2. Objective

Fit autoregressive models and diagnose whether any lag structure survives.

## 3. Complete formula

```
X_t = c + \sum_{i=1}^{p}\phi_i X_{t-i} + \varepsilon_t
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `phi_i` | autoregressive coefficients |
| `p` | order |
| `epsilon` | innovation term |

## 5. Statistical assumptions

- The numeric encoding is meaningful
- Residuals are approximately white

## 6. Required input data

Meaningful numeric encoding; several hundred observations.

## 7. Step-by-step manual calculation

1. Test the encoding's meaningfulness
2. Fit orders up to the configured maximum
3. Diagnose residuals with Ljung-Box and score out of sample

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

On a ten-point discrete sequence no AR/ARMA/ARIMA model is identified: with n=10 there are fewer observations than parameters, so the design matrix is rank-deficient and the fit is not determined. The worked arithmetic for the actual data is in the computed-results section, where n is 3131.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ar1_bic` | 20469.09744 | n/a | n/a | n/a | n/a | 4143.0 |
| `ar1_aic` | 20450.11064 | n/a | n/a | n/a | n/a | 4143.0 |
| `residual_ljungbox_p` | 0.42075 | n/a | 0.42075 | 0.72128 | n/a | 4143.0 |
| `in_sample_r2` | 0.00064 | n/a | n/a | n/a | n/a | 4143.0 |
| `oos_mse_ar` | 7.91117 | n/a | n/a | n/a | n/a | 1243.0 |
| `oos_mse_mean_baseline` | 7.91056 | n/a | n/a | n/a | n/a | 1243.0 |
| `oos_mse_ratio` | 1.00008 | n/a | n/a | n/a | n/a | 1243.0 |

**Interpretation.** AR order 1 minimises BIC (20469.1) with in-sample R-squared 0.00064. Ljung-Box on the residuals gives p = 0.4207 (residuals consistent with white noise). Out of sample the one-step MSE is 7.9112 against 7.9106 for a constant-mean baseline, a ratio of 1.0001. An R-squared of 0.00064 means the model explains a negligible share of variance; there is nothing here to exploit.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ar1_bic` | 20534.61345 | n/a | n/a | n/a | n/a | 4143.0 |
| `ar1_aic` | 20515.62665 | n/a | n/a | n/a | n/a | 4143.0 |
| `residual_ljungbox_p` | 0.09596 | n/a | 0.09596 | 0.28102 | n/a | 4143.0 |
| `in_sample_r2` | 0.00011 | n/a | n/a | n/a | n/a | 4143.0 |
| `oos_mse_ar` | 8.35919 | n/a | n/a | n/a | n/a | 1243.0 |
| `oos_mse_mean_baseline` | 8.36098 | n/a | n/a | n/a | n/a | 1243.0 |
| `oos_mse_ratio` | 0.99979 | n/a | n/a | n/a | n/a | 1243.0 |

**Interpretation.** AR order 1 minimises BIC (20534.6) with in-sample R-squared 0.00011. Ljung-Box on the residuals gives p = 0.0960 (residuals consistent with white noise). Out of sample the one-step MSE is 8.3592 against 8.3610 for a constant-mean baseline, a ratio of 0.9998. An R-squared of 0.00011 means the model explains a negligible share of variance; there is nothing here to exploit.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `ar1_bic` | 20534.61345 |
| Close | computed | `ar1_bic` | 20469.09744 |

Open produced ar1_bic=20534.61345; Close produced ar1_bic=20469.09744. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

14 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Linear AR structure cannot represent modular relationships, and a discrete bounded outcome violates the Gaussian innovation assumption.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
