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
    let swipePlaces: [SwipePlace]                 // D112: before the first plan (6)
    let swipePlacesLater: [SwipePlace]?           // in "Improve future plans" (4)
    let conjointTasks: [ConjointTask]             // before the first plan (5)
    let conjointTasksLater: [ConjointTask]?       // in "Improve future plans" (5)
    let aboutYou: [Question]
    let photos: [ScaleQuestion]
    let fields: Fields?
    let exampleShotCard: Card?
    let based: BasedQuestion?                     // D116: "Where are you based?", the first question
    let categoryCards: [CategoryCard]?            // D116: visitors from abroad get these instead of the London places
    let categories: CategoriesPrompt?
    let conjointWords: [PatternWords]?            // D117: "So far you've picked less walking every time"
    let summary: SummaryText?                     // D117: "So far, I've learned…"
    let testb: TestBText?                         // Build 2: the blind Plan 1 / Plan 2 pair
    let survey: SurveyText?                       // Build 2: the Test A survey
}

/// Build 2: the words around the Test B pair (brain/data/onboarding.yaml `testb`).
struct TestBText: Codable, Hashable {
    let intentTitle: String?
    let moodPrompt: String?
    let companyPrompt: String?
    let wishPrompt: String?
    let intro: String?
    let choosePrompt: String?
    let fitPrompt: String?
    let fitScale: String?
    let whyPrompt: String?
}

/// Build 2: the Test A survey's questions (validation/interview-script.md §8).
struct SurveyText: Codable, Hashable {
    let title: String?
    let understood: String?
    let likePerson: String?
    let scale: String?
    let typedOrSpoke: String?
    let intrusive: String?
}

/// D117: one "this or that" attribute's two sides in words (brain/summary.py, the same words as "So far").
struct PatternWords: Codable, Hashable {
    let attr: String
    let low: String
    let high: String
}

/// D117: what to say after an answer. Typed, because the decoder turns snake_case dictionary keys into camelCase.
struct Reactions: Codable, Hashable {
    let loved: String?
    let didntEnjoy: String?
    let wantYes: String?

    /// The words for an answer: "loved", "didnt_enjoy" or "want_yes"; nothing for the rest.
    func text(for answer: String) -> String? {
        switch answer {
        case "loved": return loved
        case "didnt_enjoy": return didntEnjoy
        case "want_yes": return wantYes
        default: return nil
        }
    }
}

struct SummaryText: Codable, Hashable {
    let title: String?
    let note: String?
    let empty: String?
    let changeNote: String?
}

/// D117: "So far, I've learned…" (GET /v1/me/summary): the person's own answers in plain words, never scores.
struct Learned: Codable, Hashable {
    let title: String?
    let note: String?
    let empty: String?
    let changeNote: String?
    let items: [LearnedItem]
}

struct LearnedItem: Codable, Hashable, Identifiable {
    let id: String
    let text: String
}

/// D116: "Where are you based?" London / elsewhere in the UK / visiting from abroad, then a town or city (optional).
struct BasedQuestion: Codable, Hashable {
    let prompt: String
    let options: [String]
    let cityPrompt: String?
    let note: String?
}

/// D116: a kind of place (brain/data/categories.yaml), shown with a ready London card's photo as its example.
struct CategoryCard: Codable, Hashable, Identifiable {
    let key: String
    let title: String
    let line: String
    let exampleId: String
    let exampleTitle: String?
    let reactions: Reactions?          // D117
    var id: String { key }
}

struct CategoriesPrompt: Codable, Hashable {
    let prompt: String
    let note: String?
    let wantPrompt: String?
}

struct OpenQuestion: Codable, Hashable {
    let key: String
    let title: String?             // D112: "A great moment"
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
    let optionLabel: String?       // "Example day" (D112)
}

struct SwipePlace: Codable, Hashable, Identifiable {
    let item: Int
    let name: String
    let reactions: Reactions?          // D117: "Got it: food with a bit of atmosphere."
    let photoIds: [String]?            // D119: cards at the same place; the first photo the app has is shown
    var id: Int { item }
}

struct ConjointTask: Codable, Hashable, Identifiable {
    let task: Int
    let a: String
    let b: String
    let levels: [String: [Double]]?   // D117: each day's level per attribute (lower is the "less" side)
    var id: Int { task }

    enum CodingKeys: String, CodingKey {
        case task
        case a = "A"
        case b = "B"
        case levels
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
    let feelLine: String?          // D115: "Lunch to start, one big reveal, some history, then a big view"
    let basis: Basis?              // D115: what the reasons rest on so far
    let blind: Bool?               // D115: the blind Test B comparison: no reasons, no feeling line, no worth

    var isBlind: Bool { blind == true }
}

/// D115: one reason a stop was picked, from the person's own answers: "you" for the app, "me" for the share card.
struct Reason: Codable, Hashable {
    let you: String
    let me: String?
}

/// D115: how much the person has told us so far, for the honest "so far" line under the reasons.
struct Basis: Codable, Hashable {
    let places: Int
    let choices: Int
    let ratings: Int
    let feelings: Int
    let kinds: Int?                // D116: a visitor's category cards

    var soFar: String {
        func n(_ k: Int, _ one: String, _ many: String) -> String? { k > 0 ? "\(k) \(k == 1 ? one : many)" : nil }
        let parts = [n(places, "place", "places"), n(choices, "example day", "example days"),
                     n(kinds ?? 0, "kind of place", "kinds of place"),
                     n(feelings, "feeling", "feelings"), n(ratings, "rating", "ratings")].compactMap { $0 }
        guard !parts.isEmpty else { return "We'll learn more about you as you answer and rate stops." }
        let list = parts.count == 1 ? parts[0] : parts.dropLast().joined(separator: ", ") + " and " + parts.last!
        return "From what you've told us so far: \(list). It gets better as you rate stops."
    }
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

struct ApproachStep: Codable, Hashable {
    let label: String              // "From", "The way in", "You arrive"
    let text: String
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
    let worthGbp: Double?          // "Worth about £V to you" (D88, D112); nil for lunch slots and the example day
    let approachSteps: [ApproachStep]?   // from where, the way in, where you arrive: the card's own text (D112)
    let bestLight: String?         // the card's light line
    let bestWindow: String?        // "16:12–17:12" on the plan's date
    let reasons: [Reason]?         // D115: "Why we picked this for you"
    let feelWord: String?          // D119: "Awe", "Calm", "Lunch": the kind of moment, from the card (same for everyone)
    let reveal: Bool?              // D119: the arrival is the moment, so the way in marks "The reveal"
    let lines: [String]?           // Build 2: the stop as text, in the Test B format (the blind pair shows only these)
    let bookAhead: String?         // journey audit: a booking the visit needs, from the card's checked source
    let hours: String?             // m176: opening hours as people read them, from the card's checked source
    let checked: String?           // journey round 2: when the card's facts were last checked ("2026-10-08")

    var id: String { momentId + "@" + arrive }

    /// D118: the worth and the price side by side ("Worth about £32 to you · Free entry").
    var worthLine: String? {
        worthGbp.map { "Worth about \(Money.text($0)) to you · " + (costGbp == 0 ? "Free entry" : "Costs \(Money.text(costGbp))") }
    }

    /// The word for this stop on "How the day moves" and its line.
    var word: String { feelWord ?? (rateable ? "Easy" : "Lunch") }
}

// ---- requests ---------------------------------------------------------------------------------

struct InstallRequest: Encodable {
    let channel: String
    let src: String?
    let consent: ConsentBody
    var code: String? = nil        // Build 2: a tester code, if one was typed on the welcome screen
}

struct ConsentBody: Encodable {
    let version: String
    let research: Bool
    let aiProcessing: Bool
}

struct InstallResponse: Decodable {
    let userId: String
    let token: String
    let channel: String?                   // journey round 2: which channel the install was counted in
}

/// D114: the person's share code and the words that go with the link.
struct ReferralResponse: Decodable {
    let code: String
    let text: String
}

struct Items<T: Encodable>: Encodable {
    let items: [T]
}

struct AnswerItem: Encodable {
    let question: String
    let text: String
    let inputMode: String
}

/// D116: Love it / Fine / Not for me / Never tried (then yes / maybe / no to trying it in London).
/// D117: the "So far" items the person marked "not right".
struct CorrectionsRequest: Encodable {
    let items: [String]
}

struct CategoryItem: Encodable, Hashable {
    let key: String
    let reaction: String
    var want: String?
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
    var based: String?                      // D116: london | uk | abroad
    var homeCity: String?                   // D116: a town or city, never nationality
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
    var intent: [String: String]? = nil    // m176: {"must_do": card id}, a place they want in the day
    var feelings: [String]? = nil          // journey round 2: a trip day's feelings, so swaps plan it like the trip
    var conditions: PlanConditions? = nil  // journey round 2: "it's raining" when re-planning the rest of today
}

/// The weather the planner should assume (rain makes the rain swaps win).
struct PlanConditions: Codable, Hashable {
    var rainProb: Double?
}

/// m176: a ready moment, for "Must include" on "Plan a day" (GET /v1/moments).
struct MomentSummary: Codable, Hashable, Identifiable {
    let id: String
    let title: String
    let status: String
    let plannable: Bool?
}

struct RatingRequest: Codable {   // Codable: kept on the phone while there is no signal (journey audit)
    let momentId: String
    let rating: Int
    let planId: Int?
    let wouldBring: Bool?
}

struct SafetyRequest: Encodable {
    let message: String
    let contact: String?           // D118: optional phone or email, only to reply; deleted once it's sorted
}

/// D118: one Help & safety message and the replies to it (GET /v1/me/safety).
struct SafetyThread: Codable, Hashable, Identifiable {
    let id: Int
    let message: String
    let createdAt: String
    let contactKept: Bool
    let replies: [SafetyReplyItem]
}

struct SafetyReplyItem: Codable, Hashable {
    let text: String
    let createdAt: String
}

struct SafetyResponse: Decodable {
    let alertId: Int
    let message: String
}

struct EventRequest: Encodable {
    let name: String
    let props: [String: String]
}

// ---- Build 2: the survey and the blind Test B pair ------------------------------------------------------------

struct SurveyBody: Encodable {
    let understood: Int?
    let likePerson: Int?
    let typedOrSpoke: String?
    let intrusive: String?
}

/// Screen 18, trip intent: stored with both plans; it changes neither.
struct PairIntent: Encodable {
    var mood: String?
    var company: String?
    var wish: String?
}

/// One plan of the pair, in the shared text format: nothing in it says how it was made.
struct PairPlan: Codable, Hashable, Identifiable {
    let id: Int
    let label: String              // "1" or "2"
    let title: String
    let summary: [String]
    let totals: Totals
    let stops: [Stop]
    let fitRating: Int?
}

struct PairResponse: Codable, Hashable {
    let title: String
    let intro: String?
    let done: Bool
    let plans: [PairPlan]
    let personalLabel: String?     // only once they've chosen
    let chosenLabel: String?
    let chosen: Plan?              // the chosen plan in full, to use on the day
    let reveal: [String]?
}

struct PairFeedback: Encodable {
    let chosen: String
    let fit1: Int
    let fit2: Int
    let why: String?
    let inputMode: String

    enum CodingKeys: String, CodingKey {
        case chosen, why
        case fit1 = "fit_1"
        case fit2 = "fit_2"
        case inputMode = "input_mode"
    }
}

extension Stop {
    /// Build 2: a stop of the generic Test B plan ("generic:<i>"): it can be rated, but it has no card to share.
    var isGeneric: Bool { momentId.hasPrefix("generic:") }
}
