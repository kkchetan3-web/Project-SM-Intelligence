# M003 - Rolling Frequency Analysis

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_003`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{p}_{k,t} = \frac{1}{W}\sum_{i=t-W+1}^{t}\mathbf{1}[X_i=k]`

---

## 1. Definition and mathematical foundation

A moving window makes the empirical measure local in time, trading variance for adaptivity. If the generating process is stationary the rolling estimate is strictly worse than the expanding one; if it drifts, the rolling estimate can be better. Which holds is an empirical question answered by out-of-sample log loss.

## 2. Objective

Test whether recent-window frequencies predict future draws better than long-run frequencies.

## 3. Complete formula

```
\hat{p}_{k,t} = \frac{1}{W}\sum_{i=t-W+1}^{t}\mathbf{1}[X_i=k]
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `W` | window length in observations |
| `p_k,t` | smoothed probability at time t |
| `log loss` | mean negative log predictive density |

## 5. Statistical assumptions

- Window length W is chosen a priori
- The underlying process is locally homogeneous

## 6. Required input data

N > 5W to leave a usable out-of-sample window.

## 7. Step-by-step manual calculation

1. For each W in the configured grid, produce causal predictions
2. Score every step with log loss
3. Compare against the expanding-frequency and uniform baselines

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

No worked example is defined for this category.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `rolling_ll_w25` | 2.40006 | n/a | n/a | n/a | n/a | 3131.0 |
| `rolling_ll_w50` | 2.37031 | n/a | n/a | n/a | n/a | 3131.0 |
| `rolling_ll_w100` | 2.33057 | n/a | n/a | n/a | n/a | 3131.0 |
| `rolling_ll_w250` | 2.31478 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_window` | 250.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_rolling_ll` | 2.31478 | n/a | n/a | n/a | n/a | 3131.0 |
| `expanding_ll` | 2.30041 | n/a | n/a | n/a | n/a | 3131.0 |
| `improvement_over_expanding` | -0.01437 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Out-of-sample log loss by window: W=25: 2.40006, W=50: 2.37031, W=100: 2.33057, W=250: 2.31478. The expanding-frequency baseline scores 2.30041. Best window is W=250 at 2.31478. No window beats the expanding average, so restricting to recent history loses information rather than gaining adaptivity.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 8,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `rolling_ll_w25` | 2.40088 | n/a | n/a | n/a | n/a | 3131.0 |
| `rolling_ll_w50` | 2.36278 | n/a | n/a | n/a | n/a | 3131.0 |
| `rolling_ll_w100` | 2.33648 | n/a | n/a | n/a | n/a | 3131.0 |
| `rolling_ll_w250` | 2.31573 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_window` | 250.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_rolling_ll` | 2.31573 | n/a | n/a | n/a | n/a | 3131.0 |
| `expanding_ll` | 2.30219 | n/a | n/a | n/a | n/a | 3131.0 |
| `improvement_over_expanding` | -0.01354 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Out-of-sample log loss by window: W=25: 2.40088, W=50: 2.36278, W=100: 2.33648, W=250: 2.31573. The expanding-frequency baseline scores 2.30219. Best window is W=250 at 2.31573. No window beats the expanding average, so restricting to recent history loses information rather than gaining adaptivity.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 8,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `rolling_ll_w25` | 2.40088 |
| Close | computed | `rolling_ll_w25` | 2.40006 |

Open produced rolling_ll_w25=2.40088; Close produced rolling_ll_w25=2.40006. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

16 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Short windows are noisy (10 categories, W=25 gives about 2.5 observations per category); long windows cannot adapt. The grid search itself consumes sample.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
