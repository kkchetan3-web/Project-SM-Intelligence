"""Backfill `extraction_runs` / `source_records` for the control datasets.

The control databases were generated before the generator wrote its own provenance
rows. Rather than rebuild them (which would wipe 3000 s of executed analysis), this
script records the generation act into the existing databases. It is idempotent and
trusts nothing: for every market it re-derives the expected row count from
`historical_results`, checks it against the spec, and refuses to write if they
disagree.

Usage: python scripts/record_synthetic_provenance.py [--dataset NAME ...]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.configuration import load_config  # noqa: E402
from src.ingestion.synthetic_control import (  # noqa: E402
    NULL_SPEC,
    SIGNAL_SPEC,
    record_generation_provenance,
)
from src.storage.market_database import MarketDatabase  # noqa: E402

SPECS = {"synthetic_null": NULL_SPEC, "synthetic_signal": SIGNAL_SPEC}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", action="append", choices=sorted(SPECS))
    args = parser.parse_args(argv)
    datasets = args.dataset or sorted(SPECS)

    for name in datasets:
        spec = SPECS[name]
        config = load_config(dataset=name)
        manifest_path = config.database_path(config.market_order[0]).parents[1] / "MANIFEST.json"
        when = None
        if manifest_path.exists():
            when = json.loads(manifest_path.read_text()).get("generated_at")
        print(f"--- {name} (spec {spec.start}..{spec.end}, seed {spec.seed})")
        for market_id in config.market_order:
            db = MarketDatabase(config, market_id)
            with db.session(read_only=True) as conn:
                n_rows = conn.execute(
                    "SELECT COUNT(*) FROM historical_results").fetchone()[0]
                n_distinct = conn.execute(
                    "SELECT COUNT(DISTINCT result_date) FROM historical_results").fetchone()[0]
            if n_rows == 0:
                print(f"    {market_id}: no rows, skipping")
                continue
            if n_rows != n_distinct:
                print(f"    {market_id}: {n_rows} rows but {n_distinct} distinct dates - "
                      "the database is not a clean control; refusing to stamp it")
                continue
            run_id = record_generation_provenance(
                config, market_id, spec, n_rows=n_rows, inserted=n_rows, when=when)
            print(f"    {market_id}: {n_rows} rows, "
                  + (f"recorded run {run_id}" if run_id else "already recorded"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
