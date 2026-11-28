# Batch 5, before and after (25 Nov 2026)

**One product commit for everything** (Abram, 25 Nov: "one consistent commit identifier for Brain tests, generated examples, London gate, three independent reviews, iOS and Android builds"): **`d6c6ab6`**.

| What | At `d6c6ab6` |
|---|---|
| Brain tests | **628 passed** (locally, Python 3.12) |
| Generated examples | `examples.md`, made from `d6c6ab6` |
| London gate | `gate.md`, 3 runs of `d6c6ab6` |
| Three independent reviews | of those examples and that gate (below) |
| Android | run 56 (manual, `d6c6ab6`): built, every screen test passed |
| iPhone | run 118 (manual simulator run, `d6c6ab6`): compiled with screenshots, upload off |

The commit after it, the batch 5 handover, changes only these documents.

**The comparison:**
- the batch 4 handover **`977ccfd`** against **`d6c6ab6`**, with the same gate script, travellers, dates (from Friday 4 Dec 2026), solver limit (1 s) and machine (4 CPUs), 3 runs each;
- at `977ccfd` the script ran with fallbacks only for names the older code doesn't have;
- **it can't see two things there:**
  - a ride's course (old cards don't record one), so G12's boat check finds nothing at `977ccfd`;
  - the Tate Modern and Sky Garden links, which didn't exist yet, so G3b counts fewer loved places.

**Synthetic travellers and AI reviews are not customer evidence.**

## The numbers (3 runs each; every run of each commit the same)

| Check | `977ccfd` | `d6c6ab6` |
|---|---|---|
| G1, G2a, G2c, G3, G3b, G4–G10 | 0 | 0 |
| G2b day feel | 7 | **6** |
| G11 travel within 20 min of the pace's budget | 5 | 5 |
| **G12 serious route defects** (new) | **4** | **0** |
| **G13 false or contradictory reasons** (new) | **28** | **0** |
| **G14 a change that isn't explained** (new) | **8** | **0** |
| G2 original, the six travellers (not a blocker) | 10 | 10 |
| Days over the travel budget | 12 of 16 | 11 of 16 |
| Minutes over it | 227 | 236 |
| Unused time | 1,827 min | 1,844 min |
| Generic reasons (target: none) | — | 0 of 68 places |
| Different places used | 84 | 82 |

**London does not pass.** G2b fails 6 times (Full and Balanced days ending early; one relaxed day without a break) and G11 5 times (gentle days over their travel budget).

## What changed (m353, m354)
- **Abram's data decisions:** the Golden Hinde and Mildreds back to draft. No ambiguous time is read as a closure, and no $ price is read as pounds.
- **Routes:**
  - short links are walked;
  - a ride's own course is never gone back over the same day;
  - a day that crosses London and comes back is planned again without the place it comes back to.
- **Loved places:** Tate Modern and the Sky Garden were never linked to the swipe places people loved. They are now, and G3b checks loved places across the whole trip.
- **Meals:** no named food place within two hours of another food stop.
- **Reasons:** a loved place is named only for the feature that defines it.
- **Rain:** a paid option says its price, budget, booking, distance and a free alternative.
- **Changes:** a re-planned trip day says what changed, its cost included, in both apps.
- **Families:** children's prices from five cards' own sources, and a party total at each person's own price.
- **Groups:** nobody is named in a group explanation without agreeing; a favourite is swapped in only when it's good for its member and not poor for anyone else.

## Three fresh independent reviews (25 Nov, of the `d6c6ab6` examples)

| Traveller | London local | Families and gentle pace | Sceptical product reviewer |
|---|---|---|---|
| Sam | 5/10 | 6/10 | no |
| Priya and Dan | 6/10 | 7/10 | with small fixes |
| Family | 5/10 | 5/10 | no |
| Jonas | 3/10 | 5/10 | no |
| Four friends | 5/10 | 5/10 | with small fixes |
| Margaret and Alan | 7/10 | 7/10 | with small fixes |
| **Verdict** | not yet | nearly | **5/10 against a well-informed friend; not yet** |

At batch 4 they gave 4–7/10, and the sceptical reviewer 5/10. **The scores didn't move.** The fixes removed the faults the reviewers named last time, and they found the next layer. Everything they agree on is below.

## What the reviews found, and Claude's check of each

**False statements (blockers under Abram's rule; first in the next batch):**
1. **A paid rain option said "still fits your day's budget" when it didn't.** Poppie's £22 against the friends' £70: the check left out the day's fares. Confirmed in the code (`add_rain_swaps` counts spending without fares). A meal also shouldn't be offered as the rain option for a view.
2. **"Tate Modern is open until 17:00"** gave the traveller's own end time, not the gallery's. Confirmed (`free_after` shows the earlier of the two).

**Routes the gate doesn't catch yet:**
- The friends' Embankment Gardens → Hyde Park → Villiers Street, back beside where they were. It's under G12's 3 km.
- Greenwich days that go out by DLR and come back by the boat they loved. A friend would take the boat out, but ODYS has no eastbound boat card with a verified time and fare.

**Reasons still stretched:**
- feelings linked through a weak feature ("restored… a sense of awe" for Liberty);
- a loved place linked through a stop's weak feature ("Borough Market… somewhere local and new" for Burlington Arcade);
- "one of your interests" that names none.

**Meals:**
- Sam's Wahaca at 12:00 and Borough Market at 14:21: two lunches, 141 min apart, which the two-hour rule misses;
- lunches at 11:30–12:00;
- the friends' Friday evening is empty.

**Families:**
- whether a budget is per person or for the whole party (**Abram's decision**);
- no children's fares (TfL not verified);
- no way back timed or costed.

**Filler:** Liberty, Burlington Arcade and the Garden at 120 each appear for three travellers.

**Facts to check** (the reviewers' memory, not verified):
- the boat's £22.90 (a day ticket?);
- the Diana playground's December closing time;
- the British Library on a Friday evening;
- "£3.00 a Tube or bus journey" (buses cost less);
- London Fields is on the Overground.

## Remaining defects, most harmful first (the next batch)
1. The two false statements above, and a G13 check for each.
2. Routes:
   - lower G12's distance for a return, or measure route efficiency;
   - an eastbound boat card, verified;
   - count walking apart from Tube journeys in G11 (Abram's decision).
3. Reasons: a link needs the feature to be strong on both sides. An existing test, the boat and Waterloo Bridge, would change with it.
4. Meals: lunch from about 12:00, three hours between food stops, and an evening for the lively.
5. Families: per-person or party budgets (Abram), children's fares once verified, the way back.
6. Filler: cap how often one place appears across travellers, as a warning with a target.
