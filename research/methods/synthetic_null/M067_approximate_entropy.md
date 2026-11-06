# M067 - Approximate Entropy

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_067`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `ApEn(m,r)=\Phi^m(r)-\Phi^{m+1}(r)`

---

## 1. Definition and mathematical foundation

Approximate entropy is the predecessor of sample entropy. It counts self-matches, which biases it toward reporting more regularity than exists, but it is retained because the discrepancy between the two is itself a useful diagnostic.

## 2. Objective

Measure sequence regularity with the original statistic.

## 3. Complete formula

```
ApEn(m,r)=\Phi^m(r)-\Phi^{m+1}(r)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `Phi^m` | mean log match fraction at length m |
| `m` | embedding dimension |

## 5. Statistical assumptions

- Pattern length and tolerance are fixed a priori

## 6. Required input data

Several hundred observations.

## 7. Step-by-step manual calculation

1. Count matches at length m and m+1 including self-matches
2. Average the log match fractions
3. Take the difference

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Entropy, Hurst and latent-state estimators are all severely biased below ~100 observations, so no honest worked example exists at n=10. The method record states the minimum sample size; the computed section reports the real estimate with its simulated reference band, which is the only defensible way to read it.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `apen_m1` | 2.28979 | n/a | n/a | n/a | n/a | 3131.0 |
| `apen_m2` | 2.13920 | n/a | n/a | n/a | n/a | 3131.0 |
| `apen_m3` | 1.10713 | n/a | n/a | n/a | n/a | 3131.0 |
| `simulated_apen_m2_mean` | 2.14576 | n/a | n/a | n/a | n/a | 20.0 |
| `sampen_minus_apen_m2` | n/a | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Approximate entropy: m=1 2.289794248855479, m=2 2.139195927206292, m=3 1.1071260371836686. Simulated uniform sequences give 2.1458 at m=2. ApEn counts self-matches, which biases it toward reporting more regularity than exists; Sample entropy (Method 66) removes that bias. The two should be read together, and a large gap between them is itself evidence that the apparent regularity is a finite-sample artefact rather than structure.

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
| `apen_m1` | 2.28635 | n/a | n/a | n/a | n/a | 3131.0 |
| `apen_m2` | 2.12282 | n/a | n/a | n/a | n/a | 3131.0 |
| `apen_m3` | 1.11018 | n/a | n/a | n/a | n/a | 3131.0 |
| `simulated_apen_m2_mean` | 2.14576 | n/a | n/a | n/a | n/a | 20.0 |
| `sampen_minus_apen_m2` | n/a | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Approximate entropy: m=1 2.286347681536565, m=2 2.1228169037504223, m=3 1.1101818279402638. Simulated uniform sequences give 2.1458 at m=2. ApEn counts self-matches, which biases it toward reporting more regularity than exists; Sample entropy (Method 66) removes that bias. The two should be read together, and a large gap between them is itself evidence that the apparent regularity is a finite-sample artefact rather than structure.

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
| Open | computed | `apen_m1` | 2.28635 |
| Close | computed | `apen_m1` | 2.28979 |

Open produced apen_m1=2.28635; Close produced apen_m1=2.28979. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

The self-match bias makes ApEn systematically lower than SampEn; comparing the two reveals how much of the apparent regularity is an artefact.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Pincus (1991)
