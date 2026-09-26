# LOG

These are the founder's hours, not Claude's. Budget is **~7.5 hrs/week**. Claude fills in the estimates. The founder fills in actuals.

## Phase status

| Phase | Target | Budget (hrs) | Est. (hrs) | Actual (hrs) | Status |
|---|---|---|---|---|---|
| 1 Research sweep | 2–3 wks | 15 | ≈ 18.5 | | **Approved** at Checkpoint 1 (D18). Full reviews of the notes continue in the weeks of 28 Sep and 5 Oct |
| 2 Unit economics | 1 wk | 5 | 5 | | **At Checkpoint 2.** `economics/unit-economics.xlsx`, `economics/assumptions.md` and `decisions/phase-2-summary.md` are drafted. Waiting for approval |
| 1b Light scans, Areas 13–17 | — | — | 2.5 | | Requested at Checkpoint 1 (D22). Design now, build after Phase 3 |
| 3 Validation | 2–3 wks | 15 | 15 | — | Not started. Thresholds confirmed (D18). Needs Checkpoint 2 approval |
| 4 Prototype v0 | 4–5 wks | 35 | ≈ 36 | — | Gated: only if Phase 3 passes. 36 h accepted (D14) |
| 5 Test v0 and decide | 2 wks | 10 | 10 | — | Not started |
| **Total** | **11–14 wks** | **80** | **≈ 87** | | 87 ÷ 7.5 ≈ 11.6 weeks: inside the window, with little slack |

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

## Areas 13–17 (light scans, D22): design now, build after Phase 3

| # | Note | Review (hrs) | Build later (hrs) | Status |
|---|---|---|---|---|
| 13 | `13-moment-mining.md` | 0.5 | ~6 (pilot on Wikivoyage + Geograph) | Drafted: 9 sources. Reddit and Tripadvisor ruled out on their terms |
| 14 | `14-spatial-moments.md` | 0.5 | 8–10 (2D isovist reveal score + scenicness prior) | Drafted: 10 sources |
| 15 | `15-travel-motivation.md` | 0.5 | ~1 in Phase 4 (store intent) + 4–6 later | Drafted: 6 sources |
| 16 | `16-home-contrast-novelty.md` | 0.5 | 4–6 | Drafted: 3 sources (plus Areas 12 and 14) |
| 17 | `17-on-device-personalisation.md` | 0.5 | ~1 in Phase 4 (separate δ) + 8–12 on device + 20–30 federated/DP, needs a native app | Drafted: 7 sources |
| | **Total** | **2.5** | **~2 in Phase 4; ~50–70 later** | The ~2 h design hooks raise Phase 4 from ≈36 h to **≈38 h**, unless Abram drops something else (open question 7) |

Sources now total 231 in `research/sources.csv`: 121 read on the page, 107 through search only, 3 UNVERIFIED.

## Phase 4 build estimate (founder hours, assuming Claude Code writes most code)

Scope decisions: D5–D8, D11, D14–D16 and D19. That means 50 hand-picked moments, shot cards for ~20, no photo taste, log-only feedback, peak–end off by default, and no allergy question.

| Component | Est. (hrs) | Source |
|---|---|---|
| Onboarding: Telegram bot, transcription, read-back, extraction, gold-set check | 10 | Area 1 |
| Planner: asymmetric matrices (50 moments), OR-Tools model, end-bonus toggle, weather and UTCI, tests, LLM explanation | 11 | Areas 4, 6 |
| Moment DB: schema, seed session, LLM-drafted cards plus review, shot cards for ~20, swipe-set selection | 5 | Area 2 |
| Weights and scoring: per-user Laplace posterior, scoring, offline HB refit (PyMC) | 6 | Area 3 |
| Feedback logging (D7) | 2 | Estimate |
| Privacy notice, audio deletion, data-deletion command | 2 | Area 12 |
| **Total** | **≈ 36** | Accepted (D14) |

Phase 3 carries about 2 h for the conjoint design (Area 3) and about 2 h for the consent form and privacy notice (Area 12), inside its 15 h.

## Hours log

| Date | Phase | Activity | Est. (hrs) | Actual (hrs) | Notes |
|---|---|---|---|---|---|
| 2026-09-26 | 1 | Kickoff: write brief and `CLAUDE.md`, review repo setup and plan | 1.0 | | |
| 2026-09-26 | 1 | Skim Areas 1 and 4, decisions D1–D8, widen network access | 1.0 | | |
| 2026-09-26 | 1 | Decisions D9–D13 (moments, Python 3.12, hand-picking) | 0.5 | | |
| 2026-09-26 | 1 | Decisions D14–D17 (hours, peak–end, photos, schedule) | 0.5 | | |
| 2026-09-26 | 1 | Read Checkpoint 1 summary and approve | 1.5 | | Done early |
| 2026-09-26 | 2 | Decisions D18–D22 | 0.5 | | |
| wk 28 Sep | 1 | Review Areas 1–4 in full, including the 15 moment features (D17) | 7.0 | | Pending |
| wk 28 Sep | 1 | Write up 5 seed moments in the Area 2 schema (D13) | 1.0 | | Pending |
| wk 5 Oct | 1 | Review Areas 5–7 (D17) | 3.0 | | Pending |
| wk 5 Oct | 1 | Review Areas 8–12 light scans | 2.5 | | Pending |
| wk 5 Oct | 2 | Read Checkpoint 2 summary and decide | 1.5 | | Pending |
| wk 12 Oct | 2 | Review workbook GUESS inputs and `assumptions.md` | 3.0 | | Pending |
| wk 12 Oct | 1b | Review Areas 13–17 light scans | 2.5 | | Pending |

## Weekly totals

| Week of (Mon) | Budget | Est. | Actual |
|---|---|---|---|
| 2026-09-21 | 7.5 | 5.0 | |
| 2026-09-28 | 7.5 | 8.0 (Areas 1–4 review 7, seed moments 1) | |
| 2026-10-05 | 7.5 | 7.0 (Areas 5–12 reviews 5.5, Checkpoint 2 1.5) | |
| 2026-10-12 | 7.5 | 5.5 (workbook 3, Areas 13–17 2.5). Phase 3 can start with the remaining 2 h | |

## Decisions

See [`decisions/decision-log.md`](decisions/decision-log.md).
- D1–D8: Test D takes no money; audio retention opt-in for 30 days; answer mode is a Test A variable; v0 scope cut; peak–end is a toggle.
- D9–D13: moments are the unit; new moment features; moments hand-picked; Python 3.12; 5 seed moments.
- D14–D17: shot cards for ~20 moments and ~36 h accepted; end bonus off by default; photo pairs replaced by two Test A questions; review schedule.
- D18–D22: Checkpoint 1 approved and thresholds kept, with Test A split by voice vs text; one optional "foods or drinks you avoid" question; pricing re-verified before the model; separate recruitment posts; light scans of Areas 13–17.

## Open questions

1. **Checkpoint 2.** Approve moving to Phase 3 (validation)?
2. **Payment channel.** Web checkout through Stripe (keeps ~94% of the price), or Telegram Stars (~62%)? Whether a bot may link out to a web checkout is UNVERIFIED.
3. **Test D prices.** Test £4.99 vs £9.99 a month (with £29.99 vs £59.99 a year) and a hard paywall after the first free plan?
4. **Paid ad test.** Spend ~£50–100 on Meta to measure cost per click and visit-to-sign-up? This spends money but takes none, so the legal gates don't block it.
5. **Conjoint attributes (Area 3).** Confirm 5–6 attributes and levels.
6. **Moment features (Area 2).** Abram is reviewing these in the week of 28 Sep (D17).
7. **Design hooks for Areas 15 and 17.** Storing trip-intent answers and keeping δ_person separate add ~2 h to Phase 4 (≈38 h). Accept, or defer them?

Resolved 2026-09-26: network access; Test D vs legal gates (D1/D2); Test A audio (D3); voice vs text (D4); Python version (D12); place DB sourcing (D11); Phase 4 budget (D14); peak–end default (D15); photo pairs (D16); Checkpoint 1 and thresholds (D18); food question (D19); source re-verification (D20); recruitment posts (D21).
