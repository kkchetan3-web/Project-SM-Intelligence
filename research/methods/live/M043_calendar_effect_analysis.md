# M043 - Calendar Effect Analysis

**Category:** D - Time Series  
**Implementation:** `src.mathematics.time_series::run_043`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\chi^2_{\text{cal}} = \sum_{d}\sum_{k}\frac{(O_{dk}-E_{dk})^2}{E_{dk}}`

---

## 1. Definition and mathematical foundation

Calendar effects assert that the day of week, day of month or month changes the distribution. Such features are known in advance, which makes them attractive predictors, and the many possible calendar partitions guarantee that some will look significant by chance unless the tests are corrected.

## 2. Objective

Test calendar features for distributional effects with multiple-testing control.

## 3. Complete formula

```
\chi^2_{\text{cal}} = \sum_{d}\sum_{k}\frac{(O_{dk}-E_{dk})^2}{E_{dk}}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `O_dk` | count of outcome k on calendar state d |
| `df` | degrees of freedom |
| `adjusted p` | FDR-controlled p-value |

## 5. Statistical assumptions

- Calendar features are known before the draw
- Observations in each cell are exchangeable

## 6. Required input data

Enough full cycles to populate each calendar cell.

## 7. Step-by-step manual calculation

1. Partition dates by weekday, month and day-of-month band
2. Build contingency tables and test homogeneity
3. Apply Benjamini-Hochberg across the calendar features tested

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

On a ten-point discrete sequence no AR/ARMA/ARIMA model is identified: with n=10 there are fewer observations than parameters, so the design matrix is rank-deficient and the fit is not determined. The worked arithmetic for the actual data is in the computed-results section, where n is 3131.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `weekday_chi2` | 36.83950 | n/a | 0.80151 | 1.00000 | 0.04217 | 4143.0 |
| `month_chi2` | 109.88027 | n/a | 0.21372 | 0.52855 | 0.05429 | 4143.0 |
| `dom_band_chi2` | 43.84815 | n/a | 0.17297 | 0.48433 | 0.05144 | 4143.0 |
| `weekday_parity_chi2` | 2.93905 | n/a | 0.70938 | 0.93106 | 0.02663 | 4143.0 |
| `month_parity_chi2` | 19.70096 | n/a | 0.04961 | 0.29769 | 0.06896 | 4143.0 |
| `n_tests` | 5.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `n_significant_uncorrected` | 1.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `n_significant_holm` | 0.00000 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** 5 calendar tests were run. Uncorrected, 1 reach p<0.05; after Holm correction across the family, 0 do. With 5 tests, 0.2 uncorrected rejections are expected by chance alone, so the uncorrected count is exactly the noise level. Calendar features are known in advance, which makes them attractive; the tests show whether they actually change the outcome distribution.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 8,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `weekday_chi2` | 34.57844 | n/a | 0.86975 | 0.94779 | 0.04086 | 4143.0 |
| `month_chi2` | 107.39628 | n/a | 0.26510 | 0.53604 | 0.05367 | 4143.0 |
| `dom_band_chi2` | 29.22649 | n/a | 0.78074 | 0.94148 | 0.04200 | 4143.0 |
| `weekday_parity_chi2` | 0.79885 | n/a | 0.97711 | 1.00000 | 0.01389 | 4143.0 |
| `month_parity_chi2` | 30.60052 | n/a | 0.00127 | 0.01281 | 0.08594 | 4143.0 |
| `n_tests` | 5.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `n_significant_uncorrected` | 1.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `n_significant_holm` | 1.00000 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** 5 calendar tests were run. Uncorrected, 1 reach p<0.05; after Holm correction across the family, 1 do. With 5 tests, 0.2 uncorrected rejections are expected by chance alone, so the uncorrected count is exactly the noise level. Calendar features are known in advance, which makes them attractive; the tests show whether they actually change the outcome distribution.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 8,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `weekday_chi2` | 34.57844 |
| Close | computed | `weekday_chi2` | 36.83950 |

Open produced weekday_chi2=34.57844; Close produced weekday_chi2=36.83950. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis or pannas. Seasonality methods assume an unbroken daily calendar.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample one-step-ahead comparison for the predictive claim; the two are never conflated.

## 13. Statistical interpretation

16 p-values were produced across the computed targets; 1 survive Benjamini-Hochberg control at q=0.05 (open:month_parity_chi2). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

These markets draw most days, so calendar partitions have small cells and multiple testing is severe.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
