# Decision log

Founder decisions that amend `KICKOFF_PROMPT.md`. Newest first. Where this log and the kickoff brief disagree, this log wins.

## 2026-09-26 (night) — seed moments batch 1, agreement split, Apple renewal, after-9-Nov rule

| # | Decision | Replaces | Why |
|---|---|---|---|
| D72 | **Seed moments batch 1 (11) are drafted as cards**, with gaps flagged (`research/seed-moments/02-batch-1.md`). Three new ideas go in now because the cards need them for Test B: **entry types** (moment vs area vibe; one area a day, never the peak), **variants** (day/night; at most one per plan) and **route direction**. **Draft cards never go into real plans**: Test B and the API use only `status: ready` | — | Founder request. The rest of the new features wait (D75); `decisions/new-moment-features.md` |
| D73 | **The contributors agreement is split.** (a) **Part A**, IP assignment, confidentiality and the personal-data clause, is **signed now, as a deed**. (b) **Part B**, the equity terms, gets a solicitor review before incorporation. **No fixed hours:** contributions are voluntary and flexible (`legal/contributor-deed-part-a.md`, `legal/contributor-equity-terms-part-b-draft.md`) | D70d's single agreement | Founder decision. It's a deed because Part A gives nothing in return (see its notes) |
| D74 | **Apple Developer membership:** Abram checks its status. **Renew only if Test B passes.** The GitHub secrets (0.75 h) need an active membership, so if it has lapsed they move after Test B. **Auto-renew must be off**: Apple charges the card on the expiry date when it's on (Apple help, 2026-09-26) | D70e's timing for the secrets | Founder decision (money) |
| D75 | **New rule:** any new idea that doesn't help Test B goes on `decisions/after-9-nov.md` instead of into the current plan. Added to `CLAUDE.md` as working rule 9 | — | Founder decision |
| D76 | **The swipe page's privacy note is approved.** Abram deploys on Render with **no payment method** and shares the link | For Abram item 1 (D69–D71) | Founder decision |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m9 | The night river card ends at **Westminster**, the only pier reached every evening (checked on the timetables). The day card runs to Battersea | `m_uber_boat_west_night.yaml` |
| m10 | The two tower walks (Canary Wharf, City) share a variant group: at most one per plan | the two cards |
| m11 | "Any London park" is drafted as **St James's Park** (pelicans, checked); Richmond's viewpoint as **King Henry's Mound** (checked). Both are for Abram to confirm | the two cards |
| m12 | Coordinates come from OpenStreetMap (Nominatim), one request a second. Two are approximate points near the stations (Canary Wharf, Bank) | cards; `research/sources.csv` |
| m13 | `--include-drafts` gives a dry run with draft cards; the output says "DRY RUN" | `brain/src/brain/testb.py` |

**For Abram (scope):** **aspiration match** is the one new weight that could help Test B. It needs one optional Test A question (≈ 0.5 h of your time). Yes, or on the after-9-Nov list? (`decisions/new-moment-features.md`)

## 2026-09-26 (evening) — standing rule, Test E kit, swipe page, agreement, iOS pipeline

| # | Decision | Replaces | Why |
|---|---|---|---|
| D69 | **Standing rule:** Claude makes minor decisions itself and logs them: wording, file layout, scheduling moves under 1 h, and tooling within the agreed stack. It stops only for decisions that **change scope, cost money, affect privacy or safety, or move a checkpoint**. Everything else is batched into one list at each checkpoint (below) | Asking about each minor choice | Founder decision; added to `CLAUDE.md` as working rule 8 |
| D70a | **WhatsApp Business second number is ready.** Abram shares it when needed | Set-up pending | Founder update |
| D70b | **Test E comes in two shareable forms:** a 30-min call guide, and a two-message version agencies answer in writing (English, Russian, Uzbek). **Hotel staff contacts are asked to introduce Abram to a manager or budget holder** (`validation/test-e-kit.md`, published with copy buttons) | The script only | Founder request. The description stays in message 2, so nothing is pitched before the questions |
| D70c | **An anonymous swipe page calibrates the 16 places:** ~30 candidates; Loved it / It was fine / Didn't enjoy it / Haven't been. There is no login and no personal questions, and no IP address is stored, only a random browser ID. **The 16 are picked by familiarity × divisiveness** (`brain/src/brain/calibration.py`) | Abram choosing the 16 by judgement (D30, D48) | Founder request. Onboarding needs places that split people (CLAUDE.md) |
| D70d | **Contributors agreement drafted:** role, IP assigned to the company (via Abram until it's incorporated), a **~10% equity placeholder with 4-year vesting and a 1-year cliff, granted once the company is incorporated** (`legal/contributors-agreement-draft.md`) | Agreement pending (D38) | Founder request. It must be signed before anyone else contributes work |
| D70e | **The GitHub Actions iOS pipeline starts now** (`.github/workflows/ios.yml`, a placeholder `app/`). Abram adds the secrets. **The app's feature code still waits until Test B reports** | D65's hold on the workflow | Founder request |
| D71 | **The Areas 8–12 review stays deferred to after Checkpoint 3** (approved). **Moment names arrive as they come**, not only in the week of 5 Oct; Claude drafts each card on arrival | Open questions 1 and 2 | Founder decision |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m1 | The swipe page runs as a small separate app on **Render's free tier** (a free web service plus free Postgres in Frankfurt, £0), deployed from `render.yaml`. The Artifact database can't take answers from anonymous public visitors (it is organisation-internal only) | `render.yaml`, `brain/README.md` |
| m2 | **30 candidates:** the draft 16, plus London Eye, Tower of London, Covent Garden, Buckingham Palace, Oxford Street, Piccadilly/Leicester Square, Kew, Richmond Park, Portobello Road, St Paul's, South Bank walk, Platform 9¾, Madame Tussauds and Westfield. All tags are DRAFT | `brain/data/calibration/places.yaml` |
| m3 | **Ranking rule:** only people with ≥ 10 answers count; places with < 5 visitors rank last; the results page warns when a taste tag appears in fewer than 2 of the 16 | `calibration.py` |
| m4 | **Page details:** the day is stored, not the time; one-tap deletion; no cookies, analytics or third-party fonts; `noindex`; the contact email is set at deploy | `data/calibration/index.html` |
| m5 | Test E message version: two messages. Claude's Russian and Uzbek translations, to be checked (0.25 h, already budgeted) | `validation/test-e-kit.md` |
| m6 | Agreement: IP goes to Abram, who holds it for the company until incorporation; one week's notice; the bad-leaver terms are left to the solicitor | `legal/contributors-agreement-draft.md` |
| m7 | **iOS pipeline:** XcodeGen (no committed project file); target "Face", display name "Planner" (placeholder); iOS 17+, iPhone only; the `macos-26` runner; team, bundle ID and profile read from the profile; a throwaway keychain password; simulator-only builds until the secrets exist; uploads only from `main` or a manual run | `app/`, `.github/workflows/ios.yml` |
| m8 | **Schedule moves:** swipe page deploy and share in the week of 28 Sep (0.75 h); pick the 16 in the week of 12 Oct (0.5 h, after two weeks of answers); "confirm the 16 places" shrinks to checking the candidates (1.0 → 0.5 h); secrets and the App Store Connect record move from the week of 9 Nov to the week of 26 Oct (0.75 h). **Net +0.75 h on the phase totals** (≈ 115.25 h in the window, 15.4 weeks), plus 0.25 h for this decision round | `LOG.md` |

**For Abram (money or privacy; not decided by Claude):**
1. **Privacy: read the swipe page's privacy note before sharing the link.** It is live only once you deploy it.
   - It keeps a random ID in the browser's local storage. Claude judges this to be "strictly necessary" under PECR (ICO guidance, 29 Apr 2026), because it only records the answers the visitor chose to give. This is Claude's judgement, not legal advice.
   - It deletes answers by 31 March 2027, the same date as the study data.
   - It says Render's own servers may keep technical logs, which our code can't switch off.
2. **Money: solicitor review of the agreement** before signing. The cost is UNVERIFIED.
3. **Money: the secrets need an active Apple Developer Program membership.** If you aren't enrolled yet, enrolling now pays the annual fee before Test B reports (it was planned for 9 Nov, and only if Test B passed). The simulator build runs without it.
4. **Legal gate:** the designer works now (D65), so the agreement must be signed before their work is used. If they've already started, sign now: clause 3 covers work already done.

## 2026-09-26 (after the founder briefing) — Test B first, WhatsApp, brain now

| # | Decision | Replaces | Why |
|---|---|---|---|
| D65 | **Build the Brain now, and use it to generate the Test B plans.** The designer starts now. **The iOS app code, including its GitHub Actions build, is held until Test B reports** | The app built in parallel (D63) | Test B is the premise; don't spend app hours before it |
| D66 | **Test A runs on WhatsApp Business with a separate number**, not Telegram. The materials are updated | Telegram for the hand-run tests | Founder decision |
| D67 | **The 1.3-week overrun is accepted** (≈ 114.5 h in the window) | Open question | Founder decision |
| D68 | **Test B runs first and as fast as possible after Test E.** Each person's Test A chat is followed by their two plans within 1–3 days, so Test B reports about the week of 2 Nov | Test B as a batch in the week of 26 Oct | The briefing's advice: Test B is the most informative test |

## 2026-09-26 (Phase 3 round 6) — iOS plan accepted, hand-run tests, build in the cloud

| # | Decision | Replaces | Why |
|---|---|---|---|
| D59 | **Accept the iOS v0 at 53.5 h with the proposed cuts** (`decisions/v0-ios-plan.md`): no AI support agent in v0 (a safety button instead), keyboard dictation, local notifications, no login, and "Directions" opens Apple Maps | Proposed (D54) | Founder decision |
| D60 | **Abram does the Apple outside-activities policy check and the IP/invention-clause check in both contracts this week**, before the first external TestFlight build | Proposed timing (D53) | Founder decision |
| D61 | **An individual developer account for TestFlight. Switch to a company account before the public App Store launch.** That means incorporation (online, "usually within 24 hours", £100), then a D-U-N-S number ("allow up to 5 business days"; email D&B after two weeks), then "up to 2 business days" for Apple to receive it (sources: gov.uk, Apple D-U-N-S page, 2026-09-26). **Start about 3 weeks before the planned App Store submission.** How to move the app to the company account is UNVERIFIED | Open question | Founder decision |
| D62 | **Voice in the app is keyboard dictation plus "Did you type or speak?"** No custom recorder | Open question | Founder decision |
| D63 | **Checkpoint 3 stays in the week of 9 Nov. Tests A–C run by hand**: Test A as a chat conversation, and the Test B/C plans sent as messages or PDFs. **The iOS app is built in parallel**, so the first external TestFlight build carries the lessons | Tests A–C through TestFlight (D50) | Keeps the evidence gate before most build hours |
| D64 | **iOS builds run on GitHub Actions** (Abram has shipped an iOS app this way; no personal Mac). A macOS runner builds, signs and uploads to TestFlight. Backend tests run on Linux. iOS builds trigger only on changes under the app folder. **Abram adds the signing certificate, provisioning profile and App Store Connect API key to GitHub Secrets.** No 30% buffer, but **+3 h for the slower build-and-check loop** without Xcode previews, so Phase 4 ≈ 56.5 h | "Built on a personal Mac" (D50, D51) | Founder decision |

## 2026-09-26 (Phase 3 round 5) — v0 becomes a native iOS app

| # | Decision | Replaces | Why |
|---|---|---|---|
| D50 | **v0 is a native iOS app (SwiftUI).** Testers get it through **TestFlight**, then the App Store once it passes. **The Telegram bot plan is replaced.** Phase 3 Tests A–C run through TestFlight; Tests D (web page) and E are unchanged. Plan, hours, proposed cuts and designer screens: `decisions/v0-ios-plan.md`, `design/v0-screens.md` | Telegram bot v0 (Areas 1, 8, 19); the "no code before Phase 3 passes" rule for Tests A–C | Founder decision |
| D51 | **Two parts.** The **Brain** is a FastAPI backend: moment database, scoring (hierarchical βs, with δ_person separate so it can move on-device later) and the OR-Tools planner. The **Face** is the SwiftUI app: self-serve onboarding (text first, voice optional), moment and shot cards, a day plan with map, one-tap ratings. **Building the Brain starts now, in parallel with Test E**, because it doesn't depend on test results. First draft in `brain/` (28 tests pass) | Phase 4 gated on Phase 3 for all build work | Founder decision |
| D52 | **Economics work is paused** unless a decision needs it. The workbook reviews (3 h) are deferred. The workbook's Telegram Stars base case is now stale; its Apple rows already cover an iOS app | — | Hours go to the build |
| D53 | **New gate before public App Store release:** check Apple's outside-activities policy for publishing under Abram's own developer account. Added to `CLAUDE.md`. *Proposed:* do the check before the first external TestFlight build too (open question) | — | Founder decision |
| D54 | **The 3 h overrun question is held** until Phase 4 is re-planned for iOS. The re-plan is now in `decisions/v0-ios-plan.md`: ≈ 106.5 h in the window, about 1.5 h over | LOG open question 1 | Founder decision |
| D55 | **Abram names the backup helper** for safety alerts. They sign the contributors agreement (D38) **before support goes live**. In the iOS plan that is the first external TestFlight build, when the Help & safety button goes live | Open question on who the helper is | Founder decision |
| D56 | **The Area 4 review moves to the week of 2 Nov** | Week of 28 Sep | Balances that week |
| D57 | **Test E pass bar confirmed:** ≥ 2 of 5 already spend money or staff time on this, **and** ≥ 2 of 5 give an introduction or agree to an unpaid pilot | Proposed read-out | Founder confirmed |
| D58 | **Uzbek payment route accepted** (Area 20): a GBP invoice from the UK company, paid by international card through Stripe or by SWIFT to the UK business account; an HMRC certificate of residence first; **one adviser call before the first Uzbek invoice** | Proposed route (D49) | Founder decision |

## 2026-09-26 (Phase 3 round 4) — Phase 4 trim, safety cover, gate confirmed, Uzbek focus

| # | Decision | Replaces | Why |
|---|---|---|---|
| D45 | **Content automation (≈5 h) moves to after v0.** Phase 4 keeps self-serve onboarding (3 h) and the AI support agent (6 h), so Phase 4 ≈ 47 h and the plan ≈ 108 h | Automation 3 in Phase 4 (D44) | Brings the plan back to about 14.4 weeks |
| D46 | **Safety alerts at the start: Abram handles them, with a response target of within a few hours. A named backup helper covers his working hours.** The helper signs the contributors agreement, including confidentiality, first (D38). The auto-reply gives 999 guidance and never promises a faster reply. Added to `CLAUDE.md` and Area 19 | "A human, promptly", same hour where possible (D44) | 7.5 h a week and a full-time job |
| D47 | **City-expansion thresholds confirmed:** ≥ 300 monthly active strangers, ≥ 30% asking for a second plan within 30 days, stranger K ≥ 0.3, all held for 3 consecutive months | Proposed thresholds (D42) | Founder confirmed |
| D48 | **The review of the conjoint attributes and swipe places moves to the week of 28 Sep** | Week of 21 Sep (D30) | That week was 2.5 h over |
| D49 | **Uzbekistan: focus on outbound agencies sending clients to London, at London prices.** Both Uzbek Test E interviews are with outbound agencies. Uzbek hotels and tour operators, and local PPP prices, are not pursued in year one. Payment route checked (Area 20): invoice from the UK company, paid by an Uzbek-issued international Visa or Mastercard through Stripe, or by SWIFT transfer to the UK business bank account. **No Stripe presence in Uzbekistan is needed** | Uzbek hotel or tour operator interview and local price scenarios (D36) | London prices are ~3× the local level, and the curation already exists |

## 2026-09-26 (Phase 3 round 3) — B2B first in Phase 3, team, automation, expansion

| # | Decision | Replaces | Why |
|---|---|---|---|
| D36 | **Test E runs first in Phase 3, all 5 interviews kept.** Two of the five are **Uzbek contacts**: travel agencies sending clients to London, and hotels or tour operators in Uzbekistan. Add local price scenarios | Test E in parallel (D34) | B2B is the likely primary line |
| D37 | **Year one: no paid group trips** (the unpaid weekend test stays). **Venues are a user benefit only**, not revenue. B2B account management is kept. **Path50k is rebuilt with B2B as the primary line** and the consumer app as the product engine, showing hours per £ for each line | Group-trip fee and venue commission lines (D34) | Hours: every £50k path was ~420–440 h a year over budget |
| D38 | **More gates.** IP/invention clauses checked in both employment contracts. Incorporation, the ICO fee and public liability + PI insurance before the first paid client or trip. **A written founders/contributors agreement** (roles, hours, equity or compensation, IP assignment to the company) before anyone contributes work | D33 gate list | Founder decision |
| D39 | **Guardrail: never hold trip money; Stripe Connect direct charges only.** Added to `CLAUDE.md` | Proposed in Area 18 | FCA commercial agent exclusion |
| D40 | **After Test E:** a short decision note, B2B-first vs consumer-first, with hours, revenue and interview evidence (`decisions/b2b-vs-consumer-first.md`) | — | Founder request |
| D41 | **Team capacity is one input: extra helper hours per week, default 0.** Helpers cost 1.5 h a week of founder coordination. The model shows which £50k paths become feasible, and the helper hours each path needs. The earlier "3 helpers" assumption is removed | — | Founder sets it |
| D42 | **City-expansion gate:** London must pass usage, return-rate and stranger-K thresholds before the next city. Curation hours per new city are estimated (`decisions/city-expansion-gate.md`) | — | Founder request |
| D43 | **Friends and family are a separate launch channel.** K and every Phase 3 threshold are measured on **strangers only** | Friends excluded from the study | Keeps the evidence clean while using the warm network |
| D44 | **Automation scenario, built in Phase 4:** (1) fully self-serve onboarding; (2) an AI support agent with escalation (technical and payment issues wait for Abram; safety issues and complaints always go to a human promptly; AI disclosed, with an option to reach a person); (3) content generated from moments and shot cards, auto-scheduled on our own channels, with community-group posting kept manual. Build hours are added to Phase 4 and the £50k paths are recomputed | — | Hours are the wall |

## 2026-09-26 (Phase 3 round 2) — Legal gates, prices, new revenue lines

| # | Decision | Replaces | Why |
|---|---|---|---|
| D30 | **Phase 3 Tests A–D at ≈ 17 h with 12 participants** accepted. Abram confirms the 6 conjoint attributes and 16 swipe places this week | 15 h budget | Checkpoint 2 open question |
| D31 | **Test D annual prices: about two months free in both arms.** Arm A £4.99/month or **£49.99/year**; arm B £9.99/month or **£99.99/year** | £59.99/year in both arms (D25) | £59.99 was no discount in arm A |
| D32 | **Jev vs Claude tagging benchmark runs after v0**, not in Phase 4 | Proposed +1.5 h in Phase 4 | Hours |
| D33 | **Legal gates:** right to run a business **cleared** (confirmed by Abram). Remaining before taking any money: (1) Apple's outside-activities policy check, with disclosure if required and work kept on personal time and devices; (2) written secondary-employment approval from the government agency employer. Revenue can start once both are done | `CLAUDE.md` gate list (employer permission, right to run a business, IP clauses) | Founder update |
| D34 | **Phase 3 additions:** (1) trip payments research: Package Travel Regulations, payment splitting without holding money, safety duties (Area 18); (2) a free-first scenario in the workbook; (3) new revenue lines modelled and tested: **venue partnerships** (group discounts + commission, off-peak) and **B2B** (hotels, tourism boards, employers buying moment plans) at £200–500/month per client; (4) **5 B2B discovery interviews** (Test E); (5) a £50k path scenario with B2B clients and K = 0.3 | — | Founder request |
| D35 | **Seed moment 1 received** ("From the tube to the museum"). It is the Test A example shot card; exit, route, best time and shot position are to be filled in on one walk | D13 (5 seed moments) | First seed |

## Checkpoint 2 approval — Phase 3 go, virality, pricing test, tools

| # | Decision | Replaces | Why |
|---|---|---|---|
| D23 | **Measure referral and virality in Phase 3:** invites sent per user, invitees who sign up, shares of shot-card photos, and a computed K-factor. Test C plans get a **"bring a friend"** option, and there is a **share prompt after shot-card moments**. The workbook gets a K-factor input and a scenario showing the K needed for £50k at the founder's hours | — | Checkpoint 2: acquisition, not cost, decides viability |
| D24 | **Payment method deferred.** Check Telegram's rules on linking out to an external checkout, and note the app-store fees for a future native app | Open question | Telegram's link-out rule was UNVERIFIED |
| D25 | **Test D prices:** £4.99 vs £9.99 a month (random arm), plus £59.99 a year in both arms. Payment is asked for after one free plan. **Waitlist only, no money taken** (D1 still holds) | "Two price points if traffic allows" | Checkpoint 2 upside scenario |
| D26 | **Meta ad test deferred** until the Test A and B results are in | Open question | Don't spend before the product is shown to work |
| D27 | **Accept +2 h in Phase 4** for the design hooks: keep δ_person separate from b_population, and store trip-intent answers with each plan (≈1 h each). Phase 4 ≈38 h | Phase 4 ≈36 h (D14) | Areas 15 and 17: design now, build later |
| D28 | **Evaluate God's Eye View** (Area 14) for pre-trip moment previews and shot-card view previews. Analysis (isovists) stays on OSM/Overture in Python. **No tracking or CCTV layers.** Post-v0 only | — | Founder request |
| D29 | **Benchmark Jev (TypeSafe AI) against Claude** on moment feature tagging (Areas 2 and 13): 50 moments hand-labelled by the founder; accuracy and calibration. If calibrated, auto-accept high-confidence tags and route low-confidence ones to the founder | — | Founder request |

## Checkpoint 1 approval — Phase 2 go, thresholds, food, sources, recruitment

| # | Decision | Replaces | Why |
|---|---|---|---|
| D18 | **Checkpoint 1 approved.** Keep the six proposed Phase 3 thresholds. **Report every Test A metric split by voice vs text** | Thresholds "proposed" | Area 1: voice break-off risk |
| D19 | **Food:** one optional question, "Any foods or drinks you avoid?", with a one-line consent note. **No allergy question in v0** | `CLAUDE.md` "food needs (halal, vegetarian, allergies)" | Area 12: allergies are health data; halal may reveal religion |
| D20 | **Re-verify pricing and cost sources now**, before the economics model. Re-verify the other search-only sources when each note is revised | Open question | Phase 2 depends on prices |
| D21 | **Separate recruitment posts** for Tests A–D and for the weekend test. Weekend-trip attendees are invited to do Test A afterwards | Open question | Keeps the weekend test clean while reusing its attendees |
| D22 | **After Phase 2, light-scan five new areas:** 13 moment mining from text + data rights; 14 spatial moment detection (isovists, scenicness, building data); 15 travel motivation + per-trip intent (β_trip = β_person + trip adjustment); 16 home-contrast novelty (home city only); 17 on-device personalisation (b_person = b_population + δ_person, federated learning, differential privacy). Design now, build after Phase 3 | — | Founder request |

## 2026-09-26 (third round) — Hours, peak–end, photos

| # | Decision | Replaces | Why |
|---|---|---|---|
| D14 | **Shot cards only for the ~20 swipe and peak moments.** Keep LLM-written explanations. **Accept a Phase 4 estimate of about 36 hours** | Shot cards for all 50 moments; 35-hour budget | Option (a) from LOG.md |
| D15 | **Peak–end end-of-day bonus is off by default.** The planner maximises the sum of predicted moment satisfaction, and our ratings will test whether the bonus should be switched on | D8 left the default open | Area 6: peak–end is weak for multi-part experiences (Kemp et al. 2008; Strijbosch et al. 2019) |
| D16 | **Photo pairs dropped from the model and from Test A.** Instead, Test A adds two 1–5 questions: "How much do photos and sharing matter on your trips?" and "Would a shot card make you more likely to visit this moment?" | Onboarding layer (a), camera taste | Area 5: 10 examples add only +0.006 ρ over a generic model |
| D17 | **Review schedule.** Abram reviews the 15 moment features in the week of 28 Sep. The Areas 5–7 review moves to the week of 5 Oct | LOG.md weekly plan | Keeps weekly hours near 7.5 |

## 2026-09-26 (second round) — Moments, Python, place database

| # | Decision | Replaces | Why |
|---|---|---|---|
| D9 | **The unit of the database is a moment, not a place.** A moment = place + route/approach + best time + features + shot card. The swipe layer, planner and per-stop ratings work on moments | "~100 hand-tagged places" (D5 kept the count at 50) | Founder example: the South Kensington tube exit to the Natural History Museum reveal is the experience, not the museum |
| D10 | **New moment features:** contrast/reveal, absorption/flow, awe, social pull. Cost stays a raw £ input, and feeling-per-pound is derived by the model | Area 2's 12-attribute list | Founder design change. Evidence in Area 6 (Kaplan's mystery, Csikszentmihalyi's flow, Keltner's awe) |
| D11 | **v0 moments are hand-picked by the founder**, with no Overture bulk pull and no second tagger | Area 2 "Overture pull" and "tag reliability" steps | Hours (Phase 4 was estimated at 37 of 35) |
| D12 | **Prototype pinned to Python 3.12** | — | PyMC 6 and Biogeme 3.3 require ≥3.12 |
| D13 | **Five seed moments** come from the founder's own experience this week | — | Real examples to calibrate the schema before tagging the rest |

## 2026-09-26 — Test design, audio, v0 scope

| # | Decision | Replaces | Why |
|---|---|---|---|
| D1 | **Test D:** waitlist and stated price only, **no money taken**. A priced "Reserve founding spot" button leads to the waitlist with an honest note. Test two price points if traffic allows | "Small refundable deposit" | `CLAUDE.md` legal gates: no charging before employer permission, right to run a business and IP clauses are cleared |
| D2 | **Test D pass threshold:** ≥20% of sign-ups pick the priced option | "Any paid deposits ≥3" | Follows from D1 |
| D3 | **Audio:** delete after transcription by default. Opt-in 30-day retention, used only for transcription-accuracy spot-checks | — | `CLAUDE.md` guardrail; Area 1 risk (ASR hallucination and accent bias need spot-checks) |
| D4 | **Test A:** answer mode (voice/text) is a recorded variable. Report the choice, completion and "felt understood" for each mode | — | Area 1: voice answers are 2× longer but break-off is 45% vs 13% (Gavras & Höhne 2020) and 51% vs 24% (Höhne et al. 2024) |
| D5 | **Phase 4 scope cut:** 50 places (not ~100) | "~100 hand-tagged places" | Hours: onboarding and planner alone were estimated at 22 of 35 |
| D6 | **Phase 4 scope cut:** no photo taste in v0 | "Photo taste: basic embedding similarity" | Same |
| D7 | **Phase 4 scope cut:** feedback is log-only. Weight updates run offline, not live | "Simple Bayesian update of the person's weights" | Same |
| D8 | **Peak–end** stays as a planner toggle, not a hard guarantee | "guaranteeing one peak and a good finish" | Area 4: the tourism evidence is mixed. Test it on our own ratings |

## Phase 3 thresholds (confirmed: D2, D18)

| Metric | Pass |
|---|---|
| Onboarding completion | ≥ 70% (reported overall and by mode) |
| "Felt understood" | median ≥ 4/5 (reported overall and by mode) |
| Prefer personalised plan (blind) | ≥ 7 of 10 |
| Used the plan on a real day | ≥ 40% |
| Asked for a second plan within 2 weeks | ≥ 30% |
| Landing page visit → sign-up | ≥ 10% |
| Sign-ups choosing the priced option | ≥ 20% (confirmed, D2) |

Descriptive Test A measures with no pass threshold (D16): "How much do photos and sharing matter on your trips?" (1–5), and "Would a shot card make you more likely to visit this moment?" (1–5).

Descriptive virality measures with no pass threshold (D23): invites sent per participant, invitee sign-ups, shot-card shares, and K. They are compared with the K the workbook says £50k would need (`Virality` tab).
