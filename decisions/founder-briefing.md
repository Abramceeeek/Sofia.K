# Founder briefing: where we are, what's true, and what I'd do

*For Abram. Written 2026-09-26, after decisions D1–D64. **Updated 2026-09-27 for D86 (Test E postponed; see the box below), and 2026-09-28 for an early signal from friends (§2c, D98).** Plain English on purpose. Anything marked **(my judgement)** is my opinion, not something a source showed. Everything else comes from the research notes (`research/notes/`, 311 sources) or the model (`economics/unit-economics.xlsx`).*

---

## The short version

- **The idea holds up in part.** The research backs the core bet: personal preferences differ, a short onboarding can learn some of them, and a solver plans better than an AI chat on its own.
- **Two of your assumptions did not survive:**
  - Learning taste from ten of your own photos adds almost nothing.
  - "Remember the best moment and the ending" is weak for full days out.
- **The idea itself is not unique.** Google, Mindtrip and Layla already plan trips for free, and Explorest and Komoot already do parts of "moments".
- **What could be yours** is learning how each moment *actually felt* for each person, from their ratings, and getting visibly better each time. That is only defensible once you have a lot of ratings.
- **The next month decides it.**
  - **Test B:** does a personal plan beat a good generic one for strangers?
  - ~~Test E: will businesses pay?~~ **Postponed until v0 exists (D86)**, then run with a working demo after Test B, before any business-only build.
- **Money is the weakest part.** No path to £50k a year fits your 7.5 hours a week without help, and the consumer-only path needs people to spread the app far more than is typical (my judgement).
- **My verdict:** worth pursuing to the 9 November checkpoint, with a real stop/go there. Not yet worth betting on as a £50k business.

> **Untested assumption (D86): businesses will pay.** The model's main money line is business clients (D37): hotels, tourism bodies, employers and Uzbek agencies buying plans for their guests. **No business has been asked yet.** Test E (5 interviews) is postponed until v0 exists, so it can run with a working demo, after Test B and before any business-only build work. Until then, every business number below is an assumption, and **this is the main revenue risk.** If Test E fails, the consumer path alone would have to carry the money (§6), and it is the weaker path.

---

## 1. The story so far

**What we set out to do.** Take your idea to an evidence-backed decision, go, change course or stop, in five phases: research, economics, validation (testing with real people), a first version (v0), and testing that version. Your hours are the limit, so every step has an hour cost.

**What I researched (Phase 1, plus light scans).** Twenty areas, 311 sources, 196 of them read directly:
- how to understand a person quickly (conversation, choices, swipes, photos);
- how to turn that into personal weights;
- how to plan a day;
- the wellbeing science;
- competitors;
- money, legal rules, safety and payments;
- finding and scoring "moments";
- automation;
- selling to businesses, including Uzbek travel agencies.

**What was built or prepared:**
- **A cost-and-revenue model** (spreadsheet): what each user costs, what each revenue idea earns, and how many users or clients £50k needs. It's paused now (D52).
- **A test kit for Phase 3**, ready to use:
  - the interview script;
  - the consent form and privacy notice;
  - the 10 "this or that" questions;
  - a landing page that tests two prices;
  - the business interview guide;
  - a results sheet that scores each test against its pass mark.
- **The backend ("the brain")**, a first draft:
  - it stores moments and learns each person's weights from their answers and ratings;
  - it plans a day with a proper solver;
  - it lets people delete their data and sends safety alerts to a person;
  - 28 automated checks pass;
  - nothing is live yet.
- **A 22-screen list for your designer**, and an iOS plan with hours.

**What changed along the way:**
- **Places became moments** (D9). The walk out of South Kensington tube *is* the experience.
- **Photo taste was dropped** from the first version, and so were the photo pairs in testing (D16), because the evidence was weak (see §2).
- **"Best moment and ending" became an optional setting, off by default** (D15).
- **Typing became an equal choice to voice** (D4). Asking people for voice answers loses about half of them.
- **Telegram bot → native iPhone app** (D50). The app is built on GitHub Actions, and testers get it through TestFlight, Apple's beta-testing app (D64).
- **Consumer-first → business-first as the main money line in the model** (D37). Hotels, tourism bodies, employers and Uzbek agencies would buy plans for their guests. **Test E decides whether this holds. It now runs after v0 exists, with a demo (D86), so until then this is an explicit, untested assumption.**
- **Paid group trips were dropped for year one** (D37). The legal gates, safety duties and moderation hours made them the wrong first step.
- **Safety cover:** you, within a few hours, plus a named backup helper (D46, D55).
- **Tests A–C run by hand**, and the checkpoint stays in November (D63). The app is built alongside.

---

## 2. Your idea vs what the research found

Your idea had five parts. Here is each one, honestly.

### a) Understand each person deeply: photos, past places, "this or that" choices, and a conversation

| Part | Verdict | How strong |
|---|---|---|
| **Conversation** | **Confirmed.** Chat-style surveys collected 39% more information than forms (N≈600). An AI interviewer produced 148% more words than a text box, and 55% of people would choose another AI interview (N=354). | Good: several controlled studies |
| **Voice answers** | **Weakened.** Voice answers are richer, but *asking* for voice lost 45–51% of people, against 13–24% for text. So typing must be an equal option, not a fallback. Speech-to-text also makes things up in about 1% of cases, so the app should read back what it heard | Good: large survey experiments |
| **"This or that" choices** | **Confirmed, with limits.** Ten choices roughly halve the error in a person's weights compared with knowing nothing, in a standard simulation. That's real, but early weights are still rough guesses | Moderate: simulation plus industry practice, not our own data |
| **Past places ("Loved it / Didn't enjoy it")** | **Confirmed as a method.** The places must be familiar *and* divisive, or people can't answer | Moderate |
| **Photos (your own ~10 photos)** | **Contradicted.** On a standard benchmark, learning from 10 of a person's photos improved a generic "is this a nice photo" model by only 0.006 on a 0–1 scale. Predicting from their 10 photos alone was much *worse* than the generic model | Good, for photo liking. Nothing links photo taste to *enjoying a place* |

**Something better the research points to:**
- A 15-minute conversation plus choices is enough to *start*.
- **The real learning comes afterwards, from one-tap ratings of each moment.** What people *say* they enjoy differs from what they actually enjoy.
- Onboarding gets you in the door, and the ratings make it personal.

### b) Trip satisfaction as an equation with personal weights

- **Confirmed as an approach.**
  - Think of it as a "person-specific scoring rule": each person starts at the average of similar people and moves toward their own weights as they answer and rate.
  - The statistics are standard and well tested. Two ways of doing it give nearly the same answers, so the method isn't the risk.
- **Confirmed: thresholds matter more than straight lines.**
  - UK transport appraisal already treats walking and waiting as more painful than riding.
  - Heat has standard comfort bands.
  - Your "15 minutes fine, 50 ruins it" fits that.
- **Weakened: "interactions matter most" (rain × outdoors, heat × walking).** They probably do, but **they can't be learned per person from 10 choices**. We estimate them for everyone together.
- **Weakened: the "best moment and ending" rule (peak–end).**
  - It holds for short, simple experiences.
  - For holidays and multi-part days, the *average* predicted memory as well or better (two studies).
  - So it is a switch that is off, and your ratings will test it.
- **Something better:** the AI should only write the explanations; a solver (maths software that finds the best set and order of stops within time limits) should choose and order them.
  - Evidence: AI chat models on their own passed **0.6%** of hard travel-planning tasks.
  - Paired with a solver, they passed **93.9%**.
  - The brain is built that way.

### c) Moments, not places

- **Partly confirmed.**
  - Nobody I found curates city moments with the approach and timing as part of the experience.
  - Close cousins exist:
    - Komoot routes you to the start of a trail segment "so you experience it as intended";
    - Explorest gives photographers the exact spot and the best light;
    - VoiceMap times audio to a walk.
  - So the format is proven in niches, just not for city days out.
- **Mixed evidence on the "reveal" itself.**
  - "The promise of more ahead" was the strongest predictor in one classic study of scene preference.
  - But across 28 published articles its effect swings from clearly negative to clearly positive.
  - Narrow spaces measurably make people tense; whether the release *after* feels better is untested.
  - **That makes it a personal weight to learn, not a universal truth**, which fits your premise that people differ.
- **Confirmed: awe and nature** have validated measures and field evidence. A weekly 15-minute "awe walk" raised joy in a small trial (60 older adults).
- **Something better:**
  - Score reveals automatically from street maps (how suddenly the view opens as you walk), and use your ratings to check it (Area 14, later).
  - Find candidate moments in open-licence text such as Wikivoyage and Geograph. **Reddit and Tripadvisor terms forbid this** for a commercial product.
- **An early signal from friends (28 Sep, D98).** Asked for their favourite London moments, several friends described the moment features **without being prompted**:
  - **transitions:** walking out of busy streets until the river opens up;
  - **slow against fast:** standing still while the city rushes past;
  - **evening lights:** Chinatown's lanterns, and Tower Bridge at sunset.
  - **How much it counts:** these are friends, not strangers, a handful of people, and one message each. It is early qualitative support that the features match how people describe good moments, **not evidence that a personal plan wins.** Test B still decides that.

### d) "Every person gets trips that make them feel different"

- **This is the part with no direct evidence yet.** Everything above says it *could* work. Nothing says a stranger will feel the difference after a 20-minute onboarding.
- **Test B is the whole ballgame:** a blind choice between your personal plan and a good generic plan, with a pass at 7 of 10.
- **(My judgement:)** the gap may be smaller than you hope for a first plan, because the early weights are rough. The loop (rate, then a better next plan) is where the difference should grow, and v0 can't show that until Phase 5.

### e) Shot cards and "photo potential"

- **Kept for about 20 moments.** Explorest shows photographers value this.
- **Unknown for general users.** Test A asks how much photos matter and whether a shot card would make a moment more appealing (1–5).

---

## 3. Where the uniqueness comes from

**What the others do:**
- **Google (Gemini/Maps), Mindtrip and Layla** (now owned by Expedia) turn a chat into an itinerary for free or cheaply, often with booking.
- **Wanderlog** does group planning on a map.
- **WeRoad, Flash Pack and Timeleft** show strangers will travel or meet together, with paid human organisers.
- **Explorest, Komoot and VoiceMap** each do one slice of "moments".

**What's different here:**
1. **Moments with the approach and timing built in**, for city days out.
2. **A personal scoring rule with named reasons**, for example "we swapped the walk for the boat because heat and long transfers affect you most".
3. **Learning from how each moment actually felt**, rated on the spot, and feeding that back into your weights.

**Is it defensible? Honestly, not at first (my judgement):**
- **The idea is easy to copy.** Google could add "vibe" prompts cheaply.
- **The first 50 moments are copyable** with a few weeks of curation.
- **The named reasons are copyable** too.
- **What is hard to copy is the data:** thousands of "this moment, this person, this weather, this rating" records. Until you have them, you have no moat (a lasting advantage others can't easily copy), only a head start and taste.

**The one thing to get right:**
- **Get people to rate each moment, and make the next plan visibly better because they did.**
- That loop is the product, and it is the only asset competitors can't get by prompting a chat model.
- The first plan must be good enough (Test B) for people to reach the second.

---

## 4. Is it doable?

**Hours (your time; Claude writes most of the code):**

| Phase | Your hours | When |
|---|---|---|
| Tests, by hand (Phase 3) | ≈ 24 | Now until the **9 Nov checkpoint** |
| First version (v0): iPhone app + backend | ≈ 56.5 | About 8.5 h before the checkpoint, the rest mid-Nov to late Dec |
| Test v0 (Phase 5) | 10 | January, through TestFlight |
| **Whole plan** | **≈ 114.5 in the window** | About **1.3 weeks past the 14-week window** |

- **Skills fit well:**
  - the statistics are your home ground;
  - you've shipped an iOS app through GitHub Actions before;
  - Claude writes the code, and you review and test it.
- **Helpers:** none counted (default 0). The designer's hours are theirs. The backup helper is for safety cover only. Both sign the contributors agreement first.
- **"Build in parallel" in practice:** until the checkpoint, your weeks are full with testing. Claude can write code in parallel, but your review and testing hours on the app mostly start after 9 November. That's fine: it keeps the stop/go decision cheap.

**Biggest technical risks:**
1. **The moments themselves.** Plans are only as good as the 50 moments and their details (exit, route, timing). That is your curation time, estimated at 5 h, which is **probably optimistic (my judgement)**.
2. **Early plans may not feel personal** because the weights start rough (see §2d).
3. **Travel times.** The planner currently guesses walking time in a straight line. Real walking and Tube times need precomputed tables. TfL's rules on storing journey results haven't been read yet.
4. **Building without a Mac.** Every check of the app goes through a GitHub Actions build and then your phone, which is slower. +3 h is budgeted. GitHub's Mac build minutes may cost more than Linux (UNVERIFIED on your plan).
5. **Explanations that don't match the maths.** The app writes explanations from what actually drove the choice, and checks them against it.

**Non-technical blocker to clear first:** your Apple outside-activities policy and the IP (invention) clauses in both job contracts. You're checking these this week. If either restricts building or publishing an app, it changes everything else.

---

## 5. Will it bring real value to people?

**Evidence that people want something like this (all indirect):**
- 25% of travellers want to start a search from a *mood* rather than a destination (a 2026 survey of 4,300 travellers in 9 countries, including the UK).
- People pay to meet strangers (Timeleft) and to travel with them (WeRoad raised $58M; Flash Pack runs groups of about 12).
- The wellbeing effects are real:
  - holidays help, but the benefit fades within 2–4 weeks;
  - people are happier *before* a trip than non-travellers;
  - nature restores attention;
  - awe lifts mood.
  - These support **short, frequent, well-chosen days out**, which is your product.

**What is still unproven, and which test answers it:**

| Unknown | Test | Pass mark |
|---|---|---|
| Will strangers finish the onboarding and feel understood? | **A** (chat) | ≥ 70% finish; "felt understood" median ≥ 4/5 |
| Does a personal plan beat a good generic one? | **B** (blind A/B) | ≥ 7 of 10 prefer it |
| Will they actually use it on a real day and come back? | **C** | ≥ 40% use it; ≥ 30% ask for a second plan unprompted within 2 weeks |
| Would they pay, and at what price? | **D** (landing page, no money taken) | ≥ 10% sign up; ≥ 20% of sign-ups pick a priced option |
| Will businesses pay for plans for their guests? | **E** (5 interviews) | ≥ 2 of 5 already spend on this, **and** ≥ 2 of 5 commit to an intro or an unpaid pilot (D57) |
| Will strangers turn up to trips posted by someone they don't know? | **Your weekend test** | ≥ 3 strangers join and turn up |
| Do ratings make the *next* plan better? | **Phase 5** (v0 in TestFlight) | Not measurable before v0 |
| Do reveals, awe and so on matter to people? | Ratings, over time | Needs volume |

**Caution:** with about 12 people, a 70% pass is "consistent with" success, not proof. The uncertainty is roughly ±25 points either way.

---

## 6. Can it make money?

**Plain terms:**
- **LTV** (lifetime value): the total money one paying user brings in.
- **CAC** (customer acquisition cost): what it costs to win one paying user.
- **K** (the viral coefficient, "K-factor" in the tables below): how many new users each user brings in. At 0.5, every two users bring one more.

**Running costs are tiny:** about £0.14 per paying user a month, and £0.32 to onboard someone. **The problem is getting paying users, not serving them.**

| Path | What has to be true | Honest picture | Confidence |
|---|---|---|---|
| **Consumer subscription** (e.g. £4.99/month) | People pay after a free plan, and spread it | At normal conversion (2.1% of sign-ups pay) a payer is worth ~£24, and ads cost ~£375 per payer. So **ads don't work.** Posting in groups works but costs about 5 of your hours per payer. For £50k from consumers alone, each user must bring in 0.98 new users (standard price) or 0.53 (£9.99 with a paywall) | **Low.** Spread that high is unusual for a planning app (my judgement; no source). In the app, subscriptions likely go through Apple's in-app payments (15% fee for small developers), which is better than Telegram's ~38% cut but still a cut |
| **Business clients** (£200–500 a month each) | ≥ 2 of 5 interviews show spend and commitment; a price anchor of £200+; account time nearer 1 h than 3 h a month | £50k ≈ **12 clients at £350**. Uzbek agencies can pay a UK company easily (card or bank transfer), with a tax certificate first (D58). But **every number is a guess** until Test E, which now runs after v0 exists (D86) | **Medium-low.** A plausible model with zero customer evidence yet. **An explicit, untested assumption and the main revenue risk (D86)** |
| **Paid group trips** (a fee per attendee) | Legal gates, insurance, safety set-up | About £15 per trip, but lots of moderation hours. **Dropped for year one** (D37) | Low for now |
| **Venue partnerships** | Venues give group discounts | £50k would need ~99 venues. A user benefit, not a revenue line | Very low as revenue |
| Pay per plan, affiliate links, promoted listings | — | **Ruled out:** fees eat pay-per-plan; affiliate links earn about as much as a plan costs; promotions conflict with honest ranking | — |

**The combined path the model prefers:** business clients as the main line, with the consumer app as the product that makes it work, K = 0.3 and some automation. Even then:
- **it needs ~450–530 hours a year against your 390** (7.5 h a week);
- that means **~2.6–4.2 helper hours a week**.
- **No £50k path fits your hours alone.**

---

## 7. My overall verdict (my judgement throughout)

**Worth pursuing to the 9 November checkpoint: yes.** The tests are cheap (about 24 of your hours), well designed, and they answer the questions that matter. **Worth committing to as a £50k business today: not yet.** That depends on Tests B and E, and Test E now comes after v0 (D86).

**The three biggest reasons for:**
1. **A real gap.** Nobody learns how *moments* feel for each person from their own ratings. The AI itinerary space is crowded, but not at this.
2. **Cheap to run and to test.** Pennies per user, a clear kill switch in six weeks, and a product that suits your skills (statistics) and experience (you've shipped iOS).
3. **A plausible business buyer.** Hotels and agencies already spend time helping guests choose what to do, and the Uzbek agencies' payment path is solved. Test E will say whether they'd pay. It runs with a working demo once v0 exists (D86); until then, this is assumed.

**The four biggest risks:**
1. **The personal plan may not beat a good generic plan** for a stranger (Test B). If it doesn't, the premise fails.
2. **Distribution and hours.** Every consumer costs your time to find, spreading would have to be unusually strong, and no £50k path fits 7.5 hours a week.
3. **Businesses paying is assumed, not tested (D86).** It's the main revenue risk: the model's main money line rests on it, and Test E now waits for v0.
4. **Your employment, and copying.** The Apple policy or IP clauses could restrict you, which you're checking now. And big players can copy the idea cheaply, so the moat is only data you don't have yet.

**What I would do differently if it were my decision:**
- **Run Test B first and fastest.** Two plans, blind, to 10 strangers within two weeks, before any more building. It's the single most informative test.
- **Hold app building (beyond what's drafted) until Test B reports, and any business-only building until Test E reports (D86).** The current plan already keeps only about 8.5 of your hours before the checkpoint, which is close to this.
- **Pick one first customer type for v0.** Either "Londoners' day off" or "hotel guests" (if Test E is strong); not both. They need different screens, content and selling.
- **Line up helper hours early** (a contributors agreement for someone), because every money path needs them.

---

## 8. What happens next

**The next three steps:**
1. **This week (you):**
   - the Apple outside-activities policy check and the IP-clause check in both contracts;
   - if either blocks you, stop and we re-plan.
2. **Weeks of 28 Sep – 12 Oct:**
   - confirm the 6 "this or that" factors and the 16 swipe places;
   - do one walk to fill the seed moment's gaps;
   - ~~recruit and run the 5 business interviews (Test E), then the business-vs-consumer decision note~~ **postponed until v0 exists (D86)**; those hours go to moment cards and Test B;
   - ~~the designer signs the agreement and gets the brief~~ (dropped, D81: you design v0 yourself after Test B).
3. **Weeks of 19 Oct – 9 Nov:** run **Tests A–D by hand**, then **Checkpoint 3 on 9 Nov**: go, change course or stop.

**Meanwhile (Claude, when you say go):**
- set up the GitHub Actions builds (the iPhone app on a Mac runner, backend checks on Linux, iPhone builds only when the app folder changes);
- keep drafting the backend.
- *Not started in this message, as you asked.*

**What I need from you:**
- The results of the two employment checks.
- **Which chat app for Test A?** The materials assume Telegram.
- The factors and swipe places confirmed, and the seed-moment walk done.
- The backup helper named and signed before any external TestFlight build.
- The signing certificate, provisioning profile and App Store Connect key in GitHub Secrets, when we start the build.
- **Accept the 1.3-week overrun, or give some hours to a helper?**
