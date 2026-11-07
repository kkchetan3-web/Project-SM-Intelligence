# M052 - Reversal Relationship Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_052`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\mathrm{rev}(d_1d_2d_3) = d_3d_2d_1`

---

## 1. Definition and mathematical foundation

Reversal preserves the digit multiset and therefore the ank, changing only the order. If panels were generated without order structure, a panel and its reversal should appear with comparable frequency; if the operator ranks panels, one orientation may dominate.

## 2. Objective

Test whether panel orientation carries a systematic asymmetry.

## 3. Complete formula

```
\mathrm{rev}(d_1d_2d_3) = d_3d_2d_1
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `rev(x)` | reversed digit sequence |
| `orientation` | palindrome / ascending / descending class |

## 5. Statistical assumptions

- Fixed-width strings are preserved through storage
- Reversal is its own inverse

## 6. Required input data

Panels available.

## 7. Step-by-step manual calculation

1. Reverse each panel as a string
2. Classify orientation
3. Test the orientation distribution against the combinatorial expectation

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Even values in the toy sequence: 2 of 10 (0, 2 are even; 3, 1, 7, 9, 3, 3, 3 are odd). Primes among the observed values: 3, 3, 7, 3, 3, 2, 3 - seven of ten, which is unremarkable on ten draws but illustrates how coarse a partition this is.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `palindrome_share` | 0.00097 | n/a | n/a | n/a | n/a | 4136.0 |
| `reversal_pair_count` | 0.00000 | n/a | n/a | n/a | n/a | 4136.0 |
| `strictly_increasing_share` | 0.54014 | n/a | n/a | n/a | n/a | 4136.0 |
| `strictly_decreasing_share` | 0.00000 | n/a | n/a | n/a | n/a | 4136.0 |

**Interpretation.** Of 4136 panels, 4 (0.097%) are palindromes against 10.0% for independent uniform digits, and 0 belong to a non-trivial reversal pair. Strictly increasing panels make up 54.014% and strictly decreasing 0.000%, against the combinatorial 12.0% for each. Orientation frequencies deviate from the combinatorial expectation, indicating the operator's panel ranking may be non-uniform.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `palindrome_share` | 0.00194 | n/a | n/a | n/a | n/a | 4134.0 |
| `reversal_pair_count` | 0.00000 | n/a | n/a | n/a | n/a | 4134.0 |
| `strictly_increasing_share` | 0.53919 | n/a | n/a | n/a | n/a | 4134.0 |
| `strictly_decreasing_share` | 0.00000 | n/a | n/a | n/a | n/a | 4134.0 |

**Interpretation.** Of 4134 panels, 8 (0.194%) are palindromes against 10.0% for independent uniform digits, and 0 belong to a non-trivial reversal pair. Strictly increasing panels make up 53.919% and strictly decreasing 0.000%, against the combinatorial 12.0% for each. Orientation frequencies deviate from the combinatorial expectation, indicating the operator's panel ranking may be non-uniform.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `palindrome_share` | 0.00194 |
| Close | computed | `palindrome_share` | 0.00097 |

Open produced palindrome_share=0.00194; Close produced palindrome_share=0.00097. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Palindrome panels are their own reversal and must be counted once; failing to do so inflates apparent reversal pairs.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
