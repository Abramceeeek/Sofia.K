"""WS2 (m208): food needs, honestly. Synthetic venues only; nothing is stored or used in a plan yet."""
import json
from dataclasses import fields
from datetime import date
from pathlib import Path

import pytest
import yaml

from brain import food
from brain.food import Consent, FoodNeeds, PurposeError, VenueFood

from test_api import client  # noqa: F401  (the client fixture, m223)
from brain.places import from_osm_element

HERE = Path(__file__).parent / "fixtures"
TODAY = date(2026, 11, 7)
CONSENT = Consent("food-2026-11-draft", TODAY)


def _venues():
    raw = yaml.safe_load((HERE / "food_venues.yaml").read_text())["venues"]
    return {name: {need: VenueFood(need, **v) for need, v in (needs or {}).items()} for name, needs in raw.items()}


def test_each_need_has_its_class_and_consent_names_both_legal_grounds():
    """m232 (Abram, m224): halal and kosher potentially reveal religion; vegetarian, vegan and alcohol-free are
    assessed on context; allergies aren't a need at all. Article 6(1)(a) and Article 9(2)(a) are recorded apart."""
    assert set(food.NEED_CLASS) == set(food.NEEDS)
    assert {n for n, c in food.NEED_CLASS.items() if c == "religion"} == {"halal", "kosher"}
    assert {n for n, c in food.NEED_CLASS.items() if c == "context"} == {"vegetarian", "vegan", "no_alcohol"}
    assert not set(food.ALLERGENS) & set(food.NEEDS)            # health data: never a need ODYS keeps
    assert (CONSENT.article6, CONSENT.article9) == ("6(1)(a) consent", "9(2)(a) explicit consent")
    # every class needs the same consent: a context need without it is refused like halal
    with pytest.raises(ValueError, match="consent"):
        FoodNeeds(frozenset({"vegetarian"}))


def test_needs_are_kept_only_with_explicit_consent_and_only_offered_ones():
    with pytest.raises(ValueError, match="consent"):
        FoodNeeds(frozenset({"halal"}))
    with pytest.raises(ValueError, match="not food needs"):
        FoodNeeds(frozenset({"low_sodium"}), consent=CONSENT)
    assert FoodNeeds(frozenset()).needs == frozenset()          # no needs, nothing to consent to


def test_food_needs_serve_one_purpose_and_nothing_else():
    n = FoodNeeds(frozenset({"halal"}), consent=CONSENT)
    assert n.use("own_suggestions") == {"halal"}
    for other in ("matching", "advertising", "analytics", "group_trip"):
        with pytest.raises(PurposeError):
            n.use(other)


def test_certified_needs_a_certifier_its_listing_and_a_date_and_a_map_tag_never_is():
    with pytest.raises(ValueError, match="certifier"):
        VenueFood("halal", "certified", "venue_own", "https://example.org/x")
    with pytest.raises(ValueError):
        VenueFood("halal", "certified", "community_tag", "osm:node/1", certifier="x", verified_on=TODAY)
    with pytest.raises(ValueError, match="evidence"):
        VenueFood("halal", "whole_menu")


def test_the_words_never_claim_more_than_the_evidence():
    v = _venues()
    assert food.fit("halal", v["Example Grill"]["halal"], True, TODAY).line == \
        "Certified halal by Halal Monitoring Committee (their listing, checked 20 Oct 2026)."
    stale = food.fit("halal", v["Example Old Listing"]["halal"], False, TODAY)
    assert stale.fit == "may_suit" and "check it's current" in stale.line
    bistro = food.fit("halal", v["Example Bistro"]["halal"], True, TODAY)
    assert bistro.line == "The venue says its whole menu is halal. Not certified." and bistro.fit == "may_suit"
    veg = food.fit("vegetarian", v["Example Grill"]["vegetarian"], False, TODAY)
    assert veg.line == "The venue says some dishes are vegetarian: halloumi wrap, falafel plate."
    assert food.fit("halal", food.unknown("halal"), False, TODAY).line == \
        "Not known whether it's halal: check with the venue."


def test_a_name_or_a_cuisine_is_never_evidence():
    v = _venues()
    assert v["Halal Example Kitchen"] == {}                        # a name with "Halal" in it: nothing known
    names = {f.name for f in fields(VenueFood)}
    assert not names & {"cuisine", "owner", "neighbourhood", "photo", "name"}   # no field could carry a guess
    osm = json.loads((HERE / "overpass_sample.json").read_text())["elements"]
    turkish = food.from_place(from_osm_element(osm[2], "london", "2026-11-07"))
    assert turkish["halal"].status == "unknown"                    # cuisine=turkish says nothing about halal
    cafe = food.from_place(from_osm_element(osm[0], "london", "2026-11-07"))
    assert cafe["halal"].status == "some_dishes" and cafe["halal"].evidence == "community_tag"
    assert cafe["vegetarian"].status == "whole_menu"               # diet:vegetarian=only, as mapped, not checked
    assert "community map says" in food.fit("halal", cafe["halal"], False, TODAY).line.lower()


def test_strict_halal_gets_only_current_certification_and_flexible_gets_evidence_first():
    v = _venues()
    strict = FoodNeeds(frozenset({"halal"}), strict=frozenset({"halal"}), consent=CONSENT)
    assert [s.venue for s in food.suggest(strict, v, TODAY)] == ["Example Grill"]
    flexible = FoodNeeds(frozenset({"halal"}), consent=CONSENT)
    out = [s.venue for s in food.suggest(flexible, v, TODAY)]
    assert out[0] == "Example Grill" and "Example Pub" not in out    # not suitable: left out
    assert out.index("Halal Example Kitchen") > out.index("Example Bistro")   # unknown after "the venue says"


def test_allergies_are_never_called_safe():
    line = food.allergy_line(frozenset({"peanuts"}))
    assert "safe" not in line.replace("can't confirm what's safe", "") and "ask the venue" in line.lower()
    assert len(food.ALLERGENS) == 14 and food.allergy_line(frozenset()) == ""


def test_food_needs_are_never_stored_until_their_dpia(client):
    """m223 (Abram, 7 Nov: "Do not implement food preference persistence before its DPIA and legal review"): the old
    free-text "foods you avoid" (D19, no longer asked since D123) is accepted from older builds and dropped, never
    stored; and no profile or user field can hold a food need, a diet or an allergy."""
    from test_api import ADMIN, install
    from brain import db
    from brain.schemas import ProfileIn
    h, uid = install(client)
    r = client.put("/v1/me/profile", headers=h, json={"based": "london", "foods_avoided": "pork, peanuts"})
    assert r.status_code == 204
    me = next(u for u in client.get("/v1/admin/export", headers=ADMIN).json()["users"] if u["id"] == uid)
    assert "foods_avoided" not in (me.get("profile") or {}) and "peanuts" not in str(me)
    risky = ("diet", "halal", "kosher", "allerg", "religio", "vegan", "vegetarian")
    assert not [f for f in ProfileIn.model_fields if any(w in f for w in risky)]
    assert not [c for c in db.User.__table__.columns.keys() if any(w in c for w in risky + ("food",))]


def test_an_old_app_sending_the_retired_field_is_counted_and_never_logged(client, caplog):
    """m251, m257 (Abram, m244, m252): build 91 and Android 21 still send `foodsAvoided` with a profile save. The branch
    Brain drops it and keeps only an aggregate count, reported by the admin audit: no log line, no user, no value."""
    import logging
    from test_api import ADMIN, install
    h, _ = install(client)
    before = client.get("/v1/admin/audit/foods-avoided", headers=ADMIN).json()["old_app_saves_dropped_since_start"]
    with caplog.at_level(logging.DEBUG):
        client.put("/v1/me/profile", headers=h, json={"based": "london", "foods_avoided": "no pork, peanuts"})
        client.put("/v1/me/profile", headers=h, json={"based": "london"})
    assert not [r for r in caplog.records if "foods_avoided" in r.getMessage() and "audit" not in r.getMessage()]
    assert "pork" not in caplog.text and "peanuts" not in caplog.text
    after = client.get("/v1/admin/audit/foods-avoided", headers=ADMIN).json()
    assert after["old_app_saves_dropped_since_start"] == before + 1 and after["with_key"] == 0
