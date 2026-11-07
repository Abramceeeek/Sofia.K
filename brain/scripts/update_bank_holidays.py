"""m204: refresh data/calendar/bank_holidays.json from GOV.UK's official file (https://www.gov.uk/bank-holidays.json).

    python scripts/update_bank_holidays.py            # from brain/

It keeps the source, the publisher and the day it was fetched in the file, and prints what changed. GOV.UK covers
about two years ahead (on 7 Nov 2026: 2019 to 2028); run it once a year, or when the ODYS calendar nears its end.
"""

from __future__ import annotations

import json
import urllib.request
from datetime import date
from pathlib import Path

SOURCE = "https://www.gov.uk/bank-holidays.json"
OUT = Path(__file__).resolve().parents[1] / "data" / "calendar" / "bank_holidays.json"
NAMES = {"england-and-wales": "England and Wales", "scotland": "Scotland", "northern-ireland": "Northern Ireland"}


def build(d: dict, fetched: date) -> dict:
    return {"kind": "bank_holidays", "source": SOURCE, "source_page": "https://www.gov.uk/bank-holidays",
            "publisher": "GOV.UK (UK government)", "fetched": fetched.isoformat(),
            "note": "Bank holidays only: they don't say when schools are closed. School holidays are a separate kind of data.",
            "divisions": {k: {"name": NAMES.get(k, k),
                              "events": [{"date": e["date"], "title": e["title"], "substitute": e["notes"] == "Substitute day"}
                                         for e in v["events"]]} for k, v in d.items()}}


def main() -> None:
    with urllib.request.urlopen(SOURCE, timeout=30) as r:
        fresh = build(json.load(r), date.today())
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"divisions": {}}
    for k, v in fresh["divisions"].items():
        before = {e["date"] for e in old["divisions"].get(k, {}).get("events", [])}
        now = {e["date"] for e in v["events"]}
        print(f"{k}: {len(now)} dates ({len(now - before)} new, {len(before - now)} gone)")
    OUT.write_text(json.dumps(fresh, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
