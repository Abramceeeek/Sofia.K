package com.odys.app

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
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
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import kotlinx.serialization.Serializable

// m320 (Abram, 21 Nov: "Seville in the app, me only"): a place ODYS doesn't fully support, shown read-only to a phone
// that typed the preview's code on You. As app/Sources/PreviewViews.swift; nothing is planned, booked or searched
// (brain/src/brain/preview.py).

@Serializable
data class PreviewInfo(
    val key: String,
    val name: String,
    val country: String,
    val countryName: String,
    val label: String,
    val emergencyNumber: String? = null,
)

@Serializable
data class PreviewList(val previews: List<PreviewInfo> = emptyList())

@Serializable
data class PreviewCode(val code: String)

@Serializable
data class PreviewDay(val date: String, val label: String)

@Serializable
data class PreviewEmergency(val number: String, val line: String, val source: String, val checked: String? = null)

@Serializable
data class PreviewPlace(
    val id: String,
    val name: String,
    val title: String,
    val kind: String,
    val category: String,
    val district: String? = null,
    val lat: Double,
    val lon: Double,
    val hours: String,
    val hoursSource: String? = null,
    val hoursRead: String? = null,
    val states: List<String> = emptyList(),
    val price: String,
    val access: String,
    val notices: List<String> = emptyList(),
)

@Serializable
data class PreviewContent(
    val key: String,
    val name: String,
    val countryName: String,
    val label: String,
    val caveat: String,
    val read: String? = null,
    val days: List<PreviewDay> = emptyList(),
    val emergency: PreviewEmergency? = null,
    val places: List<PreviewPlace> = emptyList(),
    val airport: List<String> = emptyList(),
    val airportSource: String? = null,
    val notCovered: List<String> = emptyList(),
)

/** "Sun 22 Nov" style dates from the Brain's ISO day ("2026-11-20" → "20 Nov 2026"). */
private fun readOn(iso: String?): String? = runCatching {
    val d = java.time.LocalDate.parse(iso)
    "${d.dayOfMonth} ${d.month.getDisplayName(java.time.format.TextStyle.SHORT, java.util.Locale.UK)} ${d.year}"
}.getOrNull()

/** A preview of one place: opened from You, from "Where are you going?", or in the screen tests. */
@Composable
fun PreviewScreen(model: AppModel, key: String, onClose: () -> Unit) {
    val context = LocalContext.current
    var content by remember { mutableStateOf(model.previewDemo) }
    var failed by remember { mutableStateOf(false) }
    var day by remember { mutableIntStateOf(0) }
    var attempt by remember { mutableIntStateOf(0) }
    LaunchedEffect(attempt) {
        if (content == null) {
            failed = false
            val got = runCatching { model.client.preview(key) }.getOrNull()
            if (got == null) failed = true else content = got
        }
    }
    FullSheet(model, onClose) {
        Column(Modifier.fillMaxSize()) {
            SheetBar(onClose = onClose)
            ScrollPage(spacing = 18, top = 0, bottom = 32) {
                val c = content
                when {
                    c != null -> {
                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Eyebrow(c.label)
                            PageTitle(c.name)
                            Text(c.caveat, style = Theme.subheadline.copy(color = Theme.inkTertiary))
                        }
                        c.emergency?.let { e ->
                            Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(20.dp)).background(Theme.emergencyBg)
                                .border(1.dp, Theme.emergencyBorder, RoundedCornerShape(20.dp)).padding(18.dp),
                                verticalArrangement = Arrangement.spacedBy(12.dp)) {
                                Text("Emergency in ${c.countryName}", style = Theme.headline.copy(color = Theme.emergencyTitle))
                                Text(e.line, style = Theme.body.copy(color = Theme.emergencyText))
                                Pill("Call ${e.number}", PillKind.Danger, height = 54.dp, icon = Icons.Filled.Phone) {
                                    dial(context, e.number)
                                }
                                Text("999 is the UK's number. In ${c.countryName}, call ${e.number}.",
                                    style = Theme.footnote.copy(color = Theme.emergencyText))
                            }
                        }
                        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                c.days.forEachIndexed { i, d ->
                                    val on = i == day
                                    Box(Modifier.heightIn(min = 44.dp).clip(CircleShape)
                                        .background(if (on) Theme.surfaceHigh else Theme.surface)
                                        .clickable(role = Role.Tab) { day = i }.semantics { selected = on }
                                        .padding(horizontal = 14.dp), contentAlignment = Alignment.Center) {
                                        Text(d.label, style = Theme.subheadline.copy(color = if (on) Theme.ink else Theme.muted,
                                            fontWeight = if (on) FontWeight.SemiBold else FontWeight.Normal))
                                    }
                                }
                            }
                            Text("Open: the venue's own page lists this day. Check: probably open, but check before you go. Shut: closed that day.",
                                style = Theme.footnote)
                        }
                        for (kind in c.places.map { it.kind }.distinct()) {
                            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                                SectionLabel(kind)
                                for (p in c.places.filter { it.kind == kind }) PreviewPlaceCard(p, p.states.getOrElse(day) { "check" })
                            }
                        }
                        if (c.airport.isNotEmpty()) {
                            Column(Modifier.fillMaxWidth().surfaceCard(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                SectionLabel("From the airport")
                                for (line in c.airport) Text(line, style = Theme.subheadline.copy(color = Theme.inkSoft))
                                c.airportSource?.let { Text("Source: $it", style = Theme.footnote) }
                            }
                        }
                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            SectionLabel("Not covered here")
                            for (line in c.notCovered) Text(line, style = Theme.subheadline.copy(color = Theme.inkSoft))
                            readOn(c.read)?.let { Text("Read from official pages on $it.", style = Theme.footnote) }
                        }
                    }
                    failed -> {
                        PageTitle("Preview")
                        Text("The preview couldn't be loaded just now. Check your signal, then try again.",
                            style = Theme.body.copy(color = Theme.inkSoft))
                        SecondaryButton("Try again") { attempt++ }
                    }
                    else -> Box(Modifier.fillMaxWidth().heightIn(min = 200.dp), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(color = Theme.accent)
                    }
                }
            }
        }
    }
}

@Composable
fun PreviewPlaceCard(place: PreviewPlace, state: String) {
    val context = LocalContext.current
    val (word, ink, fill) = when (state) {
        "open" -> Triple("Open", Theme.okInk, Theme.okBg)
        "shut" -> Triple("Shut", Theme.warnInk, Theme.warnBg)
        else -> Triple("Check", Theme.amberDeep, Theme.savedBg)
    }
    Column(Modifier.fillMaxWidth().alpha(if (state == "shut") 0.72f else 1f).clip(RoundedCornerShape(18.dp))
        .background(Theme.surface).padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(verticalAlignment = Alignment.Top) {
            Text(place.name, style = Theme.headline, modifier = Modifier.weight(1f).padding(end = 8.dp))
            Text(word, style = Theme.caption.copy(color = ink, fontWeight = FontWeight.SemiBold),
                modifier = Modifier.clip(CircleShape).background(fill).padding(horizontal = 8.dp, vertical = 3.dp))
        }
        Text(place.title, style = Theme.subheadline.copy(color = Theme.inkSoft))
        place.district?.let { Text(it, style = Theme.footnote) }
        Text(place.hours, style = Theme.subheadline)
        Text("${place.price} · ${place.access}", style = Theme.footnote.copy(color = Theme.inkTertiary))
        for (n in place.notices) Text(n, style = Theme.footnote.copy(color = Theme.warnInk))
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            place.hoursSource?.let { src ->
                QuietButton("The venue's page", color = Theme.accent) { openUrl(context, src) }
            }
            // Google Maps, walking, to the place's point (nothing about the person is sent)
            QuietButton("Directions", color = Theme.accent) {
                openUrl(context, "https://www.google.com/maps/dir/?api=1&destination=${place.lat},${place.lon}&travelmode=walking")
            }
            Box(Modifier.weight(1f))
            readOn(place.hoursRead)?.let { Text("read $it", style = Theme.footnote) }
        }
    }
}

/** On You: the previews this phone has opened, and "Got a preview code?". */
@Composable
fun PreviewSection(model: AppModel) {
    val scope = rememberCoroutineScope()
    var askCode by remember { mutableStateOf(false) }
    var message by remember { mutableStateOf<String?>(null) }
    var open by remember { mutableStateOf<PreviewInfo?>(null) }
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        if (model.previews.isNotEmpty()) {
            SectionLabel("Previews")
            for (p in model.previews) {
                Row(Modifier.pressable(onClick = { open = p }).surfaceCard(padding = 18.dp, radius = 20.dp),
                    verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(p.name, style = Theme.headline)
                        Text("${p.label}. Places and opening days only.", style = Theme.subheadline.copy(color = Theme.inkTertiary))
                    }
                    Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = Theme.muted)
                }
            }
        }
        QuietButton("Got a preview code?") { askCode = true }
        message?.let { Text(it, style = Theme.footnote) }
    }
    if (askCode) {
        var code by remember { mutableStateOf("") }
        AlertDialog(
            onDismissRequest = { askCode = false },
            title = { Text("Preview code", style = Theme.headline) },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("A code opens a preview of a place ODYS doesn't fully support yet.",
                        style = Theme.subheadline.copy(color = Theme.inkSoft))
                    OutlinedTextField(code, { code = it.uppercase() }, singleLine = true, label = { Text("Code") },
                        keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.Characters, autoCorrect = false),
                        colors = odysFieldColors())
                }
            },
            confirmButton = {
                TextButton({ askCode = false; scope.launch { message = model.openPreview(code) } }) {
                    Text("Open", color = Theme.accent)
                }
            },
            dismissButton = { TextButton({ askCode = false }) { Text("Cancel", color = Theme.inkSoft) } },
            containerColor = Theme.surfaceHigh,
        )
    }
    open?.let { p -> PreviewScreen(model, p.key) { open = null } }
}

/** "Where are you going?": a preview this phone has opened, under London. It opens the preview, not a trip. */
@Composable
fun PreviewCityLines(model: AppModel) {
    var open by remember { mutableStateOf<PreviewInfo?>(null) }
    for (p in model.previews) {
        Box(Modifier.clickable(role = Role.Button) { open = p }) { CityLine(p.name, "Preview: places only", true) }
    }
    open?.let { p -> PreviewScreen(model, p.key) { open = null } }
}

/** Help & safety: the emergency number of each country this phone has a preview for (Spain: 112), under 999. */
@Composable
fun PreviewEmergencyLines(model: AppModel) {
    val context = LocalContext.current
    for (p in model.previews) {
        val n = p.emergencyNumber ?: continue
        if (n == "999") continue
        Pill("In ${p.countryName}: call $n", PillKind.Secondary, height = 48.dp, icon = Icons.Filled.Phone) { dial(context, n) }
    }
}
