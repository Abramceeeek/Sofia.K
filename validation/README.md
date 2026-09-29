# Phase 3 — Validation

> **D109 (29 Sep): app first.** No posting or advertising until the app is ready. Tests A–C will run **inside the app**, through TestFlight: Abram's iPhone (~7 Oct), then friends (16–25 Oct), then strangers (from ~27 Oct). Test B reports ~13 Nov; **Checkpoint 3 is in the week of 23 Nov.** The hand-run WhatsApp materials below are paused and kept as a fallback. Plan and gates: `decisions/v0-ios-plan.md` (D109 block).

Will strangers finish the onboarding, prefer a plan built from it, use it, and pay? Decisions D1–D4, D16, D18, D19, D21, D23–D26, D30–D35 and D50–D57 apply.

**D50–D64 in short:**
- v0 is an iOS app.
- **Tests A–C still run by hand (D63)**: Test A as a chat, and the B/C plans as messages or PDFs.
- **Checkpoint 3 is in the week of 2 Nov** (D106; was 9 Nov).
- **The app is built now, in parallel with the tests (D107)**, and its first external TestFlight build comes after the checkpoint, about the week of 9 Nov (`decisions/v0-ios-plan.md`).

## Files

| File | What it is |
|---|---|
| `test-plan.md` | Tests A–D, virality (K), pass thresholds, analysis plan, risks |
| `recruitment-posts.md` | Separate posts for Tests A–C and Test D, the weekend-attendee invitation, and a post tracking table (D21) |
| `interview-script.md` | Word-for-word host script for Test A (Wizard of Oz in a chat), then Tests B and C. The app reuses its wording (`brain/data/onboarding.yaml`) |
| `consent-form.md` | Plain-English consent for the hand-run tests. A version for the app is needed before the first external TestFlight build |
| `privacy-notice.md` | UK GDPR notice for the study and the Test D waitlist. A version for the app is needed later |
| `conjoint/` | The 10 "this or that" tasks (`design.csv`) and the script that makes them |
| `test-d-landing/` | Test D landing page (static HTML): random arm A £4.99/£49.99 or arm B £9.99/£99.99, waitlist only (D25, D31) |
| `discovery-interviews.md` | Test E, **postponed until v0 exists (D86)**: 5 B2B discovery interviews (3 London, 2 Uzbek) and 3 optional venue conversations (D34, D36) |
| `test-e-kit.md` | Test E in shareable form (D70), **postponed with Test E (D86)**: a 30-min call guide, a two-message version agencies answer in writing (English, Russian, Uzbek), and the hotel budget-holder intro line. Published with copy buttons: https://claude.ai/artifact/LZQEYVFmjWUXXpVMLx7qu8 |
| `shot-card-example.md` | The Test A example shot card: Waterloo Bridge at sunset, text only (D106) |
| `study-info.pdf`, `make_study_pdf.py` | The consent form and privacy notice as one PDF, sent with the first message after sign-up. The script also writes the public `test-d-landing/privacy.html`, without the WhatsApp number (D106) |
| `testb-real/` | The real Test B brief and generic plan (tracked copy; the working copy is `raw/testb/`, D106) |
| `results-sheet.xlsx` | Where every result goes; the Summary tab scores against the thresholds, split by voice and text (D18) |
| `results.md` | *Checkpoint 3, written after the tests* |

## Order (D36, changed by D86)

1. **Tests A–C**, by hand. **Recruitment starts now (D105)**, once the four items in `recruit-now.md` are done (D107). Test A chats run from the first sign-ups to about mid-October. **Test D runs after Test B reports (D107).**
2. **Test E after v0 exists (D86):** 5 B2B discovery interviews (3 London, 2 Uzbek) **with a working demo**, after Test B and before any B2B-specific build work. Then the decision note, B2B-first vs consumer-first (`decisions/b2b-vs-consumer-first.md`, D40). **Until then, "businesses will pay" is an explicit, untested assumption: the main revenue risk.**

Detail for step 1: **Test B goes first and fast (D68):** each person's two plans are sent 1–3 days after their Test A chat, written by the Brain from the results sheet (D65). Test B reports around 23 Oct (D106; was the week of 2 Nov), and that decides whether the iOS app code starts. **Checkpoint 3 in the week of 2 Nov** (D106).

## Flow per participant (12 strangers target, 14 recruited)

**Friends and family** are a separate launch channel (D43): tagged, reported separately, and never counted in thresholds or K.

1. **Recruit** (Post 1 or the weekend-trip invitation).
2. **Consent.**
3. **Test A:** onboarding chat on WhatsApp Business (a separate number, D66), voice notes or text. 20–30 min, can be spread over a day. Enter their swipes and choices in the results sheet the same day.
4. **Test B (1–3 days later):** two plans, A/B blind, written by `brain.testb`, checked by you, and sent as WhatsApp messages or PDFs. Pick one, rate both.
5. **Test C:** use the plan on a real day. Rate each stop, bring a friend, get a share prompt at the shot-card moment. Follow up for 2 weeks.

**Test D runs separately:** its own post and its own visitors. Study participants are tagged and excluded from Test D rates.

## Before the first participant (checklist, lean mode D107)

The short version is `recruit-now.md`. Only what's needed to run the stranger tests legally and safely:

- [x] Conjoint attributes confirmed (28 Sep, with the 3-level weather factor, D95).
- [x] **The 16 swipe places: locked 28 Sep (D107)**, the provisional list, without waiting for the swipe page.
- [x] Consent form and privacy notice filled in (D106), sent as `study-info.pdf` with the first reply.
- [x] Example shot card: Waterloo Bridge at sunset, text only (D106).
- [x] Real brief and generic plan copied (`testb-real/`, `raw/testb/`, D106).
- [ ] ICO data protection fee: **the fee checker said not required yet (29 Sep, D108).** Re-check, and pay if required, before spreading to strangers, which starts with Post 1.
- [x] **WhatsApp basics** on the study number: greeting and away messages with the 999 line, chat backup off, a test message. **Done 29 Sep.**
- [x] Claude's Model Improvement setting off. **Done 29 Sep.**
- [x] Abram reads the generic plan once. **Done 29 Sep: fine.**
- [ ] Copy `results-sheet.xlsx` to `validation/raw/results.xlsx` and fill in the copy. `validation/raw/` is git-ignored, and the template in the repo stays empty. **Never commit participant data.**
- [ ] Safety during Test C: participants message the study number; you reply within a few hours (D46).

**Deferred by D107:** the Tally sign-up form (sign-ups come by click-to-chat), the Test D landing page (after Test B), WhatsApp quick replies and labels, the full materials review, the Area 18 review, and the South Kensington walk. The swipe page's results are no longer waited for; downloading them before 23 Oct is optional.

## Founder hours (budget 15)

| Step | Est. (h) |
|---|---|
| Review materials; confirm conjoint and swipe items | 2.0 |
| Landing page, form and analytics set-up (Claude writes the code) | 1.0 |
| Recruitment: posts, replies, scheduling (log minutes per post) | 2.0 |
| Test A: run 12 chats (≈20 min of your time each, asynchronous) | 4.0 |
| Transcripts and read-back check (local transcription; Claude drafts the extraction) | 1.0 |
| Test B: generic plan once (0.5) + 12 personalised plans (≈15 min each: `brain.testb` writes them, you check and send) | 3.5 |
| Moments for Test B: pick ~25 and check Claude's drafted cards (pulled forward from Phase 4, D65; +1.0, D86) | 4.5 |
| Moment cards from friends' suggestions (D86) | 1.25 |
| Test B dry run (1.0) and a Test B buffer for a second recruitment round, spent only if needed (3.0) (D86) | 4.0 |
| Test C: follow-ups over 2 weeks and data entry | 2.0 |
| Analysis and `results.md` with Claude | 1.5 |
| **Tests A–D total** (accepted, D30; by hand, D63; + moments for Test B, D65; + D86) | **≈ 26.75** |
| ~~Test E (5.25) and the decision note (1.0)~~ | **After v0 exists (D86)**, outside Phase 3 |
| Seed moment walk and shot card | 0.5 |
| **Phase 3 total** | **≈ 27.25** (the extra 3.5 h comes out of Phase 4, so the plan total is unchanged). `LOG.md` shows ≈ 28.25 because it adds the swipe page (0.75) and the aspiration question (0.25) |
| *Optional:* 3 venue conversations | *+2.0* |

Running Tests A–C in the app would have saved about 5 h, but it would have needed about 40 h of the app built before Checkpoint 3. D63 keeps the tests by hand and the checkpoint in November.
