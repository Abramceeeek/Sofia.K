"""m254 (Abram, m252): today's ranking rule against two alternatives, before any change. SYNTHETIC PEOPLE ONLY.

Rules: "today" (any doubt before relevance), "0.10 a doubt" (m249), "calibrated" (the expected chance of a good visit
given what's uncertain for this use: quality.uncertainties and RISK). The 11 travellers and the set-up are those of
benchmark_profiles.py (London 49, Paris ready; a Tuesday and a Saturday; top 5; EUR at the 6 Nov ECB rate).

Each dimension is reported separately, not just the average chance of "Good":
- relevance: mean chance of "Good" in the top 5, and the traveller's own kind;
- poorly suited: share of the top 5 below the traveller's own median match in that city (complete data or not);
- practicality: share judged good; share whose hours aren't known at all for the day; places closed that day (must be 0);
- money: share judged good; share with an unknown price;
- trust: share judged good;
- access: for the step-free traveller, places a source says aren't step-free (must be 0), and unverified ones.
Two stress cases, run per traveller and city:
- relevant but incomplete: the traveller's best match loses its hours (unknown), or keeps them only as text;
  is it still in the top 5?
- verified but poorly suited: a fully verified place that is the traveller's worst match: does it ever reach the
  top 5?

Run from brain/: `.venv/bin/python scripts/benchmark_ranking.py` → benchmarks/synthetic/ranking_rules.txt
"""

from __future__ import annotations

import importlib.util
import statistics
import sys
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
spec = importlib.util.spec_from_file_location("bp", HERE / "benchmark_profiles.py")
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)

from brain import quality  # noqa: E402
from brain.catalogue import OpeningHours, load_catalogue, load_dev  # noqa: E402
from brain.config import DATA_DIR  # noqa: E402
from brain.discovery import Scorer  # noqa: E402
from brain.population import load_population  # noqa: E402
from brain.moments import WEEKDAYS  # noqa: E402

RULES = {"today": dict(), "0.10 a doubt": dict(doubt_cost=0.10), "calibrated": dict(calibrated=True),
         "calib. price.03": dict(calibrated=True)}
# the last is a sensitivity run: an unknown price (no budget set) risks 0.03 instead of quality.RISK's 0.10
OVERRIDES = {"calib. price.03": {"price_unknown": 0.03}}


def ranked(s, xs, budget_gbp, needs, day, cur, rule):
    budget = None if budget_gbp is None else (budget_gbp if cur == "GBP" else round(budget_gbp / bp.RATES.per_eur["GBP"], 2))
    saved = dict(quality.RISK)
    quality.RISK.update(OVERRIDES.get(rule, {}))
    items = [(x, quality.assess(x, p_good=s.p_good(x), today=bp.TODAY, day=day, budget_left=budget,
                                needs_step_free=needs)) for x in xs]
    quality.RISK.clear()
    quality.RISK.update(saved)
    return quality.rank(items, **RULES[rule])


def main() -> int:
    pop = load_population(DATA_DIR / "priors.yaml")
    cities = {"London": ([x for x in load_catalogue() if x.status == "ready"], "GBP"),
              "Paris": ([x for x in load_dev("paris")[1] if x.status == "ready"], "EUR")}
    res: dict[tuple[str, str], dict[str, list]] = {}
    for name, (d, sig, budget, needs, _gap) in bp.PROFILES.items():
        s = Scorer(pop, bp.delta_for(pop, d), rates=bp.RATES)
        for city, (xs, cur) in cities.items():
            ps = {x.id: s.p_good(x) for x in xs}
            med = statistics.median(ps.values())
            best = max(xs, key=lambda x: ps[x.id])
            complete = [x for x in xs if x.hours.weekly is not None and x.price.known and x.price.trust != "estimated"]
            worst = min(complete, key=lambda x: ps[x.id]) if complete else None
            for rule in RULES:
                r = res.setdefault((rule, city), {k: [] for k in (
                    "p", "own", "unsuited", "prac", "hours_unknown", "closed", "money", "price_unknown", "trust",
                    "no_step", "unverified", "best_unknown", "best_text", "worst_in")})
                for day in bp.DAYS:
                    top = ranked(s, xs, budget, needs, day, cur, rule)[:bp.K]
                    r["p"].append(statistics.mean(a.p_good for _, a in top))
                    if sig:
                        r["own"].append(sum(1 for x, _ in top if x.category in sig) / bp.K)
                    r["unsuited"].append(sum(1 for x, _ in top if ps[x.id] < med) / bp.K)
                    r["prac"].append(sum(1 for _, a in top if a.practicality.level == "good") / bp.K)
                    r["hours_unknown"].append(sum(1 for x, _ in top if not x.hours.text and not getattr(x.facet, "event_based", False)) / bp.K)
                    r["closed"].append(sum(1 for x, _ in top if x.hours.open_on(WEEKDAYS[day.weekday()]) is False))
                    r["money"].append(sum(1 for _, a in top if a.money.level == "good") / bp.K)
                    r["price_unknown"].append(sum(1 for x, _ in top if not x.price.known) / bp.K)
                    r["trust"].append(sum(1 for _, a in top if a.trust.level == "good") / bp.K)
                    if needs:
                        sf = lambda x: x.accessibility.step_free
                        r["no_step"].append(sum(1 for x, _ in top if sf(x).known and sf(x).value == "no"))
                        r["unverified"].append(sum(1 for x, _ in top if not sf(x).known) / bp.K)
                    # stress: the best match with its hours unknown, then as text only
                    for key, hrs in (("best_unknown", OpeningHours(None, None, "unknown", None, None)),
                                     ("best_text", OpeningHours("Hours vary by season (test)", None, "checked", "test", best.hours.checked))):
                        alt = [replace(x, hours=hrs) if x.id == best.id else x for x in xs]
                        r[key].append(best.id in {x.id for x, _ in ranked(s, alt, budget, needs, day, cur, rule)[:bp.K]})
                    if worst is not None:
                        r["worst_in"].append(worst.id in {x.id for x, _ in top})
    pct = lambda v: f"{statistics.mean(v):.0%}" if v else "—"
    out = ["SYNTHETIC PEOPLE ONLY. Three ranking rules compared on 11 travellers (scripts/benchmark_profiles.py), London",
           f"({len(cities['London'][0])}) and Paris ({len(cities['Paris'][0])} ready, development only). Top 5, a Tuesday and a Saturday.",
           "The calibrated rule's risks are GUESSES (quality.RISK), to be calibrated on real outcomes.", "",
           "Relevance, and how well suited the top 5 are:",
           f"{'rule':<16}{'city':<8}{'p(Good)':>8}{'own kind':>9}{'below own median':>18}"]
    for (rule, city), r in res.items():
        out.append(f"{rule:<16}{city:<8}{statistics.mean(r['p']):>8.2f}{pct(r['own']):>9}{pct(r['unsuited']):>18}")
    out += ["", "Practicality, money and trust, each on its own (share of the top 5):",
            f"{'rule':<16}{'city':<8}{'practical good':>15}{'hours unknown':>14}{'closed':>7}{'money good':>11}"
            f"{'price unknown':>14}{'trust good':>11}"]
    for (rule, city), r in res.items():
        out.append(f"{rule:<16}{city:<8}{pct(r['prac']):>15}{pct(r['hours_unknown']):>14}{sum(r['closed']):>7}"
                   f"{pct(r['money']):>11}{pct(r['price_unknown']):>14}{pct(r['trust']):>11}")
    out += ["", "Step-free traveller (a stated need): places a source says aren't step-free in the top 5 (must be 0),",
            "and places whose access isn't verified (shown as unverified, never as step-free):",
            f"{'rule':<16}{'city':<8}{'not step-free':>14}{'unverified':>11}"]
    for (rule, city), r in res.items():
        out.append(f"{rule:<16}{city:<8}{sum(r['no_step']):>14}{pct(r['unverified']):>11}")
    out += ["", "Stress cases, over 11 travellers × 2 days:",
            f"{'rule':<16}{'city':<8}{'best match, hours unknown':>27}{'best match, hours as text':>27}{'worst verified match':>22}",
            f"{'':<24}{'(still in the top 5)':>27}{'(still in the top 5)':>27}{'(reaches the top 5)':>22}"]
    for (rule, city), r in res.items():
        out.append(f"{rule:<16}{city:<8}{pct(r['best_unknown']):>27}{pct(r['best_text']):>27}{pct(r['worst_in']):>22}")
    Path("benchmarks/synthetic/ranking_rules.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
