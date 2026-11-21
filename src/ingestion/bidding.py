"""Market-side bidding quotes: player money, not results.

The results table records what the market *announced*. Bidding quotes record
what bookies *quoted* for each ank - the price at which they would take money.
In these markets the quote is where player psychology is priced: a low quote on
an ank means heavy public money on it (bookies pay less for it), a high quote
means the market is reluctant to take money there.

This module provides:

* a feed reader for CSV (long format) or JSON;
* an importer that upserts quotes into ``bidding_quotes`` and audits the feed
  run in ``bidding_feed_runs``;
* a pressure channel that turns quotes into side features for the forecast
  path (opt-in, exactly like the psychology channel).

**Status of the live feed:** no bidding source has ever been reachable from
this environment (the configured sites reset the TLS connection; verified
2026-11-06 and again 2026-11-09). The loader, schema, feature channel and tests
are therefore implemented and fixture-tested, but no real quotes have been
imported yet. When a feed is supplied - as a file, the same way the chart
snapshots were - ``import-bidding`` loads it and the pressure channel becomes
available to the forecast path.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from src.core.configuration import Config
from src.core.logging import get_logger
from src.core.provenance import utcnow
from src.storage.market_database import MarketDatabase

log = get_logger(__name__)

REQUIRED_COLUMNS = ("date", "side", "ank", "rate")


@dataclass
class BiddingImportReport:
    market_id: str
    dataset: str
    source_id: str
    source_url: str | None
    rows_read: int = 0
    inserted: int = 0
    updated: int = 0
    rejected: int = 0
    errors: list[str] = field(default_factory=list)
    run_id: int | None = None
    quotes_path: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "market_id": self.market_id, "dataset": self.dataset,
            "source_id": self.source_id, "source_url": self.source_url,
            "rows_read": self.rows_read, "inserted": self.inserted,
            "updated": self.updated, "rejected": self.rejected,
            "errors": self.errors[:20], "run_id": self.run_id,
            "quotes_path": self.quotes_path,
        }


def _parse_row(raw: Mapping[str, Any], source: str) -> dict[str, Any] | None:
    """Validate one feed row; return the canonical dict or None if malformed."""
    try:
        day = str(raw["date"]).strip()
        date.fromisoformat(day)
        side = str(raw["side"]).strip().lower()
        if side not in ("open", "close"):
            raise ValueError(f"side must be open/close, got {side!r}")
        ank = int(raw["ank"])
        if not 0 <= ank <= 9:
            raise ValueError(f"ank must be 0..9, got {ank}")
        rate = float(raw["rate"])
        if not 0 < rate <= 1:
            raise ValueError(f"rate must be in rupees (0, 1], got {rate}")
        volume = raw.get("volume")
        volume = float(volume) if volume not in (None, "", "nan") else None
        return {
            "result_date": day, "quote_side": side, "ank": ank, "rate": rate,
            "volume": volume,
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{source}: {exc}") from exc


def read_feed(path: str | Path) -> list[dict[str, Any]]:
    """Read a bidding feed file: CSV (long format) or JSON.

    CSV expects a header with at least ``date,side,ank,rate`` and an optional
    ``volume`` column. JSON expects a list of objects with the same keys.
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json" or text.lstrip().startswith("["):
        data = json.loads(text)
        rows = [dict(item) for item in data]
    else:
        reader = csv.DictReader(text.splitlines())
        missing = set(REQUIRED_COLUMNS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV feed missing required columns: {sorted(missing)}")
        rows = [dict(item) for item in reader]
    return [_parse_row(raw, f"row {i}") for i, raw in enumerate(rows)]


def import_bidding(config: Config, market_id: str, feed_path: str | Path, *,
                   source_id: str | None = None, source_url: str | None = None,
                   source_timestamp: str | None = None,
                   audit_dir: str | Path | None = None,
                   rebuild: bool = False) -> BiddingImportReport:
    """Load a bidding feed for one market into ``bidding_quotes``."""
    if config.dataset.name != "live":
        raise ValueError("bidding quotes are real-world data and may only be loaded "
                         "into the live dataset, not into a control world")
    config.market(market_id)
    market = config.market(market_id)
    source = source_id or str(market.primary_source) + "_bidding"

    rows = read_feed(feed_path)
    report = BiddingImportReport(market_id=market_id, dataset=config.dataset.name,
                                 source_id=source, source_url=source_url,
                                 rows_read=len(rows))
    if not rows:
        return report

    db = MarketDatabase(config, market_id)
    db.manager.initialise(market_id, rebuild=rebuild)

    # Distinguish new quotes from revised ones for the report.
    with db.session(read_only=True) as conn:
        existing = {
            (r["result_date"], r["quote_side"], r["ank"])
            for r in conn.execute(
                "SELECT result_date, quote_side, ank FROM bidding_quotes")
        }

    payload = {
        "source_id": source, "source_url": source_url,
        "source_timestamp": source_timestamp,
    }
    rows = [{**row, "source_id": source, "source_url": source_url,
             "source_timestamp": source_timestamp,
             "extraction_timestamp": utcnow(),
             "raw_payload": json.dumps(payload),
             "notes": None}
            for row in rows]
    n = db.save_bidding_quotes(rows)
    report.inserted = sum(1 for r in rows
                          if (r["result_date"], r["quote_side"], r["ank"]) not in existing)
    report.updated = n - report.inserted

    with db.session() as conn:
        cur = conn.execute(
            "INSERT INTO bidding_feed_runs (market_id, source_id, source_url, "
            "started_at, finished_at, rows_read, rows_inserted, rows_updated, "
            "rows_rejected, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (market_id, source, source_url, utcnow(), utcnow(),
             report.rows_read, report.inserted, report.updated, report.rejected,
             "feed imported; quotes upserted"),
        )
        report.run_id = int(cur.lastrowid)

    if audit_dir is not None:
        out = Path(audit_dir)
        out.mkdir(parents=True, exist_ok=True)
        report.quotes_path = str(out / f"bidding_import_{market_id}.json")
        Path(report.quotes_path).write_text(
            json.dumps(report.as_dict(), indent=2, default=str))
    return report


# ---------------------------------------------------------------------------
# pressure channel (side features for the forecast path)
# ---------------------------------------------------------------------------
def bidding_pressure_features(quotes: pd.DataFrame,
                              dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Turn quoted rates into a pressure channel, aligned to ``dates``.

    ``quotes`` is the ``bidding_quotes`` frame (or an equivalent with columns
    ``result_date, quote_side, ank, rate``). The channel is *inverse rate*:
    the lower the quote on an ank, the more money the market expects on it.

    Produces 20 per-ank columns (``bid_press_{side}_{ank}``), the per-side
    entropy of the pressure distribution, and the overall max pressure - all
    NaN for dates with no quotes. This is a *side backup* channel: it is added
    only when a feed exists and the caller opts in; it never replaces the
    results-based features.
    """
    dates = pd.DatetimeIndex(dates)
    out = pd.DataFrame(index=dates)
    if quotes is None or quotes.empty:
        for side in ("open", "close"):
            for ank in range(10):
                out[f"bid_press_{side}_{ank}"] = np.nan
        return out

    q = quotes.copy()
    q["result_date"] = pd.to_datetime(q["result_date"])
    q["press"] = 1.0 / q["rate"] - 1.0
    for side in ("open", "close"):
        sub = q[q["quote_side"] == side]
        pivot = sub.pivot_table(index="result_date", columns="ank",
                                values="press", aggfunc="mean")
        for ank in range(10):
            col = f"bid_press_{side}_{ank}"
            out[col] = pivot[ank].reindex(dates).to_numpy() if ank in pivot.columns \
                else np.nan
        present = pivot.notna().any(axis=1).reindex(dates).fillna(False)
        p = pivot.reindex(dates)
        entropy = pd.Series(
            -np.sum(np.where(p > 0, p * np.log(np.clip(p, 1e-12, None)), 0.0),
                    axis=1),
            index=dates)
        out[f"bid_entropy_{side}"] = entropy.where(present)
        out[f"bid_max_{side}"] = p.max(axis=1).where(present)
    return out
