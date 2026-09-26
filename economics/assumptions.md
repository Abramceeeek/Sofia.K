# Unit economics — assumptions

*2026-09-26. The model is `unit-economics.xlsx`. Every number in it is on the `Inputs` or `PriceTables` tab with its unit, status, source URL and access date. This note explains the structure and flags what is weakest. Sources are also in `research/sources.csv` (area `econ`).*

## Decision first

**Costs are not the problem; conversion, price, payment channel and founder hours are.** An active paying user costs £0.03–0.31 a month in cash across the three stacks. But at benchmark conversion (2.1%) and a £4.99/£29.99 price sold in Telegram Stars, a payer is worth ~£24 over their lifetime (the lifetime value, LTV), while paid social costs ~£375 per payer (the customer acquisition cost, CAC). Organic posting costs almost no cash but about 5 founder hours per payer. Phase 3 has to measure the inputs that move this: conversion, price, posts-to-sign-ups, and hours.

## How the model works

- **Costs** (`Costs`): three stacks, each a column. Choices at the top (model, transcription, host format, channel, payment channel) look up unit prices. Costs are split into onboarding per sign-up, per plan, per active paying user per month, and fixed per month.
- **Revenue** has one tab per model: `Subscription`, `PerTrip`, `GroupTrip`, `Affiliate` and `Promoted`. Each gives contribution per user and per plan ("trip") for all three stacks.
- **LTV** (`Subscription`, `LTV`): constant monthly churn implied by year-one retention, so expected lifetime = 1 ÷ (1 − monthly survival). This is a geometric lifetime with no cap. Blended by the annual/monthly mix.
- **CAC** (`CAC`) = (channel cost per sign-up + onboarding and free-plan cost per sign-up) ÷ sign-up-to-paying conversion. Every sign-up costs money whether or not they pay.
- **Revenue targets** (`BreakEven`): steady state, so revenue per year = new payers per year × lifetime revenue per payer. Targets are **net receipts** (after the app store, Telegram, Stripe and VAT).
- **Sensitivity**: each row changes one input and restates the formulas. A two-way grid shows price × conversion.
- **Virality** (D23): with S0 seed sign-ups a year from posting and viral coefficient K, steady-state sign-ups are S0 ÷ (1 − K), so the K needed is 1 − S0 ÷ S. The tab then checks founder hours at that volume.
  - At 7.5 h a week, half of the spare hours spent posting, and 5 sign-ups per post, you get ~1,750 seed sign-ups a year.
  - £50k needs **K ≈ 0.98** (base) or **K ≈ 0.69** (upside: paywall, £9.99/£59.99, web checkout).
  - Even the upside needs onboarding and support time to fall to **~19%** of the current guesses. Automation is not optional.
- **PaymentChannels** (D24): net per sale at the Test D prices for Stars, Stripe, Apple and Google.

## The three stacks

| | Cheapest | Default | Premium |
|---|---|---|---|
| Channel | Telegram | Telegram | Web live avatar; WhatsApp during the trip |
| Host | Text or pre-recorded clips | Synthetic voice (Deepgram Aura-2) | Tavus live avatar |
| LLM | Claude Haiku 4.5 ($1/$5 per MTok) | Claude Opus 5 ($5/$25) | Claude Opus 5 |
| Transcription | gpt-4o-mini-transcribe ($0.003/min) | gpt-transcribe ($0.0045/min) | gpt-4o-transcribe ($0.006/min) |
| Onboarding cost per sign-up | £0.06 | £0.32 | £4.46 (avatar £4.19) |
| Cost per plan | £0.018 | £0.086 | £0.146 |
| Fixed cost per month | £15 | £25 | £83 |

Opus 5.5 ($4/$20) is cheaper than Opus 5 and can be picked from the dropdown. Prompt caching is not modelled, so LLM costs are an upper bound.

## Findings from re-verifying prices (all 2026-09-26)

- **Telegram Stars.** Digital goods and services sold *inside* Telegram must be paid in Stars ([Telegram](https://core.telegram.org/bots/payments-stars), fetched). Developers receive $0.013 per Star ([Developer Terms s.6.2.4](https://telegram.org/tos/bot-developers), fetched). Users pay about $1.99 per 100 Stars through the app stores ([third-party estimate](https://dev.to/starsearn/telegram-stars-economics-for-bot-developers-what-your-stars-are-actually-worth-in-2026-2742), fetched). After a ~5% withdrawal fee (search), **we keep ~62% of the price**, against ~94% through Stripe (1.5% + 20p, [Stripe](https://stripe.com/gb/pricing), fetched). A web checkout raises lifetime value from £24 to £39. Physical services, such as group-trip costs, may use normal payment providers.
- **WhatsApp**: messages inside the 24-hour customer service window are free ([Meta](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing), fetched). The UK template rates are third-party figures (search).
- **Weather**: the Met Office free plan gives 360 calls/day, then £9/month for 900/day ([Met Office](https://datahub.metoffice.gov.uk/pricing/site-specific), fetched). The Open-Meteo free API excludes apps with subscriptions or ads ([terms](https://open-meteo.com/en/terms), fetched), so it can't be used once we charge.
- **Live avatar**: Tavus Starter costs $59/month for 100 minutes, then $0.37/min ([Tavus](https://www.tavus.io/pricing), fetched). A 15-minute onboarding costs ~£4.19, which is 13× the whole Default onboarding.
- **Subscription benchmarks** ([RevenueCat 2026](https://www.revenuecat.com/state-of-subscription-apps/), fetched):
  - Travel apps have the lowest prices ($20/year median) and the best yearly retention (39%).
  - Freemium converts 2.1% of downloads to paying; a hard paywall converts 10.7%, with near-identical year-one retention.
  - The median travel app makes ~$35/month one year after launch.
- **Fixed obligations**: ICO data protection fee £52/year (search). Once turnover passes £90,000, VAT registration applies at 20% ([GOV.UK](https://www.gov.uk/vat-registration/when-to-register), fetched). The £100k target crosses it.

## Weakest assumptions (44 of 86 inputs are GUESS)

| Input | Value | Why it matters | Measured by |
|---|---|---|---|
| Sign-ups per community post | 5 | Sets founder hours per payer (≈5 h) | Recruitment posts (D21) |
| Sign-up → paying | 2.1% (benchmark) | CAC scales with its inverse | Test D proxy only: no money taken (D1) |
| Price | £4.99 / £29.99 | LTV scales with it | Test D, two price points |
| Minutes spoken, session length, voice share | 8, 15, 50% | Onboarding cost; avatar cost | Test A (D4) |
| Plans per payer per month | 1.5 | Per-plan cost; value | Test C |
| Group size, spend per person, moderation minutes | 5, £40, 30 min | Group-trip model | Weekend test |
| Support minutes per user | 3/month, 5 per sign-up | Founder capacity | Tests A and C (log time) |

## Payment channels (D24, checked 2026-09-26; decision deferred)

- **Telegram: a bot must not link out to a web checkout for digital goods.** The Bot Platform Developer Terms (s.6.2, [fetched](https://telegram.org/tos/bot-developers)) say:
  - all digital goods and services must be sold "exclusively through the exchange of Telegram Stars";
  - Telegram follows Apple's and Google's definitions of digital goods;
  - a bot "found to be using alternative payment systems for digital goods and services" gets a notice, then can be made "inaccessible from store versions of Telegram" or terminated.
  - Physical goods and services, such as a group trip's real-world costs, may use any payment provider.
  - → A web subscription is only safe if it is sold on the web with **no link or prompt from the bot**. That caps its reach, so treat Stars as the price of being in Telegram.
- **Future native app** (fetched):
  - **Apple:** subscriptions pay 70% in year one and 85% after a year of paid service, or 85% throughout under the Small Business Program (up to $1M proceeds). In the UK, apps may not link to other payment methods; the US storefront may.
  - **Google Play** (UK, EEA and US, from 30 June 2026): auto-renewing subscriptions pay a 10% service fee plus a 5% billing fee.
  - **UK:** the CMA consulted (30 June 2026, fetched) on requiring Apple and Google to allow steering to external payment, with lower fees. The decision is due later in 2026 (search).
- The `PaymentChannels` tab compares what each channel keeps at the Test D prices.

## Unverified or open

- The Stars user price is a third-party estimate. The VAT treatment of Stars income is **UNVERIFIED** (the model deducts no VAT from Stars sales). App-store proceeds are modelled net of VAT ("minus applicable taxes", Apple).
- Taking money for group trips needs the legal gates cleared and a licensed marketplace payment provider. The Package Travel Regulations would need checking if accommodation is ever bundled (**UNVERIFIED**).
- The LTV:CAC target of 3 is a rule of thumb (**UNVERIFIED**).
- Not readable here: the Booking.com affiliate terms (25–40% of its own commission, search), the GetYourGuide rate (8%, search), and the Open-Meteo paid price.
