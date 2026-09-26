# Phase 3 test plan

**Order (D36):** Test E (B2B discovery) runs **first**, then the decision note `decisions/b2b-vs-consumer-first.md` (D40), then Tests A–D.

**Sample:** 12 completing **strangers** (recruit 14). Record the source of each, since that is the distribution signal. Adults 18+ in or near London. Test B needs ≥10 strangers who finish Test A for the "7 of 10" threshold.

**Friends and family are a separate launch channel (D43).** They are welcome, tagged `friends & family` in the results sheet and reported separately. **Every threshold and K are measured on strangers only.** Rule: anyone Abram knows, or who was sent by someone he knows, counts as friends and family.

**Principle:** no code except the Test D page. Abram plays "the system" (Wizard of Oz). Participants are told a person runs the chat, and that AI helps draft summaries and plans (`consent-form.md`).

## Pass thresholds (D2, D18)

Every Test A metric is reported **overall, and separately for voice and text** (D4, D18).

| Test | Metric | Pass |
|---|---|---|
| A | Onboarding completion (finished the read-back) | ≥ 70% |
| A | "I felt understood" (1–5) | median ≥ 4 |
| B | Prefer the personalised plan (blind) | ≥ 7 of 10 |
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

## Test A — onboarding (Wizard of Oz on Telegram)

- **Mode:** the participant chooses voice notes or typing and can switch; record the first choice (D4). Voice notes are transcribed **locally** (open-source Whisper) and audio is deleted once transcribed. The opt-in keeps it 30 days for accuracy spot-checks (D3).
- **Layers**, in order (`interview-script.md`):
  1. best hour of the last trip, with an "anything else?" follow-up;
  2. why they travel (tap up to 2);
  3. 16 London swipe items;
  4. 10 "this or that" plans (`conjoint/design.csv`);
  5. personal context, including the optional food question (D19) and "where you grew up" (place type, optional);
  6. two photo questions and an example shot card (D16);
  7. **read-back**: "Here's what I heard — did I get that right?";
  8. short survey.
- **Measures:** completion; minutes from first to last message; drop-off layer; the survey items; open answers.

## Test B — plan quality (blind)

- **Same brief for both plans:** same city, same day length, same budget, same number of stops, same format and length.
  - **Personalised:** drafted by an LLM from the read-back profile and a list of London moments Abram knows (seed moments first). Abram checks it.
  - **Generic:** a top-attractions plan written once and reused.
- **Labels A/B come from the pre-randomised list** in `results-sheet.xlsx` (balanced 50/50, fixed seed).
- **Measures:** which they prefer and why; "This plan fits me" (1–5) for each.
- **Trip intent** (Area 15) is asked just before: "recharge or explore?", "who's coming?", "one must-do?". It is stored with the plan (D27).

## Test C — actual use (plus virality, D23)

- **Offer the personalised plan** for a real day or weekend. If they clearly preferred the generic one, let them choose, and record which.
- **During the day:** after each stop they send one number, 1–5. Log the message time, the weather (look it up afterwards) and the travel time from the plan.
- **"Bring a friend":** the plan message includes a line to forward to a friend, with a personal referral link (`?ref=P07`).
- **Share prompt after the shot-card moment:** "Got a shot you like? Share it if you want — here's a link friends can use to try this." Same referral link. **We never ask for the photo.**
- **After the day:** "Would you go again?"; "How did it feel?"; "Did you invite anyone? How many?"; "Did you share a photo? Where?".
- **For 2 weeks:** log any unprompted request for a second plan.

**Virality measures:**
- **Invites sent** per participant (self-report, plus forwarded "bring a friend" messages they mention).
- **Invitee sign-ups:** waitlist sign-ups carrying their `ref`, or friends who contact Abram and name them.
- **Shot-card shares** per participant (self-report).
- **K** = invitee sign-ups ÷ **stranger** participants who did Test C (D43). Their invitees count, whoever they are; friends-and-family participants' invites are reported separately. Also report invites per participant, sign-ups per invite and shares per participant.
- **Compare with the workbook** (`Virality` tab): £50k needs K ≈ 0.98 (base) or ≈ 0.69 (upside).
- **Caveat:** with ~12 people, one enthusiastic sharer moves K a lot, so report counts, not just the ratio.

## Test D — willingness to pay (landing page, D1, D2, D25)

- **Its own recruitment post** (D21) and its own visitors. Traffic from study participants (`src=participant`) and from friends and family (`src=ff`) is excluded from the rates and counted separately.
- **Random arm on first visit:** A = £4.99/month or £49.99/year; B = £9.99/month or £99.99/year. Both annual prices are about two months free (D31). The copy says the first plan is free and payment would be asked for after it.
- **Buttons:** "Join the free waitlist", "Reserve founding price (monthly)", "Reserve founding price (annual)". **All three lead to the same waitlist form**, with an honest note: no payment is taken now; we'll email before anything is ever charged.
- **Measures:** visits by arm (GoatCounter); sign-ups by arm and by option (Tally hidden fields); monthly vs annual split.
- **Two sign-up rates:** sign-ups with a `ref` code (invitees) are counted for K, and the Test D rates are reported both with and without them.
- **Meta ads: none** (D26).

## Test E — B2B discovery (5 interviews, D34, D36): runs first

- **Who:** 3 London contacts (a hotel, a serviced-apartment operator, a tourism body) and **2 Uzbek contacts** (a travel agency sending clients to London; a hotel or tour operator in Uzbekistan).
- **How:** past-behaviour questions only, **no pitching** until the close (`discovery-interviews.md`). Optional: 3 venue conversations about off-peak slots and group discounts.
- **Measures:** current spend on helping guests find things to do; whether a budget owner is named; the strongest pain quote; commitment (none / introduction / unpaid pilot).
- **Proposed read-out (Abram to confirm):** ≥ 2 of 5 already spend money or staff time on this, **and** ≥ 2 of 5 give an introduction or agree to an unpaid pilot.
- **Workbook:** the results replace the `B2B` guesses (plans per client, sales hours, price range) and feed `Path50k`, where B2B closes the gap to £50k.

## Trip payments during Phase 3 (Area 18)

- **No trip money goes through us.** Any trip in the weekend test or Test C is paid as attendees arrange it themselves.
- **Ask attendees:** "How did you split the costs? Did anything go wrong?" Record the answers in the notes columns. This informs the Stripe Connect direct-charges design (host or venue as the merchant).

## Analysis (Claude-assisted, ~1.5 founder hours)

- **Proportions** with Wilson 95% intervals. With n ≈ 12, a 70% rate has an interval of roughly ±25 points, so read passes as "consistent with", not proof.
- **Medians** of 1–5 items, with a count at each level.
- **Voice vs text:** side by side, descriptive (samples too small for tests).
- **Conjoint:** a pooled binary logit on 120 choices, as a sign and magnitude check.
- **Checkpoint 3** (`results.md`):
  - results vs thresholds;
  - top 5 quotes and top 5 objections;
  - onboarding changes;
  - build v0 / redesign and retest / stop.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Friends and family inflate scores | Separate launch channel (D43): tag on sign-up ("how do you know me?"); thresholds and K on strangers only; report friends and family side by side |
| Wizard of Oz is smoother than software will be | Keep Abram's replies to scripted prompts; note every improvisation |
| Novelty effect in Test C | Unprompted second-plan requests over 2 weeks are the real signal |
| Test D traffic is too low for two arms | If there are fewer than ~100 visits per arm after 2 weeks, report the pooled rate and treat the arm split as descriptive |
| Participants volunteer health or allergy details | The script says we don't need them; don't record them; delete them from transcripts |
