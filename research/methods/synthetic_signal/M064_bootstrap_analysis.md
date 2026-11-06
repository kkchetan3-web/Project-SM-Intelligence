# M064 - Bootstrap Analysis

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_064`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\mathrm{CI}_{1-\alpha} = [q_{\alpha/2}(\hat{\theta}^*), q_{1-\alpha/2}(\hat{\theta}^*)]`

---

## 1. Definition and mathematical foundation

The bootstrap estimates sampling variability by resampling the observed data. For time series the naive i.i.d. bootstrap understates variability when observations are dependent, so the moving-block variant is used throughout this platform.

## 2. Objective

Attach confidence intervals to frequency and recurrence estimates.

## 3. Complete formula

```
\mathrm{CI}_{1-\alpha} = [q_{\alpha/2}(\hat{\theta}^*), q_{1-\alpha/2}(\hat{\theta}^*)]
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `theta*` | bootstrap replicate |
| `B` | number of resamples |
| `block` | block length |

## 5. Statistical assumptions

- The resampling scheme reproduces the dependence structure
- The statistic is smooth in the data

## 6. Required input data

Several hundred observations.

## 7. Step-by-step manual calculation

1. Choose a resampling scheme (moving block)
2. Generate B resamples and recompute the statistic
3. Report percentile confidence intervals

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Permutation/bootstrap/Monte-Carlo arithmetic is mechanical given a statistic; the toy sequence's contribution is to show the sample size involved. With n=10 the bootstrap has only 10^10 distinct resamples and the permutation group has 10! orderings, so the empirical p-value granularity is 1/(B+1) - fine for the real data, meaningless at this size.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_ci_width_iid` | 0.02089 | n/a | n/a | n/a | n/a | 1000.0 |
| `mean_ci_width_block` | 0.02061 | n/a | n/a | n/a | n/a | 500.0 |
| `width_ratio_block_over_iid` | 0.98632 | n/a | n/a | n/a | n/a | 1000.0 |
| `uniform_inside_all_ci` | 0.60000 | n/a | n/a | n/a | n/a | 10.0 |
| `max_ci_width` | 0.02268 | n/a | n/a | n/a | n/a | 10.0 |

**Interpretation.** 1000 i.i.d. bootstrap resamples give a mean 95% interval width of 0.02089 for category probabilities; the moving-block bootstrap (block length 5) gives 0.02061, a ratio of 0.986. A ratio near 1 means the sequence carries no extra dependence that widens the true uncertainty. The uniform value 0.10 lies inside 60% of the intervals. Every frequency estimate here should be read with these widths attached: with N=3131 a probability of 0.1 is only pinned to within about ±0.0104.

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
| `mean_ci_width_iid` | 0.02080 | n/a | n/a | n/a | n/a | 1000.0 |
| `mean_ci_width_block` | 0.02045 | n/a | n/a | n/a | n/a | 500.0 |
| `width_ratio_block_over_iid` | 0.98318 | n/a | n/a | n/a | n/a | 1000.0 |
| `uniform_inside_all_ci` | 0.40000 | n/a | n/a | n/a | n/a | 10.0 |
| `max_ci_width` | 0.02268 | n/a | n/a | n/a | n/a | 10.0 |

**Interpretation.** 1000 i.i.d. bootstrap resamples give a mean 95% interval width of 0.02080 for category probabilities; the moving-block bootstrap (block length 5) gives 0.02045, a ratio of 0.983. A ratio near 1 means the sequence carries no extra dependence that widens the true uncertainty. The uniform value 0.10 lies inside 40% of the intervals. Every frequency estimate here should be read with these widths attached: with N=3131 a probability of 0.1 is only pinned to within about ±0.0104.

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
| Open | computed | `mean_ci_width_iid` | 0.02080 |
| Close | computed | `mean_ci_width_iid` | 0.02089 |

Open produced mean_ci_width_iid=0.02080; Close produced mean_ci_width_iid=0.02089. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Block bootstrap requires a block length long enough to span the dependence, which is unknown and must be varied as a sensitivity check.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Efron (1979)
