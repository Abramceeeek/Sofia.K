import SwiftUI

@main
struct FaceApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var delegate   // D118: rating reminders' taps
    @State private var model = AppModel()
    @Environment(\.scenePhase) private var scenePhase

    init() {
        Theme.applyAppearance()
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(model)
                .tint(Theme.accent)
                .preferredColorScheme(model.sky.isDay ? .light : .dark)   // D130 (Daylight): London's light, or Always dark
                .onOpenURL { url in model.openLink(url) }   // D114: a share link, daysout://r/<code>
                .onChange(of: scenePhase, initial: true) { _, phase in
                    // each time the app comes to the front, start waking the free server (it sleeps after 15 min)
                    if phase == .active {
                        model.clock = .now   // journey round 2: Today / Tomorrow follow the date after a night away
                        model.refreshSky()   // D130: the light is set as the app comes to the front, never while reading
                        Task {
                            await model.wake()
                            await model.sendPendingRatings()   // journey audit: ratings made without signal
                            await model.finishPendingDelete()  // m176: a deletion made without signal
                            await model.loadSafety()   // D118: a reply to a Help & safety message shows on the plan
                        }
                    }
                }
                .onReceive(NotificationCenter.default.publisher(for: ReminderTaps.openStop)) { note in
                    if let id = note.object as? String { model.openStop(id) }   // D118: a rating reminder was tapped
                }
        }
    }
}
