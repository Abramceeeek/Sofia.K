# London quality work: where it stands (handover, 25 Nov 2026, end of batch 5)

**Branch:** `claude/pensive-euler-fftd63`, on PR #4. PR #4 merges into the development branch `claude/vigilant-cannon-my82dj`; `main` is the frozen friends' round build.
- **Not merged, not deployed, nothing uploaded.** London is held (Abram, 25 Nov).
- **The product commit for every result below is `d6c6ab6`.** The handover commit after it changes only documents.

## Batch 5 commits
| Commit | What |
|---|---|
| (this handover) | Documents only: the gate, examples and reviews of `d6c6ab6`, the before-and-after, this file |
| `d6c6ab6` | m353–m354 logged: **the verified product commit** |
| `73383ab` | m354: meals two hours apart, reasons that link only like places, rain options disclosed, changes explained, children's prices, group privacy |
| `9810781` | m353: Abram's data decisions; routes (walk short links, never back over a ride's course, no crossing back); G12, G3b |

## Checks, all at `d6c6ab6`
- **Brain:** 628 tests passed.
- **London gate** (3 runs, identical): **NOT PASSED.**
  - G2b fails 6 times and G11 5 times.
  - G1, G2a, G2c, G3, G3b and G4–G10 pass, and so do the new G12, G13 and G14.
  - Baseline `977ccfd` by the same script: G12 4, G13 28, G14 8, G2b 7, G11 5.
- **Android:** run 56 built the app and passed every screen test.
- **iPhone:** run 118 compiled with screenshots at `d6c6ab6`. It was a manual simulator run with upload off, at $0 on a public repository.
- **Brain CI:** green at `d6c6ab6` and on the handover commit.
- **Reviews:** 3–7/10 per traveller; 5/10 against a well-informed friend; "not yet" (the families reviewer: "nearly"). See `before-after-batch5-2026-11-25.md`.

## Decisions for Abram
1. **Is a traveller's budget per person or for the whole party?** The family's £34.90 a person is £139.60 for four against a £20–40 band.
2. **G11:** count pleasant walking apart from Tube and bus time (Jonas's 83 min is mostly walking).
3. **The eight rewritten why lines** (`decisions/why-lines-for-abram.md`): accept or reword each.
4. **Unchanged from batch 4:**
   - the QA build steps (`decisions/qa-build-path.md`);
   - who the six moderated-session participants are (`validation/human-testing/`).

## Next batch, in order (Claude's hours are estimates)
1. **The two false statements the reviews found** (~1 h), with G13 checks:
   - a paid rain option claiming it fits the budget, with fares left out;
   - "open until" giving the traveller's end time instead of the place's.
2. **Routes** (~3 h):
   - returns over shorter distances;
   - an eastbound boat card, verified, so a Greenwich day goes out by boat;
   - route efficiency measured.
3. **Reasons** (~1.5 h): a strong feature on both sides; "one of your interests" names the interest.
4. **Meals** (~1.5 h): lunch from about 12:00; three hours between food stops; an evening for the lively.
5. **Families** (~2 h): per Abram's budget decision; children's fares once TfL's page is read; the way back.
6. **Filler** (~1 h): repetition across travellers, as a warning with a target.
7. **One-commit verification again** (~1.5 h): tests, gate, examples, three reviews, both apps.

## Abram's outstanding items (unchanged)
- **Render:** a manual deploy of `c2513fa` for the Seville preview. Auto-Deploy stays off.
- **Database:** remove the IP rule and rotate the password; upgrade by 2 Dec.
- **Android:** delete the `android-latest` pre-release.
- **At release:** fill in the friends' round version lines.
