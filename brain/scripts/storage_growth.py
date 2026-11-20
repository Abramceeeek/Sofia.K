"""m306: how much database storage each tester adds. The real Brain on a scratch PostgreSQL, never Render.

    python brain/scripts/storage_growth.py <testers> <scratch database URL>

for example `20 postgresql+psycopg://postgres@/odys?host=/tmp&port=55433`. It creates the tables in that (empty)
database, runs simulated testers through a whole round (onboarding, the Test B pair, two day plans, a four-night
trip, ratings) and prints `pg_database_size` after the first and the last, with the largest tables and row counts.
Measured on 20 Nov: about 79 KB per tester (decisions/database-before-6-dec.md, "Storage").
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from brain.api import create_app
from brain.config import DATA_DIR, Settings

URL = sys.argv[2]
eng = create_engine(URL)
def size():
    with eng.connect() as c:
        db = c.execute(text("select pg_database_size(current_database())")).scalar()
        tabs = c.execute(text("select relname, pg_total_relation_size(c.oid) from pg_class c join pg_namespace n "
                              "on n.oid=c.relnamespace where n.nspname='public' and c.relkind='r' order by 2 desc")).all()
    return db, tabs
app = create_app(Settings(database_url=URL, data_dir=DATA_DIR, admin_token="x", alert_webhook_url=None, planner_time_limit_s=0.2))
DAY = {"start": {"lat": 51.507819, "lon": -0.126137}, "start_name": "Charing Cross station", "date": "2026-12-05"}
out = {}
with TestClient(app) as c:
    base, _ = size(); out["empty_schema_bytes"] = base
    n_testers = int(sys.argv[1])
    for i in range(n_testers):
        h = {"Authorization": "Bearer " + c.post("/v1/installs", json={"consent": {"version": "app-2026-10-02", "research": True}}, headers={"CF-Connecting-IP": f"203.0.113.{i+1}"}).json()["token"]}
        c.post("/v1/me/swipes", headers=h, json={"items": [{"item": k, "reaction": r} for k, r in [(2,"loved"),(3,"fine"),(4,"didnt_enjoy"),(6,"loved"),(11,"havent_been"),(12,"fine")]]})
        c.post("/v1/me/conjoint", headers=h, json={"items": [{"task": t, "choice": ch} for t, ch in [(2,"A"),(4,"B"),(6,"A"),(8,"B"),(9,"A")]]})
        c.put("/v1/me/profile", headers=h, json={"why_travel": ["curious", "peaceful"], "fields": ["history_culture"], "budget_band": "20_40"})
        c.post("/v1/me/answers", headers=h, json={"items": [{"question": "best_hour", "text": "x" * 400}]})
        for k in range(20):
            c.post("/v1/me/events", headers=h, json={"name": "screen", "props": {"screen": f"s{k}", "ms": "1234"}})
        pair = c.post("/v1/me/testb/pair", headers=h, json={"mood": "explore", "company": "friends"})
        plans = [c.post("/v1/me/plans", headers=h, json=DAY).json() for _ in range(2)]
        c.post("/v1/me/trips/days", headers=h, json={"start_date": "2026-12-05", "nights": 4, "stay": {"lat": 51.5111, "lon": -0.1221}, "stay_name": "A stay", "day_start": "10:00", "day_end": "18:00", "stops_per_day": 3})
        for p in plans:
            for st in [s for s in p.get("stops", []) if s.get("rateable")][:5]:
                c.post("/v1/me/ratings", headers=h, json={"plan_id": p["id"], "moment_id": st["moment_id"], "rating": 4, "would_bring": True})
        if i in (0, n_testers - 1):
            out[f"after_{i+1}_testers_bytes"] = size()[0]
    db, tabs = size()
    out["tables_top"] = [(t, n) for t, n in tabs[:8]]
    with eng.connect() as cc:
        out["rows"] = {t: cc.execute(text(f'select count(*) from "{t}"')).scalar() for t, _ in tabs}
print(json.dumps(out, indent=1))
