"""m239 (WS4): discovering places without a generic feed, and the ODYS quality standard (m234) in code. Three
synthetic tastes over London's checked catalogue and the synthetic Testville. At most three suggestions each, each
with reasons from the inputs that chose it."""
from dataclasses import replace
from datetime import date

import numpy as np
import pytest

from brain import discovery as dv, quality
from brain.config import DATA_DIR
from brain.destination import Emergency, Profile
from brain.population import load_population

from test_destination import LONDON, TEST

POP = load_population(DATA_DIR / "priors.yaml")
TODAY, MONDAY = date(2026, 11, 10), date(2026, 11, 16)


def persona(**w):
    d = np.zeros(len(POP.delta_prior_sd))
    for k, v in w.items():
        d[POP.names.index(k)] = v
    return dv.Scorer(POP, d)


VIEWS = persona(movement_views=2.0, awe=2.0, photo_potential=1.5)
CULTURE = persona(history_culture=2.0, absorption=1.5)
FOOD = persona(food=2.5, local_novel=1.0, social_pull=1.0)
X = {x.legacy_ids[0]: x for x in LONDON.experiences}


def _reasons_are_grounded(sgs):
    assert len(sgs) <= dv.LIMIT
    for sg in sgs:
        assert 1 <= len(sg.why) <= dv.LIMIT and not any("%" in w and "simulated" not in w for w in sg.why)


def test_a_strong_match_that_is_closed_unaffordable_or_unverified_never_outranks_a_sound_one():
    soane, gallery = X["m_soane_museum"], X["m_national_gallery"]       # Soane: closed Mondays and Tuesdays
    a = quality.assess(soane, p_good=0.95, today=TODAY, day=MONDAY)
    b = quality.assess(gallery, p_good=0.55, today=TODAY, day=MONDAY)
    assert a.practicality == quality.Perspective("poor", "Closed on Mondays.") and not a.recommendable
    assert [x for x, _ in quality.rank([(soane, a), (gallery, b)])] == [gallery, soane]
    kart = quality.assess(X["m_go_karting_canary_wharf"], p_good=0.9, today=TODAY, budget_left=20)
    assert kart.money.level == "poor" and "more than the 20" in kart.money.reason
    assert quality.assess(X["m_borough_market_graze"], p_good=0.8, today=TODAY).money.level == "fair"   # estimate
    old = replace(gallery, provenance=replace(gallery.provenance, checked="2025-06-01"))
    assert quality.trust(old, TODAY).level == "poor"                  # over a year since anyone checked
    synthetic = TEST.experiences[0]
    assert quality.trust(synthetic, TODAY) == quality.Perspective("poor", "Test data, not a checked place.")
    assert quality.relevance(None).level == "unknown" and quality.relevance(0.8).reason == "A strong match for you."


def test_what_fits_ninety_minutes_and_no_money_on_a_monday():
    for s in (VIEWS, CULTURE, FOOD):
        sgs = dv.fits(s, LONDON, 90, 0, TODAY, day=MONDAY)
        _reasons_are_grounded(sgs)
        assert all(sg.assessment.recommendable for sg in sgs)
        for sg in sgs:
            x = next(e for e in LONDON.experiences if e.id == sg.id)
            assert x.price.value.amount == 0 and x.duration.max_minutes <= 90 and x.hours.open_on("mon") is not False
    assert dv.fits(VIEWS, LONDON, 90, 0, TODAY, day=MONDAY)[0].why[0].startswith(
        "From your answers, it has what you like: movement and views")


def test_neighbourhoods_follow_the_persons_taste_and_only_areas_the_cards_name():
    views = [sg.title for sg in dv.neighbourhoods(VIEWS, LONDON, TODAY)]
    culture = [sg.title for sg in dv.neighbourhoods(CULTURE, LONDON, TODAY)]
    assert views != culture and len(views) <= dv.LIMIT
    for sg in dv.neighbourhoods(CULTURE, LONDON, TODAY):
        best = sg.why[0].split("the best for you is ")[1].rstrip(".")
        x = next(e for e in LONDON.experiences if e.title == best)
        assert x.geo.area.value == sg.title                           # its own record names the area


def test_hidden_local_moments_are_local_seldom_planned_and_still_a_good_match():
    shares = dv.load_popularity()
    for sg in dv.hidden_local(FOOD, LONDON, TODAY):
        x = next(e for e in LONDON.experiences if e.id == sg.id)
        assert x.features["local_novel"] >= 2 and shares.get(x.legacy_ids[0], 0) <= 0.05
        assert FOOD.p_good(x) >= quality.GOOD and any(w.startswith("Local, and in") for w in sg.why)


def test_seasons_come_only_from_dated_notes_never_from_guesses():
    assert dv.seasonal(VIEWS, LONDON, 4, TODAY) == []                  # London has no checked season notes yet
    spring = dv.seasonal(VIEWS, TEST, 4, TODAY)
    assert [sg.title for sg in spring] == ["The river path at blossom time"]
    assert "Blossom along the river path (synthetic) (synthetic test data)." in spring[0].why
    assert not spring[0].assessment.recommendable                     # test data is never trustworthy enough
    assert dv.seasonal(VIEWS, TEST, 10, TODAY) == []


def test_food_discovery_is_about_interest_in_food_never_a_diet():
    sgs = dv.food(FOOD, LONDON, TODAY)
    _reasons_are_grounded(sgs)
    words = " ".join(w for sg in sgs for w in sg.why).lower()
    assert "food" in words and not any(d in words for d in ("halal", "kosher", "vegan", "vegetarian", "allerg"))


def test_where_to_go_ranks_ready_destinations_and_names_what_the_rest_lack():
    def subset(key, name, cats):
        p = Profile(replace(LONDON.dest, key=key, name=name), dict(LONDON.parts), dict(LONDON.sources))
        p.parts["experiences"] = [x for x in LONDON.experiences if x.category in cats]
        return p
    views_city = subset("views_city", "A views city (London's views, synthetic split)", {"views", "nature"})
    museum_city = subset("museum_city", "A museum city (London's culture, synthetic split)", {"culture"})
    test = Profile(TEST.dest, dict(TEST.parts), dict(TEST.sources))
    test.parts["emergency"] = Emergency("ZZ", "Testville", (), "2026-11-10")   # numbers present, facts still synthetic
    out = dv.destinations(VIEWS, [museum_city, views_city, test, TEST], days=2, stops_a_day=3, today=TODAY)
    assert [sg.id for sg in out[:2]] == ["views_city", "museum_city"]
    assert out[0].why[0].endswith("strong matches among its best 6 moments for you.")
    assert [sg.id for sg in dv.destinations(CULTURE, [views_city, museum_city], 2, 3, TODAY)][0] == "museum_city"
    not_ready = {sg.id: sg.why[0] for sg in out[2:]}
    assert not_ready["testville"].startswith("Not ready to recommend yet")
    assert len(out[:2]) <= dv.LIMIT


@pytest.mark.parametrize("s", [VIEWS, CULTURE, FOOD])
def test_every_kind_of_discovery_stays_short_and_explained(s):
    for sgs in (dv.neighbourhoods(s, LONDON, TODAY), dv.hidden_local(s, LONDON, TODAY), dv.food(s, LONDON, TODAY)):
        assert len(sgs) <= dv.LIMIT and all(sg.why for sg in sgs)
