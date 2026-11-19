# Mobile validation: what is tested, what is only drawn, and what needs real phones (16 Nov 2026)

Abram's review of the audit, part 5 (12 Nov): "Android's 119 tests are not equivalent to 119 fully tested customer journeys", and "No public release without successful real-device testing". This plan is for the next app builds after the friends' round. The round's own builds (TestFlight 91, Android 21) are frozen and checked by `validation/friends-round-rehearsal.md`.

**Recommendation:**
1. Add three automated checks where the tooling here allows, about 11 h in all:
   - A1: a Brain-side contract test;
   - A2: an Android journey test against a fake Brain;
   - A3: a small iPhone unit-test target, run by hand.
2. Then run the real-device checklist below on both phones before every external build.
3. **A public release needs every "blocks release" row passed on real phones.** No automated result stands in for one.

## Three kinds of check (kept apart, as Abram asked)

- **Drawn:** a screen is rendered from a set state, with sample data, and kept as an image.
  - It proves the screen draws without crashing and fits.
  - It proves nothing about getting there, or about what happens when you tap.
  - Android's 100 `ScreensTest` renders and the iPhone's 40+ CI screenshots are this kind.
- **Tested:** code runs and its result is checked.
  - Android has 22 logic tests:
    - token store and Keystore migration: 7;
    - offline pack: 4;
    - https-only links: 2;
    - "Delete my data" clears everything: 1;
    - money: 2;
    - contrast: 3;
    - tab fit: 3.
  - **The iPhone has none.**
- **Real phone:** a person does it on a device. This is the only kind that covers the Keychain and Keystore, permissions, speech, notifications, OS gestures, background termination and battery.

## Abram's journeys: what each has today, and what to add

| Journey | iPhone today | Android today | Add (automated) | Real phone (checklist step) |
|---|---|---|---|---|
| Onboarding | drawn (each step) | drawn (each step) | A2: driven end to end against a fake Brain | R1 |
| Creating a plan | drawn | drawn | A2 | R2 |
| Changing a plan (swap, re-plan the rest of today) | drawn (swap) | drawn (swap) | A2: swap and re-plan, with the answer checked | R3 |
| Viewing a day's itinerary | drawn | drawn | A1: the fields the day needs are in the Brain's answer | R4 |
| Accommodation comparison ("best for your days") | drawn | drawn (stay, stay for trip, large text) | A1 | R5 |
| Currency display | none | tested (money, 2) | A3: the iPhone's money formatting | R6 |
| Offline | drawn (offline, saved) | tested (offline pack, 4) and drawn | A2: rating offline, sent later; planning offline says so | R7 |
| Deleting information | none | tested (1) | A3: `clearLocal` leaves only the two display settings | R8 |
| Authentication lifecycle (install token: made, kept, migrated, lost, deleted) | none | tested (token store, 7) | A3: Keychain save, update, migrate, load | R9 |
| Large text | drawn (2 screens at the largest size) | drawn (1) | A5: more screens at the largest size | R10 |
| VoiceOver / TalkBack | none | none | — (needs a person) | R11 |
| **Android only:** screen sizes | — | drawn at one size | A5: a small and a large size | R12 |
| Android back navigation (predictive back) | — | none | A2: back from a stop, a trip day and the pair | R13 |
| App process termination | — | none | A2: recreate the activity mid-pair; the state comes back | R14 |
| Restoring a saved trip | — | tested (no token still keeps trips) | A2 | R15 |
| Keystore migration | — | tested (an upgrade moves the token once) | — | R16 |
| Offline transitions | — | tested (signal coming and going) | A2 | R7 |
| App upgrades (install over the previous build) | none | none | — (needs two builds) | R17 |

## The automated checks to add

| # | Check | How | Hours | Cost |
|---|---|---|---|---|
| A1 | **Contract test:** for every response the apps decode, the Brain's answer has the fields the apps' models require, with the right types. It includes m275's `match` text and the absence of `predicted` (m276). | A Python test listing each model's required fields from `Models.swift` and `Models.kt`, against real responses from the test client | 2 | free (Linux) |
| A2 | **Android journeys** against a fake Brain (OkHttp `MockWebServer` serving the sample JSON): consent, onboarding, pair, reveal, day, swap, re-plan, rating, offline rating sent later, "Delete my data", back navigation, the activity recreated mid-pair. Plus the error paths: 429, 500, a slow first answer (the server waking), no connection. | Robolectric with Compose UI test and one new test dependency | 5 | free (Linux) |
| A3 | **iPhone unit tests:**<br>• `SafeLink.https`;<br>• Keychain save, update, migrate and load (the simulator has a Keychain);<br>• `clearLocal`;<br>• money formatting;<br>• the Daylight contrast rule (4.5:1). | A test target in `project.yml`, run by hand with `xcodebuild test` on the macOS runner (m188: not on branch pushes) | 4 | about 10 macOS minutes a run; $0.062/min beyond the free quota (GitHub billing, read 26 Sep; **re-check before relying on it**) |
| A4 | iPhone UI test (XCUITest) of onboarding to first plan in demo mode | after Checkpoint 3 | 6 | macOS minutes |
| A5 | More large-text and size renders: the pair, the day, the rating, at Android font scale 2.0 and a small screen; the same on the iPhone | extend the two existing lists | 1 | small |

A1 and A2 give the most per hour. They catch the commonest break, a Brain change an app can't decode, plus the journeys between screens, on every push and for free. A3 is cheap insurance for the security-relevant Swift (SEC-15, SEC-16), which today is only compiled.

## The real-device checklist (both phones, every external build)

Run the rehearsal's 25 steps, then these. Minimum devices:
- **iPhone:** Abram's own iPhone, on the newest iOS (the app needs iOS 17 or later).
- **Android:** an Android 16 phone (API 36). If one is available, also an older phone near the minimum (API 26), for the slow path.

**Blocks release** marks a row that must pass before any build goes to strangers or the public.

| # | Check | iPhone | Android | Pass when | Blocks release |
|---|---|---|---|---|---|
| R1 | Onboarding from a fresh install, with a tester code; skip what can be skipped | ☐ | ☐ | First plan reached; the question count is honest | yes |
| R2 | Make a plan for a Saturday, then for today | ☐ | ☐ | Stops, times, travel and prices; "Recommended because…" or "Chosen to fit…", never a % or "strong match" (m275) | yes |
| R3 | Swap a stop; "Re-plan the rest of today" | ☐ | ☐ | The swapped stop differs; kept stops stay; nothing breaks the day's hours | yes |
| R4 | Open the day, a stop card, "Why this stop?", the way in, the map | ☐ | ☐ | Matches the plan; directions open the maps app | yes |
| R5 | A trip: flights and stays, "best for your days", a stay's detail, its booking link | ☐ | ☐ | Sample results are labelled as samples; the link opens the provider's https page (SEC-16) | yes |
| R6 | A stay priced in euros or dollars beside a pound one | ☐ | ☐ | Each shows its own currency; no raw sum across currencies (m218) | yes |
| R7 | Aeroplane mode: rate a stop, try to plan, open the offline pack; signal back | ☐ | ☐ | The rating is kept and sent later; planning says offline; nothing claims to be live | yes |
| R8 | "Delete my data", then reopen; and again with no signal, then signal back | ☐ | ☐ | A fresh start; no old plan, code, feedback or video choice (SEC-15); the deletion completes when online | yes |
| R9 | Force-quit, restart the phone, reopen; (iPhone) back up and restore onto a **different** iPhone if one is available | ☐ | ☐ | Still signed in on the same phone; on the other iPhone, a fresh start (the token stays on its own device) | yes |
| R10 | The largest text size on onboarding, the pair, the day, a stop, rating, a stay | ☐ | ☐ | Nothing cut off or overlapping | yes |
| R11 | VoiceOver / TalkBack through welcome, consent, a place card, the pair and a rating | ☐ | ☐ | Every control announced with its purpose; a sensible order | yes |
| R12 | A small screen (iPhone SE size, or an Android at its largest display size) and a large one | ☐ | ☐ | Nothing cut off | yes |
| R13 | Android back gesture from a stop, a trip day and the pair | — | ☐ | Back one level; never out of the pair by accident | yes |
| R14 | Android: in the middle of the pair, switch apps and open a few heavy ones (or "Don't keep activities" in developer options); come back | — | ☐ | The same step, with the answers kept | yes |
| R15 | Android: a saved trip after the app has been killed, and after a phone restart | — | ☐ | The trip and its days are there | yes |
| R16 | Android: install the new build over the round's build | — | ☐ | The token is moved to the Keystore once and the person stays signed in. If the signing key changed (SEC-12), uninstall is needed and the start is fresh: say so to testers | yes |
| R17 | Both: install the new build over the previous one | ☐ | ☐ | iPhone: everything kept. Android: as R16 | yes |
| R18 | Notification permission: asked once, after the first plan; a reminder fires for a rated stop's time | ☐ | ☐ | One prompt; nothing sent if refused | yes |
| R19 | Location on "Now": asked only when needed; "when in use" only | ☐ | ☐ | The prompt text matches the privacy notice; refusing still works | yes |
| R20 | "Tell it instead" (speech), then speech refused | ☐ | ☐ | The text appears as typed; refusing leaves typing | no |
| R21 | Edge-to-edge (Android 16) and the iPhone's Dynamic Island area on every main screen | ☐ | ☐ | Nothing under the status or gesture bar | yes |
| R22 | Time zone set to New York, then back | ☐ | ☐ | London times stay London times where the app says so | no |
| R23 | Low Power Mode / Battery Saver | ☐ | ☐ | Plans load; motion reduced, not broken | no |
| R24 | Three hours out with "Now" open and location on | ☐ | ☐ | Battery used is noted (for comparison) | no |
| R25 | Reinstall after deleting the app (not "Delete my data") | ☐ | ☐ | A fresh start (D124). Note what happens to the old install's answers on the server, and check that the privacy notice describes it | no |

**Recording:** a copy of this table per build in `validation/`. It records the build numbers, each phone and OS version, and a screenshot of each failure.

## Hours

| Who | Work | Hours |
|---|---|---|
| Claude | A1 | 2 |
| Claude | A2 | 5 |
| Claude | A3 | 4 |
| Claude | A5, when convenient | 1 |
| Abram, or a tester with the second phone | The 25 checks, per phone | about 1.5 |
