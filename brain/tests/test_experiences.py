"""The place and experience standard (batch 9, m364): the reference places pass it, and it rejects what it should."""

from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from brain.experiences import (Claim, Score, appeals, atmosphere, hard_facts, legacy_tags, load_places, problems,
                               unverified_hard)
from brain.moments import load_moments

DATA = Path(__file__).resolve().parents[1] / "data"
TODAY = date(2026, 11, 28)


@pytest.fixture(scope="module")
def places():
    return {p.id: p for p in load_places(DATA / "places")}


@pytest.fixture(scope="module")
def cards():
    return {m.id: m for m in load_moments(DATA / "moments")}


def test_the_seven_reference_places_pass_the_standard(places, cards):
    assert set(places) == {"p_tate_modern", "p_borough_market", "p_natural_history_museum", "p_british_museum",
                           "p_hyde_park", "p_sky_garden", "p_liberty"}
    for p in places.values():
        assert problems(p, card_ids=set(cards)) == [], p.id


def test_tate_modern_is_art_not_history(places):
    """Abram (m364): Tate Modern needs a genuine art dimension, not the history tag."""
    e = places["p_tate_modern"].experience("e_collection")
    assert e.primary == ("art",)
    assert e.score("art") == 2 and e.score("history") == 0
    assert legacy_tags(places["p_tate_modern"])["history_culture"] == 0


def test_borough_market_history_is_secondary_and_sourced(places):
    """Abram (m364): not a strong historical experience without evidence. With the market's own story, it's a 1."""
    p = places["p_borough_market"]
    e = p.experience("e_graze")
    assert e.primary == ("food_discovery",)
    assert e.score("history") == 1 and "history" in e.secondary
    assert appeals(p, e)["history"].status == "verified"


def test_a_place_holds_several_experiences_with_their_own_appeals(places):
    nhm = places["p_natural_history_museum"]
    ready = {e.id: e for e in nhm.ready()}
    assert {"e_mammals", "e_dinosaurs", "e_hintze_hall", "e_family_trail"} <= set(ready)
    assert ready["e_family_trail"].primary == ("play",)
    assert ready["e_dinosaurs"].primary == ("science",)
    # A draft experience (the founder's approach, with gaps) is recorded but never ready.
    assert nhm.experience("e_approach").status == "draft"


def test_unknown_is_not_zero(places):
    """The NHM's building page failed: architecture is unknown, and an unknown is left out of the appeals."""
    p = places["p_natural_history_museum"]
    e = p.experience("e_hintze_hall")
    assert e.score("architecture") == "unknown"
    assert "architecture" not in appeals(p, e)
    assert e.score("nightlife") == "unknown"   # never assessed at all


def test_hard_rules_use_verified_current_facts_only(places):
    bm = places["p_british_museum"]          # every page refused the fetch: researched only
    assert hard_facts(bm, TODAY) == {}
    assert {c.fact_type for c in unverified_hard(bm, TODAY)} == {"hours", "closure"}
    nhm = places["p_natural_history_museum"]
    assert {"hours", "closure"} <= set(hard_facts(nhm, TODAY))
    # Hours expire after 90 days: the same verified fact stops driving a rule, and drops to medium.
    later = date(2027, 3, 30)
    assert "hours" not in hard_facts(nhm, later)
    hours = next(c for c in nhm.facts if c.id == "nhm_hours")
    assert hours.current_confidence(later) == "medium"


def test_interpretations_are_capped(places):
    """'Grand' from an official 25-metre fact is a researched reading, never verified."""
    p = places["p_natural_history_museum"]
    a = atmosphere(p, p.experience("e_hintze_hall"))
    assert a["grand"].value == 2 and a["grand"].status == "researched"


def test_atmosphere_by_window(places):
    p = places["p_borough_market"]
    e = p.experience("e_graze")
    assert e.atmos("crowded", "saturday_afternoon") == 2
    assert e.atmos("crowded", "weekday_morning") == "unknown"   # not said: unknown, not quiet


def _tate(places):
    return places["p_tate_modern"]


def _with_exp(place, **changes):
    e = replace(place.experience("e_collection"), **changes)
    return replace(place, experiences=(e,), legacy_from=("e_collection",))


def test_the_standard_rejects_three_primary_appeals(places):
    p = _tate(places)
    e = p.experience("e_collection")
    bad = _with_exp(p, primary=("art", "history", "culture"))
    assert any("at most 2" in x for x in problems(bad))
    assert e.primary == ("art",)


def test_the_standard_rejects_a_primary_from_inference(places):
    p = _tate(places)
    guess = Claim(id="g", claim="guess", kind="fact", fact_type="contents", status="inferred", source=None,
                  source_type="odys", checked=TODAY, confidence="low", central=True)
    e = p.experience("e_collection")
    bad = _with_exp(p, claims=e.claims + (guess,), scores={**e.scores, "views": Score(2, ("g",))},
                    primary=("art", "views"))
    msgs = problems(bad)
    assert any("views = 2 rests only on inferred" in x for x in msgs)


def test_the_standard_rejects_a_score_without_a_source(places):
    p = _tate(places)
    e = p.experience("e_collection")
    bad = _with_exp(p, scores={**e.scores, "views": Score(1)})
    assert any("views = 1 cites no claim" in x for x in problems(bad))


def test_the_standard_rejects_verified_interpretations_and_crowd_labels(places):
    p = _tate(places)
    e = p.experience("e_collection")
    interp = Claim(id="i", claim="peaceful", kind="interpretation", fact_type="interpretation", status="verified",
                   source="x", source_type="official", checked=TODAY, confidence="high")
    crowd = Claim(id="c", claim="halal", kind="fact", fact_type="contents", status="verified", source="overture",
                  source_type="crowd_label", checked=TODAY, confidence="high")
    msgs = problems(_with_exp(p, claims=e.claims + (interp, crowd)))
    assert any("interpretation marked verified" in x for x in msgs)
    assert any("crowd_label is above inferred" in x for x in msgs)


def test_the_standard_rejects_terms_outside_the_vocabulary(places):
    p = _tate(places)
    e = p.experience("e_collection")
    bad = _with_exp(p, scores={**e.scores, "vibes": Score(2, ("tm_art",))})
    assert any("vibes isn't in the vocabulary" in x for x in problems(bad))


def test_romantic_is_never_a_two(places):
    p = _tate(places)
    e = p.experience("e_collection")
    bad = _with_exp(p, atmosphere={**e.atmosphere, "romantic": (Score(2, ("tm_art",)),)})
    assert any("romantic = 2" in x for x in problems(bad))


def test_the_planner_still_reads_the_cards(cards):
    """Nothing in a plan changes: the cards keep their own tags (the switch waits for Abram)."""
    assert cards["m_tate_modern"].tag("history_culture") == 2
