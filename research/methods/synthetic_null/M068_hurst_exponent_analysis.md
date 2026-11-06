# M068 - Hurst Exponent Analysis

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_068`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\mathbb{E}\left[\frac{R(n)}{S(n)}\right] \sim n^{H}`

---

## 1. Definition and mathematical foundation

The Hurst exponent describes long-range dependence: H=0.5 is a random walk, H>0.5 persistent, H<0.5 anti-persistent. Rescaled-range analysis is noisy on short samples, so the estimate is reported with a simulation-based reference band for the sample size actually available.

## 2. Objective

Test for long-range dependence and interpret against a simulated null.

## 3. Complete formula

```
\mathbb{E}\left[\frac{R(n)}{S(n)}\right] \sim n^{H}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `H` | Hurst exponent |
| `R(n)` | range of partial sums |
| `S(n)` | standard deviation |

## 5. Statistical assumptions

- The series is long enough for stable range statistics
- The numeric encoding is meaningful

## 6. Required input data

At least several hundred observations.

## 7. Step-by-step manual calculation

1. Form partial sums of deviations from the mean
2. Compute the rescaled range at several scales
3. Regress log(R/S) on log(n) and compare H with a simulated band

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Entropy, Hurst and latent-state estimators are all severely biased below ~100 observations, so no honest worked example exists at n=10. The method record states the minimum sample size; the computed section reports the real estimate with its simulated reference band, which is the only defensible way to read it.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `hurst_exponent` | 0.58480 | n/a | n/a | n/a | n/a | 3131.0 |
| `simulated_hurst_mean` | 0.58271 | n/a | n/a | n/a | n/a | 100.0 |
| `simulated_hurst_95pct_low` | 0.55111 | n/a | n/a | n/a | n/a | 100.0 |
| `simulated_hurst_95pct_high` | 0.61502 | n/a | n/a | n/a | n/a | 100.0 |
| `n_scales_used` | 6.00000 | n/a | n/a | n/a | n/a | 6.0 |

**Interpretation.** Rescaled-range estimate of the Hurst exponent is 0.5848 using 6 scales. For simulated i.i.d. sequences of the same length the estimator averages 0.5827 with a 95% interval of [0.5511, 0.6150] - note how far this is from the textbook 0.5, which is exactly why the simulated band is required. The observed exponent lies inside the simulated interval, so there is no evidence of long-range dependence.

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
| `hurst_exponent` | 0.58720 | n/a | n/a | n/a | n/a | 3131.0 |
| `simulated_hurst_mean` | 0.58271 | n/a | n/a | n/a | n/a | 100.0 |
| `simulated_hurst_95pct_low` | 0.55111 | n/a | n/a | n/a | n/a | 100.0 |
| `simulated_hurst_95pct_high` | 0.61502 | n/a | n/a | n/a | n/a | 100.0 |
| `n_scales_used` | 6.00000 | n/a | n/a | n/a | n/a | 6.0 |

**Interpretation.** Rescaled-range estimate of the Hurst exponent is 0.5872 using 6 scales. For simulated i.i.d. sequences of the same length the estimator averages 0.5827 with a 95% interval of [0.5511, 0.6150] - note how far this is from the textbook 0.5, which is exactly why the simulated band is required. The observed exponent lies inside the simulated interval, so there is no evidence of long-range dependence.

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
| Open | computed | `hurst_exponent` | 0.58720 |
| Close | computed | `hurst_exponent` | 0.58480 |

Open produced hurst_exponent=0.58720; Close produced hurst_exponent=0.58480. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

R/S analysis is severely biased on short series and can produce H far from 0.5 for pure noise; the simulated band is not optional.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Hurst (1951)
