# Offline companion: storage audit, design and a proof of concept (8 Nov 2026; m221)

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
- After the trip's last day the stay and the journey read "expired".
- 30 days after (a GUESS, for Abram), the trip's offline copy is deleted from the phone.

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
- **After the trip:** expired, then deleted after 30 days;
- **Offline ratings** are never lost, the later rating wins, and the rule for which plan to keep holds.

## Found, and proposed (not built: each is an app change for after the round)

1. **iPhone: exclude the app's files from backups** (`isExcludedFromBackup`, set on each save), to match Android and decision 2 ("a reinstall starts afresh"). Today an iCloud restore could bring back the plan, trips and profile. ~0.5 h, both apps' behaviour then matches.
2. **Android: move the token off the deprecated library.** Use an AES key in the Android Keystore to encrypt the token, migrating the existing one on first launch. ~2 h with tests. It isn't urgent (the library still works), but it shouldn't be left as is: Google has deprecated it.
3. **"Offline" view on "Now":** the pack's four parts, with statuses and actions, shown when there's no signal. ~6 h, both apps, after Abram sees the design.
4. **Photos offline** stay out until licensing is checked.

**Hours:** Claude ~3 h (audit, sources, design, proof of concept). Abram: decide the 30-day deletion and whether to build items 1–3 after the round.
