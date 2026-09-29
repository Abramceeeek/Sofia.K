"""Which swipe places to keep, and what dropping the others costs the model (D110).

Build 1 feedback: too many questions before the first plan. The app cuts the 16 swipe places to about 10.
This module picks the subset and measures the cost.

Choosing the subset (Bayesian optimal design). One swipe on a place with tags x adds expected Fisher
information λ² · E[−∂²ℓ/∂η²] · x xᵀ to the precision of δ_person, where the expectation is over the three
ordered-logit outcomes at the prior (δ = 0). Adding the 10 this-or-that tasks' expected information and the
prior precision gives the expected posterior precision Λ(subset). The subset is chosen to minimise the
average posterior variance of the person's predicted enjoyment over the ready cards,
mean_c x_cᵀ Λ⁻¹ x_c (V-optimality), because that is what the planner uses. Every subset is checked
(16 choose 10 = 8008), subject to each taste tag appearing on at least `min_per_tag` kept places.

Measuring the cost (simulation). People are drawn from the prior, δ ~ N(0, diag(sd²)); they swipe (with a
chance of "haven't been") and make the 10 choices; δ is fitted on 0, the kept, or all 16 swipes. Reported:
the taste weights' posterior sd, the error in δ, and how often the top cards by the fitted weights match the
top cards by the true weights.

    python -m brain.swipeinfo --keep 10
"""

from __future__ import annotations

import argparse
import itertools
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .features import conjoint_plan_features, moment_features
from .moments import MOMENT_TAGS, PLACE_TAGS, Moment, load_moments
from .personal import _F, _f
from .population import PopulationModel, load_population
from .scoring import conjoint_observation, swipe_observation, swipe_vector, update_person

TASTE = PLACE_TAGS + MOMENT_TAGS


def ordered_info(eta: float, cutpoints: tuple[float, ...]) -> float:
    """E[−∂²ℓ/∂η²] for an ordered logit: Σ_k (f(c_k−η) − f(c_{k−1}−η))² / P_k."""
    c = (-math.inf, *cutpoints, math.inf)
    total = 0.0
    for k in range(len(c) - 1):
        p = _F(c[k + 1] - eta) - _F(c[k] - eta)
        d = _f(c[k + 1] - eta) - _f(c[k] - eta)
        if p > 1e-12:
            total += d * d / p
    return total


def _personal_x(pop: PopulationModel, x: np.ndarray) -> np.ndarray:
    """∂η/∂δ at δ = 0: x on linear features, x · b_pop on log-scale ones (D88)."""
    xt = x[pop.personal_idx].copy()
    lm = pop.log_mask
    xt[lm] *= pop.b_pop[pop.personal_idx][lm]
    return xt


def swipe_info(pop: PopulationModel, m: Moment) -> np.ndarray:
    x = swipe_vector(pop, moment_features(m))   # with the person's swiping level (m135)
    lam = pop.scales["swipe"]
    xt = _personal_x(pop, x)
    return lam ** 2 * ordered_info(lam * float(x @ pop.b_pop), pop.cutpoints["swipe"]) * np.outer(xt, xt)


def conjoint_info(pop: PopulationModel, tasks: dict[int, dict[str, dict]]) -> np.ndarray:
    lam = pop.scales["conjoint"]
    info = np.zeros((len(pop.personal_idx),) * 2)
    for t in tasks.values():
        x = pop.vector(conjoint_plan_features(t["A"])) - pop.vector(conjoint_plan_features(t["B"]))
        p = _F(lam * float(x @ pop.b_pop))
        xt = _personal_x(pop, x)
        info += lam ** 2 * p * (1 - p) * np.outer(xt, xt)
    return info


def card_matrix(pop: PopulationModel, cards: list[Moment]) -> np.ndarray:
    """Rows: ∂S/∂δ for each ready card (no weather, no travel)."""
    return np.array([_personal_x(pop, pop.vector(moment_features(m))) for m in cards])


@dataclass
class SubsetScore:
    items: tuple[int, ...]
    v: float          # mean posterior variance of S over the ready cards
    logdet: float     # log det of the expected posterior precision (D-optimality)


PBeen = float | dict[int, float]   # one rate for every place, or each place's own (swipecal.familiarity, m136)


def _p(p_been: PBeen, item: int) -> float:
    return p_been[item] if isinstance(p_been, dict) else p_been


def score_subset(base: np.ndarray, infos: dict[int, np.ndarray], items: tuple[int, ...], C: np.ndarray,
                 p_been: PBeen) -> SubsetScore:
    prec = base + sum((_p(p_been, i) * infos[i] for i in items), np.zeros_like(base))
    cov = np.linalg.inv(prec)
    v = float(np.mean(np.einsum("ij,jk,ik->i", C, cov, C)))
    return SubsetScore(items, v, float(np.linalg.slogdet(prec)[1]))


def covers(items: tuple[int, ...], swipe: dict[int, Moment], min_per_tag: int) -> bool:
    return all(sum(1 for i in items if (swipe[i].tag(t) or 0) >= 1) >= min_per_tag for t in TASTE)


def best_subsets(pop: PopulationModel, swipe: dict[int, Moment], tasks: dict, cards: list[Moment], k: int,
                 p_been: PBeen = 1.0, min_per_tag: int = 2) -> list[SubsetScore]:
    base = np.diag(1.0 / pop.delta_prior_sd ** 2) + conjoint_info(pop, tasks)
    infos = {i: swipe_info(pop, m) for i, m in swipe.items()}
    C = card_matrix(pop, cards)
    out = [score_subset(base, infos, s, C, p_been) for s in itertools.combinations(sorted(swipe), k)
           if covers(s, swipe, min_per_tag)]
    return sorted(out, key=lambda r: r.v)


def choose(ranked: list[SubsetScore], with_cards: set[int], tolerance: float = 0.01) -> SubsetScore:
    """The best subset, except that among those within `tolerance` of the best (relative), the one keeping the
    most places with moment cards wins: a loved place can then be the familiar favourite, and a disliked
    one is never planned (D100)."""
    near = [r for r in ranked if r.v <= ranked[0].v * (1 + tolerance)]
    return max(near, key=lambda r: (len(with_cards & set(r.items)), -r.v))


# ---- simulation -----------------------------------------------------------------------

def simulate(pop: PopulationModel, swipe: dict[int, Moment], tasks: dict, cards: list[Moment],
             sets: dict[str, tuple[int, ...]], n: int = 400, p_been: PBeen = 0.75, top: int = 4,
             seed: int = 7) -> dict[str, dict[str, np.ndarray]]:
    """Per-person results for each swipe set, on the same simulated people (so differences are paired)."""
    rng = np.random.default_rng(seed)
    taste = np.array([pop.personal_names.index(t) for t in TASTE])
    X = np.array([pop.vector(moment_features(m)) for m in cards])
    lam_s = pop.scales["swipe"]
    cut = np.array(pop.cutpoints["swipe"])
    res = {name: {"sd": [], "rmse": [], "hits": [], "regret": []} for name in sets}
    for _ in range(n):
        delta = rng.normal(0.0, pop.delta_prior_sd)
        b = pop.b_person(delta)
        reactions = {}
        for i, m in swipe.items():
            if rng.random() > _p(p_been, i):
                continue
            eta = lam_s * float(swipe_vector(pop, moment_features(m)) @ b)
            u = eta + rng.logistic()
            reactions[i] = ("didnt_enjoy", "fine", "loved")[int(np.searchsorted(cut, u))]
        choices = []
        for t in tasks.values():
            xa, xb = conjoint_plan_features(t["A"]), conjoint_plan_features(t["B"])
            d = float((pop.vector(xa) - pop.vector(xb)) @ b) * pop.scales["conjoint"]
            choices.append(conjoint_observation(pop, xa, xb, chose_a=rng.random() < _F(d)))
        s_true = X @ b
        best = set(np.argsort(-s_true)[:top])
        for name, items in sets.items():
            obs = list(choices)
            obs += [o for i in items if i in reactions if (o := swipe_observation(pop, swipe[i], reactions[i]))]
            post = update_person(pop, obs)
            s_hat = X @ pop.b_person(post.mean)
            pick = np.argsort(-s_hat)[:top]
            r = res[name]
            r["sd"].append(float(np.mean(post.sd()[taste])))
            r["rmse"].append(float(np.sqrt(np.mean((post.mean[taste] - delta[taste]) ** 2))))
            r["hits"].append(len(best & set(pick)) / top)
            r["regret"].append(float(np.mean(np.sort(s_true)[::-1][:top]) - np.mean(s_true[pick])))
    return {name: {k: np.array(v) for k, v in r.items()} for name, r in res.items()}


def main() -> None:
    from .dayplan import load_swipe_cards, load_swipe_items
    from .testb import load_tasks   # CLI only: testb imports the planner

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=str(Path(__file__).resolve().parents[2] / "data"))
    ap.add_argument("--keep", type=int, default=10)
    ap.add_argument("--curve", default="0,6,8,10,12,16", help="set sizes to simulate")
    ap.add_argument("--min-per-tag", type=int, default=2)
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--p-been", type=float, default=0.75)
    ap.add_argument("--answers", help="the swipe page's answers CSV: each place's own P(been) (m136)")
    args = ap.parse_args()
    data = Path(args.data)
    pop = load_population(data / "priors.yaml")
    swipe = load_swipe_items(data / "swipe_items.yaml")
    with_cards = {i for i, (_, c) in load_swipe_cards(data / "swipe_items.yaml").items() if c}
    tasks = load_tasks(data / "conjoint_design.csv")
    cards = [m for m in load_moments(data / "moments") if m.status == "ready"]
    p_been: PBeen = args.p_been
    if args.answers:
        from .calibration import load_places
        from .swipecal import familiarity, load_answers
        fam = familiarity(load_answers(Path(args.answers)), load_places(data / "calibration" / "places.yaml"))
        p_been = {i: fam[i][0] if i in fam else args.p_been for i in swipe}
        print("P(been) by item:", p_been)

    ranked = best_subsets(pop, swipe, tasks, cards, args.keep, p_been=p_been, min_per_tag=args.min_per_tag)
    pick = choose(ranked, with_cards)
    by_d = max(ranked, key=lambda r: r.logdet)
    print(f"{len(cards)} ready cards; {len(ranked)} subsets of {args.keep} pass the tag rule")
    for r in ranked[:5]:
        print(f"  V {r.v:.3f}  logdet {r.logdet:.2f}  keep {r.items}  cards {len(with_cards & set(r.items))}")
    print(f"chosen: {pick.items} (V {pick.v:.3f}, {len(with_cards & set(pick.items))} with cards); "
          f"dropped {sorted(set(swipe) - set(pick.items))}")
    print(f"best by D-optimality: {by_d.items} (V {by_d.v:.3f})")

    sets = {}
    for k in sorted({int(c) for c in args.curve.split(",")} | {args.keep}):
        if k == args.keep:
            sets[k] = pick.items
        elif k >= len(swipe):
            sets[k] = tuple(sorted(swipe))
        else:
            sets[k] = best_subsets(pop, swipe, tasks, cards, k, p_been=p_been, min_per_tag=0)[0].items
        v = best_subsets(pop, swipe, tasks, cards, 0, min_per_tag=0)[0] if k == 0 else None
        print(f"  {k:>2} swipes: {sets[k]}" + (f"  (V {v.v:.3f})" if v else ""))
    res = simulate(pop, swipe, tasks, cards, {str(k): v for k, v in sets.items()}, n=args.n, p_been=p_been)
    full = res[str(max(sets))]
    been = "each place's own P(been)" if isinstance(p_been, dict) else f"P(been) {p_been}"
    print(f"\n{args.n} simulated people, {been}; paired difference against {max(sets)} swipes (± 1 se)")
    for k in sets:
        r = res[str(k)]
        d = r["regret"] - full["regret"]
        h = r["hits"] - full["hits"]
        print(f"  {k:>2} swipes: taste sd {r['sd'].mean():.3f}  δ rmse {r['rmse'].mean():.3f}  "
              f"top-4 hits {r['hits'].mean():.3f} ({h.mean():+.3f} ± {h.std(ddof=1) / np.sqrt(len(h)):.3f})  "
              f"regret {r['regret'].mean():.3f} ({d.mean():+.3f} ± {d.std(ddof=1) / np.sqrt(len(d)):.3f})")


if __name__ == "__main__":
    main()
