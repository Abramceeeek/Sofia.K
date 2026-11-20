# Test D and Test E, prepared without taking money (16 Nov 2026)

Abram's review of the audit, part 6 (12 Nov). This document covers interviews, a non-binding purchase-intent test and five conversations with hospitality businesses.

**What is not approved (unchanged):**
- live payments or real charges;
- card storage, payouts or settlement;
- live subscriptions;
- collecting a whole trip's money.

**The commercial principle stands:** ODYS is a discovery and planning platform, and the supplier runs the checkout for any booking. No permanent decision is made that ODYS can never become a marketplace.

## Recommendation

1. **Test D in two steps.**
   - **D1:** six to eight interviews about the last day out or trip people paid for.
   - **D2:** a non-binding offer inside the conversation, shown after they have used their plan: "Would you pay £X for a plan like this for your next trip?", then a concrete next step they can take or refuse.
   - The landing-page waitlist from D1 and D2 of September (`test-plan.md`) stays as a later option for traffic. It isn't needed to answer the first question.
2. **Test E** as set up (`validation/test-e-kit.md`, D57), but with **five accommodation managers**, a working demo, and a stricter read-out: **evidence of payment, not praise** (below).
3. **Both start after the friends' round**, with the working app, once Abram's company exists.
   - Interviews need no company. A price quoted to a business is clearer from one.
   - **Nothing in either test takes, asks for or stores a payment detail.**

## Test D: will people pay for a personalised day or trip?

**What is being offered, stated before any price is shown:** the six questions Abram listed. These are the working answers for an interview, not legal positions.

| Question | Working answer for the test | Settled by |
|---|---|---|
| Exactly what ODYS sells | A **personal plan**: a day or a trip planned around the person, with reasons, timings, prices and the way in. Digital, used in the app. **Not** the boat, the ticket, the room or the flight | Abram |
| Who the seller is | ODYS (the company, once incorporated) sells the plan only | Abram, at incorporation |
| Who provides the experience | Each venue, operator, airline or hotel, booked on its own site (D120) | as today |
| Who is responsible for refunds | For the plan: ODYS, under the Consumer Rights Act's digital content rules (UNVERIFIED this session; for the solicitor). For each booking: its supplier | a solicitor |
| Whether it creates travel-sector obligations | **Selling only a plan is not selling a travel service.** Selling a flight with a stay, or two kinds of travel service for one trip, would make ODYS an "organiser" under the Package Travel and Linked Travel Arrangements Regulations 2018 (`payment-architecture.md`, sources there). The SI 2026/455 amendments are in force from 6 April 2027. The line between "a plan" and "facilitating" a linked arrangement is **for the solicitor** | a solicitor, before any charge |
| Whether app-store rules affect it | **Yes.** A plan unlocked in the app is digital content: In-App Purchase on iPhone (guideline 3.1.1) and Play Billing on Android. Real-world services used outside the app may use other payment methods (3.1.3(e)). Steering to a website for a digital sale is restricted in the UK (the CMA, 30 June 2026; `payment-architecture.md`). Re-read both stores' rules in the week anything is built | Apple's and Google's pages, re-read then |

**D1: interviews** (6 to 8 people, 30 minutes each, by call or in person):
- **Who:** people who planned a day out or a trip in the last three months. Some from the friends' round, and some who never used ODYS, so the answers aren't all from people already friendly to it.
- **Questions (past behaviour only, no pitching until the close):**
  1. "Tell me about the last day out or trip you planned. How long did planning take, and what did you use?"
  2. "Did you pay for anything to plan it: a guide, a tour, an app, a travel agent? What and how much?"
  3. "What went wrong or felt wasted?"
  4. "When did you last pay someone to save you planning time?"
- **Notes:** kept without names in `validation/raw/` (git-ignored), with no quotes attributed. A voice note is transcribed, then deleted (CLAUDE.md).

**D2: the non-binding offer**, at the close, only for those who have used an ODYS plan:
- **The price:** one price, chosen at random between £4.99 and £9.99 for a day plan, or £14.99 and £24.99 for a trip plan. Then: "Would you pay that for your next one?"
  - These prices come from D1 and D2's arms and the per-trip idea in `test-plan.md`. They are GUESSES, and the random pair is the experiment.
- **Then a next step that costs them something small and real, or that they decline:**
  - "Can I put you on the list to be asked first, with this price, when it exists?" (they give a contact, by choice);
  - or "Would you tell me the date of your next trip so I can send you the plan the week before?"
- **Measures:**
  - stated yes, maybe or no at the price;
  - **the share who take the next step** (the honest signal);
  - their own words for what it's worth.
- **Never:**
  - a payment page;
  - a card form;
  - an implied commitment.
  - The script says plainly that nothing is being sold today.

**Read-out (decided now):**
- **Keep-going signal:** at least 3 of 8 take the next step at the price they were shown.
- **Not:** a stated yes alone, which overstates willingness to pay.
- The prices from people who said no are kept, to set the next round's prices.

## Test E: business customers (5 accommodation managers)

**Kit:** `validation/test-e-kit.md`, with the call guide, the message version and the intro line. Postponed until v0 exists (D86); v0 now exists, so this is its next run.

**Changes for this run:**
- **Who:** five people who decide for an accommodation business in London, such as a hotel general manager, a guest-experience lead or a serviced-apartment operator. This narrows D49's mix: the Uzbek agencies come in a later run.
- **A demo at the close** (10 minutes):
  - Their area, one day plan for "a guest here for two days", and "best for your days" for a stay.
  - Sample data is labelled as such, as in the apps.
- **Payment evidence, not praise.** The call ends with a ladder, and each step taken is recorded:
  1. they name what they spend now on helping guests find things to do (staff time, a concierge service, printed guides, a tours partner), with an amount if they will give one;
  2. they name who holds that budget;
  3. they accept a **non-binding** quote, for example "£X a month for plans for your guests". £350 a month is the project's GUESS (D40), shown as one figure to react to;
  4. they agree to an **unpaid pilot with a written date** to decide on payment;
  5. they put a price and a start date in writing (an email is enough).
- **Never at this stage:**
  - a contract;
  - an invoice;
  - taking guest data.
  - **A pilot that would hold any guest's personal data waits** for a data-processing agreement and the ICO check (CLAUDE.md legal gates).

**Read-out:** D57 holds (at least 2 of 5 already spend money or staff time on this, **and** at least 2 of 5 introduce someone or agree to an unpaid pilot), with one addition. **"Businesses will pay" stays an untested assumption** (CLAUDE.md) until at least one reaches step 5. Steps 1 to 4 are interest; step 5 is evidence.

## What runs where

| | Needs a company | Needs the app | Collects | Hours (Abram) | Hours (Claude) |
|---|---|---|---|---|---|
| D1 interviews | no | no | notes without names | 4 (8 × 30 min) | 1 (script, notes template) |
| D2 offer | no (it's non-binding), yes before any real price | yes | the answer; a contact only if offered | in D1 | 0.5 |
| Test E | better with one, for the quote | yes | notes; no guest data | 5 (5 × 45 min plus preparation) | 1.5 (the demo section, the ladder sheet) |

## Before any money is ever taken (unchanged gates, CLAUDE.md)

1. Apple's outside-activities policy checked and disclosed if required (Abram, in progress).
2. Incorporation, the ICO fee, and public liability and professional indemnity insurance.
3. A solicitor's answer on the package-travel line and the refund duties above.
4. The store billing rules re-read for whatever is sold in the apps.
5. The provider decision (`payment-provider-comparison.md`), after the business bank account exists.
