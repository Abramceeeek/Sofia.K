# Checkpoint 2 — Phase 2 unit economics summary

*2026-09-26. Model: `economics/unit-economics.xlsx` (697 formulas, 0 errors; 86 inputs, of which 29 fetched, 4 search and 44 GUESS). Assumptions and sources: `economics/assumptions.md`. All figures are for the Default stack unless stated.*

## Answer

**Running costs are negligible; acquisition is the business.** Cash cost is £0.14 per paying user per month, and onboarding costs £0.32. At benchmark conversion and a £4.99/£29.99 price sold in Telegram Stars:

- A payer's lifetime value (LTV) is **£24**.
- Paid social costs **£375 per payer**, giving an LTV:CAC of **0.06** against a target of 3.
- Organic community posts cost almost no cash but **~5 founder hours per payer**. At 7.5 h a week, that yields about 3 payers a month.

## Revenue models

| Model | Verdict | Why (model output) |
|---|---|---|
| **Subscription** (freemium: onboarding + 1 free plan) | **Viable only if reworked** | Needs a hard paywall, ~£9.99/£59.99 and a web checkout. Together these reach LTV:CAC ≈1.1 on Meta and cut sign-ups for £50k from 91k to 5.7k a year |
| **Group-trip commission** (10%) | **Second line, after the legal gates** | ~£15 contribution per trip (7.5% take after card fees). Best value per sign-up of the five, but £50k needs ~2,600 trips and ~1,300 moderation hours a year |
| Pay per plan (£2.99) | Ruled out | The Stars cut and the 20p Stripe fee eat it. It needs 135k sign-ups a year for £50k, so subscription beats it |
| Affiliate (8%) | Ruled out | £0.08 revenue per plan against £0.09 cost on the Default stack. It also pulls the planner toward paid stops |
| Promoted experiences (£5 CPM) | Ruled out for now | £50k needs 42k MAU (the brief's check: £100k ≈ 83k MAU). A paid slot also conflicts with the predicted-feeling ranking |
| Premium stack (live avatar) | Ruled out for v0 | £4.46 per sign-up. Organic CAC rises to £217 |

## Users needed per year (net receipts, base inputs)

| Target | Subscription sign-ups | Group trips | Promoted MAU |
|---|---|---|---|
| £10k | 18,197 | 526 | 8,333 |
| £50k | 90,987 | 2,632 | 41,667 |
| £100k (VAT registration) | 181,974 | 5,263 | 83,333 |

## What Phase 3 must measure

1. **Sign-ups per community post and minutes per post** (recruitment, D21). This is the biggest driver of founder hours.
2. **Priced-option share at two price points**, including monthly vs annual (Test D). Conversion itself can't be measured until money can be taken.
3. **Minutes spoken, session length and voice share** (Test A), which set onboarding cost.
4. **Plans per user and support minutes** (Test C).
5. **Group size, spend per person and moderation minutes** (weekend test).

## Hours

Phase 2 founder time is estimated at **5 h**, on budget. Areas 13–17 add 2.5 h of review.

## Open questions

1. Payment: web checkout (keeps ~94%) or Telegram Stars (~62%)? Telegram's rule for linking out is UNVERIFIED.
2. Change the Test D prices to £4.99 vs £9.99 a month, with a hard paywall after the first free plan?
3. Spend ~£50–100 on a Meta test to measure cost per click and visit-to-sign-up for real?
