# The whole trip's cost (WS6, 7 Nov 2026; m212)

**Decision (proposed).** A trip's cost is a list of lines, each saying what it is:
- **confirmed** (booked);
- **a current quote** (a price a search shows now);
- **an estimate** (our planning figure, with its source);
- **optional** (only if the person adds it);
- **unknown** (not priced yet).

Rules:
- **An incomplete total is never called "the total".** It's "at least £907 so far", with what's missing named.
- **A line in another currency is converted only with a dated rate,** and says so. Without one it's shown in its own currency.
- **Per person and for the group** are both shown.
- **Against a budget, ODYS says the gap and which figures could move,** largest first. Booked costs never move. It never invents a cheaper price.

**Built:** the model and its rules (`brain/src/brain/tripbudget.py`), with 6 tests. It is not wired into the API or the apps: a budget screen is only honest once flights and stays have live prices (Stage 1, and m205 for stays).

## The cost types

Flights, trains, buses, car, accommodation, local transport, food, attractions, experiences, shopping, other.

**Needed for a complete total:**
- where you stay;
- getting around;
- food;
- getting there and back (any one of flight, train, bus or car).

Shopping is never "missing": it's the person's own choice.

## Where each figure comes from today

| Line | Status | Source |
|---|---|---|
| A booked flight or stay | confirmed | The person's booking (they tell us, or it was chosen through the app's link) |
| A flight or stay found in the app | quote | Duffel and LiteAPI, **sample prices while the keys are test and sandbox** (labelled) |
| Local transport in London | estimate | TfL: a Zone 1 single counted per Tube or bus leg, capped at the Zones 1–2 daily cap of £8.90 (`dayplan.transport_gbp`; TfL fares read 27–28 Sep 2026) |
| Lunch | estimate | £15 each, a planning GUESS (D102) |
| Dinners, breakfasts | unknown | Not estimated: no source yet |
| Paid places in the day plans | quote | The moment cards' prices, each with its checked date |
| An experience the person might add | optional | Its card or the provider's price |

## A worked example: two people, three nights in London, a £900 budget

The figures are samples, except the TfL cap and the £15 lunch guess.

| Line | Per | Status | Amount (group) |
|---|---|---|---|
| Train to London and back | group | quote (sample) | £180 |
| 3 nights, booked | group | confirmed | £420 |
| Tube and bus, at most the daily cap (4 days × £8.90) | person | estimate | £71.20 |
| Lunches (4 × £15) | person | estimate | £120 |
| Paid places in the day plans | person | quote | £116 |
| Dinners | — | unknown | — |
| A boat trip | person | optional | £48 |

What the person reads:

> **At least £907 so far for 2 people (£454 each): not everything is priced yet.**
> Not priced yet: Dinners.
> Optional, not included: up to £48 if you add them.
> Of which confirmed £420, quote £296, estimate £191.
> **£7 over your £900, before what isn't priced yet.**
> Where it could move:
> - Train to London and back: £180 (a price found now: other dates or options may differ).
> - Lunches: £120 (our estimate: your own choices set it).
> - Paid places in the day plans: £116 (a price found now…).
> - Tube and bus: £71 (our estimate…).

Things it deliberately doesn't do:
- It doesn't say "you're £7 over", as if dinners were free.
- It doesn't suggest a "cheaper train" it hasn't found.
- It doesn't touch the booked hotel.

Once live prices exist, the stay's nearby dates (WS4) and other trains become real levers, each with its own quote.

## Currencies

- Each line keeps its own currency. The total is in the person's home currency (GBP now).
- A line in another currency is added only when a rate is given with its source and date, and the summary names it: "A museum in Paris, EUR at 0.85 (source, date)". Without a rate, it's "Plus 44 EUR, not converted (no exchange rate set)".
- **The rate source is Abram's choice**: a free official daily rate or a paid feed. It's not researched in this session (UNVERIFIED), so none is named here.

## The screen (a spec; both apps; not built)

1. In a trip, below the days: "The trip's cost". The headline and up to five lines, as above. "See every line" opens the list grouped by status, each line with its source ("TfL's daily cap", "the booking", "a sample price").
2. "Your budget for this trip" (optional, a number), then the line against it and where it could move. The budget is the person's own, kept with the trip on the phone.
3. Per person / for the group: a two-way switch, defaulting to the group when more than one person travels.
4. Sample prices are always labelled, as everywhere in the app.

## Decisions for Abram

1. The exchange-rate source, when a second currency first matters (with WS3).
2. Whether to estimate dinners (a planning figure like lunch's £15, with its source), or keep them unknown.
3. When to build the screen: proposed after live prices, since every quote is a sample until then.

**Hours (GUESS):**
- **This step:** Claude ~2 h (the model, tests, this page).
- **The screen:** Claude ~6 h in both apps; Abram ~0.5 h to review.
