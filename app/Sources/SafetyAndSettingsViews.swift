import SwiftUI

/// Screen 19. Safety always goes to a person (D46). The reply never promises anything faster than "a few hours".
struct SafetyView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL
    @State private var confirming = false
    @State private var message = ""
    @State private var reply: String?

    var body: some View {
        NavigationStack {
            Form {
                if let reply {
                    Section { Text(reply) }
                    Section { call999 }
                } else if confirming {
                    Section {
                        Text("If you or someone else is in danger or hurt, call 999 now.")
                            .font(.headline)
                    }
                    Section { call999 }
                    Section("Tell a person on our team (the message is optional)") {
                        TextField("What's happening?", text: $message, axis: .vertical)
                            .lineLimit(3...6)
                    }
                    Section {
                        PrimaryButton(title: model.busy ? "Sending…" : "Tell a person", disabled: model.busy) {
                            Task { reply = await model.sendSafety(message) }
                        }
                    }
                } else {
                    Section {
                        Button(role: .destructive) {
                            confirming = true
                        } label: {
                            Label("I feel unsafe / something's wrong", systemImage: "exclamationmark.triangle.fill")
                                .font(.headline)
                                .frame(minHeight: 44)
                        }
                    }
                    Section("Something else?") {
                        Text("Email \(AppConfig.contactEmail)")
                            .textSelection(.enabled)
                    }
                }
            }
            .navigationTitle("Help & safety")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) { Button("Close") { dismiss() } }
            }
        }
    }

    private var call999: some View {
        Button {
            if let url = URL(string: "tel:999") { openURL(url) }
        } label: {
            Label("Call 999", systemImage: "phone.fill")
                .frame(minHeight: 44)
        }
    }
}

/// Screen 20: what we store, and Delete my data (App Review 5.1.1(v); UK GDPR erasure).
struct SettingsView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State private var confirmDelete = false

    var body: some View {
        NavigationStack {
            Form {
                Section("What we store") {
                    Text("Your answers, your reactions to the 16 places, your this-or-that choices, your \"about you\" answers, your plans and your ratings. No name, email or phone number: the app knows this phone only by a random code.")
                }
                Section("Where, and for how long") {
                    Text("On our server in Frankfurt, in the EU, until 31 March 2027.")
                }
                Section("About this test") {
                    Text("A person, Abram, runs this test in London. No AI service reads your answers in this version. Contact: \(AppConfig.contactEmail)")
                }
                Section {
                    Button("Delete my data", role: .destructive) { confirmDelete = true }
                } footer: {
                    Text("This removes everything we hold about this phone, straight away. It can't be undone.")
                }
                Section {
                    Text("Version \(version)")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Your data")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) { Button("Close") { dismiss() } }
            }
            .confirmationDialog("Delete everything we hold about this phone?", isPresented: $confirmDelete,
                                titleVisibility: .visible) {
                Button("Delete my data", role: .destructive) {
                    Task {
                        await model.deleteMyData()
                        dismiss()
                    }
                }
                Button("Cancel", role: .cancel) {}
            }
        }
    }

    private var version: String {
        let info = Bundle.main.infoDictionary
        return "\(info?["CFBundleShortVersionString"] as? String ?? "?") (\(info?["CFBundleVersion"] as? String ?? "?"))"
    }
}

/// CI screenshots only (`-demo YES -screen <name>`): each screen with the bundled demo data, no network.
struct DemoScreen: View {
    @Environment(AppModel.self) private var model
    let name: String

    var body: some View {
        switch name {
        case "welcome": WelcomeView()
        case "consent": ConsentView()
        case "besthour", "why", "places", "thisorthat", "aboutyou", "photos": OnboardingView()
        case "planform": NavigationStack { PlanFormView() }
        case "stop", "rating":
            if let stop = model.plan?.stops.first(where: { $0.rateable }) {
                if name == "stop" { NavigationStack { StopView(stop: stop) } } else { RatingView(stop: stop) }
            }
        case "shotcard":
            if let card = model.onboarding?.exampleShotCard {
                NavigationStack {
                    ScrollView { ShotCardView(card: card).padding(20) }
                        .navigationTitle("Shot card")
                }
            }
        case "safety": SafetyView()
        case "settings": SettingsView()
        default: HomeView()
        }
    }
}
