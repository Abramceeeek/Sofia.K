# Five AI reviews of the algorithm (20 Oct 2026)

Abram pasted these on 20 Oct 2026 after sending `decisions/algorithm-explained.md` to five AI models. Kept as pasted, with image and favicon links removed. What was checked against the code, and what follows from it, is in `decisions/algorithm-review-synthesis.md`. Sources the reviewers cite were not fetched in this session: treat their research claims as UNVERIFIED unless the synthesis says otherwise.

## Review 1

The document is unusually honest for an algorithm spec. That honesty is an asset, but it also makes the central problem visible: **ODYs is a well-posed model built on almost entirely unmeasured parameters, tested on a sample size that cannot distinguish a real effect from noise.** The architecture is defensible; the evidentiary base is not yet. Below is a detailed critique organized around the decisions that matter most, followed by direct answers to the twelve questions and the UX implications that follow from them.

---

#### The core verdict: right family, premature commitment

The choice of a **linear random-utility model with per-person shrinkage** is reasonable for a solo founder who needs transparency and a 2 ms update. It is not the “best” model in any absolute sense, but it is the right *starting* model because it imposes structure that can be inspected and corrected. The danger is not the family; the danger is that the model is being treated as if it were already calibrated when almost every number in it is a `GUESS`. The document says this explicitly, which is good, but the planner and the Test B design do not yet reflect that uncertainty.

A recommendation system for a 49-card catalogue is not a data problem. It is a **prior-design problem**. With twelve observations and twenty-five personal weights, most posterior mass will remain near the prior no matter how elegant the Laplace approximation. The variety nudge exists precisely because the cold-start plans collapse to the same handful of cards. That is not a bug in the nudge; it is a symptom of a prior that carries almost no information beyond a few signs.

The most important strategic question is therefore not “random utility vs. collaborative filtering” but: **what is the smallest amount of real preference data that would make the current model actually informative, and how quickly can Test B produce it?** Everything else should be subordinated to that.

---

#### Where the model is sound

**The planner formulation is correct.** Orienteering with time windows is the standard formulation for itinerary selection, and OR-Tools is an appropriate solver at this scale. The use of a utility floor to avoid planning stops the person is predicted to dislike is a sensible UX safeguard, and the lunch bonus and buffers show attention to the practical shape of a day.

**The shrinkage architecture is directionally right.** A hierarchical prior with a Laplace approximation is a legitimate way to handle thin per-person data, and the plan to move to a pooled hierarchical refit in PyMC after Test B is the correct trajectory. Fixed hyperparameters now, estimated hyperparameters later, is the right sequencing for a solo builder.

**The decision to keep a language model out of the decision loop is well supported.** Research on GenAI hallucinations in tourism shows that even plausible errors significantly reduce perceived accuracy, usefulness, and trustworthiness, and that the effect compounds when errors have negative consequences. A system that promises a day out cannot afford a confidently wrong opening time or a closed venue. Keeping the solver in charge of feasibility is not conservatism; it is the minimum condition for the product to be trustworthy.

**Cost sign-constraint is a good touch.** Forcing the cost coefficient to remain negative keeps “worth about £V” from becoming nonsensical. Small detail, correct instinct.

---

#### Where the model is fragile

##### 1. The prior is doing almost all the work, and it is arbitrary

`b_pop` is described as “almost all a GUESS,” and `σ = 0.75` for most features. With twelve answers against twenty-five personal weights, the posterior for most features will be barely distinguishable from the prior. The document acknowledges this in weakness 1 and 2, but the consequence is stronger than stated: **the model is not yet a personalization model; it is a population model with a small, noisy perturbation.** Asha’s crowds weight moving to −1.47 and Ben’s packed-day weight moving to +0.66 are large relative to the prior, which is encouraging, but those are selected examples. The planner’s floor (`u > −0.75`) and the reasons template will be dominated by the population vector for most users for most of the early experience.

The single highest-leverage change is not to the model structure but to **the prior for the cold-start user**. Options, in order of increasing effort:

- **Replace the zero-vector tag prior with a low-dimensional factor prior** estimated from the 49 cards’ tag co-occurrence structure. Tags are not independent: “history” and “culture” and “iconic” cluster, as do “green” and “nature” and “views.” A factor prior that encodes these correlations would give a cold-start user a more coherent set of weights than independent zeros. This can be estimated without any user data, from the tag matrix alone.
- **Use the four “unused” answers as prior shifts, not hard rules.** “Who they go with,” “morning or night person,” and “activity level” are exactly the kind of coarse stated preferences that can move a prior mean without needing to be estimated as free parameters. The document currently collects them and ignores them; that is a missed opportunity at precisely the moment when prior information is most valuable.
- **Do not wait for the PyMC refit to test whether the prior matters.** Run a sensitivity analysis now: plan the same brief under three different `σ` values and report how many of the four stops change. If the plan is insensitive to `σ` over a plausible range, the prior uncertainty is not yet the binding constraint; if it is sensitive, that is a reason to prioritize the hierarchical refit before Test B.

##### 2. The rating cutpoints and the ordered-logit scale are unvalidated

The rating cutpoints `(−2, −0.75, 0.75, 2)` are symmetric and guessed. The swipe cutpoints were fitted on 235 answers from 12 people, which is a very thin basis for a three-level ordered logit. The risk is not that the cutpoints are slightly wrong; it is that **the mapping from utility to the word “Good” may be systematically miscalibrated**, which would make the planner’s floor either too permissive or too strict in a way that is invisible without held-out data.

A cheap validation: in the Test B debrief, ask testers to rate not only the plan they chose but also **a single card they did not visit** (e.g., the lunch alternative or the next-best card). That gives a rating observation on a card whose utility the model can compute, and it can be compared to the cutpoints. Without something like this, the floor remains a guess dressed as a rule.

##### 3. The this-or-that days are doing too much inferential work for too few observations

Five binary choices, each varying six attributes, produce five likelihood contributions per person. The document treats these as “full” weight of evidence. But five pairwise comparisons cannot identify six attribute trade-offs, especially when the person may be using a simple heuristic (“always pick the quieter day”) that is not the same as a linear utility difference. The result is that the this-or-that block may be **fitting noise in the question design** rather than stable preference.

This is a case where adaptive question selection would help, but not in the way the document frames it. The question is not “which question buys the most information?” but “which question is least likely to be answered by a heuristic that violates the additive utility assumption?” A question that varies one attribute at a time, or that presents a dominated pair as a consistency check, may buy less Fisher information but more valid signal.

##### 4. The linear-in-tags model cannot represent the day as a sequence

This is the most consequential structural weakness, and the document knows it (weakness 3 and 4). Research on city-tour sequence effects shows that travelers value a sightseeing experience less if a previous attraction offered the same type of experience, and that active-participation attractions are rated more highly when visited after passive ones. Work on tourist trip design with fatigue explicitly models diminishing marginal utility from additional points of interest and shows that ignoring fatigue leads algorithms to over-predict the number of visits. The current model treats two museums in a row exactly like one museum and one park, which is behaviorally wrong in a way that a linear tag model cannot fix by adding more tags.

The good news is that a full fatigue model is not required to improve on the status quo. A **cheap sequence penalty** is sufficient for a first pass:

- Compute a pairwise similarity between consecutive stops based on tag overlap (e.g., cosine similarity of the tag vectors).
- Subtract a penalty proportional to that similarity from the second stop’s prize, with the penalty magnitude estimated as a single additional parameter (not per-person) from the rating data.
- Do the same for a coarse “energy” dimension (walking effort + active), so that a high-effort stop followed by another high-effort stop is penalized.

This adds one or two global parameters, not twenty-five personal ones, and it directly addresses the fatigue and satiation effects that the literature says are real. It also gives the reasons engine something more interesting to say: “We put the park after the museum because the two feel different.”

##### 5. The variety nudge is ad hoc and its effect is simulated, not measured

The nudge lowers each card by 3× its share of 200 simulated people’s plans, and it is kept only if it costs at most 0.1 utility. This is a reasonable heuristic, but it is not a principled diversity method, and the “3×” and “0.1” are guesses. Research on popularity bias and diversity shows that popularity-debiasing strategies can improve diversity and novelty, but the effect depends on the calibration of the penalty. The simulation result (38% → 28% Royal Festival Hall) is a useful diagnostic, but it is not evidence that the nudge improves real satisfaction.

A cleaner alternative is to make diversity a **constraint on the plan**, not a penalty on the prize: require that the selected stops cover at least k distinct “experience types” (e.g., at least one green/nature stop and at least one history/culture stop for a four-stop day). This is easier to explain, easier to audit, and does not require tuning a penalty that may systematically under-recommend genuinely good popular cards.

##### 6. Test B has very low power

This is the most important practical critique. Test B is a paired comparison: 10 testers, each choosing between a personal plan and a generic plan. The pass criterion is “at least 7 of 10 prefer the personal plan.” Under the null hypothesis that the personal and generic plans are equally preferred, the probability of observing 7 or more personal-plan choices out of 10 is approximately **17%** (binomial, p = 0.5). That is not a stringent test. A result of 7/10 would be encouraging but not statistically distinguishable from chance at conventional levels. A result of 8/10 would be stronger (p ≈ 5.5%), but still fragile.

This does not mean Test B is worthless. It is a **formative** test, not a confirmatory one. But the document should not describe 7/10 as a “pass” without acknowledging that the test is underpowered. If the goal is to decide whether to continue investing, 7/10 is a reasonable threshold for “keep going.” If the goal is to claim that personalization works, 10 testers cannot support that claim. The difference matters for how the result is communicated.

A more informative design, at the same cost, would be to collect **a rating for each plan** (not just a choice) and to analyze the paired difference in ratings. A paired t-test or a sign test on the rating differences uses more of the information than the binary choice alone, and it gives a sense of effect size, not just direction.

---

#### Direct answers to the twelve questions

**1. Is a random-utility model with per-person shrinkage the right core?**

For now, yes, with a caveat. Collaborative filtering is not viable at this catalogue size and data volume, and pairwise learning-to-rank would require more preference data than the current onboarding produces. A contextual bandit is attractive in principle, but with twelve observations per user the exploration cost would fall on the first users in a way that is hard to justify for a product that promises a good day out. The random-utility core is the right **interim** model because it is transparent and can absorb new data incrementally. The caveat is that it should be treated as a **prior-elicitation device** until the hierarchical refit, not as a finished personalization engine.

**2. Which questions buy the most information before the first plan?**

The current six swipes plus five this-or-that days are a reasonable starting point, but adaptive selection by expected information gain is worth testing. The key insight from the elicitation literature is that the most informative questions are those that **split the posterior most evenly**. For a cold-start user with a zero-vector prior, a question that contrasts two cards with very different tag profiles (e.g., a green/nature card versus a history/culture card) is more informative than a question that contrasts two similar cards. The this-or-that days already do this implicitly, but they could be selected adaptively: after the first two answers, choose the next pair to maximize the expected reduction in posterior entropy over the personal weights. This is a bounded change to the onboarding flow and does not require changing the model.

The four unused answers (company, morning/night, activity, photos) should be used as **prior shifts**, not as questions in the adaptive pool. They are cheap, they are asked once, and they carry coarse but reliable information that can move the prior mean before any likelihood data arrives.

**3. How would you model fatigue, sequencing, and satiation without many more parameters?**

The pairwise similarity penalty described above is the minimal viable change: one global penalty parameter for tag similarity between consecutive stops, and one for energy similarity. This is not a full fatigue model, but it captures the two most robust sequence effects in the literature: **repetition reduces value, and high-effort sequences reduce value**. It adds two parameters, both estimated globally, and it can be implemented as a modification to the prize of the second stop in the solver without changing the model’s likelihood structure.

A second cheap addition is a **time-of-day interaction**: the same card can have different utility at 11:00 and 15:00, especially for outdoor versus indoor stops. The current model has day/night variants, but the utility does not shift with time within the day. A single interaction term (outdoor × afternoon heat, or indoor × late-afternoon fatigue) would be a start.

**4. Should exploration be deliberate?**

Yes, but not with full Thompson sampling yet. The problem with Thompson sampling at this stage is that the posterior is dominated by the prior, and the prior is a guess. Sampling from a guessed posterior will produce exploration that is not actually informative about the person’s true preferences; it will just be noise around the guess. A more appropriate first step is **ε-greedy exploration with a small ε** (e.g., 0.1): with 90% probability, plan the argmax plan; with 10% probability, swap the lowest-utility stop for the highest-utility unselected card that is feasible. This gives the model a chance to learn from a card it would not otherwise plan, without exposing the user to a plan that is likely to be bad.

Research on Thompson sampling in cold-start settings shows that the prior dominates early exploration, and that a uniform prior can systematically over-explore weak items. The current prior is not uniform, but it is also not well calibrated, so the same caution applies.

**5. How should the four unused answers enter?**

As **prior means and variance reductions**, not as hard rules and not as additional personal weights. “Who they go with” can shift the prior toward social-pull features or solitude features. “Morning or night person” can shift the prior toward time-of-day interactions. “Activity level” can shift the prior toward walking effort and active tags. “Photos matter” can shift the prior toward photo-potential. This is the lowest-cost way to use information that is already being collected, and it directly addresses the cold-start convergence problem.

**6. How should the planner handle groups?**

The group recommendation literature is clear that there is no single best aggregation rule; the choice depends on whether the priority is average satisfaction or fairness. The “least misery” rule maximizes fairness at the cost of average utility, while additive utilitarian maximizes average utility at the cost of fairness. For a day out with friends, **least misery is the more defensible default**, because a plan that leaves one person miserable is a failed social experience regardless of how much everyone else enjoys it. A practical compromise is to use least misery as a constraint (no group member’s predicted utility below the “Good” floor) and additive utility as the objective within that constraint. This is a small change to the solver and it avoids the failure mode of “the plan of whoever made it.”

**7. Is the 1–5 rating enough as the outcome?**

No. The document’s own weakness 10 identifies the gap: there is no measure of whether the money felt worth it. The app’s value proposition is not just “did you enjoy it” but “was it worth the cost.” A single additional question at the end of the day—“Was the day worth what you paid?” with three options (less than worth it, about right, more than worth it)—would give a money-worth outcome without annoying people. This is a **stated-preference** measure, not a revealed-preference one, but it is exactly the kind of question that willingness-to-pay research uses in travel contexts. It should be optional and asked once per day, not after every stop.

A second useful outcome is a simple **“Would you do this day again?”** binary. This captures the repeat-intent dimension that the 1–5 rating does not, and it is easy to answer.

**8. Are hand-made tags a bottleneck?**

Yes, but not in the way the document suggests. The bottleneck is not that the tags are hand-made; it is that **the tags are not validated against anything**. Claude drafts them and Abram approves them, but there is no check that the tag vector predicts the ratings, and no mechanism for correcting tags that are systematically wrong. A cheap validation is to regress the ratings on the tag vector (after the hierarchical refit) and inspect the residuals for cards that are consistently over- or under-predicted. Cards with large residuals are candidates for tag revision. This is not learning the tags from scratch; it is using the ratings to **audit** the tags, which is a much lower-variance operation.

**9. Is the variety nudge sound?**

It is a reasonable heuristic, but it is not the cleanest diversity method. A constraint-based approach (cover at least k distinct experience types) is easier to explain and does not require calibrating a penalty. If the nudge is kept, the 3× multiplier and the 0.1 utility cap should be treated as **hyperparameters to be tuned in simulation**, not fixed guesses. The current simulation result is a useful sanity check, but it does not establish that the nudge improves real satisfaction.

**10. Should the peak-end bonus be tested?**

The evidence for multi-part experiences and peak-end effects in day-scale tourism is weaker than the evidence for fatigue and sequence effects. The document is right to leave it off. If it is tested, the test should be a **within-subject comparison** of two plans that differ only in whether the highest-utility stop is placed first or last, with ratings collected for both. This is a clean manipulation and it would give a direct answer. But it is a lower priority than the fatigue and prior issues.

**11. What would you remove to keep this simple for one founder with 7.5 hours a week?**

Remove the peak-end bonus entirely for now (it is already off; delete the code so it does not need to be maintained). Remove the “worth about £V” display from the blind comparison (it is already hidden; make that permanent until the cost model is validated). Remove the this-or-that days’ six-attribute design and replace it with **three attributes at a time** (longest transfer, pace, crowds). This reduces the cognitive load on the tester and makes the pairwise choices more interpretable. Keep the swipes, the feelings, the interests, and the budget band. These are the highest-signal, lowest-effort inputs.

**12. Where should a language model sit?**

**Option (b): language only, decisions stay in the model.** This is the right answer, and the evidence supports it. Template-based explanations can feel impersonal, and LLM-based rephrasing can produce a richer and more engaging user experience, especially when the LLM is grounded in the model’s actual weights rather than generating from scratch. At the same time, hallucinations in itinerary planning are a serious trust risk, and the decisions—which places, in what order, at what time—must remain with the solver.

The concrete architecture: the solver produces the plan and the weights; a **constrained LLM layer** turns the weights and the plan’s features into natural-language reasons, using a template that requires every claim to be traceable to a feature or a weight. The LLM is not allowed to introduce a fact that is not in the card data. This gives the UX benefit of richer language without giving up the auditability of the decision.

Option (c)—an AI that chooses the places—is the one to avoid. It collapses the distinction between feasibility and preference, and it makes the system impossible to debug when a plan is bad. Option (a)—no language model at all—is viable but leaves the repetition problem in weakness 9 unaddressed, and the repetition is a real UX problem: Ben’s reasons repeat the same British Museum sentence three times.

---

#### UX implications: what the model choices mean for the person using the app

The most important UX consequence of the current design is that **the cold-start experience is the product**, because most users will be cold-start users for most of their early sessions. The population weights are doing the heavy lifting, and the plans converge. The variety nudge helps, but it is a patch. The real fix is to make the onboarding answers carry more information and to make the first plan visibly responsive to them.

A second UX consequence is that **the reasons engine is the trust engine**. Template-based reasons that repeat are not just aesthetically weak; they undermine the credibility of the personalization claim. A person who sees “You loved the British Museum, and this has history too” three times will conclude that the system is not really listening. The LLM-rephrasing option is worth testing for this reason alone, provided it is grounded.

A third UX consequence is that **the “worth about £V” display should stay hidden until the cost model is validated**. The current formula is a linear transformation of utility, and the cost coefficient is a guess. Showing a money value that is not calibrated to actual willingness to pay is worse than showing nothing, because it invites a comparison that the model cannot yet support.

Finally, **Test B’s blind comparison is the right instinct**, but the testers should be asked to explain their choice in one sentence. That sentence is worth more than the binary choice, because it reveals whether the personal plan is winning for the right reason (it actually fits them better) or the wrong reason (it is shorter, or the lunch is nicer, or the generic plan includes a place they have already been to). The 30-minute length-matching control helps, but it does not control for content familiarity.

---

#### What I would do before Test B

If I were advising the founder, I would recommend the following sequence, in order of expected value per hour of work:

1. **Run a sensitivity analysis on `σ` and the rating cutpoints.** Plan the same three personas under three plausible values of each, and report how many stops change. This takes a few hours and tells you whether the prior uncertainty is the binding constraint.
2. **Replace the zero tag prior with a factor prior estimated from the tag matrix.** This is a one-time computation with no user data, and it will make cold-start plans more coherent.
3. **Use the four unused onboarding answers as prior shifts.** This is a small code change with a potentially large effect on the first plan.
4. **Add the pairwise sequence penalty to the planner.** One or two global parameters, estimated after Test B, and it directly addresses the fatigue effect that the literature says is real.
5. **Keep the LLM out of the decision loop; use it only to rephrase reasons, grounded in features.** Test this with a small pilot before committing.
6. **Collect a money-worth question and a repeat-intent question at the end of each day.** These are cheap and they fill the outcome gap.
7. **Reframe Test B as a formative test, not a pass/fail gate.** Report the paired rating difference, not just the 7/10 threshold, and treat 7/10 as “keep going” rather than “proven.”

The architecture is not wrong. It is **under-evidenced in exactly the places where evidence matters most**, and the path to fixing that is shorter than the document’s length suggests. The founder’s instinct to keep decisions transparent and explainable is correct; the next step is to make the numbers inside that transparent model earn their place.

## Review 2

### ODYS algorithm review: Is it actually the right algorithm?

My overall assessment is that ODYS has a strong foundation, but its recommendation quality is not yet proven. I would improve the current model rather than replace it.

The most important distinction is between building a mathematically sophisticated recommendation engine and building an algorithm that consistently gives someone a day out they genuinely enjoy.

I reviewed your eight-page document, including the Bayesian preference model, onboarding questions, itinerary optimiser, weather handling, explanations, personalisation examples and proposed Test B experiment. I've also compared the main design choices with research on recommender systems, Bayesian preference learning and itinerary optimisation.

#### My assessment at a glance

Core architecture: keep it

A personalised utility model followed by a constrained route optimiser is a sensible, interpretable foundation. It is well suited to your current catalogue and product stage.

Statistical validity: not established

Most population weights and rating thresholds are still guesses. There are too few observations to confidently estimate all personal preferences, and the model has not yet been validated against real outings.

Real-world itinerary quality: highest priority

Travel friction, fatigue, repeated types of places, companions and changing energy levels can make a mathematically high-scoring day feel exhausting or repetitive.

User experience: promising, but needs refinement

The app asks several useful questions, but some answers are ignored, some explanations repeat, and the money-equivalent value could imply more certainty than the model deserves.

#### 1. Is your chosen algorithm fundamentally right?

Yes, for the first version of ODYS. I would not switch to a large language model, collaborative filtering or a contextual bandit as the main decision-maker today.

Your system has two distinct jobs:

1. Preference estimation: infer what experiences a particular person is likely to enjoy.
2. Itinerary optimisation: choose and order places that fit their time, budget, opening hours and travel constraints.

Your Bayesian random-utility model addresses the first job. OR-Tools addresses the second. This separation is an advantage: you can debug why a place was scored highly independently from why it was included in a route. It also avoids making a language model responsible for calculations and feasibility constraints.

This is consistent with established research on personalised itinerary recommendation, which treats personal preference, ordered destinations and operational constraints as interconnected but distinct problems.

The crucial caveat is that a good architecture does not guarantee good predictions. The actual quality depends on whether the input features mean what you think they mean, the estimated preferences reflect real people, and the optimiser rewards what makes a day enjoyable.

#### 2. The biggest statistical weakness: the model knows less than its scores suggest

Your document is refreshingly honest about this. It says that most population weights are guesses, the individual weights have not been trained on real testers' data, and the current model is a fixed-prior approximation rather than a fitted hierarchical model.

That honesty is important because it changes how I would interpret the examples in the document.

##### What the Bayesian approach gets right

The model starts with a population-level preference vector and adjusts it as the person answers questions. In simplified form:

\\[ \beta_i=b\_{\mathrm{pop}}+\delta_i \\]

This is a sensible structure. A new user has almost no personal data, so the system starts from a general prior. As the user supplies evidence, their estimated preferences move away from that prior.

That is preferable to treating five or ten answers as sufficient evidence to learn an entirely separate preference model from scratch. Bayesian shrinkage is useful precisely because it moderates estimates when individual data are sparse.

The limitation is that shrinkage cannot make a bad prior correct. Your current model starts with zero for most feature weights and several manually selected adjustments. Until those assumptions are validated, the system's apparent personalisation is partly driven by design decisions rather than demonstrated user preferences.

##### Why 12 answers cannot reliably identify 25 personal preferences

Your current system estimates about 25 personal deviations, while the initial onboarding collects approximately six place responses and five hypothetical-day choices, with other answers contributing additional information or priors.

There is no strict rule that the number of observations must exceed the number of parameters in a Bayesian model. The prior can stabilise estimates even when that condition is not met.

But there is a practical problem: several different preference profiles may explain the same small set of answers.

Imagine someone chooses five packed-day scenarios. Is this person genuinely enthusiastic about busy itineraries? Or did they prefer those scenarios because the destinations were more interesting, the transfers were shorter, or the cost was lower?

The model may produce an estimate regardless, but that does not mean it has identified the underlying preference accurately.

My recommendation: retain the Bayesian structure, but make better use of the data it has.

1\. Keep strong population priors initially.

Do not try to learn 25 independent personal effects from five choices. Start with a small number of interpretable preference dimensions, and let the person's own evidence gradually override the defaults.

2\. Fit the population model using accumulated data.

Estimate population means, variation between people and response thresholds from real users. Do not treat a small pilot as enough to reliably fit a 25-feature hierarchical model; the necessary data volume will depend on how strong and correlated the preference signals are.

3\. Use uncertainty to control confidence.

If a user has not provided enough evidence about crowds, do not confidently tell them that they dislike crowds. Keep that estimate uncertain and avoid letting it dominate the itinerary.

Research on Bayesian active learning suggests a further improvement: select the next question based on how much it is expected to improve the predictions you care about, not simply how much it reduces uncertainty in the underlying parameters. That is particularly relevant here because ODYS ultimately needs to predict enjoyable itineraries, not perfectly estimate an abstract vector of preferences.

##### The five "this or that" questions need better experimental design

Each hypothetical day can vary six attributes: walking distance, longest transfer, weather, pace, crowds and cost.

These are meaningful attributes, but if both options differ on several dimensions simultaneously, it becomes difficult to identify which trade-off drove the answer. Five choices are especially limited when there are many parameters.

I would keep the paired-choice format because it asks people to make a concrete decision rather than rate a collection of abstract traits. However, I would design the comparisons more deliberately.

For example:

EXAMPLE QUESTION — ILLUSTRATIVE, NOT A CURRENT ODYS SCREEN

##### Which day would you prefer?

A slower day

3 stops, 3 km walking, shorter transfers.

A fuller day

5 stops, 8 km walking, longer transfers.

Keep cost and weather the same in this comparison. A separate comparison can test whether someone trades money for better experiences.

This particular contrast helps reveal a pace-and-walking trade-off. Other questions can isolate spending versus experience quality, quiet versus lively environments, or travel time versus destination appeal.

The goal is not to isolate every feature perfectly in the first five questions. It is to avoid unnecessarily confusing the evidence. Later, ODYS can select whichever comparison is most informative for the person's likely itinerary decisions.

Also, your document says that "No preference" is recorded but not fitted. I would either model this as indifference or remove it as a formal answer option until it is supported. Someone saying that two days are equally attractive is not necessarily giving the same information as someone who skips a question.

#### 3. An important problem in Test B: the success threshold is too weak

Your proposed test compares the personalised itinerary with a generic itinerary, presented in random order without photos or explanations. Both plans are for the same Saturday, time window and starting point, with their durations kept similar.

That is a good start. It helps isolate itinerary preference rather than letting attractive images or persuasive copy decide the result.

However, the rule that at least 7 of 10 people must prefer the personalised plan is not strong statistical evidence of success.

If ten people independently choose between two equally preferred plans, with each plan having a 50% chance of winning, the probability that at least seven choose the same plan by chance is:

\\[ P(X\geq7\mid n=10,p=0.5)=0.171875 \\]

That is about 17.2%. In other words, a 7–3 split is quite plausible even when personalisation has no real advantage.

For ten participants, even an 8–2 split has an exact one-sided binomial probability of about 5.47% under that null model. The sample is simply too small to distinguish a modest real improvement from chance with much confidence.

##### How I would improve the experiment

| Element            | My recommendation                                                                                                                                                                                                                                   |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Initial pilot      | Use around 10–15 participants to find obvious problems, understand their reasoning and verify that the test works. Treat this as exploratory, not proof.                                                                                            |
| Main comparison    | Choose a target effect and sample size before the experiment. For example, under a simple one-sided exact binomial test, detecting a true preference rate around 70% against a 50% null with approximately 80% power takes roughly 37 participants. |
| Generic baseline   | Keep the handcrafted popular-sights itinerary, but add a second baseline generated by the same algorithm using population preferences only.                                                                                                         |
| Main outcome       | Record the preferred itinerary and each plan's independent fit rating.                                                                                                                                                                              |
| Real-world outcome | Subsequently test whether people actually follow the plan, enjoy the stops and feel the overall day was worth the money.                                                                                                                            |

The sample-size figure is illustrative: it assumes independent participants, a 50% null preference rate, a true 70% preference rate, and a one-sided 5% significance level. It is not a universal sample-size requirement.

There is also an important distinction between the two baselines.

- Comparing personalised ODYS with a manually curated itinerary asks whether your algorithm can compete with a reasonable human-created plan.
- Comparing personalised ODYS with the same engine using only population preferences asks whether personalisation actually improves the plan.

You need the second comparison to isolate the specific value of your Bayesian model.

Recommender-system evaluation research cautions that offline predictions and real-world user satisfaction are not interchangeable, because relevance is subjective and feedback is affected by what people were shown. Your blind comparison is a useful first experiment, but it should be followed by a test with real outings.

#### 4. The route optimiser needs to understand the whole day, not just individual stops

Your OR-Tools approach is appropriate. The official documentation supports routing under time-window and other constraints, while noting that a feasible solution is not necessarily the globally optimal one.

However, the more fundamental issue is the objective you're asking it to optimise.

The current system largely scores stops independently, subtracts transfer disutility, and applies rules for hours, budget, lunch, pace and variety. That is a reasonable first version, but an enjoyable itinerary is not simply the sum of individually enjoyable locations.

Imagine two possible days:

Day A: four excellent attractions

Every stop has a high predicted score, but the route involves long transfers, extensive walking and two crowded museums in succession. By the final stop, the user is tired.

Day B: three very good experiences

The locations are closer together, there is a proper lunch break, the activities vary, and the final stop is easy to reach. The user finishes the day feeling satisfied rather than exhausted.

A stop-by-stop model can favour Day A even when Day B would be a noticeably better experience.

Research on itinerary recommendation identifies time-dependent preferences and nonlinear distance effects as important limitations of simpler models. In particular, what someone wants to do can depend on when and where they are, not simply on the location's features.

##### 4.1 Add a simple model of fatigue, repetition and day rhythm

You do not need a complicated sequence-learning model immediately. I would start with a few low-dimensional terms and constraints.

| Factor             | What I would implement first                                                                                | Why it matters                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Cumulative walking | Estimate total walking and penalise routes that exceed the person's preferred level.                        | A preference for active experiences does not necessarily mean unlimited walking.   |
| Fatigue            | Apply a modest penalty as the day accumulates walking, time and demanding activities.                       | An activity may become less appealing late in the day.                             |
| Repetition         | Penalise repetitive sequences, such as several similar museums or crowded indoor attractions in succession. | Variety matters within a day, not just across users.                               |
| Rhythm             | Consider alternating demanding and restorative stops, with reasonable lunch and rest opportunities.         | The sequence itself affects how manageable a day feels.                            |
| Ending             | Prefer a satisfying, practical final stop when choices are otherwise comparable.                            | It improves itinerary structure without assuming an unproven psychological effect. |

Initially, these can be simple rules. Do not estimate five additional personal weights for each new form of fatigue before you have enough data.

For example, an itinerary could accumulate a fatigue score based on walking distance, elapsed time and demanding activities. A later stop would receive a small penalty as that score grows. You can start with conservative values, label them as heuristics internally, and test whether the resulting days are better.

I agree with keeping the peak–end bonus switched off for now. First measure whether end-of-day satisfaction predicts overall trip satisfaction beyond the average of the stop ratings. Then test whether changing the ending improves the outcome.

##### 4.2 Audit a potential transfer-cost bug

There is one specific implementation detail I would check before doing anything else.

Your description says that transfer-time hinges enter the feature vector used to calculate each candidate's utility. It then says that the optimiser separately charges each route leg for the person's transfer penalty.

If the same incoming journey is included in both calculations, the transfer disutility may be counted twice.

I cannot confirm this without examining the actual source code, but the written specification is enough to justify an audit.

For every candidate stop, trace exactly which travel minutes enter its feature vector. Then trace which travel minutes are charged again when the solver adds the preceding leg. The intended result should be clear: each source of travel discomfort should enter the objective exactly as designed, not accidentally twice.

Also, be careful with the fallback from TfL travel estimates to straight-line distance. That may be sufficient for rough geographical screening, but it is not a reliable substitute for an actual route through London's streets and transport network. A solver cannot correct a misleading travel-time matrix merely by optimising it.

Use conservative estimates or communicate uncertainty when proper travel data are unavailable.

##### 4.3 Your lunch bonus may be overpowering the preference model

The document specifies a lunch bonus of five utility units for days that span 11:30–13:30.

There is nothing wrong with making lunch a regular part of a day out. I agree with the product decision.

The question is why it is implemented as a reward in the same objective used to rank experiences.

The score for each stop is its utility minus a floor. A fixed reward of five units could dominate the reward from several ordinary attractions, depending on the actual score distribution. This may be exactly what the solver needs to preserve lunch, but it risks making the model's preferences misleading.

My recommendation: treat lunch as a planned break or explicit scheduling constraint, rather than presenting an arbitrary bonus as though lunch intrinsically has five utility units of enjoyment. If lunch quality matters to the user, score the available meal experiences separately.

##### 4.4 Be cautious with the popularity nudge

I like the motivation behind your variety nudge. Your simulations show a popular fallback attraction appearing in 38% of plans, falling to 28% after the nudge. That is a useful warning that a cold-start model can make everyone else's itinerary look nearly identical.

However, your simulated popularity estimates come from people generated using mostly guessed priors.

That means the nudge partially corrects a distribution created by your own assumptions, rather than one learned from actual user behaviour.

There are two different problems to solve:

- Personal variety: avoid giving someone a monotonous itinerary.
- Population diversity: avoid showing every user the same attractions.

I would prioritise the first. Use a small penalty for repeated experience categories, or a diversity-aware objective, while preserving your existing rule that diversity should not meaningfully reduce the user's predicted utility.

Keep the 0.1-utility-loss cap as an initial guardrail, but validate that its scale is meaningful. Do not penalise an attraction simply because it is genuinely the best option for many people.

##### 4.5 Replace arbitrary cliffs with probabilities where possible

Three rules deserve particular attention.

The Good-rating floor. The current cutpoint at \\(-0.75\\) separates Fine from Good in your ordered-logit model. At exactly that score, the model assigns a 50% probability to a rating of Good or better. A score just above it does not constitute a strong guarantee of enjoyment.

Instead of calling this a minimum Good experience, calculate the probability of a Good-or-better rating and choose a threshold after testing the model's calibration. The appropriate threshold depends on the quality and quantity of evidence you eventually collect.

Rain at 50%. Your planner removes dry-only cards once the chance of rain reaches 50%. A card may suddenly disappear when a forecast changes from 49% to 50%, even though its expected usefulness has changed very little.

Keep hard exclusions for genuinely infeasible experiences. For places that are merely less enjoyable in the rain, a continuous weather penalty plus an indoor alternative is more sensible.

Hard budgets. Respecting a user's budget is essential. But the meaning of each budget band must be explicit: is it an absolute total spending ceiling, a preferred spending range, or a rough target? If someone chooses £20–40, a plan that spends £39 may technically comply but still be uncomfortable if transport and food are not adequately represented.

For each rule, make the distinction between a genuine constraint and a soft preference explicit. The optimiser should not treat those two things interchangeably.

#### 5. The user experience: what the mathematical model means to a real person

Your system has a potentially compelling value proposition: it understands how a person wants to spend their day, rather than simply listing famous places. The algorithm must make that promise believable in the interface.

##### 5.1 The onboarding questions are not necessarily too many, but they need to earn their place

Six place responses and five hypothetical-day comparisons amount to around eleven initial interactions.

That is not inherently excessive. Research into adaptive preference elicitation shows that more structured choice tasks can take longer while sometimes generating better preference estimates and more realistic responses. A separate 2025 study of conversational recommender systems found that guided preference elicitation improved recommendation match scores, although its results were context-specific and did not show a significant improvement in every subjective user-experience measure.

The relevant question is whether each interaction contributes to a better first plan.

I would measure completion time, skipped questions, onboarding abandonment and whether people feel the resulting plan reflects their answers. Give users a clear sense of progress and let them skip questions that they cannot answer confidently.

Most importantly, show them a useful first itinerary promptly. Personalisation should become progressively better through use, rather than forcing people to complete a lengthy personality questionnaire before receiving value.

##### 5.2 Do not collect answers that have no effect on the product

Your document identifies four inputs that are collected but not used by the planner: who the person is going with, morning or night preference, activity level and the free-text "best hour" answer.

There are also potentially valuable signals from the photo-related preference question that are not yet used.

This is a product-design problem, not merely a modelling problem. When a user answers a question, they reasonably expect the app to do something with the answer.

I would either implement a simple, defensible use for each question or remove it until that use exists.

For example:

- Morning or night person: adjust the preferred scheduling window where venue hours allow.
- Activity level: apply an itinerary-wide walking or exertion constraint.
- Who they are going with: begin with a simple solo, partner, family or friends distinction if it has a clear effect on the plan.
- Photos: use the preference to rank suitable photo moments, but only when there is a genuine fit.

Do not add a complex model simply to justify keeping every field. The simplest valid implementation is usually enough.

##### 5.3 Your feeling-to-feature mappings need validation

The app asks how users want to feel, including restored, excited, connected, curious and peaceful. The document maps these answers to fixed combinations of place and experience features.

For example, peaceful maps to lower crowds and better views. That is a reasonable hypothesis. However, it is still a hypothesis.

A person might feel peaceful in a small independent bookshop, a quiet museum, a botanical garden or a canal-side café. Green space and views are useful signals, but they do not necessarily represent the whole experience of peacefulness.

I would retain the feeling-based onboarding because it expresses the emotional goal of ODYS well. But I would treat the mappings as initial design assumptions to validate through feedback, not as established psychological relationships.

Long term, consider modelling a desired feeling at the itinerary level. This could mean rewarding a balanced combination of compatible experiences, rather than forcing the meaning of an entire day into a few independent location features.

##### 5.4 The explanations are more important than displaying the raw scores

The document says that users may see up to two reasons for each stop, generated from their previous answers. It also acknowledges that similar explanations repeat.

For Ben's example, the system repeatedly says that the user liked the British Museum and this attraction has history too.

That is technically consistent, but it does not help the user understand why the third museum is the right choice after visiting two others.

A stronger explanation should communicate a specific benefit that the person can recognise:

- Why this experience matches their interests.
- Why it works at this particular point in the day.
- Why it adds something that the previous stops do not.
- Why its cost or travel time is a reasonable trade-off.

Avoid explaining everything at every stop. One accurate, distinct explanation is better than two repetitive ones.

Research on recommender explanations distinguishes goals such as transparency, satisfaction, decision effectiveness and trust, which are not always aligned. The important test is whether the explanation helps a user judge the recommendation, not whether it exposes more of the model's calculations.

##### 5.5 "Worth £58 to you" could undermine trust

This is one of the most distinctive features of ODYS, but also one of the riskiest.

Your calculation turns predicted utility into a money-equivalent value using the estimated cost coefficient. This gives the model a financially interpretable output. Mathematically, that conversion is coherent under the assumed utility and cost model.

The problem is the strength of the claim implied by the interface.

At present, most model parameters are guesses, individual cost preferences are based on very little evidence, and you do not yet measure whether users actually feel that an experience was worth its money or time.

If the app says that a free rooftop visit is worth £58 to a person, they may reasonably ask: "How can you know that?"

The answer is that the model has translated its predicted utility into an estimated money equivalent. It has not established that the person would actually pay £58, or even that the estimated amount is accurate.

I would keep this calculation internally for experimentation, but initially either hide it or label it clearly as an estimate. Show it more prominently only when you have enough evidence to establish that it correlates with what users report about value.

You should also distinguish the estimated personal value of an experience from its actual price, the amount a person is willing to pay, and whether the overall day felt worth its total cost. Those are related, but different, outcomes.

##### 5.6 The "how the day moves" curve may make an unearned promise

A curve based on the predicted utility of each stop looks like an emotional progression: the day starts in one state, rises, and finishes in another.

But your current utility is primarily a measure of predicted stop appeal. The model does not adequately represent how an earlier stop changes the enjoyment of a later one.

Until fatigue, sequence and satiation are represented, I would label this as the predicted fit of each stop, rather than imply that ODYS predicts the person's emotional journey throughout the day.

That distinction matters because the product's emotional promise is stronger than its present sequence model.

#### 6. Should a language model be involved?

My recommendation is option (b): use a language model as an interface to the algorithm, not as the authority that chooses the places.

I agree with your founder's instinct to keep the underlying decisions transparent and reproducible. You do not need an LLM to compute preference scores or satisfy route constraints.

There is, however, a useful role for language understanding.

#### A sensible division of responsibilities

User expresses a need

"It's raining, I'm tired, and I don't want to spend much today."

Language model translates it

Weather override: rain. Current energy: low. Budget ceiling: confirm the intended amount if unclear.

ODYS calculates the plan

The existing preference model and route optimiser use the structured conditions, constraints and verified place data.

The app explains and confirms

The user sees what changed and can review the new itinerary or correct the interpretation.

Two safeguards are important.

First, distinguish stable preferences from temporary conditions. "I usually enjoy quiet places" might update the personal preference model. "I'm exhausted today" should normally alter today's plan, not permanently convince the system that the user dislikes walking.

Second, an LLM-generated explanation should be grounded in the actual route and the evidence used by the algorithm. It should not invent reasons for choosing an attraction or claim to understand a user more deeply than the data supports.

I would avoid option (c), letting a language model independently choose the destinations, for now. It adds uncertainty to feasibility, reproducibility and evaluation without solving the main weaknesses identified in your current system.

Later, you can compare a language-assisted interface with the existing interface in a controlled test. The question should be whether it helps people express their needs and understand their plans more easily, rather than whether AI makes the product appear more advanced.

#### 7. Group planning deserves explicit attention

Your document acknowledges that a group of friends receives the plan of whichever person created it. That is a significant limitation for a day-out product.

It is not necessary to solve sophisticated group preference learning immediately. But I would not leave this issue entirely unaddressed if partners and friends are central users.

Start with separate personal preference profiles when group members are willing to contribute them. Then compare a few simple aggregation methods:

| Approach                                              | What it prioritises                                                     | Main drawback                                                             |
| ----------------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Average utility                                       | The group's overall predicted enjoyment                                 | One person's strong dislike can be hidden by everyone else's high scores. |
| Least misery                                          | Protecting the least satisfied person                                   | May produce an overly conservative itinerary.                             |
| Average utility with a minimum-satisfaction guardrail | Good overall enjoyment while preventing a bad experience for one member | Requires a meaningful minimum-satisfaction threshold.                     |

These are established approaches in group recommendation research, although none is universally best.

For ODYS, I would start with average utility plus a guardrail against recommendations that are predicted to be particularly poor for one member. It is a practical compromise, and it is easier to explain than a complex social-welfare objective.

At minimum, let the user clarify whether the plan is for them alone or for a group. Do not imply that the system is creating a group-optimised day if it is actually optimising for just one person's preferences.

#### 8. What I would actually change, in order

The biggest risk is spending months making the statistical model more sophisticated before establishing that its current decisions produce better days.

I would use the following roadmap.

#### 01

##### Fix the high-risk assumptions

Highest priority

Low-to-moderate effort

Audit whether transfer penalties are counted twice. Validate the Good-rating floor against the ordered-logit probabilities. Check whether lunch's fixed reward overwhelms ordinary stop rewards. Verify that budgets, opening hours, travel estimates and wet-weather rules behave as intended.

#### 02

##### Make feedback useful and trustworthy

Low effort

Remove or implement unused onboarding fields. Make reasons distinct. Avoid false precision in personal monetary value. Keep track of the answers behind each recommendation so users can correct misunderstandings.

#### 03

##### Improve itinerary quality

Moderate effort

Add lightweight fatigue accumulation, walking limits and category-repetition penalties. Preserve realistic slack between stops. Use the variety nudge as a secondary objective rather than letting popularity dominate.

#### 04

##### Improve the onboarding experiments

Moderate effort

Design comparisons that reveal meaningful trade-offs. Retain explicit indifference where appropriate. Make the blind Test B comparison fair, and follow it with field testing. Measure whether the user enjoys the day, not just whether a written plan sounds attractive.

#### 05

##### Fit the learned model from real data

After collecting sufficient observations

Estimate population weights, preference variation and rating thresholds using a properly regularised hierarchical model. Use held-out users and later experiences to validate predictions before increasing model complexity.

##### What should you measure after someone uses ODYS?

I would not rely on a single 1–5 rating. The product is trying to optimise both enjoyment and value, and those are not quite the same.

After each stop, collect a simple enjoyment rating and retain the contextual data: actual visit duration, travel time, weather and any meaningful plan changes. Then, at the end of the day, ask whether the overall plan felt worth the time and money. A single optional question about whether they would choose a similar experience again could provide another useful signal.

Do not bombard the user with a questionnaire after every stop. The initial objective is to collect a small amount of high-quality feedback, not every possible data point.

Also record when people replace or skip recommendations. A user removing a particular stop can be informative, but it is not automatically evidence that the user dislikes that category of experience. They may be tired, late or already familiar with the location. This is one reason real-world recommender feedback needs careful interpretation.

#### 9. When should you consider more advanced algorithms?

| Technique                   | My recommendation for ODYS                                                                                                                         |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hierarchical Bayesian model | Yes, when the data supports it. This is the natural next step for estimating population preferences and personal differences.                      |
| Pairwise learning-to-rank   | Test as a benchmark. It may directly optimise which itinerary people prefer, but it requires informative preference labels and careful validation. |
| Collaborative filtering     | Revisit when the catalogue and user population are large enough to support reliable user-to-user or item-to-item patterns.                         |
| Contextual bandit           | Consider later, when you have enough repeated interactions and a reliable outcome metric.                                                          |
| Thompson sampling           | Potentially useful for controlled exploration among similarly good options, rather than deliberately serving a substantially worse day.            |
| LLM-selected destinations   | I would not use this as the core decision mechanism. Keep planning and constraints deterministic and testable.                                     |

The immediate bottleneck is the quality of your evidence and itinerary objective, not the absence of a more fashionable machine-learning technique.

You can already use the posterior uncertainty available in your Bayesian model to design better questions. Once the model is sufficiently calibrated, you can explore more advanced adaptive questioning and controlled exploration. But there is little value in optimising for information gain if the priors and features are still poorly specified.

#### My final verdict

Keep the model architecture. Improve the model's assumptions, the route objective and the validation process before replacing it with something more complex.

The most valuable part of ODYS is not that it uses Bayesian estimation or OR-Tools. It is that you are trying to model a real human problem: people want days out that suit their tastes, energy, time, budget and desired feelings, without having to do all the research themselves.

That is a worthwhile problem to solve. And the current architecture is capable of helping solve it.

But I would not yet claim that the algorithm reliably understands a person from eleven onboarding interactions, or that it can confidently quantify what an experience is worth to them. Those are hypotheses to validate.

With your limited development time, I would concentrate on four things: verify the scoring and travel-cost logic, make the feedback loop genuinely useful, improve whole-day itinerary quality and run a fair experiment that measures actual enjoyment.

Once those work, fitting the population priors becomes meaningful. Only after that would I consider a bandit or a substantially more complex model.

The goal should not be the most intelligent algorithm on paper. It should be that, after a user has tried ODYS several times, they feel that it increasingly understands the kind of day they want—and can explain its choices in a way that feels both accurate and honest.

## Review 3

**Yes, this is a strong, appropriate core algorithm for the stated goals** (transparent, personalised, feasible day plans from sparse preference data, no opaque LLM deciding what people should do). It sits squarely in the mainstream of the tourist trip design / personalised itinerary literature while prioritising explainability and practical constraints in a way many research systems ignore.

##### Alignment with research and practice
The combination of a **random-utility / discrete-choice model** for person-specific scores + an **orienteering problem with time windows** (solved via OR-Tools) is the dominant formulation for the Tourist Trip Design Problem (TTDP). Multiple recent surveys and papers treat itinerary recommendation as (1) scoring POIs via user interest models and (2) selecting + sequencing them under time, opening-hours, budget and transfer constraints to maximise cumulative utility. Variants appear under names such as TOPTW (Team Orienteering Problem with Time Windows), multi-day OP with personalisation of pace/diversity, and hybrid recommender + metaheuristic solvers.

Your Bayesian shrinkage to a population prior (MAP + Laplace approximation) is a principled way to handle the extreme cold-start / sparse-data regime (~12 observations against ~25 personal weights). Ordered logit for ratings and swipes, binary logit for stated choices, and a swiping-level term are statistically coherent. The explicit transfer hinges, weather interactions, cost sign constraint, and hard rules (disliked places, dry-only, lunch slot) are pragmatic and user-experience-aware—features many pure optimisation papers under-emphasise.

The founder’s stance against letting an LLM choose places is defensible. Research systems that end-to-end optimise with deep models often trade transparency and auditability for marginal accuracy gains; with a small catalogue and the need for users to trust “why this day,” the transparent model is the better product bet right now.

##### Strengths from a user-experience perspective
- **Rapid personalisation with few answers.** The worked example shows that a dozen responses already move plans meaningfully (crowds weight, green/nature, pace). Users feel the system is listening quickly—critical for onboarding retention.
- **Explainability built in.** “You loved Hyde Park and this has green space,” “worth about £V,” feeling-based headlines, and the day-curve are excellent. Transparency reduces the “black-box recommendation” distrust common in travel apps.
- **Feasibility first.** Opening hours, TfL times + buffers, lunch enforcement, rain swaps, budget hard constraints, and the floor at “Good” prevent the classic failure mode of beautiful-but-impossible itineraries.
- **Value framing.** Ranking by non-cost utility divided by –β_cost produces a natural “worth £V to you” that is mathematically consistent with the model and psychologically powerful.
- **Variety nudge with a soft utility cap.** Simple, effective, and respects the user’s own weights. Without it the system collapses to the same popular stops for cold-start users—exactly the problem many popularity-biased recommenders create.
- **Test design (Test B).** Blind, length-controlled A/B against a strong generic plan is the right success metric. Preferring the personal plan ≥7/10 is a high but clear bar.

##### Weaknesses and risks (expanding your own critique)
Your Section 11 list is accurate and honest. Additional points from literature and UX:

1. **Thin data vs. dimensionality.** With σ ≈ 0.75 and ~12 observations, most weights remain “unsure.” Plans are driven by the few confident dimensions. Hierarchical Bayesian refit (your planned PyMC step) is essential; until then the population prior dominates and cold-start plans converge.

2. **Linearity and missing interactions.** Hand-crafted tags + only weather interactions cannot capture satiation (“two museums feel worse than museum + park”), fatigue, time-of-day effects, or sequencing value. Activity-based modelling literature routinely includes these; pure linear utility underestimates diminishing returns and day-shape preferences (you already estimate a long-walk weight that never reaches the planner).

3. **Hand-crafted tags as a bottleneck.** Expert tags carry measurement error and do not scale. Research increasingly learns embeddings or refines tags from ratings across users; pure judgement tags will become the limiting factor as the catalogue grows.

4. **Cold-start prior is a pure guess.** Recent work shows LLM-elicited or demographic-informed priors can meaningfully improve early accuracy; your zero-ish prior is conservative but leaves value on the table.

5. **Exploration is absent.** Pure MAP exploitation means the system never deliberately shows something uncertain-but-potentially-high-value. Thompson sampling from the posterior is the natural next step, with a clear utility-loss budget.

6. **Group and multi-day memory.** Single-person weights + no cross-day memory outside trips will frustrate real usage (friends, returning visitors).

7. **Outcome sparsity.** 1–5 ratings after the fact are noisy and delayed. “Worth the money?” and “would go again?” are closer to the product goals but harder to collect without friction.

8. **UX friction points.** Collecting answers you ignore (company, morning/night, activity level, free-text best hour) trains users that the system is not listening. Template reasons become repetitive (as in the Ben example). With a 49-card catalogue, differentiation between users is inherently limited.

##### Direct answers to your 12 reviewer questions
1. **Core model.** Random-utility with per-person shrinkage is the right core for transparency + sparse data. Once you have hundreds of testers, add a hierarchical layer and consider collaborative-filtering or pairwise learning-to-rank components on top of (not instead of) the feature-based utility. Contextual bandits are better for pure exploration/exploitation than for constrained itinerary construction.

2. **Information-rich questions.** The 5 this-or-that days (explicit trade-offs on transfer, weather, pace, crowds, cost, walking) and the post-stop ratings are highest-value. Swipes are useful but noisier. Adaptive selection by expected information gain (or simple expected value of information) would be a clear upgrade over a fixed questionnaire.

3. **Fatigue / sequencing / satiation.** Keep the parameter count low: (a) category-satiation penalties that grow with consecutive similar tags, (b) a simple cumulative “effort so far” state that multiplies the walking/active weights, (c) peak–end style bonuses only on the last stop or the highest-utility stop. These can be added as deterministic adjustments inside the orienteering prize without exploding the personal-weight vector.

4. **Exploration.** Yes—Thompson sampling (or posterior sampling of a few candidate plans) once you have the Laplace approximation. Cap the expected utility loss at ~0.1–0.2 (roughly the £4 variety-nudge tolerance) so users rarely receive a noticeably worse day.

5. **Unused answers.** Treat company and activity level as hard constraints or soft multipliers on the relevant tags; morning/night as a prior shift on time-window preferences; photos as a weight on the photo-potential tag. Free-text “best hour” is ideal for an LLM feature extractor (option b below).

6. **Groups.** Start with average utility (simple, transparent). Move to a “least-misery” or weighted Nash product once you have data on how groups actually compromise. Always surface the individual scores so the group can negotiate.

7. **Outcome.** 1–5 is necessary but not sufficient. Add a lightweight “was the money worth it?” (binary or 3-point) and an optional “would you bring someone here?” after the day. These map cleanly onto the cost and social-pull dimensions.

8. **Tags.** They are currently a bottleneck. After Test B, run a hierarchical model that treats tags as noisy observations and learns residual item effects, or learn low-dimensional embeddings from the rating matrix and project the hand tags into that space. Keep the human-readable tags for explanation.

9. **Variety nudge.** Sound and simple. Cleaner alternatives exist (determinantal point processes, submodular diversity objectives, or explicit category-coverage constraints inside OR-Tools), but the £4 soft cap is a good pragmatic compromise.

10. **Peak–end.** Test it. Implement as an additive bonus on the final stop (or the max-utility stop) proportional to its utility, with a small coefficient. Measure whether post-day ratings rise.

11. **What to remove for a solo founder (~7.5 h/week).**  
   - Peak–end (already off).  
   - Full multi-day trip engine beyond the simplest version.  
   - Elaborate rain-swap UI until the core single-day engine is solid.  
   - Any new answer types that are not immediately used by the planner.  
   Focus ruthlessly on: hierarchical refit after Test B, better cold-start prior, adaptive questioning, and tightening the reasons/explanations.

12. **Where should a language model sit?**  
   **Strong recommendation: (b) language only.**  
   - Parse free-text (“best hour”, “it’s raining and I’m tired”, group composition notes) into the existing feature vector or hard constraints.  
   - Generate the natural-language explanations and headlines from the weights and the user’s own answers.  

   Risks of (a) pure status quo: you leave free-text and nuanced context on the table.  
   Risks of (c) AI chooses the places: opacity, harder debugging, potential misalignment with the transparent utility the user has been teaching, and loss of the “I can see why” trust that is a core product differentiator.  

   Hybrid later is fine (LLM proposes candidate moments that still go through the utility + orienteering filter), but keep the final decision in the transparent model.

##### Priority roadmap given the constraints
1. Finish Test B and the hierarchical refit—this is the highest-leverage step for both accuracy and cold-start quality.  
2. Make questioning adaptive and ensure every collected signal affects either weights or hard constraints.  
3. Add minimal satiation / sequencing terms and the long-walk weight into the planner.  
4. Introduce light exploration (Thompson) with a tight utility budget.  
5. Improve reason generation (diversity of templates, reference more answer types).  
6. Only then expand the catalogue or add multi-person logic.

Overall this is one of the more thoughtful, production-aware designs I have seen for personalised day planning. The combination of Bayesian personal utility, hard feasibility constraints, and deliberate transparency is the right foundation. The main risks are under-fitting interactions and under-using the data you already collect; both are solvable without abandoning the core philosophy.

## Review 4

I'll ground this in the research literature before giving my view, starting with the main pieces: trip planning, cold-start elicitation, bandits, group choice, and LLM use.
Verdict: the core is the right kind of algorithm for ODYS today. I've only seen the document, not the code, so this critique is of the design as described. My pushback is less about the model choice and more about three things: what the model does with no data, where guessed numbers leak into what users see, and how Test B is built. On UX, I think the 49-card catalogue and the length of onboarding will matter more than any modelling refinement.
Why the core is right
With about 12 answers per person and 49 items, collaborative filtering, learning-to-rank and bandits all starve. A feature-based utility with shrinkage to a population prior is what works at this volume. It is essentially hierarchical-Bayes choice modelling, which is how conjoint studies get individual-level estimates from few tasks. People with fewer answered tasks get pulled harder toward the population mean.
Orienteering is also the standard formulation. It's the most widely applied model for the tourist trip design problem, and heuristic solvers handle real-world instances within a few seconds. Keeping feasibility in a solver rather than a language model is also where the evidence points (see question 12).
Where I'd push back
1. Cold start is probably "free, central, quiet" by accident. With tag priors at zero, the only things separating cards for a new person are crowds, cost and transfers. A free, always-open card next to the start point wins almost by construction, which fits Royal Festival Hall taking 38% of simulated plans. The variety nudge treats the symptom. Two root-cause fixes:

* Per-card intercept. Add a random effect learned from everyone's ratings. It captures quality the 15 tags can't (Soane's Museum is better than its tags say). Its variance also tells you whether the tags are the bottleneck.
* Archetype prior. Replace the single zero-centred prior with a small mixture of 3–5 archetypes (classic, quiet-green, local-foodie, deep-culture). One mean is a poor centre when tastes are multimodal, and the feelings screen can pick the archetype.

2. Planning treats a shrunk point estimate as knowledge. In Asha's example, one disliked place (Brick Lane, which is food plus crowds plus local) produced food −0.49. The explanations label that "unsure", but the planner uses it at full strength, which probably explains her generic "lunch near Waterloo". You already have the Laplace covariance, so utilities can carry variance (xᵀΣx). Make the "Good" floor probabilistic, P(u > floor) above some threshold, so uncertain weights stop acting like known dislikes.
3. The rating model is the least anchored part, and it will carry the most data.

* Cutpoints. The symmetric cutpoints are guesses, while your swipe data (4% / 41% / 55%) skews positive. Ratings in the wild tend to be heavily inflated, and people's scales are miscalibrated differently from one another.
* Missing leniency term. Swipes have a per-person leniency term, but ratings as described don't. A generous rater can then only be explained by inflating feature weights or pushing the cost weight toward zero.
* Fix. Add a per-person threshold shift for ratings, kept out of plan utilities like the swipe level. Refit the four global cutpoints at around 100 ratings, which doesn't need the full PyMC model.
* Labels. Your labels (Flat to Unforgettable) are the right kind of design: clearly defined, positive-skewed labels gave more informative rating distributions.
* The floor. The "at least Good" floor at u > −0.75 is probably non-binding now, since most predicted utilities sit near zero. It isn't evidence that stops are Good.

4. "Worth about £V to you" is the riskiest number on screen. V divides by β_cost = −0.25·e^δ. With σ = 0.75, the 95% range of e^δ spans close to 20×, and cost is informed only by one attribute across five hypothetical days. So V is mostly prior. A lenient rater, or someone who always picked the £60 day, gets a cost weight near zero and V explodes. Hypothetical choices also tend to overstate willingness to pay. For a product selling transparency, a precise-looking £31 vs £58 that people will compare with ticket prices is a trust liability. I'd show a band or a "strong match / good match", and show £ only once the cost weight is actually identified.
5. Trait and state are mixed. Wanting a peaceful Saturday shouldn't permanently lower someone's crowd weight, but onboarding feelings update δ. Treat feelings, and the unused company / morning-night / activity answers, as context shifts for this plan (u += Γ·z, using the feature map you already wrote). Keep δ for stable taste learned from ratings and swipes. Until a pooled refit can learn Γ, hand-set small shifts like your interest +0.25. Reserve hard rules for access needs.
6. Day-level structure is missing. Per-stop additive utility is why museums stack. The literature models this with submodular aggregation, where each additional POI of the same kind adds less, and itinerary work notes that a tourist who likes museums still wouldn't want five or six in a row, because of sensory overload. OR-Tools can't easily optimise a nonlinear day score directly, so use generate-and-rerank:

1. Solve, add a no-good cut, and repeat to get about 10 candidate days.
2. Rerank them with a day score that includes satiation, walking km and fatigue.
3. Use the walking weight you already estimate but never use, via a soft upper bound on a cumulative-distance dimension.
4. Replace the variety nudge with sampling among plans within your own £4 tolerance. That also gives you free, bounded-regret exploration.

Test B
Pass means at least 7 of 10 prefer the personal plan. By my calculation, a coin-flip would reach 7+ about 17% of the time (176/1024). If the true preference rate is 70%, you pass only about 65% of the time, and at 80% about 88%. That makes it a fair go/no-go signal but not evidence. Make the paired fit ratings the primary outcome, since they have far more power than a binary pick, and aim for 20–30 testers. Design issues:

* Recognition bias. With no photos or reasons, testers will favour names they recognise. That penalises exactly the lesser-known places a personal plan should surface. Test B probably understates the product, and it measures anticipated rather than experienced enjoyment.
* Third arm. Add the zero-answer plan. If personal ≈ zero-answer, the answers add nothing and the win comes from curation. That's fine, but it changes what you can claim.
* Stratify by tester. A list of famous sights is a strong comparator for visitors and a weak one for Londoners.
* Offline check first. Hold out some of the 235 swipe answers and compare held-out log-likelihood for personal vs population-only. It costs a day and tells you whether the personalization works before you spend testers.

UX perspective

* Onboarding length. There are roughly 15+ interactions before any value. Your 2 ms update and ~1 s solve allow a live plan that visibly changes after each answer ("this answer swapped X for Y"). Each answer is then rewarded, and you can stop asking whenever the person stops.
* Zero-answer front door. Skippers get one plan for everyone, with a repeated "we don't know much about you" reason. Show 2–3 archetype day previews and let them pick. One tap carries more information than a logistics A/B because the days differ on many content tags at once, and it feels like choosing rather than answering.
* Question mix. The this-or-that days vary logistics, not content. Content taste (10+ tags) rests on about 6 swipes plus interests, and multi-tag cards are confounded, as with Brick Lane. Pairwise choices between places ("which sounds more like your Saturday?") need no prior visit.
* Reasons. Dedupe them: each feature at most once per plan, and prefer contrastive wording ("quieter than most; you said you like quiet days").
* Dead questions. Free-text "best hour", company and the other ignored answers make people feel unheard. Either use them or stop asking.
* Ratings. Make them one tap and skippable. Log skips, swaps and dwell time as weak secondary signals.

Your 12 questions, briefly

* Q1. Keep the random-utility core. Add item intercepts, which is the cheap piece of collaborative filtering, and consider low-rank taste factors in δ later.
* Q2. Don't pick questions by pure information gain. The elicitation literature notes that not all information equally affects recommendation quality; often only a little is decision-relevant. Instead, sample about 20 posterior draws and pick the question (from a pool of ~30 pre-written ones) where the draws disagree most about the top candidates.
* Q3. See issue 6.
* Q4. No Thompson sampling in Test B, because over-exploration directly degrades user experience. In multi-day trips exploration pays within the same person, so use tempered posterior samples from day 2. For single days, use ε-optimal sampling. Ratings exist only for what you recommend, so features you never recommend are never learned.
* Q5. See issue 5: priors or context shifts, with hard rules only for access needs.
* Q6. No aggregation strategy wins everywhere; it depends on the group. In sequential settings, plain average gives good satisfaction but mediocre disagreement, and least misery the reverse. A day is a sequence, so:
   1. Filter out stops any member is likely to dislike.
   2. Maximise the summed prize.
   3. Re-solve with per-person multiplicative weights until each person's total is balanced.
* Q7. Add one end-of-day question ("was today worth what you spent?", 3-point) and a per-stop "would go again" tap. Treat skips and swaps as weak evidence. Don't ask money questions per stop.
* Q8. Have 2–3 independent raters re-tag the cards and compute weighted kappa per tag. Merge or drop tags below about 0.6. Since Claude drafts your tags, an audit by the same model family would have correlated errors. Use humans plus source text, and watch the item-intercept variance.
* Q9. See issue 6.
* Q10. You don't need an experiment, just a regression on data you already collect. Regress the end-of-day rating on the mean, min, max and last of the stop ratings. The evidence is mixed:
   * Among 691 Macau travellers, a simple average of episode ratings beat peak-end.
   * In a 49-student vacation study, peak-end wasn't an outstanding predictor.
   * A 2026 study of 2,576 transit trips found minimum-end predicted best.
Leave the bonus off. The robust and cheap takeaway is to avoid very bad stops and a weak final stop.
* Q11. See the list below.
* Q12. Option (b), narrowly bounded.

Question 12: where a language model should sit
The case against (c) is the evidence on constraint planning. On the 2024 TravelPlanner benchmark, GPT-4 succeeded only 0.6% of the time. Newer models do better, but the best pure-LLM result cited in a 2025 follow-up was about 10%, while an LLM-plus-solver pipeline reached 93.9%. Open-ended language remains the hard part: in the open-ended ChinaTravel benchmark, neuro-symbolic agents reached only 27.9%. So the model should translate language into a bounded schema and the solver should decide.
For ODYS that means:

* Free text to features.
   * Convert "it's raining, I'm tired" or the best-hour answer into schema-constrained feature deltas.
   * Clip the deltas.
   * Show the interpretation ("I understood: tired, fewer long walks. OK?") and let the user correct it, like your "not right" lines.
* Explanations.
   * Have the model paraphrase structured reason objects.
   * Add a verifier that checks every place and feature mentioned is in the reason object.
   * The verifier is mandatory: users rated unfaithful explanations as just as trustworthy as faithful ones when shown in isolation.
* Offline. Use the model for catalogue drafting, tag audits and synthetic-user stress tests, with humans verifying facts. Weakness 8 (the small catalogue) is best fixed by growing the verified catalogue, not by letting an LLM choose venues at runtime.

Risks of (b) are nondeterministic extraction (pin versions, cache, log), privacy of free text, and prompt injection, which the bounded schema mostly neutralises. Risks of (a) are dead questions and repetitive reasons. Risks of (c) are hallucinated hours and prices, non-reproducible tests, and no way to improve choices from ratings.
One framing note on Abram's position: the model is already machine learning, so the real distinction isn't algorithm vs AI. It is auditable, correctable and feasibility-guaranteed vs not.
If I had 7.5 hours a week

1. Offline held-out harness (personal vs population-only log-likelihood).
2. Rating leniency, refit cutpoints, and card intercepts.
3. Probabilistic floor, and £V shown as a band.
4. Generate-and-rerank with walking and satiation, plus ε-optimal sampling replacing the nudge.
5. Test B v2: paired ratings, three arms, at least 20 testers.

Defer trips, flights and stays, the visitor flow, and the peak-end code until the core claim holds. Language-model features come after that, starting with verified explanations.
I can sketch the item-intercept and leniency model, or the generate-and-rerank loop, in code, or put this review in a document.

## Review 5

Executive Verdict
The choice of a Bayesian Random Utility Maximization (RUM) model paired with OR-Tools for orienteering is fundamentally the right architectural choice for a bootstrap travel recommender. Avoiding LLMs for core decision-making ensures that ODYS remains transparent, deterministic, and fully explainable—vital traits for user trust. Grounding recommendations in microeconomic choice theory rather than black-box collaborative filtering or hallucination-prone LLM routing gives you total control over why a place is picked.

However, because the current population priors, cutpoints, and hyperparameters are uncalibrated guesses, the engine currently functions more like a heuristic rule-system than a fitted statistical model.

User Experience (UX) & Product Evaluation

* The "Broken Promise" of Unused Inputs: You collect data on who users go with, whether they are morning or night people, their activity level, and their "best hour," but the planner completely ignores them. From a UX standpoint, asking a user personal questions and visibly ignoring them creates friction and erodes trust. Either wire these inputs into hard filters/priors immediately or remove them from onboarding.

* The Cold-Start Homogeneity: Because population priors start at zero with generic guesses, users with zero answers receive identical itineraries (e.g., Royal Festival Hall, Waterloo Bridge). If a curious tester opens the app and gets a generic tourist loop, they may churn before giving enough ratings to train their personal weights.

* Repetitive Explanations: Template-based reasons ("You loved X, and this has Y too") quickly become monotonous when they repeat across multiple cards in the same plan. Transparency loses its psychological impact if the copy sounds robotic.

Core Algorithmic Critique

* The Satiation and Fatigue Blindspot: The model is strictly linear and treats all stops independently. Packing three heavy culture stops back-to-back yields a high linear score if the user likes history, but human cognitive fatigue and semantic satiation ruin this in practice. Without diminishing marginal utility for consecutive cards sharing the same tags, packed itineraries will feel exhausting.

* Onboarding Friction: Asking 6 static swipes and 5 "this-or-day" comparisons is heavy for a casual consumer app. Transitioning to an adaptive question selection mechanism (using Expected Information Gain) would extract maximum data in half the steps.

* Why RUM is the Right Choice: Do not switch to collaborative filtering (which suffers from catastrophic cold-start problems) or contextual bandits (which are notoriously difficult to explain transparently). RUM parameters map directly to human-readable explanations ("You dislike crowds, so we avoided this"), which is a massive competitive advantage for ODYS.

Recommendations for a Solo Founder (7.5 Hours/Week)
Given your severe time constraints, focus your engineering effort on high-leverage fixes and avoid building premature complexity:

1. Prune Unused Data: Delete the survey screens for company, morning/night person, activity level, and best hour until you have the bandwidth to map them into the utility function. Never collect data you aren't utilizing.

2. Adopt LLM Option (b): Keep decision-making strictly inside the RUM and OR-Tools engine. Use a lightweight LLM only for unstructured feature extraction (translating free-text like "it's raining, I'm exhausted" into feature adjustments) and for generating dynamic, non-repetitive explanations from the model's weights.

3. Cheap Fix for Satiation: To solve the fatigue problem without adding heavy parameters, add a simple penalty rule inside the OR-Tools cost matrix: if two consecutive stops share the same primary thematic tag (e.g., history/culture), apply a small penalty to force thematic variety.

Would you like to explore how to implement an adaptive question selection method to reduce onboarding friction while maximizing information gain?
