# Kinds of places for everyone: ready for after the friends' round (8 Nov 2026; m220)

**Decision: prepared, switched off.**
- **What's in place:** one line in `brain/data/onboarding.yaml` (`places_mode: named` → `kinds`) gives everyone the eight kinds-of-places cards instead of the named London places, still with "Never tried: would you like to?".
- **What stays the same:** visitors from abroad keep getting them, and a Londoner who answers kinds stays a resident, in the Test B cohort, never a visitor.
- **The frozen friends' round is unchanged:** the switch is off, and TestFlight 91 and Android 21 don't read it.
- **The synthetic comparison below** says what the model can learn from each set of questions. It is **not** evidence about how people find them; that comes from the friends' round and real ratings.

## What existed (D116, investigated)

- `brain/data/categories.yaml`: eight kinds of places with tags like a swipe place. Each shows a ready London card's photo as "In London, for example". Love it / Fine / Not for me enter the fit like a place swipe. Never tried + yes/no is a stated choice at half a this-or-that's weight.
- `GET /v1/onboarding` already serves the cards to everyone. The apps showed them only when `based == "abroad"`.
- In both apps, `isVisitor` did two jobs: which places step to show, and the visitor cohort (no Test B pair, a visitor's first day, no later London places).
- Figma: "Editable screens" still shows the named version ("British Museum: Have you been?"); "Real screens" has "Kinds of places (visitors)".

## What changed (branch only)

| Where | Change |
|---|---|
| Brain | `onboarding.yaml` `places_mode: named`, served as `places_mode` ("named" or "kinds"; anything else reads as "named"). |
| iPhone and Android | `usesKinds = isVisitor \|\| placesMode == "kinds"` decides the places step, its title and back label, and whether the later London places are offered. Everything about the cohort (the Test B pair, the visitor's first day) still follows `isVisitor`. |
| Tests | `brain/tests/test_onboarding_mode.py`: the switch is off now and only two values count. With it on, a Londoner's category answers are fitted (`basis.kinds`), they stay "resident" in the export, and the Test B pair is still theirs. Android screenshot `06c-categories-everyone`: a Londoner with the switch on gets the kinds-of-places step. |

To switch on after the round: set `places_mode: kinds`, deploy the Brain, and use a build from this branch. Then revisit the cohort split: visitors were kept apart because they answered different questions. Once everyone answers the same ones, the only remaining reason is the Test B analysis, which will be finished.

## The synthetic comparison (`brain/scripts/compare_onboarding.py`; `brain/benchmarks/synthetic/onboarding.txt`)

**The setup:**
- 1,000 people drawn from the model's prior;
- every arm also has the 5 upfront this-or-that days;
- answers follow the model's own swipe, rating and stated-choice models;
- GUESSES: a Londoner has been to each named place with P 0.75, a visitor 0.15; a kind is tried with P 0.9; "not sure" 0.3.

| Arm | Usable place answers | Cards ranked (Spearman ρ, true vs fitted, 49 cards) | True top 8 found |
|---|---|---|---|
| Named places, a Londoner | 4.5 | 0.40 | 2.6 |
| Named places, a visitor | 0.9 | 0.31 | 2.3 |
| Kinds of places | 7.7 | 0.43 | 2.8 |
| Kinds, then 4 rated stops (the second stage) | 7.8 + 4 ratings | 0.50 | 3.3 |

**What the model learns** (share of each dimension's prior variance the answers remove):

- **Kinds learn more than named places on most tastes:** absorption (+0.10), history (+0.07), photo spots, active, bringing people, views, outdoors and reveals (+0.03 to +0.05). Named places learn slightly more only on awe (+0.03). For a visitor, named places learn almost nothing (0.9 usable answers).
- **The first ratings help most.** Four rated stops raise ranking from 0.43 to 0.50, and lift views, green space, iconic, local, photo, reveal and awe to 0.14–0.22.
- **Learned by no onboarding version** (under 10% each), whatever the places step: food, green space, iconic, local and new, walking effort, active, reveal, awe, bringing people and cost. Even after 4 rated stops, food, walking effort, active and cost stay under 10%.
  - Cost and walking come mainly from the this-or-that days.
  - Food is high on only one of the eight kinds (street-food markets), so one answer carries it.
- **Not asked at all:** heat (removed from the this-or-that days, D95) and interests (`aspiration_match`, not simulated here).
- **The this-or-that days do the most:** crowds, rain, transfers, pace and long walks (0.25–0.35 each), the same in every arm.

**What this does and doesn't say.**
- It supports Abram's decision in the model's own terms: kinds lose nothing against named places for Londoners and are far better for visitors. The second stage, feedback on specific experiences, is where most of the taste learning happens.
- It says nothing about whether people find the kinds easier, faster or more honest to answer. That's the friends' round's and later testers' to show.
- The tags on the kinds are Claude's judgements (GUESS, D116).
- No user-research conclusion is drawn from this.

**What it suggests for the after-the-round design** (for Abram to decide; not built):
1. A kind that separates food tastes, or a food question that isn't about dietary needs (the food work is research-only, m215).
2. One this-or-that day that varies "active" against "relaxed".
3. Ask for the first ratings early: the second stage is worth more than any onboarding question.

## The globally neutral proposal (m229, 9 Nov 2026; Abram's decision 3, m224)

**Recommendation: keep eight kinds, with the wording below.** Don't add shopping or live entertainment as kinds yet. The first needs a shopping taste in the model; the second needs cards. **Not switched:** `brain/data/categories_global.yaml` is a proposal that nothing serves (tested). The Brain still serves `categories.yaml` with "in London", and `places_mode` stays `named` for the round.

### The wording

| Key | Now (`categories.yaml`) | Proposed (`categories_global.yaml`) | Why |
|---|---|---|---|
| (never tried) | "Would you like to try it in London?" | "Would you like to try this kind of experience?" | Abram's wording |
| (note) | "Wherever you're from. There are no wrong answers." | "Wherever you're from, wherever you're going. There are no wrong answers." | The trip may not be to London |
| (photo caption, in the apps) | "In London, for example: …" | "For example, in {city}: …" | Every ready card is in London, so the caption still says London. It now comes from the card, never claims a photo is anywhere else, and changes by itself once other cities have cards |
| `parks` | "Parks and gardens": "Grass, trees and water in the middle of the city." | "Parks, gardens and green places": "Grass, trees and water, in town or just outside it." | Nature and outdoors (below) |
| `views_above` | "…with the whole city below." | "…with everything laid out below." | Not every view is of a city |
| `river` | "Boats and the river": "Seeing the city from the water." | **"Water experiences and boat trips"**: "Rivers, lakes and the sea: seeing a place from the water." | Abram's wording; not every place has a river |
| `street_food` | "Street-food markets": "Busy stalls, food from everywhere, eating as you go." | **"Local food and food markets"**: "Markets, stalls and the dishes a place is known for." | Abram's wording |
| `hands_on` | "Something hands-on": "Swimming outdoors, cycling through a park, doing rather than looking." | **"Hands-on activities and adventures"**: "Swimming, cycling, climbing or a kayak: doing rather than looking." | Abram's wording; examples that travel |
| `big_museums`, `art_galleries`, `old_buildings` | unchanged | unchanged | Already neutral |

**Tags.** Where a kind's meaning broadened, its tags moved (GUESS, like every tag; each change is commented in the file):
- **water:** history 1 → 0, iconic 1 → 0, outdoors 1 → 2, green 0 → 1;
- **local food:** local 1 → 2, crowds 2 → 1, walking 1 → 0.

The keys stay the same, so an answer stored under `river` keeps its place.

### What was investigated

- **Global relevance.** Five kinds were already neutral. "In London", "the city" and "a river" were the London- or city-specific parts. They're gone, except the photo caption, which says where the photo is from.
- **Shopping.** There are five ready shopping cards (`triplength.SHOPPING`), but **the model has no shopping taste**: those cards have no shopping tag. So a shopping kind (tagged as the five cards' mean) would read "I love shopping" as liking photo spots, famous sights, local places and crowds, not shopping. In the benchmark it doesn't help rank the shopping cards (0.57 with or without it). **To ask about it properly:** a `shopping` tag on the cards and its own personal weight. That's a model change, for after the round (on `after-9-nov.md`).
- **Live entertainment.** **No ready card is a show, a gig or a match.** Evensong at St Paul's is the nearest. The planner couldn't use the answer, and D123 says not to ask what no plan uses. **Cards first, then the question.** The candidate is in the file with no example photo, said rather than faked.
- **Food.** "Local food and food markets" is still the only kind high on food, so food stays weakly learned (7–8% of its prior variance, as before). A kind that separates food tastes (a sit-down meal against grazing) is the way to learn more. It isn't a dietary question, so it doesn't touch the food work (m223).
- **Nature and outdoors.** "Parks and gardens" was a city's park. Broadened to green places in or just outside town. Mountains, coast and countryside aren't in any ready card, so they aren't promised.
- **London-only kinds.** None of the eight is only London's. Their examples are, because every ready card is.

### The benchmark (`scripts/compare_onboarding.py --n 1000`; `benchmarks/synthetic/onboarding.txt`, and `onboarding_tried60.txt` for P(tried) 0.6)

The same synthetic set-up as above (the model's own prior; every arm has the 5 this-or-that days). **Only the tags enter the simulation, so it can't show anything about the wording itself.** Rank ρ is over the 49 ready cards, ± one standard error.

| Arm | Asked | Answers | Rank ρ | True top 8 found | Shopping cards ρ | At P(tried) 0.6: rank ρ |
|---|---|---|---|---|---|---|
| Named places, a Londoner | 6 | 4.5 | 0.399 ± 0.009 | 2.64 | 0.56 | 0.399 |
| Kinds, current eight | 8 | 7.7 | 0.433 ± 0.009 | 2.79 | 0.54 | 0.420 |
| **Kinds, proposed eight** | 8 | 7.8 | **0.442 ± 0.009** | 2.86 | 0.57 | 0.425 |
| Proposed eight, then 4 rated stops | 8 + 4 | 7.8 | 0.503 ± 0.008 | 3.24 | 0.74 | 0.472 |
| Ten (proposed eight + shopping + live) | 10 | 9.7 | 0.451 ± 0.009 | 2.95 | 0.57 | 0.427 |
| Eight with shopping in (museums and galleries as one) | 8 | 7.8 | 0.426 ± 0.009 | 2.86 | 0.58 | 0.422 |

**What it says:**
- **The proposed eight lose nothing against the current eight** (0.442 against 0.433, within noise). They learn a little more about local places (+0.03) and outdoors (+0.02), from the broadened tags.
- **Ten kinds aren't worth two more questions.** Rank ρ moves 0.009, within noise, and less still at P(tried) 0.6 (0.002). They add a little on photo spots, places to bring people and absorption (+0.03 to +0.04).
- **Swapping shopping in for the second history kind costs history** (−0.03) and gains nothing on the shopping cards.
- **The first rated stops still matter most:** 0.44 to 0.50, and the shopping cards from 0.57 to 0.74.
- **Assumptions (all GUESSES):**
  - every kind is tried with the same P (0.9; 0.6 as the sensitivity);
  - "not sure" with P 0.3;
  - the answers follow the model's own swipe and stated-choice models;
  - the cards are London's 49.
- **What it can't say:** whether people find the new words clearer, whether visitors from abroad try kinds at the same rate, or how a taste the model doesn't have (shopping, live shows) would behave. The friends' round and later testers show that.

### Before switching (after the round; not built)

1. Serve `example_note` and use it in both apps in place of the hard-coded "In London, for example" (`OnboardingViews.swift:254`, `Onboarding.kt:306`). ~0.5 h. Both apps already take the never-tried question from the Brain.
2. Copy the proposed wording into `categories.yaml`, then set `places_mode: kinds`. Abram checks the eight first (~0.5 h).
3. Revisit the visitor cohort split, as above.

## Hours

Claude ~3 h (m220) and ~2 h (m229: the proposal, the investigation, the benchmark and its test). Abram: none now. After the round: check the eight's wording (~0.5 h) and decide on a shopping taste.
