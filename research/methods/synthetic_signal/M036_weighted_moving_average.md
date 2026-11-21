# M036 - Weighted Moving Average

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_036`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\mathrm{WMA}_t = \frac{\sum_{i=0}^{W-1}w_i x_{t-i}}{\sum_i w_i}`

---

## 1. Definition and mathematical foundation

Descending weights inside the window let the filter favour recent values without abandoning the rest. It interpolates between the simple moving average and an exponential filter and is useful mainly as a robustness check on the latter.

## 2. Objective

Compare a linearly weighted filter with the simple and exponential alternatives.

## 3. Complete formula

```
\mathrm{WMA}_t = \frac{\sum_{i=0}^{W-1}w_i x_{t-i}}{\sum_i w_i}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `w_i` | weight for lag i |
| `WMA_t` | weighted average |

## 5. Statistical assumptions

- Weights are fixed a priori
- The window is fixed a priori

## 6. Required input data

A few hundred observations.

## 7. Step-by-step manual calculation

1. Choose linear descending weights
2. Compute the trailing weighted average
3. Compare predictive loss with MA and EMA

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Trailing 3-point moving averages of the numeric encoding: [2.333, 3.667, 3.333, 3.333, 4.0, 5.0, 4.667, 2.667]. The final value 2.667 would be the feature offered for predicting the next draw.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `correlation_WMA10` | 0.03733 | n/a | 0.03708 | 0.08197 | n/a | 3120.0 |
| `correlation_WMA25` | 0.01391 | n/a | 0.43830 | 0.59382 | n/a | 3105.0 |
| `permutation_band` | 0.03919 | n/a | n/a | n/a | n/a | 200.0 |

**Interpretation.** Linearly weighted moving averages: W=10: r=+0.0373, W=25: r=+0.0139 against a permutation band of 0.0392. Weighting recent draws more heavily inside the window does not reveal structure that the simple average missed.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `correlation_WMA10` | 0.00232 | n/a | 0.89693 | 1.00000 | n/a | 3120.0 |
| `correlation_WMA25` | -0.00548 | n/a | 0.76008 | 0.95887 | n/a | 3105.0 |
| `permutation_band` | 0.03878 | n/a | n/a | n/a | n/a | 200.0 |

**Interpretation.** Linearly weighted moving averages: W=10: r=+0.0023, W=25: r=-0.0055 against a permutation band of 0.0388. Weighting recent draws more heavily inside the window does not reveal structure that the simple average missed.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `correlation_WMA10` | 0.00232 |
| Close | computed | `correlation_WMA10` | 0.03733 |

Open produced correlation_WMA10=0.00232; Close produced correlation_WMA10=0.03733. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Adds a tuning dimension for little theoretical gain.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
