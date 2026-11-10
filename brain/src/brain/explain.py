"""m219: explanations from the algorithm's actual inputs (Abram, 7 Nov: "Explanations must use actual data. Do not
use a generic AI response that invents a justification after the algorithm has made its decision.")

Every recommendation (a stop in a day, a place to stay among the search results, a stay judged against the trip, a
trip length) can say why, as a list of **factors**. Each factor is one input the recommendation was really computed
from, with its value and where that value comes from:

- `kind`: preference, travel, hours, best_time, budget, rating, price, location, terms, coverage, pace.
- `effect`: "for", "against" or "neutral". It's decided by a fixed rule on the value (stated in each function), not
  by wording.
- `text`: a fixed template filled with the value. No model writes it, and it never claims more than the value shows.
- `value`: the number (or string) the algorithm used.
- `source`: where that value comes from, for example "your answers (the rating model)" or "the card's times".

Anything the algorithm didn't know is listed in `unknown`, never guessed. A factor is never added for show: if an input
didn't take part in the decision, it isn't a factor.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

FOR, AGAINST, NEUTRAL = "for", "against", "neutral"


@dataclass(frozen=True)
class Factor:
    kind: str
    effect: str
    text: str
    value: float | str | None
    source: str


def _out(factors: list[Factor], unknown: list[str]) -> dict:
    return {"factors": [asdict(f) for f in factors], "unknown": unknown}


def _hhmm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def _mins(t: str) -> int:
    return int(t[:2]) * 60 + int(t[3:5])


def _money(x: float, currency: str = "GBP") -> str:
    n = f"{x:,.2f}" if x < 100 and round(x, 2) != int(x) else f"{x:,.0f}"
    return f"£{n}" if currency == "GBP" else f"{n} {currency}"


# ---- a stop in a day ----------------------------------------------------------------------------------------------

# The planner's transfer penalties start at 15 and 30 minutes (planner.LegWeights: transfer_15_30, transfer_30_plus),
# so those are the lines between "short", "a fair way" and "long".
SHORT_LEG, LONG_LEG = 15, 30
MODE_WORDS = {"walk": "on foot", "tube": "by Tube", "bus": "by bus", "transit": "by Tube or bus", "rail": "by train"}


def p_good(scale: float, cutpoint: float, u: float) -> float:
    """The rating model's chance of "Good" or better, P(y ≥ 3) = F(scale·u − c₂|₃): the same number behind
    "A strong match for you" (dayplan.match_label)."""
    return 1.0 / (1.0 + math.exp(-(scale * u - cutpoint)))


def stop(st: dict, *, p: float | None, windows: list[tuple[int, int]], hours_text: str = "",
         budget: dict | None = None, travel_source: str = "straight-line estimate",
         labels: dict[str, str] | None = None, taste: set[str] | None = None) -> dict:
    """Why one stop is in the day, from what the planner used:

    - `st`: the stop as dayplan builds it. Its `why` is scoring.contributions, the named terms x_k·β_k of this
      person's score. It also has `travel_min`, `travel_mode`, `from`, `arrive`, `depart`, `best_windows`,
      `cost_gbp` and `familiar`.
    - `p`: P(Good or better) from the rating model, or None for a slot with no card (lunch, your own time).
    - `windows`: the card's allowed times that the planner fitted the visit into (Moment.windows).
    - `budget`: the day's money block (daybudget.block), when there's a budget.
    - `taste`: the score's terms that are tastes (place, moment, interests). Only these are named in "Why this
      stop?": cost, travel and weather terms have their own factors there.
    """
    f: list[Factor] = []
    unknown: list[str] = []
    labels = labels or {}
    pros: list[str] = []      # m230: the score's own named terms, for "Why this stop?" (never their values)
    cons: list[str] = []
    if p is not None:
        strong, good = p >= 0.75, p >= 0.5
        word = "A strong match for you" if strong else "A good match for you" if good else "Worth a try"
        f.append(Factor("preference", FOR if good else NEUTRAL,
                        f"{word}: the rating model gives a {round(p * 100)}% chance you'd rate it Good or better.",
                        round(p, 3), "your answers (the rating model)"))
        for w in st.get("why") or []:   # the score's own named terms, largest first (scoring.contributions)
            c = float(w["contribution"])
            if abs(c) < 0.05:
                continue
            label = labels.get(w["feature"], w["label"])
            if taste is None or w["feature"] in taste:
                (pros if c > 0 else cons).append(label)
            f.append(Factor("preference", FOR if c > 0 else AGAINST,
                            f"{label[:1].upper() + label[1:]}: counts {'for' if c > 0 else 'against'} it, for you.",
                            round(c, 3), "your answers (the scoring weights)"))
    if st.get("familiar"):
        f.append(Factor("preference", FOR, "You loved it before, so it's your one familiar place today.",
                        "familiar", "your answers (places you loved)"))
    t, mode = st.get("travel_min"), st.get("travel_mode") or "walk"
    if t is not None:
        effect = FOR if t <= SHORT_LEG else NEUTRAL if t <= LONG_LEG else AGAINST
        frm = st.get("from") or "the last stop"
        f.append(Factor("travel", effect, f"Right by {frm}: no travel." if round(t) == 0 else
                        f"{round(t)} min {MODE_WORDS.get(mode, mode)} from {frm}.", round(t), travel_source))
    if st.get("lunch") and str(st.get("moment_id", "")).startswith("lunch@"):   # m217: a lunch slot, not a venue
        line = budget["lines"][0] if budget and budget["lines"] and budget["lines"][0]["label"] == "Lunch" else None
        gbp = line["gbp"] if line else st.get("cost_gbp")
        what = line["note"] if line else "Lunch at a café, pub or food stall"
        tail = (f" The day comes to {_money(budget['total_gbp'])} of your {_money(budget['budget_gbp'])}."
                if budget else "")
        f.append(Factor("budget", AGAINST if budget and budget["status"] == "over" else NEUTRAL,
                        (f"{what}: about {_money(gbp)}, an estimate." if gbp else f"{what}: nothing set aside.") + tail,
                        gbp, "ODYS's planning estimate" + (" and your budget" if budget else "")))
    if st.get("arrive") and st.get("depart"):
        a, d = _mins(st["arrive"]), _mins(st["depart"])
        inside = next(((lo, hi) for lo, hi in windows if lo <= a and d <= hi), None)
        if windows and inside and inside != (0, 1440):
            # the planner's window is the card's visiting window (when to go, within its opening hours), so it's
            # named that, with the opening hours beside it where the card gives them
            f.append(Factor("hours", FOR, f"You're there {st['arrive']}–{st['depart']}, inside the card's visiting "
                            f"window ({_hhmm(inside[0])}–{_hhmm(inside[1])}).", f"{_hhmm(inside[0])}-{_hhmm(inside[1])}",
                            "the card's visiting window" + (f"; opening hours: {hours_text}" if hours_text else "")))
        elif windows and inside:
            f.append(Factor("hours", NEUTRAL, "Any time of day suits it.", "any", "the card's visiting window"))
        elif p is not None:
            unknown.append("opening times")
        best = st.get("best_windows") or []
        if best:
            lo, hi = best[0]
            hit = any(a < h and d > l for l, h in best)
            f.append(Factor("best_time", FOR if hit else NEUTRAL,
                            (f"Your visit overlaps its best time, {_hhmm(lo)}–{_hhmm(hi)}." if hit else
                             f"Its best time is {_hhmm(lo)}–{_hhmm(hi)}; this plan has you there {st['arrive']}–{st['depart']}."),
                            f"{_hhmm(lo)}-{_hhmm(hi)}", "the card's best time"))
    cost = st.get("cost_gbp")
    if cost is not None and p is not None:
        if budget:
            effect = AGAINST if budget["status"] == "over" else FOR if not cost else NEUTRAL
            f.append(Factor("budget", effect,
                            (f"Free. The day comes to {_money(budget['total_gbp'])} of your {_money(budget['budget_gbp'])}."
                             if not cost else
                             f"{_money(cost)} of your {_money(budget['budget_gbp'])}; the day comes to "
                             f"{_money(budget['total_gbp'])}."), round(cost, 2), "the card's price and your budget"))
        else:
            f.append(Factor("budget", FOR if not cost else NEUTRAL, "Free." if not cost else f"{_money(cost)}.",
                            round(cost, 2), "the card's price"))
    return {**_out(f, unknown), "why": why_this_stop(f, pros, cons) if p is not None else []}


# ---- "Why this stop?" on the stop card (m230; Abram's decision 2, m224) -----------------------------------------

WHY_MAX = 3   # Abram: "no more than three meaningful reasons"


def why_this_stop(factors: list[Factor], pros: list[str], cons: list[str]) -> list[dict]:
    """At most three reasons for a stop, each from a factor above, worded with no model score or percentage (Abram,
    m224: "don't expose raw model scores or percentages"). Times, minutes and prices are the plan's own facts, so they
    stay. A fixed rule, in this order:

    1. A familiar place: "You loved it before…".
    2. Your answers: the score's two largest terms for it, by name only ("From your answers, it has what you like:
       photo spots, awe"). Labels can hold "and" or a comma themselves, so they're listed, not joined with "and".
    3. The time: inside its best time, else inside the card's visiting window (not "any time").
    4. The travel there, when it's short (15 min or less, the planner's first transfer penalty).
    5. The money, when it's free.

    If anything counts against the stop (a long journey, a day over budget, a term against it in the score), the last
    place goes to one trade-off, so the reasons never read as all upside. Nothing is added that the planner didn't use.
    """
    pick = lambda kind, effect: next((x for x in factors if x.kind == kind and x.effect == effect), None)
    fors: list[tuple[str, str]] = []
    if any(x.value == "familiar" for x in factors):
        fors.append(("preference", "You loved it before, so it's your one familiar place today."))
    if pros:
        top = pros[:2]
        fors.append(("preference", f"From your answers, it has what you like: {', '.join(top)}."))
    best = pick("best_time", FOR)
    hours = pick("hours", FOR)
    if best:
        lo, hi = str(best.value).split("-")
        fors.append(("best_time", f"You're there at its best time, {lo}–{hi}."))
    elif hours and hours.value != "any":
        lo, hi = str(hours.value).split("-")
        fors.append(("hours", f"It fits the card's visiting window, {lo}–{hi}."))
    travel = pick("travel", FOR)
    if travel:
        fors.append(("travel", travel.text))
    money = pick("budget", FOR)
    if money:
        fors.append(("budget", "Free to visit." if not money.value else money.text))
    against = [x for x in factors if x.effect == AGAINST and x.kind in ("travel", "budget")]
    trade = None
    if against:
        x = against[0]
        trade = (x.kind, f"The trade-off: {x.text[:1].lower() + x.text[1:]}")
    elif cons:
        trade = ("preference", f"The trade-off: it has {cons[0]}, which your answers count against.")
    keep = fors[:WHY_MAX - (1 if trade else 0)] + ([trade] if trade else [])
    return [{"kind": k, "effect": AGAINST if (k, t) == trade else FOR, "text": t} for k, t in keep]


# ---- a place to stay among the search results ("Best for your days") ---------------------------------------------

def stay_rank(stays: list, px, centre: str) -> dict[str, dict]:
    """Why each stay sits where it does in "Best for your days": the three parts of trips.recommended_scores (45%
    guests' rating, 35% the night's real cost, 20% distance from the centre), each with the stay's own value, the range
    across these results, and the scaled part the score used. The parts are computed with the score's own scaling
    (trips._norm, trips._price_scale), and `score` is their weighted sum, so the text can't drift from the ranking."""
    from . import trips   # the ranking's own functions (trips doesn't import this module)
    rated = [s.rating for s in stays if s.rating is not None]
    dists = [s.distance_km for s in stays if s.distance_km is not None]
    rating_part = trips._norm(rated or [5.0])
    price_part = trips._price_scale({s.id: px.key(s.cost_night, s.currency) for s in stays})
    dist_part = trips._norm(dists or [0.0])
    out = {}
    for s in stays:
        f: list[Factor] = []
        unknown: list[str] = []
        r = rating_part(s.rating) if s.rating is not None else 0.5
        if s.rating is not None:
            f.append(Factor("rating", FOR if r >= 0.5 else AGAINST,
                            f"Guests rate it {s.rating:.1f} out of 10 (these results: {min(rated):.1f} to "
                            f"{max(rated):.1f}); 45% of the score.", s.rating, "guests' reviews, as the provider gives them"))
        else:
            unknown.append("guests' rating (counted as middling)")
        g, v = px.key(s.cost_night, s.currency)
        same = [px.key(x.cost_night, x.currency)[1] for x in stays if px.key(x.cost_night, x.currency)[0] == g]
        c = price_part(s.id)
        unit = "GBP" if px.mode == "converted" else s.currency
        approx = "≈ " if px.mode == "converted" and s.currency != "GBP" else ""
        fees = f", including {_money(s.pay_there / max(s.nights, 1), s.currency)} paid there" if s.pay_there else ""
        among = " in " + s.currency if px.mode == "grouped" else ""
        f.append(Factor("price", FOR if c <= 0.5 else AGAINST,
                        f"{approx}{_money(v, unit)} a night{fees} (these results{among}: {_money(min(same), unit)} to "
                        f"{_money(max(same), unit)}); 35% of the score.", round(v, 2), "the provider's price"))
        d = dist_part(s.distance_km) if s.distance_km is not None else 0.5
        if s.distance_km is not None:
            f.append(Factor("location", FOR if d <= 0.5 else AGAINST,
                            f"{s.distance_km:.1f} km from {centre} (these results: {min(dists):.1f} to "
                            f"{max(dists):.1f} km); 20% of the score.", s.distance_km, "the provider's map point"))
        else:
            unknown.append("where it is (counted as middling)")
        if s.pay_there_other:
            unknown.append(f"fees in another currency ({s.pay_there_other})")
        parts = [{"name": "rating", "weight": 0.45, "scaled": round(r, 4)},
                 {"name": "cheaper", "weight": 0.35, "scaled": round(1 - c, 4)},
                 {"name": "nearer", "weight": 0.2, "scaled": round(1 - d, 4)}]
        out[s.id] = {**_out(f, unknown), "parts": parts,
                     "score": round(sum(x["weight"] * x["scaled"] for x in parts), 4)}
    return out


# ---- a stay judged against the person's own trip -----------------------------------------------------------------

def stay_for_trip(fit: dict, cost: dict, currency: str, refundable: bool | None, holidays: list[str]) -> dict:
    """From stayprices.trip_fit (minutes to each planned day) and stayprices.cost_lines (the whole cost)."""
    f: list[Factor] = []
    unknown: list[str] = []
    a, b = fit.get("to_first"), fit.get("back")
    if a is not None or b is not None:
        worst = max(x for x in (a, b) if x is not None)
        f.append(Factor("location", FOR if worst <= SHORT_LEG else NEUTRAL if worst <= LONG_LEG else AGAINST,
                        fit["line"].split(" Day")[0], worst, "your planned days, and travel times"))
    for r in fit.get("days") or []:
        f.append(Factor("location", NEUTRAL, r["text"] + ".", r.get("to_first"), "your planned days"))
    if fit.get("missing"):
        unknown.append("days with no places yet: " + ", ".join(str(i + 1) for i in fit["missing"]))
    if a is None and b is None:
        unknown.append("how far it is from your days (plan them first)")
    f.append(Factor("price", NEUTRAL, cost["line"], cost["whole"], "the provider's price" +
                    (" (a sample price)" if cost.get("sample") else "")))
    f.append(Factor("terms", FOR if refundable else AGAINST if refundable is False else NEUTRAL, cost["cancel"],
                    "refundable" if refundable else "non-refundable" if refundable is False else None,
                    "the provider's terms"))
    if refundable is None:
        unknown.append("cancellation terms")
    for h in holidays:
        f.append(Factor("calendar", NEUTRAL, f"Your dates include a bank holiday: {h}.", h, "GOV.UK bank holidays"))
    return {**_out(f, unknown), "why": why_this_stay(fit, cost, refundable, holidays)}


def why_this_stay(fit: dict, cost: dict, refundable: bool | None, holidays: list[str]) -> list[dict]:
    """m241 (Abram, m234): why a stay suits the itinerary, not the score. At most three lines, in this order: how far
    it is from the planned days, the whole cost, the terms. The last place goes to one trade-off when there is one:
    the farthest day over 30 min away, then non-refundable terms. A bank holiday fills a spare place."""
    fors: list[tuple[str, str]] = []
    a, b = fit.get("to_first"), fit.get("back")
    if a is not None or b is not None:
        fors.append(("location", fit["line"].replace(" of this trip", "")))
    else:
        fors.append(("location", "Plan your days to see how far they are from here."))
    fors.append(("price", cost["line"]))
    if refundable:
        fors.append(("terms", cost["cancel"]))
    trade = None
    far = [r for r in fit.get("days") or [] if max(r.get("to_first") or 0, r.get("back") or 0) > LONG_LEG]
    if far:
        r = max(far, key=lambda r: max(r.get("to_first") or 0, r.get("back") or 0))
        trade = ("location", f"The trade-off: {r['text'][:1].lower() + r['text'][1:]}, the farthest of your days.")
    elif refundable is False:
        trade = ("terms", f"The trade-off: {cost['cancel'][:1].lower() + cost['cancel'][1:]}")
    if holidays and len(fors) < WHY_MAX - (1 if trade else 0):
        fors.append(("calendar", f"Your dates include a bank holiday: {holidays[0]}."))
    keep = fors[:WHY_MAX - (1 if trade else 0)] + ([trade] if trade else [])
    return [{"kind": k, "effect": AGAINST if (k, t) == trade else FOR, "text": t} for k, t in keep]


# ---- a trip length ------------------------------------------------------------------------------------------------

def trip_length(r: dict) -> dict:
    """From triplength.suggest: the person's strong and good matches, what the suggestion is built on (`best`: the
    strong matches, or with fewer of them than places a day, the best few days' worth of strong and good ones), and the
    days those take at their places a day, keeping the day's shape."""
    strong, best, per_day, need = r["strong_matches"], r["best"], r["places_per_day"], r["suggested_days"]
    days = lambda n: f"{n} exploring day{'s' if n != 1 else ''}"
    f = [Factor("coverage", FOR if strong else NEUTRAL,
                f"{strong} strong matches for you in {r['place']} (a 75% or better chance of Good), and "
                f"{r['good_matches']} good ones, of {r['checked']} checked places.", strong,
                "your answers (the rating model) and the checked places")]
    if strong >= per_day:
        f.append(Factor("coverage", FOR, f"The suggestion is built on your {strong} strong matches.", best,
                        "your answers (the rating model)"))
    else:
        f.append(Factor("coverage", NEUTRAL, f"Fewer strong matches than your places a day, so it uses your best "
                        f"{best} for now (strong and good ones).", best, "your answers (the rating model)"))
    f.append(Factor("pace", NEUTRAL, f"At {per_day} places a day, keeping the day's shape (at most two history stops "
                    f"a day, one wander), those {best} take {days(need)}"
                    + (", the most it suggests." if r.get("capped") else "."), need, "your places a day"))
    if r.get("your_days") is not None:
        yours, spare = r["your_days"], r.get("spare_days") or 0
        f.append(Factor("coverage", FOR if yours >= need else AGAINST,
                        f"Your trip has {days(yours)}" + (f": {spare} more than they need." if spare else
                                                         "." if yours >= need else ": fewer than they need."),
                        yours, "your trip's dates"))
    unknown = ["whether each day is feasible (travel, opening days): the day planner checks that when it plans them"]
    return {**_out(f, unknown), "why": why_this_length(r)}


def why_this_length(r: dict) -> list[dict]:
    """m241 (Abram, m234): what the suggested length rests on, what a shorter trip would leave out and what a longer
    one would add, from triplength's own options, by name. At most three lines, no percentages."""
    need, per_day = r["suggested_days"], r["places_per_day"]
    plural = lambda n: f"{n} day{'s' if n != 1 else ''}"
    lines = [{"kind": "coverage", "effect": FOR,
              "text": (f"{r['strong_matches']} strong matches for you in {r['place']}: at {per_day} a day they take "
                       f"{plural(need)}." if r["strong_matches"] >= per_day else
                       f"Your best {r['best']} places in {r['place']} for now take {plural(need)} at {per_day} a day.")}]
    opts = r.get("options") or []
    shorter = max((o for o in opts if o["days"] < need), key=lambda o: o["days"], default=None)
    longer = min((o for o in opts if o["days"] > need), key=lambda o: o["days"], default=None)
    if shorter:
        lines.append({"kind": "pace", "effect": AGAINST, "text": f"In {plural(shorter['days'])}: {shorter['line']}"})
    if longer:
        lines.append({"kind": "pace", "effect": FOR, "text": f"In {plural(longer['days'])}: {longer['line']}"})
    return lines[:WHY_MAX]
