# London quality work: where it stands (handover, 24 Nov 2026, end of batch 3)

**Branch:** `claude/pensive-euler-fftd63`, branch only, on PR #4. Nothing here is on `main`, deployed, uploaded or in the friends' round build. It is **not merged** (Abram, 24 Nov).

## Batch 3 commits (newest first)
| Commit | What |
|---|---|
| `4c0ad0e` | m345: fixes from three independent reviews: extra places by pace, sunset at sunset, the right finish, honest meals |
| `14c781b` | m340 fix: museums tagged history-and-culture 2 |
| `daec99c` | m344: the day-feel preference, proposed; the Brain honours it |
| `15aa6a7` | m343: estimates said as estimates; the transparency review |
| `4f4dd66` | m342: group trips: who each stop suits, the slowest pace; the proposal |
| `8682245` | m341: one-tap rain swap; "re-plan the rest of today" says what it changed |
| `2639f9e` | m340: 12 verified London places |

Batches 1 and 2 are in `before-after-2026-11-24.md` and `before-after-batch2-2026-11-24.md`.

## Files changed in batch 3
- **Brain code:**
  - `brain/src/brain/api.py`, `dayplan.py`, `planner.py` (unchanged in this batch);
  - `reasons.py`, `group.py`, `discovery.py`, `schemas.py`.
- **Brain data:** `brain/data/moments/` (12 new cards, 2 retagged, the Garden at 120's text) and `brain/data/catalogue/london.yaml`, `london_locations.yaml`.
- **Tests:** `test_day_shape.py`, `test_trip_management.py`, `test_group.py`, `test_kept_out.py`, `test_catalogue.py`, `test_destination.py`.
- **iPhone:** `app/Sources/Models.swift`, `AppModel.swift`, `PlanViews.swift`.
- **Android:** `Models.kt`, `AppModel.kt` and `Plan.kt` in `android/app/src/main/java/com/odys/app/`.
- **Docs:**
  - `decisions/decision-log.md` (m339–m345);
  - `decisions/group-trips-architecture.md`, `transparency-review.md`, `day-feel-preference.md`;
  - `decisions/after-9-nov.md` (#104);
  - this folder.

## Checks
- **Brain:** 610 tests passed locally at `4c0ad0e` (Python 3.12). CI passed at `daec99c`.
- **Android:** CI built the app and passed its screen tests at `8682245`, the last Android change: the choices sheet and the rain button.
- **iPhone:** **compiled**, with screenshots. Run 116 at `daec99c` was a manual simulator build on the branch. It cost $0, because the repository is public and GitHub's standard runners are free there. A branch run can't upload. No Swift has changed since.
- **The London gate** (`gate.md`, 3 runs at `4c0ad0e`): **NOT PASSED.**
  - **G2 fails on 12 of 13 days,** because days now keep the person's own number of places.
  - G1 and G3–G8 pass.
  - Travel over budget: 217–228 min. Waits: one, 35 min. Unused time: 1,448–1,491 min.
- **Independent reviews:** 4–6 out of 10 per traveller, and "not yet". See `before-after-batch3-2026-11-24.md`.

## Decisions for Abram
1. **How G2 should measure a day that holds the person's own places** (three options in the before-and-after document). Recommendation: approve the day-feel preference, and for gentle travellers, measure against their own number of places.
2. **The day-feel question in onboarding:** where, and with what wording (`decisions/day-feel-preference.md`).
3. **Group trips step 2** (members, invites, consent, DPIA), if he wants it to start (`decisions/group-trips-architecture.md`).

## Remaining defects
- **Evenings** for lively and night travellers; a market for the friends.
- **Named meals** for more lunches and dinners (verified sources only).
- **Zig-zags:** the family's City to Hyde Park; the friends' Saturday journeys of 35–44 min.
- **Why lines** that compare different kinds of place ("You loved the Uber Boat, and this has history too" for Liberty).
- **G7** checks only strenuous stops, not the travel budget. **G6** doesn't check titles. Both are measured elsewhere now, but the checks could say more (an authorised change to the gate only).
- **Courtauld booking:** its booking note isn't verified.
- **Children's prices** and a family total are missing.

## Next batch (Claude's hours are estimates)
1. **About 15 verified evening and cheap-eat places** where the planner already goes: the Southbank, King's Cross, Brick Lane and Covent Garden (~5 h).
2. **Why lines that never compare unlike places** (~1.5 h).
3. **Abram's G2 decision, applied**, with the gate's own explanation updated (~1 h).
4. **The family total and children's prices** where cards state them (~2 h).
5. **Rerun the gate, the examples and the three reviews** (~1 h).

## Abram's outstanding items (unchanged)
- **Render:** a manual deploy of `c2513fa` for the Seville preview. Auto-Deploy stays off.
- **Database:** remove the IP rule and rotate the password; upgrade by 2 Dec.
- **Android:** delete the `android-latest` pre-release.
- **At release:** fill in the friends' round version lines.
