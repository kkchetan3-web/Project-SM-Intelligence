# M098 - Ensemble Diversity Optimization

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_098`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\rho_{ij} = \mathrm{corr}(\epsilon_i, \epsilon_j),\quad \sigma^2_{\text{ens}}=\sum_{i,j}w_iw_j\rho_{ij}\sigma_i\sigma_j`

---

## 1. Definition and mathematical foundation

Ensemble variance depends on the correlation between member errors. Two models with identical accuracy but independent errors combine better than two correlated ones, so diversity is a quantity worth measuring rather than assuming.

## 2. Objective

Measure error diversity and test whether it produces a better combination.

## 3. Complete formula

```
\rho_{ij} = \mathrm{corr}(\epsilon_i, \epsilon_j),\quad \sigma^2_{\text{ens}}=\sum_{i,j}w_iw_j\rho_{ij}\sigma_i\sigma_j
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `rho_ij` | error correlation |
| `sigma` | error standard deviation |

## 5. Statistical assumptions

- Base models are individually reasonable
- Error correlation is estimable

## 6. Required input data

At least three base models.

## 7. Step-by-step manual calculation

1. Compute per-observation losses for each model
2. Correlate them across models
3. Compare the diversity-weighted combination with a simple average

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

The arithmetic is the ensemble/metric formula stated above; the substantive question is always whether the held-out comparison clears its uncertainty band, which is what the computed section reports.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_error_correlation` | 0.24623 | n/a | n/a | n/a | n/a | 3743.0 |
| `mean_top1_agreement` | 0.20049 | n/a | n/a | n/a | n/a | 3743.0 |
| `equal_weight_ll` | 2.36611 | n/a | n/a | n/a | n/a | 3743.0 |
| `best_single_ll` | 2.30624 | n/a | n/a | n/a | n/a | 3743.0 |
| `diversity_weighted_ll` | 6.61114 | n/a | n/a | n/a | n/a | 3743.0 |
| `diversity_gain_over_equal` | -4.24504 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** Across 10 models the mean pairwise error correlation is 0.2462 and they agree on the top outcome 20.05% of the time. Equal-weight averaging scores 2.36611; the best single model (svm) scores 2.30624; diversity-weighted averaging scores 6.61114 (-4.24504 versus equal weights). Error correlation is moderate, so there is genuine diversity, but combining diverse models does not create information that none of them has.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mean_error_correlation` | 0.27732 | n/a | n/a | n/a | n/a | 3743.0 |
| `mean_top1_agreement` | 0.21019 | n/a | n/a | n/a | n/a | 3743.0 |
| `equal_weight_ll` | 2.37267 | n/a | n/a | n/a | n/a | 3743.0 |
| `best_single_ll` | 2.30733 | n/a | n/a | n/a | n/a | 3743.0 |
| `diversity_weighted_ll` | 3.40524 | n/a | n/a | n/a | n/a | 3743.0 |
| `diversity_gain_over_equal` | -1.03257 | n/a | n/a | n/a | n/a | 3743.0 |

**Interpretation.** Across 10 models the mean pairwise error correlation is 0.2773 and they agree on the top outcome 21.02% of the time. Equal-weight averaging scores 2.37267; the best single model (svm) scores 2.30733; diversity-weighted averaging scores 3.40524 (-1.03257 versus equal weights). Error correlation is moderate, so there is genuine diversity, but combining diverse models does not create information that none of them has.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `mean_error_correlation` | 0.27732 |
| Close | computed | `mean_error_correlation` | 0.24623 |

Open produced mean_error_correlation=0.27732; Close produced mean_error_correlation=0.24623. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

12 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Diversity among models that are all equally uninformative produces no gain, only a different way of averaging noise.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
