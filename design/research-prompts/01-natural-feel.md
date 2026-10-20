# Research prompt 1: a more natural feel (20 Oct 2026)

For Abram to paste into two or three other AI models (D128). Attach `design/odys-screens.pdf` if the model can read
PDFs. Paste each answer back to Claude. Claude checks the sources, compares the models' picks with its own, and
proposes a shortlist with reasons; Abram decides. Abram chose all 16 ideas below on 20 Oct and asked the models to
help choose among them.

---

You're helping design ODYS, a mobile app (iPhone and Android) that plans a day out in London around how a person wants to feel (restored, excited, connected, curious, peaceful), not around famous sights. The unit is a "moment": a specific experience at a place and time, often including how you arrive (for example, coming out of a dark Tube station into the open in front of a museum). People answer a few questions, get a day plan, follow it on the day with a quiet "Now" screen, and rate each stop afterwards. If a PDF of the screens is attached, refer to screens by their numbers.

The current look: dark all the time, one amber light, an arch symbol, a serif font (Newsreader), quiet motion. The founder feels the app isn't natural enough. He wants it to feel like nature: easy, calming and alive, so people enjoy using it. It's built by one person with a small budget, in SwiftUI and Jetpack Compose, and must stay accessible (contrast, Reduce Motion, screen readers, colour blindness).

**Part A. The evidence (short).**
1. What does research say about nature-inspired (biophilic) design in digital interfaces, and about attention restoration theory's "soft fascination" on screens? Separate what has been measured (authors, year, link) from practice and opinion. Mark anything you can't source as UNVERIFIED.
2. Name two to four real apps or products that do this well, and exactly what they do. Link each.

**Part B. Help us choose.** These are the 16 candidate ideas. Two of them conflict (1 and 4); please say which you'd keep.

Light and time
1. Sky that follows the day: the background follows London's real sky (dawn, a pale midday, golden hour, deep blue night, greyer in rain), using the sunset times and weather forecast the app already has. The amber arch becomes the sun.
2. Seasons: colours and photos shift with the season.
3. Night stays dark: after sunset the app looks as it does now, dark with the amber light.
4. Keep dark always: don't change the light; bring nature in through shape, motion and pace instead.

Shape and material
5. The day as a path: the plan drawn as a winding path or river with the stops along it, instead of a list of cards.
6. Hand-drawn lines: routes and the arch drawn like ink on paper, a little imperfect.
7. Light textures: a hint of paper grain, water ripple or stone. Subtle, never kitsch.
8. Softer shapes: rounder, pebble-like cards and buttons, fewer hard boxes.

Motion, sound and touch
9. Settling motion: things settle like a leaf landing or ripple like water; nothing snaps or bounces.
10. Nature haptics: a soft raindrop tap when you choose something, a slow heartbeat when the day starts.
11. Place soundscape: on the "Now" screen, the quiet sound of the kind of place you're going to (park, river). Off by default.
12. Something gently alive: something you can rest your eyes on without effort, like a drifting cloud or shifting light. It never asks for attention.

Pace and growth
13. One thing at a time: fewer words, bigger pictures; the next step appears as you go, like a path unfolding.
14. Growth, not points: each day out grows something of yours, like a tree's rings or a constellation of moments. Never badges or streaks.
15. Nature in every day: every plan includes some green space or water unless the person says no.
16. Best-light photos: each stop's photo shows the place as you'll find it (golden hour, rain, night).

For each of the 16, give a row in one table with these columns:
- how much it would make the app feel natural (1–5);
- effort for one developer (S, M or L);
- the main risk;
- keep, change or drop, in one line.

Then:
3. Your top five overall, in order, and why they work together as one system rather than five separate effects.
4. Anything important that's missing from the list.
5. For idea 1 (if you keep it): how would you make the colours follow the time of day and the weather while keeping text readable at every moment? Give a palette approach (for example, a few anchor colours by sun angle, interpolated), not just adjectives.
6. How would you test whether the app now "feels natural" with 5–10 people in a week? Name the questions or measures.

Answer in plain English, in short sections, with sources linked. Please don't invent studies or statistics.
