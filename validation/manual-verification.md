# Manual verification: the most-planned London places first (19 Nov 2026; m290)

**Abram's decision (19 Nov):**
- Verify the British Museum and the Royal Festival Hall by hand first.
- Do the same for the 20 most-recommended places before any rarely-seen one.
- "Do not guess when official websites refuse automated access."

**London stays Preview** until it meets the readiness bar. **Nothing here changes the frozen friends' round:** it runs on `80a0da3`'s cards whatever is checked now.

**Why these two:**
- In simulated personal plans, the Royal Festival Hall foyers appear in **40%** and the British Museum's Great Court in **32%** (`brain/data/popularity.yaml`).
- Both lack **hours read on an official page, step-free status and a named area**.
- Both official sites refuse automated reading (HTTP 403, again on 19 Nov).
- The full ranked list is `brain/benchmarks/coverage/material_gaps.md` ("the 20 most-planned places").

## How to verify (Abram, in a browser; about 15 minutes for both)

1. Open each page below, on the official site only. Not a search result, a listing site or a map app.
2. Copy the exact words into the template at the end. Don't summarise.
3. **If a page doesn't say, write "not stated".** That is a valid answer and is kept as unknown, never filled in.
4. If two official pages disagree, write both. Claude records the conflict and the planner stays on the safe side.
5. Send the filled template to Claude. Claude records each fact with its page and your reading date (`london_checked.yaml`, "read by Abram in a browser"), runs the tests, and regenerates the coverage files.

## 1. Royal Festival Hall foyers (`m_rfh_foyers_rest`, 40% of plans)

**What the catalogue holds now:**

| Field | Value | Where it came from |
|---|---|---|
| Hours | "Tue–Sun 10:00–23:00, closed Mondays. Foyers free" | Search results limited to the official site, 28 Sep. **No page was read** |
| Price | Free (the foyers) | The same |
| Step-free | **Unknown** | — |
| Area | **Unknown** | — |
| Location | 51.505768, −0.1168 (SE1 8XX postcode centre); Wikidata Q647390, 8 m away | postcodes.io, 28 Sep; Wikidata, 11 Nov |

**Official pages to read** (addresses found by a search of the official site on 19 Nov; each answers 403 to automated reading):
- Venue page, for hours and closures: https://www.southbankcentre.co.uk/venues/royal-festival-hall/
- Access page, for the step-free route and any lift notice: https://www.southbankcentre.co.uk/visit-us/access/
- Help centre, "What are your opening hours?": https://help.southbankcentre.co.uk/hc/en-us/articles/29566015413405-What-are-your-opening-hours

**What official documents Claude *could* read say** (Southbank Centre's own "Facilities and access" PDFs on its document host, read 19 Nov). **They carry no date, so they are leads, not facts:**
- "Royal Festival Hall: Open 10am – 11pm every day except Christmas Day."
  - **This conflicts with the card's "closed Mondays".** It's the first thing to settle.
- "Occasionally Royal Festival Hall is closed to the public due to private hire. We publicise these times across the site and online."
- A step-free route to the Level 2 foyers by the JCB Glass Lift, and help at the Level 2 Welcome Desk (Green Side). Accessible toilets on every level.
- Sources:
  - https://bynder.southbankcentre.co.uk/m/26311cdf45a43b51/original/Southbank_Centre_Facilities_and_Access.pdf
  - https://bynder.southbankcentre.co.uk/m/07ab44566bb9c45b/original/Southbank_Centre_Facilities_-_access.pdf
  - https://bynder.southbankcentre.co.uk/m/3c8ab8474f688cdc/original/Southbank_Centre_Facilities_-_access-.pdf

**What search results say (UNVERIFIED; snippets, not pages read; 19 Nov):**
- the venue page: "Tuesday – Sunday, 10am – 11pm. Monday, closed";
- the access page: "The Royal Festival Hall lifts are being refurbished, and some are temporarily out of service";
- a closure "on Tuesday 17 November".

**Fields to verify:**
1. **Opening days and hours of the building and its foyers.** Open on Mondays, or closed?
2. **Where closures for private hire are announced**, so a plan can be checked.
3. **Step-free:** is there step-free entry to the foyers? Write yes, partial (for example, "only by one lift" or "some lifts out of service") or no, with the sentence that says so. Also any lift notice and its date.
4. **Area:** the address or area exactly as printed on the official page.

**Until it's verified:** the card keeps "closed Mondays". That's the safe side: a plan never sends anyone there on a day it might be shut.

## 2. British Museum: Room 4, the Great Court, Room 1 (`m_bm_great_court`, 32% of plans)

**What the catalogue holds now:**

| Field | Value | Where it came from |
|---|---|---|
| Hours | "Daily 10:00–17:00, Fridays to 20:30. Free" (last entry 16:45) | Search results, 26 Sep (britishmuseum.org refused the fetch). **No page was read** |
| Price | Free | The same |
| Route inside | Room 4 (Egyptian sculpture, west) → Great Court → Room 1 (Enlightenment, east) | The museum's map PDF (May 2026), read 26 Sep; Abram's own visit |
| Step-free | **Unknown** | — |
| Area | **Unknown** | — |
| Location | 51.51931, −0.12671; Wikidata Q6373, 22 m away | OpenStreetMap; Wikidata, 11 Nov |

**Official pages to read** (found by a search of the official site on 19 Nov; both answer 403 to automated reading):
- Visit page, for hours, last entry, closures and the two entrances: https://www.britishmuseum.org/visit
- Accessibility page, for step-free entry: https://www.britishmuseum.org/visit/accessibility-museum

**What the official map Claude *could* read says** ("British Museum map", © 2026, marked 03/2026, file updated 20 May 2026; read 19 Nov, https://www.britishmuseum.org/sites/default/files/2026-05/British_Museum_map.pdf):
- Room 4, the Great Court and Room 1 are all on Level 0, and the map shows a level-access lift.
- The main entrance is on Great Russell Street; there is also a Montague Place entrance.
- "Some galleries will close at short notice due to refurbishment or unforeseen circumstances. This may impact on step-free access."
- It gives no opening hours.

**What search results say (UNVERIFIED; 19 Nov):**
- "Daily: 10.00–17.00 (Fridays: 20.30)", last entry 16.45 (Fridays 20.15), closed 24–26 December.
- The main entrance has 12 steps, with lifts on either side.
- The Montague Place entrance is step-free.
- One ticketing page gives a different last entry (16.00).

**Fields to verify:**
1. **Hours and last entry** (and the Friday late), and the closed days.
2. **Step-free entry:** which entrance, and is it lift or level. Write yes, partial or no, with the sentence.
3. **Area:** the address as printed (for example "Great Russell Street, London WC1B 3DG"), or an area name if the page gives one.
4. **Any notice** that Rooms 1 or 4 are closed.

## 3. Ranks 3–18: the official-page pack (20 Nov 2026; about 2 h; Abram, 20 Nov §8)

In order of how often each place is planned (`material_gaps.md`). Every quote is from the official page named, read on 20 Nov. **"Not stated" stays unknown: nothing is filled in.**
- **No catalogue field has been changed yet.** The "proposed correction" column is applied on Abram's yes (about 0.5 h, then the tests and the coverage files).
- The British Museum and the Royal Festival Hall stay as sections 1–2 say. Their undated or conflicting PDFs change none of their fields (Abram, 20 Nov §8).

| # | Place (share of plans) | Now in the catalogue | Official source read 20 Nov | What's uncertain | Exact information to confirm, and by whom | Proposed correction |
|---|---|---|---|---|---|---|
| 3 | Greenwich Park, Wolfe's hill (18%) | hours "Pedestrian gates 06:00-18:00 as shown on 11 Nov (times change with the season)"; step-free **unknown**; the Rose Garden notice | royalparks.org.uk/visit/parks/greenwich-park: "Pedestrian gates 6am - 6pm". The FAQ: "Both close at dusk each day, which varies throughout the year". The mobility buggy page: "does not operate over winter between November and April"; its stops are Ignatius Sancho Café, St Mary's Gate and The Pavilion Café | **The closing time conflicts** (6pm vs dusk). A step-free way up the hill: not stated. The buggy's stops don't include the summit, and it isn't running now | The closing time for late November, from Royal Parks' 2026 opening-times page or PDF (not read). Whether there is a step-free route to the Wolfe statue. **Abram, or a call to the park** | Hours: record both sentences, and plan on the safe side, **the earlier of 18:00 and sunset** (about 16:00 now). Step-free stays unknown. Add: "the mobility buggy doesn't run November to April" |
| 4 | Somerset House to the river terrace (18%) | area **unknown**; step-free partial (checked) | somersethouse.org.uk/visit-us/getting-here: "Strand, London WC2R 1LA". The accessibility page: "There is step free access to the terrace bar, Setlist from Waterloo Bridge and the Strand level of the South Wing", and "two steps from the courtyard to the West Wing exhibition entrance" | Nothing material | — | **Area: "Strand"**, from the printed address. Step-free stays partial, with the terrace sentence as its quote |
| 5 | St Dunstan-in-the-East garden (18%) | hours "08:00 to 19:00 or dusk…" from **the card**, marked checked; step-free unknown; area City of London (from the title) | cityoflondon.gov.uk/…/st-dunstan-in-the-east-church-garden: **no hours, no postal address** ("Nearest tube: Monument or Tower Hill"); step-free not stated | The hours aren't on the official page | The garden's hours, from the City of London (its gardens team) or a sign on the gate. **Abram or a person on site** | Hours: **downgrade to "claimed"**: the source is the card, not the official page, so it shows "might be open". Area: "City of London", source the City's own gardens list. Step-free stays unknown |
| 6 | Waterloo Bridge at sunset (17%) | hours "Always open, free" from the card; step-free, area unknown | Westminster's pages: not stated. tfl.gov.uk and lambeth.gov.uk: **403** (refused) | Who publishes closures. Step-free on and off the bridge | The bridge's owner and its closure page; the step-free routes to the deck (lift or ramp at each end). **Abram in a browser** (TfL) | None yet. "Always open" stays claimed, so "might be open". Proposal for public bridges and streets, for Abram's yes: record "public right of way: open unless a dated closure notice", with the owner's closure page as the source |
| 7 | Beigel Bake, Brick Lane (14%) | hours 24/7 (checked); step-free unknown; area Brick Lane (from the title) | beigelbake.co.uk/pages/contact-us: "159 Brick Lane, London E1 6SB"; "OPENING TIMES 24 Hours / 7 Days a week"; step-free not stated | Step-free | Whether the shop has a step at the door. **A person on site**, or the shop | **Area: "Brick Lane", checked**, from the printed address. Step-free stays unknown |
| 8 | Hyde Park, the Serpentine (12%) | hours 05:00 to midnight (checked); step-free unknown | royalparks.org.uk/visit/parks/hyde-park: "Pedestrian gates 5am - midnight". The FAQ: "open from 5am and close at midnight each day throughout the year"; step-free not stated | Step-free paths round the Serpentine | Royal Parks' accessibility information for Hyde Park (not found on the pages read) | **Area: "Hyde Park", checked** (the park's own page). Step-free stays unknown |
| 9 | National Portrait Gallery (11%) | hours "Sun-Thu 10:30-18:00, Fri-Sat to 21:00" (search results, 28 Sep); step-free, area unknown | npg.org.uk/visit: **403** | Everything: no page read | Hours, step-free entrance and the address, from npg.org.uk/visit. **Abram in a browser, ~5 min** (template below) | None until read |
| 10 | Hyde Park bike loop (10%) | step-free unknown; the card's route is Serpentine Road and the Broad Walk | Hyde Park FAQ: cycling "permitted … only where stated (e.g. Serpentine Road, The Broad Walk etc.)"; "Pedestrians have priority at all times" | Nothing material: **the card's loop uses exactly the two routes the FAQ names** | — | Source the route to the FAQ's sentence (it was "Royal Parks, read 27 Sep"). Step-free isn't material for a cycle loop; it stays unknown |
| 11 | Sir John Soane's Museum (8%) | area unknown; hours and step-free checked | soane.org/your-visit: "13 Lincoln's Inn Fields, London, WC2A 3BP"; "normally open Wednesday to Sunday, 10am to 5pm"; the lift: "call at least 24 hours ahead" | Nothing material | — | **Area: "Lincoln's Inn Fields"**, from the printed address. The lift's 24-hour notice is already in the step-free note |
| 12 | Natural History Museum, the whale hall (8%) | area unknown; hours and step-free (partial) checked | nhm.ac.uk/visit/getting-here: "Cromwell Road, South Kensington, London SW7 5BD"; the access page: "step-free access to most areas"; the Central Entrance is "step free with a ramp". Hintze Hall isn't named | Whether "most areas" includes Hintze Hall | NHM access team, for Hintze Hall specifically (low priority: it's off the Central Entrance) | **Area: "South Kensington"**, from the printed address. Step-free stays partial |
| 13 | Across the Millennium Bridge (8%) | hours "Always open" (Wikivoyage, via the card); step-free, area unknown | City Bridge Foundation (the owner: "transferred … 22 February 2002"). Its works page: "**No major works or closures.**" It "links the City of London at St Paul's Cathedral with the Tate Modern Gallery at Bankside". Hours and step-free not stated | Hours and step-free aren't stated | Step-free access at both ends (ramps or steps). **A person on site**, or City Bridge Foundation | **Closures: source the owner's works page** (dated 20 Nov: none). "Always open" stays claimed until the right-of-way rule (row 6) is agreed. **Area: "Bankside"**, the end where the card starts. Step-free stays unknown |
| 14 | Burlington Arcade (7%) | hours and area (Mayfair) checked; step-free unknown | burlingtonarcade.com/location: "51 Piccadilly, London W1J 0QJ"; hours as held; step-free not stated | Step-free | The arcade's own answer on step-free entry from Piccadilly. **Abram, by email** | None. Step-free stays unknown |
| 15 | Old Spitalfields Market (6%) | hours record both conflicting blocks ("18:00 or 20:00") | oldspitalfieldsmarket.com/visitor-information: "16 Horner Square London, E1 6EW"; **two hours blocks that disagree** (10–6 vs 10–8 on Mon, Tue, Wed, Fri) | Which closing time is right; step-free (the page was cut off when read) | The market's office: the weekday closing time, and step-free entry. **Abram, by email** | Plan to **18:00**, the earlier time (the safe side), until confirmed. Area stays as held |
| 16 | Victoria Embankment Gardens (4%) | hours "from 08:00; closing varies"; area checked | westminster.gov.uk: **timed out twice**; nothing new | Step-free; seasonal closing times | Westminster's page, in a browser. **Abram, ~3 min** | None |
| 17 | Alderman Stairs (4%) | hours "public riverside path" (a friend's card); step-free, area unknown | no official visitor page exists; none read | Everything | Low priority (4%) | None. It stays as is |
| 18 | Covent Garden and Soho wander (2%) | public streets; area checked | not read (2%) | — | — | None |

**What the proposals would change in the numbers.** If accepted, they add 6 checked areas: Somerset House, Beigel Bake, Hyde Park, Soane, NHM and the Millennium Bridge. St Dunstan's area moves from the title to the City's list.
- **Missing areas:** 18 becomes 12.
- **Hours read on an official page:** St Dunstan's comes off the list.
- **Step-free:** nothing changes; no official page read today states it for these places.

**Hours spent:** Claude about 2 h (20 Nov), mostly in pages that refused or didn't say.

## The template (copy, fill, send)

```yaml
# Read in a browser by Abram on: 2026-11-__
m_rfh_foyers_rest:
  hours:     {page: "", as_written: "", mondays: "open | closed | not stated"}
  closures:  {page: "", as_written: ""}            # where private-hire closures are announced
  step_free: {page: "", answer: "yes | partial | no | not stated", as_written: "", lift_notice: ""}
  area:      {page: "", as_written: ""}            # the address or area exactly as printed
  conflicts: ""                                    # anything that disagrees with another official page
m_bm_great_court:
  hours:     {page: "", as_written: "", last_entry: "", closed_days: ""}
  step_free: {page: "", answer: "yes | partial | no | not stated", entrance: "", as_written: ""}
  area:      {page: "", as_written: ""}
  room_notices: ""                                 # any closure of Room 1 or Room 4
  conflicts: ""
m_national_portrait_gallery:                       # https://www.npg.org.uk/visit (403 to automated reading)
  hours:     {page: "", as_written: "", late_days: "", closed_days: ""}
  step_free: {page: "", answer: "yes | partial | no | not stated", entrance: "", as_written: ""}
  area:      {page: "", as_written: ""}            # the address as printed
  conflicts: ""
```

**Hours:** Abram ~15 min for sections 1–2, plus ~5 min for the National Portrait Gallery and a few emails for rows 3, 14 and 15. Claude ~0.5 h to record what he sends and to apply the accepted proposals.
