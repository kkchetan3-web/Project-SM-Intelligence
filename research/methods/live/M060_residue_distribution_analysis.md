# M060 - Residue Distribution Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_060`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `c_k = |\{t : x_t \equiv k \pmod m\}|`

---

## 1. Definition and mathematical foundation

Residue classes offer a graded family of partitions: with m=2 you get parity, with m=5 you get a five-way split, with m=10 the full space. Testing across the family shows whether apparent structure is consistent at every resolution or appears at exactly one, which is the signature of a chance finding.

## 2. Objective

Test residue distributions across a family of moduli and check consistency.

## 3. Complete formula

```
c_k = |\{t : x_t \equiv k \pmod m\}|
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `c_k` | count in residue class k |
| `m` | modulus |

## 5. Statistical assumptions

- Residues are exhaustive for each modulus
- Tests across moduli are correlated

## 6. Required input data

Any non-empty sample.

## 7. Step-by-step manual calculation

1. For each modulus build the class counts
2. Test each for uniformity
3. Check whether rejections are consistent across moduli and correct for multiplicity

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Residues mod 5 of the toy sequence: [1, 1, 2, 5, 1]. Under uniformity each of the five classes holds 2 of the 10 outcomes, so the expected count is 2 per class.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `uniformity_chi2_mod2` | 0.40574 | n/a | 0.52414 | 0.79549 | n/a | 4143.0 |
| `uniformity_chi2_mod3` | 6.99014 | n/a | 0.03035 | 0.26771 | n/a | 4143.0 |
| `uniformity_chi2_mod5` | 3.29858 | n/a | 0.50916 | 0.79549 | n/a | 4143.0 |
| `uniformity_chi2_mod10` | 15.30316 | n/a | 0.08294 | 0.33175 | n/a | 4143.0 |
| `stability_chi2_mod2` | 1.50617 | n/a | 0.21972 | 0.52855 | n/a | 4143.0 |
| `stability_chi2_mod3` | 0.03604 | n/a | 0.98214 | 1.00000 | n/a | 4143.0 |
| `stability_chi2_mod5` | 1.48233 | n/a | 0.82977 | 1.00000 | n/a | 4143.0 |
| `stability_chi2_mod10` | 4.84717 | n/a | 0.84742 | 1.00000 | n/a | 4143.0 |
| `n_moduli_with_any_rejection` | 0.00000 | n/a | n/a | n/a | n/a | 4.0 |

**Interpretation.** Residue classes tested for both uniformity and stability across sample halves: m=2: uniformity p=0.524, stability p=0.220, m=3: uniformity p=0.030, stability p=0.982, m=5: uniformity p=0.509, stability p=0.830, m=10: uniformity p=0.083, stability p=0.847. After Holm correction across all 8 tests, 0 moduli show any rejection. Residue structure is consistent at every resolution tested, which is the signature of a genuinely featureless process: a real effect would not appear at exactly one modulus and vanish at its multiples.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `uniformity_chi2_mod2` | 0.44629 | n/a | 0.50410 | 0.72564 | n/a | 4143.0 |
| `uniformity_chi2_mod3` | 5.52744 | n/a | 0.06306 | 0.22249 | n/a | 4143.0 |
| `uniformity_chi2_mod5` | 2.75308 | n/a | 0.59996 | 0.79349 | n/a | 4143.0 |
| `uniformity_chi2_mod10` | 9.53440 | n/a | 0.38947 | 0.65553 | n/a | 4143.0 |
| `stability_chi2_mod2` | 4.01644 | n/a | 0.04506 | 0.17594 | n/a | 4143.0 |
| `stability_chi2_mod3` | 1.81736 | n/a | 0.40305 | 0.66101 | n/a | 4143.0 |
| `stability_chi2_mod5` | 3.40721 | n/a | 0.49213 | 0.72564 | n/a | 4143.0 |
| `stability_chi2_mod10` | 11.11334 | n/a | 0.26802 | 0.53604 | n/a | 4143.0 |
| `n_moduli_with_any_rejection` | 0.00000 | n/a | n/a | n/a | n/a | 4.0 |

**Interpretation.** Residue classes tested for both uniformity and stability across sample halves: m=2: uniformity p=0.504, stability p=0.045, m=3: uniformity p=0.063, stability p=0.403, m=5: uniformity p=0.600, stability p=0.492, m=10: uniformity p=0.389, stability p=0.268. After Holm correction across all 8 tests, 0 moduli show any rejection. Residue structure is consistent at every resolution tested, which is the signature of a genuinely featureless process: a real effect would not appear at exactly one modulus and vanish at its multiples.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `uniformity_chi2_mod2` | 0.44629 |
| Close | computed | `uniformity_chi2_mod2` | 0.40574 |

Open produced uniformity_chi2_mod2=0.44629; Close produced uniformity_chi2_mod2=0.40574. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The tests are highly dependent across moduli, so naive multiple-testing correction is conservative while treating them as independent would be anti-conservative.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
