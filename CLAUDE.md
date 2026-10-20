# Travel App — Project Context

This file is the standing context for this project. Read it fully before any task.

## Who and what

- **Founder:** Abram — actuarial student (IFoA), data analyst, London-based. Stack: Python 3.12 (pinned: PyMC and Biogeme need ≥3.12), FastAPI. Comfortable with econometrics and statistics; explain models in those terms.
- **Time budget:** ~7.5 hours/week alongside full-time work and actuarial exams. Hours, not money, are the binding constraint. Every plan must state its hour cost.
- **Stage:** idea + design. The v0 backend (the Brain) is drafted in `brain/` (D51). No users tested yet.
- **Existing gate from the founder's own plan:** the core social idea (strangers join trips posted by someone they've never met, turn up and pay their share) is tested by a no-code "weekend test": post 5 real trips in existing travel/hiking/uni groups, pass = ≥3 strangers join and turn up. This project's validation work should run alongside or reuse that test, not replace it.
- **Legal gates** *(updated D33 and D38, confirmed by Abram 2026-09-26)*:
  - **Cleared:** right to run a business.
  - **Before taking any money:**
    1. Apple's outside-activities policy — check it and disclose if required. All project work stays on personal time and personal devices. *Abram expects it to be fine and is double-checking (28 Sep).*
    2. ~~Written secondary-employment approval from Abram's government agency employer.~~ **Done (D94):** the government job is in Uzbekistan and doesn't conflict (Abram, 28 Sep).
    3. IP/invention clauses checked in **both** employment contracts. **Government contract: done; it has no IP clause covering his own projects (confirmed 28 Sep, D96). Apple contract: with the Apple double-check.**
  - **Before the first paid client or trip:** incorporation, the ICO data protection fee, and public liability and professional indemnity insurance.
    - **ICO fee (D108):** Abram's fee checker said not required yet (29 Sep). He re-checks, and pays if required, **before spreading to strangers**, which starts with Post 1 (the study holds strangers' names, numbers and voice notes).
  - **Before anyone else contributes work:** a written founders/contributors agreement covering roles, hours, equity or compensation, and IP assignment to the company. This includes the safety backup helper and any future contributor (D55).
    - **Abram designs v0 himself (D81)**, so no designer agreement is needed unless an outside designer is brought in.
    - *Split by D73:* **Part A** (IP assignment, confidentiality, personal data) is signed as a deed before anyone's work is used, and before the helper sees any user message. **Part B** (equity) gets a solicitor review before incorporation. Contributions are voluntary and flexible, with no set hours.
  - **Before public App Store release (D53):** check Apple's outside-activities policy for publishing under Abram's own developer account. **Abram is double-checking the Apple policy and the Apple IP clause before any external TestFlight build (D60, D94).**
  - **Developer account (D61):** individual for TestFlight. Switch to a company account (incorporation plus a D-U-N-S number) before the public App Store launch. Start about 3 weeks ahead.
    - **Renew the membership only if Test B passes (D74).** Keep auto-renew off until then. **Auto-renew is off (confirmed 28 Sep, D94).**
    - **The membership runs until July 2027 (Abram, 30 Sep).** So it covers every test through Checkpoint 3; the D74 renewal decision falls due before July 2027.
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
- **Feeling per pound is computed, not tagged** (tagging it would double-count cost). *Amended (D88): no raw S ÷ cost ratio. It depends on utility's arbitrary zero, and free moments divide by zero.*
  - **The app shows "worth about £V to you":** V = the non-cost part of S ÷ the person's cost weight (per £), next to the price. *Amended (D127): no longer shown. After the short onboarding the cost weight's 95% range spans about 20 times, so £V overclaimed. The app shows the price and words from the rating model: "A strong match for you" (≥75% chance of Good or better), "A good match for you" (≥50%), else "Worth a try". £V stays inside the model and the day's curve.*
  - **Ranking is by V − price**, which is the same as ranking by S, so the planner doesn't change.
  - **The person's cost weight is constrained to stay negative:** it is fitted on a log scale (β_cost = b_pop · e^δ), so V never explodes.
- **Seed moments come from Abram's own experience.** Five to start. Batch 1 (11 cards, D72) is in `brain/data/moments/`.
- **Entry types (D72):** a **moment** (one specific experience) or an **area vibe** (a wander or street scene: a centre point, flexible time, at most one a day, never the day's peak).
  - **Variants** (the same trip by day and by night) share a group, and a plan holds at most one.
  - **Draft cards never go into real plans**; only `status: ready`.
  - **Who marks a card ready (D91):**
    - **Research-sourced cards:** Claude verifies the facts from official sources and marks them ready, then gives Abram one list with a line each to flag disagreements.
    - **Abram's own cards:** Claude asks only what only he knows (route, feeling), batched, and fills the rest with checked guesses.

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

**c) "This or that" day plans (choice-based conjoint)** — two versions of a day varying a few factors (e.g. 3 stops, lots of walking, sunny vs 5 stops by boat/train, one hot hour). ~10 choices → weights on travel time, heat, pace, crowds, cost. *Amended (D95): heat is replaced by "weather at the outdoor stops: mild and dry / cold but dry / rainy", which maps onto the model's cold × outdoors and rain × outdoors.*

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
- Languages spoken, home city / where they grew up, food needs (halal, vegetarian, allergies) — **not** nationality. *Amended (D19): v0 asks one optional question, "Any foods or drinks you avoid?", with a one-line consent note, and **no allergy question**. Allergies are health data and halal may reveal religion (Area 12).* *Amended (D123, 8 Oct): the food and "where did you grow up" questions are no longer asked, because no plan used them. Ask again only once the planner uses the answer.*
- Travel style: solo / friends / partner; morning or night person; activity level. *(D127: now used, not only kept: going with others leans toward places to bring people, and a gentle or full-on day leans walking and active; both are stated leanings like the feelings. Morning or night sets the plan's default hours.)*
- **Inspiring fields (D77, optional):** finance & tech / food / history & culture / nature / none. Art & design was dropped for Test B (D83). This asks about interests, never a job or employer.
  - It feeds `aspiration_match`, mapped onto moments in `brain/data/aspiration.yaml`.
  - A field with fewer than 2 ready moments is flagged.

Reason: nationality is a protected characteristic under UK equality law; using it to match or filter strangers is a discrimination risk. Financial and health data are sensitive under UK GDPR.

## Continuous learning after onboarding

- One-tap 1–5 rating after each stop (lock screen / watch / chat), logged with conditions: weather, time, travel time, steps. **This is the most valuable data the app will have.**
- Post-trip: "Would you go again?" / "How did it feel?" *(D127: built for each day. "Was today worth what you spent on it?" (not quite / yes / more than that) and "Would you do this day again?" on "Thanks for today", the product's second outcome.)*
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

## v0 build (D50–D52)

- **v0 is a native iOS app (SwiftUI)**, tested through TestFlight, then released on the App Store once it passes (after the D53 gate). It replaces the Telegram bot.
- **Brain** (`brain/`): FastAPI on Python 3.12. It holds the moment database, scoring as `S = x·(b_population + δ_person)` with δ kept separate and portable, and the OR-Tools planner. Claude Code builds and tests it in this repo.
  - **Live on Render** at `moments-brain.onrender.com` (free tier, 30 Sep).
  - **Day shape (D127):** at most two history-and-culture stops a day, never back to back (35% of personal plans had two in a row).
  - **Plan variety (D113):** a popularity nudge. The planner lowers each card by 3 × its share of simulated plans (`brain/data/popularity.yaml`). It keeps that plan only if it loses at most about £4 by the person's own weights and still fits the brief (`decisions/plan-variety.md`).
  - **Visitors (D116):** onboarding starts with "Where are you based?" (London / elsewhere in the UK / visiting from abroad, then a town or city; **never nationality**). Visitors from abroad get 8 kinds-of-places cards (`brain/data/categories.yaml`) instead of the London places. **They are a separate cohort, excluded from the Test B analysis** (`cohorts` in the export). Five verified shopping cards are ready. Visas, money help, in-app booking, deals, other cities and accounts stay on `decisions/after-9-nov.md`.
  - **Onboarding upgrade (D117):** a logo intro; Abram's hello and two short clips, bundled in the app with captions (`design/video-spec.md`); short reactions from the answer itself; "So far, I've learned…" (own answers only, no scores) with "Change something" (corrections stored and applied); and a plan reveal instead of a spinner. Motion is quiet (fades and one drawn line) and respects Reduce Motion. Permissions are asked only when a feature needs them. Sign-in options and adaptive questions wait until after Test B.
  - **After the D117 review (D118):** Help & safety replies now reach the person: in the app, and by phone or email if they choose to leave one (deleted once sorted, 30 days at most; `brain/README.md` has the reply commands). Rating reminders are local notifications, asked once after a plan. The plan headline uses the person's own feeling words only when the stops carry them. The 14 questions before the first plan stay, counted honestly.
  - **ODYS (D119):** the app is now called **ODYS**, dark always, in Abram's ODYS design (the arch, amber light, Newsreader, quiet motion). *Amended (D130, 20 Oct; not built yet): "Daylight". The colours will follow London's real light, dark at night, with an "Always dark" setting, plus settling motion, the day as a path and an arrival moment on "Now" (`design/natural-feel-synthesis.md`).* The day shows "How the day moves" with a word per stop (from the card, the same for everyone), and a **"Now" screen** carries the person through the day. What was kept from the old design, and why, is in m164. The name is unchecked as a UK trademark: search before the public release.
  - **Share card (D114, D119, D127):** after a rated stop, the person can share the moment's photo, **their own rating**, the reason from their answers (a switch leaves it out) and "Planned with ODYS", headed "A moment from my day", with their link and "A moment from my day out, planned with ODYS" (neutral, not words put in their mouth). **No rewards, never the model's guesses.** The funnel (shared → opened → onboarded → first plan) feeds Test C's K (`GET /v1/admin/referrals`).
  - **Trips (D120, D121, 6 Oct):** multi-day trips with flights (Duffel) and places to stay (LiteAPI) found and filtered in the app, **booked on the provider's own site** (Skyscanner, Google Flights, Booking.com, Airbnb, the hotel's site). **No commission while testing**; labelled sample results until Abram adds the keys in Render. London now, then UK cities, Europe and more (after-9-Nov #49). Three tabs (Trip, Book, You) from Abram's "ODYS Trips" design; what differs from it, and why, is D121. **D122:** each trip day runs at the person's own hours with their places a day (lunch extra); the first day starts where they land or arrive (by plane, train or car), with one place on the way if they travel light and arrive before check-in; the last day ends with the way back to the stay and on to the airport or station, with Apple Maps directions (`brain/src/brain/tripdays.py`).
  - **Build 2 (built 6 Oct):** after "So far", the Test A survey; then, for people in the UK, the blind Plan 1 / Plan 2 pair (same text format, random order stored), the gut choice, "fits me" for each, why, and the reveal. The chosen plan is their day, without swap or regenerate. An optional tester code on the welcome screen (`brain/data/tester_codes.yaml`).
- **Face:** the SwiftUI app. It is built, signed and uploaded to TestFlight by **GitHub Actions on a macOS runner**, with no personal Mac (D64). iOS builds run only on pushes to main that change files under the app folder (not on branches, since 20 Oct: m188), and backend tests run on Linux. Abram holds the signing secrets in GitHub Secrets. Claude writes the Swift here, but can't run it here, so every check goes through CI.
- **Android (D125, 9 Oct):** the same app in Kotlin and Jetpack Compose (`android/`), built on Linux by GitHub Actions. Abram installs the test APK from the `android-latest` pre-release; Google Play waits (after-9-Nov #67). Before each APK is published, CI draws every screen with the iPhone's sample data (Robolectric). **Every app change is now made in both apps.** Maps are OpenStreetMap tiles and directions open Google Maps; the privacy notice names both.
- **Phase 3 (D63, D65–D68):**
  - **App first (D109, supersedes the hand-run tests):** no posting or advertising until the app is ready. **Tests A–C run inside the app:** in-app onboarding with the swipes and the "this or that" choices, a blind Plan 1 / Plan 2 comparison with the generic plan, and one-tap ratings on a real day. The order: (1) a build on Abram's iPhone (internal TestFlight), (2) friends (external TestFlight), (3) strangers (external TestFlight). The WhatsApp chat version is paused and kept as a fallback.
  - ~~Tests A–C run by hand. Test A is a chat on WhatsApp Business with a separate number; the plans go as messages or PDFs.~~
  - **The Brain generates the Test B plans** from the results sheet, and Abram checks them.
  - **Test B is formative (D127):** "7 of 10" stays the keep-going signal, but by chance alone it happens 17% of the time. The paired "Plan 1 / Plan 2 fits me" difference is a co-primary result; aim for ~20 testers; report the overlap with the no-answers plan (`brain/scripts/testb_report.py`).
  - **Dates (D109, estimates):** Abram's iPhone build ~7 Oct; Tests A–C in the app ~14 Oct; friends 16–25 Oct; strangers from ~27 Oct; **Test B reports ~13 Nov; Checkpoint 3 in the week of 23 Nov** (was the week of 2 Nov). *Amended (D128, 20 Oct): the friends' round waits until the app's feel is fixed ("fix the feel first"), so these dates move; new dates once the work is scoped.*
  - **Lean mode (D107):** keep only what's needed to run the stranger tests legally and safely, and to build the product (`validation/recruit-now.md`). Sign-ups come by a WhatsApp click-to-chat link in the posts, and the first reply asks where they saw it. The 16 swipe places are locked. The app asks 6 places and 5 this-or-that tasks before the first plan, and the rest in "Improve future plans" (D112); Test B uses this short version. The final set is re-chosen from all 30 swipe-page candidates at 20+ people and locked before strangers (~27 Oct, D111). **Test D runs after Test B.** Desk reviews, the Tally form, quick replies and labels, and the South Kensington walk are deferred (`decisions/after-9-nov.md` #19).
  - **Test E is postponed until v0 exists (D86).** It runs with a working demo after Test B, and before any B2B-specific build work. Until then, **"businesses will pay" is an explicit, untested assumption and the main revenue risk.** Its hours went to moment cards and Test B.
  - **The iOS app is built now, in parallel with the tests (D107):** the Brain first, then native SwiftUI screens in three batches.
    - Abram's review stays small: one screenshot page per batch from CI.
    - His own design pass on the four custom screens (D81) is optional, after Test B.
    - **Visual direction (D119, replacing D112's Stitch theme):** his ODYS design files, built as custom SwiftUI parts (`app/Sources/Odys.swift`, `design/v0-screens.md`).
    - **Card photos (30 Sep):** openly licensed photos from Wikimedia Commons, with a credit under each, until Abram's own replace them (`design/photo-credits.md`). A card with no suitable photo keeps the satellite view.
    - The first external TestFlight build is about the week of 9 Nov, behind the same gates.
    - The GitHub Actions pipeline builds for the simulator until Abram adds the signing secrets (D70e).
  - **The 16 onboarding swipe places** come from an anonymous swipe page (D70c: `brain/src/brain/calibration.py`, Render free tier). It has no login and no personal questions, and no IP address is stored.
- **Plan, hours and the accepted cuts (D59):** `decisions/v0-ios-plan.md`. **Screens and design scope (D81):** `design/v0-screens.md`. **Founder briefing:** `decisions/founder-briefing.md`. **Roadmap to a real product (6 Oct):** `decisions/roadmap.md`: Stage 1 "real for testers" before strangers (live flights and hotels, TfL times, Met Office weather, a paid server), then the tests, then a public release only if Checkpoint 3 says go. **Stage 1 go (D126, 19 Oct):** Claude's steps are built: TfL times and the Met Office forecast (never for the Test B pair), logs without personal data, error alerts, rate limits, and nightly backups sealed to Abram's key (`brain/README.md`, Stage 1). TestFlight text and the gates: `decisions/testflight-external.md`. The paid server, live keys, backup keys and the ops workflow on `main` are Abram's. **Journey audit (7 Oct):** `decisions/journey-audit.md`, from onboarding to the flight home and against the free alternatives. Its findings are fixed (m175, m176), and decisions 1–3 are done (D123). **Round 2 (8 Oct):** `decisions/journey-audit-2.md`: 28 more fixes (m178); its open items are fixed too (m179), with "Re-plan the rest of today", "Checked" on stops and a fresh start after a reinstall (D124). The paid server is still Abram's. **Location while out (D123):** asked on "Now", when in use only, on the phone; only a "Start from where I am" point leaves it, rounded to ~100 m and not kept. **Closing the gaps with other apps:** `decisions/competitor-gaps-plan.md` (proposed; new ideas wait for Checkpoint 3). **UX checklist (9 Oct):** `decisions/ux-checklist.md`: the 327 questions of five pasted checklists, merged into 120 and answered for ODYS; its failures are fixed (m181).
- **Economics work is paused** unless a decision needs it (D52).

## Non-negotiable guardrails

- Wellbeing/health data: explicit opt-in, clear purpose, easy deletion.
- **Location (D123):** opt-in when it's first useful, "when in use" only, processed on the phone. Never stored on the server; never used to infer where someone lives.
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
  - The automatic reply tells the user straight away to call 999 in an emergency, and says that a person will reply, usually within a few hours. It never promises a faster reply. *(D127: it also says nobody watches through the night, so a late message is answered the next morning, and Help & safety gives Samaritans' free 24-hour line, 116 123.)*

## Working rules for Claude in this repo

1. **Never fabricate sources.** Every paper, repo, dataset, price or statistic must come from a search or fetch in this session, with URL and access date. If unverified, mark `UNVERIFIED`.
2. For each GitHub repo record: stars, last commit date, licence, maintenance status, and whether it runs on Python 3.11+.
3. For each price (APIs, LLM tokens, messaging fees) record the source URL and date — prices change.
4. State hour cost for every proposed piece of work. Prefer reuse over build.
5. Stop at each phase checkpoint in `KICKOFF_PROMPT.md` and summarise for Abram before continuing.
6. Keep notes short: one page per research area, decision first.
7. UK context by default (London first, GBP, UK law).
8. **Standing rule (D69):** make minor decisions yourself (wording, file layout, scheduling moves under 1 h, tooling within the agreed stack) and log them in `decisions/decision-log.md`. Stop only for decisions that change scope, cost money, affect privacy or safety, or move a checkpoint. Batch everything else into one list at each checkpoint.
9. **After-9-Nov rule (D75):** any new idea that doesn't help Test B goes on `decisions/after-9-nov.md`, not into the current plan. The list is reviewed at Checkpoint 3.
10. **Actual hours (D82):** when Abram reports hours spent, log them in the Actual column of `LOG.md` (hours log and weekly totals) the same day. Never fill actuals from estimates.
