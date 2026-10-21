import SwiftUI
import UIKit

// D120: the ODYS Trips design (Abram's "ODYS Trips" file): "Plan a trip" in five questions (D122 added "Your days"),
// the trip as a checklist (getting there, where you'll stay, your days) and a running total. What differs from the
// design, and why, is in decisions/decision-log.md (D121). D131: its three tabs became one home that follows the time.

// ---- the living home (D131: shape A) -----------------------------------------------------------------------

/// Home after onboarding (D131, shape A): no tabs. One home that follows the time: before a day it offers a day out or
/// a trip; on the day it is the day; afterwards it holds what you rated. Flights and stays open inside a trip; You,
/// your data and the light sit behind the menu, and Help stays one tap away. Before the first plan, people in the UK
/// get the survey and the blind pair (Build 2) first.
struct LivingHome: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        @Bindable var model = model
        if model.needsFirstRun {
            FirstPlanFlow()
        } else {
            HomeView()
                .fullScreenCover(isPresented: $model.showCreate, onDismiss: { model.editingTrip = nil; model.editStep = nil }) {
                    TripCreateFlow(trip: model.editingTrip ?? model.newTrip(), editing: model.editingTrip != nil,
                                   startAt: model.editStep)
                        .brainFeedback()
                }
                .fullScreenCover(isPresented: $model.showPair) { PairFlow().brainFeedback() }
        }
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

    static func of(_ choice: TripChoice?, fits: Bool = true) -> StatusLabel {
        guard let choice else { return StatusLabel(text: "To do", fill: Theme.surfaceHigh, color: Theme.inkSoft) }
        if !fits {   // journey audit: the trip's dates changed after this was chosen
            return StatusLabel(text: "For other dates", fill: Theme.warnBg, color: Theme.warnInk)
        }
        return choice.booked ? StatusLabel(text: "Booked", fill: Theme.okBg, color: Theme.okInk)
                             : StatusLabel(text: "Saved, not booked", fill: Theme.savedBg, color: Theme.accent)
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

// ---- home ---------------------------------------------------------------------------------------------

/// "Where to next?": one big action (Plan a trip), then your day and your trips underneath.
/// The home (D131, shape A): it follows the time. On the day, the day leads (its path, and one button back to "Now");
/// once it's done, what you rated; then "Where to next?" with a day out and a trip as equals (D129).
struct TripHome: View {
    @Environment(AppModel.self) private var model
    var onHelp: () -> Void = {}
    var onData: () -> Void = {}
    @State private var planningDay = false

    var body: some View {
        let _ = model.clock   // journey round 2: Today / Tomorrow and the greeting follow the date after a night away
        let phase = model.homePhase
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                TopBar(eyebrow: AppModel.greeting, onHelp: onHelp, onMenu: { model.path.append(TripDest.you) })
                if let plan = model.plan, phase == .today { TodayHome(plan: plan) }
                if let plan = model.plan, phase == .after { MemoriesCard(plan: plan) }
                PageTitle(text: phase == .before ? "Where to next?" : "And next?",
                          font: phase == .before ? Theme.display : Theme.h1).settle(1)
                if phase != .today, let today = model.todayInTrip {   // journey audit: during a trip, today comes first
                    TodayInTripCard(trip: today.trip, index: today.index, day: today.day).settle(1)
                } else if let next = model.tomorrowInTrip {   // Abram's comment (8 Oct): then tomorrow, to look ahead
                    TomorrowInTripCard(trip: next.trip, index: next.index, day: next.day).settle(1)
                }
                // D129: a day out and a trip are equals, side by side; people abroad see the trip first
                HStack(alignment: .top, spacing: 12) {
                    if model.isVisitor {
                        tripCard
                        dayOutCard
                    } else {
                        dayOutCard
                        tripCard
                    }
                }
                .fixedSize(horizontal: false, vertical: true)
                .settle(2)
                if let plan = model.plan, phase == .before {
                    VStack(alignment: .leading, spacing: 10) {
                        Text((plan.date ?? "") < Dates.isoDay.string(from: .now) ? "Your last day out" : "Coming up")
                            .font(.subheadline).foregroundStyle(Theme.muted)
                        NavigationLink(value: TripDest.day) { DayRow(plan: plan) }
                            .buttonStyle(PressStyle())
                    }
                    .settle(3)
                }
                if !model.isVisitor, !model.pairDone, !model.client.demo {
                    PairInviteRow { model.showPair = true }.settle(3)
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
        .skyBackground()
        .sheet(isPresented: $planningDay) {
            NavigationStack {
                PlanFormView(onDone: { planningDay = false })
                    .toolbar {
                        ToolbarItem(placement: .topBarTrailing) { Button("Close") { planningDay = false } }
                    }
            }
            .brainFeedback()
        }
    }

    private var dayOutCard: some View {
        ChoiceCard(title: "A day out", text: "In London, around what you enjoy: your hours, your start, places that fit you.",
                   icon: "sun.max", lead: !model.isVisitor) { planningDay = true }
    }

    private var tripCard: some View {
        ChoiceCard(title: "A trip", text: "A few days away: getting there, a place to stay, and days that fit you.",
                   icon: "airplane", lead: model.isVisitor) { model.showCreate = true }
    }
}

/// D129: a day out or a trip, as two equal cards. The one that leads for this person is lit a little.
struct ChoiceCard: View {
    let title: String
    let text: String
    let icon: String
    let lead: Bool
    let action: () -> Void

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            VStack(alignment: .leading, spacing: 8) {
                Image(systemName: icon).font(.title2).foregroundStyle(Theme.accent)
                Text(title).font(Theme.serif(23, relativeTo: .title3)).foregroundStyle(Theme.ink)
                Text(text).font(.subheadline).foregroundStyle(Theme.inkTertiary)
                    .fixedSize(horizontal: false, vertical: true)
                Spacer(minLength: 0)
            }
            .multilineTextAlignment(.leading)
            .padding(18)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
            .background(lead ? Theme.selected : Theme.surface, in: RoundedRectangle(cornerRadius: 22))
            .overlay(RoundedRectangle(cornerRadius: 22).stroke(lead ? Theme.accent.opacity(0.35) : Theme.outline, lineWidth: 1))
        }
        .buttonStyle(PressStyle())
        .accessibilityElement(children: .combine)
        .accessibilityAddTraits(.isButton)
    }
}

/// D131, on the day: the day's path with where you've got to, the stops and times under it, and one way back to
/// "Now". The whole plan is one tap away.
struct TodayHome: View {
    @Environment(AppModel.self) private var model
    let plan: Plan

    var body: some View {
        let i = model.dayProgress(plan)
        VStack(alignment: .leading, spacing: 14) {
            Eyebrow("Today · " + Dates.shortDay(plan.date ?? Dates.isoDay.string(from: .now)))
            Text(plan.homeHeadline).font(Theme.h1).foregroundStyle(Theme.ink)
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityAddTraits(.isHeader)
            VStack(alignment: .leading, spacing: 4) {
                DayPath(stops: plan.stops, current: i, height: 170)
                ForEach(Array(plan.stops.enumerated()), id: \.element.id) { j, stop in
                    PathStopRow(index: j, stop: stop, done: j < i, here: j == i, first: j == 0)
                }
            }
            .surfaceCard(padding: 16, radius: 24)
            PrimaryButton(title: i == 0 ? "Start the day" : "Back to now") { model.startDay() }
            QuietButton("See the whole day") { model.path.append(TripDest.day) }
                .frame(maxWidth: .infinity)
        }
        .settle(0)
    }
}

/// A stop under the path: its number, name, time and the word for how it moves the day.
struct PathStopRow: View {
    let index: Int
    let stop: Stop
    let done: Bool
    let here: Bool
    let first: Bool

    var body: some View {
        VStack(spacing: 0) {
            if !first { Rectangle().fill(Theme.hairline).frame(height: 1) }
            HStack(spacing: 12) {
                Text("\(index + 1)")
                    .font(.footnote.weight(.semibold))
                    .foregroundStyle(here || done ? Theme.onAccent : Theme.accent)
                    .frame(width: 28, height: 28)
                    .background(Circle().fill(here || done ? Theme.accent : .clear))
                    .overlay(Circle().stroke(Theme.accent, lineWidth: 1.5))
                VStack(alignment: .leading, spacing: 2) {
                    Text(stop.title).foregroundStyle(done ? Theme.inkTertiary : Theme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                    Text([stop.arrive, stop.feelWord].compactMap { $0 }.joined(separator: " · "))
                        .font(.footnote).foregroundStyle(Theme.muted)
                }
                Spacer(minLength: 0)
            }
            .frame(minHeight: 52)
            .accessibilityElement(children: .combine)
            .accessibilityValue(here ? "You're here" : (done ? "Done" : ""))
        }
    }
}

/// D131, after the day: what you rated, in your own words (Disappointing … Unforgettable).
struct MemoriesCard: View {
    @Environment(AppModel.self) private var model
    let plan: Plan

    private var label: String {
        let d = plan.date ?? ""
        if d == Dates.isoDay.string(from: .now) { return "Earlier today" }
        if d == Dates.isoDay.string(from: Date.now.addingTimeInterval(-86400)) { return "Yesterday" }
        return Dates.longDay(d) ?? "Your day"
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Eyebrow(label)
            Text(plan.homeHeadline).font(Theme.h1).foregroundStyle(Theme.ink)
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityAddTraits(.isHeader)
            ForEach(plan.stops.filter(\.rateable)) { stop in
                HStack(spacing: 12) {
                    Field(feel: stop.feelWord).frame(width: 44, height: 44).clipShape(RoundedRectangle(cornerRadius: 12))
                    VStack(alignment: .leading, spacing: 2) {
                        Text(stop.title).font(.subheadline).foregroundStyle(Theme.ink)
                            .fixedSize(horizontal: false, vertical: true)
                        Text(stop.arrive).font(.footnote).foregroundStyle(Theme.muted)
                    }
                    Spacer(minLength: 8)
                    if let r = model.myRatings[stop.momentId], (1...5).contains(r) {
                        Text(Labels.feel[r - 1]).font(Theme.italic(17, relativeTo: .body)).foregroundStyle(Theme.accent)
                    } else {
                        Text("Not rated").font(.footnote).foregroundStyle(Theme.muted)
                    }
                }
                .padding(10)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
                .accessibilityElement(children: .combine)
            }
            QuietButton("See the day") { model.path.append(TripDest.day) }
                .frame(maxWidth: .infinity)
        }
        .settle(0)
    }
}

extension Plan {
    /// D131: the day's own headline on the home ("A curious, peaceful day"), never on the blind Test B pair.
    var homeHeadline: String {
        let text = !isBlind && !(feelLine ?? "").isEmpty ? feelLine! : (title ?? "Your day")
        return text.headlineParts.0
    }
}

/// Journey audit (7 Oct): "Today · Day 3 of your London trip", one tap to make it your day (and plan it first if it's
/// one of the later days planned as you go). Nothing to find in the trip each morning.
struct TodayInTripCard: View {
    @Environment(AppModel.self) private var model
    let trip: Trip
    let index: Int
    let day: TripDayOut?
    @State private var confirm = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Eyebrow("Today · Day \(index + 1) of \(trip.dayCount)")
            Text(day?.title ?? "Your \(trip.city) trip")
                .font(Theme.serif(24, relativeTo: .title2))
                .foregroundStyle(Theme.ink)
                .fixedSize(horizontal: false, vertical: true)
            if let first = day?.plan?.stops.first {
                Text("First: \(first.title), around \(first.arrive)")
                    .font(.subheadline)
                    .foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
            }
            PrimaryButton(title: model.busy ? "Planning…" : (day == nil ? "Plan today" : day?.plan == nil ? "See today" : "Start today"),
                          disabled: model.busy) {
                // journey round 2: a travel or free day has nothing to start: its page shows the journeys
                if day != nil, day?.plan == nil { model.openTripDay(trip.id, index, from: "today") }
                else if model.testBPlanAtRisk { confirm = true } else { start() }
            }
        }
        .surfaceCard(padding: 20)
        .confirmReplacingTestBPlan($confirm) { start() }
    }

    private func start() {
        Task {
            await model.goToTripDay(trip.id, index)
            if model.plan?.date == Dates.isoDay.string(from: .now) { model.path.append(TripDest.day) }
        }
    }
}

/// Abram's comment (8 Oct): "Tomorrow · Day 3 of 6", once today is under way (or the evening before the trip). One tap
/// to look at it, so there's time to say "I'm meeting someone" and have the day planned around it.
struct TomorrowInTripCard: View {
    @Environment(AppModel.self) private var model
    let trip: Trip
    let index: Int
    let day: TripDayOut?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Eyebrow("Tomorrow · Day \(index + 1) of \(trip.dayCount)")
            Text(day?.title ?? "Your \(trip.city) trip")
                .font(Theme.serif(24, relativeTo: .title2))
                .foregroundStyle(Theme.ink)
                .fixedSize(horizontal: false, vertical: true)
            if let first = day?.plan?.stops.first {
                Text("First: \(first.title), around \(first.arrive)")
                    .font(.subheadline)
                    .foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Text("Made other plans? Change the day's hours, and I'll plan around them.")
                .font(.footnote)
                .foregroundStyle(Theme.muted)
                .fixedSize(horizontal: false, vertical: true)
            SecondaryButton(title: model.busy ? "Planning…" : (day == nil ? "Plan tomorrow" : "See tomorrow"),
                            disabled: model.busy) {
                Task {
                    await model.planTripDayIfNeeded(trip.id, index)
                    model.openTripDay(trip.id, index, from: "home")
                }
            }
        }
        .surfaceCard(padding: 20)
    }
}

/// D123: "Good to know" on a trip: entry rules for flights from abroad, getting around London, bags and signal.
/// Entry rules are general information and links to GOV.UK, the same for everyone flying in from abroad (decided by
/// the departure airport, never by nationality). It never says whether this person needs a visa: that would be
/// immigration advice, which is regulated (Immigration Advice Authority practice note, July 2025).
struct TripGoodToKnow: View {
    let trip: Trip

    var basedAbroad = false   // journey round 2: by where they said they're based (never nationality)
    private var fromAbroad: Bool { (trip.needFlight && (trip.origin?.country ?? "") != "GB") || basedAbroad }

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            SectionLabel(text: "Good to know")
            if fromAbroad {
                KnowItem(title: "Before you fly",
                         text: "Depending on nationality, most visitors to the UK need either a visa or an electronic travel authorisation (ETA, £20 for each traveller, babies included). Check what applies to you on GOV.UK before you book.",
                         links: [KnowLink(label: "Check if you need a visa or an ETA", url: "https://www.gov.uk/check-uk-visa"),
                                 KnowLink(label: "About the ETA", url: "https://www.gov.uk/eta")])
            }
            if fromAbroad {   // journey round 2: from nhs.uk, GOV.UK and TfL (read 8 Oct 2026), the same for everyone
                KnowItem(title: "Health and emergencies",
                         text: "In an emergency, call 999 or 112. For urgent help that isn't life-threatening, call NHS 111. A&E is free for everyone; if you're admitted to hospital, that care can be charged, so GOV.UK advises visitors to have travel or health insurance. Visitors from the EU can use an EHIC.",
                         links: [KnowLink(label: "NHS: using the NHS as a visitor",
                                          url: "https://www.nhs.uk/nhs-services/visiting-or-moving-to-england/how-to-access-nhs-services-in-england-if-you-are-visiting-from-abroad/")])
            }
            KnowItem(title: "Getting around London",
                     text: "Contactless cards, phones and watches work on buses, the Tube, DLR, Overground, the Elizabeth line and most trains. Touch in and out with the same one, one per person: then a daily cap stops you paying more than a set amount (£8.90 in zones 1–2). The Heathrow Express and river buses aren't in the cap, and your bank may charge a fee on each tap with a card from abroad.",
                     links: [KnowLink(label: "TfL: paying with contactless",
                                      url: "https://tfl.gov.uk/fares/how-to-pay-and-where-to-buy-tickets-and-oyster/pay-as-you-go/contactless-and-mobile-pay-as-you-go")])
            if trip.needStay {
                KnowItem(title: "Bags", text: "Most places will hold your bags before check-in and after check-out: ask your stay.", links: [])
            }
            KnowItem(title: "Without signal",
                     text: "Your days and this trip stay on your phone, and ratings wait until you're back online. New plans, Book and directions need data.",
                     links: [])
        }
        .padding(.top, 8)
    }
}

private struct KnowLink: Hashable {
    let label: String
    let url: String
}

private struct KnowItem: View {
    let title: String
    let text: String
    let links: [KnowLink]

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title).font(.headline).foregroundStyle(Theme.ink)
            Text(text).font(.subheadline).foregroundStyle(Theme.inkSoft).fixedSize(horizontal: false, vertical: true)
            ForEach(links, id: \.self) { link in
                if let url = URL(string: link.url) {
                    Link(destination: url) {
                        Text("\(link.label) ↗").font(.subheadline).foregroundStyle(Theme.accent)
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .surfaceCard(padding: 16)
    }
}

/// m176: before a new day replaces the unrated Test B plan ("your Saturday plan").
struct ReplaceTestBPlan: ViewModifier {
    @Binding var isPresented: Bool
    let replace: () -> Void

    func body(content: Content) -> some View {
        content.confirmationDialog("Replace your Saturday plan?", isPresented: $isPresented, titleVisibility: .visible) {
            Button("Replace it") { replace() }
            Button("Keep my Saturday plan", role: .cancel) {}
        } message: {
            Text("You haven't rated it yet. Going on that day and rating each stop helps the test most.")
        }
    }
}

extension View {
    func confirmReplacingTestBPlan(_ isPresented: Binding<Bool>, replace: @escaping () -> Void) -> some View {
        modifier(ReplaceTestBPlan(isPresented: isPresented, replace: replace))
    }
}

struct PlanTripCard: View {
    var title = "Plan a trip"
    var text = "One day or two weeks. I'll find the flight, the stay and the moments, and you book with whichever site you trust."
    let action: () -> Void

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            VStack(alignment: .leading, spacing: 14) {
                ArchMark()
                Text(title)
                    .font(Theme.serif(26, relativeTo: .title2))
                    .foregroundStyle(Theme.ink)
                Text(text)
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
                RadialGradient(colors: [Theme.selected, Theme.surface], center: UnitPoint(x: 0.8, y: 0),
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
    @State private var showAirports = false
    @State private var confirmReplace = false
    let editing: Bool

    init(trip: Trip, editing: Bool, startAt: Int? = nil) {
        _trip = State(initialValue: trip)
        _step = State(initialValue: startAt ?? (editing ? 1 : 0))
        self.editing = editing
    }

    var body: some View {
        VStack(spacing: 0) {
            header
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    switch step {
                    case 0: WhereStep()
                    case 1: WhenStep(trip: $trip)
                    case 2: FromStep(trip: $trip, showAirports: $showAirports)
                    case 3: DaysStep(trip: $trip)
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
            PrimaryButton(title: buttonTitle, disabled: model.busy) {
                // journey round 2: a one-day trip becomes "your day", so the unrated Test B plan asks first
                if step == Self.questions - 1, trip.nights == 0, model.testBPlanAtRisk { confirmReplace = true } else { next() }
            }
                .confirmReplacingTestBPlan($confirmReplace) { next() }
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
            .followsSky()
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
                ForEach(0..<Self.questions, id: \.self) { i in
                    Capsule()
                        .fill(i <= step ? Theme.accent : Theme.track)
                        .frame(width: i == step ? 22 : 6, height: 6)
                }
            }
            .animation(.easeOut(duration: 0.3), value: step)
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("Question \(step + 1) of \(Self.questions)")
            Spacer()
            Color.clear.frame(width: 60, height: 1)
        }
        .padding(.horizontal, 24)
        .padding(.top, 8)
        .padding(.bottom, 8)
        .background(Theme.background)
    }

    private var backTitle: String { step == 0 || (editing && step == 1) ? "Cancel" : "‹ Back" }

    /// Journey round 2: who's going and the airport you fly from change the searches, not the days.
    static func onlySearchChanged(_ old: Trip, _ new: Trip) -> Bool {
        var a = old, b = new
        a.adults = 0; b.adults = 0
        a.origin = nil; b.origin = nil
        a.originGuessed = false; b.originGuessed = false
        a.days = []; b.days = []
        return a == b && (old.adults != new.adults || old.origin != new.origin)
    }

    static let questions = 5

    private var buttonTitle: String {
        if step < Self.questions - 1 { return "Continue" }
        if model.busy { return "Planning your days…" }
        return editing ? "Plan the trip again" : "Make my trip"
    }

    private func next() {
        guard step == Self.questions - 1 else {
            step += 1
            return
        }
        Task {
            let t = trip
            let old = editing ? model.findTrip(trip.id) : nil
            if let old, Self.onlySearchChanged(old, t) {   // journey round 2: travellers or airport only: days stay
                model.save(t)
                model.book.resultsFor = nil
                dismiss()
                return
            }
            if await model.makeTrip(t, keepFrom: old) {
                if editing { model.book.resultsFor = nil }
                dismiss()
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
                Text(name).foregroundStyle(ready ? Theme.ink : Theme.muted)
                Spacer(minLength: 8)
                Text(note).font(.footnote).foregroundStyle(Theme.muted)
            }
            .frame(minHeight: 52)
            .padding(.horizontal, 4)
            Rectangle().fill(Theme.hairline).frame(height: 1)
        }
    }
}

/// Screen 21 (Abram's comment, 8 Oct): "When are you going?" on a calendar, as in Skyscanner and the booking apps.
/// The first tap is the first day and a tap on a later day is the last; one day on its own is a day out. No lengths
/// to choose first, and no counting nights.
struct WhenStep: View {
    @Binding var trip: Trip
    @State private var pickingEnd = false     // after a first tap: the next tap on that day or later is the last day

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            PageTitle(text: "When are you going?", font: Theme.h1)
            Text(pickingEnd ? "Now tap your last day. Tap the same day again for a day out."
                            : "Tap your first day, then your last day.")
                .font(.subheadline)
                .foregroundStyle(Theme.muted)
                .fixedSize(horizontal: false, vertical: true)
                .animation(nil, value: pickingEnd)
            TripCalendar(trip: $trip, pickingEnd: $pickingEnd)
            VStack(alignment: .leading, spacing: 4) {
                Text(trip.rangeLong)
                    .font(Theme.serif(21, relativeTo: .title3))
                    .foregroundStyle(Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                Text(lengthWords)
                    .font(.subheadline)
                    .foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 14)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
            .accessibilityElement(children: .combine)
        }
    }

    /// "A day out", "A weekend: 3 days, 2 nights", "7 days, 6 nights" (up to 30 nights).
    private var lengthWords: String {
        if trip.nights == 0 { return pickingEnd ? "A day out, unless you tap a later day" : "A day out: no stay needed" }
        let days = "\(trip.dayCount) days, \(trip.nights) night\(trip.nights == 1 ? "" : "s")"
        let firstDay = Calendar.london.component(.weekday, from: trip.startDate)   // Sunday 1 … Saturday 7
        return trip.nights <= 2 && (firstDay == 6 || firstDay == 7) ? "A weekend: \(days)" : days
    }
}

/// A month at a time, Monday first: the first and last day in amber, the days between warm. Days before today, more
/// than about 11 months ahead (as far as the Brain plans) or more than 30 nights after the first day can't be tapped.
struct TripCalendar: View {
    @Binding var trip: Trip
    @Binding var pickingEnd: Bool
    @State private var month: Date              // the first of the month on show

    private static let maxNights = 30
    private static let band = Theme.savedBg

    init(trip: Binding<Trip>, pickingEnd: Binding<Bool>) {
        _trip = trip
        _pickingEnd = pickingEnd
        let first = max(trip.wrappedValue.startDate, Calendar.london.startOfDay(for: .now))
        _month = State(initialValue: Self.monthStart(first))
    }

    private var cal: Calendar { Calendar.london }
    private var today: Date { cal.startOfDay(for: .now) }
    private var lastStart: Date { cal.date(byAdding: .day, value: 329, to: today) ?? today }
    private var canGoBack: Bool { month > Self.monthStart(today) }
    private var canGoOn: Bool {
        month < Self.monthStart(cal.date(byAdding: .day, value: Self.maxNights, to: lastStart) ?? lastStart)
    }

    var body: some View {
        VStack(spacing: 8) {
            HStack {
                RoundIcon(name: "chevron.left", disabled: !canGoBack) { shift(-1) }
                    .accessibilityLabel("Previous month")
                Spacer()
                Text(Dates.monthYear.string(from: month))
                    .font(Theme.serif(20, relativeTo: .title3))
                    .foregroundStyle(Theme.ink)
                    .accessibilityAddTraits(.isHeader)
                Spacer()
                RoundIcon(name: "chevron.right", disabled: !canGoOn) { shift(1) }
                    .accessibilityLabel("Next month")
            }
            HStack(spacing: 0) {
                ForEach(Array(["M", "T", "W", "T", "F", "S", "S"].enumerated()), id: \.offset) { _, d in
                    Text(d).font(.caption).foregroundStyle(Theme.muted).frame(maxWidth: .infinity)
                }
            }
            .accessibilityHidden(true)
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 0), count: 7), spacing: 4) {
                ForEach(Array(cells.enumerated()), id: \.offset) { _, day in
                    if let day { dayCell(day) } else { Color.clear.frame(height: 44) }
                }
            }
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 12)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 20))
        .simultaneousGesture(DragGesture(minimumDistance: 30).onEnded { g in   // a sideways swipe turns the page
            guard abs(g.translation.width) > abs(g.translation.height) * 2 else { return }   // not the page scrolling
            if g.translation.width < -40, canGoOn { shift(1) } else if g.translation.width > 40, canGoBack { shift(-1) }
        })
    }

    /// The month's days, after blanks for the days before the 1st (Monday first).
    private var cells: [Date?] {
        let weekday = cal.component(.weekday, from: month)          // Sunday 1 … Saturday 7
        let blanks = (weekday + 5) % 7
        let count = cal.range(of: .day, in: .month, for: month)?.count ?? 30
        return Array(repeating: nil, count: blanks)
            + (0..<count).map { cal.date(byAdding: .day, value: $0, to: month) }
    }

    private func dayCell(_ day: Date) -> some View {
        let iso = Dates.isoDay.string(from: day)
        let isStart = iso == trip.start
        let isEnd = trip.nights > 0 && iso == trip.end
        let inRange = trip.nights > 0 && iso > trip.start && iso < trip.end
        let open = canTap(day)
        return Button { tap(iso, day) } label: {
            ZStack {
                HStack(spacing: 0) {   // the warm band from the first day to the last
                    (isEnd || inRange ? Self.band : Color.clear)
                    ((isStart && trip.nights > 0) || inRange ? Self.band : Color.clear)
                }
                .frame(height: 40)
                if isStart || isEnd {
                    Circle().fill(Theme.accent).frame(width: 40, height: 40)
                } else if day == today {
                    Circle().stroke(Theme.outlineStrong, lineWidth: 1).frame(width: 40, height: 40)
                }
                Text(Dates.dayNum.string(from: day))
                    .font(.body.weight(isStart || isEnd ? .semibold : .regular))
                    .monospacedDigit()
                    .foregroundStyle(isStart || isEnd ? Theme.onAccent : (open ? Theme.ink : Theme.muted.opacity(0.45)))
            }
            .frame(maxWidth: .infinity, minHeight: 44)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .disabled(!open)
        .accessibilityLabel(Dates.dayName.string(from: day))
        .accessibilityValue(isStart ? "First day" : isEnd ? "Last day" : inRange ? "In your trip" : "")
        .accessibilityAddTraits(isStart || isEnd ? .isSelected : [])
    }

    private func canTap(_ day: Date) -> Bool {
        guard day >= today else { return false }
        if pickingEnd, day >= trip.startDate {
            return (cal.dateComponents([.day], from: trip.startDate, to: day).day ?? 0) <= Self.maxNights
        }
        return day <= lastStart
    }

    /// The first tap is the first day; the next tap on that day or later is the last day (the same day: a day out).
    /// A tap on an earlier day, or after a whole trip is chosen, starts again from that day.
    private func tap(_ iso: String, _ day: Date) {
        Haptics.light()
        if pickingEnd, iso >= trip.start {
            trip.nights = min(cal.dateComponents([.day], from: trip.startDate, to: day).day ?? 0, Self.maxNights)
            pickingEnd = false
        } else {
            trip.start = iso
            trip.nights = 0
            pickingEnd = true
        }
    }

    private func shift(_ by: Int) {
        withAnimation(.easeOut(duration: 0.2)) { month = cal.date(byAdding: .month, value: by, to: month) ?? month }
    }

    private static func monthStart(_ d: Date) -> Date {
        let c = Calendar.london
        return c.date(from: c.dateComponents([.year, .month], from: d)) ?? d
    }
}

struct FromStep: View {
    @Binding var trip: Trip
    @Binding var showAirports: Bool

    /// D122: by plane, train or car, or already in London.
    static let ways: [(key: String, label: String)] = [
        ("flight", "Flying"), ("train", "By train"), ("car", "By car"), ("here", "Already in London"),
    ]

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            PageTitle(text: "Getting there", font: Theme.h1)
            LazyVGrid(columns: [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)], spacing: 10) {
                ForEach(Self.ways, id: \.key) { w in
                    OptionTile(label: w.label, on: trip.arrivingBy == w.key, offFill: Theme.surface, offStroke: .clear) {
                        choose(w.key)
                    }
                }
            }
            switch trip.arrivingBy {
            case "flight": flightCard
            case "train": trainCard
            case "car": carCard
            default: EmptyView()
            }
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

    private func choose(_ key: String) {
        trip.needFlight = key == "flight"
        if key != "flight" { trip.travelBy = key }
        if key == "train", trip.station == nil { trip.station = "KGX" }
        if key == "train" || key == "car" {
            if trip.arriveAt == nil { trip.arriveAt = "11:00" }
            if trip.leaveAt == nil { trip.leaveAt = "17:00" }
        }
    }

    private var flightCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Button { showAirports = true } label: {
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Flying from").font(.footnote).foregroundStyle(Theme.muted)
                        Text(trip.origin?.label ?? "Choose an airport").foregroundStyle(Theme.ink)
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
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
            // journey round 2: a flight booked elsewhere (or found later) still shapes the first and last days
            Toggle(isOn: Binding(get: { trip.ownFlight ?? false }, set: { on in
                trip.ownFlight = on
                if on {
                    if trip.flightAirport == nil { trip.flightAirport = "LHR" }
                    if trip.arriveAt == nil { trip.arriveAt = "11:00" }
                    if trip.leaveAt == nil { trip.leaveAt = "17:00" }
                }
            })) {
                Text("I already have a flight").foregroundStyle(Theme.ink)
            }
            .tint(Theme.accent)
            .padding(.horizontal, 18)
            .frame(minHeight: 52)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
            if trip.ownFlight == true {
                VStack(spacing: 0) {
                    Menu {
                        Picker("London airport", selection: Binding(get: { trip.flightAirport ?? "LHR" },
                                                                    set: { trip.flightAirport = $0 })) {
                            ForEach(LondonAirports.all, id: \.code) { Text($0.name).tag($0.code) }
                        }
                    } label: {
                        MenuRow(label: "London airport", value: LondonAirports.name(trip.flightAirport) ?? "Heathrow")
                    }
                    Rectangle().fill(Theme.hairline).frame(height: 1)
                    TimeMenu(label: "It lands, on the first day", time: time(\.arriveAt, "11:00"),
                             options: HalfHours.from(5, to: 23))
                    if trip.nights > 0 {
                        Rectangle().fill(Theme.hairline).frame(height: 1)
                        TimeMenu(label: "Your flight home leaves, on the last day", time: time(\.leaveAt, "17:00"),
                                 options: HalfHours.from(6, to: 23))
                    }
                }
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
            }
            Text(trip.ownFlight == true || trip.flight != nil
                 ? "Your first day starts when your flight lands, and your last day ends in time for the flight home."
                 : "Choose a flight in Book, or add the one you have, and the first and last days fit around it.")
                .font(.footnote)
                .foregroundStyle(Theme.muted)
                .padding(.horizontal, 4)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private var trainCard: some View {
        VStack(spacing: 0) {
            Menu {
                Picker("Arriving at", selection: Binding(get: { trip.station ?? "KGX" }, set: { trip.station = $0 })) {
                    ForEach(LondonStations.all, id: \.code) { Text($0.name).tag($0.code) }
                }
            } label: {
                MenuRow(label: "Arriving at", value: LondonStations.name(trip.station) ?? "Choose a station")
            }
            Rectangle().fill(Theme.hairline).frame(height: 1)
            TimeMenu(label: "Your train arrives", time: time(\.arriveAt, "11:00"), options: HalfHours.from(5, to: 22))
            Rectangle().fill(Theme.hairline).frame(height: 1)
            TimeMenu(label: trip.nights == 0 ? "Your train home leaves" : "Your train home leaves, on the last day",
                     time: time(\.leaveAt, "17:00"), options: HalfHours.from(5, to: 23))
        }
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
    }

    private var carCard: some View {
        VStack(spacing: 0) {
            TimeMenu(label: "You arrive at your stay", time: time(\.arriveAt, "11:00"), options: HalfHours.from(5, to: 22))
            Rectangle().fill(Theme.hairline).frame(height: 1)
            TimeMenu(label: trip.nights == 0 ? "You set off home" : "You set off home, on the last day",
                     time: time(\.leaveAt, "17:00"), options: HalfHours.from(8, to: 23))
        }
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
    }

    private func time(_ key: WritableKeyPath<Trip, String?>, _ fallback: String) -> Binding<String> {
        Binding(get: { trip[keyPath: key] ?? fallback }, set: { trip[keyPath: key] = $0 })
    }
}

/// D122: "Your days": from what time to what time, how many places a day, and travelling light on day 1.
struct DaysStep: View {
    @Binding var trip: Trip

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            PageTitle(text: "Your days", font: Theme.h1)
            Text("Each day runs at these times, from where you're staying.")
                .foregroundStyle(Theme.muted)
            VStack(spacing: 0) {
                TimeMenu(label: "Out from", time: from, options: HalfHours.from(6, to: 14))
                Rectangle().fill(Theme.hairline).frame(height: 1)
                TimeMenu(label: "Back by", time: to, options: HalfHours.from(12, to: 23))
            }
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Places a day").font(.footnote).foregroundStyle(Theme.muted)
                    Text("\(trip.placesPerDay) place\(trip.placesPerDay == 1 ? "" : "s")").foregroundStyle(Theme.ink)
                }
                Spacer()
                RoundIcon(name: "minus", disabled: trip.placesPerDay <= 1) { trip.places = max(1, trip.placesPerDay - 1) }
                    .accessibilityLabel("One place fewer")
                RoundIcon(name: "plus", disabled: trip.placesPerDay >= 6) { trip.places = min(6, trip.placesPerDay + 1) }
                    .accessibilityLabel("One place more")
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 10)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
            Text("Plus lunch, when a day runs through midday. A short day holds fewer places.")
                .font(.footnote)
                .foregroundStyle(Theme.muted)
                .padding(.horizontal, 4)
            if trip.arrivingBy == "flight" || trip.arrivingBy == "train" {
                Toggle(isOn: Binding(get: { trip.travelLight }, set: { trip.light = $0 })) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Travelling light on day 1").foregroundStyle(Theme.ink)
                        Text("No big bags: if you arrive before check-in, one place on the way, then your stay.")
                            .font(.footnote)
                            .foregroundStyle(Theme.muted)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                .tint(Theme.amberDeep)
                .padding(.horizontal, 18)
                .padding(.vertical, 12)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
            }
        }
    }

    private static func mins(_ t: String) -> Int { (Int(t.prefix(2)) ?? 0) * 60 + (Int(t.suffix(2)) ?? 0) }

    private static func hhmm(_ m: Int) -> String { String(format: "%02d:%02d", m / 60, m % 60) }

    /// Changing the start keeps at least two hours before the end.
    private var from: Binding<String> {
        Binding(get: { trip.dayFrom }, set: { v in
            trip.hoursFrom = v
            if Self.mins(trip.dayTo) - Self.mins(v) < 120 { trip.hoursTo = Self.hhmm(min(Self.mins(v) + 240, 23 * 60)) }
        })
    }

    private var to: Binding<String> {
        Binding(get: { trip.dayTo }, set: { v in
            trip.hoursTo = v
            if Self.mins(v) - Self.mins(trip.dayFrom) < 120 { trip.hoursFrom = Self.hhmm(max(Self.mins(v) - 240, 6 * 60)) }
        })
    }
}

/// D122: a time from a menu of half hours.
struct TimeMenu: View {
    let label: String
    @Binding var time: String
    var options: [String] = HalfHours.from(6, to: 23)

    var body: some View {
        Menu {
            Picker(label, selection: $time) {
                ForEach(options, id: \.self) { Text($0).tag($0) }
            }
        } label: {
            MenuRow(label: label, value: time)
        }
    }
}

/// A row that opens a menu: its label, the value, and a small chevron.
struct MenuRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text(label).font(.footnote).foregroundStyle(Theme.muted)
                Text(value).foregroundStyle(Theme.ink).monospacedDigit()
            }
            Spacer(minLength: 8)
            Image(systemName: "chevron.up.chevron.down").font(.footnote).foregroundStyle(Theme.accent)
        }
        .multilineTextAlignment(.leading)
        .padding(.horizontal, 18)
        .padding(.vertical, 12)
        .contentShape(Rectangle())
        .accessibilityElement(children: .combine)
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
    @State private var searching = false
    @State private var failed = false

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 12) {
                LineField(placeholder: "A town, city or airport", text: $query)
                    .textInputAutocapitalization(.words)
                    .autocorrectionDisabled()
                if searching && found.isEmpty {   // the free server may be waking (up to about a minute)
                    HStack(spacing: 10) {
                        ProgressView()
                        Text("Searching… the first search can take up to a minute.")
                            .font(.footnote).foregroundStyle(Theme.muted)
                    }
                } else if failed {
                    Text("Couldn't reach the planner. Check your connection, then type again.")
                        .font(.footnote).foregroundStyle(Theme.muted)
                } else if !query.isEmpty && found.isEmpty {
                    Text("No airports found for that. Try a city name or a three-letter code.")
                        .font(.footnote).foregroundStyle(Theme.muted)
                }
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
                guard !Task.isCancelled else { return }
                searching = true
                failed = false
                do {
                    let places = try await model.client.places(query)
                    if !Task.isCancelled { found = places }
                } catch {
                    if !Task.isCancelled && !(error is CancellationError) { failed = true; found = [] }
                }
                if !Task.isCancelled { searching = false }
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
    @State private var removing: String?      // journey round 2: "flight" or "stay", asked before it's taken off

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
        .confirmationDialog("Remove this \(removing ?? "choice") from the trip?",
                            isPresented: Binding(get: { removing != nil }, set: { if !$0 { removing = nil } }),
                            titleVisibility: .visible) {
            Button("Remove it", role: .destructive) {
                if let kind = removing { model.removeChoice(kind, from: tripId) }
                removing = nil
            }
            Button("Keep it", role: .cancel) { removing = nil }
        } message: {
            Text("Anything you booked stays booked on the provider's site. The days will be planned again around the change.")
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
                TripStepCard(label: "1 · Getting there", status: .of(trip.flight, fits: trip.fits(trip.flight)),
                             title: trip.flight?.title ?? "Choose your flight", sub: flightSub(trip)) {
                    openBook(trip, .flights)
                }
                if trip.flight != nil {   // m176: a choice can be taken off the trip
                    QuietButton("Remove this flight from the trip") { removing = "flight" }
                }
            }
            if trip.needStay {
                TripStepCard(label: "\(trip.needFlight ? 2 : 1) · Where you'll stay",
                             status: .of(trip.stay, fits: trip.fits(trip.stay)),
                             title: trip.stay?.title ?? "Choose where to stay", sub: staySub(trip)) {
                    openBook(trip, .stays)
                }
                if trip.stay != nil {
                    QuietButton("Remove this stay from the trip") { removing = "stay" }
                }
            }
            HStack(alignment: .firstTextBaseline) {
                SectionLabel(text: "\(1 + (trip.needFlight ? 1 : 0) + (trip.needStay ? 1 : 0)) · Your days")
                Spacer()
                Text("\(trip.dayCount) day\(trip.dayCount == 1 ? "" : "s")").font(.subheadline).foregroundStyle(Theme.muted)
            }
            .padding(.top, 8)
            Button {
                model.editingTrip = trip      // D122: straight to "Your days"
                model.editStep = 3
                model.showCreate = true
            } label: {
                HStack {
                    Text(trip.daysLine).font(.subheadline).foregroundStyle(Theme.inkSoft)
                    Spacer(minLength: 8)
                    Text("Change").font(.footnote).foregroundStyle(Theme.accent)
                }
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Your days: \(trip.daysLine). Change")
            if trip.daysStale {
                SecondaryButton(title: model.busy ? "Planning…" : "Plan the days again around your stay and journeys",
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
            TripGoodToKnow(trip: trip, basedAbroad: model.isVisitor)
            QuietButton("Delete this trip") { confirmDelete = true }
        }
        .padding(.horizontal, 24)
        .padding(.top, 8)
        .padding(.bottom, 40)
    }

    private func flightSub(_ trip: Trip) -> String {
        if let f = trip.flight, !trip.fits(f) {
            return "Chosen for other dates: check it on \(f.provider), or choose again"
        }
        if let f = trip.flight {
            return "\(f.provider) · \(Money.whole(f.price))" + (f.sample == true ? " · a sample price, not a real fare" : "")
        }
        guard let origin = trip.origin else { return "Choose where you're flying from" }
        if model.book.resultsFor == trip.id, let r = model.book.flights, let low = r.facets.price?.first {
            return "From \(Money.whole(low)) · \(r.total) options from \(origin.city)"
        }
        return "Search flights from \(origin.city)"
    }

    private func staySub(_ trip: Trip) -> String {
        if let s = trip.stay, !trip.fits(s) {
            return "Chosen for other dates: check it on \(s.provider), or choose again"
        }
        if let s = trip.stay {
            return "\(s.provider) · \(Money.whole(s.price)) for \(trip.lengthLabel)" + (s.sample == true ? " · a sample price" : "")
        }
        if model.book.resultsFor == trip.id, let r = model.book.stays, let low = r.facets.priceNight?.first {
            return "From \(Money.whole(low)) a night · \(r.total) places"
        }
        return "Hotels, flats and hostels, from where your days happen"
    }

    private func openBook(_ trip: Trip, _ segment: BookState.Segment) {
        model.currentTripId = trip.id
        model.book.segment = segment
        model.path.append(TripDest.book)   // D131: flights and stays open inside the trip
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
            if let f = trip.flight, !trip.fits(f) {   // journey audit: chosen for other dates, so not counted
                out.append(("Flight", "for other dates", nil))
            } else if let f = trip.flight {
                out.append(("Flight", Money.whole(f.price), f.price))
            } else if let low = flights?.facets.price?.first {
                out.append(("Flight", "from \(Money.whole(low))", low))
            } else {
                out.append(("Flight", "not chosen yet", nil))
            }
        }
        if trip.needStay {
            if let s = trip.stay, !trip.fits(s) {
                out.append(("Stay · \(trip.lengthLabel)", "for other dates", nil))
            } else if let s = trip.stay {
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
            if trip.flight?.sample == true || trip.stay?.sample == true || flights?.source == "sample" || stays?.source == "sample" {
                Text("Includes sample prices: the real ones show once live search is on.")
                    .font(.footnote)
                    .foregroundStyle(Theme.muted)
                    .fixedSize(horizontal: false, vertical: true)
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
    var scrollToEnd = false        // CI screenshots: the last day's way home
    var openChange = false         // CI screenshots: "Change this day" open
    @State private var confirm = false
    @State private var showSafety = false
    @State private var changing: TripDayOut?

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    HStack {
                        BackLink { dismiss() }
                        Spacer()
                        HelpPill { showSafety = true }   // m176: Help on every trip page
                    }
                    if let trip = model.findTrip(tripId) {
                        let day = trip.days.first { $0.index == index }
                        let date = Calendar.london.date(byAdding: .day, value: index, to: trip.startDate) ?? trip.startDate
                        Eyebrow("Day \(index + 1) · \(Dates.dayShort.string(from: date))")
                        let parts = (day?.title ?? "Planned as you go").headlineParts
                        Text(parts.0)
                            .font(Theme.serif(30, relativeTo: .title))
                            .foregroundStyle(Theme.ink)
                            .fixedSize(horizontal: false, vertical: true)
                            .accessibilityAddTraits(.isHeader)
                        if let sub = parts.1 {   // 20 Oct (round 2): as on the plan
                            Text(sub)
                                .font(Theme.serif(19, relativeTo: .title3))
                                .foregroundStyle(Theme.inkSoft)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        if let day {   // D122: from the airport or station, and one place on the way
                            ForEach(day.journeys("arrive"), id: \.self) { JourneyCard(leg: $0) }
                            if let before = day.before {
                                SectionLabel(text: "On the way · travelling light").padding(.top, 4)
                                ForEach(before.stops) { stop in TripDayStop(stop: stop) }
                            }
                            ForEach(day.journeys("to_stay"), id: \.self) { JourneyCard(leg: $0) }
                        }
                        if let day, let plan = day.plan {
                            if day.before != nil || !day.journeys("arrive").isEmpty {
                                SectionLabel(text: "From your stay").padding(.top, 4)
                            }
                            ForEach(plan.stops) { stop in TripDayStop(stop: stop) }
                            if let end = day.window?.end, let last = plan.stops.last,   // journey round 2: free time
                               AppModel.minutes(end) - AppModel.minutes(last.depart) >= 60 {
                                FreeTimeRow(from: last.depart, to: end, canAdd: trip.placesPerDay < 6) {
                                    Task {
                                        _ = await model.changeTripDay(trip.id, index, from: day.window?.start ?? trip.dayFrom,
                                                                      to: end, places: min(6, trip.placesPerDay + 1))
                                    }
                                }
                            }
                            ForEach(day.journeys("back") + day.journeys("leave"), id: \.self) { JourneyCard(leg: $0) }
                            PrimaryButton(title: model.plan?.id == plan.id ? "This is your day" : "Make this my day",
                                          disabled: model.plan?.id == plan.id) {
                                if model.testBPlanAtRisk { confirm = true } else { use(trip, day) }
                            }
                            .confirmReplacingTestBPlan($confirm) { use(trip, day) }
                            Text("Your day gets \"Now\", a reminder to rate each stop, and swapping a stop.")
                                .font(.footnote)
                                .foregroundStyle(Theme.muted)
                            // Abram's comment (8 Oct): plans change; the day is planned again around them
                            SecondaryButton(title: "Made other plans? Change this day", icon: "clock.arrow.circlepath") {
                                changing = day
                            }
                            .id("end")
                        } else if day == nil {
                            PrimaryButton(title: model.busy ? "Planning…" : "Plan this day", disabled: model.busy) {
                                Task { await model.planDay(tripId, index) }
                            }
                        } else {
                            ForEach(day?.journeys("leave") ?? [], id: \.self) { JourneyCard(leg: $0) }
                            if day?.before == nil {
                                Text(day?.kind == "arrive" || day?.kind == "leave"
                                     ? "A travel day: nothing is planned, so you can take it easy."
                                     : "A free day: the places that suit you are already in your other days. More London moments are being checked.")
                                    .foregroundStyle(Theme.inkSoft)
                                    .padding(20)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .overlay(RoundedRectangle(cornerRadius: 20).stroke(Theme.outline, lineWidth: 1))
                            }
                        }
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 8)
                .padding(.bottom, 40)
            }
            .onAppear {
                if openChange { changing = model.findTrip(tripId)?.days.first { $0.index == index } }
                guard scrollToEnd else { return }
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) { proxy.scrollTo("end", anchor: .bottom) }
            }
        }
        .background(Theme.background)
        .toolbar(.hidden, for: .navigationBar)
        .statusBarShade()
        .sheet(isPresented: $showSafety) { SafetyView().brainFeedback() }
        .sheet(item: $changing) { day in
            if let trip = model.findTrip(tripId) { ChangeDaySheet(trip: trip, day: day).brainFeedback() }
        }
    }

    private func use(_ trip: Trip, _ day: TripDayOut) {
        model.useDay(trip, day)
        var p = NavigationPath()
        p.append(TripDest.day)
        model.path = p
    }
}

/// Abram's comment (8 Oct): "I'm meeting someone tomorrow." The hours they're free and how many places, then the day
/// planned again around them. The trip's other days stay as they are; this day may keep some of its own places.
struct ChangeDaySheet: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let trip: Trip
    let day: TripDayOut
    @State private var from: String
    @State private var to: String
    @State private var places: Int

    init(trip: Trip, day: TripDayOut) {
        self.trip = trip
        self.day = day
        // the arrival and leaving days keep the person's own hours: the journeys set their real start and end
        _from = State(initialValue: day.kind == "arrive" ? trip.dayFrom : (day.window?.start ?? trip.dayFrom))
        _to = State(initialValue: day.kind == "leave" ? trip.dayTo : (day.window?.end ?? trip.dayTo))
        _places = State(initialValue: trip.placesPerDay)
    }

    private var tooShort: Bool { Self.minutes(to) - Self.minutes(from) < 60 }

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                QuietButton("Cancel", color: Theme.accent) { dismiss() }
                Spacer()
            }
            .padding(.horizontal, 24)
            .padding(.top, 8)
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    Eyebrow("Day \(day.index + 1) · \(Dates.shortDay(day.date))")
                    PageTitle(text: "Change this day", font: Theme.h1)
                    Text("Meeting someone, or made other plans? Tell me when you're free, and I'll plan the day again around it. Your other days stay as they are.")
                        .foregroundStyle(Theme.inkSoft)
                        .fixedSize(horizontal: false, vertical: true)
                    TimeMenu(label: "Free from", time: $from)
                    TimeMenu(label: "Until", time: $to)
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Places").font(.footnote).foregroundStyle(Theme.muted)
                            Text("\(places) place\(places == 1 ? "" : "s"), plus lunch").foregroundStyle(Theme.ink)
                        }
                        Spacer()
                        RoundIcon(name: "minus", disabled: places <= 1) { places -= 1 }
                            .accessibilityLabel("One place fewer")
                        RoundIcon(name: "plus", disabled: places >= 6) { places += 1 }
                            .accessibilityLabel("One place more")
                    }
                    .padding(.horizontal, 18)
                    .padding(.vertical, 10)
                    .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
                    if tooShort {
                        Text("Leave at least an hour between the two times.")
                            .font(.subheadline)
                            .foregroundStyle(Theme.accent)
                    }
                    Text(note)
                        .font(.footnote)
                        .foregroundStyle(Theme.muted)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(.horizontal, 24)
                .padding(.vertical, 12)
            }
        }
        .background(Theme.background)
        .safeAreaInset(edge: .bottom) {
            PrimaryButton(title: model.busy ? "Planning…" : "Plan this day again", disabled: model.busy || tooShort) {
                Task {
                    if await model.changeTripDay(trip.id, day.index, from: from, to: to, places: places) { dismiss() }
                }
            }
            .padding(.horizontal, 24)
            .padding(.vertical, 8)
            .background(Theme.background)
        }
    }

    private var note: String {
        switch day.kind {
        case "arrive": return "This day still starts once you've arrived. Busy in the middle of the day? Choose the part that's free."
        case "leave": return "This day still ends in time for your journey home. Busy in the middle of the day? Choose the part that's free."
        default: return "Busy in the middle of the day? Choose the part that's free. Once it's your day, you can also swap a stop."
        }
    }

    static func minutes(_ hhmm: String) -> Int {
        let p = hhmm.split(separator: ":").compactMap { Int($0) }
        return p.count == 2 ? p[0] * 60 + p[1] : 0
    }
}

/// D122: one journey at an end of the trip ("Heathrow → your stay"), with Apple Maps for the real route.
struct JourneyCard: View {
    @Environment(\.openURL) private var openURL
    let leg: TripLeg

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline, spacing: 10) {
                Image(systemName: icon)
                    .font(.body)
                    .foregroundStyle(Theme.accent)
                    .frame(width: 24)
                    .accessibilityHidden(true)
                Text(leg.title)
                    .font(Theme.serif(19, relativeTo: .title3))
                    .foregroundStyle(Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)
            }
            VStack(alignment: .leading, spacing: 4) {
                if let times = leg.times {
                    Text(times).font(.subheadline.monospacedDigit()).foregroundStyle(Theme.inkSoft)
                }
                if let how = leg.how {
                    Text(how).font(.subheadline).foregroundStyle(Theme.inkSoft).fixedSize(horizontal: false, vertical: true)
                }
                if let note = leg.note {
                    Text(note).font(.footnote).foregroundStyle(Theme.muted).fixedSize(horizontal: false, vertical: true)
                }
                if let url = leg.mapsURL {
                    Button {
                        Haptics.light()
                        openURL(url)
                    } label: {
                        Label("Directions", systemImage: "arrow.triangle.turn.up.right.diamond")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(Theme.accent)
                            .frame(minHeight: 44)
                            .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)
                    .accessibilityHint("Opens Apple Maps")
                }
            }
            .padding(.leading, 34)
        }
        .padding(.horizontal, 16)
        .padding(.top, 14)
        .padding(.bottom, leg.mapsURL == nil ? 14 : 4)
        .frame(maxWidth: .infinity, alignment: .leading)
        .overlay(RoundedRectangle(cornerRadius: 20).stroke(Theme.outline, lineWidth: 1))
    }

    private var icon: String {
        let airport = (leg.origin?.maps ?? "").contains("Airport") || (leg.destination?.maps ?? "").contains("Airport")
        switch leg.slot {
        case "arrive": return leg.mode == "driving" ? "car.fill" : (airport ? "airplane.arrival" : "tram.fill")
        case "leave": return leg.mode == "driving" ? "car.fill" : (airport ? "airplane.departure" : "tram.fill")
        case "to_stay": return "bed.double.fill"
        default: return "bag.fill"
        }
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
    var onBack: (() -> Void)?      // D131: opened from the home's menu

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                if let onBack { BackLink(action: onBack) }
                PageTitle(text: "You", font: Theme.serif(36, relativeTo: .largeTitle))
                    .padding(.top, onBack == nil ? 30 : 0)
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
                            Image(systemName: "chevron.right").foregroundStyle(Theme.muted)   // 19 Oct: it opens
                        }
                        Text("Something wrong with a stop, a booking or how you feel? A real person replies here, usually within a few hours.")
                            .font(.subheadline)
                            .foregroundStyle(Theme.inkTertiary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .multilineTextAlignment(.leading)
                    .surfaceCard(padding: 18, radius: 20)
                }
                .buttonStyle(PressStyle())
                VStack(alignment: .leading, spacing: 2) {
                    SectionLabel(text: "What you've told us").padding(.bottom, 6)
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
                VStack(alignment: .leading, spacing: 10) {   // D130 (Daylight)
                    SectionLabel(text: "The light")
                    HStack(spacing: 0) {
                        lightChoice("Follow the sky", dark: false)
                        lightChoice("Always dark", dark: true)
                    }
                    .padding(3)
                    .background(Theme.surface, in: RoundedRectangle(cornerRadius: 14))
                    Text("By day the app is light, and it turns dark after sunset, following London's sky. Always dark keeps the night look.")
                        .font(.footnote)
                        .foregroundStyle(Theme.muted)
                        .fixedSize(horizontal: false, vertical: true)
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
        .toolbar(.hidden, for: .navigationBar)
        .statusBarShade()
        .sheet(isPresented: $showSafety) { SafetyView().brainFeedback() }
        .sheet(isPresented: $showSettings) { SettingsView().brainFeedback() }
        .task {
            await model.loadSafety()
            if model.learned == nil { model.learned = try? await model.client.summary() }
        }
    }

    private func lightChoice(_ title: String, dark: Bool) -> some View {
        let on = model.alwaysDark == dark
        return Button {
            Haptics.light()
            model.setAlwaysDark(dark)
        } label: {
            Text(title)
                .font(.subheadline.weight(on ? .semibold : .regular))
                .foregroundStyle(on ? Theme.ink : Theme.muted)
                .frame(maxWidth: .infinity, minHeight: 44)
                .background(on ? Theme.surfaceHigh : .clear, in: RoundedRectangle(cornerRadius: 11))
                .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(on ? [.isSelected] : [])
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
        case "tripwhere", "tripwhen", "tripfrom", "tripdays", "tripfeel":                 // 20-23, 22a
            if let trip = model.trips.first {
                TripCreateFlow(trip: trip, editing: false,
                               startAt: ["tripwhere": 0, "tripwhen": 1, "tripfrom": 2, "tripdays": 3, "tripfeel": 4][name] ?? 0)
            }
        case "trip", "tripday":                                                           // 24, 25
            LivingHome().onAppear {
                guard let trip = model.trips.first else { return }
                var p = NavigationPath()
                p.append(TripDest.trip(trip.id))
                if name == "tripday" { p.append(TripDest.tripDay(trip.id, 0)) }            // D122: the arrival day
                model.path = p
            }
        case "tripdaylast":                                                               // 25a: the way home
            if let trip = model.trips.first {
                NavigationStack { TripDayView(tripId: trip.id, index: trip.dayCount - 1, scrollToEnd: true) }
            }
        case "daychange":                                                                 // 25b: "Change this day"
            if let trip = model.trips.first {
                NavigationStack { TripDayView(tripId: trip.id, index: 1, openChange: true) }
            }
        case "flights", "flightfilters", "stays", "staysmap", "stayfilters":              // 26, 27, 29-31
            LivingHome().onAppear {
                model.book.segment = name.hasPrefix("flight") ? .flights : .stays
                model.book.stayMap = name == "staysmap"
                guard let trip = model.trips.first else { return }
                var p = NavigationPath()   // D131: flights and stays open inside the trip
                p.append(TripDest.trip(trip.id))
                p.append(TripDest.book)
                model.path = p
                if name.hasSuffix("filters") { model.book.showFilters = true }
            }
        case "flight", "handoff", "handoffback":                                          // 28, 28a, 28b
            if let f = model.book.flights?.results.first {
                NavigationStack { FlightDetailView(flight: f) }
                    .sheet(isPresented: .constant(name != "flight")) {
                        HandoffSheet().presentationDetents([.medium]).followsSky()
                    }
                    .onAppear { if name != "flight" { model.book.handoff = Self.handoff(f, back: name == "handoffback") } }
            }
        case "stay":                                                                      // 32
            if let s = model.book.stays?.results.first { NavigationStack { StayDetailView(stay: s) } }
        case "you": LivingHome().onAppear { model.path.append(TripDest.you) }            // 33 (D131: from the menu)
        case "hometoday", "homeafter":                                                    // 19b, 19c (D131)
            LivingHome().onAppear {
                guard let plan = model.plan else { return }
                let today = plan.dated(Dates.isoDay.string(from: .now))
                model.plan = today
                let at = name == "hometoday" ? 1 : today.stops.count
                UserDefaults.standard.set(at, forKey: "nowIndex.\(today.id)")
                model.nowIndex = at
                if name == "homeafter" {
                    var ratings: [String: Int] = [:]
                    for (k, stop) in today.stops.filter(\.rateable).enumerated() { ratings[stop.momentId] = [5, 4, 3, 4, 5][k % 5] }
                    model.myRatings = ratings
                    model.rated = Set(ratings.keys)
                }
            }
        case "nowarrived":                                                                // 10d (D130): at the stop
            DayScreen().onAppear {
                guard let plan = model.plan else { return }
                let today = plan.dated(Dates.isoDay.string(from: .now))
                model.plan = today
                UserDefaults.standard.set(1, forKey: "nowIndex.\(today.id)")
                UserDefaults.standard.set(today.stops[1].id, forKey: "arrived.\(today.id)")
                model.startDay()
            }
        default: LivingHome()                                                             // 19 ("triphome")
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
