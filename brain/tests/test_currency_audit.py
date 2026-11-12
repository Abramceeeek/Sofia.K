"""m255 (Abram, m252): a missing or unrecognised currency never turns a paid experience into a free one, and the
provider's own price is never changed. GBP, EUR, USD and the reserved test currency XTS (ISO 4217)."""
from dataclasses import replace
from datetime import date, datetime, timezone

import pytest

from brain import dayplan, fx, quality
from brain.catalogue import Money, load_catalogue, load_dev
from brain.config import DATA_DIR
from brain.discovery import Scorer, cost_gbp
from brain.group import Member, plan
from brain.moments import load_moments
from brain.places import Fact
from brain.population import load_population

TODAY = date(2026, 11, 7)
RATES = fx.Rates({"EUR": 1.0, "GBP": 0.83415, "USD": 1.1165}, date(2026, 11, 6), datetime(2026, 11, 7, tzinfo=timezone.utc))
PARIS = {x.id.split(":")[-1]: x for x in load_dev("paris")[1]}


@pytest.mark.parametrize("amount,cur,status", [(0, "GBP", "free"), (12.5, "GBP", "paid"), (31, "EUR", "paid"),
                                               (40, "USD", "paid"), (10, "XTS", "paid"), (None, "EUR", "unknown"),
                                               (12, "", "currency_unavailable"), (12, "£", "currency_unavailable"),
                                               (12, None, "currency_unavailable")])
def test_each_price_is_named_for_what_it_is(amount, cur, status):
    p = fx.price_status(amount, cur, rates=RATES, today=TODAY)
    assert p["status"] == status and p["amount"] == amount and p["currency"] == cur   # never changed
    if status != "paid" or cur == "GBP":
        assert p["estimate"] is None


def test_a_conversion_is_an_estimate_beside_the_price_never_the_price():
    eur = fx.price_status(31, "EUR", rates=RATES, today=TODAY)
    assert eur["estimate"] == {"amount": 25.86, "currency": "GBP", "kind": "converted_estimate", "as_of": "2026-11-06"}
    assert eur["amount"] == 31 and eur["currency"] == "EUR"
    usd = fx.price_status(40, "USD", rates=RATES, today=TODAY)
    assert usd["estimate"]["amount"] == round(40 / 1.1165 * 0.83415, 2)
    assert fx.price_status(10, "XTS", rates=RATES, today=TODAY)["estimate"] is None   # no rate: no estimate
    stale = fx.price_status(31, "EUR", rates=RATES, today=date(2026, 11, 20))
    assert stale["status"] == "paid" and stale["estimate"] is None                     # an old rate isn't used
    assert fx.price_status(5, "EUR", unavailable=True)["status"] == "unavailable"


def test_the_model_cost_term_never_reads_a_foreign_or_missing_price_as_free():
    cat = PARIS["catacombes"]
    assert cost_gbp(cat) is None and cost_gbp(cat, RATES) == round(31 * 0.83415, 2)
    usd = replace(cat, price=Fact(Money(40.0, "USD", "ticket"), "checked", "x", None))
    assert cost_gbp(usd, RATES) == round(40 / 1.1165 * 0.83415, 2)
    xts = replace(cat, price=Fact(Money(10.0, "XTS", "ticket"), "checked", "x", None))
    assert cost_gbp(xts, RATES) is None                                               # unconvertible: unknown
    assert cost_gbp(replace(cat, price=Fact.unknown()), RATES) is None


def test_money_says_unknown_never_free():
    m = quality.money(replace(PARIS["catacombes"], price=Fact.unknown()), 20.0, "EUR")
    assert m.level == "fair" and "isn't known" in m.reason and "Free" not in m.reason


def test_the_day_plan_never_shows_an_unknown_price_as_free():
    assert dayplan._cost_line({"cost_gbp": None}) == "Price not known"
    assert dayplan._cost_line({"cost_gbp": 0}) == "Cost: free"
    assert dayplan._cost(None) == "price not known" and dayplan._cost(0) == "free"


def test_every_ready_london_card_is_priced_so_day_totals_are_complete():
    assert all(m.cost_gbp is not None for m in load_moments(DATA_DIR / "moments") if m.status == "ready")


def test_group_budgets_use_their_own_currency_and_never_count_a_missing_price_as_free():
    pop = load_population(DATA_DIR / "priors.yaml")
    xs = [x for x in load_dev("paris")[1] if x.status == "ready"]                    # prices in EUR, five unknown
    ms = [Member("Member A", Scorer(pop, None), budget_per_day=40.0), Member("Member B", Scorer(pop, None))]
    gbp = plan(ms, xs, 1, 3, currency="GBP")                                          # no rate: nothing confirmable
    assert gbp.stops == [] or all(x.price.known and x.price.value.currency == "GBP" for x in gbp.stops)
    assert any("price isn't known in GBP" in n for n in gbp.notes)
    eur = plan(ms, xs, 1, 3, currency="EUR")
    assert eur.stops and all(x.price.known for x in eur.stops)                       # unknown prices left out
    assert any("price isn't known in EUR" in n for n in eur.notes)
    fx_gbp = plan(ms, xs, 1, 3, currency="GBP", rates=RATES)
    assert fx_gbp.stops and sum(x.price.value.amount * 0.83415 for x in fx_gbp.stops) <= 40.0 + 1e-6
