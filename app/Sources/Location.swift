import CoreLocation
import Foundation
import Observation

/// D123 (Abram, 8 Oct): where the person is while they're out, used on the phone only.
/// - Asked only when they start a day ("Now"), with ODYS's own question first and iOS's prompt only after a yes.
/// - "When in use" only: nothing runs in the background, and it stops when "Now" closes.
/// - Never sent to the Brain, except "Start from where I am" on "Plan a day": that start point, rounded to about
///   100 m (3 decimal places), is sent once to plan the day and isn't kept there.
/// - It shows how far the next stop is, notices arriving and leaving, and asks for the rating after leaving.
@MainActor
@Observable
final class Location: NSObject, CLLocationManagerDelegate {
    @ObservationIgnored private let manager = CLLocationManager()
    var status: CLAuthorizationStatus = .notDetermined
    /// The person's own choice in the app ("Use my location"); iOS's permission is separate and can be changed in Settings.
    var wanted = UserDefaults.standard.bool(forKey: "locationOn")
    var asked = UserDefaults.standard.bool(forKey: "locationAsked")
    var here: CLLocationCoordinate2D?
    @ObservationIgnored private var running = false

    override init() {
        super.init()
        status = manager.authorizationStatus
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyNearestTenMeters
        manager.distanceFilter = 20
    }

    var allowed: Bool { status == .authorizedWhenInUse || status == .authorizedAlways }
    var usable: Bool { wanted && allowed }
    var deniedBySettings: Bool { status == .denied || status == .restricted }

    /// "Yes, use my location": records the choice, then iOS's own prompt (only if it hasn't been answered).
    func turnOn() {
        wanted = true
        asked = true
        UserDefaults.standard.set(true, forKey: "locationOn")
        UserDefaults.standard.set(true, forKey: "locationAsked")
        if status == .notDetermined { manager.requestWhenInUseAuthorization() } else { start() }
    }

    func turnOff() {
        wanted = false
        asked = true
        UserDefaults.standard.set(false, forKey: "locationOn")
        UserDefaults.standard.set(true, forKey: "locationAsked")
        stop()
        here = nil
    }

    /// While "Now" or "Plan a day" is on screen.
    func start() {
        guard usable, !running else { return }
        running = true
        manager.startUpdatingLocation()
    }

    func stop() {
        guard running else { return }
        running = false
        manager.stopUpdatingLocation()
    }

    /// Clears the choice (Delete my data).
    func forget() {
        stop()
        here = nil
        wanted = false
        asked = false
        UserDefaults.standard.removeObject(forKey: "locationOn")
        UserDefaults.standard.removeObject(forKey: "locationAsked")
    }

    nonisolated func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        let s = manager.authorizationStatus
        Task { @MainActor in
            self.status = s
            if self.usable { self.start() } else { self.stop() }
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let last = locations.last, last.horizontalAccuracy >= 0, last.horizontalAccuracy < 200 else { return }
        let lat = last.coordinate.latitude, lon = last.coordinate.longitude
        Task { @MainActor in self.here = CLLocationCoordinate2D(latitude: lat, longitude: lon) }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {}

    // ---- distances, on the phone ------------------------------------------------------------------------------

    /// Straight-line metres from here to a point.
    func metres(to p: Point) -> Double? {
        guard let here else { return nil }
        return CLLocation(latitude: here.latitude, longitude: here.longitude)
            .distance(from: CLLocation(latitude: p.lat, longitude: p.lon))
    }

    /// "About 8 min walk": the straight line × 1.3 for streets, at 80 m a minute (GUESSES, the Brain's walking
    /// estimate uses similar numbers). Over 30 min it says the distance instead, since they'd take the Tube.
    static func walkText(_ metres: Double) -> String {
        let minutes = Int((metres * 1.3 / 80).rounded())
        if minutes <= 1 { return "About a minute away" }
        if minutes <= 30 { return "About \(minutes) min walk away" }
        return String(format: "About %.1f km away", metres / 1000)
    }

    /// "Start from where I am": rounded to 3 decimal places (about 100 m), the only way a location leaves the phone.
    var roundedHere: Point? {
        guard let here else { return nil }
        let r = { (x: Double) in (x * 1000).rounded() / 1000 }
        return Point(lat: r(here.latitude), lon: r(here.longitude))
    }
}
