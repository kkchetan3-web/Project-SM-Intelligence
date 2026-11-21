# M094 - SHAP-Based Feature Interpretation

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_094`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `shap_share_freq_all_6` | 0.06195 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_freq_all_9` | 0.05262 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_history_size` | 0.05010 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_freq_all_5` | 0.03258 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_gap_7` | 0.02665 | n/a | n/a | n/a | n/a | 400.0 |
| `top_feature_share` | 0.06195 | n/a | n/a | n/a | n/a | 400.0 |
| `top5_feature_share` | 0.22390 | n/a | n/a | n/a | n/a | 400.0 |

**Interpretation.** Mean absolute SHAP attributions for a random forest fitted on the first 70% of the window and explained on the next 400 rows. The five most influential features are freq_all_6 (6.2%), freq_all_9 (5.3%), history_size (5.0%), freq_all_5 (3.3%), gap_7 (2.7%), together accounting for 22.4% of total attribution. A model with no real signal spreads attribution across many features rather than concentrating it on one, so diffuse attribution is itself evidence that the model is not latching onto a genuine mechanism. Attributions explain the model, not the world.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `shap_share_history_size` | 0.04207 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_freq_w100_3` | 0.02649 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_freq_all_5` | 0.02617 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_freq_all_2` | 0.02438 | n/a | n/a | n/a | n/a | 400.0 |
| `shap_share_freq_all_4` | 0.02273 | n/a | n/a | n/a | n/a | 400.0 |
| `top_feature_share` | 0.04207 | n/a | n/a | n/a | n/a | 400.0 |
| `top5_feature_share` | 0.14183 | n/a | n/a | n/a | n/a | 400.0 |

**Interpretation.** Mean absolute SHAP attributions for a random forest fitted on the first 70% of the window and explained on the next 400 rows. The five most influential features are history_size (4.2%), freq_w100_3 (2.6%), freq_all_5 (2.6%), freq_all_2 (2.4%), freq_all_4 (2.3%), together accounting for 14.2% of total attribution. A model with no real signal spreads attribution across many features rather than concentrating it on one, so diffuse attribution is itself evidence that the model is not latching onto a genuine mechanism. Attributions explain the model, not the world.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `shap_share_history_size` | 0.04207 |
| Close | computed | `shap_share_freq_all_6` | 0.06195 |

Open produced shap_share_history_size=0.04207; Close produced shap_share_freq_all_6=0.06195. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

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
