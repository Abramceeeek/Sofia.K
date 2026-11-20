# Quality, performance and accessibility (independent review, 11 Nov 2026)

**Decision.** The Brain is well tested (486 automated tests on this branch after merging the dev branch's latest sprint, all passing) and does what its documents say. The two apps are built but **barely tested by machine**: the iPhone app has no automated tests at all, and Android's are drawings of each screen with sample data. So for the apps this audit can say what the code does, not that it works on a phone. For "thousands of travellers" three things would break first, and none is the code's logic: **a server with a tenth of a processor that sleeps**, **a database that expires on 6 Dec**, and **flight and stay search capped at 200 a day for everyone**. And the product is **English-only and London-only by construction**: neither app has a single translatable string.

**How this was checked, and what wasn't.** The Brain was run locally and timed (a real server process, this machine's 4 processors, a throwaway database). Both apps were read, not run: there is no Mac or Android SDK here, and starting a macOS build costs money, which is Abram's call. No phone was used, so nothing below about battery, VoiceOver or TalkBack is a measurement. Where a status rests on code reading alone it says "built".

## What works: the function table

Statuses: **Tested** (automated tests pass, or run here), **Built** (code present and read; not run in this audit), **Sample data** (works on made-up or test-mode data only), **Partly**, **Not built**.

| Function | iPhone | Android | Brain | Overall |
|---|---|---|---|---|
| **Onboarding** | | | | |
| A resident's first run (6 places, 5 choices, a best hour) | Built | Built; screens drawn in CI | Tested | Built; never run by an outsider yet |
| A visitor from abroad (kinds of places) | Built | Built | Tested (4 tests) | Built |
| "Not sure", "haven't been", skipped questions | Built | Built | Tested | Built |
| Going back and answering again | Built | Built | Tested (one answer per item, m176; now also inside one request) | Built |
| "So far, I've learned…" and "Change something" | Built | Built | Tested | Built |
| Starting again after deleting data or reinstalling | Built (the Keychain token is cleared on a fresh install) | Built (reinstalling loses the token: the old answers stay on the server until 31 March, as the notice says) | Tested | Built; the two phones differ, and the notice says how |
| Returning person; changing preferences later | Built ("Improve future plans") | Built | Tested | Built |
| **A day** | | | | |
| Plan a day; a late or evening start | Built | Built | Tested | Tested in the Brain |
| The person's own time: one block, two blocks, over lunch | Built | Built | Tested (`test_personal_time.py`) | Tested in the Brain |
| A relaxed day; a day that's theirs | Built | Built | Tested | Tested in the Brain |
| Rain | Built | Built | Tested: dry-weather cards are left out, a rain swap is named, the forecast is used when the key is set | Tested in the Brain; live forecast only on production |
| A place that is closed that day or hour | — | — | Tested (never planned outside its hours or days) | Tested. **A place that closes unexpectedly is not known**: cards carry a "checked" date, not live status |
| "I'm tired": re-plan the rest of today | Built | Built | Tested | Built |
| Add a place; swap a stop; another plan | Built | Built | Tested (swap, regenerate, must-do) | Tested in the Brain |
| **Trips** | | | | |
| Arrive by plane, train or car; the last day | Built | Built | Tested (`test_trips.py`) | Tested in the Brain, for London only |
| "How long should I stay?" | Built | Built | Tested | Tested |
| Several days at once | Built | Built | Tested; 13 s for seven days (below) | Tested |
| Changing dates, a different stay, a different flight | Built (the trip lives on the phone and is re-planned) | Built | The Brain keeps no trip: each change is a new request | Built; not tested end to end |
| Flight search | Built | Built | Tested on sample data | **Sample or test data only.** Production runs Duffel's test mode (`/v1/health`, 11 Nov): not real flights |
| Stay search | Built | Built | Tested on sample data | **Sandbox only** on production: not real prices |
| A stay judged against the trip; other dates | Built | Built | Tested; other dates are **sample prices** until LiteAPI confirms its terms | Partly |
| Prices in other currencies, never ranked across currencies without a rate | Built (m231) | Built | Tested (11 tests); the live rate feed is off | Tested; estimates off |
| Taxes, fees paid at the property, cancellation terms, a missing price | Built | Built | Tested (7 tests on fees, 1 on cancellation) | Tested on sample data |
| Several cities in one trip | Not built | Not built | A prototype, not connected (m237) | **Not built** |
| **Out and about** | | | | |
| "Now", arriving, rating a stop | Built | Built | Tested | Built |
| The offline view of today | Built (m228) | Built; 1 unit test | Tested (2 tests) | Built; **never tried with a phone in flight mode in this audit** |
| A rating made with no signal, sent later | Built (kept on the phone) | Built | The Brain replaces a repeat rather than doubling it | Built |
| An app restart or upgrade mid-day | Built (the plan and progress are saved) | Built | n/a | Built; an upgrade that changes a saved shape is untested |
| **Other** | | | | |
| Share a moment | Built | Built | Tested | Built |
| Help & safety, and the reply | Built | Built | Tested | Built; depends on a person answering |
| Delete my data | Built; two small leftovers on the phone (SEC-15) | Built | Tested: every row goes | Tested in the Brain |
| Location while out | Built, on the phone only | Built | The start point is no longer kept (SEC-06) | Built |
| Booking anything | By design, no | By design, no | By design, no | Links out |

**The gap this table shows:** the right-hand column says "Built" far more often than "Tested". Every journey a person takes passes through an app that no machine exercises. Before strangers, the cheapest protection is one scripted run on each phone (the project's `REHEARSAL` code already exists for this) and a handful of Android tests that tap through a journey rather than draw a screen (~6 h). The iPhone needs a test target at all (~4 h to add one with the first tests, and a paid build to run it).

## Performance, measured

A real server process on this machine (4 processors, the 49 real cards, a local database), the planner's limit at production's 1.0 s. Script and raw output are described in the main report's appendix.

| | Result |
|---|---|
| Start to first answer | 1.4 s |
| Memory after starting | 106 MB |
| Memory after the load below | 213 MB (production's limit is 512 MB) |
| Saving six swipes (refits the person's model) | 48 ms median |
| "How long should I stay?" | 53 ms |
| Flight search (sample data) | 45 ms |
| **One day's plan** | **4.7 s**, every time (12 runs: 4.67 to 4.70 s) |
| A day's plan with a tight budget | 4.7 s |
| **Seven days of a trip in one request** | **13.4 s** |
| 4 people asking for a plan at once | 3.5 s each |
| 8 at once | 4.5 s each |
| 16 at once | 7.8 s for the slowest |

What these say:

1. **A plan takes 4.7 s, not "about a second".** The limit is 1 s per solve, and one plan runs several solves (a first plan, the variety check, and re-plans). The comments in `ops.py` and `render.yaml` that say "~1 s" are out of date. People see a "reveal" screen for that time, so it is acceptable; it is also the number capacity should be worked out from.
2. **The planner's time is a limit it chooses, so a slower server gives worse plans, not slower ones.** Production runs on Render's free plan: a tenth of a processor (`render.yaml`: "plan: free"; the size is Render's published one, not re-read here: UNVERIFIED). The project's own benchmark found the search already stops short at 1 s on a fast machine for some days (m206, finding 3). On a tenth of the speed, it stops shorter. **This is the quality risk nobody will see in a test: plans that are feasible and worse.** A paid instance with a whole processor is the fix (Abram: money).
3. **It sleeps.** After 15 idle minutes the free server stops, and the next person waits about a minute (the apps are built to wait). Fine for a test; not for a product.
4. **Capacity is not the blocker at thousands of people.** At 4.7 s a plan, one processor makes about 12 plans a minute. A thousand people planning twice a day is about 1.4 a minute on average. One paid instance carries that; a busy Saturday morning needs a second, and then the limits and caches that live in one process's memory must move somewhere shared (SEC-11).
5. **Flight and stay search stops at 200 searches a day in total** (`trips.py:913`), to cap cost. A thousand people would meet "unavailable" by mid-morning.
6. **Nothing was measured on a phone:** startup time, memory and battery need a device. From the code: location updates every 20 m while "Now" is open (`Location.swift:27`), no background location, no timers found running when the app is idle, and every tap that logs an event makes a small request.

## Time zones and dates

- Every date and time in both apps is formatted in London time on purpose (`Europe/London` 11 times in the iPhone app; `en_GB_POSIX`). Right for a London day; **wrong the moment a trip is elsewhere or a visitor's phone is on another zone and they read "today".**
- The Brain plans in clock times without a zone for a day, and uses London for "today", sunset and TfL. A zone-aware itinerary module exists and is not connected (m210).
- **The days the clocks change are untested**: no test mentions them. A day plan between 10:00 and 18:00 is unaffected in the UK (the change is at 01:00). A trip spanning the last Sunday of March or October, and the "next Saturday" used for Test B, deserve one test each (~1 h).
- Trip dates are validated against "today" in UTC in two routes and London time in a third (`api.py`: flights, stays and the stay comparison use UTC; trip days use London). Between midnight and 01:00 in summer they disagree by a day. Harmless today; make them one (~0.5 h).

## Accessibility (from the code; no screen reader was used)

| | iPhone | Android |
|---|---|---|
| Text that grows with the person's setting | Yes: 63 fonts sized relative to a text style; 5 fixed sizes to check | Text in sp throughout; **32 fixed heights** that may clip text at 200% |
| Large-text screenshots in CI | 2 screens of about 80 | Not found |
| Labels for controls without words | 37 labels, 17 decorative images hidden, 38 values, hints or traits | 32 descriptions, 3 marked decorative, 52 semantics blocks, 6 headings |
| Reduce Motion | Respected (69 checks) | Respected (15 checks) |
| Contrast | 4.5:1 is the stated rule | Enforced by a test that fails the build (`ThemeTest.kt`) |
| Touch targets | 44 pt is the stated rule | 48 dp is the stated rule |
| A real VoiceOver or TalkBack pass | **Not recorded anywhere in the repository.** It has been on Abram's list since October as "15 minutes, before strangers" | The same |
| Maps | Apple's map; the stops are also in a list | Tiles with no text alternative found beyond the list |

Counts are not quality. The honest state: the foundations are right on both phones, the iPhone's contrast rule has no test behind it (the iPhone app has no tests), and **nobody has listened to the app yet**. That 15-minute pass is the most valuable accessibility work left, and only Abram's phones can do it. For limited mobility: the app is one-handed and has no gesture without a button that I found, with one exception to check, the swipe cards, which need buttons as well as swipes (both phones have them: "Loved it", "It was fine" and the rest are buttons).

## Languages and regions

| | State today |
|---|---|
| Translatable strings | **None.** iPhone: no string catalogue; at least 218 sentences written straight into the code. Android: `strings.xml` isn't used; at least 184 |
| Sentences made on the server | The Brain composes English: how to get there, why this stop, the day's headline (`dayplan.py`, `explain.py`, `reasons.py`). The cards themselves are English prose |
| Right-to-left layouts | The layouts are ready (leading and trailing edges on iPhone; `supportsRtl` and start/end on Android). The words aren't |
| Numbers and dates | Fixed to British formats on purpose (`en_GB` 8 times, `Locale.UK` 12 times) |
| Currency | Prices keep their own currency (m213, m231, m238); "£" is still typed into the code about 20 times in each app |
| Units | Kilometres and minutes only |

**What Russian or Uzbek would take:** moving the apps' strings into catalogues (~12 h a phone, mechanical); making the Brain's sentences templates with a language per request (~25 h, and the hard part: grammar that changes with number and case in Russian); translating about 400 strings and every card, and having a native speaker review them (not Claude's to sign off); and re-taking every screenshot. **About 60 hours before the first translated word is trustworthy**, for a product that has not yet shown it works in English. I would not start. Arabic or another right-to-left language adds testing, not much code.

## What would break at a commercial launch, in order

1. The database expires (6 Dec 2026). **Everything stops.**
2. The free server: a minute's wait after any quiet spell, and plans made with a tenth of the search.
3. Search capped at 200 a day; and it shows test-mode flights and sandbox stays, which a paying customer would take for real ones despite the label.
4. No way to hand the Android app to the public: it targets a version Google Play no longer accepts for new apps (SEC-13) and is a debug build (SEC-12).
5. The iPhone app's privacy manifest (SEC-14).
6. One person answers Help & safety, and not overnight. That is honest and stated, and it does not scale past a few hundred people.
7. 49 cards. A weekly user runs out.

## What to do

| When | What | Hours |
|---|---|---|
| Before strangers | The `REHEARSAL` run on both real phones, including flight mode and a restart mid-day; the VoiceOver and TalkBack pass | 2 (Abram) |
| Before strangers | Correct the "~1 s" comments; one clock for "today" | 1 |
| After the round | A journey test on Android; a test target on iPhone; tests for the clock-change days | 12 |
| Before a public release | A paid server and database; shared limits; live search or none | Abram's money; ~8 h |
| Not now | Translation | ~60 |
