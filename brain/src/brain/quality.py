"""m239: the ODYS quality standard (Abram, m234), in code. Every recommendation is judged from four perspectives, and a
place doesn't rank highly just because the person might like it:

1. **Personal relevance:** will this person enjoy it? (the rating model's chance of "Good" or better)
2. **Practicality:** can they do it at this time and place? (open that day, fits the time they have, a sane journey)
3. **Financial suitability:** does it fit what they have left to spend? (and is the price known)
4. **Trustworthiness:** are the facts verified well enough? (checked recently, hours and price known, a real source)

Each perspective gets a level, `good`, `fair`, `poor` or `unknown`, and one plain reason. **Ranking:** anything with
a `poor` perspective comes after everything without one, whatever its relevance; then fewer `fair`s, then relevance.
So a strong match that's closed today, over budget or unverified never outranks a sound one.

Thresholds are GUESSES, stated here, until real ratings say otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .catalogue import Experience
from .moments import WEEKDAYS

STRONG, GOOD = 0.75, 0.5          # the match words' own lines (dayplan.MATCH_STRONG, MATCH_GOOD)
LONG_TRIP_MIN = 45                # GUESS: a journey over this is "fair" (the planner's penalties start at 15 and 30)
STALE_DAYS, OLD_DAYS = 180, 365   # GUESS: facts checked longer ago than this are "fair", then "poor"
SYNTHETIC = ("synthetic",)        # a source that is test data is never trustworthy enough to recommend


@dataclass(frozen=True)
class Perspective:
    level: str                    # good | fair | poor | unknown
    reason: str


@dataclass(frozen=True)
class Assessment:
    relevance: Perspective
    practicality: Perspective
    money: Perspective
    trust: Perspective
    p_good: float | None

    def levels(self) -> list[str]:
        return [self.relevance.level, self.practicality.level, self.money.level, self.trust.level]

    @property
    def recommendable(self) -> bool:
        return "poor" not in self.levels()

    def rank_key(self) -> tuple:
        """Lower sorts first: nothing poor, then fewer fairs, then the most relevant."""
        lv = self.levels()
        return ("poor" in lv, lv.count("fair") + lv.count("unknown"), -(self.p_good or 0.0))

    def out(self) -> dict:
        return {k: {"level": v.level, "reason": v.reason} for k, v in
                (("relevance", self.relevance), ("practicality", self.practicality), ("money", self.money),
                 ("trust", self.trust))}


def relevance(p_good: float | None) -> Perspective:
    if p_good is None:
        return Perspective("unknown", "We don't know enough about you yet.")
    if p_good >= STRONG:
        return Perspective("good", "A strong match for you.")
    if p_good >= GOOD:
        return Perspective("good", "A good match for you.")
    return Perspective("fair", "Worth a try, but not one of your strongest matches.")


def practicality(x: Experience, day: date | None, minutes_free: float | None, travel_min: float | None) -> Perspective:
    if day is not None:
        wd = WEEKDAYS[day.weekday()]
        if x.hours.open_on(wd) is False:
            return Perspective("poor", f"Closed on {day:%A}s.")
    need = (x.duration.max_minutes if x.duration else 0) + (travel_min or 0)
    if minutes_free is not None and need > minutes_free:
        return Perspective("poor", f"Needs about {round(need)} min, and you have {round(minutes_free)}.")
    if travel_min is not None and travel_min > LONG_TRIP_MIN:
        return Perspective("fair", f"{round(travel_min)} min to get there.")
    if x.hours.weekly is None and x.hours.trust != "unknown":
        return Perspective("fair", "Its hours vary, so check them on the day.")
    if x.hours.trust == "unknown":
        return Perspective("fair", "Its opening hours aren't known.")
    return Perspective("good", "Open then, and it fits your time.")


def money(x: Experience, budget_left: float | None, currency: str | None = None) -> Perspective:
    if not x.price.known:
        return Perspective("fair", "Its price isn't known.")
    m = x.price.value
    if currency and m.currency != currency:
        return Perspective("fair", f"Priced in {m.currency}, not your budget's {currency}.")
    if budget_left is not None and m.amount > budget_left:
        return Perspective("poor", f"About {m.amount:g} {m.currency}, more than the {budget_left:g} you have left.")
    if m.amount == 0:
        return Perspective("good", "Free.")
    if x.price.trust == "estimated":
        return Perspective("fair", f"About {m.amount:g} {m.currency}, an estimate.")
    return Perspective("good", f"{m.amount:g} {m.currency}, within your budget." if budget_left is not None
                       else f"{m.amount:g} {m.currency}.")


def trust(x: Experience, today: date) -> Perspective:
    src = (x.provenance.source or "").lower()
    if any(s in src for s in SYNTHETIC):
        return Perspective("poor", "Test data, not a checked place.")
    if not x.provenance.checked:
        return Perspective("poor", "Never checked.")
    age = (today - date.fromisoformat(x.provenance.checked[:10])).days
    if age > OLD_DAYS:
        return Perspective("poor", f"Last checked {age} days ago.")
    if age > STALE_DAYS:
        return Perspective("fair", f"Last checked {age} days ago: worth checking again.")
    unknown = [k for k, f in (("hours", x.hours.trust), ("price", x.price.trust)) if f == "unknown"]
    if unknown:
        return Perspective("fair", f"Checked, but its {' and '.join(unknown)} aren't known.")
    return Perspective("good", f"Checked on {x.provenance.checked[:10]}.")


def assess(x: Experience, *, p_good: float | None, today: date, day: date | None = None,
           minutes_free: float | None = None, travel_min: float | None = None, budget_left: float | None = None,
           currency: str | None = None) -> Assessment:
    return Assessment(relevance(p_good), practicality(x, day, minutes_free, travel_min),
                      money(x, budget_left, currency), trust(x, today), p_good)


def rank(items: list[tuple[object, Assessment]]) -> list[tuple[object, Assessment]]:
    """The quality rule: nothing with a poor perspective above anything without one, then fewer doubts, then the
    strongest match."""
    return sorted(items, key=lambda t: t[1].rank_key())
