# A security-only release: what to put on the live Brain now, what waits (16 Nov 2026)

Abram's review of the audit, part 2 (12 Nov). **This is a proposal. Nothing has been deployed, merged into `main`, or changed in Render.** It covers four things: the status of every finding, what would go to the live Brain and when, the Android signing key (SEC-12), and the iPhone privacy manifest (SEC-14). It also covers verifying the address header (SEC-05).

**The fixes on the audit branch are not production protection.** Production runs `main` at `80a0da3` (tag `friends-round-1`, TestFlight 91, Android 21). Every finding below marked "fixed" is fixed **on the branch only**: it protects nobody until Abram releases it.

## Recommendation

1. **During the friends' round, release one small patch to the live Brain, if Abram approves:**
   - **The patch (it changes no question, algorithm, plan or answer a tester sees):**
     - SEC-06: don't keep "where I am" or the stay's name;
     - SEC-09: no message or contact in the alert;
     - SEC-04: one bad number can't break the export;
     - SEC-08: the backup route error.
   - **Why now:** SEC-06 and SEC-09 are privacy gaps affecting testers' data today. SEC-04 protects the round's own analysis.
   - **Where it is built:** a branch cut from `80a0da3` (about 3 h, below).
2. **Before strangers:** the rest of the Brain fixes (SEC-01, SEC-02, SEC-03, SEC-05, SEC-07, SEC-10 and SEC-19), with the m275/m276 changes, as the next normal release.
   - These add limits and validation that could refuse a request. That risk is acceptable between rounds, not inside one.
3. **The next app builds (after the round; the round's builds are frozen):** SEC-13, SEC-15 and SEC-16 (built and tested on the branch), plus SEC-12 and SEC-14 once Abram has made the decisions below.
4. **Abram can do one thing today with no code at all:**
   - Look in Render at whether `BRAIN_ALERT_WEBHOOK_URL` is set.
   - If it is, the live Brain copies each Help & safety message and any contact into that channel (SEC-09).
   - Until the patch is live, clear old alerts from the channel after reading them.

## Status of every finding

Key:
- **Branch:** fixed and tested on `claude/pensive-euler-fftd63`.
- **Prod:** the live Brain or the round's builds still have the problem.
- **Config:** needs a setting outside the code.
- **Build:** needs a new app build.
- **Abram:** needs his decision or his action.

| Finding | Branch | Prod | Config | Build | Abram | When |
|---|---|---|---|---|---|---|
| SEC-01 rate limits bypassed by made-up tokens | fixed | present | — | — | release | before strangers |
| SEC-02 no limit on request size | fixed | present | — | — | release | before strangers |
| SEC-03 impossible dates and places | fixed | present | — | — | release | before strangers |
| SEC-04 one infinity breaks the export | fixed | present | — | — | release | **patch now** (protects the round's read-out) |
| SEC-05 the address header (Cloudflare's own used first; IPv6 as /64) | fixed in part; check route added | present | confirm Render's header (below) | App Attest / Play Integrity before public release | release; check | before strangers |
| SEC-06 "where I am" and the stay name kept | fixed | **present** | — | — | release; whether to clean pins already stored | **patch now** |
| SEC-07 API pages list admin routes | fixed | present | — | — | release | before strangers |
| SEC-08 backup route error on a bad token | fixed | present | — | — | release | patch now (harmless) |
| SEC-09 safety message and contact copied to the alert | fixed (alert carries only "message #N is waiting") | **present if a webhook is set** | check `BRAIN_ALERT_WEBHOOK_URL` | — | check today; release | **patch now** |
| SEC-10 a restore brings back deleted people | fixed (deletion record, `restore --deletions`, `verify`) | present | — | — | release | **before any restore**, so before a database move (`infrastructure-decision.md`) |
| SEC-11 database expires 6 Dec; one instance | — | **present** | Render plan | — | **money: his** | before 29 Nov (`infrastructure-decision.md`) |
| SEC-12 Android debug build, key in the repository | plan below | present | a key in GitHub Secrets | yes | **create the key; choose tester delivery** | before Android strangers |
| SEC-13 Android targets API 35 | fixed (API 36; CI green) | present | — | yes | — | next Android build |
| SEC-14 no iPhone privacy manifest | inventory below | present | — | yes | **the privacy answers** | before external TestFlight to strangers |
| SEC-15 iPhone token in backups, cached answers, leftovers after "Delete my data" | fixed (Keychain this-device-only, cache off, full clear) | present | — | yes | — | next iPhone build |
| SEC-16 links from the server opened as they come | fixed (https only, both apps) | present | — | yes | — | next builds |
| SEC-17 CI: actions by tag, write token on every run | fixed (pinned by SHA; write only to publish on `main`) | n/a (CI) | — | — | merge | with the branch |
| SEC-18 referral counts can be inflated | accepted | present | — | — | revisit before paying per referral | — |
| SEC-19 one search cap for everyone | fixed (20 a day per install, on top) | present | — | — | release | before live provider keys |
| SEC-20 Android map tiles from openstreetmap.org | open | present | — | yes | tiles choice (`map-tiles-and-place-data.md`) | before public release |
| SEC-21 tests never ran on Postgres | fixed (a Postgres 18 job in CI; it found one real bug, now fixed) | n/a (CI) | — | — | merge | with the branch |
| SEC-22 tag `friends-round-1` not pushed | — | — | — | — | push the tag (the session's proxy refused it) | before the round |

## The patch during the round, exactly

- **What goes in:**
  - the four fixes and their tests from commits `f496b20` (SEC-04, SEC-06 and SEC-08 parts) and `2f2f510` (SEC-09 part);
  - each applied by hand to `80a0da3`'s code, because the branch has moved on from it;
  - nothing else.
- **Not included:**
  - the limits (SEC-01 and SEC-02) and the validation (SEC-03);
  - docs off (SEC-07);
  - the deletion record (SEC-10);
  - any planner or wording change (m275, m276).
- **Checks before Abram decides:**
  - the full test suite;
  - a diff review showing that no file under `brain/data/testb`, `testb.py`, `dayplan.py`, `planner.py` or `scoring.py` changed;
  - one plan and one Test B pair compared byte for byte with `80a0da3`'s answers for the same install.
- **How it reaches Render: Abram's choice.**
  - Render deploys `main`, and nothing may be committed to `main` without his explicit approval (m198).
  - So either he approves a merge of the patch branch into `main` and checks `/v1/health` `version` afterwards,
  - or he leaves the round as it is and takes the patch with the next release.
- **Cost:** about 3 h to build and check, plus his review.
- **Note:** this session can push only its own branch, so the patch branch would be created when he says so.
- **Stored data:** the patch stops new pins and stay names being kept. **Cleaning those already stored** (SEC-06) is a separate, destructive step on the live database. It's his decision, and it is never run without his explicit approval.

## SEC-12: the Android release key (plan; no key generated or stored)

1. **Abram makes the key on his own computer** (about 15 min), never in the repository:
   - `keytool -genkeypair -v -keystore odys-upload.jks -alias odys -keyalg RSA -keysize 4096 -validity 10000`.
   - He keeps the file and both passwords in his password manager, with an offline copy. If the key is lost, the app's updates can't be signed. Play App Signing reduces this: Google holds the app signing key, and the upload key can be reset.
2. **GitHub Secrets** (Abram, about 10 min):
   - `ANDROID_UPLOAD_KEYSTORE_B64` (the file in base64);
   - `ANDROID_UPLOAD_STORE_PASSWORD`, `ANDROID_UPLOAD_KEY_PASSWORD`, `ANDROID_UPLOAD_KEY_ALIAS`.
3. **The build changes** (about 3 h; Claude):
   - The `release` build type reads the key from the secrets, only in the publish job on `main`. The file is written to the runner's temporary directory and deleted after the build.
   - Shrinking turns on with keep rules for serialization, followed by a full Robolectric pass.
   - Testers get the release build. `debug.keystore` stays only for local debug builds, and a CI check fails if a release build is signed with it.
4. **Testers move once** (needs Abram's decision on timing):
   - A new signature can't update the old app. Each tester uninstalls and installs again.
   - On reinstall, the phone makes a new install token, so the Brain sees a new person. Their answers and ratings stay with the old token, unlinked.
   - **So switch between rounds, never inside one.**
5. **How testers get it** (Abram): Google Play internal testing (needs a Play developer account: a one-off fee, his money) or Firebase App Distribution. **Never by making the repository public**, which would publish the old key and every document.

## SEC-14: what the iPhone app does that the privacy manifest must declare (inventory; answers are Abram's)

**Read from the code on 16 Nov:**
- `app/Sources`, 26 Swift files;
- `project.yml`;
- no Swift packages, so there are no third-party SDKs with manifests of their own.

| What | Found | Where | What the manifest needs |
|---|---|---|---|
| `UserDefaults` (a "required reason" API) | 84 uses | AppModel, BrainClient, TripLogic, TripViews, PlanViews, FirstRunViews, Location | a reason. Apple's code for "the app's own data" is `CA92.1` (**UNVERIFIED this session**; Abram or Claude re-reads Apple's list before the file is written) |
| File timestamps, system boot time, disk space, active keyboards | **none** | — | nothing |
| Tracking (IDFA, App Tracking Transparency) | none | — | `NSPrivacyTracking` false, no tracking domains |
| Location | when in use, on the phone; "Start from where I am" sends one point rounded to ~100 m, not kept | Location.swift | **Abram:** whether a point used once and not kept counts as "collected" for Apple's labels |
| Speech | on the phone (`requiresOnDeviceRecognition`); only the text is sent | Speech.swift | **Abram:** the text is an answer like a typed one |
| Notifications | local only (rating reminders) | Reminders.swift | nothing sent |

**What the app sends the Brain**, for Abram to map onto Apple's data types. These answers must match the App Store privacy page, and they are his to give:
- **An anonymous install token.** Random, with no device or advertising identifier.
- **Onboarding answers:**
  - where they're based (London / UK / abroad, with a town);
  - places, choices and feelings;
  - optional interests;
  - budget band.
- **Free-text answers.** For example, "the best hour of your last trip".
- **Plans and ratings.**
  - Ratings carry weather and travel minutes.
  - Plans hold each stop's prediction since m276 (server-side only).
- **Day questions:** "worth it" and "again".
- **Help & safety:** messages, plus an optional phone number or email, deleted once sorted (30 days at most).
- **Referral codes**, share-link opens, and app events (screens reached, times taken).
- **Trip searches:** dates, airports, the stay's location (never its name).

**Not decided here:**
- which Apple categories each item falls under;
- whether any is "linked to the user";
- the purposes.

The file is added when the answers are given (about 2 h, then one TestFlight build to check Apple's processing).

## SEC-05: confirm what Render passes (steps; needs the branch's check route on a non-production service)

The live Brain already answers through Cloudflare: the `server: cloudflare` and `cf-ray` headers were seen on 12 Nov. What isn't confirmed is which address header reaches the app.

1. Deploy the branch to a **separate** Render service, a free web service with its own database. Never production. This is Abram's step, about 30 min.
2. From a phone on mobile data, call `GET /v1/admin/client-address` with the admin token. The route answers with:
   - `cf_connecting_ip`;
   - `true_client_ip`;
   - the `x_forwarded_for` list;
   - `peer`;
   - whether `cf-ray` was present;
   - `counted_as`.
3. Call it again with forged headers: `CF-Connecting-IP: 203.0.113.9` and `X-Forwarded-For: 203.0.113.10`.
4. **Reading:**
   - If `cf_connecting_ip` is the phone's real address both times (Cloudflare overwrote the forgery), the fix is right.
   - If the forgery shows through, the Brain is not behind Cloudflare's header rewrite. In that case, use the right-most `X-Forwarded-For` entry added by Render instead (about 1 h) and repeat.
5. Delete the staging service afterwards.

## Hours

| Item | Who | Hours |
|---|---|---|
| Check the alert webhook in Render | Abram | 0.1 |
| The patch branch from `80a0da3`, checked | Claude | 3 |
| Review and decide on the patch | Abram | 0.5 |
| SEC-05 staging check | Abram (Claude writes the steps) | 0.5 |
| SEC-12 key and secrets | Abram | 0.5 |
| SEC-12 build changes | Claude | 3 |
| SEC-14 answers | Abram | 1 |
| SEC-14 file and check | Claude | 2 |
