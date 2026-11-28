# The place and experience vocabulary, and how it is scored (28 Nov 2026, batch 9; m364)

**Decision first.** One controlled vocabulary describes both places and travellers, so a traveller's interest can be matched to what an experience actually offers. Every term below is defined, is scored 0–2 against written anchors, and names the evidence that can support it.

- **Primary and secondary appeals are a separate judgement from the 0–2 score** (§3). A collection of 2s never becomes a list of primary appeals.
- **No term enters the person model as a feature until the reference places carry it** (`place-knowledge-model.md` §6).

## 1. Interest dimensions (what an experience offers)

Each is scored for an **experience**, not a whole place (`place-knowledge-model.md` §1).

| Dimension | Covers | Not to be confused with |
|---|---|---|
| `history` | the past made present: historic sites, collections about the past, events that happened here | `art`; a building's age (that's `architecture`) |
| `culture` | living traditions, performance, how people live now | `history` (past) and `art` (works) |
| `art` | works of art and design to look at: galleries, collections, public art | `history`; a building that is itself beautiful (`architecture`) |
| `architecture` | the building or structure as the thing to see | general visual appeal (`views`, `grand`) |
| `science` | the natural world and science explained: specimens, fossils, instruments, experiments (added 28 Nov, when the Natural History Museum had no honest home) | `nature` (being in it) and `learning` (the format) |
| `nature` | living nature met directly: plants, animals, water, open green and wild space | a city view (`views`); specimens and models in a museum (`science`) |
| `views` | seeing a wide scene: a skyline, a river, from height or across water | `photography` (a reason someone comes, see §4) |
| `food_discovery` | tasting, browsing and trying food as the experience | `dining` |
| `dining` | a sit-down meal as the experience | `food_discovery`; a café on site that isn't why you go |
| `shopping` | browsing or buying goods as the experience | a market's food (`food_discovery`) |
| `nightlife` | after-dark social life: bars, music, late venues | an evening opening of a gallery (that's `art`, at night) |
| `learning` | structured explanation: labels, talks, hands-on discovery, **stated by a source** (never assumed because it's a museum) | `history` (subject matter) |
| `play` | activities for fun, especially for children | `adventure` |
| `adventure` | physical challenge or thrill | `play`, `walking` |
| `social` | being with others, or bringing people | `lively` (energy, §2) |

## 2. Atmosphere and sensory dimensions (what an experience feels like)

These are **separate dimensions, not opposites.** "Crowded" is not the opposite of "lively"; "historic" doesn't imply "educational". Each may differ **by time window** (weekday morning, weekend afternoon, evening) and **by season**. Where evidence gives a window, the value is recorded for that window.

| Group | Term | Defined as | Typical evidence |
|---|---|---|---|
| Energy | `peaceful` | calm, unhurried, little to demand attention | official ("a tranquil garden"): **subjective**, so researched at most (see `evidence-rules.md` §3) |
| | `quiet` | low noise | official quiet spaces; inferred otherwise |
| | `lively` | busy with activity and people, by design | official programme (markets, events) |
| Sensory | `crowded` | many people; queues, little personal space | official "busiest times" pages; researched |
| | `noisy` | loud | inferred, low confidence |
| Social character | `intimate` | small, close-up | inferred from size, low confidence |
| | `romantic` | suited to a couple's outing | inferred only; never strong evidence on its own |
| | `family_friendly` | designed for children with adults | official family pages, facilities |
| Visual | `grand` | large, impressive scale | official dimensions or descriptions (subjective: researched) |
| | `unusual` | unlike other places of its kind | researched |
| Intellectual | `thought_provoking` | asks the visitor to think | inferred only |
| | `immersive` | surrounds the visitor | official description of the format |
| Cultural | `traditional`, `contemporary`, `historic` | the period or character of what's experienced | official facts (dates, collections) |
| Environment | `outdoors`, `sheltered`, `green`, `urban` | where the visit happens | official or map facts |
| Adventure | `challenging`, `playful` | physical or play demand | official |

## 3. The 0–2 rubric, and primary versus secondary appeals

**Feature score, for one experience and one dimension:**

| Score | Rubric | Example (from the reference places) |
|---|---|---|
| **0** | No meaningful evidence that the experience offers this. **Not the same as unknown:** "unknown" is recorded when no source has been read on it. | Borough Market's `art`: nothing in its sources mentions art |
| **1** | Present, but secondary or limited: it adds to the visit without being why the visit exists. Needs at least one stated source. | the Natural History Museum's dinosaur gallery's `architecture` (the building around it) |
| **2** | Central: the experience is organised around it, and that is **strongly evidenced** (verified or researched, §4 of `evidence-rules.md`). | Tate Modern's free collection: `art` (the official page describes galleries of modern and contemporary art) |

**0 or unknown (corrected after the consistency review, 28 Nov):** the second assessor and Claude disagreed on 135 of 225 scores, all of them this. The rule is now:
- **0:** the experience's own description was read, and this dimension isn't in it.
- **unknown:** no source read describes that aspect at all (the building, when no building page was read; what's on, when no programme was read).

A 1 needs at least one claim. **An inferred claim may support a 1** (a partial appeal, `evidence-rules.md` §2), never a 2.

**Primary appeal (at most two for each experience)** is the reason the experience exists. It needs:
1. a score of 2;
2. **evidence that the experience is substantially organised around it** (the official description is about it, not merely mentions it);
3. that the experience would not make sense without it.

**Secondary appeal (any number):** a score of 1 or 2 that adds legitimate value without being the reason for the visit.

**Never:**
- a primary appeal from an inferred fact alone;
- a third primary appeal because a third dimension also scores 2;
- an appeal copied to every experience at a place because one experience has it.

**Consistency (Abram's requirement):**
- A second, independent assessor scores a sample of experiences with this rubric alone, without seeing the first scores.
- Agreement is reported for each dimension, and disagreements are resolved in writing.
- See `validation/place-knowledge/consistency-review.md`.

## 4. Traveller interests mapped to place concepts

A traveller's signal maps onto the vocabulary. **The mapping never merges distinct concepts** (Abram: art and history, quiet and peaceful, food discovery and dining, architecture and visual appeal are related but distinct).

| Traveller signal | Maps to | How it influences matching |
|---|---|---|
| Interest "history and culture" (D77) | `history` and `culture`, **as two dimensions** | Evidence of history raises history experiences. It says nothing about `art` |
| Interest "nature" | `nature`, `green`, `outdoors` | |
| Interest "food" | `food_discovery` **and** `dining`, to be split later | It doesn't yet say which, so it supports both at half weight until the traveller's ratings tell them apart |
| Interest "finance and tech" | no place dimension yet | Recorded; it influences nothing until a place dimension exists |
| A loved swipe place | the **primary appeals** of that place's experiences | Evidence for those dimensions only, never for a place's secondary appeals |
| A "didn't enjoy" swipe | that exact place, strongly; and that place's primary appeals, weakly | See `person-to-place-engine.md` §2: never a ban on the whole kind |
| An explicit category dislike ("not museums") | that category | Respected until they change it |
| Feelings ("peaceful", "excited"…) | `peaceful`; `lively` and `adventure`… (the `reasons.FEELINGS` table, re-pointed to the new terms) | A stated choice: moderate evidence |
| "This or that" choices | crowds, cost, transfers, pace, weather | As today |
| Photography (Test A's "how much do photos matter") | a **reason someone comes**, matched to `views`, `architecture`, `grand` | Never a dimension of a place on its own |

**Interpretations are capped, whatever the source** (`experiences.cap`):
- `peaceful`, `grand`, `unusual`, `immersive` and `lively` are **researched at most**. A verified fact (a 25-metre skeleton) supports "grand" only as ODYS's reading of it.
- `romantic`, `intimate`, `thought_provoking` and `noisy` are **inferred at most**, so they can never score 2.

**What the mapping can't do yet:** tell art lovers from history lovers. The onboarding interests merge them, so until a traveller rates or swipes an art place, their art interest is **unknown**, not low.
