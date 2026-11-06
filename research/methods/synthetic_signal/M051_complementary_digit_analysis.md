# M051 - Complementary Digit Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_051`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `d' = 9 - d`

---

## 1. Definition and mathematical foundation

The decimal complement maps each digit to its 'partner' summing to nine. Some players treat complements as related; the statistical claim is a negative autocorrelation in the complement variable. It is testable and, so far, consistently unsupported.

## 2. Objective

Test whether complements show elevated or depressed frequency.

## 3. Complete formula

```
d' = 9 - d
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `d'` | complement digit |
| `freq` | empirical frequency of the complement class |

## 5. Statistical assumptions

- Complement is an involution on 0-9
- The mapping is fixed a priori

## 6. Required input data

Any non-empty sample.

## 7. Step-by-step manual calculation

1. Replace each digit by 9-d
2. Compare the frequency of the original and complement classes
3. Test symmetry with an exact binomial test

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Even values in the toy sequence: 2 of 10 (0, 2 are even; 3, 1, 7, 9, 3, 3, 3 are odd). Primes among the observed values: 3, 3, 7, 3, 3, 2, 3 - seven of ten, which is unremarkable on ten draws but illustrates how coarse a partition this is.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `symmetry_chi2` | 22.88973 | n/a | 0.00035 | 0.00134 | n/a | 3131.0 |
| `max_pair_difference` | 83.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `mean_pair_difference` | 47.80000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Testing whether each digit k occurs as often as its complement 9-k: the symmetry chi-square is 22.89 on 5 df (p = 0.0004). Pair counts differ by 47.8 on average (largest 83). At least one complement pair is imbalanced, which would point at a digit-level asymmetry worth investigating in the panel data. Note that the complement transformation is an involution, so a symmetric process cannot produce a complement 'pattern' to exploit.

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
| `symmetry_chi2` | 32.15274 | n/a | 5.541e-06 | 2.065e-05 | n/a | 3131.0 |
| `max_pair_difference` | 83.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `mean_pair_difference` | 59.40000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Testing whether each digit k occurs as often as its complement 9-k: the symmetry chi-square is 32.15 on 5 df (p = 0.0000). Pair counts differ by 59.4 on average (largest 83). At least one complement pair is imbalanced, which would point at a digit-level asymmetry worth investigating in the panel data. Note that the complement transformation is an involution, so a symmetric process cannot produce a complement 'pattern' to exploit.

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
| Open | computed | `symmetry_chi2` | 32.15274 |
| Close | computed | `symmetry_chi2` | 22.88973 |

Open produced symmetry_chi2=32.15274; Close produced symmetry_chi2=22.88973. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 2 survive Benjamini-Hochberg control at q=0.05 (close:symmetry_chi2, open:symmetry_chi2). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Complement symmetry is expected for any symmetric process, so a non-significant result is the informative outcome; a significant one usually indicates asymmetry elsewhere.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
