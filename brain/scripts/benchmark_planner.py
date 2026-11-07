"""WS7: a benchmark of the day planner on fixed synthetic travellers (decisions/recommendation-engine-evaluation.md).

Run from brain/ with the venv: `.venv/bin/python scripts/benchmark_planner.py [--workers 4] [--time-limit 0.4]
[--out benchmarks/synthetic/planner.json] [--repeat 20]`.

**Synthetic only.** Every traveller here is made up: a fixed set of tastes (δ on the model's own features), written
by hand to stand for a kind of person (museums, nature, food, …). No real person's answers, ratings or plans are read,
and the output goes under `benchmarks/synthetic/`, apart from anything real. It is an *operational* check (is each
plan feasible, does it keep its constraints, does it waste time travelling, does it say what it doesn't know), the
first of Abram's three questions (product-direction.md). It is **never a target**: the planner is not tuned to these
numbers, and the 75% "strong match" line is not changed by them.

Each traveller × each day scenario gets four plans, all scored on the traveller's own (known) tastes:
- **personal (known tastes):** the real planner, told the traveller's tastes exactly: what the planner can do;
- **personal (after onboarding):** the real planner on what the short onboarding learns from simulated answers given
  by that traveller (two answer seeds): what a new user gets;
- **no answers:** the real planner with nothing known (the population average): Test B's generic comparison;
- **greedy:** a simple baseline, no solver: from where you are, the best-scoring next place that fits, until the day
  is full. Same tastes as "known", so the difference is the solver's.

What the planner can't know is reported, not hidden: no card says whether food is halal, vegetarian or kosher; most
cards don't say whether the way in is step-free; nothing knows a child's age. Those travellers run the same planner,
and the benchmark counts the stops whose suitability is unknown.

OR-Tools' guided local search stops at a time limit, so plans can differ between machines or runs. `--repeat N`
re-plans N of them and says how many changed.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing
import statistics
import sys
from dataclasses import asdict, dataclass, field, replace
from datetime import date
from pathlib import Path

import numpy as np

from brain import dayplan
from brain.config import DATA_DIR
from brain.dayplan import Block, Brief, LUNCH_START, LUNCH_MIN, spans_lunch
from brain.features import Conditions, moment_features
from brain.moments import Moment, Point, load_moments
from brain.personal import DeltaPosterior, prior_only
from brain.planner import LegWeights, parse_hhmm
from brain.popularity import load_onboarding, load_popularity, simulate_person
from brain.population import PopulationModel, load_population
from brain.scoring import score
from brain.travel import LondonEstimate

SEED = 20261107
CHARING_CROSS = Point(lat=51.507819, lon=-0.126137)   # CHECKED in data/testb/brief.yaml (TfL StopPoint API, 28 Sep)
ST_PANCRAS = Point(lat=51.5313, lon=-0.1262)          # GUESS (approximate), for the arrival-day scenario only

PLACE_AND_MOMENT = ["movement_views", "food", "green_nature", "history_culture", "iconic", "local_novel",
                    "walking_effort", "active", "outdoor_exposure", "photo_potential",
                    "contrast_reveal", "absorption", "awe", "social_pull"]


@dataclass(frozen=True)
class Profile:
    name: str
    delta: dict[str, float]                 # raw δ on the personal features (prior sd is 0.75; cost is on a log scale)
    needs: tuple[str, ...] = ()             # what the traveller needs that no card can answer yet
    brief: dict = field(default_factory=dict)   # what this traveller changes in every day (a lower budget, relaxed)
    runnable: bool = True
    note: str = ""


PROFILES = [
    Profile("museums_architecture", dict(history_culture=1.5, iconic=0.6, contrast_reveal=1.0, awe=0.8,
                                         outdoor_exposure=-0.4, green_nature=-0.3)),
    Profile("nature", dict(green_nature=1.5, outdoor_exposure=1.0, movement_views=0.6, crowds=-0.8,
                           history_culture=-0.6, iconic=-0.4)),
    Profile("food", dict(food=1.6, local_novel=1.0, social_pull=0.6, history_culture=-0.4)),
    Profile("family", dict(social_pull=1.0, absorption=1.2, walking_effort=-1.0, long_walk=-1.0,
                           transfer_30_plus=-0.7, crowds=-0.5, packed_pace=-0.6),
            needs=("children's ages, child prices, buggy access",)),
    Profile("relaxed", dict(packed_pace=-1.5, walking_effort=-0.8, long_walk=-1.0, transfer_15_30=-0.4,
                            transfer_30_plus=-0.6, crowds=-0.6, green_nature=0.5), brief=dict(relaxed=True)),
    Profile("active", dict(active=1.5, absorption=1.0, walking_effort=1.0, long_walk=1.0, packed_pace=0.8,
                           outdoor_exposure=0.5)),
    Profile("budget", dict(cost_per_10gbp=1.2, local_novel=0.4), brief=dict(budget_gbp=10.0),
            note="cost weighs e^1.2 ≈ 3.3 times the average; £10 a day for places and lunch"),
    Profile("strict_dietary", dict(food=0.8, local_novel=0.4), needs=("halal food",),
            note="the planner has no food-suitability data (WS2): every food stop is 'unknown'"),
    Profile("accessibility", dict(walking_effort=-1.2, long_walk=-1.2, active=-0.8, transfer_30_plus=-0.4),
            needs=("step-free way in",), note="no step-free filter exists; stops are counted by what the card says"),
    Profile("likes_everything", {t: 1.2 for t in PLACE_AND_MOMENT}, note="too many strong matches"),
    Profile("likes_nothing", {t: -1.2 for t in PLACE_AND_MOMENT}, note="no strong matches"),
    Profile("multi_city", {}, runnable=False,
            note="not run: the planner plans one day in one city (decisions/multi-city-travel-architecture.md)"),
]


@dataclass(frozen=True)
class Scenario:
    name: str
    start: str
    end: str
    stops: int
    weekday: str
    budget_gbp: float | None = None
    rain_prob: float | None = None
    mine: tuple[Block, ...] = ()
    lunch: bool = True
    start_point: tuple[str, Point] = ("Charing Cross station", CHARING_CROSS)
    note: str = ""


SCENARIOS = [
    Scenario("full_day_sat", "10:00", "18:00", 4, "sat"),
    Scenario("testb_sat", "12:00", "17:00", 4, "sat", budget_gbp=40.0, note="Test B's day (data/testb/brief.yaml)"),
    Scenario("weekday_mon", "10:00", "17:00", 4, "mon"),
    Scenario("morning_sun", "09:00", "13:00", 2, "sun"),
    Scenario("evening_fri", "17:00", "22:00", 3, "fri"),
    Scenario("rain_sat", "11:00", "17:00", 3, "sat", rain_prob=0.8),
    Scenario("plans_near_14", "10:00", "18:00", 4, "sat", mine=(Block("plans", 840, 930, "near"),)),
    Scenario("plans_unknown_lunch", "10:00", "18:00", 4, "sat", mine=(Block("plans", 750, 840, "unknown"),)),
    Scenario("free_afternoon", "10:00", "19:00", 4, "sat", mine=(Block("free", 900, 1020),)),
    Scenario("arrival_day", "15:00", "19:30", 2, "fri", lunch=False, start_point=("St Pancras", ST_PANCRAS),
             note="a trip's first day, after arriving by train"),
    Scenario("departure_day", "09:00", "12:30", 2, "mon", lunch=False, note="a trip's last day, before leaving"),
    Scenario("long_day", "09:00", "21:00", 6, "sat", note="many places: does it run out or repeat?"),
]


# ---- the context each worker needs (loaded once, then forked) -----------------------------------------------------

_C: dict = {}


def load_context(time_limit: float) -> dict:
    pop = load_population(DATA_DIR / "priors.yaml")
    moments = [m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"]
    pp = load_popularity(DATA_DIR / "popularity.yaml")
    _C.update(pop=pop, moments=moments, by_id={m.id: m for m in moments}, travel=LondonEstimate(),
              ob=load_onboarding(DATA_DIR, None), popularity=pp.shares if pp else None, time_limit=time_limit, seeds=2)
    return _C


def delta_of(pop: PopulationModel, prof: Profile) -> np.ndarray:
    unknown = set(prof.delta) - set(pop.personal_names)
    if unknown:
        raise KeyError(f"{prof.name}: not personal features: {sorted(unknown)}")
    return np.array([prof.delta.get(n, 0.0) for n in pop.personal_names], dtype=float)


def known(delta: np.ndarray) -> DeltaPosterior:
    """The planner told the traveller's tastes exactly (a very tight posterior)."""
    return DeltaPosterior(delta, np.diag(np.full(len(delta), 1e6)), 0, 0)


def brief_for(sc: Scenario, prof: Profile, time_limit: float) -> Brief:
    b = Brief(start_name=sc.start_point[0], start=sc.start_point[1], start_time=sc.start, end_time=sc.end,
              stops=sc.stops, budget_gbp=sc.budget_gbp, day_label="Benchmark", weekday=sc.weekday,
              rain_prob=sc.rain_prob, time_limit_s=time_limit, lunch=sc.lunch, mine=sc.mine)
    extra = dict(prof.brief)
    if "budget_gbp" in extra and b.budget_gbp is not None:
        extra["budget_gbp"] = min(extra["budget_gbp"], b.budget_gbp)
    return replace(b, **extra)


# ---- the simple baseline -----------------------------------------------------------------------------------------

@dataclass
class Stop:
    """One stop of any plan, in the benchmark's own terms."""
    id: str                 # the planner's id: a card, "<card>#lunch", "lunch@…", "mine<k>@…"
    arrive: int
    depart: int
    travel: int


def greedy_plan(pop: PopulationModel, b: np.ndarray, brief: Brief, usable: list[Moment], travel) -> list[Stop]:
    """From where you are, the best next place that fits (its utility less the leg's penalty), and lunch where you are
    when lunchtime comes; no solver.
    It keeps the same hard rules as the planner (hours, opening days, budget, one area, one variant, at most two
    history-and-culture stops and never two in a row), and the person's blocks: a place ends before a block or starts
    after it."""
    idx = {n: i for i, n in enumerate(pop.names)}
    legs = LegWeights(b[idx["transfer_15_30"]], b[idx["transfer_30_plus"]])
    cond = Conditions(None, brief.rain_prob)
    u = {m.id: score(pop.vector(moment_features(m, cond)), b) for m in usable}
    day_start, day_end = parse_hhmm(brief.start_time), parse_hhmm(brief.end_time)
    def held(blk: Block) -> tuple[int, int]:   # plans away from the places keep the planner's time to get there and back
        allow = dayplan.AWAY_MIN.get(blk.location, dayplan.AWAY_MIN["unknown"]) if blk.away else 0
        return max(day_start, blk.start_min - allow), min(day_end, blk.end_min + allow)
    blocks = sorted(held(blk) for blk in brief.mine)
    t, pos, out, used_groups, spent, areas, hist_n = day_start, brief.start, [], set(), 0.0, 0, 0
    by_id = {m.id: m for m in usable}
    history = lambda m: m is not None and moment_features(m).get("history_culture", 0) >= 1
    need_lunch = brief.lunch and spans_lunch(day_start, day_end)
    n_places = brief.stops - (1 if need_lunch else 0)
    lo_l, hi_l = LUNCH_START
    had_lunch = False
    while sum(is_place(s.id) for s in out) < n_places:
        affordable = brief.budget_gbp is None or spent + brief.lunch_gbp <= brief.budget_gbp
        if need_lunch and not had_lunch and affordable and lo_l <= t <= hi_l \
                and not any(t < be and t + LUNCH_MIN > bs for bs, be in blocks):
            out.append(Stop("lunch@here", t, t + LUNCH_MIN, 0))   # lunch where you are, as the planner's slots
            t, spent, had_lunch = t + LUNCH_MIN, spent + brief.lunch_gbp, True
            continue
        best = None
        for m in usable:
            if any(s.id == m.id for s in out) or (m.variant_of and m.variant_of in used_groups):
                continue
            if m.kind == "area" and areas >= 1:
                continue
            if history(m) and (hist_n >= 2 or (out and history(by_id.get(out[-1].id)))):   # D127, as the planner
                continue
            if brief.budget_gbp is not None and spent + (m.cost_gbp or 0) > brief.budget_gbp:
                continue
            tt = int(round(travel.minutes(pos, m.start())))
            dur = int(round(m.duration_min()))
            for lo, hi in m.windows():
                s = max(t + tt, lo, day_start)
                if s - (t + tt) > 60 or s + dur > min(hi, day_end):
                    continue
                if any(s < be and s + dur > bs for bs, be in blocks):
                    continue
                if need_lunch and not had_lunch and affordable and t < hi_l and s + dur > hi_l:
                    continue   # it would run past the latest lunch

                val = u[m.id] - legs.penalty(tt)
                if best is None or val > best[0]:
                    best = (val, m, s, dur, tt)
                break
        nxt_block = next(((bs, be) for bs, be in blocks if bs >= t), None)
        if best is None:
            if nxt_block is None:
                break
            out.append(Stop(f"mine{blocks.index(nxt_block)}@here", nxt_block[0], nxt_block[1], 0))
            t = nxt_block[1]
            continue
        _, m, s, dur, tt = best
        if nxt_block and s + dur > nxt_block[0]:   # the block comes first
            out.append(Stop(f"mine{blocks.index(nxt_block)}@here", nxt_block[0], nxt_block[1], 0))
            t = nxt_block[1]
            continue
        out.append(Stop(m.id, s, s + dur, tt))
        t, pos, spent = s + dur, m.end(), spent + (m.cost_gbp or 0)
        areas += m.kind == "area"
        hist_n += history(m)
        if m.variant_of:
            used_groups.add(m.variant_of)
    for k, (bs, be) in enumerate(blocks):   # blocks after the last place
        if not any(s.id.startswith(f"mine{k}@") for s in out):
            out.append(Stop(f"mine{k}@here", bs, be, 0))
    return sorted(out, key=lambda s: s.arrive)


# ---- checks and measures on any plan -----------------------------------------------------------------------------

def base(cid: str) -> str:
    return cid.split("#")[0]


def is_place(cid: str) -> bool:
    return not cid.startswith(("lunch@", "mine")) and not cid.endswith("#lunch")


def is_lunch(cid: str) -> bool:
    return cid.startswith("lunch@") or cid.endswith("#lunch")


def violations(stops: list[Stop], brief: Brief, by_id: dict[str, Moment], lunch_gbp: float) -> list[str]:
    """Every hard rule a plan must keep, checked from the outside (not trusting the solver)."""
    out = []
    day_start, day_end = parse_hhmm(brief.start_time), parse_hhmm(brief.end_time)
    rain = brief.rain_prob is not None and brief.rain_prob >= 0.5
    for k, s in enumerate(stops):
        if s.arrive < day_start or s.depart > day_end:
            out.append(f"outside the day: {s.id}")
        if k and s.arrive < stops[k - 1].depart + s.travel - 1:
            out.append(f"overlap: {stops[k - 1].id} -> {s.id}")
        if s.id.startswith("mine"):
            continue
        if s.id.startswith("lunch@"):
            lo, hi = LUNCH_START
            if not (lo <= s.arrive <= hi):
                out.append(f"lunch outside the lunch window: {s.id}")
            continue
        m = by_id[base(s.id)]
        if not any(lo <= s.arrive and s.depart <= hi for lo, hi in m.windows()):
            out.append(f"outside its hours: {s.id}")
        if not m.open_on(brief.weekday):
            out.append(f"closed that day: {s.id}")
        if rain and m.best_time.weather == ["dry"]:
            out.append(f"dry-weather card in rain: {s.id}")
    places = [base(s.id) for s in stops if is_place(s.id) or s.id.endswith("#lunch")]
    if len(places) != len(set(places)):
        out.append("a card twice")
    groups = [by_id[p].variant_of for p in places if by_id[p].variant_of]
    if len(groups) != len(set(groups)):
        out.append("two variants of one moment")
    if sum(by_id[p].kind == "area" for p in places) > 1:
        out.append("more than one area")
    # as in the planner (D127): any other stop between two, lunch or the person's own time, breaks the run
    hist = [is_place(s.id) and moment_features(by_id[base(s.id)]).get("history_culture", 0) >= 1 for s in stops]
    if sum(hist) > 2:
        out.append("more than two history-and-culture stops")
    if any(a and b for a, b in zip(hist, hist[1:])):
        out.append("history-and-culture back to back")
    cost = sum(by_id[p].cost_gbp or 0 for p in places) + sum(lunch_gbp for s in stops if s.id.startswith("lunch@"))
    if brief.budget_gbp is not None and cost > brief.budget_gbp + 1e-6:
        out.append(f"over budget: £{cost:.0f} of £{brief.budget_gbp:.0f}")
    for k, blk in enumerate(brief.mine):
        held = [s for s in stops if s.id.startswith(f"mine{k}@")]
        if len(held) != 1 or not (held[0].arrive <= blk.start_min and held[0].depart >= blk.end_min):
            out.append(f"block {k} not kept")
        for s in stops:
            if not s.id.startswith("mine") and s.arrive < blk.end_min and s.depart > blk.start_min:
                out.append(f"stop inside block {k}: {s.id}")
    return out


def shortest_order_travel(points: list[tuple[Point, Point]], start: Point, travel) -> float:
    """The least travel to visit the same places in any order (ignoring hours): the 'unnecessary distance' yardstick."""
    best = None
    for order in itertools.permutations(range(len(points))):
        pos, tot = start, 0.0
        for i in order:
            tot += travel.minutes(pos, points[i][0])
            pos = points[i][1]
        best = tot if best is None else min(best, tot)
    return best or 0.0


def measure(stops: list[Stop], brief: Brief, pop: PopulationModel, b_true: np.ndarray, prof: Profile) -> dict:
    by_id, travel = _C["by_id"], _C["travel"]
    cond = Conditions(None, brief.rain_prob)
    idx = {n: i for i, n in enumerate(pop.names)}
    legs = LegWeights(b_true[idx["transfer_15_30"]], b_true[idx["transfer_30_plus"]])
    day_start, day_end = parse_hhmm(brief.start_time), parse_hhmm(brief.end_time)
    places = [s for s in stops if is_place(s.id)]
    u = [score(pop.vector(moment_features(by_id[base(s.id)], cond)), b_true) for s in places]
    # a food card as the lunch stop is a moment too: it counts in the day's value (a "lunch near X" slot counts 0)
    u_lunch = [score(pop.vector(moment_features(by_id[base(s.id)], cond)), b_true) for s in stops
               if s.id.endswith("#lunch")]
    food = [s for s in stops if is_lunch(s.id) or (is_place(s.id) and (by_id[base(s.id)].tag("food") or 0) >= 2)]
    in_order = [by_id[base(s.id)] for s in stops if is_place(s.id) or s.id.endswith("#lunch")]
    travel_places = 0.0
    pos = brief.start
    for m in in_order:
        travel_places += travel.minutes(pos, m.start())
        pos = m.end()
    shortest = shortest_order_travel([(m.start(), m.end()) for m in in_order], brief.start, travel)
    busy = sum(s.depart - s.arrive for s in stops) + sum(s.travel for s in stops)
    block_min = sum(blk.end_min - blk.start_min for blk in brief.mine)
    kept_min = sum(blk.end_min - blk.start_min for k, blk in enumerate(brief.mine)
                   if any(s.id.startswith(f"mine{k}@") and s.arrive <= blk.start_min and s.depart >= blk.end_min
                          for s in stops))
    labels = [dayplan.match_label(pop, x) for x in u]
    return {
        "violations": violations(stops, brief, by_id, 15.0),
        "places": len(places),
        "lunch": any(is_lunch(s.id) for s in stops),
        "value": round(sum(u) + sum(u_lunch) - sum(legs.penalty(s.travel) for s in stops if not s.id.startswith("mine")),
                       3),
        "u": [round(x, 3) for x in u],
        "strong": sum(lab.startswith("A strong") for lab in labels),
        "good": sum(lab.startswith("A good") for lab in labels),
        "travel_min": sum(s.travel for s in stops),
        "max_leg": max((s.travel for s in stops), default=0),
        "legs_over_30": sum(s.travel > 30 for s in stops),
        "excess_travel_min": round(max(0.0, travel_places - shortest), 1),
        "slack_min": max(0, (day_end - day_start) - busy),
        "free_kept_share": (kept_min / block_min) if block_min else None,
        "unknown_step_free": sum(by_id[base(s.id)].approach.step_free is None for s in places),
        "not_step_free": sum(by_id[base(s.id)].approach.step_free is False for s in places),
        "unknown_hours_text": sum(not by_id[base(s.id)].best_time.hours for s in places),
        "unknown_diet": len(food) if "halal food" in prof.needs else 0,
        "unknown_family": len(places) if prof.needs and prof.needs[0].startswith("children") else 0,
        "ids": [s.id for s in stops],
    }


def from_planner(plan) -> list[Stop]:
    return [Stop(st.moment_id, st.arrive_min, st.depart_min, st.travel_min) for st in plan.stops]


def available_strong(pop: PopulationModel, b_true: np.ndarray, brief: Brief) -> int:
    """How many cards that fit this day are strong matches on the traveller's own tastes (the 75% line)."""
    cond = Conditions(None, brief.rain_prob)
    day_start, day_end = parse_hhmm(brief.start_time), parse_hhmm(brief.end_time)
    rain = brief.rain_prob is not None and brief.rain_prob >= 0.5
    n = 0
    for m in _C["moments"]:
        if not (m.plannable() and m.open_on(brief.weekday)) or (rain and m.best_time.weather == ["dry"]):
            continue
        if not any(max(lo, day_start) + m.duration_min() <= min(hi, day_end) for lo, hi in m.windows()):
            continue
        u = score(pop.vector(moment_features(m, cond)), b_true)
        n += dayplan.match_label(pop, u).startswith("A strong")
    return n


# ---- one traveller on one day ------------------------------------------------------------------------------------

def run_one(job: tuple[int, int]) -> list[dict]:
    pi, si = job
    prof, sc = PROFILES[pi], SCENARIOS[si]
    pop, moments, travel = _C["pop"], _C["moments"], _C["travel"]
    brief = brief_for(sc, prof, _C["time_limit"])
    delta = delta_of(pop, prof)
    b_true = pop.b_person(delta)
    rows = []

    def row(kind: str, stops: list[Stop], status: str = "ok", seed: int | None = None):
        r = {"profile": prof.name, "scenario": sc.name, "plan": kind, "seed": seed, "status": status,
             **measure(stops, brief, pop, b_true, prof)}
        rows.append(r)

    def planner(post, loved=(), disliked=()):
        plan, _, _, _ = dayplan.personal_plan(pop, post, moments, brief, travel, loved=list(loved),
                                              disliked=list(disliked), familiar=False, popularity=_C["popularity"])
        return from_planner(plan), plan.status

    stops, status = planner(known(delta))
    row("personal_known", stops, status)
    for k in range(_C["seeds"]):
        seed = SEED + 1000 * pi + 37 * si + k
        _, post, loved, disliked = simulate_person(pop, _C["ob"], seed, delta=delta)
        stops, status = planner(post, loved, disliked)
        row("personal_onboarded", stops, status, seed)
    stops, status = planner(prior_only(pop.delta_prior_sd))
    row("no_answers", stops, status)
    usable = [m for m in moments if m.plannable() and m.open_on(brief.weekday) and not m.meal
              and not (brief.rain_prob is not None and brief.rain_prob >= 0.5 and m.best_time.weather == ["dry"])]
    row("greedy", greedy_plan(pop, b_true, brief, usable, travel))
    for r in rows:
        r["strong_available"] = available_strong(pop, b_true, brief)
    return rows


# ---- the report ---------------------------------------------------------------------------------------------------

def pct(xs, q):
    return float(np.percentile(xs, q)) if xs else float("nan")


def summarise(rows: list[dict]) -> list[str]:
    out = []
    kinds = ["personal_known", "personal_onboarded", "no_answers", "greedy"]
    out.append("SYNTHETIC TRAVELLERS ONLY: not real people, not a target to tune to.\n")
    out.append("1. Hard rules (checked from outside the planner): plans with any violation")
    for k in kinds:
        rs = [r for r in rows if r["plan"] == k]
        bad = [r for r in rs if r["violations"]]
        out.append(f"   {k:20s} {len(bad):3d} of {len(rs)}" + (f"  e.g. {bad[0]['profile']}/{bad[0]['scenario']}: "
                                                              f"{bad[0]['violations'][:2]}" if bad else ""))
    out.append("\n2. Value on each traveller's own tastes (sum of stop utilities less leg penalties), by plan")
    for k in kinds:
        v = [r["value"] for r in rows if r["plan"] == k]
        out.append(f"   {k:20s} mean {statistics.mean(v):6.2f}  median {statistics.median(v):6.2f}")
    paired = {}
    for r in rows:
        paired.setdefault((r["profile"], r["scenario"]), {}).setdefault(r["plan"], []).append(r["value"])
    for a, b in (("personal_known", "no_answers"), ("personal_onboarded", "no_answers"), ("personal_known", "greedy")):
        d = [statistics.mean(p[a]) - statistics.mean(p[b]) for p in paired.values() if a in p and b in p]
        out.append(f"   {a} - {b}: mean {statistics.mean(d):+.2f}; better in {sum(x > 1e-6 for x in d)}, "
                   f"same in {sum(abs(x) <= 1e-6 for x in d)}, worse in {sum(x < -1e-6 for x in d)} of {len(d)}")
    out.append("\n3. Places kept (asked vs planned), lunch, travel and slack, by plan")
    for k in kinds:
        rs = [r for r in rows if r["plan"] == k]
        out.append(f"   {k:20s} places {statistics.mean(r['places'] for r in rs):.2f}; "
                   f"travel {statistics.mean(r['travel_min'] for r in rs):.0f} min (max leg p90 "
                   f"{pct([r['max_leg'] for r in rs], 90):.0f}); legs over 30 min {sum(r['legs_over_30'] for r in rs)}; "
                   f"extra travel vs the shortest order: median {statistics.median(r['excess_travel_min'] for r in rs):.0f}, "
                   f"p90 {pct([r['excess_travel_min'] for r in rs], 90):.0f} min; slack median "
                   f"{statistics.median(r['slack_min'] for r in rs):.0f} min")
    out.append("\n4. By scenario (personal, known tastes): places / asked, lunch, status not ok")
    for sc in SCENARIOS:
        rs = [r for r in rows if r["plan"] == "personal_known" and r["scenario"] == sc.name]
        if not rs:
            continue
        lunch_expected = sc.lunch and spans_lunch(parse_hhmm(sc.start), parse_hhmm(sc.end))
        out.append(f"   {sc.name:20s} places {statistics.mean(r['places'] for r in rs):.1f} of "
                   f"{sc.stops - lunch_expected}; lunch {sum(r['lunch'] for r in rs)}/{len(rs)}"
                   f"{' (expected)' if lunch_expected else ' (none expected)'}; free time kept "
                   f"{'—' if rs[0]['free_kept_share'] is None else f'{statistics.mean(r['free_kept_share'] for r in rs):.0%}'}; "
                   f"not ok {sum(r['status'] != 'ok' for r in rs)}")
    out.append("\n5. By traveller (personal, known tastes): strong matches available on the day vs in the plan")
    for prof in PROFILES:
        rs = [r for r in rows if r["plan"] == "personal_known" and r["profile"] == prof.name]
        if not rs:
            out.append(f"   {prof.name:20s} {prof.note}")
            continue
        out.append(f"   {prof.name:20s} available median {statistics.median(r['strong_available'] for r in rs):.0f}; "
                   f"in plan {sum(r['strong'] for r in rs)} strong, {sum(r['good'] for r in rs)} good, of "
                   f"{sum(r['places'] for r in rs)} places; stop utility p10/p50/p90 "
                   f"{pct([x for r in rs for x in r['u']], 10):.2f}/{pct([x for r in rs for x in r['u']], 50):.2f}/"
                   f"{pct([x for r in rs for x in r['u']], 90):.2f}" + (f"  [{prof.note}]" if prof.note else ""))
    out.append("\n6. What the plan can't know (personal, known tastes)")
    rs = [r for r in rows if r["plan"] == "personal_known"]
    n_places = sum(r["places"] for r in rs)
    out.append(f"   step-free way in unknown: {sum(r['unknown_step_free'] for r in rs)} of {n_places} places; "
               f"known not step-free: {sum(r['not_step_free'] for r in rs)}")
    acc = [r for r in rs if r["profile"] == "accessibility"]
    out.append(f"   accessibility traveller: unknown {sum(r['unknown_step_free'] for r in acc)} of "
               f"{sum(r['places'] for r in acc)} places")
    diet = [r for r in rs if r["profile"] == "strict_dietary"]
    out.append(f"   strict dietary traveller: food stops with unknown suitability {sum(r['unknown_diet'] for r in diet)} "
               f"(all of them: no card carries food-suitability data)")
    out.append(f"   opening hours not written for the person: {sum(r['unknown_hours_text'] for r in rs)} of {n_places}")
    out.append("\n7. Variety: how often each card appears in personal plans (known tastes), top 8")
    count: dict[str, int] = {}
    for r in rs:
        for cid in r["ids"]:
            if is_place(cid):
                count[cid] = count.get(cid, 0) + 1
    for cid, n in sorted(count.items(), key=lambda kv: -kv[1])[:8]:
        out.append(f"   {n:3d} of {len(rs)} plans  {cid}")
    out.append(f"   cards used at least once: {len(count)} of {len(_C['moments'])} ready cards")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--time-limit", type=float, default=1.0)   # the app's default (BRAIN_PLANNER_TIME_LIMIT_S)
    ap.add_argument("--out", type=Path, default=Path("benchmarks/synthetic/planner.json"))
    ap.add_argument("--repeat", type=int, default=0, help="re-plan this many (traveller, day) pairs to check stability")
    ap.add_argument("--only", nargs="*", default=None, help="limit to these travellers (names)")
    ap.add_argument("--seeds", type=int, default=2, help="simulated onboarding answers per traveller and day")
    args = ap.parse_args(argv)
    load_context(args.time_limit)
    _C["seeds"] = args.seeds
    jobs = [(pi, si) for pi, p in enumerate(PROFILES) if p.runnable and (not args.only or p.name in args.only)
            for si in range(len(SCENARIOS))]
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        rows = [r for rs in pool.map(run_one, jobs) for r in rs]
    lines = summarise(rows)
    if args.repeat:
        again = jobs[: args.repeat]
        with multiprocessing.get_context("fork").Pool(args.workers) as pool:
            rows2 = [r for rs in pool.map(run_one, again) for r in rs]
        first = {(r["profile"], r["scenario"], r["plan"], r["seed"]): r["ids"] for r in rows}
        changed = sum(first[(r["profile"], r["scenario"], r["plan"], r["seed"])] != r["ids"] for r in rows2)
        lines.append(f"\n8. Stability: re-planned {len(rows2)} plans ({len(again)} traveller-days): {changed} changed")
    print("\n".join(lines))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    meta = {"synthetic": True, "date": date.today().isoformat(), "seed": SEED, "time_limit_s": args.time_limit,
            "onboarding_seeds": args.seeds,
            "population_version": _C["pop"].version, "cards": len(_C["moments"]),
            "profiles": [asdict(p) for p in PROFILES], "scenarios": [
                {**{k: v for k, v in asdict(s).items() if k not in ("mine", "start_point")},
                 "mine": [asdict(b) for b in s.mine], "start_point": s.start_point[0]} for s in SCENARIOS]}
    args.out.write_text(json.dumps({"meta": meta, "summary": lines, "rows": rows}, indent=1, default=str))
    head = (f"Planner benchmark, {meta['date']}: synthetic travellers only. Seed {SEED}; time limit {args.time_limit} s; "
            f"{args.seeds} onboarding answer seeds; population {meta['population_version']}; {meta['cards']} ready cards.\n"
            f"Re-run: .venv/bin/python scripts/benchmark_planner.py --seeds {args.seeds} --repeat {args.repeat}\n\n")
    args.out.with_suffix(".txt").write_text(head + "\n".join(lines) + "\n")
    print(f"\nwrote {args.out} ({len(rows)} plans) and {args.out.with_suffix('.txt')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
