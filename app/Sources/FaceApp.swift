import SwiftUI

@main
struct FaceApp: App {
    @State private var model = AppModel()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(model)
                .tint(Theme.accent)
        }
    }
}

enum Theme {
    /// The one accent colour (design/v0-screens.md): the route line, pins and the "now" state.
    static let accent = Color(red: 0.78, green: 0.36, blue: 0.22)
}
