# ODYS journey audit: from the first open to the flight home

*Written 7 Oct 2026. Abram asked for "a logical real journey from the time they start onboarding or plan their first trip to finishing the trip", checking whether it's easy to go back and forth, whether every need is covered, and whether it beats the free services people already use, so that they'd pay for it. Method: a live run on the Brain (a throwaway install, deleted after), a code trace of every screen and button in `app/Sources/`, a check of 18 traveller needs against the code, and a scan of the free and paid alternatives as of 2026. Sources are in `research/sources.csv` (area `journey`, read 7 Oct); anything not checked is marked UNVERIFIED. Hours are GUESSES unless they say otherwise.*

## The decision first

**Verdict: the journey is logical from onboarding to the plan, but it breaks during a trip, and today it is not easier than the free options for planning.**

1. **Where ODYS is already better:** each day is built from checked moments, not from guesses. The cards have real opening days, the way in, the light, a rain swap and the cost. A day respects the person's own hours, and a trip starts from where they land and ends at the airport or station, with directions. This is the gap the free AI planners leave open. In one test, **90% of ChatGPT's two-day city plans had at least one error, 24% sent people somewhere closed, and 52% put a stop outside its opening hours** (SEO Travel, May 2024; an agency's test, not peer-reviewed).
2. **Where it is worse:**
   - **The first plan comes after about 25 prompts**, where Gemini, Google Maps' Ask Maps or ChatGPT give a plan from one sentence.
   - **A first open can wait 43 s** while the free server wakes.
   - **During a multi-day trip, the app forgets which day it is.** The person has to tap "Make this my day" every morning, and "That's the day" leads nowhere.
   - **Bookings stay outside the app.** TripIt and Wanderlog collect them from your emails.
3. **What people pay for in travel apps is help during the trip,** not the itinerary. TripIt Pro (£38.99 a year in the UK App Store) sells live alerts; Wanderlog Pro sells Gmail import and Maps export; the AI planners (Mindtrip, Layla, Gemini) are free and earn from bookings. Travel apps have the lowest median yearly price of any category ($20; RevenueCat 2026), but the highest trial-to-paid conversion (43.5%). **So ODYS earns its price if the day it plans works on the day:** checked places, the right timing, the trip carried morning to night, and better with every rating. The plan alone won't earn it.

**What I did now (Claude, under D69, no scope change):** fixed the 12 bugs below that break the journey or lose test data; Claude ~9 h; Abram ~15 min to try the new build. **What needs Abram:** 5 decisions (bottom of this page). Everything else is ranked for "before strangers" (~27 Oct) or "after Test B" (D75).

---

## 1. The journey, step by step

Live run on the Brain, 7 Oct, free tier (one person, 18 calls, 91.5 s in total).

| Step | What the person does | What they get | Time / prompts | Problem found | Fixed? |
|---|---|---|---|---|---|
| Open | Welcome → example day (or skip) | A real day in London before giving anything | 3 taps | **The server may be asleep: 43 s** on the first call. A "Waking up the planner" note appears after 3 s | Stage 1: a paid server (roadmap decision 2) |
| Consent | Two toggles | Plain summary, details folded | 1 screen | No way back from here | Before strangers: back on each step |
| Onboarding (UK) | Where based → best moment → feelings → 6 places → 5 this-or-that → "So far" | Reactions from the feelings on; "So far" after prompt 14 | 14 prompts, all < 1 s each | **No back between steps** (only inside places and this-or-that). **Feelings were lost if the app was closed** before this-or-that ended | Feelings: **fixed**. Back: before strangers |
| Test B (UK) | Survey (4) → intent (3) → Plan 1 / Plan 2 → choice, "fits me" ×2, why → reveal | Their plan for Saturday | ~11 prompts | **The Test B plan had no date, so "Yes, nudge me" never fired a rating reminder** | **Fixed** (dated for the Saturday it was planned for) |
| Onboarding (visitor) | Same, with 8 kinds of places instead of London places | The Trip tab, **with no plan** | ~23 prompts, then 6 more screens for a trip | Consent promises "then your day plan"; the survey says "Before your plan" | Wording: **fixed**. A first plan straight after: before strangers |
| Plan a trip | Where → when → getting there → your days → feelings → "Make my trip" | All days (up to 7), from the stay, at their hours | 5 screens; **20 s** for 5 days | Dates only 40 days ahead in the strip (the Brain allows 330) | After Test B |
| Book | Flights (3 s), stays (**15 s** fresh, cached 15 min) → "You're going to…" → provider's site → "Did you book it?" | One price found plus links to Skyscanner, Booking.com, Airbnb, Premier Inn, Travelodge | — | **"Did you book it?" was lost if iOS closed the app while they were on the site.** **A chosen flight kept its old times after the trip's dates changed** | **Both fixed** |
| Morning of a trip day | Open the app | — | — | **Nothing offers today's day**; they had to find the trip and tap "Make this my day" | **Fixed**: "Today in your trip" on the Trip tab |
| Out for the day | "Start the day" → Now → "I'm done here" → rate | One stop at a time, what's next, rating | 0.4 s a rating | **A rating made without signal (the Tube) was lost.** **Rated stops were forgotten after a restart, and could be rated twice.** **"I'm done here" before the planned arrival skipped the rating.** **Directions were always walking**, even for Tube legs | **All four fixed** |
| End of a day | "That's the day" | Thanks | — | **Leads nowhere**: no next day of the trip | **Fixed**: "Tomorrow: Day 3" when the trip goes on |
| Later days | "+ 3 more days, planned as you go" | — | — | **Days 8+ of a long trip couldn't be planned once it had started** (the Brain refused a start date in the past) | **Fixed** |
| Last day | Back for bags → "Leave for Heathrow by 15:20" → Directions | The way home | — | Works (D122) | — |
| After the trip | — | — | — | No recap, no "how was it", no "plan the next one" | After Test B (#45) |
| Lost install | Any call | "Isn't registered any more" | — | **A dead end**: nothing let them start again | **Fixed**: back to Welcome |

**Going back and forth:** inside a trip, every screen has a way back, and the Trip and Book tabs keep their place. The weak spots are onboarding (forward only) and Book (no "back to your trip" link; the Trip tab is the way back). Back and close buttons appear four ways ("‹ Back", "‹ Flights", a round chevron, the system one); one style is a polish item after Test B.

## 2. Needs: what a traveller needs, and whether ODYS has it

| Need | Covered? | Next step | When |
|---|---|---|---|
| A day that fits their time | **Yes**: their own hours and places a day (D122) | — | — |
| Getting from the airport or station | **Yes**: 5 airports, 8 stations, rail times, Directions | Say that Heathrow Express isn't in the daily cap (TfL fares 2026) | Before strangers, 0.5 h |
| Places that are open | **Yes**: closed days left out, windows respected. **The hours aren't shown** | Show a clean hours line on each stop (49 cards to tidy) | Before strangers, ~2 h |
| Places that need booking | **Was missing**: Horizon 22 and the Transport Museum need a booked slot; go-karting advises it | **Fixed**: a "Book ahead" line on those 3 cards | Done |
| Rain | Partly: a rain swap per outdoor stop, no forecast | Met Office forecast (roadmap Stage 1 #4, ~4 h) | Before strangers |
| Food needs | **Asked, never used**: the note says "Only used to choose food stops", but no code reads it. "Where did you grow up" says "Only used to guess what will feel new to you", and isn't used either | **Abram's decision 1** | Before friends |
| Emergencies | 999 and a person. **No 111** (urgent but not an emergency; it offers an interpreter) | **Abram's decision 2** | Before friends |
| Entry rules (visa, ETA) | **No**, while the app finds flights from Tashkent and Istanbul. Turkey and Uzbekistan are on the UK visa national list; most other visitors need an ETA (£20) | **Abram's decision 3**: a "Before you fly" card with GOV.UK links, never asking nationality | Before strangers, ~1 h |
| Paying for transport | A fare estimate only | A 5-line card: tap in and out with one card, one card per person aged 11+, overseas card fees, the cap (#34) | Before strangers, ~1 h |
| Step-free, prams, children | Barely: step-free is checked on 4 of 51 cards and never shown; the app is 18+ | Link TfL's step-free guide; show "Step-free" on the 4 checked cards; card age limits | Before strangers (links), after Test B (chips, #46) |
| Without signal | **Now yes for viewing and rating**: the plan and trips are on the phone, ratings wait and send later (fixed). New plans, Book and Directions need data | One line in "Before you fly" | Before strangers |
| Language | English only | Key screens in other languages, checked by native speakers (~10–20 h) | After Test B (new after-9-Nov #59) |
| Evenings | Partly: evening cards; the person sets the end time | "What's on" (#54) | After Test B |
| Companions | The traveller count changes searches and totals; nothing shared | Shared trip, "plan the next one with a friend" (#45) | After Test B |
| Bookings in one place | A saved or booked flight and stay, by hand | Forward a confirmation email to add it (new after-9-Nov #57) | After Test B |
| Clocks going back (25 Oct, the friends round's last day) | All times are London time, and sunset uses the London zone | Checked in the code; plan one day on 25 Oct before the round | Before friends, 0.25 h |

## 3. Against the free and paid alternatives (checked 7 Oct 2026)

| Service | What it does well now | Price | Where ODYS is better | Where ODYS is worse |
|---|---|---|---|---|
| **Gemini trip planning** (Google blog, 6 Aug 2026) | Plans from one request, with live data from Google Maps, Flights and Hotels; reads booking emails in Gmail; "Gemini Spark" can fill in an airline booking and leave you to press "book" | Not stated in the post | Checked moments and timing; how a stop *feels*; learns from ratings | One sentence instead of 25 prompts; reads bookings |
| **Google Maps "Ask Maps"** (US/India Mar 2026; 150+ countries in English from 6 Aug 2026; **the UK isn't named**: UNVERIFIED there) | Chat search in Maps; books hotels and tickets in a few steps; live transit delays | Free | A whole day shaped to you, with an arc | Live transit, every place on earth, reviews |
| **ChatGPT** with the Booking.com and Expedia apps (Oct 2025); in-chat checkout dropped Mar 2026 | Plans and compares hotels and flights in the chat | Free tier; paid plans | Checked places (the 90% / 24% / 52% errors above) | Speed and breadth |
| **Wanderlog** (UK App Store: 4.9 from 3.7k ratings) | Shared trips like Google Docs, offline, budgets and bill splitting; Pro adds Gmail import and Google Maps export | Free; Pro from £4.99 a month or £24.99–£59.99 a year (several prices listed) | Plans the day for you | Sharing, bookings in one place, budgets |
| **TripIt** (UK App Store: 4.8 from 23k) | Forward a confirmation, get the itinerary; offline | Free; **Pro £38.99 a year** (live flight alerts, check-in reminders) | Plans what to do | Bookings and flight alerts |
| **Mindtrip** (free; earns from bookings) | Group chat inside a trip; "Start Anywhere" from a screenshot or link | Free | Checked and personal | Groups, starting from anything |
| **Airbnb** (fall release, 30 Sep 2026) | AI search in plain words (US first), a social travel map | Free | A day plan | Homes, and friends' trips |
| **Citymapper, TfL Go** | Live London transit, disruption alerts; TfL Go's step-free mode | Free (Citymapper Club £1.49 a month removes ads, 2023 price) | — | Getting around: link to them, don't rebuild them |
| **Visit London app** (search results) | Official guide, offline maps, what's on, an itinerary from favourites | Free | Personal and timed | Events and deals |
| **iOS 26 Wallet and Maps** | Boarding passes with live flight status on the lock screen; Maps remembers visited places | Free | — | Use them: add to Wallet and Maps, don't copy them |

**What this means:**
- **Don't compete on breadth or booking.** Google and OpenAI do every place and every booking. ODYS links out (D120), which is right.
- **Compete on "a day that works and feels right for you":** checked moments (open, timed, the way in, booking needs), the person's own feelings, and a day carried through to the end.
- People already trust AI for travel: in 2025, 22% of UK travellers used generative AI in planning (US 33%), and 35% of Britons would consider it. Friends and reviews are still trusted most (Phocuswright; Kayak UK survey, Jan 2025, 2,011 people; both via search results).
- **The share card and the friend link are the right growth path,** since friends are the most trusted source.

## 4. What would make people pay

Evidence, not a price decision (prices are Abram's, and Test D measures them later):
- **Travel subscribers pay for help during the trip:** TripIt Pro and Flighty sell live alerts; Wanderlog Pro sells bookings imported automatically. Itinerary makers are free (Mindtrip, Layla, Gemini) and earn from bookings.
- **Travel subscriptions:**
  - median trial-to-paid **43.5%**, among the highest of any category;
  - **28% of conversions come after week 6**, the longest tail;
  - **about 66% yearly plans**;
  - **the lowest median yearly price ($20)**;
  - **the lowest median revenue a year after launch ($35 a month)**.

  So a subscription alone makes a small business. Most travel apps pair it with commission (RevenueCat, State of Subscription Apps 2026).
- **UK planning pain:** 71% of UK holidaymakers find at least one part of booking stressful (YouGov, Feb 2025, via search). The main challenges are budget (47%), choosing the destination (30%) and coordinating schedules (24%) (Kayak, Jan 2025).

**So the paid version of ODYS would be "the trip carried for you", not the plan:**
- today's day ready each morning, adapted to rain and delays;
- bookings in one place;
- a plan to share with the people you're going with;
- reminders to rate, and the next trip better for it.

The free version keeps one day in London at a time, so people can see that it fits them. This matches Test D's priced option (D1). The commission path stays closed until the company exists (D120).

## 5. Fixes, ranked

### Fixed now (Claude ~9 h GUESS; under D69: bugs and wording, no scope change)

| # | Fix | Where |
|---|---|---|
| 1 | A trip under way can still plan its later days and re-plan; only a finished trip is refused | Brain `api.py` (+ test) |
| 2 | The Test B plan is dated for the Saturday it was planned for, so its rating reminders fire; the blind view still shows no date | Brain `api.py` (+ test) |
| 3 | One rating per stop of a plan: rating it again replaces the earlier one (no double counting in the weights) | Brain `api.py` (+ test) |
| 4 | Ratings made without signal are kept on the phone and sent when it's back ("Saved. It'll send when you're back online") | App `AppModel`, `DayViews` |
| 5 | Rated stops and the person's own ratings are remembered per plan after a restart | App `AppModel` |
| 6 | "I'm done here" on Now always asks for the rating (the person says the visit is over, which is D110's rule) | App `DayViews` |
| 7 | Feelings are saved on the phone as soon as they're chosen | App `AppModel` |
| 8 | An install the Brain no longer knows goes back to Welcome, instead of a dead end | App `AppModel` |
| 9 | "Did you book it?" survives iOS closing the app while they're on the provider's site | App `TripLogic` |
| 10 | A saved flight or stay remembers its trip dates; after the dates change, it says "For other dates" and its times stop shaping the days | App `TripModels`, `TripViews` |
| 11 | **"Today in your trip"** on the Trip tab during a trip, and "Tomorrow: Day N" at the end of a trip day | App `TripViews`, `DayViews` |
| 12 | Directions use public transport when the leg is by Tube or bus; "Book ahead" on the 3 cards that need it; visitor wording ("then plan your trip") | App `PlanViews`, `FirstRunViews`; Brain `moments.py`, `dayplan.py`, 3 cards |

### Before strangers (~27 Oct): Claude ~12 h, Abram ~1 h

1. **A paid server** (no 43 s wait): roadmap decision 2, $7 a month. Abram's go is still pending.
2. **A first plan for visitors straight after "So far"** (a one-day trip near the centre, editable), so visitors see value as early as UK people. ~2 h.
3. **Back on every onboarding step.** ~1.5 h.
4. **Hours line and "Before you fly" / transport-payment cards** (after decision 3). ~4 h.
5. **Met Office forecast** in plans (roadmap Stage 1 #4). ~4 h.
6. **Progress words while hotels load** ("Checking 400 London hotels…", 15 s). ~0.5 h.

### After Test B (D75: on `decisions/after-9-nov.md`)

- **#57:** forward a booking email to add it to the trip.
- **#58:** one sentence in ("a slow Sunday with good food near the river"), on top of the questions.
- **#59:** key screens in other languages.
- **#60:** a short recap at the end of a trip, with "plan the next one".
- **Already listed:** #45 (shared trips and "with a friend"), #46 (step-free and pram chips), #54 ("What's on" tonight).
- **The onboarding length:** Test B locks the short version (D112). A shorter first-plan path ("3 answers, then a plan, the rest later") can be tested after Test B against completion and "felt understood".

## 6. Decisions for Abram

1. **The food and "where did you grow up" questions** ask for data the planner doesn't use, under notes that say it's used. **Recommendation: stop asking both until the planner uses them** (data minimisation; 0.25 h). Or keep them with the note "Saved for later plans; not used yet".
2. **Add NHS 111 to Help & safety:** "Urgent but not an emergency: call 111, and ask for an interpreter if you need one" (nhs.uk). Recommendation: yes; 0.5 h.
3. **A "Before you fly" card on trips with a flight:** that most visitors need a visa or an ETA, with GOV.UK's checker. Never asking nationality. It brings forward after-9-Nov #18 point 2, so check the wording against the Immigration Advice Authority line first. Recommendation: yes, before strangers; ~1 h.
4. **The paid server** (roadmap decision 2): without it, every first open after 15 minutes idle waits about 43 s. Recommendation: yes, before friends ($7 a month).
5. **The payment direction for Test D** (no build now): price "the trip carried for you", not the plan. Recommendation: note it for Test D's wording at Checkpoint 3.
