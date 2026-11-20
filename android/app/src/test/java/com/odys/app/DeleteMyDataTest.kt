package com.odys.app

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.work.testing.WorkManagerTestInitHelper
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/**
 * SEC-15 (audit, Abram, 12 Nov 2026): "Delete my data" leaves nothing personal on the phone. Every key and file the app
 * writes is filled in, then cleared; only display settings may stay (they say nothing about the person). A functional
 * check of the deletion itself, not a drawing of a screen.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class DeleteMyDataTest {
    private val files = listOf("plan.json", "request.json", "profile.json", "trips.json", "pending_ratings.json",
        "handoff.json")
    private val displayOnly = setOf("alwaysDark", "planLayout")

    @Test
    fun deleteMyDataLeavesNothingPersonalOnThePhone() {
        val app = ApplicationProvider.getApplicationContext<android.app.Application>()
        WorkManagerTestInitHelper.initializeTestWorkManager(app)
        val model = AppModel(app)
        val sp = app.getSharedPreferences("odys", Context.MODE_PRIVATE)
        sp.edit().apply {
            for (k in listOf("onboardingDone", "improved", "morePlacesDone", "moreTasksDone", "ratedOnce", "remindersOn",
                "reminderAsked", "safetySent", "surveyDone", "pairDone", "locationOn", "locationAsked", "alwaysDark")) {
                putBoolean(k, true)
            }
            putInt("onboardingStep", 3)
            putInt("nowIndex.7", 2)
            putInt("testBPlanId", 7)
            putString("testerCode", "FRIENDS")
            putString("safetySeen", "2026-11-12T10:00:00Z")
            putString("refCode.joined", "ABCDEFGH")
            putString("ratings.7", "{\"t_view\":4}")
            putString("arrived.7", "t_view")
            putString("dayFeedback.7", "{\"worth\":\"more\",\"again\":true}")
            putString("planLayout", "list")
        }.commit()
        for (f in files) File(app.filesDir, f).writeText("{}")

        model.clearLocal()

        val left = sp.all.keys - displayOnly
        assertTrue("left behind: $left", left.isEmpty())
        for (f in files) assertFalse("$f is still there", File(app.filesDir, f).exists())
        assertTrue(sp.getBoolean("alwaysDark", false))   // a display setting, kept on purpose
    }
}
