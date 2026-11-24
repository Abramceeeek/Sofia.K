# Batch 2, before and after (24 Nov 2026)

**What this compares:** the six synthetic travellers' trips at the start of batch 2 (`de6d48a`) and at its end (`566bb27`). Both were measured with the same gate script, run 3 times each, with the same settings: a 1 s solver limit and 4 CPUs.
- The "after" plans are `examples.md` and `gate.md` in this folder.
- The "before" plans are `examples.md` as committed at `de6d48a`.

**What it isn't:** evidence about real travellers. The judgements are Claude's, against Abram's test: **would a customer happily follow this itinerary without having to fix it?**

## The numbers

| Measure (3 runs each) | Before (`de6d48a`) | After (`566bb27`) |
|---|---|---|
| G1 unexplained gaps | 0 | 0 |
| **G2 days ending more than 45 min early** | **6** | **7** |
| G3–G8 (loved place, dislikes, age, Why lines, gentle pace, proportionate journeys) | all pass | all pass |
| Days over the pace's travel budget | 10 of 13 | 8–9 of 13 |
| Minutes over it, in all | 379–397 | 235–264 |
| Waits mid-day | none | 1–3, 22–127 min |
| Unused time (later start + waits + early end) | 979–1,015 min | 1,230–1,375 min |
| Days breaking "extra places are strong matches" | 1 | 0 |
| Different places across the six trips | 77–78 | 73–74 |

**The trade-off, plainly:** days now travel about a third less and carry no coin-flip filler. They are also emptier, because the strong-match rule and the travel budget refuse places that used to fill them. Abram asked for exactly that ("the objective is not to generate more itinerary stops"), but G2 shows its cost honestly. **London does not pass the gate.**

## Each traveller

### Sam (food, solo, medium, £40 a day)
- **Before:** a rest to start, then Brick Lane, Borough, the City, the British Library and King's Cross.
- **After:**
  - **Friday:** Covent Garden and Soho, lunch in St Martin-in-the-Fields' crypt, Borough Market, Leadenhall, then the evening swim.
  - **Sunday:** dim sum in Chinatown, Liberty, the British Library, King's Cross and a Brick Lane bagel at 17:56.
- **Better:** food leads both days, and the cross-London zig-zag is gone.
- **Honest:** Friday has no dinner, and the plan now says why: "with about £22 for it, today would go over your £40 budget". Sunday's bagel counts as the dinner.
- **Still to fix:** Sunday keeps Burlington Arcade and Liberty, both fair matches within his own three places.

### Priya and Dan (history, couple, medium)
- **Friday: much the same.** The British Museum, the National Gallery and Waterloo Bridge at sunset.
- **Saturday: worse.** The Wellcome, the British Library, lunch near Euston and the Natural History Museum (34 min away). It **ends at 14:38**. Their remaining good matches are history places, D127 allows two a day, and the strong-match rule refuses weaker fillers.
- **Sunday: better.** The Courtauld, lunch near St Paul's, the Millennium Bridge and Tower Bridge at sunset: one walk east, no 42-min hop to Greenwich.
- **Customer test:** Saturday fails; they would have to fill the afternoon themselves.

### The family (parks and boats, children 8 and 11)
- **Friday:** Hyde Park, the City's towers, the Garden at 120, St Dunstan's and Greenwich Park at sunset.
- **Saturday:** the Millennium Bridge, then **the Uber Boat they loved** (46 min to Greenwich Pier), lunch where it lands at Battersea, the Southbank, Waterloo Bridge at sunset and Somerset House.
- **Customer test:** a day a family could follow. The 46-min journey to the pier is long with children, but it is to the thing they loved.

### Jonas (quiet, gentle, solo)
- **The day is unchanged from batch 1:** Hyde Park (loved), lunch near Euston, the Wellcome Reading Room, the British Library, and the canal at King's Cross until 16:23.
- **As Abram decided:** no stop was forced in, and the 97-min early finish stays in G2.

### The four friends (lively, full-on)
- **Friday: shorter.** Lunch, a bike ride in Hyde Park, the Garden at 120, King's Cross, then dinner near the British Library at 18:00. It ends at 19:00, two hours early, where it used to run to 21:00 with the Lido and dinner.
- **Saturday: still full.** St Dunstan's, Tower Bridge at sunset, a Brick Lane bagel, the Lido and dinner.
- **Customer test:** Friday's evening is unplanned. A lively group would want something there, and ODYS has no verified evening cards for them yet (no Camden, no gigs).

### Margaret and Alan (art and the river, gentle, 70+)
- **Saturday: better for them.** The Courtauld, then **the Uber Boat they loved** (50 min to the pier), lunch at Battersea, and the Natural History Museum.
- **Sunday: coherent.** The Wellcome, the British Library, Soane's museum and Waterloo Bridge at sunset.
- **Friday:** much the same as before.

## What still stops London passing (next batch)
1. **Empty afternoons and evenings (G2, 7 days).**
   - **The cause is mostly a thin catalogue:** 52 cards for three-day trips, with few evening experiences and no live entertainment.
   - **Next:** verified evening cards (Friday lates, live music, comedy, a market by night) and more places outside the history cluster. That is more useful than planner tuning.
2. **Loved boats are reached by 46–50 min journeys.**
   - The direction of Abram's card (Greenwich to Battersea) is part of his experience, so it isn't reversed.
   - **Next:** pair the boat with Greenwich itself (the market, the Cutty Sark) as a morning there. That needs verified Greenwich cards.
3. **Priya's Saturday:** a better mix within D127, which stays at two a day.
4. **The iPhone side of "Other places for this time" is not compiled.** It builds on the next run from `main`, or on a manual macOS run Abram approves.
5. **Named food beyond the ready cards** waits for the open-data verification rules (m323–m325).
