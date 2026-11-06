# M007 - Laplace Smoothing

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_007`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{p}_k = \frac{n_k+\alpha}{N+\alpha K}`

---

## 1. Definition and mathematical foundation

Additive smoothing prevents zero probabilities, which would make log loss infinite for an unseen outcome. It is a Bayes posterior mean under a symmetric Dirichlet prior, and its cost is a small bias toward uniform. The right alpha is the one that minimises out-of-sample log loss, not the one that looks neatest.

## 2. Objective

Quantify the log-loss effect of additive smoothing and choose alpha empirically.

## 3. Complete formula

```
\hat{p}_k = \frac{n_k+\alpha}{N+\alpha K}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `alpha` | pseudo-count per category |
| `K` | number of categories |
| `N` | observed count total |

## 5. Statistical assumptions

- The same alpha applies to every category
- The outcome space is complete and fixed

## 6. Required input data

Any N; most valuable when some categories are sparse or unseen.

## 7. Step-by-step manual calculation

1. For each alpha in a grid, produce causal probability vectors
2. Score each with log loss
3. Report the alpha that minimises out-of-sample loss

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

With prior alpha=1.0: posterior mean for outcome 3 is (4+1.0)/(10+10.0) = 0.3000, and for an unseen outcome it is 1.0/(10+10.0) = 0.0500. Shrinkage toward uniform is total prior mass divided by total mass: 10.0/(10+10.0) = 0.500.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ll_alpha_0.0` | 2.30044 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_alpha_0.1` | 2.30044 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_alpha_0.5` | 2.30042 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_alpha_1.0` | 2.30041 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_alpha_2.0` | 2.30037 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_alpha_5.0` | 2.30029 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_alpha` | 5.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_ll` | 2.30029 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_spread_across_alpha` | 0.00016 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Out-of-sample log loss by smoothing constant: alpha=0.0: 2.30044, alpha=0.1: 2.30044, alpha=0.5: 2.30042, alpha=1.0: 2.30041, alpha=2.0: 2.30037, alpha=5.0: 2.30029. Best alpha=5.0. The entire spread across the grid is 0.000155 nats per prediction, which bounds how much this choice can matter: smoothing is a guard against zero probabilities, not a source of predictive edge.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ll_alpha_0.0` | 2.30229 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_alpha_0.1` | 2.30228 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_alpha_0.5` | 2.30224 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_alpha_1.0` | 2.30219 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_alpha_2.0` | 2.30209 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_alpha_5.0` | 2.30183 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_alpha` | 5.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_ll` | 2.30183 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_spread_across_alpha` | 0.00045 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Out-of-sample log loss by smoothing constant: alpha=0.0: 2.30229, alpha=0.1: 2.30228, alpha=0.5: 2.30224, alpha=1.0: 2.30219, alpha=2.0: 2.30209, alpha=5.0: 2.30183. Best alpha=5.0. The entire spread across the grid is 0.000454 nats per prediction, which bounds how much this choice can matter: smoothing is a guard against zero probabilities, not a source of predictive edge.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `ll_alpha_0.0` | 2.30229 |
| Close | computed | `ll_alpha_0.0` | 2.30044 |

Open produced ll_alpha_0.0=2.30229; Close produced ll_alpha_0.0=2.30044. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Smoothing cannot create information; it only avoids pathological scores.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
