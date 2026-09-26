# Kickoff prompt — paste this into Claude Code

Read `CLAUDE.md` in full first. It is the project context and its working rules apply throughout.

## Mission

Take the travel app from idea to a **decision backed by evidence**: research what already exists, model the unit economics, test whether real people like the onboarding and would use the app, build a minimal prototype only if the tests justify it, and finish with a go / iterate / stop memo.

Work in phases. **At the end of each phase, stop, summarise results in under 300 words, list open questions, and wait for my approval before continuing.** Track estimated and actual hours for my time in `LOG.md` (my budget is ~7.5 hrs/week).

## Repo structure to create

```
/research/notes/        one markdown note per area (01-onboarding.md …)
/research/sources.csv   every source: area, type, title, url, date accessed, key finding, use/adapt/skip
/economics/             unit-economics model (.xlsx) + assumptions note
/validation/            test designs, scripts, consent form, results, analysis
/prototype/             v0 code (only after Phase 4 approval)
/decisions/             phase summaries + final decision memo
LOG.md                  hours log + phase status
```

---

## Phase 1 — Research sweep (target: 2–3 weeks, ~15 of my hours)

For each area, search papers, GitHub repos, datasets and existing products. Write one note per area using this template:

```
# Area N — name
Decision (1–3 lines): use X / adapt Y / build Z, estimated hours
What exists (ranked, max 8 items): name, link, maturity, licence, why it matters
What the evidence says (key findings, effect sizes where available)
Gaps we'd have to fill ourselves
Risks / unknowns
```

**Critical path — do these first and deepest:**

1. **Conversational onboarding (voice/video).** Conversational vs form surveys (start with Xiao et al. 2020 on AI chatbot surveys); end-of-turn detection (Silero VAD etc.); transcription (Whisper and alternatives); voice-agent frameworks (Pipecat, LiveKit Agents); "active listening" video loops; LLM extraction of free speech into structured preferences — and how reliable it is.
2. **Place and experience preferences.** Cold-start recommendation from 15–20 ratings; points-of-interest recommendation literature; attribute tag sets that work across cities; place data sources (OpenStreetMap, Overture Maps, Google Places API — with costs); test datasets (Foursquare check-ins, Yelp open dataset); RecBole.
3. **Personal weights (the βs).** Mixed logit vs hierarchical Bayes; how many conjoint choices give usable individual weights; adaptive / Bayesian optimal question design; tools (Biogeme, xlogit, PyMC). Start from Train, *Discrete Choice Methods with Simulation*.
4. **Itinerary building.** Orienteering problem with time windows (tourist trip design problem); Google OR-Tools; routing (OSRM, Valhalla); TfL Unified API; Open-Meteo; the TravelPlanner benchmark (2024) and later work on LLM + solver hybrids.

**Lighter pass:**

5. **Photo taste.** Personalised image aesthetic assessment (FLICKR-AES and successors); few-shot accuracy with CLIP / SigLIP / DINOv2; LAION aesthetic predictor. Is a centroid/linear probe enough for v1?
6. **Wellbeing science → model variables.** Sonnentag & Fritz (Recovery Experience Questionnaire), Nawijn (anticipation), de Bloom (fade-out), Kahneman (peak–end), Kaplan (attention restoration), Keltner (awe), UTCI thermal comfort. Output: a table of candidate variables, how to measure each, and realistic thresholds.
7. **Existing products.** Mindtrip, Layla, Wanderlog, group/meetup travel apps, anything doing mood- or feeling-based travel. Feature map + where the gap is.

**Light scan now, deeper later:**

8. Seamless interaction (calm technology, interruptibility research, WhatsApp Business Cloud API, Telegram Bot API, iOS Live Activities).
9. Body signals (HealthKit access, what HRV/sleep can and can't say about fatigue).
10. Money psychology and cost-splitting (Van Boven & Gilovich; Prelec & Loewenstein; Open Banking providers).
11. Companion matching (reciprocal recommenders, group recommendation).
12. Legal and ethics (ICO guidance on special-category and voice data, Equality Act limits on matching, Online Safety Act risk assessment, AI disclosure).

**Checkpoint 1:** `decisions/phase-1-summary.md` — the recommended v0 stack, total estimated build hours, and the three biggest unknowns.

---

## Phase 2 — Unit economics (target: 1 week, ~5 of my hours)

Build `economics/unit-economics.xlsx` plus `economics/assumptions.md`. Every input cell must link to a sourced assumption (URL + date) or be clearly marked as a guess.

**Cost per user:**
- Onboarding: transcription minutes, LLM tokens for conversation and extraction, TTS/video delivery, image embeddings.
- Per trip plan: LLM tokens, routing/places/weather API calls, messaging fees (WhatsApp conversation pricing vs Telegram free), hosting.
- Ongoing: per-stop ratings, storage, support/moderation time (trust & safety is real cost), payment/Open Banking fees if used.
- Show costs for three stack options: cheapest (Telegram + small models), default, premium (live avatar).

**Revenue models to compare (separate tabs):**
- Subscription (monthly/annual).
- Per-trip planning fee.
- Commission on group trips (organiser or participant fee).
- Affiliate/booking commissions (activities, transport, accommodation) — find real published rates.
- Promoted experiences (CPM/CPC) — include the reality check that at ~£5 CPM, £100k needs ~20m impressions (~83k MAU).

**Outputs:**
- Contribution margin per user and per trip for each model.
- CAC by channel (organic community posting, referrals, paid social) with sourced benchmarks.
- Retention assumptions → LTV → LTV:CAC.
- Break-even users and trips; users needed for £10k, £50k, £100k annual revenue.
- Sensitivity table on the 4–5 inputs that matter most.
- Founder-hours per 100 users (support, moderation, content) — the hidden constraint.

**Checkpoint 2:** which revenue model(s) look viable, which are ruled out, and which numbers the validation test must measure (e.g. willingness to pay, trips per month).

---

## Phase 3 — Validation: will people like the onboarding and use it? (target: 2–3 weeks, ~15 of my hours)

**Principle: test with no code or minimal code first.** Build nothing in Phase 4 until this passes.

Design everything in `/validation/`: test plans, recruitment posts, interview script, consent form (plain English: what's recorded, why, deletion after transcription), results sheet.

**Recruitment:** strangers, not friends — use the same channels as the weekend test (uni and city Facebook groups, UK travel subreddits, hiking and photography groups). Target 12–20 participants. Record where each came from; that is the distribution signal.

**Test A — Onboarding desirability (Wizard of Oz).**
- Run the conversational onboarding manually: a WhatsApp/Telegram voice-note conversation or a simple web page with pre-recorded host clips. I play the "system" behind the scenes where needed.
- Include the layers: past places with reactions, 8–10 "this or that" day-plan choices, the best-hour question, optional photo pairs.
- Measure: completion rate; time taken; drop-off point; "I felt understood" (1–5); "It felt like talking to a person, not filling a form" (1–5); what felt intrusive or tedious (open).

**Test B — Plan quality (blind comparison).**
- For each participant, produce two day plans for the same city and budget: one personalised from their onboarding (hand-built or LLM-assisted), one generic top-attractions plan. Label them A/B randomly.
- Measure: which they prefer and why; "This plan fits me" (1–5) for each.

**Test C — Actual use.**
- Offer them the plan for a real day or weekend. Measure: did they use it (all or part); per-stop 1–5 ratings with time, weather and travel time; "Would you go again?"; did they ask for a second plan within 2 weeks unprompted.

**Test D — Willingness to pay (smoke test).**
- A simple landing page describing the app with a waitlist and a priced option (e.g. small refundable deposit or "reserve founding price"). Measure visit → sign-up → deposit conversion. Test 2 price points if traffic allows.

**Interview script:** ask about past behaviour, not hypotheticals ("Tell me about the last trip you planned — how did you choose what to do?", "What did you spend on it? Was it worth it?"). No leading questions, no pitching until the end.

**Proposed pass thresholds (I will confirm before the test runs):**

| Metric | Pass |
|---|---|
| Onboarding completion | ≥ 70% |
| "Felt understood" | median ≥ 4/5 |
| Prefer personalised plan (blind) | ≥ 7 of 10 |
| Used the plan on a real day | ≥ 40% |
| Asked for a second plan within 2 weeks | ≥ 30% |
| Landing page visit → sign-up | ≥ 10% |
| Any paid deposits | ≥ 3 |

**Checkpoint 3:** `validation/results.md` — results vs thresholds, top 5 quotes, top 5 objections, what to change in onboarding, and a recommendation: build v0 / redesign and retest / stop.

---

## Phase 4 — Prototype v0 (only if Phase 3 passes; target: 4–5 weeks, ~35 of my hours)

Python + FastAPI. Reuse over build. Minimal scope:

1. **Onboarding** as a Telegram or WhatsApp voice conversation; LLM turns answers into a JSON profile (βs + tags + constraints).
2. **London place database:** ~100 hand-tagged places with the attribute set from Area 2.
3. **Scoring:** profile weights × place attributes + heat and transfer-time penalties (thresholds from Area 6).
4. **Planner:** OR-Tools builds the day under time/transport/weather constraints, guaranteeing one peak and a good finish; LLM writes the explanation.
5. **Feedback loop:** per-stop 1–5 rating logged with conditions; simple Bayesian update of the person's weights.
6. **Photo taste:** basic embedding similarity only.

Out of scope for v0: video avatar, wearables, companion matching, payments, native app.

Include: tests for scoring and planner, a privacy notice, raw-audio deletion after transcription, a data-deletion command.

**Checkpoint 4:** demo script, known limitations, cost per onboarding and per plan measured against the Phase 2 model.

---

## Phase 5 — Test v0 and decide (target: 2 weeks, ~10 of my hours)

- Re-run Tests B and C with 5–10 new strangers on the real prototype.
- Update the unit-economics model with measured costs and observed behaviour.
- Write `decisions/final-memo.md`:
  - What we learned (evidence, not opinion).
  - Unit economics with real numbers.
  - Go / iterate / stop recommendation with reasons.
  - If go: next 90 days, hours required, what's cut.
  - If stop: what's worth keeping (data, code, insights).

## Definition of done

- 12 research notes + `sources.csv` with every source verified.
- Unit-economics workbook with sourced assumptions and sensitivity.
- Validation results against pre-agreed thresholds.
- v0 prototype (if justified) with tests.
- Final decision memo.

Start with Phase 1, areas 1 and 4. Before searching, set up the repo structure and `LOG.md`, then confirm the plan back to me in 5 lines.
