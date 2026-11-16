"""m262 (Abram, m260): an unknown price gets a labelled planning allowance only with enough comparable prices; budgets
keep confirmed, estimated and unknown spending apart and never claim a fit they can't verify."""
from dataclasses import replace

from brain.catalogue import Money, load_dev
from brain.places import Fact
from brain.priceestimate import MIN_SAMPLE, allowance, budget_breakdown, with_allowances

READY = [x for x in load_dev("paris")[1] if x.status == "ready"]
BY = {x.id.split(":")[-1]: x for x in READY}


def test_an_allowance_needs_enough_comparable_prices_and_says_what_it_is():
    a = allowance(BY["chasse-nature"], READY)                       # a museum with no price read
    assert a is not None and a.n >= MIN_SAMPLE and a.currency == "EUR"
    assert a.basis == "category: culture"                           # only 2 priced museums: the category instead
    assert a.conservative >= a.amount and "not this place's price" in a.label()
    assert a.observed[0] <= a.observed[1] and len(a.peers) == a.n and BY["chasse-nature"].id not in a.peers


def test_too_few_comparable_prices_leaves_it_unknown():
    assert allowance(BY["enfants-rouges"], READY) is None           # one priced food place: not enough
    assert allowance(BY["philharmonie"], READY) is None             # one priced entertainment place
    assert allowance(BY["rodin"], READY) is None                    # it has its own price


def test_allowances_are_marked_as_estimates_never_prices():
    xs, made = with_allowances(READY)
    ch = next(x for x in xs if x.id.endswith("chasse-nature"))
    assert ch.price.trust == "estimated" and ch.price.source.startswith("median") and ch.id in made
    assert not next(x for x in xs if x.id.endswith("enfants-rouges")).price.known   # still unknown


def test_budgets_never_claim_a_fit_they_cannot_verify():
    xs, made = with_allowances(READY)
    pick = lambda *ids: [x for x in xs if x.id.split(":")[-1] in ids]
    assert budget_breakdown(pick("rodin", "pantheon"), made, 40)["status"] == "fits"             # verified only
    est = budget_breakdown(pick("rodin", "chasse-nature"), made, 60)
    assert est["status"] == "likely fits" and "isn't guaranteed" in est["say"]                   # strict: not a promise
    assert est["estimated_conservative"] >= est["estimated"]
    unk = budget_breakdown(pick("rodin", "enfants-rouges"), made, 100)
    assert unk["status"] == "can't be verified yet" and unk["unknown"]                           # never free
    assert budget_breakdown(pick("catacombes", "sainte-chapelle"), made, 40)["status"] == "over budget"
