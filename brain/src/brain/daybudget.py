"""m217 (Abram, 7 Nov): a day's money, honestly. Lunch is part of the person's budget by default and never disappears
silently; Tube and bus fares count towards the budget too; and when a day can't fit, the plan says why and what
could change.

- **Lunch is chosen to fit.** The usual lunch (a café, pub or stall: £15, a planning GUESS, D102), a cheaper lunch
  (a supermarket, bakery or market stall: £6, a GUESS) or bringing lunch (£0): the most comfortable one that still
  leaves room for getting around. These are planning figures, always labelled as estimates; never a named venue and
  never shown as a live price.
- **The person can leave food out of the budget** (`food_in_budget = False`): then the budget covers places and
  fares, and lunch is shown on its own line as "not in your budget".
- **One total.** The block's total is the plan's own total (`dayplan.plan_totals`), so the two never disagree.
"""

from __future__ import annotations

from dataclasses import dataclass

from .dayplan import TUBE_FARE_GBP, transport_gbp


@dataclass(frozen=True)
class Lunch:
    key: str
    gbp: float
    line: str          # what the plan says about it
    source: str        # where the figure comes from


LUNCHES = (
    Lunch("usual", 15.0, "Lunch at a café, pub or food stall", "ODYS's planning estimate (a guess, D102)"),
    Lunch("cheaper", 6.0, "A cheaper lunch: a supermarket, bakery or market stall", "ODYS's planning estimate (a guess)"),
    Lunch("own", 0.0, "Bring lunch, or buy it nearby", "nothing set aside"),
)


def lunch_of(gbp: float) -> Lunch:
    """The lunch a brief was planned with (by its cost)."""
    return next((lunch for lunch in LUNCHES if lunch.gbp == gbp), LUNCHES[0])


def choose_lunch(budget: float | None, food_in_budget: bool = True) -> Lunch:
    """The lunch to plan first: the most comfortable one the budget can cover on its own. If the finished day goes
    over, the plan steps down (`next_lunch`) rather than drop lunch."""
    if budget is None or not food_in_budget:
        return LUNCHES[0]
    return next(lunch for lunch in LUNCHES if lunch.gbp <= budget or lunch is LUNCHES[-1])


def next_lunch(lunch: Lunch) -> Lunch | None:
    """The next cheaper lunch, or None after "bring lunch"."""
    i = LUNCHES.index(lunch)
    return LUNCHES[i + 1] if i + 1 < len(LUNCHES) else None


def _money(x: float) -> str:
    return f"£{x:,.2f}" if round(x, 2) != int(x) else f"£{x:,.0f}"


def block(budget: float | None, stops: list[dict], lunch: Lunch, *, food_in_budget: bool = True,
          lunch_expected: bool = True) -> dict | None:
    """The plan's budget, line by line, with what's left and, if it doesn't fit, why and what could change.
    `stops` are the plan's stops (as `dayplan.personal_plan` gives them). None without a budget."""
    if budget is None:
        return None
    lunch_stop = next((s for s in stops if s.get("lunch")), None)
    lunch_cost = lunch_stop["cost_gbp"] if lunch_stop else 0.0
    if lunch_stop is not None and not food_in_budget and lunch_stop["moment_id"].startswith("lunch@"):
        lunch_cost = LUNCHES[0].gbp   # planned outside the budget (at £0 to the solver): shown as its usual estimate
    places = round(sum(s["cost_gbp"] for s in stops if not s.get("lunch") and not s.get("mine")), 2)
    fares = transport_gbp(stops)
    lines = []
    if lunch_stop is not None:
        is_card = not lunch_stop["moment_id"].startswith("lunch@")
        what = lunch_stop["title"] if is_card else lunch.line
        lines.append({"label": "Lunch", "gbp": round(lunch_cost, 2), "kind": "price" if is_card else "estimate",
                      "note": what if food_in_budget else f"{what}: not in your budget",
                      "in_budget": food_in_budget})
    elif lunch_expected:
        lines.append({"label": "Lunch", "gbp": None, "kind": "missing", "in_budget": food_in_budget,
                      "note": "There's no room for a lunch stop on this day, so eat before or after."})
    lines.append({"label": "Getting around", "gbp": fares, "kind": "estimate", "in_budget": True,
                  "note": "Tube and bus fares, at most the daily cap" if fares else "On foot"})
    lines.append({"label": "Places", "gbp": places, "kind": "price", "in_budget": True,
                  "note": "Entry and tickets, as each card shows" if places else "Free places"})
    total = round(places + fares + (lunch_cost if food_in_budget else 0.0), 2)
    left = round(budget - total, 2)
    status = "over" if left < 0 else "tight" if left < TUBE_FARE_GBP or lunch.key != "usual" else "fits"
    if status == "over":
        biggest = max((ln for ln in lines if ln["gbp"] and ln["in_budget"]), key=lambda ln: ln["gbp"])
        message = (f"This day comes to {_money(total)}, {_money(-left)} over your {_money(budget)}: "
                   f"most of it is {biggest['label'].lower()}.")
    elif status == "tight" and lunch.key != "usual":
        message = (f"Your budget is tight, so we've planned {'a cheaper lunch' if lunch.key == 'cheaper' else 'no paid lunch'}"
                   f" and kept to places that cost little.")
    elif status == "tight":
        message = f"This day fits your {_money(budget)}, with {_money(left)} to spare."
    else:
        message = f"This day fits your {_money(budget)}, with {_money(left)} left."
    options = []
    if status == "over" or lunch.key != "usual":
        if food_in_budget and lunch.key != "own":
            options.append("Bring lunch, or buy it from a supermarket or market")
        if fares:
            options.append("Places closer together, so fewer Tube or bus journeys")
        if places:
            options.append("Swap a paid place for a free one")
        options.append("Raise the day's budget")
        if food_in_budget:
            options.append("Leave food out of the budget")
    return {"budget_gbp": budget, "food_in_budget": food_in_budget, "lunch_choice": lunch.key, "lines": lines,
            "total_gbp": total, "left_gbp": left, "status": status, "message": message, "options": options,
            "note": "Lunch and fares are estimates; places are the prices on their cards."}
