# M021 - Rolling Recency Weighting

**Category:** B - Recency and Occurrence  
**Implementation:** `src.mathematics.recurrence::run_021`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{p}_k(t; W, \lambda)=\frac{\sum_{i=t-W+1}^{t}\lambda^{t-i}\mathbf{1}[X_i=k]}{\sum_j(\cdot)}`

---

## 1. Definition and mathematical foundation

Combining a hard window with exponential decay inside the window gives two independent controls: how far back to look, and how sharply to discount within that horizon. The pair is selected on out-of-sample loss, because fitting it in-sample guarantees a spurious optimum.

## 2. Objective

Tune window length and decay jointly under strict out-of-sample evaluation.

## 3. Complete formula

```
\hat{p}_k(t; W, \lambda)=\frac{\sum_{i=t-W+1}^{t}\lambda^{t-i}\mathbf{1}[X_i=k]}{\sum_j(\cdot)}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `W` | window length |
| `lambda` | within-window decay |
| `grid` | candidate (W, lambda) pairs |

## 5. Statistical assumptions

- Both hyperparameters are constant over the evaluation
- Selection uses only pre-cutoff data

## 6. Required input data

N large enough that every grid point has a meaningful evaluation window.

## 7. Step-by-step manual calculation

1. Enumerate the hyperparameter grid
2. Produce causal predictions for each
3. Select by out-of-sample log loss and report the full grid

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Standardised count for outcome 3: z = (4 - 1)/sqrt(10 x 0.1 x 0.9) = 3/0.9487 = 3.162. On ten draws a z of 3 is entirely ordinary; the persistence test needs two long periods, not ten draws.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ll_W25_L0.9` | 4.37602 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W25_L0.95` | 4.28819 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W25_L0.98` | 4.26656 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W50_L0.9` | 2.78439 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W50_L0.95` | 2.60856 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W50_L0.98` | 2.55895 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W100_L0.9` | 2.66083 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W100_L0.95` | 2.44854 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W100_L0.98` | 2.37171 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W250_L0.9` | 2.66073 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W250_L0.95` | 2.44601 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W250_L0.98` | 2.35558 | n/a | n/a | n/a | n/a | 3315.0 |
| `best_configuration` | n/a | n/a | n/a | n/a | n/a | 3315.0 |
| `best_ll` | 2.35558 | n/a | n/a | n/a | n/a | 3315.0 |
| `grid_spread` | 2.02044 | n/a | n/a | n/a | n/a | 3315.0 |

**Interpretation.** Joint grid over window length and within-window decay (12 points), scored out of sample on 3315 predictions. Best configuration: W250_L0.98 at 2.35558. The whole grid spans only 2.02044 nats. A spread this small means the two-parameter tuning buys essentially nothing: choosing optimally here is indistinguishable from choosing arbitrarily, and the winner is selected on the same data that scores it, so even this apparent edge is optimistic.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 15,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ll_W25_L0.9` | 4.22808 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W25_L0.95` | 4.13635 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W25_L0.98` | 4.11138 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W50_L0.9` | 2.81765 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W50_L0.95` | 2.65154 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W50_L0.98` | 2.60881 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W100_L0.9` | 2.64473 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W100_L0.95` | 2.43485 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W100_L0.98` | 2.36691 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W250_L0.9` | 2.64436 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W250_L0.95` | 2.43146 | n/a | n/a | n/a | n/a | 3315.0 |
| `ll_W250_L0.98` | 2.34825 | n/a | n/a | n/a | n/a | 3315.0 |
| `best_configuration` | n/a | n/a | n/a | n/a | n/a | 3315.0 |
| `best_ll` | 2.34825 | n/a | n/a | n/a | n/a | 3315.0 |
| `grid_spread` | 1.87983 | n/a | n/a | n/a | n/a | 3315.0 |

**Interpretation.** Joint grid over window length and within-window decay (12 points), scored out of sample on 3315 predictions. Best configuration: W250_L0.98 at 2.34825. The whole grid spans only 1.87983 nats. A spread this small means the two-parameter tuning buys essentially nothing: choosing optimally here is indistinguishable from choosing arbitrarily, and the winner is selected on the same data that scores it, so even this apparent edge is optimistic.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 15,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `ll_W25_L0.9` | 4.22808 |
| Close | computed | `ll_W25_L0.9` | 4.37602 |

Open produced ll_W25_L0.9=4.22808; Close produced ll_W25_L0.9=4.37602. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Suited to markets with long continuous histories; it degrades when the calendar has many gaps, because 'missing' and 'not drawn' become hard to separate.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Predictive claims are limited to what a causal forecast can show: hot/cold persistence is measured between two disjoint periods, and hazard/recency tests compare against a permutation or geometric null.

## 13. Statistical interpretation

30 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Grid search over two parameters on a few thousand observations invites selection bias; the reported loss is the selected one and is therefore optimistic.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
