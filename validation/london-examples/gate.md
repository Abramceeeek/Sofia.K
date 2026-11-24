# The London gate (m326)

**NOT PASSED.** Six synthetic travellers through the real planner (`scripts/london_gate.py`).

G1 gap ≤ 20 min · G2 ends ≤ 45 min early · G3 a loved place reflected · G4 no disliked kind · G5 age and booking rules · G6 every Why and best-time line true · G7 a gentle pace kept · G8 no journey longer than its visit

| Traveller | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 |
|---|---|---|---|---|---|---|---|---|
| sam | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| priya | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| family | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| jonas | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| friends | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| margaret | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Failures in total: G1 0, G2 1, G3 0, G4 0, G5 0, G6 0, G7 0, G8 0

## Free time (tracked, not a pass or fail; Abram, 24 Nov)

G1 only says no wait is unexplained. Whether the free time is good is reviewed separately: these are the waits stated on a stop as "Free time first".

| Traveller | Waits | Total | Longest |
|---|---|---|---|
| sam | 0 | 0 min | 0 min |
| priya | 5 | 243 min | 65 min |
| family | 3 | 174 min | 66 min |
| jonas | 0 | 0 min | 0 min |
| friends | 1 | 60 min | 60 min |
| margaret | 5 | 292 min | 65 min |
| **all** | **14** | **769 min** | **66 min** |

**The test measures a good trip; it doesn't define one.** Never make a traveller's day worse to turn a check green (Abram, 24 Nov).

## Each failure

- **jonas G2:** 2026-12-04 ends 60 min early
