# M031 - Mutual Information

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_031`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `I(X;Y)=\sum_{x,y}p(x,y)\log\frac{p(x,y)}{p(x)p(y)}`

---

## 1. Definition and mathematical foundation

Mutual information measures any statistical dependence, linear or not, in bits. Unlike correlation it detects the cyclic, modular relationships that digit games are full of. Its finite-sample bias is upward and must be corrected by comparison with a permutation null rather than against a theoretical chi-square.

## 2. Objective

Detect and quantify arbitrary dependence between consecutive draws.

## 3. Complete formula

```
I(X;Y)=\sum_{x,y}p(x,y)\log\frac{p(x,y)}{p(x)p(y)}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `I(X;Y)` | mutual information in bits |
| `p(x,y)` | joint probability |
| `null` | permutation distribution of I |

## 5. Statistical assumptions

- The joint distribution is estimable from the sample
- The permutation null preserves the marginals

## 6. Required input data

N >> K^2 for the joint table to be estimable.

## 7. Step-by-step manual calculation

1. Estimate joint and marginal probabilities with smoothing
2. Compute I
3. Compare against the distribution of I under random pairing

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

MI between consecutive draws: 1.3921 bits. The permutation null mean for a table this sparse is roughly 0.05-0.10 bits, so the observed value is indistinguishable from noise - illustrating why the permutation reference is mandatory for MI on 10x10 tables.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mutual_information_bits` | 0.01082 | n/a | 0.93600 | 1.00000 | n/a | 4142.0 |
| `normalised_mi` | 0.00326 | n/a | n/a | n/a | n/a | 4142.0 |
| `permutation_null_mean` | 0.01409 | n/a | n/a | n/a | n/a | 999.0 |
| `permutation_null_95pct` | 0.01882 | n/a | n/a | n/a | n/a | 999.0 |
| `excess_over_null` | -0.00327 | n/a | 0.93600 | 1.00000 | n/a | 4142.0 |

**Interpretation.** Mutual information between consecutive draws is 0.01082 bits, i.e. 0.3259% of the marginal entropy. Random pairing of the same outcome sequence produces 0.01409 bits on average (95th percentile 0.01882), because MI is upward-biased in finite samples. The excess over the permutation null is -0.00327 bits with p = 0.936. After correcting for finite-sample bias there is no detectable dependence between successive draws.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mutual_information_bits` | 0.01169 | n/a | 0.89000 | 0.94779 | n/a | 4142.0 |
| `normalised_mi` | 0.00352 | n/a | n/a | n/a | n/a | 4142.0 |
| `permutation_null_mean` | 0.01414 | n/a | n/a | n/a | n/a | 999.0 |
| `permutation_null_95pct` | 0.01903 | n/a | n/a | n/a | n/a | 999.0 |
| `excess_over_null` | -0.00245 | n/a | 0.89000 | 0.94779 | n/a | 4142.0 |

**Interpretation.** Mutual information between consecutive draws is 0.01169 bits, i.e. 0.3521% of the marginal entropy. Random pairing of the same outcome sequence produces 0.01414 bits on average (95th percentile 0.01903), because MI is upward-biased in finite samples. The excess over the permutation null is -0.00245 bits with p = 0.890. After correcting for finite-sample bias there is no detectable dependence between successive draws.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `mutual_information_bits` | 0.01169 |
| Close | computed | `mutual_information_bits` | 0.01082 |

Open produced mutual_information_bits=0.01169; Close produced mutual_information_bits=0.01082. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

The most transferable category across markets, since it needs only a sequence. Data hunger grows sharply with order (K^order contexts).

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Transition-based methods are scored by walk-forward log loss against the expanding frequency baseline, which is the only comparison that answers 'does history help'.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

MI is biased upward for sparse tables; the permutation comparison is the remedy, not an afterthought.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Shannon (1948)
