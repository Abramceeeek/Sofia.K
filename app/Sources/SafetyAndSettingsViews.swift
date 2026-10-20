import SwiftUI

/// Screen 13. Safety always goes to a person (D46). The reply never promises anything faster than "a few hours".
/// D110: "Emergency: call 999" and "I feel unsafe or something's wrong" are two separate cards, so nobody mistakes
/// telling us for calling for help. D119 (ODYS): the emergency card is the one red thing in the app.
struct SafetyView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL
    @State private var message = ""
    @State private var contact = ""
    @State private var reply: String?
    @State private var showSettings = false

    /// `prefill` starts the message (a stop card's "Something wrong with this place?").
    init(sent: String? = nil, prefill: String = "") {      // CI screenshots: `sent` shows the reply to a message just sent
        _reply = State(initialValue: sent)
        _message = State(initialValue: prefill)
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    PageTitle(text: "Help & safety")
                    emergency
                    VStack(alignment: .leading, spacing: 12) {
                        Text("I feel unsafe or something's wrong")
                            .font(.headline)
                            .foregroundStyle(Theme.ink)
                        Text("This reaches a real person, not a bot. They'll reply here in Help & safety, usually within a few hours. It isn't watched through the night: a message sent late is answered the next morning.")
                            .font(.subheadline)
                            .foregroundStyle(Theme.inkTertiary)
                            .fixedSize(horizontal: false, vertical: true)
                        if let reply {
                            Text(reply)
                                .font(.subheadline)
                                .foregroundStyle(Theme.inkSoft)
                                .fixedSize(horizontal: false, vertical: true)
                                .padding(14)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Theme.background, in: RoundedRectangle(cornerRadius: 14))
                        } else {
                            TextField("", text: $message, prompt: Text("What's happening? (optional)").foregroundStyle(Theme.muted),
                                      axis: .vertical)
                                .lineLimit(4...8)
                                .foregroundStyle(Theme.ink)
                                .padding(14)
                                .frame(minHeight: 96, alignment: .topLeading)
                                .background(Theme.background, in: RoundedRectangle(cornerRadius: 14))
                                .overlay(RoundedRectangle(cornerRadius: 14).stroke(Theme.outline, lineWidth: 1))
                            // D118: so a reply can reach you even if you don't open the app again
                            LineField(placeholder: "Phone or email (optional)", text: $contact)
                                .textContentType(.telephoneNumber)
                                .autocorrectionDisabled()
                                .textInputAutocapitalization(.never)
                            Text("Used only to reply to this message, and deleted once it's sorted (after 30 days at the latest).")
                                .font(.footnote)
                                .foregroundStyle(Theme.muted)
                                .fixedSize(horizontal: false, vertical: true)
                            SecondaryButton(title: model.busy ? "Sending…" : "Send to a person", disabled: model.busy) {
                                let c = contact.trimmingCharacters(in: .whitespacesAndNewlines)
                                Task { reply = await model.sendSafety(message, contact: c.isEmpty ? nil : String(c.prefix(120))) }
                            }
                        }
                    }
                    .padding(18)
                    .background(Theme.surface, in: RoundedRectangle(cornerRadius: 20))
                    threads
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Something else?").font(.subheadline).foregroundStyle(Theme.muted)
                        Text("Email \(AppConfig.contactEmail)")
                            .foregroundStyle(Theme.ink)
                            .textSelection(.enabled)
                    }
                    QuietButton("Your data · what's stored and how to delete it") { showSettings = true }
                        .frame(maxWidth: .infinity)
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 24)
            }
            .background(Theme.background)
            .scrollDismissesKeyboard(.interactively)
            .navigationTitle("")                    // the title is the page's own, in the serif
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) { Button("Close") { dismiss() } }
            }
            .task {
                await model.loadSafety()
                model.markSafetySeen()
            }
            .sheet(isPresented: $showSettings) { SettingsView().brainFeedback() }
        }
    }

    private var emergency: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Emergency")
                .font(.headline)
                .foregroundStyle(Theme.emergencyTitle)
            Text("If you or someone else is in danger or hurt, call 999 now.")
                .foregroundStyle(Theme.emergencyText)
                .fixedSize(horizontal: false, vertical: true)
            Button {
                if let url = URL(string: "tel:999") { openURL(url) }
            } label: {
                Label("Call 999", systemImage: "phone.fill")
            }
            .buttonStyle(PillStyle(kind: .danger, height: 54))
            // D123: urgent medical help that isn't an emergency (nhs.uk: "call 111 and ask for an interpreter")
            Text("Urgent medical help that isn't an emergency: call NHS 111. You can ask for an interpreter.")
                .font(.subheadline)
                .foregroundStyle(Theme.emergencyText)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.top, 4)
            Button {
                if let url = URL(string: "tel:111") { openURL(url) }
            } label: {
                Label("Call 111", systemImage: "cross.case")
            }
            .buttonStyle(PillStyle(kind: .secondary, height: 48))
            // D127: the team isn't watched overnight, so a free line that is (samaritans.org, checked 20 Oct 2026)
            Button {
                if let url = URL(string: "tel:116123") { openURL(url) }
            } label: {
                Text("Need to talk to someone, day or night? Samaritans answer free on **116 123**.")
                    .font(.subheadline)
                    .foregroundStyle(Theme.emergencyText)
                    .multilineTextAlignment(.leading)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .buttonStyle(.plain)
            .padding(.top, 4)
        }
        .padding(18)
        .background(Theme.emergencyBg, in: RoundedRectangle(cornerRadius: 20))
        .overlay(RoundedRectangle(cornerRadius: 20).stroke(Theme.emergencyBorder, lineWidth: 1))
    }

    /// D118: what the person sent, and each reply, newest first.
    @ViewBuilder private var threads: some View {
        if !model.safetyThreads.isEmpty {
            VStack(alignment: .leading, spacing: 12) {
                Text("Your messages").font(.subheadline).foregroundStyle(Theme.muted)
                ForEach(model.safetyThreads) { t in
                    VStack(alignment: .leading, spacing: 10) {
                        Text(t.message.isEmpty ? "(No message, just a call for help)" : t.message)
                            .foregroundStyle(Theme.ink)
                            .fixedSize(horizontal: false, vertical: true)
                        if t.replies.isEmpty {
                            Text("No reply yet. A person replies, usually within a few hours (the next morning if it was sent late). In an emergency, call 999.")
                                .font(.footnote)
                                .foregroundStyle(Theme.muted)
                        }
                        ForEach(t.replies, id: \.self) { r in
                            VStack(alignment: .leading, spacing: 4) {
                                Eyebrow("Reply", color: Theme.accent)
                                Text(r.text).foregroundStyle(Theme.ink).fixedSize(horizontal: false, vertical: true)
                            }
                            .padding(14)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Theme.selected, in: RoundedRectangle(cornerRadius: 14))
                        }
                    }
                    .surfaceCard(padding: 18)
                }
            }
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
                // 19 Oct review: in short parts, not one paragraph. 20 Oct (round 2): three boxes, so what leaves us has
                // its own place
                Section("What we keep, until 31 March 2027") {
                    Text("Your answers, typed or spoken (as text: the sound stays on your phone and isn't kept).")
                    Text("Your reactions to places, your choices between example days, the short survey and your choice between two plans.")
                    Text("Your plans, your ratings and how each day felt, and anything you add under \"Improve future plans\".")
                    Text("Anything you send in Help & safety.")
                    Text("All of it on our server in Frankfurt, in the EU (run by Render), then deleted.")
                }
                .listRowBackground(Theme.surface)
                Section("What goes to other companies") {
                    Text("A flight or stay search goes to Duffel or LiteAPI, only when you search: the route or city, dates and number of travellers. We keep only which filters you used.")
                    Text("Transport for London and the Met Office give us journey times and the weather. They get places on the plan, nothing about you.")
                    Text("Maps come from Apple. Directions open Apple Maps with the place you're going to, and nothing else from us.")
                }
                .listRowBackground(Theme.surface)
                Section("What we never keep") {
                    Text("Your name, email or phone number. The app knows this phone only by a random code. If you leave a phone or email in Help & safety, it's used only to reply, then deleted.")
                    Text("Your location. A start point you choose for a plan is sent rounded to about 100 m, and not kept.")
                    Text("Your trips: they stay on this phone. The days planned for them are kept like any plan, starting from your stay's location (never its name).")
                }
                .listRowBackground(Theme.surface)
                Section {
                    // D118: rating reminders can be turned off (or on) here, any time
                    Toggle("Rating reminders after each stop", isOn: Binding(
                        get: { model.remindersOn },
                        set: { on in Task { if on { await model.answerReminders(true) } else { await model.turnRemindersOff() } } }))
                        .tint(Theme.accent)
                } header: {
                    Text("Reminders")
                } footer: {
                    Text("Set on your phone for the day of your plan. Nothing is sent.")
                }
                .listRowBackground(Theme.surface)
                Section {
                    // D123: location while you're out, on the phone only
                    Toggle("Use my location while I'm out", isOn: Binding(
                        get: { model.location.wanted },
                        set: { on in
                            if on { model.location.turnOn() } else { model.location.turnOff() }
                            Task { await model.client.event(on ? "location_on" : "location_off") }
                        }))
                        .tint(Theme.accent)
                    if model.location.wanted && model.location.deniedBySettings {
                        Text("Location is off for ODYS in your phone's Settings, so the app can't use it.")
                            .font(.footnote).foregroundStyle(Theme.muted)
                    }
                } header: {
                    Text("Location")
                } footer: {
                    Text("Only while \"Now\" or \"Plan a day\" is open: how far your next stop is, and asking how it felt once you've left. It stays on your phone, except a start point you choose for a plan, sent rounded to about 100 m and not kept.")
                }
                .listRowBackground(Theme.surface)
                Section("About this test") {
                    Text("A person, Abram, runs this test in London. No AI service reads your answers in this version. Contact: \(AppConfig.contactEmail)")
                    Link("Full privacy notice", destination: AppConfig.baseURL.appendingPathComponent("privacy"))
                        .foregroundStyle(Theme.accent)
                }
                .listRowBackground(Theme.surface)
                Section {
                    Button("Delete my data", role: .destructive) { confirmDelete = true }
                } footer: {
                    Text("This removes everything we hold about this phone, straight away. It can't be undone.")
                }
                .listRowBackground(Theme.surface)
                Section {
                    Text("ODYS, version \(version)")
                        .font(.footnote)
                        .foregroundStyle(Theme.muted)
                    // Stage 1: the credits the data's licences ask for
                    Text("Journey times: Powered by TfL Open Data, from the Transport for London Journey Planner API. Weather: Met Office. Card photos: Wikimedia Commons, credited on each card.")
                        .font(.footnote)
                        .foregroundStyle(Theme.muted)
                }
                .listRowBackground(Color.clear)
            }
            .themedList()
            .serifTitle("Your data")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) { Button("Close") { dismiss() } }
            }
            .sheet(isPresented: $confirmDelete) {
                DeleteConfirmView { dismiss() }.brainFeedback()
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
                .listRowBackground(Theme.surface)
                Section {
                    TextField("Type DELETE here", text: $typed)   // 20 Oct (round 2): "DELETE" alone looked already typed
                        .textInputAutocapitalization(.characters)
                        .autocorrectionDisabled()
                } header: {
                    Text("To confirm, type DELETE")
                }
                .listRowBackground(Theme.surface)
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
                .listRowBackground(Theme.surface)
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
/// Names and numbers match design/v0-screens.md and the review page (D110, D112, D119).
struct DemoScreen: View {
    @Environment(AppModel.self) private var model
    let name: String

    var body: some View {
        switch name {
        case "intro": WelcomeView(introAt: 0.55)                                // 1, the arch lighting up (D119)
        case "welcome": WelcomeView()                                           // 1
        case "example": ExampleDayView()                                        // 2a
        case "examplecard":                                                     // 2b (D115): further down screen 2
            if let stop = ExampleDay.plan?.stops.first(where: { $0.rateable && $0.card != nil }) {
                ScrollView { MomentCardContent(stop: stop, showWhy: false).padding(24) }
                    .background(Theme.background)
            }
        case "founder": FounderVideoView()                                      // 2c (D117)
        case "consent": ConsentView()                                           // 3
        case "based", "besthour", "why", "places", "categories", "thisorthat", "learned":  // 3b, 4-7, 6b, 7b
            OnboardingView()
        case "learnedchange":                                                   // 7b, changing something (D117)
            LearnedStep(startChanging: true).background(Theme.background)
        case "planform": HomeViewForm()                                         // 8
        case "plan2": DayScreen(scroll: "stops")                                // 9b: further down, the stops
        case "planmap": DayScreen(layout: "map")                                // 9d
        case "reveal": DayScreen(reveal: 0.45)                                  // 9c: the plan reveal, part-way (D117)
        case "stop":                                                            // 10
            // the stop with the most on its card: a best-light window, then any stop that can be rated
            if let stop = demoStop {
                NavigationStack { StopView(stop: stop) }
            }
        case "stop2":                                                           // 10a: further down the card
            if let stop = demoStop {
                NavigationStack { StopView(stop: stop, demoScroll: "body") }
            }
        case "now": DayScreen().onAppear { model.nowIndex = 1; model.showNow = true }  // 10b (D119): during the day
        case "nowend":                                                          // 10c: a trip's day done, tomorrow next
            DayScreen().onAppear {
                guard let trip = model.trips.first, let day = trip.days.first(where: { $0.index == 1 }) else { return }
                model.useDay(trip, day)
                model.nowIndex = day.plan?.stops.count ?? 0
                model.showNow = true
            }
        case "rating":                                                          // 11
            if let stop = demoStop { RatingView(stop: stop) }
        case "ratingdone":                                                      // 11a (D119): after saving
            if let stop = demoStop { RatingView(stop: stop, onNext: {}, savedRating: 4) }
        case "sharecard":                                                       // 11b (D114, D119)
            if let stop = model.plan?.stops.first(where: { $0.rateable && CardPhotos.photo(for: $0.momentId) != nil })
                ?? model.plan?.stops.first(where: { $0.rateable }) {
                NavigationStack { SharePreview(stop: stop, rating: 5) }
            }
        case "improve": ImproveView()                                           // 12a
        case "improveq": ImproveView(startAt: 0)                                // 12b (D115)
        case "safety": SafetyView()                                             // 13a
        case "safetysend": SafetyView(sent: Self.sentReply)                     // 13b: just sent
        case "safetyreply": SafetyView()                                        // 13c: a reply has come (D118)
        case "settings": SettingsView()                                         // 14a
        case "delete": DeleteConfirmView()                                      // 14b
        case "plan": DayScreen()                                                // 9a
        default: TripDemoScreen(name: name)                                     // D120 and Build 2 (15-31)
        }
    }

    private var demoStop: Stop? {
        model.plan?.stops.first(where: { !($0.bestWindow ?? "").isEmpty && $0.rateable })
            ?? model.plan?.stops.first(where: { $0.rateable })
    }

    /// The Brain's answer to a Help & safety message (brain/notify.py USER_MESSAGE).
    static let sentReply = "If you or someone else is in danger or hurt, call 999 now. A person reads every message and will reply here in Help & safety, and by phone or email if you left one, usually within a few hours. It isn't watched through the night: a message sent late is answered the next morning."
}

/// Screen 8 on its own, as the home screen shows it before there's a plan.
struct HomeViewForm: View {
    var body: some View {
        NavigationStack {
            PlanFormView(onHelp: {}, onData: {})
                .toolbar(.hidden, for: .navigationBar)
                .statusBarShade()
        }
    }
}
