import SwiftUI

/// Screen 1: a person, not a brand. D117: on first opening, the app icon's ring draws itself (about 0.8 s), then
/// settles into its place above the title as the words fade in (0.45 s). A tap skips it; with Reduce Motion it doesn't
/// play. Quiet and the same every time: no bounce, no confetti.
struct WelcomeView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Namespace private var logo
    var introAt: Double?                  // CI screenshots only: the intro frozen part-way (0–1 of the ring drawn)
    @State private var settled = WelcomeView.played
    @State private var drawn: CGFloat = WelcomeView.played ? 1 : 0
    private static var played = false     // once per launch

    var body: some View {
        ZStack {
            VStack(alignment: .leading, spacing: 20) {
                Spacer()
                Group {
                    if settled {
                        LogoRing(progress: 1).matchedGeometryEffect(id: "logo", in: logo)
                    } else {
                        Color.clear
                    }
                }
                .frame(width: 44, height: 44)
                Text("Days out that fit you")
                    .font(Theme.display)
                    .foregroundStyle(Theme.ink)
                Text("We wanted to bring some of the best experiences we've had to you, so you can have them too.")
                    .font(.title3)
                    .foregroundStyle(Theme.ink)
                Text("This is a research test run by a person, Abram, in London. It plans a day out around how you want it to feel, not a list of famous sights.")
                    .foregroundStyle(Theme.inkSoft)
                Spacer()
                PrimaryButton(title: "See an example day") { model.route = .example }
                Button("Skip the example") { model.afterExample() }
                    .frame(maxWidth: .infinity, minHeight: 44)
            }
            .padding(24)
            .opacity(settled ? 1 : 0)
            .allowsHitTesting(settled)
            if !settled {
                Color.clear
                    .contentShape(Rectangle())
                    .onTapGesture { finish(animated: false) }   // tap to skip
                    .accessibilityAddTraits(.isButton)
                    .accessibilityLabel("Days out. Tap to skip")
                LogoRing(progress: drawn)
                    .matchedGeometryEffect(id: "logo", in: logo)
                    .frame(width: 132, height: 132)
                    .allowsHitTesting(false)
            }
        }
        .background(Theme.background)
        .task { await play() }
    }

    private func play() async {
        if let at = introAt {             // CI: show the ring part-drawn, still centred
            settled = false
            drawn = at
            return
        }
        guard !settled else { return }
        WelcomeView.played = true
        if reduceMotion { finish(animated: false); return }
        withAnimation(.easeInOut(duration: 0.8)) { drawn = 1 }
        try? await Task.sleep(for: .milliseconds(850))
        finish(animated: true)
    }

    private func finish(animated: Bool) {
        WelcomeView.played = true
        if animated {
            withAnimation(.easeInOut(duration: 0.45)) { settled = true }
        } else {
            drawn = 1
            settled = true
        }
    }
}

/// The app icon's mark: one ring, drawn from the top clockwise. The stroke is a tenth of the width, as on the icon.
struct LogoRing: View {
    var progress: CGFloat

    var body: some View {
        GeometryReader { g in
            let w = min(g.size.width, g.size.height) * 0.105
            Circle()
                .inset(by: w / 2)
                .trim(from: 0, to: progress)
                .stroke(Theme.brand, style: StrokeStyle(lineWidth: w, lineCap: .round))
                .rotationEffect(.degrees(-90))
        }
        .aspectRatio(1, contentMode: .fit)
        .accessibilityHidden(true)
    }
}

/// Screen 2 (D112): what a plan looks like, before any question. Not personal: built from the average of all
/// answers, bundled with the app, so nothing is sent and nothing is stored.
struct ExampleDayView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        List {
            Section {
                PageTitle(text: ExampleDay.plan?.title ?? "An example day")
                Text("This is what a plan looks like. It isn't planned for you: yours is built from your answers, and from how you rate each stop.")
                    .foregroundStyle(Theme.inkSoft)
            }
            .listRowBackground(Color.clear)
            .listRowSeparator(.hidden)
            if let plan = ExampleDay.plan {
                Section {
                    PlanSummaryCard(plan: plan)
                        .listRowInsets(EdgeInsets())
                        .listRowBackground(Color.clear)
                }
                Section {
                    DayShapeChart(stops: plan.stops, personal: false)
                        .listRowBackground(Theme.surface)
                }
                Section("Stops") {
                    ForEach(plan.stops.indices, id: \.self) { i in
                        StopRow(number: i + 1, stop: plan.stops[i], rated: false)
                            .listRowBackground(Theme.surface)
                    }
                }
                // D115: one stop's card in full, so the special parts show before any question
                if let stop = plan.stops.first(where: { $0.rateable && $0.card != nil }) {
                    Section {
                        MomentCardContent(stop: stop, showWhy: false)
                            .padding(.vertical, 8)
                            .listRowBackground(Theme.background)
                    } header: {
                        Text("Every stop comes with a card like this")
                    }
                }
            }
            Section {
                PrimaryButton(title: "Start") { model.afterExample() }
                    .listRowInsets(EdgeInsets())
                    .listRowBackground(Color.clear)
            }
        }
        .themedList()
    }
}

/// Screen 3: consent (D109, D110). A short plain-English summary, the two required choices where they can't be
/// missed, and the details folded away. The 999 advice lives in Help & safety (screen 13).
/// No AI service reads answers in this version (m117), so there is no separate AI permission yet.
struct ConsentView: View {
    @Environment(AppModel.self) private var model
    @State private var adult = false
    @State private var agree = false
    @State private var showDetails = false

    private let summary = [
        ("person", "A research test run by Abram, one person in London. Nothing is sold."),
        ("list.bullet", "A few quick questions and some London places, then your day plan."),
        ("lock", "We keep your answers to plan your days and to test the idea. No name, email or phone number."),
        ("hand.raised", "Skip any question and stop any time. Settings → Delete my data removes everything."),
    ]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                PageTitle(text: "Before we start")
                ForEach(summary, id: \.1) { item in
                    Label {
                        Text(item.1).foregroundStyle(Theme.ink)
                    } icon: {
                        Image(systemName: item.0).foregroundStyle(Theme.accent)
                    }
                }
                DisclosureGroup("Read the details", isExpanded: $showDetails) {
                    VStack(alignment: .leading, spacing: 14) {
                        InfoBlock(label: "Who runs this",
                                  text: "Abram, an individual in London, testing an idea for a travel planning app. It's research: nothing is sold, and there is no payment either way. Contact: \(AppConfig.contactEmail).")
                        InfoBlock(label: "What you'll do",
                                  text: "Answer a few questions and react to some London places, then get a day plan. If you like, use it on a real day and rate each stop 1–5 after you've been. More questions, all optional, come after your first plan.")
                        InfoBlock(label: "What we keep, and why",
                                  text: "Your answers, reactions, choices and ratings, to plan days that fit you and to test whether this works. The app only knows this phone by a random code. If you speak an answer, your phone turns it into text; the sound isn't saved or sent. If you share a moment, your link carries another random code, so we can count how many people it brings in.")
                        InfoBlock(label: "Where, and for how long",
                                  text: "On our server in Frankfurt, in the EU. Kept until 31 March 2027, then deleted. Anonymised results may be kept.")
                        InfoBlock(label: "What we don't ask for",
                                  text: "Your name, email, phone number, nationality, health details or allergies. Please don't enter them.")
                        Link("Full privacy notice", destination: AppConfig.baseURL.appendingPathComponent("privacy"))
                    }
                    .padding(.top, 10)
                }
                VStack(alignment: .leading, spacing: 12) {
                    Text("To take part, please confirm both")
                        .font(.headline)
                        .foregroundStyle(Theme.ink)
                    Toggle("I'm 18 or over", isOn: $adult)
                    Toggle("I agree to take part", isOn: $agree)
                }
                .padding(16)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 14))
                .overlay(RoundedRectangle(cornerRadius: 14).stroke(Theme.accent, lineWidth: 1))
                PrimaryButton(title: model.busy ? "One moment…" : "Continue", disabled: !(adult && agree) || model.busy) {
                    Task { await model.agree() }
                }
            }
            .padding(20)
        }
        .background(Theme.background)
    }
}
