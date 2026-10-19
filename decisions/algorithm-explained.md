# How ODYS picks a day: the algorithm, for review

*19 October 2026. Written for other AI models and people to critique. It describes the code as it runs today (`brain/src/brain/`), not plans. Every number marked GUESS is a starting value, not an estimate from data. The model has not yet been fitted to any real tester's data.*

## In one paragraph

ODYS is a recommender plus a route optimiser, with **no language model making decisions**. Each place card (a "moment") is described by about 20 numeric features. Each person has their own weights on those features, starting at a population average and moving with every answer they give. The weights are estimated by a Bayesian random-utility model, a logit and ordered-logit model with shrinkage to the population. A day is then built by an orienteering solver (OR-Tools). It picks and orders the stops that maximise the person's predicted enjoyment, minus their own dislike of long transfers, inside opening hours, the day's start and end, a budget, a lunch slot and a few rules. After each stop the person rates it 1 to 5, and that rating updates their weights.

The founder's position is to keep this an algorithm, transparent and explainable, rather than letting an AI decide what people should do. Question 12 asks reviewers where, if anywhere, a language model should sit.

---

## 1. What is being recommended: moments

- **49 ready London cards** (51 written; 6 are "area vibes" such as a Soho wander, and 2 are meal-only). A card is a specific experience: the place, how you arrive, how long it takes, opening hours, the best time of day, cost per person, and a "shot card" (where to stand for the photo).
- **Features on each card, each tagged 0, 1 or 2**, entering the model as tag ÷ 2:
    - **Place tags (11):** movement and views, food, green and nature, history and culture, iconic, local and new-to-you, crowds, walking effort, active, outdoor exposure, photo potential.
    - **Moment tags (4):** contrast/reveal (dark-to-open transitions), absorption (activities that demand attention), awe, social pull ("I'd bring people here").
- **Also on each card:** cost (enters as £/10), duration, time windows, the weekdays it opens, "dry only" (15 cards are dropped when rain is likely), and day/night variants that share a group.
- **Who tags them:** Claude drafts the tags and checks the facts (hours, prices, access) against official sources; Abram approves. The tags are judgement, so they carry measurement error.

## 2. The person model (random utility)

For person *i* and moment *m* under conditions *c* (weather, travel time to get there):

> **S(i, m) = x(m, c) · β_i**, with **β_i = b_pop + δ_i**

- **x(m, c)** is the feature vector: the 15 tags; cost; and these conditions:
    - weather: heat × outdoors (28°C or more), cold × outdoors (8°C or less), rain probability × outdoors, heat × walking;
    - transfer hinges: 0 up to 15 minutes, then (t − 15)/15 capped at 1, then (t − 30)/20;
    - an interest match: 1 if the card belongs to a field the person said inspires them (finance and tech, food, history and culture, nature).
- **b_pop** is the population weight vector, in `data/priors.yaml`. Almost all of it is a GUESS:
    - tags start at 0;
    - crowds −0.4;
    - cost −0.25 per £10;
    - rain outdoors −1.0, heat outdoors −0.5, cold outdoors −0.5;
    - transfers 15–30 min −0.3, over 30 min −0.7;
    - interest match +0.25.
- **δ_i** is the person's deviation, with prior δ ~ N(0, diag(σ²)) and σ = 0.75 for most features. 25 features are personal; heat × walking stays at population level.
- **Cost is sign-constrained:** β_cost = −0.25 · e^δ. It can't turn positive, so "worth £V to you" stays finite.
- **A "swiping level" term** (σ = 1.5, fitted on the swipe page) absorbs the fact that some people love every place and others call everything "fine". It never enters a plan's scores.

### Ratings and swipes are ordered outcomes

- **Ratings:** Flat, Fine, Good, Great, Unforgettable (1–5), modelled as an ordered logit on S with cutpoints (−2, −0.75, 0.75, 2). These are a GUESS and symmetric.
- **Swipes:** "Didn't enjoy", "It was fine", "Loved it", an ordered logit with cutpoints (−5.15, −0.67). These were fitted on an anonymous swipe page: 12 people and 235 answers, 27–28 Sep. People answered 4% "didn't enjoy", 41% "fine" and 55% "loved".

## 3. What each answer does

| Answer (screen) | How it enters | Weight of evidence |
|---|---|---|
| **Where you're based** | Visitors from abroad get 8 "kinds of place" cards instead of London places, and form a separate cohort that is left out of the Test B analysis | Routing only |
| **How you want to feel** (up to 2 of 5) | Each feeling is one stated choice: a day with these features preferred over one without. Restored = green 1.0 + awe 0.5. Excited = absorption 1.0 + active 0.5 + reveal 0.5. Connected = social pull 1.0 + food 0.5. Curious = history 1.0 + local 0.5. Peaceful = crowds −1.0 + views 0.5 | Binary logit at scale 0.5 (GUESS: weaker than a concrete choice) |
| **6 London places you've been** (then 4 more, optional) | Ordered logit on the card's features plus the swiping level. "Haven't been" and "Not sure" carry no information | Full |
| **Hard rules from those swipes** | Cards at a place they **didn't enjoy** are never planned. "Familiar" mode puts exactly one loved place into a plan with new ones | Rules, not weights |
| **5 "this or that" days** (more later) | Binary logit on x_A − x_B. Each made-up day varies 6 attributes: longest transfer (15, 30 or 50 min); weather at the outdoor stops (mild, cold or rainy); pace (3 stops relaxed or 5 packed); crowds (quiet or busy at 2 stops); cost (£20, £40 or £60); walking (3 or 8 km). "No preference" is stored but not fitted | Full |
| **Interests** (finance and tech, food, history and culture, nature) | The interest-match feature on cards tagged with those fields (`data/aspiration.yaml`) | Prior mean +0.25 |
| **Budget band** (under £20, £20–40, £40–70, £70+) | A hard budget constraint in the solver | Hard |
| **"So far, I've learned…" corrections** | A line marked "not right" removes the answer behind it from the fit | — |
| **1–5 rating after each stop** | Ordered logit with the conditions at the time: the Met Office weather, and the travel minutes to get there. The weights are refitted after every rating | Full; the most valuable data |
| **Visitors' "kinds of place"** | Like a swipe. "Never tried, would like to" is a stated choice at scale 0.5 | Full or 0.5 |
| **Collected but not used by the planner yet** | Who they go with, morning or night person, activity level, how much photos matter, and the free-text "best hour" (stored; nothing reads it, since no AI is used) | None |

## 4. Estimation

- **The estimate:** the maximum a-posteriori δ_i, found by damped Newton on the log-posterior. The posterior is the Laplace approximation (Gaussian) around it.
- **The three likelihood blocks:**
    - choice logit (the this-or-that days, feelings and "would like to");
    - swipe ordered logit;
    - rating ordered logit.
    - They share δ_i, each with a scale λ, currently all 1.0.
- **Held fixed:** the hyperparameters (b_pop, cutpoints, λ, σ). This is shrinkage to a fixed prior, not yet a fitted hierarchical model. The plan is a pooled hierarchical refit (PyMC) on the testers' data after Test B.
- **The update** takes about 2 ms on the server (measured 19 Oct with 14 answers). It uses numpy only, so it could later move onto the phone.
- **Explanations:** a weight is called a "like" or "dislike" only when P(β < 0) > 0.8 or < 0.2; otherwise "unsure".

## 5. From weights to a day: the planner

1. **The brief:** start point and time, end time, number of stops, date, budget. The Met Office forecast for those hours fills temperature and rain, unless the app sends its own conditions ("it's raining" re-plan).
2. **Candidates:** ready cards that are open that weekday and not swapped out. Also removed:
    - cards at places the person disliked;
    - dry-only cards, if the chance of rain is 50% or more.
3. **The utility of each candidate**, u = x · β_i, under the forecast.
4. **A floor:** a stop is planned only if it's predicted at least "Good" (u > −0.75, the 2|3 cutpoint).
5. **Orienteering with time windows** (OR-Tools routing, guided local search, about 1 s):
    - The prize for each stop is u − floor.
    - Each leg costs the person's own transfer penalty, −(β_15–30 · h1 + β_30+ · h2), plus 1/1000 per minute as a tie-breaker.
    - Constraints: the visit fits inside the card's time window and the day; at most N stops (at least N if possible); the budget; one card per variant group; at most one area vibe; at most one lunch.
    - Buffers: 5 minutes after a walk and 10 after a Tube or bus leg.
    - Travel times come from TfL's journey planner, cached card-to-card and re-checked for the plan's own date. Without TfL, a straight-line estimate.
6. **Lunch:**
    - Any day that spans 11:30–13:30 gets one meal stop, with a bonus of 5 utility units so it's kept.
    - A food card the person is predicted to like (u ≥ 0.5) can be the lunch; otherwise it's a flexible "lunch near X" slot at £15.
    - A day starting by 10:15 never opens with lunch.
7. **Pace:**
    - If the person's packed-pace weight is confidently negative, the stays are lengthened toward the top of each card's range (45–60 min minimum in green places).
    - If it's confidently positive, each stop gets a small extra prize.
8. **Variety nudge:**
    - A second solve lowers each card by 3 × its share of 200 simulated people's plans.
    - It's kept only if, by the person's own weights, it loses at most 0.1 utility (about £4).
    - Without it, everyone with few answers would get the Royal Festival Hall: 38% of simulated plans, down to 28% with the nudge.
9. **Familiar mode** (on in the app, off in Test B): exactly one loved place, plus places they haven't marked as loved.
10. **Rain swaps:** each outdoor stop shows the best indoor alternative within 20 minutes, chosen by the person's own utilities.
11. **Peak–end bonus:** implemented but **off**, because the evidence for multi-part experiences is weak. The ratings will test it.

## 6. What the person sees, and how it's computed

- **"Worth about £V to you":** V = (the non-cost part of S) ÷ (−β_cost / 10). Ranking by V − price is the same as ranking by S. It's hidden in the blind comparison and when there are no answers yet.
- **"Why we picked this for you":** up to two reasons from the person's own answers. Examples: a loved place with the same feature ("You loved Hyde Park, and this has green space too"), a feeling they picked, or an interest. With no answers: "We don't know much about you yet: this one suits most people."
- **The headline** ("A restoring, peaceful day: …") uses their feeling words only when the stops really carry those features.
- **"How the day moves":** a curve whose height is each stop's worth, with a word per stop.

## 7. Trips (several days)

- Each day is planned by the same engine, at the person's own hours and with their number of places per day (lunch extra). No card appears twice in a trip.
- The first day starts where they arrive (airport, station or by car), with one place on the way if they travel light and arrive before check-in. The last day ends back at the stay and on to the airport or station.
- A trip's feelings ("how should this trip feel?") enter as extra stated choices for that trip only.
- Flights (Duffel) and stays (LiteAPI) are searched and filtered in the app and booked on the provider's own site. They are not part of the utility model.

## 8. The test it's built for (Test B)

- Each tester gets two plans for the same Saturday, 12:00–17:00 from Charing Cross: the personal plan and a fixed **generic plan** of popular sights written once by Abram.
- They appear in the same plain-text format, in random order, with no reasons, photos or worth.
- The tester picks one and rates how well each fits. **Pass: at least 7 of 10 prefer the personal plan.**
- The personal plan is held to end within 30 minutes of the generic one, so length doesn't decide the result.
- The Test B pair keeps the travel estimate and gets no forecast, so the test stays as designed.

## 9. A worked example (the real code, 19 Oct)

Two made-up people answer the short onboarding, and a third answers nothing. Same brief: Saturday 24 Oct, 12:00–17:00 from Charing Cross, 4 stops.

**Asha:**

- Feels restored and peaceful; interest: nature; budget £20–40.
- Loved Hyde Park, Greenwich and Primrose Hill; didn't enjoy Brick Lane.
- Always picked the quiet day.
- Biggest moves from the population: crowds −0.40 → **−1.47 (sd 0.61, "dislikes")**; green and nature 0 → **+0.62 ("likes")**; food 0 → −0.49 (unsure).
- **Plan:** lunch near Waterloo → St Dunstan-in-the-East ruined garden (worth £31) → the Garden at 120 rooftop (£58) → General Wolfe's view in Greenwich (£39). £21 in total.
- Headline: "A restoring, peaceful day".

**Ben:**

- Feels excited and connected; interests: food, history and culture; budget £40–70.
- Loved the British Museum, the walk to the Natural History Museum and Brick Lane.
- Always picked the packed day.
- Biggest moves: packed day 0 → **+0.66 ("likes", so pace "packed")**; cold outdoors −0.50 → −0.73; green and nature 0 → −0.42 (unsure).
- **Plan:** lunch in the crypt of St Martin-in-the-Fields (£34) → National Gallery (£32) → National Portrait Gallery (£28) → Sir John Soane's Museum (£32). £12 in total.
- Headline: "A lively, sociable day".

**No answers yet:**

- The population weights only.
- **Plan:** lunch near Charing Cross → Royal Festival Hall foyers → Waterloo Bridge at sunset → Somerset House to the river.
- Every reason reads "We don't know much about you yet".

What it shows: about a dozen answers move a plan a long way, mostly through the tags the person reacted to. It also shows that reasons repeat ("You loved British Museum, and this has history too" three times for Ben), and that with no answers everyone gets nearly the same day.

## 10. What is measured and what is guessed

| Measured or sourced | Guessed (to be refitted) |
|---|---|
| Swipe cutpoints and the swiping-level spread (12 people, swipe page) | Almost all of b_pop, all the prior σ, the rating cutpoints |
| Travel times (TfL), weather (Met Office), opening hours and prices (official sources, per card) | The feature map of the feelings and its 0.5 scale; the interest match +0.25 |
| The variety-nudge effect, in simulation (150 simulated people) | The 28°C and 8°C thresholds, the transfer hinges, the lunch bonus, the buffers |
| | The tags themselves (expert judgement) |

## 11. Known weaknesses (our own critique)

1. **Thin data per person.** About 12 observations against 25 personal weights with σ = 0.75 means most weights stay "unsure". Plans move through the few confident ones.
2. **The population prior is a guess, not a fit.** Until the hierarchical refit, the cold start is the zero vector plus a few signs, which is why plans with no answers converge.
3. **The model is linear in hand-made tags, and the only interactions are weather ones.** There is no fatigue or time-of-day effect, which the original concept called for, and no satiation (two museums in a row count like one museum and one park).
4. **Day-shape preferences are only partly used.** The long-walk weight is estimated from the this-or-that days but never reaches the planner. Pace enters only as a per-stop bonus or longer stays.
5. **Answers we collect but ignore:** who they go with, morning or night person, activity level, and the free-text best hour.
6. **No memory across days** (outside trips): the app doesn't avoid what a person did last week unless they swap it out.
7. **One person's weights only.** A group of friends gets the plan of whoever made it.
8. **A small catalogue** (49 cards, central London) caps how different two people's days can be.
9. **Reasons are template-based** and repetitive (see the example).
10. **Ratings are the only outcome.** There's no "would you go again?" and no measure of how worth it the money felt, though that's one of the app's two goals.

## 12. Questions for the reviewer

1. Is a random-utility model with per-person shrinkage the right core, or would you use something else? For example: collaborative filtering once there is data; a contextual bandit; or pairwise learning-to-rank on the ratings.
2. With about 12 answers before the first plan, which questions buy the most information? Would you change the 6 swipes plus 5 this-or-that days (for example, adaptive question selection by expected information gain)?
3. How would you model **fatigue, sequencing and satiation** within a day without many more parameters?
4. Should **exploration** be deliberate (Thompson sampling from the posterior) so the app learns faster, and how much "worse" a plan is acceptable for that?
5. How should the four unused answers (company, morning or night, activity, photos) enter: as priors, as hard rules, or not at all?
6. What's the right way to plan for **two or more people** (average utility, least misery, or a fairness rule)?
7. Is the 1–5 rating enough as the outcome? How would you measure "the money felt worth it" without annoying people?
8. Are the hand-made tags a bottleneck? How would you check or learn them (for example, from ratings across people)?
9. Is the **variety nudge** (a popularity penalty with a £4 cap) sound, or is there a cleaner diversity method?
10. The peak–end end-bonus is off. Would you test it, and how?
11. What would you **remove** to keep this simple for one founder with about 7.5 hours a week?
12. **Where, if anywhere, should a language model sit?** Abram's position: keep the decisions in a transparent model, because an AI may not do what a person actually wants. The options:
    - (a) none, as now;
    - (b) language only: turn free text (the "best hour" answer, "it's raining, I'm tired") into the same features, and write the explanations from the weights, while the decisions stay in the model;
    - (c) an AI that chooses the places.
    - What do you recommend, and what are the risks of each?

*Source files: `brain/src/brain/features.py`, `personal.py`, `scoring.py`, `planner.py`, `dayplan.py`, `reasons.py`, `categories.py`, `tripdays.py`, `popularity.py`; `brain/data/priors.yaml`, `aspiration.yaml`, `popularity.yaml`. The example run's output is reproducible with the Brain's test client.*
