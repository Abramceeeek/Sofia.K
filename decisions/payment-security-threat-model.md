# Payment security threat model (independent review, 11 Nov 2026)

**Decision.** If payments are built the way `payment-architecture.md` sets out (a hosted checkout page, the server pricing every order, the provider's signed message as the only proof of payment), most of the classic payment attacks have nothing to attack: ODYS never sees a card, and nothing the phone says is believed. What remains is a short list of rules, and each is already a passing test on made-up data (`prototype/payments/test_orders.py`, 24 tests). Build payments only against this list, and get an outside test before the first real charge.

No payment code exists in the Brain or the apps today, so nothing here is a finding against the current system. One existing route has a shape that must not be copied (T5).

## What is being protected, from whom

- **Assets:** customers' money; hosts' payouts; ODYS's own fee; the truth of each order's state; the provider keys; the record of what happened.
- **Who might try:** a customer who wants something for nothing; a customer who pays and then disputes; someone outside sending made-up messages to the server; a host gaming payouts or refunds; someone with a stolen card; someone with access to the server or the repository.
- **Where trust changes hands:** phone to Brain (nothing from the phone is trusted for money); Brain to provider (ODYS's secret key); provider to Brain (signed messages); Brain to host or supplier (their answer is the booking).

## The threats, the rule that stops each, and its test

| # | Threat | How it would go | Rule | Test in the prototype |
|---|---|---|---|---|
| T1 | **Card theft from ODYS** | An attacker reads card numbers from the app, the server or its logs | ODYS never has them: the card is typed on the provider's page | By design; nothing to test. Review: no card field in either app, ever |
| T2 | **A changed checkout page** | A script on ODYS's own page skims the card | No ODYS page carries a card form. The app opens the provider's page in the phone's own browser sheet, not a web view | Review at build time |
| T3 | **Something for nothing: a cheaper price** | The phone sends `amount: 1` | The server prices the order from its own catalogue; extra fields are ignored and written down | `test_the_price_comes_from_the_server_whatever_the_phone_sends` |
| T4 | **Paying twice by accident** | A double tap, a retry on a slow connection | A request key makes one order; one open checkout per order | `test_asking_twice_makes_one_order_and_one_checkout` |
| T5 | **Price taken from the phone and trusted later** | A route accepts a price "as the search found it" and a later feature charges it | Never reuse a phone-supplied price for money. **Today `POST /v1/trips/stays/compare` takes the stay's price from the phone (`StayRefIn.price_total`)**: harmless, because it is only shown back to the same person, and it must stay that way | Rule 1 above; add a comment on that schema when payments start |
| T6 | **A forged "payment succeeded"** | Someone posts a made-up message to the notification route | Believe a message only if its signature, made with a secret only the provider and ODYS hold, matches the exact bytes received | `test_a_notification_signed_with_the_wrong_secret_changes_nothing`, `test_a_real_signature_does_not_cover_a_changed_body` |
| T7 | **A real message, replayed** | A captured, validly signed message is sent again later, or for another order | Refuse messages older than five minutes; do each event id once; check the message's order and checkout belong together | `test_an_old_notification_replayed_later_is_refused`, `test_the_same_notification_twice_is_done_once`, `test_a_notification_for_another_checkout_is_refused` |
| T8 | **Wrong amount or currency** | A payment arrives for £1 against a £60 order, or in another currency | Compare with the order; on any difference change nothing and hold it for a person | `test_a_payment_for_a_different_amount_or_currency_is_held_for_a_person` |
| T9 | **Paid, never booked** | The money is taken and the host or supplier says no, or never answers | Payment and booking are separate states; "paid with a failed booking" is listed until refunded | `test_money_taken_for_a_booking_that_failed_is_owed_back_until_refunded` |
| T10 | **Messages out of order** | "Failed" arrives after "succeeded"; a refund before the payment | States only move along allowed lines; anything else is refused and written down | `test_notifications_out_of_order_never_undo_a_payment`, `test_a_failed_payment_cannot_become_paid` |
| T11 | **Refund fraud** | Refunds asked for twice, or for more than was paid; a refund asked for before any payment | Total refunds, including those asked for and not yet confirmed, never exceed the payment; a refund is final only on the provider's word | `test_refunds_never_add_up_to_more_than_was_paid`, `test_nothing_can_be_refunded_before_it_is_paid`, `test_a_refund_notification_larger_than_the_payment_is_held` |
| T12 | **Someone else's order** | One person opens or pays another's order to learn about it | An order answers only to its owner, and "not yours" looks the same as "doesn't exist" | `test_one_person_cannot_open_or_see_another_s_order` |
| T13 | **"It says paid on my phone"** | The app shows success because the browser came back to it | The return from the checkout page proves nothing; only the provider's message, or asking the provider, does | Design rule; an end-to-end test at build time |
| T14 | **Chargebacks** | A customer disputes a genuine payment | A disputed state; keep what a dispute needs (the order, the times, the confirmation, the day's ratings, messages) | `test_a_dispute_can_be_won_or_lost` |
| T15 | **Changed history** | Someone with database access edits what happened | Each line of the trail carries a hash of the one before | `test_the_trail_shows_a_changed_or_missing_line` |
| T16 | **A leaked provider key** | The secret key is in the repository, a log, a chat or an old laptop | Keys only in the host's environment; a restricted key for the Brain (create checkouts and refunds, nothing else); separate test and live keys; rotate on any doubt | Secret scanning in CI (~1 h); never print a key, even masked |
| T17 | **Stolen cards used through ODYS** | Tickets bought with stolen cards, then charged back to ODYS or the host | The provider's fraud checks and the bank's own check (3-D Secure) on the hosted page; limits on new accounts; no instant resale value in what is sold | Provider settings; review monthly |
| T18 | **A host takes the money and doesn't deliver** | A new host, a full day sold, nobody turns up | Pay hosts after the experience, not before; cap what a new host can sell; a person reviews first payouts | Process, then code |

## What stays ODYS's job even with a hosted page

- **Card-industry rules (PCI DSS).** A merchant that sends customers to the provider's own page is in the smallest category, self-assessment "A": payment processing is "fully outsourced" to a validated provider. It is not zero: the pages and scripts that send people to the checkout still have to be looked after, and an embedded frame would bring more duties than a full redirect. (PCI Security Standards Council's descriptions, via secondary sources in this session: confirm against the current SAQ A document before launch. UNVERIFIED.)
- **The bank's extra check (Strong Customer Authentication).** The hosted page handles it. ODYS's part is to cope with the "requires action" state and with people who abandon it.
- **The notification route itself.** It must read the raw bytes before anything parses them, check the signature with the provider's own library (the prototype's check shows the shape; it is not a substitute), answer quickly, and be safe to call again. Stripe says of its own messages: retried for up to three days; "Stripe doesn't guarantee the delivery of events in the order that they're generated"; duplicates happen (docs.stripe.com/webhooks). So a daily job that asks the provider for every payment and compares is part of the design, not an extra.
- **Rate limits and size limits** on the order and notification routes (this branch's `ops.py` already gives both).
- **Logs** with order ids and states, never names, emails or anything from the card.
- **Money never sits in ODYS's account for someone else** (D39). If a design ever needs it to, stop: that is a regulated payment service.

## Before the first real charge

1. The rules above as tests against the real provider's test mode, not only the prototype.
2. A walk through every state with a real phone, including the abandoned bank check and a refund.
3. A second person able to refund and to answer a payment problem when Abram can't (the safety helper's agreement doesn't cover money).
4. An outside penetration test of the Brain and both apps (a cost: Abram's decision).
5. The solicitor's answers to the questions in `payment-architecture.md`.

## Sources (read 11 Nov 2026)

- Stripe on notifications, their signing, retries and order: https://docs.stripe.com/webhooks . Idempotency keys: https://docs.stripe.com/api/idempotent_requests . Hosted checkout: https://docs.stripe.com/payments/checkout/how-checkout-works .
- PCI DSS self-assessment "A" for outsourced payment pages: PCI Security Standards Council FAQ and secondary summaries (jscrambler.com, compassitc.com, feroot.com, via search). Not read from the Council's own SAQ A document: UNVERIFIED.
