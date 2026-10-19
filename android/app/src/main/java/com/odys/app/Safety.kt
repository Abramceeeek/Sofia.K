package com.odys.app

import android.Manifest
import android.content.Intent
import android.net.Uri
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.LocalHospital
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
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
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.core.app.NotificationManagerCompat
import kotlinx.coroutines.launch

// Screens 13 and 14: Help & safety, and your data (app/Sources/SafetyAndSettingsViews.swift).

/** Opens the phone's dialler with a number (never calls by itself). */
fun dial(context: android.content.Context, number: String) {
    runCatching {
        context.startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$number")).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
    }
}

/**
 * Screen 13. Safety always goes to a person (D46). The reply never promises anything faster than "a few hours". D110:
 * "Emergency: call 999" and "I feel unsafe or something's wrong" are two separate cards, so nobody mistakes telling us
 * for calling for help. D119: the emergency card is the one red thing in the app. `prefill` starts the message (a stop
 * card's "Something wrong with this place?").
 */
@Composable
fun SafetyView(model: AppModel, prefill: String = "", onClose: () -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var message by remember { mutableStateOf(prefill) }
    var contact by remember { mutableStateOf("") }
    var reply by remember { mutableStateOf<String?>(null) }
    var showSettings by remember { mutableStateOf(false) }
    LaunchedEffect(Unit) {
        model.loadSafety()
        model.markSafetySeen()
    }
    FullSheet(model, onClose) {
        Column(Modifier.fillMaxSize().imePadding()) {
            SheetBar(onClose = onClose)
            ScrollPage(spacing = 18, top = 0, bottom = 24) {
                PageTitle("Help & safety")
                Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(20.dp)).background(Theme.emergencyBg)
                    .border(1.dp, Theme.emergencyBorder, RoundedCornerShape(20.dp)).padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Emergency", style = Theme.headline.copy(color = Theme.emergencyTitle))
                    Text("If you or someone else is in danger or hurt, call 999 now.", style = Theme.body.copy(color = Theme.emergencyText))
                    Pill("Call 999", PillKind.Danger, height = 54.dp, icon = Icons.Filled.Phone) { dial(context, "999") }
                    // D123: urgent medical help that isn't an emergency (nhs.uk: "call 111 and ask for an interpreter")
                    Text("Urgent medical help that isn't an emergency: call NHS 111. You can ask for an interpreter.",
                        style = Theme.subheadline.copy(color = Theme.emergencyText), modifier = Modifier.padding(top = 4.dp))
                    Pill("Call 111", PillKind.Secondary, height = 48.dp, icon = Icons.Filled.LocalHospital) { dial(context, "111") }
                }
                Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(20.dp)).background(Theme.surface).padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("I feel unsafe or something's wrong", style = Theme.headline)
                    Text("This reaches a real person, not a bot: Abram, or whoever is covering for him. They'll reply within a few hours, here in Help & safety.",
                        style = Theme.subheadline.copy(color = Theme.inkTertiary))
                    val sent = reply
                    if (sent != null) {
                        Text(sent, style = Theme.subheadline.copy(color = Theme.inkSoft),
                            modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(Theme.background).padding(14.dp))
                    } else {
                        val shape = RoundedCornerShape(14.dp)
                        BasicTextField(message, { message = it }, textStyle = Theme.body, cursorBrush = SolidColor(Theme.accent),
                            keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.Sentences),
                            modifier = Modifier.fillMaxWidth().heightIn(min = 96.dp).clip(shape).background(Theme.background)
                                .border(1.dp, Theme.outline, shape).padding(14.dp),
                            decorationBox = { inner ->
                                Box {
                                    if (message.isEmpty()) Text("What's happening? (optional)", style = Theme.body.copy(color = Theme.muted))
                                    inner()
                                }
                            })
                        // D118: so a reply can reach you even if you don't open the app again
                        LineField("Phone or email (optional)", contact, onChange = { contact = it },
                            keyboard = KeyboardOptions(keyboardType = KeyboardType.Email, autoCorrectEnabled = false))
                        Text("Used only to reply to this message, and deleted once it's sorted (after 30 days at the latest).",
                            style = Theme.footnote)
                        SecondaryButton(if (model.busy) "Sending…" else "Send to a person", enabled = !model.busy) {
                            val c = contact.trim()
                            scope.launch { reply = model.sendSafety(message, if (c.isEmpty()) null else c.take(120)) }
                        }
                    }
                }
                if (model.safetyThreads.isNotEmpty()) {   // D118: what the person sent, and each reply
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Text("Your messages", style = Theme.subheadline.copy(color = Theme.muted))
                        for (t in model.safetyThreads) {
                            Column(Modifier.surfaceCard(padding = 18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                                Text(t.message.ifEmpty { "(No message, just a call for help)" }, style = Theme.body)
                                if (t.replies.isEmpty()) {
                                    Text("No reply yet. A person replies within a few hours. In an emergency, call 999.", style = Theme.footnote)
                                }
                                for (r in t.replies) {
                                    Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(Theme.selected).padding(14.dp),
                                        verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                        Eyebrow("Reply", color = Theme.accent)
                                        Text(r.text, style = Theme.body)
                                    }
                                }
                            }
                        }
                    }
                }
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("Something else?", style = Theme.subheadline.copy(color = Theme.muted))
                    SelectionContainer { Text("Email ${AppConfig.CONTACT_EMAIL}", style = Theme.body) }
                }
                QuietButton("Your data · what's stored and how to delete it", Modifier.fillMaxWidth()) { showSettings = true }
            }
        }
    }
    if (showSettings) SettingsView(model) { showSettings = false }
}

/** Screen 14: what we store, and Delete my data (UK GDPR erasure). */
@Composable
fun SettingsView(model: AppModel, onClose: () -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var confirmDelete by remember { mutableStateOf(false) }
    val askLocation = rememberLocationAsk(model)
    val askNotifications = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        scope.launch { model.answerReminders(true, granted) }
    }
    FullSheet(model, onClose) {
        Column(Modifier.fillMaxSize()) {
            SheetBar("Your data", onClose = onClose)
            ScrollPage(spacing = 18, top = 4, bottom = 32) {
                SettingsSection("What we store") {
                    Text("Your answers, your reactions to places, your choices between example days, anything you add under \"Improve future plans\", the short survey and your choice between two plans, your plans and your ratings, and anything you send in Help & safety. Your location is never stored. Your trips stay on this phone; the days planned for them are kept like any plan, starting from your stay's location (never its name). Flight and stay searches go to our search providers, and we keep only which filters you used. We don't ask for your name, email or phone number: the app knows this phone only by a random code. If you leave a phone or email in Help & safety, it's used only to reply, then deleted.",
                        style = Theme.body)
                }
                SettingsSection("Reminders", "Set on your phone for the day of your plan. Nothing is sent.") {
                    // D118: rating reminders can be turned off (or on) here, any time
                    SettingSwitch("Rating reminders after each stop", model.remindersOn) { on ->
                        if (!on) scope.launch { model.turnRemindersOff() }
                        else {
                            val enabled = NotificationManagerCompat.from(context).areNotificationsEnabled()
                            if (Build.VERSION.SDK_INT >= 33 && !enabled) askNotifications.launch(Manifest.permission.POST_NOTIFICATIONS)
                            else scope.launch { model.answerReminders(true, enabled) }
                        }
                    }
                }
                SettingsSection("Location", "Only while \"Now\" or \"Plan a day\" is open: how far your next stop is, and asking how it felt once you've left. It stays on your phone, except a start point you choose for a plan, sent rounded to about 100 m and not kept.") {
                    // D123: location while you're out, on the phone only
                    SettingSwitch("Use my location while I'm out", model.location.wanted) { on ->
                        if (on) askLocation() else model.location.turnOff()
                        scope.launch { model.client.event(if (on) "location_on" else "location_off") }
                    }
                    if (model.location.wanted && model.location.deniedBySettings) {
                        Text("Location is off for ODYS in your phone's Settings, so the app can't use it.", style = Theme.footnote)
                    }
                }
                SettingsSection("Where, and for how long") {
                    Text("On our server in Frankfurt, in the EU, until 31 March 2027.", style = Theme.body)
                }
                SettingsSection("About this test") {
                    Text("A person, Abram, runs this test in London. No AI service reads your answers in this version. Contact: ${AppConfig.CONTACT_EMAIL}",
                        style = Theme.body)
                    Text("Full privacy notice", style = Theme.body.copy(color = Theme.accent),
                        modifier = Modifier.heightIn(min = 44.dp).padding(top = 12.dp)
                            .clickable(role = Role.Button) { openUrl(context, AppConfig.BASE_URL.trimEnd('/') + "/privacy") })
                }
                SettingsSection(null, "This removes everything we hold about this phone, straight away. It can't be undone.") {
                    Text("Delete my data", style = Theme.body.copy(color = Theme.danger, fontWeight = FontWeight.SemiBold),
                        modifier = Modifier.fillMaxWidth().heightIn(min = 44.dp).padding(top = 10.dp)
                            .clickable(role = Role.Button) { confirmDelete = true })
                }
                Text("ODYS for Android, version ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})", style = Theme.footnote)
                // Stage 1: the credits the data's licences ask for
                Text("Journey times: Powered by TfL Open Data. Weather: Met Office. Maps: © OpenStreetMap contributors. " +
                    "Card photos: Wikimedia Commons, credited on each card.", style = Theme.footnote)
            }
        }
    }
    if (confirmDelete) DeleteConfirmView(model, { confirmDelete = false }) { onClose() }
}

@Composable
private fun SettingsSection(title: String?, footer: String? = null, content: @Composable () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        if (title != null) Text(title.uppercase(), style = Theme.footnote, modifier = Modifier.padding(start = 4.dp))
        Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(Theme.surface).padding(horizontal = 16.dp, vertical = 12.dp)) {
            content()
        }
        if (footer != null) Text(footer, style = Theme.footnote, modifier = Modifier.padding(horizontal = 4.dp))
    }
}

@Composable
private fun SettingSwitch(label: String, on: Boolean, onChange: (Boolean) -> Unit) {
    Row(Modifier.fillMaxWidth().heightIn(min = 44.dp).clickable(role = Role.Switch) { onChange(!on) },
        verticalAlignment = Alignment.CenterVertically) {
        Text(label, style = Theme.body, modifier = Modifier.weight(1f).padding(end = 12.dp))
        Switch(on, onChange, colors = SwitchDefaults.colors(checkedTrackColor = Theme.accent, checkedThumbColor = Theme.onAccent))
    }
}

/** D110: deleting needs a deliberate step: type DELETE. */
@Composable
fun DeleteConfirmView(model: AppModel, onCancel: () -> Unit, onDeleted: () -> Unit) {
    val scope = rememberCoroutineScope()
    var typed by remember { mutableStateOf("") }
    val confirmed = typed.trim().uppercase() == "DELETE"
    FullSheet(model, onCancel) {
        Column(Modifier.fillMaxSize().imePadding()) {
            SheetBar("Delete my data", close = "Cancel", onClose = onCancel)
            ScrollPage(spacing = 18, top = 4) {
                SettingsSection(null) {
                    Text("This removes everything we hold about this phone: your answers, reactions, choices, plans and ratings. It happens straight away and can't be undone.",
                        style = Theme.body)
                }
                SettingsSection("To confirm, type DELETE") {
                    LineField("DELETE", typed, onChange = { typed = it },
                        keyboard = KeyboardOptions(capitalization = KeyboardCapitalization.Characters, autoCorrectEnabled = false))
                }
                Pill(if (model.busy) "Deleting…" else "Delete my data", PillKind.Danger, enabled = confirmed && !model.busy) {
                    scope.launch {
                        model.deleteMyData()
                        if (model.errorMessage == null) {
                            onCancel()
                            onDeleted()
                        }
                    }
                }
            }
        }
    }
}
