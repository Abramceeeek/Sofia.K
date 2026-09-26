# Area 9 — Body signals (light scan)

**Decision:**
- **Out of v0 and Test A.** HealthKit needs a native iOS app, which v0 doesn't have.
- **When it comes back, use coarse, reliable signals only:** walking minutes or steps so far today, and a one-tap "rough night?". These act as fatigue covariates.
- **Don't use HRV for day-level decisions.** Wrist HRV is too noisy.
- **Cost: 0 hours now.** Later: about 6–8 hours plus a native app.

## What exists

| Name | Maturity | Why it matters |
|---|---|---|
| HealthKit | Mature, iOS only | Permission is granted per data type. By design, **an app cannot tell whether a user refused read access**: it just sees no data. So the app must work without it |
| Apple Watch HRV (SDNN) | Consumer | Series 9 / Ultra 2 vs a Polar H10 chest strap (39 adults, 316 measurements): HRV **underestimated by 8.31 ms, MAPE 28.9%**, outside the ±10 ms equivalence margin. Resting heart rate was accurate (MAPE 5.9%) |
| Consumer sleep trackers | Consumer | Against lab polysomnography (34 adults, 3 nights): they detect sleep well (sensitivity ≥0.93) but **detect wake poorly** (specificity 0.18–0.54), and are worse on disrupted nights (Chinoy et al. 2021) |

## What the evidence says

- **The HRV–fatigue link is lab-based and inconclusive.** A 140-person randomised trial found that HRV changed after a mental task but called its effectiveness for fatigue "inconclusive" (PLOS Mental Health 2025). Machine-learning fatigue classifiers from HRV are lab studies on ECG, not wrist data (e.g. Ni et al. 2022).
- **Resting heart rate and step counts are the trustworthy wearable signals.** HRV and sleep stages are not good enough to drive a planner.

## Gaps / risks

- **No evidence that wearable signals predict leisure enjoyment or trip fatigue.** Only our own per-moment ratings could show it.
- **Health data is special category data under UK GDPR** (Area 12). It needs explicit opt-in, a clear purpose and easy deletion, as `CLAUDE.md` requires, and probably a DPIA.
