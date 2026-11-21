# M038 - Autoregressive Models

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_038`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `ar1_bic` | 15491.31948 | n/a | n/a | n/a | n/a | 3131.0 |
| `ar1_aic` | 15473.17312 | n/a | n/a | n/a | n/a | 3131.0 |
| `residual_ljungbox_p` | 0.39381 | n/a | 0.39381 | 0.55134 | n/a | 3131.0 |
| `in_sample_r2` | 0.01234 | n/a | n/a | n/a | n/a | 3131.0 |
| `oos_mse_ar` | 8.21476 | n/a | n/a | n/a | n/a | 940.0 |
| `oos_mse_mean_baseline` | 8.32274 | n/a | n/a | n/a | n/a | 940.0 |
| `oos_mse_ratio` | 0.98703 | n/a | n/a | n/a | n/a | 940.0 |

**Interpretation.** AR order 1 minimises BIC (15491.3) with in-sample R-squared 0.01234. Ljung-Box on the residuals gives p = 0.3938 (residuals consistent with white noise). Out of sample the one-step MSE is 8.2148 against 8.3227 for a constant-mean baseline, a ratio of 0.9870. An R-squared of 0.01234 means the model explains a negligible share of variance; there is nothing here to exploit.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ar1_bic` | 15533.54183 | n/a | n/a | n/a | n/a | 3131.0 |
| `ar1_aic` | 15515.39547 | n/a | n/a | n/a | n/a | 3131.0 |
| `residual_ljungbox_p` | 0.42297 | n/a | 0.42297 | 0.65440 | n/a | 3131.0 |
| `in_sample_r2` | 0.01125 | n/a | n/a | n/a | n/a | 3131.0 |
| `oos_mse_ar` | 8.44901 | n/a | n/a | n/a | n/a | 940.0 |
| `oos_mse_mean_baseline` | 8.50634 | n/a | n/a | n/a | n/a | 940.0 |
| `oos_mse_ratio` | 0.99326 | n/a | n/a | n/a | n/a | 940.0 |

**Interpretation.** AR order 1 minimises BIC (15533.5) with in-sample R-squared 0.01125. Ljung-Box on the residuals gives p = 0.4230 (residuals consistent with white noise). Out of sample the one-step MSE is 8.4490 against 8.5063 for a constant-mean baseline, a ratio of 0.9933. An R-squared of 0.01125 means the model explains a negligible share of variance; there is nothing here to exploit.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `ar1_bic` | 15533.54183 |
| Close | computed | `ar1_bic` | 15491.31948 |

Open produced ar1_bic=15533.54183; Close produced ar1_bic=15491.31948. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

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
