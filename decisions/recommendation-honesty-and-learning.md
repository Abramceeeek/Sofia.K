# Recommendations: no unsupported claims, learning measured on real people, and the missing dimensions (16 Nov 2026)

Abram's review of the audit, part 3 (12 Nov). Branch `claude/pensive-euler-fftd63` only: nothing is deployed, the frozen friends' round (`main`, build 91) is untouched, no question is added and no new personal data is collected.

**Decisions:**
- **A. The app shows no chance or match word** until real ratings support one (m275, built).
- **B. Learning is measured per real person, by milestone, against a no-answers baseline** (`learning_milestones.py`, built).
  - Building B found a gap in the development branch's evaluation, which is fixed here (m276): plans never kept their predictions, so the m264 read-out would have found no predicted stops.
- **C. The missing dimensions are mostly gaps in the catalogue, not in the model.** Fill the cards first and learn from ratings. Diet and access stay constraints, which are designed here and not built. No new questions.

## A. What the app says about a stop (m275, built)

**Before:** "Costs £12. A strong match for you." D127's words were thresholds on the rating model's chance of "Good" or better (75% and 50%). That chance has never been checked against a real rating: the priors say "Nothing here is estimated from data yet" (`brain-global-readiness.md`). The "Why this stop?" factors also carried "the rating model gives an 81% chance".

**Now:** the line names the factors from the person's own answers that raise this stop. It uses the same honesty rule as the reasons (D115): a lean the person showed (from swipes, choices, ratings or a feeling they picked), an interest they chose, or a this-or-that trade-off. It never states a chance.

| Case | Line (`reasons.factor_line`) |
|---|---|
| A place they loved | "Recommended because you loved it" |
| Leans shown in their answers | "Recommended because of your lean towards views and awe" |
| An interest, plus a lean | "Recommended because of your interest in history & culture and your lean towards awe" |
| A "this or that" trade-off | "Recommended because of your pick of quieter days" |
| Nothing from them applies | "Chosen to fit your route and hours: your answers don't say much about places like this yet" |

- **The uncertainty is stated, not hidden.** The apps' existing footnote stays: "A first guess from your answers so far, not a promise of how you'll feel. It gets sharper as you rate stops." The plan's "so far" line still counts the answers the reasons rest on.
- **Other wording changed:**
  - **Trip length:** "8 places in London rank highest for you by your answers so far". It was "8 strong matches (a 75% or better chance of Good)", "particularly well suited" and "you'd likely enjoy".
  - **Discovery, quality and the group note:** reworded the same way.
  - "Rank highest" is a ranking, not a prediction of feeling.
- **What stays inside the Brain:** the 75% and 50% bands (`dayplan.match_band`). They are used for ranking (trip length), and `evaluation.py` checks them on real ratings (`match_bands`). They come back on screen only if Abram decides so after that check: for example, if "strong" comes true about 75% of the time over 30 or more rated stops.
- **Both apps:** no code change. `match` was already optional text, so the sample data now carries the Brain's own new lines, and the comments are updated.
- **The Test B pair:** the blind pair shows nothing personal, as before.

## B. Does ODYS learn about a real person? (built)

**The gap found (m276):**
- **The problem:**
  - The m260/m264 framework pairs each rating with the prediction "stored with each plan's stops". The stored plan never held it: the app's stop drops `predicted`. A real export would have read "Planned stops with a prediction: 0".
  - It would also have reported "No rated stops yet" when there were ratings.
- **The fix:**
  - The stored plan now keeps each stop's prediction, beside the score terms (`why`) it already held. It is never sent to the app (`api.public`). Tests check both.
  - Ratings whose plan kept no prediction are counted and reported, never dropped.
  - For plans that kept no prediction, the read-out checks the words those plans showed. The frozen round's plans did store D127's words, so that check can cover them.

**The measure** (`brain/scripts/learning_milestones.py`, `evaluation.learning_by_milestone`):
- Each rated stop is judged by the prediction its own plan was made with.
- It is grouped by how much the person had told us when that plan was made:

| Milestone | Reached when the plan was made |
|---|---|
| After onboarding | no ratings yet |
| After the first rating | at least 1 rating |
| After 2 days out | ratings on at least 2 London dates |
| After 5 days out | ratings on at least 5 London dates |
| After 20 ratings | at least 20 ratings (the furthest milestone, even if it comes before 5 days) |

- **Columns for each milestone:**
  - rated stops and people;
  - the share observed Good, and the mean predicted;
  - the Brier score of the personal prediction;
  - the Brier score of a **baseline**: the population's weights alone, for the same card, weather and interests;
  - **gain** = baseline minus personal;
  - AUC.
- "Days out" counts London dates with a rating, so a day without the app isn't counted as learning.

**Reading it (fixed before any data is seen):**
1. **The learning claim needs:** gain above 0 at the later milestones, growing from "after onboarding" to "after 5 days out", with at least 30 rated stops in each row compared.
2. **Below 30, a row is labelled exploratory.** It is read stop by stop, with no conclusion drawn.
3. **Once rows reach 30 or more:** add a person-level bootstrap interval for the gain before anyone says "it learns" (about 1 h; not built, since there is no data to run it on).
4. **Selection bias:** people rate the stops they visited, and they visit the plans they chose. The read-out says so; nothing is imputed.
5. **Simulated people are never a stand-in for this.**
   - `learning_curve.py`'s synthetic results are a ceiling: correlation 0.43 after onboarding, 0.64 after 20 ratings.
   - They are never evidence that ODYS learns.

**What the friends' round can give:**
- Plans on `main` keep no prediction. So the round's ratings can only be checked by the words they showed ("A strong match for you" against observed Good), using `evaluate_export.py`.
- The milestone measure starts with the first build made from this branch.
- **Expected volume:** with about 20 testers and one rated day each, only the first two rows will fill. "After 20 ratings" needs weeks of use. Stage 2 (`first-real-user-readiness-plan.md`) is sized for this.

## C. The missing dimensions: catalogue or learning? (investigation; nothing built)

**What decides whether a dimension can be learnt.** It needs three things:
1. a personal feature in `priors.yaml`;
2. cards that differ on it;
3. a signal that touches it.

The counts below are for the 49 ready London cards and the 16 swipe places, as of 16 Nov.

| Dimension | In the model | Cards (tag ≥ 1) | Swipe places | Signals today | What's missing | Recommendation |
|---|---|---|---|---|---|---|
| Food experiences | `food` | 12 | 4 | swipes; ratings (a food card served as lunch is rateable); "connected" (half weight) | weakest-learned taste: onboarding removes 7% of its prior variance (m242) | m242 stands. **One of the first day's rated stops is a food card**: it learns more than any question. No diet question. |
| Active | `active`; also "full-on / gentle" (D127) | **6** | 5 | swipes; ratings; the activity answer | too few cards to learn from, or to serve once learnt | **Catalogue first:** about 10 active moments (a lido, climbing, cycling, kayaking; karting exists). About 5 h, research-sourced, by the D91 rule. |
| Shopping | **no feature**; category `shopping` (5 cards) | 5 | 0 | visitors' kinds-of-places cards; trip length's "A shopping day" | shopping cards rank on other tags (iconic, local), so no taste for shopping can form | **After the round:** add `shopping` as a personal feature once 15 or more cards carry it. This is a model-version change with a guessed prior (about 3 h with tests). Until then, it's a card category. |
| Entertainment (shows, games, nightlife) | covered in part by `absorption` and `social_pull` | 1 performance card, 1 karting | 0 | ratings | dated, ticketed events are a different kind of record from moments | **After Checkpoint 3** (after-9-Nov). Events need dates, stock and booking. |
| Relaxed | `packed_pace`, `walking_effort`, `long_walk`; the day's `relaxed` switch; "restored" and "peaceful" | n/a (a day setting) | n/a | this-or-that pace tasks; the activity answer | nothing material | **Covered.** The person sets it for each day; the model learns the lean. |
| Budget | `cost_per_10gbp` (log scale, D88); the day budget is a hard limit | price on every card; unknowns get an allowance (m262) | n/a | the cheaper-days choices; the budget band | trust in prices: many are estimates (m269) | **Covered** as taste plus constraint. The work is price facts, not modelling. |
| Accessibility | **a constraint, never a taste** (`quality.practicality`: `needs_step_free`) | step-free known for 17: 9 yes, 8 partial, **32 unknown** | n/a | none asked (by design) | the facts | **Facts first:** check the 32 unknown cards (about 4 h, official access pages). Then a per-day "step-free only" filter, not stored, is a decision for Abram: it is health-adjacent (Area 12), so not built. |
| Diet (halal, vegetarian, allergies) | **a constraint** (`food.py`, behind consent) | n/a | n/a | none (D123: not asked) | consent, a DPIA and a checked data source (product direction) | **Unchanged:** not collected. It must never become a taste weight: halal can reveal religion, and allergies are health data. |

**Why "catalogue first":**
- A weight the model learns can only act through the cards that carry it.
- `learning_curve.py` already shows the catalogue running out before the model has learnt a person: 40 ratings uses most of the 49 cards.
- Adding features to a model fed by 6 cards would add guessed priors and no evidence.
- So the order is: cards, then the signals that already exist (ratings above all), then a new feature only where a category has the cards.

**No new onboarding questions.**
- Each dimension above is learnt from swipes, choices and ratings that already exist.
- The one question with a measured case (food, m242) loses to a rated food stop.

## Hours

| Item | Hours | When |
|---|---|---|
| A (built, tested) | 3 | done |
| B (built, tested), including the m276 fix | 3.5 | done |
| C (this investigation) | 1.5 | done |
| Person-level bootstrap for the gain | 1 | when a milestone row reaches 30 rated stops |
| 10 active cards; 32 cards' access facts; a shopping feature | 5 + 4 + 3 | after the friends' round, if Abram approves |

## Sources and tests

- **Code:**
  - `brain/src/brain/reasons.py` (`factor_line`)
  - `dayplan.py` (`match_band`)
  - `explain.py`, `triplength.py`, `discovery.py`, `quality.py`, `group.py`
  - `api.py` (`public`, the stored prediction)
  - `evaluation.py` (`shown_from_plans`, `learning_by_milestone`)
  - `brain/scripts/learning_milestones.py`, `evaluate_export.py`
- **Tests:**
  - `tests/test_reasons.py`: the factor line, and the stored prediction never sent;
  - `tests/test_evaluation.py`: milestones, the older plans' words, and an end-to-end read-out on the Brain;
  - `test_explain.py`, `test_moments_and_scoring.py`, `test_discovery.py`, `test_group.py`.
- **Counts:** read from `brain/data` on 16 Nov 2026 (49 ready cards, 16 swipe places, `priors.yaml` 0.2).
