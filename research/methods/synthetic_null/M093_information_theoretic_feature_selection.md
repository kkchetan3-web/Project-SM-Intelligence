# M093 - Information-Theoretic Feature Selection

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_093`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\mathrm{MI}(X_i;Y) = \sum p(x_i,y)\log\frac{p(x_i,y)}{p(x_i)p(y)}`

---

## 1. Definition and mathematical foundation

Ranking features by mutual information with the target selects on relevance rather than on linear correlation. Redundancy between selected features is then removed with conditional mutual information, which is the principled way to avoid 40 collinear frequency features.

## 2. Objective

Rank features by information content and remove redundancy.

## 3. Complete formula

```
\mathrm{MI}(X_i;Y) = \sum p(x_i,y)\log\frac{p(x_i,y)}{p(x_i)p(y)}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `MI` | mutual information with the target |
| `redundancy` | MI between features |

## 5. Statistical assumptions

- Features are estimable
- Relevance implies potential usefulness

## 6. Required input data

Several hundred observations.

## 7. Step-by-step manual calculation

1. Compute MI between each feature and the target
2. Remove features that are redundant with a stronger one
3. Evaluate the retained set chronologically

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

The arithmetic is the ensemble/metric formula stated above; the substantive question is always whether the held-out comparison clears its uncertainty band, which is what the computed section reports.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `n_features` | 77.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `top_feature_mi` | 0.01361 | n/a | 0.01000 | 0.72772 | n/a | 3131.0 |
| `second_feature_mi` | 0.01298 | n/a | n/a | n/a | n/a | 3131.0 |
| `permutation_null_mean` | 0.00834 | n/a | n/a | n/a | n/a | 99.0 |
| `permutation_null_95pct` | 0.01127 | n/a | n/a | n/a | n/a | 99.0 |
| `n_features_above_null_95pct` | 7.00000 | n/a | n/a | n/a | n/a | 77.0 |

**Interpretation.** 77 causal features were each quintile-discretised and scored by mutual information with the target. The strongest is 'dom' at 0.01361 bits (permutation p = 0.010); the permutation null gives 0.00834 bits on average (95th percentile 0.01127) purely from finite-sample bias. 7 features exceed that reference. Some features exceed the bias floor; the model results in Methods 73-84 show whether that information survives a chronological test.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `n_features` | 73.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `top_feature_mi` | 0.01367 | n/a | 0.01000 | 0.41000 | n/a | 3131.0 |
| `second_feature_mi` | 0.01277 | n/a | n/a | n/a | n/a | 3131.0 |
| `permutation_null_mean` | 0.00829 | n/a | n/a | n/a | n/a | 99.0 |
| `permutation_null_95pct` | 0.01185 | n/a | n/a | n/a | n/a | 99.0 |
| `n_features_above_null_95pct` | 3.00000 | n/a | n/a | n/a | n/a | 73.0 |

**Interpretation.** 73 causal features were each quintile-discretised and scored by mutual information with the target. The strongest is 'ewm_099_max_excess' at 0.01367 bits (permutation p = 0.010); the permutation null gives 0.00829 bits on average (95th percentile 0.01185) purely from finite-sample bias. 3 features exceed that reference. Some features exceed the bias floor; the model results in Methods 73-84 show whether that information survives a chronological test.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `n_features` | 73.00000 |
| Close | computed | `n_features` | 77.00000 |

Open produced n_features=73.00000; Close produced n_features=77.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

12 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

MI is biased upward for continuous features with many effective bins; the ranking is therefore computed on discretised features with a permutation reference.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
