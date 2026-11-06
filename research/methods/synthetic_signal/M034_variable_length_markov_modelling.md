# M034 - Variable-Length Markov Modelling

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_034`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{P}(x_{t+1}\mid \text{ctx}) = \begin{cases}\text{order 3} & n_{\text{ctx}} \ge \tau_3\\ \text{order 2} & n_{\text{ctx}} \ge \tau_2\\ \text{order 1} & \text{otherwise}\end{cases}`

---

## 1. Definition and mathematical foundation

A variable-length Markov model uses a long context where the data are dense enough and falls back to a shorter one where they are not. The support thresholds make the choice of order data-dependent rather than global, which controls context-tree growth and lets the method test whether selective long contexts help.

## 2. Objective

Test whether a data-driven context length beats a fixed-order Markov model.

## 3. Complete formula

```
\hat{P}(x_{t+1}\mid \text{ctx}) = \begin{cases}\text{order 3} & n_{\text{ctx}} \ge \tau_3\\ \text{order 2} & n_{\text{ctx}} \ge \tau_2\\ \text{order 1} & \text{otherwise}\end{cases}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `ctx` | the recent outcome sequence |
| `tau` | minimum support to use a context |

## 5. Statistical assumptions

- Contexts can be ranked by support
- Backoff preserves calibration

## 6. Required input data

Large N: the tree grows exponentially in the order.

## 7. Step-by-step manual calculation

1. Build the context tree to the maximum order
2. Apply support thresholds with backoff to shorter contexts
3. Score causally against the fixed-order models

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Two-state contexts from the toy sequence include (3,1), (1,3), (3,7), (7,0), (0,3), (3,9), (9,3), (3,2), (2,3). Every context occurs once, so each context has one transition: there are 100 possible contexts and 9 observations, which shows why second-order estimation needs thousands of draws.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ll_fixed_order_2` | 2.29988 | n/a | n/a | n/a | n/a | 2349.0 |
| `ll_fixed_order_3` | 2.31593 | n/a | n/a | n/a | n/a | 2349.0 |
| `ll_variable_length` | 2.22338 | n/a | n/a | n/a | n/a | 2349.0 |
| `best_approach` | n/a | n/a | n/a | n/a | n/a | 2349.0 |
| `vlmc_vs_fixed_order2` | 0.07650 | n/a | n/a | n/a | n/a | 2349.0 |

**Interpretation.** Out-of-sample log loss: fixed_order_2 2.29988, fixed_order_3 2.31593, variable_length 2.22338. Best approach: variable_length. Variable-length modelling gains +0.07650 nats over a fixed order-2 chain. Backoff by support avoids spending parameters on contexts seen a handful of times, but it cannot manufacture information that is not there.

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
| `ll_fixed_order_2` | 2.22838 | n/a | n/a | n/a | n/a | 2349.0 |
| `ll_fixed_order_3` | 2.29725 | n/a | n/a | n/a | n/a | 2349.0 |
| `ll_variable_length` | 2.14310 | n/a | n/a | n/a | n/a | 2349.0 |
| `best_approach` | n/a | n/a | n/a | n/a | n/a | 2349.0 |
| `vlmc_vs_fixed_order2` | 0.08528 | n/a | n/a | n/a | n/a | 2349.0 |

**Interpretation.** Out-of-sample log loss: fixed_order_2 2.22838, fixed_order_3 2.29725, variable_length 2.14310. Best approach: variable_length. Variable-length modelling gains +0.08528 nats over a fixed order-2 chain. Backoff by support avoids spending parameters on contexts seen a handful of times, but it cannot manufacture information that is not there.

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
| Open | computed | `ll_fixed_order_2` | 2.22838 |
| Close | computed | `ll_fixed_order_2` | 2.29988 |

Open produced ll_fixed_order_2=2.22838; Close produced ll_fixed_order_2=2.29988. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

The most transferable category across markets, since it needs only a sequence. Data hunger grows sharply with order (K^order contexts).

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Transition-based methods are scored by walk-forward log loss against the expanding frequency baseline, which is the only comparison that answers 'does history help'.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Backoff introduces discontinuities; a context just above threshold is estimated from a handful of cases.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
