# Area 21 — travel data beyond Duffel and LiteAPI

**Decision (7 Oct 2026, proposed to Abram):** keep Duffel (flights) and LiteAPI (stays) for the tests. Close the one real gap with words, not another supplier: live flight results say that some low-cost airlines, such as Ryanair, may be missing, and Skyscanner (linked below them) shows them. Abram asks Duffel for easyJet under "Sources" (5 min). Ticketed experiences and events (Viator, Tiqets, Ticketmaster) wait until after Test B (`decisions/after-9-nov.md` #54–56). Hours: Claude 0.5 h now (done); the rest GUESSED below.

## What exists (ranked, max 8 items)

| # | Name | What it gives | Access for ODYS today | Why it matters |
|---|------|---------------|-----------------------|----------------|
| 1 | **Duffel** (in use) | Live flight offers | Test key live; live after KYC | "300+ airlines"; 380+ counting partner agreements; **easyJet on request** in the dashboard (Sources). **Ryanair and Wizz Air: not found** |
| 2 | **LiteAPI** (in use) | Live hotel rates, photos | Sandbox key live; production with a card | "2.6M+ hotels" from "300+ suppliers" (Nuitée's figures). No homes/flats like Airbnb |
| 3 | **Ryanair's approved partners** | Ryanair fares | Contracts only: aggregators Paxport, Travelfusion, Atlas, DerbySoft; OTAs such as Expedia, Kiwi, Trip.com, lastminute.com | Ryanair is big at Stansted and Luton. No route for a startup without a contract (UNVERIFIED: their terms for small partners) |
| 4 | **Travelpayouts (Aviasales data API)** | **Cached** fares from Aviasales users' searches (kept 2–7 days), all airlines Aviasales covers | Free token with an affiliate account; the data API is listed as not needing brand approval | Could show "seen from £X" for airlines Duffel lacks. Not live prices; affiliate (commission) platform |
| 5 | **Viator Partner API** | Tours, tickets, experiences: content and availability | **Basic Access straight away** with an affiliate account; bookings on viator.com | Prices and booking links for ticketed moments |
| 6 | **Tiqets Partner API** | Attractions and museum tickets: content, availability, prices, reviews | **Self-service tokens for affiliates** since 28 Nov 2025; booking API from ~200 orders a month | Same use as Viator, strong on museums and attractions |
| 7 | **Ticketmaster Discovery API** | Concerts, theatre, sport, by date and city | **Free key: 5,000 calls a day**, 5 a second | "What's on tonight" for a trip's evenings |
| 8 | Expedia Rapid, GetYourGuide, Duffel Stays, Booking.com Demand | Hotels / experiences | Partner-only, certification, or "contact sales" | Not reachable for the tests |

## What the evidence says

- **Checked on the live Brain (7 Oct, LiteAPI sandbox, London):** with 400 hotels per search, ibis (6 branches), easyHotel, Point A, Z Hotel, Holiday Inn Express, Moxy, Zedwell and Best Western come back; **Travelodge and Premier Inn never do**. A fresh search takes 13–16 s (repeats come from the 15-minute cache). Duffel's airline directory has **Turkish Airlines and Pegasus**; **AJet, Uzbekistan Airways, Wizz Air and Ryanair have no page** (404).
- Premier Inn sells ~94–97% direct (Booking.com was named as its only online agent, 2016–17 sources); Travelodge's cheapest Saver rates are direct only (Dec 2025). AJet's newest NDC connection went live first through Atlas, a B2B aggregator.

- Duffel's own airline pages say "300+ airlines"; a Duffel blog post says 380+ with partner agreements. easyJet is requested from the dashboard. None of the results list Ryanair or Wizz Air on Duffel.
- Ryanair sells through its own site and an "Approved OTA" programme of named partners and aggregators, each by agreement.
- Travelpayouts' data API returns cached prices from users' past searches, meant for content pages; partners are asked to cache for 24 h.
- Viator: an affiliate account gives Basic Access at once (no approval, no minimums), single-product requests only, bookings on viator.com.
- Tiqets opened its Partner API to affiliates on 28 Nov 2025 (self-service tokens); the Booking API needs about 200 orders a month.
- Ticketmaster's Discovery API: 5,000 calls a day and 5 a second by default (one aggregator says 2 a second).

## Other services like Duffel and LiteAPI (checked 7 Oct)

| Service | Kind | Access | Fit for ODYS now |
|---|---|---|---|
| **Duffel** (in use) | Flights: search and book, real fares | Self-serve sign-up | The only self-serve flight booking API in the comparisons found |
| Amadeus Self-Service | Flights, hotels | **Closed 17 Jul 2026**; only Amadeus Enterprise (accreditation) | No |
| Kiwi.com Tequila | Flights incl. low-cost | Invitation only | No |
| Sabre Dev Studio | GDS flights (Bargain Finder Max) | Free developer account and test environment; production needs a commercial agreement and certification | Not before a company and agency set-up |
| Travelport | GDS flights | Trial request, then sales onboarding | No |
| **Travelfusion** | 150+ low-cost and scheduled airlines; an approved Ryanair aggregator | Licence agreement and fees before use; bookings from an agency credit account | The way to Ryanair-type airlines, after the company (contract) |
| Atlas | Low-cost airlines (Ryanair, AJet) for sellers | Contract | Same as Travelfusion |
| Mystifly | 600+ airlines (its claim) | Sales onboarding, quote-based | No |
| Ignav | Flight prices and booking links, no ticketing | Free account; per-request pricing | **Data source not stated (UNVERIFIED)**: if it copies other sites, it carries the scraping risk |
| **LiteAPI** (in use) | Hotels | Self-serve | Keep |
| Hotelbeds | Hotels | Self-serve evaluation, 50 requests a day; production by contract | Too few requests for testing |
| RateHawk (ETG) | Hotels, 2.5M+ properties | Contract first; sandbox after; new entrants face more scrutiny | After the company |
| Agoda | Hotels (Search API for affiliates and metasearch) | Become a partner, then certification | After the company |
| Expedia Rapid, Booking.com Demand | Hotels | Partner-only, case by case | No |
| Duffel Stays | Hotels, 1M+ properties (Duffel dashboard, 7 Oct) | "Contact sales" | Ask when going live with Duffel |

**So:** no other self-serve service adds much for the tests. The real gains (Ryanair- and AJet-type airlines through Travelfusion or Atlas; more hotels through RateHawk or Agoda) all need a company and a contract: Stage 3 of `decisions/roadmap.md`.

## Gaps we'd have to fill ourselves

- **Ryanair and Wizz Air** fares in the app: no route without a contract. The Skyscanner link covers them.
- **Homes and flats** (Airbnb): no API (Area D120, `research/sources.csv`).
- Matching experiences to our moment cards (a Tiqets ticket to the right card) is our work, card by card.

## Risks / unknowns

- Affiliate accounts (Viator, Tiqets, Travelpayouts) are commission programmes: using them to earn is a money step after the company exists (D120: no commission while testing). Using the data while earning nothing is possible, but the links carry affiliate tracking.
- Duffel's airline list changes; check the dashboard's Airlines page when live.
- Coverage figures are the suppliers' own marketing numbers.
