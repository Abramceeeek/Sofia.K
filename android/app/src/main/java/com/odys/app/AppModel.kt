package com.odys.app

import android.app.Application
import android.net.Uri
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.serialization.SerializationException
import kotlinx.serialization.Serializable
import kotlinx.serialization.builtins.ListSerializer
import java.io.IOException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import java.time.LocalDate
import java.time.temporal.ChronoUnit

enum class Route { Welcome, Example, Consent, Onboarding, Home }

/** Onboarding up to the first plan (screens 3–6), as on the iPhone. */
enum class Step(val title: String) {
    Based("Where you're based"),
    Why("How you want to feel"),
    Places("Places you've been"),
    ThisOrThat("This or that"),
    BestHour("A great moment"),   // D127: the open question last, once the taps have warmed them up
    Learned("So far");

    companion object {
        val questions = values().filter { it != Learned }
    }
}

enum class MainTab { Trip, Book, You }

/** Where the Trip tab can go. */
sealed class Dest {
    data object Day : Dest()
    data class TripOverview(val tripId: String) : Dest()
    data class TripDay(val tripId: String, val index: Int, val openChange: Boolean = false) : Dest()
    data class StopCard(val stop: Stop, val planId: Int? = null) : Dest()
    data class Share(val stop: Stop) : Dest()
}

/** Where the Book tab can go. */
sealed class BookDest {
    data class FlightDetail(val flight: Flight) : BookDest()
    data class StayDetail(val stay: StayResult) : BookDest()
}

/** A link out, about to open: "You're going to Skyscanner", then "Did you book it?" when they come back. */
data class Handoff(
    val provider: String,
    val url: String,
    val what: String,
    val price: Double?,
    val searchedAt: String?,
    val choice: TripChoice,
    val back: Boolean = false,
)

/** Journey audit: a hand-off kept on the phone while the person is on the provider's site. */
@Serializable
data class SavedHandoff(
    val provider: String,
    val url: String,
    val what: String,
    val price: Double?,
    val searchedAt: String?,
    val choice: TripChoice,
    val tripId: String,
    val at: Long,
)

/** The Book tab: the search for the current trip, its filters and results. */
class BookState {
    var segment by mutableStateOf("flights")      // flights | stays
    var flightFilters by mutableStateOf(FlightFilters())
    var stayFilters by mutableStateOf(StayFilters())
    var flights by mutableStateOf<FlightResults?>(null)
    var stays by mutableStateOf<StayResults?>(null)
    var loading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
    var showFilters by mutableStateOf(false)
    var stayMap by mutableStateOf(false)
    var handoff by mutableStateOf<Handoff?>(null)
    var resultsFor by mutableStateOf<String?>(null)
    var job: Job? = null

    fun reset() {
        job?.cancel()
        segment = "flights"
        flightFilters = FlightFilters()
        stayFilters = StayFilters()
        flights = null
        stays = null
        loading = false
        error = null
        showFilters = false
        stayMap = false
        handoff = null
        resultsFor = null
    }
}

/** Everything the app knows and does (app/Sources/AppModel.swift and TripLogic.swift). */
class AppModel(app: Application) : AndroidViewModel(app) {
    val prefs = Prefs(app)
    val files = Files(app)
    val tokens = TokenStore(app)
    val client = BrainClient(AppConfig.BASE_URL, tokens)
    val location = Location(app, prefs)
    val reminders = Reminders(app)

    var route by mutableStateOf(Route.Welcome)
    var step by mutableStateOf(Step.Based)
    var onboarding by mutableStateOf<Onboarding?>(null)
    var plan by mutableStateOf<Plan?>(null)
    var busy by mutableStateOf(false)
    var waking by mutableStateOf(false)
    var errorMessage by mutableStateOf<String?>(null)
    var notice by mutableStateOf<Pair<String, String>?>(null)
    var clock by mutableStateOf(System.currentTimeMillis())

    // Answers, kept until each step is sent
    var bestHour by mutableStateOf("")
    var bestHourMore by mutableStateOf("")
    var bestHourVoice by mutableStateOf(false)
    val categoryAnswers = androidx.compose.runtime.mutableStateMapOf<String, CategoryItem>()
    var reaction by mutableStateOf<String?>(null)
    private val saidPatterns = mutableSetOf<String>()
    var learned by mutableStateOf<Learned?>(null)
    var revealPlanId by mutableStateOf<Int?>(null)
    var stepProgress by mutableStateOf(0)

    // D120: three tabs, trips kept on the phone, booking on the providers' own sites
    var tab by mutableStateOf(MainTab.Trip)
    val tripPath = mutableStateListOf<Dest>()
    val bookPath = mutableStateListOf<BookDest>()
    var trips by mutableStateOf<List<Trip>>(emptyList())
    var currentTripId by mutableStateOf<String?>(null)
    var showCreate by mutableStateOf(false)
    var editingTrip by mutableStateOf<Trip?>(null)
    var editStep by mutableStateOf<Int?>(null)
    val book = BookState()

    // Build 2
    var surveyDone by mutableStateOf(prefs.bool("surveyDone"))
    var pairDone by mutableStateOf(prefs.bool("pairDone"))
    var pair by mutableStateOf<PairResponse?>(null)
    var showPair by mutableStateOf(false)
    var ratedOnce by mutableStateOf(prefs.bool("ratedOnce"))
    var safetyThreads by mutableStateOf<List<SafetyThread>>(emptyList())
    var remindersOn by mutableStateOf(prefs.bool("remindersOn"))
    var reminderAsked by mutableStateOf(prefs.bool("reminderAsked"))
    var showNow by mutableStateOf(false)
    var nowIndex by mutableStateOf(0)

    var why by mutableStateOf<List<String>>(emptyList())
    val reactions = androidx.compose.runtime.mutableStateMapOf<Int, String>()
    val choices = androidx.compose.runtime.mutableStateMapOf<Int, String>()
    var profile by mutableStateOf(Profile())
    var rated by mutableStateOf<Set<String>>(emptySet())
    var myRatings by mutableStateOf<Map<String, Int>>(emptyMap())
    var pendingRatings by mutableStateOf<List<RatingRequest>>(emptyList())
    var lastRatingQueued by mutableStateOf(false)
    private var sendingRatings = false
    var improved by mutableStateOf(prefs.bool("improved"))
    var morePlacesDone by mutableStateOf(prefs.bool("morePlacesDone"))
    var moreTasksDone by mutableStateOf(prefs.bool("moreTasksDone"))
    var swappedIn by mutableStateOf<String?>(null)
    var lastRequest by mutableStateOf<PlanRequest?>(null)

    val isVisitor: Boolean get() = profile.based == "abroad"
    val stepTitle: String get() = if (step == Step.Places && isVisitor) "Kinds of places" else step.title

    init {
        if (client.token == null) {
            route = Route.Welcome
        } else {
            route = if (prefs.bool("onboardingDone")) Route.Home else Route.Onboarding
            step = prefs.int("onboardingStep")?.let { Step.values().getOrNull(it) } ?: Step.Based
            plan = files.load(Plan.serializer(), "plan.json")
            lastRequest = files.load(PlanRequest.serializer(), "request.json")
            plan?.let { val r = prefs.ratings(it.id); rated = r.keys; myRatings = r }
            pendingRatings = files.load(ListSerializer(RatingRequest.serializer()), "pending_ratings.json") ?: emptyList()
            trips = files.load(ListSerializer(Trip.serializer()), "trips.json") ?: emptyList()
            currentTripId = trips.firstOrNull()?.id
            files.load(Profile.serializer(), "profile.json")?.let { profile = it; why = it.whyTravel }
            restoreHandoff()
        }
    }

    // ---- running a call, with the "waking up" note after 3 s --------------------------------

    suspend fun run(work: suspend () -> Unit) {
        busy = true
        errorMessage = null
        val note = viewModelScope.launch {
            delay(3000)
            waking = true
        }
        try {
            work()
        } catch (e: BrainError) {
            if (e.code == 401) {
                // The Brain no longer knows this phone (its data was deleted there): start again from Welcome.
                clearLocal()
                client.forget()
                errorMessage = "This phone's answers are no longer on the planner, so let's start again."
            } else {
                errorMessage = e.message
            }
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            errorMessage = message(e)
        } finally {
            note.cancel()
            waking = false
            busy = false
        }
    }

    fun launch(work: suspend () -> Unit) = viewModelScope.launch { work() }

    suspend fun wake() = client.wake()

    /** What went wrong, in words a person can act on. */
    fun message(e: Throwable): String? = when (e) {
        is CancellationException -> null
        is BrainError -> e.message
        is SocketTimeoutException -> "The planner took too long to answer. It may still be waking up, so try again in a minute."
        is UnknownHostException, is java.net.ConnectException, is java.net.NoRouteToHostException ->
            "You seem to be offline. Check your connection and try again."
        is IOException -> "Couldn't reach the planner. Check your connection and try again."
        is SerializationException, is IllegalArgumentException ->
            "The app couldn't read the planner's answer. Please install the latest ODYS build."
        else -> "Something unexpected happened. Please try again."
    }

    /** No connection, or the server didn't answer in time: worth keeping a rating to send later. */
    private fun noSignal(e: Throwable) = e is IOException

    // ---- first run ---------------------------------------------------------------------------

    fun agree() = launch {
        val joined = prefs.string("refCode.joined")
        run {
            val code = prefs.string("testerCode")
            val channel = client.install(true, joined?.let { "ref:$it" } ?: "app", code)
            if (!code.isNullOrEmpty() && channel == "stranger") {
                notice = "We don't know that code" to
                    "That's fine: you're in as a new tester. If a friend sent you, the test still counts you."
            }
            prefs.remove("refCode.joined")
            route = Route.Onboarding
        }
    }

    /** D114: a share link opened in the app (daysout://r/<code>), kept and sent with the install. */
    fun openLink(uri: Uri) {
        if (uri.scheme != "daysout" || uri.host != "r" || client.token != null) return
        val code = uri.pathSegments.firstOrNull() ?: return
        if (code.length == 8 && code.all { it.isUpperCase() || it.isDigit() }) prefs.set("refCode.joined", code)
    }

    suspend fun loadOnboarding() {
        if (onboarding == null) onboarding = client.onboarding()
    }

    // ---- D118: "Question 7 of 14", every question before the first plan, counted honestly ---------------------

    private fun questionsIn(s: Step): Int = when (s) {
        Step.Based, Step.BestHour, Step.Why -> 1
        Step.Places -> if (isVisitor) (onboarding?.categoryCards?.size ?: 0) else (onboarding?.swipePlaces?.size ?: 0)
        Step.ThisOrThat -> onboarding?.conjointTasks?.size ?: 0
        Step.Learned -> 0
    }

    val questionTotal: Int get() = Step.questions.sumOf { questionsIn(it) }

    val questionNumber: Int
        get() {
            val before = Step.questions.takeWhile { it != step }.sumOf { questionsIn(it) }
            return minOf(before + minOf(stepProgress, maxOf(questionsIn(step) - 1, 0)) + 1, maxOf(questionTotal, 1))
        }

    val questionLabel: String get() = "Question $questionNumber of $questionTotal"
    val questionProgress: Float get() = (questionNumber - 1).toFloat() / maxOf(questionTotal, 1)

    /** `from`: only if still on that step (two taps on "Skip the rest" skipped the next step too). */
    fun next(from: Step? = null) {
        if (from != null && from != step) return
        reaction = null
        stepProgress = 0
        Step.values().getOrNull(step.ordinal + 1)?.let {
            step = it
            prefs.set("onboardingStep", it.ordinal)
        }
    }

    /** m176: back to the step before. Answers already given stay filled in. */
    fun back() {
        val p = Step.values().getOrNull(step.ordinal - 1) ?: return
        reaction = null
        stepProgress = 0
        step = p
        prefs.set("onboardingStep", p.ordinal)
    }

    // ---- D117: short reactions between answers, from the answer itself ------------------------------

    fun react(r: Reactions?, answer: String) {
        reaction = r?.text(answer)
    }

    /** "This or that": names a pattern once it has held every time, in at least 3 made-up days; each pattern once. */
    fun reactToChoices(tasks: List<ConjointTask>) {
        val words = onboarding?.conjointWords
        if (words == null) {
            reaction = null
            return
        }
        var best: Triple<Int, String, String>? = null
        words.forEachIndexed { i, w ->
            if (w.attr in saidPatterns) return@forEachIndexed
            var low = 0
            var high = 0
            for (t in tasks) {
                val c = choices[t.task] ?: continue
                if (c == "N") continue
                val lv = t.levels ?: continue
                val mine = lv[c] ?: continue
                val other = lv[if (c == "A") "B" else "A"] ?: continue
                if (i >= mine.size || i >= other.size) continue
                if (mine[i] < other[i]) low++ else if (mine[i] > other[i]) high++
            }
            val k = low + high
            if (k >= 3 && (low == 0 || high == 0) && k > (best?.first ?: 0)) {
                best = Triple(k, w.attr, "So far you've picked ${if (low > 0) w.low else w.high} every time.")
            }
        }
        best?.let { saidPatterns.add(it.second) }
        reaction = best?.third
    }

    fun finishBestHour() = launch {
        run {
            val items = mutableListOf<AnswerItem>()
            val first = bestHour.trim()
            val more = bestHourMore.trim()
            if (first.isNotEmpty()) items += AnswerItem("best_hour", first, if (bestHourVoice) "voice" else "typed")
            if (more.isNotEmpty()) items += AnswerItem("best_hour_more", more, "typed")
            if (items.isNotEmpty()) client.sendAnswers(items)
            next()
        }
    }

    private suspend fun sendReactions(places: List<SwipePlace>) {
        val items = places.mapNotNull { p -> reactions[p.item]?.let { SwipeItem(p.item, it) } }
        if (items.isNotEmpty()) client.sendSwipes(items)
    }

    private suspend fun sendChoices(tasks: List<ConjointTask>) {
        val items = tasks.mapNotNull { t -> choices[t.task]?.let { ChoiceItem(t.task, it) } }
        if (items.isNotEmpty()) client.sendChoices(items)
    }

    fun finishBased() = launch {
        run {
            client.sendProfile(profile)
            files.save(Profile.serializer(), profile, "profile.json")
            next()
        }
    }

    fun finishCategories() = launch {
        val from = step
        run {
            val items = (onboarding?.categoryCards ?: emptyList()).mapNotNull { categoryAnswers[it.key] }
            if (items.isNotEmpty()) client.sendCategories(items)
            next(from)
        }
    }

    fun finishPlaces() = launch {
        val from = step
        run {
            sendReactions(onboarding?.swipePlaces ?: emptyList())
            next(from)
        }
    }

    suspend fun finishMorePlaces() = run {
        sendReactions(onboarding?.swipePlacesLater ?: emptyList())
        morePlacesDone = true
        prefs.set("morePlacesDone", true)
    }

    suspend fun finishMoreTasks() = run {
        sendChoices(onboarding?.conjointTasksLater ?: emptyList())
        moreTasksDone = true
        prefs.set("moreTasksDone", true)
    }

    fun keepFeelings() {
        profile = profile.copy(whyTravel = why)
        files.save(Profile.serializer(), profile, "profile.json")
    }

    fun finishThisOrThat() = launch {
        profile = profile.copy(whyTravel = why)
        val from = step
        run {
            sendChoices(onboarding?.conjointTasks ?: emptyList())
            client.sendProfile(profile)
            files.save(Profile.serializer(), profile, "profile.json")
            learned = null
            next(from)
        }
    }

    fun loadLearned() = launch { run { learned = client.summary() } }

    fun finishLearned(wrong: Set<String>) = launch {
        run {
            if (wrong.isEmpty()) {
                client.event(if (learned == null) "summary_unavailable" else "summary_ok",
                    mapOf("items" to "${learned?.items?.size ?: 0}"))
            } else {
                client.sendCorrections(wrong.sorted())
                val feelings = wrong.filter { it.startsWith("feeling:") }.map { it.removePrefix("feeling:") }.toSet()
                why = why.filter { it !in feelings }
                profile = profile.copy(whyTravel = why)
                files.save(Profile.serializer(), profile, "profile.json")
                client.event("summary_changed", mapOf("n" to "${wrong.size}"))
            }
            prefs.set("onboardingDone", true)
            prefs.remove("onboardingStep")
            client.event("onboarding_done")
            route = Route.Home
        }
    }

    suspend fun saveImprovements(done: Boolean) {
        profile = profile.copy(whyTravel = why)
        run {
            client.sendProfile(profile)
            files.save(Profile.serializer(), profile, "profile.json")
            if (done) {
                improved = true
                prefs.set("improved", true)
                client.event("improve_done")
            }
        }
    }

    // ---- plans and ratings ------------------------------------------------------------------------

    suspend fun makePlan(date: LocalDate, start: String, end: String, stops: Int, from: Point? = null,
                         mustDo: String? = null) {
        var request = PlanRequest(from ?: AppConfig.START, if (from == null) AppConfig.START_NAME else "where you are",
            start, end, date.toString(), stops, true)
        if (mustDo != null) request = request.copy(intent = mapOf("must_do" to mustDo))
        fetchPlan(request, sameDay = false)
        if (from != null) client.event("plan_from_here")
    }

    suspend fun replan() {
        val request = lastRequest ?: return
        fetchPlan(request.copy(keep = emptyList(), exclude = emptyList()))
    }

    /** "Plan again" (D112): the same day with none of the current stops. Off in the blind Test B comparison. */
    suspend fun regenerate() {
        val request = lastRequest ?: return
        val current = plan ?: return
        val exclude = (request.exclude + current.stops.filter { it.rateable }.map { it.momentId }).toSet().sorted()
        fetchPlan(request.copy(intent = null, keep = emptyList(), exclude = exclude))
        client.event("regenerate_plan")
    }

    /** "Free from 15:56 until 18:00": a day that ends at least an hour before the person's end time. */
    fun freeTime(p: Plan): Pair<String, String>? {
        val request = lastRequest ?: return null
        val last = p.stops.lastOrNull() ?: return null
        return if (Dates.minutes(request.endTime) - Dates.minutes(last.depart) >= 60) last.depart to request.endTime else null
    }

    suspend fun addPlace() {
        val request = lastRequest ?: return
        val current = plan ?: return
        if (request.stops >= 6) return
        val r = request.copy(stops = request.stops + 1, keep = current.stops.map { it.key ?: it.momentId },
            conditions = null)
        fetchPlan(r, swap = true)
        client.event("add_place", mapOf("stops" to "${r.stops}"))
    }

    /** Decision 3: plans changed on the day: the rest of today from where they are, from about ten minutes from now. */
    suspend fun replanRest(reason: String) {
        val old = lastRequest ?: return
        val current = plan ?: return
        val now = Dates.now()
        val start = ((now.hour * 60 + now.minute + 14) / 5) * 5
        if (Dates.minutes(old.endTime) - start < 60) {
            notice = "Not much of the day left" to "There's less than an hour before your day ends, so there's nothing to re-plan."
            return
        }
        val upTo = minOf(nowIndex, current.stops.size)
        val done = current.stops.take(upTo).filter { it.rateable }.map { it.momentId }
        val skip = done.toMutableList()
        if (reason == "closed" && nowIndex < current.stops.size) skip += current.stops[nowIndex].momentId
        val left = current.stops.size - upTo
        val fromHere = if (location.usable) location.roundedHere() else null
        val at = if (nowIndex < current.stops.size) current.stops[nowIndex] else current.stops.lastOrNull()
        val request = PlanRequest(
            start = fromHere ?: at?.pin ?: old.start,
            startName = if (fromHere != null) "where you are" else (at?.title ?: old.startName),
            startTime = Dates.hhmm(start), endTime = old.endTime, date = Dates.todayIso(),
            stops = maxOf(2, minOf(6, if (reason == "tired") left - 1 else left)), familiar = false,
            exclude = (old.exclude + skip).toSet().sorted(), feelings = old.feelings,
            conditions = if (reason == "rain") PlanConditions(0.9) else null,
        )
        val tripId = currentTripDay()?.first?.id
        fetchPlan(request, sameDay = false)
        val new = plan ?: return
        if (new.id == current.id) return
        nowIndex = 0
        prefs.set("nowIndex.${new.id}", 0)
        if (tripId != null) findTrip(tripId)?.let { trip ->
            save(trip.copy(used = (trip.used + new.stops.filter { it.rateable }.map { it.base }).toSet().sorted()))
        }
        client.event("replan_rest", mapOf("reason" to reason, "stops" to "${request.stops}"))
    }

    suspend fun swap(stop: Stop) {
        var request = lastRequest ?: return
        val current = plan ?: return
        request = request.copy(keep = current.stops.filter { it.id != stop.id }.map { it.key ?: it.momentId },
            exclude = request.exclude + stop.momentId)
        if (request.intent?.get("must_do") == stop.momentId) request = request.copy(intent = null)
        val before = current.stops.map { it.momentId }.toSet()
        fetchPlan(request, swap = true)
        val now = plan
        if (now != null && now.id != current.id) {
            swappedIn = now.stops.firstOrNull { it.momentId !in before }?.momentId
            client.event("swap_stop", mapOf("out" to stop.momentId, "in" to (swappedIn ?: "")))
        }
    }

    /** `sameDay`: the same day changed (swap, plan again, re-plan), so a trip day it came from takes the new stops. */
    private suspend fun fetchPlan(request: PlanRequest, swap: Boolean = false, sameDay: Boolean = true) {
        val old = plan
        run {
            val p = client.makePlan(request)
            if (p.stops.isEmpty()) {
                errorMessage = "Nothing fits that day and time. Try a longer stretch of the day, or another day."
                return@run
            }
            val must = request.intent?.get("must_do")
            if (must != null && p.stops.none { it.base == must }) {
                notice = "Your must-include didn't fit" to
                    "It's closed or can't be fitted at those times, so the day is planned without it."
            }
            if (sameDay) syncTripDay(old, p)
            plan = p
            lastRequest = request
            if (!swap) {
                val r = prefs.ratings(p.id)
                rated = r.keys
                myRatings = r
                swappedIn = null
                revealPlanId = p.id
            } else {
                prefs.saveRatings(p.id, myRatings)
            }
            files.save(Plan.serializer(), p, "plan.json")
            files.save(PlanRequest.serializer(), request, "request.json")
            if (remindersOn) reminders.schedule(p, rated)
        }
    }

    /** `planId`: another plan the stop belongs to (the place on the way on an arrival day). */
    suspend fun rate(stop: Stop, rating: Int, wouldBring: Boolean?, planId: Int? = null) {
        val request = RatingRequest(stop.momentId, rating, planId ?: plan?.id, wouldBring)
        lastRatingQueued = false
        run {
            try {
                client.rate(request)
            } catch (e: IOException) {
                // journey audit: no signal (the Tube, a basement): kept on the phone and sent when it's back
                pendingRatings = pendingRatings.filterNot { it.planId == request.planId && it.momentId == request.momentId } +
                    request
                files.save(ListSerializer(RatingRequest.serializer()), pendingRatings, "pending_ratings.json")
                lastRatingQueued = true
            }
            rated = rated + stop.momentId
            myRatings = myRatings + (stop.momentId to rating)
            plan?.let { prefs.saveRatings(it.id, myRatings) }
            ratedOnce = true
            prefs.set("ratedOnce", true)
            reminders.cancel(stop)
        }
        if (!lastRatingQueued) sendPendingRatings()
    }

    suspend fun sendPendingRatings() {
        if (client.token == null || sendingRatings) return
        sendingRatings = true
        try {
            while (pendingRatings.isNotEmpty()) {
                val next = pendingRatings.first()
                try {
                    client.rate(next)
                } catch (e: BrainError) {
                    if (e.code != 404 && e.code != 422) return
                } catch (e: Exception) {
                    return
                }
                pendingRatings = pendingRatings.drop(1)
                files.save(ListSerializer(RatingRequest.serializer()), pendingRatings.ifEmpty { null }, "pending_ratings.json")
            }
        } finally {
            sendingRatings = false
        }
    }

    // ---- D118: rating reminders, asked once, right after a plan is made ---------------------------------------

    /** `granted`: the answer to Android's own prompt (asked by the screen only after a yes). */
    suspend fun answerReminders(yes: Boolean, granted: Boolean) {
        reminderAsked = true
        prefs.set("reminderAsked", true)
        remindersOn = yes && granted
        prefs.set("remindersOn", remindersOn)
        if (yes && !remindersOn) {
            notice = "Notifications are off for ODYS" to
                "To get a reminder to rate each stop, turn on notifications for ODYS in your phone's Settings."
        }
        plan?.let { if (remindersOn) reminders.schedule(it, rated) }
        client.event(if (remindersOn) "reminders_on" else "reminders_off")
    }

    suspend fun turnRemindersOff() {
        remindersOn = false
        prefs.set("remindersOn", false)
        reminders.clear()
        client.event("reminders_off")
    }

    /** A reminder was tapped: open that stop, where it's rated. */
    fun openStop(momentId: String) {
        val stop = plan?.stops?.firstOrNull { it.momentId == momentId } ?: return
        route = Route.Home
        tab = MainTab.Trip
        showNow = false
        tripPath.clear()
        tripPath += Dest.Day
        tripPath += Dest.StopCard(stop)
    }

    // ---- D119: "Now", during the day --------------------------------------------------------------------------

    fun startDay() {
        val p = plan ?: return
        nowIndex = prefs.int("nowIndex.${p.id}") ?: p.stops.indexOfFirst { it.momentId !in rated }.coerceAtLeast(0)
        showNow = true
        launch { client.event("start_day", mapOf("stop" to "$nowIndex")) }
    }

    fun advanceNow() {
        val p = plan ?: return
        nowIndex = minOf(nowIndex + 1, p.stops.size)
        prefs.set("nowIndex.${p.id}", nowIndex)
    }

    // ---- D118: Help & safety replies ------------------------------------------------------------------------

    suspend fun loadSafety() {
        if (!prefs.bool("safetySent")) return
        runCatching { client.mySafety() }.getOrNull()?.let { safetyThreads = it }
    }

    val unreadSafety: Boolean
        get() {
            val seen = prefs.string("safetySeen") ?: ""
            return safetyThreads.flatMap { it.replies }.any { it.createdAt > seen }
        }

    fun markSafetySeen() {
        val latest = safetyThreads.flatMap { it.replies }.maxOfOrNull { it.createdAt } ?: ""
        prefs.set("safetySeen", latest)
    }

    suspend fun sendSafety(message: String, contact: String?): String? {
        var reply: String? = null
        run {
            reply = client.safety(message, contact)
            prefs.set("safetySent", true)
        }
        loadSafety()
        return reply
    }

    /** D127: "Was today worth what you spent?" and "Would you do this day again?", kept on the phone per plan and
     *  sent as each is tapped (the Brain keeps the latest). */
    fun dayFeedback(planId: Int): DayFeedback =
        prefs.string("dayFeedback.$planId")?.let { runCatching { BrainJson.decodeFromString(DayFeedback.serializer(), it) }.getOrNull() }
            ?: DayFeedback()

    fun answerDay(planId: Int, answer: DayFeedback) = launch {
        prefs.set("dayFeedback.$planId", BrainJson.encodeToString(DayFeedback.serializer(), answer))
        runCatching { client.dayFeedback(planId, answer) }
    }

    fun planAnotherDay() = launch { client.event("plan_another_day") }

    suspend fun deleteMyData() {
        run {
            try {
                client.deleteMe()
            } catch (e: IOException) {
                client.token?.let { tokens.save(it, TokenStore.PENDING_DELETE) }
                client.forget()
                clearLocal()
                notice = "Deleted from this phone" to "The rest is deleted from the planner the next time ODYS is online."
                return@run
            }
            clearLocal()
        }
    }

    suspend fun finishPendingDelete() {
        val old = tokens.load(TokenStore.PENDING_DELETE) ?: return
        if (client.deleteOld(old)) tokens.delete(TokenStore.PENDING_DELETE)
    }

    /** Everything about the person kept on this phone, removed; back to Welcome. */
    fun clearLocal() {
        for (k in listOf("onboardingDone", "improved", "morePlacesDone", "moreTasksDone", "onboardingStep", "ratedOnce",
            "remindersOn", "reminderAsked", "safetySent", "safetySeen", "surveyDone", "pairDone", "testerCode",
            "testBPlanId")) prefs.remove(k)
        for (k in prefs.keys()) if (k.startsWith("ratings.") || k.startsWith("nowIndex.")) prefs.remove(k)
        for (f in listOf("plan.json", "request.json", "profile.json", "trips.json", "pending_ratings.json", "handoff.json")) {
            files.delete(f)
        }
        plan = null
        lastRequest = null
        improved = false
        morePlacesDone = false
        moreTasksDone = false
        swappedIn = null
        rated = emptySet()
        onboarding = null
        reactions.clear()
        choices.clear()
        profile = Profile()
        why = emptyList()
        bestHour = ""
        bestHourMore = ""
        categoryAnswers.clear()
        learned = null
        reaction = null
        saidPatterns.clear()
        reminders.clear()
        ratedOnce = false
        remindersOn = false
        reminderAsked = false
        safetyThreads = emptyList()
        tripPath.clear()
        bookPath.clear()
        trips = emptyList()
        currentTripId = null
        book.reset()
        surveyDone = false
        pairDone = false
        pair = null
        tab = MainTab.Trip
        showNow = false
        step = Step.Based
        route = Route.Welcome
        myRatings = emptyMap()
        pendingRatings = emptyList()
        location.forget()
    }

    // ---- Build 2: what comes before the first plan -----------------------------------------------------------

    val needsPair: Boolean get() = !isVisitor && !pairDone && plan == null
    val needsFirstRun: Boolean get() = !surveyDone || needsPair

    fun sendSurvey(body: SurveyBody?) = launch {
        run {
            if (body != null) client.survey(body) else client.event("survey_skipped")
            surveyDone = true
            prefs.set("surveyDone", true)
        }
        if (surveyDone && isVisitor && plan == null) visitorFirstDay()
    }

    /** m176: visitors skip the Test B pair, so they get a first London day from their answers at once. */
    suspend fun visitorFirstDay() {
        makePlan(Dates.nextSaturday(), "12:00", "17:00", 4)
        if (plan == null) return
        client.event("visitor_first_day")
        tab = MainTab.Trip
        tripPath.clear()
        tripPath += Dest.Day
    }

    fun startPair(intent: PairIntent) = launch {
        run {
            pair = client.makePair(intent)
            if (pair?.done == true) {
                if (pair?.chosen != null) finishPair() else skipPair()
            }
        }
    }

    fun sendPairFeedback(chosen: String, fit1: Int, fit2: Int, why: String, voice: Boolean) = launch {
        val text = why.trim()
        run {
            try {
                pair = client.pairFeedback(PairFeedback(chosen, fit1, fit2, text.ifEmpty { null },
                    if (voice) "voice" else "typed"))
            } catch (e: BrainError) {
                if (e.code == 409) pair = client.pair() else throw e
            }
        }
    }

    fun skipPair() {
        pairDone = true
        prefs.set("pairDone", true)
        showPair = false
        launch { client.event("pair_skipped") }
    }

    fun finishPair() {
        val chosen = pair?.chosen ?: return
        pairDone = true
        prefs.set("pairDone", true)
        plan = chosen
        lastRequest = null
        prefs.set("testBPlanId", chosen.id)
        val r = prefs.ratings(chosen.id)
        rated = r.keys
        myRatings = r
        revealPlanId = chosen.id
        files.save(Plan.serializer(), chosen, "plan.json")
        files.delete("request.json")
        showPair = false
        tab = MainTab.Trip
        tripPath.clear()
        tripPath += Dest.Day
    }

    // ---- D120: trips ---------------------------------------------------------------------------------------------

    val currentTrip: Trip? get() = trips.firstOrNull { it.id == currentTripId } ?: trips.firstOrNull()

    fun findTrip(id: String): Trip? = trips.firstOrNull { it.id == id }

    fun save(trip: Trip) {
        val i = trips.indexOfFirst { it.id == trip.id }
        trips = if (i >= 0) trips.toMutableList().also { it[i] = trip } else listOf(trip) + trips
        files.save(ListSerializer(Trip.serializer()), trips, "trips.json")
    }

    fun deleteTrip(id: String) {
        trips = trips.filter { it.id != id }
        if (currentTripId == id) currentTripId = trips.firstOrNull()?.id
        files.save(ListSerializer(Trip.serializer()), trips, "trips.json")
    }

    /** A blank trip for "Plan a trip": London, next Saturday, a weekend. */
    fun newTrip(): Trip {
        var t = Trip(start = Dates.nextSaturday().toString(), nights = 2, needFlight = profile.based == "abroad",
            feelings = why.take(2))
        if (profile.based == "uk") t = t.copy(travelBy = "train", station = "KGX", arriveAt = "11:00", leaveAt = "17:00")
        return t
    }

    /** "From your answers": the first airport matching the town or city they gave, if any. */
    suspend fun guessOrigin(trip: Trip): Trip {
        if (trip.origin != null) return trip
        val city = profile.homeCity?.trim()
        if (city.isNullOrEmpty()) return trip
        val first = runCatching { client.places(city) }.getOrNull()?.firstOrNull() ?: return trip
        return trip.copy(origin = first, originGuessed = true)
    }

    /** "Make my trip": plans the first days (up to 7) and keeps the trip on the phone. */
    suspend fun makeTrip(draft: Trip, keepFrom: Trip? = null, keepChanged: Boolean = true): Boolean {
        var trip = draft
        var ok = false
        val today = Dates.todayIso()
        val sameDates = keepFrom != null && keepFrom.start == draft.start && keepFrom.nights == draft.nights
        val changed: Set<Int> = if (sameDates && keepChanged) (keepFrom?.changedDays ?: emptyList()).toSet() else emptySet()
        val kept: List<TripDayOut> = if (sameDates) (keepFrom?.days ?: emptyList()).filter { it.date < today || it.index in changed }
        else emptyList()
        trip = trip.copy(changedDays = if (sameDates) keepFrom?.changedDays?.filter { it in changed } else null)
        val keptIndex = kept.map { it.index }.toSet()
        val todo = (0 until draft.dayCount).filter { it !in keptIndex }.take(7)
        val exclude = momentBases(kept)
        val currentPlanId = plan?.id
        val yourDayIndex = keepFrom?.days?.firstOrNull { currentPlanId != null && it.plan?.id == currentPlanId }?.index
        run {
            if (kept.isEmpty() || todo.isNotEmpty()) {
                val out = client.tripDays(daysRequest(trip, if (kept.isEmpty()) emptyList() else todo, exclude))
                trip = trip.copy(days = (kept + out.days).sortedBy { it.index }, used = out.used, daysFrom = out.start)
            }
            trip = trip.copy(daysStale = false)
            save(trip)
            if (yourDayIndex != null && yourDayIndex !in keptIndex) {
                trip.days.firstOrNull { it.index == yourDayIndex }?.takeIf { it.plan != null }?.let { useDay(trip, it) }
            }
            currentTripId = trip.id
            if (book.resultsFor != trip.id) {
                book.flights = null
                book.stays = null
            }
            if (trip.nights == 0) trip.days.firstOrNull()?.takeIf { it.plan != null }?.let { useDay(trip, it) }
            client.event("trip_made", mapOf("nights" to "${trip.nights}", "flight" to if (trip.needFlight) "yes" else "no",
                "adults" to "${trip.adults}", "feelings" to trip.feelings.joinToString(",")))
            ok = true
        }
        return ok
    }

    private fun momentBases(days: List<TripDayOut>): List<String> =
        days.flatMap { (it.plan?.stops ?: emptyList()) + (it.before?.stops ?: emptyList()) }
            .filter { it.rateable }.map { it.base }.toSet().sorted()

    /** A later day ("planned as you go"), without any moment the trip already has. */
    suspend fun planDay(tripId: String, index: Int) {
        val trip0 = findTrip(tripId) ?: return
        run {
            val out = client.tripDays(daysRequest(trip0, listOf(index), trip0.used))
            var days = trip0.days
            for (d in out.days) days = days.filter { it.index != d.index } + d
            save(trip0.copy(days = days.sortedBy { it.index }, used = out.used))
        }
    }

    /** The days again, from the chosen stay and around the flight's times. */
    suspend fun replanDays(tripId: String) {
        val trip = findTrip(tripId) ?: return
        makeTrip(trip, keepFrom = trip, keepChanged = false)
    }

    private fun daysRequest(trip: Trip, days: List<Int>, exclude: List<String>,
                            hours: Triple<String, String, Int>? = null): TripDaysRequest {
        val (arrive, leave) = trip.ends
        return TripDaysRequest(trip.destination, trip.start, trip.nights, trip.feelings, trip.stay?.point,
            if (trip.stay == null) null else "your stay", days, exclude, hours?.first ?: trip.dayFrom,
            hours?.second ?: trip.dayTo, hours?.third ?: trip.placesPerDay, trip.travelLight, arrive, leave)
    }

    /** "Make this my day": a trip's day becomes the current plan, with "Now", rating, swap and plan again. */
    fun useDay(trip: Trip, day: TripDayOut) {
        val dayPlan = day.plan ?: return
        val mine = dayPlan.stops.map { it.base }.toSet()
        val window = day.window ?: DayWindow("10:00", "18:00", dayPlan.stops.size)
        val request = PlanRequest(trip.stay?.point ?: AppConfig.START, trip.daysFrom ?: AppConfig.START_NAME,
            window.start, window.end, day.date, maxOf(2, minOf(window.stops, 6)), false,
            exclude = trip.used.filter { it !in mine }, feelings = trip.feelings.ifEmpty { null })
        plan = dayPlan
        lastRequest = request
        val r = prefs.ratings(dayPlan.id)
        rated = r.keys
        myRatings = r
        swappedIn = null
        files.save(Plan.serializer(), dayPlan, "plan.json")
        files.save(PlanRequest.serializer(), request, "request.json")
        if (remindersOn) reminders.schedule(dayPlan, rated)
    }

    /** m176: the plan chosen in the Test B comparison, not rated yet: replacing it asks first. */
    val testBPlanAtRisk: Boolean
        get() {
            val p = plan ?: return false
            if (p.id != prefs.int("testBPlanId") || rated.isNotEmpty()) return false
            return (p.date ?: "") >= Dates.todayIso()
        }

    private fun dayIndex(trip: Trip, date: LocalDate): Int? {
        val i = ChronoUnit.DAYS.between(trip.startDate, date).toInt()
        return if (i in 0 until trip.dayCount) i else null
    }

    /** During a trip: today's day (planned or not), unless today's plan is already "your day". */
    fun todayInTrip(): Triple<Trip, Int, TripDayOut?>? {
        val today = Dates.today()
        if (plan?.date == today.toString()) return null
        for (trip in trips) {
            val i = dayIndex(trip, today) ?: continue
            return Triple(trip, i, trip.days.firstOrNull { it.index == i })
        }
        return null
    }

    /** The trip day the current plan is. */
    fun currentTripDay(): Pair<Trip, TripDayOut>? {
        val p = plan ?: return null
        for (trip in trips) trip.days.firstOrNull { it.plan?.id == p.id }?.let { return trip to it }
        return null
    }

    /** At the end of a trip's day: the next day of the same trip, if there is one. */
    fun nextTripDay(): Triple<Trip, Int, TripDayOut?>? {
        val p = plan ?: return null
        for (trip in trips) {
            val current = trip.days.firstOrNull { it.plan?.id == p.id }
                ?: (if (trip.id == currentTripId) trip.days.firstOrNull { it.date == p.date } else null) ?: continue
            val i = current.index + 1
            if (i >= trip.dayCount) return null
            return Triple(trip, i, trip.days.firstOrNull { it.index == i })
        }
        return null
    }

    /** The trip day dated tomorrow, to look at ahead of time. */
    fun tomorrowInTrip(): Triple<Trip, Int, TripDayOut?>? {
        val tomorrow = Dates.today().plusDays(1)
        for (trip in trips) {
            val i = dayIndex(trip, tomorrow) ?: continue
            return Triple(trip, i, trip.days.firstOrNull { it.index == i })
        }
        return null
    }

    suspend fun planTripDayIfNeeded(tripId: String, index: Int) {
        if (findTrip(tripId)?.days?.any { it.index == index } != true) planDay(tripId, index)
    }

    fun openTripDay(tripId: String, index: Int, from: String) {
        tab = MainTab.Trip
        showNow = false
        tripPath.clear()
        tripPath += Dest.TripOverview(tripId)
        tripPath += Dest.TripDay(tripId, index)
        launch { client.event("trip_day_previewed", mapOf("from" to from, "day" to "${index + 1}")) }
    }

    /** One day planned again at the hours the person is free and with their places. */
    suspend fun changeTripDay(tripId: String, index: Int, from: String, to: String, places: Int): Boolean {
        val trip = findTrip(tripId) ?: return false
        val old = trip.days.firstOrNull { it.index == index }
        val own = ((old?.plan?.stops ?: emptyList()) + (old?.before?.stops ?: emptyList()))
            .filter { it.rateable }.map { it.base }.toSet()
        val request = daysRequest(trip, listOf(index), trip.used.filter { it !in own }, Triple(from, to, places))
        var ok = false
        run {
            val out = client.tripDays(request)
            val new = out.days.firstOrNull { it.index == index } ?: return@run
            val t = trip.copy(days = (trip.days.filter { it.index != index } + new).sortedBy { it.index }, used = out.used,
                changedDays = ((trip.changedDays ?: emptyList()) + index).toSet().sorted())
            save(t)
            val was = old?.plan
            if (was != null && plan?.id == was.id && new.plan != null) useDay(t, new)
            client.event("trip_day_changed", mapOf("day" to "${index + 1}", "from" to from, "to" to to,
                "places" to "$places"))
            ok = true
        }
        return ok
    }

    /** "Start today's day" / "Tomorrow: Day 3": plans the day first if needed. */
    suspend fun goToTripDay(tripId: String, index: Int) {
        if (findTrip(tripId)?.days?.firstOrNull { it.index == index }?.plan == null) planDay(tripId, index)
        val trip = findTrip(tripId) ?: return
        val day = trip.days.firstOrNull { it.index == index }?.takeIf { it.plan != null } ?: return
        currentTripId = trip.id
        useDay(trip, day)
        client.event("trip_day_started", mapOf("day" to "${index + 1}", "of" to "${trip.dayCount}"))
    }

    /** The person said they booked it (or saved it for later) on the provider's site. */
    fun keep(choice0: TripChoice, tripId: String) {
        var trip = findTrip(tripId) ?: return
        if (choice0.kind == "flight" && choice0.landsNextDay == true && trip.nights >= 1) {
            trip = trip.copy(start = trip.startDate.plusDays(1).toString(), nights = trip.nights - 1)
            notice = "Your trip now starts on ${Dates.shortDay(trip.start)}" to
                "That's the day your flight lands, so your first day starts when you arrive. Plan the days again from the trip."
        }
        val choice = choice0.copy(forStart = trip.start, forNights = trip.nights)
        trip = if (choice.kind == "flight") trip.copy(flight = choice) else trip.copy(stay = choice)
        files.delete("handoff.json")
        save(trip.copy(daysStale = trip.days.isNotEmpty()))
        launch {
            client.event("handoff_answer", mapOf("kind" to choice.kind, "provider" to choice.provider,
                "answer" to if (choice.booked) "booked" else "saved"))
        }
    }

    /** m176: after a swap or "Plan again" on a trip's day, the trip keeps the new day. */
    private fun syncTripDay(old: Plan?, new: Plan) {
        if (old == null) return
        val trip = trips.firstOrNull { t -> t.days.any { it.plan?.id == old.id } } ?: return
        val days = trip.days.map { if (it.plan?.id == old.id) it.copy(plan = new) else it }
        fun base(p: Plan) = p.stops.filter { it.rateable }.map { it.base }.toSet()
        save(trip.copy(days = days, used = ((trip.used.toSet() - base(old)) + base(new)).sorted()))
    }

    fun removeChoice(kind: String, tripId: String) {
        val trip = findTrip(tripId) ?: return
        save((if (kind == "flight") trip.copy(flight = null) else trip.copy(stay = null)).copy(daysStale = trip.days.isNotEmpty()))
        launch { client.event("choice_removed", mapOf("kind" to kind)) }
    }

    // ---- the Book tab's search ---------------------------------------------------------------------------------

    fun searchSoon(delayMs: Long = 350) {
        book.job?.cancel()
        book.job = viewModelScope.launch {
            if (delayMs > 0) delay(delayMs)
            search()
        }
    }

    suspend fun search() {
        val trip = currentTrip ?: return
        if (book.resultsFor != trip.id) {
            book.flights = null
            book.stays = null
            book.resultsFor = trip.id
        }
        book.error = null
        if (trip.start < Dates.todayIso()) {
            book.error = "This trip has started, so there's nothing to search for its dates. To change a flight or add a night, use the airline's or the stay's own site."
            return
        }
        book.loading = true
        try {
            if (book.segment == "flights") {
                val origin = trip.origin
                if (trip.needFlight && origin != null) {
                    book.flights = client.flights(FlightSearch(origin.code, trip.destination, trip.start, trip.end,
                        trip.adults, book.flightFilters))
                }
            } else if (trip.needStay) {
                book.stays = client.stays(StaySearch(trip.destination, trip.start, trip.end, trip.adults,
                    maxOf(1, (trip.adults + 1) / 2), book.stayFilters))
            }
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            book.error = message(e)
        }
        book.loading = false
    }

    fun openHandoff(h: Handoff) {
        book.handoff = h
    }

    /** The screen opens the link; this keeps it on the phone for "Did you book it?". */
    fun handoffGone() {
        val h = book.handoff ?: return
        launch { client.event("handoff_open", mapOf("kind" to h.choice.kind, "provider" to h.provider)) }
        book.handoff = h.copy(back = true)
        currentTrip?.let { trip ->
            files.save(SavedHandoff.serializer(), SavedHandoff(h.provider, h.url, h.what, h.price, h.searchedAt, h.choice,
                trip.id, System.currentTimeMillis()), "handoff.json")
        }
    }

    private fun restoreHandoff() {
        val saved = files.load(SavedHandoff.serializer(), "handoff.json") ?: return
        files.delete("handoff.json")
        if (route != Route.Home || System.currentTimeMillis() - saved.at > 24 * 3600 * 1000 || findTrip(saved.tripId) == null) return
        currentTripId = saved.tripId
        tab = MainTab.Book
        book.handoff = Handoff(saved.provider, saved.url, saved.what, saved.price, saved.searchedAt, saved.choice, back = true)
    }

    // ---- the moments a plan can include ("Must include") -------------------------------------------------------

    var moments by mutableStateOf<List<MomentSummary>>(emptyList())

    suspend fun loadMoments() {
        if (moments.isEmpty()) moments = runCatching { client.moments() }.getOrDefault(emptyList())
    }

    // ---- sharing (D114) -------------------------------------------------------------------------------------

    suspend fun referral(): ReferralResponse? {
        var out: ReferralResponse? = null
        run { out = client.referral() }
        return out
    }

    /** When the app comes back to the front. */
    fun onResume() {
        clock = System.currentTimeMillis()
        launch {
            wake()
            sendPendingRatings()
            finishPendingDelete()
            loadSafety()
        }
    }
}
