# Design decisions and the reasoning behind them

Short records of the choices that shaped the platform, including the ones that make it
report *less* than it could. Where a decision restricts what the software will claim, the
restriction is deliberate.

---

## 1. Synthetic control worlds instead of "best effort" data

**Decision.** Ship two generated datasets with known ground truth rather than any
substitute for real market history.

**Why.** The sources were unreachable (see `DATA_SOURCES.md`). The available options were
(a) stop, (b) fabricate plausible-looking history, (c) research the framework itself on data
whose truth is known. Option (b) is indefensible. Option (c) answers a real question: *does
this pipeline find structure when structure exists, and stay silent when it does not?*

**Consequence.** Every report says "synthetic control" and every row carries
`synthetic_status`. `assert_dataset_isolation` makes it a hard error to store a
synthetic-status row in the live tree, or a live-status row in a synthetic tree.

---

## 2. One database per market, even though one database would be easier

**Decision.** `data/databases/<market_id>/<market_id>.db`, one file per market.

**Why.** A single table keyed by market invites every query to forget the market filter.
Separate files make cross-market contamination a file-system impossibility rather than a
`WHERE` clause that someone will eventually omit. It also lets each market be backed up,
migrated and audited independently, and lets a market be added without touching another's
data.

**Consequence.** Cross-market tests are written twice, once into each market's file. That
duplication is the price of market isolation and is worth paying.

---

## 3. Status objects instead of numbers that always exist

**Decision.** A method returns `computed`, `not_applicable`, `insufficient_data`,
`dependency_unavailable` or `failed`. Only `computed` carries findings, and every finding
carries its sample size.

**Why.** The alternative — returning `0.0` when a test cannot run — makes an untested
hypothesis indistinguishable from a tested-and-negative one. That single confusion is
behind most of the misleading "quant" content in this problem domain.

**Consequence.** Dashboards look emptier than they otherwise would. That is the point.

---

## 4. Baselines first, promotion rule second, forecasting third

**Decision.** Seven naive baselines are computed for every market/target. A model is only
used for forecasting if it beats the *best* baseline by ≥ 0.002 log loss with a bootstrap CI
excluding zero, wins in more than half the folds, and is calibrated (slope 0.80–1.25).

**Why.** In this problem the null is overwhelmingly likely to be true: five independent
uniform digits. A framework that reports a model merely because it is better than uniform,
or better by 0.0001, is producing noise marketing. And a forecast must never be silently
downgraded — if nothing is promoted the forecast says `baseline_fallback` and states that
no edge was demonstrated.

**Consequence.** No model was promoted on any market, target or dataset. Every forecast in
the repository is a labelled baseline.

---

## 5. Same-day foreign values are inadmissible by default

**Decision.** Cross-market features use lag ≥ 1. One exception exists, declared in
`config/markets.yaml` as `cross_open_precedence: [["kalyan", "main_bazar"]]`, meaning
Kalyan's Open is treated as published before Main Bazar's Close.

**Why.** The tempting cross-market feature — "what did the other market do today?" — is
almost always published *after* the target it would be used to predict. Scraped chart pages
carry no publication timestamps, so using same-day foreign values is an unverifiable
assumption dressed up as a feature. Lag ≥ 1 is safe without any assumption.

The one exception is kept because the Open/Close ordering within a day is a documented
property of these markets, and Kalyan draws materially earlier than the night markets. It is
declared in configuration rather than hard-coded, recorded in every feature frame
(`same_day_foreign_open_used`), covered by a test that removing the declaration removes the
channel, and reported separately from the lagged features.

**Consequence on the signal world.** The planted Kalyan→Main Bazar effect is a *same-day*
channel. Without the declaration it is invisible to the model; with it, the conditional-model
test detects a real out-of-sample improvement. Both results are reported, which is exactly
the kind of statement the declaration exists to make auditable.

---

## 6. Walk-forward with a refit schedule, not cross-validation

**Decision.** Expanding-window walk-forward, refit every 80–160 steps depending on model
cost, evaluation strictly after `min_train`.

**Why.** Random k-fold cross-validation on a time series leaks the future into the training
set and inflates every metric. Expanding-window walk-forward reproduces the only evaluation
that matters: what could have been known at the time.

`verify_causality` additionally rebuilds the feature matrix on truncated history and asserts
the prefix is bit-identical — an empirical leak test rather than a code-review promise.

---

## 7. Block bootstrap for every comparison

**Decision.** Paired moving-block bootstrap (block = 5) for the CI of a metric difference;
never a paired t-test on per-observation losses.

**Why.** Consecutive draws are not independent under the alternative hypothesis (persistence
is exactly what is being tested). An i.i.d. bootstrap would understate the variance and
manufacture significance precisely when the effect is strongest.

---

## 8. Benjamini–Hochberg across the whole sweep

**Decision.** All p-values produced by the 100 methods are collected, then FDR-adjusted
together (alpha from `config/research.yaml`), and stored in `method_results.p_adjusted`.

**Why.** One hundred methods × two targets × two markets is thousands of tests. At α = 0.05
roughly 5% will be "significant" by construction. Holm and Bonferroni variants are also
implemented (M091/M092) so the sensitivity of any conclusion to the correction method is
visible.

---

## 9. Features are built once, in one place

**Decision.** `build_features` is the single source of the feature matrix for training,
backtesting and the *next-draw forecast row*. The forecast row is produced by appending a
sentinel to the history and reading the last row.

**Why.** Two code paths for "features now" and "features in training" drift, and the drift
always takes the form of the forecast path quietly using something the training path never
saw — or the reverse. A single path with a sentinel makes column mismatch impossible and
makes the leak test meaningful.

Channels that are not yet published at forecast time (the same-day Open, a foreign same-day
Open) are **removed from the whole matrix**, not imputed, so training and inference stay
consistent.

---

## 10. Reporting is generated, not written

**Decision.** `src/reporting/report.py` and `scripts/summarise_results.py` build the report
from database contents.

**Why.** Hand-written results drift from the data the moment anything is re-run, and prose
is where an unverified claim survives longest. Generated tables cannot say "all 100 methods
improved performance" unless the rows say so.

**Consequence.** Sections whose data is absent render as "not executed", with the reason.

---

## 11. Errors are recorded, not swallowed

**Decision.** No bare `except: continue` in the walk-forward loop. Model failures are
collected in `panel.errors`; method failures are recorded as `failed` with the exception
text; a NaN feature matrix raises rather than being silently imputed into a uniform
forecast.

**Why.** An earlier iteration converted a NaN column into all-zero probabilities, which the
metrics then reported as "uniform", which looked like a calibrated model. Silent failure in a
backtester is indistinguishable from a null result.

## 12. A control dataset's provenance record says "generated", not "fetched"

The provenance tables (`extraction_runs`, `source_records`) exist so that every row in
a database can be traced to the act that produced it. When no fetch is possible, the
temptation is to leave them empty and describe the gap in prose. We record the act
instead: one `extraction_runs` row per market with `source_id = synthetic_generator`,
one `source_records` row with URL `synthetic://<dataset>/<market>`, `parse_status =
generated`, and the seed plus every generator parameter in the notes.

Two consequences that matter. First, a reader of the database alone - without the
README - can see that the rows were synthesised, and with which seed. Second, the code
path that writes provenance is exercised by every control run, so it cannot rot while
waiting for a real extraction that may never be authorised.

The record is idempotent on content, not on source id: a repeated backfill of the same
spec is a no-op rather than a second run, and
`scripts/record_synthetic_provenance.py` refuses to stamp a database whose row count
and distinct-date count disagree.

## 13. Dates are recovered globally, not row by row

The jodi pages carry no dates at all, and the panel pages carry dates that are wrong in
at least seven distinct ways (year typos, a stray `v`, `tp` for `to`, one month-first
token, off-by-one labels, wrong end dates, duplicated weeks). A parser that reads one
label at a time has to guess; a greedy pass over the page was tried and drifted **ten
weeks** before the end of the Kalyan history, silently mis-dating ~10% of the data.

So the page is resolved as one problem: every label yields candidate readings with costs,
the grid contributes constraints of its own (the week starts on the weekday named by the
first column; consecutive weeks are a whole number of weeks apart; time only moves
forward), and a shortest-path pass picks the set of dates with minimum total cost. Label
faithfulness and grid coherence are then both satisfied, and every deviation is reported
in the reconciliation audit rather than absorbed.

Verification is not "the parse ran". It is: zero weekday mismatches, zero duplicate dates,
zero out-of-order rows, and - the strongest check available - the *two independent pages*
agree cell-for-cell on all 6,803 jodis once dating is applied. A single misplaced week
would break that agreement.

## 14. When the source contradicts itself, keep the arithmetic and flag the row

On 40 of 6,803 days the printed jodi is not `digit_sum(open) · digit_sum(close)`
(Kalyan 35, Main Bazar 5). Both pages print the same wrong jodi, so it is a source
transcription error, not a parsing artefact, and the pages cannot say which of the three
numbers is wrong.

The pannas win and the anks are arithmetic. Reasons: both analysis targets are defined on
anks, and every panna-derived feature (digit sums, panel type, pair patterns, M047-M060)
requires the pannas to be consistent with the anks they sit next to. Trusting the printed
jodi would produce 40 rows whose pannas contradict their own anks - an inconsistency that
would then silently propagate into features, while 40 wrong anks out of 13,606 are a
0.3% perturbation of a 10-way categorical series.

The contradiction is not swallowed: the affected rows carry a `notes` flag, a `warning`
lands in `data_quality`, and the full list is in
`research/extraction/reconciliation_<market>.json`.

## 15. Blank days stay blank

147 Kalyan cell-days and 143 Main Bazar cell-days carry no result on either page
(`* * *`). They are not interpolated, forward-filled or dropped-and-forgotten: no row is
written, the count is recorded, and the reconciliation audit lists them. A draw that did
not happen is a real gap in a time series whose lags, transition counts and walk-forward
folds all depend on calendar order; inventing a value would be the single easiest way to
manufacture a spurious result.
