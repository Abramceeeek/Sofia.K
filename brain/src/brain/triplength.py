"""m196 (6 Nov): "How long should I stay?" for a trip, from the person's own matches, not a rule of thumb.

The trip is built around the person's strong matches: places the rating model gives at least a 75% chance of "Good"
or better, the same test as "A strong match for you" on a stop (D127, `dayplan.match_label`). The good matches (50% to
75%) are what extra days add. A 50% bar alone was too low here: with no answers yet, 34 of the 39 checked London cards
pass it (they're hand-picked) and none is strong; for simulated people with real tastes, the median is about 10 strong
matches (0 to 32, 10th to 90th percentile; 6 Nov). The suggested length is the exploring days it takes to see the
strong matches at the person's places a day, keeping the day's shape (at most two history-and-culture stops a day,
D127; at most one wander, D72). Each length says what it covers, adds or leaves out, by name; extra days are offered
as choices (more good matches, a slower pace, a free day, a shopping day, something new), never filled for the sake of
it. Other places nearby come later (product direction, m196).

What it is and isn't (Abram, 6 Nov): an estimate of how much the checked catalogue holds for this person at their pace,
not a rule about how long to stay. The 75% line is the model's, awaiting validation against real ratings. It doesn't
yet check the days are feasible (travel between places, opening days, how long each takes, arriving and leaving): the
trip's days are planned by the day planner, which does. A later version should test the suggested length against
those plans.

Exploring days: a trip of n nights has n + 1 days, but the first and last are shortened by arriving and leaving, so
together they count as about one (GUESS), giving about n exploring days.
"""

from __future__ import annotations

import math
from collections.abc import Mapping

from .dayplan import MATCH_GOOD, MATCH_STRONG
from .features import Conditions, moment_features
from .moments import Moment
from .personal import DeltaPosterior
from .population import PopulationModel

MAX_DAYS = 14
HISTORY_PER_DAY = 2   # D127: at most two history-and-culture stops a day
# D116: the five shopping cards (their files say "a shopping moment"; the cards have no shopping tag of their own)
SHOPPING = frozenset({"m_burlington_arcade", "m_leadenhall_market", "m_liberty_timber_galleries",
                      "a_old_spitalfields_market", "a_portobello_saturday"})


def chance_good(pop: PopulationModel, u: float) -> float:
    """P(rating >= Good) for a card with utility u, as in `dayplan.match_label`."""
    c = pop.cutpoints["rating"][1]
    return 1.0 / (1.0 + math.exp(-(pop.scales["rating"] * u - c)))


def ranked(pop: PopulationModel, post: DeltaPosterior, moments: list[Moment], *, asp: Mapping[str, float],
           skip: set[str]) -> list[tuple[Moment, float]]:
    """The person's plannable cards, best first, with their chance of "Good"; one per day/night pair (the better)."""
    b = pop.b_person(post.mean)
    cond = Conditions(None, None)
    best: dict[str, tuple[Moment, float, float]] = {}
    for m in moments:
        if not m.plannable() or m.id in skip:
            continue
        u = float(pop.vector(moment_features(m, cond, aspiration_match=asp.get(m.id, 0.0))) @ b)
        key = m.variant_of or m.id
        if key not in best or u > best[key][2]:
            best[key] = (m, chance_good(pop, u), u)
    return [(m, p) for m, p, _ in sorted(best.values(), key=lambda x: -x[2])]


def days_for(cards: list[Moment], per_day: int) -> int:
    """Exploring days to see these cards at `per_day` places a day, keeping the day's shape."""
    if not cards:
        return 0
    history = sum((m.tag("history_culture") or 0) >= 2 for m in cards)
    wanders = sum(m.kind == "area" for m in cards)
    return max(math.ceil(len(cards) / per_day), math.ceil(history / HISTORY_PER_DAY), wanders)


def _a_day(n: int) -> str:
    return f"{n} place a day" if n == 1 else f"about {n} places a day"


def _names(cards: list[Moment], n: int = 3, seen: set[str] | None = None) -> str:
    """"A, B and 4 more". With `seen`, places the page hasn't named yet come first, so its lines don't repeat."""
    if seen is not None:
        cards = [m for m in cards if m.id not in seen] + [m for m in cards if m.id in seen]
        seen.update(m.id for m in cards[:n])
    titles = [m.title.split(":")[0] for m in cards[:n]]
    more = len(cards) - len(titles)
    return ", ".join(titles) + (f" and {more} more" if more > 0 else "")


def _covered(good: list[Moment], days: int, per_day: int) -> int:
    """How many of the best good matches fit in `days` (the largest prefix whose day count fits)."""
    k = min(len(good), days * per_day)
    while k > 0 and days_for(good[:k], per_day) > days:
        k -= 1
    return k


def suggest(pop: PopulationModel, post: DeltaPosterior, moments: list[Moment], *, asp: Mapping[str, float],
            skip: set[str], per_day: int, nights: int | None, place: str) -> dict:
    cards = ranked(pop, post, moments, asp=asp, skip=skip)
    strong = [m for m, p in cards if p >= MATCH_STRONG]
    good = [m for m, p in cards if MATCH_GOOD <= p < MATCH_STRONG]
    rest = [m for m, p in cards if p < MATCH_GOOD]
    # the trip is built around the strong matches; the good ones are what extra days add. With too few strong ones
    # (no answers yet, or tastes the cards don't suit), the best few days' worth of good ones stand in
    core = strong if len(strong) >= per_day else (strong + good)[:per_day * 3]
    more = [m for m in good if m not in core]
    need = max(1, min(MAX_DAYS, days_for(core, per_day)))
    yours = max(1, nights) if nights is not None else None
    days = lambda n: f"{n} day{'s' if n != 1 else ''}"

    # Abram, 6 Nov: an estimate of how much there is for this person, never a rule about how long to stay
    if len(strong) >= per_day:
        why = (f"Based on your current preferences, we've found {len(strong)} places in {place} that are "
               f"particularly well suited to you." + (f" {len(more)} more are likely to be good too." if more else ""))
    else:
        why = (f"No place in {place} stands out strongly for you yet, so this uses your best {len(core)} for now. "
               f"Rating the places you visit makes it sharper.")
    note = (f"Based on the {len(cards)} places we've checked in {place} so far, your preferences, and "
            f"{_a_day(per_day)}. It's an estimate of how much there is for you, not a limit on how long to stay.")

    lengths = sorted({max(1, need - 2), need, min(MAX_DAYS, need + 2)} | ({min(MAX_DAYS, yours)} if yours else set()))
    options = []
    seen: set[str] = set()   # the places already named on the page
    for d in lengths:
        k = _covered(core, d, per_day)
        missed = core[k:]
        added = more[:max(0, _covered(core + more, d, per_day) - len(core))] if d > need else []
        if d < need:
            label, line = "Highlights", (f"Your {k} best, at {_a_day(per_day)}. You'd leave out {len(missed)}: "
                                         f"{_names(missed, seen=seen)}.")
        elif d == need:
            label, line = "Suggested for you", f"All {len(core)} of your best, at {_a_day(per_day)}."
        elif added:
            label, line = "More time", (f"All {len(core)} of your best, plus {len(added)} more you'd likely enjoy, "
                                        f"such as {_names(added, 2, seen)}.")
        else:
            label, line = "More time", (f"All {len(core)} of your best at {_a_day(math.ceil(len(core) / d))}, with "
                                        f"{days(d - need)} to spare for what you choose.")
        options.append({"days": d, "label": label, "line": line, "covers": k, "of": len(core),
                        "adds": [m.id for m in added], "leaves_out": [m.id for m in missed],
                        "yours": d == yours, "suggested": d == need})

    extra = []
    if yours and yours > need:
        spare = yours - need
        if more:
            extra.append({"kind": "more", "title": "See more you'd likely enjoy",
                          "line": f"{len(more)} more good matches, such as {_names(more, 2, seen)}."})
        extra.append({"kind": "slower", "title": "Take it slower",
                      "line": f"Your best places spread out: {_a_day(math.ceil(len(core) / yours))}, "
                              f"with longer at each."})
        extra.append({"kind": "free", "title": f"Keep {'a day' if spare == 1 else 'days'} free",
                      "line": "No plan: rest, meet someone, or wander."})
        shops = [m for m, _ in cards if m.id in SHOPPING and m not in core]
        if shops:
            extra.append({"kind": "shopping", "title": "A shopping day", "line": f"Such as {_names(shops, 2, seen)}."})
        if rest:
            extra.append({"kind": "try", "title": "Try something new",
                          "line": f"Places that are worth a try for you, such as {_names(rest, 2, seen)}."})

    short = None
    if yours and yours < need:
        k = _covered(core, yours, per_day)
        short = f"In {days(yours)} you'd see {k} of your {len(core)} best. {days(need).capitalize()} would cover them all."
    return {"place": place, "strong_matches": len(strong), "good_matches": len(good), "checked": len(cards),
            # m219: what the suggestion is built on (the strong matches, or the best few days' worth standing in)
            "best": len(core), "capped": days_for(core, per_day) > MAX_DAYS,
            "places_per_day": per_day, "suggested_days": need, "your_days": yours,
            "spare_days": max(0, yours - need) if yours else None, "headline": f"Around {days(need)}",
            "why": why, "note": note, "short": short,
            "options": options, "extra": extra}
