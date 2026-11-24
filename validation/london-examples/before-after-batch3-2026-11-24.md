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

## Fresh independent reviews

(Added when the three reviews return.)
