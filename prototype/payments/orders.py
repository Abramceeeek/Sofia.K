"""A payment lifecycle for ODYS, as a prototype on made-up data (audit, 11 Nov 2026).

**Nothing here takes money.** There is no provider account, no network call, no card and no real price. `MockProvider`
stands in for a payment provider (Stripe, Mollie, …) and signs its notifications the way Stripe documents:
`t=<unix time>,v1=<HMAC-SHA256 of "<t>.<body>">` (docs.stripe.com/webhooks, read 11 Nov 2026). The point is to pin
down, in code and tests, the rules the real thing must keep (decisions/payment-architecture.md and
decisions/payment-security-threat-model.md), before any provider is chosen:

1. **The server sets the price.** An order is made from a catalogue on the server. Nothing the phone sends is a price.
2. **Asking twice is asking once.** The same idempotency key gives the same order; the same key with a different
   request is refused.
3. **A notification is believed only if it is signed, recent and new.** A wrong signature, a timestamp outside five
   minutes, or an event id seen before changes nothing.
4. **A notification is checked against the order.** A different amount or currency changes nothing and is held for a
   person to look at.
5. **Paid is not booked.** The payment's state and the booking's state are separate. Money taken with no booking
   confirmed is a state of its own, and it ends in a booking or a refund, never in silence.
6. **States only move along allowed lines**, whatever order the notifications arrive in.
7. **A refund is never more than was paid**, counting earlier refunds, and is final only when the provider says so.
8. **Everything is written down, in order, and can't be quietly changed.** Each line of the trail carries a hash of
   the line before it.

Standard library only, so it runs anywhere: `python -m pytest prototype/payments`.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from enum import Enum

TOLERANCE_S = 300   # how old a notification may be (Stripe's libraries default to five minutes)


class Pay(str, Enum):
    CREATED = "created"
    PENDING = "pending"                       # a checkout was opened
    REQUIRES_ACTION = "requires_action"       # the bank wants the person to confirm (3-D Secure)
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIALLY_REFUNDED = "partially_refunded"
    REFUNDED = "refunded"
    DISPUTED = "disputed"                     # a chargeback is open


class Booking(str, Enum):
    NONE = "none"               # nothing to book (a subscription, say), or not paid yet
    REQUESTED = "requested"     # paid; the supplier has been asked
    CONFIRMED = "confirmed"
    FAILED = "failed"           # the supplier said no: the money must go back
    CANCELLED = "cancelled"


# From each state, the states a payment may move to. Anything else is refused and written down.
MOVES: dict[Pay, set[Pay]] = {
    Pay.CREATED: {Pay.PENDING, Pay.CANCELLED},
    Pay.PENDING: {Pay.REQUIRES_ACTION, Pay.PROCESSING, Pay.SUCCEEDED, Pay.FAILED, Pay.CANCELLED},
    Pay.REQUIRES_ACTION: {Pay.PROCESSING, Pay.SUCCEEDED, Pay.FAILED, Pay.CANCELLED},
    Pay.PROCESSING: {Pay.SUCCEEDED, Pay.FAILED},
    Pay.SUCCEEDED: {Pay.PARTIALLY_REFUNDED, Pay.REFUNDED, Pay.DISPUTED},
    Pay.PARTIALLY_REFUNDED: {Pay.PARTIALLY_REFUNDED, Pay.REFUNDED, Pay.DISPUTED},
    Pay.DISPUTED: {Pay.SUCCEEDED, Pay.PARTIALLY_REFUNDED, Pay.REFUNDED},   # won, or lost (the bank takes it back)
    Pay.FAILED: set(), Pay.CANCELLED: set(), Pay.REFUNDED: set(),
}

EVENT_TO_STATE = {"payment.requires_action": Pay.REQUIRES_ACTION, "payment.processing": Pay.PROCESSING,
                  "payment.succeeded": Pay.SUCCEEDED, "payment.failed": Pay.FAILED,
                  "payment.cancelled": Pay.CANCELLED, "dispute.opened": Pay.DISPUTED, "dispute.won": Pay.SUCCEEDED}


class Refused(Exception):
    """A request that breaks a rule. The message says which."""


@dataclass(frozen=True)
class Item:
    id: str
    name: str
    amount_minor: int       # pence: whole numbers only, never a float
    currency: str
    needs_booking: bool     # a place on a tour needs the supplier's yes; a subscription doesn't


@dataclass
class Order:
    id: str
    user_id: str
    item_id: str
    quantity: int
    amount_minor: int
    currency: str
    pay: Pay = Pay.CREATED
    booking: Booking = Booking.NONE
    refunded_minor: int = 0
    session_id: str | None = None
    needs_review: list[str] = field(default_factory=list)


@dataclass
class Trail:
    """What happened, in order. Each line carries the hash of the line before, so a changed or missing line shows."""
    lines: list[dict] = field(default_factory=list)

    def add(self, order_id: str, what: str, **detail) -> None:
        prev = self.lines[-1]["hash"] if self.lines else ""
        body = {"n": len(self.lines), "order": order_id, "what": what, "detail": detail, "prev": prev}
        body["hash"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        self.lines.append(body)

    def intact(self) -> bool:
        prev = ""
        for i, line in enumerate(self.lines):
            body = {k: line[k] for k in ("n", "order", "what", "detail", "prev")}
            if line["n"] != i or line["prev"] != prev or \
                    line["hash"] != hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest():
                return False
            prev = line["hash"]
        return True


def sign(body: bytes, secret: str, t: int) -> str:
    mac = hmac.new(secret.encode(), f"{t}.".encode() + body, hashlib.sha256).hexdigest()
    return f"t={t},v1={mac}"


class MockProvider:
    """Stands in for the payment provider: opens a made-up checkout, and makes signed notifications."""

    def __init__(self, secret: str = "whsec_made_up_for_tests"):
        self.secret, self._n = secret, 0

    def checkout(self, order: Order) -> tuple[str, str]:
        self._n += 1
        sid = f"cs_test_{self._n:06d}"
        return sid, f"https://checkout.invalid/pay/{sid}"     # .invalid never resolves (RFC 2606)

    def event(self, kind: str, order: Order, t: int, *, amount_minor: int | None = None, currency: str | None = None,
              refund_minor: int | None = None, event_id: str | None = None) -> tuple[bytes, str]:
        self._n += 1
        body = json.dumps({"id": event_id or f"evt_{self._n:06d}", "type": kind, "session": order.session_id,
                           "order": order.id, "currency": currency or order.currency,
                           "amount_minor": order.amount_minor if amount_minor is None else amount_minor,
                           "refund_minor": refund_minor}).encode()
        return body, sign(body, self.secret, t)


class Orders:
    def __init__(self, catalogue: dict[str, Item], provider: MockProvider, webhook_secret: str):
        self.catalogue, self.provider, self.secret = catalogue, provider, webhook_secret
        self.orders: dict[str, Order] = {}
        self.trail = Trail()
        self._by_key: dict[str, tuple[str, str]] = {}     # idempotency key -> (request fingerprint, order id)
        self._seen: set[str] = set()                       # event ids already handled
        self._refund_keys: dict[str, int] = {}              # refund request key -> amount (asking twice is once)
        self._refunds_waiting: dict[str, list[int]] = {}    # order id -> amounts asked for and not yet confirmed

    # ---- 1 and 2: the order is priced here, once --------------------------------------------------------------
    def create(self, user_id: str, item_id: str, quantity: int, key: str, **from_the_phone) -> Order:
        """`from_the_phone` is whatever else the app sent (a price, a currency, a discount). It is never used: it is
        written down, so a phone that sends a price it shouldn't shows up in the trail."""
        if item_id not in self.catalogue:
            raise Refused("no such item")
        if not 1 <= quantity <= 20:
            raise Refused("quantity is 1 to 20")
        if not 8 <= len(key) <= 255:
            raise Refused("an idempotency key of 8 to 255 characters")
        print_ = hashlib.sha256(json.dumps([user_id, item_id, quantity]).encode()).hexdigest()
        if key in self._by_key:
            seen, oid = self._by_key[key]
            if seen != print_:
                raise Refused("that idempotency key was used for a different order")
            return self.orders[oid]
        item = self.catalogue[item_id]
        order = Order(id=f"ord_{len(self.orders) + 1:06d}", user_id=user_id, item_id=item_id, quantity=quantity,
                      amount_minor=item.amount_minor * quantity, currency=item.currency)
        self.orders[order.id], self._by_key[key] = order, (print_, order.id)
        self.trail.add(order.id, "created", amount_minor=order.amount_minor, currency=order.currency,
                       ignored_from_phone=sorted(from_the_phone))
        return order

    def open_checkout(self, order_id: str, user_id: str) -> str:
        order = self._mine(order_id, user_id)
        if order.pay is Pay.PENDING and order.session_id:
            return f"https://checkout.invalid/pay/{order.session_id}"     # the same page, not a second charge
        self._move(order, Pay.PENDING, "checkout opened")
        order.session_id, url = self.provider.checkout(order)
        return url

    def _mine(self, order_id: str, user_id: str) -> Order:
        order = self.orders.get(order_id)
        if order is None or order.user_id != user_id:
            raise Refused("no such order")      # the same answer for "not yours" and "doesn't exist"
        return order

    def _move(self, order: Order, to: Pay, why: str) -> bool:
        if to not in MOVES[order.pay]:
            self.trail.add(order.id, "refused move", frm=order.pay.value, to=to.value, why=why)
            return False
        self.trail.add(order.id, "moved", frm=order.pay.value, to=to.value, why=why)
        order.pay = to
        return True

    # ---- 3, 4 and 6: a notification from the provider --------------------------------------------------------------
    def notify(self, body: bytes, signature: str, now: int) -> str:
        """Returns what was done: "applied", "duplicate", "held" (for a person to look at) or "ignored" (a move the
        state doesn't allow). Raises `Refused` for a notification that can't be believed (the provider's sender then
        gets an error and tries again; a forger learns nothing)."""
        try:
            parts = dict(p.split("=", 1) for p in signature.split(","))
            t = int(parts["t"])
            given = parts["v1"]
        except (KeyError, ValueError):
            raise Refused("unsigned")
        expected = sign(body, self.secret, t).split("v1=")[1]
        if not hmac.compare_digest(given, expected):
            raise Refused("bad signature")
        if abs(now - t) > TOLERANCE_S:
            raise Refused("too old")            # a real notification, replayed later
        e = json.loads(body)
        if e["id"] in self._seen:
            return "duplicate"                  # providers send the same event more than once: do it once
        order = self.orders.get(e.get("order", ""))
        if order is None or order.session_id != e.get("session"):
            raise Refused("unknown order")      # not marked seen: nothing was done
        self._seen.add(e["id"])
        kind = e["type"]
        if e["currency"] != order.currency or (kind == "payment.succeeded" and e["amount_minor"] != order.amount_minor):
            order.needs_review.append(e["id"])
            self.trail.add(order.id, "held: amount or currency differs", event=e["id"], said=e["amount_minor"],
                           said_currency=e["currency"])
            return "held"
        if kind == "refund.succeeded":
            return self._refunded(order, int(e["refund_minor"] or 0), e["id"])
        to = EVENT_TO_STATE.get(kind)
        if to is None or not self._move(order, to, kind):
            return "ignored"
        if to is Pay.SUCCEEDED and order.booking is Booking.NONE and self.catalogue[order.item_id].needs_booking:
            order.booking = Booking.REQUESTED       # rule 5: paid, and the supplier has been asked. Not "booked"
            self.trail.add(order.id, "booking requested")
        return "applied"

    # ---- 5: the supplier's answer --------------------------------------------------------------------------------
    def supplier_says(self, order_id: str, confirmed: bool) -> None:
        order = self.orders[order_id]
        if order.booking is not Booking.REQUESTED:
            raise Refused("no booking is waiting")
        order.booking = Booking.CONFIRMED if confirmed else Booking.FAILED
        self.trail.add(order.id, "booking " + order.booking.value)

    def owed_back(self) -> list[Order]:
        """Money taken for something that can't be delivered: each of these must be refunded, by a person or a job."""
        return [o for o in self.orders.values() if o.booking is Booking.FAILED
                and o.pay in (Pay.SUCCEEDED, Pay.PARTIALLY_REFUNDED)]

    # ---- 7: refunds ----------------------------------------------------------------------------------------------
    def ask_refund(self, order_id: str, amount_minor: int, key: str) -> int:
        """Asks the provider for a refund. The order's state changes only when the provider confirms (`notify`)."""
        order = self.orders[order_id]
        if key in self._refund_keys:
            return self._refund_keys[key]       # asked twice: one refund
        if order.pay not in (Pay.SUCCEEDED, Pay.PARTIALLY_REFUNDED):
            raise Refused("nothing to refund")
        waiting = sum(self._refunds_waiting.get(order_id, []))
        if amount_minor <= 0 or order.refunded_minor + waiting + amount_minor > order.amount_minor:
            raise Refused("more than was paid")
        self._refund_keys[key] = amount_minor
        self._refunds_waiting.setdefault(order_id, []).append(amount_minor)   # counted until the provider confirms
        self.trail.add(order.id, "refund asked", amount_minor=amount_minor)
        return amount_minor

    def _refunded(self, order: Order, amount_minor: int, event_id: str) -> str:
        if amount_minor <= 0 or order.refunded_minor + amount_minor > order.amount_minor:
            order.needs_review.append(event_id)
            self.trail.add(order.id, "held: a refund larger than the payment", event=event_id, said=amount_minor)
            return "held"
        to = Pay.REFUNDED if order.refunded_minor + amount_minor == order.amount_minor else Pay.PARTIALLY_REFUNDED
        if not self._move(order, to, "refund.succeeded"):
            return "ignored"
        order.refunded_minor += amount_minor
        waiting = self._refunds_waiting.get(order.id, [])
        if amount_minor in waiting:
            waiting.remove(amount_minor)        # that request is settled
        if order.pay is Pay.REFUNDED and order.booking is Booking.REQUESTED:
            order.booking = Booking.CANCELLED
        return "applied"
