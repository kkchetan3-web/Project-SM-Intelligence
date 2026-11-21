# M057 - Numerical Distance Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_057`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `d_t = |x_t - x_{t-1}|`

---

## 1. Definition and mathematical foundation

Absolute change between consecutive outcomes measures how far the process moves each step. For an i.i.d. uniform digit sequence the distribution of the change is exactly known - it is triangular on 0-9 - so comparing against that distribution is a sharp test of independence.

## 2. Objective

Compare the step-size distribution with the independence prediction.

## 3. Complete formula

```
d_t = |x_t - x_{t-1}|
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `d_t` | absolute change |
| `distribution` | theoretical triangular law |

## 5. Statistical assumptions

- The numeric encoding has meaning
- Steps are comparable across the sample

## 6. Required input data

A meaningful numeric encoding.

## 7. Step-by-step manual calculation

1. Compute consecutive absolute differences
2. Tabulate the distribution
3. Compare with the exact i.i.d. prediction using a chi-square test

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

No worked example is defined for this category.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_absolute_step` | 2.94920 | n/a | n/a | n/a | n/a | 3130.0 |
| `repeat_rate` | 0.08498 | n/a | 0.00464 | 0.01298 | n/a | 3130.0 |
| `step_chi2` | 561.39949 | n/a | 4.002e-115 | 1.681e-113 | n/a | 3130.0 |

**Interpretation.** Consecutive draws differ by 2.949 on average; independent uniform digits predict 3.300. The next draw equals the previous one 0.0850 of the time against 0.1000 expected (exact binomial p = 0.0046). The full step distribution gives chi-square 561.40 on 9 df (p = 0.0000). Step sizes depart from the independence prediction; Method 23 recasts the same evidence as a transition matrix and Method 91 corrects for multiplicity.

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
| `mean_absolute_step` | 2.94856 | n/a | n/a | n/a | n/a | 3130.0 |
| `repeat_rate` | 0.06965 | n/a | 3.399e-09 | 2.788e-08 | n/a | 3130.0 |
| `step_chi2` | 1041.72398 | n/a | 1.731e-218 | 7.097e-217 | n/a | 3130.0 |

**Interpretation.** Consecutive draws differ by 2.949 on average; independent uniform digits predict 3.300. The next draw equals the previous one 0.0696 of the time against 0.1000 expected (exact binomial p = 0.0000). The full step distribution gives chi-square 1041.72 on 9 df (p = 0.0000). Step sizes depart from the independence prediction; Method 23 recasts the same evidence as a transition matrix and Method 91 corrects for multiplicity.

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
| Open | computed | `mean_absolute_step` | 2.94856 |
| Close | computed | `mean_absolute_step` | 2.94920 |

Open produced mean_absolute_step=2.94856; Close produced mean_absolute_step=2.94920. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 4 survive Benjamini-Hochberg control at q=0.05 (close:repeat_rate, close:step_chi2, open:repeat_rate, open:step_chi2). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

A bounded discrete outcome cannot move by more than K-1, so the distribution is truncated; the theoretical comparison must respect the boundary.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
