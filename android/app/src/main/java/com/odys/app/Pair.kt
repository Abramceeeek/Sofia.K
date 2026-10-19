package com.odys.app

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
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
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch

// Build 2 (Tests A and B inside the app): after "So far", the Test A survey; then, for people based in the UK, the
// blind Plan 1 / Plan 2 pair: a gut choice, "This plan fits me" for each, and why; then which one was made from their
// answers. Both plans are the same text format, so nothing gives the personal one away (app/Sources/PairViews.swift).

@Composable
fun FirstPlanFlow(model: AppModel) {
    LaunchedEffect(Unit) { runCatching { model.loadOnboarding() } }
    Box(Modifier.screen().statusBarsPadding().navigationBarsPadding()) {
        if (!model.surveyDone) SurveyView(model) else PairFlow(model)
    }
}

@Composable
fun SurveyView(model: AppModel) {
    val text = model.onboarding?.survey
    var understood by remember { mutableStateOf<Int?>(null) }
    var likePerson by remember { mutableStateOf<Int?>(null) }
    var typedOrSpoke by remember { mutableStateOf<String?>(null) }
    var intrusive by remember { mutableStateOf("") }
    val nothing = understood == null && likePerson == null && typedOrSpoke == null && intrusive.isBlank()
    PageWithBottom(
        spacing = 26,
        bottom = {
            PrimaryButton(if (model.busy) "Sending…" else "Send", enabled = !model.busy && !nothing) {
                model.sendSurvey(SurveyBody(understood, likePerson, typedOrSpoke, intrusive.trim().ifEmpty { null }))
            }
            QuietButton("Skip these", Modifier.fillMaxWidth()) { model.sendSurvey(null) }
        },
    ) {
        Eyebrow(if (model.isVisitor) "Before your first day" else "Before your plan")
        Column(Modifier.settle(0), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            PageTitle(text?.title ?: "Three quick questions")
            Text("About the questions you've just answered. Every one is optional.", style = Theme.body.copy(color = Theme.muted))
        }
        SurveyQuestion(text?.understood ?: "I felt understood.", Modifier.settle(1)) {
            ScaleRow("not at all", "completely", understood) { understood = it }
        }
        SurveyQuestion(text?.likePerson ?: "It felt like talking to a person, not filling in a form.", Modifier.settle(2)) {
            ScaleRow("not at all", "completely", likePerson) { likePerson = it }
        }
        SurveyQuestion(text?.typedOrSpoke ?: "Did you type or speak your answers?", Modifier.settle(3)) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for ((key, label) in listOf("typed" to "Typed", "spoke" to "Spoke", "both" to "Both")) {
                    Chip(label, typedOrSpoke == key, Modifier.weight(1f)) { typedOrSpoke = if (typedOrSpoke == key) null else key }
                }
            }
        }
        SurveyQuestion(text?.intrusive ?: "Was anything intrusive or tedious? (optional)") {
            AnswerBox(intrusive, { intrusive = it }, "Anything intrusive or tedious", minHeight = 90)
        }
    }
}

@Composable
fun SurveyQuestion(text: String, modifier: Modifier = Modifier, content: @Composable ColumnScope.() -> Unit) {
    Column(modifier, verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(text, style = Theme.title3)
        content()
    }
}

@Composable
fun PairFlow(model: AppModel) {
    Box(Modifier.fillMaxSize()) {
        val pair = model.pair
        when {
            pair == null -> PairIntentView(model)
            pair.done -> PairReveal(model, pair)
            else -> PairCompare(model, pair)
        }
        // m176: opened from home, it can be left for later
        if (model.showPair && model.pair?.done != true) {
            QuietButton("Not now", Modifier.align(Alignment.TopEnd).padding(horizontal = 20.dp), color = Theme.accent) {
                model.showPair = false
            }
        }
    }
}

/** Screen 18: recharge or explore, who might come, anything for sure. Stored with both plans; it changes neither. */
@Composable
fun PairIntentView(model: AppModel) {
    val text = model.onboarding?.testb
    var mood by remember { mutableStateOf<String?>(null) }
    var company by remember { mutableStateOf<String?>(null) }
    var wish by remember { mutableStateOf("") }
    PageWithBottom(
        spacing = 24,
        bottom = {
            PrimaryButton(if (model.busy) "Making your two plans…" else "Show me the two plans", enabled = !model.busy) {
                model.startPair(PairIntent(mood, company, wish.trim().ifEmpty { null }))
            }
            QuietButton("Skip the comparison", Modifier.fillMaxWidth()) { model.skipPair() }
        },
    ) {
        Eyebrow("Two plans for a Saturday")
        PageTitle(text?.intentTitle ?: "Before your plans", Modifier.settle(0))
        Text("Next you'll see two plans for the same Saturday afternoon, made in different ways. First, three quick things.",
            style = Theme.body.copy(color = Theme.inkSoft), modifier = Modifier.settle(1))
        SurveyQuestion(text?.moodPrompt ?: "Recharge or explore?", Modifier.settle(2)) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for ((key, label) in listOf("recharge" to "Recharge", "explore" to "Explore", "either" to "Either")) {
                    Chip(label, mood == key, Modifier.weight(1f)) { mood = if (mood == key) null else key }
                }
            }
        }
        SurveyQuestion(text?.companyPrompt ?: "Who might come?", Modifier.settle(3)) {
            Grid2(listOf("solo" to "Just me", "friends" to "Friends", "partner" to "A partner", "family" to "Family"), 8) { (key, label) ->
                Chip(label, company == key, Modifier.fillMaxWidth()) { company = if (company == key) null else key }
            }
        }
        SurveyQuestion(text?.wishPrompt ?: "Anything you'd want in it for sure? (optional)") {
            LineField("A place, a kind of food, a view…", wish, { wish = it })
        }
    }
}

/** Screen 19: the two plans, one at a time, in the same format; then the gut choice, "fits me" for each, and why. */
@Composable
fun PairCompare(model: AppModel, pair: PairResponse) {
    val text = model.onboarding?.testb
    var showing by remember { mutableStateOf("1") }
    var seen by remember { mutableStateOf(setOf("1")) }
    var chosen by remember { mutableStateOf<String?>(null) }
    var fit1 by remember { mutableStateOf<Int?>(null) }
    var fit2 by remember { mutableStateOf<Int?>(null) }
    var why by remember { mutableStateOf("") }
    val scroll = rememberScrollState()
    val scope = rememberCoroutineScope()
    val ready = chosen != null && fit1 != null && fit2 != null

    fun show(label: String) {
        showing = label
        seen = seen + label
        scope.launch { scroll.animateScrollTo(0) }
    }

    Column(Modifier.fillMaxSize().imePadding()) {
        Column(
            Modifier.weight(1f).verticalScroll(scroll).padding(horizontal = 24.dp).padding(top = 8.dp, bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp),
        ) {
            Eyebrow(pair.title)
            PageTitle("Plan 1 or Plan 2?")
            (pair.intro ?: text?.intro)?.let { Text(it, style = Theme.body.copy(color = Theme.inkSoft)) }
            // the switch
            Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(13.dp)).background(Theme.surface).padding(3.dp)) {
                for (label in listOf("1", "2")) {
                    Box(
                        Modifier.weight(1f).heightIn(min = 44.dp).clip(RoundedCornerShape(10.dp))
                            .background(if (showing == label) Theme.surfaceHigh else Color.Transparent)
                            .clickable { show(label) }.semantics { selected = showing == label },
                        contentAlignment = Alignment.Center,
                    ) { Text("Plan $label", style = Theme.subheadline.copy(fontWeight = FontWeight.Medium)) }
                }
            }
            AnimatedContent(showing, transitionSpec = { fadeIn() togetherWith fadeOut() }, label = "plan") { label ->
                pair.plans.firstOrNull { it.label == label }?.let { PairPlanText(it) }
            }
            if (showing == "1") SecondaryButton("Now read Plan 2") { show("2") }
            if (seen.size == 2) {
                Box(Modifier.fillMaxWidth().height(1.dp).background(Theme.hairline))
                SurveyQuestion(text?.choosePrompt ?: "Which would you rather do? Go with your gut.") {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Chip("Plan 1", chosen == "1", Modifier.weight(1f)) { chosen = "1" }
                        Chip("Plan 2", chosen == "2", Modifier.weight(1f)) { chosen = "2" }
                    }
                }
                SurveyQuestion(fitText(text?.fitPrompt, "1")) {
                    ScaleRow("not at all", "completely", fit1) { fit1 = it }
                }
                SurveyQuestion(fitText(text?.fitPrompt, "2")) {
                    ScaleRow("not at all", "completely", fit2) { fit2 = it }
                }
                SurveyQuestion(text?.whyPrompt ?: "Why? (optional)") {
                    AnswerBox(why, { why = it }, "Why", minHeight = 90)
                }
            } else {
                Text("Read both plans, then choose.", style = Theme.footnote)
            }
        }
        if (seen.size == 2) {
            Box(Modifier.fillMaxWidth().background(Theme.background).padding(horizontal = 24.dp, vertical = 8.dp)) {
                PrimaryButton(if (model.busy) "Sending…" else "Send", enabled = ready && !model.busy) {
                    val c = chosen ?: return@PrimaryButton
                    model.sendPairFeedback(c, fit1 ?: return@PrimaryButton, fit2 ?: return@PrimaryButton, why, false)
                }
            }
        }
    }
}

/** One plan of the pair, as plain text: its summary, then each stop's times, title and lines (the Test B format). */
@Composable
fun PairPlanText(plan: PairPlan) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            for (line in plan.summary) Text(line, style = Theme.subheadline.copy(color = Theme.inkSoft))
        }
        plan.stops.forEachIndexed { i, stop ->
            Column(Modifier.surfaceCard(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("${i + 1}. ${stop.arrive}–${stop.depart}", style = Theme.subheadline.copy(color = Theme.muted))
                Text(stop.title, style = Theme.title3)
                for (line in stop.lines ?: emptyList()) Text(line, style = Theme.subheadline.copy(color = Theme.inkSoft))
            }
        }
    }
}

/** After the choice: which plan was made from their answers, and on to the plan they chose. */
@Composable
fun PairReveal(model: AppModel, pair: PairResponse) {
    ScrollPage(spacing = 20, top = 40, bottom = 16) {
        ArchGlyph(width = 30.dp)
        Eyebrow("Thank you")
        (pair.reveal ?: emptyList()).forEachIndexed { i, line ->
            Text(line, style = if (i == 0) Theme.title2 else Theme.body.copy(color = Theme.inkSoft), modifier = Modifier.settle(i))
        }
        Spacer(Modifier.height(24.dp))
        PrimaryButton("See your plan") { model.finishPair() }
    }
}

/** 19 Oct review: "Plan 1 fits me", the same statement (Test B's item) with the plan named in it. */
fun fitText(prompt: String?, n: String): String {
    val p = prompt ?: "This plan fits me"
    return if ("This plan" in p) p.replace("This plan", "Plan $n") else "$p: Plan $n"
}
