# The real data: what was supplied, how it was dated, and what was stored

**Snapshot date:** 2026-11-07 (all four pages were saved on the morning of 7 November 2026)
**Status:** loaded into the LIVE databases — Kalyan **4,143** dated results, Main Bazar **2,660**
**Machine-readable proof:** `research/extraction/reconciliation_kalyan.json`,
`research/extraction/reconciliation_main_bazar.json`, `data/raw/snapshots/MANIFEST.json`

---

## 1. What was supplied

Four saved pages ("Saved by Blink" MHTML) of the two primary sources. The save timestamp
and the SHA-256 of every file are kept, so each stored row can be traced to the exact
bytes it came from.

| Page | URL | Saved (GMT) | Bytes | SHA-256 (first 12) |
|---|---|---|---|---|
| Kalyan panel chart | `https://dpbossss.com/panel-chart-record/kalyan.php?full_chart` | 2026-11-07 03:38:42 | 393,375 | `21770b4553ad` |
| Kalyan jodi chart | `https://dpbossss.com/jodi-chart-record/kalyan.php` | 2026-11-07 03:38:33 | 237,532 | `45ddc5dd7a1e` |
| Main Bazar panel chart | `https://dpbossss.com/panel-chart-record/main-bazar.php?full_chart` | 2026-11-07 03:39:02 | 470,548 | `13ebe7b5643a`*(jodi)* |
| Main Bazar jodi chart | `https://dpbossss.com/jodi-chart-record/main-bazar.php` | 2026-11-07 03:38:54 | 166,062 | see manifest |

The raw files are copied to `data/raw/snapshots/<market>/` and hashed again in
`data/raw/snapshots/MANIFEST.json` (committed). The files themselves stay out of version
control, per the repository's data policy.

## 2. The dating problem

The two pages are structured differently, and neither is directly loadable:

* **The jodi chart has no dates at all.** It is a grid of weekday columns
  (Kalyan: Mon–Sat, Main Bazar: Mon–Fri) and one row per week, 713 and 561 rows
  respectively, with the newest week last. Nothing in the row identifies the year.
* **The panel chart is dated, but defectively.** Every row carries a
  `DD/MM/YYYY to DD/MM/YYYY` label, and every day has three cells —
  `open panna`, `jodi`, `close panna`. The defects found:

| Defect | Example (verbatim from the page) | Consequence if trusted naively |
|---|---|---|
| Year typos (5 weeks in Kalyan) | `07/01/2018 to 12/01/2018` for the week of **2019**-01-07 | 5 weeks placed a year early |
| Same, larger | `20/06/2020 to 26/06/2022` for the week of 2022-06-20 | week placed 2 years early |
| Stray character | `v31/12/2018 to 05/01/2019` | date token unparseable |
| `tp` instead of `to` | `08/06/2020 tp 16/06/2020` | row unparseable |
| Mixed date formats | `12/16/2016` (month-first) among `DD/MM/YYYY` | ambiguous parse |
| Off-by-one label | `01/11/2015` (a Sunday) for the week starting Mon 02/11/2015 | every day in the week off by one |
| Wrong end date | `27/10/2014 to 01/01/2014`, `27/10/2019 to 26/10/2019` | end date unusable |
| Genuine closures | Kalyan: 14-day gaps around Diwali 2013/2014/2019; **49-day gap** from 2020-03-23 to 2020-05-11. Main Bazar: the same 49-day 2020 gap | Must stay gaps — *not* be squeezed out |

## 3. How the dates were recovered

The grid supplies three constraints of its own, and they are used together rather than
label-by-label:

1. a week starts on the weekday named by the first column;
2. consecutive weeks are a whole number of weeks apart (7, 14, 21 … days) — a closure
   leaves a multiple-of-7 hole;
3. weeks are strictly increasing in time.

Each label yields several candidate readings (day-first, month-first, and the same
reading under a neighbouring year, plus ±1-day shifts), each with a cost. The whole page
is then resolved as a **shortest-path problem** over 713 (resp. 561) rows, minimising the
total cost. A local, greedy choice was tried first and produced a **ten-week drift** by the
end of the page — which is exactly the failure mode this design avoids, and why the
resolution is global.

Verification that the result is right, rather than merely self-consistent:

* **0 weekday mismatches** — every one of the 7,079 dated cells falls on the weekday its
  column names.
* **0 duplicate dates** and **0 out-of-order rows**.
* **No Sundays** — 0 of 4,143 Kalyan rows; Main Bazar has no Saturday or Sunday rows.
* **The two independent pages agree cell-for-cell.** After dating, the jodi printed on the
  jodi chart equals the jodi printed on the panel chart on **4,143 / 4,143** Kalyan cells
  and **2,660 / 2,660** Main Bazar cells. A single misplaced week would destroy that
  agreement; nothing did.

## 4. Cross-check between the two pages, and against arithmetic

The jodi is *defined* as `open_ank · close_ank`, and an ank is the digit sum of its panna
mod 10 (`799 → 25 → 5`). That gives a third, independent check on every day:

| Check | Kalyan | Main Bazar |
|---|---|---|
| Days where the two pages agree on the jodi | 4,143 / 4,143 | 2,660 / 2,660 |
| Days where the printed jodi equals the panna arithmetic | 4,094 + 14 recovered = 4,108 / 4,143 | 2,655 / 2,660 |
| Days where the **printed jodi contradicts its own pannas** | **35** (0.84%) | **5** (0.19%) |

The 40 contradictions are transcription errors in the source: one component is wrong and
the page cannot say which. Example — 2013-02-11 Kalyan prints `368 / 79 / 339`; but
`3+6+8 = 17 → 7` and `3+3+9 = 15 → 5`, so the pannas imply **75**, not 79. Both pages
print 79, so the jodi is not a parsing artefact; one of the three numbers is simply wrong
on the site.

**Resolution rule:** the pannas are kept and the anks are arithmetic
(`open_ank = f(open_panna)`, `close_ank = f(close_panna)`), because both analysis targets
are defined on anks and every panna-derived feature needs the pannas to agree with them.
The contradiction is not hidden — the affected rows carry
`notes = 'printed_jodi_contradicts_panna;jodi_chart_contradicts_panna'` and a `warning`
row in the `data_quality` table, and the full list is in the reconciliation JSON.

The alternative (trust the printed jodi and override an ank) was rejected: it would make
16 days internally inconsistent with their own pannas, which is worse for a research
dataset than 40 flagged days out of 6,803.

## 5. What was stored

| | Kalyan | Main Bazar |
|---|---|---|
| Dated cells on the panel page | 4,276 (713 weeks × 6 days) | 2,803 (561 weeks × 5 days) |
| Days with a published result | **4,143** | **2,660** |
| Days the pages leave blank (`* * *`) | 133 | 143 |
| Days recovered from the jodi alone (a panna missing) | 14 | 0 |
| First / last stored date | 2012-12-31 → 2026-11-05 | 2015-12-28 → 2026-11-05 |
| Panna–jodi contradictions flagged | 35 | 5 |

Blank days are **not** filled. A day the source does not publish is a day the market did
not draw (or the page did not record); inventing a value would corrupt every lag, every
transition count and every walk-forward fold that touches it.

Coverage per year (rows actually stored):

| Year | Kalyan | Main Bazar |
|---|---|---|
| 2012 | 1 | – |
| 2013 | 298 | – |
| 2014 | 299 | – |
| 2015 | 302 | 4 |
| 2016 | 302 | 233 |
| 2017 | 300 | 244 |
| 2018 | 303 | 248 |
| 2019 | 296 | 235 |
| 2020 | 264 | 215 |
| 2021 | 304 | 254 |
| 2022 | 304 | 252 |
| 2023 | 301 | 251 |
| 2024 | 303 | 252 |
| 2025 | 304 | 254 |
| 2026 (to 5 Nov) | 262 | 218 |

The 2020 dip is the COVID closure (both markets stop for ~7 weeks in
March–May 2020); 2019 is lighter for Kalyan because of the Diwali week and a further
closure the page records as a gap.

## 6. What this data is *not*

* **Not independently confirmed.** Every row comes from a single provider (dpbossss.com).
  The status is `unverified_scrape`: the second source in `config/markets.yaml` has never
  been reachable, so no record has been cross-provider confirmed.
* **Not complete to today.** The latest result is 2026-11-05. The pages were saved on the
  morning of 2026-11-07 and already carried no result for 06/11/2026 or 07/11/2026; the
  site's own rows show the week ending 06/11 and 07/11 as blank. Whatever the reason, the
  snapshot cannot report draws it does not contain.
* **Not proof that anything is predictable.** More history means better estimates of
  *what the data looks like*, not of what the next draw will be. The Section 22 report
  (`research/reports/SECTION_22_REPORT_live.md`) states the backtest verdicts, which are
  the only evidence that matters for that question.

## 7. Reproduce

```bash
# 0. the four saved pages, in one directory
ls /path/to/snapshots     # *jodi* and *panel* files for kalyan and main_bazar

# 1. import (creates the databases if needed, archives + hashes the raw pages)
python -m src.cli.main --dataset live import-snapshots --input /path/to/snapshots

# 2. everything else, in order
python scripts/run_full_pipeline.py --dataset live --snapshot-dir /path/to/snapshots
```

`import-snapshots` is idempotent: re-importing the same files inserts nothing, and
re-importing a *newer* snapshot revises changed values while keeping the old row in
`result_revisions` (`is_active = 0`) rather than overwriting history.
