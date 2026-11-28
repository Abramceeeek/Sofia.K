"""m363 (Abram, 26 Nov, batch 8): the central person-to-place engine, in shadow mode. Six classes; must-go is intent and
never beats a hard rule; scores are provisional ranking measures, never chances; a reason needs evidence on both sides;
and asking for matches changes no plan."""
import tempfile

import pytest
from fastapi.testclient import TestClient

from brain import match as engine
from brain.api import create_app
from brain.config import DATA_DIR, Settings

FRIDAY = "2026-12-04"


@pytest.fixture
def real():
    """The app on the real London cards (the engine judges real places), with a throwaway database."""
    tmp = tempfile.mkdtemp()
    settings = Settings(database_url=f"sqlite:///{tmp}/m.db", data_dir=DATA_DIR, admin_token="x",
                        alert_webhook_url=None, planner_time_limit_s=0.3)
    with TestClient(create_app(settings)) as c:
        yield c


def _person(c, swipes=None, profile=None):
    r = c.post("/v1/installs", json={"channel": "stranger", "src": "test",
                                     "consent": {"version": "2026-09", "research": True, "ai_processing": False}})
    h = {"Authorization": f"Bearer {r.json()['token']}"}
    if profile:
        assert c.put("/v1/me/profile", headers=h, json=profile).status_code == 204
    if swipes:
        c.post("/v1/me/swipes", headers=h, json={"items": [{"item": i, "reaction": x} for i, x in swipes.items()]})
    return h


def _matches(c, h, **q):
    query = "&".join(f"{k}={v}" for k, v in {"date": FRIDAY, **q}.items())
    r = c.get(f"/v1/me/matches?{query}", headers=h)
    assert r.status_code == 200, r.text
    return r.json()


def _one(out, place):
    return next(x for x in out["matches"] if x["place"] == place)


def test_six_classes_and_a_score_that_is_never_called_a_chance(real):
    out = _matches(real, _person(real, {3: "loved", 4: "didnt_enjoy"}))
    assert set(out["classes"]) == set(engine.CLASSES)
    assert "not a chance" in out["note"]
    for x in out["matches"]:
        assert x["class"] in engine.CLASSES and isinstance(x["score"], float)
        assert not any(k in x for k in ("p_good", "probability", "chance"))


def test_someone_with_no_answers_gets_low_confidence_not_invented_tastes(real):
    out = _matches(real, _person(real))
    judged = [x for x in out["matches"] if x["class"] != "not_suitable"]
    assert judged and all(x["class"] == "low_confidence" and x["reason"] is None for x in judged)


def test_a_place_they_didnt_enjoy_is_a_strong_negative_not_a_ban(real):
    """m364 (Abram): "place-specific dislike: a strong negative for that place". Never recommended unasked, but never
    a hard rule (batch 8 made it not suitable)."""
    h = _person(real, {4: "didnt_enjoy", 3: "loved"})
    bm = _one(_matches(real, h), "m_bm_great_court")
    assert bm["class"] == "poor_match" and bm["restrictions"] == []
    assert bm["against"] == "You said you didn't enjoy British Museum."
    assert bm["score"] < bm["model_score"]


def test_a_loved_place_is_a_strong_match_with_its_own_reason(real):
    h = _person(real, {3: "loved"})
    bm = _one(_matches(real, h), "m_borough_market_graze")
    assert bm["class"] == "strong_match" and bm["reason"] == "You loved Borough Market."
    assert bm["evidence"] and bm["evidence"][0]["place"] == "this is that place"


def test_must_go_is_intent_beats_an_older_dislike_and_never_a_hard_rule(real):
    """m364 (Abram): "the traveller's most recent, specific instruction takes priority over an older preference,
    subject to hard constraints". Today's request beats the older swipe; the age rule beats the request."""
    h = _person(real, {4: "didnt_enjoy", 6: "loved"})
    out = _matches(real, h, must_go="m_tate_modern,m_bm_great_court")
    assert _one(out, "m_tate_modern")["class"] == "must_go"
    bm = _one(out, "m_bm_great_court")
    assert bm["class"] == "must_go" and bm["reason"] == "Included because you specifically asked to visit."
    top = bm["preferences"][0]
    assert top["decides"] and top["instruction"] == "must_go" and "the newer request wins" in top["note"]
    assert any(x["instruction"] == "dislike_place" and x["overridden_by"] == "must_go" for x in bm["preferences"])
    bike = _one(_matches(real, h, must_go="m_park_bike_loop_hyde", children="8"), "m_park_bike_loop_hyde")
    assert bike["class"] == "not_suitable" and bike["restrictions"][0].startswith("you asked for it, but")


def test_a_childs_age_rule_is_not_suitable_for_a_party_with_a_young_child(real):
    h = _person(real, {6: "loved"})
    bike = _one(_matches(real, h, children="8"), "m_park_bike_loop_hyde")
    assert bike["class"] == "not_suitable" and any("minimum age" in r for r in bike["restrictions"])


def test_every_reason_has_evidence_on_both_sides_and_none_on_a_partial_tag(real):
    """m363 work package D: the traveller's own answer, and a feature that defines the place (its tag at 2)."""
    from brain.moments import load_moments
    cards = {m.id: m for m in load_moments(DATA_DIR / "moments")}
    h = _person(real, {3: "loved", 14: "loved", 6: "fine", 4: "fine"},
                profile={"fields": ["food"], "why_travel": ["excited", "curious"]})
    out = _matches(real, h)
    with_reason = [x for x in out["matches"] if x["reason"]]
    assert with_reason
    for x in with_reason:
        assert x["class"] in ("must_go", "strong_match", "good_discovery")
        assert x["evidence"] and all(e["traveller"] and e["place"] for e in x["evidence"])
        for e in x["evidence"]:
            if "= 2" in e["place"]:
                f = e["place"].split(" = ")[0]
                assert int(cards[x["place"]].tag(f) or 0) == 2, (x["place"], f)


def test_one_place_ranks_differently_for_different_people(real):
    """Abram's demonstration: Borough Market for a food lover and for a quiet traveller who avoids crowds."""
    food = _person(real, {3: "loved", 14: "loved"}, profile={"fields": ["food"]})
    quiet = _person(real, {7: "didnt_enjoy", 6: "loved", 16: "loved"}, profile={"why_travel": ["peaceful"]})
    ob = real.get("/v1/onboarding", headers=quiet).json()
    pick = [{"task": t["task"], "choice": "A" if "mostly quiet" in t["A"] else "B"} for t in ob["conjoint_tasks"]]
    assert real.post("/v1/me/conjoint", headers=quiet, json={"items": pick}).status_code == 204
    f, q = (_one(_matches(real, h), "m_borough_market_graze") for h in (food, quiet))
    assert f["class"] == "strong_match" and f["score"] > q["score"]
    # m366: the market's own page says Saturday afternoons are busy. On a Friday that's a caution, not a fact about
    # the day, so it lowers confidence (missing, never negative); on a Saturday it's negative evidence.
    assert q["class"] == "low_confidence"
    assert q["against"] == "You picked quieter days, and this place is busy on Saturday afternoons."
    sat = _one(_matches(real, quiet, date="2026-12-05"), "m_borough_market_graze")
    assert sat["class"] == "poor_match" and sat["against"] == q["against"]


def test_asking_for_matches_changes_no_plan(real):
    """Shadow mode: the same plan request gives the same stops before and after the engine runs, and nothing is
    stored by it."""
    h = _person(real, {3: "loved", 6: "loved"})
    body = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_name": "Charing Cross", "start_time": "10:00",
            "end_time": "16:00", "date": FRIDAY, "stops": 3}
    before = real.post("/v1/me/plans", headers=h, json=body).json()
    n_plans = len(real.get("/v1/me/plans", headers=h).json())
    _matches(real, h)
    assert len(real.get("/v1/me/plans", headers=h).json()) == n_plans
    after = real.post("/v1/me/plans", headers=h, json=body).json()
    assert [s["moment_id"] for s in before["stops"]] == [s["moment_id"] for s in after["stops"]]


def test_you_picked_is_said_only_after_this_or_that_answers(real):
    """m363 (the bench: "You picked quieter days" said to travellers who never answered a "this or that" day): without
    those answers the engine says what their answers lean towards, never that they picked."""
    h = _person(real, {7: "didnt_enjoy", 6: "loved", 16: "loved", 3: "didnt_enjoy"}, profile={"why_travel": ["peaceful"]})
    out = _matches(real, h)
    words = [x["reason"] or "" for x in out["matches"]] + [x["against"] or "" for x in out["matches"]]
    assert not any("You picked" in w for w in words)
    assert any("Your answers lean" in w for w in words)


def test_the_history_enthusiast_at_borough_market_is_unknown_not_poor(real):
    """Abram (m364, decision 5): "Your answers lean away from good food" for a history enthusiast should normally be
    uncertainty, not a poor match. The bench's history traveller, through the API: nothing they said is about food,
    and the market's low score rests on most people's weights, so it's low confidence, with no claim about food."""
    h = _person(real, {4: "loved", 1: "loved", 12: "loved", 7: "fine", 14: "fine"},
                profile={"fields": ["history_culture"], "why_travel": ["curious"]})
    bm = _one(_matches(real, h), "m_borough_market_graze")
    assert bm["class"] == "low_confidence"
    assert not (bm["against"] or "").startswith("Your answers lean away from")
    assert "food_discovery" in bm["confidence"]["missing"]
    assert any("whether you enjoy trying food" in x for x in bm["missing"])
