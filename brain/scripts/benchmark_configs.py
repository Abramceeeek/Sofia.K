"""m261 (Abram, m260): the three ranking configurations (quality.CONFIGS) compared on all four dimensions, for internal
testing. SYNTHETIC PEOPLE ONLY: not evidence of customer satisfaction. ranking_rules.txt (m254) is kept as it was.

Set-up as benchmark_ranking.py: 11 travellers, London and Paris (ready places), top 5 on a Tuesday and a Saturday. Paris
is run twice: as read (unknown prices unknown), and with planning allowances (priceestimate.py) where 3+ comparable
prices exist. Per configuration and city, each dimension on its own:
- relevance: the mean chance of "Good", and the traveller's own kind;
- practicality: confirmed open on the day; might be open (hours unknown or varying); closed (must be 0);
- money: judged good; unknown price; planning allowance;
- trust: judged good.

Run from brain/: `.venv/bin/python scripts/benchmark_configs.py` → benchmarks/synthetic/ranking_configs.txt
"""

from __future__ import annotations

import importlib.util
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
spec = importlib.util.spec_from_file_location("bp", HERE / "benchmark_profiles.py")
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)

from brain import quality  # noqa: E402
from brain.catalogue import load_catalogue, load_dev  # noqa: E402
from brain.config import DATA_DIR  # noqa: E402
from brain.discovery import Scorer  # noqa: E402
from brain.population import load_population  # noqa: E402
from brain.priceestimate import with_allowances  # noqa: E402


def main() -> int:
    pop = load_population(DATA_DIR / "priors.yaml")
    paris = [x for x in load_dev("paris")[1] if x.status == "ready"]
    cities = {"London": ([x for x in load_catalogue() if x.status == "ready"], "GBP"), "Paris": (paris, "EUR"),
              "Paris+allow": (with_allowances(paris)[0], "EUR")}
    rows = {}
    for name, (d, sig, budget, needs, _gap) in bp.PROFILES.items():
        s = Scorer(pop, bp.delta_for(pop, d), rates=bp.RATES)
        for city, (xs, cur) in cities.items():
            for cfg_name, cfg in quality.CONFIGS.items():
                r = rows.setdefault((cfg_name, city), {k: [] for k in (
                    "p", "own", "confirmed", "might", "closed", "money", "unknown", "allowance", "trust")})
                bud = None if budget is None else (budget if cur == "GBP" else round(budget / bp.RATES.per_eur["GBP"], 2))
                for day in bp.DAYS:
                    top = quality.rank([(x, quality.assess(x, p_good=s.p_good(x), today=bp.TODAY, day=day,
                                                           budget_left=bud, needs_step_free=needs, risk=cfg["risk"]))
                                        for x in xs], calibrated=cfg["calibrated"])[:bp.K]
                    st = [quality.open_status(x, day) for x, _ in top]
                    k = bp.K
                    r["p"].append(statistics.mean(a.p_good for _, a in top))
                    if sig:
                        r["own"].append(sum(1 for x, _ in top if x.category in sig) / k)
                    r["confirmed"].append(st.count("confirmed open") / k)
                    r["might"].append(st.count("might be open") / k)
                    r["closed"].append(st.count("confirmed closed"))
                    r["money"].append(sum(1 for _, a in top if a.money.level == "good") / k)
                    r["unknown"].append(sum(1 for x, _ in top if not x.price.known) / k)
                    r["allowance"].append(sum(1 for x, _ in top if (x.price.source or "").startswith("median")) / k)
                    r["trust"].append(sum(1 for _, a in top if a.trust.level == "good") / k)
    pct = lambda v: f"{statistics.mean(v):.0%}" if v else "—"
    out = ["SYNTHETIC PEOPLE ONLY: not evidence of customer satisfaction. The three configurations (quality.CONFIGS) on",
           "11 travellers; top 5 on Tue 24 and Sat 28 Nov 2026. 'Paris+allow': unknown prices given a median planning",
           "allowance where 3+ comparable prices exist (priceestimate.py). The baseline stays the default.", "",
           f"{'configuration':<25}{'city':<12}{'p(Good)':>8}{'own kind':>9} | {'confirmed open':>14}{'might be open':>14}"
           f"{'closed':>7} | {'money good':>10}{'unknown':>8}{'allowance':>10} | {'trust good':>10}"]
    for city in cities:
        for cfg_name in quality.CONFIGS:
            r = rows[(cfg_name, city)]
            out.append(f"{cfg_name:<25}{city:<12}{statistics.mean(r['p']):>8.2f}{pct(r['own']):>9} | "
                       f"{pct(r['confirmed']):>14}{pct(r['might']):>14}{sum(r['closed']):>7} | {pct(r['money']):>10}"
                       f"{pct(r['unknown']):>8}{pct(r['allowance']):>10} | {pct(r['trust']):>10}")
    Path("benchmarks/synthetic/ranking_configs.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
