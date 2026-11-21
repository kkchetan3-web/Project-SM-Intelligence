"""Cleaning: turn stored rows into a validated, chronologically ordered table.

Cleaning never deletes a record to make an analysis work. It *flags*. The rules
are:

* rows are sorted by date and must be unique per date (the schema enforces this;
  cleaning verifies it and fails loudly if the invariant is broken);
* a row missing the target component is excluded from that target's series only,
  and the exclusion is counted and reported;
* values are re-validated against their declared outcome space;
* nothing is imputed. A missing draw stays missing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from src.core.configuration import Config
from src.core.logging import get_logger
from src.core.validation import ValidationError, validate_result_value
from src.storage.market_database import MarketDatabase

log = get_logger(__name__)


@dataclass
class CleanResult:
    market_id: str
    target: str
    frame: pd.DataFrame
    n_raw: int = 0
    n_used: int = 0
    n_missing_target: int = 0
    n_invalid: int = 0
    exclusions: list[dict[str, Any]] = field(default_factory=list)
    dataset: str = "live"

    def summary(self) -> dict[str, Any]:
        return {
            "market_id": self.market_id, "target": self.target,
            "n_raw": self.n_raw, "n_used": self.n_used,
            "n_missing_target": self.n_missing_target, "n_invalid": self.n_invalid,
            "first_date": (self.frame["result_date"].min().date().isoformat()
                           if not self.frame.empty else None),
            "last_date": (self.frame["result_date"].max().date().isoformat()
                          if not self.frame.empty else None),
            "dataset": self.dataset,
        }


def clean_results(config: Config, market_id: str) -> pd.DataFrame:
    """Load and validate one market's active result history."""
    db = MarketDatabase(config, market_id)
    market = config.market(market_id)
    df = db.results()
    if df.empty:
        return df

    df = df.sort_values("result_date").reset_index(drop=True)
    dups = df["result_date"].duplicated()
    if dups.any():
        raise ValidationError(
            f"{market_id}: duplicate active result dates {df.loc[dups, 'result_date'].tolist()[:5]}"
        )

    for column, space in (("open_panna", "panna"), ("close_panna", "panna"),
                          ("open_ank", "ank"), ("close_ank", "ank"), ("jodi", "jodi")):
        if column not in df:
            continue
        cleaned = []
        for value in df[column]:
            if pd.isna(value):
                cleaned.append(None)
                continue
            try:
                cleaned.append(validate_result_value(value, space))
            except ValidationError:
                log.warning("%s: invalid %s value %r -> nulled", market_id, column, value)
                cleaned.append(None)
        df[column + "_c"] = cleaned
        df[column] = cleaned
        df.drop(columns=[column + "_c"], inplace=True)

    # Consistency: ank must equal digit sum of panna when both are present.
    # A panna may legitimately be missing while its ank is known (the jodi carries
    # both anks), and pandas turns those NULLs into NaN, so the guard is `isna`,
    # not `is None`.
    if {"open_panna", "open_ank"} <= set(df.columns):
        derived = df["open_panna"].map(
            lambda p: None if pd.isna(p) else sum(int(c) for c in str(p)) % 10
        )
        mismatch = (derived.notna() & df["open_ank"].notna() & (derived != df["open_ank"]))
        if mismatch.any():
            log.warning("%s: %d open panna/ank mismatches (kept as reported)",
                        market_id, int(mismatch.sum()))
            df.loc[mismatch, "open_ank"] = derived[mismatch]

    if "open_ank" in df and "close_ank" in df and "jodi" in df:
        expected = df.apply(
            lambda r: None if pd.isna(r["open_ank"]) or pd.isna(r["close_ank"])
            else f"{int(r['open_ank'])}{int(r['close_ank'])}",
            axis=1,
        )
        bad = expected.notna() & df["jodi"].notna() & (expected.astype(str) != df["jodi"].astype(str))
        if bad.any():
            log.warning("%s: %d jodi/open-close mismatches; trusting open+close",
                        market_id, int(bad.sum()))
            df.loc[bad, "jodi"] = expected[bad]

    df.attrs["market_id"] = market.market_id
    df.attrs["dataset"] = config.dataset.name
    return df


def clean_target(config: Config, market_id: str, target: str) -> CleanResult:
    """Produce the ordered outcome series for one target, with exclusion accounting."""
    market = config.market(market_id)
    spec = market.target(target)
    df = clean_results(config, market_id)
    if df.empty:
        return CleanResult(market_id=market.market_id, target=target,
                           frame=df, dataset=config.dataset.name)

    column = spec.field
    n_raw = len(df)
    missing = df[column].isna()
    used = df.loc[~missing].copy()
    used = used.sort_values("result_date").reset_index(drop=True)

    if spec.space == "ank":
        used["y"] = used[column].astype(int)
    elif spec.space == "jodi":
        used["y"] = used[column].astype(str).str.zfill(2)
    else:
        used["y"] = used[column].astype(str)

    return CleanResult(
        market_id=market.market_id, target=target, frame=used,
        n_raw=n_raw, n_used=len(used), n_missing_target=int(missing.sum()),
        exclusions=[
            {"date": d.date().isoformat(), "reason": f"missing {column}"}
            for d in df.loc[missing, "result_date"].head(50)
        ],
        dataset=config.dataset.name,
    )


def outcome_series(config: Config, market_id: str, target: str) -> pd.Series:
    """Convenience: date-indexed outcome series, no missing values."""
    result = clean_target(config, market_id, target)
    if result.frame.empty:
        return pd.Series(dtype="object", name=target)
    return result.frame.set_index("result_date")["y"].rename(target)
