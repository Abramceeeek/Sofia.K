# The friends' round rehearsal: a checklist for the two real phones (12 Nov 2026; m265)

**Abram runs this on his own iPhone (TestFlight 91) and Android phone (build 21), with the code `REHEARSAL`.**
- **Not changed during it:** nothing in the experiment: no question, no logic, no build.
- **Why real phones:** CI screenshots draw screens with sample data. They don't install a real build, sign in to a real Brain, lose signal or use a person's text size.
- **Recording:** tick each line, and note anything odd with the screen and the time.
- **Time:** about 45 minutes for both phones.

| # | Step | iPhone | Android | What to check |
|---|---|---|---|---|
| **Install** | | | | |
| 1 | Install from TestFlight / the `android-latest` link | ☐ | ☐ | Build **91** / **21** shows in About or the store page |
| 2 | Open the app the first time | ☐ | ☐ | The logo intro, then the welcome screen; no crash |
| **Onboarding** | | | | |
| 3 | Type `REHEARSAL` on the welcome screen | ☐ | ☐ | Accepted (any case) |
| 4 | Consent, then "Where are you based?" → London | ☐ | ☐ | The consent version reads `app-2026-10-02` where shown |
| 5 | The 6 places, the 5 this-or-that days, the survey | ☐ | ☐ | Each can be skipped; the counter is honest |
| 6 | "So far, I've learned…" → "Change something" once | ☐ | ☐ | The correction shows straight away |
| **The experiment** | | | | |
| 7 | The pair: Plan 1 and Plan 2 | ☐ | ☐ | Same format, no hint which is personal |
| 8 | Gut choice, "fits me" for both, "easier" (answer on iPhone, **skip on Android**), why | ☐ | ☐ | Skipping "easier" is allowed |
| 9 | The reveal, then the chosen plan becomes the day | ☐ | ☐ | No swap or regenerate on that plan |
| **Plans** | | | | |
| 10 | Open the day: stops, times, journeys, prices | ☐ | ☐ | No "£0" or blank for a place with a price |
| 11 | (If offered) a second, generic-free personal plan later | ☐ | ☐ | It differs from the pair's plans where expected |
| **Ratings** | | | | |
| 12 | Rate two stops (one 5, one 2), and "bring someone" on one | ☐ | ☐ | The rating sticks after leaving the screen |
| 13 | At the day's end: "worth it" and "do it again" | ☐ | ☐ | Both saved |
| **Offline (build 91's own behaviour)** | | | | |
| 14 | Aeroplane mode, then rate a stop | ☐ | ☐ | It's kept on the phone; no error lost |
| 15 | Aeroplane mode, then try to make a plan | ☐ | ☐ | "You seem to be offline. Check your connection and try again." |
| 16 | Signal back on | ☐ | ☐ | The kept rating is sent (check the export) |
| **Restart** | | | | |
| 17 | Force-quit and reopen | ☐ | ☐ | The day, ratings and answers are still there; no second onboarding |
| 18 | Restart the phone, reopen | ☐ | ☐ | The same |
| **Large text and reading** | | | | |
| 19 | Set the largest text size (iOS Larger Text; Android Font size and Display size) | ☐ | ☐ | Nothing cut off on the pair, the day or the rating screens; buttons reachable |
| 20 | Dark and light (iPhone "Always dark" off and on) | ☐ | ☐ | Text readable on both |
| **Unexpected errors** | | | | |
| 21 | Turn signal off mid-onboarding, then on, and continue | ☐ | ☐ | It recovers, or says clearly what to do |
| 22 | Leave the app in the background for 15 minutes (the free server sleeps), then make a plan | ☐ | ☐ | A wait message, then a plan; no crash |
| 23 | Help & safety: send "rehearsal test, please ignore" | ☐ | ☐ | The automatic reply (999 first; a person replies within a few hours) |
| **Deletion** | | | | |
| 24 | "Delete my data" | ☐ | ☐ | Confirmation; the app returns to the start |
| 25 | Delete with no signal on one phone, then signal back | ☐ | ☐ | The deletion finishes when online (m176) |

**After both phones:**
1. Export, then `testb_report.py --code REHEARSAL --no-overlap`. It should count 2 installs (by one person), both pairs answered, and "easier" answered 1 of 2.
2. `--code FRIENDS` must count 0.
3. Delete the export file (`validation/raw/` stays git-ignored).
4. **Anything that failed:** stop, and tell Claude before inviting anyone. A fix would change the frozen build, which is a decision for Abram, not a quiet patch.
