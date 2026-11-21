# M012 - Hierarchical Bayesian Probability Modelling

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_012`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\theta_m \sim \mathrm{Dirichlet}(\alpha_0/K,\ldots),\quad \alpha_0 \sim p(\alpha_0)`

---

## 1. Definition and mathematical foundation

Partial pooling lets two markets share information about *how much* their probabilities deviate from uniform, while keeping each market's own probabilities distinct. The hyperparameter encodes the typical deviation; each market is then shrunk toward uniform by an amount determined by its own sample size and by the between-market spread.

## 2. Objective

Estimate a shared concentration across markets and quantify shrinkage per market.

## 3. Complete formula

```
\theta_m \sim \mathrm{Dirichlet}(\alpha_0/K,\ldots),\quad \alpha_0 \sim p(\alpha_0)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `alpha_0` | shared Dirichlet concentration |
| `theta_m` | market m probability vector |
| `shrinkage` | weight given to the uniform prior |

## 5. Statistical assumptions

- Markets share a common concentration but not common probabilities

## 6. Required input data

At least two markets with comparable outcome spaces.

## 7. Step-by-step manual calculation

1. Estimate per-market deviations from uniform
2. Estimate the between-market variance of those deviations
3. Derive the implied per-market shrinkage weight

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

No worked example is defined for this category.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `between_market_variance` | 1.616e-05 | n/a | n/a | n/a | n/a | 2.0 |
| `within_market_sampling_variance` | 2.874e-05 | n/a | n/a | n/a | n/a | 3131.0 |
| `signal_share` | 0.00000 | n/a | n/a | n/a | n/a | 2.0 |
| `shrinkage_to_uniform` | 1.00000 | n/a | n/a | n/a | n/a | 2.0 |

**Interpretation.** Across 2 markets the between-market variance of category deviations is 0.000016, while pure sampling variance at N=3131 is 0.000029. After removing sampling noise, an estimated 0.0% of the observed spread is real between-market difference, implying a shrinkage weight of 100.0% toward the shared uniform mean. With only two markets this hyperparameter estimate is extremely weak evidence and is reported as a mechanism demonstration rather than a finding.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `between_market_variance` | 4.449e-05 | n/a | n/a | n/a | n/a | 2.0 |
| `within_market_sampling_variance` | 2.874e-05 | n/a | n/a | n/a | n/a | 3131.0 |
| `signal_share` | 0.35384 | n/a | n/a | n/a | n/a | 2.0 |
| `shrinkage_to_uniform` | 0.64616 | n/a | n/a | n/a | n/a | 2.0 |

**Interpretation.** Across 2 markets the between-market variance of category deviations is 0.000044, while pure sampling variance at N=3131 is 0.000029. After removing sampling noise, an estimated 35.4% of the observed spread is real between-market difference, implying a shrinkage weight of 64.6% toward the shared uniform mean. With only two markets this hyperparameter estimate is extremely weak evidence and is reported as a mechanism demonstration rather than a finding.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `between_market_variance` | 4.449e-05 |
| Close | computed | `between_market_variance` | 1.616e-05 |

Open produced between_market_variance=4.449e-05; Close produced between_market_variance=1.616e-05. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

With two markets the hyperparameter is estimated from two observations, which is extremely weak evidence; the result is reported as a mechanism demonstration.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
