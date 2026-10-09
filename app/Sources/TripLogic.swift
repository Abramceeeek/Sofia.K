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

/// Journey audit (7 Oct): a hand-off the person is on, kept on the phone while they're on the provider's site, so
/// "Did you book it?" still comes if iOS closes the app meanwhile. Asked once at the next open, then removed.
struct SavedHandoff: Codable {
    let provider: String
    let url: URL
    let what: String
    let price: Double?
    let searchedAt: Date?
    let choice: TripChoice
    let tripId: UUID
    let at: Date
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
        if surveyDone, isVisitor, plan == nil, !client.demo { await visitorFirstDay() }
    }

    /// m176: visitors skip the Test B pair, so they'd reach the tabs with nothing made for them. A first London day
    /// from their answers (next Saturday afternoon, from the centre) shows the value at once; "Plan a trip" sets their
    /// real dates. Visitors stay outside the Test B analysis (D116).
    func visitorFirstDay() async {
        let saturday = Dates.nextSaturday()
        await makePlan(date: saturday, start: Dates.time(12), end: Dates.time(17), stops: 4)
        guard plan != nil else { return }
        await client.event("visitor_first_day")
        tab = .trip
        var p = NavigationPath()
        p.append(TripDest.day)
        path = p
    }

    func startPair(_ intent: PairIntent) async {
        await run {
            self.pair = try await self.client.makePair(intent)
            // journey round 2: answered before (the app closed on the reveal): their plan, not a dead end
            if self.pair?.done == true {
                if self.pair?.chosen != nil { self.finishPair() } else { self.skipPair() }
            }
        }
    }

    /// The choice, "fits me" for each, and why. The Brain answers with the reveal and the chosen plan in full.
    func sendPairFeedback(chosen: String, fit1: Int, fit2: Int, why: String, voice: Bool) async {
        let text = why.trimmingCharacters(in: .whitespacesAndNewlines)
        await run {
            do {
                self.pair = try await self.client.pairFeedback(PairFeedback(chosen: chosen, fit1: fit1, fit2: fit2,
                                                                            why: text.isEmpty ? nil : text,
                                                                            inputMode: voice ? "voice" : "typed"))
            } catch BrainError.status(409) {
                self.pair = try await self.client.pair()   // journey round 2: sent before, but the answer was lost
            }
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
        UserDefaults.standard.set(chosen.id, forKey: "testBPlanId")   // m176: replacing it unrated asks first
        (rated, myRatings) = AppModel.savedRatings(for: chosen)
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
        if profile.based == "uk" {   // journey round 2: elsewhere in the UK, not "already in London"
            t.travelBy = "train"
            t.station = "KGX"
            t.arriveAt = "11:00"
            t.leaveAt = "17:00"
        }
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
    /// Journey round 2: `keepFrom`, the trip as it was before an edit. Days already lived (and, with `keepChanged`,
    /// days changed by hand) stay as they were when the dates are the same; only the rest is planned again.
    func makeTrip(_ draft: Trip, keepFrom old: Trip? = nil, keepChanged: Bool = true) async -> Bool {
        var trip = draft
        var ok = false
        // Written with constants only: the release build's optimiser crashed on a captured `var` here (build 60)
        let today = Dates.isoDay.string(from: .now)
        let sameDates = old.map { $0.start == draft.start && $0.nights == draft.nights } ?? false
        let changed: Set<Int> = sameDates && keepChanged ? Set(old?.changedDays ?? []) : []
        let kept: [TripDayOut] = sameDates ? (old?.days ?? []).filter { $0.date < today || changed.contains($0.index) } : []
        trip.changedDays = sameDates ? old?.changedDays?.filter { changed.contains($0) } : nil
        let keptIndex = Set(kept.map(\.index))
        let todo = Array((0..<draft.dayCount).filter { !keptIndex.contains($0) }.prefix(7))
        let exclude = AppModel.momentBases(kept)
        let currentPlanId = plan?.id
        let yourDayIndex = old?.days.first(where: { currentPlanId != nil && $0.plan?.id == currentPlanId })?.index
        await run {
            if kept.isEmpty || !todo.isEmpty {
                let out = try await self.client.tripDays(self.daysRequest(trip, days: kept.isEmpty ? [] : todo,
                                                                          exclude: exclude))
                trip.days = (kept + out.days).sorted { $0.index < $1.index }
                trip.used = out.used
                trip.daysFrom = out.start
            }
            trip.daysStale = false
            self.save(trip)
            // "your day" follows its day when that day was planned again
            if let i = yourDayIndex, !keptIndex.contains(i),
               let day = trip.days.first(where: { $0.index == i }), day.plan != nil {
                self.useDay(trip, day)
            }
            self.currentTripId = trip.id
            if self.book.resultsFor != trip.id { self.book.flights = nil; self.book.stays = nil }
            if trip.nights == 0, let day = trip.days.first, day.plan != nil { self.useDay(trip, day) }
            await self.client.event("trip_made", ["nights": "\(trip.nights)", "flight": trip.needFlight ? "yes" : "no",
                                                  "adults": "\(trip.adults)", "feelings": trip.feelings.joined(separator: ",")])
            ok = true
        }
        return ok
    }

    /// The cards (not their lunch versions) in these days' plans and places on the way.
    static func momentBases(_ days: [TripDayOut]) -> [String] {
        var out = Set<String>()
        for day in days {
            for stop in (day.plan?.stops ?? []) + (day.before?.stops ?? []) where stop.rateable {
                out.insert(stop.momentId.components(separatedBy: "#")[0])
            }
        }
        return out.sorted()
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
        _ = await makeTrip(trip, keepFrom: trip, keepChanged: false)   // journey round 2: days already lived stay
    }

    /// D122: the person's hours and places a day, and how the trip starts and ends (flight, train or car).
    /// `hours`: one day's own hours and places, when the person changes that day (else the trip's).
    private func daysRequest(_ trip: Trip, days: [Int], exclude: [String],
                             hours: (from: String, to: String, places: Int)? = nil) -> TripDaysRequest {
        let ends = trip.ends
        return TripDaysRequest(destination: trip.destination, startDate: trip.start, nights: trip.nights,
                               feelings: trip.feelings, stay: trip.stay?.point, stayName: trip.stay == nil ? nil : "your stay",
                               days: days, exclude: exclude, dayStart: hours?.from ?? trip.dayFrom,
                               dayEnd: hours?.to ?? trip.dayTo, stopsPerDay: hours?.places ?? trip.placesPerDay,
                               travelLight: trip.travelLight, arrive: ends.arrive, leave: ends.leave)
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
        request.feelings = trip.feelings.isEmpty ? nil : trip.feelings   // journey round 2: as the trip planned it
        plan = dayPlan
        lastRequest = request
        (rated, myRatings) = AppModel.savedRatings(for: dayPlan)   // a day used before keeps its ratings
        swappedIn = nil
        AppModel.cache(dayPlan, "plan.json")
        AppModel.cache(request, "request.json")
        let done = rated
        if remindersOn { Task { await Reminders.schedule(dayPlan, rated: done) } }
    }

    /// m176: the plan chosen in the Test B comparison, not rated yet, for today or later. Replacing it asks first,
    /// because rating it on a real day is what the test needs most.
    var testBPlanAtRisk: Bool {
        guard let plan, !client.demo, plan.id == UserDefaults.standard.integer(forKey: "testBPlanId"), rated.isEmpty
        else { return false }
        return (plan.date ?? "") >= Dates.isoDay.string(from: .now)
    }

    // ---- journey audit (7 Oct): the trip carried day by day ---------------------------------------------------

    /// During a trip: today's day (planned or not), unless today's plan is already "your day".
    var todayInTrip: (trip: Trip, index: Int, day: TripDayOut?)? {
        let today = Dates.isoDay.string(from: .now)
        if client.demo || plan?.date == today { return nil }   // the CI screenshots stay the same whatever the date
        for trip in trips {
            guard let i = Calendar.london.dateComponents([.day], from: trip.startDate,
                                                         to: Dates.isoDay.date(from: today) ?? .now).day,
                  (0..<trip.dayCount).contains(i) else { continue }
            return (trip, i, trip.days.first { $0.index == i })   // journey round 2: a travel day too
        }
        return nil
    }

    /// The trip day the current plan is (m176: "Now" shows its journeys at each end).
    var currentTripDay: (trip: Trip, day: TripDayOut)? {
        guard let plan else { return nil }
        for trip in trips {
            if let d = trip.days.first(where: { $0.plan?.id == plan.id }) { return (trip, d) }
        }
        return nil
    }

    /// At the end of a trip's day ("That's the day"): the next day of the same trip, if there is one (planned or not;
    /// a travel day home has journeys but no plan).
    var nextTripDay: (trip: Trip, index: Int, day: TripDayOut?)? {
        guard let plan else { return nil }
        for trip in trips {
            guard let current = trip.days.first(where: { $0.plan?.id == plan.id })
                    ?? (trip.id == currentTripId ? trip.days.first(where: { $0.date == plan.date }) : nil) else { continue }
            let i = current.index + 1
            guard i < trip.dayCount else { return nil }
            return (trip, i, trip.days.first { $0.index == i })
        }
        return nil
    }

    /// Abram's comment (8 Oct): the trip day dated tomorrow, to look at ahead of time (the evening before, too).
    var tomorrowInTrip: (trip: Trip, index: Int, day: TripDayOut?)? {
        guard !client.demo,
              let tomorrow = Calendar.london.date(byAdding: .day, value: 1, to: Calendar.london.startOfDay(for: .now))
        else { return nil }
        for trip in trips {
            guard let i = Calendar.london.dateComponents([.day], from: trip.startDate, to: tomorrow).day,
                  (0..<trip.dayCount).contains(i) else { continue }
            return (trip, i, trip.days.first { $0.index == i })
        }
        return nil
    }

    /// Plans a later day first, if it's one of the "as you go" days not planned yet.
    func planTripDayIfNeeded(_ tripId: UUID, _ index: Int) async {
        if findTrip(tripId)?.days.contains(where: { $0.index == index }) != true { await planDay(tripId, index) }
    }

    /// Opens one day of a trip on the Trip tab, to look at (and change) before it's "your day".
    func openTripDay(_ tripId: UUID, _ index: Int, from source: String) {
        tab = .trip
        var p = NavigationPath()
        p.append(TripDest.trip(tripId))
        p.append(TripDest.tripDay(tripId, index))
        path = p
        Task { await client.event("trip_day_previewed", ["from": source, "day": "\(index + 1)"]) }
    }

    /// Abram's comment (8 Oct): one day planned again at the hours the person is free and with their places, around
    /// plans they've made. The trip's other days keep their places; this day may keep some of its own. If it was
    /// "your day", the new plan becomes your day.
    func changeTripDay(_ tripId: UUID, _ index: Int, from: String, to: String, places: Int) async -> Bool {
        guard var trip = findTrip(tripId) else { return false }
        let old = trip.days.first { $0.index == index }
        let base = { (p: Plan?) in (p?.stops ?? []).filter(\.rateable).map { $0.momentId.components(separatedBy: "#")[0] } }
        let own = Set(base(old?.plan) + base(old?.before))
        let request = daysRequest(trip, days: [index], exclude: trip.used.filter { !own.contains($0) },
                                  hours: (from, to, places))
        var ok = false
        await run {
            let out = try await self.client.tripDays(request)
            guard let new = out.days.first(where: { $0.index == index }) else { return }
            trip.days.removeAll { $0.index == index }
            trip.days.append(new)
            trip.days.sort { $0.index < $1.index }
            trip.used = out.used
            trip.changedDays = Array(Set((trip.changedDays ?? []) + [index])).sorted()   // kept on a re-plan
            self.save(trip)
            if let was = old?.plan, self.plan?.id == was.id, new.plan != nil { self.useDay(trip, new) }
            await self.client.event("trip_day_changed", ["day": "\(index + 1)", "from": from, "to": to,
                                                         "places": "\(places)"])
            ok = true
        }
        return ok
    }

    /// "Start today's day" / "Tomorrow: Day 3": plans the day first if it's one of the later, "as you go" days.
    func goToTripDay(_ tripId: UUID, _ index: Int) async {
        if findTrip(tripId)?.days.first(where: { $0.index == index })?.plan == nil { await planDay(tripId, index) }
        guard let trip = findTrip(tripId), let day = trip.days.first(where: { $0.index == index }), day.plan != nil else { return }
        currentTripId = trip.id
        useDay(trip, day)
        Task { await client.event("trip_day_started", ["day": "\(index + 1)", "of": "\(trip.dayCount)"]) }
    }

    /// The person said they booked it (or saved it for later) on the provider's site.
    func keep(_ choice: TripChoice, in tripId: UUID) {
        guard var trip = findTrip(tripId) else { return }
        var choice = choice
        if choice.kind == "flight", choice.landsNextDay == true, trip.nights >= 1 {
            // journey round 2: an overnight flight lands the next day; the trip's days start then (the flight home
            // stays on the same last day), so day 1 isn't planned while they're in the air
            trip.start = Dates.isoDay.string(from: Calendar.london.date(byAdding: .day, value: 1, to: trip.startDate) ?? trip.startDate)
            trip.nights -= 1
            notice = ("Your trip now starts on \(Dates.shortDay(trip.start))",
                      "That's the day your flight lands, so your first day starts when you arrive. Plan the days again from the trip.")
        }
        choice.forStart = trip.start          // journey audit: so a later change of dates is noticed
        choice.forNights = trip.nights
        if choice.kind == "flight" { trip.flight = choice } else { trip.stay = choice }
        AppModel.cache(nil as SavedHandoff?, "handoff.json")   // answered: nothing left to ask after a restart
        trip.daysStale = !trip.days.isEmpty
        save(trip)
        Task { await client.event("handoff_answer", ["kind": choice.kind, "provider": choice.provider,
                                                     "answer": choice.booked ? "booked" : "saved"]) }
    }

    /// m176: after "Swap this stop" or "Regenerate" on a trip's day, the trip keeps the new day, so its day page and
    /// "Make this my day" don't bring the old stops back. Only when the plan being changed is that trip day's plan.
    func syncTripDay(from old: Plan?, to new: Plan) {
        guard let old, var trip = trips.first(where: { $0.days.contains { $0.plan?.id == old.id } }),
              let i = trip.days.firstIndex(where: { $0.plan?.id == old.id }) else { return }
        let d = trip.days[i]
        trip.days[i] = TripDayOut(index: d.index, date: d.date, kind: d.kind, title: d.title, plan: new,
                                  window: d.window, before: d.before, legs: d.legs)
        let base = { (p: Plan) in Set(p.stops.filter(\.rateable).map { $0.momentId.components(separatedBy: "#")[0] }) }
        trip.used = Array(Set(trip.used).subtracting(base(old)).union(base(new))).sorted()
        save(trip)
    }

    /// m176: "Remove this flight / stay from the trip". Anything booked stays booked on the provider's site; the days
    /// are marked to plan again, since they started from the stay or the flight's times.
    func removeChoice(_ kind: String, from tripId: UUID) {
        guard var trip = findTrip(tripId) else { return }
        if kind == "flight" { trip.flight = nil } else { trip.stay = nil }
        trip.daysStale = !trip.days.isEmpty
        save(trip)
        Task { await client.event("choice_removed", ["kind": kind]) }
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
        book.error = nil
        if trip.start < Dates.isoDay.string(from: .now) {   // journey round 2: the Brain only searches from today
            book.error = "This trip has started, so there's nothing to search for its dates. To change a flight or add a night, use the airline's or the stay's own site."
            return
        }
        book.loading = true
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
        if let trip = currentTrip {
            AppModel.cache(SavedHandoff(provider: h.provider, url: h.url, what: h.what, price: h.price,
                                        searchedAt: h.searchedAt, choice: h.choice, tripId: trip.id, at: .now),
                           "handoff.json")
        }
    }

    /// At the next open: the question they didn't get to answer, for a hand-off in the last day.
    func restoreHandoff() {
        guard let saved = AppModel.loadCached(SavedHandoff.self, "handoff.json") else { return }
        AppModel.cache(nil as SavedHandoff?, "handoff.json")
        guard route == .home, Date.now.timeIntervalSince(saved.at) < 24 * 3600, findTrip(saved.tripId) != nil else { return }
        currentTripId = saved.tripId
        tab = .book
        book.handoff = Handoff(provider: saved.provider, url: saved.url, what: saved.what, price: saved.price,
                               searchedAt: saved.searchedAt, choice: saved.choice, back: true)
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
