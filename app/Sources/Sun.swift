import Foundation

/// D130 (Daylight): where the sun is over London, worked out on the phone with NOAA's general solar position formulas,
/// so the light needs no network and works offline. Good to a minute or two, which is plenty for a colour.
/// The same as android/…/Sun.kt (its ThemeTest checks the times).
enum Sun {
    static let lat = 51.5074
    static let lon = -0.1278

    private static func rad(_ d: Double) -> Double { d * .pi / 180 }
    private static func deg(_ r: Double) -> Double { r * 180 / .pi }

    private static var utc: Calendar {
        var c = Calendar(identifier: .gregorian)
        c.timeZone = TimeZone(identifier: "UTC")!
        return c
    }

    /// The declination (radians) and the equation of time (minutes) on a day of the year, at a UTC hour.
    private static func parts(dayOfYear: Int, utcHour: Double) -> (decl: Double, eqt: Double) {
        let g = 2 * .pi / 365 * (Double(dayOfYear - 1) + (utcHour - 12) / 24)
        let decl = 0.006918 - 0.399912 * cos(g) + 0.070257 * sin(g) - 0.006758 * cos(2 * g) + 0.000907 * sin(2 * g)
            - 0.002697 * cos(3 * g) + 0.00148 * sin(3 * g)
        let eqt = 229.18 * (0.000075 + 0.001868 * cos(g) - 0.032077 * sin(g) - 0.014615 * cos(2 * g) - 0.040849 * sin(2 * g))
        return (decl, eqt)
    }

    /// The sun's height above the horizon, in degrees, at this moment.
    static func elevation(at date: Date) -> Double {
        let c = utc.dateComponents([.hour, .minute, .second], from: date)
        let hour = Double(c.hour ?? 0) + Double(c.minute ?? 0) / 60 + Double(c.second ?? 0) / 3600
        let day = utc.ordinality(of: .day, in: .year, for: date) ?? 1
        let (decl, eqt) = parts(dayOfYear: day, utcHour: hour)
        let ha = rad((hour * 60 + eqt + 4 * lon) / 4 - 180)
        let la = rad(lat)
        let cz = sin(la) * sin(decl) + cos(la) * cos(decl) * cos(ha)
        return 90 - deg(acos(min(1, max(-1, cz))))
    }

    /// Sunrise and sunset on the UTC day of `date` (the sun's top edge at the horizon, with refraction).
    static func riseAndSet(on date: Date) -> (rise: Date, set: Date) {
        let day = utc.ordinality(of: .day, in: .year, for: date) ?? 1
        let (decl, eqt) = parts(dayOfYear: day, utcHour: 12)
        let la = rad(lat)
        let x = cos(rad(90.833)) / (cos(la) * cos(decl)) - tan(la) * tan(decl)
        let ha = deg(acos(min(1, max(-1, x))))
        let midnight = utc.startOfDay(for: date)
        return (midnight.addingTimeInterval((720 - 4 * (lon + ha) - eqt) * 60),
                midnight.addingTimeInterval((720 - 4 * (lon - ha) - eqt) * 60))
    }
}

extension Sun {
    /// D130: how far through the daylight `now` is (0 at sunrise, 1 at sunset), or nil at night. For the sun on "Now".
    static func dayFraction(_ now: Date) -> Double? {
        let (rise, set) = riseAndSet(on: now)
        let f = now.timeIntervalSince(rise) / set.timeIntervalSince(rise)
        return (0...1).contains(f) ? f : nil
    }
}

/// D130: the light the app takes on. Night is the dark ODYS look; the four day states share one set of colours and
/// differ in the sky at the top of the main screens.
enum Sky: String {
    case morning, day, golden, rain, night

    var isDay: Bool { self != .night }

    /// Dark once the sun is 4° below the horizon (about 25 minutes after sunset in London in winter). Golden in the last
    /// 90 minutes before sunset and until dark; morning from first light until 2 hours after sunrise. Rain when today's
    /// forecast gives a 60% chance or more.
    static func at(_ now: Date, rainProb: Double? = nil, alwaysDark: Bool = false) -> Sky {
        if alwaysDark || Sun.elevation(at: now) < -4 { return .night }
        if (rainProb ?? 0) >= 0.6 { return .rain }
        let (rise, set) = Sun.riseAndSet(on: now)
        if set.timeIntervalSince(now) <= 90 * 60 { return .golden }
        if now.timeIntervalSince(rise) <= 120 * 60 { return .morning }
        return .day
    }
}
