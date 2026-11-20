"""WS4 (m209): ways of looking at a few stays for one trip, each a separate question with its own answer
(decisions/accommodation-ranking.md). Never one blended score, and never a quality rating we made up: stars and
guests' scores are the provider's, shown as theirs, and nothing here ranks by them.

- **Cheapest overall:** the lowest whole cost (the total plus anything paid at the property), only among stays priced
  in the same currency.
- **Closest to your days:** the least time from the stay to each planned day's first place and back from its last.
- **Most flexible:** free cancellation, as the provider shows it; the cheapest of those.
- **The trade-offs:** the stays no other one beats on both cost and travel (the Pareto set), each said in plain terms
  against the cheapest: "£40 more than the cheapest, and 25 min less travel a day". The person weighs time against
  money; ODYS doesn't put a price on their time (the model's cost weight is far too uncertain for that, D127).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .stayprices import StayTerms


@dataclass(frozen=True)
class StayOption:
    stay: StayTerms
    fit: dict           # stayprices.trip_fit for this stay: "days" rows with to_first and back

    @property
    def whole(self) -> float:
        return round(self.stay.price_total + self.stay.pay_there, 2)

    @property
    def travel_a_day(self) -> float | None:
        """Minutes a typical day, there and back, as trip_fit counts them (arrival and leaving days have one leg).
        None when no day is planned yet."""
        if self.fit.get("to_first") is None and self.fit.get("back") is None:
            return None
        return float((self.fit.get("to_first") or 0) + (self.fit.get("back") or 0))


def _money(x: float, currency: str) -> str:
    n = f"{x:,.2f}" if x < 100 and round(x, 2) != int(x) else f"{x:,.0f}"
    return f"£{n}" if currency == "GBP" else f"{n} {currency}" if currency else f"{n} (currency not given)"


def lenses(options: list[StayOption]) -> dict:
    """Each lens's answer (a stay id, or None with the reason) and one line per stay saying where it stands."""
    if not options:
        return {"cheapest": None, "closest": None, "flexible": None, "tradeoffs": [], "lines": {}, "note": ""}
    currency = Counter(o.stay.currency for o in options).most_common(1)[0][0]
    same = [o for o in options if o.stay.currency == currency]
    apart = [o.stay.id for o in options if o.stay.currency != currency]
    cheapest = min(same, key=lambda o: (o.whole, o.stay.id))
    located = [o for o in same if o.travel_a_day is not None]
    closest = min(located, key=lambda o: (o.travel_a_day, o.whole, o.stay.id)) if located else None
    free = [o for o in same if o.stay.refundable is True]
    flexible = min(free, key=lambda o: (o.whole, o.stay.id)) if free else None
    # the Pareto set on (whole cost, travel a day): no other stay is at least as good on both and better on one
    front = [o for o in located if not any(p.whole <= o.whole and p.travel_a_day <= o.travel_a_day
                                           and (p.whole < o.whole or p.travel_a_day < o.travel_a_day) for p in located)]
    front.sort(key=lambda o: (o.whole, o.stay.id))
    lines: dict[str, list[str]] = {}
    for o in same:
        ls = []
        if o is cheapest:
            ls.append(f"Cheapest of these: {_money(o.whole, currency)} for {o.stay.nights} night"
                      f"{'s' if o.stay.nights != 1 else ''}" + (f", including {_money(o.stay.pay_there, currency)} "
                                                                 f"paid at the property." if o.stay.pay_there else "."))
        else:
            more = o.whole - cheapest.whole
            ls.append(f"{_money(more, currency)} more than the cheapest." if more > 0 else
                      "The same price as the cheapest.")
        if o.travel_a_day is None:
            ls.append("How far it is from your days: plan your days first.")
        elif closest is not None and o is closest:
            ls.append(f"Closest to your days: about {round(o.travel_a_day)} min a day there and back.")
        elif closest is not None:
            ls.append(f"About {round(o.travel_a_day - closest.travel_a_day)} min a day more travel than the closest.")
        ls.append("Free cancellation, as found." if o.stay.refundable else
                  "Non-refundable, as found." if o.stay.refundable is False else "Cancellation terms not given.")
        lines[o.stay.id] = ls
    tradeoffs = []
    for o in front:
        if o is front[0]:
            tradeoffs.append({"id": o.stay.id, "line": "The cheapest that isn't beaten on travel."})
            continue
        saved = front[0].travel_a_day - o.travel_a_day
        tradeoffs.append({"id": o.stay.id, "line": f"{_money(o.whole - front[0].whole, currency)} more, and about "
                                                   f"{round(saved)} min less travel a day."})
    note = (f"{len(apart)} stay{'s' if len(apart) != 1 else ''} priced in another currency "
            f"{'aren' if len(apart) != 1 else 'isn'}'t compared." if apart else "")
    return {"cheapest": cheapest.stay.id, "closest": closest.stay.id if closest else None,
            "flexible": flexible.stay.id if flexible else None,
            "flexible_note": "" if flexible else "None of these has free cancellation, as found.",
            "tradeoffs": tradeoffs, "lines": lines, "note": note, "currency": currency}
