"""m236 (WS2, Global Destination Intelligence): a destination's profile from any mix of providers, tested on London's
checked catalogue and on Testville, a synthetic destination (tests/fixtures/destination_testville.yaml: country ZZ,
currency XTS, both reserved codes). Nothing here calls a network."""
from datetime import date
from pathlib import Path

import yaml

from brain import offline
from brain.destination import (CatalogueProvider, EmergencyProvider, FileProvider, assemble, destinations_with,
                               load_emergency)
from brain.moments import Point

FIX = Path(__file__).parent / "fixtures" / "destination_testville.yaml"
DESTS = destinations_with({"testville": yaml.safe_load(FIX.read_text())["definition"]})
LONDON = assemble(DESTS["london"], [CatalogueProvider(), EmergencyProvider()], date(2026, 12, 20), date(2026, 12, 31))
TEST = assemble(DESTS["testville"], [FileProvider(FIX), CatalogueProvider(), EmergencyProvider()],
                date(2027, 4, 1), date(2027, 4, 30))


def test_london_is_understood_from_its_checked_catalogue():
    assert LONDON.sources == {"areas": "ODYS catalogue", "travel": "ODYS catalogue", "experiences": "ODYS catalogue",
                              "holidays": "ODYS catalogue", "stays": "ODYS catalogue",
                              "emergency": "ODYS emergency numbers (official pages, read 10 Nov 2026)"}
    assert len(LONDON.experiences) == 49 and len(LONDON.areas) >= 15          # the areas the cards themselves name
    names = {a.name for a in LONDON.areas}
    assert {"Greenwich", "Canary Wharf", "Hyde Park", "City of London"} <= names
    assert all(51.28 < a.centre.lat < 51.70 for a in LONDON.areas)
    days = {h.day for h in LONDON.parts["holidays"]}
    assert date(2026, 12, 25) in days and all(h.source == "GOV.UK bank holidays" for h in LONDON.parts["holidays"])
    m = LONDON.area_matrix()
    assert m[("greenwich", "greenwich_peninsula")][0] < m[("greenwich", "richmond_park")][0]   # near before far
    assert all(minutes >= 0 for minutes, _ in m.values()) and m[("soho", "chinatown")][0] == 0   # the cards share a point
    r = LONDON.readiness()
    assert r["missing"] == ["seasons"] and not r["experiences"] == 0          # no checked seasonal notes yet: said
    assert any("sample" in w for w in r["weak"]) and any("estimated" in w for w in r["weak"])
    assert r["ready"]                                                         # what Abram's E rule asks is there


def test_a_destination_from_another_provider_fills_the_same_profile():
    assert TEST.sources["areas"] == TEST.sources["experiences"] == "synthetic test file"
    assert "emergency" not in TEST.sources                                    # ZZ has no checked numbers: missing
    by_area = TEST.experiences_by_area()
    assert by_area["riverside"]["food_drink"] == 1 and by_area["hill_district"]["culture"] == 1
    beach = next(x for x in TEST.experiences if x.type == "beach")
    assert beach.facet.kind == "beach" and beach.facet.lifeguards.trust == "unknown"   # never assumed
    assert beach.price.value.currency == "XTS" and beach.geo.timezone == "Etc/GMT-9"
    assert [s.note for s in TEST.seasons_in(4)] == ["Blossom along the river path (synthetic)"]
    assert [h.name for h in TEST.parts["holidays"]] == ["Synthetic Spring Day"]  # only those in the dates asked
    assert TEST.stays_by_area() == {"old_town": 2, "station_quarter": 3, "riverside": 1}
    museum = next(x for x in TEST.experiences if x.type == "museum")
    assert museum.hours.open_on("mon") is False and museum.hours.open_on("tue") is True
    r = TEST.readiness()
    assert "emergency" in r["missing"] and not r["ready"]                     # never offered without them
    assert all(not x.problems() for x in TEST.experiences)


def test_the_first_provider_that_has_a_part_wins_and_is_named():
    both = assemble(DESTS["london"], [FileProvider(FIX), CatalogueProvider()])
    assert both.sources["areas"] == "ODYS catalogue"                          # the file is for Testville only
    nearest = LONDON.nearest_area(Point(lat=51.4769, lon=-0.0005))           # Greenwich Park's own coordinates
    assert nearest.name == "Greenwich"


def test_each_country_has_its_own_emergency_numbers_with_sources():
    e = load_emergency()
    assert set(e) == {"GB", "FR", "NL", "BE"}
    nums = {cc: {x.number for x in v.lines} for cc, v in e.items()}
    assert nums["GB"] == {"999", "111", "116 123"} and {"112", "15", "17", "18"} <= nums["FR"]
    assert {"112", "0900-8844"} == nums["NL"] and {"112", "101"} == nums["BE"]
    for v in e.values():
        assert v.checked == "2026-11-10" and all(x.source.startswith("https://") for x in v.lines)


def test_the_offline_pack_shows_the_trips_own_country_never_another():
    uk = offline.emergency_items("GB", "London")
    assert uk[0]["lines"] == ["If you or someone else is in danger or hurt, call 999."]   # Help & safety's words
    assert "nhs.uk" in uk[0]["source"] and uk[0]["saved"] == "2026-11-10"
    fr = offline.emergency_items("FR", "Paris")
    assert fr[0]["lines"] == ["112: the European emergency number, free."] and not any("999" in i["lines"][0] for i in fr)
    unknown = offline.emergency_items("ZZ", "Testville")
    assert unknown[0]["status"] == "check" and "hasn't checked" in unknown[0]["lines"][0]
    assert unknown[0]["action"] == "Find the local emergency number before you go."
