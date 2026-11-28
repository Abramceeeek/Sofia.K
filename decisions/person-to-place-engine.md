# The person-to-place engine: audit and proposed architecture (26 Nov 2026)

Abram's required first deliverable (m362), before any large implementation: what the recommendation engine does today, what is partial or missing, the proposed architecture, what is reused, and how improvement is measured. **Everything below is read from the code and data at `388d7dc`**, with file references. Nothing here is customer evidence: ODYS has no real ratings yet.

## Abram's decisions on this document (26 Nov, m363)

1. **Six classifications, not five.** Each place gets one:
   - **explicit must-go:** the traveller asked for it;
   - **strong match;**
   - **good discovery;**
   - **low confidence:** we don't know enough to judge;
   - **poor match;**
   - **not suitable:** a hard restriction or explicit exclusion.

   **A must-go records intent, not predicted enjoyment.** It never overrides opening hours, safety or eligibility.
2. **Scores are provisional ranking measures, not probabilities.** No score is described as a chance of enjoyment. "0.75" never means a 75% chance of a good visit. Calibration needs real labelled feedback and its own validation.
3. **A proper place knowledge model, not six more tags.** It covers:
   - what makes a place special, and what a visitor does there;
   - how it feels, and which interests it serves;
   - who might enjoy it and who might not;
   - duration, cost, effort, suitability for children, the best time, and its limitations;
   - how reliable each fact is.

   One place can appeal to different people for different reasons. Proposal: `decisions/place-knowledge-model.md`.
4. **The friends' round stays behind the gate.** G2b and G11 still fail, and the gate isn't weakened to start it.
5. **Batch 8 is approved:** the first central person-to-place engine, **in shadow mode**. It runs beside the planner and changes none of its decisions. The six classes replace the five bands of §2. §2's thresholds survive only as provisional score cut-offs (GUESSES), never as chances.

## Decision first

- **Keep the core. It is the right shape, and rewriting it would throw away tested work:**
  - a person model that starts at the population and moves with each answer (`personal.py`);
  - a route-and-time solver (`planner.py`, OR-Tools);
  - place facts that carry their source and date (`catalogue.py`, the checked layer).
- **What holds ODYS back is narrower than "the algorithm":**
  1. **Places are described thinly.** There are 74 ready London cards. Each has 15 hand-set tags from 0 to 2. There is no atmosphere, art, shopping, nightlife or cuisine, and facts are checked for only 35 cards (§1.2).
  2. **The traveller model can only learn what the tags describe.** A taste for art, nightlife or a cuisine has nowhere to go (§1.1).
  3. **Whether a place suits a person is decided in seven places, with no single answer** (§1.3). Must-go, strong match, good discovery, low confidence, poor match and not suitable exist only as scattered rules, or not at all.
  4. **Reasons can cite a feature the stop barely has.** That caused every "stretched reason" the reviews found (§1.5).
  5. **Every measure is synthetic** (§1.6).
- **Proposal: one `match` step that every planner uses** (§2):
  - it gives each (person, place, day) a class, a provisional score and the evidence behind it;
  - richer place records, built on the existing catalogue;
  - reasons that need strong evidence on both sides.
- **The day planner, trip days, food and group trips all consume the same match**, so group planning stops being a second, weaker engine.
- **Measure first** (§3): a fixed "engine bench" of travellers, dates and settings, run on every version beside the London gate, with raw results kept.
- **Next step proposed** (§6, about 14 h of Claude's time):
  - the engine bench;
  - the match step with its six classes (m363), compared against today with no change to plans yet;
  - the evidence rule for reasons.
- **Milestones M1–M7 with proposed numbers for Abram to agree** (§4). Every threshold is a GUESS until agreed. None is made easier to pass.

## 1. What exists today

### 1.1 Understanding the traveller

| Signal | Where it comes from | How it's used today | Status |
|---|---|---|---|
| Reactions to London places | 16 swipe places, 6 before the first plan (D112): Loved / Fine / Didn't enjoy / Haven't been / Not sure | An ordered-logit observation on the person's weights (`scoring.swipe_observation`). A loved place's card is protected and becomes a trip day's must-do (`api.trip_days.loved_for`). A disliked place's cards are never planned, and nor are other places of a kind they disliked (`dayplan.kept_out`) | Implemented |
| "This or that" days | 5 before the first plan, 5 later (D112): transfers, weather, pace, crowds, cost, walking | Binary-logit observations on the same weights | Implemented |
| How they want to feel | "Why you go out" (excited, curious, restored…) | Stated observations (`reasons.feeling_observation`), plus the day's feel line and reasons | Implemented |
| Interests | Finance & tech / food / history & culture / nature (D77, D83) | `aspiration_match`, a personal feature, through `data/aspiration.yaml` | Implemented; four fields only |
| Company and activity | "Improve future plans" (D127) | Stated leanings. Activity sets the journey budget by pace and keeps strenuous places out for a gentle pace. A "family" profile turns on age rules | Implemented |
| A trip's children | Ages on "Who's going" (m356, m359) | Age rules (minimum age; places for younger children); children's prices where a card's source gives one | Implemented (batch 6) |
| Budget | A band a day, per person (m356) | The day's budget constraint; lunch chosen to fit | Implemented |
| Day Feel | Relaxed / Balanced / Full, per trip (m346) | Extra places and longer stays, **separate from pace** | Implemented |
| Ratings | 1–5 after each stop | An ordered-logit observation with the conditions (weather, journey) | Implemented; **no real ratings yet** |
| The day as a whole | "Worth it?" and "Again?" (D127) | Stored; **not used by the model** | Partial |
| Corrections | "Not right" on "So far" (D117) | That answer stops counting | Implemented |
| Must-go | One `must_do` per day plan; `keep` when swapping a stop | The planner must include it if it fits | **Partial:** one place per plan, and not a trip-wide list |
| Places already visited | Implied by swipes ("Haven't been" means not visited) | `familiar`: exactly one loved place per plan, the rest new | Partial |
| Appetite for discovery | — | Only the `local_novel` tag weight | **Missing** as its own dimension |
| Atmosphere (peaceful, lively, romantic, unusual, social, family-friendly) | Partly through feelings and `crowds`, `awe`, `social_pull` | — | **Missing** as place facts |
| Art, shopping, nightlife, photography as interests | `photo_potential` is a tag; the others have none | — | **Missing** |
| Step-free need | Only in the group planner (`group.Member.needs_step_free`) | — | **Missing** in personal plans |
| Food needs (diet, allergies) | Not asked: D19, D123, privacy | — | Deferred by decision |

**The model** (`personal.py`, `population.py`, `data/priors.yaml`):
- the person's weights b + δ over 26 features, 25 of them personal;
- prior sd 0.75 on most;
- the cost weight is kept negative on a log scale (D88);
- the answer is a Laplace approximation, found by Newton's method.

**Its numbers are guesses.** `priors.yaml` says "Nothing here is estimated from data yet". The exceptions are the swipe cutpoints, fitted on the swipe page (12 people, 235 answers, 27–28 Sep), and the swiping level (m135).

**What we know about learning comes from simulation only** (`benchmarks/synthetic/learning_curve.txt`, 300 simulated people drawn from the model's own priors):
- the rank correlation between true and estimated tastes is **0.43 after onboarding, 0.64 after 20 rated stops and 0.74 after 40**;
- that is a ceiling: real people are noisier, and have tastes the tags don't describe.

### 1.2 Understanding places

| Data | What it holds | Status |
|---|---|---|
| **Moment cards** (`data/moments/`, `moments.py`) | 78 cards, 74 ready in London (67 moments, 7 area wanders). Each card holds: the place, the approach, how long the visit takes, best times, opening windows (15 with day-specific times, 19 with dated changes), price (child price on 5), what the price is for, a meal flag, rules (on 2: a minimum age, children only), 11 place and 4 moment tags (0–2, **set by hand**), a shot card, and source and date checked (47 last checked in September, 2 in October, 25 in November) | The planner's working data |
| **The catalogue** (`catalogue.py`, `data/catalogue/london.yaml`) | 76 London entries as `Experience` records. Each fact (price, setting, accessibility, transport, area) is a `Fact` with its trust, source and date. "Unknown" is never read as no | Implemented |
| **The checked layer** (`london_checked.yaml`) | 35 cards with facts read from official pages: hours (31), step-free (15), area (13), dated notices (11), price (9) | Implemented; **covers half the cards** |
| **Kinds** (`london.yaml` `type`) | restaurant, market, museum, roof garden… | Used for "kinds they didn't enjoy" and meal spacing (G15) |
| **Overture pull** (23 Nov, `decisions/plan-london-then-cities.md`) | 781,690 places in Greater London; 70,291 food and drink, 49,126 of them confident. Cuisine is well covered. Diet labels are thin (115 halal). No hours or prices | **The pull isn't stored in the repository, and no planner uses it.** A card's place can carry an `overture_id`, which links it to Overture (`places.py`) |

**Missing from the place model:**
- atmosphere and experience type beyond the 15 tags (peaceful, lively, romantic, unusual, art, shopping, nightlife);
- crowds by time of day (one `crowds` tag, plus the free-text crowd window);
- seasonality beyond dated hours;
- walking detail beyond `walking_effort`;
- food facets (cuisine, meal kind, price band, dietary labels with their source) for all but a handful of cards;
- a confidence for each tag: the tags have never been compared with people's reactions.

### 1.3 Matching a person to a place

The score is **S = x · (b_population + δ_person)**. The chance of "Good" comes from the rating cutpoints (`scoring`, `explain.p_good`). **Whether a place suits someone is decided in seven places:**

| Where | What it decides |
|---|---|
| `dayplan.kept_out` | Kinds they didn't enjoy, age rules, places only for children, strenuous places at a gentle pace (hard exclusions) |
| `planner.plan_day` | The floor (predicted at least "Good"), opening windows, budget, the journey budget by pace, at most two history stops a day and never two in a row, variants, area wanders, sunset windows |
| `dayplan._personal_plan` | Loved places (one familiar favourite), the popularity nudge (D113), extra places only at a chance of 0.65 or more (m333), lunch and dinner candidates |
| `api.trip_days` | A loved place as a day's must-do, no place twice in a trip, backtracks and meals planned again |
| `quality.assess` | Four perspectives (relevance, practicality, money, trust), each good, fair, poor or unknown. **Used by discovery's ranking, not by the day planner** |
| `group.plan` | Its own selection over catalogue records from the weights alone. No interests, and no day planner |
| `triplength.suggest` | How many days the person's matches fill |

**There is no single match result.** The five classes Abram names don't exist as one object:
- **Not suitable:** scattered across `kept_out`, opening rules and the budget;
- **Must-go:** `must_do` and `keep`;
- **Strong match:** the old match words, removed from the app by m275;
- **Good discovery:** nothing;
- **Poor match:** below the floor.

So each planner re-implements part of the judgement. The group planner showed it: its "favourites" came from the weights alone, and the food lover's favourites turned out to be two museums (batch 6 reviews).

**Food** (`dayplan.lunch_candidates`, `dinner_candidates`, m321, m334, m360):
- lunch and dinner are a food card nearby, or a "lunch near X" slot;
- the choice weighs cost and the person's food weight;
- substantial meals are three hours apart (m360);
- **no cuisine, no Overture places, no named food beyond about 12 cards.**

### 1.4 Building the day

`planner.py` solves an orienteering problem with time windows:
- prizes are utility above the floor;
- journeys cost the person's own transfer weights, scaled by pace;
- the constraints are the budget, the journey budget by pace, the history rule, lunch and dinner slots, one area wander, rides, sunset windows and the person's own time.

`dayplan` and `api` then add:
- rain swaps, with their cost disclosed;
- "open until";
- free time, said on the plan;
- re-planning to avoid backtracks and close meals;
- each trip day's stretch;
- the way to the airport on the last day.

**Known gaps (batch 6 reviews):**
- **no day costs or times the way back** to where it started, so a day "within budget" goes over with the fare home;
- returns to an earlier spot under 3 km aren't caught;
- Relaxed and Full can come out with the wrong amount of rest.

### 1.5 Explaining a choice

Where explanations come from:
- `reasons.py`: "You loved X, and this has Y too", feelings, ratings, interests, quiet and cheap;
- `explain.py`: the planner's own inputs;
- `factor_line`: the line beside the price, which never gives a chance (m275);
- `group.who_it_suits`: why a stop is in a group's plan.

**The cause of every stretched reason the reviews found:**
- since m353, a loved place is named only when the feature is what defines it (its tag is 2);
- but **the stop itself needs only a tag of 1** (`reasons._reasons`: `tags.get(f, 0) >= 1`).

So "something absorbing to do" is said of a quiet terrace, and "a sense of awe" of a department store.

**Two more gaps:**
- the text isn't checked against the time of day ("among people heading to work" at 18:12);
- G13 catches only known patterns.

### 1.6 Measuring quality

| Tool | Measures | Status |
|---|---|---|
| London gate (`scripts/london_gate.py`) | G1–G15 on 6 synthetic travellers plus 2 Day Feel variants: 3 runs, a 1 s solver limit, fixed dates; quality measures beside it | Runs on every batch. **Not passed** |
| Synthetic benchmarks (`benchmark_profiles`, `benchmark_ranking`, `compare_onboarding`, `learning_curve`, `compare_food_interest`, `compare_group`) | Ranking, onboarding and learning, inside the model's own world | Exist; not run on every version |
| Real-data read-outs (`evaluate_export`, `learning_milestones`, `testb_report`) | Calibration of predicted vs rated, learning by milestone, the Test B pair | **Ready but unused: no real ratings yet** |
| Three AI reviews a batch | A London local, families and gentle pace, a sceptic | Direction only, never customer evidence |

**What's missing:**
- a fixed, versioned benchmark of person-to-place quality (the gate judges days, not whether the right places were chosen);
- a measure of how different travellers' recommendations are;
- a measure of Must-go reliability;
- any human ratings.

### 1.7 Group trips (supporting)

`group.py` is fair (Nash welfare) and private (m353, m361), but it runs its own selection:
- it uses the members' weights only, plus each member's first loved place and their dislikes;
- it doesn't use their interests or the day planner;
- so shared days are a list of places.

## 2. Proposed architecture

**Four layers. Each reuses what exists.**

```
 Traveller profile ──┐
 (answers, ratings,  │      ┌────────────────────────┐     ┌──────────────────────┐
  hard rules, list   ├────▶ │ match(person, place,    │ ──▶ │ Day builder          │ ──▶ plan, reasons
  of must-go)        │      │       day, context)     │     │ (planner.py, dayplan) │
 Place record ───────┘      │ → class, score, evidence│     └──────────────────────┘
 (catalogue facts with      └────────────────────────┘        ▲ also: trip days, discovery,
  source and date)                                              food, group (Nash on members' matches)
```

**1. The place record:** extend `catalogue.Experience`, with no new store.
- **New facets, each a `Fact` with trust, source and date:**
  - experience types and atmosphere, from a fixed vocabulary: peaceful, lively, romantic, unusual, social, family-friendly, art, shopping, nightlife, photography;
  - crowds by time window;
  - seasonal suitability;
  - walking and access detail;
  - food: meal kind (substantial, tasting, snack, coffee), cuisine, price band, dietary labels (only from a stated source, never inferred).
- **Missing stays unknown, never false.**
- The existing 15 tags stay, because the model's features are built on them.
- Each new facet enters the model only when places carry it, so no question is asked without a use.

**2. The traveller profile:** keep `personal.py` and the observations as they are, and add:
- **hard rules apart from tastes:** age (from the party), step-free need (asked only when someone wants it), later dietary needs (behind consent, a DPIA and a checked data source, as decided);
- **a must-go list for each trip**, not one place per plan;
- **"not this time" for each trip**, as distinct from a "Didn't enjoy";
- **appetite for discovery:** familiar or new, derived from the swipes' "Haven't been" share and the `local_novel` weight, with no new question.

**3. Match:** `brain/src/brain/match.py` (built in batch 8, m363). `match(traveller, place, day)` returns the **class**, the first that applies:
1. **Not suitable:** a hard restriction or explicit exclusion. Examples: closed that date, an age rule, a place they didn't enjoy (or a place of that kind), too strenuous for a gentle pace, dry-weather only on a rainy day.
2. **Explicit must-go:** the traveller asked for it. This is intent, not predicted enjoyment, and it never overrides class 1.
3. **Low confidence:** the score rests on the population average. Nothing the person has said touches this place's defining features, and no direct signal does (loved, disliked, rated, asked for, an interest or a feeling).
4. **Strong match:** score at least the strong cut-off, with at least one piece of evidence that is strong on both sides.
5. **Good discovery:** at or above the planner's floor.
6. **Poor match:** below the floor.

It also returns:
- **score:** the person's utility for the place, in the model's own units. It's **a provisional ranking measure, never a chance**. The floor is the planner's existing −0.75. The strong cut-off is 1.1 above it (+0.35, a GUESS: the position of the old "0.75" line, kept only as a score cut-off);
- **factors:** the strongest positive and negative terms, each labelled with its person side (a stated answer or the population default) and its place side (a defining tag, a partial tag, or a checked fact);
- **evidence:** references to the card's field, the checked source and its date, and the person's answer;
- **missing:** place facts not known (step-free, a child's price, checked hours) and traveller facts not known;
- **confidence:** how much rests on the person's own answers, and how much of the place's side is checked rather than hand-set;
- **reason:** one sentence, only when the evidence is strong on both sides; otherwise none, and the class says why.

It reuses `kept_out`, the opening rules, `scoring`, and the reasons' evidence. It does **not** yet use `quality.assess`, whose four perspectives are a next step (the batch 8 review caught an earlier claim that it did). **In batch 8 it runs in shadow mode only.** Later, once comparisons justify it and Abram approves, the planner takes the classes:
- prizes come from Must-go, Strong and Good discovery;
- Low confidence and Poor come in only to fill a day where that's allowed today;
- Not suitable never comes in.

**4. The day builder:** `planner.py` as it is. It's fed matches instead of raw candidates, and carries the evidence into each stop's reasons.
- **Reasons are built only from evidence.** A feature needs a tag of 2 on the stop, or a checked fact, as well as a clear lean from the person.
- **The text is checked against the visit's time.**
- **Food:** food places become ordinary places with food facets. Overture and OpenStreetMap provide candidates. An unchecked one can be offered only as "an option nearby, not checked", and planned only once it is checked.
- **Group:** each member's matches, Nash welfare over them, then the same day builder on the chosen places. This is the design paused in m362.

## 3. How improvement is measured

**A fixed engine bench**, `scripts/engine_bench.py`, run on every version beside the gate. Raw results go to `validation/engine-bench/<commit>.md`.

**Its travellers:**
- the gate's 6;
- the 11 benchmark profiles;
- 6 new archetypes: an art lover, a night owl, a shopper, a photographer, a family with a toddler, and someone who needs step-free access.

All are synthetic, with fixed dates, seeds and solver settings.

**Measures for each version (raw numbers, never only an average):**

| Measure | Why |
|---|---|
| Not suitable in any plan (must be 0) | Safety and trust |
| Must-go kept, where it can be | M3 |
| A disliked kind or place shown | M2 |
| Classes of planned stops (must-go, strong, good discovery, low confidence, poor) | Personal fit, and how much rests on guesses |
| How different travellers' top 10 overlap (mean pairwise Jaccard) | Personalisation, not popularity |
| Reasons backed by strong evidence on both sides | No invented reasons |
| The least-served traveller, as well as the average | Fairness, and groups |
| Journey minutes, walking, rests, free time | Fatigue and realism |
| G1–G15 | The day itself |

**Real evidence, kept apart from all of the above:**
- the six moderated sessions;
- once the round runs, the friends' ratings through `evaluate_export.py` (calibration of predicted against rated, and their rank correlation).

## 4. Milestones: what each measures, how, and how independent the measure is (revised 28 Nov, m364; for Abram to agree)

**Abram's principles (m364):**
- hard safety and eligibility rules: 100%;
- explicit exclusions: 100%;
- explanations: no unsupported claims;
- personal matching: improves against an *independent* benchmark;
- real-world satisfaction: measured separately, from real feedback;
- no target is ever lowered because the algorithm struggles.

**Three kinds of measure, never mixed** (Abram, m364):
- **[R] Rule-keeping:** does the engine obey its own rules? Necessary, but it proves nothing about whether the rules are right.
- **[S] Synthetic recovery:** does it recover hidden preferences it can't see, from a generator that shares none of its scoring code? Evidence about the method, never about real people.
- **[H] Human:** do real travellers enjoy what it recommends? The only evidence of satisfaction.

| Milestone | Measure | How it's calculated | Kind | Proposed threshold |
|---|---|---|---|---|
| **M1 Place knowledge** | Records to the standard | Share of ready places whose experiences pass `experiences.py`'s validation (every claim has a status, a source or "unknown", and a date) | R | 100% of ready London places |
| | Planner-critical facts verified | Share of ready places with hours, price, age, booking and dated closures **verified** and unexpired (`evidence-rules.md` §4) | R | 100% |
| | Facts are true | A random audit of 20 verified claims against their sources, by someone other than the author | H (a person checks) | 0 false |
| | Scoring consistency | Agreement between two independent scorings of a sample (`place-vocabulary.md` §3), for each dimension | S (two assessors) | at least 80% exact agreement on primary appeals; disagreements resolved in writing |
| **M2 Personal matching** | Eligibility | Plans that include a place failing a verified hard rule | R | 0 |
| | Explicit exclusions | Plans that include a place the traveller currently excluded, or a category they explicitly excluded | R | 0 |
| | Unsupported reasons | Shown reasons whose place side isn't verified or researched at 2, or whose traveller side isn't clear evidence | R | 0 |
| | Recovery of hidden tastes | Rank correlation and top-10 precision between the engine's ranking and the hidden-truth ranking (`scripts/hidden_bench.py`), against a population-only and a random baseline | S | above both baselines for every archetype, and better than the previous engine version |
| | Appropriate difference | Top-10 overlap between travellers whose hidden tastes overlap, against travellers whose don't (relevance, not maximum difference: Abram) | S | overlap tracks hidden similarity (positive correlation) |
| | Honest uncertainty | Of the engine's low-confidence judgements, how often its ranking is wrong against hidden truth, compared with its confident ones | S | confident judgements wrong less often than low-confidence ones |
| **M3 Must-go reliability** | Requests kept | Feasible requests planned; infeasible ones explained | R | 95% kept; 100% explained |
| | The cost of keeping them | G11 and G12 with and without the requests | R | no worse |
| **M4 Excellent days** | The gate | G1–G15, 3 runs | R | pass in 3 of 3 |
| | Reviewers | Three AI reviewers per traveller (direction only) | S | 7/10 or more; no false statement |
| **M5 London validation** | Moderated sessions | Median of "I would trust this plan" across six sessions; tasks failed unaided | H | median 4/5 or more; no task failed by more than 2 of 6 |
| | Friends' round | Mean rating of planned stops; rank correlation between predicted and rated, with its 95% interval (`validation/stage2-sample-size.md`) | H | mean 3.5/5 or more; correlation above 0 with its interval excluding 0 |
| **M6 Second city** | The same measures | M1–M4 on a city with at least 50 places to the standard | R, S | the same thresholds |
| **M7 Public launch** | Readiness | The legal gates (`CLAUDE.md`), operations, privacy, support | — | Abram's call |

**Every threshold is a proposal until Abram agrees it,** and none is made easier afterwards. Each R measure is labelled as rule-keeping wherever it is reported, so a 100% there is never read as proof that the rule is right.

## 5. What is reused, what changes, and the hours

| Part | Reused | Changes | Claude's hours (GUESS) |
|---|---|---|---|
| Person model (`personal`, `population`, `scoring`, observations) | All | New features only when places carry the facet | 2 |
| Catalogue and checked layer | All | Facet vocabulary; food facets | 6, plus about 12 to fill 74 London places from official sources (D91) |
| `match.py` | `kept_out`, `quality`, `scoring`, reasons' evidence | New: classes, evidence, blockers | 8 including tests |
| Planner and `dayplan` | All | Take matches; a must-go list for each trip | 4 |
| Reasons | Wording | The evidence rule (tag 2 on the stop); a time-of-day check | 3 |
| Engine bench | Gate personas, benchmark profiles | New script and archetypes | 6 |
| Food from open data | The Overture and OSM pilot | A candidate pipeline, unchecked or checked | 8 (later phase) |
| Group onto the engine | `group.py` fairness and privacy | Members' matches, then the day builder | 8 (later phase) |

**Phase 1** (bench, match, evidence rule, facets for London) is about 41 h of Claude's time, over about three batches. Abram's part is about 1 h: agree the milestone numbers (the classes and facets are decided, m363).

## 6. Proposed order

1. **Batch 8 (about 14 h): measure first.**
   - The engine bench and its baseline at `388d7dc`.
   - `match.py` with the six classes, run beside today's planner with no change to plans, reporting where the two disagree.
   - The evidence rule for reasons, with G13 extended to check it.
2. **Batch 9 (about 18 h).**
   - Facets for the 74 ready London places, from official sources, with Abram's one-line review list (D91).
   - The new archetypes.
   - Bench and gate again.
3. **Batch 10 (about 12 h).**
   - The planner takes matches.
   - A must-go list for each trip.
   - Food facets for named food places.
   - The way back costed and timed.
4. **Then** food from open data, and the group planner onto the engine.

## 7. Decisions for Abram

Answered on 26 Nov (m363; see the top of this document):
1. **The classes:** six, with must-go as intent.
2. **The thresholds:** not probabilities; provisional score cut-offs only.
3. **The place model:** a proper knowledge model.
4. **The friends' round:** stays behind the gate.

**Still open:** the milestone numbers in §4. They become gates only once agreed, and are never made easier afterwards.

## 8. Where ODYS stands (facts, 26 Nov)

- **Not launched.** No friend has been invited. The round waits for the London gate (`validation/friends-round.md`).
- **Branch `claude/pensive-euler-fftd63`:** nothing on it is merged, deployed or uploaded.
- **The London gate, the engine work's baseline:** **NOT PASSED** at `388d7dc`, 3 runs, every run identical. The file records `d0c6dfe`, the audit's own commit, which changes only this document.
  - G2b fails 5 times and G11 5 times; G15 (new) and every other check pass.
  - At `05ea04c` it was G2b 6, G11 5. The friends' Friday no longer ends 73 min early.
  - Unused time is 1,781 min (1,881 at `05ea04c`).
  - What still fails:
    - **G2b:** Full and Balanced days ending 65–117 min early, and the friends' Relaxed day with 397 min of visits and no break;
    - **G11:** the family's days at 96–102 min of travel against 60, mostly Tube or bus; Jonas's at 83, mostly walking.
- **Other cities:** Seville is a read-only preview for Abram's own phone (m320). Paris is development data only. Neither has day plans.
