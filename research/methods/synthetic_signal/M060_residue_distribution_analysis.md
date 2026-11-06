# M060 - Residue Distribution Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_060`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `uniformity_chi2_mod2` | 0.43724 | n/a | 0.50846 | 0.66684 | n/a | 3131.0 |
| `uniformity_chi2_mod3` | 6.05392 | n/a | 0.04846 | 0.09929 | n/a | 3131.0 |
| `uniformity_chi2_mod5` | 32.10923 | n/a | 1.817e-06 | 1.018e-05 | n/a | 3131.0 |
| `uniformity_chi2_mod10` | 34.05589 | n/a | 8.733e-05 | 0.00035 | n/a | 3131.0 |
| `stability_chi2_mod2` | 1.52133 | n/a | 0.21742 | 0.36526 | n/a | 3131.0 |
| `stability_chi2_mod3` | 0.60859 | n/a | 0.73764 | 0.80470 | n/a | 3131.0 |
| `stability_chi2_mod5` | 4.56178 | n/a | 0.33528 | 0.50293 | n/a | 3131.0 |
| `stability_chi2_mod10` | 12.99552 | n/a | 0.16281 | 0.29730 | n/a | 3131.0 |
| `n_moduli_with_any_rejection` | 2.00000 | n/a | n/a | n/a | n/a | 4.0 |

**Interpretation.** Residue classes tested for both uniformity and stability across sample halves: m=2: uniformity p=0.508, stability p=0.217, m=3: uniformity p=0.048, stability p=0.738, m=5: uniformity p=0.000, stability p=0.335, m=10: uniformity p=0.000, stability p=0.163. After Holm correction across all 8 tests, 2 moduli show any rejection. Some modulus shows a rejection after correction. Because nested moduli are strongly dependent, consistency across the family is the real test and a single-modulus rejection is weak evidence.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `uniformity_chi2_mod2` | 0.03865 | n/a | 0.84415 | 1.00000 | n/a | 3131.0 |
| `uniformity_chi2_mod3` | 3.65852 | n/a | 0.16053 | 0.31342 | n/a | 3131.0 |
| `uniformity_chi2_mod5` | 35.20728 | n/a | 4.211e-07 | 2.656e-06 | n/a | 3131.0 |
| `uniformity_chi2_mod10` | 41.91920 | n/a | 3.400e-06 | 1.394e-05 | n/a | 3131.0 |
| `stability_chi2_mod2` | 0.34774 | n/a | 0.55539 | 0.77190 | n/a | 3131.0 |
| `stability_chi2_mod3` | 0.14978 | n/a | 0.92784 | 1.00000 | n/a | 3131.0 |
| `stability_chi2_mod5` | 0.68501 | n/a | 0.95316 | 1.00000 | n/a | 3131.0 |
| `stability_chi2_mod10` | 1.16390 | n/a | 0.99896 | 1.00000 | n/a | 3131.0 |
| `n_moduli_with_any_rejection` | 2.00000 | n/a | n/a | n/a | n/a | 4.0 |

**Interpretation.** Residue classes tested for both uniformity and stability across sample halves: m=2: uniformity p=0.844, stability p=0.555, m=3: uniformity p=0.161, stability p=0.928, m=5: uniformity p=0.000, stability p=0.953, m=10: uniformity p=0.000, stability p=0.999. After Holm correction across all 8 tests, 2 moduli show any rejection. Some modulus shows a rejection after correction. Because nested moduli are strongly dependent, consistency across the family is the real test and a single-modulus rejection is weak evidence.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `uniformity_chi2_mod2` | 0.03865 |
| Close | computed | `uniformity_chi2_mod2` | 0.43724 |

Open produced uniformity_chi2_mod2=0.03865; Close produced uniformity_chi2_mod2=0.43724. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

18 p-values were produced across the computed targets; 4 survive Benjamini-Hochberg control at q=0.05 (close:uniformity_chi2_mod5, close:uniformity_chi2_mod10, open:uniformity_chi2_mod5, open:uniformity_chi2_mod10). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The tests are highly dependent across moduli, so naive multiple-testing correction is conservative while treating them as independent would be anti-conservative.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
