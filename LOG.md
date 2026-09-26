# LOG

These are the founder's hours, not Claude's. Budget is **~7.5 hrs/week**. Claude fills in the estimates. The founder fills in actuals.

## Phase status

| Phase | Target | Budget (hrs) | Est. (hrs) | Actual (hrs) | Status |
|---|---|---|---|---|---|
| 1 Research sweep | 2–3 wks | 15 | ≈ 18.5 | | **Approved** at Checkpoint 1 (D18). Full reviews of the notes continue in the weeks of 28 Sep and 5 Oct |
| 2 Unit economics | 1 wk | 5 | 5 | | **Approved** at Checkpoint 2 (2026-09-26). K-factor and payment-channel tabs added (D23, D24). **Economics paused (D52):** the 3 h of workbook review are deferred |
| 1b Light scans, Areas 13–20 | — | — | 3.75 | | Areas 13–17 (D22), Area 18 trip payments (D34), Area 19 automation (D44), Area 20 Uzbek B2B payments (D49). Design now, build after Phase 3 |
| 3 Validation | 2–3 wks | 15 | ≈ 18.75 | | **Test E runs first** (D36), then the decision note (D40). **Tests A–C run through TestFlight in the app (D50)**: Test A from about 23 Nov. Thresholds on strangers only (D43). **Checkpoint 3 about the week of 4 Jan** (was 9 Nov) |
| 4 Prototype v0 | 4–5 wks | 35 | ≈ 53.5 | | **Native iOS app (D50): the Face ≈ 31, and what's left of the Brain ≈ 22.5.** The Brain is started (D51, `brain/`). About 40.5 h is built before Checkpoint 3 so Tests A–C can run in the app; ≈ 13 h is left after it. Proposed cuts are in `decisions/v0-ios-plan.md` (the Telegram v0 was 47) |
| 5 Test v0 and decide | 2 wks | 10 | 10 | — | Not started |
| **Total** | **11–14 wks** | **80** | **≈ 109.5** | | ≈ 106.5 h in the window with the 3 h of workbook review paused (D52): 14.2 weeks, **about 1.5 h past the 14-week window** (105 h). App Store submission (≈ 3 h) comes after Phase 5 and the D53 gate |

## Phase 1 areas

The founder's hours below are for reviewing each note and skimming its 1–2 key sources.

| # | Note | Depth | Est. (hrs) | Actual (hrs) | Status |
|---|---|---|---|---|---|
| 1 | `01-onboarding.md` | Critical | 2.0 | | Drafted: 39 sources, key stats and prices re-verified |
| 2 | `02-place-preferences.md` | Critical | 2.0 | | Drafted and revised for moments (D9): 26 sources |
| 3 | `03-personal-weights.md` | Critical | 2.0 | | Drafted: 17 sources |
| 4 | `04-itinerary.md` | Critical | 2.0 | | Drafted: 26 sources, key stats and prices re-verified |
| 5 | `05-photo-taste.md` | Lighter | 1.0 | | Drafted: 6 sources |
| 6 | `06-wellbeing.md` | Lighter | 1.0 | | Drafted: 22 sources |
| 7 | `07-existing-products.md` | Lighter | 1.0 | | Drafted: 14 sources |
| 8 | `08-seamless-interaction.md` | Light scan | 0.5 | | Drafted: 7 sources |
| 9 | `09-body-signals.md` | Light scan | 0.5 | | Drafted: 5 sources |
| 10 | `10-money.md` | Light scan | 0.5 | | Drafted: 6 sources |
| 11 | `11-companion-matching.md` | Light scan | 0.5 | | Drafted: 3 sources |
| 12 | `12-legal-ethics.md` | Light scan | 0.5 | | Drafted: 6 sources |
| — | `decisions/phase-1-summary.md` (Checkpoint 1) | Review | 1.5 | | Approved 2026-09-26 |
| | Decision rounds (D1–D17) and seed moments | — | 3.5 | | Not in the original 15 h |
| | **Phase 1 total** | | **≈ 18.5** | | 3.5 h over the 15 h budget |

## Phase 2 (unit economics)

| Item | Est. (hrs) | Status |
|---|---|---|
| Read `decisions/phase-2-summary.md` and decide the open questions | 1.5 | Pending |
| Review the workbook: the 44 GUESS inputs on `Inputs` and the yellow cells | 2.5 | Pending |
| Read `economics/assumptions.md` | 0.5 | Pending |
| Decision round D18–D22 (Checkpoint 1 approval) | 0.5 | Done 2026-09-26 |
| **Phase 2 total** | **5.0** | On budget |

Claude re-verified the pricing and cost sources before building the model (D20). That corrected the Met Office tiers and the Tavus plans, and found the Telegram Stars rule. Nineteen sources are Phase 2 (`econ`) sources.

## Areas 13–20 (light scans, D22, D34, D44, D49): design now, build after Phase 3

| # | Note | Review (hrs) | Build later (hrs) | Status |
|---|---|---|---|---|
| 13 | `13-moment-mining.md` | 0.5 | ~6 (pilot on Wikivoyage + Geograph) | Drafted: 9 sources. Reddit and Tripadvisor ruled out on their terms |
| 14 | `14-spatial-moments.md` | 0.5 | 8–10 (2D isovist reveal score + scenicness prior) | Drafted: 10 sources |
| 15 | `15-travel-motivation.md` | 0.5 | ~1 in Phase 4 (store intent) + 4–6 later | Drafted: 6 sources |
| 16 | `16-home-contrast-novelty.md` | 0.5 | 4–6 | Drafted: 3 sources (plus Areas 12 and 14) |
| 17 | `17-on-device-personalisation.md` | 0.5 | ~1 in Phase 4 (separate δ) + 8–12 on device + 20–30 federated/DP, needs a native app | Drafted: 7 sources |
| 18 | `18-trip-payments.md` (D34) | 0.5 | Payments ~8–10, safety kit ~4, after v0 and the legal gates | Drafted: 13 sources. Day trips are outside the Package Travel Regs; never hold trip money |
| 19 | `19-automation.md` (D44) | 0.5 | iOS plan (D50): the app is self-serve by design; the AI support agent (6) is proposed for after v0, with a safety button instead (0.5, built). Content 5, after v0 (D45) | Drafted: escalation rules. Safety alerts go to Abram within a few hours, and to a named backup helper during his work hours (D46) |
| 20 | `20-uzbek-b2b-payments.md` (D49) | 0.25 | ~2.5 one-off at the first Uzbek client: Stripe Invoicing, Wise Business, HMRC certificate, adviser call | Drafted: 16 sources. GBP invoice paid by international card or SWIFT; no Stripe in Uzbekistan needed |
| | **Total** | **3.75** | **In the iOS Phase 4 plan (D50); ~70–95 later** | |

Sources now total 309 in `research/sources.csv`: 194 read on the page, 112 through search only, 3 UNVERIFIED. The 21 `v0` rows cover Apple (TestFlight, enrolment, App Review, iOS APIs), StatCounter and the brain's packages.

## Phase 3 (validation): founder hours

Plan in `validation/README.md`. **Test E runs first** (D36). **Tests A–C run in the app through TestFlight (D50).** There are 12 stranger participants (D30, D43). The app build these tests need is counted in Phase 4.

| Item | Est. (hrs) | Week |
|---|---|---|
| Confirm the 6 conjoint attributes and the 16 swipe places (D30, moved by D48) | 1.0 | 28 Sep |
| Seed moment 1 walk: fill the gaps, photo, finish the example shot card (D35) | 0.5 | 28 Sep |
| **Test E:** recruit 5 B2B contacts (3 London, 2 Uzbek outbound agencies, D49; log minutes) | 1.25 | 5 Oct |
| **Test E:** 5 discovery interviews with prep and notes | 3.75 | 12 Oct |
| **Test E:** check the translated script for Uzbek interviews, if needed | 0.25 | 12 Oct |
| **Decision note:** B2B-first vs consumer-first (D40) | 1.0 | 12 Oct |
| Rewrite the consent form, privacy notice, Post 1 and a tester guide for the app (Claude drafts) | 1.0 | 16 Nov |
| Landing page, form and analytics set-up | 1.0 | 16 Nov |
| Recruitment posts and replies (log minutes per post) | 2.0 | 16 Nov |
| Test A: tester support (the app runs the onboarding) | 1.0 | 23 Nov |
| Read-back checks | 0.5 | 23 Nov |
| Test B plans (generic once + 12 personalised: the planner drafts, you edit and push) | 3.0 | 7 Dec |
| Test C follow-ups (ratings arrive in the app) | 1.0 | 7–21 Dec |
| Analysis and `results.md` (Checkpoint 3) | 1.5 | ~4 Jan |
| **Total** | **≈ 18.75** | Tests A–D ≈ 12 (D50) + Test E, decision note and seed walk ≈ 6.75 |
| *Optional:* 3 venue conversations | *+2.0* | — |

## Phase 4 build estimate: native iOS app (D50, D51; founder hours, Claude Code writes the code)

Full plan, cuts and the Telegram comparison: [`decisions/v0-ios-plan.md`](decisions/v0-ios-plan.md). Scope decisions D5–D8, D11, D14–D16 and D19 still hold: 50 hand-picked moments, shot cards for ~20, no photo taste, log-only feedback, peak–end off by default, and no allergy question.

| Component | Est. (hrs, left) | Status 2026-09-26 |
|---|---|---|
| **Face:** the SwiftUI app (22 screens, `design/v0-screens.md`), Apple set-up, designer, TestFlight | 31 | Not started. Built on your personal Mac |
| Onboarding back end: extraction (only with AI permission), read-back lines, gold-set check | 3 | Read-back from named weights is built; LLM extraction is not |
| Safety alert to a person (D46) | 0.5 | Built; set up the webhook |
| Moment DB: seed session, 45 LLM-drafted cards and review, ~20 shot cards, swipe set | 5 | Schema, loader and API built; the content is yours |
| Planner: matrices, weather rules, LLM explanation, tuning | 7 | OR-Tools model, time windows, transfer thresholds, peak–end toggle and tests built |
| Weights and scoring: review, pooled refit from Phase 3 data | 2.5 | Per-user Laplace posterior and scoring built |
| Ratings and events logging | 0.5 | Built |
| Privacy: deletion, notice, AI permission | 1.5 | Deletion and the consent flag built; the notice needs rewriting |
| Design hooks: separate δ, trip intent per plan (D27) | 0.5 | Built |
| Hosting: Render + Postgres, secrets, migrations | 2 | Not started |
| **Total** | **≈ 53.5** | ≈ 40.5 before Checkpoint 3 (Test A ≈ 28, Tests B–C ≈ 12.5); ≈ 13 after |
| *After v0:* AI support agent (proposed cut), content automation (D45), full HB refit, on-device δ (Area 17), tagging benchmark (D32) | *6 + 5 + ~1 + 8–12* | |
| *After Phase 5 and the D53 gate:* App Store submission | *≈ 3* | |

## Hours log

| Date | Phase | Activity | Est. (hrs) | Actual (hrs) | Notes |
|---|---|---|---|---|---|
| 2026-09-26 | 1 | Kickoff: write brief and `CLAUDE.md`, review repo setup and plan | 1.0 | | |
| 2026-09-26 | 1 | Skim Areas 1 and 4, decisions D1–D8, widen network access | 1.0 | | |
| 2026-09-26 | 1 | Decisions D9–D13 (moments, Python 3.12, hand-picking) | 0.5 | | |
| 2026-09-26 | 1 | Decisions D14–D17 (hours, peak–end, photos, schedule) | 0.5 | | |
| 2026-09-26 | 1 | Read Checkpoint 1 summary and approve | 1.5 | | Done early |
| 2026-09-26 | 2 | Decisions D18–D22 | 0.5 | | |
| 2026-09-26 | 2 | Read Checkpoint 2 summary and approve; decisions D23–D29 | 2.0 | | Done early |
| 2026-09-26 | 3 | Decisions D30–D35; seed moment 1 written up | 1.0 | | |
| 2026-09-26 | 3 | Decisions D36–D44 | 1.0 | | |
| 2026-09-26 | 3 | Decisions D45–D49; read the Uzbek payment answer | 0.5 | | |
| 2026-09-26 | 4 | Decisions D50–D58 (iOS direction) | 0.5 | | |
| wk 28 Sep | 3 | Confirm conjoint attributes and swipe places (D30, moved by D48) | 1.0 | | Pending |
| wk 28 Sep | 1 | Review Areas 1–3 in full, including the 15 moment features (D17) | 5.0 | | Pending. Area 4 moved to the week of 2 Nov (D56) |
| wk 28 Sep | gate | Apple outside-activities check (D53; proposed before external TestFlight) | 0.5 | | Pending |
| wk 28 Sep | 1 | Seed moments 2–5 in the Area 2 schema (D13); walk for seed 1 (D35) | 1.0 | | Pending. Seed 1 received 2026-09-26 |
| wk 5 Oct | 1 | Review Areas 5–7 (D17) | 3.0 | | Pending |
| wk 5 Oct | 1 | Review Areas 8–12 light scans | 2.5 | | Pending |
| wk 5 Oct | 3 | Test E: recruit 5 B2B contacts; review the Area 18 and Area 20 notes | 2.0 | | Pending |
| wk 12 Oct | 3 | Test E: 5 interviews, Uzbek script check, decision note | 5.0 | | Pending |
| wk 12 Oct | 4 | Brain code review: scoring maths and the planner (`brain/`); part of the Test A build | 1.0 | | Pending |
| wk 12 Oct | 4 | Designer brief and contributors agreement (D38); part of the Test A build | 1.5 | | Pending |
| wk 12 Oct | 2 | Review workbook GUESS inputs and `assumptions.md` (first half) | (1.5) | | **Paused (D52)** |
| wk 19 Oct – 16 Nov | 4 | Test A build: Face and Brain (`decisions/v0-ios-plan.md`); 28 h in all, with 2.5 in the week of 12 Oct | 25.5 | | Pending |
| wk 2 Nov | 1 | Review Area 4 (D56) | 2.0 | | Pending |
| wk 16 Nov | 3 | Materials rewrite, recruitment, landing page; first external build to App Review | 4.0 | | Pending |
| wk 23 Nov – 4 Jan | 3 | Run Tests A–D (see the Phase 3 table) | 7.0 | | Pending |
| wk 16 Nov – 30 Nov | 4 | Build for Tests B and C | 12.5 | | Pending |
| Jan | 4, 5 | The rest of v0 (≈ 13), then Phase 5 (10) | 23.0 | | After Checkpoint 3 |
| wk 2 Nov | 1b | Review Areas 13–17 and 19 light scans, including the God's Eye View and Jev addenda (Areas 18 and 20 are in the week of 5 Oct) | 3.0 | | Pending |
| wk 2 Nov | 2 | Review workbook (second half: Path50k, Automation, Expansion) | (1.5) | | **Paused (D52)** |

## Weekly totals

| Week of (Mon) | Budget | Est. | Actual |
|---|---|---|---|
| 2026-09-21 | 7.5 | 10.0 (kick-off, checkpoints and decision rounds D1–D58, already spent): **2.5 over** | |
| 2026-09-28 | 7.5 | 7.5 (Areas 1–3 review 5, seed moments 1, conjoint and places 1, Apple check 0.5) | |
| 2026-10-05 | 7.5 | 7.5 (Areas 5–12 reviews 5.5, Test E recruiting 1.25, Areas 18 and 20 0.75) | |
| 2026-10-12 | 7.5 | 7.5 (**Test E interviews 4.0, decision note 1.0**; the Test A build starts: brain review 1.0, designer brief and agreement 1.5) | |
| 2026-10-19 | 7.5 | 7.5 (Test A build) | |
| 2026-10-26 | 7.5 | 7.5 (Test A build) | |
| 2026-11-02 | 7.5 | 7.5 (Area 4 review 2.0, Areas 13–17 and 19 review 3.0, Test A build 2.5) | |
| 2026-11-09 | 7.5 | 7.5 (Test A build) | |
| 2026-11-16 | 7.5 | 7.5 (Test A build 0.5, materials rewrite 1.0, recruitment 2.0, landing page 1.0, build for B and C 3.0). First external build to App Review | |
| 2026-11-23 | 7.5 | 7.5 (**Test A runs**: support 1.0, read-back 0.5; build for B and C 6.0) | |
| 2026-11-30 | 7.5 | 3.5 (build for B and C). Slack for App Review of the second build, and late testers | |
| 2026-12-07 | 7.5 | 3.5 (**Test B** plans 3.0; Test C starts, follow-ups 0.5) | |
| 2026-12-14 | 7.5 | 0.5 (Test C follow-ups). Spare weeks over Christmas | |
| 2027-01-04 | 7.5 | 1.5 (analysis). **Checkpoint 3** | |

## Decisions

See [`decisions/decision-log.md`](decisions/decision-log.md).
- D1–D8: Test D takes no money; audio retention opt-in for 30 days; answer mode is a Test A variable; v0 scope cut; peak–end is a toggle.
- D9–D13: moments are the unit; new moment features; moments hand-picked; Python 3.12; 5 seed moments.
- D14–D17: shot cards for ~20 moments and ~36 h accepted; end bonus off by default; photo pairs replaced by two Test A questions; review schedule.
- D18–D22: Checkpoint 1 approved and thresholds kept, with Test A split by voice vs text; one optional "foods or drinks you avoid" question; pricing re-verified before the model; separate recruitment posts; light scans of Areas 13–17.
- D23–D29: Phase 3 measures referral and K; payment method deferred (Telegram forbids linking out for digital goods); Test D at £4.99 vs £9.99 a month, waitlist only; Meta test deferred; +2 h Phase 4 hooks accepted; God's Eye View and Jev evaluated.
- D30–D35: Tests A–D at ≈ 17 h with 12 participants; annual prices £49.99 / £99.99 (about two months free); Jev benchmark after v0; right-to-run-a-business gate cleared, two gates remain; trip payments, free-first, venue and B2B lines added, plus 5 B2B interviews (Test E); seed moment 1 received.
- D36–D44: Test E first, with 2 Uzbek interviews; no paid group trips in year one, venues a user benefit only, B2B primary in Path50k; more gates (IP clauses, incorporation + ICO + insurance, contributors agreement); never hold trip money; decision note after Test E; helper hours as one input (default 0); city-expansion gate; friends and family a separate channel with strangers-only thresholds; automation scenario.
- D45–D49: content automation after v0 (Phase 4 ≈ 47 h); safety alerts to Abram within a few hours, with a named backup helper in his work hours; expansion thresholds confirmed; conjoint and places review moved to the week of 28 Sep; Uzbek focus on outbound agencies at London prices, paid by international card or SWIFT to a UK account.
- D50–D58: v0 is a native iOS app, tested through TestFlight, replacing the Telegram bot; Brain (FastAPI) and Face (SwiftUI), with the Brain started now; economics paused; a new gate before App Store release (Apple outside-activities policy); the overrun question held until the iOS re-plan; Abram names the backup helper, who signs before support goes live; the Area 4 review moved to the week of 2 Nov; the Test E bar confirmed; the Uzbek payment route accepted, with one adviser call first.

## Open questions

1. **Accept the iOS v0 at ≈ 53.5 h, with the proposed cuts?** That puts the plan at ≈ 106.5 h in the window, about 1.5 h over. This is the overrun question you held (D54). The cuts are in `decisions/v0-ios-plan.md`: the AI support agent goes after v0, keyboard dictation replaces a voice recorder, local notifications replace a push server, and so on.
2. **Run the Apple outside-activities check now**, before the first external TestFlight build, rather than only before App Store release (D53)? External TestFlight is already public distribution under your account.
3. **Individual or organisation developer account?** An individual account shows your legal name as the seller. An organisation needs the company and a D-U-N-S number.
4. **How to measure voice in Test A?** Keyboard dictation plus a self-report question (0 h), or a measured on-device voice button (+2.5 h)?
5. **Checkpoint 3 in early January (TestFlight), or November?** November means hand-run tests over iMessage or WhatsApp, with TestFlight kept for Phase 5.
6. **Have you shipped an iOS app before, and do you have a personal Mac?** If not, add about 30% to the Face estimate. A Mac is required.
7. **Helper hours** (`helper_hours_week`, default 0). Set your own number when you know it.
8. **Weekend test hours.** Your weekend test isn't in this budget.

Resolved 2026-09-26: network access; Test D vs legal gates (D1/D2); Test A audio (D3); voice vs text (D4); Python version (D12); place DB sourcing (D11); Phase 4 budget (D14, D27, D44, D45); peak–end default (D15); photo pairs (D16); Checkpoint 1 and thresholds (D18); food question (D19); source re-verification (D20); recruitment posts (D21); Checkpoint 2 (D23–D29); payment channel deferred (D24); Test D prices (D25, D31); Meta test deferred (D26); Phase 3 at 12 participants (D30); Jev timing (D32); legal gates (D33, D38); seed moment 1 (D35); Test E order (D36); year-one scope (D37); trip money guardrail (D39); team capacity input (D41); friends and family channel (D43); safety cover (D46); expansion thresholds (D47); week of 21 Sep (D48); Uzbek focus (D49); v0 platform (D50–D52); backup helper (D55); Area 4 review week (D56); Test E bar (D57); Uzbek payment route (D58).
