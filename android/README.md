# ODYS for Android (D125)

The same app as `app/` (iPhone), in Kotlin and Jetpack Compose: the same screens, words and order, the ODYS design,
and the same Brain (`https://moments-brain.onrender.com`). Built on Linux by `.github/workflows/android.yml`.

## Install it (Abram, about 5 minutes)

1. On the Android phone, open **github.com/Abramceeeek/Sofia.K/releases/tag/android-latest** (the repository is
   public, so no sign-in is needed, and anyone with the link can download it too).
2. Under **Assets**, tap `ODYS-android-<build>.apk` to download it.
3. Open the download. If Android asks, allow installs from your browser ("Install unknown apps"), then **Install**.
4. A newer build installs over the old one and keeps your answers (each build is signed with the same key).

Android may warn that the app is from an unknown developer. That's because it isn't from Google Play yet
(after-9-Nov #67).

## Each build

- A push that changes `android/` (or the workflow) runs the workflow. It:
  1. draws every screen;
  2. builds the APK;
  3. keeps both with the run;
  4. replaces the `android-latest` pre-release.
- **Every screen drawn first:** `app/src/test/java/com/odys/app/ScreensTest.kt` (Robolectric) draws 46 screens and
  sheets with the iPhone app's sample data (`app/Sources/Demo`), with no server. A screen that crashes stops the
  build. The pictures are the run's `ODYS-android-screens-<n>` artifact.
- Locally: `ANDROID_HOME=<sdk> ./gradlew testDebugUnitTest assembleDebug`. The pictures land in `app/build/screens`.

## Where it differs from the iPhone, and why

| | iPhone | Android |
|---|---|---|
| Maps | Apple MapKit | OpenStreetMap tiles: no key, credit shown, the app named in each request. No guarantee of service, so a paid provider is needed before a public release |
| Directions | Apple Maps | Google Maps (a link; no key) |
| Speech | On-device | On-device only (Android 12+); otherwise type |
| Location | When in use | While using the app only; never in the background |
| Rating reminders | Local notifications | WorkManager on the phone; Android 13+ asks first |
| Share | Share sheet, "sent" | Share sheet; "shared" means an app was picked |
| Reinstall | Old answers deleted from the server | Can't be deleted after a reinstall (the code goes with the app); Delete my data first, or they go on 31 March 2027 |
| Videos | Left out until the files exist | The same |

## Files

- `app/src/main/java/com/odys/app/`:
  - **The app's state:** `AppModel.kt`, a port of `AppModel.swift` and `TripLogic.swift`.
  - **Talking to the Brain:** `BrainClient.kt` and `Models.kt`.
  - **The design:** `Theme.kt` and `Odys.kt`, the ODYS colours, type, parts and motion.
  - **Screens:** one file per area. `FirstRun`, `Onboarding`, `Pair`, `Plan`, `Day` ("Now"), `Trips`, `Book`, `Safety` and
    `ShareCard`.
- `app/debug.keystore`: a debug key only (public passwords). A Google Play key goes in GitHub Secrets, never here.
