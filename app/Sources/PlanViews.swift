import Charts
import MapKit
import SwiftUI

/// Home: the current plan, or the form to make one. Help & safety and your data are always one tap away.
struct HomeView: View {
    @State private var showSafety = false
    @State private var showSettings = false
    @Environment(AppModel.self) private var model
    var layout: String?          // CI screenshots only: "list"

    var body: some View {
        NavigationStack {
            Group {
                if let plan = model.plan {
                    PlanView(plan: plan, forcedLayout: layout)
                } else {
                    PlanFormView()
                }
            }
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button { showSafety = true } label: {
                        Label("Help & safety", systemImage: "exclamationmark.shield")
                    }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button { showSettings = true } label: {
                        Label("Your data", systemImage: "gearshape")
                    }
                }
            }
            .sheet(isPresented: $showSafety) { SafetyView() }
            .sheet(isPresented: $showSettings) { SettingsView() }
        }
    }
}

/// Screen 8. Build 1 plans from Charing Cross (the Test B start, D104), on a date and between times you choose.
struct PlanFormView: View {
    @Environment(AppModel.self) private var model
    var onDone: (() -> Void)?
    @State private var date = Dates.nextSaturday()
    @State private var start = Dates.time(12)
    @State private var end = Dates.time(17)
    @State private var stops = 4

    var body: some View {
        Form {
            Section {
                Text("Your day starts at \(AppConfig.startName), by the Trafalgar Square exit.")
            } header: {
                Text("Where")
            }
            Section("When") {
                DatePicker("Day", selection: $date, in: Calendar.current.startOfDay(for: .now)..., displayedComponents: .date)
                DatePicker("Start", selection: $start, displayedComponents: .hourAndMinute)
                DatePicker("Finish", selection: $end, displayedComponents: .hourAndMinute)
            }
            Section {
                Stepper("\(stops) stops", value: $stops, in: 3...5)
            } footer: {
                Text("Including lunch when the day spans midday.")
            }
            Section {
                PrimaryButton(title: model.busy ? "Planning…" : "Make my plan", disabled: model.busy || end <= start) {
                    Task {
                        await model.makePlan(date: date, start: start, end: end, stops: stops)
                        if model.errorMessage == nil { onDone?() }
                    }
                }
                .listRowInsets(EdgeInsets())
                .listRowBackground(Color.clear)
            }
        }
        .themedList()
        .serifTitle("Plan a day")
    }
}

/// Screen 9: the summary first and prominent (D110, D112), the day's shape, then the map and the stops (the
/// numbers match), or the stops as a list. Regenerate, improve and plan another day at the end.
struct PlanView: View {
    @Environment(AppModel.self) private var model
    let plan: Plan
    var forcedLayout: String?
    @AppStorage("planLayout") private var savedLayout = "map"
    @State private var showNewPlan = false
    @State private var showImprove = false
    @State private var confirmRegenerate = false

    var body: some View {
        let layout = Binding(get: { forcedLayout ?? savedLayout }, set: { savedLayout = $0 })
        let asList = layout.wrappedValue == "list"
        List {
            Section {
                PlanSummaryCard(plan: plan)
                    .listRowInsets(EdgeInsets())
                    .listRowBackground(Color.clear)
            } header: {
                Text(plan.title ?? "Your day")
                    .font(Theme.title2)
                    .foregroundStyle(Theme.ink)
                    .textCase(nil)
            }
            Section {
                DayShapeChart(stops: plan.stops, personal: true)
                    .listRowBackground(Theme.surface)
                Picker("Show", selection: layout) {
                    Text("Map").tag("map")
                    Text("List").tag("list")
                }
                .pickerStyle(.segmented)
                .listRowBackground(Theme.surface)
            }
            if !asList {
                Section {
                    PlanMap(stops: plan.stops)
                        .frame(height: 240)
                        .listRowInsets(EdgeInsets())
                }
            }
            Section {
                ForEach(plan.stops.indices, id: \.self) { i in
                    let stop = plan.stops[i]
                    if asList, !stop.travelText.isEmpty {
                        Label(stop.travelText, systemImage: stop.travelMode == "walk" ? "figure.walk" : "tram")
                            .font(.footnote)
                            .foregroundStyle(Theme.inkSoft)
                            .listRowBackground(Theme.background)
                    }
                    NavigationLink(value: stop) {
                        StopRow(number: i + 1, stop: stop, showTravel: !asList,
                                rated: model.rated.contains(stop.momentId), swapped: model.swappedIn == stop.momentId)
                    }
                    .listRowBackground(Theme.surface)
                    .swipeActions {
                        if stop.rateable {
                            Button("Swap") { Task { await model.swap(stop) } }
                                .tint(Theme.accent)
                        }
                    }
                }
            } header: {
                Text("Stops")
            } footer: {
                Text("Open a stop to swap it for something else.")
            }
            Section {
                Button {
                    confirmRegenerate = true
                } label: {
                    Label("Regenerate plan", systemImage: "arrow.clockwise")
                }
                .disabled(model.busy)
                .listRowBackground(Theme.surface)
                if model.improved {
                    Button("Plan this day again with your new answers") { Task { await model.replan() } }
                        .disabled(model.busy)
                        .listRowBackground(Theme.surface)
                }
                Button {
                    showImprove = true
                } label: {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(model.improved ? "Change your answers" : "Improve future plans").font(.headline)
                        Text("Optional, about 2 minutes: a few more places and example days, your budget, pace and interests.")
                            .font(.footnote)
                            .foregroundStyle(Theme.inkSoft)
                    }
                }
                .listRowBackground(Theme.surface)
                Button("Plan another day") {
                    model.planAnotherDay()
                    showNewPlan = true
                }
                .listRowBackground(Theme.surface)
            }
        }
        .themedList()
        .serifTitle("Your day")
        .navigationDestination(for: Stop.self) { stop in
            StopView(stop: stop)
        }
        .confirmationDialog("Make a new plan for this day?", isPresented: $confirmRegenerate, titleVisibility: .visible) {
            Button("Regenerate plan") { Task { await model.regenerate() } }
            Button("Keep this plan", role: .cancel) {}
        } message: {
            Text("You'll get different stops for the same times. This plan will be replaced.")
        }
        .sheet(isPresented: $showNewPlan) {
            NavigationStack {
                PlanFormView(onDone: { showNewPlan = false })
            }
        }
        .sheet(isPresented: $showImprove) { ImproveView() }
    }
}

/// Cost per person, walking between stops and the finish time, large and first (D110, D112).
struct PlanSummaryCard: View {
    let plan: Plan

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            if let t = plan.totals {
                HStack(alignment: .top, spacing: 12) {
                    Stat(value: Money.text(t.costGbp), label: "per person")
                    Stat(value: String(format: "%.1f km", t.walkKm), label: "walking between stops")
                    Stat(value: t.finish ?? plan.stops.last?.depart ?? "–", label: "finish")
                }
                Text(breakdown(t))
                    .font(.footnote)
                    .foregroundStyle(Theme.inkSoft)
            }
            if let start = plan.summary?.first {
                Text(start).font(.footnote).foregroundStyle(Theme.inkSoft)
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
        .overlay(RoundedRectangle(cornerRadius: 18).stroke(Theme.accent.opacity(0.7), lineWidth: 1))
    }

    private func breakdown(_ t: Totals) -> String {
        let spend = t.spendGbp > 0 ? "\(Money.text(t.spendGbp)) food and entry" : "Free entry"
        let fare = t.transportGbp > 0 ? "\(Money.text(t.transportGbp)) Tube or bus" : "all on foot"
        return "\(spend), \(fare)."
    }
}

struct Stat: View {
    let value: String
    let label: String

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(value)
                .font(Theme.title.monospacedDigit())
                .foregroundStyle(Theme.accent)
                .lineLimit(1)
                .minimumScaleFactor(0.8)
            Text(label)
                .font(.footnote)
                .foregroundStyle(Theme.inkSoft)
                .lineLimit(2)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .accessibilityElement(children: .combine)
    }
}

enum Money {
    /// £21, or £21.50
    static func text(_ gbp: Double) -> String {
        gbp.rounded() == gbp ? "£\(Int(gbp))" : String(format: "£%.2f", gbp)
    }
}

/// The day's shape (D112): each stop as a block across the day, taller where we expect you to enjoy it more.
/// No numbers on the height: it's a picture of the day, not a score. The example day's blocks are all the same height.
struct DayShapeChart: View {
    let stops: [Stop]
    let personal: Bool

    private struct Block: Identifiable {
        let id: Int
        let start: Double
        let end: Double
        let height: Double
    }

    private static func minutes(_ hhmm: String) -> Double {
        let parts = hhmm.split(separator: ":").compactMap { Double($0) }
        return parts.count == 2 ? parts[0] * 60 + parts[1] : 0
    }

    private var blocks: [Block] {
        let top = stops.compactMap(\.worthGbp).max() ?? 0
        return stops.indices.map { i in
            let s = stops[i]
            let h = (personal && top > 0) ? max(0.35, (s.worthGbp ?? 0) / top) : 0.7
            return Block(id: i + 1, start: Self.minutes(s.arrive), end: Self.minutes(s.depart), height: h)
        }
    }

    /// The time axis: 20 minutes either side of the stops, and room after the last hour mark for its label (m150).
    private static func axis(_ bs: [Block]) -> (lo: Double, hi: Double, ticks: [Double]) {
        let lo = (bs.map(\.start).min() ?? 600) - 20
        let end = (bs.map(\.end).max() ?? 1020) + 20
        let ticks = stride(from: (lo / 60).rounded(.up) * 60, through: end, by: 60).map { $0 }
        return (lo, max(end, (ticks.last ?? end) + 35), ticks)
    }

    var body: some View {
        let bs = blocks
        let axis = Self.axis(bs)
        VStack(alignment: .leading, spacing: 8) {
            Text("The shape of the day")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(Theme.inkSoft)
            Chart(bs) { b in
                RectangleMark(xStart: .value("Arrive", b.start), xEnd: .value("Leave", b.end),
                              yStart: .value("Base", 0.0), yEnd: .value("Height", b.height))
                    .foregroundStyle(Theme.accentFill)
                    .cornerRadius(5)
                    .annotation(position: .top) {
                        Text("\(b.id)").font(.footnote.weight(.semibold)).foregroundStyle(Theme.ink)
                    }
            }
            .chartYAxis(.hidden)
            .chartYScale(domain: 0.0...1.3)
            .chartXScale(domain: axis.lo...axis.hi)
            .chartXAxis {
                AxisMarks(values: axis.ticks) { v in
                    AxisGridLine().foregroundStyle(Theme.outline)
                    AxisValueLabel {
                        if let m = v.as(Double.self) {
                            Text(String(format: "%02d:00", Int(m / 60))).font(.footnote).foregroundStyle(Theme.inkSoft)
                        }
                    }
                }
            }
            .frame(height: 130)
            .accessibilityLabel("The day's \(bs.count) stops from \(stops.first?.arrive ?? "") to \(stops.last?.depart ?? "")")
            Text(personal ? "Taller blocks are the stops we expect you to enjoy most."
                          : "Each block is a stop, from arrival to leaving.")
                .font(.footnote)
                .foregroundStyle(Theme.inkSoft)
        }
        .padding(.vertical, 6)
    }
}

struct PlanMap: View {
    let stops: [Stop]

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
        Map(initialPosition: .automatic) {
            MapPolyline(coordinates: pins.map(\.coordinate))
                .stroke(Theme.accentFill, lineWidth: 3)
            ForEach(pins) { pin in
                Marker(pin.title, monogram: Text("\(pin.id)"), coordinate: pin.coordinate)
                    .tint(Theme.accentFill)
            }
        }
        .accessibilityLabel("Map of the day's \(pins.count) stops")
    }
}

struct StopRow: View {
    let number: Int
    let stop: Stop
    var showTravel = true
    let rated: Bool
    var swapped = false

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text("\(number)")
                .font(.headline)
                .foregroundStyle(Theme.onAccent)
                .frame(width: 30, height: 30)
                .background(Circle().fill(Theme.accentFill))
            VStack(alignment: .leading, spacing: 4) {
                Text("\(stop.arrive)–\(stop.depart)")
                    .font(.subheadline.monospacedDigit())
                    .foregroundStyle(Theme.inkSoft)
                Text(stop.title).font(Theme.title3).foregroundStyle(Theme.ink)
                if showTravel, !stop.travelText.isEmpty {
                    Text(stop.travelText).font(.footnote).foregroundStyle(Theme.inkSoft)
                }
                if swapped {
                    Label("Swapped in", systemImage: "arrow.triangle.2.circlepath").font(.footnote)
                }
                if stop.familiar {
                    Label("A place you loved", systemImage: "heart").font(.footnote)
                }
                if !stop.chosenFor.isEmpty {
                    Text("Chosen for: " + stop.chosenFor.joined(separator: ", ")).font(.footnote)
                        .foregroundStyle(Theme.ink)
                }
                if rated {
                    Label("Rated", systemImage: "checkmark").font(.footnote).foregroundStyle(Theme.inkSoft)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

extension Stop {
    /// Rating opens at the planned arrival (D110: only after the visit). Nil when the plan has no date.
    func ratingOpens(on day: String?) -> Date? {
        guard let day else { return nil }
        return Dates.stamp.date(from: "\(day) \(arrive)")
    }
}

/// Screen 10: the moment card in the new style (D112). Everything on it comes from the verified card or the plan:
/// the approach line, the best-light window, the cost and "worth about £V to you".
struct StopView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.openURL) private var openURL
    @Environment(\.dismiss) private var dismiss
    let stop: Stop
    @State private var showShot = false
    @State private var showRating = false
    @State private var confirmSwap = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                MomentHero(stop: stop)
                Text(stop.title)
                    .font(Theme.title)
                    .foregroundStyle(Theme.ink)
                if stop.familiar {
                    Label("A place you loved", systemImage: "heart").font(.subheadline).foregroundStyle(Theme.accent)
                }
                VStack(alignment: .leading, spacing: 6) {
                    InfoBlock(label: "Cost", text: stop.costText.replacingOccurrences(of: "Cost: ", with: "").capitalizedFirst)
                    if let worth = stop.worthGbp {
                        Text("Worth about \(Money.text(worth)) to you: our estimate from your answers so far.")
                            .font(.footnote)
                            .foregroundStyle(Theme.inkSoft)
                    }
                }
                VStack(alignment: .leading, spacing: 12) {
                    Text("How to arrive")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(Theme.inkSoft)
                    if !stop.travelText.isEmpty {
                        Text(stop.travelText).foregroundStyle(Theme.ink)
                    }
                    if let steps = stop.approachSteps, !steps.isEmpty {
                        ApproachLine(steps: steps)
                    } else if !stop.approach.isEmpty {
                        Text(stop.approach).foregroundStyle(Theme.ink)
                    }
                }
                .surfaceCard()
                if let light = stop.bestLight, !light.isEmpty {
                    BestLightBox(light: light, window: stop.bestWindow ?? "")
                }
                InfoBlock(label: "What happens", text: stop.what)
                if let queue = stop.queueMin, queue > 0 {
                    InfoBlock(label: "Queue", text: "Allow about \(Int(queue)) min to queue.")
                }
                InfoBlock(label: "If it rains", text: stop.rainSwap)
                HStack {
                    if let pin = stop.pin {
                        Button {
                            openURL(URL(string: "http://maps.apple.com/?daddr=\(pin.lat),\(pin.lon)&dirflg=w")!)
                        } label: {
                            Label("Directions", systemImage: "arrow.triangle.turn.up.right.diamond")
                        }
                        .buttonStyle(.bordered)
                    }
                    if stop.card?.shotCard != nil {
                        Button { showShot = true } label: { Label("Shot card", systemImage: "camera") }
                            .buttonStyle(.bordered)
                    }
                }
                if stop.rateable {
                    Button {
                        confirmSwap = true
                    } label: {
                        Label("Swap this stop", systemImage: "arrow.triangle.2.circlepath")
                            .frame(maxWidth: .infinity, minHeight: 44)
                    }
                    .buttonStyle(.bordered)
                    .disabled(model.busy)
                    rating
                }
            }
            .padding(20)
        }
        .background(Theme.background)
        .navigationBarTitleDisplayMode(.inline)   // the card's serif title is the page title
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
        .sheet(isPresented: $showShot) {
            if let card = stop.card {
                NavigationStack {
                    ScrollView { ShotCardView(card: card).padding(20) }
                        .background(Theme.background)
                        .serifTitle("Shot card")
                }
            }
        }
        .sheet(isPresented: $showRating) { RatingView(stop: stop) }
    }

    /// Only after the visit (D110): before the planned arrival, say when the rating opens.
    @ViewBuilder private var rating: some View {
        let done = model.rated.contains(stop.momentId)
        if let opens = stop.ratingOpens(on: model.plan?.date), opens > .now, !done {
            InfoBlock(label: "Rating",
                      text: "You can rate this stop after your visit, from \(stop.arrive) on \(Dates.dayName.string(from: opens)).")
        } else {
            PrimaryButton(title: done ? "Rated. Thank you" : "Been here? How did it feel?", disabled: done) {
                showRating = true
            }
        }
    }
}

/// The big picture at the top of a moment card: the card's photo with its credit underneath (openly licensed, until
/// Abram's own replace them), or, for a card without one, the satellite view of the place: real, not invented.
struct MomentHero: View {
    let stop: Stop

    var body: some View {
        let found = CardPhotos.photo(for: stop.momentId)
        VStack(alignment: .leading, spacing: 6) {
            ZStack(alignment: .topLeading) {
                if let image = found?.1 {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFill()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .clipped()
                        .accessibilityLabel("Photo of the place")
                } else if let pin = stop.pin {
                    Map(initialPosition: .camera(MapCamera(centerCoordinate: pin.coordinate, distance: 900,
                                                           heading: 0, pitch: 50))) {
                        Marker(stop.title, coordinate: pin.coordinate).tint(Theme.accentFill)
                    }
                    .mapStyle(.imagery(elevation: .realistic))
                    .allowsHitTesting(false)
                } else {
                    Theme.surfaceHigh
                }
                // the chip and the time sit at the top, so the map's logo and legal link at the bottom stay clear (m150)
                LinearGradient(colors: [.black.opacity(0.6), .clear], startPoint: .top, endPoint: .center)
                    .allowsHitTesting(false)
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 8) {
                        if let worth = stop.worthGbp {
                            Text("Worth about \(Money.text(worth)) to you")
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(Theme.onAccent)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(Theme.accentFill, in: Capsule())
                        }
                        Text("\(stop.arrive)–\(stop.depart)")
                            .font(.subheadline.monospacedDigit())
                            .foregroundStyle(.white)
                    }
                    Spacer(minLength: 8)
                    if found == nil {
                        Text("Photo to come")
                            .font(.footnote)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 4)
                            .background(.ultraThinMaterial, in: Capsule())
                    }
                }
                .padding(14)
            }
            .frame(height: 260)
            .clipShape(RoundedRectangle(cornerRadius: 18))
            .accessibilityElement(children: .combine)
            if let photo = found?.0 {
                // the credit the licence asks for; it opens the photo's page on Wikimedia Commons
                Link(photo.credit, destination: photo.source)
                    .font(.footnote)
                    .foregroundStyle(Theme.inkSoft)
            }
        }
    }
}

/// The approach as one vertical line: from where, the way in, where you arrive (the card's own words).
struct ApproachLine: View {
    let steps: [ApproachStep]

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            ForEach(steps.indices, id: \.self) { i in
                let last = i == steps.count - 1
                HStack(alignment: .top, spacing: 12) {
                    VStack(spacing: 0) {
                        Circle()
                            .fill(last ? Theme.accentFill : Theme.surface)
                            .overlay(Circle().stroke(Theme.accentFill, lineWidth: 2))
                            .frame(width: 14, height: 14)
                            .padding(.top, 3)
                        if !last {
                            Rectangle()
                                .fill(Theme.accentFill.opacity(0.6))
                                .frame(width: 2)
                                .frame(maxHeight: .infinity)
                        }
                    }
                    VStack(alignment: .leading, spacing: 2) {
                        Text(steps[i].label)
                            .font(.footnote.weight(.semibold))
                            .foregroundStyle(Theme.inkSoft)
                        Text(steps[i].text)
                            .foregroundStyle(Theme.ink)
                    }
                    .padding(.bottom, last ? 0 : 14)
                }
                .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}

/// The best-light window from the card, with the time on the plan's day when there is one.
struct BestLightBox: View {
    let light: String
    let window: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Label("Best light", systemImage: "sun.horizon")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(Theme.accent)
            if !window.isEmpty {
                Text(window).font(Theme.title2.monospacedDigit()).foregroundStyle(Theme.ink)
            }
            Text(light).foregroundStyle(Theme.inkSoft)
        }
        .surfaceCard()
    }
}

/// Opened from a stop that has one.
struct ShotCardView: View {
    let card: Card

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(card.title, systemImage: "camera").font(Theme.title3).foregroundStyle(Theme.ink)
            if let shot = card.shotCard {
                if let lat = shot.standAt?.lat, let lon = shot.standAt?.lon {
                    let here = CLLocationCoordinate2D(latitude: lat, longitude: lon)
                    Map(initialPosition: .region(MKCoordinateRegion(center: here, latitudinalMeters: 500,
                                                                    longitudinalMeters: 500))) {
                        Marker("Stand here", coordinate: here).tint(Theme.accentFill)
                    }
                    .frame(height: 150)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                    .allowsHitTesting(false)
                }
                InfoBlock(label: "Where to stand", text: shot.standAt?.note ?? "")
                InfoBlock(label: "Which way to face", text: shot.face ?? "")
                InfoBlock(label: "What to frame", text: shot.frame ?? "")
                InfoBlock(label: "When", text: shot.when ?? "")
                InfoBlock(label: "What spoils it", text: shot.avoid ?? "")
            }
        }
    }
}

/// Screen 11: after the visit, one tap on a worded 1–5 scale (D110, D112).
struct RatingView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let stop: Stop
    @State private var rating: Int?
    @State private var bring = ""

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text("How did that feel?")
                        .font(Theme.title)
                        .foregroundStyle(Theme.ink)
                    ScaleRow(low: "Flat", high: "Unforgettable", labels: Labels.feel, value: $rating)
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Would you bring someone here? (optional)")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(Theme.inkSoft)
                        Picker("Bring someone", selection: $bring) {
                            Text("Skip").tag("")
                            Text("Yes").tag("yes")
                            Text("No").tag("no")
                        }
                        .pickerStyle(.segmented)
                    }
                    PrimaryButton(title: model.busy ? "Saving…" : "Save", disabled: rating == nil || model.busy) {
                        guard let rating else { return }
                        Task {
                            await model.rate(stop, rating: rating, wouldBring: bring.isEmpty ? nil : bring == "yes")
                            if model.errorMessage == nil { dismiss() }
                        }
                    }
                }
                .padding(20)
            }
            .background(Theme.background)
            .serifTitle(stop.title)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) { Button("Close") { dismiss() } }
            }
        }
    }
}

extension String {
    /// "free" → "Free", for lines shown under their own label.
    var capitalizedFirst: String { prefix(1).uppercased() + String(dropFirst()) }
}
