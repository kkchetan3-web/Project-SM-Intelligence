"""Does the player-psychology channel carry ANY predictive signal?

The channel (src/preprocessing/psychology.py) is a proxy for what players bet
on: recent heat, cold streaks, coverage, jodi repetition. Whether that moves
the next draw is an empirical question, and this script answers it directly
on the real history:

* for every channel feature, history is binned by the feature's value and the
  next-draw distribution is compared across bins (chi-square) and scored
  against uniform (log loss);
* the jodi channel is checked the same way on the open+close pairs;
* nothing is fitted, tuned or selected - the numbers are descriptive tests.

Usage:
    python scripts/psychology_signal_check.py [--dataset live] [--market kalyan]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.core.configuration import load_config
from src.preprocessing.psychology import (PsychologyConfig, jodi_psychology_features,
                                          psychology_features)

UNIFORM_LL = float(np.log(10))


def _load_series(db_path: Path, table: str, column: str) -> np.ndarray:
    import sqlite3

    conn = sqlite3.connect(db_path)
    try:
        rows = [r[0] for r in conn.execute(
            f"select {column} from {table} where {column} is not null order by result_date")]
    finally:
        conn.close()
    return np.asarray(rows, dtype=int)


def _check_feature(name: str, values: np.ndarray, next_y: np.ndarray,
                   n_outcomes: int = 10) -> dict:
    """Bin history by one feature value; test next-draw distribution across bins."""
    mask = np.isfinite(values)
    v, y = values[mask], next_y[mask]
    if len(v) < 300 or np.unique(y).size < 5:
        return {"feature": name, "n": int(len(v)), "skipped": "too few rows"}
    # Decile binning on the observed distribution.
    cuts = np.quantile(v, np.linspace(0, 1, 11))
    cuts[0], cuts[-1] = -np.inf, np.inf
    idx = np.clip(np.searchsorted(cuts, v, side="right") - 1, 0, 9)
    k = n_outcomes
    table = np.zeros((10, k))
    for i in range(10):
        yi = y[idx == i]
        table[i] = np.bincount(yi, minlength=k)
    keep = table.sum(axis=1) > 0
    table = table[keep]
    if table.shape[0] < 2:
        return {"feature": name, "n": int(len(v)), "skipped": "single non-empty bin"}
    chi2, p, dof, _ = stats.chi2_contingency(table)
    # Log loss of "predict the bin's own empirical distribution" vs uniform.
    ll = 0.0
    kept_bins = np.flatnonzero(keep)
    for i in kept_bins:
        yi = y[idx == i]
        if len(yi) == 0:
            continue
        p_bin = table[np.where(kept_bins == i)[0][0]] / max(len(yi), 1)
        p_bin = np.where(p_bin > 0, p_bin, 1e-12)
        ll += float(np.sum(-np.log(p_bin[yi])))
    ll /= len(y)
    return {"feature": name, "n": int(len(v)), "chi2": float(chi2), "p": float(p),
            "log_loss": float(ll), "vs_uniform": float(ll - UNIFORM_LL)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="live")
    ap.add_argument("--market", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    config = load_config(dataset=args.dataset)
    markets = [args.market] if args.market else list(config.markets)
    out = {}

    for market_id in markets:
        market_db = config.database_path(market_id)
        if not Path(market_db).exists():
            print(f"{market_id}: database missing, skipped")
            continue
        for target, column in (("open", "open_ank"), ("close", "close_ank")):
            y = _load_series(Path(market_db), "historical_results", column)
            if len(y) < 400:
                continue
            shifted = np.concatenate([[-1], y[:-1]])
            next_y = y  # feature row t (info through draw t-1) predicts draw t;
                        # row 0 is warm-up NaN and is dropped by the mask
            feats = psychology_features(shifted, PsychologyConfig())
            checks = [_check_feature(c, feats[c].to_numpy(), next_y)
                      for c in feats.columns]

            # Jodi channel: needs both open and close.
            o = _load_series(Path(market_db), "historical_results", "open_ank")
            c = _load_series(Path(market_db), "historical_results", "close_ank")
            n = min(len(o), len(c))
            o, c = o[:n], c[:n]
            j_next = o * 10 + c  # feature row t predicts the t-th jodi; row 0 dropped by mask
            jfeats = jodi_psychology_features(
                np.concatenate([[-1], o[:-1]]), np.concatenate([[-1], c[:-1]]),
                PsychologyConfig())
            checks += [_check_feature(c2, jfeats[c2].to_numpy(), j_next,
                                      n_outcomes=100)
                       for c2 in jfeats.columns]

            checks = [x for x in checks if "chi2" in x]
            best = sorted(checks, key=lambda x: x["p"])[:3]
            out[f"{market_id}/{target}"] = {
                "n_draws": int(len(y)),
                "features_checked": len(checks),
                "best_by_p": best,
                "any_beat_uniform": [x["feature"] for x in checks
                                     if x["log_loss"] < UNIFORM_LL - 0.01],
            }
            print(f"{market_id}/{target}: {len(y)} draws, {len(checks)} features")
            for b in best:
                print(f"   best p: {b['feature']} p={b['p']:.4f} "
                      f"chi2={b['chi2']:.1f} ll={b['log_loss']:.4f} "
                      f"(vs uniform {b['vs_uniform']:+.4f})")
            if out[f"{market_id}/{target}"]["any_beat_uniform"]:
                print("   BEAT UNIFORM:", out[f"{market_id}/{target}"]["any_beat_uniform"])
            else:
                print("   nothing beats uniform by >0.01 log loss")

    path = args.out or (REPO / "research" / "psychology_signal_check.json")
    Path(path).write_text(json.dumps(out, indent=2))
    print(f"written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
