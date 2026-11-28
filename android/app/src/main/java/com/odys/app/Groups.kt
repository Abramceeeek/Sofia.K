package com.odys.app

import android.content.Context
import android.content.Intent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Group
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch
import kotlinx.serialization.Serializable
import java.time.LocalDate
import java.time.format.TextStyle
import java.util.Locale

// m358 (Abram, 25 Nov: "test whether two or three people can actually create one together, contribute their
// individual preferences and produce something they all want to do"): a trip planned by friends, each from their own
// phone. As app/Sources/GroupViews.swift: the organiser starts it and sends the code; each friend joins with it and
// agrees first. Nobody's answers are shown to the others; a person is named only if they agreed. Friends only.

@Serializable
data class GroupMemberInfo(val label: String, val you: Boolean, val named: Boolean)

@Serializable
data class GroupSettings(val startDate: String, val nights: Int, val perDay: Int)

@Serializable
data class GroupTripInfo(
    val id: Int,
    val settings: GroupSettings,
    val you: String,
    val code: String? = null,
    val members: List<GroupMemberInfo> = emptyList(),
)

@Serializable
data class GroupList(val groups: List<GroupTripInfo> = emptyList())

@Serializable
data class GroupStop(val id: String, val title: String, val why: String? = null)

@Serializable
data class GroupPlanOut(
    val group: GroupTripInfo,
    val method: String,
    val days: List<List<GroupStop>> = emptyList(),
    val notes: List<String> = emptyList(),
    val yourShare: String? = null,
)

@Serializable
data class GroupCreateRequest(val startDate: String, val nights: Int, val perDay: Int, val consent: Boolean,
                              val sharePreferences: Boolean)

@Serializable
data class GroupJoinRequest(val code: String, val consent: Boolean, val sharePreferences: Boolean)

object GroupText {
    fun whenText(s: GroupSettings): String {
        val d = runCatching { LocalDate.parse(s.startDate) }.getOrNull()
        val date = d?.let {
            "${it.dayOfWeek.getDisplayName(TextStyle.FULL, Locale.UK)} ${it.dayOfMonth} ${it.month.getDisplayName(TextStyle.FULL, Locale.UK)}"
        } ?: s.startDate
        val days = s.nights + 1
        return "London from $date, $days day${if (days == 1) "" else "s"}"
    }

    fun who(g: GroupTripInfo): String =
        if (g.members.size == 1) "Just you so far: send the code to a friend" else "${g.members.size} of you · you're ${g.you}"

    const val CONSENT = "My answers in ODYS (the places I swiped and the days I chose) help plan this shared trip. The others never see my answers, only why each stop is there."
    const val NAMED = "The plan may name me (by my member letter) when it says who a stop suits. Otherwise I'm counted, never named."
}

/** "Planning with friends?" on the home screen. */
@Composable
fun GroupInviteRow(onClick: () -> Unit) {
    Row(Modifier.fillMaxWidth().pressable(onClick = onClick).surfaceCard(padding = 18.dp),
        horizontalArrangement = Arrangement.spacedBy(14.dp)) {
        Icon(Icons.Filled.Group, null, tint = Theme.accent, modifier = Modifier.padding(top = 2.dp))
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text("Planning with friends?", style = Theme.title3)
            Text("Start a shared trip and send the code, or join a friend's. Each of you answers on your own phone.",
                style = Theme.subheadline.copy(color = Theme.muted))
        }
    }
}

/** The shared trips this phone is in, and starting or joining one. `demo` is for the screen tests only. */
@Composable
fun GroupTripsScreen(model: AppModel, onClose: () -> Unit, demo: String? = null) {
    var groups by remember { mutableStateOf(model.groupsDemo?.groups ?: emptyList()) }
    var loaded by remember { mutableStateOf(model.groupsDemo != null) }
    var mode by remember { mutableStateOf(if (demo == "join") "join" else null as String?) }
    var open by remember { mutableStateOf(if (demo == "plan" || demo == "trip") model.groupsDemo?.groups?.firstOrNull() else null) }
    LaunchedEffect(Unit) {
        if (!loaded) {
            runCatching { model.client.groups() }.getOrNull()?.let { groups = it.groups }
            loaded = true
        }
    }
    FullSheet(model, onClose) {
        Column(Modifier.fillMaxSize()) {
            val g = open
            if (g != null) {
                SheetBar(onClose = onClose, leading = { QuietButton("‹ Back", color = Theme.accent) { open = null } })
                GroupTripPage(model, g, autoPlan = demo == "plan") { left -> groups = groups.filter { it.id != left }; open = null }
            } else {
            SheetBar(onClose = onClose)
            ScrollPage(spacing = 18, top = 0, bottom = 32) {
                Eyebrow("With friends")
                PageTitle("Plan a trip together")
                Text("Each of you answers on your own phone. The days come from all of your answers: nobody sees anyone else's, and a place one of you said no to is left out.",
                    style = Theme.body.copy(color = Theme.inkSoft))
                when (mode) {
                    "start" -> GroupStartForm(model) { created -> groups = listOf(created) + groups; mode = null; open = created }
                    "join" -> GroupJoinForm(model) { joined ->
                        if (groups.none { it.id == joined.id }) groups = listOf(joined) + groups
                        mode = null; open = joined
                    }
                    else -> {
                        PrimaryButton("Start a shared trip") { mode = "start" }
                        SecondaryButton("Join with a code") { mode = "join" }
                    }
                }
                if (groups.isNotEmpty()) {
                    SectionLabel("Your shared trips")
                    for (t in groups) {
                        Row(Modifier.fillMaxWidth().pressable(onClick = { open = t }).surfaceCard(padding = 18.dp, radius = 20.dp),
                            verticalAlignment = Alignment.CenterVertically) {
                            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                Text(GroupText.whenText(t.settings), style = Theme.headline)
                                Text(GroupText.who(t), style = Theme.subheadline.copy(color = Theme.inkTertiary))
                            }
                            Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = Theme.muted)
                        }
                    }
                } else if (loaded && mode == null) {
                    Text("No shared trips yet.", style = Theme.subheadline.copy(color = Theme.muted))
                }
                Text("Friends only: there's no way to find or match strangers, and no money changes hands in ODYS.",
                    style = Theme.footnote)
            }
            }
        }
    }
}

@Composable
private fun GroupStartForm(model: AppModel, onDone: (GroupTripInfo) -> Unit) {
    val scope = rememberCoroutineScope()
    var start by remember { mutableStateOf(LocalDate.now().plusDays(7)) }
    var nights by remember { mutableIntStateOf(1) }
    var perDay by remember { mutableIntStateOf(3) }
    var agreed by remember { mutableStateOf(false) }
    var named by remember { mutableStateOf(false) }
    var busy by remember { mutableStateOf(false) }
    var failed by remember { mutableStateOf(false) }
    Column(Modifier.fillMaxWidth().surfaceCard(padding = 18.dp, radius = 20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        val first = "${start.dayOfWeek.getDisplayName(TextStyle.SHORT, Locale.UK)} ${start.dayOfMonth} ${start.month.getDisplayName(TextStyle.SHORT, Locale.UK)}"
        Stepper("First day", first, atMin = !start.isAfter(LocalDate.now()), atMax = false,
            minusLabel = "A day earlier", plusLabel = "A day later",
            minus = { if (start.isAfter(LocalDate.now())) start = start.minusDays(1) }, plus = { start = start.plusDays(1) })
        Stepper("Days", "${nights + 1}", atMin = nights == 0, atMax = nights == 6, minusLabel = "One day fewer",
            plusLabel = "One day more", minus = { if (nights > 0) nights-- }, plus = { if (nights < 6) nights++ })
        Stepper("Places a day", "$perDay", atMin = perDay == 1, atMax = perDay == 5, minusLabel = "One place fewer",
            plusLabel = "One place more", minus = { if (perDay > 1) perDay-- }, plus = { if (perDay < 5) perDay++ })
        CheckRow(GroupText.CONSENT, agreed) { agreed = it }
        CheckRow(GroupText.NAMED, named) { named = it }
        if (failed) Text("That didn't go through. Check your signal, then try again.", style = Theme.footnote.copy(color = Theme.warnInk))
        PrimaryButton(if (busy) "Starting…" else "Start the trip", enabled = agreed && !busy) {
            scope.launch {
                busy = true
                failed = false
                val out = runCatching {
                    model.client.createGroup(GroupCreateRequest(start.toString(), nights, perDay, true, named))
                }.getOrNull()
                busy = false
                if (out == null) failed = true else onDone(out)
            }
        }
    }
}

@Composable
private fun GroupJoinForm(model: AppModel, onDone: (GroupTripInfo) -> Unit) {
    val scope = rememberCoroutineScope()
    var code by remember { mutableStateOf("") }
    var agreed by remember { mutableStateOf(false) }
    var named by remember { mutableStateOf(false) }
    var busy by remember { mutableStateOf(false) }
    var message by remember { mutableStateOf<String?>(null) }
    val clean = code.uppercase().filter { it.isLetterOrDigit() }.take(16)
    Column(Modifier.fillMaxWidth().surfaceCard(padding = 18.dp, radius = 20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        OutlinedTextField(code, { code = it.uppercase() }, singleLine = true, label = { Text("The code your friend sent") },
            keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.Characters, autoCorrect = false),
            colors = odysFieldColors(), modifier = Modifier.fillMaxWidth())
        CheckRow(GroupText.CONSENT, agreed) { agreed = it }
        CheckRow(GroupText.NAMED, named) { named = it }
        message?.let { Text(it, style = Theme.footnote.copy(color = Theme.warnInk)) }
        PrimaryButton(if (busy) "Joining…" else "Join the trip", enabled = agreed && !busy && clean.length >= 6) {
            scope.launch {
                busy = true
                message = null
                try {
                    onDone(model.client.joinGroup(GroupJoinRequest(clean, true, named)))
                } catch (e: BrainError) {
                    message = when (e.code) {
                        404 -> "No shared trip has that code. Check it with your friend."
                        409 -> "That trip is full: a shared trip holds six people."
                        else -> "That didn't go through. Check your signal, then try again."
                    }
                } catch (e: Exception) {
                    message = "That didn't go through. Check your signal, then try again."
                }
                busy = false
            }
        }
    }
}

/** One shared trip: who's in (by letter), the code to send, the days once two of you are in, and leaving. */
@Composable
private fun GroupTripPage(model: AppModel, group: GroupTripInfo, autoPlan: Boolean, onLeft: (Int) -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var plan by remember { mutableStateOf<GroupPlanOut?>(null) }
    var busy by remember { mutableStateOf(false) }
    var failed by remember { mutableStateOf(false) }
    var confirmLeave by remember { mutableStateOf(false) }
    val organiser = group.code != null
    val current = plan?.group ?: group
    suspend fun makePlan() {
        busy = true
        failed = false
        val out = model.groupPlanDemo ?: runCatching { model.client.planGroup(group.id) }.getOrNull()
        busy = false
        if (out == null) failed = true else plan = out
    }
    LaunchedEffect(Unit) { if (autoPlan && plan == null) makePlan() }
    ScrollPage(spacing = 18, top = 0, bottom = 32) {
        Eyebrow("Shared trip")
        PageTitle(GroupText.whenText(current.settings))
        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            SectionLabel("Who's in")
            for (m in current.members) {
                Text(m.label + (if (m.you) " (you)" else "") + (if (m.named) "" else " · counted, not named"), style = Theme.body)
            }
        }
        current.code?.let { code ->
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                SectionLabel("Send this code to your friends")
                Text(code, style = Theme.h1.copy(fontFamily = FontFamily.Monospace, fontWeight = FontWeight.SemiBold, fontSize = 28.sp))
                QuietButton("Send the code", color = Theme.accent) { shareCode(context, code) }
            }
        }
        if (current.members.size < 2) {
            Text("The days are planned once a friend has joined.", style = Theme.body.copy(color = Theme.muted))
        } else {
            PrimaryButton(if (busy) "Planning…" else if (plan == null) "Plan our days" else "Plan again with everyone's latest answers",
                enabled = !busy) { scope.launch { makePlan() } }
        }
        if (failed) Text("The days couldn't be planned just now. Check your signal, then try again.",
            style = Theme.footnote.copy(color = Theme.warnInk))
        plan?.let { p ->
            p.days.forEachIndexed { i, day ->
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    SectionLabel("Day ${i + 1}")
                    for (st in day) {
                        Column(Modifier.fillMaxWidth().surfaceCard(padding = 16.dp, radius = 18.dp),
                            verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text(st.title, style = Theme.serif(19.sp))
                            st.why?.let { Text(it, style = Theme.subheadline.copy(color = Theme.inkTertiary)) }
                        }
                    }
                }
            }
            p.yourShare?.let { Text("For you: $it.", style = Theme.subheadline) }
            for (n in p.notes) Text(n, style = Theme.footnote)
            Text("A shared plan of places, without times or routes yet: plan each day out from it on your own phone.",
                style = Theme.footnote)
        }
        QuietButton(if (organiser) "End this shared trip for everyone" else "Leave this shared trip") { confirmLeave = true }
    }
    if (confirmLeave) {
        AlertDialog(
            onDismissRequest = { confirmLeave = false },
            title = { Text(if (organiser) "End this shared trip for everyone?" else "Leave this shared trip?", style = Theme.headline) },
            text = {
                Text(if (organiser) "Everyone's place in it is removed. Your own answers stay yours."
                     else "Your part in it is removed. Your own answers stay yours.", style = Theme.subheadline.copy(color = Theme.inkSoft))
            },
            confirmButton = {
                TextButton({
                    confirmLeave = false
                    scope.launch { runCatching { model.client.leaveGroup(group.id) }; onLeft(group.id) }
                }) { Text(if (organiser) "End it" else "Leave", color = Theme.warnInk) }
            },
            dismissButton = { TextButton({ confirmLeave = false }) { Text("Cancel", color = Theme.inkSoft) } },
            containerColor = Theme.surfaceHigh,
        )
    }
}

private fun shareCode(context: Context, code: String) {
    val send = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_TEXT,
            "Join my trip on ODYS with the code $code: open ODYS, then \"Planning with friends?\" and \"Join with a code\".")
    }
    context.startActivity(Intent.createChooser(send, "Send the code").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
}
