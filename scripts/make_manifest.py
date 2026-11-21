#!/usr/bin/env python
"""Write SHA-256 digests of the data snapshot.

Databases are git-ignored, so the manifest is the only committed record of *which*
data produced a report. It is written to `data/<dataset>/MANIFEST.json` and lists
every database file with its size, mtime and digest, plus the configuration
fingerprint.

Usage
-----
    python scripts/make_manifest.py --dataset synthetic_null
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.configuration import load_config  # noqa: E402
from src.core.provenance import utcnow  # noqa: E402


def digest(path: Path, chunk: int = 1 << 20) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            sha.update(block)
    return sha.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="synthetic_null",
                        choices=["live", "synthetic_null", "synthetic_signal"])
    args = parser.parse_args(argv)

    config = load_config(dataset=args.dataset)
    entries = []
    for market_id in config.market_order:
        path = config.database_path(market_id)
        if not path.exists():
            entries.append({"market": market_id, "path": str(path.relative_to(ROOT)),
                            "present": False})
            continue
        stat = path.stat()
        entries.append({
            "market": market_id, "path": str(path.relative_to(ROOT)), "present": True,
            "bytes": stat.st_size,
            "modified": utcnow(),
            "sha256": digest(path),
        })

    manifest = {
        "dataset": config.dataset.name,
        "description": config.dataset.description,
        "generated_at": utcnow(),
        "config_fingerprint": config.fingerprint(),
        "databases": entries,
        "note": ("All rows in a synthetic dataset were produced by "
                 "src/ingestion/synthetic_control.py and are not market history."
                 if config.dataset.name.startswith("synthetic") else
                 "Live dataset: populated only by the ingestion pipeline."),
    }
    out = config.dataset.root / "MANIFEST.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for entry in entries:
        state = entry.get("sha256", "MISSING")[:16]
        print(f"{entry['market']:14s} {state}  {entry['path']}")
    print(f"\nWritten: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
