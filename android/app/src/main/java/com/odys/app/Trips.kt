package com.odys.app

import android.content.Intent
import android.net.Uri
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Flight
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowLeft
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Bed
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.FlightLand
import androidx.compose.material.icons.filled.FlightTakeoff
import androidx.compose.material.icons.filled.LocalMall
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.Tram
import androidx.compose.material.icons.filled.UnfoldMore
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveableStateHolder
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.temporal.ChronoUnit

// D120: the ODYS Trips design: three tabs, "Plan a trip" in five questions (D122 added "Your days"), the trip as a
// checklist (getting there, where you'll stay, your days) and a running total (app/Sources/TripViews.swift).

// ---- the tabs -------------------------------------------------------------------------------------------------

/** Home after onboarding. Before the first plan, people in the UK get the survey and the blind pair (Build 2) first. */
@Composable
fun MainTabs(model: AppModel) {
    if (model.needsFirstRun) {
        FirstPlanFlow(model)
        return
    }
    var showSafety by remember { mutableStateOf(false) }
    var showSettings by remember { mutableStateOf(false) }
    val onHelp = { showSafety = true }
    val onData = { showSettings = true }
    Column(Modifier.screen()) {
        Box(Modifier.weight(1f)) {
            when (model.tab) {
                MainTab.Trip -> TripTab(model, onHelp, onData)
                MainTab.Book -> Box(Modifier.statusBarsPadding()) { BookView(model, onHelp) }
                MainTab.You -> Box(Modifier.statusBarsPadding()) { YouView(model, onHelp, onData) }
            }
        }
        TabBar(model)
    }
    if (model.showCreate) TripCreateFlow(model)
    if (model.showPair) FullSheet(model, { model.showPair = false }) { PairFlow(model) }
    if (model.showNow) NowView(model)
    if (showSafety) SafetyView(model) { showSafety = false }
    if (showSettings) SettingsView(model) { showSettings = false }
    model.book.handoff?.let { HandoffSheet(model, it) }
}

/** The design's tab bar: an arch for Trip, a paper plane for Book, a person for You. Tapping the open tab goes to its top. */
@Composable
fun TabBar(model: AppModel) {
    Column(Modifier.fillMaxWidth().background(Theme.background).navigationBarsPadding()) {
        Box(Modifier.fillMaxWidth().height(1.dp).background(Theme.hairline))
        Row(Modifier.fillMaxWidth().height(58.dp)) {
            for ((tab, label) in listOf(MainTab.Trip to "Trip", MainTab.Book to "Book", MainTab.You to "You")) {
                val on = model.tab == tab
                val color = if (on) Theme.accent else Theme.tabOff
                Column(
                    Modifier.weight(1f).fillMaxHeight().clickable(role = Role.Tab) {
                        if (on && tab == MainTab.Trip) model.tripPath.clear()
                        if (on && tab == MainTab.Book) model.bookPath.clear()
                        model.tab = tab
                    }.semantics { selected = on },
                    horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center,
                ) {
                    TabIcon(tab, color)
                    Text(label, style = Theme.caption.copy(color = color, fontSize = 11.sp))
                }
            }
        }
    }
}

@Composable
fun TabIcon(tab: MainTab, color: Color) {
    Canvas(Modifier.size(24.dp, 22.dp)) {
        val s = density
        val p = Path()
        when (tab) {
            MainTab.Trip -> {
                p.moveTo(12 * s, 2 * s)
                p.cubicTo(8 * s, 2 * s, 5 * s, 5 * s, 5 * s, 9 * s)
                p.lineTo(5 * s, 20 * s)
                p.lineTo(19 * s, 20 * s)
                p.lineTo(19 * s, 9 * s)
                p.cubicTo(19 * s, 5 * s, 16 * s, 2 * s, 12 * s, 2 * s)
                p.close()
            }
            MainTab.Book -> {
                p.moveTo(3 * s, 12 * s)
                p.lineTo(21 * s, 4 * s)
                p.lineTo(15 * s, 20 * s)
                p.lineTo(12 * s, 13 * s)
                p.close()
            }
            MainTab.You -> {
                p.addOval(androidx.compose.ui.geometry.Rect(8 * s, 3 * s, 16 * s, 11 * s))
                p.moveTo(4 * s, 21 * s)
                p.cubicTo(4 * s, 16 * s, 8 * s, 14 * s, 12 * s, 14 * s)
                p.cubicTo(16 * s, 14 * s, 20 * s, 16 * s, 20 * s, 21 * s)
            }
        }
        drawPath(p, color, style = Stroke(1.8f * s, cap = StrokeCap.Round, join = StrokeJoin.Round))
    }
}

/** The Trip tab: home, then your day, a trip, a trip's day or a stop, one on top of another. Back goes down a level. */
@Composable
fun TripTab(model: AppModel, onHelp: () -> Unit, onData: () -> Unit) {
    val holder = rememberSaveableStateHolder()
    val top = model.tripPath.lastOrNull()
    val pop: () -> Unit = { if (model.tripPath.isNotEmpty()) model.tripPath.removeAt(model.tripPath.lastIndex) }
    BackHandler(enabled = top != null, onBack = pop)
    holder.SaveableStateProvider("${model.tripPath.size}:${top.hashCode()}") {
        when (top) {
            null -> Box(Modifier.statusBarsPadding()) { TripHome(model, onHelp, onData) }
            Dest.Day -> Box(Modifier.statusBarsPadding()) { DayView(model, onHelp, onData, onBack = pop) }
            is Dest.TripOverview -> Box(Modifier.statusBarsPadding()) { TripOverview(model, top.tripId, onHelp, pop) }
            is Dest.TripDay -> Box(Modifier.statusBarsPadding()) { TripDayView(model, top.tripId, top.index, top.openChange, pop) }
            is Dest.StopCard -> StopView(model, top.stop, top.planId, pop)
            is Dest.Share -> {
                Box(Modifier.statusBarsPadding()) { TripHome(model, onHelp, onData) }
                SharePreview(model, top.stop, model.myRatings[top.stop.momentId] ?: 5, pop)
            }
        }
    }
}

// ---- Trip tab: home ---------------------------------------------------------------------------------------------

/** "Where to next?": one big action (Plan a trip), then your day and your trips underneath. */
@Composable
fun TripHome(model: AppModel, onHelp: () -> Unit, onData: () -> Unit) {
    var planningDay by remember { mutableStateOf(false) }
    @Suppress("UNUSED_VARIABLE") val tick = model.clock   // journey round 2: Today / Tomorrow follow the date
    ScrollPage(spacing = 22) {
        TopBar(Dates.greeting, model.unreadSafety, onHelp, onData)
        PageTitle("Where to next?", Modifier.settle(0), style = Theme.display)
        val today = model.todayInTrip()
        val tomorrow = if (today == null) model.tomorrowInTrip() else null
        if (today != null) {   // journey audit: during a trip, today comes first
            Box(Modifier.settle(1)) { TodayInTripCard(model, today.first, today.second, today.third) }
        } else if (tomorrow != null) {   // Abram's comment (8 Oct): then tomorrow, to look ahead
            Box(Modifier.settle(1)) { TomorrowInTripCard(model, tomorrow.first, tomorrow.second, tomorrow.third) }
        }
        val plan = model.plan
        @Composable
        fun yourDay(p: Plan, m: Modifier) = Column(m, verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("Your day", style = Theme.subheadline.copy(color = Theme.muted))
            DayRow(p) { model.tripPath += Dest.Day }
        }
        if (model.isVisitor) {
            Box(Modifier.settle(1)) { PlanTripCard { model.showCreate = true } }
            if (plan != null) yourDay(plan, Modifier.settle(2))
            else {   // journey round 2: with no day yet, "Plan a day" was out of reach
                SecondaryButton("Plan a day out instead", Modifier.settle(2), icon = Icons.Filled.WbSunny) { planningDay = true }
            }
        } else {
            // 20 Oct (round 2): people who live here mostly want a day out, so that leads; a trip is one tap below
            if (plan != null) yourDay(plan, Modifier.settle(1))
            Box(Modifier.settle(1)) {
                PlanTripCard("Plan a day out",
                    "A day in London around what you enjoy: your hours, where you start, and the places that fit you.") { planningDay = true }
            }
            SecondaryButton("Plan a trip instead", Modifier.settle(2), icon = Icons.Filled.Flight) { model.showCreate = true }
            if (!model.pairDone) Box(Modifier.settle(2)) { PairInviteRow { model.showPair = true } }
        }
        if (model.trips.isNotEmpty()) {
            Column(Modifier.settle(3), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("Your trips", style = Theme.subheadline.copy(color = Theme.muted))
                for (trip in model.trips) TripRow(trip) { model.tripPath += Dest.TripOverview(trip.id) }
            }
        }
    }
    if (planningDay) {
        FullSheet(model, { planningDay = false }) {
            Column(Modifier.fillMaxSize()) {
                SheetBar(onClose = { planningDay = false })
                PlanFormView(model, onDone = {
                    planningDay = false
                    model.tripPath += Dest.Day
                })
            }
        }
    }
}

/** Journey audit (7 Oct): "Today · Day 3 of your London trip", one tap to make it your day (and plan it first). */
@Composable
fun TodayInTripCard(model: AppModel, trip: Trip, index: Int, day: TripDayOut?) {
    val scope = rememberCoroutineScope()
    var confirm by remember { mutableStateOf(false) }
    fun start() = scope.launch {
        model.goToTripDay(trip.id, index)
        if (model.plan?.date == Dates.todayIso()) model.tripPath += Dest.Day
    }
    Column(Modifier.surfaceCard(padding = 20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Eyebrow("Today · Day ${index + 1} of ${trip.dayCount}")
        Text(day?.title ?: "Your ${trip.city} trip", style = Theme.serif(24.sp))
        day?.plan?.stops?.firstOrNull()?.let {
            Text("First: ${it.title}, around ${it.arrive}", style = Theme.subheadline.copy(color = Theme.inkSoft))
        }
        PrimaryButton(if (model.busy) "Planning…" else if (day == null) "Plan today" else if (day.plan == null) "See today" else "Start today",
            enabled = !model.busy) {
            // journey round 2: a travel or free day has nothing to start: its page shows the journeys
            if (day != null && day.plan == null) model.openTripDay(trip.id, index, "today")
            else if (model.testBPlanAtRisk) confirm = true else start()
        }
    }
    if (confirm) ReplaceTestBPlanDialog({ confirm = false }) { start() }
}

/** Abram's comment (8 Oct): "Tomorrow · Day 3 of 6": one tap to look at it, so the day can be planned around other plans. */
@Composable
fun TomorrowInTripCard(model: AppModel, trip: Trip, index: Int, day: TripDayOut?) {
    val scope = rememberCoroutineScope()
    Column(Modifier.surfaceCard(padding = 20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Eyebrow("Tomorrow · Day ${index + 1} of ${trip.dayCount}")
        Text(day?.title ?: "Your ${trip.city} trip", style = Theme.serif(24.sp))
        day?.plan?.stops?.firstOrNull()?.let {
            Text("First: ${it.title}, around ${it.arrive}", style = Theme.subheadline.copy(color = Theme.inkSoft))
        }
        Text("Made other plans? Change the day's hours, and I'll plan around them.", style = Theme.footnote)
        SecondaryButton(if (model.busy) "Planning…" else if (day == null) "Plan tomorrow" else "See tomorrow", enabled = !model.busy) {
            scope.launch {
                model.planTripDayIfNeeded(trip.id, index)
                model.openTripDay(trip.id, index, "home")
            }
        }
    }
}

/** The arch lit, with its light spilling out (the design's 30 × 36 mark on "Plan a trip"). */
@Composable
fun ArchMark() {
    Canvas(Modifier.size(30.dp, 36.dp)) {
        drawPath(Pool.logo.path(size), Theme.accent.copy(alpha = 0.35f))
        drawPath(Door.logoLight.path(size), Theme.accent)
    }
}

@Composable
fun PlanTripCard(
    title: String = "Plan a trip",
    text: String = "One day or two weeks. I'll find the flight, the stay and the moments, and you book with whichever site you trust.",
    onClick: () -> Unit,
) {
    Column(
        Modifier.fillMaxWidth().pressable(haptic = true, onClick = onClick).clip(RoundedCornerShape(24.dp))
            .background(Brush.radialGradient(listOf(Color(0xFF3B2E1E), Theme.surface), center = Offset(900f, 0f), radius = 900f))
            .background(Theme.surface.copy(alpha = 0f)).padding(22.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        ArchMark()
        Text(title, style = Theme.serif(26.sp))
        Text(text, style = Theme.body.copy(color = Theme.inkSoft))
        Box(Modifier.heightIn(min = 48.dp).clip(CircleShape).background(Theme.accent).padding(horizontal = 22.dp),
            contentAlignment = Alignment.Center) {
            Text("Start", style = Theme.headline.copy(color = Theme.onAccent))
        }
    }
}

/** Build 2: the comparison is still offered to someone who had a plan before the pair existed. */
@Composable
fun PairInviteRow(onClick: () -> Unit) {
    Row(Modifier.pressable(onClick = onClick).surfaceCard(padding = 18.dp), horizontalArrangement = Arrangement.spacedBy(14.dp)) {
        Box(Modifier.padding(top = 4.dp)) { ArchGlyph() }
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text("Two plans for a Saturday", style = Theme.title3)
            Text("Which would you rather do? About two minutes, and it helps the test most.",
                style = Theme.subheadline.copy(color = Theme.muted))
        }
    }
}

/** "Your day": the current plan, one tap from home. */
@Composable
fun DayRow(plan: Plan, onClick: () -> Unit) {
    Row(Modifier.fillMaxWidth().pressable(onClick = onClick).clip(RoundedCornerShape(20.dp)).background(Theme.surface).padding(12.dp),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
        Box(Modifier.size(56.dp).clip(RoundedCornerShape(14.dp))
            .background(fieldBrush(plan.stops.firstOrNull { it.rateable }?.feelWord)))
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(Dates.longDay(plan.date) ?: plan.title ?: "Your day", style = Theme.serif(20.sp))
            Text("${plan.stops.size} stops" + (plan.totals?.finish?.let { " · done by $it" } ?: ""),
                style = Theme.subheadline.copy(color = Theme.muted))
        }
        Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = Theme.muted)
    }
}

@Composable
fun TripRow(trip: Trip, onClick: () -> Unit) {
    Row(Modifier.fillMaxWidth().pressable(onClick = onClick).clip(RoundedCornerShape(20.dp)).background(Theme.surface).padding(12.dp),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
        Box(Modifier.size(56.dp).clip(RoundedCornerShape(14.dp)).background(Brush.radialGradient(
            listOf(Color(0xFFE7B77A), Color(0xFF9A6A3E), Color(0xFF2A1F17)), center = Offset(80f, 30f), radius = 150f)))
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(trip.city, style = Theme.serif(20.sp))
            Text("${trip.range} · ${trip.lengthLabel}", style = Theme.subheadline.copy(color = Theme.muted))
        }
        Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = Theme.muted)
    }
}

/** "To do", "Saved, not booked", "Booked", or "For other dates" (journey audit: the trip's dates changed). */
@Composable
fun ChoiceStatus(choice: TripChoice?, fits: Boolean = true) = when {
    choice == null -> StatusLabel("To do", Theme.surfaceHigh, Theme.inkSoft)
    !fits -> StatusLabel("For other dates", Color(0xFF3A1F1C), Color(0xFFF0A090))
    choice.booked -> StatusLabel("Booked", Color(0xFF1F3A2A), Color(0xFF9BE0B0))
    else -> StatusLabel("Saved, not booked", Color(0xFF3A2F1C), Theme.accent)
}

/**
 * D123: "Good to know" on a trip: entry rules for flights from abroad, getting around London, bags and signal. Entry rules
 * are general information and links to GOV.UK, the same for everyone flying in from abroad (decided by the departure
 * airport, never by nationality). It never says whether this person needs a visa: that would be immigration advice.
 */
@Composable
fun TripGoodToKnow(trip: Trip, basedAbroad: Boolean) {
    val fromAbroad = (trip.needFlight && (trip.origin?.country ?: "") != "GB") || basedAbroad
    Column(Modifier.padding(top = 8.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
        SectionLabel("Good to know")
        if (fromAbroad) {
            KnowItem("Before you fly",
                "Depending on nationality, most visitors to the UK need either a visa or an electronic travel authorisation (ETA, £20 for each traveller, babies included). Check what applies to you on GOV.UK before you book.",
                listOf("Check if you need a visa or an ETA" to "https://www.gov.uk/check-uk-visa", "About the ETA" to "https://www.gov.uk/eta"))
            KnowItem("Health and emergencies",
                "In an emergency, call 999 or 112. For urgent help that isn't life-threatening, call NHS 111. A&E is free for everyone; if you're admitted to hospital, that care can be charged, so GOV.UK advises visitors to have travel or health insurance. Visitors from the EU can use an EHIC.",
                listOf("NHS: using the NHS as a visitor" to "https://www.nhs.uk/nhs-services/visiting-or-moving-to-england/how-to-access-nhs-services-in-england-if-you-are-visiting-from-abroad/"))
        }
        KnowItem("Getting around London",
            "Contactless cards, phones and watches work on buses, the Tube, DLR, Overground, the Elizabeth line and most trains. Touch in and out with the same one, one per person: then a daily cap stops you paying more than a set amount (£8.90 in zones 1–2). The Heathrow Express and river buses aren't in the cap, and your bank may charge a fee on each tap with a card from abroad.",
            listOf("TfL: paying with contactless" to "https://tfl.gov.uk/fares/how-to-pay-and-where-to-buy-tickets-and-oyster/pay-as-you-go/contactless-and-mobile-pay-as-you-go"))
        if (trip.needStay) KnowItem("Bags", "Most places will hold your bags before check-in and after check-out: ask your stay.", emptyList())
        KnowItem("Without signal",
            "Your days and this trip stay on your phone, and ratings wait until you're back online. New plans, Book and directions need data.",
            emptyList())
    }
}

@Composable
private fun KnowItem(title: String, text: String, links: List<Pair<String, String>>) {
    val context = LocalContext.current
    Column(Modifier.surfaceCard(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(title, style = Theme.headline)
        Text(text, style = Theme.subheadline.copy(color = Theme.inkSoft))
        for ((label, url) in links) {
            Text("$label ↗", style = Theme.subheadline.copy(color = Theme.accent),
                modifier = Modifier.heightIn(min = 32.dp).clickable(role = Role.Button) { openUrl(context, url) })
        }
    }
}

// ---- Plan a trip: where, when, getting there, your days, how it should feel ------------------------------------

private const val TRIP_QUESTIONS = 5

/** Journey round 2: who's going and the airport you fly from change the searches, not the days. */
fun onlySearchChanged(old: Trip, new: Trip): Boolean {
    val a = old.copy(adults = 0, origin = null, originGuessed = false, days = emptyList())
    val b = new.copy(adults = 0, origin = null, originGuessed = false, days = emptyList())
    return a == b && (old.adults != new.adults || old.origin != new.origin)
}

@Composable
fun TripCreateFlow(model: AppModel) {
    // a trip already saved is being changed; a draft handed in (a new trip part-way, as in the screenshots) is not
    val editing = model.editingTrip?.let { model.findTrip(it.id) } != null
    var trip by remember { mutableStateOf(model.editingTrip ?: model.newTrip()) }
    var step by remember { mutableIntStateOf(model.editStep ?: if (editing) 1 else 0) }
    var showAirports by remember { mutableStateOf(false) }
    var confirmReplace by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    fun dismiss() {
        model.showCreate = false
        model.editingTrip = null
        model.editStep = null
    }
    val backTitle = if (step == 0 || (editing && step == 1)) "Cancel" else "‹ Back"
    LaunchedEffect(Unit) { if (!editing && trip.origin == null) trip = model.guessOrigin(trip) }

    fun next() {
        if (step < TRIP_QUESTIONS - 1) {
            step += 1
            return
        }
        scope.launch {
            val t = trip
            val old = if (editing) model.findTrip(t.id) else null
            if (old != null && onlySearchChanged(old, t)) {   // travellers or airport only: the days stay
                model.save(t)
                model.book.resultsFor = null
                dismiss()
                return@launch
            }
            if (model.makeTrip(t, keepFrom = old)) {
                if (editing) model.book.resultsFor = null
                dismiss()
                model.tab = MainTab.Trip
                model.tripPath.clear()
                model.tripPath += Dest.TripOverview(t.id)
            }
        }
    }

    FullSheet(model, ::dismiss) {
        BackTo(enabled = backTitle != "Cancel") { step -= 1 }
        PageWithBottom(spacing = 16, bottom = {
            val title = when {
                step < TRIP_QUESTIONS - 1 -> "Continue"
                model.busy -> "Planning your days…"
                editing -> "Plan the trip again"
                else -> "Make my trip"
            }
            PrimaryButton(title, enabled = !model.busy) {
                // journey round 2: a one-day trip becomes "your day", so the unrated Test B plan asks first
                if (step == TRIP_QUESTIONS - 1 && trip.nights == 0 && model.testBPlanAtRisk) confirmReplace = true else next()
            }
        }) {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.widthIn(min = 72.dp)) {   // 19 Oct review: Android's ✕ and arrow, not words
                    if (backTitle == "Cancel") CloseLink("Cancel") { dismiss() } else BackLink { step -= 1 }
                }
                Row(Modifier.weight(1f).semantics { contentDescription = "Question ${step + 1} of $TRIP_QUESTIONS" },
                    horizontalArrangement = Arrangement.spacedBy(6.dp, Alignment.CenterHorizontally)) {
                    for (i in 0 until TRIP_QUESTIONS) {
                        Box(Modifier.size(if (i == step) 22.dp else 6.dp, 6.dp).clip(CircleShape)
                            .background(if (i <= step) Theme.accent else Color(0xFF3A3E46)))
                    }
                }
                Spacer(Modifier.width(72.dp))
            }
            androidx.compose.runtime.key(step) {
                Column(Modifier.settle(0), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    when (step) {
                        0 -> WhereStep()
                        1 -> WhenStep(trip) { trip = it }
                        2 -> FromStep(trip, { trip = it }) { showAirports = true }
                        3 -> DaysStep(trip) { trip = it }
                        else -> FeelStep(trip) { trip = it }
                    }
                }
            }
        }
    }
    if (showAirports) {
        AirportPicker(model, { showAirports = false }) { place ->
            trip = trip.copy(origin = place, originGuessed = false, needFlight = true)
            showAirports = false
        }
    }
    if (confirmReplace) ReplaceTestBPlanDialog({ confirmReplace = false }) { next() }
}

@Composable
fun WhereStep() {
    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
        PageTitle("Where are you going?")
        Row(Modifier.fillMaxWidth().height(54.dp).clip(RoundedCornerShape(16.dp)).background(Theme.surface)
            .border(1.5.dp, Theme.accent, RoundedCornerShape(16.dp)).padding(horizontal = 16.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Text("London", style = Theme.body, modifier = Modifier.weight(1f))
            Text("United Kingdom", style = Theme.footnote)
        }
        Text("In this test", style = Theme.subheadline.copy(color = Theme.muted), modifier = Modifier.padding(top = 6.dp))
        // D120: London now, then UK cities, then Europe, then further (Abram, 6 Oct)
        CityLine("London", "Ready to test", true)
        CityLine("Edinburgh, Manchester and the UK", "Coming next", false)
        CityLine("Paris, Rome and Europe", "Coming later", false)
    }
}

@Composable
fun CityLine(name: String, note: String, ready: Boolean) {
    Column {
        Row(Modifier.fillMaxWidth().heightIn(min = 52.dp).padding(horizontal = 4.dp), verticalAlignment = Alignment.CenterVertically) {
            Text(name, style = Theme.body.copy(color = if (ready) Theme.ink else Color(0xFF7A746B)),
                modifier = Modifier.weight(1f).padding(end = 12.dp))
            Text(note, style = Theme.footnote)
        }
        Box(Modifier.fillMaxWidth().height(1.dp).background(Theme.hairline))
    }
}

/**
 * Screen 21 (Abram's comment, 8 Oct): "When are you going?" on a calendar. The first tap is the first day and a tap on
 * a later day is the last; one day on its own is a day out.
 */
@Composable
fun WhenStep(trip: Trip, onChange: (Trip) -> Unit) {
    var pickingEnd by remember { mutableStateOf(false) }
    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
        PageTitle("When are you going?")
        Text(if (pickingEnd) "Now tap your last day. Tap the same day again for a day out." else "Tap your first day, then your last day.",
            style = Theme.subheadline.copy(color = Theme.muted))
        TripCalendar(trip, pickingEnd, { pickingEnd = it }, onChange)
        val length = if (trip.nights == 0) {
            if (pickingEnd) "A day out, unless you tap a later day" else "A day out: no stay needed"
        } else {
            val days = "${trip.dayCount} days, ${trip.nights} night${if (trip.nights == 1) "" else "s"}"
            val first = trip.startDate.dayOfWeek.value   // Monday 1 … Sunday 7
            if (trip.nights <= 2 && (first == 5 || first == 6)) "A weekend: $days" else days
        }
        Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface)
            .padding(horizontal = 18.dp, vertical = 14.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(trip.rangeLong, style = Theme.serif(21.sp))
            Text(length, style = Theme.subheadline.copy(color = Theme.inkSoft))
        }
    }
}

/** A month at a time, Monday first: the first and last day in amber, the days between warm. */
@Composable
fun TripCalendar(trip: Trip, pickingEnd: Boolean, setPickingEnd: (Boolean) -> Unit, onChange: (Trip) -> Unit) {
    val maxNights = 30
    val band = Color(0xFF3A2F1C)
    val today = Dates.today()
    val lastStart = today.plusDays(329)
    var month by remember { mutableStateOf(maxOf(trip.startDate, today).withDayOfMonth(1)) }
    val canGoBack = month > today.withDayOfMonth(1)
    val canGoOn = month < lastStart.plusDays(maxNights.toLong()).withDayOfMonth(1)
    var drag by remember { mutableFloatStateOf(0f) }

    fun canTap(day: LocalDate): Boolean {
        if (day < today) return false
        if (pickingEnd && day >= trip.startDate) return ChronoUnit.DAYS.between(trip.startDate, day) <= maxNights
        return day <= lastStart
    }

    fun tap(day: LocalDate) {
        if (pickingEnd && day >= trip.startDate) {
            onChange(trip.copy(nights = minOf(ChronoUnit.DAYS.between(trip.startDate, day).toInt(), maxNights)))
            setPickingEnd(false)
        } else {
            onChange(trip.copy(start = day.toString(), nights = 0))
            setPickingEnd(true)
        }
    }

    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(20.dp)).background(Theme.surface).padding(horizontal = 10.dp, vertical = 12.dp)
            .pointerInput(month) {
                detectHorizontalDragGestures(onDragStart = { drag = 0f }, onDragEnd = {
                    if (drag < -120 && canGoOn) month = month.plusMonths(1) else if (drag > 120 && canGoBack) month = month.minusMonths(1)
                }) { _, dx -> drag += dx }
            },
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            RoundIcon(Icons.AutoMirrored.Filled.KeyboardArrowLeft, "Previous month", !canGoBack) { month = month.minusMonths(1) }
            Text(Dates.monthYear(month), style = Theme.serif(20.sp), textAlign = TextAlign.Center,
                modifier = Modifier.weight(1f).semantics { heading() })
            RoundIcon(Icons.AutoMirrored.Filled.KeyboardArrowRight, "Next month", !canGoOn) { month = month.plusMonths(1) }
        }
        Row {
            for (d in listOf("M", "T", "W", "T", "F", "S", "S")) {
                Text(d, style = Theme.caption, textAlign = TextAlign.Center, modifier = Modifier.weight(1f))
            }
        }
        val blanks = month.dayOfWeek.value - 1
        val cells: List<LocalDate?> = List(blanks) { null } + (0 until month.lengthOfMonth()).map { month.plusDays(it.toLong()) }
        for (week in cells.chunked(7)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                for (k in 0 until 7) {
                    val day = week.getOrNull(k)
                    Box(Modifier.weight(1f).height(44.dp), contentAlignment = Alignment.Center) {
                        if (day != null) {
                            val iso = day.toString()
                            val isStart = iso == trip.start
                            val isEnd = trip.nights > 0 && iso == trip.end
                            val inRange = trip.nights > 0 && iso > trip.start && iso < trip.end
                            val open = canTap(day)
                            Row(Modifier.fillMaxWidth().height(40.dp)) {   // the warm band from the first day to the last
                                Box(Modifier.weight(1f).fillMaxHeight().background(if (isEnd || inRange) band else Color.Transparent))
                                Box(Modifier.weight(1f).fillMaxHeight().background(if ((isStart && trip.nights > 0) || inRange) band else Color.Transparent))
                            }
                            Box(
                                Modifier.size(40.dp).clip(CircleShape)
                                    .background(if (isStart || isEnd) Theme.accent else Color.Transparent)
                                    .then(if (!isStart && !isEnd && day == today) Modifier.border(1.dp, Theme.outlineStrong, CircleShape) else Modifier)
                                    .clickable(enabled = open, role = Role.Button) { tap(day) }
                                    .semantics {
                                        contentDescription = Dates.dayName(day)
                                        stateDescription = if (isStart) "First day" else if (isEnd) "Last day" else if (inRange) "In your trip" else ""
                                    },
                                contentAlignment = Alignment.Center,
                            ) {
                                Text("${day.dayOfMonth}", style = Theme.body.copy(
                                    fontWeight = if (isStart || isEnd) FontWeight.SemiBold else FontWeight.Normal,
                                    color = if (isStart || isEnd) Theme.onAccent else if (open) Theme.ink else Theme.muted.copy(alpha = 0.45f)))
                            }
                        }
                    }
                }
            }
        }
    }
}

/** D122: by plane, train or car, or already in London. */
@Composable
fun FromStep(trip: Trip, onChange: (Trip) -> Unit, chooseAirport: () -> Unit) {
    val ways = listOf("flight" to "Flying", "train" to "By train", "car" to "By car", "here" to "Already in London")
    fun choose(key: String) {
        var t = trip.copy(needFlight = key == "flight")
        if (key != "flight") t = t.copy(travelBy = key)
        if (key == "train" && t.station == null) t = t.copy(station = "KGX")
        if (key == "train" || key == "car") t = t.copy(arriveAt = t.arriveAt ?: "11:00", leaveAt = t.leaveAt ?: "17:00")
        onChange(t)
    }
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        PageTitle("Getting there")
        for (pair in ways.chunked(2)) {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                for ((key, label) in pair) {
                    OptionTile(label, null, trip.arrivingBy == key, Modifier.weight(1f), offFill = Theme.surface,
                        offStroke = Color.Transparent) { choose(key) }
                }
            }
        }
        when (trip.arrivingBy) {
            "flight" -> Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface)
                    .clickable(role = Role.Button, onClick = chooseAirport).padding(horizontal = 18.dp, vertical = 16.dp),
                    verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text("Flying from", style = Theme.footnote)
                        Text(trip.origin?.label ?: "Choose an airport", style = Theme.body)
                    }
                    Text(if (trip.originGuessed) "From your answers" else "Change",
                        style = Theme.footnote.copy(color = if (trip.originGuessed) Theme.muted else Theme.accent))
                }
                // journey round 2: a flight booked elsewhere still shapes the first and last days
                SwitchRow("I already have a flight", null, trip.ownFlight == true) { on ->
                    onChange(if (on) trip.copy(ownFlight = true, flightAirport = trip.flightAirport ?: "LHR",
                        arriveAt = trip.arriveAt ?: "11:00", leaveAt = trip.leaveAt ?: "17:00") else trip.copy(ownFlight = false))
                }
                if (trip.ownFlight == true) {
                    Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface)) {
                        PickMenu("London airport", LondonAirports.name(trip.flightAirport) ?: "Heathrow", LondonAirports.all) {
                            onChange(trip.copy(flightAirport = it))
                        }
                        Hairline()
                        TimeMenu("It lands, on the first day", trip.arriveAt ?: "11:00", HalfHours.from(5, 23)) {
                            onChange(trip.copy(arriveAt = it))
                        }
                        if (trip.nights > 0) {
                            Hairline()
                            TimeMenu("Your flight home leaves, on the last day", trip.leaveAt ?: "17:00", HalfHours.from(6, 23)) {
                                onChange(trip.copy(leaveAt = it))
                            }
                        }
                    }
                }
                Text(if (trip.ownFlight == true || trip.flight != null)
                    "Your first day starts when your flight lands, and your last day ends in time for the flight home."
                else "Choose a flight in Book, or add the one you have, and the first and last days fit around it.",
                    style = Theme.footnote, modifier = Modifier.padding(horizontal = 4.dp))
            }
            "train" -> Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface)) {
                PickMenu("Arriving at", LondonStations.name(trip.station) ?: "Choose a station", LondonStations.all) {
                    onChange(trip.copy(station = it))
                }
                Hairline()
                TimeMenu("Your train arrives", trip.arriveAt ?: "11:00", HalfHours.from(5, 22)) { onChange(trip.copy(arriveAt = it)) }
                Hairline()
                TimeMenu(if (trip.nights == 0) "Your train home leaves" else "Your train home leaves, on the last day",
                    trip.leaveAt ?: "17:00", HalfHours.from(5, 23)) { onChange(trip.copy(leaveAt = it)) }
            }
            "car" -> Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface)) {
                TimeMenu("You arrive at your stay", trip.arriveAt ?: "11:00", HalfHours.from(5, 22)) { onChange(trip.copy(arriveAt = it)) }
                Hairline()
                TimeMenu(if (trip.nights == 0) "You set off home" else "You set off home, on the last day",
                    trip.leaveAt ?: "17:00", HalfHours.from(8, 23)) { onChange(trip.copy(leaveAt = it)) }
            }
        }
        Stepper("Who's going", "${trip.adults} ${if (trip.adults == 1) "adult" else "adults"}", trip.adults <= 1, trip.adults >= 6,
            "Fewer travellers", "More travellers",
            { onChange(trip.copy(adults = maxOf(1, trip.adults - 1))) }) { onChange(trip.copy(adults = minOf(6, trip.adults + 1))) }
    }
}

/** D122: "Your days": from what time to what time, how many places a day, and travelling light on day 1. */
@Composable
fun DaysStep(trip: Trip, onChange: (Trip) -> Unit) {
    fun mins(t: String) = Dates.minutes(t)
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        PageTitle("Your days")
        Text("Each day runs at these times, from where you're staying.", style = Theme.body.copy(color = Theme.muted))
        Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface)) {
            // changing one end keeps at least two hours between them
            TimeMenu("Out from", trip.dayFrom, HalfHours.from(6, 14)) { v ->
                onChange(if (mins(trip.dayTo) - mins(v) < 120) trip.copy(hoursFrom = v, hoursTo = Dates.hhmm(minOf(mins(v) + 240, 23 * 60)))
                else trip.copy(hoursFrom = v))
            }
            Hairline()
            TimeMenu("Back by", trip.dayTo, HalfHours.from(12, 23)) { v ->
                onChange(if (mins(v) - mins(trip.dayFrom) < 120) trip.copy(hoursTo = v, hoursFrom = Dates.hhmm(maxOf(mins(v) - 240, 6 * 60)))
                else trip.copy(hoursTo = v))
            }
        }
        val n = trip.placesPerDay
        Stepper("Places a day", "$n place${if (n == 1) "" else "s"}", n <= 1, n >= 6, "One place fewer", "One place more",
            { onChange(trip.copy(places = maxOf(1, n - 1))) }) { onChange(trip.copy(places = minOf(6, n + 1))) }
        Text("Plus lunch, when a day runs through midday. A short day holds fewer places.", style = Theme.footnote,
            modifier = Modifier.padding(horizontal = 4.dp))
        if (trip.arrivingBy == "flight" || trip.arrivingBy == "train") {
            SwitchRow("Travelling light on day 1", "No big bags: if you arrive before check-in, one place on the way, then your stay.",
                trip.travelLight) { onChange(trip.copy(light = it)) }
        }
    }
}

@Composable
fun FeelStep(trip: Trip, onChange: (Trip) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        PageTitle("How should the trip feel?")
        Text("Pick one or two. They shape every day of this trip.", style = Theme.body.copy(color = Theme.muted),
            modifier = Modifier.padding(bottom = 4.dp))
        for ((key, label, line) in TripFeelings.all) {
            OptionTile(label, line, key in trip.feelings, serif = true, offFill = Theme.surface, offStroke = Color.Transparent) {
                onChange(trip.copy(feelings = if (key in trip.feelings) trip.feelings - key else (trip.feelings + key).takeLast(2)))
            }
        }
    }
}

@Composable
fun Hairline() = Box(Modifier.fillMaxWidth().height(1.dp).background(Theme.hairline))

/** A label, a value and − / + (travellers, places a day). */
@Composable
fun Stepper(label: String, value: String, atMin: Boolean, atMax: Boolean, minusLabel: String, plusLabel: String,
            minus: () -> Unit, plus: () -> Unit) {
    Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface).padding(horizontal = 18.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically) {
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(label, style = Theme.footnote)
            Text(value, style = Theme.body)
        }
        RoundIcon(Icons.Filled.Remove, minusLabel, atMin, minus)
        RoundIcon(Icons.Filled.Add, plusLabel, atMax, plus)
    }
}

/** A setting with a switch, on the surface. */
@Composable
fun SwitchRow(label: String, sub: String?, on: Boolean, onChange: (Boolean) -> Unit) {
    Row(Modifier.fillMaxWidth().heightIn(min = 52.dp).clip(RoundedCornerShape(18.dp)).background(Theme.surface)
        .clickable(role = Role.Switch) { onChange(!on) }.padding(horizontal = 18.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically) {
        Column(Modifier.weight(1f).padding(end = 12.dp), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(label, style = Theme.body)
            if (sub != null) Text(sub, style = Theme.footnote)
        }
        Switch(on, onChange, colors = SwitchDefaults.colors(checkedTrackColor = Theme.amberDeep, checkedThumbColor = Theme.onAccent))
    }
}

/** D122: a time from a menu of half hours. */
@Composable
fun TimeMenu(label: String, time: String, options: List<String>, onPick: (String) -> Unit) =
    PickMenu(label, time, options.map { it to it }, onPick)

/** A row that opens a menu: its label, the value, and a small chevron. */
@Composable
fun PickMenu(label: String, value: String, options: List<Pair<String, String>>, onPick: (String) -> Unit) {
    var open by remember { mutableStateOf(false) }
    Box {
        Row(Modifier.fillMaxWidth().clickable(role = Role.DropdownList) { open = true }
            .padding(horizontal = 18.dp, vertical = 12.dp).semantics { contentDescription = "$label: $value" },
            verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(label, style = Theme.footnote)
                Text(value, style = Theme.body)
            }
            Icon(Icons.Filled.UnfoldMore, null, tint = Theme.accent, modifier = Modifier.size(18.dp))
        }
        DropdownMenu(open, { open = false }, Modifier.heightIn(max = 360.dp).background(Theme.surfaceHigh)) {
            for ((key, text) in options) {
                DropdownMenuItem(text = { Text(text, style = Theme.body.copy(color = if (text == value) Theme.accent else Theme.ink)) },
                    onClick = {
                        onPick(key)
                        open = false
                    })
            }
        }
    }
}

/** "Flying from": type a town, city or airport code. */
@Composable
fun AirportPicker(model: AppModel, onClose: () -> Unit, onPick: (TripPlace) -> Unit) {
    var query by remember { mutableStateOf("") }
    var found by remember { mutableStateOf<List<TripPlace>>(emptyList()) }
    var searching by remember { mutableStateOf(false) }
    var failed by remember { mutableStateOf(false) }
    LaunchedEffect(query) {
        delay(250)
        if (query.isBlank()) {
            found = emptyList()
            return@LaunchedEffect
        }
        searching = true
        failed = false
        try {
            found = model.client.places(query)
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            failed = true
            found = emptyList()
        }
        searching = false
    }
    FullSheet(model, onClose) {
        Column(Modifier.fillMaxSize().imePadding()) {
            SheetBar("Flying from", close = "Cancel", onClose = onClose)
            Column(Modifier.padding(horizontal = 24.dp, vertical = 12.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                LineField("A town, city or airport", query, onChange = { query = it })
                when {
                    searching && found.isEmpty() -> Row(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
                        CircularProgressIndicator(Modifier.size(16.dp), color = Theme.accent, strokeWidth = 2.dp)
                        Text("Searching… the first search can take up to a minute.", style = Theme.footnote)
                    }
                    failed -> Text("Couldn't reach the planner. Check your connection, then type again.", style = Theme.footnote)
                    query.isNotBlank() && found.isEmpty() -> Text("No airports found for that. Try a city name or a three-letter code.",
                        style = Theme.footnote)
                }
            }
            LazyColumn(Modifier.fillMaxSize().padding(horizontal = 24.dp)) {
                items(found, key = { it.code }) { place ->
                    Column {
                        Row(Modifier.fillMaxWidth().heightIn(min = 56.dp).clickable(role = Role.Button) { onPick(place) },
                            verticalAlignment = Alignment.CenterVertically) {
                            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                Text(place.city, style = Theme.body)
                                Text(place.name, style = Theme.footnote)
                            }
                            Text(place.code, style = Theme.subheadline.copy(color = Theme.accent, fontWeight = FontWeight.SemiBold))
                        }
                        Hairline()
                    }
                }
            }
        }
    }
}

// ---- the trip: getting there, where you'll stay, your days, the total --------------------------------------------

@Composable
fun TripOverview(model: AppModel, tripId: String, onHelp: () -> Unit, onBack: () -> Unit) {
    val scope = rememberCoroutineScope()
    var confirmDelete by remember { mutableStateOf(false) }
    var removing by remember { mutableStateOf<String?>(null) }
    val trip = model.findTrip(tripId)
    fun openBook(t: Trip, segment: String) {
        model.currentTripId = t.id
        model.book.segment = segment
        model.tab = MainTab.Book
    }
    ScrollPage(spacing = 18, bottom = 40) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            BackLink(onClick = onBack)
            Spacer(Modifier.weight(1f))
            HelpPill(model.unreadSafety, onHelp)
        }
        if (trip == null) {
            Text("This trip isn't on this phone any more.", style = Theme.body.copy(color = Theme.muted))
            return@ScrollPage
        }
        Eyebrow("${trip.range} · ${trip.lengthLabel}")
        PageTitle(trip.city, style = Theme.display)
        Text(trip.feelLine, style = Theme.subheadline.copy(color = Theme.inkSoft))
        val results = model.book.resultsFor == trip.id
        if (trip.needFlight) {
            val f = trip.flight
            val sub = when {
                f != null && !trip.fits(f) -> "Chosen for other dates: check it on ${f.provider}, or choose again"
                f != null -> "${f.provider} · ${Money.whole(f.price)}" + if (f.sample == true) " · a sample price, not a real fare" else ""
                trip.origin == null -> "Choose where you're flying from"
                results && model.book.flights?.facets?.price?.firstOrNull() != null ->
                    "From ${Money.whole(model.book.flights!!.facets.price!!.first())} · ${model.book.flights!!.total} options from ${trip.origin.city}"
                else -> "Search flights from ${trip.origin.city}"
            }
            TripStepCard("1 · Getting there", { ChoiceStatus(f, trip.fits(f)) }, f?.title ?: "Choose your flight", sub) {
                openBook(trip, "flights")
            }
            if (f != null) QuietButton("Remove this flight from the trip") { removing = "flight" }
        }
        if (trip.needStay) {
            val s = trip.stay
            val sub = when {
                s != null && !trip.fits(s) -> "Chosen for other dates: check it on ${s.provider}, or choose again"
                s != null -> "${s.provider} · ${Money.whole(s.price)} for ${trip.lengthLabel}" + if (s.sample == true) " · a sample price" else ""
                results && model.book.stays?.facets?.priceNight?.firstOrNull() != null ->
                    "From ${Money.whole(model.book.stays!!.facets.priceNight!!.first())} a night · ${model.book.stays!!.total} places"
                else -> "Hotels, flats and hostels, from where your days happen"
            }
            TripStepCard("${if (trip.needFlight) 2 else 1} · Where you'll stay", { ChoiceStatus(s, trip.fits(s)) },
                s?.title ?: "Choose where to stay", sub) { openBook(trip, "stays") }
            if (s != null) QuietButton("Remove this stay from the trip") { removing = "stay" }
        }
        Row(Modifier.padding(top = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            SectionLabel("${1 + (if (trip.needFlight) 1 else 0) + (if (trip.needStay) 1 else 0)} · Your days", Modifier.weight(1f))
            Text("${trip.dayCount} day${if (trip.dayCount == 1) "" else "s"}", style = Theme.subheadline.copy(color = Theme.muted))
        }
        Row(Modifier.fillMaxWidth().heightIn(min = 44.dp).clickable(role = Role.Button) {
            model.editingTrip = trip       // D122: straight to "Your days"
            model.editStep = 3
            model.showCreate = true
        }.semantics { contentDescription = "Your days: ${trip.daysLine}. Change" }, verticalAlignment = Alignment.CenterVertically) {
            Text(trip.daysLine, style = Theme.subheadline.copy(color = Theme.inkSoft), modifier = Modifier.weight(1f))
            Text("Change", style = Theme.footnote.copy(color = Theme.accent))
        }
        if (trip.daysStale) {
            SecondaryButton(if (model.busy) "Planning…" else "Plan the days again around your stay and journeys", enabled = !model.busy) {
                scope.launch { model.replanDays(trip.id) }
            }
        }
        Column {
            for (i in 0 until trip.dayCount) TripDayLine(model, trip, i)
        }
        TripTotal(trip, if (results) model.book.flights else null, if (results) model.book.stays else null)
        TripGoodToKnow(trip, model.isVisitor)
        QuietButton("Delete this trip") { confirmDelete = true }
    }
    if (confirmDelete) {
        ConfirmDialog("Delete this trip?", "It's removed from this phone. Anything you booked stays booked on the provider's site.",
            "Delete the trip", "Keep it", destructive = true, onConfirm = {
                model.deleteTrip(tripId)
                onBack()
            }, onDismiss = { confirmDelete = false })
    }
    removing?.let { kind ->
        ConfirmDialog("Remove this $kind from the trip?",
            "Anything you booked stays booked on the provider's site. The days will be planned again around the change.",
            "Remove it", "Keep it", destructive = true, onConfirm = { model.removeChoice(kind, tripId) },
            onDismiss = { removing = null })
    }
}

@Composable
fun TripStepCard(label: String, status: @Composable () -> Unit, title: String, sub: String, onClick: () -> Unit) {
    Column(Modifier.fillMaxWidth().pressable(onClick = onClick).clip(RoundedCornerShape(22.dp)).background(Theme.surface).padding(18.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            SectionLabel(label, Modifier.weight(1f))
            status()
        }
        Text(title, style = Theme.serif(22.sp))
        Text(sub, style = Theme.subheadline.copy(color = Theme.inkSoft))
    }
}

/** One day of the trip: its date, its line, and whether it's ready. */
@Composable
fun TripDayLine(model: AppModel, trip: Trip, index: Int) {
    val scope = rememberCoroutineScope()
    val day = trip.days.firstOrNull { it.index == index }
    val date = trip.startDate.plusDays(index.toLong())
    Column {
        Row(
            Modifier.fillMaxWidth().pressable(enabled = day != null || !model.busy) {
                if (day != null) model.tripPath += Dest.TripDay(trip.id, index) else scope.launch { model.planDay(trip.id, index) }
            }.padding(vertical = 14.dp),
            horizontalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Column(Modifier.width(46.dp).padding(top = 2.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text(Dates.weekdayShort(date), style = Theme.caption)
                Text("${date.dayOfMonth}", style = Theme.title2Sans.copy(fontSize = 20.sp))
            }
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(3.dp)) {
                Text(day?.title ?: "Planned as you go", style = Theme.body)
                val note = when {
                    day == null -> if (model.busy) "Planning…" else "Plan this day"
                    day.plan != null -> "Ready"
                    else -> "Nothing planned: a travel day"
                }
                Text(note, style = Theme.footnote.copy(color = if (day?.plan != null) Theme.accent else Theme.muted))
            }
        }
        Hairline()
    }
}

/** "Trip so far": what's chosen, what it starts from, and the days planned. Only numbers we have; never a guess. */
@Composable
fun TripTotal(trip: Trip, flights: FlightResults?, stays: StayResults?) {
    val rows = mutableListOf<Triple<String, String, Double?>>()
    if (trip.needFlight) {
        val f = trip.flight
        val low = flights?.facets?.price?.firstOrNull()
        rows += when {
            f != null && !trip.fits(f) -> Triple("Flight", "for other dates", null)
            f != null -> Triple("Flight", Money.whole(f.price), f.price)
            low != null -> Triple("Flight", "from ${Money.whole(low)}", low)
            else -> Triple("Flight", "not chosen yet", null)
        }
    }
    if (trip.needStay) {
        val s = trip.stay
        val low = stays?.facets?.priceNight?.firstOrNull()
        val label = "Stay · ${trip.lengthLabel}"
        rows += when {
            s != null && !trip.fits(s) -> Triple(label, "for other dates", null)
            s != null -> Triple(label, Money.whole(s.price), s.price)
            low != null -> Triple(label, "from ${Money.whole(low * trip.nights)}", low * trip.nights)
            else -> Triple(label, "not chosen yet", null)
        }
    }
    val days = trip.days.mapNotNull { it.plan?.totals?.costGbp }
    if (days.isNotEmpty()) {
        val total = days.sum() * trip.adults
        rows += Triple("Days out (${days.size} planned)", Money.whole(total), total)
    }
    val sum = rows.mapNotNull { it.third }.sum()
    Column(Modifier.fillMaxWidth().border(1.dp, Theme.outline, RoundedCornerShape(20.dp)).padding(18.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(verticalAlignment = Alignment.Bottom) {
            Text("Trip so far", style = Theme.subheadline.copy(color = Theme.muted), modifier = Modifier.weight(1f))
            Text(Money.whole(sum), style = Theme.serif(28.sp))
        }
        if (trip.flight?.sample == true || trip.stay?.sample == true || flights?.source == "sample" || stays?.source == "sample") {
            Text("Includes sample prices: the real ones show once live search is on.", style = Theme.footnote)
        }
        for ((label, value, _) in rows) {
            Row {
                Text(label, style = Theme.subheadline.copy(color = Theme.inkSoft), modifier = Modifier.weight(1f))
                Text(value, style = Theme.subheadline.copy(color = Theme.inkSoft))
            }
        }
    }
}

/** One day of a trip: its stops, and "Make this my day" for "Now", rating, swap and plan again. */
@Composable
fun TripDayView(model: AppModel, tripId: String, index: Int, openChange: Boolean, onBack: () -> Unit) {
    val scope = rememberCoroutineScope()
    var confirm by remember { mutableStateOf(false) }
    var showSafety by remember { mutableStateOf(false) }
    var changing by remember { mutableStateOf<TripDayOut?>(null) }
    val trip = model.findTrip(tripId)
    LaunchedEffect(openChange) { if (openChange) changing = trip?.days?.firstOrNull { it.index == index } }
    fun use(t: Trip, d: TripDayOut) {
        model.useDay(t, d)
        model.tripPath.clear()
        model.tripPath += Dest.Day
    }
    ScrollPage(spacing = 18, bottom = 40) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            BackLink(onClick = onBack)
            Spacer(Modifier.weight(1f))
            HelpPill(model.unreadSafety) { showSafety = true }   // m176: Help on every trip page
        }
        if (trip == null) return@ScrollPage
        val day = trip.days.firstOrNull { it.index == index }
        val date = trip.startDate.plusDays(index.toLong())
        Eyebrow("Day ${index + 1} · ${Dates.dayShort(date)}")
        val (title, sub) = headlineParts(day?.title ?: "Planned as you go")
        Text(title, style = Theme.serif(30.sp), modifier = Modifier.semantics { heading() })
        if (sub != null) Text(sub, style = Theme.serif(19.sp).copy(color = Theme.inkSoft))   // 20 Oct (round 2): as on the plan
        if (day != null) {   // D122: from the airport or station, and one place on the way
            day.journeys("arrive").forEach { JourneyCard(it) }
            day.before?.let { before ->
                SectionLabel("On the way · travelling light", Modifier.padding(top = 4.dp))
                for (stop in before.stops) TripDayStop(stop)
            }
            day.journeys("to_stay").forEach { JourneyCard(it) }
        }
        val plan = day?.plan
        if (day != null && plan != null) {
            if (day.before != null || day.journeys("arrive").isNotEmpty()) SectionLabel("From your stay", Modifier.padding(top = 4.dp))
            for (stop in plan.stops) TripDayStop(stop)
            val end = day.window?.end
            val last = plan.stops.lastOrNull()
            if (end != null && last != null && Dates.minutes(end) - Dates.minutes(last.depart) >= 60) {   // journey round 2
                FreeTimeRow(model, last.depart, end, trip.placesPerDay < 6) {
                    scope.launch {
                        model.changeTripDay(trip.id, index, day.window.start, end, minOf(6, trip.placesPerDay + 1))
                    }
                }
            }
            (day.journeys("back") + day.journeys("leave")).forEach { JourneyCard(it) }
            val mine = model.plan?.id == plan.id
            PrimaryButton(if (mine) "This is your day" else "Make this my day", enabled = !mine) {
                if (model.testBPlanAtRisk) confirm = true else use(trip, day)
            }
            Text("Your day gets \"Now\", a reminder to rate each stop, and swapping a stop.", style = Theme.footnote)
            // Abram's comment (8 Oct): plans change; the day is planned again around them
            SecondaryButton("Made other plans? Change this day", icon = Icons.Filled.Schedule) { changing = day }
        } else if (day == null) {
            PrimaryButton(if (model.busy) "Planning…" else "Plan this day", enabled = !model.busy) {
                scope.launch { model.planDay(tripId, index) }
            }
        } else {
            day.journeys("leave").forEach { JourneyCard(it) }
            if (day.before == null) {
                Text(if (day.kind == "arrive" || day.kind == "leave") "A travel day: nothing is planned, so you can take it easy."
                     else "A free day: the places that suit you are already in your other days. More London moments are being checked.",
                    style = Theme.body.copy(color = Theme.inkSoft),
                    modifier = Modifier.fillMaxWidth().border(1.dp, Theme.outline, RoundedCornerShape(20.dp)).padding(20.dp))
            }
        }
    }
    if (confirm) {
        val d = trip?.days?.firstOrNull { it.index == index }
        ReplaceTestBPlanDialog({ confirm = false }) { if (trip != null && d != null) use(trip, d) }
    }
    if (showSafety) SafetyView(model) { showSafety = false }
    changing?.let { d -> if (trip != null) ChangeDaySheet(model, trip, d) { changing = null } }
}

/**
 * Abram's comment (8 Oct): "I'm meeting someone tomorrow." The hours they're free and how many places, then the day
 * planned again around them. The trip's other days stay as they are.
 */
@Composable
fun ChangeDaySheet(model: AppModel, trip: Trip, day: TripDayOut, onClose: () -> Unit) {
    val scope = rememberCoroutineScope()
    // the arrival and leaving days keep the person's own hours: the journeys set their real start and end
    var from by remember { mutableStateOf(if (day.kind == "arrive") trip.dayFrom else day.window?.start ?: trip.dayFrom) }
    var to by remember { mutableStateOf(if (day.kind == "leave") trip.dayTo else day.window?.end ?: trip.dayTo) }
    var places by remember { mutableIntStateOf(trip.placesPerDay) }
    val tooShort = Dates.minutes(to) - Dates.minutes(from) < 60
    val note = when (day.kind) {
        "arrive" -> "This day still starts once you've arrived. Busy in the middle of the day? Choose the part that's free."
        "leave" -> "This day still ends in time for your journey home. Busy in the middle of the day? Choose the part that's free."
        else -> "Busy in the middle of the day? Choose the part that's free. Once it's your day, you can also swap a stop."
    }
    FullSheet(model, onClose) {
        PageWithBottom(spacing = 14, bottom = {
            PrimaryButton(if (model.busy) "Planning…" else "Plan this day again", enabled = !model.busy && !tooShort) {
                scope.launch { if (model.changeTripDay(trip.id, day.index, from, to, places)) onClose() }
            }
        }) {
            CloseLink("Cancel", onClose)   // 19 Oct review: Android's ✕
            Eyebrow("Day ${day.index + 1} · ${Dates.shortDay(day.date)}")
            PageTitle("Change this day")
            Text("Meeting someone, or made other plans? Tell me when you're free, and I'll plan the day again around it. Your other days stay as they are.",
                style = Theme.body.copy(color = Theme.inkSoft))
            Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface)) {
                TimeMenu("Free from", from, HalfHours.from(6, 23)) { from = it }
                Hairline()
                TimeMenu("Until", to, HalfHours.from(6, 23)) { to = it }
            }
            Stepper("Places", "$places place${if (places == 1) "" else "s"}, plus lunch", places <= 1, places >= 6,
                "One place fewer", "One place more", { places -= 1 }) { places += 1 }
            if (tooShort) Text("Leave at least an hour between the two times.", style = Theme.subheadline.copy(color = Theme.accent))
            Text(note, style = Theme.footnote)
        }
    }
}

/** D122: one journey at an end of the trip ("Heathrow → your stay"), with Google Maps for the real route. */
@Composable
fun JourneyCard(leg: TripLeg) {
    val context = LocalContext.current
    val airport = (leg.origin?.maps ?: "").contains("Airport") || (leg.destination?.maps ?: "").contains("Airport")
    val icon = when (leg.slot) {
        "arrive" -> if (leg.mode == "driving") Icons.Filled.DirectionsCar else if (airport) Icons.Filled.FlightLand else Icons.Filled.Tram
        "leave" -> if (leg.mode == "driving") Icons.Filled.DirectionsCar else if (airport) Icons.Filled.FlightTakeoff else Icons.Filled.Tram
        "to_stay" -> Icons.Filled.Bed
        else -> Icons.Filled.LocalMall
    }
    val url = leg.mapsUrl
    Column(Modifier.fillMaxWidth().border(1.dp, Theme.outline, RoundedCornerShape(20.dp))
        .padding(start = 16.dp, end = 16.dp, top = 14.dp, bottom = if (url == null) 14.dp else 4.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Icon(icon, null, tint = Theme.accent, modifier = Modifier.size(24.dp))
            Text(leg.title, style = Theme.serif(19.sp))
        }
        Column(Modifier.padding(start = 34.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            leg.times?.let { Text(it, style = Theme.subheadline.copy(color = Theme.inkSoft)) }
            leg.how?.let { Text(it, style = Theme.subheadline.copy(color = Theme.inkSoft)) }
            leg.note?.let { Text(it, style = Theme.footnote) }
            if (url != null) {
                Text("Directions", style = Theme.subheadline.copy(color = Theme.accent, fontWeight = FontWeight.SemiBold),
                    modifier = Modifier.heightIn(min = 44.dp).padding(top = 12.dp)
                        .clickable(role = Role.Button) { openUrl(context, url.toString()) }
                        .semantics { contentDescription = "Directions, opens Google Maps" })
            }
        }
    }
}

@Composable
fun TripDayStop(stop: Stop) {
    Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(20.dp)).background(Theme.surface).height(IntrinsicSize.Min).padding(12.dp),
        horizontalArrangement = Arrangement.spacedBy(14.dp)) {
        // 20 Oct (round 2): the photo fills the text's height and never sets it (it stretched the card), as on the iPhone
        Box(Modifier.width(70.dp).heightIn(min = 84.dp).fillMaxHeight().clip(RoundedCornerShape(14.dp))) {
            MomentImage(stop.momentId, stop.feelWord, Modifier.matchParentSize())
        }
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text("${stop.arrive} · ${stop.word}", style = Theme.footnote)
            Text(stop.title, style = Theme.serif(20.sp))
            Text(stop.reasons?.firstOrNull()?.you ?: stop.what, style = Theme.subheadline.copy(color = Theme.inkSoft), maxLines = 3)
        }
    }
}

// ---- You -------------------------------------------------------------------------------------------------------

/** The You tab: safety first (999, then a person), what the app has learned in plain words, and your data. */
@Composable
fun YouView(model: AppModel, onHelp: () -> Unit, onData: () -> Unit) {
    val context = LocalContext.current
    LaunchedEffect(Unit) {
        model.loadSafety()
        if (model.learned == null) model.learned = runCatching { model.client.summary() }.getOrNull()
    }
    ScrollPage(spacing = 18, top = 30, bottom = 40) {
        PageTitle("You", style = Theme.serif(36.sp))
        Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(20.dp)).background(Theme.emergencyBg)
            .border(1.dp, Theme.emergencyBorder, RoundedCornerShape(20.dp)).padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("Emergency in the UK", style = Theme.headline.copy(color = Theme.emergencyTitle))
            Text("If you or someone else is in danger, call 999 first.", style = Theme.body.copy(color = Theme.emergencyText))
            Pill("Call 999", PillKind.Danger, height = 52.dp) {
                runCatching {
                    context.startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:999")).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
                }
            }
        }
        Column(Modifier.pressable(onClick = onHelp).surfaceCard(padding = 18.dp, radius = 20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("Talk to a person", style = Theme.headline, modifier = Modifier.weight(1f))
                if (model.unreadSafety) Box(Modifier.size(9.dp).background(Theme.danger, CircleShape))
                Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = Theme.muted)   // 19 Oct: it opens
            }
            Text("Something wrong with a stop, a booking or how you feel? A real person replies here, usually within a few hours.",
                style = Theme.subheadline.copy(color = Theme.inkTertiary))
        }
        Column {
            SectionLabel("What you've told us", Modifier.padding(bottom = 6.dp))
            val items = model.learned?.items ?: emptyList()
            if (items.isEmpty()) {
                Text("Nothing yet. It comes from your answers and your ratings.", style = Theme.body.copy(color = Theme.muted),
                    modifier = Modifier.padding(vertical = 12.dp))
            }
            for (item in items) {
                Text(item.text, style = Theme.serif(19.sp), modifier = Modifier.padding(vertical = 12.dp))
                Hairline()
            }
        }
        Row(Modifier.fillMaxWidth().heightIn(min = 44.dp).clickable(role = Role.Button, onClick = onData),
            verticalAlignment = Alignment.CenterVertically) {
            Text("Your data · what's stored and how to delete it", style = Theme.body.copy(color = Theme.muted), modifier = Modifier.weight(1f))
            Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = Theme.muted)
        }
    }
}
