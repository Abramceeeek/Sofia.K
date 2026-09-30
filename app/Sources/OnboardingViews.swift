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
                TextEditor(text: $model.bestHour)
                    .scrollContentBackground(.hidden)
                    .frame(minHeight: 120)
                    .padding(8)
                    .background(Theme.surface, in: RoundedRectangle(cornerRadius: 10))
                    .overlay(RoundedRectangle(cornerRadius: 10).stroke(Theme.outline, lineWidth: 1))
                    .accessibilityLabel("Your answer")
                Text("A few words is fine. Tap the mic on your keyboard to speak instead.")
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

// ---- 5. Why you go out (up to two, or none) -----------------------------------------------------

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
    /// The rating's words (D112), one per step of the 1–5 scale.
    static let feel = ["Flat", "Pleasant", "Restorative", "Vivid", "Unforgettable"]
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
                    .font(Theme.title3)
                    .foregroundStyle(Theme.ink)
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
                    Text(model.onboarding?.conjoint?.prompt ?? "Two made-up example days. Which would you rather have?")
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

// ---- 12. Improve future plans: one optional screen after the first plan (D112) ---------------------

struct ImproveView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State private var morePlaces = false
    @State private var moreTasks = false

    var body: some View {
        @Bindable var model = model
        let questions = Dictionary(uniqueKeysWithValues: (model.onboarding?.aboutYou ?? []).map { ($0.key, $0) })
        let later = model.onboarding?.swipePlacesLater ?? []
        let laterTasks = model.onboarding?.conjointTasksLater ?? []
        let photos = model.onboarding?.photos ?? []
        NavigationStack {
            Form {
                Section {
                    Text("All optional. Each answer helps your next plans fit you better.")
                        .foregroundStyle(Theme.inkSoft)
                }
                if !later.isEmpty || !laterTasks.isEmpty {
                    Section("More quick questions") {
                        if !later.isEmpty {
                            Button { morePlaces = true } label: {
                                MoreRow(title: "\(later.count) more places you may have been", done: model.morePlacesDone)
                            }
                        }
                        if !laterTasks.isEmpty {
                            Button { moreTasks = true } label: {
                                MoreRow(title: "\(laterTasks.count) more made-up example days", done: model.moreTasksDone)
                            }
                        }
                    }
                }
                Section("A bit about you") {
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
                Section("Photos") {
                    Text(photos.first?.text ?? "How much do photos and sharing matter on your trips?")
                    ScaleRow(low: "Not at all", high: "A lot", value: $model.profile.photosMatter)
                }
                Section("Shot cards") {
                    Text(photos.count > 1 ? photos[1].text : "Some stops come with a shot card: where to stand for the best photo. Would that make you more likely to go?")
                    if let card = model.onboarding?.exampleShotCard {
                        ShotCardSummary(card: card, label: photos.count > 1 ? photos[1].exampleLabel : nil)
                    }
                    ScaleRow(low: "No", high: "Definitely", value: $model.profile.shotCardAppeal)
                }
                Section {
                    PrimaryButton(title: model.busy ? "Saving…" : "Save", disabled: model.busy) {
                        Task {
                            await model.saveImprovements(done: true)
                            if model.errorMessage == nil { dismiss() }
                        }
                    }
                    .listRowInsets(EdgeInsets())
                    .listRowBackground(Color.clear)
                }
            }
            .themedList()
            .serifTitle("Improve future plans")
            .toolbar {
                ToolbarItem(placement: .topBarLeading) { Button("Close") { dismiss() } }
            }
            .sheet(isPresented: $morePlaces) {
                NavigationStack {
                    PlacesStep(places: later) {
                        await model.finishMorePlaces()
                        if model.errorMessage == nil { morePlaces = false }
                    }
                    .background(Theme.background)
                    .serifTitle("More places")
                }
            }
            .sheet(isPresented: $moreTasks) {
                NavigationStack {
                    ThisOrThatStep(tasks: laterTasks, doneText: "Thank you. Your next plans will use these.",
                                   doneButton: "Save") {
                        await model.finishMoreTasks()
                        if model.errorMessage == nil { moreTasks = false }
                    }
                    .background(Theme.background)
                    .serifTitle("More example days")
                }
            }
        }
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
