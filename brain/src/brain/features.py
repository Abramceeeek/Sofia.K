"""Named features: the x in S = x·b.

Thresholds, not lines (CLAUDE.md): transfers cost nothing up to 15 min, then two hinges.
Heat (28°C+) and cold (8°C or below, D95) are thresholds that only bite outdoors; rain scales with its probability.
"""

from __future__ import annotations

from dataclasses import dataclass

from .moments import MOMENT_TAGS, PLACE_TAGS, Moment

HOT_C = 28.0
COLD_C = 8.0   # GUESS (D95): "cold but dry" in the conjoint; the interviewer says "about 5°C" if asked


@dataclass(frozen=True)
class Conditions:
    temp_c: float | None = None     # forecast or observed temperature at the stop
    rain_prob: float | None = None  # 0-1


def leg_features(travel_min: float | None) -> dict[str, float]:
    """Transfer hinges: 15 min is fine; 15-30 costs a little; every 20 min past 30 costs more."""
    if travel_min is None:
        return {}
    t = float(travel_min)
    return {
        "transfer_15_30": min(max(t - 15.0, 0.0), 15.0) / 15.0,
        "transfer_30_plus": max(t - 30.0, 0.0) / 20.0,
    }


def moment_features(moment: Moment, conditions: Conditions | None = None,
                    travel_min: float | None = None, aspiration_match: float = 0.0) -> dict[str, float]:
    """Features of one stop. Missing tags count as 0 (the planner only uses complete moments).

    `aspiration_match` (D77) is person-specific: 1 if the moment belongs to a field the person picked
    (`brain.aspiration.AspirationMap.match`), else 0.
    """
    x: dict[str, float] = {}
    for t in PLACE_TAGS + MOMENT_TAGS:
        v = moment.tag(t)
        x[t] = (v or 0) / 2.0
    x["cost_per_10gbp"] = (moment.cost_gbp or 0.0) / 10.0
    c = conditions or Conditions()
    hot = 1.0 if (c.temp_c is not None and c.temp_c >= HOT_C) else 0.0
    x["hot_outdoor"] = hot * x["outdoor_exposure"]
    x["heat_walking"] = hot * x["walking_effort"]
    x["rain_outdoor"] = (c.rain_prob or 0.0) * x["outdoor_exposure"]
    cold = 1.0 if (c.temp_c is not None and c.temp_c <= COLD_C) else 0.0
    x["cold_outdoor"] = cold * x["outdoor_exposure"]
    x.update(leg_features(travel_min))
    if aspiration_match:
        x["aspiration_match"] = float(aspiration_match)
    return x


# ---- the conjoint "this or that" tasks (validation/conjoint/design.csv) -------------

def conjoint_plan_features(row: dict[str, str]) -> dict[str, float]:
    """Map one plan description from design.csv onto the same named features.

    The plan-level coding differs in scale from the moment-level tags (e.g. "busy at 2 stops"
    vs a 0-1 crowd tag). The source-specific scale parameter absorbs that (Area 3, Train §7.2).
    """
    transfer = float(row["transfer"].split()[2])          # "longest transfer 30 min"
    x = leg_features(transfer)
    # D95: "weather at the outdoor stops": mild and dry (baseline) / cold but dry / rainy
    weather = row["weather"]
    if weather.startswith("cold"):
        x["cold_outdoor"] = 1.0
    elif weather.startswith("rainy"):
        x["rain_outdoor"] = 1.0
    x["packed_pace"] = 1.0 if row["pace"].startswith("5 stops") else 0.0
    x["crowds"] = 1.0 if row["crowds"].startswith("busy") else 0.0
    x["cost_per_10gbp"] = float(row["cost"].lstrip("£").split()[0]) / 10.0
    x["long_walk"] = 1.0 if "8 km" in row["walking"] else 0.0
    return x
