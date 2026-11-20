# Global financial intelligence: a display currency, and who supplies prices (10 Nov 2026; m238)

**Decision: the Brain supports any display currency now; the apps add the choice after the friends' round.**
- **A traveller plans in their own currency.** A UK traveller in pounds (the default, unchanged), a US traveller in dollars: any currency the ECB publishes, or the euro.
- **The provider's price and currency are never changed.** The conversion is an estimate shown beside the price, with its source and date. The price is in the original currency, never the display one.
- **Freshness and fallback are unchanged from m218:**
  - a rate over five days old is never used;
  - a currency the ECB doesn't publish isn't converted;
  - without a usable rate, prices are grouped by currency, the display currency first, and **nothing ranks across currencies**.
- **The live ECB rates stay off** (`fx_rates_live = False`), as Abram decided (m224).

`brain/src/brain/fx.py` (`pricing(…, display=)`, `display_options`, `currency_name`); `display_currency` on the flight and stay searches (pattern `^[A-Z]{3}$`, default GBP); `brain/tests/test_currency.py` (3 new tests, 12 in all).

## How it behaves

| Case | What the person sees |
|---|---|
| Pounds (the default) | Exactly as today: m218's wording and tests are unchanged |
| US dollars, fares in GBP and EUR, a current ECB rate | 400 EUR shows "≈ $446.60 · ECB rate of 6 Nov 2026" beside the fare (400 × 1.1165). £389 shows ≈ $520.67 (crossed through the euro). "Cheapest" compares the dollar estimates. The note says "converted to US dollars … an estimate. You pay the price in its own currency." |
| Display currency the same as the fares' | No estimate and no note: nothing to convert |
| A display currency the ECB doesn't publish (for example UZS), or a rate over five days old | Grouped by currency, not ranked across them; no estimates |
| Without rates | Pounds is the only display option (`display_options`) |

## Exchange-rate sources (read 10 Nov 2026)

| Source | Rates | Cost and limits | What it says about use |
|---|---|---|---|
| **ECB euro reference rates** (in use, off) | About 30 currencies against the euro, "usually updated at around 16:00 CET every working day" | Free, no key | "published for information purposes only"; "Using the rates for transaction purposes is strongly discouraged". That's why ODYS only ever shows an estimate |
| **Frankfurter** (frankfurter.dev) | Blended from "111 central banks and official sources" by default; can be filtered to one provider, such as the ECB | "Free, open-source", no key; "There are no quotas", only abuse rate limits | "These are reference rates, not live market quotes". Blended rates are its own calculation |
| **Open Exchange Rates** | USD base, hourly on the free plan | Free: 1,000 requests a month. Developer **$12 a month**; Enterprise **$47 a month** (30-minute updates); Unlimited **$97 a month** (5-minute updates) | The licence page wasn't read |

**Recommendation.** Keep the ECB as the only source. If its host is ever unreachable, the fallback is **Frankfurter filtered to the ECB**: the same rates from another host, never its blended rates mixed in silently. Each fallback rate carries its own source line, and the same five-day rule applies. A paid feed isn't needed: ODYS shows estimates, not payable amounts.

## Who could supply prices (read 10 Nov 2026 unless said)

| For | Provider | Access | Cost or commission | Notes |
|---|---|---|---|---|
| **Flights** | **Duffel** (in the code; test keys only) | Pay as you go, with sign-up; enterprise by contact | **$3.00 per order**; managed content 1% of order value; **$2.00 per paid ancillary**; **$0.005 per excess search** above a 1,500:1 search-to-book ratio; **2% on the exchange rate** when Duffel converts | Its FX charge is one more reason to show fares in their own currency |
| Flights | Amadeus for Developers (self-service) | **Reported shut down:** PhocusWire (Feb 2026) quotes Amadeus "decommissioning only the self-service section". A third-party guide gives 17 Jul 2026 for the closure | — | Amadeus's own page returned an empty body: **UNVERIFIED from Amadeus itself**. Enterprise APIs are by request |
| **Hotels** | **LiteAPI** (in the code; sample results only; live prices off) | — | **UNVERIFIED**: its pricing page returned 404 | Stays off (Abram) |
| Hotels | Booking.com Demand API | The developer site lists the Demand API | Access terms not read (the getting-started page returned 404) | UNVERIFIED |
| **Activities** | **Viator** (affiliate API) | "Quick & free sign-up with no traffic or follower minimums"; Basic API access straight away | **8% commission** on completed bookings within a 30-day cookie; "no costs to sign up" | A commission is revenue, so it waits for the money gates (incorporation, insurance) and "no commission while testing" |
| Activities | GetYourGuide Partner API | — | — | The page had only a title: **UNVERIFIED** |
| **Public transport** | TfL (London; in use since Stage 1) | — | — | Today's open-data page refused automated reading (403). The existing setup is in `brain/README.md` |
| Public transport | GTFS feeds (Mobility Database; Transitland) | Mobility Database: "free access" to over 6,000 feeds; Transitland: commercial use only on paid tiers | Transitland: $1.50 per 1,000 REST requests after 10,000 free a month | Whether a city's feed carries fares varies (UNVERIFIED per city) |

**What ODYS does with any of them:**
1. Keep the provider's price and currency exactly as given.
2. Convert only for display, labelled as an estimate with its source and date.
3. Never present a conversion as payable.
4. Book on the provider's own site.

## The apps (after the friends' round; not built)

A "Currency" choice in You: pounds by default, the options from `display_options`. Both apps send `display_currency` with each search and show the estimate line in that currency. They already show the estimate line separately (m218, m231).

**GUESS: ~3 h, both apps, with screenshots.** It only matters once the ECB rates are on.

**Hours this step:** Claude ~2 h.
