# M022 - Change-Point Detection

**Category:** B - Recency and Occurrence  
**Implementation:** `src.mathematics.recurrence::run_022`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `S_t = \max\left(0, S_{t-1} + (X_t - \mu_0)\right)`

---

## 1. Definition and mathematical foundation

A change point is a time at which the data-generating distribution changes. CUSUM accumulates deviations from a reference mean and alarms when the accumulation exceeds a threshold; binary segmentation applies the same idea recursively. For these markets the interesting question is whether any detected structural break is followed by a genuinely different distribution.

## 2. Objective

Detect candidate structural breaks and evaluate their consequences.

## 3. Complete formula

```
S_t = \max\left(0, S_{t-1} + (X_t - \mu_0)\right)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `S_t` | CUSUM statistic |
| `mu_0` | reference level |
| `threshold` | alarm level |
| `break` | estimated change location |

## 5. Statistical assumptions

- The pre-break and post-break segments are internally homogeneous
- The reference distribution is correctly specified

## 6. Required input data

Several hundred observations on each side of a candidate break.

## 7. Step-by-step manual calculation

1. Build an indicator series for the outcome of interest
2. Run CUSUM and record alarm times
3. Validate each candidate break by comparing pre- and post-segment distributions

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Standardised count for outcome 3: z = (4 - 1)/sqrt(10 x 0.1 x 0.9) = 3/0.9487 = 3.162. On ten draws a z of 3 is entirely ordinary; the persistence test needs two long periods, not ten draws.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `n_candidate_breaks` | 1.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `n_validated_breaks` | 0.00000 | n/a | n/a | n/a | n/a | 1.0 |
| `best_split_statistic` | 10.49995 | n/a | 0.33663 | 0.60465 | n/a | 4143.0 |
| `split_permutation_p` | 0.33663 | n/a | 0.33663 | 0.60465 | n/a | 100.0 |

**Interpretation.** CUSUM flagged 1 candidate break locations at a 2.5-sigma threshold. Comparing the 500 draws either side of each, 0 of 1 show a significant distributional change. An independent single-split likelihood-ratio search puts the best break at index 1703 (2018-08-28) with statistic 10.50, and a 100-shuffle permutation gives p = 0.337. The apparent breaks are consistent with sampling variation: no structural change is established.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `n_candidate_breaks` | 8.00000 | n/a | n/a | n/a | n/a | 4143.0 |
| `n_validated_breaks` | 0.00000 | n/a | n/a | n/a | n/a | 8.0 |
| `best_split_statistic` | 13.05296 | n/a | 0.13861 | 0.32325 | n/a | 4143.0 |
| `split_permutation_p` | 0.13861 | n/a | 0.13861 | 0.32325 | n/a | 100.0 |

**Interpretation.** CUSUM flagged 8 candidate break locations at a 2.5-sigma threshold. Comparing the 500 draws either side of each, 0 of 8 show a significant distributional change. An independent single-split likelihood-ratio search puts the best break at index 2328 (2020-11-05) with statistic 13.05, and a 100-shuffle permutation gives p = 0.139. The apparent breaks are consistent with sampling variation: no structural change is established.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 4,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `n_candidate_breaks` | 8.00000 |
| Close | computed | `n_candidate_breaks` | 1.00000 |

Open produced n_candidate_breaks=8.00000; Close produced n_candidate_breaks=1.00000. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Suited to markets with long continuous histories; it degrades when the calendar has many gaps, because 'missing' and 'not drawn' become hard to separate.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Predictive claims are limited to what a causal forecast can show: hot/cold persistence is measured between two disjoint periods, and hazard/recency tests compare against a permutation or geometric null.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

CUSUM is sensitive to gradual drift, not only to sharp breaks, and with many categories it generates alarms readily. Multiple testing across categories must be corrected.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.

## References

Page (1954)
