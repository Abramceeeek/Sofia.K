# Comparing prices in different currencies (8 Nov 2026; m218)

**Decision: built, on the branch.** ODYS no longer ranks prices in different currencies against each other as raw numbers.

- With a current exchange rate, it converts each price to pounds to compare them. The original fare and its currency stay as they are, and the converted estimate is shown beside the fare with its source and the rate's date.
- Without a current rate, it groups results by currency and never calls anything the cheapest overall.

Fetching rates is **off** until Abram switches it on (`Settings.fx_rates_live`, one line). Until then, results in one currency are compared as before, and results in several currencies are grouped.

## What the audit found (before this change)

| Where | What was wrong |
|---|---|
| Flights: "Cheapest" sort, tab and tag | Sorted by the raw number. 300 EUR would rank as cheaper than £389. |
| Flights: "Best" | Prices in different currencies were scaled together as if they were one currency. |
| Flights: the price filter, "from" per stops and per airline, the slider range | All were minimums and comparisons across currencies. |
| Stays: "Cheapest", "Recommended" and the price filter | The same raw comparison. "Cheapest" also ignored fees paid at the property. |
| Both apps: sort tabs, filter prices, airline rows, "From £…" on the trip, the hand-off sheet | Showed **£** whatever the currency (`Money.whole(x)` with no currency). |
| Both apps: "Trip so far" | Added the flight's and the stay's numbers into a pound total, whatever their currency. |
| The chosen flight or stay saved on the phone | Had no currency, so it was always shown as pounds. |

**How likely mixed currencies are.** Duffel prices offers in the organisation's billing currency. The exceptions are an accredited IATA agent, or a request priced for a card or airline credit; then the airline's own currency is used (duffel.com/docs/api/v2/offers, `total_currency`, read 7 Nov 2026). LiteAPI is asked for GBP. So today a whole result set in one other currency is more likely than a mix, for example if the Duffel account is billed in USD. Both cases are handled.

## How it works now

**The rates** (`brain/src/brain/fx.py`):
- **Source:** the European Central Bank's euro foreign exchange reference rates, from the daily file `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml`. It's free and needs no key. It covers 29 currencies against the euro and is usually updated around 16:00 CET on working days. The page says "The reference rates are published for information purposes only" (read 7 Nov 2026), so ODYS only ever shows them as an estimate.
- **Conversion:** pounds per unit is crossed through the euro, rounded half-up to the penny in decimals.
- **When rates count:** a rate is current for 5 days, which covers Easter, the longest usual gap. After that nothing is converted.
- **Fetching:** at most every 6 hours. A failed fetch keeps the last good rates and never makes rates up.

**Comparing** (`fx.Pricing`, used by `trips.filter_flights`, `flight_tops`, `flight_facets`, `filter_stays`, `stay_tops` and `stay_facets`):

| Results in… | Sorting | "Cheapest" | Price filter and slider | What the person is told |
|---|---|---|---|---|
| one currency | as before | as before | in that currency (shown with its code) | if it isn't pounds and a rate is current: the pounds beside each, "an estimate. You pay the price in EUR." |
| several, with a current rate for all | by the pound estimate | the cheapest by estimate | in pounds, marked "≈" | "To compare them, other currencies are converted to pounds at the ECB rate of 6 Nov 2026: an estimate. You pay the price in its own currency." |
| several, no rate (or one the ECB doesn't publish, such as the Uzbek som) | grouped by currency, pounds first; ranked within each | "Cheapest in GBP", "Cheapest in EUR"… and nothing overall | in the first group's currency; a fare in another currency can't be checked, so it doesn't pass the filter (like any unknown) | "…there's no current exchange rate here, so they're grouped by currency and not ranked against each other." |

- **The original fare is never rewritten.** The response keeps `price` and `currency`. The estimate is a separate `estimate` object with `amount`, `currency`, `rate`, `source`, `as_of` and `line`; a stay's also has `total`.
- **Fees.** A stay's "Cheapest" now sorts by what a night really costs: the price plus fees paid at the property in the same currency. The card shows those fees ("+ £20 paid at the property"). Fees in another currency are stated and never added (m209).
- **Bags.** Fares are compared as sold. If some include a checked bag and some don't, or it isn't known, the results say so and point to the "Checked bag included" filter. A bag's own price isn't shown: Duffel returns `available_services` (bags and their prices) only from its single-offer call. Asking for that per offer would be an extra provider request for every result, so it isn't done.

**The apps (both):**
- every price shows its own currency;
- the estimate goes under the fare: "367 EUR / ≈ £306 · ECB rate of 6 Nov 2026";
- the comparison notes sit above the results;
- a chosen flight or stay keeps its currency;
- "Trip so far" adds only pounds, and lists any other currency below with "Prices in another currency are listed below, not added to this total";
- choices saved by older builds have no currency and read as pounds, as they were.

## Checks

- `brain/tests/test_currency.py` (9 tests) covers:
  - the ECB file (the real structure, with its USD and GBP rates for 6 Nov 2026) and crossing through the euro;
  - rounding;
  - how long a rate stays current;
  - a failed fetch keeping the last good rates, and stale rates not being used;
  - one currency (GBP, and EUR alone);
  - GBP, EUR and USD without a rate (grouped, no overall "Cheapest", the price filter in pounds only, no minimum across currencies), and with a rate (converted, the fare kept);
  - UZS, which the ECB doesn't publish;
  - stays sorted by their real cost per night, and mixed-currency stays;
  - the bag note;
  - the flight endpoint end to end, without and with a rate.
  - On the old sorting, 300 EUR came out "Cheapest" ahead of £389.
- `test_trips.py`: one assertion updated, because facet rows now carry their currency.
- **Android:** `MoneyTest.estimatesAndChoicesKeepTheirCurrency`, and the screenshot `26b-flightscurrency`.
- **iPhone:** demo screen `flightscurrency`, with the same data (`app/Sources/Demo/demo_flights_mixed.json`). That file is the sample flights with three fares re-priced in euros and compared at the 6 Nov rate. It's sample data, labelled "sample prices" on the screen.

## The sort tabs and the estimate screenshot (m231, 9 Nov 2026; branch only)

- **The fault:** the iPhone's "Cheapest" tab cut off "357 EUR · 22h 5…" (run #105). A currency code is longer than a £ sign.
- **The fix, both apps:** each tab puts the price on one line and the time (flights) or the distance or rating (stays) on the next. A line may shrink to 80% before anything is cut, as the iPhone already did. The three tabs keep one height.
- **Measured on Android** (`SortTabFitTest`, 3 tests), on a 360 dp phone with the header's 20 dp sides:
  - "12,345 USD", "9,999 EUR", "1,234 USD", "22h 53m" and "Rated 4.5" fit at full size ("12,345 USD" needs 135 of 166 px);
  - the old one-line form still doesn't fit even at 80%.
- **On the iPhone:** the CI screenshots `flightscurrency` (the tabs) and a new `flightcurrency`. The new one opens a fare in euros: its price in euros, and under it "≈ £306 · ECB rate of 6 Nov 2026", the estimate kept apart from the fare.
- **Abram's conditions for switching the ECB rates on (m224), checked against the code:**

  | Condition | Where it's met |
  |---|---|
  | The fare keeps its own currency | The price shown is always the fare's own |
  | The estimate is shown apart, with its source and date | The "≈ … · ECB rate of …" line |
  | Rates over five days old stop cross-currency ranking | `fx.MAX_AGE_DAYS = 5`; older than that, nothing is converted and the currencies are grouped |
  | A conversion is never presented as payable | "≈", and the line sits under the fare, never in its place |

  **Still off:** `fx_rates_live = False`.

## What's left, and Abram's decision

- **Switch on the ECB rates?** (`fx_rates_live = True`, one line, then a deploy after the friends' round.) This would be ODYS's first data from the ECB; it's free and needs no key. Until it's on, the app never shows an estimate, and mixed currencies are grouped. **Recommendation:** switch it on when live flight keys are added, not before, because sample results are all in pounds.
- **Bag prices.** Only if a booking flow ever needs them; each one is an extra Duffel request per offer.
- **The trip budget** (`tripbudget.py`, sprint 1) already keeps other currencies apart, and it stays that way.

**Hours:** Claude ~4 h. Abram: the switch decision above (5 minutes).
