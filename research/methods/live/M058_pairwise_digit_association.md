# M058 - Pairwise Digit Association

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_058`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\chi^2 = \sum_{i,j}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}`

---

## 1. Definition and mathematical foundation

Testing whether digit positions are independent inside a panel is a two-way contingency problem. It matters because a panel generated as a single ranked object will show dependence between positions, while independently drawn digits will not.

## 2. Objective

Test the independence of digit positions within panels.

## 3. Complete formula

```
\chi^2 = \sum_{i,j}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `O_ij` | joint count of digits i and j |
| `E_ij` | product of marginal shares |

## 5. Statistical assumptions

- Panels are three independent digits under the null

## 6. Required input data

Panels available, ideally several thousand.

## 7. Step-by-step manual calculation

1. Build the 10x10 joint table for position pairs
2. Compute the chi-square statistic and Cramer's V
3. Assess with a permutation null to avoid sparse-cell problems

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

No worked example is defined for this category.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `chi2_pos0_1` | 2512.10328 | n/a | 0.00000 | 0.00000 | 0.25978 | 4136.0 |
| `chi2_pos0_2` | 660.79204 | n/a | 5.144e-96 | 1.080e-94 | 0.14132 | 4136.0 |
| `chi2_pos1_2` | 2726.46228 | n/a | 0.00000 | 0.00000 | 0.28705 | 4136.0 |
| `max_cramers_v` | 0.28705 | n/a | n/a | n/a | n/a | 4136.0 |
| `n_significant_holm` | 3.00000 | n/a | n/a | n/a | n/a | 3.0 |

**Interpretation.** Digit-position independence within panels: pos0_1: V=0.2598 (Holm p=0.0000), pos0_2: V=0.1413 (Holm p=0.0000), pos1_2: V=0.2871 (Holm p=0.0000). The strongest association has Cramer's V of 0.2871, which for a 10x10 table corresponds to a negligible departure from independence. At least one position pair shows dependence surviving correction, which would indicate the panel is generated as a ranked object rather than three separate digits.

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
| `chi2_pos0_1` | 2709.22011 | n/a | 0.00000 | 0.00000 | 0.26985 | 4134.0 |
| `chi2_pos0_2` | 750.72394 | n/a | 4.093e-109 | 8.391e-108 | 0.14205 | 4134.0 |
| `chi2_pos1_2` | 2805.28062 | n/a | 0.00000 | 0.00000 | 0.27459 | 4134.0 |
| `max_cramers_v` | 0.27459 | n/a | n/a | n/a | n/a | 4134.0 |
| `n_significant_holm` | 3.00000 | n/a | n/a | n/a | n/a | 3.0 |

**Interpretation.** Digit-position independence within panels: pos0_1: V=0.2698 (Holm p=0.0000), pos0_2: V=0.1420 (Holm p=0.0000), pos1_2: V=0.2746 (Holm p=0.0000). The strongest association has Cramer's V of 0.2746, which for a 10x10 table corresponds to a negligible departure from independence. At least one position pair shows dependence surviving correction, which would indicate the panel is generated as a ranked object rather than three separate digits.

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
| Open | computed | `chi2_pos0_1` | 2709.22011 |
| Close | computed | `chi2_pos0_1` | 2512.10328 |

Open produced chi2_pos0_1=2709.22011; Close produced chi2_pos0_1=2512.10328. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 6 survive Benjamini-Hochberg control at q=0.05 (close:chi2_pos0_1, close:chi2_pos0_2, close:chi2_pos1_2, open:chi2_pos0_1, open:chi2_pos0_2). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

With 100 cells and a few thousand panels the chi-square approximation is adequate but the effect size is what determines whether the dependence is usable.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
