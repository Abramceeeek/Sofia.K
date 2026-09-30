# Why a few cards fill most plans, and a fix that keeps fit

**Decision for Abram (yes or no):** add a **popularity nudge with a £4 cap** to the personal planner, and use it in Test B. It costs about 1.5 h of Claude's time and none of yours. Plans take about twice as long to compute.

The evidence comes from 200 simulated people on Test B's day: Charing Cross, Saturday 12:00–17:00, 4 stops, £40. They answer the short onboarding (6 places, 5 tasks). The plan must end within 30 min of the generic plan, and it includes one place they loved (the app's default). **Fit** is the value of the plan under each person's *true* weights. **Regret** is how far that falls short of the plan made with the true weights.

## First, a correction

My earlier "Garden at 120 in 40% of plans, St Dunstan in 32%" came from a quick run with two flaws:
- it planned with people's *true* tastes;
- it left out the loved-place and end-time rules.

In Test B's real setting, those two cards are **close to what tastes justify**. The cards that are over-picked are the **free, "safe" cards near the start**:

| Card | In plans now | With true tastes |
|---|---|---|
| Royal Festival Hall foyers (12 min from Charing Cross) | **40%** | 20% |
| British Museum (the loved-place rule, by design) | 33% | 24% |
| The Garden at 120 | 28% | 22% |
| Waterloo Bridge at sunset (12 min, near the finish) | **21%** | 9% |
| St Dunstan-in-the-East | 20% | 18% |
| National Portrait Gallery (4 min) | **16%** | 8% |

## Why: the population prior and the cards near Charing Cross, together

Utility is u_ij = x_j · (b + δ_i).

1. **The population prior is flat on taste.**
   - All 15 taste weights have a population mean of 0 (a GUESS: there is no data yet). Only cost (−0.25 per £10), crowds (−0.40), weather and transfers have non-zero means.
   - So before any answers, every free, quiet card ties at the top (utility 0): 7 cards on Test B's day.
2. **The short onboarding leaves the estimates shrunk.**
   - After 6 places and 5 tasks, the estimated spread of a card's utility across people is about half the true spread (sd 0.9 against 1.9).
   - That is correct Bayesian shrinkage, but it means most cards' estimated utilities sit near 0, so **the tie-breakers decide**.
3. **The tie-breakers favour free, "safe", nearby cards.**
   - A card with few or weak taste tags (the Royal Festival Hall foyers: four tags at half strength, sd 0.75 across people, against 2.0 for the Garden at 120) is estimated at about 0, "fine", for almost everyone.
   - Cards near Charing Cross, or near the generic plan's finish on the South Bank, avoid the transfer penalties (−0.3 for 15–30 min, −0.7 beyond).
   - So the Royal Festival Hall, Waterloo Bridge and the National Portrait Gallery win whenever nothing else clearly stands out.
4. **Geography amplifies it but doesn't cause it.** With travel time switched off (every leg 12 min), plans still converge, only on the far "view" cards instead: Greenwich Park 41% and Richmond Park 38%, against 26% for the top card with true tastes.

## What each fix does (200 simulated people, paired)

| Variant | Regret (lower is better) | Change against today | Top card | Two people's plans overlap (Jaccard) | Distinct cards in use (effective number) |
|---|---|---|---|---|---|
| With true tastes (the ideal) | 0 | | 24% | 0.09 | 23.6 |
| **Today** | 2.50 | | 40% | 0.16 | 15.9 |
| Solve twice, keep the better (a control) | 2.50 | +0.00 ± 0.01 | 40% | 0.16 | 16.0 |
| A random draw from the posterior (Thompson sampling) | 3.54 | **+1.05 ± 0.18 (worse)** | 26% | 0.10 | 22.1 |
| Nudge alone (lower utility by 3 × share) | 2.75 | +0.25 ± 0.15 (worse) | 28% | 0.10 | 16.7 |
| **Nudge, kept only if the person's own estimate loses ≤ 0.1 (≈ £4)** | **2.24** | **−0.26 ± 0.07** | 30% | **0.10** | **18.4** |
| Nudge with a £10 cap | 2.27 | −0.23 ± 0.08 | 26% | 0.08 | 20.1 |

**With the £4 cap:**
- The Royal Festival Hall falls from 40% to 18%, Waterloo Bridge stays at 20%, and the National Portrait Gallery falls from 16% to 10%.
- The Garden at 120 (24%) and St Dunstan (18%) stay about where true tastes put them.
- Two people's plans overlap about as much as their true tastes imply (0.10 against 0.09).

**Fit doesn't get worse; in the simulation it gets slightly better.**
- The control shows this isn't just the second solve: solving twice alone changes nothing.
- The likely reason: the usual plan is not exactly the best plan in expectation. Transfer penalties are convex in the weights, cost is on a log scale, and the posterior is a Laplace approximation. The nudge finds near-ties the planner's heuristic misses.
- **Treat it as "no worse", not as a gain, until real ratings exist.**

## The proposal

1. **Once per brief type,** simulate 200 people and record how often each card lands in a plan: its reference share. The table goes in `brain/data/`; it is redone when the cards or the priors change.
2. **When planning for a person,** solve twice:
   - the usual plan;
   - a plan where each card's utility is lowered by 3 × its reference share. A card in 40% of plans loses 1.2, about £48.
3. **Keep the nudged plan only if, by that person's own estimated weights, it's worth at most 0.1 less:** about £4 at the population's cost weight. Otherwise keep the usual plan.

**The nudge is fixed per brief, never learned from the plans already served.** So it doesn't depend on who signs up first, which matters for Test B. "Regenerate plan" and "swap this stop" keep working as they do.

**Not recommended:**
- **Thompson sampling:** about 40% more regret.
- **A nudge without the cap:** it pushes plans too far from people's tastes.

**The real fix needs data, after Test B** (`decisions/after-9-nov.md` #21):
- population taste means estimated from the swipe page, Test A and the ratings;
- a card-level random effect, so a card's popularity is learned rather than implied by its tags.

*Simulation code: Claude's scratchpad (`overlap_diag.py`, `overlap_v2.py`), 30 Sep 2026. The fit measure counts stop utilities and travel penalties under true weights; the lunch slot scores 0. Planner time limit 0.3 s per solve in the simulation. Standard errors are of the paired difference against today.*
