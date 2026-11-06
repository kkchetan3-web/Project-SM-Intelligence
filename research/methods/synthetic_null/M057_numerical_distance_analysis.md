# M057 - Numerical Distance Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_057`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `mean_absolute_step` | 3.25016 | n/a | n/a | n/a | n/a | 3130.0 |
| `repeat_rate` | 0.11278 | n/a | 0.01857 | 0.72772 | n/a | 3130.0 |
| `step_chi2` | 11.18350 | n/a | 0.26334 | 0.85225 | n/a | 3130.0 |

**Interpretation.** Consecutive draws differ by 3.250 on average; independent uniform digits predict 3.300. The next draw equals the previous one 0.1128 of the time against 0.1000 expected (exact binomial p = 0.0186). The full step distribution gives chi-square 11.18 on 9 df (p = 0.2633). Step sizes behave exactly as independence predicts.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_absolute_step` | 3.34665 | n/a | n/a | n/a | n/a | 3130.0 |
| `repeat_rate` | 0.08850 | n/a | 0.03191 | 0.65418 | n/a | 3130.0 |
| `step_chi2` | 11.58736 | n/a | 0.23758 | 0.94116 | n/a | 3130.0 |

**Interpretation.** Consecutive draws differ by 3.347 on average; independent uniform digits predict 3.300. The next draw equals the previous one 0.0885 of the time against 0.1000 expected (exact binomial p = 0.0319). The full step distribution gives chi-square 11.59 on 9 df (p = 0.2376). Step sizes behave exactly as independence predicts.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `mean_absolute_step` | 3.34665 |
| Close | computed | `mean_absolute_step` | 3.25016 |

Open produced mean_absolute_step=3.34665; Close produced mean_absolute_step=3.25016. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

A bounded discrete outcome cannot move by more than K-1, so the distribution is truncated; the theoretical comparison must respect the boundary.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
