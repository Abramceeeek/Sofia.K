# Independent review of the person-to-place engine (batch 8, 26 Nov 2026)

**An AI review, not evidence from users.**
- It was written by a separate reviewer, briefed to find weaknesses, wrong assumptions, missing cases and better designs.
- It read the architecture, the place knowledge model, `brain/src/brain/match.py` and the two bench runs (`15a6f61`, `e26828f`). It changed no file.
- It is kept apart from the implementation decisions (batch 8 work package G). What Claude checked and did with it is at the end, under its own heading.

---

## 1. Verdict
It's mostly a sound foundation. The order is right: first the hard rules, then what the traveller asked for, then how well a place fits them. Running it in shadow mode against a fixed bench is also right.

The biggest risk is false confidence. One swipe becomes a hard ban, and the labels claim more than five swipes can support. Neither problem shows up as a failure, because the bench only checks the engine against its own rules.

## 2. Incorrect or fragile assumptions
- **"Not suitable" mixes hard rules with taste.** `kept_out` bans a whole kind of place after one "didn't enjoy". Real travellers silently lose good places.
  - The photographer disliked the British Museum, so all 15 museums are removed.
  - The quiet traveller disliked Big Ben, so St Dunstan-in-the-East (crowds 0, green 2) is removed.
  - `basis` says "verified" whenever the card has checked hours, even when the kind rule did the excluding.
- **"Your answers" vs "most people".** The test is `abs(float(t.delta[i])) > MIN_WEIGHT`: 0.15, against a prior sd of 0.75.
  - The code comment says the spread test was dropped because "after a few swipes it rarely does". So the rule was loosened because the data didn't meet it.
  - `delta_sd` is never read.
  - A history lover who called Brick Lane "fine" is told "Your answers lean away from good food".
  - `personal.prob_negative` already exists and could do this test properly.
- **"Low confidence" almost never fires.** `direct` is true whenever any reason or "against" line exists. `person_known` credits a whole term to the person once δ passes 0.15. The 13 travellers who answered get 10 low-confidence judgements in total; the one who answered nothing gets 72. Yet the simulated rank correlation after onboarding is only 0.43.
- **Strong match.** The rule is `known_good or (score >= STRONG and reason)`.
  - 15 of 137 strong matches score below the strong cut-off.
  - The art lover's Tate Modern scores −1.01, below the planner's floor. The model can't explain that love (it has no art feature), and the class hides it.
  - Whether a reason sentence can be written changes the class.
- **Cut-offs.** STRONG is −0.75 + logit(0.75) on rating cutpoints that are guesses. It's the old 75% line in disguise. The ordering holds, but the class boundaries mean little.
- **The evidence rule.** "Defining" means a tag of 2, but 50 of the 74 ready cards have three or more tags at 2, and one has eight. So Borough Market is "about" being a famous sight.
  - The fall from 116 weak claims to 0 is true by construction: the bench's regex tests exactly the rule that was built.
  - The family-with-children traveller still gets the NHM walk → Borough Market link. The lean now comes from their "family" and "connected" answers, not from the place they loved.
  - 153 of the 420 reasons come from `aspiration.yaml`, which still files Tate Modern under history.
  - 54 places recommended as good discoveries carry only a line saying why they may not suit.
- **New travellers.** The population's content weights are all 0, so a new traveller is ranked on crowds and cost alone. "This one suits most people" (`reasons.py`) is unsupported.
- **A wrong claim in the architecture doc.** It says `match` reuses `quality.assess`; `match.py` never imports it.

## 3. Missing cases
- **Time of day:** `open_on` judges a whole day only. Evening, sunset and morning-only places, and night owls, are never judged.
- **Weather:** the API never sets `temp_c` and the bench never sets `rain_prob`. The 16 cards that need a dry day are never tested.
- **Travellers:** toddlers, step-free needs, shoppers, nightlife, visitors from abroad, contradictory or all-"loved" swipers. Also returning users who want new places: a past love is treated as a present want.
- **Places:** day and night variants, area wanders, meals, timed entry, cards tagged 2 on many features.
- **Groups:** the group planner ignores kind rules. It planned the Queen's House for the quiet member, whom the engine marks not suitable.
- **Edge cases:** a must-go list of any length; an unknown price scored as £0.

## 4. The benchmark
- **What's good:** hashes, dates and solver settings are fixed, the raw JSON is kept, and the two commits give identical results where they should.
- **What's circular:**
  - "0 not suitable planned" and "0 poor planned" are guaranteed, because the engine reuses the planner's rules and floor.
  - A "feasible" must-go is defined by the engine's own class.
- **No ground truth.** The synthetic travellers answer by noiseless rules and have no hidden true taste, so nothing measures whether the picks are right. A random ranking would beat the 16% top-10 overlap (about 8%).
- **Bugs:**
  - `c.replace("m_", "")` also strips an "m_" inside an id ("museudocklands"), so 2 of the 6 group stops go unjudged.
  - The dislike check skips `before` stops and reuses Friday's list on Saturday.
  - The bench runs once.
- **What I would add:**
  - hidden, noisy tastes for each traveller, including tastes outside the 15 tags;
  - leave-one-answer-out tests, and tests that flip one swipe;
  - a rain day and an evening;
  - group checks;
  - how concentrated plans are (the Garden at 120 is in 9 of 14 plans);
  - three runs.

## 5. The place knowledge model
- **Strengths:**
  - experiences sit under places, which fits the moment idea;
  - every attribute carries its evidence;
  - unknown never means no;
  - inferred facts are barred from hard rules;
  - crowd-sourced labels are kept apart;
  - the old 15 tags are derived from the record, so nothing breaks;
  - a new dimension waits for enough places to carry it.
- **Gaps:**
  - The source types rank factual reliability, but "breathtaking" on an official page is marketing, not evidence of awe. Feelings like awe need a source learned from ratings.
  - There are no rubric anchors for a 1 versus a 2, no second rater and no "primary appeal".
  - The approach and the shot card, which are the heart of a moment, are missing from Experience.
  - Facts don't expire by type.
  - Appeals duplicate the dimensions.
- **At scale:** 12 h for 74 places looks optimistic (GUESS). Thousands of places would need automated extraction, so their facts would be "inferred". Inferred facts are never defining, so the long tail would never get a strong match. Abram should decide that policy.

## 6. Alternative designs
- **Separate axes instead of one class.** Keep four things apart: a hard-rule gate, a flag for what the traveller asked for, fit, and confidence.
  - Fit would be a percentile within the person's own ranking.
  - Confidence would be √(xᵀΣx), from the Laplace covariance the model already computes.
  - Classes become only a display. The cost is more to explain.
- **Thompson sampling** for one discovery slot a day. Seed it (the blind Plan 1 / Plan 2 pair needs repeatable plans) and only sample places above the floor.
- **Kind as a hierarchical effect** in the model, not a ban.
- **Text embeddings** of place descriptions, to find candidates and similar places for art, nightlife and atmosphere. They're cheap, but they can't give a sourced reason.
- **Learning-to-rank** needs thousands of ratings. Refit the hierarchical model, with fitted rating cutpoints, first.

## 7. The open decision
The request should win. By Abram's own rule, a must-go gives way only to opening hours, safety and eligibility. A past dislike is none of those, and it's older, coarser evidence than a specific request. So the engine should change, not the planner:
- "Didn't enjoy" becomes a strong negative: never proposed unasked, but never blocking a request.
- The plan shows one line: "In because you asked; you didn't enjoy it last time."
- The app asks no question, and the request doesn't update the person's weights.

Today two engines give two answers, which is the worst outcome.

## 8. Top 5 recommendations, ranked (hours are GUESSES)
1. Keep "not suitable" for hard rules only: kind bans become score penalties, and requests beat past dislikes (~3 h).
2. Use the posterior: a sign-probability test before saying "your answers", the predictive sd as confidence, and a misfit flag instead of relabelling places they loved (~4 h).
3. Fix the bench: hidden noisy tastes, held-out answers, rain and evening days, group checks, the id bug, three runs (~6 h).
4. Replace "any tag of 2" with one or two anchored primary appeals per card, and remove Tate Modern as history now (~4 h, plus about 1 h of Abram's).
5. Keep the planner off the classes until the friends' round gives a first real rank correlation.

---

## What Claude checked and did (separate from the review)

- **Checked and confirmed:**
  - 50 of the 74 ready cards have three or more tags at 2, and one has eight;
  - the bench's group-stop mapping broke ids with an inner "m_";
  - the dislike check skipped `before` stops;
  - `match.py` doesn't use `quality.assess`, so the architecture doc's claim was wrong.
- **Fixed now, in the bench script only** (the Brain stays at `ecba269`):
  - the id mapping;
  - the dislike check, which now covers each day against its own judgements, `before` stops included;
  - the report now says which results are true by construction.
- **Fixed now, in the architecture doc:** the `quality.assess` claim.
- **Not fixed: the engine's logic** (classes, the "your answers" test, `basis`, kind bans). Changing it is the next stage, measured before and after. The review's top 5 is folded into the next-stage proposal (`validation/engine-bench/evaluation-batch8.md` §5).
