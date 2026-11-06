# M029 - Autocorrelation Function

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_029`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\rho_k = \frac{\sum_t (x_t-\bar{x})(x_{t-k}-\bar{x})}{\sum_t (x_t-\bar{x})^2}`

---

## 1. Definition and mathematical foundation

Autocorrelation measures linear serial dependence. Applied to the numeric encoding of an ank it asks whether large values follow large values; applied to indicator series it asks whether a category's presence predicts its own presence. Bands from a permutation null replace the inappropriate i.i.d. Gaussian bands.

## 2. Objective

Detect linear serial dependence at multiple lags.

## 3. Complete formula

```
\rho_k = \frac{\sum_t (x_t-\bar{x})(x_{t-k}-\bar{x})}{\sum_t (x_t-\bar{x})^2}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `rho_k` | lag-k autocorrelation |
| `band` | permutation-based significance band |

## 5. Statistical assumptions

- The numeric encoding has a defensible ordering
- The series is stationary over the window

## 6. Required input data

A few hundred observations for stable estimates.

## 7. Step-by-step manual calculation

1. Choose the representation (indicator or numeric)
2. Compute autocorrelations up to the configured maximum lag
3. Compare against a permutation null band

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

No worked example is defined for this category.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `max_abs_autocorrelation` | 0.05025 | n/a | n/a | n/a | n/a | 3131.0 |
| `permutation_95pct_band` | 0.05163 | n/a | n/a | n/a | n/a | 3131.0 |
| `lags_exceeding_band` | 0.00000 | n/a | n/a | n/a | n/a | 20.0 |
| `acf_lag1` | 0.01408 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Autocorrelation of the numeric outcome encoding peaks at 0.0502 (lag 3). A permutation null of 300 shuffles puts the 95th percentile of the maximum absolute autocorrelation at 0.0516; 0 of 20 lags exceed it. The series shows no autocorrelation beyond what shuffling produces.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `max_abs_autocorrelation` | 0.03577 | n/a | n/a | n/a | n/a | 3131.0 |
| `permutation_95pct_band` | 0.05294 | n/a | n/a | n/a | n/a | 3131.0 |
| `lags_exceeding_band` | 0.00000 | n/a | n/a | n/a | n/a | 20.0 |
| `acf_lag1` | -0.01350 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Autocorrelation of the numeric outcome encoding peaks at 0.0358 (lag 5). A permutation null of 300 shuffles puts the 95th percentile of the maximum absolute autocorrelation at 0.0529; 0 of 20 lags exceed it. The series shows no autocorrelation beyond what shuffling produces.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `max_abs_autocorrelation` | 0.03577 |
| Close | computed | `max_abs_autocorrelation` | 0.05025 |

Open produced max_abs_autocorrelation=0.03577; Close produced max_abs_autocorrelation=0.05025. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

The most transferable category across markets, since it needs only a sequence. Data hunger grows sharply with order (K^order contexts).

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Transition-based methods are scored by walk-forward log loss against the expanding frequency baseline, which is the only comparison that answers 'does history help'.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

A flat ACF does not imply independence - nonlinear dependence is invisible to it, which is why M031 is also required.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
