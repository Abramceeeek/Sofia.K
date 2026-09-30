import SwiftUI

@main
struct FaceApp: App {
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
                .onOpenURL { url in model.openLink(url) }   // D114: a share link, daysout://r/<code>
                .onChange(of: scenePhase, initial: true) { _, phase in
                    // each time the app comes to the front, start waking the free server (it sleeps after 15 min)
                    if phase == .active { Task { await model.wake() } }
                }
        }
    }
}
