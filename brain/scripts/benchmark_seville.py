"""m318: the 11 international synthetic travellers (benchmark_profiles.py) in London and Seville, unchanged ranking.

SYNTHETIC PEOPLE ONLY: not evidence that a real person would enjoy any of this. Seville is a development destination
(data/dev/seville.yaml); nothing here offers it to anyone. The default ranking rule is used (doubts first), the same
as production; no experimental configuration.

Days: Tue 24 and Sat 28 Nov 2026 (as benchmark_profiles), plus Sun 22 Nov 2026, the pilot traveller's arrival day,
when Seville's municipal markets are closed.

Run from brain/: `.venv/bin/python scripts/benchmark_seville.py` → benchmarks/synthetic/profiles_seville.txt
"""

from __future__ import annotations

import importlib.util
import statistics
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
spec = importlib.util.spec_from_file_location("benchmark_profiles", HERE / "benchmark_profiles.py")
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)

from brain import quality  # noqa: E402
from brain.catalogue import load_catalogue, load_dev  # noqa: E402
from brain.config import DATA_DIR  # noqa: E402
from brain.discovery import Scorer  # noqa: E402
from brain.population import load_population  # noqa: E402

SUNDAY = date(2026, 11, 22)


def sunday_top(pop, xs, name):
    d, sig, budget, needs, _ = bp.PROFILES[name]
    s = Scorer(pop, bp.delta_for(pop, d), rates=bp.RATES)
    return bp.top(s, xs, budget, needs, SUNDAY, "EUR")


def main() -> int:
    pop = load_population(DATA_DIR / "priors.yaml")
    london = [x for x in load_catalogue() if x.status == "ready"]
    seville = [x for x in load_dev("seville")[1] if x.status == "ready"]
    rows, _ = bp.run(pop, {"London": (london, "GBP"), "Seville": (seville, "EUR")})
    out = ["SYNTHETIC PEOPLE ONLY. 11 travellers, the Brain's default ranking (quality.rank, doubts first):",
           f"London {len(london)} ready, Seville {len(seville)} ready (DEVELOPMENT only, never offered). "
           f"Top {bp.K} on Tue 24 and Sat 28 Nov 2026.",
           "EUR prices enter the model's cost term at ECB 6 Nov 2026 (EUR 1 = GBP 0.83415), an assumption.", "",
           f"{'profile':<27}{'city':<9}{'p(Good)':>8}{'lift':>7}{'practical':>10}{'money':>7}{'trust':>7}"
           f"{'kinds':>6}{'own kind':>9}"]
    for r in rows:
        sig = "—" if r["sig"] is None else f"{r['sig']:.0%}"
        out.append(f"{r['profile']:<27}{r['city']:<9}{r['p']:>8.2f}{r['lift']:>+7.2f}{r['prac']:>10.0%}"
                   f"{r['money']:>7.0%}{r['trust']:>7.0%}{r['cats']:>6}{sig:>9}")
    out += ["", "Transfer: the share of the profile's own kind in its Tuesday top 5, London vs Seville:"]
    by = {(r["profile"], r["city"]): r for r in rows}
    for name, (_, sig, *_rest) in bp.PROFILES.items():
        if sig:
            out.append(f"- {name:<27} London {by[(name, 'London')]['sig']:.0%}   Seville {by[(name, 'Seville')]['sig']:.0%}")
    out += ["", "Seville top 5 on the Tuesday:"]
    for r in rows:
        if r["city"] == "Seville":
            out.append(f"- {r['profile']}: " + "; ".join(t.split(':')[0][:40] for t in r["titles"]))
    out += ["", "Sunday 22 Nov (arrival day; the municipal markets are closed): the food-experience enthusiast's top 5,",
            "with each place's state that day:"]
    for x, a in sunday_top(pop, seville, "food-experience enthusiast"):
        out.append(f"- {x.name}: {quality.availability(x, SUNDAY, bp.TODAY)}; practicality {a.practicality.level}")
    seen = {x.category for x in seville}
    out += ["", f"Kinds of place in Seville's ready set: {', '.join(sorted(seen))} ({len(seen)} of 9).",
            "Mean p(Good) by city: " + ", ".join(
                f"{c} {statistics.mean(r['p'] for r in rows if r['city'] == c):.2f}" for c in ("London", "Seville"))]
    Path("benchmarks/synthetic").mkdir(parents=True, exist_ok=True)
    Path("benchmarks/synthetic/profiles_seville.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
