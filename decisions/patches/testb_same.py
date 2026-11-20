"""The Test B pair for 10 fixed people, with the personal plan identified by its kind, not by its random label.
Printed as one sha256 per person and one overall, so base and patched code can be compared."""
import hashlib, json, sys, tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from brain.api import create_app
from brain.config import DATA_DIR, Settings

tmp = Path(tempfile.mkdtemp())
app = create_app(Settings(database_url=f"sqlite:///{tmp / 'b.db'}", data_dir=DATA_DIR, admin_token="x",
                          alert_webhook_url=None, planner_time_limit_s=float(sys.argv[1])))
people = []
for i in range(10):
    swipes = [(k, ["loved", "fine", "didnt_enjoy", "havent_been"][(i + k) % 4]) for k in (2, 3, 4, 6, 11, 12)]
    tasks = [(t, "AB"[(i * 7 + t) % 2]) for t in (2, 4, 6, 8, 9)]
    people.append((swipes, tasks, ["curious", "peaceful", "social", "adventurous"][i % 4]))
digests, uids = [], []
with TestClient(app) as c:
    for i, (swipes, tasks, why) in enumerate(people):
        r = c.post("/v1/installs", json={"consent": {"version": "2026-09", "research": True}},
                   headers={"CF-Connecting-IP": f"203.0.113.{i + 1}"})
        h = {"Authorization": "Bearer " + r.json()["token"]}
        c.post("/v1/me/swipes", headers=h, json={"items": [{"item": k, "reaction": x} for k, x in swipes]})
        c.post("/v1/me/conjoint", headers=h, json={"items": [{"task": t, "choice": x} for t, x in tasks]})
        c.put("/v1/me/profile", headers=h, json={"why_travel": [why], "budget_band": "20_40"})
        pair = c.post("/v1/me/testb/pair", headers=h, json={"mood": "explore", "company": "friends"}).json()
        uids.append(r.json()["user_id"])
    ex = c.get("/v1/admin/export", headers={"Authorization": "Bearer x"}).json()
    kinds = sorted({p["kind"] for p in ex["plans"]})
    for uid in uids:
        plans = sorted(((p["kind"], [s["moment_id"] for s in p["stops"]], [s.get("start") for s in p["stops"]])
                        for p in ex["plans"] if p["user_id"] == uid), key=str)
        digests.append(hashlib.sha256(json.dumps(plans).encode()).hexdigest()[:12])
print("plan kinds", kinds, "plans", len(ex["plans"]))
print(" ".join(digests))
print("overall", hashlib.sha256(" ".join(digests).encode()).hexdigest()[:16])
