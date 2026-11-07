"""WS6 (m212): the whole trip's cost, honestly (decisions/full-trip-budget.md). Not wired into the API or the apps yet.

Every line says what it is: **confirmed** (booked and paid or owed), a **current quote** (a price a search shows now),
an **estimate** (our planning figure, with its source), **optional** (only if the person adds it) or **unknown** (not
priced yet). An incomplete total is never called "the total": it's "at least £X so far", with what's missing named.
A line in another currency is converted only with a dated rate given to it, and then marked as converted; without one
it's shown in its own currency, apart from the pounds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Category = Literal["flights", "trains", "buses", "car", "accommodation", "local_transport", "food", "attractions",
                   "experiences", "shopping", "other"]
Status = Literal["confirmed", "quote", "estimate", "optional", "unknown"]
STATUS_ORDER = ("confirmed", "quote", "estimate")
# what any trip needs priced before its total can be called complete (getting there is checked separately)
NEEDED = ("accommodation", "local_transport", "food")
GETTING_THERE = ("flights", "trains", "buses", "car")


@dataclass(frozen=True)
class Line:
    category: Category
    label: str
    amount: float | None            # None only when unknown
    currency: str | None
    status: Status
    per: Literal["person", "group"] = "group"
    source: str = ""                # where the figure comes from (a booking, a search, TfL's fares, a GUESS)

    def __post_init__(self):
        if (self.amount is None) != (self.status == "unknown"):
            raise ValueError(f"{self.label}: an amount, unless it's unknown")
        if self.amount is not None and (self.amount < 0 or not self.currency):
            raise ValueError(f"{self.label}: a non-negative amount and its currency")


@dataclass(frozen=True)
class Rate:
    to_home: float                  # 1 unit of the other currency in the home currency
    source: str
    as_of: str                      # ISO date: a rate is only ever as good as its date


@dataclass
class Summary:
    people: int
    currency: str
    known: float                    # confirmed + quotes + estimates, in the home currency, for the group
    by_status: dict[str, float]
    optional: float
    not_converted: dict[str, float] = field(default_factory=dict)   # currency → amount, kept apart
    missing: list[str] = field(default_factory=list)                # what isn't priced, in words
    converted: list[str] = field(default_factory=list)              # which lines used a rate, with its date

    @property
    def complete(self) -> bool:
        return not self.missing and not self.not_converted

    def money(self, x: float) -> str:
        return f"£{x:,.0f}" if self.currency == "GBP" else f"{x:,.0f} {self.currency}"

    def headline(self) -> str:
        each = self.known / max(self.people, 1)
        who = f" for {self.people} people ({self.money(each)} each)" if self.people > 1 else ""
        if self.complete:
            return f"About {self.money(self.known)}{who}, everything priced."
        return f"At least {self.money(self.known)} so far{who}: not everything is priced yet."

    def lines(self) -> list[str]:
        out = [self.headline()]
        if self.missing:
            out.append("Not priced yet: " + "; ".join(self.missing) + ".")
        for cur, amt in self.not_converted.items():
            out.append(f"Plus {amt:,.0f} {cur}, not converted (no exchange rate set).")
        if self.converted:
            out.append("Converted at: " + "; ".join(self.converted) + ".")
        if self.optional:
            out.append(f"Optional, not included: up to {self.money(self.optional)} if you add them.")
        parts = [f"{s} {self.money(self.by_status[s])}" for s in STATUS_ORDER if self.by_status.get(s)]
        if parts:
            out.append("Of which " + ", ".join(parts) + ".")
        return out


def _group(line: Line, people: int) -> float:
    return (line.amount or 0.0) * (people if line.per == "person" else 1)


def summarise(lines: list[Line], people: int, currency: str = "GBP", rates: dict[str, Rate] | None = None) -> Summary:
    rates = rates or {}
    s = Summary(people, currency, 0.0, {k: 0.0 for k in STATUS_ORDER}, 0.0)
    for ln in lines:
        if ln.status == "unknown":
            s.missing.append(ln.label)
            continue
        amt = _group(ln, people)
        if ln.currency != currency:
            r = rates.get(ln.currency)
            if r is None:
                if ln.status != "optional":
                    s.not_converted[ln.currency] = s.not_converted.get(ln.currency, 0.0) + amt
                continue
            amt = amt * r.to_home
            s.converted.append(f"{ln.label}, {ln.currency} at {r.to_home:g} ({r.source}, {r.as_of})")
        if ln.status == "optional":
            s.optional += amt
        else:
            s.known += amt
            s.by_status[ln.status] += amt
    cats = {ln.category for ln in lines if ln.status != "optional"}
    for c in NEEDED:
        if c not in cats:
            s.missing.append({"accommodation": "where you'll stay", "local_transport": "getting around",
                              "food": "food"}[c])
    if not cats & set(GETTING_THERE):
        s.missing.append("getting there and back")
    s.known, s.optional = round(s.known, 2), round(s.optional, 2)
    s.by_status = {k: round(v, 2) for k, v in s.by_status.items()}
    return s


def against(s: Summary, budget: float) -> str:
    """The trip against the person's budget, never more certain than the summary."""
    gap = budget - s.known
    tail = "" if s.complete else ", before what isn't priced yet"
    if gap >= 0:
        return f"{s.money(gap)} under your {s.money(budget)}{tail}."
    return f"{s.money(-gap)} over your {s.money(budget)}{tail}."


def levers(lines: list[Line], people: int, s: Summary, budget: float) -> list[str]:
    """Where the money could move, largest first, using only the figures already here: confirmed costs are fixed;
    quotes and estimates can change; optional items are already left out. Never an invented cheaper price."""
    over = s.known - budget
    if over <= 0:
        return []
    out = []
    movable = sorted((ln for ln in lines if ln.status in ("quote", "estimate") and ln.currency == s.currency),
                     key=lambda ln: _group(ln, people), reverse=True)
    for ln in movable:
        amt = _group(ln, people)
        what = "a price found now: other dates or options may differ" if ln.status == "quote" else \
            "our estimate: your own choices set it"
        out.append(f"{ln.label}: {s.money(amt)} ({what}).")
    fixed = sum(_group(ln, people) for ln in lines if ln.status == "confirmed" and ln.currency == s.currency)
    if fixed > budget:
        out.insert(0, f"What's already booked ({s.money(fixed)}) is more than the budget on its own.")
    return out
