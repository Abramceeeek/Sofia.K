# The Brain: how good are the recommendations, and is it ready for the world? (independent review, 11 Nov 2026)

**Decision.** The engine is well built and unusually honest about itself: a small, sound statistical model, a planner that keeps hard rules, and explanations taken from its real inputs. **What it can't yet do is know a person.** Every population number in it is a guess, the short onboarding moves a plan only a little, and by a new benchmark it takes about **20 rated stops (five days out)** before its picks are reliably the person's own, in a best case that real people won't match. That is a fact about data, not a fault in the code. It is **not ready for any city but London**, and what blocks it is not the model: it is cards, travel times and a dozen places where London is assumed.

Everything measured here is on **synthetic people** with a fixed seed, and says so. Nothing was tuned to it, no real answer was read, and the frozen Test B was not touched.

## The model, in a statistician's terms

- **Utility.** `S = x·β`, linear in 26 named features of a stop: 15 tastes (place and moment tags, 0 to 1), cost per £10, four weather interactions, two travel-time hinges (15 to 30 minutes, over 30), two day-shape terms, an interest match and a swiping level.
- **People.** `β_person = b_population + δ`, with `δ ~ N(0, diag(σ²))`, σ = 0.75 on almost everything. Cost is on a log scale (`β = b·e^δ`) so it can't change sign.
- **Three kinds of evidence, one δ:** a binary logit on each "this or that" pair; an ordered logit with three levels on each place swipe; an ordered logit with five levels on each stop rating. Scales and cutpoints are held fixed.
- **Fitting.** The posterior mode by damped Newton, with a Laplace approximation for its spread (`personal.py`, 194 lines, numpy only). Refitted from all of a person's answers each time one arrives.
- **Planning.** OR-Tools routes the day to maximise the sum of utilities less travel, inside opening hours, the budget, the person's own time, and shape rules, within a time limit.

**What is sound:** the likelihoods are standard and log-concave; the sign constraint on cost is done properly; the spread is carried, so the app can say "unsure" (`named_weights` only names a weight when it is 80% sure of its sign); the same maths could run on the phone; and the code states which numbers are guesses.

**What it is not:** hierarchical in practice. `brain/data/priors.yaml` says of itself "Nothing here is estimated from data yet". All 15 taste weights start at exactly zero for everyone, every σ is the same guess, all three evidence scales are 1.0, and the rating cutpoints are a symmetric guess. Only the swipe cutpoints were fitted, from 12 people. So "each new user starts at the mean of similar users" (CLAUDE.md) is the design, and there are no similar users yet: a new person starts at "cheap, uncrowded, close together".

## How fast does it learn a person? (new benchmark)

`brain/scripts/learning_curve.py`, 300 synthetic people, seed 20261111, the 49 ready cards (`brain/benchmarks/synthetic/learning_curve.txt`; three tests). People's tastes are drawn from the model's own prior and they answer exactly as the model assumes, so this is a **ceiling**. "Gain kept" is the true value of the model's four best cards for the person over the generic four, as a share of what knowing them exactly would gain.

| After | Rank correlation with their true order | Of their true top 8, found | Gain kept | Their four beat the generic four |
|---|---|---|---|---|
| The onboarding only (6 places, 5 choices) | 0.43 | 2.8 | 28% (± 3) | for 68% of people; worse for 31% |
| 4 rated stops (one day) | 0.49 | 3.0 | 42% | 73% |
| 8 (two days) | 0.54 | 3.4 | 50% | 81% |
| 20 (five days) | 0.64 | 4.1 | 64% | 86% |
| 40 (ten days) | 0.74 | 4.7 | 71% | 88% |
| 20, if people also have a taste the tags can't describe (sd 0.75, a GUESS) | 0.54 | 3.7 | 54% | 86% |

Three things follow.

1. **After the onboarding alone the personal plan is a modest favourite, not a sure thing.** In the model's own world it beats the generic plan for 68% of people and loses for 31%. This agrees with the project's own benchmark (m206: better on 78 of 132 days, worse on 53).
2. **Ratings are where the product is.** One rated day does more than the whole onboarding added over the starting point. This is the strongest argument in the audit for getting people to a first rated stop quickly (`odys-market-and-product-strategy.md`).
3. **The catalogue runs out before the model is done.** Forty ratings is most of the 49 cards. In London today a person finishes the content at about the point the model begins to know them.

Also tested: whether it matters that the app only learns from stops it already chose (the app's own days against random days). It doesn't, here: the two learn at the same rate.

### What this means for Test B

Test B asks each tester to choose between the personal and the generic plan. If the model's best case holds, a tester picks the personal plan with probability about 0.68; with real people it will be lower.

| If the true chance of choosing the personal plan is | "7 of 10" passes | "14 of 20" passes | Testers needed to tell it from a coin (80% power, one-sided 5%) |
|---|---|---|---|
| 0.50 (no effect) | 17% | 6% | — |
| 0.55 | 27% | 13% | about 616 |
| 0.60 | 38% | 25% | about 152 |
| 0.68 (the model's own ceiling) | 60% | 53% | about 46 |

The project already calls Test B "formative" and knows the 17% (D127). The new point is the other side: **even if the idea works as well as its own model says, ten or twenty testers will fail the test almost half the time.** A pass will be weak evidence and a fail weaker. Two consequences:
- Read the paired "fits me" scores (already a co-primary result) and the ratings on the day, not the count.
- A decisive answer needs about 50 testers at the ceiling, and more in reality. That is a recruiting cost to weigh at Checkpoint 3, not a reason to wait.

## Where the recommendations are strong, and where they aren't

| | Evidence | Judgement |
|---|---|---|
| **Feasibility** | The project's benchmark: 0 of 1,188 plans broke a hard rule (hours, open days, budget, own time), checked from outside the solver | **Strong.** This is the real edge over a chatbot |
| **Explanations** | Built from the planner's inputs (m219), "unknown" said as unknown | **Strong**, and rare |
| **Telling kinds of traveller apart after onboarding** | The project's table: a nature lover keeps 69% of the possible gain; museums 24%; food 11%; active 13%; family 0%; **relaxed, budget, dietary and accessibility travellers get plans worse than no answers at all** | **Weak.** Four of the six onboarding places are green spaces or views, so nature is the one taste learned |
| **"A strong match for you"** | A 75% chance of rating it Good or better, from cutpoints that are a guess | **Unvalidated.** The label is a probability claim with nothing behind the scale yet. Check it against the first 100 real ratings: of stops called strong matches, did about 75% get Good or better? (~2 h for a script) |
| **Dietary needs and accessibility** | Step-free access is unknown for 82% of planned places; no card says whether food is halal, vegetarian or kosher | **Not served.** These are not tastes to be weighed; they are rules, and the data to apply them doesn't exist. The project already declines to claim them, which is right |
| **Variety** | One card (the Garden at 120) is in 39% of the benchmark's personal plans | A small catalogue, not a model fault |
| **Search quality** | A day takes 4.7 s on this machine (several solves at the 1 s limit each); on days with own time the 1 s search loses to a simple greedy plan on 5 of 33 days (m206) | Adequate. Start the solver from the greedy plan, as m206 already recommends (~2 h) |
| **Numerical safety** | Two overflow warnings in about 40,000 fits (a line-search step on the log-scale cost that the search then backs away from); no fit returned a non-number | Fine. Worth a guard so a non-finite result is never stored (~0.5 h) |

## An improvement proposed and tested: a personal rating level

The model lets each person swipe more or less warmly (`swipe_level`, m135) but has no such term for ratings. Someone who calls every stop "Great" would look like someone who likes whatever those stops share.

Tested on the same benchmark, with people given a personal rating level (sd 1.0, a GUESS) and the same answers fitted both ways (random days: tables D and E of the benchmark file, 300 people; the app's own days: a separate run of 200 people with the same script, not kept in the file):

| After 20 rated stops | Today's model | With a `rating_level` term |
|---|---|---|
| Random days: gain kept | 55% (± 2) | 54% (± 2) |
| The app's own days: gain kept | 60% (± 3) | 62% (± 3) |
| The app's own days: true top 8 found | 4.13 | 4.24 |

**Result: no gain worth having.** Ranking is what the planner uses, and a constant added to every rating barely changes a ranking. I'd leave the model as it is, and revisit with real ratings, where how much people differ in generosity can be measured rather than guessed. Recorded here so it isn't tried twice.

## Can it tell these travellers apart?

The brief's ten kinds, against what exists:

| Traveller | Can the model represent it? | Can it learn it from the onboarding? (project's benchmark) | What's missing |
|---|---|---|---|
| Nature | Yes (`green_nature`, `outdoor_exposure`) | Yes: 69% of the gain | — |
| Food | Yes (`food`) | Barely: 11% | One food place among the six asked |
| Architecture and museums | Partly (`history_culture`, `iconic`; no architecture tag) | Some: 24% | A tag, and places that split on it |
| Shopping | No taste dimension; five shopping cards exist | Not measurable | A tag or a kind-of-place question |
| Active | Yes (`active`, `walking_effort`) | Barely: 13% | Active places among those asked |
| Relaxed | Only through the day's pace | No: worse than no answers | A direct question; it is asked later, in "Improve future plans" |
| Family | No: nothing knows a child's age, a buggy or a child price | No: 0% | Data, and it is a set of rules as much as a taste |
| Budget | Yes (cost weight) | No: worse than no answers. Two of five choices carry cost | A direct budget question does more than inference; one exists |
| Dietary needs | **By design not a taste.** A filter the person sets, never inferred, never a proxy for belief | n/a | Certified venue data (none licensed), consent, the DPIA (drafted, unsigned) |
| Accessibility | **A rule, not a taste** | n/a | Step-free and access data for 82% of places |

So: three of ten are distinguished today, in London, after onboarding. The rest need either a direct question (cheap), more varied places to react to (cheap), or data that doesn't exist (dear). No sensitive characteristic is inferred anywhere in the code, and the food design keeps diet apart from religion (`food.py`, `food-preferences-and-privacy.md`).

## What stops it working in another country

In order of how much each costs.

1. **Cards.** A city needs on the order of 100 checked moments before a visitor's three days don't repeat and tastes can be told apart. London has 49 after six weeks. At even 45 minutes a card to find, write and check against an official source (a GUESS: time per card isn't recorded), a city is about 75 hours, ten weeks of the whole project's time. **Hand-made moments do not scale to the world at 7.5 hours a week.** The realistic shape is the one the last sprint sketched (m235, m236): places in bulk from a provider, held to the quality standard's fourth test (is it verified?), with hand-made moments as the layer on top in the few cities ODYS knows.
2. **Travel times.** London uses TfL's journey planner and a straight-line guess. Every other city needs a source: a paid routing API, or self-hosted open routing plus each city's public-transport timetable feed. Per city, and it costs money or hours.
3. **London written into the code.** `Europe/London` or "London" appears in 12 of the Brain's modules (9 times each in `api.py` and `dayplan.py`, 8 in `tripdays.py`) and 11 times in the iPhone app. A zone-aware itinerary module exists (`itinerary.py`, m210) and isn't wired in. ~15 h to thread the destination's zone through.
4. **Thresholds fitted to one climate and one city.** "Hot" is 28°C and "cold" is 8°C for everyone; a transfer starts to hurt at 15 minutes. Right for London; wrong for Seville or Los Angeles. They should belong to the destination, with the person's own weight on top (~4 h).
5. **Money.** The cost weight is "per £10". Abroad it needs the local price put on a common footing, and £10 doesn't buy the same afternoon everywhere (~3 h for currency; purchasing power is a research question).
6. **Language.** The Brain writes its sentences in English (`dayplan.py`, `explain.py`, `reasons.py`), and neither app has any translation files. See the quality audit.
7. **The population model.** Priors from Londoners' guesses can't be assumed for visitors from elsewhere. With real ratings, fit `b_population` and σ properly, by where people are based (never nationality); until then say less, not more.

**What is ready:** the destination registry (m207), the catalogue's structure (m235), the kinds-of-places questions worded neutrally (m229), bank and school holidays kept apart by place (m204, m211), currencies never ranked against each other without a rate (m218). The scaffolding is ahead of the content.

## What to do

| When | What | Hours |
|---|---|---|
| With the first real ratings | Check "strong match" against what people rated; fit the rating cutpoints and the three scales | 4 |
| After the round | Re-choose the onboarding places and choices so they split food, active and budget travellers, measured on the project's benchmark (already its own recommendation) | 4 |
| After the round | Start the solver from the greedy plan | 2 |
| At 200 or more rated stops across 30 or more people | The first real hierarchical fit of `b_population` and σ (PyMC, which is why Python is pinned at 3.12) | 10 |
| Before a second city | Thread time zones through; move thresholds to the destination; one routing source; decide bulk places against hand-made | 30+, and Abram's decision on the data source |
| Not now | A rating-level term; collaborative filtering (needs hundreds of raters per city) | — |
