"""m260 (Abram, m252): measure recommendation quality over time, keeping what was *predicted* before a visit apart from
what was *observed* after it. Research and a prototype: read-only over data the Brain already keeps, no new table, no
new question, and nothing in the frozen friends' round changes.

**Before the experience** (stored with each plan's stops today): the predicted fit (`predicted`, the model's utility,
turned into the chance of "Good" or better) and the match words shown. The quality perspectives and data confidence
(quality.py) are computed, not stored yet: storing them with each stop is a later step, for Abram (no new table).

**After the experience** (stored today): the 1-5 rating after a stop (Good or better = 4 or 5), "Would you bring
someone here?", and at the end of a day "Was it worth what you spent?" and "Would you do this day again?".
Not collected (and not to be added without Abram's approval, never into the frozen round): whether a stop matched
expectations (approved to investigate after the round, m260) and whether the person would recommend it (deferred):
`decisions/post-experience-questions.md`.

**Measures:** calibration (Brier score, and predicted against observed by band), discrimination (the chance a stop
rated Good was predicted higher than one that wasn't: AUC), whether each match word holds up, how many planned stops
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
    match: str | None = None       # the words shown ("A strong match for you"…)
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


def p_from_utility(u: float, scale: float, cut: float) -> float:
    """The planner stores each stop's utility (`predicted`); the rating model turns it into the chance of Good."""
    return 1.0 / (1.0 + math.exp(-(scale * u - cut)))


def predictions_from_plans(plans: list[dict], scale: float, cut: float) -> list[Prediction]:
    """From stored plans ({id, kind, stops: [{moment_id, predicted, match}]}); lunch slots (no prediction) are skipped."""
    return [Prediction(p["id"], s["moment_id"], p_from_utility(s["predicted"], scale, cut), s.get("match"),
                       p.get("kind", "personal"))
            for p in plans for s in p.get("stops") or [] if s.get("predicted") is not None]


def evaluate(preds: list[Prediction], outs: list[Outcome], days: list[DayOutcome] = (), *, synthetic: bool,
             bands: int = 5, open_questions: dict[tuple[int, str], tuple[str, ...]] | None = None) -> dict:
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
           "rated_share": round(len(pairs) / len(preds), 3) if preds else None}
    if not pairs:
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
    words = {}
    for (pr, _), yi in zip(pairs, y):
        if pr.match:
            words.setdefault(pr.match, []).append(yi)
    out["match_words"] = {w: {"n": len(v), "observed_good": round(sum(v) / len(v), 3)} for w, v in words.items()}
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


def _auc(p: list[float], y: list[int]) -> float | None:
    pos = [pi for pi, yi in zip(p, y) if yi]
    neg = [pi for pi, yi in zip(p, y) if not yi]
    if not pos or not neg:
        return None
    wins = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in pos for b in neg)
    return round(wins / (len(pos) * len(neg)), 3)


__all__ = ["Prediction", "Outcome", "DayOutcome", "evaluate", "predictions_from_plans", "p_from_utility"]
