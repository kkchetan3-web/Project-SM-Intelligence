# Player psychology and bidding quotes

Two side channels were added on 2026-11-09, both opt-in, neither of which is
used by the default pipeline. They exist because the user asked for them:
the first models what players *bet on*, the second captures what the market
*quotes* for each ank. Both are honest about their limits - neither has been
shown to predict the next draw, and neither replaces the results-based
features.

## 1. The psychology channel

**What it is.** `src/preprocessing/psychology.py` turns the published history
into proxies for three documented biases:

| Feature group | Bias it proxies | Meaning |
|---|---|---|
| `heat_w{30,90}_{ank}` | availability / hot hand | recent frequency of each ank - where public attention has been |
| `heat_mom_{ank}`, `heat_concentration` | momentum of attention | is the hot ank getting hotter? |
| `cold_max_norm`, `overdue_count` | gambler's fallacy | how "due" each ank is (gap since last appearance vs expected) |
| `coverage_w{30,90}` | engagement | how many distinct anks the recent window touched |
| `jodi_heat_*`, `jodi_repeat_rate` | jodi-level attention | heat and repetition of the 100 jodis, formed as open+close |

The jodi channel uses the market's own formation rule: open digit followed by
close digit (open 5, close 1 -> jodi 51).

**How it is wired.** `FeatureConfig(include_psychology=True)` adds the channel
to `build_features`; the default is off so every published result stays
reproducible. The channel is causal by construction (computed on the same
shifted series as the main matrix) and `tests/test_psychology.py` asserts the
truncation property directly.

**What the data says.** `scripts/psychology_signal_check.py` bins the history
by each channel feature and tests whether the next-draw distribution differs
across bins (chi-square) and scores bin-frequency predictions against uniform
(log loss). On the live data (4,143 Kalyan / 2,660 Main Bazar draws, 39
features per target plus the jodi channel):

* the smallest p-values are around 0.001-0.05 for a handful of heat/momentum
  features - which is what 156 tests with no true signal look like;
* **no feature beats uniform by more than 0.025 log loss**, and the bin
  frequencies that do are in-sample estimates of the same rows they are
  scored on - overfitting, not edge;
* the jodi channel's top-heat identifier on Main Bazar scores *worse* than
  uniform (log loss 4.56) because binning on a categorical id is degenerate.

`scripts/psychology_channel_eval.py` runs the walk-forward arbiter for Kalyan
(the forecast market): the same 10 models, channel ON, compared against the
pipeline's channel-OFF numbers (identical protocol, identical data) and the
uniform baseline.

| Kalyan | Channel ON features | Best model (ON) | Pipeline (OFF) | Delta | Beats uniform? |
|---|---|---|---|---|---|
| open | 108 | svm 2.30689 | svm 2.30733 | −0.00044 | no |
| close | 112 | svm 2.30522 | svm 2.30624 | −0.00102 | no |

The channel moves the best model by 0.0004-0.001 log loss - an order of
magnitude below the 0.002 promotion margin - and nothing beats uniform on
either target. **The psychology channel is implemented, tested and honestly
evaluated: it carries no exploitable signal on this data.** It stays opt-in
and out of the default pipeline for exactly that reason.

## 2. The bidding framework

**What it is.** `src/ingestion/bidding.py` + schema v4 (`bidding_quotes`,
`bidding_feed_runs`) store what bookies *quoted* for each ank - the price at
which they would take money. In these markets the quote is where player
psychology is priced: a low quote on an ank means heavy public money on it
(bookies pay less for it), a high quote means the market is reluctant to take
money there. The pressure channel (`bidding_pressure_features`) turns quotes
into inverse-rate features (`1/rate - 1`) aligned to the draw calendar.

**Feed format.** CSV (long format) or JSON:

```csv
date,side,ank,rate,volume
2026-11-05,open,5,0.82,15000
2026-11-05,close,1,0.86,13000
```

`rate` is in rupees (0.90 = 90 paise); `volume` is optional. One row per
(date, side, ank); re-imports update quotes in place.

```bash
python -m src.cli.main --dataset live import-bidding --market kalyan \
    --input feed.csv --source-url https://...
```

**Status of live bidding data.** **Not reachable.** All five configured
sources reset the TLS connection from this environment (verified 2026-11-06 and
again 2026-11-09: TCP connects, TLS handshake is killed). The loader, schema,
channel and tests are implemented and fixture-tested; no real quotes have been
imported yet. When a feed is supplied as a file - the same way the chart
snapshots were - `import-bidding` loads it and the pressure channel becomes
available to the forecast path. Quotes are real-world data and are refused for
non-live datasets, like the snapshots.

## 3. What was forecast for 2026-11-16 (Kalyan)

With the holiday (6-15 November 2026) honoured via `--target-date`, the two
forecasts stored in the ledger are **uniform** - every digit 0.1000, every
jodi 0.0100 - because no candidate model passed promotion on this history. The
platform's own arbiter therefore says the *most accurate* open and close is
any open and any close: the joint distribution is flat.

For a concrete answer anyway, the historically most frequent picks (4,143
draws) are:

| | Picks | Frequency |
|---|---|---|
| Open anks | 9, 5 | 450, 432 |
| Close anks | 1, 2 | 465, 444 |
| Jodis (open+close) | 51, 31, 58, 04 | 55, 55, 52, 52 |
| Best single pair | open 5 + close 1 -> jodi 51 | 55 |

These are frequency rankings, not predictions: the jodi distribution is
statistically flat (chi-square 82.2 over 100 jodis, p=0.89; expected 99 under
uniform), so the top jodis are +2 sigma noise around the 41.4 expected count.
