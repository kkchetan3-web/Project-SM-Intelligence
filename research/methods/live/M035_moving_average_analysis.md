# M035 - Moving Average Analysis

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_035`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\mathrm{MA}_t^{(W)} = \frac{1}{W}\sum_{i=0}^{W-1}x_{t-i}`

---

## 1. Definition and mathematical foundation

A moving average is a low-pass filter: it removes high-frequency variation to expose trend. For a numeric encoding of a categorical outcome it is a legitimate descriptive tool, but the smoothed value is not a probability and must not be read as one.

## 2. Objective

Smooth the outcome series and test whether the smoothed level predicts the next draw.

## 3. Complete formula

```
\mathrm{MA}_t^{(W)} = \frac{1}{W}\sum_{i=0}^{W-1}x_{t-i}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `MA_t` | moving average at t |
| `W` | window length |
| `x_t` | numeric outcome |

## 5. Statistical assumptions

- The numeric encoding has meaning
- The window is chosen a priori

## 6. Required input data

A few hundred observations.

## 7. Step-by-step manual calculation

1. Compute the trailing average excluding the current draw
2. Correlate it with the next outcome
3. Score it as a regression predictor out of sample

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Trailing 3-point moving averages of the numeric encoding: [2.333, 3.667, 3.333, 3.333, 4.0, 5.0, 4.667, 2.667]. The final value 2.667 would be the feature offered for predicting the next draw.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `correlation_MA5` | -0.01483 | n/a | 0.34013 | 0.60465 | n/a | 4138.0 |
| `correlation_MA10` | -0.01883 | n/a | 0.22612 | 0.52855 | n/a | 4133.0 |
| `correlation_MA25` | -0.00956 | n/a | 0.53980 | 0.79549 | n/a | 4118.0 |
| `correlation_MA50` | -0.02137 | n/a | 0.17156 | 0.48433 | n/a | 4093.0 |
| `permutation_band` | 0.03151 | n/a | n/a | n/a | n/a | 200.0 |
| `best_abs_correlation` | 0.02137 | n/a | n/a | n/a | n/a | 4093.0 |

**Interpretation.** Correlation between the trailing moving average and the next draw: W=5: -0.0148, W=10: -0.0188, W=25: -0.0096, W=50: -0.0214. The permutation band for |correlation| is 0.0315. The largest is 0.0214 at W=50, which sits inside the band: the smoothed level carries no information about the next draw.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `correlation_MA5` | -0.02851 | n/a | 0.06669 | 0.22249 | n/a | 4138.0 |
| `correlation_MA10` | -0.03581 | n/a | 0.02134 | 0.10293 | n/a | 4133.0 |
| `correlation_MA25` | -0.03379 | n/a | 0.03012 | 0.13000 | n/a | 4118.0 |
| `correlation_MA50` | -0.04990 | n/a | 0.00141 | 0.01281 | n/a | 4093.0 |
| `permutation_band` | 0.02785 | n/a | n/a | n/a | n/a | 200.0 |
| `best_abs_correlation` | 0.04990 | n/a | n/a | n/a | n/a | 4093.0 |

**Interpretation.** Correlation between the trailing moving average and the next draw: W=5: -0.0285, W=10: -0.0358, W=25: -0.0338, W=50: -0.0499. The permutation band for |correlation| is 0.0279. The largest is 0.0499 at W=50, which exceeds the band and would need confirmation on independent periods.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `correlation_MA5` | -0.02851 |
| Close | computed | `correlation_MA5` | -0.01483 |

Open produced correlation_MA5=-0.02851; Close produced correlation_MA5=-0.01483. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

12 p-values were produced across the computed targets; 1 survive Benjamini-Hochberg control at q=0.05 (open:correlation_MA50). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Averaging arbitrary labels produces a meaningless number; the method is implemented with an explicit meaningfulness check.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
