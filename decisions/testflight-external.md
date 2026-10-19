# External TestFlight and the gates before strangers (roadmap Stage 1, steps 7 and 8)

**Decision first:** everything Apple asks for an external TestFlight group is below, ready to paste (~30 min for Abram in App Store Connect). The first external build goes to Beta App Review. **No external build goes out before the Apple check (gate 4)**, and strangers wait for every gate in section 5.

Sources (read 19 Oct 2026): Apple's [Provide test information](https://developer.apple.com/help/app-store-connect/test-a-beta-version/provide-test-information) (the Beta App Description is required; feedback email), [App Review information](https://developer.apple.com/help/app-store-connect/reference/app-review-information) (notes up to 4,000 bytes; phone in +44 format; sign-in only if the app needs a login), [App privacy details](https://developer.apple.com/app-store/app-privacy-details/) (definitions below). Character limits for the description and "What to Test" are not stated on Apple's pages: UNVERIFIED, so each text below is kept well under 4,000 characters.

## 1. Test Information (App Store Connect → TestFlight → Test Information)

**Beta App Description** (required):

> ODYS plans a day out in London around how you like to feel, not around famous sights. This is an early test run by one person, Abram, in London. You answer a few quick questions (some London places you've been to, and a few "this or that" days), then compare two plans for a Saturday and pick the one you'd rather do. On the day, you rate each stop from 1 to 5 with one tap; those ratings are what we're testing. It takes about 10 minutes to start. There's no login, nothing to buy, and Help & safety reaches a person.

**Feedback Email:** `abram@abdurakhmonbek.com` (the contact in the privacy notice).

**Marketing URL:** leave empty.

**Privacy Policy URL:** `https://moments-brain.onrender.com/privacy`

## 2. Beta App Review Information

- **Contact:** Abram's name, email and phone, typed in App Store Connect (phone as `+44…`). Never in this repository.
- **Sign-in required:** No. The app has no accounts; it makes a random code on first launch.
- **Review notes** (paste):

> No login is needed. Tap through the welcome and consent screens, answer the short questions (any answers work), then compare "Plan 1" and "Plan 2" and pick one; that becomes your day. Optional tester code on the first screen: leave it empty.
> The server is in Frankfurt; its first answer can take a moment. Location is asked only on the "Now" screen and is optional. The app takes no payments: flight and hotel results link out to the provider's own site (Skyscanner, Booking.com and others). Help & safety sends a message to a person, and tells the user to call 999 in an emergency. No AI service receives the user's answers. Delete my data (Your data) removes everything held on the server straight away.

## 3. What to Test (for each build)

> Thank you for testing ODYS.
> 1. Answer the questions and pick between Plan 1 and Plan 2. Did the one you picked feel like you?
> 2. Go on the day if you can. After each stop, rate it 1–5 (a reminder can do this for you). That's the most useful thing you can give us.
> 3. Anything wrong, confusing or slow: screenshot it in TestFlight, or email abram@abdurakhmonbek.com.
> New in this build: the plan shows the Met Office forecast, and Tube and bus legs name the real lines (TfL).

## 4. App Privacy answers (needed for the App Store, not for TestFlight)

Apple's page says these are "required to submit new apps and app updates to the App Store"; it doesn't mention TestFlight, so they wait for Stage 3. Drafted now so the notice and the labels agree. **"Collect"** = sent off the phone and kept longer than needed to answer the request; data processed only on the phone, or sent and immediately discarded, is not collected (Apple's definition, quoted on the page above).

| Apple's data type | Collected? | Why | Linked to the user? | Tracking? |
|---|---|---|---|---|
| User ID | Yes | The random install code (stored as a hash) ties answers, plans and ratings together | Yes | No |
| Product Interaction | Yes | App events (finished the questions, asked for another plan, shared a moment) | Yes | No |
| Other User Content | Yes | The answers, the best-hour text, the "why" for a plan, the 1–5 ratings | Yes | No |
| Customer Support | Yes | Help & safety messages and the replies | Yes | No |
| Phone Number / Email Address | Yes, only if left in Help & safety | To reply; deleted when sorted, 30 days at most | Yes | No |
| Coarse Location | Probably **No** | "Start from where I am" sends a point rounded to ~100 m, used for that plan and not kept. A trip's stay location is the stay's, not the person's. GUESS: confirm against Apple's wording when filling the form | — | — |
| Precise Location | No | Processed only on the phone (D123) | — | — |
| Crash Data / Performance Data | No | The app has no crash or analytics SDK; Apple's own TestFlight crash reports are Apple's | — | — |

**Purposes:** App Functionality and Analytics (testing whether the plans work). Never Third-Party Advertising, Developer's Advertising or Marketing, or tracking.

## 5. The gates before strangers (step 8)

From CLAUDE.md and `validation/recruit-now.md`. Each is Abram's unless marked.

| # | Gate | Status (19 Oct) | Abram's time |
|---|---|---|---|
| 1 | **Paid server and database** in Render, before the free database expires ~27 Oct (upgrade in place keeps the data) | **Not done: urgent** | ~15 min, $7 + $6 a month |
| 2 | `BRAIN_ALERT_WEBHOOK_URL` set, and one test safety message seen on both phones (yours and the helper's) | Not confirmed | ~15 min |
| 3 | The backup helper signs **Part A** before joining the alerts channel (D38, D55) | Not done | ~30 min with the helper |
| 4 | **Apple check:** outside-activities policy and the IP clause (D60, D94) | Open since 28 Sep | ~30 min |
| 5 | **ICO fee re-check** before strangers; pay £52 if required (D108) | Re-check due | ~10 min |
| 6 | Privacy notice reviewed (`/privacy`; updated 19 Oct for backups, logs, TfL and the Met Office) | Draft | ~15 min |
| 7 | Backup set up and one backup opened on your computer (`brain/README.md`, Stage 1) | Not done | ~15 min |
| 8 | `/v1/health` shows `"travel": "tfl"` and `"weather": "met_office"` after the deploy (Claude checks) | Claude, after the deploy | — |
| 9 | Live flight and hotel keys (Duffel live, LiteAPI production), or keep the labelled test results for the friends' round | Optional for friends | ~1.5 h (accounts, card) |

**Friends** (also external TestFlight) need gates 1, 2 and 4, since the Apple check comes before any external build (D60, D94), and gate 3 before the helper sees any of their messages. **Strangers** wait for all of 1–7.
