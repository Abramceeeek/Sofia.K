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

## 3. The rest of the top 20 (`material_gaps.md`)

| Rank | Place | Missing | Who can check |
|---|---|---|---|
| 4, 9, 11, 16, 17, 18 | Greenwich Park, Hyde Park (twice), Burlington Arcade, Old Spitalfields, Victoria Embankment Gardens | step-free (and seasons for 18) | **Claude:** their official pages were readable on 11–12 Nov. About 1.5 h; any page that doesn't say stays unknown |
| 5, 12, 13 | Somerset House, Soane Museum, Natural History Museum | area | **Claude:** the address as printed on their readable pages; ~0.5 h |
| 6, 14 | St Dunstan-in-the-East, the Millennium Bridge | hours, step-free (and area and season for 14) | **A person**, or the City of London. The official pages state no hours, and there's no visitor page for the bridge |
| 7, 19 | Waterloo Bridge, Alderman Stairs | hours, step-free, area, season | Open public places with no "official hours". Claude proposes how to record "always open" with a source (e.g. the bridge's owner), for Abram's yes |
| 10 | National Portrait Gallery | hours, step-free, area | **Abram in a browser** (403), as above; ~5 min |

**Reaching Limited support** needs 40 of 49 places with official hours (31 now) and 25 with step-free status (17 now). The top 20 alone can't get there. But checking them makes what most testers see reliable, which is Abram's priority.

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
```

**Hours:** Abram ~15 min (plus ~5 min for the National Portrait Gallery); Claude ~0.5 h to record them, and ~2 h for ranks 4–18 where the pages are readable.
