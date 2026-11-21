# M028 - Cross-Correlation Analysis

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_028`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `\rho(k) = \mathrm{corr}(X_t, Y_{t-k})`

---

## 1. Definition and mathematical foundation

Pearson correlation is meaningless for nominal categories, so this implementation uses Cramer's V on the lagged contingency table, which is the categorical analogue. Testing many lags across many market pairs creates a large multiple-testing problem that must be corrected.

## 2. Objective

Measure lagged association between markets with a categorical-appropriate statistic.

## 3. Complete formula

```
\rho(k) = \mathrm{corr}(X_t, Y_{t-k})
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `rho(k)` | association at lag k |
| `V` | Cramer's V |
| `k` | lag in observations |

## 5. Statistical assumptions

- Lagged pairs are correctly time-aligned
- Observations are independent across pairs

## 6. Required input data

Adequate overlap of calendars between the two markets.

## 7. Step-by-step manual calculation

1. Align the two markets on shared dates
2. For each lag build the contingency table
3. Compute V and a chi-square p-value, then correct across lags

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

MI between consecutive draws: 1.3921 bits. The permutation null mean for a table this sparse is roughly 0.05-0.10 bits, so the observed value is indistinguishable from noise - illustrating why the permutation reference is mandatory for MI on 10x10 tables.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `cramers_v_lag-3` | 0.06080 | n/a | 0.27929 | 0.54559 | n/a | 2646.0 |
| `cramers_v_lag-2` | 0.05570 | n/a | 0.69913 | 0.93106 | n/a | 2647.0 |
| `cramers_v_lag-1` | 0.05770 | n/a | 0.53313 | 0.79549 | n/a | 2648.0 |
| `cramers_v_lag0` | 0.06650 | n/a | 0.03506 | 0.26771 | n/a | 2649.0 |
| `cramers_v_lag1` | 0.05180 | n/a | 0.91812 | 1.00000 | n/a | 2648.0 |
| `cramers_v_lag2` | 0.06160 | n/a | 0.22184 | 0.52855 | n/a | 2647.0 |
| `cramers_v_lag3` | 0.06180 | n/a | 0.20796 | 0.52855 | n/a | 2646.0 |
| `best_lag` | 0.00000 | n/a | n/a | n/a | n/a | 2649.0 |
| `best_cramers_v` | 0.06650 | n/a | 0.24540 | 0.52855 | n/a | 2649.0 |
| `n_lags_significant_holm` | 0.00000 | n/a | n/a | n/a | n/a | 7.0 |

**Interpretation.** Categorical association between kalyan close and main_bazar close over 2649 common dates, tested at lags [-3, -2, -1, 0, 1, 2, 3]: lag -3: V=0.0608, lag -2: V=0.0557, lag -1: V=0.0577, lag 0: V=0.0665, lag 1: V=0.0518, lag 2: V=0.0616, lag 3: V=0.0618. The strongest lag is 0 with V = 0.0665 (Holm-adjusted p = 0.2454); 0 of 7 lags survive Holm correction. Note that the zero lag is not automatically admissible for prediction - see the availability rules in the cross-market module.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 10,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `cramers_v_lag-3` | 0.05400 | n/a | 0.81751 | 0.94779 | n/a | 2646.0 |
| `cramers_v_lag-2` | 0.05280 | n/a | 0.87892 | 0.94779 | n/a | 2647.0 |
| `cramers_v_lag-1` | 0.05540 | n/a | 0.72351 | 0.89890 | n/a | 2648.0 |
| `cramers_v_lag0` | 0.05260 | n/a | 0.88770 | 0.94779 | n/a | 2649.0 |
| `cramers_v_lag1` | 0.05850 | n/a | 0.46442 | 0.72564 | n/a | 2648.0 |
| `cramers_v_lag2` | 0.05830 | n/a | 0.48192 | 0.72564 | n/a | 2647.0 |
| `cramers_v_lag3` | 0.05800 | n/a | 0.50441 | 0.72564 | n/a | 2646.0 |
| `best_lag` | 1.00000 | n/a | n/a | n/a | n/a | 2648.0 |
| `best_cramers_v` | 0.05850 | n/a | 1.00000 | 1.00000 | n/a | 2648.0 |
| `n_lags_significant_holm` | 0.00000 | n/a | n/a | n/a | n/a | 7.0 |

**Interpretation.** Categorical association between kalyan open and main_bazar open over 2649 common dates, tested at lags [-3, -2, -1, 0, 1, 2, 3]: lag -3: V=0.0540, lag -2: V=0.0528, lag -1: V=0.0554, lag 0: V=0.0526, lag 1: V=0.0585, lag 2: V=0.0583, lag 3: V=0.0580. The strongest lag is 1 with V = 0.0585 (Holm-adjusted p = 1.0000); 0 of 7 lags survive Holm correction. Note that the zero lag is not automatically admissible for prediction - see the availability rules in the cross-market module.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 10,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `cramers_v_lag-3` | 0.05400 |
| Close | computed | `cramers_v_lag-3` | 0.06080 |

Open produced cramers_v_lag-3=0.05400; Close produced cramers_v_lag-3=0.06080. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

The most transferable category across markets, since it needs only a sequence. Data hunger grows sharply with order (K^order contexts).

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Transition-based methods are scored by walk-forward log loss against the expanding frequency baseline, which is the only comparison that answers 'does history help'.

## 13. Statistical interpretation

20 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Association at any lag does not establish causation, and with enough lags some association appears by construction.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
