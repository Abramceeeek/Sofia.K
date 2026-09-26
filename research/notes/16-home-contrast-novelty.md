# Area 16 — Home-contrast novelty (light scan)

**Decision:**
- **Novelty = distance between a moment's environment and the user's home environment.** Each is a vector of open-data features within ~500 m: building density and height, green share, water, street width, topography.
- **"Home" is what the user states:** home city, or the type of place they grew up in (big city / town / coast / countryside). **Never nationality, and never inferred.**
- **The effect is person-specific and nonlinear.** Some people seek strangeness, others want the familiar. Model a quadratic or spline in novelty with a person-specific weight.
- **Use it only to score places for that user.** Never for matching or filtering people, and never shown to others.
- **Cost: ~4–6 h after Phase 3,** to compute vectors for ~50 moments and ~20 home types.

## What exists

| Name | Maturity | Why it matters |
|---|---|---|
| Novelty-seeking scale (Lee & Crompton 1992, *Annals of Tourism Research*) | 21-item scale | Four dimensions: thrill, change from routine, boredom alleviation, surprise. They separate people who want more or less novelty (search) |
| Familiarity–strangeness continuum (Cohen 1972) | Classic theory | Tourists seek novelty but many stay in an "environmental bubble" of the familiar. Four roles from organised mass tourist to drifter (search) |
| Berlyne 1970, *Perception & Psychophysics* | Lab experiments | Pleasingness and interest rose with novelty in his sequences. His two-factor account (positive habituation vs tedium) implies an **inverted U** in familiarity (search) |
| OSM / Overture buildings, land use, water | Production (ODbL) | Source of the environment vectors, and the same data as Area 14 |

## What the evidence says

- **People differ in how much novelty they want** (Lee & Crompton; Cohen). This supports a person-specific weight, not a global "novelty is good".
- **The shape is probably not linear** (Berlyne). This matches `CLAUDE.md`'s "thresholds, not lines". Test a quadratic against a linear term on ratings.
- **London first:** most early users live in London, so city-level contrast is near zero. That's why "where you grew up" (place type) carries the signal: someone from a coastal town may find the Thames Barrier strange, and a Londoner may not.

## Gaps / risks

- **Proxy discrimination.** Home city or where someone grew up can correlate with nationality or ethnic origin, which are protected under race (Equality Act s.9, Area 12). Rules:
  - optional question;
  - used only for that user's own place scores;
  - never for companion matching;
  - audit that plan quality doesn't differ systematically across home types.
- **Environment features are coarse.** Two very different cities can share density and green share. Start with 5–6 features and check face validity on the seed moments.
- **Double-counting.** Area 15's "novelty" motive and this feature overlap. Keep the motive as a prior on the novelty weight, not a second novelty term.
