# Area 5 — Photo taste

**Decision:**
- **Not in v0** (D6).
- **For v1, a centroid or linear probe fitted on ~10 of a user's photos is *not* enough.** On benchmark data, a model fitted directly on 10 of a user's images did worse than a generic aesthetic model. Use a **generic aesthetic score plus a small personal offset shrunk towards zero**: a residual model, the same hierarchical logic as Area 3.
- **In v0, image models are only useful for tagging `photo_potential` on moments**, not for personal taste.
- **v1 cost: about 4 hours** (embeddings, generic score, pairwise personal offset). Optional v0 photo_potential check: about 1 hour.

## What exists (ranked)

| # | Name | Maturity | Licence | Why it matters |
|---|---|---|---|---|
| 1 | [open_clip](https://github.com/mlfoundations/open_clip) (CLIP, SigLIP, SigLIP2) | ★14.2k, last commit 2026-09-25, PyPI 3.3.0, Py ≥3.9 | MIT | One library for all the candidate embedding models. SigLIP2 models reach up to 84.1% ImageNet zero-shot |
| 2 | [LAION improved-aesthetic-predictor](https://github.com/christophschuhmann/improved-aesthetic-predictor) | ★1.3k, last commit 2023-10-12 (**stale**) | Apache-2.0 | A linear/MLP head on CLIP ViT-L/14 embeddings, trained on AVA + SAC + LAION-Logos. It predicts how much people like an image *on average*: the generic baseline |
| 3 | [DINOv2](https://github.com/facebookresearch/dinov2) | ★13.4k, last commit 2026-06-03 | Apache-2.0 (main weights) | Strong self-supervised features (80.8–87.0% ImageNet linear probe). An alternative embedding with no text side |
| 4 | FLICKR-AES (Ren et al., ICCV 2017) | Benchmark | Research | 40,000 Creative Commons Flickr images rated 1–5 by 210 workers. The standard personalisation test |
| 5 | PARA (Yang et al., CVPR 2022) | Benchmark | Research | 31,220 images, 438 raters, 9 objective + 4 subjective attributes, plus rater personality traits |
| 6 | VLM-latent PIAA (2026) | Research code | — | Simple linear models on vision-language hidden states personalise without fine-tuning. A cheaper route than training |

## What the evidence says

- **A generic model already captures most personal taste, and 10 examples add almost nothing.**
  - On FLICKR-AES, the generic aesthetic model's mean rank correlation with individual raters was **ρ=0.514**.
  - Personalising from **10** of the rater's own scores improved that by only **+0.006**; from **100**, by **+0.039**.
  - Predicting each person's scores *directly* from their 10 examples was **0.352 worse** than the generic model.
  - The residual approach (generic score + learned offset) was the only one that helped (Ren et al. 2017).
- **A raw centroid of 10 liked photos is a form of direct prediction.** The direct approach Ren et al. tested (a regressor fitted on the user's own images) failed; a centroid wasn't tested, but it has the same weakness of ignoring generic aesthetics. If photo taste comes back in v1, it must be a shrunken offset on a generic score. Learning it from pairwise "which do you prefer" choices fits naturally with the Area 3 model.
- **Personal taste does relate to content and aesthetic attributes.** Rater deviations from the generic score correlate with those attributes (Ren et al. 2017). Rater traits such as personality help predict personal taste (PARA). And VLM representations encode aesthetic attributes that simple linear models can use (2026).
- **`CLAUDE.md` is right to keep camera taste separate from experience taste.** Nothing here links photo taste to *enjoying* a place.

## Gaps we'd have to fill ourselves

- **No dataset of photos of *moments*.** `photo_potential` is founder-tagged. An optional check: run the LAION predictor over 3–5 public photos per moment and compare with Abram's tags (~1 h).
- **No evidence that camera taste predicts trip satisfaction.** Only our own data could show it.

## Risks / unknowns

- **User effort vs payoff.** Picking 10 photos plus 8–10 pairwise choices is real work for about +0.006 ρ at k=10. Consider dropping the optional photo pairs from Test A (Abram's call).
- **Privacy.** Personal photos can contain faces. Embed and discard: store no images, and never run face recognition. This is also relevant to Area 12.
- **The LAION predictor is stale (2023)** and trained on AVA/SAC. Its sense of "beautiful" may not fit London street moments.
