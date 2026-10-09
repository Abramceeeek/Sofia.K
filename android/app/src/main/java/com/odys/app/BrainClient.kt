package com.odys.app

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import kotlinx.serialization.ExperimentalSerializationApi
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonNamingStrategy
import kotlinx.serialization.serializer
import okhttp3.Call
import okhttp3.Callback
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import java.io.IOException
import java.util.concurrent.TimeUnit
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/** An answer from the Brain that wasn't a success. */
class BrainError(val code: Int) : Exception(
    when (code) {
        401 -> "This phone isn't registered any more. Please start again."
        -1 -> "Please agree to take part first."
        else -> "The planner answered with an error ($code). Please try again."
    }
)

/**
 * The Brain's snake_case names. The naming strategy also rewrites names given with @SerialName, so the "this or that"
 * days' "A" and "B" are kept as they are (snake_case would make them "a" and "b").
 */
@OptIn(ExperimentalSerializationApi::class)
private object BrainNames : JsonNamingStrategy {
    override fun serialNameForJson(descriptor: kotlinx.serialization.descriptors.SerialDescriptor, elementIndex: Int,
                                   serialName: String): String =
        if (serialName.length == 1 && serialName[0].isUpperCase()) serialName
        else JsonNamingStrategy.SnakeCase.serialNameForJson(descriptor, elementIndex, serialName)
}

@OptIn(ExperimentalSerializationApi::class)
val BrainJson = Json {
    namingStrategy = BrainNames
    ignoreUnknownKeys = true
    explicitNulls = false
    encodeDefaults = true
    coerceInputValues = true
}

/** Talks to the Brain (brain/src/brain/api.py), as app/Sources/BrainClient.swift does. */
class BrainClient(val base: String, private val tokens: TokenStore) {
    var token: String? = tokens.load()

    // The free server sleeps after 15 min idle and takes about a minute to wake (D109), so wait long.
    private val http = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(90, TimeUnit.SECONDS)
        .callTimeout(120, TimeUnit.SECONDS)
        .build()

    // ---- the calls the app makes -----------------------------------------------------------

    /** Starts waking the free server as the app opens. Fire and forget. */
    suspend fun wake() {
        runCatching { raw("GET", "v1/health", null, auth = false) }
    }

    /** Returns the channel the Brain counted the install in. */
    suspend fun install(research: Boolean, src: String = "app", code: String? = null): String? {
        val body = InstallRequest("stranger", src, ConsentBody(AppConfig.CONSENT_VERSION, research, false), code)
        val out: InstallResponse = call("POST", "v1/installs", body, auth = false)
        token = out.token
        tokens.save(out.token)
        return out.channel
    }

    suspend fun onboarding(): Onboarding = call("GET", "v1/onboarding")
    suspend fun sendAnswers(items: List<AnswerItem>) = send("POST", "v1/me/answers", AnswerItems(items))
    suspend fun sendSwipes(items: List<SwipeItem>) = send("POST", "v1/me/swipes", SwipeItems(items))
    suspend fun sendCategories(items: List<CategoryItem>) = send("POST", "v1/me/categories", CategoryItems(items))
    suspend fun summary(): Learned = call("GET", "v1/me/summary")
    suspend fun sendCorrections(ids: List<String>) = send("POST", "v1/me/corrections", CorrectionsRequest(ids))
    suspend fun sendChoices(items: List<ChoiceItem>) = send("POST", "v1/me/conjoint", ChoiceItems(items))
    suspend fun sendProfile(profile: Profile) = send("PUT", "v1/me/profile", profile)
    suspend fun makePlan(request: PlanRequest): Plan = call("POST", "v1/me/plans", request)
    suspend fun moments(): List<MomentSummary> = call("GET", "v1/moments?plannable_only=true")
    suspend fun referral(): ReferralResponse = call("GET", "v1/me/referral")
    suspend fun rate(request: RatingRequest) = send("POST", "v1/me/ratings", request)

    suspend fun safety(message: String, contact: String?): String {
        val out: SafetyResponse = call("POST", "v1/me/safety", SafetyRequest(message, contact))
        return out.message
    }

    suspend fun mySafety(): List<SafetyThread> = call("GET", "v1/me/safety")

    // ---- Build 2: the survey and the blind Test B pair ----
    suspend fun survey(body: SurveyBody) = send("POST", "v1/me/survey", body)
    suspend fun pair(): PairResponse = call("GET", "v1/me/testb/pair")
    suspend fun makePair(intent: PairIntent): PairResponse = call("POST", "v1/me/testb/pair", intent)
    suspend fun pairFeedback(body: PairFeedback): PairResponse = call("POST", "v1/me/testb/pair/feedback", body)

    // ---- D120: trips ----
    suspend fun places(query: String): List<TripPlace> =
        call("GET", "v1/trips/places?q=" + java.net.URLEncoder.encode(query, "UTF-8"))

    suspend fun flights(search: FlightSearch): FlightResults = call("POST", "v1/trips/flights", search)
    suspend fun stays(search: StaySearch): StayResults = call("POST", "v1/trips/stays", search)
    suspend fun tripDays(request: TripDaysRequest): TripDaysResponse = call("POST", "v1/me/trips/days", request)

    suspend fun event(name: String, props: Map<String, String> = emptyMap()) {
        runCatching { send("POST", "v1/me/events", EventRequest(name, props)) }
    }

    /** The Brain no longer knows this phone's token, so it's dropped and the person starts again. */
    fun forget() {
        token = null
        tokens.delete()
    }

    /** m176: finishes a deletion made with no signal, with the old token. */
    suspend fun deleteOld(old: String): Boolean = withContext(Dispatchers.IO) {
        val req = Request.Builder().url(base.trimEnd('/') + "/v1/me").delete()
            .header("Authorization", "Bearer $old").build()
        runCatching { http.newCall(req).execute().use { it.code in 200..299 || it.code == 401 || it.code == 404 } }
            .getOrDefault(false)
    }

    suspend fun deleteMe() {
        raw("DELETE", "v1/me", null)
        forget()
    }

    // ---- plumbing -------------------------------------------------------------------------------

    private suspend inline fun <reified Out> call(method: String, path: String, auth: Boolean = true): Out {
        val text = raw(method, path, null, auth)
        return BrainJson.decodeFromString(serializer<Out>(), text)
    }

    private suspend inline fun <reified In, reified Out> call(method: String, path: String, body: In,
                                                             auth: Boolean = true): Out {
        val text = raw(method, path, BrainJson.encodeToString(serializer<In>(), body), auth)
        return BrainJson.decodeFromString(serializer<Out>(), text)
    }

    private suspend inline fun <reified In> send(method: String, path: String, body: In) {
        raw(method, path, BrainJson.encodeToString(serializer<In>(), body))
    }

    suspend fun raw(method: String, path: String, body: String?, auth: Boolean = true): String {
        val url = (base.trimEnd('/') + "/" + path).toHttpUrl()
        val builder = Request.Builder().url(url)
        if (auth) {
            val t = token ?: throw BrainError(-1)
            builder.header("Authorization", "Bearer $t")
        }
        val rb = body?.toRequestBody("application/json".toMediaType())
        builder.method(method, rb ?: if (method == "POST" || method == "PUT") "".toRequestBody() else null)
        val response = http.newCall(builder.build()).await()
        response.use {
            val text = it.body?.string() ?: ""
            if (it.code !in 200..299) throw BrainError(it.code)
            return text
        }
    }
}

/** OkHttp's call, cancelled when the coroutine is. */
suspend fun Call.await(): Response = suspendCancellableCoroutine { cont ->
    enqueue(object : Callback {
        override fun onResponse(call: Call, response: Response) = cont.resume(response)
        override fun onFailure(call: Call, e: IOException) {
            if (!cont.isCancelled) cont.resumeWithException(e)
        }
    })
    cont.invokeOnCancellation { runCatching { cancel() } }
}
