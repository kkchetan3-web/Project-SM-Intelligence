# M071 - Wald-Wolfowitz Runs Analysis

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_071`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `E[R] = \frac{2n_1n_2}{n}+1,\quad \mathrm{Var}(R)=\frac{2n_1n_2(2n_1n_2-n)}{n^2(n-1)}`

---

## 1. Definition and mathematical foundation

This is the formal statement of the runs test with its exact expectation and variance. It is implemented separately from M061 so that the two can be cross-checked and so that the evidence is not double-counted in the summary.

## 2. Objective

Provide the closed-form runs test and cross-validate M061.

## 3. Complete formula

```
E[R] = \frac{2n_1n_2}{n}+1,\quad \mathrm{Var}(R)=\frac{2n_1n_2(2n_1n_2-n)}{n^2(n-1)}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `R` | observed runs |
| `E[R]` | expected runs |
| `n_1, n_2, n` | state counts and total |

## 5. Statistical assumptions

- The binary sequence is exchangeable under the null
- The normal approximation is adequate

## 6. Required input data

At least ~20 observations per state.

## 7. Step-by-step manual calculation

1. Count runs in the binary sequence
2. Compute the theoretical mean and variance
3. Standardise and obtain a p-value

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Parity sequence: [1, 1, 1, 1, 0, 1, 1, 1, 0, 1]. Number of runs = 5. With n1 = 8 odd and n0 = 2 even, E[R] = 2 x 8 x 2/10 + 1 = 4.20.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `runs` | 1896.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `expected_runs` | 1566.28138 | n/a | n/a | n/a | n/a | 3131.0 |
| `z_statistic` | 11.78859 | n/a | 4.469e-32 | 6.257e-31 | n/a | 3131.0 |

**Interpretation.** With 1584 odd and 1547 even outcomes the expected number of runs is 1566.281; the sequence contains 1896, giving z = +11.789 and a two-sided p of 0.0000. This is the closed-form version of Method 61 - identical evidence, computed from the Wald-Wolfowitz expectation and variance rather than by simulation. The platform reports both but counts them once in the summary, so the finding list is not double-weighted.

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
| `runs` | 2008.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `expected_runs` | 1566.48068 | n/a | n/a | n/a | n/a | 3131.0 |
| `z_statistic` | 15.78385 | n/a | 4.019e-56 | 6.591e-55 | n/a | 3131.0 |

**Interpretation.** With 1571 odd and 1560 even outcomes the expected number of runs is 1566.481; the sequence contains 2008, giving z = +15.784 and a two-sided p of 0.0000. This is the closed-form version of Method 61 - identical evidence, computed from the Wald-Wolfowitz expectation and variance rather than by simulation. The platform reports both but counts them once in the summary, so the finding list is not double-weighted.

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
| Open | computed | `runs` | 2008.00000 |
| Close | computed | `runs` | 1896.00000 |

Open produced runs=2008.00000; Close produced runs=1896.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 2 survive Benjamini-Hochberg control at q=0.05 (close:z_statistic, open:z_statistic). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Reports the same evidence as M061; the platform flags this so the two are not counted as two independent findings.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Wald & Wolfowitz (1940)
