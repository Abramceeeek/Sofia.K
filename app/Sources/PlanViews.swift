import MapKit
import SwiftUI

/// D120 (ODYS Trips): the Trip tab. Home is "Where to next?" (plan a trip, your day, your trips); your day, a trip and
/// a trip's day open from it. Help & safety and your data stay one tap away at the top (and in the You tab).
struct HomeView: View {
    @State private var showSafety = false
    @State private var showSettings = false
    @Environment(AppModel.self) private var model

    var body: some View {
        @Bindable var model = model
        NavigationStack(path: $model.path) {   // D118: a rating reminder opens its stop
            TripHome(onHelp: { showSafety = true }, onData: { showSettings = true })
                .toolbar(.hidden, for: .navigationBar)
                .statusBarShade()
                .navigationDestination(for: TripDest.self) { dest in
                    switch dest {
                    case .day: DayView(onHelp: { showSafety = true }, onData: { showSettings = true }, pushed: true)
                    case .trip(let id): TripOverview(tripId: id, onHelp: { showSafety = true })
                    case .tripDay(let id, let index): TripDayView(tripId: id, index: index)
                    }
                }
                .navigationDestination(for: Stop.self) { stop in
                    StopView(stop: stop)
                }
        }
        .sheet(isPresented: $showSafety) { SafetyView().brainFeedback() }
        .sheet(isPresented: $showSettings) { SettingsView().brainFeedback() }
        .fullScreenCover(isPresented: $model.showNow) { NowView().brainFeedback() }   // D119: during the day
    }
}

/// Your day: the current plan (screen 9), or the form to make one (screen 8).
struct DayView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    var onHelp: () -> Void = {}
    var onData: () -> Void = {}
    var pushed = false
    var layout: String?          // CI screenshots only: "list" or "map"
    var reveal: Double?          // CI screenshots only: the plan reveal frozen part-way (D117)
    var scroll: String?          // CI screenshots only: further down the plan ("stops")

    var body: some View {
        Group {
            if let plan = model.plan {
                PlanView(plan: plan, forcedLayout: layout, forcedReveal: reveal, demoScroll: scroll,
                         onHelp: onHelp, onData: onData, onBack: pushed ? { dismiss() } : nil)
            } else {
                PlanFormView(onHelp: onHelp, onData: onData)
            }
        }
        .navigationTitle("Your day")
        .toolbar(.hidden, for: .navigationBar)
        .statusBarShade()
    }
}

/// CI screenshots: the day on its own, as it was before the tabs (screens 8-10).
struct DayScreen: View {
    @Environment(AppModel.self) private var model
    var layout: String?
    var reveal: Double?
    var scroll: String?

    var body: some View {
        @Bindable var model = model
        NavigationStack {
            DayView(layout: layout, reveal: reveal, scroll: scroll)
                .navigationDestination(for: Stop.self) { stop in StopView(stop: stop) }
        }
        .fullScreenCover(isPresented: $model.showNow) { NowView().brainFeedback() }
    }
}

extension Dates {
    /// "Sat 10 Oct", on the day chips.
    static let short: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_GB")
        f.timeZone = TimeZone(identifier: "Europe/London")
        f.dateFormat = "EEE d MMM"
        return f
    }()

    /// "Saturday 31 October" from "2026-10-31".
    static func longDay(_ iso: String?) -> String? {
        guard let iso, let d = isoDay.date(from: iso) else { return nil }
        return dayName.string(from: d)
    }
}

/// Screen 8 (D115, D118): next Saturday, 12:00–17:00 from Charing Cross (the Test B day, D104) is already filled in, so
/// one tap makes the plan. Today and Tomorrow are one tap too; the day, times and number of stops can be changed.
/// The food question stays in "Improve future plans" (D19).
struct PlanFormView: View {
    @Environment(AppModel.self) private var model
    var onDone: (() -> Void)?
    var onHelp: (() -> Void)?
    var onData: (() -> Void)?
    @State private var date = AppConfig.demo ? (Dates.isoDay.date(from: AppConfig.demoDate) ?? Dates.nextSaturday())
                                             : Dates.nextSaturday()
    @State private var start = Dates.time(12)
    @State private var end = Dates.time(17)
    @State private var stops = 4
    @State private var fromHere = false           // D123: start from where I am (location, rounded on the phone)
    @State private var mustDo: MomentSummary?     // m176: a place they want in the day
    @State private var pickMust = false
    @State private var confirm = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                if onHelp != nil || onData != nil {
                    TopBar(eyebrow: "Your day out", onHelp: onHelp, onData: onData)
                }
                PageTitle(text: "Plan a day").settle(0)
                VStack(alignment: .leading, spacing: 10) {
                    Text("When").font(.subheadline).foregroundStyle(Theme.muted)
                    HStack(spacing: 8) {
                        Chip(title: "Today", on: isSameDay(date, .now)) { pickToday() }
                        Chip(title: "Tomorrow", on: isSameDay(date, tomorrow)) { pick(tomorrow) }
                        if !isSameDay(Dates.nextSaturday(), .now), !isSameDay(Dates.nextSaturday(), tomorrow) {
                            Chip(title: Dates.short.string(from: Dates.nextSaturday()),
                                 on: isSameDay(date, Dates.nextSaturday())) { pick(Dates.nextSaturday()) }
                        }
                    }
                }
                .settle(1)
                VStack(spacing: 0) {
                    FormRow(label: "Day") {
                        DatePicker("Day", selection: $date, in: Calendar.current.startOfDay(for: .now)...,
                                   displayedComponents: .date)
                            .labelsHidden()
                    }
                    FormRow(label: "Start") {
                        DatePicker("Start", selection: $start, displayedComponents: .hourAndMinute).labelsHidden()
                    }
                    FormRow(label: "Finish by") {
                        DatePicker("Finish by", selection: $end, displayedComponents: .hourAndMinute).labelsHidden()
                    }
                    FormRow(label: "Stops") {
                        HStack(spacing: 14) {
                            RoundIcon(name: "minus", disabled: stops <= 3) { stops -= 1 }
                            Text("\(stops)")
                                .font(Theme.title3.monospacedDigit())
                                .foregroundStyle(Theme.accent)
                                .frame(minWidth: 20)
                            RoundIcon(name: "plus", disabled: stops >= 5) { stops += 1 }
                        }
                        .accessibilityElement(children: .ignore)
                        .accessibilityLabel("\(stops) stops")
                        .accessibilityAdjustableAction { dir in
                            if dir == .increment, stops < 5 { stops += 1 }
                            if dir == .decrement, stops > 3 { stops -= 1 }
                        }
                    }
                    FormRow(label: "Starting near") {
                        HStack(spacing: 8) {
                            Chip(title: "Charing Cross", on: !fromHere, height: 44) { fromHere = false }
                            Chip(title: "Where I am", on: fromHere, height: 44) { chooseHere() }
                        }
                    }
                    FormRow(label: "Must include", last: true) {
                        Button { pickMust = true } label: {
                            Text(mustDo?.title ?? "Anything")
                                .foregroundStyle(mustDo == nil ? Theme.muted : Theme.accent)
                                .lineLimit(1)
                                .frame(minHeight: 44)
                        }
                        .accessibilityHint("Optional: a place you want in the day")
                    }
                }
                .tint(Theme.accent)
                .environment(\.timeZone, TimeZone(identifier: "Europe/London") ?? .current)   // London times, 24-hour
                .environment(\.locale, Locale(identifier: "en_GB"))
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
                .settle(2)
                Text(startNote)
                    .font(.footnote)
                    .foregroundStyle(Theme.muted)
                    .fixedSize(horizontal: false, vertical: true)
                PrimaryButton(title: model.busy ? "Planning…" : "Make my day",
                              disabled: model.busy || end <= start || (fromHere && (model.location.roundedHere == nil || !inLondon))) {
                    if model.testBPlanAtRisk { confirm = true } else { make() }
                }
                .confirmReplacingTestBPlan($confirm) { make() }
            }
            .padding(.horizontal, 24)
            .padding(.top, 8)
            .padding(.bottom, 32)
        }
        .background(Theme.background)
        .sheet(isPresented: $pickMust) { MustIncludePicker(selected: $mustDo) }
        .onDisappear { if !model.showNow { model.location.stop() } }
    }

    private var startNote: String {
        if !fromHere {
            return "From \(AppConfig.startName), by the Trafalgar Square exit. Lunch is in the plan if the day spans midday."
        }
        if model.location.deniedBySettings {
            return "Location is off for ODYS. Turn it on in your phone's Settings, or start from Charing Cross."
        }
        if model.location.roundedHere == nil { return "Finding where you are…" }
        if !inLondon { return "\"Where I am\" works in London: you seem to be further away, so start from Charing Cross." }
        return "From where you are now (sent rounded to about 100 m, and not kept). Lunch is in the plan if the day spans midday."
    }

    /// Journey round 2: the moments are all in London, so "Where I am" means within about 25 km of Charing Cross.
    private var inLondon: Bool { (model.location.metres(to: AppConfig.start) ?? .infinity) < 25_000 }

    /// D123: "Where I am" asks for location the first time (ODYS's reason is in the permission text).
    private func chooseHere() {
        fromHere = true
        if model.location.usable { model.location.start() } else { model.location.turnOn() }
    }

    private func make() {
        Task {
            await model.makePlan(date: date, start: start, end: end, stops: stops,
                                 from: fromHere ? model.location.roundedHere : nil, mustDo: mustDo?.id)
            if model.errorMessage == nil { onDone?() }
        }
    }

    private var tomorrow: Date { Calendar.current.date(byAdding: .day, value: 1, to: .now) ?? .now }

    private func isSameDay(_ a: Date, _ b: Date) -> Bool { Calendar.current.isDate(a, inSameDayAs: b) }

    private func pick(_ day: Date) {
        date = day
        start = Dates.time(12)
        end = Dates.time(17)
    }

    /// Today: from the next half hour (at the earliest 12:00), for at least three hours, ending by 22:00.
    private func pickToday() {
        date = .now
        let soon = Date.now.addingTimeInterval(15 * 60)
        let half = Calendar.current.date(bySetting: .second, value: 0, of: soon) ?? soon
        let minute = Calendar.current.component(.minute, from: half)
        let rounded = Calendar.current.date(byAdding: .minute, value: (30 - minute % 30) % 30, to: half) ?? half
        start = max(Dates.time(12), rounded)
        end = min(max(Dates.time(17), start.addingTimeInterval(3 * 3600)), Dates.time(22))
    }
}

/// m176: "Must include": one of the checked moments, by name. Optional; the planner builds the day around it.
struct MustIncludePicker: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @Binding var selected: MomentSummary?
    @State private var all: [MomentSummary] = []
    @State private var query = ""
    @State private var loading = true

    var body: some View {
        NavigationStack {
            List {
                if loading {
                    HStack(spacing: 10) { ProgressView(); Text("Loading places…").foregroundStyle(Theme.muted) }
                }
                Button("Anything (no must-include)") { selected = nil; dismiss() }
                    .foregroundStyle(Theme.accent)
                ForEach(shown) { m in
                    Button {
                        selected = m
                        dismiss()
                    } label: {
                        HStack {
                            Text(m.title).foregroundStyle(Theme.ink)
                            Spacer()
                            if selected?.id == m.id { Image(systemName: "checkmark").foregroundStyle(Theme.accent) }
                        }
                    }
                }
            }
            .scrollContentBackground(.hidden)
            .background(Theme.background)
            .searchable(text: $query, prompt: "Search places")
            .serifTitle("Must include")
            .toolbar { ToolbarItem(placement: .topBarLeading) { Button("Cancel") { dismiss() } } }
            .task {
                if let list = try? await model.client.moments() {
                    all = list.filter { $0.status == "ready" }.sorted { $0.title < $1.title }
                }
                loading = false
            }
        }
    }

    private var shown: [MomentSummary] {
        query.isEmpty ? all : all.filter { $0.title.localizedCaseInsensitiveContains(query) }
    }
}

/// One row of a grouped card: a label on the left, its value or control on the right.
struct FormRow<Content: View>: View {
    let label: String
    var last = false
    @ViewBuilder let content: Content

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text(label).foregroundStyle(Theme.ink)
                Spacer(minLength: 12)
                content
            }
            .padding(.horizontal, 18)
            .frame(minHeight: 56)
            if !last { Rectangle().fill(Theme.hairline).frame(height: 1) }
        }
    }
}

/// A small round icon button (− and + for the number of stops).
struct RoundIcon: View {
    let name: String
    var disabled = false
    let action: () -> Void

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            Image(systemName: name)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(disabled ? Theme.muted : Theme.ink)
                .frame(width: 34, height: 34)
                .overlay(Circle().stroke(Theme.outlineStrong, lineWidth: 1))
                .frame(minWidth: 44, minHeight: 44)
                .contentShape(Rectangle())
        }
        .buttonStyle(PressStyle())
        .disabled(disabled)
    }
}

/// Screen 9 (D119, ODYS): the day's date, how it should feel (the headline), the numbers, how the day moves, then the
/// stops as a list (or on a map), and "Start the day". Regenerate, improve and plan another day at the end.
struct PlanView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    let plan: Plan
    var forcedLayout: String?
    var forcedReveal: Double?                  // CI screenshots only: the reveal frozen part-way
    var demoScroll: String?                    // CI screenshots only: scrolled to this part
    var onHelp: () -> Void = {}
    var onData: () -> Void = {}
    var onBack: (() -> Void)?                  // D120: opened from the Trip tab's home
    @AppStorage("planLayout") private var savedLayout = "list"
    @State private var reveal: Double = 1      // D117: 0…1 through the reveal; 1 = everything shown
    @State private var showNewPlan = false
    @State private var showImprove = false
    @State private var confirmRegenerate = false
    @State private var replanning = false
    @State private var swapping: Stop?          // UX checklist (9 Oct): a long-press swap asks first, like the card

    var body: some View {
        let layout = Binding(get: { forcedLayout ?? savedLayout }, set: { savedLayout = $0 })
        let asList = layout.wrappedValue != "map"
        let fractions = RouteMath.stopFractions(plan.stops)
        ScrollViewReader { proxy in
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                if let onBack { BackLink(action: onBack) }
                TopBar(eyebrow: Dates.longDay(plan.date) ?? plan.title ?? "Your day", onHelp: onHelp, onData: onData)
                header
                if !model.reminderAsked, !plan.isBlind, shown >= 1 {
                    ReminderAsk()   // D118: asked once, right after a plan, never before
                        .transition(.opacity)
                }
                DayMoves(plan: plan, progress: phase(0.2, 0.6))
                    .opacity(phase(0.18, 0.3))
                ViewToggle(selection: layout)
                if !asList {
                    VStack(alignment: .leading, spacing: 8) {
                        PlanMap(stops: plan.stops, progress: phase(Self.route.lowerBound, Self.route.upperBound))
                            .frame(height: 260)
                            .clipShape(RoundedRectangle(cornerRadius: 22))
                        Text("Open a stop for directions in Apple Maps.")
                            .font(.footnote)
                            .foregroundStyle(Theme.muted)
                    }
                }
                stopList(fractions)
                    .id("stops")
                if let free = model.freeTime(plan), shown >= 1 {   // journey round 2: free time, said plainly
                    FreeTimeRow(from: free.from, to: free.to,
                                canAdd: (model.lastRequest?.stops ?? 6) < 6) { Task { await model.addPlace() } }
                }
                Text(model.lastRequest == nil ? "Open a stop to see how you'll arrive." : "Open a stop to see how you'll arrive, or to swap it.")
                    .font(.footnote)
                    .foregroundStyle(Theme.muted)
                PrimaryButton(title: "Start the day") { model.startDay() }   // D119: "Now", while you're out
                actions
            }
            .padding(.horizontal, 24)
            .padding(.top, 8)
            .padding(.bottom, 40)
        }
        .onAppear {
            if let demoScroll { proxy.scrollTo(demoScroll, anchor: .top) }
        }
        }
        .background(Theme.background)
        .animation(reduceMotion ? nil : Motion.fade, value: model.reminderAsked)
        .confirmationDialog("Make a new plan for this day?", isPresented: $confirmRegenerate, titleVisibility: .visible) {
            Button("Regenerate plan") { Task { await model.regenerate() } }
            Button("Keep this plan", role: .cancel) {}
        } message: {
            Text("You'll get different stops for the same times. This plan will be replaced.")
        }
        .confirmationDialog("Swap \(swapping?.title ?? "this stop") for something else?",
                            isPresented: Binding(get: { swapping != nil }, set: { if !$0 { swapping = nil } }),
                            titleVisibility: .visible, presenting: swapping) { stop in
            Button("Swap it") { Task { await model.swap(stop) } }
            Button("Keep it", role: .cancel) {}
        } message: { _ in
            Text("The other stops stay. This one won't come back in this plan.")
        }
        .sheet(isPresented: $showNewPlan) {
            NavigationStack {
                PlanFormView(onDone: { showNewPlan = false })
                    .toolbar {
                        ToolbarItem(placement: .topBarTrailing) { Button("Close") { showNewPlan = false } }
                    }
            }
            .brainFeedback()
        }
        .sheet(isPresented: $showImprove) { ImproveView().brainFeedback() }
        .replanRest(isPresented: $replanning)
        .task(id: plan.id) { await runReveal() }
    }

    /// Bloom: the headline settles first, then the numbers.
    private var header: some View {
        let settle = CGFloat(phase(0, 0.15))
        return VStack(alignment: .leading, spacing: 12) {
            Text(headline)
                .font(Theme.serif(31, relativeTo: .title))
                .foregroundStyle(Theme.ink)
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityAddTraits(.isHeader)
                .opacity(Double(settle))
                .offset(y: reduceMotion ? 0 : (1 - settle) * 14)
            PlanStats(plan: plan)
                .opacity(phase(plan.isBlind ? 0 : 0.12, 0.25))
        }
    }

    private func stopList(_ fractions: [Double]) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(Array(plan.stops.enumerated()), id: \.element.id) { item in
                stopRow(item.offset, item.element)
                    .opacity(rowShown(item.offset, fractions))   // D117: each stop as the route reaches it
                    // Swap: the old stop steps aside, the new one settles in
                    .transition(.asymmetric(insertion: .opacity.combined(with: .offset(y: 10)),
                                            removal: .opacity.combined(with: .offset(x: -28))))
            }
        }
        .animation(reduceMotion ? nil : .easeOut(duration: 0.3), value: plan.stops.map(\.id))
    }

    private func stopRow(_ i: Int, _ stop: Stop) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            if !stop.travelText.isEmpty {
                TravelLine(stop: stop)
            }
            NavigationLink(value: stop) {
                StopCard(number: i + 1, stop: stop, rated: model.rated.contains(stop.momentId),
                         swapped: model.swappedIn == stop.momentId, showWhy: !plan.isBlind)
            }
            .buttonStyle(PressStyle())
            .contextMenu {
                if stop.rateable, model.lastRequest != nil {   // Build 2: never on the Test B plan
                    Button { swapping = stop } label: {
                        Label("Swap this stop", systemImage: "arrow.triangle.2.circlepath")
                    }
                }
            }
        }
    }

    private var headline: String {
        if !plan.isBlind, let feel = plan.feelLine, !feel.isEmpty { return feel }
        return plan.title ?? "Your day"
    }

    @ViewBuilder private var actions: some View {
        VStack(spacing: 10) {
            if model.improved {
                SecondaryButton(title: "Plan this day again with your new answers", disabled: model.busy) {
                    Task { await model.replan() }
                }
            }
            if model.ratedOnce || model.improved {
                // D118: offered once a stop is rated, so it doesn't arrive as a second ask on top of the plan
                Button { showImprove = true } label: {
                    HStack(alignment: .top, spacing: 14) {
                        ArchGlyph().padding(.top, 4)
                        VStack(alignment: .leading, spacing: 4) {
                            Text(model.improved ? "Change your answers" : "Your first stop taught us something")
                                .font(Theme.title3)
                                .foregroundStyle(Theme.ink)
                            Text(model.improved ? "Your budget, pace and interests, a few more places and example days."
                                                : "Make the next day even better? About 30 seconds, then more if you like.")
                                .font(.subheadline)
                                .foregroundStyle(Theme.muted)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        Spacer(minLength: 0)
                    }
                    .multilineTextAlignment(.leading)
                    .surfaceCard()
                }
                .buttonStyle(PressStyle())
            } else {
                QuietButton("A few more questions (optional)") { showImprove = true }
            }
            if model.lastRequest != nil, plan.date == Dates.isoDay.string(from: .now) {   // decision 3
                SecondaryButton(title: "Plans changed? Re-plan the rest of today", disabled: model.busy) { replanning = true }
            }
            HStack(spacing: 10) {
                if model.lastRequest != nil {   // Build 2: the Test B plan is rated as it was chosen
                    SecondaryButton(title: "Regenerate", disabled: model.busy) { confirmRegenerate = true }
                }
                SecondaryButton(title: "Another day") {
                    model.planAnotherDay()
                    showNewPlan = true
                }
            }
        }
    }

    // ---- D117: the plan reveal, instead of a spinner (D119: the ODYS "Bloom") ------------------------------------
    // The headline settles first, then the numbers, then the day's curve draws and the stops appear as the route
    // reaches them. About 2.6 s, once per new plan (not on a swap, not when reopening the app). Quiet: no bounce.
    // With Reduce Motion everything is simply there.

    private static let revealSeconds = 2.6
    private static let route = 0.28...0.88       // the share of the reveal the route takes

    /// How far the reveal is. A plan that has just arrived is hidden from its first frame, so nothing flashes.
    private var shown: Double {
        if let f = forcedReveal { return f }
        return model.revealPlanId == plan.id && !reduceMotion ? 0 : reveal
    }

    /// 0…1 within one part of the reveal.
    private func phase(_ from: Double, _ to: Double) -> Double {
        min(1, max(0, (shown - from) / max(to - from, 0.001)))
    }

    private func rowShown(_ i: Int, _ fractions: [Double]) -> Double {
        let at = Self.route.lowerBound + (Self.route.upperBound - Self.route.lowerBound) * (i < fractions.count ? fractions[i] : 1)
        return phase(at, at + 0.06)
    }

    private func runReveal() async {
        guard forcedReveal == nil, model.revealPlanId == plan.id else { return }
        if reduceMotion {
            model.revealPlanId = nil
            reveal = 1
            return
        }
        reveal = 0
        model.revealPlanId = nil
        let start = Date.now
        while !Task.isCancelled, reveal < 1 {
            try? await Task.sleep(for: .milliseconds(30))
            reveal = min(1, Date.now.timeIntervalSince(start) / Self.revealSeconds)
        }
        reveal = 1
    }
}

/// List or Map, as two soft tabs.
struct ViewToggle: View {
    @Binding var selection: String

    var body: some View {
        HStack(spacing: 0) {
            tab("List", "list")
            tab("Map", "map")
        }
        .padding(3)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 12))
    }

    private func tab(_ title: String, _ value: String) -> some View {
        let on = (selection == "map") == (value == "map")
        return Button {
            withAnimation(Motion.select) { selection = value }
        } label: {
            Text(title)
                .font(.subheadline)
                .foregroundStyle(Theme.ink)
                .frame(maxWidth: .infinity, minHeight: 44)
                .background(on ? Theme.surfaceHigh : Color.clear, in: RoundedRectangle(cornerRadius: 9))
                .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(on ? .isSelected : [])
    }
}

/// D117: the route line drawn part-way, and where each stop sits along it.
enum RouteMath {
    /// Flat distance on the map, good enough across a day in London.
    private static func dist(_ a: CLLocationCoordinate2D, _ b: CLLocationCoordinate2D) -> Double {
        let k = cos(a.latitude * .pi / 180)
        return hypot((b.latitude - a.latitude), (b.longitude - a.longitude) * k)
    }

    /// Each point's share of the way along the line (0 for the first, 1 for the last).
    static func fractions(_ cs: [CLLocationCoordinate2D]) -> [Double] {
        guard cs.count > 1 else { return cs.map { _ in 0 } }
        var acc = [0.0]
        for i in 1..<cs.count { acc.append(acc[i - 1] + dist(cs[i - 1], cs[i])) }
        let total = max(acc.last ?? 0, 1e-9)
        return acc.map { $0 / total }
    }

    /// The same, per stop (a stop without a pin takes the one before it).
    static func stopFractions(_ stops: [Stop]) -> [Double] {
        let withPin = stops.indices.filter { stops[$0].pin != nil }
        let f = fractions(withPin.compactMap { stops[$0].pin?.coordinate })
        var out: [Double] = []
        var last = 0.0
        for i in stops.indices {
            if let j = withPin.firstIndex(of: i) { last = f[j] }
            out.append(last)
        }
        return out
    }

    /// The line from the first point to `t` of the way along (always two points, so it can be drawn).
    static func partial(_ cs: [CLLocationCoordinate2D], _ t: Double) -> [CLLocationCoordinate2D] {
        guard let first = cs.first else { return [] }
        if t >= 1 || cs.count < 2 { return cs.count < 2 ? [first, first] : cs }
        let f = fractions(cs)
        var out = [first]
        for i in 1..<cs.count {
            if f[i] <= t {
                out.append(cs[i])
            } else {
                let span = max(f[i] - f[i - 1], 1e-9)
                let u = (t - f[i - 1]) / span
                out.append(CLLocationCoordinate2D(latitude: cs[i - 1].latitude + (cs[i].latitude - cs[i - 1].latitude) * u,
                                                  longitude: cs[i - 1].longitude + (cs[i].longitude - cs[i - 1].longitude) * u))
                break
            }
        }
        return out.count < 2 ? [first, first] : out
    }

    /// The whole day in view from the start, so the map doesn't move while the line draws.
    static func camera(_ cs: [CLLocationCoordinate2D]) -> MapCameraPosition {
        guard cs.count > 1 else { return .automatic }
        let lats = cs.map(\.latitude), lons = cs.map(\.longitude)
        let center = CLLocationCoordinate2D(latitude: (lats.min()! + lats.max()!) / 2,
                                            longitude: (lons.min()! + lons.max()!) / 2)
        let span = MKCoordinateSpan(latitudeDelta: max((lats.max()! - lats.min()!) * 1.5, 0.008),
                                    longitudeDelta: max((lons.max()! - lons.min()!) * 1.5, 0.008))
        return .region(MKCoordinateRegion(center: center, span: span))
    }
}

/// Cost per person, walking between stops and the finish time (D110), then what the cost is made of and where the
/// day starts.
struct PlanStats: View {
    let plan: Plan

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            if let t = plan.totals {
                FlowRow(spacing: 18, lineSpacing: 4) {
                    Text("\(Money.text(t.costGbp)) per person")
                    Text(String(format: "%.1f km walking between stops", t.walkKm))
                    Text("Done by \(t.finish ?? plan.stops.last?.depart ?? "–")")
                }
                .font(.subheadline)
                .foregroundStyle(Theme.inkSoft)
                Text(breakdown(t) + (plan.summary?.first.map { " " + $0 + "." } ?? ""))
                    .font(.footnote)
                    .foregroundStyle(Theme.muted)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .accessibilityElement(children: .combine)
    }

    private func breakdown(_ t: Totals) -> String {
        let spend = t.spendGbp > 0 ? "\(Money.text(t.spendGbp)) food and entry" : "Free entry"
        let fare = t.transportGbp > 0 ? "\(Money.text(t.transportGbp)) Tube or bus" : "all on foot"
        return "\(spend), \(fare)."
    }
}

enum Money {
    /// £21, or £21.50
    static func text(_ gbp: Double) -> String {
        gbp.rounded() == gbp ? "£\(Int(gbp))" : String(format: "£%.2f", gbp)
    }
}

/// "How the day moves" (D119, the ODYS curve; was the day's shape, D112): one point per stop across the day, higher
/// where we expect you to enjoy it more (from the worth to you, so never in the blind comparison or the example day),
/// with each stop's word for the kind of moment it is. No numbers on the height: a picture of the day, not a score.
struct DayMoves: View {
    let plan: Plan
    var progress: Double = 1

    var body: some View {
        let personal = !plan.isBlind && plan.stops.contains { $0.worthGbp != nil }
        let top = plan.stops.compactMap(\.worthGbp).max() ?? 0
        let points = plan.stops.map { s in
            DayCurve.Point(minute: Self.minutes(s.arrive),
                           level: personal && top > 0 ? (s.worthGbp.map { max(0.22, $0 / top) } ?? 0.4) : 0.55,
                           word: s.word, time: s.arrive)
        }
        let peak = personal ? points.indices.max { points[$0].level < points[$1].level } : nil
        VStack(alignment: .leading, spacing: 6) {
            Text("How the day moves")
                .font(.subheadline)
                .foregroundStyle(Theme.muted)
            Text(personal ? "Higher means we think you'll enjoy it more. Each word is the kind of moment a stop is."
                          : "Each word is the kind of moment a stop is.")
                .font(.footnote)
                .foregroundStyle(Theme.inkTertiary)
                .fixedSize(horizontal: false, vertical: true)
            DayCurve(points: points, progress: progress, peak: peak)
                .padding(.top, 8)
        }
        .padding(16)
        .background(Theme.deep, in: RoundedRectangle(cornerRadius: 22))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("How the day moves: " + points.map { "\($0.time), \($0.word)" }.joined(separator: "; "))
    }

    static func minutes(_ hhmm: String) -> Double {
        let parts = hhmm.split(separator: ":").compactMap { Double($0) }
        return parts.count == 2 ? parts[0] * 60 + parts[1] : 0
    }
}

/// The curve itself: a smooth line through the stops with a soft amber fill under it, a dot at each stop and its
/// word and time underneath. `progress` draws it from the left; the peak's dot pulses once when it's drawn.
struct DayCurve: View {
    struct Point {
        let minute: Double
        let level: Double
        let word: String
        let time: String
    }

    let points: [Point]
    var progress: Double = 1
    var peak: Int?
    @State private var pulse = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.dynamicTypeSize) private var typeSize
    @ScaledMetric(relativeTo: .callout) private var rowHeight: CGFloat = 40   // journey round 2: grows with the text

    private static let curveHeight: CGFloat = 104

    var body: some View {
        // journey round 2: with large text, each stop's word gets its own row, so labels never overlap
        let rows = typeSize.isAccessibilitySize ? max(points.count, 1) : (points.count >= 4 ? 2 : 1)
        GeometryReader { g in
            let w = g.size.width
            let lo = (points.map(\.minute).min() ?? 600) - 35
            let hi = (points.map(\.minute).max() ?? 1020) + 35
            let x: (Double) -> CGFloat = { m in 8 + CGFloat((m - lo) / max(hi - lo, 1)) * (w - 16) }
            let y: (Double) -> CGFloat = { l in 90 - CGFloat(l) * 70 }
            let pts = [CGPoint(x: 0, y: 92)] + points.map { CGPoint(x: x($0.minute), y: y($0.level)) } + [CGPoint(x: w, y: 92)]
            let line = Self.smooth(pts)
            ZStack(alignment: .topLeading) {
                Path { p in
                    p.move(to: CGPoint(x: 0, y: 96))
                    p.addLine(to: CGPoint(x: w, y: 96))
                }
                .stroke(Theme.ink.opacity(0.1), lineWidth: 1)
                Self.area(line, w)
                    .fill(LinearGradient(colors: [Theme.accent.opacity(0.4), Theme.accent.opacity(0)],
                                         startPoint: .top, endPoint: .bottom))
                    .opacity(progress)
                line.trim(from: 0, to: progress)
                    .stroke(Theme.accent, style: StrokeStyle(lineWidth: 2.5, lineCap: .round, lineJoin: .round))
                ForEach(points.indices, id: \.self) { i in
                    let px = x(points[i].minute)
                    let reached = progress >= Double(px / max(w, 1)) - 0.01
                    Circle()
                        .fill(Theme.accent)
                        .frame(width: 9, height: 9)
                        .background(Circle().fill(Theme.deep).frame(width: 15, height: 15))
                        .scaleEffect(pulse && i == peak ? 1.7 : 1)
                        .position(x: px, y: y(points[i].level))
                        .opacity(reached ? 1 : 0)
                    VStack(spacing: 1) {
                        Text(points[i].word)
                            .font(Theme.italic(16, relativeTo: .callout))
                            .foregroundStyle(Theme.ink)
                        Text(points[i].time)
                            .font(.caption)
                            .foregroundStyle(Theme.muted)
                    }
                    .fixedSize()
                    .position(x: min(max(px, 34), w - 34),
                              y: Self.curveHeight + 18 + CGFloat(rows == points.count && rows > 2 ? i : (rows == 2 ? i % 2 : 0)) * rowHeight)
                    .opacity(reached ? 1 : 0)
                }
            }
        }
        .frame(height: Self.curveHeight + CGFloat(rows) * rowHeight + 2)
        .onChange(of: progress >= 1, initial: true) { _, done in
            guard done, peak != nil, !reduceMotion, !AppConfig.demo else { return }
            Task {
                withAnimation(.easeOut(duration: 0.3)) { pulse = true }
                try? await Task.sleep(for: .milliseconds(320))
                withAnimation(.easeIn(duration: 0.3)) { pulse = false }
            }
        }
    }

    /// A smooth line through the points: each segment a cubic with flat handles half-way along.
    static func smooth(_ pts: [CGPoint]) -> Path {
        var p = Path()
        guard let first = pts.first else { return p }
        p.move(to: first)
        for i in 1..<max(pts.count, 1) where i < pts.count {
            let a = pts[i - 1], b = pts[i]
            let dx = (b.x - a.x) / 2
            p.addCurve(to: b, control1: CGPoint(x: a.x + dx, y: a.y), control2: CGPoint(x: b.x - dx, y: b.y))
        }
        return p
    }

    static func area(_ line: Path, _ w: CGFloat) -> Path {
        var a = line
        a.addLine(to: CGPoint(x: w, y: 96))
        a.addLine(to: CGPoint(x: 0, y: 96))
        a.closeSubpath()
        return a
    }
}

/// The day on a map (kept from D112: a real map, not a drawing), dark like the app, with numbered amber pins.
struct PlanMap: View {
    let stops: [Stop]
    var progress: Double = 1       // D117: how much of the route line is drawn; a stop's pin shows once it's reached

    private struct Pin: Identifiable {
        let id: Int
        let title: String
        let coordinate: CLLocationCoordinate2D
    }

    private var pins: [Pin] {
        stops.indices.compactMap { i in
            guard let p = stops[i].pin else { return nil }
            return Pin(id: i + 1, title: stops[i].title, coordinate: p.coordinate)
        }
    }

    var body: some View {
        let all = pins
        let coords = all.map(\.coordinate)
        let along = RouteMath.fractions(coords)
        let reached = all.indices.filter { along[$0] <= progress + 1e-6 }.map { all[$0] }
        Map(initialPosition: progress < 1 ? RouteMath.camera(coords) : .automatic) {
            MapPolyline(coordinates: RouteMath.partial(coords, progress))
                .stroke(Theme.accentFill, lineWidth: 3)
            ForEach(reached) { pin in
                Annotation(pin.title, coordinate: pin.coordinate) {
                    Text("\(pin.id)")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(Theme.accent)
                        .frame(width: 24, height: 24)
                        .background(Circle().fill(Theme.background))
                        .overlay(Circle().stroke(Theme.accent, lineWidth: 2.5))
                }
            }
        }
        .mapStyle(.standard(pointsOfInterest: .excludingAll))
        .accessibilityLabel("Map of the day's \(pins.count) stops")
    }
}

/// How you get to a stop, between the cards.
struct TravelLine: View {
    let stop: Stop

    var body: some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Image(systemName: stop.travelMode == "walk" ? "figure.walk" : "tram.fill")
                .foregroundStyle(Theme.muted)
            Text(stop.travelText)
                .foregroundStyle(Theme.muted)
                .fixedSize(horizontal: false, vertical: true)
        }
        .font(.footnote)
        .padding(.leading, 6)
    }
}

/// One stop on the day (D119): its photo or field, "13:30 · Awe", the title, the reason in plain words (D115), and
/// the worth to you in amber (D88, D118).
struct StopCard: View {
    let number: Int
    let stop: Stop
    var rated = false
    var swapped = false
    var showWhy = true             // D115: off in the blind Test B comparison

    var body: some View {
        HStack(alignment: .top, spacing: 14) {
            Color.clear
                .frame(width: 78)
                .frame(minHeight: 96, maxHeight: .infinity)
                .overlay { MomentImage(momentId: stop.momentId, feel: stop.feelWord) }
                .overlay(alignment: .topLeading) {
                    Text("\(number)")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(Theme.accent)
                        .frame(width: 22, height: 22)
                        .background(Circle().fill(Theme.background.opacity(0.85)))
                        .padding(6)
                }
                .clipShape(RoundedRectangle(cornerRadius: 14))
            VStack(alignment: .leading, spacing: 5) {
                Text("\(stop.arrive)–\(stop.depart) · \(stop.word)")
                    .font(.subheadline.monospacedDigit())
                    .foregroundStyle(Theme.muted)
                Text(stop.title)
                    .font(Theme.title3)
                    .foregroundStyle(Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                if showWhy, let why = stop.reasons?.first?.you {
                    Text(why)
                        .font(.subheadline)
                        .foregroundStyle(Theme.inkSoft)
                        .fixedSize(horizontal: false, vertical: true)
                }
                if showWhy, let worth = stop.worthLine {
                    Text(worth).font(.subheadline).foregroundStyle(Theme.accent)
                }
                let badges = [swapped ? "Swapped in" : nil, stop.familiar ? "A place you loved" : nil,
                              rated ? "Rated" : nil].compactMap { $0 }
                if !badges.isEmpty {
                    Text(badges.joined(separator: " · "))
                        .font(Theme.italic(15, relativeTo: .subheadline))
                        .foregroundStyle(Theme.accent)
                }
            }
            .multilineTextAlignment(.leading)
            .padding(.vertical, 2)
            Spacer(minLength: 0)
        }
        .fixedSize(horizontal: false, vertical: true)
        .padding(12)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 20))
        .contentShape(RoundedRectangle(cornerRadius: 20))
        .accessibilityElement(children: .combine)
        .accessibilityHint("Opens the stop")
    }
}

extension Stop {
    /// Rating opens at the planned arrival (D110: only after the visit). Nil when the plan has no date.
    func ratingOpens(on day: String?) -> Date? {
        guard let day else { return nil }
        return Dates.stamp.date(from: "\(day) \(arrive)")
    }
}

/// The moment card, framed as a picture and its details, for the example day (screen 2, D115) and its screenshot.
struct MomentCardContent: View {
    let stop: Stop
    var basis: Basis?
    var showWhy = true

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            MomentHero(stop: stop, height: 260, rounded: true)
            MomentCardBody(stop: stop, basis: basis, showWhy: showWhy)
        }
    }
}

/// The big picture at the top of a moment card: the card's photo (openly licensed, its credit underneath, until
/// Abram's own replace them), or for a card without one the satellite view of the place: real, not invented. The time,
/// the kind of moment and the title sit at its foot. Drift (16 s) while it's open.
struct MomentHero: View {
    let stop: Stop
    var height: CGFloat = 380
    var rounded = false
    var drift = false

    var body: some View {
        let found = CardPhotos.photo(for: stop.momentId)
        VStack(alignment: .leading, spacing: 8) {
            Color.clear
                .frame(height: height)
                .overlay {
                    if found != nil {
                        MomentImage(momentId: stop.momentId, feel: stop.feelWord, drift: drift)
                    } else if let pin = stop.pin {
                        Map(initialPosition: .camera(MapCamera(centerCoordinate: pin.coordinate, distance: 900,
                                                               heading: 0, pitch: 50))) {
                            Marker(stop.title, coordinate: pin.coordinate).tint(Theme.accentFill)
                        }
                        .mapStyle(.imagery(elevation: .realistic))
                        .allowsHitTesting(false)
                    } else {
                        Field(feel: stop.feelWord)
                    }
                }
                .overlay(alignment: .top) {
                    if !rounded {   // so the back button reads on a bright photo
                        LinearGradient(colors: [.black.opacity(0.5), .clear], startPoint: .top, endPoint: .bottom)
                            .frame(height: 130)
                            .allowsHitTesting(false)
                    }
                }
                .overlay(alignment: .bottomLeading) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("\(stop.arrive)–\(stop.depart) · \(stop.word)")
                            .font(.subheadline.monospacedDigit())
                            .foregroundStyle(Theme.amberDeep)
                        Text(stop.title)
                            .font(rounded ? Theme.title : Theme.h1)
                            .foregroundStyle(Theme.ink)
                            .fixedSize(horizontal: false, vertical: true)
                            .accessibilityAddTraits(.isHeader)
                    }
                    .padding(rounded ? 18 : 24)
                    .padding(.top, 48)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(LinearGradient(stops: [.init(color: .clear, location: 0),
                                                       .init(color: Theme.background.opacity(0.7), location: 0.3),
                                                       .init(color: Theme.background.opacity(rounded ? 0.92 : 1), location: 1)],
                                               startPoint: .top, endPoint: .bottom))
                    .allowsHitTesting(false)
                }
                .clipShape(RoundedRectangle(cornerRadius: rounded ? 22 : 0))
            if let photo = found?.0 {
                // the credit the licence asks for; it opens the photo's page on Wikimedia Commons
                Link(photo.credit, destination: photo.source)
                    .font(.caption)
                    .foregroundStyle(Theme.muted)
                    .padding(.horizontal, rounded ? 0 : 24)
            }
        }
    }
}

/// Everything under the picture (D112, D115, D119): why it was picked, the way in, the shot card, then the details.
/// All of it comes from the verified card or the plan.
struct MomentCardBody: View {
    let stop: Stop
    var basis: Basis?
    var showWhy = true             // D115: never in the blind Test B comparison or the example day
    @State private var showShot = false

    /// Decision 4: "Hours, prices and the way in last checked on 27 Sep, from the place's own site."
    private var checkedText: String {
        guard let iso = stop.checked, let day = Dates.isoDay.date(from: iso) else { return "" }
        return "Hours, prices and the way in last checked on \(Dates.dayMonth.string(from: day)), from the place's own site."
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 26) {
            if stop.familiar {
                Label("A place you loved", systemImage: "heart.fill")
                    .font(.subheadline)
                    .foregroundStyle(Theme.accent)
            }
            let reasons = showWhy ? (stop.reasons ?? []) : []
            if !reasons.isEmpty || (showWhy && stop.worthLine != nil) {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Why we picked this for you").font(.subheadline).foregroundStyle(Theme.muted)
                    ForEach(reasons, id: \.you) { r in
                        Text(r.you)
                            .font(Theme.serif(22, relativeTo: .title3))
                            .foregroundStyle(Theme.ink)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    if let basis, !reasons.isEmpty {
                        Text(basis.soFar).font(.footnote).foregroundStyle(Theme.muted)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    if let worth = stop.worthLine {
                        Text(worth).foregroundStyle(Theme.accent).padding(.top, 4)
                        // D118: plainly a first estimate
                        Text("A first estimate from what you've told us so far.")
                            .font(.footnote)
                            .foregroundStyle(Theme.muted)
                    }
                }
            }
            if !stop.travelText.isEmpty || !(stop.approachSteps ?? []).isEmpty || !stop.approach.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    Text("The way in").font(.subheadline).foregroundStyle(Theme.muted)
                    if !stop.travelText.isEmpty {
                        Text(stop.travelText)
                            .font(.subheadline)
                            .foregroundStyle(Theme.inkSoft)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    if let steps = stop.approachSteps, !steps.isEmpty {
                        WayIn(steps: steps, reveal: stop.reveal ?? false)
                            .padding(.top, 6)
                    } else if !stop.approach.isEmpty {
                        Text(stop.approach).foregroundStyle(Theme.ink).fixedSize(horizontal: false, vertical: true)
                    }
                }
            }
            if let card = stop.card, let shot = card.shotCard {
                Button { showShot = true } label: {
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Label("Shot card", systemImage: "camera").font(.subheadline).foregroundStyle(Theme.muted)
                            Spacer()
                            Image(systemName: "chevron.right").font(.footnote).foregroundStyle(Theme.muted)
                        }
                        Text(shot.standAt?.note ?? shot.frame ?? "Where to stand for the best photo.")
                            .foregroundStyle(Theme.ink)
                            .multilineTextAlignment(.leading)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .surfaceCard(padding: 18)
                }
                .buttonStyle(PressStyle())
            }
            DetailRows(rows: [
                ("Best time and light", bestText),
                ("What happens", stop.what),
                ("Opening hours", stop.hours ?? ""),     // m176: checked on the card's own source
                ("Book ahead", stop.bookAhead ?? ""),   // journey audit: Horizon 22, the Transport Museum, karting
                ("Checked", checkedText),               // decision 4: when the card's facts were last checked
                ("Queue", (stop.queueMin ?? 0) > 0 ? "Allow about \(Int(stop.queueMin ?? 0)) min to queue." : ""),
                ("Cost", stop.costText.replacingOccurrences(of: "Cost: ", with: "").capitalizedFirst),
                ("If it rains", stop.rainSwap),
            ])
        }
        .sheet(isPresented: $showShot) {
            if let card = stop.card {
                NavigationStack {
                    ScrollView { ShotCardView(card: card).padding(24) }
                        .background(Theme.background)
                        .serifTitle("Shot card")
                        .toolbar {
                            ToolbarItem(placement: .topBarTrailing) { Button("Close") { showShot = false } }
                        }
                }
            }
        }
    }

    private var bestText: String {
        let light = stop.bestLight ?? ""
        let window = stop.bestWindow ?? ""
        if light.isEmpty { return "" }
        let sentence = light.hasSuffix(".") ? light : light + "."
        return window.isEmpty ? sentence : "\(sentence) On your day: \(window)."
    }
}

/// "The way in" (D119): the approach as a path you can tap along: from where, the way in, where you arrive. The Way-in
/// motion (450 ms): the light walks down the path to the step you tap, and glows at "The reveal".
struct WayIn: View {
    let steps: [ApproachStep]
    let reveal: Bool
    @State private var current = 0
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            ForEach(steps.indices, id: \.self) { i in
                let last = i == steps.count - 1
                let done = i < current
                let on = i == current
                let isReveal = last && reveal
                Button {
                    withAnimation(reduceMotion ? nil : Motion.wayIn) { current = i }
                } label: {
                    HStack(alignment: .top, spacing: 14) {
                        VStack(spacing: 0) {
                            Circle()
                                .fill(on || done ? Theme.accent : Color.clear)
                                .overlay(Circle().strokeBorder(on || done ? Theme.accent : Color(hex: 0x4A4E57), lineWidth: 2))
                                .frame(width: on ? 16 : 12, height: on ? 16 : 12)
                                .shadow(color: isReveal && on ? Theme.accent.opacity(0.9) : .clear, radius: 8)
                                .frame(width: 22, height: 22)
                            if !last {
                                Rectangle()
                                    .fill(done ? Theme.accent : Theme.line)
                                    .frame(width: 2)
                                    .frame(maxHeight: .infinity)
                            }
                        }
                        VStack(alignment: .leading, spacing: 4) {
                            Text(steps[i].label)
                                .font(.footnote)
                                .foregroundStyle(Theme.muted)
                            Text(steps[i].text)
                                .foregroundStyle(on ? Theme.ink : (done ? Theme.inkTertiary : Theme.inkSoft))
                                .multilineTextAlignment(.leading)
                                .fixedSize(horizontal: false, vertical: true)
                            if isReveal {
                                Eyebrow("The reveal", color: Theme.accent)
                            }
                        }
                        .padding(.bottom, last ? 0 : 18)
                        Spacer(minLength: 0)
                    }
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityLabel("\(steps[i].label): \(steps[i].text)" + (isReveal ? ". The reveal." : ""))
            }
        }
    }
}

/// The shot card in full, opened from a stop that has one.
struct ShotCardView: View {
    let card: Card

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            PageTitle(text: card.title, font: Theme.title2)
            if let shot = card.shotCard {
                if let lat = shot.standAt?.lat, let lon = shot.standAt?.lon {
                    let here = CLLocationCoordinate2D(latitude: lat, longitude: lon)
                    Map(initialPosition: .region(MKCoordinateRegion(center: here, latitudinalMeters: 500,
                                                                    longitudinalMeters: 500))) {
                        Marker("Stand here", coordinate: here).tint(Theme.accentFill)
                    }
                    .frame(height: 170)
                    .clipShape(RoundedRectangle(cornerRadius: 18))
                    .allowsHitTesting(false)
                }
                DetailRows(rows: [("Where to stand", shot.standAt?.note ?? ""), ("Which way to face", shot.face ?? ""),
                                  ("What to frame", shot.frame ?? ""), ("When", shot.when ?? ""),
                                  ("What spoils it", shot.avoid ?? "")])
            }
        }
    }
}

/// Screen 10: the moment card, full-bleed, then directions, swapping and (after the visit) rating and sharing.
struct StopView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL
    let stop: Stop
    var demoScroll: String?            // CI screenshots only: scrolled to this part ("body")
    @State private var showRating = false
    @State private var confirmSwap = false
    @State private var confirmRegenerate = false
    @State private var sharing = false
    @State private var reporting = false

    var body: some View {
        let done = model.rated.contains(stop.momentId)
        let opens = stop.ratingOpens(on: model.plan?.date)
        let canRate = stop.rateable && !done && (opens == nil || opens! <= .now)
        ScrollViewReader { proxy in
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                MomentHero(stop: stop, drift: true)
                VStack(alignment: .leading, spacing: 26) {
                    MomentCardBody(stop: stop, basis: model.plan?.basis, showWhy: !(model.plan?.isBlind ?? false))
                        .id("body")
                    VStack(spacing: 10) {
                        if canRate {
                            PrimaryButton(title: "Been here? How did it feel?") { showRating = true }
                        }
                        if let pin = stop.pin {
                            // journey audit: by Tube or bus when the plan's leg is, else walking
                            let mode = stop.travelMode == "transit" ? "r" : "w"
                            let maps = URL(string: "http://maps.apple.com/?daddr=\(pin.lat),\(pin.lon)&dirflg=\(mode)")!
                            if canRate {
                                SecondaryButton(title: "Directions in Apple Maps") { openURL(maps) }
                            } else {
                                PrimaryButton(title: "Directions in Apple Maps") { openURL(maps) }
                            }
                        }
                        if stop.rateable, model.lastRequest != nil {   // Build 2: not on the Test B plan
                            HStack(spacing: 10) {
                                SecondaryButton(title: "Swap this stop", disabled: model.busy) { confirmSwap = true }
                                SecondaryButton(title: "Regenerate", disabled: model.busy) { confirmRegenerate = true }
                            }
                        }
                    }
                    if stop.rateable {
                        rating(done: done, opens: opens)
                    }
                    // UX checklist (9 Oct): a wrong price, hours or route is reported where it's seen, to a person
                    QuietButton("Something wrong with this place? Tell us") { reporting = true }
                        .frame(maxWidth: .infinity)
                }
                .padding(.horizontal, 24)
                .padding(.top, 14)
                .padding(.bottom, 40)
            }
        }
        .ignoresSafeArea(edges: .top)
        .onAppear {
            if let demoScroll { proxy.scrollTo(demoScroll, anchor: .top) }
        }
        }
        .background(Theme.background)
        .navigationTitle("")                       // the title is on the picture
        .navigationBarTitleDisplayMode(.inline)
        .toolbar(.visible, for: .navigationBar)
        .confirmationDialog("Swap \(stop.title) for something else?", isPresented: $confirmSwap,
                            titleVisibility: .visible) {
            Button("Swap it") {
                Task {
                    await model.swap(stop)
                    if model.errorMessage == nil { dismiss() }
                }
            }
            Button("Keep it", role: .cancel) {}
        } message: {
            Text("The other stops stay. This one won't come back in this plan.")
        }
        .confirmationDialog("Make a new plan for this day?", isPresented: $confirmRegenerate, titleVisibility: .visible) {
            Button("Regenerate plan") {
                Task {
                    await model.regenerate()
                    if model.errorMessage == nil { dismiss() }
                }
            }
            Button("Keep this plan", role: .cancel) {}
        } message: {
            Text("You'll get different stops for the same times. This plan will be replaced.")
        }
        .sheet(isPresented: $showRating) { RatingView(stop: stop).brainFeedback() }
        .sheet(isPresented: $reporting) { SafetyView(prefill: "About \(stop.title): ").brainFeedback() }
        .navigationDestination(isPresented: $sharing) {
            SharePreview(stop: stop, rating: model.myRatings[stop.momentId] ?? 5)
        }
    }

    /// Only after the visit (D110): before the planned arrival, say when the rating opens.
    @ViewBuilder private func rating(done: Bool, opens: Date?) -> some View {
        if let opens, opens > .now, !done {
            Text("You can rate this stop after your visit, from \(stop.arrive) on \(Dates.dayName.string(from: opens)).")
                .font(.subheadline)
                .foregroundStyle(Theme.muted)
                .fixedSize(horizontal: false, vertical: true)
        } else if done {
            VStack(alignment: .leading, spacing: 12) {
                HStack(spacing: 10) {
                    ArchGlyph()
                    Text("Rated. Thank you.").foregroundStyle(Theme.inkSoft)
                }
                if model.myRatings[stop.momentId] != nil, !stop.isGeneric {
                    // D114: for any rating, so rating high never unlocks anything (Build 2: a generic stop has no card)
                    SecondaryButton(title: "Share this moment", icon: "square.and.arrow.up") { sharing = true }
                }
            }
        }
    }
}

extension String {
    /// "free" → "Free", for lines shown under their own label.
    var capitalizedFirst: String { prefix(1).uppercased() + String(dropFirst()) }
}

/// D118: asked once, right after a plan is made. "Yes" brings iOS's own permission prompt (only then, D117); the
/// reminders are local, one after each stop. "No thanks" is the same size and style as "Yes" (no dark patterns).
struct ReminderAsk: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top, spacing: 12) {
                Image(systemName: "bell").foregroundStyle(Theme.accent).padding(.top, 3)
                Text("A nudge to rate each stop after you leave?")
                    .font(Theme.title3)
                    .foregroundStyle(Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Text("One tap each, on the day. Your ratings are what make the next plan better. Set on your phone; nothing else is sent.")
                .font(.subheadline)
                .foregroundStyle(Theme.muted)
                .fixedSize(horizontal: false, vertical: true)
            HStack(spacing: 10) {
                SecondaryButton(title: "Yes, nudge me") { Task { await model.answerReminders(true) } }
                SecondaryButton(title: "No thanks") { Task { await model.answerReminders(false) } }
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
        .overlay(RoundedRectangle(cornerRadius: 18).stroke(Theme.outline, lineWidth: 1))
    }
}

/// Journey round 2: a day that ends early says so, with one tap to add a place.
struct FreeTimeRow: View {
    @Environment(AppModel.self) private var model
    let from: String
    let to: String
    let canAdd: Bool
    let add: () -> Void

    var body: some View {
        HStack(alignment: .center, spacing: 12) {
            VStack(alignment: .leading, spacing: 2) {
                Text("Free from \(from) until \(to)").foregroundStyle(Theme.ink)
                Text("Rest, wander, or add one more place.")
                    .font(.footnote)
                    .foregroundStyle(Theme.muted)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 8)
            if canAdd {
                QuietButton(model.busy ? "Adding…" : "Add a place", color: Theme.accent, action: add)
                    .disabled(model.busy)
            }
        }
        .surfaceCard(padding: 16)
    }
}

/// Decision 3 (8 Oct): "Re-plan the rest of today": why, then the rest of the day from about ten minutes from now.
struct ReplanRest: ViewModifier {
    @Environment(AppModel.self) private var model
    @Binding var isPresented: Bool

    func body(content: Content) -> some View {
        content.confirmationDialog("Re-plan the rest of today?", isPresented: $isPresented, titleVisibility: .visible) {
            Button("It's raining") { go("rain") }
            Button("A place is closed or too busy") { go("closed") }
            Button("I'm tired: fewer stops") { go("tired") }
            Button("Something else") { go("other") }
            Button("Keep my day", role: .cancel) {}
        } message: {
            Text("From where you are, starting in about ten minutes, without the places you've done.")
        }
    }

    private func go(_ reason: String) { Task { await model.replanRest(reason) } }
}

extension View {
    func replanRest(isPresented: Binding<Bool>) -> some View { modifier(ReplanRest(isPresented: isPresented)) }
}
