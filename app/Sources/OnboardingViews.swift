import SwiftUI
import MapKit

/// Screens 3b–7: onboarding up to the first plan (Test A inside the app, D109). Each step is sent as it finishes.
/// D112: a great moment, how you want to feel, 6 places and 5 "this or that" tasks, then the plan. D116: "Where are you
/// based?" comes first, and visitors from abroad get the kinds-of-places cards (6b) instead of the London places.
/// D119 (ODYS): no navigation bar; each question carries its own eyebrow ("Question 7 of 14", D118) and title.
struct OnboardingView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
            if model.step != .based, model.onboarding != nil, let previous = Step(rawValue: model.step.rawValue - 1) {
                // m176: a way back to the step before (places and this-or-that also step back one at a time inside)
                HStack {
                    Button { withAnimation(Motion.settle) { model.back() } } label: {
                        Text("‹ \(previous == .places && model.isVisitor ? "Kinds of places" : previous.title)")
                            .font(.subheadline)
                            .foregroundStyle(Theme.accent)
                            .frame(minHeight: 44)
                    }
                    .accessibilityLabel("Back to \(previous.title)")
                    Spacer()
                }
                .padding(.horizontal, 24)
            }
            Group {
                if let onboarding = model.onboarding {
                    switch model.step {
                    case .based: BasedStep()
                    case .bestHour: BestHourStep()
                    case .why: WhyStep()
                    case .places:
                        if model.isVisitor, let cards = onboarding.categoryCards, !cards.isEmpty {
                            CategoryStep(cards: cards) { await model.finishCategories() }   // D116
                        } else {
                            PlacesStep(places: onboarding.swipePlaces) { await model.finishPlaces() }
                        }
                    case .thisOrThat:
                        ThisOrThatStep(tasks: onboarding.conjointTasks) { await model.finishThisOrThat() }
                    case .learned: LearnedStep()   // D117
                    }
                } else {
                    OnboardingLoading()
                }
            }
            }
            .background(Theme.background)
            .navigationTitle(model.stepTitle)
            .toolbar(.hidden, for: .navigationBar)
            .statusBarShade()
        }
    }
}

/// Loads the questions once; if that fails, says so and offers "Try again" instead of spinning for ever.
struct OnboardingLoading: View {
    @Environment(AppModel.self) private var model
    @State private var failed = false

    var body: some View {
        VStack(spacing: 18) {
            ArchGlyph(width: 28)
            if failed {
                Text("The questions didn't load.")
                    .font(Theme.title3)
                    .foregroundStyle(Theme.ink)
                PrimaryButton(title: "Try again", disabled: model.busy) {
                    Task { await load() }
                }
            } else {
                Text("Getting the questions…")
                    .foregroundStyle(Theme.muted)
            }
        }
        .padding(24)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .task { await load() }
    }

    private func load() async {
        failed = false
        await model.run { try await model.loadOnboarding() }
        failed = model.onboarding == nil
    }
}

/// The top of each question: "Question 7 of 14" (D118: every question counted) and a thin line of progress, with a
/// quiet action on the right ("Skip", "Skip the rest"). No timers anywhere (design brief).
struct StepHeader<Trailing: View>: View {
    let label: String
    let progress: Double
    let trailing: Trailing

    init(_ label: String, progress: Double, @ViewBuilder trailing: () -> Trailing) {
        self.label = label
        self.progress = progress
        self.trailing = trailing()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Eyebrow(label)
                Spacer(minLength: 8)
                trailing
            }
            .frame(minHeight: 44)
            ProgressLine(value: progress)
        }
    }
}

extension StepHeader where Trailing == EmptyView {
    init(_ label: String, progress: Double) {
        self.init(label, progress: progress) { EmptyView() }
    }
}

struct ProgressLine: View {
    let value: Double

    var body: some View {
        GeometryReader { g in
            ZStack(alignment: .leading) {
                Capsule().fill(Theme.ink.opacity(0.1))
                Capsule().fill(Theme.amberDeep).frame(width: g.size.width * min(max(value, 0), 1))
            }
        }
        .frame(height: 4)
        .animation(.easeOut(duration: 0.4), value: value)
        .accessibilityHidden(true)
    }
}

/// A typed answer: a dark box with a soft outline.
struct AnswerBox: View {
    @Binding var text: String
    var minHeight: CGFloat = 110
    let label: String

    var body: some View {
        TextEditor(text: $text)
            .scrollContentBackground(.hidden)
            .foregroundStyle(Theme.ink)
            .frame(minHeight: minHeight)
            .padding(10)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 14))
            .overlay(RoundedRectangle(cornerRadius: 14).stroke(Theme.outline, lineWidth: 1))
            .accessibilityLabel(label)
    }
}

/// A one-line typed answer.
struct LineField: View {
    let placeholder: String
    @Binding var text: String

    var body: some View {
        TextField("", text: $text, prompt: Text(placeholder).foregroundStyle(Theme.muted))
            .foregroundStyle(Theme.ink)
            .padding(.horizontal, 16)
            .frame(minHeight: 52)
            .overlay(RoundedRectangle(cornerRadius: 14).stroke(Theme.outlineStrong, lineWidth: 1))
    }
}

// ---- 3b. Where you're based (D116) ----------------------------------------------------------------------

struct BasedStep: View {
    @Environment(AppModel.self) private var model
    private let labels = [("london", "In London"), ("uk", "Elsewhere in the UK"), ("abroad", "Visiting from abroad")]

    var body: some View {
        @Bindable var model = model
        let q = model.onboarding?.based
        let abroad = model.profile.based == "abroad"
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                StepHeader(model.questionLabel, progress: model.questionProgress)
                PageTitle(text: q?.prompt ?? "Where are you based?")
                    .padding(.vertical, 6)
                    .settle(0)
                ForEach(labels.indices, id: \.self) { i in
                    let option = labels[i]
                    let on = model.profile.based == option.0
                    SelectTile(on: on, action: { model.profile.based = option.0 }) {
                        HStack {
                            Text(option.1).foregroundStyle(Theme.ink)
                            Spacer()
                            RadioDot(on: on)
                        }
                        .padding(.horizontal, 20)
                    }
                    .settle(i + 1)
                }
                if model.profile.based == "uk" || abroad {   // 19 Oct: Londoners have said where already
                VStack(alignment: .leading, spacing: 8) {
                    // a town or city, never nationality (D116)
                    Text(abroad ? "Which town or city are you visiting from? (optional)"
                                : (q?.cityPrompt ?? "Which town or city? (optional)"))
                        .font(.subheadline)
                        .foregroundStyle(Theme.muted)
                    LineField(placeholder: abroad ? "e.g. Tashkent" : "e.g. Manchester", text: Binding(
                        get: { model.profile.homeCity ?? "" },
                        set: { model.profile.homeCity = $0.isEmpty ? nil : String($0.prefix(80)) }))
                        .textInputAutocapitalization(.words)
                }
                .padding(.top, 10)
                }
                Text(q?.note ?? "So we ask the right questions. We never ask your nationality.")
                    .font(.subheadline)
                    .foregroundStyle(Theme.muted)
                    .fixedSize(horizontal: false, vertical: true)
                PrimaryButton(title: model.busy ? "One moment…" : "Continue", disabled: model.busy || model.profile.based == nil) {
                    Task { await model.finishBased() }
                }
                .padding(.top, 12)
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
        .scrollDismissesKeyboard(.interactively)
    }
}

// ---- 6b. Kinds of places: visitors from abroad, instead of the London places (D116) --------------------------

/// One kind of place at a time, with a London example's photo. "Never tried" asks whether they'd like to.
struct CategoryStep: View {
    @Environment(AppModel.self) private var model
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    let cards: [CategoryCard]
    let onDone: () async -> Void
    @State private var index = 0
    @State private var askingWant = false
    @State private var advance: Task<Void, Never>?

    private let reactions = [("loved", "Love it"), ("fine", "It's fine"), ("didnt_enjoy", "Not for me"),
                             ("never_tried", "Never tried")]
    private let wants = [("yes", "Yes, I'd like to"), ("maybe", "Not sure"), ("no", "No thanks")]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                StepHeader(model.questionLabel, progress: model.questionProgress) {
                    if index < cards.count { QuietButton("Skip the rest") { Task { await onDone() } }.disabled(model.busy) }
                }
                if index < cards.count {
                    let card = cards[index]
                    VStack(alignment: .leading, spacing: 16) {
                        PlaceField(title: card.title, photoId: card.exampleId, feel: nil,
                                   note: card.exampleTitle.map { "In London, for example: \($0)" })
                        Text(card.line)
                            .font(Theme.italic(19, relativeTo: .body))
                            .foregroundStyle(Theme.inkSoft)
                            .fixedSize(horizontal: false, vertical: true)
                        if askingWant {
                            Text(model.onboarding?.categories?.wantPrompt ?? "Would you like to try it in London?")
                                .font(Theme.title3)
                                .foregroundStyle(Theme.ink)
                            ForEach(wants, id: \.0) { w in
                                AnswerTile(title: w.1, on: false) { answer(card, "never_tried", want: w.0) }
                            }
                        } else {
                            Text(model.onboarding?.categories?.prompt ?? "What kinds of places do you enjoy?")
                                .foregroundStyle(Theme.inkSoft)
                            LazyVGrid(columns: [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)],
                                      spacing: 10) {
                                ForEach(reactions, id: \.0) { r in
                                    AnswerTile(title: r.1, on: model.categoryAnswers[card.key]?.reaction == r.0) {
                                        if r.0 == "never_tried" { askingWant = true } else { answer(card, r.0) }
                                    }
                                }
                            }
                        }
                    }
                    .id(card.key)
                    .transition(.opacity)
                    ReactionSpace(text: model.reaction)
                    HStack {
                        QuietButton("Previous") { back() }
                            .disabled(index == 0 && !askingWant)
                        Spacer()
                        QuietButton("Not sure, skip") { answer(card, "skip") }
                    }
                } else {
                    StepEnd(text: "That's all \(cards.count). Thank you.", onBack: { index = max(cards.count - 1, 0) },
                            onDone: onDone)
                }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
        .animation(reduceMotion ? nil : Motion.fade, value: index)
    }

    private func back() {
        advance?.cancel()
        model.reaction = nil
        if askingWant { askingWant = false } else { index = max(index - 1, 0) }
        model.stepProgress = index
    }

    private func answer(_ card: CategoryCard, _ reaction: String, want: String? = nil) {
        model.categoryAnswers[card.key] = CategoryItem(key: card.key, reaction: reaction, want: want)
        model.react(card.reactions, want == "yes" ? "want_yes" : reaction)   // D117
        let wait = model.reaction == nil ? 300 : 1100     // long enough to read a reaction; any tap goes on
        advance?.cancel()
        advance = Task {
            try? await Task.sleep(for: .milliseconds(wait))
            if Task.isCancelled { return }
            askingWant = false
            model.reaction = nil
            index += 1
            model.stepProgress = index
            if index >= cards.count { await onDone() }
        }
    }
}

/// A place or a kind of place: its photo (openly licensed, credited underneath) or a field of colour, with its name.
struct PlaceField: View {
    let title: String
    let photoId: String?
    let feel: String?
    var note: String?

    var body: some View {
        let found = photoId.flatMap { CardPhotos.photo(for: $0) }
        VStack(alignment: .leading, spacing: 6) {
            Color.clear
                .frame(height: 260)
                .overlay {
                    if let found {
                        Image(uiImage: found.1).resizable().scaledToFill()
                    } else {
                        Field(feel: feel)
                    }
                }
                .overlay(alignment: .bottomLeading) {
                    Text(title)
                        .font(Theme.serif(34, relativeTo: .largeTitle))
                        .foregroundStyle(Theme.ink)
                        .lineLimit(3)
                        .minimumScaleFactor(0.7)
                        .padding(20)
                        .padding(.top, 30)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(LinearGradient(colors: [.clear, .black.opacity(0.7)], startPoint: .top, endPoint: .bottom))
                }
                .clipShape(RoundedRectangle(cornerRadius: 24))
                .accessibilityElement(children: .combine)
            if let note {
                Text(note).font(.footnote).foregroundStyle(Theme.muted).fixedSize(horizontal: false, vertical: true)
            }
            if let photo = found?.0 {
                Text(photo.credit).font(.caption2).foregroundStyle(Theme.muted).lineLimit(2)
            }
        }
    }
}

/// An answer in the 2 × 2 grid, or in a list.
struct AnswerTile: View {
    let title: String
    let on: Bool
    let action: () -> Void

    var body: some View {
        SelectTile(on: on, radius: 16, minHeight: 56, action: action) {
            // 19 Oct review: a tick as well as the amber edge, so the choice doesn't rest on colour alone
            HStack(spacing: 6) {
                if on { Image(systemName: "checkmark").font(.footnote.weight(.bold)).foregroundStyle(Theme.accent) }
                Text(title)
                    .foregroundStyle(Theme.ink)
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity)
            .padding(.horizontal, 8)
        }
        .accessibilityAddTraits(on ? .isSelected : [])
    }
}

/// Where a reaction appears, with room kept for it so nothing jumps.
struct ReactionSpace: View {
    let text: String?

    var body: some View {
        ZStack(alignment: .topLeading) {
            if let text { WordReveal(text: text) }
        }
        .frame(maxWidth: .infinity, minHeight: 52, alignment: .topLeading)
    }
}

/// The end of a set of questions: what normally goes on by itself, with a button in case sending failed.
struct StepEnd: View {
    @Environment(AppModel.self) private var model
    let text: String
    let onBack: () -> Void
    let onDone: () async -> Void

    var body: some View {
        VStack(spacing: 18) {
            ArchGlyph(width: 28).padding(.top, 40)
            Text(text)
                .font(Theme.title3)
                .foregroundStyle(Theme.ink)
                .multilineTextAlignment(.center)
            PrimaryButton(title: model.busy ? "One moment…" : "Next", disabled: model.busy) { Task { await onDone() } }
            QuietButton("Back", action: onBack)
        }
        .frame(maxWidth: .infinity)
    }
}

// ---- 7b. So far, I've learned… (D117): before the first plan ------------------------------------------------

/// The person's own answers in plain words (never scores, never from the weights), with Abram's thank-you clip.
/// "Looks right" goes on to the first plan. "Change something" lets them mark any line that isn't right; those are
/// stored and stop counting. A screen they can always pass: with nothing learned, it says so and goes on.
struct LearnedStep: View {
    @Environment(AppModel.self) private var model
    var startChanging = false        // CI screenshots only
    @State private var changing = false
    @State private var wrong: Set<String> = []
    @State private var failed = false   // the list didn't load: it's optional, so the first plan is still one tap away

    var body: some View {
        let learned = model.learned
        let items = learned?.items ?? []
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                // D118: a small "note from Abram"; the person's own answers are what this screen is for
                ClipTile(name: "thanks", label: "A note from Abram, a short video. Tap to play.", small: true) {
                    VStack(alignment: .leading, spacing: 8) {
                        Eyebrow(learned?.title ?? "So far, I've learned…")
                        Text(learned?.note ?? "From your answers only. Nothing here is a score.")
                            .font(.subheadline)
                            .foregroundStyle(Theme.muted)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                .padding(.top, 28)
                if failed {
                    Text("This didn't load just now, but your answers are saved.")
                        .foregroundStyle(Theme.ink)
                    PrimaryButton(title: "Plan my first day", disabled: model.busy) {
                        Task { await model.finishLearned(wrong: []) }
                    }
                } else if learned == nil {
                    ProgressView().tint(Theme.accent).frame(maxWidth: .infinity, minHeight: 80)
                } else if items.isEmpty {
                    Text(learned?.empty ?? "Your first plan starts from what most people enjoy, and it learns from how you rate each stop.")
                        .font(Theme.title3)
                        .foregroundStyle(Theme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                } else {
                    if changing {
                        Text(learned?.changeNote ?? "Tap anything that isn't right. We'll stop using that answer.")
                            .font(.subheadline)
                            .foregroundStyle(Theme.inkSoft)
                    }
                    VStack(alignment: .leading, spacing: 16) {
                        ForEach(items.indices, id: \.self) { i in
                            let item = items[i]
                            LearnedRow(item: item, changing: changing, wrong: wrong.contains(item.id)) {
                                if wrong.contains(item.id) { wrong.remove(item.id) } else { wrong.insert(item.id) }
                            }
                            .settle(i)
                        }
                    }
                }
                VStack(spacing: 10) {
                    if changing {
                        PrimaryButton(title: model.busy ? "One moment…" : (wrong.isEmpty ? "Plan my first day" : "Save and plan my first day"),
                                      disabled: model.busy) {
                            Task { await model.finishLearned(wrong: wrong) }
                        }
                        QuietButton("Cancel") {
                            changing = false
                            wrong = []
                        }
                    } else if learned != nil {
                        PrimaryButton(title: model.busy ? "One moment…" : (items.isEmpty ? "Plan my first day" : "Looks right"),
                                      disabled: model.busy) {
                            Task { await model.finishLearned(wrong: []) }
                        }
                        if !items.isEmpty {
                            SecondaryButton(title: "Change something") { changing = true }
                        }
                    }
                }
                .padding(.top, 10)
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
        .task {
            if model.learned == nil {
                await model.loadLearned()
                failed = model.learned == nil
            }
            if startChanging, let last = model.learned?.items.last?.id {   // CI: one line marked
                changing = true
                wrong = [last]
            }
        }
    }
}

struct LearnedRow: View {
    let item: LearnedItem
    let changing: Bool
    let wrong: Bool
    let toggle: () -> Void

    var body: some View {
        HStack(alignment: .top, spacing: 14) {
            ArchGlyph(color: wrong ? Theme.line : Theme.accent)
                .padding(.top, changing ? 6 : 9)
            VStack(alignment: .leading, spacing: 8) {
                Text(item.text)   // m190 (design review): a list, not six headlines (was 24 pt)
                    .font(Theme.serif(20, relativeTo: .title3))
                    .strikethrough(wrong)
                    .foregroundStyle(wrong ? Theme.muted : Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                if changing {
                    // D118: one clear button per line ("Not right" / "Undo"); a marked line says what happens
                    HStack(spacing: 10) {
                        Button(action: toggle) {
                            Text(wrong ? "Undo" : "Don't use this")
                                .font(.subheadline.weight(.medium))
                                .foregroundStyle(wrong ? Theme.accent : Theme.ink)
                                .padding(.horizontal, 16)
                                .frame(minHeight: 44)
                                .overlay(Capsule().stroke(wrong ? Theme.accent : Theme.outlineStrong, lineWidth: 1))
                                .contentShape(Capsule())
                        }
                        .buttonStyle(PressStyle())
                        .accessibilityLabel(wrong ? "Undo: keep using this answer" : "Don't use this answer")
                        if wrong {
                            Text("We'll stop using this answer.")
                                .font(.footnote)
                                .foregroundStyle(Theme.muted)
                        }
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .accessibilityElement(children: .contain)
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
                // D118: Skip where it's always visible
                StepHeader(model.questionLabel, progress: model.questionProgress) {
                    QuietButton("Skip") { skip() }.disabled(model.busy)
                }
                // D117: Abram asking the question himself, as a small tile beside it (left out until the clip exists)
                ClipTile(name: "ask_moment", label: "Video: Abram asks this question. Tap to play.") {
                    PageTitle(text: q?.text ?? "Tell us about a great moment from a recent day out.",
                              font: Theme.title2)
                }
                .settle(0)
                if let examples = q?.examples, !examples.isEmpty {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("For example")
                            .font(.subheadline)
                            .foregroundStyle(Theme.muted)
                        ForEach(examples, id: \.self) { line in
                            Text("“\(line)”")
                                .font(Theme.italic(18, relativeTo: .body))
                                .foregroundStyle(Theme.inkSoft)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .settle(1)
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
                        .foregroundStyle(Theme.muted)
                }
                if let problem = dictation.problem {
                    Text(problem).font(.footnote).foregroundStyle(Theme.ink)
                }
                Text(dictation.available ? "Or type it" : "Type it, or tap the mic on your keyboard")
                    .font(.subheadline)
                    .foregroundStyle(Theme.muted)
                AnswerBox(text: $model.bestHour, label: "Your answer")
                Text("A few words is fine. There are no wrong answers.")
                    .font(.footnote)
                    .foregroundStyle(Theme.muted)
                if !model.bestHour.isEmpty {
                    Text(q?.followUp ?? "Is there anything else you'd like to add about that?")
                        .font(Theme.title3)
                        .foregroundStyle(Theme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                    AnswerBox(text: $model.bestHourMore, minHeight: 80, label: "Anything else")
                }
                PrimaryButton(title: "Next", disabled: model.busy || model.bestHour.isEmpty) {
                    dictation.stop()
                    Task { await model.finishBestHour() }
                }
                .padding(.top, 4)
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
        .scrollDismissesKeyboard(.interactively)
    }

    private func skip() {
        dictation.stop()
        model.bestHour = ""
        model.bestHourMore = ""
        model.bestHourVoice = false
        Task { await model.finishBestHour() }
    }
}

/// D115: the big "Tell it instead" button: a mic in an amber circle. D119: rings move out from it while it listens.
struct TellItButton: View {
    let listening: Bool
    let action: () -> Void

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            HStack(spacing: 16) {
                ZStack {
                    ListenRings(active: listening)
                    Image(systemName: listening ? "stop.fill" : "mic.fill")
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(Theme.onAccent)
                        .frame(width: 52, height: 52)
                        .background(Circle().fill(Theme.accentFill))
                }
                .frame(width: 52, height: 52)
                VStack(alignment: .leading, spacing: 2) {
                    Text(listening ? "Listening… tap when you're done" : "Speak instead")
                        .font(.headline)
                        .foregroundStyle(Theme.ink)
                    Text(listening ? "Say it the way you'd tell a friend." : "Speak your answer. No typing.")
                        .font(.subheadline)
                        .foregroundStyle(Theme.muted)
                }
                Spacer(minLength: 0)
            }
            .padding(14)
            .frame(maxWidth: .infinity, minHeight: 80)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 22))
            .overlay(RoundedRectangle(cornerRadius: 22).stroke(Theme.accent.opacity(listening ? 1 : 0.55), lineWidth: 1.5))
            .contentShape(RoundedRectangle(cornerRadius: 22))
        }
        .buttonStyle(PressStyle())
        .accessibilityLabel(listening ? "Stop listening" : "Speak your answer instead")
    }
}

// ---- 5. How you want to feel (D115: was "Why you go out"; up to two, or none) ------------------------

enum Labels {
    /// D115: feelings, each mapped onto the model's features in brain/reasons.py (FEELINGS)
    static let why = ["restored": "Restored", "excited": "Excited", "connected": "Connected",
                      "curious": "Curious", "peaceful": "Peaceful"]
    /// D119: the lines under each feeling, from the ODYS design
    static let whyNote = ["restored": "Come home lighter than you left",
                          "excited": "Something to tell people about",
                          "connected": "Time that feels shared",
                          "curious": "Learn something you didn't expect",
                          "peaceful": "Calm while the city rushes past"]
    static let budget = [("under_20", "Under £20"), ("20_40", "£20–40"), ("40_70", "£40–70"), ("70_plus", "£70 or more")]
    static let company = [("solo", "On my own"), ("friends", "Friends"), ("partner", "A partner"), ("family", "Family")]
    static let chronotype = [("morning", "Morning person"), ("night", "Night person"), ("neither", "Neither")]
    static let activity = [("gentle", "Gentle"), ("medium", "In between"), ("full_on", "Full on")]
    static let grewUp = [("big_city", "A big city"), ("town", "A town"), ("coast", "By the coast"),
                         ("countryside", "The countryside")]
    static let reactions = [("loved", "Loved it"), ("fine", "It was fine"), ("didnt_enjoy", "Didn't enjoy it"),
                            ("havent_been", "Haven't been")]
    /// The rating's words (D115: one dimension), 1–5.
    static let feel = ["Disappointing", "Fine", "Good", "Great", "Unforgettable"]
    /// The "this or that" attributes, always in the same order with the same icons (D95).
    static let attributeIcons = ["arrow.triangle.swap", "cloud.sun", "gauge.with.dots.needle.33percent",
                                 "person.3", "sterlingsign.circle", "figure.walk"]

    /// 20 Oct (round 2): the weather line's icon follows its words (rain, cold, mild), so the picture never contradicts
    /// the text.
    static func attributeIcon(_ i: Int, _ text: String) -> String {
        if i == 1 {
            if text.contains("rain") { return "cloud.rain" }
            if text.contains("cold") { return "thermometer.snowflake" }
            if text.contains("mild") { return "sun.max" }
        }
        return i < attributeIcons.count ? attributeIcons[i] : "circle"
    }
}

struct WhyStep: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        let choices = model.onboarding?.whyTravel
        let prompt = PromptText.split(choices?.prompt ?? "How do you most want to feel on a day out? Pick one or two.")
        let options = choices?.options ?? []
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                StepHeader(model.questionLabel, progress: model.questionProgress)
                PageTitle(text: prompt.0).padding(.top, 6).settle(0)
                if let sub = prompt.1 {
                    Text(sub).foregroundStyle(Theme.muted).padding(.bottom, 6)
                }
                ForEach(options.indices, id: \.self) { i in
                    let key = options[i]
                    let on = model.why.contains(key)
                    SelectTile(on: on, action: { pick(key, on) }) {
                        HStack(spacing: 14) {
                            VStack(alignment: .leading, spacing: 3) {
                                Text(Labels.why[key] ?? key)
                                    .font(Theme.option)
                                    .foregroundStyle(Theme.ink)
                                if let note = Labels.whyNote[key] {
                                    Text(note)
                                        .font(.subheadline)
                                        .foregroundStyle(Theme.inkTertiary)
                                        .fixedSize(horizontal: false, vertical: true)
                                }
                            }
                            Spacer(minLength: 8)
                            TickBox(on: on)   // D118: squares mean "pick more than one"
                        }
                        .padding(.horizontal, 18)
                        .padding(.vertical, 14)
                    }
                    .settle(i + 1)
                }
                // D117: what we take from it, in their own words
                ReactionSpace(text: model.why.isEmpty ? nil
                              : "Got it: you want to feel " + model.why.joined(separator: " and ") + ".")
                PrimaryButton(title: "Continue", disabled: model.why.isEmpty) {
                    model.keepFeelings()             // journey audit: kept even if the app is closed before the end
                    model.next()
                }
                // D118: opting out is never the loudest button; 19 Oct review: but a real one, easy to see and tap
                SecondaryButton(title: "None of these") {
                    model.why = []
                    model.keepFeelings()
                    model.next()
                }
                .frame(maxWidth: .infinity)
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
    }

    /// Up to two: a third choice takes the place of the first one.
    private func pick(_ key: String, _ on: Bool) {
        if on {
            model.why.removeAll { $0 == key }
        } else {
            if model.why.count >= 2 { model.why.removeFirst() }
            model.why.append(key)
        }
    }
}

// ---- 6. Places you've been (6 before the plan, 4 more in screen 12; D112) -------------------------

struct PlacesStep: View {
    @Environment(AppModel.self) private var model
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    let places: [SwipePlace]
    var standalone = false          // in "Improve future plans": counted on its own
    let onDone: () async -> Void
    @State private var index = 0
    @State private var answered: String?
    @State private var advance: Task<Void, Never>?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                StepHeader(standalone ? "\(min(index + 1, places.count)) of \(places.count)" : model.questionLabel,
                           progress: standalone ? Double(index) / Double(max(places.count, 1)) : model.questionProgress) {
                    // D112: the unanswered ones aren't sent
                    if index < places.count { QuietButton("Skip the rest") { Task { await onDone() } }.disabled(model.busy) }
                }
                if index < places.count {
                    let place = places[index]
                    VStack(alignment: .leading, spacing: 16) {
                        PlaceField(title: place.name,
                                   photoId: place.photoIds?.first { CardPhotos.photo(for: $0) != nil }, feel: nil)
                        Text(model.onboarding?.swipe?.prompt ?? "Have you been? How did it feel?")
                            .foregroundStyle(Theme.inkSoft)
                        LazyVGrid(columns: [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)],
                                  spacing: 10) {
                            ForEach(Labels.reactions, id: \.0) { pair in
                                AnswerTile(title: pair.1, on: (answered ?? model.reactions[place.item]) == pair.0) {
                                    react(place, pair.0)
                                }
                            }
                        }
                    }
                    .id(place.item)
                    .transition(.opacity)
                    ReactionSpace(text: model.reaction)   // D117: loved / didn't enjoy say something; the rest don't
                    HStack {
                        QuietButton("Previous") { back() }
                            .disabled(index == 0)
                        Spacer()
                        QuietButton("Not sure, skip") { react(place, "skip") }
                    }
                } else {
                    StepEnd(text: "That's all \(places.count) places. Thank you.",
                            onBack: { index = max(places.count - 1, 0) }, onDone: onDone)
                }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
        .animation(reduceMotion ? nil : Motion.fade, value: index)
    }

    private func back() {
        advance?.cancel()
        answered = nil
        model.reaction = nil
        index = max(index - 1, 0)
        model.stepProgress = index
    }

    /// The answer shows at once (and its reaction, if it has one); the next place follows by itself.
    private func react(_ place: SwipePlace, _ reaction: String) {
        model.reactions[place.item] = reaction
        model.react(place.reactions, reaction)
        answered = reaction
        let wait = model.reaction == nil ? 300 : 1100     // long enough to read a reaction
        advance?.cancel()
        advance = Task {
            try? await Task.sleep(for: .milliseconds(wait))
            if Task.isCancelled { return }
            answered = nil
            model.reaction = nil
            index += 1
            model.stepProgress = index
            if index >= places.count { await onDone() }
        }
    }
}

// ---- 7. This or that: made-up example days (5 before the plan, 5 more in screen 12; D112) --------------

struct ThisOrThatStep: View {
    @Environment(AppModel.self) private var model
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    let tasks: [ConjointTask]
    var standalone = false
    let onDone: () async -> Void
    @State private var index = 0
    @State private var picked: String?

    var body: some View {
        let label = model.onboarding?.conjoint?.optionLabel ?? "Example day"
        let prompt = PromptText.split(model.onboarding?.conjoint?.prompt
                                      ?? "Which day sounds more like you? There are no wrong answers.")
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                StepHeader(standalone ? "\(min(index + 1, tasks.count)) of \(tasks.count)" : model.questionLabel,
                           progress: standalone ? Double(index) / Double(max(tasks.count, 1)) : model.questionProgress)
                if index < tasks.count {
                    let task = tasks[index]
                    PageTitle(text: prompt.0).padding(.top, 6)
                    if let sub = prompt.1 {
                        Text(sub).foregroundStyle(Theme.muted)
                    }
                    VStack(spacing: 10) {
                        DayOption(label: "\(label) A", text: task.a, field: index % 2,
                                  on: (picked ?? model.choices[task.task]) == "A") { choose(task, "A") }
                        Text("or")
                            .font(Theme.italic(18, relativeTo: .body))
                            .foregroundStyle(Theme.muted)
                        DayOption(label: "\(label) B", text: task.b, field: (index + 1) % 2,
                                  on: (picked ?? model.choices[task.task]) == "B") { choose(task, "B") }
                    }
                    .id(task.task)
                    .transition(.opacity)
                    HStack {
                        QuietButton("Previous") {
                            picked = nil
                            index = max(index - 1, 0)
                            model.stepProgress = index
                        }
                        .disabled(index == 0)
                        Spacer()
                        if picked == nil, let earlier = model.choices[task.task] {   // journey round 2: answered before
                            QuietButton("Keep \(earlier == "N" ? "no preference" : earlier), next", color: Theme.accent) {
                                choose(task, earlier)
                            }
                        } else {
                            QuietButton(model.onboarding?.conjoint?.noPreference ?? "No preference") { choose(task, "N") }
                        }
                    }
                    ReactionSpace(text: model.reaction)   // D117: a pattern, once it has held 3 times
                } else {
                    StepEnd(text: standalone ? "Thank you. Your next plans will use these." : "That's everything. Next: what I've learned so far.",
                            onBack: { index = max(tasks.count - 1, 0) }, onDone: onDone)
                }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
        .animation(reduceMotion ? nil : Motion.fade, value: index)
        .onAppear {   // journey round 2: back from "So far", pick up at the first pair not answered
            if index == 0, let first = tasks.firstIndex(where: { model.choices[$0.task] == nil }), first > 0 {
                index = first
                model.stepProgress = first
            } else if index == 0, !tasks.isEmpty, tasks.allSatisfy({ model.choices[$0.task] != nil }) {
                index = tasks.count
            }
        }
    }

    /// Select (250 ms) on the chosen day, then the next pair.
    private func choose(_ task: ConjointTask, _ choice: String) {
        guard picked == nil else { return }   // one choice per pair, even with a quick second tap
        picked = choice
        model.choices[task.task] = choice    // "N": no preference (D110), left out of the fit
        model.reactToChoices(tasks)
        Task {
            try? await Task.sleep(for: .milliseconds(280))
            picked = nil
            index += 1
            model.stepProgress = index
            if index >= tasks.count { await onDone() }
        }
    }
}

/// One made-up day: all six details, each with its icon (D95; Abram kept the six, D119). 19 Oct review: both days on
/// the same quiet field (a red one could make a day look worse before it's read), with a plain cue to choose.
struct DayOption: View {
    let label: String
    let text: String
    let field: Int
    var on = false
    let action: () -> Void

    var body: some View {
        let parts = text.components(separatedBy: "; ")
        Button {
            Haptics.light()
            action()
        } label: {
            VStack(alignment: .leading, spacing: 10) {
                HStack(alignment: .firstTextBaseline) {
                    Text(label).font(Theme.serif(22, relativeTo: .title3)).foregroundStyle(Theme.ink)
                    Spacer()
                    Text("Made up").font(.footnote).foregroundStyle(Theme.inkSoft)
                }
                ForEach(parts.indices, id: \.self) { i in
                    HStack(alignment: .firstTextBaseline, spacing: 10) {
                        Image(systemName: Labels.attributeIcon(i, parts[i]))
                            .font(.subheadline)
                            .foregroundStyle(Theme.accent)
                            .frame(width: 22)
                        Text(parts[i].prefix(1).uppercased() + String(parts[i].dropFirst()))
                            .foregroundStyle(Theme.ink)
                            .multilineTextAlignment(.leading)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                // 20 Oct (round 2): a pill, so it reads as the thing to tap
                Label(on ? "Chosen" : "Choose this day", systemImage: on ? "checkmark" : "hand.tap")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(on ? Theme.background : Theme.accent)
                    .padding(.horizontal, 16)
                    .frame(minHeight: 40)
                    .background(on ? Theme.accent : Color.clear, in: Capsule())
                    .overlay(Capsule().stroke(Theme.accent, lineWidth: 1))
                    .padding(.top, 4)
            }
            .padding(20)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(on ? Theme.selected : Theme.surface)
            .clipShape(RoundedRectangle(cornerRadius: 24))
            .overlay(RoundedRectangle(cornerRadius: 24).stroke(on ? Theme.accent : Theme.outline, lineWidth: on ? 2 : 1))
            .contentShape(RoundedRectangle(cornerRadius: 24))
            .animation(Motion.select, value: on)
        }
        .buttonStyle(PressStyle())
        .accessibilityHint("Choose this made-up day")
    }
}

// ---- 12. Improve future plans (D115): one question at a time ---------------------------------------------

/// An invitation, then one quick question per screen: tap an answer and the next one comes. Skip any, stop any time;
/// what's answered is saved. Seven taps, about a minute (D127: 30 seconds was optimistic). The 4 more places and 5 more example days come after,
/// as their own optional step (about a minute).
struct ImproveView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    var startAt = -1               // CI screenshots: 0 opens the first question
    @State private var step = -2   // -2: not set yet (startAt is used); -1: the invitation
    @State private var morePlaces = false
    @State private var moreTasks = false

    // D123: "where did you grow up" and "foods you avoid" are no longer asked: the plans never used them
    private enum Q: CaseIterable { case budget, company, chronotype, activity, fields, photos, shotCard }

    var body: some View {
        let current = step == -2 ? startAt : step
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    if current < 0 {
                        invitation
                    } else if current < Q.allCases.count {
                        StepHeader("\(current + 1) of \(Q.allCases.count)",
                                   progress: Double(current) / Double(Q.allCases.count)) {
                            QuietButton("Skip") { go(current + 1) }
                        }
                        question(Q.allCases[current])
                        HStack {
                            QuietButton("Previous") { go(current - 1) }.disabled(current == 0)
                            Spacer()
                            QuietButton("Stop here, keep my answers") { Task { await save(done: false) } }
                                .disabled(model.busy)
                        }
                    } else {
                        finished
                    }
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 24)
            }
            .background(Theme.background)
            .scrollDismissesKeyboard(.interactively)
            .serifTitle("Improve future plans")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Close") {   // journey round 2: closing keeps what was answered (Test A's scales too)
                        if current >= 0 { Task { await model.saveImprovements(done: false); dismiss() } } else { dismiss() }
                    }
                }
            }
            .sheet(isPresented: $morePlaces) {
                NavigationStack {
                    PlacesStep(places: model.onboarding?.swipePlacesLater ?? [], standalone: true) {
                        await model.finishMorePlaces()
                        if model.errorMessage == nil { morePlaces = false }
                    }
                    .background(Theme.background)
                    .serifTitle("More places")
                    .toolbar { ToolbarItem(placement: .topBarTrailing) { Button("Close") { morePlaces = false } } }
                }
                .followsSky()
            }
            .sheet(isPresented: $moreTasks) {
                NavigationStack {
                    ThisOrThatStep(tasks: model.onboarding?.conjointTasksLater ?? [], standalone: true) {
                        await model.finishMoreTasks()
                        if model.errorMessage == nil { moreTasks = false }
                    }
                    .background(Theme.background)
                    .serifTitle("More example days")
                    .toolbar { ToolbarItem(placement: .topBarTrailing) { Button("Close") { moreTasks = false } } }
                }
                .followsSky()
            }
        }
    }

    private func go(_ next: Int) {
        withAnimation(reduceMotion ? Motion.fade : Motion.settle) { step = max(0, next) }   // D130: one settle rule
        // journey round 2: saved here at the end; "Done" then only closes (it sent "improve_done" twice)
        if next >= Q.allCases.count { Task { await model.saveImprovements(done: true) } }
    }

    private func save(done: Bool) async {
        await model.saveImprovements(done: done)
        if model.errorMessage == nil { dismiss() }
    }

    private var invitation: some View {
        VStack(alignment: .leading, spacing: 16) {
            ArchGlyph(width: 22).padding(.top, 12)
            PageTitle(text: "Make your next day even better?")   // D118: was "Want us to learn you better?"
            Text("About a minute. One quick question at a time: your budget, who you go with, your pace, what interests you. Skip any, stop any time.")
                .foregroundStyle(Theme.inkSoft)
                .fixedSize(horizontal: false, vertical: true)
            Text("Your budget and interests shape your next plans; the other answers help us test the idea.")   // D123: honest
                .font(.footnote)
                .foregroundStyle(Theme.muted)
            PrimaryButton(title: model.improved ? "Change my answers" : "Start") { go(0) }
                .padding(.top, 8)
            QuietButton("Not now") { dismiss() }
                .frame(maxWidth: .infinity)
        }
    }

    private var finished: some View {
        VStack(alignment: .leading, spacing: 16) {
            ArchGlyph(width: 22).padding(.top, 12)
            PageTitle(text: "Thank you.")
            Text("Your next plans will use your budget and interests.")
                .foregroundStyle(Theme.inkSoft)
            let later = model.isVisitor ? [] : (model.onboarding?.swipePlacesLater ?? [])   // D116: not London places
            let laterTasks = model.onboarding?.conjointTasksLater ?? []
            if !later.isEmpty || !laterTasks.isEmpty {
                Text("Want to go further? About 2 minutes more.")
                    .font(.headline)
                    .foregroundStyle(Theme.ink)
                    .padding(.top, 8)
                if !later.isEmpty {
                    Button { morePlaces = true } label: {
                        MoreRow(title: "\(later.count) more places you may have been", done: model.morePlacesDone)
                    }
                    .buttonStyle(PressStyle())
                }
                if !laterTasks.isEmpty {
                    Button { moreTasks = true } label: {
                        MoreRow(title: "\(laterTasks.count) more made-up example days", done: model.moreTasksDone)
                    }
                    .buttonStyle(PressStyle())
                }
            }
            PrimaryButton(title: model.busy ? "Saving…" : "Done", disabled: model.busy) {
                // already saved on reaching this screen; saved again only if that failed (journey round 2)
                if model.improved { dismiss() } else { Task { await save(done: true) } }
            }
            .padding(.top, 8)
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
                    SelectTile(on: on, action: {
                        model.profile.fields.removeAll { $0 == option.key }
                        if !on { model.profile.fields.append(option.key) }
                    }) {
                        HStack {
                            Text(option.label).foregroundStyle(Theme.ink)
                            Spacer()
                            TickBox(on: on)
                        }
                        .padding(.horizontal, 18)
                    }
                }
                Text(fields.note).font(.footnote).foregroundStyle(Theme.muted)
                PrimaryButton(title: model.profile.fields.isEmpty ? "None of these" : "Next") { go(5) }
            } else {
                PrimaryButton(title: "Next") { go(5) }
            }
        case .photos:
            QuestionTitle(photos.first?.text ?? "How much do photos and sharing matter on your trips?")
            ScaleRow(low: "Not at all", high: "A lot", value: $model.profile.photosMatter)
            PrimaryButton(title: "Next", disabled: model.profile.photosMatter == nil) { go(6) }
        case .shotCard:
            QuestionTitle(photos.count > 1 ? photos[1].text : "Some stops come with a shot card: where to stand for the best photo. Would that make you more likely to go?")
            if let card = model.onboarding?.exampleShotCard {
                ShotCardSummary(card: card, label: photos.count > 1 ? photos[1].exampleLabel : nil)
                    .surfaceCard()
            }
            ScaleRow(low: "No", high: "Definitely", value: $model.profile.shotCardAppeal)
            PrimaryButton(title: "Finish", disabled: model.profile.shotCardAppeal == nil) { go(7) }
        }
    }
}

struct QuestionTitle: View {
    let text: String
    init(_ text: String) { self.text = text }

    var body: some View {
        PageTitle(text: text, font: Theme.title)
            .padding(.vertical, 6)
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
        SelectTile(on: on, minHeight: 56, action: action) {
            HStack {
                Text(label).foregroundStyle(Theme.ink)
                Spacer()
                RadioDot(on: on)
            }
            .padding(.horizontal, 18)
        }
    }
}

struct MoreRow: View {
    let title: String
    let done: Bool

    var body: some View {
        HStack {
            Text(title).foregroundStyle(Theme.ink).multilineTextAlignment(.leading)
            Spacer()
            if done {
                Label("Done", systemImage: "checkmark").labelStyle(.titleAndIcon).font(.footnote)
                    .foregroundStyle(Theme.muted)
            } else {
                Image(systemName: "chevron.right").foregroundStyle(Theme.muted)
            }
        }
        .padding(.horizontal, 18)
        .frame(minHeight: 56)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
    }
}

/// The short shot-card example (D112): where to stand and when, with a small map. The full card opens from a stop.
struct ShotCardSummary: View {
    let card: Card
    var label: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Eyebrow(label ?? "Example of what you'll get")
            Label(card.title, systemImage: "camera").font(.headline).foregroundStyle(Theme.ink)
            if let shot = card.shotCard {
                if let lat = shot.standAt?.lat, let lon = shot.standAt?.lon {
                    let here = CLLocationCoordinate2D(latitude: lat, longitude: lon)
                    Map(initialPosition: .region(MKCoordinateRegion(center: here, latitudinalMeters: 500,
                                                                    longitudinalMeters: 500))) {
                        Marker("Stand here", coordinate: here).tint(Theme.accentFill)
                    }
                    .frame(height: 110)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .allowsHitTesting(false)
                }
                InfoBlock(label: "Where to stand", text: shot.standAt?.note ?? "")
                InfoBlock(label: "When", text: shot.when ?? "")
            }
        }
        .padding(.vertical, 4)
    }
}
