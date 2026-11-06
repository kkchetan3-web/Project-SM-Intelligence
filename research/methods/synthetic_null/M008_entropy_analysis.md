# M008 - Entropy Analysis

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_008`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `H(X) = -\sum_{k=1}^{K} p_k \log_2 p_k \le \log_2 K`

---

## 1. Definition and mathematical foundation

Entropy measures the average surprise of a distribution and therefore the irreducible uncertainty in the draw. For K=10 the ceiling is log2(10) = 3.3219 bits; a process at that ceiling is maximally unpredictable in the marginal sense, and any persistent drop below it signals exploitable imbalance.

## 2. Objective

Measure and monitor the uncertainty of the outcome distribution over time.

## 3. Complete formula

```
H(X) = -\sum_{k=1}^{K} p_k \log_2 p_k \le \log_2 K
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `H` | Shannon entropy in bits |
| `p_k` | probability of outcome k |
| `normalised H` | H / log2(K) |

## 5. Statistical assumptions

- The entropy estimate is computed from the empirical distribution
- Rolling entropy is comparable across windows

## 6. Required input data

N >= 100 for a stable estimate with K=10.

## 7. Step-by-step manual calculation

1. Estimate the marginal distribution
2. Compute entropy and normalised entropy
3. Compare rolling entropy against a simulated uniform process

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Non-zero empirical probabilities are (0.4, 0.1, 0.1, 0.1, 0.1, 0.1) at outcomes (3, 1, 7, 0, 9, 2).

```
H = -(0.4 log2 0.4 + 5 x 0.1 log2 0.1)
  = -(0.4 x -1.3219 + 5 x 0.1 x -3.3219)
  = 0.5288 + 1.6610 = 2.1610 bits
```
Note this toy-sample entropy (2.161) is far below the population ceiling of 3.322 bits only because ten draws cannot populate ten categories.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `entropy_bits` | 3.32043 | n/a | n/a | n/a | n/a | 3131.0 |
| `normalised_entropy` | 0.99955 | n/a | n/a | n/a | n/a | 3131.0 |
| `entropy_gap_from_max` | 0.00150 | n/a | n/a | n/a | n/a | 3131.0 |
| `rolling_entropy_mean` | 3.29341 | n/a | n/a | n/a | n/a | 250.0 |
| `simulated_entropy_mean` | 3.29552 | n/a | n/a | n/a | n/a | 250.0 |
| `rolling_vs_simulated_z` | -0.17225 | n/a | n/a | n/a | n/a | 47.0 |

**Interpretation.** Marginal entropy is 3.3204 bits against a ceiling of 3.3219 (normalised 0.9995). The deficit of 0.0015 bits is the total predictable content available in the marginal distribution. Rolling entropy over a 250-draw window averages 3.2934 bits, against 3.2955 for simulated uniform draws of the same window size - a z-score of -0.17. Entropy measures only the marginal; serial dependence is invisible to it.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `entropy_bits` | 3.32035 | n/a | n/a | n/a | n/a | 3131.0 |
| `normalised_entropy` | 0.99952 | n/a | n/a | n/a | n/a | 3131.0 |
| `entropy_gap_from_max` | 0.00158 | n/a | n/a | n/a | n/a | 3131.0 |
| `rolling_entropy_mean` | 3.29189 | n/a | n/a | n/a | n/a | 250.0 |
| `simulated_entropy_mean` | 3.29552 | n/a | n/a | n/a | n/a | 250.0 |
| `rolling_vs_simulated_z` | -0.29613 | n/a | n/a | n/a | n/a | 47.0 |

**Interpretation.** Marginal entropy is 3.3203 bits against a ceiling of 3.3219 (normalised 0.9995). The deficit of 0.0016 bits is the total predictable content available in the marginal distribution. Rolling entropy over a 250-draw window averages 3.2919 bits, against 3.2955 for simulated uniform draws of the same window size - a z-score of -0.30. Entropy measures only the marginal; serial dependence is invisible to it.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `entropy_bits` | 3.32035 |
| Close | computed | `entropy_bits` | 3.32043 |

Open produced entropy_bits=3.32035; Close produced entropy_bits=3.32043. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

12 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Entropy summarises the marginal only; it is blind to serial dependence, which is why M023 and M031 are needed as well.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
