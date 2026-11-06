# ODYS product direction (agreed 6 Nov 2026, m196)

**Decision.** ODYS becomes a personal travel and entertainment platform for any trip: where to go, how long to stay, what to do each day, where to eat and sleep, how to get there, and when to book. The person decides; ODYS shows the options, explains its suggestions and keeps their own time free. **Trips become the main product; the day planner ("moments") is the engine inside every trip day.** Abram's brief and the outside review are summarised here; this page is what new screens and code are checked against.

| Decision (Abram, 6 Nov) | Position |
|---|---|
| Friends' round (Test B) | Run it now, on a **frozen** build |
| New work | On the branch, beside the test; nothing reaches the testers until the round ends |
| First feature | "How long should I stay?" |
| Second | Free time as a real choice |
| Third | Hotel prices across nearby dates, and watching a saved stay |
| Food preferences, halal included | Yes, after the consent and data-source work below |
| Price forecasting | No: observations only |
| Several cities in one trip | Later |
| Architecture | Works for any place from the start |
| Coverage | Added city by city, only where the data is checked |

## Principles (every screen and ranking is checked against these)

1. **The quality of the experience, not the number of stops, bookings or attractions.**
2. **Explain every suggestion.** Five days rather than three, this hotel rather than that one: say why, in the person's terms.
3. **Show the alternatives.** A suggestion never hides the other options.
4. **Protect personal time.** Rest, meeting someone, shopping or wandering are choices, not gaps to fill.
5. **The whole cost and the whole day.** The cheapest flight or the nearest hotel isn't always the best for this trip.
6. **Say what we don't know.** No invented facts: unverified halal status, prices or opening hours are labelled as such. No price predictions.

**Every major recommendation is checked three ways (Abram, 6 Nov; m199).** Automated tests answer only part of the first.
1. **Is it logically reasonable?** Run it on realistic simulated people and look at the spread of results, not one output. Read what a person would see.
2. **Do people prefer it?** Tested with real users against an alternative, as Test B does for day plans.
3. **Does it lead to a better real experience?** Measured afterwards: the ratings, "worth what you spent", "would you do it again".

Trip length is at step 1. The 75% "strong match" line and the suggested lengths still need steps 2 and 3.

## A. What works today (code on `main`, 6 Nov)

- **A day out in London:** a short onboarding (where you're based, a great moment, feelings, 6 places, 5 this-or-that choices) builds a personal plan from **49 checked London moment cards**. Each card has the way in, best time, what to notice, cost and why it was picked. Swap a stop, plan again, map view, free time shown in the plan.
- **On the day:** "Now" (the way in, "I'm here", what to notice), rating each stop in words, share card, "Re-plan the rest of today" (rain, closed or busy, tired), skip a stop, location only when in use and only on the phone.
- **Trips (London):** dates, where you're coming from, the hours of your day, places a day, how the trip should feel. Day 1 starts where you arrive (plane, train or car), with one place on the way if you travel light. The last day ends at the stay and on to the airport or station, with directions. Change a day; preview tomorrow.
- **Flights and stays inside a trip:** search, filters, details, then booking on the provider's own site, with no commission. Duffel (flights) and LiteAPI (stays) run on **test and sandbox keys**, so prices are labelled as samples until the live keys are added.
- **Visitors from abroad** get kinds-of-places onboarding, and are a separate cohort in Test B.
- **Around it:** TfL journey times, the Met Office forecast, Help & safety (999 first, a person replies), your data and deleting it, nightly sealed backups, both apps (iPhone and Android) at parity.
- **London-only parts to generalise later:** the cards (`brain/data/moments`), TfL times (`tfl.py`), the straight-line London estimate (`travel.py`), the Met Office forecast (`weather.py`), arrival times (`brain/data/arrivals.yaml`), and the trip destination list (`brain/data/airports.yaml`, London only).

## B. Direction (six parts; the first three are this winter's work)

1. **Trip length** ("How long should I stay?"): from the person's own good matches, places a day and the time between places. For each length, it shows what they gain or give up. Extra days are offered as choices: another place, a shopping day, a slower pace, or a free day.
2. **Days with personal time:** "I have plans at 16:00", "leave two hours free", "a relaxed day", alongside the stops.
3. **Stays, honestly priced:** the same stay's price across nearby dates; save a stay and see when its price changes (shown when the app opens, push later); the English school holidays marked, from official term dates, with the area named.
4. **Food:** halal, vegetarian, vegan, kosher, allergies and other needs, as an explicit opt-in used only for that person's own suggestions (see "Before food preferences").
5. **Several places in one trip** (later): route, nights in each, the travel between them, and where to stay.
6. **Discovery** (later): "I don't know where to go" (budget, days, weather, interests), then the duration and cost compared.

Not doing: price forecasts, a chat that writes itineraries, a social feed, handling visas (only links to official information and partners), selling trips or taking payments ourselves (flight-inclusive sales need ATOL or an exemption: a separate decision with its own legal review), or ranking that a partner can pay to change.

## C. Three ways in, and the screens

| Journey | Flow | Existing screens used | New screens |
|---|---|---|---|
| **A. "I don't know where to go"** | Explore → suggestions → compare length and cost → choose → plan | Home: before the day ("A trip") | Discover (later); compare places (later) |
| **B. "I know where I'm going"** | Place → dates → **suggested length** → days → flights and stays | New trip: where, when, from, your days, the feel; A trip; A trip day; Flights; Stays; A stay | **Trip length** (after dates); **extra days** choice; **personal time** in "your days"; **stay prices across dates**; **watched stays** |
| **C. "I'm already there"** | What's near → suggestions → food and things to do → re-plan the rest of today | Home: on the day; Now; Re-plan the rest of today; A stop's card | Food filter on suggestions (after the food work) |

## D. Build order and hours (Claude's are GUESSES; Abram's are review time)

| # | Work | Claude | Abram | Needs |
|---|---|---|---|---|
| 0 | Test B: add "which plan would be easier to actually do?"; list who chose the generic plan, with their reasons, in the report; then freeze `main` | ~2 h | 0.25 h | Before the round starts |
| 1 | Trip length | ~8 h | 0.5 h | Nothing new |
| 2 | Personal time in a day | ~5 h | 0.5 h | Nothing new |
| 3 | Stay prices across dates; watched stays; school holidays | ~10 h | 0.5 h + adding the live LiteAPI key in Render | Live prices (sandbox ones aren't real) |
| 4 | Food preferences | research ~2 h, consent and DPIA draft ~2 h, then build | decides the lawful basis and signs off the DPIA | See below |

**Before food preferences:** an Article 6 lawful basis and an Article 9 condition (explicit consent, done properly: specific, separate, easy to withdraw); a DPIA; a privacy-notice update. It is used only for the person's own restaurant suggestions: never for matching people, advertising or anything else. Halal is offered as a food choice, never as a question about religion. A source of checked halal data must exist before any venue is labelled: certified (with the certifier), halal menu, halal options, unknown, or not suitable, each with its source and the date it was checked. The ICO pages are to be read and cited in the research step (UNVERIFIED here).

## E. Coverage

"Works for any place" means the code makes no London-only assumptions (the list in A). It does not mean coverage. A place is offered only when its moments, travel times and opening hours are checked, and the app says plainly when something is unknown. Next places come after the friends' round, chosen with Abram. Each needs a source of place data: free (OpenStreetMap, Wikidata) or paid (a money decision).

## Technical debt and open questions (Abram, 6 Nov)

- **Card attributes:** the five shopping cards are listed by ID in `brain/src/brain/triplength.py`, because the cards have no category. Before the next city, every card gets structured attributes: category, experience type, duration, location, opening hours, price level, and the preference tags. Then no destination-specific lists spread through the Brain.
- **Trip length:** an estimate of experience coverage, not a recommended holiday length. The 75% "strong match" line is the model's, awaiting validation against real ratings. A later version checks feasibility: travel time, opening hours, durations, arriving and leaving, and pace.

## F. Testing during the build

- **`main` is the test build** while the friends' round runs: no commits to it at all, notes included (m198). The round's manifest is `validation/friends-round.md`. New work stays on `claude/vigilant-cannon-my82dj`. Its iPhone checks run as simulator screenshots only, never TestFlight uploads; Android runs as local tests, not the published APK.
- **What the round collects:** the gut choice, "this plan fits me" for each plan (how personal it felt), which would be easier to actually do (added in step 0), and why. Testers who chose the generic plan are listed with their reasons.
- **Formative, not proof:** friends are a first usability group; the 7-of-10 signal and the paired fit difference are read as direction, not as evidence for the wider market (D127).
- **Before it starts:** the Apple check for external TestFlight (D60, D94). The free database lasts until 6 Dec 2026 (m195): the round, or a move to a paid database, has to fit before then.
