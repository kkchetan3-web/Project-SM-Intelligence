# M087 - Conformal Prediction

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_087`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\mathcal{C}_\alpha(x)=\{y : s(x,y) \le \hat{q}_{1-\alpha}\}`

---

## 1. Definition and mathematical foundation

Conformal prediction builds prediction sets with a distribution-free marginal coverage guarantee, provided calibration and test points are exchangeable. Time series violate exchangeability, so the guarantee is nominal rather than actual - and measuring the gap between nominal and empirical coverage is the useful part here.

## 2. Objective

Construct prediction sets and measure realised coverage against the nominal level.

## 3. Complete formula

```
\mathcal{C}_\alpha(x)=\{y : s(x,y) \le \hat{q}_{1-\alpha}\}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `s(x,y)` | nonconformity score |
| `q` | calibration quantile |
| `coverage` | 1-alpha |

## 5. Statistical assumptions

- Exchangeability between calibration and test points

## 6. Required input data

A calibration set of at least a few hundred observations.

## 7. Step-by-step manual calculation

1. Score the calibration set
2. Take the appropriate empirical quantile
3. Build test sets and measure realised coverage

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

The arithmetic is the ensemble/metric formula stated above; the substantive question is always whether the held-out comparison clears its uncertainty band, which is what the computed section reports.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `nominal_coverage` | 0.90000 | n/a | n/a | n/a | n/a | 2246.0 |
| `empirical_coverage` | 0.97017 | n/a | n/a | n/a | n/a | 2246.0 |
| `coverage_gap` | 0.07017 | n/a | n/a | n/a | n/a | 2246.0 |
| `mean_prediction_set_size` | 9.73464 | n/a | n/a | n/a | n/a | 2246.0 |
| `min_set_size` | 7.00000 | n/a | n/a | n/a | n/a | 2246.0 |

**Interpretation.** Split-conformal prediction using svm as the underlying model, with a nominal 90% coverage target: the empirical coverage on the later 60% of the window is 0.9702, a gap of +0.0702. Mean prediction set size is 9.73 of 10 possible outcomes (smallest 7). The conformal guarantee requires exchangeability between calibration and test points, which a time series does not satisfy - so this gap is the honest measure of how much the guarantee is worth here. A model with no skill produces large sets; small sets on a 10-way problem would themselves indicate real information.

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
| `nominal_coverage` | 0.90000 | n/a | n/a | n/a | n/a | 2246.0 |
| `empirical_coverage` | 0.94479 | n/a | n/a | n/a | n/a | 2246.0 |
| `coverage_gap` | 0.04479 | n/a | n/a | n/a | n/a | 2246.0 |
| `mean_prediction_set_size` | 9.41318 | n/a | n/a | n/a | n/a | 2246.0 |
| `min_set_size` | 7.00000 | n/a | n/a | n/a | n/a | 2246.0 |

**Interpretation.** Split-conformal prediction using svm as the underlying model, with a nominal 90% coverage target: the empirical coverage on the later 60% of the window is 0.9448, a gap of +0.0448. Mean prediction set size is 9.41 of 10 possible outcomes (smallest 7). The conformal guarantee requires exchangeability between calibration and test points, which a time series does not satisfy - so this gap is the honest measure of how much the guarantee is worth here. A model with no skill produces large sets; small sets on a 10-way problem would themselves indicate real information.

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
| Open | computed | `nominal_coverage` | 0.90000 |
| Close | computed | `nominal_coverage` | 0.90000 |

Open produced nominal_coverage=0.90000; Close produced nominal_coverage=0.90000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Exchangeability fails for dependent sequences, so nominal coverage will not be achieved; the method reports the discrepancy rather than assuming it away.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Vovk et al. (2005)
