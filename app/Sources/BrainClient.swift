import Foundation
import Security

enum BrainError: LocalizedError {
    case status(Int)
    case noToken

    var errorDescription: String? {
        switch self {
        case .status(401): return "This phone isn't registered any more. Please start again."
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

    /// `src` is "app", or "ref:<code>" for someone who arrived through a share link (D114).
    func install(research: Bool, src: String = "app") async throws {
        if demo { return }
        let body = InstallRequest(channel: "stranger", src: src,
                                  consent: ConsentBody(version: AppConfig.consentVersion, research: research,
                                                       aiProcessing: false))
        let out: InstallResponse = try await call("POST", "v1/installs", body)
        token = out.token
        Keychain.save(out.token)
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

    func referral() async throws -> ReferralResponse {
        if demo { return ReferralResponse(code: "DEMOCARD", text: "I think you'd love this day — try it") }
        return try await call("GET", "v1/me/referral")
    }

    func rate(_ request: RatingRequest) async throws {
        try await send("POST", "v1/me/ratings", request)
    }

    func safety(_ message: String) async throws -> String {
        if demo {
            return "If you or someone else is in danger or hurt, call 999 now. We've told a person on our team, and they will reply within a few hours."
        }
        let out: SafetyResponse = try await call("POST", "v1/me/safety", SafetyRequest(message: message))
        return out.message
    }

    func event(_ name: String, _ props: [String: String] = [:]) async {
        try? await send("POST", "v1/me/events", EventRequest(name: name, props: props))
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
        var request = URLRequest(url: base.appendingPathComponent(path))
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
    private static let base: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: "days-out.brain",
        kSecAttrAccount as String: "install-token",
    ]

    static func save(_ value: String) {
        SecItemDelete(base as CFDictionary)
        var add = base
        add[kSecValueData as String] = Data(value.utf8)
        add[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlock
        SecItemAdd(add as CFDictionary, nil)
    }

    static func load() -> String? {
        var query = base
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne
        var out: AnyObject?
        guard SecItemCopyMatching(query as CFDictionary, &out) == errSecSuccess, let data = out as? Data else {
            return nil
        }
        return String(data: data, encoding: .utf8)
    }

    static func delete() {
        SecItemDelete(base as CFDictionary)
    }
}
