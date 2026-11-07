package com.odys.app

import org.junit.Assert.assertEquals
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
}
