# Global UX and cross-platform audit (WS8, 7 Nov 2026; m213)

**Decision.** The identity stays: the arch, charcoal, amber and cream, Newsreader, quiet motion, Daylight. This pass checked both apps against what a trip anywhere will need, and **fixed four real inconsistencies on both phones**:
- **Prices keep their own currency.** A flight offer in euros showed a pound sign.
- **With large text, the price no longer squeezes its source line** to a few letters a row.
- **"Try again"** when the stay comparison fails.
- **New large-text, small-screen screenshots** of the newest screens on both phones.

Everything else is either sound or a deliberate London-first choice, written down below. Each such choice has its own next step for when a second destination exists (WS1).

## The audit

| Area | iPhone | Android | Finding | Action |
|---|---|---|---|---|
| **Currencies** | `Money.whole` always wrote "£" | The same | **Inconsistent with the data.** The Brain passes Duffel's `total_currency` straight through, and stays carry `currency`, but both apps prefixed "£" to any amount | **Fixed:** `Money.whole(amount, currency)`; pounds keep "£", another currency shows its code ("1,318 EUR", as the Brain writes it). Used for every flight and stay price, the found-price box and the map pins. Other amounts are pounds by construction (filters, facets, the Brain's own totals). Android unit test `MoneyTest` |
| **Large text** | Text scales with Dynamic Type (`Theme.serif(…, relativeTo:)`); fixed sizes only on the share card image, the logo and one video caption | Text in sp throughout | **The found-price box** (stay and flight) squeezed "A sample price, made up for testing" into a column split mid-word ("testin / g") at 1.6× on a 320 dp phone | **Fixed on both:** at large sizes (iPhone ≥ xxxLarge; Android font scale ≥ 1.3) the price goes under its source line. New screenshots: Android `90-stayfortrip-large`, `91-tripdaymine-large` (320 × 568 dp, 1.6×); iPhone `stayfortrip-largetext`, `tripdaymine-largetext` (Accessibility Large), in CI |
| **Small screens** | CI shoots one iPhone size | Robolectric at 393 dp | Not tested below 393 dp before | Android 320 dp shots added (above). Personal time and the stay comparison read correctly; nothing truncated |
| **Loading and errors** | The stay comparison: a spinner, then "This couldn't be worked out just now." | The same | No way to retry except leaving the screen | **Fixed on both:** "Try again" (48 dp tall on Android) |
| **Missing images** | Stays: a colour field per place, the same each launch; cards: the satellite view where no photo | The same | Sound | — |
| **Long names** | `lineLimit(1)` in 6 places (rooms, small labels) | `maxLines = 1` in 8 | Hotel and stop names wrap; only secondary lines truncate | — |
| **Date formats** | `en_GB`: "Sat 7 Nov" | `Locale.UK`: the same | Consistent. The Brain writes the same form | London-first, by design |
| **12 or 24 hours** | Always 24-hour (en_GB), whatever the phone's setting | The same | Deliberate: times are London's, as on station boards | Revisit per destination's custom, not per phone |
| **Time zones** | `Europe/London` fixed in date maths (11 places) | `ZoneId.of("Europe/London")` | Correct for the only destination. A second city must use its own zone | `Destination.zone` from the registry (WS1, `places.py`); about 1.5 h in each app when a second city comes |
| **Languages** | English; speech recognition `en-GB` | English | One language | Translation waits for a non-English market |
| **Right-to-left** | Leading and trailing layout throughout | `supportsRtl="true"`; start and end padding | Not exercised: no RTL language yet | A pseudo-RTL screenshot pass when a language needs it |
| **VoiceOver and TalkBack** | 37 explicit labels; rows combine their children | 19 content descriptions; rows merge semantics; 2 decorative images marked null | Counts aren't a measure on their own; the stay rows and personal-time rows read as one line each | A device check by Abram with VoiceOver and TalkBack before strangers (15 min each) |
| **Contrast** | A test fails the build under 4.5:1 on every surface and sky (D130) | The same (`ThemeTest`) | Sound | — |
| **Maps and directions** | Apple MapKit; Apple Maps | OSM tiles; Google Maps | Deliberate (D125). OSM's public tiles aren't for a commercial app at scale (WS1) | A tile provider before public release: Abram's money decision |

## The parity matrix (new work on this branch)

| Feature | iPhone | Android | Screens (iPhone · Android) |
|---|---|---|---|
| Personal time: blocks, where the plans are, the meal question, free and relaxed days (m200–m203) | ✓ | ✓ | `tripdaymine`, `daychangemine` · `25c`, `25d` |
| Trip length (m196) | ✓ | ✓ | `triplength`, `triplength2` · `23b`, `23c` |
| A stay judged for your trip (m203) | ✓ | ✓ | `stayfortrip` · `32c` |
| Bank holidays on nearby dates (m204) | ✓ | ✓ | `stayfortrip` · `32c` |
| Arrival and leaving days in their own words (m209) | ✓ (the Brain's text, old line as fallback) | ✓ | `stayfortrip` · `32c` |
| "Holidays aren't known" note (m211) | ✓ | ✓ | Only shown when the dates go past the data, so not in the demo |
| Prices in their own currency (m213) | ✓ | ✓ (unit test) | Demo prices are pounds |
| Found price stacked at large text (m213) | ✓ | ✓ | `stayfortrip-largetext` · `90` |
| "Try again" on the stay comparison (m213) | ✓ | ✓ | Only on failure |
| Food needs (WS2), the trip's cost (WS6), several places (WS3), the stay lenses screen (WS4) | — | — | Specified, not built: each waits on a decision or on live data |

**Tests run:**
- **Android:** all unit and screen tests, 98, pass (Robolectric, including the two new large-text screens and `MoneyTest`).
- **iPhone:** built on CI for the simulator, with screenshots and no upload (the branch guard, m197). The m209 build passed. The m211 and m213 build is checked by the next run, and the report links it.

**Hours:**
- **This step:** Claude ~3 h.
- **Abram:** a 15-minute VoiceOver and TalkBack pass on his own phones before strangers.
