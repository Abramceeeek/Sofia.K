# The London gate (m326)

Run on 24 Nov 2026, from Brain commit 14c781b.

**NOT PASSED.** Six synthetic travellers through the real planner (`scripts/london_gate.py`). London passes only when every check passes in every run.

G1 gap ≤ 20 min · G2 ends ≤ 45 min early · G3 a loved place reflected · G4 no disliked kind · G5 age and booking rules · G6 every Why and best-time line true · G7 a gentle pace kept · G8 no journey longer than its visit

| Traveller | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 |
|---|---|---|---|---|---|---|---|---|
| sam | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| priya | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| family | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| jonas | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| friends | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| margaret | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Failures in total (run 1): G1 0, G2 10, G3 0, G4 0, G5 0, G6 0, G7 0, G8 0

## Repeatability

3 runs of the same commit and settings (solver limit 1.0 s a search, 4 CPUs). The solver stops at a time limit, so a run can differ slightly from the next; the tables below are run 1, and this table is every run.

| Run | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | Unused time | Waits mid-day | Days over the travel budget | Minutes over it | Different places |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 1293 min | 1, 37 min | 8 of 13 | 235 min | 71 |
| 2 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 1236 min | 1, 37 min | 8 of 13 | 255 min | 72 |
| 3 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 1240 min | 1, 37 min | 8 of 13 | 250 min | 72 |

## Quality measures (reviewed, not pass or fail)

Free time is split by kind, as Abram asked: rest, meals and wandering are part of a good day; the waits are stated on the next stop, with what they wait for. Travel is compared with a day's budget for the person's pace (gentle 60 min, medium 90 min, full_on 120 min, unstated 90 min).

Unused time is the day's window with nothing planned: a later start, waits and an early end together (fewer is better; rest, meals and wandering are planned, so they don't count).

| Traveller | Unused per day | Rest | Meals | Wandering | Waits (count, total, longest) | Later starts | Travel per day | Meals named | Titles |
|---|---|---|---|---|---|---|---|---|---|
| sam | 168 min, 162 min | 50 min | 167 min | 148 min | 1, 37 min, 37 min | 60 min | 90 min, 63 min | 2 of 3 | ok |
| priya | 48 min, 158 min, 144 min | 106 min | 135 min | 0 min | 0, 0 min, 0 min | 27 min, 57 min | 84 min, 119 min ⚠, 84 min | 0 of 3 | 0 alike, 2 long ⚠ |
| family | 85 min, 43 min | 129 min | 90 min | 0 min | 0, 0 min, 0 min | 25 min | 98 min ⚠, 99 min ⚠ | 0 of 2 | 0 alike, 2 long ⚠ |
| jonas | 89 min | 246 min | 45 min | 0 min | 0, 0 min, 0 min | none | 100 min ⚠ | 0 of 1 | ok |
| friends | 80 min, 80 min | 118 min | 230 min | 73 min | 0, 0 min, 0 min | none | 143 min ⚠, 144 min ⚠ | 1 of 4 | ok |
| margaret | 5 min, 99 min, 132 min | 153 min | 135 min | 0 min | 0, 0 min, 0 min | none | 78 min ⚠, 84 min ⚠, 60 min | 0 of 3 | 0 alike, 2 long ⚠ |

**Extra places** (Abram: "it must match the person's actual preferences"): 20 places beyond the number a day each person asked for. The rule: a day holds at most that number of places with under a 0.65 chance of Good (the planner's own estimate), so every place beyond it is a strong match. Days breaking it: 0. The weaker places, within each day's own number:

- sam 2026-12-05 (4 places, 3 asked): A wander through Covent Garden and S (area_walk) 0.62; Centuries of British faces at the Na (gallery) 0.52
- priya 2026-12-04 (7 places, 3 asked): Down Villiers Street until the river (riverside) 0.57
- priya 2026-12-05 (4 places, 3 asked): An unhurried hour in the Wellcome Co (museum) 0.63; Tower Bridge at sunset from Alderman (riverside) 0.62
- priya 2026-12-06 (3 places, 3 asked): The Uber Boat up the river from Gree (river_bus) 0.54
- jonas 2026-12-04 (4 places, 3 asked): A quiet hour among the Wallace Colle (museum) 0.57; Quiet treasures in the British Libra (gallery) 0.52
- friends 2026-12-04 (7 places, 4 asked): A steak and dripping chips at Flat I (restaurant) 0.64; A rest in the Royal Festival Hall's  (arts_centre) 0.62
- friends 2026-12-05 (4 places, 4 asked): A park break in Victoria Embankment  (garden) 0.62
- margaret 2026-12-04 (6 places, 2 asked): Down Villiers Street until the river (riverside) 0.55
- margaret 2026-12-05 (3 places, 2 asked): The Uber Boat up the river from Gree (river_bus) 0.53

**How each day ends:** sam: A heated outdoor swim at London Fields at 17:17, Dinner near Burlington Arcade at 19:00; priya: Waterloo Bridge at sunset, both ways at 17:44, Tower Bridge at sunset from Alderman S at 16:37, The Uber Boat up the river from Greenw at 15:52; family: A pirate-ship afternoon at the Diana M at 15:45, Through Somerset House to the river te at 16:59; jonas: Quiet treasures in the British Library at 16:41; friends: Dinner near the Golden Jubilee footbri at 19:50, Dinner near Granary Square and Coal Dr at 19:50; margaret: A rest in the Royal Festival Hall's fr at 17:00, The Natural History Museum: into the w at 15:36, Quiet treasures in the British Library at 14:58

**Unused time, all 13 days:** 1293 min, a mean of 99 min a day.

**The largest waits, and what they wait for:**
- **sam:** 37 min before A wander through Covent Garden and Soho (2026-12-05), waiting for the day's shape
- **friends route ⚠:** 2026-12-04 goes back to Down Villiers Street until the after going over 3 km away
- **friends route ⚠:** 2026-12-04 goes back to Dinner near the Golden Jubilee after going over 3 km away

**The same stop for 3 or more of the 6 travellers** (variety; fewer is better): m_rfh_foyers_rest (5), m_wellcome_reading_room (3), m_uber_boat_west_day (3), m_to_river_villiers (3)

**The test measures a good trip; it doesn't define one.** Never make a traveller's day worse to turn a check green (Abram, 24 Nov).

## Each failure (run 1)

- **sam G2:** 2026-12-04 ends 163 min early
- **sam G2:** 2026-12-05 ends 60 min early
- **priya G2:** 2026-12-05 ends 83 min early
- **priya G2:** 2026-12-06 ends 128 min early
- **family G2:** 2026-12-04 ends 75 min early
- **jonas G2:** 2026-12-04 ends 79 min early
- **friends G2:** 2026-12-04 ends 70 min early
- **friends G2:** 2026-12-05 ends 70 min early
- **margaret G2:** 2026-12-05 ends 84 min early
- **margaret G2:** 2026-12-06 ends 122 min early
