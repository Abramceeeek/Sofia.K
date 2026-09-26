# Area 8 — Seamless interaction (light scan)

**Decision:**
- **v0 runs on Telegram.** It is free, supports voice notes, and has inline buttons for one-tap ratings. Send **one rating prompt at the scheduled end of each moment**, never during one. Silence = fine, and a "rate later" batch runs at the end of the day.
- **No Live Activities in v0.** They need a native iOS app, which is out of scope.
- **WhatsApp waits for v1**, and only if Test A shows Telegram puts people off.
- **Cost: 0 extra hours.** This sits inside the onboarding and feedback estimates.

## What exists

| Name | Maturity | Cost / licence | Why it matters |
|---|---|---|---|
| Telegram Bot API (10.3) | Mature | **Free** | Inline keyboards appear right under a message, which makes one-tap 1–5 ratings easy. Limits: about 1 message/s per chat, 20/min in groups, about 30/s broadcast |
| WhatsApp Business Platform | Mature | **Per message since 1 Jul 2025** | Free-form replies inside a 24-hour window the user opened are **free**, as are utility templates in that window. Proactive templates are charged: UK marketing ≈ £0.038 per message and utility ≈ $0.022 (third-party figures; re-check in Phase 2) |
| iOS Live Activities (ActivityKit) | Mature | Native app only | Lock-screen card for up to 8 hours active + 4 more (12 hours maximum); 4 KB payload. Ideal for "next moment" cards, but out of v0 scope |
| Calm technology (Weiser & Brown 1995) | Design principle | — | Technology should inform without demanding focus, moving between the periphery and the centre of attention only when needed |

## What the evidence says

- **Even useful notifications disrupt.** Across 10,372 real notifications and 474 experience-sampling answers from 20 users, disruption depended on presentation, alert type, who sent it, and the *type, completion stage and complexity of the task the person was doing*. Even notifications with useful content disrupted (Mehrotra et al., CHI 2016). **So prompt at natural breakpoints (the end of a moment), deliver silently, and never interrupt a moment in progress.**

## Gaps / risks

- **Telegram bots can't see a user's background location**, so prompts go out on the plan's schedule rather than on arrival. The "reveal" moments that need a rating at the end of the approach will be approximate.
- **Channel preference in the UK is unverified.** Record which channel each Test A participant prefers.
- **WhatsApp costs for proactive messages.** Keep them inside the 24-hour user-opened window, e.g. the user taps "start my day" each morning.
