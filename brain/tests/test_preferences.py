"""Batch 9 (Abram, m364): preference intelligence and uncertainty in the match engine. Shadow mode throughout.

Each test names the rule it holds. The engine is called directly so each instruction's time, source and context is
set exactly; `test_match.py` covers the same engine through the API.
"""
from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from brain import match as engine
from brain.aspiration import load_aspiration
from brain.config import DATA_DIR
from brain.dayplan import load_card_kinds
from brain.experiences import load_places
from brain.moments import load_moments
from brain.population import load_population

FRI = engine.Day(weekday="fri", date="2026-12-04")
SAT = engine.Day(weekday="sat", date="2026-12-05")
T0 = datetime(2026, 10, 1, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def world():
    pop = load_population(DATA_DIR / "priors.yaml")
    cards = {m.id: m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"}
    kinds = load_card_kinds(DATA_DIR / "catalogue" / "london.yaml")
    know = engine.Knowledge.build(load_places(DATA_DIR / "places"), kinds, "2026-12-04")
    amap = load_aspiration(DATA_DIR / "aspiration.yaml")
    return pop, cards, know, amap, kinds


def person(pop, leans=None, sd=0.2, **kw):
    """A traveller whose answers moved the named features clearly (δ with a narrow posterior)."""
    names = pop.personal_names
    delta = np.zeros(len(names))
    dsd = pop.delta_prior_sd.copy()
    for f, v in (leans or {}).items():
        delta[names.index(f)] = v
        dsd[names.index(f)] = sd
    kw.setdefault("n_answers", 8)
    return engine.Traveller(delta=delta, delta_sd=dsd, **kw)


def I(kind, target, days=0, label="", **kw):
    return engine.Instruction(kind, target, T0 + timedelta(days=days), kw.pop("source", "swipe"), label or target, **kw)


def judge(world, t, card, day=FRI):
    pop, cards, know, amap, _ = world
    return engine.match(pop, t, cards[card], day, amap=amap, know=know)


# ---- A: preference levels ------------------------------------------------------------------------------------------

def test_a_place_dislike_is_a_strong_negative_never_a_ban(world):
    t = person(world[0], instructions=(I("dislike_place", "m_bm_great_court", label="British Museum"),))
    r = judge(world, t, "m_bm_great_court")
    assert r.cls == "poor_match" and not r.restrictions
    assert r.score == pytest.approx(r.model_score - engine.DISLIKE_PLACE)
    assert r.against == "You said you didn't enjoy British Museum."


def test_one_disliked_museum_doesnt_exclude_all_museums(world):
    """The batch 8 review: one "didn't enjoy" at the British Museum removed all 15 museums."""
    pop, cards, know, amap, kinds = world
    t = person(pop, {"history_culture": 0.6},
               instructions=(I("dislike_place", "m_bm_great_court", label="British Museum"),))
    museums = [c for c, k in kinds.items() if k == "museum" and c in cards and c != "m_bm_great_court"]
    out = [judge(world, t, c) for c in museums]
    assert len(out) >= 10
    assert not any(any("didn't enjoy" in x for x in r.restrictions) for r in out)
    # a similar museum loses a little; a museum about something else (the NHM: science) loses nothing
    nhm = judge(world, t, "m_nhm_whale_hall")
    assert nhm.score == pytest.approx(nhm.model_score)
    assert sum(r.cls == "not_suitable" for r in out) == sum(bool(r.restrictions) for r in out)


def test_a_similar_experience_loses_a_little_by_how_similar(world):
    pop = world[0]
    t = person(pop, instructions=(I("dislike_place", "m_national_gallery", label="the National Gallery"),))
    r = judge(world, t, "m_courtauld_gallery")      # another gallery, both known only by their cards
    assert r.score == pytest.approx(r.model_score - engine.DISLIKE_SIMILAR * 0.5)
    assert r.against == "You didn't enjoy the National Gallery, and this is a similar kind of place."
    assert not r.restrictions
    # the planner's own caveat: they loved another gallery, so the penalty halves and isn't said as a reason
    t2 = person(pop, instructions=(I("dislike_place", "m_national_gallery", label="the National Gallery"),
                                   I("love_place", "m_tate_modern", label="Tate Modern")))
    r2 = judge(world, t2, "m_courtauld_gallery")
    assert r2.model_score - r2.score < r.model_score - r.score
    assert r2.against is None or "similar kind" not in r2.against


def test_an_explicit_category_dislike_is_respected_until_changed(world):
    pop, cards, know, amap, kinds = world
    no_museums = I("dislike_kind", "museum", days=10, label="museums", source="request")
    t = person(pop, instructions=(no_museums,))
    for c in [c for c, k in kinds.items() if k == "museum" and c in cards]:
        r = judge(world, t, c)
        assert r.cls == "not_suitable" and r.basis == "your instruction", c
        assert "you asked for no museums" in r.restrictions[0]
    # changed: a newer request for one museum wins over the older "no museums"
    t2 = person(pop, instructions=(no_museums, I("must_go", "m_science_museum", days=11, source="request")))
    assert judge(world, t2, "m_science_museum").cls == "must_go"
    assert judge(world, t2, "m_nhm_whale_hall").cls == "not_suitable"


# ---- recency: the newest, most specific instruction wins, under hard rules -------------------------------------------

def test_a_current_must_go_beats_an_older_dislike(world):
    t = person(world[0], instructions=(I("dislike_place", "m_bm_great_court", label="British Museum"),
                                       I("must_go", "m_bm_great_court", days=30, source="request")))
    r = judge(world, t, "m_bm_great_court")
    assert r.cls == "must_go" and r.reason == "Included because you specifically asked to visit."
    assert r.preferences[0]["decides"] and "the newer request wins" in r.preferences[0]["note"]
    assert r.preferences[1] == {"instruction": "dislike_place", "about": "British Museum", "source": "swipe",
                                "at": T0.isoformat(), "decides": False, "overridden_by": "must_go"}


def test_a_current_avoid_beats_an_older_must_go(world):
    pop = world[0]
    asked = I("must_go", "m_sky_garden", days=1, source="request")
    not_now = I("avoid", "m_sky_garden", days=2, label="the Sky Garden", source="request")
    r = judge(world, person(pop, instructions=(asked, not_now)), "m_sky_garden")
    assert r.cls == "not_suitable" and r.restrictions == ["explicit exclusion: you asked not to visit the Sky Garden"]
    # and the other way round: asked again after saying no, the request wins
    again = I("must_go", "m_sky_garden", days=3, source="request")
    assert judge(world, person(pop, instructions=(asked, not_now, again)), "m_sky_garden").cls == "must_go"


def test_a_request_never_beats_a_hard_rule(world):
    pop, cards, *_ = world
    t = person(pop, children=(8,), kept_out={"m_park_bike_loop_hyde": "a minimum age, with children"},
               instructions=(I("must_go", "m_park_bike_loop_hyde", days=5, source="request"),))
    r = judge(world, t, "m_park_bike_loop_hyde")
    assert r.cls == "not_suitable" and r.restrictions[0] == "you asked for it, but a hard rule applies"
    assert r.basis == "planner rule"      # not "verified" (the batch 8 review)


def test_the_planners_kind_rule_is_a_penalty_here_not_a_restriction(world):
    pop = world[0]
    t = person(pop, kept_out={"a_greenwich_market": "kinds they didn't enjoy: market"},
               instructions=(I("dislike_place", "a_portobello_saturday", label="Portobello Road"),))
    r = judge(world, t, "a_greenwich_market", SAT)
    assert not r.restrictions and r.score < r.model_score


def test_basis_is_verified_only_for_a_verified_fact(world):
    pop = world[0]
    t = person(pop)
    closed = engine.Day(weekday="fri", date="2026-12-25")     # the NHM is closed 24-26 Dec (verified)
    r = judge(world, t, "m_nhm_whale_hall", closed)
    assert r.cls == "not_suitable" and r.basis == "verified"
    bm = judge(world, t, "m_bm_great_court", FRI)              # researched only: said, never applied
    assert any("not verified" in w for w in bm.warnings)


# ---- context -------------------------------------------------------------------------------------------------------

def test_a_negative_said_in_one_context_counts_half_in_another(world):
    pop = world[0]
    low = I("rated", "m_borough_market_graze", value=2, source="rating", label="Borough Market",
            context=(("window", "weekend"),))
    t = person(pop, instructions=(low,))
    sat, fri = judge(world, t, "m_borough_market_graze", SAT), judge(world, t, "m_borough_market_graze", FRI)
    assert sat.model_score - sat.score == pytest.approx(engine.DISLIKE_PLACE)
    assert fri.model_score - fri.score == pytest.approx(engine.DISLIKE_PLACE * engine.CONTEXT_OTHER)
    assert "said about a weekend visit; this is a weekday" in fri.against


# ---- B and missing evidence: the uncertainty axis -------------------------------------------------------------------

def test_missing_is_not_negative(world):
    """Abram (m364): the history enthusiast was told "Your answers lean away from good food" for Borough Market. With
    no evidence either way about food, that's uncertainty, never a poor match."""
    pop = world[0]
    t = person(pop, {"history_culture": 0.7}, fields=frozenset({"history_culture"}))
    r = judge(world, t, "m_borough_market_graze")
    assert r.cls == "low_confidence"
    assert "food_discovery" in r.confidence["missing"]
    assert not r.against or "lean away from" not in r.against
    assert any("whether you enjoy trying food" in x for x in r.missing)
    # the market's verified long history is a secondary appeal they do care about: recorded as a positive
    fit = r.experiences[0]["fit"]
    assert fit["history"]["traveller"] == "positive" and fit["history"]["role"] == "secondary"


def test_a_clear_negative_on_a_primary_appeal_is_a_poor_match(world):
    t = person(world[0], {"food": -0.8})
    r = judge(world, t, "m_borough_market_graze")
    assert r.cls == "poor_match"
    assert r.against == "Your answers lean away from trying food, and that's what Grazing the stalls is about."


def test_conflicting_evidence_is_low_confidence_with_both_sides(world):
    """Abram's table: likes food, dislikes crowds; food 2 and crowded 2, both evidenced (a Saturday)."""
    t = person(world[0], {"crowds": -0.8}, fields=frozenset({"food"}))
    r = judge(world, t, "m_borough_market_graze", SAT)
    assert r.cls == "low_confidence" and "the evidence conflicts" in r.confidence["why_low"]
    assert r.reason and "food" in r.reason
    assert r.against.endswith("this place is busy on Saturday afternoons.")


def test_no_answers_is_low_confidence_everywhere(world):
    pop, cards, *_ = world
    t = person(pop, n_answers=0)
    out = [judge(world, t, c) for c in cards]
    judged = [r for r in out if r.cls != "not_suitable"]
    assert judged and all(r.cls == "low_confidence" and r.reason is None for r in judged)


def test_confidence_reads_the_posterior(world):
    """The predictive spread: with no answers it's the prior's (ratio 1); clear answers on a place's features narrow
    it. Confidence is a level with its parts, never a probability."""
    pop = world[0]
    none = judge(world, person(pop, n_answers=0), "m_park_break_hyde")
    some = judge(world, person(pop, {"green_nature": 0.7, "outdoor_exposure": 0.4}, sd=0.15), "m_park_break_hyde")
    assert none.confidence["predictive_ratio"] == pytest.approx(1.0)
    assert some.confidence["predictive_ratio"] < none.confidence["predictive_ratio"]
    for r in (none, some):
        assert r.confidence["level"] in ("low", "medium", "high")
        assert not any(k in r.confidence for k in ("probability", "chance", "p_good"))


def test_your_answers_needs_a_clear_sign(world):
    """A lean the posterior isn't sure of (wide spread) is "most people", never "your answers" (the batch 8 review)."""
    pop = world[0]
    unsure = person(pop, {"food": -0.3}, sd=0.7)
    assert engine.lean(pop, unsure, "food") == (0, pytest.approx(engine._phi(0.3 / 0.7)))
    r = judge(world, unsure, "m_borough_market_graze")
    assert r.cls != "poor_match" and not (r.against or "").startswith("Your answers lean away from trying food")


# ---- experiences and evidence ---------------------------------------------------------------------------------------

def test_different_travellers_get_different_classes_for_one_place(world):
    pop = world[0]
    art = person(pop, instructions=(I("love_place", "m_tate_modern", label="Tate Modern"),))
    history = person(pop, {"history_culture": 0.7}, fields=frozenset({"history_culture"}))
    no_art = person(pop, instructions=(I("dislike_place", "m_tate_modern", label="Tate Modern"),))
    got = {k: judge(world, t, "m_tate_modern").cls for k, t in (("art", art), ("history", history),
                                                                  ("no_art", no_art))}
    assert got == {"art": "strong_match", "history": "low_confidence", "no_art": "poor_match"}
    # the history lover isn't told Tate Modern is history (it's art now): ODYS says it doesn't know about art
    h = judge(world, history, "m_tate_modern")
    assert "art" in h.confidence["missing"] and h.reason is None


def test_a_loved_place_lifts_its_primary_appeals_and_says_where_it_came_from(world):
    pop = world[0]
    art = person(pop, instructions=(I("love_place", "m_tate_modern", label="Tate Modern"),))
    ev = engine.dim_evidence(pop, art, world[2])
    assert ev["art"][0]["sign"] == 1 and "you loved Tate Modern" in ev["art"][0]["from"]
    assert "history" not in ev       # Tate Modern's appeals don't spill onto history


def test_reasons_rest_on_evidence_and_card_only_places_are_never_strong(world):
    pop, cards, know, amap, _ = world
    t = person(pop, {"food": 0.7, "green_nature": 0.6, "movement_views": 0.6, "history_culture": 0.5},
               fields=frozenset({"food", "nature"}), instructions=(I("love_place", "m_sky_garden", label="Sky Garden"),))
    out = [judge(world, t, c) for c in cards]
    for r in out:
        if r.reason:
            assert r.evidence and all(e["traveller"] and e["place"] for e in r.evidence), r.place
            src = r.evidence[0]["place_source"]
            if r.place in know.records and src == "place record":
                assert r.evidence[0]["place"].split("(")[-1].rstrip(")") in ("verified", "researched")
            if r.place not in know.records:
                assert src in ("card (inferred)", "your request", "your own answer"), (r.place, src)
        if r.cls == "strong_match":
            assert r.place in know.records or r.preferences and r.preferences[0]["decides"], r.place
            assert r.score >= engine.STRONG or r.preferences[0]["instruction"] in ("love_place", "rated"), r.place


def test_a_loved_place_the_model_scores_low_is_flagged_not_hidden(world):
    pop = world[0]
    t = person(pop, {"history_culture": -0.9, "iconic": -0.9, "crowds": -0.9},
               instructions=(I("love_place", "m_tate_modern", label="Tate Modern"),))
    r = judge(world, t, "m_tate_modern")
    assert r.cls == "strong_match" and r.reason == "You loved Tate Modern."
    assert r.misfit == (r.model_score < engine.FLOOR)


def test_matches_change_no_card(world):
    """Shadow mode: judging places reads the cards and the records, and changes neither."""
    pop, cards, *_ = world
    before = {c: dict(m.features.place) for c, m in cards.items()}
    for c in list(cards)[:20]:
        judge(world, person(pop, {"food": 0.5}), c)
    assert {c: dict(m.features.place) for c, m in cards.items()} == before
