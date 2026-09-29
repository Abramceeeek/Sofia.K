# Face: the iOS app (D50, D64, D70)

**Status (2026-09-28):** pipeline placeholder, with the real app code starting now (D107, lean mode). The build order is the Brain first (step 1 done), then native SwiftUI screens in three batches (`design/v0-screens.md`, Timing). Each batch ends with one simulator build in CI and a page of screenshots for Abram. `project.yml` (XcodeGen) and one "Pipeline check" screen proved that GitHub Actions can build with no Mac.

**The simulator build passed on its first run** (2026-09-26, run 36262736945; the build step took 18 s). Signing and upload haven't run yet.
- **Before the secrets exist:** any push that changes `app/` builds for the simulator only (no signing). That checks the runner, XcodeGen and the Swift.
- **After the secrets exist:** a push to `main`, or **Actions → ios → Run workflow** with "upload" ticked, archives, signs and uploads to TestFlight. The build number is the run number.

## Build 1 on your iPhone: what you do (about 1–1.5 h, D109)

Do these in order. Each has a check at the end. **Never paste a key, password or certificate into a chat with me:** they go straight into GitHub Secrets.

### 1. The membership (2 min)

developer.apple.com/account → Membership details. **Send me the expiry date.**
- TestFlight needs an active membership. If it lapses, you can't upload builds or open Certificates, Identifiers & Profiles (Apple's renewal page, read 29 Sep).
- The tests now run in the app until about the week of 23 Nov, so **the membership must stay active until then.** D74 said "renew only if Test B passes". If it expires before late November, renewing is a money decision for you (US$99 a year, in local currency).

### 2. The app's identity (10 min)

In Certificates, Identifiers & Profiles:
1. **Identifiers → +** → App IDs → App → an explicit bundle ID, e.g. `com.abdurakhmonbek.daysout`. No capabilities are needed.
2. **Certificates → +** → Apple Distribution. Reuse your earlier app's certificate instead if it's still valid.
   - Without a Mac, make the signing request with OpenSSL on any computer:
     ```
     openssl genrsa -out dist.key 2048
     openssl req -new -key dist.key -out dist.csr -subj "/CN=Abram/C=GB"
     ```
   - Upload `dist.csr` and download `distribution.cer`. Then make the `.p12` (choose a password):
     ```
     openssl x509 -inform DER -in distribution.cer -out dist.pem
     openssl pkcs12 -export -legacy -inkey dist.key -in dist.pem -out dist.p12
     ```
   - `-legacy` keeps the file readable by macOS's keychain tool (OpenSSL 3; UNVERIFIED whether the runner still needs it). Keep `dist.key` private.
3. **Profiles → +** → App Store Connect (distribution) → your App ID → the certificate → name it, e.g. "Days out App Store" → download the `.mobileprovision` file.

### 3. App Store Connect (10 min)

1. **Apps → + → New App:**
   - iOS; English (UK); the bundle ID from step 2; any SKU;
   - a name. It must be unique on the App Store and can change later; you choose it.
2. **Users and Access → Integrations → App Store Connect API → Team Keys → +:**
   - role App Manager;
   - download the `.p8` file (you can only download it once);
   - note the Key ID and the Issuer ID.

### 4. The six GitHub secrets (10 min)

GitHub → Settings → Secrets and variables → Actions → New repository secret. There are six:

| Secret | What it is |
|---|---|
| `BUILD_CERTIFICATE_BASE64` | `dist.p12`, base64-encoded |
| `P12_PASSWORD` | The password you chose for the `.p12` |
| `BUILD_PROVISION_PROFILE_BASE64` | The `.mobileprovision` file, base64-encoded |
| `APP_STORE_CONNECT_KEY_ID` | The API key's Key ID |
| `APP_STORE_CONNECT_ISSUER_ID` | The Issuer ID |
| `APP_STORE_CONNECT_KEY_BASE64` | The `AuthKey_XXXX.p8` file, base64-encoded |

- Base64 on Linux: `base64 -w0 file`.
- Base64 in Windows PowerShell: `[Convert]::ToBase64String([IO.File]::ReadAllBytes("file"))`.

### 5. The Brain on Render (10 min)

1. Render dashboard → Blueprints → your blueprint → **Sync**. If the blueprint syncs automatically, the service may already be there. It adds the `moments-brain` service from `render.yaml`:
   - free tier;
   - Frankfurt;
   - shares the swipe page's free database, because Render allows only one free database per workspace.
2. When it's live, open `https://<its address>/v1/health`. It should say `"ok": true`.
3. **Send me the address.** I'll put it in the app if it isn't `moments-brain.onrender.com`.

### 6. The first upload and your iPhone (15 min)

1. GitHub → Actions → **ios** → Run workflow → pick the branch `claude/vigilant-cannon-my82dj`, tick "upload" → Run. It builds, signs and uploads (about 10 min).
2. App Store Connect → your app → **TestFlight → Internal Testing → +** → add a group and add yourself. Internal testers need no App Review (Apple, read 29 Sep).
3. On your iPhone, install **TestFlight** from the App Store, accept the invitation and install **Days out**.

**The check:**
- Open the app and agree.
- Answer the questions (about 15 min), then make a plan.
- The first answer may take up to a minute while the free server wakes up. The app says so.

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
