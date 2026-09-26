# LOG

These are the founder's hours, not Claude's. Budget is **~7.5 hrs/week**. Claude fills in the estimates. The founder fills in actuals.

## Phase status

| Phase | Target | Budget (hrs) | Actual (hrs) | Status |
|---|---|---|---|---|
| 1 Research sweep | 2–3 wks | 15 | | **In progress**: areas 1–7 drafted and waiting for review. Next: light scans of areas 8–12, then Checkpoint 1 |
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
| 2 | `02-place-preferences.md` | Critical | 2.0 | | Drafted 2026-09-26; revised for moments (D9) with schema: 26 sources |
| 3 | `03-personal-weights.md` | Critical | 2.0 | | Drafted 2026-09-26: 17 sources (12 fetched) |
| 5 | `05-photo-taste.md` | Lighter | 1.0 | | Drafted 2026-09-26: 6 sources |
| 6 | `06-wellbeing.md` | Lighter | 1.0 | | Drafted 2026-09-26: 22 sources; peak–end evidence settled (weak for complex experiences) |
| 7 | `07-existing-products.md` | Lighter | 1.0 | | Drafted 2026-09-26: 13 sources; includes the "who curates moments" answer |
| 8 | `08-seamless-interaction.md` | Light scan | 0.5 | | Next |
| 9 | `09-body-signals.md` | Light scan | 0.5 | | |
| 10 | `10-money.md` | Light scan | 0.5 | | |
| 11 | `11-companion-matching.md` | Light scan | 0.5 | | |
| 12 | `12-legal-ethics.md` | Light scan | 0.5 | | |
| — | `decisions/phase-1-summary.md` (Checkpoint 1) | Review | 1.5 | | |
| | **Phase 1 total** | | **15.0** | | |

## Build-hour estimates so far (for Phase 4, founder hours, assuming Claude Code writes most code)

Scope was cut on 2026-09-26 (decisions D5–D8, D11): 50 hand-picked moments, no photo taste, log-only feedback, peak–end as a toggle.

| Component | Est. (hrs) | Source |
|---|---|---|
| Onboarding: Telegram bot, transcription, read-back, extraction, gold-set check | 10 | Area 1 |
| Planner: asymmetric travel-time matrices (50 moments), OR-Tools model, peak/finish toggle, weather and UTCI, tests, explanation | 11 | Areas 4, 6 |
| Moment DB: schema, seed-moment session, LLM-drafted cards (approach, best time, shot card) plus review for 45 more, swipe-set selection | 6.5 | Area 2 |
| Weights and scoring: per-user Laplace posterior, scoring function, offline HB refit (PyMC) | 6 | Area 3 |
| Feedback logging (log-only, D7) | 2 | Estimate |
| Privacy notice, raw-audio deletion, data-deletion command | 2 | Estimate |
| **Running total** | **37.5 of 35** | **About 2.5 hours over** (see note below) |

**Correction.** My earlier "hand-pick and drop the second tagger saves 2 hours" was wrong. The second tagger (1 h) was never inside the 6-hour estimate. Hand-picking saves the 1-hour Overture pull, and moment cards cost about +1.5 h over place tags (approach, best time, shot card).

**Options to reach 35:**
- (a) Shot cards only for the ~20 swipe and peak moments: −1.5 h.
- (b) Templated explanations built from the solver's structured diff, instead of LLM-written ones: −0.5 h.
- (c) Accept about 37.5.

Phase 3 needs about 2 hours for the conjoint design (Area 3), inside Phase 3's 15.

## Hours log

| Date | Phase | Activity | Est. (hrs) | Actual (hrs) | Notes |
|---|---|---|---|---|---|
| 2026-09-26 | 1 | Kickoff: write brief and `CLAUDE.md`, review repo setup and plan | 1.0 | | |
| 2026-09-26 | 1 | Skim Areas 1 and 4, make decisions D1–D8, widen network access | 1.0 | | Full review of the notes still pending |
| — | 1 | Review `01-onboarding.md` and `04-itinerary.md` in full | 3.0 | | Pending |
| — | 1 | Review `02-place-preferences.md` and `03-personal-weights.md`; confirm attribute lists | 4.0 | | Pending |
| 2026-09-26 | 1 | Decisions D9–D13 (moments, Python 3.12, hand-picking) | 0.5 | | |
| — | 1 | Write up 5 seed moments from this week, in the Area 2 schema | 1.0 | | Pending (D13) |
| — | 1 | Review `05`, `06` and `07` notes | 3.0 | | Pending |

## Weekly totals

| Week of (Mon) | Budget | Est. | Actual |
|---|---|---|---|
| 2026-09-21 | 7.5 | 2.5 | |
| 2026-09-28 | 7.5 | **11.0** (reviews of Areas 1–7 = 10, seed moments = 1) | |

The 2026-09-28 week is **3.5 hours over budget** if all reviews happen that week. Suggest reviewing Areas 1–4 (7 h) plus the seed moments (1 h) that week, and pushing the Areas 5–7 review (3 h) into the following week alongside the light scans.

## Decisions

See [`decisions/decision-log.md`](decisions/decision-log.md).
- D1–D8 (2026-09-26): Test D takes no money, audio retention is opt-in for 30 days, answer mode is a Test A variable, the v0 scope is cut, and peak–end is a toggle.
- D9–D13 (2026-09-26, second round): moments are the unit, new moment features, hand-picked moments, Python 3.12, and 5 seed moments from Abram.

## Open questions

1. **Phase 3 pass thresholds.** The Test D row is confirmed (D2). The other six are proposed and not yet confirmed (see the decision log).
2. **Weekend test.** Should Tests A–D recruit from the same posts as the weekend test, or from separate ones (`CLAUDE.md`: run alongside, don't replace)?
3. **Search-only sources.** Many Area 1 and 4 rows are still `verified=search`. The four headline stats are now `fetched`. Should the rest be re-verified now (about 1–2 hours of Claude time, no founder hours) or only when a note is revised?
4. **Moment features (Area 2).** Confirm or edit the 11 place attributes + 4 moment features, each scored 0–2, plus cost in £.
5. **Conjoint attributes (Area 3).** Confirm 5–6 attributes and levels, e.g. transfer 15/30/50 min, one hot hour yes/no, 3 vs 5 stops, crowds low/high, £20/£40/£60, walking low/high.
6. **Phase 4 budget.** The estimate is 37.5 hrs against 35. Choose from (a) shot cards for ~20 moments only, (b) templated explanations, (c) accept.
7. **Peak–end default (Area 6).** Should the end-bonus toggle start **off**? The evidence is weak for multi-part experiences. Our ratings would then test whether it should be switched on.
8. **Photo pairs in Test A (Area 5).** Keep the optional photo pairs, or drop them? Ten examples barely beat a generic model (+0.006 ρ).

Resolved 2026-09-26:
- Network access was widened.
- Test D vs the legal gates → D1/D2.
- Test A audio → D3.
- Voice vs text → D4 (participants choose, and mode is recorded).
- Python version → D12 (3.12).
- Place DB sourcing → D11 (hand-picked, no second tagger).
