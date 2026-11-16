"""m260 (Abram, m252): measure recommendation quality over time, keeping what was *predicted* before a visit apart from
what was *observed* after it. Research and a prototype: read-only over data the Brain already keeps, no new table, no
new question, and nothing in the frozen friends' round changes.

**Before the experience** (stored with each plan's stops today): the predicted fit (`predicted`, the model's utility,
turned into the chance of "Good" or better) and the line shown beside it. The quality perspectives and data confidence
(quality.py) are computed, not stored yet: storing them with each stop is a later step, for Abram (no new table).

**After the experience** (stored today): the 1-5 rating after a stop (Good or better = 4 or 5), "Would you bring
someone here?", and at the end of a day "Was it worth what you spent?" and "Would you do this day again?".
Not collected (and not to be added without Abram's approval, never into the frozen round): whether a stop matched
expectations (approved to investigate after the round, m260) and whether the person would recommend it (deferred):
`decisions/post-experience-questions.md`.

**Measures:** calibration (Brier score, and predicted against observed by band), discrimination (the chance a stop
rated Good was predicted higher than one that wasn't: AUC), whether each internal band holds up (m275: no words or
chances are shown until it does), how many planned stops
are rated (a low share means the rest is guesswork), and the day-level answers. Synthetic data is labelled and never
reported as real-user validation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

GOOD_RATING = 4                    # "Good" or better on the 1-5 scale (dayplan's match words use the same line)


@dataclass(frozen=True)
class Prediction:
    plan_id: int
    moment_id: str
    p_good: float                  # the chance of "Good" or better, before the visit
    match: str | None = None       # the line shown: the old words before m275, the factor line after
    kind: str = "personal"         # personal | generic (Test B's no-answers plan)


@dataclass(frozen=True)
class Outcome:
    plan_id: int
    moment_id: str
    rating: int                    # 1-5, after the visit
    would_bring: bool | None = None


@dataclass(frozen=True)
class DayOutcome:
    plan_id: int
    worth: str | None              # less | about_right | more
    again: bool | None


STRONG_LINE, GOOD_LINE = 0.75, 0.5   # dayplan.MATCH_STRONG, MATCH_GOOD (internal since m275; never shown)


def _band(p: float) -> str:
    return "strong" if p >= STRONG_LINE else "good" if p >= GOOD_LINE else "other"


def p_from_utility(u: float, scale: float, cut: float) -> float:
    """The planner stores each stop's utility (`predicted`); the rating model turns it into the chance of Good."""
    return 1.0 / (1.0 + math.exp(-(scale * u - cut)))


def predictions_from_plans(plans: list[dict], scale: float, cut: float) -> list[Prediction]:
    """From stored plans ({id, kind, stops: [{moment_id, predicted, match}]}); lunch slots (no prediction) are skipped."""
    return [Prediction(p["id"], s["moment_id"], p_from_utility(s["predicted"], scale, cut), s.get("match"),
                       p.get("kind", "personal"))
            for p in plans for s in p.get("stops") or [] if s.get("predicted") is not None]


def shown_from_plans(plans: list[dict]) -> dict[tuple[int, str], str]:
    """m276: the line each stored stop showed beside its price, (plan id, moment id) → text. Plans made before m276
    kept no prediction, but those from the frozen round (build 91) kept D127's words, the bands themselves."""
    return {(p["id"], s["moment_id"]): s["match"] for p in plans for s in p.get("stops") or [] if s.get("match")}


def evaluate(preds: list[Prediction], outs: list[Outcome], days: list[DayOutcome] = (), *, synthetic: bool,
             bands: int = 5, open_questions: dict[tuple[int, str], tuple[str, ...]] | None = None,
             shown: dict[tuple[int, str], str] | None = None) -> dict:
    """Pair each rating with the prediction made for that stop in that plan, then measure. Nothing is imputed: an
    unrated stop is counted as unrated, never as a guess.

    m268 (Abram, m260, priority C): with `open_questions` ((plan id, moment id) → the facts quality.uncertainties
    leaves materially open for that day, empty when none), rated stops are also split by whether their facts had an
    open question. That tests the premise of the uncertainty-aware ranking on real ratings: places with open questions
    disappoint more often. A stop not in the mapping is counted apart, never guessed."""
    by = {(p.plan_id, p.moment_id): p for p in preds}
    pairs = [(by[(o.plan_id, o.moment_id)], o) for o in outs if (o.plan_id, o.moment_id) in by]
    out = {"synthetic": synthetic, "label": "SYNTHETIC: not real-user validation" if synthetic else "real ratings",
           "planned_stops": len(preds), "rated": len(pairs),
           "rated_share": round(len(pairs) / len(preds), 3) if preds else None,
           # m276: ratings whose plan kept no prediction (plans made before m276, the frozen round's included)
           "rated_without_prediction": len(outs) - len(pairs)}
    # the line each rated stop showed, whether or not its plan kept a prediction: before m275, D127's words
    said = dict(shown or {}) | {k: pr.match for k, pr in by.items() if pr.match and k not in (shown or {})}
    words: dict[str, list[int]] = {}
    for o in outs:
        if (w := said.get((o.plan_id, o.moment_id))):
            words.setdefault(w, []).append(1 if o.rating >= GOOD_RATING else 0)
    out["match_words"] = {w: {"n": len(v), "observed_good": round(sum(v) / len(v), 3)} for w, v in words.items()}
    if not pairs:
        if outs:   # never "no rated stops" when there are ratings: say what they can and can't show
            return out | {"note": f"{len(outs)} rated stops, but their plans kept no prediction (made before m276): "
                                  "only the words shown with them can be checked."}
        return out | {"note": "No rated stops yet: nothing can be said about quality."}
    y = [1 if o.rating >= GOOD_RATING else 0 for _, o in pairs]
    p = [pr.p_good for pr, _ in pairs]
    out["brier"] = round(sum((pi - yi) ** 2 for pi, yi in zip(p, y)) / len(y), 4)
    out["base_rate_brier"] = round(sum((sum(y) / len(y) - yi) ** 2 for yi in y) / len(y), 4)   # always predicting the mean
    out["observed_good"] = round(sum(y) / len(y), 3)
    out["mean_predicted"] = round(sum(p) / len(p), 3)
    out["auc"] = _auc(p, y)
    edges = [i / bands for i in range(bands + 1)]
    out["calibration"] = []
    for lo, hi in zip(edges, edges[1:]):
        idx = [i for i, pi in enumerate(p) if lo <= pi < hi or (hi == 1.0 and pi == 1.0)]
        if idx:
            out["calibration"].append({"band": f"{lo:.1f}-{hi:.1f}", "n": len(idx),
                                       "predicted": round(sum(p[i] for i in idx) / len(idx), 3),
                                       "observed": round(sum(y[i] for i in idx) / len(idx), 3)})
    bands = {}
    for (pr, _), yi in zip(pairs, y):
        bands.setdefault(_band(pr.p_good), []).append(yi)
    # m275 (Abram, 12 Nov): the internal bands behind the old words, by the chance before the visit. The evidence
    # any wording of a chance would need first: does "strong" (75% or more) come true about that often on real ratings?
    out["match_bands"] = {k: {"n": len(bands[k]), "observed_good": round(sum(bands[k]) / len(bands[k]), 3)}
                          for k in ("strong", "good", "other") if k in bands}
    bring = [o.would_bring for _, o in pairs if o.would_bring is not None]
    out["would_bring"] = round(sum(bring) / len(bring), 3) if bring else None
    if open_questions is not None:
        share = lambda v: {"n": len(v), "observed_good": round(sum(v) / len(v), 3) if v else None}
        split, fields = {"none": [], "some": []}, {}
        for (pr, _), yi in zip(pairs, y):
            qs = open_questions.get((pr.plan_id, pr.moment_id))
            if qs is None:
                continue
            split["some" if qs else "none"].append(yi)
            for f in qs:
                fields.setdefault(f, []).append(yi)
        out["open_questions"] = {"none": share(split["none"]), "some": share(split["some"]),
                                 "by_fact": {f: share(v) for f, v in sorted(fields.items())},
                                 "not_in_catalogue": sum(1 for pr, _ in pairs
                                                         if (pr.plan_id, pr.moment_id) not in open_questions)}
    if days:
        again = [d.again for d in days if d.again is not None]
        out["day_again"] = round(sum(again) / len(again), 3) if again else None
        worth = [d.worth for d in days if d.worth]
        out["day_worth"] = {k: worth.count(k) for k in ("less", "about_right", "more")} if worth else None
    return out


# ---- learning by milestone (Abram, 12 Nov, part 3B) ---------------------------------------------------------------

# Does ODYS learn about a real person? Each rated stop is judged by the prediction its plan was made with, grouped by
# how much the person had told us when that plan was made, and compared with what the model would have said knowing
# nothing about them (the population's weights alone, the same stop and conditions). Learning shows as the personal
# prediction beating that baseline by more at each later milestone. Ratings only; nothing imputed; never synthetic
# users in place of real ones.
MILESTONES = ("after onboarding", "after the first rating", "after 2 days out", "after 5 days out", "after 20 ratings")
MIN_PER_MILESTONE = 30   # GUESS, as evaluate_export's MIN_FOR_PATTERNS: fewer rated stops and a row is exploratory


def milestone(n_ratings_before: int, days_out_before: int) -> str:
    """The furthest milestone reached when a plan was made. "Days out" are London dates with at least one rating, so
    a day without the app doesn't count as learning. Twenty ratings can come before five days out; it's the further."""
    if n_ratings_before >= 20:
        return MILESTONES[4]
    if days_out_before >= 5:
        return MILESTONES[3]
    if days_out_before >= 2:
        return MILESTONES[2]
    return MILESTONES[1] if n_ratings_before >= 1 else MILESTONES[0]


@dataclass(frozen=True)
class PlanMade:
    user_id: str
    made_at: str                  # ISO time the plan was made (the stored plan's created_at)


def learning_by_milestone(preds: list[Prediction], outs: list[Outcome], made: dict[int, PlanMade],
                          rated_at: dict[str, list[str]], baseline: dict[tuple[int, str], float] | None = None, *,
                          synthetic: bool) -> dict:
    """`rated_at`: each person's rating times (ISO). `baseline`: (plan id, moment id) → the chance of Good from the
    population's weights alone. Per milestone: rated stops, people, observed Good, mean predicted, Brier score for the
    personal prediction and for the baseline, and the gain (baseline minus personal: above 0, the person's answers
    helped). Rows under MIN_PER_MILESTONE are marked exploratory."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    london = ZoneInfo("Europe/London")
    when = lambda t: datetime.fromisoformat(t.replace("Z", "+00:00"))
    times = {u: sorted(when(t) for t in ts) for u, ts in rated_at.items()}
    by = {(p.plan_id, p.moment_id): p for p in preds}
    groups: dict[str, list[tuple[str, float, float | None, int]]] = {m: [] for m in MILESTONES}
    unplaced = 0
    for o in outs:
        pr, meta = by.get((o.plan_id, o.moment_id)), made.get(o.plan_id)
        if pr is None or meta is None:
            unplaced += 1
            continue
        t0 = when(meta.made_at)
        before = [t for t in times.get(meta.user_id, []) if t < t0]
        stage = milestone(len(before), len({t.astimezone(london).date() for t in before}))
        base = (baseline or {}).get((o.plan_id, o.moment_id))
        groups[stage].append((meta.user_id, pr.p_good, base, 1 if o.rating >= GOOD_RATING else 0))
    brier = lambda ps, ys: round(sum((p - y) ** 2 for p, y in zip(ps, ys)) / len(ys), 4)
    rows = []
    for stage, g in groups.items():
        row = {"milestone": stage, "n": len(g), "people": len({u for u, *_ in g})}
        if g:
            ps, ys = [x[1] for x in g], [x[3] for x in g]
            row.update(observed_good=round(sum(ys) / len(ys), 3), mean_predicted=round(sum(ps) / len(ps), 3),
                       brier=brier(ps, ys), auc=_auc(ps, ys), exploratory=len(g) < MIN_PER_MILESTONE)
            with_base = [x for x in g if x[2] is not None]
            if with_base:
                bp, bp_base, by_ = [x[1] for x in with_base], [x[2] for x in with_base], [x[3] for x in with_base]
                row.update(n_with_baseline=len(with_base), brier_baseline=brier(bp_base, by_),
                           gain=round(brier(bp_base, by_) - brier(bp, by_), 4))
        rows.append(row)
    return {"synthetic": synthetic, "label": "SYNTHETIC: not real-user validation" if synthetic else "real ratings",
            "rows": rows, "rated_without_prediction": unplaced}


def _auc(p: list[float], y: list[int]) -> float | None:
    pos = [pi for pi, yi in zip(p, y) if yi]
    neg = [pi for pi, yi in zip(p, y) if not yi]
    if not pos or not neg:
        return None
    wins = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in pos for b in neg)
    return round(wins / (len(pos) * len(neg)), 3)


__all__ = ["Prediction", "Outcome", "DayOutcome", "evaluate", "predictions_from_plans", "p_from_utility",
           "shown_from_plans", "MILESTONES", "milestone", "PlanMade", "learning_by_milestone"]
