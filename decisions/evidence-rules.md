# Evidence and verification rules for place knowledge (28 Nov 2026, batch 9; m364)

**Decision first.** Every meaningful claim about a place or experience is stored as a claim with its own evidence.
- **Missing information is never negative information.**
- **Only verified facts drive hard rules.**
- **A strong reason shown to a traveller needs verified or researched evidence about the place,** as well as clear evidence about the traveller.
- **An inference may help ranking provisionally,** but it is never shown as a fact and never makes a strong claim alone.

## 1. What every claim records

| Field | Meaning |
|---|---|
| `claim` | what is said, e.g. "the free collection is modern and contemporary art" |
| `applies_to` | the place, or one experience in it |
| `kind` | **fact** (checkable: hours, price, contents, rules) or **interpretation** (subjective: peaceful, grand, romantic) |
| `status` | **verified**, **researched**, **inferred** or **unknown** (§2) |
| `source` | URL or file, with the quote where there is one |
| `source_type` | official, reference (e.g. a museum's own collection page), map data, crowd label (Overture or OSM), ODYS's own reading |
| `checked` | date |
| `confidence` | high, medium or low (§2) |
| `expires` | when it must be checked again (§4) |

## 2. Status, and what each may support

| Status | Means | Hard rule (closure, age, step-free) | A primary appeal | A strong reason shown to the traveller | Provisional ranking |
|---|---|---|---|---|---|
| **verified** | an identifiable source states the fact directly | ✔ | ✔ | ✔ | ✔ |
| **researched** | ODYS assessed it from a cited source: a fair reading, not a direct statement | ✗ (needs verified) | ✔ | ✔ | ✔ |
| **inferred** | a reasonable interpretation with no source that states it | ✗ | ✗ | ✗ | ✔, as a partial appeal only |
| **unknown** | no source read on it | ✗ | ✗ | ✗ | **Lowers certainty, never suitability** |

**Confidence:**
- **high:** verified, fresh, and factual.
- **medium:** researched; or verified but near its expiry.
- **low:** inferred, a crowd label, or stale.

## 3. Facts and interpretations

- **An official page verifies facts, not experiences.** For example, Tate's page verifies that Tate Modern's free collection is modern and contemporary art. It doesn't verify that visitors find it inspiring.
- **Marketing words are not evidence of the feeling they name** ("spectacular", "breathtaking", "unmissable"). At most they support a **researched** interpretation that the place *presents itself* that way. They never support `awe`, `grand` or `romantic` as verified.
- **Interpretations** (peaceful, romantic, grand, immersive) are researched at best. Real ratings are what will eventually show whether visitors feel them (the evaluation's job).
- **A crowd label** (an Overture category, an OSM tag, "halal") is a source of type crowd label, **inferred at best**, until a verified source confirms it. It never supports a dietary or access rule (D19, D123).

## 4. When evidence expires

| Fact | Check again after |
|---|---|
| Opening hours; dated closures and events | 90 days, and before any date the source marks as changing (holidays) |
| Prices | 180 days |
| Access (step-free, lifts) | 365 days |
| Booking rules, age rules | 180 days |
| What the experience is (collection, gallery, garden) | 365 days, or when the place announces a change |
| Interpretations (peaceful, grand) | 365 days, or sooner when real ratings disagree |

An expired verified fact becomes **medium** confidence until checked. It is never silently treated as still verified. These match `quality.py`'s `STALE_DAYS` (180) for prices and are stricter for hours.

## 5. Missing is not negative: what the engine does with each case

| The traveller | The place | The engine says |
|---|---|---|
| Likes history (clear evidence) | History is verified or researched at 2 | **Positive evidence:** may be a strong reason |
| Dislikes crowds (clear evidence) | Crowding is verified or researched at 2 | **Negative evidence:** a reason it may not suit |
| Likes history | History is **unknown** for this experience | **Missing evidence:** lower certainty, and ODYS says it doesn't know yet. **Never a poor match for that reason** |
| Likes food, dislikes crowds | Food 2 and crowded 2, both evidenced | **Conflicting evidence:** low confidence, with both sides said |
| No evidence either way | anything | **Low confidence:** the population's view only |
