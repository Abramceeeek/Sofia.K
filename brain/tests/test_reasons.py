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


def test_one_feeling_alone_is_enough_to_say_so():
    post = update_person(POP, [reasons.feeling_observation(POP, "curious")])
    history = next(mm for mm in BY_ID.values() if (mm.features.place.get("history_culture") or 0) >= 2)
    r = reasons.stop_reasons(POP, post.mean, history, loved=[], feelings=["curious"], rated=[], interests=[],
                             n_choices=0)
    assert r[0]["you"] == "You go out to feel curious, and this has history."


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


def test_the_line_beside_the_price_names_factors_and_never_a_chance():
    """m275 (Abram, 12 Nov): "Recommended because you enjoy architecture and prefer quieter experiences", not "A strong
    match for you": the factors from the person's own answers that raise this stop, by the same rules as the reasons."""
    boat = next(i for i, (_, cards, *_) in CARDS.items() if "m_uber_boat_west_day" in cards)
    line = lambda m, d, **kw: reasons.factor_line(POP, d, m, **{"loved": [], "feelings": [], "interests": [],
                                                                "n_choices": 0, **kw})
    assert line(BY_ID["m_uber_boat_west_day"], delta(), loved=[loved(boat)]) == "Recommended because you loved it"
    bridge = BY_ID["m_waterloo_bridge_sunset"]
    assert line(bridge, delta(movement_views=0.6)) == "Recommended because of your lean towards views"
    # no lean of their own on what the stop has: it says the stop fits the route and hours, and claims nothing
    assert line(bridge, delta()) == reasons.NOT_YET
    assert line(bridge, delta(movement_views=0.1)) == reasons.NOT_YET          # under the clear-lean line
    garden = next(mm for mm in BY_ID.values() if (mm.features.place.get("green_nature") or 0) >= 2)
    # a feeling they picked is itself the evidence, as in the reasons
    assert line(garden, delta(green_nature=0.1), feelings=["restored"]) == \
        "Recommended because of your lean towards green space"
    assert line(garden, delta(green_nature=0.4), interests=["Nature"]) == \
        "Recommended because of your interest in nature and your lean towards green space"
    quiet = next(mm for mm in BY_ID.values() if not (mm.features.moment.get("crowds") or mm.features.place.get("crowds")))
    assert line(quiet, delta(crowds=-0.5), n_choices=5) == "Recommended because of your pick of quieter days"
    assert line(quiet, delta(crowds=-0.5), n_choices=0) == reasons.NOT_YET     # no this-or-that answers: not said
    for m in BY_ID.values():                                                   # never a chance, a % or a match word
        text = line(m, delta(movement_views=0.6, history_culture=0.5, crowds=-0.5), n_choices=5)
        assert "%" not in text and "match" not in text and "chance" not in text and not text.endswith(".")


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
    assert p["basis"] == {"places": 1, "choices": 0, "ratings": 0, "feelings": 2, "kinds": 0}
    rateable = [s for s in p["stops"] if s["rateable"]]
    assert rateable and all(s["reasons"] and s["reasons"][0]["you"] for s in rateable)
    assert all(s["match"].startswith(("Recommended because", "Chosen to fit")) for s in rateable)   # m275
    assert not any(s["match"] for s in p["stops"] if not s["rateable"])
    b = _plan(client, h, blind=True)
    assert b["blind"] is True and b["feel_line"] is None and b["basis"] is None
    assert all(not s.get("reasons") and not s["chosen_for"] and s["worth_gbp"] is None and s["match"] is None
               for s in b["stops"])


def test_rating_a_food_card_served_as_lunch(client):
    h, _ = install(client)
    r = client.post("/v1/me/ratings", headers=h, json={"moment_id": "m_waterloo_bridge_sunset#lunch", "rating": 4})
    assert r.status_code == 201
    ratings = client.get("/v1/admin/export", headers=ADMIN).json()["ratings"]
    assert ratings[-1]["moment_id"] == "m_waterloo_bridge_sunset"


def test_a_stored_plan_keeps_each_stops_prediction_but_the_app_is_never_sent_it(client):
    """m276: the evaluation pairs ratings with the prediction made before the visit, so the stored plan keeps it; the
    app gets no raw model score (Abram, m224)."""
    h, _ = install(client)
    p = _plan(client, h)
    assert not any("predicted" in s for s in p["stops"])
    stored = client.get("/v1/admin/export", headers=ADMIN).json()["plans"][-1]
    assert stored["id"] == p["id"]
    places = [s for s in stored["stops"] if s["rateable"]]
    assert places and all(isinstance(s["predicted"], float) for s in places)
    assert all(s["predicted"] is None for s in stored["stops"] if not s["rateable"])
    listed = client.get("/v1/me/plans", headers=h).json()
    one = client.get(f"/v1/me/plans/{p['id']}", headers=h).json()
    assert "predicted" not in str(listed) and "predicted" not in str(one)   # stored plans read back without it


def test_a_loved_place_is_named_only_for_the_feature_that_defines_it():
    """m353 (three reviews, 25 Nov: "You loved Sky Garden, and this has green space" on a bike loop; Abram: "It must not
    invent a connection between two unrelated places"): the Sky Garden's green space is a 1, not what it is."""
    sky = next(i for i, (name, *_) in CARDS.items() if name == "Sky Garden")
    bike = BY_ID["m_park_bike_loop_hyde"]
    r = reasons.stop_reasons(POP, delta(green_nature=0.6), bike, loved=[loved(sky)], feelings=[], rated=[],
                             interests=[], n_choices=0)
    assert not any("Sky Garden" in x["you"] for x in r)
    boat = next(i for i, (_, cards, *_) in CARDS.items() if "m_uber_boat_west_day" in cards)
    r = reasons.stop_reasons(POP, delta(movement_views=0.6), BY_ID["m_waterloo_bridge_sunset"], loved=[loved(boat)],
                             feelings=[], rated=[], interests=[], n_choices=0)
    assert r[0]["you"].endswith("and this has views too.")        # the boat is views: a real connection
