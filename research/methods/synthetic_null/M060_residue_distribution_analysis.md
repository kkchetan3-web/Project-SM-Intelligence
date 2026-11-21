# M060 - Residue Distribution Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_060`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `uniformity_chi2_mod2` | 1.03769 | n/a | 0.30836 | 0.85225 | n/a | 3131.0 |
| `uniformity_chi2_mod3` | 1.98094 | n/a | 0.37140 | 0.85225 | n/a | 3131.0 |
| `uniformity_chi2_mod5` | 1.68125 | n/a | 0.79412 | 0.93952 | n/a | 3131.0 |
| `uniformity_chi2_mod10` | 6.58224 | n/a | 0.68052 | 0.89312 | n/a | 3131.0 |
| `stability_chi2_mod2` | 1.18954 | n/a | 0.27542 | 0.85225 | n/a | 3131.0 |
| `stability_chi2_mod3` | 0.16946 | n/a | 0.91876 | 0.98154 | n/a | 3131.0 |
| `stability_chi2_mod5` | 3.37625 | n/a | 0.49694 | 0.88815 | n/a | 3131.0 |
| `stability_chi2_mod10` | 7.77131 | n/a | 0.55735 | 0.89312 | n/a | 3131.0 |
| `n_moduli_with_any_rejection` | 0.00000 | n/a | n/a | n/a | n/a | 4.0 |

**Interpretation.** Residue classes tested for both uniformity and stability across sample halves: m=2: uniformity p=0.308, stability p=0.275, m=3: uniformity p=0.371, stability p=0.919, m=5: uniformity p=0.794, stability p=0.497, m=10: uniformity p=0.681, stability p=0.557. After Holm correction across all 8 tests, 0 moduli show any rejection. Residue structure is consistent at every resolution tested, which is the signature of a genuinely featureless process: a real effect would not appear at exactly one modulus and vanish at its multiples.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `uniformity_chi2_mod2` | 2.52986 | n/a | 0.11171 | 0.83640 | n/a | 3131.0 |
| `uniformity_chi2_mod3` | 1.58677 | n/a | 0.45231 | 0.94116 | n/a | 3131.0 |
| `uniformity_chi2_mod5` | 1.73235 | n/a | 0.78483 | 0.95351 | n/a | 3131.0 |
| `uniformity_chi2_mod10` | 6.77387 | n/a | 0.66065 | 0.94116 | n/a | 3131.0 |
| `stability_chi2_mod2` | 2.76630 | n/a | 0.09627 | 0.83640 | n/a | 3131.0 |
| `stability_chi2_mod3` | 0.09345 | n/a | 0.95435 | 1.00000 | n/a | 3131.0 |
| `stability_chi2_mod5` | 3.12173 | n/a | 0.53767 | 0.94116 | n/a | 3131.0 |
| `stability_chi2_mod10` | 7.55152 | n/a | 0.57990 | 0.94116 | n/a | 3131.0 |
| `n_moduli_with_any_rejection` | 0.00000 | n/a | n/a | n/a | n/a | 4.0 |

**Interpretation.** Residue classes tested for both uniformity and stability across sample halves: m=2: uniformity p=0.112, stability p=0.096, m=3: uniformity p=0.452, stability p=0.954, m=5: uniformity p=0.785, stability p=0.538, m=10: uniformity p=0.661, stability p=0.580. After Holm correction across all 8 tests, 0 moduli show any rejection. Residue structure is consistent at every resolution tested, which is the signature of a genuinely featureless process: a real effect would not appear at exactly one modulus and vanish at its multiples.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 9,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `uniformity_chi2_mod2` | 2.52986 |
| Close | computed | `uniformity_chi2_mod2` | 1.03769 |

Open produced uniformity_chi2_mod2=2.52986; Close produced uniformity_chi2_mod2=1.03769. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

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
