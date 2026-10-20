# What five AI reviewers said about the algorithm, and what the checks found (20 Oct 2026)

The reviews are kept as pasted in `decisions/reviews/2026-10-20-ai-algorithm.md` (R1–R5). They reviewed `decisions/algorithm-explained.md`. Their testable claims were measured on the real model and planner with `brain/scripts/algorithm_checks.py`, using 120 simulated people and the Test B brief. Research the reviewers cite was not fetched in this session, so treat it as UNVERIFIED.

## Decision first

- **All five say keep the core:**
    - a personal utility model that leans on the population until a person's answers say otherwise;
    - the OR-Tools planner;
    - and no AI choosing places.
    - At most, an AI could word things or read free text, with the algorithm still deciding (their option b).

    None says replace the model. What they question is the evidence behind it, and our checks agree, with numbers.
- **Two things fixed now:**
    - **The "at least Good" floor could leave a day nearly empty.** About 1 simulated person in 8 got a day with 0–2 places. This is a real bug for Test B, whose two plans must have the same number of stops.
    - **Reasons repeated across a day.**
- **Checked, and not a bug:** transfer time counted twice; the lunch bonus.
- **Six decisions are yours** (below). The biggest: stop showing a £ figure, and treat Test B as a "keep going" signal rather than proof.
- **Hours:** Claude GUESS ~5 h on the checks and fixes. **Abram: about 20 minutes to read and decide.**

## What the checks found

These numbers come from inside the model's own world. The simulated people's true tastes are drawn from the same guessed priors the model uses. So the checks show what the model *can* learn if its assumptions are right, not whether they are. Only real ratings can show that.

| What the reviewers said (who) | What we measured | Verdict |
|---|---|---|
| Test B's "7 of 10" is a weak test (R1, R2, R4) | By chance alone, 7+ of 10 happens 17.2% of the time. If 70% of people truly prefer the personal plan, the test passes only 65% of the time. A proper test at that rate (5% level, 80% power) needs 37 testers; at a true 80% rate, 18 | **True** |
| "Worth about £V" rests on a guess (R1, R2, R4) | The cost weight's uncertainty barely moves with onboarding: sd 0.80 before, 0.76 after (median). The 95% range of £V spans about 20 times, so "£32" could be anywhere from about £7 to £140. Price differs in 3 of the 5 upfront example-day pairs, but always together with 5 other things | **True, and worse than they assumed** |
| A dozen answers can't pin down 25 weights (R1, R2, R3) | 12 of 25 weights track a person's true weight at all (correlation above 0.3). Best: rain outdoors 0.63, packed days 0.61. Weakest: food 0.08, active 0.18, cost 0.29 | **True** |
| Is personalisation worth it at all? (R2, R4: compare with a no-answers plan) | Judged on each person's true tastes, the personal plan gets a median 29% of the gain the best possible plan would. It beats the no-answers plan for 69% of people. The implied preference over the no-answers plan is about 66%, at a GUESSED noise scale. **So even if the model were exactly right, a 10-person test against a no-answers plan would pass only about half the time** | Model-world only. Test B compares against your hand-written day, which is likely stronger |
| The floor is probably not binding (R4); or it's an arbitrary cliff (R2) | It removes 7 of 49 cards with no answers, and a median of 8 after onboarding. But about 1 person in 8 had only 0–2 cards above it, so their day had 0–2 places. The utility level is partly arbitrary per person (choices only fix differences), so an absolute floor can empty a whole day | **Bug, fixed.** When too few cards clear the floor, the person's own best cards fill the day. Places they said they didn't enjoy never come back. Short plans fell from 14% to 1%, and a new test covers it |
| Plans depend on the guessed spreads, not just the answers (R1's sensitivity test) | Refitting the same answers with every prior sd halved changes at least one stop in 70% of plans (2+ stops in 35%). With them ×1.5: 49% (16%) | **True.** The guessed spreads shape plans; refitting them on real data matters |
| Two museums in a row; no fatigue (all five) | 35% of personal plans put two history-and-culture stops back to back; 5% have three or more | **True but moderate.** Decision 3 |
| Transfer time may be counted twice (R2) | A stop's score is computed without its travel time (`dayplan.py:295`), and each leg is charged once, on the route (`planner.py:156`) | **No bug** |
| The lunch bonus (5) may swamp the stops (R2) | It is how "lunch when the day spans midday" is enforced. It is left out of the plan's value and of £V (`planner.py:227`) | **Works as intended.** It could become a plain rule later |
| Reasons repeat (all five; Ben's British Museum line three times) | Each stop's reasons were chosen on their own | **Fixed.** Later stops try a different place, feeling or line first. Ben's line now appears twice, only where nothing else fits; Asha's four stops each say something different |

## Where all five agree

1. **Keep the core**, and keep decisions out of an AI's hands. If an AI is added, it words things or reads free text, and a check confirms every claim against the card data.
2. **The model is honest but under-evidenced.** It's a population model with a personal nudge until real ratings refit it (PyMC after Test B, as planned).
3. **The day needs some sense of sequence:** too many of one kind in a row, and fatigue.
4. **Use the answers you collect, or stop collecting them** (company, morning or night, activity level).
5. **The £ figure overclaims.**
6. **Test B is formative.** Paired ratings say more than a single choice.
7. **Measure "worth the money"**, the product's second outcome (CLAUDE.md), which nothing measures today.
8. **Not yet:** a bandit or Thompson sampling (4 of 5), collaborative filtering, or an AI choosing places (5 of 5).

## Yours to decide (Abram)

1. **Stop showing "worth about £V"** (R1, R2, R4, plus 4 of the 5 screen reviewers).
    - **Recommendation:** show "One of your strongest matches today" or "A good match" instead. Keep the £ figure inside the model; within one person, the stops' order stays right.
    - This reverses my recommendation of 19 Oct; the measurement above is why.
    - Claude: ~3 h, Brain and both apps.
2. **Test B: what a result means.**
    - **Recommendation:** keep "7 of 10" as the "keep going" signal (CLAUDE.md), but call it formative, not proof.
    - Make the paired "Plan 1 fits me / Plan 2 fits me" difference a co-primary result: it's already collected, so it costs no build. Aim for 20 testers if recruiting allows.
    - At analysis, also report how much each personal plan shares with the no-answers plan (Claude ~1 h). If the overlap is high, the win is the curation, not the answers.
    - **Known bias:** with no photos, testers may favour names they recognise, which helps the generic plan.
3. **Two history stops in a row** (35% of personal plans).
    - **Recommendation:** a simple rule, at most two history-and-culture stops and never back to back. Do it before the first tester, or not until after Test B, so the sample isn't split. Claude: ~2 h.
4. **The answers that change nothing:** company, morning or night, and activity level. They're asked in "Improve future plans", after the first plan.
    - **Recommendation:** use them simply. Morning or night sets the default start time. Activity level caps walking. Company is kept for the research, and the app says so.
    - Claude: ~3 h. Or stop asking until they're used (D123's rule): ~0.5 h.
5. **End-of-day questions:** "Was today worth what you spent?" (less / about right / more) and "Would you do this day again?" (yes / no).
    - **Recommendation:** yes, before the friends' round. It measures the product's second outcome, and it's one tap each, once a day. Claude: ~3 h, Brain and both apps.
6. **Where an AI could sit** (your question). All five say option (b), and none says (c).
    - **Recommendation:** nothing before Test B. After Checkpoint 3, pilot (b) for the wording of reasons only, with a check that every claim is in the card data.
    - It needs a privacy change first: the data page says no AI service reads your answers.

## Not now, and why

- **Three attributes per example day instead of six (R1):**
    - the design is balanced for estimating across people, which is what the PyMC refit uses;
    - the Test A questions lock before strangers (D111).
    - Revisit with the refit. Cost could then get its own pair.
- **Explore with Thompson sampling now (R3):** four of five say not yet. Testers would get a worse day so the model can learn.
- **Delete the peak–end code (R1):** it's off, small and tested. Deleting it saves nothing.
- **After Test B, with real ratings** (after-9-Nov #78):
    - a per-person rating leniency term;
    - refitted rating cutpoints;
    - a per-card quality term;
    - a floor stated as a probability;
    - feelings as context for one day rather than lasting taste;
    - several candidate days re-ranked on a whole-day score (walking, repetition, fatigue);
    - adaptive questions;
    - a tag audit by two or three people (the tags were drafted by Claude, so a check by the same kind of model would share its errors);
    - groups: average with a guardrail for the least happy person.
