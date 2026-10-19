import SwiftUI

// Build 2 (Tests A and B inside the app): after "So far", the Test A survey (screen 16); then, for people based in the
// UK, the blind Plan 1 / Plan 2 pair (screens 18-19): a gut choice, "This plan fits me" for each, and why; then which
// one was made from their answers. Both plans are the same text format, with no photos, map, feeling words or reasons,
// so nothing gives the personal one away (validation/test-plan.md).

/// What comes between onboarding and the tabs.
struct FirstPlanFlow: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        Group {
            if !model.surveyDone {
                SurveyView()
            } else {
                PairFlow()
            }
        }
        .background(Theme.background)
        .task { try? await model.loadOnboarding() }
    }
}

// ---- screen 16: the survey -------------------------------------------------------------------------------------

struct SurveyView: View {
    @Environment(AppModel.self) private var model
    @State private var understood: Int?
    @State private var likePerson: Int?
    @State private var typedOrSpoke: String?
    @State private var intrusive = ""

    var body: some View {
        let text = model.onboarding?.survey
        ScrollView {
            VStack(alignment: .leading, spacing: 26) {
                Eyebrow(model.isVisitor ? "Before your first day" : "Before your plan")   // visitors get a first day next
                VStack(alignment: .leading, spacing: 8) {
                    PageTitle(text: text?.title ?? "Three quick questions")
                    Text("About the questions you've just answered. Every one is optional.")
                        .foregroundStyle(Theme.muted)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .settle(0)
                SurveyQuestion(text: text?.understood ?? "I felt understood.") {
                    ScaleRow(low: "not at all", high: "completely", value: $understood)
                }
                .settle(1)
                SurveyQuestion(text: text?.likePerson ?? "It felt like talking to a person, not filling in a form.") {
                    ScaleRow(low: "not at all", high: "completely", value: $likePerson)
                }
                .settle(2)
                SurveyQuestion(text: text?.typedOrSpoke ?? "Did you type or speak your answers?") {
                    HStack(spacing: 8) {
                        ForEach([("typed", "Typed"), ("spoke", "Spoke"), ("both", "Both")], id: \.0) { key, label in
                            Chip(title: label, on: typedOrSpoke == key) { typedOrSpoke = typedOrSpoke == key ? nil : key }
                        }
                    }
                }
                .settle(3)
                SurveyQuestion(text: text?.intrusive ?? "Was anything intrusive or tedious? (optional)") {
                    AnswerBox(text: $intrusive, minHeight: 90, label: "Anything intrusive or tedious")
                }
            }
            .padding(.horizontal, 24)
            .padding(.top, 8)
            .padding(.bottom, 24)
        }
        .scrollDismissesKeyboard(.interactively)
        .statusBarShade()
        .safeAreaInset(edge: .bottom) {
            VStack(spacing: 2) {
                PrimaryButton(title: model.busy ? "Sending…" : "Send", disabled: model.busy || nothingAnswered) {
                    let note = intrusive.trimmingCharacters(in: .whitespacesAndNewlines)
                    Task {
                        await model.sendSurvey(SurveyBody(understood: understood, likePerson: likePerson,
                                                          typedOrSpoke: typedOrSpoke, intrusive: note.isEmpty ? nil : note))
                    }
                }
                QuietButton("Skip these") { Task { await model.sendSurvey(nil) } }
            }
            .padding(.horizontal, 24)
            .padding(.top, 8)
            .background(Theme.background)
        }
    }

    private var nothingAnswered: Bool {
        understood == nil && likePerson == nil && typedOrSpoke == nil
            && intrusive.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }
}

struct SurveyQuestion<Content: View>: View {
    let text: String
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(text)
                .font(Theme.title3)
                .foregroundStyle(Theme.ink)
                .fixedSize(horizontal: false, vertical: true)
            content
        }
    }
}

// ---- screens 18-19: trip intent, the pair, the reveal ----------------------------------------------------------

struct PairFlow: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        Group {
            if let pair = model.pair {
                if pair.done { PairReveal(pair: pair) } else { PairCompare(pair: pair) }
            } else {
                PairIntentView()
            }
        }
        .background(Theme.background)
        .overlay(alignment: .topTrailing) {
            // m176: opened from home, it can be left for later (the comparison stays open on the Trip tab)
            if model.showPair && !(model.pair?.done ?? false) {
                Button("Not now") { model.showPair = false }
                    .font(.subheadline)
                    .foregroundStyle(Theme.accent)
                    .frame(minHeight: 44)
                    .padding(.horizontal, 20)
                    .padding(.top, 8)
            }
        }
    }
}

/// Screen 18: recharge or explore, who might come, anything for sure. Stored with both plans; it changes neither.
struct PairIntentView: View {
    @Environment(AppModel.self) private var model
    @State private var mood: String?
    @State private var company: String?
    @State private var wish = ""

    var body: some View {
        let text = model.onboarding?.testb
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                Eyebrow("Two plans for a Saturday")
                PageTitle(text: text?.intentTitle ?? "Before your plans").settle(0)
                Text("Next you'll see two plans for the same Saturday afternoon, made in different ways. First, three quick things.")
                    .foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
                    .settle(1)
                SurveyQuestion(text: text?.moodPrompt ?? "Recharge or explore?") {
                    HStack(spacing: 8) {
                        ForEach([("recharge", "Recharge"), ("explore", "Explore"), ("either", "Either")], id: \.0) { key, label in
                            Chip(title: label, on: mood == key) { mood = mood == key ? nil : key }
                        }
                    }
                }
                .settle(2)
                SurveyQuestion(text: text?.companyPrompt ?? "Who might come?") {
                    LazyVGrid(columns: [GridItem(.flexible(), spacing: 8), GridItem(.flexible(), spacing: 8)], spacing: 8) {
                        ForEach([("solo", "Just me"), ("friends", "Friends"), ("partner", "A partner"), ("family", "Family")],
                                id: \.0) { key, label in
                            Chip(title: label, on: company == key) { company = company == key ? nil : key }
                        }
                    }
                }
                .settle(3)
                SurveyQuestion(text: text?.wishPrompt ?? "Anything you'd want in it for sure? (optional)") {
                    LineField(placeholder: "A place, a kind of food, a view…", text: $wish)
                }
            }
            .padding(.horizontal, 24)
            .padding(.top, 8)
            .padding(.bottom, 24)
        }
        .scrollDismissesKeyboard(.interactively)
        .statusBarShade()
        .safeAreaInset(edge: .bottom) {
            VStack(spacing: 2) {
                PrimaryButton(title: model.busy ? "Making your two plans…" : "Show me the two plans", disabled: model.busy) {
                    let w = wish.trimmingCharacters(in: .whitespacesAndNewlines)
                    Task { await model.startPair(PairIntent(mood: mood, company: company, wish: w.isEmpty ? nil : w)) }
                }
                QuietButton("Skip the comparison") { model.skipPair() }
            }
            .padding(.horizontal, 24)
            .padding(.top, 8)
            .background(Theme.background)
        }
    }
}

/// Screen 19: the two plans, one at a time, in the same format; then the gut choice, "fits me" for each, and why.
struct PairCompare: View {
    @Environment(AppModel.self) private var model
    let pair: PairResponse
    var demoQuestions = false                  // CI screenshots: both read, scrolled to the questions
    @State private var showing = "1"
    @State private var seen: Set<String> = ["1"]
    @State private var chosen: String?
    @State private var fit1: Int?
    @State private var fit2: Int?
    @State private var why = ""

    var body: some View {
        let text = model.onboarding?.testb
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Eyebrow(pair.title)
                    PageTitle(text: "Plan 1 or Plan 2?").id("top")
                    if let intro = pair.intro ?? text?.intro {
                        Text(intro).foregroundStyle(Theme.inkSoft).fixedSize(horizontal: false, vertical: true)
                    }
                    planSwitch
                    if let plan = pair.plans.first(where: { $0.label == showing }) {
                        PairPlanText(plan: plan)
                            .id(plan.label)
                            .transition(.opacity)
                    }
                    if showing == "1" {
                        SecondaryButton(title: "Now read Plan 2") { show("2", proxy) }
                    }
                    if seen.count == 2 {
                        questions(text).id("questions")
                    } else {
                        Text("Read both plans, then choose.")
                            .font(.footnote)
                            .foregroundStyle(Theme.muted)
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 8)
                .padding(.bottom, 24)
            }
            .scrollDismissesKeyboard(.interactively)
            .onAppear {
                guard demoQuestions else { return }
                seen = ["1", "2"]
                showing = "2"
                chosen = "2"
                fit1 = 3
                fit2 = 4
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) { proxy.scrollTo("questions", anchor: .top) }
            }
        }
        .statusBarShade()
        .safeAreaInset(edge: .bottom) {
            if seen.count == 2 {
                PrimaryButton(title: model.busy ? "Sending…" : "Send", disabled: !ready || model.busy) {
                    guard let chosen, let fit1, let fit2 else { return }
                    Task { await model.sendPairFeedback(chosen: chosen, fit1: fit1, fit2: fit2, why: why, voice: false) }
                }
                .padding(.horizontal, 24)
                .padding(.top, 8)
                .background(Theme.background)
            }
        }
        .animation(Motion.fade, value: showing)
    }

    private var ready: Bool { chosen != nil && fit1 != nil && fit2 != nil }

    private var planSwitch: some View {
        HStack(spacing: 0) {
            ForEach(["1", "2"], id: \.self) { label in
                Button {
                    Haptics.light()
                    showing = label
                    seen.insert(label)
                } label: {
                    Text("Plan \(label)")
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(Theme.ink)
                        .frame(maxWidth: .infinity, minHeight: 44)
                        .background(showing == label ? Theme.surfaceHigh : Color.clear, in: RoundedRectangle(cornerRadius: 10))
                        .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
                .accessibilityAddTraits(showing == label ? .isSelected : [])
            }
        }
        .padding(3)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 13))
    }

    private func show(_ label: String, _ proxy: ScrollViewProxy) {
        showing = label
        seen.insert(label)
        withAnimation(Motion.fade) { proxy.scrollTo("top", anchor: .top) }
    }

    /// 19 Oct review: "Plan 1 fits me", the same statement (Test B's item) with the plan named in it.
    static func fit(_ text: TestBText?, _ n: String) -> String {
        let p = text?.fitPrompt ?? "This plan fits me"
        return p.contains("This plan") ? p.replacingOccurrences(of: "This plan", with: "Plan \(n)") : "\(p): Plan \(n)"
    }

    @ViewBuilder private func questions(_ text: TestBText?) -> some View {
        VStack(alignment: .leading, spacing: 24) {
            Rectangle().fill(Theme.hairline).frame(height: 1)
            SurveyQuestion(text: text?.choosePrompt ?? "Which would you rather do? Go with your gut.") {
                HStack(spacing: 8) {
                    Chip(title: "Plan 1", on: chosen == "1") { chosen = "1" }
                    Chip(title: "Plan 2", on: chosen == "2") { chosen = "2" }
                }
            }
            SurveyQuestion(text: Self.fit(text, "1")) {
                ScaleRow(low: "not at all", high: "completely", value: $fit1)
            }
            SurveyQuestion(text: Self.fit(text, "2")) {
                ScaleRow(low: "not at all", high: "completely", value: $fit2)
            }
            SurveyQuestion(text: text?.whyPrompt ?? "Why? (optional)") {
                AnswerBox(text: $why, minHeight: 90, label: "Why")
            }
        }
    }
}

/// One plan of the pair, as plain text: its summary, then each stop's times, title and lines (the Test B format).
struct PairPlanText: View {
    let plan: PairPlan

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 4) {
                ForEach(plan.summary, id: \.self) { line in
                    Text(line).font(.subheadline).foregroundStyle(Theme.inkSoft)
                }
            }
            ForEach(Array(plan.stops.enumerated()), id: \.offset) { i, stop in
                VStack(alignment: .leading, spacing: 6) {
                    Text("\(i + 1). \(stop.arrive)–\(stop.depart)")
                        .font(.subheadline.monospacedDigit())
                        .foregroundStyle(Theme.muted)
                    Text(stop.title)
                        .font(Theme.title3)
                        .foregroundStyle(Theme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                    ForEach(stop.lines ?? [], id: \.self) { line in
                        Text(line)
                            .font(.subheadline)
                            .foregroundStyle(Theme.inkSoft)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                .padding(16)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
            }
        }
    }
}

/// After the choice: which plan was made from their answers, and on to the plan they chose.
struct PairReveal: View {
    @Environment(AppModel.self) private var model
    let pair: PairResponse

    var body: some View {
        ScrollView {   // journey round 2: with large text, "See your plan" stays reachable
        VStack(alignment: .leading, spacing: 20) {
            Spacer(minLength: 40)
            ArchMark()
            Eyebrow("Thank you")
            ForEach(Array((pair.reveal ?? []).enumerated()), id: \.offset) { i, line in
                Text(line)
                    .font(i == 0 ? Theme.title2 : .body)
                    .foregroundStyle(i == 0 ? Theme.ink : Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
                    .settle(i)
            }
            Spacer(minLength: 24)
            PrimaryButton(title: "See your plan") { model.finishPair() }
        }
        .padding(.horizontal, 24)
        .padding(.bottom, 16)
        .frame(maxWidth: .infinity, alignment: .leading)
        }
        .background(Theme.background)
    }
}
