# Decision note — B2B-first vs consumer-first (D40)

*Status: **template, to fill after Test E** (5 interviews, weeks of 5–12 Oct). Model numbers below are pre-filled from `economics/unit-economics.xlsx` → `Path50k` and rest on GUESS inputs. Founder time to finish and decide: ≈ 1 h.*

## Decision

*To fill:* B2B-first / consumer-first / both, with a date to revisit.

## What the model says before Test E

Four £50k paths, steady state. Stranger K = 0.3, community posting 1.5 h a week, no paid group trips, venues a user benefit only (D37). B2B at £350 per client per month.

| Path | Consumer revenue | B2B clients | Hours needed / year | Helper hours / week needed (D41) |
|---|---|---|---|---|
| Base pricing, manual | ~£0.6k | 12 | ~1,030 | ~13.8 |
| Upside pricing, manual | ~£15k | 9 | ~910 | ~11.5 |
| Base pricing, automated (D44) | ~£0.6k | 12 | ~530 | ~4.2 |
| Upside pricing, automated | ~£15k | 9 | ~450 | ~2.6 |

**Hours per £1,000 of revenue:**

| Line | Manual | Automated |
|---|---|---|
| B2B | 14.9 h | 6.6 h |
| Consumer, base pricing | 313 h | 181 h |
| Consumer, upside pricing | 17.6 h | 7.4 h |

- **Only the upside consumer line competes with B2B per hour.** It needs strangers to choose a priced option (Test D) and a hard paywall that converts.
- **Consumer-first alone** needs ~3,700 sign-ups a year and K ≈ 0.53 even at upside pricing (`Virality`).
- **B2B's big remaining cost is account management** (1.5 h per client per month, a GUESS). Test E should tell us whether that is realistic.

## Evidence from Test E (fill in from `validation/raw/results.xlsx` → `Discovery`)

| # | Type | Current spend (£/month) | Staff time (h/week) | Budget owner named? | Commitment | Strongest quote |
|---|---|---|---|---|---|---|
| E1 | London hotel | | | | | |
| E2 | London serviced apartments | | | | | |
| E3 | London tourism body | | | | | |
| E4 | Uzbek agency sending clients to London | | | | | |
| E5 | Second Uzbek outbound agency (D49) | | | | | |

**Read-out vs the proposed bar:** ≥ 2 of 5 already spend money or staff time; ≥ 2 of 5 give an introduction or agree to an unpaid pilot.

- Spend: __ of 5.
- Commitment: __ of 5.
- Median current spend: £__ a month.

**Re-run the model with what we learned:** plans per client, sales hours per client and the price anchor on the `B2B` tab. Updated clients needed: __. Updated hours per £1k: __.

## Which way the evidence points

- **B2B-first if** the bar is met, a price anchor of ≥ £200 a month appears, and account time looks nearer 1 h than 3 h per client per month. The consumer app is then the product engine and a free acquisition channel.
- **Consumer-first if** Test E shows no current spend and no commitment, and the plan is to lean on Tests A–D (onboarding desirability, plan preference, use, and the priced-option share).
- **Uzbek interviews (D49):**
  - Both are outbound agencies at London prices. One or two agencies wanting to pay strengthens B2B-first.
  - **Payment is not a blocker.** Agencies can pay a GBP invoice by international card (≈ £337 net of £350) or by SWIFT (≈ £348), with no Stripe presence in Uzbekistan (Area 20).
  - Before the first invoice, get an HMRC certificate of residence. Without it, 20% is withheld.
  - Record how each agency last paid a foreign supplier.

## Hours

- This decision: ≈ 1 h.
- **B2B-first changes Phase 3:** Tests A–D still run, because the consumer app is the engine. The Test D priced-option threshold becomes descriptive.
- **B2B-first also changes Phase 4:** add a client-facing guest flow, about 4–6 h, UNVERIFIED estimate.

## Risks

- Five interviews give a direction, not proof.
- B2B sales take founder hours in blocks, which clash with a steady 7.5 h week.
- Taking money needs the money gates plus incorporation, the ICO fee and insurance first (CLAUDE.md, D38).
