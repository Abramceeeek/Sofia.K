import SwiftUI

/// D119 (ODYS, new): "Now", the screen for while you're out. Quiet on purpose: the stop you're at, "Enjoy it. I'll stay
/// quiet until you need me.", a slowly breathing arch, and what's next. "I'm done here" asks for the rating (the visit
/// is over, D110), then moves on to the next stop. Where you are in the day is kept per plan. D123: with location on,
/// how far the stop is, and the rating asked for once they've left it. m176: a trip day's journeys at each end.
/// Abram's comment (8 Oct): at the end of a trip's day, "Preview tomorrow", where the day can still be changed.
/// D130 (the arrival moment): on the way, the stop's way in and "I'm here"; once there (tapped, or seen by the phone),
/// the screen brightens once, like coming out of the station into the open, and shows what to notice. With Reduce
/// Motion on it only fades. The day's path sits under the way in.
struct NowView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL
    @State private var rating: Stop?
    @State private var showSafety = false
    @State private var card: Stop?
    @State private var onTheWay: Stop?               // journey round 2: rating the place on the way (its own plan)
    @State private var replanning = false            // decision 3: "Re-plan the rest of today"
    @State private var asked: Set<String> = []       // D123: stops already asked about after leaving
    @State private var glow = 0.0                    // D130: the light opening out as you arrive
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        let stops = model.plan?.stops ?? []
        let i = min(model.nowIndex, stops.count)
        let tripDay = model.currentTripDay?.day
        NavigationStack {
            ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if i == 0, let day = tripDay {   // m176: the trip's first journeys come before the first stop
                    ForEach(day.journeys("arrive"), id: \.self) { JourneyCard(leg: $0) }
                    if let before = day.before {   // the place on the way, when travelling light (as on the day's page)
                        SectionLabel(text: "On the way · travelling light")
                        ForEach(before.stops) { stop in
                            TripDayStop(stop: stop)
                            if stop.rateable, !model.rated.contains(stop.momentId) {   // journey round 2: rated too
                                QuietButton("Been there? How was it?", color: Theme.accent) { onTheWay = stop }
                            }
                        }
                    }
                    ForEach(day.journeys("to_stay"), id: \.self) { JourneyCard(leg: $0) }
                }
                if i < stops.count {
                    let stop = stops[i]
                    let here = model.arrivedStops.contains(stop.id) || lookAhead != nil
                    Eyebrow(here ? "Now" : "Next · around \(stop.arrive)")
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
                    if let line = distanceLine(stop) {   // D123: from the phone's location, never sent
                        Label(line, systemImage: "location.fill")
                            .font(.subheadline)
                            .foregroundStyle(Theme.accent)
                    }
                    if !here {
                        // D130: on the way, how you arrive is part of the moment
                        let steps = stop.approachSteps ?? []
                        if !steps.isEmpty || !stop.approach.isEmpty || !stop.travelText.isEmpty {
                            VStack(alignment: .leading, spacing: 10) {
                                SectionLabel(text: "The way in")
                                if !steps.isEmpty {
                                    WayIn(steps: steps, reveal: stop.reveal == true)
                                } else {
                                    Text(stop.approach.isEmpty ? stop.travelText : stop.approach)
                                        .foregroundStyle(Theme.inkSoft)
                                        .fixedSize(horizontal: false, vertical: true)
                                }
                            }
                            .surfaceCard(padding: 18, radius: 20)
                            .transition(.opacity)
                        }
                        DayPath(stops: stops, current: i, height: 120)
                        if let pin = stop.pin {
                            // 20 Oct (round 2): the way there without opening the card; by Tube or bus when the leg is
                            let mode = stop.travelMode == "transit" ? "r" : "w"
                            SecondaryButton(title: "Directions") {
                                if let url = URL(string: "http://maps.apple.com/?daddr=\(pin.lat),\(pin.lon)&dirflg=\(mode)") { openURL(url) }
                            }
                        }
                        PrimaryButton(title: "I'm here") { arrive(stop, how: "tap") }
                    } else {
                        if !stop.what.isEmpty, lookAhead == nil {
                            Text(stop.what)
                                .font(Theme.italic(21, relativeTo: .title3))
                                .foregroundStyle(Theme.ink)
                                .fixedSize(horizontal: false, vertical: true)
                                .transition(.opacity)
                        }
                        Text(lookAhead.map { "A look ahead: this day is \($0). Ratings open on the day." }
                             ?? "Enjoy it. I'll stay quiet until you need me.")
                            .foregroundStyle(Theme.inkSoft)
                            .fixedSize(horizontal: false, vertical: true)
                        Spacer(minLength: 12)
                        BreathingArch(showSun: true).frame(maxWidth: .infinity)
                        Spacer(minLength: 12)
                        if i + 1 < stops.count {
                            NextUp(stop: stops[i + 1])
                        } else if let leave = tripDay?.journeys("leave").first {   // journey round 2: the way home, ahead
                            Label("After this: \(leave.title)", systemImage: "airplane.departure")
                                .font(.subheadline)
                                .foregroundStyle(Theme.inkSoft)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        PrimaryButton(title: "I'm done here") { done(stop) }
                    }
                    if lookAhead == nil {   // journey round 2: a closed place or a long queue needn't be rated to move on
                        QuietButton("Didn't go? Skip this stop") { skip(stop) }
                        if model.lastRequest != nil {   // decision 3; never on the Test B plan
                            QuietButton("Plans changed? Re-plan the rest of today", color: Theme.accent) { replanning = true }
                        }
                    }
                    // 19 Oct review: asked under the day's own buttons, so the stop and "I'm done here" come first
                    if !model.location.asked && (!model.client.demo || model.screen == "nowlocation") {
                        LocationAsk()
                    }
                } else {
                    if let day = tripDay {   // m176: the way back for bags, and on to the airport or station
                        ForEach(day.journeys("back") + day.journeys("leave"), id: \.self) { JourneyCard(leg: $0) }
                    }
                    Eyebrow("That's the day")
                    Text("Thanks for today.")
                        .font(Theme.hero)
                        .foregroundStyle(Theme.ink)
                    Text("Every stop you rated makes the next day fit you better.")
                        .foregroundStyle(Theme.inkSoft)
                    if let id = model.plan?.id, lookAhead == nil {
                        DayEndQuestions(planId: id).padding(.top, 8)
                    }
                    Spacer(minLength: 12)
                    BreathingArch().frame(maxWidth: .infinity)
                    Spacer(minLength: 12)
                    if let next = model.nextTripDay {   // Abram's comment (8 Oct): look at tomorrow tonight
                        Text("Tomorrow is Day \(next.index + 1). Have a look tonight: if you've made other plans, change its hours and I'll plan around them.")
                            .font(.subheadline)
                            .foregroundStyle(Theme.inkSoft)
                            .fixedSize(horizontal: false, vertical: true)
                        PrimaryButton(title: model.busy ? "Planning…" : "Preview tomorrow: Day \(next.index + 1)",
                                      disabled: model.busy) {
                            Task {
                                await model.planTripDayIfNeeded(next.trip.id, next.index)
                                dismiss()
                                try? await Task.sleep(for: .milliseconds(450))   // the cover closes, then the trip opens
                                model.openTripDay(next.trip.id, next.index, from: "now")
                            }
                        }
                    } else {
                        PrimaryButton(title: "See the whole day") { dismiss() }
                    }
                }
                HStack {
                    if i < stops.count || model.nextTripDay != nil {   // m176: not twice on the last screen
                        QuietButton("See the whole day") { dismiss() }
                    }
                    Spacer()
                    QuietButton("Help") { showSafety = true }
                }
            }
            .padding(.horizontal, 28)
            .padding(.top, 40)
            .padding(.bottom, 12)
            }
            .defaultScrollAnchor(model.screen == "nowlocation" ? UnitPoint.bottom : nil)   // CI screenshots: the ask
            .skyBackground(base: Theme.calm)   // D130
            .overlay {   // D130: the light opening out as you arrive; it never takes a tap
                RadialGradient(colors: [Theme.amberLight.opacity(glow), .clear], center: UnitPoint(x: 0.5, y: 0.2),
                               startRadius: 0, endRadius: 700)
                    .ignoresSafeArea()
                    .allowsHitTesting(false)
                    .accessibilityHidden(true)
            }
            .animation(reduceMotion ? Motion.fade : Motion.settle, value: model.arrivedStops)
            .toolbar(.hidden, for: .navigationBar)
            .navigationDestination(item: $card) { StopView(stop: $0) }
        }
        .sheet(item: $rating) { stop in
            RatingView(stop: stop, onNext: { model.advanceNow() }).brainFeedback()
        }
        .sheet(isPresented: $showSafety) { SafetyView().brainFeedback() }
        .sheet(item: $onTheWay) { stop in
            RatingView(stop: stop, planId: model.currentTripDay?.day.before?.id).brainFeedback()
        }
        .replanRest(isPresented: $replanning)
        .onAppear {
            model.location.start()
            if model.screen == "replan" {   // CI screenshots only: the question, open
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) { replanning = true }
            }
        }
        .onDisappear { model.location.stop() }
        .onChange(of: model.location.here?.latitude) { _, _ in noticeArrival(stops, i) }
    }

    /// D123: "You're here", or how far the stop is, while location is on.
    private func distanceLine(_ stop: Stop) -> String? {
        guard model.location.usable, let pin = stop.pin, let m = model.location.metres(to: pin) else { return nil }
        return m < 120 || model.arrivedStops.contains(stop.id) && m < 250 ? "You're here" : Location.walkText(m)
    }

    /// D130: they've arrived. The way in gives way to what to notice, and the light opens out once (a fade only with
    /// Reduce Motion on). Counted, by how, so the test knows whether "I'm here" is used.
    private func arrive(_ stop: Stop, how: String) {
        guard !model.arrivedStops.contains(stop.id) else { return }
        Haptics.light()
        model.markArrived(stop)
        Task { await model.client.event("arrived", ["how": how]) }
        guard !reduceMotion else { return }
        withAnimation(.easeOut(duration: 0.26)) {
            glow = 0.6
        } completion: {
            withAnimation(.timingCurve(0.2, 0.7, 0.2, 1, duration: 1.1)) { glow = 0 }
        }
    }

    /// D123: once the phone has seen them at the stop (within 120 m) and then about 250 m away, the visit is over, so
    /// the rating is asked for once (D110: only after the visit). Nothing about where they are is sent.
    private func noticeArrival(_ stops: [Stop], _ i: Int) {
        guard model.location.usable, i < stops.count, rating == nil else { return }
        let stop = stops[i]
        guard let pin = stop.pin, let m = model.location.metres(to: pin) else { return }
        if m < 120 { arrive(stop, how: "location"); return }
        if m > 250, model.arrivedStops.contains(stop.id), !asked.contains(stop.id), stop.rateable, !model.rated.contains(stop.momentId) {
            asked.insert(stop.id)
            rating = stop
            Task { await model.client.event("rating_on_leaving") }
        }
    }

    /// Journey round 2: "Start the day" on a plan for a later day is a look ahead: nothing is rated before the day.
    private var lookAhead: String? {
        guard let date = model.plan?.date, date > Dates.isoDay.string(from: .now) else { return nil }
        return Dates.shortDay(date)
    }

    /// Journey round 2: they didn't go (closed, a queue, changed their mind). On to the next stop, no rating and no
    /// reminder for it; counted, so the test knows which stops were skipped.
    private func skip(_ stop: Stop) {
        Reminders.cancel(stop: stop)
        Task { await model.client.event("stop_skipped", ["moment": stop.momentId]) }
        withAnimation(Motion.settle) { model.advanceNow() }
    }

    /// "I'm done here" says the visit is over, so an unrated stop asks for its rating whatever the planned time
    /// (journey audit: people ahead of the plan lost their ratings). Rated stops and lunch slots simply move on.
    private func done(_ stop: Stop) {
        if stop.rateable, !model.rated.contains(stop.momentId), lookAhead == nil {
            rating = stop
        } else {
            withAnimation(Motion.settle) { model.advanceNow() }
        }
    }
}

/// D123: asked once, the first time "Now" opens, with equal-weight answers; iOS's own prompt comes only after a yes.
struct LocationAsk: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Use your location while you're out?")
                .font(.headline)
                .foregroundStyle(Theme.ink)
            Text("I'll show how far your next stop is, and ask how it felt once you've left. Your location stays on your phone.")
                .font(.subheadline)
                .foregroundStyle(Theme.inkSoft)
                .fixedSize(horizontal: false, vertical: true)
            HStack(spacing: 10) {
                SecondaryButton(title: "Yes, use it") {
                    model.location.turnOn()
                    Task { await model.client.event("location_on") }
                }
                SecondaryButton(title: "No thanks") {
                    model.location.turnOff()
                    Task { await model.client.event("location_off") }
                }
            }
        }
        .surfaceCard(padding: 16)
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
/// (Disappointing … Unforgettable), and the light spills as it rises. Save sends it (so a mis-tap isn't sent); then a mote of
/// light rises into the arch, a thank-you, and "Share this moment" (for any rating, D114) or on to the next stop.
struct RatingView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let stop: Stop
    var planId: Int?                 // journey round 2: the stop's own plan (the place on the way), if not "your day"
    var onNext: (() -> Void)?
    var savedRating: Int?            // CI screenshots only: the thank-you, after saving
    var pickedRating: Int?           // CI screenshots only: a word chosen, before Save
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
                        ScaleRow(low: "Disappointing", high: "Unforgettable", labels: Labels.feel, value: $rating)
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
                } else if let pickedRating, rating == nil {
                    rating = pickedRating
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
                Text("Saved on your phone. It'll send the next time you open ODYS with signal.")
                    .font(.footnote)
                    .foregroundStyle(Theme.muted)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: .infinity)
            }
            // 19 Oct review: moving on is the main thing mid-day; sharing is there, not pushed
            PrimaryButton(title: onNext == nil ? "Done" : "On to the next stop") {
                onNext?()
                dismiss()
            }
            if !model.lastRatingQueued, !stop.momentId.hasPrefix("generic:") {   // m176: a generic Test B stop has no card
                SecondaryButton(title: "Share this moment", icon: "square.and.arrow.up") { sharing = true }
            }
        }
        .settle()
    }

    private func save() {
        guard let rating else { return }
        Task {
            await model.rate(stop, rating: rating, wouldBring: bring.isEmpty ? nil : bring == "yes", planId: planId)
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

/// D127 (algorithm reviews): the product's second outcome, how worthwhile the money felt (CLAUDE.md), which nothing
/// else measured. Two taps, both optional, once the day is done.
struct DayEndQuestions: View {
    @Environment(AppModel.self) private var model
    let planId: Int
    @State private var answer = DayFeedback()

    var body: some View {
        VStack(alignment: .leading, spacing: 22) {
            Text("Two quick questions, both optional.")   // m191 (design review)
                .font(.footnote)
                .foregroundStyle(Theme.muted)
            SurveyQuestion(text: "Was today worth what you spent on it?") {
                HStack(spacing: 8) {
                    ForEach([("less", "Not quite"), ("about_right", "Yes"), ("more", "More than that")], id: \.0) { key, label in
                        Chip(title: label, on: answer.worth == key) {
                            answer.worth = answer.worth == key ? nil : key
                            send()
                        }
                    }
                }
            }
            SurveyQuestion(text: "Would you do this day again?") {
                HStack(spacing: 8) {
                    ForEach([(true, "Yes"), (false, "No")], id: \.0) { key, label in
                        Chip(title: label, on: answer.again == key) {
                            answer.again = answer.again == key ? nil : key
                            send()
                        }
                    }
                }
            }
        }
        .onAppear { answer = model.dayFeedback(for: planId) }
    }

    private func send() {
        let now = answer
        Task { await model.answerDay(planId, now) }
    }
}

/// D114, D119: the share card before it's sent, lifted into place. It carries the person's own rating and their own
/// reason (D115), never the model's "worth £X"; no rewards.
struct SharePreview: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let stop: Stop
    let rating: Int
    @State private var reason = true

    var body: some View {
        let hasReason = stop.reasons?.contains { $0.me != nil } ?? false
        ScrollView {
            VStack(spacing: 18) {
                ShareCardView(stop: stop, rating: rating, reason: reason)
                    .clipShape(RoundedRectangle(cornerRadius: 26))
                    .shadow(color: .black.opacity(0.45), radius: 30, y: 24)
                    .modifier(Lift())
                    .padding(.top, 8)
                if hasReason {   // D127: the reason is worded by ODYS from their answers, so it's theirs to leave out
                    Toggle(isOn: $reason) {
                        Text("Include the line about why").foregroundStyle(Theme.ink)
                    }
                    .tint(Theme.accent)
                }
                Text(reason && hasReason ? "Your rating and the line about why go with it, and nothing else about you."
                                         : "Your rating goes with it, and nothing else about you.")
                    .font(.footnote)
                    .foregroundStyle(Theme.muted)
                    .multilineTextAlignment(.center)
                    .fixedSize(horizontal: false, vertical: true)
                PrimaryButton(title: model.busy ? "One moment…" : "Send to a friend", disabled: model.busy) {
                    Task { await model.share(stop, reason: reason) }
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
