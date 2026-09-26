# Decision log

Founder decisions that amend `KICKOFF_PROMPT.md`. Newest first. Where this log and the kickoff brief disagree, this log wins.

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
