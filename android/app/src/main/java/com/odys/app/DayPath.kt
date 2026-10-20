package com.odys.app

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.cos
import kotlin.math.max
import kotlin.math.min

/**
 * D130 (the day as a path): the day's stops drawn where they really are, joined by a gentle line and numbered in order.
 * The part already walked is solid, the rest dotted, and the stop you're at is lit. No map tiles: the list of stops
 * and times sits straight under it. `current` is the stop you're at (null before the day starts). The same as
 * app/Sources/DayPath.swift.
 */
@Composable
fun DayPath(stops: List<Stop>, current: Int?, modifier: Modifier = Modifier, height: Dp = 180.dp) {
    val pins = stops.mapIndexedNotNull { i, s -> s.pin?.let { i to it } }
    if (pins.size < 2) return
    val label = "The day as a path: ${stops.size} stops, from ${stops.first().title} to ${stops.last().title}" +
        (current?.takeIf { it < stops.size }?.let { ". You're at stop ${it + 1}, ${stops[it].title}" } ?: "")
    val measurer = rememberTextMeasurer()
    val accent = Theme.accent
    val onAccent = Theme.onAccent
    val surface = Theme.surface
    Canvas(modifier.fillMaxWidth().height(height).semantics { contentDescription = label }) {
        val pad = 24.dp.toPx()
        val k = cos(Math.toRadians(pins.map { it.second.lat }.average()))
        val xs = pins.map { it.second.lon * k }
        val ys = pins.map { -it.second.lat }
        val spanX = max(xs.max() - xs.min(), 1e-6)
        val spanY = max(ys.max() - ys.min(), 1e-6)
        val w = size.width - 2 * pad
        val h = size.height - 2 * pad
        val scale = min(w / spanX, h / spanY)
        val ox = pad + (w - spanX * scale) / 2
        val oy = pad + (h - spanY * scale) / 2
        val r = 13.dp.toPx()
        val p = spread(pins.indices.map { j ->
            Offset((ox + (xs[j] - xs.min()) * scale).toFloat(), (oy + (ys[j] - ys.min()) * scale).toFloat())
        }, minGap = r * 2.4f, pad = pad, size = size)
        // a Catmull-Rom curve through the stops, one segment at a time, so walked and unwalked can differ
        for (j in 0 until p.size - 1) {
            val a = p[maxOf(j - 1, 0)]
            val b = p[j]
            val c = p[j + 1]
            val d = p[minOf(j + 2, p.size - 1)]
            val seg = Path().apply {
                moveTo(b.x, b.y)
                cubicTo(b.x + (c.x - a.x) / 6, b.y + (c.y - a.y) / 6, c.x - (d.x - b.x) / 6, c.y - (d.y - b.y) / 6, c.x, c.y)
            }
            val walked = current != null && pins[j + 1].first <= current
            drawPath(seg, accent.copy(alpha = if (walked) 1f else 0.85f), style = Stroke(
                width = 2.5.dp.toPx(), cap = StrokeCap.Round,
                pathEffect = if (walked) null else PathEffect.dashPathEffect(floatArrayOf(2.dp.toPx(), 7.dp.toPx())),
            ))
        }
        pins.forEachIndexed { j, (i, _) ->
            val at = p[j]
            val lit = current != null && i <= current
            if (current == i) drawCircle(accent.copy(alpha = 0.22f), r * 1.6f, at)
            drawCircle(if (lit) accent else surface, r, at)
            drawCircle(accent, r, at, style = Stroke(2.dp.toPx()))
            val text = measurer.measure("${i + 1}", TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold,
                color = if (lit) onAccent else accent))
            drawText(text, topLeft = Offset(at.x - text.size.width / 2f, at.y - text.size.height / 2f))
        }
    }
}

/** Stops a few hundred metres apart would sit on top of each other: push any two closer than `minGap` apart, a little
 *  at a time, and keep them inside the frame. The order and the rough shape stay. */
private fun spread(points: List<Offset>, minGap: Float, pad: Float, size: Size): List<Offset> {
    val p = points.toMutableList()
    repeat(40) {
        for (a in p.indices) for (b in a + 1 until p.size) {
            var d = p[b] - p[a]
            var len = d.getDistance()
            if (len >= minGap) continue
            if (len < 0.5f) { d = Offset(1f, 0.4f); len = d.getDistance() }
            val push = d / len * ((minGap - len) / 2)
            p[a] = p[a] - push
            p[b] = p[b] + push
        }
        for (k in p.indices) p[k] = Offset(p[k].x.coerceIn(pad, size.width - pad), p[k].y.coerceIn(pad, size.height - pad))
    }
    return p
}

/** D130 (Daylight): the sky at the top of the main screens, fading into the page. It changes only between steps. */
fun Modifier.skyBackground(base: Color = Theme.background): Modifier = this.drawBehind {
    drawRect(base)
    val end = min(size.height, 440.dp.toPx())
    drawRect(Brush.verticalGradient(0f to Theme.skyTop, 1f to base, startY = 0f, endY = end), size = Size(size.width, end))
}
