package com.odys.app

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.WifiOff
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import java.time.LocalDate
import java.time.temporal.ChronoUnit

/**
 * m228 (Abram, 9 Nov): what's saved on this phone for the day, in order: today's itinerary, where you're staying, the
 * journey, emergency help. Built on the phone from what it already keeps (the plan and the trip), never fetched, so it
 * works with no signal. Each item says where it came from, when it was saved, whether it's current, needs checking, has
 * expired or is past, and the one thing to do. Nothing here claims to be live. The rules are the Brain's tested
 * reference (brain/src/brain/offline.py), the same on the iPhone.
 */
data class OfflineItem(
    val title: String,
    val lines: List<String>,
    val source: String,
    val saved: String?,
    val status: Status,
    val action: String? = null,
    val missing: List<String> = emptyList(),
) {
    enum class Status { Current, Check, Expired, Past }
}

data class OfflineSection(val id: String, val title: String, val items: List<OfflineItem>)

object OfflinePack {
    const val CARD_CHECK_DAYS = 90L   // GUESS (offline.py): a card's facts older than this say "check on the day"
    const val PLAN_STALE_DAYS = 7L    // GUESS: a day planned this long before its date may have changed travel times

    /** The same words as Help & safety, which is in the app and works offline. */
    val emergency = listOf(
        OfflineItem("Emergency", listOf("If you or someone else is in danger or hurt, call 999 now."),
            "Help & safety, in the app", null, OfflineItem.Status.Current),
        OfflineItem("Urgent medical help", listOf("Urgent medical help that isn't an emergency: call NHS 111. You can ask for an interpreter."),
            "Help & safety, in the app", null, OfflineItem.Status.Current),
        OfflineItem("Someone to talk to", listOf("Samaritans answer free, day or night, on 116 123."),
            "Help & safety, in the app", null, OfflineItem.Status.Current),
    )

    fun build(plan: Plan?, trip: Trip?, today: LocalDate): List<OfflineSection> = listOf(
        OfflineSection("itinerary", "Today", listOf(itinerary(plan, today))),
        OfflineSection("stay", "Where you're staying",
            if (trip != null && trip.needStay) listOf(choice("stay", trip.stay, trip, today)) else emptyList()),
        OfflineSection("journey", "Your journey",
            if (trip != null && trip.needFlight) listOf(choice("flight", trip.flight, trip, today)) else emptyList()),
        OfflineSection("emergency", "Emergency help in the UK", emergency),   // m236: the UK's numbers only (m234)
    )

    fun itinerary(plan: Plan?, today: LocalDate): OfflineItem {
        if (plan == null) return OfflineItem("No day saved", emptyList(), "This phone", null, OfflineItem.Status.Current,
            missing = listOf("a plan for today"))
        val day = Dates.parse(plan.date)
        val lines = plan.stops.map { "${it.arrive}–${it.depart} ${it.title}" }.toMutableList()
        val missing = mutableListOf<String>()
        for (s in plan.stops.filter { it.rateable }) {
            val checked = Dates.parse(s.checked)
            if (checked == null) missing += "when ${s.title}'s facts were checked"
            else if (day != null && ChronoUnit.DAYS.between(checked, day) > CARD_CHECK_DAYS)
                lines += "${s.title}: facts checked ${Dates.dayMonth(checked)}; check opening hours on the day."
            s.bookAhead?.takeIf { it.isNotBlank() }?.let { lines += "${s.title}: $it" }
        }
        val made = Dates.parse(plan.createdAt)
        var status = if (day != null && day < today) OfflineItem.Status.Past else OfflineItem.Status.Current
        var action: String? = null
        if (status == OfflineItem.Status.Current && made != null && day != null && ChronoUnit.DAYS.between(made, day) > PLAN_STALE_DAYS) {
            status = OfflineItem.Status.Check
            action = "Planned on ${Dates.dayMonth(made)}: travel times may have changed. Plan this day again when you have signal."
        }
        return OfflineItem(plan.title ?: "Your day", lines, "Your plan", plan.createdAt, status, action, missing)
    }

    fun choice(kind: String, c: TripChoice?, trip: Trip, today: LocalDate): OfflineItem {
        val label = if (kind == "stay") "Where you're staying" else "Your journey"
        if (c == null) return OfflineItem(label, emptyList(), "Your trip", null, OfflineItem.Status.Current,
            missing = listOf(if (kind == "stay") "no stay chosen" else "no flight chosen"))
        val lines = mutableListOf(c.title, "${c.money}, as found on ${c.provider}")
        val missing = mutableListOf<String>()
        if (kind == "stay") {
            lines += "The address isn't saved on this phone."
        } else {
            c.arriveTime?.let { lines += "Lands $it" + (c.arrivePlace?.let { p -> " ($p)" } ?: "") } ?: run { missing += "when the flight lands" }
            c.leaveTime?.let { lines += "Flight home leaves $it" + (c.leavePlace?.let { p -> " ($p)" } ?: "") } ?: run { missing += "when the flight home leaves" }
        }
        val ended = today > trip.endDate
        var status = if (ended) OfflineItem.Status.Expired else OfflineItem.Status.Current
        val action: String
        when {
            c.sample == true -> { status = OfflineItem.Status.Check; action = "A sample price, made up for testing: not a real booking." }
            c.forStart != null && c.forStart != trip.start -> {
                status = OfflineItem.Status.Check; action = "Chosen for other dates: check it on ${c.provider}, or choose again."
            }
            !c.booked -> {
                if (status == OfflineItem.Status.Current) status = OfflineItem.Status.Check
                action = "Not marked as booked: check with ${c.provider}."
            }
            else -> action = if (kind == "flight") "Times can change: check with the airline on the day."
                             else "The address and check-in details are in ${c.provider}'s confirmation."
        }
        if (ended && status == OfflineItem.Status.Check) status = OfflineItem.Status.Expired
        return OfflineItem(label, lines, "Found on ${c.provider}", c.forStart, status, action, missing)
    }

    fun word(s: OfflineItem.Status) = when (s) {
        OfflineItem.Status.Current -> "Saved"
        OfflineItem.Status.Check -> "Check"
        OfflineItem.Status.Expired -> "Expired"
        OfflineItem.Status.Past -> "Past"
    }

    /** "From your plan · saved 8 Nov": a date, never shown as more recent than it is. */
    fun provenance(i: OfflineItem): String = Dates.parse(i.saved)?.let { "${i.source} · saved ${Dates.dayMonth(it)}" } ?: i.source
}

/**
 * m228: whether the phone has a network. Only a hint (a network can exist without a working connection), so the
 * screens say "No signal" only to point at what's saved, never "this is live".
 */
class Connectivity(context: Context?) {
    var online by mutableStateOf(true)
    private var pinned = false   // screenshots and tests: a state the real network can't change

    fun pin(value: Boolean) { pinned = true; online = value }

    /** What the network callback reports, also used by tests to play the transitions. */
    fun report(up: Boolean) { if (!pinned) online = up }

    init {
        val cm = context?.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
        if (cm != null) runCatching {
            online = cm.getNetworkCapabilities(cm.activeNetwork)?.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) ?: false
            cm.registerDefaultNetworkCallback(object : ConnectivityManager.NetworkCallback() {
                override fun onAvailable(network: Network) = report(true)
                override fun onLost(network: Network) = report(false)
            })
        }
    }
}

/** m228: the "No signal" note on "Now". */
@Composable
fun OfflineBanner(onOpen: () -> Unit) {
    Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(16.dp)).background(Theme.surface)
        .clickable(onClick = onOpen).padding(14.dp)
        .clearAndSetSemantics { contentDescription = "No signal. Your day, stay and journey are saved on this phone. Opens what's saved." },
        verticalAlignment = Alignment.Top) {
        Icon(Icons.Filled.WifiOff, contentDescription = null, tint = Theme.amberDeep)
        Spacer(Modifier.width(10.dp))
        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text("No signal", style = Theme.subheadline.copy(fontWeight = FontWeight.SemiBold))
            Text("Your day, stay and journey are saved on this phone. Nothing shown is live.", style = Theme.footnote.copy(color = Theme.inkSoft))
            Text("See what's saved", style = Theme.footnote.copy(color = Theme.accent, fontWeight = FontWeight.SemiBold))
        }
    }
}

/** m228: what's saved on this phone, from "Now". In ODYS's look: the sky behind, quiet cards, amber only for "Check". */
@Composable
fun OfflineView(model: AppModel, onClose: () -> Unit) {
    val sections = OfflinePack.build(model.plan, model.tripForToday, Dates.today())
    FullSheet(model, onClose, color = Theme.calm) {
        Box(Modifier.fillMaxSize().skyBackground(Theme.calm)) {
            Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 24.dp, vertical = 28.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)) {
                BackLink("Back to now", onClick = onClose)
                Eyebrow(if (model.connectivity.online) "Saved on this phone" else "No signal")
                Text("What's saved on this phone", style = Theme.title)
                Text(if (model.connectivity.online) "Kept here in case you lose signal. None of it is live: check anything marked “Check”."
                     else "You're offline, so this is what was saved, not live information. Check anything marked “Check” when you have signal.",
                    style = Theme.subheadline.copy(color = Theme.inkSoft))
                for (section in sections.filter { it.items.isNotEmpty() }) {
                    SectionLabel(section.title, Modifier.padding(top = 4.dp))
                    for (item in section.items) OfflineItemCard(item)
                }
            }
        }
    }
}

@Composable
fun OfflineItemCard(item: OfflineItem) {
    val check = item.status == OfflineItem.Status.Check
    Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(item.title, style = Theme.headline, modifier = Modifier.weight(1f))
            Text(OfflinePack.word(item.status), style = Theme.caption.copy(color = if (check) Theme.amberDeep else Theme.muted,
                fontWeight = FontWeight.SemiBold),
                modifier = Modifier.clip(RoundedCornerShape(50)).background(if (check) Theme.savedBg else Theme.surfaceHigh)
                    .padding(horizontal = 8.dp, vertical = 3.dp))
        }
        for (line in item.lines) Text(line, style = Theme.subheadline.copy(color = Theme.inkSoft))
        item.action?.let { Text(it, style = Theme.subheadline.copy(fontWeight = FontWeight.SemiBold)) }
        for (m in item.missing) Text("Not saved: $m", style = Theme.footnote.copy(color = Theme.muted))
        Text(OfflinePack.provenance(item), style = Theme.footnote.copy(color = Theme.muted))
    }
}
