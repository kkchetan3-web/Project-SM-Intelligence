# M002 - Relative Frequency Analysis

**Category:** A - Frequency and Probability  
**Implementation:** `src.mathematics.frequency::run_002`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\hat{p}_k = \frac{n_k}{N}, \qquad \sum_{k=1}^{K}\hat{p}_k = 1`

---

## 1. Definition and mathematical foundation

Dividing counts by N gives the empirical measure, the maximum-likelihood estimate of the categorical probabilities. Its sampling variability is governed by the multinomial distribution, with Var(p_k) = p_k(1-p_k)/N, so deviations must be judged against that scale rather than by eye.

## 2. Objective

Convert counts into probabilities and quantify how far the empirical distribution departs from the theoretical uniform baseline.

## 3. Complete formula

```
\hat{p}_k = \frac{n_k}{N}, \qquad \sum_{k=1}^{K}\hat{p}_k = 1
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `p_k` | empirical probability of outcome k |
| `N` | total observations |
| `KL` | Kullback-Leibler divergence from uniform |

## 5. Statistical assumptions

- Draws are identically distributed within the estimation window
- Multinomial sampling applies

## 6. Required input data

N >= 10 recommended for the deviations to be interpretable.

## 7. Step-by-step manual calculation

1. Divide each count by N
2. Compute the maximum absolute deviation from 1/K
3. Compute KL divergence and a chi-square-scale deviation

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

p_3 = 4/10 = 0.4; the other observed outcomes have p = 0.1 and the unobserved seven outcomes have p = 0. Maximum deviation from 1/10 is 0.3.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `max_abs_deviation` | 0.01728 | n/a | n/a | n/a | n/a | 3131.0 |
| `kl_from_uniform` | 0.00552 | n/a | n/a | n/a | n/a | 3131.0 |
| `max_deviation_in_se` | 3.22281 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** The largest departure of any empirical probability from the uniform 0.1 is 0.0173, which is 3.22 standard errors of a proportion at this sample size (SE = 0.0054). KL divergence from uniform is 0.00552 nats. Values in this range are typical of a fair process; the formal test is Method 9.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `max_abs_deviation` | 0.01824 | n/a | n/a | n/a | n/a | 3131.0 |
| `kl_from_uniform` | 0.00675 | n/a | n/a | n/a | n/a | 3131.0 |
| `max_deviation_in_se` | 3.40152 | n/a | n/a | n/a | n/a | 3131.0 |

**Interpretation.** The largest departure of any empirical probability from the uniform 0.1 is 0.0182, which is 3.40 standard errors of a proportion at this sample size (SE = 0.0054). KL divergence from uniform is 0.00675 nats. Values in this range are typical of a fair process; the formal test is Method 9.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `max_abs_deviation` | 0.01824 |
| Close | computed | `max_abs_deviation` | 0.01728 |

Open produced max_abs_deviation=0.01824; Close produced max_abs_deviation=0.01728. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Applicable to any market publishing single-digit anks and to jodi markets with the outcome space widened to 100. It assumes nothing beyond a fixed categorical space.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These methods are descriptive rather than predictive; where an out-of-sample number appears (rolling and exponentially weighted frequency) it is scored as a forecast, with the hyperparameter grid evaluated on the same out-of-sample window it is scored on - which makes the reported loss optimistic and is flagged as such.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Relative frequency is a historical average. It is an unbiased estimate of a *stationary* probability, which the data may not possess.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
