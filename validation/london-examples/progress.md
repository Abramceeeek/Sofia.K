# London quality work: where it stands (handover, 24 Nov 2026)

**Branch:** `claude/pensive-euler-fftd63`, branch only. Nothing here is on `main`, deployed, or in the friends' round build (m327: merge only once validated, and before the round starts).

## Commits in this stretch (newest first)
| Commit | What |
|---|---|
| `de6d48a` | m331–m332: no mid-day waits, genuine extra places, loved places across a trip, one view from above, no rest first, the Wellcome Reading Room, the gate's quality measures, `tests/test_day_shape.py` |
| `79c6ee5` | m331 checkpoint: journey costs by pace; loved places never refused for distance |
| `d45094f` | m329–m330: the British Library card, a gentle pace keeps strenuous cards out, proportionate journeys |
| `d16e70e` | m328: the solver's waiting cost; G2 5 → 1 |
| `756981d` | m327: release decision; every plan records the Brain commit and the app build |
| `b7c6159`, `326b045`, `00188fe` | m326: the London gate and its first passes |

## Checks, as of `de6d48a`
- **Brain tests:** 593 passed (`pytest`, Python 3.12, 24 Nov).
- **The London gate** (`gate.md`): G1 and G3–G8 pass for all six travellers. **G2 fails on 6 of 13 days** (64–126 min early). There are no mid-day waits, and unused time is about 1,000 min (1,321 before batch 1). **Not passed, so not ready to release** (m327).
- **Before and after, per traveller:** `before-after-2026-11-24.md`.
- **The apps:** nothing changed in batch 1, which is Brain only.

## What a passing unit test doesn't show
The gate's travellers are synthetic, and the judgements in `before-after-2026-11-24.md` are Claude's. The two reviews from other models (`answers/`) were of the older plans. **Next:** run the question pack (`questions-for-other-ais.md`) on the new `examples.md`, plus one fresh subagent review. Real evidence comes only from the friends' round.

## Next tasks (in order; Claude's hours are estimates)
1. **Dinner scored by the person's liking for food**, as lunch's credit works (open issue 1). ~2 h.
2. **A loved ride's start as a neighbourhood:** Greenwich with the boat, not a 50-min journey to the pier and away (open issue 3). ~3 h.
3. **Titles:** shorter and less alike (the gate flags 1–3 per traveller). ~1.5 h.
4. **Named food from verified sources only** (Overture places with a confident category, open and checked), never halal or allergen claims (m323–m325 rules). ~4 h for a London pilot.
5. **Editing and recovery:** a single-stop swap inside a trip day, reusing "swap this stop" (D110) and "Re-plan the rest of today" (D124); a rain swap offer ("Replace stop / Keep original"). ~6 h, Brain and both apps.
6. **Costs and directions:** each and for the party; "Tube or bus" made specific where TfL gives the line. ~3 h.
7. **Rerun the gate, the examples and three independent reviews; then Abram decides on the release.** ~1 h for Claude; Abram ~30 min to read.

## Decisions for Abram
- **D127 for history lovers:** two history stops a day caps Priya's Sunday. Keep it, or allow three when history is the person's top weight?
- **Jonas's early end:** a calm day that finishes at 16:23 (97 min early). Accept it as free time, or should Claude look for another verified, quiet, free place near King's Cross open to 18:00 on Fridays?

## Abram's outstanding items (unchanged)
- Render: a manual deploy of `c2513fa` for the Seville preview (Auto-Deploy stays off).
- Database: remove the IP rule and rotate the password (it was pasted into a chat); upgrade by 2 Dec.
- Delete the `android-latest` pre-release.
- Fill in the friends' round version lines (`validation/friends-round.md`) at release.
