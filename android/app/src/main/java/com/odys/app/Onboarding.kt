package com.odys.app

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.TouchApp
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material.icons.filled.AcUnit
import androidx.compose.material.icons.filled.WaterDrop
import androidx.compose.material.icons.automirrored.filled.DirectionsWalk
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.CurrencyPound
import androidx.compose.material.icons.filled.Groups
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.PhotoCamera
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material.icons.filled.SwapHoriz
import androidx.compose.material.icons.filled.WbCloudy
import androidx.compose.material.icons.outlined.Circle
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

// Screens 3b–7: onboarding up to the first plan (Test A inside the app, D109). Each step is sent as it finishes.
// (app/Sources/OnboardingViews.swift)

object Labels {
    /** D115: feelings, each mapped onto the model's features in brain/reasons.py (FEELINGS) */
    val why = mapOf("restored" to "Restored", "excited" to "Excited", "connected" to "Connected",
        "curious" to "Curious", "peaceful" to "Peaceful")
    val whyNote = mapOf("restored" to "Come home lighter than you left", "excited" to "Something to tell people about",
        "connected" to "Time that feels shared", "curious" to "Learn something you didn't expect",
        "peaceful" to "Calm while the city rushes past")
    val budget = listOf("under_20" to "Under £20", "20_40" to "£20–40", "40_70" to "£40–70", "70_plus" to "£70 or more")
    val company = listOf("solo" to "On my own", "friends" to "Friends", "partner" to "A partner", "family" to "Family")
    val chronotype = listOf("morning" to "Morning person", "night" to "Night person", "neither" to "Neither")
    val activity = listOf("gentle" to "Gentle", "medium" to "In between", "full_on" to "Full on")
    val reactions = listOf("loved" to "Loved it", "fine" to "It was fine", "didnt_enjoy" to "Didn't enjoy it",
        "havent_been" to "Haven't been")
    /** The rating's words (D115: one dimension), 1–5. */
    val feel = listOf("Disappointing", "Fine", "Good", "Great", "Unforgettable")
    /** The "this or that" attributes, always in the same order with the same icons (D95). */
    val attributeIcons = listOf(Icons.Filled.SwapHoriz, Icons.Filled.WbCloudy, Icons.Filled.Speed, Icons.Filled.Groups,
        Icons.Filled.CurrencyPound, Icons.AutoMirrored.Filled.DirectionsWalk)

    /** 20 Oct (round 2): the weather line's icon follows its words (rain, cold, mild). */
    fun attributeIcon(i: Int, text: String) = when {
        i == 1 && "rain" in text -> Icons.Filled.WaterDrop
        i == 1 && "cold" in text -> Icons.Filled.AcUnit
        i == 1 && "mild" in text -> Icons.Filled.WbSunny
        else -> attributeIcons.getOrNull(i) ?: Icons.Outlined.Circle
    }
}

@Composable
fun OnboardingView(model: AppModel) {
    val previous = Step.values().getOrNull(model.step.ordinal - 1)
    BackTo(enabled = previous != null && model.onboarding != null) { model.back() }
    Column(Modifier.screen().statusBarsPadding().navigationBarsPadding()) {
        if (model.step != Step.Based && model.onboarding != null && previous != null) {
            // m176: a way back to the step before
            val label = if (previous == Step.Places && model.isVisitor) "Kinds of places" else previous.title
            Box(Modifier.padding(horizontal = 12.dp)) { BackLink("Back to $label") { model.back() } }   // 19 Oct: Android's arrow
        }
        val ob = model.onboarding
        Box(Modifier.weight(1f)) {
            if (ob == null) {
                OnboardingLoading(model)
            } else {
                when (model.step) {
                    Step.Based -> BasedStep(model)
                    Step.BestHour -> BestHourStep(model)
                    Step.Why -> WhyStep(model)
                    Step.Places -> {
                        val cards = ob.categoryCards
                        if (model.isVisitor && !cards.isNullOrEmpty()) CategoryStep(model, cards) { model.finishCategories() }
                        else PlacesStep(model, ob.swipePlaces) { model.finishPlaces() }
                    }
                    Step.ThisOrThat -> ThisOrThatStep(model, ob.conjointTasks) { model.finishThisOrThat() }
                    Step.Learned -> LearnedStep(model)
                }
            }
        }
    }
}

/** Loads the questions once; if that fails, says so and offers "Try again". */
@Composable
fun OnboardingLoading(model: AppModel) {
    var failed by remember { mutableStateOf(false) }
    var attempt by remember { mutableIntStateOf(0) }
    LaunchedEffect(attempt) {
        failed = false
        model.run { model.loadOnboarding() }
        failed = model.onboarding == null
    }
    Column(Modifier.fillMaxSize().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(18.dp, Alignment.CenterVertically)) {
        ArchGlyph(width = 28.dp)
        if (failed) {
            Text("The questions didn't load.", style = Theme.title3)
            PrimaryButton("Try again", enabled = !model.busy) { attempt++ }
        } else {
            Text("Getting the questions…", style = Theme.body.copy(color = Theme.muted))
        }
    }
}

/** The top of each question: "Question 7 of 14" (D118) and a thin line of progress, with a quiet action on the right. */
@Composable
fun StepHeader(label: String, progress: Float, trailing: (@Composable () -> Unit)? = null) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Row(Modifier.fillMaxWidth().heightIn(min = 44.dp), verticalAlignment = Alignment.CenterVertically) {
            Eyebrow(label, Modifier.weight(1f))
            trailing?.invoke()
        }
        ProgressLine(progress)
    }
}

@Composable
fun ProgressLine(value: Float) {
    val v by animateFloatAsState(value.coerceIn(0f, 1f), androidx.compose.animation.core.tween(400), label = "progress")
    Box(Modifier.fillMaxWidth().height(4.dp).clip(CircleShape).background(Theme.ink.copy(alpha = 0.1f))) {
        Box(Modifier.fillMaxWidth(v).height(4.dp).clip(CircleShape).background(Theme.amberDeep))
    }
}

/** A typed answer: a dark box with a soft outline. */
@Composable
fun AnswerBox(text: String, onChange: (String) -> Unit, label: String, minHeight: Int = 110, placeholder: String? = null) {
    val shape = RoundedCornerShape(14.dp)
    BasicTextField(
        text, onChange,
        textStyle = Theme.body,
        cursorBrush = SolidColor(Theme.accent),
        keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.Sentences),
        modifier = Modifier.fillMaxWidth().heightIn(min = minHeight.dp).clip(shape).background(Theme.surface)
            .border(1.dp, Theme.outline, shape).padding(14.dp).semantics { contentDescription = label },
        decorationBox = { inner ->
            Box {
                if (text.isEmpty() && placeholder != null) Text(placeholder, style = Theme.body.copy(color = Theme.muted))
                inner()
            }
        },
    )
}

/** A one-line typed answer. */
@Composable
fun LineField(placeholder: String, text: String, onChange: (String) -> Unit,
              keyboard: KeyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.Words)) {
    val shape = RoundedCornerShape(14.dp)
    BasicTextField(
        text, onChange, singleLine = true, textStyle = Theme.body, cursorBrush = SolidColor(Theme.accent),
        keyboardOptions = keyboard,
        modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp).border(1.dp, Theme.outlineStrong, shape)
            .padding(horizontal = 16.dp, vertical = 14.dp),
        decorationBox = { inner ->
            Box(contentAlignment = Alignment.CenterStart) {
                if (text.isEmpty()) Text(placeholder, style = Theme.body.copy(color = Theme.muted))
                inner()
            }
        },
    )
}

// ---- 3b. Where you're based (D116) ----------------------------------------------------------------------

@Composable
fun BasedStep(model: AppModel) {
    val q = model.onboarding?.based
    val abroad = model.profile.based == "abroad"
    val labels = listOf("london" to "In London", "uk" to "Elsewhere in the UK", "abroad" to "Visiting from abroad")
    ScrollPage(spacing = 14, top = 0, bottom = 24) {
        StepHeader(model.questionLabel, model.questionProgress)
        PageTitle(q?.prompt ?: "Where are you based?", Modifier.padding(vertical = 6.dp).settle(0))
        labels.forEachIndexed { i, (key, label) ->
            val on = model.profile.based == key
            SelectTile(on, Modifier.settle(i + 1), onClick = { model.profile = model.profile.copy(based = key) }) {
                Row(Modifier.padding(horizontal = 20.dp), verticalAlignment = Alignment.CenterVertically) {
                    Text(label, style = Theme.body, modifier = Modifier.weight(1f))
                    RadioDot(on)
                }
            }
        }
        if (model.profile.based == "uk" || abroad) Column(Modifier.padding(top = 10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            // a town or city, never nationality (D116); 19 Oct: not for Londoners, who have said where already
            Text(if (abroad) "Which town or city are you visiting from? (optional)" else (q?.cityPrompt ?: "Which town or city? (optional)"),
                style = Theme.subheadline.copy(color = Theme.muted))
            LineField(if (abroad) "e.g. Tashkent" else "e.g. Manchester", model.profile.homeCity ?: "", onChange = {
                model.profile = model.profile.copy(homeCity = it.take(80).ifEmpty { null })
            })
        }
        Text(q?.note ?: "So we ask the right questions. We never ask your nationality.",
            style = Theme.subheadline.copy(color = Theme.muted))
        PrimaryButton(if (model.busy) "One moment…" else "Continue", Modifier.padding(top = 12.dp),
            enabled = !model.busy && model.profile.based != null) { model.finishBased() }
    }
}

// ---- 6b. Kinds of places: visitors from abroad (D116) --------------------------------------------------------

@Composable
fun CategoryStep(model: AppModel, cards: List<CategoryCard>, onDone: suspend () -> Unit) {
    var index by remember { mutableIntStateOf(0) }
    var askingWant by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    var advance by remember { mutableStateOf<Job?>(null) }
    val reactions = listOf("loved" to "Love it", "fine" to "It's fine", "didnt_enjoy" to "Not for me", "never_tried" to "Never tried")
    val wants = listOf("yes" to "Yes, I'd like to", "maybe" to "Not sure", "no" to "No thanks")

    fun answer(card: CategoryCard, reaction: String, want: String? = null) {
        model.categoryAnswers[card.key] = CategoryItem(card.key, reaction, want)
        model.react(card.reactions, if (want == "yes") "want_yes" else reaction)
        val wait = if (model.reaction == null) 300L else 1100L
        advance?.cancel()
        advance = scope.launch {
            delay(wait)
            askingWant = false
            model.reaction = null
            index += 1
            model.stepProgress = index
            if (index >= cards.size) onDone()
        }
    }

    fun back() {
        advance?.cancel()
        model.reaction = null
        if (askingWant) askingWant = false else index = maxOf(index - 1, 0)
        model.stepProgress = index
    }

    ScrollPage(spacing = 16, top = 0, bottom = 24) {
        StepHeader(model.questionLabel, model.questionProgress) {
            if (index < cards.size) QuietButton("Skip the rest", enabled = !model.busy) { scope.launch { onDone() } }
        }
        if (index < cards.size) {
            val card = cards[index]
            AnimatedContent(card.key, transitionSpec = { fadeIn() togetherWith fadeOut() }, label = "card") { _ ->
                Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    PlaceField(card.title, card.exampleId, null, card.exampleTitle?.let { "In London, for example: $it" })
                    Text(card.line, style = Theme.italic(19.sp, Theme.inkSoft))
                    if (askingWant) {
                        Text(model.onboarding?.categories?.wantPrompt ?: "Would you like to try it in London?", style = Theme.title3)
                        for ((k, label) in wants) AnswerTile(label, false) { answer(card, "never_tried", k) }
                    } else {
                        Text(model.onboarding?.categories?.prompt ?: "What kinds of places do you enjoy?",
                            style = Theme.body.copy(color = Theme.inkSoft))
                        Grid2(reactions) { (k, label) ->
                            AnswerTile(label, model.categoryAnswers[card.key]?.reaction == k) {
                                if (k == "never_tried") askingWant = true else answer(card, k)
                            }
                        }
                    }
                }
            }
            ReactionSpace(model.reaction)
            Row(Modifier.fillMaxWidth()) {
                QuietButton("Previous", enabled = index > 0 || askingWant) { back() }
                Spacer(Modifier.weight(1f))
                QuietButton("Not sure, skip") { answer(card, "skip") }
            }
        } else {
            StepEnd(model, "That's all ${cards.size}. Thank you.", { index = maxOf(cards.size - 1, 0) }, onDone)
        }
    }
}

/** Two equal columns, wrapping. */
@Composable
fun <T> Grid2(items: List<T>, spacing: Int = 10, cell: @Composable (T) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(spacing.dp)) {
        for (row in items.chunked(2)) {
            Row(horizontalArrangement = Arrangement.spacedBy(spacing.dp)) {
                for (item in row) Box(Modifier.weight(1f)) { cell(item) }
                if (row.size == 1) Spacer(Modifier.weight(1f))
            }
        }
    }
}

/** A place or a kind of place: its photo (credited underneath) or a field of colour, with its name. */
@Composable
fun PlaceField(title: String, photoId: String?, feel: String?, note: String? = null) {
    val context = LocalContext.current
    val found = remember(photoId) { photoId?.let { CardPhotos.photo(context, it) } }
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Box(Modifier.fillMaxWidth().height(260.dp).clip(RoundedCornerShape(24.dp))) {
            if (found != null) {
                Image(found.second.asImageBitmap(), null, contentScale = ContentScale.Crop, modifier = Modifier.fillMaxSize())
            } else {
                Box(Modifier.fillMaxSize().background(fieldBrush(feel)))
            }
            Text(
                title, style = Theme.serif(34.sp), maxLines = 3, overflow = TextOverflow.Ellipsis,
                modifier = Modifier.align(Alignment.BottomStart).fillMaxWidth()
                    .background(Brush.verticalGradient(listOf(Color.Transparent, Color.Black.copy(alpha = 0.7f))))
                    .padding(start = 20.dp, end = 20.dp, top = 50.dp, bottom = 20.dp),
            )
        }
        if (note != null) Text(note, style = Theme.footnote)
        found?.first?.let { Text(it.credit, style = Theme.caption.copy(fontSize = 11.sp), maxLines = 2) }
    }
}

/** An answer in the 2 × 2 grid, or in a list. */
@Composable
fun AnswerTile(title: String, on: Boolean, onClick: () -> Unit) {
    SelectTile(on, radius = 16.dp, minHeight = 56.dp, onClick = onClick) {
        // 19 Oct review: a tick as well as the amber edge, so the choice doesn't rest on colour alone
        Row(Modifier.fillMaxWidth().padding(horizontal = 8.dp), horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically) {
            if (on) Icon(Icons.Filled.Check, null, tint = Theme.accent, modifier = Modifier.size(16.dp).padding(end = 2.dp))
            Text(title, style = Theme.body, textAlign = TextAlign.Center)
        }
    }
}

/** Where a reaction appears, with room kept for it so nothing jumps. */
@Composable
fun ReactionSpace(text: String?) {
    Box(Modifier.fillMaxWidth().heightIn(min = 52.dp)) {
        if (text != null) WordReveal(text)
    }
}

/** The end of a set of questions: what normally goes on by itself, with a button in case sending failed. */
@Composable
fun StepEnd(model: AppModel, text: String, onBack: () -> Unit, onDone: suspend () -> Unit) {
    val scope = rememberCoroutineScope()
    Column(Modifier.fillMaxWidth().padding(top = 40.dp), horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(18.dp)) {
        ArchGlyph(width = 28.dp)
        Text(text, style = Theme.title3, textAlign = TextAlign.Center)
        PrimaryButton(if (model.busy) "One moment…" else "Next", enabled = !model.busy) { scope.launch { onDone() } }
        QuietButton("Back", onClick = onBack)
    }
}

// ---- 7b. So far, I've learned… (D117) ------------------------------------------------------------------------

@Composable
fun LearnedStep(model: AppModel) {
    var changing by remember { mutableStateOf(false) }
    var wrong by remember { mutableStateOf(setOf<String>()) }
    var failed by remember { mutableStateOf(false) }
    LaunchedEffect(Unit) {
        if (model.learned == null) {
            model.run { model.learned = model.client.summary() }
            failed = model.learned == null
        }
    }
    val learned = model.learned
    val items = learned?.items ?: emptyList()
    ScrollPage(spacing = 18, top = 28, bottom = 24) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Eyebrow(learned?.title ?: "So far, I've learned…")
            Text(learned?.note ?: "From your answers only. Nothing here is a score.", style = Theme.subheadline.copy(color = Theme.muted))
        }
        when {
            failed -> {
                Text("This didn't load just now, but your answers are saved.", style = Theme.body)
                PrimaryButton("Plan my first day", enabled = !model.busy) { model.finishLearned(emptySet()) }
            }
            learned == null -> Box(Modifier.fillMaxWidth().heightIn(min = 80.dp), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = Theme.accent)
            }
            items.isEmpty() -> Text(learned.empty ?: "Your first plan starts from what most people enjoy, and it learns from how you rate each stop.",
                style = Theme.title3)
            else -> {
                if (changing) Text(learned.changeNote ?: "Tap anything that isn't right. We'll stop using that answer.",
                    style = Theme.subheadline.copy(color = Theme.inkSoft))
                Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    items.forEachIndexed { i, item ->
                        LearnedRow(item, changing, item.id in wrong, Modifier.settle(i)) {
                            wrong = if (item.id in wrong) wrong - item.id else wrong + item.id
                        }
                    }
                }
            }
        }
        Column(Modifier.padding(top = 10.dp), verticalArrangement = Arrangement.spacedBy(10.dp),
            horizontalAlignment = Alignment.CenterHorizontally) {
            if (changing) {
                PrimaryButton(if (model.busy) "One moment…" else if (wrong.isEmpty()) "Plan my first day" else "Save and plan my first day",
                    enabled = !model.busy) { model.finishLearned(wrong) }
                QuietButton("Cancel") { changing = false; wrong = emptySet() }
            } else if (learned != null) {
                PrimaryButton(if (model.busy) "One moment…" else if (items.isEmpty()) "Plan my first day" else "Looks right",
                    enabled = !model.busy) { model.finishLearned(emptySet()) }
                if (items.isNotEmpty()) SecondaryButton("Change something") { changing = true }
            }
        }
    }
}

@Composable
fun LearnedRow(item: LearnedItem, changing: Boolean, wrong: Boolean, modifier: Modifier = Modifier, toggle: () -> Unit) {
    Row(modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(14.dp)) {
        Box(Modifier.padding(top = 6.dp)) { ArchGlyph(if (wrong) Theme.line else Theme.accent) }   // m190: level with the 20 sp first line
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(item.text, style = Theme.serif(20.sp).copy(   // m190 (design review): a list, not six headlines (was 24)
                color = if (wrong) Theme.muted else Theme.ink,
                textDecoration = if (wrong) TextDecoration.LineThrough else null))
            if (changing) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    Box(
                        Modifier.heightIn(min = 44.dp).pressable(onClick = toggle)
                            .semantics { contentDescription = if (wrong) "Undo: keep using this answer" else "Don't use this answer" },
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(if (wrong) "Undo" else "Don't use this",
                            style = Theme.subheadline.copy(fontWeight = FontWeight.Medium, color = if (wrong) Theme.accent else Theme.ink),
                            modifier = Modifier.border(1.dp, if (wrong) Theme.accent else Theme.outlineStrong, CircleShape)
                                .padding(horizontal = 16.dp, vertical = 10.dp))
                    }
                    if (wrong) Text("We'll stop using this answer.", style = Theme.footnote)
                }
            }
        }
    }
}

// ---- 4. A great moment (D112) -----------------------------------------------------------------------------

@Composable
fun BestHourStep(model: AppModel) {
    val context = LocalContext.current
    val dictation = remember { Dictation(context) }
    val q = model.onboarding?.openQuestions?.firstOrNull()
    var pendingStart by remember { mutableStateOf(false) }
    val askMic = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { ok ->
        if (!ok) dictation.problem = "To speak your answer, allow the microphone for ODYS in Settings. Or just type."
        else pendingStart = true
    }

    fun startListening() {
        val before = model.bestHour.trim()
        dictation.start { text ->
            model.bestHour = if (before.isEmpty()) text else "$before $text"
            model.bestHourVoice = true
        }
    }
    LaunchedEffect(pendingStart) {
        if (pendingStart) {
            pendingStart = false
            startListening()
        }
    }

    fun skip() {
        dictation.stop()
        model.bestHour = ""
        model.bestHourMore = ""
        model.bestHourVoice = false
        model.finishBestHour()
    }

    ScrollPage(spacing = 16, top = 0, bottom = 24) {
        StepHeader(model.questionLabel, model.questionProgress) {
            QuietButton("Skip", enabled = !model.busy) { skip() }
        }
        PageTitle(q?.text ?: "Tell us about a great moment from a recent day out.", Modifier.settle(0), style = Theme.title2)
        val examples = q?.examples
        if (!examples.isNullOrEmpty()) {
            Column(Modifier.settle(1), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("For example", style = Theme.subheadline.copy(color = Theme.muted))
                for (line in examples) Text("“$line”", style = Theme.italic(18.sp, Theme.inkSoft))
            }
        }
        if (dictation.available) {
            // D115: speaking is the easy way in, so it comes first and big; typing stays below
            TellItButton(dictation.listening) {
                if (dictation.listening) {
                    dictation.stop()
                } else if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) ==
                    PackageManager.PERMISSION_GRANTED) {
                    startListening()
                } else {
                    askMic.launch(Manifest.permission.RECORD_AUDIO)
                }
            }
            Text("Your phone turns your words into text. The sound isn't saved or sent.", style = Theme.footnote)
        }
        dictation.problem?.let { Text(it, style = Theme.footnote.copy(color = Theme.ink)) }
        Text(if (dictation.available) "Or type it" else "Type it, or tap the mic on your keyboard",
            style = Theme.subheadline.copy(color = Theme.muted))
        AnswerBox(model.bestHour, { model.bestHour = it }, "Your answer")
        Text("A few words is fine. There are no wrong answers.", style = Theme.footnote)
        if (model.bestHour.isNotEmpty()) {
            Text(q?.followUp ?: "Is there anything else you'd like to add about that?", style = Theme.title3)
            AnswerBox(model.bestHourMore, { model.bestHourMore = it }, "Anything else", minHeight = 80)
        }
        PrimaryButton("Next", Modifier.padding(top = 4.dp), enabled = !model.busy && model.bestHour.isNotEmpty()) {
            dictation.stop()
            model.finishBestHour()
        }
    }
}

/** D115: the big "Tell it instead" button: a mic in an amber circle; rings move out from it while it listens. */
@Composable
fun TellItButton(listening: Boolean, onClick: () -> Unit) {
    val shape = RoundedCornerShape(22.dp)
    Row(
        Modifier.fillMaxWidth().heightIn(min = 80.dp).pressable(haptic = true, onClick = onClick)
            .semantics { contentDescription = if (listening) "Stop listening" else "Speak your answer instead" }
            .clip(shape).background(Theme.surface)
            .border(1.5.dp, Theme.accent.copy(alpha = if (listening) 1f else 0.55f), shape).padding(14.dp),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Box(Modifier.size(52.dp), contentAlignment = Alignment.Center) {
            ListenRings(listening, Modifier.size(52.dp))
            Box(Modifier.size(52.dp).clip(CircleShape).background(Theme.accent), contentAlignment = Alignment.Center) {
                Icon(if (listening) Icons.Filled.Stop else Icons.Filled.Mic, null, tint = Theme.onAccent)
            }
        }
        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(if (listening) "Listening… tap when you're done" else "Speak instead", style = Theme.headline)
            Text(if (listening) "Say it the way you'd tell a friend." else "Speak your answer. No typing.",
                style = Theme.subheadline.copy(color = Theme.muted))
        }
    }
}

// ---- 5. How you want to feel (D115; up to two, or none) -----------------------------------------------------

@Composable
fun WhyStep(model: AppModel) {
    val choices = model.onboarding?.whyTravel
    val (title, sub) = PromptText.split(choices?.prompt?.ifEmpty { null } ?: "How do you most want to feel on a day out? Pick one or two.")
    val options = choices?.options ?: emptyList()

    fun pick(key: String, on: Boolean) {
        model.why = if (on) model.why - key else (if (model.why.size >= 2) model.why.drop(1) else model.why) + key
    }

    ScrollPage(spacing = 12, top = 0, bottom = 24) {
        StepHeader(model.questionLabel, model.questionProgress)
        PageTitle(title, Modifier.padding(top = 6.dp).settle(0))
        if (sub != null) Text(sub, style = Theme.body.copy(color = Theme.muted), modifier = Modifier.padding(bottom = 6.dp))
        options.forEachIndexed { i, key ->
            val on = key in model.why
            SelectTile(on, Modifier.settle(i + 1), onClick = { pick(key, on) }) {
                Row(Modifier.padding(horizontal = 18.dp, vertical = 14.dp), verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(3.dp)) {
                        Text(Labels.why[key] ?: key, style = Theme.option)
                        Labels.whyNote[key]?.let { Text(it, style = Theme.subheadline.copy(color = Theme.inkTertiary)) }
                    }
                    TickBox(on)   // D118: squares mean "pick more than one"
                }
            }
        }
        ReactionSpace(if (model.why.isEmpty()) null else "Got it: you want to feel " + model.why.joinToString(" and ") + ".")
        PrimaryButton("Continue", enabled = model.why.isNotEmpty()) {
            model.keepFeelings()
            model.next()
        }
        // D118: opting out is never the loudest button; 19 Oct review: but a real one, easy to see and tap
        SecondaryButton("None of these", Modifier.fillMaxWidth()) {
            model.why = emptyList()
            model.keepFeelings()
            model.next()
        }
    }
}

// ---- 6. Places you've been (6 before the plan, 4 more in "Improve future plans"; D112) -------------------------

@Composable
fun PlacesStep(model: AppModel, places: List<SwipePlace>, standalone: Boolean = false, onDone: suspend () -> Unit) {
    val context = LocalContext.current
    var index by remember { mutableIntStateOf(0) }
    var answered by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()
    var advance by remember { mutableStateOf<Job?>(null) }

    fun react(place: SwipePlace, reaction: String) {
        model.reactions[place.item] = reaction
        model.react(place.reactions, reaction)
        answered = reaction
        val wait = if (model.reaction == null) 300L else 1100L
        advance?.cancel()
        advance = scope.launch {
            delay(wait)
            answered = null
            model.reaction = null
            index += 1
            model.stepProgress = index
            if (index >= places.size) onDone()
        }
    }

    ScrollPage(spacing = 16, top = 0, bottom = 24) {
        StepHeader(if (standalone) "${minOf(index + 1, places.size)} of ${places.size}" else model.questionLabel,
            if (standalone) index.toFloat() / maxOf(places.size, 1) else model.questionProgress) {
            if (index < places.size) QuietButton("Skip the rest", enabled = !model.busy) { scope.launch { onDone() } }
        }
        if (index < places.size) {
            val place = places[index]
            AnimatedContent(place.item, transitionSpec = { fadeIn() togetherWith fadeOut() }, label = "place") { _ ->
                Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    PlaceField(place.name, place.photoIds?.firstOrNull { CardPhotos.photo(context, it) != null }, null)
                    Text(model.onboarding?.swipe?.prompt ?: "Have you been? How did it feel?", style = Theme.body.copy(color = Theme.inkSoft))
                    Grid2(Labels.reactions) { (k, label) ->
                        AnswerTile(label, (answered ?: model.reactions[place.item]) == k) { react(place, k) }
                    }
                }
            }
            ReactionSpace(model.reaction)
            Row(Modifier.fillMaxWidth()) {
                QuietButton("Previous", enabled = index > 0) {
                    advance?.cancel()
                    answered = null
                    model.reaction = null
                    index = maxOf(index - 1, 0)
                    model.stepProgress = index
                }
                Spacer(Modifier.weight(1f))
                QuietButton("Not sure, skip") { react(place, "skip") }
            }
        } else {
            StepEnd(model, "That's all ${places.size} places. Thank you.", { index = maxOf(places.size - 1, 0) }, onDone)
        }
    }
}

// ---- 7. This or that: made-up example days (D112) -----------------------------------------------------------

@Composable
fun ThisOrThatStep(model: AppModel, tasks: List<ConjointTask>, standalone: Boolean = false, onDone: suspend () -> Unit) {
    var index by remember {
        // journey round 2: back from "So far", pick up at the first pair not answered
        val first = tasks.indexOfFirst { model.choices[it.task] == null }
        mutableIntStateOf(if (first < 0 && tasks.isNotEmpty()) tasks.size else maxOf(first, 0))
    }
    var picked by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()
    LaunchedEffect(Unit) { model.stepProgress = index }
    val label = model.onboarding?.conjoint?.optionLabel ?: "Example day"
    val (title, sub) = PromptText.split(model.onboarding?.conjoint?.prompt ?: "Which day sounds more like you? There are no wrong answers.")

    fun choose(task: ConjointTask, choice: String) {
        if (picked != null) return   // one choice per pair, even with a quick second tap
        picked = choice
        model.choices[task.task] = choice
        model.reactToChoices(tasks)
        scope.launch {
            delay(280)
            picked = null
            index += 1
            model.stepProgress = index
            if (index >= tasks.size) onDone()
        }
    }

    ScrollPage(spacing = 14, top = 0, bottom = 24) {
        StepHeader(if (standalone) "${minOf(index + 1, tasks.size)} of ${tasks.size}" else model.questionLabel,
            if (standalone) index.toFloat() / maxOf(tasks.size, 1) else model.questionProgress)
        if (index < tasks.size) {
            val task = tasks[index]
            PageTitle(title, Modifier.padding(top = 6.dp))
            if (sub != null) Text(sub, style = Theme.body.copy(color = Theme.muted))
            AnimatedContent(task.task, transitionSpec = { fadeIn() togetherWith fadeOut() }, label = "pair") { _ ->
                Column(verticalArrangement = Arrangement.spacedBy(10.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    DayOption("$label A", task.a, index % 2, (picked ?: model.choices[task.task]) == "A") { choose(task, "A") }
                    Text("or", style = Theme.italic(18.sp, Theme.muted))
                    DayOption("$label B", task.b, (index + 1) % 2, (picked ?: model.choices[task.task]) == "B") { choose(task, "B") }
                }
            }
            Row(Modifier.fillMaxWidth()) {
                QuietButton("Previous", enabled = index > 0) {
                    picked = null
                    index = maxOf(index - 1, 0)
                    model.stepProgress = index
                }
                Spacer(Modifier.weight(1f))
                val earlier = model.choices[task.task]
                if (picked == null && earlier != null) {
                    QuietButton("Keep ${if (earlier == "N") "no preference" else earlier}, next", color = Theme.accent) {
                        choose(task, earlier)
                    }
                } else {
                    QuietButton(model.onboarding?.conjoint?.noPreference ?: "No preference") { choose(task, "N") }
                }
            }
            ReactionSpace(model.reaction)
        } else {
            StepEnd(model, if (standalone) "Thank you. Your next plans will use these." else "That's everything. Next: what I've learned so far.",
                { index = maxOf(tasks.size - 1, 0) }, onDone)
        }
    }
}

/** One made-up day: all six details, each with its icon (D95), on a field of colour that swaps from pair to pair. */
@Composable
fun DayOption(label: String, text: String, field: Int, on: Boolean, onClick: () -> Unit) {
    val parts = text.split("; ")
    val shape = RoundedCornerShape(24.dp)
    // 19 Oct review: both days on the same quiet field (a red one could make a day look worse before it's read)
    Box(
        Modifier.fillMaxWidth().pressable(haptic = true, onClick = onClick).clip(shape).background(if (on) Theme.selected else Theme.surface)
            .border(if (on) 2.dp else 1.dp, if (on) Theme.accent else Theme.outline, shape)
            .semantics { contentDescription = "$label: $text. Choose this made-up day" },
    ) {
        Column(Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(label, style = Theme.serif(22.sp), modifier = Modifier.weight(1f))
                Text("Made up", style = Theme.footnote.copy(color = Theme.inkSoft))
            }
            parts.forEachIndexed { i, part ->
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    Icon(Labels.attributeIcon(i, part), null, tint = Theme.accent,
                        modifier = Modifier.size(20.dp).padding(top = 2.dp))
                    Text(part.replaceFirstChar { it.uppercase() }, style = Theme.body)
                }
            }
            // 20 Oct (round 2): a pill, so it reads as the thing to tap
            Row(Modifier.padding(top = 4.dp).clip(RoundedCornerShape(50)).background(if (on) Theme.accent else Color.Transparent)
                .border(1.dp, Theme.accent, RoundedCornerShape(50)).heightIn(min = 40.dp).padding(horizontal = 16.dp),
                verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                Icon(if (on) Icons.Filled.Check else Icons.Filled.TouchApp, null, tint = if (on) Theme.background else Theme.accent,
                    modifier = Modifier.size(16.dp))
                Text(if (on) "Chosen" else "Choose this day", style = Theme.subheadline.copy(color = if (on) Theme.background else Theme.accent,
                    fontWeight = FontWeight.SemiBold))
            }
        }
    }
}

// ---- 12. Improve future plans (D115): one question at a time ---------------------------------------------

@Composable
fun ImproveView(model: AppModel, onClose: () -> Unit) {
    var step by remember { mutableIntStateOf(-1) }      // -1: the invitation
    var morePlaces by remember { mutableStateOf(false) }
    var moreTasks by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    val count = 7   // budget, company, chronotype, activity, fields, photos, shot card (D123: two dropped)

    fun go(next: Int) {
        step = maxOf(0, next)
        if (next >= count) scope.launch { model.saveImprovements(true) }
    }

    fun close() {
        if (step >= 0) scope.launch { model.saveImprovements(false); onClose() } else onClose()
    }

    FullSheet(model, ::close) {
        Column(Modifier.fillMaxSize()) {
            SheetBar("Improve future plans", onClose = ::close)
            ScrollPage(spacing = 16, top = 0, bottom = 24) {
                when {
                    step < 0 -> {
                        Box(Modifier.padding(top = 12.dp)) { ArchGlyph(width = 22.dp) }
                        PageTitle("Make your next day even better?")
                        Text("About a minute. One quick question at a time: your budget, who you go with, your pace, what interests you. Skip any, stop any time.",
                            style = Theme.body.copy(color = Theme.inkSoft))
                        Text("Your budget and interests shape your next plans; the other answers help us test the idea.", style = Theme.footnote)
                        PrimaryButton(if (model.improved) "Change my answers" else "Start", Modifier.padding(top = 8.dp)) { go(0) }
                        QuietButton("Not now", Modifier.fillMaxWidth()) { onClose() }
                    }
                    step < count -> {
                        StepHeader("${step + 1} of $count", step.toFloat() / count) { QuietButton("Skip") { go(step + 1) } }
                        ImproveQuestion(model, step) { go(it) }
                        Row(Modifier.fillMaxWidth()) {
                            QuietButton("Previous", enabled = step > 0) { go(step - 1) }
                            Spacer(Modifier.weight(1f))
                            QuietButton("Stop here, keep my answers", enabled = !model.busy) {
                                scope.launch {
                                    model.saveImprovements(false)
                                    if (model.errorMessage == null) onClose()
                                }
                            }
                        }
                    }
                    else -> {
                        Box(Modifier.padding(top = 12.dp)) { ArchGlyph(width = 22.dp) }
                        PageTitle("Thank you.")
                        Text("Your next plans will use your budget and interests.", style = Theme.body.copy(color = Theme.inkSoft))
                        val later = if (model.isVisitor) emptyList() else (model.onboarding?.swipePlacesLater ?: emptyList())
                        val laterTasks = model.onboarding?.conjointTasksLater ?: emptyList()
                        if (later.isNotEmpty() || laterTasks.isNotEmpty()) {
                            Text("Want to go further? About 2 minutes more.", style = Theme.headline, modifier = Modifier.padding(top = 8.dp))
                            if (later.isNotEmpty()) MoreRow("${later.size} more places you may have been", model.morePlacesDone) { morePlaces = true }
                            if (laterTasks.isNotEmpty()) MoreRow("${laterTasks.size} more made-up example days", model.moreTasksDone) { moreTasks = true }
                        }
                        PrimaryButton(if (model.busy) "Saving…" else "Done", Modifier.padding(top = 8.dp), enabled = !model.busy) {
                            if (model.improved) onClose() else scope.launch {
                                model.saveImprovements(true)
                                if (model.errorMessage == null) onClose()
                            }
                        }
                    }
                }
            }
        }
    }
    if (morePlaces) {
        FullSheet(model, { morePlaces = false }) {
            Column(Modifier.fillMaxSize()) {
                SheetBar("More places") { morePlaces = false }
                PlacesStep(model, model.onboarding?.swipePlacesLater ?: emptyList(), standalone = true) {
                    model.finishMorePlaces()
                    if (model.errorMessage == null) morePlaces = false
                }
            }
        }
    }
    if (moreTasks) {
        FullSheet(model, { moreTasks = false }) {
            Column(Modifier.fillMaxSize()) {
                SheetBar("More example days") { moreTasks = false }
                ThisOrThatStep(model, model.onboarding?.conjointTasksLater ?: emptyList(), standalone = true) {
                    model.finishMoreTasks()
                    if (model.errorMessage == null) moreTasks = false
                }
            }
        }
    }
}

@Composable
private fun ColumnScope.ImproveQuestion(model: AppModel, q: Int, go: (Int) -> Unit) {
    val about = (model.onboarding?.aboutYou ?: emptyList()).associateBy { it.key }
    val photos = model.onboarding?.photos ?: emptyList()
    val p = model.profile
    when (q) {
        0 -> {
            QuestionTitle(about["budget_band"]?.text ?: "About how much do you like to spend on a day out?")
            ChoiceList(Labels.budget, p.budgetBand) { model.profile = p.copy(budgetBand = it); go(1) }
        }
        1 -> {
            QuestionTitle(about["company"]?.text ?: "Who do you usually go with?")
            ChoiceList(Labels.company, p.company) { model.profile = p.copy(company = it); go(2) }
        }
        2 -> {
            QuestionTitle(about["chronotype"]?.text ?: "Are you a morning or a night person?")
            ChoiceList(Labels.chronotype, p.chronotype) { model.profile = p.copy(chronotype = it); go(3) }
        }
        3 -> {
            QuestionTitle(about["activity"]?.text ?: "How active do you like a day out to be?")
            ChoiceList(Labels.activity, p.activity) { model.profile = p.copy(activity = it); go(4) }
        }
        4 -> {
            val fields = model.onboarding?.fields
            if (fields != null) {
                QuestionTitle(fields.question)
                for (option in fields.options.filter { it.key != "none" }) {
                    val on = option.key in p.fields
                    SelectTile(on, onClick = {
                        model.profile = model.profile.copy(fields = model.profile.fields.filter { it != option.key } +
                            if (on) emptyList() else listOf(option.key))
                    }) {
                        Row(Modifier.padding(horizontal = 18.dp), verticalAlignment = Alignment.CenterVertically) {
                            Text(option.label, style = Theme.body, modifier = Modifier.weight(1f))
                            TickBox(on)
                        }
                    }
                }
                Text(fields.note, style = Theme.footnote)
                PrimaryButton(if (p.fields.isEmpty()) "None of these" else "Next") { go(5) }
            } else {
                PrimaryButton("Next") { go(5) }
            }
        }
        5 -> {
            QuestionTitle(photos.firstOrNull()?.text ?: "How much do photos and sharing matter on your trips?")
            ScaleRow("Not at all", "A lot", p.photosMatter) { model.profile = model.profile.copy(photosMatter = it) }
            PrimaryButton("Next", enabled = p.photosMatter != null) { go(6) }
        }
        else -> {
            QuestionTitle(if (photos.size > 1) photos[1].text else "Some stops come with a shot card: where to stand for the best photo. Would that make you more likely to go?")
            model.onboarding?.exampleShotCard?.let {
                Box(Modifier.surfaceCard()) { ShotCardSummary(it, if (photos.size > 1) photos[1].exampleLabel else null) }
            }
            ScaleRow("No", "Definitely", p.shotCardAppeal) { model.profile = model.profile.copy(shotCardAppeal = it) }
            PrimaryButton("Finish", enabled = p.shotCardAppeal != null) { go(7) }
        }
    }
}

@Composable
fun QuestionTitle(text: String) = PageTitle(text, Modifier.padding(vertical = 6.dp), style = Theme.title)

/** One tap answers and moves on (D115). */
@Composable
fun ChoiceList(options: List<Pair<String, String>>, selected: String?, pick: (String) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        for ((key, label) in options) ChoiceRow(label, selected == key) { pick(key) }
    }
}

@Composable
fun ChoiceRow(label: String, on: Boolean, onClick: () -> Unit) {
    SelectTile(on, minHeight = 56.dp, onClick = onClick) {
        Row(Modifier.padding(horizontal = 18.dp), verticalAlignment = Alignment.CenterVertically) {
            Text(label, style = Theme.body, modifier = Modifier.weight(1f))
            RadioDot(on)
        }
    }
}

@Composable
fun MoreRow(title: String, done: Boolean, onClick: () -> Unit) {
    Row(
        Modifier.fillMaxWidth().heightIn(min = 56.dp).pressable(onClick = onClick).clip(RoundedCornerShape(18.dp))
            .background(Theme.surface).padding(horizontal = 18.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(title, style = Theme.body, modifier = Modifier.weight(1f))
        if (done) {
            Icon(Icons.Filled.Check, null, tint = Theme.muted, modifier = Modifier.size(16.dp))
            Text(" Done", style = Theme.footnote)
        } else {
            Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = Theme.muted)
        }
    }
}

/** The short shot-card example (D112): where to stand and when, with a small map. */
@Composable
fun ShotCardSummary(card: Card, label: String?) {
    Column(Modifier.padding(vertical = 4.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Eyebrow(label ?: "Example of what you'll get")
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Icon(Icons.Filled.PhotoCamera, null, tint = Theme.ink, modifier = Modifier.size(18.dp))
            Text(card.title, style = Theme.headline)
        }
        val shot = card.shotCard
        if (shot != null) {
            val lat = shot.standAt?.lat
            val lon = shot.standAt?.lon
            if (lat != null && lon != null) {
                OsmMap(listOf(MapPin(Point(lat, lon), "Stand here")), Modifier.fillMaxWidth().height(110.dp)
                    .clip(RoundedCornerShape(12.dp)), zoom = 16)
            }
            InfoBlock("Where to stand", shot.standAt?.note ?: "")
            InfoBlock("When", shot.`when` ?: "")
        }
    }
}
