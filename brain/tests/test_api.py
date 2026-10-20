import shutil
from datetime import date

import pytest
import yaml
from fastapi.testclient import TestClient

from brain.api import EXAMPLE_DAY, create_app
from brain.config import Settings

from conftest import DATA, make_moment


@pytest.fixture
def client(tmp_path, test_moments):
    data = tmp_path / "data"
    (data / "moments").mkdir(parents=True)
    for f in ("priors.yaml", "onboarding.yaml", "conjoint_design.csv", "swipe_items.yaml", "aspiration.yaml",
              "privacy_app.html", "categories.yaml"):
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
    # D112: 6 places and 5 tasks before the first plan, the rest in "Improve future plans"
    assert [t["task"] for t in r["conjoint_tasks"]] == [2, 4, 6, 8, 9]
    assert [t["task"] for t in r["conjoint_tasks_later"]] == [1, 3, 5, 7, 10]
    places = r["swipe_places"]
    assert [p["item"] for p in places] == [4, 6, 11, 12, 13, 14]
    assert [p["item"] for p in r["swipe_places_later"]] == [1, 2, 3, 15]
    assert {k: places[0][k] for k in ("item", "name")} == {"item": 4, "name": "British Museum"}
    assert places[0]["reactions"]["loved"] == "Got it: big museums full of history."   # D117
    assert r["open_questions"][0]["text"].startswith("Tell us about a great moment")
    assert "skip" in r["swipe"]["reactions"] and r["conjoint"]["no_preference"]
    assert len(r["open_questions"][0]["examples"]) == 3
    assert r["fields"]["question"].startswith("What interests you most?")
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
    assert w["n_observations"] == 8           # 2 informative swipes + the 5 upfront choices (D112) + company (D127)
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
    tot = plan["totals"]   # the summary at the top of the plan (D110)
    assert tot["finish"] == plan["stops"][-1]["depart"] and tot["walk_km"] >= 0
    assert tot["cost_gbp"] == round(sum(st["cost_gbp"] for st in plan["stops"]) + tot["transport_gbp"], 2)
    for st in plan["stops"]:
        assert st["pin"] and st["lines"] and st["cost_text"] and st["arrive"] >= "10:00"
    first = next(st for st in plan["stops"] if st["rateable"])
    assert first["why"] and first["card"]["id"] == first["moment_id"]
    assert all(st["worth_gbp"] is None or st["worth_gbp"] >= 1 for st in plan["stops"])   # "worth about £V" (D112)
    assert any(st["worth_gbp"] for st in plan["stops"] if st["rateable"])

    assert client.post(f"/v1/me/plans/{plan['id']}/feedback", headers=h,
                       json={"chosen": True, "fit_rating": 4, "reason": "short walks"}).status_code == 204
    r = client.post("/v1/me/ratings", headers=h, json={
        "moment_id": first["moment_id"], "rating": 5, "plan_id": plan["id"], "would_bring": True,
        "conditions": {"temp_c": 20}, "travel_min": first["travel_min"]})
    assert r.status_code == 201 and r.json()["n_observations"] == 9
    assert client.post("/v1/me/events", headers=h, json={"name": "onboarding_done", "props": {"seconds": 900}}
                       ).status_code == 204
    day = f"/v1/me/plans/{plan['id']}/day"   # D127: the two end-of-day questions
    assert client.post(day, headers=h, json={"worth": "less", "again": False}).status_code == 204
    assert client.post(day, headers=h, json={"worth": "about_right", "again": True}).status_code == 204
    rows = [r for r in client.get("/v1/admin/export", headers=ADMIN).json()["day_feedback"] if r["user_id"] == uid]
    assert [(r["worth"], r["again"]) for r in rows] == [("about_right", True)]   # answering again replaces it
    assert client.post(day, headers=h, json={"worth": "lots"}).status_code == 422
    assert client.post("/v1/me/plans/999999/day", headers=h, json={"again": True}).status_code == 404

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


def test_skip_and_no_preference_are_stored_but_carry_no_information(client):
    """D110: "Not sure" on a place and "No preference" on a this-or-that task are allowed and left out of the fit."""
    h, _ = install(client)
    assert client.post("/v1/me/swipes", headers=h, json={"items": [
        {"item": 1, "reaction": "skip"}, {"item": 5, "reaction": "loved"}]}).status_code == 204   # 5: not shown, still valid
    assert client.post("/v1/me/conjoint", headers=h, json={"items": [
        {"task": 1, "choice": "N"}, {"task": 2, "choice": "A"}]}).status_code == 204
    assert client.get("/v1/me/weights", headers=h).json()["n_observations"] == 2
    assert client.post("/v1/me/conjoint", headers=h, json={"items": [{"task": 3, "choice": "C"}]}).status_code == 422


def test_swap_this_stop_keeps_the_rest_and_brings_something_new(client):
    """D110: the app sends the same request with the other stops in `keep` and the swapped-out card in `exclude`."""
    h, _ = install(client)
    body = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_time": "13:30", "end_time": "18:00", "stops": 3,
            "familiar": False}
    first = client.post("/v1/me/plans", headers=h, json=body).json()
    out = next(st for st in first["stops"] if st["rateable"])
    kept = [st["key"] for st in first["stops"] if st["key"] != out["key"]]
    r = client.post("/v1/me/plans", headers=h, json={**body, "keep": kept, "exclude": [out["moment_id"]]})
    assert r.status_code == 201, r.text
    second = r.json()
    ids = [st["moment_id"] for st in second["stops"]]
    assert out["moment_id"] not in ids and len(ids) == 3
    assert {k.split("#")[0] for k in kept} <= set(ids)   # the other stops stay
    assert second["id"] != first["id"]


def test_example_day_needs_no_install_and_holds_nothing_personal(client):
    """D112: shown before consent, so no token; population weights only; no reasons or worth. m150: no Test B place."""
    r = client.get("/v1/example-day")
    assert r.status_code == 200
    day = r.json()
    assert day["title"] == "An example Sunday" and 2 <= len(day["stops"]) <= 3
    assert all(st["chosen_for"] == [] and st["worth_gbp"] is None for st in day["stops"])
    assert not {st["moment_id"].split("@")[-1] for st in day["stops"]} & set(EXAMPLE_DAY["exclude"])
    assert day["totals"]["finish"] <= "14:30"
    assert client.get("/v1/example-day").json() == day   # built once, then kept


def test_answering_again_replaces_the_earlier_answer(client):
    """m176: onboarding's Back lets people answer a place or a made-up day again; the fit counts each once."""
    h, uid = install(client)
    post = lambda r: client.post("/v1/me/swipes", headers=h, json={"items": [{"item": 4, "reaction": r}]})
    assert post("loved").status_code == 204
    n1 = client.get("/v1/me/weights", headers=h).json()["n_observations"]
    assert post("didnt_enjoy").status_code == 204
    assert client.get("/v1/me/weights", headers=h).json()["n_observations"] == n1
    export = client.get("/v1/admin/export", headers=ADMIN).json()
    assert [sw["reaction"] for sw in export["swipes"] if sw["user_id"] == uid] == ["didnt_enjoy"]
    # journey round 2: the best-moment answer too, after Back and Next
    for text in ("The lido at 8am.", "The lido at 8am, then breakfast."):
        assert client.post("/v1/me/answers", headers=h, json={"items": [
            {"question": "best_hour", "text": text, "input_mode": "typed"}]}).status_code == 204
    export = client.get("/v1/admin/export", headers=ADMIN).json()
    assert [a["text"] for a in export["answers"] if a["user_id"] == uid] == ["The lido at 8am, then breakfast."]


def test_a_stop_that_needs_booking_says_so(tmp_path, test_moments):
    """Journey audit (7 Oct): Horizon 22 needs a booked slot; the stop says so, and stops without one say nothing."""
    data = tmp_path / "data"
    (data / "moments").mkdir(parents=True)
    for f in ("priors.yaml", "onboarding.yaml", "conjoint_design.csv", "swipe_items.yaml", "aspiration.yaml",
              "privacy_app.html", "categories.yaml"):
        shutil.copy(DATA / f, data / f)
    shutil.copy(DATA / "moments" / "m_horizon_22.yaml", data / "moments")
    for m in test_moments:
        (data / "moments" / f"{m.id}.yaml").write_text(yaml.safe_dump(m.model_dump(by_alias=True)))
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'b.db'}", data_dir=data, admin_token="x",
                        alert_webhook_url=None, planner_time_limit_s=0.3)
    with TestClient(create_app(settings)) as client:
        h, _ = install(client)
        body = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_time": "12:00", "end_time": "17:00", "stops": 3,
                "date": "2026-10-12", "familiar": False, "intent": {"must_do": "m_horizon_22"}}   # a Monday
        r = client.post("/v1/me/plans", headers=h, json=body)
        assert r.status_code == 201, r.text
        by_id = {st["moment_id"]: st for st in r.json()["stops"]}
    assert by_id["m_horizon_22"]["book_ahead"].startswith("Book a free time slot on horizon22.co.uk")
    assert by_id["m_horizon_22"]["hours"].startswith("Mon–Fri 10:00–18:00")
    assert all(st["book_ahead"] == "" for k, st in by_id.items() if k != "m_horizon_22")


def test_regenerate_leaves_out_the_current_stops_or_falls_back(client):
    """D112, "Regenerate plan": the app sends the current stops in `exclude`; with nothing new left, the best day."""
    h, _ = install(client)
    body = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_time": "13:30", "end_time": "18:00", "stops": 3,
            "familiar": False}
    first = client.post("/v1/me/plans", headers=h, json=body).json()
    old = [st["moment_id"] for st in first["stops"] if st["rateable"]]
    again = client.post("/v1/me/plans", headers=h, json={**body, "exclude": old}).json()
    assert again["stops"] and not set(old) & {st["moment_id"] for st in again["stops"]}
    every = [m["id"] for m in client.get("/v1/moments", headers=h).json()]
    fallback = client.post("/v1/me/plans", headers=h, json={**body, "exclude": every[:40]}).json()
    assert fallback["stops"]


def _onboard(client, h):
    assert client.put("/v1/me/profile", headers=h, json={"based": "london"}).status_code == 204
    assert client.post("/v1/me/swipes", headers=h, json={"items": [
        {"item": 4, "reaction": "loved"}, {"item": 3, "reaction": "didnt_enjoy"}]}).status_code == 204


def test_test_b_pair_is_blind_random_once_and_reveals_after_the_choice(client):
    h, uid = install(client)
    _onboard(client, h)
    assert client.get("/v1/me/testb/pair", headers=h).status_code == 404
    r = client.post("/v1/me/testb/pair", headers=h, json={"mood": "explore", "company": "friends"})
    assert r.status_code == 201, r.text
    pair = r.json()
    assert pair["done"] is False and "personal_label" not in pair and "chosen" not in pair
    p1, p2 = pair["plans"]
    assert (p1["label"], p2["label"]) == ("1", "2") and p1["id"] < p2["id"]
    # identical format: the same fields, no photos, pins, feeling words, reasons or worth on either plan
    for pl in (p1, p2):
        assert pl["blind"] and pl["feel_line"] is None and pl["basis"] is None
        assert pl["summary"][0].startswith("Start: Charing Cross station at 12:00 · 4 stops, including lunch")
        for i, st in enumerate(pl["stops"]):
            assert st["moment_id"] == f"plan{pl['label']}-{i}" and st["lines"]
            assert st["card"] is None and st["pin"] is None and st["feel_word"] is None
            assert not st["reasons"] and not st["chosen_for"] and st["worth_gbp"] is None and not st["rateable"]
            # D127: the same shape for both, so neither reads richer: a short title, one sentence per field
            assert ": " not in st["title"]
            for field in ("approach", "what"):
                assert len([x for x in (st[field] or "").split(". ") if x]) <= 1, st[field]
    assert {tuple(sorted(st)) for pl in (p1, p2) for st in pl["stops"]} == {tuple(sorted(p1["stops"][0]))}
    titles = {pl["label"]: [st["title"] for st in pl["stops"]] for pl in (p1, p2)}
    generic = next(k for k, v in titles.items() if v[0] == "The National Gallery")
    assert client.get("/v1/me/plans", headers=h).json() == []           # hidden until they've chosen
    assert client.get(f"/v1/me/plans/{p1['id']}", headers=h).status_code == 404
    assert client.post(f"/v1/me/plans/{p1['id']}/feedback", headers=h, json={"chosen": True}).status_code == 409
    again = client.post("/v1/me/testb/pair", headers=h, json={})          # made once: the same pair
    assert [pl["id"] for pl in again.json()["plans"]] == [p1["id"], p2["id"]]
    # the personal plan ends within 30 min of the generic one (D97)
    ends = {pl["label"]: pl["totals"]["finish"] for pl in (p1, p2)}
    mins = lambda t: int(t[:2]) * 60 + int(t[3:])
    assert abs(mins(ends["1"]) - mins(ends["2"])) <= 30

    r = client.post("/v1/me/testb/pair/feedback", headers=h,
                    json={"chosen": generic, "fit_1": 4, "fit_2": 2, "why": "  More of a walk.  "})
    assert r.status_code == 200, r.text
    done = r.json()
    personal = "1" if generic == "2" else "2"
    assert done["done"] and done["personal_label"] == personal and done["chosen_label"] == generic
    assert done["reveal"][0].startswith(f"Plan {personal} was made from your answers")
    chosen = done["chosen"]
    assert chosen["kind"] == "generic" and chosen["title"] == "A Saturday out in London"
    # dated for the Saturday it was planned for, so its rating reminders can fire; the blind view shows no date
    assert date.fromisoformat(chosen["date"]).weekday() == 5 and all(pl["date"] is None for pl in done["plans"])
    assert chosen["stops"][0]["moment_id"] == "generic:0" and chosen["stops"][0]["rateable"]
    assert client.post("/v1/me/testb/pair/feedback", headers=h,
                       json={"chosen": "1", "fit_1": 1, "fit_2": 1}).status_code == 409
    plans = {pl["label"]: pl for pl in client.get("/v1/me/plans", headers=h).json()}
    assert plans["1"]["fit_rating"] == 4 and plans["2"]["fit_rating"] == 2
    assert plans[generic]["status"] == "chosen" and plans[personal]["status"] == "not_chosen"
    assert plans[generic]["intent"]["trip"] == {"mood": "explore", "company": "friends"}

    # a generic stop can be rated against the generic plan only, and it never feeds the fit
    rate = lambda pid: client.post("/v1/me/ratings", headers=h,
                                   json={"moment_id": "generic:1", "rating": 5, "plan_id": pid})
    assert rate(plans[personal]["id"]).status_code == 404
    r = rate(plans[generic]["id"])
    assert r.status_code == 201 and r.json()["n_observations"] == 2     # the two swipes only: unchanged
    # rating the same stop again (the app restarted, or an offline rating sent late) replaces it
    again = client.post("/v1/me/ratings", headers=h,
                        json={"moment_id": "generic:1", "rating": 3, "plan_id": plans[generic]["id"]})
    assert again.status_code == 201
    export = client.get("/v1/admin/export", headers=ADMIN).json()
    fb = [p for p in export["plans"] if p["user_id"] == uid and p["status"] == "chosen"][0]
    assert fb["reason"] == "More of a walk."
    assert [r["rating"] for r in export["ratings"] if r["user_id"] == uid] == [3]
    assert any(e["name"] == "testb_pair_feedback" and e["user_id"] == uid for e in export["events"])


def test_test_b_pair_order_is_random_and_skips_visitors(client):
    labels = set()
    for _ in range(12):
        h, _ = install(client)
        _onboard(client, h)
        done = client.post("/v1/me/testb/pair", headers=h, json={})
        labels.add(next(pl["label"] for pl in done.json()["plans"] if pl["stops"][0]["title"] != "The National Gallery"))
        if len(labels) == 2:
            break
    assert labels == {"1", "2"}   # chance of failing: 2 × 0.5^12
    h, _ = install(client)
    assert client.put("/v1/me/profile", headers=h, json={"based": "abroad"}).status_code == 204
    assert client.post("/v1/me/testb/pair", headers=h, json={}).status_code == 409


def test_survey_and_tester_code(client):
    h, uid = install(client, code=" friends ")
    assert client.post("/v1/me/survey", headers=h, json={
        "understood": 4, "like_person": 5, "typed_or_spoke": "spoke", "intrusive": "  "}).status_code == 204
    assert client.post("/v1/me/survey", headers=h, json={"understood": 6}).status_code == 422
    h2, uid2 = install(client, code="ucl hiking")
    h3, uid3 = install(client, src="ref:abc123", code="FRIENDS")
    export = client.get("/v1/admin/export", headers=ADMIN).json()
    users = {u["id"]: u for u in export["users"]}
    assert (users[uid]["channel"], users[uid]["src"]) == ("friends_family", "code:FRIENDS")
    assert (users[uid2]["channel"], users[uid2]["src"]) == ("stranger", "code:UCL-HIKING")
    assert (users[uid3]["channel"], users[uid3]["src"]) == ("friends_family", "ref:abc123")   # the share funnel
    answers = {a["question"]: a["text"] for a in export["answers"] if a["user_id"] == uid}
    assert answers == {"survey:understood": "4", "survey:like_person": "5", "survey:typed_or_spoke": "spoke"}
    assert any(e["name"] == "tester_code" and e["props"] == {"code": "FRIENDS"} and e["user_id"] == uid3
               for e in export["events"])


def test_the_android_app_is_recorded_at_install(client):
    """D125: the Android app says so at install (an event); the iPhone app sends nothing and nothing is added."""
    _, android = install(client, platform="android")
    _, iphone = install(client)
    assert client.post("/v1/installs", json={"consent": {"version": "x", "research": True, "ai_processing": False},
                                             "platform": "windows"}).status_code == 422
    events = client.get("/v1/admin/export", headers=ADMIN).json()["events"]
    marks = [(e["user_id"], e["props"]) for e in events if e["name"] == "install_platform"]
    assert marks == [(android, {"platform": "android"})]
    assert iphone not in {u for u, _ in marks}


def test_a_trip_days_feelings_and_checked_dates_reach_the_plan(client):
    """Journey round 2: swap and regenerate on a trip day send the trip's feelings (this plan only, the profile isn't
    changed); every stop says when its card was last checked; long trips can exclude more than 40 places."""
    h, _ = install(client)
    body = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_time": "12:00", "end_time": "17:00", "stops": 3,
            "familiar": False, "feelings": ["curious", "nonsense"], "exclude": [f"m_none_{i}" for i in range(60)]}
    r = client.post("/v1/me/plans", headers=h, json=body)
    assert r.status_code == 201, r.text
    assert all("checked" in st for st in r.json()["stops"])
    assert client.get("/v1/me/weights", headers=h).json()["n_observations"] == 0
