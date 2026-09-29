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

/// Screen 7. Build 1 plans from Charing Cross (the Test B start, D104), on a date and between times you choose.
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
            }
        }
        .navigationTitle("Plan a day")
    }
}

/// Screen 8: the summary first (D110), then the map and the stops (the numbers match), or the stops as a list.
struct PlanView: View {
    @Environment(AppModel.self) private var model
    let plan: Plan
    var forcedLayout: String?
    @AppStorage("planLayout") private var savedLayout = "map"
    @State private var showNewPlan = false
    @State private var showImprove = false

    var body: some View {
        let layout = Binding(get: { forcedLayout ?? savedLayout }, set: { savedLayout = $0 })
        let asList = layout.wrappedValue == "list"
        List {
            Section {
                PlanSummary(plan: plan)
                Picker("Show", selection: layout) {
                    Text("Map").tag("map")
                    Text("List").tag("list")
                }
                .pickerStyle(.segmented)
            } header: {
                Text(plan.title ?? "Your day")
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
                            .foregroundStyle(.secondary)
                    }
                    NavigationLink(value: stop) {
                        StopRow(number: i + 1, stop: stop, showTravel: !asList,
                                rated: model.rated.contains(stop.momentId), swapped: model.swappedIn == stop.momentId)
                    }
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
                if model.improved {
                    Text("Thanks. Your next plans use what you told us.")
                    Button("Plan this day again") { Task { await model.replan() } }
                        .disabled(model.busy)
                    Button("Change what you told us") { showImprove = true }
                } else {
                    Button {
                        showImprove = true
                    } label: {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Improve my plans").font(.headline)
                            Text("Optional, about 2 minutes: your budget, pace, interests and photos.")
                                .font(.footnote)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
            Section {
                Button("Plan another day") {
                    model.planAnotherDay()
                    showNewPlan = true
                }
            }
        }
        .navigationTitle("Your day")
        .navigationDestination(for: Stop.self) { stop in
            StopView(stop: stop)
        }
        .sheet(isPresented: $showNewPlan) {
            NavigationStack {
                PlanFormView(onDone: { showNewPlan = false })
            }
        }
        .sheet(isPresented: $showImprove) { ImproveView() }
    }
}

/// Cost per person, walking between stops and the finish time, at the top of the plan (D110).
struct PlanSummary: View {
    let plan: Plan

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            if let t = plan.totals {
                HStack(alignment: .top, spacing: 12) {
                    Stat(value: Money.text(t.costGbp), label: "per person")
                    Stat(value: String(format: "%.1f km", t.walkKm), label: "walking between stops")
                    Stat(value: t.finish ?? plan.stops.last?.depart ?? "–", label: "finish")
                }
                Text(breakdown(t))
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            if let start = plan.summary?.first {
                Text(start).font(.footnote).foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 4)
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
            Text(value).font(.title3.bold().monospacedDigit())
            Text(label).font(.caption).foregroundStyle(.secondary)
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
                .stroke(Theme.accent, lineWidth: 3)
            ForEach(pins) { pin in
                Marker(pin.title, monogram: Text("\(pin.id)"), coordinate: pin.coordinate)
                    .tint(Theme.accent)
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
                .foregroundStyle(.white)
                .frame(width: 28, height: 28)
                .background(Circle().fill(Theme.accent))
            VStack(alignment: .leading, spacing: 4) {
                Text("\(stop.arrive)–\(stop.depart)")
                    .font(.subheadline.monospacedDigit())
                    .foregroundStyle(.secondary)
                Text(stop.title).font(.headline)
                if showTravel, !stop.travelText.isEmpty {
                    Text(stop.travelText).font(.footnote).foregroundStyle(.secondary)
                }
                if swapped {
                    Label("Swapped in", systemImage: "arrow.triangle.2.circlepath").font(.footnote)
                }
                if stop.familiar {
                    Label("A place you loved", systemImage: "heart").font(.footnote)
                }
                if !stop.chosenFor.isEmpty {
                    Text("Chosen for: " + stop.chosenFor.joined(separator: ", ")).font(.footnote)
                }
                if rated {
                    Label("Rated", systemImage: "checkmark").font(.footnote).foregroundStyle(.secondary)
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

/// Screen 9: the moment card. The arrival comes first, because the approach is the moment.
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
            VStack(alignment: .leading, spacing: 16) {
                Text("\(stop.arrive)–\(stop.depart)")
                    .font(.subheadline.monospacedDigit())
                    .foregroundStyle(.secondary)
                Text(stop.title).font(.title2.bold())
                InfoBlock(label: "How to arrive",
                          text: [stop.travelText, stop.approach].filter { !$0.isEmpty }.joined(separator: "\n"))
                InfoBlock(label: "What happens", text: stop.what)
                if let queue = stop.queueMin, queue > 0 {
                    InfoBlock(label: "Queue", text: "Allow about \(Int(queue)) min to queue.")
                }
                InfoBlock(label: "When it's best", text: stop.bestText.replacingOccurrences(of: "Best: ", with: ""))
                InfoBlock(label: "Cost", text: stop.costText.replacingOccurrences(of: "Cost: ", with: "").capitalizedFirst)
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
        .navigationTitle(stop.title)
        .navigationBarTitleDisplayMode(.inline)
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
                        .navigationTitle("Shot card")
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
            PrimaryButton(title: done ? "Rated. Thank you" : "Been here? Rate it 1–5", disabled: done) {
                showRating = true
            }
        }
    }
}

/// Opened from a stop that has one. The layout is the example on screen 13.
struct ShotCardView: View {
    let card: Card

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(card.title, systemImage: "camera").font(.headline)
            if let shot = card.shotCard {
                if let lat = shot.standAt?.lat, let lon = shot.standAt?.lon {
                    let here = CLLocationCoordinate2D(latitude: lat, longitude: lon)
                    Map(initialPosition: .region(MKCoordinateRegion(center: here, latitudinalMeters: 500,
                                                                    longitudinalMeters: 500))) {
                        Marker("Stand here", coordinate: here).tint(Theme.accent)
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

/// Screen 10: after the visit, one tap 1–5 on large labelled buttons (D110).
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
                        .font(.title2.bold())
                    ScaleRow(low: "Poor", high: "Wonderful", labels: Labels.feel, value: $rating)
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Would you bring someone here? (optional)")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(.secondary)
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
            .navigationTitle(stop.title)
            .navigationBarTitleDisplayMode(.inline)
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
