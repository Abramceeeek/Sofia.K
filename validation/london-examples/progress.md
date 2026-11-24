# London quality work: where it stands (handover, 24 Nov 2026)

**Branch:** `claude/pensive-euler-fftd63`, branch only, on draft PR #4. Nothing here is on `main`, deployed, uploaded or in the friends' round build. It merges only once validated, before the round starts, with Abram's approval (m327).

## Commits in batch 2 (newest first)
| Commit | What |
|---|---|
| `566bb27` | m334 fix: an evening food stop counts as the dinner |
| `e9a511e` | m333 fix: a loved ride that's the day's must-do is never dropped for want of a stop near its start |
| `041de24` | m337: a day's title names its own places; the examples show the per-person total |
| `8624455` | m336: other places for a stop (Brain, iPhone, Android), each saying what it changes |
| `b88ed03` | m334–m335: dinner scored by the person, named where verified; extra places strong only |
| `fbecd6c` | m333: a day's travel against its pace's budget; rides from near their start; the gate run 3 times |

Batch 1 is `de6d48a`, `79c6ee5` and `8893856` (see `before-after-2026-11-24.md`).

## Files changed in batch 2
- **Brain code:**
  - `brain/src/brain/planner.py`: travel budget, ride rule, strong extras, one dinner, late-start tie-breaker.
  - `brain/src/brain/dayplan.py`: dinners, the no-dinner line, rides, strong extras, `plan_change`.
  - `brain/src/brain/api.py`: the alternatives endpoint, `compare_to`, the fill loop, loved must-dos, day titles.
  - `brain/src/brain/reasons.py` (`day_title`) and `brain/src/brain/schemas.py`.
- **Brain data:** `brain/data/catalogue/london.yaml` (`short` names).
- **Brain scripts:** `brain/scripts/london_gate.py` (repeat runs, audits) and `brain/scripts/london_examples.py`.
- **Tests:** `brain/tests/test_day_shape.py` and `brain/tests/test_trip_management.py`.
- **iPhone:** `app/Sources/Models.swift`, `BrainClient.swift`, `AppModel.swift`, `PlanViews.swift`.
- **Android:**
  - `Models.kt`, `BrainClient.kt`, `AppModel.kt` and `Plan.kt` in `android/app/src/main/java/com/odys/app/`;
  - `ScreensTest.kt` in `android/app/src/test/java/com/odys/app/`.
- **Docs:** `decisions/decision-log.md` (m333–m338), `decisions/after-9-nov.md` (#104), and this folder.

## Checks at `566bb27`
- **Brain:** 603 tests passed locally (Python 3.12). CI passed at `8624455`.
- **Android:** CI built the app and ran the screen tests at `8624455`, including the new "Other places for this time".
- **iPhone:** **not compiled.** iOS builds run only from `main` or a manual macOS run (paid, so not triggered).
- **The London gate** (`gate.md`, 3 runs): **NOT PASSED.**
  - **G2 fails on 7 days** in every run.
  - G1 and G3–G8 pass.
  - Waits mid-day: 1–3. Travel over budget: 235–264 min. Unused time: 1,230–1,375 min. Days breaking the strong-extras rule: 0.
- **Before and after:** `before-after-batch2-2026-11-24.md`.

## Remaining defects
1. **Empty afternoons and evenings (G2):** Priya's Saturday ends at 14:38; the friends' Friday at 19:00; Jonas at 16:23. The cause is mostly a thin catalogue.
2. **Loved boats come after 46–50 min journeys to Greenwich Pier.**
3. **Sam's Sunday keeps two fair-match shops** (within his own three places).
4. **The iPhone side of m336 has never been compiled.**
5. **Directions say "by Tube or bus" here,** because the gate and examples use the distance estimate. With the TfL key (Stage 1) they name the line.

## Next batch (Claude's hours are estimates)
1. **Verified evening and Greenwich cards** (~4 h), from official pages (D91):
   - Friday lates and a market by night;
   - Greenwich Market and the Cutty Sark, to pair with the boat;
   - live music or comedy if one is suitable.
2. **A gentle traveller's "I prefer a shorter day"** (Abram m338), with G2 measuring against it (~2 h, both apps). This is a product decision: Abram first.
3. **Rerun the question pack and three independent reviews on the new `examples.md`** (~1 h for Claude; Abram ~30 min to read).
4. **Compile the iPhone change:** on Abram's approval of a macOS run, or with the next release from `main`.

## Abram's outstanding items (unchanged)
- **Render:** a manual deploy of `c2513fa` for the Seville preview. Auto-Deploy stays off.
- **Database:** remove the IP rule and rotate the password (it was pasted into a chat); upgrade by 2 Dec.
- **Android:** delete the `android-latest` pre-release.
- **At release:** fill in the friends' round version lines in `validation/friends-round.md`.
