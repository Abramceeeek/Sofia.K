# The London gate (m326)

Run on 25 Nov 2026, from Brain commit 8f21fde.

**NOT PASSED.** Six synthetic travellers, and two more Day Feel combinations, through the real planner (`scripts/london_gate.py`). London passes only when every check passes in every run.

G1 gap ≤ 20 min · **G2a** the places asked for (meals apart), no more than the day feel adds · **G2b** the day matches Relaxed, Balanced or Full · **G2c** time left at the end is said on the plan · G3 a loved place reflected · G4 no disliked kind · G5 age and booking rules · G6 every Why and best-time line true · G7 a gentle pace kept · G8 no journey longer than its visit · **G9** open for the whole visit that date · **G10** a sunset stop at sunset · **G11** travel within 20 min of the pace's budget

All of these block a release (m350). The measures further down are for a person to review.

**G2 (original)** (no day ending more than 45 min early) is reported for comparison with the earlier reports, as Abram asked, and no longer blocks (m346).

| Traveller | Day feel | G1 | G2a | G2b | G2c | G3 | G4 | G5 | G6 | G7 | G8 | G9 | G10 | G11 | G2 original |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sam | full | ✅ | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 2 |
| priya | balanced | ✅ | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 2 |
| family | balanced | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ 2 | 1 |
| jonas | relaxed | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ 1 | 1 |
| friends | full | ✅ | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ 1 | 1 |
| margaret | relaxed | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 3 |
| jonas+full | full | ✅ | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ 1 | 1 |
| friends+relaxed | relaxed | ✅ | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 1 |

Failures in total (run 1): G1 0, G2a 0, G2b 6, G2c 0, G3 0, G4 0, G5 0, G6 0, G7 0, G8 0, G9 0, G10 0, G11 5; G2 original 10 for the six travellers (12 with the two combinations)

## Repeatability

3 runs of the same commit and settings (solver limit 1.0 s a search, 4 CPUs). The solver stops at a time limit, so a run can differ slightly from the next; the tables below are run 1, and this table is every run.

| Run | G1 | G2a | G2b | G2c | G3 | G4 | G5 | G6 | G7 | G8 | G9 | G10 | G11 | G2 original (six; all eight) | Unused time | Waits mid-day | Days over the travel budget | Minutes over it | Different places |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 10; 12 | 1822 min | 1, 30 min | 12 of 16 | 227 min | 84 |
| 2 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 10; 12 | 1844 min | 1, 30 min | 11 of 16 | 223 min | 84 |
| 3 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 10; 12 | 1844 min | 1, 30 min | 11 of 16 | 223 min | 84 |

## Quality measures (reviewed, not pass or fail)

Free time is split by kind, as Abram asked: rest, meals and wandering are part of a good day; the waits are stated on the next stop, with what they wait for. Travel is compared with a day's budget for the person's pace (gentle 60 min, medium 90 min, full_on 120 min, unstated 90 min).

Unused time is the day's window with nothing planned: a later start, waits and an early end together (fewer is better; rest, meals and wandering are planned, so they don't count).

| Traveller | Unused per day | Rest | Meals | Wandering | Waits (count, total, longest) | Later starts | Travel per day | Meals named | Titles |
|---|---|---|---|---|---|---|---|---|---|
| sam | 118 min, 124 min | 95 min | 147 min | 149 min | 0, 0 min, 0 min | 41 min | 94 min ⚠, 94 min ⚠ | 2 of 2 | ok |
| priya | 134 min, 74 min, 134 min | 165 min | 135 min | 0 min | 0, 0 min, 0 min | 49 min, 34 min | 85 min, 96 min ⚠, 110 min ⚠ | 0 of 3 | ok |
| family | 85 min, 48 min | 129 min | 90 min | 0 min | 0, 0 min, 0 min | none | 98 min ⚠, 99 min ⚠ | 0 of 2 | 0 alike, 1 long ⚠ |
| jonas | 140 min | 132 min | 45 min | 0 min | 0, 0 min, 0 min | none | 83 min ⚠ | 0 of 1 | ok |
| friends | 64 min, 16 min | 124 min | 237 min | 78 min | 0, 0 min, 0 min | none | 150 min ⚠, 135 min ⚠ | 2 of 4 | ok |
| margaret | 185 min, 170 min, 197 min | 124 min | 135 min | 0 min | 0, 0 min, 0 min | none | 25 min, 64 min ⚠, 48 min | 0 of 3 | 1 alike, 0 long ⚠ |
| jonas+full | 89 min | 246 min | 45 min | 0 min | 0, 0 min, 0 min | none | 100 min ⚠ | 0 of 1 | ok |
| friends+relaxed | 184 min, 60 min | 93 min | 247 min | 83 min | 1, 30 min, 30 min | 41 min | 120 min, 124 min ⚠ | 2 of 4 | ok |

**Remaining time (G2c measures, m346):** each day's free time in periods over 20 min (a later start, waits and the end of the day), the longest, whether the plan says it, why it's there (chosen on a relaxed day; nothing strong enough to add; waiting for a place's time) and whether the plan offers something to do with it at the end of the day (staying on where they are):

| Traveller | Day feel | Each day: main places / asked · free time · longest · said · why · useful |
|---|---|---|
| sam | full | 4/3 · 105 min · 64 min · yes · nothing strong enough to add · yes; 4/3 · 115 min · 115 min · yes · nothing strong enough to add · yes |
| priya | balanced | 4/3 · 124 min · 75 min · yes · nothing strong enough to add · yes; 4/3 · 69 min · 35 min · yes · waits for a time · –; 5/3 · 117 min · 117 min · yes · nothing strong enough to add · yes |
| family | balanced | 4/3 · 75 min · 75 min · yes · nothing strong enough to add · no; 4/3 · 28 min · 28 min · yes · waits for a time · – |
| jonas | relaxed | 3/3 · 120 min · 120 min · yes · chosen (relaxed) · no |
| friends | full | 5/4 · 54 min · 54 min · yes · nothing strong enough to add · yes; 5/4 · 0 min · 0 min · yes · – · – |
| margaret | relaxed | 2/2 · 173 min · 173 min · yes · chosen (relaxed) · yes; 2/2 · 165 min · 165 min · yes · chosen (relaxed) · no; 2/2 · 182 min · 182 min · yes · chosen (relaxed) · yes |
| jonas+full | full | 4/3 · 79 min · 79 min · yes · nothing strong enough to add · yes |
| friends+relaxed | relaxed | 4/4 · 164 min · 93 min · yes · chosen (relaxed) · yes; 4/4 · 0 min · 0 min · yes · – · – |

**Costs (m350, measured):** each day's cost per person (entry, food and fares, from the plan's own summary) against the person's daily budget, and for the whole party. Children's prices aren't used yet, so a family's total is per person times four, an overestimate where a child pays less.

| Traveller | Party | Budget a day | Each day: per person · whole party |
|---|---|---|---|
| sam | 1 | £40.0 | £38.90 · £38.90; £27.50 · £27.50 |
| priya | 2 | £70.0 | £18.00 · £36.00; £23.90 · £47.80; £29.90 · £59.80 |
| family | 4 | £40.0 | £23.90 · £95.60; £34.90 · £139.60 |
| jonas | 1 | £20.0 | £18.00 · £18.00 |
| friends | 4 | £70.0 | £48.40 · £193.60; £52.30 · £209.20 |
| margaret | 2 | none | £15.00 · £30.00; £40.90 · £81.80; £30.00 · £60.00 |
| jonas+full | 1 | £20.0 | £14.90 · £14.90 |
| friends+relaxed | 4 | £70.0 | £48.40 · £193.60; £52.30 · £209.20 |

**Extra places** (Abram: "it must match the person's actual preferences"): 19 places beyond the number a day each person asked for. The rule: a day holds at most that number of places with under a 0.65 chance of Good (the planner's own estimate), so every place beyond it is a strong match. Days breaking it: 0. The weaker places, within each day's own number:

- sam 2026-12-04 (5 places, 3 asked): Down Villiers Street until the river (riverside) 0.51; Quiet treasures in the British Libra (gallery) 0.61
- sam 2026-12-05 (6 places, 3 asked): Burlington Arcade: a covered shoppin (arcade) 0.57; Centuries of British faces at the Na (gallery) 0.52
- priya 2026-12-06 (5 places, 3 asked): Aboard the Golden Hinde, Drake's gal (historic_site) 0.55; An unhurried hour in the Wellcome Co (museum) 0.63; Down Villiers Street until the river (riverside) 0.57
- jonas 2026-12-04 (3 places, 3 asked): The Hunterian: the art and science o (museum) 0.63
- friends 2026-12-04 (7 places, 4 asked): A rest in the Royal Festival Hall's  (arts_centre) 0.62
- friends 2026-12-05 (5 places, 4 asked): A park break: St James's Park and it (park) 0.62; Liberty's wooden galleries, built fr (department_store) 0.52
- margaret 2026-12-05 (2 places, 2 asked): The Uber Boat up the river from Gree (river_bus) 0.53
- jonas+full 2026-12-04 (4 places, 3 asked): A quiet hour among the Wallace Colle (museum) 0.57; Quiet treasures in the British Libra (gallery) 0.52
- friends+relaxed 2026-12-05 (4 places, 4 asked): A park break: St James's Park and it (park) 0.62

**How each day ends:** sam: Canal steps and Coal Drops Yard at Kin at 18:56, Beigel Bake: a salt beef bagel on Bric at 18:05; priya: A rest in the Royal Festival Hall's fr at 16:45, London from the Sky Garden, at the top at 17:25, Down Villiers Street until the river o at 16:03; family: A pirate-ship afternoon at the Diana M at 15:45, Through Somerset House to the river te at 16:32; jonas: A park break: the Serpentine in Hyde P at 16:00; friends: Down Villiers Street until the river o at 20:06, London from the Sky Garden, at the top at 20:54; margaret: British Museum: Egypt galleries, the G at 14:07, Lunch near Battersea Power Station Pie at 14:15, Quiet treasures in the British Library at 13:58; jonas+full: Quiet treasures in the British Library at 16:41; friends+relaxed: A steak and dripping chips at Flat Iro at 19:27, Dinner near Granary Square and Coal Dr at 20:40

**Unused time, all 16 days:** 1822 min, a mean of 114 min a day.

**The largest waits, and what they wait for:**
- **friends route ⚠:** 2026-12-04 goes back to A rest in the Royal Festival H after going over 3 km away
- **friends+relaxed:** 30 min before A steak and dripping chips at Flat Iron, (2026-12-04), waiting for the day's shape

**The same stop for 3 or more of the 6 travellers** (variety; fewer is better): m_to_river_villiers (4), m_rfh_foyers_rest (4), m_british_library_treasures (4), m_wellcome_reading_room (3), m_wahaca_southbank (3), m_st_dunstan_garden (3), m_sky_garden (3), m_park_break_hyde (3), m_garden_at_120 (3), a_kings_cross_canal (3)

**The test measures a good trip; it doesn't define one.** Never make a traveller's day worse to turn a check green (Abram, 24 Nov).

## Each failure (run 1)

- **sam G2b:** 2026-12-04 full, but ends 64 min early
- **sam G2b:** 2026-12-05 full, but ends 115 min early
- sam G2 (original, not a blocker): 2026-12-04 ends 64 min early
- sam G2 (original, not a blocker): 2026-12-05 ends 115 min early
- **priya G2b:** 2026-12-06 balanced, but ends 117 min early
- priya G2 (original, not a blocker): 2026-12-04 ends 75 min early
- priya G2 (original, not a blocker): 2026-12-06 ends 117 min early
- **family G11:** 2026-12-04 98 min of travel, budget 60 (gentle)
- **family G11:** 2026-12-05 99 min of travel, budget 60 (gentle)
- family G2 (original, not a blocker): 2026-12-04 ends 75 min early
- **jonas G11:** 2026-12-04 83 min of travel, budget 60 (gentle)
- jonas G2 (original, not a blocker): 2026-12-04 ends 120 min early
- **friends G2b:** 2026-12-04 full, but ends 54 min early
- **friends G11:** 2026-12-04 150 min of travel, budget 120 (full_on)
- friends G2 (original, not a blocker): 2026-12-04 ends 54 min early
- margaret G2 (original, not a blocker): 2026-12-04 ends 173 min early
- margaret G2 (original, not a blocker): 2026-12-05 ends 165 min early
- margaret G2 (original, not a blocker): 2026-12-06 ends 182 min early
- **jonas+full G2b:** 2026-12-04 full, but ends 79 min early
- **jonas+full G11:** 2026-12-04 100 min of travel, budget 60 (gentle)
- jonas+full G2 (original, not a blocker): 2026-12-04 ends 79 min early
- **friends+relaxed G2b:** 2026-12-05 relaxed, but 310 min of visits without a break
- friends+relaxed G2 (original, not a blocker): 2026-12-04 ends 93 min early
