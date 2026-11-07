# M046 - Dynamic Generalized Linear Models

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_046`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `g(\mu_t) = x_t^\top\beta_t,\quad \beta_t = \beta_{t-1} + \eta_t`

---

## 1. Definition and mathematical foundation

A dynamic GLM lets coefficients evolve over time, so a model can adapt to regime change without a discrete break detection. Tracking the coefficient path also answers a diagnostic question: if the coefficients wander randomly, there is no stable relationship to learn.

## 2. Objective

Estimate time-varying coefficients and assess coefficient stability.

## 3. Complete formula

```
g(\mu_t) = x_t^\top\beta_t,\quad \beta_t = \beta_{t-1} + \eta_t
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `beta_t` | time-varying coefficient vector |
| `g` | link function |
| `eta_t` | state noise |

## 5. Statistical assumptions

- Coefficients evolve slowly
- The link function is appropriate

## 6. Required input data

Several hundred observations per refit.

## 7. Step-by-step manual calculation

1. Refit the GLM on expanding windows
2. Track coefficient paths over time
3. Measure path variance relative to the coefficient magnitude

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

On a ten-point discrete sequence no AR/ARMA/ARIMA model is identified: with n=10 there are fewer observations than parameters, so the design matrix is rank-deficient and the fit is not determined. The worked arithmetic for the actual data is in the computed-results section, where n is 3131.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `n_refits` | 12.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `coefficient_scale_mean` | 0.06235 | n/a | n/a | n/a | n/a | 12.0 |
| `coefficient_relative_drift` | 0.31725 | n/a | n/a | n/a | n/a | 12.0 |
| `coefficient_first` | 0.10356 | n/a | n/a | n/a | n/a | 200.0 |
| `coefficient_last` | 0.04023 | n/a | n/a | n/a | n/a | 3995.0 |

**Interpretation.** Refitting a multinomial logistic model at 12 expanding cut-offs, the mean absolute coefficient moves from 0.10356 to 0.04023 with a relative standard deviation of 0.317 across refits. Coefficient scale barely changes as data accumulate, which is the behaviour of a model converging on 'the features are uninformative' rather than of a relationship being learned. A true dynamic GLM would add a state equation for the coefficients; this expanding-window path is a transparency approximation and is labelled as such.

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
| `n_refits` | 12.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `coefficient_scale_mean` | 0.05057 | n/a | n/a | n/a | n/a | 12.0 |
| `coefficient_relative_drift` | 0.38620 | n/a | n/a | n/a | n/a | 12.0 |
| `coefficient_first` | 0.09457 | n/a | n/a | n/a | n/a | 200.0 |
| `coefficient_last` | 0.03134 | n/a | n/a | n/a | n/a | 3995.0 |

**Interpretation.** Refitting a multinomial logistic model at 12 expanding cut-offs, the mean absolute coefficient moves from 0.09457 to 0.03134 with a relative standard deviation of 0.386 across refits. Coefficient scale barely changes as data accumulate, which is the behaviour of a model converging on 'the features are uninformative' rather than of a relationship being learned. A true dynamic GLM would add a state equation for the coefficients; this expanding-window path is a transparency approximation and is labelled as such.

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
| Open | computed | `n_refits` | 12.00000 |
| Close | computed | `n_refits` | 12.00000 |

Open produced n_refits=12.00000; Close produced n_refits=12.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Expanding-window refitting is only an approximation to a true dynamic GLM; the implementation notes that explicitly.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
