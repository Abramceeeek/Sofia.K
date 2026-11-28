# The plan: London right first, then a city a day (24 Nov 2026; m323, proposed)

Abram, 23 Nov:
- "As soon as we evaluate that the London one is … enough coverage of places … and … more personalized … then we will move to another city. And I want to do every single city every day."
- On food: "If it is possible to get Google's database or the Apple Maps database … it would be a quick way … If it was possible to understand if they are halal or not … vegetarian … what kind of cuisine."

## Decision first

1. **London fails its own gate today.** Three independent reviews of six example trips, from the real planner, agree: "not yet" (`validation/london-examples/reviews-2026-11-24.md`).
   - The writing about each place is strong.
   - The planning has five faults that would hurt any city we add: days end hours early, silent waits, loved places missed, disliked kinds coming back, and untrue "Why" lines.
   - **These are planner faults, so copying London's method to new cities would copy them too.** London is fixed first.
2. **Google's and Apple's place databases can't be copied.** Their terms forbid it (`city-expansion-playbook.md` §5). The quick, legal way to "see how it would work" is open data. **It is already working:** Greater London's places were pulled from Overture on 23 Nov (§2).
3. **Halal, vegetarian, vegan and cuisine are available as place labels from open data,** but they are thin and unverified (§2). They can be shown on a place as what the source says ("listed as halal by OpenStreetMap contributors; check with the venue"). **A person's own halal or food preference still waits for the solicitor's DPIA review (m224)**, because halal can reveal religion. Cuisine as a taste ("I enjoy Indian food") is lower risk, but it is a new onboarding question, so it waits for the round.
4. **"A city a day" is realistic only for the Preview level,** after the engineering (E1–E7), and only once London passes. Preview means places and opening days, without plans. Plannable cities take 2–3 days each. **Abram's part is 30 minutes of review a day.** That fits only if review stays that small: 3.5 h a week out of his 7.5.

## 1. The order, with hours

Claude's hours are estimates. Abram's hours come out of his 7.5 a week.

| Phase | What | Claude | Abram | Done when |
|---|---|---|---|---|
| **0. Now** | ✅ The lunch fix (m321) on the branch: food places now reach trips (0 / 1 / 2 / 4 / 0 for five kinds of person; 577 tests pass) | done | decide whether it ships with the next release | — |
| | ✅ Six example trips, three independent reviews, and the question pack for other AI models | done | **send the pack to 3–4 other models (about 30 min)** | their answers are saved in `validation/london-examples/answers/` |
| | ✅ The open-data pull for London (Overture: 781,690 places) | done | — | — |
| **1. Fix London's planning** (the reviewers' 10) | Fill the person's window (no early ends; evenings for night people) | 6–8 h | — | no simulated day ends more than 45 min early |
| | No silent waits; free time is labelled, or the plan works back from timed stops | 4–6 h | — | no unlabelled gap over 20 min |
| | One stop matching a loved place per trip; dislikes counted by features, not only the name | 4–6 h | — | each of the six gets a loved-type stop and none gets a disliked type |
| | "Why": one true reason and at most one "Good to know"; the internal lines and the false "best time" lines dropped | 4–6 h, both apps | 15 min of screenshots | the UX review's 12 items done |
| | Card rules enforced (age, booking, kit); December-true text; costs for the party | 4–6 h | — | the family never gets the bike ride |
| **2. Fill London's gaps** | About 35 checked cards: the 8 swipe places with no card, about 12 named food places (cuisines and price bands, Sunday and evening), 6 evening, 5 for children, 4 big history (`reviews` list) | about 12–15 h (20 min a place, the Seville rate) | **30 min**: Claude gives one list with a line each to flag (D91) | `readiness.checklist` passes, with 8+ kinds |
| | Lunch "near X" becomes up to 3 named nearby places from open data, marked "listed, not checked" | 4–6 h | — | the median stop has 159 open food places within about 300 m (§2) |
| **3. The London gate** | Re-run the six travellers and the three reviews; read the other models' answers | 2 h | 30 min | **Passed:** every traveller averages ≥ 4/5; the London guide answers "yes"; each person's "one change" happens unasked; and the friends' round has started (real people, m196) |
| **4. Engineering for any city** (E1–E7 in the playbook) | The planner reads checked catalogue places; travel and arrivals outside London; the apps' destination list and country emergency numbers; the registry obeys readiness | 35–55 h | about 2 h of screenshot reviews and one TestFlight install | Seville plans a day in simulation |
| **5. A city a day** | Each day, one city to Preview: the country items if new, about 20 checked places, emergency numbers, holidays, transport said as it is | 6–8 h a city | **30 min a city** | the readiness check says Preview, and Abram signs it off |
| | Plannable when people go there: 60 checked places, transport estimates, arrivals | 15–20 h a city | about 1 h | readiness says Limited support |

**Elapsed time:** Phases 1–3 take about 2 weeks. Phase 4 takes 2–3 weeks. A city a day can start after that, around **mid-to-late December**, as long as the gate has passed. **Nothing reaches `main` while the friends' round runs** (m198), unless Abram moves the round again.

## 2. Food data we can get legally: what London's pull shows

**The source:** Overture Maps, release 2026-11-18.0, pulled on 23 Nov 2026 for Greater London's box (licence CDLA-Permissive-2.0 or Apache-2.0 depending on the source; no OpenStreetMap data).

| | Count |
|---|---|
| All places in the box | **781,690** |
| Food and drink (restaurants, cafés, coffee, bars, bakeries, fast food, food courts) | **70,291** |
| … with confidence 0.7 or more, and not marked closed | **49,126** |
| … with a website | 42,328 of the 50,021 confident ones |
| Restaurants by cuisine (confidence 0.7 or more), top | Indian 2,470 · pizza 1,902 · Italian 1,676 · Chinese 1,369 · fish and chips 813 · burger 710 · Turkish 604 · British 600 · Thai 575 · Japanese 565 |
| Labelled `halal_restaurant` / `vegetarian_restaurant` / `vegan_restaurant` / `kosher_restaurant` | **115 / 264 / 162 / 31** |
| Open food places within about 300 m of each of London's 49 ready stops | median **159** (from 1 at Regent's Park to 918 in Soho and Chinatown) |
| Our checked food places found in Overture | Beigel Bake (confidence 1.0), Meet Bros Steakhouse (1.0), Café in the Crypt (0.99): matched by name |

**What this means:**
- **Cuisine is well covered.** Most restaurants carry a cuisine category, so "Indian food near here" is possible from open data today.
- **Diet labels are thin.** 115 halal restaurants for all of London is far below reality. A label is the source's category, not a certificate.
- **Opening hours and prices are not in Overture.** Anything a plan relies on still needs the venue's own page (the checked layer).

**OpenStreetMap diet tags, worldwide** (taginfo, 23 Nov 2026): `diet:halal` on 30,844 places (yes 16,861, only 2,332, no 11,626), `diet:vegetarian` 120,328, `diet:vegan` 69,130, `cuisine` 1,542,536, `opening_hours` 4,948,311. **London's counts:** see §2b. OSM is ODbL: credit "© OpenStreetMap contributors", and share-alike on what's built from it, so its labels are kept as a separately credited source.

**How a diet label would be shown** (place data, not personal data; the rules in `food-preferences-and-privacy.md`):
- "**Listed as halal** by OpenStreetMap contributors · check with the venue."
- "Certified" only with a named certifier's own listing and its date.
- Nothing is inferred from a cuisine, a name or a neighbourhood.
- **Never filtered by a person's need** until the DPIA review allows the on-phone filter.

**Next steps for food data (Claude's hours):**
- Foursquare OS Places as a second source. **It needs a free token from Foursquare's Places portal, which Abram creates (about 10 min).** Claude: 3–4 h to pull and merge.
- A London food table that joins Overture, Foursquare and OSM by name and distance, with every field's source: 6–8 h.
- Google's live details (hours, rating, price) only after the current Service Specific Terms are read on the non-Google-map clause. This is a likely blocker (playbook §5).

## 2b. OpenStreetMap in London

**Partial: 20 of the 36 map tiles answered.** The public Overpass mirror, the only one reachable from here, timed out on the other 16, central London among them. So these are shares, not London's totals. Queried 24 Nov 2026; data © OpenStreetMap contributors, ODbL.

| In the 20 tiles that answered | Places | Share |
|---|---|---|
| Food and drink (restaurant, café, fast food, pub, bar, ice cream, food court, beer garden) | 10,168 | — |
| with a `cuisine` tag | 5,758 | 56.6% |
| with a `website` | 2,791 | 27.4% |
| with `opening_hours` | 2,242 | **22.0%** |
| with `wheelchair` (access) | 889 | 8.7% |
| `diet:vegetarian` = yes or only | 544 | 5.4% |
| `diet:vegan` = yes or only | 286 | 2.8% |
| `diet:halal` = yes or only | **130** | **1.3%** |

**What it means:**
- OSM adds what Overture lacks: **opening hours for about one place in five**, and some access information. These are a second source for the checked layer, never a replacement for the venue's own page.
- **Diet tags are rare:** halal on about 1 place in 77. Like Overture's 115 halal restaurants, that is far below how many halal places London has.
- **No open source answers "which places are halal" well enough to filter by it.** The honest options are:
  - show the label where a source gives it, saying which source;
  - later, a certifier's own published listing, if one publishes data that may be reused (to research);
  - or the venue's own words, read on its page.
- To get all of London's tiles, either retry the mirror at a quiet hour, or allow an OSM extract download (Geofabrik is blocked here). That needs one environment change, which Abram approves.

## 3. What Abram does this week

1. **Send the question pack to 3–4 AI models** (`validation/london-examples/questions-for-other-ais.md`) and save their answers. About 30 min.
2. **Decide whether the lunch fix ships now or after the round.** It changes the personal plans in the round's build.
3. **Create a free Foursquare Places portal token** if you want the second food source. About 10 min. It goes into the environment's secrets, never into the chat.
4. **The earlier list still stands:** Render Auto-Deploy off, the database IP rule removed, the database password rotated, `android-latest` deleted, and the database upgrade by 2 Dec.
