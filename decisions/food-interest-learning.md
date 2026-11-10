# Learning whether someone enjoys food experiences, without asking about diet (10 Nov 2026; m242)

**Recommendation: no new question.** After the friends' round, make **one of the first day's rated stops a food moment**, the best-fitting food card. It learns food interest better than any extra question, and asks nothing.
- If Abram wants one more onboarding question as well, the **ninth kind, "A meal worth travelling for"**, beats a direct food question.
- Every option is about **enjoying food experiences**: markets, food streets, a meal a place is known for. None asks what someone eats or avoids, so nothing touches religion, health or the DPIA (m232). Diet stays with `food.py`, behind consent.

`brain/scripts/compare_food_interest.py`, `brain/benchmarks/synthetic/food_interest.txt`.

## Why food is weakly learned today

The onboarding benchmark (m220, m229) found food the least learned of the tastes: the proposed eight kinds and the five this-or-that days remove **7%** of the food weight's prior variance. Only one kind is high on food ("Local food and food markets"), and no this-or-that day contrasts food.

## The options compared (synthetic people only, 1,000, the model's own prior)

Every arm has the proposed eight kinds and the five upfront this-or-that days.

| Option | Questions before the first plan | Food variance removed | Food weight, fitted vs true | All 49 cards ranked (ρ) | The 6 food cards' fit vs true |
|---|---|---|---|---|---|
| Today's base | 13 | 0.069 | 0.253 | 0.437 | 0.480 |
| **+ a question:** "How much is food part of why you go somewhere?" (a big part / some / not much) | 14 | 0.088 | 0.280 | 0.452 | 0.491 |
| **+ a ninth kind:** "A meal worth travelling for" | 14 | 0.113 | 0.325 | 0.455 | 0.519 |
| **+ a food day:** a sixth this-or-that, a market-lunch day against two more sights | 14 | 0.148 | 0.299 | 0.439 | 0.520 |
| Base, then the first 4 rated stops (as today) | 13 | 0.075 | 0.261 | 0.498 | 0.620 |
| **Base, then 4 rated stops with one a food card** | 13 | **0.162** | **0.340** | **0.515** | **0.680** |

**What it says:**
- **A rated food stop does most:** with no extra question it learns more than any added question on every food measure. That's the CLAUDE.md principle: ratings are the most valuable data.
- **Of the questions, a direct one does least** (food variance 7% → 9%). A stated leaning is weak evidence (the feelings' half weight).
- **The ninth kind** gives the best food correlation of the questions.
- **The food day** removes the most variance, but it mixes in history and views, so its food signal is less clean.

**Assumptions (all GUESSES):**
- "some" answered by 30% (it says nothing);
- the ninth kind's tags and the food day's feature differences;
- people answer as the model assumes.

**What it can't say:** whether people find a food question welcome, or how real ratings of food stops behave. That's for real people after the round.

## How the recommendation would work (after the round; not built)

On a person's first planned day, when a food card fits the day (open, in the budget, near the route), the lunch stop uses that card ("m_x#lunch", which the planner already supports), so the person can rate it. A day with no fitting food card keeps the usual lunch estimate; nothing is forced. **GUESS: Claude ~2 h** with the planner benchmark, so plan quality doesn't drop.

**Hours this step:** Claude ~1.5 h.
