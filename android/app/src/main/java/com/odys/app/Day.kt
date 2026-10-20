package com.odys.app

import androidx.compose.ui.unit.sp
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.draw.drawBehind
import androidx.compose.animation.core.tween
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.Crossfade
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.FlightTakeoff
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * D119: "Now", the screen for while you're out (app/Sources/DayViews.swift). Quiet on purpose: the stop you're at, "Enjoy
 * it. I'll stay quiet until you need me.", a slowly breathing arch, and what's next. "I'm done here" asks for the rating
 * (the visit is over, D110), then moves on. D123: with location on, how far the stop is, and the rating asked for once
 * they've left it. m176: a trip day's journeys at each end; at the end of a trip's day, "Preview tomorrow".
 * D130 (the arrival moment): on the way, the stop's way in and "I'm here"; once there (tapped, or seen by the phone),
 * the screen brightens once, like coming out of the station into the open, and shows what to notice. With Reduce
 * Motion on it only fades. The day's path sits under the way in.
 */
@Composable
fun NowView(model: AppModel) {
    val scope = rememberCoroutineScope()
    var rating by remember { mutableStateOf<Stop?>(null) }
    var showSafety by remember { mutableStateOf(false) }
    var card by remember { mutableStateOf<Stop?>(null) }
    var onTheWay by remember { mutableStateOf<Stop?>(null) }
    var replanning by remember { mutableStateOf(false) }
    var asked by remember { mutableStateOf(setOf<String>()) }
    val reduce = rememberReduceMotion()
    val glow = remember { Animatable(0f) }
    val stops = model.plan?.stops ?: emptyList()
    val i = minOf(model.nowIndex, stops.size)
    val tripDay = model.currentTripDay()?.second
    val next = model.nextTripDay()
    val date = model.plan?.date
    // journey round 2: "Start the day" on a plan for a later day is a look ahead: nothing is rated before the day
    val lookAhead = if (date != null && date > Dates.todayIso()) Dates.shortDay(date) else null
    val loc = model.location
    val context = LocalContext.current
    fun close() { model.showNow = false }

    fun advance() = model.advanceNow()

    fun done(stop: Stop) {
        if (stop.rateable && stop.momentId !in model.rated && lookAhead == null) rating = stop else advance()
    }

    fun arrive(stop: Stop, how: String) {
        if (stop.id in model.arrivedStops) return
        model.markArrived(stop)
        scope.launch { model.client.event("arrived", mapOf("how" to how)) }
        if (!reduce) scope.launch {
            glow.animateTo(0.6f, tween(260))
            glow.animateTo(0f, tween(1100, easing = Motion.settleEasing))
        }
    }

    fun skip(stop: Stop) {
        model.reminders.cancel(stop)
        scope.launch { model.client.event("stop_skipped", mapOf("moment" to stop.momentId)) }
        advance()
    }

    DisposableEffect(Unit) {
        loc.start()
        onDispose { loc.stop() }
    }
    // D123: seen at the stop (within 120 m), then about 250 m away: the visit is over, so the rating is asked for once
    LaunchedEffect(loc.here) {
        if (!loc.usable || i >= stops.size || rating != null) return@LaunchedEffect
        val stop = stops[i]
        val m = stop.pin?.let { loc.metres(it) } ?: return@LaunchedEffect
        if (m < 120) {
            arrive(stop, "location")
        } else if (m > 250 && stop.id in model.arrivedStops && stop.id !in asked && stop.rateable && stop.momentId !in model.rated) {
            asked = asked + stop.id
            rating = stop
            model.client.event("rating_on_leaving")
        }
    }

    FullSheet(model, ::close, color = Theme.calm) {
        val open = card
        if (open != null) {
            StopView(model, open) { card = null }
            return@FullSheet
        }
        Box(Modifier.fillMaxSize().skyBackground(Theme.calm)) {
        Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 28.dp)
            .padding(top = 40.dp, bottom = 12.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            if (i == 0 && tripDay != null) {   // m176: the trip's first journeys come before the first stop
                tripDay.journeys("arrive").forEach { JourneyCard(it) }
                tripDay.before?.let { before ->
                    SectionLabel("On the way · travelling light")
                    for (stop in before.stops) {
                        TripDayStop(stop)
                        if (stop.rateable && stop.momentId !in model.rated) {
                            QuietButton("Been there? How was it?", color = Theme.accent) { onTheWay = stop }
                        }
                    }
                }
                tripDay.journeys("to_stay").forEach { JourneyCard(it) }
            }
            if (i < stops.size) {
                val stop = stops[i]
                val pin = stop.pin
                val m = if (loc.usable && pin != null) loc.metres(pin) else null
                val here = stop.id in model.arrivedStops || lookAhead != null
                androidx.compose.runtime.key(i) {   // D130: each new stop settles into place (a fade with Reduce Motion)
                    Column(Modifier.settle(), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                        Eyebrow(if (here) "Now" else "Next · around ${stop.arrive}")
                        Text(stop.title, style = Theme.hero, maxLines = 4, overflow = TextOverflow.Ellipsis,
                            modifier = Modifier.clickable(role = Role.Button) { card = stop }
                                .semantics { contentDescription = "${stop.title}. Opens the stop's card" })
                    }
                }
                if (m != null) {   // D123: from the phone's location, never sent
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        Icon(Icons.Filled.LocationOn, null, tint = Theme.accent, modifier = Modifier.size(16.dp))
                        Text(if (m < 120 || (here && m < 250)) "You're here" else Location.walkText(m),
                            style = Theme.subheadline.copy(color = Theme.accent))
                    }
                }
                Crossfade(here, animationSpec = tween(if (reduce) 200 else 450, easing = Motion.settleEasing), label = "arrival") { there ->
                    if (!there) {
                        // D130: on the way, how you arrive is part of the moment
                        Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                            val steps = stop.approachSteps.orEmpty()
                            if (steps.isNotEmpty() || stop.approach.isNotEmpty() || stop.travelText.isNotEmpty()) {
                                Column(Modifier.surfaceCard(padding = 18.dp, radius = 20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                                    SectionLabel("The way in")
                                    if (steps.isNotEmpty()) WayIn(steps, stop.reveal == true)
                                    else Text(stop.approach.ifEmpty { stop.travelText }, style = Theme.body.copy(color = Theme.inkSoft))
                                }
                            }
                            DayPath(stops, current = i, height = 120.dp)
                        }
                    } else {
                        Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                            if (stop.what.isNotEmpty() && lookAhead == null) Text(stop.what, style = Theme.italic(21.sp, Theme.ink))
                            Text(lookAhead?.let { "A look ahead: this day is $it. Ratings open on the day." }
                                ?: "Enjoy it. I'll stay quiet until you need me.", style = Theme.body.copy(color = Theme.inkSoft))
                            Box(Modifier.fillMaxWidth().padding(vertical = 8.dp), contentAlignment = Alignment.Center) { BreathingArch(showSun = true) }
                            val leave = tripDay?.journeys("leave")?.firstOrNull()
                            if (i + 1 < stops.size) {
                                NextUp(stops[i + 1])
                            } else if (leave != null) {   // journey round 2: the way home, ahead
                                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                    Icon(Icons.Filled.FlightTakeoff, null, tint = Theme.inkSoft, modifier = Modifier.size(18.dp))
                                    Text("After this: ${leave.title}", style = Theme.subheadline.copy(color = Theme.inkSoft))
                                }
                            }
                        }
                    }
                }
                if (!here) {
                    if (pin != null) {   // 20 Oct (round 2): the way there without opening the card; by Tube or bus when the leg is
                        SecondaryButton("Directions") { openUrl(context, directionsUrl(pin, stop.travelMode == "transit")) }
                    }
                    PrimaryButton("I'm here") { arrive(stop, "tap") }
                } else {
                    PrimaryButton("I'm done here") { done(stop) }
                }
                if (lookAhead == null) {   // journey round 2: a closed place or a long queue needn't be rated to move on
                    QuietButton("Didn't go? Skip this stop", Modifier.fillMaxWidth()) { skip(stop) }
                    if (model.lastRequest != null) {   // decision 3; never on the Test B plan
                        QuietButton("Plans changed? Re-plan the rest of today", Modifier.fillMaxWidth(), color = Theme.accent) {
                            replanning = true
                        }
                    }
                }
                // 19 Oct review: asked under the day's own buttons, so the stop and "I'm done here" come first
                if (!loc.asked) LocationAsk(model)
            } else {
                if (tripDay != null) {   // m176: the way back for bags, and on to the airport or station
                    (tripDay.journeys("back") + tripDay.journeys("leave")).forEach { JourneyCard(it) }
                }
                Eyebrow("That's the day")
                Text("Thanks for today.", style = Theme.hero)
                Text("Every stop you rated makes the next day fit you better.", style = Theme.body.copy(color = Theme.inkSoft))
                model.plan?.id?.let { id -> if (lookAhead == null) DayEndQuestions(model, id, Modifier.padding(top = 8.dp)) }
                Spacer(Modifier.height(12.dp))
                Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) { BreathingArch() }
                Spacer(Modifier.height(12.dp))
                if (next != null) {   // Abram's comment (8 Oct): look at tomorrow tonight
                    val (trip, index, _) = next
                    Text("Tomorrow is Day ${index + 1}. Have a look tonight: if you've made other plans, change its hours and I'll plan around them.",
                        style = Theme.subheadline.copy(color = Theme.inkSoft))
                    PrimaryButton(if (model.busy) "Planning…" else "Preview tomorrow: Day ${index + 1}", enabled = !model.busy) {
                        scope.launch {
                            model.planTripDayIfNeeded(trip.id, index)
                            close()
                            delay(300)
                            model.openTripDay(trip.id, index, "now")
                        }
                    }
                } else {
                    PrimaryButton("See the whole day") { close() }
                }
            }
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                if (i < stops.size || next != null) QuietButton("See the whole day") { close() }
                Spacer(Modifier.weight(1f))
                QuietButton("Help") { showSafety = true }
            }
        }
        // D130: the light opening out as you arrive; it never takes a tap
        Box(Modifier.fillMaxSize().drawBehind {
            if (glow.value > 0f) drawRect(Brush.radialGradient(listOf(Theme.amberLight.copy(alpha = glow.value), Color.Transparent),
                center = Offset(size.width / 2, size.height * 0.2f), radius = size.maxDimension))
        })
        }
    }
    rating?.let { stop -> RatingView(model, stop, onNext = { advance() }) { rating = null } }
    onTheWay?.let { stop -> RatingView(model, stop, planId = tripDay?.before?.id) { onTheWay = null } }
    if (showSafety) SafetyView(model) { showSafety = false }
    if (replanning) ReplanRestDialog(model) { replanning = false }
}

/** D123: asked once, the first time "Now" opens, with equal-weight answers; Android's own prompt comes only after a yes. */
@Composable
fun LocationAsk(model: AppModel) {
    val scope = rememberCoroutineScope()
    val ask = rememberLocationAsk(model)
    Column(Modifier.surfaceCard(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text("Use your location while you're out?", style = Theme.headline)
        Text("I'll show how far your next stop is, and ask how it felt once you've left. Your location stays on your phone.",
            style = Theme.subheadline.copy(color = Theme.inkSoft))
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            SecondaryButton("Yes, use it", Modifier.weight(1f)) {
                ask()
                scope.launch { model.client.event("location_on") }
            }
            SecondaryButton("No thanks", Modifier.weight(1f)) {
                model.location.turnOff()
                scope.launch { model.client.event("location_off") }
            }
        }
    }
}

/** "Next, around 14:34": the next stop and how to get there. */
@Composable
fun NextUp(stop: Stop) {
    Column(Modifier.fillMaxWidth().border(1.dp, Theme.outline, RoundedCornerShape(18.dp))
        .padding(horizontal = 18.dp, vertical = 16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text("Next, around ${stop.arrive}", style = Theme.subheadline.copy(color = Theme.muted))
        Text(stop.title, style = Theme.body)
        if (stop.travelText.isNotEmpty()) Text(stop.travelText, style = Theme.subheadline.copy(color = Theme.inkTertiary))
    }
}


/**
 * D127 (algorithm reviews): the product's second outcome, how worthwhile the money felt (CLAUDE.md), which nothing else
 * measured. Two taps, both optional, once the day is done.
 */
@Composable
fun DayEndQuestions(model: AppModel, planId: Int, modifier: Modifier = Modifier) {
    var answer by remember(planId) { mutableStateOf(model.dayFeedback(planId)) }
    fun set(new: DayFeedback) {
        answer = new
        model.answerDay(planId, new)
    }
    Column(modifier, verticalArrangement = Arrangement.spacedBy(22.dp)) {
        SurveyQuestion("Was today worth what you spent on it?") {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for ((key, label) in listOf("less" to "Not quite", "about_right" to "Yes", "more" to "More than that")) {
                    Chip(label, answer.worth == key, Modifier.weight(1f)) { set(answer.copy(worth = if (answer.worth == key) null else key)) }
                }
            }
        }
        SurveyQuestion("Would you do this day again?") {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for ((key, label) in listOf(true to "Yes", false to "No")) {
                    Chip(label, answer.again == key, Modifier.weight(1f)) { set(answer.copy(again = if (answer.again == key) null else key)) }
                }
            }
        }
    }
}
