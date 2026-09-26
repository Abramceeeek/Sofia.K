# LOG

These are the founder's hours, not Claude's. Budget is **~7.5 hrs/week**. Claude fills in the estimates. The founder fills in actuals.

## Phase status

| Phase | Target | Budget (hrs) | Actual (hrs) | Status |
|---|---|---|---|---|
| 1 Research sweep | 2–3 wks | 15 | | **In progress**: critical-path areas 1–4 drafted and waiting for review. Next: areas 5–7 (lighter pass) |
| 2 Unit economics | 1 wk | 5 | — | Not started |
| 3 Validation | 2–3 wks | 15 | — | Not started. Pass thresholds to be confirmed by founder before any test runs |
| 4 Prototype v0 | 4–5 wks | 35 | — | Gated: only if Phase 3 passes |
| 5 Test v0 and decide | 2 wks | 10 | — | Not started |
| **Total** | **11–14 wks** | **80** | | 80 hrs ÷ 7.5 hrs/wk ≈ 10.7 wks, so there is little slack |

## Phase 1 areas

The founder's hours below are for reviewing each note and skimming its 1–2 key sources.

| # | Note | Depth | Est. (hrs) | Actual (hrs) | Status |
|---|---|---|---|---|---|
| 1 | `01-onboarding.md` | Critical | 2.0 | | Drafted 2026-09-26: 39 sources, key stats re-verified |
| 4 | `04-itinerary.md` | Critical | 2.0 | | Drafted 2026-09-26: 26 sources, key stats re-verified |
| 2 | `02-place-preferences.md` | Critical | 2.0 | | Drafted 2026-09-26: 24 sources (15 fetched) |
| 3 | `03-personal-weights.md` | Critical | 2.0 | | Drafted 2026-09-26: 17 sources (12 fetched) |
| 5 | `05-photo-taste.md` | Lighter | 1.0 | | Next. Photo taste is out of v0 (D6), so this stays a light pass |
| 6 | `06-wellbeing.md` | Lighter | 1.0 | | Must settle the peak–end evidence (see Area 4) |
| 7 | `07-existing-products.md` | Lighter | 1.0 | | |
| 8 | `08-seamless-interaction.md` | Light scan | 0.5 | | |
| 9 | `09-body-signals.md` | Light scan | 0.5 | | |
| 10 | `10-money.md` | Light scan | 0.5 | | |
| 11 | `11-companion-matching.md` | Light scan | 0.5 | | |
| 12 | `12-legal-ethics.md` | Light scan | 0.5 | | |
| — | `decisions/phase-1-summary.md` (Checkpoint 1) | Review | 1.5 | | |
| | **Phase 1 total** | | **15.0** | | |

## Build-hour estimates so far (for Phase 4, founder hours, assuming Claude Code writes most code)

Scope was cut on 2026-09-26 (decisions D5–D8): 50 places, no photo taste, log-only feedback, peak–end as a toggle.

| Component | Est. (hrs) | Source |
|---|---|---|
| Onboarding: Telegram bot, transcription, read-back, extraction, gold-set check | 10 | Area 1 |
| Planner: travel-time matrices (50 places), OR-Tools model, peak/finish toggle, weather, tests, explanation | 11 | Area 4 |
| Place DB: Overture pull, 12-attribute schema, LLM-drafted tags plus review of 50 places, swipe-set selection | 6 | Area 2 |
| Weights and scoring: per-user Laplace posterior, scoring function, offline HB refit (PyMC) | 6 | Area 3 |
| Feedback logging (log-only, D7) | 2 | Estimate |
| Privacy notice, raw-audio deletion, data-deletion command | 2 | Estimate |
| **Running total** | **37 of 35** | **About 2 hours over.** Options: drop the second tagger and the Overture pull (hand-pick 50 places), −2 h; or accept 37 |

Phase 3 needs about 2 hours for the conjoint design (Area 3), inside Phase 3's 15.

## Hours log

| Date | Phase | Activity | Est. (hrs) | Actual (hrs) | Notes |
|---|---|---|---|---|---|
| 2026-09-26 | 1 | Kickoff: write brief and `CLAUDE.md`, review repo setup and plan | 1.0 | | |
| 2026-09-26 | 1 | Skim Areas 1 and 4, make decisions D1–D8, widen network access | 1.0 | | Full review of the notes still pending |
| — | 1 | Review `01-onboarding.md` and `04-itinerary.md` in full | 3.0 | | Pending |
| — | 1 | Review `02-place-preferences.md` and `03-personal-weights.md`; confirm attribute lists | 4.0 | | Pending |

## Weekly totals

| Week of (Mon) | Budget | Est. | Actual |
|---|---|---|---|
| 2026-09-21 | 7.5 | 2.0 | |
| 2026-09-28 | 7.5 | 7.0 (reviews of Areas 1–4) | |

## Decisions

See [`decisions/decision-log.md`](decisions/decision-log.md). D1–D8 were decided on 2026-09-26: Test D takes no money, audio retention is opt-in for 30 days, answer mode is a Test A variable, the v0 scope is cut, and peak–end is a toggle.

## Open questions

1. **Phase 3 pass thresholds.** The Test D row is confirmed (D2). The other six are proposed and not yet confirmed (see the decision log).
2. **Weekend test.** Should Tests A–D recruit from the same posts as the weekend test, or from separate ones (`CLAUDE.md`: run alongside, don't replace)?
3. **Search-only sources.** Many Area 1 and 4 rows are still `verified=search`. The four headline stats are now `fetched`. Should the rest be re-verified now (about 1–2 hours of Claude time, no founder hours) or only when a note is revised?
4. **Place attributes (Area 2).** Confirm or edit the proposed 12 experiential attributes, each scored 0–2.
5. **Conjoint attributes (Area 3).** Confirm 5–6 attributes and levels, e.g. transfer 15/30/50 min, one hot hour yes/no, 3 vs 5 stops, crowds low/high, £20/£40/£60, walking low/high.
6. **Phase 4 budget.** The estimate is 37 hrs against 35. Cut the 2 hours from the place DB, or accept the overrun?
7. **Python version.** PyMC 6 and Biogeme 3.3 need Python ≥3.12. OK to pin the prototype to 3.12?

Resolved 2026-09-26:
- Network access was widened.
- Test D vs the legal gates → D1/D2.
- Test A audio → D3.
- Voice vs text → D4 (participants choose, and mode is recorded).
