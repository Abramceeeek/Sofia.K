# Recommendation engine evaluation: the planner on synthetic travellers (WS7, 7 Nov 2026; m206)

**Decision.** The day planner now has a fixed-seed benchmark (`brain/scripts/benchmark_planner.py`). It plans 11 kinds of made-up traveller on 12 kinds of day, four ways each, and checks every plan from outside the solver. **No plan broke a hard rule.** It found **two planner bugs, now fixed and tested**, and it raised two questions for Abram:
- the short onboarding learns very little about most kinds of traveller;
- on days with personal time, the 1-second search sometimes stops at a poor plan.

This is the first of the three checks (product-direction.md, m199): *is it logically reasonable?* It says nothing about whether people prefer the plans (Test B) or enjoy the day (ratings). **Synthetic travellers only**: no real answers, ratings or plans are read, and nothing is tuned to these numbers. The 75% "strong match" line is unchanged.

## What was run

| | |
|---|---|
| **Travellers** (fixed tastes, δ on the model's own features) | museums and architecture; nature; food; family; relaxed (also asks for "a relaxed day"); active; budget (cost weighs 3.3× the average, £10 a day); strict dietary (halal); accessibility (step-free); likes everything; likes nothing. **Several cities: not run**, since the planner plans one day in one city (WS3). |
| **Days** (from Charing Cross unless said) | full Saturday 10–18; Test B's Saturday 12–17 (£40); Monday 10–17; Sunday morning 9–13; Friday evening 17–22; rain 11–17; plans near the places 14:00–15:30; plans somewhere not decided over lunch 12:30–14:00; free time 15:00–17:00; a trip's first day after a train (St Pancras, 15:00–19:30, no lunch); a trip's last morning 9–12:30, no lunch; a long day 9–21 with 6 stops |
| **Plans per traveller and day** | *personal, known tastes* (the planner told the tastes exactly); *personal, after onboarding* (the real 6 places and 5 this-or-that tasks, answered by the traveller with model noise, 6 answer seeds); *no answers* (Test B's generic comparison); *greedy* (a simple baseline with no solver: the best next place that fits, lunch when it's time, the same hard rules) |
| **Scored on** | The traveller's own tastes: the sum of stop utilities (a food card as lunch counts; a "lunch near X" slot is 0) less the leg penalties |
| **Checked from outside the solver** | Inside the day; no overlaps (travel included); each stop inside its hours; open that weekday; no dry-weather card in rain; no card twice or two variants of one; one area at most; at most two history-and-culture stops and never two in a row (lunch or the person's own time between them breaks the run, as in the planner); within budget (lunch included); each block kept at its times, with nothing inside it |
| **Measured** | Places kept vs asked; lunch; travel, longest leg, legs over 30 min; extra travel vs the shortest order of the same places; slack; free time kept; strong and good matches available vs planned; stops whose step-free access, food suitability or family suitability is unknown; how often each card is used; whether a re-run changes the plan |
| **Settings** | Seed 20261107; the app's 1-second time limit; the popularity nudge on, as in the app; the straight-line London travel estimate (GUESS), not TfL |

The benchmark's own checks have tests (`brain/tests/test_benchmark_planner.py`: a clean plan passes; overlaps, closed days, hours, budget, history in a row and a broken block are caught). A clean report therefore means the plans are clean, not that the checks are blind.

## Results (1-second limit, 132 traveller-days, 1,188 plans)

| | Personal, known tastes | Personal, after onboarding | No answers | Greedy |
|---|---|---|---|---|
| Plans breaking a hard rule | 0 of 132 | 0 of 792 | 0 of 132 | 0 of 132 |
| Value, mean (median) | 4.27 (2.06) | 2.04 (0.54) | 0.63 (0.40) | 3.29 (1.81) |
| Places per day (lunch apart) | 2.80 | 2.77 | 2.80 | 2.73 |
| Travel a day, mean | 64 min | 44 min | 26 min | 64 min |
| Legs over 30 min, across all plans | 60 (132 plans) | 97 (792 plans) | 0 | 99 |
| Extra travel vs the shortest order of the same places | median 0, p90 20 min | median 0, p90 8 | 0, 0 | median 0, p90 22 |

- **Known tastes vs no answers:** better on 121 days, the same on 10, worse on 1. The one worse day is a 0.05 loss: the variety nudge, which accepts up to 0.1 by design (D113).
- **Known tastes vs greedy:** better on 96, the same on 13, worse on 23. Of those 23, **8 lose by more than 0.1**, 5 of them days with personal time (finding 3).
- **Every scenario got its places**, 0 days short. Lunch was planned on every day that spans it, except the budget traveller (finding 4) and plans over lunchtime (by design, m202: the day says so). Every block was kept, at its own times.
- **After onboarding vs no answers:** better on 78 days, the same on 1, worse on 53 (finding 5).
- **Stability:** re-planning 120 of the plans (a separate run with `--repeat 24`) changed 2. The search stops at its time limit, so it isn't bit-for-bit repeatable; the fixed seed fixes the travellers and their answers.

## Findings

**1. Fixed: a lowered floor could leave a day short of places.** When fewer cards clear the "at least Good" floor than the day needs, the planner lowers the floor (m187). It let in exactly as many cards as the day needed. If those couldn't fit together, the day came up short. Example: the "likes nothing" traveller on a Friday evening. Their three best cards all close at 18:00, so the 17:00–22:00 evening got **one place instead of three**. Now three more of the person's best cards come in as spares (`FLOOR_SPARES`, a GUESS), and the evening has three places. Test: `test_a_lowered_floor_lets_in_spares_when_the_best_cards_cannot_fit_together`, which fails on the old code.

**2. Fixed: a dislike of packed days made the choice of places depend on distance alone.** The planner adds the person's packed-day weight to each place's prize, then clamps the prize at zero. For someone who dislikes packed days, several places' prizes hit zero. The solver couldn't tell them apart and took the nearest. Example: the relaxed traveller's Sunday morning was planned at the Embankment gardens (−0.4) rather than the Royal Festival Hall foyers (0.0) or the Garden at 120. The day's number of stops is fixed, so the pace term is the same for every candidate plan. It now stays out of the prizes (it's still in the reported value), and that morning goes to the Royal Festival Hall. Test: `test_a_dislike_of_packed_days_never_makes_the_choice_of_places_by_distance_alone`, which fails on the old code. Both fixes are on the branch only: the friends' round runs the frozen `80a0da3`.

**3. Open: on days with personal time, the 1-second search sometimes stops at a poor plan.** A block adds a slot beside each of the 12 best places (m200), about 13 more nodes. On 5 of 33 such days the planner lost more than 0.1 to the greedy baseline. The worst was the relaxed traveller with plans at 14:00, at −0.40 against 0.53. With 3 seconds the planner finds 0.63, better than greedy. So the search is the cause, not the model. Options for Abram (minor, D69, unless the response time matters to him):
- (a) start the solver from the greedy plan, or keep the better of the two (~2 h, with tests);
- (b) a longer limit on days with blocks (~0.25 h, but each plan takes about 2 s longer);
- (c) fewer host slots (cheaper, but blocks have fewer places to sit beside).

Recommended: (a).

**4. Open (product): a budget below lunch's cost removes lunch without saying so.** Lunch counts £15 against the day's budget (D102). With £10, lunch can't fit, and on a day with no personal time the empty slot becomes a fourth place. The budget traveller got **no lunch on 8 of 8 days that span it**, and nothing on the day says why. On days with personal time, an extra place can't happen (m202), but the silence is the same. Decision for Abram:
- (a) lunch outside the places budget ("£10 for places; lunch is extra");
- (b) keep it inside and say "Lunch doesn't fit a £10 day: bring something, or raise the budget".

Either is about 1 h in the Brain and both apps.

**5. The short onboarding learns little about most travellers (step 1 only, and in the model's own world).** The table below is the gain over the no-answers plan after onboarding, as a share of the gain if the tastes were known exactly (6 answer seeds per traveller, 72 onboarded plans each):

| Traveller | Gain if the tastes were known | Gain after onboarding | Share | Onboarded plans better than no answers |
|---|---|---|---|---|
| Nature | +4.29 | +2.95 | 69% | 63 of 72 |
| Museums and architecture | +3.82 | +0.92 | 24% | 50 of 72 |
| Food | +5.09 | +0.57 | 11% | 47 of 72 |
| Active | +3.20 | +0.41 | 13% | 51 of 72 |
| Family | +1.43 | +0.00 | 0% | 29 of 72 |
| Strict dietary | +0.96 | −0.21 | worse than none | 17 of 72 |
| Budget | +0.42 | −0.36 | worse than none | 18 of 72 |
| Accessibility | +0.58 | −0.19 | worse than none | 18 of 72 |
| Relaxed | +0.75 | −0.46 | worse than none | 16 of 72 |
| Likes everything | +13.95 | +6.55 | 47% | 66 of 72 |
| Likes nothing | +5.53 | +5.34 | 97% | 66 of 72 |

The six upfront places are the British Museum, Hyde Park, the view from Greenwich Park, South Kensington to the Natural History Museum, Primrose Hill at sunset, and Brick Lane for food. Four of six are green spaces or views, two are museums, one is about food. That fits the pattern: nature is learned, food and pace barely. This agrees with the algorithm review's check 3 (`scripts/algorithm_checks.py`). The places are locked for Test B (D107, D111), so nothing changes now. **After the round:** choose upfront places and tasks that separate these kinds of traveller. Measure the result with this benchmark, then confirm it with real ratings, never with the simulation alone.

**6. Personal plans travel more.** 64 min a day against 26 for the no-answers plan; 60 of 132 personal plans have a leg over 30 minutes. The order is close to the shortest (median 0 extra minutes, p90 20). The distance comes from which places the person would enjoy: the model judges them worth the trip. Whether people agree is Test B's "easier to actually do" question. These are straight-line estimates. TfL times on the live Brain will differ.

**7. What the planner can't know: no step-free data, food suitability or family data in most places.** The step-free way in is unknown for **304 of 369 planned places (82%)**; none is known not to be step-free. The accessibility traveller had 28 of 33 places with access unknown. No card says whether food is halal, vegetarian, vegan or kosher, so all 14 of the dietary traveller's food stops are unknown. Nothing knows children's ages, child prices or buggy access. The planner treats these needs as preferences (less walking), never as constraints. That is honest only if the app says so. WS1 (structured place attributes) and WS2 (food data) are the way forward. Until then, neither need is claimed as served.

**8. A few cards carry the personal plans.** The Garden at 120 is in 52 of 132 personal plans (39%), St Dunstan in the East and the Royal Festival Hall foyers in 36 each, and 38 of 49 cards are used at least once. The travellers are deliberately extreme, so read this loosely. It's a reason to add cards, not to retune the nudge.

**9. With strong tastes, most cards are "strong matches".** The museums traveller has 33 cards past the 75% line on a typical day; the food traveller 30; "likes everything" 41. The relaxed traveller has 2, accessibility 0, "likes nothing" 0. So the label separates little for people with strong tastes, and the plans for relaxed or accessibility travellers are mostly "good" matches. The 75% line isn't changed here (the sprint's rule). Its validation is steps 2 and 3, against real ratings.

## What this doesn't say

- **Whether the plans are good.** Every number is computed on tastes we wrote. Real people's tastes, the rating model's fit, the feature tags and the travel estimate all add error this can't see.
- **Whether onboarding is good enough.** Finding 5 assumes the model's own likelihood for how people answer. Real answers may carry more signal or less.
- **Anything about other cities.** Only the 49 London cards exist.

## Running it

```
cd brain && .venv/bin/python scripts/benchmark_planner.py --seeds 6 --repeat 24
```

It takes about 8 minutes on 4 cores at the app's 1-second limit with 6 answer seeds (about 5 with the default 2). It writes `brain/benchmarks/synthetic/planner.txt`, the summary, which is committed. It also writes `planner.json`, the per-plan rows, which is git-ignored and re-made by the script. Run it after any change to the planner, the cards or the priors, and compare the summary. It is a guard against breakage, not a score to raise.

**Hours.** Claude ~4 h (the benchmark, its tests, the two fixes). Abram: findings 3 and 4 (~0.25 h).
