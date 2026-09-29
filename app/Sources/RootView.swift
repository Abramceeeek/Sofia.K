import SwiftUI

struct RootView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        Group {
            if let screen = model.screen {
                DemoScreen(name: screen)          // CI screenshots only
            } else {
                switch model.route {
                case .welcome: WelcomeView()
                case .consent: ConsentView()
                case .onboarding: OnboardingView()
                case .home: HomeView()
                }
            }
        }
        .overlay(alignment: .top) {
            if model.waking { WakingBanner() }
        }
        .alert("Something went wrong", isPresented: Binding(
            get: { model.errorMessage != nil },
            set: { if !$0 { model.errorMessage = nil } }
        )) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(model.errorMessage ?? "")
        }
    }
}

/// The free server sleeps when nobody has used it for 15 minutes (D109).
struct WakingBanner: View {
    var body: some View {
        HStack(spacing: 8) {
            ProgressView()
            Text("Waking up the planner. This can take up to a minute.")
                .font(.footnote)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
        .background(.regularMaterial, in: Capsule())
        .padding(.top, 8)
        .accessibilityElement(children: .combine)
    }
}

/// A 1–5 scale as five equal buttons, with the ends labelled.
struct ScaleRow: View {
    let low: String
    let high: String
    @Binding var value: Int?

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                ForEach(1...5, id: \.self) { n in
                    Button {
                        value = n
                    } label: {
                        Text("\(n)")
                            .font(.headline)
                            .frame(maxWidth: .infinity, minHeight: 44)
                    }
                    .buttonStyle(.bordered)
                    .tint(value == n ? Theme.accent : .secondary)
                    .accessibilityLabel("\(n) of 5")
                    .accessibilityAddTraits(value == n ? .isSelected : [])
                }
            }
            HStack {
                Text(low)
                Spacer()
                Text(high)
            }
            .font(.caption)
            .foregroundStyle(.secondary)
        }
    }
}

/// The main action at the bottom of a screen.
struct PrimaryButton: View {
    let title: String
    var disabled = false
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.headline)
                .frame(maxWidth: .infinity, minHeight: 44)
        }
        .buttonStyle(.borderedProminent)
        .disabled(disabled)
    }
}

/// A labelled block of text on a card or plan screen.
struct InfoBlock: View {
    let label: String
    let text: String

    var body: some View {
        if !text.isEmpty {
            VStack(alignment: .leading, spacing: 4) {
                Text(label)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.secondary)
                Text(text)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}
