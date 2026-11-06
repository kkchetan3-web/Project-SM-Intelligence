# M035 - Moving Average Analysis

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_035`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `correlation_MA5` | -0.00286 | n/a | 0.87287 | 0.97378 | n/a | 3126.0 |
| `correlation_MA10` | 0.01468 | n/a | 0.41217 | 0.85225 | n/a | 3121.0 |
| `correlation_MA25` | 0.01012 | n/a | 0.57288 | 0.89312 | n/a | 3106.0 |
| `correlation_MA50` | 0.01325 | n/a | 0.46205 | 0.86597 | n/a | 3081.0 |
| `permutation_band` | 0.03593 | n/a | n/a | n/a | n/a | 200.0 |
| `best_abs_correlation` | 0.01468 | n/a | n/a | n/a | n/a | 3121.0 |

**Interpretation.** Correlation between the trailing moving average and the next draw: W=5: -0.0029, W=10: +0.0147, W=25: +0.0101, W=50: +0.0133. The permutation band for |correlation| is 0.0359. The largest is 0.0147 at W=10, which sits inside the band: the smoothed level carries no information about the next draw.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `correlation_MA5` | 0.00949 | n/a | 0.59590 | 0.94116 | n/a | 3126.0 |
| `correlation_MA10` | 0.00280 | n/a | 0.87592 | 0.95768 | n/a | 3121.0 |
| `correlation_MA25` | -0.00448 | n/a | 0.80290 | 0.95417 | n/a | 3106.0 |
| `correlation_MA50` | 0.00636 | n/a | 0.72401 | 0.94351 | n/a | 3081.0 |
| `permutation_band` | 0.03798 | n/a | n/a | n/a | n/a | 200.0 |
| `best_abs_correlation` | 0.00949 | n/a | n/a | n/a | n/a | 3126.0 |

**Interpretation.** Correlation between the trailing moving average and the next draw: W=5: +0.0095, W=10: +0.0028, W=25: -0.0045, W=50: +0.0064. The permutation band for |correlation| is 0.0380. The largest is 0.0095 at W=5, which sits inside the band: the smoothed level carries no information about the next draw.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `correlation_MA5` | 0.00949 |
| Close | computed | `correlation_MA5` | -0.00286 |

Open produced correlation_MA5=0.00949; Close produced correlation_MA5=-0.00286. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

12 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Averaging arbitrary labels produces a meaningless number; the method is implemented with an explicit meaningfulness check.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
