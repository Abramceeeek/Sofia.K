# v0 screens: design brief (D50, D81)

**What the app does:** it plans a day out around how a specific person wants to *feel*, not around famous sights. The unit is a **moment**: a specific experience at a place and time, often including how you arrive. One example is walking out of South Kensington tube and seeing the Natural History Museum open up in front of you.

**Who designs (D107, lean mode):** Claude builds **every screen native-first now**, in parallel with the tests: native SwiftUI with one accent colour. Abram reviews one screenshot page per batch. **His own design pass on the four custom screens (D81) is optional, after Test B reports** (about 23 Oct), as a restyle. An outside designer is optional too. If one is brought in, they sign Part A (`legal/contributor-deed-part-a.md`) before their work is used.

## Design scope (D81): four custom screens, everything else native

| Custom screen | The one thing it must get right | Build | Your design hours (GUESS) |
|---|---|---|---|
| **Welcome** (1) | A person, not a brand: your photo, the one line, and "a person runs this test" visible without scrolling | 1 | 1.5 |
| **Moment card** (10) | **The arrival is the hero.** Show "from → path → the reveal" as one vertical line before the photo gallery, because the approach *is* the moment | 2 | 1.5 |
| **Shot card** (opens from 10; short example on 12) | Read in one glance while standing on the spot: a mini map pin, a facing arrow (compass bearing), what to frame, when | 2 | 1.5 |
| **Day plan** (9) | The map and the timeline are one object: the same line colour links the numbered pins and the stop list, and travel legs are labelled segments ("12 min walk") | 2 | 1.5 |
| Type, colour and hand-off | One shared style for the four screens; frames at 393 × 852 pt, light and dark | 1–2 | 1.0 |
| **Total** | | | **7.0** |

**Everything else uses native SwiftUI** with the D112 theme: the example day and consent (2–3), onboarding (4–8), rating (11), improve future plans (12), help & safety (13), your data (14), and Build 2's screens (15–22).
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

**Screen numbers (D110, D112):** Build 1 is screens 1–14, in the order a person meets them. The same numbers are used on the review page and in the screens PDF; a second picture of the same screen gets a letter (9a, 9b). Build 2's screens are 15–22.

## Visual direction (D112): "Sensory Cartography", as a theme

From Abram's Google Stitch explorations, applied as a **theme on standard SwiftUI parts** (colours and fonts, no custom controls), in light and dark.
- **Keep:** the palette (charcoal #111317 surfaces, amber #FFC665), Newsreader serif titles, a big picture on moment cards, "Worth about £X to you", the approach line, the best-light window, the cost, the numbered day plan with a simple chart of the day's shape, and worded rating labels (Flat / Pleasant / Restorative / Vivid / Unforgettable).
- **Don't use:** any model internals (β, calibration, convergence, σ, EV, "sensory yield", "surplus NET"), percentages of invented metrics, sensor or heart-rate data, or jargon ("phenomenological", "olfactory").
- **Every card detail comes from our verified cards**, never invented. Until the cards have photos (Abram's own, or Wikimedia Commons with a credit), the big picture is the satellite view of the place, marked "Photo to come".
- **Type:** Newsreader for titles only (SIL Open Font License 1.1, bundled with its licence); body text stays SF Pro. Everything scales with Dynamic Type, and no text is smaller than footnote (13 pt at the default size), so no 9–11 px labels.
- **Light mode:** warm paper (#FAF7F0) with a deeper amber (#7E5700) for text and icons, so contrast holds; the main button is amber with dark brown text in both modes.

## A. First run

| # | Screen | Build | What's on it |
|---|---|---|---|
| 1 | **Welcome** | 1 | "Days out that fit you", the one line, and who runs the test. **"See an example day"**, or "Skip the example" |
| 2 | **An example day** | 1 | **D112:** what a plan looks like, before any question: the summary, the day's shape and the stops. Not personal (population weights only, a Sunday from Charing Cross, with none of Test B's usual places: m151) and bundled with the app, so nothing is sent. "Start" leads to consent |
| 3 | **Consent** | 1 | A four-line plain-English summary; **the two required choices in a box** ("I'm 18 or over", "I agree to take part"); the details folded under "Read the details", with the privacy notice. No 999 text here (it's on 13) and no AI toggle (m117) |

## B. Onboarding, up to the first plan (D112: shorter)

| # | Screen | Build | What's on it |
|---|---|---|---|
| 4 | **A great moment** | 1 | "Tell us about a great moment from a recent day out. Where were you, what was happening, how did it feel?" Three short example answers, a text field (keyboard mic for voice), the follow-up once they type, and "Skip this question" |
| 5 | **Why you go out** | 1 | "Pick up to two, or none." With none picked, the button reads **"None of these"** |
| 6 | **Places you've been** | 1 | **6 places**, one at a time: Loved it · It was fine · Didn't enjoy it · Haven't been, plus "Not sure, skip", Back, a progress bar and **"Skip the rest"**. The other 4 are in screen 12 |
| 7 | **This or that** | 1 | **5 made-up example days**, labelled "Example day A / B" and "Made up", six attributes in the same order with the same icons; "No preference", Back and a progress bar. The other 5 are in screen 12 |

## C. The plan and the day out

| # | Screen | Build | What's on it |
|---|---|---|---|
| 8 | **Plan a day** | 1 | Where it starts (Charing Cross in Build 1), the day, the times and the number of stops |
| 9 | **Your day** (9a map, 9b list) | 1 | **The summary first and large:** cost per person, walking between stops, finish time. **The shape of the day:** each stop as a block across the day, taller where we expect the person to enjoy it more (no numbers). Map or List, the numbered stops ("Chosen for: …"), swipe to swap. **"Regenerate plan"** (one confirmation; off in the blind Test B comparison), "Improve future plans" and "Plan another day" |
| 10 | **A stop** (moment card) | 1 | The big picture with **"Worth about £X to you"**, the title, the cost, **the approach line** (From → The way in → You arrive, in the card's words), **the best-light window** on the plan's day, what happens, the queue, the rain option, Directions, Shot card, Swap this stop. **Rating only after the visit** |
| 11 | **Rating** | 1 | "How did that feel?" **Five worded steps: Flat · Pleasant · Restorative · Vivid · Unforgettable**, an optional "Would you bring someone here?", Save |

## D. Improve future plans: one optional screen after the first plan (D112)

| # | Screen | Build | What's on it |
|---|---|---|---|
| 12 | **Improve future plans** | 1 | One screen: **4 more places** and **5 more made-up example days** (each opens the same step as 6 or 7), then budget, company, morning or night, how active, "What interests you most?", where you grew up, foods avoided, how much photos matter, and the shot-card question with a **short example** (where to stand and when). Save. **No nationality, income, health or allergy questions** |

## E. Help, safety and your data

| # | Screen | Build | What's on it |
|---|---|---|---|
| 13 | **Help & safety** (13a, 13b after the button) | 1 | **Emergency:** "call 999 now", with a red Call 999 button. **Not an emergency:** "I feel unsafe / something's wrong" leads to an optional message and "Tell a person"; a person replies within a few hours, and the Emergency section stays on screen. An email address as text. **Never promise a faster reply** |
| 14 | **Your data** (14a, 14b delete) | 1 | What we store, where and for how long, "About this test", the privacy notice. **Delete my data**: type DELETE to confirm. The version number |

## F. Build 2 (not built yet)

| # | Screen | Build | What's on it |
|---|---|---|---|
| 15 | **Here's what we heard** (read-back) | 2 | 3–6 plain lines, each with **Right / Not quite**; "Not sure yet about crowds" where the model is unsure; "Anything to fix or add?" |
| 16 | **Quick survey** | 2 | "I felt understood" 1–5; "It felt like talking to a person, not filling in a form" 1–5; typed or spoke; "Was anything intrusive or tedious?" |
| 17 | **Plans home** | 2 | The list of plans, a card for a new pair, and "Plan another day" (a Test C measure) |
| 18 | **Trip intent** | 2 | Recharge or explore? Who might come? Anything you'd want in it for sure? |
| 19 | **Plan 1 vs Plan 2** | 2 | Two plans in the screen 9 layout, **without Swap or Regenerate**, so the test stays blind. The personal plan uses only the answers from screens 4–7 (D112: the short version we'd ship). Then which they'd rather do, "This plan fits me" 1–5 for each, and why |
| 20 | **Before the notification permission** | 2 | "We'll ask for one tap after each stop." **Allow** and **Not now** carry equal weight |
| 21 | **Bring a friend** | 2 | The share sheet with a referral link; after a stop with a shot card, "Got a shot you like? Share it." We never ask for the photo |
| 22 | **States** | 1–2 | Loading ("Waking up the planner"), empty and errors ("Couldn't reach us. Your plan is saved on this phone.") |

## Also needed

- **App icon** (1024 px) and a working name. Abram decides the name.
- **A small component sheet:** primary and secondary buttons, a chip, the 1–5 scale, the four reaction buttons, a plan card, a stop row, a map pin (numbered, with a highlighted variant), an attribute row with icon for "this or that", and a toggle row with a note.
- **Hand-off:** frames at iPhone 15/16 size (393 × 852 pt), light and dark, with notes on spacing and states.

## Please don't design (cut from v0)

Login or sign-up, a paywall or payments, an AI support chat, a social feed or profiles, widgets, Live Activities, Watch, iPad, landscape, in-app turn-by-turn routing, or a custom voice recorder (the keyboard mic covers voice in v0).

## Timing (D109, app first; replaces D107)

- **Build 1 (~7 Oct), on Abram's iPhone through internal TestFlight:** screens 1–14. After feedback rounds 1 and 2 (D110, D112): an example day before consent, four short steps to the first plan (a great moment, why, 6 places, 5 made-up example days), the day plan with its summary, shape, map or list, swap and regenerate, the moment card in the new style, rating after the visit, one optional "Improve future plans" screen, help & safety, and your data with a typed DELETE.
- **Build 2 (~14 Oct): Tests A–C inside the app:** screens 15–22 (read-back, survey, plans home, trip intent, the blind Plan 1 / Plan 2 pair, rating reminders, bring a friend, states).
- **One screenshot page per batch** for Abram (about 15 min each).

*The D107 timing, for reference (old screen numbers, before D110):*

- **Now, native-first, in three batches** (Claude builds; Abram looks at one screenshot page per batch, about 15 min):
  1. **First run and safety** (screens 1, 2, 19, 20 and 22): the week of 28 Sep.
  2. **Onboarding** (screens 3–10): the week of 5 Oct.
  3. **Plans and the day out** (screens 11–18 and 21): the week of 12 Oct.
- **The custom design pass (D81)** on welcome, moment card, shot card and day plan: optional, after Test B reports (about 23 Oct) and Checkpoint 3 (the week of 2 Nov).
- **The first external TestFlight build:** about the week of 9 Nov.
- **Plan behind this:** `decisions/v0-ios-plan.md`.
