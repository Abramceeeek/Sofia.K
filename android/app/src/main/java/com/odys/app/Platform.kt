package com.odys.app

import android.Manifest
import android.annotation.SuppressLint
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.location.Location as AndroidLocation
import android.location.LocationListener
import android.location.LocationManager
import android.os.Build
import android.os.Bundle
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import androidx.work.Data
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.Worker
import androidx.work.WorkerParameters
import java.time.LocalDate
import java.time.LocalTime
import java.time.ZonedDateTime
import java.util.concurrent.TimeUnit
import kotlin.math.roundToInt

/**
 * D123: where the person is while they're out, used on the phone only (app/Sources/Location.swift).
 * - Asked only when they start a day ("Now"), with ODYS's own question first and Android's prompt only after a yes.
 * - "While using the app" only: nothing runs in the background, and it stops when "Now" closes.
 * - Never sent to the Brain, except "Start from where I am", rounded to about 100 m and not kept there.
 */
class Location(private val context: Context, private val prefs: Prefs) {
    private val manager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
    var wanted by mutableStateOf(prefs.bool("locationOn"))
    var asked by mutableStateOf(prefs.bool("locationAsked"))
    var here by mutableStateOf<Point?>(null)
    var allowed by mutableStateOf(granted())
    var deniedBySettings by mutableStateOf(false)
    private var running = false

    private val listener = LocationListener { loc: AndroidLocation ->
        if (loc.hasAccuracy() && loc.accuracy < 200) here = Point(loc.latitude, loc.longitude)
    }

    private fun granted() = ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) ==
        PackageManager.PERMISSION_GRANTED || ContextCompat.checkSelfPermission(context,
        Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED

    val usable: Boolean get() = wanted && allowed

    /** "Yes, use my location": records the choice; the screen then asks Android (only if it hasn't been answered). */
    fun turnOn() {
        wanted = true
        asked = true
        prefs.set("locationOn", true)
        prefs.set("locationAsked", true)
        refresh()
    }

    fun turnOff() {
        wanted = false
        asked = true
        prefs.set("locationOn", false)
        prefs.set("locationAsked", true)
        stop()
        here = null
    }

    /** After Android's prompt (or coming back from Settings). */
    fun refresh(deniedNow: Boolean = false) {
        allowed = granted()
        if (deniedNow) deniedBySettings = true
        if (usable) start() else stop()
    }

    @SuppressLint("MissingPermission")
    fun start() {
        if (!usable || running) return
        running = true
        runCatching {
            for (p in listOf(LocationManager.GPS_PROVIDER, LocationManager.NETWORK_PROVIDER)) {
                if (manager.isProviderEnabled(p)) {
                    manager.requestLocationUpdates(p, 5000L, 20f, listener, Looper.getMainLooper())
                    manager.getLastKnownLocation(p)?.let { if (here == null) listener.onLocationChanged(it) }
                }
            }
        }
    }

    fun stop() {
        if (!running) return
        running = false
        runCatching { manager.removeUpdates(listener) }
    }

    fun forget() {
        stop()
        here = null
        wanted = false
        asked = false
        prefs.remove("locationOn")
        prefs.remove("locationAsked")
    }

    fun metres(p: Point): Double? {
        val h = here ?: return null
        val out = FloatArray(1)
        AndroidLocation.distanceBetween(h.lat, h.lon, p.lat, p.lon, out)
        return out[0].toDouble()
    }

    /** "Start from where I am": rounded to 3 decimal places (about 100 m), the only way a location leaves the phone. */
    fun roundedHere(): Point? = here?.let { Point(Math.round(it.lat * 1000) / 1000.0, Math.round(it.lon * 1000) / 1000.0) }

    companion object {
        /** "About 8 min walk": the straight line × 1.3 for streets, at 80 m a minute (GUESSES, as on the iPhone). */
        fun walkText(metres: Double): String {
            val minutes = (metres * 1.3 / 80).roundToInt()
            if (minutes <= 1) return "About a minute away"
            if (minutes <= 30) return "About $minutes min walk away"
            return String.format(java.util.Locale.UK, "About %.1f km away", metres / 1000)
        }
    }
}

/**
 * D118: rating reminders, set by the phone itself (nothing is sent to a server). One per stop, 10 minutes after the
 * stop's planned end, on the plan's day; tapping one opens that stop, where it's rated.
 */
class Reminders(private val context: Context) {
    private val work = WorkManager.getInstance(context)

    fun channel() {
        if (Build.VERSION.SDK_INT >= 26) {
            val nm = context.getSystemService(NotificationManager::class.java)
            nm.createNotificationChannel(NotificationChannel(CHANNEL, "Rating reminders",
                NotificationManager.IMPORTANCE_DEFAULT).apply { description = "One reminder after each stop of your day" })
        }
    }

    fun schedule(plan: Plan, rated: Set<String>) {
        clear()
        val day = Dates.parse(plan.date) ?: return
        for (stop in plan.stops) {
            if (!stop.rateable || stop.momentId in rated) continue
            val end = runCatching { LocalTime.parse(stop.depart.take(5)) }.getOrNull() ?: continue
            val at = ZonedDateTime.of(day, end, Dates.london).plusMinutes(AFTER_MINUTES)
            val wait = at.toInstant().toEpochMilli() - System.currentTimeMillis()
            if (wait <= 0) continue
            val req = OneTimeWorkRequestBuilder<ReminderWorker>()
                .setInitialDelay(wait, TimeUnit.MILLISECONDS)
                .setInputData(Data.Builder().putString("momentId", stop.momentId).putString("title", stop.title).build())
                .addTag(TAG)
                .build()
            work.enqueueUniqueWork(TAG + stop.momentId, ExistingWorkPolicy.REPLACE, req)
        }
    }

    fun cancel(stop: Stop) {
        work.cancelUniqueWork(TAG + stop.momentId)
    }

    fun clear() {
        work.cancelAllWorkByTag(TAG)
    }

    companion object {
        const val CHANNEL = "rate"
        const val TAG = "rate."
        const val AFTER_MINUTES = 10L
    }
}

class ReminderWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result {
        val id = inputData.getString("momentId") ?: return Result.success()
        val title = inputData.getString("title") ?: "Your stop"
        val open = Intent(applicationContext, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra("momentId", id)
        }
        val pi = PendingIntent.getActivity(applicationContext, id.hashCode(), open,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val n = NotificationCompat.Builder(applicationContext, Reminders.CHANNEL)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("How was it?")
            .setContentText("$title. One tap to rate it.")
            .setContentIntent(pi)
            .setAutoCancel(true)
            .build()
        runCatching { NotificationManagerCompat.from(applicationContext).notify(id.hashCode(), n) }
        return Result.success()
    }
}

/**
 * D115: "Tell it instead". Speech becomes text on the phone itself (on-device recognition only, never a server), live
 * into the answer box. No sound is recorded, saved or sent: only the text is, as if typed. If this phone can't
 * recognise speech on the device, the button isn't offered and the keyboard's own mic still works.
 */
class Dictation(private val context: Context) {
    var listening by mutableStateOf(false)
    var problem by mutableStateOf<String?>(null)
    private var recognizer: SpeechRecognizer? = null

    /** On-device recognition only (Android 12 and later, where the phone has it). */
    val available: Boolean
        get() = Build.VERSION.SDK_INT >= 31 && SpeechRecognizer.isOnDeviceRecognitionAvailable(context)

    fun start(onText: (String) -> Unit) {
        problem = null
        if (!available) {
            problem = "Speaking isn't available on this phone. You can type, or use the mic on your keyboard."
            return
        }
        if (Build.VERSION.SDK_INT < 31) return
        val r = SpeechRecognizer.createOnDeviceSpeechRecognizer(context)
        recognizer = r
        r.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {}
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(rmsdB: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {}
            override fun onError(error: Int) {
                if (error == SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS) {
                    problem = "To speak your answer, allow the microphone for ODYS in Settings. Or just type."
                }
                finish()
            }

            override fun onResults(results: Bundle?) {
                results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()?.let {
                    if (it.isNotEmpty()) onText(it)
                }
                finish()
            }

            override fun onPartialResults(partialResults: Bundle?) {
                partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()?.let {
                    if (it.isNotEmpty()) onText(it)
                }
            }

            override fun onEvent(eventType: Int, params: Bundle?) {}
        })
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-GB")
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
        }
        listening = true
        r.startListening(intent)
    }

    fun stop() {
        recognizer?.stopListening()
        listening = false
    }

    private fun finish() {
        listening = false
        recognizer?.destroy()
        recognizer = null
    }
}

/** Today's date at a given time, for "Plan a day". */
fun LocalDate.isToday() = this == Dates.today()
