# Benchmark design — moment feature tagging: Jev vs Claude (D29)

**Decision:**
- **Run it when the 50 v0 moments are tagged in Phase 4.** Abram labels them **blind** first, and those labels become the gold set.
- **Adopt a tagger only if its confidence predicts correctness** on held-out moments. Then auto-accept tags above a threshold chosen on a separate calibration half, and route the rest to Abram.
- **Founder cost ≈ +1.5 h on Phase 4:**
  - blind labelling (2.5 h) replaces reviewing LLM drafts (~2 h), so +0.5 h;
  - a 10-moment re-label a week later to measure Abram's own consistency: +0.5 h;
  - reading the results: +0.5 h.
- **Cash:** well under £10 (below).

## Set-up

| Item | Choice | Why |
|---|---|---|
| Items | 50 moments × 15 features (11 place attributes + 4 moment features), each 0/1/2 (Area 2): **750 labels** | Same features the planner uses |
| Input to every model | The moment card text only: place, approach, best time, a 2–3 sentence neutral description. No feature scores, no images | Jev is text-only (docs, fetched), so Claude gets text only too, for fairness |
| Gold | Abram's blind labels. 10 moments re-labelled a week later (test–retest) | The retest agreement is the ceiling for any model |
| Jev | `jev-1.13.0`, **pinned** (not `jev-latest`). One Score question per feature with the three levels described in words; all 15 questions in one call per moment | Score returns probabilities per level and a confidence |
| Claude | Haiku 4.5 and Opus 5, pinned IDs. Structured output: the level plus a probability for each level. **Plus self-consistency:** 5 samples, confidence = share agreeing with the mode | The Claude API gives no token probabilities, so we test both stated and sampled confidence |
| Split | 25 moments to calibrate the threshold, 25 to test. Split by moment, not by label; bootstrap CIs resampling moments (1,000 draws) | Labels within a moment are correlated |

## Metrics

1. **Accuracy:** exact-match rate, within-one rate, and quadratic-weighted κ vs Abram, per feature and macro-averaged. Compare with Abram's own retest κ.
2. **Calibration** (does stated confidence match hit rate?):
   - Expected Calibration Error (10 equal-count bins), multi-class Brier score, and a reliability diagram.
   - Use the probability of the chosen level.
   - For Jev, also use its `confidence`. The docs say this is *derived from* the probabilities: for a Choice it equals (n·p_max − 1)/(n − 1). It is not a separate correctness estimate.
3. **Discrimination** (does confidence predict correctness?): AUROC of confidence for correct vs wrong labels. **This is the core question.**
4. **Selective accuracy:**
   - A risk–coverage curve.
   - On the calibration half, pick the threshold τ where accuracy among auto-accepted labels ≥ **target** (Abram sets it; 90% proposed).
   - On the test half, report coverage (share auto-accepted), accuracy above τ, and Abram's review load in labels.

**Adoption rule** (test half, bootstrap 90% CI):
- accuracy above τ ≥ target;
- coverage ≥ 50%;
- AUROC ≥ 0.75.

If more than one model qualifies, pick the cheapest. If none does, keep LLM drafts plus full review (the current plan).

## Cost (cash)

- **Jev:** $0.042 per million input tokens, output free (models page, fetched). 50 calls × ~3k tokens costs a fraction of a cent.
- **Claude:** 50 moments × 5 samples × (~2k in + ~0.5k out). About $1 on Haiku 4.5 and about $6 on Opus 5 at list prices (`economics/unit-economics.xlsx` → PriceTables).

## Terms to clear before Jev sees any user data (checked 2026-09-26)

| Point | What the documents say | Status |
|---|---|---|
| Pricing stability | $0.042/Mtok input on the models page. A homepage FAQ asks "Are these prices temporary or subsidized?", but the answer isn't readable without JavaScript. Rate limits "can change without notice" | **UNVERIFIED**: ask sales before depending on it |
| Early access | Jev is in early access. The API may change incompatibly, with "commercially reasonable efforts" at advance notice (MCA 2.5) | Pin model versions; keep Claude as fallback |
| Training on our data | Privacy policy: won't train or fine-tune on Input. MCA 4.1: no Customer Data in training sets without consent; but a perpetual right to derive **telemetry** from Customer Data | Acceptable for moment text. Ask what telemetry includes before sending transcripts |
| Where data goes | Hosted in the US. DPA (updated 24 Apr 2026) includes the **UK Addendum** to the EU SCCs; subprocessors at trust.typesafe.ai | OK for a UK controller on paper; needs a transfer risk assessment |
| Retention | DPA: "as long as necessary"; no fixed period. Zero data retention for enterprise customers only | **Blocks transcripts** until ZDR or a fixed retention period is agreed |
| Website terms | US-oriented, with an arbitration clause; the site is "intended for visitors located within the United States" | The MCA governs API use; check governing law before signing |

**Consequence:** the benchmark (moment text, no personal data) can run under early-access terms. **Do not send user transcripts** (Area 1 extraction) to Jev until retention and telemetry are settled in writing.
