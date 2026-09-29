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
                case .example: ExampleDayView()
                case .consent: ConsentView()
                case .onboarding: OnboardingView()
                case .home: HomeView()
                }
            }
        }
        .background(Theme.background)
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

/// A 1–5 scale as five large, equal buttons. With `labels`, each number carries a word (the rating: Flat …
/// Unforgettable, D112); without, the two ends are labelled underneath. Text never goes below footnote size.
struct ScaleRow: View {
    let low: String
    let high: String
    var labels: [String]? = nil
    @Binding var value: Int?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            if let labels, labels.count == 5 {
                // Worded scale: one full-width row per step, so the words never shrink
                ForEach(1...5, id: \.self) { n in
                    let on = value == n
                    Button {
                        value = n
                    } label: {
                        HStack(spacing: 14) {
                            Text("\(n)")
                                .font(Theme.title3)
                                .frame(width: 28)
                            Text(labels[n - 1])
                                .font(.body)
                            Spacer()
                            if on { Image(systemName: "checkmark") }
                        }
                        .foregroundStyle(on ? Theme.onAccent : Theme.ink)
                        .padding(.horizontal, 16)
                        .frame(maxWidth: .infinity, minHeight: 52)
                        .background(on ? Theme.accentFill : Theme.surface, in: RoundedRectangle(cornerRadius: 12))
                        .overlay(RoundedRectangle(cornerRadius: 12)
                            .stroke(on ? Theme.accentFill : Theme.outline, lineWidth: 1))
                    }
                    .buttonStyle(.borderless)
                    .accessibilityLabel("\(n) of 5, \(labels[n - 1])")
                    .accessibilityAddTraits(on ? .isSelected : [])
                }
            } else {
                HStack(spacing: 8) {
                    ForEach(1...5, id: \.self) { n in
                        let on = value == n
                        Button {
                            value = n
                        } label: {
                            Text("\(n)")
                                .font(Theme.title3)
                                .frame(maxWidth: .infinity, minHeight: 56)
                                .foregroundStyle(on ? Theme.onAccent : Theme.ink)
                                .background(on ? Theme.accentFill : Theme.surface, in: RoundedRectangle(cornerRadius: 12))
                                .overlay(RoundedRectangle(cornerRadius: 12)
                                    .stroke(on ? Theme.accentFill : Theme.outline, lineWidth: 1))
                        }
                        .buttonStyle(.borderless)
                        .accessibilityLabel("\(n) of 5")
                        .accessibilityAddTraits(on ? .isSelected : [])
                    }
                }
                HStack {
                    Text("1 = \(low)")
                    Spacer()
                    Text("5 = \(high)")
                }
                .font(.footnote)
                .foregroundStyle(Theme.inkSoft)
            }
        }
    }
}

/// The main action at the bottom of a screen: amber, with dark text in both modes.
struct PrimaryButton: View {
    let title: String
    var disabled = false
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.headline)
                .foregroundStyle(disabled ? Theme.inkSoft : Theme.onAccent)
                .frame(maxWidth: .infinity, minHeight: 50)
                .background(disabled ? Theme.surfaceHigh : Theme.accentFill, in: RoundedRectangle(cornerRadius: 14))
        }
        .buttonStyle(.plain)
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
                    .foregroundStyle(Theme.inkSoft)
                Text(text)
                    .foregroundStyle(Theme.ink)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}
