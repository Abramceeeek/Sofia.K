# What a traveller is told, and how sure it is (review, 24 Nov 2026)

**Decision first:** ODYS already says most of what a traveller needs where they need it. The one gap was that estimates looked like checked facts. **Fixed on the branch (m343):**
- a meal with no named place now says its price is ODYS's planning estimate;
- the day's first Tube or bus journey says how fares are estimated.

Everything below is on each stop in both apps, unless it says otherwise.

| What | How ODYS says it today | How sure | Gap, and next step |
|---|---|---|---|
| **A named place's hours, price and way in** | The stop's hours ("Daily 10:00–17:00; closed 24–26 Dec"), its cost line, and **"Hours, prices and the way in last checked on 24 Nov, from the place's own site"** | **Checked** on the place's own pages (D91), with the date | Facts age. **Next:** a re-check list by age (the readiness check already flags old facts) |
| **A meal with no named place** ("Lunch near Soho Square") | "Food: about £15" **plus, since m343:** "The price is ODYS's planning estimate for a meal nearby, not a menu price." | **Estimate** (D102) | Named places for more meals, from verified sources only (m323–m325) |
| **A named restaurant's price** (Padella, Flat Iron, Dishoom) | The cost line ("Food: about £15") and the checked date | **Checked** from the menu on its own site; one dish, not the whole bill | Say "a main dish" in the line (small wording change; Test B shares the line, so after the round) |
| **Fares** | The day's total, "plus about £8.90 transport". **Since m343,** the first Tube or bus stop also says: "Fares are estimated: £3.00 a Tube or bus journey, at most £8.90 a day (TfL's fares, read Sep 2026). TfL charges the real fare." | **Estimate** from TfL's own fares | Re-read TfL's fares each March, when they change |
| **Booking** | "Book ahead" on the stop: Horizon 22, the Cutty Sark, the Science Museum's free ticket, Padella's virtual queue | **Checked** | The London gate's G5 fails a plan if a booking a card needs isn't said |
| **Closures** | Dated closures and early closings on the card are never planned (24–26 Dec, 17 Dec from 15:00). When the place's page doesn't give Christmas hours, the stop says "Check Christmas hours before 24–26 Dec" (Tate Modern). On the day: **"Re-plan the rest of today" → closed** | **Checked** where stated | Unannounced closures: re-plan on the day, which also says what changed (m341) |
| **Weather** | The Met Office forecast shapes the plan (Stage 1). Outdoor stops carry "If it rains: …". **Since m341:** "Raining? Swap for the indoor option", one tap, saying what changed | Forecast, then the person's own call | A forecast-change nudge on the day (after the round) |
| **Travel changes** (strikes, delays) | "Re-plan the rest of today" from where they are. With TfL's key, the planned journeys use TfL's times and name the line | TfL journey times; disruptions not read | Read TfL's line status for the day's lines and say it on the stop (needs the TfL key; ~3 h) |
| **When a plan changes** | **Since m336/m341:** every swap, "Plan again" and re-plan says what changed: what left and came in, the finish, the cost and the travel ("Instead of Liberty: Borough Market. The day ends at 17:20 (was 17:40). It costs about £18 more.") | Computed from the two plans | — |
| **Why a stop is in the plan** | "Recommended because…", from the person's own answers (m275); never a chance or a score | From the person's answers | Group trips: "who it suits", built in `group.py` (m342), not yet in the apps |

**Not shown, on purpose:** any chance of enjoying a place, until real ratings check it (m275); weights or scores; anything about other members of a group except the shared plan.
