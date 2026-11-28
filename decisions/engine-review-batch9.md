# Independent review of the batch 9 preference and uncertainty architecture (28 Nov 2026, at 417594a)

**An AI review, not user evidence.** Read-only. The three test files pass (34/34). I reproduced every number below with probes and five hidden-bench runs on 417594a's code (travellers 0–19, 200 in all; the scripts and JSON are in this folder).

**HEAD moved to `2082790` (m367) during the review.** That commit adds the hidden-bench reports and turns a below-floor "poor" based on the population into "low confidence". The reports match my reruns. They're noted below where they change a point.

## Verdict

The m364 rules hold for one place and one instruction. They fail where evidence combines.

1. **The ranking doesn't beat the population-only ranking.**
   - Mean Spearman over 200 travellers: 0.219 against 0.228. The paired difference is −0.009 (se 0.018), and the engine is better for 48% of travellers.
   - The committed reports also show 417594a below the old engine: 0.20 vs 0.22 on travellers 0–3, and 0.23 vs 0.25 on 4–7.
2. **Confidence is mostly a property of the place,** largely its price. On the fresh travellers 4–7 it fails its own check: the gap to the truth is 0.94 at low against 0.97 at medium. m366 says this was checked.
3. **"Newest wins" overrides evidence, not just instructions,** and overridden evidence still drives reasons elsewhere.
4. **78% of the reasons shown still rest on hand-set card tags.**

## Incorrect or fragile assumptions

**The recency rule** (`match.py:246-256`, `api.py:803-817`)
- **Ratings and swipes are observations, but the newest decides.**
  - Ratings of 5, 5 and then 2 give `poor_match` with confidence "high".
  - A rating of 3 cancels an older love or dislike and gives "high". The British Museum then became `strong_match` on δ alone.
- **Overridden items still count.** `dim_evidence` (`:350`) and the similarity loop (`:498-506`) read every instruction.
  - Loved Tate Modern, later rated it 1: the British Museum shows "You loved Tate Modern, which is about art…". It's displayed under low confidence with a conflict (`:697`).
  - A dislike that a must-go overrides still costs the Courtauld −0.30.
- **A newer item about one place lifts a category exclusion for it, even a dislike.**
  - "No museums", then "didn't enjoy" the British Museum, gives `poor_match`, not `not_suitable`.
  - A later "loved" gives `strong_match`.
- **Ties.** Every request is stamped `now_`. A must-go and an avoid for the same place resolve by list order. The restriction then says "you asked not to visit m_sky_garden": the label is the raw card id (`api.py:816`).
- **Nothing is scoped or expires.** `avoid`, `avoid_kinds` and `must_go` are query parameters, never stored.
  - "Respected until changed" lasts one request: the next call is `low_confidence`.
  - Swipes never age.
- **Context comes from when the rating was given:** `created_at`, weekday or weekend in UTC (`api.py:812`). A Monday rating of a Sunday visit counts as "weekday". The rating's own rain, temperature, plan date and company are ignored.

**The dislike levels** (`:388-399`, `:496-517`)
- **"No category ban from one dislike" holds in the engine** (`:317`). The planner still bans the whole kind.
- **Similarity jumps with data coverage.** It's a Jaccard of the pooled primary appeals where both places have records, else 0.5 for the same kind. One British Museum dislike costs:
  - Tate Modern −0.40;
  - Liberty, a shop, −0.20;
  - the Science Museum −0.30;
  - the Natural History Museum 0.
- **Dislikes skip the share rule** that loves get (`:363`).
- **`DISLIKE_PLACE` 1.5 comes on top of the same swipe's update of δ,** so that swipe counts twice. That's defensible only as a place-level random effect.

**Missing turned negative**
- **An unknown time of day is read as the busy window.** `_window_applies` (`:426`) treats "saturday_afternoon" as any Saturday, even with `window=saturday_morning`, so Borough Market becomes `poor_match`. `test_match.py:132` enshrines this.
- **At 417594a, 3,999 of 5,462 held-out poor labels rested on "mostly the population",** and 26% of those were truly in the traveller's top quarter (chance is 25%).
  - m367 makes them low confidence. Low confidence is then 54% of the judgements on travellers 4–7, with no difference in gap (0.967 low against 0.965 medium; my rerun).
  - It has swung from too rarely to too often.

**The uncertainty axis** (`:402-412`)
- **The log-scale cost Jacobian is missing.** β = −0.25·e^δ, so the cost entry of x needs a factor of 0.25·e^δ. With only cost learned, an £18.50 place reads 0.78 where it should read 0.98.
  - corr(place cost, mean ratio) is 0.69.
  - The ratio is above 0.93 for 44% of paid places and 5% of free ones.
- **The ratio identifies the place, not the traveller.** 80% of its variance is between places and 7.5% between travellers. Within a place, its correlation with the error is about 0 (from −0.03 to +0.005).
- **No bin earns its threshold.** Below 0.85 is no better than 0.85–0.93. "High" fired 0–3 times in 2,600 judgements.
- **It leaves out the uncertainty in `b_population`, the cutpoints and ε.**
- **A hidden pseudo-probability remains.** `STRONG = 0.35` is −0.75 + ln 3, the old "75% line", relabelled only.

**Evidence and explanations**
- **Most reasons rest on inferred evidence.** Of 2,091 shown reasons, 1,633 come from card tags or `aspiration.yaml`, and 115 from a record's appeal.
  - 185 call an art gallery history, e.g. "You go out to feel curious, and history is what this place is about" (the National Gallery).
  - `_card_reason` (`:713-745`) still says "that's what this place is about".
- **The traveller's side of a strong reason can be inferred too.** "Your answers" leans are learned from the swipe items' hand-set tags: swipe 12 has `history_culture: 2`.
- **Over-claim:** the British Museum card is "busy" from one claim about the Rosetta Stone, in one of its three rooms. So a crowd-averse traveller gets `poor_match` on every day.
- **A record never changes the score.** Tate Modern still gets +0.95 for a history lover from the card and the aspiration map.
- **A verified annual closure lapses.**
  - The Natural History Museum's 24–26 Dec closure expires 90 days after it was checked, and `Knowledge.today` is the trip's date (`api.py:851`). So 25 Dec 2027 isn't restricted.
  - The warning then reads "(verified, not verified…)" (`:532`).

**Experiences**
- **Swipes map to cards, not experiences.** Swipe 12, the walk from South Kensington tube, maps to `m_nhm_whale_hall`. Loving only that walk:
  - makes the Mammals hall a `strong_match`;
  - gives the British Museum "You loved Natural History Museum, which is about science…, and Room 1 has science too". Science is a secondary 1 there.

## Missing cases

- Trip scope and expiry, stored requests, mixed ratings, company and time of day as context, returning travellers, groups.
- An unknown price counts as £0 (`:321`).
- Tests:
  - None of the probes above is tested.
  - `test_preferences.py:34` uses a hand-set δ with a diagonal Σ, so the real covariance is never exercised.

## The benchmark

- **Its code is independent of the engine, but not its data or judgement:**
  - The catalogue's `type` drives `KIND`. It's also the engine's similarity fallback and the planner's kind rule.
  - `WORDS` mirrors the records written the same day: liberty/timber → architecture, nhm/science → science, great court/whale → busy, tate/gallery → art.
  - `observe()` maps tastes to interests the same way `FIELD_DIMS` does.
- **The thresholds were tuned on the bench's own error measure.** Travellers 4–7 are a resample of the same generator, not a validation, and the check fails there.
- **74% of the travellers answer "N" to every "this or that"** (`choose`). The conjoint is the strongest real signal, and here it's mostly missing.
- **The m364 rules are never exercised:** no must-gos, avoids, ratings, weekends, rain or time windows.
- **It can show** regressions between engine versions in one synthetic world. **It can't show** accuracy, calibration or the thresholds.
- **Against the population ranking,** personalisation helps food (+0.31) and history (+0.14), and hurts budget (−0.25) and shoppers (−0.10).

## Batch 8 points: fixed or not

| Point | Status |
|---|---|
| A kind ban as "not suitable" | **Fixed in the engine**; the planner is unchanged |
| A "verified" basis for the kind rule | **Fixed** |
| A sign test before "your answers" | **Fixed** (`lean`) |
| Low confidence rarely fires | **Changed, not fixed:** 26% of judgements, then 54% after m367, and uninformative |
| A strong match below the cut-off; the art lover at Tate Modern | **Fixed** (`misfit`, records) |
| Cut-offs mean little | **Not fixed** (`STRONG`) |
| Any tag of 2 "defines" a place | **Fixed for the 7 records only.** The galleries are still history on their cards and in `aspiration.yaml` |
| New travellers | **Partly fixed** |
| Time of day; weather | **Not fixed:** time windows are wrong; rain is a parameter, never benched |
| Returning users, groups, an unknown price | **Not fixed** |
| Bench: hidden noisy tastes; results kept | **Done** (the results were committed only in m367) |
| Bench: leave-one-out, flip one swipe, rain and evening, groups | **Not done** |
| A request beats an older dislike | **Done** |

## Top 5 recommendations (hours are GUESSES)

1. **Split instructions from evidence (~4 h GUESS).**
   - Recency applies only to requests, which get a scope and an expiry and are stored.
   - Swipes and ratings are aggregated.
   - Overridden items leave `dim_evidence` and the similarity loop.
   - Simultaneous conflicts are refused.
2. **Rebuild the confidence axis (~4 h GUESS).**
   - Apply the Jacobian.
   - Test within each place.
   - Validate on a second generator, written independently.
   - Show one "we don't know yet" flag, not three levels.
3. **Stop card tags from claiming what a place is about (~5 h GUESS, plus about 1 h of Abram's).**
   - Soften or drop card-only reasons.
   - Re-tag the galleries as art.
   - Let a record override the card's score, or flag where they disagree.
4. **Make the bench test what it claims (~6 h GUESS).**
   - Travellers answer A or B.
   - Add instruction streams with times, weekend, rain and evening days.
   - Report against the population with a paired confidence interval.
5. **Fix experience-level matching (~4 h GUESS).**
   - Map swipes to experiences.
   - Keep a crowd claim about one spot inside it, and treat a time window as unknown when the visit's time is.
   - Weight similarity by share.
   - Never let an annual closure lapse silently.

---

## What Claude checked and did (separate from the review)

**Confirmed and fixed (m368), each with a test in `brain/tests/test_preferences.py` or `test_match.py`:**

| The review's point | What changed |
|---|---|
| "Newest wins" overrode evidence (ratings 5, 5, then 2 gave a poor match) | **Requests and evidence are now separate.** The newest-wins rule applies to requests only: a must-go, "not this place", "no museums". A request beats recorded evidence. Swipes and ratings about one place are combined: their ratings, averaged, take precedence over their swipe. |
| Overridden items still drove other places' reasons | Other places learn only from each place's combined evidence (`evidence_by_place`) |
| A later swipe lifted "no museums" | A request beats any recorded evidence, however recent |
| A must-go and an avoid for one place in the same request were settled by list order, and the message showed the card id | "Not this place" wins, and the message names the place |
| A Saturday-afternoon window was applied to all of Saturday; a spot (the Rosetta Stone) to the whole museum | A time of day applies only when the visit's own time matches. A spot is a caution, never the place's crowding |
| The cost weight's log-scale Jacobian was missing from the predictive spread | Added: the gradient is x·b·e^δ on log-scale features |
| An annual closure lapsed silently after 90 days, and the warning read "(verified, not verified…)" | An out-of-date verified closure warns, naming the date. It is still never applied as a rule until re-checked (`evidence-rules.md` §4) |
| Card-only reasons said "that's what this place is about"; 185 called a gallery history | Card-only reasons are now worded as "ODYS's first reading of this place", not checked. A gallery's history_culture tag is never said as history |
| (Found by the engine bench, m367) A score below the floor from most people's weights was called poor | It's low confidence unless the traveller's own answers drive the negative |

**Confirmed, not fixed now (the next stage, §5 of `validation/engine-bench/evaluation-batch9.md`):**

1. **Personalisation doesn't beat the population on the hidden bench** (0.219 against 0.228 over 200 travellers). This is the most important finding. The engine is honest about what it doesn't know, but it doesn't yet rank better than most people's weights. No real ratings exist to say whether that holds for people.
2. **Confidence still doesn't separate good judgements from bad on fresh travellers.** The m366 log entry claimed this was checked. The check was run, and it failed on travellers 4–7. The batch 9 evaluation now says so.
3. **Swipes map to cards, not experiences.** Swipe 12, the walk from South Kensington tube, lands on the Mammals hall card. The fix needs a swipe-to-experience map (data), checked by Abram.
4. **`DISLIKE_PLACE` counts the same swipe twice**, on top of its update of δ. Defensible only as a place-level effect; to be refitted from real ratings.
5. **`STRONG = 0.35` is the old 75% line relabelled.** Still a GUESS cut-off, never shown as a chance.
6. **Requests aren't stored or scoped to a trip.** They live in the query.
7. **The bench's travellers mostly answer "no preference" to "this or that"**, and the bench never exercises requests, ratings, weekends, rain or evenings.

**Not agreed:** a dislike that a must-go overrides still lowers similar places. Asking to visit a place for this trip isn't a change of taste: the batch 8 review's own rule, "the request doesn't update the person's weights".
