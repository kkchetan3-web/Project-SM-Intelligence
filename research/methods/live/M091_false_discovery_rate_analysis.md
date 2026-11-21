# M091 - False Discovery Rate Analysis

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_091`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\mathrm{FDR} = \mathbb{E}\left[\frac{V}{\max(R,1)}\right]`

---

## 1. Definition and mathematical foundation

Testing 100 methods produces many p-values, and at alpha=0.05 roughly five spurious rejections are expected by construction. The Benjamini-Hochberg procedure controls the expected proportion of false discoveries and is far less conservative than family-wise correction when many tests are genuinely null.

## 2. Objective

Control the false discovery rate across all method p-values.

## 3. Complete formula

```
\mathrm{FDR} = \mathbb{E}\left[\frac{V}{\max(R,1)}\right]
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `V` | false discoveries |
| `R` | total rejections |
| `q` | target FDR |

## 5. Statistical assumptions

- Tests are independent or positively dependent
- P-values are valid under the null

## 6. Required input data

A collected set of valid p-values.

## 7. Step-by-step manual calculation

1. Collect every p-value produced by the method suite
2. Sort and apply the Benjamini-Hochberg step-up procedure
3. Report which findings survive

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
| `n_tests_collected` | 84.00000 | n/a | n/a | n/a | n/a | 84.0 |
| `n_significant_uncorrected` | 14.00000 | n/a | n/a | n/a | n/a | 84.0 |
| `n_significant_bh` | 4.00000 | n/a | n/a | n/a | n/a | 84.0 |
| `expected_false_positives_uncorrected` | 4.20000 | n/a | n/a | n/a | n/a | 84.0 |
| `smallest_p_value` | 0.00000 | n/a | 0.00000 | n/a | n/a | 84.0 |

**Interpretation.** 84 p-values were collected across the method suite. At the 5% level, 14 are nominally significant, and about 4.2 would be expected by chance alone. Benjamini-Hochberg at q=0.05 leaves 4 significant (M058:chi2_pos0_1, M058:chi2_pos0_2, M058:chi2_pos1_2, M059:hamming_chi2). A subset survives FDR control, but note the tests are strongly dependent (many share the same underlying sequence), which makes BH conservative here rather than invalid.

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
| `n_tests_collected` | 82.00000 | n/a | n/a | n/a | n/a | 82.0 |
| `n_significant_uncorrected` | 21.00000 | n/a | n/a | n/a | n/a | 82.0 |
| `n_significant_bh` | 13.00000 | n/a | n/a | n/a | n/a | 82.0 |
| `expected_false_positives_uncorrected` | 4.10000 | n/a | n/a | n/a | n/a | 82.0 |
| `smallest_p_value` | 0.00000 | n/a | 0.00000 | n/a | n/a | 82.0 |

**Interpretation.** 82 p-values were collected across the method suite. At the 5% level, 21 are nominally significant, and about 4.1 would be expected by chance alone. Benjamini-Hochberg at q=0.05 leaves 13 significant (M013:most_overdue_hit_rate, M035:correlation_MA50, M037:correlation_EMA5, M043:month_parity_chi2, M049:digit_sum_chi2, M057:repeat_rate, M058:chi2_pos0_1, M058:chi2_pos0_2). A subset survives FDR control, but note the tests are strongly dependent (many share the same underlying sequence), which makes BH conservative here rather than invalid.

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
| Open | computed | `n_tests_collected` | 82.00000 |
| Close | computed | `n_tests_collected` | 84.00000 |

Open produced n_tests_collected=82.00000; Close produced n_tests_collected=84.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

BH assumes independence or positive dependence; the tests here are heavily correlated, which makes it conservative rather than invalid.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Benjamini & Hochberg (1995)
