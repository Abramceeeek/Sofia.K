"""D120: trips: flights and places to stay, found and filtered like a flight-comparison site, booked elsewhere.

ODYS never books and never takes money (CLAUDE.md: never hold trip money). Every result carries links that open the
provider's own site with the same search. No affiliate IDs while testing: commission waits for the money gates (D120).

Where results come from:
- **flights:** Duffel's offer search (duffel.com/docs/api/v2/offer-requests, read 2026-10-06) when
  `DUFFEL_ACCESS_TOKEN` is set. A test token returns test offers only (made-up flights, some under real
  airline names: checked 7 Oct); a live token, after Duffel's account checks, returns real fares;
- **stays:** LiteAPI's rate search (docs.liteapi.travel/reference/post_hotels-rates, read 2026-10-06) when
  `LITEAPI_KEY` is set. LiteAPI requires a "guest nationality" for its prices: we always send the fixed market `GB` and
  never ask the person (CLAUDE.md: never nationality);
- **without a key:** clearly labelled sample results, made up here, so the screens and filters can be tested. They are
  never shown as real, and a provider that fails never falls back to them.

Filtering and sorting happen here, on results kept for 15 minutes, so changing a filter doesn't search again.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
import time
from collections import deque
from dataclasses import asdict, dataclass, field, replace
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote, urlencode

import yaml

DUFFEL_URL = "https://api.duffel.com/air/offer_requests"
LITEAPI_URL = "https://api.liteapi.travel/v3.0/hotels/rates"
LITEAPI_LIMIT = 250   # hotels asked for per search (7 Oct: 150 missed most budget chains; 400 took 13-16 s)
CACHE_SECONDS = 15 * 60
LITEAPI_MARKET = "GB"        # LiteAPI's required "guestNationality": a fixed market, never the person's
SAMPLE_NOTE = "Sample results, made up for testing: not real flights or prices. The links below search for real."
SAMPLE_STAY_NOTE = "Sample results, made up for testing: not real places or prices. The links below search for real."
SANDBOX_STAY_NOTE = ("Test results from LiteAPI's sandbox: prices may not be real offers. The links below search "
                     "for real.")

Fetch = Callable[[str, dict, dict], dict]      # (url, headers, json body) -> parsed JSON


# ---- places -------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Airport:
    code: str
    city: str
    name: str
    country: str
    region: str


@dataclass(frozen=True)
class Destination:
    key: str
    name: str
    country_code: str
    airport: str
    lat: float
    lon: float
    centre_name: str
    day_plans: bool


def load_places(path: Path) -> tuple[list[Airport], dict[str, Destination]]:
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    airports = [Airport(**a) for a in d["airports"]]
    dests = {x["key"]: Destination(key=x["key"], name=x["name"], country_code=x["country_code"],
                                   airport=x["airport"], lat=x["centre"]["lat"], lon=x["centre"]["lon"],
                                   centre_name=x["centre"]["name"], day_plans=bool(x.get("day_plans")))
             for x in d["destinations"]}
    return airports, dests


def suggest(airports: list[Airport], q: str, limit: int = 8) -> list[Airport]:
    """"tash" → Tashkent; "lhr" → Heathrow. Codes first, then cities, then airport names."""
    q = q.strip().lower()
    if not q:
        return []
    def rank(a: Airport) -> int | None:
        if a.code.lower() == q:
            return 0
        if a.city.lower().startswith(q):
            return 1
        if a.name.lower().startswith(q):
            return 2
        if q in a.city.lower() or q in a.name.lower():
            return 3
        return None
    hits = [(r, i, a) for i, a in enumerate(airports) if (r := rank(a)) is not None]
    return [a for _, _, a in sorted(hits)[:limit]]


# ---- queries and results ------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class FlightQuery:
    origin: str                     # IATA airport or city code
    destination: str
    depart: date
    ret: date | None
    adults: int = 1
    children: tuple[int, ...] = ()  # ages
    cabin: str = "economy"          # economy | premium_economy | business | first

    def key(self) -> str:
        return "f:" + hashlib.sha256(json.dumps(asdict(self), default=str).encode()).hexdigest()[:24]


@dataclass(frozen=True)
class StayQuery:
    city: str
    country_code: str
    lat: float
    lon: float
    checkin: date
    checkout: date
    adults: int = 2
    children: tuple[int, ...] = ()
    rooms: int = 1

    @property
    def nights(self) -> int:
        return (self.checkout - self.checkin).days

    def key(self) -> str:
        return "s:" + hashlib.sha256(json.dumps(asdict(self), default=str).encode()).hexdigest()[:24]


@dataclass
class Leg:
    origin: str
    destination: str
    depart_at: str                  # local time at the airport, "2026-10-20T08:35"
    arrive_at: str
    duration_min: int
    stops: int
    via: list[str]                  # connecting airports
    carriers: list[str]
    flight_numbers: list[str]

    @property
    def depart_minute(self) -> int:
        t = self.depart_at[11:16]
        return int(t[:2]) * 60 + int(t[3:5]) if len(t) == 5 else 0


@dataclass
class Flight:
    id: str
    airline: str
    airline_code: str
    price: float
    currency: str
    outbound: Leg
    inbound: Leg | None
    checked_bags: int | None        # per adult; None = not known
    refundable: bool | None
    changeable: bool | None
    sample: bool = False

    @property
    def stops(self) -> int:
        return max(self.outbound.stops, self.inbound.stops if self.inbound else 0)

    @property
    def duration_min(self) -> int:
        return self.outbound.duration_min + (self.inbound.duration_min if self.inbound else 0)

    @property
    def longest_leg_min(self) -> int:
        return max(self.outbound.duration_min, self.inbound.duration_min if self.inbound else 0)


@dataclass
class Stay:
    id: str
    name: str
    kind: str                       # hotel | apartment | hostel …, as the provider says
    stars: float | None
    rating: float | None            # guests' score out of 10
    reviews: int | None
    address: str
    lat: float | None
    lon: float | None
    photo: str | None
    price_total: float
    currency: str
    nights: int
    room: str
    board: str                      # "Room only", "Breakfast included" …
    breakfast: bool
    refundable: bool | None
    distance_km: float | None = None
    sample: bool = False

    @property
    def price_night(self) -> float:
        return self.price_total / max(self.nights, 1)


# ---- Duffel (flights) ---------------------------------------------------------------------------------------------

_ISO_DUR = re.compile(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:\d+(?:\.\d+)?S)?)?$")


def iso_minutes(s: str | None) -> int | None:
    """"PT2H26M" → 146; "P1DT2H" → 1560."""
    m = _ISO_DUR.match(s or "")
    if not m or not any(m.groups()):
        return None
    d, h, mi = (int(x) if x else 0 for x in m.groups())
    return d * 1440 + h * 60 + mi


def _minutes_between(a: str, b: str) -> int:
    try:
        return int((datetime.fromisoformat(b[:19]) - datetime.fromisoformat(a[:19])).total_seconds() // 60)
    except ValueError:
        return 0


def _leg(sl: dict) -> Leg:
    segs = sl.get("segments") or []
    first, last = segs[0], segs[-1]
    carriers: list[str] = []
    for s in segs:
        name = (s.get("marketing_carrier") or {}).get("name") or (s.get("operating_carrier") or {}).get("name")
        if name and name not in carriers:
            carriers.append(name)
    numbers = [f"{(s.get('marketing_carrier') or {}).get('iata_code', '')}{s.get('marketing_carrier_flight_number', '')}"
               for s in segs]
    dur = iso_minutes(sl.get("duration"))
    if dur is None:     # local times at each end can't be subtracted across time zones, so sum the segments
        dur = sum(iso_minutes(s.get("duration")) or 0 for s in segs) or _minutes_between(first["departing_at"],
                                                                                          last["arriving_at"])
    return Leg(origin=first["origin"]["iata_code"], destination=last["destination"]["iata_code"],
               depart_at=first["departing_at"][:16], arrive_at=last["arriving_at"][:16], duration_min=dur,
               stops=len(segs) - 1, via=[s["destination"]["iata_code"] for s in segs[:-1]], carriers=carriers,
               flight_numbers=[n for n in numbers if n.strip()])


def _checked_bags(offer: dict) -> int | None:
    """Checked bags for the first passenger: on each segment's passengers, or (older shape) on the offer's."""
    for sl in offer.get("slices") or []:
        for seg in sl.get("segments") or []:
            for p in seg.get("passengers") or []:
                bags = p.get("baggages")
                if bags is not None:
                    return sum(b.get("quantity", 0) for b in bags if b.get("type") == "checked")
    for p in offer.get("passengers") or []:
        bags = p.get("baggages")
        if bags is not None:
            return sum(b.get("quantity", 0) for b in bags if b.get("type") == "checked")
    return None


def _allowed(cond: Any) -> bool | None:
    if cond is None:
        return None
    if isinstance(cond, dict):
        return bool(cond.get("allowed"))
    return bool(cond)


def parse_duffel(resp: dict) -> list[Flight]:
    data = resp.get("data") or {}
    offers = data.get("offers") or []
    out = []
    for o in offers:
        slices = o.get("slices") or []
        if not slices or not slices[0].get("segments"):
            continue
        owner = o.get("owner") or {}
        cond = o.get("conditions") or {}
        out.append(Flight(id=o.get("id", ""), airline=owner.get("name", ""), airline_code=owner.get("iata_code", ""),
                          price=float(o.get("total_amount", 0)), currency=o.get("total_currency", "GBP"),
                          outbound=_leg(slices[0]), inbound=_leg(slices[1]) if len(slices) > 1 else None,
                          checked_bags=_checked_bags(o), refundable=_allowed(cond.get("refund_before_departure")),
                          changeable=_allowed(cond.get("change_before_departure"))))
    return out


def duffel_body(q: FlightQuery) -> dict:
    slices = [{"origin": q.origin, "destination": q.destination, "departure_date": q.depart.isoformat()}]
    if q.ret:
        slices.append({"origin": q.destination, "destination": q.origin, "departure_date": q.ret.isoformat()})
    passengers = [{"type": "adult"} for _ in range(q.adults)] + [{"age": a} for a in q.children]
    return {"data": {"slices": slices, "passengers": passengers, "cabin_class": q.cabin}}


def search_duffel(q: FlightQuery, token: str, fetch: Fetch) -> list[Flight]:
    headers = {"Authorization": f"Bearer {token}", "Duffel-Version": "v2", "Accept": "application/json",
               "Content-Type": "application/json"}
    resp = fetch(DUFFEL_URL + "?return_offers=true&supplier_timeout=15000", headers, duffel_body(q))
    return parse_duffel(resp)


# ---- LiteAPI (stays) ----------------------------------------------------------------------------------------------

_BREAKFAST_BOARDS = {"BB", "HB", "FB", "AI"}   # bed and breakfast, half board, full board, all inclusive


def liteapi_body(q: StayQuery) -> dict:
    rooms = max(1, min(q.rooms, q.adults))
    occ = [{"adults": q.adults // rooms + (1 if i < q.adults % rooms else 0), "children": []} for i in range(rooms)]
    occ[0]["children"] = list(q.children)
    return {"checkin": q.checkin.isoformat(), "checkout": q.checkout.isoformat(), "currency": "GBP",
            "guestNationality": LITEAPI_MARKET, "occupancies": occ, "cityName": q.city, "countryCode": q.country_code,
            "limit": LITEAPI_LIMIT, "timeout": 8, "maxRatesPerHotel": 1, "includeHotelData": True}


def parse_liteapi(resp: dict, q: StayQuery) -> list[Stay]:
    hotels = {h.get("id"): h for h in resp.get("hotels") or []}
    out = []
    for item in resp.get("data") or []:
        best = None
        for rt in item.get("roomTypes") or []:
            amount = (rt.get("offerRetailRate") or {}).get("amount")
            rates = rt.get("rates") or []
            if amount is None and rates:
                total = (rates[0].get("retailRate") or {}).get("total") or []
                amount = total[0].get("amount") if total else None
            if amount is not None and (best is None or float(amount) < best[0]):
                best = (float(amount), rt, rates[0] if rates else {})
        if best is None:
            continue
        amount, rt, rate = best
        h = hotels.get(item.get("hotelId"), {})
        board_type = (rate.get("boardType") or "").upper()
        board = rate.get("boardName") or ("Room only" if board_type in ("RO", "") else board_type)
        tag = ((rate.get("cancellationPolicies") or {}).get("refundableTag") or "").upper()
        currency = (rt.get("offerRetailRate") or {}).get("currency") or "GBP"
        rating = h.get("rating")
        out.append(Stay(id=str(item.get("hotelId")), name=h.get("name") or "A place to stay",
                        kind=(h.get("location_type") or h.get("style") or "hotel"),
                        stars=float(h["stars"]) if h.get("stars") else None,
                        rating=float(rating) if rating not in (None, "") else None,
                        reviews=int(h["review_count"]) if h.get("review_count") else None,
                        address=h.get("address") or "", lat=h.get("latitude"), lon=h.get("longitude"),
                        photo=h.get("main_photo") or h.get("thumbnail"), price_total=amount, currency=currency,
                        nights=q.nights, room=rate.get("name") or "", board=board,
                        breakfast=board_type in _BREAKFAST_BOARDS or "breakfast" in board.lower(),
                        refundable=True if tag == "RFN" else False if tag == "NRFN" else None))
    return out


def search_liteapi(q: StayQuery, key: str, fetch: Fetch) -> list[Stay]:
    headers = {"X-API-Key": key, "Accept": "application/json", "Content-Type": "application/json"}
    return parse_liteapi(fetch(LITEAPI_URL, headers, liteapi_body(q)), q)


# ---- sample results (no key) --------------------------------------------------------------------------------------

_SAMPLE_AIRLINES = [("Sample Air", "S1"), ("Demo Airways", "D2"), ("Test Wings", "T3"), ("Example Jet", "E4")]
# rough direct flight minutes to London by region, for the made-up flights only
_REGION_MINUTES = {"uk": 75, "europe": 140, "central_asia": 400, "middle_east": 400, "africa": 480,
                   "south_asia": 570, "east_asia": 760, "north_america": 450}
_HUBS = {"uk": ["AMS"], "europe": ["AMS", "FRA", "CDG"], "central_asia": ["IST", "FRA", "GYD"],
         "middle_east": ["IST", "FRA"], "africa": ["CDG", "AMS"], "south_asia": ["DXB", "DOH"],
         "east_asia": ["DXB", "HEL", "FRA"], "north_america": ["DUB", "KEF"]}


def _rng(key: str) -> random.Random:
    return random.Random(int(hashlib.sha256(key.encode()).hexdigest()[:12], 16))


def _sample_leg(r: random.Random, origin: str, dest: str, day: date, base: int, hubs: list[str],
                depart_minute: int, stops: int, airline: tuple[str, str]) -> Leg:
    dur = int(base * (1 + 0.04 * r.random()) + stops * r.randint(70, 220))
    dep = datetime.combine(day, datetime.min.time()) + timedelta(minutes=depart_minute)
    arr = dep + timedelta(minutes=dur)       # sample times ignore time zones: they're made up
    via = r.sample(hubs, k=min(stops, len(hubs)))
    numbers = [f"{airline[1]}{r.randint(100, 999)}" for _ in range(stops + 1)]
    return Leg(origin=origin, destination=dest, depart_at=dep.strftime("%Y-%m-%dT%H:%M"),
               arrive_at=arr.strftime("%Y-%m-%dT%H:%M"), duration_min=dur, stops=stops, via=via,
               carriers=[airline[0]], flight_numbers=numbers)


def sample_flights(q: FlightQuery, airports: list[Airport]) -> list[Flight]:
    by_code = {a.code: a for a in airports}
    regions = [by_code[c].region for c in (q.origin, q.destination) if c in by_code]
    region = next((r for r in regions if r != "uk"), "uk" if regions else "europe")   # the far end sets the length
    base = _REGION_MINUTES.get(region, 180)
    hubs = _HUBS.get(region, ["AMS"])
    r = _rng(q.key())
    n = r.randint(18, 28)
    flights = []
    for i in range(n):
        airline = _SAMPLE_AIRLINES[r.randrange(len(_SAMPLE_AIRLINES))]
        direct_share = 0.75 if base < 200 else 0.35
        stops = 0 if r.random() < direct_share else (1 if r.random() < 0.8 else 2)
        out_dep = r.choice(range(6 * 60, 22 * 60, 5))
        outbound = _sample_leg(r, q.origin, q.destination, q.depart, base, hubs, out_dep, stops, airline)
        inbound = None
        if q.ret:
            in_stops = stops if r.random() < 0.7 else max(0, stops - 1)
            inbound = _sample_leg(r, q.destination, q.origin, q.ret, base, hubs, r.choice(range(6 * 60, 22 * 60, 5)),
                                  in_stops, airline)
        per_person = (40 + base * 0.55) * (1.8 if q.ret else 1) * (0.75 + 0.6 * r.random()) * (1 - 0.12 * stops)
        cabin = {"premium_economy": 1.7, "business": 3.6, "first": 6.0}.get(q.cabin, 1.0)
        people = q.adults + 0.75 * len(q.children)
        bags = 1 if r.random() < 0.55 else 0
        flights.append(Flight(id=f"sample-{i}", airline=airline[0], airline_code=airline[1],
                              price=round(per_person * cabin * people + bags * 25, 2), currency="GBP",
                              outbound=outbound, inbound=inbound, checked_bags=bags,
                              refundable=r.random() < 0.25, changeable=r.random() < 0.6, sample=True))
    return flights


_SAMPLE_AREAS = [("Covent Garden", 51.5117, -0.1240), ("South Bank", 51.5055, -0.1160), ("Bloomsbury", 51.5220, -0.1260),
                 ("Shoreditch", 51.5260, -0.0780), ("Kensington", 51.4990, -0.1930), ("Paddington", 51.5160, -0.1760),
                 ("King's Cross", 51.5310, -0.1240), ("Greenwich", 51.4810, -0.0090), ("Camden", 51.5390, -0.1430),
                 ("Canary Wharf", 51.5050, -0.0200), ("Westminster", 51.4990, -0.1340), ("Clerkenwell", 51.5240, -0.1050)]
_SAMPLE_KINDS = [("Hotel", 0.55), ("Apartment", 0.25), ("Guest house", 0.1), ("Hostel", 0.1)]


def sample_stays(q: StayQuery) -> list[Stay]:
    r = _rng(q.key())
    out = []
    for i in range(r.randint(20, 30)):
        area, lat, lon = r.choice(_SAMPLE_AREAS)
        roll, acc, kind = r.random(), 0.0, "Hotel"
        for k, w in _SAMPLE_KINDS:
            acc += w
            if roll <= acc:
                kind = k
                break
        stars = None if kind in ("Apartment", "Guest house") else float(r.choice([2, 3, 3, 4, 4, 5]))
        quality = (stars or 3.5) / 5
        night = (45 if kind == "Hostel" else 85) + 230 * quality * (0.7 + 0.6 * r.random())
        breakfast = kind == "Hotel" and r.random() < 0.4
        out.append(Stay(id=f"sample-{i}", name=f"Sample {kind.lower()} {chr(65 + i % 26)}, {area}", kind=kind.lower(),
                        stars=stars, rating=round(min(9.8, 6.0 + 3.6 * quality * (0.7 + 0.5 * r.random())), 1),
                        reviews=r.randint(12, 2400), address=f"{area}, London", lat=lat + r.uniform(-0.004, 0.004),
                        lon=lon + r.uniform(-0.006, 0.006), photo=None,
                        price_total=round(night * q.nights * max(1, q.rooms) * (1.1 if breakfast else 1), 2),
                        currency="GBP", nights=q.nights, room="Double room" if q.adults <= 2 else "Family room",
                        board="Breakfast included" if breakfast else "Room only", breakfast=breakfast,
                        refundable=r.random() < 0.6, sample=True))
    return out


# ---- filters, sorting and facets ----------------------------------------------------------------------------------

@dataclass
class FlightFilters:
    max_stops: int | None = None                 # 0 = direct only
    stops: list[int] = field(default_factory=list)       # keep these numbers of stops; 2 means "2 or more"
    out_times: list[str] = field(default_factory=list)   # night / morning / afternoon / evening, leaving
    out_depart: tuple[int, int] | None = None    # minutes after midnight, local
    in_depart: tuple[int, int] | None = None
    max_leg_min: int | None = None               # the longest journey, each way
    airlines: list[str] = field(default_factory=list)    # keep only these (names)
    max_price: float | None = None
    checked_bag: bool = False
    refundable: bool = False
    sort: str = "best"                           # best | cheapest | fastest


def _norm(values: list[float]) -> Callable[[float], float]:
    lo, hi = (min(values), max(values)) if values else (0.0, 1.0)
    return lambda v: 0.0 if hi == lo else (v - lo) / (hi - lo)


def best_scores(flights: list[Flight]) -> dict[str, float]:
    """Our own "Best": 60% price and 40% total time, each scaled across the results (lower is better). Not
    Skyscanner's formula, which isn't public; it puts cheap-but-slow and quick-but-dear behind the balanced ones."""
    p = _norm([f.price for f in flights])
    d = _norm([float(f.duration_min) for f in flights])
    return {f.id: 0.6 * p(f.price) + 0.4 * d(float(f.duration_min)) for f in flights}


def _in_window(minute: int, window: tuple[int, int] | None) -> bool:
    return window is None or window[0] <= minute <= window[1]


# The design's "Leaving" times (ODYS Trips): night 00-06, morning 06-12, afternoon 12-18, evening 18-24
TIME_BUCKETS = {"night": (0, 359), "morning": (360, 719), "afternoon": (720, 1079), "evening": (1080, 1439)}


def time_bucket(minute: int) -> str:
    return next(k for k, (lo, hi) in TIME_BUCKETS.items() if lo <= minute <= hi)


def filter_flights(flights: list[Flight], f: FlightFilters) -> list[Flight]:
    keep = [x for x in flights
            if (f.max_stops is None or x.stops <= f.max_stops)
            and (not f.stops or min(x.stops, 2) in f.stops)
            and (not f.out_times or time_bucket(x.outbound.depart_minute) in f.out_times)
            and _in_window(x.outbound.depart_minute, f.out_depart)
            and (x.inbound is None or _in_window(x.inbound.depart_minute, f.in_depart))
            and (f.max_leg_min is None or x.longest_leg_min <= f.max_leg_min)
            and (not f.airlines or x.airline in f.airlines)
            and (f.max_price is None or x.price <= f.max_price)
            and (not f.checked_bag or (x.checked_bags or 0) >= 1)
            and (not f.refundable or x.refundable is True)]
    if f.sort == "cheapest":
        return sorted(keep, key=lambda x: (x.price, x.duration_min))
    if f.sort == "fastest":
        return sorted(keep, key=lambda x: (x.duration_min, x.price))
    scores = best_scores(flights)
    return sorted(keep, key=lambda x: (scores.get(x.id, 1.0), x.price))


FLIGHT_TAGS = {"best": "Best", "cheapest": "Cheapest", "fastest": "Fastest"}


def flight_tops(flights: list[Flight], f: FlightFilters) -> tuple[dict, dict[str, list[str]]]:
    """The design's sort tabs: the top of each sort within the current filters (its price and time, shown on the tab),
    and each result's tags ("Best · Cheapest")."""
    tabs, tags = {}, {}
    for sort, label in FLIGHT_TAGS.items():
        top = filter_flights(flights, replace(f, sort=sort))
        tabs[sort] = {"price": top[0].price, "duration_min": top[0].duration_min} if top else None
        if top:
            tags.setdefault(top[0].id, []).append(label)
    return tabs, tags


def flight_facets(flights: list[Flight]) -> dict:
    """What the filter screen needs, from all results (not only the filtered ones): the cheapest price per number of
    stops and per airline, and the ranges for the sliders; plus the top of each sort, as on the tabs."""
    if not flights:
        return {"stops": [], "airlines": [], "price": None, "leg_minutes": None, "tabs": {}}
    stops = {}
    for x in flights:
        stops[x.stops] = min(stops.get(x.stops, math.inf), x.price)
    airlines: dict[str, dict] = {}
    for x in flights:
        a = airlines.setdefault(x.airline, {"name": x.airline, "code": x.airline_code, "min_price": math.inf, "count": 0})
        a["min_price"] = min(a["min_price"], x.price)
        a["count"] += 1
    tabs = {}
    for sort in ("best", "cheapest", "fastest"):
        top = filter_flights(flights, FlightFilters(sort=sort))[0]
        tabs[sort] = {"price": top.price, "duration_min": top.duration_min}
    return {"stops": [{"stops": k, "min_price": v} for k, v in sorted(stops.items())],
            "airlines": sorted(airlines.values(), key=lambda a: a["min_price"]),
            "price": [min(x.price for x in flights), max(x.price for x in flights)],
            "leg_minutes": [min(x.longest_leg_min for x in flights), max(x.longest_leg_min for x in flights)],
            "tabs": tabs}


@dataclass
class StayFilters:
    max_night: float | None = None
    min_night: float | None = None
    min_stars: float | None = None
    min_rating: float | None = None              # out of 10
    kinds: list[str] = field(default_factory=list)
    refundable: bool = False
    breakfast: bool = False
    max_km: float | None = None
    sort: str = "recommended"                    # recommended | price | rating | distance


def km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def add_distances(stays: list[Stay], lat: float, lon: float) -> list[Stay]:
    for s in stays:
        s.distance_km = round(km(lat, lon, s.lat, s.lon), 2) if s.lat is not None and s.lon is not None else None
    return stays


def recommended_scores(stays: list[Stay]) -> dict[str, float]:
    """Our own "Recommended" (higher is better): 45% guests' rating, 35% cheaper per night, 20% nearer the centre,
    each scaled across the results. A place with no rating counts as middling."""
    rating = _norm([s.rating for s in stays if s.rating is not None] or [5.0])
    price = _norm([s.price_night for s in stays])
    dist = _norm([s.distance_km for s in stays if s.distance_km is not None] or [0.0])
    return {s.id: 0.45 * (rating(s.rating) if s.rating is not None else 0.5)
                  + 0.35 * (1 - price(s.price_night))
                  + 0.2 * (1 - dist(s.distance_km) if s.distance_km is not None else 0.5) for s in stays}


def filter_stays(stays: list[Stay], f: StayFilters) -> list[Stay]:
    keep = [s for s in stays
            if (f.max_night is None or s.price_night <= f.max_night)
            and (f.min_night is None or s.price_night >= f.min_night)
            and (f.min_stars is None or (s.stars or 0) >= f.min_stars)
            and (f.min_rating is None or (s.rating or 0) >= f.min_rating)
            and (not f.kinds or s.kind in f.kinds)
            and (not f.refundable or s.refundable is True)
            and (not f.breakfast or s.breakfast)
            and (f.max_km is None or (s.distance_km is not None and s.distance_km <= f.max_km))]
    if f.sort == "price":
        return sorted(keep, key=lambda s: s.price_night)
    if f.sort == "rating":
        return sorted(keep, key=lambda s: (-(s.rating or 0), s.price_night))
    if f.sort == "distance":
        return sorted(keep, key=lambda s: (s.distance_km if s.distance_km is not None else math.inf))
    scores = recommended_scores(stays)
    return sorted(keep, key=lambda s: -scores.get(s.id, 0.0))


STAY_TAGS = {"recommended": "Best for your days", "price": "Cheapest", "rating": "Top rated"}


def stay_tops(stays: list[Stay], f: StayFilters) -> tuple[dict, dict[str, list[str]]]:
    """As flight_tops, for stays: the top of each sort within the filters, and the tags (not "Top rated" as a tag)."""
    tabs, tags = {}, {}
    for sort, label in STAY_TAGS.items():
        top = filter_stays(stays, replace(f, sort=sort))
        tabs[sort] = ({"price_night": round(top[0].price_night, 2), "rating": top[0].rating,
                       "distance_km": top[0].distance_km} if top else None)
        if top and sort != "rating":
            tags.setdefault(top[0].id, []).append(label)
    return tabs, tags


def stay_facets(stays: list[Stay]) -> dict:
    if not stays:
        return {"price_night": None, "stars": [], "kinds": [], "max_km": None}
    stars: dict[float, int] = {}
    kinds: dict[str, int] = {}
    for s in stays:
        if s.stars:
            stars[s.stars] = stars.get(s.stars, 0) + 1
        kinds[s.kind] = kinds.get(s.kind, 0) + 1
    dists = [s.distance_km for s in stays if s.distance_km is not None]
    return {"price_night": [round(min(s.price_night for s in stays), 2), round(max(s.price_night for s in stays), 2)],
            "stars": [{"stars": k, "count": v} for k, v in sorted(stars.items())],
            "kinds": [{"kind": k, "count": v} for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])],
            "max_km": round(max(dists), 1) if dists else None}


# ---- links out (book on the provider's own site; no affiliate IDs, D120) -------------------------------------------

def flight_links(q: FlightQuery) -> list[dict]:
    """Skyscanner's documented referral link (developers.skyscanner.net/docs/referrals, read 2026-10-06), without a
    partner ID; and a Google Flights search."""
    cabin = {"premium_economy": "premiumeconomy"}.get(q.cabin, q.cabin)
    sky = {"origin": q.origin, "destination": q.destination, "outboundDate": q.depart.isoformat(),
           "adultsv2": q.adults, "cabinclass": cabin, "market": "UK", "locale": "en-GB", "currency": "GBP"}
    if q.ret:
        sky["inboundDate"] = q.ret.isoformat()
    if q.children:
        sky["childrenv2"] = "|".join(str(a) for a in q.children)
    words = f"Flights from {q.origin} to {q.destination} on {q.depart.isoformat()}"
    if q.ret:
        words += f" returning {q.ret.isoformat()}"
    words += f" for {q.adults} adult{'s' if q.adults > 1 else ''}"
    return [{"name": "Skyscanner", "url": "https://www.skyscanner.net/g/referrals/v1/flights/day-view/?" + urlencode(sky)},
            {"name": "Google Flights",
             "url": "https://www.google.com/travel/flights?" + urlencode({"q": words, "hl": "en-GB", "curr": "GBP"})}]


# Budget chains that sell mostly on their own sites (Premier Inn: ~94-97% direct; Travelodge: its cheapest rates
# only direct; research/notes/21-travel-data.md). Links to their home pages: their search links aren't documented.
UK_DIRECT_CHAINS = (("Premier Inn", "https://www.premierinn.com/gb/en/home.html"),
                    ("Travelodge", "https://www.travelodge.co.uk/"))


def stay_links(q: StayQuery, stay: Stay | None = None, max_night: float | None = None) -> list[dict]:
    """Booking.com's and Airbnb's search pages with the same dates and guests; for one place, its name on Booking.com
    and a search for its own website (hotels' own sites have no shared search to link to)."""
    booking = {"ss": f"{stay.name}, {q.city}" if stay else q.city, "checkin": q.checkin.isoformat(),
               "checkout": q.checkout.isoformat(), "group_adults": q.adults, "no_rooms": max(1, q.rooms),
               "group_children": len(q.children), "selected_currency": "GBP"}
    pairs = list(booking.items()) + [("age", a) for a in q.children]
    links = [{"name": "Booking.com", "url": "https://www.booking.com/searchresults.html?" + urlencode(pairs)}]
    if stay is None:
        air = [("checkin", q.checkin.isoformat()), ("checkout", q.checkout.isoformat()), ("adults", q.adults)]
        if q.children:
            air.append(("children", len(q.children)))
        if max_night:
            air.append(("price_max", int(max_night)))
        links.append({"name": "Airbnb", "url": f"https://www.airbnb.co.uk/s/{quote(q.city)}/homes?" + urlencode(air)})
        if q.country_code == "GB":   # 7 Oct: they sell mostly on their own sites, so LiteAPI doesn't carry them
            links += [{"name": name, "url": url, "note": "Sells mostly on its own site, so it isn't in these results"}
                      for name, url in UK_DIRECT_CHAINS]
    else:
        links.append({"name": "The place's own website",
                      "url": "https://www.google.com/search?" + urlencode({"q": f"{stay.name} {q.city} official site"})})
    return links


# ---- the service: cache, rate limit, provider choice --------------------------------------------------------------

def http_fetch(url: str, headers: dict, body: dict) -> dict:
    import httpx   # only needed with a provider key
    r = httpx.post(url, headers=headers, json=body, timeout=30.0)
    r.raise_for_status()
    return r.json()


class ProviderError(Exception):
    pass


@dataclass
class TripSearch:
    """Searches once per query (kept 15 min), then filters and sorts the kept results. At most `per_hour` provider
    searches per person per hour, so a stuck filter loop can't run up Duffel's per-search charges."""
    airports: list[Airport]
    destinations: dict[str, Destination]
    duffel_token: str | None = None
    liteapi_key: str | None = None
    fetch: Fetch = http_fetch
    per_hour: int = 40
    clock: Callable[[], float] = time.monotonic
    _cache: dict[str, tuple[float, list]] = field(default_factory=dict)
    _calls: dict[str, deque] = field(default_factory=dict)

    @property
    def flight_source(self) -> str:
        if not self.duffel_token:
            return "sample"
        return "duffel_test" if self.duffel_token.startswith("duffel_test") else "duffel"

    @property
    def stay_source(self) -> str:
        if not self.liteapi_key:
            return "sample"
        # sandbox keys start "sand_" (docs.liteapi.travel/reference/authentication, read 2026-10-06)
        return "liteapi_sandbox" if self.liteapi_key.startswith("sand_") else "liteapi"

    def _allowed(self, who: str) -> bool:
        now, calls = self.clock(), self._calls.setdefault(who, deque())
        while calls and now - calls[0] > 3600:
            calls.popleft()
        if len(calls) >= self.per_hour:
            return False
        calls.append(now)
        return True

    def _cached(self, key: str, who: str, run: Callable[[], list]) -> list:
        now = self.clock()
        hit = self._cache.get(key)
        if hit and now - hit[0] < CACHE_SECONDS:
            return hit[1]
        if not self._allowed(who):
            raise ProviderError("too_many")
        results = run()
        if len(self._cache) > 300:
            for k in sorted(self._cache, key=lambda k: self._cache[k][0])[:100]:
                del self._cache[k]
        self._cache[key] = (now, results)
        return results

    def flights(self, q: FlightQuery, who: str) -> list[Flight]:
        if not self.duffel_token:
            return sample_flights(q, self.airports)
        try:
            return self._cached(q.key(), who, lambda: search_duffel(q, self.duffel_token, self.fetch))
        except ProviderError:
            raise
        except Exception as e:   # the provider failed: say so; never fall back to made-up results
            raise ProviderError("unavailable") from e

    def stays(self, q: StayQuery, who: str) -> list[Stay]:
        if not self.liteapi_key:
            found = sample_stays(q)
        else:
            try:
                found = self._cached(q.key(), who, lambda: search_liteapi(q, self.liteapi_key, self.fetch))
            except ProviderError:
                raise
            except Exception as e:
                raise ProviderError("unavailable") from e
        return add_distances(found, q.lat, q.lon)


def flight_out(f: Flight) -> dict:
    d = asdict(f)
    d.update(stops=f.stops, duration_min=f.duration_min)
    return d


def stay_out(s: Stay) -> dict:
    d = asdict(s)
    d.update(price_night=round(s.price_night, 2))
    return d
