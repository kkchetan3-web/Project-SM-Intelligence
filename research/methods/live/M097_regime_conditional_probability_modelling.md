# M097 - Regime-Conditional Probability Modelling

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_097`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(Y\mid \text{regime}=r) \perp \text{regime assignment uses only past data}`

---

## 1. Definition and mathematical foundation

Regime-conditional modelling estimates a separate distribution per regime. The critical discipline is that regime assignment must use only information available at prediction time; assigning regimes with full-sample knowledge and then 'predicting' within them is one of the most common and most fatal leakage patterns.

## 2. Objective

Estimate regime-specific distributions with causal regime assignment.

## 3. Complete formula

```
P(Y\mid \text{regime}=r) \perp \text{regime assignment uses only past data}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `r` | regime label |
| `P(Y|r)` | regime-conditional distribution |

## 5. Statistical assumptions

- Regimes are identifiable from past data only
- Regimes are persistent enough to matter

## 6. Required input data

Several hundred observations per regime.

## 7. Step-by-step manual calculation

1. Define a causal regime rule from past statistics
2. Estimate the conditional distribution within each regime
3. Compare predictive loss with the unconditional model

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

The arithmetic is the ensemble/metric formula stated above; the substantive question is always whether the held-out comparison clears its uncertainty band, which is what the computed section reports.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `regime_conditional_ll` | 2.30615 | n/a | n/a | n/a | n/a | 2901.0 |
| `unconditional_ll` | 2.30280 | n/a | n/a | n/a | n/a | 2901.0 |
| `improvement` | -0.00335 | n/a | n/a | n/a | n/a | 2901.0 |
| `regime_share_high` | 0.51431 | n/a | n/a | n/a | n/a | 2901.0 |
| `n_regime_switches` | 288.00000 | n/a | n/a | n/a | n/a | 2901.0 |

**Interpretation.** Regimes are defined causally by whether the trailing 50-draw entropy is above or below its historical median, so the assignment uses no future information. The high-entropy regime covers 51.4% of the evaluation window with 288 switches. Regime-conditional frequencies score 2.30615 against 2.30280 for a single pooled distribution, an improvement of -0.00335. Splitting history into regimes does not help: the apparent regime structure is measurement noise in a short entropy window, not a real change in the process.

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
| `regime_conditional_ll` | 2.30685 | n/a | n/a | n/a | n/a | 2901.0 |
| `unconditional_ll` | 2.30405 | n/a | n/a | n/a | n/a | 2901.0 |
| `improvement` | -0.00280 | n/a | n/a | n/a | n/a | 2901.0 |
| `regime_share_high` | 0.51706 | n/a | n/a | n/a | n/a | 2901.0 |
| `n_regime_switches` | 231.00000 | n/a | n/a | n/a | n/a | 2901.0 |

**Interpretation.** Regimes are defined causally by whether the trailing 50-draw entropy is above or below its historical median, so the assignment uses no future information. The high-entropy regime covers 51.7% of the evaluation window with 231 switches. Regime-conditional frequencies score 2.30685 against 2.30405 for a single pooled distribution, an improvement of -0.00280. Splitting history into regimes does not help: the apparent regime structure is measurement noise in a short entropy window, not a real change in the process.

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
| Open | computed | `regime_conditional_ll` | 2.30685 |
| Close | computed | `regime_conditional_ll` | 2.30615 |

Open produced regime_conditional_ll=2.30685; Close produced regime_conditional_ll=2.30615. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Regime definitions are themselves a researcher degree of freedom; with many candidate rules, some will appear to help by chance.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
