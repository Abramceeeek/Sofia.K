"""m220: the switch that, after the friends' round, gives everyone the kinds-of-places cards. It's off ("named") now,
so the friends' round is unchanged. When on, a person based in London answers the category cards: the answers enter
their fit like a visitor's, and they stay a resident (in the Test B cohort), never a visitor."""
from test_api import ADMIN, client, install  # noqa: F401  (the client fixture)

DAY = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_name": "Charing Cross station",
       "start_time": "10:00", "end_time": "18:00", "conditions": {"temp_c": 18, "rain_prob": 0.1}}


def test_the_switch_is_off_now_and_only_two_values_count(client):
    h, _ = install(client)
    assert client.get("/v1/onboarding", headers=h).json()["places_mode"] == "named"   # the friends' round: as it is
    ob = client.app.state.onboarding
    try:
        ob["places_mode"] = "kinds"
        assert client.get("/v1/onboarding", headers=h).json()["places_mode"] == "kinds"
        ob["places_mode"] = "everything"
        assert client.get("/v1/onboarding", headers=h).json()["places_mode"] == "named"   # anything else: as now
    finally:
        ob["places_mode"] = "named"


def test_a_londoner_answering_kinds_of_places_is_fitted_and_stays_a_resident(client):
    h, uid = install(client)
    assert client.put("/v1/me/profile", headers=h, json={"based": "london"}).status_code == 204
    r = client.post("/v1/me/categories", headers=h, json={"items": [
        {"key": "views_above", "reaction": "loved"}, {"key": "big_museums", "reaction": "didnt_enjoy"},
        {"key": "street_food", "reaction": "never_tried", "want": "yes"}]})
    assert r.status_code == 204
    plan = client.post("/v1/me/plans", headers=h, json=DAY).json()
    assert plan["basis"]["kinds"] == 3                     # the answers are what the plan rests on
    reasons = [x["you"] for st in plan["stops"] for x in st.get("reasons") or []]
    assert not any("museum" in x.lower() and "love" in x.lower() for x in reasons)   # never "you love big museums"
    assert client.get("/v1/admin/export", headers=ADMIN).json()["cohorts"][uid] == "resident"   # never a visitor
    assert client.post("/v1/me/testb/pair", headers=h).status_code == 201   # the Test B pair is still theirs to do
