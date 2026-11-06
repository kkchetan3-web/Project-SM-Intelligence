# M095 - Stability Selection

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_095`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{\Pi}_i = \frac{1}{B}\sum_{b=1}^{B}\mathbf{1}[i \in \hat{S}(D_b)]`

---

## 1. Definition and mathematical foundation

Stability selection refits a selection procedure on many subsamples and keeps features chosen frequently. It converts a fragile, sample-specific selection into a reproducible one and provides a principled threshold on the selection frequency.

## 2. Objective

Identify features that are selected reproducibly.

## 3. Complete formula

```
\hat{\Pi}_i = \frac{1}{B}\sum_{b=1}^{B}\mathbf{1}[i \in \hat{S}(D_b)]
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `Pi_i` | selection probability of feature i |
| `S(D_b)` | selected set on subsample b |

## 5. Statistical assumptions

- Subsamples are drawn from the same distribution
- The base selector is sparse

## 6. Required input data

Enough observations for subsampling to be informative.

## 7. Step-by-step manual calculation

1. Draw B subsamples
2. Run the selector on each
3. Report selection frequencies and retain features above the threshold

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

The arithmetic is the ensemble/metric formula stated above; the substantive question is always whether the held-out comparison clears its uncertainty band, which is what the computed section reports.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `n_subsamples` | 20.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `k_selected_per_run` | 10.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `max_selection_frequency` | 0.60000 | n/a | n/a | n/a | n/a | 20.0 |
| `n_features_above_0.5` | 1.00000 | n/a | n/a | n/a | n/a | 77.0 |
| `n_features_above_threshold` | 0.00000 | n/a | n/a | n/a | n/a | 77.0 |

**Interpretation.** An F-test selector (k=10) refitted on 20 random 60% subsamples. The most frequently selected feature is 'freq_all_3' at 60%; 1 features are chosen in more than half the runs and 0 exceed the stability threshold of 0.600. With no stable signal, selection frequencies stay near the k/n_features = 13% you would get from random selection - which is what is observed. Stability selection converts a fragile, sample-specific selection into a reproducible one, which is valuable even when the answer is 'nothing is stable'.

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
| `n_subsamples` | 20.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `k_selected_per_run` | 10.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `max_selection_frequency` | 0.85000 | n/a | n/a | n/a | n/a | 20.0 |
| `n_features_above_0.5` | 6.00000 | n/a | n/a | n/a | n/a | 73.0 |
| `n_features_above_threshold` | 6.00000 | n/a | n/a | n/a | n/a | 73.0 |

**Interpretation.** An F-test selector (k=10) refitted on 20 random 60% subsamples. The most frequently selected feature is 'freq_w25_max_excess' at 85%; 6 features are chosen in more than half the runs and 6 exceed the stability threshold of 0.600. Some features are selected consistently, but stability within a sample is not evidence of a real effect; the chronological tests are decisive. Stability selection converts a fragile, sample-specific selection into a reproducible one, which is valuable even when the answer is 'nothing is stable'.

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
| Open | computed | `n_subsamples` | 20.00000 |
| Close | computed | `n_subsamples` | 20.00000 |

Open produced n_subsamples=20.00000; Close produced n_subsamples=20.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Frequent selection can reflect a strong but spurious association that is stable within the sample, so stability is necessary but not sufficient.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Meinshausen & Buhlmann (2010)
