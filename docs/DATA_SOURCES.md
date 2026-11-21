# Data sources: what was attempted, what happened, what to do next

> **Update, 2026-11-07 — real data is now in the databases.** The user supplied saved
> pages (MHTML snapshots) of the four primary dpboss chart URLs, taken on the morning of
> 7 November 2026. They were parsed, dated, cross-checked against each other and loaded:
> **Kalyan 4,143 results (2012-12-31 → 2026-11-05)** and **Main Bazar 2,660 results
> (2015-12-28 → 2026-11-05)**. The whole dating and reconciliation story — including the
> five year-typo week labels the site itself contains and the 40 days where a printed
> jodi contradicts its own pannas — is in
> [`DATA_SNAPSHOT_2026-11-07.md`](DATA_SNAPSHOT_2026-11-07.md). The remaining sections of
> this file describe the automated fetch path, which is still blocked from this
> environment.

## Summary

| Source | Role | Result in the build environment |
|---|---|---|
| `https://dpbossss.com/jodi-chart-record/kalyan.php` | Kalyan jodi chart (primary) | **Unreachable** |
| `https://dpbossss.com/panel-chart-record/kalyan.php` | Kalyan panel/panna chart (primary) | **Unreachable** |
| `https://dpbossss.com/jodi-chart-record/main-bazar.php` | Main Bazar jodi chart (primary) | **Unreachable** |
| `https://dpbossss.com/panel-chart-record/main-bazar.php` | Main Bazar panel chart (primary) | **Unreachable** |
| `https://dpbossss.com/` | Index / link discovery | **Unreachable** |
| `https://www.sattamatka.sale/` | Secondary corroboration | **Unreachable** |
| `https://sattadpbossmatka.com/` | Secondary corroboration | **Unreachable** |

**Zero records were extracted from any of them by the live scraper.** No partial page,
cached HTML or third-party copy of these charts was used to fill the gap, because a record
whose provenance cannot be demonstrated is not research data.

The data that *is* loaded came from the user's own saved copies of the four pages listed
above (same host, same URLs, saved 2026-11-07 03:38–03:39 GMT). They are treated as a
first-class source: hashed, archived under `data/raw/snapshots/`, recorded in
`extraction_runs` / `source_records`, and imported by a committed code path
(`python -m src.cli.main --dataset live import-snapshots --input <dir>`), not by hand.

## Exact failure modes

Two distinct transport failures were observed, both at the network edge rather than
at the application:

- **HTTPS (port 443):** the TLS handshake is reset — `SSL_ERROR_SYSCALL` /
  `Connection reset by peer` — before any HTTP response is returned.
- **HTTP (port 80):** the TCP connection is accepted and then closed with an empty
  reply, so no status line is ever received.

Outbound access from the environment was limited to package registries
(`pypi.org`, `files.pythonhosted.org`) and GitHub. This is an egress restriction of
the sandbox, not a decision of the platform, and it applies equally to every
configured host.

`python -m src.cli.main discover` reproduces the probe and writes
`research/extraction/discovery_report.json` with the per-source error text, so the
claim above can be re-checked rather than taken on trust.

## Why the platform does not work around it

- **No third-party dumps.** A scraped dataset of unknown provenance cannot be
  distinguished from a fabricated one, and mixing it into `historical_results` would
  poison every downstream number.
- **No fabricated records.** Generating "plausible" historical rows and labelling
  them as market history would be the single worst thing this repository could do.
  The synthetic worlds exist precisely so that the platform never has to choose
  between "no data" and "invented data" — they are labelled, quarantined by
  `assert_dataset_isolation`, and excluded from any live-tagged report.
- **No access-control circumvention.** No CAPTCHA solving, no paywall bypass, no
  authentication spoofing, no aggressive retry storms.

## What happens when a networked environment runs this

```bash
# 1. Probe first, and read the report before scraping anything
python -m src.cli.main --dataset live discover

# 2. Respect robots.txt and the configured politeness delay
#    (config/sources.yaml -> http: user_agent, timeout_seconds, max_retries,
#     delay_seconds; pagination.py enforces the delay between requests)

# 3. Extract one market at a time; raw bodies are stored under data/raw/live/<market>/
python -m src.cli.main --dataset live extract --market kalyan

# 4. Validate BEFORE modelling - a failed gate must stop the pipeline
python -m src.cli.main --dataset live validate --market kalyan
```

The extraction path already implements: robots checking, per-host politeness delay,
retry with backoff, raw-body archiving with SHA-256 digests, pagination, resume from
a stored state file, cross-source merge with explicit conflict records, and
append-only revisions when a re-scrape disagrees with what was stored.

## Field mapping and integrity rules

| Chart | Provides | Stored as |
|---|---|---|
| Jodi chart | open ank, close ank, jodi | `open_ank`/`close_ank` (int 0–9), `jodi` (2-char string) |
| Panel chart | open panna + ank, close panna + ank | `open_panna`/`close_panna` (3-char string), anks as above |

- Panna → ank is arithmetic: digit sum mod 10. It is always derivable and is always
  re-derived and checked (`open_panna_ank_consistent`).
- Ank → panna is **not** derivable. The platform never invents a panna.
- Fixed-width values keep their leading zeros (`"007"`, `"07"`) because they are
  identifiers, not numbers.
- Every row records `source_id`, `source_url`, `source_timestamp`,
  `extraction_timestamp` and `verification_status`. A row claiming to be live data
  without a URL is rejected by the storage layer.

## Expected scale

The charts publish one row per draw date per market, so ten years of Mon–Sat draws is
≈ 3,130 rows per market — the same size as the synthetic control worlds, which is why
the control worlds use that span. Spot-checking a handful of dates against a second
source is part of the ingestion acceptance criteria; wholesale independent
re-extraction of the full history is not feasible within rate limits.
