# M044 - Rolling Regime Analysis

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_044`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{p}^{(w)}_k = \frac{1}{|W_w|}\sum_{t \in W_w}\mathbf{1}[X_t=k]`

---

## 1. Definition and mathematical foundation

A regime is a stretch of time over which the distribution is approximately constant. Dividing history into windows and comparing window-wise distributions exposes whether the process is stable enough for any pooled estimate to mean anything.

## 2. Objective

Quantify regime instability and its effect on predictive performance.

## 3. Complete formula

```
\hat{p}^{(w)}_k = \frac{1}{|W_w|}\sum_{t \in W_w}\mathbf{1}[X_t=k]
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `W_w` | window w |
| `p_k^(w)` | window-wise probability |
| `drift` | dispersion of window-wise estimates |

## 5. Statistical assumptions

- The process is piecewise homogeneous
- Windows are comparable in length

## 6. Required input data

Several hundred observations per window.

## 7. Step-by-step manual calculation

1. Slice history into equal windows
2. Estimate the distribution in each
3. Measure dispersion and compare with the multinomial expectation

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

On a ten-point discrete sequence no AR/ARMA/ARIMA model is identified: with n=10 there are fewer observations than parameters, so the design matrix is rank-deficient and the fit is not determined. The worked arithmetic for the actual data is in the computed-results section, where n is 3131.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `window_dispersion` | 0.01288 | n/a | n/a | n/a | n/a | 8.0 |
| `expected_dispersion_under_stationarity` | 0.01517 | n/a | n/a | n/a | n/a | 8.0 |
| `dispersion_ratio` | 0.84882 | n/a | n/a | n/a | n/a | 8.0 |
| `n_adjacent_pairs_differing` | 0.00000 | n/a | n/a | n/a | n/a | 7.0 |
| `n_adjacent_pairs_tested` | 7.00000 | n/a | n/a | n/a | n/a | 7.0 |

**Interpretation.** Across 8 windows of 391 draws the average standard deviation of category probabilities is 0.01288, against 0.01517 expected from pure multinomial sampling (ratio 0.849). Of 7 adjacent window pairs, 0 differ at p<0.05. Window-wise distributions vary no more than sampling noise requires, so the process is stable enough for pooled estimates.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `window_dispersion` | 0.01396 | n/a | n/a | n/a | n/a | 8.0 |
| `expected_dispersion_under_stationarity` | 0.01517 | n/a | n/a | n/a | n/a | 8.0 |
| `dispersion_ratio` | 0.92035 | n/a | n/a | n/a | n/a | 8.0 |
| `n_adjacent_pairs_differing` | 0.00000 | n/a | n/a | n/a | n/a | 7.0 |
| `n_adjacent_pairs_tested` | 7.00000 | n/a | n/a | n/a | n/a | 7.0 |

**Interpretation.** Across 8 windows of 391 draws the average standard deviation of category probabilities is 0.01396, against 0.01517 expected from pure multinomial sampling (ratio 0.920). Of 7 adjacent window pairs, 0 differ at p<0.05. Window-wise distributions vary no more than sampling noise requires, so the process is stable enough for pooled estimates.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `window_dispersion` | 0.01396 |
| Close | computed | `window_dispersion` | 0.01288 |

Open produced window_dispersion=0.01396; Close produced window_dispersion=0.01288. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Windows are an arbitrary partition; results depend on the chosen length.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
