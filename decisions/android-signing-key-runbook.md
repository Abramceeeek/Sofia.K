# The Android release key: made and kept by Abram, never in GitHub (19 Nov 2026)

Abram's decision of 19 Nov, §6: generate the release key locally with Android's own tools, keep it under his control, with:
- a secure password;
- an encrypted backup;
- a recovery procedure;
- a recorded fingerprint;
- development and production signing kept apart.

**The key and its password never go to Claude, to the repository, or to GitHub Secrets.** This replaces the 16 Nov plan, which put the key in GitHub Secrets. It is needed for Android friends only under option B below, and before Android strangers or Google Play.

**Sources, read 19 Nov 2026:**
- developer.android.com/studio/publish/app-signing;
- developer.android.com/tools/apksigner;
- developer.android.com/build/building-cmdline;
- the keytool reference for Java 21 (docs.oracle.com/en/java/javase/21/docs/specs/man/keytool.html).

## The decisions this follows

- **Signing happens on Abram's computer.**
  - CI builds the **unsigned** release APK, or later the app bundle.
  - Abram downloads it, signs it locally, checks it and publishes it.
  - About 10 minutes a release.
  - The private key never exists anywhere he doesn't control.
- **When Google Play comes:** use **Play App Signing**.
  - Google holds the app signing key; Abram's key becomes the **upload key**.
  - Android: "if you lose your upload key, or if it is compromised, you can request an upload key reset in the Play Console".
  - Without Play App Signing: "if you lose your app's signing key, you lose the ability to update your app".
  - **So the first Play upload should opt in.**
- **Validity:** Android says a key "should be valid for at least 25 years", and Google Play needs one "ending after 22 October 2033". 10,000 days is about 27 years.

## Step by step (Abram, about 45 minutes once)

1. **Tools:** a JDK (for `keytool` and `jarsigner`), and the Android SDK Build Tools 24.0.3 or newer (for `zipalign` and `apksigner`). These come with Android Studio.
2. **A password:** let a password manager generate it (24+ random characters) and save it there before running anything.
3. **Make the key** (keytool's own options; PKCS12 is named explicitly, so the format doesn't depend on the JDK's default):

```bash
keytool -genkeypair -v -storetype PKCS12 -keystore odys-release.p12 -alias odys-release -keyalg RSA -keysize 4096 -validity 10000
```

   - It asks for the password and a name: "ODYS" and the company or his own name is enough. **No other personal details are needed.**

4. **Record the fingerprint.** keytool: "By default, this command prints the SHA-256 fingerprint of a certificate."

```bash
keytool -list -keystore odys-release.p12 -alias odys-release
```

   - He sends **only the SHA-256 fingerprint** (a public value). It goes into this file below, and CI checks signed builds against it.

5. **The encrypted backup:**
   - (a) attach `odys-release.p12` to the password manager entry that holds its password;
   - (b) one offline copy on an encrypted drive, kept somewhere else;
   - (c) **never** in the repository, in email, in a chat, or in cloud storage without encryption.
6. **Prove the backup works** (now, then once a year): from the backup copy, run step 4's command. The fingerprint must match.

## Signing a release (each time)

```bash
zipalign -v -p 4 app-release-unsigned.apk app-release-unsigned-aligned.apk
```

```bash
apksigner sign --ks odys-release.p12 --out ODYS-android-release.apk app-release-unsigned-aligned.apk
```

```bash
apksigner verify --print-certs ODYS-android-release.apk
```

- These are the commands Android documents. `zipalign` must come before `apksigner`: "If you sign your APK using apksigner and make further changes to the APK, the APK's signature is invalidated."
- **Check the result:** the certificate shown by `--print-certs` must match the recorded fingerprint. Android's page doesn't say which digests it prints, so compare the SHA-256 line if present. Otherwise run `keytool -printcert -jarfile ODYS-android-release.apk`.
- **For Google Play's app bundle:** "You cannot use apksigner to sign your app bundle." Use:

```bash
jarsigner -keystore odys-release.p12 app-release.aab odys-release
```

## Keeping development and production apart (Claude, about 3 h, after the round)

- `android/app/debug.keystore` stays for development builds only.
- **The CI workflow builds the `release` type unsigned**, with no signing configuration and no secret.
- **A CI check fails** if any release artifact is signed with the debug certificate. It compares against the debug keystore's own fingerprint.
- Testers move from the debug build to the release build **between rounds, never inside one.**
  - A different signature can't install over the old app, so each tester uninstalls first.
  - Their phone then makes a new install id, and their old answers stay with the old one on the server.

## Recovery

| What happens | What to do |
|---|---|
| The password manager entry is lost | The offline copy and the password, if he kept the password elsewhere; otherwise as "the key is lost" |
| The key is lost, **with** Play App Signing | Make a new upload key (step 3), then "request an upload key reset in the Play Console"; users' updates continue |
| The key is lost, **without** Play (sideloaded test builds) | No update can install over the old app. Testers uninstall and install the new one, as above. This is why the first Play upload opts in to Play App Signing |
| The key is exposed | As lost. With Play: reset the upload key. Without: a new key, and testers reinstall. Note the date and what was signed since |

## Build 21 and the friends' round (checked 20 Nov; Abram's decision of 20 Nov §3)

**Build 21 is signed with the exposed debug key, and is a debuggable build. Under Abram's rule, it is not distributed as a standalone APK.**

| His check (20 Nov §3) | Result | How |
|---|---|---|
| 1. The exact signing certificate of build 21 | SHA-256 `a07dae0c6c3d90b57cdae26856052624169625e6b6cc6949996f7d054a49cfb9` (APK Signature Scheme v2; no v1 or v3 signature) | the public `ODYS-android-21.apk` downloaded from `android-latest`. Its file sha256 is `43a3e80d…174c`, the manifest's. Its v2 signing block was read with a short script, so no Android SDK was needed |
| 2. The official distribution channel | the GitHub pre-release `android-latest` of this repository, published by `android.yml` from `main` (run 21, `80a0da3`, 6 Nov) | the release and the workflow |
| 3. Whether build 21 is signed with the exposed key | **Yes.** The debug keystore committed at `android/app/debug.keystore` holds a certificate with **the same SHA-256** (`CN=ODYS Debug, O=ODYS, C=GB`, valid 9 Oct 2026 to 2054). Its password is in `build.gradle.kts` in the public repository, so anyone can sign an APK that installs over ODYS as an update | `keytool -exportcert` on the committed keystore, compared byte for byte. The password was read from the build file and never printed |
| (also) Debuggable | **Yes:** `android:debuggable` is true in the APK's manifest. `android.yml` builds `assembleDebug`. Someone with the phone in hand and USB debugging on could read the app's own files, the install token included | the APK's binary manifest |
| 4. A secure release-signing strategy | this page, from "The decisions this follows" to "Recovery": a key made and kept by Abram, never in GitHub; signing on his computer; Play App Signing later | — |
| 5. Future release builds use a separate key | "Keeping development and production apart" above: CI builds `release` unsigned, and a CI check fails any release artifact signed with the debug certificate (`a07dae0c…cfb9`). About 3 h, after the round | — |

**What the frozen code allows.** At `80a0da3` the Android app reads only `BuildConfig.BRAIN_BASE_URL` and `VERSION_NAME`/`VERSION_CODE`. Nothing reads `BuildConfig.DEBUG`, and R8 is off for both build types. So a `release` build of the same commit runs the same code; only its signature and the debuggable flag differ.

**The three ways forward for Android friends (Abram's decision):**

| | What | Abram's time | Effect on the round |
|---|---|---|---|
| **A. iPhone only (recommended for the first invites)** | Invite only friends with an iPhone. TestFlight 91 is Apple-signed and unaffected. Android friends join a later round, once a release build exists | none | The cleanest: one build, one rehearsal phone. The sample may be smaller |
| **B. A properly signed build of the same commit** | On his computer:<br>• make the release key (steps 1–6 above);<br>• `git worktree add ..\odys-80a0da3 80a0da3`, then in its `android\` folder set `$env:BUILD_NUMBER = "121"` and run `.\gradlew assembleRelease`;<br>• `apksigner sign --ks odys-release.p12 --out ODYS-android-121.apk app\build\outputs\apk\release\app-release.apk`. That apksigner replaces the debug signature, rather than adding a second one, is **UNVERIFIED** in Android's docs, so the next step checks it;<br>• `apksigner verify --print-certs ODYS-android-121.apk` must show **only** the release fingerprint.<br>Then publish it through a channel he controls (for example a manual GitHub release, `android-friends-1`, with its sha256), and run the Android half of the rehearsal **on that exact file** | ~1.5 h once | The same code and Brain, so Test B is unchanged. The manifest records the new file and its sha256, and the Android row of the preflight checks it. **A phone with build 21 must uninstall it first**: a different signature can't install over it |
| C. Build 21 as it is | — | — | **Ruled out** by Abram's rule |

**Making the repository private doesn't undo the exposure.** The debug key has been public, so it stays compromised. Any build signed with it is treated as untrusted from now on, whichever option is chosen.

## The fingerprint (filled in after step 4)

| Key | SHA-256 fingerprint | Made | Backup proven |
|---|---|---|---|
| `odys-release` | *to be filled in by Abram* | — | — |
