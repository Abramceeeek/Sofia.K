"""m288 (Abram, 19 Nov): the final export must be "completed and independently checked before migration". This prints
the number of rows in each table of an admin export, and nothing else, to compare with a sealed backup taken by a
different route (`python -m brain.backup counts <file> --key <key>`). Read-only; no row is printed.

    python scripts/export_counts.py ../validation/raw/export-<date>.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def counts(export: dict) -> dict[str, int]:
    return {k: len(v) for k, v in sorted(export.items()) if isinstance(v, list)}


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 1
    for name, n in counts(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))).items():
        print(f"{name} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
