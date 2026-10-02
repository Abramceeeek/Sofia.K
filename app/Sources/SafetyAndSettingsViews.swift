import SwiftUI

/// Screen 13. Safety always goes to a person (D46). The reply never promises anything faster than "a few hours".
/// D110: "Emergency: call 999" and "I feel unsafe / something's wrong" are two separate sections, so nobody
/// mistakes telling us for calling for help.
struct SafetyView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL
    @State private var confirming: Bool
    @State private var message = ""
    @State private var contact = ""
    @State private var reply: String?

    init(confirming: Bool = false) {
        _confirming = State(initialValue: confirming)
    }

    var body: some View {
        NavigationStack {
            Form {
                if let reply {
                    Section { Text(reply) }
                    emergency
                    threads
                } else if confirming {
                    Section {
                        Text("Tell a person what's happening: Abram, or whoever is covering for him. They'll reply within a few hours, here in Help & safety.")
                        TextField("What's happening? (optional)", text: $message, axis: .vertical)
                            .lineLimit(3...6)
                        // D118: so a reply can reach you even if you don't open the app again
                        TextField("Phone or email, so we can reply (optional)", text: $contact)
                            .textContentType(.telephoneNumber)
                            .autocorrectionDisabled()
                            .textInputAutocapitalization(.never)
                        Text("Used only to reply to this message, and deleted once it's sorted (after 30 days at the latest).")
                            .font(.footnote)
                            .foregroundStyle(Theme.inkSoft)
                        PrimaryButton(title: model.busy ? "Sending…" : "Tell a person", disabled: model.busy) {
                            let c = contact.trimmingCharacters(in: .whitespacesAndNewlines)
                            Task { reply = await model.sendSafety(message, contact: c.isEmpty ? nil : String(c.prefix(120))) }
                        }
                    } header: {
                        Text("Something's wrong")
                    }
                    emergency
                } else {
                    emergency
                    threads
                    Section {
                        Text("You feel unsafe, or something has gone wrong on your day out, and it isn't an emergency. A person (Abram, or whoever is covering for him) replies within a few hours, here in Help & safety.")
                        Button {
                            confirming = true
                        } label: {
                            Label("I feel unsafe / something's wrong", systemImage: "hand.raised.fill")
                                .font(.headline)
                                .frame(maxWidth: .infinity, minHeight: 44)
                        }
                        .buttonStyle(.bordered)
                        .tint(Theme.accent)
                    } header: {
                        Text("Not an emergency")
                    }
                    Section("Something else?") {
                        Text("Email \(AppConfig.contactEmail)")
                            .textSelection(.enabled)
                    }
                }
            }
            .themedList()
            .serifTitle("Help & safety")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) { Button("Close") { dismiss() } }
            }
            .task {
                await model.loadSafety()
                model.markSafetySeen()
            }
        }
    }

    /// D118: what the person sent, and each reply, newest first.
    @ViewBuilder private var threads: some View {
        if !model.safetyThreads.isEmpty {
            Section("Your messages") {
                ForEach(model.safetyThreads) { t in
                    VStack(alignment: .leading, spacing: 8) {
                        Text(t.message.isEmpty ? "(No message, just a call for help)" : t.message)
                            .foregroundStyle(Theme.ink)
                        if t.replies.isEmpty {
                            Text("No reply yet. A person replies within a few hours. In an emergency, call 999.")
                                .font(.footnote)
                                .foregroundStyle(Theme.inkSoft)
                        }
                        ForEach(t.replies, id: \.self) { r in
                            VStack(alignment: .leading, spacing: 2) {
                                Text("Reply").font(.footnote.weight(.semibold)).foregroundStyle(Theme.accent)
                                Text(r.text).foregroundStyle(Theme.ink)
                            }
                            .padding(10)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Theme.surfaceHigh, in: RoundedRectangle(cornerRadius: 10))
                        }
                    }
                    .padding(.vertical, 4)
                }
            }
        }
    }

    private var emergency: some View {
        Section {
            Text("If you or someone else is in danger or hurt, call 999 now.")
            Button {
                if let url = URL(string: "tel:999") { openURL(url) }
            } label: {
                Label("Call 999", systemImage: "phone.fill")
                    .font(.headline)
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity, minHeight: 44)
            }
            .buttonStyle(.borderedProminent)
            .tint(Theme.danger)
        } header: {
            Text("Emergency")
        }
    }
}

/// Screen 14: what we store, and Delete my data (App Review 5.1.1(v); UK GDPR erasure).
struct SettingsView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State private var confirmDelete = false

    var body: some View {
        NavigationStack {
            Form {
                Section("What we store") {
                    Text("Your answers, your reactions to places, your choices between example days, anything you add under \"Improve future plans\", your plans and your ratings, and anything you send in Help & safety. We don't ask for your name, email or phone number: the app knows this phone only by a random code. If you leave a phone or email in Help & safety, it's used only to reply, then deleted.")
                }
                Section {
                    // D118: rating reminders can be turned off (or on) here, any time
                    Toggle("Rating reminders after each stop", isOn: Binding(
                        get: { model.remindersOn },
                        set: { on in Task { if on { await model.answerReminders(true) } else { await model.turnRemindersOff() } } }))
                } header: {
                    Text("Reminders")
                } footer: {
                    Text("Set on your phone for the day of your plan. Nothing is sent.")
                }
                Section("Where, and for how long") {
                    Text("On our server in Frankfurt, in the EU, until 31 March 2027.")
                }
                Section("About this test") {
                    Text("A person, Abram, runs this test in London. No AI service reads your answers in this version. Contact: \(AppConfig.contactEmail)")
                    Link("Full privacy notice", destination: AppConfig.baseURL.appendingPathComponent("privacy"))
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
            .themedList()
            .serifTitle("Your data")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) { Button("Close") { dismiss() } }
            }
            .sheet(isPresented: $confirmDelete) {
                DeleteConfirmView { dismiss() }
            }
        }
    }

    private var version: String {
        let info = Bundle.main.infoDictionary
        return "\(info?["CFBundleShortVersionString"] as? String ?? "?") (\(info?["CFBundleVersion"] as? String ?? "?"))"
    }
}

/// D110: deleting needs a deliberate step: type DELETE.
struct DeleteConfirmView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    var onDeleted: () -> Void = {}
    @State private var typed = ""

    private var confirmed: Bool {
        typed.trimmingCharacters(in: .whitespaces).uppercased() == "DELETE"
    }

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    Text("This removes everything we hold about this phone: your answers, reactions, choices, plans and ratings. It happens straight away and can't be undone.")
                }
                Section {
                    TextField("DELETE", text: $typed)
                        .textInputAutocapitalization(.characters)
                        .autocorrectionDisabled()
                } header: {
                    Text("To confirm, type DELETE")
                }
                Section {
                    Button(role: .destructive) {
                        Task {
                            await model.deleteMyData()
                            if model.errorMessage == nil {
                                dismiss()
                                onDeleted()
                            }
                        }
                    } label: {
                        Text(model.busy ? "Deleting…" : "Delete my data")
                            .font(.headline)
                            .frame(maxWidth: .infinity, minHeight: 44)
                    }
                    .disabled(!confirmed || model.busy)
                }
            }
            .themedList()
            .serifTitle("Delete my data")
            .toolbar {
                ToolbarItem(placement: .topBarLeading) { Button("Cancel") { dismiss() } }
            }
        }
    }
}

/// CI screenshots only (`-demo YES -screen <name>`): each screen with the bundled demo data, no network.
/// Names and numbers match design/v0-screens.md and the review page (D110, D112).
struct DemoScreen: View {
    @Environment(AppModel.self) private var model
    let name: String

    var body: some View {
        switch name {
        case "intro": WelcomeView(introAt: 0.7)                                 // 1, the logo drawing (D117)
        case "welcome": WelcomeView()                                           // 1
        case "example": ExampleDayView()                                        // 2a
        case "examplecard":                                                     // 2b (D115): further down screen 2
            if let stop = ExampleDay.plan?.stops.first(where: { $0.rateable && $0.card != nil }) {
                ScrollView { MomentCardContent(stop: stop, showWhy: false).padding(20) }
                    .background(Theme.background)
            }
        case "founder": FounderVideoView()                                      // 2c (D117)
        case "consent": ConsentView()                                           // 3
        case "based", "besthour", "why", "places", "categories", "thisorthat", "learned":  // 3b, 4-7, 6b, 7b
            OnboardingView()
        case "learnedchange":                                                   // 7b, changing something (D117)
            NavigationStack { LearnedStep(startChanging: true).background(Theme.background).serifTitle("So far") }
        case "planform": NavigationStack { PlanFormView() }                     // 8
        case "planlist": HomeView(layout: "list")                               // 9b
        case "reveal": HomeView(reveal: 0.55)                                   // 9c: the plan reveal, part-way (D117)
        case "stop", "rating":                                                  // 10, 11
            // the stop with the most on its card: a best-light window, then any stop that can be rated
            if let stop = model.plan?.stops.first(where: { !($0.bestWindow ?? "").isEmpty })
                ?? model.plan?.stops.first(where: { $0.rateable }) {
                if name == "stop" { NavigationStack { StopView(stop: stop) } } else { RatingView(stop: stop) }
            }
        case "sharecard":                                                       // 11b (D114)
            if let stop = model.plan?.stops.first(where: { $0.rateable && CardPhotos.photo(for: $0.momentId) != nil })
                ?? model.plan?.stops.first(where: { $0.rateable }) {
                ZStack {
                    Theme.background.ignoresSafeArea()
                    ShareCardView(stop: stop, rating: 5)
                        .environment(\.colorScheme, .light)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                        .shadow(radius: 8)
                }
            }
        case "improve": ImproveView()                                           // 12a
        case "improveq": ImproveView(startAt: 0)                                // 12b (D115)
        case "safety": SafetyView()                                             // 13a
        case "safetysend": SafetyView(confirming: true)                         // 13b
        case "safetyreply": SafetyView()                                        // 13c: a reply has come (D118)
        case "settings": SettingsView()                                         // 14a
        case "delete": DeleteConfirmView()                                      // 14b
        default: HomeView()                                                     // 9a ("plan")
        }
    }
}
