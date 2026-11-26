"""m326: the London gate. The six acceptance tests Abram set on 24 Nov, run on the six example travellers
(scripts/london_examples.py) through the real API, data and planner. London passes only when every test passes.

  G1  no unexplained gap over 20 min: arriving at a stop earlier than its own travel needs, or waiting before it
  G2  (m346, Abram, 24 Nov: "I don't think the original G2 rule should remain a universal release blocker. However, I
      also don't want us simply weakening the gate") three checks in its place:
  G2a requested places: the main places a day (meals, rests and the person's own time apart) are the number they asked
      for, never fewer, and no more than their day feel adds (relaxed 0, balanced 2, full 4)
  G2b day feel: Relaxed adds nothing and leaves breathing room (no more than 3 h of visits without a break); Balanced
      has a meal, a change of pace, and ends no more than 90 min early; Full ends no more than 45 min early (the
      original G2) with dinner when the day runs to 19:30 or later, or says why not
  G2c remaining time: time left at the end of a day (over 45 min) is said on the plan, from the last stop's end to
      the day's end; total and longest free time, and whether it's intentional and useful, are reported
  G2 (original, kept for comparison, not a blocker): no day ending more than 45 min before the person's end time
  G9  (m350, Abram: "date-specific opening and closure rules") every stop is open for its whole visit on that date,
      by the card's own hours for that weekday and its dated changes (Christmas, early closings, refurbishments)
  G10 (m350, "actual sunset suitability") a stop that promises sunset in its title is there at sunset for that date:
      it starts within the card's own window around sunset and is still there when the sun sets (m352)
  G12 (m353, Abram, 25 Nov: "Make serious routing defects blockers… measure unnecessary distance, journey time and
      repeated crossings, with exceptions for genuinely loved experiences") no Tube or bus for a link walkable in
      about the same time (a walk of up to 30 min the Tube would shorten by less than 8); no stop along the stretch a
      ride covers on the same day (the boat past the Southbank, then back to it); no return to within 600 m of a place
      left earlier after going more than 3 km away. A place the person loved is exempt.
  G13 (m353, Abram: "A false or contradictory explanation is a release blocker… It must not invent a connection
      between two unrelated places") no reason that says the person loved a place the stop isn't, no "You loved X, and
      this has Y too" where Y isn't what X is (its tag below 2), and no "open until" for a place that's always open.
      Generic reasons ("suits most people") are measured, not blocking, with a target
  G14 (m353, Abram: "Unexplained changes to itinerary costs: release blocker") the trip's first day planned again
      with the other day feel (Relaxed for Full or Balanced, Full for Relaxed), as the app does when it's changed: if
      the day changes, the plan says what changed, and its cost when that changes by 50p or more
  G15 (m360, Abram, 26 Nov: "A substantial restaurant lunch followed by another substantial lunch 141 minutes later
      should be rejected") two substantial meals (a restaurant, a meal card, the day's lunch or dinner) start at least
      three hours apart. A market tasting, a bakery, a snack or coffee never counts. Judged here from the catalogue's
      own kinds, not by the planner's function
  G11 (m350, "daily travel budget by pace") no day's travel is more than 20 min over its pace's budget (gentle 60,
      medium or unstated 90, full-on 120 min): one journey's slack, never a day of crossing London

RELEASE BLOCKERS AND MEASUREMENTS (m350, Abram: "Distinguish absolute release blockers from quality measurements"):
G1, G2a-c and G3-G11 block: each is something a traveller would have to fix themselves, or would be misled by. The
quality measures below the tables are for a person to review, never pass or fail: named and generic meals, the same
stop for many travellers, going back across London (backtracking), total and longest unused time, the cost per person
and for the whole party against the budget, the original G2, and the extra places' strength.
  G3  every traveller gets a stop reflecting a place they loved: that place's own card, or one of the same kind
  G3b (m353, Abram, 25 Nov: "Loved places should be protected across the entire trip… Test that favourite places are
      considered across the complete trip") each place they loved that has a ready card, open on one of the trip's
      days, is in the trip at least once, when the trip has at least as many days as such places
  G4  no stop of a kind the person didn't enjoy (unless they loved or were fine with a place of that kind)
  G5  card rules hold: no stop below its minimum age for a party with children; a booking the card needs is said
  G6  every "Why" and best-time line is true of the stop: no internal wording, no best time the visit misses
  G7  the stated pace holds: someone who asked for a gentle day gets no strenuous stop (m329, Abram: "never make a
      traveller's experience worse just to make an automated test green")
  G8  no journey is longer than the visit it leads to (over 30 min): "without a disproportionate transfer" (m329)

Day Feel combinations (m346, Abram: "Test these combinations"): the six travellers cover gentle + relaxed, medium +
balanced, medium + full, full-on + full and gentle + balanced; two more runs give gentle + full (Jonas choosing Full)
and full-on + relaxed (the friends choosing Relaxed). London passes only when all eight pass.

SYNTHETIC PEOPLE: the gate measures the planner, never real travellers.
Run from brain/: `.venv/bin/python scripts/london_gate.py` → ../validation/london-examples/gate.md (and exit 1 on fail)
"""
from __future__ import annotations

from datetime import date

import importlib.util
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

import yaml  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from brain.api import create_app  # noqa: E402
from brain.config import DATA_DIR, Settings  # noqa: E402

spec = importlib.util.spec_from_file_location("london_examples", HERE / "london_examples.py")
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)

GAP_MAX, EARLY_MAX = 20, 45
CHILD_AGES = {"family": 8}            # the youngest in each example party, where children travel
ITEMS = yaml.safe_load((DATA_DIR / "swipe_items.yaml").read_text(encoding="utf-8"))["items"]
KIND = {k: v.get("type") for k, v in
        yaml.safe_load((DATA_DIR / "catalogue" / "london.yaml").read_text(encoding="utf-8"))["experiences"].items()}
from brain.moments import load_moments  # noqa: E402

WINDOWS = {m.id: m.windows() for m in load_moments(DATA_DIR / "moments")}
from brain.planner import PACE_TRAVEL_BUDGET  # noqa: E402
from brain.dayplan import EXTRA_MIN_P, spans_lunch  # noqa: E402
import brain.api as _api  # noqa: E402
EXTRA_BY_FEEL = getattr(_api, "EXTRA_BY_FEEL", {"relaxed": 0, "balanced": 2, "full": 4})   # so older commits can run it
from brain.sun import sunset as _sunset  # noqa: E402
GATES = ("G1", "G2a", "G2b", "G2c", "G3", "G3b", "G4", "G5", "G6", "G7", "G8", "G9", "G10", "G11", "G12", "G13", "G14",
         "G15")
from brain.reasons import PHRASE as _PHRASE, LINK_MIN as _LINK, _mid  # noqa: E402
from brain.travel import LondonEstimate as _LE  # noqa: E402
from brain.moments import Point as _Pt  # noqa: E402
from brain.planner import along_ride as _along, candidate_for as _cand  # noqa: E402
_EST = _LE()
from brain.api import BUDGET_BAND_GBP as BUDGET_BAND  # noqa: E402
TRAVEL_SLACK = 20                     # G11: minutes over the pace's budget a day may run
# m350 (Abram: "group budget and per-person versus party costs"): how many travel in each party, from the people's
# own descriptions (london_examples.py); children's prices aren't used yet, so the party's cost is per person x size
PARTY = {"sam": (1, 0), "priya": (2, 0), "family": (2, 2), "jonas": (1, 0), "friends": (4, 0), "margaret": (2, 0)}
from brain.dayplan import party_cost as _party  # noqa: E402
from brain.moments import load_moments as _load  # noqa: E402
MOMENTS = {m.id: m for m in _load(DATA_DIR / "moments")}
BREAK_MIN, RUN_MAX = 20, 180          # G2b relaxed: a break is 20 min or more; at most 3 h of visits without one
BALANCED_EARLY_MAX, DINNER_FROM = 90, 19 * 60 + 30
VARIANTS = [("jonas", "full", "Jonas (gentle) choosing Full"),
            ("friends", "relaxed", "The four friends (full-on) choosing Relaxed")]
# m331, m333: travel a day, by pace (minutes): the planner's own budget, so the gate measures what the planner aims at
TRAVEL_BUDGET = {**{k: v for k, v in PACE_TRAVEL_BUDGET.items() if k != "unstated"}, None: PACE_TRAVEL_BUDGET["unstated"]}
CARDS = {}
for f in (DATA_DIR / "moments").glob("*.yaml"):
    c = yaml.safe_load(f.read_text(encoding="utf-8"))
    CARDS[c["id"]] = c


def mins(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def base(mid: str) -> str:
    return mid.split("#")[0]


def kinds_of(reaction: set[str], swipes: dict) -> set[str]:
    return {t for i, r in swipes.items() if r in reaction for t in ITEMS[i].get("types", [])}


def check(p: dict, trip: dict, chance: dict | None = None) -> dict[str, list[str]]:
    t, sw = p["trip"], p["swipes"]
    fails = {g: [] for g in (*GATES, "G2orig")}
    loved_cards = {c for i, r in sw.items() if r == "loved" for c in ITEMS[i].get("cards") or []}
    loved_kinds = kinds_of({"loved"}, sw)
    bad_kinds = kinds_of({"didnt_enjoy"}, sw) - kinds_of({"loved", "fine"}, sw)
    reflected = False
    stated = []
    q = {"_band": p["profile"].get("budget_band"), "waits": [], "starts": [], "unused": {}, "extras": [], "ends": [], "travel": {}, "time": {}, "meals": [], "fit": [], "pins": {}, "stops": set(),
         "free": [], "feel": [],
         "titles": [d["title"] for d in trip["days"] if d.get("plan")]}
    for d in trip["days"]:
        pl = d.get("plan")
        if not pl:
            continue
        stops = pl["stops"]
        prev_end = mins(t["day_start"])
        kinds, gaps = [], []            # m346: each stop's kind, and the free time before it, for G2a-G2c
        for st in stops:
            mid = base(st["moment_id"])
            arrive, depart, travel = mins(st["arrive"]), mins(st["depart"]), st.get("travel_min") or 0
            idle = arrive - travel - prev_end
            gaps.append(max(0, idle))
            q["unused"][d["date"]] = q["unused"].get(d["date"], 0) + max(0, idle)
            first = st is stops[0]
            # m349: said where the app shows it (`notes`, under the stop on the day), not only in the text lines
            said = any(ln.startswith(("Free time first:", "A gentle start:")) for ln in st.get("notes") or [])
            if idle > GAP_MAX and not said:   # stated, not silent
                fails["G1"].append(f"{d['date']} {idle} min before {st['title'][:40]}")
            card = CARDS.get(mid, {})
            if first and idle > GAP_MAX:   # m331: a later start is measured on its own, not as a wait
                q["starts"].append((idle, st["title"][:40], d["date"]))
            elif said:
                stated.append(idle)
                why = "its best time" if st.get("best_text") else "its opening" if any(
                    lo == arrive for lo, _ in WINDOWS.get(mid, [])) else "the day's shape"
                q["waits"].append((idle, why, st["title"][:40], d["date"]))
            prev_end = depart
            q["travel"][d["date"]] = q["travel"].get(d["date"], 0) + travel
            fw = (st.get("feel_word") or "")
            meal_id = str(st["moment_id"])
            key_ = str(st.get("key") or "")   # m346: a named lunch or dinner ("m_flat_iron_covent_garden#lunch") is a meal
            kind = "meal" if st.get("lunch") or meal_id.startswith(("lunch@", "dinner@")) or "#dinner" in meal_id \
                or key_.endswith(("#lunch", "#dinner")) else \
                "rest" if fw in ("Resting", "Calm", "Quiet") else "explore" if mid.startswith("a_") else "visit"
            q["time"][kind] = q["time"].get(kind, 0) + (depart - arrive)
            kinds.append("mine" if meal_id.startswith("mine") else kind)
            if kind == "meal":
                q["meals"].append("generic" if str(st["moment_id"]).startswith(("lunch@", "dinner@")) else "named")
            if (((card.get("features") or {}).get("place") or {}).get("active", 0) >= 2
                    and set(t.get("feelings") or []) & {"peaceful", "restored"}):
                q["fit"].append(f"{d['date']} {st['title'][:40]} (strenuous, on a day to feel {', '.join(t['feelings'])})")
            if st.get("pin"):
                q["pins"].setdefault(d["date"], []).append((st["pin"]["lat"], st["pin"]["lon"], st["title"][:30]))
            q["stops"].add(mid)
            if mid in loved_cards or KIND.get(mid) in loved_kinds:
                reflected = True
            if KIND.get(mid) in bad_kinds:
                fails["G4"].append(f"{d['date']} {st['title'][:40]} ({KIND.get(mid)})")
            card = CARDS.get(mid, {})
            stay = depart - arrive
            if travel > 30 and travel > stay and mid not in loved_cards \
                    and not str(st["moment_id"]).startswith(("lunch@", "dinner@")):   # m331: a loved place is worth it
                fails["G8"].append(f"{d['date']} {travel} min to a {stay}-min visit: {st['title'][:36]}")
            m_ = MOMENTS.get(mid)
            if m_ is not None and not meal_id.startswith(("lunch@", "dinner@", "mine")):   # G9: open for the visit
                wd = date.fromisoformat(d["date"]).strftime("%a").lower()
                wins = m_.windows(wd, d["date"])
                if "sunset" in m_.title.lower() and m_.best_time.best_around_sunset:
                    # a sunset place's hours are its sunset for that date (m345), not the fixed window the card was
                    # written with; G10 checks it's there at sunset
                    sun0 = mins(_sunset(date.fromisoformat(d["date"])))
                    wins = [(sun0 + m_.best_time.best_around_sunset[0],
                             sun0 + m_.best_time.best_around_sunset[1] + (depart - arrive))]
                if not any(lo <= arrive and depart <= hi for lo, hi in wins):
                    fails["G9"].append(f"{d['date']} {st['title'][:40]} {st['arrive']}-{st['depart']}: not open "
                                       f"then ({', '.join(f'{lo // 60:02d}:{lo % 60:02d}-{hi // 60:02d}:{hi % 60:02d}' for lo, hi in m_.windows(wd, d['date'])) or 'closed'})")
                if "sunset" in m_.title.lower() and m_.best_time.best_around_sunset:   # G10
                    sun = mins(_sunset(date.fromisoformat(d["date"])))
                    lo, hi = m_.best_time.best_around_sunset
                    # m352 (review): there as the sun sets, not gone ten minutes before it
                    if not (sun + lo <= arrive <= sun + hi) or depart < sun:
                        fails["G10"].append(f"{d['date']} {st['title'][:40]} at {st['arrive']}, sunset "
                                            f"{_sunset(date.fromisoformat(d['date']))}")
            if p["profile"].get("activity") == "gentle" and ((card.get("features") or {}).get("place") or {}).get("active", 0) >= 2:
                fails["G7"].append(f"{d['date']} {st['title'][:40]} (strenuous, for a gentle day)")
            min_age = (card.get("rules") or {}).get("min_age")
            if p["key"] in CHILD_AGES and min_age and CHILD_AGES[p["key"]] < min_age:
                fails["G5"].append(f"{d['date']} {st['title'][:40]}: minimum age {min_age}")
            need = (card.get("best_time") or {}).get("book_ahead")
            if need and not (st.get("book_ahead") or any("ook" in ln for ln in st.get("lines") or [])):
                fails["G5"].append(f"{d['date']} {st['title'][:40]}: booking not said")
            texts = list(st.get("lines") or []) + [r["you"] for r in st.get("reasons") or []] + \
                [w if isinstance(w, str) else w.get("text", "") for w in (st.get("explain") or {}).get("why") or []]
            for ln in texts:
                if "visiting window" in ln or "card's" in ln:
                    fails["G6"].append(f"{d['date']} {st['title'][:30]}: \"{ln[:70]}\"")
                m = re.search(r"You're there at its best time, (\d\d:\d\d)[–-](\d\d:\d\d)", ln)
                n = re.search(r"best time, (\d\d:\d\d)[–-](\d\d:\d\d), starts while", ln)
                if (m and not (mins(m.group(1)) <= arrive <= mins(m.group(2)))) or \
                        (n and not (arrive < mins(n.group(1)) < depart)):
                    fails["G6"].append(f"{d['date']} {st['title'][:30]}: arrives {st['arrive']}, \"{ln[:60]}\"")
        early = mins(t["day_end"]) - prev_end
        q["unused"][d["date"]] = q["unused"].get(d["date"], 0) + max(0, early)
        if stops:
            q["ends"].append(f"{stops[-1]['title'][:38]} at {stops[-1]['depart']}")
        # m333 (Abram: "review every extra place added by the planner"): the places beyond the person's own number a
        # day, taken as the ones the person is least likely to rate Good, with that chance from the stored plan
        places = [st for st in stops if st.get("rateable") and "#dinner" not in str(st.get("key") or "")]
        if chance is not None:
            pg = {id(st): chance.get((d["date"], base(st["moment_id"]))) for st in places}
            weak = [st for st in places if pg[id(st)] is not None and pg[id(st)] < EXTRA_MIN_P]
            q["extras"].append((d["date"], len(places), int(t["stops_per_day"]), [
                (st["title"][:36], pg[id(st)], KIND.get(base(st["moment_id"])) or "") for st in weak]))
        if early > EARLY_MAX:
            fails["G2orig"].append(f"{d['date']} ends {early} min early")
        budget = TRAVEL_BUDGET.get(p["profile"].get("activity"), 90)   # G11 (unchanged: the whole journey)
        tot = pl.get("totals") or {}
        walk_, transit_ = tot.get("walk_min", 0), tot.get("transit_min", 0)
        # m355 (Abram: "Report separate components and identify which rules fail"): walking, Tube or bus, waits
        q.setdefault("journeys", []).append((d["date"], walk_, tot.get("walk_km", 0), transit_,
                                             tot.get("transit_legs", 0), tot.get("wait_min", 0), walk_ + transit_))
        if q["travel"].get(d["date"], 0) > budget + TRAVEL_SLACK:
            fails["G11"].append(f"{d['date']} {q['travel'][d['date']]} min of travel, budget {budget} "
                                f"({p['profile'].get('activity') or 'unstated'}): {walk_} min walking, {transit_} min "
                                f"by Tube or bus; mostly {'walking' if walk_ > transit_ else 'Tube or bus'}")
        q.setdefault("cost", []).append((d["date"], (pl.get("totals") or {}).get("cost_gbp")))
        ad, ch = PARTY.get(p["key"].split("+")[0], (1, 0))   # m353: the party at each person's own price
        q.setdefault("party", []).append(_party(stops, MOMENTS, ad, ch))
        feel_day(d, t, stops, kinds, gaps, early, fails, q)
        route_day(d, stops, loved_cards, fails)
        meals_day(d, stops, fails)
        why_day(d, stops, sw, fails, q)
    if not reflected:
        fails["G3"].append("no stop reflects a loved place")
    # G3b: each loved place with a ready card, open on a day of the trip, is in it once, given enough days
    planned = {base(st["moment_id"]) for d in trip["days"] if d.get("plan") for st in d["plan"]["stops"]}
    dates = [date.fromisoformat(d["date"]) for d in trip["days"] if d.get("plan")]
    sets = [(i, [c for c in ITEMS[i].get("cards") or [] if c in MOMENTS and MOMENTS[c].status == "ready"])
            for i, r in sw.items() if r == "loved"]
    sets = [(i, cs) for i, cs in sets if cs and any(MOMENTS[c].open_on(x.strftime("%a").lower(), x.isoformat())
                                                     for c in cs for x in dates)]
    if len(dates) >= len(sets):
        for i, cs in sets:
            if not set(cs) & planned:
                fails["G3b"].append(f"{ITEMS[i]['name'][:36]}, loved, not in the {len(dates)}-day trip")
    q["loved_no_card"] = [ITEMS[i]["name"] for i, r in sw.items() if r == "loved" and not ITEMS[i].get("cards")]
    fails["_free"] = stated
    fails["_q"] = q
    return fails


def why_day(d: dict, stops: list, sw: dict, fails: dict, q: dict) -> None:
    """m353: G13, reasons that are false or contradictory; and generic ones, counted."""
    names = {_mid(ITEMS[i]["name"]): i for i, r in sw.items() if r == "loved"}
    feature = {v: k for k, v in _PHRASE.items()}
    day = d["date"]
    for st in stops:
        if not st.get("rateable"):
            continue
        mid = base(st["moment_id"])
        texts = [r.get("you") or "" for r in st.get("reasons") or []]
        q.setdefault("why", []).append(not texts or texts[0].startswith(
            ("We don't know much", "Another that suits", "One more that most", "Also a good fit")))
        for t in texts:
            m1 = re.match(r"You loved (.+?)\.$", t)
            m2 = re.match(r"You loved (.+?), and this has (.+?) too\.$", t)
            if m2:
                i, f = names.get(m2.group(1)), feature.get(m2.group(2))
                tags = {**(ITEMS[i].get("place") or {}), **(ITEMS[i].get("moment") or {})} if i is not None else {}
                if i is None or f is None or (tags.get(f) or 0) < _LINK:
                    fails["G13"].append(f"{day} {st['title'][:30]}: \"{t[:70]}\"")
            elif m1 and "," not in m1.group(1):
                i = names.get(m1.group(1))
                if i is None or mid not in (ITEMS[i].get("cards") or []):
                    fails["G13"].append(f"{day} {st['title'][:30]}: \"{t[:70]}\" (not that place)")
    # m355: a paid rain option that says the day's budget still holds must be right, fares included
    band = BUDGET_BAND.get(q.get("_band"))
    total = ((d.get("plan") or {}).get("totals") or {}).get("cost_gbp")
    for st in stops:
        rid, text = st.get("rain_swap_id"), st.get("rain_swap") or ""
        if rid in MOMENTS and "fits your day's budget" in text and band is not None and total is not None and \
                total - float(st.get("cost_gbp") or 0) + float(MOMENTS[rid].cost_gbp or 0) > band + 0.5:
            fails["G13"].append(f"{day} rain option {MOMENTS[rid].title[:28]} said to fit the £{band} budget; it doesn't")
        if rid in MOMENTS and (MOMENTS[rid].cost_kind == "food" or (MOMENTS[rid].features.place.get("food") or 0) >= 2):
            fails["G13"].append(f"{day} a meal ({MOMENTS[rid].title[:28]}) offered as the rain option for {st['title'][:24]}")
    fa = (d.get("plan") or {}).get("free_after") or {}
    last = MOMENTS.get(base(stops[-1]["moment_id"])) if stops else None
    if fa.get("stay_on") and last and re.search(r"always open|24 hours", last.best_time.hours or "", re.I):
        fails["G13"].append(f"{day} \"open until\" for {last.title[:30]}, which is always open")
    if fa.get("stay_on") and last and (m_ := re.search(r"open until (\d\d:\d\d)", fa.get("text") or "")):
        wd = date.fromisoformat(day).strftime("%a").lower()
        arrive = mins(stops[-1]["arrive"])
        close = max((hi for lo, hi in last.windows(wd, day) if lo <= arrive <= hi), default=None)
        if close is not None and mins(m_.group(1)) != close:
            fails["G13"].append(f"{day} \"open until {m_.group(1)}\" for {last.title[:30]}, which closes at "
                                f"{close // 60:02d}:{close % 60:02d}")


MEAL_KINDS_G15 = {"restaurant"}
MEALS_APART_G15 = 180
_CARD_KINDS = None


def meals_day(d: dict, stops: list, fails: dict) -> None:
    """m360: G15, two substantial meals under three hours apart (a tasting or a snack never counts)."""
    global _CARD_KINDS
    if _CARD_KINDS is None:
        from brain.dayplan import load_card_kinds
        _CARD_KINDS = load_card_kinds(DATA_DIR / "catalogue" / "london.yaml")
    meals = []
    for st in stops:
        key, mid = str(st.get("key") or ""), str(st["moment_id"])
        if mid.startswith(("lunch@", "dinner@")) or key.endswith(("#lunch", "#dinner")) or st.get("lunch") or \
                _CARD_KINDS.get(base(mid)) in MEAL_KINDS_G15:
            meals.append((mins(st["arrive"]), st["title"][:36]))
    for (a, ta), (b, tb) in zip(meals, meals[1:]):
        if b - a < MEALS_APART_G15:
            fails["G15"].append(f"{d['date']} {tb} at {b // 60:02d}:{b % 60:02d}, {b - a} min after {ta}")


def route_day(d: dict, stops: list, loved: set, fails: dict) -> None:
    """m353: G12, the serious route defects a Londoner wouldn't make."""
    pins = [(_Pt(lat=st["pin"]["lat"], lon=st["pin"]["lon"]) if st.get("pin") else None) for st in stops]
    day = d["date"]
    for i, st in enumerate(stops):
        mid = base(st["moment_id"])
        if mid in loved or i == 0 or not pins[i] or not pins[i - 1]:
            continue
        if st.get("travel_mode") not in (None, "walk") and st.get("travel_min"):
            walk = _EST.walking.minutes(pins[i - 1], pins[i])
            if walk <= _EST.WALK_PREFER_MAX and walk <= (st["travel_min"] or 0) + _EST.WALK_PREFER_SLACK:
                fails["G12"].append(f"{day} {st['title'][:36]}: {st['travel_min']} min by Tube or bus, "
                                    f"{round(walk)} min on foot")
    rides = [(i, MOMENTS[base(st["moment_id"])]) for i, st in enumerate(stops)
             if base(st["moment_id"]) in MOMENTS and MOMENTS[base(st["moment_id"])].route]
    for i, m in rides:
        c = _cand(m, 0.0)
        for k, st in enumerate(stops):
            if k != i and pins[k] and base(st["moment_id"]) not in loved and _along(pins[k], c):
                fails["G12"].append(f"{day} {st['title'][:36]}: along the {m.title[:30]}'s own course, the same day")
    for j in range(len(stops)):
        for i in range(j - 1):
            if pins[i] and pins[j] and base(stops[j]["moment_id"]) not in loved and _km(
                    (pins[i].lat, pins[i].lon), (pins[j].lat, pins[j].lon)) < 0.6 and max(
                    (_km((pins[i].lat, pins[i].lon), (pins[k].lat, pins[k].lon)) for k in range(i + 1, j) if pins[k]),
                    default=0) > 3:
                fails["G12"].append(f"{day} back to {stops[j]['title'][:30]} after going over 3 km away")
                break


def feel_day(d: dict, t: dict, stops: list, kinds: list, gaps: list, early: int, fails: dict, q: dict) -> None:
    """m346: G2a (requested places), G2b (day feel) and G2c (remaining time) for one planned day."""
    feel = d.get("day_feel") or t.get("day_feel") or "balanced"
    win = d.get("window") or {"start": t["day_start"], "end": t["day_end"], "stops": t["stops_per_day"]}
    asked = int(win["stops"]) - (1 if spans_lunch(mins(win["start"]), mins(win["end"])) and int(win["stops"]) > 1 else 0)
    # a main place is any planned place but a meal, the person's own time, or a stop that is only a rest (the planner's
    # own "Resting" stops, m331); a quiet museum is a main place
    main_ = [st for st, k in zip(stops, kinds) if k not in ("meal", "mine") and st.get("rateable")
             and (st.get("feel_word") or "") != "Resting"]
    n, allow = len(main_), EXTRA_BY_FEEL[feel]
    day = d["date"]
    if n < asked:
        fails["G2a"].append(f"{day} {n} main places for the {asked} asked ({feel})")
    elif n > asked + allow:
        fails["G2a"].append(f"{day} {n} main places for the {asked} asked: more than {feel} adds ({allow})")
    pl = d["plan"]
    lines = [ln for st in stops for ln in st.get("lines") or []]
    if feel == "relaxed":
        if n > asked:
            fails["G2b"].append(f"{day} relaxed, but {n - asked} place(s) added")
        run, longest = 0, 0
        for st, k, gap in zip(stops, kinds, gaps):
            food = (CARDS.get(base(st["moment_id"]), {}).get("cost_kind") == "food")   # eating somewhere is a pause too
            if gap >= BREAK_MIN or k in ("meal", "rest", "mine") or food:
                run = 0
                if food:
                    continue
            if k in ("visit", "explore"):   # from arriving at the first place of the run: the journey there is apart
                run += mins(st["depart"]) - mins(st["arrive"]) + ((st.get("travel_min") or 0) if run else 0)
                longest = max(longest, run)
        if longest > RUN_MAX:
            fails["G2b"].append(f"{day} relaxed, but {longest} min of visits without a break")
    elif feel == "balanced":
        if spans_lunch(mins(win["start"]), mins(win["end"])) and "meal" not in kinds:
            fails["G2b"].append(f"{day} balanced, but no meal")
        if not (set(kinds) & {"rest", "explore", "meal"} or any(g >= BREAK_MIN for g in gaps)):
            fails["G2b"].append(f"{day} balanced, but no change of pace (a meal, a rest, a wander or free time)")
        if early > BALANCED_EARLY_MAX:
            fails["G2b"].append(f"{day} balanced, but ends {early} min early")
    else:
        if early > EARLY_MAX:
            fails["G2b"].append(f"{day} full, but ends {early} min early")
        # as the product counts it (dayplan.say_no_dinner): an evening food stop (Beigel Bake at 17:15) is the dinner
        dinner = any(str(st.get("key") or "").endswith("#dinner") or str(st["moment_id"]).startswith("dinner@")
                     or (st.get("cost_kind") == "food" and mins(st["arrive"]) >= 17 * 60 + 30 - 30) for st in stops)
        no_dinner_said = any("dinner" in ln.lower() and ("no " in ln.lower() or "budget" in ln.lower()) for ln in lines)
        if mins(win["end"]) >= DINNER_FROM and not dinner and not no_dinner_said:
            fails["G2b"].append(f"{day} full, to {win['end']}, but no dinner and no word on it")
    fa = pl.get("free_after")
    if early > EARLY_MAX and not fa:
        fails["G2c"].append(f"{day} {early} min left at the end, not said on the plan")
    elif fa and (fa["from"] != stops[-1]["depart"] or fa["until"] != win["end"]):
        fails["G2c"].append(f"{day} free time said {fa['from']}-{fa['until']}, but the day is "
                            f"{stops[-1]['depart']}-{win['end']}")
    periods = [g for g in gaps if g > BREAK_MIN] + ([early] if early > BREAK_MIN else [])
    said = not [x for x in fails["G2c"] if x.startswith(day)]   # mid-day and start periods are G1's, which must pass
    q["free"].append((day, sum(periods), max(periods, default=0), said,
                      "chosen (relaxed)" if feel == "relaxed" and periods else
                      "nothing strong enough to add" if fa else "waits for a time" if periods else "–",
                      bool(fa and fa.get("stay_on")) if fa else None))
    q["feel"].append((day, feel, n, asked))


def _km(a, b) -> float:
    import math
    dy = (a[0] - b[0]) * 111.2
    dx = (a[1] - b[1]) * 111.2 * math.cos(math.radians(a[0]))
    return (dx * dx + dy * dy) ** 0.5


def _similar(a: str, b: str) -> bool:
    wa, wb = set(re.findall(r"[a-z]+", a.lower())), set(re.findall(r"[a-z]+", b.lower()))
    return bool(wa and wb) and len(wa & wb) / len(wa | wb) >= 0.6


def quality(qual: list) -> list[str]:
    """m331 (Abram, 24 Nov): measures reviewed by a person, never pass or fail. ⚠ marks what needs a look."""
    out = ["## Quality measures (reviewed, not pass or fail)", "",
           "Free time is split by kind, as Abram asked: rest, meals and wandering are part of a good day; the waits "
           "are stated on the next stop, with what they wait for. Travel is compared with a day's budget for the "
           f"person's pace ({', '.join(f'{k or 'unstated'} {v} min' for k, v in TRAVEL_BUDGET.items())}).", "",
           "Unused time is the day's window with nothing planned: a later start, waits and an early end together "
           "(fewer is better; rest, meals and wandering are planned, so they don't count).", "",
           "| Traveller | Unused per day | Rest | Meals | Wandering | Waits (count, total, longest) | Later starts | "
           "Travel per day | Meals named | Titles |", "|---|---|---|---|---|---|---|---|---|---|"]
    notes, seen = [], {}
    for p, q in qual:
        pace = p["profile"].get("activity")
        budget = TRAVEL_BUDGET.get(pace, 90)
        per_day = ", ".join(f"{m} min{' ⚠' if m > budget else ''}" for m in q["travel"].values())
        waits = q["waits"]
        w = f"{len(waits)}, {sum(x[0] for x in waits)} min, {max((x[0] for x in waits), default=0)} min"
        named = q["meals"].count("named")
        food = "food" in p["profile"].get("fields", []) or any(
            p["swipes"].get(i) == "loved" for i in (3, 7, 14))
        meals = f"{named} of {len(q['meals'])}" + (" ⚠" if food and q["meals"] and not named else "")
        titles = q["titles"]
        rep = sum(1 for i in range(len(titles)) for j in range(i + 1, len(titles)) if _similar(titles[i], titles[j]))
        long_t = sum(len(x) > 80 for x in titles)
        tq = "ok" if not rep and not long_t else f"{rep} alike, {long_t} long ⚠"
        starts = ", ".join(f"{x[0]} min" for x in q["starts"]) or "none"
        unused = ", ".join(f"{m} min" for m in q["unused"].values())
        out.append(f"| {p['key']} | {unused} | {q['time'].get('rest', 0)} min | {q['time'].get('meal', 0)} min | "
                   f"{q['time'].get('explore', 0)} min | {w} | {starts} | {per_day} | {meals} | {tq} |")
        for x in sorted(waits, reverse=True)[:2]:
            notes.append(f"- **{p['key']}:** {x[0]} min before {x[2]} ({x[3]}), waiting for {x[1]}")
        notes += [f"- **{p['key']} fit ⚠:** {x}" for x in q["fit"]]
        for day, pins in q["pins"].items():   # back to a spot left earlier, after a long trip away
            for i in range(len(pins)):
                for j in range(i + 2, len(pins)):
                    if _km(pins[i], pins[j]) < 0.6 and max(_km(pins[i], pins[k]) for k in range(i + 1, j)) > 3:
                        notes.append(f"- **{p['key']} route ⚠:** {day} goes back to {pins[j][2]} after going "
                                     f"over 3 km away")
        for mid in q["stops"]:
            seen.setdefault(mid, []).append(p["key"])
    out += ["", "**Remaining time (G2c measures, m346):** each day's free time in periods over 20 min (a later "
                "start, waits and the end of the day), the longest, whether the plan says it, why it's there (chosen "
                "on a relaxed day; nothing strong enough to add; waiting for a place's time) and whether the plan "
                "offers something to do with it at the end of the day (staying on where they are):", "",
                "| Traveller | Day feel | Each day: main places / asked · free time · longest · said · why · useful |",
                "|---|---|---|"]
    for p, q in qual:
        cells = [f"{n}/{a} · {tot} min · {lg} min · {'yes' if said else 'no ⚠'} · {why} · "
                 f"{'–' if use is None else 'yes' if use else 'no'}"
                 for (_, _, n, a), (_, tot, lg, said, why, use) in zip(q["feel"], q["free"])]
        out.append(f"| {p['key']} | {q['feel'][0][1] if q['feel'] else '–'} | " + "; ".join(cells) + " |")
    out += ["", "**Journeys (m355, measured; G11 still judges the whole journey):** walking (minutes and km), Tube or "
                "bus (door to door: the walk to the station and the wait are inside the estimate; legs), the waits "
                "the day states, and the whole journey. ⚠ marks walking over 45 min a day for a gentle traveller with "
                "children, or Tube and bus over the pace's budget on their own.", "",
                "| Traveller | Pace | Each day: walk min · km · Tube/bus min (legs) · waits · whole journey |", "|---|---|---|"]
    for p, q in qual:
        pace = p["profile"].get("activity")
        kids = p["key"].split("+")[0] in CHILD_AGES
        b = TRAVEL_BUDGET.get(pace, 90)
        cells = [f"{w} · {km} km · {tr} ({lg}){' ⚠' if tr > b else ''} · {wt} · {tot}"
                 + (" ⚠" if kids and pace == "gentle" and w > 45 else "")
                 for _, w, km, tr, lg, wt, tot in q.get("journeys", [])]
        out.append(f"| {p['key']} | {pace or 'unstated'} | " + "; ".join(cells) + " |")
    from brain.api import BUDGET_BAND_GBP
    out += ["", "**Costs (m350, measured):** each day's cost per person (entry, food and fares, from the plan's own "
                "summary) against the person's daily budget, and for the whole party at each person's own price "
                "(m353: children's prices where the card's source gives them; otherwise the adult price, named). "
                "Fares are TfL's adult fares for everyone: children's fares aren't verified yet.", "",
                "| Traveller | Party | Budget a day | Each day: per person · whole party |", "|---|---|---|---|"]
    for p, q in qual:
        k = p["key"].split("+")[0]
        band = BUDGET_BAND_GBP.get(p["profile"].get("budget_band"))
        cells = [f"£{c:,.2f}{' ⚠' if band is not None and c is not None and c > band else ''} · £{pc['total_gbp']:,.2f}"
                 + (f" (children's price not known: {', '.join(t[:24] for t in pc['child_price_unknown'])})"
                    if pc["child_price_unknown"] else "")
                 if c is not None else "–" for (_, c), pc in zip(q.get("cost", []), q.get("party", []))]
        ad, ch = PARTY.get(k, (1, 0))
        out.append(f"| {p['key']} | {ad} adult{'s' if ad > 1 else ''}{f', {ch} children' if ch else ''} | "
                   f"{'£' + str(band) if band is not None else 'none'} | " + "; ".join(cells) + " |")
    gen = [g for _, q in qual for g in q.get("why", [])]
    out += ["", f"**Generic reasons (measured; target: none for a traveller who answered onboarding, m353):** "
                f"{sum(gen)} of {len(gen)} planned places give only a general reason (\"suits most people\")."]
    gaps_ = sorted({n for _, q in qual for n in q.get("loved_no_card", [])})
    out += ["", "**Loved places with no card yet** (catalogue gaps, measured): " + ("; ".join(gaps_) or "none"), ""]
    days_ = [(p["key"], *x) for p, q in qual for x in q["extras"]]
    extra_n = sum(max(0, n - asked) for _, _, n, asked, _ in days_)
    broken = [(k, d) for k, d, n, asked, weak in days_ if len(weak) > asked]
    out += ["", f"**Extra places** (Abram: \"it must match the person's actual preferences\"): {extra_n} places beyond "
                f"the number a day each person asked for. The rule: a day holds at most that number of places with "
                f"under a {EXTRA_MIN_P} chance of Good (the planner's own estimate), so every place beyond it is a "
                f"strong match. Days breaking it: {len(broken)}{' ⚠ ' + str(broken) if broken else ''}. The weaker "
                "places, within each day's own number:", ""]
    out += [f"- {k} {d} ({n} places, {asked} asked): " + "; ".join(f"{t} ({kd or 'no kind'}) {pg}" for t, pg, kd in weak)
            for k, d, n, asked, weak in days_ if weak]
    out += ["", "**How each day ends:** " + "; ".join(f"{p['key']}: " + ", ".join(q["ends"]) for p, q in qual)]
    allu = [m for _, q in qual for m in q["unused"].values()]
    out += ["", f"**Unused time, all {len(allu)} days:** {sum(allu)} min, a mean of "
                f"{round(sum(allu) / max(1, len(allu)))} min a day."]
    common = sorted(((len(v), k) for k, v in seen.items() if len(v) >= 3 and not k.startswith(("lunch@", "dinner@"))),
                    reverse=True)
    out += ["", "**The largest waits, and what they wait for:**", *notes, "",
            "**The same stop for 3 or more of the 6 travellers** (variety; fewer is better): "
            + (", ".join(f"{k} ({n})" for n, k in common) or "none"), ""]
    return out


RUNS = 3              # m333 (Abram, 24 Nov: "consistent configuration, repeatable runs and exact commit identifiers")
TIME_LIMIT_S = 1.0    # the solver's limit per search, as in production (BRAIN_PLANNER_TIME_LIMIT_S)


def chances(app, uid: str) -> dict:
    """The chance of Good or better the planner gave each stop (kept with the stored plan, m276, never sent)."""
    from brain import db
    from brain.explain import p_good
    pop = app.state.pop
    with app.state.Session() as s:
        rows = s.query(db.Plan).filter(db.Plan.user_id == uid).all()
        return {(r.date, base(st["moment_id"])): round(p_good(pop.scales["rating"], pop.cutpoints["rating"][1],
                                                            st["predicted"]), 2)
                for r in rows for st in r.stops if st.get("predicted") is not None}


def travellers() -> list[dict]:
    """The six travellers, then the two Day Feel combinations they don't cover (m346)."""
    by_key = {p["key"]: p for p in ex.PEOPLE}
    return list(ex.PEOPLE) + [{**by_key[k], "key": f"{k}+{feel}", "variant": label,
                               "trip": {**by_key[k]["trip"], "day_feel": feel}} for k, feel, label in VARIANTS]


def one_run() -> dict:
    """Every traveller once, through a fresh app and database."""
    tmp = tempfile.mkdtemp()
    settings = Settings(database_url=f"sqlite:///{tmp}/gate.db", data_dir=DATA_DIR, admin_token="x",
                        alert_webhook_url=None, planner_time_limit_s=TIME_LIMIT_S)
    rows, total, orig = [], {g: 0 for g in GATES}, {"six": 0, "all": 0}
    qual: list = []
    detail = []
    with TestClient(create_app(settings)) as c:
        for p in travellers():
            r = c.post("/v1/installs", json={"channel": "stranger", "src": "gate",
                                             "consent": {"version": "2026-09", "research": True, "ai_processing": False}})
            h, uid = {"Authorization": f"Bearer {r.json()['token']}"}, r.json()["user_id"]
            c.put("/v1/me/profile", headers=h, json=p["profile"])
            c.post("/v1/me/swipes", headers=h, json={"items": [{"item": i, "reaction": x} for i, x in p["swipes"].items()]})
            trip = c.post("/v1/me/trips/days", headers=h, json={"start_date": ex.START.isoformat(), **p["trip"]}).json()
            f = check(p, trip, chances(c.app, uid))
            first = next((d for d in trip["days"] if d.get("plan") and d["index"] == 0), None)
            if first:   # G14: the day planned again with the other day feel says what changed, its cost included
                other = "full" if (p["trip"].get("day_feel") or "balanced") == "relaxed" else "relaxed"
                again = c.post("/v1/me/trips/days", headers=h, json={
                    "start_date": ex.START.isoformat(), **p["trip"], "day_feel": other, "days": [0],
                    "exclude": [], "compare_to": {"0": first["plan"]["id"]}}).json()
                d2 = next((d for d in again.get("days", []) if d.get("plan")), None)
                if d2:
                    ch = d2["plan"].get("change")
                    same = [st["key"] for st in first["plan"]["stops"]] == [st["key"] for st in d2["plan"]["stops"]]
                    if not same and not ch:
                        f["G14"].append(f"{first['date']} planned again ({other}) without saying what changed")
                    elif ch and abs(ch["cost_after_gbp"] - ch["cost_before_gbp"]) >= 0.5 and "costs about" not in ch["text"]:
                        f["G14"].append(f"{first['date']} cost changed £{ch['cost_before_gbp']}→£{ch['cost_after_gbp']}, "
                                        "not said")
            f.pop("_free")
            qual.append((p, f.pop("_q")))
            g2 = f.pop("G2orig")
            orig["all"] += len(g2)
            orig["six"] += 0 if p.get("variant") else len(g2)
            rows.append(f"| {p['key']} | {p['trip'].get('day_feel') or 'balanced'} | " +
                        " | ".join("✅" if not f[g] else f"❌ {len(f[g])}" for g in total) +
                        f" | {len(g2) or '–'} |")
            for g, items in f.items():
                total[g] += len(items)
                detail += [f"- **{p['key']} {g}:** {x}" for x in items]
            detail += [f"- {p['key']} G2 (original, not a blocker): {x}" for x in g2]
    unused = sum(m for _, q in qual for m in q["unused"].values())
    waits = [w[0] for _, q in qual for w in q["waits"]]
    over = sum(1 for p, q in qual for m in q["travel"].values()
               if m > TRAVEL_BUDGET.get(p["profile"].get("activity"), 90))
    over_min = sum(max(0, m - TRAVEL_BUDGET.get(p["profile"].get("activity"), 90)) for p, q in qual
                   for m in q["travel"].values())
    days = sum(len(q["unused"]) for _, q in qual)
    return {"rows": rows, "total": total, "orig": orig, "qual": qual, "detail": detail, "unused": unused, "waits": waits,
            "over": over, "over_min": over_min, "days": days, "places": sum(len(q["stops"]) for _, q in qual)}


def main(runs: int = RUNS) -> int:
    import os
    results = [one_run() for _ in range(runs)]
    first = results[0]
    ok = all(not any(r["total"].values()) for r in results)
    rep = ["## Repeatability", "",
           f"{runs} runs of the same commit and settings (solver limit {TIME_LIMIT_S} s a search, {os.cpu_count()} "
           "CPUs). The solver stops at a time limit, so a run can differ slightly from the next; the tables below "
           "are run 1, and this table is every run.", "",
           "| Run | " + " | ".join(GATES) + " | G2 original (six; all eight) | Unused time | Waits mid-day | "
           "Days over the travel budget | Minutes over it | Different places |",
           "|---|" + "---|" * len(GATES) + "---|---|---|---|---|---|"]
    for k, r in enumerate(results, start=1):
        rep.append(f"| {k} | " + " | ".join(str(n) for n in r["total"].values()) +
                   f" | {r['orig']['six']}; {r['orig']['all']} | {r['unused']} min | {len(r['waits'])}, {sum(r['waits'])} min | {r['over']} of {r['days']} "
                   f"| {r['over_min']} min | {r['places']} |")
    out = ["# The London gate (m326)", "",
           f"Run on {date.today():%-d %b %Y}, from {ex.built_from()}.", "",
           f"**{'PASSED' if ok else 'NOT PASSED'}.** Six synthetic travellers, and two more Day Feel combinations, "
           "through the real planner (`scripts/london_gate.py`). London passes only when every check passes in every "
           "run.", "",
           "G1 gap ≤ 20 min · **G2a** the places asked for (meals apart), no more than the day feel adds · **G2b** the "
           "day matches Relaxed, Balanced or Full · **G2c** time left at the end is said on the plan · G3 a loved place "
           "reflected · G4 no disliked kind · G5 age and booking rules · G6 every Why and best-time line true · "
           "G7 a gentle pace kept · G8 no journey longer than its visit · **G9** open for the whole visit that date · "
           "**G10** a sunset stop at sunset · **G11** travel within 20 min of the pace's budget · **G12** no serious route "
           "defect (a walkable link by Tube, back over a ride's course, a return after going far away) · **G13** no false "
           "or contradictory reason · **G14** a change to the day says what it changed, its cost included · **G15** "
           "two substantial meals at least three hours apart (a tasting or a snack never counts)", "",
           "All of these block a release (m350). The measures further down are for a person to review.", "",
           "**G2 (original)** (no day ending more than 45 min early) is reported for comparison with the earlier "
           "reports, as Abram asked, and no longer blocks (m346).", "",
           "| Traveller | Day feel | " + " | ".join(GATES) + " | G2 original |",
           "|---|---|" + "---|" * len(GATES) + "---|",
           *first["rows"], "",
           "Failures in total (run 1): " + ", ".join(f"{g} {n}" for g, n in first["total"].items()) +
           f"; G2 original {first['orig']['six']} for the six travellers ({first['orig']['all']} with the two "
           "combinations)", "",
           *rep, "",
           *quality(first["qual"]),
           "**The test measures a good trip; it doesn't define one.** Never make a traveller's day worse to turn a "
           "check green (Abram, 24 Nov).", "", "## Each failure (run 1)", "", *first["detail"]]
    path = HERE.parents[1] / "validation" / "london-examples" / "gate.md"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[:12] + rep))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else RUNS))
