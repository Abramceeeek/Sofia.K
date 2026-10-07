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

- Duffel's own airline pages say "300+ airlines"; a Duffel blog post says 380+ with partner agreements. easyJet is requested from the dashboard. None of the results list Ryanair or Wizz Air on Duffel.
- Ryanair sells through its own site and an "Approved OTA" programme of named partners and aggregators, each by agreement.
- Travelpayouts' data API returns cached prices from users' past searches, meant for content pages; partners are asked to cache for 24 h.
- Viator: an affiliate account gives Basic Access at once (no approval, no minimums), single-product requests only, bookings on viator.com.
- Tiqets opened its Partner API to affiliates on 28 Nov 2025 (self-service tokens); the Booking API needs about 200 orders a month.
- Ticketmaster's Discovery API: 5,000 calls a day and 5 a second by default (one aggregator says 2 a second).

## Gaps we'd have to fill ourselves

- **Ryanair and Wizz Air** fares in the app: no route without a contract. The Skyscanner link covers them.
- **Homes and flats** (Airbnb): no API (Area D120, `research/sources.csv`).
- Matching experiences to our moment cards (a Tiqets ticket to the right card) is our work, card by card.

## Risks / unknowns

- Affiliate accounts (Viator, Tiqets, Travelpayouts) are commission programmes: using them to earn is a money step after the company exists (D120: no commission while testing). Using the data while earning nothing is possible, but the links carry affiliate tracking.
- Duffel's airline list changes; check the dashboard's Airlines page when live.
- Coverage figures are the suppliers' own marketing numbers.
