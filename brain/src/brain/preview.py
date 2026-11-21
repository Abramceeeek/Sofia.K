"""m320 (Abram, 21 Nov: "Seville in the app, me only"): a development destination shown read-only in the app.

A preview is a list of the destination's ready places with what's known about each, and each place's state on the
coming days: the same content as the reviewed preview sheet (`scripts/seville_preview.py`), from the same data. It is
not a plan: nothing is ranked for the person, planned, booked or searched, and it makes no claim of support. Its
readiness stays Development (readiness.py); a code (`data/previews.yaml`) keeps it out of everyone else's way.

What each place says, and nothing else:
- the hours as the venue prints them, with the page and the date it was read;
- the state on each day, in three words: "open" (the venue's own page, read within 180 days, lists that day),
  "check" (probably open, but the hours come from an older leaflet, a non-secure page or a seasonal timetable),
  "shut" (the venue's own hours or a dated notice leave that day out). From `quality.availability`, unchanged;
- the price in its own currency, or "Price not printed"; "as printed, not confirmed" where nobody checked it;
- step-free only where the venue says so; otherwise "Step-free access not known", never "no".
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from . import quality
from .catalogue import Experience, load_dev
from .config import DATA_DIR
from .destination import load_emergency

DAYS = 7
STATE = {"confirmed open": "open", "might be open": "check", "closed or unavailable": "shut"}
KINDS = {"culture": "Museums and monuments", "views": "Views", "nature": "Parks", "neighbourhood": "Areas to wander",
         "food_drink": "Markets and food", "shopping": "Shopping", "activity": "Things to do",
         "entertainment": "Shows", "transport_experience": "On the water and in the air"}
SYMBOL = {"EUR": "€", "GBP": "£"}
CAVEAT = ("This is a preview: ODYS doesn't plan days, journeys or bookings here yet. Please don't rely on it alone: "
          "check each place's own site on the day for hours, prices and bookings.")


@dataclass(frozen=True)
class Preview:
    key: str
    code: str
    dev: str
    name: str
    country: str
    country_name: str


@lru_cache(maxsize=1)
def load_previews(path: Path = DATA_DIR / "previews.yaml") -> dict[str, Preview]:
    with open(path, encoding="utf-8") as f:
        raw = (yaml.safe_load(f) or {}).get("previews") or {}
    return {k: Preview(key=k, code=v["code"].upper(), dev=v["dev"], name=v["name"], country=v["country"],
                       country_name=v["country_name"]) for k, v in raw.items()}


def by_code(code: str | None) -> Preview | None:
    return next((p for p in load_previews().values() if code and p.code == code), None)


def info(p: Preview) -> dict:
    em = load_emergency().get(p.country)
    return {"key": p.key, "name": p.name, "country": p.country, "country_name": p.country_name,
            "label": "Preview: not fully supported",
            "emergency_number": em.lines[0].number if em and em.lines else None}   # Help & safety shows it too


def price_text(x: Experience) -> str:
    if not x.price.known:
        return "Price not printed"
    m = x.price.value
    unconfirmed = "" if x.price.trust == "checked" else " (as printed, not confirmed)"
    if m.kind == "free" or m.amount == 0:
        return "Free" + unconfirmed
    amount = f"{m.amount:g}" if float(m.amount).is_integer() else f"{m.amount:.2f}"     # €15.50, never €15.5
    return f"{SYMBOL.get(m.currency, m.currency + ' ')}{amount}" + unconfirmed


def access_text(x: Experience) -> str:
    sf = x.accessibility.step_free
    if sf.known and sf.value == "yes":
        return "Step-free (the venue says)"
    if sf.known and sf.value == "partial":
        return "Partly step-free (the venue says)"
    if sf.known and sf.value == "no":
        return "Not step-free (the venue says)"
    return "Step-free access not known"


def notice_text(n) -> str:
    if not n.start:
        return n.what if not n.end else f"{n.what} (until {_short(n.end)})"
    if n.end == n.start:
        return f"{n.what} ({_short(n.start)})"
    return f"{n.what} ({_short(n.start)} to {_short(n.end) if n.end else 'further notice'})"


def _short(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {d:%b %Y}"


def _dedupe(xs: list[str]) -> list[str]:
    return list(dict.fromkeys(xs))


def place(x: Experience, days: list[date], today: date) -> dict:
    return {"id": x.id, "name": x.name, "title": x.title, "kind": KINDS.get(x.category, x.category),
            "category": x.category, "district": x.district.value if x.district.known else None,
            "lat": x.geo.lat, "lon": x.geo.lon,
            "hours": x.hours.text or "Opening hours not printed",
            "hours_source": x.hours.source if (x.hours.source or "").startswith("http") else None,
            "hours_read": x.hours.checked,
            "states": [STATE[quality.availability(x, d, today)] for d in days],
            "price": price_text(x), "access": access_text(x),
            "notices": _dedupe([notice_text(n) for n in x.notices])}


def content(p: Preview, today: date | None = None, days: int = DAYS) -> dict:
    """The preview for the `days` days from `today` (by default, today in the destination's own time zone), in the
    sheet's order."""
    dest, xs, raw = load_dev(p.dev)
    today = today or datetime.now(ZoneInfo(dest.timezone)).date()
    ready = [x for x in xs if x.status == "ready"]
    span = [today + timedelta(days=i) for i in range(days)]
    order = {c: i for i, c in enumerate(KINDS)}
    ready.sort(key=lambda x: order.get(x.category, len(order)))      # stable: the data's own order within a kind
    em = load_emergency().get(p.country)
    airport = (raw.get("transport") or {}).get("airport") or {}
    weather = raw.get("weather") or {}
    return {
        **info(p),
        "timezone": dest.timezone, "currency": dest.currency,
        "caveat": CAVEAT,
        "read": raw.get("checked"),
        "days": [{"date": d.isoformat(), "label": f"{d:%a} {d.day}"} for d in span],
        "emergency": ({"number": em.lines[0].number, "line": em.lines[0].line, "source": em.lines[0].source,
                       "checked": em.checked} if em and em.lines else None),
        "places": [place(x, span, today) for x in ready],
        "airport": [line for line in (airport.get("bus") and f"Bus: {airport['bus']}",
                                      airport.get("taxi") and f"Taxi: {airport['taxi']}") if line],
        "airport_source": airport.get("source"),
        "not_covered": [
            "City buses, metro and journey times: the operators' pages couldn't be read, so none are given.",
            "Weather: no forecast here. " + (f"AEMET, Spain's weather service: {weather['page']}"
                                             if weather.get("page") else ""),
            "Restaurant prices, step-free access at most places, and dietary information: not checked.",
            f"{p.name}'s own local holidays: not included.",
        ],
    }
