# Area 17 — On-device personalisation (light scan)

**Decision:**
- **Design now (~1 h inside Phase 4):**
  - Store b_population and δ_person **separately** in v0.
  - Make scoring a pure function: score(moment, b_population + δ_person).
  - Keep the Laplace update of δ self-contained.
  - Then δ can move onto a phone later without a redesign.
- **Build after Phase 3, and only with a native app.** v0 is a Telegram bot, which has no on-device compute.
- **For ~20 weights, on-device needs no federated-learning framework.** δ's posterior (a 20×20 Laplace/Newton update on the user's own ratings) runs in milliseconds on any phone. Estimate **8–12 h** on top of a native app.
- **Federated population updates with differential privacy** (DP): **20–30 h**. Only worth it at roughly **≥10k active users** (GUESS). Below that, DP noise swamps the signal. Until then, refit b_population centrally on consented, minimised data (ratings + conditions; no raw audio, D3).

## What exists

| # | Name | Maturity | Licence | Why it matters |
|---|---|---|---|---|
| 1 | Flower (`flwr` 1.38.0, 2026-09-22): 7.1k stars, active, Python ≥3.11 | Production | Apache-2.0 | Federated-learning framework with iOS (Core ML) client examples and DP examples |
| 2 | Opacus 1.6.0 (2026-05-05): 2.0k stars | Production | Apache-2.0 | DP-SGD for PyTorch. Overkill for a 20-weight model |
| 3 | Core ML `MLUpdateTask` (iOS 13+) | Production | Apple SDK | Updates a model on the user's device |
| 4 | Apple Foundation Models framework (iOS/macOS 26+) | Production | Apple SDK | On-device LLM with guided generation (typed structured output) and tool calling. Needs an Apple Intelligence device. Could run evidence extraction on the phone |

## What the evidence says

- **b_person = b_population + δ_person is personalised federated learning.** The Tan et al. (2021) survey gives the taxonomy. **Ditto** (Li et al. 2020) is exactly a global model plus regularised per-device models, and gains fairness and robustness across devices.
- **DP federated averaging works "given a sufficiently large number of users".** McMahan et al. (2017, arXiv) trained user-level-DP language models with negligible accuracy loss on large datasets. The cost falls on compute, not accuracy, *only* at scale. Our early user counts are far below that.

## Gaps / risks

- **Native app first.** On-device work presumes an iOS app, which is not in v0 or the Phase 4 36 h. The app itself is the big cost, UNVERIFIED and to be estimated when decided.
- **Device coverage.** Foundation Models needs Apple Intelligence hardware and iOS 26+, so a server fallback is still needed.
- **Privacy is a benefit, not a pitch.** Keeping δ on the device reduces the personal data we hold (UK GDPR minimisation). But ratings still reach the server for the population refit until federated updates exist, so the privacy notice must say so.
