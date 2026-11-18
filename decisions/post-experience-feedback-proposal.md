# One tap on what let a stop down: the five ideas compared, and a small proposal (16 Nov 2026)

Abram's review of the audit, part 9 (12 Nov): "do not implement all five… evaluate which one has the highest expected user value with the lowest development cost. My initial preference is the one-tap post-experience feedback."

**This is a proposal only: nothing is built.** It would go into the first build after the friends' round, never into the frozen one (build 91).

## The five ideas, compared

Value and hours are from `odys-new-opportunities.md`, re-read against what exists today.

| Idea | What it adds for the person | What it adds to ODYS | Hours | Needs | Verdict |
|---|---|---|---|---|---|
| 1. A plan for about three hours from where I am | A new reason to open the app with no planning | Reach, not learning | ~10 | location on the phone (D123 allows it, opt-in) | strong, but it's a feature, and it puts more plans on a model that can't yet tell good from bad |
| **2. One tap on what let a stop down** | Feeling heard after a bad stop; the next plan avoids the cause | **Every low rating teaches the model the cause, not just the score**, with no new question | ~6.5 | nothing | **chosen** |
| 3. "Was anything different from what we said?" | Trust that stale facts get fixed | Keeps Layer 2 checked (`map-tiles-and-place-data.md`) | ~6 | nothing | **folded into 2** as one of its taps; the full version (asked after good stops too) is m267's "Was it what you expected?", kept for later |
| 4. Any stay judged against my days | A better stay choice | Uses the trip's own days | ~12 | the phone's address lookup | worthwhile, but the biggest build; after the first trips are planned for real |
| 5. Thursday's look at Saturday | A nudge to plan the weekend | Return visits, not learning | ~8 | notifications | an experiment once there's something to come back to |

**Why 2:** it is the only one of the five that makes the model better from data people already give. A low rating today says *that* a stop was poor; the model then spreads the blame across every feature the stop has. One optional tap says *why*.
- **It is also the cheapest:** one optional row, on the rating sheet that already exists, with no new screen and no new personal data.
- **It answers Abram's two concerns in part 3:**
  - it learns more with fewer questions;
  - it keeps "the facts were wrong" out of the person's tastes.

## The proposal

**Where and when:**
- On the stop's rating sheet, **only after a 1 or 2**, as one row under the stars.
- It is never its own screen, never a reminder, and never asked again for that stop.
- Skipping is the default; the sheet closes as it does now.

**Words** (both apps, the same):
> Sorry it wasn't great. What let it down? (optional)

| Tap | Stored as | What the model does with it |
|---|---|---|
| Too crowded | `crowds` | Adds one stated observation that crowds made this stop worse, on the stop's own crowd level. **Half the weight of a this-or-that choice** (like the feelings, `reasons.FEELING_SCALE`; a GUESS until tested) |
| Too far to get there | `travel` | The same, on the stop's own leg (`transfer_15_30` or `transfer_30_plus`, from the rating's `travel_min`). Under 15 minutes, nothing is learnt from it |
| Too expensive | `cost` | The same, on the cost weight (`cost_per_10gbp`, log scale: it can only make the person more cost-sensitive, D88) |
| The weather | `weather` | The same, on the weather term that applied (rain, cold or heat outdoors, from the rating's conditions). With no outdoor exposure, nothing |
| Not my kind of place | `taste` | **Nothing extra.** The rating already counts against the stop's tastes; the tap confirms it was taste, not the day |
| Not as described (hours, price, closed, different) | `not_as_described` | **The rating is left out of the person's tastes** (the place, not the person, was wrong), and the card goes into a re-check queue. Its facts are marked "being checked" for the next plans (quality's trust perspective) |

**The model** (`scoring.py`):
- **The new observation:** one new function, `letdown_observation(pop, moment, reason, conditions, travel_min)`. It builds the same kind of `Observation` that `feeling_observation` does today: one feature, y = 0, half scale.
- **What it doesn't change:**
  - the hierarchical structure;
  - the population weights;
  - the planner.
- **"Not as described":** its rating is the one change to an existing input. The person's own rating stays stored and in the export: it is excluded only from `observations()`.
- **Before it is trusted** (Claude, ~1 h, synthetic, **for the design only, never as evidence**):
  - In `learning_curve.py`, make simulated low ratings have a known cause.
  - Check that the tap's half weight improves the fit, and that **a wrong tap doesn't do more harm than no tap**. People will sometimes tap the nearest reason.
  - If it does more harm, the weight is lowered.

**Privacy:**
- One more optional field on the existing rating (`ratings.letdown`, one of six fixed values or empty).
- It is deleted with the rating and included in the export.
- **No free text.** A text box after a bad experience invites personal detail.
- **No reason that touches health:**
  - there is no "too tiring" or "too much walking" tap, which could hint at a condition;
  - walking effort is learnt from ratings and choices as now.
- **The privacy notice:** it already covers ratings and the conditions they were given in. Abram confirms whether one line is added ("and, if you choose, what let it down").
- No new consent: it's a rating detail, not a new purpose.

**What it is read against after the next round:**
- **How often each tap is used:**
  - if fewer than 1 in 5 low ratings carry a tap, the row isn't worth its space;
  - if most say "not as described", the catalogue is the problem, not the model.
- **"Not as described"** against the stop's facts' trust levels (checked against estimated or unknown: m268's split). This is the real-user test of the uncertainty-aware ranking's premise.
- **Learning by milestone** (`learning_milestones.py`), with and without the taps. **Real ratings only.**

## Hours (after the friends' round)

| Item | Hours |
|---|---|
| Brain: the column, the observation, the "not as described" exclusion, the re-check queue in the admin export, tests | 2 |
| The synthetic check of the weighting (design only) | 1 |
| iPhone and Android: the row on the rating sheet, both apps together (CLAUDE.md) | 3 |
| Screen renders and the real-device step (`mobile-validation-plan.md` R7 covers the rating sheet) | 0.5 |
| **Total** | **6.5** |

**After-9-Nov rule:** it helps the next validation round, not Test B, so it waits for the round's end. m267's "Was it what you expected?" stays designed and unbuilt. Abram decides after this one's first read-out whether it is still needed.
