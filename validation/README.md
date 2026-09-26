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
| `discovery-interviews.md` | Test E (runs first): 5 B2B discovery interviews (3 London, 2 Uzbek) and 3 optional venue conversations (D34, D36) |
| `shot-card-example.md` | The Test A example shot card, built from seed moment 1 (gaps to fill on one walk) |
| `results-sheet.xlsx` | Where every result goes; the Summary tab scores against the thresholds, split by voice and text (D18) |
| `results.md` | *Checkpoint 3, written after the tests* |

## Order (D36)

1. **Test E first:** 5 B2B discovery interviews (3 London, 2 Uzbek) in the weeks of 5 and 12 Oct.
2. **Decision note:** B2B-first vs consumer-first (`decisions/b2b-vs-consumer-first.md`, D40).
3. **Then Tests A–D**, by hand, from the week of 19 Oct. **Checkpoint 3 in the week of 9 Nov.**

## Flow per participant (12 strangers target, 14 recruited)

**Friends and family** are a separate launch channel (D43): tagged, reported separately, and never counted in thresholds or K.

1. **Recruit** (Post 1 or the weekend-trip invitation).
2. **Consent.**
3. **Test A:** onboarding chat, voice notes or text. 20–30 min, can be spread over a day.
4. **Test B:** two plans, A/B blind, as messages or PDFs. Pick one, rate both.
5. **Test C:** use the plan on a real day. Rate each stop, bring a friend, get a share prompt at the shot-card moment. Follow up for 2 weeks.

**Test D runs separately:** its own post and its own visitors. Study participants are tagged and excluded from Test D rates.

## Before the first participant (checklist)

- [ ] Abram confirms the conjoint attributes (`conjoint/README.md`) and the 16 swipe items (`interview-script.md` §3).
- [ ] Seed moment 1 is in (`research/seed-moments/01-tube-to-museum.md`). **Fill its gaps on one walk** (exit, route, best time, shot position), take a photo from the spot, and complete `shot-card-example.md` (≈ 0.5 h).
- [ ] ICO data protection fee: do the self-assessment (search: £52/year for tier 1). Pay if required before collecting data.
- [ ] Choose the chat app for Test A (the materials assume Telegram; a separate account is cleaner). Set up the Tally form and GoatCounter (`test-d-landing/README.md`).
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
| Test B: generic plan once (0.5) + 12 personalised plans (≈15 min each; the planner or an LLM drafts) | 3.5 |
| Test C: follow-ups over 2 weeks and data entry | 2.0 |
| Analysis and `results.md` with Claude | 1.5 |
| **Tests A–D total** (accepted, D30; by hand, D63) | **≈ 17** |
| Test E: 5 B2B discovery interviews, including recruiting and an Uzbek script check (D34, D36) | 5.25 |
| Decision note: B2B-first vs consumer-first (D40) | 1.0 |
| Seed moment walk and shot card | 0.5 |
| **Phase 3 total** | **≈ 23.75** |
| *Optional:* 3 venue conversations | *+2.0* |

Running Tests A–C in the app would have saved about 5 h, but it would have needed about 40 h of the app built before Checkpoint 3. D63 keeps the tests by hand and the checkpoint in November.
