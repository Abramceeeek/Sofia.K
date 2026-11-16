"""m262 (Abram, m260): an unknown price is never zero. Where enough comparable places have known prices, ODYS uses their
median as a **planning allowance**, said as an allowance and never as the place's price; otherwise it stays unknown.

The rules:
- **Comparable:** ready places in the same city, priced in the same currency, with a verified or venue-stated price
  (an earlier estimate is never a peer). The same type first (museum with museum); if too few, the same category.
- **Enough:** at least `MIN_SAMPLE` (3, a GUESS). Fewer, and the price stays unknown.
- **Recorded:** the sample size, what it was drawn from, and the dates its prices were checked.
- **Two figures:** the median is the planning allowance; the upper quartile is the **conservative** figure used for a
  budget check, because a median is not a maximum.

Budgets keep three kinds of spending apart: **confirmed** (a verified price), **estimated** (an allowance or a
planning estimate) and **unknown**. A strict budget can only be confirmed when everything is confirmed; with
estimates it "likely fits" at the conservative figure, and with unknowns its total "can't be verified yet".
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, replace

from .catalogue import Experience, Money
from .places import Fact

MIN_SAMPLE = 3                      # GUESS: fewer comparable prices and nothing is estimated


@dataclass(frozen=True)
class Allowance:
    amount: float                   # the median: the planning allowance
    conservative: float             # the upper quartile: for budget checks
    currency: str
    basis: str                      # "type: museum" or "category: culture"
    n: int
    observed: tuple[str, str]       # the earliest and latest dates its prices were checked
    peers: tuple[str, ...]

    def label(self) -> str:
        return (f"No verified price. Planning allowance about {self.amount:g} {self.currency}: the median of {self.n} "
                f"{self.basis} prices here (checked {self.observed[0]} to {self.observed[1]}), not this place's price.")


def _priced(x: Experience) -> bool:
    return x.price.known and x.price.trust in ("checked", "claimed") and not (x.price.source or "").startswith("median")


def allowance(x: Experience, places: list[Experience], min_sample: int = MIN_SAMPLE) -> Allowance | None:
    if x.price.known:
        return None
    cur = next((p.price.value.currency for p in places if _priced(p)), None)
    pool = [p for p in places if p.id != x.id and p.status == "ready" and _priced(p)
            and p.geo.locality == x.geo.locality and p.price.value.currency == cur]
    for basis, same in (("type", lambda p: p.category == x.category and p.type == x.type),
                        ("category", lambda p: p.category == x.category)):
        peers = [p for p in pool if same(p)]
        if len(peers) >= min_sample:
            amounts = sorted(p.price.value.amount for p in peers)
            q3 = statistics.quantiles(amounts, n=4, method="inclusive")[2]
            dates = sorted(p.price.checked or "" for p in peers)
            return Allowance(round(statistics.median(amounts), 2), round(q3, 2), cur,
                             f"{basis}: {x.type if basis == 'type' else x.category}", len(peers),
                             (dates[0], dates[-1]), tuple(p.id for p in peers))
    return None


def with_allowances(places: list[Experience]) -> tuple[list[Experience], dict[str, Allowance]]:
    """The places with an allowance where one can be made, marked `estimated` with a source starting "median" (so
    quality.py names it as an allowance), and the allowances themselves."""
    out, made = [], {}
    for x in places:
        a = allowance(x, places)
        if a is None:
            out.append(x)
            continue
        made[x.id] = a
        out.append(replace(x, price=Fact(Money(a.amount, a.currency, "entry"), "estimated",
                                         f"median of {a.n} ({a.basis}); not this place's price", a.observed[1])))
    return out, made


def budget_breakdown(items: list[Experience], allowances: dict[str, Allowance], budget: float | None,
                     strict: bool = True) -> dict:
    """Confirmed, estimated and unknown spending, kept apart, and what can honestly be said about the budget."""
    confirmed = [x for x in items if _priced(x)]
    estimated = [x for x in items if x.price.known and not _priced(x)]
    unknown = [x for x in items if not x.price.known]
    c = round(sum(x.price.value.amount for x in confirmed), 2)
    e_mid = round(sum(x.price.value.amount for x in estimated), 2)
    e_high = round(sum(allowances[x.id].conservative if x.id in allowances else x.price.value.amount
                       for x in estimated), 2)
    out = {"confirmed": c, "estimated": e_mid, "estimated_conservative": e_high,
           "unknown": [x.title for x in unknown], "budget": budget}
    if budget is None:
        out["status"] = "no budget"
    elif c > budget:
        out["status"] = "over budget"
    elif unknown:
        out["status"] = "can't be verified yet"           # an unknown cost could be anything
    elif not estimated:
        out["status"] = "fits"
    elif c + e_high <= budget:
        out["status"] = "likely fits" if strict else "fits with estimates"
    else:
        out["status"] = "may not fit"
    out["say"] = {
        "no budget": "No budget set.",
        "over budget": "Over budget on confirmed prices alone.",
        "can't be verified yet": f"Some costs aren't known ({', '.join(out['unknown'])}), so the total can't be "
                                 "verified yet.",
        "fits": "Fits your budget on verified prices.",
        "likely fits": "Likely fits, but part of it is an estimate, so it isn't guaranteed.",
        "fits with estimates": "Fits, counting planning allowances at their higher figure.",
        "may not fit": "May not fit once the estimated costs are known.",
    }[out["status"]]
    return out


__all__ = ["Allowance", "allowance", "with_allowances", "budget_breakdown", "MIN_SAMPLE"]
