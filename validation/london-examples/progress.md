# London quality work: where it stands (handover, 25 Nov 2026, end of batch 4)

**Branch:** `claude/pensive-euler-fftd63`, on PR #4. PR #4 merges into the development branch `claude/vigilant-cannon-my82dj`, as every batch has; `main` is the frozen friends' round build (m315).
- Nothing here is on `main`, deployed, uploaded or in the friends' round build.
- It is **not merged** (Abram, 24 Nov).
- **Recorded baseline:** `4c0ad0e`. The batch 3 handover was `dce636a`.

## Batch 4 commits (newest first)
| Commit | What |
|---|---|
| (this handover) | Every stop keeps its reason (a repeat is said differently); m352 logged; gate, examples and before-and-after from `1746408` |
| `1746408` | m352: fixes from three independent reviews (a sunset stop spans the sunset; no "open until" for streets; Somerset House's ice rink; Padella's queue line) |
| `612ce90` | gate (3 runs) and examples from `8f21fde`; the five pace × day-feel combinations tested; logged |
| `8f21fde` | m350–m351: the gate's blockers (G9–G11) and measurements; the QA build path; a script for six moderated sessions |
| `9f3a157` | m349: confirmed defects with regression tests; Day Feel in both apps; the Brain's notes reach the day view |
| `1b376f6` | m346–m348: Day Feel on the trip; G2a–c in place of G2, the original kept; 13 verified places |

## What Abram decided this batch (24 Nov), and what was built
- **Day Feel, Relaxed / Balanced / Full, separate from pace** (m346):
  - stored with the trip and changeable on "Your days" in both apps;
  - extra places follow it, never the pace;
  - **Relaxed keeps the places asked for**, with longer stays;
  - the time left at the end of a day is said as the person's own.
- **G2 replaced by G2a–c, with the original G2 reported every run** (m347).
- **Blockers kept apart from measurements**, with three new blockers, G9–G11 (m350).
- **About 15 verified places:** 13 added (m348). 12 more were checked and not added, with the reasons.
- **A QA build path and a script for six moderated sessions** (m351). Nothing is uploaded: each step is Abram's to approve.

## Checks
- **Brain:** all 622 tests passed locally on the handover commit (Python 3.12). CI passed at `8f21fde` and every earlier batch 4 push. The handover commit's only code change after `1746408` is the reasons rule (every stop keeps one), which doesn't change any plan's stops.
- **Android:** CI built the app and passed every screen test at `9f3a157`, the last Android change. That includes the new rain-swap screen.
- **iPhone:** **compiled with screenshots, run 117 at `9f3a157`** (no Swift since), at $0 on a public repository. It's a manual simulator run on the branch, which can't upload.
- **The London gate** (`gate.md`, 3 runs at `1746408`): **NOT PASSED.** G2b fails 7 times and G11 5 times; G1, G2a, G2c and G3–G10 pass. Travel over budget: 208–218 min (baseline `4c0ad0e` 307–315 by the same script). See `before-after-batch4-2026-11-25.md`.
- **Independent reviews:** 4–7 out of 10 per traveller; "not yet" overall (the sceptical reviewer: 5/10 against a well-informed friend). They're AI reviews of synthetic travellers, not customer evidence.

## Decisions for Abram
1. **The QA build** (`decisions/qa-build-path.md`): a QA Brain with its own database; a separate iPhone app and TestFlight group; a debug APK for his own phone. Each is his call, and the m197 upload guard is a release control.
2. **Moderated sessions** (`validation/human-testing/`): who the six people are, and when. Not friends' round testers.
3. **The gate's next blockers:** backtracking, rain options that need tickets, and reasons a person wouldn't agree with are measured or not checked. Making them blockers changes the gate.
4. **Wording for Abram to check:** the seven why lines rewritten (m349; six were his card 10's), the Day Feel question's three lines, and the free-time sentences.
5. **Still open from batch 3:** group trips step 2.

## Next batch (Claude's hours are estimates)
1. **Routes** (~4 h):
   - walk short links instead of taking the Tube;
   - no boat-then-Tube back;
   - start a boat day eastbound;
   - direct rail where it's quicker. This needs TfL's journey planner (Abram's key) or a walk-or-rail rule.
2. **Loved places across the trip** (~2 h): weigh a loved place across all the trip's days, not only the stretch it first fits.
3. **Meals** (~2 h): no two meals back to back; lunch from 12:00; lunch by the person's own budget.
4. **Evenings** (~4 h): verified pubs, music and late openings, from official sources only.
5. **Reasons** (~1.5 h): never compare unlike places; warnings aren't reasons.
6. **Families** (~2 h): the party total and children's fares, where cards and TfL state them.
7. **Rerun the gate, the examples and three reviews; compare with `1746408`** (~1 h).

## Abram's outstanding items (unchanged)
- **Render:** a manual deploy of `c2513fa` for the Seville preview. Auto-Deploy stays off.
- **Database:** remove the IP rule and rotate the password; upgrade by 2 Dec.
- **Android:** delete the `android-latest` pre-release.
- **At release:** fill in the friends' round version lines.
