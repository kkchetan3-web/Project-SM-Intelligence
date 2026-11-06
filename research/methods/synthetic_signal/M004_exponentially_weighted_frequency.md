# M004 - Exponentially Weighted Frequency

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_004`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `w_k(t)=\sum_{i \le t}\lambda^{t-i}\mathbf{1}[X_i=k],\quad \hat{p}_k(t)=\frac{w_k(t)}{\sum_j w_j(t)}`

---

## 1. Definition and mathematical foundation

Exponential weighting generalises the hard window of M003 to a soft one: every past observation contributes, with weight decaying geometrically at rate lambda. The effective sample size is (1+lambda)/(1-lambda), so lambda=0.95 behaves like a window of about 39 draws and lambda=0.99 like about 199.

## 2. Objective

Test whether smooth recency weighting improves forecasts over a fixed window.

## 3. Complete formula

```
w_k(t)=\sum_{i \le t}\lambda^{t-i}\mathbf{1}[X_i=k],\quad \hat{p}_k(t)=\frac{w_k(t)}{\sum_j w_j(t)}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `lambda` | per-step decay factor in (0,1) |
| `w_k` | accumulated weight for outcome k |
| `effective N` | (1+lambda)/(1-lambda) |

## 5. Statistical assumptions

- The decay rate is constant over the evaluation window
- Recent draws are more informative than distant draws

## 6. Required input data

N >= 10/(1-lambda) for the effective sample to exceed the outcome space.

## 7. Step-by-step manual calculation

1. Set the weight vector to zero
2. At each step multiply all weights by lambda and add one to the observed outcome
3. Normalise to a probability vector and score causally

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

No worked example is defined for this category.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ewm_ll_lambda0.9` | 2.65378 | n/a | n/a | n/a | n/a | 3131.0 |
| `ewm_ll_lambda0.95` | 2.43969 | n/a | n/a | n/a | n/a | 3131.0 |
| `ewm_ll_lambda0.98` | 2.34604 | n/a | n/a | n/a | n/a | 3131.0 |
| `ewm_ll_lambda0.99` | 2.32043 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_lambda` | 0.99000 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_ewm_ll` | 2.32043 | n/a | n/a | n/a | n/a | 3131.0 |
| `expanding_ll` | 2.30041 | n/a | n/a | n/a | n/a | 3131.0 |
| `effective_sample_size` | 199.00000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Out-of-sample log loss by decay: lambda=0.9: 2.65378, lambda=0.95: 2.43969, lambda=0.98: 2.34604, lambda=0.99: 2.32043. Best lambda=0.99 (effective memory about 199 draws) scoring 2.32043 against 2.30041 for the expanding average. Exponential weighting does not beat the flat average, i.e. recent draws are not more informative than the long run.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 8,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ewm_ll_lambda0.9` | 2.66863 | n/a | n/a | n/a | n/a | 3131.0 |
| `ewm_ll_lambda0.95` | 2.44704 | n/a | n/a | n/a | n/a | 3131.0 |
| `ewm_ll_lambda0.98` | 2.34924 | n/a | n/a | n/a | n/a | 3131.0 |
| `ewm_ll_lambda0.99` | 2.32277 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_lambda` | 0.99000 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_ewm_ll` | 2.32277 | n/a | n/a | n/a | n/a | 3131.0 |
| `expanding_ll` | 2.30219 | n/a | n/a | n/a | n/a | 3131.0 |
| `effective_sample_size` | 199.00000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Out-of-sample log loss by decay: lambda=0.9: 2.66863, lambda=0.95: 2.44704, lambda=0.98: 2.34924, lambda=0.99: 2.32277. Best lambda=0.99 (effective memory about 199 draws) scoring 2.32277 against 2.30219 for the expanding average. Exponential weighting does not beat the flat average, i.e. recent draws are not more informative than the long run.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 8,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `ewm_ll_lambda0.9` | 2.66863 |
| Close | computed | `ewm_ll_lambda0.9` | 2.65378 |

Open produced ewm_ll_lambda0.9=2.66863; Close produced ewm_ll_lambda0.9=2.65378. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

16 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Lambda is a tuning parameter; optimising it on the same data used for scoring inflates apparent performance, so the grid is scored strictly out of sample.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
