import SwiftUI

/// Placeholder screen. It only proves that GitHub Actions can build, sign and upload the app (D70).
/// The real screens (design/v0-screens.md) start after Test B reports (D65).
struct ContentView: View {
    private var version: String {
        let info = Bundle.main.infoDictionary
        let short = info?["CFBundleShortVersionString"] as? String ?? "?"
        let build = info?["CFBundleVersion"] as? String ?? "?"
        return "\(short) (\(build))"
    }

    var body: some View {
        VStack(spacing: 12) {
            Text("Pipeline check")
                .font(.title2.bold())
            Text("This build only checks that the app can be built, signed and sent to TestFlight. The real app comes after the tests.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
            Text("Version \(version)")
                .font(.footnote.monospacedDigit())
                .foregroundStyle(.secondary)
        }
        .padding(24)
    }
}

#Preview {
    ContentView()
}
