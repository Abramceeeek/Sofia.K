"""Travel times between moments.

v0 default: a straight-line walking estimate. Area 4's plan replaces it with precomputed
matrices (OSRM or openrouteservice for walking, the TfL Journey Planner for transit), which
plug in through `MatrixTravelTimes`. Travel runs from one moment's end point to the next
moment's approach start, so the matrix is asymmetric (D9).
"""

from __future__ import annotations

import math
from typing import Protocol

from .moments import Point

EARTH_RADIUS_M = 6_371_000.0


class TravelTimes(Protocol):
    def minutes(self, a: Point, b: Point) -> float: ...


def haversine_m(a: Point, b: Point) -> float:
    p1, p2 = math.radians(a.lat), math.radians(b.lat)
    dp, dl = p2 - p1, math.radians(b.lon - a.lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(h))


class WalkingEstimate:
    """Straight-line distance × a detour factor at walking pace. A placeholder, not a router."""

    def __init__(self, speed_kmh: float = 4.8, detour: float = 1.3):
        self.speed_m_per_min = speed_kmh * 1000.0 / 60.0
        self.detour = detour

    def minutes(self, a: Point, b: Point) -> float:
        return haversine_m(a, b) * self.detour / self.speed_m_per_min


class LondonEstimate:
    """Walk if it's short, otherwise a rough Tube/bus estimate. Every parameter is a GUESS.

    A stop-gap for Test B plans until the precomputed TfL and walking matrices exist (Area 4).
    Abram checks every leg over `walk_max_min` by hand before a plan is sent.
    """

    def __init__(self, walk_max_min: float = 20.0, access_min: float = 10.0, egress_min: float = 5.0,
                 transit_kmh: float = 18.0, walking: WalkingEstimate | None = None):
        self.walk_max_min, self.access_min, self.egress_min = walk_max_min, access_min, egress_min
        self.transit_m_per_min = transit_kmh * 1000.0 / 60.0
        self.walking = walking or WalkingEstimate()

    def mode(self, a: Point, b: Point) -> str:
        return "walk" if self.walking.minutes(a, b) <= self.walk_max_min else "transit"

    def minutes(self, a: Point, b: Point) -> float:
        walk = self.walking.minutes(a, b)
        if walk <= self.walk_max_min:
            return walk
        transit = self.access_min + haversine_m(a, b) * 1.3 / self.transit_m_per_min + self.egress_min
        return min(walk, transit)


class MatrixTravelTimes:
    """Precomputed minutes keyed by (from_key, to_key), falling back to another estimate."""

    def __init__(self, table: dict[tuple[str, str], float], key, fallback: TravelTimes | None = None):
        self.table, self.key, self.fallback = table, key, fallback or WalkingEstimate()

    def minutes(self, a: Point, b: Point) -> float:
        v = self.table.get((self.key(a), self.key(b)))
        return v if v is not None else self.fallback.minutes(a, b)
