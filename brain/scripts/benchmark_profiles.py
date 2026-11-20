"""m249 (WS3): the Brain's recommendations for 11 international synthetic travellers, in London and in Paris.

SYNTHETIC PEOPLE ONLY. Each profile is a person-weight vector δ (in prior-sd units, on the model's own features),
plus at most one stated rule (a budget, step-free access). Nothing is inferred about anyone: no age, nationality,
health or family facts; a "family" or "accessibility" traveller is only the preference or rule written here.

For each profile and city, the top 5 of the ready experiences, ranked by quality.rank (relevance, practicality,
money, trust) on a Tuesday and a Saturday in late November 2026:
- relevance: mean chance of "Good" or better, and the lift over the city's average;
- practicality / money / trust: the share of the top 5 judged good on each;
- diversity: distinct categories in the top 5;
- transfer: whether the profile's own signature category leads in both cities;
- sensitivity to missing information: how much the top 5 changes when (a) an unknown price is treated as the
  city's median instead of nothing, and (b) all step-free facts are hidden (the accessibility traveller).

Prices in euros are converted for the model's cost term at the ECB rate of 6 Nov 2026 (EUR 1 = GBP 0.83415, the
test fixture read on 7 Nov), stated as an assumption; the live ECB fetch stays off.

Run from brain/: `.venv/bin/python scripts/benchmark_profiles.py` → benchmarks/synthetic/profiles.txt
"""

from __future__ import annotations

import statistics
import sys
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from brain import quality  # noqa: E402
from brain.catalogue import Accessibility, Money, load_catalogue, load_dev  # noqa: E402
from brain.config import DATA_DIR  # noqa: E402
from brain.discovery import Scorer  # noqa: E402
from brain.fx import Rates  # noqa: E402
from brain.places import Fact  # noqa: E402
from brain.population import load_population  # noqa: E402

TODAY = date(2026, 11, 11)
DAYS = (date(2026, 11, 24), date(2026, 11, 28))        # a Tuesday and a Saturday
RATES = Rates({"EUR": 1.0, "GBP": 0.83415}, date(2026, 11, 6), datetime(2026, 11, 7, tzinfo=timezone.utc),
              "ECB (the test fixture's 6 Nov 2026 rates, read 7 Nov 2026)")
K = 5

# name: (δ on features in prior-sd units, signature categories, budget per stop in GBP, needs step-free, what the
#        model can't represent)
PROFILES = {
    "museum enthusiast": ({"history_culture": 2, "absorption": 1}, {"culture"}, None, False, None),
    "architecture enthusiast": ({"iconic": 1.5, "awe": 1.5, "photo_potential": 1, "contrast_reveal": 1},
                                {"culture", "views", "neighbourhood"}, None, False,
                                "no architecture feature: iconic, awe, photos and reveal stand in"),
    "nature enthusiast": ({"green_nature": 2, "crowds": -1}, {"nature"}, None, False, None),
    "food-experience enthusiast": ({"food": 2, "local_novel": 1, "social_pull": 0.5}, {"food_drink"}, None, False, None),
    "shopping enthusiast": ({"local_novel": 0.5}, {"shopping"}, None, False,
                            "no shopping taste in the model (m229): it can't be represented"),
    "entertainment enthusiast": ({"absorption": 2, "social_pull": 1}, {"entertainment", "activity"}, None, False,
                                 "no entertainment feature: absorption and social pull stand in"),
    "budget-conscious": ({"cost_per_10gbp": 1.5}, set(), 12.0, False, None),
    "relaxed": ({"walking_effort": -1.5, "active": -1, "crowds": -1}, set(), None, False, None),
    "active": ({"active": 2, "walking_effort": 1}, {"activity", "nature"}, None, False, None),
    "family": ({"social_pull": 1, "crowds": -0.5, "walking_effort": -0.5}, set(), None, False,
               "no child-suitability data, and none is inferred: a stated preference only"),
    "accessibility-focused": ({}, set(), None, True, None),
}


def delta_for(pop, d: dict) -> np.ndarray:
    v = np.zeros(len(pop.delta_prior_sd))
    personal = [pop.names[i] for i in pop.personal_idx] if hasattr(pop, "personal_idx") else pop.names
    for k, z in d.items():
        v[personal.index(k)] = z * float(pop.delta_prior_sd[personal.index(k)])
    return v


def with_median_cost(xs):
    """Sensitivity (a): an unknown price imputed as the city's median known price (an assumption, not a fact)."""
    known = [x.price.value.amount for x in xs if x.price.known]
    med = statistics.median(known) if known else 0.0
    cur = next((x.price.value.currency for x in xs if x.price.known), "GBP")
    return [x if x.price.known else replace(x, price=Fact(Money(med, cur, "entry"), "estimated", "median", None))
            for x in xs]


def hide_access(xs):
    return [replace(x, accessibility=Accessibility(Fact.unknown())) for x in xs]


RULE = None   # the ranking rule in use: None = today's (doubts first); a float = quality.rank's doubt_cost


def top(scorer, xs, budget_gbp, needs, day, currency):
    budget = None if budget_gbp is None else (budget_gbp if currency == "GBP" else round(budget_gbp / RATES.per_eur["GBP"], 2))
    ranked = quality.rank([(x, quality.assess(x, p_good=scorer.p_good(x), today=TODAY, day=day, budget_left=budget,
                                             needs_step_free=needs)) for x in xs], doubt_cost=RULE)
    return ranked[:K]


def run(pop, cities):
    rows, picks = [], {}
    for name, (d, sig, budget, needs, gap) in PROFILES.items():
        s = Scorer(pop, delta_for(pop, d), rates=RATES)
        for city, (xs, cur) in cities.items():
            base = statistics.mean(s.p_good(x) for x in xs)
            per_day = [top(s, xs, budget, needs, day, cur) for day in DAYS]
            t = [p for day in per_day for p in day]
            ids = [x.id for x, _ in per_day[0]]
            picks[(name, city)] = ids
            good = lambda f: sum(1 for _, a in t if getattr(a, f).level == "good") / len(t)
            cats = len({x.category for x, _ in per_day[0]})
            lead = per_day[0][0][0].category
            a_ids = {x.id for x, _ in top(s, with_median_cost(xs), budget, needs, DAYS[0], cur)}
            h_ids = {x.id for x, _ in top(s, hide_access(xs), budget, needs, DAYS[0], cur)} if needs else set(ids)
            no_step = sum(1 for x, a in per_day[0] if x.accessibility.step_free.known and x.accessibility.step_free.value == "no")
            rows.append(dict(profile=name, city=city, p=statistics.mean(a.p_good for _, a in t), lift=statistics.mean(
                a.p_good for _, a in t) - base, prac=good("practicality"), money=good("money"), trust=good("trust"),
                cats=cats, sig=(sum(1 for x, _ in per_day[0] if x.category in sig) / K) if sig else None, lead=lead,
                d_cost=len(set(ids) ^ a_ids) // 2, d_access=len(set(ids) ^ h_ids) // 2, no_step=no_step, gap=gap,
                titles=[x.title for x, _ in per_day[0]]))
    return rows, picks


def main() -> int:
    pop = load_population(DATA_DIR / "priors.yaml")
    london = [x for x in load_catalogue() if x.status == "ready"]
    _, paris_all, _ = load_dev("paris")
    paris = [x for x in paris_all if x.status == "ready"]
    global RULE
    summary, by_rule = [], {}
    for rule in (None, 0.05, 0.10):
        RULE = rule
        rs, _ = run(pop, {"London": (london, "GBP"), "Paris": (paris, "EUR")})
        by_rule[rule] = {(r["profile"], r["city"]): r["sig"] for r in rs}
        for city in ("London", "Paris"):
            c = [r for r in rs if r["city"] == city]
            sig = [r["sig"] for r in c if r["sig"] is not None]
            summary.append(f"{'doubts first (today)' if rule is None else f'match less {rule:.2f} a doubt':<26}{city:<8}"
                           f"{statistics.mean(r['p'] for r in c):>8.2f}{statistics.mean(sig):>9.0%}"
                           f"{statistics.mean(r['prac'] for r in c):>10.0%}{statistics.mean(r['money'] for r in c):>7.0%}"
                           f"{statistics.mean(r['trust'] for r in c):>7.0%}{statistics.mean(r['cats'] for r in c):>7.1f}")
    RULE = None
    rows, picks = run(pop, {"London": (london, "GBP"), "Paris": (paris, "EUR")})
    out = ["SYNTHETIC PEOPLE ONLY. 11 travellers, the Brain's ranking (quality.rank) of the ready experiences:",
           f"London {len(london)}, Paris {len(paris)} (development only). Top {K} on Tue 24 and Sat 28 Nov 2026.",
           "EUR prices enter the model's cost term at ECB 6 Nov 2026 (EUR 1 = GBP 0.83415), an assumption.", "",
           f"{'profile':<27}{'city':<8}{'p(Good)':>8}{'lift':>7}{'practical':>10}{'money':>7}{'trust':>7}"
           f"{'kinds':>6}{'own kind':>9}{'Δ cost':>7}{'Δ access':>9}"]
    for r in rows:
        sig = "—" if r["sig"] is None else f"{r['sig']:.0%}"
        out.append(f"{r['profile']:<27}{r['city']:<8}{r['p']:>8.2f}{r['lift']:>+7.2f}{r['prac']:>10.0%}{r['money']:>7.0%}"
                   f"{r['trust']:>7.0%}{r['cats']:>6}{sig:>9}{r['d_cost']:>7}{r['d_access']:>9}")
    out += ["", "The ranking rule, averaged over the 11 profiles (own kind: over the 8 with a signature kind):",
            f"{'rule':<26}{'city':<8}{'p(Good)':>8}{'own kind':>9}{'practical':>10}{'money':>7}{'trust':>7}{'kinds':>7}"]
    out += summary
    out += ["", "Transfer: the profile's own kind in its top 5, London and Paris, under today's rule and at 0.10 a doubt:",
            f"{'profile':<27}{'today L':>8}{'today P':>8}{'0.10 L':>8}{'0.10 P':>8}"]
    for name, (_, sig, *_rest) in PROFILES.items():
        if sig:
            v = lambda rule, city: by_rule[rule][(name, city)]
            out.append(f"{name:<27}{v(None, 'London'):>8.0%}{v(None, 'Paris'):>8.0%}{v(0.10, 'London'):>8.0%}"
                       f"{v(0.10, 'Paris'):>8.0%}")
    out += ["", "Δ cost: of the top 5, how many change when an unknown price is imputed at the city's median.",
            "Δ access: for the accessibility traveller, how many change when every step-free fact is hidden.",
            "own kind: share of the top 5 in the profile's signature categories (— when it has none).", "",
            "Top 5 on the Tuesday (first title each):"]
    for r in rows:
        out.append(f"- {r['profile']} / {r['city']}: " + "; ".join(t.split(':')[0][:38] for t in r["titles"]))
    gaps = {r["profile"]: r["gap"] for r in rows if r["gap"]}
    out += ["", "What the model can't represent (limitations, said rather than guessed):"]
    out += [f"- {k}: {v}" for k, v in gaps.items()]
    acc = [r for r in rows if r["profile"] == "accessibility-focused"]
    out += ["", "Accessibility traveller: places marked not step-free in the top 5: "
            + ", ".join(f"{r['city']} {r['no_step']}" for r in acc) + " (a stated need is a rule)."]
    Path("benchmarks/synthetic").mkdir(parents=True, exist_ok=True)
    Path("benchmarks/synthetic/profiles.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
