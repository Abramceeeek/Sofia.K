package com.odys.app

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** WS8 (m213): a price keeps its own currency; only pounds get a pound sign. */
class MoneyTest {
    @Test
    fun poundsAndOtherCurrencies() {
        assertEquals("£1,318", Money.whole(1318.4))
        assertEquals("£1,318", Money.whole(1318.4, "GBP"))
        assertEquals("1,318 EUR", Money.whole(1318.4, "EUR"))
        assertEquals("420", Money.whole(420.0, ""))
    }

    /** m218: a converted figure says it's an estimate; a choice keeps its currency; older saved choices are pounds. */
    @Test
    fun estimatesAndChoicesKeepTheirCurrency() {
        val e = BrainJson.decodeFromString(PriceEstimate.serializer(),
            """{"amount": 306.13, "currency": "GBP", "rate": 0.83415, "source": "ECB", "as_of": "2026-11-06", "line": "ECB rate of 6 Nov 2026"}""")
        assertEquals("≈ £306 · ECB rate of 6 Nov 2026", e.text)
        assertEquals("≈ £334", FlightFacets(currency = "GBP", estimated = true).money(333.66))
        assertEquals("420 EUR", FlightFacets(currency = "EUR").money(420.0))
        val eur = TripChoice("flight", "Sample Air", "Skyscanner", 367.0, false, currency = "EUR")
        assertEquals("367 EUR", eur.money)
        assertFalse(eur.inPounds)
        val old = BrainJson.decodeFromString(TripChoice.serializer(),
            """{"kind": "stay", "title": "A hotel", "provider": "Booking.com", "price": 840.0, "booked": true}""")
        assertTrue(old.inPounds)
        assertEquals("£840", old.money)
    }
}
