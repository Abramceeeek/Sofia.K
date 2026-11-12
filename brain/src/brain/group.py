"""m240 (WS6, Global Destination Intelligence): a shared trip for several people, chosen so that it works for everyone
and no one person's tastes dominate. A prototype: no group accounts, nothing stored (Abram, m234).

**The inputs, per member:** their tastes (the same person model as everyone, so each has a chance of rating a stop
"Good" or better), a budget per day, the places they want ("must-sees") and the places they reject.

**Hard rules, never traded away:**
- **A place any member rejects is out.** A rejection is a veto, so nobody is taken somewhere they said no to.
- **The plan's cost per person fits the smallest budget,** day by day, so nobody is priced out.
- **Every member's first must-see is in,** where the days allow it (the rest as room allows, taking turns).

**The choice among the rest: Nash welfare on each member's satisfaction,** that is, the plan that maximises the sum of
the logs of each member's mean chance of "Good" or better. Logs make a gain matter more to whoever has least, so one
person can't take the whole trip: taking every stop for one member costs the others more than it gains. Two
alternatives are kept for comparison (`compare_group.py`):
- **average:** the sum of everyone's raw utilities. A member with strong tastes has big utilities and pulls the trip
  their way;
- **least misery:** the best plan for the least happy member, which can leave everyone lukewarm.

**Fairness is measured, not assumed** (Sato, "Enumerating Fair Packages for Group Recommendations", WSDM '22,
arXiv 2105.14423, read 10 Nov 2026):
- **proportionality:** a member "likes" a stop if it's in their own top 20% (Δ, a GUESS), and a plan is fair to them
  if it holds at least one they like;
- **envy-freeness:** a member is envy-free for a stop if their own fit for it is in the top 20% of the group's fits
  for it.

Sato also notes that a plan can be "fair" and still liked by nobody, which is why both satisfaction and fairness are
reported. **Each day's highlight takes turns** between members, so the shared itinerary says whose pick leads each day.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .catalogue import Experience
from .discovery import Scorer

DELTA = 0.2          # GUESS: "likes" = in the member's own top 20% (Sato's top-Δ%)
EPS = 1e-6
GOOD = 0.5           # quality.GOOD: below this for every place, nothing here is a good match for that member


@dataclass(frozen=True)
class Member:
    label: str                      # "Member A": never a name or anything about the person
    scorer: Scorer
    budget_per_day: float | None = None
    musts: tuple[str, ...] = ()     # experience ids, in the member's order
    rejects: tuple[str, ...] = ()
    needs_step_free: bool = False   # m250: a stated need, a hard rule; never inferred
    days_present: tuple[int, ...] | None = None   # m250: the days (1-based) the member is there; None = every day
    strict_access: bool = False     # m256: only places a source says are step-free (unknown access is left out)
    joins_first: dict[int, int] | None = None     # m256: day → how many of that day's stops they join (a later start
                                                  # or an earlier finish is the same count from the other end: GUESS)


@dataclass
class GroupPlan:
    days: list[list[Experience]]
    highlights: list[str]           # whose pick leads each day
    method: str
    satisfaction: dict[str, float]  # each member's mean chance of "Good" or better over the plan
    proportional: dict[str, bool]
    envy_free: dict[str, int]       # how many stops each member is envy-free for
    notes: list[str] = field(default_factory=list)

    @property
    def stops(self) -> list[Experience]:
        return [x for d in self.days for x in d]

    def fairness(self) -> dict:
        s = list(self.satisfaction.values())
        return {"min": min(s), "mean": sum(s) / len(s), "gap": max(s) - min(s),
                "proportional_share": sum(self.proportional.values()) / len(self.proportional)}


def _price(x: Experience, currency: str = "GBP", rates=None) -> float | None:
    """m255: the price per person in the budget's currency, or None when it isn't known or can't be converted (a
    missing or foreign price is never counted as free)."""
    if not x.price.known:
        return None
    m = x.price.value
    if m.currency == currency:
        return m.amount
    if rates is not None and m.currency in rates.per_eur and currency in rates.per_eur:
        return m.amount / rates.per_eur[m.currency] * rates.per_eur[currency]
    return None


def _objective(method: str, members: list[Member], chosen: list[Experience], P: dict, U: dict) -> float:
    if not chosen:
        return -math.inf
    if method == "average":
        return sum(U[(m.label, x.id)] for m in members for x in chosen)
    sats = [sum(P[(m.label, x.id)] for x in chosen) / len(chosen) for m in members]
    if method == "least_misery":
        return min(sats) + 1e-3 * sum(sats)          # ties broken by the others
    return sum(math.log(s + EPS) for s in sats)     # nash


def plan(members: list[Member], candidates: list[Experience], days: int, per_day: int,
         method: str = "nash", unknown_access: str = "flag", currency: str = "GBP", rates=None) -> GroupPlan:
    """The shared itinerary: `days` days of `per_day` stops. Greedy on the objective, then single swaps until nothing
    improves it; the hard rules hold throughout.

    m250: when a member needs step-free access, a place a source says isn't step-free is out (a hard rule). A place
    whose access is unknown stays in and is named in the notes (`unknown_access="flag"`), or is left out too
    (`"exclude"`): unknown is never read as "no", but the group can choose to be strict."""
    vetoed = {r for m in members for r in m.rejects}
    access = any(m.needs_step_free for m in members)
    strict = any(m.needs_step_free and m.strict_access for m in members) or unknown_access == "exclude"
    sf = lambda x: x.accessibility.step_free
    not_step_free = {x.id for x in candidates if access and sf(x).known and sf(x).value == "no"}
    unknown = {x.id for x in candidates if access and not sf(x).known}
    out_ids = vetoed | not_step_free | (unknown if strict else set())
    pool = [x for x in candidates if x.id not in out_ids]
    cap0 = min((m.budget_per_day for m in members if m.budget_per_day is not None), default=None)
    unpriced = [x for x in pool if _price(x, currency, rates) is None] if cap0 is not None else []
    if unpriced:          # m255: with a budget, a price that isn't known in the budget's currency can't be shown to fit
        pool = [x for x in pool if x not in unpriced]
    cap = min((m.budget_per_day for m in members if m.budget_per_day is not None), default=None)
    P = {(m.label, x.id): m.scorer.p_good(x) for m in members for x in pool}
    U = {(m.label, x.id): m.scorer.utility(x) for m in members for x in pool}
    n = days * per_day
    notes = []
    if vetoed & {x.id for x in candidates}:
        notes.append(f"{len(vetoed & {x.id for x in candidates})} place(s) left out because someone rejected them.")
    if not_step_free:
        notes.append(f"{len(not_step_free)} place(s) left out because their own sources say they aren't step-free: "
                     + "; ".join(x.title for x in candidates if x.id in not_step_free) + ".")
    if strict and unknown & {x.id for x in candidates}:
        notes.append(f"{len(unknown)} place(s) left out because no source confirms they're step-free (not because "
                     "they're known to have steps): " + "; ".join(x.title for x in candidates if x.id in unknown) + ".")
    if unpriced:
        notes.append(f"{len(unpriced)} place(s) left out because their price isn't known in {currency}, so they can't "
                     "be checked against the smallest budget: " + "; ".join(x.title for x in unpriced) + ".")
    for m in members:
        if pool and max(P[(m.label, x.id)] for x in pool) < GOOD:
            notes.append(f"Nothing here is a strong match for {m.label}: their satisfaction will be low whatever we "
                         "choose, so it's said rather than hidden.")
    def fits_budget(xs: list[Experience]) -> bool:   # the trip's cost per person within the smallest budget overall
        return cap is None or sum(_price(x, currency, rates) for x in xs) <= cap * days + 1e-9

    # must-sees: each member's first, then the rest in turns, while they fit the days and the smallest budget
    by_id = {x.id: x for x in pool}
    chosen: list[Experience] = []
    queues = [[i for i in m.musts if i in by_id] for m in members]
    for m in members:
        if any(i in vetoed for i in m.musts):
            notes.append(f"A must-see of {m.label} was rejected by someone else, so it's left out.")
    while any(queues) and len(chosen) < n:
        for m, q in zip(members, queues):
            while q and by_id[q[0]] in chosen:
                q.pop(0)
            if q and len(chosen) < n:
                x = by_id[q.pop(0)]
                if fits_budget(chosen + [x]):
                    chosen.append(x)
                else:
                    notes.append(f"{m.label}'s must-see {x.title} doesn't fit the smallest budget, so it's left for "
                                 "the group to decide.")
    fixed = list(chosen)

    rest = [x for x in pool if x not in chosen]
    while len(chosen) < n:
        best, best_v = None, -math.inf
        for x in rest:
            trial = chosen + [x]
            if not fits_budget(trial):
                continue
            v = _objective(method, members, trial, P, U)
            if v > best_v:
                best, best_v = x, v
        if best is None:
            notes.append("Not enough places fit everyone's budget and rejections to fill every slot.")
            break
        chosen.append(best)
        rest.remove(best)
    improved = True
    while improved:   # single swaps of the free choices
        improved = False
        base = _objective(method, members, chosen, P, U)
        for i, x in enumerate(chosen):
            if x in fixed:
                continue
            for y in rest:
                trial = chosen[:i] + [y] + chosen[i + 1:]
                if fits_budget(trial) and _objective(method, members, trial, P, U) > base + 1e-9:
                    rest.remove(y)
                    rest.append(x)
                    chosen = trial
                    improved = True
                    break
            if improved:
                break
    day_lists, highlights, over = _assign(chosen, members, days, per_day, P, cap,
                                          lambda x: _price(x, currency, rates) or 0.0)
    notes += over
    if access and not strict:
        flagged = [x.title for x in chosen if x.id in unknown]
        if flagged:
            notes.append(f"Step-free access isn't known for {len(flagged)} stop(s): check before going ("
                         + "; ".join(flagged) + ").")

    def seen(m: Member) -> list[Experience]:      # the stops on the days, and the part of each day, the member is there
        return [x for i, d in enumerate(day_lists, 1) if m.days_present is None or i in m.days_present
                for x in (d[:m.joins_first[i]] if m.joins_first and i in m.joins_first else d)]
    sats = {m.label: (sum(P[(m.label, x.id)] for x in seen(m)) / len(seen(m))) if seen(m) else 0.0 for m in members}
    _, envy = _fairness(members, pool, chosen, P)
    k = max(1, round(DELTA * len(pool)))
    favourites = {m.label: set(x.id for x in sorted(pool, key=lambda y: -P[(m.label, y.id)])[:k]) for m in members}
    prop = {m.label: any(x.id in favourites[m.label] for x in seen(m)) for m in members}   # only stops they're there for
    left_out = [m.label for m in members if not prop[m.label]]
    if left_out:          # m256: say the trade-off, and what would change it (Abram: "Do not hide this limitation")
        notes.append(f"{', '.join(left_out)} {'has' if len(left_out) == 1 else 'have'} none of their favourite places in "
                     f"this plan: {days * per_day} stops can't hold a favourite for all {len(members)} of you. To change "
                     "that: add a day or a stop, split up for one stop, or let them choose one stop.")
    return GroupPlan(day_lists, highlights, method, sats, prop, envy, notes)


def _assign(chosen: list[Experience], members: list[Member], days: int, per_day: int, P: dict,
            cap: float | None, price) -> tuple[list[list[Experience]], list[str], list[str]]:
    """Each day's highlight takes turns: day 1 leads with member A's favourite of what's left, day 2 with B's…, and
    each day's cost per person stays within the smallest budget where the stops allow it (said where it can't)."""
    left = list(chosen)
    out, leads, over, led = [], [], [], set()
    spend = lambda day: sum(price(x) for x in day)   # only known prices reach here when a cap is set
    fits = lambda day, x: cap is None or spend(day) + price(x) <= cap + 1e-9
    for d in range(days):
        if not left:
            break
        here = [o for o in members if o.days_present is None or d + 1 in o.days_present] or members
        # m250: a member who is only there some days leads one of them; otherwise turns go round the group
        short = [o for o in here if o.days_present is not None and o.label not in led]
        m = short[0] if short else here[d % len(here)]
        led.add(m.label)
        options = [x for x in left if fits([], x)] or left
        lead = max(options, key=lambda x: P[(m.label, x.id)])
        left.remove(lead)
        day = [lead]
        others = [o for o in here if o is not m] or [m]
        while len(day) < per_day and left:
            # the stop the day's other members like most, so each day has something for someone else too
            options = [x for x in left if fits(day, x)]
            if not options:
                break
            nxt = max(options, key=lambda x: sum(P[(o.label, x.id)] for o in others))
            left.remove(nxt)
            day.append(nxt)
        out.append(day)
        leads.append(f"Day {d + 1} leads with {m.label}'s pick: {lead.title}.")
    for x in left:   # what couldn't go in a day within the budget: the day with room and the least spent, and said
        day = min((dd for dd in out if len(dd) < per_day), key=spend, default=None) or min(out, key=spend)
        day.append(x)
    for i, day in enumerate(out):
        if cap is not None and spend(day) > cap + 1e-9:
            over.append(f"Day {i + 1} costs {spend(day):g} a person, over the smallest budget ({cap:g}).")
    return out, leads, over


def _fairness(members: list[Member], pool: list[Experience], chosen: list[Experience],
              P: dict) -> tuple[dict[str, bool], dict[str, int]]:
    prop, envy = {}, {}
    k = max(1, round(DELTA * len(pool)))
    for m in members:
        top = sorted(pool, key=lambda x: -P[(m.label, x.id)])[:k]
        prop[m.label] = any(x in top for x in chosen)
        envy[m.label] = 0
        for x in chosen:
            ranks = sorted((P[(o.label, x.id)] for o in members), reverse=True)
            cut = ranks[max(0, math.ceil(DELTA * len(members)) - 1)]
            envy[m.label] += P[(m.label, x.id)] >= cut
    return prop, envy
