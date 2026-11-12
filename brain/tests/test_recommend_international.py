"""m249: the Brain recommends outside the UK without London assumptions, and treats unknowns as unknown."""
from dataclasses import replace
from datetime import date, datetime, timezone

from brain import quality
from brain.catalogue import Accessibility, load_catalogue, load_dev
from brain.discovery import Scorer, cost_gbp
from brain.fx import Rates
from brain.places import Fact
from brain.population import load_population
from brain.config import DATA_DIR

POP = load_population(DATA_DIR / "priors.yaml")
RATES = Rates({"EUR": 1.0, "GBP": 0.83415}, date(2026, 11, 6), datetime(2026, 11, 7, tzinfo=timezone.utc))
PARIS = {x.id.split(":")[-1]: x for x in load_dev("paris")[1]}
LONDON = {x.legacy_ids[0]: x for x in load_catalogue()}


def test_a_euro_price_is_converted_or_unknown_never_free():
    cat = PARIS["catacombes"]                                         # 31 €
    assert cost_gbp(cat) is None                                      # no rate: unknown (before m249 it scored as free)
    assert cost_gbp(cat, RATES) == round(31 / 1.0 * 0.83415, 2)
    s, s_fx = Scorer(POP, None), Scorer(POP, None, rates=RATES)
    assert s_fx.utility(cat) < s.utility(cat)                         # a real price costs something


def test_a_stated_step_free_need_is_a_rule_and_unknown_is_not_no():
    day = date(2026, 11, 24)
    p = quality.practicality(PARIS["catacombes"], day, None, None, needs_step_free=True)
    assert p.level == "poor" and "131" in p.reason                    # the source said no
    p = quality.practicality(PARIS["rodin"], day, None, None, needs_step_free=True)
    assert p.level == "fair" and "isn't known" in p.reason            # unknown: said, never excluded
    hidden = replace(PARIS["catacombes"], accessibility=Accessibility(Fact.unknown()))
    assert quality.practicality(hidden, day, None, None, needs_step_free=True).level == "fair"


def test_dated_closures_and_sessions_shape_practicality():
    bank = LONDON["m_bank_of_england_gold"]
    assert quality.practicality(bank, date(2026, 11, 28), None, None).level == "poor"      # a Saturday: closed
    rex = PARIS["grand-rex"]
    assert "per event" in quality.practicality(rex, date(2026, 11, 24), None, None).reason
    court = LONDON["m_courtauld_gallery"]
    assert quality.practicality(court, date(2026, 12, 25), None, None).level == "poor"     # a dated closure


def test_the_weighted_rule_lets_a_strong_match_with_one_doubt_win():
    a = quality.Assessment(quality.Perspective("good", ""), quality.Perspective("fair", ""), quality.Perspective("good", ""),
                           quality.Perspective("good", ""), 0.9)
    b = quality.Assessment(quality.Perspective("good", ""), quality.Perspective("good", ""), quality.Perspective("good", ""),
                           quality.Perspective("good", ""), 0.6)
    assert [x for x, _ in quality.rank([("a", a), ("b", b)])] == ["b", "a"]                 # today: doubts first
    assert [x for x, _ in quality.rank([("a", a), ("b", b)], doubt_cost=0.10)] == ["a", "b"]
    poor = replace(a, practicality=quality.Perspective("poor", ""))
    assert [x for x, _ in quality.rank([("p", poor), ("b", b)], doubt_cost=0.10)] == ["b", "p"]   # poor still last
