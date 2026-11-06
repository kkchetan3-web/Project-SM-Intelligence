# M009 - Chi-Square Goodness-of-Fit

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_009`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `chi2_statistic` | 6.58224 | 6.58224 | 0.68052 | 0.89312 | 0.04585 | 3131.0 |
| `cramers_v` | 0.04585 | n/a | n/a | n/a | n/a | 3131.0 |
| `p_value` | 0.68052 | n/a | 0.68052 | 0.89312 | n/a | 3131.0 |
| `min_expected_count` | 313.10000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Pearson chi-square against the uniform distribution is 6.582 on 9 degrees of freedom, p = 0.6805. Cramer's V is 0.0459, i.e. the association between outcome and uniform expectation explains about 0.21% of the chi-square scale. The expected-count assumption is satisfied (min expected 313.1 >= 5). The data are consistent with a uniform marginal distribution.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `chi2_statistic` | 6.77387 | 6.77387 | 0.66065 | 0.94116 | 0.04651 | 3131.0 |
| `cramers_v` | 0.04651 | n/a | n/a | n/a | n/a | 3131.0 |
| `p_value` | 0.66065 | n/a | 0.66065 | 0.94116 | n/a | 3131.0 |
| `min_expected_count` | 313.10000 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** Pearson chi-square against the uniform distribution is 6.774 on 9 degrees of freedom, p = 0.6606. Cramer's V is 0.0465, i.e. the association between outcome and uniform expectation explains about 0.22% of the chi-square scale. The expected-count assumption is satisfied (min expected 313.1 >= 5). The data are consistent with a uniform marginal distribution.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `chi2_statistic` | 6.77387 |
| Close | computed | `chi2_statistic` | 6.58224 |

Open produced chi2_statistic=6.77387; Close produced chi2_statistic=6.58224. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Rejection means 'not exactly uniform', not 'predictable'. With thousands of draws a tiny deviation is detectable and useless.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Pearson (1900)
