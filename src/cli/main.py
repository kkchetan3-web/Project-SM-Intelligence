"""Command-line interface.

Design constraints that shaped this file:

* **One market per command unless the command is inherently comparative.** Every
  command that produces market output takes a single ``--market``; only
  ``cross-market`` and the explicit ``predict-compare`` produce multi-market
  output, and they say so in their own help text.
* **Failures are loud.** Commands propagate errors with a non-zero exit status
  rather than printing a reassuring message over an empty result.
* **Nothing pretends to be live data.** Every command that touches a database
  prints which dataset it operated on.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from src.core.configuration import Config, ConfigurationError, load_config
from src.core.logging import configure_logging, get_logger

log = get_logger("cli")

DATASETS = ("live", "synthetic_null", "synthetic_signal")
DEFAULT_DATASET = "synthetic_null"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _load(args: argparse.Namespace) -> Config:
    config = load_config(dataset=args.dataset)
    if args.verbose:
        configure_logging("DEBUG")
    return config


def _market(config: Config, name: str) -> str:
    return config.market(name).market_id


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, default=str))


def _require_database(config: Config, market_id: str) -> None:
    from src.storage.database_manager import DatabaseManager

    if not DatabaseManager(config).exists(market_id):
        raise SystemExit(
            f"No database for '{market_id}' in dataset '{config.dataset.name}'.\n"
            f"Run: python -m src.cli.main init --dataset {config.dataset.name}")


def _dataset_banner(config: Config) -> None:
    label = {
        "live": "LIVE (real extracted records)",
        "synthetic_null": "SYNTHETIC CONTROL - H0 (i.i.d. uniform; no edge should be found)",
        "synthetic_signal": "SYNTHETIC CONTROL - H1 (planted dependence; edge should be found)",
    }.get(config.dataset.name, config.dataset.name)
    print(f"Dataset: {label}")
    print(f"Root:    {config.dataset.root}")
    print()


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------
def cmd_init(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.storage.database_manager import DatabaseManager

    _dataset_banner(config)
    manager = DatabaseManager(config)
    markets = [config.market(m).market_id for m in args.markets] if args.markets \
        else list(config.market_order)
    paths = {m: manager.initialise(m, rebuild=args.rebuild) for m in markets}
    for market_id, path in paths.items():
        info = manager.integrity_check(market_id)
        print(f"{market_id:14s} {path}")
        print(f"{'':14s} integrity={info['pragma']} "
              f"missing_tables={info['missing_tables'] or 'none'}")
    return 0


def cmd_synthetic(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.ingestion.synthetic_control import (
        NULL_SPEC,
        SIGNAL_SPEC,
        build_dataset,
    )

    spec = {"synthetic_null": NULL_SPEC, "synthetic_signal": SIGNAL_SPEC}.get(config.dataset.name)
    if spec is None:
        raise SystemExit("synthetic generation is only valid for the synthetic_* datasets")
    summary = build_dataset(config, spec, rebuild=args.rebuild)
    _dataset_banner(config)
    for market_id, info in summary["markets"].items():
        print(f"{market_id:14s} generated={info['generated']} inserted={info['inserted']} "
              f"rejected={info['rejected']} {info['oldest']}..{info['newest']}")
    print("\nThese rows are synthetic by construction: verification_status="
          f"'{config.project.get('provenance', {}).get('synthetic_status', 'synthetic_control')}'. "
          "They are a validation fixture, not market history.")
    return 0


def cmd_discover(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.ingestion.website_discovery import investigate_all, summarise

    reports = investigate_all(config)
    summary = summarise(reports)
    _dataset_banner(config)
    for report in reports:
        print(f"{report.source_id:22s} reachable={report.reachable} "
              f"robots_allows={report.robots_allows} verdict={report.verdict}")
        for probe in report.probes:
            if probe.error:
                print(f"{'':22s} {probe.url} -> {probe.error}")
    print()
    _print_json(summary)
    out = config.research_dir("extraction")
    out.mkdir(parents=True, exist_ok=True)
    path = out / "discovery_report.json"
    path.write_text(json.dumps({"summary": summary,
                                "reports": [r.as_dict() for r in reports]},
                               indent=2, default=str))
    print(f"\nWritten: {path}")
    return 0


def cmd_import_snapshots(args: argparse.Namespace) -> int:
    """Load saved chart pages (user-supplied snapshots) into the live databases."""
    config = _load(args)
    from src.ingestion.snapshot_loading import (
        discover_snapshots,
        import_market,
        write_snapshot_manifest,
    )

    if config.dataset.name != "live":
        print(f"refusing: snapshots hold real records, but --dataset is "
              f"'{config.dataset.name}'. Use --dataset live.")
        return 2

    found = discover_snapshots(args.input)
    if not found:
        print(f"no snapshots found in {args.input} "
              f"(expected filenames containing 'jodi'/'panel' and the market name)")
        return 2

    _dataset_banner(config)
    raw_dir = Path(args.raw_dir) if args.raw_dir else Path("data/raw/snapshots")
    audit_dir = config.research_dir("extraction")
    reports = []
    failures = 0
    for market_id, paths in found.items():
        if market_id not in config.market_order:
            print(f"skipping {market_id}: not a configured market")
            continue
        if not {"jodi", "panel"} <= set(paths):
            print(f"skipping {market_id}: need both a jodi and a panel snapshot, got "
                  f"{sorted(paths)}")
            failures += 1
            continue
        print(f"--- importing {market_id}")
        print(f"    panel: {paths['panel'].name}")
        print(f"    jodi : {paths['jodi'].name}")
        result = import_market(config, market_id, jodi_path=paths["jodi"],
                               panel_path=paths["panel"], raw_dir=raw_dir,
                               audit_dir=audit_dir, rebuild=args.rebuild)
        print(f"    dated days={result.rows_built} inserted={result.inserted} "
              f"revised={result.revised} rejected={result.rejected} "
              f"blank days={result.missing_days} jodi-vs-panna conflicts={result.conflicts}")
        if result.errors:
            for error in result.errors[:5]:
                print(f"    rejected: {error}")
        if result.audit_path:
            print(f"    audit: {result.audit_path}")
        reports.append(result.as_dict())

    if reports:
        manifest = write_snapshot_manifest(raw_dir)
        print(f"\nsnapshot manifest: {manifest}")
        out = config.research_dir("extraction") / "snapshot_import.json"
        out.write_text(json.dumps({"dataset": config.dataset.name,
                                   "input": str(args.input), "markets": reports},
                                  indent=2, default=str))
        print(f"import summary: {out}")
    return 1 if failures else 0


def cmd_extract(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.ingestion.historical_archive import extract_market

    markets = [config.market(a).market_id for a in args.markets] if args.markets \
        else list(config.market_order)
    _dataset_banner(config)
    failures = 0
    for market_id in markets:
        print(f"--- extracting {market_id}")
        try:
            result = extract_market(config, market_id)
        except Exception as exc:
            failures += 1
            print(f"    FAILED: {type(exc).__name__}: {exc}")
            continue
        print(f"    status={result.status} pages_ok={result.pages_ok} "
              f"pages_failed={result.pages_failed} records_seen={result.records_seen} "
              f"inserted={result.inserted} revised={result.revised}")
        for failure in result.failures[:5]:
            print(f"    fetch failure: {failure}")
        if result.status != "ok":
            failures += 1
            print(f"    extraction did not complete: {result.error_text or result.status}")
    if failures:
        print(f"\n{failures} market(s) failed. Extraction failure is reported, never hidden.")
        return 1
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.preprocessing.quality_checks import run_quality_checks
    from src.storage.database_manager import DatabaseManager

    markets = [config.market(a).market_id for a in args.markets] if args.markets \
        else list(config.market_order)
    _dataset_banner(config)
    exit_code = 0
    for market_id in markets:
        _require_database(config, market_id)
        report = run_quality_checks(config, market_id)
        info = DatabaseManager(config).integrity_check(market_id)
        print(f"--- {market_id}")
        print(f"    records={report.n_records} ok={report.ok} "
              f"errors={len(report.errors)} warnings={len(report.warnings)}")
        for item in report.errors:
            print(f"    ERROR   {item.check}: {item.detail}")
        for item in report.warnings:
            print(f"    WARNING {item.check}: {item.detail}")
        print(f"    integrity={info['pragma']} missing_tables={info['missing_tables'] or 'none'}")
        if not report.ok:
            exit_code = 1
    return exit_code


def cmd_analyse(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.mathematics.engine import run_suite

    markets = [config.market(a).market_id for a in args.markets] if args.markets \
        else list(config.market_order)
    targets = args.targets or ["open", "close"]
    _dataset_banner(config)
    for market_id in markets:
        _require_database(config, market_id)
        for target in targets:
            print(f"--- {market_id} / {target}")
            result = run_suite(config, market_id, target, persist=not args.no_persist,
                               verbose=args.verbose)
            counts = result.status_counts()
            print(f"    methods={len(result.outputs)} "
                  f"computed={counts.get('computed', 0)} "
                  f"not_applicable={counts.get('not_applicable', 0)} "
                  f"insufficient={counts.get('insufficient_data', 0)} "
                  f"failed={counts.get('failed', 0)}")
            if counts.get("failed"):
                for failure in result.failures:
                    print(f"    FAILED {failure}")
    return 0


def cmd_cross_market(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.cross_market.cross_market_validation import run_all

    if args.markets and len(args.markets) != 2:
        raise SystemExit("--market takes exactly two market ids for cross-market analysis")
    _dataset_banner(config)
    if args.markets:
        pair = (config.market(args.markets[0]).market_id, config.market(args.markets[1]).market_id)
        original = config.cross_market_pairs
        object.__setattr__(config, "cross_market_pairs", (pair,))
        try:
            summary = run_all(config, persist=not args.no_persist)
        finally:
            object.__setattr__(config, "cross_market_pairs", original)
    else:
        summary = run_all(config, persist=not args.no_persist)

    print(f"Leakage validation: {'PASS' if summary['leakage_validation']['ok'] else 'FAIL'}")
    for pair in summary["pairs"]:
        lead = pair["lead_lag"]
        print(f"\n--- {pair['pair'][0]} vs {pair['pair'][1]}")
        print(f"    lag tests={lead['n_tests']} significant after Holm={lead['n_significant_holm']}")
        for test in pair["conditional_model_tests"]:
            if not test.get("available"):
                print(f"    {test.get('target_market')}/{test.get('target')}: "
                      f"unavailable ({test.get('reason')})")
                continue
            print(f"    {test['target_market']}/{test['target']}: "
                  f"domestic={test['domestic_only_log_loss']:.5f} "
                  f"+foreign={test['domestic_plus_foreign_log_loss']:.5f} "
                  f"improvement={test['improvement']:+.5f} "
                  f"CI=[{test['ci_low']:+.5f}, {test['ci_high']:+.5f}] "
                  f"-> {test['verdict']}")
    print("\nHeadline:")
    _print_json(summary["headline"])
    out = config.research_dir("cross_market")
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"cross_market_{config.dataset.name}.json"
    path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWritten: {path}")
    return 0


def cmd_backtest(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.backtesting.validation import decide
    from src.mathematics.engine import build_context
    from src.mathematics.model_panel import get_panel
    from src.storage.market_database import MarketDatabase

    market_id = _market(config, args.market)
    _require_database(config, market_id)
    _dataset_banner(config)
    targets = args.targets or ["open", "close"]
    output: dict[str, Any] = {"market": market_id, "dataset": config.dataset.name, "targets": {}}

    for target in targets:
        ctx = build_context(config, market_id, target)
        panel = get_panel(ctx)
        print(f"--- {market_id} / {target}")
        table = panel.table()
        print(table.to_string(index=False, float_format=lambda v: f"{v:.5f}"))
        best_base = panel.best_baseline_name()
        verdicts = {}
        for name in panel.models:
            verdict = decide(panel.get(name), panel.baselines, min_improvement=0.002)
            verdicts[name] = verdict.as_dict()
            stored = MarketDatabase(config, market_id)
            model_id = stored.register_model(
                target=target, model_name=name,
                model_version=f"{name}-{panel.frame.feature_version}-{config.fingerprint()[:8]}",
                config={"refit_every": None, "features": panel.feature_count},
                feature_version=panel.frame.feature_version,
                trained_from=str(panel.dates[0].date()), trained_to=str(panel.dates[-1].date()),
                train_size=int(panel.min_train),
                metrics=panel.get(name).metrics().as_dict(),
                is_selected=bool(verdict.promoted),
            )
            stored.save_backtest(
                model_id=model_id, target=target, scheme="expanding_walk_forward",
                test_start=str(panel.dates[panel.min_train].date()),
                test_end=str(panel.dates[-1].date()),
                n_predictions=int(len(panel.get(name).y_true)),
                metrics=panel.get(name).metrics().as_dict(),
                calibration=panel.diagnostics_for(name)["calibration"],
                baselines={b: panel.baselines[b].metrics().as_dict() for b in panel.baselines},
            )
        promoted = [n for n, v in verdicts.items() if v["promoted"]]
        print(f"    best baseline: {best_base} "
              f"(log loss {panel.baselines[best_base].per_obs_log_loss().mean():.5f})")
        print(f"    promoted models: {promoted or 'none - no model beat the best baseline'}")
        output["targets"][target] = {
            "table": table.to_dict(orient="records"),
            "best_baseline": best_base,
            "promoted": promoted,
            "verdicts": verdicts,
        }

    path = config.research_dir("backtests") / f"backtest_{market_id}_{config.dataset.name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, default=str))
    print(f"\nWritten: {path}")
    return 0


def cmd_predict(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.predictions import reporting
    from src.predictions.prediction_engine import generate

    market_id = _market(config, args.market)
    _require_database(config, market_id)
    if args.compare:
        # Explicit multi-market request only.
        market_ids = [market_id] + [config.market(m).market_id for m in args.compare]
        forecasts = [generate(config, m, args.target, next_open=args.open_ank,
                              next_foreign_open=args.foreign_open_ank,
                              persist=not args.no_persist)
                     for m in market_ids]
        print(reporting.render_comparison(forecasts))
        return 0

    forecast = generate(config, market_id, args.target, next_open=args.open_ank,
                        next_foreign_open=args.foreign_open_ank,
                        persist=not args.no_persist)
    print(reporting.render_forecast(forecast))
    if not args.no_persist:
        print(f"\nStored in {config.database_path(market_id)}")
    return 0


def cmd_ledger(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.predictions import reporting
    from src.predictions.prediction_ledger import resolve, summary

    market_id = _market(config, args.market)
    _require_database(config, market_id)
    resolved = resolve(config, market_id, args.target)
    print(f"Resolved {resolved.get('resolved', 0)} outcome(s); "
          f"{resolved.get('pending_without_result', 0)} forecast(s) still pending "
          f"a published result.\n")
    print(reporting.render_ledger(summary(config, market_id, args.target)))
    return 0


def cmd_update_all(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.ingestion.incremental_updates import update_market
    from src.mathematics.engine import run_suite
    from src.predictions.prediction_engine import generate
    from src.preprocessing.quality_checks import run_quality_checks

    markets = [config.market(a).market_id for a in args.markets] if args.markets \
        else list(config.market_order)
    _dataset_banner(config)
    report: dict[str, Any] = {"dataset": config.dataset.name, "markets": {}}
    for market_id in markets:
        _require_database(config, market_id)
        entry: dict[str, Any] = {}
        try:
            update = update_market(config, market_id)
            entry["update"] = {"status": update.status, "new_records": update.new_records,
                               "pages_ok": update.pages_ok,
                               "pages_failed": update.pages_failed,
                               "detail": update.error_text or update.status}
        except Exception as exc:
            entry["update"] = {"status": "failed", "detail": f"{type(exc).__name__}: {exc}"}
        quality = run_quality_checks(config, market_id)
        entry["quality"] = {"ok": quality.ok, "n_records": quality.n_records,
                            "errors": [i.check for i in quality.errors]}
        methods = {}
        for target in ("open", "close"):
            result = run_suite(config, market_id, target, persist=True)
            methods[target] = {"n": len(result.outputs), "status": result.status_counts()}
        entry["methods"] = methods
        forecasts = {}
        for target in ("open", "close"):
            try:
                forecast = generate(config, market_id, target)
                forecasts[target] = {"target_date": forecast.target_date,
                                     "mode": forecast.mode,
                                     "model": forecast.model_name,
                                     "top": forecast.ranked[:3]}
            except Exception as exc:
                forecasts[target] = {"error": f"{type(exc).__name__}: {exc}"}
        entry["forecasts"] = forecasts
        report["markets"][market_id] = entry
        print(f"{market_id}: update={entry['update']['status']} "
              f"quality_ok={quality.ok} forecasts="
              f"{ {t: v.get('mode', v.get('error')) for t, v in forecasts.items()} }")

    path = config.research_dir("runs") / f"update_all_{config.dataset.name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, default=str))
    print(f"\nWritten: {path}")
    return 0


def cmd_methods(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.mathematics.dossier import write_all
    from src.mathematics.registry import METHOD_REGISTRY, methods_for_category

    specs = methods_for_category(args.category) if args.category \
        else list(METHOD_REGISTRY.values())
    print(f"{len(specs)} methods selected"
          + (f" in category {args.category}" if args.category else ""))
    for spec in specs:
        print(f"  {spec.id}  {spec.category}  {spec.name[:70]:72s} {spec.spec.implementation}")
    if args.write:
        from src.mathematics.dossier import payloads_from_database

        market_id = _market(config, args.market)
        payloads = payloads_from_database(config, market_id)
        # One directory per dataset: the dossiers carry computed numbers, and the
        # null world's numbers must never overwrite the signal world's.
        written = write_all(
            specs, payloads, config.research_dir("methods") / config.dataset.name,
            dataset_note=(f"`{config.dataset.name}` - {config.dataset.description} "
                          f"Market: {market_id}. Synthetic control data; not real market history."))
        print(f"\nWrote {len(written)} dossier(s) under "
              f"{config.research_dir('methods') / config.dataset.name}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.reporting.report import build_report

    path = build_report(config, markets=args.markets, write=not args.no_write)
    if path:
        print(f"Written: {path}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    config = _load(args)
    from src.storage.database_manager import DatabaseManager

    _dataset_banner(config)
    manager = DatabaseManager(config)
    rows = []
    for market_id in config.market_order:
        exists = manager.exists(market_id)
        row: dict[str, Any] = {"market": market_id, "database": str(manager.path_for(market_id)),
                              "exists": exists}
        if exists:
            info = manager.integrity_check(market_id)
            row["ok"] = info["ok"]
            row["row_counts"] = info["row_counts"]
        rows.append(row)
    _print_json(rows)
    return 0


# ---------------------------------------------------------------------------
# parser
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sm-intel",
        description="Satta Matka quantitative research platform (market-isolated, "
                    "leakage-audited, honestly reported).",
    )
    parser.add_argument("--dataset", default=DEFAULT_DATASET, choices=DATASETS,
                        help="which database tree to operate on (default: %(default)s)")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="create or migrate each market's database")
    p.add_argument("--market", dest="markets", nargs="+")
    p.add_argument("--rebuild", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("synthetic", help="regenerate the synthetic control datasets")
    p.add_argument("--rebuild", action="store_true")
    p.set_defaults(func=cmd_synthetic)

    p = sub.add_parser("discover", help="probe the configured sources for structure")
    p.set_defaults(func=cmd_discover)

    p = sub.add_parser("import-snapshots",
                       help="load saved chart pages (MHTML/HTML) into the live databases")
    p.add_argument("--input", required=True,
                   help="directory holding the saved jodi and panel pages")
    p.add_argument("--raw-dir", default=None,
                   help="where to archive the raw snapshots (default data/raw/snapshots)")
    p.add_argument("--rebuild", action="store_true",
                   help="recreate the market database before importing")
    p.set_defaults(func=cmd_import_snapshots)

    p = sub.add_parser("extract", help="extract historical records for one or more markets")
    p.add_argument("--market", dest="markets", nargs="+")
    p.set_defaults(func=cmd_extract)

    sub.add_parser("extract-all", help="extract every configured market").set_defaults(
        func=cmd_extract, markets=None)

    p = sub.add_parser("validate", help="run data-quality checks")
    p.add_argument("--market", dest="markets", nargs="+")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("analyse", help="run the full method suite")
    p.add_argument("--market", dest="markets", nargs="+")
    p.add_argument("--target", dest="targets", nargs="+", choices=["open", "close"])
    p.add_argument("--no-persist", action="store_true")
    p.set_defaults(func=cmd_analyse)

    p = sub.add_parser("cross-market", help="cross-market dependency analysis (multi-market by nature)")
    p.add_argument("--market", dest="markets", nargs="+")
    p.add_argument("--no-persist", action="store_true")
    p.set_defaults(func=cmd_cross_market)

    p = sub.add_parser("backtest", help="walk-forward backtest with baselines")
    p.add_argument("--market", required=True)
    p.add_argument("--target", dest="targets", nargs="+", choices=["open", "close"])
    p.set_defaults(func=cmd_backtest)

    p = sub.add_parser("predict", help="forecast one market's next draw")
    p.add_argument("--market", required=True)
    p.add_argument("--target", required=True, choices=["open", "close"])
    p.add_argument("--open-ank", type=int, default=None,
                   help="same-day Open, once published (close forecasts only)")
    p.add_argument("--foreign-open-ank", type=int, default=None,
                   help="paired market's same-day Open, once published")
    p.add_argument("--compare", nargs="+", default=None,
                   help="explicitly request a multi-market comparison")
    p.add_argument("--no-persist", action="store_true")
    p.set_defaults(func=cmd_predict)

    p = sub.add_parser("ledger", help="score stored forecasts against published results")
    p.add_argument("--market", required=True)
    p.add_argument("--target", choices=["open", "close"])
    p.set_defaults(func=cmd_ledger)

    p = sub.add_parser("update-all", help="update, validate, analyse and forecast every market")
    p.add_argument("--market", dest="markets", nargs="+")
    p.set_defaults(func=cmd_update_all)

    p = sub.add_parser("methods", help="list the method catalogue / write dossiers")
    p.add_argument("--category", choices=list("ABCDEFGH"))
    p.add_argument("--market", default="kalyan",
                   help="market whose persisted results populate the dossiers")
    p.add_argument("--write", action="store_true")
    p.set_defaults(func=cmd_methods)

    p = sub.add_parser("report", help="build the final report")
    p.add_argument("--market", dest="markets", nargs="+")
    p.add_argument("--no-write", action="store_true")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("status", help="show database state")
    p.set_defaults(func=cmd_status)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging("DEBUG" if args.verbose else "INFO")
    try:
        return int(args.func(args) or 0)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except (ConfigurationError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
