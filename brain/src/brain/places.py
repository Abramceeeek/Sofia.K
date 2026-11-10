"""WS1 (m207): places from any source, in one shape, with every fact's source and date, or "unknown".

`decisions/global-place-data.md` has the reasoning and the sources compared. This module is the first, non-breaking
step: nothing in the planner uses it yet. The planner keeps planning the checked London moment cards exactly as before;
this gives the next city (and the next source) somewhere to land without London assumptions spreading further.

Three ideas:
- **A destination** (`data/destinations.yaml`) says what changes from place to place: time zone, currency, languages,
  bank-holiday division, which travel-time and weather services, and whether coverage is checked.
- **A place record** has a namespaced id (`odys:m_bm_great_court`, `osm:node/123`, `wikidata:Q6373`), so ids from
  different sources never collide and the existing card ids stay exactly as they are.
- **Every fact is a `Fact`**: its value, where it came from, when it was checked, and how much it can be trusted:
  `checked` (we checked it at a named source), `claimed` (the source says so but nobody checked: a community map tag,
  a venue's own page) or `unknown`. Nothing is inferred: no halal status from a cuisine, no step-free access from a
  building's age, no opening hours from a category.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Generic, Literal, Protocol, TypeVar
from zoneinfo import ZoneInfo

import yaml

from .moments import Moment, Point

T = TypeVar("T")
Trust = Literal["checked", "claimed", "estimated", "unknown"]   # m235: "estimated" is ODYS's own estimate


@dataclass(frozen=True)
class Fact(Generic[T]):
    value: T | None
    trust: Trust
    source: str | None = None       # a URL, or a provider name with the record's id
    checked: str | None = None      # ISO date it was checked (checked) or fetched (claimed)

    @staticmethod
    def unknown() -> "Fact":
        return Fact(None, "unknown")

    @property
    def known(self) -> bool:
        return self.trust != "unknown" and self.value is not None


@dataclass(frozen=True)
class Destination:
    key: str
    name: str
    country: str                    # ISO 3166-1 alpha-2
    region: str | None
    timezone: str                   # IANA
    currency: str                   # ISO 4217
    languages: tuple[str, ...]
    centre: Point
    bank_holidays: str | None       # the GOV.UK division, for UK destinations
    coverage: Literal["checked", "none"]
    travel: str                     # "tfl" | "estimate"
    weather: str | None
    region_code: str | None = None  # m235: ISO 3166-2 (GB-ENG)

    @property
    def zone(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)


def load_destinations(path: Path) -> dict[str, Destination]:
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)["destinations"]
    out = {}
    for key, v in d.items():
        ZoneInfo(v["timezone"])   # a bad zone name fails here, at load
        if len(v["currency"]) != 3 or not v["currency"].isupper():
            raise ValueError(f"{key}: currency must be an ISO 4217 code")
        out[key] = Destination(key, v["name"], v["country"], v.get("region"), v["timezone"], v["currency"],
                               tuple(v.get("languages") or ()), Point(**v["centre"]), v.get("bank_holidays"),
                               v.get("coverage", "none"), v.get("travel", "estimate"), v.get("weather"),
                               v.get("region_code"))
    return out


@dataclass(frozen=True)
class Price:
    amount: float
    currency: str
    kind: str                       # entry | ticket | food | hire | free


@dataclass(frozen=True)
class PlaceRecord:
    id: str                         # "<provider>:<native id>": never reused across providers
    provider: str
    name: str
    destination: str
    point: Point | None
    category: Fact[str]
    opening_hours: Fact[str]        # as the source writes it; parsing it is a separate, per-source step
    price: Fact[Price]
    step_free: Fact[str]            # "yes" | "limited" | "no", as the source says it
    diet: dict[str, Fact[str]] = field(default_factory=dict)   # e.g. "halal": Fact("yes", "claimed", "osm:…")
    website: Fact[str] = field(default_factory=Fact.unknown)
    licence: str = ""
    attribution: str = ""           # what must be shown wherever this record's data is shown
    same_as: tuple[str, ...] = ()   # the same place in other sources ("wikidata:Q…", an Overture GERS id)

    def unknowns(self) -> list[str]:
        """The facts this record doesn't have, said out loud rather than filled in."""
        out = [n for n in ("category", "opening_hours", "price", "step_free", "website")
               if not getattr(self, n).known]
        return out + ([] if self.diet else ["diet"])


class PlaceProvider(Protocol):
    """A source of places. Each adapter turns its source's records into `PlaceRecord`s and says its licence and the
    attribution it needs; the planner never sees a source's own format."""
    name: str
    licence: str
    attribution: str

    def places(self, destination: Destination) -> list[PlaceRecord]: ...


# ---- the checked London moment cards ------------------------------------------------------------------------------

CARDS_LICENCE = "ODYS's own cards; photos credited per card (design/photo-credits.md)"


def from_card(m: Moment, destination: str = "london") -> PlaceRecord:
    """A moment card as a place record. The card keeps its id, prefixed `odys:`. What the card was checked against
    stays with it (the source and date in `opening_hours`, `last_checked`); what a card doesn't say is unknown."""
    checked = m.last_checked
    hours = m.best_time.hours or m.best_time.opening_hours
    price = (Fact(Price(float(m.cost_gbp), "GBP", "free" if not m.cost_gbp else m.price_kind()), "checked",
                  f"odys:{m.id}", checked) if m.cost_gbp is not None else Fact.unknown())
    step_free = ({True: "yes", False: "no"}.get(m.approach.step_free))
    return PlaceRecord(
        id=f"odys:{m.id}", provider="odys", name=m.place.name, destination=destination,
        point=m.start(), category=Fact.unknown(),   # the cards have no category yet (product-direction.md, debt)
        opening_hours=Fact(hours, "checked", f"odys:{m.id}", checked) if hours else Fact.unknown(),
        price=price,
        step_free=Fact(step_free, "checked", f"odys:{m.id}", checked) if step_free else Fact.unknown(),
        licence=CARDS_LICENCE, attribution="",
        same_as=(f"overture:{m.place.overture_id}",) if m.place.overture_id else ())


# ---- OpenStreetMap (an Overpass API element), not called from anywhere yet ----------------------------------------

OSM_LICENCE = "ODbL 1.0 (https://www.openstreetmap.org/copyright)"
OSM_ATTRIBUTION = "© OpenStreetMap contributors"
_OSM_CATEGORY_KEYS = ("tourism", "amenity", "leisure", "historic", "shop")
_OSM_ACCESS = {"yes": "yes", "limited": "limited", "no": "no", "designated": "yes"}
_OSM_DIET = {"yes": "yes", "only": "only", "no": "no", "limited": "limited"}


def from_osm_element(el: dict, destination: str, fetched: str) -> PlaceRecord:
    """An Overpass API JSON element (`{"type": "node", "id": 1, "lat": …, "lon": …, "tags": {…}}`) as a place record.
    Every tag is a community **claim**, never "checked": `diet:halal=yes` says a mapper tagged it, not that anyone
    certified it, so it can never be shown as certified (decisions/food-preferences-and-privacy.md). A missing tag is
    unknown, not "no"."""
    tags = el.get("tags") or {}
    osm_id = f"osm:{el.get('type', 'node')}/{el['id']}"
    src = lambda key: f"{osm_id} ({key})"
    claim = lambda v, key: Fact(v, "claimed", src(key), fetched) if v is not None else Fact.unknown()
    centre = el.get("center") or el
    point = Point(lat=centre["lat"], lon=centre["lon"]) if "lat" in centre and "lon" in centre else None
    cat_key = next((k for k in _OSM_CATEGORY_KEYS if k in tags), None)
    diet = {k.split(":", 1)[1]: claim(_OSM_DIET.get(v), k) for k, v in tags.items()
            if k.startswith("diet:") and _OSM_DIET.get(v)}
    same_as = (f"wikidata:{tags['wikidata']}",) if tags.get("wikidata") else ()
    return PlaceRecord(
        id=osm_id, provider="osm", name=tags.get("name") or "", destination=destination, point=point,
        category=claim(f"{cat_key}={tags[cat_key]}" if cat_key else None, cat_key or "category"),
        opening_hours=claim(tags.get("opening_hours"), "opening_hours"),
        price=(Fact(Price(0.0, "", "free"), "claimed", src("fee"), fetched) if tags.get("fee") == "no" else
               Fact.unknown()),   # fee=yes or charge=… gives no comparable price: unknown, not a guess
        step_free=claim(_OSM_ACCESS.get(tags.get("wheelchair", "")), "wheelchair"),
        diet=diet, website=claim(tags.get("website") or tags.get("contact:website"), "website"),
        licence=OSM_LICENCE, attribution=OSM_ATTRIBUTION, same_as=same_as)
