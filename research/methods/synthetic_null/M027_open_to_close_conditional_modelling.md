# M027 - Open-to-Close Conditional Modelling

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_027`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(C_t = c \mid O_t = o)`

---

## 1. Definition and mathematical foundation

In these markets the same day's Open is announced before the Close, so it is the one same-day variable that is legitimately available to a Close forecast. The joint distribution of (Open, Close) on the same day either factorises or it does not; if it does, the Open carries exactly zero information about the Close.

## 2. Objective

Test whether the same-day Open predicts the Close, and quantify any gain out of sample.

## 3. Complete formula

```
P(C_t = c \mid O_t = o)
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `O_t` | same-day open outcome |
| `C_t` | same-day close outcome |
| `mutual information` | dependence in bits |

## 5. Statistical assumptions

- Publication order really does put Open before Close
- Same-day pairing is exact (no date shifting)

## 6. Required input data

Several hundred paired observations.

## 7. Step-by-step manual calculation

1. Join each date's Open and Close
2. Build the 10x10 contingency table
3. Test independence and compare a Close model with and without the Open feature

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

No worked example is defined for this category.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `joint_chi2` | 60.36994 | 60.36994 | 0.95817 | 0.98154 | 0.04629 | 3131.0 |
| `mutual_information_bits` | 0.01413 | n/a | 0.94667 | 0.98154 | n/a | 3131.0 |
| `cramers_v` | 0.04629 | n/a | n/a | n/a | n/a | 3131.0 |
| `frequency_ll` | 2.30508 | n/a | n/a | n/a | n/a | 2505.0 |
| `open_conditional_ll` | 2.33339 | n/a | n/a | n/a | n/a | 2505.0 |
| `ll_improvement_from_open` | -0.02831 | n/a | n/a | n/a | n/a | 2505.0 |

**Interpretation.** Across 3131 same-day pairs the Open-Close contingency table gives chi-square 60.37 (p = 0.9582, V = 0.0463) and mutual information 0.01413 bits (permutation p = 0.947). Out of sample, a Close model conditioned on the same-day Open scores 2.33339 against 2.30508 for unconditional frequency, an improvement of -0.02831. The Open carries no usable information about the Close: the joint distribution is consistent with independence.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 6,
  "dataset": "synthetic_null"
}
```
</details>

### OPEN

**Not applicable** to this data (the required component is absent).

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `no_metric` | n/a | n/a | n/a | n/a | n/a | nan |

**Interpretation.** The same-day Close is published after the Open, so it cannot be a predictor of the Open. This method is evaluated in the Close context, where the Open is legitimately available.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 1,
  "dataset": "synthetic_null"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | not_applicable | `no_metric` | n/a |
| Close | computed | `joint_chi2` | 60.36994 |

Open produced no_metric=n/a; Close produced joint_chi2=60.36994. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

The most transferable category across markets, since it needs only a sequence. Data hunger grows sharply with order (K^order contexts).

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Transition-based methods are scored by walk-forward log loss against the expanding frequency baseline, which is the only comparison that answers 'does history help'.

## 13. Statistical interpretation

6 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

If publication times are unavailable the pairing may be wrong; the platform records that assumption explicitly.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
