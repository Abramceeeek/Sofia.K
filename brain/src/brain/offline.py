"""m221: the offline companion's reference rules (a proof of concept, tested here, for both apps to follow).

What both phones keep today (m221 audit, decisions/offline-companion.md):
- the plan, its request, the trips (with each day's plan and the chosen flight and stay) and unsent ratings, as JSON
  files in the app's own storage;
- Help & safety's 999, NHS 111 and Samaritans lines, bundled in the app.

Ratings made with no signal are already kept and sent later. What's missing is one place that says what the person
needs on the day, **in priority order** (the itinerary, the stay, the journey, emergency help), and **how fresh each
part is**. A plan or a fare can go stale without the phone knowing.

The pack is built **on the phone** from what the phone already has. Nothing new is stored on the server, and nothing
is fetched to build it. Each item carries:
- where it came from;
- when it was saved;
- a status: current, check, expired or past;
- the one action to take when it isn't current.

Missing data is said ("not saved"), never filled in. A trip's offline copy is deleted 30 days after its last day
(GUESS, for Abram), and at once with "Delete my data".
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta

SECTIONS = ("itinerary", "stay", "travel", "emergency")   # Abram's order: the saved itinerary first
CARD_CHECK_DAYS = 90       # GUESS: a card's facts (hours, prices) older than this say "check on the day"
PLAN_STALE_DAYS = 7        # GUESS: a day planned this long before its date says travel times may have changed
KEEP_AFTER_TRIP_DAYS = 30  # GUESS: the offline copy is deleted this long after the trip's last day
PACK_BUDGET_BYTES = 512 * 1024   # GUESS: the pack is text only; card photos are web images, not kept offline

# The same lines as Help & safety in both apps (bundled there, so they work with no signal: m221 audit)
EMERGENCY = [
    {"title": "Emergency", "lines": ["If you or someone else is in danger or hurt, call 999."]},
    {"title": "Urgent medical help that isn't an emergency", "lines": ["NHS 111, by phone or online."]},
    {"title": "If you need to talk", "lines": ["Samaritans, free, 24 hours: 116 123."]},
]


def _d(s: str | None) -> date | None:
    try:
        return date.fromisoformat(s[:10]) if s else None
    except ValueError:
        return None


def _item(title: str, lines: list[str], source: str, saved: str | None, status: str, action: str | None = None,
          missing: list[str] | None = None) -> dict:
    return {"title": title, "lines": lines, "source": source, "saved": saved, "status": status, "action": action,
            "missing": missing or []}


def trip_end(trip: dict) -> date:
    return date.fromisoformat(trip["start"]) + timedelta(days=int(trip["nights"]))


def keep_until(trip: dict) -> date:
    """After this day the trip's offline copy is deleted from the phone (and at once with "Delete my data")."""
    return trip_end(trip) + timedelta(days=KEEP_AFTER_TRIP_DAYS)


def _day(day: dict, today: date) -> dict:
    when = _d(day.get("date"))
    plan = day.get("plan")
    title = f"Day {day['index'] + 1}" + (f", {when:%a} {when.day} {when:%b}" if when else "")
    if plan is None:
        return _item(title, ["Nothing planned: a travel or free day."], "your trip", None,
                     "past" if when and when < today else "current")
    made = _d(plan.get("created_at"))
    lines, notes, missing = [], [], []
    for st in plan.get("stops") or []:
        lines.append(f"{st.get('arrive', '')}–{st.get('depart', '')} {st.get('title', '')}".strip())
        if st.get("rateable"):
            checked = _d(st.get("checked"))
            if checked is None:
                missing.append(f"when {st.get('title', 'a stop')}'s facts were checked")
            elif when and (when - checked).days > CARD_CHECK_DAYS:
                notes.append(f"{st.get('title')}: facts checked {checked:%-d %b %Y}; check opening hours on the day.")
            if st.get("book_ahead"):
                notes.append(f"{st.get('title')}: {st['book_ahead']}")
    status = "past" if when and when < today else "current"
    action = None
    if status == "current" and made and when and (when - made).days > PLAN_STALE_DAYS:
        status, action = "check", (f"Planned on {made:%-d %b}: travel times may have changed. Plan this day again "
                                   f"when you have signal.")
    return _item(title, lines + notes, "your plan", plan.get("created_at"), status, action, missing)


def _choice(kind: str, c: dict | None, trip: dict, today: date) -> dict:
    label = "Where you're staying" if kind == "stay" else "Your journey"
    if c is None:
        return _item(label, [], "your trip", None, "current", None, [f"no {kind if kind == 'stay' else 'flight'} chosen"])
    end = trip_end(trip)
    status = "expired" if today > end else "current"
    lines, missing = [c.get("title", "")], []
    cur = c.get("currency") or "GBP"   # m218: the price in its own currency; older choices are pounds
    price = c.get("price")
    if price is not None:
        lines.append((f"£{price:,.0f}" if cur == "GBP" else f"{price:,.0f} {cur}") + f", as found on {c.get('provider')}")
    if kind == "stay":
        if c.get("point") is None:
            missing.append("the address (open the booking site when you have signal)")
    else:
        for k, word in (("arriveTime", "lands"), ("leaveTime", "leaves home")):
            if c.get(k):
                lines.append(f"{'Lands' if k == 'arriveTime' else 'Flight home leaves'} {c[k]}"
                             + (f" ({c.get('arrivePlace') if k == 'arriveTime' else c.get('leavePlace')})"
                                if c.get('arrivePlace' if k == 'arriveTime' else 'leavePlace') else ""))
            else:
                missing.append(f"when the flight {word}")
    if c.get("forStart") and c["forStart"] != trip["start"]:
        status = "check"
        action = f"Chosen for other dates ({c['forStart']}): check it on {c.get('provider')}, or choose again."
    elif not c.get("booked"):
        action = f"Not marked as booked: check with {c.get('provider')}."
        status = "check" if status == "current" else status
    else:
        action = (f"Times can change: check with the airline on the day." if kind == "flight" else
                  f"Check-in details are on {c.get('provider')}'s confirmation.")
    if c.get("sample"):
        status, action = "check", "A sample price, made up for testing: not a real booking."
    return _item(label, [x for x in lines if x], f"found on {c.get('provider')}", c.get("forStart"), status, action,
                 missing)


def build_pack(trip: dict, today: date, built_at: datetime) -> dict:
    """The offline pack for one trip, from the phone's own copy (the trip JSON both apps keep)."""
    if today > keep_until(trip):
        return {"built_at": built_at.isoformat(), "deleted": True, "sections": [], "bytes": 0,
                "line": "This trip ended more than 30 days ago, so its offline copy is deleted."}
    days = [_day(d, today) for d in sorted(trip.get("days") or [], key=lambda d: d["index"])]
    sections = [
        {"name": "itinerary", "items": days},
        {"name": "stay", "items": [_choice("stay", trip.get("stay"), trip, today)] if trip.get("needStay", True) else []},
        {"name": "travel", "items": [_choice("flight", trip.get("flight"), trip, today)] if trip.get("needFlight", True)
         else []},
        {"name": "emergency", "items": [_item(e["title"], e["lines"], "bundled in the app", None, "current")
                                        for e in EMERGENCY]},
    ]
    pack = {"built_at": built_at.isoformat(), "deleted": False, "keep_until": keep_until(trip).isoformat(),
            "sections": sections, "photos": "not kept offline: card photos are web images"}
    pack["bytes"] = len(json.dumps(pack).encode())
    pack["within_budget"] = pack["bytes"] <= PACK_BUDGET_BYTES
    return pack


# ---- syncing what was done offline ---------------------------------------------------------------------------------

def merge_ratings(phone: list[dict], server: list[dict]) -> list[dict]:
    """One rating per (plan, stop): the later one wins, whichever side it's on. A rating made offline is never lost
    to an older one on the server, and a later change on another device isn't undone by an old unsent one."""
    best: dict[tuple, dict] = {}
    for r in server + phone:
        k = (r["plan_id"], r["moment_id"])
        if k not in best or r["at"] > best[k]["at"]:
            best[k] = r
    return sorted(best.values(), key=lambda r: r["at"])


def which_plan(phone: dict | None, server: dict | None, unsent_for_phone_plan: int) -> str:
    """"phone" or "server": a newer plan from the server replaces the phone's, unless ratings for the phone's plan
    haven't been sent yet. Then the phone keeps its plan until they're sent (they belong to that plan's id)."""
    if server is None:
        return "phone"
    if phone is None:
        return "server"
    if unsent_for_phone_plan:
        return "phone"
    return "server" if (server.get("created_at") or "") > (phone.get("created_at") or "") else "phone"
