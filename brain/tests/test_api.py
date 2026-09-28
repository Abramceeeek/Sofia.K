import shutil

import pytest
import yaml
from fastapi.testclient import TestClient

from brain.api import create_app
from brain.config import Settings

from conftest import DATA


@pytest.fixture
def client(tmp_path, test_moments):
    data = tmp_path / "data"
    (data / "moments").mkdir(parents=True)
    for f in ("priors.yaml", "onboarding.yaml", "conjoint_design.csv"):
        shutil.copy(DATA / f, data / f)
    shutil.copy(DATA / "moments" / "m_southken_nhm_reveal.yaml", data / "moments")
    for m in test_moments:
        (data / "moments" / f"{m.id}.yaml").write_text(yaml.safe_dump(m.model_dump(by_alias=True)))
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", data_dir=data,
                        admin_token="admin-secret", alert_webhook_url=None, planner_time_limit_s=0.3)
    with TestClient(create_app(settings)) as c:
        yield c


def install(client, **kw):
    body = {"channel": "stranger", "src": "test", "consent": {"version": "2026-09", "research": True,
                                                            "ai_processing": False}, **kw}
    r = client.post("/v1/installs", json=body)
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}, r.json()["user_id"]


ADMIN = {"Authorization": "Bearer admin-secret"}


def test_consent_is_required(client):
    r = client.post("/v1/installs", json={"consent": {"version": "x", "research": False}})
    assert r.status_code == 400


def test_unknown_token_is_rejected(client):
    assert client.get("/v1/onboarding", headers={"Authorization": "Bearer nope"}).status_code == 401


def test_onboarding_serves_swipes_tasks_and_questions(client):
    h, _ = install(client)
    r = client.get("/v1/onboarding", headers=h).json()
    assert len(r["conjoint_tasks"]) == 10
    ids = {c["id"] for c in r["swipe_cards"]}
    assert "m_southken_nhm_reveal" in ids and "t_view" in ids
    assert r["open_questions"][0]["key"] == "best_hour"


def test_full_flow_answers_weights_plan_rating_and_deletion(client):
    h, uid = install(client)
    # swipes and "this or that": always avoid the rainy plan (D95), otherwise take the milder one
    assert client.post("/v1/me/swipes", headers=h, json={"items": [
        {"moment_id": "t_museum", "reaction": "loved"}, {"moment_id": "t_market", "reaction": "didnt_enjoy"},
        {"moment_id": "t_park", "reaction": "havent_been"}]}).status_code == 204
    tasks = client.get("/v1/onboarding", headers=h).json()["conjoint_tasks"]
    def pick(t):
        rank = lambda s: 2 if "rainy" in s else (1 if "cold but dry" in s else 0)
        return "A" if rank(t["A"]) <= rank(t["B"]) else "B"
    choices = [{"task": t["task"], "choice": pick(t)} for t in tasks]
    assert client.post("/v1/me/conjoint", headers=h, json={"items": choices}).status_code == 204
    assert client.post("/v1/me/answers", headers=h, json={"items": [
        {"question": "best_hour", "text": "On the boat at sunset.", "input_mode": "typed"}]}).status_code == 204
    assert client.put("/v1/me/profile", headers=h, json={"company": "friends", "why_travel": ["discover"]}
                      ).status_code == 204

    w = client.get("/v1/me/weights", headers=h).json()
    assert w["n_observations"] == 12          # 2 informative swipes + 10 choices
    rain = next(x for x in w["weights"] if x["name"] == "rain_outdoor")
    assert rain["weight"] < -1.0 and rain["direction"] == "dislikes"

    r = client.post("/v1/me/plans", headers=h, json={
        "start": {"lat": 51.5081, "lon": -0.1281}, "start_time": "10:00", "end_time": "18:00",
        "conditions": {"temp_c": 20, "rain_prob": 0.1}})
    assert r.status_code == 201, r.text
    plan = r.json()
    assert plan["stops"], plan
    assert "m_southken_nhm_reveal" not in [st["moment_id"] for st in plan["stops"]]   # draft: never planned
    first = plan["stops"][0]
    assert first["why"] and first["arrive"] >= "10:00"

    assert client.post(f"/v1/me/plans/{plan['id']}/feedback", headers=h,
                       json={"chosen": True, "fit_rating": 4, "reason": "short walks"}).status_code == 204
    r = client.post("/v1/me/ratings", headers=h, json={
        "moment_id": first["moment_id"], "rating": 5, "plan_id": plan["id"], "would_bring": True,
        "conditions": {"temp_c": 20}, "travel_min": first["travel_min"]})
    assert r.status_code == 201 and r.json()["n_observations"] == 13
    assert client.post("/v1/me/events", headers=h, json={"name": "onboarding_done", "props": {"seconds": 900}}
                       ).status_code == 204

    assert client.delete("/v1/me", headers=h).status_code == 204
    assert client.get("/v1/me/plans", headers=h).status_code == 401
    export = client.get("/v1/admin/export", headers=ADMIN).json()
    for table, rows in export.items():
        assert not [r for r in rows if r.get("user_id") == uid or r.get("id") == uid], table


def test_safety_alert_goes_to_a_person_and_tracks_reply_time(client):
    h, _ = install(client)
    r = client.post("/v1/me/safety", headers=h, json={"message": "I feel unsafe here"})
    assert r.status_code == 201
    assert "999" in r.json()["message"] and "few hours" in r.json()["message"]
    alerts = client.get("/v1/admin/safety", headers=ADMIN).json()
    assert len(alerts) == 1 and alerts[0]["message"] == "I feel unsafe here"
    r = client.post(f"/v1/admin/safety/{alerts[0]['id']}/reply", headers=ADMIN, json={"replied_by": "abram"})
    assert r.status_code == 200 and r.json()["minutes_to_first_reply"] >= 0
    assert client.get("/v1/admin/safety", headers=ADMIN).json() == []


def test_cannot_rate_against_someone_elses_plan(client):
    h1, uid1 = install(client)
    h2, _ = install(client)
    plan = client.post(f"/v1/admin/users/{uid1}/plans", headers=ADMIN,
                       json={"stops": [{"moment_id": "t_view", "arrive": "11:00"}]}).json()
    r = client.post("/v1/me/ratings", headers=h2, json={"moment_id": "t_view", "rating": 4, "plan_id": plan["id"]})
    assert r.status_code == 404


def test_admin_needs_the_admin_token(client):
    h, _ = install(client)
    assert client.get("/v1/admin/safety", headers=h).status_code == 403
    r = client.post("/v1/admin/moments/reload", headers=ADMIN).json()
    assert r["plannable"] == 6 and "m_southken_nhm_reveal" in r["drafts"]


def test_curated_plan_for_test_b(client):
    h, uid = install(client)
    r = client.post(f"/v1/admin/users/{uid}/plans", headers=ADMIN, json={
        "kind": "curated", "label": "A", "stops": [{"moment_id": "t_view", "arrive": "11:00"},
                                                   {"moment_id": "t_boat", "arrive": "13:00"}]})
    assert r.status_code == 201
    plans = client.get("/v1/me/plans", headers=h).json()
    assert plans[0]["label"] == "A" and [s["moment_id"] for s in plans[0]["stops"]] == ["t_view", "t_boat"]
    bad = client.post(f"/v1/admin/users/{uid}/plans", headers=ADMIN,
                      json={"stops": [{"moment_id": "nope", "arrive": "10:00"}]})
    assert bad.status_code == 422
