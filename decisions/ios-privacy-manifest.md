# The iPhone privacy manifest: every declaration, and which ones need Abram (19 Nov 2026)

Abram's decision of 19 Nov, §6: prepare the exact declarations Apple requires; for each, say which API, where, why, which declaration, and whether it is documented elsewhere. **No privacy answer is invented here.** Where the answer is a judgement about ODYS's data, the choice is laid out for Abram, with the facts from the code. The manifest file (`PrivacyInfo.xcprivacy`) is added to the app only after his answers. It is needed **before public App Store release**.

**Sources** (Apple's documentation, read 19 Nov 2026 from its JSON source at developer.apple.com/tutorials/data/documentation/bundleresources/…, the same content as the pages):
- `privacy-manifest-files`;
- `describing-use-of-required-reason-api`, and its key page `…/nsprivacyaccessedapitypes/nsprivacyaccessedapitype`;
- `describing-data-use-in-privacy-manifests`, and its key pages `…/nsprivacycollecteddatatype` and `…/nsprivacycollecteddatatypepurposes`;
- the App Store page "App privacy details" (developer.apple.com/app-store/app-privacy-details/, read in full).

**Apple, in short:**
- **The file and its rule:** the file is `PrivacyInfo.xcprivacy`. Since 1 May 2024, apps that don't describe their use of required-reason APIs "aren't accepted by App Store Connect".
- **What "collect" means:** data is collected when it is sent off the phone and kept longer than it takes to serve the request. Data processed only on the phone is not collected.
- **What "linked" means:** "Personal Data" under privacy laws counts as linked to the user.

**The code it was checked against** (19 Nov, `app/Sources`, 26 Swift files):
- `project.yml`;
- no Swift packages, so there are no third-party SDKs bringing manifests of their own;
- no App Groups.

## Part 1: required-reason APIs (`NSPrivacyAccessedAPITypes`)

| Apple's category | Used? | Where | Why ODYS uses it | Declaration Apple requires | Documented elsewhere | Abram's input |
|---|---|---|---|---|---|---|
| `NSPrivacyAccessedAPICategoryUserDefaults` (the `UserDefaults` API) | **Yes**, 84 uses | `AppModel.swift` (59), `Location.swift` (8), `FirstRunViews.swift` (7), `TripLogic.swift` (5), `TripViews.swift` (3), `BrainClient.swift` (1), `PlanViews.swift` (1) | The app's own settings and progress on this phone. Keys:<br>• display: `alwaysDark`, `planLayout`, `sky`;<br>• progress: `onboardingDone`, `onboardingStep`, `surveyDone`, `pairDone`, `morePlacesDone`, `moreTasksDone`;<br>• flags: `locationAsked`, `locationOn`, `reminderAsked`, `remindersOn`, `safetySeen`, `safetySent`, `ratedOnce`;<br>• per-plan state: `ratings.<plan>`, `arrived.<plan>`, `nowIndex.<plan>`, `dayFeedback.<plan>`;<br>• codes: `testerCode`, `refCode.joined`, `testBPlanId`, `installMarker`;<br>• other: `founderVideo`, `improved`, `screen`, `demo` | Reason **`CA92.1`**: "Declare this reason to access user defaults to read and write information that is only accessible to the app itself." The others don't fit:<br>• `1C8F.1` is for App Groups (none);<br>• `C56D.1` is for third-party SDKs only;<br>• `AC6B.1` is for MDM configuration | the privacy notice: "Your plan is saved on this phone" | **None:** the facts decide it. Abram confirms it on review |
| `NSPrivacyAccessedAPICategoryFileTimestamp` | **No** | — (none of `creationDate`, `modificationDate`, `contentModificationDateKey`, `getattrlist`, `stat` and the rest; files are read and written, never their dates) | — | nothing | — | none |
| `NSPrivacyAccessedAPICategorySystemBootTime` | **No** | — (no `systemUptime`, no `mach_absolute_time`) | — | nothing | — | none |
| `NSPrivacyAccessedAPICategoryDiskSpace` | **No** | — (no volume capacity keys, no `statfs`) | — | nothing | — | none |
| `NSPrivacyAccessedAPICategoryActiveKeyboards` | **No** | — (no `activeInputModes`) | — | nothing | — | none |

## Part 2: tracking (`NSPrivacyTracking`, `NSPrivacyTrackingDomains`)

**Facts:**
- no advertising SDK;
- no advertising identifier;
- no App Tracking Transparency prompt;
- no tracking domains in the code.

**Proposed:**
- `NSPrivacyTracking` = **false**;
- `NSPrivacyTrackingDomains` = none.

**Abram confirms** that ODYS shares no data for advertising or with data brokers. That is a business fact, not something code can show.

## Part 3: data the app collects (`NSPrivacyCollectedDataTypes`)

**Common to every row:**
- **Tracking:** no (Part 2).
- **Linked:** each row is stored against the install's id, which Apple's page treats as personal data and so linked. **Abram decides "linked"**, and it should match the App Store answers.
- **Purposes:** Apple's identifiers are `…PurposeAppFunctionality`, `…ProductPersonalization`, `…Analytics`, `…DeveloperAdvertising`, `…ThirdPartyAdvertising` and `…Other`.

| What the app sends and the Brain keeps | Where | Candidate Apple type(s) | Purposes it serves (facts) | Documented elsewhere | **Abram decides** |
|---|---|---|---|---|---|
| A random install id, made by the Brain; the phone keeps the token in the Keychain | `POST /v1/installs`; every request | `…UserID` ("assigned user ID") or `…DeviceID` ("other device-level ID") | App functionality (it knows the person's answers and plans) | privacy notice: "a random code" | **which type:** it's per install, kept "this device only" (SEC-15), assigned by ODYS |
| Where they're based (London / UK / abroad) and the town or city they type | onboarding | `…CoarseLocation`, or `…OtherDataTypes` | App functionality (visitors' cohort, D116), Analytics (Test B excludes visitors) | privacy notice | whether a typed town is "location" |
| Place reactions, this-or-that choices, feelings, interests, company, activity level | onboarding, "Improve future plans" | `…OtherUsageData` or `…OtherDataTypes` (tastes stated by the person) | Product personalization, Analytics (Tests A–B) | privacy notice | which type |
| Budget band for a day | onboarding, plans | `…OtherFinancialInfo` ("any other financial information"), or not financial (a spending choice, not income) | Product personalization | privacy notice ("budget per trip/day — not income") | **whether it counts as financial info** |
| Free-text answers ("the best hour of your last trip") | onboarding | `…OtherUserContent` | Product personalization | privacy notice | confirm |
| Plans, ratings, "would bring someone", the day's "worth it" and "again", corrections | plans, rating sheet, day end | `…ProductInteraction` and/or `…OtherUsageData` | App functionality, Product personalization, Analytics | privacy notice | which type(s) |
| App events: screens reached, time taken | `POST /v1/me/events` | `…ProductInteraction` | Analytics (Test A's completion and time) | privacy notice | confirm |
| Help & safety message | `POST /v1/me/safety` | `…CustomerSupport` ("data generated by the user during a customer support request") | App functionality (a person replies) | privacy notice | confirm |
| An optional phone number or email left with that message, deleted once sorted, 30 days at most | `POST /v1/me/safety` | `…PhoneNumber`, `…EmailAddress` | App functionality (the reply only) | privacy notice | **whether Apple's optional-disclosure rule applies.** It needs all four of Apple's criteria. Optional, user-entered each time and infrequent are met; not core to the app is arguable |
| **"Start from where I am": one point, rounded to 3 decimal places** | `POST /v1/me/plans` | **`…PreciseLocation`**: Apple's line is "three or more decimal places", and 3 is on it | App functionality (that day's plan) | privacy notice: "isn't kept" | **Today the live Brain keeps it** in the plan row (SEC-06), so by Apple's definition it is collected. With Patch A2 (`production-privacy-patch.md`) it is used once and not kept, so not collected. **Decide after A2, or round to 2 places instead (about 1 km).** That would be an app change (Category B) |
| The chosen stay's location (never its name) in a trip's plans | `POST /v1/me/trips/days` | possibly `…PreciseLocation` (where the person will sleep), or not location (a hotel's address) | App functionality | privacy notice: "its location, never its name" | **whether a stay's point is the person's location** |
| Referral code joined, share-link opens | share card | `…ProductInteraction` | Analytics (Test C's K) | privacy notice | confirm |
| **Not collected:** speech (turned into text on the phone; only the text is sent, as typed); photos (none); contacts (none); health (none); crash or performance data (no reporter in the app); flight and stay searches (not stored against the person) | — | — | — | the notice and the permission prompts | none |

## What happens after Abram's answers (Claude, about 2 h)

1. Write `app/Sources/PrivacyInfo.xcprivacy` with Part 1 (`UserDefaults`, `CA92.1`), Part 2 (false, none), and Part 3 exactly as answered.
2. Add it to the app target in `project.yml`.
3. One TestFlight build on `main` (after the round), and check Apple's processing for "ITMS-91053" warnings.
4. **The App Store privacy answers must say the same as the file:** Abram enters them in App Store Connect.

## Abram's answers needed (one list)

1. The install id: User ID or Device ID.
2. A typed town or city: location or not.
3. The budget band: financial info or not.
4. Phone and email in Help & safety: disclosed, or optional under Apple's rule.
5. "Start from where I am": decide after Patch A2, or round to 2 places.
6. A stay's point: location or not.
7. "Linked to the user": yes for all (the recommended reading), or not.
8. Purposes for each row (the column above lists what each serves).
9. Confirm no data is shared for advertising or with data brokers.
