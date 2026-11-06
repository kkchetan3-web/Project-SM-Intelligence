# M030 - Partial Autocorrelation

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_030`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\phi_{kk} = \mathrm{corr}(x_t, x_{t-k} \mid x_{t-1},\ldots,x_{t-k+1})`

---

## 1. Definition and mathematical foundation

The PACF isolates the direct contribution of lag k by removing the intermediate lags. For a first-order Markov process the theoretical PACF is zero beyond lag 1; a non-zero value at lag 2 is therefore evidence of genuine second-order structure rather than inherited dependence.

## 2. Objective

Identify lags that carry direct rather than mediated information.

## 3. Complete formula

```
\phi_{kk} = \mathrm{corr}(x_t, x_{t-k} \mid x_{t-1},\ldots,x_{t-k+1})
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `phi_kk` | partial autocorrelation at lag k |
| `k` | lag |

## 5. Statistical assumptions

- The series is stationary
- The AR representation is adequate

## 6. Required input data

A few hundred observations.

## 7. Step-by-step manual calculation

1. Compute the ACF
2. Solve the Yule-Walker recursion to obtain partial autocorrelations
3. Compare with a permutation band

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

No worked example is defined for this category.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `pacf_lag1` | 0.01408 | n/a | n/a | n/a | n/a | 3131.0 |
| `pacf_lag2` | 0.02114 | n/a | n/a | n/a | n/a | 3131.0 |
| `max_abs_pacf_beyond_lag1` | 0.05087 | n/a | n/a | n/a | n/a | 3131.0 |
| `permutation_95pct_band` | 0.04969 | n/a | n/a | n/a | n/a | 3131.0 |
| `n_significant_lags` | 1.00000 | n/a | n/a | n/a | n/a | 15.0 |

**Interpretation.** Partial autocorrelation at lag 1 is +0.0141; beyond lag 1 the largest is +0.0509, against a permutation band of 0.0497. 1 lags exceed the band ([3]). A first-order Markov process has non-zero PACF at lag 1 only; direct information at higher lags would indicate longer memory.

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
| `pacf_lag1` | -0.01350 | n/a | n/a | n/a | n/a | 3131.0 |
| `pacf_lag2` | -0.00369 | n/a | n/a | n/a | n/a | 3131.0 |
| `max_abs_pacf_beyond_lag1` | 0.03605 | n/a | n/a | n/a | n/a | 3131.0 |
| `permutation_95pct_band` | 0.05020 | n/a | n/a | n/a | n/a | 3131.0 |
| `n_significant_lags` | 0.00000 | n/a | n/a | n/a | n/a | 15.0 |

**Interpretation.** Partial autocorrelation at lag 1 is -0.0135; beyond lag 1 the largest is +0.0360, against a permutation band of 0.0502. 0 lags exceed the band. A first-order Markov process has non-zero PACF at lag 1 only; direct information at higher lags would indicate longer memory.

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
| Open | computed | `pacf_lag1` | -0.01350 |
| Close | computed | `pacf_lag1` | 0.01408 |

Open produced pacf_lag1=-0.01350; Close produced pacf_lag1=0.01408. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

The most transferable category across markets, since it needs only a sequence. Data hunger grows sharply with order (K^order contexts).

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Transition-based methods are scored by walk-forward log loss against the expanding frequency baseline, which is the only comparison that answers 'does history help'.

## 13. Statistical interpretation

10 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

PACF assumes a linear autoregressive structure; categorical dependence may be entirely invisible to it.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
