import Foundation
import Observation
import SwiftUI

/// D120 (ODYS Trips): the three tabs. Trip is home (your day and your trips), Book is flights and stays for the current
/// trip, You is help, what the app has learned, and your data.
enum MainTab: Hashable {
    case trip, book, you
}

/// Where the Trip tab can go.
enum TripDest: Hashable {
    case day                       // the current day plan (screen 9)
    case trip(UUID)                // a trip's overview
    case tripDay(UUID, Int)        // one day of a trip
}

/// A link out, about to open: "You're going to Skyscanner", then "Did you book it?" when they come back.
struct Handoff: Identifiable {
    let id = UUID()
    let provider: String
    let url: URL
    let what: String               // "Return flight", "6 nights"
    let price: Double?             // the price found here, if it's from this provider's offer
    let searchedAt: Date?
    let choice: TripChoice         // what goes into the trip if they say yes
    var back = false               // they went, and came back
}

/// The Book tab: the search for the current trip, its filters and results. Filters are searched again on the Brain
/// (which keeps the provider's results for 15 minutes), a moment after the last change.
@MainActor
@Observable
final class BookState {
    enum Segment: Hashable { case flights, stays }

    var segment: Segment = .flights
    var flightFilters = FlightFilters()
    var stayFilters = StayFilters()
    var flights: FlightResults?
    var stays: StayResults?
    var loading = false
    var error: String?
    var showFilters = false
    var stayMap = false
    var handoff: Handoff?
    var showAirports = false
    var resultsFor: UUID?                  // the trip the results belong to
    @ObservationIgnored var task: Task<Void, Never>?

    func reset() {
        task?.cancel()
        segment = .flights
        flightFilters = FlightFilters()
        stayFilters = StayFilters()
        flights = nil
        stays = nil
        loading = false
        error = nil
        showFilters = false
        stayMap = false
        handoff = nil
        resultsFor = nil
    }
}

extension AppModel {
    // ---- Build 2: what comes before the first plan -----------------------------------------------------------

    /// People based in the UK see the blind pair as their first plan; visitors from abroad don't (D116).
    var needsPair: Bool { !isVisitor && !pairDone && plan == nil }

    /// The survey (about onboarding, so straight after it) and then the pair, before the tabs.
    var needsFirstRun: Bool { !client.demo && (!surveyDone || needsPair) }

    func sendSurvey(_ body: SurveyBody?) async {
        await run {
            if let body { try await self.client.survey(body) } else { await self.client.event("survey_skipped") }
            self.surveyDone = true
            UserDefaults.standard.set(true, forKey: "surveyDone")
        }
    }

    func startPair(_ intent: PairIntent) async {
        await run {
            self.pair = try await self.client.makePair(intent)
            if self.pair?.done == true { self.pairDone = true }
        }
    }

    /// The choice, "fits me" for each, and why. The Brain answers with the reveal and the chosen plan in full.
    func sendPairFeedback(chosen: String, fit1: Int, fit2: Int, why: String, voice: Bool) async {
        let text = why.trimmingCharacters(in: .whitespacesAndNewlines)
        await run {
            self.pair = try await self.client.pairFeedback(PairFeedback(chosen: chosen, fit1: fit1, fit2: fit2,
                                                                        why: text.isEmpty ? nil : text,
                                                                        inputMode: voice ? "voice" : "typed"))
        }
    }

    /// "Skip the comparison": never a dead end if the Brain can't make the pair. Counted, so the test knows.
    func skipPair() {
        pairDone = true
        UserDefaults.standard.set(true, forKey: "pairDone")
        showPair = false
        Task { await client.event("pair_skipped") }
    }

    /// After the reveal: the chosen plan becomes their day (Test C). No swap or regenerate on it, so the plan they
    /// judged is the plan they rate.
    func finishPair() {
        guard let chosen = pair?.chosen else { return }
        pairDone = true
        UserDefaults.standard.set(true, forKey: "pairDone")
        plan = chosen
        lastRequest = nil
        rated = []
        revealPlanId = chosen.id
        AppModel.cache(chosen, "plan.json")
        AppModel.cache(nil as PlanRequest?, "request.json")
        showPair = false
        tab = .trip
        var p = NavigationPath()
        p.append(TripDest.day)
        path = p
    }

    // ---- D120: trips ---------------------------------------------------------------------------------------------

    var currentTrip: Trip? { trips.first { $0.id == currentTripId } ?? trips.first }

    func findTrip(_ id: UUID) -> Trip? { trips.first { $0.id == id } }

    func save(_ trip: Trip) {
        if let i = trips.firstIndex(where: { $0.id == trip.id }) { trips[i] = trip } else { trips.insert(trip, at: 0) }
        AppModel.cache(trips, "trips.json")
    }

    func deleteTrip(_ id: UUID) {
        trips.removeAll { $0.id == id }
        if currentTripId == id { currentTripId = trips.first?.id }
        AppModel.cache(trips, "trips.json")
    }

    /// A blank trip for "Plan a trip": London, next Saturday, a weekend; the airport from the town or city they gave
    /// (never from nationality, and only if they're visiting from abroad); feelings from their answers.
    func newTrip() -> Trip {
        var t = Trip(start: Dates.isoDay.string(from: Dates.nextSaturday()), nights: 2)
        t.needFlight = profile.based == "abroad"
        t.feelings = Array(why.prefix(2))
        return t
    }

    /// "From your answers": the first airport matching the town or city they gave, if any.
    func guessOrigin(for trip: Trip) async -> Trip {
        var t = trip
        guard t.origin == nil, let city = profile.homeCity?.trimmingCharacters(in: .whitespaces), !city.isEmpty,
              let found = try? await client.places(city), let first = found.first else { return t }
        t.origin = first
        t.originGuessed = true
        return t
    }

    /// "Make my trip": plans the first days (up to 7) and keeps the trip on the phone. A one-day trip is also "your
    /// day", so it can be rated stop by stop.
    func makeTrip(_ draft: Trip) async -> Bool {
        var trip = draft
        var ok = false
        await run {
            let out = try await self.client.tripDays(self.daysRequest(trip, days: [], exclude: []))
            trip.days = out.days
            trip.used = out.used
            trip.daysFrom = out.start
            trip.daysStale = false
            self.save(trip)
            self.currentTripId = trip.id
            if self.book.resultsFor != trip.id { self.book.flights = nil; self.book.stays = nil }
            if trip.nights == 0, let day = out.days.first, day.plan != nil { self.useDay(trip, day) }
            await self.client.event("trip_made", ["nights": "\(trip.nights)", "flight": trip.needFlight ? "yes" : "no",
                                                  "adults": "\(trip.adults)", "feelings": trip.feelings.joined(separator: ",")])
            ok = true
        }
        return ok
    }

    /// A later day ("+ 3 more days, planned as you go"), without any moment the trip already has.
    func planDay(_ tripId: UUID, _ index: Int) async {
        guard var trip = findTrip(tripId) else { return }
        await run {
            let out = try await self.client.tripDays(self.daysRequest(trip, days: [index], exclude: trip.used))
            for d in out.days {
                trip.days.removeAll { $0.index == d.index }
                trip.days.append(d)
            }
            trip.days.sort { $0.index < $1.index }
            trip.used = out.used
            self.save(trip)
        }
    }

    /// The days again, from the chosen stay and around the flight's times.
    func replanDays(_ tripId: UUID) async {
        guard let trip = findTrip(tripId) else { return }
        var fresh = trip
        fresh.days = []
        fresh.used = []
        _ = await makeTrip(fresh)
    }

    /// D122: the person's hours and places a day, and how the trip starts and ends (flight, train or car).
    private func daysRequest(_ trip: Trip, days: [Int], exclude: [String]) -> TripDaysRequest {
        let ends = trip.ends
        return TripDaysRequest(destination: trip.destination, startDate: trip.start, nights: trip.nights,
                               feelings: trip.feelings, stay: trip.stay?.point, stayName: trip.stay?.title,
                               days: days, exclude: exclude, dayStart: trip.dayFrom, dayEnd: trip.dayTo,
                               stopsPerDay: trip.placesPerDay, travelLight: trip.travelLight,
                               arrive: ends.arrive, leave: ends.leave)
    }

    /// "Make this my day": a trip's day becomes the current plan, with "Now", rating, swap and regenerate.
    func useDay(_ trip: Trip, _ day: TripDayOut) {
        guard let dayPlan = day.plan else { return }
        let mine = Set(dayPlan.stops.map { $0.momentId.components(separatedBy: "#")[0] })
        let window = day.window ?? DayWindow(start: "10:00", end: "18:00", stops: dayPlan.stops.count)
        var request = PlanRequest(start: trip.stay?.point ?? AppConfig.start,
                                  startName: trip.daysFrom ?? AppConfig.startName, startTime: window.start,
                                  endTime: window.end, date: day.date, stops: max(2, min(window.stops, 6)), familiar: false)
        request.exclude = trip.used.filter { !mine.contains($0) }   // the trip's other days
        plan = dayPlan
        lastRequest = request
        rated = []
        swappedIn = nil
        AppModel.cache(dayPlan, "plan.json")
        AppModel.cache(request, "request.json")
        if remindersOn { Task { await Reminders.schedule(dayPlan, rated: []) } }
    }

    /// The person said they booked it (or saved it for later) on the provider's site.
    func keep(_ choice: TripChoice, in tripId: UUID) {
        guard var trip = findTrip(tripId) else { return }
        if choice.kind == "flight" { trip.flight = choice } else { trip.stay = choice }
        trip.daysStale = !trip.days.isEmpty
        save(trip)
        Task { await client.event("handoff_answer", ["kind": choice.kind, "provider": choice.provider,
                                                     "answer": choice.booked ? "booked" : "saved"]) }
    }

    // ---- the Book tab's search ---------------------------------------------------------------------------------

    /// Searches again a moment after the last change (filters, sort, segment), so a slider doesn't send a request
    /// for every step.
    func searchSoon(_ delay: Duration = .milliseconds(350)) {
        book.task?.cancel()
        book.task = Task { [weak self] in
            if delay > .zero { try? await Task.sleep(for: delay) }
            guard !Task.isCancelled, let self else { return }
            await self.search()
        }
    }

    func search() async {
        guard let trip = currentTrip else { return }
        if book.resultsFor != trip.id {
            book.flights = nil
            book.stays = nil
            book.resultsFor = trip.id
        }
        book.loading = true
        book.error = nil
        do {
            switch book.segment {
            case .flights:
                guard trip.needFlight, let origin = trip.origin else { break }
                let found = try await client.flights(FlightSearch(origin: origin.code, destination: trip.destination,
                                                                  departDate: trip.start, returnDate: trip.end,
                                                                  adults: trip.adults, filters: book.flightFilters))
                if !Task.isCancelled { book.flights = found }
            case .stays:
                guard trip.needStay else { break }
                let found = try await client.stays(StaySearch(destination: trip.destination, checkin: trip.start,
                                                              checkout: trip.end, adults: trip.adults,
                                                              rooms: max(1, (trip.adults + 1) / 2),
                                                              filters: book.stayFilters))
                if !Task.isCancelled { book.stays = found }
            }
        } catch {
            if !Task.isCancelled { book.error = AppModel.message(for: error) }
        }
        if !Task.isCancelled { book.loading = false }
    }

    func openHandoff(_ h: Handoff) {
        book.handoff = h
    }

    func handoffGo(_ openURL: OpenURLAction) {
        guard let h = book.handoff else { return }
        Task { await client.event("handoff_open", ["kind": h.choice.kind, "provider": h.provider]) }
        openURL(h.url)
        book.handoff?.back = true
    }

    // ---- CI screenshots ------------------------------------------------------------------------------------------

    static func demoTrip() -> Trip? {
        guard let days: TripDaysResponse = try? BrainClient.bundled("demo_trip_days"),
              let first = days.days.first else { return nil }
        var t = Trip(start: first.date, nights: days.totalDays - 1)
        t.origin = TripPlace(code: "TAS", city: "Tashkent", name: "Tashkent Islam Karimov", country: "UZ")
        t.originGuessed = true
        t.feelings = ["curious", "peaceful"]
        t.hoursFrom = "09:30"                                   // D122: the demo trip's own day (make_demo.py)
        t.hoursTo = "19:00"
        t.places = 3
        t.light = true
        t.days = days.days
        t.used = days.used
        t.daysFrom = days.start
        if let flights: FlightResults = try? BrainClient.bundled("demo_flights"), let f = flights.results.first {
            t.flight = TripChoice(kind: "flight", title: "\(f.airline) · \(f.outbound.departTime) → \(f.outbound.arriveTime)",
                                  provider: "Skyscanner", price: f.price, booked: false, arriveTime: f.outbound.arriveTime,
                                  leaveTime: f.inbound?.departTime, arrivePlace: "LHR", leavePlace: "LHR")
        }
        if let stays: StayResults = try? BrainClient.bundled("demo_stays"), let s = stays.results.first {
            t.stay = TripChoice(kind: "stay", title: s.name, provider: "Booking.com", price: s.priceTotal, booked: true,
                                point: s.point)
        }
        return t
    }

    /// "Good morning", in London time.
    static var greeting: String {
        let h = Calendar.london.component(.hour, from: .now)
        return h < 12 ? "Good morning" : (h < 18 ? "Good afternoon" : "Good evening")
    }
}
