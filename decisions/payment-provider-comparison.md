# Payment providers compared (independent review, 11 Nov 2026)

**Decision.** When ODYS first takes money, use **Stripe**, through its hosted checkout page. Keep **Mollie** as the named second choice. Use **Apple's and Google's own billing** for anything digital sold inside the apps, because the stores require it. Don't approach Adyen, Checkout.com or Worldpay yet: they sell through a sales team and set minimums a new company won't meet. **Don't open any account now**: there is no company, no bank account and no product anyone has agreed to pay for. This note is so the choice takes an hour when that day comes.

Not advice from a payments or tax professional. Every price below was read from the provider's own page on 11 Nov 2026 unless marked; prices change, so re-read before signing anything.

## Why Stripe first

1. **It can be built and tested before the company exists.** "Test your integration in a sandbox … these transactions don't move funds"; live mode needs "verify your business and complete its activation requirements" (docs.stripe.com/testing, /get-started/account/activate).
2. **Its hosted page keeps card details away from ODYS entirely**, which keeps the card-industry paperwork at its smallest (see the threat model).
3. **It fits the rule ODYS already has.** "Never hold trip money. Use Stripe Connect direct charges only" (CLAUDE.md, D39). With direct charges the payment lands on the host's own Stripe balance, and "refunds and chargebacks reduce the connected account's balance" (docs.stripe.com/connect/charges).
4. **Public UK prices, no monthly fee, no minimum.**
5. **It documents the hard parts plainly:** signed notifications, retries for up to three days, no promise about order, and idempotency keys (docs.stripe.com/webhooks, /api/idempotent_requests). The prototype's tests are written to those statements.

What counts against it: it is dearer than Mollie on UK cards; its restricted list names "Travel reservation services and clubs" (stripe.com/legal/restricted-businesses), so anything that looks like booking travel needs Stripe's say-so first; and like every provider it can hold a reserve or pause payouts on a new account.

## The providers

| | Stripe | Mollie | PayPal | Paddle | Adyen | Checkout.com, Worldpay |
|---|---|---|---|---|---|---|
| **Suits a new UK company?** | Yes: self-serve | Yes: self-serve (UNVERIFIED for travel) | Yes | Yes, for digital goods only | No: "we do have a minimum invoice depending on industry or business model" | No: sales-led with minimum volumes (third-party reports; UNVERIFIED) |
| **UK consumer card** | 1.5% + 20p | 1.20% + £0.20 | 2.9% + 30p ("all other commercial transactions") | 5% + US$0.50, all in | A fixed fee plus the card's own cost; not published as one rate | Not published |
| **EEA card** | 2.5% + 20p | 2.90% + £0.20 (also UK business cards) | + 1.29% | included | — | — |
| **Other international card** | 3.15% + 20p | 3.25% + £0.20 | + 1.99% | included | — | — |
| **Currency conversion** | + 2% | UNVERIFIED | 3% above the base rate | included | — | — |
| **Amex** | In the card rates (as extracted; re-check) | UK 2.50% + £0.20; other 2.60% + £0.20 | 3.5% on advanced card processing | included | — | — |
| **A lost dispute** | £20 | UNVERIFIED | £14 chargeback fee | Paddle handles chargebacks | — | — |
| **Subscriptions** | Billing: 0.7% of billing volume, pay as you go | "Recurring" listed; price UNVERIFIED | Not seen (page cut off) | Yes | — | — |
| **Hosted page with a price set per order** | Yes: a Checkout Session made by the server | Yes (UNVERIFIED detail) | Yes | Yes | Yes | Yes |
| **Payment links** | Yes, no extra charge | Yes | Yes | Yes | Yes | — |
| **Apple Pay, Google Pay** | Built into Checkout | "Apple Pay: rate defined by card used" | Yes | Yes | Yes | Yes |
| **Paying independent hosts** | Connect (direct charges) | Mollie Connect (UNVERIFIED) | Multiparty (UNVERIFIED) | No | Adyen for Platforms | — |
| **Who is the seller in law** | ODYS, or the host with direct charges | ODYS | ODYS | **Paddle** (it handles sales tax abroad) | ODYS | ODYS |
| **Travel** | "Travel reservation services and clubs" restricted; airlines and cruises prohibited | UNVERIFIED | UNVERIFIED | Digital products only | Sales decision | Sales decision |
| **Refund: are the fees returned?** | UNVERIFIED | UNVERIFIED | No: "the fees you originally paid … are not returned" | UNVERIFIED | — | — |

Square, SumUp and GoCardless were not researched: the first two are built for shops and tills, and bank debits are slow to confirm, which suits rent, not a ticket for Saturday.

## What three sales would cost

My arithmetic from the prices above, not a quote. Store commissions are in the last two columns for the one case where they apply.

| Sale | Stripe | Mollie | PayPal | Paddle | Apple in-app | Google Play |
|---|---|---|---|---|---|---|
| **£9.99 subscription charge, UK card** | £0.35, plus £0.07 Billing = **£0.42** (4.2%) | **£0.32** (3.2%), recurring fee UNVERIFIED | **£0.59** (5.9%) | £0.50 + US$0.50 (roughly 9% at about 80p to the dollar; the rate was not checked) | **£1.50** (15%, Small Business Program) | **£1.50** (10% + 5% billing fee, UK since 30 June 2026) |
| **£60 experience ticket, UK card** | **£1.10** (1.8%) | **£0.92** (1.5%) | **£2.04** (3.4%) | not for physical services | not allowed (3.1.3(e)) | not allowed |
| **£400 on an overseas card, converted** | £20.80 (5.2%) | £13.20 (3.3%), conversion fee UNVERIFIED | £19.86, or £31.86 if PayPal converts (8%) | — | — | — |

Two things this shows:
- On a £9.99 digital subscription, the stores take about **four times** what a card provider takes. That is the price of selling inside the app, and for small developers it is 15%, not 30%.
- On an overseas card the fee is several times the UK one. A trip sold to visitors from abroad should be priced with that in mind.

## Before committing to Stripe, ask Stripe

1. "We plan trips and may charge a service fee for a single experience, paid to the host by direct charge. Is that 'travel reservation services'? Do you need to approve it?"
2. What reserve or payout delay applies to a new UK account in this category? (The agreement allows a reserve; the first payout is "typically … 7-14 days".)
3. Connect: the fee per active connected account and per payout (not on the page read: UNVERIFIED), and whether the platform or the host carries dispute fees under direct charges with each fee setting.
4. Are the original processing fees returned on a refund?
5. Which entity types can open a UK account (sole trader, limited company): not confirmed from a primary page.

## Sources (all read 11 Nov 2026)

- Stripe UK prices: https://stripe.com/gb/pricing (the three card rates re-read directly by the reviewer; the rest via a summarising fetch, so re-check exact figures). Restricted businesses: https://stripe.com/legal/restricted-businesses . Checkout: https://docs.stripe.com/payments/checkout/how-checkout-works . Webhooks: https://docs.stripe.com/webhooks . Idempotency: https://docs.stripe.com/api/idempotent_requests . Connect charge types: https://docs.stripe.com/connect/charges . Testing and activation: https://docs.stripe.com/testing , https://docs.stripe.com/get-started/account/activate . Payouts: https://docs.stripe.com/payouts . Services agreement: https://stripe.com/gb/legal/ssa .
- Mollie UK prices: https://www.mollie.com/gb/pricing (read directly).
- PayPal UK fees: https://www.paypal.com/uk/business/paypal-business-fees (the page was cut off; subscription pricing not seen).
- Paddle: https://www.paddle.com/pricing ("5% + 50¢ per Checkout transaction", read directly).
- Adyen: https://www.adyen.com/pricing ("We do not have monthly fees, set-up fees, integration fees or closure fees. We do have a minimum invoice depending on industry or business model", read directly).
- Checkout.com and Worldpay: third-party comparison sites only. UNVERIFIED.
- Apple's Small Business Program (15%): https://developer.apple.com/app-store/small-business-program/ . Google Play service fees: https://support.google.com/googleplay/android-developer/answer/112622 (page title "Service fees", confirmed).
