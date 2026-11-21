import SwiftUI

// m320 (Abram, 21 Nov: "Seville in the app, me only"): a place ODYS doesn't fully support, shown read-only to a phone
// that typed the preview's code on You. Its places, each day's state in three words, the hours as the venue prints
// them, the price or "not printed", step-free only where the venue says so, and the country's own emergency number.
// Nothing is planned, booked or searched (brain/src/brain/preview.py).

struct PreviewInfo: Codable, Hashable, Identifiable {
    let key: String
    let name: String
    let country: String
    let countryName: String
    let label: String
    let emergencyNumber: String?
    var id: String { key }
}

struct PreviewList: Codable {
    let previews: [PreviewInfo]
}

struct PreviewDay: Codable, Hashable {
    let date: String
    let label: String
}

struct PreviewEmergency: Codable, Hashable {
    let number: String
    let line: String
    let source: String
    let checked: String?
}

struct PreviewPlace: Codable, Hashable, Identifiable {
    let id: String
    let name: String
    let title: String
    let kind: String
    let category: String
    let district: String?
    let lat: Double
    let lon: Double
    let hours: String
    let hoursSource: String?
    let hoursRead: String?
    let states: [String]
    let price: String
    let access: String
    let notices: [String]
}

struct PreviewContent: Codable {
    let key: String
    let name: String
    let countryName: String
    let label: String
    let caveat: String
    let read: String?
    let days: [PreviewDay]
    let emergency: PreviewEmergency?
    let places: [PreviewPlace]
    let airport: [String]
    let airportSource: String?
    let notCovered: [String]
}

extension BrainClient {
    func previews() async throws -> PreviewList {
        if demo { return try Self.bundled("demo_previews") }
        return try await callPreview("GET", "v1/me/previews", nil)
    }

    func openPreview(code: String) async throws -> PreviewList {
        if demo { return try Self.bundled("demo_previews") }
        return try await callPreview("POST", "v1/me/previews", try Self.encode(["code": code]))
    }

    func preview(_ key: String) async throws -> PreviewContent {
        if demo { return try Self.bundled("demo_preview") }
        return try await callPreview("GET", "v1/me/previews/\(key)", nil)
    }
}

/// A preview of one place: opened from You, from "Where are you going?", or in the CI screenshots.
struct PreviewView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL
    let key: String
    @State private var content: PreviewContent?
    @State private var failed = false
    @State private var day = 0

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    if let c = content {
                        page(c)
                    } else if failed {
                        PageTitle(text: "Preview")
                        Text("The preview couldn't be loaded just now. Check your signal, then try again.")
                            .foregroundStyle(Theme.inkSoft)
                            .fixedSize(horizontal: false, vertical: true)
                        SecondaryButton(title: "Try again") { Task { await load() } }
                    } else {
                        ProgressView().tint(Theme.accent).frame(maxWidth: .infinity, minHeight: 200)
                    }
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
            .task { await load() }
        }
    }

    private func load() async {
        failed = false
        do { content = try await model.client.preview(key) } catch { failed = true }
    }

    @ViewBuilder private func page(_ c: PreviewContent) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Eyebrow(c.label)
            PageTitle(text: c.name)
            Text(c.caveat)
                .font(.subheadline)
                .foregroundStyle(Theme.inkTertiary)
                .fixedSize(horizontal: false, vertical: true)
        }
        if let e = c.emergency { emergency(e, country: c.countryName) }
        days(c)
        let kinds = c.places.map(\.kind).reduce(into: [String]()) { if !$0.contains($1) { $0.append($1) } }
        ForEach(kinds, id: \.self) { kind in
            VStack(alignment: .leading, spacing: 10) {
                SectionLabel(text: kind)
                ForEach(c.places.filter { $0.kind == kind }) { p in PreviewPlaceCard(place: p, state: state(p)) }
            }
        }
        if !c.airport.isEmpty {
            VStack(alignment: .leading, spacing: 8) {
                SectionLabel(text: "From the airport")
                ForEach(c.airport, id: \.self) { line in
                    Text(line).font(.subheadline).foregroundStyle(Theme.inkSoft).fixedSize(horizontal: false, vertical: true)
                }
                if let s = c.airportSource {
                    Text("Source: \(s)").font(.footnote).foregroundStyle(Theme.muted).fixedSize(horizontal: false, vertical: true)
                }
            }
            .surfaceCard(padding: 16, radius: 18)
        }
        VStack(alignment: .leading, spacing: 8) {
            SectionLabel(text: "Not covered here")
            ForEach(c.notCovered, id: \.self) { line in
                Text(line).font(.subheadline).foregroundStyle(Theme.inkSoft).fixedSize(horizontal: false, vertical: true)
            }
            if let read = c.read, let d = Dates.isoDay.date(from: read) {
                Text("Read from official pages on \(Dates.dayMonth.string(from: d)).")
                    .font(.footnote).foregroundStyle(Theme.muted)
            }
        }
    }

    private func state(_ p: PreviewPlace) -> String { day < p.states.count ? p.states[day] : "check" }

    /// The country's own number, in the red card. Help & safety keeps 999 for the UK and shows this one too.
    private func emergency(_ e: PreviewEmergency, country: String) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Emergency in \(country)").font(.headline).foregroundStyle(Theme.emergencyTitle)
            Text(e.line).foregroundStyle(Theme.emergencyText).fixedSize(horizontal: false, vertical: true)
            Button {
                if let url = URL(string: "tel:\(e.number)") { openURL(url) }
            } label: {
                Label("Call \(e.number)", systemImage: "phone.fill")
            }
            .buttonStyle(PillStyle(kind: .danger, height: 54))
            Text("999 is the UK's number. In \(country), call \(e.number).")
                .font(.footnote).foregroundStyle(Theme.emergencyText).fixedSize(horizontal: false, vertical: true)
        }
        .padding(18)
        .background(Theme.emergencyBg, in: RoundedRectangle(cornerRadius: 20))
        .overlay(RoundedRectangle(cornerRadius: 20).stroke(Theme.emergencyBorder, lineWidth: 1))
    }

    private func days(_ c: PreviewContent) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(Array(c.days.enumerated()), id: \.offset) { i, d in
                        Button { day = i } label: {
                            Text(d.label)
                                .font(.subheadline.weight(i == day ? .semibold : .regular))
                                .foregroundStyle(i == day ? Theme.ink : Theme.muted)
                                .padding(.horizontal, 14)
                                .frame(minHeight: 44)
                                .background(i == day ? Theme.surfaceHigh : Theme.surface, in: Capsule())
                        }
                        .buttonStyle(.plain)
                        .accessibilityAddTraits(i == day ? [.isSelected] : [])
                    }
                }
            }
            Text("Open: the venue's own page lists this day. Check: probably open, but check before you go. Shut: closed that day.")
                .font(.footnote)
                .foregroundStyle(Theme.muted)
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}

struct PreviewPlaceCard: View {
    @Environment(\.openURL) private var openURL
    let place: PreviewPlace
    let state: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                Text(place.name).font(.headline).foregroundStyle(Theme.ink).fixedSize(horizontal: false, vertical: true)
                Spacer(minLength: 8)
                Text(Self.word(state))
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Self.ink(state))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 3)
                    .background(Self.fill(state), in: Capsule())
            }
            Text(place.title).font(.subheadline).foregroundStyle(Theme.inkSoft).fixedSize(horizontal: false, vertical: true)
            if let d = place.district {
                Text(d).font(.footnote).foregroundStyle(Theme.muted)
            }
            Text(place.hours).font(.subheadline).foregroundStyle(Theme.ink).fixedSize(horizontal: false, vertical: true)
            Text("\(place.price) · \(place.access)")
                .font(.footnote).foregroundStyle(Theme.inkTertiary).fixedSize(horizontal: false, vertical: true)
            ForEach(place.notices, id: \.self) { n in
                Text(n).font(.footnote).foregroundStyle(Theme.warnInk).fixedSize(horizontal: false, vertical: true)
            }
            HStack(spacing: 16) {
                if let s = place.hoursSource, let url = URL(string: s) {
                    Button("The venue's page") { openURL(url) }
                        .font(.footnote.weight(.semibold)).foregroundStyle(Theme.accent).frame(minHeight: 44)
                }
                if let url = Self.directions(place) {
                    Button("Directions") { openURL(url) }
                        .font(.footnote.weight(.semibold)).foregroundStyle(Theme.accent).frame(minHeight: 44)
                }
                Spacer(minLength: 0)
                if let r = place.hoursRead, let d = Dates.isoDay.date(from: r) {
                    Text("read \(Dates.dayMonth.string(from: d)) \(Calendar.current.component(.year, from: d))")
                        .font(.footnote).foregroundStyle(Theme.muted)
                }
            }
            .buttonStyle(.plain)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
        .opacity(state == "shut" ? 0.72 : 1)
    }

    static func word(_ s: String) -> String { ["open": "Open", "shut": "Shut"][s] ?? "Check" }
    static func ink(_ s: String) -> Color { s == "open" ? Theme.okInk : s == "shut" ? Theme.warnInk : Theme.amberDeep }
    static func fill(_ s: String) -> Color { s == "open" ? Theme.okBg : s == "shut" ? Theme.warnBg : Theme.savedBg }

    /// Apple Maps, walking, to the place's point (nothing about the person is sent).
    static func directions(_ p: PreviewPlace) -> URL? {
        var c = URLComponents(string: "https://maps.apple.com/")
        c?.queryItems = [URLQueryItem(name: "daddr", value: "\(p.lat),\(p.lon)"), URLQueryItem(name: "dirflg", value: "w"),
                         URLQueryItem(name: "q", value: p.name)]
        return c?.url
    }
}

/// On You: the previews this phone has opened, and "Got a preview code?".
struct PreviewSection: View {
    @Environment(AppModel.self) private var model
    @State private var askCode = false
    @State private var code = ""
    @State private var message: String?
    @State private var open: PreviewInfo?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            if !model.previews.isEmpty {
                SectionLabel(text: "Previews")
                ForEach(model.previews) { p in
                    Button { open = p } label: {
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(p.name).font(.headline).foregroundStyle(Theme.ink)
                                Text("\(p.label). Places and opening days only.")
                                    .font(.subheadline).foregroundStyle(Theme.inkTertiary)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                            Spacer()
                            Image(systemName: "chevron.right").foregroundStyle(Theme.muted)
                        }
                        .multilineTextAlignment(.leading)
                        .surfaceCard(padding: 18, radius: 20)
                    }
                    .buttonStyle(PressStyle())
                }
            }
            QuietButton("Got a preview code?") { code = ""; askCode = true }
            if let message {
                Text(message).font(.footnote).foregroundStyle(Theme.muted).fixedSize(horizontal: false, vertical: true)
            }
        }
        .alert("Preview code", isPresented: $askCode) {
            TextField("Code", text: $code)
                .textInputAutocapitalization(.characters)
                .autocorrectionDisabled()
            Button("Open") { Task { message = await model.openPreview(code: code) } }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("A code opens a preview of a place ODYS doesn't fully support yet.")
        }
        .sheet(item: $open) { p in PreviewView(key: p.key).brainFeedback() }
    }
}

/// "Where are you going?": a preview this phone has opened, under London. It opens the preview, not a trip.
struct PreviewCityLines: View {
    @Environment(AppModel.self) private var model
    @State private var open: PreviewInfo?

    var body: some View {
        ForEach(model.previews) { p in
            Button { open = p } label: {
                CityLine(name: p.name, note: "Preview: places only", ready: true)
            }
            .buttonStyle(.plain)
            .accessibilityHint("Opens the preview. Trips there can't be planned yet.")
        }
        .sheet(item: $open) { p in PreviewView(key: p.key).brainFeedback() }
    }
}

/// Help & safety: the emergency number of each country this phone has a preview for (Spain: 112), under 999.
struct PreviewEmergencyLines: View {
    @Environment(AppModel.self) private var model
    @Environment(\.openURL) private var openURL

    var body: some View {
        ForEach(model.previews.filter { ($0.emergencyNumber ?? "999") != "999" }) { p in
            if let n = p.emergencyNumber {
                Button {
                    if let url = URL(string: "tel:\(n)") { openURL(url) }
                } label: {
                    Label("In \(p.countryName): call \(n)", systemImage: "phone.fill")
                }
                .buttonStyle(PillStyle(kind: .secondary, height: 48))
            }
        }
    }
}
