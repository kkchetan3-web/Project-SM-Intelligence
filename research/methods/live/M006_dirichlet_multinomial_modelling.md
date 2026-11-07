# M006 - Dirichlet-Multinomial Modelling

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_006`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\theta \mid D \sim \mathrm{Dirichlet}(\alpha_1+n_1,\ldots,\alpha_K+n_K)`

---

## 1. Definition and mathematical foundation

The Dirichlet-multinomial is the conjugate pair for over-dispersed categorical counts: unlike the multinomial it allows correlation between category counts through the shared concentration. Estimating the concentration from the data reveals whether the observed dispersion exceeds multinomial noise.

## 2. Objective

Estimate the concentration parameter and test for over-dispersion.

## 3. Complete formula

```
\theta \mid D \sim \mathrm{Dirichlet}(\alpha_1+n_1,\ldots,\alpha_K+n_K)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `alpha_0` | total concentration |
| `n_k` | observed counts |
| `over-dispersion` | observed vs multinomial variance ratio |

## 5. Statistical assumptions

- Counts arise from a Dirichlet-multinomial, not a plain multinomial
- Concentration is constant across the sample

## 6. Required input data

N considerably larger than K.

## 7. Step-by-step manual calculation

1. Estimate alpha_0 by matching the observed variance of counts
2. Compute posterior means under the fitted concentration
3. Compare predicted dispersion against the multinomial prediction

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

With prior alpha=1.0: posterior mean for outcome 3 is (4+1.0)/(10+10.0) = 0.3000, and for an unseen outcome it is 1.0/(10+10.0) = 0.0500. Shrinkage toward uniform is total prior mass divided by total mass: 10.0/(10+10.0) = 0.500.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `variance_ratio` | 0.55297 | n/a | n/a | n/a | n/a | 4143.0 |
| `estimated_alpha0` | n/a | n/a | n/a | n/a | n/a | 4143.0 |
| `multinomial_expected_count_var` | 186.35848 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** The split-half variance of category counts is 103.05 against a multinomial prediction of 186.36, a ratio of 0.553. A ratio near 1 means the counts behave exactly as multinomial sampling predicts, i.e. there is no extra over-dispersion to model; the concentration is not identifiable because the ratio is at or below 1.

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
| `variance_ratio` | 1.20690 | n/a | n/a | n/a | n/a | 4143.0 |
| `estimated_alpha0` | 10006.47466 | n/a | n/a | n/a | n/a | 4143.0 |
| `multinomial_expected_count_var` | 186.38733 | n/a | n/a | n/a | n/a | 4143.0 |

**Interpretation.** The split-half variance of category counts is 224.95 against a multinomial prediction of 186.39, a ratio of 1.207. A ratio near 1 means the counts behave exactly as multinomial sampling predicts, i.e. there is no extra over-dispersion to model; the implied Dirichlet concentration is about 10006.5, indicating only weak between-category correlation.

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
| Open | computed | `variance_ratio` | 1.20690 |
| Close | computed | `variance_ratio` | 0.55297 |

Open produced variance_ratio=1.20690; Close produced variance_ratio=0.55297. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Moment estimation of alpha_0 is noisy when K is small relative to N.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
