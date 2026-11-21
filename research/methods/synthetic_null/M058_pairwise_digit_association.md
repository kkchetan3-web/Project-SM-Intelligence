# M058 - Pairwise Digit Association

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_058`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `chi2_pos0_1` | 97.44071 | n/a | 0.10294 | 0.73172 | 0.05880 | 3131.0 |
| `chi2_pos0_2` | 62.73951 | n/a | 0.93395 | 0.98154 | 0.04719 | 3131.0 |
| `chi2_pos1_2` | 73.91890 | n/a | 0.69869 | 0.89312 | 0.05122 | 3131.0 |
| `max_cramers_v` | 0.05880 | n/a | n/a | n/a | n/a | 3131.0 |
| `n_significant_holm` | 0.00000 | n/a | n/a | n/a | n/a | 3.0 |

**Interpretation.** Digit-position independence within panels: pos0_1: V=0.0588 (Holm p=0.3088), pos0_2: V=0.0472 (Holm p=1.0000), pos1_2: V=0.0512 (Holm p=1.0000). The strongest association has Cramer's V of 0.0588, which for a 10x10 table corresponds to a negligible departure from independence. Digit positions are independent within panels.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `chi2_pos0_1` | 71.89163 | n/a | 0.75535 | 0.95291 | 0.05051 | 3131.0 |
| `chi2_pos0_2` | 87.09440 | n/a | 0.30174 | 0.94116 | 0.05559 | 3131.0 |
| `chi2_pos1_2` | 92.90665 | n/a | 0.17233 | 0.88318 | 0.05742 | 3131.0 |
| `max_cramers_v` | 0.05742 | n/a | n/a | n/a | n/a | 3131.0 |
| `n_significant_holm` | 0.00000 | n/a | n/a | n/a | n/a | 3.0 |

**Interpretation.** Digit-position independence within panels: pos0_1: V=0.0505 (Holm p=0.7554), pos0_2: V=0.0556 (Holm p=0.6035), pos1_2: V=0.0574 (Holm p=0.5170). The strongest association has Cramer's V of 0.0574, which for a 10x10 table corresponds to a negligible departure from independence. Digit positions are independent within panels.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `chi2_pos0_1` | 71.89163 |
| Close | computed | `chi2_pos0_1` | 97.44071 |

Open produced chi2_pos0_1=71.89163; Close produced chi2_pos0_1=97.44071. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

With 100 cells and a few thousand panels the chi-square approximation is adequate but the effect size is what determines whether the dependence is usable.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
