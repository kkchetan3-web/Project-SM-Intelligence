# M037 - Exponential Moving Average

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_037`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
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
| `correlation_EMA5` | -0.02902 | n/a | 0.06180 | 0.33175 | n/a | 4142.0 |
| `correlation_EMA10` | -0.02153 | n/a | 0.16590 | 0.48433 | n/a | 4142.0 |
| `correlation_EMA20` | -0.01847 | n/a | 0.23467 | 0.52855 | n/a | 4142.0 |
| `correlation_EMA50` | -0.01842 | n/a | 0.23584 | 0.52855 | n/a | 4142.0 |
| `permutation_band` | 0.03262 | n/a | n/a | n/a | n/a | 200.0 |

**Interpretation.** Exponential moving average correlations: alpha=0.05: r=-0.0290, alpha=0.1: r=-0.0215, alpha=0.2: r=-0.0185, alpha=0.5: r=-0.0184, permutation band 0.0326. The best smoothing rate still produces a correlation indistinguishable from noise.

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
| `correlation_EMA5` | -0.04723 | n/a | 0.00236 | 0.01489 | n/a | 4142.0 |
| `correlation_EMA10` | -0.03655 | n/a | 0.01866 | 0.10200 | n/a | 4142.0 |
| `correlation_EMA20` | -0.02260 | n/a | 0.14586 | 0.32325 | n/a | 4142.0 |
| `correlation_EMA50` | 0.00170 | n/a | 0.91290 | 0.95972 | n/a | 4142.0 |
| `permutation_band` | 0.03216 | n/a | n/a | n/a | n/a | 200.0 |

**Interpretation.** Exponential moving average correlations: alpha=0.05: r=-0.0472, alpha=0.1: r=-0.0365, alpha=0.2: r=-0.0226, alpha=0.5: r=+0.0017, permutation band 0.0322. The best smoothing rate still produces a correlation indistinguishable from noise.

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
| Open | computed | `correlation_EMA5` | -0.04723 |
| Close | computed | `correlation_EMA5` | -0.02902 |

Open produced correlation_EMA5=-0.04723; Close produced correlation_EMA5=-0.02902. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 1 survive Benjamini-Hochberg control at q=0.05 (open:correlation_EMA5). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Like every smoother here, it can create apparent trend from pure noise.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
