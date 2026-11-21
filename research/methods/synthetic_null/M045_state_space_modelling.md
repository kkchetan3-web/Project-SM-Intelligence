# M045 - State-Space Modelling

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_045`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `x_t = F x_{t-1} + w_t,\quad y_t = H x_t + v_t`

---

## 1. Definition and mathematical foundation

A state-space model separates an unobserved latent level from observation noise. The Kalman filter gives the optimal linear estimate of the state, and the innovation sequence provides a direct test of the model's adequacy.

## 2. Objective

Estimate a latent level and inspect the innovations for unexplained structure.

## 3. Complete formula

```
x_t = F x_{t-1} + w_t,\quad y_t = H x_t + v_t
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `x_t` | latent state |
| `y_t` | observation |
| `F, H` | transition and observation matrices |
| `w_t, v_t` | process and observation noise |

## 5. Statistical assumptions

- Linear Gaussian dynamics
- Innovations are white if the model is adequate

## 6. Required input data

A meaningful numeric encoding.

## 7. Step-by-step manual calculation

1. Specify the state and observation equations
2. Run the Kalman recursion
3. Test the standardised innovations for serial correlation

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

On a ten-point discrete sequence no AR/ARMA/ARIMA model is identified: with n=10 there are fewer observations than parameters, so the design matrix is rank-deficient and the fit is not determined. The worked arithmetic for the actual data is in the computed-results section, where n is 3131.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `loglik` | -7729.26218 | n/a | n/a | n/a | n/a | 3131.0 |
| `innovation_ljungbox_p` | 0.18081 | n/a | 0.18081 | 0.84380 | n/a | 3131.0 |
| `innovation_skew` | 0.00359 | n/a | n/a | n/a | n/a | 3131.0 |
| `innovation_kurtosis` | -1.19528 | n/a | n/a | n/a | n/a | 3131.0 |
| `state_variance_estimate` | 8.14473 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** A local-level state-space model on the numeric encoding gives log-likelihood -7729.3. The standardised innovations have Ljung-Box p = 0.1808, skewness 0.004 and excess kurtosis -1.195. The innovations are consistent with white noise, i.e. the latent-level model has nothing left to explain - unsurprising for a bounded discrete outcome.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `loglik` | -7744.48290 | n/a | n/a | n/a | n/a | 3131.0 |
| `innovation_ljungbox_p` | 0.47590 | n/a | 0.47590 | 0.94116 | n/a | 3131.0 |
| `innovation_skew` | -0.00010 | n/a | n/a | n/a | n/a | 3131.0 |
| `innovation_kurtosis` | -1.20646 | n/a | n/a | n/a | n/a | 3131.0 |
| `state_variance_estimate` | 8.23259 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** A local-level state-space model on the numeric encoding gives log-likelihood -7744.5. The standardised innovations have Ljung-Box p = 0.4759, skewness -0.000 and excess kurtosis -1.206. The innovations are consistent with white noise, i.e. the latent-level model has nothing left to explain - unsurprising for a bounded discrete outcome.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `loglik` | -7744.48290 |
| Close | computed | `loglik` | -7729.26218 |

Open produced loglik=-7744.48290; Close produced loglik=-7729.26218. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

A Gaussian latent-level model is a poor fit for a bounded 10-category outcome; the method is applied to the numeric encoding and its conclusions are qualified accordingly.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
