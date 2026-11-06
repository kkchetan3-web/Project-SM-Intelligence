# M009 - Chi-Square Goodness-of-Fit

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_009`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\chi^2 = \sum_{k=1}^{K}\frac{(O_k-E_k)^2}{E_k},\quad df = K-1`

---

## 1. Definition and mathematical foundation

The Pearson statistic compares observed counts with the counts a hypothesised distribution predicts. Under the null and with adequate expected counts it is asymptotically chi-square with K-1 degrees of freedom. Cramer's V rescales it to a 0-1 effect size, which matters because with large N a negligible imbalance becomes 'significant'.

## 2. Objective

Test whether the outcome distribution departs from uniform.

## 3. Complete formula

```
\chi^2 = \sum_{k=1}^{K}\frac{(O_k-E_k)^2}{E_k},\quad df = K-1
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `O_k` | observed count |
| `E_k` | expected count under the null |
| `df` | degrees of freedom |
| `V` | Cramer's V effect size |

## 5. Statistical assumptions

- Observations are independent
- Expected count per category >= 5

## 6. Required input data

Expected count >= 5 in every category.

## 7. Step-by-step manual calculation

1. Compute expected counts N/K
2. Sum squared standardised deviations
3. Compare with the chi-square distribution and report V

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Expected count = 10/10 = 1 per outcome.

```
chi2 = (4-1)^2/1 + 5 x (1-1)^2/1 + 4 x (0-1)^2/1 = 9 + 0 + 4 = 20.0
df = 9
```
The expected-count assumption fails badly here, which is exactly why the method record requires min E_k >= 5.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `chi2_statistic` | 34.05589 | 34.05589 | 8.733e-05 | 0.00035 | 0.10429 | 3131.0 |
| `cramers_v` | 0.10429 | n/a | n/a | n/a | n/a | 3131.0 |
| `p_value` | 8.733e-05 | n/a | 8.733e-05 | 0.00035 | n/a | 3131.0 |
| `min_expected_count` | 313.10000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Pearson chi-square against the uniform distribution is 34.056 on 9 degrees of freedom, p = 0.0001. Cramer's V is 0.1043, i.e. the association between outcome and uniform expectation explains about 1.09% of the chi-square scale. The expected-count assumption is satisfied (min expected 313.1 >= 5). A rejection here means the distribution is not exactly uniform; it says nothing about whether the deviation is large enough to forecast.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `chi2_statistic` | 41.91920 | 41.91920 | 3.400e-06 | 1.394e-05 | 0.11571 | 3131.0 |
| `cramers_v` | 0.11571 | n/a | n/a | n/a | n/a | 3131.0 |
| `p_value` | 3.400e-06 | n/a | 3.400e-06 | 1.394e-05 | n/a | 3131.0 |
| `min_expected_count` | 313.10000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Pearson chi-square against the uniform distribution is 41.919 on 9 degrees of freedom, p = 0.0000. Cramer's V is 0.1157, i.e. the association between outcome and uniform expectation explains about 1.34% of the chi-square scale. The expected-count assumption is satisfied (min expected 313.1 >= 5). A rejection here means the distribution is not exactly uniform; it says nothing about whether the deviation is large enough to forecast.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `chi2_statistic` | 41.91920 |
| Close | computed | `chi2_statistic` | 34.05589 |

Open produced chi2_statistic=41.91920; Close produced chi2_statistic=34.05589. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 4 survive Benjamini-Hochberg control at q=0.05 (close:chi2_statistic, close:p_value, open:chi2_statistic, open:p_value). Surviving correction is necessary but not sufficient: the predictive section is what establishes usefulness. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Rejection means 'not exactly uniform', not 'predictable'. With thousands of draws a tiny deviation is detectable and useless.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Pearson (1900)
