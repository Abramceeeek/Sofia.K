"""Scoring: S = x · (b_population + δ_person), plus named explanations (CLAUDE.md: explainability)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .features import Conditions, moment_features
from .moments import Moment
from .personal import DeltaPosterior, Observation, fit_delta, prob_negative
from .population import PopulationModel

SWIPE_LEVELS = {"didnt_enjoy": 0, "fine": 1, "loved": 2}   # "havent_been" carries no information
CONFIDENT = 0.8   # name a weight only when P(β<0) > 0.8 or < 0.2 (Area 3)


def score(x: np.ndarray, b: np.ndarray) -> float:
    """The pure scoring function (Area 17): no state, so it can move to the phone later."""
    return float(x @ b)


def score_moment(pop: PopulationModel, b: np.ndarray, moment: Moment,
                 conditions: Conditions | None = None, travel_min: float | None = None,
                 aspiration_match: float = 0.0) -> float:
    return score(pop.vector(moment_features(moment, conditions, travel_min, aspiration_match)), b)


def contributions(pop: PopulationModel, b: np.ndarray, x: dict[str, float], top: int = 3) -> list[dict]:
    """The named terms that drive one stop's score, largest first (input for the LLM explanation)."""
    v = pop.vector(x)
    terms = [(n, float(v[i] * b[i])) for i, n in enumerate(pop.names) if v[i] != 0.0]
    terms.sort(key=lambda t: abs(t[1]), reverse=True)
    return [{"feature": n, "label": pop.spec(n).label, "contribution": round(c, 3)} for n, c in terms[:top]]


# ---- turning a person's answers into observations for the δ update -----------------

def conjoint_observation(pop: PopulationModel, x_a: dict[str, float], x_b: dict[str, float],
                         chose_a: bool) -> Observation:
    x = pop.vector(x_a) - pop.vector(x_b)
    return Observation(x=x, y=1 if chose_a else 0, scale=pop.scales["conjoint"])


def swipe_observation(pop: PopulationModel, moment: Moment, reaction: str,
                      aspiration_match: float = 0.0) -> Observation | None:
    if reaction not in SWIPE_LEVELS:
        return None
    x = pop.vector(moment_features(moment, aspiration_match=aspiration_match))
    return Observation(x=x, y=SWIPE_LEVELS[reaction], scale=pop.scales["swipe"],
                       cutpoints=pop.cutpoints["swipe"])


def rating_observation(pop: PopulationModel, moment: Moment, rating: int,
                       conditions: Conditions | None, travel_min: float | None,
                       aspiration_match: float = 0.0) -> Observation:
    if not 1 <= rating <= 5:
        raise ValueError("rating must be 1-5")
    x = pop.vector(moment_features(moment, conditions, travel_min, aspiration_match))
    return Observation(x=x, y=rating - 1, scale=pop.scales["rating"], cutpoints=pop.cutpoints["rating"])


def update_person(pop: PopulationModel, observations: list[Observation]) -> DeltaPosterior:
    return fit_delta(pop.b_pop, pop.personal_idx, pop.delta_prior_sd, observations, log_mask=pop.log_mask)


# ---- "worth about £V to you" (D88) ----------------------------------------------------

COST = "cost_per_10gbp"


def value_gbp(pop: PopulationModel, b: np.ndarray, moment: Moment, conditions: Conditions | None = None,
              travel_min: float | None = None, aspiration_match: float = 0.0) -> float:
    """V: the non-cost part of S, in pounds, using the person's own cost weight (D88).

    S = S_rest + β_cost · cost/10, so V = S_rest ÷ (−β_cost/10) and S = (−β_cost/10) · (V − cost).
    Ranking by V − price is therefore the same as ranking by S. The cost weight is fitted on a log
    scale, so it stays negative and V stays finite.
    """
    i = pop.names.index(COST)
    beta = float(b[i])
    if beta >= 0:
        raise ValueError("the cost weight must be negative to express value in pounds")
    x = pop.vector(moment_features(moment, conditions, travel_min, aspiration_match))
    s_rest = float(x @ b) - beta * x[i]
    return s_rest * 10.0 / -beta


@dataclass(frozen=True)
class NamedWeight:
    name: str
    label: str
    weight: float           # b_pop + δ
    population: float
    sd: float | None        # None for population-only features
    p_negative: float | None
    confident: bool
    direction: str          # "likes" | "dislikes" | "unsure"; sign-constrained: "stronger" | "weaker" | "unsure"


def named_weights(pop: PopulationModel, post: DeltaPosterior) -> list[NamedWeight]:
    b = pop.b_person(post.mean)
    sds = post.sd()
    pidx = {n: i for i, n in enumerate(pop.personal_names)}
    out = []
    for i, f in enumerate(pop.features):
        if f.name in pidx and f.scale == "log":
            # The sign is fixed (D88), so "confident" means clearly stronger or weaker than most people:
            # P(δ > 0) on the log scale. The sd is put back on the weight's scale (delta method).
            k = pidx[f.name]
            d, sd_log = float(post.mean[k]), float(sds[k])
            p_up = 1.0 - prob_negative(d, sd_log)
            confident = p_up > CONFIDENT or p_up < 1 - CONFIDENT
            direction = ("stronger" if p_up > 0.5 else "weaker") if confident else "unsure"
            out.append(NamedWeight(f.name, f.label, round(float(b[i]), 3), f.mean,
                                   round(abs(float(b[i])) * sd_log, 3), 1.0 if f.mean < 0 else 0.0,
                                   confident, direction))
        elif f.name in pidx:
            sd = float(sds[pidx[f.name]])
            p = prob_negative(float(b[i]), sd)
            confident = p > CONFIDENT or p < 1 - CONFIDENT
            direction = ("dislikes" if p > 0.5 else "likes") if confident else "unsure"
            out.append(NamedWeight(f.name, f.label, round(float(b[i]), 3), f.mean, round(sd, 3),
                                   round(p, 3), confident, direction))
        else:
            out.append(NamedWeight(f.name, f.label, round(float(b[i]), 3), f.mean, None, None, False,
                                   "population"))
    return out
