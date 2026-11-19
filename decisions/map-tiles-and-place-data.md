# Android map tiles, and a three-layer catalogue: what the data providers allow and cost (16 Nov 2026)

Abram's review of the audit, parts 7 and 8 (12 Nov). This is research only: nothing is bought, no provider is chosen and nothing is imported. Paris stays a development destination and the portability benchmark. All provider terms were read on 12 Nov 2026 (sources at the end); UNVERIFIED marks what wasn't confirmed from a primary page.

## Part 1. Android map tiles (a release blocker: SEC-20)

**Today:**
- `android/app/src/main/java/com/odys/app/Map.kt` draws tiles from `tile.openstreetmap.org`, with a proper User-Agent.
- The OSM Foundation's tile policy says "Offline use is not permitted", bans bulk download and "prefetch features", and warns commercial services that "access may be withdrawn at any point".
- So it is fine for a test and not for a release.
- The iPhone uses Apple's MapKit, which has no such issue.

**Recommendation:**
1. **Now, at no cost:** OpenFreeMap tiles drawn by MapLibre Native.
   - **OpenFreeMap:** "Is commercial usage allowed? Yes." No key and no request limit. Offline saving is allowed in small pieces: each download "at most 3,000 tiles or 50 MB", at most 4 requests in parallel, and a unique User-Agent.
   - **MapLibre Native Android:** BSD 2-Clause.
   - This replaces the hand-drawn tile grid with a real map view (about 6 h, with the screen renders).
   - **The risk:** OpenFreeMap is donation-funded with no SLA, and it may stop "at any time without notice".
2. **The fallback, built when the first city's offline pack is designed:** our own PMTiles file, an OpenStreetMap extract for London, on Cloudflare R2.
   - **Cost:** R2 storage is $0.015 per GB-month with no egress charge, and the free tier covers 10 GB and 10 million reads a month. A city extract is tens to hundreds of MB, so about $0 to a few dollars a month (an estimate from R2's prices, not a Protomaps figure).
   - **What it gives:** full control of offline packs, and no third party to withdraw.
   - **Licence:** ODbL attribution ("© OpenStreetMap contributors"). Protomaps' own statement was read only in a search snippet: UNVERIFIED.
   - **Effort:** about 6 h to build and host.
3. **If a paid vendor is wanted, Stadia Maps Starter at $20 a month** is the cheapest with an explicit offline right: "not to exceed 100MB cached at a time per device".

| Option | Cost | Commercial use | Offline on the phone | Why not first |
|---|---|---|---|---|
| **OpenFreeMap + MapLibre** | $0 | yes | yes, ≤3,000 tiles or 50 MB per download | no SLA |
| **Own PMTiles on R2** | ~$0–few $/month | yes (ODbL) | yes, ours to package | more to build and run |
| Stadia Starter | $20/month | yes (not on the free tier) | ≤100 MB per device | money |
| Thunderforest Small Business | £195/month | yes | "may be cached … on-device for offline use" | cost |
| Mapbox | 25,000 monthly users free, then $4 per 1,000 | yes | offline regions, ≤750 tile packs | priced per user; its own SDK |
| MapTiler Flex | $30/month | yes (not on free) | "temporary personal cache" only; bulk download prohibited without a written agreement | no offline save |
| Google Maps SDK | free to load | yes | **no**: "don't pre-fetch … store … Google Maps Content" | no offline; its own styling |
| tile.openstreetmap.org (today) | $0 | withdrawable | **banned** | the blocker |

**Attribution, whichever is chosen:** "© OpenStreetMap contributors" always shown, plus the provider's own line. The privacy notice names the map provider: it names OpenStreetMap today and must change with it (both apps; Abram approves the wording).

## Part 2. A three-layer catalogue

Abram's three layers map onto what already exists:

| Layer | What it is | In ODYS today | What's missing |
|---|---|---|---|
| **1. Broad destination data** | Every place that exists: names, points, categories, websites, sometimes hours | **Nothing.** Each card starts from a person | A legally storable bulk source |
| **2. Verified experience records** | The facts ODYS stands behind: hours, prices, access, area, season, each with its source and date | **Built:** `catalogue.py`'s `Experience` with `Fact` provenance (checked / claimed / estimated / unknown; m235, m245); readiness rules (m263); material gaps ranked (m269) | Scale: verification is by hand, per fact |
| **3. ODYS moments** | The approach, the reveal, the best time, the shot card, the features for personalisation | **Built:** the moment cards (49 ready in London, 19 in Paris) | The founder's hours per card |

**The flow at scale:**
1. Layer 1 offers candidates in an area.
2. A candidate becomes a Layer 2 record only when its facts are read from an official source and dated.
3. A Layer 2 record becomes a moment only when someone writes the moment.

Layer 1 never reaches a plan on its own. That keeps Abram's rule: no city "supported" that ODYS doesn't understand.

### What Layer 1 can be built from (licence and cost)

| Source | What it gives | May we store it? | Cost | Fit |
|---|---|---|---|---|
| **Overture Maps Places** | names, points, addresses, phones, websites, categories, a confidence score; monthly releases; no photos, ratings or hours | **Yes.** CDLA Permissive 2.0 and Apache 2.0; "contains no OpenStreetMap data and carries none of the share-alike obligations of the ODbL" | free (bulk files) | **the base for Layer 1** |
| Foursquare OS Places | the same kind of points (one of Overture's sources) | yes (Apache 2.0) | free | only if its categories are needed |
| **OpenStreetMap** | points, **opening hours, wheelchair access**, many tags | yes, but **ODbL share-alike**: a database built on it may only be shared under the same licence | free | for hours and access hints, **kept in its own table**, joined by id, never merged into ODYS's own records. Where that line falls is a question for a solicitor before release |
| **Wikidata** | ids, coordinates, links, official websites | yes (CC0) | free | links each place to its official site, which is where Layer 2 checks happen |
| Wikivoyage | guide text | share-alike (CC BY-SA 4.0) | free | link to it, don't copy |
| **Viator affiliate API** | bookable tours and activities, with photos and reviews | yes: its docs expect a stored local catalogue | free to join; commission on bookings | Layer 1 for **bookable** experiences, later (a commercial step: Abram) |
| Geoapify | an API over OSM data | yes, with OSM attribution (still ODbL) | free 3,000 a day; from $59/month | convenience only, not a licence escape |
| Google Places | rich places, photos, ratings | **no**: only place ids may be kept | $5–$40 per 1,000 calls | ruled out for storage |
| Tripadvisor | ratings, reviews | **no**: "storing or indexing content is not permitted", except the location id | not published | ruled out |
| Yelp | businesses, reviews | display licence; caching terms not read (UNVERIFIED) | from $229/month | ruled out on cost |

**The financial picture:**
- **Layer 1:** free in data (Overture, Wikidata, OSM). It needs storage (small) and a nightly or monthly job.
- **The real cost is Layer 2:** the hours to read and date each fact.
  - The project's own rate: 32 cards' step-free facts are estimated at about 4 h (`recommendation-honesty-and-learning.md`), about 7–8 minutes a fact. That is a GUESS until measured.
  - At around 5 facts per experience (hours, price, access, area, season), a city of 100 verified experiences is roughly 60 h by hand.
  - That is why Layer 1 must narrow the candidates, and why Layer 2 checks should be **re-checks on a schedule** (readiness's review dates, m263), not one-offs.
- **Layer 3:** moments are written, by Abram or by research under D91. It stays the slowest layer and the reason ODYS is different.

### Proposed next step (a measurement, not an import; for Abram's approval)

**A one-borough trial, read-only, on a laptop:**
1. Take Overture Places for Westminster and the City.
2. Match them against the 49 London cards: same place within 50 m and a similar name.
3. Measure three things:
   - how many cards Overture finds;
   - how many of the m269 gaps OSM's tags would point to (for example, hours present in OSM for a card whose hours are unknown);
   - how much official-site linking Wikidata gives.
4. Run the same for Paris's 19, as the portability benchmark.
5. Report the counts only. Nothing goes into the catalogue or a plan.

- **Effort:** about 4 h. **Cost:** £0.
- **No provider commitment:** Overture's licence asks nothing of us until we publish data.

## Sources (read 12 Nov 2026)

**Map tiles:**
- https://operations.osmfoundation.org/policies/tiles/
- https://openfreemap.org/ and https://openfreemap.org/tos/
- https://raw.githubusercontent.com/maplibre/maplibre-native/main/LICENSE.md
- https://raw.githubusercontent.com/protomaps/PMTiles/main/README.md
- https://developers.cloudflare.com/r2/pricing/
- https://stadiamaps.com/pricing/ and https://stadiamaps.com/terms-of-service/
- https://www.thunderforest.com/pricing/ and https://www.thunderforest.com/terms/
- https://www.mapbox.com/pricing and https://docs.mapbox.com/android/maps/guides/offline/
- https://www.maptiler.com/cloud/pricing/ and https://www.maptiler.com/cloud/terms/
- https://developers.google.com/maps/billing-and-pricing/pricing and https://developers.google.com/maps/documentation/android-sdk/policies

**Place data:**
- https://docs.overturemaps.org/guides/places/ and https://docs.overturemaps.org/attribution/
- https://docs.foursquare.com/data-products/docs/places-os-data-schema
- https://www.openstreetmap.org/copyright and https://opendatacommons.org/licenses/odbl/summary/
- https://www.wikidata.org/wiki/Wikidata:Licensing
- https://en.wikivoyage.org/wiki/Wikivoyage:Copyleft
- https://partnerresources.viator.com/travel-commerce/affiliate/ and https://docs.viator.com/partner-api/technical/
- https://www.geoapify.com/pricing/
- https://docs.terra.tripadvisor.com/docs/caching-policy
- https://business.yelp.com/data/products/fusion/

**UNVERIFIED:**
- Protomaps' ODbL statement and hosting guidance (search snippets only);
- MapLibre Native's latest version and maintenance figures (GitHub was not reachable in that session);
- Yelp's caching terms;
- Carto's offline rules;
- the hours-per-fact rate (a GUESS).
