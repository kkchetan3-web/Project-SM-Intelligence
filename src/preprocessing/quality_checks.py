"""Data-quality gates.

These run before any analysis and their output is written to ``data_quality``.
A market with a failing ``error``-severity check is excluded from modelling:
producing a beautiful backtest on a corrupted table is worse than producing
nothing.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.core.configuration import Config
from src.core.logging import get_logger
from src.core.validation import QualityReport, find_duplicate_dates, validate_chronology
from src.preprocessing.cleaning import clean_results
from src.storage.market_database import MarketDatabase

log = get_logger(__name__)


def run_quality_checks(config: Config, market_id: str, *, persist: bool = True) -> QualityReport:
    db = MarketDatabase(config, market_id)
    market = config.market(market_id)
    report = QualityReport(market_id=market.market_id)

    df = db.results()
    report.n_records = len(df)

    report.add("has_records", len(df) > 0, "n_records", len(df), severity="error",
               detail="an empty table cannot support any method")

    if df.empty:
        if persist:
            db.record_quality(report.to_rows())
        return report

    dates = df["result_date"].dt.normalize()
    report.add("unique_dates", dates.nunique() == len(dates), "duplicate_dates",
               find_duplicate_dates(dates.tolist()), severity="error")
    report.add("chronological_order", validate_chronology(dates.tolist()),
               "monotonic", bool(validate_chronology(dates.tolist())), severity="error")

    # Value-domain checks against the declared outcome space.
    for column, space, low, high in (("open_ank", "ank", 0, 9), ("close_ank", "ank", 0, 9)):
        if column not in df or df[column].isna().all():
            continue
        vals = df[column].dropna()
        ok = bool(vals.between(low, high).all())
        report.add(f"{column}_domain", ok, "n_out_of_range", int((~vals.between(low, high)).sum()),
                   severity="error")
        report.add(f"{column}_nulls", df[column].notna().all(), "n_missing",
                   int(df[column].isna().sum()), severity="warning")

    # Leading-zero preservation: jodi must always be two characters.
    if "jodi" in df:
        jodi = df["jodi"].dropna().astype(str)
        bad_width = int((jodi.str.len() != 2).sum())
        report.add("jodi_fixed_width", bad_width == 0, "n_bad_width", bad_width,
                   severity="error", detail="leading zeros must survive storage")
        leading_zero_rows = int(jodi.str.startswith("0").sum())
        report.add("jodi_leading_zeros_present", True, "n_leading_zero_values",
                   leading_zero_rows, severity="info",
                   detail="count of stored jodi values beginning with 0 (a good sign if > 0)")

    # Panna/ank arithmetic consistency.
    if {"open_panna", "open_ank"} <= set(df.columns):
        sub = df.dropna(subset=["open_panna", "open_ank"])
        if not sub.empty:
            derived = sub["open_panna"].map(lambda p: sum(int(c) for c in p) % 10)
            bad = int((derived != sub["open_ank"]).sum())
            report.add("open_panna_ank_consistent", bad == 0, "n_mismatch", bad,
                       severity="warning")

    # Coverage / gaps - reported, not "fixed".
    span_days = int((dates.max() - dates.min()).days) + 1
    missing = span_days - dates.nunique()
    report.add("coverage_reported", True, "missing_calendar_days", missing, severity="info",
               detail=f"{dates.nunique()} observed of {span_days} calendar days")
    coverage_pct = round(100 * dates.nunique() / max(span_days, 1), 2)
    report.add("coverage_threshold", coverage_pct >= 50.0, "coverage_pct", coverage_pct,
               severity="warning",
               detail="very sparse coverage weakens every chronological method")

    # Provenance.
    has_url = df["source_url"].notna()
    if config.dataset.is_live:
        report.add("source_url_present", bool(has_url.all()), "n_missing_url",
                   int((~has_url).sum()), severity="error",
                   detail="every live record must cite its source URL")
        bad_status = df["verification_status"].astype(str).str.startswith("synthetic")
        report.add("no_synthetic_rows_in_live", not bool(bad_status.any()),
                   "n_synthetic_rows", int(bad_status.sum()), severity="error")
    else:
        synthetic = df["verification_status"].astype(str).str.startswith("synthetic")
        report.add("synthetic_status_declared", bool(synthetic.all()),
                   "n_non_synthetic", int((~synthetic).sum()), severity="error",
                   detail="control datasets must be unmistakable in every row")

    # Revision audit trail.
    revisions = db.revision_log()
    report.add("revision_audit", True, "n_revisions", len(revisions), severity="info")

    # Duplicate-jodi-value sanity: not an error, but worth surfacing that the
    # ank marginal should be roughly flat if the draw is fair.
    for column in ("open_ank", "close_ank"):
        if column in df and df[column].notna().sum() > 100:
            counts = df[column].dropna().value_counts()
            ratio = float(counts.max() / max(counts.min(), 1))
            report.add(f"{column}_marginal_flatness", ratio < 3.0, "max_min_ratio", round(ratio, 3),
                       severity="info", detail="large imbalance would suggest a parsing error")

    if persist:
        db.record_quality(report.to_rows())
    log.info("quality %s: %d checks, %d errors, %d warnings",
             market_id, len(report.issues), len(report.errors), len(report.warnings))
    return report


def gate(config: Config, market_id: str) -> dict[str, Any]:
    """Hard gate used by the modelling pipeline."""
    report = run_quality_checks(config, market_id)
    return {
        "market_id": market_id,
        "ok": report.ok,
        "n_records": report.n_records,
        "errors": [i.check for i in report.errors],
        "warnings": [i.check for i in report.warnings],
    }
