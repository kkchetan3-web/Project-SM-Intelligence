# M026 - Conditional Probability Analysis

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_026`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(A \mid B) = \frac{P(A \cap B)}{P(B)}`

---

## 1. Definition and mathematical foundation

Conditional probability is the primitive that every dependence-based predictor ultimately rests on. Estimating P(next outcome | current outcome) reproduces the Markov matrix, but the general form also covers events rather than states - for example 'next draw is even given that the previous draw was prime'.

## 2. Objective

Build conditional frequency tables and test whether conditioning changes anything.

## 3. Complete formula

```
P(A \mid B) = \frac{P(A \cap B)}{P(B)}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `A` | target event |
| `B` | conditioning event |
| `P(B)` | marginal probability of the condition |

## 5. Statistical assumptions

- The conditioning event has non-trivial probability
- Event definitions are fixed before looking at the data

## 6. Required input data

Enough observations in the conditioning cell (say >= 50).

## 7. Step-by-step manual calculation

1. Define the events
2. Tabulate joint and marginal counts
3. Compute the conditional distribution and the lift over the unconditional one

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Consecutive pairs: [(np.int64(3), np.int64(1)), (np.int64(1), np.int64(3)), (np.int64(3), np.int64(7)), (np.int64(7), np.int64(0)), (np.int64(0), np.int64(3)), (np.int64(3), np.int64(9)), (np.int64(9), np.int64(3)), (np.int64(3), np.int64(2)), (np.int64(2), np.int64(3))]. Transitions out of state 3 are [np.int64(1), np.int64(7), np.int64(9), np.int64(2)] (to 1, 7, 9, 2 - one each). Row-normalised without smoothing, P(·|3) puts 0.25 on each of 1, 7, 9, 2 and 0 on the rest; with Laplace smoothing alpha=1 each of the ten cells becomes 1.4/14 = 0.1 except the four observed ones at 2.4/14 = 0.171.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `max_conditional_lift` | 1.38121 | n/a | n/a | n/a | n/a | 4142.0 |
| `min_conditional_lift` | 0.66404 | n/a | n/a | n/a | n/a | 4142.0 |
| `lift_range` | 0.71717 | n/a | n/a | n/a | n/a | 4142.0 |

**Interpretation.** The most extreme conditional lift is 1.381x: given 0 the probability of 6 is 1.381 times its unconditional value. The range of lift across well-populated cells is 0.717. With 4142 transitions across 100 cells, lifts of this magnitude are expected from noise alone; the formal test is in Method 23 and the usable test is its out-of-sample comparison.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `max_conditional_lift` | 1.48657 | n/a | n/a | n/a | n/a | 4142.0 |
| `min_conditional_lift` | 0.74299 | n/a | n/a | n/a | n/a | 4142.0 |
| `lift_range` | 0.74358 | n/a | n/a | n/a | n/a | 4142.0 |

**Interpretation.** The most extreme conditional lift is 1.487x: given 2 the probability of 2 is 1.487 times its unconditional value. The range of lift across well-populated cells is 0.744. With 4142 transitions across 100 cells, lifts of this magnitude are expected from noise alone; the formal test is in Method 23 and the usable test is its out-of-sample comparison.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `max_conditional_lift` | 1.48657 |
| Close | computed | `max_conditional_lift` | 1.38121 |

Open produced max_conditional_lift=1.48657; Close produced max_conditional_lift=1.38121. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

The most transferable category across markets, since it needs only a sequence. Data hunger grows sharply with order (K^order contexts).

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Transition-based methods are scored by walk-forward log loss against the expanding frequency baseline, which is the only comparison that answers 'does history help'.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Conditioning on rare events yields unstable estimates; and with many candidate events, apparent lift is easy to find by chance.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
