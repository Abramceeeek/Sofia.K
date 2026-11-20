# Planner optimisation: two-stage planning, measured (7 Nov 2026; m216)

**Decision: built, benchmarked, and left off.** Two-stage planning is implemented:
- **stage 1:** a valid day built one stop at a time, keeping every rule and never making the person's own time unreachable;
- **stage 2:** the solver improves that day within the time limit.

It runs beside the usual search, and the better plan by the solver's own cost wins.

At the app's 1-second limit with all 49 cards it makes no clear difference (better on 2 days, worse on 3, mean +0.003). The bar was Abram's: "a faster planner must not simply produce a worse itinerary more quickly". So it stays **off** (`dayplan.SEEDED_WITH_BLOCKS = False`). The code, its tests and the comparison script stay, so it can be switched on if a better seed, a faster server or a larger catalogue changes the numbers.

## What was compared (`brain/scripts/benchmark_seeding.py`, synthetic travellers only)

- **Days:** every one of the benchmark's 11 travellers, on each day with the person's own time: plans near the places at 14:00; plans somewhere not decided over lunch; free time in the afternoon; and a new day with two blocks.
- **Catalogue sizes:** 15, 30 and all 49 ready cards (the smaller ones a fixed random subset).
- **Time limits:** 0.2 s (like a busy server) and the app's 1 s.
- **Planners:** the current planner, and the two-stage one, where the usual search gets 80% of the limit, the seeded one 20%, and the better wins.
- **Checks:** every plan checked from outside the solver (the benchmark's own rules) and timed. Four plans solved at once, as in the main benchmark.

| Cards | Limit | Better | Same | Worse | Mean gain | Worst | Rule breaks (current/new) | Places short (current/new) | Time p90 (current/new) |
|---|---|---|---|---|---|---|---|---|---|
| 15 | 0.2 s | 3 | 41 | 0 | +0.139 | 0.00 | 0/0 | 6/6 | 0.72/0.75 s |
| 15 | 1 s | 5 | 36 | 3 | −0.017 | −5.32 | 0/0 | 6/6 | 2.02/2.05 s |
| 30 | 0.2 s | 3 | 36 | 5 | +0.001 | −0.66 | 0/0 | 0/0 | 0.56/0.62 s |
| 30 | 1 s | 4 | 35 | 5 | −0.004 | −0.57 | 0/0 | 0/0 | 1.56/1.62 s |
| 49 | 0.2 s | 4 | 35 | 5 | +0.043 | −0.45 | 0/0 | 0/0 | 0.62/0.75 s |
| 49 | 1 s | 2 | 39 | 3 | +0.003 | −0.21 | 0/0 | 0/0 | 1.61/1.71 s |

**The noise floor.** The current planner run twice against itself (`--noise`) differs on 5 of 264 days (2 worse, 3 better), with 0 rule breaks either way. So the 21 worse and 21 better days above are real differences, not chance.

**Constraints:** 0 rule breaks in 1,056 plans. Every block of personal time was kept in every plan, both ways (528 of 528 in each run).

## What the numbers say

1. **Seeding alone (the seeded search with all the time) was worse.** The first version gave the whole limit to the seeded search. With 49 cards it lost on 9–11 of 44 days, by up to 2.2: starting from the step-by-step day can lead the solver into a worse corner. So the two searches now run side by side and the better one wins.
2. **Side by side, the 1-second results are a wash.** The losses come from giving the usual search less time, which the seed doesn't make up. The worst day (−5.32: "likes everything", plans at 14:00, 15 cards) is one where the strict first search (all four stops required) fails and the retry finds the good plan only with the full second.
3. **Under time pressure it helps on average.** At 0.2 s the mean gain is +0.04 to +0.14, and on 15 cards it's never worse. That matters because the original problem (the m206 finding) appeared when four plans were solved at once. The same day planned alone now gets the good plan at 1 s.
4. **What actually moves quality is time.** On a quiet machine the current planner does well; under load it can stop at a poor plan. The live Brain is on Render's free tier, and the paid server is in the roadmap. A busier server (more people planning at once) is when this gets re-measured.

## Found along the way

- **The strict first search can use the whole second and fail.** With a small catalogue the "exactly this many stops" search may find nothing. The planner then retries, and the plan takes about 2 s (p90 2.02 s with 15 cards, against 1.6 s with 49). A shorter limit for that first attempt (or detecting it can't succeed) would halve the wait. ~1 h with the benchmark; proposed for the next planner pass.
- **Starting strategies:** the solver's other built-in starting strategies were tried on the worst days. None wins every day (one even lost a day the current one gets right), so the current one stays.

## In the code

- `planner._greedy_route` (stage 1) and the seeded `_solve(seeded=True)` (stage 2); `planner._solve_best` runs both and keeps the lower solver cost; `DayPlan.objective` carries that cost.
- `dayplan.SEEDED_WITH_BLOCKS` switches it on, for days with personal time only. **Ordinary days and Test B can never use it:** tested by making the seed raise and planning an ordinary day with the switch on.
- Tests (`test_planner.py`): a seeded day keeps every rule and holds the block at its own times; a day without personal time never touches the seed.
- Results: `brain/benchmarks/synthetic/seeding.txt`.

**Hours:** Claude ~3 h. Abram: none; switching it on later is a one-line change, after a fresh benchmark.
