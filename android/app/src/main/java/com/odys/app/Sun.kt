package com.odys.app

import java.time.Instant
import java.time.LocalDate
import java.time.ZoneOffset
import kotlin.math.acos
import kotlin.math.cos
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sin
import kotlin.math.tan

/**
 * D130 (Daylight): where the sun is over London, worked out on the phone with NOAA's general solar position formulas,
 * so the light needs no network and works offline. Good to a minute or two, which is plenty for a colour.
 * The same as app/Sources/Sun.swift.
 */
object Sun {
    const val LAT = 51.5074
    const val LON = -0.1278

    private fun rad(d: Double) = Math.toRadians(d)
    private fun deg(r: Double) = Math.toDegrees(r)

    /** The fractional year (radians), the declination (radians) and the equation of time (minutes) at a UTC moment. */
    private fun parts(dayOfYear: Int, utcHour: Double): Pair<Double, Double> {
        val g = 2 * Math.PI / 365 * (dayOfYear - 1 + (utcHour - 12) / 24)
        val decl = 0.006918 - 0.399912 * cos(g) + 0.070257 * sin(g) - 0.006758 * cos(2 * g) +
            0.000907 * sin(2 * g) - 0.002697 * cos(3 * g) + 0.00148 * sin(3 * g)
        val eqt = 229.18 * (0.000075 + 0.001868 * cos(g) - 0.032077 * sin(g) - 0.014615 * cos(2 * g) -
            0.040849 * sin(2 * g))
        return decl to eqt
    }

    /** The sun's height above the horizon, in degrees, at this moment. */
    fun elevation(at: Instant): Double {
        val t = at.atOffset(ZoneOffset.UTC)
        val hour = t.hour + t.minute / 60.0 + t.second / 3600.0
        val (decl, eqt) = parts(t.dayOfYear, hour)
        val solarMinutes = hour * 60 + eqt + 4 * LON
        val ha = rad(solarMinutes / 4 - 180)
        val la = rad(LAT)
        val cz = sin(la) * sin(decl) + cos(la) * cos(decl) * cos(ha)
        return 90 - deg(acos(min(1.0, max(-1.0, cz))))
    }

    /** Sunrise and sunset that day, as instants (the sun's top edge at the horizon, with refraction). */
    fun riseAndSet(day: LocalDate): Pair<Instant, Instant> {
        val (decl, eqt) = parts(day.dayOfYear, 12.0)
        val la = rad(LAT)
        val x = cos(rad(90.833)) / (cos(la) * cos(decl)) - tan(la) * tan(decl)
        val ha = deg(acos(min(1.0, max(-1.0, x))))
        val midnight = day.atStartOfDay().toInstant(ZoneOffset.UTC)
        val rise = 720 - 4 * (LON + ha) - eqt
        val set = 720 - 4 * (LON - ha) - eqt
        return midnight.plusSeconds((rise * 60).toLong()) to midnight.plusSeconds((set * 60).toLong())
    }
}

/** D130: how far through the daylight `now` is (0 at sunrise, 1 at sunset), or null at night. For the sun on "Now". */
fun Sun.dayFraction(now: Instant): Double? {
    val (rise, set) = riseAndSet(now.atOffset(ZoneOffset.UTC).toLocalDate())
    val f = (now.epochSecond - rise.epochSecond).toDouble() / (set.epochSecond - rise.epochSecond)
    return f.takeIf { it in 0.0..1.0 }
}

/** D130: the light the app takes on. Night is today's dark ODYS look; the four day states share one set of colours
 *  and differ in the sky at the top of the main screens. */
enum class Sky(val day: Boolean) {
    Morning(true), Day(true), Golden(true), Rain(true), Night(false);

    companion object {
        /** Dark once the sun is 4° below the horizon (about 25 minutes after sunset in London in winter). Golden in
         *  the last 90 minutes before sunset and until dark; morning from first light until 2 hours after sunrise.
         *  Rain when today's forecast gives a 60% chance or more. */
        fun at(now: Instant, rainProb: Double? = null, alwaysDark: Boolean = false): Sky {
            val elevation = Sun.elevation(now)
            if (alwaysDark || elevation < -4) return Night
            if ((rainProb ?: 0.0) >= 0.6) return Rain
            val (rise, set) = Sun.riseAndSet(now.atOffset(ZoneOffset.UTC).toLocalDate())
            val toSet = (set.epochSecond - now.epochSecond) / 60
            val sinceRise = (now.epochSecond - rise.epochSecond) / 60
            return when {
                toSet <= 90 -> Golden
                sinceRise <= 120 -> Morning
                else -> Day
            }
        }
    }
}
