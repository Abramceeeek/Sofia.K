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
  G3  every traveller gets a stop reflecting a place they loved: that place's own card, or one of the same kind
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
from brain.api import EXTRA_BY_FEEL  # noqa: E402
GATES = ("G1", "G2a", "G2b", "G2c", "G3", "G4", "G5", "G6", "G7", "G8")
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
    q = {"waits": [], "starts": [], "unused": {}, "extras": [], "ends": [], "travel": {}, "time": {}, "meals": [], "fit": [], "pins": {}, "stops": set(),
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
            said = any(ln.startswith(("Free time first:", "A gentle start:")) for ln in st.get("lines") or [])
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
        feel_day(d, t, stops, kinds, gaps, early, fails, q)
    if not reflected:
        fails["G3"].append("no stop reflects a loved place")
    fails["_free"] = stated
    fails["_q"] = q
    return fails


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
            if gap >= BREAK_MIN or k in ("meal", "rest", "mine"):
                run = 0
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
        dinner = any(str(st.get("key") or "").endswith("#dinner") or str(st["moment_id"]).startswith("dinner@")
                     for st in stops)
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
           "G7 a gentle pace kept · G8 no journey longer than its visit", "",
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
