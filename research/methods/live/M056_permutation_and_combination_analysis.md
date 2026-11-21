# M056 - Permutation and Combination Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_056`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `{}^nP_r=\frac{n!}{(n-r)!},\qquad {}^nC_r=\frac{n!}{r!(n-r)!}`

---

## 1. Definition and mathematical foundation

Ordered arrangements and unordered selections generate different counts, which matters when the panel orientation is or is not treated as meaningful. Repeated digits reduce the count of distinct permutations, so the multinomial coefficient is the correct tool.

## 2. Objective

Enumerate arrangement counts and test orientation-sensitive distributions.

## 3. Complete formula

```
{}^nP_r=\frac{n!}{(n-r)!},\qquad {}^nC_r=\frac{n!}{r!(n-r)!}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `nPr` | ordered arrangements |
| `nCr` | unordered selections |
| `multinomial` | n!/(n1!n2!n3!) |

## 5. Statistical assumptions

- Permutations count order, combinations do not
- Repeated digits are handled by the multinomial coefficient

## 6. Required input data

Panels available.

## 7. Step-by-step manual calculation

1. Enumerate digit multisets
2. Compute the number of distinct arrangements of each
3. Compare the observed orientation frequencies with the weighted expectation

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

No worked example is defined for this category.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `ordered_space_size` | 1000.00000 | n/a | n/a | n/a | n/a | 4136.0 |
| `unordered_multiset_space_size` | 220.00000 | n/a | n/a | n/a | n/a | 4136.0 |
| `distinct_multisets_observed` | 214.00000 | n/a | n/a | n/a | n/a | 4136.0 |
| `multiset_coverage` | 0.97273 | n/a | n/a | n/a | n/a | 4136.0 |
| `triple_repeat_share` | 0.00097 | n/a | n/a | n/a | n/a | 4136.0 |
| `permutations_per_distinct_multiset` | 6.00000 | n/a | n/a | n/a | n/a | 4136.0 |

**Interpretation.** The ordered panel space has 1000 elements but only 220 unordered digit multisets, each of which can be arranged in up to 6 ways (fewer when digits repeat). The sample covers 214 of the 220 multisets (97.3%); the most common are 679 (38), 589 (38), 145 (36). Triple-repeated panels account for 0.097% against the 1.0% expected from independent uniform digits. This confirms that the ordered space is the correct one to model: treating panels as unordered would over-weight the small multiset space.

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
| `ordered_space_size` | 1000.00000 | n/a | n/a | n/a | n/a | 4134.0 |
| `unordered_multiset_space_size` | 220.00000 | n/a | n/a | n/a | n/a | 4134.0 |
| `distinct_multisets_observed` | 215.00000 | n/a | n/a | n/a | n/a | 4134.0 |
| `multiset_coverage` | 0.97727 | n/a | n/a | n/a | n/a | 4134.0 |
| `triple_repeat_share` | 0.00194 | n/a | n/a | n/a | n/a | 4134.0 |
| `permutations_per_distinct_multiset` | 6.00000 | n/a | n/a | n/a | n/a | 4134.0 |

**Interpretation.** The ordered panel space has 1000 elements but only 220 unordered digit multisets, each of which can be arranged in up to 6 ways (fewer when digits repeat). The sample covers 215 of the 220 multisets (97.7%); the most common are 368 (39), 569 (39), 578 (39). Triple-repeated panels account for 0.194% against the 1.0% expected from independent uniform digits. This confirms that the ordered space is the correct one to model: treating panels as unordered would over-weight the small multiset space.

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
| Open | computed | `ordered_space_size` | 1000.00000 |
| Close | computed | `ordered_space_size` | 1000.00000 |

Open produced ordered_space_size=1000.00000; Close produced ordered_space_size=1000.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

12 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Panel providers may rank panels non-uniformly by convention, so a departure from equiprobability may reflect operator ranking rather than draw physics.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
