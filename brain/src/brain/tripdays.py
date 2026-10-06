"""D122: the shape of each day of a trip, before and after the planner fills it.

Abram's comment on the screens page (6 Oct): the days run at the hours the person sets, with as many places as they
want; the first day starts where they land ("Heathrow → your stay", or one place on the way if they travel light
and land early); the last day ends with the way back to the airport, station or car. The planner still fills each
day; this module only sets its start, end and number of stops, and the journeys around it ("legs").

Journey times are estimates (`brain/data/arrivals.yaml`: published rail times plus GUESSED allowances, and the
straight-line London estimate in `travel.py`). The app's Directions button opens Apple Maps on the real route.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .dayplan import spans_lunch
from .moments import Point
from .travel import LondonEstimate, haversine_m

MIN_PER_STOP = 75   # GUESS: a stop and the journey to it, to cap the stops a short window can hold
ON_THE_WAY_SLACK_M = 2500   # GUESS: "on the way" = a detour of at most 2.5 km between the station and the stay
LATEST_START = 22 * 60


def mins(t: str) -> int:
    return int(t[:2]) * 60 + int(t[3:5])


def hhmm(m: float) -> str:
    m = int(max(0, min(m, 24 * 60 - 1)))
    return f"{m // 60:02d}:{m % 60:02d}"


def up5(m: float) -> int:
    return int(-(-m // 5) * 5)


def down5(m: float) -> int:
    return int(m // 5 * 5)


@dataclass(frozen=True)
class Place:
    key: str
    name: str
    maps_name: str
    lat: float
    lon: float

    @property
    def point(self) -> Point:
        return Point(lat=self.lat, lon=self.lon)


@dataclass(frozen=True)
class AirportLink:
    place: Place
    hub: Place
    rail_min: int
    link: str                  # "Gatwick Express"


@dataclass(frozen=True)
class Arrivals:
    exit_after_flight_min: int
    airport_before_flight_min: int
    station_before_train_min: int
    exit_after_train_min: int
    check_in_min: int
    check_in_time: str
    back_for_bags_min: int
    airports: dict[str, AirportLink]
    stations: dict[str, Place]


def load_arrivals(path: Path) -> dict[str, Arrivals]:
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    out = {}
    for dest, x in d.items():
        airports = {code: AirportLink(
            place=Place(code, a["name"], a["maps_name"], a["point"]["lat"], a["point"]["lon"]),
            hub=Place(code + ":hub", a["hub"]["name"], a["hub"]["name"], a["hub"]["lat"], a["hub"]["lon"]),
            rail_min=int(a["rail_min"]), link=a["link"]) for code, a in x["airports"].items()}
        stations = {code: Place(code, s["name"], s["maps_name"], s["lat"], s["lon"])
                    for code, s in x["stations"].items()}
        out[dest] = Arrivals(airports=airports, stations=stations,
                             **{k: x[k] for k in ("exit_after_flight_min", "airport_before_flight_min",
                                                  "station_before_train_min", "exit_after_train_min",
                                                  "check_in_min", "check_in_time", "back_for_bags_min")})
    return out


GENERIC_AIRPORT_MIN = 60   # GUESS: an airport we have no rail link for (or none named), to central London
GENERIC_STATION_MIN = 30   # GUESS: a station we don't know


@dataclass
class End:
    """How the trip starts or ends: by flight, train or car, where, and at what time (local)."""
    mode: str                  # flight | train | car
    place: str | None
    time: str


@dataclass
class Spot:
    """One end of a leg, as the app sends it to Apple Maps: a name (an address Maps can find) and maybe a point."""
    name: str
    maps: str | None = None    # what to search for in Maps; None means "from where you are"
    lat: float | None = None
    lon: float | None = None

    def out(self) -> dict:
        return {"name": self.name, "maps": self.maps, "lat": self.lat, "lon": self.lon}


@dataclass
class Leg:
    slot: str                  # arrive | to_stay | back | leave
    title: str
    origin: Spot | None
    destination: Spot | None
    mode: str                  # transit | driving | walking (Apple Maps)
    depart: str | None = None
    arrive: str | None = None
    minutes: int | None = None
    how: str | None = None
    note: str | None = None

    def out(self) -> dict:
        return {"slot": self.slot, "title": self.title, "depart": self.depart, "arrive": self.arrive,
                "minutes": self.minutes, "how": self.how, "note": self.note, "mode": self.mode,
                "origin": self.origin.out() if self.origin else None,
                "destination": self.destination.out() if self.destination else None}


@dataclass
class Part:
    """A stretch of the day for the planner: start where, when, until when, with how many stops."""
    start: Point
    start_name: str
    start_time: str
    end_time: str
    stops: int                 # including lunch, when the stretch spans midday
    lunch: bool = True
    toward: Point | None = None   # the place on the way: only places between `start` and here


@dataclass
class Frame:
    kind: str                  # one | arrive | full | leave
    main: Part | None          # the day's plan, from the stay
    before: Part | None = None # travelling light and early: one place on the way from the airport or station
    legs: list[Leg] = field(default_factory=list)       # the journeys before the plan (arrive)
    leave_at: int | None = None                         # minutes: when to leave the stay on the last day
    leave_leg: Leg | None = None
    title: str = ""            # when nothing can be planned


def on_the_way(p: Point, a: Point, b: Point, slack_m: float = ON_THE_WAY_SLACK_M) -> bool:
    """Whether p lies on the way from a to b: going via p adds at most `slack_m` (an ellipse around the line)."""
    return haversine_m(a, p) + haversine_m(p, b) <= haversine_m(a, b) + slack_m


def stops_for(start: int, end: int, wanted: int) -> int:
    """Stops for a stretch: the places the person wants (as many as fit), plus lunch if it spans midday (D102).
    Lunch isn't one of the person's "places a day"."""
    places = max(0, min(wanted, (end - start) // MIN_PER_STOP))
    return places + (1 if places and spans_lunch(start, end) else 0)


def frame_day(i: int, total: int, cfg: Arrivals | None, est: LondonEstimate, *, stay: Point, stay_name: str,
              stay_chosen: bool, day_start: str, day_end: str, stops: int, arrive: End | None, leave: End | None,
              travel_light: bool) -> Frame:
    """The day's frame: where the plan starts and when, when it ends, how many stops, and the journeys around it."""
    first, last = i == 0, i == total - 1
    kind = "one" if total == 1 else "arrive" if first else "leave" if last else "full"
    start, end = mins(day_start), mins(day_end)
    you = Spot(stay_name if stay_chosen else f"{stay_name} (no stay chosen yet)", f"{stay.lat},{stay.lon}",
               stay.lat, stay.lon)
    frame = Frame(kind=kind, main=None)
    plan_start = start

    if first and arrive:
        t = mins(arrive.time)
        if arrive.mode == "car":
            frame.legs.append(Leg("arrive", "Drive to your stay", None, you, "driving", arrive=hhmm(t),
                                  note="Arriving by car at the time you gave."))
            plan_start = max(start, t + (cfg.check_in_min if cfg else 20))
        else:
            light_from: Place | None = None
            at_hub = t
            if arrive.mode == "flight":
                ap = cfg.airports.get(arrive.place or "") if cfg else None
                out = t + (cfg.exit_after_flight_min if cfg else 60)
                if ap:
                    at_hub = out + ap.rail_min
                    to_stay = round(est.minutes(ap.hub.point, stay))
                    light_from = ap.hub
                    origin = Spot(ap.place.name, ap.place.maps_name)
                    how = f"{ap.link} to {ap.hub.name} ({ap.rail_min} min), then about {to_stay} min to your stay"
                    total_min = ap.rail_min + to_stay
                else:
                    at_hub = out + GENERIC_AIRPORT_MIN
                    origin = Spot("the airport", None)
                    how, total_min = None, GENERIC_AIRPORT_MIN
                note = "We've allowed an hour from landing for passport control and bags: a guess, queues vary."
                where = origin.name
            else:   # train
                st = cfg.stations.get(arrive.place or "") if cfg else None
                out = t + (cfg.exit_after_train_min if cfg else 10)
                if st:
                    at_hub = out
                    light_from = st
                    total_min = round(est.minutes(st.point, stay))
                    origin = Spot(st.name, st.maps_name, st.lat, st.lon)
                else:
                    total_min = GENERIC_STATION_MIN
                    origin = Spot("the station", None)
                how, note, where = None, None, origin.name
            check_in = mins(cfg.check_in_time) if cfg else 15 * 60
            if travel_light and stay_chosen and light_from and at_hub < check_in and at_hub + 60 <= end:
                # no bags to drop: start from the station, one place, then the stay (D122)
                if arrive.mode == "flight":
                    frame.legs.append(Leg("arrive", f"{where} → {light_from.name}", origin,
                                          Spot(light_from.name, light_from.maps_name, light_from.lat, light_from.lon),
                                          "transit", depart=hhmm(out), arrive=hhmm(at_hub), minutes=at_hub - out,
                                          how=f"{ap.link} ({ap.rail_min} min)", note=note))
                b0 = up5(max(at_hub, start))
                frame.before = Part(light_from.point, light_from.name, hhmm(b0), hhmm(min(b0 + 180, end)), 1,
                                    lunch=False, toward=stay)
            else:
                arrive_at = out + total_min
                frame.legs.append(Leg("arrive", f"{where} → your stay", origin, you, "transit", depart=hhmm(out),
                                      arrive=hhmm(arrive_at), minutes=arrive_at - out, how=how, note=note))
                plan_start = max(start, arrive_at + (cfg.check_in_min if cfg else 20))

    plan_end = end
    if last and leave:
        L = mins(leave.time)
        if leave.mode == "car":
            frame.leave_at = L
            frame.leave_leg = Leg("leave", f"Leave by car at {hhmm(L)}", you, None, "driving", depart=hhmm(L))
        else:
            if leave.mode == "flight":
                ap = cfg.airports.get(leave.place or "") if cfg else None
                before = cfg.airport_before_flight_min if cfg else 120
                if ap:
                    to_ap = round(est.minutes(stay, ap.hub.point)) + ap.rail_min
                    dest = Spot(ap.place.name, ap.place.maps_name)
                    how = f"About {to_ap - ap.rail_min} min to {ap.hub.name}, then the {ap.link} ({ap.rail_min} min)"
                else:
                    to_ap, dest, how = GENERIC_AIRPORT_MIN, Spot("the airport", None), None
                note = f"At the airport {before // 60} hours before your {hhmm(L)} flight: check your airline's advice."
            else:
                st = cfg.stations.get(leave.place or "") if cfg else None
                before = cfg.station_before_train_min if cfg else 20
                if st:
                    to_ap, dest = round(est.minutes(stay, st.point)), Spot(st.name, st.maps_name, st.lat, st.lon)
                else:
                    to_ap, dest = GENERIC_STATION_MIN, Spot("the station", None)
                how = None
                note = f"At the station {before} min before your {hhmm(L)} train."
            leave_at = down5(L - before - to_ap)
            frame.leave_at = leave_at
            frame.leave_leg = Leg("leave", f"Leave for {dest.name} by {hhmm(leave_at)}", you, dest, "transit",
                                  depart=hhmm(leave_at), arrive=hhmm(leave_at + to_ap), minutes=to_ap, how=how,
                                  note=note)
        plan_end = min(end, frame.leave_at - (cfg.back_for_bags_min if cfg else 30))

    plan_start = up5(plan_start)
    n = stops_for(plan_start, plan_end, stops - (1 if frame.before else 0))
    if plan_start <= LATEST_START and n > 0:
        frame.main = Part(stay, stay_name, hhmm(plan_start), hhmm(plan_end), n)
    if frame.main is None and frame.before is None:
        frame.title = {"arrive": "Arrive and settle in", "leave": "Travel day: an easy trip home"}.get(
            kind, "A free day: no time left for a place")
    return frame


def to_stay_leg(est: LondonEstimate, last_stop: dict, stay: Point, stay_name: str, check_in_min: int) -> Leg:
    """After the place on the way: from it to the stay, to check in."""
    pin = last_stop.get("pin") or {}
    p = Point(lat=pin.get("lat", stay.lat), lon=pin.get("lon", stay.lon))
    m = round(est.minutes(p, stay))
    dep = mins(last_stop["depart"])
    return Leg("to_stay", "To your stay: check in", Spot(last_stop["title"], f"{p.lat},{p.lon}", p.lat, p.lon),
               Spot(stay_name, f"{stay.lat},{stay.lon}", stay.lat, stay.lon), est.mode(p, stay).replace(
                   "walk", "walking"), depart=hhmm(dep), arrive=hhmm(dep + m), minutes=m,
               note=f"About {check_in_min} min to check in and leave your things.")


def back_leg(est: LondonEstimate, last_stop: dict, stay: Point, stay_name: str) -> Leg:
    """The last day: from the last place back to the stay for the bags."""
    pin = last_stop.get("pin") or {}
    p = Point(lat=pin.get("lat", stay.lat), lon=pin.get("lon", stay.lon))
    m = round(est.minutes(p, stay))
    dep = mins(last_stop["depart"])
    return Leg("back", "Back to your stay for your bags", Spot(last_stop["title"], f"{p.lat},{p.lon}", p.lat, p.lon),
               Spot(stay_name, f"{stay.lat},{stay.lon}", stay.lat, stay.lon), est.mode(p, stay).replace(
                   "walk", "walking"), depart=hhmm(dep), arrive=hhmm(dep + m), minutes=m)
