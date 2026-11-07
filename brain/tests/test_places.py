"""WS1 (m207): one place record for every source, with every fact's source, or "unknown"; London unchanged."""
import json
from pathlib import Path

from brain import traveltiming
from brain.config import DATA_DIR
from brain.moments import load_moments
from brain.places import Fact, from_card, from_osm_element, load_destinations

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "overpass_sample.json").read_text())


def test_london_is_a_destination_like_any_other():
    d = load_destinations(DATA_DIR / "destinations.yaml")
    ldn = d["london"]
    assert (ldn.country, ldn.timezone, ldn.currency, ldn.bank_holidays) == ("GB", "Europe/London", "GBP",
                                                                            "england-and-wales")
    assert ldn.coverage == "checked" and ldn.zone.key == "Europe/London"
    assert traveltiming.DESTINATION_DIVISION == {"london": "england-and-wales"}   # read from the registry now


def test_every_card_becomes_a_record_with_its_own_id_and_says_what_it_doesnt_know():
    cards = load_moments(DATA_DIR / "moments")
    recs = [from_card(m) for m in cards]
    assert [r.id for r in recs] == [f"odys:{m.id}" for m in cards]           # the card ids, unchanged, namespaced
    assert len({r.id for r in recs}) == len(recs)
    for m, r in zip(cards, recs):
        assert r.category.trust == "unknown"                                 # cards have no category yet: said
        if m.approach.step_free is None:
            assert r.step_free.trust == "unknown" and "step_free" in r.unknowns()
        if m.cost_gbp is not None:
            assert r.price.value.currency == "GBP" and r.price.trust == "checked"
        assert r.diet == {} and "diet" in r.unknowns()                     # no card says anything about food needs


def test_an_osm_element_is_claims_with_its_source_never_checked():
    cafe, museum, nameless = (from_osm_element(e, "london", "2026-11-07") for e in FIXTURE["elements"])
    assert cafe.id == "osm:node/1001" and cafe.attribution == "© OpenStreetMap contributors"
    assert cafe.diet["halal"] == Fact("yes", "claimed", "osm:node/1001 (diet:halal)", "2026-11-07")
    assert all(f.trust == "claimed" for f in cafe.diet.values())           # a map tag is never "checked"
    assert cafe.step_free.value == "limited" and cafe.same_as == ("wikidata:Q0000001",)
    assert museum.id == "osm:way/2002" and museum.point is not None and museum.price.value.kind == "free"
    assert museum.opening_hours.trust == "unknown" and museum.diet == {}
    # a restaurant with a cuisine but no diet tag: halal stays unknown, never inferred from "turkish"
    assert "halal" not in nameless.diet and "diet" in nameless.unknowns() and nameless.name == ""


def test_ids_from_different_sources_never_collide():
    card = from_card(load_moments(DATA_DIR / "moments")[0])
    osm = from_osm_element(FIXTURE["elements"][0], "london", "2026-11-07")
    assert card.id.split(":")[0] != osm.id.split(":")[0]
