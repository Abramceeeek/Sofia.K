# Hidden-preference bench: old engine `ecba269` against new `5af215a`

**Travellers 0–3: the set the two confidence thresholds (`RATIO_LEARNED`, `RATIO_LITTLE`) were set on.** So the honest-uncertainty table below isn't independent of that choice; see the fresh travellers (`hidden-travellers-4-7.md`). The new engine's label `5af215a` is a documents-only commit: its Brain is identical to `417594a` (`git diff 417594a 5af215a -- brain/src brain/data` is empty).

**Synthetic travellers only, never evidence about people.** 40 travellers (4 for each of 10 archetypes), each with a hidden taste from `scripts/hidden_truth.py` (it imports nothing from the Brain), answering onboarding through the app's API with noise and gaps. Measured on the places each one never swiped, with hard rules (a closed day, an age rule) left out. Friday 2026-12-04. Raw results: the two `.json.gz` files beside this one.

| Measure | Random | Population only | Old engine | New engine | Better is |
|---|---|---|---|---|---|
| Rank correlation with the hidden truth (mean Spearman) | -0.00 | 0.19 | 0.22 | 0.20 | higher |
| Top-10 precision (share in the traveller's true top quarter) | 0.24 | 0.34 | 0.34 | 0.33 | higher |
| Mean top-10 overlap between two travellers | 0.15 | 1.00 | 0.34 | 0.36 | relevance, not difference |
| Overlap tracks hidden similarity (correlation) | -0.01 | – | 0.11 | 0.12 | higher |
| Poor matches truly below the traveller's median | – | – | 0.58 | 0.54 | higher |
| Poor matches truly in their top quarter (wrongly called poor) | – | – | 0.20 | 0.20 | lower |
| Low-confidence places truly in their top quarter (base rate 0.25) | – | – | 0.05 | 0.21 | near 0.25: unknown, not bad |
| Travellers with a place they didn't enjoy in their top 10 recommended | – | – | 0 | 0 | 0 |

**Honest uncertainty:** the gap between the engine's standardised score and the truth, by its own confidence level (lower is closer). If confidence means something, low should show the largest gap.

| Confidence | Old: gap (n) | New: gap (n) |
|---|---|---|
| low | 1.14 (46) | 1.11 (767) |
| medium | 0.96 (624) | 0.95 (1863) |
| high | 1.01 (1977) | 1.04 (3) |

**By archetype (mean Spearman):**

| Archetype | Population | Old | New |
|---|---|---|---|
| food | -0.17 | 0.22 | 0.20 |
| quiet | 0.34 | 0.46 | 0.38 |
| history | 0.12 | 0.37 | 0.36 |
| kids | 0.13 | 0.17 | 0.18 |
| budget | 0.37 | 0.07 | 0.07 |
| art | 0.38 | 0.38 | 0.39 |
| views | 0.36 | 0.27 | 0.28 |
| shopper | 0.02 | 0.02 | -0.01 |
| night | 0.08 | -0.02 | -0.10 |
| science | 0.23 | 0.25 | 0.25 |

**Classes over every judgement:**

| Class | Old | New |
|---|---|---|
| must_go | 0 | 0 |
| strong_match | 130 | 62 |
| good_discovery | 1007 | 799 |
| low_confidence | 47 | 766 |
| poor_match | 1458 | 1223 |
| not_suitable | 318 | 110 |

**What this can and can't show:**
- The truth is Claude's own construction (kinds and words to hidden attributes, GUESS weights). It's independent of the engine's code, not of Claude's judgement; a real traveller is the only real test.
- The engine sees only a handful of noisy answers; the place-by-place part of the truth (sd 0.5) is unrecoverable by design, so no engine should reach 1.
- Hidden tastes the person model has no feature for (art, science, shopping, nightlife, architecture) can be recovered only through places they loved or disliked.
