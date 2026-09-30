import SwiftUI
import MapKit

/// Screens 4–7: onboarding up to the first plan (Test A inside the app, D109). Each step is sent as it finishes.
/// D112: a great moment, why, 6 places and 5 "this or that" tasks, then the plan. The other places and tasks
/// are in "Improve future plans" (screen 12).
struct OnboardingView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        NavigationStack {
            Group {
                if let onboarding = model.onboarding {
                    switch model.step {
                    case .bestHour: BestHourStep()
                    case .why: WhyStep()
                    case .places:
                        PlacesStep(places: onboarding.swipePlaces) { await model.finishPlaces() }
                    case .thisOrThat:
                        ThisOrThatStep(tasks: onboarding.conjointTasks, doneText: "That's everything. Next: your first plan.",
                                       doneButton: "Plan my first day") { await model.finishThisOrThat() }
                    }
                } else {
                    OnboardingLoading()
                }
            }
            .background(Theme.background)
            .serifTitle(model.step.title)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Text("Step \(model.step.rawValue + 1) of \(Step.allCases.count)")
                        .font(.footnote.monospacedDigit())
                        .foregroundStyle(Theme.inkSoft)
                }
            }
        }
    }
}

/// Loads the questions once; if that fails, says so and offers "Try again" instead of spinning for ever.
struct OnboardingLoading: View {
    @Environment(AppModel.self) private var model
    @State private var failed = false

    var body: some View {
        VStack(spacing: 16) {
            if failed {
                Text("The questions didn't load.")
                    .font(Theme.title3)
                    .foregroundStyle(Theme.ink)
                PrimaryButton(title: "Try again", disabled: model.busy) {
                    Task { await load() }
                }
            } else {
                ProgressView("Loading the questions…")
            }
        }
        .padding(20)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .task { await load() }
    }

    private func load() async {
        failed = false
        await model.run { try await model.loadOnboarding() }
        failed = model.onboarding == nil
    }
}

/// A progress bar with "4 of 6" under it. No timers anywhere (design brief).
struct SectionProgress: View {
    let done: Int
    let total: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            ProgressView(value: Double(done), total: Double(max(total, 1)))
                .tint(Theme.accent)
            Text("\(min(done + 1, total)) of \(total)")
                .font(.footnote.monospacedDigit())
                .foregroundStyle(Theme.inkSoft)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(min(done + 1, total)) of \(total)")
    }
}

// ---- 4. A great moment (D112: was "The best hour") -----------------------------------------------

struct BestHourStep: View {
    @Environment(AppModel.self) private var model
    @State private var dictation = Dictation()

    var body: some View {
        @Bindable var model = model
        let q = model.onboarding?.openQuestions.first
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(q?.text ?? "Tell us about a great moment from a recent day out.")
                    .font(Theme.title3)
                    .foregroundStyle(Theme.ink)
                if let examples = q?.examples, !examples.isEmpty {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("For example")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(Theme.inkSoft)
                        ForEach(examples, id: \.self) { line in
                            Text("“\(line)”")
                                .font(.subheadline)
                                .foregroundStyle(Theme.inkSoft)
                        }
                    }
                }
                if dictation.available {
                    // D115: speaking is the easy way in, so it comes first and big; typing stays below
                    TellItButton(listening: dictation.listening) {
                        if dictation.listening {
                            dictation.stop()
                        } else {
                            let before = model.bestHour.trimmingCharacters(in: .whitespacesAndNewlines)
                            Task {
                                await dictation.start { text in
                                    model.bestHour = before.isEmpty ? text : before + " " + text
                                    model.bestHourVoice = true
                                }
                            }
                        }
                    }
                    Text("Your phone turns your words into text. The sound isn't saved or sent.")
                        .font(.footnote)
                        .foregroundStyle(Theme.inkSoft)
                }
                if let problem = dictation.problem {
                    Text(problem).font(.footnote).foregroundStyle(Theme.ink)
                }
                Text(dictation.available ? "Or type it" : "Type it, or tap the mic on your keyboard")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(Theme.inkSoft)
                TextEditor(text: $model.bestHour)
                    .scrollContentBackground(.hidden)
                    .frame(minHeight: 110)
                    .padding(8)
                    .background(Theme.surface, in: RoundedRectangle(cornerRadius: 10))
                    .overlay(RoundedRectangle(cornerRadius: 10).stroke(Theme.outline, lineWidth: 1))
                    .accessibilityLabel("Your answer")
                Text("A few words is fine.")
                    .font(.footnote)
                    .foregroundStyle(Theme.inkSoft)
                if !model.bestHour.isEmpty {
                    Text(q?.followUp ?? "Is there anything else you'd like to add about that?")
                        .foregroundStyle(Theme.ink)
                    TextEditor(text: $model.bestHourMore)
                        .scrollContentBackground(.hidden)
                        .frame(minHeight: 80)
                        .padding(8)
                        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 10))
                        .overlay(RoundedRectangle(cornerRadius: 10).stroke(Theme.outline, lineWidth: 1))
                        .accessibilityLabel("Anything else")
                }
                PrimaryButton(title: "Next", disabled: model.busy || model.bestHour.isEmpty) {
                    dictation.stop()
                    Task { await model.finishBestHour() }
                }
                Button("Skip this question") {
                    dictation.stop()
                    model.bestHour = ""
                    model.bestHourMore = ""
                    model.bestHourVoice = false
                    Task { await model.finishBestHour() }
                }
                .frame(maxWidth: .infinity, minHeight: 44)
                .disabled(model.busy)
            }
            .padding(20)
        }
    }
}

/// D115: the big "Tell it instead" button: a mic in an amber circle, outlined in amber so it can't be missed.
struct TellItButton: View {
    let listening: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 14) {
                Image(systemName: listening ? "stop.fill" : "mic.fill")
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(Theme.onAccent)
                    .frame(width: 44, height: 44)
                    .background(Circle().fill(Theme.accentFill))
                VStack(alignment: .leading, spacing: 2) {
                    Text(listening ? "Listening… tap when you're done" : "Tell it instead")
                        .font(.headline)
                        .foregroundStyle(Theme.ink)
                    Text(listening ? "Say it the way you'd tell a friend." : "Speak your answer. No typing.")
                        .font(.footnote)
                        .foregroundStyle(Theme.inkSoft)
                }
                Spacer()
            }
            .padding(12)
            .frame(maxWidth: .infinity, minHeight: 68)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
            .overlay(RoundedRectangle(cornerRadius: 16).stroke(Theme.accentFill, lineWidth: 2))
        }
        .buttonStyle(.plain)
        .accessibilityLabel(listening ? "Stop listening" : "Tell it instead: speak your answer")
    }
}

// ---- 5. How you want to feel (D115: was "Why you go out"; up to two, or none) ------------------------

enum Labels {
    /// D115: feelings, each mapped onto the model's features in brain/reasons.py (FEELINGS)
    static let why = ["restored": "Restored", "excited": "Excited", "connected": "Connected",
                      "curious": "Curious", "peaceful": "Peaceful"]
    static let whyNote = ["restored": "Rested and recharged, back to yourself",
                          "excited": "Heart going, something to talk about",
                          "connected": "Close to the people you're with",
                          "curious": "Finding out something new",
                          "peaceful": "Calm and unhurried, away from the crowds"]
    static let budget = [("under_20", "Under £20"), ("20_40", "£20–40"), ("40_70", "£40–70"), ("70_plus", "£70 or more")]
    static let company = [("solo", "On my own"), ("friends", "Friends"), ("partner", "A partner"), ("family", "Family")]
    static let chronotype = [("morning", "Morning person"), ("night", "Night person"), ("neither", "Neither")]
    static let activity = [("gentle", "Gentle"), ("medium", "In between"), ("full_on", "Full on")]
    static let grewUp = [("big_city", "A big city"), ("town", "A town"), ("coast", "By the coast"),
                         ("countryside", "The countryside")]
    static let reactions = [("loved", "Loved it"), ("fine", "It was fine"), ("didnt_enjoy", "Didn't enjoy it"),
                            ("havent_been", "Haven't been")]
    /// The rating's words (D115: one dimension, was Flat · Pleasant · Restorative · Vivid · Unforgettable), 1–5.
    static let feel = ["Flat", "Fine", "Good", "Great", "Unforgettable"]
    /// The "this or that" attributes, always in the same order with the same icons (D95).
    static let attributeIcons = ["arrow.triangle.swap", "cloud.sun", "gauge.with.dots.needle.33percent",
                                 "person.3", "sterlingsign.circle", "figure.walk"]
}

struct WhyStep: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        let choices = model.onboarding?.whyTravel
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                Text(choices?.prompt ?? "How do you most want to feel on a day out? Pick up to two, or none.")
                    .font(Theme.title3)
                    .foregroundStyle(Theme.ink)
                ForEach(choices?.options ?? [], id: \.self) { key in
                    let on = model.why.contains(key)
                    Button {
                        if on { model.why.removeAll { $0 == key } } else if model.why.count < 2 { model.why.append(key) }
                    } label: {
                        HStack {
                            VStack(alignment: .leading, spacing: 2) {
                                Text(Labels.why[key] ?? key).font(.headline)
                                if let note = Labels.whyNote[key] {
                                    Text(note).font(.footnote).opacity(0.8)
                                }
                            }
                            Spacer()
                            Image(systemName: on ? "checkmark.circle.fill" : "circle")
                        }
                        .padding(.vertical, 6)
                        .foregroundStyle(on ? Theme.onAccent : Theme.ink)
                        .padding(.horizontal, 16)
                        .frame(maxWidth: .infinity, minHeight: 50)
                        .background(on ? Theme.accentFill : Theme.surface, in: RoundedRectangle(cornerRadius: 12))
                        .overlay(RoundedRectangle(cornerRadius: 12).stroke(on ? Theme.accentFill : Theme.outline, lineWidth: 1))
                    }
                    .buttonStyle(.plain)
                    .accessibilityAddTraits(on ? .isSelected : [])
                }
                PrimaryButton(title: model.why.isEmpty ? "None of these" : "Next") { model.next() }
                    .padding(.top, 8)
            }
            .padding(20)
        }
    }
}

// ---- 6. Places you've been (6 before the plan, 4 more in screen 12; D112) -------------------------

struct PlacesStep: View {
    @Environment(AppModel.self) private var model
    let places: [SwipePlace]
    let onDone: () async -> Void
    @State private var index = 0

    var body: some View {
        VStack(spacing: 14) {
            if index < places.count {
                let place = places[index]
                SectionProgress(done: index, total: places.count)
                Spacer()
                Text(place.name)
                    .font(Theme.title)
                    .foregroundStyle(Theme.ink)
                    .multilineTextAlignment(.center)
                Text(model.onboarding?.swipe?.prompt ?? "Have you been? How did it feel?")
                    .foregroundStyle(Theme.inkSoft)
                Spacer()
                ForEach(Labels.reactions, id: \.0) { pair in
                    Button {
                        react(place, pair.0)
                    } label: {
                        Text(pair.1)
                            .foregroundStyle(Theme.ink)
                            .frame(maxWidth: .infinity, minHeight: 48)
                            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 12))
                            .overlay(RoundedRectangle(cornerRadius: 12).stroke(Theme.outline, lineWidth: 1))
                    }
                    .buttonStyle(.plain)
                }
                HStack {
                    Button("Back") { index -= 1 }
                        .disabled(index == 0)
                    Spacer()
                    Button("Not sure, skip") { react(place, "skip") }
                }
                .font(.subheadline)
                .frame(minHeight: 44)
                Button("Skip the rest") { Task { await onDone() } }   // D112: the unanswered ones aren't sent
                    .font(.subheadline)
                    .frame(maxWidth: .infinity, minHeight: 44)
                    .disabled(model.busy)
            } else {
                SectionProgress(done: places.count, total: places.count)
                Spacer()
                Text("That's all \(places.count) places. Thank you.")
                    .font(Theme.title3)
                    .foregroundStyle(Theme.ink)
                Spacer()
                PrimaryButton(title: "Next", disabled: model.busy) { Task { await onDone() } }
                Button("Back") { index = max(places.count - 1, 0) }
                    .frame(minHeight: 44)
            }
        }
        .padding(20)
    }

    private func react(_ place: SwipePlace, _ reaction: String) {
        model.reactions[place.item] = reaction
        index += 1
    }
}

// ---- 7. This or that: made-up example days (5 before the plan, 5 more in screen 12; D112) --------------

struct ThisOrThatStep: View {
    @Environment(AppModel.self) private var model
    let tasks: [ConjointTask]
    let doneText: String
    let doneButton: String
    let onDone: () async -> Void
    @State private var index = 0

    var body: some View {
        let label = model.onboarding?.conjoint?.optionLabel ?? "Example day"
        ScrollView {
            VStack(spacing: 14) {
                if index < tasks.count {
                    let task = tasks[index]
                    SectionProgress(done: index, total: tasks.count)
                    Text(model.onboarding?.conjoint?.prompt ?? "Which day sounds more like you? There's no right answer.")
                        .font(Theme.title3)
                        .foregroundStyle(Theme.ink)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    DayOption(label: "\(label) A", text: task.a) { choose(task, "A") }
                    DayOption(label: "\(label) B", text: task.b) { choose(task, "B") }
                    HStack {
                        Button("Back") { index -= 1 }
                            .disabled(index == 0)
                        Spacer()
                        Button(model.onboarding?.conjoint?.noPreference ?? "No preference") { choose(task, "N") }
                            .buttonStyle(.bordered)
                    }
                    .frame(minHeight: 44)
                } else {
                    SectionProgress(done: tasks.count, total: tasks.count)
                    Text(doneText)
                        .font(Theme.title3)
                        .foregroundStyle(Theme.ink)
                        .padding(.vertical, 40)
                    PrimaryButton(title: model.busy ? "One moment…" : doneButton, disabled: model.busy) {
                        Task { await onDone() }
                    }
                    Button("Back") { index = max(tasks.count - 1, 0) }
                        .frame(minHeight: 44)
                }
            }
            .padding(20)
        }
    }

    private func choose(_ task: ConjointTask, _ choice: String) {
        model.choices[task.task] = choice    // "N": no preference (D110), left out of the fit
        index += 1
    }
}

struct DayOption: View {
    let label: String
    let text: String
    let action: () -> Void

    var body: some View {
        let parts = text.components(separatedBy: "; ")
        Button(action: action) {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text(label).font(.headline).foregroundStyle(Theme.accent)
                    Spacer()
                    Text("Made up").font(.footnote).foregroundStyle(Theme.inkSoft)
                }
                ForEach(parts.indices, id: \.self) { i in
                    Label(parts[i].prefix(1).uppercased() + String(parts[i].dropFirst()),
                          systemImage: i < Labels.attributeIcons.count ? Labels.attributeIcons[i] : "circle")
                        .foregroundStyle(Theme.ink)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 14))
            .overlay(RoundedRectangle(cornerRadius: 14).stroke(Theme.outline, lineWidth: 1))
        }
        .buttonStyle(.plain)
        .accessibilityHint("Choose this made-up day")
    }
}

// ---- 12. Improve future plans (D115): "Want us to learn you better?", one question at a time ---------------

/// An invitation, then one quick question per screen: tap an answer and the next one comes. Skip any, stop any time;
/// what's answered is saved. Nine taps is about 30 seconds. The 4 more places and 5 more example days come after,
/// as their own optional step (about a minute).
struct ImproveView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    var startAt = -1               // CI screenshots: 0 opens the first question
    @State private var step = -2   // -2: not set yet (startAt is used); -1: the invitation
    @State private var morePlaces = false
    @State private var moreTasks = false

    private enum Q: CaseIterable { case budget, company, chronotype, activity, fields, grewUp, foods, photos, shotCard }

    var body: some View {
        let current = step == -2 ? startAt : step
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    if current < 0 {
                        invitation
                    } else if current < Q.allCases.count {
                        SectionProgress(done: current, total: Q.allCases.count)
                        question(Q.allCases[current])
                        HStack {
                            Button("Back") { go(current - 1) }.disabled(current == 0)
                            Spacer()
                            Button("Skip") { go(current + 1) }
                        }
                        .font(.subheadline)
                        .frame(minHeight: 44)
                        Button("Stop here, keep my answers") { Task { await save(done: false) } }
                            .font(.subheadline)
                            .frame(maxWidth: .infinity, minHeight: 44)
                            .disabled(model.busy)
                    } else {
                        finished
                    }
                }
                .padding(20)
            }
            .background(Theme.background)
            .serifTitle("Improve future plans")
            .toolbar {
                ToolbarItem(placement: .topBarLeading) { Button("Close") { dismiss() } }
            }
            .sheet(isPresented: $morePlaces) {
                NavigationStack {
                    PlacesStep(places: model.onboarding?.swipePlacesLater ?? []) {
                        await model.finishMorePlaces()
                        if model.errorMessage == nil { morePlaces = false }
                    }
                    .background(Theme.background)
                    .serifTitle("More places")
                }
            }
            .sheet(isPresented: $moreTasks) {
                NavigationStack {
                    ThisOrThatStep(tasks: model.onboarding?.conjointTasksLater ?? [],
                                   doneText: "Thank you. Your next plans will use these.", doneButton: "Save") {
                        await model.finishMoreTasks()
                        if model.errorMessage == nil { moreTasks = false }
                    }
                    .background(Theme.background)
                    .serifTitle("More example days")
                }
            }
        }
    }

    private func go(_ next: Int) {
        withAnimation { step = max(0, next) }
        if next >= Q.allCases.count { Task { await model.saveImprovements(done: true) } }
    }

    private func save(done: Bool) async {
        await model.saveImprovements(done: done)
        if model.errorMessage == nil { dismiss() }
    }

    private var invitation: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Want us to learn you better?")
                .font(Theme.title)
                .foregroundStyle(Theme.ink)
            Text("About 30 seconds. One quick question at a time: your budget, who you go with, your pace, what interests you. Skip any, stop any time.")
                .foregroundStyle(Theme.ink)
            Text("Your next plans use every answer.")
                .font(.footnote)
                .foregroundStyle(Theme.inkSoft)
            PrimaryButton(title: model.improved ? "Change my answers" : "Start") { go(0) }
            Button("Not now") { dismiss() }
                .frame(maxWidth: .infinity, minHeight: 44)
        }
    }

    private var finished: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Thank you.")
                .font(Theme.title)
                .foregroundStyle(Theme.ink)
            Text("Your next plans will use these answers.")
                .foregroundStyle(Theme.ink)
            let later = model.onboarding?.swipePlacesLater ?? []
            let laterTasks = model.onboarding?.conjointTasksLater ?? []
            if !later.isEmpty || !laterTasks.isEmpty {
                Text("Want to go further? About a minute more.")
                    .font(.headline)
                    .foregroundStyle(Theme.ink)
                    .padding(.top, 8)
                if !later.isEmpty {
                    Button { morePlaces = true } label: {
                        MoreRow(title: "\(later.count) more places you may have been", done: model.morePlacesDone)
                    }
                    .surfaceCard()
                }
                if !laterTasks.isEmpty {
                    Button { moreTasks = true } label: {
                        MoreRow(title: "\(laterTasks.count) more made-up example days", done: model.moreTasksDone)
                    }
                    .surfaceCard()
                }
            }
            PrimaryButton(title: model.busy ? "Saving…" : "Done", disabled: model.busy) {
                Task { await save(done: true) }
            }
        }
    }

    @ViewBuilder private func question(_ q: Q) -> some View {
        @Bindable var model = model
        let about = Dictionary(uniqueKeysWithValues: (model.onboarding?.aboutYou ?? []).map { ($0.key, $0) })
        let photos = model.onboarding?.photos ?? []
        switch q {
        case .budget:
            QuestionTitle(about["budget_band"]?.text ?? "About how much do you like to spend on a day out?")
            ChoiceList(options: Labels.budget, selected: model.profile.budgetBand) { model.profile.budgetBand = $0; go(1) }
        case .company:
            QuestionTitle(about["company"]?.text ?? "Who do you usually go with?")
            ChoiceList(options: Labels.company, selected: model.profile.company) { model.profile.company = $0; go(2) }
        case .chronotype:
            QuestionTitle(about["chronotype"]?.text ?? "Are you a morning or a night person?")
            ChoiceList(options: Labels.chronotype, selected: model.profile.chronotype) { model.profile.chronotype = $0; go(3) }
        case .activity:
            QuestionTitle(about["activity"]?.text ?? "How active do you like a day out to be?")
            ChoiceList(options: Labels.activity, selected: model.profile.activity) { model.profile.activity = $0; go(4) }
        case .fields:
            if let fields = model.onboarding?.fields {
                QuestionTitle(fields.question)
                ForEach(fields.options.filter { $0.key != "none" }) { option in
                    let on = model.profile.fields.contains(option.key)
                    ChoiceRow(label: option.label, on: on) {
                        model.profile.fields.removeAll { $0 == option.key }
                        if !on { model.profile.fields.append(option.key) }
                    }
                }
                Text(fields.note).font(.footnote).foregroundStyle(Theme.inkSoft)
                PrimaryButton(title: model.profile.fields.isEmpty ? "None of these" : "Next") { go(5) }
            } else {
                PrimaryButton(title: "Next") { go(5) }
            }
        case .grewUp:
            QuestionTitle(about["grew_up"]?.text ?? "Where did you grow up?")
            ChoiceList(options: Labels.grewUp, selected: model.profile.grewUp) { model.profile.grewUp = $0; go(6) }
            if let note = about["grew_up"]?.note { Text(note).font(.footnote).foregroundStyle(Theme.inkSoft) }
        case .foods:
            QuestionTitle(about["foods_avoided"]?.text ?? "Any foods or drinks you avoid?")
            TextField("For example: pork, alcohol", text: Binding(get: { model.profile.foodsAvoided ?? "" },
                                                              set: { model.profile.foodsAvoided = $0.isEmpty ? nil : $0 }))
                .padding(12)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 10))
                .overlay(RoundedRectangle(cornerRadius: 10).stroke(Theme.outline, lineWidth: 1))
            if let note = about["foods_avoided"]?.note { Text(note).font(.footnote).foregroundStyle(Theme.inkSoft) }
            PrimaryButton(title: "Next") { go(7) }
        case .photos:
            QuestionTitle(photos.first?.text ?? "How much do photos and sharing matter on your trips?")
            ScaleRow(low: "Not at all", high: "A lot", value: $model.profile.photosMatter)
            PrimaryButton(title: "Next", disabled: model.profile.photosMatter == nil) { go(8) }
        case .shotCard:
            QuestionTitle(photos.count > 1 ? photos[1].text : "Some stops come with a shot card: where to stand for the best photo. Would that make you more likely to go?")
            if let card = model.onboarding?.exampleShotCard {
                ShotCardSummary(card: card, label: photos.count > 1 ? photos[1].exampleLabel : nil)
                    .surfaceCard()
            }
            ScaleRow(low: "No", high: "Definitely", value: $model.profile.shotCardAppeal)
            PrimaryButton(title: "Finish", disabled: model.profile.shotCardAppeal == nil) { go(9) }
        }
    }
}

struct QuestionTitle: View {
    let text: String
    init(_ text: String) { self.text = text }

    var body: some View {
        Text(text)
            .font(Theme.title3)
            .foregroundStyle(Theme.ink)
            .fixedSize(horizontal: false, vertical: true)
    }
}

/// One tap answers and moves on (D115).
struct ChoiceList: View {
    let options: [(String, String)]
    let selected: String?
    let pick: (String) -> Void

    var body: some View {
        VStack(spacing: 10) {
            ForEach(options, id: \.0) { option in
                ChoiceRow(label: option.1, on: selected == option.0) { pick(option.0) }
            }
        }
    }
}

struct ChoiceRow: View {
    let label: String
    let on: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack {
                Text(label)
                Spacer()
                if on { Image(systemName: "checkmark") }
            }
            .foregroundStyle(on ? Theme.onAccent : Theme.ink)
            .padding(.horizontal, 16)
            .frame(maxWidth: .infinity, minHeight: 50)
            .background(on ? Theme.accentFill : Theme.surface, in: RoundedRectangle(cornerRadius: 12))
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(on ? Theme.accentFill : Theme.outline, lineWidth: 1))
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(on ? .isSelected : [])
    }
}

struct MoreRow: View {
    let title: String
    let done: Bool

    var body: some View {
        HStack {
            Text(title).foregroundStyle(Theme.ink)
            Spacer()
            if done {
                Label("Done", systemImage: "checkmark").labelStyle(.titleAndIcon).font(.footnote)
                    .foregroundStyle(Theme.inkSoft)
            } else {
                Image(systemName: "chevron.right").foregroundStyle(Theme.inkSoft)
            }
        }
        .frame(minHeight: 44)
    }
}

/// A picker that can stay unanswered ("Skip" is always allowed).
struct OptionalPicker: View {
    let title: String
    let options: [(String, String)]
    @Binding var value: String?

    var body: some View {
        Picker(title, selection: Binding(get: { value ?? "" }, set: { value = $0.isEmpty ? nil : $0 })) {
            Text("Skip").tag("")
            ForEach(options, id: \.0) { pair in
                Text(pair.1).tag(pair.0)
            }
        }
    }
}

/// The short shot-card example (D112): where to stand and when, with a small map. The full card opens from a stop.
struct ShotCardSummary: View {
    let card: Card
    var label: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(label ?? "Example of what you'll get")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(Theme.accent)
            Label(card.title, systemImage: "camera").font(.headline).foregroundStyle(Theme.ink)
            if let shot = card.shotCard {
                if let lat = shot.standAt?.lat, let lon = shot.standAt?.lon {
                    let here = CLLocationCoordinate2D(latitude: lat, longitude: lon)
                    Map(initialPosition: .region(MKCoordinateRegion(center: here, latitudinalMeters: 500,
                                                                    longitudinalMeters: 500))) {
                        Marker("Stand here", coordinate: here).tint(Theme.accentFill)
                    }
                    .frame(height: 110)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                    .allowsHitTesting(false)
                }
                InfoBlock(label: "Where to stand", text: shot.standAt?.note ?? "")
                InfoBlock(label: "When", text: shot.when ?? "")
            }
        }
        .padding(.vertical, 4)
    }
}
