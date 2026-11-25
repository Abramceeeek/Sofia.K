# Batch 4, before and after (24–25 Nov 2026)

**What this compares:** the recorded baseline **`4c0ad0e`** (Abram, 24 Nov: "Use the current code commit 4c0ad0e as the recorded baseline") against **`8f21fde`**, the head's last Brain change.
- **Same everything:** the same gate script (`brain/scripts/london_gate.py`, as of `8f21fde`) run on each commit, 3 times, with the same travellers, dates (from Friday 4 Dec 2026), solver limit (1 s a search) and machine (4 CPUs).
- **The plans are the real planner's, unedited.**
- **Synthetic travellers and AI reviews are not customer evidence.** The moderated sessions (`validation/human-testing/`) are where that starts.

**The handover commit and the PR:**
- The handover commit is the newest on `claude/pensive-euler-fftd63`.
- PR #4 merges into the development branch `claude/vigilant-cannon-my82dj`, as every batch has. `main` is the frozen friends' round build (m315).

## The numbers (3 runs each, the same script)

| Measure | Baseline `4c0ad0e` | Head `8f21fde` |
|---|---|---|
| G1 unexplained gaps (as the app shows them) | 5 | **0** |
| G2a places asked for | 4 | **0** |
| G2b day feel | 11 | **6** |
| G2c time left said | 15 | **0** |
| G3–G8 | 0 | 0 |
| G9 open for the visit | 0 | 0 |
| G10 sunset stop at sunset | 0 | 0 |
| G11 travel within 20 min of the pace's budget | 10 | **5** |
| G2 original, the six travellers (not a blocker) | 12 | **10** |
| Days over the travel budget | 12 of 16 | 11–12 of 16 |
| Minutes over it | 307–315 | **223–227** |
| Unused time | 1,709–1,738 min | 1,822–1,844 min |
| Different places used | 87 | 84 |
| Ready London places | 63 | 76 |

**How to read it:**
- **London does not pass.** G2b fails 6 times (Full and Balanced days ending early) and G11 5 times (gentle days over their travel budget).
- **The baseline's G1 and G2c failures are about what the customer saw, not about the planner.** At `4c0ad0e` the free-time sentences existed, but only on the blind pair's text lines; the apps' day view never showed them (m349).
- **Unused time went up by about 110 min on purpose.** Relaxed days no longer add places (Abram: "ODYS must never confuse a busy day with a good day"). Time left at the end is now said on the plan.
- **The original G2 is still reported.** It no longer blocks (m347).

## Each traveller (run 1)

| Traveller | Day feel | Baseline `4c0ad0e` | Head `8f21fde` |
|---|---|---|---|
| **Margaret and Alan** (2 places, gentle) | Relaxed | 3 or 4 places a day; the Millennium Bridge, then 54 min to Greenwich | **Exactly 2 places and lunch each day**, done by about 14:00, with the rest said as theirs ("A relaxed day, as you asked…"). Saturday is the Queen's House, then the boat they loved from Greenwich |
| **Jonas** (3 places, gentle) | Relaxed | 5 stops for 3 asked | **3 places and lunch**: the Hunterian, the Wellcome, Hyde Park; free from 16:00, said |
| **Sam** (3 places, food, £40) | Full | Ends 18:25 and 18:44 | Ends 18:56 and 18:05: still early for a Full day. Saturday: Wahaca, Spitalfields, Beigel Bake |
| **Priya and Dan** (3 places, history) | Balanced | Tate Modern, the Millennium Bridge, Tower Bridge | **The V&A and the Sky Garden on Saturday; the Golden Hinde on Sunday.** Sunday still ends 117 min early |
| **The family** (3 places, gentle) | Balanced | City, then Hyde Park, 42 min across London | **The same Friday zig-zag.** Saturday is still 52 min to Greenwich for the boat they loved |
| **The four friends** (4 places, full-on) | Full | Both days end before 20:00 | **Saturday ends at the Sky Garden at 20:54 (new; weekends to 21:00).** Friday still 150 min of travel |

## What changed in the product
- **Day Feel (m346):**
  - Relaxed, Balanced or Full, stored with the trip, separate from pace, in both apps' "Your days";
  - changing it plans the days not yet lived again;
  - **Relaxed keeps the places asked for**;
  - extra places follow the day feel, never the pace.
- **A planner bug, found by G2a:** dinner took one of the places asked for. It now comes on top of them.
- **The end of the day** is said as the person's own, with the place's hours if they'd like to stay on. Reworded after a review, below.
- **What the Brain says about a stop reaches the phone** (m349): free time, a later start, estimates, no dinner.
- **Defects fixed, with regression tests (m349):**
  - sunset for the date and the place;
  - meal estimates said in the price;
  - no out-of-season promises;
  - no sentence twice;
  - the finish, costs and schedule agree.
- **13 verified places** (m348); 12 more checked and not added, with the reasons.
- **The gate (m347, m350):**
  - G2a–c in place of G2, the original kept;
  - G9–G11 added;
  - blockers kept apart from measurements;
  - costs per person and for the whole party.
- **Prepared, nothing uploaded (m351):** the QA build path and a neutral script for six moderated sessions.

## Fresh independent reviews (25 Nov, on the `8f21fde` examples)

REVIEWS

## Remaining defects (Claude's list, for the next batch)
1. **Full and Balanced days end early** (G2b, 6 days): for a food-loving night traveller on £40 a day, nothing strong and affordable is left in the evening near King's Cross or Brick Lane.
2. **Gentle days over their travel budget** (G11, 5 days), the family most:
   - the 52-min journey to Greenwich;
   - the City-to-Hyde-Park Friday.
   Starting the boat day at Westminster or Embankment, going east, would remove one crossing.
3. **Two meals back to back** (Sam's Borough Market, then Padella).
4. **Evenings for the lively friends:** no bar or night market among the cards yet.
5. **Families:**
   - no party total in the apps;
   - no children's fares;
   - no toilets or snacks on stops.
6. **The day's own start:** without a stay chosen, every day starts at Charing Cross.
