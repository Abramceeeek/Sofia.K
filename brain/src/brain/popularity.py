"""The popularity nudge's reference shares (D113, decisions/plan-variety.md).

How often each card lands in a personal plan, across simulated people who answer the short onboarding (the 6 upfront
places and 5 upfront tasks, D112) and get the usual plan for a brief, as the app makes it (one loved place, D103).
The planner then lowers each card's utility by NUDGE_GAMMA × its share, and keeps the nudged plan only if it loses at
most NUDGE_CAP by the person's own weights (`dayplan.personal_plan`).

The table is fixed per brief type, never learned from the plans served, so no plan depends on who came first.
Regenerate it when the cards, the priors or the upfront questions change (a test checks the population version):

    .venv/bin/python -m brain.popularity --brief ../validation/testb-real/brief.yaml \\
        --generic ../validation/testb-real/generic.yaml --answers <the swipe page's answers CSV>
"""

from __future__ import annotations

import argparse
import collections
import multiprocessing
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

import numpy as np
import yaml

from . import dayplan
from .config import DATA_DIR
from .features import conjoint_plan_features, moment_features
from .moments import Moment, load_moments
from .personal import _F
from .population import PopulationModel, load_population
from .scoring import conjoint_observation, swipe_observation, swipe_vector, update_person
from .travel import LondonEstimate


@dataclass(frozen=True)
class Popularity:
    shares: dict[str, float]        # card id → share of simulated plans holding it
    population_version: str


def load_popularity(path: Path) -> Popularity | None:
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f) or {}
    return Popularity({k: float(v) for k, v in (d.get("shares") or {}).items()}, str(d.get("population_version")))


@dataclass
class Onboarding:
    """What a simulated person is asked before the first plan, and how likely they are to have been to each place."""
    swipe_items: dict[int, Moment]
    swipe_cards: dict[int, tuple[str, list[str]]]
    upfront_places: list[int]
    tasks: dict
    upfront_tasks: list[int]
    p_been: dict[int, float]


def simulate_person(pop: PopulationModel, ob: Onboarding, seed: int):
    """True tastes δ ~ N(0, prior sd); their answers to the upfront places and tasks; the fitted posterior."""
    rng = np.random.default_rng(seed)
    delta = rng.normal(0.0, pop.delta_prior_sd)
    b = pop.b_person(delta)
    cut = np.array(pop.cutpoints["swipe"])
    obs, loved, disliked = [], [], []
    for i in ob.upfront_places:
        if rng.random() > ob.p_been.get(i, 0.75):
            continue
        m = ob.swipe_items[i]
        u = pop.scales["swipe"] * float(swipe_vector(pop, moment_features(m)) @ b) + rng.logistic()
        reaction = ("didnt_enjoy", "fine", "loved")[int(np.searchsorted(cut, u))]
        if (o := swipe_observation(pop, m, reaction)):
            obs.append(o)
        if reaction == "loved":
            loved.append(ob.swipe_cards[i])
        elif reaction == "didnt_enjoy":
            disliked.append(ob.swipe_cards[i])
    for k in ob.upfront_tasks:
        t = ob.tasks[k]
        xa, xb = conjoint_plan_features(t["A"]), conjoint_plan_features(t["B"])
        d = float((pop.vector(xa) - pop.vector(xb)) @ b) * pop.scales["conjoint"]
        obs.append(conjoint_observation(pop, xa, xb, chose_a=rng.random() < _F(d)))
    return delta, update_person(pop, obs), loved, disliked


_CTX: dict = {}


def _plan_cards(seed: int) -> set[str]:
    c = _CTX
    _, post, loved, disliked = simulate_person(c["pop"], c["ob"], seed)
    plan, _, _, _ = dayplan.personal_plan(c["pop"], post, c["moments"], c["brief"], c["travel"],
                                          end_window=c["end_window"], loved=loved, disliked=disliked, familiar=True)
    return {dayplan._base(st.moment_id) for st in plan.stops if not st.moment_id.startswith("lunch@")}


def reference_shares(pop: PopulationModel, ob: Onboarding, moments: list[Moment], brief: dayplan.Brief,
                     travel: LondonEstimate, end_window: tuple[int, int] | None, n: int = 200, seed: int = 20260930,
                     workers: int = 1) -> dict[str, float]:
    _CTX.update(pop=pop, ob=ob, moments=moments, brief=brief, travel=travel, end_window=end_window)
    seeds = [seed + i for i in range(n)]
    if workers > 1:
        with multiprocessing.get_context("fork").Pool(workers) as pool:
            plans = pool.map(_plan_cards, seeds)
    else:
        plans = [_plan_cards(s) for s in seeds]
    count = collections.Counter(c for cards in plans for c in cards)
    return {k: round(v / n, 3) for k, v in sorted(count.items(), key=lambda kv: -kv[1])}


def load_onboarding(data: Path, answers: Path | None) -> Onboarding:
    from .calibration import load_places
    from .swipecal import familiarity, load_answers
    from .testb import load_tasks   # CLI only: testb imports the planner
    with open(data / "onboarding.yaml", encoding="utf-8") as f:
        upfront_tasks = list(yaml.safe_load(f)["conjoint"]["upfront"])
    p_been: dict[int, float] = {}
    if answers:
        places = load_places(data / "calibration" / "places.yaml")
        fam = familiarity(load_answers(answers), places)
        p_been = {p.swipe_item: fam[p.id][0] for p in places if p.swipe_item and p.id in fam}
    return Onboarding(dayplan.load_swipe_items(data / "swipe_items.yaml"),
                      dayplan.load_swipe_cards(data / "swipe_items.yaml"),
                      dayplan.load_app_items(data / "swipe_items.yaml"),
                      load_tasks(data / "conjoint_design.csv"), upfront_tasks, p_been)


def main() -> None:
    from .testb import generic_stops, plan_end   # CLI only
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=str(DATA_DIR))
    ap.add_argument("--brief", required=True, help="the brief the table is for (Test B's)")
    ap.add_argument("--generic", help="the generic plan: personal plans end within 30 min of it (D97)")
    ap.add_argument("--answers", help="the swipe page's answers CSV: each place's own P(been) (m136); else 0.75")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260930)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--time-limit", type=float, default=0.5, help="the planner's time per solve, in seconds")
    ap.add_argument("--out", default=str(DATA_DIR / "popularity.yaml"))
    args = ap.parse_args()
    data = Path(args.data)
    pop = load_population(data / "priors.yaml")
    moments = [m for m in load_moments(data / "moments") if m.status == "ready"]
    brief = replace(dayplan.load_brief(Path(args.brief)), time_limit_s=args.time_limit)
    end_window = None
    if args.generic:
        gen_end = plan_end(generic_stops(Path(args.generic), {m.id: m for m in moments}))
        end_window = (gen_end - 30, gen_end + 30) if gen_end is not None else None
    ob = load_onboarding(data, Path(args.answers) if args.answers else None)
    shares = reference_shares(pop, ob, moments, brief, LondonEstimate(), end_window, n=args.n, seed=args.seed,
                              workers=args.workers)
    head = (f"# D113: each card's share of simulated personal plans, the popularity nudge's reference "
            f"(decisions/plan-variety.md).\n# Written by `python -m brain.popularity` on {date.today():%d %b %Y}: "
            f"{args.n} simulated people, the short onboarding\n# (6 places, 5 tasks), one loved place, "
            f"{'P(been) from the swipe page' if args.answers else 'P(been) 0.75'}. Regenerate when the cards, "
            f"the priors or the upfront questions change.\n")
    body = {"population_version": pop.version, "people": args.n, "seed": args.seed,
            "brief": f"{brief.start_name}, {brief.weekday or 'any day'} {brief.start_time}-{brief.end_time}, "
                     f"{brief.stops} stops" + (", ending near the generic plan" if end_window else ""),
            "shares": shares}
    Path(args.out).write_text(head + yaml.safe_dump(body, sort_keys=False, allow_unicode=True), encoding="utf-8")
    top = list(shares.items())[:6]
    print(f"wrote {args.out}: {len(shares)} cards; most common {top}")


if __name__ == "__main__":
    main()
