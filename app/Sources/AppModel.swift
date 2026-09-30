import Foundation
import Observation

enum AppConfig {
    /// The Brain's address, from Info.plist (`BrainBaseURL` in project.yml).
    static var baseURL: URL {
        let raw = Bundle.main.object(forInfoDictionaryKey: "BrainBaseURL") as? String ?? ""
        return URL(string: raw) ?? URL(string: "https://moments-brain.onrender.com")!
    }
    static let consentVersion = "app-2026-09"
    static let contactEmail = "abram@abdurakhmonbek.com"
    /// Build 1 plans from the Test B start point (D104): Charing Cross station, Trafalgar Square exit (TfL).
    static let startName = "Charing Cross station"
    static let start = Point(lat: 51.507819, lon: -0.126137)
    /// CI screenshots: `-demo YES -screen plan` (launch arguments land in UserDefaults).
    static var demo: Bool { UserDefaults.standard.bool(forKey: "demo") }
    static var screen: String? { UserDefaults.standard.string(forKey: "screen") }
}

enum Route: Hashable {
    case welcome, example, consent, onboarding, home   // D112: an example day before consent
}

/// Onboarding up to the first plan (screens 3–6). D110: "about you" and photos moved after the first plan.
enum Step: Int, CaseIterable {
    case bestHour, why, places, thisOrThat

    /// CI screenshots: `-screen places` opens that onboarding step.
    static func forScreen(_ name: String?) -> Step? {
        ["besthour": .bestHour, "why": .why, "places": .places, "thisorthat": .thisOrThat][name ?? ""]
    }

    var title: String {
        switch self {
        case .bestHour: return "A great moment"
        case .why: return "Why you go out"
        case .places: return "Places you've been"
        case .thisOrThat: return "This or that"
        }
    }
}

/// The non-personal example day shown before consent (D112), bundled so it needs no network.
enum ExampleDay {
    static let plan: Plan? = try? BrainClient.bundled("example_day")
}

@MainActor
@Observable
final class AppModel {
    var route: Route
    var step: Step = .bestHour
    var onboarding: Onboarding?
    var plan: Plan?
    var busy = false
    var waking = false
    var errorMessage: String?

    // Answers, kept until each step is sent
    var bestHour = ""
    var bestHourMore = ""
    var why: [String] = []
    var reactions: [Int: String] = [:]
    var choices: [Int: String] = [:]
    var profile = Profile()
    var rated: Set<String> = []            // moment ids rated in this plan
    var improved = UserDefaults.standard.bool(forKey: "improved")
    var morePlacesDone = UserDefaults.standard.bool(forKey: "morePlacesDone")   // D112: the 4 later places
    var moreTasksDone = UserDefaults.standard.bool(forKey: "moreTasksDone")     // and the 5 later tasks
    var swappedIn: String?                 // the stop the last swap brought in, marked on the plan
    var lastRequest: PlanRequest?

    let client: BrainClient
    let screen: String?

    init() {
        let demo = AppConfig.demo
        let brain = BrainClient(base: AppConfig.baseURL, demo: demo)
        let screen = demo ? AppConfig.screen : nil
        client = brain
        self.screen = screen
        if demo {
            route = .home
            onboarding = try? BrainClient.bundled("demo_onboarding")
            let demoPlan: Plan? = try? BrainClient.bundled("demo_plan")
            plan = demoPlan
            step = Step.forScreen(screen) ?? .bestHour
            lastRequest = PlanRequest(start: AppConfig.start, startName: AppConfig.startName, startTime: "12:00",
                                      endTime: "17:00", date: demoPlan?.date, stops: 4, familiar: true)
        } else if brain.token == nil {
            route = .welcome
        } else {
            route = UserDefaults.standard.bool(forKey: "onboardingDone") ? .home : .onboarding
            plan = AppModel.loadCached(Plan.self, "plan.json")
            lastRequest = AppModel.loadCached(PlanRequest.self, "request.json")
        }
    }

    // ---- running a call, with the "waking up" note after 3 s --------------------------------

    func run(_ work: @escaping @MainActor () async throws -> Void) async {
        busy = true
        errorMessage = nil
        let note = Task { [weak self] in
            try? await Task.sleep(for: .seconds(3))
            if !Task.isCancelled { self?.waking = true }
        }
        do {
            try await work()
        } catch {
            errorMessage = AppModel.message(for: error)
        }
        note.cancel()
        waking = false
        busy = false
    }

    /// What went wrong, in words a person can act on. A cancelled call (the screen moved on) is not an error.
    static func message(for error: Error) -> String? {
        if error is CancellationError { return nil }
        if let e = error as? URLError {
            switch e.code {
            case .cancelled:
                return nil
            case .timedOut:
                return "The planner took too long to answer. It may still be waking up, so try again in a minute."
            case .notConnectedToInternet, .networkConnectionLost, .dataNotAllowed:
                return "You seem to be offline. Check your connection and try again."
            default:
                return "Couldn't reach the planner (error \(e.code.rawValue)). Check your connection and try again."
            }
        }
        if error is DecodingError {
            return "The app couldn't read the planner's answer. Please update the app in TestFlight."
        }
        return (error as? LocalizedError)?.errorDescription ?? "Something unexpected happened. Please try again."
    }

    // ---- first run ---------------------------------------------------------------------------

    /// Registers the phone, then shows onboarding, which loads its own questions (one request, one place).
    func agree() async {
        await run {
            try await self.client.install(research: true)
            self.route = .onboarding
        }
    }

    func loadOnboarding() async throws {
        if onboarding == nil { onboarding = try await client.onboarding() }
    }

    // ---- onboarding: each step is sent as it finishes -------------------------------------------

    func next() {
        if let n = Step(rawValue: step.rawValue + 1) { step = n }
    }

    func finishBestHour() async {
        await run {
            var items: [AnswerItem] = []
            let first = self.bestHour.trimmingCharacters(in: .whitespacesAndNewlines)
            let more = self.bestHourMore.trimmingCharacters(in: .whitespacesAndNewlines)
            if !first.isEmpty { items.append(AnswerItem(question: "best_hour", text: first, inputMode: "typed")) }
            if !more.isEmpty { items.append(AnswerItem(question: "best_hour_more", text: more, inputMode: "typed")) }
            if !items.isEmpty { try await self.client.sendAnswers(items) }
            self.next()
        }
    }

    /// Sends the reactions to these places (unanswered ones, after "Skip the rest", are simply not sent).
    private func sendReactions(_ places: [SwipePlace]) async throws {
        let items = places.compactMap { p in reactions[p.item].map { SwipeItem(item: p.item, reaction: $0) } }
        if !items.isEmpty { try await client.sendSwipes(items) }
    }

    private func sendChoices(_ tasks: [ConjointTask]) async throws {
        let items = tasks.compactMap { t in choices[t.task].map { ChoiceItem(task: t.task, choice: $0) } }
        if !items.isEmpty { try await client.sendChoices(items) }
    }

    func finishPlaces() async {
        await run {
            try await self.sendReactions(self.onboarding?.swipePlaces ?? [])
            self.next()
        }
    }

    /// "Improve future plans": the places and tasks not asked before the first plan (D112).
    func finishMorePlaces() async {
        await run {
            try await self.sendReactions(self.onboarding?.swipePlacesLater ?? [])
            self.morePlacesDone = true
            UserDefaults.standard.set(true, forKey: "morePlacesDone")
        }
    }

    func finishMoreTasks() async {
        await run {
            try await self.sendChoices(self.onboarding?.conjointTasksLater ?? [])
            self.moreTasksDone = true
            UserDefaults.standard.set(true, forKey: "moreTasksDone")
        }
    }

    /// The last onboarding step: straight on to the first plan (D110).
    func finishThisOrThat() async {
        profile.whyTravel = why
        await run {
            try await self.sendChoices(self.onboarding?.conjointTasks ?? [])
            try await self.client.sendProfile(self.profile)
            UserDefaults.standard.set(true, forKey: "onboardingDone")
            await self.client.event("onboarding_done")
            self.route = .home
        }
    }

    /// "Improve future plans": saved when the person taps Save; `done` marks the step as finished.
    func saveImprovements(done: Bool) async {
        profile.whyTravel = why
        await run {
            try await self.client.sendProfile(self.profile)
            if done {
                self.improved = true
                UserDefaults.standard.set(true, forKey: "improved")
                await self.client.event("improve_done")
            }
        }
    }

    // ---- plans and ratings ------------------------------------------------------------------------

    func makePlan(date: Date, start: Date, end: Date, stops: Int) async {
        let day = Dates.isoDay.string(from: date)
        let request = PlanRequest(start: AppConfig.start, startName: AppConfig.startName,
                                  startTime: Dates.hhmm.string(from: start), endTime: Dates.hhmm.string(from: end),
                                  date: day, stops: stops, familiar: true)
        await fetchPlan(request)
    }

    /// The same day again, e.g. after "Improve future plans": no stops kept, nothing left out.
    func replan() async {
        guard var request = lastRequest else { return }
        request.keep = []
        request.exclude = []
        await fetchPlan(request)
    }

    /// "Regenerate plan" (D112): the same day with none of the current stops; the Brain falls back to the best day
    /// if nothing new fits. Off in the blind Test B comparison (Build 2).
    func regenerate() async {
        guard var request = lastRequest, let current = plan else { return }
        request.keep = []
        request.exclude = Array(Set(request.exclude + current.stops.filter(\.rateable).map(\.momentId))).sorted()
        await fetchPlan(request)
        await client.event("regenerate_plan")
    }

    /// "Swap this stop" (D110): the other stops stay; this card, and any swapped out before, are left out.
    func swap(_ stop: Stop) async {
        guard var request = lastRequest, let current = plan else { return }
        request.keep = current.stops.filter { $0.id != stop.id }.map { $0.key ?? $0.momentId }
        request.exclude.append(stop.momentId)
        let before = Set(current.stops.map(\.momentId))
        await fetchPlan(request, swap: true)
        if let now = plan, now.id != current.id {
            swappedIn = now.stops.first { !before.contains($0.momentId) }?.momentId
            await client.event("swap_stop", ["out": stop.momentId, "in": swappedIn ?? ""])
        }
    }

    private func fetchPlan(_ request: PlanRequest, swap: Bool = false) async {
        await run {
            let plan = try await self.client.makePlan(request)
            self.plan = plan
            self.lastRequest = request
            if !swap {
                self.rated = []
                self.swappedIn = nil
            }
            AppModel.cache(plan, "plan.json")
            AppModel.cache(request, "request.json")
        }
    }

    func rate(_ stop: Stop, rating: Int, wouldBring: Bool?) async {
        await run {
            try await self.client.rate(RatingRequest(momentId: stop.momentId, rating: rating, planId: self.plan?.id,
                                                     wouldBring: wouldBring))
            self.rated.insert(stop.momentId)
        }
    }

    func planAnotherDay() {
        Task { await client.event("plan_another_day") }   // a Test C measure: unprompted second plans
    }

    func sendSafety(_ message: String) async -> String? {
        var reply: String?
        await run { reply = try await self.client.safety(message) }
        return reply
    }

    func deleteMyData() async {
        await run {
            try await self.client.deleteMe()
            UserDefaults.standard.removeObject(forKey: "onboardingDone")
            UserDefaults.standard.removeObject(forKey: "improved")
            UserDefaults.standard.removeObject(forKey: "morePlacesDone")
            UserDefaults.standard.removeObject(forKey: "moreTasksDone")
            AppModel.cache(nil as Plan?, "plan.json")
            AppModel.cache(nil as PlanRequest?, "request.json")
            self.plan = nil
            self.lastRequest = nil
            self.improved = false
            self.morePlacesDone = false
            self.moreTasksDone = false
            self.swappedIn = nil
            self.rated = []
            self.onboarding = nil
            self.reactions = [:]
            self.choices = [:]
            self.profile = Profile()
            self.why = []
            self.bestHour = ""
            self.bestHourMore = ""
            self.step = .bestHour
            self.route = .welcome
        }
    }

    // ---- the current plan and its request stay on the phone ("Your plan is saved on this phone") -------

    static func cache<T: Codable>(_ value: T?, _ name: String) {
        let fm = FileManager.default
        let file = URL.applicationSupportDirectory.appendingPathComponent(name)
        guard let value else { try? fm.removeItem(at: file); return }
        try? fm.createDirectory(at: URL.applicationSupportDirectory, withIntermediateDirectories: true)
        if let data = try? BrainClient.encode(value) { try? data.write(to: file, options: .atomic) }
    }

    static func loadCached<T: Codable>(_ type: T.Type, _ name: String) -> T? {
        let file = URL.applicationSupportDirectory.appendingPathComponent(name)
        guard let data = try? Data(contentsOf: file) else { return nil }
        return try? BrainClient.decode(type, from: data)
    }

}

/// Date helpers outside the main-actor model (London time, 24-hour clock).
enum Dates {
    static let isoDay: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_GB_POSIX")
        f.timeZone = TimeZone(identifier: "Europe/London")
        f.dateFormat = "yyyy-MM-dd"
        return f
    }()

    static let hhmm: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_GB_POSIX")
        f.timeZone = TimeZone(identifier: "Europe/London")
        f.dateFormat = "HH:mm"
        return f
    }()

    /// The coming Saturday (or today, if it is one): the Test B day (D105).
    static func nextSaturday(from now: Date = .now) -> Date {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(identifier: "Europe/London")!
        let weekday = cal.component(.weekday, from: now)   // Sunday = 1 ... Saturday = 7
        return cal.date(byAdding: .day, value: (7 - weekday + 7) % 7, to: now) ?? now
    }

    /// "2026-10-31 13:33" in London time, for "rate it after your visit" (D110).
    static let stamp: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_GB_POSIX")
        f.timeZone = TimeZone(identifier: "Europe/London")
        f.dateFormat = "yyyy-MM-dd HH:mm"
        return f
    }()

    /// "Saturday 31 October"
    static let dayName: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_GB")
        f.timeZone = TimeZone(identifier: "Europe/London")
        f.dateFormat = "EEEE d MMMM"
        return f
    }()

    static func time(_ hour: Int, _ minute: Int = 0) -> Date {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(identifier: "Europe/London")!
        return cal.date(bySettingHour: hour, minute: minute, second: 0, of: .now) ?? .now
    }
}
