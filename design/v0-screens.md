# v0 screens: design brief (D50, D81)

**What the app does:** it plans a day out around how a specific person wants to *feel*, not around famous sights. The unit is a **moment**: a specific experience at a place and time, often including how you arrive. One example is walking out of South Kensington tube and seeing the Natural History Museum open up in front of you.

**Who designs (D107, lean mode):** Claude builds **every screen native-first now**, in parallel with the tests: native SwiftUI with one accent colour. Abram reviews one screenshot page per batch. **His own design pass on the four custom screens (D81) is optional, after Test B reports** (about 23 Oct), as a restyle. An outside designer is optional too. If one is brought in, they sign Part A (`legal/contributor-deed-part-a.md`) before their work is used.

## Design scope (D81): four custom screens, everything else native

| Custom screen | The one thing it must get right | Build | Your design hours (GUESS) |
|---|---|---|---|
| **Welcome** (1) | A person, not a brand: your photo, the one line, and "a person runs this test" visible without scrolling | 1 | 1.5 |
| **Moment card** (9) | **The arrival is the hero.** Show "from → path → the reveal" as one vertical line before the photo gallery, because the approach *is* the moment | 2 | 1.5 |
| **Shot card** (opens from 9; example on 13) | Read in one glance while standing on the spot: a mini map pin, a facing arrow (compass bearing), what to frame, when | 2 | 1.5 |
| **Day plan** (8) | The map and the timeline are one object: the same line colour links the numbered pins and the stop list, and travel legs are labelled segments ("12 min walk") | 2 | 1.5 |
| Type, colour and hand-off | One shared style for the four screens; frames at 393 × 852 pt, light and dark | 1–2 | 1.0 |
| **Total** | | | **7.0** |

**Everything else uses native SwiftUI:** consent and onboarding (screens 2–7), rating (10), improve my plans (11–13), help & safety (14), your data (15), and Build 2's screens (16–23).
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

**Build 1 and Build 2 now ship together** in the first external TestFlight build, about the week of 9 Nov (D107). The Phase 3 tests run by hand in parallel (D63), and their lessons go in before that build.

**Screen numbers (D110):** Build 1 is screens 1–15, in the order a person meets them. The same numbers are used on the review page and in the screens PDF. Build 2's screens are 16–23.

## A. First run

| # | Screen | Build | What's on it |
|---|---|---|---|
| 1 | **Welcome** | 1 | Abram's photo and one line: "We wanted to bring some of the best experiences we've had to you, so you can have them too." What this is: a research test run by a person. "Get started". (An optional **tester code** field, e.g. `S-fbucl-07`, comes in Build 2) |
| 2 | **Consent** | 1 | **D110:** a short plain-English summary in four lines (who runs it, what you'll do and how long, what we keep, how to skip, stop or delete). **The two required choices sit in a box where they can't be missed:** "I'm 18 or over" and "I agree to take part". The details are folded under "Read the details", with a link to the full privacy notice. No 999 text here: it lives in Help & safety (14). No AI toggle while no AI service reads answers (m117) |

## B. Onboarding, up to the first plan (D110)

| # | Screen | Build | What's on it |
|---|---|---|---|
| 3 | **Best hour** | 1 | "Tell me about the best hour of your last trip or day out. Where were you, what was happening, how did it feel?" **Three short example answers.** A large text field, with a hint: "A few words is fine. Tap the mic on your keyboard to speak instead." After the first answer: "Is there anything else you'd like to add about that?" **"Skip this question"** is always there |
| 4 | **Why you go out** | 1 | "Which of these is most often why you go out or travel? **Pick up to two, or none.**" Six options: switch off and rest · time with people · discover something new · nature and outdoors · culture and history · food. With none picked, the button reads "None of these: next" |
| 5 | **Places you've been** | 1 | **10 places** (the most informative of the locked 16, D110), one at a time. Four reactions: **Loved it · It was fine · Didn't enjoy it · Haven't been**, plus **"Not sure, skip"** and **Back**. **A progress bar** with "4 of 10" |
| 6 | **This or that** | 1 | 10 tasks. Two made-up day plans, A and B, each with six attributes **in the same order with the same icons**: longest transfer, weather at the outdoor stops (mild and dry / cold but dry / rainy, D95), pace, crowds, cost per person, walking. Tap one to choose, or **"No preference"**. Back, and a progress bar. The last page: "That's everything. Next: your first plan." |

## C. The plan and the day out

| # | Screen | Build | What's on it |
|---|---|---|---|
| 7 | **Plan a day** | 1 | Where it starts (Charing Cross in Build 1), the day, start and finish times, and the number of stops. "Make my plan" |
| 8 | **Your day** | 1 | **D110: a summary at the top:** cost per person, walking between stops and the finish time, with the cost split underneath. **Map / List** switch: the map with numbered pins above the stops, or the stops as a list with the travel legs between them. Each row shows the time, the title, the travel ("12 min walk") and one line on why it's there ("Chosen for: the views, awe"). A place they loved is marked. **Swipe a row to swap it.** Below: **"Improve my plans"** (optional, about 2 minutes) and "Plan another day" |
| 9 | **A stop** (moment card) | 1 | The time and title, then **how to arrive** first: from where, which exit, the path. Then what happens, the queue, when it's best, the cost and the rain option. **Directions** (Apple Maps) and, where the stop has one, **Shot card**, which opens the card in the layout of the example on 13. **"Swap this stop"**, with one confirmation. **Rating only after the visit:** before the planned arrival it says "You can rate this stop after your visit, from 13:33 on Saturday 31 October" |
| 10 | **Rating** | 1 | "How did that feel?" **Five large buttons, 1–5, each with a word** (Poor · Not great · OK · Good · Wonderful). An optional "Would you bring someone here?" (yes / no). Save. The same prompt as a notification after each stop comes in Build 2 |

## D. Improve my plans: optional, after the first plan (D110)

| # | Screen | Build | What's on it |
|---|---|---|---|
| 11 | **A bit about you** | 1 | All optional: budget per day out (4 bands), who you go with, morning or night person, how active; **"What interests you most? Pick any, or none."** with "We ask so we can add a place tied to what interests you"; where you grew up (with why it's asked); "Any foods or drinks you avoid?" (only used to choose food stops). **No nationality, income, health or allergy questions** |
| 12 | **Photos** | 1 | One question: "How much do photos and sharing matter on your trips?" 1–5, or Skip |
| 13 | **Shot cards** | 1 | One question: "Some stops come with a shot card: where to stand for the best photo. Would that make you more likely to go?" 1–5, with the Waterloo Bridge card labelled **"Example of what you'll get"**. It is the only place the example appears. Save |

## E. Help, safety and your data

| # | Screen | Build | What's on it |
|---|---|---|---|
| 14 | **Help & safety** | 1 | **Two separate sections (D110).** **Emergency:** "If you or someone else is in danger or hurt, call 999 now", with a red **Call 999** button. **Not an emergency:** "I feel unsafe / something's wrong" (orange, not red) leads to an optional message and "Tell a person"; the reply says a person will reply within a few hours, and the Emergency section stays on screen. "Something else?" shows an email address as text. **Never promise a faster reply** |
| 15 | **Your data** | 1 | What we store, as a plain list; where and for how long; "About this test"; the privacy notice. **Delete my data** opens a page where the person **types DELETE** to confirm, because it can't be undone. The version number |

## F. Build 2 (not built yet)

| # | Screen | Build | What's on it |
|---|---|---|---|
| 16 | **Here's what we heard** (read-back) | 2 | 3–6 plain lines from the model, such as "Long transfers put you off" or "You love a reveal". Each has **Right / Not quite**. Where the model is unsure, it says "Not sure yet about crowds". A friendly persona label on top, then "Anything to fix or add?" |
| 17 | **Quick survey** | 2 | "I felt understood" 1–5; "It felt like talking to a person, not filling in a form" 1–5; "Did you type or speak your answers?" (typed / spoke / both); "Was anything intrusive or tedious?" |
| 18 | **Plans home** | 2 | An empty state ("Your plans will appear here"). A card for a new pair: "Two plans for your day. Which would you rather do?" The list of plans. **"Plan another day"**: tapping it is a Test C measure |
| 19 | **Trip intent** | 2 | Three short questions before a plan: recharge or explore? who might come? anything you'd want in it for sure? |
| 20 | **Plan 1 vs Plan 2** | 2 | Two plans in **identical format** (the screen 8 layout, without Swap, so the test stays blind). Then "Which would you rather do?", "This plan fits me" 1–5 for each, and "Why?" |
| 21 | **Before the notification permission** | 2 | "We'll ask for one tap after each stop. That's it." **Allow** and **Not now** carry equal weight. Everything works without notifications |
| 22 | **Bring a friend** | 2 | A button and one line. The system share sheet carries the text and a link with a referral code. After a stop with a shot card: "Got a shot you like? Share it." **We never ask for the photo** |
| 23 | **States** | 1–2 | Loading ("Waking up the planner" while the free server starts), empty and errors. Example error: "Couldn't reach us. Your plan is saved on this phone." There is no offline mode beyond the current plan |

## Also needed

- **App icon** (1024 px) and a working name. Abram decides the name.
- **A small component sheet:** primary and secondary buttons, a chip, the 1–5 scale, the four reaction buttons, a plan card, a stop row, a map pin (numbered, with a highlighted variant), an attribute row with icon for "this or that", and a toggle row with a note.
- **Hand-off:** frames at iPhone 15/16 size (393 × 852 pt), light and dark, with notes on spacing and states.

## Please don't design (cut from v0)

Login or sign-up, a paywall or payments, an AI support chat, a social feed or profiles, widgets, Live Activities, Watch, iPad, landscape, in-app turn-by-turn routing, or a custom voice recorder (the keyboard mic covers voice in v0).

## Timing (D109, app first; replaces D107)

- **Build 1 (~7 Oct), on Abram's iPhone through internal TestFlight:** screens 1–15. After the Build 1 feedback (D110): four onboarding steps to the first plan (best hour, why, 10 places, 10 this-or-that), the day plan with its summary, map or list and swap, moment and shot cards, rating after the visit, the optional "Improve my plans" step, help & safety, and your data with a typed DELETE.
- **Build 2 (~14 Oct): Tests A–C inside the app:** screens 16–23 (read-back, survey, plans home, trip intent, the blind Plan 1 / Plan 2 pair, rating reminders, bring a friend, states).
- **One screenshot page per batch** for Abram (about 15 min each).

*The D107 timing, for reference (old screen numbers, before D110):*

- **Now, native-first, in three batches** (Claude builds; Abram looks at one screenshot page per batch, about 15 min):
  1. **First run and safety** (screens 1, 2, 19, 20 and 22): the week of 28 Sep.
  2. **Onboarding** (screens 3–10): the week of 5 Oct.
  3. **Plans and the day out** (screens 11–18 and 21): the week of 12 Oct.
- **The custom design pass (D81)** on welcome, moment card, shot card and day plan: optional, after Test B reports (about 23 Oct) and Checkpoint 3 (the week of 2 Nov).
- **The first external TestFlight build:** about the week of 9 Nov.
- **Plan behind this:** `decisions/v0-ios-plan.md`.
