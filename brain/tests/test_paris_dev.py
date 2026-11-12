"""m246: Paris as a development destination (Abram, m244): checked facts with sources, unknowns left unknown, no
London assumptions, and never offered to anyone until its readiness is reviewed."""
from brain.catalogue import TAXONOMY, load_dev
from brain.config import DATA_DIR
from brain.places import load_destinations

DEST, XS, RAW = load_dev("paris")
READY = [x for x in XS if x.status == "ready"]


def test_paris_is_never_offered():
    assert "paris" not in load_destinations(DATA_DIR / "destinations.yaml")    # not a trip destination
    assert not (DATA_DIR / "catalogue" / "paris.yaml").exists()                # not in the served catalogue


def test_its_own_country_currency_and_clock():
    assert (DEST.country, DEST.currency, DEST.timezone) == ("FR", "EUR", "Europe/Paris")
    for x in XS:
        assert x.id.startswith("xp:fr:paris:") and not x.problems(), x.id
        assert x.geo.timezone == "Europe/Paris" and 48.80 < x.geo.lat < 48.91 and 2.22 < x.geo.lon < 2.47, x.id
        if x.price.known:
            assert x.price.value.currency == "EUR", x.id                       # never pounds


def test_every_ready_experience_has_a_checked_location_and_hours_with_their_sources():
    assert 19 <= len(READY) and len(XS) >= 20
    for x in READY:
        assert x.place_id.startswith(("wikidata:Q", "osm")), x.id
        if getattr(x.facet, "event_based", False):                            # a concert or film: sessions, not hours
            assert x.facet.sessions.known and x.facet.sessions.source.startswith("https://"), x.id
        else:
            assert x.hours.trust == "checked" and x.hours.source.startswith("https://"), x.id
        for f in (x.price, x.accessibility.step_free, x.geo.area):
            assert not f.known or f.source, x.id
    for x in XS:
        if not x.hours.text and not getattr(x.facet, "event_based", False):
            assert x.status == "draft", x.id                                   # never assumed open


def test_a_diverse_catalogue_not_just_landmarks():
    cats = {x.category for x in READY}
    assert {"culture", "nature", "food_drink", "shopping", "entertainment", "neighbourhood", "views"} <= cats
    assert all(x.type in TAXONOMY[x.category] for x in XS)
    assert sum(1 for x in READY if x.features.get("local_novel", 0) >= 2) >= 5   # unusual and local, not only famous


def test_unknowns_stay_unknown_and_nationality_prices_are_a_range():
    assert {x.id.split(":")[-1] for x in READY if not x.accessibility.step_free.known} >= {"rodin", "carnavalet"}
    sc = next(x for x in XS if x.id.endswith("sainte-chapelle"))
    assert sc.price.value.amount == 22 and "never asks nationality" in RAW["experiences"]["sainte_chapelle"]["price"]["quote"]
    assert next(x for x in XS if x.id.endswith("catacombes")).accessibility.step_free.value == "no"
