# Face: the iOS app (D50, D64, D70)

**Status (2026-09-26):** pipeline placeholder only. `project.yml` (XcodeGen) and one "Pipeline check" screen let GitHub Actions prove it can build, sign and upload with no Mac. **The real app code waits until Test B reports (D65).** The screens it will build are in `design/v0-screens.md`.

Nothing here has run yet. The first run of `.github/workflows/ios.yml` is the first real check.
- **Before the secrets exist:** any push that changes `app/` builds for the simulator only (no signing). That checks the runner, XcodeGen and the Swift.
- **After the secrets exist:** a push to `main`, or **Actions → ios → Run workflow** with "upload" ticked, archives, signs and uploads to TestFlight. The build number is the run number.

## What you add (about 0.5 h)

**First, in App Store Connect:** create the app record (**Apps → + → New App**) with the bundle ID you'll use. The upload fails without it. It needs an **App Store distribution** provisioning profile for that bundle ID.

**Then in GitHub: Settings → Secrets and variables → Actions → New repository secret.** There are six:

| Secret | What it is |
|---|---|
| `BUILD_CERTIFICATE_BASE64` | Your **Apple Distribution** certificate with its private key, as a `.p12` file, base64-encoded |
| `P12_PASSWORD` | The password you set when exporting the `.p12` |
| `BUILD_PROVISION_PROFILE_BASE64` | The App Store distribution profile (`.mobileprovision`), base64-encoded |
| `APP_STORE_CONNECT_KEY_ID` | The API key's Key ID (App Store Connect → Users and Access → Integrations → App Store Connect API) |
| `APP_STORE_CONNECT_ISSUER_ID` | The Issuer ID shown on the same page |
| `APP_STORE_CONNECT_KEY_BASE64` | The downloaded `AuthKey_XXXX.p8`, base64-encoded |

- To base64-encode a file without a Mac:
  - Linux: `base64 -w0 file`
  - Windows PowerShell: `[Convert]::ToBase64String([IO.File]::ReadAllBytes("file"))`
- The workflow reads the **team ID, bundle ID and profile name from the profile itself**, so they need no secrets.
- It makes its own **throwaway keychain password**, which GitHub's guide says can be any random string. That is one secret fewer than the guide uses.
- If your earlier project used other secret names, rename them here or in the workflow. The six values are the same.
- The API key needs a role that can upload builds. Claude's understanding is that **App Manager** or **Admin** can (UNVERIFIED).

## How it works

1. The job runs on the `macos-26` runner (Xcode 26; generally available since 2026-02-26).
   - Since 28 Apr 2026, App Store Connect only takes builds made with the iOS 26 SDK. Apple's "Upcoming requirements" page was searched on 2026-09-26.
   - It runs only when `app/**` or the workflow changes, or when you start it by hand. The Brain's tests run separately on Linux (`brain-tests.yml`).
2. `xcodegen generate` makes `Face.xcodeproj`. The project file is never committed.
3. **Signing** follows GitHub's guide "Installing an Apple certificate on macOS runners for Xcode development" (fetched 2026-09-26). The job imports the `.p12` into a temporary keychain and installs the profile.
4. **Upload:** `xcodebuild -exportArchive` with `destination = upload`, method `app-store-connect`, and the App Store Connect key flags (`-authenticationKeyPath/-KeyID/-KeyIssuerID`, from the xcodebuild man page).
   - The first run prints the export keys that this Xcode accepts, which confirms the key names.
   - If a key has been renamed, the log shows it.

**Cost:**
- macOS minutes are **$0.062 a minute** beyond the free quota on private repos (2,000 minutes a month on GitHub Free), and free on public repos (GitHub billing docs, fetched 2026-09-26).
- Whether macOS minutes use up the free quota faster than Linux minutes: UNVERIFIED.
- **Without a payment method on file, GitHub blocks usage once the quota is used, rather than charging.**
- A build takes about 5–10 min (Claude's estimate, UNVERIFIED until the first run).

**Local run:** not possible here (no Mac). Every check goes through CI (D64).
