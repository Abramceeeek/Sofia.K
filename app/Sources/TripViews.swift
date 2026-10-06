import SwiftUI
import UIKit

// D120: the ODYS Trips design (Abram's "ODYS Trips" file): three tabs, "Plan a trip" in four questions, the trip as a
// checklist (getting there, where you'll stay, your days) and a running total. What differs from the design, and why,
// is in decisions/decision-log.md (D121).

// ---- the tabs -------------------------------------------------------------------------------------------------

/// Home after onboarding. Before the first plan, people in the UK get the survey and the blind pair (Build 2) first.
struct MainTabs: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        @Bindable var model = model
        if model.needsFirstRun {
            FirstPlanFlow()
        } else {
            TabView(selection: $model.tab) {
                HomeView()
                    .tabItem { Label { Text("Trip") } icon: { Image(uiImage: TabIcons.image(.trip)) } }
                    .tag(MainTab.trip)
                BookView()
                    .tabItem { Label { Text("Book") } icon: { Image(uiImage: TabIcons.image(.book)) } }
                    .tag(MainTab.book)
                YouView()
                    .tabItem { Label { Text("You") } icon: { Image(uiImage: TabIcons.image(.you)) } }
                    .tag(MainTab.you)
            }
            .tint(Theme.accent)
            .fullScreenCover(isPresented: $model.showCreate, onDismiss: { model.editingTrip = nil }) {
                TripCreateFlow(trip: model.editingTrip ?? model.newTrip(), editing: model.editingTrip != nil)
            }
            .fullScreenCover(isPresented: $model.showPair) { PairFlow() }
        }
    }
}

/// The design's tab icons, drawn from its own paths (24 × 22): an arch for Trip, a paper plane for Book, a person for You.
enum TabIcons {
    static func image(_ tab: MainTab) -> UIImage {
        let image = UIGraphicsImageRenderer(size: CGSize(width: 24, height: 22)).image { _ in
            let p = UIBezierPath()
            switch tab {
            case .trip:
                p.move(to: CGPoint(x: 12, y: 2))
                p.addCurve(to: CGPoint(x: 5, y: 9), controlPoint1: CGPoint(x: 8, y: 2), controlPoint2: CGPoint(x: 5, y: 5))
                p.addLine(to: CGPoint(x: 5, y: 20))
                p.addLine(to: CGPoint(x: 19, y: 20))
                p.addLine(to: CGPoint(x: 19, y: 9))
                p.addCurve(to: CGPoint(x: 12, y: 2), controlPoint1: CGPoint(x: 19, y: 5), controlPoint2: CGPoint(x: 16, y: 2))
                p.close()
            case .book:
                p.move(to: CGPoint(x: 3, y: 12))
                p.addLine(to: CGPoint(x: 21, y: 4))
                p.addLine(to: CGPoint(x: 15, y: 20))
                p.addLine(to: CGPoint(x: 12, y: 13))
                p.close()
            case .you:
                p.append(UIBezierPath(arcCenter: CGPoint(x: 12, y: 7), radius: 4, startAngle: 0, endAngle: .pi * 2,
                                      clockwise: true))
                let body = UIBezierPath()
                body.move(to: CGPoint(x: 4, y: 21))
                body.addCurve(to: CGPoint(x: 12, y: 14), controlPoint1: CGPoint(x: 4, y: 16), controlPoint2: CGPoint(x: 8, y: 14))
                body.addCurve(to: CGPoint(x: 20, y: 21), controlPoint1: CGPoint(x: 16, y: 14), controlPoint2: CGPoint(x: 20, y: 16))
                p.append(body)
            }
            p.lineWidth = 1.8
            p.lineJoinStyle = .round
            p.lineCapStyle = .round
            UIColor.black.setStroke()
            p.stroke()
        }
        return image.withRenderingMode(.alwaysTemplate)
    }
}

// ---- small parts from the design ----------------------------------------------------------------------------------

/// The arch lit, with its light spilling out (the design's 30 × 36 mark on "Plan a trip").
struct ArchMark: View {
    var body: some View {
        ZStack {
            PoolShape.logo.fill(Theme.accent.opacity(0.35))
            DoorShape.logoLight.fill(Theme.accent)
        }
        .frame(width: 30, height: 36)
        .accessibilityHidden(true)
    }
}

/// A tile with a label and a line under it: lengths, feelings, filters. Amber edge and a little warmth when chosen.
struct OptionTile: View {
    let label: String
    var sub: String?
    let on: Bool
    var serif = false
    var offFill: Color = .clear
    var offStroke: Color = Theme.outline
    let action: () -> Void

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            VStack(alignment: .leading, spacing: 2) {
                Text(label)
                    .font(serif ? Theme.serif(21, relativeTo: .title3) : .subheadline)
                    .foregroundStyle(Theme.ink)
                if let sub, !sub.isEmpty {
                    Text(sub)
                        .font(serif ? .subheadline : .caption)
                        .foregroundStyle(serif ? Theme.inkTertiary : Theme.muted)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
            .multilineTextAlignment(.leading)
            .padding(.horizontal, serif ? 18 : 12)
            .padding(.vertical, serif ? 13 : 10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(on ? Theme.selected : offFill, in: RoundedRectangle(cornerRadius: serif ? 18 : 14))
            .overlay(RoundedRectangle(cornerRadius: serif ? 18 : 14).stroke(on ? Theme.accent : offStroke, lineWidth: 1.5))
            .contentShape(RoundedRectangle(cornerRadius: serif ? 18 : 14))
            .animation(Motion.select, value: on)
        }
        .buttonStyle(PressStyle())
        .accessibilityAddTraits(on ? .isSelected : [])
    }
}

/// A one-tap filter: a small outlined pill that warms up when on.
struct FilterChip: View {
    let label: String
    let on: Bool
    let action: () -> Void

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            Text(label)
                .font(.subheadline)
                .foregroundStyle(Theme.ink)
                .lineLimit(1)
                .padding(.horizontal, 14)
                .frame(height: 36)
                .background(on ? Theme.selected : Color.clear, in: Capsule())
                .overlay(Capsule().stroke(on ? Theme.accent : Theme.outline, lineWidth: 1.5))
                .contentShape(Capsule())
                .frame(minHeight: 44)
        }
        .buttonStyle(PressStyle())
        .accessibilityAddTraits(on ? .isSelected : [])
    }
}

/// "To do", "Saved, not booked", "Booked": one coloured label per trip card.
struct StatusLabel: View {
    let text: String
    let fill: Color
    let color: Color

    static func of(_ choice: TripChoice?) -> StatusLabel {
        guard let choice else { return StatusLabel(text: "To do", fill: Theme.surfaceHigh, color: Theme.inkSoft) }
        return choice.booked ? StatusLabel(text: "Booked", fill: Color(hex: 0x1F3A2A), color: Color(hex: 0x9BE0B0))
                             : StatusLabel(text: "Saved, not booked", fill: Color(hex: 0x3A2F1C), color: Theme.accent)
    }

    var body: some View {
        Text(text)
            .font(.footnote)
            .foregroundStyle(color)
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(fill, in: RoundedRectangle(cornerRadius: 12))
    }
}

/// The small uppercase label above a section ("1 · GETTING THERE").
struct SectionLabel: View {
    let text: String

    var body: some View {
        Text(text.uppercased())
            .font(.footnote)
            .tracking(0.8)
            .foregroundStyle(Theme.muted)
    }
}

// ---- Trip tab: home ---------------------------------------------------------------------------------------------

/// "Where to next?": one big action (Plan a trip), then your day and your trips underneath.
struct TripHome: View {
    @Environment(AppModel.self) private var model
    var onHelp: () -> Void = {}
    var onData: () -> Void = {}

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                TopBar(eyebrow: AppModel.greeting, onHelp: onHelp, onData: onData)
                PageTitle(text: "Where to next?", font: Theme.display).settle(0)
                PlanTripCard { model.showCreate = true }.settle(1)
                if !model.pairDone, !model.isVisitor, !model.client.demo {
                    PairInviteRow { model.showPair = true }.settle(2)
                }
                if let plan = model.plan {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Your day").font(.subheadline).foregroundStyle(Theme.muted)
                        NavigationLink(value: TripDest.day) { DayRow(plan: plan) }
                            .buttonStyle(PressStyle())
                    }
                    .settle(2)
                }
                if !model.trips.isEmpty {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Your trips").font(.subheadline).foregroundStyle(Theme.muted)
                        ForEach(model.trips) { trip in
                            NavigationLink(value: TripDest.trip(trip.id)) { TripRow(trip: trip) }
                                .buttonStyle(PressStyle())
                        }
                    }
                    .settle(3)
                }
            }
            .padding(.horizontal, 24)
            .padding(.top, 8)
            .padding(.bottom, 32)
        }
        .background(Theme.background)
    }
}

struct PlanTripCard: View {
    let action: () -> Void

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            VStack(alignment: .leading, spacing: 14) {
                ArchMark()
                Text("Plan a trip")
                    .font(Theme.serif(26, relativeTo: .title2))
                    .foregroundStyle(Theme.ink)
                Text("One day or two weeks. I'll find the flight, the stay and the moments, and you book with whichever site you trust.")
                    .font(.body)
                    .foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
                Text("Start")
                    .font(.headline)
                    .foregroundStyle(Theme.onAccent)
                    .padding(.horizontal, 22)
                    .frame(height: 48)
                    .background(Theme.accentFill, in: Capsule())
            }
            .multilineTextAlignment(.leading)
            .padding(22)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RadialGradient(colors: [Color(hex: 0x3B2E1E), Theme.surface], center: UnitPoint(x: 0.8, y: 0),
                               startRadius: 0, endRadius: 260),
                in: RoundedRectangle(cornerRadius: 24))
        }
        .buttonStyle(PressStyle())
    }
}

/// Build 2, for someone who had a plan before the pair existed (an earlier build): the comparison is still offered.
struct PairInviteRow: View {
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(alignment: .top, spacing: 14) {
                ArchGlyph().padding(.top, 4)
                VStack(alignment: .leading, spacing: 4) {
                    Text("Two plans for a Saturday").font(Theme.title3).foregroundStyle(Theme.ink)
                    Text("Which would you rather do? About two minutes, and it helps the test most.")
                        .font(.subheadline)
                        .foregroundStyle(Theme.muted)
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer(minLength: 0)
            }
            .multilineTextAlignment(.leading)
            .surfaceCard(padding: 18)
        }
        .buttonStyle(PressStyle())
    }
}

/// "Your day": the current plan, one tap from home.
struct DayRow: View {
    let plan: Plan

    var body: some View {
        HStack(spacing: 14) {
            Field(feel: plan.stops.first(where: { $0.rateable })?.feelWord)
                .frame(width: 56, height: 56)
                .clipShape(RoundedRectangle(cornerRadius: 14))
            VStack(alignment: .leading, spacing: 2) {
                Text(Dates.longDay(plan.date) ?? plan.title ?? "Your day")
                    .font(Theme.serif(20, relativeTo: .title3))
                    .foregroundStyle(Theme.ink)
                Text("\(plan.stops.count) stops" + (plan.totals?.finish.map { " · done by \($0)" } ?? ""))
                    .font(.subheadline)
                    .foregroundStyle(Theme.muted)
            }
            Spacer(minLength: 0)
            Image(systemName: "chevron.right").font(.footnote).foregroundStyle(Theme.muted)
        }
        .padding(12)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 20))
    }
}

struct TripRow: View {
    let trip: Trip

    var body: some View {
        HStack(spacing: 14) {
            RadialGradient(colors: [Color(hex: 0xE7B77A), Color(hex: 0x9A6A3E), Color(hex: 0x2A1F17)],
                           center: UnitPoint(x: 0.5, y: 0.2), startRadius: 0, endRadius: 50)
                .frame(width: 56, height: 56)
                .clipShape(RoundedRectangle(cornerRadius: 14))
            VStack(alignment: .leading, spacing: 2) {
                Text(trip.city).font(Theme.serif(20, relativeTo: .title3)).foregroundStyle(Theme.ink)
                Text("\(trip.range) · \(trip.lengthLabel)").font(.subheadline).foregroundStyle(Theme.muted)
            }
            Spacer(minLength: 0)
            Image(systemName: "chevron.right").font(.footnote).foregroundStyle(Theme.muted)
        }
        .padding(12)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 20))
    }
}

// ---- Plan a trip: where, how long, getting there, how it should feel ---------------------------------------------

struct TripCreateFlow: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State private var trip: Trip
    @State private var step: Int
    @State private var lengthKey: String
    @State private var showAirports = false
    let editing: Bool

    static let lengths: [(key: String, label: String, nights: Int?, sub: String)] = [
        ("day", "One day", 0, "Just the moments"), ("wknd", "A weekend", 2, "2 nights"), ("week", "A week", 6, "6 nights"),
        ("two", "Two weeks", 13, "13 nights"), ("custom", "Custom", nil, "Any number of nights"),
    ]

    init(trip: Trip, editing: Bool, startAt: Int? = nil) {
        _trip = State(initialValue: trip)
        _step = State(initialValue: startAt ?? (editing ? 1 : 0))
        let key = Self.lengths.first { $0.nights == trip.nights }?.key ?? "custom"
        _lengthKey = State(initialValue: key)
        self.editing = editing
    }

    var body: some View {
        VStack(spacing: 0) {
            header
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    switch step {
                    case 0: WhereStep()
                    case 1: WhenStep(trip: $trip, lengthKey: $lengthKey)
                    case 2: FromStep(trip: $trip, showAirports: $showAirports)
                    default: FeelStep(trip: $trip)
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 12)
                .padding(.bottom, 24)
                .id(step)
                .settle(0)
            }
            .scrollBounceBehavior(.basedOnSize)
        }
        .background(Theme.background)
        .safeAreaInset(edge: .bottom) {
            PrimaryButton(title: buttonTitle, disabled: model.busy) { next() }
                .padding(.horizontal, 24)
                .padding(.top, 8)
                .padding(.bottom, 8)
                .background(Theme.background)
        }
        .sheet(isPresented: $showAirports) {
            AirportPicker { place in
                trip.origin = place
                trip.originGuessed = false
                trip.needFlight = true
            }
        }
        .task {
            if !editing, trip.origin == nil { trip = await model.guessOrigin(for: trip) }
        }
    }

    private var header: some View {
        HStack {
            Button(backTitle) {
                if backTitle == "Cancel" { dismiss() } else { step -= 1 }
            }
            .font(.body)
            .foregroundStyle(Theme.accent)
            .frame(minWidth: 60, minHeight: 44, alignment: .leading)
            Spacer()
            HStack(spacing: 6) {
                ForEach(0..<4, id: \.self) { i in
                    Capsule()
                        .fill(i <= step ? Theme.accent : Color(hex: 0x3A3E46))
                        .frame(width: i == step ? 22 : 6, height: 6)
                }
            }
            .animation(.easeOut(duration: 0.3), value: step)
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("Question \(step + 1) of 4")
            Spacer()
            Color.clear.frame(width: 60, height: 1)
        }
        .padding(.horizontal, 24)
        .padding(.top, 8)
        .padding(.bottom, 8)
        .background(Theme.background)
    }

    private var backTitle: String { step == 0 || (editing && step == 1) ? "Cancel" : "‹ Back" }

    private var buttonTitle: String {
        if step < 3 { return "Continue" }
        if model.busy { return "Planning your days…" }
        return editing ? "Plan the trip again" : "Make my trip"
    }

    private func next() {
        guard step == 3 else {
            step += 1
            return
        }
        Task {
            var t = trip
            if editing { t.days = []; t.used = [] }
            if await model.makeTrip(t) {
                if editing { model.book.resultsFor = nil }
                dismiss()
                model.tab = .trip
                var p = NavigationPath()
                p.append(TripDest.trip(t.id))
                model.path = p
            }
        }
    }
}

struct WhereStep: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            PageTitle(text: "Where are you going?", font: Theme.h1)
            HStack {
                Text("London").foregroundStyle(Theme.ink)
                Spacer()
                Text("United Kingdom").font(.footnote).foregroundStyle(Theme.muted)
            }
            .padding(.horizontal, 16)
            .frame(height: 54)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
            .overlay(RoundedRectangle(cornerRadius: 16).stroke(Theme.accent, lineWidth: 1.5))
            Text("In this test").font(.subheadline).foregroundStyle(Theme.muted).padding(.top, 6)
            // D120: London now, then UK cities, then Europe, then further (Abram, 6 Oct)
            CityLine(name: "London", note: "Ready to test", ready: true)
            CityLine(name: "Edinburgh, Manchester and the UK", note: "Coming next", ready: false)
            CityLine(name: "Paris, Rome and Europe", note: "Coming later", ready: false)
        }
    }
}

struct CityLine: View {
    let name: String
    let note: String
    let ready: Bool

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text(name).foregroundStyle(ready ? Theme.ink : Color(hex: 0x7A746B))
                Spacer(minLength: 8)
                Text(note).font(.footnote).foregroundStyle(Theme.muted)
            }
            .frame(minHeight: 52)
            .padding(.horizontal, 4)
            Rectangle().fill(Theme.hairline).frame(height: 1)
        }
    }
}

struct WhenStep: View {
    @Binding var trip: Trip
    @Binding var lengthKey: String

    private var isCustom: Bool { lengthKey == "custom" }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            PageTitle(text: "How long for?", font: Theme.h1)
            LazyVGrid(columns: [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)], spacing: 10) {
                ForEach(TripCreateFlow.lengths.filter { $0.nights != nil }, id: \.key) { l in
                    OptionTile(label: l.label, sub: l.sub, on: lengthKey == l.key, serif: true, offFill: Theme.surface,
                               offStroke: .clear) {
                        lengthKey = l.key
                        trip.nights = l.nights ?? trip.nights
                    }
                }
            }
            OptionTile(label: "Custom", sub: isCustom ? "\(trip.nights) night\(trip.nights == 1 ? "" : "s")" : "Any number of nights",
                       on: isCustom, serif: true, offFill: Theme.surface, offStroke: .clear) { lengthKey = "custom" }
            if isCustom { nightsStepper }
            Text(isCustom ? "Tap the first day, then the last day" : "Starting")
                .font(.subheadline)
                .foregroundStyle(Theme.muted)
                .padding(.top, 6)
            DateStrip(trip: $trip, custom: isCustom)
                .padding(.horizontal, -24)
            Text(trip.rangeLong)
                .font(Theme.serif(21, relativeTo: .title3))
                .foregroundStyle(Theme.ink)
                .padding(.horizontal, 18)
                .padding(.vertical, 16)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
        }
    }

    private var nightsStepper: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text("How many nights").font(.footnote).foregroundStyle(Theme.muted)
                Text("\(trip.nights) night\(trip.nights == 1 ? "" : "s")").foregroundStyle(Theme.ink)
            }
            Spacer()
            RoundIcon(name: "minus", disabled: trip.nights <= 1) { trip.nights = max(1, trip.nights - 1) }
                .accessibilityLabel("One night fewer")
            RoundIcon(name: "plus", disabled: trip.nights >= 30) { trip.nights = min(30, trip.nights + 1) }
                .accessibilityLabel("One night more")
        }
        .padding(.horizontal, 18)
        .padding(.vertical, 10)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
    }
}

/// The next 40 days in a strip: the first and last day in amber, the days between warm.
struct DateStrip: View {
    @Binding var trip: Trip
    let custom: Bool

    private var days: [Date] {
        let today = Calendar.london.startOfDay(for: .now)
        return (0..<40).compactMap { Calendar.london.date(byAdding: .day, value: $0, to: today) }
    }

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(Array(days.enumerated()), id: \.offset) { i, day in
                        dayButton(day, first: i == 0).id(Dates.isoDay.string(from: day))
                    }
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 4)
            }
            .onAppear { proxy.scrollTo(trip.start, anchor: .leading) }   // the first day in view, not today
        }
    }

    private func dayButton(_ day: Date, first: Bool) -> some View {
        let iso = Dates.isoDay.string(from: day)
        let isStart = iso == trip.start
        let isEnd = trip.nights > 0 && iso == trip.end
        let inRange = iso > trip.start && iso < trip.end
        let showMonth = first || Calendar.london.component(.day, from: day) == 1
        return Button {
            Haptics.light()
            if custom, iso > trip.start {
                let n = Calendar.london.dateComponents([.day], from: trip.startDate, to: day).day ?? trip.nights
                trip.nights = min(max(n, 1), 30)
            } else {
                trip.start = iso
            }
        } label: {
            VStack(spacing: 2) {
                Text(Dates.weekdayShort.string(from: day)).font(.caption).opacity(0.8)
                Text(Dates.dayNum.string(from: day)).font(.title3.weight(.semibold))
                Text(showMonth ? Dates.monthShort.string(from: day) : " ").font(.caption2).opacity(0.8)
            }
            .foregroundStyle(isStart || isEnd ? Theme.onAccent : Theme.ink)
            .frame(width: 52, height: 74)
            .background(isStart || isEnd ? Theme.accent : (inRange ? Color(hex: 0x3A2F1C) : Theme.surface),
                        in: RoundedRectangle(cornerRadius: 16))
        }
        .buttonStyle(PressStyle())
        .accessibilityLabel(Dates.dayName.string(from: day))
        .accessibilityAddTraits(isStart || isEnd ? .isSelected : [])
    }
}

struct FromStep: View {
    @Binding var trip: Trip
    @Binding var showAirports: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            PageTitle(text: "Getting there", font: Theme.h1)
            VStack(spacing: 0) {
                Button { showAirports = true } label: {
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Flying from").font(.footnote).foregroundStyle(Theme.muted)
                            Text(trip.origin?.label ?? "Choose an airport")
                                .foregroundStyle(trip.needFlight ? Theme.ink : Color(hex: 0x7A746B))
                        }
                        Spacer(minLength: 8)
                        Text(trip.originGuessed ? "From your answers" : "Change")
                            .font(.footnote)
                            .foregroundStyle(trip.originGuessed ? Theme.muted : Theme.accent)
                    }
                    .padding(.horizontal, 18)
                    .padding(.vertical, 16)
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
                Rectangle().fill(Theme.hairline).frame(height: 1)
                Toggle(isOn: Binding(get: { !trip.needFlight }, set: { trip.needFlight = !$0 })) {
                    Text("I don't need a flight").foregroundStyle(Theme.ink)
                }
                .tint(Theme.amberDeep)
                .padding(.horizontal, 18)
                .padding(.vertical, 12)
            }
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Who's going").font(.footnote).foregroundStyle(Theme.muted)
                    Text("\(trip.adults) \(trip.adults == 1 ? "adult" : "adults")").foregroundStyle(Theme.ink)
                }
                Spacer()
                RoundIcon(name: "minus", disabled: trip.adults <= 1) { trip.adults = max(1, trip.adults - 1) }
                    .accessibilityLabel("Fewer travellers")
                RoundIcon(name: "plus", disabled: trip.adults >= 6) { trip.adults = min(6, trip.adults + 1) }
                    .accessibilityLabel("More travellers")
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 12)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
        }
    }
}

struct FeelStep: View {
    @Binding var trip: Trip

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            PageTitle(text: "How should the trip feel?", font: Theme.h1)
            Text("Pick one or two. They shape every day of this trip.")
                .foregroundStyle(Theme.muted)
                .padding(.bottom, 4)
            ForEach(TripFeelings.all, id: \.key) { f in
                OptionTile(label: f.label, sub: f.line, on: trip.feelings.contains(f.key), serif: true,
                           offFill: Theme.surface, offStroke: .clear) {
                    if let i = trip.feelings.firstIndex(of: f.key) {
                        trip.feelings.remove(at: i)
                    } else {
                        trip.feelings = Array((trip.feelings + [f.key]).suffix(2))
                    }
                }
            }
        }
    }
}

/// "Flying from": type a town, city or airport code.
struct AirportPicker: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let onPick: (TripPlace) -> Void
    @State private var query = ""
    @State private var found: [TripPlace] = []

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 12) {
                LineField(placeholder: "A town, city or airport", text: $query)
                    .textInputAutocapitalization(.words)
                    .autocorrectionDisabled()
                ScrollView {
                    VStack(spacing: 0) {
                        ForEach(found) { place in
                            Button {
                                onPick(place)
                                dismiss()
                            } label: {
                                HStack {
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(place.city).foregroundStyle(Theme.ink)
                                        Text(place.name).font(.footnote).foregroundStyle(Theme.muted)
                                    }
                                    Spacer()
                                    Text(place.code).font(.subheadline.weight(.semibold)).foregroundStyle(Theme.accent)
                                }
                                .frame(minHeight: 56)
                                .contentShape(Rectangle())
                            }
                            .buttonStyle(.plain)
                            Rectangle().fill(Theme.hairline).frame(height: 1)
                        }
                    }
                }
            }
            .padding(.horizontal, 24)
            .padding(.top, 12)
            .background(Theme.background)
            .serifTitle("Flying from")
            .toolbar {
                ToolbarItem(placement: .topBarLeading) { Button("Cancel") { dismiss() } }
            }
            .task(id: query) {
                try? await Task.sleep(for: .milliseconds(250))
                if !Task.isCancelled, let places = try? await model.client.places(query) { found = places }
            }
        }
    }
}

// ---- the trip: getting there, where you'll stay, your days, the total --------------------------------------------

struct TripOverview: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let tripId: UUID
    var onHelp: () -> Void = {}
    @State private var confirmDelete = false

    var body: some View {
        ScrollView {
            if let trip = model.findTrip(tripId) {
                content(trip)
            } else {
                Text("This trip isn't on this phone any more.")
                    .foregroundStyle(Theme.muted)
                    .padding(24)
            }
        }
        .background(Theme.background)
        .toolbar(.hidden, for: .navigationBar)
        .statusBarShade()
        .confirmationDialog("Delete this trip?", isPresented: $confirmDelete, titleVisibility: .visible) {
            Button("Delete the trip", role: .destructive) {
                model.deleteTrip(tripId)
                dismiss()
            }
            Button("Keep it", role: .cancel) {}
        } message: {
            Text("It's removed from this phone. Anything you booked stays booked on the provider's site.")
        }
    }

    private func content(_ trip: Trip) -> some View {
        VStack(alignment: .leading, spacing: 18) {
            HStack {
                BackLink { dismiss() }
                Spacer()
                HelpPill(action: onHelp)
            }
            Eyebrow("\(trip.range) · \(trip.lengthLabel)")
            PageTitle(text: trip.city, font: Theme.display)
            Text(trip.feelLine).font(.subheadline).foregroundStyle(Theme.inkSoft)
            if trip.needFlight {
                TripStepCard(label: "1 · Getting there", status: .of(trip.flight),
                             title: trip.flight?.title ?? "Choose your flight", sub: flightSub(trip)) {
                    openBook(trip, .flights)
                }
            }
            if trip.needStay {
                TripStepCard(label: "\(trip.needFlight ? 2 : 1) · Where you'll stay", status: .of(trip.stay),
                             title: trip.stay?.title ?? "Choose where to stay", sub: staySub(trip)) {
                    openBook(trip, .stays)
                }
            }
            HStack(alignment: .firstTextBaseline) {
                SectionLabel(text: "\(1 + (trip.needFlight ? 1 : 0) + (trip.needStay ? 1 : 0)) · Your days")
                Spacer()
                Text("\(trip.dayCount) day\(trip.dayCount == 1 ? "" : "s")").font(.subheadline).foregroundStyle(Theme.muted)
            }
            .padding(.top, 8)
            if trip.daysStale {
                SecondaryButton(title: model.busy ? "Planning…" : "Plan the days again from your stay and flight",
                                disabled: model.busy) {
                    Task { await model.replanDays(trip.id) }
                }
            }
            VStack(spacing: 0) {
                ForEach(0..<trip.dayCount, id: \.self) { i in
                    TripDayLine(trip: trip, index: i)
                }
            }
            TripTotal(trip: trip, flights: model.book.resultsFor == trip.id ? model.book.flights : nil,
                      stays: model.book.resultsFor == trip.id ? model.book.stays : nil)
            QuietButton("Delete this trip") { confirmDelete = true }
        }
        .padding(.horizontal, 24)
        .padding(.top, 8)
        .padding(.bottom, 40)
    }

    private func flightSub(_ trip: Trip) -> String {
        if let f = trip.flight { return "\(f.provider) · \(Money.whole(f.price))" }
        guard let origin = trip.origin else { return "Choose where you're flying from" }
        if model.book.resultsFor == trip.id, let r = model.book.flights, let low = r.facets.price?.first {
            return "From \(Money.whole(low)) · \(r.total) options from \(origin.city)"
        }
        return "Search flights from \(origin.city)"
    }

    private func staySub(_ trip: Trip) -> String {
        if let s = trip.stay { return "\(s.provider) · \(Money.whole(s.price)) for \(trip.lengthLabel)" }
        if model.book.resultsFor == trip.id, let r = model.book.stays, let low = r.facets.priceNight?.first {
            return "From \(Money.whole(low)) a night · \(r.total) places"
        }
        return "Hotels, flats and hostels, from where your days happen"
    }

    private func openBook(_ trip: Trip, _ segment: BookState.Segment) {
        model.currentTripId = trip.id
        model.book.segment = segment
        model.tab = .book
    }
}

struct TripStepCard: View {
    let label: String
    let status: StatusLabel
    let title: String
    let sub: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    SectionLabel(text: label)
                    Spacer()
                    status
                }
                Text(title)
                    .font(Theme.serif(22, relativeTo: .title3))
                    .foregroundStyle(Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                Text(sub)
                    .font(.subheadline)
                    .foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .multilineTextAlignment(.leading)
            .padding(18)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 22))
        }
        .buttonStyle(PressStyle())
    }
}

/// One day of the trip: its date, its line, and whether it's ready.
struct TripDayLine: View {
    @Environment(AppModel.self) private var model
    let trip: Trip
    let index: Int

    var body: some View {
        let day = trip.days.first { $0.index == index }
        let date = Calendar.london.date(byAdding: .day, value: index, to: trip.startDate) ?? trip.startDate
        VStack(spacing: 0) {
            if day != nil {
                NavigationLink(value: TripDest.tripDay(trip.id, index)) { row(day, date) }
                    .buttonStyle(PressStyle())
            } else {
                Button { Task { await model.planDay(trip.id, index) } } label: { row(day, date) }
                    .buttonStyle(PressStyle())
                    .disabled(model.busy)
            }
            Rectangle().fill(Theme.hairline).frame(height: 1)
        }
    }

    private func row(_ day: TripDayOut?, _ date: Date) -> some View {
        HStack(alignment: .top, spacing: 14) {
            VStack(spacing: 0) {
                Text(Dates.weekdayShort.string(from: date)).font(.caption).foregroundStyle(Theme.muted)
                Text(Dates.dayNum.string(from: date)).font(.title3.weight(.semibold)).foregroundStyle(Theme.ink)
            }
            .frame(width: 46)
            .padding(.top, 2)
            VStack(alignment: .leading, spacing: 3) {
                Text(day?.title ?? "Planned as you go")
                    .foregroundStyle(Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                Text(note(day))
                    .font(.footnote)
                    .foregroundStyle(day?.plan != nil ? Theme.accent : Theme.muted)
            }
            .multilineTextAlignment(.leading)
            Spacer(minLength: 0)
        }
        .padding(.vertical, 14)
        .contentShape(Rectangle())
    }

    private func note(_ day: TripDayOut?) -> String {
        guard let day else { return model.busy ? "Planning…" : "Plan this day" }
        return day.plan != nil ? "Ready" : "Nothing planned: a travel day"
    }
}

/// "Trip so far": what's chosen, what it starts from, and the days planned. Only numbers we have; never a guess.
struct TripTotal: View {
    let trip: Trip
    let flights: FlightResults?
    let stays: StayResults?

    private var rows: [(String, String, Double?)] {
        var out: [(String, String, Double?)] = []
        if trip.needFlight {
            if let f = trip.flight {
                out.append(("Flight", Money.whole(f.price), f.price))
            } else if let low = flights?.facets.price?.first {
                out.append(("Flight", "from \(Money.whole(low))", low))
            } else {
                out.append(("Flight", "not chosen yet", nil))
            }
        }
        if trip.needStay {
            if let s = trip.stay {
                out.append(("Stay · \(trip.lengthLabel)", Money.whole(s.price), s.price))
            } else if let low = stays?.facets.priceNight?.first {
                let total = low * Double(trip.nights)
                out.append(("Stay · \(trip.lengthLabel)", "from \(Money.whole(total))", total))
            } else {
                out.append(("Stay · \(trip.lengthLabel)", "not chosen yet", nil))
            }
        }
        let days = trip.days.compactMap { $0.plan?.totals?.costGbp }
        if !days.isEmpty {
            let total = days.reduce(0, +) * Double(trip.adults)
            out.append(("Days out (\(days.count) planned)", Money.whole(total), total))
        }
        return out
    }

    var body: some View {
        let r = rows
        let sum = r.compactMap { $0.2 }.reduce(0, +)
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                Text("Trip so far").font(.subheadline).foregroundStyle(Theme.muted)
                Spacer()
                Text(Money.whole(sum)).font(Theme.serif(28, relativeTo: .title)).foregroundStyle(Theme.ink)
            }
            ForEach(r.indices, id: \.self) { i in
                HStack {
                    Text(r[i].0)
                    Spacer()
                    Text(r[i].1)
                }
                .font(.subheadline)
                .foregroundStyle(Theme.inkSoft)
            }
        }
        .padding(18)
        .overlay(RoundedRectangle(cornerRadius: 20).stroke(Theme.outline, lineWidth: 1))
        .accessibilityElement(children: .combine)
    }
}

/// One day of a trip: its stops, and "Make this my day" for "Now", rating, swap and regenerate.
struct TripDayView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let tripId: UUID
    let index: Int

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                BackLink { dismiss() }
                if let trip = model.findTrip(tripId) {
                    let day = trip.days.first { $0.index == index }
                    let date = Calendar.london.date(byAdding: .day, value: index, to: trip.startDate) ?? trip.startDate
                    Eyebrow("Day \(index + 1) · \(Dates.dayShort.string(from: date))")
                    Text(day?.title ?? "Planned as you go")
                        .font(Theme.serif(30, relativeTo: .title))
                        .foregroundStyle(Theme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                        .accessibilityAddTraits(.isHeader)
                    if let day, let plan = day.plan {
                        ForEach(plan.stops) { stop in TripDayStop(stop: stop) }
                        PrimaryButton(title: model.plan?.id == plan.id ? "This is your day" : "Make this my day",
                                      disabled: model.plan?.id == plan.id) {
                            model.useDay(trip, day)
                            var p = NavigationPath()
                            p.append(TripDest.day)
                            model.path = p
                        }
                        Text("Your day gets \"Now\", a nudge to rate each stop, and swapping a stop.")
                            .font(.footnote)
                            .foregroundStyle(Theme.muted)
                    } else if day == nil {
                        PrimaryButton(title: model.busy ? "Planning…" : "Plan this day", disabled: model.busy) {
                            Task { await model.planDay(tripId, index) }
                        }
                    } else {
                        Text("A travel day: nothing is planned, so you can take it easy.")
                            .foregroundStyle(Theme.inkSoft)
                            .padding(20)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .overlay(RoundedRectangle(cornerRadius: 20).stroke(Theme.outline, lineWidth: 1))
                    }
                }
            }
            .padding(.horizontal, 24)
            .padding(.top, 8)
            .padding(.bottom, 40)
        }
        .background(Theme.background)
        .toolbar(.hidden, for: .navigationBar)
        .statusBarShade()
    }
}

struct TripDayStop: View {
    let stop: Stop

    var body: some View {
        HStack(alignment: .top, spacing: 14) {
            Color.clear
                .frame(width: 70)
                .frame(minHeight: 84, maxHeight: .infinity)
                .overlay { MomentImage(momentId: stop.momentId, feel: stop.feelWord) }
                .clipShape(RoundedRectangle(cornerRadius: 14))
            VStack(alignment: .leading, spacing: 4) {
                Text("\(stop.arrive) · \(stop.word)").font(.footnote).foregroundStyle(Theme.muted)
                Text(stop.title)
                    .font(Theme.serif(20, relativeTo: .title3))
                    .foregroundStyle(Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                Text(stop.reasons?.first?.you ?? stop.what)
                    .font(.subheadline)
                    .foregroundStyle(Theme.inkSoft)
                    .lineLimit(3)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 0)
        }
        .fixedSize(horizontal: false, vertical: true)
        .padding(12)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 20))
        .accessibilityElement(children: .combine)
    }
}

// ---- You -------------------------------------------------------------------------------------------------------

/// The You tab: safety first (999, then a person), what the app has learned in plain words, and your data.
struct YouView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.openURL) private var openURL
    @State private var showSafety = false
    @State private var showSettings = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                PageTitle(text: "You", font: Theme.serif(36, relativeTo: .largeTitle))
                    .padding(.top, 30)
                VStack(alignment: .leading, spacing: 12) {
                    Text("Emergency in the UK").font(.headline).foregroundStyle(Theme.emergencyTitle)
                    Text("If you or someone else is in danger, call 999 first.")
                        .foregroundStyle(Theme.emergencyText)
                    Button("Call 999") { if let url = URL(string: "tel://999") { openURL(url) } }
                        .buttonStyle(PillStyle(kind: .danger, height: 52))
                }
                .padding(18)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Theme.emergencyBg, in: RoundedRectangle(cornerRadius: 20))
                .overlay(RoundedRectangle(cornerRadius: 20).stroke(Theme.emergencyBorder, lineWidth: 1))
                Button { showSafety = true } label: {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Talk to a person").font(.headline).foregroundStyle(Theme.ink)
                            Spacer()
                            if model.unreadSafety { Circle().fill(Theme.danger).frame(width: 9, height: 9) }
                        }
                        Text("Something wrong with a stop, a booking or how you feel? A real person replies here, within a few hours.")
                            .font(.subheadline)
                            .foregroundStyle(Theme.inkTertiary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .multilineTextAlignment(.leading)
                    .surfaceCard(padding: 18, radius: 20)
                }
                .buttonStyle(PressStyle())
                VStack(alignment: .leading, spacing: 2) {
                    SectionLabel(text: "What I've learned about you").padding(.bottom, 6)
                    let items = model.learned?.items ?? []
                    if items.isEmpty {
                        Text("Nothing yet. It comes from your answers and your ratings.")
                            .foregroundStyle(Theme.muted)
                            .padding(.vertical, 12)
                    }
                    ForEach(items) { item in
                        VStack(alignment: .leading, spacing: 0) {
                            Text(item.text)
                                .font(Theme.serif(19, relativeTo: .body))
                                .foregroundStyle(Theme.ink)
                                .fixedSize(horizontal: false, vertical: true)
                                .padding(.vertical, 12)
                            Rectangle().fill(Theme.hairline).frame(height: 1)
                        }
                    }
                }
                Button { showSettings = true } label: {
                    HStack {
                        Text("Your data · what's stored and how to delete it")
                        Spacer()
                        Image(systemName: "chevron.right").font(.footnote)
                    }
                    .foregroundStyle(Theme.muted)
                    .frame(minHeight: 44)
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 40)
        }
        .background(Theme.background)
        .statusBarShade()
        .sheet(isPresented: $showSafety) { SafetyView() }
        .sheet(isPresented: $showSettings) { SettingsView() }
        .task {
            await model.loadSafety()
            if model.learned == nil { model.learned = try? await model.client.summary() }
        }
    }
}

// ---- CI screenshots (`-demo YES -screen <name>`): D120 and Build 2, with the bundled demo data --------------------

struct TripDemoScreen: View {
    @Environment(AppModel.self) private var model
    let name: String

    var body: some View {
        switch name {
        case "survey": SurveyView().background(Theme.background)                          // 15
        case "pairintent": PairIntentView().background(Theme.background)                  // 16
        case "pair":                                                                      // 17a
            if let pair = Self.pair("demo_pair") { PairCompare(pair: pair).background(Theme.background) }
        case "pair2":                                                                     // 17b: both read, the questions
            if let pair = Self.pair("demo_pair") { PairCompare(pair: pair, demoQuestions: true).background(Theme.background) }
        case "pairreveal":                                                                // 18
            if let pair = Self.pair("demo_pair_done") { PairReveal(pair: pair) }
        case "tripwhere", "tripwhen", "tripfrom", "tripfeel":                             // 20-23
            if let trip = model.trips.first {
                TripCreateFlow(trip: trip, editing: false,
                               startAt: ["tripwhere": 0, "tripwhen": 1, "tripfrom": 2, "tripfeel": 3][name] ?? 0)
            }
        case "trip", "tripday":                                                           // 24, 25
            MainTabs().onAppear {
                guard let id = model.trips.first?.id else { return }
                var p = NavigationPath()
                p.append(TripDest.trip(id))
                if name == "tripday" { p.append(TripDest.tripDay(id, 1)) }
                model.path = p
            }
        case "flights", "flightfilters", "stays", "staysmap", "stayfilters":              // 26, 27, 29-31
            MainTabs().onAppear {
                model.book.segment = name.hasPrefix("flight") ? .flights : .stays
                model.book.stayMap = name == "staysmap"
                model.tab = .book
                if name.hasSuffix("filters") { model.book.showFilters = true }
            }
        case "flight", "handoff", "handoffback":                                          // 28, 28a, 28b
            if let f = model.book.flights?.results.first {
                NavigationStack { FlightDetailView(flight: f) }
                    .sheet(isPresented: .constant(name != "flight")) {
                        HandoffSheet().presentationDetents([.medium])
                    }
                    .onAppear { if name != "flight" { model.book.handoff = Self.handoff(f, back: name == "handoffback") } }
            }
        case "stay":                                                                      // 32
            if let s = model.book.stays?.results.first { NavigationStack { StayDetailView(stay: s) } }
        case "you": MainTabs().onAppear { model.tab = .you }                              // 33
        default: MainTabs()                                                               // 19 ("triphome")
        }
    }

    static func pair(_ file: String) -> PairResponse? { try? BrainClient.bundled(file) }

    static func handoff(_ f: Flight, back: Bool) -> Handoff {
        var h = Handoff(provider: "Skyscanner", url: URL(string: "https://www.skyscanner.net")!, what: "Return flight",
                        price: f.price, searchedAt: Date.now.addingTimeInterval(-120),
                        choice: TripChoice(kind: "flight", title: f.airline, provider: "Skyscanner", price: f.price,
                                           booked: false))
        h.back = back
        return h
    }
}
