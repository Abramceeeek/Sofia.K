# ODYS: what it has, what a whole trip needs, and what could come next

*19 October 2026. Written for Abram and for other AI models to critique, alongside `algorithm-explained.md` and the screens PDF (`design/odys-screens.pdf`). Sources were searched on 19 Oct and are listed at the end. Survey figures are as the publishers report them, and most surveys are commercial, which is noted where it matters. Anything not sourced is our own judgement and is marked as such.*

## The decision first

- **Nothing new is built before the stranger tests** (D75). Every idea below goes on `after-9-nov.md` and is reviewed at Checkpoint 3 (week of 23 Nov).
- **Recommended order after Checkpoint 3, if it says go:**
    1. a **morning check-in** ("Still on for today?", one tap);
    2. **more choice in planning** (pick between 2–3 days; build or lock your own);
    3. **a short story at each moment**, written and recorded by people (a "historical guide" without AI);
    4. **plans for friends who already know each other** (shared plan, "I'm in");
    5. **buddies** (strangers matched to go together), only after the safety and legal work below. On 30 Sep you rejected stranger matching for year one, and that stands until you change it. This is research only.
- **The research says:**
    - The core reasons people travel are **novelty, escape and relaxation, and relationships**.
    - Holiday wellbeing rises with **relaxation, savouring and control over your own time**, and fades soon after.
    - Too much choice can demotivate, but **a few good options plus control** helps.
    - So ODYS should **suggest a small number of strong options and let the person steer**, rather than hand over one fixed plan or a long list.

---

## 1. What ODYS has today

| Area | What it does | Status |
|---|---|---|
| **First run** | Welcome, an example day, consent (research and AI permission kept apart), an optional tester code | Built, iOS and Android |
| **Onboarding** (14 questions before the first plan) | Where you're based (never nationality); a great moment (typed or spoken; speech is turned into text on the phone); how you want to feel; 6 places you've been; 5 "this or that" days; "So far, I've learned…" with corrections | Built |
| **Visitors from abroad** | 8 kinds of places instead of London places; their own cohort; "Good to know" (health, transport, entry rules as general information) | Built |
| **Plan a day** | Date, hours, start point (or "where I am", rounded to about 100 m and not kept), number of stops, budget, must-include. The real Tube lines (TfL) and the Met Office forecast | Built; TfL and weather live since 19 Oct |
| **The day** | Stops with photo, time, "why we picked this", worth to you, the way in, opening hours, rain swaps; "How the day moves"; map; swap a stop; plan again; re-plan the rest of today | Built |
| **Now** (during the day) | The stop you're at, what's next, distance (location on the phone only), "I'm done here", rating reminders | Built |
| **Rating** | Flat, Fine, Good, Great or Unforgettable after each stop, kept offline until there's signal; the model refits | Built |
| **Share card** | Your own rating and words, the photo, "Planned with ODYS"; no rewards, never "worth £X" | Built |
| **Improve future plans** | More places and "this or that" days, budget, company, pace and interests, all optional | Built |
| **Trips** | Where and when (calendar), getting there (fly, train, car, already in London), your days (hours, places a day, travel light), feelings; one plan per day with no repeats; arrival and departure journeys; tomorrow's preview; change a day | Built (London) |
| **Book** | Flights (Duffel) and places to stay (LiteAPI) with filters, booked on the provider's own site; "did you book it?" | Built; test data until live keys |
| **Test B** | The blind Plan 1 / Plan 2 pair, the survey, the reveal | Built |
| **Help and safety** | 999 first, a message that reaches a person within a few hours, replies in the app, NHS 111, "something wrong with this place?" | Built |
| **Your data** | What's stored and where, location switch, reminders, Delete my data | Built |
| **Behind it** | Request logs with no personal data, error alerts, rate limits, nightly sealed backups, an uptime check (once GitHub Actions billing is fixed) | Built 19 Oct |

## 2. A whole trip, end to end

| Stage | What a person needs | ODYS today |
|---|---|---|
| **Inspiration** | Ideas that fit them; previews (anticipation is part of the pleasure, per the research foundations in `CLAUDE.md`) | Partly: the example day and the plan itself. No browsing or "save for later" |
| **Where and when** | Destination, dates, length, budget | London only; the dates calendar; a budget band |
| **Getting there** | Flights, trains, coaches, driving | Flights searched; trains and car as arrival modes but **no train search** |
| **Places to stay** | Search, filter, compare against where the days are | Built (LiteAPI), booked on the provider's site |
| **Getting around** | Local transport, times, cost | TfL lines and times; fares estimated |
| **The days** | Places that fit, food, timing, opening hours, weather | Built: the core of ODYS |
| **Things to book** | Tickets, timed entry, restaurants | "Book ahead" notes on cards; **no ticket or table links yet** (#66 parked) |
| **Events** | What's on (concerts, exhibitions, markets) | None (#54 parked) |
| **Money** | Total cost, splitting with friends, worth it | Cost per person; no splitting (and never holding money: Stripe Connect only, later) |
| **On the day** | Changes (weather, energy, closures), directions, what's next | Now, re-plan the rest of today, rain swaps, directions |
| **How the person feels** | Checking in, adjusting | **None yet** (proposal 4.1) |
| **Safety, health, documents** | Emergency help, insurance, entry rules | 999, a person replies, NHS 111, general entry-rule guidance with GOV.UK's checker |
| **Accessibility** | Step-free routes, quieter options | Step-free notes on some cards; no filter |
| **After** | Memories, photos, "would you go again?", sharing | Ratings and the share card; no journal; no "would you go again?" |
| **Company** | Planning with friends; finding people to go with | **None** (proposals 4.4 and 4.5) |

## 3. What people want from trips (research)

### 3.1 Why people travel

- **Push and pull.** Crompton's 1979 model splits motives:
    - **push:** escape from the everyday, exploring yourself, relaxation, prestige, regression, family ties, social interaction;
    - **pull:** novelty and education, plus what the destination offers (climate, nature, monuments). [Secondary summaries of Crompton (1979), *Annals of Tourism Research*.] In one destination study, **rest and relaxation** was the strongest push, followed by nostalgia, escape, novelty and social interaction.
- **Core motives for everyone:** Pearce's travel career pattern names **novelty, escaping and relaxing, and relationships** as important whatever a person's experience. **Nature and engaging with the place and its people** matter more to experienced travellers. [Pearce and Lee 2005, *Journal of Travel Research*; JCU research repository.]
- **What this means for ODYS (our judgement):** the five feelings in onboarding cover these motives: restored and peaceful are escape and relaxation, curious is novelty and learning, excited is stimulation, connected is relationships. **Nature and "local, new-to-you"** should weigh more for people who travel often, which we could learn from a "how often do you travel?" answer.

### 3.2 What makes a holiday feel good, and last

- In de Bloom and colleagues' studies:
    - wellbeing during a holiday rose with **pleasure, relaxation, savouring and control** (autonomy over time and activities);
    - those experiences also predicted **how long the effect lasted** after;
    - the gains **fade soon** after return.
- A separate study found life satisfaction linked to **perceived control, detachment from work, relaxation and mastery** during the holiday.
- **For ODYS (our judgement):** control is a wellbeing driver in its own right, so the plan should feel like the person's own (section 4.2). Short, frequent days out fit the fade-out (already in `CLAUDE.md`).

### 3.3 Choice: a few good options, and control

- **Too many options can demotivate.** In Iyengar and Lepper's field study, a display of 6 jams sold to about 30% of the people who stopped, against about 3% for 24 jams. In a separate experiment, people choosing from 30 chocolates were less satisfied than those choosing from 6. Replications are mixed, so treat it as a tendency.
- **Autonomy, competence and relatedness** (self-determination theory) predicted:
    - taking part in customised travel services (303 tourists);
    - attachment and loyalty to a destination (725 respondents).
- **For ODYS:** offer **2–3 strong options, never a long list**, and let people lock, swap, add and remove. That keeps the algorithm doing the hard work while the person keeps control.

### 3.4 UK travellers now

- **Holidays are the last spend people cut.** In ABTA's survey of 2,001 adults (Jul–Aug 2025):
    - 87% had been on holiday in the past year;
    - using AI for trip inspiration doubled to 8% (13% of 18–24-year-olds).
- **Somewhere new is the top priority.** In easyJet's survey of 2,000:
    - 82% said exploring somewhere new was their top priority for 2025;
    - about half (47%) planned a city break;
    - AllClear (2,000) found 48%.
- **Planning takes long and money worries most:**
    - A sponsored US survey (Go City, 2,000 frequent travellers) reported about **18 hours of planning per trip**. Overspending was the top pain point (44%).
    - Expedia measured about **5 hours with travel content** in the 45 days before booking.
    - Klook found most **group-trip organisers spend more than 10 hours** on one trip.
- **Solo travel:** in Opodo's survey (2,000 of 9,000 from the UK), **freedom** was the main reason for UK solo travellers (32%). **Safety** was the top priority for solo travellers, at 40% in 2026, up from 34% in 2023.
- **Families:**
    - Rest and relaxation, value for money and involving the children recur. A commissioned 2025 study reported 95% of UK parents saying downtime matters, and about half saying their children help decide where to go.
    - Hilton (2022): 62% said it's hard to please everyone.

### 3.5 What each kind of trip wants, and what ODYS could do

*Rows combine the sources above with our own judgement (marked "ours").*

| Kind of trip | What people want | ODYS today | Could add (ours) |
|---|---|---|---|
| **City break** (London now) | Somewhere new; food; culture; not wasting time; value | The core product | Events; ticket and table links |
| **Restorative / slow** | Rest, nature, savouring, control of time | "Restored", "peaceful", relaxed pace with longer stays | A "slow day" switch; fewer stops by default |
| **Solo** | Freedom; safety; maybe meeting people | Safety screen; location only on the phone | Safer-route notes after dark; group activities with strangers only after section 4.5 |
| **Friends** | Shared plan, fair costs, everyone heard | One person's plan | A shared plan and "I'm in" (#69); a plan for the group's combined weights |
| **Couple** | Shared moments, atmosphere | One plan for one person | A plan for two people's weights |
| **Family** | Downtime, value, the children's wishes, pacing | Not designed for it | Child-friendly tags; shorter days; "everyone picks one" |
| **Culture / learning** | Stories behind places, depth | History tags; card text | **Stories at each moment** (4.3) |
| **Nature / active** | Being outdoors, movement | Green and active tags; rain swaps | More outdoor cards, beyond central London |
| **Business plus a free afternoon** | The best 2–3 hours near where they are | Plan a day with custom hours and start | Fine as is |

## 4. Proposals

### 4.1 A morning check-in

- **What:** on a planned day (a day out or a trip day), one quiet notification at a time the person picks (default 08:30):
    - "Morning. Still on for today?" with three answers: **Ready**, **Slow start** or **Not today**.
    - **Slow start** moves the day an hour later and drops the lowest-value stop.
    - **Not today** keeps the plan for another day.
    - With rain likely, it says so and offers the rain swaps.
- **Why:** control over the day is one of the wellbeing drivers (3.2). It is the human check before the algorithm commits a day.
- **Guardrails:**
    - Opt-in; a local notification on the phone; silence counts as "all fine" (calm technology).
    - It asks about **the trip, never mood scores**, so it stays trip wellbeing, not psychological assessment (`CLAUDE.md`).
    - Answers are stored only as plan changes. One a day at most, since research on smartphone check-ins shows burden lowers adherence.
- **Hours:** GUESS Claude ~6 h (both apps, Brain). Builds on the evening-before note (#64).

### 4.2 More choice: steer the plan

- **What:**
    - **"Pick your day":** 2–3 different days from the same model, ranked, each with one line on how it differs ("more outdoors", "quieter", "more food").
    - **"Build it with me":** lock stops you want, remove ones you don't, add from a short list of 3. The planner fills the rest.
    - **"Save for later":** a list of moments you want, which the planner tries to include.
- **Why:** autonomy and control (3.2, 3.3) without long lists.
- **The algorithm stays the same:** these are constraints and different solutions from the same model, so no AI is needed.
- **Hours:** GUESS Claude ~10 h.

### 4.3 A story at each moment (a guide without AI)

- **What:** each card gets a short story, 60–90 seconds: what you're looking at and why it matters. It's written by a person from checked sources and recorded by Abram (or a voice actor). It plays when you arrive, and the text is always available.
- **Existing tools:**
    - Museums often have **Smartify** guides (free app; tours free or paid per venue). VoiceMap and izi.TRAVEL host GPS-triggered walks.
    - ODYS can **link to them** where they exist and write its own only for its moments.
- **Why:** "curious" and history lovers; it deepens the reveal moments; no AI involved.
- **Hours:** GUESS ~1 h per card to research and write, plus ~15 min to record. About 10 cards first (~12 h, mostly Abram's or a writer's).

### 4.4 Plans for friends who already know each other

- **What:** share a plan before the day ("I'm in", #69); plan for two to four people using everyone's weights, with a fairness rule so nobody's least favourite stop is chosen; costs per person.
- **Why:** relationships are a core motive (3.1), and group organisers spend the most planning time (3.4).
- **Hours:** GUESS Claude ~12 h.
- **Risk:** low. People invite people they know.

### 4.5 Buddies: strangers matched to go together (research only)

- **The founder's original idea** (strangers join trips posted by someone they've never met) is still the "weekend test" in `CLAUDE.md`. **Year one says no group trips** (30 Sep), and nothing is built.
- **What the research shows:**
    - Would-be users want **identity verification, detailed profiles and a video call before meeting**. Mismatched budget, pace and schedules cause conflict (an SJSU design thesis).
    - Women-only **Tourlina** screens every new user, and only verified users can chat.
    - Safety habits from dating apps carry over: daylight, busy public places, telling a friend.
    - No independent study shows these apps reduce harm.
- **The law (UK):** letting users contact each other makes ODYS a **user-to-user service under the Online Safety Act**. Ofcom's illegal-content duties need a written risk assessment covering the priority illegal harms (its guidance gives 17 or 18 kinds), with codes of practice, reporting and complaints. This is on top of the contributors agreement for anyone who helps moderate.
- **What a safe version would need (ours):**
    - verified accounts;
    - small groups, never one-to-one;
    - public meeting points;
    - matching on trip, dates, pace and budget, **never on protected characteristics** (`CLAUDE.md`);
    - report and block, and a person answering reports;
    - an Online Safety Act risk assessment;
    - insurance.
- **Hours:** GUESS 60–100 h plus legal advice. Only after Checkpoint 3 and the company.

### 4.6 Other future items

| Item | Why | Hours (GUESS) |
|---|---|---|
| **Train search** (link-outs to UK rail booking, as flights do) | Trains are how many reach London | ~4 |
| **Tickets and tables** (timed entry, OpenTable or TheFork, #66) | "Book ahead" moments | ~3 |
| **"Would you go again?" and "Was it worth the money?"** after a day | The app's second goal has no measure yet | ~2 |
| **Use the unused answers** (company, morning or night, activity) | Collected but ignored (see the algorithm document §11) | ~3 |
| **Accessibility filter** (step-free, quieter, seats) | Inclusion | ~4 plus card checks |
| **More cards** (49 → ~100) and beyond central London | Variety; nature for experienced travellers | ~25 |
| **Events** (what's on, #54) | Novelty | ~6 |
| **A trip journal** (your ratings, photos and words, private) | Savouring after the trip (3.2) | ~6 |

## 5. Questions for the reviewing AI

1. Which **one** of the proposals in section 4 would most improve a first-time user's trip, and why?
2. What would you **remove** from the app as it is (section 1) to make it simpler?
3. Are we missing a stage of a trip (section 2) that matters more than the ones listed?
4. How would you give people **more control without more taps**?
5. Is a morning check-in welcome or annoying? How would you design it so people keep it on?
6. For **buddies**, what is the smallest safe version, and what would you never do?
7. Would you build our own short stories at each moment, or link to existing guides?
8. What would make ODYS **clearly better than asking a general AI chatbot** to plan a day in London?

---

## Sources (searched 19 October 2026)

- Crompton (1979) push and pull motives, via secondary summaries: [Turiba conference paper](https://m.turiba.lv/storage/files/studzinkonf-narmin-nazirova.pdf); [Revista de Turismo, Universidad de Murcia](https://revistas.um.es/turismo/article/download/290391/212321/1011991)
- Pearce's travel career pattern: [Pearce and Lee 2005, JCU](https://researchonline.jcu.edu.au/6740); [Travel Career Pattern Theory, JCU](https://researchonline.jcu.edu.au/74336/)
- Holiday wellbeing: [de Bloom et al. 2013, *Journal of Happiness Studies*](https://link.springer.com/article/10.1007/s10902-012-9345-3)
- Choice overload: [Iyengar and Lepper 2000, summary](https://andrewclark.super.site/all-media/when-choice-is-demotivating-can-one-desire-too-much-of-a-good-thing); [replication notes](https://www.atticusli.com/replication-crisis/choice-overload-jam-study/)
- Self-determination theory in tourism: [custom travel services, IJCHM](https://emerald.com/insight/content/doi/10.1108/IJCHM-05-2021-0563/full/html); [destination loyalty, Southampton](https://eprints.soton.ac.uk/500225)
- UK travellers: [ABTA Holiday Habits 2025–26](https://www.abta.com/industry-zone/reports-and-publications/abta-holiday-habits-reports/holiday-habits-2025-26); [easyJet Great British Holiday Audit](https://www.easyjet.com/en/news/story/the-great-british-holiday-audit); [AllClear 2025 trends](https://allcleartravel.co.uk/blog/2025s-biggest-travel-trends-for-brits)
- Planning time: [Go City survey (sponsored)](https://newsroom.gocity.com/2024-12-12-Travelers-Underutilize-Technology-When-Trip-Planning,-Missing-Opportunities-to-Save-Time-and-Money-According-to-Go-City-Consumer-Survey); [Expedia Path to Purchase 2023](https://news.gtp.gr/2023/08/02/travelers-spend-over-5-hours-researching-trips-says-expedia/)
- Solo travel: [Opodo survey via Travel Extra](https://www.travelextra.ie/i-want-to-break-free-opodo-releases-results-solo-travel-survey/)
- Families: [Experience Abu Dhabi study (commissioned), Globetrender](https://globetrender.com/2025/06/18/alpha-influence-kids-call-holiday-shots/); [family priorities summary](https://fifetoday.co.uk/read-this/affordability-rest-and-relaxation-and-access-to-a-pool-among-british-families-top-holiday-priorities-3709050)
- Check-in burden: [van Genugten et al. 2020, PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7073581/)
- Buddies: [TabiSubi thesis, SJSU](https://sjsu.edu/design/graduate-programs/experience-design-master/student-work/jimmy-shih-2026.php); [Tourlina, App Store](https://apple.co/2F6jO2n); [Essence](https://www.essence.com/lifestyle/tech/the-upgrade-4-apps-for-women-who-travel-solo); [travellers using dating apps](https://bendbulletin.com/2018/12/23/travelers-use-dating-apps-to-find-recommendations-in-new-places)
- Online Safety Act: [Ofcom, illegal content duties](https://www.ofcom.org.uk/online-safety/illegal-and-harmful-content/illegal-content-duties-under-the-online-safety-act); [Ofcom risk assessment quick guide](https://www.ofcom.org.uk/online-safety/illegal-and-harmful-content/quick-guide-to-online-safety-risk-assessments/)
- Guides: [VoiceMap, App Store](https://apps.apple.com/app/id852027939); [Smartify free plan](https://smartify.org/partners/free-plan); [Ashmolean on Smartify](https://ashmolean.org/smartify); [izi.TRAVEL via AlternativeTo](https://alternativeto.net/software/narrando)
