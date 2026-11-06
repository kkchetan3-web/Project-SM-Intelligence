# M053 - Parity Analysis

**Category:** E - Number Theory and Transformations  
**Implementation:** `src.mathematics.number_theory::run_053`  
**Data source:** `synthetic_null` - H0 control: i.i.d. uniform draws. Framework must report NO predictive edge. Market: kalyan. Synthetic control data; not real market history.  
**Formula:** `P(\text{even}) = \sum_{k \text{ even}} p_k`

---

## 1. Definition and mathematical foundation

Parity is the coarsest non-trivial partition of a digit space and therefore the most statistically powerful: pooling five categories per side gives large expected counts even in short samples. It is also the natural first target for a binary classifier.

## 2. Objective

Test the even/odd balance and the persistence of any imbalance.

## 3. Complete formula

```
P(\text{even}) = \sum_{k \text{ even}} p_k
```

## 4. Explanation of every variable

| Symbol | Meaning |
| --- | --- |
| `p_even` | probability of an even outcome |
| `n_even` | count of even outcomes |

## 5. Statistical assumptions

- Parity is a deterministic function of the outcome
- Even and odd classes partition the space

## 6. Required input data

Any non-empty sample.

## 7. Step-by-step manual calculation

1. Map each outcome to its parity
2. Test the proportion against 0.5
3. Test run structure and persistence separately

## 8. Worked numerical example (hypothetical)

> Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), ten draws over the outcome space 0-9.

Even values in the toy sequence: 2 of 10 (0, 2 are even; 3, 1, 7, 9, 3, 3, 3 are odd). Primes among the observed values: 3, 3, 7, 3, 3, 2, 3 - seven of ten, which is unremarkable on ten draws but illustrates how coarse a partition this is.

## 9. Actual computation on the market database

### CLOSE

**Computed** on the market database.

| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |
| --- | --- | --- | --- | --- | --- | --- |
| `even_proportion` | 0.49090 | n/a | 0.31692 | 0.85225 | n/a | 3131.0 |
| `observed_runs` | 1510.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `expected_runs` | 1565.98116 | n/a | n/a | n/a | n/a | 3131.0 |
| `runs_z_statistic` | -2.00191 | n/a | 0.04529 | 0.72772 | n/a | 3131.0 |

**Interpretation.** Even outcomes make up 0.4909 of the sample (exact 95% CI 0.4732 to 0.5086); the binomial test against 0.5 gives p = 0.3169. The parity sequence contains 1510 runs against 1566.0 expected (z = -2.002, p = 0.0453). Parity departs from the 50/50 expectation or shows clustering; the two tests are separate pieces of evidence and must be corrected for multiplicity before being called a finding.

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
| `even_proportion` | 0.48579 | n/a | 0.11578 | 0.83640 | n/a | 3131.0 |
| `observed_runs` | 1576.00000 | n/a | n/a | n/a | n/a | 3131.0 |
| `expected_runs` | 1565.23507 | n/a | n/a | n/a | n/a | 3131.0 |
| `runs_z_statistic` | 0.38514 | n/a | 0.70013 | 0.94116 | n/a | 3131.0 |

**Interpretation.** Even outcomes make up 0.4858 of the sample (exact 95% CI 0.4681 to 0.5035); the binomial test against 0.5 gives p = 0.1158. The parity sequence contains 1576 runs against 1565.2 expected (z = +0.385, p = 0.7001). Parity is balanced and the run structure is consistent with independence.

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
| Open | computed | `even_proportion` | 0.48579 |
| Close | computed | `even_proportion` | 0.49090 |

Open produced even_proportion=0.48579; Close produced even_proportion=0.49090. The two targets are analysed on separate feature sets and separate models, so a difference between them is a difference in the data, not in the pipeline. Where the Open and Close results diverge materially, the dossier records both rather than averaging them.

## 11. Market-specific suitability

Panel-level methods need the 3-digit panna to be published; where a market reports only the ank, the method is reported as not applicable rather than approximated.

## 12. Historical stability, backtesting methodology and predictive metrics

Every predictive claim in this record comes from a strictly chronological walk-forward: the first 25-40% of each market's history (minimum 400 observations) is reserved for estimation, and each prediction is made from data strictly preceding its target date, with a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match and top-k accuracy, expected calibration error and the calibration slope. Comparisons against baselines use a paired moving-block bootstrap so that serial dependence is not mistaken for significance.

These tests are distributional rather than predictive, and their p-values feed the multiple-testing correction across the whole suite.

## 13. Statistical interpretation

8 p-values were produced across the computed targets; 0 survive Benjamini-Hochberg control at q=0.05. A result that does not survive correction across the 100-method family should not be interpreted as evidence of structure. The distinction this platform enforces is between a *statistically detectable* deviation and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; they are useful only if a causal forecast beats the baseline out of sample. The evidence above is read that way.

## 14. Limitations

A significant imbalance over years is more likely to indicate a biased mechanism or a data artefact than an exploitable edge.

## 15. Final research conclusion

No predictive information was demonstrated. Where the method produced a statistically notable statistic, it did not survive multiple-testing correction or did not translate into out-of-sample log-loss improvement. The honest conclusion for this method is a negative result, which is recorded as such rather than minimised.
