package com.odys.app

import android.net.Uri
import kotlinx.serialization.Serializable
import java.time.LocalDate
import java.time.ZoneId
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.util.Locale
import java.util.UUID
import kotlin.math.roundToInt

// D120 (ODYS Trips design): multi-day trips, flights and stays (app/Sources/TripModels.swift). Nothing is booked in the
// app: every result links out to the provider's own site, and ODYS earns nothing from those links while testing.

@Serializable
data class TripPlace(val code: String, val city: String, val name: String, val country: String) {
    /** "Tashkent (TAS)", "London Heathrow (LHR)", or "London, all airports (LON)" for a city code. */
    val label: String
        get() = when {
            name.startsWith("All ") -> "$city, all airports ($code)"
            name.startsWith(city) -> "$city ($code)"
            else -> "$city $name ($code)"
        }
}

@Serializable
data class TripLink(val name: String, val url: String, val note: String? = null)

// ---- flights (POST /v1/trips/flights) ---------------------------------------------------------------------------

@Serializable
data class FlightFilters(
    val stops: List<Int> = emptyList(),
    val outTimes: List<String> = emptyList(),
    val inTimes: List<String> = emptyList(),
    val maxLegMin: Int? = null,
    val airlines: List<String> = emptyList(),
    val maxPrice: Double? = null,
    val checkedBag: Boolean = false,
    val sort: String = "best",
) {
    val count: Int
        get() = listOf(stops.isNotEmpty(), outTimes.isNotEmpty(), inTimes.isNotEmpty(), maxLegMin != null,
            airlines.isNotEmpty(), maxPrice != null, checkedBag).count { it }

    fun cleared() = FlightFilters(sort = sort)
}

@Serializable
data class FlightSearch(val origin: String, val destination: String, val departDate: String, val returnDate: String?,
                        val adults: Int, val filters: FlightFilters)

@Serializable
data class FlightLeg(
    val origin: String,
    val destination: String,
    val departAt: String,
    val arriveAt: String,
    val durationMin: Int,
    val stops: Int = 0,
    val via: List<String> = emptyList(),
    val carriers: List<String> = emptyList(),
    val flightNumbers: List<String> = emptyList(),
) {
    val departTime: String get() = departAt.drop(11).take(5)
    val arriveTime: String get() = arriveAt.drop(11).take(5)
    val departDay: String get() = departAt.take(10)
    val plusDays: Int
        get() = runCatching {
            ChronoUnit.DAYS.between(LocalDate.parse(departAt.take(10)), LocalDate.parse(arriveAt.take(10))).toInt()
                .coerceAtLeast(0)
        }.getOrDefault(0)
}

@Serializable
data class Flight(
    val id: String,
    val airline: String,
    val airlineCode: String,
    val price: Double,
    val currency: String = "GBP",
    val outbound: FlightLeg,
    val inbound: FlightLeg? = null,
    val checkedBags: Int? = null,
    val refundable: Boolean? = null,
    val changeable: Boolean? = null,
    val sample: Boolean = false,
    val stops: Int = 0,
    val durationMin: Int = 0,
    val tags: List<String>? = null,
)

@Serializable
data class StopFacet(val stops: Int, val minPrice: Double)

@Serializable
data class AirlineFacet(val name: String, val code: String, val minPrice: Double, val count: Int)

@Serializable
data class FlightFacets(
    val stops: List<StopFacet> = emptyList(),
    val airlines: List<AirlineFacet> = emptyList(),
    val price: List<Double>? = null,
    val legMinutes: List<Int>? = null,
)

@Serializable
data class FlightTab(val price: Double, val durationMin: Int)

@Serializable
data class FlightResults(
    val source: String,
    val note: String? = null,
    val total: Int = 0,
    val shown: Int = 0,
    val results: List<Flight> = emptyList(),
    val facets: FlightFacets = FlightFacets(),
    val tabs: Map<String, FlightTab?>? = null,
    val links: List<TripLink> = emptyList(),
    val searchedAt: String? = null,
)

// ---- stays (POST /v1/trips/stays) -------------------------------------------------------------------------------

@Serializable
data class StayFilters(
    val maxNight: Double? = null,
    val minRating: Double? = null,
    val kinds: List<String> = emptyList(),
    val refundable: Boolean = false,
    val breakfast: Boolean = false,
    val sort: String = "recommended",
) {
    val count: Int
        get() = listOf(maxNight != null, minRating != null, kinds.isNotEmpty(), refundable, breakfast).count { it }

    fun cleared() = StayFilters(sort = sort)
}

@Serializable
data class StaySearch(val destination: String, val checkin: String, val checkout: String, val adults: Int,
                      val rooms: Int, val filters: StayFilters)

@Serializable
data class StayResult(
    val id: String,
    val name: String,
    val kind: String = "hotel",
    val stars: Double? = null,
    val rating: Double? = null,
    val reviews: Int? = null,
    val address: String = "",
    val lat: Double? = null,
    val lon: Double? = null,
    val photo: String? = null,
    val priceTotal: Double,
    val currency: String = "GBP",
    val nights: Int = 1,
    val room: String = "",
    val board: String = "",
    val breakfast: Boolean = false,
    val refundable: Boolean? = null,
    val distanceKm: Double? = null,
    val sample: Boolean = false,
    val priceNight: Double,
    val links: List<TripLink> = emptyList(),
    val tags: List<String>? = null,
) {
    val point: Point? get() = if (lat != null && lon != null) Point(lat, lon) else null
}

@Serializable
data class KindFacet(val kind: String, val count: Int)

@Serializable
data class StayFacets(val priceNight: List<Double>? = null, val kinds: List<KindFacet> = emptyList(),
                      val maxKm: Double? = null)

@Serializable
data class StayTab(val priceNight: Double, val rating: Double? = null, val distanceKm: Double? = null)

@Serializable
data class StayResults(
    val source: String,
    val note: String? = null,
    val total: Int = 0,
    val shown: Int = 0,
    val results: List<StayResult> = emptyList(),
    val facets: StayFacets = StayFacets(),
    val tabs: Map<String, StayTab?>? = null,
    val links: List<TripLink> = emptyList(),
    val centre: String = "",
    val searchedAt: String? = null,
)

// ---- days (POST /v1/me/trips/days) ------------------------------------------------------------------------------

@Serializable
data class TripEnd(val mode: String, val place: String?, val time: String)

@Serializable
data class TripDaysRequest(
    val destination: String,
    val startDate: String,
    val nights: Int,
    val feelings: List<String>,
    val stay: Point?,
    val stayName: String?,
    val days: List<Int>,
    val exclude: List<String>,
    val dayStart: String,
    val dayEnd: String,
    val stopsPerDay: Int,
    val travelLight: Boolean,
    val arrive: TripEnd?,
    val leave: TripEnd?,
)

@Serializable
data class TripDayOut(
    val index: Int,
    val date: String,
    val kind: String,
    val title: String,
    val plan: Plan? = null,
    val window: DayWindow? = null,
    val before: Plan? = null,
    val legs: List<TripLeg>? = null,
) {
    fun journeys(slot: String): List<TripLeg> = (legs ?: emptyList()).filter { it.slot == slot }
}

@Serializable
data class TripLeg(
    val slot: String,
    val title: String,
    val depart: String? = null,
    val arrive: String? = null,
    val minutes: Int? = null,
    val how: String? = null,
    val note: String? = null,
    val mode: String = "transit",
    val origin: LegSpot? = null,
    val destination: LegSpot? = null,
) {
    /** "10:40 → 11:39 · about 59 min" */
    val times: String?
        get() = when {
            depart != null && arrive != null -> "$depart → $arrive" + (minutes?.let { " · about $it min" } ?: "")
            depart != null -> "Leave at $depart"
            arrive != null -> "Arrive at $arrive"
            else -> null
        }

    /** Google Maps directions (the Android counterpart of Apple Maps on iOS). None for "leave by car". */
    val mapsUrl: Uri?
        get() {
            val to = destination?.query ?: return null
            val mode = when (mode) { "driving" -> "driving"; "walking" -> "walking"; else -> "transit" }
            val b = Uri.parse("https://www.google.com/maps/dir/").buildUpon().appendQueryParameter("api", "1")
            origin?.query?.let { b.appendQueryParameter("origin", it) }
            b.appendQueryParameter("destination", to).appendQueryParameter("travelmode", mode)
            return b.build()
        }
}

@Serializable
data class LegSpot(val name: String, val maps: String? = null, val lat: Double? = null, val lon: Double? = null) {
    val query: String? get() = maps ?: if (lat != null && lon != null) "$lat,$lon" else null
}

@Serializable
data class DayWindow(val start: String, val end: String, val stops: Int)

@Serializable
data class TripDaysResponse(val totalDays: Int, val days: List<TripDayOut>, val start: String, val used: List<String>)

// ---- the trip, kept on the phone (trips.json) -------------------------------------------------------------------

@Serializable
data class TripChoice(
    val kind: String,
    val title: String,
    val provider: String,
    val price: Double,
    val booked: Boolean,
    val arriveTime: String? = null,
    val leaveTime: String? = null,
    val point: Point? = null,
    val arrivePlace: String? = null,
    val leavePlace: String? = null,
    val forStart: String? = null,
    val forNights: Int? = null,
    val sample: Boolean? = null,
    val landsNextDay: Boolean? = null,
)

@Serializable
data class Trip(
    val id: String = UUID.randomUUID().toString(),
    val destination: String = "london",
    val city: String = "London",
    val start: String,
    val nights: Int,
    val adults: Int = 1,
    val origin: TripPlace? = null,
    val originGuessed: Boolean = false,
    val needFlight: Boolean = true,
    val feelings: List<String> = emptyList(),
    val days: List<TripDayOut> = emptyList(),
    val used: List<String> = emptyList(),
    val daysFrom: String? = null,
    val daysStale: Boolean = false,
    val flight: TripChoice? = null,
    val stay: TripChoice? = null,
    val hoursFrom: String? = null,
    val hoursTo: String? = null,
    val places: Int? = null,
    val light: Boolean? = null,
    val travelBy: String? = null,
    val station: String? = null,
    val arriveAt: String? = null,
    val leaveAt: String? = null,
    val ownFlight: Boolean? = null,
    val flightAirport: String? = null,
    val changedDays: List<Int>? = null,
) {
    val dayFrom: String get() = hoursFrom ?: "10:00"
    val dayTo: String get() = hoursTo ?: "18:00"
    val placesPerDay: Int get() = places ?: 3
    val travelLight: Boolean get() = light ?: false
    /** flight | train | car | here */
    val arrivingBy: String get() = if (needFlight) "flight" else (travelBy ?: "here")

    val daysLine: String
        get() = "$dayFrom–$dayTo · $placesPerDay place${if (placesPerDay == 1) "" else "s"} a day" +
            if (travelLight && arrivingBy != "here" && arrivingBy != "car") " · travelling light" else ""

    /** Journey audit: a saved or booked choice still matches the trip's dates. */
    fun fits(choice: TripChoice?): Boolean {
        val from = choice?.forStart ?: return true
        return from == start && choice.forNights == nights
    }

    /** How the trip starts and ends, for the Brain. */
    val ends: Pair<TripEnd?, TripEnd?>
        get() = when (arrivingBy) {
            "flight" -> {
                val f = if (fits(flight)) flight else null
                if (f == null && ownFlight == true) {
                    val place = flightAirport ?: "LHR"
                    arriveAt?.let { TripEnd("flight", place, it) } to leaveAt?.let { TripEnd("flight", place, it) }
                } else {
                    f?.arriveTime?.let { TripEnd("flight", f.arrivePlace, it) } to
                        f?.leaveTime?.let { TripEnd("flight", f.leavePlace, it) }
                }
            }
            "train", "car" -> {
                val place = if (arrivingBy == "train") station else null
                arriveAt?.let { TripEnd(arrivingBy, place, it) } to leaveAt?.let { TripEnd(arrivingBy, place, it) }
            }
            else -> null to null
        }

    val dayCount: Int get() = nights + 1
    val needStay: Boolean get() = nights > 0
    val startDate: LocalDate get() = runCatching { LocalDate.parse(start) }.getOrDefault(Dates.today())
    val endDate: LocalDate get() = startDate.plusDays(nights.toLong())
    val end: String get() = endDate.toString()

    /** "10–16 Oct", "30 Oct – 2 Nov", or "Sat 10 Oct" for one day. */
    val range: String
        get() {
            if (nights <= 0) return Dates.dayShort(startDate)
            return if (startDate.month == endDate.month) "${startDate.dayOfMonth}–${Dates.dayMonth(endDate)}"
            else "${Dates.dayMonth(startDate)} – ${Dates.dayMonth(endDate)}"
        }

    val lengthLabel: String get() = if (nights == 0) "One day" else "$nights night${if (nights == 1) "" else "s"}"

    val rangeLong: String
        get() = if (nights == 0) "${Dates.dayShort(startDate)} · one day"
        else "${Dates.dayShort(startDate)} to ${Dates.dayShort(endDate)} · $lengthLabel"

    val travellers: String get() = "$adults ${if (adults == 1) "traveller" else "travellers"}"

    val feelLine: String
        get() = (if (feelings.isEmpty()) "Your trip" else "A ${feelings.joinToString(", ")} trip") + " · " + travellers
}

/** Journey round 2: London's five airports (the codes match brain/data/arrivals.yaml). */
object LondonAirports {
    val all = listOf("LHR" to "Heathrow", "LGW" to "Gatwick", "STN" to "Stansted", "LTN" to "Luton", "LCY" to "London City")
    fun name(code: String?) = all.firstOrNull { it.first == code }?.second
}

/** D122: London's main stations, for "Arriving by train". */
object LondonStations {
    val all = listOf("KGX" to "King's Cross St Pancras", "EUS" to "Euston", "PAD" to "Paddington", "VIC" to "Victoria",
        "WAT" to "Waterloo", "LST" to "Liverpool Street", "LBG" to "London Bridge", "MYB" to "Marylebone")
    fun name(code: String?) = all.firstOrNull { it.first == code }?.second
}

object HalfHours {
    fun from(start: Int, to: Int): List<String> =
        (start * 60..to * 60 step 30).map { String.format(Locale.UK, "%02d:%02d", it / 60, it % 60) }
}

/** The five feelings (brain/reasons.py FEELINGS), with the design's lines under each. */
object TripFeelings {
    val all = listOf(
        Triple("restored", "Restored", "Come home lighter than you left"),
        Triple("excited", "Excited", "Something to tell people about"),
        Triple("connected", "Connected", "Time that feels shared"),
        Triple("curious", "Curious", "Learn something you didn’t expect"),
        Triple("peaceful", "Peaceful", "Calm while the city rushes past"),
    )
}

/** Dates in London time, 24-hour clock. */
object Dates {
    val london: ZoneId = ZoneId.of("Europe/London")
    private val uk = Locale.UK

    fun now(): ZonedDateTime = ZonedDateTime.now(london)
    fun today(): LocalDate = LocalDate.now(london)
    fun todayIso(): String = today().toString()

    fun parse(iso: String?): LocalDate? = iso?.let { runCatching { LocalDate.parse(it.take(10)) }.getOrNull() }

    private fun fmt(p: String) = DateTimeFormatter.ofPattern(p, uk)

    /** "Sat 10 Oct" */
    fun dayShort(d: LocalDate): String = d.format(fmt("EEE d MMM"))
    /** "10 Oct" */
    fun dayMonth(d: LocalDate): String = d.format(fmt("d MMM"))
    /** "Saturday 31 October" */
    fun dayName(d: LocalDate): String = d.format(fmt("EEEE d MMMM"))
    /** "October 2026" */
    fun monthYear(d: LocalDate): String = d.format(fmt("MMMM yyyy"))
    fun weekdayShort(d: LocalDate): String = d.format(fmt("EEE"))

    /** "Sat 10 Oct" from "2026-10-10" (or the first ten characters of a date-time). */
    fun shortDay(iso: String): String = parse(iso)?.let { dayShort(it) } ?: iso

    /** "Saturday 31 October", or null. */
    fun longDay(iso: String?): String? = parse(iso)?.let { dayName(it) }

    /** "11h 05m" */
    fun duration(minutes: Int): String = "${minutes / 60}h ${String.format(uk, "%02d", minutes % 60)}m"

    /** The coming Saturday (or today, if it is one): the Test B day (D105). */
    fun nextSaturday(): LocalDate {
        val t = today()
        val add = (6 - (t.dayOfWeek.value % 7) + 7) % 7   // Saturday is 6 in ISO (Mon 1 … Sun 7)
        return t.plusDays(add.toLong())
    }

    fun minutes(hhmm: String): Int {
        val p = hhmm.take(5).split(":").mapNotNull { it.toIntOrNull() }
        return if (p.size == 2) p[0] * 60 + p[1] else 0
    }

    fun hhmm(minutes: Int): String = String.format(uk, "%02d:%02d", minutes / 60, minutes % 60)

    /** m191: set by the screenshot test, so both phones' screenshots greet the same. */
    var greetingForScreens: String? = null

    /** "Good morning", in London time. */
    val greeting: String
        get() {
            greetingForScreens?.let { return it }
            val h = now().hour
            return if (h < 12) "Good morning" else if (h < 18) "Good afternoon" else "Good evening"
        }
}

object Money {
    /** £21, or £21.50 */
    fun text(gbp: Double): String =
        if (gbp == Math.rint(gbp)) "£${gbp.toLong()}" else String.format(Locale.UK, "£%.2f", gbp)

    /** £398, or £1,318: rounded to the pound for prices that aren't ours to promise. */
    fun whole(gbp: Double): String = "£" + String.format(Locale.UK, "%,d", gbp.roundToInt())
}
