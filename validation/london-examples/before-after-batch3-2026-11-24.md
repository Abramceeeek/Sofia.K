# Batch 3, before and after (24 Nov 2026)

**What this compares:** the six synthetic travellers' trips at the end of batch 2 (`566bb27`) and at the end of batch 3 (`14c781b`). Both were measured with the same gate script, run 3 times each, with the same settings (a 1 s solver limit, 4 CPUs). The plans are the real planner's, unedited. The judgements are Claude's, against Abram's test: **would a customer happily follow this without having to fix it?**

Three fresh independent reviews of the new plans are summarised at the end.

## The numbers

| Measure (3 runs each) | Batch 2 (`566bb27`) | Batch 3 (`14c781b`) |
|---|---|---|
| G1 unexplained gaps | 0 | 0 |
| **G2 days ending more than 45 min early** | **7** | **9–10** |
| G3–G8 | all pass | all pass |
| Days over the pace's travel budget | 8–9 of 13 | 8 of 13 |
| Minutes over it | 235–264 | 235–255 |
| Waits mid-day | 1–3, 22–127 min | 1, 37 min |
| Unused time | 1,230–1,375 min | 1,236–1,293 min |
| Days breaking "extra places are strong matches" | 0 | 0 |
| Ready London places | 51 | 63 |

**G2 is worse by two or three days.** With 12 more places the planner chooses differently. Several early ends are now shorter (54–84 min), but more days cross the 45-min line. The gate isn't relaxed to hide it. **London does not pass.**

## Each traveller

### Sam (food, £40 a day)
- **Friday: worse.** Borough Market, Beigel Bake, Spitalfields, then the Lido, ending at 17:17 (163 min early). No dinner, and the plan says why: the budget.
- **Sunday: better.** A named lunch at Flat Iron, Covent Garden and Soho, the National Portrait Gallery, then dinner nearby. No shops as filler.

### Priya and Dan (history)
- **Friday:** the same as before.
- **Saturday: better.** The Natural History Museum, the Wellcome, lunch, the Millennium Bridge and Tower Bridge at sunset, ending 16:37. It used to end at 14:38.
- **Sunday: different.**
  - Tate Modern, lunch, then **the Painted Hall and the boat from the pier beside it**, the Greenwich pairing Abram asked for.
  - It ends at Battersea at 15:52 (128 min early).

### The family (children 8 and 11)
- **Friday: better for the children, but the geography is weak.**
  - The new Diana Memorial Playground (families only).
  - The day goes from the City to Hyde Park in 42 min, and ends at 15:45 (75 min early).
- **Saturday:** unchanged: Greenwich Park, the boat they loved, lunch at Battersea, the Southbank and Waterloo Bridge at sunset.

### Jonas (quiet, gentle)
- **Better:** Hyde Park, the new Wallace Collection (free, step-free, usually quietest in the late afternoon), lunch, the Wellcome Reading Room and the British Library.
- **Ends at 16:41,** 79 min early (was 97). No stop was forced in.

### The four friends (lively, full-on)
- **Friday: fuller.** A bike ride, a named lunch at Flat Iron, the City, two sunsets, dinner, and the Southbank until 20:41.
- **Saturday: worse for travel.** Three journeys of 35–44 min (Greenwich Peninsula, the Lido, King's Cross).

### Margaret and Alan (art, the river, gentle)
- **Saturday: better.** The Painted Hall in Greenwich, then the boat they loved from the pier five minutes away, lunch at Battersea, and the Natural History Museum.
- **Sunday: worse.** The Courtauld, lunch, the Wellcome and the British Library, ending at 14:58 (122 min early).

## What changed in the product (both apps where it's on screen)
- **12 verified places** (m340): Greenwich, evenings, families, quiet places, and named food at three price levels.
- **"Raining? Swap for the indoor option",** one tap; "Re-plan the rest of today" says what it changed (m341).
- **Estimates said as estimates** (m343).
- **Group trips:** each stop says who it suits, and the proposal (m342).
- **The day-feel preference**, built in the Brain and proposed for the apps (m344).
- **The iPhone app compiled** on this branch (run 116, at no cost, the repository being public).

## Fresh independent reviews (24 Nov, on the `14c781b` plans)

Three subagents each read the plans with a different brief. They aren't real travellers, so this is still not evidence about customers.

| Traveller | London local | Families and gentle pace | Sceptical product reviewer |
|---|---|---|---|
| Sam | 5/10 | 6/10 | with small fixes |
| Priya and Dan | 6/10 | 6/10 | no (5 Dec), small fixes otherwise |
| Family | 6/10 | 5/10 | no |
| Jonas | 6/10 | 6/10 | no |
| Four friends | 4/10 | 5/10 | no |
| Margaret and Alan | 5/10 | 5/10 | with small fixes |
| **Overall** | — | — | **4/10 against a well-informed friend; "not yet"** |

**What all three agree on:**
1. **The number of places a day and the pace are ignored.** Margaret and Alan asked for 2 gentle places and got 6 on Friday; Priya 7 for 3; the friends 9 for 4. The gaps fill with the same few places: the Royal Festival Hall foyers for 5 of 6 travellers.
2. **Evenings and meals fail.** No real evening for night people or the lively friends. Sam eats twice in two hours, then has no dinner. A generic lunch sits next to a named market.
3. **Geography and light.** Days zig-zag across London. "At sunset" stops fall after dark (Waterloo Bridge at 17:06 and 17:24).
4. **Presentation errors.** The "finishes at" time disagreed with the last stop on 10 of 13 days. The same "lunch near X" cost £6 for one traveller and £15 for another, unexplained. A free-time line pasted a whole stop title. Some Why lines compare different kinds of place ("You loved the Uber Boat, and this has history too" for Liberty).
5. **The gate can mislead.**
   - G7 ("a gentle pace kept") passes while gentle days exceed their travel budget. It only checks for strenuous stops.
   - G6 passes while "at sunset" titles fall after dark.
   - G2 pushes towards filling days, which is the wrong cure for a gentle traveller.

**What they praised:** the cards: exact approaches, prices, booking notes and rain options. Also Priya's Sunday (Tate Modern, the Painted Hall, the boat), the family's boat day, and Jonas's calm, cheap day.

## Fixed after the reviews (m345, `4c0ad0e`)
- **Extra places follow the person's pace:** gentle at most 1, medium or unstated 2, full-on 4.
- **A place called "at sunset" is planned at sunset** when the date's sunset is known.
- **The "finishes at" time** is computed after the last stay is lengthened.
- **A cheaper lunch reads as one.**
- **Free time names the place.**
- **No summer flowers in December.**
Tested.

**The result** (3 runs, `4c0ad0e`):

| Measure | `4c0ad0e` |
|---|---|
| G2 | 12 of 13 days |
| Unused time | 1,448–1,491 min |
| Waits mid-day | 1 (35 min) |
| Days over the travel budget | 9 of 13, 217–228 min over |
| Different places | 68 |

**Margaret and Alan's Friday:** the National Gallery, Burlington Arcade, lunch and the British Museum, ending at 14:36. That is 3 places, against the 2 they asked for and the 6 they had before.

## The decision this leaves for Abram
The reviews and G2 pull in opposite directions:
- **G2 says** a day must run to within 45 min of the person's end time.
- **The reviews say** a day must hold the places and pace the person asked for, and not be filled.

Both can't hold with today's catalogue. The options:
1. **Keep G2 as it is** and keep failing until the catalogue has enough strong matches. That is honest, but nothing passes soon.
2. **Approve the day-feel preference** (`decisions/day-feel-preference.md`): someone who chose Relaxed is measured against the day they asked for. Others keep G2.
3. **Make G2 measure the person's own number of places** ("no day short of the places they asked for"), with free time said as free time, and keep unused time as a reported measure.

**Claude's recommendation: 2, with 3 for gentle travellers.** Either way, more evening and named-food places are the work that helps every option.
