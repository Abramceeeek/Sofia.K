# Area 12 — Legal and ethics (light scan; not legal advice)

**Decision:** v0 needs three things that fit inside the existing hour estimates: a plain-English privacy notice and consent form (Phase 3, about 2 hours), audio deletion (D3), and a data-deletion command (Phase 4). Three design rules follow:
1. **Never analyse voice tone for emotion.** Extract preferences from the *transcript* only.
2. **Treat food allergies as health data**, and "halal" as possibly revealing religious belief. Make both optional, ask for explicit consent, and use them only to filter food.
3. **No user-to-user features in v0.** When trip posting or messaging arrives, do an Online Safety Act illegal-content risk assessment **within 3 months**.

## What exists (sources)

| Item | What it says | Why it matters |
|---|---|---|
| ICO: what is special category data | 9 categories, including racial or ethnic origin, **religious or philosophical beliefs**, **health**, and **biometric data "where used for identification purposes"**. Inferences count if the processing *intends* to infer, or the data clearly reveals a category | Voice recordings are personal data but are *not* special category unless used to identify someone (so no speaker ID). Allergies are health data. A halal preference may reveal religion |
| Equality Act 2010 s.4 and s.9 | 9 protected characteristics; race includes nationality | Confirms the guardrail against matching on nationality |
| Equality Act Sch 3 para 30B | Age-related holiday exception: over 24 hours or overnight, packaged, with a written statement | No age filters on day trips (Area 11) |
| Ofcom: Online Safety Act illegal content duties | **All in-scope services must do an illegal-content risk assessment, regardless of size**, within 3 months of launch and before significant changes. "Large" means more than 7 million UK monthly users | Applies once users can post trips or contact each other |
| EU AI Act Article 50 (applies from **2 Aug 2026**) | Systems that interact directly with people must tell them it is AI. Deployers of **emotion-recognition systems** (inferring emotions from biometric data) must inform the people exposed | Relevant for any EU users. It matches the `CLAUDE.md` rule to disclose AI hosts, and it is another reason not to infer emotion from voice |

## What the evidence says

- **Most of the design is already compliant by construction.** It asks for budget, not income; food needs, not nationality; and it discloses AI hosts (`CLAUDE.md`).
- **Two new catches came out of this scan:**
  1. The food-needs question collects special category data (allergies are health; halal may be religious belief).
  2. Inferring feelings from *voice* rather than text would push the app towards "emotion recognition" under the EU AI Act.

## Gaps / risks

- **A DPIA** is likely needed before collecting health or other special category data at scale. About 3 hours, before v0 launch.
- **UK-specific AI disclosure rules were not checked in this scan.** Verify before launch.
- **Everything here needs professional legal review** before charging users or incorporating, alongside the founder's existing legal gates.
