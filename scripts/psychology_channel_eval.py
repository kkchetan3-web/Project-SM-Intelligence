"""Walk-forward evaluation of the player-psychology channel (Kalyan).

The channel (src/preprocessing/psychology.py) is opt-in: the standard pipeline
does not use it. This script asks the platform's own arbiter question - does
adding the channel change any out-of-sample number? - for the market the user
forecasts (Kalyan), running the same 10 walk-forward models with the channel
ON and comparing against:

* the best baseline (uniform, log loss 2.30259 - baselines never consume
  features, so they are identical with the channel on or off);
* the pipeline's own channel-OFF model numbers for the same market/target
  (best svm: 2.30733 open, 2.30624 close), produced by the identical
  walk-forward protocol on the identical data.

Usage:
    python scripts/psychology_channel_eval.py [--dataset live] [--market kalyan]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.backtesting.baselines import make_baselines
from src.backtesting.walk_forward import batch_walk_forward, online_walk_forward
from src.core.configuration import load_config
from src.models.close_models import build_frame
from src.models.market_models import CORE_MODELS, REFIT_SCHEDULE, build
from src.preprocessing.feature_engineering import FeatureConfig

# The channel-OFF numbers from the live pipeline analyse stage (identical
# protocol: same models, same min_train, same refit schedule, same data).
PIPELINE_OFF_BEST = {"kalyan/open": 2.30733, "kalyan/close": 2.30624}
UNIFORM_LL = 2.30259


def evaluate(config, market_id: str, target: str) -> dict:
    research = config.research.get("walk_forward", {})
    min_train = int(research.get("min_train_size", 400))
    frame = build_frame(config, market_id, target, verify=False)
    n = len(frame.y)
    min_train = min(min_train, max(200, int(n * 0.25)))

    from src.models.open_models import build_open_frame

    cfg = FeatureConfig(include_psychology=True)
    if target == "open":
        f = build_open_frame(config, market_id, verify=False, feature_cfg=cfg)
    else:
        f = build_frame(config, market_id, target, verify=False, feature_cfg=cfg)
    X = np.nan_to_num(f.X.to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)

    baselines = online_walk_forward(
        make_baselines(), f.y, pd.DatetimeIndex(f.dates), min_train=min_train,
        market_id=market_id, target=target, ordinal=True)
    best_name = min(baselines, key=lambda k: baselines[k].per_obs_log_loss().mean())
    best_base_ll = float(baselines[best_name].per_obs_log_loss().mean())

    entry = {"features": int(X.shape[1]), "best_baseline": best_name,
             "best_baseline_ll": best_base_ll, "models": {}}
    started = time.time()
    for model_name in CORE_MODELS:
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                result = batch_walk_forward(
                    lambda name=model_name: build(name), X, f.y,
                    pd.DatetimeIndex(f.dates), min_train=min_train,
                    refit_every=REFIT_SCHEDULE.get(model_name, 80),
                    model_name=model_name, market_id=market_id, target=target,
                    ordinal=True)
            entry["models"][model_name] = float(result.per_obs_log_loss().mean())
        except Exception as exc:
            entry["models"][model_name] = f"failed: {type(exc).__name__}"
    entry["seconds"] = round(time.time() - started, 1)

    best_model = min((v for v in entry["models"].values() if isinstance(v, float)),
                     default=None)
    entry["best_model_ll"] = best_model
    key = f"{market_id}/{target}"
    entry["pipeline_off_best"] = PIPELINE_OFF_BEST.get(key)
    entry["delta_vs_pipeline_off"] = (
        round(best_model - PIPELINE_OFF_BEST[key], 5)
        if best_model is not None and key in PIPELINE_OFF_BEST else None)
    entry["beats_uniform"] = bool(
        best_model is not None and best_model < UNIFORM_LL - 0.002)
    entry["beats_pipeline_off"] = bool(
        best_model is not None and key in PIPELINE_OFF_BEST
        and best_model < PIPELINE_OFF_BEST[key] - 0.002)
    return entry


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="live")
    ap.add_argument("--market", default="kalyan")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    config = load_config(dataset=args.dataset)
    results: dict = {}
    for target in ("open", "close"):
        print(f"evaluating {args.market}/{target} with psychology ON ...", flush=True)
        t0 = time.time()
        entry = evaluate(config, args.market, target)
        results[f"{args.market}/{target}"] = entry
        print(f"  features: {entry['features']}")
        print(f"  best baseline: {entry['best_baseline']} "
              f"({entry['best_baseline_ll']:.5f})")
        print(f"  best model: {entry['best_model_ll']}")
        print(f"  pipeline (channel off) best: {entry['pipeline_off_best']} "
              f"(delta {entry['delta_vs_pipeline_off']})")
        print(f"  beats uniform: {entry['beats_uniform']}")
        print(f"  beats pipeline-off: {entry['beats_pipeline_off']}")
        print(f"  ({time.time() - t0:.0f}s)")
        for name, ll in sorted(entry["models"].items(), key=lambda t: t[1]
                               if isinstance(t[1], float) else 9.9):
            print(f"    {name}: {ll}")

    path = args.out or (REPO / "research" / "psychology_channel_eval.json")
    Path(path).write_text(json.dumps(results, indent=2))
    print(f"written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
