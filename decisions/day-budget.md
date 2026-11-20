# A day's money: lunch, fares and one total (7 Nov 2026; m217)

**Decision: built, on the branch.** A day with a budget now keeps lunch inside that budget by default. It never drops lunch silently. Tube and bus fares count towards the budget. The plan shows one total, line by line. When a day can't fit, it says why and what could change. The blind Test B pair is unchanged.

## What was wrong (Abram's finding, 7 Nov)

- **The planner left fares out.** It counted place prices and the lunch slot (£15, D102) against the budget, but no fares. So a "£12 day" could cost £18.
- **Lunch disappeared silently.** Under £15, lunch couldn't fit. The planner dropped it and the plan never said so.
- **A second bug, found while fixing the first.** From Greenwich, the first fix set the fares aside before planning again. That left less than lunch's cost, and the day without lunch won because it was cheaper. A regression test now covers it (`test_fares_never_squeeze_lunch_out_it_steps_down_instead`); it fails on that version for 3 of 4 budgets.

## How it works now (`brain/src/brain/daybudget.py`, `api.personal_day`)

1. **Lunch is chosen to fit.** There are three planning figures, always labelled as estimates. They never name a venue and are never shown as live prices:

   | Lunch | Figure | Source |
   |---|---|---|
   | At a café, pub or food stall | £15 | ODYS's planning estimate (a guess, D102) |
   | A supermarket, bakery or market stall | £6 | ODYS's planning estimate (a guess) |
   | Bring lunch, or buy it nearby | £0 | nothing set aside |

   The first lunch tried is the most comfortable one the budget can cover on its own: £15 at £15 or more, £6 from £6, otherwise bring lunch.
2. **Plan, then check the whole day.** If the finished day (places, fares and lunch) goes over, ODYS:
   - plans once more with the fares set aside, but only if that still leaves room for lunch;
   - if it's still over, steps lunch down a level and plans again.

   It keeps the best day it found. The order: a day that kept lunch beats one that lost it; then a day within budget beats one over it; then the cheaper day wins. Lunch is never removed to make a day fit.
3. **The person can leave food out** (`food_in_budget: false` on the plan request). Then the budget covers places and fares only. Lunch appears on its own line as "…: not in your budget", at its usual estimate.
4. **One total.** The block's total is computed from the same stops as the plan's `totals.cost_gbp`, and a test checks that the two agree at every budget.
5. **When it doesn't fit, it says so:**
   - the message, e.g. "This day comes to £14, £2 over your £12: most of it is lunch.";
   - the options, offered only when they apply: bring lunch or buy it from a supermarket or market; places closer together; swap a paid place for a free one; raise the budget; leave food out of the budget.
6. **When lunch was stepped down, it says that too:** "Your budget is tight, so we've planned a cheaper lunch and kept to places that cost little."

## What it looks like

The plan's response gains `budget` (null without a budget, and always null for the blind pair). It has three lines: Lunch, Getting around and Places. Each line has its figure, its kind (estimate, price or missing) and a note. Then come the total, what's left, a status (fits, tight or over), the message, the options and a note: "Lunch and fares are estimates; places are the prices on their cards."

- **Both apps** show it under the plan's chips as "Your budget £…" (iOS `BudgetBlock`, Android `BudgetBlock`).
- **Older app builds** ignore the new key, so TestFlight 91 and Android 21 are unaffected.
- **Screenshots:** demo screen `planbudget` (iOS CI) and `09g-planbudget` (Android).

## Checks

- `brain/tests/test_daybudget.py` (25 tests):
  - which lunch each budget starts with, and the step-down order;
  - the block's lines and wording;
  - no lunch is never silent;
  - food left out of the budget;
  - **every budget from £5 to £100** through the API: the lunch line is always present; the total equals the plan's total; the lunch is the first choice or a step down; a day over budget always explains itself;
  - the blind pair: no block, and the £15 lunch as before;
  - Greenwich, where the day needs fares, at £8, £12, £15 and £20: lunch kept and within budget.
### Results by budget

This is the test person from `test_api.install`, on a 10:00–18:00 day with every ready card and the app's 1-second limit. The script is in the session scratchpad (it isn't committed); the same checks are in the tests above.

| From | Budget | Lunch | Fares | Places | Total | Left | Status |
|---|---|---|---|---|---|---|---|
| Charing Cross | £5 | bring £0 | £0 | £0 | £0 | £5 | tight |
| Charing Cross | £8 | cheaper £6 | £0 | £0 | £6 | £2 | tight |
| Charing Cross | £10 | cheaper £6 | £0 | £0 | £6 | £4 | tight |
| Charing Cross | £12 | cheaper £6 | £0 | £0 | £6 | £6 | tight |
| Charing Cross | £15 | café £15 | £0 | £0 | £15 | £0 | tight |
| Charing Cross | £20 | café £15 | £0 | £0 | £15 | £5 | fits |
| Charing Cross | £30 | café £15 | £0 | £0 | £15 | £15 | fits |
| Charing Cross | £50 | café £15 | £0 | £0 | £15 | £35 | fits |
| Charing Cross | £100 | café £15 | £0 | £0 | £15 | £85 | fits |
| Greenwich | £5 | bring £0 | £6 | £0 | £6 | −£1 | over |
| Greenwich | £8 | bring £0 | £6 | £0 | £6 | £2 | tight |
| Greenwich | £10 | bring £0 | £6 | £0 | £6 | £4 | tight |
| Greenwich | £12 | cheaper £6 | £6 | £0 | £12 | £0 | tight |
| Greenwich | £15 | cheaper £6 | £6 | £0 | £12 | £3 | tight |
| Greenwich | £20 | cheaper £6 | £6 | £0 | £12 | £8 | tight |
| Greenwich | £30 | café £15 | £6 | £0 | £21 | £9 | fits |
| Greenwich | £50 | café £15 | £6 | £0 | £21 | £29 | fits |
| Greenwich | £100 | café £15 | £6 | £0 | £21 | £79 | fits |

What the table shows:

- Lunch is there at every budget, and the total always equals the plan's own total.
- **£5 from Greenwich is honestly over.** The day needs £6 of fares, because too few ready cards are within walking distance of Greenwich. The plan says: "This day comes to £6, £1 over your £5: most of it is getting around." It then offers places closer together, raising the budget, or leaving food out.
- **This test person's picks are free places at every budget** (London has many free ready cards), so the table only exercises lunch and fares. Paid places are covered by the unit tests of the block.

## What this does not do

- **No real cheap restaurants.** "A cheaper lunch" is a kind of place with a guessed figure, not a venue. Real food venues wait for the food work (m215 decision 4: research and design only).
- **Fares are the planner's estimates** (`dayplan.transport_gbp`: per journey, at most the daily cap), not a TfL fare quote.
- **Trip days** pick the lunch that fits the trip's day budget. They don't run the step-down loop; that is the next step if trip days show the same problem.
- **No change** to Test B, the frozen `main` build, or the questions people answer.

**Hours:** Claude ~4 h. Abram: none. Optional: a glance at the two screenshots.
