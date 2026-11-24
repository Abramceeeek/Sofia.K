# The London gate (m326)

Run on 24 Nov 2026, from Brain commit de6d48a.

**NOT PASSED.** Six synthetic travellers through the real planner (`scripts/london_gate.py`).

G1 gap ≤ 20 min · G2 ends ≤ 45 min early · G3 a loved place reflected · G4 no disliked kind · G5 age and booking rules · G6 every Why and best-time line true · G7 a gentle pace kept · G8 no journey longer than its visit

| Traveller | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 |
|---|---|---|---|---|---|---|---|---|
| sam | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| priya | ✅ | ❌ 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| family | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| jonas | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| friends | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| margaret | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Failures in total: G1 0, G2 6, G3 0, G4 0, G5 0, G6 0, G7 0, G8 0

## Free time (tracked, not a pass or fail; Abram, 24 Nov)

G1 only says no wait is unexplained. Whether the free time is good is reviewed separately: these are the waits stated on a stop as "Free time first".

| Traveller | Waits | Total | Longest |
|---|---|---|---|
| sam | 0 | 0 min | 0 min |
| priya | 0 | 0 min | 0 min |
| family | 0 | 0 min | 0 min |
| jonas | 0 | 0 min | 0 min |
| friends | 0 | 0 min | 0 min |
| margaret | 0 | 0 min | 0 min |
| **all** | **0** | **0 min** | **0 min** |

## Quality measures (reviewed, not pass or fail)

Free time is split by kind, as Abram asked: rest, meals and wandering are part of a good day; the waits are stated on the next stop, with what they wait for. Travel is compared with a day's budget for the person's pace (gentle 60 min, medium 90 min, full_on 120 min, unstated 90 min).

Unused time is the day's window with nothing planned: a later start, waits and an early end together (fewer is better; rest, meals and wandering are planned, so they don't count).

| Traveller | Unused per day | Rest | Meals | Wandering | Waits (count, total, longest) | Later starts | Travel per day | Meals named | Titles |
|---|---|---|---|---|---|---|---|---|---|
| sam | 72 min, 5 min | 141 min | 117 min | 148 min | 0, 0 min, 0 min | none | 120 min ⚠, 129 min ⚠ | 2 of 2 | 0 alike, 2 long ⚠ |
| priya | 48 min, 137 min, 186 min | 111 min | 135 min | 0 min | 0, 0 min, 0 min | 27 min, 36 min, 55 min | 84 min, 135 min ⚠, 70 min | 0 of 3 | 3 alike, 1 long ⚠ |
| family | 10 min, 53 min | 134 min | 90 min | 0 min | 0, 0 min, 0 min | none | 143 min ⚠, 125 min ⚠ | 0 of 2 | 0 alike, 1 long ⚠ |
| jonas | 102 min | 166 min | 45 min | 83 min | 0, 0 min, 0 min | none | 84 min ⚠ | 0 of 1 | 0 alike, 1 long ⚠ |
| friends | 47 min, 168 min | 124 min | 210 min | 73 min | 0, 0 min, 0 min | 60 min | 150 min ⚠, 91 min | 0 of 4 ⚠ | 0 alike, 2 long ⚠ |
| margaret | 19 min, 89 min, 43 min | 160 min | 135 min | 0 min | 0, 0 min, 0 min | 33 min | 85 min ⚠, 89 min ⚠, 87 min ⚠ | 0 of 3 | 3 alike, 2 long ⚠ |

**Unused time, all 13 days:** 979 min, a mean of 75 min a day.

**The largest waits, and what they wait for:**

**The same stop for 3 or more of the 6 travellers** (variety; fewer is better): m_rfh_foyers_rest (5), m_waterloo_bridge_sunset (4), m_wellcome_reading_room (3), m_uber_boat_west_day (3), m_to_river_villiers (3), m_liberty_timber_galleries (3), m_garden_at_120 (3), m_burlington_arcade (3), m_british_library_treasures (3), a_kings_cross_canal (3)

**The test measures a good trip; it doesn't define one.** Never make a traveller's day worse to turn a check green (Abram, 24 Nov).

## Each failure

- **sam G2:** 2026-12-04 ends 64 min early
- **priya G2:** 2026-12-05 ends 83 min early
- **priya G2:** 2026-12-06 ends 126 min early
- **jonas G2:** 2026-12-04 ends 97 min early
- **friends G2:** 2026-12-05 ends 90 min early
- **margaret G2:** 2026-12-05 ends 74 min early
