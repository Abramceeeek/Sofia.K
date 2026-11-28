# Batch 4, before and after (24–25 Nov 2026)

**What this compares:** the recorded baseline **`4c0ad0e`** (Abram, 24 Nov: "Use the current code commit 4c0ad0e as the recorded baseline") against **`8f21fde`** (the batch's work) and **`1746408`** (after the fixes from the reviews).
- **Same everything:** the same gate script (`brain/scripts/london_gate.py`) run on each commit, 3 times, with the same travellers, dates (from Friday 4 Dec 2026), solver limit (1 s a search) and machine (4 CPUs).
- **The plans are the real planner's, unedited.**
- **Synthetic travellers and AI reviews are not customer evidence.** The moderated sessions (`validation/human-testing/`) are where that starts.

**The handover commit and the PR:**
- The handover commit is the newest on `claude/pensive-euler-fftd63`.
- PR #4 merges into the development branch `claude/vigilant-cannon-my82dj`, as every batch has. `main` is the frozen friends' round build (m315).

## The numbers (3 runs each, the same script)

| Measure | Baseline `4c0ad0e` | `8f21fde` | Final `1746408` |
|---|---|---|---|
| G1 unexplained gaps (as the app shows them) | 5 | **0** | **0** |
| G2a places asked for | 4 | **0** | **0** |
| G2b day feel | 11 | **6** | **7** |
| G2c time left said | 15 | **0** | **0** |
| G3–G8 | 0 | 0 | 0 |
| G9 open for the visit | 0 | 0 | 0 |
| G10 sunset stop at sunset (and still there as it sets, from `1746408`) | 0 | 0 | 0 |
| G11 travel within 20 min of the pace's budget | 10 | **5** | **5** |
| G2 original, the six travellers (not a blocker) | 12 | **10** | **10** |
| Days over the travel budget | 12 of 16 | 11–12 of 16 | 10–11 of 16 |
| Minutes over it | 307–315 | **223–227** | **208–218** |
| Unused time | 1,709–1,738 min | 1,822–1,844 min | 1,858–1,870 min |
| Different places used | 87 | 84 | 84 |
| Ready London places | 63 | 76 | 76 |

**How to read it:**
- **London does not pass.** At `1746408`, G2b fails 7 times (Full and Balanced days ending early, one relaxed day without a break) and G11 5 times (gentle days over their travel budget). G2b went from 6 to 7 because sunset stops now span the sunset, which moved Priya's Friday to end 107 min early.
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

Three subagents read the plans, each with a different brief. **They aren't real travellers, so this is still not evidence about customers.**

| Traveller | London local | Families and gentle pace | Sceptical product reviewer |
|---|---|---|---|
| Sam | 5/10 | 6/10 | no |
| Priya and Dan | 6/10 | 6/10 | with small fixes |
| Family | 5/10 | 4/10 | no |
| Jonas | 4/10 | 5/10 | no |
| Four friends | 4/10 | 6/10 | with small fixes |
| Margaret and Alan | 7/10 | 7/10 | with small fixes |
| **Verdict** | not yet | nearly (couples, retirees); not yet for families | **5/10 against a well-informed friend; not yet** |

At batch 3 (`14c781b`) they gave 4–6/10, and the sceptical reviewer 4/10.

**What all three agree on:**
1. **Relaxed is respected.** Jonas gets 3 places and lunch; Margaret and Alan get 2 and lunch each day. "A relaxed day, as you asked: the rest of it is yours" reads well.
2. **Routes a Londoner wouldn't take:**
   - the Tube from the Serpentine to the Diana playground, a walk across the park;
   - the boat to Battersea past the Southbank, then 29 min by Tube back to it;
   - Greenwich by Tube (52 min) when there's a direct train (their knowledge, not checked);
   - Sam doubling back to Villiers Street.
3. **Meals and evenings:**
   - Sam eats twice in two hours (Borough Market, then Padella), then has no dinner;
   - Jonas's lunch is £15 on an under-£20 budget;
   - the lively friends get no pub, bar or night market.
4. **Loved places missed:** Jonas's Regent's Canal and Primrose Hill at sunset, Margaret's Tate Modern, the friends' Camden and the cable car.
5. **Reasons that read like a bot:** "You loved Sky Garden, and this has green space" on a bike loop; "You loved Regent's Canal walk" on the Hunterian.
6. **Day Feel is visible for Relaxed, much less for Full and Balanced:** both Full trips still end 1–2 hours early.

**What the gate can still miss (the sceptical review):**
- G6 passes the bot-like reasons;
- G3 passes Jonas through a reason that names the canal;
- G8 doesn't block backtracking;
- G5 and G9 don't cover the rain options, and the Sky Garden and Horizon 22 need tickets.

**Fixed after the reviews (m352, `1746408`):**
- a sunset stop now spans the sunset (Waterloo Bridge left at 15:48 for a 15:52 sunset);
- no "open until" for a public street or a 24-hour bakery;
- Somerset House's courtyard is an ice rink from November to early January (official page), no longer "quiet";
- Padella no longer reads "Book ahead: No reservations";
- the fuller days' free time no longer reads like a failure.
Tested.

**Left for the next batch** (in the list below): routes, meals, evenings, loved places, reasons and the gate's gaps.

## Remaining defects (for the next batch, most harmful first)
1. **Routes:**
   - **Walkable links sent by Tube:** the Serpentine to the Diana playground, and the British Museum from Charing Cross.
   - **The boat past the Southbank, then the Tube back to it.** Starting the boat day eastbound from Embankment would remove a crossing.
   - **Direct trains ignored** (Charing Cross to London Bridge or Greenwich). They need TfL's journey times (the TfL key is Abram's) or a walk-or-rail rule.
   - **Gentle days over their travel budget** (G11, 5 days).
2. **Loved places missed:** Jonas's Regent's Canal and Primrose Hill at sunset, Margaret's Tate Modern, the friends' Camden and the cable car. Today a loved place is a day's must-do only if it fits that stretch; it should weigh more across the trip.
3. **Meals:**
   - two meals back to back (Sam);
   - Jonas's £15 lunch on an under-£20 budget, while the family gets £6;
   - lunches at 11:30–11:57.
4. **Evenings:** no pub, bar or night market among the cards. Full and Balanced days still end early (G2b, 6 days).
5. **Reasons that compare unlike places** ("You loved Sky Garden, and this has green space"), and "Good to know: it can be busy" listed as a reason.
6. **Rain options** that need tickets (the Sky Garden, Horizon 22) don't say so. The lido doesn't say to bring swimwear.
7. **Families:**
   - no party total in the apps;
   - no children's fares;
   - no toilets or snacks on stops.
   The Uber Boat's £22.90 should be checked against the single fare (a reviewer thinks it's the Roamer; not checked).
8. **The gate:** backtracking, rain options and reasons a person wouldn't agree with aren't blockers yet. Making them blockers is an authorised change to the gate, so it's Abram's decision.
9. **The day's start:** without a stay chosen, every day starts at Charing Cross.
