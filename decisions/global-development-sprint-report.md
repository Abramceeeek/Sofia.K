# Global Travel Intelligence sprint: report (7 Nov 2026)

**In one line:** all eight workstreams are done to the point each can be safely done before the friends' round ends. Each has its design page, working code and tests. Four of them changed both phones. Two planner bugs were found and fixed. Every decision that is Abram's, or costs money, is listed at the end.

The frozen experiment wasn't touched:
- `main` is still `80a0da3` and the live Brain answers `"version": "80a0da3"` (checked at the end of the sprint);
- no TestFlight upload, no APK published, no tag, no email sent;
- no paid call, no key used;
- `stay_dates_live` stays `False`;
- no database schema change (`db.py` and `render.yaml` untouched).

**Branch:** `claude/vigilant-cannon-my82dj`: 13 commits, from `22e087c` (the LiteAPI email) to this report; 51 files changed.

**Tests at the end:**
- **Brain:** 281 passed (229 at the start; +52).
- **Android:** 98 passed (94 screen tests including 2 new large-text ones, `MoneyTest`, 3 contrast tests).
- **iPhone:** the m209 build compiled on CI (run #99, simulator build "success"). The next run (#100) **failed to compile**: giving `Money.whole` a currency argument broke one place that passed it as a function reference (`BookViews.swift:1251`). That was the only error. It's fixed (79356c0), and run #101 compiled ("Build for the simulator: success").

## Workstreams

| # | Workstream | Status | Page | Commits |
|---|---|---|---|---|
| 7 | Recommendation engine benchmark | **Done** | `recommendation-engine-evaluation.md` | 9d99fd9, e50b8c8 |
| 1 | Global destination data | **Done** (design and a non-breaking layer) | `global-place-data.md` | b3205a2 |
| 2 | Food, dietary and halal | **Research and model done**; screens waiting on decisions, by design | `food-preferences-and-privacy.md` | 2a8cf86 |
| 4 | Hotel intelligence | **Done**; the lenses screen waits for live prices | `accommodation-ranking.md` | 210f830 |
| 3 | Several places in one trip | **Architecture and module done**; not wired, by design | `multi-city-travel-architecture.md` | b81f01a |
| 5 | Travel calendar | **First slice done** (2 councils checked) | `travel-calendar-intelligence.md` | 144a543 |
| 6 | The whole trip's cost | **Model done**; the screen waits for live prices | `full-trip-budget.md` | 480cc46 |
| 8 | Global UX and parity | **Done** | `global-mobile-ux-audit.md` | abfb888 |
| — | The experience model | **Done** | `experience-model.md` | 0d2b51d |
| — | The LiteAPI email (Abram's wording) | **Ready for Abram to send** | `liteapi-clarification.md` | 22e087c |
| A | Provider adapters | **Partly**: `PlaceProvider`, and every fact with its source, date and trust (WS1). Failure and refresh policy not written | — | b3205a2 |
| B | "Why this?" explanations | **Not started**: time went to the eight workstreams. The stops already explain themselves from real inputs (`reasons.py`); stays and trip length are next | — | — |
| C | Offline travel | **Not started**, for the same reason | — | — |

### WS7: the planner benchmark
- **Before:** `algorithm_checks.py` only, on random simulated people. Nothing checked plans from outside the solver.
- **Changes:**
  - `brain/scripts/benchmark_planner.py`: 11 fixed synthetic travellers × 12 kinds of day × 4 plans (known tastes, after onboarding, no answers, a greedy baseline). Every hard rule is checked from outside; seed 20261107.
  - Its own checks have tests (7).
- **Results:**
  - 0 rule breaks in 1,188 plans.
  - Known tastes beat no answers on 121 of 132 days.
  - The solver beats greedy on 96, with 8 losses over 0.1.
  - Re-planning changed 2 of 120.
- **Two planner bugs, fixed, each with a test that fails on the old code:**
  - a lowered floor could leave a day short (an evening got 1 place, not 3);
  - a dislike of packed days made places chosen by distance alone.
- **Open:** days with personal time sometimes stop at a poor plan within 1 s. The short onboarding learns little except nature.
- **Limits:** synthetic only, straight-line travel times, London's 49 cards.

### WS1: places anywhere
- **Before:** London assumed in about a dozen places (audit table on the page).
- **Changes:**
  - a destination registry (`data/destinations.yaml`), now the source of the bank-holiday region;
  - `places.py`: one place record for any source, every fact `checked`, `claimed` or `unknown`, with an adapter for the London cards (IDs unchanged) and one for OSM;
  - 5 tests, including a guard that the two destination lists agree.
- **Sources compared** with links and terms: OSM, Overpass, Nominatim, OSM tiles, Wikidata, Overture, Foursquare, Google Places, GeoNames.
- **Limits:** the planner doesn't use it yet; cards have no category; the model's cost feature is in pounds.

### WS2: food needs
- **Before:** no food data (D19, D123).
- **Proposed:**
  - all needs treated as special category data; explicit consent; kept on the phone only;
  - one purpose, enforced in code;
  - allergies never stored ("ask the venue", as the FSA's rules make venues answer);
  - "certified" only with a certifier's listing and date.
- **Built:** `food.py`, 7 tests on synthetic venues.
- **Limits:**
  - The ICO pages refused automated reading, so they were read through ICO-domain search extracts (said on the page).
  - HFA has no public directory that could be found.
  - Kosher and vegetarian sources aren't researched.

### WS4: places to stay
- **Fixed on both phones:**
  - the arrival and leaving days count only the legs that happen;
  - a day without places is said;
  - unknown meals or cancellation terms are never "the same";
  - a fee or a rate in another currency is never added or compared;
  - a missing currency is said.
- **Added:** four separate lenses (cheapest, closest to your days, most flexible, trade-offs), with no blended score; 10 tests.
- **Screens:** Android `32c-stayfortrip`; iPhone `stayfortrip`.

### WS3: several places
- Segments and journeys, planned by the one existing planner, one request per place, with no server migration.
- Zone-aware times through the clock change, overnight trains, gap days, plain-words date checks, and only the affected days re-planned.
- A 10-day European example; 6 tests. Not wired.

### WS5: the calendar
- Home and destination calendars kept apart; bank and school holidays kept apart.
- Checked school holidays for Cardiff (Welsh Government) and Edinburgh (the council), 2026-27. Camden and Manchester refused automated reading, so nothing was copied.
- Unknowns are said. 8 tests.
- The stay comparison says when holidays aren't known, on both phones.

### WS6: the trip's cost
- Lines that each say what they are. "At least £907 so far", never "the total".
- No currency converted without a dated rate.
- Against a budget: the gap and what could move.
- The £900 example; 6 tests. Not wired.

### WS8: UX and parity
- **Fixed on both phones:**
  - prices keep their own currency;
  - the price box stacks at large text (it split "testing" mid-word);
  - "Try again" when the stay comparison fails.
- **New screenshots:** large text on a small screen (Android `90`, `91`; iPhone `*-largetext` in CI).
- **Audited and written down:** dates, 24-hour times, time zones, RTL, contrast, labels.

## Architecture problems (found, not hidden)

1. **Two destination lists** (`airports.yaml` for trips, `destinations.yaml` for the registry), with different London centres. A test keeps them in step. Merge them before a second destination (~1 h).
2. **The model's cost feature is per £10.** Another currency needs a dated conversion or a per-currency weight: a modelling decision.
3. **Europe/London is hard-coded** in both apps' date maths (11 places in the iPhone app, and Android's `ZoneId`) and in parts of the Brain. It's correct for London; at the second city it switches to the registry's zone.
4. **The 1-second search** on days with personal time (WS7 finding 3).
5. **The onboarding's six named places** learn nature tastes but little else (WS7 finding 5). Abram's to-do: kinds of places for everyone, after-9-Nov #86.
6. **Flight offers in mixed currencies** are sorted by number in the Brain. The apps now show each currency correctly, but "cheapest" across currencies isn't like for like. To fix with the exchange-rate decision (~0.5 h).
7. **The Android map's OSM tiles** aren't for a commercial app at scale. A provider is needed before public release.

## External dependencies and costs (nothing paid in this sprint)

| Service | Cost (as read 7 Nov) | Status |
|---|---|---|
| LiteAPI rates | Free under a "reasonable look-to-book ratio"; the price index $0.05 a request | Sandbox; email to Nuitée ready; index never called |
| Duffel | $0.005 a search beyond 1,500 an order (capped at $1 a day, Stage 1) | Test mode |
| Google Places (New) | Per 1,000 after free caps: Essentials $5, Pro $17, Enterprise $20, + Atmosphere $25 | Not used; only place IDs could be kept |
| Overpass (OSM queries) | The public server isn't for commercial use; a paid or self-hosted one costs money (not priced here) | Not used |
| OSM tiles | Free, best effort, no guarantee | Android map today |
| Wikidata, Overture, GeoNames | Free (CC0; CDLA and Apache; CC BY) | Not used yet |

## Decisions for Abram

1. **Send the LiteAPI email** (`liteapi-clarification.md`) to hello@nuitee.com, and forward the reply.
2. **Planner, days with personal time** (WS7 finding 3): start from a greedy plan (~2 h, recommended), or a longer time limit.
3. **Lunch and a small budget** (WS7 finding 4): lunch outside the places budget, or keep it in and say so (~1 h either way).
4. **Food needs:**
   - the Article 6 basis;
   - phone-only storage;
   - no allergy storage;
   - sign-off of the DPIA (Claude drafts it, ~2 h) and of the privacy notice, before any screen.
5. **Money, before a public release (not now):** Overpass hosting; an Android tile provider.
6. **Legal, before a public release:** whether keeping OSM facts in a separate layer satisfies ODbL's share-alike.
7. **When a second currency matters:** the exchange-rate source; and whether to estimate dinners.
8. **Before strangers:** a 15-minute VoiceOver and TalkBack pass on your phones.
9. **After the round:** kinds of places for everyone in onboarding (#86).
10. **Unchanged, for the friends' round:**
    - push the tag `friends-round-1`;
    - the rehearsal;
    - the Apple outside-activities check;
    - TestFlight's external review;
    - then recruiting (`validation/friends-round.md`).

## The next sprint (proposed; hours are GUESSES)

| Order | Work | Claude | Abram |
|---|---|---|---|
| 1 | The planner's search on days with personal time (decision 2) and the lunch line (decision 3) | 3 h | 0.25 h |
| 2 | Merge the destination lists; categories on every card | 3 h | 0.25 h |
| 3 | The food DPIA draft, then the screens once decision 4 is made | 2 h, then 5 h | 1 h |
| 4 | Kinds of places for everyone, measured with the benchmark first (#86), after the round | 4 h | 0.5 h |
| 5 | Live prices on the staging Brain once Nuitée replies: nearby dates, then watched stays | 6 h | 0.25 h + the key |
| 6 | The trip's cost screen and the stay lenses screen, on live prices | 10 h | 0.5 h |
| 7 | A second destination: choose it, its cards, its place extract, its travel and calendar | 15–25 h | choosing, checking |
| 8 | Extras B ("why this?" for stays and trip length) and C (offline days) | 6 h | 0.5 h |

**Sprint hours:** Claude ~25 h (estimated from the work; not timed). Abram: none during the sprint. The decisions above are about 2 h, spread out.
