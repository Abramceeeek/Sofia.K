# Group travel: a trip that works for everyone without one person taking it over (10 Nov 2026; m240)

**Decision (proposed): plan group trips by Nash welfare on each member's satisfaction, inside hard rules.** A prototype in the Brain; **no group accounts** (Abram, m234).

`brain/src/brain/group.py`, `brain/scripts/compare_group.py` (`benchmarks/synthetic/group.txt`), `brain/tests/test_group.py` (4 tests).

## The rules

**Per member:** their tastes (the same person model as everyone), a budget per day, must-sees and rejected places. Members are labelled "Member A", "Member B" and so on, **never named and never described**.

**Hard rules, never traded away:**
1. **A place anyone rejects is out.** One person's no is a no.
2. **The cost per person fits the smallest budget,** for the trip and day by day, so nobody is priced out. A must-see that doesn't fit is **left for the group to decide, and said**, never forced in.
3. **Each member's first must-see is in,** where the days and budget allow; further must-sees take turns.

**Choosing the rest: Nash welfare.** The plan maximises the sum of the logs of each member's satisfaction, their mean chance of "Good" or better over the plan.
- The log makes a gain matter most to whoever has least, so giving everything to one member costs the others more than it gains.
- **Satisfaction is a chance (0 to 1), not raw utility.** Raw utilities can't be compared between people: someone with strong tastes has big numbers. Summing them lets that person win, which is exactly the failure Abram named.

**The shared itinerary.** Each day's highlight takes turns: "Day 1 leads with Member A's pick…", then B, then C. The rest of each day is what the other members like most, so each day holds something for someone else.

## Fairness measured, not assumed

Sato, "Enumerating Fair Packages for Group Recommendations", WSDM '22 (arXiv 2105.14423, read 10 Nov 2026):
- **Proportionality:** "package P is m-proportional for user u if user u likes at least m items in package P". A member likes an item in their own top Δ% (Δ = 20%, a GUESS; m = 1).
- **Envy-freeness:** "user u is envy-free for item i if R_ui is ranked in the top-Δ% in {R_vi | v∈G}".
- **Why both satisfaction and fairness are reported:** the paper notes that maximising total preference "may be unfair to the minority people in the group", and that a group can be dissatisfied with a package "even if the score is high".

The group-recommender literature's "least misery" strategy (the best plan for the least happy member) is kept for comparison. Masthoff's chapters and papers on aggregation strategies **couldn't be read here** (403, 404 and a sign-in wall): **UNVERIFIED** beyond Sato's citations.

## The synthetic benchmark (`compare_group.py`, 200 groups of 3, London's 49 experiences, 2 days × 3 stops)

**Members as drawn from the prior:**

| Method | Least happy member | Gap, happiest to least happy | Everyone gets one of their own top-20% stops |
|---|---|---|---|
| Average (sum of raw utilities) | 0.529 | 0.363 | 85% |
| Least misery | **0.627** | **0.174** | 66% |
| **Nash** | 0.594 | 0.263 | 81% |

**With one member's tastes three times as strong** ("loud"):

| Method | Least happy member | Gap | Everyone gets a top-20% stop | **Share of stops from the loud member's top 20%** | …from each other member's |
|---|---|---|---|---|---|
| Average | 0.484 | 0.438 | 71% | **85%** | 40% |
| Least misery | **0.614** | **0.213** | 65% | 50% | 50% |
| **Nash** | 0.580 | 0.309 | **77%** | **57%** | 50% |

**What it says:**
- **A plain average lets the loudest member take the trip:** 85% of stops from their own favourites, against 40% for each of the others.
- **Nash cuts that to 57% against 50%,** and has the best chance that every member gets a favourite (77%).
- **Least misery** has the smallest gap, but leaves more people without a single favourite (65%): Sato's point that a "fair" plan can still be liked by no one.
- **Nash is the balance,** hence the proposal. It's Abram's call; least misery is one argument away.
- **Assumptions (all GUESSES):** synthetic people only, from the model's prior; groups of 3; Δ = 20%; satisfaction is the model's own predicted chance, not real ratings.

## Not built (after the round; GUESS hours)

| Step | Hours |
|---|---|
| Shared trip accounts and invitations (a privacy and safety design first: what each member sees of the others) | Design ~4 h, then ~20 h both apps; Abram's privacy review |
| Choosing the destination by the same rule (each member's fit per destination, `discovery.destinations`) | Claude ~2 h |
| Group budgets with split costs (never holding money: Stripe Connect direct charges only, CLAUDE.md) | After the money gates |

**Hours this step:** Claude ~3 h.
