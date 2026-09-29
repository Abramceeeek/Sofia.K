import shutil

import pytest
import yaml
from fastapi.testclient import TestClient

from brain.api import create_app
from brain.config import Settings

from conftest import DATA, make_moment


@pytest.fixture
def client(tmp_path, test_moments):
    data = tmp_path / "data"
    (data / "moments").mkdir(parents=True)
    for f in ("priors.yaml", "onboarding.yaml", "conjoint_design.csv", "swipe_items.yaml", "aspiration.yaml",
              "privacy_app.html"):
        shutil.copy(DATA / f, data / f)
    for f in ("m_southken_nhm_reveal.yaml", "m_waterloo_bridge_sunset.yaml"):
        shutil.copy(DATA / "moments" / f, data / "moments")
    # two cards at swipe places (swipe_items.yaml `cards`): the Uber Boat (item 2) and Borough Market (item 3)
    extra = [make_moment("m_uber_boat_west_day", 51.5071, -0.1218, tags=dict(movement_views=2, outdoor_exposure=1),
                         cost=12),
             make_moment("m_borough_market_graze", 51.5055, -0.0905, tags=dict(food=2, crowds=2), cost=15)]
    for m in test_moments + extra:
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
    places = r["swipe_places"]
    assert len(places) == 16 and places[0] == {"item": 1, "name": "Big Ben and Parliament Square"}   # locked, D107
    assert r["open_questions"][0]["key"] == "best_hour"
    assert {o["key"] for o in r["fields"]["options"]} >= {"food", "nature", "none"}
    assert r["example_shot_card"]["id"] == "m_waterloo_bridge_sunset" and r["example_shot_card"]["shot_card"]


def test_full_flow_answers_weights_plan_rating_and_deletion(client):
    h, uid = install(client)
    # swipes and "this or that": always avoid the rainy plan (D95), otherwise take the milder one
    assert client.post("/v1/me/swipes", headers=h, json={"items": [
        {"item": 4, "reaction": "loved"}, {"item": 3, "reaction": "didnt_enjoy"},
        {"item": 6, "reaction": "havent_been"}]}).status_code == 204
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
        "start": {"lat": 51.5081, "lon": -0.1281}, "start_name": "Charing Cross station",
        "start_time": "10:00", "end_time": "18:00", "conditions": {"temp_c": 20, "rain_prob": 0.1}})
    assert r.status_code == 201, r.text
    plan = r.json()
    assert len(plan["stops"]) == 4, plan
    ids = [st["moment_id"] for st in plan["stops"]]
    assert "m_southken_nhm_reveal" not in ids                              # draft: never planned
    assert "m_borough_market_graze" not in ids                            # a place they didn't enjoy (D100)
    assert sum(st["lunch"] for st in plan["stops"]) == 1                  # one lunch stop (D102)
    assert plan["summary"][0].startswith("Start: Charing Cross station at 10:00 · 4 stops, including lunch")
    for st in plan["stops"]:
        assert st["pin"] and st["lines"] and st["cost_text"] and st["arrive"] >= "10:00"
    first = next(st for st in plan["stops"] if st["rateable"])
    assert first["why"] and first["card"]["id"] == first["moment_id"]

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
    assert r["plannable"] == 9 and "m_southken_nhm_reveal" in r["drafts"]   # 6 test cards, 2 at swipe places, Waterloo


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


def test_swipes_and_fields_are_checked(client):
    h, _ = install(client)
    assert client.post("/v1/me/swipes", headers=h, json={"items": [{"item": 99, "reaction": "loved"}]}
                       ).status_code == 422
    assert client.put("/v1/me/profile", headers=h, json={"fields": ["astrology"]}).status_code == 422
    assert client.put("/v1/me/profile", headers=h, json={"fields": ["food"]}).status_code == 204


def test_app_plan_keeps_one_place_they_loved_by_default(client):
    """D103: the familiar favourite is on in the app. The Uber Boat (swipe item 2) was loved, so its card is in."""
    h, _ = install(client)
    client.post("/v1/me/swipes", headers=h, json={"items": [{"item": 2, "reaction": "loved"}]})
    body = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_time": "13:30", "end_time": "18:00", "stops": 3}
    plan = client.post("/v1/me/plans", headers=h, json=body).json()
    boat = [st for st in plan["stops"] if st["moment_id"] == "m_uber_boat_west_day"]
    assert boat and boat[0]["familiar"]
    off = client.post("/v1/me/plans", headers=h, json={**body, "familiar": False}).json()
    assert "m_uber_boat_west_day" not in [st["moment_id"] for st in off["stops"]]   # Test B rule: new places only


def test_budget_band_and_date_shape_the_plan(client):
    h, _ = install(client)
    client.put("/v1/me/profile", headers=h, json={"budget_band": "under_20"})
    plan = client.post("/v1/me/plans", headers=h, json={
        "start": {"lat": 51.5081, "lon": -0.1281}, "start_time": "10:00", "end_time": "18:00",
        "date": "2026-10-31"}).json()
    assert plan["title"] == "Saturday 31 October"
    assert sum(st["cost_gbp"] for st in plan["stops"]) <= 20
    assert "t_pricey" not in [st["moment_id"] for st in plan["stops"]]


def test_privacy_notice_is_public_and_says_what_the_app_holds(client):
    r = client.get("/privacy")
    assert r.status_code == 200 and "text/html" in r.headers["content-type"]
    assert "Delete my data" in r.text and "999" in r.text and "No AI service" in r.text
