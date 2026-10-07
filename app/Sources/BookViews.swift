import MapKit
import SwiftUI

// D120: the Book tab (ODYS Trips design): flights and stays for the current trip. Your search stays pinned at the top;
// Best / Cheapest / Fastest show their top price and time on the tab; the most-used filters are one-tap chips and the
// rest are in one sheet with a live count. Nothing is booked here: each result opens the provider's own site.

/// What a search depends on: a change to any of it searches again (a moment later, so sliders don't flood).
struct SearchKey: Hashable {
    let trip: UUID
    let segment: BookState.Segment
    let start: String
    let nights: Int
    let adults: Int
    let origin: String?
    let flights: FlightFilters
    let stays: StayFilters
}

struct BookView: View {
    @Environment(AppModel.self) private var model
    @State private var openStay: StayResult?

    var body: some View {
        @Bindable var book = model.book
        NavigationStack {
            Group {
                if let trip = model.currentTrip {
                    BookResults(trip: trip, openStay: $openStay)
                } else {
                    BookEmpty()
                }
            }
            .toolbar(.hidden, for: .navigationBar)
            .navigationDestination(for: Flight.self) { FlightDetailView(flight: $0) }
            .navigationDestination(for: StayResult.self) { StayDetailView(stay: $0) }
            .navigationDestination(item: $openStay) { StayDetailView(stay: $0) }
        }
        .sheet(isPresented: $book.showFilters) {
            Group {
                if book.segment == .flights { FlightFilterSheet() } else { StayFilterSheet() }
            }
            .presentationDetents([.large])
            .presentationCornerRadius(28)
        }
        .sheet(item: $book.handoff) { _ in
            HandoffSheet()
                .presentationDetents([.medium])
                .presentationCornerRadius(28)
        }
        .sheet(isPresented: $book.showAirports) {
            AirportPicker { place in
                guard var trip = model.currentTrip else { return }
                trip.origin = place
                trip.originGuessed = false
                trip.needFlight = true
                model.save(trip)
            }
        }
    }
}

/// No trip yet: one action, the same as on home.
struct BookEmpty: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Spacer()
            ArchMark()
            Text("Flights and places to stay").font(Theme.title).foregroundStyle(Theme.ink)
            Text("Plan a trip first, and I'll search for its dates and travellers. You book on the site you choose.")
                .foregroundStyle(Theme.inkSoft)
                .fixedSize(horizontal: false, vertical: true)
            PrimaryButton(title: "Plan a trip") { model.showCreate = true }
            Spacer()
        }
        .padding(.horizontal, 24)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Theme.background)
    }
}

struct BookResults: View {
    @Environment(AppModel.self) private var model
    let trip: Trip
    @Binding var openStay: StayResult?

    /// Flights only if the trip needs one; stays only if it has nights.
    private var segment: BookState.Segment? {
        switch (trip.needFlight, trip.needStay) {
        case (false, false): return nil
        case (true, false): return .flights
        case (false, true): return .stays
        default: return model.book.segment
        }
    }

    var body: some View {
        let book = model.book
        let seg = segment
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 10, pinnedViews: [.sectionHeaders]) {
                Section {
                    Group {
                        switch seg {
                        case .some(.flights): FlightList(trip: trip)
                        case .some(.stays): StayList(trip: trip, openStay: $openStay)
                        case .none: nothingToBook
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.top, 14)
                    .padding(.bottom, 40)
                } header: {
                    BookHeader(trip: trip, segment: seg)
                }
            }
        }
        .background(Theme.background)
        .statusBarShade()
        .task(id: SearchKey(trip: trip.id, segment: seg ?? .flights, start: trip.start, nights: trip.nights,
                            adults: trip.adults, origin: trip.origin?.code, flights: book.flightFilters,
                            stays: book.stayFilters)) {
            if let seg, book.segment != seg { book.segment = seg }
            guard seg != nil else { return }
            try? await Task.sleep(for: .milliseconds(300))
            guard !Task.isCancelled else { return }
            await model.search()
        }
    }

    private var nothingToBook: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Nothing to book for this trip.").font(Theme.title3).foregroundStyle(Theme.ink)
            Text("It's one day and you don't need a flight. Your day is on the Trip tab.")
                .foregroundStyle(Theme.inkSoft)
                .fixedSize(horizontal: false, vertical: true)
        }
        .surfaceCard(padding: 20, radius: 20)
    }
}

/// The pinned top: Flights / Stays, the search (tap to change), the three sorts with their tops, and the filters.
struct BookHeader: View {
    @Environment(AppModel.self) private var model
    let trip: Trip
    let segment: BookState.Segment?

    var body: some View {
        VStack(spacing: 10) {
            if trip.needFlight && trip.needStay {
                HStack(spacing: 0) {
                    segmentButton("Flights", .flights)
                    segmentButton("Stays", .stays)
                }
                .padding(3)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 12))
            }
            Button {
                model.editingTrip = trip
                model.showCreate = true
            } label: {
                HStack(spacing: 12) {
                    VStack(alignment: .leading, spacing: 1) {
                        Text(searchTitle).font(.body.weight(.semibold)).foregroundStyle(Theme.ink)
                        Text(searchSub).font(.footnote).foregroundStyle(Theme.muted)
                    }
                    Spacer()
                    Text("Edit").font(.subheadline).foregroundStyle(Theme.accent)
                }
                .padding(.horizontal, 16)
                .frame(height: 52)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
            }
            .buttonStyle(PressStyle())
            if segment == .flights { FlightSortTabs() }
            if segment == .stays { StaySortTabs() }
            if segment != nil { FilterChipsRow(segment: segment ?? .flights) }
        }
        .padding(.horizontal, 20)
        .padding(.top, 4)
        .padding(.bottom, 10)
        .background(Theme.background.opacity(0.96))
        .background(.ultraThinMaterial)
        .overlay(alignment: .bottom) { Rectangle().fill(Theme.hairline).frame(height: 1) }
    }

    private func segmentButton(_ title: String, _ s: BookState.Segment) -> some View {
        Button {
            Haptics.light()
            model.book.segment = s
        } label: {
            Text(title)
                .font(.subheadline.weight(.medium))
                .foregroundStyle(Theme.ink)
                .frame(maxWidth: .infinity, minHeight: 36)
                .background(segment == s ? Theme.surfaceHigh : Color.clear, in: RoundedRectangle(cornerRadius: 9))
                .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(segment == s ? .isSelected : [])
    }

    private var searchTitle: String {
        segment == .flights ? "\(trip.origin?.city ?? "Choose where from") → \(trip.city)" : trip.city
    }

    private var searchSub: String {
        let people = "\(trip.adults) \(trip.adults == 1 ? "adult" : "adults")"
        return segment == .flights ? "\(trip.range) · \(people) · return"
                                   : "\(trip.range) · \(trip.lengthLabel) · \(trip.adults) \(trip.adults == 1 ? "guest" : "guests")"
    }
}

struct SortTab: View {
    let label: String
    let sub: String
    let on: Bool
    let action: () -> Void

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            VStack(alignment: .leading, spacing: 1) {
                Text(label).font(.footnote.weight(.semibold)).foregroundStyle(Theme.ink)
                Text(sub).font(.footnote).foregroundStyle(on ? Theme.accent : Theme.muted).lineLimit(1)
                    .minimumScaleFactor(0.8)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 8)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(on ? Theme.selected : Theme.surface, in: RoundedRectangle(cornerRadius: 12))
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(on ? Theme.accent : Color.clear, lineWidth: 1.5))
            .animation(Motion.select, value: on)
        }
        .buttonStyle(PressStyle())
        .accessibilityAddTraits(on ? .isSelected : [])
    }
}

struct FlightSortTabs: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        let tabs = model.book.flights?.tabs ?? [:]
        HStack(spacing: 6) {
            ForEach([("best", "Best"), ("cheapest", "Cheapest"), ("fastest", "Fastest")], id: \.0) { key, label in
                let top = tabs[key] ?? nil
                SortTab(label: label, sub: top.map { "\(Money.whole($0.price)) · \(Dates.duration($0.durationMin))" } ?? "–",
                        on: model.book.flightFilters.sort == key) { model.book.flightFilters.sort = key }
            }
        }
    }
}

struct StaySortTabs: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        let tabs = model.book.stays?.tabs ?? [:]
        HStack(spacing: 6) {
            ForEach([("recommended", "For your days"), ("price", "Cheapest"), ("rating", "Top rated")], id: \.0) { key, label in
                let top = tabs[key] ?? nil
                SortTab(label: label, sub: top.map { Self.sub(key, $0) } ?? "–",
                        on: model.book.stayFilters.sort == key) { model.book.stayFilters.sort = key }
            }
        }
    }

    static func sub(_ key: String, _ t: StayTab) -> String {
        if key == "rating", let r = t.rating { return String(format: "%.1f · ", r) + Money.whole(t.priceNight) }
        return Money.whole(t.priceNight) + (t.distanceKm.map { String(format: " · %.1f km", $0) } ?? "")
    }
}

/// "Filters · 2", then the one-tap ones.
struct FilterChipsRow: View {
    @Environment(AppModel.self) private var model
    let segment: BookState.Segment

    var body: some View {
        let book = model.book
        let count = segment == .flights ? book.flightFilters.count : book.stayFilters.count
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                Button {
                    book.showFilters = true
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "line.3.horizontal.decrease")
                        Text(count > 0 ? "Filters · \(count)" : "Filters")
                    }
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(count > 0 ? Theme.onAccent : Theme.ink)
                    .padding(.horizontal, 14)
                    .frame(height: 36)
                    .background(count > 0 ? Theme.accentFill : Color.clear, in: Capsule())
                    .overlay(Capsule().stroke(count > 0 ? Theme.accent : Theme.outline, lineWidth: 1.5))
                    .frame(minHeight: 44)
                }
                .buttonStyle(PressStyle())
                if segment == .flights { flightChips } else { stayChips }
            }
            .padding(.horizontal, 2)
        }
    }

    @ViewBuilder private var flightChips: some View {
        let book = model.book
        let f = book.flightFilters
        FilterChip(label: "Direct only", on: f.stops == [0]) { book.flightFilters.stops = f.stops == [0] ? [] : [0] }
        FilterChip(label: "Bag included", on: f.checkedBag) { book.flightFilters.checkedBag.toggle() }
        FilterChip(label: "Daytime", on: Set(f.outTimes) == ["morning", "afternoon"]) {
            book.flightFilters.outTimes = Set(f.outTimes) == ["morning", "afternoon"] ? [] : ["morning", "afternoon"]
        }
        FilterChip(label: "Under 12 h", on: f.maxLegMin == 720) { book.flightFilters.maxLegMin = f.maxLegMin == 720 ? nil : 720 }
    }

    @ViewBuilder private var stayChips: some View {
        let book = model.book
        let f = book.stayFilters
        FilterChip(label: "Free cancellation", on: f.refundable) { book.stayFilters.refundable.toggle() }
        FilterChip(label: "8+ rating", on: f.minRating == 8) { book.stayFilters.minRating = f.minRating == 8 ? nil : 8 }
        let whole = StayFilterSheet.wholePlaceKinds(book.stays?.facets.kinds ?? [])
        if !whole.isEmpty {
            FilterChip(label: "Whole place", on: !f.kinds.isEmpty && Set(f.kinds) == Set(whole)) {
                book.stayFilters.kinds = Set(f.kinds) == Set(whole) ? [] : whole
            }
        }
        FilterChip(label: "Under £150", on: f.maxNight == 150) { book.stayFilters.maxNight = f.maxNight == 150 ? nil : 150 }
    }
}

/// "Sample results, made up for testing…": the Brain's note, whenever the results aren't real offers.
struct SourceNote: View {
    let text: String

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "info.circle").foregroundStyle(Theme.accent)
            Text(text).font(.footnote).foregroundStyle(Theme.inkSoft).fixedSize(horizontal: false, vertical: true)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .overlay(RoundedRectangle(cornerRadius: 16).stroke(Theme.outline, lineWidth: 1))
    }
}

/// When nothing matches: one way out.
struct NoMatch: View {
    let title: String
    let line: String
    let clear: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title).font(Theme.serif(22, relativeTo: .title3)).foregroundStyle(Theme.ink)
            Text(line).foregroundStyle(Theme.inkSoft)
            Button("Clear filters", action: clear)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(Theme.onAccent)
                .padding(.horizontal, 18)
                .frame(height: 44)
                .background(Theme.accentFill, in: Capsule())
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 28)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 20))
    }
}

extension String {
    /// "sample" → " · sample prices", for the count line.
    static func priceKind(_ source: String) -> String {
        switch source {
        case "sample": return " · sample prices"
        case "duffel_test", "liteapi_sandbox": return " · test prices"
        default: return ""
        }
    }
}

// ---- flights ---------------------------------------------------------------------------------------------------

struct FlightList: View {
    @Environment(AppModel.self) private var model
    let trip: Trip

    var body: some View {
        let book = model.book
        VStack(alignment: .leading, spacing: 10) {
            if trip.origin == nil {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Where are you flying from?").font(Theme.title3).foregroundStyle(Theme.ink)
                    PrimaryButton(title: "Choose an airport") { book.showAirports = true }
                }
                .surfaceCard(padding: 20, radius: 20)
            } else if let r = book.flights {
                Text("\(r.shown) of \(r.total) flights" + String.priceKind(r.source))
                    .font(.subheadline)
                    .foregroundStyle(Theme.muted)
                    .padding(.horizontal, 4)
                if let note = r.note { SourceNote(text: note) }
                ForEach(r.results) { f in
                    NavigationLink(value: f) { FlightRow(flight: f, adults: trip.adults) }
                        .buttonStyle(PressStyle())
                }
                if r.results.isEmpty, r.total > 0 {
                    NoMatch(title: "No flights match all of that.", line: "Loosening one filter usually helps.") {
                        book.flightFilters = book.flightFilters.cleared()
                    }
                }
                if !r.links.isEmpty {   // 7 Oct: always, for what isn't in these results (Ryanair, Premier Inn…)
                    SectionLabel(text: "Also search").padding(.top, 8)
                    LinksOut(links: r.links)
                }
            } else if let error = book.error {
                ErrorCard(text: error) { Task { await model.search() } }
            } else {
                LoadingCard(text: "Finding flights from \(trip.origin?.city ?? "")…")
            }
        }
    }
}

struct FlightRow: View {
    let flight: Flight
    let adults: Int

    var body: some View {
        let out = flight.outbound
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 10) {
                Text(flight.airlineCode)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(Theme.accent)
                    .frame(width: 30, height: 30)
                    .background(Circle().fill(Theme.surfaceHigh))
                Text(flight.airline).font(.subheadline).foregroundStyle(Theme.inkSoft)
                Spacer(minLength: 4)
                if let tags = flight.tags, !tags.isEmpty {
                    Text(tags.joined(separator: " · "))
                        .font(.caption)
                        .foregroundStyle(Theme.accent)
                        .padding(.horizontal, 9)
                        .padding(.vertical, 3)
                        .background(Color(hex: 0x3A2F1C), in: RoundedRectangle(cornerRadius: 10))
                }
            }
            HStack(alignment: .center, spacing: 12) {
                VStack(alignment: .leading, spacing: 0) {
                    Text(out.departTime).font(.title2.weight(.semibold).monospacedDigit()).foregroundStyle(Theme.ink)
                    Text(out.origin).font(.footnote).foregroundStyle(Theme.muted)
                }
                VStack(spacing: 4) {
                    Text(Dates.duration(out.durationMin)).font(.footnote).foregroundStyle(Theme.muted)
                    ZStack {
                        Rectangle().fill(Color(hex: 0x3A3E46)).frame(height: 2)
                        HStack(spacing: 14) {
                            ForEach(0..<min(out.stops, 3), id: \.self) { _ in
                                Circle().fill(Theme.accent).frame(width: 7, height: 7)
                                    .overlay(Circle().stroke(Theme.surface, lineWidth: 2))
                            }
                        }
                    }
                    Text(out.stops == 0 ? "Direct" : "\(out.stops) stop\(out.stops > 1 ? "s" : "") · \(out.via.joined(separator: ", "))")
                        .font(.footnote)
                        .foregroundStyle(out.stops == 0 ? Theme.accent : Theme.inkSoft)
                        .lineLimit(1)
                }
                .frame(maxWidth: .infinity)
                VStack(alignment: .trailing, spacing: 0) {
                    Text(out.arriveTime).font(.title2.weight(.semibold).monospacedDigit()).foregroundStyle(Theme.ink)
                    Text(out.destination + (out.plusDays > 0 ? " · +\(out.plusDays) day" : ""))
                        .font(.footnote)
                        .foregroundStyle(Theme.muted)
                }
            }
            HStack(alignment: .bottom) {
                VStack(alignment: .leading, spacing: 2) {
                    if let back = flight.inbound {
                        Text("Return \(Dates.shortDay(back.departAt)) · \(Dates.duration(back.durationMin))")
                            .font(.footnote)
                            .foregroundStyle(Theme.muted)
                    }
                    Text(FlightRow.bagLabel(flight.checkedBags))
                        .font(.footnote)
                        .foregroundStyle((flight.checkedBags ?? 0) > 0 ? Theme.inkSoft : Theme.muted)
                }
                Spacer()
                VStack(alignment: .trailing, spacing: 0) {
                    Text(Money.whole(flight.price)).font(Theme.serif(26, relativeTo: .title2)).foregroundStyle(Theme.ink)
                    Text(adults > 1 ? "total for \(adults)" : "return, 1 adult").font(.caption).foregroundStyle(Theme.muted)
                }
            }
            .padding(.top, 10)
            .overlay(alignment: .top) { Rectangle().fill(Theme.hairline).frame(height: 1) }
        }
        .multilineTextAlignment(.leading)
        .padding(16)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 20))
        .accessibilityElement(children: .combine)
    }

    static func bagLabel(_ bags: Int?) -> String {
        guard let bags else { return "Bags: check on the site" }
        return bags > 0 ? "Checked bag included" : "Cabin bag only"
    }
}

struct FlightDetailView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let flight: Flight

    var body: some View {
        let trip = model.currentTrip
        let results = model.book.flights
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Button("‹ Flights") { dismiss() }
                    .foregroundStyle(Theme.accent)
                    .frame(minHeight: 44)
                VStack(alignment: .leading, spacing: 6) {
                    Text(flight.airline).font(.subheadline).foregroundStyle(Theme.muted)
                    PageTitle(text: "\(trip?.origin?.city ?? flight.outbound.origin) to \(trip?.city ?? "London")",
                              font: Theme.serif(32, relativeTo: .largeTitle))
                    if let trip {
                        Text("\(Dates.dayShort.string(from: trip.startDate)) – \(Dates.dayShort.string(from: trip.endDate)) · \(trip.travellers) · economy")
                            .font(.subheadline)
                            .foregroundStyle(Theme.inkSoft)
                    }
                }
                LegCard(label: "Out · \(Dates.shortDay(flight.outbound.departAt))", leg: flight.outbound)
                if let back = flight.inbound {
                    LegCard(label: "Back · \(Dates.shortDay(back.departAt))", leg: back)
                }
                Text(bagNote)
                    .font(.subheadline)
                    .foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
                    .padding(.horizontal, 18)
                    .padding(.vertical, 14)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .overlay(RoundedRectangle(cornerRadius: 18).stroke(Theme.outline, lineWidth: 1))
                FoundPrice(price: flight.price, line: trip.map { $0.adults > 1 ? "total for \($0.adults)" : "return, 1 adult" } ?? "",
                           source: results?.source ?? "sample", searchedAt: results?.searchedAt)
                VStack(alignment: .leading, spacing: 10) {
                    HStack(alignment: .firstTextBaseline) {
                        SectionLabel(text: "Where to book")
                        Spacer()
                        Text("Same dates and travellers").font(.footnote).foregroundStyle(Theme.muted)
                    }
                    ForEach(providers, id: \.name) { link in
                        ProviderRow(name: link.name, note: Self.note(link.name, flight), badge: Self.badge(link.name, flight)) {
                            open(link, trip)
                        }
                    }
                    Text("ODYS earns nothing from these links in this test. Each site sets its own price, so it can differ from the one found here.")
                        .font(.footnote)
                        .foregroundStyle(Theme.muted)
                        .fixedSize(horizontal: false, vertical: true)
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

    /// The Brain's links for this search (Skyscanner, Google Flights), then the airline's own site.
    private var providers: [TripLink] {
        var links = model.book.flights?.links ?? []
        if !flight.sample, let url = Self.search("\(flight.airline) official site") {
            links.append(TripLink(name: flight.airline, url: url.absoluteString))
        }
        return links
    }

    private var bagNote: String {
        let bags: String
        switch flight.checkedBags {
        case .some(let n) where n > 0: bags = "A checked bag is included with this fare."
        case .some: bags = "Cabin bag only with this fare. A checked bag costs extra, and the price differs by site."
        case .none: bags = "This fare doesn't say which bags are included, so check on the site before you pay."
        }
        let refund = flight.refundable == true ? " It can be refunded before you fly." :
            (flight.refundable == false ? " It can't be refunded." : "")
        return bags + refund
    }

    static func note(_ name: String, _ flight: Flight) -> String {
        switch name {
        case "Skyscanner": return "Compares many sites, including this airline"
        case "Google Flights": return "Compares airlines and travel agents"
        default: return "The airline's own site · usually easiest to change later"
        }
    }

    static func badge(_ name: String, _ flight: Flight) -> String? {
        name == flight.airline ? "Official" : (name == "Skyscanner" ? "Compares sites" : nil)
    }

    static func search(_ words: String) -> URL? {
        var c = URLComponents(string: "https://www.google.com/search")
        c?.queryItems = [URLQueryItem(name: "q", value: words)]
        return c?.url
    }

    private func open(_ link: TripLink, _ trip: Trip?) {
        guard let url = URL(string: link.url), let trip else { return }
        let back = flight.inbound
        let sameDay = String(flight.outbound.arriveAt.prefix(10)) == trip.start
        let choice = TripChoice(kind: "flight",
                                title: "\(flight.airline) · \(flight.outbound.departTime) → \(flight.outbound.arriveTime)",
                                provider: link.name, price: flight.price, booked: false,
                                arriveTime: sameDay ? flight.outbound.arriveTime : nil,
                                leaveTime: back.flatMap { $0.departDay == trip.end ? $0.departTime : nil },
                                arrivePlace: flight.outbound.destination, leavePlace: back?.origin)
        model.openHandoff(Handoff(provider: link.name, url: url, what: trip.nights > 0 ? "Return flight" : "Flight",
                                  price: flight.price, searchedAt: model.book.flights?.searchedAt.flatMap(Self.parseDate),
                                  choice: choice))
    }

    static func parseDate(_ s: String) -> Date? {
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return f.date(from: s) ?? ISO8601DateFormatter().date(from: s)
    }
}

struct LegCard: View {
    let label: String
    let leg: FlightLeg

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(text: label)
            HStack(alignment: .top, spacing: 14) {
                VStack(spacing: 4) {
                    Circle().stroke(Theme.accent, lineWidth: 2).frame(width: 9, height: 9)
                    Rectangle().fill(Color(hex: 0x3A3E46)).frame(width: 2).frame(maxHeight: .infinity)
                    Circle().fill(Theme.accent).frame(width: 9, height: 9)
                }
                .frame(width: 10)
                .padding(.top, 6)
                VStack(alignment: .leading, spacing: 8) {
                    (Text(leg.departTime).bold().monospacedDigit() + Text("  \(leg.origin)")).foregroundStyle(Theme.ink)
                    Text(Dates.duration(leg.durationMin) + (leg.stops == 0 ? " · direct" : " · change in \(leg.via.joined(separator: ", "))"))
                        .font(.subheadline)
                        .foregroundStyle(Theme.muted)
                    (Text(leg.arriveTime + (leg.plusDays > 0 ? " +\(leg.plusDays)" : "")).bold().monospacedDigit()
                        + Text("  \(leg.destination)")).foregroundStyle(Theme.ink)
                }
            }
            .fixedSize(horizontal: false, vertical: true)
            if !leg.flightNumbers.isEmpty {
                Text(leg.flightNumbers.joined(separator: " · ")).font(.footnote).foregroundStyle(Theme.muted)
            }
        }
        .padding(.horizontal, 18)
        .padding(.vertical, 16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
        .accessibilityElement(children: .combine)
    }
}

/// The price found here, and what it is: a sample, a test price, or a real offer found n minutes ago.
struct FoundPrice: View {
    let price: Double
    let line: String
    let source: String
    let searchedAt: String?

    var body: some View {
        HStack(alignment: .firstTextBaseline) {
            VStack(alignment: .leading, spacing: 2) {
                Text("Found here").font(.footnote).foregroundStyle(Theme.muted)
                Text(sourceLine).font(.footnote).foregroundStyle(Theme.inkSoft).fixedSize(horizontal: false, vertical: true)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 0) {
                Text(Money.whole(price)).font(Theme.serif(26, relativeTo: .title2)).foregroundStyle(Theme.ink)
                Text(line).font(.caption).foregroundStyle(Theme.muted)
            }
        }
        .padding(16)
        .background(Theme.deep, in: RoundedRectangle(cornerRadius: 16))
    }

    private var sourceLine: String {
        switch source {
        case "sample": return "A sample price, made up for testing"
        case "duffel_test", "liteapi_sandbox": return "A test price, not a real offer"
        default:
            let mins = searchedAt.flatMap(FlightDetailView.parseDate).map { max(0, Int(Date.now.timeIntervalSince($0) / 60)) }
            return mins.map { $0 < 1 ? "Checked just now" : "Checked \($0) minute\($0 == 1 ? "" : "s") ago" } ?? "A real offer"
        }
    }
}

/// One place to book: the name, what it is, and a badge where it helps ("Official").
struct ProviderRow: View {
    let name: String
    let note: String
    var badge: String?
    let action: () -> Void

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 3) {
                    HStack(spacing: 8) {
                        Text(name).font(.body.weight(.semibold)).foregroundStyle(Theme.ink)
                        if let badge {
                            Text(badge)
                                .font(.caption2)
                                .foregroundStyle(Theme.accent)
                                .padding(.horizontal, 7)
                                .padding(.vertical, 2)
                                .background(Theme.surfaceHigh, in: RoundedRectangle(cornerRadius: 8))
                        }
                    }
                    Text(note).font(.footnote).foregroundStyle(Theme.muted).fixedSize(horizontal: false, vertical: true)
                }
                Spacer(minLength: 8)
                Text("›").font(.title3).foregroundStyle(Theme.accent)
            }
            .multilineTextAlignment(.leading)
            .padding(.horizontal, 16)
            .padding(.vertical, 14)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
            .contentShape(RoundedRectangle(cornerRadius: 18))
        }
        .buttonStyle(PressStyle())
        .accessibilityHint("Opens \(name) in Safari")
    }
}

/// When the provider couldn't be searched: the same search on the providers' own sites.
struct LinksOut: View {
    @Environment(\.openURL) private var openURL
    let links: [TripLink]

    var body: some View {
        VStack(spacing: 8) {
            ForEach(links, id: \.name) { link in
                ProviderRow(name: link.name, note: link.note ?? "Search there with the same dates") {
                    if let url = URL(string: link.url) { openURL(url) }
                }
            }
        }
    }
}

struct LoadingCard: View {
    let text: String

    var body: some View {
        HStack(spacing: 12) {
            ProgressView().tint(Theme.accent)
            Text(text).foregroundStyle(Theme.inkSoft)
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 20))
    }
}

struct ErrorCard: View {
    let text: String
    let retry: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(text).foregroundStyle(Theme.inkSoft).fixedSize(horizontal: false, vertical: true)
            SecondaryButton(title: "Try again", action: retry)
        }
        .surfaceCard(padding: 20, radius: 20)
    }
}

// ---- stays -----------------------------------------------------------------------------------------------------

struct StayList: View {
    @Environment(AppModel.self) private var model
    let trip: Trip
    @Binding var openStay: StayResult?

    var body: some View {
        let book = model.book
        VStack(alignment: .leading, spacing: 12) {
            if let r = book.stays {
                HStack {
                    Text("\(r.shown) of \(r.total) places" + String.priceKind(r.source))
                        .font(.subheadline)
                        .foregroundStyle(Theme.muted)
                    Spacer()
                    HStack(spacing: 0) {
                        viewButton("List", on: !book.stayMap) { book.stayMap = false }
                        viewButton("Map", on: book.stayMap) { book.stayMap = true }
                    }
                    .padding(2)
                    .background(Theme.surface, in: RoundedRectangle(cornerRadius: 10))
                }
                .padding(.horizontal, 4)
                if let note = r.note { SourceNote(text: note) }
                if book.stayMap {
                    StayMap(stays: r.results, centre: r.centre) { openStay = $0 }
                        .frame(height: 300)
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                }
                ForEach(r.results) { s in
                    NavigationLink(value: s) { StayCard(stay: s, centre: r.centre) }
                        .buttonStyle(PressStyle())
                }
                if r.results.isEmpty, r.total > 0 {
                    NoMatch(title: "Nothing fits all of that.", line: "Try a higher price or fewer filters.") {
                        book.stayFilters = book.stayFilters.cleared()
                    }
                }
                if !r.links.isEmpty {   // 7 Oct: always, for what isn't in these results (Ryanair, Premier Inn…)
                    SectionLabel(text: "Also search").padding(.top, 8)
                    LinksOut(links: r.links)
                }
            } else if let error = book.error {
                ErrorCard(text: error) { Task { await model.search() } }
            } else {
                LoadingCard(text: "Finding places to stay in \(trip.city)…")
            }
        }
    }

    private func viewButton(_ title: String, on: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.footnote)
                .foregroundStyle(Theme.ink)
                .padding(.horizontal, 12)
                .frame(height: 30)
                .background(on ? Theme.surfaceHigh : Color.clear, in: RoundedRectangle(cornerRadius: 8))
        }
        .buttonStyle(.plain)
        .frame(minHeight: 44)
        .accessibilityAddTraits(on ? .isSelected : [])
    }
}

/// A stay's picture: the provider's photo when there is one, else a field of colour.
struct StayImage: View {
    let stay: StayResult

    var body: some View {
        if let s = stay.photo, let url = URL(string: s) {
            AsyncImage(url: url) { phase in
                if let image = phase.image {
                    image.resizable().scaledToFill()
                } else {
                    Field(feel: Self.feel(stay))
                }
            }
        } else {
            Field(feel: Self.feel(stay))
        }
    }

    /// A stable colour per place (not random per launch).
    static func feel(_ stay: StayResult) -> String {
        let feels = ["Awe", "Calm", "Lively", "Curious", "Browsing", "Active"]
        let n = stay.id.unicodeScalars.reduce(0) { $0 + Int($1.value) }
        return feels[n % feels.count]
    }
}

struct StayCard: View {
    let stay: StayResult
    let centre: String

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Color.clear
                .frame(height: 120)
                .overlay { StayImage(stay: stay) }
                .clipped()
                .overlay(alignment: .topLeading) {
                    if let tags = stay.tags, !tags.isEmpty { pill(tags.joined(separator: " · "), Theme.accent) }
                }
                .overlay(alignment: .topTrailing) { pill(stay.kind.capitalizedFirst, Theme.ink) }
            VStack(alignment: .leading, spacing: 6) {
                HStack(alignment: .top, spacing: 10) {
                    Text(stay.name)
                        .font(Theme.serif(20, relativeTo: .title3))
                        .foregroundStyle(Theme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                    Spacer(minLength: 4)
                    if let r = stay.rating {
                        Text(String(format: "%.1f", r))
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(Theme.ink)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 3)
                            .background(Theme.surfaceHigh, in: RoundedRectangle(cornerRadius: 8))
                    }
                }
                Text(StayCard.where_(stay, centre)).font(.subheadline).foregroundStyle(Theme.inkSoft)
                Text(StayCard.perks(stay)).font(.footnote).foregroundStyle(Theme.muted)
                HStack(alignment: .bottom) {
                    Text(stay.room).font(.footnote).foregroundStyle(Theme.muted).lineLimit(1)
                    Spacer(minLength: 8)
                    VStack(alignment: .trailing, spacing: 0) {
                        Text(Money.whole(stay.priceNight)).font(Theme.serif(24, relativeTo: .title2)).foregroundStyle(Theme.ink)
                        Text("a night · \(Money.whole(stay.priceTotal)) total").font(.caption).foregroundStyle(Theme.muted)
                    }
                }
                .padding(.top, 8)
                .overlay(alignment: .top) { Rectangle().fill(Theme.hairline).frame(height: 1) }
                .padding(.top, 4)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 14)
        }
        .multilineTextAlignment(.leading)
        .background(Theme.surface)
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .accessibilityElement(children: .combine)
    }

    private func pill(_ text: String, _ color: Color) -> some View {
        Text(text)
            .font(.caption)
            .foregroundStyle(color)
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(Theme.background.opacity(0.75), in: RoundedRectangle(cornerRadius: 10))
            .padding(12)
    }

    /// The first part of the address ("Covent Garden").
    static func area(_ stay: StayResult) -> String {
        stay.address.split(separator: ",").first.map(String.init) ?? stay.address
    }

    /// "1 Strand · 0.3 km from Charing Cross"
    static func where_(_ stay: StayResult, _ centre: String) -> String {
        let place = Self.area(stay)
        let km = stay.distanceKm.map { String(format: "%.1f km from %@", $0, centre) }
        return [place.isEmpty ? nil : place, km].compactMap { $0 }.joined(separator: " · ")
    }

    static func perks(_ stay: StayResult) -> String {
        let parts = [stay.refundable == true ? "Free cancellation" : nil, stay.breakfast ? "Breakfast included" : nil]
            .compactMap { $0 }
        return parts.isEmpty ? (stay.refundable == false ? "Can't be refunded" : "Check cancellation terms")
                             : parts.joined(separator: " · ")
    }
}

/// A real map (as for the day plan, D112) with each place's price, and the point the days start from.
struct StayMap: View {
    let stays: [StayResult]
    let centre: String
    let onOpen: (StayResult) -> Void

    var body: some View {
        Map(initialPosition: .region(MKCoordinateRegion(center: AppConfig.start.coordinate,
                                                        span: MKCoordinateSpan(latitudeDelta: 0.08, longitudeDelta: 0.12)))) {
            Annotation(centre, coordinate: AppConfig.start.coordinate) {
                Circle().fill(Theme.accent).frame(width: 10, height: 10)
                    .overlay(Circle().stroke(Theme.background, lineWidth: 2))
            }
            .annotationTitles(.hidden)
            ForEach(stays.filter { $0.point != nil }) { s in
                Annotation(s.name, coordinate: s.point!.coordinate) {
                    Button { onOpen(s) } label: {
                        Text(Money.whole(s.priceNight))
                            .font(.footnote.weight(.semibold))
                            .foregroundStyle(Theme.onAccent)
                            .padding(.horizontal, 10)
                            .frame(height: 30)
                            .background((s.tags ?? []).isEmpty ? Theme.ink : Theme.accent, in: Capsule())
                            .shadow(color: .black.opacity(0.4), radius: 5, y: 4)
                    }
                    .buttonStyle(.plain)
                }
                .annotationTitles(.hidden)          // the prices alone; names would crowd the map
            }
        }
        .mapStyle(.standard(pointsOfInterest: .excludingAll))
        .accessibilityLabel("Map of \(stays.count) places to stay")
    }
}

struct StayDetailView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let stay: StayResult

    var body: some View {
        let trip = model.currentTrip
        let results = model.book.stays
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                Color.clear
                    .frame(height: 300)
                    .overlay { StayImage(stay: stay) }
                    .clipped()
                    .overlay(alignment: .bottomLeading) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text([stay.kind.capitalizedFirst, StayCard.area(stay)].filter { !$0.isEmpty }.joined(separator: " · "))
                                .font(.subheadline)
                                .foregroundStyle(Theme.amberDeep)
                            Text(stay.name)
                                .font(Theme.serif(30, relativeTo: .largeTitle))
                                .foregroundStyle(Theme.ink)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .padding(.horizontal, 24)
                        .padding(.vertical, 22)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(LinearGradient(colors: [.clear, Theme.background], startPoint: .top, endPoint: .bottom))
                    }
                    .overlay(alignment: .topLeading) {
                        Button { dismiss() } label: {
                            Image(systemName: "chevron.left")
                                .font(.title3)
                                .foregroundStyle(Theme.ink)
                                .frame(width: 44, height: 44)
                                .background(.ultraThinMaterial, in: Circle())
                        }
                        .padding(.leading, 20)
                        .padding(.top, 58)
                        .accessibilityLabel("Back to stays")
                    }
                VStack(alignment: .leading, spacing: 20) {
                    HStack(spacing: 10) {
                        fact(stay.rating.map { String(format: "%.1f / 10", $0) } ?? "–",
                             stay.reviews.map { "\($0) guest reviews" } ?? "Guest rating")
                        fact(stay.distanceKm.map { String(format: "%.1f km", $0) } ?? "–",
                             "from \(results?.centre ?? "the centre"), where your days start")
                    }
                    Text(why)
                        .foregroundStyle(Theme.inkSoft)
                        .fixedSize(horizontal: false, vertical: true)
                    FoundPrice(price: stay.priceTotal, line: "\(Money.whole(stay.priceNight)) a night · \(stay.nights) night\(stay.nights == 1 ? "" : "s")",
                               source: results?.source ?? "sample", searchedAt: results?.searchedAt)
                    VStack(alignment: .leading, spacing: 10) {
                        HStack(alignment: .firstTextBaseline) {
                            SectionLabel(text: "Where to book")
                            Spacer()
                            Text(trip?.lengthLabel ?? "").font(.footnote).foregroundStyle(Theme.muted)
                        }
                        ForEach(stay.links, id: \.name) { link in
                            ProviderRow(name: link.name, note: Self.note(link.name),
                                        badge: link.name == "The place's own website" ? "Direct" : nil) {
                                open(link, trip)
                            }
                        }
                        Text("ODYS earns nothing from these links in this test. Each site sets its own price, so check what's included (breakfast, cancellation) before you pay.")
                            .font(.footnote)
                            .foregroundStyle(Theme.muted)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 10)
                .padding(.bottom, 40)
            }
        }
        .ignoresSafeArea(edges: .top)
        .background(Theme.background)
        .toolbar(.hidden, for: .navigationBar)
    }

    private func fact(_ big: String, _ small: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(big).font(Theme.serif(24, relativeTo: .title2)).foregroundStyle(Theme.ink)
            Text(small).font(.footnote).foregroundStyle(Theme.muted).fixedSize(horizontal: false, vertical: true)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 14)
        .frame(maxWidth: .infinity, alignment: .topLeading)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
    }

    private var why: String {
        var parts = ["\(stay.room). \(stay.board)."]
        if stay.refundable == true { parts.append("Free cancellation with this rate.") }
        if stay.refundable == false { parts.append("This rate can't be refunded.") }
        return parts.joined(separator: " ")
    }

    static func note(_ name: String) -> String {
        switch name {
        case "Booking.com": return "This place, with your dates and guests"
        case "The place's own website": return "Often the same price, sometimes with breakfast or a better room"
        default: return "Your dates and guests"
        }
    }

    private func open(_ link: TripLink, _ trip: Trip?) {
        guard let url = URL(string: link.url), let trip else { return }
        let choice = TripChoice(kind: "stay", title: stay.name, provider: link.name, price: stay.priceTotal, booked: false,
                                point: stay.point)
        model.openHandoff(Handoff(provider: link.name, url: url, what: trip.lengthLabel, price: stay.priceTotal,
                                  searchedAt: model.book.stays?.searchedAt.flatMap(FlightDetailView.parseDate),
                                  choice: choice))
    }
}

// ---- the hand-off: going to a provider, and back -------------------------------------------------------------

struct HandoffSheet: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if let h = model.book.handoff {
                if h.back { comeBack(h) } else { going(h) }
            }
        }
        .padding(.horizontal, 24)
        .padding(.top, 26)
        .padding(.bottom, 20)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        .background(Theme.surface)
    }

    @ViewBuilder private func going(_ h: Handoff) -> some View {
        SectionLabel(text: "You're going to")
        Text(h.provider).font(Theme.serif(30, relativeTo: .largeTitle)).foregroundStyle(Theme.ink)
        HStack {
            Text(h.what).font(.subheadline).foregroundStyle(Theme.inkSoft)
            Spacer()
            Text(h.price.map { Money.whole($0) } ?? "See their price").font(.headline).foregroundStyle(Theme.ink)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 14)
        .background(Theme.background, in: RoundedRectangle(cornerRadius: 16))
        Text(goingNote(h))
            .font(.subheadline)
            .foregroundStyle(Theme.muted)
            .fixedSize(horizontal: false, vertical: true)
        PrimaryButton(title: "Continue to \(h.provider) ↗") { model.handoffGo(openURL) }
        QuietButton("Not yet") { model.book.handoff = nil }
            .frame(maxWidth: .infinity)
    }

    @ViewBuilder private func comeBack(_ h: Handoff) -> some View {
        SectionLabel(text: "Welcome back")
        Text("Did you book it on \(h.provider)?")
            .font(Theme.serif(28, relativeTo: .title))
            .foregroundStyle(Theme.ink)
            .fixedSize(horizontal: false, vertical: true)
        PrimaryButton(title: "Yes, add it to my trip") { answer(h, booked: true) }
        SecondaryButton(title: "Not yet, keep it saved") { answer(h, booked: false) }
    }

    private func goingNote(_ h: Handoff) -> String {
        let ago = h.searchedAt.map { max(0, Int(Date.now.timeIntervalSince($0) / 60)) }
        let checked = ago.map { $0 < 1 ? "Price found just now" : "Price found \($0) minute\($0 == 1 ? "" : "s") ago" }
            ?? "The price is on their site"
        return "\(checked), so it can change there. You pay \(h.provider) directly. ODYS earns nothing from this link."
    }

    private func answer(_ h: Handoff, booked: Bool) {
        var choice = h.choice
        choice.booked = booked
        if let id = model.currentTrip?.id { model.keep(choice, in: id) }
        model.book.handoff = nil
    }
}

// ---- filters ----------------------------------------------------------------------------------------------------

/// The sheet's frame: Clear all · Filters · Done, the filters, and "Show 6 flights" with the live count.
struct FilterSheetFrame<Content: View>: View {
    let showLabel: String
    let clear: () -> Void
    @ViewBuilder let content: Content
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Button("Clear all", action: clear).foregroundStyle(Theme.inkSoft).frame(minHeight: 44)
                Spacer()
                Text("Filters").font(.headline).foregroundStyle(Theme.ink)
                Spacer()
                Button("Done") { dismiss() }.foregroundStyle(Theme.accent).frame(minHeight: 44)
            }
            .font(.subheadline)
            .padding(.horizontal, 20)
            .padding(.top, 12)
            .padding(.bottom, 8)
            ScrollView {
                VStack(alignment: .leading, spacing: 22) { content }
                    .padding(.horizontal, 20)
                    .padding(.top, 4)
                    .padding(.bottom, 16)
            }
            VStack {
                PrimaryButton(title: showLabel) { dismiss() }
            }
            .padding(.horizontal, 20)
            .padding(.top, 12)
            .padding(.bottom, 12)
            .overlay(alignment: .top) { Rectangle().fill(Theme.hairline).frame(height: 1) }
        }
        .background(Theme.surface)
    }
}

struct FilterTitle: View {
    let text: String
    var value: String?

    var body: some View {
        HStack {
            Text(text).font(.subheadline.weight(.semibold)).foregroundStyle(Theme.ink)
            Spacer()
            if let value { Text(value).font(.subheadline).foregroundStyle(Theme.accent) }
        }
    }
}

struct FlightFilterSheet: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        let book = model.book
        FilterSheetFrame(showLabel: showLabel(book.flights), clear: { book.flightFilters = book.flightFilters.cleared() }) {
            stopsSection
            timesSection
            journeySection
            priceSection
            bagToggle
            airlinesSection
        }
    }

    private var stopsSection: some View {
        let book = model.book
        let f = book.flightFilters
        return VStack(alignment: .leading, spacing: 10) {
            FilterTitle(text: "Stops")
            HStack(spacing: 8) {
                ForEach([(0, "Direct"), (1, "1 stop"), (2, "2+ stops")], id: \.0) { k, label in
                    OptionTile(label: label, sub: fromPrice(book.flights, k), on: f.stops.isEmpty || f.stops.contains(k)) {
                        book.flightFilters.stops = Self.toggleStop(f.stops, k)
                    }
                }
            }
        }
    }

    private var timesSection: some View {
        let book = model.book
        let f = book.flightFilters
        let times: [(String, String, String)] = [("night", "Night", "00:00–06:00"), ("morning", "Morning", "06:00–12:00"),
                                                 ("afternoon", "Afternoon", "12:00–18:00"), ("evening", "Evening", "18:00–24:00")]
        return VStack(alignment: .leading, spacing: 10) {
            FilterTitle(text: "Leaving \(model.currentTrip?.origin?.city ?? "")")
            LazyVGrid(columns: [GridItem(.flexible(), spacing: 8), GridItem(.flexible(), spacing: 8)], spacing: 8) {
                ForEach(times, id: \.0) { k, label, sub in
                    OptionTile(label: label, sub: sub, on: f.outTimes.contains(k)) {
                        if let i = f.outTimes.firstIndex(of: k) {
                            book.flightFilters.outTimes.remove(at: i)
                        } else {
                            book.flightFilters.outTimes.append(k)
                        }
                    }
                }
            }
        }
    }

    @ViewBuilder private var journeySection: some View {
        let book = model.book
        if let legs = book.flights?.facets.legMinutes, legs.count == 2, legs[0] < legs[1] {
            let hi = Double(legs[1])
            VStack(alignment: .leading, spacing: 8) {
                FilterTitle(text: "Longest journey", value: book.flightFilters.maxLegMin.map { "Up to \(Dates.duration($0))" } ?? "Any")
                Slider(value: Binding(get: { Double(book.flightFilters.maxLegMin ?? Int(hi)) },
                                      set: { v in book.flightFilters.maxLegMin = v >= hi ? nil : Int(v) }),
                       in: Double(legs[0])...hi, step: 30)
                    .tint(Theme.accent)
            }
        }
    }

    @ViewBuilder private var priceSection: some View {
        let book = model.book
        if let prices = book.flights?.facets.price, prices.count == 2, prices[0] < prices[1] {
            let hi = prices[1].rounded(.up)
            VStack(alignment: .leading, spacing: 8) {
                FilterTitle(text: "Most I'll pay", value: book.flightFilters.maxPrice.map { Money.whole($0) } ?? "Any")
                Slider(value: Binding(get: { book.flightFilters.maxPrice ?? hi },
                                      set: { v in book.flightFilters.maxPrice = v >= hi ? nil : v }),
                       in: prices[0].rounded(.down)...hi, step: 10)
                    .tint(Theme.accent)
            }
        }
    }

    private var bagToggle: some View {
        let book = model.book
        return Toggle(isOn: Binding(get: { book.flightFilters.checkedBag }, set: { book.flightFilters.checkedBag = $0 })) {
            VStack(alignment: .leading, spacing: 2) {
                Text("Checked bag included").font(.subheadline.weight(.semibold)).foregroundStyle(Theme.ink)
                Text("At least one bag in the hold, in the fare").font(.footnote).foregroundStyle(Theme.muted)
            }
        }
        .tint(Theme.amberDeep)
    }

    @ViewBuilder private var airlinesSection: some View {
        let book = model.book
        if let airlines = book.flights?.facets.airlines, !airlines.isEmpty {
            VStack(alignment: .leading, spacing: 4) {
                FilterTitle(text: "Airlines").padding(.bottom, 6)
                ForEach(airlines, id: \.name) { a in
                    AirlineRow(name: a.name, price: a.minPrice, on: book.flightFilters.airlines.contains(a.name)) {
                        if let i = book.flightFilters.airlines.firstIndex(of: a.name) {
                            book.flightFilters.airlines.remove(at: i)
                        } else {
                            book.flightFilters.airlines.append(a.name)
                        }
                    }
                }
            }
        }
    }

    /// Empty means every number of stops; a tap on one of all three keeps the other two.
    static func toggleStop(_ stops: [Int], _ k: Int) -> [Int] {
        var s = stops.isEmpty ? [0, 1, 2] : stops
        if let i = s.firstIndex(of: k) {
            if s.count > 1 { s.remove(at: i) }
        } else {
            s.append(k)
        }
        s.sort()
        return s == [0, 1, 2] ? [] : s
    }

    private func fromPrice(_ r: FlightResults?, _ k: Int) -> String {
        let ps = (r?.facets.stops ?? []).filter { min($0.stops, 2) == k }.map(\.minPrice)
        return ps.min().map { "from \(Money.whole($0))" } ?? "none"
    }

    private func showLabel(_ r: FlightResults?) -> String {
        guard let r else { return "Show flights" }
        return r.shown == 0 ? "No flights match" : "Show \(r.shown) flight\(r.shown == 1 ? "" : "s")"
    }
}

struct AirlineRow: View {
    let name: String
    let price: Double
    let on: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                TickBox(on: on)
                Text(name).foregroundStyle(Theme.ink)
                Spacer()
                Text(Money.whole(price)).font(.footnote).foregroundStyle(Theme.muted)
            }
            .font(.subheadline)
            .frame(minHeight: 44)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(on ? .isSelected : [])
    }
}

struct StayFilterSheet: View {
    @Environment(AppModel.self) private var model

    /// The provider's words for a whole flat or house ("Apartment", "Holiday home" …).
    static func wholePlaceKinds(_ kinds: [KindFacet]) -> [String] {
        kinds.map(\.kind).filter { k in ["apartment", "flat", "home", "house", "villa", "studio"].contains { k.lowercased().contains($0) } }
    }

    var body: some View {
        let book = model.book
        let r = book.stays
        let f = book.stayFilters
        FilterSheetFrame(showLabel: showLabel(r), clear: { book.stayFilters = f.cleared() }) {
            if let prices = r?.facets.priceNight, prices.count == 2, prices[0] < prices[1] {
                let lo = prices[0].rounded(.down), hi = prices[1].rounded(.up)
                VStack(alignment: .leading, spacing: 8) {
                    FilterTitle(text: "Most per night", value: f.maxNight.map { Money.whole($0) } ?? "Any")
                    Slider(value: Binding(get: { f.maxNight ?? hi },
                                          set: { v in book.stayFilters.maxNight = v >= hi ? nil : v }),
                           in: lo...hi, step: 5)
                        .tint(Theme.accent)
                }
            }
            if let kinds = r?.facets.kinds, !kinds.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    FilterTitle(text: "Type of place")
                    LazyVGrid(columns: [GridItem(.flexible(), spacing: 8), GridItem(.flexible(), spacing: 8)], spacing: 8) {
                        ForEach(kinds, id: \.kind) { k in
                            OptionTile(label: k.kind.capitalizedFirst, sub: "\(k.count) place\(k.count == 1 ? "" : "s")",
                                       on: f.kinds.contains(k.kind)) {
                                if let i = f.kinds.firstIndex(of: k.kind) { book.stayFilters.kinds.remove(at: i) }
                                else { book.stayFilters.kinds.append(k.kind) }
                            }
                        }
                    }
                }
            }
            VStack(alignment: .leading, spacing: 10) {
                FilterTitle(text: "Guest rating")
                HStack(spacing: 0) {
                    ForEach([(nil, "Any"), (7.0, "7+"), (8.0, "8+"), (9.0, "9+")] as [(Double?, String)], id: \.1) { v, label in
                        Button {
                            Haptics.light()
                            book.stayFilters.minRating = v
                        } label: {
                            Text(label)
                                .font(.subheadline)
                                .foregroundStyle(Theme.ink)
                                .frame(maxWidth: .infinity, minHeight: 36)
                                .background(f.minRating == v ? Theme.surfaceHigh : Color.clear, in: RoundedRectangle(cornerRadius: 9))
                                .contentShape(Rectangle())
                        }
                        .buttonStyle(.plain)
                        .accessibilityAddTraits(f.minRating == v ? .isSelected : [])
                    }
                }
                .padding(3)
                .background(Theme.background, in: RoundedRectangle(cornerRadius: 12))
            }
            Toggle(isOn: Binding(get: { f.refundable }, set: { book.stayFilters.refundable = $0 })) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Free cancellation").font(.subheadline.weight(.semibold)).foregroundStyle(Theme.ink)
                    Text("With the rate found here").font(.footnote).foregroundStyle(Theme.muted)
                }
            }
            .tint(Theme.amberDeep)
            Toggle(isOn: Binding(get: { f.breakfast }, set: { book.stayFilters.breakfast = $0 })) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Breakfast").font(.subheadline.weight(.semibold)).foregroundStyle(Theme.ink)
                    Text("Included in the rate").font(.footnote).foregroundStyle(Theme.muted)
                }
            }
            .tint(Theme.amberDeep)
        }
    }

    private func showLabel(_ r: StayResults?) -> String {
        guard let r else { return "Show places" }
        return r.shown == 0 ? "Nothing matches" : "Show \(r.shown) place\(r.shown == 1 ? "" : "s")"
    }
}
