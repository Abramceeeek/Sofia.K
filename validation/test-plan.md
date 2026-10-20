# Phase 3 test plan

**Order (D36, changed by D86):** Tests A–D first. **Test E (B2B discovery) is postponed until v0 exists:** it runs with a working demo after Test B, before any B2B-specific build work, then the decision note `decisions/b2b-vs-consumer-first.md` (D40). Until then, "businesses will pay" is an explicit, untested assumption.

**Sample:** 12 completing **strangers** (recruit 14). Record the source of each, since that is the distribution signal. Adults 18+ in or near London. Test B needs ≥10 strangers who finish Test A for the "7 of 10" threshold.

**Friends and family are a separate launch channel (D43).** They are welcome, tagged `friends & family` in the results sheet and reported separately. **Every threshold and K are measured on strangers only.** Rule: anyone Abram knows, or who was sent by someone he knows, counts as friends and family.

**Principle (D63, D65–D68):** Tests A–C run **by hand**. Test A is a chat on **WhatsApp Business with a separate number** (D66), and the Test B/C plans are sent as messages or PDFs. **Test B runs first and fast:** each person gets their two plans 1–3 days after their Test A chat, so Test B reports around 23 Oct (D68, D106). **The Brain writes the Test B plans** (D65). Abram plays "the system" (Wizard of Oz). Participants are told a person runs the chat, and that AI helps draft summaries and plans (`consent-form.md`). Test D is a web page, and Test E is interviews. **Checkpoint 3 is in the week of 2 Nov** (D106). The iOS app is built in parallel; its first external TestFlight build comes after Checkpoint 3 and carries these lessons (`decisions/v0-ios-plan.md`).

## Pass thresholds (D2, D18)

Every Test A metric is reported **overall, and separately for voice and text** (D4, D18). In the chat, voice notes are visible, so the split is observed directly. (In the app, the open "great moment" question records whether it was spoken or typed, so the survey no longer asks "Did you type or speak?", D127. It is now the last question before "So far", and "I felt understood" is asked after it.)

| Test | Metric | Pass |
|---|---|---|
| A | Onboarding completion (finished the read-back) | ≥ 70% |
| A | "I felt understood" (1–5) | median ≥ 4 |
| B | Prefer the personalised plan (blind) | ≥ 7 of 10 (a keep-going signal, not proof: D127) |
| C | Used the plan on a real day (all or part) | ≥ 40% |
| C | Asked for a second plan within 2 weeks, unprompted | ≥ 30% |
| D | Landing visit → sign-up | ≥ 10% |
| D | Sign-ups choosing a priced option | ≥ 20% |

**Descriptive only:**
- "It felt like talking to a person, not filling a form" (1–5).
- Time taken and drop-off point.
- What felt intrusive or tedious.
- Photos matter (1–5) and shot-card appeal (1–5) (D16).
- Virality measures (below).

## Test A — onboarding (Wizard of Oz on WhatsApp Business, D63, D66)

- **Mode:** the participant chooses voice notes or typing and can switch; record the first choice (D4). Voice notes are transcribed **locally** (open-source Whisper) and audio is deleted once transcribed. The opt-in keeps it 30 days for accuracy spot-checks (D3).
- **Layers**, in order (`interview-script.md`; the same wording is in `brain/data/onboarding.yaml` for the app):
  1. best hour of the last trip, with an "anything else?" follow-up;
  2. why they travel (tap up to 2);
  3. 16 London swipe items;
  4. 10 "this or that" plans (`conjoint/design.csv`);
  5. personal context, including the optional food question (D19) and "where you grew up" (place type, optional);
  6. two photo questions and an example shot card (D16);
  7. **read-back**: "Here's what I heard — did I get that right?";
  8. short survey.
- **Measures:** completion; minutes from first to last message; drop-off layer; the survey items; open answers.
- **In the app (D117), descriptive, no pass threshold:**
  - "So far, I've learned…" is the app's read-back (layer 7). Report:
    - the share who tap "Looks right" (`summary_ok`) versus "Change something" (`summary_changed`);
    - which kinds of line get corrected (`corrections` in the export, with the words shown). Many corrected place lines would mean the place phrases or tags are off.
  - How far people watch Abram's hello (`founder_video`: seconds, and whether it ended).
- **Test C (D118):** the share who turn on rating reminders (`reminders_on` / `reminders_off`), and ratings per stop with and without them. Descriptive.
  - Time from install to first plan, with and without the video. The video and "So far" add time, so read completion and minutes beside these.

## Test B — plan quality (blind)

- **Same brief for both plans:** same city, same day length, same budget, same number of stops, same format and length.
  - **The day runs 12:00–17:00 (D99)**, so it ends around sunset (16:47 on 26 Oct, 16:24 on 8 Nov) and the river, sunset and evening-light moments can appear.
  - **Both plans end within 30 min of each other (D97).**
  - **Personalised:** written by the Brain (`python -m brain.testb plans`, `brain/README.md`).
    - It fits the person's weights from their Swipes and Choices rows, then plans the day from the moment database with the same brief: start, times, number of stops and budget.
    - Abram checks it with the review sheet (legs over 20 min, opening hours, prices) and sends it as a WhatsApp message or PDF.
    - **The sent plan never says why a stop was chosen**, so it stays blind.
    - About 25 complete moments are needed in `brain/data/moments/` before the first plan.
  - **Generic:** a top-attractions plan written once and reused (`validation/raw/testb/generic.yaml`). It uses the same fields as the personalised plan, including how to arrive, so the format gives nothing away.
- **Labels come from the pre-randomised list** in `results-sheet.xlsx` (balanced 50/50, fixed seed). The sheet says A or B; the plans are sent as **Plan 1 and Plan 2** (A → 1, B → 2; D97, D99).
- **Measures:** which they prefer and why; "This plan fits me" (1–5) for each.
  - **Two co-primary results (D127):** the gut choice, and the paired difference "Plan fits me" (personal minus generic) for each person. By chance alone, 7 or more of 10 happens 17% of the time; at a true 70% preference, 10 testers pass only 65% of the time (`brain/scripts/algorithm_checks.py`). **Aim for ~20 UK testers** if recruiting allows.
  - **Overlap:** how many of each personal plan's places the no-answers plan also has. A high overlap means a win comes from the curation, not the answers.
  - **Known bias:** no photos in the blind pair, so names people recognise may favour the generic plan. The blind texts are made alike (the title up to its colon, one sentence each for the way in and what happens) so the personal plan's longer stories don't give it away (D127).
  - **Read-out:** `brain/scripts/testb_report.py` on the admin export (choice with an exact binomial p, the paired fit difference with a bootstrap interval and a sign test, the overlap, the end-of-day answers, and "felt understood" by typed or spoken).
  - **Ask for a gut reaction** ("which would you rather do?"), not an analysis (D100).
  - **Both plans include lunch around midday** (D102): the generic plan marks its lunch stop, and the personal plan gets a food card the person likes or a flexible "lunch near" slot.
  - **Some "why" answers may be AI-assisted.** Mark long, polished answers with "(possibly AI-assisted)" in the "Why (open)" cell; the choice still counts, but those answers aren't quoted as evidence of feeling.
  - **The dry run (friends, not test data)** found the personal plan easy to spot from its content, and the generic plan weak. So the generic plan is now a strong "best of London" day (D100).
- **Trip intent** (Area 15) is asked just before: "recharge or explore?", "who's coming?", "one must-do?". It is stored with the plan (D27).
- **Visitors from abroad are a separate cohort, excluded from the Test B analysis (D116).** The app's first question is "Where are you based?" (London / elsewhere in the UK / visiting from abroad). Visitors get the kinds-of-places cards instead of the London places, so their plans rest on different evidence.
  - Split by `cohorts` in the admin export ("visitor" or "resident").
  - Report visitors' preference and "fits me" separately and descriptively, and count them in the sign-ups.
  - The share of sign-ups who are visitors is itself a result: it feeds the London-first or visitor-first decision at Checkpoint 3.

## Test C — actual use (plus virality, D23)

- **Offer the personalised plan** for a real day or weekend. If they clearly preferred the generic one, let them choose, and record which.
- **During the day:** after each stop they send one number, 1–5. Log the message time, the weather (look it up afterwards) and the travel time from the plan.
- **In the app (D109, D114): "Share this moment"** appears on a stop once it's rated, whatever the rating (so rating high never unlocks anything). It shares a card with the moment's photo, **the person's own rating** and "Planned with Days out", plus their link and the words "I think you'd love this day — try it". **No rewards, and never the model's "worth £X".** It only appears after the visit, so the blind plan comparison is already over.
- ~~**"Bring a friend":** the plan message includes a line to forward to a friend, with a personal referral link (`?ref=P07`).~~ ~~**Share prompt after the shot-card moment.**~~ (WhatsApp version, paused by D109.) **We never ask for anyone's photo.**
- **After the day:** "Would you go again?"; "How did it feel?"; "Did you invite anyone? How many?"; "Did you share a photo? Where?".
- **For 2 weeks:** log any unprompted request for a second plan.

**Virality measures (D114: logged by the app and the Brain, `GET /v1/admin/referrals`):**
- **The funnel, per sharer and in total:** share screen opened → **shared** (the share sheet completed; the kind of app, never who to) → link page **opened** in a browser (counted by the page's script, so link previews don't count; a reload counts again) → **installed** through the link → **onboarded** → **first plan**.
- **Invites sent** per participant = shares; **invitee sign-ups** = installs through their link.
- **Known undercount:** someone who installs from TestFlight and then opens the app directly, without tapping "Open Days out" on the link's page, isn't attributed. Ask in the after-the-day questions too ("Did you share it? Did anyone join?").
- **Before external TestFlight exists, the page says the test is closed.** When the public TestFlight link exists, set `BRAIN_TESTFLIGHT_URL` on Render and the page offers it.
- **K** = invitee sign-ups ÷ **stranger** participants who did Test C (D43). Their invitees count, whoever they are; friends-and-family participants' invites are reported separately. Also report invites per participant, sign-ups per invite and shares per participant.
- **Compare with the workbook** (`Virality` tab): £50k from the consumer app alone needs K ≈ 0.98 (base) or ≈ 0.53 (upside, D31 prices).
- **Caveat:** with ~12 people, one enthusiastic sharer moves K a lot, so report counts, not just the ratio.

## Test D — willingness to pay (landing page, D1, D2, D25)

- **Its own recruitment post** (D21) and its own visitors. Traffic from study participants (`src=participant`) and from friends and family (`src=ff`) is excluded from the rates and counted separately.
- **Random arm on first visit:** A = £4.99/month or £49.99/year; B = £9.99/month or £99.99/year. Both annual prices are about two months free (D31). The copy says the first plan is free and payment would be asked for after it.
- **Buttons:** "Join the free waitlist", "Reserve founding price (monthly)", "Reserve founding price (annual)". **All three lead to the same waitlist form**, with an honest note: no payment is taken now; we'll email before anything is ever charged.
- **Measures:** visits by arm (GoatCounter); sign-ups by arm and by option (Tally hidden fields); monthly vs annual split.
- **Two sign-up rates:** sign-ups with a `ref` code (invitees) are counted for K, and the Test D rates are reported both with and without them.
- **Meta ads: none** (D26).
- **To consider at Checkpoint 3 (journey audit round 2, D124):** a per-trip price beside the monthly and yearly ones. Flighty sells £4.99 pay-as-you-go next to £59.99 a year (UK App Store, read 8 Oct 2026). UK paid travel apps charge £24.99–£59.99 a year. Only 17% would pay up to 5% of a trip's value for an AI assistant (Amadeus, Sep 2025). The arms are not changed yet.

## Test E — B2B discovery (5 interviews, D34, D36, D49): postponed until v0 exists (D86)

- **When:** after Test B, with a working demo, and before any B2B-specific build work (D86). The questions below stay as they are; a short demo section is added at the close before it runs.

- **Who:** 3 London contacts (a hotel, a serviced-apartment operator, a tourism body) and **2 Uzbek outbound agencies** sending clients to London, at London prices (D49). The Uzbek interviews also ask how the agency pays foreign suppliers (Area 20).
- **How:** past-behaviour questions only, **no pitching** until the close (`discovery-interviews.md`). Optional: 3 venue conversations about off-peak slots and group discounts.
- **Measures:** current spend on helping guests find things to do; whether a budget owner is named; the strongest pain quote; commitment (none / introduction / unpaid pilot).
- **Read-out (confirmed, D57):** ≥ 2 of 5 already spend money or staff time on this, **and** ≥ 2 of 5 give an introduction or agree to an unpaid pilot.
- **Workbook:** the results replace the `B2B` guesses (plans per client, sales hours, price range) and feed `Path50k`, where B2B closes the gap to £50k.

## Trip payments during Phase 3 (Area 18)

- **No trip money goes through us.** Any trip in the weekend test or Test C is paid as attendees arrange it themselves.
- **Ask attendees:** "How did you split the costs? Did anything go wrong?" Record the answers in the notes columns. This informs the Stripe Connect direct-charges design (host or venue as the merchant).

## Analysis (Claude-assisted, ~1.5 founder hours)

- **Proportions** with Wilson 95% intervals. With n ≈ 12, a 70% rate has an interval of roughly ±25 points, so read passes as "consistent with", not proof.
- **Medians** of 1–5 items, with a count at each level.
- **Voice vs text:** side by side, descriptive (samples too small for tests).
- **Residents and visitors (D116):** every Test B and Test A result is for residents (London and the rest of the UK); visitors are reported beside them, descriptively.
- **Conjoint:** a pooled binary logit on 120 choices, as a sign and magnitude check.
- **Worth the money (D127, descriptive):** "Was today worth what you spent on it?" (not quite / yes / more than that) and "Would you do this day again?" (yes / no), asked once a day is done, by kind of plan. This is the product's second outcome, which nothing measured before.
- **Checkpoint 3** (`results.md`):
  - results vs thresholds;
  - top 5 quotes and top 5 objections;
  - onboarding changes;
  - build v0 / redesign and retest / stop.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Friends and family inflate scores | Separate launch channel (D43): tag on sign-up ("how do you know me?"); thresholds and K on strangers only; report friends and family side by side |
| Wizard of Oz is smoother than software will be | Keep Abram's replies to scripted prompts; note every improvisation. Log every edit to the planner's draft plans |
| Novelty effect in Test C | Unprompted second-plan requests over 2 weeks are the real signal |
| Test D traffic is too low for two arms | If there are fewer than ~100 visits per arm after 2 weeks, report the pooled rate and treat the arm split as descriptive |
| Participants volunteer health or allergy details | The script says we don't need them; don't record them; delete them from transcripts |
