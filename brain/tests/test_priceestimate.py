"""m262 (Abram, m260): an unknown price gets a labelled planning allowance only with enough comparable prices; budgets
keep confirmed, estimated and unknown spending apart and never claim a fit they can't verify."""
from dataclasses import replace
from datetime import date

from brain.catalogue import Money, load_dev
from brain.places import Fact
from brain.priceestimate import MIN_SAMPLE, allowance, budget_breakdown, with_allowances

READY = [x for x in load_dev("paris")[1] if x.status == "ready"]
BY = {x.id.split(":")[-1]: x for x in READY}
TODAY = date(2026, 11, 19)                                          # fixed, so no test changes with the calendar


def test_an_allowance_needs_enough_comparable_prices_and_says_what_it_is():
    a = allowance(BY["chasse-nature"], READY, today=TODAY)                       # a museum with no price read
    assert a is not None and a.n >= MIN_SAMPLE and a.currency == "EUR"
    assert a.basis == "category: culture"                           # only 2 priced museums: the category instead
    assert a.conservative >= a.amount and "not this place's price" in a.label()
    assert a.observed[0] <= a.observed[1] and len(a.peers) == a.n and BY["chasse-nature"].id not in a.peers


def test_too_few_comparable_prices_leaves_it_unknown():
    assert allowance(BY["enfants-rouges"], READY, today=TODAY) is None           # one priced food place: not enough
    assert allowance(BY["philharmonie"], READY, today=TODAY) is None             # one priced entertainment place
    assert allowance(BY["rodin"], READY, today=TODAY) is None                    # it has its own price


def test_allowances_are_marked_as_estimates_never_prices():
    xs, made = with_allowances(READY, today=TODAY)
    ch = next(x for x in xs if x.id.endswith("chasse-nature"))
    assert ch.price.trust == "estimated" and ch.price.source.startswith("median") and ch.id in made
    assert not next(x for x in xs if x.id.endswith("enfants-rouges")).price.known   # still unknown


def test_budgets_never_claim_a_fit_they_cannot_verify():
    xs, made = with_allowances(READY, today=TODAY)
    pick = lambda *ids: [x for x in xs if x.id.split(":")[-1] in ids]
    assert budget_breakdown(pick("rodin", "pantheon"), made, 40, today=TODAY)["status"] == "fits"   # verified only
    est = budget_breakdown(pick("rodin", "chasse-nature"), made, 60, today=TODAY)
    assert est["status"] == "likely fits" and "isn't guaranteed" in est["say"]                   # strict: not a promise
    assert est["estimated_conservative"] >= est["estimated"]
    unk = budget_breakdown(pick("rodin", "enfants-rouges"), made, 100, today=TODAY)
    assert unk["status"] == "can't be verified yet" and unk["unknown"]                           # never free
    assert budget_breakdown(pick("catacombes", "sainte-chapelle"), made, 40, today=TODAY)["status"] == "over budget"
    assert "estimate" in made[BY["chasse-nature"].id].label().lower()                            # labelled as one


def test_an_old_or_undated_verified_price_is_never_confirmed_spending():   # Abram, 20 Nov §6
    two = [x for x in READY if x.id.split(":")[-1] in ("rodin", "pantheon")]
    assert budget_breakdown(two, {}, 40, today=TODAY)["status"] == "fits"
    late = budget_breakdown(two, {}, 40, today=date(2028, 1, 1))              # over a year after they were checked
    assert late["status"] == "likely fits" and late["confirmed"] == 0 and late["estimated"] > 0
    undated = [replace(x, price=replace(x.price, checked=None)) for x in two]
    assert budget_breakdown(undated, {}, 40, today=TODAY)["status"] == "likely fits"
    assert late["currency"] == "EUR"                                          # the supplier's own currency, kept


def test_prices_in_two_currencies_are_never_added_up():                     # Abram, 20 Nov §6
    rodin = BY["rodin"]
    pounds = replace(BY["pantheon"], price=replace(BY["pantheon"].price,
                                                     value=replace(BY["pantheon"].price.value, amount=10.0, currency="GBP")))
    r = budget_breakdown([rodin, pounds], {}, 100, today=TODAY)
    assert r["status"] == "mixed currencies" and r["currencies"] == ["EUR", "GBP"] and r["currency"] is None
    assert rodin.price.value.currency == "EUR" and pounds.price.value.amount == 10.0   # neither price was changed


def test_comparable_prices_must_be_recent_enough_for_their_kind():         # m292 (Abram, 19 Nov)
    from brain import priceestimate as pe
    assert allowance(BY["chasse-nature"], READY, today=date(2027, 11, 12)) is None   # its peers' prices, a year old
    assert allowance(BY["chasse-nature"], READY, today=date(2027, 11, 1)) is not None
    undated = [replace(x, price=replace(x.price, checked=None)) if x.price.known else x for x in READY]
    assert allowance(BY["chasse-nature"], undated, today=TODAY) is None      # no date: its age can't be judged
    assert pe.MAX_AGE_DAYS["entertainment"] < pe.DEFAULT_MAX_AGE_DAYS        # event tickets go stale fastest


def test_a_missing_price_is_never_free_in_the_model_and_london_is_unchanged():   # m293 (Abram, 19 Nov)
    from datetime import datetime, timezone
    from brain.catalogue import load_catalogue
    from brain.config import DATA_DIR
    from brain.discovery import Scorer
    from brain.fx import Rates
    from brain.population import load_population
    from brain.priceestimate import model_costs
    rates = Rates({"EUR": 1.0, "GBP": 0.83415}, date(2026, 11, 6), datetime(2026, 11, 7, tzinfo=timezone.utc), "test")
    costs = model_costs(READY, today=TODAY, rates=rates)
    unknown = {x.id for x in READY if not x.price.known}
    assert set(costs) == unknown and all(v > 0 for v in costs.values())     # every missing price, none free
    assert costs[BY["chasse-nature"].id] > 0 and costs[BY["philharmonie"].id] > 0   # allowance; neutral paid figure
    median = model_costs(READY, today=TODAY, rates=rates, figure="median")
    assert all(costs[k] >= median[k] for k in costs)                         # the default is the conservative one
    pop = load_population(DATA_DIR / "priors.yaml")
    old, new = Scorer(pop, None, rates=rates), Scorer(pop, None, rates=rates, missing_costs=costs)
    ph = BY["philharmonie"]
    assert new.utility(ph) < old.utility(ph)                                 # no longer scored as free
    london = [x for x in load_catalogue() if x.status == "ready"]
    assert model_costs(london, today=TODAY) == {}                            # every London card is priced
    s0 = Scorer(pop, None)
    s1 = Scorer(pop, None, missing_costs=model_costs(london, today=TODAY))
    assert [x.id for x in sorted(london, key=s0.utility)] == [x.id for x in sorted(london, key=s1.utility)]


def test_a_group_budget_never_counts_an_allowance_as_a_confirmed_price():   # m293
    from brain.group import _price
    xs, made = with_allowances(READY, today=TODAY)
    ch = next(x for x in xs if x.id.endswith("chasse-nature"))
    assert ch.price.known and _price(ch, "EUR") is None                      # an estimate, so left out and named
    assert _price(BY["rodin"], "EUR") == BY["rodin"].price.value.amount
