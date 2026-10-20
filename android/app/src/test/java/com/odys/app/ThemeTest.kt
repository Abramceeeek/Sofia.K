package com.odys.app

import androidx.compose.ui.graphics.Color
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.Instant
import java.time.LocalDate
import kotlin.math.abs
import kotlin.math.pow

/**
 * D130 (Daylight): every text colour stays readable (4.5:1, WCAG AA) on every ground and sky, by day and by night,
 * and the sun lands where it should over London. A colour that drops below fails the build.
 *
 *     ./gradlew testDebugUnitTest --tests com.odys.app.ThemeTest
 */
class ThemeTest {
    private fun channel(c: Float) = if (c <= 0.04045f) c / 12.92 else ((c + 0.055) / 1.055).pow(2.4)
    private fun lum(c: Color) = 0.2126 * channel(c.red) + 0.7152 * channel(c.green) + 0.0722 * channel(c.blue)
    private fun ratio(a: Color, b: Color): Double {
        val (hi, lo) = listOf(lum(a), lum(b)).sortedDescending()
        return (hi + 0.05) / (lo + 0.05)
    }

    private fun check(name: String, fg: Color, bg: Color, min: Double = 4.5) {
        val r = ratio(fg, bg)
        assertTrue("$name is ${"%.2f".format(r)}:1, below $min:1", r >= min)
    }

    @Test
    fun everyTextColourIsReadableOnEveryGround() {
        for (sky in Sky.values()) {
            Theme.sky = sky
            val grounds = mapOf("background" to Theme.background, "surface" to Theme.surface, "deep" to Theme.deep,
                "surfaceHigh" to Theme.surfaceHigh, "selected" to Theme.selected, "calm" to Theme.calm,
                "sky" to Theme.skyTop)
            val texts = mapOf("ink" to Theme.ink, "inkSoft" to Theme.inkSoft, "inkTertiary" to Theme.inkTertiary,
                "muted" to Theme.muted, "accent" to Theme.accent, "amberDeep" to Theme.amberDeep)
            for ((t, fg) in texts) for ((g, bg) in grounds) check("$sky: $t on $g", fg, bg)
            check("$sky: red text on background", Theme.dangerInk, Theme.background)
            check("$sky: red text in a dialog", Theme.dangerInk, Theme.surfaceHigh)
            check("$sky: onAccent on accent", Theme.onAccent, Theme.accent)
            check("$sky: white on danger", Color.White, Theme.danger)
            check("$sky: emergency title", Theme.emergencyTitle, Theme.emergencyBg)
            check("$sky: emergency text", Theme.emergencyText, Theme.emergencyBg)
            check("$sky: booked", Theme.okInk, Theme.okBg)
            check("$sky: other dates", Theme.warnInk, Theme.warnBg)
            check("$sky: saved", Theme.accent, Theme.savedBg)
        }
        Theme.sky = Sky.Night
    }

    @Test
    fun theSunOverLondon() {
        val (rise, set) = Sun.riseAndSet(LocalDate.of(2026, 10, 31))
        // Sunset on 31 Oct 2026 is about 16:38 GMT and sunrise about 06:55 GMT (the same NOAA formulas, run separately)
        assertTrue("sunset $set", abs(set.epochSecond - Instant.parse("2026-10-31T16:38:00Z").epochSecond) < 240)
        assertTrue("sunrise $rise", abs(rise.epochSecond - Instant.parse("2026-10-31T06:55:00Z").epochSecond) < 300)
        assertEquals(24.5, Sun.elevation(Instant.parse("2026-10-31T12:00:00Z")), 0.5)
        assertEquals(61.9, Sun.elevation(Instant.parse("2027-06-21T12:00:00Z")), 0.5)
    }

    @Test
    fun theLightThroughADayOut() {
        fun at(t: String, rain: Double? = null, dark: Boolean = false) = Sky.at(Instant.parse(t), rain, dark)
        assertEquals(Sky.Morning, at("2026-10-31T07:30:00Z"))
        assertEquals(Sky.Day, at("2026-10-31T12:00:00Z"))
        assertEquals(Sky.Golden, at("2026-10-31T15:30:00Z"))
        assertEquals(Sky.Golden, at("2026-10-31T16:50:00Z"))   // after sunset, until the sun is 4° down
        assertEquals(Sky.Night, at("2026-10-31T18:00:00Z"))
        assertEquals(Sky.Rain, at("2026-10-31T12:00:00Z", rain = 0.8))
        assertEquals(Sky.Day, at("2026-10-31T12:00:00Z", rain = 0.3))
        assertEquals(Sky.Night, at("2026-10-31T12:00:00Z", dark = true))
    }
}
