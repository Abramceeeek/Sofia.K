"""D119: each stop's word on "How the day moves", and "The reveal" on the arrival, both from the card alone."""
from brain import dayplan
from brain.config import DATA_DIR
from brain.moments import load_moments

from conftest import make_moment
from test_api import client  # noqa: F401  (the client fixture)


def test_the_word_comes_from_the_tags_first_rule_wins():
    assert dayplan.feel_word(None) == "Lunch"                                     # a "lunch near X" slot
    assert dayplan.feel_word(make_moment("a", 51.5, -0.1, tags=dict(food=2, crowds=2))) == "Lively"
    assert dayplan.feel_word(make_moment("b", 51.5, -0.1, tags=dict(green_nature=2, food=2))) == "Calm"
    assert dayplan.feel_word(make_moment("c", 51.5, -0.1, tags=dict(history_culture=1))) == "Easy"
    awe = make_moment("d", 51.5, -0.1, tags=dict(green_nature=2))
    awe.features.moment["awe"] = 2
    assert dayplan.feel_word(awe) == "Awe"
    assert dayplan.feel_word(awe.model_copy(update={"feel_word": "Drifting"})) == "Drifting"   # the card's own
    assert dayplan.feel_word(awe.model_copy(update={"kind": "area", "feel_word": None})) == "Wandering"


def test_every_ready_card_gets_a_word_and_strong_reveals_are_marked():
    ready = [m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"]
    words = {m.id: dayplan.feel_word(m) for m in ready}
    assert all(words.values())
    assert words["m_uber_boat_west_day"] == "Drifting" and words["m_park_break_hyde"] == "Calm"
    assert words["m_nhm_whale_hall"] == "Awe" and words["a_covent_garden_soho"] == "Wandering"
    by_id = {m.id: m for m in ready}
    assert dayplan.is_reveal(by_id["m_nhm_whale_hall"]) and not dayplan.is_reveal(by_id["m_park_break_hyde"])
    assert not dayplan.is_reveal(None)


def test_app_stops_carry_the_word_and_the_flag(client):
    day = client.get("/v1/example-day").json()
    assert all(st["feel_word"] for st in day["stops"])
    assert all(isinstance(st["reveal"], bool) for st in day["stops"])
    lunch = [st for st in day["stops"] if st["moment_id"].startswith("lunch@")]
    assert all(st["feel_word"] == "Lunch" and st["reveal"] is False for st in lunch)
