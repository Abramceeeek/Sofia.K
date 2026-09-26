# Phase 3 — Validation

Will strangers finish the onboarding, prefer a plan built from it, use it, and pay? Decisions D1–D4, D16, D18, D19, D21, D23–D26, D30–D35 and D50–D57 apply.

**Changed by D50–D51:**
- Tests A–C now run **inside the v0 iPhone app through TestFlight**, not on Telegram.
- The Brain is being built now, and about 40.5 h of the app is built before Checkpoint 3 (`decisions/v0-ios-plan.md`).
- Test D (web page) and Test E (interviews) are unchanged.

## Files

| File | What it is |
|---|---|
| `test-plan.md` | Tests A–D, virality (K), pass thresholds, analysis plan, risks |
| `recruitment-posts.md` | Separate posts for Tests A–C and Test D, the weekend-attendee invitation, and a post tracking table (D21) |
| `interview-script.md` | The Test A wording. **The app now asks these questions itself** (`brain/data/onboarding.yaml`); the script is kept as the source of the copy |
| `consent-form.md` | Plain-English consent. **Telegram version: rewrite for the app before the first external TestFlight build** |
| `privacy-notice.md` | UK GDPR notice for the study and the Test D waitlist. **Telegram version: rewrite for the app** (with `test-d-landing/privacy.html`) |
| `conjoint/` | The 10 "this or that" tasks (`design.csv`) and the script that makes them |
| `test-d-landing/` | Test D landing page (static HTML): random arm A £4.99/£49.99 or arm B £9.99/£99.99, waitlist only (D25, D31) |
| `discovery-interviews.md` | Test E (runs first): 5 B2B discovery interviews (3 London, 2 Uzbek) and 3 optional venue conversations (D34, D36) |
| `shot-card-example.md` | The Test A example shot card, built from seed moment 1 (gaps to fill on one walk) |
| `results-sheet.xlsx` | Where every result goes; the Summary tab scores against the thresholds, split by voice and text (D18) |
| `results.md` | *Checkpoint 3, written after the tests* |

## Order (D36)

1. **Test E first:** 5 B2B discovery interviews (3 London, 2 Uzbek) in the weeks of 5 and 12 Oct.
2. **Decision note:** B2B-first vs consumer-first (`decisions/b2b-vs-consumer-first.md`, D40).
3. **Test D** (web) whenever convenient. **Tests A–C through TestFlight:** Test A from about the week of 23 Nov, Test B about the week of 7 Dec, then Test C for 2 weeks. **Checkpoint 3 about the week of 4 Jan.**

## Flow per participant (12 strangers target, 14 recruited)

**Friends and family** are a separate launch channel (D43): tagged, reported separately, and never counted in thresholds or K.

1. **Recruit** (Post 1 or the weekend-trip invitation). An iPhone is needed. The sign-up form gives each person a **tester code**.
2. **Install** through the TestFlight public link, then enter the tester code. **Consent** in the app, including a separate AI permission.
3. **Test A:** self-serve onboarding in the app, typed or dictated.
4. **Test B:** two plans, A/B blind, in the app. Pick one, rate both.
5. **Test C:** use the plan on a real day. Rate each stop from a notification, bring a friend, get a share prompt at the shot-card moment. The "Plan another day" button logs second-plan requests for 2 weeks.

**Test D runs separately:** its own post and its own visitors. Study participants are tagged and excluded from Test D rates.

## Before the first participant (checklist)

- [ ] Abram confirms the conjoint attributes (`conjoint/README.md`) and the 16 swipe items (`interview-script.md` §3).
- [ ] Seed moment 1 is in (`research/seed-moments/01-tube-to-museum.md`). **Fill its gaps on one walk** (exit, route, best time, shot position), take a photo from the spot, and complete `shot-card-example.md` (≈ 0.5 h).
- [ ] ICO data protection fee: do the self-assessment (search: £52/year for tier 1). Pay if required before collecting data.
- [ ] **Apple:** outside-activities check (D53, proposed before external TestFlight); developer enrolment (individual or organisation, an open question); the TestFlight external group and public link; the first build through App Review.
- [ ] **Rewrite for the app** (Claude drafts, ≈ 1 h review): the consent form, privacy notice, `test-d-landing/privacy.html`, Post 1 and a one-page tester guide.
- [ ] **The backup helper** has signed the contributors agreement before the first external build (D55). Set up the safety alert channel (`BRAIN_ALERT_WEBHOOK_URL`).
- [ ] Set up the Tally form (with tester codes) and GoatCounter (`test-d-landing/README.md`).
- [ ] Put a contact email in the consent form, privacy notice and landing page.
- [ ] Copy `results-sheet.xlsx` to `validation/raw/results.xlsx` and fill in the copy. `validation/raw/` is git-ignored, and the template in the repo stays empty. **Never commit participant data.** Participant IDs P01–P20 and the Test B A/B labels are pre-filled.

## Founder hours (budget 15; running the tests only, the app build is in Phase 4)

| Step | Est. (h) |
|---|---|
| Confirm conjoint and swipe items (1.0) + rewrite the materials for the app (1.0) | 2.0 |
| Landing page, form and analytics set-up (Claude writes the code) | 1.0 |
| Recruitment: posts, replies, scheduling (log minutes per post) | 2.0 |
| Test A: tester support (install help, stuck testers); the app runs the onboarding | 1.0 |
| Read-back checks | 0.5 |
| Test B: generic plan once (0.5) + 12 personalised plans (the planner drafts, you edit and push) | 3.0 |
| Test C: follow-ups (ratings arrive in the app) | 1.0 |
| Analysis and `results.md` from the brain's export | 1.5 |
| **Tests A–D total** (D50) | **≈ 12** |
| Test E: 5 B2B discovery interviews, including recruiting and an Uzbek script check (D34, D36) | 5.25 |
| Decision note: B2B-first vs consumer-first (D40) | 1.0 |
| Seed moment walk and shot card | 0.5 |
| **Phase 3 total** | **≈ 18.75** (was ≈ 23.75 on Telegram) |
| *Optional:* 3 venue conversations | *+2.0* |

Running Tests A–C in the app saves about 5 h of chats, transcripts and follow-ups. The cost moves into the Phase 4 build: about 40.5 h of it happens before Checkpoint 3 (`decisions/v0-ios-plan.md`).
