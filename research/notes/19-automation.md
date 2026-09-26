# Area 19 — Automation: self-serve onboarding, AI support, auto-content (D44)

**Decision:**
- **Build three automations in Phase 4:** self-serve onboarding, an AI support agent with hard escalation rules, and content generated from moments and shot cards.
- **Cost: +14 founder hours** (3 + 6 + 5), so Phase 4 ≈ 52 h. Claude Code writes the code; Abram reviews and tests.
- **Effect** (workbook `Automation` tab, all inputs GUESS): at 1,000 active users and 100 sign-ups a month, founder time on onboarding, support and escalations falls from **~17.7 to ~5.3 h a month**.
- **Safety issues and complaints are never automated.**

## 1. Fully self-serve onboarding (≈3 h, after Phase 3)

- The Telegram bot runs the Test A flow itself: best hour, why they travel, swipes, the 10 "this or that" tasks, context, and read-back.
- **Read-back stays** (Area 1: the user confirms what was heard).
- **Fallbacks:** "type instead" whenever transcription fails; one nudge after 24 h of silence, then stop.
- **Monitoring:** a daily digest of failed extractions to Abram (≈0.5 min per sign-up budgeted), plus the weekly gold-set spot check (Area 1).

## 2. AI support agent with escalation (≈6 h)

| Message type | Who handles it | Target |
|---|---|---|
| How-to, plan questions, "why this stop?" | AI (Claude, same bot) | Immediate |
| Technical problem, payment or refund | **Queue for Abram**; the AI acknowledges and never promises money | Within 2 working days |
| **Safety** (feeling unsafe, harassment, injury, emergency) | **A human, promptly**: immediate alert to Abram or an agreed helper. The auto-reply gives emergency guidance (call 999) | Same hour where possible |
| **Complaint** about a plan, host, venue or the app | **A human, promptly** | Same day |
| Data request (access, deletion) | Abram, logged | Within the UK GDPR one-month limit |

- **Disclosure:** the first support message says it is an AI, and "type *person* to reach Abram" works at any point (CLAUDE.md: disclose AI; EU AI Act Art 50, Area 12).
- **Never proactive with money** (CLAUDE.md): the agent cannot refund, charge or change payments.
- **Test set before launch:** 20 red-team messages, including disguised safety cases. A missed safety escalation blocks release.
- **Cost:** tokens per contact are negligible at Haiku 4.5 prices (`economics/unit-economics.xlsx` → PriceTables).

## 3. Content from moments and shot cards (≈5 h)

- **Generator:** an LLM drafts a post from each moment record and shot card (what happens, best time, where to stand).
- **Images:** only Abram's own photos, or Wikimedia Commons files with their attribution. **Never Google 3D Tiles captures** (display only, Area 14).
- **Weekly review batch** (≈1 h a month), then automatic scheduling on **our own channels**:
  - a Telegram channel via the Bot API (Area 8);
  - an Instagram professional account via the Content Publishing API. Limit 100 API-published posts in 24 hours; JPEG only (Meta docs, read 2026-09-26).
- **Community-group posting stays manual.** Groups have their own rules, and minutes and sign-ups per post are a Phase 3 measure (D21).

## Risks / unknowns

- **"A human, promptly" needs cover.** With 7.5 h a week, safety alerts need an agreed helper or a stated response window. Helpers need the contributors agreement first (D38).
- **The AI resolution rate (70%) is a guess.** Log it from day one and re-fit the `Automation` tab.
- **Auto-content can drift into landmark lists**, the opposite of the product. The weekly review is the guard.
