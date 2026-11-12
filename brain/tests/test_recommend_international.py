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


# ---- m254: calibrated uncertainty (Abram, m252) -----------------------------------------------------------------

def _a(x, p, day=None, **kw):
    return quality.assess(x, p_good=p, today=date(2026, 11, 12), day=day, **kw)


def test_each_gap_costs_what_it_risks_for_this_use():
    from brain.catalogue import OpeningHours
    rodin = PARIS["rodin"]
    day = date(2026, 11, 24)
    no_hours = replace(rodin, hours=OpeningHours(None, None, "unknown", None, None))
    text_hours = replace(rodin, hours=OpeningHours("Varies by season", None, "checked", "x", "2026-11-11"))
    r = lambda x, **kw: {k.field: k.p for k in _a(x, 0.8, day, **kw).risks}
    assert r(no_hours)["hours"] == quality.RISK["hours_unknown_on_day"] > r(text_hours)["hours"] == quality.RISK["hours_text_on_day"]
    assert "access" not in r(rodin)                                    # no stated need: unknown access costs nothing
    assert r(rodin, needs_step_free=True)["access"] == quality.RISK["access_unknown_need"]
    assert "area" not in r(rodin)                                      # its arrondissement is known
    bank = LONDON["m_bank_of_england_gold"]                            # no area or district named by a source
    assert 0 < r(bank)["area"] < 0.05                                  # a small confidence cost
    assert all(k.dimension in ("practicality", "money", "trust") for k in _a(no_hours, 0.8, day).risks)


def test_unknown_access_is_never_step_free_and_strict_needs_are_verified():
    rodin = PARIS["rodin"]                                             # access unknown
    day = date(2026, 11, 24)
    a = _a(rodin, 0.9, day, needs_step_free=True)
    assert a.practicality.level == "fair" and "isn't known" in a.practicality.reason
    strict = _a(rodin, 0.9, day, needs_step_free=True, strict_access=True)
    assert strict.practicality.level == "poor" and "isn't verified" in strict.practicality.reason


def test_a_strong_match_with_seasonal_hours_beats_a_complete_poor_match_only_when_calibrated():
    day = date(2026, 11, 24)
    park = _a(PARIS["buttes-chaumont"], 0.85, day)                     # hours as seasonal text
    arcade = _a(PARIS["galerie-vivienne"], 0.55, day)                  # complete data, a weaker match
    items = [("park", park), ("arcade", arcade)]
    assert [k for k, _ in quality.rank(items)] == ["arcade", "park"]    # today's rule (unchanged): any doubt first
    assert [k for k, _ in quality.rank(items, calibrated=True)] == ["park", "arcade"]


def test_the_default_ranking_is_unchanged():
    import inspect
    sig = inspect.signature(quality.rank)
    assert sig.parameters["doubt_cost"].default is None and sig.parameters["calibrated"].default is False
