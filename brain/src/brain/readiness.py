"""m248 (WS5): what ODYS must know before it can say it supports a destination (Abram, m244: "A destination should
not become fully supported simply because a few places have been entered into the database").

Before any level, **development**: data is being gathered; nothing is offered to anyone. Then Abram's three levels
(m252, m259):
1. **Preview**: every *essential* item passes. For internal development and evaluation; never presented as reliable
   coverage.
2. **Limited support**: preview, plus fresh hours (80%), named areas (60%), known accessibility (50%) and sourced or
   labelled prices, and Abram has reviewed it. Offered for the features that pass, with the limits said.
3. **Supported**: every item passes, and Abram has reviewed it.

**What may be claimed depends on each feature, not on the level** (`claims`): accessibility is never "comprehensive"
because half of the places are known; transport is "official" only when an official source is behind it.

Each item is pass, partial, fail or unknown, with the evidence counted from the data. The thresholds are Claude's
proposal (GUESS) for Abram to set; they're constants here so a change is one line and a test.
"""

from __future__ import annotations

from dataclasses import dataclass
from zoneinfo import ZoneInfo

from .catalogue import _SEASONAL, Experience

MIN_READY = 20              # GUESS: enough for a few days without repeats
MIN_CATEGORIES = 6          # of the taxonomy's 9, so it isn't only museums and landmarks
HOURS_SHARE = 0.8           # checked hours (or sessions) on an official page, in the last 180 days
ACCESS_SHARE = 0.5          # step-free known (yes, partial or no) from a named source
AREA_SHARE = 0.6            # a named area or a printed district
FRESH_DAYS = 180
ECB_CURRENCIES = frozenset("USD JPY BGN CZK DKK GBP HUF PLN RON SEK CHF ISK NOK TRY AUD BRL CAD CNY HKD IDR ILS INR "
                           "KRW MXN MYR NZD PHP SGD THB ZAR EUR".split())   # fx.py's ECB set, plus the euro itself


@dataclass(frozen=True)
class Item:
    key: str
    label: str
    essential: bool          # essential: needed for a preview; else a quality item, needed for "supported"
    status: str              # pass | partial | fail | unknown
    evidence: str


@dataclass(frozen=True)
class Inputs:
    """What a destination's data says, gathered by the caller (tests, the coverage script)."""
    country: str
    timezone: str
    currency: str
    emergency_lines: int             # official emergency numbers for the country, with sources
    emergency_checked: str | None
    holidays_source: str | None      # the government page for public holidays
    holiday_years: tuple[int, ...]   # the years it covers
    school_holidays: str             # checked | partial | not relevant | missing
    transport: str                   # checked (an official journey planner) | estimated | missing
    formats: str | None              # the locale whose date and number formats are recorded (data/formats.yaml)
    photos_checked: bool             # every photo's page read one by one (or there are none)
    located: int | None = None       # experiences whose location an independent source confirms (else counted here)


def _share(n: int, d: int) -> str:
    return f"{n} of {d}" if d else "none"


def checklist(inp: Inputs, ready: list[Experience], today: str, trip_year: int) -> list[Item]:
    n = len(ready)
    fresh = lambda d: d is not None and d >= _days_before(today, FRESH_DAYS)
    hours = sum(1 for x in ready if (getattr(x.facet, "event_based", False) and x.facet.sessions.known)
                or (x.hours.trust == "checked" and (x.hours.source or "").startswith("https://") and fresh(x.hours.checked)))
    access = sum(1 for x in ready if x.accessibility.step_free.known)
    area = sum(1 for x in ready if x.geo.area.known or x.district.known)
    outdoor = [x for x in ready if x.category in ("nature", "views", "neighbourhood")]
    seasonal = sum(1 for x in outdoor if x.notices or _SEASONAL.search((x.hours.text or "").lower()))
    cats = {x.category for x in ready}
    located = inp.located if inp.located is not None else sum(
        1 for x in ready if (x.place_id or "").startswith(("wikidata:", "osm")))
    try:
        ZoneInfo(inp.timezone)
        tz = "pass"
    except Exception:            # noqa: BLE001: any failure means the zone isn't usable
        tz = "fail"
    ratio = lambda k, d, t: "pass" if d and k / d >= t else ("partial" if k else "fail")
    return [
        Item("emergency", "Official emergency numbers, with their sources", True,
             "pass" if inp.emergency_lines else "fail",
             f"{inp.emergency_lines} lines, checked {inp.emergency_checked}" if inp.emergency_lines else "none checked"),
        Item("holidays", "Public holidays from the government's own page", True,
             "pass" if inp.holidays_source and trip_year in inp.holiday_years else ("partial" if inp.holidays_source else "fail"),
             f"{inp.holidays_source} ({', '.join(map(str, inp.holiday_years))})" if inp.holidays_source else "none"),
        Item("currency", "Local currency, with a published exchange rate", True,
             "pass" if inp.currency in ECB_CURRENCIES else "partial", inp.currency),
        Item("timezone", "Time zone (IANA), for clock changes and opening times", True, tz, inp.timezone),
        Item("experiences", f"At least {MIN_READY} ready experiences, each with a checked location and hours", True,
             "pass" if n >= MIN_READY and located >= MIN_READY else ("partial" if n else "fail"),
             f"{n} ready; {located} with a sourced location"),
        Item("variety", f"At least {MIN_CATEGORIES} kinds of experience, not only landmarks", True,
             "pass" if len(cats) >= MIN_CATEGORIES else "partial", f"{len(cats)}: {', '.join(sorted(cats))}"),
        Item("transport", "Getting around: an official journey planner, or estimates said as such", True,
             {"checked": "pass", "estimated": "partial"}.get(inp.transport, "fail"), inp.transport),
        Item("formats", "Local date and number formats", False, "pass" if inp.formats else "unknown",
             inp.formats or "not recorded"),
        Item("school", "School holidays, where they change crowds", False,
             {"checked": "pass", "not relevant": "pass", "partial": "partial"}.get(inp.school_holidays, "fail"),
             inp.school_holidays),
        Item("hours", f"Opening hours or sessions read on an official page in the last {FRESH_DAYS} days", False,
             ratio(hours, n, HOURS_SHARE), _share(hours, n)),
        Item("access", "Step-free access known from a named source (unknown never counts as no)", False,
             ratio(access, n, ACCESS_SHARE), _share(access, n)),
        Item("areas", "Neighbourhoods or districts named by a source", False, ratio(area, n, AREA_SHARE), _share(area, n)),
        Item("seasons", "Seasonal information for outdoor experiences", False,
             ratio(seasonal, len(outdoor), 1.0) if outdoor else "pass", _share(seasonal, len(outdoor))),
        Item("photos", "Photos' licences and credits checked one by one", False,
             "pass" if inp.photos_checked else "fail", "yes" if inp.photos_checked else "no"),
        Item("prices", "Every price shown has a source, or is labelled an estimate (unknown stays unknown)", False,
             "pass" if all(x.price.source and (x.price.trust == "estimated" or x.price.source) for x in ready
                           if x.price.known) else "fail",
             f"{sum(1 for x in ready if x.price.known)} priced, {sum(1 for x in ready if not x.price.known)} unknown"),
    ]


LIMITED = ("hours", "areas", "access", "prices")   # limited support's quality items (Abram, m260)


def level(items: list[Item], reviewed_by_abram: bool = False) -> str:
    """development → preview (all essentials pass) → limited support (and fresh hours and areas, reviewed) →
    supported (everything passes, reviewed)."""
    if not all(i.status == "pass" for i in items if i.essential):
        return "development"
    by = {i.key: i for i in items}
    if reviewed_by_abram and all(i.status == "pass" for i in items):
        return "supported"
    if reviewed_by_abram and all(by[k].status == "pass" for k in LIMITED):
        return "limited support"
    return "preview"


def assessment(items: list[Item], last_reviewed: str, reviewed_by: str, abram_final_review: str | None = None) -> dict:
    """m263 (Abram, m260): every assessment carries its last review date; Supported needs Abram's final manual
    review (a date), not just passing numbers."""
    lv = level(items, reviewed_by_abram=abram_final_review is not None)
    return {"level": lv, "last_reviewed": last_reviewed, "reviewed_by": reviewed_by,
            "abram_final_review": abram_final_review, "items": [i.__dict__ for i in items], "claims": claims(items),
            "gaps": [f"{i.label}: {i.evidence}" for i in items if i.status != "pass"]}


def claims(items: list[Item]) -> dict[str, str]:
    """m259: what ODYS may say about each feature in this destination, from the evidence, whatever the level."""
    by = {i.key: i for i in items}
    access = by["access"]
    known, total = (access.evidence.split(" of ") + ["0"])[:2] if " of " in access.evidence else ("0", "0")
    return {
        "accessibility": ("verified step-free status for every place" if known == total and total != "0" else
                          f"step-free status per place where a source gives it ({access.evidence}); "
                          "unknown is shown as unknown, never as step-free"),
        "transport": {"pass": "journey times from an official journey planner",
                      "partial": "estimated journey times, labelled as estimates; not official transport information"
                      }.get(by["transport"].status, "no journey times"),
        "opening_hours": f"hours read on an official page for {by['hours'].evidence}; others said as unknown or varying",
        "emergency": "official emergency numbers" if by["emergency"].status == "pass" else "none: not offered",
        "seasons": f"seasonal information for {by['seasons'].evidence} outdoor places",
        "photos": "licences checked one by one" if by["photos"].status == "pass" else "photos not checked: none shown",
    }


def _days_before(day: str, n: int) -> str:
    from datetime import date, timedelta
    return (date.fromisoformat(day) - timedelta(days=n)).isoformat()


__all__ = ["Item", "Inputs", "checklist", "level", "claims", "assessment", "MIN_READY", "MIN_CATEGORIES"]
