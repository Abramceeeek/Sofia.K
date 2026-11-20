# Destination intelligence: understanding a place before recommending in it (10 Nov 2026; m236)

**Decision: built on the branch.** No API is bought, no network is called, and the planner is unchanged.
- **A destination profile** holds Abram's parts: geography, areas, travel between them, experiences, seasons, holidays and places to stay. **Emergency numbers** are added as an eighth.
- **Providers fill the parts behind one interface,** so OpenStreetMap, Wikidata, a GTFS router or a paid service each becomes one more provider, never a rewrite.
- **A part nobody supplies is missing, and said.** A destination isn't offered until its experiences, travel, holidays and emergency numbers are there and checked.

`brain/src/brain/destination.py`, `brain/data/emergency.yaml`, `brain/tests/test_destination.py` (5 tests). The test destination is the synthetic **Testville** (`tests/fixtures/destination_testville.yaml`). Its country `ZZ` and currency `XTS` are ISO codes reserved for testing, so it can't pass for a real place.

## What a profile holds, and where each part comes from today

| Part (Abram's "a user enters Kyoto") | London today | Testville (synthetic) | A real second city would use |
|---|---|---|---|
| **Geography** | The registry: GB, GB-ENG, Europe/London, GBP | The fixture: ZZ, Etc/GMT-9 (UTC+9), XTS | The registry entry |
| **Areas** (neighbourhoods) | **23 areas, only the ones the cards' own titles name** (Greenwich, Soho, Canary Wharf…). Each centre is the mean of its experiences | 4 | OSM's suburb and neighbourhood boundaries, named by hand |
| **Travel between areas** | The planner's London estimate (walk under 20 min, else transit; GUESS parameters, `estimated`). TfL's measured times are used by the planner where it has them | A made-up tram network | GTFS feeds through a router (OpenTripPlanner), or the estimate with the city's own parameters until then |
| **Experiences** | The checked catalogue (m235): 49 | 6, including a beach with its own facet | Cards written and checked per city (m235), never a mass import |
| **Seasons** | **None checked: missing, and said** | 2 synthetic notes (blossom, heat) | The city's official tourism pages, by hand, each note dated |
| **Holidays** | GOV.UK's bank holidays (already in use) | 2 synthetic | Each government's own page, by hand, as for school holidays (m225) |
| **Places to stay** | The labelled sample results (trips.py), grouped by area | 6 sample points: Station Quarter 3, Old Town 2, Riverside 1 | The stays provider's own results (LiteAPI when live) |
| **Emergency numbers** | GB: 999, NHS 111, Samaritans, each with its official source | **Not checked: missing**, so not ready | `emergency.yaml`, one country at a time |

`Profile` gives:
- each area's experiences by category;
- minutes and mode between every pair of areas;
- where the places to stay are;
- the season notes for a month;
- **`readiness()`**: what's missing, and what's only estimated or sample.

London is ready, and reads "seasons missing; travel estimated; stays are samples". Testville is **not** ready: no emergency numbers.

## Emergency numbers, per country (Abram, m234; read 10 Nov 2026 from official pages)

| Country | Numbers | Source |
|---|---|---|
| UK | 999; 111 (NHS, "ask for an interpreter"); 116 123 (Samaritans, free, day or night) | nhs.uk (both pages are past their own review dates: Feb 2026, Nov 2025), samaritans.org |
| France | 112 (EU); 15 SAMU; 17 police or gendarmerie; 18 fire; 114 deaf or hard of hearing (text, app, online) | service-public.gouv.fr (updated 18 Oct 2024), European Commission (updated 5 Nov 2026) |
| Netherlands | 112 emergency; 0900-8844 police, not urgent | politie.nl |
| Belgium | 112 ambulance and fire; 101 police | securitecivile.be (police.be refused automated reading, 403) |

- **The offline pack now shows the trip's own country's numbers**, each with its source and date (`offline.emergency_items`).
- **A country ODYS hasn't checked** gets "ODYS hasn't checked the emergency numbers for … yet. Find the local emergency number before you go." It never gets another country's numbers.
- **In both apps** the offline section now reads **"Emergency help in the UK"**, since trips are London-only today.

## Providers compared

Sources were read on **10 Nov 2026** unless marked 7 Nov (`decisions/global-place-data.md`, which has the full places table).

**Places and identity:**

| Provider | Gives | Cost | Licence and limits |
|---|---|---|---|
| OpenStreetMap, via self-hosted or paid Overpass (7 Nov) | Places, tags, hours claims, district boundaries | Free data | ODbL, with attribution. The public Overpass instance says commercial use should be self-hosted or paid |
| Wikidata (7 Nov) | Identity, official websites, coordinates | Free | CC0. The query service is limited to 60 s of processing a minute |
| Overture Maps (7 Nov) | Existence, categories, stable IDs; no opening hours | Free | CDLA Permissive 2.0 or Apache 2.0, by source |
| Google Places (7 Nov) | Live details, ratings, photos | $5–$25 per 1,000 after the free monthly caps | **Only place IDs may be kept**; coordinates up to 30 days |
| GeoNames (7 Nov) | Towns and administrative areas | Free | CC BY |

**Districts:**

| Provider | Gives | Cost | Licence and limits |
|---|---|---|---|
| Who's On First | Neighbourhood and locality boundaries | Not stated | **Per-source licences** (about 312 sources). "Crediting Who's On First is recommended and linking back to the License is required." The page was generated on 21 Feb 2020 |
| Wikivoyage | District guides, as text | Free | **CC BY-SA 4.0**: attribution and share-alike. Our cards' own text stays ours, so it isn't copied in |

**Travel times:**

| Provider | Gives | Cost | Licence and limits |
|---|---|---|---|
| Mobility Database | GTFS, GTFS Realtime and GBFS feeds: "over 6000" in "over 99 countries" | "free access" | The data licence isn't stated on the page; each feed has its own (UNVERIFIED) |
| Transitland | Feeds, a REST API, routing | **Free tiers exclude commercial use.** Pay as you go: 10,000 REST requests a month free, then **$1.50 per 1,000**. Routing: **$2 per 1,000** (street) to **$8 per 1,000** (matrix) | The page states no data licence |
| OpenTripPlanner | Multimodal journeys from OSM and GTFS, self-hosted | Free software | The licence isn't stated on its page (UNVERIFIED) |
| OSRM | Road, bike and walking routes from OSM | Free software | **2-clause BSD** |
| Google Routes | Routes and matrices | Compute Routes or Matrix Essentials: **$5 per 1,000** after 10,000 free a month. Pro: **$10 per 1,000** after 5,000 free | Google's terms |

**Seasons and holidays:**

| Provider | Gives | Cost | Licence and limits |
|---|---|---|---|
| Open-Meteo | Weather and climate data | **Free for non-commercial use only** (under 10,000 calls a day). Commercial plans of 1M, 5M and 50M+ calls a month; prices not shown on the page | Data under **CC BY 4.0**, with attribution |
| Nager.Date | Public holidays | — | The page redirected to another host, which wasn't followed: **UNVERIFIED** |

**Recommendation (no purchase now).**
1. **Places:** a checked OSM and Wikidata extract per city (self-hosted Overpass), with Overture optional.
2. **Districts:** OSM boundaries, named by hand.
3. **Travel:** GTFS through a self-hosted OpenTripPlanner, the open route. Until then, the estimate with the city's parameters, labelled `estimated`.
4. **Seasons and holidays:** official pages by hand, as with school holidays.
5. **Google** only for live, per-request details, if Abram ever pays.

**Money decisions for Abram, none needed now:**
- Overpass hosting;
- a commercial Open-Meteo plan, if weather is used outside the UK (the Met Office covers London);
- Transitland pay-as-you-go, versus hosting OpenTripPlanner ourselves.

## Checks (`test_destination.py`, 5 tests)

- **London** is understood from its checked catalogue: 23 areas named by the cards, GOV.UK holidays, an area matrix (near before far), "seasons missing", and the estimate and samples named.
- **Testville,** from another provider, fills the same profile:
  - experiences by area;
  - a beach whose lifeguard season stays unknown;
  - a museum closed on Mondays;
  - season notes by month;
  - only the holidays in the dates asked;
  - places to stay by area.

  It is **not ready** without emergency numbers.
- **The first provider with a part wins,** and is named.
- **Each country's numbers** have an official source and a date.
- **The offline pack shows the trip's own country's numbers,** never another's.

## Next (GUESS hours)

| Step | Hours |
|---|---|
| A second city's profile: areas, travel parameters, holidays, emergency numbers, 20–30 checked cards | Claude ~20–30 h; Abram's card review ~2 h |
| GTFS and OpenTripPlanner as a travel provider, self-hosted | Claude ~6 h, plus a small server (money: Abram) |
| Season notes for London from official sources | Claude ~1 h |
| The apps read `emergency.yaml` for a trip outside the UK | ~2 h, both apps, with the second city |

**Hours this step:** Claude ~3.5 h (the research, the model, the providers, the tests and this page).
