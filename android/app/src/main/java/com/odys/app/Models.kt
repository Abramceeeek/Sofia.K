package com.odys.app

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// What the Brain sends and receives (brain/src/brain/api.py). JSON keys are snake_case; the Json in BrainClient
// converts the camelCase names here (JsonNamingStrategy.SnakeCase). The same shapes as app/Sources/Models.swift.

@Serializable
data class Point(val lat: Double, val lon: Double)

// ---- onboarding (GET /v1/onboarding) ------------------------------------------------------

@Serializable
data class Onboarding(
    val openQuestions: List<OpenQuestion> = emptyList(),
    val whyTravel: Choices = Choices("", emptyList()),
    val conjoint: Prompt? = null,
    val swipe: Prompt? = null,
    val swipePlaces: List<SwipePlace> = emptyList(),          // D112: before the first plan (6)
    val swipePlacesLater: List<SwipePlace>? = null,           // in "Improve future plans" (4)
    val conjointTasks: List<ConjointTask> = emptyList(),      // before the first plan (5)
    val conjointTasksLater: List<ConjointTask>? = null,       // in "Improve future plans" (5)
    val aboutYou: List<Question> = emptyList(),
    val photos: List<ScaleQuestion> = emptyList(),
    val fields: Fields? = null,
    val exampleShotCard: Card? = null,
    val based: BasedQuestion? = null,                         // D116
    val categoryCards: List<CategoryCard>? = null,            // D116
    val categories: CategoriesPrompt? = null,
    val conjointWords: List<PatternWords>? = null,            // D117
    val summary: SummaryText? = null,                         // D117
    val testb: TestBText? = null,                             // Build 2
    val survey: SurveyText? = null,                           // Build 2
)

@Serializable
data class TestBText(
    val intentTitle: String? = null,
    val moodPrompt: String? = null,
    val companyPrompt: String? = null,
    val wishPrompt: String? = null,
    val intro: String? = null,
    val choosePrompt: String? = null,
    val fitPrompt: String? = null,
    val fitScale: String? = null,
    val whyPrompt: String? = null,
)

@Serializable
data class SurveyText(
    val title: String? = null,
    val understood: String? = null,
    val likePerson: String? = null,
    val scale: String? = null,
    val typedOrSpoke: String? = null,
    val intrusive: String? = null,
)

@Serializable
data class PatternWords(val attr: String, val low: String, val high: String)

/** D117: what to say after an answer. */
@Serializable
data class Reactions(val loved: String? = null, val didntEnjoy: String? = null, val wantYes: String? = null) {
    fun text(answer: String): String? = when (answer) {
        "loved" -> loved
        "didnt_enjoy" -> didntEnjoy
        "want_yes" -> wantYes
        else -> null
    }
}

@Serializable
data class SummaryText(val title: String? = null, val note: String? = null, val empty: String? = null,
                       val changeNote: String? = null)

/** D117: "So far, I've learned…" (GET /v1/me/summary). */
@Serializable
data class Learned(
    val title: String? = null,
    val note: String? = null,
    val empty: String? = null,
    val changeNote: String? = null,
    val items: List<LearnedItem> = emptyList(),
)

@Serializable
data class LearnedItem(val id: String, val text: String)

@Serializable
data class BasedQuestion(val prompt: String, val options: List<String>, val cityPrompt: String? = null,
                         val note: String? = null)

@Serializable
data class CategoryCard(
    val key: String,
    val title: String,
    val line: String,
    val exampleId: String,
    val exampleTitle: String? = null,
    val reactions: Reactions? = null,
)

@Serializable
data class CategoriesPrompt(val prompt: String, val note: String? = null, val wantPrompt: String? = null)

@Serializable
data class OpenQuestion(
    val key: String,
    val title: String? = null,
    val text: String,
    val followUp: String? = null,
    val examples: List<String>? = null,
)

@Serializable
data class Choices(val prompt: String, val options: List<String>)

@Serializable
data class Prompt(val prompt: String, val noPreference: String? = null, val optionLabel: String? = null)

@Serializable
data class SwipePlace(val item: Int, val name: String, val reactions: Reactions? = null,
                      val photoIds: List<String>? = null)

@Serializable
data class ConjointTask(
    val task: Int,
    @SerialName("A") val a: String,
    @SerialName("B") val b: String,
    val levels: Map<String, List<Double>>? = null,
)

@Serializable
data class Question(val key: String, val text: String, val note: String? = null)

@Serializable
data class ScaleQuestion(val key: String, val text: String, val scale: String? = null, val exampleLabel: String? = null)

@Serializable
data class Fields(val question: String, val note: String, val options: List<FieldOption>)

@Serializable
data class FieldOption(val key: String, val label: String)

// ---- moments and plans ----------------------------------------------------------------------

@Serializable
data class Card(
    val id: String,
    val title: String,
    val place: Place,
    val approach: Approach? = null,
    val whatHappens: String? = null,
    val costGbp: Double? = null,
    val shotCard: ShotCard? = null,
)

@Serializable
data class Place(val name: String, val lat: Double? = null, val lon: Double? = null)

@Serializable
data class Approach(val from: String? = null, val path: String? = null, val stepFree: Boolean? = null)

@Serializable
data class ShotCard(val standAt: StandAt? = null, val face: String? = null, val frame: String? = null,
                    val `when`: String? = null, val avoid: String? = null)

@Serializable
data class StandAt(val lat: Double? = null, val lon: Double? = null, val note: String? = null)

@Serializable
data class Plan(
    val id: Int,
    val title: String? = null,
    val summary: List<String>? = null,
    val totals: Totals? = null,
    val date: String? = null,
    val stops: List<Stop> = emptyList(),
    val feelLine: String? = null,
    val basis: Basis? = null,
    val blind: Boolean? = null,
) {
    val isBlind: Boolean get() = blind == true
}

@Serializable
data class Reason(val you: String, val me: String? = null)

@Serializable
data class Basis(val places: Int = 0, val choices: Int = 0, val ratings: Int = 0, val feelings: Int = 0,
                 val kinds: Int? = null) {
    val soFar: String
        get() {
            fun n(k: Int, one: String, many: String) = if (k > 0) "$k ${if (k == 1) one else many}" else null
            val parts = listOfNotNull(n(places, "place", "places"), n(choices, "example day", "example days"),
                n(kinds ?: 0, "kind of place", "kinds of place"), n(feelings, "feeling", "feelings"),
                n(ratings, "rating", "ratings"))
            if (parts.isEmpty()) return "We'll learn more about you as you answer and rate stops."
            val list = if (parts.size == 1) parts[0] else parts.dropLast(1).joinToString(", ") + " and " + parts.last()
            return "From what you've told us so far: $list. It gets better as you rate stops."
        }
}

/** Cost per person, walking between stops and the finish time (brain.dayplan.plan_totals). */
@Serializable
data class Totals(
    val costGbp: Double = 0.0,
    val spendGbp: Double = 0.0,
    val transportGbp: Double = 0.0,
    val walkMin: Double = 0.0,
    val walkKm: Double = 0.0,
    val finish: String? = null,
)

@Serializable
data class ApproachStep(val label: String, val text: String)

@Serializable
data class Stop(
    val momentId: String,
    val key: String? = null,
    val title: String,
    val arrive: String,
    val depart: String,
    val travelMin: Double? = null,
    val travelMode: String? = null,
    val travelText: String = "",
    val approach: String = "",
    val what: String = "",
    val queueMin: Double? = null,
    val bestText: String = "",
    val costGbp: Double = 0.0,
    val costText: String = "",
    val rainSwap: String = "",
    val lunch: Boolean = false,
    val familiar: Boolean = false,
    val rateable: Boolean = true,
    val pin: Point? = null,
    val chosenFor: List<String> = emptyList(),
    val card: Card? = null,
    val worthGbp: Double? = null,
    val approachSteps: List<ApproachStep>? = null,
    val bestLight: String? = null,
    val bestWindow: String? = null,
    val reasons: List<Reason>? = null,
    val feelWord: String? = null,
    val reveal: Boolean? = null,
    val lines: List<String>? = null,
    val bookAhead: String? = null,
    val hours: String? = null,
    val checked: String? = null,
) {
    val id: String get() = "$momentId@$arrive"

    /** D118: the worth and the price side by side ("Worth about £32 to you · Free entry"). */
    val worthLine: String?
        get() = worthGbp?.let {
            "Worth about ${Money.text(it)} to you · " + if (costGbp == 0.0) "Free entry" else "Costs ${Money.text(costGbp)}"
        }

    /** The word for this stop on "How the day moves". */
    val word: String get() = feelWord ?: if (rateable) "Easy" else "Lunch"

    /** Build 2: a stop of the generic Test B plan ("generic:<i>"): rated, but nothing to share. */
    val isGeneric: Boolean get() = momentId.startsWith("generic:")

    val base: String get() = momentId.substringBefore("#")
}

// ---- requests ---------------------------------------------------------------------------------

@Serializable
data class InstallRequest(val channel: String, val src: String?, val consent: ConsentBody, val code: String? = null,
                          val platform: String? = "android")

@Serializable
data class ConsentBody(val version: String, val research: Boolean, val aiProcessing: Boolean)

@Serializable
data class InstallResponse(val userId: String, val token: String, val channel: String? = null)

@Serializable
data class ReferralResponse(val code: String, val text: String)

@Serializable
data class AnswerItem(val question: String, val text: String, val inputMode: String)

@Serializable
data class CorrectionsRequest(val items: List<String>)

@Serializable
data class CategoryItem(val key: String, val reaction: String, val want: String? = null)

@Serializable
data class SwipeItem(val item: Int, val reaction: String)

@Serializable
data class ChoiceItem(val task: Int, val choice: String)

@Serializable
data class AnswerItems(val items: List<AnswerItem>)

@Serializable
data class SwipeItems(val items: List<SwipeItem>)

@Serializable
data class ChoiceItems(val items: List<ChoiceItem>)

@Serializable
data class CategoryItems(val items: List<CategoryItem>)

/** "About you" (D19, D77): all optional. */
@Serializable
data class Profile(
    val whyTravel: List<String> = emptyList(),
    val budgetBand: String? = null,
    val company: String? = null,
    val chronotype: String? = null,
    val activity: String? = null,
    val grewUp: String? = null,
    val foodsAvoided: String? = null,
    val photosMatter: Int? = null,
    val shotCardAppeal: Int? = null,
    val fields: List<String> = emptyList(),
    val based: String? = null,              // D116: london | uk | abroad
    val homeCity: String? = null,           // D116: a town or city, never nationality
)

/** Kept on the phone with the plan, so "Swap this stop" can ask again with `keep` and `exclude` (D110). */
@Serializable
data class PlanRequest(
    val start: Point,
    val startName: String,
    val startTime: String,
    val endTime: String,
    val date: String?,
    val stops: Int,
    val familiar: Boolean,
    val keep: List<String> = emptyList(),
    val exclude: List<String> = emptyList(),
    val intent: Map<String, String>? = null,
    val feelings: List<String>? = null,
    val conditions: PlanConditions? = null,
)

@Serializable
data class PlanConditions(val rainProb: Double? = null)

@Serializable
data class MomentSummary(val id: String, val title: String, val status: String, val plannable: Boolean? = null)

@Serializable
data class RatingRequest(val momentId: String, val rating: Int, val planId: Int?, val wouldBring: Boolean?)

@Serializable
data class SafetyRequest(val message: String, val contact: String?)

@Serializable
data class SafetyThread(
    val id: Int,
    val message: String,
    val createdAt: String,
    val contactKept: Boolean = false,
    val replies: List<SafetyReplyItem> = emptyList(),
)

@Serializable
data class SafetyReplyItem(val text: String, val createdAt: String)

@Serializable
data class SafetyResponse(val alertId: Int, val message: String)

@Serializable
data class EventRequest(val name: String, val props: Map<String, String>)

// ---- Build 2: the survey and the blind Test B pair ------------------------------------------------------------

@Serializable
data class SurveyBody(val understood: Int?, val likePerson: Int?, val typedOrSpoke: String?, val intrusive: String?)

@Serializable
data class PairIntent(val mood: String? = null, val company: String? = null, val wish: String? = null)

@Serializable
data class PairPlan(
    val id: Int,
    val label: String,
    val title: String,
    val summary: List<String> = emptyList(),
    val totals: Totals = Totals(),
    val stops: List<Stop> = emptyList(),
    val fitRating: Int? = null,
)

@Serializable
data class PairResponse(
    val title: String,
    val intro: String? = null,
    val done: Boolean = false,
    val plans: List<PairPlan> = emptyList(),
    val personalLabel: String? = null,
    val chosenLabel: String? = null,
    val chosen: Plan? = null,
    val reveal: List<String>? = null,
)

@Serializable
data class PairFeedback(
    val chosen: String,
    @SerialName("fit_1") val fit1: Int,
    @SerialName("fit_2") val fit2: Int,
    val why: String?,
    val inputMode: String,
)
