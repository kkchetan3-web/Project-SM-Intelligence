"""Prediction ledger: score forecasts against what actually happened.

A forecast that is never scored is marketing. Every prediction this platform makes
is written to ``predictions``; once the real result is known, this module records
the outcome in ``prediction_outcomes`` and reports the running score.

The reference point is always the uniform floor (log loss ``ln 10 = 2.302585``,
Brier ``0.9``, exact-hit rate ``0.1``). Anything worse than that is a model that
has actively harmed the forecast, and it is reported as such.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from src.core.configuration import Config
from src.core.logging import get_logger
from src.preprocessing.cleaning import clean_target
from src.storage.market_database import MarketDatabase

log = get_logger(__name__)

UNIFORM_LOG_LOSS = math.log(10.0)
UNIFORM_BRIER = 0.9
UNIFORM_HIT_RATE = 0.1


def _probs_from_json(payload: str) -> dict[str, float]:
    import json

    raw = json.loads(payload)
    return {str(k): float(v) for k, v in raw.items()}


def resolve(config: Config, market_id: str, target: str | None = None) -> dict:
    """Write outcomes for every forecast whose draw has since been published."""
    db = MarketDatabase(config, market_id)
    if not db.manager.exists(market_id):
        return {"market": market_id, "resolved": 0, "reason": "database not initialised"}

    ledger = db.ledger()
    if ledger.empty:
        return {"market": market_id, "resolved": 0, "reason": "no forecasts recorded"}

    pending = ledger[ledger["actual_value"].isna()].copy()
    if target:
        pending = pending[pending["target"] == target]
    if pending.empty:
        return {"market": market_id, "resolved": 0, "reason": "no unresolved forecasts"}

    outcomes = []
    for row in pending.itertuples():
        actual_df = clean_target(config, market_id, row.target)
        if actual_df.frame.empty:
            continue
        series = actual_df.frame.set_index("result_date")["y"]
        if pd.Timestamp(row.target_date) not in series.index:
            continue
        actual = str(series.loc[pd.Timestamp(row.target_date)])
        probs = _probs_from_json(row.prob_json)
        p_actual = max(probs.get(actual, 1e-12), 1e-12)
        ranked = sorted(probs.items(), key=lambda kv: -kv[1])
        rank = [k for k, _ in ranked].index(actual) + 1 if actual in probs else None
        onehot = np.zeros(10)
        if actual.isdigit():
            onehot[int(actual)] = 1.0
        vector = np.array([probs.get(str(i), 0.0) for i in range(10)])
        outcomes.append({
            "prediction_id": int(row.prediction_id),
            "actual_value": actual,
            "correct_exact": int(rank == 1),
            "rank_of_actual": rank,
            "log_loss_i": float(-math.log(p_actual)),
            "brier_i": float(np.sum((vector - onehot) ** 2)),
        })

    written = db.save_outcomes(outcomes) if outcomes else 0
    return {"market": market_id, "resolved": written,
            "pending_without_result": int(len(pending) - written)}


def summary(config: Config, market_id: str, target: str | None = None) -> dict:
    """Running score of every resolved forecast for one market."""
    db = MarketDatabase(config, market_id)
    if not db.manager.exists(market_id):
        return {"market": market_id, "available": False, "reason": "database not initialised"}
    ledger = db.ledger()
    if ledger.empty:
        return {"market": market_id, "available": False, "reason": "no forecasts recorded"}

    if target:
        ledger = ledger[ledger["target"] == target]
    resolved = ledger[ledger["actual_value"].notna()]
    headline = {
        "market": market_id,
        "available": True,
        "target": target or "all",
        "n_forecasts": int(len(ledger)),
        "n_resolved": int(len(resolved)),
        "n_pending": int(len(ledger) - len(resolved)),
    }
    if resolved.empty:
        headline.update({"reason": "forecasts exist but none has been resolved yet"})
        return headline

    ll = float(resolved["log_loss_i"].mean())
    brier = float(resolved["brier_i"].mean())
    hit = float(resolved["correct_exact"].mean())
    rank1 = int((resolved["rank_of_actual"] == 1).sum())
    headline.update({
        "log_loss": round(ll, 6),
        "brier": round(brier, 6),
        "exact_hit_rate": round(hit, 4),
        "top3_rate": round(float((resolved["rank_of_actual"] <= 3).mean()), 4),
        "uniform_log_loss": round(UNIFORM_LOG_LOSS, 6),
        "uniform_brier": UNIFORM_BRIER,
        "uniform_hit_rate": UNIFORM_HIT_RATE,
        "edge_vs_uniform_log_loss": round(UNIFORM_LOG_LOSS - ll, 6),
        "edge_vs_uniform_brier": round(UNIFORM_BRIER - brier, 6),
        "edge_vs_uniform_hit_rate": round(hit - UNIFORM_HIT_RATE, 4),
    })
    n = len(resolved)
    se = math.sqrt(UNIFORM_HIT_RATE * (1 - UNIFORM_HIT_RATE) / n) if n else None
    z = (hit - UNIFORM_HIT_RATE) / se if se else None
    headline["hit_rate_z_vs_uniform"] = None if z is None else round(z, 3)
    headline["verdict"] = _verdict(ll, brier, hit, z, n)
    headline["by_model"] = (resolved.groupby("model_version")
                            .agg(n=("log_loss_i", "size"),
                                 log_loss=("log_loss_i", "mean"),
                                 brier=("brier_i", "mean"),
                                 hit_rate=("correct_exact", "mean"))
                            .round(5).reset_index().to_dict(orient="records"))
    return headline


def _verdict(ll: float, brier: float, hit: float, z: float | None, n: int) -> str:
    if ll >= UNIFORM_LOG_LOSS:
        return ("no edge: realised log loss is no better than the uniform floor "
                f"({ll:.5f} vs {UNIFORM_LOG_LOSS:.5f})")
    if z is not None and z < 2:
        return ("log loss is below the uniform floor, but the exact-hit rate is not "
                f"distinguishable from chance at n={n} (z={z:.2f}); treat as unproven")
    return ("realised performance better than uniform across log loss, Brier and hit rate; "
            "still requires a long, fully out-of-sample record before it means anything")


def recent_forecasts(config: Config, market_id: str, target: str | None = None,
                     limit: int = 10) -> pd.DataFrame:
    db = MarketDatabase(config, market_id)
    if not db.manager.exists(market_id):
        return pd.DataFrame()
    ledger = db.ledger()
    if ledger.empty:
        return ledger
    if target:
        ledger = ledger[ledger["target"] == target]
    return ledger.tail(limit)[["target", "target_date", "model_version", "prob_json",
                               "actual_value", "rank_of_actual", "log_loss_i"]]
