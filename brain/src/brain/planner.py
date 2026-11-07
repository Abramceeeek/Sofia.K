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

The person's own time (m200, product direction step 2): "Your plans 13:00-15:00" or "Free time 16:00-18:00" is a
block the plan goes around. It comes as one slot beside each place (and the start), pinned to its times; at most one
of a block's slots is in a plan, and a large bonus (`MINE_BONUS`, as lunch's) brings one in whenever the day allows,
so the block sits beside one of the day's places (wherever the travel is least). It isn't one of the day's places. (An "exactly one" rule left the
solver's first, greedy solution with nothing to aim for, and days with a block went unplanned: 6 Nov.)

One rule for the day's shape (D127, from the algorithm review, 20 Oct): at most `max_theme` (2) history-and-culture
stops a day, and never two of them in a row, so a day isn't three museums back to back (35% of simulated personal
plans had two in a row). Lunch doesn't count, and a lunch between two of them breaks the run.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from .features import leg_features, moment_features
from .moments import Moment, Point
from .travel import TravelTimes

SCALE = 1000  # utility units → integer solver cost; travel adds 1 per minute as a tie-breaker
MINE_BONUS = 50.0   # m200: the person's own time outweighs any place (lunch's bonus is 5)
FLOOR_SPARES = 3    # m206 (GUESS): when the floor is lowered to fill a day, this many more of the best cards come in


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
    theme: str | None = None                # D127: "history" for a history-and-culture stop (at most 2, never in a row)
    mine: str | None = None                 # m200: the person's own block this slot stands for (exactly one per block)


def candidate_for(m: Moment, utility: float) -> Candidate:
    """The planner's view of a plannable moment."""
    return Candidate(m.id, m.start(), m.end(), int(round(m.duration_min())), tuple(m.windows()),
                     float(utility), float(m.cost_gbp or 0.0), m.variant_of, m.kind,
                     theme="history" if moment_features(m).get("history_culture", 0) >= 1 else None)


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
    objective: int | None = None      # the solver's own cost (lower is better): compares two searches of one model


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
           lunch_bonus: float = 0.0, lunch_not_first: bool = False, max_theme: int = 2,
           max_places: int | None = None, fixed_count: bool = False,
           strategy: str = "PARALLEL_CHEAPEST_INSERTION", seeded: bool = False) -> DayPlan | None:
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
                if i != j and not (cands[i - 1].mine or cands[j - 1].mine):   # m202: the person's own time has
                    # its own allowance either side (or sits where they are), so no extra gap beside it
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

    count_idx = routing.RegisterUnaryTransitCallback(   # m200: the person's own time isn't one of the places
        lambda fi: 1 if 1 <= manager.IndexToNode(fi) <= n and not cands[manager.IndexToNode(fi) - 1].mine else 0)
    routing.AddDimension(count_idx, 0, max_stops, True, "Stops")
    if min_stops:
        routing.GetDimensionOrDie("Stops").CumulVar(routing.End(0)).SetMin(min(min_stops, max_stops))
    if max_places is not None:   # m202: lunch that can't fit is never replaced by a place the person didn't ask for
        places_idx = routing.RegisterUnaryTransitCallback(
            lambda fi: 1 if 1 <= manager.IndexToNode(fi) <= n and not cands[manager.IndexToNode(fi) - 1].mine
            and not cands[manager.IndexToNode(fi) - 1].lunch else 0)
        routing.AddDimension(places_idx, 0, max_places, True, "Places")
    if budget_gbp is not None:
        cost_idx = routing.RegisterUnaryTransitCallback(
            lambda fi: (math.ceil(cands[manager.IndexToNode(fi) - 1].cost_gbp)
                        if 1 <= manager.IndexToNode(fi) <= n else 0))
        routing.AddDimension(cost_idx, 0, int(math.floor(budget_gbp)), True, "Budget")

    pace_bonus = legs.packed_pace / 2.0
    prizes = [0.0] * (n + 2)   # what the solver gains by visiting each node (utility units), for the seed
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
        if cands[j - 1].mine:   # m200: one slot of the block, pulled in by its bonus (at most one, below)
            prizes[j] = MINE_BONUS
            routing.AddDisjunction([idx], int(round(SCALE * MINE_BONUS)))
            continue
        # m206 (WS7 benchmark): when the day's number of stops is fixed, the pace term is the same for every plan, so
        # it stays out of the prize. Added in, a dislike of packed days pushed the prizes of several places to the
        # zero clamp, and the solver then chose among them by travel time alone, not by the person's tastes.
        pace = 0.0 if fixed_count else pace_bonus
        prize = cands[j - 1].utility - floor + pace + stop_bonus + (lunch_bonus if cands[j - 1].lunch else 0.0)
        prizes[j] = max(0.0, prize)
        routing.AddDisjunction([idx], int(round(SCALE * max(0.0, prize))))

    solver = routing.solver()
    groups: dict[str, list[int]] = {}
    for j, c in enumerate(cands, start=1):
        if c.group:
            groups.setdefault(c.group, []).append(manager.NodeToIndex(j))
    for members in groups.values():
        if len(members) > 1:
            solver.Add(solver.Sum([routing.ActiveVar(i) for i in members]) <= 1)
    blocks: dict[str, list[int]] = {}
    for j, c in enumerate(cands, start=1):
        if c.mine:
            blocks.setdefault(c.mine, []).append(manager.NodeToIndex(j))
    for members in blocks.values():   # m200: the person's own time is in the plan once
        solver.Add(solver.Sum([routing.ActiveVar(i) for i in members]) <= 1)
    meals = [manager.NodeToIndex(j) for j, c in enumerate(cands, start=1) if c.lunch]
    if len(meals) > 1:
        solver.Add(solver.Sum([routing.ActiveVar(i) for i in meals]) <= 1)
    if lunch_not_first:   # journey round 2: a morning starts with a place, not lunch
        for i in meals:
            solver.Add(routing.NextVar(routing.Start(0)) != i)
    areas = [manager.NodeToIndex(j) for j, c in enumerate(cands, start=1) if c.kind == "area"]
    if len(areas) > max_areas:
        solver.Add(solver.Sum([routing.ActiveVar(i) for i in areas]) <= max_areas)
    # D127: history and culture at most `max_theme` times a day, and never straight after another (an inactive
    # stop's next is itself, so the rule only binds stops in the plan)
    themed = [manager.NodeToIndex(j) for j, c in enumerate(cands, start=1) if c.theme == "history" and not c.lunch]
    if len(themed) > max_theme:
        solver.Add(solver.Sum([routing.ActiveVar(i) for i in themed]) <= max_theme)
    for a in themed:
        for b in themed:
            if a != b:
                solver.Add(routing.NextVar(a) != b)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = getattr(routing_enums_pb2.FirstSolutionStrategy, strategy)
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.FromMilliseconds(int(time_limit_s * 1000))
    sol = None
    if seeded and forced_last is None:
        # m216 (Abram, 7 Nov): stage 1, a valid day built step by step; stage 2, the solver improves it within the
        # time limit. The search no longer depends on finding a good start itself (on a busy machine it sometimes
        # didn't), and if it can't improve the seed, the seed is the plan. An invalid seed falls back to the old way.
        route = _greedy_route(cands, T, B, service, ranges, day_start, max_wait_min, prizes, legs,
                              max_stops=max_stops, max_places=max_places, budget_gbp=budget_gbp,
                              max_areas=max_areas, max_theme=max_theme, lunch_not_first=lunch_not_first,
                              must=must_include)
        routing.CloseModelWithParameters(params)
        initial = routing.ReadAssignmentFromRoutes([[manager.NodeToIndex(j) for j in route]], True) if route else None
        if initial is not None:
            sol = routing.SolveFromAssignmentWithParameters(initial, params) or initial
    if sol is None:
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
    own = {c.moment_id for c in cands if c.mine}
    value = sum((0.0 if s.moment_id in own else s.utility - floor + pace_bonus) - s.leg_penalty for s in stops)
    kind = {c.moment_id: c.kind for c in cands}
    peaks = [s for s in stops if kind[s.moment_id] != "area" and s.moment_id not in own] or \
        [s for s in stops if s.moment_id not in own]
    peak = max(peaks, key=lambda s: s.utility).moment_id if peaks else None
    return DayPlan(stops, round(value, 3), peak, False,
                   dropped=[c.moment_id for c in cands if c.moment_id not in visited], objective=sol.ObjectiveValue())


def _greedy_route(cands: list[Candidate], T: list[list[int]], B: list[list[int]], service: list[int],
                  ranges: list[list[tuple[int, int]]], day_start: int, max_wait: int, prizes: list[float],
                  legs: LegWeights, *, max_stops: int, max_places: int | None, budget_gbp: float | None,
                  max_areas: int, max_theme: int, lunch_not_first: bool, must: frozenset[str]) -> list[int]:
    """m216, stage 1: a valid day built one stop at a time, keeping every rule the solver keeps (hours, waits, budget,
    one of a group, one lunch, one area, history at most twice and never in a row, the stop and place counts) and
    never taking a stop that would make one of the person's own blocks unreachable. Each step takes the stop worth
    most to the solver (its prize less the leg's penalty). Returns node numbers in order (1-based); may be short or
    empty, in which case the solver starts on its own as before."""
    n = len(cands)
    budget = None if budget_gbp is None else int(math.floor(budget_gbp))

    def start_at(j: int, frm: int, ready: int) -> int | None:
        arrive = ready + T[frm][j] + B[frm][j]
        for lo, hi in ranges[j - 1]:
            s = max(arrive, lo)
            if s <= hi:
                return s if s - arrive <= max_wait else None
        return None

    blocks: dict[str, list[int]] = {}
    for j, c in enumerate(cands, start=1):
        if c.mine:
            blocks.setdefault(c.mine, []).append(j)
    route, used = [], set()
    prev, ready = 0, day_start
    groups, done_blocks = set(), set()
    meals = areas = hist = spent = stops = places = 0
    last_hist = False
    while True:
        best = None
        for j in range(1, n + 1):
            c = cands[j - 1]
            if j in used or (c.group and c.group in groups) or (c.mine and c.mine in done_blocks):
                continue
            if c.lunch and (meals or (lunch_not_first and not route)):
                continue
            if c.kind == "area" and areas >= max_areas:
                continue
            themed = c.theme == "history" and not c.lunch
            if themed and (hist >= max_theme or last_hist):
                continue
            cost = math.ceil(c.cost_gbp)
            if budget is not None and spent + cost > budget:
                continue
            if not c.mine and (stops >= max_stops or (max_places is not None and not c.lunch and places >= max_places)):
                continue
            if not c.mine and prizes[j] <= 0 and c.moment_id not in must:
                continue
            s = start_at(j, prev, ready)
            if s is None:
                continue
            end = s + service[j]
            if any(k != c.mine and k not in done_blocks and not any(start_at(x, j, end) is not None for x in slots)
                   for k, slots in blocks.items()):
                continue   # it would leave one of the person's own blocks out of reach
            score = SCALE * (prizes[j] - legs.penalty(T[prev][j])) - T[prev][j]
            if best is None or score > best[0]:
                best = (score, j, end, themed, cost)
        if best is None:
            return route
        _, j, end, themed, cost = best
        c = cands[j - 1]
        route.append(j)
        used.add(j)
        prev, ready = j, end
        if c.group:
            groups.add(c.group)
        if c.mine:
            done_blocks.add(c.mine)
        else:
            stops += 1
            places += 0 if c.lunch else 1
        meals += c.lunch
        areas += c.kind == "area"
        hist += themed
        last_hist = themed
        spent += cost


PORTFOLIO_SPLIT = 0.8   # m216 (GUESS, benchmarked): the share of the time limit the usual search gets on a seeded day


def _solve_best(usable: list[Candidate], args: dict) -> DayPlan | None:
    """m216: on a seeded day, two searches of the same model share the time limit: the usual one (the solver's own
    first solution) and the two-stage one (a valid day built step by step, then improved). The plan with the lower
    solver cost wins, so the day is never worse than either search finds, and the total time is unchanged. Any other
    day is one usual search, exactly as before."""
    if not args.get("seeded"):
        return _solve(usable, forced_last=None, **args)
    limit = args["time_limit_s"]
    plans = [_solve(usable, forced_last=None, **{**args, "seeded": False, "time_limit_s": limit * PORTFOLIO_SPLIT}),
             _solve(usable, forced_last=None, **{**args, "seeded": True, "time_limit_s": limit * (1 - PORTFOLIO_SPLIT)})]
    found = [p for p in plans if p is not None]
    return min(found, key=lambda p: p.objective) if found else None


def plan_day(cands: list[Candidate], start_point: Point, day_start: int, day_end: int,
             travel: TravelTimes, legs: LegWeights, *, floor: float = -0.75, max_stops: int = 5,
             min_stops: int | None = None, budget_gbp: float | None = None,
             must_include: set[str] | frozenset[str] = frozenset(),
             peak_end: bool = False, end_bonus: float = 0.5, n_end_candidates: int = 5,
             time_limit_s: float = 1.0, max_wait_min: int = 60, max_areas: int = 1,
             buffer_walk_min: int = 0, buffer_transit_min: int = 0, lunch_bonus: float = 0.0,
             lunch_not_first: bool = False, max_theme: int = 2, max_places: int | None = None,
             seeded: bool = False) -> DayPlan:
    """Choose and order the stops for one day.

    Candidates below the floor or with no feasible time window are left out before solving,
    except must-do stops, which stay in if they fit a window. `min_stops` asks for at least that
    many stops (Test B: the same number as the generic plan). If it can't be met, the planner
    solves again without it and says so in `status`.
    """
    must = frozenset(must_include)
    if min_stops:
        # m187 (algorithm review, 20 Oct): the floor keeps out stops predicted to fall short of "Good", but it must
        # never leave a day short of its places. In simulation about 1 person in 8 had only 0-2 cards above it, so
        # their day had 0-2 places (and Test B's pair would differ in length). Then the person's own best cards come
        # in instead. A place they said they didn't enjoy never does: dayplan leaves those out before this.
        places = sorted((c.utility for c in cands if not c.lunch and not c.mine and _start_ranges(c, day_start, day_end)),
                        reverse=True)
        # m206 (WS7 benchmark): with spares. Letting in exactly `min_stops` cards left a day short whenever those
        # couldn't fit together (an evening after three places that close at 18:00 gave one place, not three).
        if places and sum(u > floor for u in places) < min_stops:
            floor = min(floor, places[min(min_stops + FLOOR_SPARES, len(places)) - 1] - 1e-6)
    usable = [c for c in cands if (c.utility > floor or c.moment_id in must or c.lunch or c.mine)
              and _start_ranges(c, day_start, day_end)]
    skipped = [c.moment_id for c in cands if c not in usable]
    missing_must = sorted(must - {c.moment_id for c in usable})
    if not usable:
        return DayPlan([], 0.0, None, False, dropped=skipped, status="no feasible moments")

    args = dict(start_point=start_point, day_start=day_start, day_end=day_end, travel=travel,
                legs=legs, floor=floor, max_stops=max_stops, time_limit_s=time_limit_s,
                max_wait_min=max_wait_min, budget_gbp=budget_gbp, must_include=must & {c.moment_id for c in usable},
                min_stops=min_stops, max_areas=max_areas,
                buffer_walk_min=buffer_walk_min, buffer_transit_min=buffer_transit_min, lunch_bonus=lunch_bonus,
                lunch_not_first=lunch_not_first, max_theme=max_theme, max_places=max_places,
                fixed_count=bool(min_stops) and min_stops >= max_stops, seeded=seeded)
    status = "ok"
    best = _solve_best(usable, args)
    if best is None and min_stops:
        # The hard minimum can defeat the first-solution heuristic. Drop it and instead add a
        # growing per-stop bonus (in utility units) until the plan has enough stops.
        args["min_stops"] = None
        for bonus in (0.0, 0.5, 1.0, 2.0, 4.0):
            best = _solve_best(usable, {**args, "stop_bonus": bonus})
            if best is not None and len(best.stops) >= min_stops:
                break
        if best is not None and len(best.stops) >= min_stops:
            args["stop_bonus"] = bonus
        else:
            status = f"could not fit {min_stops} stops"
    if best is None and args["must_include"]:
        args["must_include"] = frozenset()
        best = _solve_best(usable, args)
        status = "could not fit the must-do stop"

    if peak_end:
        def with_bonus(p: DayPlan | None) -> float:
            if p is None or not p.stops:
                return -math.inf
            return p.value + end_bonus * (p.stops[-1].utility - floor)

        top = sorted((k for k in range(len(usable)) if not usable[k].mine), key=lambda k: usable[k].utility,
                     reverse=True)[:n_end_candidates]
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
