# Batch 8 evaluation: the first central person-to-place engine (shadow mode)

**Product commit for every result: `ecba269`.** The engine is `brain/src/brain/match.py`, reached by `GET /v1/me/matches`.

| Check | On `ecba269` |
|---|---|
| Brain tests | **654 passed** (locally, Python 3.12) |
| Engine bench | `validation/engine-bench/2c0b964.md` and `.json`. Recorded under `2c0b964`, a commit that changed only the bench script and documents; the Brain is `ecba269`'s |
| London gate, 3 runs, every run identical | **NOT PASSED:** G2b 5, G11 5, G13 0 (now with the evidence rule), G15 0, everything else 0 (`gate.md`, recorded under `06721a0`, results only) |
| Examples | `examples.md`, from the same code |
| Android | run 62: built, every screen test passed |
| iPhone | run 122: compiled with screenshots (simulator build, upload off) |
| Independent review | `decisions/engine-review-batch8.md`, kept apart from these decisions |

**What this is and isn't:**
- **Shadow mode:** the engine judges places; the planner still makes every plan, and no plan changed (§1).
- **Synthetic travellers only:** 6 from the gate and 8 archetypes, each answering onboarding through the app's own API. **Nothing here is evidence about real people or real enjoyment.**
- **Scores are provisional ranking measures, never chances** (Abram, m363).

The raw results: `validation/engine-bench/2c0b964.json`, and the full report beside it (`2c0b964.md`).

## 1. Measures, each on its own (work package F)

| Measure | Result | How it's measured |
|---|---|---|
| **Ranking consistency** | Engine output identical on 28 of 28 traveller-days across two runs and two commits (`15a6f61`, `e26828f`) | `validation/engine-bench/*.json`, compared field by field |
| **The planner unchanged** | 153 planned stops (lunches included), identical before and after the evidence rule | The same comparison, on the plans |
| **Hard-constraint correctness** | **0** planned stops the engine calls not suitable, over 122 planned places | Bench §3 |
| **Explicit dislikes avoided** | **0** planned stops at a place the traveller (or the planner's kind rule) excludes | Bench §5 |
| **Must-go preservation** | **6 of 6** feasible requests planned, through the planner's own "must include" | Bench §5, must-go trials |
| **The one disagreement** | Sam asked for the British Museum, which he said he didn't enjoy. The planner plans it; the engine rules it out | **Abram's decision** (§4) |
| **Explanation accuracy** | Shown claims on a feature the stop has below tag 2: **116 → 0** after the evidence rule (`e26828f`). G13 now blocks them | Bench §4; gate G13 |
| **Personal relevance** | Planned places: 49 strong, 62 good discovery, 11 low confidence (all 10 of the traveller with no answers, and 1 of the budget traveller), 0 poor | Bench §3 |
| **Diversity** | Mean overlap of two travellers' top 10 (must-go, strong, good) is **16%** over 78 pairs (highest 82%, lowest 0%) | Bench §5 |
| **Evidence quality** | 420 of 557 recommended places (75%) have a reason strong on both sides; the rest say nothing | Bench §5 |
| **Place facts** | Not from the place's own page: the price in 910 judgements, step-free in 630, the hours in 602. Every tag is set by hand | Bench JSON, `missing` |
| **Calibration readiness** | **None.** There are no real ratings, so no score can be checked against outcomes. `scripts/evaluate_export.py` is ready for the first real export | — |

**What these measures can't show (the independent review, `decisions/engine-review-batch8.md`):**
- **0 not suitable, 0 poor and 0 dislikes planned are true by construction.** The engine shares the planner's rules and floor, so they show agreement, not that either is right.
- **116 → 0 is also by construction.** The check tests the rule that was built. It can't say whether a tag of 2 is right: 50 of the 74 ready cards have three or more tags at 2, and one has eight.
- **There's no ground truth.** The synthetic travellers answer by fixed rules, with no hidden true taste. So nothing here measures whether the picks are *right*. The 16% overlap shows travellers differ; random rankings would overlap about 8%.
- **"Low confidence" almost never fires** for anyone who answered: 10 judgements across 13 travellers. Yet the simulated learning curve has a rank correlation of only 0.43 after onboarding. So the engine claims more knowledge than five swipes can support.

## 2. One place, many people (Abram's demonstration)

From the bench at `ecba269`, Friday 4 December, synthetic travellers. Each line is the engine's own words; a reason appears only with evidence on both sides.

| Traveller | Borough Market | Why, or why not |
|---|---|---|
| Food enthusiast (loved Borough Market, Brick Lane, Camden) | **strong match** | "You loved Borough Market." |
| Quiet traveller (picked quieter days; peaceful) | **poor match** | "You picked quieter days, and this place is busy." |
| History enthusiast | **poor match** | "Your answers lean away from good food, and that's what this place is about." |
| Family with children of 6 and 9 | **good discovery** | the loved Natural History Museum walk and "somewhere to bring people", both defining |
| Budget traveller | **poor match** | "Your answers lean away from good food…" |
| The gate's family (didn't enjoy Camden Market) | **not suitable** | the planner's own rule: kinds they didn't enjoy (markets) |
| Someone with no answers | **low confidence** | not enough evidence about this traveller for this place |

The same place gets a different class for each traveller, and each class says why, from the traveller's own answers and the card's own facts. The full tables for Borough Market, the British Museum, Hyde Park, Tate Modern, the Sky Garden and Liberty are in the bench report, §2.

## 3. What the engine shows about the data

1. **Art has nowhere to go.**
   - The art lover gets 1 strong match (Tate Modern, only because they loved it) and 39 poor matches.
   - Tate Modern is tagged history 2.
2. **Food is thin.** The food enthusiast has 3 strong matches, because 12 of the 74 ready cards are food places.
3. **Kinds are excluded broadly.** 92 exclusions come from "kinds they didn't enjoy". One disliked market rules out every market. It's the planner's established rule, carried over in shadow mode and flagged for review.
4. **Facts are mostly the card's, not the place's own** (§1, place facts). Whether a fact is checked or a guess lives in YAML comments that no code reads (`decisions/place-knowledge-model.md`).
5. **Waterloo Bridge's views are a 1 on its card.** "Movement and views" is one tag for two things, so the bridge at sunset now makes no views claim.
6. **A place the traveller loved can score below the planner's floor.**
   - Example: the art lover's Tate Modern, at −1.01.
   - Swipes move the weights on a place's features, not the place itself.
   - The engine calls it a strong match on the evidence; the planner would plan it only as the familiar favourite.

## 4. Decisions for Abram

1. **A request for a place they said they didn't enjoy:** should the request win, as the planner does today, or the dislike, as the engine does? Recommendation: the request wins, because it's newer and explicit. The plan says "You said you didn't enjoy it; it's here because you asked." Hard rules (opening, age, safety) still win over both.
2. **"Kinds they didn't enjoy":** keep excluding every place of a kind after one dislike, or make it a poor match instead, so a single dislike lowers the kind rather than banning it?
3. **The milestone numbers** in `decisions/person-to-place-engine.md` §4. Still open.
4. **The place knowledge model's three questions** (`decisions/place-knowledge-model.md` §6).

## 5. Next stage, prioritised (with the independent review's top five; Claude's hours, GUESSES)

1. **"Not suitable" for hard rules only (about 3 h, after Abram's decisions in §4).**
   - Kind bans become score penalties.
   - A request beats a past dislike, and the plan says so.
   - The two engines then give one answer. Shadow first, bench before and after.
2. **Use the posterior properly (about 4 h).**
   - "Your answers" only when the sign of the lean is clear: `personal.prob_negative` already exists.
   - Confidence from the predictive spread (the Laplace covariance), so "low confidence" means something.
   - A misfit flag where the person loved a place the model scores low, instead of relabelling it.
3. **A bench with ground truth (about 6 h).**
   - Each traveller gets a hidden, noisy true taste, including tastes outside the 15 tags, and answers from it.
   - Held-out answers, and one swipe flipped at a time.
   - A rainy day and an evening; group checks; three runs; how concentrated plans are.
4. **Primary appeals, and the place knowledge model's first steps (about 4 h plus 11 h, and about 1 h of Abram's).**
   - One or two anchored primary appeals per card, with a written rubric for a 1 and a 2.
   - Tate Modern as art, not history.
   - The schema in code, and CHECKED and GUESS moved from comments into evidence fields.
5. **Keep the planner off the classes** until the friends' round gives a first real rank correlation, and Abram approves. **This is the first change to live plans,** measured on the bench and the gate before and after.
6. **Later:**
   - new dimensions for the 74 places (art, architecture, shopping, nightlife, atmosphere; about 12 h);
   - the Overture quality sample (about 3 h) before any open-data place reaches the engine.
