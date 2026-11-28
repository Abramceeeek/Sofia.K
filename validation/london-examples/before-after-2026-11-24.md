# Batch 1, before and after (24 Nov 2026)

**What this compares:** the six synthetic travellers' trips before batch 1 (`d45094f`, plans saved before any batch 1 change) and after it (`de6d48a`, `examples.md` in this folder). The plans are the real planner's output, unedited. Both runs use the same cards except one: the Wellcome Collection's Reading Room is new.

**What it isn't:** evidence about real travellers. The judgements below are Claude's, read against Abram's five questions. They are not a review by anyone else. The independent reviews (two subagents and two other AI models) were of the earlier plans; the next round should review these.

## The numbers (the London gate, same script on both commits)

| Measure | Before (`79c6ee5`, pace costs only) | After (`de6d48a`) |
|---|---|---|
| Unexplained gaps (G1) | 0 | 0 |
| Days ending more than 45 min early (G2) | 1 | 6 |
| Waits in the middle of a day | 6, 338 min in all, longest 70 min | 0 |
| Unused time (later start + waits + early end), 13 days | 1,321 min, 102 min a day | 979–1,015 min, 75–78 min a day (two runs) |
| A loved place in the trip (G3) | 6 of 6 | 6 of 6, and more loved places kept (below) |
| Disliked kinds, age rules, Why lines, gentle pace, journeys (G4–G8) | all pass | all pass |
| Two views from above on one day | the friends, day 1 | none |
| A day starting with a rest | none in this run | none (now a rule) |
| Time to plan a trip (gate laptop, 1 s solver limit) | about 19 s for Priya's 3 days | 5–19 s |

**Read G2 with the waits.** Before, several days reached their end time by waiting mid-day: Priya's Saturday had an hour before the Millennium Bridge, which never closes, and the family's Saturday had 65 min before Somerset House. Those waits are now gone. The time left over sits at the end of the day, where G2 sees it. Overall, a quarter less of the traveller's day is unused. **The gate isn't green, and it shouldn't be made green by putting the waits back.**

## Each traveller

The five questions: more enjoyable? more personal? sensible geography? appropriate pace? would a local recommend it?

### Sam (food, solo, medium pace, 11:00–20:00)
- **Personal: better.** Borough Market and Beigel Bake, both places he loved, are his first two stops. Before, his day opened with a rest in the Royal Festival Hall.
- **Geography: mixed.** He goes Borough → Brick Lane → the City, then up to King's Cross and back across to Mayfair. That evening crossing is the weak part.
- **Pace: too full.** He asked for 3 places a day and gets 8.
- **Local: no, not for the evening.** A local would send a food lover to dinner on Brick Lane or in Soho, not to Burlington Arcade and Liberty from 18:25. There's no dinner on either day; see open issue 1.

### Priya and Dan (history, couple, medium, 09:30–18:00)
- **Friday: better.** The same museums, with the sunset from Waterloo Bridge as the ending, and no 37-min wait before the first stop.
- **Saturday: better, but long journeys.** Before, the day had two waits of about an hour and went east, then back west, then east again. Now there are no waits, but there are four journeys of 21–31 min (135 min of travel).
- **Sunday: worse.** They travel 50 min to Greenwich for the Uber Boat but miss General Wolfe's hill beside the pier, and the day ends at 15:54.
- **The cause:** their remaining good matches are all history places, and D127 allows two a day. See open issue 2.

### The family (parks and boats, children 8 and 11)
- **Personal: better.** The Uber Boat they loved is in. ChatGPT's review had flagged it as missing.
- **The cost of the boat:** a 52-min journey to Greenwich to board it, which is long with children.
- **Waits:** the 53-min and 65-min waits are gone.
- **Geography: a long sweep on Friday.** Hyde Park → the City → Greenwich: 143 min of travel.

### Jonas (quiet, local, gentle pace, solo, under £20)
- **Gentle and coherent:** Hyde Park, which he loved, then lunch near Euston, the Wellcome Reading Room, the British Library and the canal at King's Cross. After lunch everything is within 13 min on foot.
- **Before,** his afternoon was a 57-min journey to the Greenwich Peninsula.
- **The end of the day:** it ends at 16:23, 97 min early. That's free time after a calm day, and no strenuous or ill-suited place was added to fill it. **Abram's call:** is that the right ending for him, or should ODYS find a verified quiet evening place (see the next steps)?

### The four friends (lively, full-on, 11:00–21:00)
- **Friday: better.** One view from above (before: Horizon 22 and the Garden at 120, 6 min apart). It adds Brick Lane and the evening swim, with dinner.
- **Saturday: a little emptier.** Liberty is gone and the day ends at 19:30.
- **Still missing:** Camden and the cable car. They have no cards (a catalogue gap).

### Margaret and Alan (art and the river, gentle, 70+ budget)
- **Personal: better.** The Uber Boat, for the river they loved, is in on Saturday. ChatGPT's review had flagged it as missing.
- **The cost of the boat:** a 50-min journey to its start, which is long for a gentle pace. Their own rules allow it, because it's a place they loved.
- **Sunday: better.** No 70-min wait. It runs from King's Cross to Holborn and ends at Waterloo Bridge at sunset.

## Open issues (for the next batch, or for Abram)
1. **Dinner for food lovers.** The dinner slot is neutral (it scores 0), so for Sam shops beat dinner at 18:00. Should a meal score by the person's own liking for food? *Claude's recommendation: yes, the same way lunch's credit works (m321); about 2 h.*
2. **D127's two history stops a day, for history lovers.** This caps Priya's Sunday. **Abram's decision:** keep it, or raise it to three for people whose top weight is history?
3. **The trip to a loved boat's start.** Both boat days begin with a 50-min journey to Greenwich. A local would pair the boat with Greenwich itself: the hill, the market, the Cutty Sark. That needs the planner to treat "the place where a ride starts" as a neighbourhood.
4. **Travel over the pace's budget** on 9 of 13 days, mostly because loved places and extra places pull journeys in.
5. **Early ends** on 6 days, mostly a catalogue limit: three days for one person use most of London's 51 cards that fit them.
