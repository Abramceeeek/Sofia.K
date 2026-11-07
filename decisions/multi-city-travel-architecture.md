# Trips through several places (WS3, 7 Nov 2026; m210)

**Decision (proposed).** A trip becomes a list of **places** (destination segments), each with its nights and its stay, joined by **journeys** (transfer segments) whose times are local at each end. Each place is planned by **the same trip-days planner as today**, one request per place:
- the journey in is that place's arrival;
- the journey out is its leaving;
- moments planned elsewhere in the trip are excluded.

**No second planner, no server migration.** The Brain keeps no trips. The phone holds the trip and asks for days, so the change lives in the apps' saved trip and in one new Brain module.

**A trip with one place is exactly today's trip.** The module is built and tested (`brain/src/brain/itinerary.py`, 6 tests with a 10-day European example), but not wired into the API or the apps. Building it into the product is after the friends' round (product-direction.md: "later").

## The entities

| Entity | What it holds | Today |
|---|---|---|
| **Trip** | first day, places, journeys, the journey in from home and the journey home | `Trip` on the phone: one destination, `start`, `nights`, a flight or train in and out |
| **DestinationSegment** | a destination key, its first day, nights (in a bed, not on a sleeper), its stay | The whole trip |
| **TransferSegment** | from, to, mode (flight, train, bus, car, ferry), **local** departure and arrival times, booked or planned | Only in and out of London (`TripEndIn`: flight, train, car) |
| **AccommodationStay** | name, check-in, check-out (must match the nights) | `Trip.stay` |
| **TripDay** | date, kind (arrival, full, transfer, on board, departure, gap), where the person is, what the day says, the journeys it holds | `TripDayOut`, per day |
| **ExperienceStop** | a planned moment | The planner's stop: unchanged |
| **PersonalTimeBlock** | the person's own time | `dayplan.Block`: unchanged |
| **ArrivalDepartureEvent** | the legs at either end of a day | `tripdays.Leg`, from `TripEndIn`: unchanged |

Everything that varies by place comes from the destination registry (WS1): time zone, currency, languages, bank-holiday region, travel and weather providers, and coverage.

## How a trip becomes days (`itinerary.days`)

- **The first day of each place is its arrival.** The journey in is said in local time: "Arrive in Paris at 14:20 (Paris time), after 2 h 20 min."
- **The day you move is one day, a "transfer"**: the morning in the old place until you leave, the evening in the new one. One request to the planner covers each side: the old place's leaving day and the new place's arrival.
- **An overnight journey makes two days:** the leaving day ("You sleep on board tonight.") and the next day's arrival in the new place. The night on board isn't a night in either stay.
- **A missing journey is a "gap" day**, "How you get from London to Paris isn't set yet, so this day is planned only until midday", never an invented train.
- **Places without checked coverage** keep their structure (arriving, leaving, the stay) and get no planned places. Today that is every place but London (WS1, E in product-direction.md).

## The hard cases

| Case | How it's handled | Tested |
|---|---|---|
| **Time zones** | Departures are in the origin's zone, arrivals in the destination's. Durations come from the two instants: 11:00 London to 14:20 Paris is 2 h 20, not 3 h 20 | Yes |
| **Clock changes** | The same: 23:00 in London on Sat 24 Oct 2026 to 07:00 in Paris after the clocks go back is 8 h, though the wall clocks alone would say 7 | Yes |
| **Overnight trains** | Two days, a night on board, no stay that night; the dates must fit together ("…after the night on board") | Yes |
| **Missing transport** | A gap day that says what's missing | Yes |
| **Dates that don't fit** | Said in plain words: "Paris starts on Mon 26 Oct, but after London it would be Sun 25 Oct." Also a journey that arrives before it leaves (times entered in the wrong zone), and a stay whose nights don't match | Yes |
| **Delays** | A late journey changes only the days that hold it: the leaving day, and the arrival day (the next day, after a night train). `affected_days` gives them, so only those are planned again | Yes |
| **Changing one place** | Only that place's days and the journeys in and out of it are planned again. Changing Amsterdam touches Paris's leaving day, Amsterdam's own day and Vienna's arrival after the night train out of it; every other day is kept (as `changedDays` already keeps days changed by hand) | Yes |
| **Currencies** | Each place has its own currency (registry). Totals across currencies are WS6 | — |
| **Buses and ferries** | The planner's arrival legs know flights, trains and cars. A bus or ferry gives the day no arrival leg: it starts at the stay and says so, never pretending it's a train | By design |
| **Moments twice** | Moments planned in other places are excluded per request (D121 across the trip) | Yes |

## A 10-day European example (illustrative times, not a timetable)

Thu 22 – Sat 31 Oct 2026; 9 nights; the clocks go back on Sun 25 Oct.

| Day | Date | Kind | Where | What the day says |
|---|---|---|---|---|
| 1 | Thu 22 | arrival | London | Arrive at 10:00 (flight in) |
| 2–3 | Fri 23 – Sat 24 | full | London | Planned days (checked coverage) |
| 4 | Sun 25 | transfer | London → Paris | Leave London by train at 11:00 (London time). Arrive in Paris at 14:20 (Paris time), after 2 h 20 min |
| 5–6 | Mon 26 – Tue 27 | full | Paris | "Day plans aren't ready for Paris yet": the days have a structure but no places |
| 7 | Wed 28 | transfer | Paris → Amsterdam | 10:00 to 13:20 |
| 8 | Thu 29 | transfer | Amsterdam, then on board | Leave Amsterdam by train at 19:00. You sleep on board tonight |
| 9 | Fri 30 | arrival | Vienna | Arrive in Vienna at 09:00, after 14 h 00 min |
| 10 | Sat 31 | departure | Vienna | Flight home at 15:00 |

Nights: London 3, Paris 3, Amsterdam 1, on board 1, Vienna 1. Currencies: GBP, then EUR. Only London's days get places today. The rest of the trip is still useful (journeys, stays, the shape of each day), and it says plainly what it doesn't plan.

## Moving the apps to it, without breaking saved trips

1. The phone's `Trip` gets an optional `segments` list (Codable and kotlinx with defaults, as `personal` was added in m200). A trip saved without it is read as one segment from `destination`, `start`, `nights`, `stay` and the flight or train in and out. No migration runs: old trips simply open.
2. "Plan the days" sends one `trip_days` request per place with checked coverage (`itinerary.segment_requests`, which already produces the request fields), and joins the answers by date.
3. New screens: "Add another place" after the first place's nights; the journey between (with "I'll sort this later" giving a gap day); each place's own stay. Both apps.

**Hours (GUESS):** Brain wiring and tests ~3 h; both apps ~12 h; Abram's review ~1 h. After the friends' round, and only once a second place has checked coverage, since before that every added place would have no planned days.

**This step:** Claude ~2.5 h (the module, 6 tests, this page).
