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

- **Platform:** iPhone only, portrait, iOS 17+, English. **Dark only (D119).**
- **Use system parts wherever possible:** SF Pro, SF Symbols, `List`, `NavigationStack`, sheets, the system share sheet, and MapKit. Every custom component costs build hours; the whole app has about 31 hours.
- **Accessibility:** support Dynamic Type, 44 pt tap targets, and a VoiceOver label on every control. Swipes always have button equivalents.
- **Tone:** a well-travelled friend. Short, plain and warm. No emoji.
- **Copy:** use the real copy, which is already written (`brain/data/onboarding.yaml`, `validation/interview-script.md`). Please don't design with lorem ipsum.
- **Images:** only Abram's own photos, or Wikimedia Commons files with a credit line.
- **No dark patterns.** "Not now" and "No" get the same weight as "Yes" on every permission and on the AI toggle.
- **Honesty is visible.** Say that a real person runs this test and that AI helps draft summaries and plans. Never imply a person replied when it was the app.
- **Time limits:** no visible timers and no time limits anywhere in onboarding. A section progress indicator is fine.
- **Motion (D117):** quiet and consistent. Fades and a line drawing only; no bounce, no confetti, no celebration screens. Everything respects Reduce Motion (it's simply there), and a tap skips the logo.
- **Question counter (D118):** onboarding counts every question ("7 of 14"), not steps.
- **Permissions (D117):** ask only at the moment a feature needs it, never up front. Today the only prompts are the microphone and speech recognition, when someone taps "Speak instead" (was "Tell it instead" until 19 Oct). The app asks for no location and no notifications; any later feature that needs them asks when it's first used.

**Build 1 and Build 2 now ship together** in the first external TestFlight build, about the week of 9 Nov (D107). The Phase 3 tests run by hand in parallel (D63), and their lessons go in before that build.

**Screen numbers (D110, D112):** Build 1 is screens 1–14, in the order a person meets them. The same numbers are used on the review page and in the screens PDF; a second picture of the same screen gets a letter (9a, 9b). Build 2's screens are 15–22.

## Visual direction (D119): ODYS (replaces D112's theme)

From Abram's three ODYS design files (Explorations, Motion, Prototype), built as custom SwiftUI parts in `app/Sources/Odys.swift`:
- **Dark always.** Charcoal #111317, cards #1A1D23, warm ink #F4EBDD, one amber light #FFC665 (#E5A93C for eyebrows), red only for "Call 999", cream #F4EBDD for the share card.
- **Type:** Newsreader (regular and italic, SIL OFL, bundled) for titles, answers, reactions and feel words; the system font for the rest; everything scales with Dynamic Type.
- **The arch:** the icon (design 1r), the welcome reveal, the bullets on "So far", the rating arch and the "Now" glow.
- **Motion:** Reveal, Settle, Select, Little reaction, Bloom, Listen, Drift, Way in, Swap, Thank-you mote, Lift, Breathe and Press. A response to a tap finishes within 300 ms, nothing bounces, taps always go through, and with Reduce Motion things fade or are simply there.
- **What was kept from the current app, and why:** m164 in the decision log.

## Visual direction (D112, superseded by D119): "Sensory Cartography", as a theme

From Abram's Google Stitch explorations, applied as a **theme on standard SwiftUI parts** (colours and fonts, no custom controls), in light and dark.
- **Keep:** the palette (charcoal #111317 surfaces, amber #FFC665), Newsreader serif titles, a big picture on moment cards, "Worth about £X to you" (D127: now the price and "A strong match for you", not a £ figure), the approach line, the best-light window, the cost, the numbered day plan with a simple chart of the day's shape, and worded rating labels (Flat / Pleasant / Restorative / Vivid / Unforgettable).
- **Don't use:** any model internals (β, calibration, convergence, σ, EV, "sensory yield", "surplus NET"), percentages of invented metrics, sensor or heart-rate data, or jargon ("phenomenological", "olfactory").
- **Every card detail comes from our verified cards**, never invented. The big picture is an openly licensed photo from Wikimedia Commons with its credit underneath (m152, `design/photo-credits.md`), until Abram's own replace them. The four cards without one show the satellite view, marked "Photo to come".
- **Type:** Newsreader for titles only (SIL Open Font License 1.1, bundled with its licence); body text stays SF Pro. Everything scales with Dynamic Type, and no text is smaller than footnote (13 pt at the default size), so no 9–11 px labels.
- **Light mode:** warm paper (#FAF7F0) with a deeper amber (#7E5700) for text and icons, so contrast holds; the main button is amber with dark brown text in both modes.

## A. First run

| # | Screen | Build | What's on it |
|---|---|---|---|
| 1 | **Welcome** | 1 | **D119 (ODYS): the arch lights up (the light rises, then spills; about a second), then the words settle in; a tap skips it. The ODYS wordmark, "Days out that fit you.", Abram's card ("Watch his short hello" once the video exists), "Show me an example day" and "Skip the example".** **D117: on first opening, the app icon's ring draws itself (about 0.8 s) and settles above the title as the words fade in; a tap skips it; nothing moves with Reduce Motion.** "Days out that fit you", the one line, and who runs the test. **"See an example day"**, or "Skip the example" |
| 2 | **An example day** (2b: further down, the full card) | 1 | **D119: eyebrow, title and the feeling line in italic; one stop as a picture; the stops with their kind of moment; the full card; "Make one that fits me" with "About 3 minutes. No account or name needed."** **D112:** what a plan looks like, before any question: the feeling line, the summary, the day's shape and the stops, **and one stop's full card (D115)**, so the special parts show before any question. Not personal (population weights only, a Sunday from Charing Cross, with none of Test B's usual places). "Start" |
| 2c | **A hello from Abram** (D117) | 1 | A 20–30 s video of Abram, bundled in the app, with captions. It plays if the person allows video autoplay. **"Skip"**, which becomes "Continue" when it ends. Left out until the video is in the app (`design/video-spec.md`) |
| 3 | **Consent** | 1 | A four-line plain-English summary; **the two required choices in a box** ("I'm 18 or over", "I agree to take part"); the details folded under "Read the details", with the privacy notice. No 999 text here (it's on 13) and no AI toggle (m117) |

## B. Onboarding, up to the first plan (D112: shorter)

| # | Screen | Build | What's on it |
|---|---|---|---|
| 3b | **Where you're based** (D116) | 1 | "Where are you based?" In London · Elsewhere in the UK · Visiting from abroad, then "Which town or city? (optional)" and the note "So we ask the right questions. We never ask your nationality." Next once a choice is made. It picks the questions that follow and the cohort (visitors are reported apart from Test B) |
| 4 | **A great moment** | 1 | **D118: "Skip" always visible at the top left.** **D117: a small portrait tile of Abram asking the question, beside it (captions underneath; left out until the clip exists).** "Tell us about a great moment from a recent day out. Where were you, what was happening, how did it feel?" Three short example answers, **a big "Speak instead" button (19 Oct; D115: speech becomes text on the phone; the sound is never saved or sent)**, then "Or type it", the follow-up once there's an answer, Next and **Skip this question** |
| 5 | **How you want to feel** (D115; was "Why you go out") | 1 | **D118: tick boxes (pick several), Next as the main button, "None of these" as a link.** "How do you most want to feel on a day out? Pick one or two." **Restored · Excited · Connected · Curious · Peaceful**, each with a short line; each maps onto existing features and counts in the fit as one stated choice (`brain/reasons.py`). With none picked, the button reads "None of these" |
| 6 | **Places you've been** | 1 | **6 places**, one at a time: Loved it · It was fine · Didn't enjoy it · Haven't been, plus "Not sure, skip", Back, a progress bar and **"Skip the rest"**. The other 4 are in screen 12 |
| 6b | **Kinds of places** (visitors from abroad only, D116) | 1 | **Instead of 6**, for someone who answered "Visiting from abroad": "What kinds of places do you enjoy?" 8 kinds, one at a time, each with a London example's photo and its credit ("In London, for example: …"). Love it · It's fine · Not for me · Never tried; "Never tried" then asks "Would you like to try it in London?" (Yes · Not sure · No). "Not sure, skip", Back, a progress bar and "Skip the rest". Visitors don't get the later London places in 12 |
| 7 | **This or that** | 1 | **"Which day sounds more like you? There are no wrong answers." (D117)** 5 made-up example days, labelled "Example day A / B" and "Made up", six attributes in the same order with the same icons; "No preference", Back and a progress bar. The other 5 are in screen 12 |
| 7b | **So far, I've learned…** (D117) | 1 | **D118: the tile is a small "note from Abram"; on "Change something" each line has a clear "Don't use this" / "Undo" button (19 Oct; was "Not right").** Before the first plan: Abram's 5–8 s thank-you tile, then the person's own answers in plain words (no scores), e.g. "You loved Brick Lane for food: local food with a bit of history", "In the example days, you chose the relaxed day with fewer stops every time". **"Looks right"**, or **"Change something"**: tap any line that isn't right, then "Save and plan my first day". Corrections are stored and those answers stop counting |

**Reactions between answers (D117), on 5, 6, 6b and 7:** a short line above the next question, only from what the person answered: "Got it: food with a bit of atmosphere" (a place loved), "Noted: not so much …" (not enjoyed), the feelings picked, and on this-or-that a pattern once it has held three times ("So far you've picked less walking every time"). "It was fine", "Haven't been" and skips say nothing.

## C. The plan and the day out

| # | Screen | Build | What's on it |
|---|---|---|---|
| 8 | **Plan a day** | 1 | **D118: Today / Tomorrow / Saturday quick picks.** **D115: next Saturday, 12:00–17:00 from Charing Cross, 4 stops, already filled in; one tap on "Make my plan".** "Change the day or times" opens the pickers |
| 9 | **Your day** (9a–9d) | 1 | **D119: (9a top, 9b the stops further down, 9c the reveal, 9d the map) the date as an eyebrow with Help and Your data; the headline; cost, walking and finish; "How the day moves" (a curve, higher where we think you'll enjoy it more, with each stop's word: Awe, Calm, Lunch …); List / Map; stop cards with a photo, "13:30–14:45 · Awe", the reason and the worth in amber; "Start the day".** **D118: the headline uses the person's own feeling words when the stops carry them ("A curious, peaceful day: …"); once, after a plan: "Remind me to rate each stop?" (Yes, remind me / No thanks, equal weight; iOS's prompt only after yes; 19 Oct: just above "Start the day", and the numbers are chips with List / Map under the headline); the chart is titled "How much we think you'll enjoy each stop".** **D117: a new plan appears in order instead of after a spinner (about 2.6 s, once): the feeling line, then the summary, then the route draws across the map and each stop appears as the line reaches it. Fades only; nothing moves with Reduce Motion.** **D115: the feeling line first** ("Lunch to start, one big reveal, some history, then a big view"), then **the summary, large:** cost per person, walking between stops, finish time. **The shape of the day:** each stop as a block across the day, taller where we expect the person to enjoy it more (no numbers). Map or List, the numbered stops ("Chosen for: …"), swipe to swap. **"Plan again"** (was "Regenerate plan" until 9 Oct; one confirmation; off in the blind Test B comparison), "Improve future plans" and "Plan another day" | **Each stop shows its first reason** (D115). The chart says what it shows in one sentence (D115). Feeling line and reasons are hidden in the blind comparison |
| 10 | **A stop** (moment card) | 1 | **D119: (10a further down) the photo full-bleed with the time, the word and the title on it, drifting slowly; "Why we picked this for you" in the serif; "The way in" as a path you can tap along, with "The reveal" marked where the arrival is the moment; the shot card; Best time and light, What happens, Cost, If it rains; "Directions in Apple Maps", Swap, Regenerate.** **D118: "Worth about £X to you · Free entry" (or "· Costs £Y"), then "A first estimate from what you've told us so far"; the time over the photo on a dark band.** The big picture with **"Worth about £X to you"**, the title, the cost, **the approach line** (From → The way in → You arrive, in the card's words), **the best-light window** on the plan's day, what happens, the queue, the rain option, Directions, Shot card, Swap this stop. **Rating only after the visit**. **D115: "Why we picked this for you"**, up to two reasons from the person's own answers and an honest "so far" line; **"Worth about £X to you, and it's free"** on free stops |
| 10b | **Now** (D119, new) | 1 | While you're out, on a darker screen: "Now", the stop's title, "Enjoy it. I'll stay quiet until you need me.", a slowly breathing arch, "Next, around 14:34" with how to get there, **"I'm done here"** (the rating, then on to the next stop), "See the whole day" and "Help". Opened by "Start the day"; kept per plan |
| 10c | **Now: the day done** (m177) | On a trip: the way back to the stay, "Thanks for today" (19 Oct), then **"Preview tomorrow: Day N"**, which opens tomorrow's page, where it can still be changed |
| 11 | **Rating** | 1 | **D119 (11a after saving): "Just finished", "How did … feel?", the arch fills with light to the word; Save; then a mote of light, "Thank you. That helps the next day fit better.", "Share this moment" and "On to the next stop".** "How did that feel?" **Five worded steps, one dimension (D115): Disappointing (was Flat, D127) · Fine · Good · Great · Unforgettable**, an optional "Would you bring someone here?", Save |
| 11b | **Share card** (D114) | 1 | **D119: cream, "Rated: Great" on the photo, "I think you'd love this", the title, the person's own reason as the quote, the arch and "Planned with ODYS"; lifted into place before "Send to a friend" / "Not now".** After a stop is rated, **"Share this moment"** under "Rated. Thank you" (for any rating). The card: the moment's photo with its credit, the title, **the person's own rating** ("My rating: 5 of 5, unforgettable"), "Planned with Days out". The system share sheet adds their link and "I think you'd love this day — try it". **Never "worth £X"; no rewards**. **D115: the plain-language reason, in their own voice** ("I loved the view from the top of Greenwich Park.") |

## D. Improve future plans: one optional screen after the first plan (D112)

| # | Screen | Build | What's on it |
|---|---|---|---|
| 12 | **Improve future plans** (12a invitation, 12b a question) | 1 | **D118: offered once a stop is rated ("Your first stop taught us something"), as "Make your next day even better?"; before that, a quiet "A few more questions (optional)" link.** **D115: "Want us to learn you better? About 30 seconds."** Then one question per screen, one tap each: budget, company, morning or night, how active, "What interests you most?", where you grew up, foods avoided, how much photos matter, the shot-card question with a **short example**. Skip any; "Stop here, keep my answers". After that, optionally, **4 more places** and **5 more made-up example days** (about a minute). **No nationality, income, health or allergy questions** |

## E. Help, safety and your data

| # | Screen | Build | What's on it |
|---|---|---|---|
| 13 | **Help & safety** (13a, 13b just sent, 13c a reply) | 1 | **D119: the emergency card is the one red thing (Call 999); the second card says a real person replies within a few hours; "Your data" at the foot.** **D118: the form also asks "Phone or email, so we can reply (optional)", used only to reply and deleted once sorted (30 days at most); replies show under the message, and "Help" on the plan gets a dot. It says who replies: Abram, or whoever is covering for him.** **Emergency:** "call 999 now", with a red Call 999 button. **Not an emergency:** "I feel unsafe / something's wrong" leads to an optional message and "Tell a person"; a person replies within a few hours, and the Emergency section stays on screen. An email address as text. **Never promise a faster reply** |
| 14 | **Your data** (14a, 14b delete) | 1 | **D118: lists Help & safety messages; a "Rating reminders" switch.** What we store, where and for how long, "About this test", the privacy notice. **Delete my data**: type DELETE to confirm. The version number |

## F. Build 2 (built 6 Oct; the screenshots are numbered 15–18 on the review page)

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

## G. Trips (D120, D121: Abram's "ODYS Trips" design, built 6 Oct; review page 19–33)

| # | Screen | What's on it |
|---|---|---|
| 19–19c | **Home (D131: no tabs)** | Before a day: "Where to next?", a day out and a trip as two equal cards, what's coming up, your trips. **On the day (19b):** the day's path, its stops, "Back to now". **After it (19c):** what you rated, in your words. Help and the menu (You, the light, your data) at the top. Flights and stays (26–32) open inside a trip. During a trip, "Today · Day N" comes first; once today is under way (or the evening before), **"Tomorrow · Day N"** with "See tomorrow" (Abram's comment, 8 Oct, m177) |
| 20–23 | **Plan a trip** | Where (London ready; UK cities next; Europe later), **when, on a calendar: the first tap is the first day, a later tap the last day, the same day twice a day out** (Abram's comment, 8 Oct, m177; replaces the lengths and the date strip), getting there (the airport from the town or city they gave; "I don't need a flight"; who's going), how it should feel (one or two) |
| 24–25b | **The trip and a day** | The checklist (getting there, where you'll stay, your days) with a coloured status each and the running total; a day's stops and "Make this my day"; **"Made other plans? Change this day"**: the hours they're free and their places, then the day planned again around them (25b, m177) |
| 26–28b | **Flights** | The pinned search, Best / Cheapest / Fastest with their tops, chips, the filter sheet with "Show N", a flight's legs and bags, where to book, and the hand-off ("You're going to…", "Did you book it?") |
| 29–32 | **Stays** | List or map, the filter sheet, a place's page with its price and where to book |
| 33 | **You** | 999, a person, what the app has learned, your data |

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
