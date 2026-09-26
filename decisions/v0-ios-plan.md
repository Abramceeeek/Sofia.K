# v0 as a native iOS app: plan, hours, cuts and TestFlight (D50–D54, D59–D64)

> **Updated by D59–D64 (2026-09-26):**
> - **The cuts are accepted** (D59).
> - **Tests A–C run by hand** and Checkpoint 3 stays in the week of 9 Nov (D63). The app is built in parallel, so the first external TestFlight build carries the Phase 3 lessons.
> - **iOS builds run on GitHub Actions**, with no Mac (D64), which adds 3 h, so **Phase 4 ≈ 56.5 h**.
> - **Individual developer account for TestFlight**; a company account before the App Store launch (D61).
>
> **Updated again by D65–D68:**
> - **The Brain is built now and writes the Test B plans** (`python -m brain.testb`).
> - **iOS app code and its GitHub Actions workflow wait until Test B reports**, about 2 Nov. The designer starts now.
> - About 25 moments move into Phase 3 for Test B (3.5 h), so **Phase 4 ≈ 53 h**. The plan total is unchanged, and the 1.3-week overrun is accepted (D67).
> - Test A runs on WhatsApp Business (D66).

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
  | iOS v0, left now (after the brain draft and the cuts below) | ≈ 53.5 (accepted, D59) |
  | **Plus the build-and-check loop through GitHub Actions** (D64) | **≈ 56.5** |

  The app itself is the big new cost: about 34 h, against 10 h for the bot.
- **Phase 3 (D63):**
  - Tests A–C run by hand, as originally planned: Test A is a chat, and the Test B/C plans go as messages or PDFs.
  - Phase 3 stays ≈ 23.75 h, and **Checkpoint 3 stays in the week of 9 Nov.**
  - The app is built in parallel. Only about 8.5 h of your build time falls before the checkpoint, because Phase 3 fills those weeks; the rest comes after it.
- **Plan total:** ≈ 117.5 h, or ≈ 114.5 h with the workbook reviews paused (D52). That is 15.3 weeks at 7.5 h, **about 9.5 h (1.3 weeks) past the 14-week window.**
- **Where the extra hours come from:**
  - hand-run tests cost 5 h more than the TestFlight version;
  - the build loop adds 3 h.

## The split

| | Brain (FastAPI, Python 3.12) | Face (SwiftUI, iOS 17+) |
|---|---|---|
| Owns | Moment database, population weights, each person's δ, the planner, ratings, the safety alert, data deletion | Screens, local notifications, map, share sheet, keyboard dictation |
| Where the maths runs | Server in v0. `brain/src/brain/personal.py` is numpy-only and stateless, so the same update can run on the phone later (Area 17, 8–12 h, after v0) | Nothing in v0 |
| Where it's built | Here, by Claude Code in the cloud (tests run here, and on Linux in GitHub Actions) | **GitHub Actions on a macOS runner (D64)**: build, sign and upload to TestFlight, triggered only by changes under the app folder. Claude writes the Swift here, but can't run it here, so every check goes through CI |
| Built so far | Schema and loader, seed moment 1 (draft), priors file, scoring with thresholds and interactions, δ update (Laplace), planner (time windows, transfer thresholds, peak–end toggle off), 22 API endpoints, 28 tests | Nothing |

**iOS 17+** because the SwiftUI `Map`/`Marker` API starts at iOS 17.0 (Apple docs).

## Build hours: iOS vs Telegram

| Block | Telegram v0 (D44, D45) | iOS v0, like-for-like | iOS v0, left now |
|---|---|---|---|
| **Face:** Telegram bot flow and transcription, or the SwiftUI app (below) | 10 | 31 | 31 + 3 for the CI loop (D64) |
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
| **Total** | **47** | **62.5** | **53.5 + 3 = 56.5** |

**The Face, 34 h:**

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
| Slower build-and-check loop through GitHub Actions, with no Xcode previews (D64) | 3 |

- **No 30% buffer** (D64): you have shipped an iOS app through GitHub Actions before.
- **The Apple set-up hours now cover the workflow:** a macOS runner builds, signs and uploads; Linux runs the brain's tests; you add the certificate, profile and App Store Connect API key to GitHub Secrets.
- **Cost:** the Apple Developer Program is **US$99 a year**, in local currency at enrolment. GitHub's macOS runners use up free Actions minutes faster than Linux; the rate on your plan is **UNVERIFIED**, so check it before relying on many builds a day.

## Cuts to keep v0 small (accepted, D59)

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

- **Voice (D62):** keyboard dictation plus "Did you type or speak?". No custom voice button. If it's ever wanted: +2.5 h, with on-device recognition (`requiresOnDeviceRecognition`, iOS 13+; `SpeechAnalyzer` on iOS 26).

## Testing through TestFlight: the first external build and Phase 5

*Superseded for Phase 3 by D63, where Tests A–C run by hand. This section now describes how the app is tested once the first external build goes out after Checkpoint 3, and in Phase 5.*

**How TestFlight works (Apple):**
- Up to **10,000 external testers**, invited by email or a **public link** with tester criteria (device, OS).
- Internal testers are **only App Store Connect users** (up to 100). **Strangers are therefore external testers.**
- **The first build for external testers goes through App Review.**
- Each build lasts **90 days**.
- Guideline 2.2: TestFlight apps "should be intended for public distribution" and **testers can't be given "compensation of any kind"**. A free day plan is the product itself, so it is fine; vouchers are not.

**Test by test:**

| Test | Hand-run (Phase 3, D63) | Through TestFlight (after Checkpoint 3) |
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

## Schedule (7.5 h a week, D63)

| Week of | Plan |
|---|---|
| 21 Sep (this week) | **Apple outside-activities check and the IP/invention-clause check in both contracts (D60)** |
| 28 Sep | Areas 1–3 review 5; seed moments and walk 1; conjoint and places 1 (D48) |
| 5 Oct | Areas 5–12 reviews 5.5; Test E recruiting 1.25; Areas 18 and 20 0.75 |
| 12 Oct | Test E interviews 4; decision note 1; validation materials 1; moment cards 1.5. **The designer brief moved to the week of 28 Sep** (D65) |
| 19 Oct – 2 Nov | **Tests A–D by hand**, with each person's Test B plans 1–3 days after their Test A (D68). The brain code review (2 h) is in the weeks of 26 Oct and 2 Nov. The Area 4 review is in the week of 2 Nov (D56). **Test B reports about 2 Nov: go or hold on the iOS code** |
| 9 Nov | Analysis and **Checkpoint 3** (2.5). If Test B passed, build 5: the GitHub Actions workflow, individual enrolment, the App Store Connect record |
| 16 Nov – ~28 Dec | **The build (≈ 48 h at 7.5 h a week), using what Phase 3 taught.** The first external TestFlight build is about the week of 30 Nov, once the onboarding, plan and safety screens work (≈ 19.5 h after 9 Nov). The designer's Build 1 screens are needed by about 16 Nov |
| Jan | Phase 5 through TestFlight (10 h), then the decision |
| ~3 weeks before App Store submission | Incorporate, get the D-U-N-S number and enrol as a company (D61; lead times under Gates) |

**If Phase 3 fails at Checkpoint 3**, only about 8.5 h of your build time has been spent, plus the brain draft (Claude's time).

## Gates

- **D53 and D60:** you check Apple's outside-activities policy **and** the IP/invention clauses in both contracts **this week**, before any external TestFlight build. The D53 gate before public release stays.
- **Developer account (D61): individual for TestFlight, a company before the App Store launch.**
  - As an individual, "your name will be displayed as the seller name of your apps on the App Store". TestFlight shows it to testers too (UNVERIFIED how prominently).
  - **Company lead time: about 1.5–3 weeks.**
    - Incorporation: online, "usually registered within 24 hours", £100 (gov.uk).
    - D-U-N-S number: "allow up to 5 business days" from D&B, and email them after two weeks.
    - Apple: "allow up to 2 business days" to receive it before you can enrol as a company (Apple D-U-N-S page).
    - Apple's own verification of the company enrolment takes an UNVERIFIED time on top.
  - **Start about 3 weeks before the planned submission.** Incorporation is also a gate before the first paid client (D38).
  - Moving the app from the individual account to the company account is UNVERIFIED here. Check Apple's app-transfer rules before the switch.
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

Resolved by D59–D64: hours and cuts, the timing of the Apple check, the account type, voice, the Checkpoint 3 date, and CI instead of a Mac. Still open:
1. **Which chat app for the hand-run Test A?** The materials are written for Telegram and work as they are.
2. **The app folder's name and layout in this repo** (for example `app/`), so the iOS workflow triggers only on it. This is decided when the workflow is written.

## Sources (accessed 2026-09-26)

- **TestFlight overview:** https://developer.apple.com/help/app-store-connect/test-a-beta-version/overview-of-testflight — 10,000 external and 100 internal testers; first build reviewed; 90 days; public links.
- **TestFlight:** https://developer.apple.com/testflight/ — "Share your beta with just your team, or the public"; public links.
- **Enrolment:** https://developer.apple.com/programs/enroll/ — the individual's legal name is shown as seller; organisations need a D-U-N-S number; US$99 a year, in local currency where available.
- **App Review Guidelines:** https://developer.apple.com/app-store/review/guidelines/ — 2.2, 4.2, 4.8, 5.1.1(v), 5.1.2(i); last updated 8 June 2026.
- **StatCounter, UK mobile OS share:** https://gs.statcounter.com/os-market-share/mobile/united-kingdom — August 2026: iOS 51.47%, Android 48.51%.
- **Apple D-U-N-S page:** https://developer.apple.com/support/D-U-N-S/ — "allow up to 5 business days to receive your number from D&B"; "allow up to 2 business days for Apple to receive your information".
- **Companies House (gov.uk):** https://www.gov.uk/limited-company-formation/register-your-company — online, £100, "usually registered within 24 hours"; by post, 8–10 days and £124.
- **Apple docs:**
  - `MapKit/Marker` (iOS 17.0);
  - `Speech/requiresOnDeviceRecognition` (iOS 13.0: "prevent … sending audio over the network");
  - `Speech/SpeechAnalyzer` (iOS 26.0);
  - `SwiftUI/ShareLink` (iOS 16.0);
  - `UserNotifications/UNTimeIntervalNotificationTrigger` (iOS 10.0).
