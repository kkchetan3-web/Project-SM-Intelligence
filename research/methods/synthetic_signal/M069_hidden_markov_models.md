# M069 - Hidden Markov Models

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_069`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(X_{1:T},Z_{1:T}) = \pi_{z_1}b_{z_1}(x_1)\prod_{t=2}^{T}A_{z_{t-1},z_t}b_{z_t}(x_t)`

---

## 1. Definition and mathematical foundation

An HMM posits that observed draws are emitted by an unobserved state that itself follows a Markov chain. It generalises the plain Markov model in M023 and can capture regime switching that a homogeneous chain cannot - at the cost of identifiability issues and local optima.

## 2. Objective

Fit latent-regime models and test their out-of-sample value.

## 3. Complete formula

```
P(X_{1:T},Z_{1:T}) = \pi_{z_1}b_{z_1}(x_1)\prod_{t=2}^{T}A_{z_{t-1},z_t}b_{z_t}(x_t)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `Z_t` | latent state |
| `A` | state transition matrix |
| `b` | emission distribution |
| `pi` | initial state distribution |

## 5. Statistical assumptions

- The latent state is discrete and small
- Emissions depend only on the current state

## 6. Required input data

Several hundred observations per state.

## 7. Step-by-step manual calculation

1. Fit models with increasing state counts
2. Initialise from multiple random starts to avoid local optima
3. Compare out-of-sample log loss against the plain Markov model

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Entropy, Hurst and latent-state estimators are all severely biased below ~100 observations, so no honest worked example exists at n=10. The method record states the minimum sample size; the computed section reports the real estimate with its simulated reference band, which is the only defensible way to read it.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `loglik_states2` | -7191.08240 | n/a | n/a | n/a | n/a | 3131.0 |
| `loglik_states3` | -7112.93070 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_n_states` | 3.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `aic_hmm` | 14295.86141 | n/a | n/a | n/a | n/a | 3131.0 |
| `aic_first_order_markov` | 13886.42557 | n/a | n/a | n/a | n/a | 3131.0 |
| `aic_advantage_of_hmm` | -409.43584 | n/a | n/a | n/a | n/a | 3131.0 |
| `markov1_out_of_sample_ll` | 2.18883 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Fitting categorical HMMs with [2, 3] latent states (three random restarts each, keeping the best log-likelihood): 2 states: ll=-7191.1, mean persistence 0.549, 3 states: ll=-7112.9, mean persistence 0.391. Best is 3 states. Against a first-order Markov chain the AIC advantage is -409.4 units (positive favours the HMM). The latent-state model does not explain the data better than a plain chain once its extra parameters are charged for, so there is no evidence of regime switching. The first-order chain's out-of-sample log loss is 2.18883, which is the benchmark any latent-state model must beat.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `loglik_states2` | -7185.14276 | n/a | n/a | n/a | n/a | 3131.0 |
| `loglik_states3` | -6982.29748 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_n_states` | 3.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `aic_hmm` | 14034.59495 | n/a | n/a | n/a | n/a | 3131.0 |
| `aic_first_order_markov` | 13337.33656 | n/a | n/a | n/a | n/a | 3131.0 |
| `aic_advantage_of_hmm` | -697.25839 | n/a | n/a | n/a | n/a | 3131.0 |
| `markov1_out_of_sample_ll` | 2.10114 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Fitting categorical HMMs with [2, 3] latent states (three random restarts each, keeping the best log-likelihood): 2 states: ll=-7185.1, mean persistence 0.577, 3 states: ll=-6982.3, mean persistence 0.210. Best is 3 states. Against a first-order Markov chain the AIC advantage is -697.3 units (positive favours the HMM). The latent-state model does not explain the data better than a plain chain once its extra parameters are charged for, so there is no evidence of regime switching. The first-order chain's out-of-sample log loss is 2.10114, which is the benchmark any latent-state model must beat.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `loglik_states2` | -7185.14276 |
| Close | computed | `loglik_states2` | -7191.08240 |

Open produced loglik_states2=-7185.14276; Close produced loglik_states2=-7191.08240. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

14 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

HMM fitting is non-convex; a good in-sample likelihood is weak evidence, and extra states nearly always improve it.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Baum & Petrie (1966)
