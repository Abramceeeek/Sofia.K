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

from dataclasses import dataclass, field
from datetime import date

from .catalogue import _SEASONAL, Experience
from .moments import WEEKDAYS

STRONG, GOOD = 0.75, 0.5          # the match words' own lines (dayplan.MATCH_STRONG, MATCH_GOOD)
LONG_TRIP_MIN = 45                # GUESS: a journey over this is "fair" (the planner's penalties start at 15 and 30)
STALE_DAYS, OLD_DAYS = 180, 365   # GUESS: facts checked longer ago than this are "fair", then "poor"
SYNTHETIC = ("synthetic",)        # a source that is test data is never trustworthy enough to recommend


@dataclass(frozen=True)
class Perspective:
    level: str                    # good | fair | poor | unknown
    reason: str


# ---- m254: calibrated uncertainty (Abram, m252) ---------------------------------------------------------------------
# What a missing fact risks depends on what it is and how it's used. Each value is the chance (GUESS) that the gap spoils
# the visit as planned; they're one table so real outcomes can calibrate them (evaluation.py, after the round).
RISK = {
    "hours_unknown_on_day": 0.30,     # planned for a known day and its hours aren't known at all
    "hours_text_on_day": 0.08,        # hours known only as text (seasonal, conflicting, "dusk") on a known day
    "hours_unknown": 0.10,            # browsing with no day yet
    "hours_text": 0.02,
    "season_outdoor_winter": 0.10,    # outdoor, November to March, and no seasonal information at all
    "season_outdoor": 0.03,
    "price_unknown_budget": 0.15,     # a budget is set and the price isn't known
    "price_unknown": 0.10,            # m254: 0.03 left a third of Paris's top 5 unpriced (benchmark_ranking.py)
    "price_estimate": 0.02,
    "access_unknown_need": 0.50,      # step-free needed (not strictly) and access isn't known
    "area_unknown": 0.01,             # where it is, roughly: a small confidence cost
    "stale": 0.10,                    # facts checked 180 to 365 days ago
}
OUTDOOR = ("nature", "views", "neighbourhood")
WINTER = (11, 12, 1, 2, 3)


@dataclass(frozen=True)
class Risk:
    field: str                    # which fact is missing or uncertain
    dimension: str                # the perspective it bears on: practicality | money | trust
    p: float                      # the chance it spoils the visit as planned (RISK)
    reason: str


def uncertainties(x: Experience, *, today: date, day: date | None = None, budget_left: float | None = None,
                  needs_step_free: bool = False) -> tuple[Risk, ...]:
    """Each gap that matters for this use, with its dimension and its risk. A gap that doesn't bear on the use (access
    for someone with no step-free need, a missing description) costs nothing. Unknown is never read as good."""
    out = []
    event = getattr(x.facet, "event_based", False)
    if not event:
        if x.hours.trust == "unknown" or not x.hours.text:
            k = "hours_unknown_on_day" if day else "hours_unknown"
            out.append(Risk("hours", "practicality", RISK[k], "Opening hours aren't known."))
        elif x.hours.weekly is None:
            k = "hours_text_on_day" if day else "hours_text"
            out.append(Risk("hours", "practicality", RISK[k], "Hours vary: check them for the day."))
    if x.category in OUTDOOR and not x.notices and not _SEASONAL.search((x.hours.text or "").lower()):
        winter = (day or today).month in WINTER
        out.append(Risk("season", "practicality", RISK["season_outdoor_winter" if winter else "season_outdoor"],
                        "No seasonal information for an outdoor place."))
    if not x.price.known:
        out.append(Risk("price", "money", RISK["price_unknown_budget" if budget_left is not None else "price_unknown"],
                        "The price isn't known."))
    elif x.price.trust == "estimated":
        out.append(Risk("price", "money", RISK["price_estimate"], "The price is an estimate."))
    if needs_step_free and not x.accessibility.step_free.known:
        out.append(Risk("access", "practicality", RISK["access_unknown_need"], "Step-free access isn't verified."))
    if not x.geo.area.known and not x.district.known:
        out.append(Risk("area", "trust", RISK["area_unknown"], "Its neighbourhood isn't named by a source."))
    if x.provenance.checked:
        age = (today - date.fromisoformat(x.provenance.checked[:10])).days
        if STALE_DAYS < age <= OLD_DAYS:
            out.append(Risk("freshness", "trust", RISK["stale"], f"Last checked {age} days ago."))
    return tuple(out)


@dataclass(frozen=True)
class Assessment:
    relevance: Perspective
    practicality: Perspective
    money: Perspective
    trust: Perspective
    p_good: float | None
    risks: tuple[Risk, ...] = field(default=())   # m254: what's uncertain, for this use

    @property
    def confidence(self) -> float:
        """The chance none of the gaps spoils the visit as planned (independent risks)."""
        c = 1.0
        for r in self.risks:
            c *= 1 - r.p
        return c

    @property
    def expected(self) -> float:
        """The expected chance of a good visit that happens as planned: the match, discounted by the gaps."""
        return (self.p_good or 0.0) * self.confidence

    def levels(self) -> list[str]:
        return [self.relevance.level, self.practicality.level, self.money.level, self.trust.level]

    @property
    def recommendable(self) -> bool:
        return "poor" not in self.levels()

    def rank_key(self, doubt_cost: float | None = None, calibrated: bool = False) -> tuple:
        """Lower sorts first: nothing poor, then fewer fairs, then the most relevant.

        m249: with `doubt_cost`, each doubt (a fair or unknown practicality, money or trust) costs that much chance of
        "Good" instead of coming first, so a strong match with one open question can outrank a weak match with none.
        The benchmark (scripts/benchmark_profiles.py) compares the two; Abram chooses."""
        lv = self.levels()
        if calibrated:              # m254: hard failures last; then the expected chance of a good visit
            return ("poor" in lv, -self.expected)
        if doubt_cost is None:
            return ("poor" in lv, lv.count("fair") + lv.count("unknown"), -(self.p_good or 0.0))
        doubts = sum(1 for v in lv[1:] if v in ("fair", "unknown"))
        return ("poor" in lv, -((self.p_good or 0.0) - doubt_cost * doubts))

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


def practicality(x: Experience, day: date | None, minutes_free: float | None, travel_min: float | None,
                 needs_step_free: bool = False, strict_access: bool = False) -> Perspective:
    if needs_step_free:                       # m249: a stated need is a rule; unknown access is never read as "no"
        sf = x.accessibility.step_free
        if sf.known and sf.value == "no":
            return Perspective("poor", "Not step-free" + (f": {x.accessibility.note}" if x.accessibility.note else "."))
        if strict_access and not (sf.known and sf.value == "yes"):   # m254: strict means verified step-free only
            return Perspective("poor", "Step-free access isn't verified" if not sf.known else
                               "Only partly step-free" + (f": {x.accessibility.note}" if x.accessibility.note else "."))
    if day is not None:
        wd = WEEKDAYS[day.weekday()]
        if x.hours.open_on(wd) is False:
            return Perspective("poor", f"Closed on {day:%A}s.")
        for n in x.notices_on(day.isoformat()):   # m245: a dated closure or change, from the source
            if n.what.lower().startswith("closed"):
                return Perspective("poor", f"{n.what} that day.")
        notice = next(iter(x.notices_on(day.isoformat())), None)
    else:
        notice = None
    need = (x.duration.max_minutes if x.duration else 0) + (travel_min or 0)
    if minutes_free is not None and need > minutes_free:
        return Perspective("poor", f"Needs about {round(need)} min, and you have {round(minutes_free)}.")
    if travel_min is not None and travel_min > LONG_TRIP_MIN:
        return Perspective("fair", f"{round(travel_min)} min to get there.")
    if needs_step_free and not x.accessibility.step_free.known:
        return Perspective("fair", "Step-free access isn't known: check before you go.")
    if needs_step_free and x.accessibility.step_free.value == "partial":
        return Perspective("fair", "Partly step-free" + (f": {x.accessibility.note}" if x.accessibility.note else "."))
    if notice is not None:
        return Perspective("fair", f"That day: {notice.what}.")
    if getattr(x.facet, "event_based", False):
        return Perspective("fair", "Sessions are listed per event: check the calendar.")
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
           currency: str | None = None, needs_step_free: bool = False, strict_access: bool = False) -> Assessment:
    return Assessment(relevance(p_good), practicality(x, day, minutes_free, travel_min, needs_step_free, strict_access),
                      money(x, budget_left, currency), trust(x, today), p_good,
                      uncertainties(x, today=today, day=day, budget_left=budget_left, needs_step_free=needs_step_free))


def rank(items: list[tuple[object, Assessment]], doubt_cost: float | None = None,
         calibrated: bool = False) -> list[tuple[object, Assessment]]:
    """The quality rule: nothing with a poor perspective above anything without one, then fewer doubts, then the
    strongest match (or, with `doubt_cost`, the match less a cost per doubt: m249; or, `calibrated`, the expected
    chance of a good visit given what's uncertain for this use: m254). The default is unchanged (Abram, m252)."""
    return sorted(items, key=lambda t: t[1].rank_key(doubt_cost, calibrated))
