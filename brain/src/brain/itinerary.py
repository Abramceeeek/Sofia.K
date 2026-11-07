"""WS3 (m210): a trip through several places, as segments, without a second planner
(decisions/multi-city-travel-architecture.md). Not wired into the API or the apps yet.

A trip is a list of **destination segments** (a place, its nights, its stay) joined by **transfers** (a flight, a train,
a bus, a car or a ferry, with local times at each end). Each segment becomes one request to the existing trip-days
planner (`api.trip_days`, unchanged): the transfer into it is its arrival leg, the transfer out its leaving leg, and
the moments planned in other segments are excluded. A trip with one segment and no transfers is exactly today's trip.

Times are always zone-aware: a departure is in the place it leaves from, an arrival in the place it reaches, and
durations come from the two instants, so a clock change or a time-zone border never makes a journey an hour too long
or short.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Literal

from .places import Destination

Mode = Literal["flight", "train", "bus", "car", "ferry"]
DayKind = Literal["arrival", "full", "transfer", "on_board", "departure", "gap"]


@dataclass(frozen=True)
class AccommodationStay:
    name: str
    checkin: date
    checkout: date


@dataclass(frozen=True)
class DestinationSegment:
    destination: str                # a key in the destination registry (data/destinations.yaml)
    arrive: date                    # the first day here
    nights: int                     # nights here, in a bed (not on a sleeper)
    stay: AccommodationStay | None = None


@dataclass(frozen=True)
class TransferSegment:
    """A journey between two places. Times are local wall-clock times where each end is ("09:01" in London,
    "12:20" in Paris)."""
    from_dest: str
    to_dest: str
    mode: Mode
    depart: datetime                # naive local time at the origin
    arrive: datetime                # naive local time at the destination
    booked: bool = False            # a ticket exists (a booking elsewhere); else a plan

    def instants(self, dests: dict[str, Destination]) -> tuple[datetime, datetime]:
        return (self.depart.replace(tzinfo=dests[self.from_dest].zone),
                self.arrive.replace(tzinfo=dests[self.to_dest].zone))

    def minutes(self, dests: dict[str, Destination]) -> int:
        a, b = self.instants(dests)
        return round((b - a).total_seconds() / 60)

    @property
    def overnight(self) -> bool:
        return self.arrive.date() > self.depart.date()


@dataclass(frozen=True)
class Trip:
    start: date                     # the first day
    segments: tuple[DestinationSegment, ...]
    transfers: tuple[TransferSegment, ...] = ()   # transfers[i] joins segments[i] and segments[i + 1]
    inbound: TransferSegment | None = None        # into the first place (from home)
    outbound: TransferSegment | None = None       # home from the last place


@dataclass
class TripDay:
    day: date
    index: int
    kind: DayKind
    destination: str | None         # where the person wakes up or spends the day (None on board)
    notes: list[str] = field(default_factory=list)
    journeys: list[tuple[str, str]] = field(default_factory=list)   # (from, to) of the journeys this day holds


class TripError(ValueError):
    """A trip whose dates, places or journeys don't fit together. The message says what to fix."""


def validate(trip: Trip, dests: dict[str, Destination]) -> list[str]:
    """Problems that stop a trip from being planned, in the person's words (empty: it fits together)."""
    out = []
    if not trip.segments:
        return ["A trip needs at least one place."]
    for s in trip.segments:
        if s.destination not in dests:
            out.append(f"We don't know {s.destination!r} yet.")
        if s.nights < 0:
            out.append("Nights can't be negative.")
        if s.stay and (s.stay.checkin != s.arrive or (s.stay.checkout - s.stay.checkin).days != s.nights):
            out.append(f"The stay in {_name(s.destination, dests)} doesn't match the nights there.")
    if trip.segments[0].arrive != trip.start:
        out.append("The first place should start on the trip's first day.")
    for i, (a, b) in enumerate(zip(trip.segments, trip.segments[1:])):
        t = next((t for t in trip.transfers if t.from_dest == a.destination and t.to_dest == b.destination), None)
        leave_day = a.arrive + timedelta(days=a.nights)
        on_board = 1 if t is not None and t.overnight else 0
        if b.arrive != leave_day + timedelta(days=on_board):
            want = leave_day + timedelta(days=on_board)
            out.append(f"{_name(b.destination, dests)} starts on {b.arrive:%a %-d %b}, but after "
                       f"{_name(a.destination, dests)} it would be {want:%a %-d %b}"
                       + (" (after the night on board)" if on_board else "") + ".")
        if a.nights < 1:
            out.append(f"Each place on a trip of several needs at least one night ({_name(a.destination, dests)}).")
        if t is not None and t.minutes(dests) <= 0:
            out.append(f"The journey from {_name(a.destination, dests)} arrives before it leaves: check the times "
                       "(they're local at each end).")
    return out


def _name(key: str, dests: dict[str, Destination]) -> str:
    return dests[key].name if key in dests else key


def days(trip: Trip, dests: dict[str, Destination]) -> list[TripDay]:
    """Every calendar day of the trip, with where the person is and what kind of day it is. A missing journey between
    two places is a "gap" day that says so, never an invented train."""
    problems = validate(trip, dests)
    if problems:
        raise TripError(" ".join(problems))
    out: list[TripDay] = []
    k = 0

    def add(d: date, kind: DayKind, dest: str | None, *notes: str, via: TransferSegment | None = None):
        nonlocal k
        out.append(TripDay(d, k, kind, dest, list(notes), [(via.from_dest, via.to_dest)] if via else []))
        k += 1

    for i, seg in enumerate(trip.segments):
        nxt = trip.segments[i + 1] if i + 1 < len(trip.segments) else None
        t_in = trip.inbound if i == 0 else _transfer(trip, trip.segments[i - 1].destination, seg.destination)
        t_out = _transfer(trip, seg.destination, nxt.destination) if nxt else trip.outbound
        for n in range(seg.nights + 1):
            d = seg.arrive + timedelta(days=n)
            first, last = n == 0, n == seg.nights
            if first and i > 0:
                continue   # the previous segment's leaving day already holds this date (or the night on board did)
            if last and nxt is not None:
                if t_out is None:
                    add(d, "gap", seg.destination,
                        f"How you get from {_name(seg.destination, dests)} to {_name(nxt.destination, dests)} isn't "
                        "set yet, so this day is planned only until midday.",
                        via=TransferSegment(seg.destination, nxt.destination, "train", datetime.min, datetime.min))
                    continue
                notes = [_leave_note(t_out, dests)]
                if t_out.overnight:
                    add(d, "transfer", seg.destination, *notes, "You sleep on board tonight.", via=t_out)
                    on = t_out.arrive.date()
                    add(on, "arrival", nxt.destination, _arrive_note(t_out, dests), via=t_out)
                else:
                    add(d, "transfer", seg.destination, *notes, _arrive_note(t_out, dests), via=t_out)
                continue
            if first:
                add(d, "arrival", seg.destination, *([_arrive_note(t_in, dests)] if t_in else []), via=t_in)
            elif last:
                add(d, "departure", seg.destination, *([_leave_note(t_out, dests)] if t_out else []), via=t_out)
            else:
                add(d, "full", seg.destination)
    return out


def _transfer(trip: Trip, a: str, b: str) -> TransferSegment | None:
    return next((t for t in trip.transfers if t.from_dest == a and t.to_dest == b), None)


def _leave_note(t: TransferSegment, dests: dict[str, Destination]) -> str:
    return f"Leave {_name(t.from_dest, dests)} by {t.mode} at {t.depart:%H:%M} ({_name(t.from_dest, dests)} time)."


def _arrive_note(t: TransferSegment, dests: dict[str, Destination]) -> str:
    h, m = divmod(t.minutes(dests), 60)
    return (f"Arrive in {_name(t.to_dest, dests)} at {t.arrive:%H:%M} ({_name(t.to_dest, dests)} time), "
            f"after {h} h {m:02d} min.")


def segment_requests(trip: Trip, dests: dict[str, Destination], used: dict[str, list[str]] | None = None) -> list[dict]:
    """One request per segment for the existing trip-days planner (the fields of `schemas.TripDaysIn`): the same
    planner for every place, never a second one. A place without checked coverage gets no request: its days keep
    their structure (arriving, leaving, the stay) and say plans aren't ready there yet."""
    used = used or {}
    out = []
    for i, seg in enumerate(trip.segments):
        d = dests[seg.destination]
        if d.coverage != "checked":
            continue
        t_in = trip.inbound if i == 0 else _transfer(trip, trip.segments[i - 1].destination, seg.destination)
        nxt = trip.segments[i + 1] if i + 1 < len(trip.segments) else None
        t_out = _transfer(trip, seg.destination, nxt.destination) if nxt else trip.outbound
        others = sorted({m for k, ids in used.items() if k != seg.destination for m in ids})
        out.append({
            "destination": seg.destination, "start_date": seg.arrive.isoformat(), "nights": seg.nights,
            "stay_name": seg.stay.name if seg.stay else None,
            # `schemas.TripEndIn` knows flights, trains and cars; a bus or ferry isn't modelled yet, so the day
            # starts (or ends) at the stay and says so, rather than pretending it's a train
            "arrive": _end(t_in, "arrive"), "leave": _end(t_out, "leave"),
            "exclude": others})
    return out


def _end(t: TransferSegment | None, which: str) -> dict | None:
    if t is None or t.mode not in ("flight", "train", "car"):
        return None
    return {"mode": t.mode, "time": f"{(t.arrive if which == 'arrive' else t.depart):%H:%M}"}


def affected_days(trip: Trip, dests: dict[str, Destination], changed: str) -> list[int]:
    """When one place changes (or a journey into or out of it is delayed), only its own days and the travel days at
    either end are planned again; every other day is kept."""
    return [d.index for d in days(trip, dests) if d.destination == changed
            or any(changed in pair for pair in d.journeys)]
