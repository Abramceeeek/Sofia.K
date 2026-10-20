package com.odys.app

import androidx.compose.animation.core.CubicBezierEasing
import androidx.compose.animation.core.tween
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.sp

/** One set of the app's colours (D130): the night set is the ODYS look of D119; the day set is for Daylight. */
data class Palette(
    val background: Color, val calm: Color, val surface: Color, val deep: Color, val surfaceHigh: Color,
    val selected: Color, val ink: Color, val inkSoft: Color, val inkTertiary: Color, val muted: Color, val line: Color,
    val outlineBase: Color, val accent: Color, val amberDeep: Color, val amberLight: Color, val onAccent: Color,
    val danger: Color, val dangerInk: Color, val emergencyBg: Color, val emergencyBorder: Color, val emergencyTitle: Color,
    val emergencyText: Color, val track: Color, val ring: Color, val warnBg: Color, val warnInk: Color,
    val okBg: Color, val okInk: Color, val savedBg: Color,
)

val NightPalette = Palette(
    background = Color(0xFF111317), calm = Color(0xFF0B0C0E), surface = Color(0xFF1A1D23), deep = Color(0xFF15171C),
    surfaceHigh = Color(0xFF2A2E36), selected = Color(0xFF241F17), ink = Color(0xFFF4EBDD),
    inkSoft = Color(0xFFCFC6B8), inkTertiary = Color(0xFFB5AB9C), muted = Color(0xFFA89F92), line = Color(0xFF2C2F36),
    outlineBase = Color(0xFFF4EBDD), accent = Color(0xFFFFC665), amberDeep = Color(0xFFE5A93C),
    amberLight = Color(0xFFFFE7B0), onAccent = Color(0xFF111317), danger = Color(0xFFD0363B),
    dangerInk = Color(0xFFFF8A8D),
    emergencyBg = Color(0xFF3A1416), emergencyBorder = Color(0xFF7A2A2E), emergencyTitle = Color(0xFFFFDCDC),
    emergencyText = Color(0xFFF6D2D2), track = Color(0xFF3A3E46), ring = Color(0xFF4A4E57),
    warnBg = Color(0xFF3A1F1C), warnInk = Color(0xFFF0A090), okBg = Color(0xFF1F3A2A), okInk = Color(0xFF9BE0B0),
    savedBg = Color(0xFF3A2F1C),
)

/** Daylight's colours: dark ink on warm paper, the amber deepened so it reads by day. Every text colour is 4.5:1 or
 *  better on every ground and sky (checked in ThemeTest). */
val DayPalette = Palette(
    background = Color(0xFFF4F1EA), calm = Color(0xFFF4F1EA), surface = Color(0xFFFFFDF8), deep = Color(0xFFECE8DF),
    surfaceHigh = Color(0xFFE7E2D8), selected = Color(0xFFF5E8D2), ink = Color(0xFF1E2326),
    inkSoft = Color(0xFF3B4044), inkTertiary = Color(0xFF4C5156), muted = Color(0xFF5A5F64), line = Color(0xFFD6D0C4),
    outlineBase = Color(0xFF1E2326), accent = Color(0xFF80521A), amberDeep = Color(0xFF6E4614),
    amberLight = Color(0xFFE8B76A), onAccent = Color(0xFFFFFDF8), danger = Color(0xFFB8262C),
    dangerInk = Color(0xFFB8262C),
    emergencyBg = Color(0xFFFBE4E2), emergencyBorder = Color(0xFFE7AEAD), emergencyTitle = Color(0xFF7A1518),
    emergencyText = Color(0xFF6A2023), track = Color(0xFFCFC8BB), ring = Color(0xFFA9A398),
    warnBg = Color(0xFFF8E1DC), warnInk = Color(0xFF8A2A1C), okBg = Color(0xFFDDEFE3), okInk = Color(0xFF1F5A35),
    savedBg = Color(0xFFF5E8D2),
)

/**
 * ODYS (D119, from Abram's design files): warm ink, one amber light, Newsreader serif for what matters and the system
 * font for the rest. D130 (Daylight): the colours follow London's light. `sky` is set by the app model when it opens,
 * comes back to the front, or moves on a step on "Now", never while someone is reading. The same values as
 * app/Sources/Theme.swift.
 */
object Theme {
    var sky by mutableStateOf(Sky.Night)
    val day get() = sky.day
    private val p get() = if (sky.day) DayPalette else NightPalette

    val background get() = p.background     // the phone
    val calm get() = p.calm                 // "Now": the screen gets quieter while you're out
    val surface get() = p.surface           // cards and tiles
    val deep get() = p.deep                 // the day's curve and the map
    val surfaceHigh get() = p.surfaceHigh   // a chosen tab, a field
    val selected get() = p.selected         // a chosen tile: a little warmth
    val ink get() = p.ink
    val inkSoft get() = p.inkSoft
    val inkTertiary get() = p.inkTertiary
    val muted get() = p.muted               // labels
    val line get() = p.line                 // the arch's frame, the path not yet walked
    val outline get() = p.outlineBase.copy(alpha = if (sky.day) 0.16f else 0.12f)
    val outlineStrong get() = p.outlineBase.copy(alpha = if (sky.day) 0.24f else 0.18f)
    val hairline get() = p.outlineBase.copy(alpha = if (sky.day) 0.09f else 0.07f)
    /** The one light: amber for text, icons, fills and the tint. */
    val accent get() = p.accent
    val amberDeep get() = p.amberDeep       // eyebrows, a pressed button
    val amberLight get() = p.amberLight     // the top of the arch's light
    val onAccent get() = p.onAccent
    // Help & safety: one red, only for emergencies (UX checklist: white on it is 4.9:1 at night, 6.3:1 by day)
    val danger get() = p.danger           // a fill, under white
    val dangerInk get() = p.dangerInk     // red as text
    val emergencyBg get() = p.emergencyBg
    val emergencyBorder get() = p.emergencyBorder
    val emergencyTitle get() = p.emergencyTitle
    val emergencyText get() = p.emergencyText
    val track get() = p.track               // a progress track, a timeline
    val ring get() = p.ring                 // a step not yet done
    val warnBg get() = p.warnBg
    val warnInk get() = p.warnInk
    val okBg get() = p.okBg
    val okInk get() = p.okInk
    val savedBg get() = p.savedBg
    /** The sky at the top of the main screens: its colour fades into the page (D130). */
    val skyTop get() = when (sky) {
        Sky.Morning -> Color(0xFFE9DCE3)
        Sky.Day -> Color(0xFFDDEBE6)
        Sky.Golden -> Color(0xFFF4D6B3)
        Sky.Rain -> Color(0xFFD5DCE2)
        Sky.Night -> Color(0xFF1A2030)
    }
    // The share card is cream, so it reads the same wherever it's sent
    val cream = Color(0xFFF4EBDD)
    val creamInk = Color(0xFF111317)
    val creamSoft = Color(0xFF6B5E4C)
    val creamQuote = Color(0xFF3A3128)
    val tabOff get() = muted

    val serifFamily = FontFamily(
        Font(R.font.newsreader, FontWeight.Normal, FontStyle.Normal),
        Font(R.font.newsreader_italic, FontWeight.Normal, FontStyle.Italic),
    )

    fun serif(size: TextUnit, color: Color = ink) =
        TextStyle(fontFamily = serifFamily, fontSize = size, lineHeight = size * 1.18f, color = color)

    fun italic(size: TextUnit, color: Color = accent) =
        TextStyle(fontFamily = serifFamily, fontStyle = FontStyle.Italic, fontSize = size, lineHeight = size * 1.25f,
            color = color)

    val hero get() = serif(44.sp)                   // "Now"
    val display get() = serif(40.sp)                // Welcome
    val h1 get() = serif(34.sp)                     // each screen's title
    val title get() = serif(28.sp)
    val title2 get() = serif(24.sp)
    val title3 get() = serif(21.sp)
    val option get() = serif(22.sp)                 // an answer on a tile
    val reaction get() = italic(20.sp)              // "Got it: …", in amber

    // The system font, in iOS's sizes (body 17, subheadline 15, footnote 13, caption 12)
    val body get() = TextStyle(fontSize = 17.sp, lineHeight = 23.sp, color = ink)
    val bodyMedium get() = body.copy(fontWeight = FontWeight.Medium)
    val headline get() = TextStyle(fontSize = 17.sp, lineHeight = 22.sp, fontWeight = FontWeight.SemiBold, color = ink)
    val subheadline get() = TextStyle(fontSize = 15.sp, lineHeight = 20.sp, color = ink)
    val footnote get() = TextStyle(fontSize = 13.sp, lineHeight = 18.sp, color = muted)
    val caption get() = TextStyle(fontSize = 12.sp, lineHeight = 16.sp, color = muted)
    val title2Sans get() = TextStyle(fontSize = 22.sp, lineHeight = 28.sp, fontWeight = FontWeight.SemiBold, color = ink)
}

/** The motion vocabulary (ODYS Motion): ease, never bounce; a response to a tap finishes within 300 ms. */
object Motion {
    val settleEasing = CubicBezierEasing(0.2f, 0.7f, 0.2f, 1f)
    fun <T> settle(delay: Int = 0) = tween<T>(450, delay, settleEasing)
    fun <T> press() = tween<T>(120)
    fun <T> select() = tween<T>(250)
    fun <T> fade() = tween<T>(300)
    fun <T> lift() = tween<T>(700, 0, settleEasing)
}
