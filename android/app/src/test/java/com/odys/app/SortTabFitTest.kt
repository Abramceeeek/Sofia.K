package com.odys.app

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.text.TextLayoutResult
import androidx.compose.ui.unit.dp
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/**
 * m231: the sort tabs (Best / Cheapest / Fastest; For your days / Cheapest / Top rated) fit a price in any currency
 * without cutting it off. Measured, not eyeballed: each line's text layout says whether it overflowed. A 360 dp phone,
 * the narrowest common width, less the header's 20 dp sides (BookHeader): 320 dp for three tabs. A line may shrink to
 * 80% first, as on the iPhone (minimumScaleFactor 0.8).
 */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w360dp-h740dp-xhdpi")
class SortTabFitTest {
    @get:Rule
    val compose = createComposeRule()

    private fun tabs(vararg t: Pair<String, String?>) = compose.setContent {
        Row(Modifier.width(320.dp).height(IntrinsicSize.Min), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            for ((sub, detail) in t) SortTab("Cheapest", sub, false, Modifier.weight(1f).fillMaxHeight(), detail = detail) {}
        }
    }

    /** The line's own text layout (the unmerged tree: the tab's merged node would report its first line, the label). */
    private fun cutOff(text: String): Boolean =
        compose.onAllNodesWithText(text, useUnmergedTree = true).fetchSemanticsNodes().any { node ->
            val out = mutableListOf<TextLayoutResult>()
            node.config[SemanticsActions.GetTextLayoutResult].action?.invoke(out)
            out.first().hasVisualOverflow
        }

    @Test
    fun longCurrencyCodesAndTimesFitOnANarrowPhone() {
        tabs("12,345 USD" to "22h 53m", "9,999 EUR" to "13h 22m", "£1,234" to "8h 5m")
        for (s in listOf("12,345 USD", "9,999 EUR", "£1,234", "22h 53m", "13h 22m", "8h 5m")) assertFalse(s, cutOff(s))
    }

    @Test
    fun staysFitToo() {
        tabs("1,234 USD" to "12.5 km", "999 EUR" to "0.4 km", "£1,234" to "Rated 4.5")
        for (s in listOf("1,234 USD", "999 EUR", "£1,234", "12.5 km", "0.4 km", "Rated 4.5")) assertFalse(s, cutOff(s))
    }

    @Test
    fun theOldOneLineFormDoesNotFitEvenShrunk() {   // the fault this fixes (iPhone run #105): price and time on one line
        tabs("357 EUR · 22h 53m" to null, "367 EUR · 17h 8m" to null, "£512 · 13h 22m" to null)
        assertTrue(cutOff("357 EUR · 22h 53m"))
    }
}
