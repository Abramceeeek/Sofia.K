import CoreLocation
import Foundation

// What the Brain sends and receives (brain/src/brain/api.py). JSON keys are snake_case; the coders convert them.

struct Point: Codable, Hashable {
    var lat: Double
    var lon: Double

    var coordinate: CLLocationCoordinate2D { .init(latitude: lat, longitude: lon) }
}

// ---- onboarding (GET /v1/onboarding) ------------------------------------------------------

struct Onboarding: Codable {
    let openQuestions: [OpenQuestion]
    let whyTravel: Choices
    let conjoint: Prompt?
    let swipe: Prompt?
    let swipePlaces: [SwipePlace]
    let conjointTasks: [ConjointTask]
    let aboutYou: [Question]
    let photos: [ScaleQuestion]
    let fields: Fields?
    let exampleShotCard: Card?
}

struct OpenQuestion: Codable, Hashable {
    let key: String
    let text: String
    let followUp: String?
    let examples: [String]?        // D110: two or three short example answers
}

struct Choices: Codable, Hashable {
    let prompt: String
    let options: [String]
}

struct Prompt: Codable, Hashable {
    let prompt: String
    let noPreference: String?      // "this or that" only (D110)
}

struct SwipePlace: Codable, Hashable, Identifiable {
    let item: Int
    let name: String
    var id: Int { item }
}

struct ConjointTask: Codable, Hashable, Identifiable {
    let task: Int
    let a: String
    let b: String
    var id: Int { task }

    enum CodingKeys: String, CodingKey {
        case task
        case a = "A"
        case b = "B"
    }
}

struct Question: Codable, Hashable {
    let key: String
    let text: String
    let note: String?
}

struct ScaleQuestion: Codable, Hashable {
    let key: String
    let text: String
    let scale: String?
    let exampleLabel: String?      // "Example of what you'll get" (D110)
}

struct Fields: Codable, Hashable {
    let question: String
    let note: String
    let options: [FieldOption]
}

struct FieldOption: Codable, Hashable, Identifiable {
    let key: String
    let label: String
    var id: String { key }
}

// ---- moments and plans ----------------------------------------------------------------------

struct Card: Codable, Hashable, Identifiable {
    let id: String
    let title: String
    let place: Place
    let approach: Approach?
    let whatHappens: String?
    let costGbp: Double?
    let shotCard: ShotCard?
}

struct Place: Codable, Hashable {
    let name: String
    let lat: Double?
    let lon: Double?
}

struct Approach: Codable, Hashable {
    let from: String?
    let path: String?
    let stepFree: Bool?
}

struct ShotCard: Codable, Hashable {
    let standAt: StandAt?
    let face: String?
    let frame: String?
    let when: String?
    let avoid: String?
}

struct StandAt: Codable, Hashable {
    let lat: Double?
    let lon: Double?
    let note: String?
}

struct Plan: Codable, Hashable, Identifiable {
    let id: Int
    let title: String?
    let summary: [String]?
    let totals: Totals?            // the summary at the top (D110)
    let date: String?
    let stops: [Stop]
}

/// Cost per person, walking between stops and the finish time (brain.dayplan.plan_totals).
struct Totals: Codable, Hashable {
    let costGbp: Double
    let spendGbp: Double
    let transportGbp: Double
    let walkMin: Double
    let walkKm: Double
    let finish: String?
}

struct Stop: Codable, Hashable, Identifiable {
    let momentId: String
    let key: String?               // the planner's id, sent back in `keep` when swapping another stop (D110)
    let title: String
    let arrive: String
    let depart: String
    let travelMin: Double?
    let travelMode: String?
    let travelText: String
    let approach: String
    let what: String
    let queueMin: Double?
    let bestText: String
    let costGbp: Double
    let costText: String
    let rainSwap: String
    let lunch: Bool
    let familiar: Bool
    let rateable: Bool
    let pin: Point?
    let chosenFor: [String]
    let card: Card?

    var id: String { momentId + "@" + arrive }
}

// ---- requests ---------------------------------------------------------------------------------

struct InstallRequest: Encodable {
    let channel: String
    let src: String?
    let consent: ConsentBody
}

struct ConsentBody: Encodable {
    let version: String
    let research: Bool
    let aiProcessing: Bool
}

struct InstallResponse: Decodable {
    let userId: String
    let token: String
}

struct Items<T: Encodable>: Encodable {
    let items: [T]
}

struct AnswerItem: Encodable {
    let question: String
    let text: String
    let inputMode: String
}

struct SwipeItem: Encodable {
    let item: Int
    let reaction: String
}

struct ChoiceItem: Encodable {
    let task: Int
    let choice: String
}

/// "About you" (D19, D77): all optional; nil fields are left out of the JSON.
struct Profile: Codable, Equatable {
    var whyTravel: [String] = []
    var budgetBand: String?
    var company: String?
    var chronotype: String?
    var activity: String?
    var grewUp: String?
    var foodsAvoided: String?
    var photosMatter: Int?
    var shotCardAppeal: Int?
    var fields: [String] = []
}

/// Kept on the phone with the plan, so "Swap this stop" can ask again with `keep` and `exclude` (D110).
struct PlanRequest: Codable, Hashable {
    let start: Point
    let startName: String
    let startTime: String
    let endTime: String
    let date: String?
    let stops: Int
    let familiar: Bool
    var keep: [String] = []
    var exclude: [String] = []
}

struct RatingRequest: Encodable {
    let momentId: String
    let rating: Int
    let planId: Int?
    let wouldBring: Bool?
}

struct SafetyRequest: Encodable {
    let message: String
}

struct SafetyResponse: Decodable {
    let alertId: Int
    let message: String
}

struct EventRequest: Encodable {
    let name: String
    let props: [String: String]
}
