package com.odys.app

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.time.LocalDate

/**
 * m228: the offline view's rules, the same as the Brain's tested reference (brain/src/brain/offline.py) and the
 * iPhone's: today's day first, then the stay, the journey and help; a status and an action on each; nothing filled in.
 */
class OfflinePackTest {
    private val plan = BrainJson.decodeFromString(Plan.serializer(), File("../../app/Sources/Demo/demo_plan.json").readText())
    private val stay = TripChoice("stay", "Sample hotel U, Covent Garden", "Booking.com", 840.0, true, forStart = "2026-11-20")
    private val flight = TripChoice("flight", "Sample Air · 20:55 → 00:22", "Skyscanner", 367.0, true, arriveTime = "00:22",
        leaveTime = "10:00", arrivePlace = "LHR", leavePlace = "LHR", forStart = "2026-11-20", currency = "EUR")
    private val trip = Trip(start = "2026-11-20", nights = 3, stay = stay, flight = flight)
    private val day = LocalDate.parse("2026-11-21")

    @Test fun theOrderIsTodayStayJourneyHelp() {
        val p = OfflinePack.build(plan.copy(date = "2026-11-21", createdAt = "2026-11-21T08:00:00Z"), trip, day)
        assertEquals(listOf("itinerary", "stay", "journey", "emergency"), p.map { it.id })
        val today = p[0].items[0]
        assertEquals(OfflineItem.Status.Current, today.status)
        assertEquals("Your plan · saved 21 Nov", OfflinePack.provenance(today))
        assertTrue(p[2].items[0].lines.contains("367 EUR, as found on Skyscanner"))   // its own currency, never £
        assertEquals("Times can change: check with the airline on the day.", p[2].items[0].action)
        assertTrue(p[3].items[0].lines[0].contains("call 999"))
        assertEquals("Emergency help in the UK", p[3].title)   // m236: never presented as universal (Abram, m234)
    }

    @Test fun staleUnbookedPastAndExpiredAreSaid() {
        val old = OfflinePack.itinerary(plan.copy(date = "2026-11-21", createdAt = "2026-11-01T08:00:00Z"), day)
        assertEquals(OfflineItem.Status.Check, old.status)
        assertTrue(old.action!!.startsWith("Planned on 1 Nov"))
        assertEquals(OfflineItem.Status.Past, OfflinePack.itinerary(plan.copy(date = "2026-11-20"), day).status)
        val unbooked = OfflinePack.choice("stay", stay.copy(booked = false), trip, day)
        assertEquals(OfflineItem.Status.Check, unbooked.status)
        assertEquals("Not marked as booked: check with Booking.com.", unbooked.action)
        val after = OfflinePack.choice("stay", stay, trip, LocalDate.parse("2026-11-24"))
        assertEquals(OfflineItem.Status.Expired, after.status)                       // marked, never deleted
        val other = OfflinePack.choice("flight", flight.copy(forStart = "2026-01-01"), trip, day)
        assertTrue(other.action!!.startsWith("Chosen for other dates"))
        val noTimes = OfflinePack.choice("flight", flight.copy(arriveTime = null), trip, day)
        assertTrue("when the flight lands" in noTimes.missing)
        assertEquals(listOf("a plan for today"), OfflinePack.itinerary(null, day).missing)
    }

    @Test fun nothingClaimsToBeLive() {
        val text = OfflinePack.build(plan.copy(date = "2026-11-21"), trip, day)
            .flatMap { s -> s.items.flatMap { it.lines + listOfNotNull(it.action) } }.joinToString(" ").lowercase()
        for (word in listOf("available now", "live", "open now", "in stock", "real-time")) assertFalse(word, text.contains(word))
    }

    @Test fun signalComingAndGoingIsFollowedUnlessPinned() {
        val c = Connectivity(null)
        c.report(false); assertFalse(c.online)
        c.report(true); assertTrue(c.online)
        c.pin(false); c.report(true); assertFalse(c.online)                          // screenshots: held offline
    }
}
