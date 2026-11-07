# M005 - Bayesian Frequency Estimation

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_005`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(\theta \mid D) \propto P(D \mid \theta)P(\theta)`

---

## 1. Definition and mathematical foundation

A Dirichlet prior conjugates the categorical likelihood, so the posterior is Dirichlet and the posterior mean shrinks raw frequencies toward the prior mean. The shrinkage weight is exactly the ratio of prior to total concentration, which makes the amount of 'belief' in the prior explicit and auditable.

## 2. Objective

Estimate outcome probabilities with an explicit prior and attach credible intervals.

## 3. Complete formula

```
P(\theta \mid D) \propto P(D \mid \theta)P(\theta)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `theta` | probability vector |
| `alpha` | Dirichlet concentration |
| `D` | observed data |
| `posterior mean` | (alpha_k+n_k)/(A_0+N) |

## 5. Statistical assumptions

- Outcomes are conditionally independent given theta
- The prior is Dirichlet with known concentration

## 6. Required input data

Sufficient data to make the posterior interval narrower than the prior.

## 7. Step-by-step manual calculation

1. Choose a prior concentration
2. Add observed counts to the prior parameters
3. Report posterior means and 95% credible intervals per category

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

With prior alpha=1.0: posterior mean for outcome 3 is (4+1.0)/(10+10.0) = 0.3000, and for an unseen outcome it is 1.0/(10+10.0) = 0.0500. Shrinkage toward uniform is total prior mass divided by total mass: 10.0/(10+10.0) = 0.500.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `posterior_max_prob` | 0.11221 | n/a | n/a | n/a | n/a | 4143.0 |
| `mean_credible_width` | 0.01823 | n/a | n/a | n/a | n/a | 4143.0 |
| `prior_shrinkage_weight` | 0.00241 | n/a | n/a | n/a | n/a | 4143.0 |
| `uniform_in_all_ci` | 0.90000 | n/a | n/a | n/a | n/a | 10.0 |

**Interpretation.** With a Dirichlet(1.0) prior the posterior is Dirichlet([388, 465, 444, 397, 437, 408, 402, 393, 421, 388] + 1.0) and the prior retains a weight of 0.2408% of the posterior. The 95% credible intervals average 0.0182 in width, and the uniform value 0.10 lies inside 90% of them. Intervals that all contain 0.10 mean the data are consistent with a fair process at this sample size.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `posterior_max_prob` | 0.10860 | n/a | n/a | n/a | n/a | 4143.0 |
| `mean_credible_width` | 0.01824 | n/a | n/a | n/a | n/a | 4143.0 |
| `prior_shrinkage_weight` | 0.00241 | n/a | n/a | n/a | n/a | 4143.0 |
| `uniform_in_all_ci` | 0.90000 | n/a | n/a | n/a | n/a | 10.0 |

**Interpretation.** With a Dirichlet(1.0) prior the posterior is Dirichlet([420, 376, 406, 430, 402, 432, 423, 405, 399, 450] + 1.0) and the prior retains a weight of 0.2408% of the posterior. The 95% credible intervals average 0.0182 in width, and the uniform value 0.10 lies inside 90% of them. Intervals that all contain 0.10 mean the data are consistent with a fair process at this sample size.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `posterior_max_prob` | 0.10860 |
| Close | computed | `posterior_max_prob` | 0.11221 |

Open produced posterior_max_prob=0.10860; Close produced posterior_max_prob=0.11221. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The prior is a modelling choice. With weak priors the result converges to M002; with strong priors it can mask real imbalance.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
