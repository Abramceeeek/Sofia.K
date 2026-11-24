"""m326: the London gate. The six acceptance tests Abram set on 24 Nov, run on the six example travellers
(scripts/london_examples.py) through the real API, data and planner. London passes only when every test passes.

  G1  no unexplained gap over 20 min: arriving at a stop earlier than its own travel needs, or waiting before it
  G2  no day ending more than 45 min before the person's own end time
  G3  every traveller gets a stop reflecting a place they loved: that place's own card, or one of the same kind
  G4  no stop of a kind the person didn't enjoy (unless they loved or were fine with a place of that kind)
  G5  card rules hold: no stop below its minimum age for a party with children; a booking the card needs is said
  G6  every "Why" and best-time line is true of the stop: no internal wording, no best time the visit misses

SYNTHETIC PEOPLE: the gate measures the planner, never real travellers.
Run from brain/: `.venv/bin/python scripts/london_gate.py` → ../validation/london-examples/gate.md (and exit 1 on fail)
"""
from __future__ import annotations

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


def check(p: dict, trip: dict) -> dict[str, list[str]]:
    t, sw = p["trip"], p["swipes"]
    fails = {g: [] for g in ("G1", "G2", "G3", "G4", "G5", "G6")}
    loved_cards = {c for i, r in sw.items() if r == "loved" for c in ITEMS[i].get("cards") or []}
    loved_kinds = kinds_of({"loved"}, sw)
    bad_kinds = kinds_of({"didnt_enjoy"}, sw) - kinds_of({"loved", "fine"}, sw)
    reflected = False
    for d in trip["days"]:
        pl = d.get("plan")
        if not pl:
            continue
        stops = pl["stops"]
        prev_end = mins(t["day_start"])
        for st in stops:
            mid = base(st["moment_id"])
            arrive, depart, travel = mins(st["arrive"]), mins(st["depart"]), st.get("travel_min") or 0
            idle = arrive - travel - prev_end
            if idle > GAP_MAX:
                fails["G1"].append(f"{d['date']} {idle} min before {st['title'][:40]}")
            prev_end = depart
            if mid in loved_cards or KIND.get(mid) in loved_kinds:
                reflected = True
            if KIND.get(mid) in bad_kinds:
                fails["G4"].append(f"{d['date']} {st['title'][:40]} ({KIND.get(mid)})")
            card = CARDS.get(mid, {})
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
        if early > EARLY_MAX:
            fails["G2"].append(f"{d['date']} ends {early} min early")
    if not reflected:
        fails["G3"].append("no stop reflects a loved place")
    return fails


def main() -> int:
    tmp = tempfile.mkdtemp()
    settings = Settings(database_url=f"sqlite:///{tmp}/gate.db", data_dir=DATA_DIR, admin_token="x",
                        alert_webhook_url=None, planner_time_limit_s=1.0)
    rows, total = [], {g: 0 for g in ("G1", "G2", "G3", "G4", "G5", "G6")}
    detail = []
    with TestClient(create_app(settings)) as c:
        for p in ex.PEOPLE:
            r = c.post("/v1/installs", json={"channel": "stranger", "src": "gate",
                                             "consent": {"version": "2026-09", "research": True, "ai_processing": False}})
            h = {"Authorization": f"Bearer {r.json()['token']}"}
            c.put("/v1/me/profile", headers=h, json=p["profile"])
            c.post("/v1/me/swipes", headers=h, json={"items": [{"item": i, "reaction": x} for i, x in p["swipes"].items()]})
            trip = c.post("/v1/me/trips/days", headers=h, json={"start_date": ex.START.isoformat(), **p["trip"]}).json()
            f = check(p, trip)
            rows.append(f"| {p['key']} | " + " | ".join("✅" if not f[g] else f"❌ {len(f[g])}" for g in total) + " |")
            for g, items in f.items():
                total[g] += len(items)
                detail += [f"- **{p['key']} {g}:** {x}" for x in items]
    ok = not any(total.values())
    out = ["# The London gate (m326)", "",
           f"**{'PASSED' if ok else 'NOT PASSED'}.** Six synthetic travellers through the real planner "
           "(`scripts/london_gate.py`).", "",
           "G1 gap ≤ 20 min · G2 ends ≤ 45 min early · G3 a loved place reflected · G4 no disliked kind · "
           "G5 age and booking rules · G6 every Why and best-time line true", "",
           "| Traveller | G1 | G2 | G3 | G4 | G5 | G6 |", "|---|---|---|---|---|---|---|", *rows, "",
           "Failures in total: " + ", ".join(f"{g} {n}" for g, n in total.items()), "", "## Each failure", "", *detail]
    path = HERE.parents[1] / "validation" / "london-examples" / "gate.md"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[:12]))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
