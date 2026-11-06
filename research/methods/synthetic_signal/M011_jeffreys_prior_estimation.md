# M011 - Jeffreys Prior Estimation

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_011`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\theta \sim \mathrm{Dirichlet}(\tfrac{1}{2},\ldots,\tfrac{1}{2})`

---

## 1. Definition and mathematical foundation

The Jeffreys prior is the square root of the Fisher information determinant; it is the default objective prior because it is invariant to reparameterisation. For a categorical model it is Dirichlet(1/2), which is deliberately less smooth than Laplace's Dirichlet(1).

## 2. Objective

Compare an information-based prior with the flat and Laplace alternatives.

## 3. Complete formula

```
\theta \sim \mathrm{Dirichlet}(\tfrac{1}{2},\ldots,\tfrac{1}{2})
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `alpha=1/2` | Jeffreys concentration per category |
| `log loss` | scoring rule used to compare priors |

## 5. Statistical assumptions

- Jeffreys prior is the appropriate objective choice

## 6. Required input data

Any N; most relevant when categories are sparse.

## 7. Step-by-step manual calculation

1. Compute the posterior mean under alpha=1/2
2. Do the same under alpha=1
3. Compare their causal log loss on the same evaluation window

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

With prior alpha=0.5: posterior mean for outcome 3 is (4+0.5)/(10+5.0) = 0.3667, and for an unseen outcome it is 0.5/(10+5.0) = 0.0333. Shrinkage toward uniform is total prior mass divided by total mass: 5.0/(10+5.0) = 0.333.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `jeffreys_ll` | 2.30042 | n/a | n/a | n/a | n/a | 3131.0 |
| `laplace_ll` | 2.30041 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_difference` | 1.688e-05 | n/a | 0.04000 | n/a | n/a | 3131.0 |
| `max_posterior_mean_difference` | 2.746e-05 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Jeffreys (alpha=1/2) scores 2.30042 against Laplace (alpha=1) at 2.30041, a difference of +0.000017 (bootstrap p = 0.040). The two posterior means differ by at most 0.00003. With N=3131 the prior is drowned by the likelihood: the choice of objective prior is immaterial here, which is the expected result and a useful sanity check on the implementation.

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
| `jeffreys_ll` | 2.30224 | n/a | n/a | n/a | n/a | 3131.0 |
| `laplace_ll` | 2.30219 | n/a | n/a | n/a | n/a | 3131.0 |
| `ll_difference` | 4.910e-05 | n/a | 0.00400 | n/a | n/a | 3131.0 |
| `max_posterior_mean_difference` | 2.898e-05 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Jeffreys (alpha=1/2) scores 2.30224 against Laplace (alpha=1) at 2.30219, a difference of +0.000049 (bootstrap p = 0.004). The two posterior means differ by at most 0.00003. With N=3131 the prior is drowned by the likelihood: the choice of objective prior is immaterial here, which is the expected result and a useful sanity check on the implementation.

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
| Open | computed | `jeffreys_ll` | 2.30224 |
| Close | computed | `jeffreys_ll` | 2.30042 |

Open produced jeffreys_ll=2.30224; Close produced jeffreys_ll=2.30042. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The difference between priors vanishes as N grows; it matters only in short samples.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Jeffreys (1946)
