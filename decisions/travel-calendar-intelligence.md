# The travel calendar: dates that change a trip, as facts (WS5, 7 Nov 2026; m211)

**Decision.** Travel timing's calendar part is two calendars, kept apart:
- **your calendar:** home, meaning your nation's bank holidays and, if you choose to say it, your council's school holidays;
- **the destination's calendar:** its own holidays, and later its festivals, major events and seasons.

Every entry carries:
- its kind (bank holiday, public holiday, school holiday, major event, festival, seasonal);
- its country, region and council;
- its dates (inclusive);
- its source and the date it was last checked;
- who it applies to, and its exceptions.

**Bank holidays and school holidays are different kinds of data.** A council's school holidays never apply to every school.

**What isn't known is said:** an unknown destination, a year outside the data, an area not checked yet. It's never shown as "nothing on". Nothing says "busier" or "dearer": only what's on.

**Built:** `brain/src/brain/travelcalendar.py` and the first checked school holidays (`brain/data/calendar/school_holidays.yaml`: Cardiff and Edinburgh, 2026-27), with 8 tests. The stay comparison now says when the destination's holidays aren't known (`holidays_note`), on both phones.

## Sources (read 7 Nov 2026)

| What | Source | Notes |
|---|---|---|
| UK bank holidays | GOV.UK's file, https://www.gov.uk/bank-holidays.json (m204) | England and Wales, Scotland, Northern Ireland; 2019 to 26 Dec 2028; substitute days marked |
| School holidays in England | **Each council, not the government.** GOV.UK's page sends you to your council (https://www.gov.uk/school-term-holiday-dates, m204) | Academies, free schools and voluntary-aided schools can set their own; independent schools always do |
| School holidays in Wales | Welsh Government, "Approved school term dates 2026 to 2027", https://www.gov.wales/approved-school-term-dates-2026-2027-html (last updated 16 July 2025) | One table for all 22 councils. 21 share the same dates; **Powys** ends the autumn term on Tue 22 Dec 2026 and the summer term on Fri 16 Jul 2027. Term dates only: holidays are the days between terms |
| School holidays in Scotland | Each council | Edinburgh: https://www.edinburgh.gov.uk/schools/term-dates ("Dates for holidays are inclusive"; "Schools set their own start and finish times") |
| Northern Ireland | Not researched yet | — |

## Coverage matrix (m222, 8 Nov 2026): what's checked, and what isn't

The matrix is data (`brain/data/calendar/coverage.yaml`), not prose. A test holds it to the dates both ways: every area with dates is in a "checked" row, and every "checked" row has its dates. **Two councils are never "UK-wide"**: England has no council checked.

| Where | Level | Status | Source (read) | Years | Notes |
|---|---|---|---|---|---|
| **Wales**, all 22 councils | council | **checked** | Welsh Government's approved term dates (gov.wales, updated 16 Jul 2025; re-read 8 Nov) | 2026-27 | 21 share dates. **Powys** ends the autumn term Tue 22 Dec 2026 and the summer term Fri 16 Jul 2027. The page doesn't say which kinds of school follow them. Summer 2027's end: the 2027-28 page doesn't exist yet (404) |
| **Scotland**, City of Edinburgh | council | **checked** | edinburgh.gov.uk (7 Nov) | 2026-27 | — |
| Scotland, the other 31 councils | council | not checked | — | — | one council at a time |
| **Northern Ireland** | national | **checked** | Department of Education, "school holidays" (8 Nov) | 2026-27 | "Non-operational dates": schools "can operate on these dates at their own discretion". It includes the Minister's three extra closure days (25 Sep 2026, 25 Jan 2027, 4 May 2027). Summer starts 1 Jul 2027 |
| **England, Westminster** (bi-borough with Kensington and Chelsea) | council | **checked** (m225, 9 Nov) | westminster.gov.uk "School term and holiday dates" (updated 29 Oct 2026) and its 2026-27 and 2027-28 PDFs | 2026-27 | **Recommended** dates: "schools have the autonomy to determine their own term dates". Kensington and Chelsea shares the PDF but isn't added from Westminster's page |
| **England, Birmingham** | council | **checked** (m225) | birmingham.gov.uk "School term dates" (updated 12 Oct 2026) | 2026-27 | Term dates only (holidays between terms). "May not apply to academies, foundation, free or voluntary aided schools" |
| **England, Leeds** | council | **checked** (m225) | leeds.gov.uk "School holidays and term dates" (its new address; the old one is 404) | 2026-27 | Academies, free, foundation and voluntary-aided schools can set their own. Each school has 5 training days of its own |
| England: Camden, Manchester, Kent, Hampshire | council | **blocked** (re-tried 9 Nov) | Camden, Manchester and Kent: a Cloudflare bot challenge on the whole site. Hampshire: a captcha, documents host included. Kent's schools site is refused by this environment's network | — | **For Abram to read by hand** (~10 min each), never from an aggregator. Not worked around: getting past a bot check isn't reading the page as the council offers it |
| England, every other council | council | not checked | — | — | — |
| **France**, zones A, B and C | region | **checked** | Ministry of Education open data "Le calendrier scolaire" (DNE, Licence Ouverte v2.0, modified 1 Oct 2026; read 8 Nov) | 2026-27 | **The definition:** the data says holidays begin "après la classe des jours indiqués" and classes resume "le matin des jours indiqués". So each holiday runs from its Saturday to the day before classes resume. Winter and spring differ by zone. The Ascension bridge is left out: its row has the same start and end time. Which académies are in each zone: the ministry's page is 403. Corsica and overseas aren't added |
| **The Netherlands**, regions noord, midden and zuid | region | **checked** | Government open data (Ministerie van OCW, CC0, modified 7 May 2025; read 8 Nov) | 2026-27 | Autumn, spring and May are **advice dates** ("Scholen mogen hier dus van afwijken"), and each says so. Christmas and summer are compulsory. Provinces per region aren't in the data |
| Every other country | national | not checked | — | — | — |

**Bank holidays stay separate.** On 17 March 2027 a Northern Ireland traveller sees two entries: the bank holiday (GOV.UK) and the school's non-operational day (the Department), each with its source (tested).

**Found:** France and the Netherlands publish official, machine-readable school calendars under open licences. That makes them the cheapest next countries. England has no national source. Of the 7 English councils tried, 3 are checked from their own pages (m225) and 4 sit behind bot checks.

## Council coverage (7 Nov, the first table; superseded by the matrix above)

| Country | Region | Council | Source | School years | Last verified | Exceptions | Status |
|---|---|---|---|---|---|---|---|
| GB | Wales | Cardiff Council | gov.wales approved dates | 2026-27 (summer holiday's end not read) | 7 Nov 2026 | Independent schools set their own; the page doesn't say whether every kind of school follows them | **Checked** |
| GB | Scotland | City of Edinburgh Council | edinburgh.gov.uk term dates | 2026-27 (summer holiday's end not read) | 7 Nov 2026 | Schools set their own start and finish times; independent schools set their own dates | **Checked** |
| GB | England | London Borough of Camden | camden.gov.uk/term-dates | — | — | The page says "some Camden schools have different term dates" (via a search extract) | **Not checked:** the page refused automated reading (403). Third-party copies exist but aren't used |
| GB | England | Manchester City Council | manchester.gov.uk/termdates | — | — | — | **Not checked:** 403 |
| GB | England | Westminster, the London Councils summary | — | — | — | — | **Not checked:** 500 and 403 (m204) |
| GB | Wales | The 20 other councils sharing Cardiff's dates | gov.wales | 2026-27 | 7 Nov 2026 | Powys differs (above) | Ready to add from the same table |

**How the table grows.** One council at a time, read from its own page, or the Welsh Government's table. Each entry gets the date it was read. Every summer, when the new year's dates are out, each entry is re-read. A council whose page can't be read automatically is checked by hand (about 10 minutes each), never copied from an aggregator.

**Asking for someone's council is asking roughly where they live.** So it's optional ("Want your area's school holidays shown?"), kept on the phone like location (D123), and sent only with each request, which stores nothing. It's never used for anything else.

## What the code does

- `home_calendar(division, school_area, start, end)` and `destination_calendar(destination, key, start, end)` return separate views. The destination's view never holds the traveller's school holidays (tested).
- Bank holidays are taken from the existing file, with "Everyone in England and Wales" as who it applies to and substitute days said. School holidays read "Schools that follow Cardiff Council's dates", with the exceptions.
- A bank holiday and a school holiday on the same dates stay two entries (Edinburgh's winter holiday and Christmas Day, tested).
- **Unknown, said:**
  - "We don't have Paris's holidays yet.";
  - "Bank holidays are known from 1 Jan 2019 to 26 Dec 2028 only.";
  - "Cardiff Council's school holidays are checked for 2026-27 only.";
  - "School holidays for your area aren't checked yet.";
  - "Festivals and major events aren't added yet."
- **Dates are the place's own:** `local_day` gives the date at the destination (23:30 UTC on 24 Dec is already Christmas Day in Vienna; 23:30 UTC on 30 Jun is 1 Jul in London's summer time).

**Tested** (`tests/test_travel_calendar.py`, 8):
- the UK nations (2 January in Scotland only, St Patrick's Day in Northern Ireland);
- substitute days;
- overlaps;
- unknown destinations;
- missing years;
- an uncovered council;
- inclusive date boundaries (the day a break starts, a one-day holiday);
- time zones and summer time;
- every school entry has its source, date, exceptions and years.

## Next (after the round; hours are GUESSES)

| Step | Hours |
|---|---|
| The 20 other Welsh councils from the same table, and Northern Ireland's source | Claude ~1 h |
| English councils by hand, starting with London's 33 (a checker can do it from this table's columns) | ~10 min each |
| "Your calendar" in the apps: optional nation and council, on the phone; the trip's dates show home and destination side by side | Claude ~5 h, both apps |
| Destination events and festivals, each from the organiser's own page | Per city, with WS1's coverage |
| Other countries' public holidays (an official source per country) | Per country |

**This step:** Claude ~3 h (the model, the checked data, the tests, the note on both phones, this page).
