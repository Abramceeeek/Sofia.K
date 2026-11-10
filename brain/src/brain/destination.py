"""m236 (WS2, Global Destination Intelligence): what ODYS knows about a destination before recommending anything in it,
from any mix of providers, with each part saying where it came from and how sure it is.

A destination's profile has eight parts, the ones Abram listed for "a user enters Kyoto":
- **geography:** the destination (registry: country, region, time zone, currency, languages, centre);
- **areas:** its neighbourhoods or districts, each with a centre;
- **travel:** how long it takes to get between areas (a model with its parameters and its source);
- **experiences:** the catalogue's experiences there (catalogue.py), never raw places;
- **seasons:** what changes by month, each note with its source;
- **holidays:** public holidays in a date range;
- **stays:** where the places to stay are, by area;
- **emergency:** the country's emergency numbers (data/emergency.yaml).

**Providers** fill parts. Each implements only what it has (`DestinationProvider`); `assemble` takes the first provider
that answers each part and records which one did. Nothing calls a network here: OpenStreetMap, Wikidata, Overture or a
paid service would each be one more provider, behind the same interface, once Abram decides on them
(decisions/destination-intelligence.md).

A part nobody supplies is **missing, and said**: `readiness()` lists what's missing or only estimated, so a
destination is never offered as if it were understood (product-direction.md, E; the quality standard, m234).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Protocol

import yaml

from .catalogue import Experience, load_catalogue
from .config import DATA_DIR
from .moments import Point
from .places import Destination, Fact, load_destinations
from .travel import LondonEstimate, haversine_m

PARTS = ("areas", "travel", "experiences", "seasons", "holidays", "stays", "emergency")


@dataclass(frozen=True)
class Area:
    key: str
    name: str
    centre: Point
    source: str                    # where the area and its centre come from


@dataclass(frozen=True)
class TravelModel:
    """Door-to-door minutes between two points: walk when it's short, else public transport. The parameters say
    where they came from; a measured provider (TfL, a GTFS router) replaces the estimate where one exists."""
    walk_kmh: float
    detour: float
    walk_max_min: float
    transit_kmh: float
    access_min: float
    egress_min: float
    source: str
    trust: str = "estimated"

    def _walk(self, a: Point, b: Point) -> float:
        return haversine_m(a, b) * self.detour / (self.walk_kmh * 1000 / 60)

    def mode(self, a: Point, b: Point) -> str:
        return "walk" if self._walk(a, b) <= self.walk_max_min else "transit"

    def minutes(self, a: Point, b: Point) -> float:
        walk = self._walk(a, b)
        if walk <= self.walk_max_min:
            return walk
        transit = self.access_min + haversine_m(a, b) * 1.3 / (self.transit_kmh * 1000 / 60) + self.egress_min
        return min(walk, transit)


@dataclass(frozen=True)
class SeasonNote:
    months: tuple[int, ...]        # 1-12
    note: str
    source: str
    checked: str | None


@dataclass(frozen=True)
class Holiday:
    day: date
    name: str
    source: str


@dataclass(frozen=True)
class StayPoint:
    name: str
    point: Point
    sample: bool                   # made-up sample results (trips.py), never presented as real


@dataclass(frozen=True)
class EmergencyLine:
    title: str
    line: str
    number: str
    source: str


@dataclass(frozen=True)
class Emergency:
    country: str
    name: str
    lines: tuple[EmergencyLine, ...]
    checked: str | None


class DestinationProvider(Protocol):
    """A source of what's known about destinations. A provider answers the parts it has and returns None for the
    rest (or for destinations it doesn't know)."""
    name: str

    def part(self, which: str, dest: Destination, start: date | None = None, end: date | None = None): ...


@dataclass
class Profile:
    dest: Destination
    parts: dict[str, object] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)      # part -> provider name

    @property
    def areas(self) -> list[Area]:
        return list(self.parts.get("areas") or [])

    @property
    def experiences(self) -> list[Experience]:
        return list(self.parts.get("experiences") or [])

    @property
    def travel(self) -> TravelModel | None:
        return self.parts.get("travel")

    def nearest_area(self, p: Point) -> Area | None:
        return min(self.areas, key=lambda a: haversine_m(a.centre, p)) if self.areas else None

    def area_matrix(self) -> dict[tuple[str, str], tuple[int, str]]:
        """Minutes and mode between every pair of areas' centres, from the travel model."""
        t = self.travel
        if t is None:
            return {}
        return {(a.key, b.key): (round(t.minutes(a.centre, b.centre)), t.mode(a.centre, b.centre))
                for a in self.areas for b in self.areas if a.key != b.key}

    def experiences_by_area(self) -> dict[str, Counter]:
        """Each area's experiences by category: an experience counts for its own area where its record names one,
        else for the nearest area centre (said as 'nearest')."""
        out: dict[str, Counter] = {a.key: Counter() for a in self.areas}
        names = {a.name: a.key for a in self.areas}
        for x in self.experiences:
            key = names.get(x.geo.area.value) if x.geo.area.known else None
            if key is None:
                near = self.nearest_area(Point(lat=x.geo.lat, lon=x.geo.lon))
                key = near.key if near else None
            if key is not None:
                out[key][x.category] += 1
        return out

    def stays_by_area(self) -> dict[str, int]:
        out: Counter = Counter()
        for s in self.parts.get("stays") or []:
            a = self.nearest_area(s.point)
            if a:
                out[a.key] += 1
        return dict(out)

    def seasons_in(self, month: int) -> list[SeasonNote]:
        return [s for s in self.parts.get("seasons") or [] if month in s.months]

    def readiness(self) -> dict:
        """What's known, what's only estimated or sample, and what's missing. A destination is ready to offer only
        with experiences that are checked, a travel model, holidays and checked emergency numbers."""
        missing = [p for p in PARTS if not self.parts.get(p)]
        weak = []
        if self.travel is not None and self.travel.trust != "checked":
            weak.append(f"travel times are {self.travel.trust} ({self.travel.source})")
        stays = self.parts.get("stays") or []
        if stays and all(s.sample for s in stays):
            weak.append("places to stay are sample results")
        xs = self.experiences
        unchecked = [x for x in xs if x.provenance.checked is None]
        if unchecked:
            weak.append(f"{len(unchecked)} experiences have no checked date")
        hours_known = sum(1 for x in xs if x.hours.weekly) if xs else 0
        must = ("experiences", "travel", "holidays", "emergency")
        return {"missing": missing, "weak": weak, "experiences": len(xs), "hours_as_table": hours_known,
                "ready": not any(p in missing for p in must) and not unchecked}


def assemble(dest: Destination, providers: list[DestinationProvider], start: date | None = None,
             end: date | None = None) -> Profile:
    """Each part from the first provider that has it; which provider answered is kept with the part."""
    prof = Profile(dest)
    for which in PARTS:
        for p in providers:
            got = p.part(which, dest, start, end)
            if got:
                prof.parts[which], prof.sources[which] = got, p.name
                break
    return prof


# ---- providers ------------------------------------------------------------------------------------------------------

def load_emergency(path: Path = DATA_DIR / "emergency.yaml") -> dict[str, Emergency]:
    d = yaml.safe_load(path.read_text(encoding="utf-8"))["countries"]
    return {cc: Emergency(cc, v["name"], tuple(EmergencyLine(x["title"], x["line"], x["number"], x["source"])
                                              for x in v["lines"]), v.get("checked"))
            for cc, v in d.items()}


class EmergencyProvider:
    """data/emergency.yaml: each country's own official numbers (m236)."""
    name = "ODYS emergency numbers (official pages, read 10 Nov 2026)"

    def __init__(self, path: Path = DATA_DIR / "emergency.yaml"):
        self.by_country = load_emergency(path)

    def part(self, which, dest, start=None, end=None):
        return self.by_country.get(dest.country) if which == "emergency" else None


class CatalogueProvider:
    """The checked catalogue (catalogue.py) for its destinations. Areas are the ones the cards themselves name, centred
    on their experiences; travel is the London estimate (TfL's measured times are used by the planner where known);
    holidays come from GOV.UK's file for the destination's division; stays are the labelled sample results."""
    name = "ODYS catalogue"

    def __init__(self, data_dir: Path = DATA_DIR):
        self.catalogue = load_catalogue(data_dir)

    def part(self, which, dest, start=None, end=None):
        xs = [x for x in self.catalogue if x.geo.locality == dest.key]
        if not xs:
            return None
        if which == "experiences":
            return xs
        if which == "areas":
            named: dict[str, list[Experience]] = {}
            for x in xs:
                if x.geo.area.known:
                    named.setdefault(x.geo.area.value, []).append(x)
            return [Area(_key(n), n, Point(lat=sum(x.geo.lat for x in g) / len(g), lon=sum(x.geo.lon for x in g) / len(g)),
                         "the cards' own titles; centre = the mean of their experiences")
                    for n, g in sorted(named.items())]
        if which == "travel" and dest.key == "london":
            e = LondonEstimate()
            return TravelModel(e.walking.speed_m_per_min * 60 / 1000, e.walking.detour, e.walk_max_min, e.transit_m_per_min * 60 / 1000,
                               e.access_min, e.egress_min, "the planner's London estimate (travel.py, GUESS)")
        if which == "holidays" and dest.bank_holidays and start and end:
            from .traveltiming import bank_holidays
            return [Holiday(h.day, h.title, "GOV.UK bank holidays") for h in bank_holidays(dest.bank_holidays, start, end)]
        if which == "stays":
            from .trips import StayQuery, sample_stays
            q = StayQuery(dest.name, dest.country, dest.centre.lat, dest.centre.lon, start or date(2026, 12, 1),
                          end or date(2026, 12, 4))
            return [StayPoint(s.name, Point(lat=s.lat, lon=s.lon), True) for s in sample_stays(q) if s.lat is not None]
        return None


class FileProvider:
    """A destination described in one YAML file: the synthetic test destination, or a hand-checked extract later.
    Its experiences use the catalogue's own fields."""

    def __init__(self, path: Path):
        self.d = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.name = self.d.get("provider", path.name)

    def part(self, which, dest, start=None, end=None):
        if self.d.get("destination") != dest.key:
            return None
        d = self.d
        if which == "areas":
            return [Area(k, v["name"], Point(**v["centre"]), d.get("source", self.name)) for k, v in d.get("areas", {}).items()]
        if which == "travel" and "travel" in d:
            t = d["travel"]
            return TravelModel(t["walk_kmh"], t["detour"], t["walk_max_min"], t["transit_kmh"], t["access_min"],
                               t["egress_min"], t["source"], t.get("trust", "estimated"))
        if which == "experiences":
            return [_file_experience(k, v, dest) for k, v in d.get("experiences", {}).items()]
        if which == "seasons":
            return [SeasonNote(tuple(s["months"]), s["note"], s["source"], s.get("checked")) for s in d.get("seasons", [])]
        if which == "holidays" and start and end:
            return [Holiday(date.fromisoformat(h["day"]), h["name"], h["source"]) for h in d.get("holidays", [])
                    if start <= date.fromisoformat(h["day"]) <= end]
        if which == "stays":
            return [StayPoint(s["name"], Point(**s["point"]), bool(s.get("sample", True))) for s in d.get("stays", [])]
        return None


def _key(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")


def _file_experience(key: str, v: dict, dest: Destination) -> Experience:
    from .catalogue import (FACET_OF_CATEGORY, Accessibility, AreaFacet, BeachFacet, CultureFacet, Duration, FoodFacet,
                            Geo, Money, OpeningHours, OutdoorFacet, Provenance, Transport, parse_hours)
    facet = {"culture": CultureFacet, "outdoor": OutdoorFacet, "food": FoodFacet, "area": AreaFacet}[
        FACET_OF_CATEGORY[v["category"]]]() if v["type"] != "beach" else BeachFacet()
    price = Fact(Money(float(v["price"]), dest.currency, "free" if v["price"] == 0 else v.get("price_kind", "entry")),
                 v.get("trust", "claimed"), v["source"], v.get("checked")) if "price" in v else Fact.unknown()
    return Experience(
        id=f"xp:{dest.country.lower()}:{dest.key}:{key.replace('_', '-')}", legacy_ids=(), place_id=v.get("place_id"),
        name=v["name"], title=v["title"],
        geo=Geo(dest.country, dest.region_code, dest.key, dest.name,
                Fact(v["area"], "claimed", v["source"], v.get("checked")) if v.get("area") else Fact.unknown(),
                v["point"]["lat"], v["point"]["lon"], dest.timezone),
        category=v["category"], type=v["type"],
        duration=Duration(v["minutes"][0], v["minutes"][1], None, None) if v.get("minutes") else None,
        hours=OpeningHours(v.get("hours"), parse_hours(v.get("hours")), "claimed" if v.get("hours") else "unknown",
                           v["source"] if v.get("hours") else None, v.get("checked")),
        price=price, setting=Fact(v["setting"], "claimed", v["source"], v.get("checked")) if v.get("setting") else Fact.unknown(),
        accessibility=Accessibility(Fact.unknown()), transport=Transport(v.get("nearest"), None, None, None),
        provenance=Provenance(v["source"], v.get("checked"), "the file"), features=v.get("features", {}), photos=(),
        facet=facet)


def destinations_with(extra: dict | None = None, path: Path = DATA_DIR / "destinations.yaml") -> dict[str, Destination]:
    """The registry, plus destinations described elsewhere (the synthetic test destination)."""
    dests = load_destinations(path)
    for key, v in (extra or {}).items():
        dests[key] = Destination(key, v["name"], v["country"], v.get("region"), v["timezone"], v["currency"],
                                 tuple(v.get("languages") or ()), Point(**v["centre"]), None, v.get("coverage", "none"),
                                 v.get("travel", "estimate"), None, v.get("region_code"))
    return dests


def distance_km(a: Point, b: Point) -> float:
    return haversine_m(a, b) / 1000


__all__ = ["Area", "TravelModel", "SeasonNote", "Holiday", "StayPoint", "Emergency", "EmergencyLine", "Profile",
           "assemble", "CatalogueProvider", "FileProvider", "EmergencyProvider", "load_emergency", "destinations_with",
           "distance_km"]
