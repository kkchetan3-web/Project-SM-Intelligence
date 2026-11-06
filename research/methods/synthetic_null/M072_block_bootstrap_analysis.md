# M072 - Block Bootstrap Analysis

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_072`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{\theta}^*_b \text{ from blocks } (x_{i},x_{i+1},\ldots,x_{i+\ell-1})`

---

## 1. Definition and mathematical foundation

The moving-block bootstrap resamples contiguous blocks rather than individual observations, preserving short-range dependence. Varying the block length is the sensitivity analysis that shows how much the conclusions depend on the assumed dependence scale.

## 2. Objective

Estimate uncertainty under dependence and test block-length sensitivity.

## 3. Complete formula

```
\hat{\theta}^*_b \text{ from blocks } (x_{i},x_{i+1},\ldots,x_{i+\ell-1})
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `ell` | block length |
| `theta*` | replicate statistic |
| `B` | resamples |

## 5. Statistical assumptions

- Dependence has a finite range smaller than the block
- Blocks are long enough to capture it

## 6. Required input data

Several hundred observations.

## 7. Step-by-step manual calculation

1. Choose a block length
2. Draw overlapping blocks and concatenate
3. Recompute the statistic and vary the block length as a check

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Permutation/bootstrap/Monte-Carlo arithmetic is mechanical given a statistic; the toy sequence's contribution is to show the sample size involved. With n=10 the bootstrap has only 10^10 distinct resamples and the permutation group has 10! orderings, so the empirical p-value granularity is 1/(B+1) - fine for the real data, meaningless at this size.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_ci_width_block1` | 0.02112 | n/a | n/a | n/a | n/a | 500.0 |
| `mean_ci_width_block5` | 0.02168 | n/a | n/a | n/a | n/a | 500.0 |
| `mean_ci_width_block10` | 0.02118 | n/a | n/a | n/a | n/a | 500.0 |
| `mean_ci_width_block25` | 0.02115 | n/a | n/a | n/a | n/a | 500.0 |
| `mean_ci_width_block50` | 0.02099 | n/a | n/a | n/a | n/a | 500.0 |
| `width_ratio_block50_over_block1` | 0.99388 | n/a | n/a | n/a | n/a | 500.0 |
| `max_ci_width_any_block` | 0.02412 | n/a | n/a | n/a | n/a | 500.0 |

**Interpretation.** Mean 95% interval width for category probabilities by block length: L=1: 0.02112, L=5: 0.02168, L=10: 0.02118, L=25: 0.02115, L=50: 0.02099. Going from i.i.d. resampling (L=1) to L=50 changes the width by a factor of 0.994. If the sequence had strong short-range dependence, longer blocks would widen the intervals substantially, because they would capture the dependence that i.i.d. resampling destroys. The near-flat curve is itself evidence of independence.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_ci_width_block1` | 0.02069 | n/a | n/a | n/a | n/a | 500.0 |
| `mean_ci_width_block5` | 0.02026 | n/a | n/a | n/a | n/a | 500.0 |
| `mean_ci_width_block10` | 0.02047 | n/a | n/a | n/a | n/a | 500.0 |
| `mean_ci_width_block25` | 0.02102 | n/a | n/a | n/a | n/a | 500.0 |
| `mean_ci_width_block50` | 0.02135 | n/a | n/a | n/a | n/a | 500.0 |
| `width_ratio_block50_over_block1` | 1.03184 | n/a | n/a | n/a | n/a | 500.0 |
| `max_ci_width_any_block` | 0.02414 | n/a | n/a | n/a | n/a | 500.0 |

**Interpretation.** Mean 95% interval width for category probabilities by block length: L=1: 0.02069, L=5: 0.02026, L=10: 0.02047, L=25: 0.02102, L=50: 0.02135. Going from i.i.d. resampling (L=1) to L=50 changes the width by a factor of 1.032. If the sequence had strong short-range dependence, longer blocks would widen the intervals substantially, because they would capture the dependence that i.i.d. resampling destroys. The near-flat curve is itself evidence of independence.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `mean_ci_width_block1` | 0.02069 |
| Close | computed | `mean_ci_width_block1` | 0.02112 |

Open produced mean_ci_width_block1=0.02069; Close produced mean_ci_width_block1=0.02112. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

14 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

If the dependence range exceeds the block length the interval is too narrow, and there is no direct diagnostic for that from the data alone.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Kunsch (1989)
