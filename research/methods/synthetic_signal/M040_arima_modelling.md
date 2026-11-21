# M040 - ARIMA Modelling

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_040`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\phi(B)(1-B)^d X_t = \theta(B)\varepsilon_t`

---

## 1. Definition and mathematical foundation

Differencing removes integrated behaviour, which matters because a non-stationary level will otherwise produce spurious persistence. The order of differencing is chosen by unit-root testing rather than by guesswork.

## 2. Objective

Determine the integration order and fit a differenced model.

## 3. Complete formula

```
\phi(B)(1-B)^d X_t = \theta(B)\varepsilon_t
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `d` | differencing order |
| `ADF` | unit-root test statistic |

## 5. Statistical assumptions

- Differencing achieves stationarity
- The differenced series is invertible

## 6. Required input data

Meaningful numeric encoding.

## 7. Step-by-step manual calculation

1. Run an ADF test on the level and on differences
2. Select d accordingly
3. Fit and evaluate out of sample

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

On a ten-point discrete sequence no AR/ARMA/ARIMA model is identified: with n=10 there are fewer observations than parameters, so the design matrix is rank-deficient and the fit is not determined. The worked arithmetic for the actual data is in the computed-results section, where n is 3131.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `adf_statistic_level` | -32.02956 | n/a | 0.00000 | n/a | n/a | 3131.0 |
| `adf_p_level` | 0.00000 | n/a | 0.00000 | n/a | n/a | 3131.0 |
| `adf_p_differenced` | 0.00000 | n/a | 0.00000 | n/a | n/a | 3131.0 |
| `selected_d` | 0.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `arima_aic` | 15479.73630 | n/a | n/a | n/a | n/a | 3131.0 |
| `arima_bic` | 15503.93273 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** A Dickey-Fuller test on the level gives statistic -32.030 (p = 0.0000), so the selected differencing order is d=0. On the differenced series the p-value is 0.0000. ARIMA(1,0,1) gives AIC 15479.7. The level series is already stationary, so differencing would be unnecessary.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `adf_statistic_level` | -50.25975 | n/a | 0.00000 | n/a | n/a | 3131.0 |
| `adf_p_level` | 0.00000 | n/a | 0.00000 | n/a | n/a | 3131.0 |
| `adf_p_differenced` | 0.00000 | n/a | 0.00000 | n/a | n/a | 3131.0 |
| `selected_d` | 0.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `arima_aic` | 15520.70794 | n/a | n/a | n/a | n/a | 3131.0 |
| `arima_bic` | 15544.90437 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** A Dickey-Fuller test on the level gives statistic -50.260 (p = 0.0000), so the selected differencing order is d=0. On the differenced series the p-value is 0.0000. ARIMA(1,0,1) gives AIC 15520.7. The level series is already stationary, so differencing would be unnecessary.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `adf_statistic_level` | -50.25975 |
| Close | computed | `adf_statistic_level` | -32.02956 |

Open produced adf_statistic_level=-50.25975; Close produced adf_statistic_level=-32.02956. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

12 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Ank sequences are bounded and discrete; differencing them is arithmetically possible but conceptually weak.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
