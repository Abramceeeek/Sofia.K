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

Missing data is said ("not saved"), never filled in.

**Retention (m226, Abram 9 Nov: "trip information belongs to the traveller").** What the phone keeps falls into five
classes (`STORAGE` below). The person's own trips, plans, ratings and settings are never deleted automatically: only
by the person (a trip, or "Delete my data"). After a trip, its booking details read "expired" and its summary stays.
The 30-day rule (GUESS) applies only to **disposable** content: a stored copy of an offline pack, cached images, share
images. The pack itself is derived from the trip record, so it can always be built again while the trip exists.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta

SECTIONS = ("itinerary", "stay", "travel", "emergency")   # Abram's order: the saved itinerary first
CARD_CHECK_DAYS = 90       # GUESS: a card's facts (hours, prices) older than this say "check on the day"
PLAN_STALE_DAYS = 7        # GUESS: a day planned this long before its date says travel times may have changed
DISPOSABLE_AFTER_TRIP_DAYS = 30  # GUESS: a stored offline pack or cached content for a trip may go this long after it
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


# m226: what the phone keeps, by class. Only "derived" and "cache" ever expire on their own; "user" and "history" are
# the traveller's, kept until they delete them; "credential" is the install token, never in plain storage.
STORAGE = {
    "trips.json": ("user", "Your trips: dates, the chosen flight and stay, your own time, each day's plan."),
    "plan.json": ("user", "Your current day's plan."),
    "request.json": ("user", "The settings of your last plan (start, hours, places a day)."),
    "profile.json": ("user", "Your answers that shape plans."),
    "pending_ratings.json": ("user", "Ratings made with no signal, until the Brain has them."),
    "handoff.json": ("user", "A booking you went to make, until you say whether you booked it."),
    "settings": ("user", "Small settings: the onboarding step, reminders, your ratings per plan, where you are in a day."),
    "past trips": ("history", "A trip after its last day: its summary and days, with booking details marked expired."),
    "offline pack (stored copy)": ("derived", "Built from trips.json; any stored copy may go 30 days after the trip."),
    "images and share cards": ("cache", "Card photos and share images: the system may clear them; never backed up."),
    "install token": ("credential", "iPhone Keychain; Android: encrypted with an Android Keystore key."),
}
EXPIRES = {"derived", "cache"}   # the only classes with an automatic deletion rule


def disposable_after(trip: dict) -> date:
    """From the day after this, a stored offline pack or cached content for the trip may be discarded. The trip
    itself, its days and its summary stay until the person deletes them."""
    return trip_end(trip) + timedelta(days=DISPOSABLE_AFTER_TRIP_DAYS)


def summary(trip: dict) -> dict:
    """A past trip's lasting record (kept, never expired): where, when, the days and places, what was chosen."""
    days = sorted(trip.get("days") or [], key=lambda d: d["index"])
    places = [st.get("title") for d in days for st in ((d.get("plan") or {}).get("stops") or []) if st.get("rateable")]
    return {"city": trip.get("city"), "start": trip["start"], "end": trip_end(trip).isoformat(),
            "nights": int(trip["nights"]), "days_planned": sum(1 for d in days if d.get("plan")), "places": places,
            "stay": (trip.get("stay") or {}).get("title"), "flight": (trip.get("flight") or {}).get("title")}


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
    """The offline pack for one trip, from the phone's own copy (the trip JSON both apps keep). m226: it's always
    built from the trip record, past trips included; nothing about the trip is ever deleted here. After the trip, the
    pack only says whether a stored copy of it is still worth keeping (`keep_stored_copy`)."""
    days = [_day(d, today) for d in sorted(trip.get("days") or [], key=lambda d: d["index"])]
    sections = [
        {"name": "itinerary", "items": days},
        {"name": "stay", "items": [_choice("stay", trip.get("stay"), trip, today)] if trip.get("needStay", True) else []},
        {"name": "travel", "items": [_choice("flight", trip.get("flight"), trip, today)] if trip.get("needFlight", True)
         else []},
        {"name": "emergency", "items": [_item(e["title"], e["lines"], "bundled in the app", None, "current")
                                        for e in EMERGENCY]},
    ]
    pack = {"built_at": built_at.isoformat(), "past": today > trip_end(trip),
            "keep_stored_copy": today <= disposable_after(trip), "disposable_after": disposable_after(trip).isoformat(),
            "summary": summary(trip) if today > trip_end(trip) else None,
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
