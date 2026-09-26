# Area 6 — Wellbeing science → model variables

**Decision:** v0 uses three sourced numerical inputs and four moment tags, and **no psychometric scales in the app** (`CLAUDE.md` guardrail).
- **Numerical inputs:**
  - UTCI heat/cold bands (planner penalty);
  - DfT walk/wait/transfer weights (prior for transfer penalties);
  - one trip-framed question on recovery need.
- **Moment tags:** contrast/reveal, awe, absorption, green/nature.
- **Planner objective:** the **sum of predicted moment satisfaction**. The end-bonus toggle (D8) stays **off by default** until our own ratings show an end effect. The evidence for peak–end in complex, multi-part experiences is weak.
- **Cost: about 0.5 extra hours.** The UTCI calculation already sits inside Area 4's weather step.

## Candidate variables

| Variable | Evidence | How to measure in the app | Threshold / prior | v0? |
|---|---|---|---|---|
| **Heat/cold stress (UTCI)** | UTCI bands (Bröde et al. 2012): 9–26 °C no thermal stress, 26–32 moderate heat, 32–38 strong, 38–46 very strong, >46 extreme | Hourly UTCI from forecast temperature, humidity, wind and radiation via [pythermalcomfort](https://github.com/CenterForTheBuiltEnvironment/pythermalcomfort) (MIT, ★231, 2026-09-17, Py ≥3.10) | No penalty 9–26; linear penalty 26–32; steep 32–38; no outdoor moments above 38. Cold penalty below 9 for outdoor moments. Tolerance is context-dependent (one beach study: 62% wanted no change even at UTCI 39) | **Yes** |
| **Walk / wait / transfer time** | DfT TAG M3.2 Table 1: walk 1.5–2.0× in-vehicle time; wait 1.5–2.5×; 2–10 min penalty per transfer | Generalised minutes from TfL and OSRM legs | Prior: walk ×1.75, wait ×2, 5 min per transfer. Abram's "15 fine, 50 ruins it" becomes a piecewise penalty whose βs are learned | **Yes** |
| **Peak vs average vs end** | In 49 students' ~7-day holidays, peak–end was "not an outstandingly good predictor" (Kemp et al. 2008). For heterogeneous experiences, averages beat peak and end (Strijbosch et al. 2019). Peaks and ends predicted recall at 3 weeks but not 7 (Geng et al. 2013, **UNVERIFIED**, seen as cited) | One-tap per-moment rating, an end-of-day rating, and a 1-week recall rating | Default objective = sum. The end bonus is a toggle to test by regressing day rating and recall on mean, max and last | Toggle, off |
| **Recovery need** (detachment, relaxation, mastery, control) | REQ: 16 items, α .82–.89 (Sonnentag & Fritz 2007). A 5th "contrast" factor was proposed in 2025 (Almén et al., N=812) | **Don't administer the REQ.** Ask trip-framed: "On a day off, do you want to switch off, learn something, or push yourself?" Tag moments relaxing vs mastery | Person-level covariate in the Area 3 upper level | **Yes** (1 question) |
| **Restoration / nature** | Attention restoration theory: in 42 studies, attentional control, working memory and cognitive flexibility responded most to nature (Stevenson et al. 2018) | Moment tag `green_nature` (0–2) | No dose threshold found | **Yes** (tag) |
| **Mystery / reveal (contrast)** | Mystery was the only significant informational predictor, among 20 that together explained 83% of preference variance across 59 scenes (Kaplan, Kaplan & Brown 1989). But across studies its correlation ranges from −0.45 to +0.95 (Stamps 2004 meta-analysis, 28 articles). Narrowing space → arousing and unpleasant; open → pleasant (Presti et al. 2022, VR) | Moment tag `contrast_reveal` (0–2); legibility = how easy the approach is to follow | None. Learn β; the **release-after-compression** bonus is untested | **Yes** (tag) |
| **Awe** | Vastness + need for accommodation (Keltner & Haidt 2003). AWE-S: 30 items, 6 factors, α ≥ .80 (Yaden et al. 2019). Weekly 15-minute "awe walks" for 8 weeks raised joy and lowered distress vs ordinary walks (N=60 older adults; Sturm et al. 2022) | Moment tag `awe` (0–2). Optional one-tap "Did anything take your breath away?" | None | **Yes** (tag) |
| **Absorption / flow** | Challenge–skill balance is moderately related to flow and is a robust antecedent (Fong et al. 2015, 28 studies). The Flow Short Scale has 10 items on fluency and absorption (Rheinberg et al. 2003) | Moment tag `absorption` (0–2) plus the skill it needs; activity level from onboarding | Match the moment's challenge to stated skill | **Yes** (tag) |
| **Anticipation** | Vacationers were happier *before* the trip than non-vacationers, with no difference after unless "very relaxed" (N=1,530; Nawijn et al. 2010). Anticipation is more intense than retrospection (Van Boven & Ashworth 2007, 5 experiments) | Days between plan delivery and the trip; whether previews are opened | Deliver plans days ahead; optimal lead time unknown | Test C |
| **Fade-out** | Vacation d=+0.43, fading d=−0.38 within 2–4 weeks of return (de Bloom et al. 2009 meta-analysis, 7 studies) | Days since last trip | Nudge cadence of 2–4 weeks | Later |
| **Memorability dimensions** | MTES: 24 items, 7 domains (hedonism, refreshment, local culture, meaningfulness, knowledge, involvement, novelty) (Kim, Ritchie & McCormick 2012) | Cross-check that the tag set covers them | — | Schema check |

## What the evidence says

- **Peak–end is the weakest link in `CLAUDE.md`.** It holds for simple experiences, but for holidays and multi-part episodes the average predicts memory as well or better. So measure it rather than build around it.
- **Contrast/reveal is real at the level of arousal**: narrow, enclosed spaces are measurably unpleasant and arousing. But mystery's effect on *preference* is not reproducible across studies. It fits as a **learned, person-specific β**, which matches the app's premise that people differ.
- **Awe and flow have validated measures and field evidence.** The awe-walk result (15 minutes a week, attention directed to vastness) is the closest analogue to "a moment".
- **The UK already has standard weights for how much walking, waiting and changing hurt** (DfT TAG). They are calibrated on routine travel, so treat them as a prior for leisure.

## Gaps we'd have to fill ourselves

- **Leisure-specific thresholds.** TAG weights and UTCI comfort bands come from commuting and general populations.
- **Whether a "reveal" adds utility beyond its parts.** The test is β on `contrast_reveal` in per-moment ratings, with the rating fired at the end of the approach.
- **A dose–response for nature or awe** per moment length.

## Risks / unknowns

- **Guardrail drift.** Using REQ or AWE-S items verbatim would make the app feel like a psychological assessment. Keep questions trip-framed.
- **Rating timing biases results.** A rating on exit captures the end, not the peak. Log the timestamp and position in the day.
- **Small n.** With 12–20 Test A participants, none of these βs will be precise. Treat Phase 3 as checking direction, not size.
