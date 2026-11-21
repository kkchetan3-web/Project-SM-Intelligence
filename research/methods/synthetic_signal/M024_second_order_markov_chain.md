# M024 - Second-Order Markov Chain

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_024`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(X_{t+1}=k \mid X_t=j, X_{t-1}=i) = P_{ijk}`

---

## 1. Definition and mathematical foundation

Conditioning on two previous states captures patterns a first-order chain cannot express, at the cost of K^2 = 100 contexts. Each context then holds only ~N/100 observations, so the estimates are severely data-limited and smoothing or pooling is mandatory.

## 2. Objective

Test whether two-step history adds predictive information.

## 3. Complete formula

```
P(X_{t+1}=k \mid X_t=j, X_{t-1}=i) = P_{ijk}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `P_ijk` | transition probability given two states |
| `context` | the pair (i, j) |
| `sparsity` | fraction of empty contexts |

## 5. Statistical assumptions

- The process is second-order Markov
- Contexts are adequately populated

## 6. Required input data

N >> K^2 for reliable estimation.

## 7. Step-by-step manual calculation

1. Tabulate transitions conditioned on the previous two outcomes
2. Smooth sparse rows toward the first-order estimate
3. Score causally against the first-order model

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Two-state contexts from the toy sequence include (3,1), (1,3), (3,7), (7,0), (0,3), (3,9), (9,3), (3,2), (2,3). Every context occurs once, so each context has one transition: there are 100 possible contexts and 9 observations, which shows why second-order estimation needs thousands of draws.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `order2_ll` | 2.29988 | n/a | n/a | n/a | n/a | 2505.0 |
| `order1_ll` | 2.18575 | n/a | n/a | n/a | n/a | 2505.0 |
| `ll_difference_order2_minus_order1` | 0.11413 | n/a | n/a | n/a | n/a | 2505.0 |
| `contexts_populated` | 100.00000 | n/a | n/a | n/a | n/a | 100.0 |
| `context_chi2_p` | 0.00249 | 2135.61611 | 0.00249 | 0.00748 | 0.27538 | 3131.0 |

**Interpretation.** Of the 100 possible two-state contexts, 100 hold at least ten transitions - the rest are too sparse to estimate. Out of sample the second-order chain scores 2.29988 versus 2.18575 for first order, a change of +0.11413 (negative means the extra history helps). Two-step history does not improve forecasts, and with ~31 observations per context that is a data-limited conclusion as much as a structural one.

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
| `order2_ll` | 2.22838 | n/a | n/a | n/a | n/a | 2505.0 |
| `order1_ll` | 2.10227 | n/a | n/a | n/a | n/a | 2505.0 |
| `ll_difference_order2_minus_order1` | 0.12611 | n/a | n/a | n/a | n/a | 2505.0 |
| `contexts_populated` | 100.00000 | n/a | n/a | n/a | n/a | 100.0 |
| `context_chi2_p` | 0.00249 | 3037.24129 | 0.00249 | 0.00705 | 0.32841 | 3131.0 |

**Interpretation.** Of the 100 possible two-state contexts, 100 hold at least ten transitions - the rest are too sparse to estimate. Out of sample the second-order chain scores 2.22838 versus 2.10227 for first order, a change of +0.12611 (negative means the extra history helps). Two-step history does not improve forecasts, and with ~31 observations per context that is a data-limited conclusion as much as a structural one.

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
| Open | computed | `order2_ll` | 2.22838 |
| Close | computed | `order2_ll` | 2.29988 |

Open produced order2_ll=2.22838; Close produced order2_ll=2.29988. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

The most transferable category across markets, since it needs only a sequence. Data hunger grows sharply with order (K^order contexts).

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Transition-based methods are scored by walk-forward log loss against the expanding frequency baseline, which is the only comparison that answers 'does history help'.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 2 survive Benjamini-Hochberg control at q=0.05 (close:context_chi2_p, open:context_chi2_p). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The parameter count grows as K^2(K-1) = 900, which for these sample sizes generally loses to the simpler model - a genuine bias-variance trade-off, measured rather than assumed.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
