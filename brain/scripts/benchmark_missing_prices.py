"""m293 (Abram, 19 Nov): does the model reward a place for having no price? The old rule scored a missing price as no
cost at all (free); the new one uses a valid planning allowance, or else a neutral figure (the city's median paid
price), with the uncertainty penalty kept separate (quality.RISK). SYNTHETIC TRAVELLERS ONLY: not evidence of real
satisfaction. Writes benchmarks/synthetic/missing_prices.txt. Run from brain/: `.venv/bin/python
scripts/benchmark_missing_prices.py`.

1. **Masking.** For each priced ready place and each of the 11 benchmark travellers, the place's rank by the model's
   utility with its real price, then with its price hidden, under each rule. A place that climbs 3 or more places only
   because its price went missing is "rewarded". Split by traveller (budget-conscious or not), by price band (free,
   inexpensive, expensive: either side of the city's median paid price) and by currency (London GBP, Paris EUR).
2. **Incomplete coverage.** London with 30% of its prices hidden (fixed seed): how many of each traveller's top 5
   have a hidden price, and how much of the real-price top 5 survives, under each rule.
3. **Group budgets.** 200 groups of three (one budget-conscious) on London with 30% hidden, with and without a daily
   budget: stops with an unconfirmed price under each rule. With a budget none may appear (m255, m293).
"""

from __future__ import annotations

import importlib.util
import random
import statistics
import sys
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
spec = importlib.util.spec_from_file_location("bp", HERE / "benchmark_profiles.py")
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)

from brain.catalogue import load_catalogue, load_dev  # noqa: E402
from brain.config import DATA_DIR  # noqa: E402
from brain.discovery import Scorer, cost_gbp  # noqa: E402
from brain.group import Member, _price, plan  # noqa: E402
from brain.places import Fact  # noqa: E402
from brain.population import load_population  # noqa: E402
from brain.priceestimate import model_costs, with_allowances  # noqa: E402

TODAY = bp.TODAY
REWARDED = 3          # places climbed only because the price went missing


def _hide(x):
    return replace(x, price=Fact.unknown())


def _rank(s: Scorer, xs, target_id: str) -> int:
    order = sorted(xs, key=lambda y: -s.utility(y))
    return next(i for i, y in enumerate(order) if y.id == target_id)


def masking(pop, city: str, xs) -> list[dict]:
    rows = []
    paid = sorted(c for x in xs if (c := cost_gbp(x, bp.RATES)) is not None and c > 0)
    mid = statistics.median(paid)
    for name, (d, *_rest) in bp.PROFILES.items():
        delta = bp.delta_for(pop, d)
        true = Scorer(pop, delta, rates=bp.RATES)
        for x in xs:
            c = cost_gbp(x, bp.RATES)
            if c is None:
                continue
            masked = [_hide(y) if y.id == x.id else y for y in xs]
            old = Scorer(pop, delta, rates=bp.RATES)
            new = Scorer(pop, delta, rates=bp.RATES,
                         missing_costs=model_costs(masked, today=TODAY, rates=bp.RATES, figure="median"))
            cons = Scorer(pop, delta, rates=bp.RATES,
                          missing_costs=model_costs(masked, today=TODAY, rates=bp.RATES, figure="conservative"))
            r0 = _rank(true, xs, x.id)
            rows.append({"city": city, "budget": name == "budget-conscious",
                         "band": "free" if c == 0 else ("inexpensive" if c <= mid else "expensive"),
                         "old": _rank(old, masked, x.id) - r0, "new": _rank(new, masked, x.id) - r0,
                         "cons": _rank(cons, masked, x.id) - r0})
    return rows


def _summary(rows, rule) -> str:
    if not rows:
        return "-"
    moves = [r[rule] for r in rows]
    up = sum(1 for m in moves if m <= -REWARDED) / len(moves)
    return f"{statistics.mean(moves):+5.1f} {up:5.0%}"


def coverage(pop, xs, share=0.3, seed=20261119):
    rng = random.Random(seed)
    hidden = {x.id for x in rng.sample([x for x in xs if x.price.known], round(share * len(xs)))}
    masked = [_hide(x) if x.id in hidden else x for x in xs]
    costs = model_costs(masked, today=TODAY, rates=bp.RATES)
    out = {"old": [], "new": []}
    for _name, (d, *_rest) in bp.PROFILES.items():
        delta = bp.delta_for(pop, d)
        real = {y.id for y in sorted(xs, key=lambda y: -Scorer(pop, delta, rates=bp.RATES).utility(y))[:5]}
        for rule, s in (("old", Scorer(pop, delta, rates=bp.RATES)),
                        ("new", Scorer(pop, delta, rates=bp.RATES, missing_costs=costs))):
            top = [y.id for y in sorted(masked, key=lambda y: -s.utility(y))[:5]]
            out[rule].append((sum(1 for i in top if i in hidden), len(real & set(top))))
    return hidden, out


def groups(pop, xs, hidden, n=200, seed=7):
    rng = random.Random(seed)
    masked, _ = with_allowances([_hide(x) if x.id in hidden else x for x in xs], today=TODAY)
    costs = model_costs([_hide(x) if x.id in hidden else x for x in xs], today=TODAY, rates=bp.RATES)
    names = [k for k in bp.PROFILES if k != "accessibility-focused"]
    res = {}
    for budget in (None, 15.0):
        for rule in ("old", "new"):
            unconfirmed = total = 0
            for _ in range(n):
                trio = ["budget-conscious", *rng.sample([k for k in names if k != "budget-conscious"], 2)]
                members = [Member(f"Member {'ABC'[i]}", Scorer(pop, bp.delta_for(pop, bp.PROFILES[k][0]), rates=bp.RATES,
                                                               missing_costs=costs if rule == "new" else None),
                                  budget_per_day=budget) for i, k in enumerate(trio)]
                g = plan(members, masked, days=1, per_day=4, rates=bp.RATES)
                total += len(g.stops)
                unconfirmed += sum(1 for x in g.stops if _price(x, "GBP", bp.RATES) is None)
            res[(budget, rule)] = (unconfirmed, total)
    return res


def main() -> int:
    pop = load_population(DATA_DIR / "priors.yaml")
    london = [x for x in load_catalogue() if x.status == "ready"]
    paris = [x for x in load_dev("paris")[1] if x.status == "ready"]
    rows = masking(pop, "London (GBP)", london) + masking(pop, "Paris (EUR)", paris)
    lines = ["SYNTHETIC TRAVELLERS ONLY: not evidence of real satisfaction. m293: a missing price under the old rule (no",
             "cost: scored as free) and the new one (a valid allowance, else the city's paid prices; the uncertainty",
             "penalty stays separate). 'new: median' uses medians; 'new: upper q.' uses upper quartiles, the default and",
             "what sections 2 and 3 use.",
             f"'Rewarded' = climbed {REWARDED}+ places only because the price went missing.", "",
             "1. Masking: mean change in rank (negative = climbed) and the share rewarded",
             f"{'group':<40}{'old: free':>14}{'new: median':>14}{'new: upper q.':>15}{'n':>7}"]
    groups_ = [("all", lambda r: True)]
    groups_ += [(c, lambda r, c=c: r["city"] == c) for c in ("London (GBP)", "Paris (EUR)")]
    groups_ += [("budget-conscious traveller", lambda r: r["budget"]), ("other travellers", lambda r: not r["budget"])]
    groups_ += [(f"{b} places", lambda r, b=b: r["band"] == b) for b in ("free", "inexpensive", "expensive")]
    for label, f in groups_:
        sel = [r for r in rows if f(r)]
        lines.append(f"{label:<40}{_summary(sel, 'old'):>14}{_summary(sel, 'new'):>14}{_summary(sel, 'cons'):>15}"
                     f"{len(sel):>7}")
    hidden, cov = coverage(pop, london)
    lines += ["", f"2. Incomplete coverage: London with {len(hidden)} of {len(london)} prices hidden (30%, seed fixed)",
              f"{'rule':<10}{'hidden-price places in top 5 (mean)':>38}{'real top 5 kept (mean)':>26}"]
    for rule in ("old", "new"):
        h = statistics.mean(a for a, _ in cov[rule])
        k = statistics.mean(b for _, b in cov[rule])
        lines.append(f"{rule:<10}{h:>38.2f}{k:>26.2f}")
    g = groups(pop, london, hidden)
    lines += ["", "3. Group budgets: 200 groups of three (one budget-conscious), London with the same 30% hidden",
              f"{'daily budget':<16}{'rule':<8}{'stops with an unconfirmed price':>34}"]
    for (budget, rule), (u, t) in g.items():
        lines.append(f"{'none' if budget is None else f'GBP {budget:g}':<16}{rule:<8}{f'{u} of {t}':>34}")
    out = HERE.parent / "benchmarks" / "synthetic" / "missing_prices.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
