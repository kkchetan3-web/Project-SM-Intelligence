#!/usr/bin/env python
"""Export the 100-method catalogue as markdown (no database required)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.mathematics.registry import (  # noqa: E402
    CATEGORY_NAMES,
    all_methods,
    methods_for_category,
    validate_registry,
)


def main() -> int:
    report = validate_registry()
    if not report["ok"]:
        print(f"registry invalid: {report['problems']}", file=sys.stderr)
        return 1

    lines = [
        "# Complete method catalogue",
        "",
        f"{report['n_documented']} methods documented, {report['n_implemented']} implemented, "
        "0 missing. Generated from `src/mathematics/registry.py` by "
        "`scripts/export_catalogue.py` - do not edit by hand.",
        "",
        "Status vocabulary used by every method: `computed`, `not_applicable`, "
        "`insufficient_data`, `dependency_unavailable`, `failed`. A method that cannot run says "
        "so; it never returns a placeholder number.",
        "",
    ]

    for letter, name in CATEGORY_NAMES.items():
        methods = methods_for_category(letter)
        lines += [f"## Category {letter} - {name} ({len(methods)} methods)", ""]
        lines.append("| ID | Method | Implementation | Formula |")
        lines.append("|---|---|---|---|")
        for m in methods:
            formula = m.spec.formula.replace("|", "\\|")
            if len(formula) > 160:
                formula = formula[:157] + "..."
            lines.append(f"| `{m.id}` | {m.name} | `{m.spec.implementation}` | `{formula}` |")
        lines.append("")

    out = ROOT / "docs" / "METHOD_CATALOGUE.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Written: {out} ({len(all_methods())} methods)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
