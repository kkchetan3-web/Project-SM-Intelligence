"""Cross-market orchestration and leakage validation.

Runs the full cross-market programme for every configured pair, writes the test
rows into **each** market's own database (so a market's file remains a complete
record of what was tested about it), and validates that no cross-market feature
could have used later information.

The leakage validation is not a formality: cross-market feature engineering is the
single easiest place in this platform to introduce look-ahead bias, because the
"obvious" feature - the other market's same-day result - is usually published
later.
"""

from __future__ import annotations

import json

from src.core.configuration import Config
from src.core.logging import get_logger
from src.core.provenance import utcnow
from src.cross_market import conditional_models, dependency_analysis, lead_lag_analysis
from src.cross_market.market_alignment import align, available_at
from src.storage.market_database import MarketDatabase

log = get_logger(__name__)


def validate_no_leakage(config: Config) -> dict:
    """Assert every constructed cross-market feature is strictly lagged."""
    from src.models.close_models import build_frame
    from src.cross_market.conditional_models import cross_market_columns

    checks = []
    for market_id in config.market_order:
        for target in ("open", "close"):
            try:
                frame = build_frame(config, market_id, target, verify=True)
            except Exception as exc:
                checks.append({"market": market_id, "target": target, "ok": False,
                               "error": str(exc)[:200]})
                continue
            foreign = cross_market_columns(frame.X)
            same_day_foreign = [c for c in foreign if c.startswith("x_today")]
            partner = frame.causality.get("foreign_partner")
            declared = (partner, market_id) in config.cross_open_precedence
            # A same-day foreign feature is admissible only if markets.yaml
            # declares that the foreign component is publishd first.
            same_day_ok = (not same_day_foreign) or declared
            checks.append({
                "market": market_id, "target": target,
                "n_foreign_features": len(foreign),
                "foreign_features": foreign,
                "causality_verified": frame.causality.get("passed"),
                "same_day_open_used": frame.causality.get("same_day_open_used", False),
                "same_day_foreign_open_used": bool(frame.causality.get("same_day_foreign_open_used")),
                "same_day_foreign_columns": same_day_foreign,
                "foreign_partner": partner,
                "precedence_declared": declared,
                "ok": bool(frame.causality.get("passed")) and same_day_ok,
            })

    lag_rules = []
    for market_a, market_b in config.cross_market_pairs:
        alignment = align(config, market_a, market_b)
        lag_rules.append({
            "pair": [market_a, market_b],
            "n_matched": alignment.n_matched,
            "lag0_admissible": available_at(alignment, 0),
            "lag_minus1_admissible": available_at(alignment, -1),
            "lag_plus1_admissible": available_at(alignment, 1),
            "policy": ("same-date foreign values are treated as unavailable because historical "
                       "publication timestamps cannot be verified; only strictly lagged values "
                       "(|lag| >= 1) are admitted"),
        })
    return {
        "checked_at": utcnow(),
        "feature_checks": checks,
        "lag_policy": lag_rules,
        "ok": (all(c.get("ok") for c in checks)
               and all(r["lag0_admissible"] is False for r in lag_rules)
               and all(r["lag_minus1_admissible"] and r["lag_plus1_admissible"]
                       for r in lag_rules)),
    }


def run_pair(config: Config, market_a: str, market_b: str) -> dict:
    lead_lag = lead_lag_analysis.investigate_pair(config, market_a, market_b)
    dependency = dependency_analysis.run(config, market_a, market_b, component="open")
    dependency_close = dependency_analysis.run(config, market_a, market_b, component="close")
    feature_tests = []
    for market in (market_a, market_b):
        for target in ("open", "close"):
            try:
                feature_tests.append(conditional_models.test_feature_value(config, market, target))
            except Exception as exc:
                feature_tests.append({"available": False, "target_market": market,
                                      "target": target, "reason": str(exc)[:200]})
    return {
        "pair": [market_a, market_b],
        "lead_lag": lead_lag,
        "dependency_open": dependency,
        "dependency_close": dependency_close,
        "conditional_model_tests": feature_tests,
        "finished_at": utcnow(),
    }


def _persist(config: Config, result: dict) -> int:
    rows = []
    for row in result["lead_lag"]["tests"]:
        rows.append({
            "market_a": row["market_a"], "market_b": row["market_b"],
            "component_a": row["component_a"], "component_b": row["component_b"],
            "lag": row["lag"], "method": "cramers_v_chi2",
            "statistic": row.get("chi2"), "p_value": row["p_value"],
            "p_adjusted": row.get("p_adjusted"), "effect_size": row["cramers_v"],
            "n_obs": row["n_obs"],
            "stability": None,
            "verdict": row.get("verdict"),
            "extra": {"direction": row["direction"],
                      "admissible_same_day": row["admissible_same_day"],
                      "admissible_by_declaration": row.get("admissible_by_declaration", False),
                      "mutual_information": row["mutual_information"]},
        })
    written = 0
    for market_id in result["pair"]:
        db = MarketDatabase(config, market_id)
        if db.manager.exists(market_id):
            written += db.save_cross_market_tests(rows)
    return written


def run_all(config: Config, *, persist: bool = True) -> dict:
    """Full cross-market programme over every configured pair."""
    validation = validate_no_leakage(config)
    pairs = []
    for market_a, market_b in config.cross_market_pairs:
        log.info("cross-market analysis: %s vs %s", market_a, market_b)
        result = run_pair(config, market_a, market_b)
        if persist:
            result["rows_persisted"] = _persist(config, result)
        pairs.append(result)

    summary = {
        "dataset": config.dataset.name,
        "generated_at": utcnow(),
        "leakage_validation": validation,
        "n_pairs": len(pairs),
        "pairs": pairs,
        "headline": _headline(pairs),
    }
    return summary


def _headline(pairs: list[dict]) -> dict:
    if not pairs:
        return {"message": "no cross-market pairs configured"}
    n_tests = sum(p["lead_lag"]["n_tests"] for p in pairs)
    n_sig = sum(p["lead_lag"]["n_significant_holm"] for p in pairs)
    improvements = [
        t for p in pairs for t in p["conditional_model_tests"]
        if t.get("significant_improvement")
    ]
    best_v = max(
        (row for p in pairs for row in p["lead_lag"]["tests"]
         if row["cramers_v"] is not None),
        key=lambda r: r["cramers_v"], default=None)
    return {
        "n_lag_tests": n_tests,
        "n_significant_after_holm": n_sig,
        "n_conditional_tests": sum(len(p["conditional_model_tests"]) for p in pairs),
        "n_demonstrated_predictive_improvements": len(improvements),
        "strongest_association": None if best_v is None else {
            "pair": [best_v["market_a"], best_v["market_b"]],
            "components": [best_v["component_a"], best_v["component_b"]],
            "lag": best_v["lag"], "cramers_v": best_v["cramers_v"],
            "p_adjusted": best_v.get("p_adjusted"), "verdict": best_v.get("verdict"),
        },
        "conclusion": (
            "No cross-market relationship produced a demonstrable out-of-sample predictive "
            "improvement for either market. Markets are therefore modelled independently, and the "
            "cross-market layer remains an analytical overlay rather than an input to prediction."
            if not improvements else
            f"{len(improvements)} conditional-model tests showed a demonstrated out-of-sample "
            f"improvement; those features are eligible for the prediction engine subject to "
            f"re-confirmation on untouched periods."
        ),
    }
