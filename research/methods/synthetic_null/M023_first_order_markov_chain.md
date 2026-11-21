# M023 - First-Order Markov Chain

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_023`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(X_{t+1}=j \mid X_t=i, X_{t-1},\ldots) = P(X_{t+1}=j \mid X_t=i) = P_{ij}`

---

## 1. Definition and mathematical foundation

A first-order Markov chain is the minimal model of serial dependence: the next state depends on the current one and on nothing earlier. Its transition matrix P is estimated by row normalisation of the transition counts, and the Markov property itself is testable by comparing higher-order conditional distributions.

## 2. Objective

Estimate the transition matrix and test whether it beats the marginal distribution out of sample.

## 3. Complete formula

```
P(X_{t+1}=j \mid X_t=i, X_{t-1},\ldots) = P(X_{t+1}=j \mid X_t=i) = P_{ij}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `P_ij` | probability of moving from i to j |
| `n_ij` | transition count |
| `row sum` | total transitions out of state i |

## 5. Statistical assumptions

- The process is time-homogeneous
- The state space is the observed outcome space

## 6. Required input data

At least ~10 transitions out of every state.

## 7. Step-by-step manual calculation

1. Tabulate transitions between consecutive draws
2. Row-normalise with smoothing
3. Score causally and compare against the marginal-frequency baseline

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Consecutive pairs: [(np.int64(3), np.int64(1)), (np.int64(1), np.int64(3)), (np.int64(3), np.int64(7)), (np.int64(7), np.int64(0)), (np.int64(0), np.int64(3)), (np.int64(3), np.int64(9)), (np.int64(9), np.int64(3)), (np.int64(3), np.int64(2)), (np.int64(2), np.int64(3))]. Transitions out of state 3 are [np.int64(1), np.int64(7), np.int64(9), np.int64(2)] (to 1, 7, 9, 2 - one each). Row-normalised without smoothing, P(·|3) puts 0.25 on each of 1, 7, 9, 2 and 0 on the rest; with Laplace smoothing alpha=1 each of the ten cells becomes 1.4/14 = 0.1 except the four observed ones at 2.4/14 = 0.171.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `transition_chi2` | 72.53695 | 72.53695 | 0.73785 | 0.89825 | 0.05074 | 3131.0 |
| `cramers_v` | 0.05074 | n/a | n/a | n/a | n/a | 3131.0 |
| `markov_ll` | 2.33380 | n/a | n/a | n/a | n/a | 2662.0 |
| `frequency_ll` | 2.30569 | n/a | n/a | n/a | n/a | 2662.0 |
| `ll_improvement_over_frequency` | -0.02810 | n/a | 0.00000 | n/a | n/a | 2662.0 |
| `order2_ll` | 2.47332 | n/a | n/a | n/a | n/a | 2505.0 |

**Interpretation.** The transition table shows chi-square 72.54 against independence (p = 0.7378, Cramer's V = 0.0507). Out of sample the first-order chain scores 2.33380 against 2.30569 for plain frequency, a difference of -0.02810 (paired block-bootstrap p = 0.000). The chain is not better than plain frequency out of sample, so any transition structure in the table is not exploitable. A second-order chain scores 2.47332 (worse, so the extra history does not help).

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `transition_chi2` | 94.77708 | 94.77708 | 0.14047 | 0.83640 | 0.05800 | 3131.0 |
| `cramers_v` | 0.05800 | n/a | n/a | n/a | n/a | 3131.0 |
| `markov_ll` | 2.33087 | n/a | n/a | n/a | n/a | 2662.0 |
| `frequency_ll` | 2.30558 | n/a | n/a | n/a | n/a | 2662.0 |
| `ll_improvement_over_frequency` | -0.02529 | n/a | 0.00000 | n/a | n/a | 2662.0 |
| `order2_ll` | 2.46009 | n/a | n/a | n/a | n/a | 2505.0 |

**Interpretation.** The transition table shows chi-square 94.78 against independence (p = 0.1405, Cramer's V = 0.0580). Out of sample the first-order chain scores 2.33087 against 2.30558 for plain frequency, a difference of -0.02529 (paired block-bootstrap p = 0.000). The chain is not better than plain frequency out of sample, so any transition structure in the table is not exploitable. A second-order chain scores 2.46009 (worse, so the extra history does not help).

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `transition_chi2` | 94.77708 |
| Close | computed | `transition_chi2` | 72.53695 |

Open produced transition_chi2=94.77708; Close produced transition_chi2=72.53695. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

The most transferable category across markets, since it needs only a sequence. Data hunger grows sharply with order (K^order contexts).

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Transition-based methods are scored by walk-forward log loss against the expanding frequency baseline, which is the only comparison that answers 'does history help'.

## 13. Statistical interpretation

12 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

With K=10 each row has 10 cells; at N=3000 that is ~30 transitions per cell, enough for the diagonal but thin for distant off-diagonals.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
