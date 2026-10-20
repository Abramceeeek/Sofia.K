"""Test B read-out from the admin export (D127: the algorithm reviews asked for more than one number).

Run from brain/ with the venv, on an export saved outside git:
    .venv/bin/python scripts/testb_report.py ../validation/raw/export-2026-11-13.json [--no-overlap]

The export is `GET /v1/admin/export` (admin token in an env var, never pasted anywhere). Visitors from abroad are left
out (D116). It prints:

1. The gut choice: how many chose the personal plan, the "7 of 10" signal scaled to the number of testers, and the
   exact one-sided binomial p against a coin toss. Formative, not proof (decisions/algorithm-review-synthesis.md).
2. "This plan fits me", paired: personal minus generic for each tester; mean, a bootstrap 95% interval and an exact
   sign test. Co-primary with the choice (D127).
3. Overlap: how many of each personal plan's places the no-answers plan (the same brief, population weights only)
   also has. A high overlap means a win comes from the curation, not from the answers.
4. The end-of-day questions (worth what you spent; would you do it again), by the kind of plan.
5. Test A's typed-or-spoken split: "I felt understood" by how the open question was answered.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from dataclasses import replace
from pathlib import Path

import numpy as np

PASS_SHARE = 0.7   # CLAUDE.md: "7 of 10" chose the personal plan


def p_at_least(k: int, n: int, p: float = 0.5) -> float:
    """P(X >= k) for X ~ Binomial(n, p), exactly."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def sign_test(diffs: list[int]) -> tuple[int, int, float]:
    """Exact one-sided sign test that personal > generic: (positive, non-zero, p). Ties are dropped."""
    pos = sum(d > 0 for d in diffs)
    nz = sum(d != 0 for d in diffs)
    return pos, nz, p_at_least(pos, nz) if nz else 1.0


def bootstrap_ci(xs: list[float], reps: int = 10000, seed: int = 20261020) -> tuple[float, float]:
    if len(xs) < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    a = np.asarray(xs, dtype=float)
    means = a[rng.integers(0, len(a), (reps, len(a)))].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def _places(stops: list[dict]) -> list[str]:
    return [st["moment_id"].split("#")[0] for st in stops if not st.get("lunch") and st.get("rateable", True)]


def pairs(export: dict) -> list[dict]:
    """Each UK tester's answered pair: which they chose, both fit ratings, the personal plan's places and its sunset."""
    visitors = {u for u, c in (export.get("cohorts") or {}).items() if c == "visitor"}
    by_user: dict[str, list[dict]] = {}
    for pl in export.get("plans", []):
        if (pl.get("intent") or {}).get("testb_pair") and pl["user_id"] not in visitors:
            by_user.setdefault(pl["user_id"], []).append(pl)
    out = []
    for uid, rows in sorted(by_user.items()):
        personal = next((r for r in rows if r["kind"] == "personal"), None)
        generic = next((r for r in rows if r["kind"] == "generic"), None)
        if not personal or not generic or personal["status"] == "offered":
            continue
        out.append({"user": uid, "chose_personal": personal["status"] == "chosen",
                    "fit_personal": personal.get("fit_rating"), "fit_generic": generic.get("fit_rating"),
                    "places": _places(personal["stops"]), "sunset": (personal.get("intent") or {}).get("sunset")})
    return out


def no_answers_places(sunset: str | None, _cache: dict = {}) -> list[str]:
    """The no-answers plan on the Test B brief (population weights, nothing loved or disliked), as made in the app."""
    if sunset in _cache:
        return _cache[sunset]
    from brain import dayplan, testb
    from brain.config import DATA_DIR
    from brain.moments import load_moments
    from brain.personal import prior_only
    from brain.population import load_population
    from brain.travel import LondonEstimate
    pop = load_population(DATA_DIR / "priors.yaml")
    ready = [m for m in load_moments(DATA_DIR / "moments") if m.status == "ready" and m.in_test_b]
    brief = dayplan.load_brief(DATA_DIR / "testb" / "brief.yaml")
    brief = replace(brief, sunset=sunset or brief.sunset)
    gen = testb.generic_stops(DATA_DIR / "testb" / "generic.yaml", {m.id: m for m in ready}, dayplan._sunset(brief))
    end = testb.plan_end(gen)
    plan, _, _, _ = dayplan.personal_plan(pop, prior_only(pop.delta_prior_sd), ready, brief, LondonEstimate(),
                                          end_window=(end - 30, end + 30) if end is not None else None)
    _cache[sunset] = [dayplan._base(s.moment_id) for s in plan.stops if not s.moment_id.startswith("lunch@")]
    return _cache[sunset]


def report(export: dict, overlap=no_answers_places) -> list[str]:
    ps = pairs(export)
    n = len(ps)
    lines = [f"Test B read-out: {n} UK testers answered the pair (visitors from abroad left out)"]
    if not n:
        return lines
    k = sum(p["chose_personal"] for p in ps)
    need = math.ceil(PASS_SHARE * n)
    lines += ["", "1. Gut choice",
              f"   chose the personal plan: {k} of {n} ({k / n:.0%}); the 7-of-10 signal at this size is {need} of {n}: "
              f"{'met' if k >= need else 'not met'}",
              f"   exact one-sided p against a coin toss: {p_at_least(k, n):.3f} (formative, not proof)"]

    both = [p for p in ps if p["fit_personal"] and p["fit_generic"]]
    diffs = [p["fit_personal"] - p["fit_generic"] for p in both]
    lines += ["", "2. 'This plan fits me' (1-5), personal minus generic, paired"]
    if diffs:
        lo, hi = bootstrap_ci(diffs)
        pos, nz, p = sign_test(diffs)
        lines += [f"   {len(diffs)} testers: mean {np.mean(diffs):+.2f}, median {np.median(diffs):+.1f}, "
                  f"bootstrap 95% interval {lo:+.2f} to {hi:+.2f}",
                  f"   personal rated higher by {pos} of the {nz} who rated them differently; sign test p = {p:.3f}",
                  f"   the choice and the fit agree for {sum((d > 0) == p['chose_personal'] for d, p in zip(diffs, both) if d)} "
                  f"of {nz}"]
    else:
        lines.append("   no paired ratings yet")

    if overlap is not None:
        shares = []
        for p in ps:
            base = set(overlap(p["sunset"]))
            if p["places"]:
                shares.append(len(set(p["places"]) & base) / len(p["places"]))
        if shares:
            mine = [s for s, p in zip(shares, ps) if p["chose_personal"]]
            lines += ["", "3. Overlap with the no-answers plan (share of the personal plan's places it also has)",
                      f"   mean {np.mean(shares):.0%}; fully the same for {sum(s == 1 for s in shares)} of {len(shares)}",
                      f"   among those who chose the personal plan: {np.mean(mine):.0%}" if mine else
                      "   nobody chose the personal plan"]

    kind = {pl["id"]: pl["kind"] for pl in export.get("plans", [])}
    fb = export.get("day_feedback", [])
    lines += ["", "4. End of the day (D127)"]
    if fb:
        for k_ in sorted({kind.get(f["plan_id"], "other") for f in fb}):
            rows = [f for f in fb if kind.get(f["plan_id"], "other") == k_]
            worth = Counter(f["worth"] for f in rows if f["worth"])
            again = Counter(f["again"] for f in rows if f["again"] is not None)
            lines.append(f"   {k_} plans, {len(rows)} days: worth what they spent: less {worth['less']}, about right "
                         f"{worth['about_right']}, more {worth['more']}; would do it again: yes {again[True]}, "
                         f"no {again[False]}")
    else:
        lines.append("   no answers yet")

    answers = export.get("answers", [])
    mode = {a["user_id"]: a["input_mode"] for a in answers if a["question"] == "best_hour"}
    understood = [(mode.get(a["user_id"]), int(a["text"])) for a in answers if a["question"] == "survey:understood"]
    lines += ["", "5. Test A: 'I felt understood' (1-5) by how the open question was answered"]
    for m in ("typed", "voice", None):
        xs = [v for md, v in understood if md == m]
        if xs:
            lines.append(f"   {m or 'skipped it'}: {len(xs)} people, mean {np.mean(xs):.1f}")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("export", type=Path)
    ap.add_argument("--no-overlap", action="store_true", help="skip planning the no-answers plan")
    args = ap.parse_args()
    export = json.loads(args.export.read_text(encoding="utf-8"))
    print("\n".join(report(export, None if args.no_overlap else no_answers_places)))


if __name__ == "__main__":
    main()
