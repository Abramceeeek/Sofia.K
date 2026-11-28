# Overture Maps places: a stratified sample of 50 from central London (28 Nov 2026, batch 9)

**Decision first.** Overture is good for **finding candidates and placing them**, not for knowing them.
- **Coordinates are good.** Where the record really is the same place, it sits a median 34 m from the card's own sourced point. 48 of 54 are within 150 m.
- **Category and existence are weak.**
  - Of 45 records in nine visitor categories, 15 are right, 7 are approximately right and 12 are wrong: not that kind of place, not a place at all, or junk.
  - Of 10 checked by search, 4 could not be found.
- **It says nothing ODYS matches on:** no experiences, appeals, atmosphere, opening hours, prices or access.
- **So:** an Overture record can only ever be an `inferred` candidate (a crowd label, `evidence-rules.md` §3). It reaches the engine after the controlled enrichment step, never by import. Nothing in this sample was added to the planner.

**How the sample was drawn, and how far it represents anything.**
- **Release:** `2026-11-18.0`, read from Overture's Azure mirror (`overturemapswestus2.blob.core.windows.net`). The S3 route is blocked here.
- **Area:** a central London box (−0.25 to 0.05 longitude, 51.45 to 51.57 latitude). That's 363,504 records, every status included.
- **Strata:** 10 strata of 5, picked in a fixed pseudo-random order (`hash(id ‖ 'odys-batch9')`):
  - nine visitor kinds ODYS plans with: museums, galleries, parks and gardens, restaurants, cafés, pubs and bars, historic sites, markets, shops;
  - one stratum from the whole file, to show the long tail.
- **What it doesn't represent:**
  - **It is not proportional.** The nine visitor kinds are about 5% of the file. The biggest categories are offices, IT companies and professional services.
  - **Five per stratum** gives each stratum's figure a wide margin. These are indications, not rates.
  - **One area and one release.** Outer London, other cities and later releases may differ.
- **Reproducible:** `overture/pull.py`, `overture/sample.py` and `overture/coords.py`, with the measured rows in `overture/sample.json` and `overture/coords.json`. The 363k-row extract isn't committed.
- **Who judged:**
  - **Category, existence and duplicates:** Claude's judgement from each record's name, category and address, with the web searches cited below. These are not verified facts.
  - **The automatic measures:** confidence, website, licence and the coordinate distances.

## 1. The measures, each on its own

| Measure | Result | How |
|---|---|---|
| **Existence** (10 records checked by web search) | **5 confirmed**, 1 under a name 9 years out of date, 4 not found | Searches on 28 Nov (§3). Existence is not the same as having a website |
| **Category accuracy** (45 records in the nine visitor strata) | **15 right, 7 approximately right, 12 wrong**, 3 closed or stale, 8 can't tell | Claude's reading of each record (§2) |
| **Coordinates** (against the cards' own sourced points, cards whose coordinates came from Overture left out) | Median **34 m**; 37 of 54 within 50 m, 48 within 150 m, 2 beyond 300 m | `coords.py`: the nearest Overture record within 1 km sharing at least half the name's words. The far ones are mostly a different record with a similar name (a bar called "B.Y.O.C. – Soho", a sportswear shop on Waterloo Bridge), not a misplaced point |
| **Duplicates** | 1 of 50 with a near-duplicate within 75 m (the Natural History Museum: 2 others). Elsewhere, "Windsor Castle" appears 6 times in the box: a castle 35 km away placed near Buckingham Palace, a "museum", a tour operator, a gift shop | Records within 75 m sharing at least 60% of the name's words |
| **Website availability** (a metric, not an existence test: Abram, m364) | 73% of the whole box; 36 of 50 in the sample (parks 2 of 5, historic sites 2 of 5) | The `websites` field. Parks and landmarks often have none, and a junk record can have one |
| **Operating status** | 8.4% of the box marked permanently closed; 2 of 50 in the sample | The `operating_status` field. Most records (40%) have no status at all |
| **Confidence score** | Mean 0.68. In the sample, the junk record "Mcbeuvb" is 0.21, but wrong records also score high ("North Cross Vintage Store" as a farmers' market: 0.95) | Overture's own `confidence`. Not a measure of category accuracy |
| **Enrichment potential** | Name, category (a crowd label), coordinates, address, website, phone, sources. **Nothing on what to do there or how it feels; no opening hours, prices or access** | The release's schema (no hours field) |
| **Licence** | Places is "published under the CDLA Permissive 2.0 and Apache 2.0 licenses, depending on the source", with "no OpenStreetMap data" (Overture's Places guide). In this box, 916,372 source entries are CDLA-Permissive-2.0 (Meta, Microsoft, BrightQuery and others), 24,423 Apache-2.0 (Foursquare) and 5,497 CC0-1.0 (AllThePlaces) | [docs.overturemaps.org/guides/places](https://docs.overturemaps.org/guides/places/) and [docs.overturemaps.org/attribution](https://docs.overturemaps.org/attribution/), read 28 Nov 2026; each record's `sources[].license` |
| **Attribution** | No single required string for Places. Some sources need their own notices (e.g. "Data from Meta. Available under CDLA Permissive 2.0."; Foursquare's Apache 2.0 copyright line). Joining Places to OSM "may need to carry the Open Database License (ODbL)" | The same pages. Part of the attribution page was read only as a summary: check the exact notices before any release. **Not legal advice** |
| **Effort to bring one place in** | About 25–45 min a place (GUESS: the seven reference places took about 3 h with the schema). Filtering junk is partly automatic (confidence, status, category); category errors need a person or a checked model | §4 |

## 2. The 50 records

`web` means the record has a website. Category and existence are Claude's judgements (§3 cites the searches).

| Stratum | Name (as in Overture) | Overture category | Conf. | Web | Claude's reading |
|---|---|---|---|---|---|
| museum | Windsor Castle | museum | 0.73 | ✔ | **Wrong.** Placed in Maida Vale with address "London": not the castle (Berkshire). Possibly a pub of that name |
| museum | Natural History Museum, London | history_museum | 1.00 | ✔ | Right (it is a natural history museum); 2 near-duplicates |
| museum | Museum Chambers | museum | 0.78 | – | **Wrong:** a building's name on Bury Place |
| museum | Archive Gallery | art_museum | 0.87 | ✔ | Can't tell (address "Gb") |
| museum | Museum Cafe | museum | 0.52 | ✔ | **Wrong:** a café |
| gallery | Peripheral Vision | art_gallery | 0.58 | ✔ | **Wrong:** at Four Corners' address; not found as a venue, probably an exhibition |
| gallery | Art Play Nights | art_gallery | 0.87 | ✔ | **Wrong:** an event's name |
| gallery | Creative Art & Design Centre | art_gallery | 0.50 | – | Closed (marked permanently closed) |
| gallery | Maxilla Studios | art_gallery | 0.70 | – | Approximately right: artists' studios with a gallery space (ACAVA) |
| gallery | Prints & Posters | art_gallery | 0.77 | ✔ | Approximately right: a print shop |
| park | Grafton Square | park | 1.00 | ✔ | Right (Lambeth's own page) |
| park | St John's Churchyard | park | 0.91 | – | Right: a churchyard garden |
| park | Bermondsey Spa Gardens | park | 0.94 | – | Right |
| park | Marble Arc | park | 0.73 | ✔ | **Wrong:** misspelt Marble Arch, a monument |
| park | Regents Park Gloucester Green | park | 0.73 | – | Right: part of Regent's Park |
| restaurant | Nasi Economy Rice | restaurant | 0.50 | – | Closed (marked permanently closed) |
| restaurant | Bite Bistro | restaurant | 0.82 | – | Not found |
| restaurant | Mamaput Kitchen Ltd. | restaurant | 0.97 | ✔ | Not found (marked open, confidence 0.97) |
| restaurant | Beit El Iraqi | restaurant | 0.73 | ✔ | Right: found as a delivery listing; address unconfirmed |
| restaurant | Giraffe | restaurant | 0.77 | ✔ | Can't tell |
| cafe | Bread & Butter cafe | cafe | 1.00 | ✔ | Plausible, unchecked |
| cafe | Coffee Bird | coffee_shop | 0.92 | ✔ | Not confirmed (one contradictory aggregator page) |
| cafe | Masala Zone | cafe | 0.97 | ✔ | Approximately right: an Indian restaurant, not a café |
| cafe | Highland Coffee @ Ct3 Linh Dam | coffee_shop | 0.62 | – | **Wrong:** a Hanoi address in its name, placed on Kingly Street |
| cafe | Coffee shop | coffee_shop | 0.68 | ✔ | Can't tell: a generic name |
| pub_bar | The Eagle | pub | 1.00 | ✔ | Plausible, unchecked |
| pub_bar | Tommy Flynns | pub | 0.85 | ✔ | **Stale:** renamed in 2017 (now the Clissold Park Tavern, CAMRA) |
| pub_bar | HIT KING | pub | 0.68 | – | Can't tell |
| pub_bar | Gordon Ramsay Bread Street Kitchen & BAR | bar | 0.97 | ✔ | Approximately right: the name doesn't match the Heddon Street address |
| pub_bar | The Terrace Bar | bar | 0.96 | ✔ | Plausible, unchecked |
| historic | Forbes House, Belgravia | historic_site | 0.77 | – | Plausible, but a private house: not visitable |
| historic | Metropolitan Borough of Camberwell | historic_site | 0.83 | – | **Wrong:** a former council area |
| historic | Notting Hill London UK | historic_site | 0.80 | ✔ | **Wrong:** a district |
| historic | Victory Plaza | historic_site | 0.61 | – | **Wrong:** a development |
| historic | Park Place London | historic_site | 0.58 | ✔ | Can't tell |
| market | Stoke Newington Green Fruit & Veg | market | 0.77 | ✔ | Approximately right: a greengrocer |
| market | Swiss Cottage Farmers' Market | farmers_market | 1.00 | ✔ | Right (London Farmers' Markets) |
| market | North Cross Vintage Store | farmers_market | 0.95 | ✔ | **Wrong:** a vintage shop |
| market | Strutton Ground Market | farmers_market | 0.83 | ✔ | Right: a street market |
| market | Stroud Green Market | farmers_market | 1.00 | ✔ | Right: a Sunday market (Islington's listings) |
| shop | Mcbeuvb | department_store | 0.21 | – | **Wrong:** junk |
| shop | Argos West Hampstead (Sainsbury's C&C) | department_store | 0.99 | ✔ | Approximately right |
| shop | Liberty Stores | department_store | 0.67 | ✔ | Right (Liberty; the name is a variant) |
| shop | TK Maxx | department_store | 0.77 | ✔ | Approximately right |
| shop | Marks & Spencer | department_store | 0.90 | ✔ | Right |
| any | Soulfresh Group Pty Ltd (uk) | distribution_service | 0.50 | ✔ | Not visitable: an office |
| any | Idn Chelsea Locksmith | key_and_locksmith | 0.95 | ✔ | Not visitable: a flat's address |
| any | French Embassy | embassy | 0.83 | ✔ | Not visitable |
| any | Photo Centre | professional_service | 0.78 | ✔ | Not visitable |
| any | The Blackstone Group International | financial_service | 0.77 | ✔ | Not visitable: an office |

## 3. The existence searches (28 Nov 2026)

| Record | Found | Source |
|---|---|---|
| Swiss Cottage Farmers' Market | ✔ Wednesdays on Eton Avenue, run by London Farmers' Markets | [lfm.org.uk/markets/swiss-cottage](https://lfm.org.uk/markets/swiss-cottage) |
| Stroud Green Market | ✔ Sundays, Stroud Green Primary School, Perth Road | [islingtonlife.london](https://islingtonlife.london/things-to-do/stroud-green-market) |
| Grafton Square | ✔ a Lambeth park | [lambeth.gov.uk/parks/grafton-square](https://www.lambeth.gov.uk/parks/grafton-square) |
| Maxilla Studios | ✔ ACAVA artists' studios, with Maxilla Space | [acava.org](https://www.acava.org/building/maxilla-walk-studios/) |
| Beit El Iraqi | ✔ a delivery listing in Marylebone; the street isn't confirmed | [deliveroo.co.uk](https://deliveroo.co.uk/menu/london/marylebone/beit-el-iraqi) |
| Tommy Flynns, 177 Green Lanes | The pub exists, renamed in 2017 (the Clissold Park Tavern) | [camra.org.uk/pubs/125033](https://camra.org.uk/pubs/125033) |
| Coffee Bird, Hoxton Street | ✗ one contradictory aggregator page only | [mimoji.com](https://mimoji.com/gb-en/listing/coffee-bird/207311) |
| Mamaput Kitchen, Middlesex Street | ✗ nothing found | search only |
| Bite Bistro, Clapham High Street | ✗ nothing found | search only |
| Peripheral Vision, 121 Roman Road | ✗ not found as a venue at that address | search only |

## 4. What this means for ODYS

1. **Use Overture to find and place candidates, never as knowledge.**
   - **A record enters as `inferred`:** its category is a crowd label, and its existence is unconfirmed.
   - **Before it can be planned, it needs:**
     - an official or reference source that it exists and is open;
     - its experiences, and their appeals from that source;
     - verified hours for any hard rule.
2. **Automatic filters help but aren't enough:**
   - **What they remove:** confidence under 0.5, "permanently closed", categories outside the visitor kinds, and a name that's an area or an event.
   - **What remains:** wrong categories (12 of 45 here) and records that can't be found (4 of 10). Those need a check against a real source.
3. **Coordinates can be reused once the entity is confirmed.** Name matching alone picks wrong records (3 of the 6 far matches).
4. **Licence:** permissive (CDLA Permissive 2.0, Apache 2.0, CC0), with per-source notices, and ODbL obligations only if joined with OSM. A licence check by Abram (or a solicitor) is needed before any release that shows Overture-derived data.
5. **Next step, if Abram approves:** a 20-place enrichment trial from Overture candidates in one area (about 8–15 h, GUESS). It would show the real time per place and the share that survive the checks. It isn't started.
