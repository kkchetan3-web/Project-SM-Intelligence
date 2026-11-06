"""CLI surface tests.

These check the *contract* of the interface - which commands exist, that market
isolation is expressed in the arguments, and that bad input fails loudly - without
running the expensive stages.
"""

from __future__ import annotations

import pytest

from src.cli.main import build_parser, main

EXPECTED_COMMANDS = {
    "init", "synthetic", "discover", "extract", "extract-all", "validate", "analyse",
    "cross-market", "backtest", "predict", "ledger", "update-all", "methods", "report",
    "status",
}


def test_every_documented_command_exists():
    parser = build_parser()
    subparsers = [a for a in parser._actions if a.__class__.__name__ == "_SubParsersAction"]
    assert subparsers, "the parser exposes no subcommands"
    available = set(subparsers[0].choices)
    assert EXPECTED_COMMANDS.issubset(available), EXPECTED_COMMANDS - available


def test_single_market_commands_take_one_market():
    parser = build_parser()
    for command in ("backtest", "predict", "ledger"):
        with pytest.raises(SystemExit):
            parser.parse_args([command])  # --market is required
    args = parser.parse_args(["predict", "--market", "kalyan", "--target", "open"])
    assert args.market == "kalyan"
    assert args.target == "open"


def test_predict_rejects_an_unknown_target():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["predict", "--market", "kalyan", "--target", "jodi"])


def test_dataset_choice_is_validated():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--dataset", "not_a_dataset", "status"])


def test_unknown_market_exits_with_a_message(capsys):
    code = main(["--dataset", "synthetic_null", "predict", "--market", "atlantis",
                 "--target", "open"])
    assert code == 2
    captured = capsys.readouterr()
    assert "unknown market" in (captured.err + captured.out)


def test_status_runs_against_a_real_database(small_config, monkeypatch, capsys):
    monkeypatch.setenv("SM_INTEL_DATABASE_ROOT", str(small_config.dataset.root))
    code = main(["--dataset", "synthetic_null", "status"])
    assert code == 0
    output = capsys.readouterr().out
    assert "kalyan" in output and "main_bazar" in output
