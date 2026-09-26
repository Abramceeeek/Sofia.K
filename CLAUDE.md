# Travel App — Project Context

This file is the standing context for this project. Read it fully before any task.

## Who and what

- **Founder:** Abram — actuarial student (IFoA), data analyst, London-based. Stack: Python 3.12 (pinned: PyMC and Biogeme need ≥3.12), FastAPI. Comfortable with econometrics and statistics; explain models in those terms.
- **Time budget:** ~7.5 hours/week alongside full-time work and actuarial exams. Hours, not money, are the binding constraint. Every plan must state its hour cost.
- **Stage:** idea + design. Nothing built. No users tested yet.
- **Existing gate from the founder's own plan:** the core social idea (strangers join trips posted by someone they've never met, turn up and pay their share) is tested by a no-code "weekend test": post 5 real trips in existing travel/hiking/uni groups, pass = ≥3 strangers join and turn up. This project's validation work should run alongside or reuse that test, not replace it.
- **Legal gates** *(updated D33 and D38, confirmed by Abram 2026-09-26)*:
  - **Cleared:** right to run a business.
  - **Before taking any money:**
    1. Apple's outside-activities policy — check it and disclose if required. All project work stays on personal time and personal devices.
    2. Written secondary-employment approval from Abram's government agency employer.
    3. IP/invention clauses checked in **both** employment contracts.
  - **Before the first paid client or trip:** incorporation, the ICO data protection fee, and public liability and professional indemnity insurance.
  - **Before anyone else contributes work:** a written founders/contributors agreement covering roles, hours, equity or compensation, and IP assignment to the company.
  - Revenue from trips or subscriptions can start once the money gates are done. Research and unpaid tests can proceed now.

## The core idea

The app does not list famous places. It predicts **how a trip will make a specific person feel**, and plans around that.

Founder's example: Big Ben leaves him flat ("must-do", seen once, feel nothing). An Uber Boat, eating in the streets, walking through parks make him happy. Someone else may be the opposite.

Two outcomes the app tries to raise:
1. **How good the trip feels** — out of work mode, away from problems, restored or entertained.
2. **How worthwhile the money feels** — afterwards, the spend felt fully worth it.

## The unit is a moment, not a place

The database, the swipe layer, the planner and the per-stop ratings all work on **moments**. A moment is a specific experience at a place, at a time, often including how you arrive.

Founder's example: you come out of South Kensington tube and walk out to the Natural History Museum. The dark-to-open transition and the reveal *are* the experience, not "the museum". One place can hold several moments, and a moment can span a short walk.

- **A moment record:** place + route/approach (where you come from, the path, the entry point) + best time (time of day, light, season, crowd window) + features + a **shot card** (where to stand, what to frame, when). The schema is in `research/notes/02-place-preferences.md`.
- **Moment-level features, on top of place attributes:**
  - contrast/reveal (compression and release);
  - absorption/flow (activities that demand action, like go-karting or swimming);
  - awe;
  - photo potential;
  - social pull ("I need to bring people here");
  - cost in £.
- **Feeling per pound is computed, not tagged.** The model derives it as predicted S ÷ cost. Tagging it directly would double-count cost.
- **Seed moments come from Abram's own experience.** Five to start.

## The model: satisfaction as an equation

Satisfaction (per stop and per trip) is the dependent variable:

`S = β1·travel_time + β2·temperature + β3·crowds + β4·walking + β5·food + β6·novelty + β7·history_culture + β8·photo_potential + β9·fatigue + … + ε`

- **Person-specific βs.** Hierarchical model: each new user starts at the mean of similar users and shrinks toward their own weights as data arrives. This is why short onboarding can work.
- **Nonlinear effects.** Thresholds, not lines (15-min transfer ≈ fine, 50-min ruins the afternoon; heat fine until a threshold, then steep penalty).
- **Interactions matter most.** Rain × outdoor, heat × walking, fatigue × time of day.
- **Peak–end.** Trips are remembered by their best moment and their ending, not the average. The planner guarantees one strong peak and a good finish. *Amended (D15): the evidence is weak for multi-part experiences, so the end bonus is a toggle that is **off by default**, and per-moment ratings will test it.*
- **Explainability.** Named weights let the app explain choices ("We swapped the walk for the boat because heat and long transfers affect you most").

## Onboarding: layers of understanding

**a) Camera taste** — user picks ~10 own photos, then 8–10 pairwise "which do you prefer?" choices. Image embeddings (CLIP/SigLIP/DINOv2) + simple centroid or linear probe. Kept **separate** from experience taste (people photograph landmarks they don't enjoy). *Amended (D16): dropped from the v0 model and from Test A, because 10 examples barely beat a generic model (Area 5). Test A asks instead how much photos and sharing matter (1–5) and whether a shot card would make a moment more appealing (1–5).*

**b) Places already visited (revealed preference)** — for a city they know, swipe 15–20 places: Loved it / It was fine / Didn't enjoy it / Haven't been. Visiting alone means little (everyone visits Big Ben); the reaction is the data. Each place tagged with attributes (e.g. Big Ben: history, iconic, crowded, passive; Uber Boat: movement, views, relaxed; Borough Market: food, busy, local). Use places that **split** people (British Museum vs cable car; Hyde Park vs Camden). Friendly persona label on the result screen, continuous scores underneath.

**c) "This or that" day plans (choice-based conjoint)** — two versions of a day varying a few factors (e.g. 3 stops, lots of walking, sunny vs 5 stops by boat/train, one hot hour). ~10 choices → weights on travel time, heat, pace, crowds, cost.

**d) One open question** — "Tell me about the best hour of your last trip."

**e) Body signals (optional, opt-in, later)** — Apple Health: sleep, steps, heart rate, HRV to adapt on the day.

## Conversational video onboarding

Replace forms with a conversation that feels like talking to a well-travelled friend.

- Intro from a real person: "We wanted to bring some of the best experiences we've had to you, so you can have them too."
- Host asks one question at a time; user answers by voice.
- Recording starts automatically when the host finishes asking.
- While the user speaks, the host is shown **actively listening** (nods, attentive loop) so it never feels like talking into a void.
- Speech detection ends the turn — no visible timer, **no time limit**.
- When they stop: "Is there anything else you'd like to add about that?"
- Adaptive follow-ups (e.g. "loved the boat but hated the queues" → next question probes crowds).
- Answers are transcribed and converted into the same structured data as a–d.
- Build options, simplest first: (1) pre-recorded human clips + AI choosing order; (2) voice-only, call-like; (3) live AI avatar (disclose clearly it's AI).
- Always allow typing instead of speaking.

## Personal context — ask for what's needed, not the sensitive category

- Budget per trip/day — **not** income or financial situation.
- Languages spoken, home city / where they grew up, food needs (halal, vegetarian, allergies) — **not** nationality. *Amended (D19): v0 asks one optional question, "Any foods or drinks you avoid?", with a one-line consent note, and **no allergy question**. Allergies are health data and halal may reveal religion (Area 12).*
- Travel style: solo / friends / partner; morning or night person; activity level.

Reason: nationality is a protected characteristic under UK equality law; using it to match or filter strangers is a discrimination risk. Financial and health data are sensitive under UK GDPR.

## Continuous learning after onboarding

- One-tap 1–5 rating after each stop (lock screen / watch / chat), logged with conditions: weather, time, travel time, steps. **This is the most valuable data the app will have.**
- Post-trip: "Would you go again?" / "How did it feel?"
- Later: "people like you" collaborative filtering.

## Research foundations (to verify and deepen)

- **Recovery experiences** (Sonnentag & Fritz): detachment, relaxation, mastery, control. Score each stop on these; people differ in which they need.
- **Anticipation** (Nawijn et al.): happiness boost often larger before the trip than after → build anticipation with previews.
- **Fade-out** (de Bloom et al.): benefits fade within weeks → shorter, more frequent trips.
- **Awe and nature** (Keltner; Kaplan's attention restoration theory): measurably restorative.
- **Body sets the ceiling:** heat, hunger, poor sleep, too many steps, decision fatigue.
- **Money:** experiences beat material purchases for lasting happiness (Van Boven & Gilovich); paying hurts less when decoupled from the moment (Prelec & Loewenstein) → prepay and auto-split costs.

## Seamless interaction ("calm technology")

- Infer mostly, ask rarely. Silence = "all fine".
- Meet people where they are: WhatsApp/Telegram assistant, lock-screen cards, watch taps, voice via earbuds.
- Proactive with suggestions, **never** with money — every booking or payment needs a tap.

## Companion matching

The same profile matches **people**, not just places. Compatible trip-mates make strangers more likely to commit and turn up — the hardest part of the app.

## Non-negotiable guardrails

- Wellbeing/health data: explicit opt-in, clear purpose, easy deletion.
- Transcribe voice/video, then delete raw recordings unless the user chooses to keep them.
- Frame as trip wellbeing — never psychological assessment or therapy.
- Disclose AI-generated hosts.
- Never use nationality or other protected characteristics to match or filter people.
- No consumer credit, no card issuing (both need FCA authorisation) — Open Banking via a licensed provider only, and only later.
- **Never hold trip money.** Use Stripe Connect direct charges only, so each payment goes to the host's or venue's own account and only our fee reaches us (D39, Area 18).
- Trust & safety (strangers + travel) is part of the product; Online Safety Act duties apply regardless of size.
- **Safety alerts always go to a person, never only to the AI** (D46, Area 19).
  - **At the start, Abram handles them**, with a response target of **within a few hours**.
  - **A named backup helper** covers the hours when Abram is at work. The helper signs the contributors agreement, including confidentiality, before seeing any user messages (D38).
  - The automatic reply tells the user straight away to call 999 in an emergency, and says that a person will reply within a few hours. It never promises a faster reply.

## Working rules for Claude in this repo

1. **Never fabricate sources.** Every paper, repo, dataset, price or statistic must come from a search or fetch in this session, with URL and access date. If unverified, mark `UNVERIFIED`.
2. For each GitHub repo record: stars, last commit date, licence, maintenance status, and whether it runs on Python 3.11+.
3. For each price (APIs, LLM tokens, messaging fees) record the source URL and date — prices change.
4. State hour cost for every proposed piece of work. Prefer reuse over build.
5. Stop at each phase checkpoint in `KICKOFF_PROMPT.md` and summarise for Abram before continuing.
6. Keep notes short: one page per research area, decision first.
7. UK context by default (London first, GBP, UK law).
