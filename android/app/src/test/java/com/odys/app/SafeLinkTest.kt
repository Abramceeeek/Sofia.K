package com.odys.app

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** SEC-16 (audit): only https links with a host are opened. Plain JUnit: no Android needed. */
class SafeLinkTest {
    @Test
    fun theLinksTheAppReallyOpensAreAllowed() {
        for (url in listOf(
            "https://www.skyscanner.net/g/referrals/v1/flights/day-view/?origin=EDI",
            "https://www.google.com/maps/dir/?api=1&destination=51.5,-0.12&travelmode=transit",
            "https://moments-brain.onrender.com/privacy",
            "https://commons.wikimedia.org/wiki/File:Example.jpg",
            "  https://www.booking.com/searchresults.html?ss=London  ",
        )) assertTrue(url, isSafeLink(url))
    }

    @Test
    fun anythingElseIsRefused() {
        for (url in listOf(
            "http://www.booking.com/",                       // in the clear
            "intent://scan/#Intent;scheme=zxing;end",        // another app, by intent
            "tel:+447700900123", "sms:123", "file:///sdcard/x", "content://x/y",
            "javascript:alert(1)", "market://details?id=x", "odys://r/ABCDEFGH",
            "https://", "https:///path", "https://user:pass@example.com/", "not a url", "",
        )) assertFalse(url, isSafeLink(url))
    }
}
