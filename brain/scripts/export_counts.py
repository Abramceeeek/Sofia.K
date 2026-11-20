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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from brain.exportcheck import counts, problems  # noqa: E402


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
