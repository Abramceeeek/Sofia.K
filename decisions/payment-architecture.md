# Payment architecture (independent review, 11 Nov 2026)

**Decision.** Payments are premature, and building them now would be building the wrong thing. There is no company, no bank account, and no evidence yet that anyone will pay (Test D hasn't run). What can be settled now is **what ODYS would be selling, who the seller is in law, who holds the money and who refunds it**, because those four answers, not the choice of provider, decide the design. This note settles them, and a small program with 24 tests (`prototype/payments/`) pins down the rules the real thing must keep.

**The order to do things in:**

| Step | What | Money handled by ODYS | When |
|---|---|---|---|
| 0 | Nothing. Keep linking out; earn nothing | None | Now, through Test B |
| 1 | Affiliate links for the bookings people already make elsewhere | None (the programme pays ODYS) | After incorporation; needs each programme's approval and a visible disclosure |
| 2 | One paid experience, paid to the host's own account, ODYS takes a fee | Only its own fee | Only if Test D shows people pay. The first real payment code |
| 3 | A subscription for the planning itself | Through Apple and Google | Only once people come back unprompted (the model needs about five rated days to know someone: `brain-global-readiness.md`) |
| 4 | Selling travel itself (a flight, a room, a combined trip) | All of it | **Recommended: never as the seller.** It makes ODYS a travel organiser in law |

Not legal, tax or payments advice. The legal points are from the statutes and official guidance read on 11 Nov 2026 (sources at the end) and each needs a solicitor before money moves.

## 1. Four questions first

For anything ODYS might charge for:

| | Who is the seller? | Who holds the money? | Who refunds? | What it triggers |
|---|---|---|---|---|
| **A link out to book elsewhere** (today) | The airline, hotel or site | They do | They do | Nothing for payments. A duty to say clearly when a link earns commission, and that a ranking is affected by it if it ever is |
| **An affiliate link** | The same | The same | The same | The same, plus the programme's terms. **From 6 April 2027 see section 5: how the hand-off is done starts to matter** |
| **A premium plan or feature in the app** | ODYS, through Apple or Google | Apple or Google | Apple or Google, by their rules | Store billing is compulsory (section 3). Consumer cancellation rights; the new subscription rules when they start (expected spring 2027; date UNVERIFIED) |
| **A fee on one experience, the host paid directly** | The host sells the experience; ODYS sells its own service | The provider, then the host. ODYS only ever receives its fee | The host, for the experience; ODYS for its fee | Card payments through a provider; no package, because it is one service; clear terms on who is responsible for what |
| **ODYS sells one service itself** (buys in and resells) | ODYS | ODYS | ODYS | ODYS carries refunds, chargebacks and supplier failure. VAT under the Tour Operators' Margin Scheme may apply (UNVERIFIED: ask an accountant) |
| **ODYS sells a flight with anything, or two kinds of travel service together** | ODYS, as "organiser" | ODYS | ODYS, within 14 days in set cases (UNVERIFIED this session) | **A package.** Liability for the whole trip, insolvency protection, and an ATOL licence if there is a flight. Criminal offences with unlimited fines for getting it wrong (guidance, paras 72-73) |

**The row to stay out of is the last one**, and the law is moving so that it is easier to fall into by accident (section 5).

## 2. Payment links or a checkout made per order

| | A payment link | A checkout session the server makes for each order |
|---|---|---|
| What it is | One reusable page for one fixed product | A one-off page for one order, made by the Brain |
| Price | Fixed when the link is made | Set by the server for this order |
| Knows which order and which person it is for | No, unless added by hand | Yes |
| Stops two payments for one order | No | Yes: one session per order, and it expires (30 minutes to 24 hours on Stripe) |
| Several travellers, a changing price, another currency | A new link each time | Normal |
| Refund and booking status tied to the order | By hand | By the order's id |
| Good for | A pilot: "the Saturday walk, £20", ten people, checked by eye | Anything the app sells |

**Use a link only for a hand-run pilot** (it could be the whole of Test D, with no code at all). **Use a per-order checkout for everything in the app.** A generic link is wrong for travel inventory: the price, the availability and the traveller all vary per order.

## 3. Apple Pay is not In-App Purchase; Google Pay is not Play Billing

- **Apple Pay and Google Pay** are ways to pay by card. The card is charged through ODYS's own payment provider at the provider's fee. They are a button, not a billing system.
- **In-App Purchase and Google Play Billing** are the stores' own billing systems. The store is the till, and takes a commission (15% for a small developer).

Which one applies is not a choice. It follows from what is sold:

- Apple, guideline 3.1.1: "If you want to unlock features or functionality within your app, (by way of example: subscriptions … access to premium content, or unlocking a full version), you must use in-app purchase."
- Apple, guideline 3.1.3(e): "If your app enables people to purchase physical goods or services that will be consumed outside of the app, you must use purchase methods other than in-app purchase to collect those payments, such as Apple Pay or traditional credit card entry."
- Google Play, Payments policy: apps "requiring or accepting payment for access to in-app features or services … must use Google Play's billing system", and it must not be used "for the purchase of physical services (such as transportation services, cleaning services, airfare, gym memberships, food delivery, tickets for live events)".

| What is paid for | iPhone app (UK) | Android app (Google Play, UK) | Website |
|---|---|---|---|
| A hotel room | Not In-App Purchase. Card or Apple Pay through a provider, or a link out (3.1.3(e)) | Not Play Billing. Card or Google Pay through a provider, or a link out | Card through a provider |
| A flight | The same | The same ("airfare" is named) | The same |
| A ticket for an experience or event | The same | The same ("tickets for live events" is named) | The same |
| A one-to-one service with a person (a private guide) | Other methods are allowed (3.1.3(d)); "one-to-few and one-to-many real-time services must use in-app purchase" where they are delivered in the app | Physical service: not Play Billing | Card |
| A premium subscription to the planning | **In-App Purchase** (3.1.1). 15% in the Small Business Program (under US$1m a year) | **Play Billing.** In the UK since 30 June 2026: 10% plus a 5% billing fee for subscriptions | Card through a provider. May be used in the app only if also offered there as an in-app purchase (3.1.3(b)) |
| A one-off premium feature | **In-App Purchase** | **Play Billing** (15% to 25% plus the 5% billing fee, by programme and install date) | As above |

**Sending people from the app to the website to buy a digital subscription** is where the rules differ by country and are changing:
- **iPhone, UK:** the CMA said on 30 June 2026 that steering "is currently banned by Apple and restricted by Google in the UK", and consulted on requirements to lift that. Whether those requirements are now final was **not confirmed in this session (UNVERIFIED)**. In the United States no entitlement is needed for such links (3.1.1(a)); the UK is not the United States.
- **Android, UK:** Google's "billing choice program" (UK from 30 June 2026) lets a developer use its own billing or link to its website, at a fee ("20% for external web links" as standard, 15% under two programmes).
- **So:** assume store billing for digital sales inside both apps, and re-read both pages in the week this is built.

**Other things a paid feature brings:** account deletion inside the app once accounts exist (Apple 5.1.1(v); Google has the same rule), and updated privacy answers on both stores.

## 4. The design

The pieces, and where each is in the prototype (`prototype/payments/orders.py`):

| Piece | What it does | Rule it keeps | In the prototype |
|---|---|---|---|
| **Catalogue** | What can be bought and its price, on the server | The server sets the price; nothing from the phone is a price | `Item`, `Orders.create` |
| **Order service** | Makes one order per request key | Asking twice is asking once | `Orders.create` |
| **Checkout** | Asks the provider for a hosted page for this order | One open page per order, never a second charge | `Orders.open_checkout` |
| **Provider adapter** | The only code that knows the provider | Swapping or adding a provider touches one module | `MockProvider` |
| **Payment states** | created, pending, requires action, processing, succeeded, failed, cancelled, partially refunded, refunded, disputed | A state only moves along allowed lines | `Pay`, `MOVES` |
| **Booking states** | none, requested, confirmed, failed, cancelled | **Paid is not booked** | `Booking`, `supplier_says`, `owed_back` |
| **Notification handler** | Takes the provider's signed messages | Signed, recent, new, and matching the order, or nothing changes | `Orders.notify` |
| **Refunds** | Asks the provider; final when the provider says so | Never more than was paid | `ask_refund` |
| **Trail** | Every step, in order, each line hashed with the last | A changed or missing line shows | `Trail` |
| **Reconciliation** (not in the prototype) | A daily job that asks the provider for every payment and compares | Catches any message that never arrived | To build: ~3 h |

**How one sale goes** (an experience with a host):

1. The app asks the Brain for an order: an item id, a quantity and a fresh request key. Nothing else it sends is used.
2. The Brain prices it from the catalogue, stores the order as *created*, and asks the provider for a hosted page, charged directly to the host's account with ODYS's fee attached.
3. The app opens that page in the phone's own browser sheet (never a web view inside the app). The person pays there, with a card, Apple Pay or Google Pay; the bank's extra check, if any, happens there.
4. The provider sends the Brain a signed message. Only that message moves the order to *succeeded*. The page the person lands back on is not proof of anything.
5. The booking becomes *requested*, and the host is asked. The host's yes makes it *confirmed*. A no makes it *failed*, and the order appears in "owed back" until it is refunded.
6. The app shows "paid, waiting for the host" and "confirmed" as two different things.

**What ODYS never does:** see or store a card number; hold the price of the experience in its own account; decide a payment succeeded from anything the phone says; mark a booking confirmed because money moved.

## 5. Why ODYS should not become the seller of travel

The Package Travel and Linked Travel Arrangements Regulations 2018 make whoever sells two different kinds of travel service for one trip (transport, somewhere to stay, car hire, or another tourist service that is a large part of the trip) an "organiser", liable for the whole trip, with insolvency protection, and an ATOL licence if a flight is included.

**The law changes on 6 April 2027** (SI 2026/455, made 22 April 2026; the GOV.UK guidance was updated on 28 October 2026 to reflect it, as Abram had been told). Two changes matter to ODYS:

- **"Linked travel arrangements" are abolished.** Today, helping someone book a second service within 24 hours of the first creates a lighter set of duties. From April that middle category goes.
- **A new kind of package is added.** Services "provided under separate contracts with individual service providers" are a package "if a single trader has facilitated, on the occasion of a single visit to, or contact with, the trader's point of sale, the separate selection of and separate payment for each of the travel services by the traveller."

Read that against ODYS's own direction ("Trips are the main product": a flight, a stay and days planned in one place). **Separate suppliers, separate contracts and separate payments do not keep it out of a package** if ODYS's own screen is where each is selected and paid for in one visit. The guidance's own tests:

- Sending someone on to "a second site or tab, clearly operated by a separate entity" to book the next thing "is unlikely to be considered the same point of sale".
- A gap of "several hours (for example 4 hours)" is likely a clear break in a "single visit".
- A "generic banner advert … clearly not personalised" is unlikely to be facilitating; being "immediately presented with a personalised offer" is likely to be.

ODYS's whole idea is the personalised offer. So the line it must hold is the first one: **each booking is selected and paid for on the supplier's own site, clearly theirs**, as it is today (D120). The moment a flight and a hotel can both be chosen and paid for inside ODYS in one sitting, ODYS is likely an organiser, whatever the contracts say.

**So, for trips:** stay the planner and the referrer. If a provider's terms push towards booking inside the app (the open LiteAPI question, `liteapi-clarification.md`), that is this decision in disguise, and the answer for now is no. A single experience with no flight and no stay is one service and isn't a package; that is why step 2 is safe and step 4 isn't.

## 6. Independent hosts (a marketplace), later

- **Use Stripe Connect with direct charges**, as D39 already says. The host is the seller; the payment lands on the host's balance; "refunds and chargebacks reduce the connected account's balance"; ODYS takes an application fee. Stripe checks the host's identity.
- **Why a regulated provider and not ODYS's own account:** collecting money for others is a payment service. The FCA's "commercial agent" exclusion needs the agent to act for the payer or the payee, "but not both parties", and a marketplace acts for both (FCA guidance; the newest version seen was dated May 2024).
- **Still ODYS's job:** who may host, what happens when a host doesn't turn up, a refund policy people can read, complaints, and its Online Safety Act duties once hosts and guests can message each other.
- **A direct charge can still end up at ODYS's door** if a host's balance goes negative and can't be recovered. Ask Stripe how that works for each account type before launch.
- Don't build it until one host and ten paying guests exist by hand.

## 7. More than one provider, later

Don't build a second provider until the first has taken real money for a quarter. What makes a later switch cheap, and costs nothing now:

- one adapter module, and no provider names anywhere else;
- amounts as whole numbers of pence with a currency code, never floats;
- ODYS's own order ids as the reference, with the provider's ids stored beside them as opaque text;
- ODYS's own state names (section 4), translated from each provider's events in the adapter;
- no card details saved with a provider in a form that can't be moved (ask about export before saving any).

## 8. What opening the business account needs

| Step | Cost or need | Source |
|---|---|---|
| Incorporate a limited company | £100 online; £156 the same day | Companies House fees, updated 25 Sep 2026 |
| A business bank account | The company's number, directors' identity and address, what the business does | Typical; varies by bank (secondary) |
| The ICO data protection fee | Before the first paid client (already a gate, D108). Amount by size: UNVERIFIED this session | — |
| VAT | Compulsory above £90,000 of taxable turnover a year (secondary sources; unchanged from April 2024). Selling abroad or reselling travel changes the picture: ask an accountant | — |
| A Stripe account, live | Business and owner details, a website that says what is sold and how refunds work, a bank account, a name for card statements | docs.stripe.com/get-started/account/activate |
| Apple and Google paid apps agreements | A company account on Apple (with a D-U-N-S number, D61), bank and tax forms on both | Already on the project's list |
| Insurance | Public liability and professional indemnity before the first paid client (already a gate) | CLAUDE.md |

## 9. Questions for a solicitor (specific, answerable)

1. With flights, stays and days planned in one trip in the app, and each booked on the supplier's own site: are we outside "package" today and after 6 April 2027? What exactly must the hand-off screen say and do to stay outside limb (c)?
2. If an affiliate programme pays us for a booking, does anything change in question 1?
3. If we charge a fee for one hosted experience by direct charge to the host: are we an agent for the host, for the guest, or neither? What must our terms say so that the host, not ODYS, is liable for the experience?
4. Does showing a provider's live prices and then sending people elsewhere to book breach Duffel's or LiteAPI's terms as signed?
5. A subscription sold in the apps: which cancellation and renewal-reminder rules apply now, and what changes when the Digital Markets, Competition and Consumers Act's subscription rules start?
6. When a ranking is affected by commission, or a place is sponsored, what wording and placement satisfy the CMA and the ASA?
7. Is the name ODYS clear as a UK trade mark in classes 9, 39 and 42? (Unchecked: CLAUDE.md.)
8. Do host and guest messaging, or reviews, bring Online Safety Act duties we don't have today, and which?

## 10. Hours, if and when

| Piece | Hours (estimate) |
|---|---|
| Test D by hand with one payment link | 2 |
| Affiliate links with disclosure, both apps | 8 |
| Step 2 in the Brain: tables, the Stripe adapter, the notification route, reconciliation, tests | 20 |
| Step 2 in both apps: the order, the browser sheet, "paid" and "confirmed" as two states | 12 |
| Step 3: store billing in both apps and receipt checks in the Brain | 25 to 30 |
| Connect onboarding for hosts | 15 |

## Sources (read 11 Nov 2026)

- SI 2026/455, the Package Travel and Linked Travel Arrangements (Amendment) Regulations 2026 (made 22 April 2026, in force 6 April 2027; limb (c) quoted from it): https://www.legislation.gov.uk/uksi/2026/455/made . Re-read directly by the reviewer.
- GOV.UK guidance, "Package holidays: complying with regulations", last updated 28 October 2026: https://www.gov.uk/government/publications/the-package-travel-regulations-question-and-answer-guidance-for-organisers-and-retailers (the date re-read directly; the quoted tests are from its October 2026 PDF as read by a research assistant in this session).
- The 2018 Regulations: https://www.legislation.gov.uk/uksi/2018/634/regulation/2 .
- Apple's App Review Guidelines (3.1.1, 3.1.1(a), 3.1.3(b), (d), (e), 5.1.1(v), quoted from the page): https://developer.apple.com/app-store/review/guidelines/ . Small Business Program: https://developer.apple.com/app-store/small-business-program/ .
- Google Play: Payments policy https://support.google.com/googleplay/android-developer/answer/9858738 ; "Understanding Google Play's Payments policy" …/answer/10281818 ; Service fees …/answer/112622 ; the billing choice programme (page read; its address was not recorded).
- CMA, 30 June 2026, "CMA consults on new requirements for Apple and Google's mobile platforms", and the mobile platforms page (strategic market status designated 22 October 2025): gov.uk (addresses not recorded; find by title).
- FCA, commercial agent exclusion: https://www.fca.org.uk/firms/commercial-agent-exclusion-cae and PERG 15.5 (via search summaries; the version seen was dated May 2024).
- Companies House fees: https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees .
- Stripe: as listed in `payment-provider-comparison.md`.
- Not confirmed from a primary page in this session, and marked UNVERIFIED above: the ICO fee amounts; the ATOL exemptions and small-business ATOL costs; the start date of the subscription rules (law firms give "spring 2027" and one "January 2027"); the 14-day refund rule; TOMS; the VAT threshold (secondary sources agree on £90,000).
