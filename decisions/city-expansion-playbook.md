# Adding cities and countries: the playbook (21 Nov 2026; proposed, m322)

Abram, 21 Nov: "I want to make a checklist that we go through to add a city or a country … I want to cover all cities and all countries at some point … all food places that are in Google Maps or Apple Maps … I want full understanding of how fast we can get other countries and cities."

## Decision first

1. **Three layers of places, not one.** London was slow because every place was built as a hand-made moment. Covering the world needs three layers, each with its own job and its own label in the app:

| Layer | What it is | Where it comes from | Can a plan use it? | Label in the app |
|---|---|---|---|---|
| **Listed** | every place we can find: name, point, kind, website, phone | open data (Overture, Foursquare OS Places, OpenStreetMap), pulled by a script | not as a timed stop; for "nearby" and "lunch near here" ideas | "Listed, not checked" |
| **Checked** | a place whose hours, price, access and notices were read on its own official page, with dates | Claude, one place at a time (as Seville on 20 Nov) | **yes**: this is what plans are built from | the hours' source and date |
| **Moment** | a checked place plus the experience: route in, best time, shot card, feeling words | Claude and Abram, and later locals | yes, ranked highest | as now in London |

2. **Google Maps and Apple Maps can't be our database.** Their terms forbid copying their places:
   - **Google** lists "copy and save business names, addresses, or user reviews" and "bulk download" as prohibited. Only place IDs may be stored indefinitely, and coordinates for at most 30 days.
   - **Apple** bars "the creation of any databases based upon results".
   - So "every food place in Google Maps" can only be **shown live**, at the moment someone asks, paid per call, and never stored (§5).
   - **Our own coverage comes from open data,** which may be stored: Overture (about 88 million places) and Foursquare OS Places (over 100 million).
3. **Plans need the checked layer, and that is the bottleneck.** About 20 minutes of research per place (Seville: 20 places plus Spain's basics in about 7 h). **Expansion is therefore by demand:** cities where testers actually go get checked places first; everywhere else is Listed only.
4. **Before any second city can be *planned* (not just previewed), about 40–55 h of one-time engineering** is needed (§4). After that, each new city takes about **6–8 h of Claude's research to Preview and 15–20 h to Plannable**, plus **30–60 min of Abram's review**. A second city in a country already done costs about a third less.

## 1. The levels a city goes through

The levels are the ones already in `brain/src/brain/readiness.py` (m259–m263), plus Listed before them.

| Level | What a person gets | Needs (all checked by `readiness.checklist`) |
|---|---|---|
| **Listed** | search and a map of places, all marked "not checked"; no plans | the open-data pull for the city (§5) |
| **Development** | nothing in the app; data being built (Seville until 21 Nov, Paris) | the country checklist started |
| **Preview** | a read-only list of places with each day's state (Seville since m320, behind a code) | the essentials: emergency numbers, holidays, currency, time zone, **20 checked places**, **6 kinds**, transport (official, or "no journey times" said plainly) |
| **Limited support** | plans, with gaps said | Preview, plus fresh hours and named areas, and Abram's review |
| **Supported** | plans, trips and the "Now" screen, as London | every item passes, and Abram's final review with a date |

## 2. The country checklist (once per country)

Each item needs its official source and the date it was read (CLAUDE.md rule 1).

| # | Item | Source (official only) | Where it goes | Seville (Spain) |
|---|---|---|---|---|
| C1 | Emergency numbers, with what each is for | the government's own page; GOV.UK foreign travel advice as a cross-check | `data/emergency.yaml` | ✅ 112 |
| C2 | Public holidays for this year and next: national and regional | the government gazette (Spain: BOE) | the destination file | ✅ national and Andalusia; local ❌ |
| C3 | School holidays, where they change crowds | the education ministry, or the region | the destination file | ❌ missing |
| C4 | Currency, and the rate source | ECB reference rates (`fx.py`) | the destination | ✅ EUR |
| C5 | Time zone(s), clock changes | IANA (`zoneinfo`) | the destination | ✅ Europe/Madrid |
| C6 | Languages; date and number formats | — | the destination | ✅ languages; formats ❌ |
| C7 | Weather source, and its licence | the national met service; the Met Office "Global spot" API the Brain already uses names itself global (check its quota first) | `weather.py` provider | AEMET read, not integrated |
| C8 | Transport authorities: the national rail operator, city operators, a journey planner or GTFS feed | the operators' own sites; Mobility Database or Transitland for feeds | the destination's transport block | ❌ unreadable (TUSSAM 403) |
| C9 | GOV.UK travel advice link (ODYS links to it, never restates it) | gov.uk | the city screen | ✅ read |
| C10 | Anything that limits what ODYS may say there (food claims, accessibility claims, consumer rules) | the regulator | `decisions/` note | — |

**Cost:** about 2–3 h of Claude's work for a new country (Spain: about 2 h). Reused by every city in it.

## 3. The city checklist

| # | Item | Done when | Seville now |
|---|---|---|---|
| T1 | **The registry entry:** key, name, country, time zone, currency, a named centre point | in `data/destinations.yaml` (or `data/dev/` until Preview) | dev file ✅ |
| T2 | **Arrival hubs:** airports and main stations, each transfer with its price and hours (operators' pages) | in the arrivals config (`tripdays`) | Aena bus and taxi ✅; config ❌ |
| T3 | **Areas:** named neighbourhoods, each from a source | every checked place has one | 20 of 20 ✅ |
| T4 | **Local holidays,** and dated city closures | in the destination file | ❌ |
| T5 | **Transport:** the official journey planner or a GTFS feed; otherwise estimates, labelled as such | the transport block | ❌ |
| T6 | **The Listed pull:** open data for the city's area, deduplicated, closed places dropped | a count by kind | not built |
| T7 | **Checked places, by kind.** Preview: 20 places and 6 kinds. Plannable: 60 places, and in each kind at least culture 10, views 4, nature 4, neighbourhood 4, **food 12** (markets, cafés, restaurants, across price bands; some open on Sundays and evenings), shopping 4, activity or entertainment 4 | `readiness.checklist` passes | 20 places, 5 kinds; food 6 |
| T8 | **Seasons and notices:** seasonal hours, works, dated closures | each with dates | partial |
| T9 | **Photos:** each licence checked one by one, or the satellite view | `photo-credits` | none (satellite) |
| T10 | **The portability check:** the synthetic travellers (`benchmark_profiles.py`) find their own kinds | the report, never called evidence | ✅ run |
| T11 | **Readiness → level, then Abram's review, then the registry switch** | the level written down with its date | Development; Preview by code |
| T12 | **The apps:** CI screenshots of the city's screens on both phones | screenshot pages | ✅ Preview |
| T13 | **Freshness:** hours re-read within 180 days; a place that fails becomes "check" | a scheduled re-check | — |

## 4. One-time engineering before a second city can be planned

| # | Work | Why | Claude's hours (estimate) |
|---|---|---|---|
| E1 | **The planner reads checked catalogue places** (`Experience`), not only London's moment cards | today's day and trip planner only knows `brain/data/moments` (London) | 8–12 |
| E2 | **Travel times outside London:** walking plus a public-transport estimate, labelled "estimate" | `tripdays` and the planner use TfL and the London estimate | 6–10 |
| E2b | Later: real public-transport times from Transitous (free, open, community-run; built on MOTIS and GTFS feeds) | real times where feeds exist | 15–25 |
| E3 | **Arrivals for any city:** airports and stations from the city file | `tripdays` knows London's airports and stations only | 4–6 |
| E4 | **Weather outside the UK:** confirm the Met Office global API, or a national service per country | plans use weather for outdoor stops | 3–6 |
| E5 | **The apps:** the destination list from the Brain (not "london" hard-coded), the trip country's emergency number (not only 999), local currency and time | both apps hard-code London and 999 (m319) | 10–16 |
| E6 | **The registry obeys readiness:** a city is offered only at its level, with what it lacks said | so nothing unchecked reaches people | 2–3 |
| E7 | **The lunch fix** (m321), so food places can be a day's lunch | otherwise new cities repeat London's problem | 2–3 |
| | **Total** | | **about 35–55 h, plus E2b later** |

**Abram's part:**
- reviewing each step's screenshot page, about 15 min a step;
- one TestFlight build at the end.

## 5. Food at scale: how we find, check and show eating places

### Finding (the Listed layer)
- **Overture Maps Places:** about 88 million places, released monthly.
  - Licence CDLA-Permissive-2.0 or Apache-2.0 depending on the source, and no OpenStreetMap data, so no share-alike.
  - Fields: names, addresses, websites, phones, a confidence score, brand, a taxonomy.
  - **No opening hours, prices or ratings** in the guide.
- **Foursquare OS Places:** over 100 million places, Apache 2.0, free with attribution.
  - Since October 2025 it is downloaded through its Places portal, Snowflake or Hugging Face, no longer from public S3.
  - Fields: name, point, address, phone, website, social handles, categories, and a date it was marked closed.
  - **No hours, price, ratings or popularity.**
- **OpenStreetMap:** the `opening_hours` tag (for example `Mo-Fr 08:00-17:00`) where mappers have added it.
  - Licence ODbL: credit "OpenStreetMap contributors", and share-alike on what is built from it.
  - So OSM hours are kept as a separate, credited source, and never mixed silently into our own data.

**The pull, for each city:**
1. Food categories inside the city's area.
2. Keep places with Overture confidence above a threshold, and drop those marked closed.
3. Deduplicate Overture against Foursquare by name and distance.
4. Each kept place becomes a Listed record carrying its source ids.

### Choosing which to check (the Checked layer)
Check the food places plans will need first:
- near the clusters of checked sights, where days actually go;
- markets and food halls;
- a spread of cuisines and price bands;
- some open on Sundays and in the evening;
- the places a city is known for.

Seville's gap shows why: all four of its markets close on Sundays.

### Checking each place
- **Hours:** from the venue's own site, with the date read. An OSM `opening_hours` value, if present, is a second source; when the two disagree, add a "check" notice.
- **Price:** only if printed (a menu price or set menu), with the date. Otherwise "Price not printed".
- **Kind:** market (whose hours are the market's, never a stall's), restaurant, café, bakery, street food, bar.
- **Step-free:** only if the venue says so.
- **Reservations and deposits:** as printed (for example, Casa Robles' €20 no-show fee).
- **Never as data:** dietary claims (halal, vegetarian, allergens) stay out until the DPIA path is done (m224). A venue's own words may be kept as a comment only.

### Showing live places from Google (later, optional)
This is the only lawful way to show "everything on Google Maps". The place details are fetched when the person opens a place, shown, and not stored.

**Costs, read on 21 Nov 2026 (USD per 1,000 calls; first tier):**

| Call | Free a month | Price | Fields |
|---|---|---|---|
| Place Details Enterprise | 1,000 | $20.00 | opening hours, rating, price level |
| Place Details Enterprise + Atmosphere | 1,000 | $25.00 | adds reviews |
| Text Search Pro | 5,000 | $32.00 | — |

**Rules for showing them:**
- the Google Maps logo or "Google Maps" next to the content;
- every review or photo credited to its author, with a link to it on Google Maps;
- only place IDs may be kept.

**UNVERIFIED and a likely blocker:** archived versions of Google's Service Specific Terms say Places content must not be used "in conjunction with a non-Google map". ODYS's maps are Apple Maps on the iPhone and OpenStreetMap on Android. The current terms must be read before any build.

**Apple Maps Server API:** 25,000 calls a day per team (Maps Server API and MapKit JS together). Caching is allowed only temporarily, and databases built from its results are barred.

## 6. How fast: the timeline

These are estimates. They come from the Seville sprint, where 20 places plus Spain's basics took Claude about 7 h, and Abram's review is separate.

| Step | Claude | Abram | Elapsed (with Abram's ~7.5 h a week) |
|---|---|---|---|
| E1–E7, the one-time engineering | 35–55 h | about 2 h of screenshot reviews, plus one TestFlight install | 2–3 weeks |
| The Listed pull (a script, then any city) | 15–25 h once; under 1 h a city after that | 10 min a city | 1 week |
| A city to **Preview** (20 checked) | 6–8 h | 30 min | 2–3 days |
| A city to **Plannable** (60 checked, transport estimates, arrivals) | 15–20 h | about 1 h | about 1 week |
| The next city in the same country | about a third less | the same | — |
| A city to **Supported** (moments, a local's review, licensed photos, official transport) | another 20–40 h | 1–2 h, plus a local reviewer | 2–3 weeks |

**What that means in practice:**
- **Seville to Plannable:** about 12 more hours of Claude's work once E1–E7 exist. That is 40 more checked places, a sixth kind, food open on Sundays and transport estimates.
- **Edinburgh or Manchester:** the cheapest next cities (D120: "London now, then UK cities"). The UK country items, UK weather and holidays are already done.
- **Every city "Listed":** reachable within weeks of the pull existing.
- **Every city Plannable:** not a sensible goal. Cities move up a level when people travel there, and freshness re-checks then become ongoing work.

## 7. What to do next, and in what order

1. **The lunch fix (E7).** Your approval is needed, because it changes plans in the round's build. 2–3 h, and a Brain deploy only, with no app build.
2. **Decide the first expansion target.** I recommend Edinburgh (cheapest, UK basics done), then Seville to Plannable. Your friend's trip makes Seville's gaps concrete.
3. **E1–E6 on the branch, after the friends' round** (no commits to `main` once it starts, m198), unless you choose to move the round again.
4. **The Listed pull,** once E1 exists, so new cities start with everything open data knows.

All of this is proposed. Under the after-9-Nov rule (D75) it is reviewed at Checkpoint 3, unless you decide otherwise.

## Sources (read 21 Nov 2026)

**Places data:**
- Overture Places guide, updated 18 Nov 2026: https://docs.overturemaps.org/guides/places
- Foursquare OS Places schema: https://docs.foursquare.com/data-products/docs/places-os-data-schema
- Foursquare, "Evolving FSQ Open Source Places" (8 Oct 2025): https://foursquare.com/resources/blog/data/evolving-fsq-open-source-places/
- OpenStreetMap copyright: https://www.openstreetmap.org/copyright
- OpenStreetMap `opening_hours` tag: https://wiki.openstreetmap.org/wiki/Key:opening_hours

**Google and Apple:**
- Google Places API policies: https://developers.google.com/maps/documentation/places/web-service/policies
- Google Maps Platform pricing (Places API (New) table): https://developers.google.com/maps/billing-and-pricing/pricing
- Google Service Specific Terms, archived versions only (the non-Google map clause is **UNVERIFIED** in the current version): https://cloud.google.com/archive/maps-platform/terms/maps-service-terms-20250501
- Apple Maps Terms of Use (databases): https://www.apple.com/legal/internet-services/maps/terms-en.html
- Apple Maps Server API (daily quota): https://developer.apple.com/documentation/applemapsserverapi

**Transit, holidays and weather:**
- Transitous: https://transitous.org/doc/ and https://github.com/public-transport/transitous
- MOTIS: https://github.com/motis-project/motis
- Nager.Date, now Nager.Holidays: about 210 countries; **commercial use needs sponsorship** under its terms of 15 Sep 2023, so ODYS takes holidays from each government instead. https://nagerholidays.com/legal/termsofservice
- Open-Meteo: free only for non-commercial use, under 10,000 calls a day, with data under CC BY 4.0. https://open-meteo.com/en/terms and https://open-meteo.com/en/pricing
