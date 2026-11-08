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

## Hours

Claude ~3 h. Abram: none now. After the round: flip the switch (one line) and check the eight kinds' wording (~0.5 h, as #86 says).
