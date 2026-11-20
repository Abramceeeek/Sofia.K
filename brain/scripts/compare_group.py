"""m240: how three ways of planning for a group treat its members. SYNTHETIC PEOPLE ONLY (drawn from the model's own
prior), on London's 49 checked experiences, 2 days of 3 stops.

Run from brain/: `.venv/bin/python scripts/compare_group.py [--groups 200]`

For each group of 3, each method plans the trip (group.plan). Reported per method:
- the least happy member's satisfaction (their mean chance of "Good" or better over the plan), on average;
- the gap between the happiest and the least happy member;
- how often every member gets at least one stop from their own top 20% (Sato's proportionality, m = 1);
- in the "intense" variant, where one member's tastes are three times as strong as drawn: the share of the plan's stops
  that are among that member's own top 20%, against the other members' share. A fair method doesn't let them take
  the trip just because their preferences are louder.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from brain.catalogue import load_catalogue  # noqa: E402
from brain.config import DATA_DIR  # noqa: E402
from brain.discovery import Scorer  # noqa: E402
from brain.group import DELTA, Member, plan  # noqa: E402
from brain.population import load_population  # noqa: E402

SEED = 20261110
METHODS = ("average", "least_misery", "nash")


def run(groups: int, intense: bool) -> dict[str, dict[str, float]]:
    pop = load_population(DATA_DIR / "priors.yaml")
    cands = list(load_catalogue())
    sd = np.asarray(pop.delta_prior_sd, dtype=float)
    out = {m: {"min": [], "gap": [], "prop": [], "loud": [], "quiet": []} for m in METHODS}
    for g in range(groups):
        rng = np.random.default_rng([SEED, g])
        deltas = [rng.normal(0.0, sd) for _ in range(3)]
        if intense:
            deltas[0] = deltas[0] * 3.0
        members = [Member(f"Member {'ABC'[i]}", Scorer(pop, d)) for i, d in enumerate(deltas)]
        k = max(1, round(DELTA * len(cands)))
        tops = {m.label: set(x.id for x in sorted(cands, key=lambda x: -m.scorer.p_good(x))[:k]) for m in members}
        for method in METHODS:
            p = plan(members, cands, days=2, per_day=3, method=method)
            f = p.fairness()
            r = out[method]
            r["min"].append(f["min"])
            r["gap"].append(f["gap"])
            r["prop"].append(f["proportional_share"] == 1.0)
            ids = {x.id for x in p.stops}
            r["loud"].append(len(ids & tops["Member A"]) / len(ids))
            r["quiet"].append(np.mean([len(ids & tops[m.label]) / len(ids) for m in members[1:]]))
    return {m: {k: float(np.mean(v)) for k, v in r.items()} for m, r in out.items()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--groups", type=int, default=200)
    ap.add_argument("--out", type=Path, default=Path("benchmarks/synthetic/group.txt"))
    args = ap.parse_args(argv)
    lines = ["SYNTHETIC GROUPS ONLY (the model's own prior), London's 49 checked experiences, 2 days x 3 stops,",
             f"{args.groups} groups of 3, seed {SEED}. Satisfaction = a member's mean chance of 'Good' or better.", ""]
    for intense in (False, True):
        lines.append("One member's tastes x3 ('intense'):" if intense else "Members as drawn:")
        lines.append(f"{'method':<14} | {'least happy':>11} | {'gap':>6} | {'all get a top-20% stop':>22} | "
                     f"{'loud member top-20% share':>25} | {'others':>6}")
        for m, r in run(args.groups, intense).items():
            lines.append(f"{m:<14} | {r['min']:>11.3f} | {r['gap']:>6.3f} | {r['prop']:>22.2f} | {r['loud']:>25.2f} | "
                         f"{r['quiet']:>6.2f}")
        lines.append("")
    print("\n".join(lines))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
