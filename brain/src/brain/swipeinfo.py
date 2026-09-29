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
    python -m brain.swipeinfo --answers <swipe page CSV> --candidates all    # D111: the final 10 from all 30

With `--candidates all` (D111) there are too many subsets to check each one (30 choose 10 is about 30 million), so the
choice is a search: a greedy start plus random starts, each improved by single swaps until none helps (a Fedorov-type
exchange). On the locked 16 it finds the same best subset as checking every one (a test checks).
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


_GH = np.polynomial.hermite.hermgauss(20)


def _prior_average(f, mean: float, sd: float) -> float:
    """E[f(η)] for η ~ N(mean, sd²), by Gauss-Hermite quadrature."""
    nodes, weights = _GH
    return float(sum(w * f(mean + math.sqrt(2.0) * sd * z) for z, w in zip(nodes, weights)) / math.sqrt(math.pi))


def _eta_prior(pop: PopulationModel, x: np.ndarray, lam: float) -> tuple[float, float]:
    """Mean and sd of λ x·(b_pop + δ) over people, δ ~ the prior (linearised on log-scale weights)."""
    xt = _personal_x(pop, x)
    return lam * float(x @ pop.b_pop), lam * float(np.sqrt(np.sum((xt * pop.delta_prior_sd) ** 2)))


def swipe_info(pop: PopulationModel, m: Moment) -> np.ndarray:
    """Expected Fisher information of one swipe, averaged over people drawn from the prior (pseudo-Bayesian
    design, D111). At δ = 0 alone it misleads: with the fitted cutpoints most answers are "loved", and how much a
    swipe tells us depends on where a person's η falls against the cutpoints."""
    x = swipe_vector(pop, moment_features(m))   # with the person's swiping level (m135)
    lam = pop.scales["swipe"]
    xt = _personal_x(pop, x)
    mean, sd = _eta_prior(pop, x, lam)
    return lam ** 2 * _prior_average(lambda e: ordered_info(e, pop.cutpoints["swipe"]), mean, sd) * np.outer(xt, xt)


def task_info(pop: PopulationModel, task: dict[str, dict]) -> np.ndarray:
    """Expected information of one "this or that" task, averaged over the prior like `swipe_info`."""
    lam = pop.scales["conjoint"]
    x = pop.vector(conjoint_plan_features(task["A"])) - pop.vector(conjoint_plan_features(task["B"]))
    mean, sd = _eta_prior(pop, x, lam)
    xt = _personal_x(pop, x)
    return lam ** 2 * _prior_average(lambda e: _F(e) * (1 - _F(e)), mean, sd) * np.outer(xt, xt)


def conjoint_info(pop: PopulationModel, tasks: dict[int, dict[str, dict]]) -> np.ndarray:
    return sum((task_info(pop, t) for t in tasks.values()), np.zeros((len(pop.personal_idx),) * 2))


def card_matrix(pop: PopulationModel, cards: list[Moment]) -> np.ndarray:
    """Rows: ∂S/∂δ for each ready card (no weather, no travel)."""
    return np.array([_personal_x(pop, pop.vector(moment_features(m))) for m in cards])


@dataclass
class SubsetScore:
    items: tuple
    v: float          # mean posterior variance of S over the ready cards
    logdet: float     # log det of the expected posterior precision (D-optimality)
    regret: float | None = None   # preposterior expected regret of a 4-stop pick (D111), when asked for


class ExpectedRegret:
    """The utility a person is expected to lose because we pick their top cards from estimated weights (D111).

    Preposterior analysis in the Gaussian approximation: with prior δ ~ N(0, Σ₀) and posterior covariance Σ (from
    the expected information), the estimate is δ̂ ~ N(0, Σ₀ − Σ) and the truth is δ | δ̂ ~ N(δ̂, Σ). Each draw
    picks the `top` cards with the highest estimated S and scores them with the true S, against the true best
    `top`. Common random numbers make subsets comparable. This is what a plan cares about: the average variance
    over all cards (`v`) can favour sets that sharpen cards nobody would be planned."""

    def __init__(self, pop: PopulationModel, cards: list[Moment], n_draws: int = 3000, top: int = 4, seed: int = 11):
        rng = np.random.default_rng(seed)
        P = len(pop.personal_idx)
        self.C = card_matrix(pop, cards)
        self.s0 = np.array([float(pop.vector(moment_features(m)) @ pop.b_pop) for m in cards])
        self.prior = np.diag(pop.delta_prior_sd ** 2)
        self.Z1, self.Z2 = rng.standard_normal((n_draws, P)), rng.standard_normal((n_draws, P))
        self.top = top

    @staticmethod
    def _sqrt(S: np.ndarray) -> np.ndarray:
        w, V = np.linalg.eigh((S + S.T) / 2)
        return V * np.sqrt(np.clip(w, 0.0, None))

    def __call__(self, prec: np.ndarray) -> float:
        post = np.linalg.inv(prec)
        d_hat = self.Z1 @ self._sqrt(self.prior - post).T
        d_true = d_hat + self.Z2 @ self._sqrt(post).T
        s_hat, s_true = self.s0 + d_hat @ self.C.T, self.s0 + d_true @ self.C.T
        k = self.top
        pick = np.argpartition(-s_hat, k, axis=1)[:, :k]
        best = -np.partition(-s_true, k, axis=1)[:, :k]
        return float(np.mean(best.mean(axis=1) - np.take_along_axis(s_true, pick, axis=1).mean(axis=1)))


PBeen = float | dict   # one rate for every place, or each place's own (swipecal.familiarity, m136)


def _p(p_been: PBeen, item) -> float:
    return p_been[item] if isinstance(p_been, dict) else p_been


def score_subset(base: np.ndarray, infos: dict, items: tuple, C: np.ndarray, p_been: PBeen,
                 regret: ExpectedRegret | None = None) -> SubsetScore:
    prec = base + sum((_p(p_been, i) * infos[i] for i in items), np.zeros_like(base))
    cov = np.linalg.inv(prec)
    v = float(np.mean(np.einsum("ij,jk,ik->i", C, cov, C)))
    return SubsetScore(items, v, float(np.linalg.slogdet(prec)[1]), regret(prec) if regret else None)


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


def search_subsets(pop: PopulationModel, cands: dict, tasks: dict, cards: list[Moment], k: int,
                   p_been: PBeen = 1.0, min_per_tag: int = 2, with_cards: set = frozenset(),
                   tolerance: float = 0.01, restarts: int = 25, seed: int = 0,
                   regret: ExpectedRegret | None = None) -> tuple[SubsetScore, SubsetScore]:
    """(best subset, chosen subset) by exchange search, for candidate sets too big to check every subset (D111).

    The criterion is V, or the expected regret when `regret` is given. The chosen subset applies `choose`'s rule
    by single swaps: while a swap keeps the criterion within `tolerance` of the best and keeps more places with
    moment cards, take it."""
    base = np.diag(1.0 / pop.delta_prior_sd ** 2) + conjoint_info(pop, tasks)
    infos = {i: swipe_info(pop, m) for i, m in cands.items()}
    C = card_matrix(pop, cards)
    keys = sorted(cands)
    crit = (lambda s: s.regret) if regret else (lambda s: s.v)

    def shortfall(items) -> int:
        return sum(max(0, min_per_tag - sum(1 for i in items if (cands[i].tag(t) or 0) >= 1)) for t in TASTE)

    def score(items) -> tuple[SubsetScore, float]:
        s = score_subset(base, infos, tuple(sorted(items)), C, p_been, regret)
        return s, crit(s) + 10.0 * shortfall(items)   # the tag rule as a penalty, so a search can pass through gaps

    def improve(cur: list) -> tuple[list, float, SubsetScore]:
        cur_s, cur_f = score(cur)
        while True:
            move = None
            for i in cur:
                for j in keys:
                    if j in cur:
                        continue
                    trial = [x for x in cur if x != i] + [j]
                    s, f = score(trial)
                    if f < cur_f - 1e-12 and (move is None or f < move[1]):
                        move = (trial, f, s)
            if move is None:
                return cur, cur_f, cur_s
            cur, cur_f, cur_s = move

    rng = np.random.default_rng(seed)
    best = None
    for r in range(restarts):
        if r == 0:   # greedy start
            cur: list = []
            while len(cur) < k:
                cur.append(min((j for j in keys if j not in cur), key=lambda j: score(cur + [j])[1]))
        else:
            cur = [keys[i] for i in rng.choice(len(keys), size=k, replace=False)]
        cur, f, s = improve(cur)
        if shortfall(cur) == 0 and (best is None or f < best[1]):
            best = (sorted(cur), f, s)
    if best is None:
        raise ValueError(f"no subset of {k} covers every taste tag {min_per_tag} times")
    chosen, chosen_s = list(best[0]), best[2]
    while True:   # the moment-cards tie-break, by single swaps within the tolerance
        n_cards = len(with_cards & set(chosen))
        options = []
        for i in chosen:
            for j in keys:
                if j in chosen or j not in with_cards or i in with_cards:
                    continue
                trial = [x for x in chosen if x != i] + [j]
                s, _ = score(trial)
                if shortfall(trial) == 0 and crit(s) <= crit(best[2]) * (1 + tolerance):
                    options.append((crit(s), trial, s))
        if not options:
            break
        _, chosen, chosen_s = min(options, key=lambda o: o[0])
        assert len(with_cards & set(chosen)) > n_cards
    return best[2], chosen_s


def select_upfront(pop: PopulationModel, places: dict, tasks: dict, cards: list[Moment], n_places: int,
                   n_tasks: int, p_been: PBeen, regret: ExpectedRegret, min_per_tag: int = 1,
                   rounds: int = 6) -> tuple[tuple, tuple, float]:
    """The places and "this or that" tasks to ask before the first plan (D112), chosen together.

    Coordinate descent on the expected regret: the best tasks given the places (every subset), then the best places
    given the tasks (every subset, each taste tag on at least `min_per_tag` of them), until neither changes. Every
    start (the best places alone, and each single-task start) is tried and the best end point kept."""
    prior = np.diag(1.0 / pop.delta_prior_sd ** 2)
    s_info = {i: _p(p_been, i) * swipe_info(pop, m) for i, m in places.items()}
    t_info = {k: task_info(pop, t) for k, t in tasks.items()}
    ok = [c for c in itertools.combinations(sorted(places), n_places)
          if all(sum(1 for i in c if (places[i].tag(t) or 0) >= 1) >= min_per_tag for t in TASTE)]

    def value(ps, ts) -> float:
        return regret(prior + sum((s_info[i] for i in ps), np.zeros_like(prior))
                      + sum((t_info[k] for k in ts), np.zeros_like(prior)))

    best = None
    starts = [tuple(sorted(tasks))[:n_tasks]] + [tuple(c) for c in itertools.combinations(sorted(tasks), n_tasks)][::25]
    for ts in starts:
        ps = min(ok, key=lambda c: value(c, ts))
        for _ in range(rounds):
            new_ts = min(itertools.combinations(sorted(tasks), n_tasks), key=lambda c: value(ps, c))
            new_ps = min(ok, key=lambda c: value(c, new_ts))
            if new_ts == ts and new_ps == ps:
                break
            ps, ts = new_ps, new_ts
        v = value(ps, ts)
        if best is None or v < best[2]:
            best = (ps, ts, v)
    return best


def choose(ranked: list[SubsetScore], with_cards: set[int], tolerance: float = 0.01) -> SubsetScore:
    """The best subset, except that among those within `tolerance` of the best (relative), the one keeping the
    most places with moment cards wins: a loved place can then be the familiar favourite, and a disliked
    one is never planned (D100)."""
    near = [r for r in ranked if r.v <= ranked[0].v * (1 + tolerance)]
    return max(near, key=lambda r: (len(with_cards & set(r.items)), -r.v))


# ---- simulation -----------------------------------------------------------------------

def simulate(pop: PopulationModel, swipe: dict[int, Moment], tasks: dict, cards: list[Moment],
             sets: dict[str, tuple], n: int = 400, p_been: PBeen = 0.75, top: int = 4,
             seed: int = 7, task_sets: dict[str, tuple] | None = None) -> dict[str, dict[str, np.ndarray]]:
    """Per-person results for each swipe set, on the same simulated people (so differences are paired).
    `task_sets` gives the "this or that" tasks for a set (default: all of them)."""
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
        choices = {}
        for k, t in tasks.items():
            xa, xb = conjoint_plan_features(t["A"]), conjoint_plan_features(t["B"])
            d = float((pop.vector(xa) - pop.vector(xb)) @ b) * pop.scales["conjoint"]
            choices[k] = conjoint_observation(pop, xa, xb, chose_a=rng.random() < _F(d))
        s_true = X @ b
        best = set(np.argsort(-s_true)[:top])
        for name, items in sets.items():
            obs = [choices[k] for k in (task_sets or {}).get(name, tuple(tasks))]
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


def place_moment(place) -> Moment:
    """A swipe-page candidate (calibration.Place) as a moment with the same tags, for scoring its swipes."""
    return Moment.model_validate({
        "id": place.id, "title": place.name, "place": {"name": place.name}, "source": "swipe-candidate",
        "features": {"place": {t: place.tags.get(t, 0) for t in PLACE_TAGS},
                     "moment": {t: place.tags.get(t, 0) for t in MOMENT_TAGS}}})


def item_stanza(place, number: int) -> str:
    """A swipe_items.yaml entry for a new candidate that makes the final 10 (D111). Its tags are Claude's draft."""
    pt = ", ".join(f"{t}: {place.tags.get(t, 0)}" for t in PLACE_TAGS)
    mt = ", ".join(f"{t}: {place.tags.get(t, 0)}" for t in MOMENT_TAGS)
    return (f"  {number}:\n    name: \"{place.name}\"\n    cards: [{', '.join(place.cards)}]\n"
            f"    place: {{{pt}}}\n    moment: {{{mt}}}")


def main() -> None:
    from .calibration import load_places
    from .dayplan import load_app_items, load_swipe_cards, load_swipe_items   # noqa: F811
    from .swipecal import familiarity, load_answers
    from .testb import load_tasks   # CLI only: testb imports the planner

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=str(Path(__file__).resolve().parents[2] / "data"))
    ap.add_argument("--keep", type=int, default=10)
    ap.add_argument("--curve", default="0,6,8,10,12,16", help="set sizes to simulate (locked 16 only)")
    ap.add_argument("--min-per-tag", type=int, default=2)
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--p-been", type=float, default=0.75)
    ap.add_argument("--answers", help="the swipe page's answers CSV: each place's own P(been) (m136)")
    ap.add_argument("--candidates", choices=("locked", "all"), default="locked",
                    help="choose from the locked 16, or from all 30 swipe-page candidates (D111)")
    ap.add_argument("--upfront", help="places,tasks to ask before the first plan, chosen from the app's places "
                                      "and all tasks, e.g. 6,5 (D112)")
    args = ap.parse_args()
    data = Path(args.data)
    pop = load_population(data / "priors.yaml")
    swipe = load_swipe_items(data / "swipe_items.yaml")
    locked_cards = load_swipe_cards(data / "swipe_items.yaml")
    tasks = load_tasks(data / "conjoint_design.csv")
    cards = [m for m in load_moments(data / "moments") if m.status == "ready"]
    places = load_places(data / "calibration" / "places.yaml")
    fam = familiarity(load_answers(Path(args.answers)), places) if args.answers else {}

    if args.candidates == "all":
        cands = {p.id: place_moment(p) for p in places}
        by_id = {p.id: p for p in places}
        with_cards = {p.id for p in places if p.cards or (p.swipe_item and locked_cards[p.swipe_item][1])}
        p_been: PBeen = {pid: fam[pid][0] if pid in fam else args.p_been for pid in cands}
        current = sorted(p.id for p in places if p.swipe_item in set(load_app_items(data / "swipe_items.yaml")))
        regret = ExpectedRegret(pop, cards)
        best, chosen = search_subsets(pop, cands, tasks, cards, args.keep, p_been=p_been,
                                      min_per_tag=args.min_per_tag, with_cards=with_cards, regret=regret)
        base = np.diag(1.0 / pop.delta_prior_sd ** 2) + conjoint_info(pop, tasks)
        infos = {i: swipe_info(pop, m) for i, m in cands.items()}
        C = card_matrix(pop, cards)
        cur_s = score_subset(base, infos, tuple(current), C, p_been, regret)
        people = max((n for _, _, n in fam.values()), default=0)
        print(f"{len(cards)} ready cards; {len(cands)} candidates; familiarity from {people} people")
        print(f"expected regret (V): best {best.regret:.3f} ({best.v:.3f}); chosen, moment-cards rule "
              f"{chosen.regret:.3f} ({chosen.v:.3f}); the app's current 10 {cur_s.regret:.3f} ({cur_s.v:.3f})")
        for pid in chosen.items:
            p = by_id[pid]
            f = fam.get(pid)
            print(f"  {('item ' + str(p.swipe_item)) if p.swipe_item else 'NEW':>7}  {p.name:<50} "
                  f"P(been) {p_been[pid]:.2f}{f' ({f[1]}/{f[2]})' if f else ''}  {'cards' if pid in with_cards else ''}")
        print("out:", ", ".join(by_id[x].name for x in current if x not in chosen.items) or "none")
        new = [by_id[x] for x in chosen.items if not by_id[x].swipe_item]
        if new:
            print("\nAdd to swipe_items.yaml (tags are Claude's draft: Abram checks them), then set app_items:")
            for n, p in enumerate(new, start=max(swipe) + 1):
                print(item_stanza(p, n))
        sets = {"0 swipes": (), "current 10": tuple(current), "chosen 10": tuple(chosen.items),
                "all 30": tuple(sorted(cands))}
        res = simulate(pop, cands, tasks, cards, sets, n=args.n, p_been=p_been)
        full = res["all 30"]
        print(f"\n{args.n} simulated people; paired difference against all 30 swipes (± 1 se)")
        for name, r in res.items():
            d = r["regret"] - full["regret"]
            print(f"  {name:>10}: top-4 hits {r['hits'].mean():.3f}  regret {r['regret'].mean():.3f} "
                  f"({d.mean():+.3f} ± {d.std(ddof=1) / np.sqrt(len(d)):.3f})")
        return

    with_cards = {i for i, (_, c) in locked_cards.items() if c}
    item_of = {p.id: p.swipe_item for p in places if p.swipe_item}
    p_been = args.p_been
    if fam:
        by_item = {item_of[pid]: v[0] for pid, v in fam.items() if pid in item_of}
        p_been = {i: by_item.get(i, args.p_been) for i in swipe}
        print("P(been) by item:", p_been)

    if args.upfront:
        n_places, n_tasks = (int(x) for x in args.upfront.split(","))
        app = load_app_items(data / "swipe_items.yaml")
        regret = ExpectedRegret(pop, cards, n_draws=1500)
        ps, ts, v = select_upfront(pop, {i: swipe[i] for i in app}, tasks, cards, n_places, n_tasks, p_been, regret)
        print(f"upfront places {ps}, later {tuple(i for i in app if i not in ps)}")
        print(f"upfront tasks {ts}, later {tuple(k for k in sorted(tasks) if k not in ts)}; expected regret {v:.3f}")
        sets = {"none": (), f"{n_places}+{n_tasks}": ps, "10+10": tuple(app)}
        task_sets = {"none": (), f"{n_places}+{n_tasks}": ts, "10+10": tuple(sorted(tasks))}
        res = simulate(pop, swipe, tasks, cards, sets, n=args.n, p_been=p_been, task_sets=task_sets)
        full = res["10+10"]
        print(f"\n{args.n} simulated people; paired difference against 10 places + 10 tasks (± 1 se)")
        for name, r in res.items():
            d, h = r["regret"] - full["regret"], r["hits"] - full["hits"]
            print(f"  {name:>6}: taste sd {r['sd'].mean():.3f}  top-4 hits {r['hits'].mean():.3f} "
                  f"({h.mean():+.3f} ± {h.std(ddof=1) / np.sqrt(len(h)):.3f})  regret {r['regret'].mean():.3f} "
                  f"({d.mean():+.3f} ± {d.std(ddof=1) / np.sqrt(len(d)):.3f})")
        return

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
