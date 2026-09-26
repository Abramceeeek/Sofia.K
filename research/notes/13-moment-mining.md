# Area 13 — Moment mining from text, and data rights (light scan)

**Decision:**
- **Mine only open-licence text:** Wikivoyage (CC BY-SA 4.0) and Geograph photo titles and descriptions (CC BY-SA 2.0, from the bulk dumps).
- **Do not mine Reddit or Tripadvisor.** Their terms forbid it for a commercial product, and the UK text-mining exception covers only non-commercial research.
- **Mining finds candidates; the founder decides.** An LLM proposes candidate moments (place + approach + time + feature cues), each backed by a verbatim quote. The founder reviews and rewrites them in the Area 2 schema. Nothing mined goes to users unedited.
- **Cost: ~6 h pilot after Phase 3,** and about £1 of Batch API tokens for ~2,000 passages. Not in the v0 36 h.

## What exists

| # | Source | Licence / terms | Use? |
|---|---|---|---|
| 1 | Wikivoyage (London guides) | CC BY-SA 4.0: commercial use allowed with attribution; adaptations must carry the same licence | **Use.** Candidate discovery |
| 2 | Geograph (British Isles photo archive: titles and descriptions) | Submissions CC BY-SA 2.0. The API page says not to use the live site or API for bulk collection or model training; use the dumps. Credit the photographer and state the licence | **Use** the dumps. Descriptions often name the viewpoint ("looking north from…") |
| 3 | Wikimedia Commons | Licence varies by file; most need attribution; no permission needed within the licence | **Adapt.** Reference images for shot cards, checked per file |
| 4 | Reddit (Data API terms, revised 2026-07-20) | Commercial use needs a separate agreement. Using user content to train an ML/AI model needs the rightsholders' express permission. Delete data beyond the approved use | **Skip** |
| 5 | Tripadvisor (terms of use, effective 2025-07-15) | Forbids any robot, scraper or **AI system** accessing, copying or indexing content without written permission | **Skip** |
| 6 | UK CDPA s.29A (text and data analysis) | Only "for the sole purpose of research for a non-commercial purpose", with lawful access. Contract terms can't override it, but the copies can't then be used commercially | Covers a research pilot only, not the product |

## What the evidence says

- **LLMs can extract structured records from free text.** Dagdelen et al. (2024, *Nature Communications*) fine-tuned GPT-3 and Llama-2 to output JSON records of entities and relations from scientific paragraphs.
- **In tourism, LLMs extract aspect-opinion-sentiment tuples.** Xu et al. (2024, arXiv) report a +7.49% F1 gain on a tourism review dataset.
- **Neither paper extracts what we need.** Approach and timing cues ("as you come out of the tube…", "at dusk") are new, so precision has to be measured on our own sample.
- **The pattern to use**, which is the same as Area 1:
  - schema-constrained output;
  - **every field backed by a verbatim quote**, checked by exact string match;
  - records without a quote are rejected;
  - de-duplicate by Overture place ID;
  - audit precision on 50 random records.

## Gaps / risks

- **Share-alike reach.** Facts are not copyrightable, but CC BY-SA 4.0 also licenses database rights. Whether a moment database built from substantial extraction must be shared alike is **UNVERIFIED**, so a legal check is needed before scale. Meanwhile, keep a source link and attribution on every mined moment.
- **Old text.** Guides and photo captions go stale: closed entrances, changed routes. The founder's walk-through check stays the gate.
- **Selection bias.** Text over-represents famous places, which is the opposite of the product's aim. Weight the mining toward the approach and transition cues, not landmark names.
