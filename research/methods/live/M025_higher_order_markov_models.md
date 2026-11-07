# M025 - Higher-Order Markov Models

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_025`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(X_{t+1}\mid X_{t-p+1},\ldots,X_t),\quad p=1,2,3`

---

## 1. Definition and mathematical foundation

Varying the Markov order traces the bias-variance trade-off explicitly. A useful summary is the conditional mutual information at each order: if conditioning on one more past state adds no information, the higher order is not earning its parameter count.

## 2. Objective

Select the Markov order by out-of-sample performance, not by in-sample fit.

## 3. Complete formula

```
P(X_{t+1}\mid X_{t-p+1},\ldots,X_t),\quad p=1,2,3
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `p` | Markov order |
| `order selection` | chosen by out-of-sample log loss |

## 5. Statistical assumptions

- Orders are nested
- The evaluation window is identical across orders

## 6. Required input data

N decreasing sharply in usefulness beyond p=2.

## 7. Step-by-step manual calculation

1. Fit orders 1 through the configured maximum
2. Score each on the same causal evaluation window
3. Report the loss curve and the selected order

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Two-state contexts from the toy sequence include (3,1), (1,3), (3,7), (7,0), (0,3), (3,9), (9,3), (3,2), (2,3). Every context occurs once, so each context has one transition: there are 100 possible contexts and 9 observations, which shows why second-order estimation needs thousands of draws.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ll_order1` | 2.32473 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_order2` | 2.48124 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_order3` | 2.32667 | n/a | n/a | n/a | n/a | 3315.0 |
| `selected_order` | 1.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `conditional_mi_order1_given_0` | 0.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `conditional_mi_order2_given_1` | 0.13253 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** Out-of-sample log loss by Markov order: order 1: 2.32473, order 2: 2.48124, order 3: 2.32667. The selected order is 1. Conditional mutual information added by each extra step: order-1 given nothing 0.00000 bits, order-2 given order-1 0.13253 bits. Additional history contributes almost no information, which is why the simplest chain is selected.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ll_order1` | 2.32577 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_order2` | 2.46592 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_order3` | 2.33040 | n/a | n/a | n/a | n/a | 3315.0 |
| `selected_order` | 1.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `conditional_mi_order1_given_0` | 2.908e-17 | n/a | n/a | n/a | n/a | 4143.0 |
| `conditional_mi_order2_given_1` | 0.15212 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** Out-of-sample log loss by Markov order: order 1: 2.32577, order 2: 2.46592, order 3: 2.33040. The selected order is 1. Conditional mutual information added by each extra step: order-1 given nothing 0.00000 bits, order-2 given order-1 0.15212 bits. Additional history contributes almost no information, which is why the simplest chain is selected.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `ll_order1` | 2.32577 |
| Close | computed | `ll_order1` | 2.32473 |

Open produced ll_order1=2.32577; Close produced ll_order1=2.32473. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

The most transferable category across markets, since it needs only a sequence. Data hunger grows sharply with order (K^order contexts).

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Transition-based methods are scored by walk-forward log loss against the expanding frequency baseline, which is the only comparison that answers 'does history help'.

## 13. Statistical interpretation

12 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

In-sample likelihood always increases with order; only the out-of-sample comparison is informative.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
