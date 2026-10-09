# ODYS roadmap: from the test build to a real product

*Written 6 Oct 2026, after D121 and Build 2. It answers three questions from Abram (6 Oct): how fast the app can use real data from Skyscanner, Booking.com, Airbnb and others; whether to start "finishing the product for massive use"; and what every step to a finished product is. Facts come from `research/sources.csv`, with the date read; anything not checked is marked UNVERIFIED, and every estimate not measured is a GUESS. Claude's hours aren't measured (m169), so they are GUESSES too.*

## The decision first

**Recommendation: make the app real for testers now, and build for "massive use" only after Checkpoint 3 (week of 23 Nov).**

- **Stage 1, "real for testers" (now to ~27 Oct, before strangers):**
  - real flights and hotels in the app;
  - real travel times (TfL) and real weather (Met Office);
  - a server that never sleeps or loses data;
  - logs and alerts.
  - **Cost: Claude ~25 h, Abram ~4 h, about $13 a month plus small search fees.** This is what makes testers see "the real thing that works".
- **Stage 2, the tests (friends 16–25 Oct, strangers from ~27 Oct, Test B reports ~13 Nov).** No new features, only fixes from what testers say.
- **Stage 3, public release (GUESS: Dec–Jan, only if Checkpoint 3 says go):**
  - the company, insurance, ICO, and a company Apple account;
  - accounts, migrations, a faster planner, more cards, and the App Store listing.
  - **Claude ~70 h GUESS; Abram ~15 h over several weeks.**
- **Stage 4, growth (2027):** more cities, earning money, businesses (Test E), group trips.

**Why not "massive use" now:** nothing yet shows that the personal plan beats the generic one (Test B) or that strangers come back (Test C). Building for thousands of users first risks scaling the wrong product. The money gates also still stand: the Apple check, then the company before the first paid client. Stage 1 gives testers the real experience without that risk.

---

## 1. Connecting real sources: how fast, source by source

**Short answer:** real flights and real hotels inside the app in about **1–2 weeks**, once Abram opens two accounts (~1.5 h of his time; Claude ~5 h to test the code against real answers).

Skyscanner, Booking.com and Airbnb **don't let a new app show their results**, at any speed. The app already opens each of them on the exact search, with the city, dates and travellers filled in. That's how small travel apps work until they have large traffic.

| Source | What testers see today | The fastest real version | When, and what it takes | Source (read) |
|---|---|---|---|---|
| **Flights: Duffel** | Sample flights; with the test key, Duffel's test airline ("Duffel Airways", not real prices) | **Live Duffel: real airlines, times and prices in the app** | **~1 week.** Abram opens the account and does the identity checks (KYC; it asks for the business type, and what each type needs isn't stated); ~1 h. Then the live key goes into Render (never a chat). Claude ~3 h to check the code against live answers. Approval time: UNVERIFIED | duffel.com/docs (6 Oct); help.duffel.com (search results, 6 Oct) |
| **Hotels: LiteAPI** | Sample stays; with the sandbox key, test prices | **Production key: real hotels, photos and prices** | **Days.** Abram adds a card to the LiteAPI account (~30 min; "core endpoints free", some premium ones billed). Claude ~2 h | docs.liteapi.travel FAQ (6 Oct) |
| **Skyscanner** | **A link that opens Skyscanner with the same flight search** (works now) | Skyscanner's results in the app (its Travel API) | **Not available to us.** Needs a commercial agreement and an established business with more than 100k monthly visits. Its affiliate programme (commission only, still links) needs a website with at least 5,000 monthly unique visitors (secondary sources) | skyscannerpartnersupport (search results, 6 Oct); travelpayouts.com (search results, 6 Oct) |
| **Booking.com** | **A link that opens Booking.com with the city, dates and guests** (works now) | Booking.com's results in the app (Demand API) | **Not available now.** Needs Managed Affiliate Partner status and a signed contract. The plain affiliate programme (links that earn a share) is free to join, with a review of a few days, but it's commission: a money gate (#50) | developers.booking.com (search results, 6 Oct) |
| **Airbnb** | **A link that opens Airbnb with the city and dates** (works now) | None | **No route.** There is no public API. The public affiliate programme closed on 31 Mar 2021, and partnerships are invite-only | travelpayouts.com; track360.io (9 Jun 2026); both search results, 6 Oct |
| **Google Flights** | A link with the search filled in | None | It has no public flight API | — |
| **Copying their websites ("scraping")** | — | **Never** | Against their terms, breaks without warning, and puts the App Store listing at risk | — |

**What a tester will see after Stage 1:**
- a real flight (airline, times, price, bags);
- real hotels with photos and nightly prices;
- a tap that opens Skyscanner, Booking.com or Airbnb on the same search;
- day plans with real TfL journey times and the real forecast.

The app keeps its honest lines: "one price found, plus links", "found at 14:05, check on the site", and "ODYS earns nothing from these links".

**Costs (from the sources above):**
- **Duffel** charges $0.005 per "excess" search; how many searches are free per order is UNVERIFIED. Since ODYS never books, every search may count as excess: about **$5 per 1,000 searches**.
- **The Brain already limits searches** per person per hour.
- **The second-biggest unknown:** whether Duffel and LiteAPI accept search-only use with no bookings. UNVERIFIED: **ask both in writing when signing up.**

---

## 2. The outside code review: what's right and what isn't

I checked each point against the code on 6 Oct.

| What the review said | Verdict | What we do |
|---|---|---|
| Travel times are guesses | **Right.** They are estimates from straight-line distance (`brain/src/brain/travel.py`) | **Stage 1:** TfL Journey Planner, cached. **~8 h, not the review's 2 h** (stop matching, caching, fallbacks, tests). Free key, 500 requests a minute |
| The app sends no weather | **Right** | **Stage 1:** Met Office DataHub free plan, 360 calls a day, cached by hour and area (~4 h). Open-Meteo's free plan is non-commercial only |
| No logging or monitoring | **Right** (only the safety alerts log) | **Stage 1:** request logs without personal data, an uptime check, an alert on errors (~3 h) |
| No database migrations (`create_all`) | **Right, not urgent** | **Stage 3**, before accounts: Alembic (~3 h) |
| Rate limits only on trip searches | **Right** | **Stage 1:** limits on installs, plans and feedback too (~2 h) |
| Moment cards aren't validated | **Wrong.** Every card is checked against the schema when it loads | — |
| Aspiration and CLIP not built | **Half wrong.** Aspiration match is built (`brain/data/aspiration.yaml`). CLIP was dropped on purpose (D16) | — |
| The float tolerance is a bug | **Wrong.** It's a correct line-search check | — |
| The test count | **Out of date:** 150 tests pass | — |
| Test B is mostly a separate script | **By design.** The script made the hand-run plans; the in-app pair (Build 2) uses the same engine | — |
| "Not production-ready" | **Agreed for a public release.** Ready for testers once Stage 1 is done | Stages 1 and 3 |

**One thing the review missed, measured here (6 Oct, 4 CPUs, all 49 ready cards):**
- **Timings:** a one-day plan takes **~1.7 s** and a 4-day trip **~6.5 s**. The planner searches for up to 1 s per day.
- **On Render:** the paid instance has less CPU (0.5), so GUESS 2–4 times slower.
- **Fine for tests, but this is the first thing to break under heavy use.** It goes in Stage 3.

---

## 3. What's done (6 Oct)

| Area | Done |
|---|---|
| **Research** | 19 areas; 503 sources, each with a date; 125 decisions in the log. The legal gates mapped, with the money gates in order |
| **Moments** | **51 cards, 49 ready** (5 of them shopping); openly licensed photos with credits; plan variety (D113) |
| **The Brain** (live at moments-brain.onrender.com) | Personal scoring `S = x·(b + δ)`; the OR-Tools day planner. Onboarding: 6 places and 5 "this or that" choices, then "Improve future plans". Ratings refit the weights. "Worth about £V". Share card and referral funnel. Help & safety replies by a person. Visitors as their own cohort. **Trips:** flights and stays with filters and links out, multi-day London plans. **Test B in the app:** Plan 1 / Plan 2, the survey, tester codes. 150 tests |
| **The app (ODYS)** | SwiftUI, built and uploaded by GitHub Actions with no Mac. Onboarding with Abram's video, "So far", the plan reveal, "Now" for the day, one-tap ratings, sharing, Help & safety. **Trip, Book and You tabs** (D121). TestFlight build 36, plus the build now in CI |
| **Legal** | Cleared: the right to run a business, and the government job and its contract (D94, D96) |
| **Not done** | **No real user yet**: the app is on Abram's phone only. No paid server or database. No company. No real flight or hotel data. The Apple check is still open |

---

## 4. The stages, step by step

### Stage 1: real for testers (now to ~27 Oct)

| # | Step | Claude | Abram | Money | Why |
|---|---|---|---|---|---|
| 1 | Live flights (Duffel) and hotels (LiteAPI production) | ~5 h | ~1.5 h (accounts, identity checks, a card, keys into Render) | ~$5 per 1,000 flight searches (UNVERIFIED allowance); hotel searches free | Testers see real results (section 1) |
| 2 | **A paid server and database**, before the free database expires ~27 Oct (re-checked 9 Oct: free databases expire 30 days after creation, then are deleted after a 14-day grace; upgrading in place keeps the data) | ~0.5 h (check it after the upgrade) | ~15 min (change both instance types in Render) | **$7 + $6 a month, plus storage at $0.30/GB** (9 Oct). Hetzner Cloud (from €5.99, Abram's screenshot) compared 9 Oct: cheaper, but Abram would run the server, the database, backups and security updates himself, so Claude recommends staying on Render (Abram decides) | The free server sleeps after 15 minutes (a minute's wait); the free database expires and its data goes |
| 3 | Real travel times from TfL, cached | ~8 h | ~15 min (a free key) | £0 | Plans that hold up on the day |
| 4 | Real weather from the Met Office, cached | ~4 h | ~15 min (a free key) | £0 (free plan) | Rain and cold already change the plan (D95); now from the forecast |
| 5 | Logs without personal data, an uptime check, error alerts, a nightly backup export | ~3 h | ~15 min (an alert email) | £0 GUESS (free tiers) | We find out about a failure before a tester does |
| 6 | Rate limits on every endpoint | ~2 h | — | — | One person or a bot can't run up the provider bills |
| 7 | **External TestFlight:** test information, beta App Review | ~1 h | ~1 h | — | Friends and strangers can install it |
| 8 | **The gates before strangers** (CLAUDE.md): the Apple check; the helper signs Part A; `BRAIN_ALERT_WEBHOOK_URL` set; re-check the ICO fee | ~0.5 h | ~2 h | ICO £52 if required | Safety and legal |
| | **Total** | **~25 h** | **~4 h + gates** | **~$13 a month + search fees** | |

### Stage 2: the tests (16 Oct to ~13 Nov)

- **Friends 16–25 Oct; strangers from ~27 Oct** (external TestFlight, Post 1 in 4–6 groups).
- **Test B report ~13 Nov; Checkpoint 3 in the week of 23 Nov:** go, change course, or stop.
- **Building is frozen** apart from fixes from testers (D75: new ideas go to `after-9-nov.md`).
- **Abram's hours:** about 1.5–3 h a week (`LOG.md` weekly plan). **Claude:** fixes as they come, and the Test B analysis (~6 h).

### Stage 3: public release, if Checkpoint 3 says go (GUESS: Dec–Jan)

**Legal and money (Abram, in this order):**

| Step | Cost | Time | Source |
|---|---|---|---|
| Company at Companies House | £100 | Usually within 24 h | gov.uk (26 Sep) |
| D-U-N-S number, then the Apple company account (start ~3 weeks before release, D61) | £0 for D-U-N-S; $99 a year for Apple | Up to 5 business days, then up to 2 for Apple | developer.apple.com (26 Sep) |
| ICO data protection fee | £52 (tier 1) | Online | sources.csv |
| Public liability and professional indemnity insurance | UNVERIFIED: get quotes | — | — |
| UK trade mark for ODYS: search the register (free), then apply | **£205 online for one class, £60 per extra class** (from 1 Apr 2026; secondary sources) | Months to register: UNVERIFIED | hindles.co.uk, reddie.co.uk (search results, 6 Oct) |
| Solicitor: Part B (equity), and the April 2027 package-travel question before any commission (#14, #50) | UNVERIFIED: get quotes | — | — |

**Product (Claude, GUESS ~70 h in total):**

| Step | Claude | Why |
|---|---|---|
| Sign in with Apple, plus in-app account deletion (#32) | ~4 h | Answers survive a new phone; Apple requires deletion once accounts exist |
| Database migrations (Alembic) | ~3 h | Change the database without losing data |
| **A faster planner:** stop the search when the plan stops improving, plan trip days side by side, then more workers | ~6 h | The 1.7 s and 6.5 s measured above |
| A load test: plans for 100 people at once, and a server size that fits | ~3 h | Know the limit before the launch, not on the day |
| Security pass: admin endpoints, secrets, dependency audit, abuse limits | ~4 h | Public apps get probed |
| **More London cards: 49 → ~100 ready** | ~25 h (~0.5 h each, verified, with photos) | Variety for people who use it every week |
| Server push for "your next trip day is ready" (#52) | ~8 h | Today reminders are on the phone only |
| Offline and error states, an accessibility pass (VoiceOver, text size) | ~8 h | App Review and real-world use |
| App Store listing: screenshots, privacy labels, review notes | ~4 h (+ Abram ~2 h) | Required to publish |
| Commission links, only after the money gates and the solicitor (#50) | ~2 h | The first revenue line |
| **Total** | **~70 h GUESS** | |

**Running costs at launch (Render, sources.csv 26 Sep):**
- $7 + $6 a month while small;
- $25 (2 GB) + $19 (1 GB database) a month if the load test needs it;
- Duffel's search fees grow with use (section 1).

### Stage 4: growth (2027, if the numbers say so)

- **More places, in Abram's order (#49):** one UK city, then Europe. GUESS: Claude ~6–10 h of cards per city, plus ~1 h of Abram's review. Flights and hotels already work for any city.
- **Earning money:**
  - commission links (#50);
  - real price comparison once traffic qualifies for partner APIs (#51);
  - businesses (Test E, **still the main untested revenue risk**, D86).
- **Group trips with strangers** (the founder's original idea):
  - Stripe Connect direct charges only (never hold trip money);
  - trust and safety under the Online Safety Act;
  - the package-travel rules from April 2027 (#14). **A solicitor first.**
- **A smarter model:** adaptive onboarding (#29), and "people like you" from the ratings.

---

## 5. What "finished, for real use" means

A checklist for the public release. Each line names the stage that covers it.

1. **Real data:** flights, hotels, travel times, weather, and every card fact sourced. *Stage 1 (cards: ongoing)*
2. **Always on:** a paid server, monitoring, backups, and a restore that has been tested. *Stages 1 and 3*
3. **Safe:** every safety message goes to a person, with a reply within a few hours (Abram, plus a named helper); a way to report; an Online Safety Act risk assessment if users ever see each other's content. *Stage 1, then before group trips*
4. **Legal:** company, ICO, insurance, privacy notice, company Apple account, trade mark. *Stage 3*
5. **Accounts, with deletion.** *Stage 3*
6. **Holds up under load:** a load test passed, a faster planner. *Stage 3*
7. **Earns money:** at least one tested revenue line. *Untested today: Stage 4 and Test E*

---

## 6. Risks

| Risk | What we do |
|---|---|
| Test B fails: the personal plan doesn't beat the generic one | That's what Checkpoint 3 is for. Stage 3 changes or doesn't happen; little is lost, because Stage 1 is small |
| Duffel or LiteAPI won't allow search-only use, or the identity checks need a company | Ask in writing at sign-up (UNVERIFIED today). Fallback: keep the samples and links for that source, and say so in the app |
| The prices shown differ from the provider's site | The app shows when the price was found, and says to check on the site; it never books |
| The free database expires ~27 Oct and its data is lost | Stage 1 step 2, before strangers |
| Founder hours (7.5 a week, alongside work and exams) | Stage 1 asks ~4 h; Stage 3's legal steps ~15 h, spread over several weeks |
| The Apple outside-activities check is still open | It blocks external TestFlight and any money; Abram is checking it |
| "Businesses will pay" is untested | Test E after Test B (D86) |

---

## 7. Decisions needed from Abram

1. **Go for Stage 1 now?** (Recommended: it's what makes testers see the real thing.)
2. **Money:**
   - $13 a month on Render, from about 20 Oct;
   - a card on LiteAPI;
   - Duffel's search fees (about $5 per 1,000 searches, GUESS).
3. **Duffel identity checks:** as an individual now (faster), or wait for the company in Stage 3? (Recommended: individual now, if Duffel allows search-only use; move to the company later.)
4. **Weather:** the Met Office free plan (360 calls a day)? Open-Meteo's free plan is non-commercial only.
5. **Confirm: no building for scale until Checkpoint 3** (week of 23 Nov).
