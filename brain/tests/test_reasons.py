"""D115: plain-words reasons, the feeling line, feelings in the fit, and the blind flag."""
import numpy as np

from brain import reasons
from brain.config import DATA_DIR
from brain.dayplan import load_swipe_cards, load_swipe_items
from brain.moments import load_moments
from brain.personal import prior_only
from brain.population import load_population
from brain.scoring import update_person

from test_api import ADMIN, client, install  # noqa: F401  (the client fixture)

POP = load_population(DATA_DIR / "priors.yaml")
BY_ID = {m.id: m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"}
ITEMS = load_swipe_items(DATA_DIR / "swipe_items.yaml")
CARDS = load_swipe_cards(DATA_DIR / "swipe_items.yaml")
NAMES = POP.personal_names


def delta(**lean):
    d = np.zeros(len(NAMES))
    for k, v in lean.items():
        d[NAMES.index(k)] = v
    return d


def loved(item):
    return (*CARDS[item], ITEMS[item])


def test_a_feeling_is_a_stated_choice_that_moves_its_own_features():
    o = reasons.feeling_observation(POP, "curious")
    assert o.y == 1 and o.x[POP.names.index("history_culture")] == 1.0 and o.scale == 0.5
    assert reasons.feeling_observation(POP, "discover") is None          # an old key is ignored, not an error
    post = update_person(POP, [o])
    assert post.mean[NAMES.index("history_culture")] > 0.1
    peaceful = update_person(POP, [reasons.feeling_observation(POP, "peaceful")])
    assert peaceful.mean[NAMES.index("crowds")] < 0


def test_reasons_cite_only_what_really_raises_the_stop():
    boat = next(i for i, (_, cards, *_) in CARDS.items() if "m_uber_boat_west_day" in cards)
    m = BY_ID["m_waterloo_bridge_sunset"]
    lean = delta(movement_views=0.6)
    r = reasons.stop_reasons(POP, lean, m, loved=[loved(boat)], feelings=[], rated=[], interests=[], n_choices=0)
    assert r[0]["you"] == f"You loved {CARDS[boat][0]}, and this has views too."
    assert r[0]["me"].startswith("I loved")
    # the same loved place, but no personal lean on the shared feature: not a reason
    r = reasons.stop_reasons(POP, delta(), m, loved=[loved(boat)], feelings=[], rated=[], interests=[], n_choices=0)
    assert r == [{"you": "We don't know much about you yet: this one suits most people and fits your route.",
                  "me": None}]


def test_the_familiar_favourite_and_feelings():
    boat = next(i for i, (_, cards, *_) in CARDS.items() if "m_uber_boat_west_day" in cards)
    m = BY_ID["m_uber_boat_west_day"]
    r = reasons.stop_reasons(POP, delta(), m, loved=[loved(boat)], feelings=[], rated=[], interests=[], n_choices=0)
    assert r[0]["you"] == f"You loved {CARDS[boat][0]}."
    garden = next(mm for mm in BY_ID.values() if (mm.features.place.get("green_nature") or 0) >= 2)
    r = reasons.stop_reasons(POP, delta(green_nature=0.4), garden, loved=[], feelings=["restored"], rated=[],
                             interests=["Nature"], n_choices=0)
    assert r[0]["you"] == "You go out to feel restored, and this has green space."
    assert r[1]["you"] == "It fits your interest in nature."
    assert len(reasons.stop_reasons(POP, delta(green_nature=0.4), garden, loved=[], feelings=["restored"], rated=[],
                                    interests=["Nature"], n_choices=5)) == 2


def test_feel_line_reads_as_a_day():
    stops = [{"moment_id": "m_st_dunstan_garden" if "m_st_dunstan_garden" in BY_ID else next(iter(BY_ID)),
              "predicted": 0.1, "lunch": False},
             {"moment_id": "lunch@start", "predicted": None, "lunch": True},
             {"moment_id": "m_waterloo_bridge_sunset", "predicted": 0.9, "lunch": False}]
    line = reasons.feel_line(stops, BY_ID)
    assert line[0].isupper() and ", lunch, then " in line and line.endswith("the river")
    assert reasons.feel_line(stops[1:], BY_ID).startswith("Lunch to start, then ")
    assert reasons._mid("The view from the top of Greenwich Park") == "the view from the top of Greenwich Park"
    assert reasons.feel_line([], BY_ID) == ""


def _plan(client, h, **kw):
    r = client.post("/v1/me/plans", headers=h, json={"start": {"lat": 51.507819, "lon": -0.126137},
                                                     "start_name": "Charing Cross station", "date": "2026-10-31", **kw})
    assert r.status_code == 201, r.text
    return r.json()


def test_the_app_plan_carries_reasons_but_the_blind_one_does_not(client):
    h, _ = install(client)
    client.post("/v1/me/swipes", headers=h, json={"items": [{"item": 2, "reaction": "loved"}]})
    assert client.put("/v1/me/profile", headers=h, json={"why_travel": ["curious", "peaceful"]}).status_code == 204
    w = client.get("/v1/me/weights", headers=h).json()
    assert w["n_observations"] == 3                       # the swipe and the two feelings
    p = _plan(client, h)
    assert p["feel_line"] and p["blind"] is False
    assert p["basis"] == {"places": 1, "choices": 0, "ratings": 0, "feelings": 2}
    rateable = [s for s in p["stops"] if s["rateable"]]
    assert rateable and all(s["reasons"] and s["reasons"][0]["you"] for s in rateable)
    b = _plan(client, h, blind=True)
    assert b["blind"] is True and b["feel_line"] is None and b["basis"] is None
    assert all(not s.get("reasons") and not s["chosen_for"] and s["worth_gbp"] is None for s in b["stops"])


def test_rating_a_food_card_served_as_lunch(client):
    h, _ = install(client)
    r = client.post("/v1/me/ratings", headers=h, json={"moment_id": "m_waterloo_bridge_sunset#lunch", "rating": 4})
    assert r.status_code == 201
    ratings = client.get("/v1/admin/export", headers=ADMIN).json()["ratings"]
    assert ratings[-1]["moment_id"] == "m_waterloo_bridge_sunset"
