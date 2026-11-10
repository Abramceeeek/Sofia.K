# Global Destination Intelligence sprint: report (10 Nov 2026; m234–m243)

Abram's six workstreams and four smaller items (m234), built on the branch `claude/vigilant-cannon-my82dj`. Everything new is in the Brain, except one line in both apps ("Emergency help in the UK"). **The apps use none of the new modules yet;** each item says what the apps would need, after the friends' round.

**The release rules held:**
- `main` is unchanged at `80a0da3`, and the live Brain still answers `"version":"80a0da3"` (checked 10 Nov).
- Nothing was deployed, and no TestFlight build or APK was published. The iPhone run was dispatched with `upload: false`, and upload only ever runs on `main` (`WANT_UPLOAD` in `ios.yml`).
- No paid API was called, and no API access was bought. LiteAPI live prices and the ECB rates stay off. Food preferences aren't collected, and no email was sent.
- No Test B question was added, and the friends' round is untouched.
- No places were imported in bulk: the catalogue holds only the 49 ready London cards.
- Home is unchanged.

**The ODYS quality standard** (relevance, practicality, money, trust) is now in `CLAUDE.md` and in code (`quality.py`). Discovery uses it; the planner doesn't yet.

## 1. Work completed

| # | Item | What was built | Verified by |
|---|---|---|---|
| m234 | **Abram's decisions, and the quality standard** | Logged: the `foods_avoided` rules (count, delete, and check a clean replacement backup first; never inspect the values), the eight kinds' caption condition, the export rules, the UK-only emergency rule. The standard is in `CLAUDE.md`. Export and per-country emergency numbers are on after-9-Nov (#95, #96) | A new test: the eight kinds' caption names the example photo's real city |
| m235 | **WS1: a structured experience catalogue** | **A common core plus one facet per kind** (culture, outdoor, food, shopping, activity, area, transport, beach). Global IDs `xp:<country>:<locality>:<slug>`. **Every fact says how sure it is:** checked, claimed, estimated or unknown. **All 49 ready cards convert.** Opening hours parse into a weekly table for 25; vague or seasonal wording stays as text. **No module but the frozen Test A/B settings lists card IDs.** Plans unchanged | 11 tests (one scans the code for card-ID lists) |
| m236 | **WS2: destination intelligence** | **A profile per destination:** geography, areas, travel between areas, experiences, seasons, holidays, stays and **emergency numbers**. **Providers fill the parts behind one interface;** the first provider with a part wins and is named. `readiness()` says what's missing or estimated. **London is ready** ("seasons missing; travel estimated; stays are samples"). **The synthetic Testville** (ISO test codes ZZ and XTS) is not ready without emergency numbers. **Emergency numbers for GB, FR, NL and BE** come from official pages. **The offline pack shows the trip's own country,** and an unchecked country says so | 5 tests; the Android offline tests (4) |
| m237 | **WS3: London → Paris → Amsterdam → Brussels** | **One itinerary** with nights per city, journeys and each city's currency. **Clock notes** ("Paris is 1 hour ahead of London"). **Night trains count as nights on board.** **A missed connection:** a later train today changes only the times; tomorrow means a bed tonight and a night lost at the next place. **Changing one city's nights** moves the rest, or the next city gives or takes nights. **Every change lists the bookings to change; nothing moves silently.** Sample journey times only. Paris, Amsterdam and Brussels are defined in the test, not in the app's list of places | 7 tests |
| m238 | **WS5: a display currency** | Flight and stay searches take `display_currency` (default GBP, so nothing changes today). **The provider's price and currency are never changed;** the estimate beside the price is in the display currency, through the ECB euro rate, with its date. No usable rate means no conversion and no ranking across currencies. **Rate and price providers compared** | 3 new tests (12 currency tests) |
| m239 | **WS4: discovery without a feed; the quality standard in code** | **At most three answers, each with its reasons:** destinations, neighbourhoods, hidden local moments, seasonal moments, food, and what fits a time and budget. **Anything poor on one of the four perspectives ranks after everything that isn't.** A destination that isn't ready is named, with what it lacks. Seasons come only from dated notes that name their moments | 9 tests |
| m240 | **WS6: group trips (prototype, no accounts)** | **Hard rules first:** one member's rejection is a veto; the cost fits the smallest budget (for the trip and day by day); each member's first must-see is in where the budget allows, and said where it isn't. **Then Nash welfare** on each member's chance of enjoying the plan. **Highlights take turns** by day. Members are "Member A", "Member B" and so on, never named | 4 tests; a synthetic benchmark of 200 groups |
| m241 | **Why a stay; why a trip length** | **Why a stay:** distance from the planned days, its whole cost, its terms, and a trade-off (the farthest day over 30 min away, or non-refundable). **Why a trip length:** what it covers, and what a shorter trip leaves out or a longer one adds, by name. At most three lines, no percentages | 3 new tests |
| m242 | **Learning food interest without asking about diet** | **A synthetic benchmark of 1,000 people.** Making one of the first four rated stops a food card learns most, with no extra question (food variance removed 7% → 16%). A direct question does least (9%). **Recommendation:** after the round, the first day's lunch uses a fitting food card (~2 h). Nothing asks what anyone eats | The benchmark (`food_interest.txt`) |
| m243 | **Photo attribution** | **A test fails the build if:**<br>• the two apps' photos or credits differ;<br>• a photo lacks a credit, or a credit lacks a photo;<br>• a credit lacks a title, author, licence or Commons page;<br>• a licence isn't CC0, public domain, CC BY or CC BY-SA, or its link doesn't match it;<br>• a credited card isn't ready;<br>• the apps stop showing the credit.<br>**All 45 pass.** Six source pages were re-read on Commons, and all six match | 4 tests |

**Benchmark results (synthetic people only, from the model's own prior):**
- **Groups** (m240): with one member's tastes three times as strong:
  - a plain average gives that member 85% of stops from their own top 20%, against 40% for the others;
  - **Nash gives 57% against 50%,** with the best chance that every member gets a favourite (77%);
  - least misery has the smallest gap, but 65% get a favourite.
- **Food interest** (m242), the share of the food weight's uncertainty removed:

| Option | Removed |
|---|---|
| Today | 0.069 |
| A food question | 0.088 |
| A ninth kind, "A meal worth travelling for" | 0.113 |
| A food this-or-that day | 0.148 |
| 4 rated stops | 0.075 |
| **4 rated stops, one a food card** | **0.162** |

## 2. Found, blocked, or not done

**Found in London's own data:**
- **Hours:** only 25 of 49 cards have hours a machine can read. The rest are seasonal, run "until dusk", or are vague.
- **Areas:** only 28 of 49 cards name an area, so only 3 areas have two or more moments. **Placing cards in their nearest area was tried and dropped:** it put St Paul's in "Borough", across the river.
- **Step-free access:** checked for only 4 of 49 cards.
- **Season notes:** none checked for London, so seasonal discovery is empty there by design.
- **Popularity** comes from simulated plans (D113). "Hidden" means rarely planned for others by the model, and the wording says so.

**Old builds:** build 91 and Android 21 still send `foodsAvoided`, so Abram's weekly re-count stays until the branch Brain is live.

**Not built, by design (each after the round):**
- the apps reading the catalogue, discovery, group plans, the display currency, and the stay and trip-length "why";
- Paris, Amsterdam and Brussels as real places: they need checked cards, travel, holidays and emergency numbers first;
- live journey times between cities;
- group accounts and invitations;
- Android export and import (approved, #95);
- per-country emergency numbers in the apps (#96);
- the first-day food stop (#97).

**Unverified or unread:**

| What | Why | Where it's marked |
|---|---|---|
| LiteAPI pricing | its pricing page returned 404 | `display-currency-and-price-providers.md` |
| Booking.com Demand API access terms | the getting-started page returned 404 | the same |
| GetYourGuide Partner API | the page had only a title | the same |
| Amadeus self-service closure | **reported** by PhocusWire and a third-party guide; Amadeus's own page was empty | the same |
| TfL's open-data page (the current setup is unchanged) | refused automated reading (403) | the same |
| Nager.Date (holidays) | redirected to another host, not followed | `destination-intelligence.md` |
| The Mobility Database's and OpenTripPlanner's licences | not stated on the pages read | the same |
| Belgian police | police.be refused automated reading (403); the numbers came from securitecivile.be | `emergency.yaml` |
| The NHS emergency pages | read, but past their own review dates | `emergency.yaml` |
| Masthoff's group-recommender chapters | 403, 404 and a sign-in wall; Sato's paper was used | `group-travel.md` |
| 39 of the 45 photo credits | Commons refused a batch read (HTTP 429), not retried in a loop | `design/photo-credits.md` |

## 3. Files changed

48 files, 11 commits (`9238fc0`..this report).

| Area | Files |
|---|---|
| Brain (new) | `catalogue.py`, `destination.py`, `quality.py`, `discovery.py`, `group.py` |
| Brain (changed) | `itinerary.py`, `fx.py`, `explain.py`, `offline.py`, `places.py`, `triplength.py`, `trips.py`, `schemas.py`, `api.py` |
| Brain data | `catalogue/london.yaml` (new), `emergency.yaml` (new), `destinations.yaml` (`region_code`) |
| Brain scripts and benchmarks | `compare_group.py` → `benchmarks/synthetic/group.txt`; `compare_food_interest.py` → `food_interest.txt` |
| Brain tests | new: `test_catalogue.py`, `test_destination.py`, `test_multicity.py`, `test_discovery.py`, `test_group.py`, `test_photo_credits.py`, `fixtures/destination_testville.yaml`. Changed: `test_currency.py`, `test_explain.py`, `test_categories_global.py` |
| iPhone | `Offline.swift` (the section title) |
| Android | `Offline.kt` (the section title) |
| Decisions | new: `global-experience-catalogue.md`, `destination-intelligence.md`, `experience-discovery.md`, `display-currency-and-price-providers.md`, `group-travel.md`, `food-interest-learning.md`, this report. Changed: `decision-log.md` (m234–m243), `multi-city-travel-architecture.md`, `explanations.md`, `offline-companion.md`, `foods-avoided-audit.md`, `after-9-nov.md` (#95–#97) |
| Other | `CLAUDE.md` (the quality standard); `design/photo-credits.md` (the re-check) |

## 4. Test results (10 Nov)

| Suite | Result |
|---|---|
| Brain (`pytest`) | **396 passed**, 0 failed (one library deprecation warning). It was 348 at the last report |
| Android (`testDebugUnitTest`, Robolectric) | **119 tests, 0 failures, 0 errors** |
| iPhone (CI run #108, simulator, `upload: false`, commit `3a31957`) | Running when this report was first committed; the result is added here when it finishes. The only Swift change is the section title in `Offline.swift` |

## 5. Sources

Every source is listed, with its URL and the date it was read, in the document that uses it. **All were read on 10 Nov 2026,** except the places table carried over from 7 Nov (`global-place-data.md`):
- **Emergency numbers:** official pages per country (`brain/data/emergency.yaml`, one URL per line).
- **Providers:** places, districts, travel, holidays and weather (`destination-intelligence.md`).
- **Exchange rates and prices:** ECB, Frankfurter, Open Exchange Rates; flights, hotels, activities and transport (`display-currency-and-price-providers.md`).
- **Group fairness:** Sato, "Enumerating Fair Packages for Group Recommendations", WSDM '22 (arXiv 2105.14423), in `group-travel.md`.
- **Photo licences:** six Wikimedia Commons file pages (`design/photo-credits.md`).

## 6. Needs Abram's approval or action

| # | What | Time |
|---|---|---|
| 1 | **The `foods_avoided` count,** and the delete if any exist. Make sure a clean replacement backup exists before deleting older ones. Re-count weekly (`foods-avoided-audit.md`). **Unchanged from m234** | ~10 min, then ~2 min a week |
| 2 | **Groups: Nash or least misery?** Nash is proposed: it stops one member dominating, and has the best chance that everyone gets a favourite. Least misery has the smallest gap, but leaves more people without a favourite | a decision |
| 3 | **Which city comes second?** Abram chooses the city; it's a scope decision. Its profile needs 20–30 checked cards, areas, travel, holidays and emergency numbers (`destination-intelligence.md`) | Claude ~20–30 h; Abram's review ~2 h |
| 4 | **London's data gaps:** step-free access for 45 cards; an area for every card; season notes. They make discovery and accessibility honest | Claude ~4 h + ~1.5 h + ~1.5 h; Abram ~0.5 h to check the categories and areas |
| 5 | **After the round, in both apps:** the currency choice (~3 h); "why" on stays and trip lengths (~2 h, reusing the stop card); the first-day food stop (~2 h, Brain) | ~7 h |
| 6 | **Providers: no money is needed now.** Later decisions: Overpass hosting; Transitland, or hosting OpenTripPlanner; commercial Open-Meteo outside the UK | each a later decision |
| 7 | **Before the public release:** re-read the other 39 photo pages | Claude ~0.5 h |
| 8 | **Unchanged:** the four councils (when practical), the DPIA with the solicitor, and the visual review of the offline view and "Why this stop?" | as before |

**Hours (Claude, approximate):**

| Item | Hours |
|---|---|
| Decisions | ~0.5 |
| Catalogue | ~3 |
| Destination intelligence | ~3.5 |
| Multi-city | ~3 |
| Display currency | ~2 |
| Discovery and quality | ~3 |
| Groups | ~3 |
| Explanations | ~1.5 |
| Food interest | ~1.5 |
| Photos | ~1 |
| Report | ~0.5 |
| **Total** | **about 22.5 h** |
