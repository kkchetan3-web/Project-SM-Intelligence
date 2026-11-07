# M010 - Categorical Distribution Testing

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_010`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\chi^2_{\text{indep}} = \sum_{i,j}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}`

---

## 1. Definition and mathematical foundation

Beyond the one-sample fit of M009, categorical inference compares two or more empirical distributions. Comparing early and late periods (or two markets) uses the contingency chi-square, with the same expected-count caveat and the same need for an effect size.

## 2. Objective

Test whether the distribution is stable across sub-periods.

## 3. Complete formula

```
\chi^2_{\text{indep}} = \sum_{i,j}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `O_ij` | observed cell count |
| `E_ij` | expected under homogeneity |
| `df` | (r-1)(c-1) |

## 5. Statistical assumptions

- Sub-periods are independent samples
- Expected cell counts are adequate

## 6. Required input data

At least 5 expected observations per cell.

## 7. Step-by-step manual calculation

1. Split the sample into consecutive halves
2. Build the period-by-category contingency table
3. Apply the chi-square test and report Cramer's V

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Expected count = 10/10 = 1 per outcome.

```
chi2 = (4-1)^2/1 + 5 x (1-1)^2/1 + 4 x (0-1)^2/1 = 9 + 0 + 4 = 20.0
df = 9
```
The expected-count assumption fails badly here, which is exactly why the method record requires min E_k >= 5.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `halves_chi2` | 4.84717 | 4.84717 | 0.84742 | 1.00000 | 0.03420 | 4143.0 |
| `halves_cramers_v` | 0.03420 | n/a | n/a | n/a | n/a | 4143.0 |
| `thirds_chi2` | 6.09155 | 6.09155 | 0.99581 | 1.00000 | 0.02711 | 4143.0 |

**Interpretation.** Comparing the first and second halves of the sample gives chi-square 4.847 (p = 0.8474, V = 0.0342). A three-way split gives chi-square 6.092 (p = 0.9958). The distribution is stable across periods, so pooling is defensible.

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
| `halves_chi2` | 11.11334 | 11.11334 | 0.26802 | 0.53604 | 0.05179 | 4143.0 |
| `halves_cramers_v` | 0.05179 | n/a | n/a | n/a | n/a | 4143.0 |
| `thirds_chi2` | 13.59030 | 13.59030 | 0.75538 | 0.92450 | 0.04050 | 4143.0 |

**Interpretation.** Comparing the first and second halves of the sample gives chi-square 11.113 (p = 0.2680, V = 0.0518). A three-way split gives chi-square 13.590 (p = 0.7554). The distribution is stable across periods, so pooling is defensible.

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
| Open | computed | `halves_chi2` | 11.11334 |
| Close | computed | `halves_chi2` | 4.84717 |

Open produced halves_chi2=11.11334; Close produced halves_chi2=4.84717. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

A significant result indicates non-stationarity, which undermines every pooled estimate in the platform.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
