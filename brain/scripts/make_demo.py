"""The apps' sample data for the CI screenshots (app/Sources/Demo, read by both apps), made by the real Brain.

Run from brain/ with the venv: `.venv/bin/python scripts/make_demo.py [YYYY-MM-DD]` (the day it's "today"; default:
today in London). Committed after the 19 Oct review, which found the old hand-kept files out of step with the Brain
(a plan 12 days ahead with a forecast, flights landing at 02:50 London time, a Paddington arrival at 04:18).

- **Your day:** next Saturday, so it matches the "Sat" chip on Plan a day. The weather line is a made-up Met Office
  reply (no key here), shaped like the real one, so the screenshots show where the line goes; at 5 days ahead it is
  the daily outlook, as the live Brain would show it.
- **The trip:** two weeks ahead from Tashkent, with the labelled sample flights and stays (no provider keys here).
  The first flight sets the trip's first and last day, as TripLogic.demoTrip expects.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
import tempfile
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from brain.api import create_app
from brain.config import DATA_DIR, Settings
from brain.weather import Forecast

DEMO = Path(__file__).resolve().parents[2] / "app" / "Sources" / "Demo"
ANDROID_EXAMPLE = Path(__file__).resolve().parents[2] / "android" / "app" / "src" / "main" / "assets" / "demo"


def fake_met(day: dt.date):
    """A Met Office reply for the demo only: hourly for the next 48 h, daily for the week (made up)."""
    now = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
    hourly = {"features": [{"properties": {"timeSeries": [
        {"time": (now + dt.timedelta(hours=i)).strftime("%Y-%m-%dT%H:%MZ"), "screenTemperature": 13.0,
         "probOfPrecipitation": 20} for i in range(48)]}}]}
    days = [now.date() + dt.timedelta(days=i) for i in range(-1, 7)]
    daily = {"features": [{"properties": {"timeSeries": [
        {"time": f"{d.isoformat()}T00:00Z", "dayMaxScreenTemperature": 14.0, "dayProbabilityOfPrecipitation": 30}
        for d in days]}}]}
    return lambda url, headers, params: hourly if url.endswith("hourly") else daily


def main(today: dt.date) -> None:
    saturday = today + dt.timedelta(days=(5 - today.weekday()) % 7 or 7)
    with tempfile.TemporaryDirectory() as d:
        s = Settings(database_url=f"sqlite:///{d}/demo.db", data_dir=DATA_DIR, admin_token="x", alert_webhook_url=None,
                     planner_time_limit_s=1.0)
        app = create_app(s)
        with TestClient(app) as c:
            app.state.forecast = Forecast("demo", fetch=fake_met(saturday))
            r = c.post("/v1/installs", json={"consent": {"version": "demo", "research": True}}).json()
            h = {"Authorization": "Bearer " + r["token"]}
            ob = c.get("/v1/onboarding", headers=h).json()
            c.post("/v1/me/swipes", headers=h, json={"items": [{"item": 2, "reaction": "loved"},
                   {"item": 3, "reaction": "didnt_enjoy"}, {"item": 11, "reaction": "loved"}]})
            c.post("/v1/me/conjoint", headers=h, json={"items": [{"task": t, "choice": ch} for t, ch in
                   [(2, "B"), (4, "A"), (6, "B"), (8, "B"), (9, "B")]]})
            c.put("/v1/me/profile", headers=h, json={"fields": ["history_culture"], "budget_band": "20_40",
                                                      "why_travel": ["curious", "peaceful"]})
            plan = c.post("/v1/me/plans", headers=h, json={"start": {"lat": 51.507819, "lon": -0.126137},
                          "start_name": "Charing Cross station", "date": saturday.isoformat()}).json()
            example = c.get("/v1/example-day").json()
            summary = c.get("/v1/me/summary", headers=h).json()     # the same person as the plan, so screens agree
            # Build 2: the blind pair, before and after the choice
            pair = c.post("/v1/me/testb/pair", headers=h, json={"mood": "explore", "company": "friends"}).json()
            dump = c.get("/v1/admin/export", headers={"Authorization": "Bearer x"}).json()
            mine = next(p["label"] for p in dump["plans"]
                        if p["kind"] == "personal" and (p["intent"] or {}).get("testb_pair"))
            fits = {"1": 3, "2": 3, mine: 4}
            pair_done = c.post("/v1/me/testb/pair/feedback", headers=h, json={
                "chosen": mine, "fit_1": fits["1"], "fit_2": fits["2"], "why": "More walking by the river."}).json()
            # D120, D122: a trip from Tashkent two weeks ahead; the first flight sets its first and last day
            start = today + dt.timedelta(days=14)
            flights = c.post("/v1/trips/flights", headers=h, json={
                "origin": "TAS", "depart_date": start.isoformat(),
                "return_date": (start + dt.timedelta(days=6)).isoformat(), "adults": 1}).json()
            f0 = flights["results"][0]
            first = dt.date.fromisoformat(f0["outbound"]["arrive_at"][:10])
            last = dt.date.fromisoformat(f0["inbound"]["depart_at"][:10])
            stays = c.post("/v1/trips/stays", headers=h, json={"checkin": first.isoformat(),
                           "checkout": last.isoformat(), "adults": 1}).json()
            st0 = stays["results"][0]
            days = c.post("/v1/me/trips/days", headers=h, json={
                "start_date": first.isoformat(), "nights": (last - first).days, "feelings": ["curious", "peaceful"],
                "stay": {"lat": st0["lat"], "lon": st0["lon"]}, "stay_name": st0["name"], "day_start": "09:30",
                "day_end": "19:00", "stops_per_day": 3, "travel_light": True,
                "arrive": {"mode": "flight", "place": "LHR", "time": f0["outbound"]["arrive_at"][11:16]},
                "leave": {"mode": "flight", "place": "LHR", "time": f0["inbound"]["depart_at"][11:16]}}).json()
            places = [x for q in ("tashkent", "samarkand", "london", "manchester", "istanbul", "dubai")
                      for x in c.get(f"/v1/trips/places?q={q}", headers=h).json()]
    out = {"demo_onboarding": ob, "demo_plan": plan, "example_day": example, "demo_summary": summary,
           "demo_pair": pair, "demo_pair_done": pair_done, "demo_trip_days": days, "demo_flights": flights,
           "demo_stays": stays, "demo_places": places}
    for name, obj in out.items():
        (DEMO / f"{name}.json").write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (ANDROID_EXAMPLE / "example_day.json").write_text((DEMO / "example_day.json").read_text(encoding="utf-8"),
                                                      encoding="utf-8")
    print("plan:", plan["date"], plan.get("weather", {}).get("line"))
    print("  ", [(x["title"][:32], x["arrive"], x.get("best_window")) for x in plan["stops"]])
    print("flight:", f0["outbound"]["depart_at"], "->", f0["outbound"]["arrive_at"], "|",
          f0["inbound"]["depart_at"], "->", f0["inbound"]["arrive_at"])
    print("trip:", [(x["index"], x["date"], [(l["slot"], l.get("depart"), l.get("arrive")) for l in x["legs"]])
                    for x in days["days"]])


if __name__ == "__main__":
    main(dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1
         else dt.datetime.now(ZoneInfo("Europe/London")).date())
