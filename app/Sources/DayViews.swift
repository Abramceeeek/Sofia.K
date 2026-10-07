import SwiftUI

/// D119 (ODYS, new): "Now", the screen for while you're out. Quiet on purpose: the stop you're at, "Enjoy it. I'll stay
/// quiet until you need me.", a slowly breathing arch, and what's next. "I'm done here" asks for the rating (only after
/// the planned arrival, D110), then moves on to the next stop. Where you are in the day is kept per plan.
struct NowView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State private var rating: Stop?
    @State private var showSafety = false
    @State private var card: Stop?

    var body: some View {
        let stops = model.plan?.stops ?? []
        let i = min(model.nowIndex, stops.count)
        NavigationStack {
            VStack(alignment: .leading, spacing: 16) {
                if i < stops.count {
                    let stop = stops[i]
                    Eyebrow("Now")
                    Button { card = stop } label: {
                        Text(stop.title)
                            .font(Theme.hero)
                            .foregroundStyle(Theme.ink)
                            .multilineTextAlignment(.leading)
                            .lineLimit(4)
                            .minimumScaleFactor(0.6)
                    }
                    .buttonStyle(.plain)
                    .accessibilityHint("Opens the stop's card")
                    Text("Enjoy it. I'll stay quiet until you need me.")
                        .foregroundStyle(Theme.inkSoft)
                    Spacer(minLength: 12)
                    BreathingArch().frame(maxWidth: .infinity)
                    Spacer(minLength: 12)
                    if i + 1 < stops.count {
                        NextUp(stop: stops[i + 1])
                    }
                    PrimaryButton(title: "I'm done here") { done(stop) }
                } else {
                    Eyebrow("That's the day")
                    Text("Thank you for going.")
                        .font(Theme.hero)
                        .foregroundStyle(Theme.ink)
                    Text("Every stop you rated makes the next day fit you better.")
                        .foregroundStyle(Theme.inkSoft)
                    Spacer(minLength: 12)
                    BreathingArch().frame(maxWidth: .infinity)
                    Spacer(minLength: 12)
                    if let next = model.nextTripDay {   // journey audit: a trip goes on to its next day
                        PrimaryButton(title: model.busy ? "Planning…" : "Tomorrow: Day \(next.index + 1)",
                                      disabled: model.busy) {
                            Task {
                                await model.goToTripDay(next.trip.id, next.index)
                                dismiss()
                            }
                        }
                    } else {
                        PrimaryButton(title: "See the whole day") { dismiss() }
                    }
                }
                HStack {
                    QuietButton("See the whole day") { dismiss() }
                    Spacer()
                    QuietButton("Help") { showSafety = true }
                }
            }
            .padding(.horizontal, 28)
            .padding(.top, 40)
            .padding(.bottom, 12)
            .background(Theme.calm.ignoresSafeArea())
            .toolbar(.hidden, for: .navigationBar)
            .navigationDestination(item: $card) { StopView(stop: $0) }
        }
        .sheet(item: $rating) { stop in
            RatingView(stop: stop, onNext: { model.advanceNow() })
        }
        .sheet(isPresented: $showSafety) { SafetyView() }
    }

    /// "I'm done here" says the visit is over, so an unrated stop asks for its rating whatever the planned time
    /// (journey audit: people ahead of the plan lost their ratings). Rated stops and lunch slots simply move on.
    private func done(_ stop: Stop) {
        if stop.rateable, !model.rated.contains(stop.momentId) {
            rating = stop
        } else {
            withAnimation(Motion.settle) { model.advanceNow() }
        }
    }
}

/// "Next, around 14:34": the next stop and how to get there.
struct NextUp: View {
    let stop: Stop

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("Next, around \(stop.arrive)").font(.subheadline).foregroundStyle(Theme.muted)
            Text(stop.title).foregroundStyle(Theme.ink).fixedSize(horizontal: false, vertical: true)
            if !stop.travelText.isEmpty {
                Text(stop.travelText)
                    .font(.subheadline)
                    .foregroundStyle(Theme.inkTertiary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(.horizontal, 18)
        .padding(.vertical, 16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .overlay(RoundedRectangle(cornerRadius: 18).stroke(Theme.outline, lineWidth: 1))
        .accessibilityElement(children: .combine)
    }
}

/// Screen 11 (D110, D112, D119): after the visit, one word on a 1–5 scale. The arch fills with light to the word
/// (Flat … Unforgettable), and the light spills as it rises. Save sends it (so a mis-tap isn't sent); then a mote of
/// light rises into the arch, a thank-you, and "Share this moment" (for any rating, D114) or on to the next stop.
struct RatingView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let stop: Stop
    var onNext: (() -> Void)?
    var savedRating: Int?            // CI screenshots only: the thank-you, after saving
    @State private var rating: Int?
    @State private var bring = ""
    @State private var saved = false
    @State private var mote = 0
    @State private var sharing = false

    private static let levels: [CGFloat] = [0.12, 0.32, 0.55, 0.8, 1]

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    Eyebrow("Just finished")
                    PageTitle(text: "How did \(stop.title) feel?", font: Theme.serif(30, relativeTo: .largeTitle))
                    RatingArch(level: rating.map { Self.levels[$0 - 1] } ?? 0, mote: mote)
                        .frame(width: 150, height: 190)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 4)
                    if saved {
                        thanks
                    } else {
                        ScaleRow(low: "Flat", high: "Unforgettable", labels: Labels.feel, value: $rating)
                        if rating != nil {
                            VStack(alignment: .leading, spacing: 10) {
                                Text("Would you bring someone here? (optional)")
                                    .font(.subheadline)
                                    .foregroundStyle(Theme.muted)
                                HStack(spacing: 8) {
                                    Chip(title: "Yes", on: bring == "yes", height: 44) { bring = bring == "yes" ? "" : "yes" }
                                    Chip(title: "No", on: bring == "no", height: 44) { bring = bring == "no" ? "" : "no" }
                                }
                            }
                            .padding(.top, 6)
                            .transition(.opacity)
                            PrimaryButton(title: model.busy ? "Saving…" : "Save", disabled: model.busy) { save() }
                        }
                    }
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 24)
                .animation(Motion.fade, value: rating != nil)
            }
            .background(Theme.background)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) { Button("Close") { dismiss() } }
            }
            .navigationDestination(isPresented: $sharing) {
                SharePreview(stop: stop, rating: rating ?? 5)
            }
            .onAppear {
                if let savedRating, rating == nil {
                    rating = savedRating
                    saved = true
                }
            }
        }
    }

    private var thanks: some View {
        VStack(spacing: 12) {
            Text("Thank you. That helps the next day fit better.")
                .font(Theme.italic(19, relativeTo: .body))
                .foregroundStyle(Theme.inkSoft)
                .multilineTextAlignment(.center)
                .frame(maxWidth: .infinity)
            if model.lastRatingQueued {   // journey audit: no signal; kept on the phone
                Text("Saved on your phone. It'll send when you're back online.")
                    .font(.footnote)
                    .foregroundStyle(Theme.muted)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: .infinity)
            } else {
                PrimaryButton(title: "Share this moment") { sharing = true }
            }
            SecondaryButton(title: onNext == nil ? "Done" : "On to the next stop") {
                onNext?()
                dismiss()
            }
        }
        .settle()
    }

    private func save() {
        guard let rating else { return }
        Task {
            await model.rate(stop, rating: rating, wouldBring: bring.isEmpty ? nil : bring == "yes")
            if model.errorMessage == nil {
                withAnimation(Motion.settle) { saved = true }
                mote += 1
            }
        }
    }
}

/// The rating's arch (design 120 × 152): dark inside, filling with light from the bottom to the chosen word; the pool
/// in front brightens with it. The Thank-you mote (600 ms): one small light rises into the arch.
struct RatingArch: View {
    let level: CGFloat
    var mote = 0
    @State private var moteY: CGFloat = 0
    @State private var moteOpacity: Double = 0
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    private static let box = CGSize(width: 120, height: 152)

    var body: some View {
        ZStack {
            DoorShape.rating.fill(Theme.surface)
            DoorShape.rating
                .fill(LinearGradient(colors: [Theme.amberLight, Theme.amberDeep], startPoint: UnitPoint(x: 0.5, y: 24 / 152),
                                     endPoint: UnitPoint(x: 0.5, y: 120 / 152)))
                .mask { RisingLevel(box: Self.box, top: 24, bottom: 120, level: level) }
            DoorShape.rating.stroke(Theme.line, lineWidth: 3)
            PoolShape.rating.fill(Theme.accent).opacity(Double(level) * 0.5)
            Circle()
                .fill(Theme.amberLight)
                .frame(width: 8, height: 8)
                .shadow(color: Theme.accent, radius: 6)
                .offset(y: moteY)
                .opacity(moteOpacity)
        }
        .animation(reduceMotion ? Motion.fade : .timingCurve(0.2, 0.8, 0.2, 1, duration: 0.7), value: level)
        .onChange(of: mote) { _, _ in
            guard !reduceMotion else { return }
            moteY = 60
            moteOpacity = 1
            withAnimation(.easeIn(duration: 0.6)) {
                moteY = -30
                moteOpacity = 0
            }
        }
        .accessibilityHidden(true)
    }
}

/// D114, D119: the share card before it's sent, lifted into place. It carries the person's own rating and their own
/// reason (D115), never the model's "worth £X"; no rewards.
struct SharePreview: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let stop: Stop
    let rating: Int

    var body: some View {
        ScrollView {
            VStack(spacing: 18) {
                ShareCardView(stop: stop, rating: rating)
                    .clipShape(RoundedRectangle(cornerRadius: 26))
                    .shadow(color: .black.opacity(0.45), radius: 30, y: 24)
                    .modifier(Lift())
                    .padding(.top, 8)
                Text("Your rating and your own words go with it, never what we estimated it's worth to you.")
                    .font(.footnote)
                    .foregroundStyle(Theme.muted)
                    .multilineTextAlignment(.center)
                    .fixedSize(horizontal: false, vertical: true)
                PrimaryButton(title: model.busy ? "One moment…" : "Send to a friend", disabled: model.busy) {
                    Task { await model.share(stop) }
                }
                SecondaryButton(title: "Not now") { dismiss() }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 24)
        }
        .background(Theme.background)
        .serifTitle("Share this moment")
    }
}
