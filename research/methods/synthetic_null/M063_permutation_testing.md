# M063 - Permutation Testing

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_063`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `p = \frac{1+\sum_{b=1}^{B}\mathbf{1}[T_b \ge T_{\text{obs}}]}{B+1}`

---

## 1. Definition and mathematical foundation

A permutation test builds the null distribution of a statistic by rearranging the observed values, which is valid whenever the null corresponds to exchangeability. It makes no distributional assumption, which is exactly what a 10-category discrete process needs.

## 2. Objective

Obtain valid p-values without distributional assumptions.

## 3. Complete formula

```
p = \frac{1+\sum_{b=1}^{B}\mathbf{1}[T_b \ge T_{\text{obs}}]}{B+1}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `T_obs` | observed statistic |
| `T_b` | statistic on permutation b |
| `B` | number of permutations |
| `p` | empirical p-value |

## 5. Statistical assumptions

- Observations are exchangeable under the null
- The statistic is computed identically on permuted data

## 6. Required input data

B large enough to resolve the p-value of interest.

## 7. Step-by-step manual calculation

1. Compute the observed statistic
2. Generate B random permutations and recompute
3. Compute the empirical p-value with the +1 correction

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Permutation/bootstrap/Monte-Carlo arithmetic is mechanical given a statistic; the toy sequence's contribution is to show the sample size involved. With n=10 the bootstrap has only 10^10 distinct resamples and the permutation group has 10! orderings, so the empirical p-value granularity is 1/(B+1) - fine for the real data, meaningless at this size.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `max_abs_frequency_deviation` | 0.01051 | n/a | 1.00000 | 1.00000 | n/a | 3131.0 |
| `entropy_deficit` | 0.00150 | n/a | 1.00000 | 1.00000 | n/a | 3131.0 |
| `lag1_mutual_information` | 0.01698 | n/a | 0.71700 | 0.89312 | n/a | 3131.0 |

**Interpretation.** 999 random permutations of the outcome sequence give an exact null distribution for three statistics: max_abs_frequency_deviation = 0.01051 (null mean 0.01051, p = 1.0000); entropy_deficit = 0.00150 (null mean 0.00150, p = 1.0000); lag1_mutual_information = 0.01698 (null mean 0.01871, p = 0.7170). Permutation is exact here because the null hypothesis of exchangeability is precisely what shuffling destroys, so no distributional approximation is involved. All three statistics lie well inside their permutation nulls, which is what an i.i.d. process looks like.

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
| `max_abs_frequency_deviation` | 0.00993 | n/a | 1.00000 | 1.00000 | n/a | 3131.0 |
| `entropy_deficit` | 0.00158 | n/a | 1.00000 | 1.00000 | n/a | 3131.0 |
| `lag1_mutual_information` | 0.02185 | n/a | 0.15300 | 0.83640 | n/a | 3131.0 |

**Interpretation.** 999 random permutations of the outcome sequence give an exact null distribution for three statistics: max_abs_frequency_deviation = 0.00993 (null mean 0.00993, p = 1.0000); entropy_deficit = 0.00158 (null mean 0.00158, p = 1.0000); lag1_mutual_information = 0.02185 (null mean 0.01868, p = 0.1530). Permutation is exact here because the null hypothesis of exchangeability is precisely what shuffling destroys, so no distributional approximation is involved. All three statistics lie well inside their permutation nulls, which is what an i.i.d. process looks like.

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
| Open | computed | `max_abs_frequency_deviation` | 0.00993 |
| Close | computed | `max_abs_frequency_deviation` | 0.01051 |

Open produced max_abs_frequency_deviation=0.00993; Close produced max_abs_frequency_deviation=0.01051. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Permutation destroys only the structure the null asserts; if the series has trend, a plain permutation is the wrong null.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
