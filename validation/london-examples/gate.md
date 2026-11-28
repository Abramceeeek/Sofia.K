# The London gate (m326)

Run on 28 Nov 2026, from Brain commit 417594a.

**NOT PASSED.** Six synthetic travellers, and two more Day Feel combinations, through the real planner (`scripts/london_gate.py`). London passes only when every check passes in every run.

G1 gap ≤ 20 min · **G2a** the places asked for (meals apart), no more than the day feel adds · **G2b** the day matches Relaxed, Balanced or Full · **G2c** time left at the end is said on the plan · G3 a loved place reflected · G4 no disliked kind · G5 age and booking rules · G6 every Why and best-time line true · G7 a gentle pace kept · G8 no journey longer than its visit · **G9** open for the whole visit that date · **G10** a sunset stop at sunset · **G11** travel within 20 min of the pace's budget · **G12** no serious route defect (a walkable link by Tube, back over a ride's course, a return after going far away) · **G13** no false or contradictory reason · **G14** a change to the day says what it changed, its cost included · **G15** two substantial meals at least three hours apart (a tasting or a snack never counts)

All of these block a release (m350). The measures further down are for a person to review.

**G2 (original)** (no day ending more than 45 min early) is reported for comparison with the earlier reports, as Abram asked, and no longer blocks (m346).

| Traveller | Day feel | G1 | G2a | G2b | G2c | G3 | G3b | G4 | G5 | G6 | G7 | G8 | G9 | G10 | G11 | G12 | G13 | G14 | G15 | G2 original |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sam | full | ✅ | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 1 |
| priya | balanced | ✅ | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 2 |
| family | balanced | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | 2 |
| jonas | relaxed | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | 1 |
| friends | full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | – |
| margaret | relaxed | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 3 |
| jonas+full | full | ✅ | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | 1 |
| friends+relaxed | relaxed | ✅ | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | 1 |

Failures in total (run 1): G1 0, G2a 0, G2b 5, G2c 0, G3 0, G3b 0, G4 0, G5 0, G6 0, G7 0, G8 0, G9 0, G10 0, G11 5, G12 0, G13 0, G14 0, G15 0; G2 original 9 for the six travellers (11 with the two combinations)

## Repeatability

3 runs of the same commit and settings (solver limit 1.0 s a search, 4 CPUs). The solver stops at a time limit, so a run can differ slightly from the next; the tables below are run 1, and this table is every run.

| Run | G1 | G2a | G2b | G2c | G3 | G3b | G4 | G5 | G6 | G7 | G8 | G9 | G10 | G11 | G12 | G13 | G14 | G15 | G2 original (six; all eight) | Unused time | Waits mid-day | Days over the travel budget | Minutes over it | Different places |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 9; 11 | 1818 min | 0, 0 min | 11 of 16 | 228 min | 83 |
| 2 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 9; 11 | 1873 min | 0, 0 min | 11 of 16 | 236 min | 83 |
| 3 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 9; 11 | 1867 min | 0, 0 min | 11 of 16 | 239 min | 83 |

## Quality measures (reviewed, not pass or fail)

Free time is split by kind, as Abram asked: rest, meals and wandering are part of a good day; the waits are stated on the next stop, with what they wait for. Travel is compared with a day's budget for the person's pace (gentle 60 min, medium 90 min, full_on 120 min, unstated 90 min).

Unused time is the day's window with nothing planned: a later start, waits and an early end together (fewer is better; rest, meals and wandering are planned, so they don't count).

| Traveller | Unused per day | Rest | Meals | Wandering | Waits (count, total, longest) | Later starts | Travel per day | Meals named | Titles |
|---|---|---|---|---|---|---|---|---|---|
| sam | 76 min, 96 min | 93 min | 127 min | 156 min | 0, 0 min, 0 min | 47 min, 23 min | 101 min ⚠, 105 min ⚠ | 2 of 2 | ok |
| priya | 136 min, 74 min, 141 min | 111 min | 135 min | 0 min | 0, 0 min, 0 min | 24 min, 34 min | 90 min, 96 min ⚠, 91 min ⚠ | 0 of 3 | 0 alike, 2 long ⚠ |
| family | 80 min, 63 min | 86 min | 90 min | 0 min | 0, 0 min, 0 min | none | 102 min ⚠, 96 min ⚠ | 0 of 2 | 0 alike, 1 long ⚠ |
| jonas | 140 min | 132 min | 45 min | 0 min | 0, 0 min, 0 min | none | 83 min ⚠ | 0 of 1 | ok |
| friends | 70 min, 86 min | 75 min | 247 min | 73 min | 0, 0 min, 0 min | 40 min, 57 min | 119 min, 129 min ⚠ | 2 of 4 | ok |
| margaret | 207 min, 185 min, 170 min | 74 min | 135 min | 0 min | 0, 0 min, 0 min | none | 25 min, 25 min, 64 min ⚠ | 0 of 3 | ok |
| jonas+full | 91 min | 169 min | 45 min | 0 min | 0, 0 min, 0 min | none | 105 min ⚠ | 0 of 1 | ok |
| friends+relaxed | 160 min, 43 min | 30 min | 247 min | 73 min | 0, 0 min, 0 min | 30 min, 23 min | 115 min, 156 min ⚠ | 2 of 4 | ok |

**Remaining time (G2c measures, m346):** each day's free time in periods over 20 min (a later start, waits and the end of the day), the longest, whether the plan says it, why it's there (chosen on a relaxed day; nothing strong enough to add; waiting for a place's time) and whether the plan offers something to do with it at the end of the day (staying on where they are):

| Traveller | Day feel | Each day: main places / asked · free time · longest · said · why · useful |
|---|---|---|
| sam | full | 4/3 · 69 min · 47 min · yes · waits for a time · –; 5/3 · 88 min · 65 min · yes · nothing strong enough to add · no |
| priya | balanced | 4/3 · 131 min · 107 min · yes · nothing strong enough to add · no; 4/3 · 69 min · 35 min · yes · waits for a time · –; 4/3 · 117 min · 117 min · yes · nothing strong enough to add · no |
| family | balanced | 4/3 · 75 min · 75 min · yes · nothing strong enough to add · no; 4/3 · 48 min · 48 min · yes · nothing strong enough to add · yes |
| jonas | relaxed | 3/3 · 120 min · 120 min · yes · chosen (relaxed) · no |
| friends | full | 6/4 · 40 min · 40 min · yes · waits for a time · –; 5/4 · 57 min · 57 min · yes · waits for a time · – |
| margaret | relaxed | 2/2 · 197 min · 197 min · yes · chosen (relaxed) · no; 2/2 · 173 min · 173 min · yes · chosen (relaxed) · yes; 2/2 · 165 min · 165 min · yes · chosen (relaxed) · no |
| jonas+full | full | 4/3 · 81 min · 81 min · yes · nothing strong enough to add · yes |
| friends+relaxed | relaxed | 4/4 · 145 min · 115 min · yes · chosen (relaxed) · no; 4/4 · 23 min · 23 min · yes · chosen (relaxed) · – |

**Journeys (m355, measured; G11 still judges the whole journey):** walking (minutes and km), Tube or bus (door to door: the walk to the station and the wait are inside the estimate; legs), the waits the day states, and the whole journey. ⚠ marks walking over 45 min a day for a gentle traveller with children, or Tube and bus over the pace's budget on their own.

| Traveller | Pace | Each day: walk min · km · Tube/bus min (legs) · waits · whole journey |
|---|---|---|
| sam | medium | 47 · 3.5 km · 54 (2) · 0 · 101; 68 · 5.1 km · 37 (1) · 0 · 105 |
| priya | medium | 90 · 6.8 km · 0 (0) · 0 · 90; 5 · 0.4 km · 91 (3) ⚠ · 0 · 96; 13 · 1.0 km · 78 (3) · 0 · 91 |
| family | gentle | 31 · 2.3 km · 71 (2) ⚠ · 0 · 102; 16 · 1.2 km · 80 (2) ⚠ · 0 · 96 |
| jonas | gentle | 53 · 4.0 km · 30 (1) · 0 · 83 |
| friends | full_on | 43 · 3.2 km · 76 (3) · 0 · 119; 32 · 2.4 km · 97 (3) · 0 · 129 |
| margaret | gentle | 1 · 0.1 km · 24 (1) · 0 · 25; 25 · 1.9 km · 0 (0) · 0 · 25; 10 · 0.8 km · 54 (1) · 0 · 64 |
| jonas+full | gentle | 46 · 3.5 km · 59 (2) · 0 · 105 |
| friends+relaxed | full_on | 40 · 3.0 km · 75 (3) · 0 · 115; 7 · 0.5 km · 149 (4) ⚠ · 0 · 156 |

**Costs (m350, measured):** each day's cost per person (entry, food and fares, from the plan's own summary) against the person's daily budget, and for the whole party at each person's own price (m353: children's prices where the card's source gives them; otherwise the adult price, named). Fares are TfL's adult fares for everyone: children's fares aren't verified yet.

| Traveller | Party | Budget a day | Each day: per person · whole party |
|---|---|---|---|
| sam | 1 adult | £40.0 | £38.00 · £38.00; £40.00 · £40.00 |
| priya | 2 adults | £70.0 | £15.00 · £30.00; £23.90 · £47.80; £23.90 · £47.80 |
| family | 2 adults, 2 children | £40.0 | £21.00 · £84.00; £34.90 · £139.60 (children's price not known: The Uber Boat up the riv) |
| jonas | 1 adult | £20.0 | £18.00 · £18.00 |
| friends | 4 adults | £70.0 | £58.40 · £233.60; £56.80 · £227.20 |
| margaret | 2 adults | none | £18.00 · £36.00; £15.00 · £30.00; £40.90 · £81.80 |
| jonas+full | 1 adult | £20.0 | £12.00 · £12.00 |
| friends+relaxed | 4 adults | £70.0 | £50.90 · £203.60; £56.80 · £227.20 |

**Generic reasons (measured; target: none for a traveller who answered onboarding, m353):** 14 of 69 planned places give only a general reason ("suits most people").

**Loved places with no card yet** (catalogue gaps, measured): Big Ben and Parliament Square; Camden Market; Hampstead Heath ponds (swimming); IFS Cloud Cable Car; Primrose Hill at sunset; Regent's Canal walk from Little Venice


**Extra places** (Abram: "it must match the person's actual preferences"): 20 places beyond the number a day each person asked for. The rule: a day holds at most that number of places with under a 0.65 chance of Good (the planner's own estimate), so every place beyond it is a strong match. Days breaking it: 0. The weaker places, within each day's own number:

- sam 2026-12-04 (6 places, 3 asked): The Garden at 120: a rooftop garden  (roof_garden) 0.61; Quiet treasures in the British Libra (gallery) 0.61
- sam 2026-12-05 (6 places, 3 asked): A wander through Covent Garden and S (area_walk) 0.62; Liberty's wooden galleries, built fr (department_store) 0.52; Burlington Arcade: a covered shoppin (arcade) 0.57
- priya 2026-12-06 (4 places, 3 asked): An unhurried hour in the Wellcome Co (museum) 0.63; Tower Bridge at sunset from Alderman (riverside) 0.62
- family 2026-12-05 (4 places, 3 asked): Burlington Arcade: a covered shoppin (arcade) 0.62; Liberty's wooden galleries, built fr (department_store) 0.6
- jonas 2026-12-04 (3 places, 3 asked): The Hunterian: the art and science o (museum) 0.63
- friends 2026-12-04 (7 places, 4 asked): A park break in Victoria Embankment  (garden) 0.62; Through the City towers, Bank to Liv (architecture_walk) 0.6; Beigel Bake: a salt beef bagel on Br (bakery) 0.64
- friends 2026-12-05 (6 places, 4 asked): A steak and dripping chips at Flat I (restaurant) 0.64
- margaret 2026-12-06 (2 places, 2 asked): The Uber Boat up the river from Gree (river_bus) 0.53
- jonas+full 2026-12-04 (4 places, 3 asked): The Hunterian: the art and science o (museum) 0.63; Quiet treasures in the British Libra (gallery) 0.52
- friends+relaxed 2026-12-05 (5 places, 4 asked): A steak and dripping chips at Flat I (restaurant) 0.64

**How each day ends:** sam: Canal steps and Coal Drops Yard at Kin at 19:38, Beigel Bake: a salt beef bagel on Bric at 18:55; priya: Waterloo Bridge at sunset, both ways at 16:13, London from the Sky Garden, at the top at 17:25, Tower Bridge at sunset from Alderman S at 16:03; family: A pirate-ship afternoon at the Diana M at 15:45, Liberty's wooden galleries, built from at 16:12; jonas: A park break: the Serpentine in Hyde P at 16:00; friends: Beigel Bake: a salt beef bagel on Bric at 20:43, Dinner near Granary Square and Coal Dr at 20:51; margaret: Across the Millennium Bridge towards S at 13:43, British Museum: Egypt galleries, the G at 14:07, Lunch near Battersea Power Station Pie at 14:15; jonas+full: Quiet treasures in the British Library at 16:39; friends+relaxed: Dinner near Sky Garden at 19:05, Dinner near Granary Square and Coal Dr at 21:00

**Unused time, all 16 days:** 1818 min, a mean of 114 min a day.

**The largest waits, and what they wait for:**

**The same stop for 3 or more of the 6 travellers** (variety; fewer is better): m_garden_at_120 (4), m_wellcome_reading_room (3), m_wahaca_southbank (3), m_st_dunstan_garden (3), m_sky_garden (3), m_park_break_hyde (3), m_liberty_timber_galleries (3), m_flat_iron_covent_garden (3), m_burlington_arcade (3), m_alderman_stairs_sunset (3), a_kings_cross_canal (3)

**The test measures a good trip; it doesn't define one.** Never make a traveller's day worse to turn a check green (Abram, 24 Nov).

## Each failure (run 1)

- **sam G2b:** 2026-12-05 full, but ends 65 min early
- sam G2 (original, not a blocker): 2026-12-05 ends 65 min early
- **priya G2b:** 2026-12-04 balanced, but ends 107 min early
- **priya G2b:** 2026-12-06 balanced, but ends 117 min early
- priya G2 (original, not a blocker): 2026-12-04 ends 107 min early
- priya G2 (original, not a blocker): 2026-12-06 ends 117 min early
- **family G11:** 2026-12-04 102 min of travel, budget 60 (gentle): 31 min walking, 71 min by Tube or bus; mostly Tube or bus
- **family G11:** 2026-12-05 96 min of travel, budget 60 (gentle): 16 min walking, 80 min by Tube or bus; mostly Tube or bus
- family G2 (original, not a blocker): 2026-12-04 ends 75 min early
- family G2 (original, not a blocker): 2026-12-05 ends 48 min early
- **jonas G11:** 2026-12-04 83 min of travel, budget 60 (gentle): 53 min walking, 30 min by Tube or bus; mostly walking
- jonas G2 (original, not a blocker): 2026-12-04 ends 120 min early
- margaret G2 (original, not a blocker): 2026-12-04 ends 197 min early
- margaret G2 (original, not a blocker): 2026-12-05 ends 173 min early
- margaret G2 (original, not a blocker): 2026-12-06 ends 165 min early
- **jonas+full G2b:** 2026-12-04 full, but ends 81 min early
- **jonas+full G11:** 2026-12-04 105 min of travel, budget 60 (gentle): 46 min walking, 59 min by Tube or bus; mostly Tube or bus
- jonas+full G2 (original, not a blocker): 2026-12-04 ends 81 min early
- **friends+relaxed G2b:** 2026-12-05 relaxed, but 397 min of visits without a break
- **friends+relaxed G11:** 2026-12-05 156 min of travel, budget 120 (full_on): 7 min walking, 149 min by Tube or bus; mostly Tube or bus
- friends+relaxed G2 (original, not a blocker): 2026-12-04 ends 115 min early
