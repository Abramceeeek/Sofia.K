"""m318 (Abram, 20 Nov): Seville as a DEVELOPMENT destination, and food discovery that stays out of dietary data.
Every check here is on data/dev/seville.yaml as read from official pages on 20 Nov 2026."""
import importlib.util
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from brain import offline, quality
from brain.catalogue import Accessibility, FoodFacet, load_dev, parse_hours
from brain.config import DATA_DIR
from brain.destination import load_emergency
from brain.discovery import Scorer, cost_gbp
from brain.fx import Rates
from brain.places import Fact
from brain.population import load_population
from brain.priceestimate import allowance
from brain.readiness import Inputs, checklist, claims, level
from brain.sun import sunset

DEST, XS, RAW = load_dev("seville")
BY = {x.id.split(":")[-1]: x for x in XS}
READY = [x for x in XS if x.status == "ready"]
TODAY = date(2026, 11, 20)
SUNDAY, MONDAY, TUESDAY = date(2026, 11, 22), date(2026, 11, 23), date(2026, 11, 24)
RATES = Rates({"EUR": 1.0, "GBP": 0.83415}, date(2026, 11, 6), datetime(2026, 11, 7, tzinfo=timezone.utc))
MARKETS = ("mercado-triana", "mercado-feria", "mercado-encarnacion", "mercado-arenal")


# ---- the destination ------------------------------------------------------------------------------------------------

def test_seville_is_development_only_and_never_offered():
    for f in ("destinations.yaml", "airports.yaml"):
        assert "seville" not in (DATA_DIR / f).read_text(encoding="utf-8").lower()   # no route, trip or plan offers it
    assert DEST.country == "ES" and DEST.currency == "EUR" and DEST.timezone == "Europe/Madrid"
    assert all(x.id.startswith("xp:es:seville:") for x in XS)


def test_every_ready_place_has_a_checked_location_hours_and_a_source():
    assert len(READY) == 20
    for x in READY:
        assert 37.30 < x.geo.lat < 37.45 and -6.05 < x.geo.lon < -5.90, x.id                  # inside the city
        assert x.place_id and (x.place_id.startswith("osm:") or x.place_id.startswith("wikidata:")), x.id
        assert x.hours.text and x.hours.source and x.hours.source.startswith("http"), x.id
        assert x.geo.timezone == "Europe/Madrid", x.id                                        # never London's
        assert not x.problems(), (x.id, x.problems())


def test_drafts_are_never_ready_and_say_why():
    drafts = {k for k, x in BY.items() if x.status == "draft"}
    assert drafts == {"el-rinconcillo", "eslava", "antonio-romero"}       # their own sites print no hours
    assert all(BY[k].hours.text is None for k in drafts)


def test_the_emergency_number_is_spains_own_with_its_source():
    es = load_emergency()["ES"]
    assert es.checked == "2026-11-20" and {l.number for l in es.lines} == {"112"}
    assert all(l.source.startswith("https://") for l in es.lines)
    assert not any(l.number in ("999", "111") for l in es.lines)          # never the UK's numbers
    pack = offline.emergency_items("ES", "Seville")                      # the offline pack a Spanish trip would carry
    assert pack[0]["lines"][0].startswith("112") and not any("999" in i["lines"][0] for i in pack)


def test_local_dates_and_clock_changes_follow_madrid():
    tz = ZoneInfo(DEST.timezone)
    late = datetime(2026, 11, 22, 23, 30, tzinfo=timezone.utc)
    assert late.astimezone(tz).date() == MONDAY                          # already Monday in Seville
    assert late.astimezone(ZoneInfo("Europe/London")).date() == SUNDAY  # still Sunday in London
    assert datetime(2026, 11, 22, 12, tzinfo=tz).utcoffset().total_seconds() == 3600            # CET
    assert datetime(2027, 3, 28, 0, 30, tzinfo=timezone.utc).astimezone(tz).utcoffset().total_seconds() == 3600
    assert datetime(2027, 3, 28, 1, 30, tzinfo=timezone.utc).astimezone(tz).utcoffset().total_seconds() == 7200


def test_sunset_is_seville_s_not_london_s():
    c = RAW["destination"]["centre"]
    assert sunset(SUNDAY, c["lat"], c["lon"], DEST.timezone) == "18:10"
    assert sunset(SUNDAY) == "16:04"                                     # the London default, for contrast


def test_holidays_come_from_the_boe_for_both_years():
    h = RAW["holidays"]
    assert h["source_2026"].startswith("https://www.boe.es/") and h["source_2027"].startswith("https://www.boe.es/")
    assert "2026-02-28" in h["days"] and "2027-03-01" in h["days"]     # Día de Andalucía
    assert "local holidays are not included" in h["note"]


def test_missing_transport_and_weather_are_said_not_filled():
    assert RAW["transport"]["status"] == "missing"
    assert RAW["weather"]["status"] == "not integrated"
    assert all("journey" not in str(x.transport) or x.transport.nearest is None for x in READY)


def test_seville_stays_in_development():
    em = load_emergency()["ES"]
    h = RAW["holidays"]
    inp = Inputs("ES", "Europe/Madrid", "EUR", len(em.lines), em.checked, h["source_2026"],
                 tuple(sorted({int(d[:4]) for d in h["days"]})), "missing", "missing", None, False)   # no photos yet
    items = checklist(inp, READY, TODAY.isoformat(), 2027)
    by = {i.key: i for i in items}
    assert by["emergency"].status == by["currency"].status == by["timezone"].status == "pass"
    assert by["experiences"].status == "pass"                            # 20 ready, 20 independently located
    assert by["variety"].status != "pass" and by["transport"].status != "pass"
    assert level(items) == level(items, reviewed_by_abram=True) == "development"
    assert "not official transport information" in claims(items)["transport"] or "no" in claims(items)["transport"].lower()


# ---- prices -----------------------------------------------------------------------------------------------------------

def test_euros_stay_euros_and_convert_only_with_a_rate():
    pil = BY["pilatos"]
    assert pil.price.value.currency == "EUR" and pil.price.value.amount == 12
    assert cost_gbp(pil) is None                                         # no rate: unknown, never treated as pounds
    assert cost_gbp(pil, RATES) == round(12 * 0.83415, 2)
    assert BY["plaza-espana"].price.value.amount == 0 and BY["plaza-espana"].price.value.kind == "free"


def test_unknown_food_prices_stay_unknown():
    for k in MARKETS + ("arte-y-sabor", "casa-robles"):
        assert not BY[k].price.known, k                                  # no price was printed
        assert allowance(BY[k], READY, today=TODAY) is None, k           # too few comparable dated food prices


# ---- food ------------------------------------------------------------------------------------------------------------

def test_a_market_is_not_a_restaurant():
    for k in MARKETS:
        assert BY[k].type == "market" and BY[k].facet.service == "market"
    for k in ("arte-y-sabor", "casa-robles"):
        assert BY[k].type == "restaurant" and BY[k].facet.service == "sit_down"
    assert any("Stall hours vary" in n.what for n in BY["mercado-triana"].notices)   # the market's hours aren't a stall's


def test_the_markets_are_closed_on_sunday_and_the_arenal_has_two_sessions():
    for k in MARKETS:
        assert quality.availability(BY[k], SUNDAY, TODAY) == "closed or unavailable", k
        assert quality.availability(BY[k], TUESDAY, TODAY) == "confirmed open", k
    assert BY["mercado-arenal"].hours.weekly["mon"] == [(540, 900), (1050, 1230)]


def test_no_dietary_claim_is_data():
    assert not any(f in FoodFacet.__dataclass_fields__ for f in ("dietary", "diet", "halal", "vegetarian", "allergens"))
    raw = yaml.safe_load((DATA_DIR / "dev" / "seville.yaml").read_text(encoding="utf-8"))
    flat = str(raw["experiences"]).lower()
    for word in ("vegetar", "vegan", "halal", "gluten", "allerg"):
        assert word not in flat, word                                    # a venue's words live in comments only


# ---- freshness and unknowns -------------------------------------------------------------------------------------------

def test_leaflet_hours_are_never_confirmed_open():
    for k in ("archivo-indias", "artes-costumbres", "plaza-espana"):
        assert BY[k].hours.checked == "2025-06-27"
        assert quality.availability(BY[k], TUESDAY, TODAY) == "might be open", k


def test_a_dated_closure_and_an_expired_check():
    assert quality.availability(BY["catedral"], date(2026, 12, 8), TODAY) == "closed or unavailable"
    stale = replace(BY["pilatos"], hours=replace(BY["pilatos"].hours, checked="2026-01-02"))
    assert quality.availability(stale, TUESDAY, TODAY) == "might be open"   # official, but read too long ago


def test_unknown_access_is_never_no():
    assert not BY["alcazar"].accessibility.step_free.known
    p = quality.practicality(BY["alcazar"], TUESDAY, None, None, needs_step_free=True)
    assert p.level == "fair" and "isn't known" in p.reason
    assert BY["baile-flamenco"].accessibility.step_free.value == "yes"
    hidden = replace(BY["baile-flamenco"], accessibility=Accessibility(Fact.unknown()))
    assert quality.practicality(hidden, TUESDAY, None, None, needs_step_free=True).level == "fair"


# ---- the hours parser (m318: split hours were losing their first session) ------------------------------------------

def test_split_hours_keep_both_sessions_and_midnight_is_the_day_s_end():
    t = parse_hours("Mon-Fri 09:00-15:00, 17:30-20:30; Sat 09:00-15:00")
    assert t["mon"] == [(540, 900), (1050, 1230)] and t["sat"] == [(540, 900)] and t["sun"] == []
    assert parse_hours("Daily 09:30-00:00")["tue"] == [(570, 1440)]
    assert parse_hours("Daily 20:00-02:00") is None                     # past midnight: the text is kept, not guessed
    assert parse_hours("Daily 10:00-18:00, Fridays to 21:00")["fri"] == [(600, 1260)]   # unchanged


# ---- recommendations transfer (default ranking, synthetic people only) ---------------------------------------------

def _bp():
    path = Path(__file__).resolve().parents[1] / "scripts" / "benchmark_profiles.py"
    spec = importlib.util.spec_from_file_location("benchmark_profiles", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_a_museum_lover_s_taste_transfers_to_seville():
    bp, pop = _bp(), load_population(DATA_DIR / "priors.yaml")
    d = bp.PROFILES["museum enthusiast"][0]
    s = Scorer(pop, bp.delta_for(pop, d), rates=RATES)
    top = bp.top(s, READY, None, False, TUESDAY, "EUR")
    assert all(x.category == "culture" for x, _ in top)
    assert all(a.practicality.level == "good" for _, a in top)          # nothing shut that day is offered


def test_a_food_lover_s_best_matches_are_food_even_if_today_s_rule_hides_them():
    """Found on 20 Nov: food places are the food lover's strongest matches, but the default rule ("doubts first")
    ranks every food place below fixed-price museums, because a meal's price is always an estimate or unknown. The
    default rule is unchanged during Test B; the fix is proposed in decisions/food-and-seville-pilot-2026-11-20.md."""
    bp, pop = _bp(), load_population(DATA_DIR / "priors.yaml")
    d = bp.PROFILES["food-experience enthusiast"][0]
    s = Scorer(pop, bp.delta_for(pop, d), rates=RATES)
    best = sorted(READY, key=lambda x: -s.p_good(x))[:5]
    assert all(x.category == "food_drink" for x in best)                # the model knows what they like
    bp.RULE = 0.10
    try:
        assert any(x.category == "food_drink" for x, _ in bp.top(s, READY, None, False, TUESDAY, "EUR"))
    finally:
        bp.RULE = None
