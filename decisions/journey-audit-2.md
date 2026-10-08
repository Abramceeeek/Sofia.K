# ODYS journey audit, round 2: after builds 53–55

*Written 8 Oct 2026. Abram asked again for "a logical real journey from the time they start onboarding or plan their first trip to finishing the trip", with subagents if useful. Round 1 is `decisions/journey-audit.md` (7 Oct). Method:*
- *two code traces of every screen in `app/Sources/` by subagents: (1) first open to the end of a day out; (2) a whole trip, for a visitor flying in for 5 nights, a UK weekend by train, and a Londoner's day trip;*
- *a live run on the Brain with three throwaway people (24 calls, timed, deleted after);*
- *a local simulation of 36 trip days;*
- *a web scan of what's new since 7 Oct (24 sources in `research/sources.csv`, area `journey`, read 8 Oct).*

*Hours are GUESSES unless stated. Anything not checked is marked UNVERIFIED.*

## The decision first

**Verdict: the journey now holds together from the first open to the flight home, and it is starting to do what free tools don't. It isn't yet easy enough that people would pay.**

1. **What works now:**
   - There is a way back on every onboarding step and on consent.
   - A trip carries on day by day: "Today", "Preview tomorrow" and "Change this day".
   - The arrival and leaving journeys are in the plan.
   - Ratings are kept without signal.
   - The free tools still get places wrong. In 2026 surveys:
     - **16% of AI travel users were sent somewhere that doesn't exist, and 27% got wrong prices or hours** (Greetwell, Aug 2026, 485 US users, commissioned);
     - **25% got outdated or wrong results** (Amadeus, Sep 2025, 9,500 people including the UK).

   ODYS's checked moments are the answer to that.
2. **What still stops it:**
   - **The first plan is slow.** The free server took **42.8 s** to wake again today, and about 25 prompts come before a plan.
   - **The days were thin.** In 21 of 36 simulated trip days (free 10:00–18:00, 3 places), the day waited and **opened with lunch at 11:30**. **Fixed today:** a day that starts by 10:15 now opens with a place. The median first stop moves to 10:27, and lunch and the number of stops are unchanged. The afternoon still ends early (median 15:56) because 3 places is what the person asked for. The app should say "free from 16:00, add a place" (open, 1 h).
   - **Flights and stays are still samples** until Abram adds the keys. **Until today, a visitor whose flight was booked elsewhere couldn't enter it.** They can now.
3. **Almost no app re-plans the day for you during the trip.** Romie (Expedia) is a US alpha; Travierge announced it but it's UNVERIFIED that it shipped. Paid travel apps in the UK charge **£24.99–£59.99 a year**: Polarsteps Plus, Tripsy, Travio, Layla, Rhyme and Flighty. Flighty also sells a **£4.99 pay-as-you-go** option. **So the paid ODYS is "the day carried for you"**: preview tomorrow, change the day, skip a stop, and (next) re-plan the rest of today.

**Done now (Claude ~9 h GUESS, under D69: bugs, wording and honesty, no scope change):** 4 Brain fixes and 24 app fixes, listed in section 2. Build 57 goes to TestFlight once CI passes.

**Needs Abram:** 5 decisions (section 6), about 15 min. Trying the build takes about 15 min more.

## 1. The journey, step by step (as built today)

| Step | What happens now | Found in this round | Status |
|---|---|---|---|
| First open | Intro, welcome, example day, tester code, consent | **The free server took 42.8 s** to wake (live, 8 Oct). Consent had no way back | Back: **fixed**. Server: Abram's decision (paid plan) |
| Onboarding | Where based, best moment, feelings, 6 places, 5 this-or-that, "So far" | **Tapping "Skip the rest" twice skipped all 5 this-or-that tasks.** Going back and answering the best moment again stored it twice | **Both fixed** |
| Test B pair | Survey, the blind Plan 1 / Plan 2, choice, reveal | **If the app closed on the reveal, the next open asked the questions again, then showed no plan, on every launch.** A lost reply to Send gave "already answered" | **Fixed**: the chosen plan becomes their day |
| Plan a day | Date, times, start (Charing Cross or "Where I am"), must include | **An empty plan replaced the current one.** A must-include that didn't fit was dropped silently. "Where I am" worked from Manchester. With no plan yet, "Plan a day" couldn't be reached from the Trip tab | **All fixed** |
| Out for the day ("Now") | One stop at a time, location, rating after leaving | **A closed place or a long queue could only be passed by rating it** (fake ratings). "Start the day" on a plan for next Saturday asked for ratings today | **Both fixed**: "Didn't go? Skip this stop"; a look-ahead without ratings |
| Errors | — | **Errors and the "waking up" note were hidden under any open sheet**, so a failed Help & safety message said nothing | **Fixed** in every sheet that calls the Brain |
| Plan a trip | Calendar (2 taps), getting there, your days, feelings | **A flight booked elsewhere had nowhere to go.** "Elsewhere in the UK" defaulted to "already in London" | **Both fixed** |
| Trip page and Book | Checklist, total, Good to know, flights and stays | **Sample prices weren't labelled on the trip page.** "Good to know" hid entry rules from visitors coming by Eurostar or car. Book failed with a confusing date error once the trip had started. Removing a flight took one tap with no confirm | **All fixed** |
| A day trip by train | Arrive, the day, go home | **It routed them to "your stay (no stay chosen)", with check-in and bags: about 65 min of a 6-hour day** | **Fixed**: the day starts at the station |
| Each morning | "Today · Day N" | **On a travel day, "Plan today" did nothing.** If the app stayed open overnight, it still said "Tomorrow" | **Both fixed** |
| Long trips | Up to 30 nights | **The 49 ready cards run out.** At 13 nights × 3 places, the last days were lunch only but showed as planned | **Fixed**: shown as free days with the reason. More cards is the real fix |
| Last day | Back for bags, "Leave for Heathrow by 15:20" | Only appeared after every stop was marked done | **Fixed**: shown on the last stop |
| After the trip | — | No recap, no "how was it" | After Test B (#60) |

**Going back and forth:** every onboarding step and consent now has a way back. Every trip page and Book has one. Sheets close with Close or Cancel. The styles still differ ("‹ Back", "Close" left or right, the system chevron): one style is polish after Test B.

## 2. Fixed in this round

**Brain** (tests: 160 passed):
1. **A morning opens with a place, not lunch.** For days starting by 10:15, lunch can't be the first stop (`dayplan.py`, `planner.py`). In the simulation, lunch-first fell from 19–21 of 36 days to 0. The first stop moved from 11:30 to 10:27 (median). Lunch and the stop count are the same on every day. Test B (12:00–17:00) is not affected.
2. **Day trips start at the station or the airport link** and end on the way home, with no check-in and no bags (`tripdays.py`, plus a test).
3. **A trip day with only lunch left is a free day**, not a planned one (plus a test).
4. **One best-moment answer per question**, like the places and made-up days (plus a test).

**App:**
- **Test data:** the Test B relaunch; the double skip; one rating send at a time (two loops could drop an unsent rating); a one-day trip asks before replacing the unrated Test B plan; closing "Improve future plans" keeps the answers.
- **Now:** skip a stop; no ratings before the plan's day; the way home on the last stop.
- **Errors** show inside sheets and covers, plus a notice for "your must-include didn't fit".
- **Plan a day:** never replaced by an empty plan; "Where I am" only within about 25 km of Charing Cross; "Plan a day out instead" on the Trip tab.
- **Trips:**
  - a flight you already have (airport and times);
  - "See today" on travel days;
  - free days say why;
  - sample prices labelled;
  - "Good to know" for anyone based abroad (never by nationality);
  - Book says when a trip has started;
  - removing a flight or stay asks first;
  - Today and Tomorrow follow the date after a night away;
  - "elsewhere in the UK" starts by train.
- **Honesty:**
  - The stay's **name** stays on the phone; the days use its location, and the privacy notice and "Your data" say so.
  - The share card no longer puts the app's reason in quotes as "your own words".
  - "You book and pay on their site" replaces "You pay Skyscanner directly".
  - Offline ratings send "the next time you open ODYS with signal".
  - The consent line is softened, because "Where are you based?" can't be skipped.
- **Accessibility:**
  - 44 pt tap targets on the onboarding back link, "Not right", "Watch his short hello", the start chips, Must include, the List/Map and Plan 1/2 switches, "Not now" and "‹ Your trip";
  - the reveal scrolls with large text.

## 3. Still open, ranked

| # | What | Why it matters | When | Hours (GUESS) |
|---|---|---|---|---|
| 1 | **Free time shown:** "Free from 15:56 · add a place" on a day that ends early (re-plans with one more place) | People set 10–18 and see a day end at 15:56 | Before strangers | 1 |
| 2 | **Overnight flights:** a flight landing the next day loses its landing time; day 1 is planned while they're in the air | Breaks visitors' first day once real flights are on | Before Abram adds the flight key | 3 |
| 3 | **The place on the way can't be rated** (arrival day, travelling light) | Loses ratings | Before strangers | 1.5 |
| 4 | **Editing hours or dates re-plans past days**, losing "Change this day" and swaps | Skews data mid-trip | Before strangers | 2 |
| 5 | **Journeys past midnight:** a 22:45 landing shows "23:45 → 23:59"; a 01:30 flight says "leave by 00:00" | Wrong times at night | Before strangers | 1 |
| 6 | **Changing travellers on Book re-plans every day** (20 s, 4 screens) | Slow | After Test B | 1 |
| 7 | **This-or-that after Back** doesn't show the earlier picks | All 5 must be chosen again | Before friends | 0.5 |
| 8 | **The tester code is only on Welcome;** an unknown code says nothing | Friends counted as strangers | Before friends | 0.5 |
| 9 | **Large text:** the "How the day moves" curve and the example day's time column | Labels overlap | Before strangers | 1 |
| 10 | **Regenerate and swap ignore the trip's feelings;** the Brain's limit of 40 excluded places will break swaps on long trips | Long trips | After Test B | 1 |
| 11 | **One style for back and close** | Polish | After Test B | 1 |
| 12 | **Checks only a phone can do:** alerts inside sheets, VoiceOver order, a reminder tapped on a cold launch, the 120/250 m arrival distances, whether the Keychain keeps the code after the app is deleted | — | Abram's iPhone, ~15 min | — |

## 4. Against the alternatives: what changed since 7 Oct

| Service | New | Price (UK App Store unless stated, 8 Oct) | What it means for ODYS |
|---|---|---|---|
| **Layla** (bought by Expedia, 31 Jul 2026) | Chat planner and booker, kept as its own app | £9.99/month, £49.99/year | Big companies are buying planners. ODYS's edge has to be the checked, personal day |
| **Google AI Mode** | Restaurant tables in the UK (Apr 2026, links out to OpenTable, TheFork and others); flight tracking (Aug 2026); hotel booking US only | Free | Meals are now easy on a free tool. Linking ODYS's lunch slot to a table site would match it |
| **TikTok GO** (May 2026) | Book hotels and tours inside videos | US only | Not in the UK yet |
| **Rhyme, Travio** | A saved reel becomes a place, then a day plan | Rhyme £14.99/month; Travio £39.99/year | "Start from what you saved" is a paid feature now |
| **Polarsteps Plus** (Jul 2026) | Replay, stats, up to 10 travel buddies; planning stays free | £24.99/year | Paying for memories and companions, not the plan |
| **Tripsy** | Lock-screen "next activity" | Pro £29.99–£49.99/year | Same idea as #61 (Live Activity for "Now") |
| **Flighty** | Live Activities are a paid (Pro) feature; pay-as-you-go | £4.99 a trip, £59.99/year | **Pay per trip is a real model** |
| **Kayak** "Ask AI" (Apr 2026), **Skyscanner** inside ChatGPT (Feb 2026, UK first) | Chat search for flights and hotels | Free | Searching is free everywhere. ODYS links out (D120): right |
| **TfL Go** (May 2026) | Shows when you hit the fare cap; live buses | Free | Link to it, don't rebuild it |
| **Tube signal** | About 60%+ of below-ground stations have 4G/5G; full network targeted by end of 2026 (via search) | — | Offline ratings still matter this year |

**Updates to round 1:**
- **YouGov:** 20% of UK travellers are comfortable using AI for planning (Oct 2025, up from 15%). This replaces the Feb 2025 figure.
- **UK use of AI for travel** differs a lot by the question asked:
  - 20% are comfortable using it (YouGov);
  - 31% use it to plan (Dentsu, May 2026, via search);
  - 52% use it (MMGY, Jun 2026).
- **Older UK specialist travellers** (AITO, Mar 2026, 93% aged 50+): 60% are unlikely to use AI, and 80%+ would pay more for a better holiday.

## 5. Newer ideas worth adding

New ideas follow D75 and wait for Checkpoint 3, unless they help Test B or C.

| # | Idea | Who does it | Why people would pay or come back | Needs | Hours (GUESS) | Suggested |
|---|---|---|---|---|---|---|
| a | **"Re-plan the rest of today"** in one tap (rain, closed, tired), from where you are, from now | Almost no one ships it (see above) | It's the gap the free tools leave. 65% want a person, not AI, for a weather rebooking (Greetwell), so ODYS keeps it simple and asks | The planner as it is, location on the phone; the Met Office forecast later | 3 | **Before strangers** if Abram agrees (it helps Test C: the day works on the day) |
| b | **The evening before:** one quiet note at about 19:00 ("Tomorrow: first stop 10:30, leave by 10:05, book Horizon 22") | ChatGPT Pulse (Pro, $200/month) | Builds anticipation (Nawijn) and a habit; carries on from "Preview tomorrow" | A local notification; no server | 2 | After Test B (#64) |
| c | **"Checked on 8 Oct"** on each stop, from the card's `last_checked` | Travierge's "evidence cards" idea (UNVERIFIED) | Makes the checked-places advantage visible when people distrust AI plans | Nothing new | 0.5 | **Before strangers** if Abram agrees |
| d | **Start from a saved reel or link:** match it to a checked moment, then fit it into a day | Rhyme, Travio, Mindtrip | A first plan from what people already saved | AI on the person's link: a consent change | 6 | After Test B (#65) |
| e | **Book a table for the lunch slot** (links to OpenTable or TheFork) | Google AI Mode (UK) | Matches the free tool; ODYS holds no money | Partner links | 2 | After Test B (#66) |
| f | **"Plan 1 or Plan 2?" for friends by a shared link,** no account | TripsTogether, SyncUp (UNVERIFIED) | Group decisions; reuses the pair | Link sharing | 4 | After Test B (with #45) |
| g | **Pay per trip** beside a yearly price | Flighty £4.99 | Fits people who travel a few times a year; no cancelling after the trip | Nothing to build now | 0 | Test D wording (Checkpoint 3) |
| h | **Visitor essentials** in "Good to know": phone data (roaming or an eSIM), health cover, the fare cap | GOV.UK, NHS, TfL | Visitors' practical needs | Facts checked first | 1 | Before strangers (wording checked from GOV.UK, NHS and TfL first) |

## 6. Decisions for Abram

1. **The paid server** (roadmap decision 2): the first open waited **42.8 s** again today. $7 a month. **Recommendation: yes, before friends** (16 Oct).
2. **Deleting and reinstalling the app:** iOS normally keeps the app's code in the Keychain, so a reinstall skips Welcome and consent and carries on with the old answers (check on your iPhone, 2 min). **Recommendation:** on the first open after a reinstall, delete the old data on the server and start afresh, and say so in the privacy notice. That is less data kept, and consent is asked again. 0.5 h.
3. **"Re-plan the rest of today"** (idea a, ~3 h) **before strangers**? **Recommendation: yes.** It's the clearest thing people would pay for, and it helps Test C.
4. **"Checked on [date]" on each stop** (idea c, 0.5 h) before strangers? **Recommendation: yes.**
5. **Test D prices:** add a per-trip option (Flighty sells one at £4.99) beside a yearly price. UK paid travel apps charge £24.99–£59.99 a year. Only 17% would pay up to 5% of a trip's value for an AI assistant (Amadeus). **Recommendation:** note it for Test D's wording at Checkpoint 3. Nothing to build.
