package com.odys.app

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowLeft
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.material.icons.outlined.Info
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveableStateHolder
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.SubcomposeAsyncImage
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.net.URLEncoder
import java.time.Duration
import java.time.OffsetDateTime
import java.util.Locale

// D120: the Book tab (ODYS Trips design): flights and stays for the current trip (app/Sources/BookViews.swift). The
// search stays at the top; Best / Cheapest / Fastest show their top price and time; the most-used filters are one-tap
// chips and the rest are in one sheet with a live count. Nothing is booked here: each result opens the provider's site.

/** What a search depends on: a change to any of it searches again (a moment later, so sliders don't flood). */
private data class SearchKey(val trip: String, val segment: String, val start: String, val nights: Int, val adults: Int,
                             val origin: String?, val flights: FlightFilters, val stays: StayFilters)

@Composable
fun BookView(model: AppModel, onHelp: () -> Unit) {
    val holder = rememberSaveableStateHolder()
    val top = model.bookPath.lastOrNull()
    var showAirports by remember { mutableStateOf(false) }
    val pop: () -> Unit = { if (model.bookPath.isNotEmpty()) model.bookPath.removeAt(model.bookPath.lastIndex) }
    BackHandler(enabled = top != null, onBack = pop)
    holder.SaveableStateProvider("${model.bookPath.size}:${top.hashCode()}") {
        when (top) {
            null -> {
                val trip = model.currentTrip
                if (trip == null) BookEmpty(model) else BookResults(model, trip, onHelp) { showAirports = true }
            }
            is BookDest.FlightDetail -> FlightDetailView(model, top.flight, pop)
            is BookDest.StayDetail -> StayDetailView(model, top.stay, pop)
        }
    }
    if (model.book.showFilters) {
        if (model.book.segment == "flights") FlightFilterSheet(model) else StayFilterSheet(model)
    }
    if (showAirports) {
        AirportPicker(model, { showAirports = false }) { place ->
            model.currentTrip?.let { model.save(it.copy(origin = place, originGuessed = false, needFlight = true)) }
            showAirports = false
        }
    }
}

/** No trip yet: one action, the same as on home. */
@Composable
fun BookEmpty(model: AppModel) {
    Column(Modifier.fillMaxSize().padding(horizontal = 24.dp), verticalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterVertically)) {
        ArchMark()
        Text("Flights and places to stay", style = Theme.title)
        Text("Plan a trip first, and I'll search for its dates and travellers. You book on the site you choose.",
            style = Theme.body.copy(color = Theme.inkSoft))
        PrimaryButton("Plan a trip") { model.showCreate = true }
    }
}

@Composable
fun BookResults(model: AppModel, trip: Trip, onHelp: () -> Unit, chooseAirport: () -> Unit) {
    val book = model.book
    // flights only if the trip needs one; stays only if it has nights
    val seg: String? = when {
        !trip.needFlight && !trip.needStay -> null
        trip.needFlight && !trip.needStay -> "flights"
        !trip.needFlight && trip.needStay -> "stays"
        else -> book.segment
    }
    LaunchedEffect(SearchKey(trip.id, seg ?: "flights", trip.start, trip.nights, trip.adults, trip.origin?.code,
        book.flightFilters, book.stayFilters)) {
        if (seg != null && book.segment != seg) book.segment = seg
        if (seg == null) return@LaunchedEffect
        delay(300)
        model.search()
    }
    Column(Modifier.fillMaxSize()) {
        BookHeader(model, trip, seg, onHelp)
        Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 16.dp)
            .padding(top = 14.dp, bottom = 40.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            when (seg) {
                "flights" -> FlightList(model, trip, chooseAirport)
                "stays" -> StayList(model, trip)
                else -> Column(Modifier.surfaceCard(padding = 20.dp, radius = 20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("Nothing to book for this trip.", style = Theme.title3)
                    Text("It's one day and you don't need a flight. Your day is on the home screen.", style = Theme.body.copy(color = Theme.inkSoft))
                }
            }
        }
    }
}

/** The top: Flights / Stays, the search (tap to change), the three sorts with their tops, and the filters. */
@Composable
fun BookHeader(model: AppModel, trip: Trip, segment: String?, onHelp: () -> Unit) {
    val book = model.book
    Column(Modifier.fillMaxWidth().background(Theme.background).padding(horizontal = 20.dp).padding(top = 4.dp, bottom = 10.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {   // m176: the way back to the trip, and Help, on Book too
            ArrowLink("Your trip") {   // D131: flights and stays sit inside the trip, so back goes to it
                if (model.tripPath.lastOrNull() == Dest.Book) model.tripPath.removeAt(model.tripPath.lastIndex)
                if (model.tripPath.lastOrNull() != Dest.TripOverview(trip.id)) {
                    model.tripPath.clear()
                    model.tripPath += Dest.TripOverview(trip.id)
                }
            }
            Spacer(Modifier.weight(1f))
            HelpPill(model.unreadSafety, onHelp)
        }
        if (trip.needFlight && trip.needStay) {
            Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)).background(Theme.surface).padding(3.dp)) {
                for ((title, s) in listOf("Flights" to "flights", "Stays" to "stays")) {
                    Box(Modifier.weight(1f).heightIn(min = 40.dp).clip(RoundedCornerShape(9.dp))
                        .background(if (segment == s) Theme.surfaceHigh else Color.Transparent)
                        .clickable(role = Role.Tab) { book.segment = s }.semantics { selected = segment == s },
                        contentAlignment = Alignment.Center) {
                        Text(title, style = Theme.subheadline.copy(fontWeight = FontWeight.Medium))
                    }
                }
            }
        }
        val people = "${trip.adults} ${if (trip.adults == 1) "adult" else "adults"}"
        val title = if (segment == "flights") "${trip.origin?.city ?: "Choose where from"} → ${trip.city}" else trip.city
        val sub = if (segment == "flights") "${trip.range} · $people · return"
                  else "${trip.range} · ${trip.lengthLabel} · ${trip.adults} ${if (trip.adults == 1) "guest" else "guests"}"
        Row(Modifier.fillMaxWidth().height(52.dp).pressable {
            model.editingTrip = trip
            model.showCreate = true
        }.clip(RoundedCornerShape(16.dp)).background(Theme.surface).padding(horizontal = 16.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text(title, style = Theme.headline, maxLines = 1)
                Text(sub, style = Theme.footnote, maxLines = 1)
            }
            Text("Edit", style = Theme.subheadline.copy(color = Theme.accent))
        }
        if (segment == "flights") {
            val tabs = book.flights?.tabs ?: emptyMap()
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                for ((key, label) in listOf("best" to "Best", "cheapest" to "Cheapest", "fastest" to "Fastest")) {
                    val t = tabs[key]
                    SortTab(label, t?.let { "${Money.whole(it.price)} · ${Dates.duration(it.durationMin)}" } ?: "–",
                        book.flightFilters.sort == key, Modifier.weight(1f)) { book.flightFilters = book.flightFilters.copy(sort = key) }
                }
            }
            // m191 (design review): "Best" is a judgement, so say whose
            if (book.flightFilters.sort == "best") Text("Best balances price and journey time.", style = Theme.footnote)
        }
        if (segment == "stays") {
            val tabs = book.stays?.tabs ?: emptyMap()
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                for ((key, label) in listOf("recommended" to "For your days", "price" to "Cheapest", "rating" to "Top rated")) {
                    val t = tabs[key]
                    val s = t?.let {
                        if (key == "rating" && it.rating != null) String.format(Locale.UK, "%.1f · ", it.rating) + Money.whole(it.priceNight)
                        else Money.whole(it.priceNight) + (it.distanceKm?.let { km -> String.format(Locale.UK, " · %.1f km", km) } ?: "")
                    } ?: "–"
                    SortTab(label, s, book.stayFilters.sort == key, Modifier.weight(1f)) { book.stayFilters = book.stayFilters.copy(sort = key) }
                }
            }
        }
        if (segment != null) FilterChipsRow(model, segment)
    }
    Box(Modifier.fillMaxWidth().height(1.dp).background(Theme.hairline))
}

@Composable
fun SortTab(label: String, sub: String, on: Boolean, modifier: Modifier = Modifier, onClick: () -> Unit) {
    Column(modifier.pressable(haptic = true, onClick = onClick).semantics { selected = on }.clip(RoundedCornerShape(12.dp))
        .background(if (on) Theme.selected else Theme.surface).border(1.5.dp, if (on) Theme.accent else Color.Transparent, RoundedCornerShape(12.dp))
        .padding(horizontal = 10.dp, vertical = 8.dp), verticalArrangement = Arrangement.spacedBy(1.dp)) {
        Text(label, style = Theme.footnote.copy(color = Theme.ink, fontWeight = FontWeight.SemiBold))
        Text(sub, style = Theme.footnote.copy(color = if (on) Theme.accent else Theme.muted), maxLines = 1)
    }
}

/** "Filters · 2", then the one-tap ones. */
@Composable
fun FilterChipsRow(model: AppModel, segment: String) {
    val book = model.book
    val count = if (segment == "flights") book.flightFilters.count else book.stayFilters.count
    Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically) {
        Row(Modifier.heightIn(min = 44.dp).pressable { book.showFilters = true }, verticalAlignment = Alignment.CenterVertically) {
            Row(Modifier.clip(CircleShape).background(if (count > 0) Theme.accent else Color.Transparent)
                .border(1.5.dp, if (count > 0) Theme.accent else Theme.outline, CircleShape).padding(horizontal = 14.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                val color = if (count > 0) Theme.onAccent else Theme.ink
                Icon(Icons.Filled.FilterList, null, tint = color, modifier = Modifier.size(16.dp))
                Text(if (count > 0) "Filters · $count" else "Filters", style = Theme.subheadline.copy(color = color, fontWeight = FontWeight.SemiBold))
            }
        }
        if (segment == "flights") {
            val f = book.flightFilters
            FilterChipPill("Direct only", f.stops == listOf(0)) { book.flightFilters = f.copy(stops = if (f.stops == listOf(0)) emptyList() else listOf(0)) }
            FilterChipPill("Bag included", f.checkedBag) { book.flightFilters = f.copy(checkedBag = !f.checkedBag) }
            val day = setOf("morning", "afternoon")
            FilterChipPill("Daytime", f.outTimes.toSet() == day) {
                book.flightFilters = f.copy(outTimes = if (f.outTimes.toSet() == day) emptyList() else day.toList())
            }
            FilterChipPill("Under 12 h", f.maxLegMin == 720) { book.flightFilters = f.copy(maxLegMin = if (f.maxLegMin == 720) null else 720) }
        } else {
            val f = book.stayFilters
            FilterChipPill("Free cancellation", f.refundable) { book.stayFilters = f.copy(refundable = !f.refundable) }
            FilterChipPill("8+ rating", f.minRating == 8.0) { book.stayFilters = f.copy(minRating = if (f.minRating == 8.0) null else 8.0) }
            val whole = wholePlaceKinds(book.stays?.facets?.kinds ?: emptyList())
            if (whole.isNotEmpty()) {
                val on = f.kinds.isNotEmpty() && f.kinds.toSet() == whole.toSet()
                FilterChipPill("Whole place", on) { book.stayFilters = f.copy(kinds = if (on) emptyList() else whole) }
            }
            FilterChipPill("Under £150", f.maxNight == 150.0) { book.stayFilters = f.copy(maxNight = if (f.maxNight == 150.0) null else 150.0) }
        }
    }
}

/** The provider's words for a whole flat or house ("Apartment", "Holiday home" …). */
fun wholePlaceKinds(kinds: List<KindFacet>): List<String> =
    kinds.map { it.kind }.filter { k -> listOf("apartment", "flat", "home", "house", "villa", "studio").any { k.lowercase().contains(it) } }

/** "Sample results, made up for testing…": the Brain's note, whenever the results aren't real offers. */
@Composable
fun SourceNote(text: String) {
    Row(Modifier.fillMaxWidth().border(1.dp, Theme.outline, RoundedCornerShape(16.dp)).padding(14.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp)) {
        Icon(Icons.Outlined.Info, null, tint = Theme.accent, modifier = Modifier.size(18.dp))
        Text(text, style = Theme.footnote.copy(color = Theme.inkSoft))
    }
}

/** When nothing matches: one way out. */
@Composable
fun NoMatch(title: String, line: String, clear: () -> Unit) {
    Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(20.dp)).background(Theme.surface).padding(horizontal = 20.dp, vertical = 28.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(title, style = Theme.serif(22.sp))
        Text(line, style = Theme.body.copy(color = Theme.inkSoft))
        Box(Modifier.height(44.dp).clip(CircleShape).background(Theme.accent).clickable(role = Role.Button, onClick = clear)
            .padding(horizontal = 18.dp), contentAlignment = Alignment.Center) {
            Text("Clear filters", style = Theme.subheadline.copy(color = Theme.onAccent, fontWeight = FontWeight.SemiBold))
        }
    }
}

/** "sample" → " · sample prices", for the count line. */
fun priceKind(source: String) = when (source) {
    "sample" -> " · sample prices"
    "duffel_test", "liteapi_sandbox" -> " · test prices"
    else -> ""
}

// ---- flights ---------------------------------------------------------------------------------------------------

@Composable
fun FlightList(model: AppModel, trip: Trip, chooseAirport: () -> Unit) {
    val book = model.book
    val scope = rememberCoroutineScope()
    val r = book.flights
    val error = book.error
    when {
        trip.origin == null -> Column(Modifier.surfaceCard(padding = 20.dp, radius = 20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("Where are you flying from?", style = Theme.title3)
            PrimaryButton("Choose an airport", onClick = chooseAirport)
        }
        r != null -> {
            Text("${r.shown} of ${r.total} flights" + priceKind(r.source), style = Theme.subheadline.copy(color = Theme.muted),
                modifier = Modifier.padding(horizontal = 4.dp))
            r.note?.let { SourceNote(it) }
            for (f in r.results) FlightRow(f, trip.adults) { model.bookPath += BookDest.FlightDetail(f) }
            if (r.results.isEmpty() && r.total > 0) {
                NoMatch("No flights match all of that.", "Loosening one filter usually helps.") { book.flightFilters = book.flightFilters.cleared() }
            }
            if (r.links.isNotEmpty()) {   // 7 Oct: always, for what isn't in these results
                SectionLabel("Also search", Modifier.padding(top = 8.dp))
                LinksOut(r.links)
            }
        }
        error != null -> ErrorCard(error) { scope.launch { model.search() } }
        else -> LoadingCard("Finding flights from ${trip.origin.city}…")
    }
}

/** "Back Sun 12 Oct · 18:40 → 21:05 · direct" (9 Oct, Abram: the flight home's own times, not only its day). */
fun backLine(back: FlightLeg): String {
    val plus = if (back.plusDays > 0) " +${back.plusDays}" else ""
    val stops = if (back.stops == 0) "direct" else if (back.stops == 1) "1 stop" else "${back.stops} stops"
    return "Back ${Dates.shortDay(back.departAt)} · ${back.departTime} → ${back.arriveTime}$plus · $stops"
}

fun bagLabel(bags: Int?): String = when {
    bags == null -> "Bags: check on the site"
    bags > 0 -> "Checked bag included"
    else -> "Cabin bag only"
}

@Composable
fun FlightRow(flight: Flight, adults: Int, onClick: () -> Unit) {
    val out = flight.outbound
    Column(Modifier.fillMaxWidth().pressable(onClick = onClick).clip(RoundedCornerShape(20.dp)).background(Theme.surface).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Box(Modifier.size(30.dp).background(Theme.surfaceHigh, CircleShape), contentAlignment = Alignment.Center) {
                Text(flight.airlineCode, style = Theme.caption.copy(color = Theme.accent, fontWeight = FontWeight.Bold, fontSize = 11.sp))
            }
            Text(flight.airline, style = Theme.subheadline.copy(color = Theme.inkSoft), modifier = Modifier.weight(1f))
            val tags = flight.tags
            if (!tags.isNullOrEmpty()) {
                Text(tags.joinToString(" · "), style = Theme.caption.copy(color = Theme.accent),
                    modifier = Modifier.clip(RoundedCornerShape(10.dp)).background(Theme.savedBg).padding(horizontal = 9.dp, vertical = 3.dp))
            }
        }
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            Column {
                Text(out.departTime, style = Theme.title2Sans)
                Text(out.origin, style = Theme.footnote)
            }
            Column(Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(Dates.duration(out.durationMin), style = Theme.footnote)
                Box(Modifier.fillMaxWidth().height(8.dp), contentAlignment = Alignment.Center) {
                    Box(Modifier.fillMaxWidth().height(2.dp).background(Theme.track))
                    Row(horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                        repeat(minOf(out.stops, 3)) {
                            Box(Modifier.size(7.dp).background(Theme.accent, CircleShape).border(2.dp, Theme.surface, CircleShape))
                        }
                    }
                }
                Text(if (out.stops == 0) "Direct" else "${out.stops} stop${if (out.stops > 1) "s" else ""} · ${out.via.joinToString(", ")}",
                    style = Theme.footnote.copy(color = if (out.stops == 0) Theme.accent else Theme.inkSoft), maxLines = 1)
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(out.arriveTime, style = Theme.title2Sans)
                Text(out.destination + if (out.plusDays > 0) " · +${out.plusDays} day" else "", style = Theme.footnote)
            }
        }
        Hairline()
        Row(verticalAlignment = Alignment.Bottom) {
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                flight.inbound?.let { Text(backLine(it), style = Theme.footnote.copy(color = Theme.inkSoft), maxLines = 2) }
                Text(bagLabel(flight.checkedBags), style = Theme.footnote.copy(color = if ((flight.checkedBags ?: 0) > 0) Theme.inkSoft else Theme.muted))
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(Money.whole(flight.price), style = Theme.serif(26.sp))
                Text(if (adults > 1) "total for $adults" else "return, 1 adult", style = Theme.caption)
            }
        }
    }
}

/** A Google search for an airline's own site (the Brain gives the comparison sites; this adds the airline). */
private fun searchUrl(words: String) = "https://www.google.com/search?q=" + URLEncoder.encode(words, "UTF-8")

private fun minutesAgo(iso: String?): Long? = iso?.let {
    runCatching { Duration.between(OffsetDateTime.parse(it).toInstant(), java.time.Instant.now()).toMinutes().coerceAtLeast(0) }.getOrNull()
}

@Composable
fun FlightDetailView(model: AppModel, flight: Flight, onBack: () -> Unit) {
    val trip = model.currentTrip
    val results = model.book.flights
    val providers = (results?.links ?: emptyList()) +
        if (!flight.sample) listOf(TripLink(flight.airline, searchUrl("${flight.airline} official site"))) else emptyList()
    val bags = when {
        flight.checkedBags == null -> "This fare doesn't say which bags are included, so check on the site before you pay."
        flight.checkedBags > 0 -> "A checked bag is included with this fare."
        else -> "Cabin bag only with this fare. A checked bag costs extra, and the price differs by site."
    }
    val refund = when (flight.refundable) {
        true -> " It can be refunded before you fly."
        false -> " It can't be refunded."
        null -> ""
    }

    fun open(link: TripLink) {
        val t = trip ?: return
        val back = flight.inbound
        val landing = flight.outbound.arriveAt.take(10)
        val sameDay = landing == t.start
        // journey round 2: an overnight flight lands the next day; keeping it moves the trip's first day to then
        val nextDay = landing == t.startDate.plusDays(1).toString()
        val choice = TripChoice("flight", "${flight.airline} · ${flight.outbound.departTime} → ${flight.outbound.arriveTime}",
            link.name, flight.price, false,
            arriveTime = if (sameDay || nextDay) flight.outbound.arriveTime else null,
            leaveTime = back?.let { if (it.departDay == t.end) it.departTime else null },
            arrivePlace = flight.outbound.destination, leavePlace = back?.origin, sample = flight.sample,
            landsNextDay = if (nextDay && t.nights >= 1) true else null)
        model.openHandoff(Handoff(link.name, link.url, if (t.nights > 0) "Return flight" else "Flight", flight.price,
            results?.searchedAt, choice))
    }

    ScrollPage(spacing = 20, bottom = 40) {
        BackLink("Back to flights", onClick = onBack)   // 19 Oct review: Android's arrow
        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(flight.airline, style = Theme.subheadline.copy(color = Theme.muted))
            PageTitle("${trip?.origin?.city ?: flight.outbound.origin} to ${trip?.city ?: "London"}", style = Theme.serif(32.sp))
            if (trip != null) {
                // 19 Oct review: these are the days in London; each flight's own date is on its leg below
                Text("In ${trip.city} ${Dates.dayShort(trip.startDate)} – ${Dates.dayShort(trip.endDate)} · ${trip.travellers} · economy",
                    style = Theme.subheadline.copy(color = Theme.inkSoft))
            }
        }
        LegCard("Out · ${Dates.shortDay(flight.outbound.departAt)}", flight.outbound)
        flight.inbound?.let { LegCard("Back · ${Dates.shortDay(it.departAt)}", it) }
        Text(bags + refund, style = Theme.subheadline.copy(color = Theme.inkSoft),
            modifier = Modifier.fillMaxWidth().border(1.dp, Theme.outline, RoundedCornerShape(18.dp)).padding(horizontal = 18.dp, vertical = 14.dp))
        FoundPrice(flight.price, trip?.let { if (it.adults > 1) "total for ${it.adults}" else "return, 1 adult" } ?: "",
            results?.source ?: "sample", results?.searchedAt)
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                SectionLabel("Where to book", Modifier.weight(1f))
                Text("Same dates and travellers", style = Theme.footnote)
            }
            // 19 Oct review: said next to the links, before anyone taps one
            Text("ODYS earns nothing from these links while we test. You pay the site you book with, and each sets its own price, so it can differ from the one found here.",
                style = Theme.footnote.copy(color = Theme.inkSoft))
            for (link in providers) {
                val note = when (link.name) {
                    "Skyscanner" -> "Compares many sites, including this airline"
                    "Google Flights" -> "Compares airlines and travel agents"
                    else -> "The airline's own site · usually easiest to change later"
                }
                val badge = if (link.name == flight.airline) "Official" else if (link.name == "Skyscanner") "Compares sites" else null
                ProviderRow(link.name, note, badge) { open(link) }
            }
        }
    }
}

@Composable
fun LegCard(label: String, leg: FlightLeg) {
    Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface).padding(horizontal = 18.dp, vertical = 16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)) {
        SectionLabel(label)
        Row(Modifier.height(IntrinsicSize.Min), horizontalArrangement = Arrangement.spacedBy(14.dp)) {
            Column(Modifier.width(10.dp).fillMaxHeight().padding(top = 6.dp, bottom = 6.dp), horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Box(Modifier.size(9.dp).border(2.dp, Theme.accent, CircleShape))
                Box(Modifier.width(2.dp).weight(1f).background(Theme.track))
                Box(Modifier.size(9.dp).background(Theme.accent, CircleShape))
            }
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(fontWeight = FontWeight.Bold)) { append(leg.departTime) }
                    append("  ${leg.origin}")
                }, style = Theme.body)
                Text(Dates.duration(leg.durationMin) + if (leg.stops == 0) " · direct" else " · change in ${leg.via.joinToString(", ")}",
                    style = Theme.subheadline.copy(color = Theme.muted))
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(fontWeight = FontWeight.Bold)) { append(leg.arriveTime + if (leg.plusDays > 0) " +${leg.plusDays}" else "") }
                    append("  ${leg.destination}")
                }, style = Theme.body)
            }
        }
        if (leg.flightNumbers.isNotEmpty()) Text(leg.flightNumbers.joinToString(" · "), style = Theme.footnote)
    }
}

/** The price found here, and what it is: a sample, a test price, or a real offer found n minutes ago. */
@Composable
fun FoundPrice(price: Double, line: String, source: String, searchedAt: String?) {
    val sourceLine = when (source) {
        "sample" -> "A sample price, made up for testing"
        "duffel_test", "liteapi_sandbox" -> "A test price, not a real offer"
        else -> minutesAgo(searchedAt)?.let { if (it < 1) "Checked just now" else "Checked $it minute${if (it == 1L) "" else "s"} ago" } ?: "A real offer"
    }
    Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(16.dp)).background(Theme.deep).padding(16.dp), verticalAlignment = Alignment.Bottom) {
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text("Found here", style = Theme.footnote)
            Text(sourceLine, style = Theme.footnote.copy(color = Theme.inkSoft))
        }
        Column(horizontalAlignment = Alignment.End) {
            Text(Money.whole(price), style = Theme.serif(26.sp))
            Text(line, style = Theme.caption)
        }
    }
}

/** One place to book: the name, what it is, and a badge where it helps ("Official"). */
@Composable
fun ProviderRow(name: String, note: String, badge: String? = null, onClick: () -> Unit) {
    Row(Modifier.fillMaxWidth().pressable(haptic = true, onClick = onClick).clip(RoundedCornerShape(18.dp)).background(Theme.surface)
        .padding(horizontal = 16.dp, vertical = 14.dp).semantics { contentDescription = "$name. $note. Opens in your browser" },
        verticalAlignment = Alignment.CenterVertically) {
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(3.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                Text(name, style = Theme.headline)
                if (badge != null) {
                    Text(badge, style = Theme.caption.copy(color = Theme.accent, fontSize = 11.sp),
                        modifier = Modifier.clip(RoundedCornerShape(8.dp)).background(Theme.surfaceHigh).padding(horizontal = 7.dp, vertical = 2.dp))
                }
            }
            Text(note, style = Theme.footnote)
        }
        Text("›", style = Theme.title3.copy(color = Theme.accent))
    }
}

/** The same search on the providers' own sites. */
@Composable
fun LinksOut(links: List<TripLink>) {
    val context = LocalContext.current
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        for (link in links) ProviderRow(link.name, link.note ?: "Search there with the same dates") { openUrl(context, link.url) }
    }
}

@Composable
fun LoadingCard(text: String) {
    Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(20.dp)).background(Theme.surface).padding(20.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
        CircularProgressIndicator(Modifier.size(20.dp), color = Theme.accent, strokeWidth = 2.dp)
        Text(text, style = Theme.body.copy(color = Theme.inkSoft))
    }
}

@Composable
fun ErrorCard(text: String, retry: () -> Unit) {
    Column(Modifier.surfaceCard(padding = 20.dp, radius = 20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(text, style = Theme.body.copy(color = Theme.inkSoft))
        SecondaryButton("Try again", onClick = retry)
    }
}

// ---- stays -----------------------------------------------------------------------------------------------------

@Composable
fun StayList(model: AppModel, trip: Trip) {
    val book = model.book
    val scope = rememberCoroutineScope()
    val r = book.stays
    val error = book.error
    when {
        r != null -> {
            Row(Modifier.padding(horizontal = 4.dp), verticalAlignment = Alignment.CenterVertically) {
                Text("${r.shown} of ${r.total} places" + priceKind(r.source), style = Theme.subheadline.copy(color = Theme.muted),
                    modifier = Modifier.weight(1f))
                Row(Modifier.clip(RoundedCornerShape(10.dp)).background(Theme.surface).padding(2.dp)) {
                    for ((title, map) in listOf("List" to false, "Map" to true)) {
                        Box(Modifier.heightIn(min = 36.dp).clip(RoundedCornerShape(8.dp))
                            .background(if (book.stayMap == map) Theme.surfaceHigh else Color.Transparent)
                            .clickable(role = Role.Tab) { book.stayMap = map }.semantics { selected = book.stayMap == map }
                            .padding(horizontal = 12.dp), contentAlignment = Alignment.Center) {
                            Text(title, style = Theme.footnote.copy(color = Theme.ink))
                        }
                    }
                }
            }
            r.note?.let { SourceNote(it) }
            if (book.stayMap) {
                val placed = r.results.filter { it.point != null }
                val pins = listOf(MapPin(AppConfig.START, r.centre, dot = true)) +
                    placed.map { MapPin(it.point!!, it.name, price = Money.whole(it.priceNight), highlight = !it.tags.isNullOrEmpty()) }
                OsmMap(pins, Modifier.fillMaxWidth().height(300.dp).clip(RoundedCornerShape(20.dp))
                    .semantics { contentDescription = "Map of ${r.results.size} places to stay" }) { i ->
                    if (i > 0) model.bookPath += BookDest.StayDetail(placed[i - 1])
                }
            }
            for (s in r.results) StayCard(s, r.centre) { model.bookPath += BookDest.StayDetail(s) }
            if (r.results.isEmpty() && r.total > 0) {
                NoMatch("Nothing fits all of that.", "Try a higher price or fewer filters.") { book.stayFilters = book.stayFilters.cleared() }
            }
            if (r.links.isNotEmpty()) {
                SectionLabel("Also search", Modifier.padding(top = 8.dp))
                LinksOut(r.links)
            }
        }
        error != null -> ErrorCard(error) { scope.launch { model.search() } }
        else -> LoadingCard("Checking hundreds of places to stay in ${trip.city}. This can take about 15 seconds…")
    }
}

/** A stable colour per place (not random per launch). */
private fun stayFeel(stay: StayResult): String {
    val feels = listOf("Awe", "Calm", "Lively", "Curious", "Browsing", "Active")
    return feels[stay.id.sumOf { it.code } % feels.size]
}

/** A stay's picture: the provider's photo when there is one, else a field of colour. */
@Composable
fun StayImage(stay: StayResult, modifier: Modifier = Modifier) {
    val photo = stay.photo
    if (photo != null) {
        SubcomposeAsyncImage(photo, contentDescription = "Photo of ${stay.name}", contentScale = ContentScale.Crop, modifier = modifier,
            loading = { Box(Modifier.fillMaxSize().background(fieldBrush(stayFeel(stay)))) },
            error = { Box(Modifier.fillMaxSize().background(fieldBrush(stayFeel(stay)))) })
    } else {
        Box(modifier.background(fieldBrush(stayFeel(stay))))
    }
}

/** The first part of the address ("Covent Garden"). */
fun stayArea(stay: StayResult): String = stay.address.split(",").firstOrNull()?.trim() ?: stay.address

/** "1 Strand · 0.3 km from Charing Cross" */
fun stayWhere(stay: StayResult, centre: String): String = listOfNotNull(stayArea(stay).ifEmpty { null },
    stay.distanceKm?.let { String.format(Locale.UK, "%.1f km from %s", it, centre) }).joinToString(" · ")

fun stayPerks(stay: StayResult): String {
    val parts = listOfNotNull(if (stay.refundable == true) "Free cancellation" else null, if (stay.breakfast) "Breakfast included" else null)
    return if (parts.isEmpty()) (if (stay.refundable == false) "Can't be refunded" else "Check cancellation terms") else parts.joinToString(" · ")
}

@Composable
fun StayCard(stay: StayResult, centre: String, onClick: () -> Unit) {
    Column(Modifier.fillMaxWidth().pressable(onClick = onClick).clip(RoundedCornerShape(20.dp)).background(Theme.surface)) {
        Box(Modifier.fillMaxWidth().height(120.dp)) {
            StayImage(stay, Modifier.fillMaxSize())
            val tags = stay.tags
            if (!tags.isNullOrEmpty()) TagPill(tags.joinToString(" · "), Theme.accent, Modifier.align(Alignment.TopStart))
            TagPill(stay.kind.capitalizedFirst, Theme.ink, Modifier.align(Alignment.TopEnd))
        }
        Column(Modifier.padding(horizontal = 16.dp, vertical = 14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Text(stay.name, style = Theme.serif(20.sp), modifier = Modifier.weight(1f))
                stay.rating?.let {
                    Text(String.format(Locale.UK, "%.1f", it), style = Theme.subheadline.copy(fontWeight = FontWeight.SemiBold),
                        modifier = Modifier.clip(RoundedCornerShape(8.dp)).background(Theme.surfaceHigh).padding(horizontal = 8.dp, vertical = 3.dp))
                }
            }
            Text(stayWhere(stay, centre), style = Theme.subheadline.copy(color = Theme.inkSoft))
            Text(stayPerks(stay), style = Theme.footnote)
            Hairline()
            Row(Modifier.padding(top = 4.dp), verticalAlignment = Alignment.Bottom) {
                Text(stay.room, style = Theme.footnote, maxLines = 1, modifier = Modifier.weight(1f).padding(end = 8.dp))
                Column(horizontalAlignment = Alignment.End) {
                    Text(Money.whole(stay.priceNight), style = Theme.serif(24.sp))
                    Text("a night · ${Money.whole(stay.priceTotal)} total", style = Theme.caption)
                }
            }
        }
    }
}

@Composable
private fun TagPill(text: String, color: Color, modifier: Modifier) {
    Text(text, style = Theme.caption.copy(color = color), modifier = modifier.padding(12.dp).clip(RoundedCornerShape(10.dp))
        .background(Theme.background.copy(alpha = 0.75f)).padding(horizontal = 10.dp, vertical = 4.dp))
}

@Composable
fun StayDetailView(model: AppModel, stay: StayResult, onBack: () -> Unit) {
    val trip = model.currentTrip
    val results = model.book.stays
    fun open(link: TripLink) {
        val t = trip ?: return
        val choice = TripChoice("stay", stay.name, link.name, stay.priceTotal, false, point = stay.point, sample = stay.sample)
        model.openHandoff(Handoff(link.name, link.url, t.lengthLabel, stay.priceTotal, results?.searchedAt, choice))
    }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState())) {
        Box(Modifier.fillMaxWidth().height(300.dp)) {
            StayImage(stay, Modifier.fillMaxSize())
            Column(Modifier.align(Alignment.BottomStart).fillMaxWidth()
                .background(Brush.verticalGradient(listOf(Color.Transparent, Theme.background)))
                .padding(horizontal = 24.dp, vertical = 22.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(listOf(stay.kind.capitalizedFirst, stayArea(stay)).filter { it.isNotEmpty() }.joinToString(" · "),
                    style = Theme.subheadline.copy(color = Theme.amberDeep))
                Text(stay.name, style = Theme.serif(30.sp))
            }
            Box(Modifier.padding(start = 20.dp, top = 12.dp).size(44.dp).clip(CircleShape).background(Theme.background.copy(alpha = 0.6f))
                .clickable(role = Role.Button, onClick = onBack).semantics { contentDescription = "Back to stays" },
                contentAlignment = Alignment.Center) {
                Icon(Icons.AutoMirrored.Filled.KeyboardArrowLeft, null, tint = Theme.ink)
            }
        }
        Column(Modifier.padding(horizontal = 24.dp).padding(top = 10.dp, bottom = 40.dp), verticalArrangement = Arrangement.spacedBy(20.dp)) {
            Row(Modifier.height(IntrinsicSize.Min), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                // 19 Oct review: a sample's rating says it's made up, with no made-up review count
                Fact(stay.rating?.let { String.format(Locale.UK, "%.1f / 10", it) } ?: "–",
                    stay.reviews?.let { "$it guest reviews" } ?: if (stay.sample) "Made-up rating, for testing" else "Guest rating",
                    Modifier.weight(1f))
                Fact(stay.distanceKm?.let { String.format(Locale.UK, "%.1f km", it) } ?: "–",
                    "from ${results?.centre ?: "the centre"}, in central London", Modifier.weight(1f))
            }
            val why = listOfNotNull("${stay.room}. ${stay.board}.",
                if (stay.refundable == true) "Free cancellation with this rate." else null,
                if (stay.refundable == false) "This rate can't be refunded." else null).joinToString(" ")
            Text(why, style = Theme.body.copy(color = Theme.inkSoft))
            FoundPrice(stay.priceTotal, "${Money.whole(stay.priceNight)} a night · ${stay.nights} night${if (stay.nights == 1) "" else "s"}",
                results?.source ?: "sample", results?.searchedAt)
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    SectionLabel("Where to book", Modifier.weight(1f))
                    Text(trip?.lengthLabel ?: "", style = Theme.footnote)
                }
                // 19 Oct review: said next to the links, before anyone taps one
                Text("ODYS earns nothing from these links while we test. You pay the site you book with, and each sets its own price, so check what's included (breakfast, cancellation) before you pay.",
                    style = Theme.footnote.copy(color = Theme.inkSoft))
                for (link in stay.links) {
                    val note = when (link.name) {
                        "Booking.com" -> "This place, with your dates and guests"
                        "The place's own website" -> "Often the same price, sometimes with breakfast or a better room"
                        else -> "Your dates and guests"
                    }
                    ProviderRow(link.name, note, if (link.name == "The place's own website") "Direct" else null) { open(link) }
                }
            }
        }
    }
}

@Composable
private fun Fact(big: String, small: String, modifier: Modifier) {
    Column(modifier.fillMaxHeight().clip(RoundedCornerShape(16.dp)).background(Theme.surface).padding(horizontal = 16.dp, vertical = 14.dp),
        verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(big, style = Theme.serif(24.sp))
        Text(small, style = Theme.footnote)
    }
}

// ---- the hand-off: going to a provider, and back -------------------------------------------------------------

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HandoffSheet(model: AppModel, h: Handoff) {
    val context = LocalContext.current
    val state = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    fun close() {
        model.book.handoff = null
        model.files.delete("handoff.json")
    }
    fun answer(booked: Boolean) {
        model.currentTrip?.id?.let { model.keep(h.choice.copy(booked = booked), it) }
        close()
    }
    ModalBottomSheet(::close, sheetState = state, containerColor = Theme.surface, contentColor = Theme.ink) {
        Column(Modifier.fillMaxWidth().padding(horizontal = 24.dp).padding(top = 10.dp, bottom = 20.dp).navigationBarsPadding(),
            verticalArrangement = Arrangement.spacedBy(14.dp)) {
            if (h.back) {
                SectionLabel("Welcome back")
                Text("Did you book it?", style = Theme.serif(28.sp))
                PrimaryButton("Yes, add it to my trip") { answer(true) }
                SecondaryButton("Not yet, keep it saved") { answer(false) }
            } else {
                SectionLabel("You're going to")
                Text(h.provider, style = Theme.serif(30.sp))
                Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(16.dp)).background(Theme.background).padding(horizontal = 16.dp, vertical = 14.dp),
                    verticalAlignment = Alignment.CenterVertically) {
                    Text(h.what, style = Theme.subheadline.copy(color = Theme.inkSoft), modifier = Modifier.weight(1f))
                    Text(h.price?.let { Money.whole(it) } ?: "See their price", style = Theme.headline)
                }
                val ago = minutesAgo(h.searchedAt)
                val checked = ago?.let { if (it < 1) "Price found just now" else "Price found $it minute${if (it == 1L) "" else "s"} ago" }
                    ?: "The price is on their site"
                // m190 (design review): said for what's being booked; Skyscanner and Google Flights pass you on to sell it
                val how = if (h.choice.kind == "flight") "${h.provider} shows the fare, then sends you to the airline or a travel agent to book and pay."
                          else "You book and pay on their site, not in ODYS."
                Text("$checked, so it can change there. $how ODYS earns nothing from this link while we test.",
                    style = Theme.subheadline.copy(color = Theme.muted))
                PrimaryButton("Continue to ${h.provider} ↗") {
                    openUrl(context, h.url)
                    model.handoffGone()
                }
                QuietButton("Not yet", Modifier.fillMaxWidth()) { close() }
            }
        }
    }
}

// ---- filters ----------------------------------------------------------------------------------------------------

/** The sheet's frame: Clear all · Filters · Done, the filters, and "Show 6 flights" with the live count. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FilterSheetFrame(model: AppModel, showLabel: String, clear: () -> Unit, content: @Composable ColumnScope.() -> Unit) {
    val state = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    val done = { model.book.showFilters = false }
    ModalBottomSheet(done, sheetState = state, containerColor = Theme.surface, contentColor = Theme.ink) {
        Column(Modifier.fillMaxWidth().navigationBarsPadding()) {
            Row(Modifier.fillMaxWidth().padding(horizontal = 20.dp), verticalAlignment = Alignment.CenterVertically) {
                QuietButton("Clear all", color = Theme.inkSoft, onClick = clear)
                Text("Filters", style = Theme.headline, textAlign = TextAlign.Center, modifier = Modifier.weight(1f))
                CloseLink("Close", done)   // 19 Oct review: Android's ✕; the button below shows the results
            }
            Column(Modifier.weight(1f, fill = false).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp)
                .padding(top = 4.dp, bottom = 16.dp), verticalArrangement = Arrangement.spacedBy(22.dp), content = content)
            Hairline()
            Box(Modifier.padding(horizontal = 20.dp, vertical = 12.dp)) { PrimaryButton(showLabel, onClick = done) }
        }
    }
}

@Composable
fun FilterTitle(text: String, value: String? = null) {
    Row {
        Text(text, style = Theme.subheadline.copy(fontWeight = FontWeight.SemiBold), modifier = Modifier.weight(1f))
        if (value != null) Text(value, style = Theme.subheadline.copy(color = Theme.accent))
    }
}

/** Empty means every number of stops; a tap on one of all three keeps the other two. */
fun toggleStop(stops: List<Int>, k: Int): List<Int> {
    val s = (if (stops.isEmpty()) listOf(0, 1, 2) else stops).toMutableList()
    if (k in s) {
        if (s.size > 1) s.remove(k)
    } else {
        s += k
    }
    s.sort()
    return if (s == listOf(0, 1, 2)) emptyList() else s
}

fun toggled(k: String, list: List<String>) = if (k in list) list - k else list + k

@Composable
fun FilterSlider(value: Double, lo: Double, hi: Double, step: Double, onChange: (Double) -> Unit) {
    var v by remember(value) { mutableStateOf(value.toFloat()) }
    Slider(v, { v = it }, valueRange = lo.toFloat()..hi.toFloat(),
        steps = (((hi - lo) / step).toInt() - 1).coerceAtLeast(0),
        onValueChangeFinished = { onChange(v.toDouble()) },
        colors = SliderDefaults.colors(thumbColor = Theme.accent, activeTrackColor = Theme.accent, inactiveTrackColor = Theme.surfaceHigh,
            activeTickColor = Color.Transparent, inactiveTickColor = Color.Transparent))
}

@Composable
fun FlightFilterSheet(model: AppModel) {
    val book = model.book
    val r = book.flights
    val f = book.flightFilters
    val label = if (r == null) "Show flights" else if (r.shown == 0) "No flights match" else "Show ${r.shown} flight${if (r.shown == 1) "" else "s"}"
    FilterSheetFrame(model, label, { book.flightFilters = f.cleared() }) {
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            FilterTitle("Stops")
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for ((k, l) in listOf(0 to "Direct", 1 to "1 stop", 2 to "2+ stops")) {
                    val from = (r?.facets?.stops ?: emptyList()).filter { minOf(it.stops, 2) == k }.minOfOrNull { it.minPrice }
                    OptionTile(l, from?.let { "from ${Money.whole(it)}" } ?: "none", f.stops.isEmpty() || k in f.stops, Modifier.weight(1f)) {
                        book.flightFilters = f.copy(stops = toggleStop(f.stops, k))
                    }
                }
            }
        }
        val times = listOf(Triple("night", "Night", "00:00–06:00"), Triple("morning", "Morning", "06:00–12:00"),
            Triple("afternoon", "Afternoon", "12:00–18:00"), Triple("evening", "Evening", "18:00–24:00"))
        @Composable
        fun TimeGrid(on: List<String>, toggle: (String) -> Unit) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                for (row in times.chunked(2)) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        for ((k, l, sub) in row) OptionTile(l, sub, k in on, Modifier.weight(1f)) { toggle(k) }
                    }
                }
            }
        }
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            FilterTitle("Leaving ${model.currentTrip?.origin?.city ?: ""}")
            TimeGrid(f.outTimes) { book.flightFilters = f.copy(outTimes = toggled(it, f.outTimes)) }
        }
        if ((model.currentTrip?.nights ?: 0) > 0) {   // 9 Oct (Abram): the flight home has its own times
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                FilterTitle("Flying home from ${model.currentTrip?.city ?: "London"}")
                TimeGrid(f.inTimes) { book.flightFilters = f.copy(inTimes = toggled(it, f.inTimes)) }
            }
        }
        val legs = r?.facets?.legMinutes
        if (legs != null && legs.size == 2 && legs[0] < legs[1]) {
            val hi = legs[1].toDouble()
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterTitle("Longest journey", f.maxLegMin?.let { "Up to ${Dates.duration(it)}" } ?: "No limit")
                FilterSlider((f.maxLegMin ?: legs[1]).toDouble(), legs[0].toDouble(), hi, 30.0) { v ->
                    book.flightFilters = f.copy(maxLegMin = if (v >= hi) null else v.toInt())
                }
            }
        }
        val prices = r?.facets?.price
        if (prices != null && prices.size == 2 && prices[0] < prices[1]) {
            val lo = kotlin.math.floor(prices[0])
            val hi = kotlin.math.ceil(prices[1])
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterTitle("Maximum price", f.maxPrice?.let { Money.whole(it) } ?: "No limit")
                FilterSlider(f.maxPrice ?: hi, lo, hi, 10.0) { v -> book.flightFilters = f.copy(maxPrice = if (v >= hi) null else v) }
            }
        }
        FilterSwitch("Checked bag included", "At least one bag in the hold, in the fare", f.checkedBag) {
            book.flightFilters = f.copy(checkedBag = it)
        }
        val airlines = r?.facets?.airlines ?: emptyList()
        if (airlines.isNotEmpty()) {
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Box(Modifier.padding(bottom = 6.dp)) { FilterTitle("Airlines") }
                for (a in airlines) {
                    val on = a.name in f.airlines
                    Row(Modifier.fillMaxWidth().heightIn(min = 44.dp).clickable(role = Role.Checkbox) {
                        book.flightFilters = f.copy(airlines = if (on) f.airlines - a.name else f.airlines + a.name)
                    }.semantics { selected = on }, verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        TickBox(on)
                        Text(a.name, style = Theme.subheadline, modifier = Modifier.weight(1f))
                        Text(Money.whole(a.minPrice), style = Theme.footnote)
                    }
                }
            }
        }
    }
}

@Composable
fun FilterSwitch(label: String, sub: String, on: Boolean, onChange: (Boolean) -> Unit) {
    Row(Modifier.fillMaxWidth().clickable(role = Role.Switch) { onChange(!on) }, verticalAlignment = Alignment.CenterVertically) {
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(label, style = Theme.subheadline.copy(fontWeight = FontWeight.SemiBold))
            Text(sub, style = Theme.footnote)
        }
        androidx.compose.material3.Switch(on, onChange, colors = odysSwitchColors())   // 19 Oct: one look for every switch
    }
}

@Composable
fun StayFilterSheet(model: AppModel) {
    val book = model.book
    val r = book.stays
    val f = book.stayFilters
    val label = if (r == null) "Show places" else if (r.shown == 0) "Nothing matches" else "Show ${r.shown} place${if (r.shown == 1) "" else "s"}"
    FilterSheetFrame(model, label, { book.stayFilters = f.cleared() }) {
        val prices = r?.facets?.priceNight
        if (prices != null && prices.size == 2 && prices[0] < prices[1]) {
            val lo = kotlin.math.floor(prices[0])
            val hi = kotlin.math.ceil(prices[1])
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterTitle("Maximum per night", f.maxNight?.let { Money.whole(it) } ?: "No limit")
                FilterSlider(f.maxNight ?: hi, lo, hi, 5.0) { v -> book.stayFilters = f.copy(maxNight = if (v >= hi) null else v) }
            }
        }
        val kinds = r?.facets?.kinds ?: emptyList()
        if (kinds.isNotEmpty()) {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                FilterTitle("Type of place")
                for (row in kinds.chunked(2)) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        for (k in row) {
                            val on = k.kind in f.kinds
                            OptionTile(k.kind.capitalizedFirst, "${k.count} place${if (k.count == 1) "" else "s"}", on, Modifier.weight(1f)) {
                                book.stayFilters = f.copy(kinds = if (on) f.kinds - k.kind else f.kinds + k.kind)
                            }
                        }
                        if (row.size == 1) Spacer(Modifier.weight(1f))
                    }
                }
            }
        }
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            FilterTitle("Guest rating")
            Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)).background(Theme.background).padding(3.dp)) {
                for ((v, l) in listOf<Pair<Double?, String>>(null to "Any", 7.0 to "7+", 8.0 to "8+", 9.0 to "9+")) {
                    val on = f.minRating == v
                    Box(Modifier.weight(1f).heightIn(min = 40.dp).clip(RoundedCornerShape(9.dp))
                        .background(if (on) Theme.surfaceHigh else Color.Transparent)
                        .clickable(role = Role.RadioButton) { book.stayFilters = f.copy(minRating = v) }.semantics { selected = on },
                        contentAlignment = Alignment.Center) {
                        Text(l, style = Theme.subheadline)
                    }
                }
            }
        }
        FilterSwitch("Free cancellation", "With the rate found here", f.refundable) { book.stayFilters = f.copy(refundable = it) }
        FilterSwitch("Breakfast", "Included in the rate", f.breakfast) { book.stayFilters = f.copy(breakfast = it) }
    }
}
