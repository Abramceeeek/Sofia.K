# Does Stage 1 of the trip cost layer fit v0? (D87)

*Short note, 2026-09-27. **The value display is decided (D88)**: "worth about £V to you", ranked by V − price, with the cost weight kept negative (built in the Brain, 27 Sep). **The day total is still decided at Checkpoint 3**, where v0's scope is decided. The rest of the trip cost layer is on `decisions/after-9-nov.md` (#14). Anything marked **(my judgement)** is opinion. The facts are in `research/sources.csv` (area `cost`).*

## Answer

**Yes, a thin Stage 1 fits v0, for about 1.5 h of your time (GUESS). Decide it at Checkpoint 3.** (my judgement)
- **It adds one line to the day plan:** "About £X for the day". X is the card prices, plus TfL fares capped at the daily cap, plus a food estimate.
- **Each moment gets a "worth about £V to you" figure**, in place of a raw feeling-per-pound ratio (see below).
- **Fuel is left out,** because v0 plans walking and public transport only (`brain/src/brain/travel.py`).

**Why it's worth it:** the second outcome the app tries to raise is "the spend felt fully worth it". v0 already uses cost in three places:
- **a price on every card** (`cost_gbp`);
- **a personal cost weight** (`cost_per_10gbp`, prior −0.25 per £10);
- **a daily budget limit in the planner.**

Stage 1 mostly shows what the model already uses.

## What exists and what's missing

| Part | Now | For v0 |
|---|---|---|
| Entry and activity prices | On every card | Nothing new. Prices need rechecking: the Uber Boat fares change after 31 Oct |
| TfL fares between stops | Not built; transit legs are a rough time estimate | **A small zone fare table, with the day's total capped.** The Zones 1–2 daily cap is £8.90, and caps are frozen until March 2027 (TfL, read 27 Sep). TfL's fare finder API is an option, but search results describe it as Tube only |
| Food | Not built | One per-meal figure from the person's own budget answer, labelled as an estimate. No price data needed |
| Fuel | No driving in v0 | Left out |
| "Worth it" ranking | The planner already maximises value net of cost | Show it in pounds (below) |

## Why not a raw feeling-per-pound ratio

In a choice model, utility is identified only up to location and scale. Add a constant to every S and the choices don't change, but the S ÷ cost ranking does. Free moments also divide by zero.

**Suggested instead (my judgement):**
- Show the **money-metric value**: V = the non-cost part of S ÷ the person's cost weight, in £, next to the price.
- Ranking by V − price is the same as ranking by S, so the planner doesn't change. Only the display is new.
- **One requirement:** the person's cost weight must stay negative. With a prior sd of 0.5 around −0.25, some people's weight could cross zero, and V would explode. The fix is to fit the cost weight on a log scale, or to estimate in willingness-to-pay space.

**A trade-off to test in Phase 5:** a visible day total makes the cost more salient. Prelec & Loewenstein (CLAUDE.md) suggest that makes paying hurt more.

## Hours (GUESS; Claude writes the code)

| Piece | Your hours |
|---|---|
| Choose the food rule and check the wording | 0.25 |
| Review the fare table, the cap and the cost-weight change (with the Brain review; the cost-weight change is built, D88) | 0.5 |
| Design: the total on the day plan screen and V on the moment card (on top of D81's 7 h) | 0.5 |
| Check the station zone Claude adds to each card, during card reviews | 0.25 |
| **Total** | **≈ 1.5** (Phase 4 would go from ≈ 57 to ≈ 58.5 h) |

**No booking is involved,** so Stage 1 raises no package-travel question. Stage 2 does (`decisions/after-9-nov.md` #14).
