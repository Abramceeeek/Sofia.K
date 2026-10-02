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
                case .founder: FounderVideoView()
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
        HStack(spacing: 10) {
            ProgressView().tint(Theme.accent)
            Text("Waking up the planner. This can take up to a minute.")
                .font(.footnote)
                .foregroundStyle(Theme.ink)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(Theme.surface, in: Capsule())
        .overlay(Capsule().stroke(Theme.outline, lineWidth: 1))
        .padding(.top, 8)
        .accessibilityElement(children: .combine)
    }
}

/// A 1–5 scale as five equal tiles. With `labels`, each number carries a word (the rating's words, D112); without,
/// the two ends are labelled underneath. Text never goes below footnote size.
struct ScaleRow: View {
    let low: String
    let high: String
    var labels: [String]? = nil
    @Binding var value: Int?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            if let labels, labels.count == 5 {
                ForEach(1...5, id: \.self) { n in
                    SelectTile(on: value == n, radius: 16, minHeight: 52, action: { value = n }) {
                        Text(labels[n - 1])
                            .font(Theme.option)
                            .foregroundStyle(Theme.ink)
                            .frame(maxWidth: .infinity)
                    }
                    .accessibilityLabel("\(n) of 5, \(labels[n - 1])")
                }
            } else {
                HStack(spacing: 8) {
                    ForEach(1...5, id: \.self) { n in
                        SelectTile(on: value == n, radius: 16, minHeight: 56, action: { value = n }) {
                            Text("\(n)")
                                .font(Theme.title3)
                                .foregroundStyle(Theme.ink)
                                .frame(maxWidth: .infinity)
                        }
                        .accessibilityLabel("\(n) of 5")
                    }
                }
                HStack {
                    Text("1 = \(low)")
                    Spacer()
                    Text("5 = \(high)")
                }
                .font(.footnote)
                .foregroundStyle(Theme.muted)
            }
        }
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
                    .font(.subheadline)
                    .foregroundStyle(Theme.muted)
                Text(text)
                    .foregroundStyle(Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

/// Rows of label and text on one card, divided by hairlines (the moment card's "Best time and light", "Cost" …).
struct DetailRows: View {
    let rows: [(String, String)]

    var body: some View {
        let shown = rows.filter { !$0.1.isEmpty }
        VStack(alignment: .leading, spacing: 0) {
            ForEach(shown.indices, id: \.self) { i in
                VStack(alignment: .leading, spacing: 4) {
                    Text(shown[i].0).font(.subheadline).foregroundStyle(Theme.muted)
                    Text(shown[i].1)
                        .foregroundStyle(Theme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(.horizontal, 18)
                .padding(.vertical, 16)
                .frame(maxWidth: .infinity, alignment: .leading)
                if i < shown.count - 1 {
                    Rectangle().fill(Theme.hairline).frame(height: 1)
                }
            }
        }
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
    }
}
