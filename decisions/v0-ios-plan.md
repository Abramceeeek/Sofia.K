# v0 as a native iOS app: plan, hours, cuts and Phase 3 through TestFlight (D50–D54)

*Written 2026-09-26. All founder-hour figures are estimates (GUESS) that assume Claude Code writes most of the code. Apple facts come from Apple's own pages, fetched on 2026-09-26 (sources at the end).*

## Decision

- **v0 is a native iOS app (SwiftUI).** Testers get it through **TestFlight**, and it goes on the **App Store** only after it passes Phase 5 **and** the new Apple gate clears (D53). **This replaces the Telegram bot plan.**
- **The system has two parts:**
  - **Brain:** a FastAPI backend holding the moment database, the scoring (hierarchical βs, with δ_person kept separate so it can move onto the phone later) and the OR-Tools planner.
  - **Face:** the SwiftUI app. It covers onboarding (text first, voice optional), moment and shot cards, the day plan with a map, and one-tap ratings.
- **The brain is started.** A working first version was drafted on 2026-09-26 and is in `brain/`, with 28 passing tests. It runs in parallel with Test E, because it does not depend on test results.
- **Hours:**

  | Version | Founder hours |
  |---|---|
  | Telegram v0 | 47 |
  | iOS v0, like-for-like | ≈ 62.5 |
  | **iOS v0, left now** (after the brain draft and the cuts below) | **≈ 53.5** |

  The app itself is the big new cost: about 31 h, against 10 h for the bot.
- **Phase 3 through TestFlight:**
  - Tests A–C run inside the app.
  - About 40.5 h of the v0 build therefore happens **before** Checkpoint 3.
  - Test running gets cheaper: Phase 3 falls from 23.75 to ≈ 18.75 h.
  - **Checkpoint 3 moves from the week of 9 Nov to about the week of 4 Jan.**
  - v0 then needs only ≈ 13 h after the checkpoint, so the whole plan ends about 3 weeks later than the Telegram plan.
- **Plan total:** ≈ 109.5 h, or ≈ 106.5 h with the workbook reviews paused (D52). That is 14.2 weeks at 7.5 h, **about 1.5 h past the 14-week window.**

## The split

| | Brain (FastAPI, Python 3.12) | Face (SwiftUI, iOS 17+) |
|---|---|---|
| Owns | Moment database, population weights, each person's δ, the planner, ratings, the safety alert, data deletion | Screens, local notifications, map, share sheet, keyboard dictation |
| Where the maths runs | Server in v0. `brain/src/brain/personal.py` is numpy-only and stateless, so the same update can run on the phone later (Area 17, 8–12 h, after v0) | Nothing in v0 |
| Where it's built | Here, by Claude Code in the cloud (tests run here) | **On your personal Mac with Xcode.** Claude Code needs to run locally there, because SwiftUI can't be compiled in this Linux container |
| Built so far | Schema and loader, seed moment 1 (draft), priors file, scoring with thresholds and interactions, δ update (Laplace), planner (time windows, transfer thresholds, peak–end toggle off), 22 API endpoints, 28 tests | Nothing |

**iOS 17+** because the SwiftUI `Map`/`Marker` API starts at iOS 17.0 (Apple docs).

## Build hours: iOS vs Telegram

| Block | Telegram v0 (D44, D45) | iOS v0, like-for-like | iOS v0, left now |
|---|---|---|---|
| **Face:** Telegram bot flow and transcription, or the SwiftUI app (below) | 10 | 31 | 31 |
| Onboarding back end: extraction of the open answer, read-back lines, gold-set check | 3 | 3 | 3 |
| AI support agent | 6 | 0 (cut: Help & safety screen) | 0 |
| Safety alert to a person (D46) | in support | 1 | 0.5 (built; set up the webhook) |
| Moment database: seed session, 45 LLM-drafted cards and review, ~20 shot cards, swipe set | 5 | 5 | 5 |
| Planner: OR-Tools model, travel matrices, weather rules, tests, LLM explanation | 11 | 11 | 7 (model, toggle and tests drafted) |
| Weights and scoring: per-user posterior, scoring, population refit | 6 | 5 (full HB refit after v0) | 2.5 (posterior drafted; pooled refit from Phase 3 data 1 h) |
| Ratings and events logging | 2 | 1 | 0.5 (built) |
| Privacy: deletion, notice, AI permission (no audio to delete) | 2 | 1.5 | 1.5 |
| Design hooks: separate δ, trip intent stored per plan (D27) | 2 | 2 | 0.5 (built) |
| Hosting: Render + Postgres, secrets, migrations | not in the estimate | 2 | 2 |
| **Total** | **47** | **62.5** | **53.5** |

**The Face, 31 h:**

| Part | Hours |
|---|---|
| Apple set-up: developer account, signing, App Store Connect record, first TestFlight upload | 3 |
| Designer: brief, two review rounds, handoff (the designer's own hours are not counted) | 3 |
| Onboarding screens (consent, best hour, why travel, 16 swipes, 10 "this or that", about you, photos, read-back) | 7 |
| Moment card and shot card | 2.5 |
| Plans: two-plan choice (Test B), day plan list and map | 4 |
| One-tap rating and local notifications | 2.5 |
| Settings, delete my data, Help & safety | 1.5 |
| Networking, models and error states | 2.5 |
| "Bring a friend" share | 0.5 |
| TestFlight external group, tester notes, App Privacy details | 1.5 |
| Device testing and fixes | 3 |

- **Risk:** if you haven't shipped an iOS app before, add about 30% to the Face (≈ 9 h, GUESS). Signing and provisioning are the usual time sinks.
- **Also needed:** a personal Mac with Xcode (CLAUDE.md: personal devices only), and the Apple Developer Program at **US$99 a year**, charged in local currency at enrolment.

## What to cut to keep v0 small

| Cut from v0 | Instead | Saves (h) |
|---|---|---|
| AI support agent | A Help & safety screen: safety goes to a person (D46), everything else to email | 6 |
| Content automation | After v0 (D45) | 5 |
| An admin app | FastAPI's built-in `/docs` page, plus YAML files for moments | ~3 |
| A custom voice recorder | Keyboard dictation (the iPhone keyboard's mic). Test A asks "Did you type or speak?" | ~2.5 |
| A push-notification server | Local notifications scheduled from the plan's stop times | ~2 |
| Accounts and login | An anonymous install token, plus "Delete my data" in the app | ~2 |
| In-app routing | Pins on the map; "Directions" opens Apple Maps | ~2 |
| Offline mode | Cache the current plan only | ~1.5 |
| Full hierarchical refit (PyMC) | A pooled logit from Phase 3 data; HB after v0, when there is enough data | ~1 |
| iPad, landscape, widgets, Live Activities, Watch, localisation | iPhone, portrait, English | not estimated |
| Payments or in-app purchase | None in v0 (money gates). Test D stays a web page | — |
| On-device δ | Later (Area 17), once the app exists | 8–12 later |

- **Custom voice button:** add it back if you want Test A's voice-vs-text split (D4, D18) *measured* rather than self-reported: +2.5 h. It would use on-device recognition, so audio never leaves the phone (`requiresOnDeviceRecognition`, iOS 13+; `SpeechAnalyzer` on iOS 26).

## Phase 3 through TestFlight

**How TestFlight works (Apple):**
- Up to **10,000 external testers**, invited by email or a **public link** with tester criteria (device, OS).
- Internal testers are **only App Store Connect users** (up to 100). **Strangers are therefore external testers.**
- **The first build for external testers goes through App Review.**
- Each build lasts **90 days**.
- Guideline 2.2: TestFlight apps "should be intended for public distribution" and **testers can't be given "compensation of any kind"**. A free day plan is the product itself, so it is fine; vouchers are not.

**Test by test:**

| Test | Telegram plan | Through TestFlight |
|---|---|---|
| **A** onboarding | Abram chats by hand (≈ 4 h) | **Self-serve in the app.** The events give completion, time and drop-off screen. The read-back shows the brain's confident weights ("You avoid long transfers") and asks "Right? / Not quite" for each line. The survey is in the app |
| **B** plan quality | LLM-drafted text plans | **Two plans, A and B, in the app.** The planner drafts the personal plan and Abram edits it. Both plans are pushed with `POST /v1/admin/users/{id}/plans` (Wizard of Oz), and labels come from the pre-randomised list. The tester picks one, gives each a "This plan fits me" 1–5, and says why |
| **C** real use | Numbers sent by message | **Local notifications after each stop:** a 1–5 rating plus "Would you bring someone here?", saved with conditions. A **"Plan another day"** button records unprompted second-plan requests (≥ 30% threshold) |
| **D** willingness to pay | Web landing page | **Unchanged**: a web page, open to Android users too. The copy says "iPhone app in testing" |
| **E** B2B | Interviews | **Unchanged** |
| K (virality) | Referral links in messages | **Share button** with a `ref` code that goes to the landing page, then on to the TestFlight link |

**Other changes:**
- **Launch channel (D43):** every tester gets a **tester code** from the sign-up form, for example `S-fbucl-07` for strangers or `F-03` for friends and family. The app asks for it on the welcome screen and sends the channel and source to the brain. Thresholds and K stay strangers only.
- **iPhone only:** iOS was **51.5%** of UK mobile web traffic in August 2026 (StatCounter). Expect about half the sign-ups per post for Tests A–C, so Post 1 says "iPhone needed". Test D is unaffected.
- **Materials to rewrite before the first external build** (Claude drafts, ≈ 1 h of your review): the consent form and privacy notice (server storage, **separate AI permission**, no audio), Post 1, a one-page tester guide, and the Test D privacy page. The host script becomes app copy (`brain/data/onboarding.yaml`).
- **Thresholds are unchanged** (D2, D18). Test A now tests the real onboarding rather than a concierge chat, which is a harder and more honest test.

**Phase 3 founder hours: ≈ 18.75 (was 23.75):**

| Item | Hours |
|---|---|
| Unchanged items: conjoint and places 1, seed walk 0.5, Test E 5.25, decision note 1, landing page 1, recruitment 2, analysis 1.5 | 12.25 |
| Materials rewrite for TestFlight | 1 |
| Test A tester support (was 4 h of chats) | 1 |
| Read-back checks (was 1 h of transcripts) | 0.5 |
| Test B plans (planner drafts, Abram edits) | 3 |
| Test C follow-ups (ratings arrive in the app) | 1 |

**What moves before Checkpoint 3 (≈ 40.5 h of the 53.5):**
- **For Test A (≈ 28 h):**
  - Apple set-up, designer, the onboarding screens, settings and safety, networking, TestFlight;
  - hosting, privacy and AI permission, safety alert, events, weights review;
  - **the 16 swipe moments with photos.** Photos are yours or Wikimedia Commons with credit (Area 19 rule).
- **For Tests B and C (≈ 12.5 h):** plan and map screens, rating and notifications, moment and shot cards, share, and the remaining moment records.
- **After Checkpoint 3 (≈ 13 h):** planner matrices, weather and explanation (7); LLM extraction for consented users (3); pooled refit (1); shot-card polish and device testing (2).

**Risk:** if Phase 3 fails, most of those ~40.5 h are spent before the gate. The brain was your call regardless. The onboarding screens are the part a failed Test A would change most.

## Schedule (7.5 h a week)

| Week of | Plan |
|---|---|
| 28 Sep | Areas 1–3 review 5; seed moments and walk 1; conjoint and places 1 (D48); **Apple outside-activities check 0.5** (see Gates) |
| 5 Oct | Areas 5–12 reviews 5.5; Test E recruiting 1.25; Areas 18 and 20 0.75 |
| 12 Oct | Test E interviews 4; decision note 1. **The Test A build starts:** brain code review 1, designer brief and contributors agreement 1.5 |
| 19 Oct – 16 Nov | The rest of the Test A build (≈ 25.5 h of its 28). In the week of 2 Nov: the Area 4 review 2 (D56) and the Areas 13–17 and 19 review 3 |
| 16 Nov | First external build to App Review; materials rewrite 1; recruitment 2; landing page 1; the build for B and C starts |
| 23 Nov | **Test A runs.** Build for B and C (≈ 12.5 h in all, done by the week of 30 Nov) |
| 7 Dec | **Test B.** Then **Test C** for 2 weeks (over Christmas: expect slower replies) |
| ~4 Jan | Analysis and **Checkpoint 3** |
| Jan | The rest of v0 (≈ 13 h), then Phase 5 (10 h) |

**Fallback if the slip matters more than testing the real app:** run Tests A–C by hand as before, over iMessage or WhatsApp with no build, and keep TestFlight for Phase 5. Checkpoint 3 then stays in November.

## Gates

- **New (D53): before public App Store release,** check Apple's outside-activities policy for publishing under your own developer account.
- **Recommended: do that check before the first external TestFlight build too** (the week of 28 Sep, ≈ 0.5 h).
  - External TestFlight is already a public distribution under your developer account: it has a public link and goes through App Review. Apple's own words are "Share your beta with just your team, or the public."
  - **Whether the policy treats it that way is for you to check.**
- **Individual or organisation enrolment:**
  - As an individual, "your name will be displayed as the seller name of your apps on the App Store".
  - An organisation shows the company name, but needs the company to exist and a **D-U-N-S number**.
  - Incorporation is already a gate before the first paid client (D38), so decide which before enrolling.
  - Moving an app between accounts later is possible but UNVERIFIED here.
- **The designer and the backup helper each sign the contributors agreement first** (D38, D55).
  - The designer signs before the brief (the week of 12 Oct).
  - The helper signs before the first external build, because that is when the safety button goes live.
- **The existing money gates are unchanged.** No in-app purchase in v0.

## Apple rules that shape v0 (App Review Guidelines, last updated 8 June 2026)

- **5.1.1(v):** "If your app supports account creation, you must also offer account deletion within the app." The app has no login, and **Delete my data** calls `DELETE /v1/me`, which is built and tested.
- **5.1.2(i):** "You must clearly disclose where personal data will be shared with third parties, including with third-party AI, and obtain explicit permission before doing so." So:
  - the consent screen has a **separate AI toggle**;
  - the brain stores it (`consent_ai`);
  - LLM extraction runs only for people who said yes.
- **4.8** (a Sign in with Apple equivalent) applies only to third-party logins, which v0 doesn't have.
- **4.2 minimum functionality** matters at App Store submission (≈ 3 h after Phase 5, outside v0). The plan and map make it more than a repackaged website.

## Open questions

1. Accept ≈ 53.5 h for the iOS v0 (plan ≈ 106.5 h in the window, about 1.5 h over)? This is the overrun question you held (D54).
2. Run the Apple outside-activities check now, before external TestFlight, rather than only before App Store release?
3. Individual or organisation developer account?
4. Voice for Test A: keyboard dictation plus a self-report question (0 h), or a measured on-device voice button (+2.5 h)?
5. Checkpoint 3 in about January (TestFlight), or keep November with hand-run tests (the fallback)?
6. Have you shipped an iOS app before? If not, the Face estimate probably needs +30%.

## Sources (accessed 2026-09-26)

- **TestFlight overview:** https://developer.apple.com/help/app-store-connect/test-a-beta-version/overview-of-testflight — 10,000 external and 100 internal testers; first build reviewed; 90 days; public links.
- **TestFlight:** https://developer.apple.com/testflight/ — "Share your beta with just your team, or the public"; public links.
- **Enrolment:** https://developer.apple.com/programs/enroll/ — the individual's legal name is shown as seller; organisations need a D-U-N-S number; US$99 a year, in local currency where available.
- **App Review Guidelines:** https://developer.apple.com/app-store/review/guidelines/ — 2.2, 4.2, 4.8, 5.1.1(v), 5.1.2(i); last updated 8 June 2026.
- **StatCounter, UK mobile OS share:** https://gs.statcounter.com/os-market-share/mobile/united-kingdom — August 2026: iOS 51.47%, Android 48.51%.
- **Apple docs:**
  - `MapKit/Marker` (iOS 17.0);
  - `Speech/requiresOnDeviceRecognition` (iOS 13.0: "prevent … sending audio over the network");
  - `Speech/SpeechAnalyzer` (iOS 26.0);
  - `SwiftUI/ShareLink` (iOS 16.0);
  - `UserNotifications/UNTimeIntervalNotificationTrigger` (iOS 10.0).
