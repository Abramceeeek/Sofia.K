import Foundation
import Security

enum BrainError: LocalizedError {
    case status(Int)
    case noToken

    var errorDescription: String? {
        switch self {
        case .status(401): return "This phone isn't registered any more. Please start again."
        // Stage 1: the Brain's rate limits (brain/src/brain/ops.py)
        case .status(429): return "That's a lot in a short time. Please wait a minute, then try again."
        case .status(500...599): return "Something went wrong on our side. Please try again in a minute."
        case .status(let code): return "The planner answered with an error (\(code)). Please try again."
        case .noToken: return "Please agree to take part first."
        }
    }
}

/// Talks to the Brain (brain/src/brain/api.py). In demo mode (`-demo YES`, used for the CI screenshots) it
/// answers from the bundled JSON in Demo/ and never touches the network.
final class BrainClient {
    let base: URL
    let demo: Bool
    var token: String?
    private let session: URLSession

    private static let encoder: JSONEncoder = {
        let e = JSONEncoder()
        e.keyEncodingStrategy = .convertToSnakeCase
        return e
    }()
    private static let decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        return d
    }()

    init(base: URL, demo: Bool) {
        self.base = base
        self.demo = demo
        // The free server sleeps after 15 min idle and takes about a minute to wake (D109), so wait long.
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 90
        config.timeoutIntervalForResource = 120
        session = URLSession(configuration: config)
        token = demo ? "demo" : Keychain.load()
    }

    // ---- the calls the app makes -----------------------------------------------------------

    /// Starts waking the free server (D109) as the app opens, so it's usually up before the first real call.
    /// Fire and forget: no token, and any failure is ignored.
    func wake() async {
        if demo { return }
        _ = try? await session.data(from: base.appendingPathComponent("v1/health"))
    }

    /// `src` is "app", or "ref:<code>" for someone who arrived through a share link (D114). Build 2: `code` is an
    /// optional tester code from the welcome screen; the Brain stores it as the source and sets the channel.
    /// Returns the channel the Brain counted the install in (journey round 2: an unknown tester code stays "stranger").
    @discardableResult
    func install(research: Bool, src: String = "app", code: String? = nil) async throws -> String? {
        if demo { return nil }
        let body = InstallRequest(channel: "stranger", src: src,
                                  consent: ConsentBody(version: AppConfig.consentVersion, research: research,
                                                       aiProcessing: false), code: code)
        let out: InstallResponse = try await call("POST", "v1/installs", body)
        token = out.token
        Keychain.save(out.token)
        return out.channel
    }

    func onboarding() async throws -> Onboarding {
        if demo { return try Self.bundled("demo_onboarding") }
        return try await call("GET", "v1/onboarding")
    }

    func sendAnswers(_ items: [AnswerItem]) async throws {
        try await send("POST", "v1/me/answers", Items(items: items))
    }

    func sendSwipes(_ items: [SwipeItem]) async throws {
        try await send("POST", "v1/me/swipes", Items(items: items))
    }

    func sendCategories(_ items: [CategoryItem]) async throws {
        try await send("POST", "v1/me/categories", Items(items: items))
    }

    /// D117: "So far, I've learned…", from the person's own answers.
    func summary() async throws -> Learned {
        if demo { return try Self.bundled("demo_summary") }
        return try await call("GET", "v1/me/summary")
    }

    func sendCorrections(_ ids: [String]) async throws {
        try await send("POST", "v1/me/corrections", CorrectionsRequest(items: ids))
    }

    func sendChoices(_ items: [ChoiceItem]) async throws {
        try await send("POST", "v1/me/conjoint", Items(items: items))
    }

    func sendProfile(_ profile: Profile) async throws {
        try await send("PUT", "v1/me/profile", profile)
    }

    func makePlan(_ request: PlanRequest) async throws -> Plan {
        if demo { return try Self.bundled("demo_plan") }
        return try await call("POST", "v1/me/plans", request)
    }

    /// m176: the moments a plan can include, for "Must include".
    func moments() async throws -> [MomentSummary] {
        if demo {   // the sample plan's places, for the screenshots (as on Android)
            let plan: Plan = try BrainClient.bundled("demo_plan")
            return plan.stops.filter(\.rateable).map {
                MomentSummary(id: $0.momentId.components(separatedBy: "#")[0], title: $0.title, status: "ready", plannable: true)
            }
        }
        return try await call("GET", "v1/moments?plannable_only=true")
    }

    func referral() async throws -> ReferralResponse {
        if demo { return ReferralResponse(code: "DEMOCARD", text: "A moment from my day out, planned with ODYS") }
        return try await call("GET", "v1/me/referral")
    }

    func rate(_ request: RatingRequest) async throws {
        try await send("POST", "v1/me/ratings", request)
    }

    /// D127: answering again replaces the earlier answer.
    func dayFeedback(_ planId: Int, _ body: DayFeedback) async throws {
        try await send("POST", "v1/me/plans/\(planId)/day", body)
    }

    func safety(_ message: String, contact: String?) async throws -> String {
        if demo {
            return "If you or someone else is in danger or hurt, call 999 now. A person reads every message and will reply here in Help & safety, and by phone or email if you left one, usually within a few hours. It isn't watched through the night: a message sent late is answered the next morning."
        }
        let out: SafetyResponse = try await call("POST", "v1/me/safety", SafetyRequest(message: message, contact: contact))
        return out.message
    }

    /// D118: this person's Help & safety messages, with the replies.
    func mySafety() async throws -> [SafetyThread] {
        if demo {
            return [SafetyThread(id: 1, message: "I've lost the group near the market and my phone is on 10%.",
                                 createdAt: "2026-10-31T14:05:00+00:00", contactKept: true,
                                 replies: [SafetyReplyItem(text: "Hi, it's Abram. Are you somewhere safe? I'll call the number you left in a minute.",
                                                           createdAt: "2026-10-31T14:31:00+00:00")])]
        }
        return try await call("GET", "v1/me/safety")
    }

    // ---- Build 2: the survey and the blind Test B pair ----------------------------------------------------

    func survey(_ body: SurveyBody) async throws {
        try await send("POST", "v1/me/survey", body)
    }

    /// Journey round 2: the pair as it stands (answered or not), after a lost reply.
    func pair() async throws -> PairResponse {
        try await call("GET", "v1/me/testb/pair")
    }

    func makePair(_ intent: PairIntent) async throws -> PairResponse {
        if demo { return try Self.bundled("demo_pair") }
        return try await call("POST", "v1/me/testb/pair", intent)
    }

    func pairFeedback(_ body: PairFeedback) async throws -> PairResponse {
        if demo { return try Self.bundled("demo_pair_done") }
        return try await call("POST", "v1/me/testb/pair/feedback", body)
    }

    // ---- D120: trips -----------------------------------------------------------------------------------------

    /// "Flying from": airports and city codes matching what's typed.
    func places(_ query: String) async throws -> [TripPlace] {
        if demo {
            let all: [TripPlace] = try Self.bundled("demo_places")
            let q = query.lowercased()
            return q.isEmpty ? all : all.filter { $0.city.lowercased().hasPrefix(q) || $0.code.lowercased() == q }
        }
        var parts = URLComponents()
        parts.queryItems = [URLQueryItem(name: "q", value: query)]
        return try await call("GET", "v1/trips/places" + (parts.percentEncodedQuery.map { "?" + $0 } ?? ""))
    }

    func flights(_ search: FlightSearch) async throws -> FlightResults {
        if demo { return try Self.bundled("demo_flights") }
        return try await call("POST", "v1/trips/flights", search)
    }

    func stays(_ search: StaySearch) async throws -> StayResults {
        if demo { return try Self.bundled("demo_stays") }
        return try await call("POST", "v1/trips/stays", search)
    }

    func tripDays(_ request: TripDaysRequest) async throws -> TripDaysResponse {
        if demo { return try Self.bundled("demo_trip_days") }
        return try await call("POST", "v1/me/trips/days", request)
    }

    func event(_ name: String, _ props: [String: String] = [:]) async {
        try? await send("POST", "v1/me/events", EventRequest(name: name, props: props))
    }

    /// Journey audit: the Brain no longer knows this phone's token, so it's dropped and the person starts again.
    func forget() {
        token = nil
        Keychain.delete()
    }

    /// m176: finishes a deletion made with no signal, with the old token. True once the Brain no longer holds the
    /// data (deleted now, or already gone).
    func deleteOld(token old: String) async -> Bool {
        if demo { return true }
        var request = URLRequest(url: base.appendingPathComponent("v1/me"))
        request.httpMethod = "DELETE"
        request.setValue("Bearer \(old)", forHTTPHeaderField: "Authorization")
        guard let result = try? await session.data(for: request),
              let code = (result.1 as? HTTPURLResponse)?.statusCode else { return false }
        return (200..<300).contains(code) || code == 401 || code == 404
    }

    func deleteMe() async throws {
        if !demo { _ = try await raw("DELETE", "v1/me", nil) }
        token = nil
        Keychain.delete()
    }

    // ---- plumbing -------------------------------------------------------------------------------

    private func call<Out: Decodable>(_ method: String, _ path: String) async throws -> Out {
        try Self.decoder.decode(Out.self, from: try await raw(method, path, nil))
    }

    private func call<In: Encodable, Out: Decodable>(_ method: String, _ path: String, _ body: In) async throws -> Out {
        try Self.decoder.decode(Out.self, from: try await raw(method, path, try Self.encoder.encode(body)))
    }

    private func send<In: Encodable>(_ method: String, _ path: String, _ body: In) async throws {
        if demo { return }
        _ = try await raw(method, path, try Self.encoder.encode(body))
    }

    private func raw(_ method: String, _ path: String, _ body: Data?) async throws -> Data {
        // a path with a query ("v1/trips/places?q=tash"): the query is added on its own, so "?" isn't escaped
        let parts = path.split(separator: "?", maxSplits: 1).map(String.init)
        var url = base.appendingPathComponent(parts[0])
        if parts.count == 2, var comps = URLComponents(url: url, resolvingAgainstBaseURL: false) {
            comps.percentEncodedQuery = parts[1]
            url = comps.url ?? url
        }
        var request = URLRequest(url: url)
        request.httpMethod = method
        if path != "v1/installs" {
            guard let token else { throw BrainError.noToken }
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        if let body {
            request.httpBody = body
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        let (data, response) = try await session.data(for: request)
        let code = (response as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(code) else { throw BrainError.status(code) }
        return data
    }

    static func bundled<T: Decodable>(_ name: String) throws -> T {
        guard let url = Bundle.main.url(forResource: name, withExtension: "json") else {
            throw CocoaError(.fileNoSuchFile)
        }
        return try decoder.decode(T.self, from: Data(contentsOf: url))
    }

    static func encode<T: Encodable>(_ value: T) throws -> Data { try encoder.encode(value) }
    static func decode<T: Decodable>(_ type: T.Type, from data: Data) throws -> T { try decoder.decode(type, from: data) }
}

/// The install token is a credential, so it lives in the Keychain, not in UserDefaults.
enum Keychain {
    private static func base(_ account: String) -> [String: Any] {
        [kSecClass as String: kSecClassGenericPassword,
         kSecAttrService as String: "days-out.brain",
         kSecAttrAccount as String: account]
    }

    /// m176: the token of a "Delete my data" made with no signal, kept until the Brain has deleted it too.
    static let pendingDelete = "pending-delete"

    static func save(_ value: String, account: String = "install-token") {
        let item = base(account)
        SecItemDelete(item as CFDictionary)
        var add = item
        add[kSecValueData as String] = Data(value.utf8)
        add[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlock
        SecItemAdd(add as CFDictionary, nil)
    }

    static func load(account: String = "install-token") -> String? {
        var query = base(account)
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne
        var out: AnyObject?
        guard SecItemCopyMatching(query as CFDictionary, &out) == errSecSuccess, let data = out as? Data else {
            return nil
        }
        return String(data: data, encoding: .utf8)
    }

    static func delete(account: String = "install-token") {
        SecItemDelete(base(account) as CFDictionary)
    }
}
