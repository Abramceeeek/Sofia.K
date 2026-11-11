"""Audit (11 Nov 2026): how many rated stops until the model knows a person? (decisions/brain-global-readiness.md)

Run from brain/ with the venv: `.venv/bin/python scripts/learning_curve.py [--people 300] [--out
benchmarks/synthetic/learning_curve.txt]`.

**Synthetic people only**, in the model's own world: tastes are drawn from the model's prior, and people answer the
short onboarding and rate stops exactly as the model assumes (the helpers are `compare_onboarding.py`'s own). So the
numbers are a ceiling: real people are noisier and have tastes the tags don't describe. No real answer is read, and
nothing is tuned to these numbers.

`compare_onboarding.py` showed what the questions teach. This adds the part that decides retention: what the model
knows after 0, 4, 8, … rated stops, and how much a taste the tags can't describe takes away.

For each person, after the onboarding and then after each day of rated stops:
- **rank rho**: how well the fitted order of the ready cards follows the person's true order (Spearman);
- **true top 8 found**: how many of their true best eight are in the fitted best eight;
- **gain kept**: the true value of the model's four best cards for them, less that of the no-answers four (Test B's
  generic comparison), as a share of what knowing their tastes exactly would gain. 0% is "no better than the generic
  plan"; 100% is "knows them". It is the total gain over everyone divided by the total possible gain (a ratio for
  each person and then a mean would be swamped by the people for whom the generic four is already nearly right),
  with a bootstrap standard error over people.

Which stops get rated:
- **the app's own days**: each day is the four cards the model currently rates highest that they haven't done, as the
  app would plan (it learns only about what it already recommends);
- **random days**: four cards at random, for comparison (what trying things the model wouldn't pick would teach).

`--idio τ`: a taste for each card that no tag describes (the same every time they'd rate it), with sd τ. τ = 0 is the
model's own world. The second run uses τ = 0.75, the sd of one taste weight (a GUESS: nothing measures it yet; the
first real ratings will).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from brain.config import DATA_DIR  # noqa: E402
from brain.features import moment_features  # noqa: E402
from brain.moments import load_moments  # noqa: E402
from brain.popularity import load_onboarding  # noqa: E402
from brain.population import load_population  # noqa: E402
from brain.scoring import rating_observation, update_person  # noqa: E402

from compare_onboarding import P_BEEN_LONDONER, _ranks, _tasks, named  # noqa: E402

SEED = 20261111
DAY = 4          # stops rated in one day
TOP, BEST = 8, 4


def _rate(pop, rng, m, x, b, extra: float):
    """One 1-5 rating, as the model assumes, plus the person's own untagged taste for this card."""
    u = pop.scales["rating"] * (float(x @ b) + extra) + rng.logistic()
    y = int(np.searchsorted(np.array(pop.cutpoints["rating"]), u))
    return rating_observation(pop, m, y + 1, None, None)


def run(people: int, days: int, idio: float, arm: str, seed: int = SEED) -> list[dict]:
    pop = load_population(DATA_DIR / "priors.yaml")
    ob = load_onboarding(DATA_DIR, None)
    cards = [m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"]
    X = np.array([pop.vector(moment_features(m)) for m in cards])
    generic = np.argsort(-(X @ pop.b_pop))[:BEST]
    rows = [dict(rated=d * DAY, rho=[], top=[], got=[], could=[]) for d in range(days + 1)]
    for person in range(people):
        # each person has their own streams, so every run meets the same people giving the same onboarding answers
        b = pop.b_person(np.random.default_rng([seed, person, 1]).normal(0.0, pop.delta_prior_sd))
        own = (np.random.default_rng([seed, person, 2]).normal(0.0, idio, len(cards)) if idio
               else np.zeros(len(cards)))
        rng = np.random.default_rng([seed, person, 3])
        truth = X @ b + own
        best = np.sort(truth)[::-1][:BEST].sum()
        base = truth[generic].sum()
        obs = named(pop, ob, rng, b, P_BEEN_LONDONER) + _tasks(pop, ob, rng, b)
        done: set[int] = set()
        for d in range(days + 1):
            fit = X @ pop.b_person(update_person(pop, obs).mean)
            rows[d]["rho"].append(float(np.corrcoef(_ranks(fit), _ranks(truth))[0, 1]))
            rows[d]["top"].append(len(set(np.argsort(-fit)[:TOP]) & set(np.argsort(-truth)[:TOP])))
            rows[d]["got"].append(float(truth[np.argsort(-fit)[:BEST]].sum() - base))
            rows[d]["could"].append(float(best - base))
            left = [i for i in range(len(cards)) if i not in done]
            if len(left) < DAY:
                break
            pick = (sorted(left, key=lambda i: -fit[i])[:DAY] if arm == "app"
                    else list(rng.choice(left, DAY, replace=False)))
            for i in pick:
                done.add(int(i))
                obs.append(_rate(pop, rng, cards[i], X[i], b, float(own[i])))
    boot = np.random.default_rng([seed, 9])
    out = []
    for r in rows:
        if not r["rho"]:
            continue
        got, could = np.array(r["got"]), np.array(r["could"])
        picks = boot.integers(0, len(got), (400, len(got)))
        shares = got[picks].sum(axis=1) / np.maximum(could[picks].sum(axis=1), 1e-9)
        out.append(dict(rated=r["rated"], n=len(r["rho"]), rho=float(np.mean(r["rho"])),
                        rho_se=float(np.std(r["rho"]) / np.sqrt(len(r["rho"]))), top=float(np.mean(r["top"])),
                        kept=float(got.sum() / max(could.sum(), 1e-9)), kept_se=float(np.std(shares)),
                        better=float(np.mean(got > 1e-9)), worse=float(np.mean(got < -1e-9))))
    return out


def table(title: str, rows: list[dict]) -> str:
    out = [title, "rated stops | rank rho (± se) | true top 8 found | gain kept vs the generic four (± se) | "
                  "their four beat / lose to the generic four"]
    for r in rows:
        out.append(f"{r['rated']:>11} |  {r['rho']:.3f} ±{r['rho_se']:.3f} | {r['top']:>10.2f} of 8 | "
                   f"{100 * r['kept']:>5.0f}% ±{100 * r['kept_se']:.0f} | "
                   f"{100 * r['better']:.0f}% / {100 * r['worse']:.0f}% of people")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--people", type=int, default=300)
    ap.add_argument("--days", type=int, default=10)
    ap.add_argument("--idio", type=float, default=0.75)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    head = (f"SYNTHETIC PEOPLE ONLY (the model's own prior). What the model knows about a person after the short\n"
            f"onboarding (6 named places as a Londoner, 5 this-or-that days) and then after each day of {DAY} rated stops.\n"
            f"{a.people} people, seed {SEED}, the ready cards. A ceiling: real people are noisier. See the script's notes.\n")
    parts = [head,
             table("A. The app's own days, tastes fully described by the tags", run(a.people, a.days, 0.0, "app")),
             table("B. Random days (trying what the model wouldn't pick), same people",
                   run(a.people, a.days, 0.0, "random")),
             table(f"C. The app's own days, with a taste the tags can't describe (sd {a.idio}, a GUESS)",
                   run(a.people, a.days, a.idio, "app"))]
    text = "\n\n".join(parts) + "\n"
    print(text)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
