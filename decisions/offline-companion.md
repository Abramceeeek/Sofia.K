# Offline companion: storage audit, design and a proof of concept (8 Nov 2026; m221; retention and backups revised 9 Nov, m226)

> **Revised by Abram's decision (m224): "trip information belongs to the traveller."** The 30-day deletion now applies only to disposable offline content, never to the person's trip. The iPhone backup exclusion proposed in m221 is **withdrawn**: the audit below shows it would have taken people's trips out of their backups. See "Retention and backups (m226)" at the end; it replaces section 5's deletion line and proposal 1.

**Decision:**
- **Designed, with a tested proof of concept in the Brain** (`brain/src/brain/offline.py`, `tests/test_offline.py`) that both apps can follow.
- **No app change yet,** so the frozen build and the screens are untouched.
- **Most of an offline mode already exists:** both phones keep the plan, the trips and unsent ratings, and Help & safety is bundled.
- **What's missing:** one view that puts what you need first, and says how fresh each part is.

## What the phones keep today (audit of the code, 8 Nov)

| What | iPhone | Android |
|---|---|---|
| The install token (a credential) | Keychain | `EncryptedSharedPreferences` (androidx security-crypto) |
| The plan, its request, the trips (each day's plan, the chosen flight and stay), the profile, unsent ratings, a hand-off in progress | JSON files in Application Support (`AppModel.cache`) | JSON files in `filesDir` (`Files`) |
| Small settings (onboarding step, reminders, ratings per plan, "Now" position) | UserDefaults | SharedPreferences |
| Help & safety (999, NHS 111, Samaritans 116 123) | in the app's code | in the app's code |
| Card photos | web images (Wikimedia Commons), not kept | the same |
| Backups | **not excluded** (no `isExcludedFromBackup` in the code) | **excluded:** `allowBackup="false"`, and `data_extraction_rules.xml` excludes every domain from cloud backup and device transfer |

**Already offline-safe:**
- ratings made with no signal are kept and sent later (journey audit);
- "Delete my data" with no signal deletes everything on the phone at once and finishes on the server later (m176);
- the plan and the trip days open without signal.

## What the platforms provide (official sources, read 7–8 Nov 2026)

**iPhone:**
- **Encryption of app files.** A file created with no protection level gets "Complete until first user authentication" (the default): "The file is inaccessible until the first time the user unlocks the device", and then it "remains accessible until the device shuts down or reboots". Apple's Platform Security guide: "This is the default class for all third-party app data not otherwise assigned to a Data Protection class".
  - Sources: developer.apple.com/documentation/uikit/encrypting-your-app-s-files (read through its JSON); support.apple.com/guide/security/data-protection-classes-secb010e978a.
- **Backups.**
  - The system "periodically purges" `tmp` and `Library/Caches`, so "iCloud Backup excludes them by default".
  - A file is kept out of backups with `isExcludedFromBackup`, which "exists only to provide guidance to the system… it's not a mechanism to guarantee those items never appear in a backup", and must be set again after each save.
  - Source: developer.apple.com/documentation/foundation/optimizing-your-app-s-data-for-icloud-backup.
  - **Whether Application Support is backed up isn't stated on that page: UNVERIFIED here.** Since nothing excludes it, assume it can be.
- **Keychain:** "Securely store small chunks of data on behalf of the user" (developer.apple.com/documentation/security/keychain-services). Whether items outlive the app isn't stated there: UNVERIFIED.

**Android:**
- **App storage.** Other apps "cannot access files stored within internal storage". It's encrypted since Android 10, and "When the user uninstalls your app, the files saved in app-specific storage are removed". The cache may be deleted when storage is low (developer.android.com/training/data-storage/app-specific).
- **Backups.** Auto Backup is on by default for apps targeting API 23+. It covers shared preferences, `filesDir` and databases, to "a private folder in the user's Google Drive account, limited to 25 MB per app". It's off here, by `allowBackup` and the extraction rules (developer.android.com/guide/topics/data/autobackup).
- **Encryption at rest.** "All devices launching with Android 10 and higher are required to use file-based encryption". App data sits in credential-encrypted storage, available only after the user unlocks (source.android.com/docs/security/features/encryption/file-based).
- **The token's library is deprecated.** androidx security-crypto 1.1.0-alpha07 (9 Apr 2025) and 1.1.0-beta01 (4 Jun 2025): "Deprecated all APIs in favour of existing platform APIs and direct use of Android Keystore" (developer.android.com/jetpack/androidx/releases/security). The Keystore keeps key material "non-exportable" (developer.android.com/privacy-and-security/keystore).

## The design

**1. What's kept, in Abram's order.** The pack is built **on the phone** from what the phone already has. Nothing new goes to the server and nothing is fetched to build it.

| # | Part | From | Status rules (the GUESS thresholds are constants in `offline.py`) |
|---|---|---|---|
| 1 | **The itinerary:** each day's stops and times, plus each stop's "book ahead" line | the trip's day plans | **past** before today. **Check** if planned more than 7 days before the day ("Planned on 1 Nov: travel times may have changed. Plan this day again when you have signal."). A card checked more than 90 days before the day says "check opening hours on the day". An unknown check date is listed as missing. |
| 2 | **The stay:** name, price in its own currency, provider, whether it's marked booked | the chosen stay | **expired** after the last night. **Check** if not marked booked, chosen for other dates, or a sample price. No saved address is listed as missing ("open the booking site when you have signal"). |
| 3 | **The journey:** flight, landing and leaving times, airports | the chosen flight | the same rules, plus always "Times can change: check with the airline on the day". |
| 4 | **Emergency help:** 999, NHS 111, Samaritans 116 123 | bundled in the app | always current. |

**2. Freshness.**
- Every item says where it came from ("your plan", "found on Booking.com", "bundled in the app") and when it was saved.
- Every item has a status (current, check, expired or past) and the one action to take when it isn't current.
- Nothing is refreshed silently. A refresh happens when the person opens it with signal, as today.

**3. Synchronisation and conflicts** (`merge_ratings`, `which_plan`):
- **Ratings.** One per stop. The later one wins, on either side: a rating made offline is never lost to an older one, and an old unsent one never undoes a later change.
- **Plans.** A newer plan from the server replaces the phone's, unless the phone still has unsent ratings for its plan. Those go first, because they belong to that plan's id.
- **Trips.** The trips live only on the phone, so the phone is the source of truth. The server never overwrites them.

**4. Missing data** is listed ("not saved: the address"), never filled in or guessed.

**5. Expired bookings.**
- After the trip's last day the stay and the journey read "expired". They are **marked**, never deleted.
- The trip itself, its days and its summary stay until the person deletes them (m226).
- Only disposable content (a stored copy of the pack, cached images) may go 30 days after the trip (GUESS).

**6. Deletion.** "Delete my data" removes everything on the phone at once, offline included (already built, m176). Uninstalling removes app files on Android (stated). On the iPhone the pages read don't say: UNVERIFIED, though deleting an app is expected to remove its container.

**7. Storage security.**
- The itinerary is ordinary app data, encrypted at rest by the platform: iPhone "until first unlock", Android credential-encrypted storage. That's enough for plans and choices.
- The token stays in the Keychain / Keystore.
- **No health, food or location data is kept for offline use** (m215; D123: location is never stored).

**8. Size.** Text only, budget 512 KB (a GUESS). The demo trip's six-day pack is about 4 KB. Photos aren't kept: they're web images, and caching them would mean copying third-party files onto the phone (credits and licences apply).

## The proof of concept (`brain/src/brain/offline.py`; `tests/test_offline.py`, 4 tests)

It runs on the apps' own demo trip (`app/Sources/Demo/demo_trip_days.json`). The tests check:
- **Order and freshness:** the itinerary comes first, the price stays in its own currency (367 EUR, never £), the flight's "check with the airline" line is there, and the emergency lines are the apps' own;
- **Stale, unbooked, wrong-dates, missing and sample items** are each said, never filled in;
- **After the trip:** bookings marked expired, the trip and its summary kept a year on, and only a stored copy of the pack disposable (m226);
- **Only disposable content can expire:** the storage classes in `offline.STORAGE`, tested (m226);
- **Offline ratings** are never lost, the later rating wins, and the rule for which plan to keep holds.

## Found, and proposed (not built: each is an app change for after the round)

1. ~~**iPhone: exclude the app's files from backups.**~~ **Withdrawn (m224, m226):** every file it would have excluded is the traveller's own data (below).
2. **Android: move the token off the deprecated library.** **Built (m227):** an AES-256-GCM Keystore key seals the token in `noBackupFilesDir/tokens`; the old store is read once, the copy checked, then removed; any failure keeps the old copy, so nobody is signed out. 7 tests (`TokenStoreTest`).
3. **"Offline" view on "Now":** the pack's four parts, with statuses and actions, shown when there's no signal. **Built on the branch (m228), both apps** (`app/Sources/Offline.swift`, `android/.../Offline.kt`):
   - **What it shows, in Abram's order:** today's itinerary, where you're staying, the journey, emergency help. Each card has its source, the day it was saved, a status chip (Saved, Check, Expired or Past; amber only for Check), the one thing to do, and "Not saved: …" for anything missing.
   - **Where:** "Saved on this phone" on "Now" is always there. With no network path, a banner at the top says "No signal. Your day, stay and journey are saved on this phone. Nothing shown is live." and opens it.
   - **Built on the phone** from the plan and the trip it already keeps; nothing is fetched. The rules are the Brain's reference; the app shows today only, not every day of the trip.
   - **Online and offline:** the phones' network monitors (`NWPathMonitor`, `ConnectivityManager`) only switch the banner and the heading. Neither state claims anything is live. Tested on Android (`OfflinePackTest`, 4 tests); the iPhone draws `nowoffline` and `offlinesaved` in CI.
   - **Differences from the reference, on purpose:** the stay says "The address isn't saved on this phone" as a line, and a booked stay points to the provider's confirmation; the emergency lines are Help & safety's own words.
4. **Photos offline** stay out until licensing is checked.

**Hours:** Claude ~3 h (audit, sources, design, proof of concept). Abram: decide the 30-day deletion and whether to build items 1–3 after the round.

## Retention and backups (m226, 9 Nov 2026)

### What each phone keeps, by class (audit of the code)

Both apps write the same six files and the same small settings. `offline.STORAGE` holds this table in code, and a test checks that only disposable classes can expire.

| Class | What | iPhone | Android | Retention |
|---|---|---|---|---|
| **User data** | `trips.json` (trips, chosen flight and stay, own time, each day's plan), `plan.json`, `request.json`, `profile.json`, `pending_ratings.json` (unsent ratings), `handoff.json` (a booking in progress) | Application Support | `filesDir` | **Until the person deletes it** (a trip, or "Delete my data"). Never on a timer. `pending_ratings` empties as the Brain receives each rating; `handoff` empties once answered |
| **User settings** | the onboarding step, reminders, ratings per plan, day feedback, where you are in a day, appearance | UserDefaults | SharedPreferences | the same |
| **History** | a trip after its last day | inside `trips.json` | the same | **Kept.** Bookings are marked "expired"; the summary (city, dates, days, places, stay, flight) stays available (`offline.summary`) |
| **Derived** | the offline pack | not stored: built from `trips.json` when needed | the same | If a later version stores a copy, it goes in Caches / `cacheDir` and **may be discarded 30 days after the trip** (GUESS). It can always be built again while the trip exists |
| **Cache** | card photos (web images), share-card images | the system's URL cache (Caches) | `cacheDir/share` | The system may clear it; never backed up; removed when no longer needed |
| **Credential** | the install token, and a pending-deletion token | Keychain, `kSecAttrAccessibleAfterFirstUnlock` | `EncryptedSharedPreferences` today; **Android Keystore-encrypted** after the migration (m227) | Kept until "Delete my data" or a fresh install |

### The iPhone backup audit

- **Apple's rules** (developer.apple.com, read through the documentation JSON on 9 Nov 2026):
  - `tmp` and `Library/Caches` are purged by the system, so "iCloud Backup excludes them by default", and Apple says not to use them "to exclude nonpurgeable data". It defines nonpurgeable data as "data the user creates, or data the app requires to function as the user expects".
  - `isExcludedFromBackup` "exists only to provide guidance to the system… it's not a mechanism to guarantee those items never appear in a backup or on a restored device".
  - Keychain items with `kSecAttrAccessibleAfterFirstUnlock` "migrate to a new device when using encrypted backups". A `ThisDeviceOnly` item "can be restored to the same device that created a backup" but "isn't migrated when restoring another device's backup data".
- **What a blanket exclusion of Application Support would have removed:** all six files above, every one of them user data. Nothing in Application Support today is disposable.
- **So: no exclusion.** Disposable content goes to Caches, which Apple already leaves out, and that is where any future stored pack or image cache goes.
- **Restoring an encrypted backup on a new iPhone** brings back the trips, the settings and the token together. The person continues as before, which is what "trips belong to the traveller" asks for. It doesn't conflict with decision 2: "a reinstall starts afresh" is detected on the same phone by the missing `installMarker` after the app is deleted, and a restore brings the marker back.
- **Restoring without the token** (a backup that doesn't carry Keychain items to a new device) shows the welcome screen. The trips stay on the phone and reappear after the person agrees again and reopens the app. They're never deleted. It's a rough edge worth smoothing: show "Your trips are here" after re-joining (~1 h, after the round).
- **Keep the Keychain class as it is.** `ThisDeviceOnly` would restore trips to a new phone without the token that goes with them.

### Android: the recommendation for parity

Today Android backs up nothing: `allowBackup="false"`, and every domain is excluded from cloud backup and device transfer. With no cloud sync of trips, **a new phone or a reinstall loses the traveller's trips.** The iPhone keeps them. The options:

| Option | What it does | Problems |
|---|---|---|
| A. **"Export my trips" and "Import"** (a file the person keeps, both apps) | The person moves their own trips, offline, with no Google or Apple account involved | They have to remember to do it |
| B. Turn Auto Backup on for user-data files only | Trips come back on a new Android phone | Android Keystore keys don't travel, so the token can't be read on the new phone: a new install, and the person's learned model on the server isn't linked. Auto Backup also restores on a reinstall, which conflicts with decision 2 unless that's revisited. It goes to the person's Google Drive (25 MB) |
| C. Sync trips with an account | Trips everywhere | Accounts wait for after Test B (after-9-Nov) |

**Recommendation:**
- **A first** (~3 h, both apps, after the round): no change to what's backed up, the person in control, and it works on both platforms the same way.
- **Keep Android's `allowBackup="false"` until C.**
- **Revisit B only together with decision 2.**

Until then the asymmetry is stated, not hidden: the privacy notice and the trip screen can say "Trips are kept on this phone. On Android, export them before changing phones."

### Decisions after the review (m234)

- **Android "Export and import my trips": approved for after the friends' round.** The export holds trips, personal plans and selected bookings (the choices the person marked). **Never** the install token or any credential, food preferences or API secrets. It's a file the person saves and moves themselves, until accounts sync trips.
- **Emergency help is UK-specific today** (999, NHS 111, Samaritans 116 123), and is labelled that way in the app. **The pack will carry each destination's own emergency numbers,** from that country's official sources and with the date they were checked. The model for that is `destinations.emergency` (m236).

### Retention, in one line each

- **The traveller's trips, plans, ratings, answers and settings:** kept until they delete them.
- **Past trips:** kept, bookings marked expired.
- **Offline copies and images:** disposable, 30 days after the trip at the latest (GUESS).
- **The token:** kept until "Delete my data" or a fresh install.
