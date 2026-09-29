"""The day planner behind every plan a person gets: the Test B plans (`brain.testb`) and the app (`brain.api`).

One engine, so the app plans exactly as Test B did (D107):
- the person's utility for each ready card, S = x·(b_population + δ_person);
- one lunch stop when the day spans midday (D102), buffers after each leg (D100);
- longer stays for a relaxed person (D102); cards at places they didn't enjoy are never planned (D100);
- with `familiar`, one place they loved plus new places (D100; off for the real Test B, on in the app, D103);
- rain swaps that respect their weights (D102); "Best" lines only when the stop's time matches (D100, D105);
- participant-facing wording: travel legs, approach, costs (D100–D102).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, replace
from pathlib import Path

import yaml

from .aspiration import AspirationMap
from .features import Conditions, moment_features
from .moments import Moment, Point
from .personal import DeltaPosterior
from .planner import (Candidate, DayPlan, LegWeights, candidate_for, extend_dwell, fits_day, hhmm, parse_hhmm,
                      plan_day, spread_to_end)
from .population import PopulationModel
from .scoring import contributions, named_weights, value_gbp
from .travel import LondonEstimate


# ---- inputs -------------------------------------------------------------------------

def load_swipe_items(path: Path) -> dict[int, Moment]:
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    out = {}
    for num, it in d["items"].items():
        out[int(num)] = Moment.model_validate({
            "id": it.get("moment_id") or f"swipe_{int(num):02d}", "title": it["name"],
            "place": {"name": it["name"]}, "features": {"place": it["place"], "moment": it["moment"]},
            "cost_gbp": it.get("cost_gbp"), "source": "swipe-item"})
    return out


def load_app_items(path: Path, later: bool = False) -> list[int]:
    """The swipe places the app shows before the first plan (D110, D112): `app_items`, or all of them if the list is
    missing. With `later`, the ones asked in "Improve future plans" (`app_items_later`)."""
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    items = [int(i) for i in (d.get("app_items_later") or [] if later else d.get("app_items") or d["items"])]
    unknown = set(items) - {int(i) for i in d["items"]}
    if unknown:
        raise ValueError(f"app_items not in items: {sorted(unknown)}")
    return items


def load_swipe_cards(path: Path) -> dict[int, tuple[str, list[str]]]:
    """Each swipe place's name and the moment cards at the same place (D100)."""
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    return {int(num): (it["name"], list(it.get("cards") or [])) for num, it in d["items"].items()}


@dataclass
class Brief:
    """The same brief for both plans (test-plan.md): same day, times, number of stops and budget."""
    start_name: str
    start: Point
    start_time: str
    end_time: str
    stops: int
    budget_gbp: float | None = None
    day_label: str = "A day out in London"
    weekday: str | None = None     # "mon".."sun": cards closed that day are left out
    temp_c: float | None = None
    rain_prob: float | None = None
    time_limit_s: float = 2.0
    lunch_gbp: float = 15.0        # D102 (GUESS): the flexible lunch slot's cost per person
    sunset: str | None = None      # D105: "hh:mm" on the day the plans are for; sets the sunset-based "Best" lines


def load_brief(path: Path) -> Brief:
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    d["start"] = Point(**d["start"])
    return Brief(**d)


@dataclass
class PlanNotes:
    """For the review only (never sent): the familiar favourite and what happened to each loved place (D100),
    the person's pace and the lunch stop (D102)."""
    favourite: str | None = None
    loves: list[tuple[str, str]] = field(default_factory=list)       # (place, what happened to it)
    dislikes: list[tuple[str, str]] = field(default_factory=list)
    pace: str = "even"                                               # relaxed | even | packed
    lunch: str = ""


BUFFER_WALK_MIN, BUFFER_TRANSIT_MIN = 5, 10   # D100 (GUESS): breathing space after a walk / a Tube or bus leg


DAY_NAMES = dict(mon="Mondays", tue="Tuesdays", wed="Wednesdays", thu="Thursdays", fri="Fridays",
                 sat="Saturdays", sun="Sundays")


# D102 (GUESSES): every plan that spans midday has one meal stop, starting 11:30-13:30: a food card, or a flexible
# "lunch near X" slot of 45 min. The bonus (in utility units) makes the solver keep a lunch over an extra sight.
LUNCH_START = (11 * 60 + 30, 13 * 60 + 30)


LUNCH_MIN = 45


LUNCH_BONUS = 5.0


LUNCH_CARD_MIN = 0.5   # a food card is offered as the lunch stop only if the person is predicted to like it this much


def _base(cid: str) -> str:
    """A card's id from a planner id: "m_x#lunch" (the card as the lunch stop) → "m_x"."""
    return cid.split("#")[0]


def _sunset(brief: Brief) -> int | None:
    return parse_hhmm(brief.sunset) if brief.sunset else None


def pace_of(pop: PopulationModel, post: DeltaPosterior) -> str:
    """relaxed / packed from a confident packed-day weight, else even (D102)."""
    w = next((w for w in named_weights(pop, post) if w.name == "packed_pace"), None)
    if w is None or not w.confident:
        return "even"
    return "relaxed" if w.direction == "dislikes" else "packed"


def dwell_targets(by_id: dict[str, Moment], ids: list[str]) -> dict[str, int]:
    """D102: a relaxed person's stay at each stop: the top of the card's range, and at least 45 min in a garden
    or 60 in a park (a green place with "park" in its name)."""
    out = {}
    for mid in ids:
        m = by_id[mid]
        exp = m.experience.duration_min
        top = float(max(exp) if isinstance(exp, list) else exp)
        if (m.features.place.get("green_nature") or 0) >= 2:
            top = max(top, 60.0 if "park" in m.place.name.lower() else 45.0)
        out[mid] = int(round(float(m.approach.duration_min or 0) + top + float(m.experience.queue_min or 0)))
    return out


def lunch_candidates(real: list, by_id: dict[str, Moment], brief: Brief) -> list:
    """The planner's candidates plus the lunch options (D102): each food card the person is predicted to like
    (utility ≥ LUNCH_CARD_MIN) again as "<id>#lunch", allowed to start only in the lunch window (sharing a variant
    group with the card, so a plan holds one of the two), and a flexible "lunch near X" slot beside every place,
    scored as neutral (0). Nothing is added if the day doesn't span lunch."""
    lo, hi = LUNCH_START
    day_start, day_end = parse_hhmm(brief.start_time), parse_hhmm(brief.end_time)
    if day_end < lo + LUNCH_MIN or day_start > hi:
        return [c for c in real if not by_id[c.moment_id].meal]   # meal cards only ever serve as lunch (D104)
    out = []
    for c in real:
        m = by_id[c.moment_id]
        if (m.features.place.get("food") or 0) >= 2 and (m.cost_gbp or 0) > 0 and c.utility >= LUNCH_CARD_MIN:
            wins = tuple((max(a, lo), min(b, hi + c.duration_min)) for a, b in c.windows
                         if max(a, lo) + c.duration_min <= min(b, hi + c.duration_min))
            if wins:
                c = replace(c, group=c.group or f"meal:{c.moment_id}")
                out.append(replace(c, moment_id=f"{c.moment_id}#lunch", windows=wins, lunch=True))
        if not m.meal:
            out.append(c)
    slot = lambda mid, p: Candidate(mid, p, p, LUNCH_MIN, ((lo, hi + LUNCH_MIN),), 0.0, float(brief.lunch_gbp),
                                    None, "moment", lunch=True)
    out += [slot(f"lunch@{c.moment_id}", c.end) for c in real]
    out.append(slot("lunch@start", brief.start))   # D104: lunch near the start point, too
    return out


def leg_text(t: int | None, mode: str, came_from: str, exit_station: str | None, arrive_at: str | None,
             first: bool) -> str:
    """D102: a Tube or bus leg from a stop starts with the walk to a station, then names where you go."""
    if t is None or t <= 2:
        return ""
    if mode == "walk":
        return f"Getting there: about {t} min on foot from {came_from}."
    dest = f" to {arrive_at}" if arrive_at else ""
    if first:
        return f"Getting there: about {t} min by Tube or bus from {came_from}{dest}."
    walk = f"walk to {exit_station}" if exit_station else "walk to the nearest station"
    return f"Getting there: about {t} min: {walk}, then take the Tube or bus{dest}."


def personal_plan(pop: PopulationModel, post: DeltaPosterior, moments: list[Moment], brief: Brief,
                  travel: LondonEstimate, must_do: str | None = None, amap: AspirationMap | None = None,
                  fields: frozenset[str] = frozenset(), end_window: tuple[int, int] | None = None,
                  loved: list[tuple[str, list[str]]] = (), disliked: list[tuple[str, list[str]]] = (),
                  familiar: bool = False, keep: set[str] | frozenset[str] = frozenset(),
                  exclude: set[str] | frozenset[str] = frozenset()) -> tuple[DayPlan, list[dict], list[dict], PlanNotes]:
    """The personalised plan. `end_window` (earliest, latest end in minutes) keeps it ending within
    30 min of the generic plan (D97); if that can't be met, it plans without it and says so in `status`.

    D100: cards at places the person didn't enjoy are never planned. With `familiar`, the plan holds exactly one
    card at a place they loved (the best combination of the top three that fit the day), and the other stops are
    places they haven't marked as loved. `loved` and `disliked` are (swipe place, its card ids).
    D102: one of the stops is lunch when the day spans midday; a relaxed person gets longer stays where the day
    has room; rain swaps respect the person's weights.
    D110 ("swap this stop"): `keep` holds the other stops of the plan being changed, and `exclude` the cards swapped
    out so far; their day/night variants are left out too, so the swap brings something different."""
    b = pop.b_person(post.mean)
    cond = Conditions(brief.temp_c, brief.rain_prob)
    rain = brief.rain_prob is not None and brief.rain_prob >= 0.5
    gone = {m.variant_of for m in moments if m.id in exclude and m.variant_of}
    usable = [m for m in moments if m.plannable() and m.open_on(brief.weekday)
              and m.id not in exclude and not (m.variant_of and m.variant_of in gone)]
    if rain:
        usable = [m for m in usable if m.best_time.weather != ["dry"]]
    by_id = {m.id: m for m in usable}
    asp = {m.id: (amap.match(m, fields) if amap else 0.0) for m in usable}
    disliked_ids = {cid for _, ids in disliked for cid in ids} - {must_do}
    loved_ids = {cid for _, ids in loved for cid in ids} - disliked_ids
    floor = pop.cutpoints["rating"][1]
    real = [candidate_for(m, float(pop.vector(moment_features(m, cond, aspiration_match=asp[m.id])) @ b))
            for m in usable if m.id not in disliked_ids]
    cands = lunch_candidates(real, by_id, brief)
    by_cand = {c.moment_id: c for c in cands}
    idx = {n: i for i, n in enumerate(pop.names)}
    legs = LegWeights(b[idx["transfer_15_30"]], b[idx["transfer_30_plus"]], b[idx["packed_pace"]])
    day_start, day_end = parse_hhmm(brief.start_time), parse_hhmm(brief.end_time)
    common = dict(floor=floor, max_stops=brief.stops, min_stops=brief.stops,
                  budget_gbp=brief.budget_gbp, time_limit_s=brief.time_limit_s,
                  buffer_walk_min=BUFFER_WALK_MIN, buffer_transit_min=BUFFER_TRANSIT_MIN, lunch_bonus=LUNCH_BONUS)
    base_must = ({must_do} if must_do else set()) | {k for k in keep if k in by_cand}
    kept_loved = {k for k in base_must if _base(k) in loved_ids}
    notes = PlanNotes(pace=pace_of(pop, post))
    targets = dwell_targets(by_id, [c.moment_id for c in real]) if notes.pace == "relaxed" else {}

    def solve(sub: list, must: set[str]) -> DayPlan:
        latest = min(day_end, end_window[1]) if end_window else day_end
        plan = None
        if end_window:   # D97: end within 30 min of the generic plan
            plan = plan_day(sub, brief.start, day_start, latest, travel, legs, must_include=must, **common)
            if plan.status != "ok" or not plan.stops:
                plan = None
        if plan is None:
            plan = plan_day(sub, brief.start, day_start, day_end, travel, legs, must_include=must, **common)
        if targets and plan.stops:
            extend_dwell(plan, by_cand, targets, latest)
        if end_window and plan.stops:
            ok = spread_to_end(plan, by_cand, end_window[0], latest)
            if (not ok or plan.stops[-1].depart_min > end_window[1]) and plan.status == "ok":
                plan.status = "could not end within 30 min of the generic plan: fix by hand"
        return plan

    loved_all = {c.moment_id for c in cands if _base(c.moment_id) in loved_ids}
    if familiar and loved_ids:
        # when swapping, a kept stop at a loved place stays the one familiar favourite
        options = sorted((c for c in real if c.moment_id in loved_ids and fits_day(c, day_start, day_end)
                          and (not kept_loved or c.moment_id in {_base(k) for k in kept_loved})
                          and (brief.budget_gbp is None or c.cost_gbp <= brief.budget_gbp)),
                         key=lambda c: c.utility, reverse=True)[:3]
        best = None
        for fav in options:
            forced_ids = [fav.moment_id] + [x for x in (f"{fav.moment_id}#lunch",) if x in by_cand]
            for forced in forced_ids:
                sub = [c for c in cands if c.moment_id not in loved_all or _base(c.moment_id) == fav.moment_id]
                trial = solve(sub, base_must | {forced})
                if trial.status == "ok" and forced in {st.moment_id for st in trial.stops} \
                        and (best is None or trial.value > best.value):
                    best, notes.favourite = trial, fav.moment_id
        plan = best if best is not None else solve([c for c in cands if c.moment_id not in loved_all], base_must)
    else:
        plan = solve(cands, base_must)

    stops, prev_point, prev_name, prev_exit = [], brief.start, brief.start_name, brief.start_name
    for st in plan.stops:
        c = by_cand[st.moment_id]
        mode = travel.mode(prev_point, c.start)
        if st.moment_id == "lunch@start":
            place = brief.start_name
            stop = {"title": f"Lunch near {place}", "approach": "",
                    "what": "Pick a café, pub or food stall nearby.", "best": "", "best_windows": [],
                    "queue": 0, "moment_id": st.moment_id, "predicted": None, "why": [],
                    "travel_text": leg_text(st.travel_min, mode, prev_name, prev_exit, place, not stops)}
            nxt = (c.end, place, brief.start_name)
        elif st.moment_id.startswith("lunch@"):
            host = by_id[st.moment_id[len("lunch@"):]]
            # the slot sits where the host card ends: after the host, that's where you are; otherwise (no end point
            # of its own) it's where you arrive for it, e.g. Cutty Sark DLR station before the Greenwich hill
            after_host = bool(stops) and _base(stops[-1]["moment_id"]) == host.id
            place = host.leave_name() if after_host or host.experience.end_point else \
                (clean(host.approach.from_) or host.leave_name())
            stop = {"title": f"Lunch near {place}", "approach": "",
                    "what": "Pick a café, pub or food stall nearby.", "best": "", "best_windows": [],
                    "queue": 0, "moment_id": st.moment_id, "predicted": None, "why": [],
                    "travel_text": leg_text(st.travel_min, mode, prev_name, prev_exit, host.approach.from_, not stops)}
            nxt = (c.end, place, host.exit_station())
        else:
            m = by_id[_base(st.moment_id)]
            worth = value_gbp(pop, b, m, cond, aspiration_match=asp[m.id])   # "worth about £V to you" (D88, D112)
            stop = {"worth_gbp": round(worth) if worth >= 1 else None,
                    # the moment card's approach line (D112): from where, the path, where you arrive; card text only
                    "approach_steps": [{"label": k, "text": v} for k, v in
                                       (("From", clean(m.approach.from_)), ("The way in", clean(m.approach.path)),
                                        ("You arrive", clean(m.place.name))) if v],
                    "title": m.display_title(), "approach": approach_text(m, walked_from_stop=True),
                    "what": clean(m.experience.what_happens), "best": clean(m.best_time.light),
                    "best_windows": m.best_windows(_sunset(brief)), "queue": m.experience.queue_min or 0,
                    "moment_id": m.id, "predicted": st.utility,
                    "why": contributions(pop, b, moment_features(m, cond, st.travel_min, asp[m.id])),
                    "travel_text": leg_text(st.travel_min, mode, prev_name, prev_exit, m.approach.from_, not stops)}
            nxt = (m.end(), m.leave_name(), m.exit_station())
        stop.update({"key": st.moment_id,   # the planner's id ("<card>#lunch" when a food card is the lunch), for `keep`
                     "arrive": hhmm(st.arrive_min), "depart": hhmm(st.depart_min), "travel_min": st.travel_min,
                     "travel_mode": mode, "from": prev_name, "cost_gbp": c.cost_gbp,
                     "cost_kind": "food" if c.lunch else by_id[_base(st.moment_id)].price_kind(),
                     "rain_swap": "", "lunch": c.lunch, "familiar": _base(st.moment_id) == notes.favourite})
        stops.append(stop)
        prev_point, prev_name, prev_exit = nxt
    lunch_stop = next((s for s in stops if s["lunch"]), None)
    notes.lunch = (f"{lunch_stop['title']} at {lunch_stop['arrive']}" if lunch_stop else
                   "none fitted: add one by hand" if len(cands) > len(real) else "the day doesn't span lunch")
    # Rain swaps are backups, not part of the planned day: a loved place can be one; a disliked place never is,
    # nor a place the person is predicted not to enjoy, nor one with a feature they clearly dislike (D102).
    dislikes = {w.name for w in named_weights(pop, post) if w.confident and w.direction == "dislikes"}
    allowed = {c.moment_id for c in real if c.utility >= floor
               and not any(moment_features(by_id[c.moment_id], cond, aspiration_match=asp[c.moment_id]).get(f, 0) >= 1.0
                           for f in dislikes)}
    add_rain_swaps(stops, plan, by_id, by_cand, allowed, brief, travel)
    # Only moments that fit the day's hours count as "left out" (D99: no evening cards in a 12:00-17:00 day)
    visited = {_base(s["moment_id"]) for s in stops}
    left_out = [{"moment_id": c.moment_id, "title": by_id[c.moment_id].title, "predicted": round(c.utility, 3)}
                for c in sorted(real, key=lambda c: c.utility, reverse=True)
                if fits_day(c, day_start, day_end) and c.moment_id not in visited][:3]
    all_ready = {m.id: m for m in moments}
    notes.loves = [(name, love_note(ids, all_ready, by_cand, plan, notes.favourite, familiar, brief, rain, travel))
                   for name, ids in loved]
    notes.dislikes = [(name, "kept out of the plan" if any(i in all_ready for i in ids) else "no moment card")
                      for name, ids in disliked]
    return plan, stops, left_out, notes


def love_note(ids: list[str], ready: dict[str, Moment], cands: dict, plan: DayPlan, favourite: str | None,
              familiar: bool, brief: Brief, rain: bool, travel: LondonEstimate) -> str:
    """Why a place the person loved is in the plan or not (D100): no card, closed, hours, budget, distance or the
    one-favourite rule. For Abram's review; never sent."""
    have = [i for i in ids if i in ready]
    if not have:
        return "no moment card yet"
    planned = {_base(st.moment_id) for st in plan.stops}
    if favourite in have:
        return "in the plan, as the familiar favourite"
    if planned & set(have):
        return "in the plan"
    day_start, day_end = parse_hhmm(brief.start_time), parse_hhmm(brief.end_time)

    def could_fit(m: Moment) -> bool:
        return (m.plannable() and m.open_on(brief.weekday) and not (rain and m.best_time.weather == ["dry"])
                and fits_day(candidate_for(m, 0.0), day_start, day_end)
                and (brief.budget_gbp is None or (m.cost_gbp or 0) <= brief.budget_gbp))

    # judge the place by its card that could fit the day, if any (the day boat, not the night boat)
    m = max((ready[i] for i in have), key=lambda m: (could_fit(m), cands[m.id].utility if m.id in cands else -99))
    if not m.plannable():
        why = "its card isn't complete yet"
    elif not m.open_on(brief.weekday):
        why = f"closed on {DAY_NAMES.get((brief.weekday or '')[:3], brief.weekday)}"
    elif rain and m.best_time.weather == ["dry"]:
        why = "it's outdoors and rain is forecast"
    elif not fits_day(candidate_for(m, 0.0), day_start, day_end):
        hours = ", ".join(f"{hhmm(a)}–{hhmm(b)}" for a, b in m.windows())
        why = f"its hours ({hours}) don't fit {brief.start_time}–{brief.end_time}"
    elif brief.budget_gbp is not None and (m.cost_gbp or 0) > brief.budget_gbp:
        why = f"it costs {_money(m.cost_gbp)}, over the {_money(brief.budget_gbp)} budget"
    elif familiar and favourite:
        why = f"only one familiar favourite per plan, and {_lower_article(ready[favourite].title)} fitted the day better"
    elif familiar:
        why = "it didn't fit alongside the other stops"
    else:
        why = "it scored lower than the stops chosen, with the travel between them"
    near = [travel.minutes(ready[_base(st.moment_id)].end(), m.start()) for st in plan.stops
            if _base(st.moment_id) in ready and m.start() is not None]
    if near:
        why += f"; about {round(min(near))} min from the nearest stop"
    return why


def _lower_article(title: str) -> str:
    first, _, rest = title.partition(" ")
    return f"{first.lower()} {rest}" if first in ("A", "An", "The") else title


def _outdoors(m: Moment) -> bool:
    return (m.features.place.get("outdoor_exposure") or 0) >= 2 or m.best_time.weather == ["dry"]


def add_rain_swaps(stops: list[dict], plan: DayPlan, by_id: dict[str, Moment], cands: dict, allowed: set[str],
                   brief: Brief, travel: LondonEstimate, max_min: float = 20.0) -> None:
    """D100: for each outdoor stop, an indoor or covered moment nearby that fits the same time, written as
    "If it rains: …". Each swap is used once, and only `allowed` moments are used (D102: the person's weights).
    If no stop gets one and there is no indoor stop, the best allowed indoor moment within 30 min of any stop (at
    any time of the day) goes on that stop."""
    day_start, day_end = parse_hhmm(brief.start_time), parse_hhmm(brief.end_time)
    planned = {_base(st.moment_id) for st in plan.stops}
    groups = {by_id[i].variant_of for i in planned if i in by_id and by_id[i].variant_of}
    spend = sum(s["cost_gbp"] for s in stops)
    pool = [m for m in by_id.values() if m.id not in planned and m.id in allowed and m.id in cands
            and m.kind == "moment" and not m.meal and not _outdoors(m)
            and (m.variant_of is None or m.variant_of not in groups)]
    used: set[str] = set()

    def pick(st, stop: dict, limit: float, any_time: bool):
        here = by_id[_base(st.moment_id)].start()
        best = None
        for m in pool:
            if m.id in used:
                continue
            c = cands[m.id]
            lo, hi = (day_start, day_end) if any_time else (max(day_start, st.arrive_min - 30),
                                                             min(day_end, st.arrive_min + 30 + c.duration_min))
            if not fits_day(c, lo, hi):
                continue
            if brief.budget_gbp is not None and spend - stop["cost_gbp"] + (m.cost_gbp or 0) > brief.budget_gbp:
                continue
            t = travel.minutes(here, m.start())
            if t > limit:
                continue
            score = c.utility - 0.02 * t
            if best is None or score > best[0]:
                best = (score, m, t, travel.mode(here, m.start()))
        return best

    def line(m: Moment, t: float, mode: str) -> str:
        how = "on foot" if mode == "walk" else "by Tube or bus"
        return f"{m.display_title()}, about {max(5, math.ceil(t / 5) * 5)} min away {how}."

    real = [(st, s) for st, s in zip(plan.stops, stops) if _base(st.moment_id) in by_id]
    outdoor = [(st, s) for st, s in real if _outdoors(by_id[_base(st.moment_id)])]
    for st, s in outdoor:
        if (hit := pick(st, s, max_min, any_time=False)):
            used.add(hit[1].id)
            s["rain_swap"] = line(hit[1], hit[2], hit[3])
    indoor = [st for st, _ in real if (by_id[_base(st.moment_id)].features.place.get("outdoor_exposure") or 0) == 0]
    if outdoor and not used and not indoor:
        hits = [(h, s) for st, s in outdoor if (h := pick(st, s, 30.0, any_time=True))]
        if hits:
            hit, s = max(hits, key=lambda x: x[0][0])
            s["rain_swap"] = line(hit[1], hit[2], hit[3])


GENERIC_STOP_MIN = 45   # GUESS: used when a generic stop has no `depart` time


_VERBS = {"walk", "take", "go", "enter", "leave", "cross", "follow", "climb", "step", "ride", "head", "turn",
          "come", "start"}


def _same_place(a: str, b: str) -> bool:
    a, b = a.lower().strip(), b.lower().strip()
    return bool(a and b) and (a in b or b in a)


def approach_text(m: Moment, walked_from_stop: bool = False, came_from: str | None = None) -> str:
    """How to arrive, as full sentences (D100): "From X station, walk ..." when the path starts with a verb, else
    "Start at X. <path>". The card's "from" is left out after a walk from the previous stop (you aren't coming
    from it), when the path already says where from, and when you are already coming from there."""
    path = _sentence(clean(m.approach.path))
    frm = clean(m.approach.from_)
    if (not frm or walked_from_stop or path.lower().startswith("from ")
            or (came_from and _same_place(came_from, frm))):
        return path
    if not path:
        return f"Start at {frm}."
    if path.split()[0].lower().strip(",:;") in _VERBS:
        return f"From {frm}, {path[0].lower()}{path[1:]}"
    return f"Start at {frm}. {path}"


def _sentence(text: str) -> str:
    return text + "." if text and text[-1] not in ".!?" else text


_MARKER = re.compile(r"\s*\((?:GUESS|CHECKED|FOUNDER|FRIEND|UNVERIFIED)\b[^)]*\)")


# D100: the transport estimate. Each Tube or bus leg is counted as one Zone 1 pay-as-you-go single, capped at the
# Zones 1-2 daily cap. Sources: TfL fare API (London Bridge -> Westminster, valid from 4 Jul 2026: £3.00 off-peak,
# £3.10 peak; read 2026-09-28) and TfL adult fares 2026 (daily cap £8.90; read 2026-09-27).
TUBE_FARE_GBP = 3.00


DAILY_CAP_GBP = 8.90


def clean(text: str | None) -> str:
    """Participant-facing text: drop the cards' internal notes, e.g. "(GUESS)" or "(CHECKED: ...)"."""
    return _MARKER.sub("", text or "").strip()


def _travel_line(s: dict) -> str:
    if "travel_text" in s:          # personal stops: worded in personal_plan (D102)
        return s["travel_text"]
    if s.get("travel_min") is None:
        return ""
    how = "on foot" if s["travel_mode"] == "walk" else "by Tube or bus"
    src = f" from {s['from']}" if s.get("from") else ""
    return f"Getting there: about {int(s['travel_min'])} min {how}{src}."


def _money(c: float) -> str:
    return f"£{c:,.0f}" if float(c).is_integer() else f"£{c:,.2f}"


def _cost(c: float) -> str:
    return "free" if not c else _money(c)


def _cost_line(s: dict) -> str:
    """Never call food "entry" (D100)."""
    c = s.get("cost_gbp") or 0.0
    if not c:
        return "Cost: free"
    return {"food": f"Food: about {_money(c)}", "ticket": f"Ticket: {_money(c)}",
            "hire": f"Hire: {_money(c)}"}.get(s.get("cost_kind") or "entry", f"Entry: {_money(c)}")


def transport_gbp(stops: list[dict]) -> float:
    legs = sum(1 for s in stops if s.get("travel_min") is not None and s.get("travel_mode") != "walk")
    return round(min(legs * TUBE_FARE_GBP, DAILY_CAP_GBP), 2)


def _leave(s: dict) -> str:
    return s.get("depart") or hhmm(parse_hhmm(s["arrive"]) + GENERIC_STOP_MIN)


def _best_line(s: dict) -> str:
    """"Best: …" only when the stop's own time matches (D100)."""
    if not s.get("best"):
        return ""
    a, b = parse_hhmm(s["arrive"]), parse_hhmm(_leave(s))
    return f"Best: {s['best']}" if any(lo < b and a < hi for lo, hi in s.get("best_windows") or []) else ""


def summary_lines(brief: Brief, stops: list[dict]) -> list[str]:
    """The plan's two header lines: where and when it starts, with the lunch, and what it costs (D100)."""
    spend, fare = sum(s["cost_gbp"] for s in stops), transport_gbp(stops)
    money = (f"about {_money(spend)} for food and entry" if spend else "free entry") + \
            (f", plus about {_money(fare)} transport" if fare else ", all on foot")
    lunch = ", including lunch" if any(s.get("lunch") for s in stops) else ""
    return [f"Start: {brief.start_name} at {brief.start_time} · {len(stops)} stops{lunch}", f"Costs: {money}"]


def plan_totals(stops: list[dict], travel: LondonEstimate) -> dict:
    """The app's summary line (D110): cost per person, walking between stops and the finish time.

    Walking counts the legs planned on foot, at the planner's walking pace (a GUESS, travel.py); walking inside a
    stop and to and from stations is not included, so the app says "between stops"."""
    spend, fare = sum(s["cost_gbp"] for s in stops), transport_gbp(stops)
    walk_min = sum(s["travel_min"] or 0 for s in stops if s.get("travel_mode") == "walk")
    return {"cost_gbp": round(spend + fare, 2), "spend_gbp": round(spend, 2), "transport_gbp": fare,
            "walk_min": round(walk_min), "walk_km": round(walk_min * travel.walking.speed_m_per_min / 1000, 1),
            "finish": stops[-1]["depart"] if stops else None}


def _header(label: str, brief: Brief, stops: list[dict]) -> list[str]:
    return [f"Plan {label}: {brief.day_label}", *summary_lines(brief, stops)]


def _stop_lines(s: dict) -> list[str]:
    parts = (_travel_line(s), s.get("approach"), s.get("what"),
             s.get("queue") and f"Allow about {int(s['queue'])} min to queue.", _best_line(s), _cost_line(s),
             s.get("rain_swap") and f"If it rains: {s['rain_swap']}")
    return [x for x in parts if x]


# ---- the app's view of a plan (D107) --------------------------------------------------

# The priors' labels are written for Abram's review ("... inspires them"); the app speaks to the person
APP_LABELS = {"aspiration_match": "one of your interests"}   # D110: plain words, not "fields that inspire you"


def stop_point(stop_id: str, by_id: dict[str, Moment], brief: Brief) -> Point | None:
    """Where a stop's map pin goes: the card's start, or for a flexible lunch slot, where it sits."""
    if stop_id == "lunch@start":
        return brief.start
    if stop_id.startswith("lunch@"):
        host = by_id.get(stop_id[len("lunch@"):])
        return host.end() if host else None
    m = by_id.get(_base(stop_id))
    return m.start() if m else None


def app_stop(s: dict, point: Point | None) -> dict:
    """One stop as the app shows it: the same wording as the Test B plans, plus a map pin and "chosen for"."""
    return {"moment_id": s["moment_id"], "key": s.get("key", s["moment_id"]), "title": s["title"],
            "arrive": s["arrive"], "depart": s["depart"],
            "travel_min": s["travel_min"], "travel_mode": s["travel_mode"], "travel_text": s.get("travel_text", ""),
            "approach": s["approach"], "what": s["what"], "queue_min": s.get("queue") or 0,
            "best_text": _best_line(s), "cost_gbp": s["cost_gbp"], "cost_kind": s["cost_kind"],
            "cost_text": _cost_line(s), "rain_swap": s["rain_swap"], "lunch": s["lunch"],
            "familiar": s.get("familiar", False), "rateable": not s["moment_id"].startswith("lunch@"),
            "worth_gbp": s.get("worth_gbp"),
            "approach_steps": s.get("approach_steps") or [],
            "best_light": s.get("best") or "",     # the card's light line, whatever the stop's time (D112)
            "best_window": next((f"{hhmm(a)}–{hhmm(b)}" for a, b in s.get("best_windows") or []), ""),
            "pin": point.model_dump() if point else None,
            "chosen_for": [APP_LABELS.get(w["feature"], w["label"]) for w in s.get("why") or []
                           if w["contribution"] > 0][:2],
            "why": s.get("why") or [], "lines": _stop_lines(s)}
