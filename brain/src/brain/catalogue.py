"""m235 (WS1, Global Destination Intelligence): one structured record for every experience, anywhere.

A museum, a beach, a market, a shopping street and a guided boat trip don't fit one flat shape, so an `Experience` is
**a common core** that every kind shares, plus **one facet** with the attributes only that kind has:

- **Core:** a global id, the geography (country, region, locality, area, coordinates, time zone), a category and type
  from ODYS's taxonomy, the duration, the opening hours, the price in its own currency, indoor or outdoor,
  accessibility (verified only), getting there, provenance, the recommendation features and the photos with their
  credits.
- **Facets:** culture, nature and views (outdoor), food and drink, shopping, an activity, a neighbourhood, a transport
  experience and a beach. A beach has a lifeguard season and whether swimming is allowed; a museum has whether a
  timed ticket is needed. A restaurant's facet never holds dietary claims: those go through `food.py`'s evidence
  model, never a tag.

**Every fact says where it came from** (`places.Fact`): `checked` at a named source with a date, `claimed` by a source
nobody checked, `estimated` by ODYS, or `unknown`. Nothing is inferred to fill a gap: step-free access stays unknown
unless a card says it, an area is set only where the card's own words name one, and hours the parser can't read stay
as the card's text with no weekly table.

The London cards stay the source of their own facts; `data/catalogue/<locality>.yaml` adds only the category, the
type and the area. Nothing here is used by the planner yet, so plans don't change (tested).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml

from .config import DATA_DIR
from .moments import WEEKDAYS, Moment, load_moments
from .places import Destination, Fact, Point, load_destinations

# ---- the taxonomy --------------------------------------------------------------------------------------------------

# ODYS's own short list: a category, then the types under it. New kinds are added here, never invented per card.
TAXONOMY: dict[str, tuple[str, ...]] = {
    "culture": ("museum", "gallery", "historic_site", "religious_site", "performance", "arts_centre"),
    "nature": ("park", "garden", "wild_park", "riverside_walk", "forest", "mountain", "lake", "beach"),
    "views": ("viewpoint", "tower", "bridge", "riverside", "roof_garden"),
    "food_drink": ("market", "restaurant", "cafe", "bakery", "street_food", "food_street", "bar"),
    "shopping": ("arcade", "market", "market_hall", "department_store", "shopping_street", "bookshop"),
    "activity": ("swimming", "cycling", "karting", "climbing", "kayaking", "guided_tour", "class"),
    "neighbourhood": ("area_walk", "waterfront", "evening_area", "architecture_walk"),
    "transport_experience": ("river_bus", "boat_trip", "cable_car", "heritage_railway"),
    "entertainment": ("live_music", "theatre", "comedy", "sport", "cinema"),
}
FACET_OF_CATEGORY = {"culture": "culture", "nature": "outdoor", "views": "outdoor", "food_drink": "food",
                     "shopping": "shopping", "activity": "activity", "neighbourhood": "area",
                     "transport_experience": "transport", "entertainment": "entertainment"}
Setting = Literal["indoor", "outdoor", "mixed"]
GLOBAL_ID = re.compile(r"^xp:[a-z]{2}:[a-z0-9_]+:[a-z0-9-]+$")   # xp:<country>:<locality>:<slug>
PHOTO_LICENCES = ("CC0", "PD", "Public domain", "CC BY", "CC BY-SA")   # the open licences ODYS shows (photo-credits.md)
PHOTO_CREDITS = DATA_DIR.parents[1] / "app" / "Sources" / "Photos" / "photo-credits.json"


# ---- the core's parts ----------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Geo:
    country: str                    # ISO 3166-1 alpha-2
    region: str | None              # ISO 3166-2 (GB-ENG)
    locality: str                   # the destination registry's key (london)
    locality_name: str
    area: Fact                      # a neighbourhood, only where a source names it
    lat: float
    lon: float
    timezone: str                   # IANA


@dataclass(frozen=True)
class Duration:
    min_minutes: float
    max_minutes: float
    approach_minutes: float | None  # the way in, which is part of the moment
    queue_minutes: float | None


@dataclass(frozen=True)
class OpeningHours:
    """`weekly` maps "mon".."sun" to [(open, close)] in minutes from midnight, in the locality's time zone; None
    means the text couldn't be read into a table (it's kept, and nothing is assumed). An empty list is closed."""
    text: str | None
    weekly: dict[str, list[tuple[int, int]]] | None
    trust: str                      # checked | claimed | unknown
    source: str | None
    checked: str | None

    def open_on(self, day: str) -> bool | None:
        if self.weekly is None:
            return None
        return bool(self.weekly.get(day))


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str                   # ISO 4217: the price's own currency, never converted here
    kind: Literal["free", "entry", "ticket", "food", "hire"]
    per: Literal["person"] = "person"


@dataclass(frozen=True)
class Photo:
    file: str
    title: str | None
    author: str
    licence: str
    licence_url: str | None
    source: str                     # the file's page (Wikimedia Commons)


@dataclass(frozen=True)
class Transport:
    nearest: str | None             # "Green Park or Piccadilly Circus station"
    walk_minutes: float | None      # from there
    by_public_transport: bool | None   # the card's way in starts at a station, stop or pier
    needs_booking: str | None       # the card's own "book ahead" line, when the visit needs one


@dataclass(frozen=True)
class Accessibility:
    """m245: "yes", "partial" or "no", only as a named source says it. Unknown stays unknown, never "no"."""
    step_free: Fact                 # verified only; unknown otherwise
    note: str | None = None         # the source's own words (a quote)


@dataclass(frozen=True)
class Notice:
    """m245: something dated a source announced that changes a visit: a closure, works, a season, an event."""
    what: str
    start: str | None               # ISO date; None = already in force when read
    end: str | None                 # ISO date; None = "until further notice"
    source: str

    def on(self, day: str) -> bool:
        return (self.start is None or self.start <= day) and (self.end is None or day <= self.end)


@dataclass(frozen=True)
class Provenance:
    source: str                     # research | founder | provider name
    checked: str | None             # ISO date the facts were last checked
    assigned: str                   # who assigned the category, type and features


# ---- facets: what only one kind of experience has ------------------------------------------------------------------

@dataclass(frozen=True)
class CultureFacet:
    kind: Literal["culture"] = "culture"
    free_entry: bool | None = None
    timed_ticket: bool | None = None          # a timed or booked slot is needed
    weekday_only: bool | None = None
    booking: Fact = field(default_factory=Fact.unknown)          # m245: required | recommended | none, as stated
    exhibitions: tuple[Notice, ...] = ()                         # dated temporary exhibitions, from the source


@dataclass(frozen=True)
class OutdoorFacet:
    kind: Literal["outdoor"] = "outdoor"
    weather: tuple[str, ...] = ()             # the card's "best in" weather ("dry", "any")
    closes_at_dusk: bool | None = None        # the hours say "dusk"
    light: str | None = None                  # the card's light line
    weather_dependence: Fact = field(default_factory=Fact.unknown)   # m245: how much rain or cold spoils it
    terrain: Fact = field(default_factory=Fact.unknown)              # paths, slopes, steps, as a source says


@dataclass(frozen=True)
class FoodFacet:
    """How a food place is used. Never what it serves for a diet or a belief: that's food.py's evidence."""
    kind: Literal["food"] = "food"
    service: Literal["market", "sit_down", "counter", "street"] | None = None
    as_lunch: bool | None = None              # the card is only planned as the day's lunch
    cuisine: Fact = field(default_factory=Fact.unknown)          # m245: as the venue describes it
    meals: Fact = field(default_factory=Fact.unknown)            # breakfast, lunch, dinner, all day
    price_range: Fact = field(default_factory=Fact.unknown)      # the venue's own menu prices
    reservations: Fact = field(default_factory=Fact.unknown)     # taken | not taken | required
    # Dietary evidence (halal, vegetarian…) is never a field here: a venue's claim goes through food.py's evidence
    # model, behind the DPIA and the solicitor's review (Abram, m224, m244). None is collected now.


@dataclass(frozen=True)
class ShoppingFacet:
    kind: Literal["shopping"] = "shopping"
    covered: bool | None = None
    open_days: tuple[str, ...] = ()           # from the parsed hours, else the card's planning days


@dataclass(frozen=True)
class ActivityFacet:
    kind: Literal["activity"] = "activity"
    exertion: int | None = None               # the card's "active" tag, 0-2
    booking: bool | None = None
    hire: bool | None = None                  # the price is for hiring something
    age_limit: Fact = field(default_factory=Fact.unknown)        # m245: "14 and over", as stated


@dataclass(frozen=True)
class AreaFacet:
    """D72: an area vibe: a centre, flexible time, at most one a day, never the day's peak."""
    kind: Literal["area"] = "area"
    one_a_day: bool = True
    evening: bool | None = None


@dataclass(frozen=True)
class TransportFacet:
    kind: Literal["transport"] = "transport"
    direction: str | None = None              # "Greenwich → Battersea"
    variant: str | None = None                # day | night


@dataclass(frozen=True)
class BeachFacet:
    """For coasts and lakes: none in London. Every field is a Fact, because each changes by season and source."""
    kind: Literal["beach"] = "beach"
    swimming_allowed: Fact = field(default_factory=Fact.unknown)
    lifeguards: Fact = field(default_factory=Fact.unknown)          # e.g. "15 Jun - 15 Sep"
    water_quality: Fact = field(default_factory=Fact.unknown)


@dataclass(frozen=True)
class EntertainmentFacet:
    """m245: a concert, a show, a cinema: what matters is a session, not opening hours."""
    kind: Literal["entertainment"] = "entertainment"
    event_based: bool = True                  # sessions are listed per event; there are no general hours
    sessions: Fact = field(default_factory=Fact.unknown)         # how and where sessions are listed
    tickets: Fact = field(default_factory=Fact.unknown)          # prices and booking, as stated
    age_limit: Fact = field(default_factory=Fact.unknown)


Facet = EntertainmentFacet | CultureFacet | OutdoorFacet | FoodFacet | ShoppingFacet | ActivityFacet | AreaFacet | TransportFacet | BeachFacet


@dataclass(frozen=True)
class Experience:
    id: str                         # xp:<country>:<locality>:<slug>
    legacy_ids: tuple[str, ...]     # the moment card's id, unchanged
    place_id: str | None            # the place underneath (places.PlaceRecord): odys:<card id>, osm:node/…
    name: str
    title: str
    geo: Geo
    category: str
    type: str
    duration: Duration | None
    hours: OpeningHours
    price: Fact                     # a Money, with its trust
    setting: Fact                   # indoor | outdoor | mixed
    accessibility: Accessibility
    transport: Transport
    provenance: Provenance
    features: dict[str, int]        # the recommendation features (place and moment tags, 0-2)
    photos: tuple[Photo, ...]
    facet: Facet
    status: str = "ready"
    notices: tuple[Notice, ...] = ()          # m245: dated closures, seasons and events, from sources
    district: Fact = field(default_factory=Fact.unknown)         # m245: borough or arrondissement, as printed

    def notices_on(self, day: str) -> list[Notice]:
        return [n for n in self.notices if n.on(day)]

    def problems(self) -> list[str]:
        """What breaks the catalogue's rules (an empty list is a valid record)."""
        out = []
        if not GLOBAL_ID.match(self.id):
            out.append(f"id {self.id!r} isn't xp:<country>:<locality>:<slug>")
        if self.category not in TAXONOMY or self.type not in TAXONOMY.get(self.category, ()):
            out.append(f"{self.category}/{self.type} isn't in the taxonomy")
        if self.facet.kind != FACET_OF_CATEGORY.get(self.category) and not (
                self.type == "beach" and self.facet.kind == "beach"):
            out.append(f"facet {self.facet.kind} doesn't fit {self.category}")
        if not (-90 <= self.geo.lat <= 90 and -180 <= self.geo.lon <= 180):
            out.append("coordinates out of range")
        if self.duration and self.duration.min_minutes > self.duration.max_minutes:
            out.append("duration min > max")
        if self.price.known:
            m = self.price.value
            if m.amount < 0 or len(m.currency) != 3 or not m.currency.isupper():
                out.append("price needs an amount ≥ 0 and an ISO 4217 currency")
        if self.provenance.checked is None:
            out.append("no checked date")
        for p in self.photos:
            if not p.author or not p.source or not any(p.licence.startswith(x) for x in PHOTO_LICENCES):
                out.append(f"photo {p.file} lacks an author, a source or an open licence")
        if self.accessibility.step_free.trust == "checked" and self.accessibility.step_free.source is None:
            out.append("checked access with no source")
        if self.accessibility.step_free.known and self.accessibility.step_free.value not in ("yes", "partial", "no"):
            out.append("step-free must be yes, partial or no")
        return out


# ---- opening hours: the cards' own text into a weekly table, where it can be read -----------------------------------

_DAY = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6, "monday": 0, "tuesday": 1,
        "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6, "mondays": 0, "tuesdays": 1,
        "wednesdays": 2, "thursdays": 3, "fridays": 4, "saturdays": 5, "sundays": 6}
_TIME = r"(\d{1,2}):(\d{2})"
_RANGE = re.compile(_TIME + r"\s*[-–]\s*" + _TIME)
_TO = re.compile(r"\bto\s+" + _TIME)


def _days(spec: str) -> list[int] | None:
    s = spec.lower().strip()
    if re.search(r"\b(daily|every day|open daily)\b", s):
        return list(range(7))
    m = re.search(r"\b([a-z]+)\s*[-–]\s*([a-z]+)\b", s)
    if m and m.group(1) in _DAY and m.group(2) in _DAY:
        a, b = _DAY[m.group(1)], _DAY[m.group(2)]
        return [(a + i) % 7 for i in range((b - a) % 7 + 1)]
    found = [_DAY[w] for w in re.findall(r"[a-z]+", s) if w in _DAY]
    return found or None


_SEASONAL = re.compile(r"\b(dusk|sunset|sunrise|seasonal|season|bst|winter|summer|midnight|jan|feb|mar|apr|jun|jul|"
                       r"aug|sep|oct|nov|dec)\b|own hours")
_VAGUE = re.compile(r"\b(about|around|usually|most|roughly|approximately|varies)\b")


def parse_hours(text: str | None) -> dict[str, list[tuple[int, int]]] | None:
    """A weekly table from the plain forms the cards use: "Daily 10:00-18:00, Fridays to 21:00", "Mon, Tue, Wed, Fri
    10:00-20:00; Thu 08:00-18:00", "Sun-Thu 10:30-18:00, Fri-Sat to 21:00", "Tue-Sun 10:00-23:00, closed Monday",
    "Open 24/7". A "closed …" list with dates ("closed 24-26 Dec", "closed weekends, bank holidays, Fri 2 Oct") is an
    exception: its weekdays are closed and its dates are left to the text. Anything else, including hours that change
    by season, "dusk", "midnight", "restaurants' own hours" and vague times ("about 16:00"), gives None: the text is
    kept and nothing is assumed. Exceptions for some weeks ("third Thursday to 20:00") are left out of the table."""
    if not text:
        return None
    t = re.sub(r"\([^)]*\)?", " ", text)               # sources and asides in brackets
    if re.search(r"24/7|24 hours|always open", t.lower()) and not _RANGE.search(t):
        return {d: [(0, 1440)] for d in WEEKDAYS}
    table: dict[int, list[tuple[int, int]]] = {}
    pending: list[int] = []                           # "Mon, Tue, Wed, Fri 10:00-20:00": days waiting for their time
    last_days: list[int] | None = None
    last_open: int | None = None
    for segment in re.split(r";|\.\s", t + " "):
        seg = segment.strip()
        if re.match(r"(?i)closed\b", seg):           # an exception list: weekdays closed, dates left to the text
            for word in re.findall(r"[a-z]+", seg.lower()):
                for d in ([5, 6] if word == "weekends" else [0, 1, 2, 3, 4] if word == "weekdays"
                          else [_DAY[word]] if word in _DAY and not re.search(r"\d", seg) else []):
                    table[d] = []
            continue
        if _SEASONAL.search(seg.lower()) or _VAGUE.search(seg.lower()):
            if _RANGE.search(seg) or _TO.search(seg):
                return None                           # hours that change, or that the source itself only estimates
            continue
        for clause in seg.split(","):
            c = clause.strip()
            if not c or re.search(r"\b(first|second|third|fourth|last)\b", c.lower()):
                continue                              # a week's exception or a last entry: not the regular hours
            r = _RANGE.search(c)
            to = None if r else _TO.search(c)
            days = _days(c[: r.start()] if r else (c[: to.start()] if to else c))
            if r:
                target = pending + (days or [])
                if not target:
                    if last_days is None:
                        return None
                    target = last_days
                lo = int(r.group(1)) * 60 + int(r.group(2))
                hi = int(r.group(3)) * 60 + int(r.group(4))
                for d in target:
                    table[d] = [(lo, hi)]
                last_days, last_open, pending = target, lo, []
            elif to and (days or pending):
                hi = int(to.group(1)) * 60 + int(to.group(2))
                for d in pending + (days or []):
                    start = table[d][0][0] if table.get(d) else last_open
                    if start is None:
                        return None
                    table[d] = [(start, hi)]
                pending = []
            elif days:
                pending += days
    if not any(table.values()):
        return None
    return {WEEKDAYS[d]: table.get(d, []) for d in range(7)}


# ---- from a London card ---------------------------------------------------------------------------------------------

def _slug(card_id: str) -> str:
    return re.sub(r"^(m|a)_", "", card_id).replace("_", "-")


@lru_cache(maxsize=1)
def _photo_credits() -> dict:
    return json.loads(PHOTO_CREDITS.read_text(encoding="utf-8")) if PHOTO_CREDITS.exists() else {}


def _photos(card_id: str) -> tuple[Photo, ...]:
    c = _photo_credits().get(card_id)
    if not c:
        return ()
    return (Photo(c["file"], c.get("title"), c.get("author") or "", c.get("licence") or "", c.get("licenceURL"),
                  c.get("source") or ""),)


def _setting(m: Moment) -> Fact:
    tag = m.tag("outdoor_exposure")
    if tag is None:
        return Fact.unknown()
    return Fact({0: "indoor", 1: "mixed", 2: "outdoor"}[tag], "estimated", "the card's outdoor tag (ODYS)",
                m.last_checked)


def _price(m: Moment, currency: str) -> Fact:
    if m.cost_gbp is None:
        return Fact.unknown()
    kind = "free" if m.cost_gbp == 0 else (m.cost_kind or ("food" if (m.tag("food") or 0) >= 2 else "entry"))
    # a meal's price is ODYS's planning estimate; an entry, ticket or hire price was read from the place's own site
    trust = "estimated" if kind == "food" else "checked"
    return Fact(Money(float(m.cost_gbp), currency, kind), trust,
                "ODYS's planning estimate" if trust == "estimated" else f"the card ({m.source})", m.last_checked)


def _facet(m: Moment, category: str, type_: str, weekly) -> Facet:
    hours = (m.best_time.opening_hours or "").lower()
    if FACET_OF_CATEGORY[category] == "culture":
        return CultureFacet(free_entry=(m.cost_gbp == 0) if m.cost_gbp is not None else None,
                            timed_ticket=bool(m.best_time.book_ahead),
                            weekday_only=set(m.best_time.days) <= set(WEEKDAYS[:5]) if m.best_time.days else False)
    if FACET_OF_CATEGORY[category] == "outdoor":
        return OutdoorFacet(weather=tuple(m.best_time.weather), closes_at_dusk="dusk" in hours, light=m.best_time.light)
    if category == "food_drink":
        service = {"market": "market", "food_street": "street", "street_food": "street", "bakery": "counter",
                   "cafe": "counter", "restaurant": "sit_down", "bar": "sit_down"}.get(type_)
        return FoodFacet(service=service, as_lunch=m.meal == "lunch")
    if category == "shopping":
        days = tuple(d for d in WEEKDAYS if weekly and weekly.get(d)) if weekly else tuple(m.best_time.days)
        return ShoppingFacet(covered=(m.tag("outdoor_exposure") == 0) if m.tag("outdoor_exposure") is not None
                             else None, open_days=days)
    if category == "activity":
        return ActivityFacet(exertion=m.tag("active"), booking=bool(m.best_time.book_ahead), hire=m.cost_kind == "hire")
    if category == "neighbourhood":
        return AreaFacet(evening=type_ == "evening_area" or "after dark" in m.title.lower())
    return TransportFacet(direction=m.direction, variant=m.variant)


def from_card(m: Moment, meta: dict, dest: Destination) -> Experience:
    weekly = parse_hours(m.best_time.opening_hours)
    point = m.approach.start_point if (m.place.lat is None and m.approach.start_point) else None
    lat = m.place.lat if m.place.lat is not None else (point.lat if point else dest.centre.lat)
    lon = m.place.lon if m.place.lon is not None else (point.lon if point else dest.centre.lon)
    exp = m.experience.duration_min
    lo, hi = (exp[0], exp[-1]) if isinstance(exp, list) and exp else ((exp, exp) if exp is not None else (None, None))
    frm = m.approach.from_
    return Experience(
        id=f"xp:{dest.country.lower()}:{dest.key}:{_slug(m.id)}",
        legacy_ids=(m.id,),
        place_id=f"odys:{m.id}",
        name=m.place.name,
        title=m.title,
        geo=Geo(dest.country, dest.region_code, dest.key, dest.name,
                Fact(meta["area"], "claimed", "the card's own title or place name", m.last_checked)
                if meta.get("area") else Fact.unknown(),
                lat, lon, dest.timezone),
        category=meta["category"],
        type=meta["type"],
        duration=Duration(lo, hi, m.approach.duration_min, m.experience.queue_min) if lo is not None else None,
        hours=OpeningHours(m.best_time.opening_hours, weekly,
                           "checked" if m.best_time.opening_hours else "unknown",
                           f"the card ({m.source})" if m.best_time.opening_hours else None, m.last_checked),
        price=_price(m, dest.currency),
        setting=_setting(m),
        accessibility=Accessibility(Fact({True: "yes", False: "no"}[m.approach.step_free], "checked",
                                         f"the card ({m.source})", m.last_checked)
                                    if m.approach.step_free is not None else Fact.unknown()),
        transport=Transport(frm, m.approach.duration_min,
                            bool(re.search(r"station|stop|pier|tube|overground", (frm or "").lower())) if frm else None,
                            m.best_time.book_ahead),
        provenance=Provenance(m.source, m.last_checked, "category and type: Claude, 10 Nov 2026; tags: D91"),
        features={k: v for k, v in {**m.features.place, **m.features.moment}.items() if v is not None},
        photos=_photos(m.id),
        facet=_facet(m, meta["category"], meta["type"], weekly),
        status=m.status,
    )


# ---- m245: facts read from official sources, layered over the cards ------------------------------------------------

_YES_NO = {True: "yes", False: "no"}          # YAML reads a bare yes/no as a boolean


def _access(sf: dict, day: str) -> Accessibility:
    return Accessibility(Fact(_YES_NO.get(sf["value"], sf["value"]), "checked", sf["source"], day), sf.get("quote"))


def _hours(h: dict, day: str) -> OpeningHours:
    """A weekly table only when the source gives plain weekly hours; seasonal, conflicting or general text stays
    text (Abram, m244: "Preserve uncertain opening-hour text rather than forcing it into a schedule")."""
    weekly = parse_hours(h.get("parse", h["text"])) if h.get("status", "verified") == "verified" else None   # `parse`:
    # the plain weekly part of the page's own wording (a substring of `text`, tested), when the rest is detail
    return OpeningHours(h["text"], weekly, "checked", h["source"], day)


def _money(p: dict, currency: str, day: str) -> Fact:
    return Fact(Money(float(p["amount"]), p.get("currency", currency), p.get("kind", "entry")),
                "claimed" if p.get("status") in ("unclear", "claimed") else
                "estimated" if p.get("status") == "estimated" else "checked", p["source"], day)


def _notices(items) -> tuple[Notice, ...]:
    return tuple(Notice(n["what"], n.get("from"), n.get("to"), n["source"]) for n in items or ())


def apply_checked(x: Experience, c: dict, day: str, currency: str) -> Experience:
    """One card's record with the facts an official page gave (data/catalogue/<locality>_checked.yaml) on top."""
    geo = replace(x.geo, area=Fact(c["area"]["value"], "checked", c["area"]["source"], day)) if "area" in c else x.geo
    facet = x.facet
    if "age" in c and isinstance(facet, ActivityFacet):
        facet = replace(facet, age_limit=Fact(c["age"]["quote"], "checked", c["age"]["source"], day))
    if "menu" in c and isinstance(facet, FoodFacet):
        facet = replace(facet, price_range=Fact(c["menu"]["quote"], "checked", c["menu"]["source"], day))
    return replace(x, geo=geo, facet=facet,
                   hours=_hours(c["hours"], day) if "hours" in c else x.hours,
                   price=_money(c["price"], currency, day) if "price" in c else x.price,
                   accessibility=_access(c["step_free"], day) if "step_free" in c else x.accessibility,
                   notices=x.notices + _notices(c.get("notices")))


def load_checked(locality: str, data_dir: Path = DATA_DIR) -> dict:
    f = data_dir / "catalogue" / f"{locality}_checked.yaml"
    return yaml.safe_load(f.read_text(encoding="utf-8")) if f.exists() else {"cards": {}, "not_read": []}


@lru_cache(maxsize=4)
def load_catalogue(data_dir: Path = DATA_DIR, checked: bool = True) -> tuple[Experience, ...]:
    """Every ready card that the catalogue maps, as an Experience, with the official facts read since (m245) on
    top. `checked=False` gives the cards alone (the coverage report's "before"). A ready card left out of the map
    fails loudly."""
    dests = load_destinations(data_dir / "destinations.yaml")
    cards = {m.id: m for m in load_moments(data_dir / "moments") if m.status == "ready"}
    out = []
    for f in sorted((data_dir / "catalogue").glob("*.yaml")):
        d = yaml.safe_load(f.read_text(encoding="utf-8"))
        if "locality" not in d:                    # <locality>_checked.yaml, <locality>_locations.yaml: layers, not a list
            continue
        dest = dests[d["locality"]]
        missing = [i for i in cards if i not in d["experiences"]] if dest.key == "london" else []
        if missing:
            raise ValueError(f"ready cards with no catalogue entry: {missing}")
        ch = load_checked(dest.key, data_dir) if checked else {"cards": {}}
        for i, meta in d["experiences"].items():
            if i in cards:
                x = from_card(cards[i], meta, dest)
                c = ch["cards"].get(i)
                out.append(apply_checked(x, c, ch["checked"], dest.currency) if c else x)
    return tuple(out)


# ---- m245: a destination described in one file, for development (Paris) ---------------------------------------------

DEV_DIR = DATA_DIR / "dev"


def _record_facet(category: str, type_: str, f: dict, day: str) -> Facet:
    fact = lambda k: Fact(f[k]["value"], f[k].get("trust", "checked"), f[k]["source"], day) if k in f else Fact.unknown()
    kind = FACET_OF_CATEGORY[category]
    if kind == "culture":
        return CultureFacet(booking=fact("booking"), timed_ticket=f.get("timed_ticket"))
    if kind == "outdoor":
        return OutdoorFacet(terrain=fact("terrain"), weather_dependence=fact("weather_dependence"),
                            closes_at_dusk=f.get("closes_at_dusk"))
    if kind == "food":
        return FoodFacet(service={"market": "market", "restaurant": "sit_down"}.get(type_), cuisine=fact("cuisine"),
                         reservations=fact("reservations"), price_range=fact("price_range"), meals=fact("meals"))
    if kind == "shopping":
        return ShoppingFacet(covered=f.get("covered"))
    if kind == "activity":
        return ActivityFacet(age_limit=fact("age_limit"))
    if kind == "area":
        return AreaFacet()
    if kind == "entertainment":
        return EntertainmentFacet(sessions=fact("sessions"), tickets=fact("tickets"), age_limit=fact("age_limit"))
    return TransportFacet()


def from_record(key: str, v: dict, dest: Destination, day: str) -> Experience:
    """One experience written straight into the model (no card underneath), every fact with its source."""
    pt = v["point"]
    lo, hi = v.get("minutes", (None, None))
    return Experience(
        id=f"xp:{dest.country.lower()}:{dest.key}:{key.replace('_', '-')}", legacy_ids=(), place_id=pt.get("source"),
        name=v["name"], title=v["title"],
        geo=Geo(dest.country, dest.region_code, dest.key, dest.name,
                Fact(v["area"]["value"], "checked", v["area"]["source"], day) if "area" in v else Fact.unknown(),
                pt["lat"], pt["lon"], dest.timezone),
        category=v["category"], type=v["type"],
        duration=Duration(lo, hi, None, None) if lo is not None else None,
        hours=_hours(v["hours"], day) if "hours" in v else OpeningHours(None, None, "unknown", None, None),
        price=_money(v["price"], dest.currency, day) if "price" in v else Fact.unknown(),
        setting=Fact(v["setting"], "estimated", "Claude's reading of the place", day) if "setting" in v else Fact.unknown(),
        accessibility=_access(v["step_free"], day) if "step_free" in v else Accessibility(Fact.unknown()),
        transport=Transport(v.get("nearest"), None, None, None),
        provenance=Provenance(v.get("source", "research"), day, "category, type and tags: Claude, " + day),
        features=v.get("features", {}), photos=(),
        facet=_record_facet(v["category"], v["type"], v.get("facet", {}), day),
        status=v.get("status", "draft"),
        notices=_notices(v.get("notices")),
        district=Fact(v["district"]["value"], v["district"].get("trust", "checked"), v["district"]["source"], day)
        if "district" in v else Fact.unknown(),
    )


@lru_cache(maxsize=4)
def load_dev(key: str, dev_dir: Path = DEV_DIR) -> tuple[Destination, tuple[Experience, ...], dict]:
    """A development destination (data/dev/<key>.yaml): never in the registry, so never offered to anyone."""
    d = yaml.safe_load((dev_dir / f"{key}.yaml").read_text(encoding="utf-8"))
    g = d["destination"]
    dest = Destination(key, g["name"], g["country"], g.get("region"), g["timezone"], g["currency"],
                       tuple(g.get("languages") or ()), Point(**{k: g["centre"][k] for k in ("lat", "lon")}), None,
                       "none", "estimate", None, g.get("region_code"))
    day = d["checked"]
    return dest, tuple(from_record(k, v, dest, day) for k, v in d["experiences"].items()), d


def ids_in_category(category: str, data_dir: Path = DATA_DIR) -> frozenset[str]:
    """The card ids in a category, so code asks the catalogue ("shopping") instead of listing ids."""
    return frozenset(i for x in load_catalogue(data_dir) if x.category == category for i in x.legacy_ids)
