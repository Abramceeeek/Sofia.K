# Hidden-preference bench: old engine `ecba269` against new `5af215a`

**Travellers 4–7: fresh travellers the thresholds never saw.** This is the independent check. The new engine's label `5af215a` is a documents-only commit: its Brain is identical to `417594a` (`git diff 417594a 5af215a -- brain/src brain/data` is empty).

**Synthetic travellers only, never evidence about people.** 40 travellers (4 for each of 10 archetypes), each with a hidden taste from `scripts/hidden_truth.py` (it imports nothing from the Brain), answering onboarding through the app's API with noise and gaps. Measured on the places each one never swiped, with hard rules (a closed day, an age rule) left out. Friday 2026-12-04. Raw results: the two `.json.gz` files beside this one.

| Measure | Random | Population only | Old engine | New engine | Better is |
|---|---|---|---|---|---|
| Rank correlation with the hidden truth (mean Spearman) | -0.02 | 0.22 | 0.25 | 0.23 | higher |
| Top-10 precision (share in the traveller's true top quarter) | 0.26 | 0.34 | 0.35 | 0.33 | higher |
| Mean top-10 overlap between two travellers | 0.14 | 1.00 | 0.31 | 0.35 | relevance, not difference |
| Overlap tracks hidden similarity (correlation) | -0.03 | – | 0.17 | 0.18 | higher |
| Poor matches truly below the traveller's median | – | – | 0.58 | 0.55 | higher |
| Poor matches truly in their top quarter (wrongly called poor) | – | – | 0.20 | 0.21 | lower |
| Low-confidence places truly in their top quarter (base rate 0.25) | – | – | 0.04 | 0.19 | near 0.25: unknown, not bad |
| Travellers with a place they didn't enjoy in their top 10 recommended | – | – | 0 | 0 | 0 |

**Honest uncertainty:** the gap between the engine's standardised score and the truth, by its own confidence level (lower is closer). If confidence means something, low should show the largest gap.

| Confidence | Old: gap (n) | New: gap (n) |
|---|---|---|
| low | 0.96 (58) | 0.94 (666) |
| medium | 0.93 (597) | 0.97 (1957) |
| high | 0.97 (1982) | – (0) |

**By archetype (mean Spearman):**

| Archetype | Population | Old | New |
|---|---|---|---|
| food | -0.21 | 0.05 | 0.02 |
| quiet | 0.36 | 0.28 | 0.21 |
| history | 0.42 | 0.50 | 0.51 |
| kids | 0.03 | 0.09 | 0.11 |
| budget | 0.55 | 0.32 | 0.32 |
| art | 0.38 | 0.40 | 0.40 |
| views | 0.42 | 0.51 | 0.52 |
| shopper | 0.11 | 0.05 | 0.05 |
| night | -0.04 | 0.06 | -0.04 |
| science | 0.18 | 0.23 | 0.23 |

**Classes over every judgement:**

| Class | Old | New |
|---|---|---|
| must_go | 0 | 0 |
| strong_match | 161 | 73 |
| good_discovery | 1123 | 964 |
| low_confidence | 58 | 667 |
| poor_match | 1282 | 1158 |
| not_suitable | 336 | 98 |

**What this can and can't show:**
- The truth is Claude's own construction (kinds and words to hidden attributes, GUESS weights). It's independent of the engine's code, not of Claude's judgement; a real traveller is the only real test.
- The engine sees only a handful of noisy answers; the place-by-place part of the truth (sd 0.5) is unrecoverable by design, so no engine should reach 1.
- Hidden tastes the person model has no feature for (art, science, shopping, nightlife, architecture) can be recovered only through places they loved or disliked.
