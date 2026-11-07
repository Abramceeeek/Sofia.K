"""WS5 (m211): the travel calendar: dates that change a trip, as facts with their source
(decisions/travel-calendar-intelligence.md).

Two calendars, never mixed (Abram, 7 Nov):
- **Your calendar** (home): your nation's bank holidays and, where a checked source exists, your council's school
  holidays. A family from England meets more demand in English school holidays wherever they go.
- **The destination's calendar:** its own holidays (and later its festivals, major events and seasons).

Every entry carries its country, its region or council, its dates, its source, when it was last checked, who it
applies to and its exceptions. **Bank holidays and school holidays are different kinds of data**: a bank holiday
doesn't say when schools are closed, and a council's school holidays never apply to every school (academies,
free schools and voluntary-aided schools can set their own). Nothing says "busier" or "dearer": only what's on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Literal

import yaml

from .config import DATA_DIR
from .places import Destination
from .traveltiming import bank_holidays, covered, load_bank_holidays

Kind = Literal["bank_holiday", "public_holiday", "school_holiday", "major_event", "festival", "seasonal"]
KINDS = ("bank_holiday", "public_holiday", "school_holiday", "major_event", "festival", "seasonal")


@dataclass(frozen=True)
class Entry:
    kind: Kind
    title: str
    start: date
    end: date                       # inclusive
    country: str                    # ISO 3166-1
    region: str | None              # a nation or region ("england-and-wales"), if it applies to one
    authority: str | None           # a council, for school holidays
    source: str                     # where it came from (a URL)
    last_verified: str              # ISO date the source was read
    applies_to: str                 # who it's true for, in words
    exceptions: str = ""            # who it isn't true for

    def line(self) -> str:
        span = (f"{self.start:%a} {self.start.day} {self.start:%b}" if self.start == self.end else
                f"{self.start:%a} {self.start.day} {self.start:%b} – {self.end:%a} {self.end.day} {self.end:%b}")
        return f"{span}: {self.title}"


@dataclass
class View:
    side: Literal["home", "destination"]
    entries: list[Entry] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)   # what can't be said, in words: never read as "nothing on"


@dataclass(frozen=True)
class SchoolArea:
    authority: str                  # the council
    country: str
    region: str                     # the bank-holiday division the council is in
    source: str
    last_verified: str
    years: tuple[str, ...]          # school years covered, "2026-27"
    exceptions: str
    holidays: tuple[tuple[str, date, date], ...]


def load_school_areas(path: Path = DATA_DIR / "calendar" / "school_holidays.yaml") -> dict[str, SchoolArea]:
    if not path.exists():
        return {}
    d = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out = {}
    for key, a in (d.get("areas") or {}).items():
        hols = tuple((h["title"], h["from"], h["to"]) for h in a.get("holidays") or [])
        for title, f, t in hols:
            if t < f:
                raise ValueError(f"{key}: {title} ends before it starts")
        out[key] = SchoolArea(a["authority"], a["country"], a["region"], a["source"], str(a["last_verified"]),
                              tuple(a.get("years") or ()), a.get("exceptions", ""), hols)
    return out


def _bank(division: str, start: date, end: date, view: View) -> None:
    meta, _ = load_bank_holidays()
    span = covered(division)
    if span is None:
        view.unknown.append("Bank holidays here aren't known.")
        return
    if start < span[0] or end > span[1]:
        view.unknown.append(f"Bank holidays are known from {span[0]:%-d %b %Y} to {span[1]:%-d %b %Y} only.")
    name = meta["names"].get(division, division)
    for h in bank_holidays(division, start, end):
        view.entries.append(Entry("bank_holiday", h.title + (" (substitute day)" if h.substitute else ""), h.day,
                                  h.day, "GB", division, None, meta["source"], meta["fetched"],
                                  f"Everyone in {name}"))


def _school(area_key: str, start: date, end: date, view: View, areas: dict[str, SchoolArea]) -> None:
    a = areas.get(area_key)
    if a is None:
        view.unknown.append("School holidays for your area aren't checked yet.")
        return
    covered_until = max((t for _, _, t in a.holidays), default=None)
    if covered_until is None or end > covered_until:
        view.unknown.append(f"{a.authority}'s school holidays are checked for {', '.join(a.years)} only.")
    for title, f, t in a.holidays:
        if f <= end and t >= start:
            view.entries.append(Entry("school_holiday", title, f, t, a.country, a.region, a.authority, a.source,
                                      a.last_verified, f"Schools that follow {a.authority}'s dates", a.exceptions))


def home_calendar(division: str | None, school_area: str | None, start: date, end: date,
                  areas: dict[str, SchoolArea] | None = None) -> View:
    """The traveller's own calendar for the trip's dates. `division` is their nation's bank-holiday division (asked
    as "where are you based", never nationality); `school_area` their council, only if they choose to say it."""
    v = View("home")
    if division:
        _bank(division, start, end, v)
    else:
        v.unknown.append("Bank holidays where you live aren't known.")
    if school_area:
        _school(school_area, start, end, v, load_school_areas() if areas is None else areas)
    v.entries.sort(key=lambda e: (e.start, e.kind))
    return v


def destination_calendar(dest: Destination | None, key: str, start: date, end: date) -> View:
    """The destination's own calendar for the trip's dates. Events, festivals and seasons come later, each with its
    own source; until then the view says what it doesn't know."""
    v = View("destination")
    if dest is None or not dest.bank_holidays:
        name = dest.name if dest else key
        v.unknown.append(f"We don't have {name}'s holidays yet.")
        return v
    _bank(dest.bank_holidays, start, end, v)
    v.unknown.append("Festivals and major events aren't added yet.")
    v.entries.sort(key=lambda e: (e.start, e.kind))
    return v


def local_day(at: datetime, dest: Destination) -> date:
    """The date it is at the destination at an instant: holidays are the place's own dates, never the server's."""
    return at.astimezone(dest.zone).date()


def overlaps(a: Entry, start: date, end: date) -> bool:
    return a.start <= end and a.end >= start


def stay_note(dest: Destination | None, key: str, checkin: date, checkout: date) -> str | None:
    """For a stay's dates: what isn't known about the destination's holidays (None when everything is)."""
    v = destination_calendar(dest, key, checkin, checkout - timedelta(days=0))
    gaps = [u for u in v.unknown if not u.startswith("Festivals")]
    return " ".join(gaps) or None
