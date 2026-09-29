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
    case welcome, consent, onboarding, home
}

enum Step: Int, CaseIterable {
    case bestHour, why, places, thisOrThat, aboutYou, photos

    /// CI screenshots: `-screen places` opens that onboarding step.
    static func forScreen(_ name: String?) -> Step? {
        ["besthour": .bestHour, "why": .why, "places": .places, "thisorthat": .thisOrThat,
         "aboutyou": .aboutYou, "photos": .photos][name ?? ""]
    }

    var title: String {
        switch self {
        case .bestHour: return "The best hour"
        case .why: return "Why you go out"
        case .places: return "Places you've been"
        case .thisOrThat: return "This or that"
        case .aboutYou: return "A bit about you"
        case .photos: return "Photos"
        }
    }
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
    var rated: Set<String> = []

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
            plan = try? BrainClient.bundled("demo_plan")
            step = Step.forScreen(screen) ?? .bestHour
        } else if brain.token == nil {
            route = .welcome
            plan = AppModel.loadCachedPlan()
        } else {
            route = UserDefaults.standard.bool(forKey: "onboardingDone") ? .home : .onboarding
            plan = AppModel.loadCachedPlan()
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
            errorMessage = (error as? LocalizedError)?.errorDescription
                ?? "Couldn't reach the planner. Check your connection and try again."
        }
        note.cancel()
        waking = false
        busy = false
    }

    // ---- first run ---------------------------------------------------------------------------

    func agree() async {
        await run {
            try await self.client.install(research: true)
            self.route = .onboarding
            try await self.loadOnboarding()
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

    func finishPlaces() async {
        await run {
            let items = self.reactions.sorted { $0.key < $1.key }.map { SwipeItem(item: $0.key, reaction: $0.value) }
            try await self.client.sendSwipes(items)
            self.next()
        }
    }

    func finishThisOrThat() async {
        await run {
            let items = self.choices.sorted { $0.key < $1.key }.map { ChoiceItem(task: $0.key, choice: $0.value) }
            try await self.client.sendChoices(items)
            self.next()
        }
    }

    func finishAboutYou() async {
        profile.whyTravel = why
        await run {
            try await self.client.sendProfile(self.profile)
            self.next()
        }
    }

    func finishOnboarding() async {
        profile.whyTravel = why
        await run {
            try await self.client.sendProfile(self.profile)
            UserDefaults.standard.set(true, forKey: "onboardingDone")
            await self.client.event("onboarding_done")
            self.route = .home
        }
    }

    // ---- plans and ratings ------------------------------------------------------------------------

    func makePlan(date: Date, start: Date, end: Date, stops: Int) async {
        let day = Dates.isoDay.string(from: date)
        let request = PlanRequest(start: AppConfig.start, startName: AppConfig.startName,
                                  startTime: Dates.hhmm.string(from: start), endTime: Dates.hhmm.string(from: end),
                                  date: day, stops: stops, familiar: true)
        await run {
            let plan = try await self.client.makePlan(request)
            self.plan = plan
            self.rated = []
            AppModel.cache(plan)
        }
    }

    func rate(_ stop: Stop, rating: Int, wouldBring: Bool?) async {
        await run {
            try await self.client.rate(RatingRequest(momentId: stop.momentId, rating: rating, planId: self.plan?.id,
                                                     wouldBring: wouldBring))
            self.rated.insert(stop.id)
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
            AppModel.cache(nil)
            self.plan = nil
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

    // ---- the current plan stays on the phone ("Your plan is saved on this phone") -------------------

    private static var planFile: URL {
        URL.applicationSupportDirectory.appendingPathComponent("plan.json")
    }

    static func cache(_ plan: Plan?) {
        let fm = FileManager.default
        guard let plan else { try? fm.removeItem(at: planFile); return }
        try? fm.createDirectory(at: URL.applicationSupportDirectory, withIntermediateDirectories: true)
        if let data = try? BrainClient.encode(plan) { try? data.write(to: planFile, options: .atomic) }
    }

    static func loadCachedPlan() -> Plan? {
        guard let data = try? Data(contentsOf: planFile) else { return nil }
        return try? BrainClient.decode(Plan.self, from: data)
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

    static func time(_ hour: Int, _ minute: Int = 0) -> Date {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(identifier: "Europe/London")!
        return cal.date(bySettingHour: hour, minute: minute, second: 0, of: .now) ?? .now
    }
}
