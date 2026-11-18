"""Plan value against the solver's time limit, on the machine's full CPU (Abram, 12 Nov, part 4).

    .venv/bin/python scripts/perf_budget.py benchmarks/performance/search_budget.json

The planner stops each solve on wall-clock time (`BRAIN_PLANNER_TIME_LIMIT_S`), so a server with a fraction of a CPU
searches for that fraction of the limit. Running the same requests with smaller limits on a full CPU shows what the
search budget buys: the same person and days as perf_study.py, one request each, limits 0.1 to 4 s. Provider keys are
not used; plans use the straight-line travel estimate.
"""
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fastapi.testclient import TestClient
from brain.api import create_app
from brain.config import DATA_DIR, Settings
import perf_study as ps
out = {}
for limit in (0.1, 0.2, 0.5, 1.0, 2.0, 4.0):
    with tempfile.TemporaryDirectory() as d:
        app = create_app(Settings(database_url=f"sqlite:///{d}/x.db", data_dir=DATA_DIR, admin_token="x",
                                  alert_webhook_url=None, planner_time_limit_s=limit))
        with TestClient(app) as c:
            for name, req in (("day", ps.DAY), ("one block", {**ps.DAY, "mine": ps.ONE_BLOCK}),
                              ("two blocks", {**ps.DAY, "mine": ps.TWO_BLOCKS}),
                              ("relaxed", {**ps.DAY, "relaxed": True, "stops": 4})):
                r = c.post("/v1/installs", json={"consent": {"version": "perf", "research": True}}).json()
                h = {"Authorization": "Bearer " + r["token"]}
                c.post("/v1/me/swipes", headers=h, json={"items": [{"item": i, "reaction": x} for i, x in ps.SWIPES]})
                c.post("/v1/me/conjoint", headers=h, json={"items": [{"task": t, "choice": ch} for t, ch in ps.CHOICES]})
                t0 = time.perf_counter(); p = c.post("/v1/me/plans", headers=h, json=req).json(); dt = time.perf_counter() - t0
                out.setdefault(name, {})[limit] = {"value": p.get("value"), "s": round(dt, 2),
                                                   "stops": [s["moment_id"] for s in p["stops"]], "status": p.get("solver_status")}
                print(name, limit, p.get("value"), round(dt, 2), p.get("solver_status"), flush=True)
json.dump(out, open(sys.argv[1], "w"), indent=1)
