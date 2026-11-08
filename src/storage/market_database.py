"""Per-market data access layer.

This is the only module that writes to ``historical_results``. Centralising it
buys three guarantees the research depends on:

1. **No silent overwrite.** :meth:`MarketDatabase.upsert_result` compares the
   incoming value with the stored one; a disagreement is written to
   ``result_revisions`` and the old row is deactivated, never updated in place.
2. **No dataset mixing.** Every row is stamped with the configured dataset name
   and the verification status is checked against it.
3. **No market mixing.** ``market_id`` is validated against the file's own
   identity on every write.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import pandas as pd

from src.core.configuration import Config
from src.core.logging import get_logger
from src.core.provenance import Revision, record_revision, utcnow
from src.core.validation import (
    ValidationError,
    assert_dataset_isolation,
    validate_result_value,
)
from src.storage.database_manager import DatabaseManager

log = get_logger(__name__)

RESULT_COLUMNS = [
    "record_id", "market_id", "result_date", "open_panna", "open_ank",
    "close_panna", "close_ank", "jodi", "source_id", "source_url",
    "source_timestamp", "extraction_timestamp", "verification_status",
    "dataset", "record_version", "notes",
]


@dataclass
class UpsertOutcome:
    inserted: int = 0
    revised: int = 0
    unchanged: int = 0
    rejected: int = 0
    errors: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []

    @property
    def total(self) -> int:
        return self.inserted + self.revised + self.unchanged + self.rejected

    def as_dict(self) -> dict[str, Any]:
        return {
            "inserted": self.inserted, "revised": self.revised,
            "unchanged": self.unchanged, "rejected": self.rejected,
            "errors": self.errors[:20],
        }


class MarketDatabase:
    """Read/write facade over one market file."""

    def __init__(self, config: Config, market_id: str):
        self.config = config
        self.market = config.market(market_id)
        self.market_id = self.market.market_id
        self.manager = DatabaseManager(config)
        self.dataset = config.dataset.name

    # ------------------------------------------------------------------
    # context helper
    # ------------------------------------------------------------------
    def session(self, *, read_only: bool = False):
        return self.manager.session(self.market_id, read_only=read_only)

    # ------------------------------------------------------------------
    # results
    # ------------------------------------------------------------------
    def _canonicalise(self, row: Mapping[str, Any]) -> dict[str, Any]:
        """Validate and normalise one incoming record."""
        date = str(row["result_date"]).strip()[:10]
        pd.Timestamp(date)  # raises on an invalid date

        open_panna = row.get("open_panna")
        close_panna = row.get("close_panna")
        open_ank = row.get("open_ank")
        close_ank = row.get("close_ank")
        jodi = row.get("jodi")

        # Derive whatever is derivable, but never invent a component the source
        # did not carry: panna -> ank is arithmetic, ank -> panna is not.
        if open_panna is not None:
            open_panna = validate_result_value(open_panna, "panna")
            if open_ank is None:
                open_ank = int(sum(int(c) for c in open_panna) % 10)
        if close_panna is not None:
            close_panna = validate_result_value(close_panna, "panna")
            if close_ank is None:
                close_ank = int(sum(int(c) for c in close_panna) % 10)
        if open_ank is not None:
            open_ank = validate_result_value(open_ank, "ank")
        if close_ank is not None:
            close_ank = validate_result_value(close_ank, "ank")
        if jodi is not None:
            jodi = validate_result_value(jodi, "jodi")
        elif open_ank is not None and close_ank is not None:
            jodi = f"{open_ank}{close_ank}"

        if open_ank is None and close_ank is None and jodi is None:
            raise ValidationError(f"record for {date} has no usable result component")

        status = row.get("verification_status", "unverified_scrape")
        assert_dataset_isolation(self.dataset, status)

        # Provenance requirement from project.yaml: a row that claims to be a real
        # observation must carry the URL it came from. Synthetic rows are exempt
        # because their provenance is the generator itself.
        provenance = (self.config.project.get("provenance") or {}) if hasattr(self, "config") else {}
        synthetic_statuses = {"synthetic_control", "synthetic"}
        if (status not in synthetic_statuses
                and provenance.get("require_source_url_for_live", True)
                and not str(row.get("source_url") or "").strip()):
            raise ValidationError(
                f"record for {date} claims verification_status={status!r} without a source_url; "
                "live observations must be attributable to a URL")

        return {
            "market_id": self.market_id,
            "result_date": date,
            "open_panna": open_panna,
            "open_ank": int(open_ank) if open_ank is not None else None,
            "close_panna": close_panna,
            "close_ank": int(close_ank) if close_ank is not None else None,
            "jodi": jodi,
            "source_id": row.get("source_id", "unknown"),
            "source_url": row.get("source_url"),
            "source_timestamp": row.get("source_timestamp"),
            "extraction_timestamp": row.get("extraction_timestamp", utcnow()),
            "verification_status": status,
            "raw_payload": json.dumps(row.get("raw_payload"), default=str)
            if row.get("raw_payload") is not None else None,
            "notes": row.get("notes", ""),
        }

    def upsert_results(self, rows: Iterable[Mapping[str, Any]]) -> UpsertOutcome:
        """Insert or revise records. Returns counts, never raises on bad rows."""
        outcome = UpsertOutcome()
        with self.session() as conn:
            for raw in rows:
                try:
                    rec = self._canonicalise(raw)
                except (ValidationError, ValueError, TypeError) as exc:
                    outcome.rejected += 1
                    outcome.errors.append(f"{raw.get('result_date')}: {exc}")
                    continue

                existing = conn.execute(
                    "SELECT * FROM historical_results WHERE market_id = ? AND "
                    "result_date = ? AND is_active = 1",
                    (self.market_id, rec["result_date"]),
                ).fetchone()

                if existing is None:
                    self._insert(conn, rec)
                    outcome.inserted += 1
                    continue

                diffs = self._diff(dict(existing), rec)
                if not diffs:
                    outcome.unchanged += 1
                    continue

                # Record what changed, deactivate the old row, insert the new one.
                for field_name, (old, new) in diffs.items():
                    record_revision(
                        conn,
                        Revision(
                            record_id=str(existing["record_id"]),
                            field_name=field_name,
                            old_value=old,
                            new_value=new,
                            observed_at=utcnow(),
                            source_id=rec["source_id"],
                            source_url=rec["source_url"],
                            reason="source value differed from stored value; "
                                   "newer extraction retained, original preserved",
                        ),
                    )
                conn.execute(
                    "UPDATE historical_results SET is_active = 0 WHERE record_id = ?",
                    (existing["record_id"],),
                )
                rec["record_version"] = int(existing["record_version"]) + 1
                self._insert(conn, rec)
                outcome.revised += 1
            conn.commit()
        return outcome

    @staticmethod
    def _diff(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, tuple[Any, Any]]:
        """Fields whose stored value disagrees with the incoming value."""
        diffs: dict[str, tuple[Any, Any]] = {}
        for field in ("open_panna", "open_ank", "close_panna", "close_ank", "jodi"):
            old, new = existing.get(field), incoming.get(field)
            if new is None:
                continue  # absence of evidence is not a revision
            old_norm = str(old) if old is not None else None
            new_norm = str(new) if new is not None else None
            if old_norm != new_norm:
                diffs[field] = (old, new)
        return diffs

    def _insert(self, conn: sqlite3.Connection, rec: Mapping[str, Any]) -> int:
        cur = conn.execute(
            """
            INSERT INTO historical_results
                (market_id, result_date, open_panna, open_ank, close_panna, close_ank,
                 jodi, source_id, source_url, source_timestamp, extraction_timestamp,
                 verification_status, dataset, raw_payload, notes)
            VALUES (:market_id, :result_date, :open_panna, :open_ank, :close_panna,
                    :close_ank, :jodi, :source_id, :source_url, :source_timestamp,
                    :extraction_timestamp, :verification_status, :dataset, :raw_payload,
                    :notes)
            """,
            {**rec, "dataset": self.dataset},
        )
        return int(cur.lastrowid)

    def save_bidding_quotes(self, rows: Sequence[Mapping[str, Any]]) -> int:
        """Upsert bidding quotes (market-side prices, not results).

        One row per (date, side, ank); a revised quote updates the stored row.
        The feed itself is audited through ``bidding_feed_runs`` by the caller.
        """
        if not rows:
            return 0
        with self.session() as conn:
            conn.executemany(
                """
                INSERT INTO bidding_quotes
                    (market_id, result_date, quote_side, ank, rate, volume,
                     source_id, source_url, source_timestamp, extraction_timestamp,
                     dataset, raw_payload, notes)
                VALUES (:market_id, :result_date, :quote_side, :ank, :rate, :volume,
                        :source_id, :source_url, :source_timestamp, :extraction_timestamp,
                        :dataset, :raw_payload, :notes)
                ON CONFLICT (market_id, result_date, quote_side, ank) DO UPDATE SET
                    rate = excluded.rate,
                    volume = excluded.volume,
                    source_id = excluded.source_id,
                    source_url = excluded.source_url,
                    source_timestamp = excluded.source_timestamp,
                    extraction_timestamp = excluded.extraction_timestamp,
                    raw_payload = excluded.raw_payload,
                    notes = excluded.notes
                """,
                [
                    {
                        "market_id": self.market_id,
                        "result_date": r["result_date"],
                        "quote_side": r["quote_side"],
                        "ank": int(r["ank"]),
                        "rate": float(r["rate"]),
                        "volume": r.get("volume"),
                        "source_id": r.get("source_id", ""),
                        "source_url": r.get("source_url"),
                        "source_timestamp": r.get("source_timestamp"),
                        "extraction_timestamp": r.get("extraction_timestamp", utcnow()),
                        "dataset": self.dataset,
                        "raw_payload": r.get("raw_payload"),
                        "notes": r.get("notes"),
                    }
                    for r in rows
                ],
            )
            conn.commit()
        return len(rows)

    def bidding_quotes(self) -> pd.DataFrame:
        with self.session(read_only=True) as conn:
            df = pd.read_sql_query(
                "SELECT * FROM bidding_quotes ORDER BY result_date, quote_side, ank",
                conn,
            )
        if df.empty:
            return df
        df["result_date"] = pd.to_datetime(df["result_date"])
        return df

    # reads
    # ------------------------------------------------------------------
    def results(self, *, active_only: bool = True) -> pd.DataFrame:
        """Return the chronological result table for this market."""
        where = "WHERE is_active = 1" if active_only else ""
        with self.session(read_only=True) as conn:
            df = pd.read_sql_query(
                f"SELECT {', '.join(RESULT_COLUMNS)} FROM historical_results {where} "
                f"ORDER BY result_date",
                conn,
            )
        if df.empty:
            return pd.DataFrame(columns=RESULT_COLUMNS)
        df["result_date"] = pd.to_datetime(df["result_date"])
        for col in ("open_ank", "close_ank", "record_version"):
            if col in df:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        for col in ("open_panna", "close_panna", "jodi"):
            if col in df:
                df[col] = df[col].astype("string")
        return df.sort_values("result_date").reset_index(drop=True)

    def target_series(self, target: str) -> pd.Series:
        """Ordered outcome series for a target, index = result_date."""
        spec = self.market.target(target)
        df = self.results()
        if df.empty:
            return pd.Series(dtype="object", name=target)
        col = spec.field
        if col not in df.columns:
            raise KeyError(f"market '{self.market_id}' has no field '{col}'")
        series = df.set_index("result_date")[col].dropna()
        if spec.space == "jodi":
            series = series.astype(str).str.zfill(2)
        elif spec.space == "ank":
            series = series.astype(int)
        return series.rename(target)

    def coverage(self) -> dict[str, Any]:
        """Extraction coverage summary - the honest version, gaps included."""
        df = self.results()
        if df.empty:
            return {
                "market_id": self.market_id, "n_records": 0, "oldest": None,
                "newest": None, "missing_dates": 0, "duplicate_dates": 0,
                "by_year": {}, "by_component": {}, "coverage_pct": 0.0,
            }
        dates = df["result_date"].dt.normalize()
        span_days = max((dates.max() - dates.min()).days + 1, 1)
        by_year = dates.dt.year.value_counts().sort_index().to_dict()
        return {
            "market_id": self.market_id,
            "n_records": int(len(df)),
            "oldest": dates.min().date().isoformat(),
            "newest": dates.max().date().isoformat(),
            "span_days": int(span_days),
            "missing_dates": int(span_days - dates.nunique()),
            "duplicate_dates": int(len(dates) - dates.nunique()),
            "coverage_pct": round(100.0 * dates.nunique() / span_days, 2),
            "by_year": {int(k): int(v) for k, v in by_year.items()},
            "by_component": {
                "open_ank": int(df["open_ank"].notna().sum()),
                "close_ank": int(df["close_ank"].notna().sum()),
                "jodi": int(df["jodi"].notna().sum()),
                "open_panna": int(df["open_panna"].notna().sum()),
                "close_panna": int(df["close_panna"].notna().sum()),
            },
            "distinct_verification_status": sorted(df["verification_status"].dropna().unique().tolist()),
            "dataset": self.dataset,
        }

    def revision_log(self) -> pd.DataFrame:
        with self.session(read_only=True) as conn:
            return pd.read_sql_query(
                "SELECT * FROM result_revisions ORDER BY revision_id", conn
            )

    # ------------------------------------------------------------------
    # quality / metadata writes
    # ------------------------------------------------------------------
    def record_quality(self, rows: Sequence[Mapping[str, Any]], run_id: int | None = None) -> None:
        with self.session() as conn:
            conn.executemany(
                """
                INSERT INTO data_quality
                    (run_id, market_id, check_name, severity, passed, metric_name,
                     metric_value, detail, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id, self.market_id, r["check_name"], r["severity"],
                        int(r["passed"]), r.get("metric_name"), r.get("metric_value"),
                        r.get("detail", ""), utcnow(),
                    )
                    for r in rows
                ],
            )
            conn.commit()

    def latest_quality(self) -> pd.DataFrame:
        with self.session(read_only=True) as conn:
            return pd.read_sql_query(
                """
                SELECT q.* FROM data_quality q
                JOIN (SELECT check_name, MAX(created_at) AS ts
                        FROM data_quality GROUP BY check_name) m
                  ON q.check_name = m.check_name AND q.created_at = m.ts
                WHERE q.market_id = ?
                ORDER BY q.severity DESC, q.check_name
                """,
                conn, params=(self.market_id,),
            )

    def record_update(self, run_type: str, status: str, started_at: str,
                      new_records: int = 0, revised_records: int = 0,
                      new_watermark: str | None = None, error_text: str = "") -> None:
        with self.session() as conn:
            conn.execute(
                """
                INSERT INTO update_history
                    (market_id, run_type, started_at, finished_at, status,
                     new_records, revised_records, new_watermark, error_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (self.market_id, run_type, started_at, utcnow(), status,
                 new_records, revised_records, new_watermark, error_text),
            )
            conn.commit()

    def extraction_history(self) -> pd.DataFrame:
        with self.session(read_only=True) as conn:
            return pd.read_sql_query(
                "SELECT * FROM extraction_runs WHERE market_id = ? ORDER BY run_id DESC",
                conn, params=(self.market_id,),
            )

    # ------------------------------------------------------------------
    # analytics writes
    # ------------------------------------------------------------------
    def save_method_results(self, rows: Sequence[Mapping[str, Any]]) -> int:
        """Replace the stored results for the (market, target) this batch covers.

        A re-run must not append a second, slightly different copy of the same
        numbers: the table holds *the* result of each method, and the run_id column
        records which run produced it.
        """
        if not rows:
            return 0
        with self.session() as conn:
            targets = sorted({str(r.get("target")) for r in rows})
            for target in targets:
                conn.execute(
                    "DELETE FROM method_results WHERE market_id = ? AND target = ?",
                    (self.market_id, target),
                )
            conn.executemany(
                """
                INSERT INTO method_results
                    (method_id, method_name, category, market_id, target, scope,
                     metric_name, metric_value, statistic, p_value, p_adjusted,
                     effect_size, sample_size, extra_json, run_id, computed_at)
                VALUES (:method_id, :method_name, :category, :market_id, :target, :scope,
                        :metric_name, :metric_value, :statistic, :p_value, :p_adjusted,
                        :effect_size, :sample_size, :extra_json, :run_id, :computed_at)
                """,
                [
                    {
                        "method_id": r["method_id"],
                        "method_name": r["method_name"],
                        "category": r["category"],
                        "market_id": r.get("market_id", self.market_id),
                        "target": r.get("target"),
                        "scope": r.get("scope", "full_sample"),
                        "metric_name": r["metric_name"],
                        "metric_value": _f(r.get("metric_value")),
                        "statistic": _f(r.get("statistic")),
                        "p_value": _f(r.get("p_value")),
                        "p_adjusted": _f(r.get("p_adjusted")),
                        "effect_size": _f(r.get("effect_size")),
                        "sample_size": r.get("sample_size"),
                        "extra_json": json.dumps(r.get("extra"), default=str)
                        if r.get("extra") is not None else None,
                        "run_id": r.get("run_id"),
                        "computed_at": r.get("computed_at", utcnow()),
                    }
                    for r in rows
                ],
            )
            conn.commit()
        return len(rows)

    def method_results(self) -> pd.DataFrame:
        with self.session(read_only=True) as conn:
            return pd.read_sql_query(
                "SELECT * FROM method_results ORDER BY method_id, target", conn
            )

    def save_features(self, df: pd.DataFrame, target: str, feature_version: str) -> int:
        if df.empty:
            return 0
        long = df.melt(id_vars=["result_date"], var_name="feature_name", value_name="feature_value")
        long["feature_value"] = pd.to_numeric(long["feature_value"], errors="coerce")
        now = utcnow()
        with self.session() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO market_features
                    (market_id, result_date, target, feature_name, feature_value,
                     feature_version, computed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (self.market_id, str(r.result_date)[:10], target, r.feature_name,
                     None if pd.isna(r.feature_value) else float(r.feature_value),
                     feature_version, now)
                    for r in long.itertuples()
                ],
            )
            conn.commit()
        return len(long)

    def register_model(self, *, target: str, model_name: str, model_version: str,
                       config: Mapping[str, Any], feature_version: str,
                       trained_from: str, trained_to: str, train_size: int,
                       metrics: Mapping[str, Any], is_selected: bool,
                       artifact_path: str | None = None) -> int:
        with self.session() as conn:
            cur = conn.execute(
                """
                INSERT INTO model_registry
                    (market_id, target, model_name, model_version, config_json,
                     feature_version, trained_from, trained_to, train_size,
                     metrics_json, is_selected, artifact_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (self.market_id, target, model_name, model_version,
                 json.dumps(config, default=str), feature_version, trained_from,
                 trained_to, train_size, json.dumps(metrics, default=str),
                 int(is_selected), artifact_path, utcnow()),
            )
            conn.commit()
            return int(cur.lastrowid)

    def save_backtest(self, *, model_id: int | None, target: str, scheme: str,
                      test_start: str, test_end: str, n_predictions: int,
                      metrics: Mapping[str, Any], calibration: Mapping[str, Any],
                      baselines: Mapping[str, Any]) -> int:
        with self.session() as conn:
            cur = conn.execute(
                """
                INSERT INTO backtest_results
                    (model_id, market_id, target, scheme, test_start, test_end,
                     n_predictions, log_loss, brier, accuracy, top3, top5,
                     calibration_json, baseline_json, metrics_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (model_id, self.market_id, target, scheme, test_start, test_end,
                 n_predictions, _f(metrics.get("log_loss")), _f(metrics.get("brier")),
                 _f(metrics.get("accuracy")), _f(metrics.get("top3")), _f(metrics.get("top5")),
                 json.dumps(calibration, default=str),
                 json.dumps(baselines, default=str),
                 json.dumps(metrics, default=str), utcnow()),
            )
            conn.commit()
            return int(cur.lastrowid)

    def save_predictions(self, rows: Sequence[Mapping[str, Any]]) -> int:
        if not rows:
            return 0
        with self.session() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO predictions
                    (market_id, target, target_date, model_id, model_version, cutoff_date,
                     train_size, feature_version, prob_json, ranked_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (self.market_id, r["target"], r["target_date"], r.get("model_id"),
                     r["model_version"], r.get("cutoff_date"), r.get("train_size"),
                     r.get("feature_version"), json.dumps(r["probs"]),
                     json.dumps(r["ranked"]), r.get("created_at", utcnow()))
                    for r in rows
                ],
            )
            conn.commit()
        return len(rows)

    def save_outcomes(self, rows: Sequence[Mapping[str, Any]]) -> int:
        if not rows:
            return 0
        with self.session() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO prediction_outcomes
                    (prediction_id, actual_value, correct_exact, rank_of_actual,
                     log_loss_i, brier_i, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (r["prediction_id"], str(r["actual_value"]), int(r["correct_exact"]),
                     r.get("rank_of_actual"), _f(r.get("log_loss_i")),
                     _f(r.get("brier_i")), utcnow())
                    for r in rows
                ],
            )
            conn.commit()
        return len(rows)

    def ledger(self) -> pd.DataFrame:
        """Joined prediction ledger: forecast, realisation, metrics."""
        with self.session(read_only=True) as conn:
            return pd.read_sql_query(
                """
                SELECT p.*, o.actual_value, o.correct_exact, o.rank_of_actual,
                       o.log_loss_i, o.brier_i
                  FROM predictions p
                  LEFT JOIN prediction_outcomes o ON o.prediction_id = p.prediction_id
                 ORDER BY p.target, p.target_date
                """,
                conn,
            )

    def save_cross_market_tests(self, rows: Sequence[Mapping[str, Any]]) -> int:
        """Replace this pair's stored cross-market tests (idempotent re-analysis)."""
        if not rows:
            return 0
        pairs = sorted({(str(r["market_a"]), str(r["market_b"])) for r in rows})
        with self.session() as conn:
            for market_a, market_b in pairs:
                conn.execute(
                    "DELETE FROM cross_market_tests WHERE market_a = ? AND market_b = ?",
                    (market_a, market_b),
                )
            conn.executemany(
                """
                INSERT INTO cross_market_tests
                    (market_a, market_b, component_a, component_b, lag, method,
                     statistic, p_value, p_adjusted, effect_size, n_obs, stability,
                     verdict, extra_json, created_at)
                VALUES (:market_a, :market_b, :component_a, :component_b, :lag, :method,
                        :statistic, :p_value, :p_adjusted, :effect_size, :n_obs,
                        :stability, :verdict, :extra_json, :created_at)
                """,
                [
                    {
                        "market_a": r["market_a"], "market_b": r["market_b"],
                        "component_a": r["component_a"], "component_b": r["component_b"],
                        "lag": int(r["lag"]), "method": r["method"],
                        "statistic": _f(r.get("statistic")),
                        "p_value": _f(r.get("p_value")),
                        "p_adjusted": _f(r.get("p_adjusted")),
                        "effect_size": _f(r.get("effect_size")),
                        "n_obs": r.get("n_obs"),
                        "stability": _f(r.get("stability")),
                        "verdict": r.get("verdict"),
                        "extra_json": json.dumps(r.get("extra"), default=str)
                        if r.get("extra") is not None else None,
                        "created_at": r.get("created_at", utcnow()),
                    }
                    for r in rows
                ],
            )
            conn.commit()
        return len(rows)

    def cross_market_tests(self) -> pd.DataFrame:
        with self.session(read_only=True) as conn:
            return pd.read_sql_query(
                "SELECT * FROM cross_market_tests ORDER BY market_a, market_b, component_a, lag",
                conn,
            )

    def identity(self) -> dict[str, str]:
        with self.session(read_only=True) as conn:
            try:
                rows = conn.execute("SELECT key, value FROM database_identity").fetchall()
            except sqlite3.Error:
                return {}
        return {r["key"]: r["value"] for r in rows}


def _f(value: Any) -> float | None:
    """Coerce to a finite float or None (SQLite cannot store NaN/inf)."""
    if value is None:
        return None
    try:
        fval = float(value)
    except (TypeError, ValueError):
        return None
    if fval != fval or fval in (float("inf"), float("-inf")):
        return None
    return fval
