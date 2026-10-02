import Foundation
import UIKit
import UserNotifications

/// D118: rating reminders. Asked once, right after a plan is made ("A nudge to rate each stop after you leave?"), and
/// iOS's permission prompt comes only after a yes (D117: permissions at the moment they're needed). They're local
/// notifications, set by the phone itself: nothing is sent to a server. One per stop, 10 minutes after the stop's
/// planned end, on the plan's day; tapping one opens that stop, where it's rated.
enum Reminders {
    private static let idPrefix = "rate."
    private static let afterMinutes = 10

    static func ask() async -> Bool {
        (try? await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound])) ?? false
    }

    /// Replaces the reminders with this plan's: rateable stops not yet rated, still in the future.
    static func schedule(_ plan: Plan, rated: Set<String>) async {
        await clearNow()
        guard let day = plan.date else { return }
        let center = UNUserNotificationCenter.current()
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(identifier: "Europe/London")!
        for stop in plan.stops where stop.rateable && !rated.contains(stop.momentId) {
            guard let end = Dates.stamp.date(from: "\(day) \(stop.depart)"),
                  let at = cal.date(byAdding: .minute, value: afterMinutes, to: end), at > .now else { continue }
            let content = UNMutableNotificationContent()
            content.title = "How was it?"
            content.body = "\(stop.title). One tap to rate it."
            content.sound = .default
            content.userInfo = ["momentId": stop.momentId]
            var when = cal.dateComponents([.year, .month, .day, .hour, .minute], from: at)
            when.timeZone = cal.timeZone
            let request = UNNotificationRequest(identifier: idPrefix + stop.momentId, content: content,
                                                trigger: UNCalendarNotificationTrigger(dateMatching: when, repeats: false))
            try? await center.add(request)
        }
    }

    static func cancel(stop: Stop) {
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: [idPrefix + stop.momentId])
    }

    static func clear() {
        Task { await clearNow() }
    }

    /// Removes only this app's rating reminders, and finishes before new ones are added.
    static func clearNow() async {
        let center = UNUserNotificationCenter.current()
        let ours = await center.pendingNotificationRequests().map(\.identifier).filter { $0.hasPrefix(idPrefix) }
        center.removePendingNotificationRequests(withIdentifiers: ours)
    }
}

/// Shows a reminder even with the app open, and turns a tap into "open that stop" (via NotificationCenter, so the
/// app's model stays the only owner of navigation).
final class ReminderTaps: NSObject, UNUserNotificationCenterDelegate {
    static let shared = ReminderTaps()
    static let openStop = Notification.Name("days-out.open-stop")

    func userNotificationCenter(_ center: UNUserNotificationCenter, willPresent notification: UNNotification,
                                withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        completionHandler([.banner, .sound])
    }

    func userNotificationCenter(_ center: UNUserNotificationCenter, didReceive response: UNNotificationResponse,
                                withCompletionHandler completionHandler: @escaping () -> Void) {
        if let id = response.notification.request.content.userInfo["momentId"] as? String {
            DispatchQueue.main.async { NotificationCenter.default.post(name: ReminderTaps.openStop, object: id) }
        }
        completionHandler()
    }
}

final class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        UNUserNotificationCenter.current().delegate = ReminderTaps.shared
        return true
    }
}
