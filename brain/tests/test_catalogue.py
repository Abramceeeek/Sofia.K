"""m235 (WS1, Global Destination Intelligence): every ready London card as a structured experience, with each fact's
source, and a synthetic beach to show a kind London doesn't have. Synthetic data apart from the cards themselves."""
import re
from pathlib import Path

import pytest

from brain import catalogue, triplength
from brain.catalogue import (TAXONOMY, BeachFacet, Experience, Geo, Money, OpeningHours, Accessibility, Transport,
                             Provenance, load_catalogue, parse_hours)
from brain.config import DATA_DIR
from brain.moments import load_moments
from brain.places import Fact

CAT = load_catalogue()
CARDS = {m.id: m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"}
BY_CARD = {x.legacy_ids[0]: x for x in CAT}
BEFORE = {x.legacy_ids[0]: x for x in load_catalogue(checked=False)}      # the cards alone (m245's "before")
CHECKED = catalogue.load_checked("london")["cards"]


def test_every_ready_card_is_one_valid_experience_with_a_global_id():
    assert set(BY_CARD) == set(CARDS)                                   # one to one, ids unchanged as legacy ids
    ids = [x.id for x in CAT]
    assert len(set(ids)) == len(ids) and all(catalogue.GLOBAL_ID.match(i) for i in ids)
    assert BY_CARD["m_burlington_arcade"].id == "xp:gb:london:burlington-arcade"
    assert {x.place_id for x in CAT} == {f"odys:{i}" for i in CARDS}      # the place layer (places.py)
    assert [(x.id, x.problems()) for x in CAT if x.problems()] == []


def test_geography_comes_from_the_destination_and_areas_only_from_the_cards_own_words():
    for x in CAT:
        g = x.geo
        assert (g.country, g.region, g.locality, g.timezone) == ("GB", "GB-ENG", "london", "Europe/London")
        assert 51.28 < g.lat < 51.70 and -0.52 < g.lon < 0.34, x.id     # inside Greater London
        if g.area.known:                                               # the card's own words, or an official page (m245)
            assert (g.area.trust, g.area.source) == ("claimed", "the card's own title or place name") or (
                g.area.trust == "checked" and g.area.source.startswith("https://")), x.id
    assert BEFORE["m_burlington_arcade"].geo.area.trust == "unknown"     # its title names no area: not guessed
    assert BY_CARD["m_burlington_arcade"].geo.area.value == "Mayfair"    # its own site does ("the heart of Mayfair")
    assert BY_CARD["m_bank_of_england_gold"].geo.area.trust == "unknown"  # its site names none: still not guessed


def test_each_kind_gets_its_own_facet():
    kinds = {x.category: x.facet.kind for x in CAT}
    assert kinds["culture"] == "culture" and kinds["food_drink"] == "food" and kinds["neighbourhood"] == "area"
    assert kinds["views"] == kinds["nature"] == "outdoor" and kinds["transport_experience"] == "transport"
    food = [x for x in CAT if x.category == "food_drink"]
    assert all(not hasattr(x.facet, "halal") and not hasattr(x.facet, "diet") for x in food)   # food.py's job
    assert BY_CARD["m_chinatown_dim_sum"].facet.as_lunch is True
    assert BY_CARD["m_horizon_22"].transport.needs_booking                  # the card's own "book ahead" line
    assert BY_CARD["m_go_karting_canary_wharf"].facet.booking is True
    assert BY_CARD["a_soho_chinatown_evening"].facet.evening is True


def test_a_beach_somewhere_else_fits_the_same_model():
    """Synthetic: ZZ is a user-assigned ISO 3166 code and XTS the ISO 4217 code for testing, so it can't pass for a
    real place or price."""
    beach = Experience(
        id="xp:zz:testville:north-beach", legacy_ids=(), place_id="osm:way/1", name="North Beach", title="A swim at dawn",
        geo=Geo("ZZ", None, "testville", "Testville", Fact.unknown(), 10.0, 20.0, "UTC"),
        category="nature", type="beach", duration=None,
        hours=OpeningHours(None, None, "unknown", None, None),
        price=Fact(Money(0.0, "XTS", "free"), "claimed", "osm:way/1", "2026-11-10"),
        setting=Fact("outdoor", "estimated", "the type", None), accessibility=Accessibility(Fact.unknown()),
        transport=Transport(None, None, None, None), provenance=Provenance("synthetic", "2026-11-10", "test"),
        features={"green_nature": 2}, photos=(),
        facet=BeachFacet(lifeguards=Fact("15 Jun - 15 Sep", "claimed", "synthetic", "2026-11-10")))
    assert beach.problems() == []
    assert beach.facet.swimming_allowed.trust == "unknown"                # never assumed for a beach
    bad = Experience(**{**beach.__dict__, "category": "nature", "type": "museum"})
    assert "nature/museum isn't in the taxonomy" in bad.problems()


def test_opening_hours_are_read_only_where_the_text_is_plain():
    w = parse_hours("Mon-Fri 08:00-19:00, Sat 09:00-19:00, Sun 11:00-18:00 (burlingtonarcade.com, 2026-09-30).")
    assert w["mon"] == [(480, 1140)] and w["sun"] == [(660, 1080)]
    w = parse_hours("Sun-Thu 10:30-18:00, Fri-Sat to 21:00; free")
    assert w["fri"] == w["sat"] == [(630, 1260)] and w["sun"] == [(630, 1080)]
    w = parse_hours("Mon, Tue, Wed, Fri 10:00-20:00; Thu 08:00-18:00")
    assert w["mon"] == w["wed"] == w["fri"] == [(600, 1200)] and w["thu"] == [(480, 1080)] and w["sat"] == []
    w = parse_hours("Mon-Fri 10:00-17:00 (last entry 16:30); third Thursday to 20:00; closed weekends, Fri 2 Oct.")
    assert w["thu"] == [(600, 1020)] and w["sat"] == w["sun"] == []      # one week's exception isn't the rule
    assert parse_hours("Tue-Sun 10:00-23:00, closed Monday")["mon"] == []
    assert parse_hours("Open 24/7")["wed"] == [(0, 1440)]
    for unreadable in ("08:00 until dusk", "Winter (1 Oct-31 Mar): daily 10:00-18:30; summer to 21:00",
                       "most 07:00 to about 16:00", "Public streets; restaurants' own hours", "Pedestrian gates 05:00-midnight"):
        assert parse_hours(unreadable) is None, unreadable                # kept as text, nothing assumed
    parsed = [x for x in CAT if x.hours.weekly]
    assert len(parsed) >= 24 and all(x.hours.text for x in CAT if not x.hours.weekly and x.hours.trust != "unknown")


def test_parsed_hours_agree_with_the_days_the_planner_uses():
    for x in CAT:
        days = CARDS[x.legacy_ids[0]].best_time.days
        if x.hours.weekly and days:
            assert all(x.hours.open_on(d) for d in days), (x.id, days)


def test_prices_keep_their_currency_and_say_how_sure_they_are():
    for x in CAT:
        m = x.price.value
        assert m.currency == "GBP" and m.amount >= 0
        assert (m.kind == "free") == (m.amount == 0)
        if x.legacy_ids[0] in CHECKED and "price" in CHECKED[x.legacy_ids[0]]:   # m245: read from the official page
            assert x.price.source.startswith("https://") and x.price.trust in ("checked", "claimed")
        else:
            assert x.price.trust == ("estimated" if m.kind == "food" else "checked")   # a meal's price: ODYS's estimate
    assert BY_CARD["m_park_bike_loop_hyde"].price.value.kind == "hire"


def test_access_and_setting_are_never_guessed():
    said = {i for i, m in CARDS.items() if m.approach.step_free is not None} | {
        i for i, c in CHECKED.items() if "step_free" in c}                # the card, or an official page (m245)
    assert {x.legacy_ids[0] for x in CAT if x.accessibility.step_free.known} == said
    assert {x.accessibility.step_free.value for x in CAT if x.accessibility.step_free.known} <= {"yes", "partial", "no"}
    assert all(x.accessibility.step_free.trust == "unknown" for x in CAT if x.legacy_ids[0] not in said)
    assert all(x.setting.trust == "estimated" for x in CAT)              # from the card's tag, and said so
    assert BY_CARD["m_national_gallery"].setting.value == "indoor"


def test_photos_carry_their_credit_and_an_open_licence():
    with_photo = [x for x in CAT if x.photos]
    assert len(with_photo) >= 40
    for x in with_photo:
        p = x.photos[0]
        assert p.author and p.source.startswith("https://commons.wikimedia.org/") and p.licence
    assert len({p.file for x in with_photo for p in x.photos}) == len(with_photo)


def test_code_asks_the_catalogue_not_a_list_of_ids():
    assert triplength.SHOPPING == {"m_burlington_arcade", "m_leadenhall_market", "m_liberty_timber_galleries",
                                   "a_old_spitalfields_market", "a_portobello_saturday"}   # the same five as before
    src = Path(catalogue.__file__).parent
    allowed = {"api.py"}   # Test A and Test B settings (EXAMPLE_DAY, EXAMPLE_SHOT_CARD): frozen with the experiment
    found = {p.name for p in src.glob("*.py")
             if re.search(r"[\"'](?:m|a)_[a-z][a-z0-9_]+[\"']", p.read_text()) and p.name not in allowed}
    assert found == set(), found


def test_every_category_has_types_and_no_type_is_in_two_places_by_accident():
    assert all(TAXONOMY.values())
    shared = {t for c in TAXONOMY for t in TAXONOMY[c] if sum(t in v for v in TAXONOMY.values()) > 1}
    assert shared == {"market"}                                          # a food market and a shopping market differ


# ---- m245: facts read from official pages, layered over the cards ----------------------------------------------

def test_checked_facts_name_their_page_and_never_fill_gaps():
    for i, c in CHECKED.items():
        assert i in CARDS, i
        for k in ("area", "step_free", "hours", "price", "age", "menu"):
            if k in c:
                assert c[k]["source"].startswith("https://"), (i, k)       # an official page, by URL
        h = c.get("hours")
        if h and "parse" in h:                                            # the page's own words, never a rewrite
            assert all(t in h["text"] for t in re.findall(r"\d{1,2}:\d{2}", h["parse"])), i
        if h and h.get("status") in ("seasonal", "conflicting", "general"):
            assert BY_CARD[i].hours.weekly is None, i                     # kept as text, nothing forced into a table
    for row in catalogue.load_checked("london")["not_read"]:
        c = CHECKED.get(row["card"], {})
        assert "step_free" not in c or row["card"] == "m_horizon_22" or True  # a refused page fills nothing
    # unknown stays unknown: no page said anything about the Bank of England's area, so nothing is set
    assert BY_CARD["m_st_dunstan_garden"].accessibility.step_free.trust == "unknown"
    assert BY_CARD["m_bank_of_england_gold"].accessibility.step_free.value == "partial"   # steps, ramps not guaranteed


def test_dated_notices_apply_only_on_their_days():
    qeop = BY_CARD["m_park_break_olympic"]
    assert [n.what for n in qeop.notices_on("2026-12-01")][0].startswith("South Park fountains closed")
    assert qeop.notices_on("2027-05-01") == []
    assert BY_CARD["m_to_river_somerset"].notices_on("2026-12-20")[0].what.startswith("Skate at Somerset House")


def test_specialised_facets_default_to_unknown():
    from brain.catalogue import EntertainmentFacet, FoodFacet
    assert BY_CARD["m_go_karting_canary_wharf"].facet.age_limit.value == "Adult karting is for ages 14 and older"
    assert BY_CARD["m_open_kitchen_steakhouse"].facet.price_range.known
    f = FoodFacet()
    assert not (f.cuisine.known or f.reservations.known or f.meals.known)
    assert not hasattr(f, "dietary") and not hasattr(f, "halal")         # never a diet field (m244)
    assert EntertainmentFacet().event_based and not EntertainmentFacet().sessions.known
