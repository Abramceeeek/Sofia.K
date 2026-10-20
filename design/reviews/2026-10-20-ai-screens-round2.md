# AI reviews of the revised ODYS screens, round 2 (20 Oct 2026)

Abram pasted these on 20 Oct 2026 after sending the revised `design/odys-screens.pdf` (with the 19 Oct fixes on Android; the iPhone pictures were still the 18 Oct build). They came as one paste; the breaks between reviewers are marked where the text makes them clear (five parts). Kept as pasted, with headings nested one level down. What was checked and done is in `design/screen-review-synthesis.md` (Round 2).

## Review 1

### What I see in the revised pack

The fixes are real and mostly in the right places. The plan screen is much easier to scan with the three chips, List/Map directly under the headline, and the reminder question moved down. "Free entry. We guess it's worth about £25 to you" is a clear improvement on "Worth about £32 to you · Free entry", and the explanatory line underneath does the work. The data page now has "What we keep" and "What we don't keep", which is far more scannable. The booking disclosure is in the right place — before the links, not after. Android now uses its own back arrow and ✕, and the tab bar no longer looks like it is covering content. The date consistency is fixed on the screens I can read: "Sat 24 Oct" and "SATURDAY 24 OCTOBER" now agree. The flight time zones are fixed: 07:50 Tashkent → 10:56 London with a stop is plausible, and the return is 6h 52m direct. "No limit" instead of "Any" is better. "Made-up rating, for testing" on the sample stay is honest. "Plus lunch" and "Done by" are consistent. The "this or that" days now sit on the same quiet card, with "Choose this day", which removes the red tint that made one day look worse before it was read.

### What is still wrong, or newly visible

**The PDF itself is hard to review.** The iOS screenshots on pages 4–23 mostly show the old text and layout — "Not right", "Tell it instead", "SATURDAY 31 OCTOBER", the nudge question at the top of 9a — while the Android screenshots on pages 25–39 show the fixed version. The cover note says the iPhone pictures predate the fixes, but a reviewer cannot tell which fixes are in which platform. If the point of this pack is for Abram to decide, the pack should show the current state of both apps, or clearly label every old screenshot. Right now I have to read the captions to know what the app actually does.

**The path to the first plan is still too long.** The synthesis defers this to Abram (decision 1). The recommendation — move the open "great moment" question after the first plan, add "Skip to my plan" from question 4 — is sensible, but it leaves 13 questions, then the three-question survey (screen 15), then the three-question pre-plan setup (screen 16), then two long plans to read and two fit ratings. That is still a lot before the user gets their own plan. I understand the Test B pair must stay before the plan to stay blind. But the *survey* on screen 15 ("I felt understood", "It felt like talking to a person") is rating the onboarding, not the plans. It could move after the plan comparison. The pre-plan setup on screen 16 ("Recharge or explore?", "Who might come?") could be merged into the comparison screen or moved after. The pair itself can stay; the scaffolding around it does not need to.

**The "great moment" question is still Q2 of 14** in the Android screenshot on page 26. The synthesis says it should move after the first plan. That is decision 1, not yet implemented. Until it is, the first real effort in the app is an open-ended memory question before the user has seen anything.

**"Skip to my plan" is not visible.** The synthesis recommends adding it from question 4. The screenshots still show "Skip" (top right on 3b) and "Skip the rest" (on 6/6b). "Skip to my plan" is a stronger, clearer escape hatch. It is not there yet.

**The safety promise is still "within a few hours"** on page 32 (13a). The synthesis flags this as decision 5, with a recommendation to state cover hours. I would decide this before strangers use the app. A broken promise is worse than a qualified one. "Usually within a few hours, 8:00–22:00 UK time; overnight, by the morning" is honest and still reassuring. "999 first" is correctly first.

**The rating word "Flat" is still there** on page 30 (11). Decision 3 recommends "Disappointing". I agree. "Flat" can read as neutral or merely unexciting; "Disappointing" is unambiguously the low end. Change it before any tester rates, so the data stays comparable.

**The "What I've learned about you" heading is still on the old iOS screenshot** on page 23. The synthesis says it was changed to "What you've told us". The Android version may have it, but the new PDF does not show the Android "You" screen — page 39 ends at screen 32, and page 40 only describes screen 33. So I cannot verify the fix. This is part of the old/new screenshot mix problem.

**The share card still looks like it says "I think you'd love this"** on page 31 (11c). The synthesis defers this to decision 7 (let people write their own line). I would decide it before the friends round. "I think you'd love this" puts words in the user's mouth after they have just rated the place. "I loved this" or an editable line is better.

**The plan comparison is still two long plans** on page 33 (17a). The new sample data is different — "Lunch near Waterloo station" and "The Garden at 120" — but the Garden plan is much more exciting than the lunch plan. For a blind comparison, that may bias the gut choice toward the more exciting plan, not the one made from the user's answers. Shortening the plans or balancing their excitement level would help the test. The synthesis says decision 2 is to ask the gut choice first; I cannot tell from the screenshot whether that is implemented, because the screen still shows the plans first.

**The "worth" line is better but still a strong claim.** "Free entry. We guess it's worth about £25 to you" with the explanatory line is much clearer than before. The synthesis recommends keeping it for Test B (decision 4) because it is the app's distinctive claim. I agree for the friends round. For strangers, I would ask them how they read it. "Worth to you" is still a judgement the app is making about the user's experience, even with "we guess". The explanatory line helps; consider making it less prominent than the entry price.

**The data page is better but still dense.** "What we keep" and "What we don't keep" is the right structure. The paragraphs are still long. For a privacy screen, more bullets and fewer sentences would be better. The spoken-answers line — "as text: the sound stays on your phone and isn't kept" — is good and specific.

**The "Remove this flight from the trip" link** on page 36 (24) is still a plain text link under the card. The synthesis says it asks for confirmation first. That is fine, but the link is visually prominent for a destructive action. A quieter "Remove" in a menu, or a less prominent style, would be better. This is minor.

**The "How the day moves" curve labels may still be out of order.** On page 29 (9a), the labels under the curve are "Lunch 12:12", "Calm 14:34", "Big views 13:33" — the order on the x-axis should be Lunch, Big views, Calm, Awe. I cannot read the small image clearly enough to be sure, but the old PDF had this problem and I do not see a fix in the synthesis. If the labels are out of order, the curve looks wrong even though the underlying data is right. Check this.

### What I would decide, in order

1. **The safety promise.** State cover hours. This is the one pending decision that affects trust most directly. Do it before strangers.
2. **The rating word.** Change "Flat" to "Disappointing" before any tester rates.
3. **The path to the first plan.** Move the great moment question after the first plan, add "Skip to my plan" from Q4, and consider moving the survey (15) after the comparison. Keep the Test B pair before the plan.
4. **The share card line.** Make it editable, pre-filled with the user's own words. Remove "I think you'd love this".
5. **The iOS screenshots in the PDF.** Update them or label them clearly. The current mix makes the pack hard to review.
6. **The "worth" line.** Keep for Test B, but ask testers how they read it. Make the entry price more prominent than the guess.
7. **The plan comparison.** Shorten the plans and balance their excitement level so the blind test is fair.

The product is in better shape than the first pack. The remaining issues are mostly about test friction and a few pending decisions, not about the core idea. The arch, the amber, the serif, the example day, "So far, I've learned", the way in, 999 kept separate, "Delete my data" and "we earn nothing" are all still the right things to keep. The next version should protect them by deciding the pending items and showing the current state of both apps in one clean pack.

## Review 2

I've read both the new synthesis and the revised ODYS screen pack. My assessment is that this is a meaningful improvement over simply collecting another round of design opinions: you've separated actual bugs, completed changes, rejected suggestions and decisions that still need your judgement.
My recommendation is to stop making broad design changes for now and resolve the remaining product and research decisions before testing with strangers. There are a few things I would decide differently from the current synthesis, and one visible issue in the revised Android screenshots that I would investigate.
1. What you've done well
The synthesis identifies 31 fixed points, 14 suggestions left unchanged with reasons, and seven decisions for you. It also records 194 passing Brain tests and confirms that Android compiles and renders the screens. That's a useful engineering record rather than just a design critique.
screen-review-synthesis.md

Several changes are particularly good.
Date and time consistency
The Android screen now has Saturday 24 October selected in the date shortcuts and the date field. The revised examples also acknowledge the timing of the forecast and connect the best-light window to the actual visit time. These changes address real sources of confusion, not cosmetic preferences.
screen-review-synthesis.md

A clearer plan screen
Moving List/Map directly under the headline and showing the map when Map is selected makes the main task easier to understand. Moving the reminder question closer to “Start the day” is also sensible: users see their result before being asked to configure an additional feature.
screen-review-synthesis.md

Less ambiguous language
“What you've told us” is friendlier than “What I've learned about you”. “Don't use this” is clearer than “Not right”. “Thanks for today” sounds more natural, and moving the external-booking disclosure ahead of the links is a good trust improvement.
screen-review-synthesis.md

Better handling of sample data and privacy
Regenerating the flight examples, removing fictional hotel review counts and rewriting the data page are meaningful improvements. They help prevent a prototype from giving the impression that invented results or metrics are real.
screen-review-synthesis.md

I also agree with keeping the dark visual identity, arch, amber accents, example day, arrival paths and preference-correction experience. These are coherent parts of ODYS's identity, and the reviewers broadly agreed on their value.
screen-review-synthesis.md

2. One issue I'd still investigate in the revised screens
The Android screen labelled 9d, “Your day, on the map,” is the main visual concern I see in the new PDF.
The view shows numbered stops connected by a route line on an almost entirely black background. There are no obvious streets, place labels or geographical features to help a person orient themselves.
That makes it look more like a route diagram than a map.
I'd verify that OpenStreetMap tiles are actually loading on a physical Android device and that the chosen dark map style retains enough geographic detail to be useful. If the minimalist appearance is intentional, the map still needs recognisable geographic context. Otherwise, I would not consider the map experience finished.
There is one important limitation to this review: the revised pack explicitly says the iPhone screenshots predate the fixes, while Android shows the newer build. The iPhone build is paused because of GitHub Actions billing, so its changed code has been checked by inspection rather than a full build.
odys-screens.pdf

I would therefore avoid drawing conclusions about the final appearance of the iPhone changes until there is a runnable build. Reviewing the code is useful, but it doesn't replace testing actual layout, permissions, navigation and interaction on the device.
3. The seven decisions I'd make
The synthesis has correctly separated these from straightforward fixes. Here is how I would resolve them.
Decision 1 — The path to the first plan
My vote: move the open “great moment” question until after the first plan, and offer a clearly labelled shortcut for people who want to get to their plan sooner.
The question fits ODYS philosophically, but it requires more effort than the surrounding questions. Importantly, the synthesis says the planner doesn't use that answer, so moving it does not sacrifice information the current algorithm needs.
screen-review-synthesis.md

I would keep the six place reactions and five day comparisons for the normal research path, since you've identified them as valuable inputs to the model.
One additional condition: record how far someone got before using the shortcut. People who complete all the questions and people who skip most of them shouldn't automatically be treated as equivalent observations in your analysis.
The blind comparison must also remain intact for the Test B cohort. Don't let a shorter route silently bypass the experimental comparison and then merge those results with the primary test group.
Decision 2 — Keep the Plan 1 / Plan 2 comparison before the result
I agree with keeping it before the first personalised plan.
The point of the test is to find out which day someone prefers before they know which one was personalised. Showing the personalised result first would compromise that blind comparison. Your synthesis correctly identifies this trade-off.
screen-review-synthesis.md

I would make the question “Which day would you rather do?” the primary required response. Ask it before the individual fit ratings, and make those ratings and the explanation of why optional during the stranger round unless they are essential to a clearly defined research question.
This preserves the most useful measurement while reducing the effort required to complete the test.
Decision 3 — Replace “Flat”?
My preference is “Not for me”, provided the rating is intended to teach ODYS about personal fit.
There is a meaningful distinction between these options:

* “Flat” can mean neutral, dull or emotionally uneventful.
* “Disappointing” communicates a negative experience, perhaps because something went wrong.
* “Not for me” communicates that the experience didn't suit the person.

For a product that aims to learn what each person enjoys, I find “Not for me” the most relevant of the three. It avoids treating a disappointing day caused by bad weather or an unexpectedly crowded venue as necessarily evidence that the user dislikes the place itself.
If your intended measurement is specifically how enjoyable the experience felt, irrespective of personal fit, “Disappointing” is also defensible.
Choose the meaning first, then keep the scale stable throughout the test. The synthesis is right that this should be settled before ratings accumulate.
screen-review-synthesis.md

Decision 4 — Should strangers see “Worth about £25 to you”?
Keep the feature in ODYS, but be deliberate about what you are measuring when it appears.
The revised copy is an improvement. “Free entry. We guess it's worth about £25 to you” is followed by an explanation that it is an estimate, not a price or a promise of how someone will feel.
It is still a bold claim. A disclaimer can explain what the number isn't, but it doesn't establish that the number is meaningful to the user.
I'd ask a small number of testers, without explaining the feature first:
“What do you think this £25 means?”
Their answers will tell you whether people understand it as an estimate of personal value, mistake it for a cost or saving, or find it oddly precise.
There is also a research distinction worth preserving: the estimate appears after the blind choice, so it doesn't necessarily contaminate the initial Plan 1 / Plan 2 preference. It could, however, influence subsequent expectations and stop ratings.
Record that distinction in your analysis. If the primary question is how accurately ODYS predicts satisfaction, consider testing stop ratings without the value estimate first, or evaluating the estimate in a separate group.
screen-review-synthesis.md

Decision 5 — The safety response promise
Don't promise a response time you cannot reliably deliver.
“A person will reply within a few hours” sounds reassuring, but it creates an expectation of ongoing availability. The synthesis notes that this is a concern for a founder working a limited number of hours, and suggests specifying cover hours.
screen-review-synthesis.md

I would choose a schedule that you and any backup helper can actually sustain. State when messages are monitored, what happens outside those hours, and make it explicit that the contact form is not emergency support.
Keep emergency instructions first, as they are now.
Decision 6 — Hide Trips during testing with strangers?
Yes, I would hide or feature-gate Trips for the stranger round.
The current research is primarily about whether a personal day plan is better than a generic one. The larger trip flow adds flights, stays, filters, external bookings and many more screens. Those are significant features, but they are a separate research problem.
For friends, keep Trips available for exploratory feedback. For strangers, focus the first study on the London day planner. Decide whether to expose Trips in the stranger round after you have reviewed the results from the friends round. This is also the direction proposed in your synthesis.
screen-review-synthesis.md

Decision 7 — Make the share-card sentence editable?
Yes, with one safeguard: don't put words into the user's mouth without letting them approve them.
The current share card can generate a line such as “I loved Uber Boat on the Thames, and this has views too.” It sounds personal and gives the card a reason to exist beyond simply displaying a photograph.
But it reads like a statement the user personally wrote. If ODYS generates that wording from inferred preferences, the user may not agree with every part of it.
I'd prefill an editable field and let users change or remove the sentence before sharing. Make sure the preview is exactly what will be sent.
That preserves the convenience of suggested wording without sacrificing personal control.
screen-review-synthesis.md

4. One distinction I'd keep in mind about all five AI reviews
The fact that all five reviewers independently identified the long path to the first plan is useful. It gives you a strong reason to investigate that issue first.
But five AI reviewers agreeing is not the same as five real people abandoning onboarding. It is evidence of a plausible usability risk, not a measured drop-off rate.
Your next step should be real users, not a sixth AI opinion.
I would focus the first sessions on whether people:

1. Understand what ODYS offers without a lengthy explanation.
2. Finish onboarding without feeling that they are being interviewed.
3. Understand why a particular moment was selected.
4. Know what the personal-value estimate means.
5. Can reach and use the map, directions and next-stop actions without help.

Observe where they hesitate and what they say spontaneously. Don't explain the design to them while they're completing the tasks.
5. My final recommendation
I would resolve the onboarding shortcut, the rating label, the presentation of the value estimate and the real safety cover hours now. I'd also verify the Android map rendering and get a build of the updated iPhone app running before treating the cross-platform work as complete.
After that, freeze the interface for a small, structured test. The remaining work listed for later—such as clustering accommodation price markers, shortening the long plan headline and improving the relationship between chosen feelings and stop labels—can wait unless real testers struggle with those areas.
screen-review-synthesis.md

The central point is this: ODYS already has a strong enough visual identity to start learning from real people. The biggest risk now is spending too long polishing screens before establishing whether people understand the recommendations, trust the estimates and actually prefer the personalised day.
The next round should give you evidence about those questions, rather than simply produce another list of design suggestions.

## Review 3

**ODYS Updated Screens Review – Real Human View**  
(19–20 Oct 2026 builds – iPhone mostly pre-fix, Android post-fix)

I’ve gone through the new pack carefully, comparing it to the previous version and the synthesis of the five earlier reviews. Here’s a grounded, screen-level and flow-level take as someone actually using the app for the first time.

### Overall first impression

The product still feels unusually thoughtful and calm. The dark + amber + Newsreader + arch language is consistent and distinctive without being precious. Most of the copy improvements from the 19 Oct fixes are clear improvements. The remaining friction is almost entirely structural (how much happens before the first real plan) rather than visual or tonal.

### 1. Flow – Where people still hesitate or drop

The biggest issue is unchanged in spirit:

**You still have 14 questions + the Test B pair before anyone sees a personal plan.**

Even with better wording and “Skip rest”, this is a long tunnel. A first-time user who is only mildly curious will feel the length. The example day helps a lot, and “So far, I’ve learned…” is excellent trust-building, but the cognitive cost of the full sequence remains high.

Specific friction points that still exist:

- Question 4–6 (places / kinds of places) is the heaviest stretch. Doing several photo cards in a row starts to feel like work.
- The Test B comparison (two full plans to read and rate) sits right before the personal plan. It’s methodologically clean, but it adds another layer of reading and decision-making when the user is already tired.
- Once you’re past that, the rest of the flow (plan → day → stop → Now → rating → share) is smooth and well-paced.

Recommendation that still holds: move the open “great moment” question later (or make it optional after the first plan) and add a clearer “Skip to my plan” earlier. The rest of the sequence can stay for accuracy.

### 2. Clarity – Wording that still confuses or feels heavy

Much better than before. Specific remaining notes:

- **“Worth about £32 to you · Free entry”** (and the new longer version) is clearer, but it still mixes a price signal, a value judgement, and a free-entry fact in one place. Some people will still read it as “this is what it costs me” the first time. The added clarification helps, but the concept itself is the distinctive (and slightly risky) claim.
- **“How the day moves”** is better with the “our guess, not a score” line, but the little mountain graphic still needs one more second of understanding the first time you see it.
- **“Flat”** on the rating scale still feels slightly ambiguous (neutral? disappointing?). “Disappointing” would be clearer as the low end.
- **“Lunch on top”** has been improved in places, but the concept of “places a day + lunch” can still feel a little opaque the first time.
- On the stop screen, the nested “The way in” steps are good, but the hierarchy between “Why we picked this”, the value estimate, and the arrival path could still be tighter.

Most other copy is now tight and human.

### 3. Visual design – Hierarchy, spacing, consistency

**Improvements that land well**
- Plan screen hierarchy is better: numbers as chips, List/Map higher, reminder moved down. This was one of the strongest fixes.
- Share is correctly secondary after rating.
- Consent now has clear “Tick both to continue”.
- Selected answers get ticks (good for accessibility and clarity).
- “None of these” as a full button under Continue is much better than a quiet link.
- Android switches now have visible thumbs when off.

**Remaining visual notes**
- Primary amber buttons are excellent. Secondary actions are sometimes still a little soft or inconsistently weighted.
- On several screens the primary CTA sits close to the bottom safe area (especially noticeable on iPhone).
- The “How the day moves” graphic is elegant but still low-contrast in places.
- Stop detail screens remain quite dense once you scroll past the hero photo. The emotional “why this for you” could lead more strongly.
- Android and iPhone are still very close in overall language, which is a strength. A few Material controls still sit slightly less comfortably inside the custom dark cards than the iOS versions.

### 4. Accessibility

- Contrast is generally strong (the earlier “dim text” complaints were largely PDF compression artefacts).
- Tap targets for main chips and CTAs are good.
- Some secondary labels and photo credits are still on the small side.
- The rating arch animation is a nice progressive disclosure and respects Reduce Motion.
- Location and reminder permissions are well explained.

### 5. Trust, safety, privacy

This remains one of the strongest parts of the product.

- 999 is correctly separated from the “I feel unsafe” form.
- “We earn nothing from these links” is now placed before the booking links — good.
- Data page is clearer with the short “What we keep / What we don’t keep” structure.
- Typing DELETE is still the right deliberate step for irreversible deletion.
- The safety reply promise (“within a few hours”) is still strong for a one-person operation. Stating cover hours would make it more honest without losing the human tone.

Nothing feels pushy or extractive. The tone is consistent with the rest of the product.

### 6. Platform fit

- **iOS**: Still feels mostly native and quiet. Custom elements (arch, amber, Newsreader) sit comfortably.
- **Android**: Material controls are used correctly. Maps and directions are platform-appropriate. A few custom cards still feel slightly less “Material” than the iOS counterparts, but the gap is small.

Both versions feel like the same product.

### Top 10 remaining changes (current state)

| Screen / Area | Problem | Why it matters | Suggested fix | Severity |
|---------------|---------|----------------|---------------|----------|
| Onboarding (3–7 + Test B) | Still ~14 questions + comparison before first personal plan | Highest drop-off risk | Move open “great moment” later or make optional; add clearer early “Skip to my plan”; keep Test B before the plan for blindness | High |
| 6 / 6b | Long sequence of place cards | Fatigue sets in | Cap or make more swipeable; stronger “Skip rest” | High |
| 9a / 9c | “How the day moves” still subtle | First-time understanding cost | One short first-time explanation or slightly stronger visual labels | Medium |
| 10 / 10a | Stop detail density | Scroll fatigue on the day | Lead more strongly with the emotional reason; make “The way in” collapsible by default | Medium |
| Rating (11) | “Flat” is ambiguous | Rating data quality | Change to “Disappointing” (or “Not for me”) before any real testers | Medium |
| Primary CTAs | Sometimes too close to bottom edge | Accidental taps / gesture conflict | Consistent bottom safe-area padding | Medium |
| Value estimate | Still can read as a price | Confusion / slight sales feel | Keep the reworded version, but consider testing a version without the £ figure for strangers | Medium |
| Safety promise | “Within a few hours” is strong for one person | Trust if someone actually needs it | State cover hours clearly | Medium |
| Share card | Line is generated, not editable | Missed ownership | Pre-fill an editable line in the user’s voice | Low–Medium |
| Trips tab | Large surface while Test B is about day plans | Scope creep for the stranger round | Keep for friends; decide after friends feedback whether to hide for strangers | Low |

### Bottom line

The 19 Oct fixes addressed most of the surface issues the previous reviewers raised. The product is cleaner, clearer, and more trustworthy than it was 24 hours earlier.

The remaining high-severity problem is structural: the path to the first personal plan is still long. Everything after that point (the plan itself, the “Now” mode, the rating loop, the calm tone, the ethical stance on money and data) is already strong.

If you shorten the tunnel to the first plan without damaging the model’s accuracy, this becomes a genuinely distinctive and pleasant experience rather than a careful but demanding one. The visual and verbal language is already doing most of the hard work.

## Review 4

I compared the new pack with the first one and read the synthesis against it. Three limits first:

- **The iPhone pictures are still the 18 Oct build.** I could verify fixes only on Android.
- **Some pictures are unreadable.** Android 11b and 12a are cropped by the PDF layout, and the map has no tiles. 28a and 28b show black behind the sheets, which I flagged last time and the synthesis doesn't answer. I can't tell whether that is capture or a real bug.
- **The iPhone fixes have never been built or seen.** Thirty-one changes checked only by reading code is a real risk, so don't send an iPhone build to friends until someone has run it once.

### How I read the synthesis

It's careful, and where it rejects a point with evidence I'm persuaded: "Grazze" and "5 = completely", on-device speech, "Borough Market" being only a stated answer, typing DELETE, and not reading booking emails. My "2–3:1 by eye" on dim text was wrong against your measured 5–8:1. Still, measure the controls that matter ("Previous", "Skip", placeholders) on a real device, not just the tokens.

One caution: five AI reviewers agreeing tells you what is cheap for a model to notice (length, hedging, small text). It doesn't tell you that people will quit. Have three friends do first-run on a screen share and note where they stop talking.

### Fixes I could verify on Android

- **Time zones.** 07:50 Tashkent to 10:56 London in 8h06 checks out, as does 15:30 London to 03:22 +1 in 6h52. Day 1 (Paddington 11:56) now follows.
- **Plan screen.** The chip and date agree (Sat 24 Oct), the Outlook wording is honest, and the List/Map toggle is now near the top.
- **Wording and controls.** "Choose this day", "Plus lunch", "Speak instead" and "None of these" as a button all help. So do the checkboxes with "Tick both to continue", the arrows and ✕, and the chevron on "Talk to a person".
- **Trust.** The earns-nothing line now sits before the links, and "Made-up rating, for testing" replaces fake review counts.

### Partial fixes

- **Plan screen.** On Android the first stop is still about a screen and a half down, behind a four-line, 17-word headline, three chips and the curve. "Done by 17:00" wraps alone onto a second row, and the chips are filled pills that aren't tappable. The headline is a copy change, so it doesn't belong in "noted for later".
- **Best-light card.** "17:26–18:26; this plan has you here at 13:33" is honest. But the day ends at 17:00, so a dusk place can never fit. Say "this day ends at 17:00, so you'll see it by day", or offer "Finish later".
- **"Free entry. We guess it's worth about £25 to you."** This reads far better, but a free place worth £25 still needs one line on what "worth" means.

### What the synthesis missed

1. **Test B may leak which plan is which (17a).**
   - The personal plan's first stop is "Lunch near Waterloo station — Pick a café, pub or food stall nearby". The generic one is a named place, "Lunch at Borough Market".
   - The personal plan's Garden stop carries a long story ("You step up 15 floors into a garden of wisteria…"). The generic stops get one line ("Wander the free collection of paintings at your own pace").
   - The generic plan also has an "If it rains" line. I can't see the personal plan's bottom, so check it.
   - People may pick the plan with named places and more detail for reasons unrelated to personalisation. The caption's "nothing gives one away" isn't quite true. Equalise length, structure and specificity, then have someone read both cold.
2. **Screen 16 asks for wants that change nothing.** The caption says it changes neither plan, but the screen asks "Anything you'd want in it for sure?" Someone who types "a view" and sees it ignored will feel unheard, which undercuts "I felt understood". Reword it ("so we can see why you chose") or ask it after the choice.
3. **"About 3 minutes" (2a) isn't true.** It's 14 questions (16 for visitors, whose counter says "of 16"), four survey items, three preference items, two plans and a rating. Time three friends and use that number. Also log the last screen reached per person (no personal data needed), so drop-off tells you where to cut.
4. **The data page's "What we don't keep" box contains things that are kept or sent.**
   - Trips: "The days planned for them are kept like any plan."
   - Searches: "we keep only which filters you used."
   - Location: "sent rounded to about 100 m".
   - Help contact details are kept until deleted.
   
   Use three boxes: kept, sent to providers, never kept. I also couldn't see the "for how long" section the caption mentions, so make sure it states real periods.
5. **Screen 15 says "Three quick questions" and has four.** "Did you type or speak your answers?" is something the app already knows, so log it instead of asking.
6. **Android parity:**
   - 23's button says "Plan the trip again" in a first-run flow (iPhone says "Make my trip").
   - 25's photo is a tall sliver.
   - 10's back arrow sits bare on a bright photo.
   - 9d's pins 2 and 3 overlap, and there's no stop name on the map view.
   - 1b lacks "Watch his short hello", and 3b's helper line ("So we ask the right questions") dangles without the town field.
7. **"Now" (10b) has no Directions.** The next stop is a small dim card and "I'm done here" is enabled while the text says ratings open on the day.
8. **On-device speech may fail visitors.** On-device recognition tends to be weaker for accents and other languages, and Android needs a language pack. If it's missing, hide "Speak instead" rather than silently falling back to cloud. Test it with a non-native speaker.

### My take on your seven decisions

1. **Move Q2 after the first plan.** Yes, and I'd go further. If the planner doesn't use it, asking it first is pure cost. Rename the existing "Skip the rest" to "Skip to my plan" instead of adding a third skip. Tag the build version in the data, since the "talking to a person" item now measures a different flow.
2. **Keep the pair before the plan, and make the gut choice first.** I'd keep the two fit ratings but make them optional, and tolerate the lost secondary measure.
3. **"Flat" → "Disappointing", before anyone rates.** "Flat" is also idiomatic, and visitors are a core group. Ask two non-native speakers.
4. **Keep "worth about £V" for friends.** Add a one-tap "useful?" and decide for strangers afterwards.
5. **State cover hours.** Make the auto-reply (13b) match, and only claim "whoever is covering" if a named person has agreed. Consider adding that 112 also works in the UK, and Samaritans 116 123.
6. **Keep Trips, but demote it.** You already ask "Where are you based?", so lead the home screen with "Plan a day" for Londoners and "Plan a trip" for visitors.
7. **Editable share line.** Yes.

### Revised top 10

| Screen | Problem | Why it matters | Suggested fix | Severity |
|---|---|---|---|---|
| 17a | Plans differ in specificity, length and structure | Test B may measure writing, not personalisation | Normalise both and name lunch in each | High |
| 16 | Asks for wants that "change neither" plan | Feels ignored and hurts "understood" | Reword it, or ask after the choice | High |
| 2a, 6b, 4 | "About 3 minutes" against 14 or 16 questions; open question at Q2 | Broken first promise and early drop-off | Time it, move Q2, "Skip to my plan", log drop-off | High |
| 11 | "Flat" is ambiguous and idiomatic | Ratings can't be compared later | "Disappointing" before the first rating | High |
| 13a, 13b, 33 | "Within a few hours" from one person | An unkept safety promise | Cover hours, matching auto-reply, 112 and Samaritans | High |
| 9a | Stops start about 1.5 screens down; four-line headline | The payoff is spent on setup | Shorten the headline, curve below or collapsed, non-pill stats | Medium |
| 14a | "Don't keep" box contains kept items | Reads as contradictory, with legal risk | Three boxes and a visible retention section | Medium |
| 10, 10a | Best-light window can't fit the day; "worth £25" unexplained | Looks like a planner flaw | Honest line plus "Finish later"; one-line meaning of "worth" | Medium |
| 10b | No Directions; weak next-stop card | The key outdoor action is missing | Lead with next stop plus Directions | Medium |
| 23, 25, 28a/b, 9d, 10 | Android parity bugs | Looks unfinished | CTA text, square thumbnail, scrimmed back arrow, pin fit, check the black sheets | Medium |

### Small ones

- 7: "Choose this day" is a small text link, so make it a full-width button. "Longest journey between stops 50 min" wraps with an orphaned "min", and the same cloud icon is used for dry and rainy.
- 14b: the grey "DELETE" placeholder looks pre-filled.
- 6 and 6b: a dim "Previous" duplicates the top back link with a different scope.
- 12a: seven questions in "about 30 seconds" is optimistic.
- 18: check the copy for someone who picks the generic plan, so they don't feel they failed a quiz.

For the next pack, add scrolled-to-end shots, selected, error and empty states, and one large-text set. Most of the disagreements here (tab bar, below the fold, dim text) were capture artefacts of first-screenful pictures.

## Review 5

Here is an executive review and breakdown of the seven open decisions for Abram based on the review synthesis:

* The path to the first plan: Moving the open "great moment" question to post-plan (inside "Improve future plans") and introducing a skip option streamlines onboarding to 13 steps without sacrificing model accuracy.

* The Test B pair: Retaining the comparison before the initial plan is essential to preserve the blind nature of the test and ensure valid evaluation.

* The rating word "Flat": Changing "Flat" to "Disappointing" provides a much clearer and more intuitive low-end anchor for stop ratings.

* "Worth about £V to you": Keeping this estimate is worthwhile during Test B because it serves as the app's most distinctive claim and tests how users interpret algorithmic value.

* The safety promise: Explicitly stating coverage hours (such as 8:00–22:00 UK time) sets realistic expectations for a solo founder while maintaining strong trust and safety UX.

* Hide Trips for the stranger round?: Keeping Trips active for the friends round allows for comprehensive feedback before deciding whether to scope it down for strangers.

* Share card text customizability: Allowing users to edit the pre-filled, AI-generated reason on the share card strikes the right balance between effortless sharing and personal voice.

Which of these seven decisions would you like to finalize first?
