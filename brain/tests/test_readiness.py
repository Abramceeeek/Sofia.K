"""m248 (WS5): the destination-readiness checklist, applied to London, Paris and the synthetic Testville."""
import yaml

from brain.catalogue import load_catalogue, load_dev
from brain.config import DATA_DIR
from brain.destination import load_emergency
from brain.readiness import Inputs, assessment, checklist, claims, level
from brain.traveltiming import load_bank_holidays

EM = load_emergency()
TODAY = "2026-11-11"


def london_inputs() -> Inputs:
    meta, hs = load_bank_holidays()
    loc = yaml.safe_load((DATA_DIR / "catalogue" / "london_locations.yaml").read_text(encoding="utf-8"))["cards"]
    return Inputs("GB", "Europe/London", "GBP", len(EM["GB"].lines), EM["GB"].checked, meta["source"],
                  tuple(sorted({h.day.year for h in hs})), "partial", "checked", "en-GB", True,
                  located=sum(1 for v in loc.values() if v["wikidata"]))


def paris_inputs(raw: dict) -> Inputs:
    h = raw["holidays"]
    return Inputs("FR", "Europe/Paris", "EUR", len(EM["FR"].lines), EM["FR"].checked, h["source_2026"],
                  tuple(sorted({int(d[:4]) for d in h["days"]})), "checked", "estimated", "fr-FR", True)


def test_london_is_a_preview_until_its_quality_items_pass():
    items = checklist(london_inputs(), [x for x in load_catalogue() if x.status == "ready"], TODAY, 2027)
    assert all(i.status == "pass" for i in items if i.essential), [(i.key, i.status) for i in items]
    assert level(items) == "preview" and level(items, reviewed_by_abram=True) == "preview"   # quality items fail
    weak = {i.key for i in items if i.status != "pass"}
    assert {"access", "hours", "school"} <= weak                         # said, not hidden


def test_paris_stays_in_development():
    dest, xs, raw = load_dev("paris")
    items = checklist(paris_inputs(raw), [x for x in xs if x.status == "ready"], TODAY, 2027)
    by = {i.key: i for i in items}
    assert by["emergency"].status == by["holidays"].status == by["currency"].status == "pass"
    assert by["transport"].status == "partial"                          # estimates only: RATP and IDFM refused
    assert level(items) == "development"                                # never "supported" because cards exist


def test_a_destination_with_cards_but_no_emergency_numbers_is_never_ready():
    dest, xs, raw = load_dev("paris")
    inp = paris_inputs(raw)
    items = checklist(Inputs(**{**inp.__dict__, "emergency_lines": 0, "transport": "checked"}),
                      [x for x in xs if x.status == "ready"] * 2, TODAY, 2027)
    assert level(items, reviewed_by_abram=True) == "development"


def test_formats_come_from_cldr():
    f = yaml.safe_load((DATA_DIR / "formats.yaml").read_text(encoding="utf-8"))
    assert f["locales"]["fr-FR"]["number"] == "1 234,5" or f["locales"]["fr-FR"]["number"].replace(" ", " ") == "1 234,5"


def test_claims_follow_each_feature_not_the_level():                     # m259 (Abram, m252)
    items = checklist(london_inputs(), [x for x in load_catalogue() if x.status == "ready"], TODAY, 2027)
    c = claims(items)
    assert "never as step-free" in c["accessibility"] and "every place" not in c["accessibility"]
    assert c["transport"].startswith("journey times from an official")      # TfL
    dest, xs, raw = load_dev("paris")
    p = claims(checklist(paris_inputs(raw), [x for x in xs if x.status == "ready"], TODAY, 2027))
    assert "not official transport information" in p["transport"]          # RATP and IDFM unread
    assert level(items) == "preview"                                        # London stays a preview (Abram, m252)


def test_every_assessment_has_a_review_date_and_supported_needs_abrams_final_review():   # m263 (Abram, m260)
    items = checklist(london_inputs(), [x for x in load_catalogue() if x.status == "ready"], TODAY, 2027)
    a = assessment(items, last_reviewed="2026-11-12", reviewed_by="Claude (data check)")
    assert a["last_reviewed"] == "2026-11-12" and a["level"] == "preview" and a["abram_final_review"] is None
    assert any(g.startswith("Step-free access") for g in a["gaps"])        # gaps listed, never hidden by a percentage
    by = {i["key"]: i for i in a["items"]}
    assert by["prices"]["status"] == "pass"                                # every shown price has a source
    passing = [type(i)(**{**i.__dict__, "status": "pass"}) for i in items]
    assert level(passing) == "preview"                                     # all numbers pass: still not supported
    assert assessment(passing, "2026-11-12", "x", abram_final_review="2026-12-01")["level"] == "supported"
