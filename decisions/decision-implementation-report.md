# Decision implementation sprint: report (9 Nov 2026; m224–m233)

Abram's decisions on the next-sprint report (m224), built on the branch `claude/vigilant-cannon-my82dj`, in his order.

**The release rules held:**
- `main` is unchanged at `80a0da3`, and the live Brain still answers `"version":"80a0da3"` (checked 9 Nov).
- Nothing was deployed, and no TestFlight build or APK was published. The iPhone runs were dispatched with `upload: false`, and upload only ever runs on `main` anyway (`WANT_UPLOAD` in `ios.yml`).
- No paid API was called, LiteAPI and the ECB rates stay off, food-need collection stays off, and no email was sent.
- Nothing destructive was run against live data.

## 1. Work completed

| # | Item | What was built | Verified by |
|---|---|---|---|
| m225 | **English school holidays: the seven councils** | Westminster, Birmingham and Leeds, each from its own official page, each with its own exceptions (academies and others may differ; schools set training days). The coverage matrix says 3 checked, 4 blocked and "every other English council: not checked". It never implies England | 14 calendar tests |
| m226 | **Offline retention and backups** | Five storage classes (`offline.STORAGE`). **Only derived and cache content can expire.** Trips are kept until the person deletes them, expired bookings are marked, and the summary stays. **The iPhone backup exclusion is withdrawn.** **Bug found and fixed in both apps:** starting with no token skipped loading `trips.json`, so a new trip could overwrite the old ones | 5 offline tests (a year after a trip, everything is still there) |
| m227 | **Android install token on the Keystore** | AES-256-GCM, a Keystore key, `noBackupFilesDir`. A one-time migration from the deprecated store keeps the old copy until the new one reads back, so **nobody is signed out**. A lost key or a corrupted file reads as no token or the old copy, never a crash. Sealing impossible: the token is kept in memory only, never in plain. Nothing is logged but exception class names | 7 tests: upgrade, failed migration, corruption, lost key, memory-only, delete, no token in logs |
| m228 | **The offline view on "Now", both apps** | "Saved on this phone", in Abram's order: today's itinerary, the stay, the journey, emergency help. Each card gives its source, the day it was saved, Saved / Check / Expired / Past, and the one thing to do; missing details say "Not saved: …". With no network path, a banner says "Nothing shown is live." | 4 Android tests (order, statuses, nothing claims to be live, online/offline changes); screenshots on both apps |
| m229 | **Kinds of places, globally neutral (proposal, not served)** | `categories_global.yaml`: the same eight kinds and keys, Abram's four wordings, no "London". The photo caption names the card's own city. **Shopping and live entertainment were investigated and left out** (reasons in section 7). `places_mode` stays `named` | 5 tests; a synthetic benchmark (1,000 people, two sensitivities) |
| m230 | **"Why this stop?", both apps** | Collapsed under "Why we picked this for you". **At most three reasons** from the planner's own inputs, by a fixed rule, with **one trade-off** when something counts against the stop. **No percentages or scores.** **Never on the blind pair** | 2 new Brain tests and 1 extended; the screenshots |
| m231 | **Currency on the sort tabs** | Price on its own line, with the time, distance or rating under it. A line shrinks to 80% before anything is cut off. **New iPhone screenshot `flightcurrency`:** a fare in euros with its estimate line. Abram's ECB conditions are checked against the code; the rates stay off | 3 Android layout tests on a 360 dp phone: "12,345 USD" fits at full size; the old line doesn't fit even at 80% |
| m232 | **The food DPIA corrected (unsigned)** | Abram's four classes. Article 6(1)(a) and Article 9(2)(a) are identified separately, including the UK's new requirement for an Article 6(1) basis under Article 9(2). `food-preferences-and-privacy.md` is reconciled to on-device filtering. `food.py` names both grounds and each need's class | 1 new test; Articles 6 and 9 read on legislation.gov.uk on 9 Nov |
| m233 | **The old `foods_avoided` field: audit and deletion plan** | Admin routes give counts only, and the delete needs a confirmation. **Backups never carry it, and restoring an older one strips it.** Count-only SQL and a one-transaction delete for the live database, for Abram to run | 3 tests; both SQL statements and both routes tested on PostgreSQL 16 with synthetic rows |

## 2. Work blocked, or not done

- **The `foods_avoided` count on the live Brain: not run.** This session has no access to the live database or the admin token, and must not. The live Brain (main) has no audit route, and the admin export would show the values, so it wasn't used. **For Abram:** the SQL in `foods-avoided-audit.md`.
- **Four councils are blocked by bot protection:** Camden, Manchester, Kent and Hampshire (Cloudflare challenges, or a captcha). Getting past a bot check isn't reading the page as the council offers it, so it wasn't attempted. **For Abram to read by hand.**
- **Not built, by design or for after the round:**
  - explanations on stays and trip lengths (their factors exist; where to show them is a design call);
  - the apps reading the new photo caption (`example_note`): one line each, before switching `places_mode`;
  - "Export and import my trips" (Android parity, recommended in m226);
  - the food screens, consent and storage (after the solicitor's review);
  - turning on the ECB rates (with the live flight keys).

## 3. Files changed

52 files, 10 commits (`621c130`..`3061aa5`).

| Area | Files |
|---|---|
| Brain | `api.py` (stop reasons, the audit routes), `explain.py` (`why_this_stop`), `offline.py` (retention classes), `backup.py` (the food-field scrub), `food.py` (need classes, both grounds, audit and scrub), `categories.py` (`category_from`) |
| Brain data | `calendar/school_holidays.yaml`, `calendar/coverage.yaml`, `categories_global.yaml` (new, not served) |
| Brain scripts and benchmarks | `scripts/compare_onboarding.py`, `benchmarks/synthetic/onboarding.txt`, `onboarding_tried60.txt` |
| Brain tests | `test_explain.py`, `test_offline.py`, `test_food.py`, `test_school_coverage.py`, `test_categories_global.py` (new), `test_foods_avoided_audit.py` (new) |
| iPhone | `Offline.swift` (new), `AppModel.swift`, `BookViews.swift`, `BrainClient.swift`, `DayViews.swift`, `Models.swift`, `PlanViews.swift`, `SafetyAndSettingsViews.swift`, `TripLogic.swift`, `TripViews.swift`, `Demo/demo_plan.json` |
| Android | `Offline.kt` (new), `Store.kt`, `AppModel.kt`, `Book.kt`, `Day.kt`, `Models.kt`, `Plan.kt`; tests `TokenStoreTest.kt`, `OfflinePackTest.kt`, `SortTabFitTest.kt` (new) and `ScreensTest.kt` |
| CI | `.github/workflows/ios.yml` (screens `nowoffline`, `offlinesaved`, `stopwhy`, `flightcurrency`) |
| Decisions | `decision-log.md` (m224–m233), `offline-companion.md`, `universal-onboarding.md`, `explanations.md`, `currency-comparison.md`, `dpia-food-needs.md`, `food-preferences-and-privacy.md`, `foods-avoided-audit.md` (new), `travel-calendar-intelligence.md`, `after-9-nov.md`; `brain/README.md` |

## 4. Test results (9 Nov)

| Suite | Result |
|---|---|
| Brain (`pytest`) | **348 passed**, 0 failed (one library deprecation warning) |
| Android (`testDebugUnitTest`, Robolectric) | **119 tests, 0 failures, 0 errors** |
| iPhone (CI run #107, simulator, `upload: false`, commit `03ded9a`) | **Passed**: every Swift change through m231 compiles, and every screen was drawn. m232 and m233 change only the Brain and the documents |
| PostgreSQL 16.15 (a throwaway local server, synthetic rows, deleted after) | The count SQL and the audit route agree (4, 2, 1); the SQL delete and the API delete each remove only the key |

## 5. Screenshots

- **Android** (drawn locally by `ScreensTest` with the iPhone's sample data):
  - `10m-nowoffline`, `10n-offlinesaved`: the offline note and view;
  - `10o-stopwhy`: "Why this stop?" tapped open, with 3 reasons and the trade-off;
  - `26b-flightscurrency`, `29-stays`: the two-line tabs ("357 EUR" over "22h 53m"; "£324" over "0.5 km").
- **iPhone** (CI run #107, the `screenshots` artifact, kept until 23 Nov). Checked on 9 Nov:
  - `nowoffline`: the "No signal" note above "Now".
  - `offlinesaved`: today's plan marked "Check" ("Planned on Tue 20 Oct: travel times may have changed…"), then the stay marked "Saved".
  - `stopwhy`: "Why this stop?" open, with two reasons and the trade-off.
  - `flightscurrency`: the tabs read "367 EUR" over "17h 08m" and "357 EUR" over "22h 53m". Nothing is cut off.
  - `flightcurrency`: "367 EUR", "return, 1 adult", then "≈ £306 · ECB rate of 6 Nov 2026" under the fare.
  - `stays`: "£324" over "0.5 km", "Rated 9.8".
- **Small differences, left as they are:**
  - The iPhone writes the day as "Tue 20 Oct" and Android as "20 Oct", following each app's own date format.
  - The estimate line wraps onto two lines on the iPhone; nothing is cut off.
  - In the screenshots only, the offline card's title reads "Saturday 31 October", because the sample plan is moved to today. A real plan's title is its own date.

## 6. Data retention decisions

| What | Class | Kept | On the iPhone | On Android |
|---|---|---|---|---|
| Trips, plans, ratings, answers, settings | the traveller's own | **until the person deletes them**; never on a timer | in backups (Apple: don't exclude "data the user creates") | `allowBackup` off (unchanged); "Export and import my trips" recommended |
| Past trips and their summaries | history | until the person deletes them; bookings marked "expired" | as above | as above |
| A stored copy of the offline pack | derived | may go 30 days after the trip (GUESS) | rebuilt from the trip; nothing stored yet | the same |
| Images, share cards | cache | removed when no longer needed | Caches (purged, not backed up) | cache directory |
| The install token | credential | until deleted | Keychain, "after first unlock" (it migrates with encrypted backups, with the trips) | Keystore-sealed, `noBackupFilesDir` (m227) |
| Food needs (not built) | special category, or assessed on context | until withdrawn | **excluded from backup: a deliberate exception to m226** (the DPIA) | Keystore-sealed, not backed up |
| `foods_avoided` (retired) | to delete | delete if any exist | — | — |

For `foods_avoided`, backups now never carry it and a restore strips it. The older backups expire within 30 days.

## 7. Legal questions remaining

**For a UK data-protection solicitor, before any user sees food needs** (`dpia-food-needs.md`):
1. Does one consent screen at the explicit standard suit the "assessed on context" needs (vegetarian, vegan, alcohol-free), or should they rest on Article 6(1)(a) alone?
2. Can one screen carry both the Article 6(1)(a) consent and the Article 9(2)(a) explicit consent?
3. The consent screen's wording.
4. Ethical veganism as a protected philosophical belief: UNVERIFIED in this session.
5. A comparison against the ICO's DPIA template. The ICO's pages refused automated reading, so it was never read here.

**Smaller, unverified:** whether deleting the iPhone app always removes its files (`offline-companion.md`, UNVERIFIED; expected yes).

**Unchanged gates (CLAUDE.md):**
- the Apple outside-activities policy and IP clause, before an external TestFlight;
- the ICO fee re-check before strangers;
- a UK trademark search for "ODYS" before a public release.

**From the onboarding investigation** (m229): a shopping taste needs a model change and live entertainment needs cards (after-9-Nov #93, #94). Neither is a legal question; both are for after the round.

## 8. Needs Abram's approval or action

| # | What | Time |
|---|---|---|
| 1 | **Run the `foods_avoided` count** on the live database (SQL in `foods-avoided-audit.md`). If any exist, run the delete there. Re-count weekly until the branch Brain is live, because build 91 and Android 21 still send the field | ~10 min, then ~2 min a week |
| 2 | **Read the four blocked councils by hand** (Camden, Manchester, Kent, Hampshire), or leave them "blocked" | ~15 min each |
| 3 | **Send the DPIA to a UK data-protection solicitor** with the questions in section 7. Sign after their review | ~1 h, plus their fee (not estimated) |
| 4 | **The offline view and "Why this stop?":** approve the look and the words from the screenshots | ~15 min |
| 5 | **Kinds of places:** check the proposed eight wording; decide whether to add a shopping taste (#93) after the round | ~30 min |
| 6 | **Android trips:** approve "Export and import my trips" as the parity route (m226 option A) | a decision; build ~4 h (GUESS) |
| 7 | **After the round:** deploy the branch Brain (it drops `foods_avoided` on save), then switch `places_mode` and turn on the ECB rates with the live flight keys | each a deploy |

**Hours (Claude, approximate):** councils ~3 h, retention ~2 h, token ~2 h, offline view ~3 h, onboarding ~2 h, explanations ~2.5 h, currency ~1 h, DPIA ~1.5 h, audit ~1.5 h, report ~0.5 h. **About 19 h in all.**
