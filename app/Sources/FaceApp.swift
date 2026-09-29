import SwiftUI

@main
struct FaceApp: App {
    @State private var model = AppModel()

    init() {
        Theme.applyAppearance()
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(model)
                .tint(Theme.accent)
        }
    }
}
