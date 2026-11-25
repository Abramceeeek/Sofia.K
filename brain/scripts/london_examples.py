"""m324: example London trips from the real Brain, for review by people and by other AI models.

SYNTHETIC PEOPLE: each person below is invented, with the onboarding answers written out. The plans are exactly what
the Brain returns for those answers (the same code and data as the app), printed in the order and words the app
shows. Nothing is edited by hand. They are examples to judge the product by, never evidence about real travellers.

Run from brain/: `.venv/bin/python scripts/london_examples.py` → ../validation/london-examples/examples.md
"""
from __future__ import annotations

import sys
import tempfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

import yaml  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from brain.api import create_app  # noqa: E402
from brain.config import DATA_DIR, Settings  # noqa: E402

START = date(2026, 12, 4)   # a Friday
ITEMS = yaml.safe_load((DATA_DIR / "swipe_items.yaml").read_text(encoding="utf-8"))["items"]
WORDS = {"loved": "Loved it", "fine": "It was fine", "didnt_enjoy": "Didn't enjoy it", "havent_been": "Haven't been"}

# m346 (Abram, 24 Nov): each trip carries its day feel. Abram named three: Margaret and Alan and Jonas Relaxed, Sam
# Full; Claude chose the rest (Priya and Dan and the family Balanced, the four friends Full), logged in m346.
PEOPLE = [
    dict(key="sam", who="Sam, 29, travelling alone from Manchester for a weekend; loves food, on a budget",
         profile=dict(based="uk", home_city="Manchester", company="solo", budget_band="20_40", activity="medium",
                      chronotype="night", fields=["food"], why_travel=["excited", "curious"]),
         swipes={3: "loved", 14: "loved", 7: "loved", 4: "didnt_enjoy", 6: "fine", 13: "havent_been"},
         trip=dict(nights=1, feelings=["excited", "curious"], day_start="11:00", day_end="20:00", stops_per_day=3, day_feel="full")),
    dict(key="priya", who="Priya and Dan, a couple in their 30s from Leeds; history and museums, mid budget",
         profile=dict(based="uk", home_city="Leeds", company="partner", budget_band="40_70", activity="medium",
                      chronotype="morning", fields=["history_culture"], why_travel=["curious", "connected"]),
         swipes={4: "loved", 12: "loved", 1: "loved", 3: "fine", 15: "didnt_enjoy", 7: "didnt_enjoy"},
         trip=dict(nights=2, feelings=["curious", "connected"], day_start="09:30", day_end="18:00", stops_per_day=3, day_feel="balanced",
                   party=dict(adults=2))),
    dict(key="family", who="A family of four (two children, 8 and 11) from Bristol; parks and boats, a gentle pace",
         profile=dict(based="uk", home_city="Bristol", company="family", budget_band="20_40", activity="gentle",
                      chronotype="morning", fields=["nature"], why_travel=["connected", "restored"]),
         swipes={6: "loved", 2: "loved", 11: "loved", 4: "fine", 7: "didnt_enjoy", 9: "havent_been"},
         trip=dict(nights=1, feelings=["connected", "restored"], day_start="10:00", day_end="17:00", stops_per_day=3, day_feel="balanced",
                   party=dict(adults=2, children=[8, 11]))),
    dict(key="jonas", who="Jonas, who lives in London and needs a quiet day to recharge; no plans to spend much",
         profile=dict(based="london", company="solo", budget_band="under_20", activity="gentle", chronotype="morning",
                      fields=["nature"], why_travel=["peaceful", "restored"]),
         swipes={16: "loved", 13: "loved", 6: "loved", 1: "didnt_enjoy", 9: "didnt_enjoy", 8: "fine"},
         trip=dict(nights=0, feelings=["peaceful", "restored"], day_start="10:00", day_end="18:00", stops_per_day=3, day_feel="relaxed")),
    dict(key="friends", who="Four friends in their 20s from Glasgow; views, markets and a lively evening",
         profile=dict(based="uk", home_city="Glasgow", company="friends", budget_band="40_70", activity="full_on",
                      chronotype="night", fields=["food"], why_travel=["excited", "connected"]),
         swipes={7: "loved", 9: "loved", 5: "loved", 15: "loved", 3: "fine", 4: "didnt_enjoy"},
         trip=dict(nights=1, feelings=["excited", "connected"], day_start="11:00", day_end="21:00", stops_per_day=4, day_feel="full",
                   party=dict(adults=4))),
    dict(key="margaret", who="Margaret and Alan, retired, from Norwich; art and the river, unhurried, happy to spend",
         profile=dict(based="uk", home_city="Norwich", company="partner", budget_band="70_plus", activity="gentle",
                      chronotype="morning", fields=["history_culture"], why_travel=["restored", "curious"]),
         swipes={8: "loved", 4: "loved", 2: "loved", 15: "didnt_enjoy", 7: "didnt_enjoy", 13: "fine"},
         trip=dict(nights=2, feelings=["restored", "curious"], day_start="10:00", day_end="17:00", stops_per_day=2, day_feel="relaxed",
                   party=dict(adults=2))),
]


def built_from() -> str:
    """m331 (Abram: "keep each plan tied to its Brain commit"): the commit these plans came from, and whether the
    Brain's code or data had changes not yet committed."""
    import subprocess
    here = Path(__file__).resolve().parent.parent
    try:
        rev = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], cwd=here, capture_output=True, text=True,
                             check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "src", "data"], cwd=here, capture_output=True,
                               text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "an unknown Brain commit"
    return f"Brain commit {rev}" + (" with uncommitted changes" if dirty else "")


def shared_trip(c, heads: dict) -> list[str]:
    """m358: a trip planned together from three of the people's own accounts (each with their own answers above). Sam
    starts it and agrees to be named; Priya and Dan's account joins and agrees; Jonas joins without agreeing to be
    named, so he's counted, never named. What each member's app shows, for Sam's account."""
    g = c.post("/v1/me/groups", headers=heads["sam"], json={"start_date": START.isoformat(), "nights": 1, "per_day": 3,
                                                             "consent": True, "share_preferences": True}).json()
    for key, named in (("priya", True), ("jonas", False)):
        r = c.post("/v1/me/groups/join", headers=heads[key], json={"code": g["code"], "consent": True,
                                                                   "share_preferences": named})
        assert r.status_code == 201, r.text
    out = ["## A shared trip: Sam, Priya and Dan, and Jonas, planning together", "",
           "Each joined from their own account, with the answers above. Sam started it (Member A, agreed to be named); "
           "Priya and Dan's account joined as Member B (agreed); Jonas joined as Member C and didn't agree to be named. "
           "The app shows places for each day and why each is there; there are no times or routes yet.", ""]
    for key in ("sam", "priya", "jonas"):
        r = c.post(f"/v1/me/groups/{g['id']}/plan", headers=heads[key])
        assert r.status_code == 200, r.text
        plan = r.json()
        if key == "sam":
            for i, day in enumerate(plan["days"], 1):
                out.append(f"### Day {i}")
                for st in day:
                    out += [f"**{st['title']}**", f"- Why: {st['why']}", ""]
            for n in plan["notes"]:
                out.append(f"> {n}")
            out.append("")
        out.append(f"- {plan['group']['you']} sees: \"For you: {plan['your_share']}.\"")
    out += ["", "---", ""]
    return out


def main() -> int:
    tmp = tempfile.mkdtemp()
    settings = Settings(database_url=f"sqlite:///{tmp}/examples.db", data_dir=DATA_DIR, admin_token="x",
                        alert_webhook_url=None, planner_time_limit_s=1.0)
    out = ["# ODYS: example London trips", "",
           f"Made by `scripts/london_examples.py` on {date.today():%-d %b %Y}, from {built_from()} (no app build: "
           "the planner is called directly).", "",
           "**Synthetic people.** Each person is invented. Their onboarding answers are listed, and the plans are "
           "exactly what ODYS's planner returns for them, in the words the app shows. Nothing was edited by hand. "
           "These are for judging the product, not evidence about real travellers.", "",
           f"Trips start on Friday {START.day} December 2026. No weather forecast is used here, and no place to stay "
           "is chosen, so each day starts and ends at Charing Cross, the app's London centre.", ""]
    heads = {}
    with TestClient(create_app(settings)) as c:
        for p in PEOPLE:
            r = c.post("/v1/installs", json={"channel": "stranger", "src": "examples",
                                             "consent": {"version": "2026-09", "research": True, "ai_processing": False}})
            h = {"Authorization": f"Bearer {r.json()['token']}"}
            heads[p["key"]] = h
            assert c.put("/v1/me/profile", headers=h, json=p["profile"]).status_code == 204
            c.post("/v1/me/swipes", headers=h, json={"items": [{"item": i, "reaction": x} for i, x in p["swipes"].items()]})
            t = p["trip"]
            r = c.post("/v1/me/trips/days", headers=h, json={"start_date": START.isoformat(), **t})
            assert r.status_code == 201, r.text
            trip = r.json()
            learned = c.get("/v1/me/summary", headers=h).json().get("items", [])
            out += [f"## {p['who']}", "", "**What they told ODYS:**"]
            pr = p["profile"]
            out.append(f"- Company: {pr.get('company')}; budget a day: {pr.get('budget_band')}; pace: {pr.get('activity')}; "
                       f"{pr.get('chronotype')} person; interests: {', '.join(pr.get('fields', [])) or 'none'}")
            out.append(f"- How the trip should feel: {', '.join(t['feelings'])}")
            out.append("- Places they know: " + "; ".join(f"{ITEMS[i]['name']}: {WORDS[x]}" for i, x in p["swipes"].items()))
            out.append(f"- Trip: {t['nights'] + 1} day(s), {t['day_start']}–{t['day_end']}, {t["stops_per_day"]} places a day, days to feel {t.get("day_feel") or "balanced"}")
            if learned:
                out.append("- \"So far, I've learned\": " + " ".join(i["text"] for i in learned[:6]))
            out.append("")
            for d in trip["days"]:
                out.append(f"### {d['title']} ({d['date']})")
                for part in ("before", "plan"):
                    pl = d.get(part)
                    if not pl:
                        continue
                    if pl.get("feel_line"):
                        out.append(f"*{pl['feel_line']}*")
                    for line in pl.get("summary") or []:
                        out.append(f"> {line}")
                    t = pl.get("totals") or {}
                    if t.get("cost_gbp") is not None:   # m337: what the app's top line says (each price is per person)
                        out.append(f"> In the app: £{t['cost_gbp']:,.2f} per person, entry, food and fares; finishes at "
                                   f"{t.get('finish')}")
                    if (pa := pl.get("party")):   # m356: each traveller and the whole party, as the app says it
                        each = "; ".join(f"{x['label']} £{x['cost_gbp']:,.2f}" for x in pa["travellers"])
                        out.append(f"> For all {len(pa['travellers'])} of you: about £{pa['total_gbp']:,.2f} ({each}). "
                                   + " ".join(pa.get("notes") or []))
                    if (fa := pl.get("free_after")):   # m346: the time left at the end, as the app says it
                        out.append(f"> Free time: {fa['text']}")
                    out.append("")
                    for st in pl["stops"]:
                        head = f"**{st.get('arrive', '')}–{st.get('depart', '')} · {st['title']}**"
                        if st.get("feel_word"):
                            head += f" · _{st['feel_word']}_"
                        out.append(head)
                        for line in st.get("lines") or []:
                            out.append(f"- {line}")
                        if st.get("book_ahead"):                       # the app shows it on the stop
                            out.append(f"- Book ahead: {st['book_ahead']}")
                        for rsn in (st.get("reasons") or [])[:2]:      # what the app shows under "Why this?"
                            out.append(f"- Why: {rsn['you']}")
                        for w in (st.get("explain") or {}).get("why") or []:
                            out.append(f"- Why: {w if isinstance(w, str) else w.get('text', '')}")
                        out.append("")
                if not d.get("plan") and not d.get("before"):
                    out.append("_(Nothing planned this day.)_")
                out.append("")
            out.append("---")
            out.append("")
        out += shared_trip(c, heads)
    path = HERE.parents[1] / "validation" / "london-examples" / "examples.md"
    path.write_text("\n".join(out), encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
