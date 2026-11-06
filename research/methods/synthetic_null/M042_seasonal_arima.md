# M042 - Seasonal ARIMA

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_042`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\phi(B)\Phi(B^s)(1-B)^d(1-B^s)^D X_t = \theta(B)\Theta(B^s)\varepsilon_t`

---

## 1. Definition and mathematical foundation

SARIMA adds seasonal autoregressive and moving-average polynomials. Its parameter count grows quickly, so a defensible seasonal period and strong prior evidence are prerequisites rather than niceties.

## 2. Objective

Fit a seasonal model only where a seasonal period is empirically justified.

## 3. Complete formula

```
\phi(B)\Phi(B^s)(1-B)^d(1-B^s)^D X_t = \theta(B)\Theta(B^s)\varepsilon_t
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `s` | seasonal period |
| `Phi` | seasonal AR polynomial |
| `Theta` | seasonal MA polynomial |

## 5. Statistical assumptions

- A genuine seasonal cycle exists
- Enough cycles to estimate seasonal parameters

## 6. Required input data

Numerous complete cycles.

## 7. Step-by-step manual calculation

1. Establish the seasonal period from decomposition
2. Fit a small seasonal model
3. Evaluate out of sample and against the non-seasonal model

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

On a ten-point discrete sequence no AR/ARMA/ARIMA model is identified: with n=10 there are fewer observations than parameters, so the design matrix is rank-deficient and the fit is not determined. The worked arithmetic for the actual data is in the computed-results section, where n is 3131.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `sarima_aic` | 15522.35232 | n/a | n/a | n/a | n/a | 3131.0 |
| `converged` | 1.00000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** A SARIMA(1,0,1)(1,0,0,7) fit gives AIC 15522.4 (converged). A seasonal period of 7 is imposed rather than discovered, and Method 41 found no seasonal strength to model. Fitting a seasonal model to a series with no seasonal structure adds parameters and degrees of freedom without adding information, which is why the platform does not promote it regardless of its information criterion.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 2,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `sarima_aic` | 15462.71998 | n/a | n/a | n/a | n/a | 3131.0 |
| `converged` | 1.00000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** A SARIMA(1,0,1)(1,0,0,7) fit gives AIC 15462.7 (converged). A seasonal period of 7 is imposed rather than discovered, and Method 41 found no seasonal strength to model. Fitting a seasonal model to a series with no seasonal structure adds parameters and degrees of freedom without adding information, which is why the platform does not promote it regardless of its information criterion.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 2,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `sarima_aic` | 15462.71998 |
| Close | computed | `sarima_aic` | 15522.35232 |

Open produced sarima_aic=15462.71998; Close produced sarima_aic=15522.35232. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

4 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Fitting a seasonal model to noise will always appear to fit better in-sample and will generally fail out of sample.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
