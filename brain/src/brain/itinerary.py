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
                    add(on, "arrival", nxt.destination, _arrive_note(t_out, dests),
                        *filter(None, [clock_note(t_out, dests)]), via=t_out)
                else:
                    add(d, "transfer", seg.destination, *notes, _arrive_note(t_out, dests),
                        *filter(None, [clock_note(t_out, dests)]), via=t_out)
                continue
            if first:
                add(d, "arrival", seg.destination, *([_arrive_note(t_in, dests)] if t_in else []), via=t_in)
            elif last:
                add(d, "departure", seg.destination, *([_leave_note(t_out, dests)] if t_out else []),
                    *filter(None, [clock_note(t_out, dests) if t_out else None]), via=t_out)
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


def clock_note(t: TransferSegment, dests: dict[str, Destination]) -> str | None:
    """m237: when the place you arrive in keeps a different clock from the one you left, at the moment you arrive
    (so a clock change on the day counts): "Paris is 1 hour ahead of London: your phone changes its clock"."""
    if t.from_dest == t.to_dest or t.from_dest not in dests or t.to_dest not in dests:
        return None
    _, arrive = t.instants(dests)
    there = arrive.utcoffset()
    here = arrive.astimezone(dests[t.from_dest].zone).utcoffset()
    if there == here:
        return None
    hours = (there - here).total_seconds() / 3600
    n = abs(hours)
    amount = f"{n:g} hour{'s' if n != 1 else ''}"
    return (f"{_name(t.to_dest, dests)} is {amount} {'ahead of' if hours > 0 else 'behind'} "
            f"{_name(t.from_dest, dests)}: your phone changes its clock.")


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



# ---- m237 (WS3): changing a trip that's already planned ------------------------------------------------------------

def _shift(t: TransferSegment | None, days_: int) -> TransferSegment | None:
    if t is None or days_ == 0:
        return t
    dt = timedelta(days=days_)
    return TransferSegment(t.from_dest, t.to_dest, t.mode, t.depart + dt, t.arrive + dt, t.booked)


def _with_nights(seg: DestinationSegment, arrive: date, nights: int) -> DestinationSegment:
    stay = seg.stay
    if stay is not None:
        stay = AccommodationStay(stay.name, arrive, arrive + timedelta(days=nights))
    return DestinationSegment(seg.destination, arrive, nights, stay)


def _moved(old: Trip, new: Trip, dests: dict[str, Destination]) -> list[str]:
    """What the person has to change elsewhere: booked journeys on new dates, stays on new dates."""
    notes = []
    for a, b in zip(old.transfers + tuple(x for x in (old.outbound,) if x),
                    new.transfers + tuple(x for x in (new.outbound,) if x)):
        if a.depart != b.depart and a.booked:
            notes.append(f"Your {a.mode} from {_name(a.from_dest, dests)} is booked for {a.depart:%a %-d %b}: "
                         f"it needs changing to {b.depart:%a %-d %b} with whoever sold it.")
    for a, b in zip(old.segments, new.segments):
        if a.stay and b.stay and (a.stay.checkin, a.stay.checkout) != (b.stay.checkin, b.stay.checkout):
            notes.append(f"The stay in {_name(a.destination, dests)} ({a.stay.name}) needs new dates: "
                         f"{b.stay.checkin:%a %-d %b} to {b.stay.checkout:%a %-d %b}. Check them with the stay.")
    return notes


def change_nights(trip: Trip, dests: dict[str, Destination], key: str, nights: int,
                  keep_end: bool = False) -> tuple[Trip, list[str]]:
    """One place's nights change. Either the rest of the trip moves with it (the trip ends later or earlier), or, with
    `keep_end`, the next place gives or takes the nights so the trip still ends on the same day. Returns the new trip
    and, in the person's words, what has to change elsewhere (booked journeys, stays). Nothing is changed silently."""
    i = next((k for k, s in enumerate(trip.segments) if s.destination == key), None)
    if i is None:
        raise TripError(f"{_name(key, dests)} isn't on this trip.")
    if nights < (1 if len(trip.segments) > 1 else 0):
        raise TripError(f"{_name(key, dests)} needs at least one night on a trip through several places.")
    delta = nights - trip.segments[i].nights
    segs = list(trip.segments)
    segs[i] = _with_nights(segs[i], segs[i].arrive, nights)
    transfers = list(trip.transfers)
    outbound = trip.outbound
    if keep_end:
        j = i + 1 if i + 1 < len(segs) else i - 1
        if j < 0 or j == i:
            raise TripError("There's no other place to give or take the nights, so the trip's end has to move.")
        if segs[j].nights - delta < 1:
            raise TripError(f"{_name(segs[j].destination, dests)} would have no nights left. Keep fewer nights in "
                            f"{_name(key, dests)}, or let the trip end later.")
        if j > i:
            segs[j] = _with_nights(segs[j], segs[j].arrive + timedelta(days=delta), segs[j].nights - delta)
            k = next((n for n, t in enumerate(transfers) if t.from_dest == key and t.to_dest == segs[j].destination), None)
            if k is not None:
                transfers[k] = _shift(transfers[k], delta)
        else:   # the last place changed: the place before it gives or takes, and this place's arrival moves
            segs[j] = _with_nights(segs[j], segs[j].arrive, segs[j].nights - delta)
            segs[i] = _with_nights(segs[i], segs[i].arrive - timedelta(days=delta), nights)
            k = next((n for n, t in enumerate(transfers) if t.to_dest == key), None)
            if k is not None:
                transfers[k] = _shift(transfers[k], -delta)
    else:
        for j in range(i + 1, len(segs)):
            segs[j] = _with_nights(segs[j], segs[j].arrive + timedelta(days=delta), segs[j].nights)
        later = {s.destination for s in segs[i:]}
        transfers = [_shift(t, delta) if t.from_dest in later else t for t in transfers]
        outbound = _shift(outbound, delta)
    new = Trip(trip.start, tuple(segs), tuple(transfers), trip.inbound, outbound)
    problems = validate(new, dests)
    if problems:
        raise TripError(" ".join(problems))
    notes = [f"{_name(key, dests)}: {nights} night{'s' if nights != 1 else ''}."]
    if not keep_end and delta:
        end = (new.segments[-1].arrive + timedelta(days=new.segments[-1].nights))
        notes.append(f"The trip now ends on {end:%a %-d %b}.")
    return new, notes + _moved(trip, new, dests)


def missed_transfer(trip: Trip, dests: dict[str, Destination], from_key: str, depart: datetime, arrive: datetime,
                    mode: Mode | None = None) -> tuple[Trip, list[str]]:
    """The journey out of `from_key` is missed, and the next one leaves at `depart` and arrives at `arrive` (local
    times at each end). A later one the same day changes only those times. One the next day means a night more where
    you are and a night less at the next place (the trip keeps its end); if the next place has no night to give, the
    rest of the trip moves a day. The notes say what that costs: a bed tonight, an unused night, a booking to change."""
    i = next((k for k, s in enumerate(trip.segments) if s.destination == from_key), None)
    k = next((n for n, t in enumerate(trip.transfers) if t.from_dest == from_key), None)
    if i is None or k is None or i + 1 >= len(trip.segments):
        raise TripError(f"There's no journey out of {_name(from_key, dests)} on this trip.")
    old_t = trip.transfers[k]
    new_t = TransferSegment(old_t.from_dest, old_t.to_dest, mode or old_t.mode, depart, arrive, booked=False)
    if new_t.minutes(dests) <= 0:
        raise TripError("The new journey arrives before it leaves: check the times (they're local at each end).")
    extra_here = (depart.date() - old_t.depart.date()).days
    late = (arrive.date() - old_t.arrive.date()).days
    segs, transfers = list(trip.segments), list(trip.transfers)
    transfers[k] = new_t
    here, nxt = segs[i], segs[i + 1]
    notes = []
    if extra_here:
        segs[i] = _with_nights(here, here.arrive, here.nights + extra_here)
        notes.append(f"You need a bed in {_name(from_key, dests)} tonight"
                     + (f": ask {here.stay.name} for another night, or find one." if here.stay else "."))
    outbound = trip.outbound
    if late:
        if nxt.nights - late >= 1:
            segs[i + 1] = _with_nights(nxt, nxt.arrive + timedelta(days=late), nxt.nights - late)
            if nxt.stay:
                notes.append(f"Your first night{'s' if late > 1 else ''} at {nxt.stay.name} in "
                             f"{_name(nxt.destination, dests)} won't be used: tell the stay as soon as you can.")
            else:
                notes.append(f"{_name(nxt.destination, dests)} is {late} night{'s' if late > 1 else ''} shorter.")
        else:   # no night to give: the rest of the trip moves
            for j in range(i + 1, len(segs)):
                segs[j] = _with_nights(segs[j], segs[j].arrive + timedelta(days=late), segs[j].nights)
            later = {s.destination for s in segs[i + 1:]}
            transfers = [_shift(t, late) if t.from_dest in later else t for t in transfers]
            outbound = _shift(outbound, late)
            notes.append(f"{_name(nxt.destination, dests)} had no night to give, so the rest of the trip moves "
                         f"{late} day{'s' if late > 1 else ''} later.")
    new = Trip(trip.start, tuple(segs), tuple(transfers), trip.inbound, outbound)
    problems = validate(new, dests)
    if problems:
        raise TripError(" ".join(problems))
    h, m = divmod(new_t.minutes(dests), 60)
    notes.insert(0, f"New {new_t.mode}: leave {_name(from_key, dests)} at {depart:%a %H:%M}, arrive in "
                    f"{_name(new_t.to_dest, dests)} at {arrive:%a %H:%M} (local times), after {h} h {m:02d} min.")
    if old_t.booked:
        notes.append(f"The missed {old_t.mode} was booked: ask whoever sold it about the next one.")
    return new, notes + [n for n in _moved(trip, new, dests) if "booked for" in n]


def summary(trip: Trip, dests: dict[str, Destination]) -> list[dict]:
    """The whole trip, one line a day: where you are, the day's kind, its currency and its notes, in local times."""
    return [{"date": d.day.isoformat(), "kind": d.kind, "where": _name(d.destination, dests) if d.destination else None,
             "currency": dests[d.destination].currency if d.destination in dests else None, "notes": d.notes}
            for d in days(trip, dests)]
