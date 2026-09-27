# Phase 3 — Validation

Will strangers finish the onboarding, prefer a plan built from it, use it, and pay? Decisions D1–D4, D16, D18, D19, D21, D23–D26, D30–D35 and D50–D57 apply.

**D50–D64 in short:**
- v0 is an iOS app.
- **Tests A–C still run by hand (D63)**: Test A as a chat, and the B/C plans as messages or PDFs.
- **Checkpoint 3 is in the week of 9 Nov.**
- The app is built in parallel, and its first external TestFlight build comes after the checkpoint (`decisions/v0-ios-plan.md`).

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
| `shot-card-example.md` | The Test A example shot card, built from seed moment 1 (gaps to fill on one walk) |
| `results-sheet.xlsx` | Where every result goes; the Summary tab scores against the thresholds, split by voice and text (D18) |
| `results.md` | *Checkpoint 3, written after the tests* |

## Order (D36, changed by D86)

1. **Tests A–D**, by hand. **Recruitment starts in the week of 12 Oct**, a week earlier than before (D86), and the Test A chats run from the first sign-ups to 26 Oct.
2. **Test E after v0 exists (D86):** 5 B2B discovery interviews (3 London, 2 Uzbek) **with a working demo**, after Test B and before any B2B-specific build work. Then the decision note, B2B-first vs consumer-first (`decisions/b2b-vs-consumer-first.md`, D40). **Until then, "businesses will pay" is an explicit, untested assumption: the main revenue risk.**

Detail for step 1: **Test B goes first and fast (D68):** each person's two plans are sent 1–3 days after their Test A chat, written by the Brain from the results sheet (D65). Test B reports about the week of 2 Nov, and that decides whether the iOS app code starts. **Checkpoint 3 in the week of 9 Nov.**

## Flow per participant (12 strangers target, 14 recruited)

**Friends and family** are a separate launch channel (D43): tagged, reported separately, and never counted in thresholds or K.

1. **Recruit** (Post 1 or the weekend-trip invitation).
2. **Consent.**
3. **Test A:** onboarding chat on WhatsApp Business (a separate number, D66), voice notes or text. 20–30 min, can be spread over a day. Enter their swipes and choices in the results sheet the same day.
4. **Test B (1–3 days later):** two plans, A/B blind, written by `brain.testb`, checked by you, and sent as WhatsApp messages or PDFs. Pick one, rate both.
5. **Test C:** use the plan on a real day. Rate each stop, bring a friend, get a share prompt at the shot-card moment. Follow up for 2 weeks.

**Test D runs separately:** its own post and its own visitors. Study participants are tagged and excluded from Test D rates.

## Before the first participant (checklist)

- [ ] Abram confirms the conjoint attributes (`conjoint/README.md`) and the 16 swipe items (`interview-script.md` §3).
- [ ] Seed moment 1 is in (`research/seed-moments/01-tube-to-museum.md`). **Fill its gaps on one walk** (exit, route, best time, shot position), take a photo from the spot, and complete `shot-card-example.md` (≈ 0.5 h).
- [ ] ICO data protection fee: do the self-assessment (search: £52/year for tier 1). Pay if required before collecting data.
- [ ] **WhatsApp Business on a separate number (D66)**, on a personal phone, never the work one (CLAUDE.md). **The number is ready (2026-09-26); you'll share it when it's needed.** Still to do:
  - Set a greeting message and an away message: "I reply within a few hours; in an emergency call 999".
  - Save the script's prompts as quick replies, and use labels for each person's stage (A done, plans sent, day done). WhatsApp lists all four as Business app features.
  - Check the chat-backup setting, so voice notes you delete after transcribing aren't kept in a backup.
- [ ] Set up the Tally form (asking for the WhatsApp number) and GoatCounter (`test-d-landing/README.md`).
- [x] **Swipe calibration page (D70):** deployed with the Render Blueprint on 27 Sep (Frankfurt, £0, no card), tried and shared.
  - [ ] Pick the 16 in the week of 12 Oct, before the recruitment posts go out (D86).
  - [ ] **Download both CSVs again by Fri 23 Oct.** The free database expires about 26 Oct. Then suspend or delete the service and database in Render.
- [ ] Safety during Test C: participants message you directly (consent form); you reply within a few hours (D46).
- [ ] Put a contact email in the consent form, privacy notice and landing page.
- [ ] Copy `results-sheet.xlsx` to `validation/raw/results.xlsx` and fill in the copy. `validation/raw/` is git-ignored, and the template in the repo stays empty. **Never commit participant data.** Participant IDs P01–P20 and the Test B A/B labels are pre-filled.

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
