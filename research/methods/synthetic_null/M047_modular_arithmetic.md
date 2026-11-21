# M047 - Modular Arithmetic

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_047`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `r = n \bmod m`

---

## 1. Definition and mathematical foundation

Reducing outcomes modulo m folds the outcome space into residue classes. For a fair draw each residue class should receive a predictable share (equal when m divides K, otherwise differing by at most one observation), so residues give a compact, low-dimensional test of structure that is more statistically powerful than a full 10-category test.

## 2. Objective

Test whether residue classes are uniformly represented.

## 3. Complete formula

```
r = n \bmod m
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `r` | residue |
| `n` | numeric outcome |
| `m` | modulus |

## 5. Statistical assumptions

- The underlying integer representation is meaningful
- Residue classes are exhaustive and mutually exclusive

## 6. Required input data

Enough observations for the smallest residue class to have >= 5 expected counts.

## 7. Step-by-step manual calculation

1. Choose moduli (2, 3, 5, 7)
2. Map each outcome to its residue
3. Test the residue distribution with exact binomial or chi-square methods

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Residues mod 5 of the toy sequence: [1, 1, 2, 5, 1]. Under uniformity each of the five classes holds 2 of the 10 outcomes, so the expected count is 2 per class.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `chi2_mod2` | 1.03769 | n/a | 0.30836 | 0.85225 | n/a | 3131.0 |
| `chi2_mod3` | 1.98094 | n/a | 0.37140 | 0.85225 | n/a | 3131.0 |
| `chi2_mod5` | 1.68125 | n/a | 0.79412 | 0.93952 | n/a | 3131.0 |
| `chi2_mod7` | 6.38582 | n/a | 0.38139 | 0.85225 | n/a | 3131.0 |
| `n_significant_holm` | 0.00000 | n/a | n/a | n/a | n/a | 4.0 |

**Interpretation.** Residue uniformity across moduli: m=2: chi2=1.04 (Holm p=1.0000), m=3: chi2=1.98 (Holm p=1.0000), m=5: chi2=1.68 (Holm p=1.0000), m=7: chi2=6.39 (Holm p=1.0000). 0 of 4 remain significant after correction. Mod 2 is the coarsest and most powerful split, so if any modulus were to show a real effect it would most likely be that one.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `chi2_mod2` | 2.52986 | n/a | 0.11171 | 0.83640 | n/a | 3131.0 |
| `chi2_mod3` | 1.58677 | n/a | 0.45231 | 0.94116 | n/a | 3131.0 |
| `chi2_mod5` | 1.73235 | n/a | 0.78483 | 0.95351 | n/a | 3131.0 |
| `chi2_mod7` | 3.55446 | n/a | 0.73671 | 0.94391 | n/a | 3131.0 |
| `n_significant_holm` | 0.00000 | n/a | n/a | n/a | n/a | 4.0 |

**Interpretation.** Residue uniformity across moduli: m=2: chi2=2.53 (Holm p=0.4468), m=3: chi2=1.59 (Holm p=1.0000), m=5: chi2=1.73 (Holm p=1.0000), m=7: chi2=3.55 (Holm p=1.0000). 0 of 4 remain significant after correction. Mod 2 is the coarsest and most powerful split, so if any modulus were to show a real effect it would most likely be that one.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `chi2_mod2` | 2.52986 |
| Close | computed | `chi2_mod2` | 1.03769 |

Open produced chi2_mod2=2.52986; Close produced chi2_mod2=1.03769. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Modular folding throws away information; a rejection here does not identify which categories drive the imbalance.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
