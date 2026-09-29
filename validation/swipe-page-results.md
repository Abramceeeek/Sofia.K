# Swipe page results (29 Sep 2026)

**Decision first (m134–m136):**
- The swipe model's cutpoints are now fitted from these answers.
- Each person gets a swiping level of their own.
- In the app, Hyde Park replaces Columbia Road among the 10 places.
- The locked 16 are unchanged (D107).

**Data:** the anonymous swipe page (D70c) export from 27–28 Sep.
- 12 people each answered all 30 candidate places, giving 235 answers where they had been. There are no names and no IP addresses; the only identifier is a random browser code.
- The raw file stays in `validation/raw/swipe-page/`, which is git-ignored. This note holds counts only.
- **Caveat:** 12 people is a small, self-selected sample, probably people close to Abram. Each "been" share has a standard error of about ±14 points.

## What people answered

| Place | Item | In the app? | Been | Loved | Fine | Didn't enjoy |
|---|---|---|---|---|---|---|
| Big Ben and Parliament Square | 1 | **app** | 12 of 12 | 4 | 8 | 0 |
| Buckingham Palace and the Changing of the Guard |  |  | 12 of 12 | 5 | 7 | 0 |
| British Museum | 4 | **app** | 11 of 12 | 6 | 3 | 2 |
| Canary Wharf among the towers |  |  | 11 of 12 | 6 | 5 | 0 |
| Hyde Park | 6 | **app** | 11 of 12 | 7 | 4 | 0 |
| Camden Market | 7 | locked | 10 of 12 | 6 | 3 | 1 |
| London Eye |  |  | 10 of 12 | 3 | 7 | 0 |
| Westfield shopping centre |  |  | 10 of 12 | 7 | 2 | 1 |
| Richmond Park |  |  | 9 of 12 | 6 | 3 | 0 |
| The view from the top of Greenwich Park | 11 | **app** | 9 of 12 | 6 | 3 | 0 |
| Walking from South Kensington tube to the Natural History Museum | 12 | **app** | 9 of 12 | 5 | 3 | 1 |
| Borough Market | 3 | **app** | 8 of 12 | 5 | 3 | 0 |
| Covent Garden |  |  | 8 of 12 | 4 | 4 | 0 |
| Platform 9¾ at King's Cross |  |  | 8 of 12 | 1 | 6 | 1 |
| Primrose Hill at sunset | 13 | **app** | 8 of 12 | 7 | 1 | 0 |
| The South Bank riverside walk |  |  | 8 of 12 | 4 | 4 | 0 |
| Tower of London |  |  | 8 of 12 | 3 | 4 | 1 |
| Brick Lane for food | 14 | **app** | 7 of 12 | 3 | 4 | 0 |
| IFS Cloud Cable Car | 5 | locked | 7 of 12 | 3 | 4 | 0 |
| Sky Garden | 9 | locked | 7 of 12 | 4 | 3 | 0 |
| Uber Boat on the Thames | 2 | **app** | 7 of 12 | 5 | 2 | 0 |
| Hampstead Heath ponds (swimming) | 15 | **app** | 6 of 12 | 4 | 2 | 0 |
| Madame Tussauds |  |  | 6 of 12 | 3 | 3 | 0 |
| St Paul's Cathedral |  |  | 6 of 12 | 4 | 2 | 0 |
| Go-karting |  |  | 5 of 12 | 5 | 0 | 0 |
| Notting Hill and Portobello Road Market |  |  | 5 of 12 | 1 | 3 | 1 |
| Regent's Canal walk from Little Venice | 16 | locked | 5 of 12 | 4 | 1 | 0 |
| Columbia Road Flower Market (Sunday) | 10 | locked | 4 of 12 | 2 | 1 | 1 |
| Kew Gardens |  |  | 4 of 12 | 2 | 2 | 0 |
| Tate Modern Turbine Hall | 8 | locked | 4 of 12 | 4 | 0 | 0 |

## What it changed

1. **The swipe cutpoints were badly off (m134).**
   - The GUESS [−1, 1] implied 33% "didn't enjoy", 45% "fine" and 22% "loved" at the population weights.
   - People answered 4%, 41% and 55%.
   - Refitted by marginal maximum likelihood in the Brain's own model (`python -m brain.swipecal`), the cutpoints are **−5.15 and −0.67** (se 0.72 and 0.60).
   - So "loved" is the usual answer and tells us less; a rare "didn't enjoy" tells us more.
2. **People differ in how positively they swipe (m135).**
   - Two of the 12 loved every place they had been to (17 of 17 and 28 of 28). One called all 15 of theirs "fine".
   - Without a level of their own, that style is read as liking, or not minding, every tag at once. It then tilts plans toward cards with many tags.
   - The fitted sd of the level is **1.51** (se 0.71). The level is 1 on every swipe and 0 on every moment, so it never enters a plan's scores.
   - It is left out of the read-back, because it is how someone answers, not what they like.
3. **Familiarity decided the app's 10 (m136).**
   - Only 4 of 12 had been to Columbia Road, so **Hyde Park (11 of 12) replaces it**, as m123 planned.
   - Rerun with each place's shrunk P(been): `python -m brain.swipeinfo --answers <csv>`.
   - Hampstead Heath ponds (6 of 12) stays: it is the only place strong on "being active" and "absorbing activities".
4. **The model cost of 10 swipes instead of 16, recomputed** with the fitted cutpoints, the swiping level and each place's familiarity (600 simulated people):
   - the true top-4 cards found: 30.0% with 10, 31.1% with 16 (−1.0 point ± 0.7);
   - utility lost versus the true best 4: 0.875 with 10, 0.823 with 16 (+0.05 ± 0.02);
   - so **10 swipes keep about 89% of what 16 give**.
   - Every swipe carries less information than the old cutpoints suggested: the taste weights' posterior sd is 0.70 with 10 swipes (prior 0.75). **Ratings after each stop matter more than ever.**

## Worth knowing (no change made)

- **Some candidates outside the locked 16 are better known than several inside it:**
  - better known: Buckingham Palace (12 of 12), Canary Wharf (11), Westfield (10), the London Eye (10) and Richmond Park (9);
  - less known, inside the 16: the Tate Turbine Hall (4), Columbia Road (4) and Regent's Canal (5).
  - Changing the locked 16 is Abram's decision (D107), and the app already avoids most of the less-known ones.
- **The page is still up.** More answers firm up these numbers.

## The re-run at 20+ people (D111, D112)

1. **Abram** exports the answers CSV from the swipe page's admin view once 20+ people have answered. **The export has to happen before about 25 Oct in any case:** the free database expires about 27 Oct (m115).
2. **Claude**, in about an hour:
   - refits the cutpoints and the swiping level (`python -m brain.swipecal <csv>`), and updates `priors.yaml`;
   - runs `python -m brain.swipeinfo --answers <csv> --candidates all` to choose from all 30 by expected regret, with each place's familiarity, and checks the pick against the paired simulation (m138);
   - re-chooses the 6 upfront places and 5 tasks from that set (`--upfront 6,5`).
3. **Abram** checks the draft tags of any new place (about 10 min).
4. **Claude** adds the new places to `swipe_items.yaml` (items 17+, printed by the command) and deploys. Only the Brain changes, because the app gets its places from the Brain. So there's no new app build and no App Review.
5. **The set is locked by about Sat 24 Oct**, before the stranger round (~27 Oct).
6. **If there are still fewer than 20 people by Fri 23 Oct,** the current set stays and is locked (Claude's default; Abram can overrule).
