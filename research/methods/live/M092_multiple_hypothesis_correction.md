# M092 - Multiple Hypothesis Correction

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_092`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `p_i^{\text{Holm}} = \max_{j \le i}\left((n-j+1)p_{(j)}\right)`

---

## 1. Definition and mathematical foundation

Family-wise error control bounds the probability of *any* false rejection. Holm's step-down procedure is uniformly more powerful than Bonferroni while retaining that guarantee, which makes it the sensible default when a single false claim is costly.

## 2. Objective

Apply family-wise error control and compare it with FDR control.

## 3. Complete formula

```
p_i^{\text{Holm}} = \max_{j \le i}\left((n-j+1)p_{(j)}\right)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `p_(j)` | j-th ordered p-value |
| `n` | number of tests |

## 5. Statistical assumptions

- Tests are valid marginally
- The family of tests is defined in advance

## 6. Required input data

A defined family of tests.

## 7. Step-by-step manual calculation

1. Order the p-values
2. Apply the Holm step-down adjustment
3. Compare surviving findings with the BH set

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Ten hypothetical p-values [0.001, 0.008, 0.039, 0.041, 0.049, 0.2, 0.35, 0.62, 0.88, 0.97].

```
ranked          = [0.001, 0.008, 0.039, 0.041, 0.049, 0.2, 0.35, 0.62, 0.88, 0.97]
BH adjusted     = [0.01, 0.04, 0.098, 0.098, 0.098, 0.3333, 0.5, 0.775, 0.97, 0.97]
Holm adjusted   = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]
```
BH keeps the three smallest; Holm keeps only the first two. That is the power/stringency trade-off the two methods are meant to expose.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `n_tests` | 84.00000 | n/a | n/a | n/a | n/a | 84.0 |
| `n_significant_holm` | 4.00000 | n/a | n/a | n/a | n/a | 84.0 |
| `n_significant_bonferroni` | 4.00000 | n/a | n/a | n/a | n/a | 84.0 |
| `holm_min_adjusted` | 0.00000 | n/a | n/a | n/a | n/a | 84.0 |
| `holm_bonferroni_power_gain` | 0.00000 | n/a | n/a | n/a | n/a | 84.0 |

**Interpretation.** Family-wise error control across 84 tests: Holm leaves 4 rejections, Bonferroni 4. Holm is uniformly at least as powerful as Bonferroni and never less, so the difference (0) is free power. Surviving findings: M058:chi2_pos0_1, M058:chi2_pos0_2, M058:chi2_pos1_2, M059:hamming_chi2. FWER control is the correct standard when a single false claim would be costly, and it is deliberately harsher than the FDR procedure in Method 91.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `n_tests` | 82.00000 | n/a | n/a | n/a | n/a | 82.0 |
| `n_significant_holm` | 7.00000 | n/a | n/a | n/a | n/a | 82.0 |
| `n_significant_bonferroni` | 7.00000 | n/a | n/a | n/a | n/a | 82.0 |
| `holm_min_adjusted` | 0.00000 | n/a | n/a | n/a | n/a | 82.0 |
| `holm_bonferroni_power_gain` | 0.00000 | n/a | n/a | n/a | n/a | 82.0 |

**Interpretation.** Family-wise error control across 82 tests: Holm leaves 7 rejections, Bonferroni 7. Holm is uniformly at least as powerful as Bonferroni and never less, so the difference (0) is free power. Surviving findings: M049:digit_sum_chi2, M058:chi2_pos0_1, M058:chi2_pos0_2, M058:chi2_pos1_2, M059:hamming_chi2, M062:ljungbox_parity_lag10, M062:ljungbox_parity_lag20. FWER control is the correct standard when a single false claim would be costly, and it is deliberately harsher than the FDR procedure in Method 91.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `n_tests` | 82.00000 |
| Close | computed | `n_tests` | 84.00000 |

Open produced n_tests=82.00000; Close produced n_tests=84.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

FWER control is very strict with 100 correlated tests; it is reported alongside FDR rather than instead of it.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Holm (1979)
