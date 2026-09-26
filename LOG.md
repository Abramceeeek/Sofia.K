# LOG

These are the founder's hours, not Claude's. Budget is **~7.5 hrs/week**. Claude fills in the estimates. The founder fills in actuals.

## Phase status

| Phase | Target | Budget (hrs) | Est. (hrs) | Actual (hrs) | Status |
|---|---|---|---|---|---|
| 1 Research sweep | 2–3 wks | 15 | ≈ 18.5 | | **At Checkpoint 1.** All 12 notes and `decisions/phase-1-summary.md` are drafted. Waiting for approval |
| 2 Unit economics | 1 wk | 5 | 5 | — | Not started. Needs Checkpoint 1 approval |
| 3 Validation | 2–3 wks | 15 | 15 | — | Not started. Six of the seven pass thresholds are still to be confirmed |
| 4 Prototype v0 | 4–5 wks | 35 | ≈ 36 | — | Gated: only if Phase 3 passes. 36 h accepted (D14) |
| 5 Test v0 and decide | 2 wks | 10 | 10 | — | Not started |
| **Total** | **11–14 wks** | **80** | **≈ 84.5** | | 84.5 ÷ 7.5 ≈ 11.3 weeks: inside the 11–14 week window, but with little slack |

## Phase 1 areas

The founder's hours below are for reviewing each note and skimming its 1–2 key sources.

| # | Note | Depth | Est. (hrs) | Actual (hrs) | Status |
|---|---|---|---|---|---|
| 1 | `01-onboarding.md` | Critical | 2.0 | | Drafted: 39 sources, key stats re-verified |
| 2 | `02-place-preferences.md` | Critical | 2.0 | | Drafted and revised for moments (D9): 26 sources |
| 3 | `03-personal-weights.md` | Critical | 2.0 | | Drafted: 17 sources |
| 4 | `04-itinerary.md` | Critical | 2.0 | | Drafted: 26 sources, key stats re-verified |
| 5 | `05-photo-taste.md` | Lighter | 1.0 | | Drafted: 6 sources |
| 6 | `06-wellbeing.md` | Lighter | 1.0 | | Drafted: 22 sources |
| 7 | `07-existing-products.md` | Lighter | 1.0 | | Drafted: 13 sources |
| 8 | `08-seamless-interaction.md` | Light scan | 0.5 | | Drafted: 7 sources |
| 9 | `09-body-signals.md` | Light scan | 0.5 | | Drafted: 5 sources |
| 10 | `10-money.md` | Light scan | 0.5 | | Drafted: 6 sources |
| 11 | `11-companion-matching.md` | Light scan | 0.5 | | Drafted: 3 sources |
| 12 | `12-legal-ethics.md` | Light scan | 0.5 | | Drafted: 6 sources |
| — | `decisions/phase-1-summary.md` (Checkpoint 1) | Review | 1.5 | | Drafted |
| | Decision rounds (D1–D17) and seed moments | — | 3.5 | | Not in the original 15 h |
| | **Phase 1 total** | | **≈ 18.5** | | 3.5 h over the 15 h budget |

Sources: 176 in `research/sources.csv`, of which 74 were read on the page, 99 confirmed through search results only, and 3 are UNVERIFIED.

## Phase 4 build estimate (founder hours, assuming Claude Code writes most code)

Scope decisions: D5–D8, D11, D14–D16. That means 50 hand-picked moments, shot cards for ~20, no photo taste, log-only feedback, and peak–end off by default.

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
| wk 28 Sep | 1 | Review Areas 1–4 in full, including the 15 moment features (D17) | 7.0 | | Pending |
| wk 28 Sep | 1 | Write up 5 seed moments in the Area 2 schema (D13) | 1.0 | | Pending |
| wk 5 Oct | 1 | Review Areas 5–7 (D17) | 3.0 | | Pending |
| wk 5 Oct | 1 | Review Areas 8–12 light scans | 2.5 | | Pending |
| wk 5 Oct | 1 | Review Checkpoint 1 summary and approve or redirect | 1.5 | | Pending |

## Weekly totals

| Week of (Mon) | Budget | Est. | Actual |
|---|---|---|---|
| 2026-09-21 | 7.5 | 3.0 | |
| 2026-09-28 | 7.5 | 8.0 (Areas 1–4 review 7, seed moments 1) | |
| 2026-10-05 | 7.5 | 7.0 (Areas 5–12 reviews 5.5, checkpoint 1.5) | |

## Decisions

See [`decisions/decision-log.md`](decisions/decision-log.md).
- D1–D8: Test D takes no money; audio retention opt-in for 30 days; answer mode is a Test A variable; v0 scope cut; peak–end is a toggle.
- D9–D13: moments are the unit; new moment features; moments hand-picked; Python 3.12; 5 seed moments.
- D14–D17: shot cards for ~20 moments and ~36 h accepted; end bonus off by default; photo pairs replaced by two Test A questions; review schedule.

## Open questions

1. **Checkpoint 1.** Approve moving to Phase 2 (unit economics)?
2. **Phase 3 pass thresholds.** The Test D row is confirmed (D2). The other six are proposed, not confirmed.
3. **Weekend test.** Should Tests A–D recruit from the same posts as the weekend test, or separate ones?
4. **Food needs (Area 12).** Keep allergies and halal (special category data, which needs explicit consent), or ask only "foods you avoid"?
5. **Search-only sources.** Re-verify the 99 `search` rows now (Claude time only), or when each note is revised?
6. **Conjoint attributes (Area 3).** Confirm 5–6 attributes and levels.
7. **Moment features (Area 2).** Abram is reviewing these in the week of 28 Sep (D17).

Resolved 2026-09-26: network access; Test D vs legal gates (D1/D2); Test A audio (D3); voice vs text (D4); Python version (D12); place DB sourcing (D11); Phase 4 budget (D14); peak–end default (D15); photo pairs (D16).
