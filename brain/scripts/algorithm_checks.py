"""Checks behind decisions/algorithm-review-synthesis.md (20 Oct 2026): the five AI reviews' testable claims, measured
on the real model and planner rather than argued.

Run from brain/ with the venv: `.venv/bin/python scripts/algorithm_checks.py [--n 120] [--workers 4]`.

Everything below is **inside the model's own world**: simulated people whose true tastes are drawn from the same
priors the model assumes (popularity.simulate_person, as for the variety nudge, D113). It says how much the model can
learn from the short onboarding *if its assumptions were right*. It cannot say whether they are right: only real
ratings can (Test B and after).

1. Test B's pass rule: exact binomial odds.
2. The cost weight behind "worth about £V": how wide its uncertainty is before and after the onboarding.
3. Learning: does the posterior recover each simulated person's true weights (correlation, by weight)?
4. Plans: on each person's true tastes, the personal plan vs the no-answers plan vs the best possible plan; and the
   implied chance of preferring the personal plan over the no-answers plan.
5. The "at least Good" floor: how many candidate cards it removes.
6. Sensitivity: refit with every prior sd ×0.5 and ×1.5; how many of the 3–4 stops change.
7. Repetition: plans with two history-and-culture stops in a row, or three or more in all.
"""

from __future__ import annotations

import argparse
import math
import multiprocessing
from dataclasses import replace
from pathlib import Path

import numpy as np

from brain import dayplan
from brain.config import DATA_DIR
from brain.features import moment_features
from brain.moments import load_moments
from brain.personal import DeltaPosterior, prior_only
from brain.population import load_population
from brain.popularity import load_onboarding, simulate_person
from brain.scoring import score, update_person
from brain.testb import generic_stops, plan_end
from brain.travel import LondonEstimate

_C: dict = {}


def p_at_least(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p), exactly."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def testers_needed(p_true: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """The smallest n where an exact one-sided test at alpha (null 0.5) passes with the given power."""
    for n in range(5, 400):
        k = next(k for k in range(n + 1) if p_at_least(k, n, 0.5) <= alpha)
        if p_at_least(k, n, p_true) >= power:
            return n
    return -1


def _scaled(pop, k: float):
    return replace(pop, features=tuple(replace(f, delta_sd=f.delta_sd * k) for f in pop.features))


def _plan(pop, post: DeltaPosterior, loved, disliked):
    c = _C
    plan, _, _, _ = dayplan.personal_plan(pop, post, c["moments"], c["brief"], c["travel"], end_window=c["end_window"],
                                          loved=loved, disliked=disliked, familiar=False)
    return [st for st in plan.stops if not st.moment_id.startswith("lunch@")]


def _true_value(stops, b) -> float:
    """The day on the person's true tastes: each stop's utility with its own leg (as a rating would see it)."""
    by_id, pop = _C["by_id"], _C["pop"]
    return sum(score(pop.vector(moment_features(by_id[dayplan._base(s.moment_id)], None, s.travel_min)), b)
               for s in stops)


def _one(seed: int) -> dict:
    c = _C
    pop = c["pop"]
    delta, post, loved, disliked = simulate_person(pop, c["ob"], seed)
    b = pop.b_person(delta)
    oracle = DeltaPosterior(delta, np.diag(np.full(len(delta), 1e6)), 0, 0)
    personal = _plan(pop, post, loved, disliked)
    nothing = _plan(pop, prior_only(pop.delta_prior_sd), [], [])
    best = _plan(pop, oracle, loved, disliked)
    ids = lambda st: {dayplan._base(s.moment_id) for s in st}
    # 5: the floor, on the person's fitted weights
    floor = pop.cutpoints["rating"][1]
    bp = pop.b_person(post.mean)
    below = sum(score(pop.vector(moment_features(m)), bp) <= floor for m in c["moments"])
    # 6: refit the same answers with every prior sd halved, then ×1.5
    obs = c["obs_of"](seed)
    changed = {}
    for k in (0.5, 1.5):
        pk = _scaled(pop, k)
        changed[k] = len(ids(personal) - ids(_plan(pk, update_person(pk, obs), loved, disliked)))
    # 7: history and culture in a row
    hist = [moment_features(c["by_id"][dayplan._base(s.moment_id)]).get("history_culture", 0) >= 1 for s in personal]
    return {"delta": delta, "mean": post.mean, "sd": post.sd(), "personal": _true_value(personal, b),
            "nothing": _true_value(nothing, b), "best": _true_value(best, b),
            "shared_with_nothing": len(ids(personal) & ids(nothing)), "n_stops": len(personal),
            "below_floor": int(below), "changed": changed,
            "hist_in_a_row": any(a and b2 for a, b2 in zip(hist, hist[1:])), "hist_3plus": sum(hist) >= 3}


def _observations(seed: int):
    """The same answers simulate_person gives for this seed, as observations (for the refits in check 6)."""
    from brain import scoring
    captured = []
    real = scoring.update_person

    def grab(pop, obs):
        captured.append(obs)
        return real(pop, obs)
    import brain.popularity as popm
    popm.update_person, saved = grab, popm.update_person
    try:
        simulate_person(_C["pop"], _C["ob"], seed)
    finally:
        popm.update_person = saved
    return captured[0]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--time-limit", type=float, default=0.5)
    args = ap.parse_args()

    print("1. Test B: 10 testers, pass = at least 7 prefer the personal plan")
    print(f"   by chance alone (p = 0.5): P(>=7) = {p_at_least(7, 10, 0.5):.3f}; P(>=8) = {p_at_least(8, 10, 0.5):.4f}")
    for p in (0.6, 0.7, 0.8):
        print(f"   if {p:.0%} truly prefer it: P(pass) = {p_at_least(7, 10, p):.2f}")
    for p in (0.7, 0.8):
        print(f"   testers for an exact one-sided test at 5%, 80% power, true rate {p:.0%}: {testers_needed(p)}")

    pop = load_population(DATA_DIR / "priors.yaml")
    i_cost = pop.personal_names.index("cost_per_10gbp")
    sd0 = pop.delta_prior_sd[i_cost]
    print(f"\n2. Cost weight = -0.25 x e^delta, delta ~ N(0, {sd0}^2): before any answer, the 95% range of e^delta is "
          f"{math.exp(-1.96 * sd0):.2f} to {math.exp(1.96 * sd0):.2f} (x{math.exp(3.92 * sd0):.0f}); "
          f"'worth about £V' scales with 1/e^delta")

    moments = [m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"]
    brief = replace(dayplan.load_brief(DATA_DIR / "testb" / "brief.yaml"), time_limit_s=args.time_limit)
    gen_end = plan_end(generic_stops(DATA_DIR / "testb" / "generic.yaml", {m.id: m for m in moments}))
    _C.update(pop=pop, ob=load_onboarding(DATA_DIR, None), moments=moments, by_id={m.id: m for m in moments},
              brief=brief, travel=LondonEstimate(), obs_of=_observations,
              end_window=(gen_end - 30, gen_end + 30) if gen_end is not None else None)
    seeds = [20261020 + i for i in range(args.n)]
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        rows = pool.map(_one, seeds)

    sds = np.array([r["sd"][i_cost] for r in rows])
    print(f"   after the short onboarding ({args.n} simulated people): cost sd median {np.median(sds):.2f} "
          f"(10th-90th percentile {np.percentile(sds, 10):.2f}-{np.percentile(sds, 90):.2f}) "
          f"-> 95% range x{math.exp(3.92 * np.median(sds)):.0f}")

    print("\n3. Learning: correlation between each simulated person's true weight and the fitted one")
    D, M = np.array([r["delta"] for r in rows]), np.array([r["mean"] for r in rows])
    cors = []
    for j, name in enumerate(pop.personal_names):
        r = float(np.corrcoef(D[:, j], M[:, j])[0, 1]) if M[:, j].std() > 1e-9 else 0.0
        cors.append((r, name))
    cors.sort(reverse=True)
    print("   " + "; ".join(f"{n} {r:.2f}" for r, n in cors))
    print(f"   weights learned at all (r > 0.3): {sum(r > 0.3 for r, _ in cors)} of {len(cors)}")

    P, N0, B = (np.array([r[k] for r in rows]) for k in ("personal", "nothing", "best"))
    gain = B - N0
    share = np.where(gain > 1e-6, (P - N0) / np.where(gain > 1e-6, gain, 1), np.nan)
    pref = 1 / (1 + np.exp(-(P - N0)))
    print("\n4. Plans on each person's true tastes (sum over the stops, utility units)")
    print(f"   personal {P.mean():.2f}, no answers {N0.mean():.2f}, best possible {B.mean():.2f}")
    print(f"   share of the possible gain the personal plan gets: median {np.nanmedian(share):.0%}")
    print(f"   personal at least as good as no answers: {np.mean(P >= N0 - 1e-9):.0%} of people")
    print(f"   stops shared with the no-answers plan: mean {np.mean([r['shared_with_nothing'] for r in rows]):.1f} "
          f"of {np.mean([r['n_stops'] for r in rows]):.1f}")
    print(f"   implied P(prefer personal over no-answers), logistic on the difference (GUESS scale 1): "
          f"mean {pref.mean():.2f}; P(>=7 of 10) at that rate {p_at_least(7, 10, pref.mean()):.2f}")

    below = np.array([r["below_floor"] for r in rows])
    floor = pop.cutpoints["rating"][1]
    none_below = sum(score(pop.vector(moment_features(m)), pop.b_pop) <= floor for m in moments)
    print(f"\n5. 'At least Good' floor (u > {floor}): cards below it, of {len(moments)}: with no answers {none_below}; "
          f"after onboarding median {np.median(below):.0f} (range {below.min()}-{below.max()})")
    ns = np.array([r["n_stops"] for r in rows])
    print(f"   places in the personal plan (lunch aside): " +
          ", ".join(f"{k}: {np.mean(ns == k):.0%}" for k in sorted(set(ns.tolist()))))

    print("\n6. Refit the same answers with every prior sd x0.5 / x1.5: stops that change")
    for k in (0.5, 1.5):
        ch = np.array([r["changed"][k] for r in rows])
        print(f"   x{k}: mean {ch.mean():.2f}; plans with any change {np.mean(ch > 0):.0%}; 2+ changes {np.mean(ch >= 2):.0%}")

    print(f"\n7. Personal plans with two history-and-culture stops in a row: {np.mean([r['hist_in_a_row'] for r in rows]):.0%}; "
          f"three or more in all: {np.mean([r['hist_3plus'] for r in rows]):.0%}")


if __name__ == "__main__":
    main()
