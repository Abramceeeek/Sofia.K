# Batch 6, before and after (25 Nov 2026)

**One product commit for everything:** `05ea04c`.
- It is `336d58a` plus one Android test line (the "DAY 1" label). The Brain is identical in both.
- The handover commits after it change only documents.

| What | At `05ea04c` |
|---|---|
| Brain tests | **641 passed** (locally, Python 3.12); Brain CI green |
| Generated examples | `examples.md`, from `05ea04c`: each party's costs, and a shared trip three of the travellers planned from their own accounts |
| London gate | `gate.md`, 3 runs of `05ea04c` |
| Android | run 60: built, all 129 screen tests passed (run 59 at `336d58a` failed one: the new shared-trip test looked for "Day 1", drawn as "DAY 1") |
| iPhone | run 120 (manual simulator run, upload off; see the PR for its result) |
| Three independent reviews | of those examples and that gate (below) |

**Synthetic travellers and AI reviews are not customer evidence.**

## The gate: `d6c6ab6` against `05ea04c`, the same script, 3 runs each

| Check | `d6c6ab6` | `05ea04c` |
|---|---|---|
| G1, G2a, G2c, G3, G3b, G4–G10, G12, G14 | 0 | 0 |
| G2b day feel | 6 | 6 |
| G11 travel within 20 min of the pace's budget | 5 | 5 |
| **G13 false or contradictory reasons** | **5** | **0** |
| Unused time (run 1) | 1,936 min | 1,881 min |
| Minutes over the travel budget (run 1) | 236 | 228 |
| Different places | 82 | 82 |

- The five G13 failures at `d6c6ab6` were the batch 5 reviews' false statements:
  - "open until 17:00" for Liberty, which closes at 20:00;
  - Poppie's said to fit the £70 budget, which it didn't, twice;
  - a meal offered as the rain option for a view, twice.
- At `d6c6ab6` the gate can't split walking from Tube time (that came in batch 6), so its G11 lines read "0 min by Tube or bus".
- At `05ea04c` run 2 differed slightly from runs 1 and 3 (unused time 1,936 vs 1,881 min) because the solver stops at a time limit. The check counts were the same in all three runs.

**London does not pass.**
- G2b fails 6 times: Full and Balanced days ending early, and one Relaxed day without a break.
- G11 fails 5 times: gentle days over their travel budget, mostly Tube or bus for the family and mostly walking for Jonas.

## What changed for travellers (m355–m359)
- **No false budget or opening claims** (m355): a rain option's budget line counts the fares, a meal is never a rain option, and "open until" is the place's own time.
- **Journeys measured apart** (m355): walking minutes and km, Tube or bus minutes and legs, waits, and the whole journey. G11 still judges the whole journey.
- **Party costs** (m356): each traveller's cost, the party's total, children's own prices where the card's source gives one, and what's verified against what's estimated.
- **Trips planned with friends** (m358), from separate accounts and with consent. Each member's own "Didn't enjoy it" places are left out, and their first loved place goes in. Nobody is named without agreeing. Both apps.
- **Group variety and nearness** (m358), over 40 test groups (80 days):

  | Measure | Before | After |
  |---|---|---|
  | Days with more than two history stops | 25 | 0 |
  | Days spread over 3 km | 62 | 22 |
  | Members left without a favourite | 3 | 3 |
  | Least-served member's mean chance of "Good" | 0.631 | 0.610 |

- **Age rules from the trip's own children** (m359): the 14+ bike loop is never planned with an 8-year-old.

## Three fresh independent reviews (of the `05ea04c` examples)

| Traveller | London local | Families and gentle pace | Sceptical product reviewer |
|---|---|---|---|
| Sam | 6/10 | 7/10 | with small fixes |
| Priya and Dan | 7/10 | 7/10 | with small fixes |
| Family | 4/10 | 5/10 | no |
| Jonas | 5/10 | 5/10 | with small fixes |
| Four friends | 6/10 | 7/10 | no |
| Margaret and Alan | 7/10 | 7/10 | with small fixes |
| **Shared trip** (new) | 3/10 | 5/10 | no |
| **Verdict** | nearly | nearly | **5/10 against a well-informed friend; nearly** |

At batch 5 the reviewers said "not yet", "nearly" and "not yet". Now all three say "nearly".

## What the reviews found (Claude's check of each is in batch 7)

**Privacy (found by two reviewers):** with Members A and B named, "because one of you asked for a gentle pace" can only mean the third member. "Counted, not named" fails by elimination in a small group.

**The shared trip:**
- a list of places, with no times, routes, meals or costs;
- the first day is three quiet indoor stops;
- "a favourite for Member A" (the food lover) on the Hunterian and the Wellcome: favourites come from the fitted weights alone, not the member's interests;
- Member B gets 1 of the 6 stops;
- the second day crosses London.

**The way back (all three reviewers):** no day times or costs the journey home, so "£40.00" on a £40 budget is really about £43.

**Reasons still stretched or contradictory:**
- "something absorbing to do" for a quiet terrace;
- "good food too" on a stop where dinner is cut;
- "one of your interests" that names none;
- "among people heading to work" at 18:12;
- "Walk five minutes up Exhibition Road" beside "no travel".

**Routes:**
- the friends' Embankment Gardens → Hyde Park → Villiers Street;
- Sam's Covent Garden → Fleet Street → back;
- a Greenwich day out by DLR and back by boat;
- the family's 42-minute Tube ride mid-day.

**Meals:**
- Sam's two lunches 141 min apart, then his dinner cut;
- lunch at 11:30 on two days;
- generic café lunches for a couple happy to spend.

**Children:**
- Burlington Arcade and Liberty at the end of the family's Day 2;
- "Each person pays for their own" said of an 8-year-old;
- children's fares at the adult fare;
- the budget doesn't say whether it is per person or for the party.

**Facts to check (the reviewers' memory, UNVERIFIED):**
- Flat Iron's opening time;
- the boat's £22.90 (a River Roamer?);
- under-11s free on the Tube with an adult;
- bus fares below £3.00;
- Wahaca Southbank still open.
