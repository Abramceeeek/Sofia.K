# Face: the iOS app (D50, D64, D70)

**Status (2026-09-28):** pipeline placeholder, with the real app code starting now (D107, lean mode). The build order is the Brain first (step 1 done), then native SwiftUI screens in three batches (`design/v0-screens.md`, Timing). Each batch ends with one simulator build in CI and a page of screenshots for Abram. `project.yml` (XcodeGen) and one "Pipeline check" screen proved that GitHub Actions can build with no Mac.

**The simulator build passed on its first run** (2026-09-26, run 36262736945; the build step took 18 s). Signing and upload haven't run yet.
- **Before the secrets exist:** any push that changes `app/` builds for the simulator only (no signing). That checks the runner, XcodeGen and the Swift.
- **After the secrets exist:** a push to `main`, or a manual run with "upload" ticked, archives, signs and uploads to TestFlight. The build number is the run number.
- **The "Run workflow" button only appears once the workflow is on `main`** (GitHub: "the workflow file exists on the default branch", read 30 Sep). `main` still holds only the first commit. A workflow that has run before can still be started on any branch through GitHub's API, so **Claude starts the upload run** when you say the secrets are in. Merging the branch into `main` later brings the button back.

## Build 1 on your iPhone: the signing set-up, step by step (about 45–60 min, D109)

Do these in order. Each step says where to click and what to keep. **Never paste a key, password or certificate into a chat with me:** they go straight into GitHub Secrets. Checked against Apple's help pages and GitHub's docs on 30 Sep 2026 (`research/sources.csv`).

### 0. Before you start (5 min)

- **A computer with a terminal.**
  - Windows: install **Git for Windows** and use **Git Bash**, which includes OpenSSL.
  - Mac or Linux: the built-in Terminal.
  - Your iPhone can't do steps 3–5.
- **One private folder** for the files you'll make, e.g. `Documents/daysout-signing`. Keep it off shared drives, and never put it in the repo.
- **A password manager entry** for the `.p12` password (step 5).

### 1. Ask Apple for App Store Connect API access (2 min, then a wait). Do this first

**Why first:** Apple approves this request "on a case-by-case basis", so it may take a while. Only the Account Holder can ask, which is you.

1. Go to appstoreconnect.apple.com and open **Users and Access**.
2. Click **Integrations**. It opens on **App Store Connect API**.
3. Click **Request Access**, tick the terms and click **Submit**.

**Check:** the page shows the request as submitted. Carry on with steps 2–7 while you wait. Step 8 needs the approval.

### 2. Register the App ID (5 min)

1. Go to developer.apple.com/account and open **Certificates, Identifiers & Profiles**.
2. Click **Identifiers**, then **+**. Choose **App IDs**, then **App**, then **Continue**.
3. **Description:** `Days out`.
4. **Bundle ID:** choose **Explicit** and enter e.g. `com.abdurakhmonbek.daysout`.
   - Pick it with care: the app record in step 7 is tied to it for good.
   - The app's display name can change later; the bundle ID can't.
5. Leave every capability unticked. Click **Continue**, then **Register**.

**Check:** the new App ID is in the list.

### 3. Make a certificate signing request (5 min)

In the terminal, go to your private folder and run:
```
openssl genrsa -out dist.key 2048
MSYS_NO_PATHCONV=1 openssl req -new -key dist.key -out dist.csr -subj "/emailAddress=YOUR_APPLE_ID_EMAIL/CN=Abram Distribution/C=GB"
```
- `MSYS_NO_PATHCONV=1` stops Git Bash on Windows from treating `/emailAddress=…` as a file path. It does nothing on a Mac or Linux.
- `dist.key` is the private key. **Anyone who has it can sign apps as you**, so never share it.
- Apple's help shows the same OpenSSL form for a request made without Keychain Access.

**Check:** the folder now holds `dist.key` and `dist.csr`.

### 4. Create the Apple Distribution certificate (3 min)

1. In Certificates, Identifiers & Profiles, click **Certificates**, then **+**.
2. Choose **Apple Distribution** and click **Continue**.
3. Upload `dist.csr` and click **Continue**, then **Download**. You get `distribution.cer`; move it into your folder.

**Check:** the certificate is listed with an expiry date about a year away.

### 5. Package the certificate and key as a `.p12` (3 min)

```
openssl x509 -inform DER -in distribution.cer -out dist.pem
openssl pkcs12 -export -inkey dist.key -in dist.pem -out dist.p12 \
  -certpbe PBE-SHA1-3DES -keypbe PBE-SHA1-3DES -macalg sha1
```
- It asks for an export password. Choose a strong one and save it in your password manager: it becomes the `P12_PASSWORD` secret.
- The three `PBE-SHA1-3DES` / `sha1` options use the older encryption that macOS's keychain tool reads without trouble. OpenSSL 3 would otherwise use a newer default, which older macOS versions couldn't import (Claude's reading; UNVERIFIED on the current runner).
- If the upload run later fails with "No signing identity in the .p12", redo this step with `-legacy` in place of those three options.

**Check:** `dist.p12` exists.

### 6. Create the App Store Connect provisioning profile (3 min)

1. In Certificates, Identifiers & Profiles, click **Profiles**, then **+**.
2. Under **Distribution**, choose **App Store Connect** and click **Continue**.
3. Choose the App ID from step 2 and click **Continue**.
4. Choose the certificate from step 4 and click **Continue**.
5. **Name:** `Days out App Store`. Click **Generate**, then **Download**.

The CI job reads your team, the bundle ID and this profile's name from the file itself, so none of them are secrets.

**Check:** a `.mobileprovision` file is in your folder.

### 7. Create the app record in App Store Connect (5 min)

1. Go to appstoreconnect.apple.com and open **Apps**. Click **+**, then **New App**.
2. **Platform:** iOS.
3. **Name:** your choice. It must be unique on the App Store; if "Days out" is taken, try e.g. "Days out: London". You can change it later.
4. **Primary language:** English (UK).
5. **Bundle ID:** the one from step 2.
6. **SKU:** any private reference, e.g. `daysout-001`.
7. **User access:** Full Access. Click **Create**.

**Check:** the app page opens.

### 8. Generate the API key (3 min, once Apple has approved step 1)

1. Go to **Users and Access**, then **Integrations**, then **App Store Connect API**, then **Team Keys**.
2. Click **Generate API Key** (or **+**).
3. **Name:** `GitHub CI`. **Access:** **App Manager**, which Apple lists as allowed to upload builds. Click **Generate**.
4. Click **Download API Key**. **This works only once**: you get `AuthKey_XXXXXXXXXX.p8`; move it into your folder.
5. Copy two values into your password manager:
   - the **Key ID**, shown in the key's row;
   - the **Issuer ID**, shown above the table.

**Check:** you have the `.p8` file, the Key ID and the Issuer ID.

### 9. Turn the three files into base64 text (3 min)

- **Git Bash, Linux or Mac:** `base64 -w0 dist.p12 > dist.p12.txt`
  - Do the same for the `.mobileprovision` file and the `.p8` file.
  - On a Mac, use `base64 -i dist.p12 -o dist.p12.txt`.
- **PowerShell:**
  ```
  [Convert]::ToBase64String([IO.File]::ReadAllBytes("dist.p12")) | Out-File -Encoding ascii dist.p12.txt
  ```

**Check:** each `.txt` file is one long line of letters and digits.

### 10. Add the six GitHub secrets (5 min)

1. On GitHub, open the repository and go to **Settings → Secrets and variables → Actions**.
2. For each row below, click **New repository secret**, paste the value exactly and click **Add secret**.

| Secret | Paste |
|---|---|
| `BUILD_CERTIFICATE_BASE64` | the contents of `dist.p12.txt` |
| `P12_PASSWORD` | the password from step 5 |
| `BUILD_PROVISION_PROFILE_BASE64` | the contents of the `.mobileprovision` `.txt` |
| `APP_STORE_CONNECT_KEY_ID` | the Key ID |
| `APP_STORE_CONNECT_ISSUER_ID` | the Issuer ID |
| `APP_STORE_CONNECT_KEY_BASE64` | the contents of the `.p8` `.txt` |

**Check:** six secrets are listed. GitHub never shows a value again, which is expected.

### 11. Make an internal testing group with you in it (3 min)

1. In App Store Connect, open your app, then the **TestFlight** tab.
2. Next to **Internal Testing**, click **+**.
3. Name the group `Me` and tick **Enable automatic distribution**, so every new build reaches you without a click. Click **Create**.
4. Click **Invite Testers**, tick yourself and click **Add**.
   - Internal testers must be users on your App Store Connect account, up to 100.
   - Builds for internal testers need no App Review.

### 12. The first upload (you: 1 min; the run: about 10 min)

1. **Tell me "the secrets are in"** (never the values). I start the `ios` workflow on the branch with "upload" ticked, through GitHub's API.
2. The run archives, signs and uploads the build.
3. Apple then processes the build before it appears under TestFlight. How long that takes: UNVERIFIED; minutes to an hour is typical.

**If the run fails,** the log names the step; I fix what's in the code. For a secret, the log says which one to redo.

### 13. Install it on your iPhone (5 min)

1. Install **TestFlight** from the App Store.
2. Open the invitation email on the iPhone (or TestFlight shows it) and tap **Accept**, then **Install**.

### 14. Tidy up (5 min)

- Keep `dist.key`, `dist.p12`, the `.p8` file and the passwords in your password manager or encrypted storage. Delete loose copies from Downloads and the `.txt` files.
- **If anything leaks:**
  - revoke the certificate (Certificates, Identifiers & Profiles);
  - revoke the API key (Users and Access → Integrations);
  - then redo steps 3–10.
- The certificate lasts about a year. When it expires, redo steps 3–6 and update three secrets.

### The Brain on Render (10 min, still needed before the app can plan)

1. Render dashboard → Blueprints → your blueprint → **Sync**. If the blueprint syncs automatically, the service may already be there. It adds the `moments-brain` service from `render.yaml`:
   - free tier;
   - Frankfurt;
   - shares the swipe page's free database, because Render allows only one free database per workspace.
2. When it's live, open `https://<its address>/v1/health`. It should say `"ok": true`.
3. **Send me the address.** I'll put it in the app if it isn't `moments-brain.onrender.com`.

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
