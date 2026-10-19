package com.odys.app

import android.content.Context
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.EaseIn
import androidx.compose.animation.core.EaseOut
import androidx.compose.animation.core.tween
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.List
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.PanTool
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.semantics.Role
import androidx.compose.foundation.selection.toggleable
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay

/** The non-personal example day shown before consent (D112), bundled so it needs no network. */
object ExampleDay {
    private var cached: Plan? = null
    fun plan(context: Context): Plan? {
        cached?.let { return it }
        return runCatching {
            val text = context.assets.open("demo/example_day.json").bufferedReader().use { it.readText() }
            BrainJson.decodeFromString(Plan.serializer(), text)
        }.getOrNull().also { cached = it }
    }
}

private var welcomePlayed = false   // once per launch

/**
 * Screen 1 (D119): the arch lights up, the light spills, then the words settle in. About a second; a tap skips it.
 * A person, not a brand: Abram's card says who runs the test.
 */
@Composable
fun WelcomeView(model: AppModel) {
    val reduce = rememberReduceMotion()
    val light = remember { Animatable(if (welcomePlayed) 1f else 0f) }
    val pool = remember { Animatable(if (welcomePlayed) 1f else 0f) }
    val settled = remember { Animatable(if (welcomePlayed) 1f else 0f) }
    var askCode by remember { mutableStateOf(false) }
    var savedCode by remember { mutableStateOf(model.prefs.string("testerCode") ?: "") }
    var skip by remember { mutableStateOf(false) }

    LaunchedEffect(skip) {
        if (welcomePlayed || reduce || skip) {
            welcomePlayed = true
            light.snapTo(1f); pool.snapTo(1f); settled.snapTo(1f)
            return@LaunchedEffect
        }
        welcomePlayed = true
        delay(200)
        light.animateTo(1f, tween(600, easing = EaseIn))            // Reveal: the light rises in the arch…
        pool.animateTo(1f, tween(350, easing = EaseOut))            // …then spills out in front
        delay(100)
        settled.animateTo(1f, Motion.settle())
    }

    Box(Modifier.screen()) {
        PageWithBottom(
            Modifier.statusBarsPadding().navigationBarsPadding(),
            spacing = 0,
            bottom = {
                Column(Modifier.graphicsLayer { alpha = settled.value }) {
                    PrimaryButton("Show me an example day", enabled = settled.value > 0.5f) { model.route = Route.Example }
                    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                        QuietButton("Skip the example") { model.route = Route.Consent }
                        Spacer(Modifier.weight(1f))
                        // Build 2: an optional code from whoever invited them; it says where they heard of the test
                        QuietButton(if (savedCode.isEmpty()) "Got a tester code?" else "Code: $savedCode") { askCode = true }
                    }
                }
            },
        ) {
            Box(Modifier.fillMaxWidth().padding(top = 36.dp), contentAlignment = Alignment.Center) {
                ArchLogo(Modifier.width(180.dp).height(220.dp), light = light.value, pool = pool.value)
            }
            Box(Modifier.fillMaxWidth().padding(top = 18.dp, bottom = 36.dp), contentAlignment = Alignment.Center) {
                Wordmark()
            }
            Column(
                Modifier.graphicsLayer { alpha = settled.value; translationY = (1 - settled.value) * 10.dp.toPx() },
                verticalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                Text("Days out that fit you.", style = Theme.display, modifier = Modifier.semantics { heading() })
                Text("Tell me how you want a day to feel. I'll plan real moments around it, including how you arrive.",
                    style = Theme.body.copy(color = Theme.inkSoft))
                AbramCard(Modifier.padding(top = 14.dp))
            }
        }
        if (settled.value < 0.5f) {
            Box(Modifier.fillMaxSize().clickable(onClickLabel = "Skip") { skip = true })
        }
    }
    if (askCode) {
        TesterCodeDialog(savedCode, onDismiss = { askCode = false }) { code ->
            savedCode = code
            model.prefs.set("testerCode", code.ifEmpty { null })
        }
    }
}

/** "If someone gave you a code, type it here." */
@Composable
fun TesterCodeDialog(initial: String, onDismiss: () -> Unit, onSave: (String) -> Unit) {
    var code by remember { mutableStateOf(initial) }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Tester code", style = Theme.headline) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("If someone gave you a code, type it here. It only says where you heard about the test, never who you are.",
                    style = Theme.subheadline.copy(color = Theme.inkSoft))
                OutlinedTextField(
                    code, { code = it.uppercase() }, singleLine = true, label = { Text("Code") },
                    keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.Characters, autoCorrect = false),
                    colors = odysFieldColors(),
                )
            }
        },
        confirmButton = { TextButton({ onSave(code.trim()); onDismiss() }) { Text("Save", color = Theme.accent) } },
        dismissButton = { TextButton(onDismiss) { Text("Cancel", color = Theme.inkSoft) } },
        containerColor = Theme.surfaceHigh,
    )
}

@Composable
fun odysFieldColors() = OutlinedTextFieldDefaults.colors(
    focusedTextColor = Theme.ink, unfocusedTextColor = Theme.ink, cursorColor = Theme.accent,
    focusedBorderColor = Theme.accent, unfocusedBorderColor = Theme.outlineStrong,
    focusedLabelColor = Theme.accent, unfocusedLabelColor = Theme.muted,
    focusedPlaceholderColor = Theme.muted, unfocusedPlaceholderColor = Theme.muted,
)

/** "This is a research test, run by one person": who's behind it, before any question (D110). */
@Composable
fun AbramCard(modifier: Modifier = Modifier) {
    Row(
        modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface).padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        AbramAvatar()
        Text("This is a research test, run by one person: Abram, in London.",
            style = Theme.subheadline.copy(color = Theme.inkSoft), modifier = Modifier.weight(1f))
    }
}

/**
 * Screen 2 (D112, D115): what a plan looks like, before any question. Not personal: built from the average of all
 * answers and bundled with the app. One stop's card is shown in full.
 */
@Composable
fun ExampleDayView(model: AppModel) {
    val context = LocalContext.current
    val plan = remember { ExampleDay.plan(context) }
    val featured = plan?.stops?.firstOrNull { it.rateable && it.card != null }
    BackTo { model.route = Route.Welcome }
    PageWithBottom(
        Modifier.statusBarsPadding().navigationBarsPadding(),
        bottom = {
            PrimaryButton("Make one that fits me") { model.route = Route.Consent }
            // D119: honest about the length (14 or so questions)
            Text("About 3 minutes. No account or name needed.", style = Theme.subheadline.copy(color = Theme.muted),
                modifier = Modifier.fillMaxWidth().padding(top = 6.dp), textAlign = androidx.compose.ui.text.style.TextAlign.Center)
        },
    ) {
        BackLink { model.route = Route.Welcome }
        Column(Modifier.settle(0), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Eyebrow("An example day")
            PageTitle(plan?.title ?: "An example day", style = Theme.serif(32.sp))
            plan?.feelLine?.takeIf { it.isNotEmpty() }?.let {
                Text(it, style = Theme.italic(20.sp, Theme.inkSoft))
            }
        }
        if (featured != null) FeaturedStop(featured, Modifier.settle(1))
        if (plan != null) {
            Column(Modifier.settle(2)) {
                for (s in plan.stops) {
                    Row(Modifier.fillMaxWidth().padding(vertical = 12.dp), verticalAlignment = Alignment.Top,
                        horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                        Text(s.arrive, style = Theme.subheadline.copy(color = Theme.muted), modifier = Modifier.width(52.dp))
                        Text(s.title, style = Theme.body, modifier = Modifier.weight(1f))
                        Text(s.word, style = Theme.italic(16.sp))
                    }
                    Box(Modifier.fillMaxWidth().height(1.dp).background(Theme.hairline))
                }
            }
            Text("This is what a plan looks like. It isn't planned for you: yours is built from your answers, and from how you rate each stop.",
                style = Theme.subheadline.copy(color = Theme.muted))
        }
        if (featured != null) {
            Column(Modifier.padding(top = 8.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                Eyebrow("Every stop comes with a card like this")
                MomentCardContent(model, featured, showWhy = false)
            }
        }
    }
}

/** The example day's first card stop, as a picture with its time and kind of moment. */
@Composable
fun FeaturedStop(stop: Stop, modifier: Modifier = Modifier) {
    Column(modifier.fillMaxWidth().clip(RoundedCornerShape(22.dp)).background(Theme.surface)) {
        Box(Modifier.fillMaxWidth().height(190.dp)) {
            MomentImage(stop.momentId, stop.feelWord, Modifier.fillMaxSize())
            Column(
                Modifier.align(Alignment.BottomStart).fillMaxWidth()
                    .background(Brush.verticalGradient(listOf(Color.Transparent, Theme.background.copy(alpha = 0.9f))))
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(2.dp),
            ) {
                Text(stop.title, style = Theme.serif(24.sp), maxLines = 3, overflow = TextOverflow.Ellipsis)
                Text("${stop.arrive} · ${stop.word.lowercase()}", style = Theme.subheadline.copy(color = Theme.inkSoft))
            }
        }
        if (stop.what.isNotEmpty()) {
            Text(stop.what, style = Theme.subheadline.copy(color = Theme.inkSoft), modifier = Modifier.padding(16.dp))
        }
    }
}

/**
 * Screen 3: consent (D109, D110). A short plain-English summary, the two required choices where they can't be missed,
 * and the details folded away. The 999 advice lives in Help & safety.
 */
@Composable
fun ConsentView(model: AppModel) {
    var adult by rememberSaveable { mutableStateOf(false) }
    var agree by rememberSaveable { mutableStateOf(false) }
    var showDetails by rememberSaveable { mutableStateOf(false) }
    var askCode by remember { mutableStateOf(false) }
    var code by remember { mutableStateOf(model.prefs.string("testerCode") ?: "") }
    val context = LocalContext.current
    val summary = listOf(
        Icons.Outlined.Person to "A research test run by Abram, one person in London. Nothing is sold.",
        Icons.AutoMirrored.Outlined.List to "A few quick questions and some places, then your plans: a day out, or a whole trip.",
        Icons.Outlined.Lock to "We keep your answers to plan your days and to test the idea. We don't ask for your name, email or phone number.",
        Icons.Outlined.PanTool to "Most questions can be skipped, and you can stop any time. \"Your data\" → Delete my data removes everything.",
    )
    BackTo { model.route = Route.Welcome }
    ScrollPage(Modifier.statusBarsPadding().navigationBarsPadding(), top = 16) {
        BackLink { model.route = Route.Welcome }
        Eyebrow("Before we start")
        PageTitle("A few things first")
        Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
            for ((icon, text) in summary) {
                Row(horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                    Icon(icon, null, tint = Theme.accent, modifier = Modifier.size(24.dp))
                    Text(text, style = Theme.body, modifier = Modifier.weight(1f))
                }
            }
        }
        Column {
            Box(Modifier.heightIn(min = 44.dp).clickable { showDetails = !showDetails }, contentAlignment = Alignment.CenterStart) {
                Text(if (showDetails) "Hide the details" else "Read the details", style = Theme.body.copy(color = Theme.accent))
            }
            AnimatedVisibility(showDetails, enter = expandVertically(), exit = shrinkVertically()) {
                Column(Modifier.padding(top = 12.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    InfoBlock("Who runs this", "Abram, an individual in London, testing an idea for a travel planning app. It's research: nothing is sold, and there is no payment either way. Contact: ${AppConfig.CONTACT_EMAIL}.")
                    InfoBlock("What you'll do", "Answer a few questions and react to some London places, then get a day plan. If you like, use it on a real day and rate each stop 1–5 after you've been. More questions, all optional, come after your first plan.")
                    InfoBlock("What we keep, and why", "Your answers, reactions, choices and ratings, to plan days that fit you and to test whether this works. The app only knows this phone by a random code. If you speak an answer, your phone turns it into text; the sound isn't saved or sent. If you share a moment, your link carries another random code, so we can count how many people it brings in.")
                    InfoBlock("Where, and for how long", "On our server in Frankfurt, in the EU. Kept until 31 March 2027, then deleted. Anonymised results may be kept.")
                    InfoBlock("What we don't ask for", "Your name, email, phone number, nationality, health details or allergies. Please don't enter them. The one exception is your choice: in Help & safety you can leave a phone or email so a person can reply, and it's deleted once it's sorted.")
                    QuietButton("Full privacy notice", color = Theme.accent) { openUrl(context, AppConfig.BASE_URL.trimEnd('/') + "/privacy") }
                }
            }
        }
        Column(Modifier.surfaceCard(padding = 18.dp)) {
            Text("To take part, please confirm both", style = Theme.headline, modifier = Modifier.padding(bottom = 6.dp))
            // 19 Oct review: agreeing is a tick, not a setting to switch
            CheckRow("I'm 18 or over", adult) { adult = it }
            Box(Modifier.fillMaxWidth().height(1.dp).background(Theme.hairline))
            CheckRow("I agree to take part", agree) { agree = it }
        }
        PrimaryButton(if (model.busy) "One moment…" else "Continue", enabled = adult && agree && !model.busy) { model.agree() }
        if (!(adult && agree)) {
            Text("Tick both to continue.", style = Theme.footnote, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())
        }
        QuietButton(if (code.isEmpty()) "Got a tester code?" else "Tester code: $code") { askCode = true }
    }
    if (askCode) {
        TesterCodeDialog(code, onDismiss = { askCode = false }) {
            code = it
            model.prefs.set("testerCode", it.ifEmpty { null })
        }
    }
}

/** A labelled switch, 48 dp or taller, amber when on. */
@Composable
fun ToggleRow(label: String, on: Boolean, enabled: Boolean = true, onChange: (Boolean) -> Unit) {
    Row(Modifier.fillMaxWidth().heightIn(min = 48.dp).clickable(enabled = enabled, role = Role.Switch) { onChange(!on) },
        verticalAlignment = Alignment.CenterVertically) {
        Text(label, style = Theme.body, modifier = Modifier.weight(1f))
        Switch(on, onChange, enabled = enabled, colors = odysSwitchColors())
    }
}

/** 19 Oct review: one look for every switch; off, the thumb is light on a dark track with a border, so it shows. */
@Composable
fun odysSwitchColors() = SwitchDefaults.colors(checkedTrackColor = Theme.accent, checkedThumbColor = Theme.onAccent,
    uncheckedTrackColor = Theme.surfaceHigh, uncheckedThumbColor = Theme.inkSoft, uncheckedBorderColor = Theme.inkTertiary)

/** A line to tick (19 Oct review: consent is agreed to, not switched on). */
@Composable
fun CheckRow(label: String, on: Boolean, onChange: (Boolean) -> Unit) {
    Row(Modifier.fillMaxWidth().heightIn(min = 48.dp).toggleable(on, role = Role.Checkbox, onValueChange = onChange),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        androidx.compose.material3.Checkbox(on, onCheckedChange = null,
            colors = androidx.compose.material3.CheckboxDefaults.colors(checkedColor = Theme.accent,
                uncheckedColor = Theme.inkSoft, checkmarkColor = Theme.onAccent))
        Text(label, style = Theme.body, modifier = Modifier.weight(1f))
    }
}
