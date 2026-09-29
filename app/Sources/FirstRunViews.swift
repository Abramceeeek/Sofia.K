import SwiftUI

/// Screen 1: a person, not a brand.
struct WelcomeView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Spacer()
            Text("Days out that fit you")
                .font(.largeTitle.bold())
            Text("We wanted to bring some of the best experiences we've had to you, so you can have them too.")
                .font(.title3)
            Text("This is a research test run by a person, Abram, in London. It plans a day out around how you want it to feel, not a list of famous sights.")
                .foregroundStyle(.secondary)
            Spacer()
            PrimaryButton(title: "Get started") { model.route = .consent }
        }
        .padding(24)
    }
}

/// Screen 2: consent (D109). D110: a short plain-English summary, the two required choices where they can't be
/// missed, and the details folded away. The 999 advice lives in Help & safety (screen 14), not here.
/// No AI service reads answers in this version (m117), so there is no separate AI permission yet.
struct ConsentView: View {
    @Environment(AppModel.self) private var model
    @State private var adult = false
    @State private var agree = false
    @State private var showDetails = false

    private let summary = [
        ("person", "A research test run by Abram, one person in London. Nothing is sold."),
        ("list.bullet", "A few questions and some London places, about 5 minutes, then your day plan."),
        ("lock", "We keep your answers to plan your days and to test the idea. No name, email or phone number."),
        ("hand.raised", "Skip any question and stop any time. Settings → Delete my data removes everything."),
    ]

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    ForEach(summary, id: \.1) { item in
                        Label {
                            Text(item.1)
                        } icon: {
                            Image(systemName: item.0).foregroundStyle(Theme.accent)
                        }
                    }
                    DisclosureGroup("Read the details", isExpanded: $showDetails) {
                        VStack(alignment: .leading, spacing: 14) {
                            InfoBlock(label: "Who runs this",
                                      text: "Abram, an individual in London, testing an idea for a travel planning app. It's research: nothing is sold, and there is no payment either way. Contact: \(AppConfig.contactEmail).")
                            InfoBlock(label: "What you'll do",
                                      text: "Answer a few questions and react to some London places, then get a day plan. If you like, use it on a real day and rate each stop 1–5 after you've been. Some more questions, all optional, come after your first plan.")
                            InfoBlock(label: "What we keep, and why",
                                      text: "Your answers, reactions, choices and ratings, to plan days that fit you and to test whether this works. The app only knows this phone by a random code.")
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
                        Toggle("I'm 18 or over", isOn: $adult)
                        Toggle("I agree to take part", isOn: $agree)
                    }
                    .padding(16)
                    .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 14))
                    .overlay(RoundedRectangle(cornerRadius: 14).stroke(Theme.accent, lineWidth: 1))
                    PrimaryButton(title: model.busy ? "One moment…" : "Continue", disabled: !(adult && agree) || model.busy) {
                        Task { await model.agree() }
                    }
                }
                .padding(20)
            }
            .navigationTitle("Before we start")
        }
    }
}
