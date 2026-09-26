# Area 11 — Companion matching (light scan)

**Decision:**
- **Out of v0.** The weekend test runs in existing groups. Log who turns up, who drops out, and why: that becomes the first training data.
- **Later, the method is a reciprocal recommender:** both people must be predicted to enjoy the trip *and* each other. Group plans use **average-without-misery**: maximise average predicted satisfaction, but exclude any plan where one member falls below a threshold.
- **No filters on protected characteristics.** In particular, **no age filters on day trips** (see below).
- **Cost: about 10–15 hours later.**

## What exists

| Name | Maturity | Why it matters |
|---|---|---|
| Reciprocal recommender survey (Palomares, Porcel, Pizzato, Guy & Herrera-Viedma, *Information Fusion* 69, 2021) | Research | People-to-people recommendation, where success needs *both* sides to accept. Covers dating, jobs and social matching |
| Group aggregation strategies (Masthoff) | Research | Average, least misery, average-without-misery. The best choice depends on how spread out the group's preferences are |
| WeRoad / Flash Pack / Timeleft (Area 7) | Commercial | Matching by age band (Flash Pack 30–49 / 50–65), shared interest (WeRoad) or quiz (Timeleft), with **human coordinators** doing the group dynamics |

## What the evidence says

- **The Equality Act's age exception is narrow.**
  - Age discrimination in services is unlawful unless an exception applies.
  - The "age-related holidays" exception (Sch 3 para 30B) requires all of these:
    - two of travel, accommodation or activities sold together for a single price;
    - **more than 24 hours or an overnight stay**;
    - the service is offered only to that age group, and bringing that age group together is an essential feature;
    - a written statement given to the customer beforehand.
  - **Age-banded day trips don't fit it.** Flash Pack-style overnight trips can.
- **Nationality is part of the protected characteristic of race** (Equality Act s.9: "Race includes colour; nationality; ethnic or national origins"). This confirms `CLAUDE.md`'s rule.
- **Commitment raises turnout.** Paid events have lower no-show rates (Area 10), so compatible matching plus a commitment device is the lever for "strangers turn up".

## Gaps / risks

- **Trust and safety is the dominant risk** for meeting strangers: identity checks, reporting and blocking. It triggers Online Safety Act duties once users can contact each other (Area 12).
- **Indirect discrimination.** Matching on innocent-looking features can proxy for protected characteristics, so audit match outcomes.
- **This is not legal advice.** Confirm the age-exception reading with a lawyer before any age-based product.
