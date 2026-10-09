# UX checklist: every question, answered for ODYS (9 Oct 2026)

**Decision first:** of 107 questions, **68 pass**, **23 are partial**, **6 failed and are fixed** (five fixes, build 68), and **10 don't apply yet** (no accounts, payments or ads). Nothing is left failing. The partial ones are either on the after-9-Nov list, waiting for the paid server (decision 1), or to be measured in Test B.

**Where it came from:** Abram pasted five UX research notes and checklists (Hick, Fitts, peak–end, Zeigarnik and goal gradient, micro-frustrations and dark patterns), one of them written for "Days Out", this app's earlier name. Their questions are merged here without duplicates and answered from the code and the decision log. **Their statistics and customer quotes are not repeated:** they weren't checked in this session, and some say they are composites (rule 1). Checks that need the phone are marked for Abram's phone pass.

**Hours:** Claude ~3 h for the audit and ~1 h for the fixes (GUESS). Abram: 0 h, plus the phone checks already on his list.

**Fixed today (build 68, m181):**
1. Swipe back from the left edge now works on the five screens that draw their own "‹ Back".
2. The long-press "Swap this stop" on the plan list asks first, like the card's button.
3. "Something wrong with this place? Tell us" on every stop opens Help & safety with the place's name filled in.
4. The "Call 999" red is darker, so its white text is 4.9:1 (was 3.9:1).
5. "Regenerate" is now "Plan again".

**Verdicts:** Pass · Partial · Fixed today · N/A (not yet relevant). **Next** says who acts, when anything is left.

## 🧠 Cognitive load and clarity (First impression and navigation)

25 questions: 19 pass, 3 partial, 3 fixed.

| # | Question | ODYS | Answer | Next |
|---|---|---|---|---|
| 1 | Can a first-time user say what the app does within 5 seconds of the first screen? | Pass | The welcome screen says "Days out that fit you. Tell me how you want a day to feel. I'll plan real moments around it, including how you arrive." |  |
| 2 | Does each screen have one clearly dominant main action? | Pass | By design: one amber button per screen ("Show me an example day", "Start the day", "Plan a trip"); everything else is outlined or quiet text. |  |
| 3 | Can people see something useful before a long onboarding? | Pass | "Show me an example day" comes before any question, and can be skipped. |  |
| 4 | Does onboarding ask only for what improves the first plan, and is it short? | Partial | 14 questions, then (for people in the UK) 3 optional survey questions and the Plan 1 / Plan 2 comparison: about 21 taps, roughly 5 minutes (my estimate), before the person's own day. Test B needs these answers. The food and "where did you grow up" questions are already gone (D123). | Test B / friends' round: Measure the real time to first plan in Test B; shorten afterwards (adaptive questions are on the after-9-Nov list). |
| 5 | Can optional personalisation be skipped, with a useful result anyway? | Pass | "Skip the rest" on the places and this-or-that steps; the survey is optional; the comparison has "Not now". |  |
| 6 | Are preferences asked in small, clear groups rather than one long list? | Pass | Five steps, one question per screen, with "Question 7 of 14" and a progress line. |  |
| 7 | Does any screen ask people to weigh more than about 5 equal options at once? | Pass | Reactions have 4 choices, scales 5, times of day 4. The flight list is long, but it opens sorted, with Best, Cheapest and Fastest tabs, tags and filters. |  |
| 8 | Is the bottom navigation 5 tabs or fewer, each with a text label? | Pass | Three tabs, Trip, Book and You, each with a word under the icon. |  |
| 9 | Is every main feature within 2 taps of home? | Pass | Plan a trip, your day, your trips, Help and Your data are each one tap from the Trip tab. |  |
| 10 | Are labels in the words people use, with no jargon? | Fixed | Mostly plain already. "Regenerate" was a tech word: it is now "Plan again" ("Plan this day again" in the confirmation). "Fits me" and "worth about £V to you" are worth listening for in Test B. | Fixed in build 68 |
| 11 | Do icons carry text labels? | Partial | Every tab has a word. One icon-only button, the gear for "Your data", has a VoiceOver label but no visible word; the same link is written out at the bottom of the You tab. |  |
| 12 | Is body text at least 16 px, with 4.5:1 contrast? | Pass | Body text is the system's 17 pt and grows with the phone's text size. Measured today, every text colour is at least 4.5:1 on its background: ink 15.7:1, labels 7.1:1, tab labels 5.2:1. Secondary lines are 13–15 pt. |  |
| 13 | Does every button pass contrast? | Fixed | One didn't: white on the red "Call 999" button was 3.9:1. The red is now D0363B, so the text is 4.9:1 and the button still stands out at 3.3:1 against its card. | Fixed in build 68 |
| 14 | Does it stay readable with large text sizes and Reduce Motion? | Pass | Fonts scale with Dynamic Type, the day's curve gives each label its own row at accessibility sizes (m178), and Reduce Motion turns off all movement (D117). | Abram's phone check: A full large-text and VoiceOver pass is still on Abram's phone-check list. |
| 15 | Does every empty state say what to do next? | Pass | Book with no trip: "Plan a trip first…" with one button. No flights match: "Clear filters". You, before any ratings: "Nothing yet. It comes from your answers and your ratings." |  |
| 16 | Is there search or filtering wherever there's a list? | Pass | Flights and stays have filters and sort tabs; "Must include" has "Search places". |  |
| 17 | Can people always tell where they are and how to go back? | Fixed | Every pushed screen has a written "‹ Back" and every sheet a "Close". But five of them (a day, a trip, a trip's day, a flight, a stay) hid the navigation bar, which on iOS also turns off the swipe from the left edge. The swipe now works on every pushed screen. | Fixed in build 68 |
| 18 | Does each recommendation say why it suits this person? | Pass | "Why this fits you" on every stop. It's hidden only on the blind Test B plan, on purpose. |  |
| 19 | Can places be compared on cost, time and location? | Pass | Each stop shows its times, price and how you get there; each plan shows the total per person. |  |
| 20 | Are travel times shown where they affect the choice? | Pass | A travel line before each stop ("about 12 min on foot from…"), and the trip's journeys with times. |  |
| 21 | Is the pace of the day clear without opening every stop? | Pass | "How the day moves" (a curve with a word per stop) and "£21 per person · 2.4 km walking · Done by 17:00". |  |
| 22 | Are confirmed facts told apart from estimates? | Partial | Card facts carry a "Checked" date, sample and test prices are labelled, and travel says "about". The travel times are our own estimates until live TfL times arrive with the paid server (roadmap Stage 1). | Abram's decision: The paid server is Abram's decision 1. |
| 23 | Do the map and the list agree? | Pass | Both are drawn from the same stops, numbered the same. |  |
| 24 | Is only one interruption shown at a time? | Pass | One alert at a time (a notice waits while an error shows); the reminder question is asked once, after a plan. |  |
| 25 | Do people never have to remember something from an earlier screen? | Pass | Each step of "Plan a trip" repeats the trip so far (dates, travellers). |  |

## ✋ Physical and motor ergonomics (Thumb zone and interaction)

16 questions: 9 pass, 5 partial, 1 fixed, 1 n/a.

| # | Question | ODYS | Answer | Next |
|---|---|---|---|---|
| 1 | Is every tap target at least 44 × 44 pt (48 × 48 dp on Android)? | Pass | Buttons are 48–56 pt tall. Chips, the Help pill and the gear are drawn at 36 pt inside 44 pt tap areas (m178). Android doesn't exist yet (after-9-Nov #67). | Abram's phone check: Abram's phone pass catches anything missed. |
| 2 | Is there at least 8 pt between neighbouring targets? | Pass | Button stacks use 10 pt gaps; chips and tiles 8 pt. |  |
| 3 | Are main actions in the bottom half, within thumb reach? | Partial | Onboarding, the plan's "Start the day" and rating sit low. "Plan a trip" is near the top of the Trip tab, and "Close" is top-right in sheets (the iOS convention; sheets also close with a swipe down). |  |
| 4 | Are destructive actions separated from common ones, and deliberate? | Fixed | "Delete my data" needs DELETE typed; removing a trip, swapping a stop and planning a day again each ask first. The long-press "Swap this stop" on the plan list swapped at once: it now asks first, like the card's button. | Fixed in build 68 |
| 5 | Does each field bring up the right keyboard and autofill? | Partial | The tester code uses capitals without autocorrect, places use word capitals. The reply contact is one field for "phone or email", so it can't open both keyboards; it suggests your phone number. |  |
| 6 | Does the keyboard never cover the field or its button? | Pass | The pages scroll the active field into view, and the keyboard closes when you scroll. | Abram's phone check |
| 7 | Does every gesture have a visible button too? | Pass | The calendar's sideways swipe also has month arrows; the places are buttons, not swipes; the long-press swap repeats the card's button; the edge swipe repeats "‹ Back". |  |
| 8 | Do custom swipes avoid clashing with the system's edge gestures? | Pass | The only custom swipe is on the calendar card, inside the page. |  |
| 9 | Does every tap give feedback within 100 ms? | Pass | Every card and tile shrinks slightly as it's pressed (120 ms), and main buttons and tiles give a light tap of haptics. |  |
| 10 | Are double taps unable to submit twice? | Pass | Buttons are disabled while a request runs, and say so ("Sending…", "Deleting…"). |  |
| 11 | Can the three most frequent actions be done one-handed? | Partial | Rating a stop, "Start the day" and moving through onboarding are low on the screen. Help and "‹ Back" are top corners; going back is now also an edge swipe. |  |
| 12 | Can stops be reordered without drag, or removed without losing the day? | N/A | There's no manual reordering: the planner orders stops by route and opening hours. A stop can be skipped on "Now" or swapped, and the rest of the day stays. |  |
| 13 | Is there a one-tap way back to the top of long pages? | Pass | Tapping the status bar scrolls to the top, as everywhere on iOS. |  |
| 14 | Are map pins big enough and far enough apart? | Partial | Plan pins are numbered and stays are tappable on the map; not yet checked by hand with a thumb. | Abram's phone check |
| 15 | Can screen-reader users tell what each control does and its state? | Partial | 34 VoiceOver labels; tiles and chips announce "selected"; the calendar names each day. A full VoiceOver pass hasn't been done. | Abram's phone check |
| 16 | Does the layout stay still under the thumb while loading? | Pass | Loading cards hold their space, and the plan's reveal fades in place. |  |

## 🛡️ Safety, trust and error forgiveness (The anxiety fillers)

27 questions: 17 pass, 5 partial, 1 fixed, 4 n/a.

| # | Question | ODYS | Answer | Next |
|---|---|---|---|---|
| 1 | Is the full price visible before any commitment? | Pass | Each plan shows the cost per person and what it's made of (food and entry, Tube or bus). Flights show the return price for everyone; stays show a night and the total. Booking happens on the provider's own site. |  |
| 2 | Are "free" claims checked? | Pass | Card facts are checked against official sources before a card is ready (D91). |  |
| 3 | Are opening hours right for the day of the visit? | Pass | Every stop shows its opening hours (m176), and the planner fits stops inside them. |  |
| 4 | Can people see when a place's details were last checked? | Pass | A "Checked" row on every card (m179). |  |
| 5 | Are temporary closures handled? | Partial | There's no live closures feed. On the day, "Re-plan the rest of today" has "Closed or too busy". |  |
| 6 | Are travel estimates realistic for the way you travel? | Partial | Walking and Tube or bus times are our own estimates, labelled "about", until live TfL times (roadmap Stage 1). | Abram's decision: Needs the paid server (decision 1). |
| 7 | Can people open trusted directions and booking pages? | Pass | "Directions in Apple Maps" on every stop; booking opens Skyscanner, Google Flights, Booking.com, Airbnb or the airline's or hotel's own site. |  |
| 8 | Can people report a wrong price, time or place? | Fixed | Before, only through "Talk to a person" on the You tab. Now every stop ends with "Something wrong with this place? Tell us", which opens Help & safety with the place's name filled in. A person reads it. | Fixed in build 68 |
| 9 | Is there an alternative when a stop isn't available? | Pass | "Swap this stop", and "Re-plan the rest of today" for rain, a closed place, tiredness or changed plans (m179). |  |
| 10 | Is each permission explained first, and asked only when needed? | Pass | Location on "Now", when first useful and only while in use (D123); notifications once, after the first plan; the microphone only when you tap to speak. |  |
| 11 | Does the app work if permissions are refused? | Pass | Yes: no location means no "You're here"; no notifications means no reminders; typing always works instead of speaking. |  |
| 12 | Is data use explained in plain words where it's collected? | Pass | The consent screen, "What we store" in Your data, and the full privacy notice. |  |
| 13 | Can people choose what they share? | Pass | Nothing is shared automatically. The share card holds only the person's own rating and reason, never the model's "worth £X" (D114). |  |
| 14 | No pre-ticked boxes, fake urgency or guilt-trip wording? | Pass | The consent switches start off; there are no countdowns or "only 1 left"; ODYS earns nothing from booking links; "Not now" is neutral. |  |
| 15 | Are subscription prices, trials, renewals and cancelling clear and easy? | N/A | Nothing is sold in the app yet. Prices are tested later on a web page (Test D). When payments come, they need plain terms and cancelling as easy as subscribing. |  |
| 16 | Are ads clearly marked, with a decent close button? | N/A | There are no ads. |  |
| 17 | Can destructive actions be confirmed or undone? | Pass | Swap, plan again, re-plan the rest, removing a trip and deleting data each ask first; corrections in "So far" have "Undo". |  |
| 18 | Do error messages say what happened, why, and what to do, without clearing input? | Partial | Offline and slow-server messages are specific ("You seem to be offline. Check your connection and try again."). A server error says only "The planner answered with an error (500). Please try again." Nothing typed is cleared by an error. |  |
| 19 | Is what people enter kept through going back, backgrounding and timeouts? | Partial | Answers are sent as each step finishes and the step is remembered; plans, trips and ratings are saved on the phone. A half-written Help message or "why" note is lost if its screen is closed. |  |
| 20 | Without signal, is work kept and the situation explained? | Pass | Ratings wait and send later (m175); the day's plan is saved on the phone; the free server's wake-up says "Waking up the planner. This can take up to a minute." |  |
| 21 | After a failure, is it clear whether the action happened? | Pass | Swap, plan again and delete close only when they worked; after a booking link, "Did you book it?". |  |
| 22 | Is a person reachable in 2 taps from anywhere? | Pass | "Help" on every main screen reaches a real person within a few hours, with 999 and NHS 111 at the top. |  |
| 23 | Are rating prompts shown only after good moments, never after errors? | Pass | There's no App Store review prompt. Stop ratings open only after the visit. |  |
| 24 | Are notification settings simple and respected? | Pass | One kind (rating reminders), set on the phone for the plan's day, switched off in Your data any time. |  |
| 25 | Is account recovery and logout simple? | N/A | There are no accounts: the phone has a random code. A reinstall starts afresh (D124); a new phone starts again. |  |
| 26 | Can people get a copy of their data themselves? | Partial | Delete is in the app; a copy is by email (the privacy notice promises a reply within a month). That's fine at test scale. | After-9-Nov #70 |
| 27 | Are security cues shown only at payment and login, and only when true? | N/A | No payments or logins in the app. |  |

## 📈 Momentum, motivation and feedback (Rewards without manipulation)

21 questions: 15 pass, 4 partial, 2 n/a.

| # | Question | ODYS | Answer | Next |
|---|---|---|---|---|
| 1 | Does the first session give a real win within a few taps? | Pass | The example day, before any question. |  |
| 2 | How long until the person's own first plan? | Partial | About 21 taps (roughly 5 minutes, my estimate), so the 60-second ideal isn't met. The example day bridges the wait. | Test B / friends' round: Time it in Test B from the onboarding events. |
| 3 | Are choices acknowledged as they're made? | Pass | A short reaction from the answer itself (D117), then "So far, I've learned…" with "Change something". |  |
| 4 | Do multi-step flows show honest progress? | Pass | "Question 7 of 14" counts every question (D118); "Plan a trip" shows its step too. |  |
| 5 | Does progress never stall, jump back or fake it? | Pass | No made-up progress bars. The plan's reveal starts only after the plan has arrived. |  |
| 6 | Does progress start with a head start (endowed progress)? | N/A | Not used on purpose: no points, streaks or pre-filled bars. |  |
| 7 | Can an unfinished plan be left and picked up later? | Pass | Onboarding reopens at the same question; this-or-that jumps to the first unanswered pair; trips are kept as they're built. |  |
| 8 | Is a short plan not treated as worse than a long one? | Pass | Places a day is the person's choice, and free time is shown plainly. |  |
| 9 | Does every add, swap, save or rating get instant feedback? | Pass | A swapped stop slides in marked "Swapped in"; a rating thanks you and offers the share card; trips save as you go. |  |
| 10 | Are waits shown at once, and long ones explained honestly? | Pass | Loading cards ("Finding flights from…") and "Waking up the planner. This can take up to a minute." A live flight search takes 11–16 s the first time. |  |
| 11 | Are animations brief, non-blocking and off with Reduce Motion? | Pass | Presses and fades take 120–300 ms; the plan's reveal (about 2.6 s) plays once per new plan; all off with Reduce Motion. |  |
| 12 | Is the finished plan a clear, satisfying summary? | Pass | A headline in the person's own words, the day's curve, cost per person, walking, finish time, and why each stop fits. |  |
| 13 | Does every flow end with a confirmation and a next step? | Partial | Plan → "Start the day"; end of a day → "Preview tomorrow"; a booking link → "Did you book it?"; a rating → share. The end of a whole trip has no recap yet. | After-9-Nov #60 |
| 14 | Is there a deliberately designed high point? | Pass | The plan reveal, and the planner's one strong peak per day. |  |
| 15 | Are celebrations proportionate and never in the way? | Pass | Quiet motion only; nothing blocks the next action. |  |
| 16 | Are notifications useful, user-controlled, and never guilt-tripping? | Pass | Only rating reminders, on the plan's day, opt-in; never "We miss you". |  |
| 17 | Do returning users land where they left off? | Pass | "Today in your trip", "Tomorrow: Day N" and "Your day" lead the Trip tab. |  |
| 18 | Can people see their history? | Partial | "What I've learned about you" on You; past days and ratings aren't listed yet. | After-9-Nov #60 |
| 19 | Do badges clear once dealt with? | Pass | The only one, Help's dot for a new reply, clears when it's read. |  |
| 20 | Do streaks forgive a missed day? | N/A | No streaks, on purpose: days out are occasional (calm technology). |  |
| 21 | After planning, can people save, share, edit and start the plan? | Partial | Saved automatically; edited by swap, plan again, add a place or change a day; started with "Now". Sharing a plan with a friend before the day isn't possible: only a rated moment can be shared afterwards. | After-9-Nov #69 |

## 🛑 Real-user friction points (Common drop-off killers)

18 questions: 8 pass, 6 partial, 1 fixed, 3 n/a.

| # | Question | ODYS | Answer | Next |
|---|---|---|---|---|
| 1 | Is there value before any registration? | Pass | There's no registration at all; the example day comes first. |  |
| 2 | Account creation timing, guest access and quick sign-in? | N/A | No accounts. Sign-in options wait until after Test B (D117). |  |
| 3 | Are fields kept to the minimum, with optional ones marked? | Pass | The only typed fields say "(optional)": the Help message and the reply contact. |  |
| 4 | Is autofill supported for names, addresses and cards? | N/A | The app never asks for them. |  |
| 5 | Can dates and numbers be entered without fiddly pickers? | Partial | Dates by calendar (two taps: first and last day; each day has a VoiceOver name); travellers and places a day by labelled − and + buttons; times by menus. There's no typed date. |  |
| 6 | Are permissions asked only when their feature is used? | Pass | Location on "Now", the microphone on tapping to speak, notifications after the first plan. |  |
| 7 | Is the notification request after value, with what you'll get? | Pass | After the first plan: "A nudge to rate each stop after you leave?" with Yes or No thanks first, and iOS's own prompt only after yes. |  |
| 8 | Does going back behave predictably, never trapping or exiting by accident? | Fixed | Onboarding has "Previous", sheets close by swipe or Close, and the edge swipe back now works on every pushed screen. | Fixed in build 68 |
| 9 | Does an expired session keep the person's place? | Partial | There are no sessions. If the server no longer knows the phone (only after a delete), the app says "This phone isn't registered any more. Please start again." |  |
| 10 | Do searches and filters answer within a second? | Partial | Place search is instant. A live flight search takes 11–16 s the first time, then about 15 minutes of instant repeats; filters search again a moment after the last change. |  |
| 11 | Does a forced update block use? | N/A | No forced updates (TestFlight). "Please update the app" appears only if the app can't read the planner's answer. |  |
| 12 | Is it smooth on mid-range phones and with long itineraries? | Pass | Days are 3–6 stops and trips up to 7 days, all on iOS 17 or later. | Abram's phone check: Friends' older iPhones in the TestFlight round are the real test. |
| 13 | Are links to other apps or sites named before they open? | Pass | "Directions in Apple Maps"; the booking step names the site and says "You book and pay on their site… ODYS earns nothing from this link." |  |
| 14 | Does the app say when live information can't be fetched? | Pass | Results are labelled "sample prices" or "test prices" until the real keys are added. |  |
| 15 | Can bad weather, a closure or changed plans be handled without starting again? | Pass | "Re-plan the rest of today" (m179) keeps what's done and re-plans what's left. |  |
| 16 | Are common edge cases handled: groups, one-way or multi-city, flexible dates, access needs? | Partial | Groups: yes, travellers for flights and stays. One-way and multi-city: no (after-9-Nov #68, #14). Flexible dates: no. Step-free and with-kids: no (after-9-Nov #46); only 4 of 51 cards have step-free access checked so far. | After-9-Nov #46 |
| 17 | Are real users watched doing the main task without coaching, and asked what they expected? | Partial | That's the friends' and strangers' TestFlight rounds. Add two questions to the friends' round: "What did you expect to happen when you tapped…?" and "Where did you hesitate?" | Test B / friends' round |
| 18 | Are drop-offs, corrections and complaints tracked? | Partial | Events already cover onboarding done, plans, swaps, plan again, re-plans, skipped stops, shares and booking hand-offs, so time to first plan, completion, share rate and correction rate can be counted. Feedback from Help & safety isn't tagged by theme yet. | Test B / friends' round: Tag Help & safety messages by theme weekly during Test B. |
