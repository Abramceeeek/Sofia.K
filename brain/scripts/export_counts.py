"""m288 (Abram, 19 Nov): the final export must be "completed and independently checked before migration". Read-only.

    python scripts/export_counts.py ../validation/raw/export-<date>.json

It prints the number of rows in each table of an admin export, one per line ("users 21"), to compare with a sealed
backup taken by a different route (`python -m brain.backup counts <file> --key <key>`, or the fuller `preflight`).
It also checks that every row that names a person names one who exists, and that every rating's plan exists (Abram,
20 Nov, condition 5). It prints counts and problems only, never a value from a row. Exit code 1 if anything doesn't
hold together.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PERSON_TABLES = ("swipes", "conjoint_choices", "answers", "plans", "ratings", "events", "safety_alerts",
                 "category_answers", "corrections", "day_feedback")


def counts(export: dict) -> dict[str, int]:
    return {k: len(v) for k, v in sorted(export.items()) if isinstance(v, list)}


def problems(export: dict) -> list[str]:
    out = []
    users = {u.get("id") for u in export.get("users", [])}
    for table in PERSON_TABLES:
        orphans = sum(1 for row in export.get(table, []) if row.get("user_id") not in users)
        if orphans:
            out.append(f"{table}: {orphans} rows name a person who isn't in users")
    plans = {p.get("id") for p in export.get("plans", [])}
    lost = sum(1 for r in export.get("ratings", []) if r.get("plan_id") is not None and r["plan_id"] not in plans)
    if lost:
        out.append(f"ratings: {lost} rows name a plan that isn't in plans")
    if not export.get("users"):
        out.append("users: none (an empty export, or the wrong file)")
    return out


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    export = json.loads(Path(args[0]).read_text(encoding="utf-8-sig"))   # PowerShell writes a BOM
    for name, n in counts(export).items():
        print(f"{name} {n}")
    found = problems(export)
    for p in found:
        print("PROBLEM: " + p, file=sys.stderr)
    print("Holds together." if not found else "Don't rely on this export: take it again.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
