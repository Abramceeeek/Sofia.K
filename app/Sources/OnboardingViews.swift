import SwiftUI

/// Screens 3–6: onboarding up to the first plan (Test A inside the app, D109). Each step is sent as it finishes.
/// D110: four steps, then the plan; "about you" and photos are an optional step after it (ImproveView).
struct OnboardingView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        NavigationStack {
            Group {
                if model.onboarding == nil {
                    ProgressView("Loading the questions…")
                        .task { await model.run { try await model.loadOnboarding() } }
                } else {
                    switch model.step {
                    case .bestHour: BestHourStep()
                    case .why: WhyStep()
                    case .places: PlacesStep()
                    case .thisOrThat: ThisOrThatStep()
                    }
                }
            }
            .navigationTitle(model.step.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Text("Step \(model.step.rawValue + 1) of \(Step.allCases.count)")
                        .font(.footnote.monospacedDigit())
                        .foregroundStyle(.secondary)
                }
            }
        }
    }
}

/// A progress bar with "4 of 10" under it. No timers anywhere (design brief).
struct SectionProgress: View {
    let done: Int
    let total: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            ProgressView(value: Double(done), total: Double(max(total, 1)))
                .tint(Theme.accent)
            Text("\(min(done + 1, total)) of \(total)")
                .font(.footnote.monospacedDigit())
                .foregroundStyle(.secondary)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(min(done + 1, total)) of \(total)")
    }
}

// ---- 3. The best hour ---------------------------------------------------------------------------

struct BestHourStep: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        @Bindable var model = model
        let q = model.onboarding?.openQuestions.first
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(q?.text ?? "Tell me about the best hour of your last trip or day out.")
                    .font(.title3)
                if let examples = q?.examples, !examples.isEmpty {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("For example")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(.secondary)
                        ForEach(examples, id: \.self) { line in
                            Text("“\(line)”")
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
                TextEditor(text: $model.bestHour)
                    .frame(minHeight: 120)
                    .padding(8)
                    .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 10))
                    .accessibilityLabel("Your answer")
                Text("A few words is fine. Tap the mic on your keyboard to speak instead.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                if !model.bestHour.isEmpty {
                    Text(q?.followUp ?? "Is there anything else you'd like to add about that?")
                    TextEditor(text: $model.bestHourMore)
                        .frame(minHeight: 80)
                        .padding(8)
                        .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 10))
                        .accessibilityLabel("Anything else")
                }
                PrimaryButton(title: "Next", disabled: model.busy || model.bestHour.isEmpty) {
                    Task { await model.finishBestHour() }
                }
                Button("Skip this question") {
                    model.bestHour = ""
                    model.bestHourMore = ""
                    Task { await model.finishBestHour() }
                }
                .frame(maxWidth: .infinity, minHeight: 44)
                .disabled(model.busy)
            }
            .padding(20)
        }
    }
}

// ---- 4. Why you go out (up to two, or none) -----------------------------------------------------

enum Labels {
    static let why = ["switch_off": "Switch off and rest", "people": "Time with people",
                      "discover": "Discover something new", "nature": "Nature and outdoors",
                      "culture": "Culture and history", "food": "Food"]
    static let budget = [("under_20", "Under £20"), ("20_40", "£20–40"), ("40_70", "£40–70"), ("70_plus", "£70 or more")]
    static let company = [("solo", "On my own"), ("friends", "Friends"), ("partner", "A partner"), ("family", "Family")]
    static let chronotype = [("morning", "Morning person"), ("night", "Night person"), ("neither", "Neither")]
    static let activity = [("gentle", "Gentle"), ("medium", "In between"), ("full_on", "Full on")]
    static let grewUp = [("big_city", "A big city"), ("town", "A town"), ("coast", "By the coast"),
                         ("countryside", "The countryside")]
    static let reactions = [("loved", "Loved it"), ("fine", "It was fine"), ("didnt_enjoy", "Didn't enjoy it"),
                            ("havent_been", "Haven't been")]
    /// One word under each number on the rating (screen 10).
    static let feel = ["Poor", "Not great", "OK", "Good", "Wonderful"]
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
                Text(choices?.prompt ?? "Which of these is most often why you go out or travel? Pick up to two, or none.")
                    .font(.title3)
                ForEach(choices?.options ?? [], id: \.self) { key in
                    let on = model.why.contains(key)
                    Button {
                        if on { model.why.removeAll { $0 == key } } else if model.why.count < 2 { model.why.append(key) }
                    } label: {
                        HStack {
                            Text(Labels.why[key] ?? key)
                            Spacer()
                            Image(systemName: on ? "checkmark.circle.fill" : "circle")
                        }
                        .frame(minHeight: 44)
                    }
                    .buttonStyle(.bordered)
                    .tint(on ? Theme.accent : .secondary)
                    .accessibilityAddTraits(on ? .isSelected : [])
                }
                PrimaryButton(title: model.why.isEmpty ? "None of these: next" : "Next") { model.next() }
                    .padding(.top, 8)
            }
            .padding(20)
        }
    }
}

// ---- 5. Places you've been (the app's 10 of the locked 16, D107, D110) ----------------------------

struct PlacesStep: View {
    @Environment(AppModel.self) private var model
    @State private var index = 0

    var body: some View {
        let places = model.onboarding?.swipePlaces ?? []
        VStack(spacing: 14) {
            if index < places.count {
                let place = places[index]
                SectionProgress(done: index, total: places.count)
                Spacer()
                Text(place.name)
                    .font(.title.bold())
                    .multilineTextAlignment(.center)
                Text(model.onboarding?.swipe?.prompt ?? "Have you been? How did it feel?")
                    .foregroundStyle(.secondary)
                Spacer()
                ForEach(Labels.reactions, id: \.0) { pair in
                    Button {
                        react(place, pair.0)
                    } label: {
                        Text(pair.1).frame(maxWidth: .infinity, minHeight: 44)
                    }
                    .buttonStyle(.bordered)
                }
                HStack {
                    Button("Back") { index -= 1 }
                        .disabled(index == 0)
                    Spacer()
                    Button("Not sure, skip") { react(place, "skip") }
                }
                .font(.subheadline)
                .frame(minHeight: 44)
            } else {
                SectionProgress(done: places.count, total: places.count)
                Spacer()
                Text("That's all \(places.count) places. Thank you.")
                    .font(.title3)
                Spacer()
                PrimaryButton(title: "Next", disabled: model.busy) { Task { await model.finishPlaces() } }
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

// ---- 6. This or that (the 10 conjoint tasks) --------------------------------------------------

struct ThisOrThatStep: View {
    @Environment(AppModel.self) private var model
    @State private var index = 0

    var body: some View {
        let tasks = model.onboarding?.conjointTasks ?? []
        ScrollView {
            VStack(spacing: 14) {
                if index < tasks.count {
                    let task = tasks[index]
                    SectionProgress(done: index, total: tasks.count)
                    Text(model.onboarding?.conjoint?.prompt ?? "Two made-up day plans. Which day would you rather have?")
                        .font(.title3)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    DayOption(label: "Day A", text: task.a) { choose(task, "A") }
                    DayOption(label: "Day B", text: task.b) { choose(task, "B") }
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
                    Text("That's everything. Next: your first plan.")
                        .font(.title3)
                        .padding(.vertical, 40)
                    PrimaryButton(title: model.busy ? "One moment…" : "Plan my first day", disabled: model.busy) {
                        Task { await model.finishThisOrThat() }
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
                Text(label).font(.headline).foregroundStyle(Theme.accent)
                ForEach(parts.indices, id: \.self) { i in
                    Label(parts[i].prefix(1).uppercased() + String(parts[i].dropFirst()),
                          systemImage: i < Labels.attributeIcons.count ? Labels.attributeIcons[i] : "circle")
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
            .foregroundStyle(.primary)
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 14))
            .overlay(RoundedRectangle(cornerRadius: 14).stroke(Color(.separator), lineWidth: 1))
        }
        .buttonStyle(.plain)
        .accessibilityHint("Choose this day")
    }
}

// ---- 11–13. Improve my plans: optional, after the first plan (D110) -------------------------------

struct ImproveView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State private var page: ImprovePage

    init(page: ImprovePage = .aboutYou) {
        _page = State(initialValue: page)
    }

    var body: some View {
        NavigationStack {
            Group {
                switch page {
                case .aboutYou:
                    AboutYouPage {
                        Task {
                            await model.saveImprovements(done: false)
                            if model.errorMessage == nil { page = .photos }
                        }
                    }
                case .photos:
                    PhotosPage { page = .shotCards }
                case .shotCards:
                    ShotCardsPage {
                        Task {
                            await model.saveImprovements(done: true)
                            if model.errorMessage == nil { dismiss() }
                        }
                    }
                }
            }
            .navigationTitle(page.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) { Button("Close") { dismiss() } }
                ToolbarItem(placement: .topBarTrailing) {
                    Text("\(page.rawValue + 1) of \(ImprovePage.allCases.count)")
                        .font(.footnote.monospacedDigit())
                        .foregroundStyle(.secondary)
                }
            }
        }
    }
}

/// Screen 11: all optional; no nationality, income, health or allergy questions.
struct AboutYouPage: View {
    @Environment(AppModel.self) private var model
    let onNext: () -> Void

    var body: some View {
        @Bindable var model = model
        let questions = Dictionary(uniqueKeysWithValues: (model.onboarding?.aboutYou ?? []).map { ($0.key, $0) })
        Form {
            Section {
                Text("Every question is optional. Your next plans use what you tell us here.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
            Section {
                OptionalPicker(title: questions["budget_band"]?.text ?? "Budget per day out",
                               options: Labels.budget, value: $model.profile.budgetBand)
                OptionalPicker(title: questions["company"]?.text ?? "Who you go with",
                               options: Labels.company, value: $model.profile.company)
                OptionalPicker(title: questions["chronotype"]?.text ?? "Morning or night",
                               options: Labels.chronotype, value: $model.profile.chronotype)
                OptionalPicker(title: questions["activity"]?.text ?? "How active",
                               options: Labels.activity, value: $model.profile.activity)
            }
            if let fields = model.onboarding?.fields {
                Section {
                    Text(fields.question).font(.headline)
                    ForEach(fields.options.filter { $0.key != "none" }) { option in
                        Toggle(option.label, isOn: Binding(
                            get: { model.profile.fields.contains(option.key) },
                            set: { on in
                                model.profile.fields.removeAll { $0 == option.key }
                                if on { model.profile.fields.append(option.key) }
                            }))
                    }
                } footer: {
                    Text(fields.note)
                }
            }
            Section {
                OptionalPicker(title: questions["grew_up"]?.text ?? "Where you grew up",
                               options: Labels.grewUp, value: $model.profile.grewUp)
            } footer: {
                Text(questions["grew_up"]?.note ?? "")
            }
            Section {
                TextField(questions["foods_avoided"]?.text ?? "Any foods or drinks you avoid?",
                          text: Binding(get: { model.profile.foodsAvoided ?? "" },
                                        set: { model.profile.foodsAvoided = $0.isEmpty ? nil : $0 }))
            } footer: {
                Text(questions["foods_avoided"]?.note ?? "")
            }
            Section {
                PrimaryButton(title: model.busy ? "Saving…" : "Next", disabled: model.busy, action: onNext)
            }
        }
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

/// Screen 12: one question (D16, D110).
struct PhotosPage: View {
    @Environment(AppModel.self) private var model
    let onNext: () -> Void

    var body: some View {
        @Bindable var model = model
        let q = model.onboarding?.photos.first
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                Text(q?.text ?? "How much do photos and sharing matter on your trips?")
                    .font(.title3)
                ScaleRow(low: "Not at all", high: "A lot", value: $model.profile.photosMatter)
                PrimaryButton(title: "Next", action: onNext)
                    .padding(.top, 8)
                Button("Skip") {
                    model.profile.photosMatter = nil
                    onNext()
                }
                .frame(maxWidth: .infinity, minHeight: 44)
            }
            .padding(20)
        }
    }
}

/// Screen 13: the second question, with the example shot card (D106), labelled as an example and shown only here.
struct ShotCardsPage: View {
    @Environment(AppModel.self) private var model
    let onSave: () -> Void

    var body: some View {
        @Bindable var model = model
        let qs = model.onboarding?.photos ?? []
        let q = qs.count > 1 ? qs[1] : nil
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                Text(q?.text ?? "Some stops come with a shot card: where to stand for the best photo. Would that make you more likely to go?")
                    .font(.title3)
                if let card = model.onboarding?.exampleShotCard {
                    VStack(alignment: .leading, spacing: 10) {
                        Text(q?.exampleLabel ?? "Example of what you'll get")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(Theme.accent)
                        ShotCardView(card: card)
                    }
                    .padding(14)
                    .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 12))
                }
                ScaleRow(low: "No", high: "Definitely", value: $model.profile.shotCardAppeal)
                PrimaryButton(title: model.busy ? "Saving…" : "Save", disabled: model.busy, action: onSave)
            }
            .padding(20)
        }
    }
}
