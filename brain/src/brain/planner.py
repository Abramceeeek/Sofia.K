"""The day planner: an orienteering problem with time windows in OR-Tools (Area 4).

Each candidate moment is an optional stop. Its prize is its predicted utility for this person
above a floor (by default the 2|3 rating threshold, so a stop enters the plan only if it is
predicted to feel at least "fine"). Transfers cost utility through the person's own transfer
weights, with the thresholds from `features.leg_features`. The solver chooses and orders stops.
It never writes text: the LLM explanation comes later, from the structured `why` of each stop.

Peak-end (D8, D15) is a toggle, off by default: when on, the planner solves once per candidate
final stop and adds an end bonus for how good the last stop is, then keeps the best plan.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from .features import leg_features
from .moments import Point
from .travel import TravelTimes

SCALE = 1000  # utility units → integer solver cost; travel adds 1 per minute as a tie-breaker


@dataclass(frozen=True)
class Candidate:
    moment_id: str
    start: Point
    end: Point
    duration_min: int
    windows: tuple[tuple[int, int], ...]   # the visit must fit inside one window (minutes from midnight)
    utility: float                          # moment-level score for this person and these conditions


@dataclass(frozen=True)
class LegWeights:
    transfer_15_30: float
    transfer_30_plus: float
    packed_pace: float = 0.0   # plan-level: 5 stops vs 3, spread as β/2 per stop

    def penalty(self, travel_min: float) -> float:
        h = leg_features(travel_min)
        return max(0.0, -(self.transfer_15_30 * h["transfer_15_30"] + self.transfer_30_plus * h["transfer_30_plus"]))


@dataclass(frozen=True)
class PlannedStop:
    moment_id: str
    arrive_min: int
    depart_min: int
    travel_min: int
    utility: float
    leg_penalty: float


@dataclass
class DayPlan:
    stops: list[PlannedStop]
    value: float                      # Σ(utility − floor) − Σ leg penalties (+ end bonus if on)
    peak_moment_id: str | None
    end_bonus_applied: bool
    dropped: list[str] = field(default_factory=list)
    status: str = "ok"


def hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def parse_hhmm(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def _start_ranges(c: Candidate, day_start: int, day_end: int) -> list[tuple[int, int]]:
    """Allowed service-start times: inside a window and inside the day, with room to finish."""
    out = []
    for lo, hi in c.windows:
        lo2, hi2 = max(lo, day_start), min(hi, day_end) - c.duration_min
        if lo2 <= hi2:
            out.append((lo2, hi2))
    return out


def _solve(cands: list[Candidate], start_point: Point, day_start: int, day_end: int,
           travel: TravelTimes, legs: LegWeights, floor: float, max_stops: int,
           forced_last: int | None, time_limit_s: float, max_wait_min: int) -> DayPlan | None:
    n = len(cands)
    START, END = 0, n + 1
    ranges = [_start_ranges(c, day_start, day_end) for c in cands]

    T = [[0] * (n + 2) for _ in range(n + 2)]
    for j in range(1, n + 1):
        T[0][j] = math.ceil(travel.minutes(start_point, cands[j - 1].start))
        for i in range(1, n + 1):
            if i != j:
                T[i][j] = math.ceil(travel.minutes(cands[i - 1].end, cands[j - 1].start))
    service = [0] + [c.duration_min for c in cands] + [0]

    manager = pywrapcp.RoutingIndexManager(n + 2, 1, [START], [END])
    routing = pywrapcp.RoutingModel(manager)

    def time_cb(fi, ti):
        i, j = manager.IndexToNode(fi), manager.IndexToNode(ti)
        return service[i] + (0 if j == END else T[i][j])

    time_idx = routing.RegisterTransitCallback(time_cb)
    routing.AddDimension(time_idx, max_wait_min, day_end, False, "Time")
    tdim = routing.GetDimensionOrDie("Time")
    tdim.CumulVar(routing.Start(0)).SetRange(day_start, min(day_start + max_wait_min, day_end))
    tdim.CumulVar(routing.End(0)).SetRange(day_start, day_end)

    def cost_cb(fi, ti):
        i, j = manager.IndexToNode(fi), manager.IndexToNode(ti)
        if j == END:
            return 0
        t = T[i][j]
        return int(round(SCALE * legs.penalty(t))) + t

    routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(cost_cb))

    count_idx = routing.RegisterUnaryTransitCallback(
        lambda fi: 1 if 1 <= manager.IndexToNode(fi) <= n else 0)
    routing.AddDimension(count_idx, 0, max_stops, True, "Stops")

    pace_bonus = legs.packed_pace / 2.0
    for j in range(1, n + 1):
        idx = manager.NodeToIndex(j)
        r = ranges[j - 1]
        cv = tdim.CumulVar(idx)
        cv.SetRange(r[0][0], r[-1][1])
        for (_, hi_prev), (lo_next, _) in zip(r, r[1:]):
            if hi_prev + 1 <= lo_next - 1:
                cv.RemoveInterval(hi_prev + 1, lo_next - 1)
        if j == forced_last:
            routing.solver().Add(routing.NextVar(idx) == routing.End(0))
            continue  # mandatory: no disjunction
        prize = cands[j - 1].utility - floor + pace_bonus
        routing.AddDisjunction([idx], int(round(SCALE * max(0.0, prize))))

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.FromMilliseconds(int(time_limit_s * 1000))
    sol = routing.SolveWithParameters(params)
    if sol is None:
        return None

    stops: list[PlannedStop] = []
    index, prev = routing.Start(0), START
    while not routing.IsEnd(index):
        index = sol.Value(routing.NextVar(index))
        node = manager.IndexToNode(index)
        if 1 <= node <= n:
            c = cands[node - 1]
            arrive = sol.Min(tdim.CumulVar(index))
            pen = legs.penalty(T[prev][node])
            stops.append(PlannedStop(c.moment_id, arrive, arrive + c.duration_min, T[prev][node],
                                     round(c.utility, 3), round(pen, 3)))
            prev = node
    visited = {s.moment_id for s in stops}
    value = sum(s.utility - floor + pace_bonus - s.leg_penalty for s in stops)
    peak = max(stops, key=lambda s: s.utility).moment_id if stops else None
    return DayPlan(stops, round(value, 3), peak, False,
                   dropped=[c.moment_id for c in cands if c.moment_id not in visited])


def plan_day(cands: list[Candidate], start_point: Point, day_start: int, day_end: int,
             travel: TravelTimes, legs: LegWeights, *, floor: float = -0.75, max_stops: int = 5,
             peak_end: bool = False, end_bonus: float = 0.5, n_end_candidates: int = 5,
             time_limit_s: float = 1.0, max_wait_min: int = 60) -> DayPlan:
    """Choose and order the stops for one day. Candidates below the floor or with no feasible
    time window are left out before solving."""
    usable = [c for c in cands if c.utility > floor and _start_ranges(c, day_start, day_end)]
    skipped = [c.moment_id for c in cands if c not in usable]
    if not usable:
        return DayPlan([], 0.0, None, False, dropped=skipped, status="no feasible moments")

    args = dict(start_point=start_point, day_start=day_start, day_end=day_end, travel=travel,
                legs=legs, floor=floor, max_stops=max_stops, time_limit_s=time_limit_s,
                max_wait_min=max_wait_min)
    best = _solve(usable, forced_last=None, **args)
    if peak_end:
        def with_bonus(p: DayPlan | None) -> float:
            if p is None or not p.stops:
                return -math.inf
            return p.value + end_bonus * (p.stops[-1].utility - floor)

        top = sorted(range(len(usable)), key=lambda k: usable[k].utility, reverse=True)[:n_end_candidates]
        best_score = with_bonus(best)
        for k in top:
            p = _solve(usable, forced_last=k + 1, **args)
            if with_bonus(p) > best_score:
                best, best_score = p, with_bonus(p)
        if best is not None and best.stops:
            best.value = round(best_score, 3)
            best.end_bonus_applied = True
    if best is None:
        return DayPlan([], 0.0, None, peak_end, dropped=[c.moment_id for c in cands], status="no solution")
    best.dropped = sorted(set(best.dropped) | set(skipped))
    return best
