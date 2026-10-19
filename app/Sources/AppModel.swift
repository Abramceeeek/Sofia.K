import Foundation
import Observation
import SwiftUI

enum AppConfig {
    /// The Brain's address, from Info.plist (`BrainBaseURL` in project.yml).
    static var baseURL: URL {
        let raw = Bundle.main.object(forInfoDictionaryKey: "BrainBaseURL") as? String ?? ""
        return URL(string: raw) ?? URL(string: "https://moments-brain.onrender.com")!
    }
    static let consentVersion = "app-2026-10-02"    // D114 share link; D115 speaking; D118 safety contact, reminders
    /// CI screenshots: the demo plan's day, so "Plan a day" (8) and the plan (9) show the same date.
    static let demoDate = "2026-10-24"        // the demo plan's day (brain/scripts/make_demo.py): next Saturday
    static let contactEmail = "abram@abdurakhmonbek.com"
    /// Build 1 plans from the Test B start point (D104): Charing Cross station, Trafalgar Square exit (TfL).
    static let startName = "Charing Cross station"
    static let start = Point(lat: 51.507819, lon: -0.126137)
    /// CI screenshots: `-demo YES -screen plan` (launch arguments land in UserDefaults).
    static var demo: Bool { UserDefaults.standard.bool(forKey: "demo") }
    static var screen: String? { UserDefaults.standard.string(forKey: "screen") }
}

enum Route: Hashable {
    case welcome, example, founder, consent, onboarding, home   // D112: an example day before consent; D117: a hello
}

/// Onboarding up to the first plan (screens 3–6). D110: "about you" and photos moved after the first plan.
enum Step: Int, CaseIterable {
    case based, bestHour, why, places, thisOrThat   // D116: "Where are you based?" first
    case learned                                    // D117: "So far, I've learned…", before the first plan

    /// The question steps, counted as "Step n of 5"; "So far" isn't a question.
    static let questions = allCases.filter { $0 != .learned }

    /// CI screenshots: `-screen places` opens that onboarding step; `categories` is the visitors' version of it.
    static func forScreen(_ name: String?) -> Step? {
        ["based": .based, "besthour": .bestHour, "why": .why, "places": .places, "categories": .places,
         "thisorthat": .thisOrThat, "learned": .learned, "learnedchange": .learned][name ?? ""]
    }

    var title: String {
        switch self {
        case .based: return "Where you're based"
        case .bestHour: return "A great moment"
        case .why: return "How you want to feel"   // D115
        case .places: return "Places you've been"
        case .thisOrThat: return "This or that"
        case .learned: return "So far"
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
    var step: Step = .based
    var onboarding: Onboarding?
    var plan: Plan?
    var busy = false
    var waking = false
    var errorMessage: String?
    var notice: (title: String, text: String)?   // journey round 2: news that isn't an error
    var sendingRatings = false             // journey round 2: one send loop at a time, so none is dropped
    var clock = Date()                     // journey round 2: set when the app comes back, so date-based cards update

    // Answers, kept until each step is sent
    var bestHour = ""
    var bestHourMore = ""
    var bestHourVoice = false              // D115: "Tell it instead" was used (the Test A typed/voice split)
    var categoryAnswers: [String: CategoryItem] = [:]   // D116: a visitor's category cards
    /// D117: the last answer's short reaction ("Got it: food with a bit of atmosphere."), shown above the next question.
    /// Only from what the person actually answered; nil when an answer tells us too little to say anything.
    var reaction: String?
    @ObservationIgnored private var saidPatterns: Set<String> = []
    var learned: Learned?                  // D117: "So far, I've learned…"
    var revealPlanId: Int?                 // D117: a new plan plays its reveal once
    var stepProgress = 0                   // D118: answers given within the current step, for "Question 7 of 14"
    var path = NavigationPath()            // D118: the Trip tab's navigation, so a rating reminder can open its stop
    // ---- D120 (ODYS Trips): three tabs, trips kept on the phone, booking on the providers' own sites ----
    var tab: MainTab = .trip
    var trips: [Trip] = []
    var currentTripId: UUID?               // the trip the Book tab searches for
    var showCreate = false                 // "Plan a trip": the four questions, full screen
    var editingTrip: Trip?                 // "Edit" on the Book tab's search: the same questions, filled in
    var editStep: Int?                     // D122: which question the edit opens on ("Your days" is 3)
    let book = BookState()
    // ---- Build 2: the Test A survey and the blind Test B pair, before the first plan ----
    var surveyDone = UserDefaults.standard.bool(forKey: "surveyDone")
    var pairDone = UserDefaults.standard.bool(forKey: "pairDone")
    var pair: PairResponse?
    var showPair = false                   // the pair for someone who already had a plan (e.g. an older build)
    var ratedOnce = UserDefaults.standard.bool(forKey: "ratedOnce")   // D118: 12a waits until the first rating
    var safetyThreads: [SafetyThread] = [] // D118: Help & safety messages and the replies to them
    var remindersOn = UserDefaults.standard.bool(forKey: "remindersOn")
    var reminderAsked = UserDefaults.standard.bool(forKey: "reminderAsked")
    var showNow = false                    // D119: "Now", the quiet screen while you're out
    var nowIndex = 0                       // which stop of the plan "Now" is on (kept per plan)

    /// D116: visiting from abroad: category cards instead of the London places, and a separate cohort
    var isVisitor: Bool { profile.based == "abroad" }

    /// Screen titles follow the person's path: visitors see "Kinds of places" where others see the London places.
    var stepTitle: String { step == .places && isVisitor ? "Kinds of places" : step.title }
    var why: [String] = []
    var reactions: [Int: String] = [:]
    var choices: [Int: String] = [:]
    var profile = Profile()
    var rated: Set<String> = []            // moment ids rated in this plan (kept per plan on the phone)
    var myRatings: [String: Int] = [:]     // their own 1–5, for the share card (D114)
    /// Journey audit (7 Oct): ratings made without signal (on the Tube), kept on the phone and sent when it's back.
    var pendingRatings: [RatingRequest] = []
    var lastRatingQueued = false           // the last rating is waiting for signal ("It'll send when you're back online")
    var improved = UserDefaults.standard.bool(forKey: "improved")
    var morePlacesDone = UserDefaults.standard.bool(forKey: "morePlacesDone")   // D112: the 4 later places
    var moreTasksDone = UserDefaults.standard.bool(forKey: "moreTasksDone")     // and the 5 later tasks
    var swappedIn: String?                 // the stop the last swap brought in, marked on the plan
    var lastRequest: PlanRequest?

    let client: BrainClient
    let screen: String?
    let location: Location                 // D123: where they are while out, on the phone only

    init() {
        location = Location()
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
            surveyDone = true
            pairDone = true
            if let trip = AppModel.demoTrip() {
                trips = [trip]
                currentTripId = trip.id
                book.flights = try? BrainClient.bundled("demo_flights")
                book.stays = try? BrainClient.bundled("demo_stays")
                book.resultsFor = trip.id
            }
            step = Step.forScreen(screen) ?? .based
            if screen == "categories" { profile.based = "abroad" }   // the visitors' onboarding (D116)
            reaction = Self.demoReactions[screen ?? ""]               // D117: one reaction on the screenshot
            lastRequest = PlanRequest(start: AppConfig.start, startName: AppConfig.startName, startTime: "12:00",
                                      endTime: "17:00", date: demoPlan?.date, stops: 4, familiar: true)
        } else if brain.token != nil, AppModel.reinstalled {
            // Decision 2 (8 Oct): the app was deleted and installed again, and iOS kept its code. Start afresh: the
            // old answers are deleted from the server (now, or the next time the app is online) and consent is asked
            // again. The privacy notice says so.
            if let old = brain.token { Keychain.save(old, account: Keychain.pendingDelete) }
            brain.forget()
            route = .welcome
        } else if brain.token == nil {
            route = .welcome
        } else {
            UserDefaults.standard.set(true, forKey: "installMarker")   // older builds: mark this install as known
            route = UserDefaults.standard.bool(forKey: "onboardingDone") ? .home : .onboarding
            // D117: back to the step they were on (each step's answers are already sent)
            step = Step(rawValue: UserDefaults.standard.integer(forKey: "onboardingStep")) ?? .based
            plan = AppModel.loadCached(Plan.self, "plan.json")
            lastRequest = AppModel.loadCached(PlanRequest.self, "request.json")
            (rated, myRatings) = AppModel.savedRatings(for: plan)   // journey audit: rated stops survive a restart
            pendingRatings = AppModel.loadCached([RatingRequest].self, "pending_ratings.json") ?? []
            trips = AppModel.loadCached([Trip].self, "trips.json") ?? []
            currentTripId = trips.first?.id
            // D116: the answers sent so far, so a later save (e.g. "Improve future plans") doesn't blank them
            if let saved = AppModel.loadCached(Profile.self, "profile.json") {
                profile = saved
                why = saved.whyTravel
            }
            restoreHandoff()                  // journey audit: "Did you book it?" after iOS closed the app
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
        } catch BrainError.status(401) where !client.demo {
            // Journey audit: the Brain no longer knows this phone (its data was deleted there), so nothing else can
            // work. Start again from Welcome instead of a dead end.
            clearLocal()
            client.forget()
            errorMessage = "This phone's answers are no longer on the planner, so let's start again."
        } catch {
            errorMessage = AppModel.message(for: error)
        }
        note.cancel()
        waking = false
        busy = false
    }

    /// Starts waking the free server early; the answer doesn't matter.
    func wake() async {
        await client.wake()
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

    /// Decision 2: a code in the Keychain but nothing at all in this install's settings means the app was deleted
    /// and installed again (iOS deletes the settings with the app, not the Keychain).
    static var reinstalled: Bool {
        let d = UserDefaults.standard
        return d.object(forKey: "installMarker") == nil && d.object(forKey: "onboardingStep") == nil
            && !d.bool(forKey: "onboardingDone")
    }

    /// Registers the phone, then shows onboarding, which loads its own questions (one request, one place).
    func agree() async {
        let joined = UserDefaults.standard.string(forKey: "refCode.joined")
        await run {
            let code = UserDefaults.standard.string(forKey: "testerCode")
            let channel = try await self.client.install(research: true, src: joined.map { "ref:\($0)" } ?? "app",
                                                        code: code)
            UserDefaults.standard.set(true, forKey: "installMarker")
            if let code, !code.isEmpty, channel == "stranger" {   // journey round 2: say so, kindly
                self.notice = ("We don't know that code",
                               "That's fine: you're in as a new tester. If a friend sent you, the test still counts you.")
            }
            UserDefaults.standard.removeObject(forKey: "refCode.joined")
            if let video = UserDefaults.standard.dictionary(forKey: "founderVideo") as? [String: String] {
                await self.client.event("founder_video", video)   // D117: watched to the end, or skipped after n s
                UserDefaults.standard.removeObject(forKey: "founderVideo")
            }
            self.route = .onboarding
        }
    }

    /// D114: a share link opened in the app (`daysout://r/<code>`). Before registering, the code is kept and sent
    /// with the install, so the funnel can count people who joined through a share. Nothing else is done with it.
    func openLink(_ url: URL) {
        guard url.scheme == "daysout", url.host == "r", client.token == nil,
              let code = url.pathComponents.dropFirst().first,
              code.count == 8, code.allSatisfy({ $0.isUppercase || $0.isNumber }) else { return }
        UserDefaults.standard.set(code, forKey: "refCode.joined")
    }

    func loadOnboarding() async throws {
        if onboarding == nil { onboarding = try await client.onboarding() }
    }

    // ---- onboarding: each step is sent as it finishes -------------------------------------------

    // ---- D118: "Question 7 of 14", every question before the first plan, counted honestly ---------------------

    private func questions(in step: Step) -> Int {
        switch step {
        case .based, .bestHour, .why: return 1
        case .places: return isVisitor ? (onboarding?.categoryCards?.count ?? 0) : (onboarding?.swipePlaces.count ?? 0)
        case .thisOrThat: return onboarding?.conjointTasks.count ?? 0
        case .learned: return 0
        }
    }

    var questionTotal: Int { Step.questions.reduce(0) { $0 + questions(in: $1) } }

    var questionNumber: Int {
        let before = Step.questions.prefix { $0 != step }.reduce(0) { $0 + questions(in: $1) }
        return min(before + min(stepProgress, max(questions(in: step) - 1, 0)) + 1, max(questionTotal, 1))
    }

    /// D119: the eyebrow on each question, and how far through the questions before the first plan
    var questionLabel: String { "Question \(questionNumber) of \(questionTotal)" }
    var questionProgress: Double { Double(questionNumber - 1) / Double(max(questionTotal, 1)) }

    /// `from`: only if still on that step (journey round 2: two taps on "Skip the rest" skipped the next step too).
    func next(from: Step? = nil) {
        if let from, from != step { return }
        reaction = nil
        stepProgress = 0
        if let n = Step(rawValue: step.rawValue + 1) {
            step = n
            if !client.demo { UserDefaults.standard.set(n.rawValue, forKey: "onboardingStep") }
        }
    }

    /// m176: "‹ Back" to the step before. Answers already given stay filled in; sending them again replaces them on
    /// the Brain (one answer per place, task and kind), so nothing is counted twice.
    func back() {
        guard let p = Step(rawValue: step.rawValue - 1) else { return }
        reaction = nil
        stepProgress = 0
        step = p
        if !client.demo { UserDefaults.standard.set(p.rawValue, forKey: "onboardingStep") }
    }

    // ---- D117: short reactions between answers, from the answer itself ------------------------------

    static let demoReactions = ["places": "Got it: big museums full of history.",
                                "categories": "Got it: big museums.",
                                "thisorthat": "So far you've picked the relaxed day with fewer stops every time."]

    /// A place swipe or a kind of place: "loved", "didnt_enjoy" or "want_yes" have words; the rest say nothing.
    func react(_ reactions: Reactions?, _ answer: String) {
        reaction = reactions?.text(for: answer)
    }

    /// "This or that": one choice can't say why (the two days differ on five or six things), so this names a pattern
    /// once it has held every time, in at least 3 made-up days; each pattern once. Same rule as "So far" (brain/summary.py).
    func reactToChoices(_ tasks: [ConjointTask]) {
        guard let words = onboarding?.conjointWords else { reaction = nil; return }
        var best: (k: Int, attr: String, text: String)?
        for (i, w) in words.enumerated() where !saidPatterns.contains(w.attr) {
            var low = 0, high = 0
            for t in tasks {
                guard let c = choices[t.task], c != "N", let lv = t.levels, let mine = lv[c],
                      let other = lv[c == "A" ? "B" : "A"], i < mine.count, i < other.count else { continue }
                if mine[i] < other[i] { low += 1 } else if mine[i] > other[i] { high += 1 }
            }
            let k = low + high
            if k >= 3, low == 0 || high == 0, k > (best?.k ?? 0) {
                best = (k, w.attr, "So far you've picked \(low > 0 ? w.low : w.high) every time.")
            }
        }
        if let best { saidPatterns.insert(best.attr) }
        reaction = best?.text
    }

    func finishBestHour() async {
        await run {
            var items: [AnswerItem] = []
            let first = self.bestHour.trimmingCharacters(in: .whitespacesAndNewlines)
            let more = self.bestHourMore.trimmingCharacters(in: .whitespacesAndNewlines)
            let mode = self.bestHourVoice ? "voice" : "typed"
            if !first.isEmpty { items.append(AnswerItem(question: "best_hour", text: first, inputMode: mode)) }
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

    /// D116: "Where are you based?" is sent straight away, so the right questions follow.
    func finishBased() async {
        await run {
            try await self.client.sendProfile(self.profile)
            AppModel.cache(self.profile, "profile.json")
            self.next()
        }
    }

    /// D116: a visitor's answers to the category cards (unanswered ones, after "Skip the rest", aren't sent).
    func finishCategories() async {
        let from = step
        await run {
            let items = (self.onboarding?.categoryCards ?? []).compactMap { self.categoryAnswers[$0.key] }
            if !items.isEmpty { try await self.client.sendCategories(items) }
            self.next(from: from)
        }
    }

    func finishPlaces() async {
        let from = step
        await run {
            try await self.sendReactions(self.onboarding?.swipePlaces ?? [])
            self.next(from: from)
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

    /// Journey audit: the feelings are kept on the phone as soon as they're chosen, so closing the app before the
    /// end of "this or that" (when they're sent) doesn't lose them.
    func keepFeelings() {
        profile.whyTravel = why
        if !client.demo { AppModel.cache(profile, "profile.json") }
    }

    /// The last onboarding step: straight on to the first plan (D110).
    func finishThisOrThat() async {
        profile.whyTravel = why
        let from = step
        await run {
            try await self.sendChoices(self.onboarding?.conjointTasks ?? [])
            try await self.client.sendProfile(self.profile)
            AppModel.cache(self.profile, "profile.json")
            self.learned = nil
            self.next(from: from)             // D117: "So far, I've learned…" before the first plan
        }
    }

    // ---- D117: "So far, I've learned…", then the first plan -------------------------------------------------

    func loadLearned() async {
        await run { self.learned = try await self.client.summary() }
    }

    /// "Looks right" (no corrections) or "Change something" then save. Corrections are stored by the Brain and those
    /// answers stop counting; a corrected feeling also leaves the answers kept on the phone, so it isn't sent again.
    func finishLearned(wrong: Set<String>) async {
        await run {
            if wrong.isEmpty {
                await self.client.event(self.learned == nil ? "summary_unavailable" : "summary_ok",
                                        ["items": "\(self.learned?.items.count ?? 0)"])
            } else {
                try await self.client.sendCorrections(Array(wrong).sorted())
                let feelings = Set(wrong.filter { $0.hasPrefix("feeling:") }.map { String($0.dropFirst(8)) })
                self.why.removeAll { feelings.contains($0) }
                self.profile.whyTravel = self.why
                AppModel.cache(self.profile, "profile.json")
                await self.client.event("summary_changed", ["n": "\(wrong.count)"])
            }
            UserDefaults.standard.set(true, forKey: "onboardingDone")
            UserDefaults.standard.removeObject(forKey: "onboardingStep")
            await self.client.event("onboarding_done")
            self.route = .home
        }
    }

    // ---- D117: Abram's hello, after the example day (only if the video is in the app) ----------------------

    func afterExample() {
        route = BundledVideo.exists("founder") ? .founder : .consent
    }

    /// The founder video plays before consent, when the app has no token yet, so how it went is kept on the phone and
    /// sent as one event once the person has agreed (`agree`).
    func founderVideoDone(seconds: Double, ended: Bool) {
        UserDefaults.standard.set(["seconds": String(format: "%.0f", seconds), "ended": ended ? "yes" : "no"],
                                  forKey: "founderVideo")
        route = .consent
    }

    /// "Improve future plans": saved when the person taps Save; `done` marks the step as finished.
    func saveImprovements(done: Bool) async {
        profile.whyTravel = why
        await run {
            try await self.client.sendProfile(self.profile)
            AppModel.cache(self.profile, "profile.json")
            if done {
                self.improved = true
                UserDefaults.standard.set(true, forKey: "improved")
                await self.client.event("improve_done")
            }
        }
    }

    // ---- plans and ratings ------------------------------------------------------------------------

    /// D123: `from` is "where you are", rounded to about 100 m on the phone (`Location.roundedHere`); m176: `mustDo` is
    /// a card they want in the day.
    func makePlan(date: Date, start: Date, end: Date, stops: Int, from: Point? = nil, mustDo: String? = nil) async {
        let day = Dates.isoDay.string(from: date)
        var request = PlanRequest(start: from ?? AppConfig.start, startName: from == nil ? AppConfig.startName : "where you are",
                                  startTime: Dates.hhmm.string(from: start), endTime: Dates.hhmm.string(from: end),
                                  date: day, stops: stops, familiar: true)
        if let mustDo { request.intent = ["must_do": mustDo] }
        await fetchPlan(request, sameDay: false)   // a new day: any trip day it replaces as "your day" stays as it was
        if from != nil { await client.event("plan_from_here") }
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
        request.intent = nil                   // a new day: the must-include goes with the old stops
        request.keep = []
        request.exclude = Array(Set(request.exclude + current.stops.filter(\.rateable).map(\.momentId))).sorted()
        await fetchPlan(request)
        await client.event("regenerate_plan")
    }

    /// "Swap this stop" (D110): the other stops stay; this card, and any swapped out before, are left out.
    // ---- journey round 2: the day as it happens ------------------------------------------------------------------

    /// "Free from 15:56 until 18:00": a day that ends at least an hour before the person's end time.
    func freeTime(_ plan: Plan) -> (from: String, to: String)? {
        guard let request = lastRequest, let last = plan.stops.last,
              AppModel.minutes(request.endTime) - AppModel.minutes(last.depart) >= 60 else { return nil }
        return (last.depart, request.endTime)
    }

    /// "Add a place": the same day with one more stop, keeping every stop it has.
    func addPlace() async {
        guard var request = lastRequest, let current = plan, request.stops < 6 else { return }
        request = PlanRequest(start: request.start, startName: request.startName, startTime: request.startTime,
                              endTime: request.endTime, date: request.date, stops: request.stops + 1,
                              familiar: request.familiar, keep: current.stops.map { $0.key ?? $0.momentId },
                              exclude: request.exclude, intent: request.intent, feelings: request.feelings)
        await fetchPlan(request, swap: true)
        await client.event("add_place", ["stops": "\(request.stops)"])
    }

    /// Decision 3 (8 Oct): plans changed on the day (rain, a closed place, tired): the rest of today from where they
    /// are (or the stop they're at), from about ten minutes from now, without the stops already done. Never on the
    /// Test B plan, which is rated as it was chosen.
    func replanRest(_ reason: String) async {
        guard let old = lastRequest, let current = plan else { return }
        let now = Calendar.london.dateComponents([.hour, .minute], from: .now)
        let start = ((now.hour ?? 0) * 60 + (now.minute ?? 0) + 14) / 5 * 5
        guard AppModel.minutes(old.endTime) - start >= 60 else {
            notice = ("Not much of the day left", "There's less than an hour before your day ends, so there's nothing to re-plan.")
            return
        }
        let done = current.stops.prefix(min(nowIndex, current.stops.count)).filter(\.rateable).map(\.momentId)
        var skip = done
        if reason == "closed", nowIndex < current.stops.count { skip.append(current.stops[nowIndex].momentId) }
        let left = current.stops.count - min(nowIndex, current.stops.count)
        let fromHere = location.usable ? location.roundedHere : nil
        let at = nowIndex < current.stops.count ? current.stops[nowIndex] : current.stops.last
        var request = PlanRequest(start: fromHere ?? at?.pin ?? old.start,
                                  startName: fromHere != nil ? "where you are" : (at?.title ?? old.startName),
                                  startTime: String(format: "%02d:%02d", start / 60, start % 60), endTime: old.endTime,
                                  date: Dates.isoDay.string(from: .now),
                                  stops: max(2, min(6, reason == "tired" ? left - 1 : left)), familiar: false,
                                  exclude: Array(Set(old.exclude + skip)).sorted(), feelings: old.feelings)
        if reason == "rain" { request.conditions = PlanConditions(rainProb: 0.9) }
        let tripId = currentTripDay?.trip.id
        await fetchPlan(request, sameDay: false)   // the trip keeps the day as planned; this is today's version
        guard let new = plan, new.id != current.id else { return }
        nowIndex = 0
        UserDefaults.standard.set(0, forKey: "nowIndex.\(new.id)")
        if let tripId, var trip = findTrip(tripId) {   // later days won't repeat this afternoon's places
            trip.used = Array(Set(trip.used).union(new.stops.filter(\.rateable).map { $0.momentId.components(separatedBy: "#")[0] })).sorted()
            save(trip)
        }
        await client.event("replan_rest", ["reason": reason, "stops": "\(request.stops)"])
    }

    static func minutes(_ hhmm: String) -> Int {
        let p = hhmm.prefix(5).split(separator: ":").compactMap { Int($0) }
        return p.count == 2 ? p[0] * 60 + p[1] : 0
    }

    func swap(_ stop: Stop) async {
        guard var request = lastRequest, let current = plan else { return }
        request.keep = current.stops.filter { $0.id != stop.id }.map { $0.key ?? $0.momentId }
        request.exclude.append(stop.momentId)
        if request.intent?["must_do"] == stop.momentId { request.intent = nil }   // they're swapping it out
        let before = Set(current.stops.map(\.momentId))
        await fetchPlan(request, swap: true)
        if let now = plan, now.id != current.id {
            swappedIn = now.stops.first { !before.contains($0.momentId) }?.momentId
            await client.event("swap_stop", ["out": stop.momentId, "in": swappedIn ?? ""])
        }
    }

    /// `sameDay`: the same day changed (swap, regenerate, re-plan), so a trip day it came from takes the new stops.
    private func fetchPlan(_ request: PlanRequest, swap: Bool = false, sameDay: Bool = true) async {
        let old = plan
        await run {
            let plan = try await self.client.makePlan(request)
            guard !plan.stops.isEmpty else {   // journey round 2: never swap a day for an empty one
                self.errorMessage = "Nothing fits that day and time. Try a longer stretch of the day, or another day."
                return
            }
            if let must = request.intent?["must_do"],
               !plan.stops.contains(where: { $0.momentId.components(separatedBy: "#")[0] == must }) {
                self.notice = ("Your must-include didn't fit",
                               "It's closed or can't be fitted at those times, so the day is planned without it.")
            }
            if sameDay { self.syncTripDay(from: old, to: plan) }   // m176: a swapped trip day changes the trip too
            self.plan = plan
            self.lastRequest = request
            if !swap {
                (self.rated, self.myRatings) = AppModel.savedRatings(for: plan)
                self.swappedIn = nil
                self.revealPlanId = plan.id   // D117: a new plan appears line by line, once
            } else {
                AppModel.saveRatings(self.myRatings, for: plan)   // a swap is a new plan id: the ratings carry over
            }
            AppModel.cache(plan, "plan.json")
            AppModel.cache(request, "request.json")
            if self.remindersOn { await Reminders.schedule(plan, rated: self.rated) }   // D118: follow the new plan
        }
    }

    /// `planId`: another plan the stop belongs to (journey round 2: the place on the way on an arrival day).
    func rate(_ stop: Stop, rating: Int, wouldBring: Bool?, planId: Int? = nil) async {
        let request = RatingRequest(momentId: stop.momentId, rating: rating, planId: planId ?? plan?.id,
                                    wouldBring: wouldBring)
        lastRatingQueued = false
        await run {
            do {
                try await self.client.rate(request)
            } catch let e as URLError where AppModel.noSignal(e) {
                // journey audit: no signal (the Tube, a basement): kept on the phone and sent when it's back
                self.pendingRatings.removeAll { $0.planId == request.planId && $0.momentId == request.momentId }
                self.pendingRatings.append(request)
                AppModel.cache(self.pendingRatings, "pending_ratings.json")
                self.lastRatingQueued = true
            }
            self.rated.insert(stop.momentId)
            self.myRatings[stop.momentId] = rating
            if let plan = self.plan { AppModel.saveRatings(self.myRatings, for: plan) }
            self.ratedOnce = true                                  // D118: now "Improve future plans" is offered
            UserDefaults.standard.set(true, forKey: "ratedOnce")
            Reminders.cancel(stop: stop)                           // rated already: no nudge for it
        }
        if !lastRatingQueued { await sendPendingRatings() }
    }

    /// Sends the ratings kept while there was no signal; each is removed once the Brain has it (or no longer has its
    /// plan). Stops at the first one that still can't be sent. Rating a stop twice replaces it on the Brain.
    func sendPendingRatings() async {
        guard !client.demo, client.token != nil, !sendingRatings else { return }
        sendingRatings = true
        defer { sendingRatings = false }
        while let next = pendingRatings.first {
            do {
                try await client.rate(next)
            } catch BrainError.status(let code) where code == 404 || code == 422 {
                // the plan or the stop is gone: nothing left to send it to
            } catch {
                return
            }
            pendingRatings.removeFirst()
            AppModel.cache(pendingRatings.isEmpty ? nil : pendingRatings, "pending_ratings.json")
        }
    }

    /// No connection, or the server didn't answer in time: worth keeping a rating to send later.
    static func noSignal(_ e: URLError) -> Bool {
        [.notConnectedToInternet, .networkConnectionLost, .dataNotAllowed, .timedOut, .cannotFindHost,
         .cannotConnectToHost, .internationalRoamingOff, .callIsActive].contains(e.code)
    }

    /// Journey audit: which stops of a plan were rated, and how, kept on the phone per plan.
    static func savedRatings(for plan: Plan?) -> (Set<String>, [String: Int]) {
        guard let plan, !AppConfig.demo,
              let saved = UserDefaults.standard.dictionary(forKey: "ratings.\(plan.id)") as? [String: Int] else { return ([], [:]) }
        return (Set(saved.keys), saved)
    }

    static func saveRatings(_ ratings: [String: Int], for plan: Plan) {
        if !AppConfig.demo { UserDefaults.standard.set(ratings, forKey: "ratings.\(plan.id)") }
    }

    // ---- D118: rating reminders, asked once, right after a plan is made ---------------------------------------

    /// "A nudge to rate each stop after you leave?" Yes asks iOS for permission (only now, never before); the
    /// reminders are local to the phone, one after each stop.
    func answerReminders(_ yes: Bool) async {
        reminderAsked = true
        UserDefaults.standard.set(true, forKey: "reminderAsked")
        remindersOn = yes ? await Reminders.ask() : false
        UserDefaults.standard.set(remindersOn, forKey: "remindersOn")
        if yes, !remindersOn {   // journey round 2: a refused permission said nothing
            notice = ("Notifications are off for ODYS",
                      "To get a reminder to rate each stop, turn on notifications for ODYS in your phone's Settings.")
        }
        if remindersOn, let plan { await Reminders.schedule(plan, rated: rated) }
        await client.event(remindersOn ? "reminders_on" : "reminders_off")
    }

    func turnRemindersOff() async {
        remindersOn = false
        UserDefaults.standard.set(false, forKey: "remindersOn")
        Reminders.clear()
        await client.event("reminders_off")
    }

    /// A reminder was tapped: open that stop, where it's rated.
    func openStop(_ momentId: String) {
        guard let stop = plan?.stops.first(where: { $0.momentId == momentId }) else { return }
        route = .home
        tab = .trip
        showNow = false
        var p = NavigationPath()
        p.append(TripDest.day)
        p.append(stop)
        path = p
    }

    // ---- D119: "Now", during the day --------------------------------------------------------------------------

    /// "Start the day": the first stop not yet rated, or where they were last time for this plan.
    func startDay() {
        guard let plan else { return }
        let saved = UserDefaults.standard.object(forKey: "nowIndex.\(plan.id)") as? Int
        nowIndex = saved ?? (plan.stops.firstIndex { !rated.contains($0.momentId) } ?? 0)
        showNow = true
        Task { await client.event("start_day", ["stop": "\(nowIndex)"]) }
    }

    /// "I'm done here", or "On to the next stop" after rating.
    func advanceNow() {
        guard let plan else { return }
        nowIndex = min(nowIndex + 1, plan.stops.count)
        UserDefaults.standard.set(nowIndex, forKey: "nowIndex.\(plan.id)")
    }

    // ---- D118: Help & safety replies ------------------------------------------------------------------------

    /// Asked only by someone who has sent a message (so nobody else makes the call).
    func loadSafety() async {
        guard (client.demo && screen == "safetyreply") || UserDefaults.standard.bool(forKey: "safetySent") else { return }
        if let threads = try? await client.mySafety() { safetyThreads = threads }
    }

    /// A reply newer than the last time Help & safety was opened.
    var unreadSafety: Bool {
        let seen = UserDefaults.standard.string(forKey: "safetySeen") ?? ""
        return safetyThreads.flatMap(\.replies).contains { $0.createdAt > seen }
    }

    func markSafetySeen() {
        let latest = safetyThreads.flatMap(\.replies).map(\.createdAt).max() ?? ""
        UserDefaults.standard.set(latest, forKey: "safetySeen")
    }

    /// D114: after a rated stop, the person can share a card with their own rating and their link. The button
    /// shows whatever the rating, so rating high never unlocks anything; and it only exists after the visit, so the
    /// plan comparison (Test B) is already over.
    func share(_ stop: Stop) async {
        guard let rating = myRatings[stop.momentId] else { return }
        var referral: ReferralResponse?
        await run { referral = try await self.client.referral() }
        guard let referral, var link = URLComponents(url: AppConfig.baseURL.appendingPathComponent("r/\(referral.code)"),
                                                     resolvingAgainstBaseURL: false) else { return }
        link.queryItems = [URLQueryItem(name: "m", value: CardPhotos.cardId(stop.momentId) ?? stop.momentId)]
        var items: [Any] = ["\(referral.text): \(link.url?.absoluteString ?? "")"]
        if let card = ShareCardView.render(stop: stop, rating: rating) { items.insert(card, at: 0) }
        await client.event("share_sheet", ["moment": stop.momentId, "rating": "\(rating)"])
        ShareSheet.present(items) { to, sent in
            Task { await self.client.event(sent ? "share_sent" : "share_cancelled", ["moment": stop.momentId, "to": to ?? ""]) }
        }
    }

    func planAnotherDay() {
        Task { await client.event("plan_another_day") }   // a Test C measure: unprompted second plans
    }

    func sendSafety(_ message: String, contact: String?) async -> String? {
        var reply: String?
        await run {
            reply = try await self.client.safety(message, contact: contact)
            UserDefaults.standard.set(true, forKey: "safetySent")
        }
        await loadSafety()
        return reply
    }

    func deleteMyData() async {
        await run {
            do {
                try await self.client.deleteMe()
            } catch let e as URLError where AppModel.noSignal(e) {
                // m176: no signal. Everything on this phone goes now; the planner's copy goes the next time the app
                // is online, with the old token kept in the Keychain for that alone.
                if let token = self.client.token { Keychain.save(token, account: Keychain.pendingDelete) }
                self.client.forget()
                self.clearLocal()
                self.notice = ("Deleted from this phone",
                               "The rest is deleted from the planner the next time ODYS is online.")
                return
            }
            self.clearLocal()
        }
    }

    /// m176: a deletion made with no signal, finished when the app is next online.
    func finishPendingDelete() async {
        guard let old = Keychain.load(account: Keychain.pendingDelete) else { return }
        if await client.deleteOld(token: old) { Keychain.delete(account: Keychain.pendingDelete) }
    }

    /// Everything about the person kept on this phone, removed; back to Welcome. Used by "Delete my data" and when
    /// the Brain no longer knows this phone.
    func clearLocal() {
        UserDefaults.standard.removeObject(forKey: "onboardingDone")
        UserDefaults.standard.removeObject(forKey: "improved")
        UserDefaults.standard.removeObject(forKey: "morePlacesDone")
        UserDefaults.standard.removeObject(forKey: "moreTasksDone")
        AppModel.cache(nil as Plan?, "plan.json")
        AppModel.cache(nil as PlanRequest?, "request.json")
        AppModel.cache(nil as Profile?, "profile.json")
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
        self.categoryAnswers = [:]
        self.learned = nil
        self.reaction = nil
        self.saidPatterns = []
        UserDefaults.standard.removeObject(forKey: "onboardingStep")
        for key in ["ratedOnce", "remindersOn", "reminderAsked", "safetySent", "safetySeen", "surveyDone", "pairDone",
                    "testerCode"] {
            UserDefaults.standard.removeObject(forKey: key)
        }
        Reminders.clear()
        self.ratedOnce = false
        self.remindersOn = false
        self.reminderAsked = false
        self.safetyThreads = []
        self.path = NavigationPath()
        AppModel.cache(nil as [Trip]?, "trips.json")
        self.trips = []
        self.currentTripId = nil
        self.book.reset()
        self.surveyDone = false
        self.pairDone = false
        self.pair = nil
        self.tab = .trip
        self.showNow = false
        self.step = .based
        self.route = .welcome
        for key in UserDefaults.standard.dictionaryRepresentation().keys
        where key.hasPrefix("ratings.") || key.hasPrefix("nowIndex.") {
            UserDefaults.standard.removeObject(forKey: key)
        }
        self.myRatings = [:]
        self.pendingRatings = []
        AppModel.cache(nil as [RatingRequest]?, "pending_ratings.json")
        AppModel.cache(nil as SavedHandoff?, "handoff.json")
        self.location.forget()                 // D123: the location choice goes too
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
