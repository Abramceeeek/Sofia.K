# Area 15 — Travel motivation and per-trip intent (light scan)

**Decision:**
- **Layer 1, "why they travel":** measure 3–4 motives once at onboarding, from the open story plus a few one-tap items: escape/relaxation, relationships, self-development/novelty, nature/culture. Use them as **covariates on the population prior**: β_person ~ N(Γ·z_person, Σ). A new user then starts nearer people with similar motives, with no extra per-person parameters.
- **Layer 2, per-trip intent:** β_trip = β_person + Δ·z_trip.
  - z_trip = answers to 2–3 generated questions per trip (e.g. "recharge or explore?", "who's coming?", "one must-do?").
  - **Δ is shared across users** and estimated from ratings. It is *not* a free random effect per trip.
- **The LLM writes the questions from a fixed menu of intent dimensions,** so every answer maps to z_trip. Only the wording and destination detail vary.
- **Cost:** store the intent answers with each plan from v0 (~1 h inside Phase 4); estimate Δ once ratings accumulate (~4–6 h after Phase 3).

## What exists

| Name | Maturity | Why it matters |
|---|---|---|
| Push/pull framework (Dann 1977; Crompton 1979; Uysal & Jurowski 1994) | Classic theory | Push = motives inside the traveller. Pull = what the destination offers |
| Crompton 1979 | Qualitative study | **Seven socio-psychological (push) motives**: escape, self-exploration, relaxation, prestige, regression, kinship, social interaction. **Two cultural (pull) motives**: novelty and education. Push motives were unrelated to destination attributes (search) |
| Travel career pattern (Pearce & Lee 2005, *J Travel Research*) | Interviews + survey | A **core shared by all travellers**: escape, relaxation, relationship enhancement, self-development. Experienced travellers weight host-site involvement and nature more; less experienced ones weight stimulation, security, nostalgia, romance and recognition more |
| Context-aware recommenders (Adomavicius & Tuzhilin, *Recommender Systems Handbook*) | Established | Trip intent is "context". Contextual *modelling* (context as features) fits our utility model |

## What the evidence says

- **Motives differ by experience, but a core is common** (Pearce & Lee). So the population prior should carry motive covariates, and "travel experience" (trips a year) is a cheap one to ask.
- **Separating per-trip from per-person variation is hard.** Hess & Train (2011, working paper, read) ran over 16,000 simulated estimations. Variation across people was recovered even by simple methods, given enough data. But when tastes also vary across choice situations, "only the most computationally intensive approach" separated the two, and data needs were "more substantial than is commonly assumed".
- → **Model the trip effect as observed intent × shared Δ**, not as a latent per-trip random coefficient.

## Gaps / risks

- **Keep it about trips, not personality.** "Why do you travel?" items must read as trip wellbeing, not psychological assessment (`CLAUDE.md`).
- **Generated questions drift.** An LLM can invent dimensions, so constrain it to the menu and validate the output schema.
- **Δ needs ratings under varied intents.** Until then, set Δ = 0 and use intent only for hard constraints ("must-do" stops).
