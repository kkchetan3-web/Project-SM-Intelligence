# M066 - Sample Entropy

**Category:** F - Randomness and Statistical Structure  
**Implementation:** `src.mathematics.randomness::run_066`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `SampEn(m,r)=-\ln\frac{A}{B}`

---

## 1. Definition and mathematical foundation

Sample entropy measures the probability that two similar patterns of length m remain similar when extended by one. Low values indicate regularity; high values indicate unpredictability. For categorical data the tolerance r is replaced by exact matching, which the implementation handles explicitly.

## 2. Objective

Quantify sequence regularity without bias from self-matches.

## 3. Complete formula

```
SampEn(m,r)=-\ln\frac{A}{B}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `m` | embedding dimension |
| `A` | extended matches |
| `B` | matches at length m |

## 5. Statistical assumptions

- Pattern length and tolerance are fixed a priori
- The series is long relative to the pattern length

## 6. Required input data

Several hundred observations.

## 7. Step-by-step manual calculation

1. Form length-m patterns
2. Count matches with and without extension
3. Compute the negative log ratio

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Entropy, Hurst and latent-state estimators are all severely biased below ~100 observations, so no honest worked example exists at n=10. The method record states the minimum sample size; the computed section reports the real estimate with its simulated reference band, which is the only defensible way to read it.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `sampen_m1` | 1.95778 | n/a | n/a | n/a | n/a | 3131.0 |
| `sampen_m2` | 1.96754 | n/a | n/a | n/a | n/a | 3131.0 |
| `sampen_m3` | 1.93774 | n/a | n/a | n/a | n/a | 3131.0 |
| `simulated_sampen_m2_mean` | 2.30471 | n/a | n/a | n/a | n/a | 20.0 |
| `sampen_excess_over_simulation` | -0.33717 | n/a | n/a | n/a | n/a | 20.0 |

**Interpretation.** Sample entropy (exact-match, so the tolerance parameter is not needed): m=1: 1.9577797004363335, m=2: 1.9675398229992496, m=3: 1.9377368301593405. Simulated uniform sequences give 2.3047 at m=2; the observed excess is -0.3372. The observed regularity differs from the simulated reference. Note that with a 10-symbol alphabet matches at m=3 are extremely rare, so high-order estimates are unreliable and may be undefined.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `sampen_m1` | 1.75819 | n/a | n/a | n/a | n/a | 3131.0 |
| `sampen_m2` | 1.79182 | n/a | n/a | n/a | n/a | 3131.0 |
| `sampen_m3` | 1.78986 | n/a | n/a | n/a | n/a | 3131.0 |
| `simulated_sampen_m2_mean` | 2.30471 | n/a | n/a | n/a | n/a | 20.0 |
| `sampen_excess_over_simulation` | -0.51289 | n/a | n/a | n/a | n/a | 20.0 |

**Interpretation.** Sample entropy (exact-match, so the tolerance parameter is not needed): m=1: 1.7581924142208274, m=2: 1.7918180580575256, m=3: 1.7898629351014863. Simulated uniform sequences give 2.3047 at m=2; the observed excess is -0.5129. The observed regularity differs from the simulated reference. Note that with a 10-symbol alphabet matches at m=3 are extremely rare, so high-order estimates are unreliable and may be undefined.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 5,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `sampen_m1` | 1.75819 |
| Close | computed | `sampen_m1` | 1.95778 |

Open produced sampen_m1=1.75819; Close produced sampen_m1=1.95778. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Universally applicable, and the correct place to look when deciding whether any other result in the report should be believed.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These are calibration tests of the null hypothesis; their output is the reference against which the other 88 methods are judged.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Matching in a 10-symbol alphabet is rare, so A and B can be zero, in which case entropy is undefined rather than infinite; the implementation reports that case honestly.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Richman & Moorman (2000)
