# LOG

These are the founder's hours, not Claude's. Budget is **~7.5 hrs/week**. Claude fills in the estimates. The founder fills in actuals.

## Phase status

| Phase | Target | Budget (hrs) | Actual (hrs) | Status |
|---|---|---|---|---|
| 1 Research sweep | 2–3 wks | 15 | | **In progress**: areas 1 and 4 drafted and waiting for review. Next: areas 2 and 3 |
| 2 Unit economics | 1 wk | 5 | — | Not started |
| 3 Validation | 2–3 wks | 15 | — | Not started. Pass thresholds to be confirmed by founder before any test runs |
| 4 Prototype v0 | 4–5 wks | 35 | — | Gated: only if Phase 3 passes |
| 5 Test v0 and decide | 2 wks | 10 | — | Not started |
| **Total** | **11–14 wks** | **80** | | 80 hrs ÷ 7.5 hrs/wk ≈ 10.7 wks, so there is little slack |

## Phase 1 areas

The founder's hours below are for reviewing each note and skimming its 1–2 key sources.

| # | Note | Depth | Est. (hrs) | Actual (hrs) | Status |
|---|---|---|---|---|---|
| 1 | `01-onboarding.md` | Critical | 2.0 | | Drafted 2026-09-26: 38 sources |
| 4 | `04-itinerary.md` | Critical | 2.0 | | Drafted 2026-09-26: 27 sources |
| 2 | `02-place-preferences.md` | Critical | 2.0 | | Next |
| 3 | `03-personal-weights.md` | Critical | 2.0 | | Next |
| 5 | `05-photo-taste.md` | Lighter | 1.0 | | |
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

| Component | Est. (hrs) | Source |
|---|---|---|
| Onboarding: Telegram bot, transcription, read-back, extraction, gold-set check | 10 | Area 1 |
| Planner: travel-time matrices, OR-Tools model, peak/finish, weather, tests, explanation | 12 | Area 4 |
| **Running total** | **22 of 35** | Place DB, scoring, feedback loop and photo taste still to estimate. Scope may need cutting |

## Hours log

| Date | Phase | Activity | Est. (hrs) | Actual (hrs) | Notes |
|---|---|---|---|---|---|
| 2026-09-26 | 1 | Kickoff: write brief and `CLAUDE.md`, review repo setup and plan | 1.0 | | |
| — | 1 | Review `01-onboarding.md` and `04-itinerary.md` | 4.0 | | Pending |

## Weekly totals

| Week of (Mon) | Budget | Est. | Actual |
|---|---|---|---|
| 2026-09-21 | 7.5 | 1.0 | |

## Open questions

1. **Network access.** The environment's network policy blocks most research hosts (arxiv.org, dl.acm.org, huggingface.co, developers.google.com, api.tfl.gov.uk, open-meteo.com, journals.sagepub.com, vendor pricing pages). Most sources are therefore verified from search results only (`verified=search`). Widening network access would allow a pass against the primary pages.
2. **Test D vs the legal gates.** `CLAUDE.md` says no charging anyone until the legal gates clear. Test D's refundable deposit is a charge. Options: clear the gates first, run Test D as a waitlist with a stated price only, or treat a refundable deposit as allowed (the founder should confirm with the employer).
3. **Test A audio.** Keep recordings for a short fixed period (explicit opt-in) to measure transcription accuracy, or delete immediately after transcription?
4. **Test A voice vs text.** Let participants choose, or randomise? Evidence says voice loses more people (Area 1).
5. **Phase 3 pass thresholds** are proposed but not yet confirmed.
6. **Weekend test.** Should Tests A–D recruit from the same posts as the weekend test, or from separate ones (`CLAUDE.md`: run alongside, don't replace)?
