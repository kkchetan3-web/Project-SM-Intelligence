# M094 - SHAP-Based Feature Interpretation

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_094`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\phi_i = \sum_{S \subseteq F \setminus \{i\}}\frac{|S|!(|F|-|S|-1)!}{|F|!}[f(S\cup\{i\})-f(S)]`

---

## 1. Definition and mathematical foundation

SHAP values attribute a prediction to its features using cooperative-game Shapley values. They are locally accurate and consistent, which makes them the best available tool for asking whether a model is relying on anything sensible - or on a spurious artefact.

## 2. Objective

Explain model predictions and check for spurious reliance.

## 3. Complete formula

```
\phi_i = \sum_{S \subseteq F \setminus \{i\}}\frac{|S|!(|F|-|S|-1)!}{|F|!}[f(S\cup\{i\})-f(S)]
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `phi_i` | attribution to feature i |
| `F` | feature set |
| `S` | coalition |

## 5. Statistical assumptions

- Features are treated as players in a cooperative game
- The model is deterministic

## 6. Required input data

A fitted tree or linear model.

## 7. Step-by-step manual calculation

1. Fit the model on the training window
2. Compute Shapley attributions for a sample of predictions
3. Rank features by mean absolute attribution

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

The arithmetic is the ensemble/metric formula stated above; the substantive question is always whether the held-out comparison clears its uncertainty band, which is what the computed section reports.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `shap_share_freq_all_3` | 0.07395 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_freq_all_9` | 0.04869 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_freq_all_8` | 0.03696 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_prev_mean10` | 0.02707 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_trans_4` | 0.02373 | n/a | n/a | n/a | n/a | 400.0 |
| `top_feature_share` | 0.07395 | n/a | n/a | n/a | n/a | 400.0 |
| `top5_feature_share` | 0.21040 | n/a | n/a | n/a | n/a | 400.0 |

**Interpretation.** Mean absolute SHAP attributions for a random forest fitted on the first 70% of the window and explained on the next 400 rows. The five most influential features are freq_all_3 (7.4%), freq_all_9 (4.9%), freq_all_8 (3.7%), prev_mean10 (2.7%), trans_4 (2.4%), together accounting for 21.0% of total attribution. A model with no real signal spreads attribution across many features rather than concentrating it on one, so diffuse attribution is itself evidence that the model is not latching onto a genuine mechanism. Attributions explain the model, not the world.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `shap_share_freq_all_3` | 0.04399 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_history_size` | 0.02806 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_freq_all_4` | 0.02581 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_freq_all_8` | 0.02540 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_freq_all_1` | 0.02478 | n/a | n/a | n/a | n/a | 400.0 |
| `top_feature_share` | 0.04399 | n/a | n/a | n/a | n/a | 400.0 |
| `top5_feature_share` | 0.14804 | n/a | n/a | n/a | n/a | 400.0 |

**Interpretation.** Mean absolute SHAP attributions for a random forest fitted on the first 70% of the window and explained on the next 400 rows. The five most influential features are freq_all_3 (4.4%), history_size (2.8%), freq_all_4 (2.6%), freq_all_8 (2.5%), freq_all_1 (2.5%), together accounting for 14.8% of total attribution. A model with no real signal spreads attribution across many features rather than concentrating it on one, so diffuse attribution is itself evidence that the model is not latching onto a genuine mechanism. Attributions explain the model, not the world.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `shap_share_freq_all_3` | 0.04399 |
| Close | computed | `shap_share_freq_all_3` | 0.07395 |

Open produced shap_share_freq_all_3=0.04399; Close produced shap_share_freq_all_3=0.07395. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

14 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Attributions explain the model, not the world; a large attribution to a meaningless feature is a warning about the model rather than a discovery.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Lundberg & Lee (2017)
