# M070 - Bayesian Change-Point Modelling

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_070`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(\tau \mid x_{1:T}) \propto P(x_{1:\tau})P(x_{\tau+1:T})P(\tau)`

---

## 1. Definition and mathematical foundation

A Bayesian change-point model places a prior over the location of a structural break and returns a posterior distribution over break positions rather than a single point. That honesty about location uncertainty is the main advantage over CUSUM.

## 2. Objective

Estimate the posterior distribution of change-point locations.

## 3. Complete formula

```
P(\tau \mid x_{1:T}) \propto P(x_{1:\tau})P(x_{\tau+1:T})P(\tau)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `tau` | change-point index |
| `prior` | geometric or uniform over locations |

## 5. Statistical assumptions

- Segments are independent given the break location
- A conjugate prior is available

## 6. Required input data

Several hundred observations.

## 7. Step-by-step manual calculation

1. Score every candidate break by the marginal likelihood of the two segments
2. Combine with the prior
3. Normalise to a posterior and report the credible set

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Entropy, Hurst and latent-state estimators are all severely biased below ~100 observations, so no honest worked example exists at n=10. The method record states the minimum sample size; the computed section reports the real estimate with its simulated reference band, which is the only defensible way to read it.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `posterior_modal_break_index` | 1771.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `posterior_credible_low` | 903.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `posterior_credible_high` | 2422.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `log_bayes_factor_two_segments` | -9.19154 | n/a | n/a | n/a | n/a | 3131.0 |
| `max_posterior_mass` | 0.36571 | n/a | n/a | n/a | n/a | 71.0 |

**Interpretation.** A grid posterior over 71 candidate break positions places its mode at index 1771 (2021-08-28), with a 95% credible interval spanning 2018-11-20 to 2023-09-27. The log Bayes factor for a two-segment model against no break is -9.19 (no meaningful evidence for a break; the usual threshold is about 3). The posterior mode carries only 0.366 of the mass, so even the best candidate is barely preferred over its neighbours - which is what a flat posterior over noise looks like.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `posterior_modal_break_index` | 655.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `posterior_credible_low` | 469.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `posterior_credible_high` | 810.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `log_bayes_factor_two_segments` | -10.06443 | n/a | n/a | n/a | n/a | 3131.0 |
| `max_posterior_mass` | 0.30435 | n/a | n/a | n/a | n/a | 71.0 |

**Interpretation.** A grid posterior over 71 candidate break positions places its mode at index 655 (2018-02-03), with a 95% credible interval spanning 2017-07-01 to 2018-08-03. The log Bayes factor for a two-segment model against no break is -10.06 (no meaningful evidence for a break; the usual threshold is about 3). The posterior mode carries only 0.304 of the mass, so even the best candidate is barely preferred over its neighbours - which is what a flat posterior over noise looks like.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `posterior_modal_break_index` | 655.00000 |
| Close | computed | `posterior_modal_break_index` | 1771.00000 |

Open produced posterior_modal_break_index=655.00000; Close produced posterior_modal_break_index=1771.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Exact posterior computation over T candidate positions is quadratic in T; the implementation uses a coarse grid and says so.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
