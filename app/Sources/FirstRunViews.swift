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

/// Screen 2: plain-English consent for the app (D109). A draft for Abram to review before any external build.
/// No AI service reads answers in this version (m117), so there is no separate AI permission yet.
struct ConsentView: View {
    @Environment(AppModel.self) private var model
    @State private var adult = false
    @State private var agree = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    InfoBlock(label: "Who runs this",
                              text: "Abram, an individual in London, testing an idea for a travel planning app. It's research: nothing is sold, and there is no payment either way. Contact: \(AppConfig.contactEmail).")
                    InfoBlock(label: "What you'll do",
                              text: "Answer a few questions and react to some London places (about 15 minutes), then get a day plan. If you like, use it on a real day and rate each stop 1–5.")
                    InfoBlock(label: "What we keep, and why",
                              text: "Your answers, reactions, choices and ratings, to plan days that fit you and to test whether this works. We don't ask for your name, email or phone number: the app only knows this phone by a random code.")
                    InfoBlock(label: "Where, and for how long",
                              text: "On our server in Frankfurt, in the EU. Kept until 31 March 2027, then deleted. Anonymised results may be kept.")
                    InfoBlock(label: "Your choices",
                              text: "Taking part is voluntary. Skip any question. Stop at any time. Settings → Delete my data removes everything straight away.")
                    InfoBlock(label: "If something goes wrong on a day out",
                              text: "In an emergency, call 999. For anything else that feels unsafe, use Help & safety in the app: a person replies within a few hours.")
                    InfoBlock(label: "What we don't ask for",
                              text: "Your nationality, health details or allergies. Please don't enter them.")
                    Toggle("I'm 18 or over", isOn: $adult)
                    Toggle("I've read this and agree to take part", isOn: $agree)
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
