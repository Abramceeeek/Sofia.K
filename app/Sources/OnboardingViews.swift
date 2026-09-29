import SwiftUI

/// Screens 3–8 (Test A inside the app, D109). Each step is sent to the Brain as it finishes.
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
                    case .aboutYou: AboutYouStep()
                    case .photos: PhotosStep()
                    }
                }
            }
            .navigationTitle(model.step.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Text("\(model.step.rawValue + 1) of \(Step.allCases.count)")
                        .font(.footnote.monospacedDigit())
                        .foregroundStyle(.secondary)
                }
            }
        }
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
                TextEditor(text: $model.bestHour)
                    .frame(minHeight: 140)
                    .padding(8)
                    .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 10))
                    .accessibilityLabel("Your answer")
                Text("Tap the mic on your keyboard to speak instead.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                if !model.bestHour.isEmpty {
                    Text(q?.followUp ?? "Is there anything else you'd like to add about that?")
                    TextEditor(text: $model.bestHourMore)
                        .frame(minHeight: 90)
                        .padding(8)
                        .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 10))
                        .accessibilityLabel("Anything else")
                }
                PrimaryButton(title: model.bestHour.isEmpty ? "Skip" : "Next", disabled: model.busy) {
                    Task { await model.finishBestHour() }
                }
            }
            .padding(20)
        }
    }
}

// ---- 4. Why you go out (up to two) --------------------------------------------------------------

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
                Text(choices?.prompt ?? "Which of these is most often why you go out or travel? Pick up to two.")
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
                PrimaryButton(title: "Next") { model.next() }
                    .padding(.top, 8)
            }
            .padding(20)
        }
    }
}

// ---- 5. Places you've been (the 16 locked places, D107) -----------------------------------------

struct PlacesStep: View {
    @Environment(AppModel.self) private var model
    @State private var index = 0

    var body: some View {
        let places = model.onboarding?.swipePlaces ?? []
        VStack(spacing: 20) {
            if index < places.count {
                let place = places[index]
                Text("\(index + 1) of \(places.count)")
                    .font(.footnote.monospacedDigit())
                    .foregroundStyle(.secondary)
                Spacer()
                Text(place.name)
                    .font(.title.bold())
                    .multilineTextAlignment(.center)
                Text(model.onboarding?.swipe?.prompt ?? "Have you been? How did it feel?")
                    .foregroundStyle(.secondary)
                Spacer()
                ForEach(Labels.reactions, id: \.0) { pair in
                    Button {
                        model.reactions[place.item] = pair.0
                        index += 1
                    } label: {
                        Text(pair.1).frame(maxWidth: .infinity, minHeight: 44)
                    }
                    .buttonStyle(.bordered)
                }
            } else {
                Spacer()
                Text("That's all 16 places. Thank you.")
                    .font(.title3)
                Spacer()
                PrimaryButton(title: "Next", disabled: model.busy) { Task { await model.finishPlaces() } }
            }
        }
        .padding(20)
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
                    Text(model.onboarding?.conjoint?.prompt ?? "Two made-up day plans. Which day would you rather have?")
                        .font(.title3)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    Text("\(index + 1) of \(tasks.count)")
                        .font(.footnote.monospacedDigit())
                        .foregroundStyle(.secondary)
                    DayOption(label: "Day A", text: task.a) { choose(task, "A") }
                    DayOption(label: "Day B", text: task.b) { choose(task, "B") }
                } else {
                    Text("Done: 10 of 10.")
                        .font(.title3)
                        .padding(.vertical, 40)
                    PrimaryButton(title: "Next", disabled: model.busy) { Task { await model.finishThisOrThat() } }
                }
            }
            .padding(20)
        }
    }

    private func choose(_ task: ConjointTask, _ choice: String) {
        model.choices[task.task] = choice
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
                Text(label).font(.headline)
                ForEach(parts.indices, id: \.self) { i in
                    Label(parts[i].prefix(1).uppercased() + String(parts[i].dropFirst()),
                          systemImage: i < Labels.attributeIcons.count ? Labels.attributeIcons[i] : "circle")
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
            .padding(14)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .buttonStyle(.bordered)
        .accessibilityHint("Choose this day")
    }
}

// ---- 7. A bit about you (all optional; no nationality, income, health or allergy questions) ----------

struct AboutYouStep: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        @Bindable var model = model
        let questions = Dictionary(uniqueKeysWithValues: (model.onboarding?.aboutYou ?? []).map { ($0.key, $0) })
        Form {
            OptionalPicker(title: questions["budget_band"]?.text ?? "Budget per day out",
                           options: Labels.budget, value: $model.profile.budgetBand)
            OptionalPicker(title: questions["company"]?.text ?? "Who you go with",
                           options: Labels.company, value: $model.profile.company)
            OptionalPicker(title: questions["chronotype"]?.text ?? "Morning or night",
                           options: Labels.chronotype, value: $model.profile.chronotype)
            OptionalPicker(title: questions["activity"]?.text ?? "How active",
                           options: Labels.activity, value: $model.profile.activity)
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
            if let fields = model.onboarding?.fields {
                Section {
                    ForEach(fields.options.filter { $0.key != "none" }) { option in
                        Toggle(option.label, isOn: Binding(
                            get: { model.profile.fields.contains(option.key) },
                            set: { on in
                                model.profile.fields.removeAll { $0 == option.key }
                                if on { model.profile.fields.append(option.key) }
                            }))
                    }
                } header: {
                    Text(fields.question)
                } footer: {
                    Text(fields.note)
                }
            }
            Section {
                PrimaryButton(title: "Next", disabled: model.busy) { Task { await model.finishAboutYou() } }
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

// ---- 8. Photos, with the example shot card (D16, D106) -------------------------------------------

struct PhotosStep: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        @Bindable var model = model
        let qs = model.onboarding?.photos ?? []
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                Text(qs.first?.text ?? "How much do photos and sharing matter on your trips?")
                    .font(.title3)
                ScaleRow(low: "Not at all", high: "A lot", value: $model.profile.photosMatter)
                if let card = model.onboarding?.exampleShotCard {
                    ShotCardView(card: card)
                        .padding(14)
                        .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 12))
                }
                Text(qs.count > 1 ? qs[1].text : "If a plan came with a card like this, would it make you more likely to go?")
                    .font(.title3)
                ScaleRow(low: "No", high: "Definitely", value: $model.profile.shotCardAppeal)
                PrimaryButton(title: model.busy ? "One moment…" : "Finish", disabled: model.busy) {
                    Task { await model.finishOnboarding() }
                }
            }
            .padding(20)
        }
    }
}
