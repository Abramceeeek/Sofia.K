import SwiftUI

// m358 (Abram, 25 Nov: "test whether two or three people can actually create one together, contribute their
// individual preferences and produce something they all want to do"): a trip planned by friends, each from their own
// phone. The organiser starts it and sends the code; each friend joins with it and agrees first. The days come from
// everyone's own answers (brain/src/brain/group.py); nobody's answers are shown to the others, and a person is named
// in a stop's reason only if they agreed. Friends only: no strangers, no matching, no payments.

struct GroupMemberInfo: Codable, Hashable {
    let label: String
    let you: Bool
    let named: Bool
}

struct GroupSettings: Codable, Hashable {
    let startDate: String
    let nights: Int
    let perDay: Int
}

struct GroupTripInfo: Codable, Hashable, Identifiable {
    let id: Int
    let settings: GroupSettings
    let you: String
    let code: String?
    let members: [GroupMemberInfo]
}

struct GroupList: Codable {
    let groups: [GroupTripInfo]
}

struct GroupStop: Codable, Hashable, Identifiable {
    let id: String
    let title: String
    let why: String?
}

struct GroupPlanOut: Codable {
    let group: GroupTripInfo
    let method: String
    let days: [[GroupStop]]
    let notes: [String]
    let yourShare: String?
}

struct GroupCreateRequest: Encodable {
    let startDate: String
    let nights: Int
    let perDay: Int
    let consent: Bool
    let sharePreferences: Bool
}

struct GroupJoinRequest: Encodable {
    let code: String
    let consent: Bool
    let sharePreferences: Bool
}

extension BrainClient {
    func groups() async throws -> GroupList {
        if demo { return try Self.bundled("demo_groups") }
        return try await callPreview("GET", "v1/me/groups", nil)
    }

    func createGroup(_ r: GroupCreateRequest) async throws -> GroupTripInfo {
        if demo { return try (Self.bundled("demo_groups") as GroupList).groups[0] }
        return try await callPreview("POST", "v1/me/groups", try Self.encode(r))
    }

    func joinGroup(_ r: GroupJoinRequest) async throws -> GroupTripInfo {
        if demo { return try (Self.bundled("demo_groups") as GroupList).groups[0] }
        return try await callPreview("POST", "v1/me/groups/join", try Self.encode(r))
    }

    func planGroup(_ id: Int) async throws -> GroupPlanOut {
        if demo { return try Self.bundled("demo_group_plan") }
        return try await callPreview("POST", "v1/me/groups/\(id)/plan", nil)
    }

    func leaveGroup(_ id: Int) async throws {
        if demo { return }
        try await callNoContent("POST", "v1/me/groups/\(id)/leave")
    }
}

/// "Planning with friends?" on the home screen.
struct GroupInviteRow: View {
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(alignment: .top, spacing: 14) {
                Image(systemName: "person.2").font(.title3).foregroundStyle(Theme.accent).padding(.top, 2)
                VStack(alignment: .leading, spacing: 4) {
                    Text("Planning with friends?").font(Theme.title3).foregroundStyle(Theme.ink)
                    Text("Start a shared trip and send the code, or join a friend's. Each of you answers on your own phone.")
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

/// The shared trips this phone is in, and starting or joining one.
struct GroupTripsView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    var demoScreen: String?
    @State private var groups: [GroupTripInfo] = []
    @State private var loaded = false
    @State private var mode: String?            // "start" or "join"
    @State private var open: GroupTripInfo?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    Eyebrow("With friends")
                    PageTitle(text: "Plan a trip together")
                    Text("Each of you answers on your own phone. The days come from all of your answers: nobody sees anyone else's, and a place one of you said no to is left out.")
                        .foregroundStyle(Theme.inkSoft)
                        .fixedSize(horizontal: false, vertical: true)
                    if mode == "start" {
                        GroupStartForm { g in groups.insert(g, at: 0); mode = nil; open = g }
                    } else if mode == "join" {
                        GroupJoinForm { g in
                            if !groups.contains(where: { $0.id == g.id }) { groups.insert(g, at: 0) }
                            mode = nil
                            open = g
                        }
                    } else {
                        PrimaryButton(title: "Start a shared trip") { mode = "start" }
                        SecondaryButton(title: "Join with a code") { mode = "join" }
                    }
                    if !groups.isEmpty {
                        SectionLabel(text: "Your shared trips")
                        ForEach(groups) { g in
                            Button { open = g } label: { GroupRow(group: g) }.buttonStyle(PressStyle())
                        }
                    } else if loaded && mode == nil {
                        Text("No shared trips yet.").font(.subheadline).foregroundStyle(Theme.muted)
                    }
                    Text("Friends only: there's no way to find or match strangers, and no money changes hands in ODYS.")
                        .font(.footnote)
                        .foregroundStyle(Theme.muted)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 32)
            }
            .background(Theme.background)
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) { Button("Close") { dismiss() } }
            }
            .navigationDestination(item: $open) { g in
                GroupTripView(group: g, autoPlan: demoScreen == "groupplan") { left in
                    groups.removeAll { $0.id == left }
                    open = nil
                }
            }
            .task {
                if let list = try? await model.client.groups() { groups = list.groups }
                loaded = true
                if demoScreen == "groupjoin" { mode = "join" }
                if demoScreen == "groupplan" { open = groups.first }   // "group" stays on the list, as on Android
            }
        }
    }
}

struct GroupRow: View {
    let group: GroupTripInfo

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(GroupText.when(group.settings)).font(.headline).foregroundStyle(Theme.ink)
                Text(GroupText.who(group)).font(.subheadline).foregroundStyle(Theme.inkTertiary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer()
            Image(systemName: "chevron.right").foregroundStyle(Theme.muted)
        }
        .multilineTextAlignment(.leading)
        .surfaceCard(padding: 18, radius: 20)
    }
}

enum GroupText {
    static func when(_ s: GroupSettings) -> String {
        let date = Dates.isoDay.date(from: s.startDate).map { $0.formatted(.dateTime.weekday(.wide).day().month(.wide)) }
            ?? s.startDate
        let days = s.nights + 1
        return "London from \(date), \(days) day\(days == 1 ? "" : "s")"
    }

    static func who(_ g: GroupTripInfo) -> String {
        let n = g.members.count
        return n == 1 ? "Just you so far: send the code to a friend" : "\(n) of you · you're \(g.you)"
    }

    /// The consent each person gives for their own answers, before starting or joining.
    static let consent = "My answers in ODYS (the places I swiped and the days I chose) help plan this shared trip. The others never see my answers, only why each stop is there."
    static let named = "The plan may name me (by my member letter) when it says who a stop suits. Otherwise I'm counted, never named."
}

struct GroupStartForm: View {
    @Environment(AppModel.self) private var model
    let onDone: (GroupTripInfo) -> Void
    @State private var start = Calendar.current.date(byAdding: .day, value: 7, to: .now) ?? .now
    @State private var nights = 1
    @State private var perDay = 3
    @State private var agreed = false
    @State private var named = false
    @State private var busy = false
    @State private var failed = false

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            DatePicker("First day", selection: $start, in: Date.now..., displayedComponents: .date)
                .foregroundStyle(Theme.ink)
            Stepper("Days: \(nights + 1)", value: $nights, in: 0...6).foregroundStyle(Theme.ink)
            Stepper("Places a day: \(perDay)", value: $perDay, in: 1...5).foregroundStyle(Theme.ink)
            consentRows
            if failed {
                Text("That didn't go through. Check your signal, then try again.").font(.footnote).foregroundStyle(Theme.warnInk)
            }
            PrimaryButton(title: busy ? "Starting…" : "Start the trip", disabled: !agreed || busy) {
                Task {
                    busy = true
                    defer { busy = false }
                    do {
                        onDone(try await model.client.createGroup(GroupCreateRequest(
                            startDate: Dates.isoDay.string(from: start), nights: nights, perDay: perDay,
                            consent: true, sharePreferences: named)))
                    } catch { failed = true }
                }
            }
        }
        .surfaceCard(padding: 18, radius: 20)
    }

    private var consentRows: some View {
        VStack(alignment: .leading, spacing: 6) {
            CheckRow(label: GroupText.consent, isOn: $agreed)
            CheckRow(label: GroupText.named, isOn: $named)
        }
    }
}

struct GroupJoinForm: View {
    @Environment(AppModel.self) private var model
    let onDone: (GroupTripInfo) -> Void
    @State private var code = ""
    @State private var agreed = false
    @State private var named = false
    @State private var busy = false
    @State private var message: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            TextField("The code your friend sent", text: $code)
                .textInputAutocapitalization(.characters)
                .autocorrectionDisabled()
                .font(.title3.monospaced())
                .padding(12)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 12))
            CheckRow(label: GroupText.consent, isOn: $agreed)
            CheckRow(label: GroupText.named, isOn: $named)
            if let message {
                Text(message).font(.footnote).foregroundStyle(Theme.warnInk).fixedSize(horizontal: false, vertical: true)
            }
            PrimaryButton(title: busy ? "Joining…" : "Join the trip", disabled: !agreed || busy || clean.count < 6) {
                Task {
                    busy = true
                    defer { busy = false }
                    do {
                        onDone(try await model.client.joinGroup(GroupJoinRequest(code: clean, consent: true,
                                                                                 sharePreferences: named)))
                    } catch BrainError.status(404) {
                        message = "No shared trip has that code. Check it with your friend."
                    } catch BrainError.status(409) {
                        message = "That trip is full: a shared trip holds six people."
                    } catch {
                        message = "That didn't go through. Check your signal, then try again."
                    }
                }
            }
        }
        .surfaceCard(padding: 18, radius: 20)
    }

    private var clean: String {
        String(code.uppercased().filter { $0.isLetter || $0.isNumber }.prefix(16))
    }
}

/// One shared trip: who's in (by letter), the code to send, the days once two of you are in, and leaving.
struct GroupTripView: View {
    @Environment(AppModel.self) private var model
    let group: GroupTripInfo
    var autoPlan = false
    let onLeft: (Int) -> Void
    @State private var plan: GroupPlanOut?
    @State private var busy = false
    @State private var failed = false
    @State private var confirmLeave = false

    private var organiser: Bool { group.code != nil }
    private var current: GroupTripInfo { plan?.group ?? group }

    var body: some View {
        ScrollViewReader { proxy in
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                Eyebrow("Shared trip")
                PageTitle(text: GroupText.when(current.settings))
                VStack(alignment: .leading, spacing: 6) {
                    SectionLabel(text: "Who's in")
                    ForEach(current.members, id: \.label) { m in
                        Text("\(m.label)\(m.you ? " (you)" : "")\(m.named ? "" : " · counted, not named")")
                            .foregroundStyle(Theme.ink)
                    }
                }
                if let code = current.code {
                    VStack(alignment: .leading, spacing: 8) {
                        SectionLabel(text: "Send this code to your friends")
                        Text(code).font(.title.monospaced().weight(.semibold)).foregroundStyle(Theme.ink)
                            .textSelection(.enabled)
                        ShareLink(item: "Join my trip on ODYS with the code \(code): open ODYS, then \"Planning with friends?\" and \"Join with a code\".") {
                            Label("Send the code", systemImage: "square.and.arrow.up")
                        }
                        .foregroundStyle(Theme.accent)
                    }
                }
                if current.members.count < 2 {
                    Text("The days are planned once a friend has joined.").foregroundStyle(Theme.muted)
                } else {
                    PrimaryButton(title: busy ? "Planning…" : (plan == nil ? "Plan our days" : "Plan again with everyone's latest answers"),
                                  disabled: busy) { Task { await makePlan() } }
                }
                if failed {
                    Text("The days couldn't be planned just now. Check your signal, then try again.")
                        .font(.footnote).foregroundStyle(Theme.warnInk)
                }
                if let plan { days(plan).id("days") }
                QuietButton(organiser ? "End this shared trip for everyone" : "Leave this shared trip") { confirmLeave = true }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 32)
        }
        .onChange(of: plan?.days.count) { if autoPlan { proxy.scrollTo("days", anchor: .top) } }   // the screenshot
        }
        .background(Theme.background)
        .confirmationDialog(organiser ? "End this shared trip for everyone?" : "Leave this shared trip?",
                            isPresented: $confirmLeave, titleVisibility: .visible) {
            Button(organiser ? "End it" : "Leave", role: .destructive) {
                Task {
                    try? await model.client.leaveGroup(group.id)
                    onLeft(group.id)
                }
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text(organiser ? "Everyone's place in it is removed. Your own answers stay yours." :
                    "Your part in it is removed. Your own answers stay yours.")
        }
        .task { if autoPlan && plan == nil { await makePlan() } }
    }

    private func makePlan() async {
        busy = true
        failed = false
        defer { busy = false }
        do { plan = try await model.client.planGroup(group.id) } catch { failed = true }
    }

    private func days(_ p: GroupPlanOut) -> some View {
        VStack(alignment: .leading, spacing: 18) {
        ForEach(Array(p.days.enumerated()), id: \.offset) { i, day in
            VStack(alignment: .leading, spacing: 10) {
                SectionLabel(text: "Day \(i + 1)")
                ForEach(day) { st in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(st.title).font(Theme.serif(19, relativeTo: .body)).foregroundStyle(Theme.ink)
                            .fixedSize(horizontal: false, vertical: true)
                        if let why = st.why {
                            Text(why).font(.subheadline).foregroundStyle(Theme.inkTertiary)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .surfaceCard(padding: 16, radius: 18)
                }
            }
        }
        if let share = p.yourShare {
            Text("For you: \(share).").font(.subheadline).foregroundStyle(Theme.ink)
                .fixedSize(horizontal: false, vertical: true)
        }
        ForEach(p.notes, id: \.self) { n in
            Text(n).font(.footnote).foregroundStyle(Theme.muted).fixedSize(horizontal: false, vertical: true)
        }
        Text("A shared plan of places, without times or routes yet: plan each day out from it on your own phone.")
            .font(.footnote).foregroundStyle(Theme.muted).fixedSize(horizontal: false, vertical: true)
        }
    }
}
