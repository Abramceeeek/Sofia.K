package com.odys.app

import android.provider.Settings
import android.view.HapticFeedbackConstants
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowLeft
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.clipRect
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.min

// D119: the ODYS parts every screen is built from: the arch, buttons, tiles, the eyebrow, and the motion vocabulary
// (app/Sources/Odys.swift). Rules: a response to a tap finishes within 300 ms; ease, never bounce; nothing makes you
// wait for it; with the phone's animations turned off, things fade or are simply there.

/** Android's "Remove animations" (animator scale 0) stands in for iOS's Reduce Motion. */
@Composable
fun rememberReduceMotion(): Boolean {
    val context = LocalContext.current
    return remember {
        Settings.Global.getFloat(context.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f
    }
}

@Composable
fun rememberHaptic(): () -> Unit {
    val view = LocalView.current
    return { view.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP) }
}

/** Press (120 ms): scale .97. */
@Composable
fun Modifier.pressable(
    enabled: Boolean = true,
    role: Role = Role.Button,
    haptic: Boolean = false,
    onClick: () -> Unit,
): Modifier {
    val source = remember { MutableInteractionSource() }
    val pressed by source.collectIsPressedAsState()
    val reduce = rememberReduceMotion()
    val scale by animateFloatAsState(if (pressed && !reduce) 0.97f else 1f, Motion.press(), label = "press")
    val tick = rememberHaptic()
    return this
        .scale(scale)
        .clickable(source, indication = null, enabled = enabled, role = role) {
            if (haptic) tick()
            onClick()
        }
}

// ---- buttons ------------------------------------------------------------------------------------------------

enum class PillKind { Primary, Secondary, Danger }

@Composable
fun Pill(
    title: String,
    kind: PillKind,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    height: Dp = if (kind == PillKind.Primary) 56.dp else 52.dp,
    icon: ImageVector? = null,
    onClick: () -> Unit,
) {
    val source = remember { MutableInteractionSource() }
    val pressed by source.collectIsPressedAsState()
    val reduce = rememberReduceMotion()
    val scale by animateFloatAsState(if (pressed && !reduce) 0.97f else 1f, Motion.press(), label = "pill")
    val tick = rememberHaptic()
    val fill = when {
        !enabled -> if (kind == PillKind.Secondary) Color.Transparent else Theme.surfaceHigh
        kind == PillKind.Primary -> if (pressed) Theme.amberDeep else Theme.accent
        kind == PillKind.Secondary -> if (pressed) Theme.surface else Color.Transparent
        else -> if (pressed) Theme.danger.copy(alpha = 0.85f) else Theme.danger
    }
    val fg = when {
        !enabled -> Theme.muted
        kind == PillKind.Primary -> Theme.onAccent
        kind == PillKind.Secondary -> Theme.ink
        else -> Color.White
    }
    Row(
        modifier
            .fillMaxWidth()
            .scale(scale)
            .heightIn(min = height)
            .clip(CircleShape)
            .background(fill)
            .then(if (kind == PillKind.Secondary) Modifier.border(1.dp, Theme.outlineStrong, CircleShape) else Modifier)
            .clickable(source, indication = null, enabled = enabled, role = Role.Button) {
                tick()
                onClick()
            }
            .padding(horizontal = 20.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (icon != null) {
            Icon(icon, contentDescription = null, tint = fg, modifier = Modifier.size(20.dp))
            Spacer(Modifier.width(8.dp))
        }
        Text(
            title,
            style = if (kind == PillKind.Secondary) Theme.body.copy(color = fg) else Theme.headline.copy(color = fg),
            textAlign = TextAlign.Center,
        )
    }
}

/** The main action at the bottom of a screen: an amber pill, 56 dp, with a light haptic. */
@Composable
fun PrimaryButton(title: String, modifier: Modifier = Modifier, enabled: Boolean = true, onClick: () -> Unit) =
    Pill(title, PillKind.Primary, modifier, enabled, onClick = onClick)

/** Every other action: an outlined pill, 52 dp. */
@Composable
fun SecondaryButton(
    title: String,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null,
    enabled: Boolean = true,
    onClick: () -> Unit,
) = Pill(title, PillKind.Secondary, modifier, enabled, icon = icon, onClick = onClick)

/** A quiet text button: skipping, going back, opting out. Never louder than the main action (D118). */
@Composable
fun QuietButton(
    title: String,
    modifier: Modifier = Modifier,
    color: Color = Theme.muted,
    enabled: Boolean = true,
    onClick: () -> Unit,
) {
    Box(
        modifier
            .heightIn(min = 44.dp)
            .clickable(enabled = enabled, role = Role.Button, onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Text(title, style = Theme.subheadline.copy(color = if (enabled) color else color.copy(alpha = 0.5f)),
            textAlign = TextAlign.Center)
    }
}

/** Back, for screens without a bar: Android's arrow (19 Oct review: "‹ Back" is the iPhone's way); the word is
 *  kept for TalkBack. 48 dp. */
@Composable
fun BackLink(title: String = "Back", onClick: () -> Unit) {
    Box(
        Modifier
            .size(48.dp)
            .clip(CircleShape)
            .clickable(role = Role.Button, onClick = onClick)
            .semantics { contentDescription = title },
        contentAlignment = Alignment.Center,
    ) {
        Icon(Icons.AutoMirrored.Filled.ArrowBack, null, tint = Theme.accent, modifier = Modifier.size(24.dp))
    }
}

/** An arrow and where it goes ("Your trip"), for a way back that leaves the tab. */
@Composable
fun ArrowLink(title: String, onClick: () -> Unit) {
    Row(Modifier.heightIn(min = 48.dp).clickable(role = Role.Button, onClick = onClick),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        Icon(Icons.AutoMirrored.Filled.ArrowBack, null, tint = Theme.accent, modifier = Modifier.size(20.dp))
        Text(title, style = Theme.body.copy(color = Theme.accent))
    }
}

/** Close or Cancel, top of a full-screen sheet: Android's ✕ (19 Oct review); any other word stays a word. */
@Composable
fun CloseLink(title: String = "Close", onClick: () -> Unit) {
    if (title == "Close" || title == "Cancel") {
        Box(Modifier.size(48.dp).clip(CircleShape).clickable(role = Role.Button, onClick = onClick)
            .semantics { contentDescription = title }, contentAlignment = Alignment.Center) {
            Icon(Icons.Filled.Close, null, tint = Theme.accent, modifier = Modifier.size(24.dp))
        }
    } else {
        Box(Modifier.heightIn(min = 48.dp).clickable(role = Role.Button, onClick = onClick), contentAlignment = Alignment.Center) {
            Text(title, style = Theme.body.copy(color = Theme.accent))
        }
    }
}

/** "Help" in a pill, on every main screen; a dot when a person has replied (D118). */
@Composable
fun HelpPill(unread: Boolean, onClick: () -> Unit) {
    Box(
        Modifier
            .heightIn(min = 44.dp)
            .pressable(onClick = onClick)
            .semantics { contentDescription = if (unread) "Help and safety, new reply" else "Help and safety" },
        contentAlignment = Alignment.Center,
    ) {
        Box {
            Text(
                "Help",
                style = Theme.subheadline,
                modifier = Modifier
                    .border(1.dp, Theme.outlineStrong, CircleShape)
                    .padding(horizontal = 14.dp, vertical = 8.dp),
            )
            if (unread) {
                Box(Modifier.align(Alignment.TopEnd).offset(x = 2.dp, y = (-2).dp).size(9.dp)
                    .background(Theme.danger, CircleShape))
            }
        }
    }
}

/** The top of a main screen: an eyebrow, then Help and "Your data". */
@Composable
fun TopBar(eyebrow: String, unread: Boolean, onHelp: (() -> Unit)?, onData: (() -> Unit)?, onMenu: (() -> Unit)? = null) {
    Row(Modifier.fillMaxWidth().heightIn(min = 44.dp), verticalAlignment = Alignment.CenterVertically) {
        Eyebrow(eyebrow, modifier = Modifier.weight(1f))
        Spacer(Modifier.width(8.dp))
        if (onHelp != null) HelpPill(unread, onHelp)
        if (onMenu != null) {   // D131: the home's menu: You, your data and the light
            Spacer(Modifier.width(6.dp))
            Box(
                Modifier.size(44.dp).pressable(onClick = onMenu).semantics { contentDescription = "You, your data and the light" },
                contentAlignment = Alignment.Center,
            ) {
                Box(Modifier.size(36.dp).border(1.dp, Theme.outlineStrong, CircleShape), contentAlignment = Alignment.Center) {
                    Icon(Icons.Filled.Menu, null, tint = Theme.ink, modifier = Modifier.size(18.dp))
                }
            }
        }
        if (onData != null) {
            Spacer(Modifier.width(6.dp))
            Box(
                Modifier.size(44.dp).pressable(onClick = onData).semantics { contentDescription = "Your data" },
                contentAlignment = Alignment.Center,
            ) {
                Box(Modifier.size(36.dp).border(1.dp, Theme.outlineStrong, CircleShape), contentAlignment = Alignment.Center) {
                    Icon(Icons.Outlined.Settings, null, tint = Theme.ink, modifier = Modifier.size(18.dp))
                }
            }
        }
    }
}

// ---- type ---------------------------------------------------------------------------------------------------

/** The small amber label above a title: 13 sp, uppercase, spaced. */
@Composable
fun Eyebrow(text: String, modifier: Modifier = Modifier, color: Color = Theme.amberDeep) {
    Text(
        text.uppercase(),
        style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium, letterSpacing = 1.sp, color = color),
        modifier = modifier.semantics { contentDescription = text },
    )
}

/** A screen's title in the serif, at the top of its content. */
@Composable
fun PageTitle(text: String, modifier: Modifier = Modifier, style: TextStyle = Theme.h1) {
    Text(text, style = style, modifier = modifier.fillMaxWidth().semantics { heading() })
}

/** The small uppercase label above a section ("1 · GETTING THERE"). */
@Composable
fun SectionLabel(text: String, modifier: Modifier = Modifier) {
    Text(text.uppercase(), style = Theme.footnote.copy(letterSpacing = 0.8.sp), modifier = modifier)
}

/**
 * A question split into its title and the line under it: "How do you most want to feel on a day out?" and
 * "Pick one or two." The Brain sends them as one string.
 */
object PromptText {
    fun split(text: String): Pair<String, String?> {
        val q = text.indexOf('?')
        if (q < 0 || q + 1 >= text.length) return text to null
        val rest = text.substring(q + 1).trim()
        return if (rest.isEmpty()) text to null else text.substring(0, q + 1) to rest
    }
}

/** A little reaction (70 ms a word), in amber italic. Only ever from what the person answered (D117). */
@Composable
fun WordReveal(text: String, modifier: Modifier = Modifier, style: TextStyle = Theme.reaction, color: Color = Theme.accent) {
    val words = remember(text) { text.split(" ").filter { it.isNotEmpty() } }
    val reduce = rememberReduceMotion()
    var shown by androidx.compose.runtime.remember(text) { mutableIntStateOf(if (reduce) words.size else 0) }
    LaunchedEffect(text) {
        if (reduce) {
            shown = words.size
            return@LaunchedEffect
        }
        for (i in 1..maxOf(words.size, 1)) {
            delay(70)
            shown = i
        }
    }
    val line: AnnotatedString = buildAnnotatedString {
        words.forEachIndexed { i, w ->
            withStyle(SpanStyle(color = color.copy(alpha = if (i < shown) 1f else 0f))) {
                append(if (i == 0) w else " $w")
            }
        }
    }
    Text(line, style = style, modifier = modifier.fillMaxWidth().semantics { contentDescription = text })
}

// ---- tiles --------------------------------------------------------------------------------------------------

/** A tile that can be chosen. Select (250 ms): a light sweeps across it, then its border turns amber. */
@Composable
fun SelectTile(
    on: Boolean,
    modifier: Modifier = Modifier,
    radius: Dp = 18.dp,
    minHeight: Dp = 64.dp,
    description: String? = null,
    onClick: () -> Unit,
    content: @Composable BoxScope.() -> Unit,
) {
    val shape = RoundedCornerShape(radius)
    val reduce = rememberReduceMotion()
    val sweep = remember { Animatable(-1f) }
    LaunchedEffect(on) {
        if (on && !reduce) {
            sweep.snapTo(-0.5f)
            sweep.animateTo(1f, tween(250))
        }
    }
    val border by androidx.compose.animation.animateColorAsState(if (on) Theme.accent else Color.Transparent,
        Motion.select(), label = "tile")
    Box(
        modifier
            .fillMaxWidth()
            .heightIn(min = minHeight)
            .pressable(haptic = true, onClick = onClick)
            .semantics {
                selected = on
                if (description != null) contentDescription = description
            }
            .clip(shape)
            .background(if (on) Theme.selected else Theme.surface)
            .drawWithContent {
                drawContent()
                val w = size.width
                val x = sweep.value * w
                drawRect(
                    Brush.horizontalGradient(
                        listOf(Color.Transparent, Theme.accent.copy(alpha = 0.22f), Color.Transparent),
                        startX = x, endX = x + w * 0.5f,
                    ),
                    topLeft = Offset(x, 0f), size = Size(w * 0.5f, size.height),
                )
            }
            .border(1.5.dp, border, shape),
        contentAlignment = Alignment.CenterStart,
        content = content,
    )
}

/** One of several: a ring that fills. */
@Composable
fun RadioDot(on: Boolean) {
    Box(
        Modifier.size(22.dp).border(1.5.dp, if (on) Theme.accent else Theme.outlineStrong, CircleShape),
        contentAlignment = Alignment.Center,
    ) {
        if (on) Box(Modifier.size(12.dp).background(Theme.accent, CircleShape))
    }
}

/** Pick several (D118: squares mean "more than one"). */
@Composable
fun TickBox(on: Boolean) {
    val shape = RoundedCornerShape(6.dp)
    Box(
        Modifier.size(22.dp).clip(shape).background(if (on) Theme.accent else Color.Transparent)
            .border(1.5.dp, if (on) Theme.accent else Theme.outlineStrong, shape),
        contentAlignment = Alignment.Center,
    ) {
        if (on) Icon(Icons.Filled.Check, null, tint = Theme.onAccent, modifier = Modifier.size(16.dp))
    }
}

/** A pill chip: "Today", "Tomorrow"; "Yes", "No". */
@Composable
fun Chip(title: String, on: Boolean, modifier: Modifier = Modifier, height: Dp = 48.dp, onClick: () -> Unit) {
    Box(
        modifier
            .heightIn(min = height)
            .pressable(haptic = true, onClick = onClick)
            .semantics { selected = on }
            .clip(CircleShape)
            .background(if (on) Theme.accent else Color.Transparent)
            .border(1.5.dp, if (on) Theme.accent else Theme.outline, CircleShape)
            .padding(horizontal = 16.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(title, style = Theme.subheadline.copy(fontWeight = FontWeight.Medium,
            color = if (on) Theme.onAccent else Theme.ink), textAlign = TextAlign.Center)
    }
}

/** A tile with a label and a line under it: lengths, feelings, filters. Amber edge when chosen. */
@Composable
fun OptionTile(
    label: String,
    sub: String?,
    on: Boolean,
    modifier: Modifier = Modifier,
    serif: Boolean = false,
    offFill: Color = Color.Transparent,
    offStroke: Color = Theme.outline,
    onClick: () -> Unit,
) {
    val shape = RoundedCornerShape(if (serif) 18.dp else 14.dp)
    Column(
        modifier
            .fillMaxWidth()
            .pressable(haptic = true, onClick = onClick)
            .semantics { selected = on }
            .clip(shape)
            .background(if (on) Theme.selected else offFill)
            .border(1.5.dp, if (on) Theme.accent else offStroke, shape)
            .padding(horizontal = if (serif) 18.dp else 12.dp, vertical = if (serif) 13.dp else 10.dp),
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        Text(label, style = if (serif) Theme.serif(21.sp) else Theme.subheadline)
        if (!sub.isNullOrEmpty()) {
            Text(sub, style = if (serif) Theme.subheadline.copy(color = Theme.inkTertiary) else Theme.caption)
        }
    }
}

/** A one-tap filter: a small outlined pill that warms up when on. */
@Composable
fun FilterChipPill(label: String, on: Boolean, onClick: () -> Unit) {
    Box(Modifier.heightIn(min = 44.dp).pressable(haptic = true, onClick = onClick).semantics { selected = on },
        contentAlignment = Alignment.Center) {
        Text(
            label,
            style = Theme.subheadline,
            maxLines = 1,
            modifier = Modifier
                .clip(CircleShape)
                .background(if (on) Theme.selected else Color.Transparent)
                .border(1.5.dp, if (on) Theme.accent else Theme.outline, CircleShape)
                .padding(horizontal = 14.dp, vertical = 8.dp),
        )
    }
}

/** "To do", "Saved, not booked", "Booked": one coloured label per trip card. */
@Composable
fun StatusLabel(text: String, fill: Color, color: Color) {
    Text(text, style = Theme.footnote.copy(color = color),
        modifier = Modifier.clip(RoundedCornerShape(12.dp)).background(fill).padding(horizontal = 10.dp, vertical = 4.dp))
}

/** A 1–5 scale as five equal tiles. With `labels`, each number carries a word. */
@Composable
fun ScaleRow(low: String, high: String, value: Int?, labels: List<String>? = null, onChange: (Int) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        if (labels != null && labels.size == 5) {
            for (n in 1..5) {
                SelectTile(on = value == n, radius = 16.dp, minHeight = 52.dp, description = "$n of 5, ${labels[n - 1]}",
                    onClick = { onChange(n) }) {
                    Text(labels[n - 1], style = Theme.option, textAlign = TextAlign.Center,
                        modifier = Modifier.fillMaxWidth())
                }
            }
        } else {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for (n in 1..5) {
                    SelectTile(on = value == n, radius = 16.dp, minHeight = 56.dp, description = "$n of 5",
                        modifier = Modifier.weight(1f), onClick = { onChange(n) }) {
                        Text("$n", style = Theme.title3, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())
                    }
                }
            }
            Row {
                Text("1 = $low", style = Theme.footnote, modifier = Modifier.weight(1f))
                Text("5 = $high", style = Theme.footnote)
            }
        }
    }
}

/** A labelled block of text on a card or plan screen. */
@Composable
fun InfoBlock(label: String, text: String) {
    if (text.isEmpty()) return
    Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(label, style = Theme.subheadline.copy(color = Theme.muted))
        Text(text, style = Theme.body)
    }
}

/** Rows of label and text on one card, divided by hairlines. */
@Composable
fun DetailRows(rows: List<Pair<String, String>>) {
    val shown = rows.filter { it.second.isNotEmpty() }
    if (shown.isEmpty()) return
    Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Theme.surface)) {
        shown.forEachIndexed { i, (label, text) ->
            Column(Modifier.fillMaxWidth().padding(horizontal = 18.dp, vertical = 16.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(label, style = Theme.subheadline.copy(color = Theme.muted))
                Text(text, style = Theme.body)
            }
            if (i < shown.size - 1) Box(Modifier.fillMaxWidth().height(1.dp).background(Theme.hairline))
        }
    }
}

/** A rounded card on the surface colour. */
fun Modifier.surfaceCard(padding: Dp = 16.dp, radius: Dp = 18.dp): Modifier =
    this.fillMaxWidth().clip(RoundedCornerShape(radius)).background(Theme.surface).padding(padding)

/** The free server sleeps when nobody has used it for 15 minutes (D109). */
@Composable
fun WakingBanner(modifier: Modifier = Modifier) {
    Row(
        modifier
            .padding(top = 8.dp)
            .clip(CircleShape)
            .background(Theme.surface)
            .border(1.dp, Theme.outline, CircleShape)
            .padding(horizontal = 16.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        androidx.compose.material3.CircularProgressIndicator(Modifier.size(16.dp), color = Theme.accent, strokeWidth = 2.dp)
        Text("Waking up the planner. This can take up to a minute.", style = Theme.footnote.copy(color = Theme.ink))
    }
}

// ---- motion -------------------------------------------------------------------------------------------------

/** Settle (450 ms): content rises 10 dp as it fades in; `order` staggers it by 60 ms. */
@Composable
fun Modifier.settle(order: Int = 0): Modifier {
    val reduce = rememberReduceMotion()
    val p = remember { Animatable(if (reduce) 1f else 0f) }
    LaunchedEffect(Unit) {
        if (p.value < 1f) p.animateTo(1f, Motion.settle(order * 60))
    }
    return this.graphicsLayer {
        alpha = p.value
        translationY = (1f - p.value) * 10.dp.toPx()
    }
}

// ---- the arch -----------------------------------------------------------------------------------------------

/** A doorway: straight sides and a half circle on top, drawn in its own units (the design files' SVG viewBoxes). */
data class Door(val boxW: Float, val boxH: Float, val left: Float, val right: Float, val spring: Float,
                val bottom: Float, val closed: Boolean = true) {
    fun path(size: Size): Path {
        val s = min(size.width / boxW, size.height / boxH)
        val ox = size.width / 2 - boxW * s / 2
        val oy = size.height / 2 - boxH * s / 2
        fun x(v: Float) = ox + v * s
        fun y(v: Float) = oy + v * s
        val r = (right - left) / 2 * s
        val cx = x((left + right) / 2)
        val cy = y(spring)
        return Path().apply {
            moveTo(x(left), y(bottom))
            lineTo(x(left), y(spring))
            arcTo(androidx.compose.ui.geometry.Rect(cx - r, cy - r, cx + r, cy + r), 180f, 180f, false)
            lineTo(x(right), y(bottom))
            if (closed) close()
        }
    }

    companion object {
        val logoLight = Door(180f, 220f, 50f, 130f, 74f, 160f)
        val logoFrame = Door(180f, 220f, 34f, 146f, 70f, 160f, closed = false)
        val rating = Door(120f, 152f, 30f, 90f, 54f, 120f)
        val glyph = Door(14f, 18f, 1f, 13f, 7f, 18f)
    }
}

/** The light spilling onto the ground in front of the door: a trapezoid, in the same units. */
data class Pool(val boxW: Float, val boxH: Float, val top: Float, val topLeft: Float, val topRight: Float,
                val bottom: Float, val bottomLeft: Float, val bottomRight: Float) {
    fun path(size: Size): Path {
        val s = min(size.width / boxW, size.height / boxH)
        val ox = size.width / 2 - boxW * s / 2
        val oy = size.height / 2 - boxH * s / 2
        return Path().apply {
            moveTo(ox + topLeft * s, oy + top * s)
            lineTo(ox + topRight * s, oy + top * s)
            lineTo(ox + bottomRight * s, oy + bottom * s)
            lineTo(ox + bottomLeft * s, oy + bottom * s)
            close()
        }
    }

    companion object {
        val logo = Pool(180f, 220f, 160f, 50f, 130f, 214f, 4f, 176f)
        val rating = Pool(120f, 152f, 121f, 30f, 90f, 150f, 4f, 116f)
    }
}

/** The ODYS mark: a doorway of light in a dark frame, the light spilling out in front, a soft halo behind. */
@Composable
fun ArchLogo(modifier: Modifier = Modifier, light: Float = 1f, pool: Float = 1f, halo: Boolean = true) {
    Canvas(modifier.aspectRatio(180f / 220f)) {
        val s = min(size.width / 180f, size.height / 220f)
        val ox = size.width / 2 - 90 * s
        val oy = size.height / 2 - 110 * s
        if (halo) {
            drawOval(
                Brush.radialGradient(listOf(Theme.accent.copy(alpha = 0.22f * light), Theme.accent.copy(alpha = 0f)),
                    center = Offset(size.width / 2, oy + 0.55f * 220 * s), radius = 100 * s),
                topLeft = Offset(size.width / 2 - 90 * s, size.height / 2 - 100 * s), size = Size(180 * s, 200 * s),
            )
        }
        drawPath(Door.logoFrame.path(size), Theme.line, style = Stroke(width = 10 * s))
        val level = light.coerceIn(0f, 1f)
        val yCut = oy + (160 - level * (160 - 34)) * s
        clipRect(top = yCut) {
            drawPath(
                Door.logoLight.path(size),
                Brush.verticalGradient(listOf(Theme.amberLight, Theme.accent, Theme.amberDeep),
                    startY = oy + 34 * s, endY = oy + 160 * s),
            )
        }
        drawPath(
            Pool.logo.path(size),
            Brush.verticalGradient(listOf(Theme.accent.copy(alpha = 0.55f * pool), Theme.accent.copy(alpha = 0f)),
                startY = oy + 160 * s, endY = oy + 214 * s),
        )
        drawLine(Theme.line, Offset(size.width / 2 - 76 * s, size.height / 2 + 50 * s),
            Offset(size.width / 2 + 76 * s, size.height / 2 + 50 * s), strokeWidth = 2 * s)
        if (ox < 0) return@Canvas
    }
}

/** The small arch, as a bullet and beside "Planned with ODYS". */
@Composable
fun ArchGlyph(color: Color = Theme.accent, width: Dp = 14.dp) {
    Canvas(Modifier.width(width).height(width * 18f / 14f)) {
        drawPath(Door.glyph.path(size), color)
    }
}

/** The "ODYS" wordmark: Newsreader, widely spaced. */
@Composable
fun Wordmark(size: Float = 20f) {
    Text("ODYS", style = Theme.serif(size.sp).copy(letterSpacing = (size * 0.34f).sp),
        modifier = Modifier.padding(start = (size * 0.34f).dp).semantics { contentDescription = "ODYS" })
}

/** Abram's initial, for "run by one person". */
@Composable
fun AbramAvatar(size: Dp = 52.dp) {
    Box(
        Modifier.size(size).clip(CircleShape).background(
            Brush.radialGradient(listOf(Color(0xFF6B5640), Color(0xFF2A231C)))),
        contentAlignment = Alignment.Center,
    ) {
        Text("A", style = Theme.serif((size.value * 0.42f).sp))
    }
}

/** Listen (2.4 s loop): rings while someone speaks. */
@Composable
fun ListenRings(active: Boolean, modifier: Modifier = Modifier) {
    if (!active) return
    val reduce = rememberReduceMotion()
    val t by if (reduce) remember { androidx.compose.runtime.mutableFloatStateOf(0.3f) } else
        rememberInfiniteTransition(label = "listen").animateFloat(0f, 1f,
            infiniteRepeatable(tween(2400, easing = LinearEasing), RepeatMode.Restart), label = "t")
    Canvas(modifier) {
        for (i in 0 until 3) {
            val p = (t + i / 3f) % 1f
            drawCircle(Theme.accent.copy(alpha = 0.55f * (1 - p)), radius = size.minDimension / 2 * (1 + p * 0.9f),
                style = Stroke(1.5.dp.toPx()))
        }
    }
}

/** Breathe (6 s loop): the glow behind the arch on "Now". */
@Composable
fun BreathingArch(showSun: Boolean = false, sunAt: Double? = null /* CI screenshots only */) {
    val reduce = rememberReduceMotion()
    // D130: by day the arch's light takes the sky's colour; on "Now" the sun sits where the real sun is, set once
    val sun = remember(showSun) { if (showSun && Theme.day) sunAt ?: Sun.dayFraction(java.time.Instant.now()) else null }
    val light = if (Theme.day) Theme.skyTop else Theme.accent
    val glow = if (Theme.day) 0.75f else 0.1f
    val t by if (reduce) remember { androidx.compose.runtime.mutableFloatStateOf(0.5f) } else
        rememberInfiniteTransition(label = "breathe").animateFloat(0f, 1f,
            infiniteRepeatable(tween(6000, easing = LinearEasing), RepeatMode.Restart), label = "b")
    val b = if (reduce) 0.5f else ((1 - cos(t * 2 * Math.PI)) / 2).toFloat()
    Box(Modifier.size(160.dp), contentAlignment = Alignment.Center) {
        Canvas(Modifier.size(160.dp).scale(0.94f + 0.06f * b)) {
            drawCircle(Brush.radialGradient(listOf(light.copy(alpha = glow + 0.1f * b),
                light.copy(alpha = 0f)), radius = size.minDimension / 2))
        }
        ArchGlyph(Theme.accent.copy(alpha = 0.62f + 0.18f * b), 40.dp)
        if (sun != null) Canvas(Modifier.size(160.dp)) {
            // sunrise on the left, sunset on the right, over the arch
            val a = Math.PI * (1 - sun)
            val c = Offset(size.width / 2 + 62.dp.toPx() * cos(a).toFloat(), size.height * 0.62f - 62.dp.toPx() * sin(a).toFloat())
            drawCircle(Theme.amberLight.copy(alpha = 0.5f), 11.dp.toPx(), c)
            drawCircle(Theme.accent, 6.dp.toPx(), c)
        }
    }
}

// ---- pictures -----------------------------------------------------------------------------------------------

/** A field of colour standing in for a photo, one per kind of moment. */
fun fieldBrush(feel: String?): Brush {
    if (feel == "Drifting" || feel == "Big views") {
        return Brush.verticalGradient(0f to Color(0xFF22304A), 0.4f to Color(0xFF4A5C78), 0.6f to Color(0xFFD49A5A),
            1f to Color(0xFF1A1C22))
    }
    val hex = when (feel) {
        "Lively", "Lunch" -> listOf(0xFFC0663A, 0xFF5E2618, 0xFF17120F)
        "Awe", "Wonder" -> listOf(0xFFE7B77A, 0xFF9A6A3E, 0xFF3B2A1E, 0xFF15130F)
        "Calm", "Resting" -> listOf(0xFF86A870, 0xFF3B5532, 0xFF141A12)
        "Curious" -> listOf(0xFF8A7A62, 0xFF4A3F33, 0xFF1B1814)
        "Browsing", "Wandering" -> listOf(0xFFC8C0B2, 0xFF6E675E, 0xFF22201D)
        "Active", "Absorbed" -> listOf(0xFF5D8BA8, 0xFF27455A, 0xFF101519)
        else -> listOf(0xFF9A7A58, 0xFF4A3A2A, 0xFF15130F)
    }
    return Brush.radialGradient(hex.map { Color(it) }, center = Offset(0.4f * 900, 0.2f * 900), radius = 900f)
}

/** A moment's photo (openly licensed, with its credit shown nearby), or its field of colour. */
@Composable
fun MomentImage(momentId: String, feel: String?, modifier: Modifier = Modifier, drift: Boolean = false) {
    val context = LocalContext.current
    val photo = remember(momentId) { CardPhotos.photo(context, momentId) }
    if (photo != null) {
        val reduce = rememberReduceMotion()
        val on = remember { Animatable(0f) }
        LaunchedEffect(drift) { if (drift && !reduce) on.animateTo(1f, tween(16000, easing = LinearEasing)) }
        Image(
            photo.second.asImageBitmap(),
            contentDescription = "Photo of the place",
            contentScale = ContentScale.Crop,
            modifier = modifier.graphicsLayer {
                val k = 1f + 0.06f * on.value
                scaleX = k
                scaleY = k
                translationX = -6.dp.toPx() * on.value
                translationY = -4.dp.toPx() * on.value
            },
        )
    } else {
        Box(modifier.background(fieldBrush(feel)))
    }
}

/** For the layout of text inside fixed boxes in Canvas drawings. */
fun DrawScope.dpx(v: Float) = v * density

/** A full-width column with the app's side margins. */
@Composable
fun Page(modifier: Modifier = Modifier, content: @Composable ColumnScope.() -> Unit) {
    Column(modifier.fillMaxWidth().widthIn(max = 640.dp).padding(horizontal = 24.dp), content = content)
}

/** Lets the default min size of icon-only things meet 44 dp. */
fun Modifier.minTouch(): Modifier = this.defaultMinSize(minWidth = 44.dp, minHeight = 44.dp)

/** Fills the whole screen with the page colour. */
fun Modifier.screen(color: Color = Theme.background): Modifier = this.fillMaxSize().background(color)

/** A rounded shape helper used by cards. */
fun rounded(r: Int): Shape = RoundedCornerShape(r.dp)
