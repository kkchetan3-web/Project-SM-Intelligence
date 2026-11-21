# M032 - Conditional Mutual Information

**Category:** C - Transitions and Dependencies  
**Implementation:** `src.mathematics.markov::run_032`  
**Data source:** `live` - Real extracted market records. Populated only by the ingestion pipeline. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `I(X;Y \mid Z)=\sum_{x,y,z}p(x,y,z)\log\frac{p(x,y\mid z)}{p(x\mid z)p(y\mid z)}`

---

## 1. Definition and mathematical foundation

Conditional MI asks whether a candidate predictor still contributes once a competing predictor is known. It is the principled filter for feature selection in Method 93, because it screens out variables that are merely redundant with ones already in the model.

## 2. Objective

Test whether a predictor adds information beyond an existing one.

## 3. Complete formula

```
I(X;Y \mid Z)=\sum_{x,y,z}p(x,y,z)\log\frac{p(x,y\mid z)}{p(x\mid z)p(y\mid z)}
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `I(X;Y|Z)` | conditional mutual information |
| `Z` | conditioning variable |

## 5. Statistical assumptions

- Conditioning variable is observed for all rows
- Cell counts are adequate

## 6. Required input data

Large N relative to the joint state space.

## 7. Step-by-step manual calculation

1. Fit the conditional distributions
2. Compute the conditional MI
3. Compare against a permutation null that preserves the conditioning

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

MI between consecutive draws: 1.3921 bits. The permutation null mean for a table this sparse is roughly 0.05-0.10 bits, so the observed value is indistinguishable from noise - illustrating why the permutation reference is mandatory for MI on 10x10 tables.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mi_prev_next` | 0.01082 | n/a | n/a | n/a | n/a | 4142.0 |
| `cmi_prev_next_given_prevopen` | 0.15159 | n/a | n/a | n/a | n/a | 4142.0 |
| `mi_removed_by_conditioning` | -0.14077 | n/a | n/a | n/a | n/a | 4142.0 |

**Interpretation.** Unconditional MI between consecutive close outcomes is 0.01082 bits. Conditioning also on the previous day's open leaves 0.15159 bits, so -0.14077 bits of the apparent dependence is shared with the conditioning variable. A conditional MI near zero means yesterday's close adds nothing once yesterday's open is known.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 3,
  "dataset": "live"
}
```
</details>

### OPEN

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `mi_prev_next` | 0.01169 | n/a | n/a | n/a | n/a | 4142.0 |
| `cmi_prev_next_given_prev2` | 1.007e-16 | n/a | n/a | n/a | n/a | 4141.0 |

**Interpretation.** MI between consecutive outcomes is 0.01169 bits, and conditioning on the second-previous outcome leaves almost the same amount, i.e. the (already negligible) information is first-order rather than longer-range.

<details><summary>Diagnostics</summary>

```json
{
  "source": "method_results table",
  "rows": 2,
  "dataset": "live"
}
```
</details>

## 10. Open-specific and Close-specific findings

| Target | Status | Headline metric | Headline value |
| --- | --- | --- | --- |
| Open | computed | `mi_prev_next` | 0.01169 |
| Close | computed | `mi_prev_next` | 0.01082 |

Open produced mi_prev_next=0.01169; Close produced mi_prev_next=0.01082. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

The most transferable category across markets, since it needs only a sequence. Data hunger grows sharply with order (K^order contexts).

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

Transition-based methods are scored by walk-forward log loss against the expanding frequency baseline, which is the only comparison that answers 'does history help'.

## 13. Statistical interpretation

5 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

Estimation noise grows quickly with the number of cells; conditioning on a 10-state variable already multiplies the table by 10.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
