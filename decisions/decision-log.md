# Decision log

Founder decisions that amend `KICKOFF_PROMPT.md`. Newest first. Where this log and the kickoff brief disagree, this log wins.

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

## Proposed Phase 3 thresholds after D2 (other rows still await confirmation)

| Metric | Pass |
|---|---|
| Onboarding completion | ≥ 70% (reported overall and by mode) |
| "Felt understood" | median ≥ 4/5 (reported overall and by mode) |
| Prefer personalised plan (blind) | ≥ 7 of 10 |
| Used the plan on a real day | ≥ 40% |
| Asked for a second plan within 2 weeks | ≥ 30% |
| Landing page visit → sign-up | ≥ 10% |
| Sign-ups choosing the priced option | ≥ 20% (confirmed, D2) |
