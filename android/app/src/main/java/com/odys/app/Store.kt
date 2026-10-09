package com.odys.app

import android.content.Context
import android.content.SharedPreferences
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.LruCache
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKeys
import kotlinx.serialization.KSerializer
import kotlinx.serialization.Serializable
import kotlinx.serialization.builtins.MapSerializer
import kotlinx.serialization.builtins.serializer
import kotlinx.serialization.json.Json
import java.io.File

object AppConfig {
    const val CONSENT_VERSION = "app-2026-10-02"   // the same consent text as the iPhone app
    const val CONTACT_EMAIL = "abram@abdurakhmonbek.com"
    /** Plans start from the Test B start point (D104): Charing Cross station, Trafalgar Square exit (TfL). */
    const val START_NAME = "Charing Cross station"
    val START = Point(51.507819, -0.126137)
    val BASE_URL: String = BuildConfig.BRAIN_BASE_URL
}

/**
 * The install token is a credential, so it's kept encrypted (Android's counterpart of the iPhone Keychain). Android
 * deletes it with the app, so a reinstall always starts afresh (the app isn't backed up: allowBackup is off).
 */
class TokenStore(context: Context) {
    private val prefs: SharedPreferences = try {
        EncryptedSharedPreferences.create(
            "odys-secure", MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC), context,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
        )
    } catch (e: Exception) {
        context.getSharedPreferences("odys-secure-fallback", Context.MODE_PRIVATE)
    }

    fun save(value: String, account: String = "install-token") = prefs.edit().putString(account, value).apply()
    fun load(account: String = "install-token"): String? = prefs.getString(account, null)
    fun delete(account: String = "install-token") = prefs.edit().remove(account).apply()

    companion object {
        /** m176: the token of a "Delete my data" made with no signal, kept until the Brain has deleted it too. */
        const val PENDING_DELETE = "pending-delete"
    }
}

/** Small settings (UserDefaults on the iPhone). */
class Prefs(context: Context) {
    val sp: SharedPreferences = context.getSharedPreferences("odys", Context.MODE_PRIVATE)

    fun bool(key: String) = sp.getBoolean(key, false)
    fun int(key: String): Int? = if (sp.contains(key)) sp.getInt(key, 0) else null
    fun string(key: String): String? = sp.getString(key, null)
    fun set(key: String, value: Boolean) = sp.edit().putBoolean(key, value).apply()
    fun set(key: String, value: Int) = sp.edit().putInt(key, value).apply()
    fun set(key: String, value: String?) =
        if (value == null) sp.edit().remove(key).apply() else sp.edit().putString(key, value).apply()
    fun remove(key: String) = sp.edit().remove(key).apply()
    fun keys(): Set<String> = sp.all.keys

    /** Journey audit: which stops of a plan were rated, and how, kept per plan. */
    fun ratings(planId: Int): Map<String, Int> {
        val text = string("ratings.$planId") ?: return emptyMap()
        return runCatching { Json.decodeFromString(MapSerializer(String.serializer(), Int.serializer()), text) }
            .getOrDefault(emptyMap())
    }

    fun saveRatings(planId: Int, ratings: Map<String, Int>) =
        set("ratings.$planId", Json.encodeToString(MapSerializer(String.serializer(), Int.serializer()), ratings))
}

/** The current plan, its request, the trips and the like, kept as JSON files on the phone. */
class Files(private val context: Context) {
    private fun file(name: String) = File(context.filesDir, name)

    fun <T> save(serializer: KSerializer<T>, value: T?, name: String) {
        val f = file(name)
        if (value == null) {
            f.delete()
            return
        }
        runCatching {
            val tmp = File(context.filesDir, "$name.tmp")
            tmp.writeText(BrainJson.encodeToString(serializer, value))
            tmp.renameTo(f)
        }
    }

    fun <T> load(serializer: KSerializer<T>, name: String): T? {
        val f = file(name)
        if (!f.exists()) return null
        return runCatching { BrainJson.decodeFromString(serializer, f.readText()) }.getOrNull()
    }

    fun delete(name: String) {
        file(name).delete()
    }
}

/**
 * The moment cards' photos (Abram, 30 Sep): openly licensed photos from Wikimedia Commons, bundled with their credits
 * in assets/photos/photo-credits.json, until Abram's own replace them. A card without one keeps its field of colour.
 */
@Serializable
data class CardPhoto(val file: String, val title: String, val author: String, val licence: String, val source: String) {
    /** The credit the licence asks for (title, author, source, licence), shown under the picture. */
    val credit: String get() = "“$title” by $author, $licence, Wikimedia Commons (resized)"
}

object CardPhotos {
    private var all: Map<String, CardPhoto>? = null
    private val cache = LruCache<String, Bitmap>(12)

    fun all(context: Context): Map<String, CardPhoto> {
        all?.let { return it }
        val loaded = runCatching {
            val text = context.assets.open("photos/photo-credits.json").bufferedReader().use { it.readText() }
            Json { ignoreUnknownKeys = true }.decodeFromString(MapSerializer(String.serializer(), CardPhoto.serializer()), text)
        }.getOrDefault(emptyMap())
        all = loaded
        return loaded
    }

    /** The card behind a plan stop: "<card>#lunch" is the same card as lunch; "lunch@…" slots have no card. */
    fun cardId(momentId: String): String? = if (momentId.startsWith("lunch@")) null else momentId.substringBefore("#")

    fun info(context: Context, momentId: String): CardPhoto? = cardId(momentId)?.let { all(context)[it] }

    fun photo(context: Context, momentId: String): Pair<CardPhoto, Bitmap>? {
        val info = info(context, momentId) ?: return null
        cache.get(info.file)?.let { return info to it }
        val bitmap = runCatching {
            context.assets.open("photos/${info.file}").use { BitmapFactory.decodeStream(it) }
        }.getOrNull() ?: return null
        cache.put(info.file, bitmap)
        return info to bitmap
    }
}
