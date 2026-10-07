import SwiftUI

/// Screen 1 (D119, ODYS): the arch lights up, the light spills, then the words settle in. About a second, the same
/// every time it plays (once per launch); a tap skips it; with Reduce Motion it doesn't play. A person, not a brand:
/// Abram's card says who runs the test.
struct WelcomeView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    var introAt: Double?                  // CI screenshots only: the light frozen part-way up the arch
    @State private var light: CGFloat = WelcomeView.played ? 1 : 0
    @State private var pool: CGFloat = WelcomeView.played ? 1 : 0
    @State private var settled = WelcomeView.played
    @State private var askCode = false
    @State private var code = UserDefaults.standard.string(forKey: "testerCode") ?? ""
    @State private var savedCode = UserDefaults.standard.string(forKey: "testerCode") ?? ""
    private static var played = false     // once per launch

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                ArchLogo(light: light, pool: pool)
                    .frame(width: 180, height: 220)
                    .frame(maxWidth: .infinity)
                    .padding(.top, 36)
                Wordmark()
                    .frame(maxWidth: .infinity)
                    .padding(.top, 18)
                    .padding(.bottom, 36)
                VStack(alignment: .leading, spacing: 14) {
                    Text("Days out that fit you.")
                        .font(Theme.display)
                        .foregroundStyle(Theme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                        .accessibilityAddTraits(.isHeader)
                    Text("Tell me how you want a day to feel. I'll plan real moments around it, including how you arrive.")
                        .foregroundStyle(Theme.inkSoft)
                        .fixedSize(horizontal: false, vertical: true)
                    AbramCard()
                        .padding(.top, 14)
                }
                .opacity(settled ? 1 : 0)
                .offset(y: settled || reduceMotion ? 0 : 10)
            }
            .padding(.horizontal, 28)
            .padding(.bottom, 16)
        }
        .scrollBounceBehavior(.basedOnSize)
        .statusBarShade()
        .safeAreaInset(edge: .bottom) {
            VStack(spacing: 2) {
                PrimaryButton(title: "Show me an example day") { model.route = .example }
                HStack {
                    QuietButton("Skip the example") { model.afterExample() }
                    Spacer()
                    // Build 2: an optional code from whoever invited them; it says where they heard of the test
                    QuietButton(savedCode.isEmpty ? "Got a tester code?" : "Code: \(savedCode)") { askCode = true }
                }
            }
            .padding(.horizontal, 28)
            .padding(.top, 8)
            .background(Theme.background)
            .opacity(settled ? 1 : 0)
            .allowsHitTesting(settled)
        }
        .background(Theme.background)
        .overlay {
            if !settled {
                Color.clear
                    .contentShape(Rectangle())
                    .onTapGesture { finish() }     // tap to skip
                    .accessibilityAddTraits(.isButton)
                    .accessibilityLabel("ODYS. Tap to skip")
            }
        }
        .task { await play() }
        .alert("Tester code", isPresented: $askCode) {
            TextField("Code", text: $code)
                .textInputAutocapitalization(.characters)
                .autocorrectionDisabled()
            Button("Save") {
                savedCode = code.trimmingCharacters(in: .whitespacesAndNewlines)
                if savedCode.isEmpty {
                    UserDefaults.standard.removeObject(forKey: "testerCode")
                } else {
                    UserDefaults.standard.set(savedCode, forKey: "testerCode")
                }
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("If someone gave you a code, type it here. It only says where you heard about the test, never who you are.")
        }
    }

    private func play() async {
        if let at = introAt {             // CI: the light part-way up, nothing else yet
            light = at
            pool = 0
            settled = false
            return
        }
        guard !settled else { return }
        WelcomeView.played = true
        if reduceMotion { finish(); return }
        try? await Task.sleep(for: .milliseconds(200))
        withAnimation(.easeIn(duration: 0.6)) { light = 1 }          // Reveal: the light rises in the arch…
        try? await Task.sleep(for: .milliseconds(550))
        withAnimation(.easeOut(duration: 0.35)) { pool = 1 }          // …then spills out in front
        try? await Task.sleep(for: .milliseconds(250))
        withAnimation(Motion.settle) { settled = true }
    }

    private func finish() {
        WelcomeView.played = true
        light = 1
        pool = 1
        settled = true
    }
}

/// "This is a research test, run by one person": who's behind it, before any question (D110). The link to his hello
/// shows only when the video is in the app.
struct AbramCard: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        HStack(alignment: .center, spacing: 14) {
            AbramAvatar()
            VStack(alignment: .leading, spacing: 4) {
                Text("This is a research test, run by one person: Abram, in London.")
                    .font(.subheadline)
                    .foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
                if BundledVideo.exists("founder") || AppConfig.demo {
                    Button("Watch his short hello") { model.route = .founder }
                        .font(.subheadline)
                        .foregroundStyle(Theme.accent)
                        .frame(minHeight: 32)
                }
            }
            Spacer(minLength: 0)
        }
        .padding(14)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
    }
}

/// Screen 2 (D112, D115): what a plan looks like, before any question. Not personal: built from the average of all
/// answers and bundled with the app, so nothing is sent and nothing is stored. One stop's card is shown in full.
struct ExampleDayView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        let plan = ExampleDay.plan
        let featured = plan?.stops.first(where: { $0.rateable && $0.card != nil })
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                BackLink { model.route = .welcome }
                VStack(alignment: .leading, spacing: 8) {
                    Eyebrow("An example day")
                    PageTitle(text: plan?.title ?? "An example day", font: Theme.serif(32, relativeTo: .largeTitle))
                    if let feel = plan?.feelLine, !feel.isEmpty {
                        Text(feel)
                            .font(Theme.italic(20, relativeTo: .title3))
                            .foregroundStyle(Theme.inkSoft)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                .settle(0)
                if let featured {
                    FeaturedStop(stop: featured).settle(1)
                }
                if let plan {
                    VStack(spacing: 0) {
                        ForEach(plan.stops) { s in
                            HStack(alignment: .firstTextBaseline, spacing: 16) {
                                Text(s.arrive)
                                    .font(.subheadline.monospacedDigit())
                                    .foregroundStyle(Theme.muted)
                                    .frame(width: 48, alignment: .leading)
                                Text(s.title).foregroundStyle(Theme.ink).fixedSize(horizontal: false, vertical: true)
                                Spacer(minLength: 8)
                                Text(s.word).font(Theme.italic(16, relativeTo: .callout)).foregroundStyle(Theme.accent)
                            }
                            .padding(.vertical, 12)
                            .overlay(alignment: .bottom) { Rectangle().fill(Theme.hairline).frame(height: 1) }
                        }
                    }
                    .settle(2)
                    Text("This is what a plan looks like. It isn't planned for you: yours is built from your answers, and from how you rate each stop.")
                        .font(.subheadline)
                        .foregroundStyle(Theme.muted)
                        .fixedSize(horizontal: false, vertical: true)
                }
                if let featured {
                    // D115: one stop's card in full, so the special parts show before any question
                    VStack(alignment: .leading, spacing: 14) {
                        Eyebrow("Every stop comes with a card like this")
                        MomentCardContent(stop: featured, showWhy: false)
                    }
                    .padding(.top, 8)
                }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
        .background(Theme.background)
        .statusBarShade()
        .safeAreaInset(edge: .bottom) {
            VStack(spacing: 6) {
                PrimaryButton(title: "Make one that fits me") { model.afterExample() }
                // D119: honest about the length (14 or so questions), where the design said "about a minute"
                Text("About 3 minutes. No account or name needed.")
                    .font(.subheadline)
                    .foregroundStyle(Theme.muted)
            }
            .padding(.horizontal, 24)
            .padding(.top, 10)
            .padding(.bottom, 4)
            .background(Theme.background)
        }
    }
}

/// The example day's first card stop, as a picture with its time and kind of moment.
struct FeaturedStop: View {
    let stop: Stop

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Color.clear
                .frame(height: 190)
                .overlay { MomentImage(momentId: stop.momentId, feel: stop.feelWord) }
                .overlay(alignment: .bottomLeading) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(stop.title)
                            .font(Theme.serif(24, relativeTo: .title2))
                            .foregroundStyle(Theme.ink)
                            .lineLimit(2)
                        Text("\(stop.arrive) · \(stop.word.lowercased())")
                            .font(.subheadline)
                            .foregroundStyle(Theme.inkSoft)
                    }
                    .padding(16)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(LinearGradient(colors: [.clear, Theme.background.opacity(0.9)], startPoint: .top,
                                               endPoint: .bottom))
                }
                .clipped()
            if !stop.what.isEmpty {
                Text(stop.what)
                    .font(.subheadline)
                    .foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
                    .padding(16)
            }
        }
        .background(Theme.surface)
        .clipShape(RoundedRectangle(cornerRadius: 22))
        .accessibilityElement(children: .combine)
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
        ("list.bullet", "A few quick questions and some places, then your plans: a day out, or a whole trip."),
        ("lock", "We keep your answers to plan your days and to test the idea. We don't ask for your name, email or phone number."),
        ("hand.raised", "Skip any question and stop any time. \"Your data\" → Delete my data removes everything."),
    ]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Eyebrow("Before we start")
                PageTitle(text: "A few things first")
                VStack(alignment: .leading, spacing: 16) {
                    ForEach(summary, id: \.1) { item in
                        HStack(alignment: .top, spacing: 14) {
                            Image(systemName: item.0)
                                .foregroundStyle(Theme.accent)
                                .frame(width: 24)
                            Text(item.1)
                                .foregroundStyle(Theme.ink)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                }
                DisclosureGroup(isExpanded: $showDetails) {
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
                                  text: "Your name, email, phone number, nationality, health details or allergies. Please don't enter them. The one exception is your choice: in Help & safety you can leave a phone or email so a person can reply, and it's deleted once it's sorted.")
                        Link("Full privacy notice", destination: AppConfig.baseURL.appendingPathComponent("privacy"))
                            .foregroundStyle(Theme.accent)
                    }
                    .padding(.top, 12)
                } label: {
                    Text("Read the details").foregroundStyle(Theme.accent)
                }
                .tint(Theme.accent)
                VStack(alignment: .leading, spacing: 4) {
                    Text("To take part, please confirm both")
                        .font(.headline)
                        .foregroundStyle(Theme.ink)
                        .padding(.bottom, 6)
                    Toggle("I'm 18 or over", isOn: $adult).frame(minHeight: 44)
                    Rectangle().fill(Theme.hairline).frame(height: 1)
                    Toggle("I agree to take part", isOn: $agree).frame(minHeight: 44)
                }
                .tint(Theme.accent)
                .foregroundStyle(Theme.ink)
                .padding(18)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
                PrimaryButton(title: model.busy ? "One moment…" : "Continue", disabled: !(adult && agree) || model.busy) {
                    Task { await model.agree() }
                }
            }
            .padding(.horizontal, 24)
            .padding(.vertical, 16)
        }
        .background(Theme.background)
        .statusBarShade()
    }
}
