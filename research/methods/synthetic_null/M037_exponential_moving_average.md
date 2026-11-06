# M037 - Exponential Moving Average

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_037`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\mathrm{EMA}_t = \alpha x_t + (1-\alpha)\mathrm{EMA}_{t-1}`

---

## 1. Definition and mathematical foundation

The EMA is a one-parameter recursive filter whose memory decays geometrically. It is the numeric counterpart of the exponentially weighted frequency in M004 and shares its property that the effective memory is 1/alpha observations.

## 2. Objective

Test smoothing rates as predictors of the next outcome.

## 3. Complete formula

```
\mathrm{EMA}_t = \alpha x_t + (1-\alpha)\mathrm{EMA}_{t-1}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `alpha` | smoothing constant in (0,1] |
| `EMA_t` | smoothed level |

## 5. Statistical assumptions

- The encoding is numeric and meaningful
- Alpha is constant

## 6. Required input data

A few hundred observations.

## 7. Step-by-step manual calculation

1. Initialise the EMA on an initial window
2. Update recursively with each new draw
3. Score the smoothed level as a predictor out of sample

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Trailing 3-point moving averages of the numeric encoding: [2.333, 3.667, 3.333, 3.333, 4.0, 5.0, 4.667, 2.667]. The final value 2.667 would be the feature offered for predicting the next draw.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `correlation_EMA5` | 0.00369 | n/a | 0.83671 | 0.95048 | n/a | 3130.0 |
| `correlation_EMA10` | 0.00725 | n/a | 0.68498 | 0.89312 | n/a | 3130.0 |
| `correlation_EMA20` | 0.00644 | n/a | 0.71855 | 0.89312 | n/a | 3130.0 |
| `correlation_EMA50` | 0.01079 | n/a | 0.54628 | 0.89312 | n/a | 3130.0 |
| `permutation_band` | 0.03182 | n/a | n/a | n/a | n/a | 200.0 |

**Interpretation.** Exponential moving average correlations: alpha=0.05: r=+0.0037, alpha=0.1: r=+0.0073, alpha=0.2: r=+0.0064, alpha=0.5: r=+0.0108, permutation band 0.0318. The best smoothing rate still produces a correlation indistinguishable from noise.

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
| `correlation_EMA5` | 0.00285 | n/a | 0.87324 | 0.95768 | n/a | 3130.0 |
| `correlation_EMA10` | -0.00294 | n/a | 0.86961 | 0.95768 | n/a | 3130.0 |
| `correlation_EMA20` | -0.00475 | n/a | 0.79072 | 0.95351 | n/a | 3130.0 |
| `correlation_EMA50` | -0.01239 | n/a | 0.48843 | 0.94116 | n/a | 3130.0 |
| `permutation_band` | 0.03397 | n/a | n/a | n/a | n/a | 200.0 |

**Interpretation.** Exponential moving average correlations: alpha=0.05: r=+0.0029, alpha=0.1: r=-0.0029, alpha=0.2: r=-0.0047, alpha=0.5: r=-0.0124, permutation band 0.0340. The best smoothing rate still produces a correlation indistinguishable from noise.

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
| Open | computed | `correlation_EMA5` | 0.00285 |
| Close | computed | `correlation_EMA5` | 0.00369 |

Open produced correlation_EMA5=0.00285; Close produced correlation_EMA5=0.00369. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Like every smoother here, it can create apparent trend from pure noise.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
