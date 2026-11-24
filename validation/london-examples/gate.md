# The London gate (m326)

**NOT PASSED.** Six synthetic travellers through the real planner (`scripts/london_gate.py`).

G1 gap ≤ 20 min · G2 ends ≤ 45 min early · G3 a loved place reflected · G4 no disliked kind · G5 age and booking rules · G6 every Why and best-time line true

| Traveller | G1 | G2 | G3 | G4 | G5 | G6 |
|---|---|---|---|---|---|---|
| sam | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ |
| priya | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ |
| family | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| jonas | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ |
| friends | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ |
| margaret | ✅ | ❌ 1 | ✅ | ✅ | ✅ | ✅ |

Failures in total: G1 0, G2 5, G3 0, G4 0, G5 0, G6 0

Free time stated on a stop (not a failure; fewer is better): 20 waits, 1109 min in all.

## Each failure

- **sam G2:** 2026-12-04 ends 60 min early
- **priya G2:** 2026-12-06 ends 83 min early
- **jonas G2:** 2026-12-04 ends 77 min early
- **friends G2:** 2026-12-04 ends 120 min early
- **margaret G2:** 2026-12-05 ends 85 min early
