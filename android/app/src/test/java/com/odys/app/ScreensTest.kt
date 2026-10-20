package com.odys.app

import android.graphics.Bitmap
import android.graphics.Canvas
import android.view.View
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.core.app.ApplicationProvider
import androidx.work.testing.WorkManagerTestInitHelper
import kotlinx.serialization.KSerializer
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode
import java.io.File

/**
 * Every main screen drawn on the computer with the iPhone app's sample data (app/Sources/Demo), and saved as a picture
 * in app/build/screens. A screen that crashes while it's drawn fails the test. No server is called: the app has no
 * token here, so every call stops before the network.
 *
 *     ./gradlew testDebugUnitTest --tests com.odys.app.ScreensTest
 */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w393dp-h852dp-xhdpi")
class ScreensTest {
    @get:Rule
    val compose = createComposeRule()

    private lateinit var model: AppModel
    private val out = File("build/screens").apply { mkdirs() }

    private fun <T> demo(name: String, s: KSerializer<T>): T =
        BrainJson.decodeFromString(s, File("../../app/Sources/Demo/$name.json").readText())

    @Before
    fun setUp() {
        val app = ApplicationProvider.getApplicationContext<android.app.Application>()
        WorkManagerTestInitHelper.initializeTestWorkManager(app)
        model = AppModel(app)
        model.onboarding = demo("demo_onboarding", Onboarding.serializer())
        model.learned = demo("demo_summary", Learned.serializer())
        val plan = demo("demo_plan", Plan.serializer())
        model.plan = plan
        model.surveyDone = true
        model.pairDone = true
        model.lastRequest = PlanRequest(AppConfig.START, AppConfig.START_NAME, "12:00", "17:00", plan.date, 4, true)
        val days = demo("demo_trip_days", TripDaysResponse.serializer())
        val flights = demo("demo_flights", FlightResults.serializer())
        val stays = demo("demo_stays", StayResults.serializer())
        val f = flights.results.first()
        val s = stays.results.first()
        val trip = Trip(start = days.days.first().date, nights = days.totalDays - 1,
            origin = TripPlace("TAS", "Tashkent", "Tashkent Islam Karimov", "UZ"), originGuessed = true,
            feelings = listOf("curious", "peaceful"), hoursFrom = "09:30", hoursTo = "19:00", places = 3, light = true,
            days = days.days, used = days.used, daysFrom = days.start,
            flight = TripChoice("flight", "${f.airline} · ${f.outbound.departTime} → ${f.outbound.arriveTime}", "Skyscanner",
                f.price, false, arriveTime = f.outbound.arriveTime, leaveTime = f.inbound?.departTime, arrivePlace = "LHR",
                leavePlace = "LHR"),
            stay = TripChoice("stay", s.name, "Booking.com", s.priceTotal, true, point = s.point))
        model.trips = listOf(trip)
        model.currentTripId = trip.id
        model.book.flights = flights
        model.book.stays = stays
        model.book.resultsFor = trip.id
        model.route = Route.Home
        Theme.sky = Sky.Night   // D130: the night look unless a test asks for the day
    }

    /** Draws the app and saves the top window (a sheet, when one is open), drawn straight into a picture. */
    private fun shoot(name: String) {
        compose.waitForIdle()
        compose.mainClock.advanceTimeBy(3000)
        compose.waitForIdle()
        val global = Class.forName("android.view.WindowManagerGlobal").getMethod("getInstance").invoke(null)
        @Suppress("UNCHECKED_CAST")
        val views = global.javaClass.getDeclaredField("mViews").apply { isAccessible = true }.get(global) as List<View>
        val top = views.last { it.width > 0 && it.height > 0 }
        val image = Bitmap.createBitmap(top.width, top.height, Bitmap.Config.ARGB_8888)
        compose.runOnUiThread { top.draw(Canvas(image)) }
        File(out, "$name.png").outputStream().use { image.compress(Bitmap.CompressFormat.PNG, 100, it) }
    }

    private fun show(name: String, setup: AppModel.() -> Unit = {}) {
        model.setup()
        compose.setContent { RootView(model) }
        shoot(name)
    }

    @Test fun welcome() = show("01-welcome") { route = Route.Welcome }
    @Test fun example() = show("02-example") { route = Route.Example }
    @Test fun consent() = show("03-consent") { route = Route.Consent }
    @Test fun based() = show("03b-based") { route = Route.Onboarding; step = Step.Based }
    @Test fun bestHour() = show("04-besthour") { route = Route.Onboarding; step = Step.BestHour }
    @Test fun why() = show("05-why") { route = Route.Onboarding; step = Step.Why }
    @Test fun places() = show("06-places") { route = Route.Onboarding; step = Step.Places }
    @Test fun categories() = show("06b-categories") {
        route = Route.Onboarding; step = Step.Places; profile = profile.copy(based = "abroad")
    }
    @Test fun thisOrThat() = show("07-thisorthat") { route = Route.Onboarding; step = Step.ThisOrThat }
    @Test fun learnedStep() = show("07b-learned") { route = Route.Onboarding; step = Step.Learned }
    @Test fun survey() = show("15-survey") { surveyDone = false }
    @Test fun pairIntent() = show("16-pairintent") { pairDone = false; plan = null }
    @Test fun pair() = show("17-pair") { pairDone = false; plan = null; pair = demo("demo_pair", PairResponse.serializer()) }
    @Test fun pairReveal() = show("18-pairreveal") {
        pairDone = false; plan = null; pair = demo("demo_pair_done", PairResponse.serializer())
    }
    @Test fun tripHome() = show("19-triphome")
    @Test fun planForm() = show("08-planform") { plan = null; tripPath += Dest.Day }
    @Test fun planDay() = show("09-plan") { tripPath += Dest.Day }
    @Test fun planMap() = show("09d-planmap") { prefs.set("planLayout", "map"); tripPath += Dest.Day }
    @Test fun stop() = show("10-stop") { tripPath += Dest.Day; tripPath += Dest.StopCard(plan!!.stops.first { it.rateable }) }
    @Test fun now() = show("10b-now") { nowIndex = 1; showNow = true }
    @Test fun trip() = show("24-trip") { tripPath += Dest.TripOverview(trips.first().id) }
    @Test fun tripDay() = show("25-tripday") { tripPath += Dest.TripOverview(trips.first().id); tripPath += Dest.TripDay(trips.first().id, 0) }
    @Test fun tripCreate() = show("20-tripcreate") { showCreate = true }
    @Test fun tripWhen() = show("21-tripwhen") { editingTrip = trips.first(); editStep = 1; showCreate = true }
    @Test fun tripFrom() = show("22-tripfrom") { editingTrip = trips.first(); editStep = 2; showCreate = true }
    @Test fun tripDays() = show("22a-tripdays") { editingTrip = trips.first(); editStep = 3; showCreate = true }
    // 20 Oct (round 2): a new trip on its last question, as on the iPhone ("Make my trip", not "Plan the trip again")
    @Test fun tripFeel() = show("23-tripfeel") { editingTrip = trips.first().copy(id = "draft"); editStep = 4; showCreate = true }
    // D131: flights and stays open inside the trip, and You from the home's menu
    private fun AppModel.openBook() { tripPath += Dest.TripOverview(trips.first().id); tripPath += Dest.Book }
    @Test fun flights() = show("26-flights") { openBook(); book.segment = "flights" }
    @Test fun flightFilters() = show("27-flightfilters") { openBook(); book.segment = "flights"; book.showFilters = true }
    @Test fun flight() = show("28-flight") { openBook(); bookPath += BookDest.FlightDetail(book.flights!!.results.first()) }
    @Test fun stays() = show("29-stays") { openBook(); book.segment = "stays" }
    @Test fun stay() = show("32-stay") { openBook(); bookPath += BookDest.StayDetail(book.stays!!.results.first()) }
    @Test fun you() = show("33-you") { tripPath += Dest.You }

    // D131 (shape A): the home on the day (part-way through) and after it (everything rated)
    private fun AppModel.today(at: Int) {
        plan = plan!!.copy(date = Dates.todayIso())
        prefs.set("nowIndex.${plan!!.id}", at)
        nowIndex = at
    }
    @Test fun homeToday() = show("19b-hometoday") { today(1) }
    @Test fun homeAfter() = show("19c-homeafter") {
        today(plan!!.stops.size)
        val r = plan!!.stops.filter { it.rateable }.mapIndexed { i, st -> st.momentId to listOf(5, 4, 3, 4, 5)[i % 5] }.toMap()
        myRatings = r; rated = r.keys
    }

    // D130 (Daylight): the main screens again by day, as they look between sunrise and sunset
    private fun day(name: String, setup: AppModel.() -> Unit = {}) = show(name) { Theme.sky = Sky.Day; setup() }
    @Test fun homeDay() = day("19d-home-day")
    @Test fun homeTodayDay() = day("19e-hometoday-golden") { Theme.sky = Sky.Golden; today(1) }
    @Test fun planDayLight() = day("09e-plan-day") { tripPath += Dest.Day }
    @Test fun nowDay() = day("10d-now-day") { today(1); showNow = true }
    @Test fun nowArrived() = day("10e-now-arrived") {
        today(1); arrivedStops = setOf(plan!!.stops[1].id); showNow = true
    }
    @Test fun tripDayLight() = day("24b-trip-day") { tripPath += Dest.TripOverview(trips.first().id) }
    @Test fun youDay() = day("33b-you-day") { tripPath += Dest.You }
    @Test fun archSun() {   // D130: the sun on "Now" at 70% of the daylight, in the golden hour
        Theme.sky = Sky.Golden
        compose.setContent {
            androidx.compose.foundation.layout.Box(androidx.compose.ui.Modifier.screen()
                .then(androidx.compose.ui.Modifier.skyBackground()), contentAlignment = androidx.compose.ui.Alignment.Center) {
                BreathingArch(showSun = true, sunAt = 0.7)
            }
        }
        shoot("10f-arch-sun")
    }
    @Test fun safetyDay() {
        Theme.sky = Sky.Day
        compose.setContent { RootView(model); SafetyView(model) {} }
        shoot("13b-safety-day")
    }

    @Test fun rating() {
        val stop = model.plan!!.stops.first { it.rateable }
        compose.setContent { RootView(model); RatingView(model, stop) {} }
        shoot("11-rating")
    }

    @Test fun shareCard() {
        val stop = model.plan!!.stops.first { it.rateable }
        val context = ApplicationProvider.getApplicationContext<android.app.Application>()
        val bmp = ShareCard.render(context, stop, 4)
        File(out, "11b-sharecard.png").outputStream().use { bmp.compress(Bitmap.CompressFormat.PNG, 100, it) }
    }

    @Test fun safety() {
        compose.setContent { RootView(model); SafetyView(model) {} }
        shoot("13-safety")
    }

    @Test fun settings() {
        compose.setContent { RootView(model); SettingsView(model) {} }
        shoot("14-settings")
    }
    @Test fun improve() {
        compose.setContent { RootView(model); ImproveView(model) {} }
        shoot("12a-improve")
    }

    @Test fun mustInclude() {
        model.moments = model.plan!!.stops.filter { it.rateable }.map { MomentSummary(it.base, it.title, "ready") }
        compose.setContent { RootView(model); MustIncludePicker(model, null, {}) {} }
        shoot("08b-mustinclude")
    }

    @Test fun changeDay() {
        val trip = model.trips.first()
        compose.setContent { RootView(model); ChangeDaySheet(model, trip, trip.days[1]) {} }
        shoot("25b-changeday")
    }

    @Test fun airports() {
        compose.setContent { RootView(model); AirportPicker(model, {}) {} }
        shoot("22b-airports")
    }

    @Test fun handoff() = show("28a-handoff") {
        openBook()
        val f = book.flights!!.results.first()
        book.handoff = Handoff("Skyscanner", "https://www.skyscanner.net", "Return flight", f.price, null,
            TripChoice("flight", f.airline, "Skyscanner", f.price, false))
    }

    @Test fun handoffBack() = show("28b-handoffback") {
        openBook()
        val f = book.flights!!.results.first()
        book.handoff = Handoff("Skyscanner", "https://www.skyscanner.net", "Return flight", f.price, null,
            TripChoice("flight", f.airline, "Skyscanner", f.price, false), back = true)
    }

    @Test fun sharePreview() {
        val stop = model.plan!!.stops.first { it.rateable }
        compose.setContent { RootView(model); SharePreview(model, stop, 4) {} }
        shoot("11c-sharepreview")
    }

    @Test fun deleteConfirm() {
        compose.setContent { RootView(model); DeleteConfirmView(model, {}) {} }
        shoot("14b-delete")
    }

    // dated today, so the day is over rather than a look ahead, and the two end-of-day questions show (D127)
    @Test fun nowEnd() = show("10c-nowend") { plan = plan!!.copy(date = Dates.todayIso()); nowIndex = plan!!.stops.size; showNow = true }
}
