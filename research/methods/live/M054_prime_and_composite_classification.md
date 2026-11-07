# M054 - Prime and Composite Classification

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_054`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\mathbb{P} = \{2,3,5,7\},\quad n \in \mathbb{P}?`

---

## 1. Definition and mathematical foundation

On the digit space 0-9 the primes are 2, 3, 5 and 7, giving a natural 4/6 partition. The test is a straightforward binomial comparison, useful as a second coarse partition alongside parity and mod-5 residues.

## 2. Objective

Test whether prime-class outcomes occur at their theoretical rate.

## 3. Complete formula

```
\mathbb{P} = \{2,3,5,7\},\quad n \in \mathbb{P}?
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `pi` | theoretical prime share (0.4 on 0-9) |
| `n_prime` | observed prime count |

## 5. Statistical assumptions

- Primality is well defined on integers
- The partition is fixed a priori

## 6. Required input data

Any non-empty sample.

## 7. Step-by-step manual calculation

1. Classify each outcome
2. Compute the observed prime share
3. Test against 0.4 with an exact binomial test

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Even values in the toy sequence: 2 of 10 (0, 2 are even; 3, 1, 7, 9, 3, 3, 3 are odd). Primes among the observed values: 3, 3, 7, 3, 3, 2, 3 - seven of ten, which is unremarkable on ten draws but illustrates how coarse a partition this is.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `prime_share` | 0.39633 | n/a | 0.63432 | 0.86683 | n/a | 4143.0 |
| `n_prime_outcomes` | 1642.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `composite_share` | 0.60367 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** Prime outcomes (2, 3, 5, 7) account for 0.3963 of draws against the theoretical 0.40 (exact binomial p = 0.6343). Note that 0 and 1 are neither prime nor composite; the implementation counts them as non-prime, which is the convention stated in the method record. The prime share matches the theoretical value.

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
| `prime_share` | 0.40381 | n/a | 0.62304 | 0.81094 | n/a | 4143.0 |
| `n_prime_outcomes` | 1673.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `composite_share` | 0.59619 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** Prime outcomes (2, 3, 5, 7) account for 0.4038 of draws against the theoretical 0.40 (exact binomial p = 0.6230). Note that 0 and 1 are neither prime nor composite; the implementation counts them as non-prime, which is the convention stated in the method record. The prime share matches the theoretical value.

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
| Open | computed | `prime_share` | 0.40381 |
| Close | computed | `prime_share` | 0.39633 |

Open produced prime_share=0.40381; Close produced prime_share=0.39633. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

0 and 1 are neither prime nor composite, which matters when the outcome space includes them; the implementation states the convention used.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
