# A structured experience catalogue for any destination (10 Nov 2026; m235)

**Decision: built on the branch, not yet used by the planner.**
- Every experience is now one record: **a common core every kind shares, plus one facet** with what only that kind has. A museum, a beach, a market, a shopping street and a river bus each fit without being forced into one flat shape.
- **All 49 ready London cards convert,** each with a global ID and every fact labelled with where it came from.
- **The code no longer lists card IDs:** the shopping set comes from the catalogue's category.
- **Plans are unchanged,** and the cards stay the source of their own facts.

`brain/src/brain/catalogue.py`, `brain/data/catalogue/london.yaml`, `brain/tests/test_catalogue.py` (11 tests).

## The model

| Abram's field | In the record | For the London cards |
|---|---|---|
| **Unique global ID** | `xp:<country>:<locality>:<slug>` (`xp:gb:london:burlington-arcade`). The card's own ID stays as a legacy ID; the place underneath keeps its ID (`odys:m_…`, `osm:node/…`, places.py) | All 49 unique |
| **Country and geographical hierarchy** | Country (ISO 3166-1), region (ISO 3166-2), locality (the destination registry's key), area (a neighbourhood), from `data/destinations.yaml` | GB, GB-ENG, london. **Area for 28 of 49**, only where the card's own title or place name gives one (`claimed`); otherwise unknown, never guessed from coordinates |
| **Coordinates** | WGS84 latitude and longitude, plus the locality's IANA time zone | All 49, inside Greater London (tested) |
| **Experience category and type** | ODYS's own taxonomy (`catalogue.TAXONOMY`): 9 categories, each with its types. Includes `beach`, `entertainment` and `guided_tour`, which London's cards don't use yet | 8 categories used. Assigned by Claude on 10 Nov, **for Abram to check** (`london.yaml`) |
| **Estimated duration** | Minimum and maximum, plus the way in and the usual queue | All 49 |
| **Opening hours** | The source's own text, plus a weekly table where the text is plain (`parse_hours`). A "closed …" list of dates is an exception. Seasonal, dusk-dependent and vague hours ("about 16:00") **stay as text**, and nothing is assumed | **25 of 49 parsed.** 24 stay as text: parks at dusk, seasonal roof gardens, "restaurants' own hours". Every parsed table agrees with the days the planner uses (tested) |
| **Price and currency** | Amount, ISO 4217 currency, and kind (free, entry, ticket, food or hire). Never converted here (WS5 does display currency) | 35 free, 7 meals, 4 entries, 2 tickets, 1 hire. **Meals are ODYS's own estimate**, labelled `estimated`; the rest were read from the place's own site (`checked`) |
| **Indoor or outdoor** | indoor, outdoor or mixed | 26 outdoor, 19 indoor, 4 mixed. Taken from the card's outdoor tag and labelled `estimated` |
| **Accessibility, where verified** | Step-free access as a `Fact`. **Unknown unless a source says so** | **4 of 49 known** (all step-free). The other 45 are unknown, and the record says so. This is the biggest gap before any accessibility promise |
| **Transport requirements** | The nearest station or stop, the walk from it, whether the way in starts at public transport, and the booking the visit needs | 46 start at public transport; 3 timed bookings (Horizon 22, the Transport Museum, go-karting) |
| **Source and verification date** | Provenance: the card's source (research or founder), its checked date, and who assigned the category | All 49 dated |
| **Recommendation features** | The card's place and moment tags (0–2), unchanged | All 49 |
| **Photographs and attribution** | File, title, author, licence, licence URL and the source page. Only open licences (CC0, PD, CC BY, CC BY-SA) are allowed | 45 of 49. The other 4 keep the satellite view (as today) |

**Specialised facets** (one per experience):

| Facet | For | Its own attributes |
|---|---|---|
| Culture | museums, galleries, historic sites, performances | free entry, timed ticket, weekday only |
| Outdoor | nature and views | best weather, closes at dusk, the light line |
| Food | food and drink | how it's used (market, sit-down, counter, street), lunch only. **Never dietary claims:** those go through `food.py`'s evidence model |
| Shopping | arcades, markets, department stores | covered or not, open days |
| Activity | swimming, cycling, karting, tours | exertion, booking, hire |
| Area | neighbourhoods (D72's area vibes) | at most one a day, evening |
| Transport | river buses, boat trips, cable cars | direction, day or night variant |
| Beach | coasts and lakes (none in London) | swimming allowed, lifeguard season, water quality: each a `Fact` and unknown until a source says |

**How sure each fact is** (`places.Fact`): `checked` (at a named source, with a date), `claimed` (a source says so, unchecked), `estimated` (ODYS's own estimate; **new in m235**, for meal prices and the indoor/outdoor setting) or `unknown`.

## How a new destination fills it (no mass imports)

- **Places come from sources; experiences are written and checked.** An OpenStreetMap or Overture import creates *place* records (`places.PlaceRecord`), never experiences. An experience is written per city, like the London cards, and points to its place.
- So a new city's catalogue grows card by card, each checked from official sources (D91), as Abram asked: **no mass import of unverified places**.
- Before a city opens, every field in the table above is filled or marked unknown. `Experience.problems()` names anything that breaks the rules.

## Checks (`test_catalogue.py`, 11 tests)

- **Every ready card converts, one to one.** IDs are unique and global, with no rule broken.
- **Geography:** it comes from the registry, and areas come only from the cards' own words.
- **Facets:** each kind gets its own. Food facets hold no diet field, and a booking is shown where the card needs one.
- **A synthetic beach** in country `ZZ`, priced in `XTS`, fits the same model. These are the ISO codes reserved for user assignment and testing, so the record can't pass for a real place or price. A wrong type is refused.
- **Hours** are parsed only where the text is plain; unreadable hours stay as text. Parsed tables agree with the planner's days.
- **Prices** keep their currency and say how sure they are.
- **Access and setting** are never guessed.
- **Photos** carry their credit and an open licence.
- **No module lists card IDs,** except `api.py`'s Test A and Test B settings, which are frozen with the experiment.
- **The kinds-of-places caption** names the example photo's real city, from the catalogue (Abram's condition, m234).

## Next (each with the second destination; GUESS hours)

| Step | Hours |
|---|---|
| Abram checks the 49 category, type and area assignments | Abram ~0.5 h |
| Step-free access checked for the 45 unknown cards (each place's own access page) | Claude ~4 h |
| The planner reads hours from the weekly table where there is one (closed days and late openings, after-9-Nov #7) | Claude ~3 h, with the planner benchmark |
| A second city's cards written into the same model (WS2) | ~1 h a card |

**Hours this step:** Claude ~3 h.
