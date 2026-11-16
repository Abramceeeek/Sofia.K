# Mobile validation: what is checked automatically, what needs real phones (16 Nov 2026)

Abram's review of the audit, part 5 (12 Nov). This plan covers the next app builds after the friends' round. The round's own builds (TestFlight 91, Android 21) are frozen and are checked by `validation/friends-round-rehearsal.md` (25 steps).

**Recommendation:**
- **Add three automated checks** where the tooling allows it here, about 11 h in all:
  - a Brain-side contract test of the fields both apps read;
  - an Android journey test against a fake Brain;
  - a small iPhone unit-test target run by hand.
- **Then run one real-device pass on both phones** before each external build. That is the rehearsal's 25 steps plus the 16 below for the new builds, about 2.5 h for Abram.
- **Nothing replaces the real phones** for these:
  - location;
  - speech;
  - notifications;
  - the Keychain and Keystore;
  - Android 16's edge-to-edge and back gestures;
  - battery over a day out.

## What is automated today (16 Nov)

| Layer | What runs | Where | Gaps |
|---|---|---|---|
| The Brain (the API both apps call) | 526 tests, with every route the apps use, on SQLite (and a Postgres 18 job in CI) | GitHub Actions, every push | no check that the answers keep the fields the apps decode |
| Android | 122 tests (Robolectric, API 34 and 36). **100 screen renders** with the iPhone's sample data, plus logic: https-only links, "Delete my data" clears everything, token store, offline pack, money, contrast, tab fit | GitHub Actions on Linux, every push | no journey (screens are drawn one by one, from set states); no network errors; no permission flows |
| iPhone | a simulator build, and **40+ screenshots** with sample data (night, day, golden hour, two at the largest text) | macOS runner, on `main` or **by hand** on a branch (m188: not on branch pushes) | **no unit or UI tests at all**; the Swift changes on this branch (SEC-15, SEC-16) are compiled only when the workflow is started by hand |
| Both | sample data made by the real Brain (`make_demo.py`; the m275 lines patched in from the Brain) | in the repository | the sample data can drift from the Brain between regenerations |

## Proposed automated checks (where the tooling permits)

| # | Check | How | Hours | Cost |
|---|---|---|---|---|
| A1 | **Contract test: the fields the apps need.** For every response the apps decode, check that the Brain's answer has the fields the apps' models require, with the right types. This includes the new `match` text and the absence of `predicted`. | A Python test with each app model's required fields listed from `Models.swift` and `Models.kt`, run against real responses from the test client | 2 | free (Linux) |
| A2 | **Android journey test:** a fake Brain (OkHttp `MockWebServer`) serving the sample JSON, and the app driven through consent, onboarding, pair, reveal, day, rating, offline rating, "Delete my data". It also covers the error paths: 429, 500, the server asleep (slow first answer), no connection. | Robolectric with Compose UI test, a new test dependency (`mockwebserver`) | 5 | free (Linux) |
| A3 | **iPhone unit tests:** `SafeLink.https`; Keychain save, update, migrate and load (the simulator has a Keychain); `clearLocal` leaves only the two display settings; money formatting; the Daylight contrast rule (4.5:1). | A test target in `project.yml`, run by hand with `xcodebuild test` on the macOS runner | 4 | about 10 macOS minutes a run (billed beyond the free quota: $0.062/min, GitHub billing docs, read 26 Sep; **re-check before relying on it**) |
| A4 | iPhone UI test (XCUITest) of the onboarding journey in demo mode | later, after Checkpoint 3 | 6 | macOS minutes |
| A5 | Largest text on more screens: Android font scale 2.0 renders of the pair, the day and the rating; iPhone screenshots of the same | extend the two existing lists | 1 | small |

A1 and A2 are the most useful per hour: they catch the commonest break, a Brain change that an app can't decode, on every push and for free. A3 is cheap insurance for the security-relevant Swift (SEC-15, SEC-16), which otherwise is only compiled.

## Real-device checklist for the next builds (both phones)

Run the rehearsal's 25 steps, then these. Minimum devices:
- **iPhone:** Abram's own, on the newest iOS (the app needs iOS 17 or later).
- **Android:** one phone on Android 16 (API 36). If anyone has one, also an old phone near the minimum (API 26, Android 8), for the slow path.

| # | Check | iPhone | Android | Pass when |
|---|---|---|---|---|
| 26 | Install the new build **over** the round's build | ☐ | ☐ | iPhone: data kept. Android: if the signing key changed (SEC-12), the old app must be removed first, and the person starts fresh (expected; say so to testers) |
| 27 | The stop line beside the price (m275) | ☐ | ☐ | "Recommended because…" or "Chosen to fit your route and hours…"; never a % or "strong match" |
| 28 | A booking link (a stay, a flight) | ☐ | ☐ | Opens the provider's https page in the browser |
| 29 | "Delete my data", then reopen | ☐ | ☐ | Fresh start; no old plan, code, feedback or video choice (SEC-15) |
| 30 | iPhone only: back up the phone (Finder or iCloud) and restore it onto a **different** iPhone, if one is available | ☐ | — | ODYS starts fresh there: the token stays on its own device (SEC-15) |
| 31 | Android 16: edge-to-edge on every main screen | — | ☐ | Nothing under the status or gesture bar |
| 32 | Android 16: the predictive back gesture from a stop card, a trip day and the pair | — | ☐ | Goes back one level; never leaves the app mid-pair |
| 33 | Notification permission: asked once after the first plan; reminders arrive for a rated stop's time | ☐ | ☐ | One prompt; a reminder fires; nothing if refused |
| 34 | Location on "Now": asked only when "Start from where I am" or "Now" is used; "when in use" only | ☐ | ☐ | The prompt text matches the privacy notice; refusing still works with a typed start |
| 35 | "Tell it instead" (speech), then speech refused | ☐ | ☐ | The text appears as typed; refusing leaves typing |
| 36 | VoiceOver / TalkBack through welcome, consent, one place card, the pair and a rating | ☐ | ☐ | Every control is announced with its purpose; the order makes sense |
| 37 | A small screen (iPhone SE size, or an Android at the largest display size) on the pair and the day | ☐ | ☐ | Nothing cut off |
| 38 | A day out with "Now" open and location on, for 3 hours | ☐ | ☐ | Battery used is noted (for comparison, not a pass mark) |
| 39 | Change the phone's time zone to New York, then back | ☐ | ☐ | Times still show London time where the app says so |
| 40 | Low Power Mode / Battery Saver on | ☐ | ☐ | Plans load; motion is reduced, not broken |
| 41 | Reinstall after deleting the app (not "Delete my data") | ☐ | ☐ | A fresh start (D124). Note what happens to the old install's answers on the server, and check that the privacy notice describes it |

**Recording:** a copy of this table per build in `validation/`, with the build numbers, the phones and their OS versions, and a screenshot for each failure. A failure in 27 to 30 or 34 blocks an external build. The others are judged by Abram.

## Hours

- **Claude:** A1 2 h, A2 5 h, A3 4 h. A5 1 h when convenient.
- **Abram:** about 1 h per phone for steps 26 to 41, on top of the rehearsal.
- **Cost:** none, apart from A3's few macOS minutes per run.
