"""m204: travel timing (Abram, 7 Nov): how the choice of dates changes a trip. Three parts, kept apart:

- **your calendar:** the person's home country's school and public holidays, and when they're free;
- **the destination's calendar:** its holidays, festivals, major events and seasons;
- **travel costs:** stays and flights on their dates and the dates around them (stayprices.py).

**Bank holidays and school holidays are separate kinds of data** (Abram): a bank holiday doesn't say when schools are
closed. Bank holidays come from GOV.UK's official file (data/calendar/bank_holidays.json, with its source and the day
it was fetched; refreshed by scripts/update_bank_holidays.py). School holidays come later, area by area, from each
council (GOV.UK gives none itself: gov.uk/school-term-holiday-dates, read 7 Nov 2026).

Facts only: a date is marked as a bank holiday, never as "busier" or "dearer".
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path

from .config import DATA_DIR
from .places import load_destinations

# The bank holidays that apply where a destination is (a destination's own calendar, not the traveller's), from the
# destination registry (WS1, data/destinations.yaml), so no second list of destinations lives here
DESTINATION_DIVISION = {k: d.bank_holidays for k, d in load_destinations(DATA_DIR / "destinations.yaml").items()
                        if d.bank_holidays}


@dataclass(frozen=True)
class BankHoliday:
    day: date
    title: str
    division: str
    substitute: bool = False

    def out(self) -> dict:
        return {"kind": "bank_holiday", "date": self.day.isoformat(), "title": self.title,
                "division": self.division, "substitute": self.substitute}


@lru_cache(maxsize=4)
def load_bank_holidays(path: Path = DATA_DIR / "calendar" / "bank_holidays.json") -> tuple[dict, tuple[BankHoliday, ...]]:
    """(the file's source and fetch date, every bank holiday in it)."""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    days = tuple(BankHoliday(date.fromisoformat(e["date"]), e["title"], k, bool(e.get("substitute")))
                 for k, v in d["divisions"].items() for e in v["events"])
    meta = {"kind": d["kind"], "source": d["source"], "source_page": d["source_page"], "fetched": d["fetched"],
            "names": {k: v["name"] for k, v in d["divisions"].items()}}
    return meta, days


def bank_holidays(division: str, start: date, end: date) -> list[BankHoliday]:
    """The division's bank holidays from `start` to `end`, both included."""
    _, days = load_bank_holidays()
    return sorted((h for h in days if h.division == division and start <= h.day <= end), key=lambda h: h.day)


def covered(division: str | None) -> tuple[date, date] | None:
    """The first and last date the file covers for a division: outside it, nothing can be said."""
    if not division:
        return None
    _, days = load_bank_holidays()
    mine = [h.day for h in days if h.division == division]
    return (min(mine), max(mine)) if mine else None


def stay_holidays(destination: str, checkin: date, checkout: date) -> list[str]:
    """The destination's bank holidays from the check-in day to the check-out day, as short lines for a stay's dates:
    "Mon 28 Dec: Boxing Day (substitute day)". Empty when there are none, or the destination's calendar isn't known."""
    division = DESTINATION_DIVISION.get(destination)
    if not division:
        return []
    return [f"{h.day:%a} {h.day.day} {h.day:%b}: {h.title}" + (" (substitute day)" if h.substitute else "")
            for h in bank_holidays(division, checkin, checkout)]

