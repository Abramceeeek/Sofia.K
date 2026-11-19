"""The rules a real payment system for ODYS must keep, on made-up data (prototype/payments/orders.py).
Each test names the attack or accident it stands against (decisions/payment-security-threat-model.md)."""

import json

import pytest

from orders import Booking, Item, MockProvider, Orders, Pay, Refused, sign

SECRET = "whsec_made_up_for_tests"
NOW = 1_800_000_000
CATALOGUE = {"tour": Item("tour", "A made-up walking tour", 6000, "GBP", needs_booking=True),
             "plus": Item("plus", "A made-up yearly plan", 999, "GBP", needs_booking=False)}


@pytest.fixture
def shop():
    provider = MockProvider(SECRET)
    return Orders(CATALOGUE, provider, SECRET), provider


def paid(orders, provider, item="tour", user="u1", key="key-0001"):
    order = orders.create(user, item, 1, key)
    orders.open_checkout(order.id, user)
    assert orders.notify(*provider.event("payment.succeeded", order, NOW), NOW) == "applied"
    return order


# ---- T5: changing the price ------------------------------------------------------------------------------------

def test_the_price_comes_from_the_server_whatever_the_phone_sends(shop):
    orders, _ = shop
    order = orders.create("u1", "tour", 2, "key-0001", amount_minor=1, currency="XXX", discount=100)
    assert (order.amount_minor, order.currency) == (12000, "GBP")
    assert orders.trail.lines[-1]["detail"]["ignored_from_phone"] == ["amount_minor", "currency", "discount"]


def test_an_unknown_item_or_a_silly_quantity_is_refused(shop):
    orders, _ = shop
    for item, n in [("free-holiday", 1), ("tour", 0), ("tour", -3), ("tour", 500)]:
        with pytest.raises(Refused):
            orders.create("u1", item, n, "key-0001")


def test_asking_twice_makes_one_order_and_one_checkout(shop):
    orders, _ = shop
    a, b = orders.create("u1", "tour", 1, "key-0001"), orders.create("u1", "tour", 1, "key-0001")
    assert a is b and len(orders.orders) == 1
    assert orders.open_checkout(a.id, "u1") == orders.open_checkout(a.id, "u1")     # a double tap: the same page
    with pytest.raises(Refused, match="different order"):
        orders.create("u1", "tour", 3, "key-0001")                                   # the key, reused for more


def test_one_person_cannot_open_or_see_another_s_order(shop):
    orders, _ = shop
    order = orders.create("u1", "tour", 1, "key-0001")
    with pytest.raises(Refused, match="no such order"):
        orders.open_checkout(order.id, "someone-else")


# ---- T6: a forged "payment succeeded" ---------------------------------------------------------------------------

def test_a_notification_signed_with_the_wrong_secret_changes_nothing(shop):
    orders, _ = shop
    order = orders.create("u1", "tour", 1, "key-0001")
    orders.open_checkout(order.id, "u1")
    body, _ = MockProvider(SECRET).event("payment.succeeded", order, NOW)
    for forged in (sign(body, "a-guessed-secret", NOW), "", "t=abc,v1=00", f"t={NOW},v1=", f"v1={'0' * 64}"):
        with pytest.raises(Refused):
            orders.notify(body, forged, NOW)
    assert order.pay is Pay.PENDING and order.booking is Booking.NONE


def test_a_real_signature_does_not_cover_a_changed_body(shop):
    orders, provider = shop
    order = orders.create("u1", "tour", 1, "key-0001")
    orders.open_checkout(order.id, "u1")
    body, signature = provider.event("payment.failed", order, NOW)
    tampered = body.replace(b"payment.failed", b"payment.succeeded")
    with pytest.raises(Refused, match="bad signature"):
        orders.notify(tampered, signature, NOW)
    assert order.pay is Pay.PENDING


def test_a_notification_for_another_checkout_is_refused(shop):
    orders, provider = shop
    mine, theirs = orders.create("u1", "tour", 1, "key-0001"), orders.create("u2", "tour", 1, "key-0002")
    orders.open_checkout(mine.id, "u1")
    orders.open_checkout(theirs.id, "u2")
    body = json.dumps({"id": "evt_x", "type": "payment.succeeded", "session": theirs.session_id, "order": mine.id,
                       "currency": "GBP", "amount_minor": 6000, "refund_minor": None}).encode()
    with pytest.raises(Refused, match="unknown order"):
        orders.notify(body, sign(body, SECRET, NOW), NOW)     # even correctly signed: the pair doesn't match
    assert mine.pay is Pay.PENDING


# ---- T7: a real notification, sent again ---------------------------------------------------------------------------

def test_an_old_notification_replayed_later_is_refused(shop):
    orders, provider = shop
    order = orders.create("u1", "tour", 1, "key-0001")
    orders.open_checkout(order.id, "u1")
    body, signature = provider.event("payment.succeeded", order, NOW)
    with pytest.raises(Refused, match="too old"):
        orders.notify(body, signature, NOW + 301)
    assert order.pay is Pay.PENDING


def test_the_same_notification_twice_is_done_once(shop):
    orders, provider = shop
    order = orders.create("u1", "tour", 1, "key-0001")
    orders.open_checkout(order.id, "u1")
    event = provider.event("payment.succeeded", order, NOW)
    assert [orders.notify(*event, NOW), orders.notify(*event, NOW + 5)] == ["applied", "duplicate"]
    assert sum(line["what"] == "booking requested" for line in orders.trail.lines) == 1


def test_a_refund_notification_sent_twice_refunds_once(shop):
    orders, provider = shop
    order = paid(orders, provider)
    orders.ask_refund(order.id, 2000, "refund-01")
    event = provider.event("refund.succeeded", order, NOW, refund_minor=2000)
    assert [orders.notify(*event, NOW), orders.notify(*event, NOW)] == ["applied", "duplicate"]
    assert order.refunded_minor == 2000 and order.pay is Pay.PARTIALLY_REFUNDED


# ---- amounts and currencies ---------------------------------------------------------------------------------------

@pytest.mark.parametrize("said", [dict(amount_minor=100), dict(amount_minor=600000), dict(currency="USD")])
def test_a_payment_for_a_different_amount_or_currency_is_held_for_a_person(shop, said):
    orders, provider = shop
    order = orders.create("u1", "tour", 1, "key-0001")
    orders.open_checkout(order.id, "u1")
    assert orders.notify(*provider.event("payment.succeeded", order, NOW, **said), NOW) == "held"
    assert order.pay is Pay.PENDING and order.booking is Booking.NONE and len(order.needs_review) == 1


# ---- paid is not booked ---------------------------------------------------------------------------------------------

def test_a_paid_tour_is_requested_not_booked_until_the_supplier_says_so(shop):
    orders, provider = shop
    order = paid(orders, provider)
    assert (order.pay, order.booking) == (Pay.SUCCEEDED, Booking.REQUESTED)
    orders.supplier_says(order.id, confirmed=True)
    assert order.booking is Booking.CONFIRMED and orders.owed_back() == []


def test_money_taken_for_a_booking_that_failed_is_owed_back_until_refunded(shop):
    orders, provider = shop
    order = paid(orders, provider)
    orders.supplier_says(order.id, confirmed=False)
    assert orders.owed_back() == [order]
    orders.ask_refund(order.id, 6000, "refund-01")
    orders.notify(*provider.event("refund.succeeded", order, NOW, refund_minor=6000), NOW)
    assert order.pay is Pay.REFUNDED and orders.owed_back() == []


def test_a_subscription_has_nothing_to_book(shop):
    orders, provider = shop
    order = paid(orders, provider, item="plus")
    assert (order.pay, order.booking) == (Pay.SUCCEEDED, Booking.NONE)
    with pytest.raises(Refused):
        orders.supplier_says(order.id, confirmed=True)


# ---- states only move along allowed lines ---------------------------------------------------------------------------

def test_notifications_out_of_order_never_undo_a_payment(shop):
    orders, provider = shop
    order = paid(orders, provider)
    for late in ("payment.processing", "payment.requires_action", "payment.failed", "payment.cancelled"):
        assert orders.notify(*provider.event(late, order, NOW), NOW) == "ignored"
    assert order.pay is Pay.SUCCEEDED
    assert sum(line["what"] == "refused move" for line in orders.trail.lines) == 4


def test_a_failed_payment_cannot_become_paid(shop):
    orders, provider = shop
    order = orders.create("u1", "tour", 1, "key-0001")
    orders.open_checkout(order.id, "u1")
    orders.notify(*provider.event("payment.failed", order, NOW), NOW)
    assert orders.notify(*provider.event("payment.succeeded", order, NOW), NOW) == "ignored"
    assert order.pay is Pay.FAILED and order.booking is Booking.NONE


def test_a_dispute_can_be_won_or_lost(shop):
    orders, provider = shop
    order = paid(orders, provider)
    orders.notify(*provider.event("dispute.opened", order, NOW), NOW)
    assert order.pay is Pay.DISPUTED
    orders.notify(*provider.event("dispute.won", order, NOW), NOW)
    assert order.pay is Pay.SUCCEEDED
    orders.notify(*provider.event("dispute.opened", order, NOW), NOW)
    orders.notify(*provider.event("refund.succeeded", order, NOW, refund_minor=6000), NOW)     # lost: taken back
    assert order.pay is Pay.REFUNDED


# ---- refunds ----------------------------------------------------------------------------------------------------------

def test_refunds_never_add_up_to_more_than_was_paid(shop):
    orders, provider = shop
    order = paid(orders, provider)
    orders.ask_refund(order.id, 4000, "refund-01")
    with pytest.raises(Refused, match="more than was paid"):
        orders.ask_refund(order.id, 2001, "refund-02")       # 4000 is already asked for, though not yet confirmed
    assert orders.ask_refund(order.id, 4000, "refund-01") == 4000            # the same request again: one refund
    orders.notify(*provider.event("refund.succeeded", order, NOW, refund_minor=4000), NOW)
    orders.ask_refund(order.id, 2000, "refund-03")
    orders.notify(*provider.event("refund.succeeded", order, NOW, refund_minor=2000), NOW)
    assert (order.pay, order.refunded_minor) == (Pay.REFUNDED, 6000)
    with pytest.raises(Refused, match="nothing to refund"):
        orders.ask_refund(order.id, 1, "refund-04")


def test_asking_for_a_refund_changes_nothing_until_the_provider_confirms(shop):
    orders, provider = shop
    order = paid(orders, provider)
    orders.ask_refund(order.id, 6000, "refund-01")
    assert (order.pay, order.refunded_minor) == (Pay.SUCCEEDED, 0)


def test_a_refund_notification_larger_than_the_payment_is_held(shop):
    orders, provider = shop
    order = paid(orders, provider)
    assert orders.notify(*provider.event("refund.succeeded", order, NOW, refund_minor=6001), NOW) == "held"
    assert (order.pay, order.refunded_minor) == (Pay.SUCCEEDED, 0)


def test_nothing_can_be_refunded_before_it_is_paid(shop):
    orders, _ = shop
    order = orders.create("u1", "tour", 1, "key-0001")
    with pytest.raises(Refused, match="nothing to refund"):
        orders.ask_refund(order.id, 100, "refund-01")


# ---- the trail ----------------------------------------------------------------------------------------------------------

def test_the_trail_shows_a_changed_or_missing_line(shop):
    orders, provider = shop
    paid(orders, provider)
    assert orders.trail.intact() and len(orders.trail.lines) >= 4
    orders.trail.lines[1]["detail"]["to"] = "succeeded"         # someone edits history
    assert not orders.trail.intact()
    orders.trail.lines[1]["detail"]["to"] = "pending"
    assert orders.trail.intact()
    del orders.trail.lines[2]                                   # someone removes a line
    assert not orders.trail.intact()
