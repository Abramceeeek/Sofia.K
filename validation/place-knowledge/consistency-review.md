# Consistency review: a second, independent scoring of the reference experiences (28 Nov 2026, batch 9)

**What was done.**
- A separate AI assessor scored all 15 ready experiences of the seven reference places on the 15 interest dimensions, and named their primary and secondary appeals.
- It worked blind. It saw only:
  - the rubric (`place-vocabulary.md`, with the reference places' own examples removed);
  - the evidence rules;
  - each experience's claims, quotes and statuses, with Claude's scores, primaries and notes stripped out.
- It read no repository file and searched nothing.
- Its scores are in `second-assessor-scores.yaml`, unchanged, and the numbers below are in `consistency.json`.
- **Both assessors are AI.** This tests whether the rubric is read the same way twice. It is not evidence that the scores match what visitors feel.

**The numbers** (Claude's scores as they stood before this review, against the second assessor's):

| Measure | Result |
|---|---|
| Score pairs (15 experiences × 15 dimensions) | 225 |
| Exact agreement on 0, 1, 2 or unknown | 34% (Cohen's κ 0.19) |
| …of which "0 against unknown" | **135 of the 148 disagreements** |
| Agreement where both gave a score (0, 1 or 2) | **92%** (45 of 49) |
| Agreement on whether the appeal is there at all (1–2 against 0 or unknown) | **96%** |
| Primary appeals identical | 12 of 15 experiences |
| Primary appeals overlapping | 15 of 15 |
| Dimensions agreeing best (κ) | social 1.0, history 0.68, architecture 0.61 |
| Dimensions agreeing worst | culture, dining, shopping, nightlife, adventure (κ 0): nearly all 0 against unknown |

**What it shows.**
- The rubric is read consistently on what an experience *offers* (92% and 96%) and on what it's *about* (all 15 primaries overlap).
- It was ambiguous on what ODYS *hasn't checked*. Claude left unassessed dimensions as unknown; the second assessor scored them 0 wherever the experience's own description had been read.
- The engine isn't moved by this. It treats unknown as missing only for a **primary** appeal, which is always a 2, and the planner reads unknown as 0. But it matters for how complete a record looks, and for the next 67 places.

## The 13 other disagreements, resolved in writing

| Experience | Dimension | Claude | Second | Resolution |
|---|---|---|---|---|
| British Museum, Room 4 | art | 1 | 2, primary | **Second assessor's.** The gallery is Egyptian *sculpture*: it is organised around the works as well as the period. Now art 2, primary history and art. |
| British Museum, Room 1 | architecture | 1 | 2, primary | **Claude's kept.** The official description is about the collections. The room's architecture rests on the founder's account and an older search, which can't meet the primary rule. The second assessor flagged it as a judgement call too. |
| Liberty | shopping | 1 | 2, primary | **Claude's kept.** The only claim is that it's a shop; what it sells wasn't read, and the experience on the card is the building. Revisit when Liberty's pages can be read. |
| NHM, Mammals hall | nature | 1 | 0 | **Second assessor's**, with the vocabulary corrected: nature is living nature met directly, and specimens and models are science. |
| NHM Mammals, Dinosaurs, family trail; British Museum Rooms 1 and 4 | learning | 1 | unknown | **Second assessor's.** No claim says there's explanation (labels, talks); Claude had assumed it from "museum". The vocabulary now says learning must be stated by a source. |
| NHM, Mammals hall | play | unknown | 1 | **Claude's kept.** "Families explore the galleries" isn't play. |
| Hyde Park, the Serpentine; Tate, Level 10 | dining | unknown | 1 | **Claude's kept**, and the vocabulary now says a café on site isn't dining unless the meal is why you go. |
| British Museum, Room 1 | art | unknown | 1 | **Kept as unknown.** Greek vases are named among the objects, but as collected objects. Revisit with a direct read of the gallery page. |
| Borough Market | culture | unknown | 1 | **Kept as unknown.** "A living market as culture" is an interpretation no source states. |

## What changed because of the review

- **`place-vocabulary.md`** has:
  - an operational rule for 0 against unknown;
  - "an inferred claim may support a 1, never a 2";
  - tighter definitions of `nature`, `dining` and `learning`.
- **Two records:**
  - the British Museum: Room 4 art is now 2 and primary, and learning is removed;
  - the Natural History Museum: Mammals nature is now 0, and learning is removed from three experiences.
- **Not yet done:** re-scoring the dimensions left unknown in all seven records under the new 0 rule. It's a mechanical pass, about 1 h (GUESS). It changes no engine result, so it's folded into the next 67 places.

## The second assessor's own list of ambiguities (summarised)

1. 0 against unknown.
2. Whether an inferred claim can support a 1.
3. Art against history for ancient sculpture.
4. What meets primary rule 2.
5. Grand against architecture.
6. A building's past: history or architecture?
7. Whether a café is dining.
8. Place-level claims repeated on each experience.
9. Family claims: play, social or only family-friendly?
10. Which appeal leads (the Sky Garden: garden or view? Liberty: building or shopping?).
11. A market as culture.
12. A verified claim whose quote covers only part of it (Level 10: the quote covers the lift, not the view).
13. Evidence only in "what you do".
14. "Thrill" undefined for adventure.

**Fixed:** 1, 2, 3 and 7 (above).

**Fixed, in the record:** 12. The Level 10 claim's quote now names the view.

**Open for the next pass:**
- 5 and 6, which need a written line on what each covers;
- 8, which needs place-level appeals that experiences inherit, as facts already do;
- 9, 10, 11, 13 and 14.
