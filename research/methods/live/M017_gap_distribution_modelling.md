# M017 - Gap Distribution Modelling

**Category:** B - Recency and Occurrence  
**Implementation:** `src.mathematics.recurrence::run_017`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(G=g) = (1-p)^{g-1}p \quad\text{(geometric)}`

---

## 1. Definition and mathematical foundation

Fitting a parametric waiting-time model makes the i.i.d. assumption testable: the geometric distribution is a sharp prediction of independence, and departures from it - a heavier tail or an excess of very short gaps - indicate clustering or avoidance that a plain frequency analysis cannot see.

## 2. Objective

Fit geometric and negative-binomial waiting-time models and compare their fit.

## 3. Complete formula

```
P(G=g) = (1-p)^{g-1}p \quad\text{(geometric)}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `p` | geometric success probability |
| `NB` | negative binomial over-dispersion parameter |
| `AIC` | information criterion for model comparison |

## 5. Statistical assumptions

- Waiting times are modelled as discrete
- A single parametric family describes the whole sample

## 6. Required input data

Enough occurrences for the histogram to be non-degenerate.

## 7. Step-by-step manual calculation

1. Build empirical gap histograms per category
2. Fit geometric and negative binomial models
3. Compare by AIC and by the predicted probability of the next gap

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

With p = 0.4 for outcome 3 the geometric hazard is h(t) = 0.4 for every t, the survival function is S(t) = 0.6^t (S(1)=0.600, S(2)=0.360, S(3)=0.216), and the expected wait is 1/0.4 = 2.5 draws. A constant hazard is the precise statement of 'waiting does not matter'.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `geometric_loglik` | -1451.51119 | n/a | n/a | n/a | n/a | 464.0 |
| `geometric_aic` | 2905.02237 | n/a | n/a | n/a | n/a | 464.0 |
| `negative_binomial_aic` | 2973.01536 | n/a | n/a | n/a | n/a | 464.0 |
| `aic_difference_nb_minus_geom` | 67.99299 | n/a | n/a | n/a | n/a | 464.0 |
| `ks_p_value_geometric` | 1.494e-05 | n/a | 1.494e-05 | n/a | n/a | 464.0 |
| `observed_variance_to_mean` | 7.29545 | n/a | n/a | n/a | n/a | 464.0 |

**Interpretation.** For 1 (464 observed gaps) the geometric fit has log-likelihood -1451.51 and AIC 2905.02; the negative binomial has AIC 2973.02. AIC difference of +67.99 favours the simpler geometric model, i.e. memorylessness fits at least as well as an over-dispersed alternative. The variance-to-mean ratio is 7.295 (geometric predicts 0.888), and the Kolmogorov-Smirnov p-value against the geometric is 0.0000.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `geometric_loglik` | -1419.53195 | n/a | n/a | n/a | n/a | 449.0 |
| `geometric_aic` | 2841.06390 | n/a | n/a | n/a | n/a | 449.0 |
| `negative_binomial_aic` | 2914.12511 | n/a | n/a | n/a | n/a | 449.0 |
| `aic_difference_nb_minus_geom` | 73.06121 | n/a | n/a | n/a | n/a | 449.0 |
| `ks_p_value_geometric` | 4.376e-05 | n/a | 4.376e-05 | n/a | n/a | 449.0 |
| `observed_variance_to_mean` | 8.38390 | n/a | n/a | n/a | n/a | 449.0 |

**Interpretation.** For 9 (449 observed gaps) the geometric fit has log-likelihood -1419.53 and AIC 2841.06; the negative binomial has AIC 2914.13. AIC difference of +73.06 favours the simpler geometric model, i.e. memorylessness fits at least as well as an over-dispersed alternative. The variance-to-mean ratio is 8.384 (geometric predicts 0.891), and the Kolmogorov-Smirnov p-value against the geometric is 0.0000.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `geometric_loglik` | -1419.53195 |
| Close | computed | `geometric_loglik` | -1451.51119 |

Open produced geometric_loglik=-1419.53195; Close produced geometric_loglik=-1451.51119. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Suited to markets with long continuous histories; it degrades when the calendar has many gaps, because 'missing' and 'not drawn' become hard to separate.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Predictive claims are limited to what a causal forecast can show: hot/cold persistence is measured between two disjoint periods, and hazard/recency tests compare against a permutation or geometric null.

## 13. Statistical interpretation

12 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Over-dispersion relative to geometric has many causes besides dependence, including non-stationarity.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
