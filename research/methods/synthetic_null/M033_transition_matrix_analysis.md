# M033 - Transition Matrix Analysis

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_033`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{P}_{ij} = \frac{n_{ij}+\alpha}{\sum_j (n_{ij}+\alpha)}`

---

## 1. Definition and mathematical foundation

The transition matrix is a complete description of a first-order chain, so its structural properties are diagnostic: the stationary distribution tells where the chain settles, the second eigenvalue governs the rate of mixing, and a near-uniform matrix indicates no dependence at all.

## 2. Objective

Characterise the transition structure and its predictive content.

## 3. Complete formula

```
\hat{P}_{ij} = \frac{n_{ij}+\alpha}{\sum_j (n_{ij}+\alpha)}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `P` | transition matrix |
| `stationary distribution` | left eigenvector for eigenvalue 1 |
| `mixing time` | governed by the second eigenvalue modulus |

## 5. Statistical assumptions

- The chain is homogeneous
- The matrix is estimated from adequate counts

## 6. Required input data

Sufficient counts per row.

## 7. Step-by-step manual calculation

1. Estimate the matrix
2. Compute the stationary distribution and spectral gap
3. Compare selective rows against the marginal distribution

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Consecutive pairs: [(np.int64(3), np.int64(1)), (np.int64(1), np.int64(3)), (np.int64(3), np.int64(7)), (np.int64(7), np.int64(0)), (np.int64(0), np.int64(3)), (np.int64(3), np.int64(9)), (np.int64(9), np.int64(3)), (np.int64(3), np.int64(2)), (np.int64(2), np.int64(3))]. Transitions out of state 3 are [np.int64(1), np.int64(7), np.int64(9), np.int64(2)] (to 1, 7, 9, 2 - one each). Row-normalised without smoothing, P(·|3) puts 0.25 on each of 1, 7, 9, 2 and 0 on the rest; with Laplace smoothing alpha=1 each of the ten cells becomes 1.4/14 = 0.1 except the four observed ones at 2.4/14 = 0.171.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `spectral_gap` | 0.95176 | n/a | n/a | n/a | n/a | 3131.0 |
| `second_eigenvalue_modulus` | 0.04824 | n/a | n/a | n/a | n/a | 3131.0 |
| `max_row_specificity` | 0.04416 | n/a | n/a | n/a | n/a | 3131.0 |
| `stationary_vs_marginal_tv_distance` | 0.00050 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** The estimated transition matrix has second-largest eigenvalue modulus 0.0482, giving a spectral gap of 0.9518. A gap near 0 means the chain mixes almost instantly, i.e. rows are nearly identical and the current state carries almost no information. The largest deviation of any row from the marginal distribution is 0.0442, and the total-variation distance between the stationary distribution and the observed marginal is 0.0005. The matrix is meaningfully structured and the current state does inform the next.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `spectral_gap` | 0.93428 | n/a | n/a | n/a | n/a | 3131.0 |
| `second_eigenvalue_modulus` | 0.06572 | n/a | n/a | n/a | n/a | 3131.0 |
| `max_row_specificity` | 0.05239 | n/a | n/a | n/a | n/a | 3131.0 |
| `stationary_vs_marginal_tv_distance` | 0.00043 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** The estimated transition matrix has second-largest eigenvalue modulus 0.0657, giving a spectral gap of 0.9343. A gap near 0 means the chain mixes almost instantly, i.e. rows are nearly identical and the current state carries almost no information. The largest deviation of any row from the marginal distribution is 0.0524, and the total-variation distance between the stationary distribution and the observed marginal is 0.0004. The matrix is meaningfully structured and the current state does inform the next.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `spectral_gap` | 0.93428 |
| Close | computed | `spectral_gap` | 0.95176 |

Open produced spectral_gap=0.93428; Close produced spectral_gap=0.95176. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

The most transferable category across markets, since it needs only a sequence. Data hunger grows sharply with order (K^order contexts).

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Transition-based methods are scored by walk-forward log loss against the expanding frequency baseline, which is the only comparison that answers 'does history help'.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

A non-uniform matrix may reflect sampling noise; the chi-square test in M023 and the out-of-sample comparison are what decide usability.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
