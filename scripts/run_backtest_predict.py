#!/usr/bin/env python
"""Run backtest + predict + cross-market + ledger + report for live markets.

Skips init, synthetic, snapshots, validate, and analyse stages (already done).
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _stage(name: str, fn, results: dict) -> None:
    started = time.time()
    print(f"\n=== {name} " + "=" * max(0, 60 - len(name)), flush=True)
    try:
        payload = fn()
        elapsed = round(time.time() - started, 1)
        results[name] = {"status": "ok", "seconds": elapsed, "payload": payload}
        print(f"--- {name}: OK in {elapsed}s", flush=True)
    except Exception as exc:
        elapsed = round(time.time() - started, 1)
        results[name] = {"status": "failed", "seconds": elapsed,
                         "error": f"{type(exc).__name__}: {exc}",
                         "traceback": traceback.format_exc()[-2000:]}
        print(f"--- {name}: FAILED after {elapsed}s: {type(exc).__name__}: {exc}", flush=True)


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--markets", nargs="+", default=None)
    parser.add_argument("--skip-cross-market", action="store_true")
    args = parser.parse_args(argv)

    from src.core.configuration import load_config
    from src.core.logging import configure_logging

    configure_logging("INFO")
    config = load_config(dataset="live")
    markets = ([config.market(m).market_id for m in args.markets]
               if args.markets else list(config.market_order))
    results: dict = {"dataset": "live", "markets": markets,
                     "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    pipeline_started = time.time()

    # -- 1. backtests ------------------------------------------------------
    def backtest():
        from src.backtesting.validation import decide
        from src.mathematics.engine import build_context
        from src.mathematics.model_panel import get_panel
        from src.storage.market_database import MarketDatabase

        out = {}
        for market_id in markets:
            for target in ("open", "close"):
                panel = get_panel(build_context(config, market_id, target))
                best_base = panel.best_baseline_name()
                verdicts = {}
                db = MarketDatabase(config, market_id)
                for name in panel.models:
                    verdict = decide(panel.get(name), panel.baselines, min_improvement=0.002)
                    verdicts[name] = verdict.as_dict()
                    model_id = db.register_model(
                        target=target, model_name=name,
                        model_version=(f"{name}-{panel.frame.feature_version}-"
                                       f"{config.fingerprint()[:8]}"),
                        config={"features": panel.feature_count},
                        feature_version=panel.frame.feature_version,
                        trained_from=str(panel.dates[0].date()),
                        trained_to=str(panel.dates[-1].date()),
                        train_size=int(panel.min_train),
                        metrics=panel.get(name).metrics().as_dict(),
                        is_selected=bool(verdict.promoted),
                    )
                    diagnostics = panel.diagnostics_for(name)
                    db.save_backtest(
                        model_id=model_id, target=target, scheme="expanding_walk_forward",
                        test_start=str(panel.dates[panel.min_train].date()),
                        test_end=str(panel.dates[-1].date()),
                        n_predictions=int(len(panel.get(name).y_true)),
                        metrics=panel.get(name).metrics().as_dict(),
                        calibration=diagnostics["calibration"],
                        baselines={b: panel.baselines[b].metrics().as_dict()
                                   for b in panel.baselines},
                    )
                out[f"{market_id}/{target}"] = {
                    "best_baseline": best_base,
                    "baseline_log_loss": float(
                        panel.baselines[best_base].per_obs_log_loss().mean()),
                    "models": {n: {"log_loss": float(r.per_obs_log_loss().mean()),
                                   "promoted": verdicts[n]["promoted"],
                                   "reasons": verdicts[n]["reasons"]}
                               for n, r in panel.models.items()},
                }
                promoted = [n for n, v in verdicts.items() if v["promoted"]]
                print(f"    {market_id}/{target}: best baseline {best_base}, "
                      f"promoted={promoted or 'none'}", flush=True)
        return out

    _stage("backtest", backtest, results)

    # -- 2. cross-market --------------------------------------------------
    if not args.skip_cross_market and len(markets) > 1:
        def cross_market():
            from src.cross_market.cross_market_validation import run_all

            summary = run_all(config, persist=True)
            out_dir = config.research_dir("cross_market")
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / f"cross_market_{config.dataset.name}.json").write_text(
                json.dumps(summary, indent=2, default=str))
            return {"leakage_ok": summary["leakage_validation"]["ok"],
                    "headline": summary["headline"]}

        _stage("cross_market", cross_market, results)

    # -- 3. predictions ---------------------------------------------------
    def predict():
        from src.predictions.prediction_engine import generate

        out = {}
        for market_id in markets:
            for target in ("open", "close"):
                try:
                    forecast = generate(config, market_id, target, persist=True)
                    out[f"{market_id}/{target}"] = {
                        "target_date": forecast.target_date,
                        "mode": forecast.mode,
                        "model": forecast.model_name,
                        "top3": forecast.top(3),
                        "notes": forecast.notes,
                    }
                    print(f"    {market_id}/{target}: {forecast.target_date} "
                          f"{forecast.model_name} ({forecast.mode}) "
                          f"top={forecast.top(1)}", flush=True)
                except Exception as exc:
                    out[f"{market_id}/{target}"] = {"error": f"{type(exc).__name__}: {exc}"}
                    print(f"    {market_id}/{target}: FAILED {exc}", flush=True)
        return out

    _stage("predict", predict, results)

    # -- 4. ledger --------------------------------------------------------
    def ledger():
        from src.predictions.prediction_ledger import resolve, summary

        out = {}
        for market_id in markets:
            resolve(config, market_id)
            out[market_id] = summary(config, market_id)
        return out

    _stage("ledger", ledger, results)

    # -- 5. report --------------------------------------------------------
    def report():
        from src.reporting.report import build_report

        path = build_report(config, markets=markets)
        return {"path": str(path)}

    _stage("report", report, results)

    results["elapsed_seconds"] = round(time.time() - pipeline_started, 1)
    results["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    out_path = config.research_dir("runs") / f"backtest_predict_{config.dataset.name}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, default=str))

    print("\n=== summary " + "=" * 50)
    for name, payload in results.items():
        if isinstance(payload, dict) and "status" in payload:
            print(f"{name:16s} {payload['status']:8s} {payload.get('seconds', '')}s")
    print(f"\nTotal: {results['elapsed_seconds']}s")
    print(f"Run record: {out_path}")

    failed = [n for n, p in results.items()
              if isinstance(p, dict) and p.get("status") == "failed"]
    if failed:
        print(f"\nFAILED STAGES: {failed}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
