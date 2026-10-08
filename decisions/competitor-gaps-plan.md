# Closing the gaps with other travel apps: the plan

*Written 8 Oct 2026, after the journey audit (`decisions/journey-audit.md`, sources in `research/sources.csv`, area `journey`). Abram asked for "a plan to add the differences found from the other apps". Hours are GUESSES of Claude's time unless stated; Abram's time is listed separately. New ideas follow D75: anything that doesn't help Test B waits for Checkpoint 3 (week of 23 Nov) on `decisions/after-9-nov.md`.*

## The decision first

**Copy what carries a trip; link out to what others already do better; never compete on breadth.**

1. **Done now (8 Oct, D123 and m176):**
   - location while out, on the phone only;
   - "Start from where I am" and "Must include" a place;
   - today's trip day, the next day, and the airport journeys on "Now";
   - opening hours and "Book ahead" on every stop;
   - entry rules and getting around London as general information;
   - NHS 111.
2. **Before strangers (~27 Oct), only if it helps Test B or C:**
   - live Tube status on the day;
   - the Met Office forecast in plans;
   - a paid server.

   About 8 h of Claude's time, plus about 30 min of Abram's for two free sign-ups, and $7 a month for the server.
3. **After Test B, if Checkpoint 3 says go:**
   - accounts with a shared trip link;
   - "one sentence in";
   - bookings by email;
   - a lock-screen "Now";
   - what's on tonight;
   - a trip recap;
   - flight and stay price alerts;
   - other languages.

   About 75 h GUESS, in the order below.
4. **Never build:**
   - turn-by-turn directions, transit routing or a review database: Apple Maps, Citymapper, TfL Go and Google do these, and ODYS links to them;
   - boarding passes and flight status: Apple Wallet already shows those.

**What stays ODYS's own:**
- checked moments, with their real hours, the way in, the light and booking needs;
- plans built from the person's feelings and ratings;
- a day carried through to the end.

The free planners get this wrong. In one test, 52% of ChatGPT's city plans put a stop outside its opening hours (SEO Travel, May 2024).

## The gaps, one by one

| # | What others have | Who (checked 7 Oct) | ODYS today | What ODYS adds | When | Hours (GUESS) | Gate |
|---|---|---|---|---|---|---|---|
| 1 | **Knows where you are** | Ask Maps, Citymapper | **Done (D123):** distance to the stop, "You're here", the rating asked after leaving, "Start from where I am" | Later: background arrival only if people ask (needs "Always" location; not planned) | Done | ~4 (done) | Privacy notice updated |
| 2 | **Live transit and disruption** | Citymapper, TfL Go, Ask Maps | A travel-time estimate; Directions open Apple Maps | Tube line status on the day of the plan ("Jubilee line part-closed: allow more time"), from TfL's open data | Before strangers (roadmap Stage 1) | ~4 | Abram: a free TfL API key (~10 min) |
| 3 | **Weather in the plan** | Gemini (live data) | A rain swap per outdoor stop, no forecast | The forecast for the plan's day; rain moves the rain swaps up | Before strangers (roadmap Stage 1 #4) | ~4 | Abram: a free Met Office DataHub account (~15 min) |
| 4 | **Starts from one sentence** | Gemini, Ask Maps, ChatGPT, Mindtrip ("Start Anywhere") | About 25 questions before the first plan | "Tell me what you fancy" on Plan a day, turned into the day's settings; the questions still run underneath | After Test B (#58) | ~6 | An AI step on the person's words: a consent change (`ai_processing` is off) |
| 5 | **Bookings in one place** | TripIt (free), Wanderlog Pro, Gemini (Gmail) | "Did you book it?" by hand | Forward a confirmation email or share a PDF; flights and stays fill in, and the days plan around them | After Test B (#57) | ~8 | Privacy: what's kept and for how long |
| 6 | **Plan with friends** | Wanderlog (live co-editing), Mindtrip (group chat), Airbnb (Travel Map) | One person, one phone | Step 1: a read-only link to a trip or day. Step 2: accounts (Sign in with Apple), then co-editing | After Test B (#45; accounts in roadmap Stage 3) | ~4 + ~12 | Accounts need a privacy update and data migration |
| 7 | **On the lock screen** | Citymapper and Flighty (Live Activities), Wallet | Local rating reminders | A Live Activity for "Now": next stop, leave-by time, one-tap "How was it?" | After Test B (new #61) | ~8 | A widget extension needs its own App ID and profile in GitHub Secrets (Abram ~30 min) |
| 8 | **What's on tonight** | Visit London app, Ask Maps (events) | Evening cards only | Concerts, theatre and sport for the trip's dates, chosen to fit the person | After Test B (#54) | ~7 | Abram: a free Ticketmaster key (~10 min) |
| 9 | **Tickets in the app** | Gemini (Viator), Mindtrip | "Book ahead" with the official site | Ticket prices and "Book" links for ticketed moments | After the company (#55) | ~8 | Affiliate commission: a money gate |
| 10 | **Price alerts** | TripIt Pro (fare drops), Google (flight tracking) | Prices found once | "Tell me if this flight or stay drops", checked once a day | After Test B (new #62) | ~10 | Push notifications and a server job; search fees when live |
| 11 | **Social proof** | Google, Tripadvisor reviews | The person's own predicted worth | "People who like what you like rated this 4.6", from ODYS's own ratings, once there are enough | After 50+ raters (new #63) | ~6 | Never shown below a minimum count (privacy) |
| 12 | **A memory of places** | Apple Maps Visited Places | Ratings stored, not shown back | "Your moments": the stops rated, with photos and the reason, and a trip recap | After Test B (#60) | ~4 | — |
| 13 | **Other languages** | Most big apps | English only | Key screens in other languages, checked by native speakers | After Test B (#59) | ~15 | Card text too, card by card |
| 14 | **Offline** | Wanderlog, Visit London (offline maps) | The day, trips and ratings work offline; maps and new plans need data | A tip to download London in Apple Maps (check the steps first: UNVERIFIED here) | Before strangers | ~0.5 | — |
| 15 | **Splitting costs** | Wanderlog, Splitwise | A total per person | "Who paid what" for group trips, settled outside the app | Stage 4 | ~6 | Never hold money (CLAUDE.md) |

## Order, and why

1. **2–3 (TfL status, weather):** they make the day work on the day, which is Test C's measure. They're also roadmap Stage 1, which already waits for Abram's go.
2. **12 (memory and recap), then 7 (lock screen):** both bring people back after a day, which is the retention Test C measures.
3. **6 (sharing, then accounts):** sharing is the growth path, since friends are the most trusted source for travellers (Phocuswright 2025, via search results).
4. **4 and 5 (one sentence in, bookings by email):** both close the "slower than free" gap, but each needs a privacy or consent decision first.
5. **8–11, 13 and 15:** once the core is proven.

## What Abram needs to do, and when

| When | What | Time |
|---|---|---|
| Now | Paid server in Render (roadmap decision 2): **Render dashboard → moments-brain → Settings → Instance type → Starter**. Tell Claude afterwards, so `render.yaml` matches | ~5 min, $7 a month |
| Before strangers | A free TfL API key and a Met Office DataHub account, put into Render's environment (never in a chat) | ~30 min |
| Checkpoint 3 | Choose which of 4–13 go ahead | ~30 min |
