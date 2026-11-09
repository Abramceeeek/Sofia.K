import Network
import SwiftUI

/// m228 (Abram, 9 Nov): what's saved on this phone for the day, in order: today's itinerary, where you're staying, the
/// journey, emergency help. Built on the phone from what it already keeps (the plan and the trip), never fetched, so it
/// works with no signal. Each item says where it came from, when it was saved, whether it's current, needs checking,
/// has expired or is past, and the one thing to do about it. Nothing here claims to be live. The rules are the
/// Brain's tested reference (brain/src/brain/offline.py), the same on Android.
struct OfflineItem: Identifiable, Hashable {
    enum Status: String { case current, check, expired, past }
    let id = UUID()
    let title: String
    let lines: [String]
    let source: String
    let saved: String?                 // ISO date or date-time, when known
    let status: Status
    let action: String?
    var missing: [String] = []
}

struct OfflineSection: Identifiable, Hashable {
    let id: String                     // itinerary | stay | journey | emergency
    let title: String
    let items: [OfflineItem]
}

enum OfflinePack {
    static let cardCheckDays = 90      // GUESS (offline.py): a card's facts older than this say "check on the day"
    static let planStaleDays = 7       // GUESS: a day planned this long before its date may have changed travel times

    /// The same words as Help & safety, which is bundled in the app and works offline.
    static let emergency = [
        OfflineItem(title: "Emergency", lines: ["If you or someone else is in danger or hurt, call 999 now."],
                    source: "Help & safety, in the app", saved: nil, status: .current, action: nil),
        OfflineItem(title: "Urgent medical help", lines: ["Urgent medical help that isn't an emergency: call NHS 111. You can ask for an interpreter."],
                    source: "Help & safety, in the app", saved: nil, status: .current, action: nil),
        OfflineItem(title: "Someone to talk to", lines: ["Samaritans answer free, day or night, on 116 123."],
                    source: "Help & safety, in the app", saved: nil, status: .current, action: nil),
    ]

    static func day(_ s: String?) -> Date? { s.flatMap { Dates.isoDay.date(from: String($0.prefix(10))) } }

    static func days(_ a: Date, _ b: Date) -> Int {
        Calendar.london.dateComponents([.day], from: a, to: b).day ?? 0
    }

    static func build(plan: Plan?, trip: Trip?, today: Date) -> [OfflineSection] {
        [OfflineSection(id: "itinerary", title: "Today", items: [itinerary(plan, today)]),
         OfflineSection(id: "stay", title: "Where you're staying",
                        items: trip.map { $0.needStay ? [choice("stay", $0.stay, $0, today)] : [] } ?? []),
         OfflineSection(id: "journey", title: "Your journey",
                        items: trip.map { $0.needFlight ? [choice("flight", $0.flight, $0, today)] : [] } ?? []),
         OfflineSection(id: "emergency", title: "Emergency help", items: emergency)]
    }

    static func itinerary(_ plan: Plan?, _ today: Date) -> OfflineItem {
        guard let plan else {
            return OfflineItem(title: "No day saved", lines: [], source: "This phone", saved: nil, status: .current,
                               action: nil, missing: ["a plan for today"])
        }
        let when = day(plan.date)
        var lines = plan.stops.map { "\($0.arrive)–\($0.depart) \($0.title)" }
        var missing: [String] = []
        for s in plan.stops where s.rateable {
            if let checked = day(s.checked) {
                if let when, days(checked, when) > cardCheckDays {
                    lines.append("\(s.title): facts checked \(Dates.dayShort.string(from: checked)); check opening hours on the day.")
                }
            } else {
                missing.append("when \(s.title)'s facts were checked")
            }
            if let book = s.bookAhead, !book.isEmpty { lines.append("\(s.title): \(book)") }
        }
        let made = day(plan.createdAt)
        var status: OfflineItem.Status = when.map { $0 < Calendar.london.startOfDay(for: today) ? OfflineItem.Status.past : OfflineItem.Status.current } ?? .current
        var action: String? = nil
        if status == .current, let made, let when, days(made, when) > planStaleDays {
            status = .check
            action = "Planned on \(Dates.dayShort.string(from: made)): travel times may have changed. Plan this day again when you have signal."
        }
        return OfflineItem(title: plan.title ?? "Your day", lines: lines, source: "Your plan", saved: plan.createdAt,
                           status: status, action: action, missing: missing)
    }

    static func choice(_ kind: String, _ c: TripChoice?, _ trip: Trip, _ today: Date) -> OfflineItem {
        let label = kind == "stay" ? "Where you're staying" : "Your journey"
        guard let c else {
            return OfflineItem(title: label, lines: [], source: "Your trip", saved: nil, status: .current, action: nil,
                               missing: [kind == "stay" ? "no stay chosen" : "no flight chosen"])
        }
        var lines = [c.title, "\(c.money), as found on \(c.provider)"]
        if kind == "stay" {
            lines.append("The address isn't saved on this phone.")
        } else {
            if let t = c.arriveTime { lines.append("Lands \(t)" + (c.arrivePlace.map { " (\($0))" } ?? "")) }
            if let t = c.leaveTime { lines.append("Flight home leaves \(t)" + (c.leavePlace.map { " (\($0))" } ?? "")) }
        }
        var missing: [String] = []
        if kind == "flight" {
            if c.arriveTime == nil { missing.append("when the flight lands") }
            if c.leaveTime == nil { missing.append("when the flight home leaves") }
        }
        let ended = Calendar.london.startOfDay(for: today) > trip.endDate
        var status: OfflineItem.Status = ended ? .expired : .current
        var action: String?
        if c.sample == true {
            status = .check; action = "A sample price, made up for testing: not a real booking."
        } else if let s = c.forStart, s != trip.start {
            status = .check; action = "Chosen for other dates: check it on \(c.provider), or choose again."
        } else if !c.booked {
            if status == .current { status = .check }
            action = "Not marked as booked: check with \(c.provider)."
        } else {
            action = kind == "flight" ? "Times can change: check with the airline on the day."
                                      : "The address and check-in details are in \(c.provider)'s confirmation."
        }
        return OfflineItem(title: label, lines: lines, source: "Found on \(c.provider)", saved: c.forStart,
                           status: ended && status == .check ? .expired : status, action: action, missing: missing)
    }
}

/// m228: whether the phone has a network path. Only a hint (a path can exist without a working connection), so the
/// screens say "No signal" only as "what's saved on this phone", never "this is live".
@Observable final class Connectivity {
    var online = true
    private var pinned = false         // CI screenshots: a state that the real network can't change
    private let monitor = NWPathMonitor()

    /// CI screenshots only: show the offline state whatever the simulator's network is.
    func pin(online value: Bool) { pinned = true; online = value }

    init() {
        monitor.pathUpdateHandler = { [weak self] path in
            let up = path.status == .satisfied
            DispatchQueue.main.async { if self?.pinned != true { self?.online = up } }
        }
        monitor.start(queue: DispatchQueue(label: "odys.connectivity"))
    }

    deinit { monitor.cancel() }
}

/// m228: the offline view, from "Now". In ODYS's look: the sky behind, quiet cards, amber only for "check".
struct OfflineView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        let sections = OfflinePack.build(plan: model.plan, trip: model.tripForToday, today: .now)
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    Eyebrow(model.connectivity.online ? "Saved on this phone" : "No signal")
                    Text("What's saved on this phone")
                        .font(Theme.title)
                        .foregroundStyle(Theme.ink)
                    Text(model.connectivity.online
                         ? "Kept here in case you lose signal. None of it is live: check anything marked \u{201C}Check\u{201D}."
                         : "You're offline, so this is what was saved, not live information. Check anything marked \u{201C}Check\u{201D} when you have signal.")
                        .font(.subheadline)
                        .foregroundStyle(Theme.inkSoft)
                        .fixedSize(horizontal: false, vertical: true)
                    ForEach(sections.filter { !$0.items.isEmpty }) { section in
                        SectionLabel(text: section.title).padding(.top, 4)
                        ForEach(section.items) { OfflineItemCard(item: $0) }
                    }
                }
                .padding(.horizontal, 24)
                .padding(.vertical, 28)
            }
            .skyBackground(base: Theme.calm)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) { Button("Done") { dismiss() } }
            }
        }
    }
}

struct OfflineItemCard: View {
    let item: OfflineItem

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                Text(item.title).font(.headline).foregroundStyle(Theme.ink)
                Spacer(minLength: 8)
                Text(Self.word(item.status))
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(item.status == .check ? Theme.amberDeep : Theme.muted)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 3)
                    .background(item.status == .check ? Theme.savedBg : Theme.surfaceHigh, in: Capsule())
            }
            ForEach(item.lines, id: \.self) { line in
                Text(line).font(.subheadline).foregroundStyle(Theme.inkSoft).fixedSize(horizontal: false, vertical: true)
            }
            if let action = item.action {
                Text(action).font(.subheadline.weight(.semibold)).foregroundStyle(Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)
            }
            ForEach(item.missing, id: \.self) { m in
                Text("Not saved: \(m)").font(.footnote).foregroundStyle(Theme.muted)
            }
            Text(Self.provenance(item)).font(.footnote).foregroundStyle(Theme.muted)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
        .accessibilityElement(children: .combine)
    }

    static func word(_ s: OfflineItem.Status) -> String {
        switch s {
        case .current: return "Saved"
        case .check: return "Check"
        case .expired: return "Expired"
        case .past: return "Past"
        }
    }

    /// "From your plan · saved 8 Nov" (a date-time shows its date; nothing is shown as more recent than it is).
    static func provenance(_ item: OfflineItem) -> String {
        guard let saved = item.saved, let d = OfflinePack.day(saved) else { return item.source }
        return "\(item.source) · saved \(Dates.dayShort.string(from: d))"
    }
}
