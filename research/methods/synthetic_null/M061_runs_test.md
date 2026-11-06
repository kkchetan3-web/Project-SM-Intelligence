# M061 - Runs Test

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_061`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `parity_runs` | 1510.00000 | -2.00191 | 0.04529 | 0.72772 | n/a | 3131.0 |
| `parity_expected_runs` | 1565.98116 | n/a | n/a | n/a | n/a | 3131.0 |
| `median_runs` | 1541.00000 | -0.90304 | 0.36650 | 0.85225 | n/a | 3131.0 |
| `median_expected_runs` | 1566.25711 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Parity sequence: 1510 runs against 1566.0 expected (z = -2.002, p = 0.0453). Above/below-median sequence: 1541 runs against 1566.3 (z = -0.903, p = 0.3665). Too few runs means clustering; too many means alternation. At least one categorisation shows run behaviour that departs from randomness. Method 71 tests exactly the same statistic, so these two must not be counted as independent evidence.

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
| `parity_runs` | 1576.00000 | 0.38514 | 0.70013 | 0.94116 | n/a | 3131.0 |
| `parity_expected_runs` | 1565.23507 | n/a | n/a | n/a | n/a | 3131.0 |
| `median_runs` | 1582.00000 | 0.56200 | 0.57412 | 0.94116 | n/a | 3131.0 |
| `median_expected_runs` | 1566.28138 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Parity sequence: 1576 runs against 1565.2 expected (z = +0.385, p = 0.7001). Above/below-median sequence: 1582 runs against 1566.3 (z = +0.562, p = 0.5741). Too few runs means clustering; too many means alternation. Neither categorisation departs from randomness. Method 71 tests exactly the same statistic, so these two must not be counted as independent evidence.

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
| Open | computed | `parity_runs` | 1576.00000 |
| Close | computed | `parity_runs` | 1510.00000 |

Open produced parity_runs=1576.00000; Close produced parity_runs=1510.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The binary split discards most of the information in a 10-category sequence.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Wald & Wolfowitz (1940)
