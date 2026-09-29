import MapKit
import SwiftUI

/// Home: the current plan, or the form to make one. Help & safety and your data are always one tap away.
struct HomeView: View {
    @State private var showSafety = false
    @State private var showSettings = false
    @Environment(AppModel.self) private var model

    var body: some View {
        NavigationStack {
            Group {
                if let plan = model.plan {
                    PlanView(plan: plan)
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

/// Build 1 plans from Charing Cross (the Test B start, D104), on a date and between times you choose.
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

/// Screen 14: the map and the stops are one object; the numbers match.
struct PlanView: View {
    @Environment(AppModel.self) private var model
    let plan: Plan
    @State private var showNewPlan = false

    var body: some View {
        List {
            Section {
                PlanMap(stops: plan.stops)
                    .frame(height: 240)
                    .listRowInsets(EdgeInsets())
            }
            Section {
                ForEach(plan.summary ?? [], id: \.self) { line in
                    Text(line).font(.subheadline)
                }
            } header: {
                Text(plan.title ?? "Your day")
            }
            Section("Stops") {
                ForEach(plan.stops.indices, id: \.self) { i in
                    NavigationLink(value: plan.stops[i]) {
                        StopRow(number: i + 1, stop: plan.stops[i], rated: model.rated.contains(plan.stops[i].id))
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
    let rated: Bool

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
                if !stop.travelText.isEmpty {
                    Text(stop.travelText).font(.footnote).foregroundStyle(.secondary)
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

/// Screen 15: the moment card. The arrival comes first, because the approach is the moment.
struct StopView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.openURL) private var openURL
    let stop: Stop
    @State private var showShot = false
    @State private var showRating = false

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
                InfoBlock(label: "Cost", text: stop.costText)
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
                    let done = model.rated.contains(stop.id)
                    PrimaryButton(title: done ? "Rated. Thank you" : "Done here: how did it feel?", disabled: done) {
                        showRating = true
                    }
                }
            }
            .padding(20)
        }
        .navigationTitle(stop.title)
        .navigationBarTitleDisplayMode(.inline)
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
}

/// Screen 16: read in one glance while standing on the spot.
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

/// Screen 17: one tap, 1–5.
struct RatingView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let stop: Stop
    @State private var rating: Int?
    @State private var bring = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("How did that feel?") {
                    ScaleRow(low: "Not good", high: "Wonderful", value: $rating)
                }
                Section("Would you bring someone here? (optional)") {
                    Picker("Bring someone", selection: $bring) {
                        Text("Skip").tag("")
                        Text("Yes").tag("yes")
                        Text("No").tag("no")
                    }
                    .pickerStyle(.segmented)
                }
                Section {
                    PrimaryButton(title: "Save", disabled: rating == nil || model.busy) {
                        guard let rating else { return }
                        Task {
                            await model.rate(stop, rating: rating, wouldBring: bring.isEmpty ? nil : bring == "yes")
                            if model.errorMessage == nil { dismiss() }
                        }
                    }
                }
            }
            .navigationTitle(stop.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) { Button("Close") { dismiss() } }
            }
        }
    }
}
