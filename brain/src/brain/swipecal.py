"""Calibrating the swipe model from the anonymous swipe page's answers (D70c; m134, m135).

Two things are estimated from the export (answers: browser_id, place_id, answer, day):

1. **The swipe cutpoints and the spread of people's swiping level**, in the Brain's own model:
       y_ij ∈ {didn't enjoy, fine, loved},  η_ij = x_j · (b_population + δ_i) + u_i,
       δ_i ~ N(0, diag(priors' sd²)),  u_i ~ N(0, σ²).
   b_population and the taste priors are held fixed (priors.yaml). The cutpoints c₁ < c₂ and σ are fitted by
   marginal maximum likelihood (type-II ML), integrating each person's (δ_i, u_i) out with the same Laplace
   approximation the Brain uses for δ_person (`personal.fit_delta`). σ becomes the prior sd of `swipe_level`:
   some people love everything, others call everything fine, and without a level of their own that style would
   be read as taste for every tag at once. The level is 0 on every moment, so it never enters a plan's scores.
2. **How many people have been to each place** (familiarity), shrunk toward the pooled rate with a Beta prior
   worth `prior_n` answers, because each place has only a handful of answers. `swipeinfo` uses it to weight
   each swipe's expected information.

    python -m brain.swipecal ../validation/raw/swipe-page/swipe-answers-2026-09-29.csv
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .calibration import TAGS, Place, load_places
from .personal import Observation, _F, fit_delta, log_posterior
from .population import PopulationModel, load_population
from .scoring import SWIPE_LEVEL, swipe_vector

LEVELS = {"didnt": 0, "fine": 1, "loved": 2}


def load_answers(path: Path) -> list[tuple[str, str, str]]:
    with open(path, encoding="utf-8") as f:
        return [(r["browser_id"], r["place_id"], r["answer"]) for r in csv.DictReader(f)]


def place_x(pop: PopulationModel, place: Place) -> np.ndarray:
    """A swipe-page place as a swipe vector, with its tags coded as in the moment records (tag / 2)."""
    return swipe_vector(pop, {t: (place.tags.get(t) or 0) / 2.0 for t in TAGS})


@dataclass(frozen=True)
class CutpointFit:
    cutpoints: tuple[float, float]
    sigma: float                     # prior sd of the person-level swiping level
    se: tuple[float, float, float]   # standard errors of c₁, c₂ and σ (delta method, observed information)
    loglik: float                    # Laplace-approximated marginal log-likelihood
    people: int
    answers: int
    shares: tuple[float, float, float]        # observed didn't / fine / loved
    implied_old: tuple[float, float, float]   # what the old cutpoints implied at the prior


def person_marginal(pop: PopulationModel, xs: list[np.ndarray], ys: list[int], c: tuple[float, float],
                    prior_sd: np.ndarray) -> float:
    """log p(y) ≈ log p(y | δ̂) + log N(δ̂; 0, Σ) + (P/2) log 2π − ½ log|Λ| (Laplace), constants dropped."""
    obs = [Observation(x=x, y=y, scale=pop.scales["swipe"], cutpoints=c) for x, y in zip(xs, ys)]
    post = fit_delta(pop.b_pop, pop.personal_idx, prior_sd, obs, log_mask=pop.log_mask)
    lp = log_posterior(post.mean, pop.b_pop, pop.personal_idx, prior_sd, obs, pop.log_mask)
    return lp - float(np.sum(np.log(prior_sd))) - 0.5 * float(np.linalg.slogdet(post.precision)[1])


def fit_cutpoints(rows: list[tuple[str, str, str]], places: list[Place], pop: PopulationModel,
                  exclude: set[str] = frozenset()) -> CutpointFit:
    if SWIPE_LEVEL not in pop.personal_names:
        raise ValueError("priors.yaml needs the personal swipe_level feature")
    by_id = {p.id: p for p in places}
    per: dict[str, tuple[list, list]] = defaultdict(lambda: ([], []))
    for b, pid, a in rows:
        if b in exclude or a not in LEVELS or pid not in by_id:
            continue
        per[b][0].append(place_x(pop, by_id[pid]))
        per[b][1].append(LEVELS[a])
    people = list(per.values())
    k = pop.personal_names.index(SWIPE_LEVEL)

    def nll(theta: np.ndarray) -> float:   # θ = (c₁, log(c₂ − c₁), log σ)
        c = (float(theta[0]), float(theta[0] + math.exp(theta[1])))
        sd = pop.delta_prior_sd.copy()
        sd[k] = math.exp(theta[2])
        return -sum(person_marginal(pop, xs, ys, c, sd) for xs, ys in people)

    def grad_hess(theta: np.ndarray, h: float = 1e-3) -> tuple[np.ndarray, np.ndarray]:
        n = len(theta)
        g, H = np.zeros(n), np.zeros((n, n))
        f0 = nll(theta)
        for i in range(n):
            ei = np.eye(n)[i] * h
            fp, fm = nll(theta + ei), nll(theta - ei)
            g[i] = (fp - fm) / (2 * h)
            H[i, i] = (fp - 2 * f0 + fm) / h ** 2
            for j in range(i):
                ej = np.eye(n)[j] * h
                H[i, j] = H[j, i] = (nll(theta + ei + ej) - nll(theta + ei - ej) - nll(theta - ei + ej)
                                     + nll(theta - ei - ej)) / (4 * h * h)
        return g, H

    theta = np.array([-2.0, math.log(2.0), 0.0])
    f = nll(theta)
    for _ in range(60):   # damped Newton; gradient steps if the Hessian isn't positive definite
        g, H = grad_hess(theta)
        try:
            np.linalg.cholesky(H)
            step = -np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            step = -g / max(1.0, float(np.abs(g).max()))
        t = 1.0
        while nll(theta + t * step) > f + 1e-10 and t > 1e-6:
            t /= 2
        new = theta + t * step
        f_new = nll(new)
        done = abs(f - f_new) < 1e-7 and float(np.abs(t * step).max()) < 1e-4
        theta, f = new, f_new
        if done:
            break
    _, H = grad_hess(theta)
    cov = np.linalg.inv(H)
    c1, d, s = float(theta[0]), math.exp(theta[1]), math.exp(theta[2])
    J = np.array([[1, 0, 0], [1, d, 0], [0, 0, s]])     # ∂(c₁, c₂, σ)/∂θ
    se = np.sqrt(np.diag(J @ cov @ J.T))

    ys = np.concatenate([np.array(y) for _, y in people])
    etas = np.concatenate([np.array([float(x @ pop.b_pop) for x in xs]) for xs, _ in people])
    old = pop.cutpoints["swipe"]
    p0 = np.array([_F(old[0] - e) for e in etas])
    p1 = np.array([_F(old[1] - e) for e in etas]) - p0
    return CutpointFit((round(c1, 3), round(c1 + d, 3)), round(s, 3), tuple(round(float(x), 3) for x in se),
                       round(-f, 3), len(people), int(len(ys)),
                       tuple(round(float(np.mean(ys == k)), 3) for k in range(3)),
                       (round(float(p0.mean()), 3), round(float(p1.mean()), 3),
                        round(float(1 - p0.mean() - p1.mean()), 3)))


def familiarity(rows: list[tuple[str, str, str]], places: list[Place], prior_n: float = 4.0,
                exclude: set[str] = frozenset()) -> dict[int, tuple[float, int, int]]:
    """P(been) for each locked swipe item: (shrunk estimate, people who have been, people who answered)."""
    item_of = {p.id: p.swipe_item for p in places if p.swipe_item}
    counts: dict[int, Counter] = defaultdict(Counter)
    for b, pid, a in rows:
        if b not in exclude and pid in item_of and a in (*LEVELS, "not_been"):
            counts[item_of[pid]]["been" if a in LEVELS else "not"] += 1
    been = sum(c["been"] for c in counts.values())
    total = sum(c["been"] + c["not"] for c in counts.values())
    pooled = been / total if total else 0.5
    return {i: (round((c["been"] + prior_n * pooled) / (c["been"] + c["not"] + prior_n), 3), c["been"],
                c["been"] + c["not"]) for i, c in sorted(counts.items())}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("answers", help="the swipe page's answers CSV (keep it under validation/raw/)")
    ap.add_argument("--data", default=str(Path(__file__).resolve().parents[2] / "data"))
    args = ap.parse_args()
    data = Path(args.data)
    pop = load_population(data / "priors.yaml")
    places = load_places(data / "calibration" / "places.yaml")
    rows = load_answers(Path(args.answers))
    fit = fit_cutpoints(rows, places, pop)
    print(f"(fitted with the taste priors from priors.yaml {pop.version})")
    print(f"{fit.people} people, {fit.answers} answers where they had been")
    print(f"observed didn't / fine / loved: {fit.shares}; the old cutpoints {tuple(pop.cutpoints['swipe'])} "
          f"implied {fit.implied_old}")
    print(f"fitted cutpoints {fit.cutpoints} (se {fit.se[0]}, {fit.se[1]}); swiping-level sd σ = {fit.sigma} "
          f"(se {fit.se[2]}); log-likelihood {fit.loglik}")
    names = {p.swipe_item: p.name for p in places if p.swipe_item}
    for i, (p, b, n) in familiarity(rows, places).items():
        print(f"  item {i:>2}  {names[i]:<45} been {b:>2}/{n:<2}  P(been) {p}")


if __name__ == "__main__":
    main()
