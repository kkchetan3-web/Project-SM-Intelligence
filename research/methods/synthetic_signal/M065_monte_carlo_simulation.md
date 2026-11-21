# M065 - Monte Carlo Simulation

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_065`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{P}(T \ge t) = \frac{1}{M}\sum_{m=1}^{M}\mathbf{1}[T_m \ge t]`

---

## 1. Definition and mathematical foundation

Monte Carlo simulation generates data from a fully specified null process and compares the resulting statistic distribution with the observed value. It is the reference implementation of 'what would randomness look like', and every p-value reported here has a simulation check.

## 2. Objective

Compare observed statistics with a simulated random process.

## 3. Complete formula

```
\hat{P}(T \ge t) = \frac{1}{M}\sum_{m=1}^{M}\mathbf{1}[T_m \ge t]
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `M` | number of simulated sequences |
| `T_m` | statistic from simulation m |

## 5. Statistical assumptions

- The simulation implements the intended null exactly
- The statistic is computed identically on simulated and real data

## 6. Required input data

Enough compute for M sequences.

## 7. Step-by-step manual calculation

1. Specify the null generating process
2. Simulate M sequences of the same length
3. Compare the observed statistic with the simulated distribution

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Permutation/bootstrap/Monte-Carlo arithmetic is mechanical given a statistic; the toy sequence's contribution is to show the sample size involved. With n=10 the bootstrap has only 10^10 distinct resamples and the permutation group has 10! orderings, so the empirical p-value granularity is 1/(B+1) - fine for the real data, meaningless at this size.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `max_category_count` | 350.00000 | n/a | 0.19934 | 0.34884 | n/a | 300.0 |
| `entropy` | 3.31397 | n/a | 1.00000 | 1.00000 | n/a | 300.0 |
| `longest_same_run` | 4.00000 | n/a | 0.91030 | 0.98032 | n/a | 300.0 |

**Interpretation.** 300 simulated i.i.d. sequences of length 3131 over 10 outcomes: max_category_count: observed 350.0000, simulated mean 341.4233 (sd 10.3069), upper-tail p = 0.199; entropy: observed 3.3140, simulated mean 3.3197 (sd 0.0011), upper-tail p = 1.000; longest_same_run: observed 4.0000, simulated mean 4.2200 (sd 0.6374), upper-tail p = 0.910. The simulated distribution is the exact answer to 'what would randomness look like at this sample size', which is the question every pattern claim must be judged against. Every observed statistic is unremarkable against this reference.

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
| `max_category_count` | 356.00000 | n/a | 0.10963 | 0.23051 | n/a | 300.0 |
| `entropy` | 3.31219 | n/a | 1.00000 | 1.00000 | n/a | 300.0 |
| `longest_same_run` | 3.00000 | n/a | 1.00000 | 1.00000 | n/a | 300.0 |

**Interpretation.** 300 simulated i.i.d. sequences of length 3131 over 10 outcomes: max_category_count: observed 356.0000, simulated mean 341.4233 (sd 10.3069), upper-tail p = 0.110; entropy: observed 3.3122, simulated mean 3.3197 (sd 0.0011), upper-tail p = 1.000; longest_same_run: observed 3.0000, simulated mean 4.2200 (sd 0.6374), upper-tail p = 1.000. The simulated distribution is the exact answer to 'what would randomness look like at this sample size', which is the question every pattern claim must be judged against. Every observed statistic is unremarkable against this reference.

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
| Open | computed | `max_category_count` | 356.00000 |
| Close | computed | `max_category_count` | 350.00000 |

Open produced max_category_count=356.00000; Close produced max_category_count=350.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Simulating the wrong null is worse than not simulating; the platform reports the null that was simulated so the choice can be challenged.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
