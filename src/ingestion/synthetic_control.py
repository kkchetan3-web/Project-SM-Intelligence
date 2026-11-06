"""Synthetic control datasets - the substitute for data this environment cannot fetch.

WHY THIS EXISTS
---------------
The source hosts are unreachable from the build sandbox (egress is restricted to
a small allowlist; every attempt returns ``SSL_ERROR_SYSCALL``). The scientific
rules forbid inventing market history, so instead of a fake "Kalyan" dataset we
generate two explicitly-synthetic worlds with *known* data-generating processes:

``synthetic_null`` (H0)
    Draws are i.i.d. uniform on 0-9, markets independent. There is nothing to
    find. A correctly-built research platform must conclude "no predictive
    information" - and if it instead reports a discovery, the platform is broken.

``synthetic_signal`` (H1)
    Draws follow a first-order Markov chain with a known transition matrix, and
    Main Bazar's close has a weak, publication-order-respecting dependence on
    Kalyan's same-day open. The platform must detect *some* of this out of sample.

Together they are a two-sided calibration test of the whole pipeline: a false
positive rate that is honest, and a power that is non-zero. Every row written by
this module is stamped ``synthetic_control`` and lives under a separate database
tree, so it can never be reported as market data.

The generator is seeded and its parameters are recorded in the manifest, so the
controls are exactly reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import numpy as np

from src.core.configuration import Config
from src.core.logging import get_logger
from src.core.provenance import ExtractionLedger, content_hash, utcnow
from src.storage.market_database import MarketDatabase

log = get_logger(__name__)

SYNTHETIC_STATUS = "synthetic_control"


@dataclass(frozen=True)
class ControlSpec:
    """The data-generating process, stated explicitly so it can be audited."""

    name: str
    start: date
    end: date
    # Persistence weight: 0 -> i.i.d. uniform; >0 -> mass moved to (previous + 1) % 10
    open_persistence: float
    close_persistence: float
    marginal_tilt: float
    # Main Bazar close depends on Kalyan's same-day open by this much.
    cross_market_strength: float
    seed: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "open_persistence": self.open_persistence,
            "marginal_tilt": self.marginal_tilt,
            "close_persistence": self.close_persistence,
            "cross_market_strength": self.cross_market_strength,
            "seed": self.seed,
            "distribution": "categorical over 0-9",
            "draw_calendar": "Mon-Sat (Sunday excluded)",
        }


NULL_SPEC = ControlSpec(
    name="synthetic_null", start=date(2016, 1, 1), end=date(2025, 12, 31),
    open_persistence=0.0, close_persistence=0.0, marginal_tilt=0.0,
    cross_market_strength=0.0, seed=20250101,
)

SIGNAL_SPEC = ControlSpec(
    name="synthetic_signal", start=date(2016, 1, 1), end=date(2025, 12, 31),
    open_persistence=0.30, close_persistence=0.22, marginal_tilt=0.12,
    cross_market_strength=0.18, seed=20250101,
)


def trading_days(start: date, end: date) -> list[date]:
    """Mon-Sat calendar; these markets do not draw on Sunday."""
    days: list[date] = []
    cursor = start
    while cursor <= end:
        if cursor.weekday() != 6:
            days.append(cursor)
        cursor += timedelta(days=1)
    return days


def _transition_matrix(rng: np.random.Generator, persistence: float,
                       tilt: float = 0.0) -> np.ndarray:
    """Base(1/K) mass plus ``persistence`` mass on the successor state.

    The successor is ``(state + 1) % 10`` rather than the state itself, because
    pure self-persistence is trivially detectable and would overstate the power
    test. The remaining mass is spread unevenly (a mild preference profile) so
    the marginal is deliberately *not* perfectly uniform - which also exercises
    the frequency-based methods.
    """
    k = 10
    base = np.full((k, k), (1.0 - persistence) / k)
    for i in range(k):
        base[i, (i + 1) % k] += persistence
    # Optional deterministic preference structure. The H0 world must be exactly
    # uniform, so tilt is 0 there; only the H1 world carries a mild imbalance.
    preference = 1.0 + tilt * np.cos(2 * np.pi * np.arange(k) / k * 2)
    base = base * preference[None, :]
    return base / base.sum(axis=1, keepdims=True)


def _sample_chain(rng: np.random.Generator, n: int, matrix: np.ndarray) -> np.ndarray:
    states = np.empty(n, dtype=int)
    states[0] = rng.integers(0, matrix.shape[0])
    cumulative = np.cumsum(matrix, axis=1)
    for t in range(1, n):
        u = rng.random()
        states[t] = int(np.searchsorted(cumulative[states[t - 1]], u))
    return states


def _panna_for_ank(rng: np.random.Generator, ank: int) -> str:
    """A 3-digit panel whose digit sum mod 10 equals ``ank`` (as the real charts do)."""
    digits = rng.integers(0, 10, size=3)
    current = int(digits.sum() % 10)
    if current != ank:
        # Adjust the last digit - always possible for a modulus of 10.
        digits[2] = (digits[2] + (ank - current)) % 10
    return "".join(str(int(d)) for d in digits)


def generate(spec: ControlSpec) -> dict[str, list[dict[str, Any]]]:
    """Build the result rows for both markets under ``spec``."""
    rng = np.random.default_rng(spec.seed)
    days = trading_days(spec.start, spec.end)
    n = len(days)

    open_matrix = _transition_matrix(rng, spec.open_persistence, spec.marginal_tilt)
    close_matrix = _transition_matrix(rng, spec.close_persistence, spec.marginal_tilt)

    kalyan_open = _sample_chain(rng, n, open_matrix)
    kalyan_close = _sample_chain(rng, n, close_matrix)

    if spec.cross_market_strength > 0:
        # Main Bazar's Open follows the same process; its Close is a mixture of
        # its own chain and Kalyan's *earlier-published* same-day Open.
        mb_open = _sample_chain(rng, n, open_matrix)
        mb_close_own = _sample_chain(rng, n, close_matrix)
        shift = spec.cross_market_strength
        mb_close = np.array([
            kalyan_open[t] if rng.random() < shift else mb_close_own[t]
            for t in range(n)
        ])
    else:
        mb_open = _sample_chain(rng, n, open_matrix)
        mb_close = _sample_chain(rng, n, close_matrix)

    out: dict[str, list[dict[str, Any]]] = {"kalyan": [], "main_bazar": []}
    for market_id, open_seq, close_seq in (
        ("kalyan", kalyan_open, kalyan_close),
        ("main_bazar", mb_open, mb_close),
    ):
        for idx, day in enumerate(days):
            o_ank = int(open_seq[idx])
            c_ank = int(close_seq[idx])
            out[market_id].append({
                "market_id": market_id,
                "result_date": day.isoformat(),
                "open_panna": _panna_for_ank(rng, o_ank),
                "open_ank": o_ank,
                "close_panna": _panna_for_ank(rng, c_ank),
                "close_ank": c_ank,
                "jodi": f"{o_ank}{c_ank}",
                "source_id": "synthetic_generator",
                "source_url": None,
                "source_timestamp": None,
                "extraction_timestamp": utcnow(),
                "verification_status": SYNTHETIC_STATUS,
                "raw_payload": {"generator": "src.ingestion.synthetic_control",
                                "spec": spec.as_dict()},
                "notes": f"{spec.name}: controlled DGP, not market data",
            })
    return out


def build_dataset(config: Config, spec: ControlSpec, *, rebuild: bool = False) -> dict[str, Any]:
    """Materialise one control dataset into its own database tree."""
    if config.dataset.name != spec.name:
        raise ValueError(
            f"config dataset is '{config.dataset.name}' but spec is '{spec.name}'; "
            "refusing to mix control worlds"
        )
    log.info("generating control dataset %s (%s..%s)", spec.name, spec.start, spec.end)
    frames = generate(spec)
    summary: dict[str, Any] = {"spec": spec.as_dict(), "markets": {}}
    for market_id, rows in frames.items():
        config.database_path(market_id).unlink(missing_ok=True)
        db = MarketDatabase(config, market_id)
        db.manager.initialise(market_id)
        outcome = db.upsert_results(rows)
        record_generation_provenance(config, market_id, spec, n_rows=len(rows),
                                     inserted=outcome.inserted)
        db.record_update("synthetic_generation", "ok", utcnow(),
                         new_records=outcome.inserted, new_watermark=rows[-1]["result_date"])
        summary["markets"][market_id] = {
            "generated": len(rows), "inserted": outcome.inserted,
            "rejected": outcome.rejected, "errors": outcome.errors[:5],
            "oldest": rows[0]["result_date"], "newest": rows[-1]["result_date"],
        }
        log.info("%s: %d rows generated, %d inserted, %d rejected",
                 market_id, len(rows), outcome.inserted, outcome.rejected)
    summary["generated_at"] = utcnow()
    return summary


def record_generation_provenance(config: Config, market_id: str, spec: ControlSpec, *,
                                 n_rows: int, inserted: int | None = None,
                                 when: str | None = None) -> int | None:
    """Write the generation act into `extraction_runs` / `source_records`.

    The provenance tables exist so every number in a database can be traced to the
    act that produced it. For a control dataset that act is *generation*, not
    fetching, and it is recorded as such: one run per market and one source record
    whose URL is `synthetic://<dataset>/<market>` and whose notes carry the seed and
    the full generator parameters. Idempotent: a market that already has a
    successful `synthetic_generator` run is not recorded twice.
    """
    db = MarketDatabase(config, market_id)
    url = f"synthetic://{spec.name}/{market_id}"
    notes = (
        f"seed={spec.seed} start={spec.start.isoformat()} end={spec.end.isoformat()} "
        f"open_persistence={spec.open_persistence} close_persistence={spec.close_persistence} "
        f"marginal_tilt={spec.marginal_tilt} cross_market_strength={spec.cross_market_strength} "
        f"generated_by=src.ingestion.synthetic_control.generate"
    )
    with db.session() as conn:
        # Idempotent on the *content* of the record, not just on the source id:
        # a second backfill of the same spec must not append a second run.
        existing = conn.execute(
            "SELECT r.run_id FROM extraction_runs r "
            "JOIN source_records s ON s.run_id = r.run_id "
            "WHERE r.market_id = ? AND r.source_id = ? AND r.status = 'ok' AND s.notes = ? "
            "ORDER BY r.run_id DESC LIMIT 1",
            (market_id, "synthetic_generator", notes),
        ).fetchone()
        if existing is not None:
            return None
        with ExtractionLedger(conn, market_id, "synthetic_generator",
                              config.fingerprint()) as run:
            run.record_page(url, None, True, byte_size=0, parse_status="generated",
                            notes=notes, body=notes)
            run.finish("ok", pages_requested=1, pages_ok=1, pages_failed=0,
                       records_seen=n_rows, records_inserted=int(inserted or n_rows),
                       records_revised=0,
                       error_text="" if when is None else f"backfilled_at={utcnow()} original={when}")
            return run.run_id
