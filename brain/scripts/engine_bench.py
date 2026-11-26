"""m363 (Abram, 26 Nov, batch 8): the fixed engine bench. The person-to-place engine (`brain.match`, shadow mode) beside
the planner it will one day inform, for the same fixed travellers, dates, data, solver settings and code, so every
future version can be compared with this one. It changes nothing: the planner makes every plan, as it does in the app.

SYNTHETIC PEOPLE ONLY. Each traveller is invented and answers onboarding through the app's own API, so the engine sees
exactly what the app would know about them. Nothing here is evidence about real travellers or real enjoyment.

Run from brain/: `.venv/bin/python scripts/engine_bench.py`
→ ../validation/engine-bench/<commit>.json (every raw result) and <commit>.md (the report).

What's fixed (and recorded in the output): the travellers below; Friday 4 and Saturday 5 December 2026; the planner's
1.0 s limit; the data snapshot (a hash of every file the engine reads); the Brain commit.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
sys.path.insert(0, str(HERE))

import yaml  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import london_examples as ex  # noqa: E402  (the gate's six travellers and built_from)
from brain.api import create_app  # noqa: E402
from brain.config import DATA_DIR, Settings  # noqa: E402
from brain.moments import load_moments  # noqa: E402
from brain.reasons import LEAN, PHRASE  # noqa: E402

DAYS = (date(2026, 12, 4), date(2026, 12, 5))     # a Friday and a Saturday, as the gate
SOLVER_S = 1.0
SNAPSHOT = ["moments/*.yaml", "catalogue/*.yaml", "priors.yaml", "swipe_items.yaml", "aspiration.yaml",
            "popularity.yaml", "onboarding.yaml", "conjoint_design.csv"]
# The places shown for every traveller: one place, many people (Abram: "Can ODYS explain why its recommendation changes
# for each person, using evidence rather than assumptions?")
SHOWCASE = ["m_borough_market_graze", "m_bm_great_court", "m_park_break_hyde", "m_tate_modern", "m_sky_garden",
            "m_liberty_timber_galleries"]


def pick(prefer: str):
    """A rule for the "this or that" days: the option whose description has `prefer` (else the other's lack of it)."""
    def choose(t: dict) -> str:
        a, b = t["A"], t["B"]
        if prefer == "quiet":
            return "A" if "mostly quiet" in a and "mostly quiet" not in b else "B" if "mostly quiet" in b else "N"
        if prefer == "cheap":
            ca, cb = (float(re.search(r"£(\d+)", x).group(1)) for x in (a, b))
            return "A" if ca < cb else "B" if cb < ca else "N"
        if prefer == "packed":
            return "A" if "5 stops" in a else "B" if "5 stops" in b else "N"
        return "N"
    return choose


# The archetypes (m363: "review whether they adequately cover different interests and traveller needs"). Each is what
# a person told the app, never a label about them. Swipe places by number (data/swipe_items.yaml).
ARCHETYPES = [
    dict(key="food", who="A food enthusiast",
         profile=dict(based="london", company="friends", budget_band="40_70", activity="medium", chronotype="night",
                      fields=["food"], why_travel=["excited", "curious"]),
         swipes={3: "loved", 14: "loved", 7: "loved", 4: "fine", 12: "fine"}, choices=None,
         must_go=("m_bm_great_court",)),
    dict(key="quiet", who="A quiet traveller who avoids crowds",
         profile=dict(based="london", company="solo", budget_band="20_40", activity="gentle", chronotype="morning",
                      fields=["nature"], why_travel=["peaceful", "restored"]),
         swipes={6: "loved", 16: "loved", 7: "didnt_enjoy", 1: "didnt_enjoy", 3: "fine"}, choices="quiet"),
    dict(key="history", who="A history enthusiast",
         profile=dict(based="uk", home_city="York", company="partner", budget_band="40_70", activity="medium",
                      chronotype="morning", fields=["history_culture"], why_travel=["curious"]),
         swipes={4: "loved", 1: "loved", 12: "loved", 7: "fine", 14: "fine"}, choices=None),
    dict(key="kids", who="A family with children of 6 and 9",
         profile=dict(based="uk", home_city="Reading", company="family", budget_band="20_40", activity="gentle",
                      chronotype="morning", fields=["nature"], why_travel=["connected"]),
         swipes={6: "loved", 12: "loved", 2: "fine", 4: "fine", 15: "havent_been"}, choices=None, children=(6, 9)),
    dict(key="budget", who="A budget traveller",
         profile=dict(based="uk", home_city="Leicester", company="solo", budget_band="under_20", activity="medium",
                      chronotype="neither", fields=[], why_travel=["curious"]),
         swipes={6: "loved", 9: "loved", 3: "fine", 8: "fine"}, choices="cheap"),
    dict(key="art", who="An art lover",
         profile=dict(based="london", company="solo", budget_band="40_70", activity="medium", chronotype="morning",
                      fields=[], why_travel=["curious", "restored"]),
         swipes={8: "loved", 12: "fine", 4: "fine", 3: "fine", 7: "didnt_enjoy"}, choices=None),
    dict(key="views", who="A photographer who loves views",
         profile=dict(based="uk", home_city="Bath", company="solo", budget_band="40_70", activity="full_on",
                      chronotype="neither", fields=["nature"], why_travel=["excited"]),
         swipes={9: "loved", 11: "loved", 13: "loved", 5: "loved", 4: "didnt_enjoy"}, choices="packed"),
    dict(key="new", who="Someone who hasn't answered anything yet",
         profile=dict(based="london"), swipes={}, choices=None),
]
GROUP = ("food", "quiet", "history")   # a shared trip: three different people, from their own accounts
# Must-go trials (M3): a day planned with one place the traveller asked for (the planner's own "must include"), on the
# Friday, 10:00-17:00 from Charing Cross, 3 places. Some are easy, some are against their tastes, one is a hard rule.
MUST_GO = [("food", "m_bm_great_court"), ("quiet", "m_tate_modern"), ("history", "m_borough_market_graze"),
           ("views", "m_sky_garden"), ("kids", "m_diana_playground"), ("art", "m_wahaca_southbank"),
           ("sam", "m_bm_great_court")]   # Sam didn't enjoy the British Museum: the hard rule must hold


def snapshot_hash() -> str:
    h = hashlib.sha256()
    for pattern in SNAPSHOT:
        for f in sorted(DATA_DIR.glob(pattern)):
            h.update(f.relative_to(DATA_DIR).as_posix().encode())
            h.update(f.read_bytes())
    return h.hexdigest()[:16]


def install(c) -> dict:
    r = c.post("/v1/installs", json={"channel": "stranger", "src": "engine-bench",
                                     "consent": {"version": "2026-09", "research": True, "ai_processing": False}})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def onboard(c, h, person: dict) -> None:
    if person.get("profile"):
        assert c.put("/v1/me/profile", headers=h, json=person["profile"]).status_code == 204
    if person.get("swipes"):
        c.post("/v1/me/swipes", headers=h, json={"items": [{"item": i, "reaction": x} for i, x in person["swipes"].items()]})
    if person.get("choices"):
        ob = c.get("/v1/onboarding", headers=h).json()
        rule = pick(person["choices"])
        items = [{"task": t["task"], "choice": rule(t)} for t in ob["conjoint_tasks"]]
        assert c.post("/v1/me/conjoint", headers=h, json={"items": items}).status_code == 204


def stop_claims(st: dict) -> list[tuple[str, str]]:
    """The features a planned stop's shown reasons claim for it: (the claim's text, the feature)."""
    by_phrase = {v: k for k, v in PHRASE.items()}
    by_lean = {v: k for k, v in LEAN.items()}
    out = []
    for r in st.get("reasons") or []:
        text = r.get("you") or ""
        for phrase, f in by_phrase.items():
            if re.search(rf"this has {re.escape(phrase)}( too)?\.", text):
                out.append((text, f))
    line = st.get("match") or ""
    if "your lean towards " in line:
        tail = line.split("your lean towards ", 1)[1].split(" and your ")[0]
        for lean, f in by_lean.items():
            if re.search(rf"\b{re.escape(lean)}\b", tail):
                out.append((line, f))
    return out


def main() -> int:
    # the bench makes one install per synthetic traveller in its own in-memory app, so the per-address install
    # limit (10 an hour, ops.LIMITS) is raised for this run only; the product's limits are untouched
    import brain.ops as ops
    ops.LIMITS["install"] = (1000, 3600)
    tmp = tempfile.mkdtemp()
    settings = Settings(database_url=f"sqlite:///{tmp}/bench.db", data_dir=DATA_DIR, admin_token="x",
                        alert_webhook_url=None, planner_time_limit_s=SOLVER_S)
    cards = {m.id: m for m in load_moments(DATA_DIR / "moments")}
    built = ex.built_from()
    commit = (built.split("commit ")[1].split()[0] if "commit " in built else "unknown")
    raw = {"commit": built, "snapshot": snapshot_hash(), "days": [d.isoformat() for d in DAYS], "solver_s": SOLVER_S,
           "bench": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16], "travellers": {}, "group": None,
           "must_go": []}
    people = [dict(p, kind="gate") for p in ex.PEOPLE] + [dict(p, kind="archetype") for p in ARCHETYPES]
    heads = {}
    with TestClient(create_app(settings)) as c:
        for p in people:
            h = install(c)
            heads[p["key"]] = h
            onboard(c, h, p)
            kids = p.get("children") or tuple((p.get("trip") or {}).get("party", {}).get("children", []))
            must = p.get("must_go", ())
            per_day = {}
            for d in DAYS:
                q = f"/v1/me/matches?date={d.isoformat()}"
                if must:
                    q += "&must_go=" + ",".join(must)
                if kids:
                    q += "&children=" + ",".join(str(k) for k in kids)
                per_day[d.isoformat()] = c.get(q, headers=h).json()
            trip = p.get("trip") or dict(nights=1, feelings=list(p["profile"].get("why_travel", [])), day_start="10:00",
                                         day_end="18:00", stops_per_day=3, day_feel="balanced",
                                         **({"party": {"adults": 2, "children": list(kids)}} if kids else {}))
            r = c.post("/v1/me/trips/days", headers=h, json={"start_date": DAYS[0].isoformat(), **trip})
            plan = r.json() if r.status_code == 201 else {"days": [], "error": r.text[:200]}
            raw["travellers"][p["key"]] = {"who": p["who"], "kind": p["kind"], "must_go": list(must),
                                           "children": list(kids), "matches": per_day, "plan": plan}
        for key, place in MUST_GO:
            kids = T_kids = tuple(next((p.get("children") or () for p in people if p["key"] == key), ()))
            body = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_name": "Charing Cross", "start_time": "10:00",
                    "end_time": "17:00", "date": DAYS[0].isoformat(), "stops": 3, "intent": {"must_do": place}}
            pl = c.post("/v1/me/plans", headers=heads[key], json=body).json()
            q = f"/v1/me/matches?date={DAYS[0].isoformat()}&must_go={place}" + (
                "&children=" + ",".join(map(str, T_kids)) if kids else "")
            m = next((x for x in c.get(q, headers=heads[key]).json()["matches"] if x["place"] == place), {})
            raw["must_go"].append({"traveller": key, "place": place, "class": m.get("class"),
                                   "restrictions": m.get("restrictions", []),
                                   "planned": any(str(st.get("moment_id", "")).split("#")[0] == place
                                                  for st in pl.get("stops", [])),
                                   "stops": [st.get("title") for st in pl.get("stops", [])]})
        g = c.post("/v1/me/groups", headers=heads[GROUP[0]], json={"start_date": DAYS[0].isoformat(), "nights": 1,
                                                                    "per_day": 3, "consent": True,
                                                                    "share_preferences": True}).json()
        for key in GROUP[1:]:
            c.post("/v1/me/groups/join", headers=heads[key], json={"code": g["code"], "consent": True,
                                                                   "share_preferences": key == "history"})
        raw["group"] = {"members": list(GROUP), "plan": c.post(f"/v1/me/groups/{g['id']}/plan",
                                                               headers=heads[GROUP[0]]).json()}
    out_dir = HERE.parents[1] / "validation" / "engine-bench"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{commit}.json").write_text(json.dumps(raw, indent=1, ensure_ascii=False), encoding="utf-8")
    (out_dir / f"{commit}.md").write_text(report(raw, cards), encoding="utf-8")
    print(out_dir / f"{commit}.md")
    return 0


def report(raw: dict, cards: dict) -> str:
    """The comparison, every measure apart (m363 work package F). Raw numbers; no average stands alone."""
    T = raw["travellers"]
    d0 = raw["days"][0]
    lines = [f"# Engine bench: {raw['commit']}", "",
             f"Bench `{raw.get('bench', '?')}` · data snapshot `{raw['snapshot']}` · days {', '.join(raw['days'])} · solver {raw['solver_s']} s · "
             f"{len(T)} synthetic travellers ({sum(v['kind'] == 'gate' for v in T.values())} from the gate, "
             f"{sum(v['kind'] == 'archetype' for v in T.values())} archetypes) and one shared trip.", "",
             "**Shadow mode:** the engine (`brain.match`) judges every ready place for each traveller; the planner makes "
             "every plan exactly as the app does, and nothing here changed a plan. **Scores are provisional ranking "
             "measures, never chances** (m363). **Synthetic travellers only:** nothing here is evidence about real "
             "people or real enjoyment.", ""]
    # 1. classes per traveller
    lines += ["## 1. How the engine classes every ready place (Friday)", "",
              "| Traveller | Must-go | Strong | Good discovery | Low confidence | Poor | Not suitable |", "|---|---|---|---|---|---|---|"]
    for k, v in T.items():
        cl = v["matches"][d0]["classes"]
        lines.append(f"| {k} | {cl['must_go']} | {cl['strong_match']} | {cl['good_discovery']} | {cl['low_confidence']} | "
                     f"{cl['poor_match']} | {cl['not_suitable']} |")
    # 2. one place, many people
    lines += ["", "## 2. One place, many people (Friday)", "",
              "For each place, what the engine says for each traveller, and why. A reason appears only with evidence on "
              "both sides (the traveller's own answer, and a feature that defines the place); otherwise the class says "
              "what's missing.", ""]
    for pid in SHOWCASE:
        if pid not in cards:
            continue
        lines += [f"### {cards[pid].display_title()}", "", "| Traveller | Class | Score | Why, or why not |", "|---|---|---|---|"]
        for k, v in T.items():
            m = next((x for x in v["matches"][d0]["matches"] if x["place"] == pid), None)
            if not m:
                continue
            neg = m["negatives"][0] if m["negatives"] else None
            why = m["reason"] or m["against"] or ("; ".join(m["restrictions"]) if m["restrictions"] else
                                                  "not enough evidence about this traveller for this place" if m["class"] == "low_confidence"
                                                  else f"no reason strong on both sides; held back most by {neg['label']} "
                                                       f"({neg['traveller']}; the place: {neg['place']})" if neg
                                                  else "no reason strong on both sides")
            lines.append(f"| {k} | {m['class'].replace('_', ' ')} | {m['score']:+.2f} | {why} |")
        lines.append("")
    # 3. the planner's plans against the engine
    lines += ["## 3. The planner's own plans, judged by the engine", "",
              "Each planned stop (meals and the person's own time apart) against the engine's class for that "
              "traveller on that day.", "",
              "| Traveller | Planned | Must-go | Strong | Good | Low confidence | Poor | **Not suitable** | Strong not planned |",
              "|---|---|---|---|---|---|---|---|---|"]
    totals = Counter()
    unsupported = []
    for k, v in T.items():
        cnt, planned_ids = Counter(), set()
        for day in v["plan"].get("days", []):
            for part in ("before", "plan"):
                pl = day.get(part) or {}
                cls_of = {x["place"]: x["class"] for x in v["matches"].get(day["date"], {}).get("matches", [])}
                for st in pl.get("stops", []):
                    mid = str(st.get("moment_id") or "").split("#")[0]
                    if not st.get("rateable") or mid not in cls_of:
                        continue
                    planned_ids.add(mid)
                    cnt[cls_of[mid]] += 1
                    for text, f in stop_claims(st):
                        tag = int(cards[mid].tag(f) or 0) if mid in cards else 0
                        if tag < 2:
                            unsupported.append((k, cards[mid].display_title() if mid in cards else mid, text, f, tag))
        strong = [x for x in v["matches"][d0]["matches"] if x["class"] == "strong_match" and x["place"] not in planned_ids]
        n = sum(cnt.values())
        totals.update(cnt)
        totals["planned"] += n
        lines.append(f"| {k} | {n} | {cnt['must_go']} | {cnt['strong_match']} | {cnt['good_discovery']} | "
                     f"{cnt['low_confidence']} | {cnt['poor_match']} | **{cnt['not_suitable']}** | "
                     f"{len(strong)}{': ' + '; '.join(x['title'][:30] for x in strong[:2]) if strong else ''} |")
    lines += ["", f"**All travellers:** {totals['planned']} planned stops: {totals['must_go']} must-go, "
              f"{totals['strong_match']} strong, {totals['good_discovery']} good discovery, {totals['low_confidence']} low "
              f"confidence, {totals['poor_match']} poor, **{totals['not_suitable']} not suitable** (the engine and the "
              "planner apply the same hard rules, so this must be 0).", ""]
    # 4. explanations shown today, against the evidence rule
    lines += ["## 4. The reasons the app shows today, against the evidence rule", "",
              f"A shown reason claims a feature for the stop (\"this has a sense of awe\", \"your lean towards views\"). "
              f"The rule (m363, work package D): the stop's own tag for that feature must be 2, its defining value. "
              f"**Claims on a weaker tag: {len(unsupported)}.**", ""]
    if unsupported:
        lines += ["| Traveller | Stop | Claim | Feature | Stop's tag |", "|---|---|---|---|---|"]
        seen = set()
        for k, title, text, f, tag in unsupported:
            if (title, text) in seen:
                continue
            seen.add((title, text))
            lines.append(f"| {k} | {title[:44]} | {text[:90]} | {f} | {tag} |")
        lines.append("")
    # 5. measures
    lines += ["## 5. Measures (work package F)", ""]
    lines += measures(raw, cards)
    # 6. the shared trip
    gp = raw["group"]["plan"]
    lines += ["", "## 6. The shared trip (the group planner, unchanged), judged for each member", "",
              f"Members: {', '.join(raw['group']['members'])} (the food enthusiast started it; the history enthusiast "
              "agreed to be named; the quiet traveller didn't).", "",
              "| Day | Place | " + " | ".join(raw["group"]["members"]) + " |", "|---|---|" + "---|" * len(raw["group"]["members"])]
    for i, day in enumerate(gp.get("days", []), 1):
        for st in day:
            mid = next((c for c in cards if st["id"].endswith(c.replace("m_", "").replace("_", "-"))), None)
            row = []
            for key in raw["group"]["members"]:
                ms = {x["place"]: x for x in T[key]["matches"][d0]["matches"]}
                x = ms.get(mid) if mid else None
                row.append(x["class"].replace("_", " ") if x else "–")
            lines.append(f"| {i} | {st['title'][:48]} | " + " | ".join(row) + " |")
    lines += ["", "The group planner doesn't use the engine yet (m362: the group work waits for it). A shared place that "
              "is low confidence or poor for a member is where the engine would change it.", ""]
    return "\n".join(lines) + "\n"


def measures(raw: dict, cards: dict) -> list[str]:
    T = raw["travellers"]
    d0 = raw["days"][0]
    out = []
    # diversity: top 10 overlap between travellers with answers
    tops = {k: [x["place"] for x in v["matches"][d0]["matches"] if x["class"] in ("must_go", "strong_match", "good_discovery")][:10]
            for k, v in T.items() if k != "new"}
    pairs = [(a, b) for i, a in enumerate(tops) for b in list(tops)[i + 1:]]
    jac = [len(set(tops[a]) & set(tops[b])) / max(1, len(set(tops[a]) | set(tops[b]))) for a, b in pairs]
    out.append(f"- **Diversity:** mean overlap of two travellers' top 10 (must-go, strong, good) is "
               f"**{sum(jac) / len(jac):.0%}** over {len(pairs)} pairs (highest {max(jac):.0%}, lowest {min(jac):.0%}). "
               "Lower is more personal.")
    # must-go (M3): the planner's own "must include", one place a day
    mg = raw.get("must_go", [])
    feasible = [x for x in mg if x["class"] == "must_go"]
    ruled = [x for x in mg if x["class"] == "not_suitable"]
    out.append(f"- **Must-go preservation:** of {len(feasible)} feasible requests, the planner kept "
               f"**{sum(x['planned'] for x in feasible)}**. Of {len(ruled)} the engine rules out, the planner planned "
               f"**{sum(x['planned'] for x in ruled)}**, and the engine said why for {sum(bool(x['restrictions']) for x in ruled)}. "
               "Where they disagree, it's a request for a place the traveller said they didn't enjoy: the planner lets "
               "the request win (`dayplan`: `disliked_ids - {must_do}`), the engine doesn't. Abram's decision.")
    for x in mg:
        out.append(f"  - {x['traveller']} asked for `{x['place']}`: engine **{(x['class'] or '?').replace('_', ' ')}**"
                   f"{' (' + '; '.join(x['restrictions']) + ')' if x['restrictions'] else ''}; planned: "
                   f"**{'yes' if x['planned'] else 'no'}** ({'; '.join(s[:28] for s in x['stops'] if s)})")
    # dislikes
    bad = 0
    for k, v in T.items():
        nots = {x["place"] for x in v["matches"][d0]["matches"] if any("exclusion" in r or "planner's rule" in r for r in x["restrictions"])}
        bad += sum(str(st.get("moment_id", "")).split("#")[0] in nots
                   for day in v["plan"].get("days", []) for st in (day.get("plan") or {}).get("stops", []))
    out.append(f"- **Explicit dislikes avoided:** {bad} planned stops at a place the traveller (or the planner's rule) "
               "excludes. Must be 0.")
    # evidence and confidence
    allm = [x for v in T.values() for x in v["matches"][d0]["matches"]]
    rec = [x for x in allm if x["class"] in ("strong_match", "good_discovery", "must_go")]
    with_reason = sum(bool(x["reason"]) for x in rec)
    out.append(f"- **Evidence quality:** {with_reason} of {len(rec)} recommended places ({with_reason / max(1, len(rec)):.0%}) "
               "have a reason strong on both sides; the rest are recommended on the score alone, and say nothing.")
    checked = sum(bool(x["confidence"]["place_checked"]) for x in allm)
    out.append(f"- **Place facts:** {checked} of {len(allm)} judgements ({checked / max(1, len(allm)):.0%}) rest on a "
               "place with checked facts (hours, price…); every tag is set by hand on the card (an inference).")
    low = Counter(k for k, v in T.items() for x in v["matches"][d0]["matches"] if x["class"] == "low_confidence")
    out.append("- **Low confidence, per traveller:** " + ", ".join(f"{k} {low.get(k, 0)}" for k in T) + ".")
    out.append("- **Calibration readiness:** none. There are no real ratings, so no score can be checked against "
               "outcomes. `scripts/evaluate_export.py` is ready for the first real export (`validation/stage2-sample-size.md`).")
    # per type
    out.append("- **By traveller type:** see §1 and §3; the archetypes that differ most from the population are where "
               "low confidence and poor matches cluster.")
    return out


if __name__ == "__main__":
    sys.exit(main())
