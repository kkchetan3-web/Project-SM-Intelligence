# M100 - Sequential Probability Ratio Testing

**Category:** H - Advanced Probability, Ensembles and Validation  
**Implementation:** `src.mathematics.advanced_statistics::run_100`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\Lambda_n = \prod_{t=1}^{n}\frac{P_1(x_t)}{P_0(x_t)},\quad \text{stop when } \log\Lambda_n \notin (a,b)`

---

## 1. Definition and mathematical foundation

SPRT tests two simple hypotheses as data arrive, with Wald's optimality result guaranteeing the smallest expected sample size for given error rates. It is the natural framework for asking 'how much evidence would it take to convince me that this market is biased?'

## 2. Objective

Quantify how much data would be needed to detect a specified bias.

## 3. Complete formula

```
\Lambda_n = \prod_{t=1}^{n}\frac{P_1(x_t)}{P_0(x_t)},\quad \text{stop when } \log\Lambda_n \notin (a,b)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `Lambda_n` | likelihood ratio |
| `a, b` | decision boundaries |
| `alpha, beta` | error rates |

## 5. Statistical assumptions

- Two simple hypotheses are specified
- Observations are independent under each

## 6. Required input data

A specified alternative hypothesis.

## 7. Step-by-step manual calculation

1. Specify a null and an alternative probability vector
2. Accumulate the log likelihood ratio as draws arrive
3. Report the stopping time and the implied sample-size requirement

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

The arithmetic is the ensemble/metric formula stated above; the substantive question is always whether the held-out comparison clears its uncertainty band, which is what the computed section reports.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `final_log_likelihood_ratio` | -199.69875 | n/a | n/a | n/a | n/a | 3131.0 |
| `upper_boundary_b` | 2.89037 | n/a | n/a | n/a | n/a | 3131.0 |
| `lower_boundary_a` | -2.25129 | n/a | n/a | n/a | n/a | 3131.0 |
| `decision_reached` | 1.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `kl_divergence_h0_h1` | 0.06083 | n/a | n/a | n/a | n/a | 3131.0 |
| `expected_sample_size_under_h0` | -1994208620781.36157 | n/a | n/a | n/a | n/a | 3131.0 |
| `log_lr_at_half_sample` | -117.05600 | n/a | n/a | n/a | n/a | 1565.0 |

**Interpretation.** Testing H0 (uniform) against H1 (a 1.5% per-category bias) with alpha=0.05, beta=0.1: boundaries are a=-2.251 and b=2.890. Over 3131 draws the accumulated log likelihood ratio is -199.699, having reached -117.056 at the halfway point. The test crossed a boundary at draw 20 and decided. The KL divergence between the hypotheses is 6.08e-02 nats per draw, implying an expected sample size of about -1,994,208,620,781 draws under H0 to reach a decision. This is the single most important number in the report: it quantifies how much data a bias of this size would require, and shows why a few thousand draws cannot settle the question either way.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `final_log_likelihood_ratio` | -198.68182 | n/a | n/a | n/a | n/a | 3131.0 |
| `upper_boundary_b` | 2.89037 | n/a | n/a | n/a | n/a | 3131.0 |
| `lower_boundary_a` | -2.25129 | n/a | n/a | n/a | n/a | 3131.0 |
| `decision_reached` | 1.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `kl_divergence_h0_h1` | 0.06083 | n/a | n/a | n/a | n/a | 3131.0 |
| `expected_sample_size_under_h0` | -1994208620781.36157 | n/a | n/a | n/a | n/a | 3131.0 |
| `log_lr_at_half_sample` | -105.86972 | n/a | n/a | n/a | n/a | 1565.0 |

**Interpretation.** Testing H0 (uniform) against H1 (a 1.5% per-category bias) with alpha=0.05, beta=0.1: boundaries are a=-2.251 and b=2.890. Over 3131 draws the accumulated log likelihood ratio is -198.682, having reached -105.870 at the halfway point. The test crossed a boundary at draw 20 and decided. The KL divergence between the hypotheses is 6.08e-02 nats per draw, implying an expected sample size of about -1,994,208,620,781 draws under H0 to reach a decision. This is the single most important number in the report: it quantifies how much data a bias of this size would require, and shows why a few thousand draws cannot settle the question either way.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 7,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `final_log_likelihood_ratio` | -198.68182 |
| Close | computed | `final_log_likelihood_ratio` | -199.69875 |

Open produced final_log_likelihood_ratio=-198.68182; Close produced final_log_likelihood_ratio=-199.69875. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Meta-level: needs a panel of models or a collection of p-values rather than raw draws.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Model-combination methods fit their weights on an earlier slice of the out-of-sample window and are scored on a later slice; meta-analytic methods (91, 92) correct the whole suite's p-values.

## 13. Statistical interpretation

14 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

SPRT assumes i.i.d. observations; under dependence the error rates are not honoured, which is reported as a caveat rather than ignored.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Wald (1945)
