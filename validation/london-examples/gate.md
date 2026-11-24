# The London gate (m326)

Run on 24 Nov 2026, from Brain commit 566bb27.

**NOT PASSED.** Six synthetic travellers through the real planner (`scripts/london_gate.py`). London passes only when every check passes in every run.

G1 gap ≤ 20 min · G2 ends ≤ 45 min early · G3 a loved place reflected · G4 no disliked kind · G5 age and booking rules · G6 every Why and best-time line true · G7 a gentle pace kept · G8 no journey longer than its visit

| Traveller | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 |
|---|---|---|---|---|---|---|---|---|
| sam | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| priya | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| family | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| jonas | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| friends | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| margaret | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Failures in total (run 1): G1 0, G2 7, G3 0, G4 0, G5 0, G6 0, G7 0, G8 0

## Repeatability

3 runs of the same commit and settings (solver limit 1.0 s a search, 4 CPUs). The solver stops at a time limit, so a run can differ slightly from the next; the tables below are run 1, and this table is every run.

| Run | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | Unused time | Waits mid-day | Days over the travel budget | Minutes over it | Different places |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 1241 min | 1, 22 min | 9 of 13 | 264 min | 74 |
| 2 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 1230 min | 1, 22 min | 9 of 13 | 264 min | 74 |
| 3 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 1375 min | 3, 127 min | 8 of 13 | 235 min | 73 |

## Quality measures (reviewed, not pass or fail)

Free time is split by kind, as Abram asked: rest, meals and wandering are part of a good day; the waits are stated on the next stop, with what they wait for. Travel is compared with a day's budget for the person's pace (gentle 60 min, medium 90 min, full_on 120 min, unstated 90 min).

Unused time is the day's window with nothing planned: a later start, waits and an early end together (fewer is better; rest, meals and wandering are planned, so they don't count).

| Traveller | Unused per day | Rest | Meals | Wandering | Waits (count, total, longest) | Later starts | Travel per day | Meals named | Titles |
|---|---|---|---|---|---|---|---|---|---|
| sam | 120 min, 99 min | 47 min | 128 min | 151 min | 0, 0 min, 0 min | none | 99 min ⚠, 102 min ⚠ | 2 of 2 | 0 alike, 1 long ⚠ |
| priya | 48 min, 158 min, 173 min | 111 min | 135 min | 0 min | 0, 0 min, 0 min | 27 min, 57 min, 55 min | 84 min, 119 min ⚠, 70 min | 0 of 3 | 0 alike, 3 long ⚠ |
| family | 5 min, 68 min | 134 min | 90 min | 0 min | 0, 0 min, 0 min | 42 min | 136 min ⚠, 111 min ⚠ | 0 of 2 | ok |
| jonas | 102 min | 166 min | 45 min | 83 min | 0, 0 min, 0 min | none | 84 min ⚠ | 0 of 1 | ok |
| friends | 202 min, 92 min | 123 min | 210 min | 73 min | 1, 22 min, 22 min | 60 min, 54 min | 119 min, 108 min | 0 of 4 ⚠ | ok |
| margaret | 5 min, 89 min, 80 min | 150 min | 135 min | 0 min | 0, 0 min, 0 min | 33 min | 78 min ⚠, 89 min ⚠, 76 min ⚠ | 0 of 3 | 0 alike, 2 long ⚠ |

**Extra places** (Abram: "it must match the person's actual preferences"): 24 places beyond the number a day each person asked for. The rule: a day holds at most that number of places with under a 0.65 chance of Good (the planner's own estimate), so every place beyond it is a strong match. Days breaking it: 0. The weaker places, within each day's own number:

- sam 2026-12-04 (5 places, 3 asked): A wander through Covent Garden and S (area_walk) 0.62; Leadenhall Market: Victorian arches  (market_hall) 0.54
- sam 2026-12-05 (6 places, 3 asked): Burlington Arcade: a covered shoppin (arcade) 0.57; Liberty's wooden galleries, built fr (department_store) 0.52; Quiet treasures in the British Libra (gallery) 0.61
- priya 2026-12-04 (7 places, 3 asked): Down Villiers Street until the river (riverside) 0.57
- priya 2026-12-05 (4 places, 3 asked): An unhurried hour in the Wellcome Co (museum) 0.63; Tower Bridge at sunset from Alderman (riverside) 0.62
- priya 2026-12-06 (3 places, 3 asked): The whole of London from General Wol (viewpoint) 0.51
- jonas 2026-12-04 (4 places, 3 asked): Quiet treasures in the British Libra (gallery) 0.52; Canal steps and Coal Drops Yard at K (waterfront) 0.6
- friends 2026-12-05 (6 places, 4 asked): A park break in Victoria Embankment  (garden) 0.62; A rest in the Royal Festival Hall's  (arts_centre) 0.62; Beigel Bake: a salt beef bagel on Br (bakery) 0.64
- margaret 2026-12-04 (6 places, 2 asked): Down Villiers Street until the river (riverside) 0.55
- margaret 2026-12-05 (3 places, 2 asked): The Uber Boat up the river from Gree (river_bus) 0.53
- margaret 2026-12-06 (4 places, 2 asked): Waterloo Bridge at sunset, both ways (bridge) 0.64

**How each day ends:** sam: A heated outdoor swim at London Fields at 18:13, Beigel Bake: a salt beef bagel on Bric at 18:46; priya: Waterloo Bridge at sunset, both ways at 17:44, Tower Bridge at sunset from Alderman S at 16:37, The whole of London from General Wolfe at 16:07; family: The whole of London from General Wolfe at 17:00, Through Somerset House to the river te at 16:59; jonas: Canal steps and Coal Drops Yard at Kin at 16:23; friends: Dinner near British Library at 19:00, Dinner near London Fields Lido at 20:29; margaret: A rest in the Royal Festival Hall's fr at 17:00, The Natural History Museum: into the w at 15:46, Waterloo Bridge at sunset, both ways at 16:23

**Unused time, all 13 days:** 1241 min, a mean of 95 min a day.

**The largest waits, and what they wait for:**
- **friends:** 22 min before A bike loop round Hyde Park (2026-12-04), waiting for the day's shape

**The same stop for 3 or more of the 6 travellers** (variety; fewer is better): m_rfh_foyers_rest (4), m_wellcome_reading_room (3), m_waterloo_bridge_sunset (3), m_liberty_timber_galleries (3), m_burlington_arcade (3), m_british_library_treasures (3), a_kings_cross_canal (3)

**The test measures a good trip; it doesn't define one.** Never make a traveller's day worse to turn a check green (Abram, 24 Nov).

## Each failure (run 1)

- **sam G2:** 2026-12-04 ends 107 min early
- **sam G2:** 2026-12-05 ends 74 min early
- **priya G2:** 2026-12-05 ends 83 min early
- **priya G2:** 2026-12-06 ends 113 min early
- **jonas G2:** 2026-12-04 ends 97 min early
- **friends G2:** 2026-12-04 ends 120 min early
- **margaret G2:** 2026-12-05 ends 74 min early
