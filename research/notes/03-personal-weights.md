# Area 3 — Personal weights (the βs)

**Decision:**
- **Model:** estimate βs with one **hierarchical Bayesian model in PyMC** that has three likelihood blocks, all loading on the same person-level β_n with source-specific scale:
  - a mixed logit on the 10 "this or that" choices;
  - an ordered logit on the swipe reactions;
  - later, an ordered logit on the per-stop 1–5 ratings.
- **Upper level:** population mean plus covariates (travel style, morning/night), which makes "start at the mean of similar users" literal.
- **Refits:** following D7, refit the full model **offline**. A new user gets their βs from a fast per-user posterior (Laplace approximation) with the population hyperparameters held fixed.
- **Test A design:** a fixed Bayesian D-efficient 10-task design generated once, not an adaptive one. Keep to **5–6 attributes with 2–3 levels**.
- **Cost:** about **2 h in Phase 3** (design) and **6 h in Phase 4**: per-user posterior and scoring 4, offline HB refit 2.

## What exists (ranked)

| # | Name | Maturity | Licence | Why it matters |
|---|---|---|---|---|
| 1 | Train, [*Discrete Choice Methods with Simulation*](https://eml.berkeley.edu/books/choice2.html), 2nd ed. 2009 | Standard text, free PDF | Free online | Ch. 6 mixed logit, §7.2 combining stated and revealed preference, §7.4 ordered logit, ch. 11 individual-level parameters, ch. 12 HB |
| 2 | [PyMC](https://github.com/pymc-devs/pymc) 6.3.2 | ★9.8k, last commit 2026-09-13, **Py ≥3.12** | Apache-2.0 | Full control over a hierarchical multinomial + ordered logit. The official "Discrete choice and random utility models" example includes person-level coefficients |
| 3 | [Biogeme](https://github.com/michelbierlaire/biogeme) 3.3.5 | ★135, 2026-09-03, **Py ≥3.12** | MIT | The choice-modelling reference. Maximum-likelihood mixtures via Monte Carlo (on JAX since 3.3.1), **Bayesian estimation through PyMC since 3.3.2**, hybrid choice models. Use it to cross-check our PyMC model |
| 4 | [idefix](https://github.com/traets/idefix) (R) | CRAN 1.1.0 (2025-03-13); GitHub ★25, last commit 2022 | GPL-3 | Generates Bayesian D-efficient designs and individually adapted sequential Bayesian designs. Used offline to create the design only, so GPL doesn't reach our code |
| 5 | Sawtooth CBC guidance | Industry standard | — | At least 6 tasks for HB share predictions; about **10+ for robust individual-level predictions**; 8–15 typical |
| 6 | Adaptive designs: polyhedral (Toubia et al. 2004), individually adapted sequential Bayesian (Yu et al. 2011), ellipsoidal (Sauré & Vielma 2019) | Research, with code | — | Choose each person's next question from their earlier answers. See the trade-off below |
| 7 | [xlogit](https://github.com/arteagac/xlogit) | ★68, last commit 2024-01-02 (**stale**) | GPL-3.0 on GitHub (PyPI says MIT) | GPU mixed logit. Skip: stale, and the licence is ambiguous |
| 8 | Huber & Train 2001 | Classic result | — | Classical (maximum simulated likelihood) and HB give virtually the same individual estimates, so the method choice is about tooling, not results |

## What the evidence says

- **What 10 choices actually buy.** In Train's Monte Carlo (Table 11.1: 3 alternatives, two N(1,1) random coefficients, 300 people), the mean absolute error of each person's conditional-mean β against their true β is:

  | Choices observed | Mean \|β̄ₙ − βₙ\| |
  |---|---|
  | 0 | 0.80 |
  | 1 | 0.72 |
  | 10 | **0.42–0.45** |
  | 20 | 0.35 |
  | 50 | 0.24 |

  So ten choices roughly **halve** the error compared with knowing only the population, and returns diminish after that. Our case is harder: binary choices and 5–6 random coefficients carry less information per β, so **expect worse than 0.43 at T=10**. Early βs are shrunken guesses. Swipes and per-stop ratings do the rest.
- **Industry rule of thumb agrees.** Sawtooth recommends at least 6 tasks for HB, and about 10 or more for robust individual-level prediction.
- **More tasks may be affordable.** With 5, 9 or 17 choice sets (N=1,053), response rates and self-rated certainty did not differ (Bech et al. 2011). If Test A shows people enjoy the "this or that" layer, 12–15 tasks is an option.
- **Adaptive designs have a cost.** Individually adapted sequential Bayesian designs beat static designs on individual-level part-worths, especially when preferences are very heterogeneous, and they stay robust when answers are noisy (Yu, Goos & Vandebroek 2011). But for *population* parameters an optimal adaptive design (Sauré & Vielma's ellipsoidal method) did **uniformly worse than random questions** (Gibbard & Sadlier 2025). We need both levels: the population prior is what makes short onboarding work. So use a static efficient design now and revisit adaptivity once there are real users.
- **Combining data sources is textbook.** Stated and revealed preference share taste parameters but differ in scale (the variance of unobserved utility) and constants. Estimate separate scale parameters (Train §7.2). Ratings are ordered logit: one utility with estimated thresholds (Train §7.4). Our three sources map directly: conjoint choices are stated preference, swipe reactions are past experience, per-stop ratings are experienced utility.
- **HB vs classical doesn't change the answer** (Huber & Train 2001). What HB adds is honest per-person uncertainty, which we need to avoid over-claiming (see Risks).

## Gaps we'd have to fill ourselves

- **Conjoint design (~2 h, Phase 3).**
  - Choose 5–6 attributes, for example transfer time (15/30/50 min), one hot hour (yes/no), pace (3 vs 5 stops), crowds (low/high), cost (£20/£40/£60) and walking (low/high).
  - Set realistic London levels, and generate one 10-task D-efficient design with weak priors.
- **Thresholds and interactions.** Thresholds (15 vs 50 min) use a piecewise or dummy coding. Interactions such as heat × walking can't be identified per person from 10 choices, so estimate them at population level only.
- **LLM evidence records from Area 1.** Treat them as a fourth, weak ordinal data source with its own scale parameter, or leave them out of the likelihood and use them only to choose follow-up questions. This is a design decision to test.
- **Per-user posterior code.** A Laplace approximation around the MAP with fixed hyperparameters, so there is no MCMC at sign-up.

## Risks / unknowns

- **Over-claiming precision.** Telling someone "you hate crowds" off 10 binary choices will sometimes be wrong. Only name a weight in explanations when the posterior is confident, for example P(β<0) > 0.8. Otherwise use the persona label.
- **Hypothetical bias.** Stated choices ≠ experienced enjoyment (Area 2, Hofschen et al.). Per-stop ratings should dominate as they accumulate, and the source-specific scale partly absorbs the gap.
- **A thin population prior at first.** With 12–20 Test A participants the hyperparameters are poorly identified, so use weakly informative priors and expect them to move.
- **Python version.** PyMC 6 and Biogeme 3.3 need **Python ≥3.12**, so pin the prototype to 3.12.
- **Offline refits need convergence checks** (R-hat, effective sample size). Budget review time for them.
