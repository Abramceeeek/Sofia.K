package com.odys.app

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathMeasure
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import kotlin.math.PI
import kotlin.math.floor
import kotlin.math.ln
import kotlin.math.roundToInt
import kotlin.math.tan

/**
 * A pin on the map: a numbered stop, or "Stand here". `price` draws a price tag instead (stays, amber when
 * `highlight`); `dot` a small dot (where the days start).
 */
data class MapPin(val point: Point, val label: String, val number: Int? = null, val price: String? = null,
                  val highlight: Boolean = false, val dot: Boolean = false)

/**
 * A small map of OpenStreetMap tiles (no account or key; the iPhone app uses Apple's MapKit). Tiles are loaded only
 * for what's on screen, with the app named in each request and "© OpenStreetMap contributors" shown, as the OSM tile
 * policy asks. Pins and the route are drawn on top; a tap near a pin calls `onPin`.
 */
@Composable
fun OsmMap(
    pins: List<MapPin>,
    modifier: Modifier = Modifier,
    zoom: Int? = null,
    route: Boolean = false,
    progress: Float = 1f,
    onPin: ((Int) -> Unit)? = null,
) {
    if (pins.isEmpty()) {
        Box(modifier.background(Theme.deep))
        return
    }
    val context = LocalContext.current
    val density = LocalDensity.current
    BoxWithConstraints(modifier.background(Theme.deep)) {
        val w = constraints.maxWidth.toFloat()
        val h = constraints.maxHeight.toFloat()
        val tile = with(density) { 192.dp.toPx() }
        val pad = with(density) { 36.dp.toPx() }
        fun tx(lon: Double, z: Int) = (lon + 180) / 360 * (1 shl z)
        fun ty(lat: Double, z: Int): Double {
            val r = lat * PI / 180
            return (1 - ln(tan(r) + 1 / kotlin.math.cos(r)) / PI) / 2 * (1 shl z)
        }
        // the largest zoom that fits every pin with some room around them
        val z = zoom ?: (17 downTo 3).firstOrNull { zz ->
            val xs = pins.map { tx(it.point.lon, zz) }
            val ys = pins.map { ty(it.point.lat, zz) }
            (xs.max() - xs.min()) * tile <= w - 2 * pad && (ys.max() - ys.min()) * tile <= h - 2 * pad
        } ?: 3
        val cx = pins.map { tx(it.point.lon, z) }.let { (it.max() + it.min()) / 2 }
        val cy = pins.map { ty(it.point.lat, z) }.let { (it.max() + it.min()) / 2 }
        // screen position of a tile coordinate
        fun sx(x: Double) = (w / 2 + (x - cx) * tile).toFloat()
        fun sy(y: Double) = (h / 2 + (y - cy) * tile).toFloat()
        val x0 = floor(cx - w / 2 / tile).toInt()
        val x1 = floor(cx + w / 2 / tile).toInt()
        val y0 = floor(cy - h / 2 / tile).toInt()
        val y1 = floor(cy + h / 2 / tile).toInt()
        val n = 1 shl z
        val tileDp = with(density) { tile.toDp() }
        for (x in x0..x1) for (y in y0..y1) {
            if (y < 0 || y >= n) continue
            val wx = ((x % n) + n) % n
            AsyncImage(
                model = ImageRequest.Builder(context)
                    .data("https://tile.openstreetmap.org/$z/$wx/$y.png")
                    .addHeader("User-Agent", "ODYS-Android/0.1 (research test; ${AppConfig.CONTACT_EMAIL})")
                    .crossfade(true)
                    .build(),
                contentDescription = null,
                contentScale = ContentScale.FillBounds,
                modifier = Modifier.size(tileDp).offset { IntOffset(sx(x.toDouble()).roundToInt(), sy(y.toDouble()).roundToInt()) },
            )
        }
        val points = pins.map { Offset(sx(tx(it.point.lon, z)), sy(ty(it.point.lat, z))) }
        // D117: with a route, a pin shows once the line reaches it
        val along = if (route && points.size > 1) {
            val acc = points.indices.runningFold(0f) { sum, i -> if (i == 0) sum else sum + (points[i] - points[i - 1]).getDistance() }.drop(1)
            val total = maxOf(acc.last(), 1e-3f)
            acc.map { it / total }
        } else points.map { 0f }
        Canvas(
            Modifier.fillMaxSize().pointerInput(pins) {
                if (onPin != null) detectTapGestures { tap ->
                    val near = points.withIndex().minByOrNull { (it.value - tap).getDistance() }
                    if (near != null && (near.value - tap).getDistance() < 28.dp.toPx()) onPin(near.index)
                }
            },
        ) {
            if (!Theme.day) drawRect(Color.Black.copy(alpha = 0.25f))   // at night, dim the tiles so the amber reads (D130)
            if (route && points.size > 1) {
                val path = Path().apply {
                    moveTo(points[0].x, points[0].y)
                    for (p in points.drop(1)) lineTo(p.x, p.y)
                }
                val measure = PathMeasure().apply { setPath(path, false) }
                val part = Path()
                measure.getSegment(0f, measure.length * progress.coerceIn(0f, 1f), part, true)
                drawPath(path, Theme.line, style = Stroke(3.dp.toPx()))
                drawPath(part, Theme.accent, style = Stroke(3.dp.toPx()))
            }
            pins.forEachIndexed { i, pin ->
                if (along[i] > progress + 1e-4f) return@forEachIndexed
                val p = points[i]
                val paint = android.graphics.Paint().apply {
                    color = android.graphics.Color.parseColor("#111317")
                    textSize = 12.sp.toPx()
                    textAlign = android.graphics.Paint.Align.CENTER
                    isFakeBoldText = true
                    isAntiAlias = true
                }
                if (pin.dot) {
                    drawCircle(Theme.background, 7.dp.toPx(), p)
                    drawCircle(Theme.accent, 5.dp.toPx(), p)
                } else if (pin.price != null) {
                    val w = paint.measureText(pin.price) + 20.dp.toPx()
                    val h = 26.dp.toPx()
                    drawRoundRect(if (pin.highlight) Theme.accent else Theme.ink, Offset(p.x - w / 2, p.y - h / 2),
                        androidx.compose.ui.geometry.Size(w, h), androidx.compose.ui.geometry.CornerRadius(h / 2))
                    drawContext.canvas.nativeCanvas.drawText(pin.price, p.x, p.y + 4.dp.toPx(), paint)
                } else {
                    drawCircle(Theme.onAccent, 13.dp.toPx(), p)
                    drawCircle(Theme.accent, 11.dp.toPx(), p)
                    drawContext.canvas.nativeCanvas.drawText(pin.number?.toString() ?: "•", p.x, p.y + 4.dp.toPx(), paint)
                }
            }
        }
        Text("© OpenStreetMap contributors", style = Theme.caption.copy(fontSize = 10.sp, color = Theme.ink),
            modifier = Modifier.align(Alignment.BottomEnd).background(Theme.background.copy(alpha = 0.7f))
                .padding(horizontal = 4.dp, vertical = 1.dp))
    }
}
