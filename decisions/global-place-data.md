# Global place data: from London cards to any destination (WS1, 7 Nov 2026; m207)

**Decision (proposed; the money and legal parts are Abram's).**
- **The moment stays ours.** The hand-checked experience, its way in and its best time are what no source supplies, and they are ODYS's difference. Outside sources only supply the *place* underneath it: that it exists, where it is, its hours, its access and what it claims about food.
- **Base the place layer on open data:**
  - OpenStreetMap, for places and their tags;
  - Wikidata, for identity and official links;
  - optionally Overture Maps, for existence and stable IDs.
- **Store each fact with its source and date.** Every fact is either checked, claimed (the source says so but nobody checked) or unknown.
- **Google Places is for live lookups only, if Abram pays for them.** It can't be our database: apart from place IDs, its content can't be kept.
- **A destination is offered only when its cards, travel times and hours are checked** (product-direction.md, E).
- **Built now, non-breaking:**
  - a destination registry (`brain/data/destinations.yaml`);
  - one place-record shape for any source (`brain/src/brain/places.py`);
  - adapters for the London cards and for an OpenStreetMap element;
  - tests.

  The planner and the 49 London cards are untouched, and their IDs are unchanged.

## 1. Where London is assumed today (audit of `brain/`, 7 Nov)

| Area | Where | The assumption | What another place needs | Severity |
|---|---|---|---|---|
| **Moment cards** | `data/moments/*.yaml` (49 ready), stored whole as JSON in the `moments` table (`db.MomentRow`) | All in London; ids like `m_bm_great_court` are unique only among London cards | Namespaced ids for new cities (below); existing ids stay. Adding fields needs **no database migration** (the record is JSON, validated by `Moment`) | Low |
| **Categories** | None on cards; the shopping cards are listed by id in `triplength.py`; `data/categories.yaml` is the visitors' kinds of place, each with a London example | No category field | A category on every card (product-direction.md, debt). The record has it as an explicit unknown until then | Medium |
| **Location and travel** | `travel.LondonEstimate` (walk 4.5 km/h × 1.35 detour; transit 18 km/h + 15 min access; GUESSES); `tfl.py`; `data/arrivals.yaml`, `tripdays.py` (London airports and stations; "Drive into London") | London's network | A travel provider per destination (`travel` in the registry); the estimate's parameters per city; arrivals per city | High, for the next city |
| **Opening hours** | `best_time.time_of_day` windows, `best_time.days`, `opening_hours` (free text with source and date), `hours` (for the person) | One set of hours for every open day; no seasonal or holiday closures (after-9-Nov #7) | Structured hours per weekday, with exceptions, source and date. The record keeps the source's own text until parsed | Medium |
| **Duration** | approach + experience + queue | None | Nothing | — |
| **Prices** | `cost_gbp`; `Brief.budget_gbp`; lunch £15; TfL fares in `dayplan.py`; `_money` writes £ | GBP only. **The model's cost feature is per £10** (`cost_per_10gbp`, priors.yaml) | Prices in their own currency in the record. The model needs them in GBP at a **dated** rate (or a per-currency cost weight: a modelling decision). Never a silent conversion | High |
| **Time zones** | `ZoneInfo("Europe/London")` in `api.py` (3 places), `ops.py`, `weather.py`; `sun.sunset` defaults to London | Plans and "today" in London time | `Destination.zone` (in the registry). Swap at the second city; no behaviour changes for London | Medium |
| **Languages** | All copy and cards in English | English | `languages` in the registry; translated card text is later | Low now |
| **Weather and light** | Met Office for central London; sunset at London's coordinates | One point for London | `weather` per destination; `sun.sunset` at the destination's centre | Low |
| **Bank holidays** | Was a London-only map in `traveltiming.py` | — | **Done**: read from the registry now | — |
| **Destinations** | `schemas.py` `destination = "london"`; `api.py` refuses others (422, "London first…"); `airports.yaml` | London only | The registry; coverage `checked` before a destination is offered | By design |
| **Visitors' flow** | "Would you like to try it in London?"; examples are London cards | London | The destination's name and examples | Low |

## 2. The canonical model

| Entity | Key fields | ID | Exists today |
|---|---|---|---|
| **Country** | ISO 3166-1 code, name, currency, languages | `GB` | In the registry, as fields |
| **Region** | ISO 3166-2 code, or the GOV.UK division for bank holidays | `GB-ENG`; `england-and-wales` | As a field |
| **Destination** (a city or town) | key, name, country, region, time zone, currency, languages, centre, bank-holiday division, travel and weather providers, **coverage** (`checked` or `none`) | `london` | **Built** (`places.Destination`, `data/destinations.yaml`) |
| **Locality** (a neighbourhood) | name, destination, outline or centre | `london:soho` | Not yet: only when a plan needs it ("near Soho") |
| **Place** | namespaced id, name, point, category, opening hours, price, step-free access, diet claims, website, licence, attribution, `same_as` | `odys:m_…`, `osm:node/123`, `wikidata:Q6373`, `overture:<GERS id>` | **Built** (`places.PlaceRecord`) |
| **Fact** (one field of a place) | value, trust (`checked` / `claimed` / `unknown`), source, date | — | **Built** (`places.Fact`) |
| **Experience** (the moment) | the place's id, the approach, what happens, best time, features, shot card | the card id, unchanged | The moment card. It becomes "an experience at a place" once cards point to place records (`place.overture_id` exists, unused) |
| **Category** | ODYS's own short list, mapped from OSM tags and Overture's `basic_category` | `museum`, `park`… | Not yet: the next step |
| **Venue** | a place with commercial hours and prices (restaurants, shops): the same record | — | The same `PlaceRecord` |
| **Opening hours** | per weekday intervals, exceptions (holidays, seasons), source, date | — | Text with source today; structure is a later step |
| **Price** | amount, currency, kind (entry, ticket, food, hire, free), per adult or child, source, date | — | **Built** (`places.Price`, inside a `Fact`) |
| **Travel connection** | from, to, minutes, mode, route, source, fetched | the pair of points | The `travel_times` table (TfL), London only |

**Two layers, kept apart.**
- **The moments** are ours: checked by us or by Abram, under our own terms.
- **The places** come from sources, each with its own licence.

They're joined only by a place's ID. That keeps attribution and share-alike obligations attached to the source's data (section 4), and it means a source can change without touching a moment.

## 3. Sources compared (read 7 Nov 2026)

Quality and coverage are **not measured here** (UNVERIFIED for any city). The test for each city is a sample: 50 places checked against their official sites, before that city's coverage is set to `checked`.

| Source | What it gives | Cost | Licence and attribution | Keeping data | Limits | Updates |
|---|---|---|---|---|---|---|
| **OpenStreetMap** (data) | Places as nodes and ways with tags: name, `opening_hours`, `wheelchair`, `diet:halal`, `diet:vegetarian`, `website`, `wikidata`, `fee` | Free | **ODbL**: "Provide credit to OpenStreetMap by displaying our attribution notice" and "Make clear that the data is available under the Open Database License" ([copyright](https://www.openstreetmap.org/copyright)). Commercial use is allowed. Credit goes on public produced works. A derived database carries share-alike ([OSMF attribution](https://osmfoundation.org/wiki/Attribution)) | Yes (it's open data), under ODbL | — | Continuous (community edits) |
| **Overpass API** (public instance, to query OSM) | OSM elements by area and tag, as JSON | Free | As OSM | Yes | "less than 10,000 queries per day and … less than 1 GB data per day"; "for regular use … divide those numbers by 100"; **"Commercial use should use self-hosted or paid Overpass servers"** ([wiki](https://wiki.openstreetmap.org/wiki/Overpass_API)) | Minutes behind OSM |
| **Nominatim** (OSM geocoding) | Search by name and address | Free | ODbL, attribution | "Results **must be cached**" | "absolute maximum of 1 request per second"; no autocomplete; commercial apps pointed to other providers ([policy](https://operations.osmfoundation.org/policies/nominatim/)) | As OSM |
| **OSM tiles** (the Android map today) | Map images | Free, best effort | "© OpenStreetMap contributors", bottom right | Cache ≥ 7 days or per headers | Named User-Agent required (generic library ones "will be blocked"); offline download prohibited; "Commercial services … should be especially aware that access may be withdrawn at any point"; "no SLA" ([tile policy](https://operations.osmfoundation.org/policies/tiles/)) | — |
| **Wikidata** | Identity, official website, Wikipedia links, coordinates, IDs in other databases | Free | **CC0** for structured data ([licensing](https://www.wikidata.org/wiki/Wikidata:Licensing)) | Yes | Query service: 60 s per query; "60 seconds of processing time each 60 seconds" per client; 30 error queries a minute ([manual](https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual)); dumps for bulk | Continuous |
| **Overture Maps** (Places) | ~88 million places: names, `basic_category`, existence `confidence`, websites, phones, addresses, brand, sources; **no opening hours** mentioned | Free (S3 and Azure downloads) | **CDLA Permissive 2.0 and Apache 2.0, by source**; "does not include OpenStreetMap data" ([guide](https://docs.overturemaps.org/guides/places/)); Foursquare-sourced records are Apache 2.0 with its notice ([release notes, Sep 2025](https://docs.overturemaps.org/blog/2025/09/24/release-notes/)) | Yes | — | Monthly; taxonomy quarterly (`categories` replaced by `taxonomy` and `basic_category` from the September 2026 release) |
| **Foursquare Open Source Places** | Places with categories, closed dates, refresh dates | Free (account and token, Iceberg catalog) | The access page doesn't state the dataset's licence (UNVERIFIED; Overture says Apache 2.0 for its Foursquare records) ([access](https://docs.foursquare.com/data-products/docs/access-fsq-os-places), updated 31 Mar 2026) | Yes | — | Not stated |
| **Google Places API (New)** | Rich, current details: hours, ratings, photos, reviews | Per 1,000 after the free monthly cap: Place Details Essentials **$5** (10,000 free), Pro **$17** (5,000), Enterprise **$20** (1,000), Enterprise + Atmosphere **$25** (1,000); Text Search Pro and Nearby Search Pro **$32** (5,000) ([pricing](https://developers.google.com/maps/billing-and-pricing/pricing); no date on the page) | Google's terms; the Google Maps logo or "Google Maps" text; photo and review authors credited ([policies](https://developers.google.com/maps/documentation/places/web-service/policies)) | **Only place IDs indefinitely**; coordinates "up to 30 consecutive calendar days"; don't "copy and save business names, addresses, or user reviews" (same page) | Billing per call | Live |
| **GeoNames** | Place names, towns, administrative areas (not venues) | Free | **CC BY**: credit GeoNames; "commercial usage is allowed" ([export](https://www.geonames.org/export/)) | Yes (dumps) | Web service: 10,000 credits a day, 1,000 an hour per app | Dumps daily |

## 4. Strategy

1. **Per destination, a checked extract, not live calls.** For each new city, a one-off pull of its places from OSM, through a paid or self-hosted Overpass server (the public one is not for commercial use). Add Wikidata for identity and official websites, and optionally Overture for existence and GERS IDs. Each fact is stored with its source and fetch date; a refresh runs monthly. The app never calls these services per user.
2. **Moments are written per city, as in London,** and each points to a place record. The sources tell us that a place exists and what it claims. The card tells us why it's worth going.
3. **Unknown stays unknown.** A missing `wheelchair` tag is unknown, not "no". `diet:halal=yes` is a community **claim**, never "certified" (WS2). Hours from a source are claims until checked against the venue's own site.
4. **Licences are kept per record.** OSM-derived facts keep "© OpenStreetMap contributors" and ODbL wherever they're shown. They live in the place layer, apart from our own cards. Whether that separation is enough under ODbL's share-alike (a "collective" rather than a "derivative" database) is a **legal question before any public release**, not a design assumption.
5. **Google only for live, per-request details,** and only if Abram decides to pay: for example, today's hours on a stop when the person opens it. Store nothing but the place ID. Roughly, 1,000 stop openings a month fit the Pro free cap of 5,000, and each 1,000 after that costs $17.
6. **The Android map at public release** needs its own tile provider, a paid OSM-based one or self-hosted. The OSM servers give no guarantee, and access for commercial apps "may be withdrawn at any point". The app already sends a named User-Agent and shows the credit. This is a money decision for Abram before the public release, not during the tests.

## 5. Built now (non-breaking), and tested

- **`brain/data/destinations.yaml`:** London as a destination like any other: GB, England, Europe/London, GBP, en-GB, its centre, `england-and-wales`, coverage `checked`, TfL, Met Office. `traveltiming.DESTINATION_DIVISION` now reads from it, so no second destination list lives in the Brain.
- **`brain/src/brain/places.py`:**
  - `Destination`, `Fact` (`checked` / `claimed` / `unknown`), `Price`, `PlaceRecord` (with `unknowns()`) and the `PlaceProvider` protocol;
  - `from_card`: a London card becomes `odys:<card id>`, keeping its checked date and source;
  - `from_osm_element`: an Overpass JSON element; every tag is a claim, a missing tag is unknown, and the record carries ODbL and the credit.

  Nothing calls a network.
- **`brain/tests/test_places.py`** (4 tests), on a **synthetic** Overpass fixture (`tests/fixtures/overpass_sample.json`, marked as made up). The tests check:
  - London's fields;
  - every card maps one to one, with its ID unchanged and namespaced;
  - cards have no category, and say so;
  - a map tag is never "checked";
  - a restaurant tagged only `cuisine=turkish` gets **no** halal value;
  - IDs from two sources never collide.

## 6. Next steps (each when a second city is chosen, after the friends' round)

| Step | Hours (GUESS) |
|---|---|
| A category on every card, from a short ODYS list mapped to OSM and Overture | Claude ~2 h; Abram 0.25 h to check |
| Structured opening hours (per weekday, exceptions), parsed from the card text and OSM's `opening_hours` | Claude ~4 h |
| Prices in their own currency; the model's cost in GBP at a dated rate, or a per-currency cost weight | Claude ~2 h + Abram's choice of rate source |
| `Destination.zone` in place of the hard-coded Europe/London (api, weather, sun) | Claude ~1.5 h |
| A travel provider per destination (the estimate's parameters per city; a transit API where one exists) | Claude ~3 h per city |
| The first city's extract (Overpass, Wikidata), with the 50-place quality sample | Claude ~4 h + a paid or self-hosted Overpass (Abram, money) |

**Hours this step:** Claude ~3 h (the audit, the sources, the code and tests). Abram: the two money decisions (Overpass hosting, Android tiles) and the legal question in 4.4, none needed before the friends' round ends.
