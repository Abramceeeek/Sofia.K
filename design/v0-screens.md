# v0 screens: design brief (D50, D81)

**What the app does:** it plans a day out around how a specific person wants to *feel*, not around famous sights. The unit is a **moment**: a specific experience at a place and time, often including how you arrive. One example is walking out of South Kensington tube and seeing the Natural History Museum open up in front of you.

**Who designs (D81):** Abram, in Claude Design, **after Test B reports** (about 2 Nov). An outside designer is optional. If one is brought in, they sign Part A (`legal/contributor-deed-part-a.md`) before their work is used.

## Design scope (D81): four custom screens, everything else native

| Custom screen | The one thing it must get right | Build | Your design hours (GUESS) |
|---|---|---|---|
| **Welcome** (1) | A person, not a brand: your photo, the one line, and "a person runs this test" visible without scrolling | 1 | 1.5 |
| **Moment card** (15) | **The arrival is the hero.** Show "from → path → the reveal" as one vertical line before the photo gallery, because the approach *is* the moment | 2 | 1.5 |
| **Shot card** (16) | Read in one glance while standing on the spot: a mini map pin, a facing arrow (compass bearing), what to frame, when | 2 | 1.5 |
| **Day plan** (14) | The map and the timeline are one object: the same line colour links the numbered pins and the stop list, and travel legs are labelled segments ("12 min walk") | 2 | 1.5 |
| Type, colour and hand-off | One shared style for the four screens; frames at 393 × 852 pt, light and dark | 1–2 | 1.0 |
| **Total** | | | **7.0** |

**Everything else uses native SwiftUI:** onboarding (screens 2–10), plans home, trip intent, A vs B, rating, notification prompt, settings, help & safety, bring a friend and states.
- That means `Form`, `List`, `NavigationStack`, sheets, `Toggle`, `Picker`, the system share sheet and MapKit, with SF Pro and SF Symbols.
- No custom styling beyond the accent colour.

**A starting direction for the four screens** (a brief for your Claude Design sessions, from the frontend-design skill; yours to change):
- **Tone:** a well-thumbed field guide rather than a travel brochure. It should feel calm, warm and sure of itself.
- **Type:** SF Pro everywhere, plus **one display face for moment titles only**. It must be open-licence and bundled with the app, so check the licence before choosing.
- **Colour:** warm neutrals, with the photos carrying the colour. **One accent**, used only for the route line, the pins and the "now" state, in both light and dark.
- **Motion:** one moment only. The moment card's photo opens as the approach line completes (the reveal). Honour Reduce Motion.
- **Avoid:** gradients, glassy cards everywhere, emoji, and anything that makes a stop look like an ad.

## Ground rules

- **Platform:** iPhone only, portrait, iOS 17+, English. Design **light and dark**.
- **Use system parts wherever possible:** SF Pro, SF Symbols, `List`, `NavigationStack`, sheets, the system share sheet, and MapKit. Every custom component costs build hours; the whole app has about 31 hours.
- **Accessibility:** support Dynamic Type, 44 pt tap targets, and a VoiceOver label on every control. Swipes always have button equivalents.
- **Tone:** a well-travelled friend. Short, plain and warm. No emoji.
- **Copy:** use the real copy, which is already written (`brain/data/onboarding.yaml`, `validation/interview-script.md`). Please don't design with lorem ipsum.
- **Images:** only Abram's own photos, or Wikimedia Commons files with a credit line.
- **No dark patterns.** "Not now" and "No" get the same weight as "Yes" on every permission and on the AI toggle.
- **Honesty is visible.** Say that a real person runs this test and that AI helps draft summaries and plans. Never imply a person replied when it was the app.
- **Time limits:** no visible timers and no time limits anywhere in onboarding. A section progress indicator is fine.

**Build 1** = the first external TestFlight build, about the week of 30 Nov: onboarding, safety and settings. **Build 2** = plans and real use, about mid-December. The Phase 3 tests run by hand before either (D63), so the screens should reflect what those tests teach.

## A. First run

| # | Screen | Build | What's on it |
|---|---|---|---|
| 1 | **Welcome** | 1 | Abram's photo and one line: "We wanted to bring some of the best experiences we've had to you, so you can have them too." What this is: a research test run by a person. An optional **tester code** field (from the sign-up form, e.g. `S-fbucl-07`). "Get started" |
| 2 | **Consent** | 1 | A plain-English summary: what is stored, why, for how long, and how to delete it. An 18+ checkbox. The required "I agree to take part". **A separate, optional toggle, off by default:** "Let an AI service read my typed answers to help write my summary and plans" (App Review 5.1.2(i)). A link to the full privacy notice |

## B. Onboarding

| # | Screen | Build | What's on it |
|---|---|---|---|
| 3 | **Best hour** | 1 | "Tell me about the best hour of your last trip or day out. Where were you, what was happening, how did it feel?" A large text field, with a hint: "Tap the mic on your keyboard to speak instead." After the first answer: "Is there anything else you'd like to add about that?" Skip is allowed |
| 4 | **Why you go out** | 1 | "Which of these is most often why you go out or travel? Pick up to two." Six chips: switch off and rest · time with people · discover something new · nature and outdoors · culture and history · food |
| 5 | **Places you've been** | 1 | 16 cards, one at a time: a photo, the name and a one-line moment. Four reactions: **Loved it · It was fine · Didn't enjoy it · Haven't been**, as buttons that swipes also trigger. A counter ("4 of 16"). After the first "Loved it" and the first "Didn't enjoy it", one optional line: "What made it that way?" |
| 6 | **This or that** | 1 | 10 tasks. Two made-up day plans, A and B, each with six attributes **in the same order with the same icons**: longest transfer, weather at the outdoor stops (mild and dry / cold but dry / rainy, D95), pace, crowds, cost per person, walking. Tap one to choose. A counter ("3 of 10") |
| 7 | **A bit about you** | 1 | All optional, with "Skip all": budget per day out (4 bands), who you go with, morning or night person, how active, where you grew up (a note on why it's asked), and "Any foods or drinks you avoid?" (a note: only used to choose food stops). **No nationality, income, health or allergy questions** |
| 8 | **Photos** | 1 | "How much do photos and sharing matter on your trips?" 1–5. Then an **example shot card** inline (screen 16), with "Would a card like this make you more likely to go?" 1–5 |
| 9 | **Here's what we heard** (read-back) | 1 | 3–6 plain lines from the model, such as "Long transfers put you off" or "You love a reveal". Each has **Right / Not quite**. Where the model is unsure, it says "Not sure yet about crowds". A friendly persona label on top, then "Anything to fix or add?" |
| 10 | **Quick survey, then done** | 1 | "I felt understood" 1–5; "It felt like talking to a person, not filling in a form" 1–5; "Did you type or speak your answers?" (typed / spoke / both); "Was anything intrusive or tedious?" Finish: "Your two plans arrive within a day or two." |

## C. Plans and the day out

| # | Screen | Build | What's on it |
|---|---|---|---|
| 11 | **Plans home** | 2 | An empty state ("Your plans will appear here"). A card for a new pair: "Two plans for your day. Which would you rather do?" The list of plans. A **"Plan another day"** button: tapping it is a Test C measure |
| 12 | **Trip intent** | 2 | Three short questions before a plan: recharge or explore? who might come? anything you'd want in it for sure? |
| 13 | **Plan A vs Plan B** | 2 | Two plans in **identical format**: times, stops and a walking and transfer summary. Each opens to screen 14. Then "Which would you rather do?" A or B, "This plan fits me" 1–5 for each, and "Why?" |
| 14 | **Day plan** | 2 | Date and times, plus a weather line if known. **A map with numbered pins** above the list of stops. Each row shows the time, the title, the travel time from the previous stop ("12 min walk") and one line on why it's there ("Chosen for: the reveal, the views"). The best stop is subtly marked. **Directions** on each stop opens Apple Maps. **Bring a friend** |
| 15 | **Moment card** | 2 | A photo, the title and **how to arrive**: from where, which exit, the path, step-free or not. Then what happens, the best time (light, when it's quiet) and the cost. A shot card button if there is one. **"Done here"** opens the rating |
| 16 | **Shot card** | 1 (example) / 2 | Where to stand (a mini map pin and a note), which way to face (a compass bearing), what to frame, when, and what spoils it. An example photo. After the moment: "Got a shot you like? Share it. Here's a link friends can use to try this." **We never ask for the photo** |
| 17 | **Rating** | 2 | One tap, 1–5: "How did that feel?" An optional "Would you bring someone here?" (yes / no). The same prompt as a **notification** after each stop, with 1–5 actions. At the end of the day: "Would you go again?" and "How did it feel?" |
| 18 | **Before the notification permission** | 2 | "We'll ask for one tap after each stop. That's it." **Allow** and **Not now** carry equal weight. Everything still works without notifications, because rating in the app is always possible |

## D. Help, safety and your data

| # | Screen | Build | What's on it |
|---|---|---|---|
| 19 | **Help & safety** | 1 | A prominent **"I feel unsafe / something's wrong"** button. It leads to a confirmation screen: "If you or someone else is in danger or hurt, **call 999 now**. We've told a person on our team, and they will reply within a few hours." There's an optional message field. "Something else?" shows an email address as text. **Never promise a faster reply** |
| 20 | **Settings: your data** | 1 | What we store, as a plain list. The AI permission toggle, which can be changed. **Delete my data**, with an in-page confirmation, because it can't be undone. The privacy notice. "About this test": a person runs it and AI helps draft. The version number |
| 21 | **Bring a friend** | 2 | A button and one line. The system share sheet carries the text and a link with a referral code |
| 22 | **States** | 1–2 | Loading, empty and errors. Example error: "Couldn't reach us. Your plan is saved on this phone." There is no offline mode beyond the current plan |

## Also needed

- **App icon** (1024 px) and a working name. Abram decides the name.
- **A small component sheet:** primary and secondary buttons, a chip, the 1–5 scale, the four reaction buttons, a plan card, a stop row, a map pin (numbered, with a highlighted variant), an attribute row with icon for "this or that", and a toggle row with a note.
- **Hand-off:** frames at iPhone 15/16 size (393 × 852 pt), light and dark, with notes on spacing and states.

## Please don't design (cut from v0)

Login or sign-up, a paywall or payments, an AI support chat, a social feed or profiles, widgets, Live Activities, Watch, iPad, landscape, in-app turn-by-turn routing, or a custom voice recorder (the keyboard mic covers voice in v0).

## Timing (D81)

- **After Test B reports** (about 2 Nov), and after Checkpoint 3 (9 Nov) so its lessons go in.
- **Welcome, plus type and colour** (2.5 h): the week of 16 Nov, before Build 1 (about 30 Nov).
- **Moment card, shot card, day plan** (4.5 h): the weeks of 23–30 Nov, before Claude builds them for Build 2 (mid-December).
- Native screens need no design pass. Claude builds them from this list.
- **Plan behind this:** `decisions/v0-ios-plan.md`.
