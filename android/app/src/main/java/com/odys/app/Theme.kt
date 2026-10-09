package com.odys.app

import androidx.compose.animation.core.CubicBezierEasing
import androidx.compose.animation.core.tween
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.sp

/**
 * ODYS (D119, from Abram's design files): warm ink on charcoal, one amber light, Newsreader serif for what matters and
 * the system font for the rest. Dark always, so every colour here is fixed. The same values as app/Sources/Theme.swift.
 */
object Theme {
    val background = Color(0xFF111317)     // the phone
    val calm = Color(0xFF0B0C0E)           // "Now": the screen gets quieter while you're out
    val surface = Color(0xFF1A1D23)        // cards and tiles
    val deep = Color(0xFF15171C)           // the day's curve and the map
    val surfaceHigh = Color(0xFF2A2E36)    // a chosen tab, a field
    val selected = Color(0xFF241F17)       // a chosen tile: a little warmth
    val ink = Color(0xFFF4EBDD)
    val inkSoft = Color(0xFFCFC6B8)
    val inkTertiary = Color(0xFFB5AB9C)
    val muted = Color(0xFFA89F92)          // labels; 7:1 on the background
    val line = Color(0xFF2C2F36)           // the arch's frame, the path not yet walked
    val outline = Color(0xFFF4EBDD).copy(alpha = 0.12f)
    val outlineStrong = Color(0xFFF4EBDD).copy(alpha = 0.18f)
    val hairline = Color(0xFFF4EBDD).copy(alpha = 0.07f)
    /** The one light: amber for text, icons, fills and the tint. */
    val accent = Color(0xFFFFC665)
    val amberDeep = Color(0xFFE5A93C)      // eyebrows, a pressed button
    val amberLight = Color(0xFFFFE7B0)     // the top of the arch's light
    val onAccent = Color(0xFF111317)
    // Help & safety: one red, only for emergencies (UX checklist: white on it is 4.9:1)
    val danger = Color(0xFFD0363B)
    val emergencyBg = Color(0xFF3A1416)
    val emergencyBorder = Color(0xFF7A2A2E)
    val emergencyTitle = Color(0xFFFFDCDC)
    val emergencyText = Color(0xFFF6D2D2)
    // The share card is cream, so it reads the same wherever it's sent
    val cream = Color(0xFFF4EBDD)
    val creamInk = Color(0xFF111317)
    val creamSoft = Color(0xFF6B5E4C)
    val creamQuote = Color(0xFF3A3128)
    val tabOff = Color(0xFF8E867A)

    val serifFamily = FontFamily(
        Font(R.font.newsreader, FontWeight.Normal, FontStyle.Normal),
        Font(R.font.newsreader_italic, FontWeight.Normal, FontStyle.Italic),
    )

    fun serif(size: TextUnit, color: Color = ink) =
        TextStyle(fontFamily = serifFamily, fontSize = size, lineHeight = size * 1.18f, color = color)

    fun italic(size: TextUnit, color: Color = accent) =
        TextStyle(fontFamily = serifFamily, fontStyle = FontStyle.Italic, fontSize = size, lineHeight = size * 1.25f,
            color = color)

    val hero = serif(44.sp)                   // "Now"
    val display = serif(40.sp)                // Welcome
    val h1 = serif(34.sp)                     // each screen's title
    val title = serif(28.sp)
    val title2 = serif(24.sp)
    val title3 = serif(21.sp)
    val option = serif(22.sp)                 // an answer on a tile
    val reaction = italic(20.sp)              // "Got it: …", in amber

    // The system font, in iOS's sizes (body 17, subheadline 15, footnote 13, caption 12)
    val body = TextStyle(fontSize = 17.sp, lineHeight = 23.sp, color = ink)
    val bodyMedium = body.copy(fontWeight = FontWeight.Medium)
    val headline = TextStyle(fontSize = 17.sp, lineHeight = 22.sp, fontWeight = FontWeight.SemiBold, color = ink)
    val subheadline = TextStyle(fontSize = 15.sp, lineHeight = 20.sp, color = ink)
    val footnote = TextStyle(fontSize = 13.sp, lineHeight = 18.sp, color = muted)
    val caption = TextStyle(fontSize = 12.sp, lineHeight = 16.sp, color = muted)
    val title2Sans = TextStyle(fontSize = 22.sp, lineHeight = 28.sp, fontWeight = FontWeight.SemiBold, color = ink)
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
