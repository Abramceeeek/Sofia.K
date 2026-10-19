package com.odys.app

import android.Manifest
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.offset
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
import androidx.compose.material.icons.automirrored.filled.DirectionsWalk
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowLeft
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.PhotoCamera
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Tram
import androidx.compose.material.icons.outlined.Notifications
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.SelectableDates
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TimePicker
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.material3.rememberTimePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.runtime.withFrameNanos
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathMeasure
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.clipRect
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.app.NotificationManagerCompat
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.time.Instant
import java.time.LocalDate
import java.time.LocalTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import kotlin.math.max
import kotlin.math.min

// Screens 8–11: make a day, the day itself, a stop's card and its rating (app/Sources/PlanViews.swift, DayViews.swift).

/** Your day: the current plan (screen 9), or the form to make one (screen 8). */
@Composable
fun DayView(model: AppModel, onHelp: () -> Unit, onData: () -> Unit, onBack: (() -> Unit)?) {
    val plan = model.plan
    if (plan != null) {
        PlanView(model, plan, onHelp, onData, onBack) { model.tripPath += Dest.StopCard(it) }
    } else {
        Column(Modifier.fillMaxSize()) {
            if (onBack != null) Box(Modifier.padding(horizontal = 24.dp)) { BackLink(onClick = onBack) }
            PlanFormView(model, onHelp = onHelp, onData = onData)
        }
    }
}

// ---- screen 8: plan a day ------------------------------------------------------------------------------------

/**
 * D115, D118: next Saturday, 12:00–17:00 from Charing Cross (the Test B day, D104) is filled in, so one tap makes the
 * plan. Today and Tomorrow are one tap too; the day, times and number of stops can be changed.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PlanFormView(model: AppModel, onDone: (() -> Unit)? = null, onHelp: (() -> Unit)? = null, onData: (() -> Unit)? = null) {
    var date by remember { mutableStateOf(Dates.nextSaturday()) }
    var start by remember { mutableIntStateOf(12 * 60) }
    var end by remember { mutableIntStateOf(17 * 60) }
    var stops by remember { mutableIntStateOf(4) }
    var fromHere by remember { mutableStateOf(false) }
    var mustDo by remember { mutableStateOf<MomentSummary?>(null) }
    var pickMust by remember { mutableStateOf(false) }
    var confirm by remember { mutableStateOf(false) }
    var pickDay by remember { mutableStateOf(false) }
    var pickTime by remember { mutableStateOf<String?>(null) }   // "start" | "end"
    val scope = rememberCoroutineScope()
    val askLocation = rememberLocationAsk(model)
    val today = Dates.today()
    val tomorrow = today.plusDays(1)
    val saturday = Dates.nextSaturday()
    val loc = model.location
    val here = loc.roundedHere()
    val inLondon = (loc.metres(AppConfig.START) ?: Double.MAX_VALUE) < 25_000

    fun pick(day: LocalDate) {
        date = day
        start = 12 * 60
        end = 17 * 60
    }

    /** Today: from the next half hour (at the earliest 12:00), for at least three hours, ending by 22:00. */
    fun pickToday() {
        date = today
        val now = Dates.now()
        val soon = now.hour * 60 + now.minute + 15
        val rounded = ((soon + 29) / 30) * 30
        start = max(12 * 60, rounded)
        end = min(max(17 * 60, start + 180), 22 * 60)
    }

    fun make() {
        scope.launch {
            model.makePlan(date, Dates.hhmm(start), Dates.hhmm(end), stops, if (fromHere) loc.roundedHere() else null,
                mustDo?.id)
            if (model.errorMessage == null) onDone?.invoke()
        }
    }

    val startNote = when {
        !fromHere -> "From ${AppConfig.START_NAME}, by the Trafalgar Square exit. Lunch is in the plan if the day spans midday."
        loc.deniedBySettings -> "Location is off for ODYS. Turn it on in your phone's Settings, or start from Charing Cross."
        here == null -> "Finding where you are…"
        !inLondon -> "\"Where I am\" works in London: you seem to be further away, so start from Charing Cross."
        else -> "From where you are now (sent rounded to about 100 m, and not kept). Lunch is in the plan if the day spans midday."
    }

    ScrollPage(spacing = 22) {
        if (onHelp != null || onData != null) TopBar("Your day out", model.unreadSafety, onHelp, onData)
        PageTitle("Plan a day", Modifier.settle(0))
        Column(Modifier.settle(1), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("When", style = Theme.subheadline.copy(color = Theme.muted))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Chip("Today", date == today) { pickToday() }
                Chip("Tomorrow", date == tomorrow) { pick(tomorrow) }
                if (saturday != today && saturday != tomorrow) {
                    Chip(Dates.dayShort(saturday), date == saturday) { pick(saturday) }
                }
            }
        }
        Column(Modifier.settle(2).fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface)) {
            FormRow("Day") { ValueButton(Dates.dayShort(date)) { pickDay = true } }
            FormRow("Start") { ValueButton(Dates.hhmm(start)) { pickTime = "start" } }
            FormRow("Finish by") { ValueButton(Dates.hhmm(end)) { pickTime = "end" } }
            FormRow("Stops") {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp),
                    modifier = Modifier.semantics { contentDescription = "$stops stops" }) {
                    RoundIcon(Icons.Filled.Remove, "Fewer stops", stops <= 3) { stops -= 1 }
                    Text("$stops", style = Theme.title3.copy(color = Theme.accent), textAlign = TextAlign.Center,
                        modifier = Modifier.widthIn(min = 20.dp))
                    RoundIcon(Icons.Filled.Add, "More stops", stops >= 5) { stops += 1 }
                }
            }
            FormRow("Starting near", stacked = true) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Chip("Charing Cross", !fromHere, height = 44.dp) { fromHere = false }
                    Chip("Where I am", fromHere, height = 44.dp) {
                        fromHere = true
                        if (loc.usable) loc.start() else askLocation()
                    }
                }
            }
            FormRow("Must include", last = true) {
                Box(Modifier.heightIn(min = 44.dp).clickable(role = Role.Button) { pickMust = true }
                    .semantics { contentDescription = "Must include: ${mustDo?.title ?: "anything"}. Optional: a place you want in the day" },
                    contentAlignment = Alignment.CenterEnd) {
                    Text(mustDo?.title ?: "Anything", maxLines = 1,
                        style = Theme.body.copy(color = if (mustDo == null) Theme.muted else Theme.accent))
                }
            }
        }
        Text(startNote, style = Theme.footnote)
        PrimaryButton(if (model.busy) "Planning…" else "Make my day",
            enabled = !model.busy && end > start && !(fromHere && (here == null || !inLondon))) {
            if (model.testBPlanAtRisk) confirm = true else make()
        }
    }
    if (confirm) ReplaceTestBPlanDialog({ confirm = false }) { make() }
    if (pickMust) MustIncludePicker(model, mustDo, { pickMust = false }) { mustDo = it; pickMust = false }
    if (pickDay) {
        val first = today.atStartOfDay().toInstant(ZoneOffset.UTC).toEpochMilli()
        val state = rememberDatePickerState(
            initialSelectedDateMillis = date.atStartOfDay().toInstant(ZoneOffset.UTC).toEpochMilli(),
            selectableDates = object : SelectableDates {
                override fun isSelectableDate(utcTimeMillis: Long) = utcTimeMillis >= first
            },
        )
        DatePickerDialog(
            onDismissRequest = { pickDay = false },
            confirmButton = {
                TextButton({
                    state.selectedDateMillis?.let { date = Instant.ofEpochMilli(it).atZone(ZoneOffset.UTC).toLocalDate() }
                    pickDay = false
                }) { Text("OK", color = Theme.accent) }
            },
            dismissButton = { TextButton({ pickDay = false }) { Text("Cancel", color = Theme.inkSoft) } },
        ) { DatePicker(state) }
    }
    pickTime?.let { which ->
        TimeDialog(if (which == "start") start else end, { pickTime = null }) {
            if (which == "start") start = it else end = it
            pickTime = null
        }
    }
    androidx.compose.runtime.DisposableEffect(Unit) { onDispose { if (!model.showNow) model.location.stop() } }
}

/** A 24-hour time, London (the phone's own picker, in a dialog). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TimeDialog(minutes: Int, onDismiss: () -> Unit, onPick: (Int) -> Unit) {
    val state = rememberTimePickerState(minutes / 60, minutes % 60, is24Hour = true)
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = { TextButton({ onPick(state.hour * 60 + state.minute) }) { Text("OK", color = Theme.accent) } },
        dismissButton = { TextButton(onDismiss) { Text("Cancel", color = Theme.inkSoft) } },
        text = { TimePicker(state) },
        containerColor = Theme.surfaceHigh,
    )
}

/** m176: the plan chosen in the Test B comparison, not rated yet: replacing it asks first. */
@Composable
fun ReplaceTestBPlanDialog(onDismiss: () -> Unit, replace: () -> Unit) =
    ConfirmDialog("Replace your Saturday plan?", "You haven't rated it yet. Going on that day and rating each stop helps the test most.",
        "Replace it", "Keep my Saturday plan", onConfirm = replace, onDismiss = onDismiss)

/** A value on the right of a form row that opens its picker. */
@Composable
fun ValueButton(text: String, onClick: () -> Unit) {
    Box(Modifier.heightIn(min = 44.dp).clip(RoundedCornerShape(10.dp)).clickable(role = Role.Button, onClick = onClick)
        .background(Theme.surfaceHigh).padding(horizontal = 12.dp, vertical = 8.dp), contentAlignment = Alignment.Center) {
        Text(text, style = Theme.body.copy(color = Theme.ink))
    }
}

/** m176: "Must include": one of the checked moments, by name. Optional; the planner builds the day around it. */
@Composable
fun MustIncludePicker(model: AppModel, selected: MomentSummary?, onClose: () -> Unit, onPick: (MomentSummary?) -> Unit) {
    var query by remember { mutableStateOf("") }
    var loading by remember { mutableStateOf(model.moments.isEmpty()) }
    LaunchedEffect(Unit) {
        model.loadMoments()
        loading = false
    }
    val all = model.moments.filter { it.status == "ready" }.sortedBy { it.title }
    val shown = if (query.isBlank()) all else all.filter { it.title.contains(query.trim(), ignoreCase = true) }
    FullSheet(model, onClose) {
        Column(Modifier.fillMaxSize()) {
            SheetBar("Must include", close = "Cancel", onClose = onClose)
            Box(Modifier.padding(horizontal = 24.dp, vertical = 8.dp)) {
                LineField("Search places", query, onChange = { query = it })
            }
            LazyColumn(Modifier.fillMaxSize().padding(horizontal = 24.dp)) {
                if (loading) item {
                    Row(Modifier.padding(vertical = 12.dp), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        CircularProgressIndicator(Modifier.size(18.dp), color = Theme.accent, strokeWidth = 2.dp)
                        Text("Loading places…", style = Theme.body.copy(color = Theme.muted))
                    }
                }
                item { PickRow("Anything (no must-include)", selected == null, Theme.accent) { onPick(null) } }
                items(shown, key = { it.id }) { m -> PickRow(m.title, selected?.id == m.id) { onPick(m) } }
            }
        }
    }
}

@Composable
fun PickRow(title: String, on: Boolean, color: Color = Theme.ink, onClick: () -> Unit) {
    Column {
        Row(Modifier.fillMaxWidth().heightIn(min = 52.dp).clickable(role = Role.Button, onClick = onClick),
            verticalAlignment = Alignment.CenterVertically) {
            Text(title, style = Theme.body.copy(color = color), modifier = Modifier.weight(1f))
            if (on) Icon(Icons.Filled.Check, null, tint = Theme.accent)
        }
        Box(Modifier.fillMaxWidth().height(1.dp).background(Theme.hairline))
    }
}

/** One row of a grouped card: a label on the left, its value or control on the right. */
@Composable
fun FormRow(label: String, last: Boolean = false, stacked: Boolean = false, content: @Composable () -> Unit) {
    Column {
        if (stacked) {   // a control too wide to sit beside its label on a phone ("Starting near")
            Column(Modifier.fillMaxWidth().padding(horizontal = 18.dp, vertical = 12.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text(label, style = Theme.body)
                content()
            }
        } else Row(Modifier.fillMaxWidth().heightIn(min = 56.dp).padding(horizontal = 18.dp, vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Text(label, style = Theme.body, modifier = Modifier.weight(1f).padding(end = 12.dp))
            content()
        }
        if (!last) Box(Modifier.fillMaxWidth().height(1.dp).background(Theme.hairline))
    }
}

/** A small round icon button (− and + for the number of stops). */
@Composable
fun RoundIcon(icon: androidx.compose.ui.graphics.vector.ImageVector, label: String, disabled: Boolean, onClick: () -> Unit) {
    Box(Modifier.size(44.dp).pressable(enabled = !disabled, haptic = true, onClick = onClick)
        .semantics { contentDescription = label }, contentAlignment = Alignment.Center) {
        Box(Modifier.size(34.dp).border(1.dp, Theme.outlineStrong, CircleShape), contentAlignment = Alignment.Center) {
            Icon(icon, null, tint = if (disabled) Theme.muted else Theme.ink, modifier = Modifier.size(18.dp))
        }
    }
}

// ---- screen 9: the day ------------------------------------------------------------------------------------------

private const val REVEAL_SECONDS = 2.6f
private const val ROUTE_FROM = 0.28f
private const val ROUTE_TO = 0.88f

/**
 * D119: the day's date, how it should feel (the headline), the numbers, how the day moves, then the stops as a list
 * (or on a map), and "Start the day". Plan again, improve and plan another day at the end. D117: the plan reveal
 * (about 2.6 s, once per new plan) instead of a spinner; with animations off everything is simply there.
 */
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun PlanView(model: AppModel, plan: Plan, onHelp: () -> Unit, onData: () -> Unit, onBack: (() -> Unit)?,
             onOpen: (Stop) -> Unit) {
    val reduce = rememberReduceMotion()
    val scope = rememberCoroutineScope()
    var layout by remember { mutableStateOf(model.prefs.string("planLayout") ?: "list") }
    var reveal by remember { mutableFloatStateOf(1f) }
    var showNewPlan by remember { mutableStateOf(false) }
    var showImprove by remember { mutableStateOf(false) }
    var confirmRegenerate by remember { mutableStateOf(false) }
    var replanning by remember { mutableStateOf(false) }
    var swapping by remember { mutableStateOf<Stop?>(null) }

    val shown = if (model.revealPlanId == plan.id && !reduce) 0f else reveal
    fun phase(from: Float, to: Float) = ((shown - from) / max(to - from, 0.001f)).coerceIn(0f, 1f)
    val fractions = RouteMath.stopFractions(plan.stops)
    fun rowShown(i: Int): Float {
        val at = ROUTE_FROM + (ROUTE_TO - ROUTE_FROM) * (fractions.getOrNull(i) ?: 1f)
        return phase(at, at + 0.06f)
    }

    LaunchedEffect(plan.id) {
        if (model.revealPlanId != plan.id) return@LaunchedEffect
        model.revealPlanId = null
        if (reduce) {
            reveal = 1f
            return@LaunchedEffect
        }
        reveal = 0f
        val start = withFrameNanos { it }
        while (reveal < 1f) {
            val t = withFrameNanos { it }
            reveal = min(1f, (t - start) / 1e9f / REVEAL_SECONDS)
        }
    }

    ScrollPage(spacing = 22, bottom = 40) {
        if (onBack != null) BackLink(onClick = onBack)
        TopBar(Dates.longDay(plan.date) ?: plan.title ?: "Your day", model.unreadSafety, onHelp, onData)
        // Bloom: the headline settles first, then the numbers
        val settle = phase(0f, 0.15f)
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            val headline = if (!plan.isBlind && !plan.feelLine.isNullOrEmpty()) plan.feelLine else plan.title ?: "Your day"
            Text(headline, style = Theme.serif(31.sp), modifier = Modifier.semantics { heading() }.graphicsLayer {
                alpha = settle
                translationY = if (reduce) 0f else (1 - settle) * 14.dp.toPx()
            })
            PlanStats(plan, Modifier.graphicsLayer { alpha = phase(if (plan.isBlind) 0f else 0.12f, 0.25f) })
        }
        AnimatedVisibility(!model.reminderAsked && !plan.isBlind && shown >= 1f, enter = fadeIn(), exit = fadeOut()) {
            ReminderAsk(model)   // D118: asked once, right after a plan, never before
        }
        DayMoves(plan, phase(0.2f, 0.6f), Modifier.graphicsLayer { alpha = phase(0.18f, 0.3f) })
        ViewToggle(layout) {
            layout = it
            model.prefs.set("planLayout", it)
        }
        if (layout == "map") {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                val pins = plan.stops.mapIndexedNotNull { i, s -> s.pin?.let { MapPin(it, s.title, i + 1) } }
                OsmMap(pins, Modifier.fillMaxWidth().height(260.dp).clip(RoundedCornerShape(22.dp)), route = true,
                    progress = phase(ROUTE_FROM, ROUTE_TO)) { i ->
                    plan.stops.getOrNull(pins[i].number!! - 1)?.let(onOpen)
                }
                Text("Tap a pin, or open a stop, for directions.", style = Theme.footnote)
            }
        }
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            plan.stops.forEachIndexed { i, stop ->
                androidx.compose.runtime.key(stop.id) {
                    Column(Modifier.graphicsLayer { alpha = rowShown(i) }, verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        if (stop.travelText.isNotEmpty()) TravelLine(stop)
                        val swappable = stop.rateable && model.lastRequest != null   // Build 2: never on the Test B plan
                        StopCard(i + 1, stop, rated = stop.momentId in model.rated, swapped = model.swappedIn == stop.momentId,
                            showWhy = !plan.isBlind,
                            modifier = Modifier.combinedClickable(
                                onClick = { onOpen(stop) },
                                onLongClick = if (swappable) ({ swapping = stop }) else null,
                                onLongClickLabel = if (swappable) "Swap this stop" else null,
                            ))
                    }
                }
            }
        }
        val free = model.freeTime(plan)
        if (free != null && shown >= 1f) {   // journey round 2: free time, said plainly
            FreeTimeRow(model, free.first, free.second, (model.lastRequest?.stops ?: 6) < 6) {
                scope.launch { model.addPlace() }
            }
        }
        Text(if (model.lastRequest == null) "Open a stop to see how you'll arrive."
             else "Open a stop to see how you'll arrive, or to swap it. Press and hold a stop to swap it.",
            style = Theme.footnote)
        PrimaryButton("Start the day") { model.startDay() }   // D119: "Now", while you're out
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            if (model.improved) {
                SecondaryButton("Plan this day again with your new answers", enabled = !model.busy) {
                    scope.launch { model.replan() }
                }
            }
            if (model.ratedOnce || model.improved) {
                // D118: offered once a stop is rated, so it doesn't arrive as a second ask on top of the plan
                Row(Modifier.pressable { showImprove = true }.surfaceCard(), horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                    Box(Modifier.padding(top = 4.dp)) { ArchGlyph() }
                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(if (model.improved) "Change your answers" else "Your first stop taught us something", style = Theme.title3)
                        Text(if (model.improved) "Your budget, pace and interests, a few more places and example days."
                             else "Make the next day even better? About 30 seconds, then more if you like.",
                            style = Theme.subheadline.copy(color = Theme.muted))
                    }
                }
            } else {
                QuietButton("A few more questions (optional)", Modifier.fillMaxWidth()) { showImprove = true }
            }
            if (model.lastRequest != null && plan.date == Dates.todayIso()) {   // decision 3
                SecondaryButton("Plans changed? Re-plan the rest of today", enabled = !model.busy) { replanning = true }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                if (model.lastRequest != null) {   // Build 2: the Test B plan is rated as it was chosen
                    SecondaryButton("Plan again", Modifier.weight(1f), enabled = !model.busy) { confirmRegenerate = true }
                }
                SecondaryButton("Another day", Modifier.weight(1f)) {
                    model.planAnotherDay()
                    showNewPlan = true
                }
            }
        }
    }

    if (confirmRegenerate) {
        ConfirmDialog("Make a new plan for this day?", "You'll get different stops for the same times. This plan will be replaced.",
            "Plan this day again", "Keep this plan", onConfirm = { scope.launch { model.regenerate() } },
            onDismiss = { confirmRegenerate = false })
    }
    swapping?.let { stop ->
        ConfirmDialog("Swap ${stop.title} for something else?", "The other stops stay. This one won't come back in this plan.",
            "Swap it", "Keep it", onConfirm = { scope.launch { model.swap(stop) } }, onDismiss = { swapping = null })
    }
    if (replanning) ReplanRestDialog(model) { replanning = false }
    if (showNewPlan) {
        FullSheet(model, { showNewPlan = false }) {
            Column(Modifier.fillMaxSize()) {
                SheetBar(onClose = { showNewPlan = false })
                PlanFormView(model, onDone = { showNewPlan = false })
            }
        }
    }
    if (showImprove) ImproveView(model) { showImprove = false }
}

/** List or Map, as two soft tabs. */
@Composable
fun ViewToggle(selection: String, onChange: (String) -> Unit) {
    Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)).background(Theme.surface).padding(3.dp)) {
        for ((title, value) in listOf("List" to "list", "Map" to "map")) {
            val on = (selection == "map") == (value == "map")
            Box(Modifier.weight(1f).heightIn(min = 44.dp).clip(RoundedCornerShape(9.dp))
                .background(if (on) Theme.surfaceHigh else Color.Transparent)
                .clickable(role = Role.Tab) { onChange(value) }
                .semantics { selected = on }, contentAlignment = Alignment.Center) {
                Text(title, style = Theme.subheadline)
            }
        }
    }
}

/** D117: where each stop sits along the day's route (0 for the first, 1 for the last). */
object RouteMath {
    private fun dist(a: Point, b: Point): Double {
        val k = kotlin.math.cos(a.lat * Math.PI / 180)
        return kotlin.math.hypot(b.lat - a.lat, (b.lon - a.lon) * k)
    }

    fun fractions(cs: List<Point>): List<Float> {
        if (cs.size < 2) return cs.map { 0f }
        val acc = mutableListOf(0.0)
        for (i in 1 until cs.size) acc += acc[i - 1] + dist(cs[i - 1], cs[i])
        val total = max(acc.last(), 1e-9)
        return acc.map { (it / total).toFloat() }
    }

    /** Per stop: a stop without a pin takes the one before it. */
    fun stopFractions(stops: List<Stop>): List<Float> {
        val withPin = stops.indices.filter { stops[it].pin != null }
        val f = fractions(withPin.mapNotNull { stops[it].pin })
        var last = 0f
        return stops.indices.map { i ->
            val j = withPin.indexOf(i)
            if (j >= 0) last = f[j]
            last
        }
    }
}

/** Cost per person, walking between stops and the finish time (D110), then what the cost is made of. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun PlanStats(plan: Plan, modifier: Modifier = Modifier) {
    val t = plan.totals ?: return
    Column(modifier, verticalArrangement = Arrangement.spacedBy(6.dp)) {
        FlowRow(horizontalArrangement = Arrangement.spacedBy(18.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            val style = Theme.subheadline.copy(color = Theme.inkSoft)
            Text("${Money.text(t.costGbp)} per person", style = style)
            Text(String.format(java.util.Locale.UK, "%.1f km walking between stops", t.walkKm), style = style)
            Text("Done by ${t.finish ?: plan.stops.lastOrNull()?.depart ?: "–"}", style = style)
        }
        val spend = if (t.spendGbp > 0) "${Money.text(t.spendGbp)} food and entry" else "Free entry"
        val fare = if (t.transportGbp > 0) "${Money.text(t.transportGbp)} Tube or bus" else "all on foot"
        Text("$spend, $fare." + (plan.summary?.firstOrNull()?.let { " $it." } ?: ""), style = Theme.footnote)
        plan.weather?.line?.takeIf { it.isNotEmpty() }?.let { Text(it, style = Theme.footnote) }
    }
}

/**
 * "How the day moves" (D119, the ODYS curve): one point per stop across the day, higher where we expect you to enjoy
 * it more (from the worth to you, so never in the blind comparison or the example day), with each stop's word.
 */
@Composable
fun DayMoves(plan: Plan, progress: Float = 1f, modifier: Modifier = Modifier) {
    val personal = !plan.isBlind && plan.stops.any { it.worthGbp != null }
    val top = plan.stops.mapNotNull { it.worthGbp }.maxOrNull() ?: 0.0
    val points = plan.stops.map { s ->
        CurvePoint(Dates.minutes(s.arrive).toFloat(),
            if (personal && top > 0) (s.worthGbp?.let { max(0.22, it / top) } ?: 0.4).toFloat() else 0.55f, s.word, s.arrive)
    }
    val peak = if (personal) points.indices.maxByOrNull { points[it].level } else null
    Column(modifier.fillMaxWidth().clip(RoundedCornerShape(22.dp)).background(Theme.deep).padding(16.dp)
        .semantics { contentDescription = "How the day moves: " + points.joinToString("; ") { "${it.time}, ${it.word}" } },
        verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text("How the day moves", style = Theme.subheadline.copy(color = Theme.muted))
        Text(if (personal) "Higher means we think you'll enjoy it more. Each word is the kind of moment a stop is."
             else "Each word is the kind of moment a stop is.", style = Theme.footnote.copy(color = Theme.inkTertiary))
        DayCurve(points, progress, peak, Modifier.padding(top = 8.dp))
    }
}

data class CurvePoint(val minute: Float, val level: Float, val word: String, val time: String)

/** A smooth line through the stops, a soft amber fill under it, a dot at each stop and its word and time underneath. */
@Composable
fun DayCurve(points: List<CurvePoint>, progress: Float, peak: Int?, modifier: Modifier = Modifier) {
    val measurer = rememberTextMeasurer()
    val reduce = rememberReduceMotion()
    val pulse = remember { Animatable(1f) }
    LaunchedEffect(progress >= 1f) {
        if (progress >= 1f && peak != null && !reduce) {
            pulse.animateTo(1.7f, tween(300))
            pulse.animateTo(1f, tween(300))
        }
    }
    val rows = if (points.size >= 4) 2 else 1
    val curveH = 104f
    val rowH = 40f
    Canvas(modifier.fillMaxWidth().height((curveH + rows * rowH + 2).dp)) {
        val d = density
        val w = size.width
        val lo = (points.minOfOrNull { it.minute } ?: 600f) - 35
        val hi = (points.maxOfOrNull { it.minute } ?: 1020f) + 35
        fun x(m: Float) = 8 * d + (m - lo) / max(hi - lo, 1f) * (w - 16 * d)
        fun y(l: Float) = (90 - l * 70) * d
        val pts = listOf(Offset(0f, 92 * d)) + points.map { Offset(x(it.minute), y(it.level)) } + listOf(Offset(w, 92 * d))
        val line = Path().apply {
            moveTo(pts[0].x, pts[0].y)
            for (i in 1 until pts.size) {
                val a = pts[i - 1]
                val b = pts[i]
                val dx = (b.x - a.x) / 2
                cubicTo(a.x + dx, a.y, b.x - dx, b.y, b.x, b.y)
            }
        }
        drawLine(Theme.ink.copy(alpha = 0.1f), Offset(0f, 96 * d), Offset(w, 96 * d), strokeWidth = d)
        val area = Path().apply {
            addPath(line)
            lineTo(w, 96 * d)
            lineTo(0f, 96 * d)
            close()
        }
        drawPath(area, Brush.verticalGradient(listOf(Theme.accent.copy(alpha = 0.4f * progress), Theme.accent.copy(alpha = 0f)),
            startY = 20 * d, endY = 96 * d))
        val part = Path()
        PathMeasure().apply {
            setPath(line, false)
            getSegment(0f, length * progress.coerceIn(0f, 1f), part, true)
        }
        drawPath(part, Theme.accent, style = Stroke(2.5f * d, cap = StrokeCap.Round, join = StrokeJoin.Round))
        points.forEachIndexed { i, p ->
            val px = x(p.minute)
            if (progress < px / max(w, 1f) - 0.01f) return@forEachIndexed
            val k = if (i == peak) pulse.value else 1f
            drawCircle(Theme.deep, 7.5f * d * k, Offset(px, y(p.level)))
            drawCircle(Theme.accent, 4.5f * d * k, Offset(px, y(p.level)))
            val word = measurer.measure(p.word, Theme.italic(16.sp, Theme.ink))
            val time = measurer.measure(p.time, Theme.caption)
            val cx = px.coerceIn(34 * d, w - 34 * d)
            val row = if (rows == 2) i % 2 else 0
            val cy = (curveH + 18 + row * rowH) * d
            val blockH = word.size.height + time.size.height
            drawText(word, topLeft = Offset(cx - word.size.width / 2, cy - blockH / 2))
            drawText(time, topLeft = Offset(cx - time.size.width / 2, cy - blockH / 2 + word.size.height))
        }
    }
}

/** How you get to a stop, between the cards. */
@Composable
fun TravelLine(stop: Stop) {
    Row(Modifier.padding(start = 6.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Icon(if (stop.travelMode == "walk") Icons.AutoMirrored.Filled.DirectionsWalk else Icons.Filled.Tram, null,
            tint = Theme.muted, modifier = Modifier.size(16.dp).padding(top = 2.dp))
        Text(stop.travelText, style = Theme.footnote)
    }
}

/**
 * One stop on the day (D119): its photo or field, "13:30–14:15 · Awe", the title, the reason in plain words (D115),
 * and the worth to you in amber (D88, D118).
 */
@Composable
fun StopCard(number: Int, stop: Stop, rated: Boolean = false, swapped: Boolean = false, showWhy: Boolean = true,
             modifier: Modifier = Modifier) {
    Row(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(20.dp)).then(modifier).background(Theme.surface)
            .height(IntrinsicSize.Min).padding(12.dp),
        horizontalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Box(Modifier.width(78.dp).heightIn(min = 96.dp).fillMaxHeight().clip(RoundedCornerShape(14.dp))) {
            MomentImage(stop.momentId, stop.feelWord, Modifier.fillMaxSize())
            Box(Modifier.padding(6.dp).size(22.dp).background(Theme.background.copy(alpha = 0.85f), CircleShape),
                contentAlignment = Alignment.Center) {
                Text("$number", style = Theme.caption.copy(color = Theme.accent, fontWeight = FontWeight.Bold))
            }
        }
        Column(Modifier.weight(1f).padding(vertical = 2.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
            Text("${stop.arrive}–${stop.depart} · ${stop.word}", style = Theme.subheadline.copy(color = Theme.muted))
            Text(stop.title, style = Theme.title3)
            if (showWhy) stop.reasons?.firstOrNull()?.you?.let {
                Text(it, style = Theme.subheadline.copy(color = Theme.inkSoft))
            }
            if (showWhy) stop.worthLine?.let { Text(it, style = Theme.subheadline.copy(color = Theme.accent)) }
            val badges = listOfNotNull(if (swapped) "Swapped in" else null, if (stop.familiar) "A place you loved" else null,
                if (rated) "Rated" else null)
            if (badges.isNotEmpty()) Text(badges.joinToString(" · "), style = Theme.italic(15.sp))
        }
    }
}

/** Rating opens at the planned arrival (D110: only after the visit). Null when the plan has no date. */
fun Stop.ratingOpens(day: String?): ZonedDateTime? {
    val d = Dates.parse(day) ?: return null
    val t = runCatching { LocalTime.parse(arrive.take(5)) }.getOrNull() ?: return null
    return ZonedDateTime.of(d, t, Dates.london)
}

/** "free" → "Free", for lines shown under their own label. */
val String.capitalizedFirst: String get() = replaceFirstChar { it.uppercase() }

// ---- the moment card --------------------------------------------------------------------------------------------

/** The moment card, framed as a picture and its details, for the example day (screen 2, D115). */
@Composable
fun MomentCardContent(model: AppModel, stop: Stop, showWhy: Boolean = true, basis: Basis? = null) {
    Column(verticalArrangement = Arrangement.spacedBy(20.dp)) {
        MomentHero(stop, height = 260.dp, rounded = true)
        MomentCardBody(model, stop, basis, showWhy)
    }
}

/**
 * The big picture at the top of a moment card: the card's photo (openly licensed, its credit underneath), or for a
 * card without one a map of the place: real, not invented. The time, the kind of moment and the title sit at its foot.
 */
@Composable
fun MomentHero(stop: Stop, height: Dp = 380.dp, rounded: Boolean = false, drift: Boolean = false) {
    val context = LocalContext.current
    val info = remember(stop.momentId) { CardPhotos.info(context, stop.momentId) }
    val shape = RoundedCornerShape(if (rounded) 22.dp else 0.dp)
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Box(Modifier.fillMaxWidth().height(height).clip(shape)) {
            val pin = stop.pin
            when {
                info != null -> MomentImage(stop.momentId, stop.feelWord, Modifier.fillMaxSize(), drift = drift)
                pin != null -> OsmMap(listOf(MapPin(pin, stop.title)), Modifier.fillMaxSize(), zoom = 16)
                else -> Box(Modifier.fillMaxSize().background(fieldBrush(stop.feelWord)))
            }
            if (!rounded) {   // so the back button reads on a bright photo
                Box(Modifier.fillMaxWidth().height(130.dp).background(Brush.verticalGradient(listOf(Color.Black.copy(alpha = 0.5f),
                    Color.Transparent))))
            }
            Column(
                Modifier.align(Alignment.BottomStart).fillMaxWidth()
                    .background(Brush.verticalGradient(0f to Color.Transparent, 0.3f to Theme.background.copy(alpha = 0.7f),
                        1f to Theme.background.copy(alpha = if (rounded) 0.92f else 1f)))
                    .padding(horizontal = if (rounded) 18.dp else 24.dp).padding(top = 48.dp, bottom = if (rounded) 18.dp else 24.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                Text("${stop.arrive}–${stop.depart} · ${stop.word}", style = Theme.subheadline.copy(color = Theme.amberDeep))
                Text(stop.title, style = if (rounded) Theme.title else Theme.h1, modifier = Modifier.semantics { heading() })
            }
        }
        if (info != null) {
            // the credit the licence asks for; it opens the photo's page on Wikimedia Commons
            Text(info.credit, style = Theme.caption.copy(textDecoration = TextDecoration.Underline),
                modifier = Modifier.padding(horizontal = if (rounded) 0.dp else 24.dp)
                    .clickable(role = Role.Button) { openUrl(context, info.source) })
        }
    }
}

/** Everything under the picture (D112, D115, D119): why it was picked, the way in, the shot card, then the details. */
@Composable
fun MomentCardBody(model: AppModel, stop: Stop, basis: Basis?, showWhy: Boolean = true) {
    var showShot by remember { mutableStateOf(false) }
    Column(verticalArrangement = Arrangement.spacedBy(26.dp)) {
        if (stop.familiar) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Filled.Favorite, null, tint = Theme.accent, modifier = Modifier.size(16.dp))
                Text("A place you loved", style = Theme.subheadline.copy(color = Theme.accent))
            }
        }
        val reasons = if (showWhy) stop.reasons ?: emptyList() else emptyList()
        if (reasons.isNotEmpty() || (showWhy && stop.worthLine != null)) {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("Why we picked this for you", style = Theme.subheadline.copy(color = Theme.muted))
                for (r in reasons) Text(r.you, style = Theme.serif(22.sp))
                if (basis != null && reasons.isNotEmpty()) Text(basis.soFar, style = Theme.footnote)
                stop.worthLine?.let {
                    Text(it, style = Theme.body.copy(color = Theme.accent), modifier = Modifier.padding(top = 4.dp))
                    Text("A first estimate from what you've told us so far.", style = Theme.footnote)   // D118
                }
            }
        }
        val steps = stop.approachSteps ?: emptyList()
        if (stop.travelText.isNotEmpty() || steps.isNotEmpty() || stop.approach.isNotEmpty()) {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("The way in", style = Theme.subheadline.copy(color = Theme.muted))
                if (stop.travelText.isNotEmpty()) Text(stop.travelText, style = Theme.subheadline.copy(color = Theme.inkSoft))
                if (steps.isNotEmpty()) Box(Modifier.padding(top = 6.dp)) { WayIn(steps, stop.reveal == true) }
                else if (stop.approach.isNotEmpty()) Text(stop.approach, style = Theme.body)
            }
        }
        val card = stop.card
        val shot = card?.shotCard
        if (card != null && shot != null) {
            Column(Modifier.pressable { showShot = true }.surfaceCard(padding = 18.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Filled.PhotoCamera, null, tint = Theme.muted, modifier = Modifier.size(16.dp))
                    Text("  Shot card", style = Theme.subheadline.copy(color = Theme.muted), modifier = Modifier.weight(1f))
                    Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = Theme.muted)
                }
                Text(shot.standAt?.note ?: shot.frame ?: "Where to stand for the best photo.", style = Theme.body)
            }
        }
        val checked = Dates.parse(stop.checked)?.let {
            "Hours, prices and the way in last checked on ${Dates.dayMonth(it)}, from the place's own site."
        } ?: ""
        val light = stop.bestLight ?: ""
        val window = stop.bestWindow ?: ""
        val best = if (light.isEmpty()) "" else (if (light.endsWith(".")) light else "$light.") +
            (if (window.isEmpty()) "" else " On your day: $window.")
        DetailRows(listOf(
            "Best time and light" to best,
            "What happens" to stop.what,
            "Opening hours" to (stop.hours ?: ""),     // m176: checked on the card's own source
            "Book ahead" to (stop.bookAhead ?: ""),
            "Checked" to checked,                       // decision 4
            "Queue" to if ((stop.queueMin ?: 0.0) > 0) "Allow about ${(stop.queueMin ?: 0.0).toInt()} min to queue." else "",
            "Cost" to stop.costText.replace("Cost: ", "").capitalizedFirst,
            "If it rains" to stop.rainSwap,
        ))
    }
    if (showShot && stop.card != null) {
        FullSheet(model, { showShot = false }) {
            Column(Modifier.fillMaxSize()) {
                SheetBar("Shot card") { showShot = false }
                Column(Modifier.verticalScroll(rememberScrollState()).padding(24.dp)) { ShotCardView(stop.card) }
            }
        }
    }
}

/** "The way in" (D119): the approach as a path you can tap along; the light walks down it and glows at the reveal. */
@Composable
fun WayIn(steps: List<ApproachStep>, reveal: Boolean) {
    var current by remember { mutableIntStateOf(0) }
    Column {
        steps.forEachIndexed { i, step ->
            val last = i == steps.size - 1
            val done = i < current
            val on = i == current
            val isReveal = last && reveal
            Row(
                Modifier.fillMaxWidth().height(IntrinsicSize.Min).clickable(role = Role.Button) { current = i }
                    .semantics { contentDescription = "${step.label}: ${step.text}" + if (isReveal) ". The reveal." else "" },
                horizontalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                Column(Modifier.width(22.dp).fillMaxHeight(), horizontalAlignment = Alignment.CenterHorizontally) {
                    val dot = if (on) 16.dp else 12.dp
                    Box(Modifier.size(22.dp), contentAlignment = Alignment.Center) {
                        Box(Modifier.size(dot)
                            .then(if (isReveal && on) Modifier.shadow(8.dp, CircleShape, ambientColor = Theme.accent, spotColor = Theme.accent) else Modifier)
                            .background(if (on || done) Theme.accent else Color.Transparent, CircleShape)
                            .border(2.dp, if (on || done) Theme.accent else Color(0xFF4A4E57), CircleShape))
                    }
                    if (!last) Box(Modifier.width(2.dp).weight(1f).background(if (done) Theme.accent else Theme.line))
                }
                Column(Modifier.weight(1f).padding(bottom = if (last) 0.dp else 18.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(step.label, style = Theme.footnote)
                    Text(step.text, style = Theme.body.copy(color = if (on) Theme.ink else if (done) Theme.inkTertiary else Theme.inkSoft))
                    if (isReveal) Eyebrow("The reveal", color = Theme.accent)
                }
            }
        }
    }
}

/** The shot card in full, opened from a stop that has one. */
@Composable
fun ShotCardView(card: Card) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        PageTitle(card.title, style = Theme.title2)
        val shot = card.shotCard ?: return@Column
        val lat = shot.standAt?.lat
        val lon = shot.standAt?.lon
        if (lat != null && lon != null) {
            OsmMap(listOf(MapPin(Point(lat, lon), "Stand here")), Modifier.fillMaxWidth().height(170.dp)
                .clip(RoundedCornerShape(18.dp)), zoom = 16)
        }
        DetailRows(listOf("Where to stand" to (shot.standAt?.note ?: ""), "Which way to face" to (shot.face ?: ""),
            "What to frame" to (shot.frame ?: ""), "When" to (shot.`when` ?: ""), "What spoils it" to (shot.avoid ?: "")))
    }
}

// ---- screen 10: a stop ------------------------------------------------------------------------------------------

/** The moment card, full-bleed, then directions, swapping and (after the visit) rating and sharing. */
@Composable
fun StopView(model: AppModel, stop: Stop, planId: Int? = null, onBack: () -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var showRating by remember { mutableStateOf(false) }
    var confirmSwap by remember { mutableStateOf(false) }
    var confirmRegenerate by remember { mutableStateOf(false) }
    var sharing by remember { mutableStateOf(false) }
    var reporting by remember { mutableStateOf(false) }
    val done = stop.momentId in model.rated
    val opens = stop.ratingOpens(model.plan?.date)
    val now = Dates.now()
    val canRate = stop.rateable && !done && (opens == null || !opens.isAfter(now))
    BackTo(onBack = onBack)
    Box(Modifier.screen()) {
        Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState())) {
            MomentHero(stop, drift = true)
            Column(Modifier.padding(horizontal = 24.dp).padding(top = 14.dp, bottom = 40.dp).navigationBarsPadding(),
                verticalArrangement = Arrangement.spacedBy(26.dp)) {
                MomentCardBody(model, stop, model.plan?.basis, showWhy = model.plan?.isBlind != true)
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    if (canRate) PrimaryButton("Been here? How did it feel?") { showRating = true }
                    stop.pin?.let { pin ->
                        // journey audit: by Tube or bus when the plan's leg is, else walking
                        val url = directionsUrl(pin, stop.travelMode == "transit")
                        if (canRate) SecondaryButton("Directions in Google Maps") { openUrl(context, url) }
                        else PrimaryButton("Directions in Google Maps") { openUrl(context, url) }
                    }
                    if (stop.rateable && model.lastRequest != null) {   // Build 2: not on the Test B plan
                        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                            SecondaryButton("Swap this stop", Modifier.weight(1f), enabled = !model.busy) { confirmSwap = true }
                            SecondaryButton("Plan again", Modifier.weight(1f), enabled = !model.busy) { confirmRegenerate = true }
                        }
                    }
                }
                if (stop.rateable) {
                    if (opens != null && opens.isAfter(now) && !done) {
                        Text("You can rate this stop after your visit, from ${stop.arrive} on ${Dates.dayName(opens.toLocalDate())}.",
                            style = Theme.subheadline.copy(color = Theme.muted))
                    } else if (done) {
                        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                            Row(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
                                ArchGlyph()
                                Text("Rated. Thank you.", style = Theme.body.copy(color = Theme.inkSoft))
                            }
                            if (model.myRatings[stop.momentId] != null && !stop.isGeneric) {
                                // D114: for any rating, so rating high never unlocks anything
                                SecondaryButton("Share this moment", icon = Icons.Filled.Share) { sharing = true }
                            }
                        }
                    }
                }
                // UX checklist (9 Oct): a wrong price, hours or route is reported where it's seen, to a person
                QuietButton("Something wrong with this place? Tell us", Modifier.fillMaxWidth()) { reporting = true }
            }
        }
        Box(Modifier.statusBarsPadding().padding(start = 12.dp, top = 4.dp)
            .clip(CircleShape).background(Theme.background.copy(alpha = 0.55f)).padding(end = 10.dp)) {
            BackLink(onClick = onBack)
        }
    }
    if (confirmSwap) {
        ConfirmDialog("Swap ${stop.title} for something else?", "The other stops stay. This one won't come back in this plan.",
            "Swap it", "Keep it", onConfirm = {
                scope.launch {
                    model.swap(stop)
                    if (model.errorMessage == null) onBack()
                }
            }, onDismiss = { confirmSwap = false })
    }
    if (confirmRegenerate) {
        ConfirmDialog("Make a new plan for this day?", "You'll get different stops for the same times. This plan will be replaced.",
            "Plan this day again", "Keep this plan", onConfirm = {
                scope.launch {
                    model.regenerate()
                    if (model.errorMessage == null) onBack()
                }
            }, onDismiss = { confirmRegenerate = false })
    }
    if (showRating) RatingView(model, stop, planId) { showRating = false }
    if (reporting) SafetyView(model, prefill = "About ${stop.title}: ") { reporting = false }
    if (sharing) SharePreview(model, stop, model.myRatings[stop.momentId] ?: 5) { sharing = false }
}

// ---- screen 11: the rating ----------------------------------------------------------------------------------

private val ratingLevels = listOf(0.12f, 0.32f, 0.55f, 0.8f, 1f)

/**
 * After the visit, one word on a 1–5 scale. The arch fills with light to the word (Flat … Unforgettable). Save sends it
 * (so a mis-tap isn't sent); then a mote of light rises into the arch, a thank-you, and "Share this moment" (for any
 * rating, D114) or on to the next stop.
 */
@Composable
fun RatingView(model: AppModel, stop: Stop, planId: Int? = null, onNext: (() -> Unit)? = null, onClose: () -> Unit) {
    var rating by remember { mutableStateOf<Int?>(null) }
    var bring by remember { mutableStateOf("") }
    var saved by remember { mutableStateOf(false) }
    var mote by remember { mutableIntStateOf(0) }
    var sharing by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    FullSheet(model, onClose) {
        Column(Modifier.fillMaxSize()) {
            SheetBar(onClose = onClose)
            ScrollPage(spacing = 14, top = 0, bottom = 24) {
                Eyebrow("Just finished")
                PageTitle("How did ${stop.title} feel?", style = Theme.serif(30.sp))
                Box(Modifier.fillMaxWidth().padding(vertical = 4.dp), contentAlignment = Alignment.Center) {
                    RatingArch(rating?.let { ratingLevels[it - 1] } ?: 0f, mote, Modifier.size(150.dp, 190.dp))
                }
                if (saved) {
                    Column(Modifier.settle(), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Text("Thank you. That helps the next day fit better.", style = Theme.italic(19.sp, Theme.inkSoft),
                            textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())
                        if (model.lastRatingQueued) {   // journey audit: no signal; kept on the phone
                            Text("Saved on your phone. It'll send the next time you open ODYS with signal.", style = Theme.footnote,
                                textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())
                        } else if (!stop.isGeneric) {   // m176: a generic Test B stop has no card to share
                            PrimaryButton("Share this moment") { sharing = true }
                        }
                        SecondaryButton(if (onNext == null) "Done" else "On to the next stop") {
                            onNext?.invoke()
                            onClose()
                        }
                    }
                } else {
                    ScaleRow("Flat", "Unforgettable", rating, Labels.feel) { rating = it }
                    AnimatedVisibility(rating != null, enter = fadeIn(), exit = fadeOut()) {
                        Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                            Column(Modifier.padding(top = 6.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                                Text("Would you bring someone here? (optional)", style = Theme.subheadline.copy(color = Theme.muted))
                                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                    Chip("Yes", bring == "yes", height = 44.dp) { bring = if (bring == "yes") "" else "yes" }
                                    Chip("No", bring == "no", height = 44.dp) { bring = if (bring == "no") "" else "no" }
                                }
                            }
                            PrimaryButton(if (model.busy) "Saving…" else "Save", enabled = !model.busy) {
                                val r = rating ?: return@PrimaryButton
                                scope.launch {
                                    model.rate(stop, r, if (bring.isEmpty()) null else bring == "yes", planId)
                                    if (model.errorMessage == null) {
                                        saved = true
                                        mote += 1
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    if (sharing) SharePreview(model, stop, rating ?: 5) { sharing = false }
}

/** The rating's arch: dark inside, filling with light from the bottom to the chosen word; the pool brightens with it. */
@Composable
fun RatingArch(level: Float, mote: Int, modifier: Modifier = Modifier) {
    val reduce = rememberReduceMotion()
    val shown by animateFloatAsState(level, if (reduce) Motion.fade() else tween(700, 0, Motion.settleEasing), label = "level")
    val moteY = remember { Animatable(0f) }
    val moteAlpha = remember { Animatable(0f) }
    LaunchedEffect(mote) {
        if (mote == 0 || reduce) return@LaunchedEffect
        moteY.snapTo(60f)
        moteAlpha.snapTo(1f)
        launch { moteY.animateTo(-30f, tween(600)) }
        moteAlpha.animateTo(0f, tween(600))
    }
    Canvas(modifier.semantics { }) {
        val s = min(size.width / 120f, size.height / 152f)
        val oy = size.height / 2 - 76 * s
        val door = Door.rating.path(size)
        drawPath(door, Theme.surface)
        val yCut = oy + (120 - shown * (120 - 24)) * s
        clipRect(top = yCut) {
            drawPath(door, Brush.verticalGradient(listOf(Theme.amberLight, Theme.amberDeep), startY = oy + 24 * s, endY = oy + 120 * s))
        }
        drawPath(door, Theme.line, style = Stroke(3 * density))
        drawPath(Pool.rating.path(size), Theme.accent.copy(alpha = shown * 0.5f))
        if (moteAlpha.value > 0f) {
            val c = Offset(size.width / 2, size.height / 2 + moteY.value * density)
            drawCircle(Theme.accent.copy(alpha = 0.4f * moteAlpha.value), 8 * density, c)
            drawCircle(Theme.amberLight.copy(alpha = moteAlpha.value), 4 * density, c)
        }
    }
}

// ---- around the plan ------------------------------------------------------------------------------------------

/**
 * D118: asked once, right after a plan is made. "Yes" brings Android's own permission prompt (only then, D117); the
 * reminders are set on the phone, one after each stop. "No thanks" is the same size and style as "Yes".
 */
@Composable
fun ReminderAsk(model: AppModel) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val ask = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        scope.launch { model.answerReminders(true, granted) }
    }
    Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface)
        .border(1.dp, Theme.outline, RoundedCornerShape(18.dp)).padding(18.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            Icon(Icons.Outlined.Notifications, null, tint = Theme.accent, modifier = Modifier.padding(top = 3.dp).size(20.dp))
            Text("A nudge to rate each stop after you leave?", style = Theme.title3)
        }
        Text("One tap each, on the day. Your ratings are what make the next plan better. Set on your phone; nothing else is sent.",
            style = Theme.subheadline.copy(color = Theme.muted))
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            SecondaryButton("Yes, nudge me", Modifier.weight(1f)) {
                val enabled = NotificationManagerCompat.from(context).areNotificationsEnabled()
                if (Build.VERSION.SDK_INT >= 33 && !enabled) ask.launch(Manifest.permission.POST_NOTIFICATIONS)
                else scope.launch { model.answerReminders(true, enabled) }
            }
            SecondaryButton("No thanks", Modifier.weight(1f)) { scope.launch { model.answerReminders(false, false) } }
        }
    }
}

/** Journey round 2: a day that ends early says so, with one tap to add a place. */
@Composable
fun FreeTimeRow(model: AppModel, from: String, to: String, canAdd: Boolean, add: () -> Unit) {
    Row(Modifier.surfaceCard(), verticalAlignment = Alignment.CenterVertically) {
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text("Free from $from until $to", style = Theme.body)
            Text("Rest, wander, or add one more place.", style = Theme.footnote)
        }
        if (canAdd) QuietButton(if (model.busy) "Adding…" else "Add a place", color = Theme.accent, enabled = !model.busy, onClick = add)
    }
}

/** Decision 3 (8 Oct): "Re-plan the rest of today": why, then the rest of the day from about ten minutes from now. */
@Composable
fun ReplanRestDialog(model: AppModel, onDismiss: () -> Unit) {
    val scope = rememberCoroutineScope()
    fun go(reason: String): () -> Unit = { scope.launch { model.replanRest(reason) } }
    ChoiceDialog("Re-plan the rest of today?",
        "From where you are, starting in about ten minutes, without the places you've done.",
        listOf("It's raining" to go("rain"), "A place is closed or too busy" to go("closed"),
            "I'm tired: fewer stops" to go("tired"), "Something else" to go("other")),
        cancel = "Keep my day", onDismiss = onDismiss)
}

/**
 * D123: "Yes, use my location" records the choice, then asks Android (only if it hasn't been allowed yet). The answer
 * comes back to Location.refresh.
 */
@Composable
fun rememberLocationAsk(model: AppModel): () -> Unit {
    val launcher = rememberLauncherForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { result ->
        model.location.refresh(deniedNow = result.values.none { it })
    }
    return {
        model.location.turnOn()
        if (!model.location.allowed) {
            launcher.launch(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION))
        }
    }
}
