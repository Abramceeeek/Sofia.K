# The ODYS experience model: one vocabulary (sprint, 7 Nov 2026; m214)

**Decision.** ODYS plans **moments**, not places. A moment is a specific experience at a place, at a time, including how you arrive: you come out of South Kensington tube and walk out to the Natural History Museum (CLAUDE.md).

As ODYS grows to more places, sources and trips, the words below each mean one thing. Outside data supplies the place layer, never the moment. Nothing is ever recommended because it's popular.

## The words

| Word | Means | In the code | Not to be confused with |
|---|---|---|---|
| **Moment** | One specific experience at a place: the way in, what happens, the best time, what to notice, the features the model scores, the shot card. Rated after the visit; the unit of the model. Two kinds: a *moment* and an *area vibe* (a wander, at most one a day). Day and night versions share a group | `moments.Moment`, `brain/data/moments/*.yaml`, ids `m_…` and `a_…` | A place (one place can hold several moments) |
| **Experience** | Not a separate thing: **what happens** in a moment (`Moment.experience`). In product language it's always "the moment" | `Moment.experience`; WS3's "experience stop" is a planned moment | A second name for a moment, which is avoided |
| **Place** | Where a moment happens: its identity, location, hours, access and food claims, from sources, each fact checked, claimed or unknown | `places.PlaceRecord` (WS1); today a moment carries its place inline (`Moment.place`, with an `overture_id` field not yet used) | The onboarding's "places" and a trip's "anchors" (below) |
| **Onboarding place** | A well-known London place swiped "Loved it / Fine / Didn't enjoy it" to learn tastes; mapped to the moments there | `swipe_items.yaml`, `calibration.py` | A moment (a swipe is about the place as the person remembers it) |
| **Kind of place** | A category ("Big museums", "Parks and gardens") asked of visitors from abroad | `categories.yaml` | A place's category (WS1's next step is one short list used by both) |
| **Anchor** | Where a trip day starts or ends: the stay, a station, an airport | `tripdays.Place`, `arrivals.yaml` | A place with moments |
| **Stop** | Something at a time in a day: a moment, a lunch slot, or the person's own time. Only moments are rated | `planner.PlannedStop`, the apps' `Stop` (`rateable`, `mine`) | A moment (a stop is a moment *scheduled*) |
| **Leg** | Travel within a day: from a stop to the next, or from an anchor | `travel_min`, `tripdays.Leg` | A journey |
| **Day** | Stops in order, with legs, inside the person's hours; on a trip it also has its arrival or leaving legs | `dayplan.personal_plan`, `TripDayOut` | — |
| **Destination** | A city or town with its zone, currency, languages, calendar, travel and weather providers, and **coverage** (`checked` or `none`) | `places.Destination`, `data/destinations.yaml` | A place |
| **Journey** | Travel between destinations on a trip, with local times at each end | `itinerary.TransferSegment` (WS3) | A leg |
| **Trip** | Destinations joined by journeys, and their days; held on the phone | `Trip` in both apps; `itinerary.Trip` | — |

## Duplicates found, and what to do

1. **Two destination lists.**
   - `airports.yaml` holds the trips code's destinations: airport, start point and whether days can be planned.
   - `destinations.yaml` holds the WS1 registry: zone, currency, calendar and coverage.
   - A new test fails if their keys, countries or coverage ever disagree (`test_places.py`).
   - **Proposed:** one list, the registry, with the airport and start point moved into it. About 1 h. Do it before a second destination, so there's never a third list.
2. **Two "centres" of London.**
   - Charing Cross is Test B's start point (D104), used as the trips' start.
   - 51.5074, −0.1278 is used by sunset and the registry.
   - This isn't a bug: they do different jobs. They'll be named `start_point` and `centre` when the lists merge.
3. **"Place" used four ways:** a moment's place, a place record, an onboarding place, and a trip's anchor. The words above settle it. Rename in code only where it's touched next, never in a sweep.
4. **Categories twice:** visitors' kinds of place, and the cards' missing category. WS1's short category list serves both.
5. **"Experience":** it's the moment, so no new entity uses the word on its own.

## Keeping the moment the difference

- **Only ready moments are planned.** A place from any source, however well known, never becomes a stop without a written, checked moment card (D72, D91). Sources fill in the place layer: that a place exists, its hours, its access. The moment says why it's worth going and how to arrive.
- **Popularity is never a recommendation.**
  - The ranking is the person's own predicted feeling. The D113 nudge lowers cards that appear in many simulated plans; it never raises one.
  - Review counts, stars and guest scores are the provider's, shown as theirs, and rank nothing (WS4).
  - The benchmark (WS7) watches concentration: the Garden at 120 is in 39% of the synthetic personal plans. That's a reason to write more moments, not to rank by fame.
- **A moment's own facts outrank a source's.** A card's checked hours (with its date) win over a map tag. Where they disagree, both are shown with their dates until someone checks.
- **What a moment needs that no database has:** where you come from, the path in, the reveal, the best light, what to notice, and where to stand for the photo. That's why coverage grows city by city, by people who've been, not by import.

**Hours:** Claude ~1 h (this page and the guard test). The merge in point 1: ~1 h, before a second destination.
