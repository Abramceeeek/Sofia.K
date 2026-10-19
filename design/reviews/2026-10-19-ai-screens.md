# Five AI reviews of the ODYS screens (19 Oct 2026)

Abram pasted these on 19 Oct 2026 after sending `design/odys-screens.pdf` (iPhone 58 screens, Android 46) to five AI models. They are kept as pasted, with image and favicon links removed. Which points were checked against the code, and what was done, is in `design/screen-review-synthesis.md`.

## Review 1

#### Overall view

The core is strong. “Days out that fit you”, the arch, the amber light, the Newsreader serif and the quiet motion feel warm and distinctive. The example day is a good idea, and the trip screens are more coherent than most booking flows. The problem is that the **test scaffolding keeps stepping in front of the product**: too many questions, too much explanatory text, and a few moments where the app contradicts itself. I would trust it more if it asked less and showed the plan sooner.

#### 1. Flow: where I’d hesitate or give up

- **Q2, screen 4, “Tell us about a great moment…”** is the first real effort. It is open-ended, early, and asks for a memory before I’ve seen a plan. I’d either skip it or bail here. Put it later, make it optional, and offer tappable examples/chips.
- **The 14-question progress label** is honest but discouraging. “QUESTION 1 OF 14” sets a survey expectation. By Q4 I’d be looking for the exit. “Skip the rest” helps, but it appears late and is quiet. Show “About 2 minutes” and a “Skip to my plan” option earlier.
- **The six place cards in screen 6/6b** are pleasant one at a time, but they add up. By the sixth, “Not sure, skip” feels like the main action. Let me rate 3 places and ask the rest later.
- **The extra test before the first plan** — screens 15–18 — is the biggest friction point. After 14 questions, “Three quick questions”, then two long plans, then “This plan fits me” for each, then “Why?” is a lot before I get my own day. Move the comparison after the first plan, or make it clearly optional.
- **Screen 9a, “A nudge to rate each stop after you leave?”** asks for another decision before I’ve even seen the plan. Defer it to after “Start the day” or to the first rating.
- **Screen 7b/7c, “So far, I’ve learned…”** is a good rescue screen. It would stop me leaving because it shows the app listened. But “Not right” is ambiguous: do I mean the fact is wrong, or that the app should stop using it? Say “Don’t use this answer”.
- **The first plan is simple once I get there.** “Make my day” on screen 8 is a good one-tap payoff. The problem is the distance to it.

#### 2. Clarity: words I’d change

- **“Worth about £32 to you – Free entry”** on screen 10/10a is the most confusing line in the pack. It reads like a price, a valuation and a contradiction at once. Change to “Why it’s worth it: about £32 of value; entry is free” or just “Entry: free. Why we picked it…”.
- **Screen 10a has a time contradiction:** the stop is shown as 13:33–14:23, but “Best time and light” says “On your day: 16:12–17:12.” That makes the planner look unreliable. Fix the sample data.
- **Screen 25a:** the caption says “Leave for Heathrow by 17:20”, but the screen shows “07:20”. Another sample-data contradiction users will notice.
- **Screens 8 and 9a use different dates:** “Sat 24 Oct” vs “SATURDAY 31 OCTOBER”. In a test build, this reads as a bug.
- **“Tell it instead”** is slightly awkward. “Speak instead” is clearer.
- **“Got it: big museums full of history”** is charming but ambiguous. Does it become a filter? Add a short confirmation line: “We’ll use this to pick places.”
- **“A nudge to rate each stop after you leave?”** — “nudge” is product language. “Remind me to rate each stop?” is plainer.
- **“Set on your phone; nothing else is sent”** is privacy-positive but unclear. Say “One reminder after each stop, on this phone only. No data is sent.”
- **“This plan fits me: Plan 1”** plus a 1–5 scale is understandable, but the label is long. “How well does Plan 1 fit you?” is cleaner.
- **“Which was yours”** on screen 18 is ambiguous. “Which plan was made from your answers?” is better.
- **“Travelling light on day 1”** is jargon. Add one line: “No big bags: one stop on the way, then your stay.”
- **“D122”** appears in the text as an internal code. If it is visible to users, remove it.
- **“ODYS earns nothing from these links in this test”** is good transparency, but “in this test” weakens it. Say “We earn nothing from booking links. You pay the provider directly.”
- **“WHAT I’VE LEARNED ABOUT YOU”** on screen 33 is creepy. Change to “What you’ve told us” or “Your answers so far”.
- **“Grazze the food stalls”** on screen 17a is a typo. “Graze”.
- **“5 = complete”** looks clipped; it should be “5 = completely”.
- **“Done by 17:00”** and **“Finish by 17:00”** should be one phrase.
- **“Not right”** and **“Undo”** on screen 7c are inconsistent. Use “Don’t use this answer” and “Undo” consistently.

#### 3. Visual design, placing and buttons

- **What works:** the arch motif, amber primary buttons, serif headlines and dark background are cohesive. Primary CTAs are consistently placed at the bottom, and “Call 999” is appropriately prominent. The trip checklist and booking cards are easy to scan.
- **Plan summary on 9a is too dense.** Price, walking distance, finish time, food, transport, start, stops and forecast are all in one paragraph. Break into chips or a 2-column summary: “£21 pp · 1.4 km walk · Done by 17:00 · 4 stops”. Then forecast separately.
- **“How the day moves”** is an interesting idea, but the graph is abstract. Label each point with the stop name and time, and say “predicted, not a score”. Also check the label order: “Lunch 12:12”, “Calm 14:34”, “Big views 13:33” looks out of sequence.
- **Full-bleed photos with white text** on screens 2a and 10a need a stronger scrim. The title over a bright sky/busy staircase can lose contrast. Add a subtle bottom gradient.
- **Selection states are colour-only.** Feeling cards and radio rows use an amber border. Add a checkmark or filled dot so it works for colour-blind users and in bright light.
- **“None of these”** on screen 5 is clipped at the bottom and styled as a quiet link. Move it above “Continue” or make it a proper secondary button.
- **Top-right “Skip”, “Close”, “Help” and gear icons** are visually quiet. Ensure 44×44 pt / 48×48 dp tap areas. “Skip” especially is small.
- **“Remove this flight from the trip”** on screen 24 is a plain text link under a card. That is a destructive action; use a quieter “Remove” menu item with confirmation, not a prominent link.
- **“Yes, nudge me” / “No thanks”** are equal-weight outlines. That is fine and not pushy, but make the default state clear.
- **Bottom tabs** work on main screens, but on Android screenshots the tab bar overlaps content on 9d, 24, 28a and 29. Add safe-area/inset padding.
- **Data screen 14a is a wall of text.** Break into “What we store”, “What we don’t store”, “How long we keep it”, “Controls”. The location paragraph especially needs bullets.

#### 4. Accessibility

- **Contrast:** muted grey secondary text on near-black is likely below WCAG AA at small sizes. Increase contrast for body copy, “Skip”, “Previous”, “Not right” and “None of these”.
- **Text over images:** add scrims; do not rely on white serif over photos.
- **Large text:** test plan summaries and data screens at 200% text size. The 9a summary and 14a paragraph will become very long and may push CTAs off-screen.
- **Tap targets:** “Skip”, “Close”, “Not right”, “Undo” and “None of these” need larger hit areas.
- **Motion:** the arch lighting (1s) and reveal (2.6s) are lovely. Respect “Reduce Motion” and allow skip on the reveal.
- **Captions:** the Abram video is promised with captions; keep that. Also provide a transcript for “Tell it instead” voice input, even though the audio is not saved.
- **Maps:** the list/map toggle is good. Ensure map pins and price labels are readable at large text, and that the list view is a full alternative.

#### 5. Trust, safety and privacy

- **Good:** “We don’t ask for your name, email or phone number”, “Delete my data”, “Sample prices made up for testing”, “This reaches a real person, not a bot”, and “999 first” all come across well.
- **Buried disclosure:** “ODYS earns nothing from these links” appears at the bottom of screens 28/28a/32, after the booking CTA. Put it next to the price or the “Continue to Skyscanner” button. Remove “in this test” unless you mean it.
- **Safety promise risk:** “They’ll reply within a few hours” is a strong promise for one founder. Add expected hours, time zone, and what happens if Abram is unavailable. Keep “If urgent, call 999” first.
- **“WHAT I’VE LEARNED ABOUT YOU”** feels surveillance-y. “What you’ve told us” is warmer and less creepy.
- **Share card copy:** “I think you’d love this” on 11b is odd because the user just rated it. If the user is sharing their own moment, say “I loved this” or “You’d love this”. Show the exact share text in the preview.
- **“Worth about £32 to you”** can feel like the app is valuing the experience for you. Explain it or remove “to you”.
- **“Set on your phone; nothing else is sent”** is good but ambiguous. Say exactly what is stored and sent.

#### 6. Platform fit

- **iOS:** the back chevron, large titles, bottom tab bar and sheet patterns feel native enough. Keep the serif, but use the native share sheet for “Send to a friend”.
- **Android:** the Material bottom sheets, sliders and filters are fine, but “Cancel” top-left and “Done” top-right feel more iOS than Material. Use a close icon or platform-appropriate actions.
- **Maps:** Android uses OpenStreetMap tiles; ensure “© OpenStreetMap contributors” is visible. iOS Apple Maps attribution is visible. Android directions to Google Maps is a sensible native choice.
- **Bottom nav:** fix safe-area overlap on Android. This is the most visible platform bug in the screenshots.
- **Inconsistent labels:** “Back”, “Cancel”, “Close” and “Done” are used across similar modal contexts. Standardise per platform.

#### Top 10 changes

| Screen number | Problem | Why it matters | Suggested fix | Severity |
|---|---|---|---|---|
| 3b–7c, 15–18 | 14 questions, then 3 more, then a plan comparison before the first plan | Highest drop-off risk; feels like a survey before the payoff | Cut to 5–7 core questions; move “great moment” later/optional; move comparison after first plan; add “Skip to my plan” early | High |
| 10a, 25a, 8/9a | Sample-data contradictions: “Worth about £32 to you – Free entry”; 13:33 stop vs 16:12 “best time”; 07:20 vs 17:20; 24 Oct vs 31 Oct | Makes the planner look unreliable and undermines trust | Fix data; add consistency checks; rewrite “Worth” as “Why it’s worth it” with value and entry separate | High |
| 11 | Rating uses Flat/Fine/Good/Great/Unforgettable while the brief says 1–5 | Confuses users and makes test data harder to compare | Use 1–5 with labels, or explicitly map words to 1–5; add “Not sure/Skip” if appropriate | High |
| 15–18 | Plan comparison is long text plus gut choice plus two fit ratings plus “Why?” | Cognitive overload before the first real plan | Shorten plans; ask gut choice first; make fit/why optional; move after first plan | High |
| 28/28a/32 | “ODYS earns nothing…” buried at the bottom; “in this test” ambiguous | Trust is most needed at the booking moment | Put near price/CTA: “We earn nothing from this link. You pay the provider directly.” | High |
| 9a | Plan summary is dense; nudge question interrupts; “nothing else is sent” unclear | Hard to scan; extra decision before the day | Use chips/cards; move nudge after “Start the day”; say “One reminder per stop, on this phone only. No data sent.” | Medium |
| 6/6b/7b/7c | “Not right” is ambiguous; “Undo” inconsistent; “Got it:…” unclear; skip labels vary | Users don’t know what will change | Use “Don’t use this answer”; confirm “We’ll stop using this”; standardise “Skip” | Medium |
| 11b | Share card says “I think you’d love this” after the user rated it | Feels inauthentic and puts words in the user’s mouth | Use “I loved this” or “You’d love this”; preview exact text | Medium |
| 13a/14a | “Reply within a few hours” is a risky promise; data screen is one long paragraph | Safety and privacy need clarity, not a wall of text | State support hours/backup; break data into “What we store / don’t store / how long / controls” | High |
| Android 9d/24/28a/29/32 | Bottom nav overlaps content; OSM attribution needs checking; “Cancel/Close/Done” inconsistent | Platform fit, legal attribution and readability | Add safe-area insets; show “© OpenStreetMap contributors”; use Material close/cancel conventions | High |

#### Quick wins I’d do first

1. Fix the sample-data contradictions on 10a, 25a, 8/9a.
2. Move the plan comparison after the first plan.
3. Rewrite “Worth about £32 to you – Free entry”.
4. Change “WHAT I’VE LEARNED ABOUT YOU” to “What you’ve told us”.
5. Put the “we earn nothing” line next to booking CTAs.
6. Add checkmarks to selected states and a scrim behind text on photos.
7. Fix Android bottom-nav overlap and OSM attribution.

The product’s soul is good. The next version should protect it by removing test friction and making the first plan feel like the reward, not the end of a questionnaire.

## Review 2

**ODYS UI/UX Review – Real Human Perspective**  
(Test build, October 2026 – based on the full set of iPhone + Android screens)

This is a thoughtful, low-key product. The dark theme + amber light + Newsreader serif + arch motif feels intentional and calm rather than trendy. It doesn’t try to look like another travel app. That personality is a strength. Below is a grounded, screen-by-screen and flow-level review as a first-time user would actually experience it.

##### 1. Flow – Where a first-time user hesitates or drops off

The biggest friction is the **14-question onboarding before the first real plan**.

- Screens 1a → 1b → 2a/2b (example day) → 2c (Abram video) → 3 (Before we start) feel good and set the tone.
- Then you hit Question 1 of 14. Even with “Skip rest” later, the progress indicator (“QUESTION X OF 14”) is demotivating. Most people will feel “this is a survey” rather than “this is going to give me a lovely day”.
- Question 4 (Places you’ve been) is a long series of photo cards. Doing 6–8 of these in a row is tiring, especially on a phone.
- The “So far, I’ve learned…” summary (7b/7c) is smart and builds trust, but it comes after a lot of effort.
- Only then do you reach “Plan a day” (screen 8).

**Result**: Many first-time users will either rush through, skip aggressively, or abandon before seeing a personalised plan. The example day helps, but it is not enough compensation for 14 questions.

Later flows (the day itself, rating, trips) are much smoother.

##### 2. Clarity – Confusing, ambiguous or too-long wording

Generally the copy is excellent – human, warm, precise. A few spots still trip people up:

- “How the day moves” (on 9a/9c) with the little mountain graphic needs a clearer explanation the first time. “Higher means we think you’ll enjoy it more” is good, but the visual language is not instantly readable.
- “Worth about £32 to you – Free entry” is clever but can feel slightly salesy or presumptuous the first time you see it.
- On the stop screen (10/10a), the nested “The way in” steps are clear once you scroll, but the hierarchy between “Why we picked this”, “Worth…”, and the arrival path could be tighter.
- “None of these” on the feelings screen is correctly quiet, but some users may miss it.
- In trips, “Travelling light on day 1” is a nice idea, but the explanation is a bit buried.

Overall the language is one of the strongest parts of the product.

##### 3. Visual design – Hierarchy, typography, spacing, contrast, consistency

**Strengths**
- Dark theme + warm amber is consistently applied and feels premium.
- Newsreader for headlines works beautifully against the dark background.
- Arch motif is used with restraint (welcome, rating, “Now”, share card).
- Cards and list items have good internal padding.
- The “reveal” animation idea on 9c is charming.

**Issues**
- Primary amber buttons are excellent, but secondary actions (Skip, Not right, Change something, No thanks) sometimes feel under-emphasised or inconsistently styled between screens.
- On several screens the bottom primary button sits very close to the home indicator / gesture area (especially noticeable on iPhone).
- Spacing between stacked cards (especially on “Your day: the stops” 9b) is a little tight on smaller phones.
- The “How the day moves” graphic is elegant but low-contrast in places.
- Android version is very close, but some Material controls (toggles, chips) sit slightly less comfortably inside the custom dark cards than the iOS versions.
- Map screens (9d, 30) look good, but the numbered pins + price bubbles on the stay map can feel a bit busy.

Consistency between iPhone and Android is high – same information architecture, same copy, same visual language. That is rare and valuable.

##### 4. Accessibility

- Text contrast is generally strong on the dark theme.
- Tap targets for the main feeling chips, rating buttons, and primary CTAs are good.
- Some smaller text (photo credits, “Made up”, secondary labels) drops below comfortable reading size.
- The rating scale (Flat → Unforgettable) is vertical and clear, but the arch that fills with light is a nice progressive disclosure.
- Location permission and rating reminders are well explained.
- Motion appears quiet, which is good.
- Large text / Dynamic Type support is not visible in the screenshots – worth verifying.

##### 5. Trust, safety, privacy, “we earn nothing”

This is handled unusually well for a solo-founder test app:

- “Nothing is sold”, “We don’t ask for your name, email or phone number” is stated early and repeatedly.
- Help & safety (13a–c) correctly separates 999 from “I feel unsafe…” and routes the latter to a real person (Abram).
- “Your data” (14a) and the hard “type DELETE” confirmation are transparent.
- Booking screens (28, 28a, 32) clearly say “ODYS earns nothing from these links” and send the user to the provider’s site. This builds more trust than most affiliate-heavy travel apps.
- The share card deliberately omits the “worth to you” estimate – good ethical choice.

Nothing feels pushy or creepy. The tone is the opposite of extractive.

##### 6. Platform fit

- **iOS**: Feels mostly native. Back buttons, sheets, toggles, and the overall quiet aesthetic sit well with Human Interface Guidelines. The custom arch and amber accents are distinctive without fighting the system.
- **Android**: Material controls are used correctly. Maps correctly use OpenStreetMap + Google Maps directions. The bottom navigation (Trip / Book / You) works. A few custom cards feel slightly less “Material” than the iOS counterparts, but the difference is small.

Both versions feel like the same product, which is the right goal at this stage.

##### 7. Top 10 changes

| Screen | Problem | Why it matters | Suggested fix | Severity |
|--------|---------|----------------|---------------|----------|
| Onboarding (3–7) | 14 questions before first plan | High drop-off risk; feels like a survey | Reduce to 6–8 highest-signal questions. Move some preference questions to after the first plan or into “Improve future plans”. Show progress as “a few questions” instead of “X of 14”. | High |
| 6 / 6b | Long series of place cards | Fatigue; users start tapping randomly | Cap at 5–6 places, or make it swipeable cards with a progress indicator and clearer “Skip rest”. | High |
| 9a / 9c | “How the day moves” graphic is subtle | Users don’t immediately understand the energy curve | Add a short first-time tooltip or make the labels more prominent. | Medium |
| 8 | Plan a day form is dense | Cognitive load right after long onboarding | Default more intelligently (today/tomorrow already good) and collapse advanced options (Must include, Starting near) behind a “More options” disclosure. | Medium |
| 10 / 10a | Stop detail is information-heavy | Scroll fatigue on the day | Make “The way in” collapsible by default or use a stepper that expands on tap. Lead with the emotional “why this for you”. | Medium |
| Primary buttons | Sometimes sit too close to bottom edge | Accidental taps / gesture conflicts | Add consistent bottom safe-area padding (especially on iPhone). | Medium |
| 7b / 7c | “So far I’ve learned” is good but long | Users may not read every line | Make the list scannable (shorter lines or two columns on larger phones) and keep “Not right” very easy. | Low–Medium |
| Rating (11) | Scale is clear but the arch animation may be missed | Missed delight and feedback | Make the fill animation slightly more noticeable on first use. | Low |
| Trips (22–25) | Some secondary settings (travelling light, places per day) feel buried | Power users will find them, casual users won’t | Surface the most common options more prominently. | Low |
| Android maps & chips | Slight visual inconsistency with iOS | Cross-platform polish | Tighten spacing and card radii so Material components sit more comfortably inside the custom dark cards. | Low |

##### Overall impression

This is one of the most carefully considered early-stage travel products I’ve seen. The philosophy (moments + feelings rather than landmarks), the ethical stance on monetisation, the quiet visual language, and the respect for the user’s time and data are all rare.

The main risk is not the design language or the individual screens — it is the length of the path to the first personalised plan. Shorten that dramatically and the rest of the experience (the plan, the “Now” mode, the rating loop, the trips) has a much better chance of landing.

The product already feels like it was made by someone who actually cares about how a day in London feels. That comes through clearly.

## Review 3

I went through all 58 iPhone and 46 Android pictures in order, as a first-time stranger would. These are static captures, so I can't judge animation, VoiceOver or large-text behaviour, and some "below the fold" items may just be scroll states.

#### The short version

ODYS has a real point of view. The arch, the amber and the Newsreader serif are distinctive and calm, and the copy is warm and specific. Several trust moves beat most commercial apps:

- the "Not right / Undo" list of what it has learned
- "Made up" labels on sample data
- 999 kept apart from the human-help form
- "ODYS earns nothing from these links"

The main problems are:

- too much effort before any payoff
- a first plan screen that buries the plan
- a few claims that overreach
- small, dim text where people need it most
- Trips behaving like a second product inside a test about day plans

#### 1. Flow: where people hesitate or leave

- **Welcome (1b).** "Show me an example day" is the big button, but the real start, "Skip the example", is small grey text. "Got a tester code?" may make a stranger wonder whether they're allowed in.
- **Before we start (2c, 3).** This is a wall before any value: a video, four bullets, a "Read the details" link, then two switches. Switches read as settings, not agreement, and the greyed Continue never says why.
- **Question 1 (3b).** "Which town or city? (optional)" with "e.g. Manchester" appears even after someone taps "In London". For a Londoner it's odd; "Which part of London?" would fit.
- **Question 2 (4).** The hardest ask, recalling and narrating a memory, comes second, before trust exists. "Tell it instead" will also trigger system permission prompts (on iPhone, microphone and speech recognition). Start easy with feelings and put the story last, or make it optional.
- **Questions 4–9 (6).** Six near-identical photo screens, each headed "Question 4 of 14" and so on. There are two skips, "Skip the rest" at the top and "Not sure, skip" at the bottom, and it's unclear what "the rest" means.
- **Questions 10–14 (7).** Five rounds of two cards with six lines each is the heaviest reading in the flow.
- **Build 2 stacking.** By my count: 14 questions, then 15 (three more), the six fields on 8, then 16 (three more), then two full plans to read and rate. "About 3 minutes" on 2a will feel like a broken promise, so say 6–8 or cut. Screen 16 also repeats earlier asks: "Recharge or explore?" echoes the feelings question, and "Anything you'd want in it for sure?" echoes "Must include" on 8.
- **Home (19).** Once a day exists there's no obvious "Plan a day out". The hero card sells "Plan a trip… the flight, the stay", which isn't what a Londoner came for.

#### 2. Clarity: the words that trip people up

- **"Worth about £32 to you · Free entry" (9b, 10).** It reads like a price or a saving, and "Free entry" beside it makes you unsure which number is the cost. It also sits awkwardly with "Nothing here is a score" (7b).
- **"Longest transfer 50 min" (7).** In London, "transfer" means changing lines. "Longest journey between stops" is clearer.
- **"Lunch comes on top" / "3 places, lunch on top" (22a, 25b).** This is an idiom that will confuse some readers. "Plus lunch" is clearer.
- **Journey descriptions (2b, 10, 10a).**
  - 2b says "about 13 min on foot from Charing Cross station", but its path says "From Temple or Covent Garden station".
  - On 10 and 10a the same journey appears three times: in the list card, in a paragraph, then as a timeline.
  - It also has a double colon ("about 26 min: walk to Waterloo…").
  - It gives a three-station "or" list without saying which to use.
- **Two vocabularies.** Users pick Restored, Excited, Connected, Curious or Peaceful, but stops are tagged "Big views", "Calm", "Awe". The headline says "curious, peaceful" while the chart says "Big views" and "Awe". Show the mapping.
- **"Best time and light… On your day: 16:12–17:12" (10a).** Your plan has you at the Garden 13:33–14:23, so it reads as if the plan misses the best light.
- **Voice.** It flips between "I" ("I'll plan real moments", "So far, I've learned…") and "we" ("We keep your answers"). With one founder, pick one.
- **Screen 3's "'Your data' → Delete my data removes everything".** This points to a menu the user can't see yet.
- **Smaller ones.** "This plan fits me: Plan 1" (17b) should be "Plan 1 fits me". "Did you book it on Skyscanner?" (28b) is off, because Skyscanner is a comparison site and people book with an airline or agent. "Best £389 · 13h 36m" (26) doesn't say it's both legs combined. On 28 the header says Thu 22 Oct but the outbound leg says Wed 21 Oct.

#### 3. Visual design and placement

- **Plan screen hierarchy (9a, 9c, 9d).** The payoff moment is spent like this:
  - a four-line, 17-word headline
  - three lines of tiny stats, with "Done by 17:00" orphaned on its own line
  - a notification-permission card
  - a decorative chart
  - only then the list/map toggle, then the stops

  The plan starts about two screens down, and the map toggle is buried so deep many people won't find it. The chart's curve between stops is invented data, with staggered labels and a clipped "Big views".
- **Text over photos (2a, 6, 10).** White and amber text sits on busy images. The amber time on 10 is hard to read over foliage, and Android's "Back" sits on bright steel.
- **Placeholder-looking images.** 9b's flat orange lunch tile, the gradient thumbnails on 19 and the brown blurs on 29 and 32 look like failed loads. "Lunch near Waterloo station" also names no place, which undercuts the "specific moment" idea.
- **Amber overload.** Eyebrows, links, times, prices, status pills and selected states all use amber, so non-tappable "Worth about £32…" looks like a link. Reserve amber for actions and selection.
- **Selection patterns.** Radios (3b), checkboxes (5), amber outlines (22, 23, 27) and switches are all used. Unify them and add a checkmark so state isn't colour alone.
- **Screen 6.** "Got it: big museums full of history." shows but none of the four buttons looks selected.
- **Screen 7.** The cards have no tap affordance or selected state. The red gradient on the rainy, busy day reads as "bad" and biases the choice.
- **Bottom edges on iPhone.** Things are clipped or cramped on 3 ("Got a tester code?"), 5 ("None of these"), 7 ("Previous" and "No preference" jammed into the corner) and 13a ("Send to a person"). On 4, Next is below the fold, though Android shows it. Use a sticky bottom area with padding.
- **Plan a day (8).**
  - The When chips and the Day row control the same thing.
  - iPhone shows no chip selected, "31 Oct 2026" in Day, and a chip saying "Sat 24 Oct".
  - "Starting near" pills wrap awkwardly ("Charing / Cross", "Where / I am").
  - Charing Cross as the only default start is a tourist assumption; let people type a station.
- **Lists with lots of chrome (26, 29).** The first result starts about 60% down the screen.
- **Map (30).** Price pills pile up in the centre; cluster them.
- **Floating tab bar (24, 25, 26, 29, 33).** Content shows through it and nothing reserves bottom space, so last rows collide with it.
- **Screen 33.** "Talk to a person" has no button or chevron, unlike the 999 card.
- **Tab labels.** "Book" with a paper-plane icon reads as send or navigate. The Trip tab also holds your day plan.

#### 4. Accessibility

- **Small text.** A lot of critical information is tiny and grey, including the "Getting there" lines, photo credits and helper text. Several screens already clip at default size (2a, 9c), so test at the largest text sizes.
- **Contrast.** Live controls look disabled: "Previous", "Skip", "Coming next", dim calendar dates. By eye they're around 2–3:1, so measure against 4.5:1 for text and 3:1 for controls. On Android, the off-state switch thumb (grey on dark grey) nearly vanishes on 3, 14a and 22. That's the consent switch on 3.
- **Tap targets.** Steppers on 8, 22, 22a and 25b look about 30pt, and calendar days and text links ("Change", "Directions", "Remove this flight…") are small. Aim for 44pt on iPhone and 48dp on Android.
- **Motion.** The arch intro and the 2.6 s reveal are fine if they respect Reduce Motion. "Once" is good.
- **Sunlight.** Dark-only is brave for an app used outdoors in daylight. At least raise contrast and size on Now and the stop path.
- **Screen readers.** The chart and map need text equivalents, such as "Lunch 12:12, Big views 13:33…".

#### 5. Trust

**Working well:**
- the founder named up front
- no name or email
- an age gate
- the plain-words "What I've learned"
- Delete my data
- a real human behind Help
- "We've allowed an hour from landing… a guess"

**Weak points:**
- **"They'll reply within a few hours" (13a, 13b, 33).** A one-person team at about 7.5 hours a week can't keep this at 3am. An unkept safety promise is worse than a modest one, so state real cover hours.
- **Help on Now (10b).** It's a tiny corner link, and it's absent on the stop page (10), exactly where people are outdoors.
- **"The sound isn't saved or sent" (4).** Platform speech recognition can send audio to Apple or Google. Verify this, or reword it to "ODYS doesn't keep the audio".
- **Invented precision.** "£32 to you" on 3 places and 5 example days, plus the near-identical reason line on stops 2 and 3, makes the personalisation feel templated.
- **Permission asks.** The notification ask (9a) and the location ask (Android 10b) sit above the content. Ask in context, after value.
- **Share card (11b).** It sends "I loved Uber Boat on the Thames, and this has views too." in the user's voice. That's the app's reason, not their words.
- **Data page (14a).** It's a 20-line wall of text. "Your location is never stored" sits near "sent rounded to about 100 m and not kept", which lay readers will find contradictory. It doesn't mention free-text or voice answers. Chunk it under headed sections, and consider a UK GDPR check on the copy.
- **"Earns nothing".** Keep it literally true if affiliate IDs ever appear, and add "in this test" everywhere, not just on 32.

#### 6. Platform fit

**iPhone:**
- The floating tab bar is in the iOS 26 idiom, but radios and checkboxes aren't iOS patterns. A checkmark list is more native.
- Cancel and Close placement is right.
- Screen 10 has no visible back button, while 32 does. Inconsistent.

**Android:**
- "‹ Back" and "Cancel" text labels are iOS idioms. Use an arrow or X icon.
- The bottom bar has no Material 3 pill indicator.
- The booking sheets (28a, 28b) sit on a solid black screen with no dimmed page behind. If that's real rather than a capture artefact, it's a rendering bug.
- Photo crop on 25 is a tall sliver.
- 22b is a blank search screen with no suggestions.
- OSM tiles need visible attribution and compliance with their usage policy.
- There are differences from iPhone: 1b is missing "Watch his short hello", and "Yes, nudge me" wraps to two lines.

#### 7. Trips, and some logic worth checking

**Scope.** Trips is about 25 of the 58 screens plus a whole nav tab, while the current test is whether a personal plan beats a generic one. For London-based testers it's irrelevant. Consider hiding it for the stranger round.

**Smaller Trips points:**
- Step 1 (20) has one valid answer, so skip it.
- The calendar's "same day twice for a day out" is invisible. Add a hint.
- Screen 23 re-asks the feelings question. Say "from your answers".
- Screen 32 says "1.9 km from Charing Cross, where your days start", but 22a says days run "from where you're staying".
- The hotel rating's source isn't named.
- "Remove this flight from the trip" (24) is bare grey text under the card.
- "Booked" is self-reported.

**Logic checks:**
- **Time zones.** On 26 and 28, 20:00 + 6h 50m = 02:50 and 10:20 + 6h 46m = 17:06. That looks like the Tashkent–London time difference isn't applied, and Day 1 maths flows from it.
- **Early-morning arrival.** Day 1 puts you at Paddington at 04:18 via the "Elizabeth line or Heathrow Express". As far as I know neither runs that early, so check the live timetable. It also leaves about a five-hour gap before the 10:01 stop.
- **Clock change.** The sample trip crosses the Sunday 25 Oct change, so test it.
- **Pack caption.** The caption for 25a says "17:20" but the screen says 07:20.

#### Top 10 changes

| Screen | Problem | Why it matters | Suggested fix | Severity |
|---|---|---|---|---|
| 9a (9c, 9d) | Plan sits about two screens down, behind a 4-line headline, tiny stats, a permission card and a decorative chart. The map toggle is buried. | The payoff moment is spent on setup, and people may never find the stops or the map. | Stops first, stats as three tiles, move the nudge to after "Start the day", pin List/Map at the top, shorten the headline. | High |
| 4 | The open memory question comes at Q2. On iPhone the tile squeezes the question and Next is below the fold. | Likely biggest drop-off, before trust exists. | Move it after feelings and places or make it optional, put the tile above the text, add a sticky Next, pre-explain permissions. | High |
| 9b, 10, 10a | "Worth about £32 to you" is unexplained and falsely precise, amber like a link, and clashes with "Nothing here is a score". The same reason line repeats. | Personalisation feels fake, which is the thing under test. | Use "Strong match" with tap-to-see-why, or a range. Vary the reasons and drop the duplicate "so far" caveat. | High |
| 13a, 13b, 10b, 33 | "Within a few hours" from a one-person team. Help is a tiny corner link on Now and absent on stops. "Talk to a person" has no button. | An unkept safety promise erodes trust, and help must be findable outdoors. | State real cover hours, keep Help on every in-day screen, make the card a button with a chevron. | High |
| 3 | Consent is two switches, Continue is greyed with no reason, details are away from the agree row, the bottom link is clipped. Android off-state is near-invisible. | It's the first legal moment, so people leave or agree blind. | One "I'm 18+ and agree" checkbox row with an inline "Read the details", a clear off state, a bottom bar clear of the edge. | High |
| 7 (7b) | No tap affordance or selected state, confounded trade-offs, "transfer" jargon, a duplicate £60 row, repeated five times. | Fatigue and a muddy signal, and "you chose the relaxed day" may be wrong. | "Choose A/B" buttons, show only differing rows, three rounds, vary one thing at a time. | Medium |
| 24, 25, 26, 29, 33 | The floating tab bar overlays content with no bottom inset. | Last rows are obstructed and it looks glitchy. | Reserve bottom padding and use a denser blur or solid fill. | Medium |
| 10b, 10c | The outdoor screen leads with a giant title and empty arch. "I'm done here" is off-screen on Android, and a permission card sits on top. | It's used one-handed in daylight, so the key action shouldn't need a scroll. | Lead with Next stop and Directions, add a sticky "I'm done here", ask for location in context, raise contrast. | Medium |
| 3, 4, 5, 6, 8, 21 | Tiny, dim controls ("Previous", "None of these"), three different Skip labels, steppers around 30pt. | Accessibility failures, and people skip the wrong scope. | One Skip pattern with clear scope, 44pt/48dp targets, 4.5:1 text. | Medium |
| 11a, 11b | "Share this moment" is the primary button after every rating, and the card sends an app-generated reason in the user's voice. | It feels pushy mid-day, and people send words they didn't write. | Make "On to the next stop" primary, offer sharing only after Great or Unforgettable, let them write one line. | Medium |

I can go deeper on any one flow, for example a restructured 9a plan screen or the first-run order, if that would help.

## Review 4

##### Executive Overview

ODYS occupies a refreshing niche in the travel and itinerary space. By anchoring days out in emotional states rather than generic tourist checklists, it flips traditional recommendation models on their head. The consistent dark-mode aesthetic, Newsreader serif typography, warm amber accents, and arch motif give it a distinct, boutique, literary feel that immediately sets it apart from hyper-utilitarian apps like Google Maps or TripAdvisor.

Below is a detailed, human-perspective review across flow, clarity, visual design, accessibility, trust, and platform fit, culminating in an actionable priority matrix.

---

##### 1. Flow & Onboarding: The 14-Question Hurdle

* **The Friction Point:** Asking a first-time user to push through up to 14 onboarding questions before they ever see a customized plan is a high-risk strategy. Even with skip options and voice input ("Tell it instead"), cognitive fatigue sets in quickly on mobile devices.

* **The Saving Grace:** The conversational copywriting ("Tell us about a great moment...", "A few things first") successfully masks the clinical feel of a survey. However, hitting users with *more* questions right after their first plan (Screen 15: "Three quick questions") creates compounding survey fatigue.

* **Recommendation:** Move to a progressive profiling model. Deliver the first AI-generated day out after 3 to 4 core questions (Base location, how you want to feel, one quick preference), and let the app learn the remaining preferences organically through stop ratings and optional prompts over time.

##### 2. Clarity, Tone & Copywriting

* **The Strengths:** The app’s voice is its superpower. Copy like *"A research test run by Abram, one person in London. Nothing is sold"* instantly disarms the user and builds profound authenticity. The explicit statement *"ODYS earns nothing from these links"* is world-class microcopy for trust.

* **Potential Confusions:**
* **Screen 7c ("So far: changing something"):** Tapping "Not right" on individual preferences to remove them is clever, but the interaction model feels slightly abstract. Users might wonder if tapping it permanently deletes it or just skips it for the current session.

* **Screen 11 (Rating scale):** The ratings (*Flat, Fine, Good, Great, Unforgettable*) are poetic, but **"Flat"** is ambiguous for a negative experience. It sounds neutral or design-related rather than disappointing (e.g., "Meh" or "Uninspiring" might read more naturally to human instincts).

##### 3. Visual Design, Typography & Dark Theme

* **The Aesthetics:** The permanent dark theme paired with rich amber highlights (`#FFB74D`-style tones) and the Newsreader serif font creates an intimate, calm environment. It feels like reading a curated weekend magazine.

* **Hierarchy & Contrast:** On dark themes, pure black backgrounds with subtle grey cards work well, but small-scale serif body copy can suffer from "halation" (light text bleeding into dark backgrounds), causing reading fatigue. Ensure secondary text labels use a slightly brighter off-white (`#E0E0E0`) rather than deep muted grey to maintain legible contrast.

##### 4. Accessibility & Ergonomics

* **Tap Targets:** Most primary CTA buttons (e.g., "Make my day", "Continue") are generously sized and well-positioned in the thumb zone at the bottom of the screen. However, inline text links (like "Read the details" or "See the whole day") have tight vertical bounding boxes that can frustrate users with larger fingers or motor impairments.

* **Motion:** The subtle opening animation (the arch lighting up) is delightful and sets a calm tempo without causing motion sickness.

##### 5. Trust, Privacy & Monetization Transparency

* **Privacy Controls:** ODYS handles privacy exceptionally well. Explicitly reassuring users that location data is never stored permanently and offering a zero-friction data wipe via a simple keyword confirmation (`DELETE`) is exemplary.

* **Affiliate Clarity:** Because travel affiliate models often invite skepticism, the upfront disclaimer on booking screens (*"ODYS earns nothing from these links"*) completely removes user guardrails and anxiety about hidden monetization motives.

##### 6. Platform Fit (iOS vs. Android)

* **Cross-Platform Consistency:** The distinction between Apple Maps (iOS) and OpenStreetMap/Google Maps (Android) is handled cleanly. However, ensure that native sheet behaviors—such as bottom sheets, system pickers, and back-navigation gestures—feel truly native to each OS rather than hardcoded web-view approximations.

---

##### Top 10 Actionable Changes

| Screen Number | Problem | Why it matters | Suggested Fix | Severity |
| --- | --- | --- | --- | --- |
| **Screen 3 / 3b** | 14 questions before a first plan creates high drop-off friction.

 | Users want immediate value before investing emotional or mental energy into a new app. | Reduce initial questionnaire to 4 core questions; generate the first plan faster and capture preferences progressively. | **High** |
| **Screen 11** | The rating term "Flat" is unintuitive for a negative experience.

 | Users might hesitate or miscategorize their feedback if terms feel abstract. | Change "Flat" to a more relatable human expression like "Meh" or "Uninspiring". | **Medium** |
| **Screen 3** | Required legal checkboxes are tucked away in a dense block.

 | Obscuring terms can cause friction or drop-offs right before onboarding completion. | Keep the 18+ and agreement toggles clean, distinct, and immediately visible without extra folds. | **High** |
| **Screen 7c** | "Not right" toggles on past learning summary lines feel ambiguous to undo.

 | Users may accidentally disable preferences they actually care about without knowing how to revert. | Add a clear visual state change (e.g., strikethrough with a prominent "Undo" toast). | **Medium** |
| **General / Typography** | Small serif body text on OLED dark backgrounds causes reading strain (halation). | Users with mild visual impairments will struggle to read paragraphs comfortably. | Increase base body font size by 1–2sp and lighten secondary text color to a soft off-white. | **High** |
| **Screen 14a/b** | Deleting data requires typing "DELETE" in all caps on a mobile keyboard.

 | Forcing manual capitalization creates unnecessary input friction for a destructive action. | Replace text-typing confirmation with a clear two-step modal warning and a red destructive button. | **Low** |
| **Screen 10b** | "I'm done here" button styling blends too closely with secondary container cards.

 | During an active day out, users need to find exit/completion actions instantly under stress. | Give the active state action a stronger amber outline or solid fill to elevate its visual weight. | **Medium** |
| **Screen 28a/b** | Manual tracking loop ("Did you book it on Skyscanner?") relies entirely on user memory.

 | Users often forget to return to the app to confirm bookings, leaving trip checklists inaccurate. | Use smart deep-linking callbacks or allow automatic itinerary ingestion via email confirmation parsing if feasible. | **Low** |
| **Screen 9a** | "How the day moves" graph description is slightly abstract.

 | Users might misinterpret what the energy curve line actually represents regarding pacing. | Refine microcopy to: *"Energy curve: peaks where moments match your chosen mood."* | **Low** |
| **Screen 22b** | "Flying from" origin input relies on manual typing without smart fallback.

 | Manual airport code lookup can stall users who don't know their exact IATA code. | Implement location-aware auto-suggestion for the nearest major airport based on device region. | **Medium** |

## Review 5

### ODYS: Detailed UI/UX review — every screen, iPhone and Android

I reviewed the 40-page screen pack, including the onboarding flow, the first personalised day, the live day-out experience, ratings, safety and privacy, the plan-comparison experiment, and the flight and accommodation screens.

My honest reaction: ODYS has a distinctive identity and a genuinely interesting product idea. The biggest problems are not the colours, typography or general visual design. They are the amount of effort required before the first result, the clarity of certain decisions, and consistency between screens.

It looks like someone has thought carefully about what makes an experience memorable, rather than simply putting attractions into a list. The idea of planning around how someone wants to feel, including how they arrive at a place, is strong. The arrival-path cards and explanations of why a place was chosen are the most distinctive parts of the experience.

However, I think ODYS currently explains and asks quite a lot before it has earned the user's patience. Some of the screens also communicate more certainty than I would expect from a young recommendation system, and there are a few visual and data inconsistencies that could undermine an otherwise thoughtful design.

I'm judging this as someone actually trying to use the app, not just looking for things to criticise as a designer. These are screenshot-based UX findings and informed predictions about user behaviour, not results from live usability sessions.

#### 1. My overall verdict

What I genuinely like

The dark charcoal and amber palette, the arch identity, the editorial typography, the example-day preview, the personal explanations, and the detailed arrival paths. The screens feel like parts of one product rather than a collection of unrelated templates.

What would make me hesitate

The long sequence before the first plan, the free-text question arriving early, repeated day comparisons, and another optional questionnaire after rating a stop. I'd be asking myself, “When do I actually get to see my day?”

What I would fix before a wider test

The date inconsistency on screen 8, content appearing behind bottom navigation, the unclear monetary “worth to you” estimates, the weather forecast's apparent precision, and some inconsistent iPhone and Android states.

The important distinction is that I would not redesign the whole app. I would preserve the visual identity and improve the order, clarity and reliability of the experience.

#### 2. The 10 changes I would prioritise

This is the order in which I would address the problems, based on their likely effect on trust, task completion and the quality of the test.

| Screen             | Problem                                                                                                                     | Why it matters                                                                                                                        | Suggested fix                                                                                                                               | Severity    |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| 8, 9a              | Date inconsistency: the quick option says Sat 24 Oct, while the date field shows 31 Oct 2026                                | People may suspect the plan is using the wrong date or that the controls are not working                                              | Use one selected date throughout the form, plan summary, stop schedule, map and forecast. Add automated consistency checks                  | High        |
| 1b–7b              | Too much before the first personalised plan                                                                                 | Casual users may not finish 14 questions, particularly when one asks them to recall and describe an experience                        | Offer a useful first plan after a smaller set of essential questions, then invite more personalisation afterwards                           | High        |
| 9a, 9c, 9d, 24, 33 | Important content is low down, and some screenshots show the bottom navigation covering content                             | People may miss the route, next stop, chart or data controls; the supposed map view also does not visibly become a map above the fold | Reserve space for the navigation inset and make switching to Map visibly change the main content                                            | High        |
| 9a, 10, 25         | “Worth about £32 to you” is intriguing but ambiguous                                                                        | Users could confuse it with a ticket price, question how ODYS knows their personal monetary value, or feel over-analysed              | Label it as an experimental personal-value estimate, explain it briefly and distinguish it from the actual cost                             | High        |
| 9a                 | A precise weather forecast appears for 31 October, although the pack is dated 19 October                                    | Exact-looking weather claims can create false confidence in plans made well in advance                                                | Show forecast confidence and uncertainty, update the outlook as the day approaches, and avoid false precision                               | High        |
| 26–32              | Demo flights and stays have realistic pricing, ratings and review counts; map/list parity needs checking                    | Sample data can look real, especially for costly decisions. The accommodation photos also appear as blank placeholders                | Explicitly label all demo metrics, remove fabricated review counts from realistic-looking examples, and verify that map pins match listings | High        |
| 6, 27, 31, 10a     | Some actions and filter states are not immediately obvious                                                                  | Users may not know which answer is selected, what a filter slider currently means, or which path step can be tapped                   | Strengthen selected states, show units and current filter values, and add clear direction affordances                                       | Medium–High |
| 10b, 11            | The location prompt interrupts the Android “Now” screen; the rating screen has different dismissal options across platforms | A person outdoors needs immediate access to their next step and should not feel trapped into rating                                   | Keep the location request contextual but non-blocking, and offer a consistent, easy-to-find way to skip a rating                            | Medium–High |
| 13a–14b, 33        | Safety response availability and some privacy wording could be clearer                                                      | Trust is particularly important when the app accompanies someone on a day out or trip                                                 | State when support is monitored, clarify UK-specific emergency guidance, and distinguish live GPS from a chosen start point                 | Medium–High |
| All screens        | Small secondary links, top controls and muted supporting text need accessibility verification                               | A visually attractive interface can still be difficult to operate with larger text, reduced vision or limited dexterity               | Test real device tap targets, colour contrast, font scaling, VoiceOver, TalkBack and reduced-motion settings                                | Medium–High |

I'll explain the reasoning behind these findings, including the screens that already work well.

### 3. Welcome and onboarding: screens 1a–7

#### Screens 1a and 1b — Welcome

My reaction: this is a strong first impression.

The arch is distinctive without being overly complicated. The charcoal background, restrained amber light and serif wordmark give ODYS a consistent visual personality. “Days out that fit you” is a clear opening proposition.

The welcome screen also does something valuable: it immediately says the app plans real moments around how you want a day to feel, including how you arrive. That's more interesting than “discover London's best attractions”.

The transparency about the research test and the fact that nothing is sold is another positive. It sets expectations instead of pretending a one-person research prototype is a fully established travel company.

##### What I would change

There are two introductions to Abram:

- On screen 1b, the welcome card says “Watch his short hello”.
- Screen 2c then has a separate “A hello from Abram” video screen.

This risks feeling repetitive. I would either make the welcome link jump to the introduction video, with a clear route back, or keep the dedicated video later and remove the duplicate invitation from the welcome card.

The screen should also make its main path immediately obvious. “Show me an example day” is a good primary button. “Skip the example” is a reasonable alternative, although the subdued footer links should remain easy to see and tap.

My recommendation: keep the screen almost exactly as it is. It is one of the strongest screens in the pack.

#### Screens 2a and 2b — The example day

This is probably the strongest part of the onboarding experience.

Showing an actual stop, the arrival route, what happens there and how it fits into the rest of the day makes the idea tangible before asking me to share anything about myself.

That is good product design. I can understand what I am getting in return for answering questions.

I particularly like the progression from:

- A photograph and an evocative stop title.
- The time and the type of moment.
- A short description of what I will experience.
- The way in, including the station and arrival instructions.

It begins to show why ODYS is different from a conventional places list.

The main issue is length. Screen 2b becomes a long editorial page. That's acceptable for someone who wants to investigate the concept, but I would avoid making every new user read the whole thing.

Suggested improvement: keep the photograph and one complete moment visible near the top, then use a small “See the full example day” action for the longer itinerary. Let interested users explore without making them feel obliged to study every detail.

Also, “About 3 minutes. No account or name needed” is persuasive copy. Keep it, but test whether people can genuinely reach their first plan within that time.

#### Screen 2c — A hello from Abram

The idea is good. For a personal research project, a short video explaining why the app exists can make the experience feel more human and build trust.

The current screenshot, however, contains a largely empty video panel. The pack says this is a placeholder until the video is recorded, so I am not treating the empty panel as a finished-design flaw.

Once the video is ready, I would check three things:

- Captions should be easy to read, and playback should not be required to continue.
- The introduction should explain what the user will get out of the test, not simply why the founder built it.
- The video should genuinely be short. Twenty to thirty seconds is reasonable.

If the video remains optional, its duration and the Skip action should be obvious.

#### Screen 3 — Before we start

The four short explanations are reassuring: the test is run by one person, answers are used for planning and research, questions can be skipped, and data can be deleted.

This is an unusually good amount of transparency for an early prototype.

I would reconsider the two required switches, though:

- “I'm 18 or over”
- “I agree to take part”

These are consent decisions rather than ongoing preferences. Checkboxes or explicit confirmation controls may communicate that more clearly than switches, which people tend to associate with settings that can be turned on or off.

I'd also make the participation details available directly from “Read the details”, with an understandable summary of what the research collects and what will happen to the results.

Do not turn this into a long legal wall. The current concise explanation is a good start; it just needs to make the actual consent decision unmistakable.

#### Screen 3b — Where you're based

This is well handled.

“In London”, “Elsewhere in the UK” and “Visiting from abroad” are understandable options. Asking for a town or city optionally, while explicitly saying that nationality is not requested, feels respectful.

I would keep the field optional and avoid asking for location permissions here. The app can get useful information from a chosen city without immediately requesting access to live GPS.

#### Screen 4 — A great moment

This is the first point where I think a user could hesitate.

The question is:

> “Tell us about a great moment from a recent day out. Where were you, what was happening, how did it feel?”

I like the question itself. It fits the product's philosophy: the app wants to learn what someone enjoys, not just which landmarks they recognise.

But it is a relatively demanding question for the second step. I have barely used the app, and it is already asking me to recall a personal experience, organise that memory into words, and decide whether to speak or type.

A person who is tired, in a hurry, or simply not good at describing feelings might stop here.

What I would do: keep the question optional, provide a short example answer near the input, and explicitly say that a few words are enough. I would also consider moving it after the simpler place and feeling questions, when the user already understands the app better.

The “Tell it instead” voice option is a nice alternative to typing. However, the statement “The sound isn't saved or sent” is an absolute privacy promise. Verify that it is true for the actual speech-to-text implementation on supported iOS and Android devices, including the languages you support. If the operating system's speech service processes audio, the copy needs to describe that accurately.

#### Screen 5 — How you want to feel

This screen works well.

“Restored”, “Excited”, “Connected”, “Curious” and “Peaceful” are understandable enough to choose from, while the supporting descriptions make them less abstract.

The layout offers the right kind of simplicity: a limited set of feelings, a clear instruction to select one or two, and plenty of space between the options.

My two minor reservations:

1. “None of these” is much quieter than the main choices. Someone who doesn't identify with the listed feelings should be able to reject them without searching for a small footer link.
2. Make sure selected states remain visible when a user taps an option and then returns to the screen. The screenshots do not establish whether those states are implemented clearly.

The question itself should stay.

#### Screens 6 and 6b — Places you've been / Kinds of places

The photograph-led layout makes these questions much easier to answer than a plain text list would.

For someone familiar with London, choosing whether they loved, tolerated, disliked or haven't visited a place is straightforward. The immediate response, such as “Got it: big museums full of history”, gives the app a little personality without forcing a conversation.

One point needs checking: in screen 6, all four choices look visually similar in the displayed state, despite the feedback line beneath them. If a selected answer is meant to persist there, make it much more obvious with a clear fill, checkmark or border.

The visitor version is a sensible alternative because someone who has never visited London should not have to evaluate a series of unfamiliar attractions.

However, the pack describes eight kinds of places for visitors, compared with six individual places for people who know London. That risks making the unfamiliar visitor do more work.

I would use fewer, broader preference questions for visitors and allow the app to refine the plan later. A person visiting from abroad may have limited knowledge of London; the onboarding shouldn't punish them for that.

#### Screen 7 — This or that

This is one of the most engaging questionnaire designs in the pack.

Two imaginary days are compared using tangible details: transfer time, weather, number of stops, pace, cost and walking distance. “There are no wrong answers” helps reduce the feeling that there is a correct response.

It also collects preferences that people may struggle to describe directly.

My concern is the amount of reading involved. The cards are attractive, but each comparison is information-dense. If a user sees several versions of this screen, the activity could begin to feel repetitive.

The counter shows “Question 10 of 14”. I read that as the first of five comparison decisions, following the earlier questions and place ratings. If that is correct, I would test whether five comparisons actually provide enough extra information to justify the time. If it is just one decision, the remaining count needs to become more understandable.

Suggested improvement: use two or three strong comparisons initially, then stop when ODYS has enough information to build a reasonable first plan. Collect more preferences later if necessary.

The “No preference” option is valuable. Keep it.

### 4. Understanding the answers and getting the first plan: screens 7b–9d

#### Screens 7b and 7c — So far, I've learned…

This is an excellent idea, and I would keep it.

Showing the user's answers in ordinary language, without numerical personality scores, is reassuring. Letting them mark individual statements “Not right” and undo the change gives them control over what the app believes.

That is important because a recommendation system will inevitably make mistakes.

However, some of the statements sound more certain than the evidence may justify.

For example:

> “Borough Market wasn't for you.”

If the user explicitly said they disliked Borough Market, that is fine. If the app inferred that from a choice between two hypothetical days, the statement is too definite.

I would say something like:

> “You tended to choose days that didn't include Borough Market.”

Or, if the evidence is weaker:

> “You might prefer a day without Borough Market.”

That distinction matters. The screen promises to reflect the person's own answers; it should not quietly turn an inference into a fact about them.

I would also make sure the “Not right” controls and Undo interaction are easy to understand on the first attempt. The underlying concept is strong.

#### Screen 8 — Plan a day

This is the clearest visible consistency problem in the whole pack.

The date shortcuts include “Sat 24 Oct”, but the date field displays “31 Oct 2026”. The pack is dated 19 October 2026, so the next Saturday is 24 October, not 31 October. The copy also describes the default as next Saturday.

There may be a reason for the different date, but the screen does not explain it. To a user, it looks like the default selection and date field disagree.

The date must be consistent across the shortcut buttons, selected date, generated plan, stop schedule, map and forecast.

The rest of the screen is quite good. Time, number of stops, starting area and a required-place option are all useful, and the amber “Make my day” button clearly indicates the main action.

I would make two further changes:

First, make the default pace personal. In the example profile, the user repeatedly prefers relaxed days with fewer stops. A default of four stops over five hours may be reasonable, but it should not contradict the preferences the app has just summarised. Consider letting pace and stop count influence the default, while keeping the controls editable.

Second, simplify the location decision. “Charing Cross” and “Where I am” make sense as alternatives, but explain what selecting “Where I am” will do before asking for device permission.

The most important improvement here is not another design flourish. It is ensuring that the form's defaults are correct and visibly connected to the user's answers.

#### Screens 9a–9d — Your day

The result screen has a lot going for it.

The title, such as “A curious, peaceful day”, is much more inviting than a generic itinerary heading. The cost, walking distance, finish time, weather, stops and personalised explanations are all useful.

The chart under “How the day moves” is visually attractive, too. It communicates a sense of progression rather than presenting the day as a flat checklist.

There are three problems I'd address.

##### A. The notification prompt arrives too early

The prompt asking “A nudge to rate each stop after you leave?” takes up a considerable part of the plan overview.

I'd rather see my plan first. I have just answered a long series of questions, and I want to find out whether the result is any good before deciding whether to enable rating reminders.

Keep the option available, but consider moving it until after the user accepts the plan or starts the day. A small reminder setting on the plan screen would also be less intrusive.

##### B. The curve is not self-explanatory

“Higher means we think you'll enjoy it more” is helpful, but the curve has no numerical scale. I can tell which moments the app expects to be stronger, but I cannot tell how uncertain those estimates are or what a meaningful difference between two points looks like.

You don't necessarily need a traditional statistical chart here. I would try a simpler visual timeline with descriptive cues, or add a short explanation that makes it clear these are estimates, not promises.

##### C. The map must behave like a map view

Screen 9d is described as “Your day, on the map”, with numbered pins. Yet the screenshot looks almost identical to the overview above the fold, with the map/list control far down the page.

If selecting “Map” leaves the user at the same top section, they may believe nothing happened.

When a user switches to Map, show the map immediately or move the viewport to it. The map should visibly be in control of the screen rather than hidden beneath the summary and chart.

Also add enough bottom padding to ensure the itinerary and chart are not obscured by persistent navigation.

### 5. The personal-value estimate: screens 9a and 10

This deserves its own discussion because it is one of ODYS's most interesting—and most potentially confusing—ideas.

The screen says:

> “Worth about £32 to you · Free entry”

And below it:

> “A first estimate from what you've told us so far.”

I understand the intended idea: a free attraction can still be valuable to a particular person, and ODYS is trying to estimate which experiences are worth their time.

That is interesting. But my instinctive reaction as a user would be: “How do you know that this moment is worth £32 to me?”

It also puts two kinds of value side by side: the amount the experience may be worth to me and the amount I actually need to spend. The distinction isn't immediately clear.

I would test a version that says:

> Estimated personal value: about £32

> This is an early estimate of how much this experience may be worth to you, based on what you've told us. It isn't the ticket price or a promise of how you'll feel.

Then offer a small “How we estimate this” link.

If the estimate is experimental, say so. If the method is genuinely validated, the explanation can be more specific.

I would not remove this feature without testing it first. It could become a distinctive part of the product. But it needs to feel like a helpful insight rather than a strangely precise judgement about somebody's internal preferences.

### 6. The actual day out: screens 10–12b

#### Screens 10 and 10a — A stop and the way in

This is where ODYS starts to feel genuinely different.

The full-width photograph, descriptive title, reason for choosing the place, estimated value and arrival path are a strong combination. I particularly like the “From”, “The way in” and “You arrive” structure.

That is a useful level of specificity. It helps a person picture the experience and navigate toward it, rather than merely telling them which landmark to visit.

My main suggestion concerns the directions.

The Garden at 120 example gives several possible stations and transport choices in the same paragraph. That is useful information, but it creates another decision for the user at the moment they need to navigate.

I would show one recommended route first, with a clearly labelled directions action. Alternative routes can sit below it or behind a secondary control.

The timeline-style arrival path is attractive, but the hollow circles alone do not make it completely obvious that each step is tappable. Add a small prompt such as “Tap a step for directions”, or a more explicit arrow/chevron treatment.

The “reveal” concept is compelling, especially when connected to the best time and light. Keep that. It helps explain why timing and arrival matter to ODYS.

#### Screens 10b and 10c — Now and the day done

The “Now” concept is appropriate for a person who is actually out. The screen focuses on the current place, the next stop and the option to finish the current stop, while promising not to interrupt unnecessarily.

That restraint is good. I would not turn ODYS into a chatty assistant that constantly asks how the user is doing.

However, on Android, the location-permission prompt shown in screen 10b takes up a substantial area at the top of the page. It pushes the stop information down, just when someone may be standing outside a venue or trying to work out where to go next.

I'd keep the contextual permission request, but make sure the current stop and the key action remain accessible. Asking for permission should not feel like a barrier to using the day plan.

I would also review the “I'm done here” button. It is clear enough, but a secondary way to skip a stop or adjust the plan would help when the user is tired, the place is unexpectedly busy, or the weather has changed.

Screen 10c's “Preview tomorrow: Day 3” is a good continuation for a multi-day trip. It makes the app useful beyond the current moment without forcing the person to start planning another day from scratch.

#### Screen 11 — Rating

The rating screen is beautifully restrained. It takes a single tap to tell ODYS how a stop felt, and the arch filling with light makes the interaction feel connected to the product identity rather than like a generic survey.

But two things need attention.

First, the scale is:

- Flat
- Fine
- Good
- Great
- Unforgettable

“Flat” may not communicate dissatisfaction or low enjoyment clearly enough. It can mean boring, emotionally neutral or simply ordinary. I would test this label against a more directly understandable option such as “Not for me”, without assuming that the alternative is necessarily better.

Second, the iPhone screenshot doesn't show a clear Skip option on this screen, while the Android screen includes “Close”. Someone may not be ready to rate a place, may be interrupted, or may simply want to continue. Rating should be easy, but it shouldn't feel compulsory.

Provide a consistent, low-friction skip or dismissal action on both platforms.

#### Screens 11a and 11b — Thank-you and share card

The share card is a strong visual asset. It combines the user's rating, a photograph, the place title and a reason related to their own preferences.

“Planned with ODYS” works well as a quiet attribution. It doesn't feel like an advertisement demanding attention, and the decision not to publish the app's monetary estimate on the card is sensible.

The “Send to a friend” option is also more human than a generic share icon alone.

I would only make sure the card preview shows exactly what will be shared, including any personal wording and rating. People should be able to understand the content before opening the system share sheet.

There is also a small copy issue in screen 11a:

> “Thank you for going.”

I understand it, but it sounds unnatural in everyday English. “Thanks for visiting” or “Thanks for giving it a try” would sound more conversational.

The thank-you screen should make the benefit of the rating clear, rather than sounding like a formal acknowledgement.

#### Screen 12a — Improve future plans

The screen says “Make your next day even better?” and offers roughly 30 seconds of optional questions. The tone is friendly and it explicitly allows the user to say “Not now”.

The problem is timing.

A person has just visited a place and submitted a rating. They may want to continue to the next stop, sit down for lunch or put their phone away. Another short questionnaire—even an optional one—can feel like an interruption.

I would offer it once the day is finished, or keep it accessible from the plan page. ODYS can collect further preferences without interrupting the actual outing.

### 7. Help, safety and privacy: screens 13–14b and 33

#### Screen 13a — Help & safety

The red emergency section is easy to distinguish from the rest of the screen. “Call 999” is prominent, and the separate NHS 111 option is useful for non-emergency medical help in the UK.

Separating emergency information from the “I feel unsafe or something's wrong” form is a good decision. A user should not have to search through a message form in an emergency.

My concern is the language around the human response:

> “Abram, or whoever is covering for him. They'll reply within a few hours.”

It is honest, but it also makes support sound uncertain and dependent on one person. In a safety-related context, that is not reassuring.

I would use clearer wording, such as:

> Contact the ODYS team

> A person will read your message and reply here, usually within a few hours.

Only use that promise if it reflects the real support arrangements. If the service isn't monitored at all times, say so explicitly.

The UK emergency instructions also need to stay clearly labelled as UK-specific as the trip feature expands beyond London. An emergency number should correspond to the user's current trip destination; UK-only guidance must not be presented as universal advice.

#### Screens 13b and 13c — Reply

The acknowledgement and in-app reply flow is thoughtful. The user knows the message has been received, who is expected to respond and where to look for the reply.

That's much better than a generic “Message sent” confirmation that leaves them wondering whether anything happened.

Make sure users can return to the reply thread easily, and that a visible notification indicator is not the only way to discover a response.

#### Screens 14a and 14b — Your data and deleting it

These screens are a positive part of the product.

The data explanation covers what ODYS stores, what is kept on the phone, how the app handles selected starting points and what happens to contact details supplied through help. The deletion screen states that deletion is immediate and irreversible, and requires the user to type DELETE.

That creates a sense of control.

The main weakness is the density of the “What we store” paragraph. There is a lot of valuable information, but the text is difficult to scan.

I'd turn it into a concise list of key points—what stays on the phone, what gets sent to providers, how contact details are used, and how to delete everything—with expandable explanations beneath each.

I would also clarify this distinction:

- Live GPS location is not stored.
- A starting point chosen for a plan may be sent in rounded form to generate the plan.

Those statements can both be true, but a user may not immediately understand the difference.

Finally, make sure the privacy language about voice input accurately describes the technology used across both platforms, as noted earlier.

#### Screen 33 — You

The “You” screen has a useful order: emergency help first, a way to contact a person, what ODYS has learned, and then data information.

The area that worries me is the bottom of the screen. The floating navigation bar appears to overlap content, and the “Your data” entry is partly hidden.

That is not merely a small spacing issue. It makes a privacy control harder to discover.

I would add appropriate bottom content insets on every scrollable screen with persistent navigation. A user should be able to scroll far enough to read and tap the last item without it hiding behind the tab bar.

Also, the “Talk to a person” card looks like an informational panel. If it opens the help flow, make that action obvious with a chevron, button label or other clear affordance.

### 8. Plan comparisons and the trip-building flow: screens 15–25b

#### Screens 15–18 — Plan 1 or Plan 2?

The comparison exercise is a well-considered research feature.

It lets the user compare two possible days for the same Saturday, without photographs, maps or reasons that could reveal which is personalised. That is a sensible way to reduce visual bias in the experiment.

The additional questions about pace, company and essential requirements also make sense, particularly if the app is testing whether personal preferences produce a better plan.

The chosen plan is identified after the user's decision, rather than before it. That is a good choice for a fair comparison.

My concern is the length of the comparison screens. Reading two complete itineraries can take time. Make sure the most decision-relevant information is easy to compare: start and finish, pace, stops, approximate spend, walking and transfer times.

The post-choice explanation that one plan was made from the user's answers and the other is a strong general day is clear. It could sound slightly dismissive of the general plan, but because it comes after the choice, it does not pre-bias that decision.

#### Screens 19–25b — Trips and days

The three-tab structure—Trip, Book and You—is simple enough to understand. The trip overview then moves through dates, how to get there, the trip's general feel and the itinerary.

The itinerary itself is useful. Arrival and departure logistics are treated as part of the experience, and labels like “Saved, not booked” and “Booked” are clearer than leaving the user to infer a reservation's status.

I particularly like screen 25b, “Change this day”. Being able to rearrange one day around a meeting or changed plans without rebuilding the entire trip is an excellent practical feature.

A few details need refinement:

Date ranges. The date picker should explain which dates represent the destination stay and which represent the outbound journey. The sample flight leaves Tashkent on Wednesday 21 October and arrives in London on Thursday 22 October. That is perfectly plausible for an overnight flight, but the heading “Thu 22 Oct – Tue 27 Oct” can be read as the dates on which both flights depart. Use “Arrive in London Thu 22 Oct” and show the outbound departure date separately.

Airport travel. Screens 25 and 25a provide useful departure times, transfer estimates and directions. Those are genuinely helpful details. However, the itinerary should distinguish an estimated travel duration from a recommended departure time, and make the buffer before the flight easy to understand.

The “Book” tab. Because ODYS sends users to external providers rather than completing the booking inside the app, keep that distinction visible before they leave. The screens already do a good job explaining that they pay the provider directly; I would preserve that transparency consistently.

### 9. Flights, accommodation and maps: screens 26–32

This is the part of ODYS where accuracy matters most. A slightly confusing recommendation is annoying; a confusing flight date or accommodation price can lead to a much more consequential mistake.

#### Screen 26 — Flights

The flight results are well organised. The Best, Cheapest and Fastest options let users orient themselves quickly, while the flight cards show departure time, duration, route, return fare and luggage information.

The “Sample results, made up for testing; not real flights or prices” notice is important and should remain visible.

I would reconsider the label “Best”, though. Cheapest and Fastest are measurable, but Best is a value judgement. A user may reasonably wonder whether it means shortest overall, lowest cost per hour, best schedule or a mixture of factors.

“Recommended” with a short explanation of why is a little clearer.

#### Screen 27 — Flight filters

The filter layout is functional, but the sliders showing “Any” don't make it clear what the user gets when they move them.

For “Longest journey”, show the selected maximum in hours. For “Most I'll pay”, show the currency and the selected price. These values should change visibly as the slider moves.

Do the same for the accommodation budget slider on screen 31.

This is a small change with a substantial practical benefit. A filter shouldn't require the user to guess where they've left the limit.

#### Screen 28 — A flight: where to book

The flight-detail screen gives the outbound and return legs, luggage, the found price and the booking provider. It also explicitly explains that ODYS earns nothing from the links.

That is good trust-building.

However, the sample date issue described above is worth treating as a data-quality problem, not just a copy issue. All route summaries, flight legs, trip dates and saved itineraries should use a consistent underlying source of truth.

The same applies to fare data. If prices are samples, all relevant places should indicate that clearly, rather than relying on users to remember a disclaimer from another screen.

#### Screens 28a and 28b — Leaving for the provider and returning

This is a thoughtful flow.

Before leaving ODYS, the user sees which provider they're opening, the price found, when it was found and that they pay the provider directly. On return, they can confirm that they booked the flight or keep it saved for later.

This is much better than simply opening a browser and hoping the user remembers to update the trip.

I would preserve this pattern for accommodation bookings too.

#### Screen 29 — Places to stay

The sort choices and filters are useful. “For your days”, “Cheapest” and “Top rated” give the user different ways of approaching the decision.

“For your days” is a little vague, however. I would try “Best fit for your trip” or “Best fit for your itinerary”, with a brief explanation of how it is selected.

The sample accommodation listing has another issue: the property image area looks like an empty gradient placeholder. In a hotel search, a photo is a major part of deciding whether a place looks acceptable.

For the final build, use real, correctly attributed imagery where permitted, or an obvious “Photos unavailable” fallback. A blank gradient can look like a loading failure.

#### Screen 30 — Places to stay on the map

The map itself is a useful addition, especially when a traveller is choosing a property relative to their itinerary.

The price markers, however, appear crowded around central London. They overlap enough that identifying and tapping the right one may become difficult.

I'd look at clustered price markers or a selected-property panel that clearly connects the pin to its listing.

I would also run a list-versus-map consistency test. The visible list and map samples appear to contain different price values; that may reflect different selected properties or sample states, but the live app should make the relationship unmistakable.

A user should never have to wonder whether a map marker represents the same property whose price and details they just read.

#### Screen 31 — Stay filters

The controls cover the right things: budget, type of place, guest rating, free cancellation and breakfast.

The same slider issue from flights applies. Display the selected budget and currency rather than just “Any”.

I would also make selected and unselected filter states unmistakable, particularly for users who have low vision or who are viewing the screen in bright daylight.

#### Screen 32 — A place to stay

The accommodation detail page includes the rating, distance, room and rate, total cost, cancellation terms and external booking links.

That is the correct general structure.

The sample property shows an 8.4 rating and 2,055 guest reviews. Since the pack identifies the listing as a made-up testing example, these look like fabricated social-proof figures. For a prototype, I'd label the entire listing and its metrics explicitly as demo data—or remove fictional review counts and ratings.

Otherwise, the card is visually close enough to a real booking result that users may unconsciously treat the rating as evidence.

For a future live product, every rating, review count, rate, cancellation term and booking link needs to be grounded in the actual provider's data. The interface already creates a useful foundation for presenting those details.

### 10. Visual design, accessibility and iOS/Android consistency

The overall visual language is one of the strongest things about ODYS. I would protect it rather than try to make every screen look more conventional.

The amber is used sparingly enough to signal important actions, the dark background provides a consistent canvas, and the serif headings give the product an editorial quality. Photos are doing real work rather than being purely decorative.

There are still some details to test on actual devices.

#### Typography and contrast

The main text looks comfortable in the screenshots, but smaller secondary text is much less prominent: footnotes, data descriptions, image credits and some helper links.

I cannot reliably measure the actual contrast ratio from the screen-pack images alone. I would test the real colour values rather than judge by appearance. Android's current accessibility guidance recommends at least 4.5:1 contrast for text, and scalable type rather than fixed text sizes.

Test the app at larger system font settings too. ODYS uses several long serif headings, and those can wrap into more lines than expected when text is enlarged.

#### Buttons and tap targets

The main amber CTAs are large and easy to recognise. Several secondary controls need the same scrutiny: “Skip”, “None of these”, the small top-right Help and gear controls, and the plus/minus buttons used to change the number of stops.

Apple's guidance recommends a hit region of at least 44 × 44 points for typical iOS controls, while Android recommends touch targets of at least 48 × 48 dp. The screenshots are not sufficient to confirm that the implemented hit regions meet those dimensions, but these are the first controls I would check.

Also verify that custom buttons show a clear pressed state. A beautiful control that doesn't visibly respond feels broken.

#### Motion and the arch

The arch animation is a good brand element. The light rising through the arch is memorable and fits the product's idea of discovery.

Keep the motion restrained. The screenshot pack describes the initial animation as about one second and the plan reveal as 2.6 seconds, once. That sounds reasonable, but the reveal should never feel like an artificial loading delay, and users should have a way to reduce non-essential motion.

The app should feel calm, not as though it is making somebody wait for an animation.

#### Differences between iPhone and Android

The brand is recognisably the same across both platforms, which is good. The map provider and directions behaviour can legitimately differ, and the use of platform-specific controls is sensible.

There are nevertheless a few inconsistencies worth fixing:

- The Android “Now” screen shows the location-permission prompt occupying a large part of the page; the corresponding iPhone screen doesn't show the same interruption.
- Android shows a Close control on the rating screen, while the iPhone version does not visibly provide the same option.
- Persistent navigation sometimes covers the bottom of content in the Android screenshots, while some deeper iPhone screens hide the navigation completely.
- Small action names and screen structures vary. Differences that help a platform feel native are good; differences that change the available action or hide content are not.

I would not force a perfect pixel-for-pixel match. I would insist on the same underlying behaviour, clarity and accessibility on both platforms.

### 11. Copy changes I'd make immediately

The visual style is already distinctive, so I would avoid rewriting everything. A handful of small wording changes would make the product feel clearer and more natural.

| Current wording                                                   | Suggested alternative                               | Reason                                                      |
| ----------------------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------- |
| “Thank you for going.”                                            | “Thanks for visiting.”                              | More natural, conversational English                        |
| “Borough Market wasn't for you.”                                  | “You tended to choose days without Borough Market.” | Distinguishes inference from an explicit dislike            |
| “Worth about £32 to you.”                                         | “Estimated personal value: about £32.”              | Makes the type of estimate clearer                          |
| “Best” (flight sorting)                                           | “Recommended”                                       | Avoids implying an objective meaning of “best”              |
| “For your days” (accommodation sorting)                           | “Best fit for your trip”                            | Communicates the basis of the recommendation more naturally |
| “The way in” with several transport alternatives in one paragraph | “Recommended route” plus “Other routes”             | Reduces the number of choices at the point of navigation    |

The goal is not to make ODYS sound like a generic travel app. It's to make the existing voice easier to understand.

### 12. One additional issue: weather confidence

The day plan for Saturday 31 October displays “about 12°C, 20% chance of rain” and attributes the forecast to the Met Office.

The screen pack is dated 19 October, so the plan is 12 days ahead. The Met Office explains that detailed prediction becomes more difficult beyond seven days and that the days 8–14 outlook should communicate uncertainty and ranges of possible outcomes.

That means I would not present this as a precise, dependable forecast without a clear confidence treatment. The problem isn't that 12°C or a 20% rain probability is necessarily impossible. It is that the screen does not tell users how much confidence to place in those numbers at that lead time.

Since weather is part of ODYS's planning proposition, this is worth getting right. An early outlook can still help the user choose outdoor versus indoor moments, but it should be labelled as an outlook and updated nearer the day.

### 13. What I would keep exactly as a product direction

A lot of this review has focused on the things to fix, so I want to be clear about what I would protect.

First, the arrival experience. The “From / The way in / You arrive” structure is one of ODYS's strongest features. It makes the app's idea of a moment feel real and practical.

Second, the explanation of why a place was picked. “You loved the view from the top of Greenwich Park, and this has a big reveal too” is much more convincing than a generic statement that a location is highly rated. It connects a recommendation to something the user actually said.

Third, the control given to the user. They can correct learned preferences, adjust the pace of their day, set a place that must be included, change a day without rebuilding the entire trip, skip many questions, and delete their data. These are all good product choices.

Fourth, the restrained visual identity. The app does not need more decoration, extra gradients, or an elaborate animation on every screen. Its strongest quality is its calm, consistent presentation.

### 14. What I would test with real people first

Before investing in more animations or polishing secondary screens, I would run five short usability tests around these specific tasks.

#### First test: can they get to a plan?

Ask a new user to start ODYS and make their first day without help. Measure whether they finish, where they hesitate, whether they skip the personal-memory question, and whether the stated three-minute expectation feels accurate.

#### Second test: do they trust the result?

Show the completed day and ask them to explain, in their own words, why ODYS chose each stop and what “Worth about £32 to you” means. Don't explain the labels in advance.

#### Third test: can they navigate on the day?

Ask them to find the next stop, identify the route into it, switch to the map and finish a stop. Check what happens when they decline location permission or want to skip a rating.

#### Fourth test: can they check a trip confidently?

Give them a flight and accommodation example. Ask them to tell you when they leave, when they arrive, what is booked, what is merely saved, the total cost and where they would pay.

#### Fifth test: do they understand the privacy promises?

Ask what stays on the phone, what is shared with providers, how location is used and how they would delete their data. Their answers will reveal whether the current explanations work without extra interpretation.

For these sessions, I would resist the temptation to guide people when they hesitate. Watch first. A moment of hesitation is useful evidence; an explanation from the facilitator can conceal the very issue you're trying to find.

#### My final recommendation

Don't redesign ODYS. Tighten the product.

Keep the arch, typography, amber palette, example-day storytelling, arrival paths and personalised reasons. Reduce the friction before the first plan, fix the date and safe-area inconsistencies, make the personal-value estimate easier to understand, communicate uncertainty in weather and demo data, and standardise the important interactions across platforms.

The biggest opportunity is to make ODYS feel as thoughtful in its behaviour as it already looks visually.

Right now, the screens communicate care and personality. The next step is making every action, recommendation, price and date dependable enough that users can stop thinking about the interface and concentrate on having a good day.
