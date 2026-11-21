# M028 - Cross-Correlation Analysis

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_028`  
**Data source:** `synthetic_signal` - H1 control: planted first-order Markov dependence. Framework must DETECT edge. Market: kalyan. Synthetic control data; not real market history.  
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
| `cramers_v_lag-3` | 0.05110 | n/a | 0.70986 | 0.79579 | n/a | 3128.0 |
| `cramers_v_lag-2` | 0.05100 | n/a | 0.71976 | 0.79579 | n/a | 3129.0 |
| `cramers_v_lag-1` | 0.04720 | n/a | 0.93485 | 0.99401 | n/a | 3130.0 |
| `cramers_v_lag0` | 0.05560 | n/a | 0.29893 | 0.46202 | n/a | 3131.0 |
| `cramers_v_lag1` | 0.05270 | n/a | 0.56398 | 0.68658 | n/a | 3130.0 |
| `cramers_v_lag2` | 0.05130 | n/a | 0.69470 | 0.79579 | n/a | 3129.0 |
| `cramers_v_lag3` | 0.05300 | n/a | 0.53941 | 0.67628 | n/a | 3128.0 |
| `best_lag` | 0.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `best_cramers_v` | 0.05560 | n/a | 1.00000 | 1.00000 | n/a | 3131.0 |
| `n_lags_significant_holm` | 0.00000 | n/a | n/a | n/a | n/a | 7.0 |

**Interpretation.** Categorical association between kalyan close and main_bazar close over 3131 common dates, tested at lags [-3, -2, -1, 0, 1, 2, 3]: lag -3: V=0.0511, lag -2: V=0.0510, lag -1: V=0.0472, lag 0: V=0.0556, lag 1: V=0.0527, lag 2: V=0.0513, lag 3: V=0.0530. The strongest lag is 0 with V = 0.0556 (Holm-adjusted p = 1.0000); 0 of 7 lags survive Holm correction. Note that the zero lag is not automatically admissible for prediction - see the availability rules in the cross-market module.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 10,
  "dataset": "synthetic_signal"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `cramers_v_lag-3` | 0.05240 | n/a | 0.59910 | 0.80535 | n/a | 3128.0 |
| `cramers_v_lag-2` | 0.05250 | n/a | 0.58440 | 0.79868 | n/a | 3129.0 |
| `cramers_v_lag-1` | 0.04550 | n/a | 0.97337 | 1.00000 | n/a | 3130.0 |
| `cramers_v_lag0` | 0.05320 | n/a | 0.51754 | 0.73170 | n/a | 3131.0 |
| `cramers_v_lag1` | 0.05710 | n/a | 0.19043 | 0.36314 | n/a | 3130.0 |
| `cramers_v_lag2` | 0.05160 | n/a | 0.66625 | 0.86718 | n/a | 3129.0 |
| `cramers_v_lag3` | 0.04990 | n/a | 0.80249 | 0.99704 | n/a | 3128.0 |
| `best_lag` | 1.00000 | n/a | n/a | n/a | n/a | 3130.0 |
| `best_cramers_v` | 0.05710 | n/a | 1.00000 | 1.00000 | n/a | 3130.0 |
| `n_lags_significant_holm` | 0.00000 | n/a | n/a | n/a | n/a | 7.0 |

**Interpretation.** Categorical association between kalyan open and main_bazar open over 3131 common dates, tested at lags [-3, -2, -1, 0, 1, 2, 3]: lag -3: V=0.0524, lag -2: V=0.0525, lag -1: V=0.0455, lag 0: V=0.0532, lag 1: V=0.0571, lag 2: V=0.0516, lag 3: V=0.0499. The strongest lag is 1 with V = 0.0571 (Holm-adjusted p = 1.0000); 0 of 7 lags survive Holm correction. Note that the zero lag is not automatically admissible for prediction - see the availability rules in the cross-market module.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 10,
  "dataset": "synthetic_signal"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `cramers_v_lag-3` | 0.05240 |
| Close | computed | `cramers_v_lag-3` | 0.05110 |

Open produced cramers_v_lag-3=0.05240; Close produced cramers_v_lag-3=0.05110. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

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
