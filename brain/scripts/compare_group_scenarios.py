"""m250 (Abram, m244): Nash welfare, least misery and the plain average across nine kinds of group, on London's ready
experiences. SYNTHETIC PEOPLE ONLY (the model's own prior). Members are "Member A", "Member B"…; nothing about anyone
is inferred: a budget, a rejection, a step-free need or the days someone is there is a stated input.

For each scenario and method, over the groups drawn:
- least happy member's satisfaction (mean chance of "Good" over the stops they're there for), and the gap;
- the share of groups where every member gets one of their own top-20% stops (Sato's proportionality);
- hard-rule breaks, which must be 0: a rejected place in the plan, a place a source says isn't step-free when someone
  needs it, a day over the smallest budget that the notes don't say.
For the demanding member: the share of stops from their own top 20%, against the others'.

Run from brain/: `.venv/bin/python scripts/compare_group_scenarios.py [--groups 60]` → benchmarks/synthetic/group_scenarios.txt
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from brain.catalogue import load_catalogue  # noqa: E402
from brain.config import DATA_DIR  # noqa: E402
from brain.discovery import Scorer  # noqa: E402
from brain.group import DELTA, Member, plan  # noqa: E402
from brain.population import load_population  # noqa: E402

SEED = 20261112
METHODS = ("nash", "least_misery", "average")
LABELS = [f"Member {c}" for c in "ABCDEFGHIJ"]


def draw(pop, rng, n, scale=1.0, base=None, noise=None):
    sd = np.asarray(pop.delta_prior_sd, dtype=float)
    if base is not None:
        return [base + rng.normal(0, noise * sd) for _ in range(n)]
    return [rng.normal(0, sd) * scale for _ in range(n)]


def scenarios(pop, cands, rng):
    sd = np.asarray(pop.delta_prior_sd, dtype=float)
    taste = [i for i, k in enumerate(pop.names[:len(sd)]) if k in (
        "movement_views", "food", "green_nature", "history_culture", "iconic", "local_novel", "photo_potential",
        "contrast_reveal", "absorption", "awe", "social_pull")]
    ids = [x.id for x in cands]
    for n in (2, 3, 4, 6, 8, 10):
        yield f"size {n}", [dict(d=d) for d in draw(pop, rng, n)], 2, 3
    yield "very different tastes (4)", [dict(d=d) for d in draw(pop, rng, 4, scale=2.0)], 2, 3
    ds = draw(pop, rng, 4)
    ds[0] = ds[0] * 3
    yield "one demanding member (4)", [dict(d=d, loud=i == 0) for i, d in enumerate(ds)], 2, 3
    b = rng.normal(0, sd)
    yield "similar tastes (4)", [dict(d=d) for d in draw(pop, rng, 4, base=b, noise=0.2)], 2, 3
    yield "conflicting budgets (4: £15, £40, £80, none a day)", [
        dict(d=d, budget=bb) for d, bb in zip(draw(pop, rng, 4), (15.0, 40.0, 80.0, None))], 2, 3
    yield "several rejections each (4 × 6)", [
        dict(d=d, rejects=tuple(rng.choice(ids, 6, replace=False))) for d in draw(pop, rng, 4)], 2, 3
    yield "one member needs step-free access (4)", [
        dict(d=d, step_free=i == 0) for i, d in enumerate(draw(pop, rng, 4))], 2, 3
    yield "one member there on day 1 only (4, 3 days)", [
        dict(d=d, days=(1,) if i == 0 else None) for i, d in enumerate(draw(pop, rng, 4))], 3, 3
    ds = draw(pop, rng, 4)
    ds[0] = ds[0].copy()
    ds[0][taste] = -2.5 * sd[taste]                     # dislikes almost everything this catalogue offers
    yield "one member with no good match (4)", [dict(d=d) for d in ds], 2, 3


def run(groups: int) -> list[str]:
    pop = load_population(DATA_DIR / "priors.yaml")
    cands = [x for x in load_catalogue() if x.status == "ready"]
    rows: dict[tuple[str, str], dict[str, list]] = {}
    for g in range(groups):
        rng = np.random.default_rng([SEED, g])
        for name, specs, days, per_day in scenarios(pop, cands, rng):
            for method in METHODS:
                members = [Member(LABELS[i], Scorer(pop, s["d"]), s.get("budget"), (), tuple(s.get("rejects", ())),
                                  s.get("step_free", False), s.get("days")) for i, s in enumerate(specs)]
                gp = plan(members, cands, days, per_day, method)
                r = rows.setdefault((name, method), {k: [] for k in ("min", "gap", "prop", "breaks", "loud", "others")})
                f = gp.fairness()
                r["min"].append(f["min"])
                r["gap"].append(f["gap"])
                r["prop"].append(all(gp.proportional.values()))
                stops = gp.stops
                rejected = {x for m in members for x in m.rejects}
                breaks = sum(1 for x in stops if x.id in rejected)
                if any(m.needs_step_free for m in members):
                    breaks += sum(1 for x in stops if x.accessibility.step_free.known
                                  and x.accessibility.step_free.value == "no")
                cap = min((m.budget_per_day for m in members if m.budget_per_day is not None), default=None)
                if cap is not None:
                    over = [i for i, d in enumerate(gp.days, 1) if sum(x.price.value.amount for x in d if x.price.known) > cap + 1e-9]
                    breaks += sum(1 for i in over if not any(n.startswith(f"Day {i} costs") for n in gp.notes))
                r["breaks"].append(breaks)
                if any(s.get("loud") for s in specs):
                    k = max(1, round(DELTA * len(cands)))
                    tops = {m.label: {x.id for x in sorted(cands, key=lambda x: -m.scorer.p_good(x))[:k]} for m in members}
                    share = lambda m: sum(1 for x in stops if x.id in tops[m.label]) / len(stops)
                    r["loud"].append(share(members[0]))
                    r["others"].append(statistics.mean(share(m) for m in members[1:]))
    out = ["SYNTHETIC PEOPLE ONLY. Group plans on London's ready experiences: Nash welfare, least misery, plain average.",
           f"{groups} groups per scenario, seed {SEED}; 2 days × 3 stops unless said.", "",
           f"{'scenario':<52}{'method':<14}{'least happy':>12}{'gap':>6}{'everyone a favourite':>22}{'rule breaks':>12}"]
    for (name, method), r in rows.items():
        out.append(f"{name:<52}{method:<14}{statistics.mean(r['min']):>12.3f}{statistics.mean(r['gap']):>6.3f}"
                   f"{statistics.mean(r['prop']):>22.0%}{sum(r['breaks']):>12}")
    out += ["", "One demanding member: share of stops from their own top 20%, against each other member's:"]
    for method in METHODS:
        r = rows[("one demanding member (4)", method)]
        out.append(f"  {method:<14}{statistics.mean(r['loud']):.0%} against {statistics.mean(r['others']):.0%}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--groups", type=int, default=60)
    a = ap.parse_args(argv)
    out = run(a.groups)
    Path("benchmarks/synthetic").mkdir(parents=True, exist_ok=True)
    Path("benchmarks/synthetic/group_scenarios.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
