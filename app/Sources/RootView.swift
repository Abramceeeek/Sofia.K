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

/// A 1–5 scale as five large, equal buttons (D110: clear 1–5 buttons). With `labels`, each number carries a word;
/// without, the two ends are labelled underneath.
struct ScaleRow: View {
    let low: String
    let high: String
    var labels: [String]? = nil
    @Binding var value: Int?

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                ForEach(1...5, id: \.self) { n in
                    let on = value == n
                    let word: String? = labels.flatMap { $0.count == 5 ? $0[n - 1] : nil }
                    Button {
                        value = n
                    } label: {
                        VStack(spacing: 2) {
                            Text("\(n)").font(.title2.bold())
                            if let word {
                                Text(word)
                                    .font(.caption2)
                                    .lineLimit(1)
                                    .minimumScaleFactor(0.7)
                            }
                        }
                        .frame(maxWidth: .infinity, minHeight: 60)
                        .foregroundStyle(on ? Color.white : Color.primary)
                        .background(on ? Theme.accent : Color(.secondarySystemBackground),
                                    in: RoundedRectangle(cornerRadius: 12))
                        .overlay(RoundedRectangle(cornerRadius: 12)
                            .stroke(on ? Theme.accent : Color(.separator), lineWidth: 1))
                    }
                    .buttonStyle(.borderless)
                    .accessibilityLabel(word.map { "\(n) of 5, \($0)" } ?? "\(n) of 5")
                    .accessibilityAddTraits(on ? .isSelected : [])
                }
            }
            if labels == nil {
                HStack {
                    Text("1 = \(low)")
                    Spacer()
                    Text("5 = \(high)")
                }
                .font(.caption)
                .foregroundStyle(.secondary)
            }
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
