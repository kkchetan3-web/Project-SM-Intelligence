# M051 - Complementary Digit Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_051`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
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
| `symmetry_chi2` | 6.31918 | n/a | 0.27639 | 0.54559 | n/a | 4143.0 |
| `max_pair_difference` | 51.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `mean_pair_difference` | 25.80000 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** Testing whether each digit k occurs as often as its complement 9-k: the symmetry chi-square is 6.32 on 5 df (p = 0.2764). Pair counts differ by 25.8 on average (largest 51). The complement pairs are balanced, as they must be for an unremarkable process. Note that the complement transformation is an involution, so a symmetric process cannot produce a complement 'pattern' to exploit.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `symmetry_chi2` | 2.85488 | n/a | 0.72235 | 0.89890 | n/a | 4143.0 |
| `max_pair_difference` | 30.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `mean_pair_difference` | 18.20000 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** Testing whether each digit k occurs as often as its complement 9-k: the symmetry chi-square is 2.85 on 5 df (p = 0.7223). Pair counts differ by 18.2 on average (largest 30). The complement pairs are balanced, as they must be for an unremarkable process. Note that the complement transformation is an involution, so a symmetric process cannot produce a complement 'pattern' to exploit.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `symmetry_chi2` | 2.85488 |
| Close | computed | `symmetry_chi2` | 6.31918 |

Open produced symmetry_chi2=2.85488; Close produced symmetry_chi2=6.31918. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Complement symmetry is expected for any symmetric process, so a non-significant result is the informative outcome; a significant one usually indicates asymmetry elsewhere.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
