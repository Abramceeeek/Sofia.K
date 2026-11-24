# The London gate (m326)

Run on 24 Nov 2026, from Brain commit 4c0ad0e.

**NOT PASSED.** Six synthetic travellers through the real planner (`scripts/london_gate.py`). London passes only when every check passes in every run.

G1 gap ≤ 20 min · G2 ends ≤ 45 min early · G3 a loved place reflected · G4 no disliked kind · G5 age and booking rules · G6 every Why and best-time line true · G7 a gentle pace kept · G8 no journey longer than its visit

| Traveller | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 |
|---|---|---|---|---|---|---|---|---|
| sam | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| priya | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| family | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| jonas | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| friends | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| margaret | ✅ | ❌ 3 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Failures in total (run 1): G1 0, G2 12, G3 0, G4 0, G5 0, G6 0, G7 0, G8 0

## Repeatability

3 runs of the same commit and settings (solver limit 1.0 s a search, 4 CPUs). The solver stops at a time limit, so a run can differ slightly from the next; the tables below are run 1, and this table is every run.

| Run | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | Unused time | Waits mid-day | Days over the travel budget | Minutes over it | Different places |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 1491 min | 1, 35 min | 9 of 13 | 228 min | 68 |
| 2 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 1462 min | 1, 35 min | 9 of 13 | 220 min | 68 |
| 3 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 1448 min | 1, 35 min | 9 of 13 | 217 min | 68 |

## Quality measures (reviewed, not pass or fail)

Free time is split by kind, as Abram asked: rest, meals and wandering are part of a good day; the waits are stated on the next stop, with what they wait for. Travel is compared with a day's budget for the person's pace (gentle 60 min, medium 90 min, full_on 120 min, unstated 90 min).

Unused time is the day's window with nothing planned: a later start, waits and an early end together (fewer is better; rest, meals and wandering are planned, so they don't count).

| Traveller | Unused per day | Rest | Meals | Wandering | Waits (count, total, longest) | Later starts | Travel per day | Meals named | Titles |
|---|---|---|---|---|---|---|---|---|---|
| sam | 105 min, 111 min | 125 min | 150 min | 153 min | 0, 0 min, 0 min | 23 min | 92 min ⚠, 94 min ⚠ | 2 of 2 | ok |
| priya | 134 min, 85 min, 228 min | 165 min | 135 min | 0 min | 1, 35 min, 35 min | 49 min, 51 min, 60 min | 85 min, 117 min ⚠, 77 min | 0 of 3 | 0 alike, 1 long ⚠ |
| family | 85 min, 79 min | 129 min | 90 min | 0 min | 0, 0 min, 0 min | none | 98 min ⚠, 98 min ⚠ | 0 of 2 | 0 alike, 2 long ⚠ |
| jonas | 89 min | 246 min | 45 min | 0 min | 0, 0 min, 0 min | none | 100 min ⚠ | 0 of 1 | ok |
| friends | 78 min, 80 min | 118 min | 230 min | 73 min | 0, 0 min, 0 min | none | 143 min ⚠, 144 min ⚠ | 1 of 4 | ok |
| margaret | 149 min, 128 min, 140 min | 43 min | 135 min | 0 min | 0, 0 min, 0 min | none | 50 min, 92 min ⚠, 46 min | 0 of 3 | 0 alike, 1 long ⚠ |

**Extra places** (Abram: "it must match the person's actual preferences"): 18 places beyond the number a day each person asked for. The rule: a day holds at most that number of places with under a 0.65 chance of Good (the planner's own estimate), so every place beyond it is a strong match. Days breaking it: 0. The weaker places, within each day's own number:

- sam 2026-12-04 (5 places, 3 asked): Quiet treasures in the British Libra (gallery) 0.61
- sam 2026-12-05 (6 places, 3 asked): St Dunstan-in-the-East: a ruined chu (historic_site) 0.6; The Garden at 120: a rooftop garden  (roof_garden) 0.61
- priya 2026-12-05 (5 places, 3 asked): An unhurried hour in the Wellcome Co (museum) 0.63; Down Villiers Street until the river (riverside) 0.57
- priya 2026-12-06 (3 places, 3 asked): Tower Bridge at sunset from Alderman (riverside) 0.62
- jonas 2026-12-04 (4 places, 3 asked): A quiet hour among the Wallace Colle (museum) 0.57; Quiet treasures in the British Libra (gallery) 0.52
- friends 2026-12-04 (7 places, 4 asked): A steak and dripping chips at Flat I (restaurant) 0.64; A rest in the Royal Festival Hall's  (arts_centre) 0.62
- friends 2026-12-05 (4 places, 4 asked): A park break in Victoria Embankment  (garden) 0.62
- margaret 2026-12-05 (3 places, 2 asked): The Uber Boat up the river from Gree (river_bus) 0.53

**How each day ends:** sam: Canal steps and Coal Drops Yard at Kin at 18:25, A heated outdoor swim at London Fields at 18:44; priya: A rest in the Royal Festival Hall's fr at 16:45, The Natural History Museum: into the w at 17:34, Tower Bridge at sunset from Alderman S at 15:55; family: A pirate-ship afternoon at the Diana M at 15:45, Through Somerset House to the river te at 16:03; jonas: Quiet treasures in the British Library at 16:41; friends: Down Villiers Street until the river o at 19:57, Dinner near Granary Square and Coal Dr at 19:50; margaret: British Museum: Egypt galleries, the G at 14:36, The Uber Boat up the river from Greenw at 15:25, Sir John Soane's house of curiosities, at 14:45

**Unused time, all 13 days:** 1491 min, a mean of 115 min a day.

**The largest waits, and what they wait for:**
- **priya:** 35 min before Across the Millennium Bridge towards St  (2026-12-06), waiting for the day's shape
- **friends route ⚠:** 2026-12-04 goes back to Dinner near Victoria Embankmen after going over 3 km away
- **friends route ⚠:** 2026-12-04 goes back to Down Villiers Street until the after going over 3 km away

**The same stop for 3 or more of the 6 travellers** (variety; fewer is better): m_rfh_foyers_rest (5), m_st_dunstan_garden (3), m_garden_at_120 (3), m_british_library_treasures (3)

**The test measures a good trip; it doesn't define one.** Never make a traveller's day worse to turn a check green (Abram, 24 Nov).

## Each failure (run 1)

- **sam G2:** 2026-12-04 ends 95 min early
- **sam G2:** 2026-12-05 ends 76 min early
- **priya G2:** 2026-12-04 ends 75 min early
- **priya G2:** 2026-12-06 ends 125 min early
- **family G2:** 2026-12-04 ends 75 min early
- **family G2:** 2026-12-05 ends 57 min early
- **jonas G2:** 2026-12-04 ends 79 min early
- **friends G2:** 2026-12-04 ends 63 min early
- **friends G2:** 2026-12-05 ends 70 min early
- **margaret G2:** 2026-12-04 ends 144 min early
- **margaret G2:** 2026-12-05 ends 95 min early
- **margaret G2:** 2026-12-06 ends 135 min early
