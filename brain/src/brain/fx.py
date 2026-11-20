"""m218: prices in different currencies, compared honestly.

- **One currency** in a set of results: compared as they are, as before.
- **Several currencies, with a fresh rate:** each price is converted to pounds with the European Central Bank's euro
  reference rates, crossed through the euro. The original fare and its currency stay as they are, and the converted
  figure is shown separately, with its source and the rate's date. It is an estimate, never the price: the ECB says
  "The reference rates are published for information purposes only", and it discourages using them for transactions
  (ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates, read 7 Nov 2026).
- **Several currencies, no fresh rate** (none fetched, too old, or a currency the ECB doesn't publish, such as the
  Uzbek som): the results are grouped by currency and ranked within each group. Nothing is called the cheapest
  overall.

The ECB publishes 29 currencies against the euro, usually at around 16:00 CET on working days (not on TARGET closing
days). The daily file is `eurofxref-daily.xml`, one `<Cube time='YYYY-MM-DD'>` holding `<Cube currency='USD'
rate='1.1165'/>` lines (units per euro; read 7 Nov 2026). It's free and needs no key. Fetching it is off until Abram
switches it on (`Settings.fx_rates_live`).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

ECB_DAILY = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
ECB_SOURCE = "European Central Bank euro reference rates"
HOME = "GBP"
# A rate counts as current for 5 days: the ECB doesn't publish at weekends or on TARGET holidays, and the longest
# usual gap (Easter: Thursday's rates until Tuesday at 16:00) is 5 days. Older than that, nothing is converted.
MAX_AGE_DAYS = 5


@dataclass(frozen=True)
class Rates:
    per_eur: dict[str, float]          # units of each currency per 1 euro; EUR itself is 1
    as_of: date                        # the ECB's date for these rates
    fetched_at: datetime
    source: str = ECB_SOURCE
    url: str = ECB_DAILY

    def _rate(self, frm: str, to: str) -> Decimal | None:
        a, b = self.per_eur.get(frm.upper()), self.per_eur.get(to.upper())
        return None if not a or not b else Decimal(str(b)) / Decimal(str(a))

    def rate(self, frm: str, to: str = HOME) -> float | None:
        """How many `to` one `frm` buys, crossed through the euro; None if either isn't published."""
        r = self._rate(frm, to)
        return None if r is None else float(r)

    def convert(self, amount: float, frm: str, to: str = HOME) -> float | None:
        """To the penny, halves rounded up (in decimals, so 100 × 0.83415 is 83.42, not float's 83.41)."""
        r = self._rate(frm, to)
        return None if r is None else float((Decimal(str(amount)) * r).quantize(Decimal("0.01"), ROUND_HALF_UP))

    def fresh(self, today: date) -> bool:
        return 0 <= (today - self.as_of).days <= MAX_AGE_DAYS

    def line(self) -> str:
        """"ECB rate of 6 Nov 2026", for the converted figure."""
        return f"ECB rate of {self.as_of.day} {self.as_of:%b %Y}"


def parse_ecb(xml_text: str, fetched_at: datetime) -> Rates:
    """The ECB's daily file → Rates. Raises ValueError if it has no date or no rates."""
    root = ET.fromstring(xml_text)
    day = next((c for c in root.iter() if c.tag.endswith("Cube") and c.get("time")), None)
    if day is None:
        raise ValueError("no dated rates in the ECB file")
    per_eur = {"EUR": 1.0}
    for c in day:
        cur, rate = c.get("currency"), c.get("rate")
        if cur and rate and float(rate) > 0:
            per_eur[cur.upper()] = float(rate)
    if len(per_eur) == 1:
        raise ValueError("the ECB file has a date but no rates")
    return Rates(per_eur, date.fromisoformat(day.get("time")), fetched_at)


def http_get_text(url: str) -> str:
    import httpx   # only needed when fetching is on
    r = httpx.get(url, timeout=10.0)
    r.raise_for_status()
    return r.text


@dataclass
class EcbRates:
    """Fetches the daily file at most every `refresh_s` and keeps the last good one. `get()` gives the rates only while
    they're current; a failed fetch keeps the last good rates, and never makes rates up."""
    fetch_text: Callable[[str], str] = http_get_text
    clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
    refresh_s: int = 6 * 3600
    _held: Rates | None = field(default=None, repr=False)
    _tried: datetime | None = field(default=None, repr=False)

    def get(self) -> Rates | None:
        now = self.clock()
        if self._tried is None or (now - self._tried).total_seconds() >= self.refresh_s:
            self._tried = now
            try:
                self._held = parse_ecb(self.fetch_text(ECB_DAILY), now)
            except Exception:   # the ECB is down or the file changed: keep what we had, if it's still current
                pass
        held = self._held
        return held if held is not None and held.fresh(now.date()) else None


# m238 (WS5): the person's display currency. Pounds unless they choose another the ECB publishes (or the euro).
CURRENCY_NAMES = {"GBP": "pounds", "EUR": "euros", "USD": "US dollars"}


def currency_name(code: str) -> str:
    return CURRENCY_NAMES.get(code, code)


def display_options(rates: Rates | None) -> list[str]:
    """The display currencies on offer: every one the current rates cover, pounds first; pounds alone without rates."""
    if rates is None:
        return [HOME]
    return sorted(rates.per_eur, key=lambda c: (c != HOME, c))


@dataclass(frozen=True)
class Pricing:
    """How the prices in one set of results compare. `mode`: "one" (a single currency), "converted" (several, all
    converted to the display currency with `rates`) or "grouped" (several, not comparable: grouped by currency,
    the display currency first). m238: `display` is the person's chosen currency (pounds by default). The provider's
    price always stays as it is; a conversion is only ever an estimate shown beside it."""
    mode: str
    currencies: tuple[str, ...]        # in the order shown: the display currency first, then by count, then by code
    rates: Rates | None = None         # current rates, when there are any (estimates are shown in any mode)
    display: str = HOME

    @property
    def unit(self) -> str:
        """The currency facets and tabs are given in: the display currency when converted, else the first group's."""
        return self.display if self.mode == "converted" else (self.currencies[0] if self.currencies else self.display)

    def key(self, amount: float, currency: str) -> tuple[int, float]:
        """Sort key, lower is cheaper. Grouped: the currency's group first, so nothing ranks across currencies."""
        if self.mode == "converted":
            return 0, self.rates.convert(amount, currency, self.display) or 0.0
        return (self.currencies.index(currency) if currency in self.currencies else len(self.currencies)), amount

    def in_unit(self, amount: float, currency: str) -> float | None:
        """The amount in `unit`, or None when it can't be compared (another currency, no rate)."""
        if currency == self.unit:
            return amount
        return self.rates.convert(amount, currency, self.unit) if self.mode == "converted" else None

    def estimate(self, amount: float, currency: str) -> dict | None:
        """The converted figure shown beside a price in another currency, never in its place (whenever a current rate
        has that currency, in any mode)."""
        d = self.display
        if self.rates is None or currency == d or self.rates.rate(currency, d) is None:
            return None
        return {"amount": self.rates.convert(amount, currency, d), "currency": d,
                "rate": round(self.rates.rate(currency, d), 6),
                "source": self.rates.source, "as_of": self.rates.as_of.isoformat(), "line": self.rates.line()}

    def note(self, what: str) -> str | None:
        """What the person is told about the comparison, or None for one currency."""
        d, dn = self.display, currency_name(self.display)
        if self.mode == "one":
            only = self.currencies[0] if self.currencies else d
            if only == d or self.rates is None or self.rates.rate(only, d) is None:
                return None
            return (f"These {what} are priced in {only}. The {dn} beside each are converted at the "
                    f"{self.rates.line()}: an estimate. You pay the price in {only}.")
        names = _and(self.currencies)
        if self.mode == "converted":
            return (f"These {what} are priced in {names}. To compare them, other currencies are converted to {dn} at "
                    f"the {self.rates.line()}: an estimate. You pay the price in its own currency.")
        missing = [c for c in self.currencies if self.rates is None or self.rates.rate(c) is None]
        which = "" if self.rates is None else f" for {_and(missing)}"
        return (f"These {what} are priced in {names}, and there's no current exchange rate{which} here, so they're "
                f"grouped by currency and not ranked against each other.")


def _and(words: Iterable[str]) -> str:
    """"GBP", "GBP and EUR", "GBP, EUR and USD"."""
    w = list(words)
    return w[0] if len(w) == 1 else ", ".join(w[:-1]) + " and " + w[-1]


def pricing(currencies: Iterable[str], rates: Rates | None, today: date | None = None,
            display: str = HOME) -> Pricing:
    """m238: `display` is the person's currency. Prices convert only with a current rate for every currency and for
    the display currency itself; otherwise they're grouped, display currency first, and nothing ranks across them."""
    display = (display or HOME).upper()
    counts = Counter(c.upper() for c in currencies if c)
    order = tuple(sorted(counts, key=lambda c: (c != display, -counts[c], c)))
    current = rates if rates is not None and rates.fresh(today or datetime.now(timezone.utc).date()) else None
    if len(order) <= 1:
        return Pricing("one", order, current, display)
    if current is not None and current.rate(display) and all(current.rate(c, display) for c in order):
        return Pricing("converted", order, current, display)
    return Pricing("grouped", order, current, display)


# ---- m255: what a price is, said plainly (Abram, m252) ----------------------------------------------------------------
PRICE_STATES = ("free", "paid", "unknown", "unavailable", "currency_unavailable", "converted_estimate")


def price_status(amount: float | None, currency: str | None, *, display: str = HOME, rates: Rates | None = None,
                 unavailable: bool = False, today: date | None = None) -> dict:
    """Classify one price without ever changing it. `free` only for a confirmed zero; a missing amount is `unknown`
    (or `unavailable` when the provider said it has none); an amount with no recognisable ISO 4217 code is
    `currency_unavailable` (never treated as pounds or as free); a price in another currency is `paid` in its own
    currency, with a `converted_estimate` beside it only when a current rate covers both. The provider's amount and
    currency are always returned unchanged; the estimate is never the payable amount."""
    out = {"amount": amount, "currency": currency, "status": None, "estimate": None}
    if unavailable:
        out["status"] = "unavailable"
    elif amount is None:
        out["status"] = "unknown"
    elif not currency or len(currency) != 3 or not currency.isalpha() or not currency.isupper():
        out["status"] = "currency_unavailable"
    elif amount == 0:
        out["status"] = "free"
    else:
        out["status"] = "paid"
        if currency != display and rates is not None and rates.fresh(today or date.today()) and \
                currency in rates.per_eur and display in rates.per_eur:
            out["estimate"] = {"amount": round(amount / rates.per_eur[currency] * rates.per_eur[display], 2),
                               "currency": display, "kind": "converted_estimate", "as_of": rates.as_of.isoformat()}
    return out
