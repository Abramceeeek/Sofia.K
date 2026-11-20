package com.odys.app

import android.app.Application
import androidx.test.core.app.ApplicationProvider
import androidx.work.testing.WorkManagerTestInitHelper
import kotlinx.serialization.builtins.ListSerializer
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.shadows.ShadowLog
import java.security.GeneralSecurityException
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/**
 * m227: the install token moves off androidx security-crypto (deprecated in 2025) to a Keystore-sealed file, with no
 * unexpected sign-out. The Keystore isn't available on the computer, so a software AES-GCM key stands in for it here;
 * the store's rules (migration, failures, corruption, no plaintext anywhere) are what's tested.
 */
@RunWith(RobolectricTestRunner::class)
class TokenStoreTest {
    @get:Rule val tmp = TemporaryFolder()

    private val token = "tok_9f3c1e2a7b6d4c58"

    /** AES-256-GCM with a key held in memory, like the Keystore's but not hardware-backed. */
    private class SoftCipher(var key: SecretKey? = KeyGenerator.getInstance("AES").apply { init(256) }.generateKey(),
                             var failSeal: Boolean = false) : TokenCipher {
        override fun seal(plain: ByteArray): ByteArray {
            if (failSeal) throw GeneralSecurityException("keystore unavailable")
            val c = Cipher.getInstance("AES/GCM/NoPadding")
            c.init(Cipher.ENCRYPT_MODE, key ?: throw GeneralSecurityException("no key"))
            return c.iv + c.doFinal(plain)
        }
        override fun open(sealed: ByteArray): ByteArray {
            val c = Cipher.getInstance("AES/GCM/NoPadding")
            c.init(Cipher.DECRYPT_MODE, key ?: throw GeneralSecurityException("no key"), GCMParameterSpec(128, sealed, 0, 12))
            return c.doFinal(sealed, 12, sealed.size - 12)
        }
    }

    private class OldStore(val values: MutableMap<String, String> = mutableMapOf()) : LegacyTokens {
        override fun load(account: String) = values[account]
        override fun delete(account: String) { values.remove(account) }
    }

    private fun noPlaintextOnDisk(dir: java.io.File) {
        dir.walkTopDown().filter { it.isFile }.forEach {
            assertFalse("plaintext token in ${it.name}", String(it.readBytes(), Charsets.ISO_8859_1).contains(token))
        }
    }

    @Before fun logs() { ShadowLog.clear() }

    @Test fun anUpgradeMovesTheTokenOnceAndNobodyIsSignedOut() {
        val dir = tmp.newFolder("tokens")
        val cipher = SoftCipher()
        val old = OldStore(mutableMapOf("install-token" to token, TokenStore.PENDING_DELETE to "tok_old"))
        assertEquals(token, TokenStore(dir, cipher, old).load())           // first launch after the upgrade
        assertNull(old.values["install-token"])                            // moved, then removed from the old store
        assertEquals(token, TokenStore(dir, cipher, OldStore()).load())   // the next launch reads the sealed copy
        assertEquals("tok_old", TokenStore(dir, cipher, old).load(TokenStore.PENDING_DELETE))   // the other account too
        noPlaintextOnDisk(dir)
    }

    @Test fun aFailedMigrationKeepsTheOldCopyAndTriesAgain() {
        val dir = tmp.newFolder("tokens")
        val cipher = SoftCipher(failSeal = true)
        val old = OldStore(mutableMapOf("install-token" to token))
        assertEquals(token, TokenStore(dir, cipher, old).load())           // still signed in
        assertEquals(token, old.values["install-token"])                   // the old copy stays
        assertTrue(dir.listFiles().orEmpty().isEmpty())                    // nothing half-written, nothing in plain
        cipher.failSeal = false
        assertEquals(token, TokenStore(dir, cipher, old).load())           // next launch: moved
        assertNull(old.values["install-token"])
    }

    @Test fun aCorruptedOrUnreadableTokenNeverCrashes() {
        val dir = tmp.newFolder("tokens")
        val cipher = SoftCipher()
        TokenStore(dir, cipher, null).save(token)
        val f = java.io.File(dir, "install-token")
        val bytes = f.readBytes(); bytes[bytes.size - 1] = (bytes.last().toInt() xor 1).toByte(); f.writeBytes(bytes)
        assertNull(TokenStore(dir, cipher, null).load())                   // changed data: no token, no crash
        val old = OldStore(mutableMapOf("install-token" to token))
        assertEquals(token, TokenStore(dir, cipher, old).load())           // an old copy still there is used
        f.writeBytes(byteArrayOf(1, 2, 3))
        assertNull(TokenStore(dir, SoftCipher(), null).load())             // too short / another key: no token
    }

    @Test fun aLostKeyReadsAsSignedOutNotACrash() {
        val dir = tmp.newFolder("tokens")
        val cipher = SoftCipher()
        TokenStore(dir, cipher, null).save(token)
        cipher.key = null                                                  // e.g. the Keystore was reset
        assertNull(TokenStore(dir, cipher, null).load())
        val fresh = SoftCipher()                                           // joining again: a new key, a new token
        TokenStore(dir, fresh, null).save("tok_new")
        assertEquals("tok_new", TokenStore(dir, fresh, null).load())       // and the next launch reads it
    }

    @Test fun whenSealingIsImpossibleTheTokenLivesOnlyInMemory() {
        val dir = tmp.newFolder("tokens")
        val store = TokenStore(dir, SoftCipher(failSeal = true), null)
        store.save(token)
        assertEquals(token, store.load())                                  // this session works
        assertNull(TokenStore(dir, SoftCipher(), null).load())             // never written down in plain
        noPlaintextOnDisk(dir)
    }

    @Test fun deleteRemovesEveryCopyAndNoLogEverHoldsTheToken() {
        val dir = tmp.newFolder("tokens")
        val old = OldStore(mutableMapOf("install-token" to token))
        val store = TokenStore(dir, SoftCipher(failSeal = true), old)
        store.load()                                                       // a deferred migration logs a warning
        store.delete()
        assertNull(old.values["install-token"]) ; assertNull(TokenStore(dir, SoftCipher(), null).load())
        assertTrue(ShadowLog.getLogs().isNotEmpty())
        ShadowLog.getLogs().forEach { assertFalse(it.msg.contains(token)) ; assertFalse((it.throwable?.message ?: "").contains(token)) }
    }

    @Test fun noTokenAtStartStillKeepsTheTravellersTrips() {
        // m226: a missing or unreadable token shows Welcome, and the trips on the phone are kept, not overwritten
        val app = ApplicationProvider.getApplicationContext<Application>()
        WorkManagerTestInitHelper.initializeTestWorkManager(app)
        val trip = Trip(start = "2026-12-01", nights = 3)
        Files(app).save(ListSerializer(Trip.serializer()), listOf(trip), "trips.json")
        val model = AppModel(app)
        assertEquals(Route.Welcome, model.route)
        assertEquals(listOf(trip.id), model.trips.map { it.id })
    }
}
