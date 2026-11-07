"""m203: a place to stay, judged against the person's trip (Abram, 7 Nov), not a list from a booking site.

Three things about one stay, for the person's own dates and days:
- **Your days from here:** how far it is from each planned day's first place, and back from its last.
- **The whole cost:** the total the provider says the guest pays, plus anything it marks as paid at the property, and
  the cancellation terms and board, as the search found them.
- **Nearby dates:** the same stay, the same number of nights, starting up to 3 days earlier or later, like for like:
  the same room, board and cancellation terms. Where a date only has something different, it says what differs.
  Observed prices only: never "it will be cheaper".

**Sample prices only for now** (Abram, 7 Nov): until Nuitée confirms its terms in writing
(decisions/liteapi-clarification.md), nearby dates are made-up sample prices, always labelled. The live path
(`liteapi_dates`) follows LiteAPI's documented rates search (docs.liteapi.travel/reference/post_hotels-rates, read
7 Nov 2026) and is tested on that shape, but it's only used when `Settings.stay_dates_live` is on, which it isn't.
"""

from __future__ import annotations

import hashlib
import statistics
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from typing import Callable

from .moments import Point
from .trips import LITEAPI_MARKET, LITEAPI_URL, StayQuery, rate_pay_there

AROUND = 3   # days either side of the person's own check-in (Abram, 7 Nov)


@dataclass(frozen=True)
class StayTerms:
    """The stay as the person found it: what any other date is compared with."""
    id: str
    name: str
    lat: float | None
    lon: float | None
    price_total: float
    nights: int
    currency: str = "GBP"
    room: str = ""
    board: str = ""
    refundable: bool | None = None
    pay_there: float = 0.0          # taxes or fees the provider marks as not included: paid at the property
    sample: bool = False


@dataclass
class DateOption:
    checkin: date
    checkout: date
    total: float | None             # None: nothing on these dates
    pay_there: float = 0.0
    same_terms: bool = True
    differs: list[str] = field(default_factory=list)
    yours: bool = False
    lowest: bool = False
    holidays: list[str] = field(default_factory=list)   # m204: the destination's bank holidays in these dates (facts)

    def out(self, nights: int) -> dict:
        d = asdict(self)
        d.update(checkin=self.checkin.isoformat(), checkout=self.checkout.isoformat(),
                 label=f"{self.checkin:%a} {self.checkin.day} – {self.checkout:%a} {self.checkout.day} {self.checkout:%b}",
                 whole=None if self.total is None else round(self.total + self.pay_there, 2),
                 per_night=None if self.total is None else round((self.total + self.pay_there) / max(nights, 1), 2))
        return d


def nearby(checkin: date, nights: int, today: date, around: int = AROUND) -> list[tuple[date, date]]:
    """The person's check-in and up to `around` days either side, keeping the nights; never a date already past."""
    out = []
    for k in range(-around, around + 1):
        ci = checkin + timedelta(days=k)
        if ci >= today:
            out.append((ci, ci + timedelta(days=nights)))
    return out


# ---- sample prices (labelled; the only prices shown until Nuitée replies) -----------------------------------------

# GUESS, for sample prices only: Friday and Saturday nights cost more in London, Sunday a little less
_SAMPLE_NIGHT = {4: 1.28, 5: 1.32, 6: 0.94}


def _noise(key: str) -> float:
    return (int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF - 0.5) * 0.1   # ±5%


def sample_dates(stay: StayTerms, own: tuple[date, date], options: list[tuple[date, date]]) -> list[DateOption]:
    """Made-up prices with a plausible weekly shape, scaled so the person's own dates cost exactly what they found."""
    raw = lambda ci, co: sum(_SAMPLE_NIGHT.get(d.weekday(), 1.0) * (1 + _noise(f"{stay.id}:{d}"))
                             for d in (ci + timedelta(days=k) for k in range((co - ci).days)))
    scale = stay.price_total / raw(*own)
    return [DateOption(ci, co, round(raw(ci, co) * scale, 2), stay.pay_there, yours=(ci, co) == own)
            for ci, co in options]


# ---- LiteAPI, one hotel on one date range (off until Nuitée replies) ----------------------------------------------

def liteapi_hotel_body(stay: StayTerms, q: StayQuery) -> dict:
    """The documented rates search for one hotel: `hotelIds`, the same guests and rooms, every rate (to find the same
    room again)."""
    rooms = max(1, min(q.rooms, q.adults))
    occ = [{"adults": q.adults // rooms + (1 if i < q.adults % rooms else 0), "children": []} for i in range(rooms)]
    occ[0]["children"] = list(q.children)
    return {"hotelIds": [stay.id], "checkin": q.checkin.isoformat(), "checkout": q.checkout.isoformat(),
            "currency": stay.currency or "GBP", "guestNationality": LITEAPI_MARKET, "occupancies": occ, "timeout": 8}


def _rate_price(rate: dict) -> tuple[float | None, float]:
    """(the total the guest pays, what's paid at the property): `retailRate.total` and the `taxesAndFees` marked
    `included: false` (LiteAPI's docs: "Indicates whether the tax is included in the total price")."""
    total = ((rate.get("retailRate") or {}).get("total") or [{}])[0].get("amount")
    return (float(total) if total is not None else None), rate_pay_there(rate)


def _terms(rate: dict) -> tuple[str, str, bool | None]:
    tag = ((rate.get("cancellationPolicies") or {}).get("refundableTag") or "").upper()
    board = rate.get("boardName") or ("Room only" if (rate.get("boardType") or "RO").upper() == "RO" else "")
    return (rate.get("name") or "").strip(), board, True if tag == "RFN" else False if tag == "NRFN" else None


def match_rate(resp: dict, want: StayTerms) -> tuple[float | None, float, list[str]]:
    """The same room on the same terms if it's there; else the closest, saying what differs. No documented field
    stays the same across searches, so the match is by the room's name, board and cancellation terms."""
    best = None
    for item in resp.get("data") or []:
        for rt in item.get("roomTypes") or []:
            for rate in rt.get("rates") or []:
                total, there = _rate_price(rate)
                if total is None:
                    continue
                name, board, refundable = _terms(rate)
                differs = []
                if want.room and name.casefold() != want.room.casefold():
                    differs.append(f"a different room ({name})" if name else "a different room")
                if want.board and board and board.casefold() != want.board.casefold():
                    differs.append(board.lower())
                if want.refundable is not None and refundable is not None and refundable != want.refundable:
                    differs.append("free cancellation" if refundable else "non-refundable")
                key = (len(differs), total + there)
                if best is None or key < best[0]:
                    best = (key, total, there, differs)
    return (best[1], best[2], best[3]) if best else (None, 0.0, [])


def liteapi_dates(stay: StayTerms, q: StayQuery, options: list[tuple[date, date]], key: str,
                  fetch: Callable[[str, dict, dict], dict]) -> list[DateOption]:
    headers = {"X-API-Key": key, "accept": "application/json", "content-type": "application/json"}
    out = []
    for ci, co in options:
        qq = StayQuery(q.city, q.country_code, q.lat, q.lon, ci, co, q.adults, q.children, q.rooms)
        total, there, differs = match_rate(fetch(LITEAPI_URL, headers, liteapi_hotel_body(stay, qq)), stay)
        out.append(DateOption(ci, co, total, there, same_terms=not differs, differs=differs,
                              yours=ci == q.checkin))
    return out


def mark_lowest(options: list[DateOption]) -> None:
    """The lowest whole cost among dates on the same terms (never a different room's price)."""
    same = [o for o in options if o.total is not None and o.same_terms]
    if len(same) > 1:
        low = min(same, key=lambda o: o.total + o.pay_there)
        if any(o.total + o.pay_there > low.total + low.pay_there for o in same):
            low.lowest = True


# ---- the stay against the trip's days -----------------------------------------------------------------------------

@dataclass(frozen=True)
class DayEnds:
    index: int
    first: Point | None             # the day's first planned place
    last: Point | None              # and its last


def trip_fit(stay: Point, days: list[DayEnds], travel) -> dict:
    """How far each planned day's places are from the stay: there in the morning, back at the end."""
    rows = []
    for d in days:
        if d.first is None or d.last is None:
            continue
        rows.append({"index": d.index, "to_first": round(travel.minutes(stay, d.first)),
                     "back": round(travel.minutes(d.last, stay))})
    if not rows:
        return {"days": [], "line": "Plan your days to see how far they are from here.", "to_first": None, "back": None}
    to_first = round(statistics.median(r["to_first"] for r in rows))
    back = round(statistics.median(r["back"] for r in rows))
    far = max(rows, key=lambda r: r["to_first"] + r["back"])
    line = f"About {to_first} min to your first place and {back} min back, on a typical day of this trip."
    if far["to_first"] + far["back"] >= to_first + back + 20 and len(rows) > 1:
        line += f" Day {far['index'] + 1} is the furthest: {far['to_first']} min there, {far['back']} back."
    return {"days": rows, "line": line, "to_first": to_first, "back": back}


def cost_lines(stay: StayTerms, sample: bool) -> dict:
    def money(x: float) -> str:   # pence only where they matter: under £100 and not a whole pound
        n = f"{x:,.2f}" if x < 100 and round(x, 2) != int(x) else f"{x:,.0f}"
        return f"£{n}" if stay.currency == "GBP" else f"{n} {stay.currency}"
    whole = stay.price_total + stay.pay_there
    line = f"{money(whole)} for {stay.nights} night{'s' if stay.nights != 1 else ''}, " + (
        f"including {money(stay.pay_there)} paid at the property." if stay.pay_there else
        "taxes included, as the provider shows it.")
    cancel = ("Free cancellation, as found: check the deadline on the provider's site." if stay.refundable else
              "Non-refundable, as found." if stay.refundable is False else
              "Cancellation terms: check on the provider's site.")
    return {"whole": round(whole, 2), "per_night": round(whole / max(stay.nights, 1), 2), "line": line,
            "cancel": cancel, "board": stay.board or None, "sample": sample}
