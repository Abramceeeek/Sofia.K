# The Android release key: made and kept by Abram, never in GitHub (19 Nov 2026)

Abram's decision of 19 Nov, §6: generate the release key locally with Android's own tools, keep it under his control, with:
- a secure password;
- an encrypted backup;
- a recovery procedure;
- a recorded fingerprint;
- development and production signing kept apart.

**The key and its password never go to Claude, to the repository, or to GitHub Secrets.** This replaces the 16 Nov plan, which put the key in GitHub Secrets. It is not needed for the friends' round (below). Needed before Android strangers or Google Play.

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

## The friends' round

**It doesn't need this.** Testers use the existing build 21, from the `android-latest` pre-release.

**One thing to know before inviting Android friends: the repository is public** (GitHub reports `visibility: public`, 19 Nov). The 11 Nov audit assumed it was private.
- **The good:** anyone can download build 21 from the release link, so friends need no access.
- **The cost, SEC-12 at its higher severity:** the debug key that signs build 21 is in the repository with its password. Anyone could sign a lookalike app that installs over ODYS on a tester's phone, and inherits its data.
- **For the round:**
  - send friends **only** the release link;
  - give them the sha256 to check if they want: `43a3e80dd38abdab72a3a1bb2da6f7c2b8104682729189829a83d4563129174c`;
  - tell them to install no ODYS file from anywhere else.
- **Whether the repository should stay public is Abram's decision** (`first-real-user-readiness-plan.md`).

## The fingerprint (filled in after step 4)

| Key | SHA-256 fingerprint | Made | Backup proven |
|---|---|---|---|
| `odys-release` | *to be filled in by Abram* | — | — |
