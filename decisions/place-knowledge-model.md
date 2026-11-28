# The place knowledge model (revised 28 Nov 2026, batch 9; m364)

**Abram's aim:** "teach ODYS how to understand any city", not only to know London. This model is the reusable structure. The seven reference places in `brain/data/places/` are its first records, built to it, not instead of it.

## Decision first

- **ODYS matches people to experiences, not to places.**
  - A place holds one or more experiences, and each has its own activities, appeals, atmosphere, duration and limits.
  - The Natural History Museum's dinosaur gallery, its building and its family activities are three experiences, each appealing to different people.
  - A place-wide fact (opening hours, access) belongs to the place, and its experiences inherit it.
- **Four judgements are kept apart, always:**

  | Judgement | Question | Rests on |
  |---|---|---|
  | **Eligibility** | Can this traveller do it at all, then? | **Verified** facts only (hours, dates, age, access, a current explicit exclusion) |
  | **Suitability** | Is it a good match for them? | Their evidence against the experience's appeals and cautions |
  | **Confidence** | How sure is ODYS of that suitability? | How much evidence exists on both sides, how good it is, and whether it conflicts |
  | **Evidence quality** | How reliable are the place facts themselves? | Status and freshness (`evidence-rules.md`) |

  An excellent potential match can be low confidence, and a well-documented place can be a poor match.
- **The vocabulary, the 0–2 rubric and primary versus secondary appeals** are in `place-vocabulary.md`.
- **The evidence rules** (verified, researched, inferred, unknown; facts versus interpretations; expiry; missing is not negative) are in `evidence-rules.md`.
- **The structure and the standard come first, then the data.** The schema and its validation are code (`brain/src/brain/experiences.py`). Every record passes the same checks, so a London card and a future Lisbon card are judged alike.

## 1. The record

```
Place
  id, name, location, area, official_url, kind (museum, market, park, gallery, tower, shop…)
  facts: [Claim]                    opening hours, dated closures, access, price, booking, age rules
  experiences: [Experience]
  legacy_card: the moment card id(s) the planner uses today

Experience                          (what a visitor does: its own appeals)
  id, title, what_you_do, activity (look | walk | eat | ride | learn | play | shop | rest | climb)
  scores: {dimension: 0 | 1 | 2 | unknown}      each with the claims behind it (place-vocabulary.md §1-3)
  primary: [≤ 2 dimensions]                     organised around it, strongly evidenced
  secondary: [dimensions]
  atmosphere: {term: {value, window?}}          by time window where evidence gives one
  cautions: [Claim]                             what may not suit someone, from evidence, never a stereotype
  duration, price, effort, age, booking         where they differ from the place's
  claims: [Claim]

Claim                               (evidence-rules.md §1)
  claim, applies_to, kind (fact | interpretation), status (verified | researched | inferred | unknown),
  source, source_type, checked, confidence, expires
```

**The legacy tags are derived, not replaced.** Each place's 15 tags for the planner are worked out from its experiences: the main experience's scores, with unknown read as 0 *for the planner only*. The derived tags are compared with today's card tags (`scripts/place_knowledge_report.py`), and the planner keeps today's tags until Abram approves the switch. Nothing in a plan changes because a record improves.

## 2. Inferred information

Abram (m364): inferred facts may support partial appeals and provisional ranking, but are never shown as verified, and never justify a strong claim on their own.
- **Verified:** an identifiable source states it.
- **Researched:** ODYS read a cited source and assessed it.
- **Inferred:** a reasonable interpretation.
- **Unknown:** not established.

The engine reads the status of every claim. An inferred appeal counts at half weight in ranking, and never in a reason. An unknown dimension counts as missing evidence: lower certainty, never lower suitability.

## 3. The 74 curated places first; Overture assessed in parallel

1. **The structure and standard:** this document, the vocabulary, the evidence rules and the schema code.
2. **Seven reference places,** researched from official pages: Tate Modern, Borough Market, the Natural History Museum, the British Museum, Hyde Park, the Sky Garden and Liberty.
3. **A second, independent scoring** of a sample, to show where the rubric is read inconsistently, and the rubric corrected where it is.
4. **The other 67 curated places,** to the same standard (about 8–10 h; GUESS, after step 3 shows how long one takes).
5. **The Overture sample** (`validation/place-knowledge/overture-sample.md`), measured on separate axes:
   - existence;
   - category accuracy;
   - coordinate accuracy;
   - duplicates and ambiguity;
   - website availability (a metric, not a requirement: parks and landmarks often have none);
   - enrichment potential;
   - licence and attribution.
6. **A controlled enrichment process** from raw records to places, never a bulk import into planning.

## 4. What the engine does with this

- **It matches each experience** where a place has experience records, and the place as one experience where it has only its card.
- **Eligibility uses verified facts only.** A missing fact is said, never assumed in either direction.
- **Suitability uses** the traveller's evidence against each experience's primary and secondary appeals, and their cautions.
- **Confidence comes down with:**
  - unknown or inferred appeals;
  - conflicting evidence;
  - a score that rests on the population's defaults;
  - a traveller who has said little about this experience's primary appeals.

## 5. Questions answered (Abram, m364)

- The atmosphere vocabulary is structured into groups, with terms as separate dimensions (`place-vocabulary.md` §2).
- Inferred facts support partial appeals for provisional ranking only.
- The 74 curated places come first, with Overture assessed separately in parallel.

## 6. When a new dimension enters the person model

A dimension (for example `art`) becomes a feature of the person model only when at least 80% of ready places record it, as a score or explicitly as unknown. Its prior is the population's (0), and the engine bench is run before and after. Until then, it is used only by the match engine's evidence and confidence.
