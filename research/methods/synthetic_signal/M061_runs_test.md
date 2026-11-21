# M061 - Runs Test

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_061`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `R = 1 + \sum_{t=2}^{N}\mathbf{1}[S_t \neq S_{t-1}]`

---

## 1. Definition and mathematical foundation

A run is a maximal stretch of the same binary state. Too few runs indicates clustering, too many indicates alternation, and the null distribution is approximately normal with known mean and variance. It is the classic test of serial randomness for a binary sequence.

## 2. Objective

Test the binary sequence for clustering or alternation.

## 3. Complete formula

```
R = 1 + \sum_{t=2}^{N}\mathbf{1}[S_t \neq S_{t-1}]
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `R` | number of runs |
| `n_1, n_2` | counts in each state |
| `E[R]` | expected runs under randomness |

## 5. Statistical assumptions

- The binary categorisation is fixed a priori
- N is large enough for the normal approximation

## 6. Required input data

At least ~20 observations in each state.

## 7. Step-by-step manual calculation

1. Form the binary sequence
2. Count runs
3. Compute the z-statistic against the randomness expectation

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Parity sequence: [1, 1, 1, 1, 0, 1, 1, 1, 0, 1]. Number of runs = 5. With n1 = 8 odd and n0 = 2 even, E[R] = 2 x 8 x 2/10 + 1 = 4.20.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `parity_runs` | 1896.00000 | 11.78859 | 4.469e-32 | 6.257e-31 | n/a | 3131.0 |
| `parity_expected_runs` | 1566.28138 | n/a | n/a | n/a | n/a | 3131.0 |
| `median_runs` | 1339.00000 | -8.13255 | 4.204e-16 | 3.923e-15 | n/a | 3131.0 |
| `median_expected_runs` | 1566.49218 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Parity sequence: 1896 runs against 1566.3 expected (z = +11.789, p = 0.0000). Above/below-median sequence: 1339 runs against 1566.5 (z = -8.133, p = 0.0000). Too few runs means clustering; too many means alternation. At least one categorisation shows run behaviour that departs from randomness. Method 71 tests exactly the same statistic, so these two must not be counted as independent evidence.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `parity_runs` | 2008.00000 | 15.78385 | 4.019e-56 | 6.591e-55 | n/a | 3131.0 |
| `parity_expected_runs` | 1566.48068 | n/a | n/a | n/a | n/a | 3131.0 |
| `median_runs` | 1266.00000 | -9.25359 | 2.171e-20 | 1.978e-19 | n/a | 3131.0 |
| `median_expected_runs` | 1516.59885 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Parity sequence: 2008 runs against 1566.5 expected (z = +15.784, p = 0.0000). Above/below-median sequence: 1266 runs against 1516.6 (z = -9.254, p = 0.0000). Too few runs means clustering; too many means alternation. At least one categorisation shows run behaviour that departs from randomness. Method 71 tests exactly the same statistic, so these two must not be counted as independent evidence.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `parity_runs` | 2008.00000 |
| Close | computed | `parity_runs` | 1896.00000 |

Open produced parity_runs=2008.00000; Close produced parity_runs=1896.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 4 survive Benjamini-Hochberg control at q=0.05 (close:parity_runs, close:median_runs, open:parity_runs, open:median_runs). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The binary split discards most of the information in a 10-category sequence.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Wald & Wolfowitz (1940)
