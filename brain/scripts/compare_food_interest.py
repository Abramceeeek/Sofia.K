"""m242: how ODYS could learn whether someone enjoys food experiences, without asking about diet, religion, allergies or
anything sensitive. SYNTHETIC PEOPLE ONLY (the model's own prior); the same set-up as compare_onboarding.py, starting
from the proposed eight kinds (data/categories_global.yaml) and the 5 upfront this-or-that days.

Run from brain/: `.venv/bin/python scripts/compare_food_interest.py [--n 1000]`

The options, each added to that base:
- **question:** "How much is food part of why you go somewhere?" "A big part" / "Some" / "Not much". A big part or not
  much is one stated leaning on the food feature, at the feelings' weight (reasons.FEELING_SCALE); "some" (P 0.3, a
  GUESS) says nothing. It's about enjoying food, never about what someone can or can't eat.
- **ninth kind:** a second food kind, "A meal worth travelling for" (sit-down, tags a GUESS), answered like the others.
- **food day:** a sixth this-or-that day: a day built around a market lunch and a food street against a day of two
  more sights (feature differences a GUESS), at a full this-or-that weight.
- **a rated food stop:** the second stage (4 rated stops), with one of the four always a food card, the best-fitting.

Reported: the share of the food weight's prior variance removed, the correlation of fitted and true food weights, the
ranking of all 49 cards (Spearman), and how well the six food cards' mean fit follows the truth across people.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
spec = importlib.util.spec_from_file_location("compare_onboarding", HERE / "compare_onboarding.py")
co = importlib.util.module_from_spec(spec)
spec.loader.exec_module(co)

from brain.catalogue import ids_in_category  # noqa: E402
from brain.categories import category_from  # noqa: E402
from brain.config import DATA_DIR  # noqa: E402
from brain.features import moment_features  # noqa: E402
from brain.moments import load_moments  # noqa: E402
from brain.personal import Observation  # noqa: E402
from brain.popularity import load_onboarding  # noqa: E402
from brain.population import load_population  # noqa: E402
from brain.reasons import FEELING_SCALE  # noqa: E402
from brain.scoring import conjoint_observation, update_person  # noqa: E402

SEED = 20261110
P_SOME = 0.3                                     # GUESS: "some" says nothing
MEAL_KIND = {"title": "A meal worth travelling for", "line": "A sit-down meal a place is known for.",
             "phrase": "a meal worth travelling for", "example": None,
             "place": {"movement_views": 0, "food": 2, "green_nature": 0, "history_culture": 0, "iconic": 0,
                       "local_novel": 1, "crowds": 1, "walking_effort": 0, "active": 0, "outdoor_exposure": 0,
                       "photo_potential": 0},
             "moment": {"contrast_reveal": 0, "absorption": 1, "awe": 0, "social_pull": 2}}   # GUESS tags
FOOD_DAY = ({"food": 1.0, "local_novel": 0.5, "social_pull": 0.5}, {"history_culture": 0.5, "movement_views": 0.5})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--out", type=Path, default=Path("benchmarks/synthetic/food_interest.txt"))
    args = ap.parse_args(argv)
    pop = load_population(DATA_DIR / "priors.yaml")
    ob = load_onboarding(DATA_DIR, None)
    g = yaml.safe_load((DATA_DIR / "categories_global.yaml").read_text(encoding="utf-8"))
    eight = [category_from(k, it) for k, it in g["items"].items()]
    nine = eight + [category_from("meal", MEAL_KIND)]
    cards = [m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"]
    food_ids = ids_in_category("food_drink")
    food_idx = [j for j, m in enumerate(cards) if m.id in food_ids]
    X = np.array([pop.vector(moment_features(m)) for m in cards])
    sd = np.asarray(pop.delta_prior_sd, dtype=float)
    fk = pop.names.index("food")
    xq = pop.vector({"food": 1.0})
    xa, xb = (pop.vector(d) for d in FOOD_DAY)

    def question(rng, b):
        if rng.random() < P_SOME:
            return []
        scale = pop.scales["conjoint"] * FEELING_SCALE
        return [Observation(x=xq, y=int(rng.random() < co.F(scale * float(xq @ b))), scale=scale)]

    def food_day(rng, b):
        d = float((xa - xb) @ b) * pop.scales["conjoint"]
        return [Observation(x=xa - xb, y=int(rng.random() < co.F(d)), scale=pop.scales["conjoint"])]

    arms = {"base (8 kinds)": lambda rng, b: co.kinds(pop, eight, rng, b),
            "+ question": lambda rng, b: co.kinds(pop, eight, rng, b) + question(rng, b),
            "+ ninth kind": lambda rng, b: co.kinds(pop, nine, rng, b),
            "+ food day": lambda rng, b: co.kinds(pop, eight, rng, b) + food_day(rng, b),
            "base, 4 rated": lambda rng, b: co.kinds(pop, eight, rng, b),
            "base, 4 rated, 1 food": lambda rng, b: co.kinds(pop, eight, rng, b)}
    res = {a: {"var": [], "mean": [], "rho": [], "ft": [], "fh": []} for a in arms}
    truths = []
    for i in range(args.n):
        delta = np.random.default_rng(SEED + i).normal(0.0, sd)
        b = pop.b_person(delta)
        truths.append(delta[fk])
        u = X @ b
        for k, (a, ask) in enumerate(arms.items()):
            rng = np.random.default_rng([SEED, i, k])
            first = ask(rng, b) + co._tasks(pop, ob, rng, b)
            post = update_person(pop, first)
            if "rated" in a:
                order = list(np.argsort(-(X @ pop.b_person(post.mean))))
                top = order[:co.RATED]
                if a.endswith("1 food") and not set(top) & set(food_idx):
                    top = top[:-1] + [next(j for j in order if j in food_idx)]
                post = update_person(pop, first + [co.rate(pop, rng, cards[j], b) for j in top])
            uh = X @ pop.b_person(post.mean)
            r = res[a]
            r["var"].append(post.sd()[fk] ** 2)
            r["mean"].append(post.mean[fk])
            r["rho"].append(float(np.corrcoef(co._ranks(u), co._ranks(uh))[0, 1]))
            r["ft"].append(float(np.mean(u[food_idx])))
            r["fh"].append(float(np.mean(uh[food_idx])))
    T = np.array(truths)
    lines = ["SYNTHETIC PEOPLE ONLY (the model's own prior). Learning whether someone enjoys food experiences, never a diet.",
             f"{args.n} people, seed {SEED}; every arm has the proposed 8 kinds and the 5 upfront this-or-that days.",
             f"'food cards': how well the fitted mean fit of the {len(food_idx)} food cards follows the truth, across people.", "",
             f"{'arm':<24} | {'questions':>9} | {'food variance removed':>21} | {'food weight corr':>16} | "
             f"{'rank rho (49)':>13} | {'food cards':>10}"]
    extra_q = {"base (8 kinds)": 0, "+ question": 1, "+ ninth kind": 1, "+ food day": 1, "base, 4 rated": 0,
               "base, 4 rated, 1 food": 0}
    for a, r in res.items():
        share = 1 - float(np.mean(r["var"])) / sd[fk] ** 2
        corr = float(np.corrcoef(r["mean"], T)[0, 1])
        fc = float(np.corrcoef(r["ft"], r["fh"])[0, 1])
        lines.append(f"{a:<24} | {13 + extra_q[a]:>9} | {share:>21.3f} | {corr:>16.3f} | {np.mean(r['rho']):>13.3f} | "
                     f"{fc:>10.3f}")
    print("\n".join(lines))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
