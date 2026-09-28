"""The day planner: an orienteering problem with time windows in OR-Tools (Area 4).

Each candidate moment is an optional stop. Its prize is its predicted utility for this person
above a floor (by default the 2|3 rating threshold, so a stop enters the plan only if it is
predicted to feel at least "fine"). Transfers cost utility through the person's own transfer
weights, with the thresholds from `features.leg_features`. The solver chooses and orders stops.
It never writes text: the LLM explanation comes later, from the structured `why` of each stop.

Peak-end (D8, D15) is a toggle, off by default: when on, the planner solves once per candidate
final stop and adds an end bonus for how good the last stop is, then keeps the best plan.

Two rules for the seed moments (D72):
- variants of one moment (the same boat ride by day and by night) share a `group`, and a plan
  holds at most one of them;
- "area vibe" entries (a Soho wander, outdoor dining streets) are capped at `max_areas` per day
  (default 1) and are never reported as the day's peak, because they fill a day rather than make it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from .features import leg_features
from .moments import Moment, Point
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
    cost_gbp: float = 0.0                   # per person, for the budget constraint
    group: str | None = None                # variants of one moment: at most one per plan
    kind: str = "moment"                    # "moment" or "area" (area vibe)
    lunch: bool = False                     # D102: a meal stop; a plan holds at most one, and `lunch_bonus` pulls one in


def candidate_for(m: Moment, utility: float) -> Candidate:
    """The planner's view of a plannable moment."""
    return Candidate(m.id, m.start(), m.end(), int(round(m.duration_min())), tuple(m.windows()),
                     float(utility), float(m.cost_gbp or 0.0), m.variant_of, m.kind)


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


def fits_day(c: Candidate, day_start: int, day_end: int) -> bool:
    """Whether the moment can be done at all between `day_start` and `day_end` (e.g. not an evening card in a day
    that ends at 17:00)."""
    return bool(_start_ranges(c, day_start, day_end))


def _solve(cands: list[Candidate], start_point: Point, day_start: int, day_end: int,
           travel: TravelTimes, legs: LegWeights, floor: float, max_stops: int,
           forced_last: int | None, time_limit_s: float, max_wait_min: int,
           min_stops: int | None = None, budget_gbp: float | None = None,
           must_include: frozenset[str] = frozenset(), stop_bonus: float = 0.0,
           max_areas: int = 1, buffer_walk_min: int = 0, buffer_transit_min: int = 0,
           lunch_bonus: float = 0.0) -> DayPlan | None:
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
    # D100: a small buffer between two stops (more after a Tube or bus leg), so a plan is never packed to the
    # minute. It only moves arrival times; the travel minutes shown to people stay the estimate.
    mode = getattr(travel, "mode", None)
    B = [[0] * (n + 2) for _ in range(n + 2)]
    if buffer_walk_min or buffer_transit_min:
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if i != j:
                    transit = mode is not None and mode(cands[i - 1].end, cands[j - 1].start) != "walk"
                    B[i][j] = buffer_transit_min if transit else buffer_walk_min

    manager = pywrapcp.RoutingIndexManager(n + 2, 1, [START], [END])
    routing = pywrapcp.RoutingModel(manager)

    def time_cb(fi, ti):
        i, j = manager.IndexToNode(fi), manager.IndexToNode(ti)
        return service[i] + (0 if j == END else T[i][j] + B[i][j])

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
    if min_stops:
        routing.GetDimensionOrDie("Stops").CumulVar(routing.End(0)).SetMin(min(min_stops, max_stops))
    if budget_gbp is not None:
        cost_idx = routing.RegisterUnaryTransitCallback(
            lambda fi: (math.ceil(cands[manager.IndexToNode(fi) - 1].cost_gbp)
                        if 1 <= manager.IndexToNode(fi) <= n else 0))
        routing.AddDimension(cost_idx, 0, int(math.floor(budget_gbp)), True, "Budget")

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
        if cands[j - 1].moment_id in must_include:
            continue  # a must-do stop (trip intent): mandatory
        prize = cands[j - 1].utility - floor + pace_bonus + stop_bonus + (lunch_bonus if cands[j - 1].lunch else 0.0)
        routing.AddDisjunction([idx], int(round(SCALE * max(0.0, prize))))

    solver = routing.solver()
    groups: dict[str, list[int]] = {}
    for j, c in enumerate(cands, start=1):
        if c.group:
            groups.setdefault(c.group, []).append(manager.NodeToIndex(j))
    for members in groups.values():
        if len(members) > 1:
            solver.Add(solver.Sum([routing.ActiveVar(i) for i in members]) <= 1)
    meals = [manager.NodeToIndex(j) for j, c in enumerate(cands, start=1) if c.lunch]
    if len(meals) > 1:
        solver.Add(solver.Sum([routing.ActiveVar(i) for i in meals]) <= 1)
    areas = [manager.NodeToIndex(j) for j, c in enumerate(cands, start=1) if c.kind == "area"]
    if len(areas) > max_areas:
        solver.Add(solver.Sum([routing.ActiveVar(i) for i in areas]) <= max_areas)

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
    kind = {c.moment_id: c.kind for c in cands}
    peaks = [s for s in stops if kind[s.moment_id] != "area"] or stops
    peak = max(peaks, key=lambda s: s.utility).moment_id if peaks else None
    return DayPlan(stops, round(value, 3), peak, False,
                   dropped=[c.moment_id for c in cands if c.moment_id not in visited])


def plan_day(cands: list[Candidate], start_point: Point, day_start: int, day_end: int,
             travel: TravelTimes, legs: LegWeights, *, floor: float = -0.75, max_stops: int = 5,
             min_stops: int | None = None, budget_gbp: float | None = None,
             must_include: set[str] | frozenset[str] = frozenset(),
             peak_end: bool = False, end_bonus: float = 0.5, n_end_candidates: int = 5,
             time_limit_s: float = 1.0, max_wait_min: int = 60, max_areas: int = 1,
             buffer_walk_min: int = 0, buffer_transit_min: int = 0, lunch_bonus: float = 0.0) -> DayPlan:
    """Choose and order the stops for one day.

    Candidates below the floor or with no feasible time window are left out before solving,
    except must-do stops, which stay in if they fit a window. `min_stops` asks for at least that
    many stops (Test B: the same number as the generic plan). If it can't be met, the planner
    solves again without it and says so in `status`.
    """
    must = frozenset(must_include)
    usable = [c for c in cands if (c.utility > floor or c.moment_id in must or c.lunch)
              and _start_ranges(c, day_start, day_end)]
    skipped = [c.moment_id for c in cands if c not in usable]
    missing_must = sorted(must - {c.moment_id for c in usable})
    if not usable:
        return DayPlan([], 0.0, None, False, dropped=skipped, status="no feasible moments")

    args = dict(start_point=start_point, day_start=day_start, day_end=day_end, travel=travel,
                legs=legs, floor=floor, max_stops=max_stops, time_limit_s=time_limit_s,
                max_wait_min=max_wait_min, budget_gbp=budget_gbp, must_include=must & {c.moment_id for c in usable},
                min_stops=min_stops, max_areas=max_areas,
                buffer_walk_min=buffer_walk_min, buffer_transit_min=buffer_transit_min, lunch_bonus=lunch_bonus)
    status = "ok"
    best = _solve(usable, forced_last=None, **args)
    if best is None and min_stops:
        # The hard minimum can defeat the first-solution heuristic. Drop it and instead add a
        # growing per-stop bonus (in utility units) until the plan has enough stops.
        args["min_stops"] = None
        for bonus in (0.0, 0.5, 1.0, 2.0, 4.0):
            best = _solve(usable, forced_last=None, stop_bonus=bonus, **args)
            if best is not None and len(best.stops) >= min_stops:
                break
        if best is not None and len(best.stops) >= min_stops:
            args["stop_bonus"] = bonus
        else:
            status = f"could not fit {min_stops} stops"
    if best is None and args["must_include"]:
        args["must_include"] = frozenset()
        best = _solve(usable, forced_last=None, **args)
        status = "could not fit the must-do stop"

    if peak_end:
        def with_bonus(p: DayPlan | None) -> float:
            if p is None or not p.stops:
                return -math.inf
            return p.value + end_bonus * (p.stops[-1].utility - floor)

        top = sorted(range(len(usable)), key=lambda k: usable[k].utility, reverse=True)[:n_end_candidates]
        best_score = with_bonus(best)
        for k in top:
            p = _solve(usable, forced_last=k + 1, **args)
            if p is not None and min_stops and len(p.stops) < min_stops:
                continue
            if with_bonus(p) > best_score:
                best, best_score = p, with_bonus(p)
        if best is not None and best.stops:
            best.value = round(best_score, 3)
            best.end_bonus_applied = True
    if best is None:
        return DayPlan([], 0.0, None, peak_end, dropped=[c.moment_id for c in cands], status="no solution")
    best.dropped = sorted(set(best.dropped) | set(skipped))
    if missing_must:
        status = f"must-do not available that day: {', '.join(missing_must)}"
    best.status = status
    return best


def spread_to_end(plan: DayPlan, cands: dict[str, Candidate], min_end: int, day_end: int) -> bool:
    """Move the stops later, keeping their order, until the last one ends at `min_end` or later (D97).

    The extra time is shared out as longer breaks before each stop (the first break is a later start),
    and no stop is moved outside its time windows or past `day_end`. Changes `plan.stops` in place and
    returns whether the plan now ends at `min_end` or later.
    """
    if not plan.stops:
        return False
    end = plan.stops[-1].depart_min
    extra = min(min_end, day_end) - end
    if extra <= 0:
        return end >= min_end
    n = len(plan.stops)
    share = [extra // n + (1 if k < extra % n else 0) for k in range(n)]
    carry, prev_depart, new = 0, None, []
    for k, st in enumerate(plan.stops):
        c = cands[st.moment_id]
        # keep at least the solver's gap before this stop (travel plus any buffer, D100)
        gap = st.arrive_min - plan.stops[k - 1].depart_min if k else 0
        earliest = st.arrive_min if prev_depart is None else max(st.arrive_min, prev_depart + max(gap, st.travel_min))
        want = earliest + share[k] + carry
        dur = st.depart_min - st.arrive_min   # the stop's own length (extend_dwell may have lengthened it)
        latest = max((hi - dur for lo, hi in c.windows if lo <= earliest <= hi - dur), default=earliest)
        latest = min(latest, day_end - dur)
        arrive = max(earliest, min(want, latest))
        carry = want - arrive
        new.append(PlannedStop(st.moment_id, arrive, arrive + dur, st.travel_min, st.utility, st.leg_penalty))
        prev_depart = arrive + dur
    plan.stops = new
    return plan.stops[-1].depart_min >= min_end


def extend_dwell(plan: DayPlan, cands: dict[str, Candidate], targets: dict[str, int], latest_end: int) -> None:
    """D102: for a relaxed person, lengthen stays toward `targets` (total minutes at the stop), in plan order, where
    the day has room. Later stops move back by the same amount; nothing leaves its time window or ends after
    `latest_end`. Changes `plan.stops` in place."""
    stops = list(plan.stops)

    def window_end(st: PlannedStop) -> int:
        c = cands[st.moment_id]
        return max((hi for lo, hi in c.windows if lo <= st.arrive_min <= hi), default=st.depart_min)

    for k, st in enumerate(stops):
        want = targets.get(st.moment_id, 0) - (st.depart_min - st.arrive_min)
        if want <= 0:
            continue
        room = min([latest_end - stops[-1].depart_min, window_end(st) - st.depart_min]
                   + [window_end(x) - x.depart_min for x in stops[k + 1:]])
        extra = max(0, min(want, room))
        if extra:
            stops[k] = replace(st, depart_min=st.depart_min + extra)
            for j in range(k + 1, len(stops)):
                stops[j] = replace(stops[j], arrive_min=stops[j].arrive_min + extra,
                                   depart_min=stops[j].depart_min + extra)
    plan.stops = stops
