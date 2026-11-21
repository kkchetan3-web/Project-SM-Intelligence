# M039 - ARMA Modelling

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_039`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\phi(B)X_t = \theta(B)\varepsilon_t`

---

## 1. Definition and mathematical foundation

ARMA adds a moving-average term, capturing transient shocks on top of persistent autoregression. For a bounded discrete outcome its usefulness is limited, and it is included for completeness of the classical toolkit rather than expectation of success.

## 2. Objective

Fit ARMA structures and compare against AR alone.

## 3. Complete formula

```
\phi(B)X_t = \theta(B)\varepsilon_t
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `phi` | autoregressive polynomial |
| `theta` | moving-average polynomial |
| `B` | lag operator |

## 5. Statistical assumptions

- The series is stationary after any differencing
- Shocks are transient

## 6. Required input data

Several hundred observations.

## 7. Step-by-step manual calculation

1. Test stationarity
2. Fit candidate orders and compare by information criterion
3. Check residual autocorrelation

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

On a ten-point discrete sequence no AR/ARMA/ARIMA model is identified: with n=10 there are fewer observations than parameters, so the design matrix is rank-deficient and the fit is not determined. The worked arithmetic for the actual data is in the computed-results section, where n is 3131.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `bic_ARMA(1,0)` | 15495.97896 | n/a | n/a | n/a | n/a | 3131.0 |
| `bic_ARMA(1,1)` | 15503.93273 | n/a | n/a | n/a | n/a | 3131.0 |
| `bic_ARMA(2,1)` | 15510.86307 | n/a | n/a | n/a | n/a | 3131.0 |
| `bic_ARMA(2,2)` | 15514.62173 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_bic` | 15495.97896 | n/a | n/a | n/a | n/a | 3131.0 |
| `aic_model_advantage_over_ar1` | 0.00000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** BIC by specification: ARMA(1,0) 15496.0, ARMA(1,1) 15503.9, ARMA(2,1) 15510.9, ARMA(2,2) 15514.6. Best is ARMA(1,0). The improvement of the moving-average term over a plain AR(1) is +0.0 BIC units. Any fitted model here is describing bounded discrete noise with a continuous unbounded process, so a low information criterion is not evidence of a real generating mechanism.

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
| `bic_ARMA(1,0)` | 15537.55440 | n/a | n/a | n/a | n/a | 3131.0 |
| `bic_ARMA(1,1)` | 15544.90437 | n/a | n/a | n/a | n/a | 3131.0 |
| `bic_ARMA(2,1)` | 15551.96263 | n/a | n/a | n/a | n/a | 3131.0 |
| `bic_ARMA(2,2)` | 15557.35719 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_bic` | 15537.55440 | n/a | n/a | n/a | n/a | 3131.0 |
| `aic_model_advantage_over_ar1` | 0.00000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** BIC by specification: ARMA(1,0) 15537.6, ARMA(1,1) 15544.9, ARMA(2,1) 15552.0, ARMA(2,2) 15557.4. Best is ARMA(1,0). The improvement of the moving-average term over a plain AR(1) is +0.0 BIC units. Any fitted model here is describing bounded discrete noise with a continuous unbounded process, so a low information criterion is not evidence of a real generating mechanism.

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
| Open | computed | `bic_ARMA(1,0)` | 15537.55440 |
| Close | computed | `bic_ARMA(1,0)` | 15495.97896 |

Open produced bic_ARMA(1,0)=15537.55440; Close produced bic_ARMA(1,0)=15495.97896. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

12 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Model selection on a few thousand discrete observations is fragile, and ARMA assumes a continuous unbounded innovation.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
