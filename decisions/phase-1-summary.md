# Checkpoint 1 — Phase 1 research summary

*2026-09-26. Twelve notes in `research/notes/`. There are 176 sources in `research/sources.csv`: 74 read on the page, 99 confirmed through search results only, 3 marked UNVERIFIED. Decisions D1–D17 are in `decisions/decision-log.md`.*

## Recommended v0 stack

| Layer | v0 choice | Why (evidence) | Running cost | Build hrs |
|---|---|---|---|---|
| Channel | **Telegram bot** (aiogram, MIT) | Free. Voice notes are push-to-talk, so no turn detection is needed. Inline buttons give one-tap ratings (Areas 1, 8) | £0 | in onboarding |
| Transcription | Hosted API (gpt-4o-mini-transcribe ~$0.003/min, or Deepgram Nova-3 ~$0.0043/min), with **read-back** | Cheap. Whisper invents phrases in ~1% of transcripts, so the user confirms what was heard (Area 1) | ~$0.03 per onboarding | in onboarding |
| Extraction | LLM with structured output → **quoted evidence records**, never numeric βs | Format is guaranteed, but LLM numeric ratings drift between runs (Area 1) | tokens (Phase 2) | in onboarding |
| **Onboarding total** | voice or text, choice recorded (D4) | | | **10** |
| Moment DB | **50 hand-picked moments** (D9, D11): Overture IDs, approach, best time, 15 features; shot cards for ~20 (D14) | No open dataset of how places *feel*. Google Places content can't be stored (Area 2) | £0 | **5** |
| Weights | **Hierarchical Bayes in PyMC** (offline refits) + a per-user Laplace posterior. Test A conjoint: 10 tasks, fixed D-efficient design | 10 choices roughly halve individual error in Train's simulation. Adaptive designs hurt population estimates (Area 3) | £0 | **6** (+2 in Phase 3) |
| Planner | **OR-Tools** orienteering with time windows. Asymmetric matrices: OSRM/openrouteservice walking + TfL Journey Planner transit. Met Office DataHub + UTCI. **End bonus off** (D15) | LLMs alone pass 0.6% of TravelPlanner tasks; with a solver, 93.9%. Peak–end is weak for multi-part days (Areas 4, 6) | £0 at v0 scale | **11** |
| Feedback | One-tap rating per moment, logged with conditions; offline refit (D7) | The most valuable data. Expected ≠ experienced utility (Area 2) | £0 | **2** |
| Privacy | Notice, audio deletion (D3), delete command. **Transcript only, no voice-emotion analysis.** Allergies and halal optional, with consent | UK GDPR special category; EU AI Act Art 50 (Area 12) | £0 | **2** |
| Runtime | Python 3.12 (D12), FastAPI | PyMC 6 and Biogeme 3.3 need ≥3.12 | hosting (Phase 2) | — |
| **Total** | | | | **≈ 36 h** (accepted, D14) |

**Out of v0:** video or avatar host, live voice, photo taste (D6, D16), wearables, WhatsApp, Live Activities, companion matching, payments.

## How Phase 1 changed the plan

- **The unit is a moment, not a place.** Approach and timing are part of the product, and no competitor curates moments for city leisure (Area 7).
- **Typing is an equal option.** Asking for voice answers caused 45–51% break-off vs 13–24% for text in surveys.
- **Peak–end off by default, photo pairs out.** Both were weaker than assumed.
- **No age filters on day trips.** The Equality Act age exception needs overnight or >24h trips. Allergies and halal are special category data.

## The three biggest unknowns, and the test that answers each

1. **Will strangers finish a conversational onboarding and feel understood?** LLM interviews get longer, richer answers, and 55% would choose another AI interview. But voice loses people. → **Test A**, by mode: ≥70% completion, median "felt understood" ≥4/5.
2. **Does a plan built from ~10 choices + swipes + one story beat a generic plan for a stranger?** Individual error only halves at 10 choices. Stated preference ≠ experienced enjoyment. Fewer than 10% of LLM itineraries reach human level. → **Test B**: blind preference ≥7 of 10.
3. **Will people use it, come back and pay, when AI itineraries are free, and will strangers turn up?** Google and Mindtrip plan for free. Free events see about 28% no-shows, and money can't be taken yet (legal gates). → **Tests C and D**, plus the weekend test.

## Hours

| | Budget | Estimate |
|---|---|---|
| Phase 1 (founder) | 15 | **≈ 18.5**: 3 rounds of decisions (+2.5 h) and seed moments (+1 h) were added |
| Phase 4 build | 35 | **≈ 36** (accepted) |

Phase 1 ends when the Areas 5–12 reviews and this checkpoint are done, in the week of 5 Oct. That is within the 2–3 week target.

## Open questions for approval

1. Approve moving to **Phase 2 (unit economics)**?
2. The six Phase 3 thresholds other than the Test D row are still unconfirmed.
3. Food needs: keep asking about allergies and halal (with explicit consent), or ask only "foods you avoid"?
4. The 99 search-only sources: re-verify now (Claude time only), or when each note is revised?
