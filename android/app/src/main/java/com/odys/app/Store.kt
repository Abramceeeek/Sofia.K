package com.odys.app

import android.content.Context
import android.content.SharedPreferences
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.LruCache
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Log
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKeys
import kotlinx.serialization.KSerializer
import kotlinx.serialization.Serializable
import kotlinx.serialization.builtins.MapSerializer
import kotlinx.serialization.builtins.serializer
import kotlinx.serialization.json.Json
import java.io.File
import java.security.GeneralSecurityException
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

object AppConfig {
    const val CONSENT_VERSION = "app-2026-10-02"   // the same consent text as the iPhone app
    const val CONTACT_EMAIL = "abram@abdurakhmonbek.com"
    /** Plans start from the Test B start point (D104): Charing Cross station, Trafalgar Square exit (TfL). */
    const val START_NAME = "Charing Cross station"
    val START = Point(51.507819, -0.126137)
    val BASE_URL: String = BuildConfig.BRAIN_BASE_URL
}

/**
 * m227: how the install token is sealed. Production: an AES-256-GCM key kept in the Android Keystore, which keeps key
 * material non-exportable (developer.android.com/privacy-and-security/keystore). Tests use a software key.
 */
interface TokenCipher {
    /** The 12-byte IV, then the ciphertext and its tag. */
    fun seal(plain: ByteArray): ByteArray
    /** Throws if the key is gone or the data has been changed; never returns wrong plaintext. */
    fun open(sealed: ByteArray): ByteArray
}

class KeystoreCipher(private val alias: String = "odys-install-token-v2") : TokenCipher {
    private fun keyStore() = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

    private fun existingKey(): SecretKey? = (keyStore().getEntry(alias, null) as? KeyStore.SecretKeyEntry)?.secretKey

    private fun newKey(): SecretKey {
        val gen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        gen.init(KeyGenParameterSpec.Builder(alias, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .build())
        return gen.generateKey()
    }

    override fun seal(plain: ByteArray): ByteArray {
        val c = Cipher.getInstance("AES/GCM/NoPadding")
        c.init(Cipher.ENCRYPT_MODE, existingKey() ?: newKey())
        return c.iv + c.doFinal(plain)
    }

    override fun open(sealed: ByteArray): ByteArray {
        require(sealed.size > IV) { "too short" }
        val key = existingKey() ?: throw GeneralSecurityException("no key")   // never a new key to read old data
        val c = Cipher.getInstance("AES/GCM/NoPadding")
        c.init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(128, sealed, 0, IV))
        return c.doFinal(sealed, IV, sealed.size - IV)
    }

    companion object { const val IV = 12 }
}

/** m227: the tokens kept by builds before the migration, read once so nobody is signed out by the upgrade. */
interface LegacyTokens {
    fun load(account: String): String?
    fun delete(account: String)
}

/**
 * The old store: androidx security-crypto's EncryptedSharedPreferences ("odys-secure"), deprecated in 2025 in favour of
 * the Keystore (developer.android.com/jetpack/androidx/releases/security), and its plain fallback ("odys-secure-fallback")
 * used when that couldn't start, which held the token in ordinary preferences. Opened only if an old file exists, and
 * only to read and then remove. The dependency stays until every install has migrated, then goes (after-9-Nov #90).
 */
@Suppress("DEPRECATION")
class LegacyTokenPrefs private constructor(context: Context) : LegacyTokens {
    private val encrypted: SharedPreferences? = try {
        EncryptedSharedPreferences.create(
            "odys-secure", MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC), context,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
        )
    } catch (e: Exception) {
        Log.w(TokenStore.TAG, "old token store unreadable: ${e.javaClass.simpleName}")
        null
    }
    private val plain: SharedPreferences = context.getSharedPreferences("odys-secure-fallback", Context.MODE_PRIVATE)

    override fun load(account: String): String? =
        runCatching { encrypted?.getString(account, null) }.getOrNull() ?: plain.getString(account, null)

    override fun delete(account: String) {
        runCatching { encrypted?.edit()?.remove(account)?.commit() }
        plain.edit().remove(account).commit()
    }

    companion object {
        /** Only when a file from an older build exists: a new install never touches the deprecated library. */
        fun ifPresent(context: Context): LegacyTokens? {
            val dir = File(context.applicationInfo.dataDir, "shared_prefs")
            val old = listOf("odys-secure.xml", "odys-secure-fallback.xml").any { File(dir, it).exists() }
            return if (old) LegacyTokenPrefs(context) else null
        }
    }
}

/**
 * The install token is a credential (Android's counterpart of the iPhone Keychain). m227: sealed with a Keystore key
 * in `noBackupFilesDir/tokens`, never in ordinary preferences and never logged. Android deletes it with the app, so a
 * reinstall always starts afresh (the app isn't backed up: allowBackup is off).
 *
 * Upgrading from an older build: the first read finds no sealed copy, reads the old store, seals it, reads it back,
 * and only then removes the old copy. If sealing or the check fails, the old copy stays and is used, so the person
 * isn't signed out, and the move is tried again next time. A sealed copy that can't be opened (the key is gone, or the
 * file was changed) reads as no token, or the old copy if there still is one; it never crashes.
 */
class TokenStore(
    private val dir: File,
    private val cipher: TokenCipher,
    private val legacy: LegacyTokens?,
) {
    constructor(context: Context) : this(File(context.noBackupFilesDir, "tokens"), KeystoreCipher(),
        LegacyTokenPrefs.ifPresent(context))

    private val memory = mutableMapOf<String, String>()   // this run only, for when sealing isn't possible

    private fun file(account: String) = File(dir, account)

    private fun write(account: String, sealed: ByteArray) {
        dir.mkdirs()
        val tmp = File(dir, "$account.tmp")
        tmp.writeBytes(sealed)
        if (!tmp.renameTo(file(account))) { tmp.delete(); throw java.io.IOException("not saved") }
    }

    private fun open(account: String): String? {
        val f = file(account)
        if (!f.exists()) return null
        return runCatching { String(cipher.open(f.readBytes()), Charsets.UTF_8) }
            .onFailure { Log.w(TAG, "sealed token unreadable: ${it.javaClass.simpleName}") }
            .getOrNull()
    }

    fun save(value: String, account: String = "install-token") {
        memory[account] = value
        val sealed = runCatching { write(account, cipher.seal(value.toByteArray(Charsets.UTF_8))) }
        sealed.onFailure { Log.w(TAG, "token kept for this session only: ${it.javaClass.simpleName}") }
        if (sealed.isSuccess && open(account) == value) legacy?.delete(account)
    }

    fun load(account: String = "install-token"): String? {
        memory[account]?.let { return it }
        open(account)?.let { memory[account] = it; return it }
        val old = legacy?.load(account) ?: return null
        memory[account] = old
        val moved = runCatching { write(account, cipher.seal(old.toByteArray(Charsets.UTF_8))) }.isSuccess &&
            open(account) == old
        if (moved) legacy.delete(account) else Log.w(TAG, "token migration deferred; the old copy stays")
        return old
    }

    fun delete(account: String = "install-token") {
        memory.remove(account)
        file(account).delete()
        legacy?.delete(account)
    }

    companion object {
        /** m176: the token of a "Delete my data" made with no signal, kept until the Brain has deleted it too. */
        const val PENDING_DELETE = "pending-delete"
        const val TAG = "OdysTokens"
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
data class CardPhoto(val file: String, val title: String, val author: String, val licence: String, val source: String,
                     val licenceURL: String? = null,
                     /** m258: cleared for the share card (brain/data/photo_checks.yaml); missing means no. */
                     val share: Boolean = false) {
    /** The credit the licence asks for (title, author, source, licence), shown under the picture. */
    val credit: String get() = "“$title” by $author, $licence, Wikimedia Commons (resized)"
    /** m258: on the share card, which crops the photo. */
    val shareCredit: String get() = "Photo: “$title” by $author, $licence, Wikimedia Commons (cropped)"
    /** m258: in the share message, where links are clickable. */
    val shareLines: String get() = "Photo: “$title” by $author, $licence" + (licenceURL?.let { " ($it)" } ?: "") +
        ", cropped. $source"
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

    /** m258: the photo only if it's cleared for sharing; otherwise the card keeps its field of colour. */
    fun sharePhoto(context: Context, momentId: String): Pair<CardPhoto, Bitmap>? =
        photo(context, momentId)?.takeIf { it.first.share }

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
