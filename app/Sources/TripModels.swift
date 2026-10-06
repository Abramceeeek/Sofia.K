import Foundation

// D120 (ODYS Trips design): multi-day trips, flights and stays. What the Brain sends (brain/src/brain/trips.py and the
// /v1/trips and /v1/me/trips endpoints), and the trip as it's kept on the phone. Nothing is booked in the app: every
// result links out to the provider's own site, and ODYS earns nothing from those links while testing.

// ---- places ------------------------------------------------------------------------------------------------

/// An airport or a city code ("All London airports"), from GET /v1/trips/places.
struct TripPlace: Codable, Hashable, Identifiable {
    let code: String
    let city: String
    let name: String
    let country: String
    var id: String { code }

    /// "Tashkent (TAS)", or "London, all airports (LON)" for a city code.
    var label: String {
        name.hasPrefix("All ") ? "\(city), all airports (\(code))" : (name == city ? "\(city) (\(code))" : "\(city) \(name) (\(code))")
    }
}

struct TripLink: Codable, Hashable {
    let name: String
    let url: String
}

// ---- flights (POST /v1/trips/flights) ---------------------------------------------------------------------------

struct FlightFilters: Codable, Hashable {
    var stops: [Int] = []                  // 0, 1, 2 (= 2 or more); empty means any
    var outTimes: [String] = []            // night / morning / afternoon / evening, leaving
    var maxLegMin: Int?                    // the longest journey, each way
    var airlines: [String] = []
    var maxPrice: Double?
    var checkedBag = false
    var sort = "best"                      // best | cheapest | fastest

    /// How many filters are on, for "Filters · 2" (the sort isn't a filter).
    var count: Int {
        [!stops.isEmpty, !outTimes.isEmpty, maxLegMin != nil, !airlines.isEmpty, maxPrice != nil, checkedBag]
            .filter { $0 }.count
    }

    func cleared() -> FlightFilters { FlightFilters(sort: sort) }
}

struct FlightSearch: Encodable {
    let origin: String
    let destination: String
    let departDate: String
    let returnDate: String?
    let adults: Int
    let filters: FlightFilters
}

struct FlightLeg: Codable, Hashable {
    let origin: String
    let destination: String
    let departAt: String                   // local time at the airport, "2026-10-20T08:35"
    let arriveAt: String
    let durationMin: Int
    let stops: Int
    let via: [String]
    let carriers: [String]
    let flightNumbers: [String]

    var departTime: String { String(departAt.dropFirst(11).prefix(5)) }
    var arriveTime: String { String(arriveAt.dropFirst(11).prefix(5)) }
    var departDay: String { String(departAt.prefix(10)) }
    /// Days between leaving and landing, for "+1 day".
    var plusDays: Int {
        guard let a = Dates.isoDay.date(from: String(departAt.prefix(10))),
              let b = Dates.isoDay.date(from: String(arriveAt.prefix(10))) else { return 0 }
        return max(0, Int((b.timeIntervalSince(a) / 86400).rounded()))
    }
}

struct Flight: Codable, Hashable, Identifiable {
    let id: String
    let airline: String
    let airlineCode: String
    let price: Double
    let currency: String
    let outbound: FlightLeg
    let inbound: FlightLeg?
    let checkedBags: Int?
    let refundable: Bool?
    let changeable: Bool?
    let sample: Bool
    let stops: Int
    let durationMin: Int
    let tags: [String]?
}

struct StopFacet: Codable, Hashable {
    let stops: Int
    let minPrice: Double
}

struct AirlineFacet: Codable, Hashable {
    let name: String
    let code: String
    let minPrice: Double
    let count: Int
}

struct FlightFacets: Codable, Hashable {
    let stops: [StopFacet]
    let airlines: [AirlineFacet]
    let price: [Double]?
    let legMinutes: [Int]?
}

struct FlightTab: Codable, Hashable {
    let price: Double
    let durationMin: Int
}

struct FlightResults: Codable, Hashable {
    let source: String                     // sample | duffel_test | duffel | unavailable
    let note: String?
    let total: Int
    let shown: Int
    let results: [Flight]
    let facets: FlightFacets
    let tabs: [String: FlightTab?]?
    let links: [TripLink]
    let searchedAt: String?
}

// ---- stays (POST /v1/trips/stays) -------------------------------------------------------------------------------

struct StayFilters: Codable, Hashable {
    var maxNight: Double?
    var minRating: Double?
    var kinds: [String] = []
    var refundable = false
    var breakfast = false
    var sort = "recommended"               // recommended | price | rating | distance

    var count: Int {
        [maxNight != nil, minRating != nil, !kinds.isEmpty, refundable, breakfast].filter { $0 }.count
    }

    func cleared() -> StayFilters { StayFilters(sort: sort) }
}

struct StaySearch: Encodable {
    let destination: String
    let checkin: String
    let checkout: String
    let adults: Int
    let rooms: Int
    let filters: StayFilters
}

struct StayResult: Codable, Hashable, Identifiable {
    let id: String
    let name: String
    let kind: String
    let stars: Double?
    let rating: Double?                    // guests' score out of 10
    let reviews: Int?
    let address: String
    let lat: Double?
    let lon: Double?
    let photo: String?
    let priceTotal: Double
    let currency: String
    let nights: Int
    let room: String
    let board: String
    let breakfast: Bool
    let refundable: Bool?
    let distanceKm: Double?
    let sample: Bool
    let priceNight: Double
    let links: [TripLink]
    let tags: [String]?

    var point: Point? { lat.flatMap { la in lon.map { Point(lat: la, lon: $0) } } }
}

struct KindFacet: Codable, Hashable {
    let kind: String
    let count: Int
}

struct StayFacets: Codable, Hashable {
    let priceNight: [Double]?
    let kinds: [KindFacet]
    let maxKm: Double?
}

struct StayTab: Codable, Hashable {
    let priceNight: Double
    let rating: Double?
    let distanceKm: Double?
}

struct StayResults: Codable, Hashable {
    let source: String                     // sample | liteapi_sandbox | liteapi | unavailable
    let note: String?
    let total: Int
    let shown: Int
    let results: [StayResult]
    let facets: StayFacets
    let tabs: [String: StayTab?]?
    let links: [TripLink]
    let centre: String
    let searchedAt: String?
}

// ---- days (POST /v1/me/trips/days) ------------------------------------------------------------------------------

struct TripDaysRequest: Encodable {
    let destination: String
    let startDate: String
    let nights: Int
    let feelings: [String]
    let stay: Point?
    let stayName: String?
    let arriveTime: String?
    let leaveTime: String?
    let days: [Int]
    let exclude: [String]
}

struct TripDayOut: Codable, Hashable {
    let index: Int
    let date: String
    let kind: String                       // one | arrive | full | leave
    let title: String
    let plan: Plan?
    let window: DayWindow?                 // the day's times, so "Swap this stop" and "Regenerate" work on it
}

struct DayWindow: Codable, Hashable {
    let start: String
    let end: String
    let stops: Int
}

struct TripDaysResponse: Codable, Hashable {
    let totalDays: Int
    let days: [TripDayOut]
    let start: String
    let used: [String]
}

// ---- the trip, kept on the phone (trips.json) -------------------------------------------------------------------

/// What the person chose on a provider's site: saved, or booked there (they tell us when they come back).
struct TripChoice: Codable, Hashable {
    var kind: String                       // flight | stay
    var title: String                      // "Turkish Airlines · 03:15 → 10:20", or the place's name
    var provider: String
    var price: Double
    var booked: Bool
    var arriveTime: String?                // a flight's landing on day 1, for the arrival day
    var leaveTime: String?                 // its departure on the last day
    var point: Point?                      // a stay, so the days start near it
}

struct Trip: Codable, Hashable, Identifiable {
    var id = UUID()
    var destination = "london"
    var city = "London"
    var start: String                      // yyyy-MM-dd, the first day
    var nights: Int
    var adults = 1
    var origin: TripPlace?
    var originGuessed = false              // filled in from the town or city they gave (never from nationality)
    var needFlight = true
    var feelings: [String] = []
    var days: [TripDayOut] = []
    var used: [String] = []
    var daysFrom: String?                  // where the planned days start ("Charing Cross" or the stay)
    var daysStale = false                  // a flight or stay was chosen after the days were planned
    var flight: TripChoice?
    var stay: TripChoice?

    var dayCount: Int { nights + 1 }
    var needStay: Bool { nights > 0 }
    var startDate: Date { Dates.isoDay.date(from: start) ?? .now }
    var endDate: Date { Calendar.london.date(byAdding: .day, value: nights, to: startDate) ?? startDate }
    var end: String { Dates.isoDay.string(from: endDate) }

    /// "10–16 Oct", "30 Oct – 2 Nov", or "Sat 10 Oct" for one day.
    var range: String {
        guard nights > 0 else { return Dates.dayShort.string(from: startDate) }
        let same = Calendar.london.component(.month, from: startDate) == Calendar.london.component(.month, from: endDate)
        return same ? "\(Dates.dayNum.string(from: startDate))–\(Dates.dayMonth.string(from: endDate))"
                    : "\(Dates.dayMonth.string(from: startDate)) – \(Dates.dayMonth.string(from: endDate))"
    }

    var lengthLabel: String { nights == 0 ? "One day" : "\(nights) night\(nights == 1 ? "" : "s")" }

    /// "Sat 10 Oct to Fri 16 Oct · 6 nights"
    var rangeLong: String {
        nights == 0 ? "\(Dates.dayShort.string(from: startDate)) · one day"
                    : "\(Dates.dayShort.string(from: startDate)) to \(Dates.dayShort.string(from: endDate)) · \(lengthLabel)"
    }

    var travellers: String { "\(adults) \(adults == 1 ? "traveller" : "travellers")" }

    /// "A curious, peaceful trip · 1 traveller"
    var feelLine: String {
        let words = feelings.map { TripFeelings.adjective($0) }
        return (words.isEmpty ? "Your trip" : "A \(words.joined(separator: ", ")) trip") + " · " + travellers
    }
}

/// The five feelings (the same as onboarding's "How do you most want to feel", brain/reasons.py FEELINGS), with the
/// design's lines under each.
enum TripFeelings {
    static let all: [(key: String, label: String, line: String)] = [
        ("restored", "Restored", "Come home lighter than you left"),
        ("excited", "Excited", "Something to tell people about"),
        ("connected", "Connected", "Time that feels shared"),
        ("curious", "Curious", "Learn something you didn’t expect"),
        ("peaceful", "Peaceful", "Calm while the city rushes past"),
    ]

    static func adjective(_ key: String) -> String { key }
}

extension Calendar {
    static let london: Calendar = {
        var c = Calendar(identifier: .gregorian)
        c.timeZone = TimeZone(identifier: "Europe/London") ?? .current
        return c
    }()
}

extension Dates {
    /// "Sat 10 Oct"
    static let dayShort: DateFormatter = make("EEE d MMM")
    /// "10 Oct"
    static let dayMonth: DateFormatter = make("d MMM")
    /// "10"
    static let dayNum: DateFormatter = make("d")
    /// "Sat"
    static let weekdayShort: DateFormatter = make("EEE")
    /// "Oct"
    static let monthShort: DateFormatter = make("MMM")

    private static func make(_ format: String) -> DateFormatter {
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_GB")
        f.timeZone = TimeZone(identifier: "Europe/London")
        f.dateFormat = format
        return f
    }

    /// "11h 05m"
    static func duration(_ minutes: Int) -> String {
        "\(minutes / 60)h \(String(format: "%02d", minutes % 60))m"
    }

    /// "Sat 10 Oct" from "2026-10-10" (or the first ten characters of a date-time).
    static func shortDay(_ iso: String) -> String {
        isoDay.date(from: String(iso.prefix(10))).map { dayShort.string(from: $0) } ?? iso
    }
}

extension Money {
    /// £398, rounded to the pound for prices that aren't ours to promise.
    static func whole(_ gbp: Double) -> String { "£\(Int(gbp.rounded()))" }
}
