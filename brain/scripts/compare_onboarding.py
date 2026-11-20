"""m220, m229: named London places vs kinds of places in onboarding: which taste dimensions does each one learn?
SYNTHETIC PEOPLE ONLY (drawn from the model's own prior). It shows what the model can learn from each set of
questions if people answer as the model assumes. It says nothing about how real people find the questions: that's
for the friends' round and after.

Run from brain/: `.venv/bin/python scripts/compare_onboarding.py [--n 400]`

Every arm also asks the same 5 "this or that" days before the first plan (D112), so the comparison is only the
places part:
- **named, Londoner:** the 6 upfront London places, each been to with P = 0.75. That's the planner's simulation default
  (popularity.py), a GUESS; the swipe page's measured familiarity isn't in this repo.
- **named, visitor:** the same 6 places, each been to with P = 0.15. This is a GUESS for someone new to London: most
  answers are "haven't been", which carries nothing.
- **kinds of places:** the 8 cards in data/categories.yaml, each tried with P = 0.9 (a GUESS; `--p-tried` changes it).
  If not tried, "Would you like to try it?" gets yes or no, or "not sure" with P = 0.3 (a GUESS), which carries nothing.
- m229, **the globally neutral proposal** (data/categories_global.yaml, not served): its 8 kinds; the 8 plus two
  investigated kinds (shopping, live shows and sport) as 10; and an 8 that keeps shopping in by making museums and
  galleries one kind. Only the tags enter the simulation, so a change of wording alone can't show here: that needs
  people.

The answers follow the model: a reaction is the swipe model's (scale, cutpoints and logistic noise), and a "would you
like to" is its stated-choice model at half weight (categories.WANT_SCALE). For each personal dimension it measures
how much of the prior variance the answers remove, and how well the fitted taste follows the true one across people.
A fourth arm is the two-stage version Abram described: kinds of places first, then the person's ratings of the
first day's 4 stops. Those are the 4 cards the fitted model ranks highest, as a plan would pick them, and they're
rated by the rating model. For each person it measures how well the 49 ready cards are ranked: Spearman's rho between true and fitted
utilities, and how many of the true top 8 are in the fitted top 8. m229 adds "shops": across people, the correlation
of true and fitted mean utility of the five shopping cards (triplength.SHOPPING), to see whether a shopping question
helps with them. The truth is drawn from the model's own tastes, which have no shopping or live-entertainment
dimension, so this can't show whether such a question captures a taste the model doesn't have.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from brain.categories import WANT_SCALE, category_from, load_categories  # noqa: E402
from brain.config import DATA_DIR  # noqa: E402
from brain.features import conjoint_plan_features, moment_features  # noqa: E402
from brain.moments import load_moments  # noqa: E402
from brain.popularity import load_onboarding  # noqa: E402
from brain.population import load_population  # noqa: E402
from brain.triplength import SHOPPING  # noqa: E402
from brain.scoring import (conjoint_observation, rating_observation, swipe_observation,  # noqa: E402
                           swipe_vector, update_person)
from brain.personal import Observation  # noqa: E402

SEED = 20261108
RATED = 4   # the second stage (Abram, 7 Nov): one day's stops rated after the first plan
P_BEEN_LONDONER, P_BEEN_VISITOR, P_TRIED, P_NOT_SURE = 0.75, 0.15, 0.9, 0.3   # GUESSES, as above
TOP = 8
F = lambda z: 1.0 / (1.0 + np.exp(-z))


def _react(pop, rng, m, b):
    u = pop.scales["swipe"] * float(swipe_vector(pop, moment_features(m)) @ b) + rng.logistic()
    return ("didnt_enjoy", "fine", "loved")[int(np.searchsorted(np.array(pop.cutpoints["swipe"]), u))]


def _tasks(pop, ob, rng, b):
    out = []
    for k in ob.upfront_tasks:
        t = ob.tasks[k]
        xa, xb = conjoint_plan_features(t["A"]), conjoint_plan_features(t["B"])
        d = float((pop.vector(xa) - pop.vector(xb)) @ b) * pop.scales["conjoint"]
        out.append(conjoint_observation(pop, xa, xb, chose_a=rng.random() < F(d)))
    return out


def named(pop, ob, rng, b, p_been):
    obs = []
    for i in ob.upfront_places:
        if rng.random() < p_been and (o := swipe_observation(pop, ob.swipe_items[i], _react(pop, rng, ob.swipe_items[i], b))):
            obs.append(o)
    return obs


def kinds(pop, cats, rng, b, p_tried=P_TRIED):
    obs = []
    for c in cats:
        if rng.random() < p_tried:
            obs.append(swipe_observation(pop, c.moment, _react(pop, rng, c.moment, b)))
        elif rng.random() >= P_NOT_SURE:
            x = pop.vector(moment_features(c.moment))
            scale = pop.scales["conjoint"] * WANT_SCALE
            obs.append(Observation(x=x, y=int(rng.random() < F(scale * float(x @ b))), scale=scale))
    return obs


def rate(pop, rng, m, b):
    u = pop.scales["rating"] * float(pop.vector(moment_features(m)) @ b) + rng.logistic()
    y = int(np.searchsorted(np.array(pop.cutpoints["rating"]), u))   # 0..4, i.e. 1-5 stars
    return rating_observation(pop, m, y + 1, None, None)


def _ranks(v):
    r = np.empty(len(v))
    r[np.argsort(v)] = np.arange(len(v))
    return r


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--p-tried", type=float, default=P_TRIED)
    ap.add_argument("--out", type=Path, default=Path("benchmarks/synthetic/onboarding.txt"))
    args = ap.parse_args(argv)
    pop = load_population(DATA_DIR / "priors.yaml")
    ob = load_onboarding(DATA_DIR, None)
    current = list(load_categories(DATA_DIR / "categories.yaml").items.values())
    g = yaml.safe_load((DATA_DIR / "categories_global.yaml").read_text(encoding="utf-8"))   # m229, not served
    glob8 = [category_from(k, it) for k, it in g["items"].items()]
    cand = {k: category_from(k, it) for k, it in g["candidates"].items()}
    ten = glob8 + [cand["shopping"], cand["live"]]
    swap8 = ([cand["museums_and_galleries"]] + [c for c in glob8 if c.key not in ("big_museums", "art_galleries")]
             + [cand["shopping"]])
    pt = args.p_tried
    cards = [m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"]
    shops = [j for j, m in enumerate(cards) if m.id in SHOPPING]
    X = np.array([pop.vector(moment_features(m)) for m in cards])
    prior_sd = np.asarray(pop.delta_prior_sd, dtype=float)
    names = pop.personal_names
    arms = {"named, Londoner": (6, lambda rng, b: named(pop, ob, rng, b, P_BEEN_LONDONER)),
            "named, visitor": (6, lambda rng, b: named(pop, ob, rng, b, P_BEEN_VISITOR)),
            "kinds, current 8": (8, lambda rng, b: kinds(pop, current, rng, b, pt)),
            "kinds, global 8": (8, lambda rng, b: kinds(pop, glob8, rng, b, pt)),
            "global 8, 4 rated": (8, lambda rng, b: kinds(pop, glob8, rng, b, pt)),
            "global 10": (10, lambda rng, b: kinds(pop, ten, rng, b, pt)),
            "global 8, shops in": (8, lambda rng, b: kinds(pop, swap8, rng, b, pt))}
    res = {a: {"mean": [], "var": [], "rho": [], "top": [], "n": [], "shop_true": [], "shop_hat": []} for a in arms}
    truths = []
    for i in range(args.n):
        rng0 = np.random.default_rng(SEED + i)
        delta = rng0.normal(0.0, prior_sd)
        b = pop.b_person(delta)
        truths.append(delta)
        u_true = X @ b
        for a, (_, ask) in arms.items():
            rng = np.random.default_rng([SEED, i, list(arms).index(a)])
            places = ask(rng, b)
            first = places + _tasks(pop, ob, rng, b)
            post = update_person(pop, first)
            if a.endswith("4 rated"):   # stage 2: rate the first plan's stops (the fitted model's top 4)
                top = np.argsort(-(X @ pop.b_person(post.mean)))[:RATED]
                post = update_person(pop, first + [rate(pop, rng, cards[j], b) for j in top])
            u_hat = X @ pop.b_person(post.mean)
            r = res[a]
            r["mean"].append(post.mean)
            r["var"].append(post.sd() ** 2)
            r["rho"].append(float(np.corrcoef(_ranks(u_true), _ranks(u_hat))[0, 1]))
            r["top"].append(len(set(np.argsort(-u_true)[:TOP]) & set(np.argsort(-u_hat)[:TOP])))
            r["n"].append(len(places))
            r["shop_true"].append(float(np.mean(u_true[shops])))
            r["shop_hat"].append(float(np.mean(u_hat[shops])))
    T = np.array(truths)
    out = ["SYNTHETIC PEOPLE ONLY (the model's own prior). What each set of onboarding questions lets the model learn,",
           f"if people answer as the model assumes. {args.n} people, seed {SEED}; every arm also has the 5 upfront",
           f"this-or-that days. P(been) Londoner 0.75, visitor 0.15; kinds: P(tried) {pt}, 'not sure' 0.3 (all GUESSES).",
           "'shops': across people, how well the fitted mean utility of the 5 shopping cards follows the true one.", ""]
    out.append(f"{'arm':<20} | {'asked':>5} | {'place answers':>13} | {'rank rho (± se)':>15} | {'true top 8 found':>16} | {'shops':>5}")
    for a, r in res.items():
        shop = float(np.corrcoef(r["shop_true"], r["shop_hat"])[0, 1])
        se = float(np.std(r["rho"], ddof=1) / np.sqrt(len(r["rho"])))
        out.append(f"{a:<20} | {arms[a][0]:>5} | {np.mean(r['n']):>13.1f} | {np.mean(r['rho']):>8.3f} ±{se:.3f} | "
                   f"{np.mean(r['top']):>12.2f} of {TOP} | {shop:>5.2f}")
    out.append("")
    out.append("Per dimension: share of the prior variance removed (0 = nothing learned) / correlation of fitted with true")
    out.append(f"{'dimension':<22} | " + " | ".join(f"{a:>20}" for a in arms))
    learned = {}
    for k, nm in enumerate(names):
        cells = []
        for a, r in res.items():
            share = 1 - float(np.mean(np.array(r["var"])[:, k])) / prior_sd[k] ** 2
            corr = float(np.corrcoef(np.array(r["mean"])[:, k], T[:, k])[0, 1])
            learned.setdefault(nm, {})[a] = (share, corr)
            cells.append(f"{share:>9.2f} / {corr:>7.2f} ")
        out.append(f"{nm:<22} | " + " | ".join(f"{c:>20}" for c in cells))
    onboarding_arms = [a for a in arms if not a.endswith("4 rated")]
    weak = [nm for nm in names if all(learned[nm][a][0] < 0.10 for a in onboarding_arms)]
    out.append("")
    out.append("Learned by no onboarding arm (under 10% of the prior variance removed by every arm without ratings): "
               + (", ".join(weak) or "none"))
    still = [nm for nm in weak if learned[nm]["global 8, 4 rated"][0] < 0.10]
    out.append("... and still under 10% after 4 rated stops: " + (", ".join(still) or "none"))

    def versus(a, b):
        d = {nm: learned[nm][a][0] - learned[nm][b][0] for nm in names}
        more = ", ".join(f"{nm} (+{v:.2f})" for nm, v in sorted(d.items(), key=lambda kv: -kv[1]) if v > 0.02)
        less = ", ".join(f"{nm} ({v:.2f})" for nm, v in sorted(d.items(), key=lambda kv: kv[1]) if v < -0.02)
        out.append(f"{a} vs {b}: learns more on {more or 'nothing'}; less on {less or 'nothing'}")

    for a, b_ in (("kinds, current 8", "named, Londoner"), ("kinds, global 8", "kinds, current 8"),
                  ("global 10", "kinds, global 8"), ("global 8, shops in", "kinds, global 8")):
        versus(a, b_)
    print("\n".join(out))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
