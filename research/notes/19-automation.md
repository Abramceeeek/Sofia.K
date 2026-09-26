# Area 19 — Automation: self-serve onboarding, AI support, auto-content (D44, D45, D46)

**Decision:**
- **Build two automations in Phase 4:** self-serve onboarding, and an AI support agent with hard escalation rules.
- **Cost: +9 founder hours** (3 + 6), so Phase 4 ≈ 47 h. Claude Code writes the code; Abram reviews and tests.
- **Content from moments and shot cards moves to after v0** (D45). It still costs about 5 h when built.
- **Effect** (workbook `Automation` tab, all inputs GUESS): at 1,000 active users and 100 sign-ups a month, founder time on onboarding, support and escalations falls from **~17.7 to ~5.3 h a month**. That figure includes 1 h a month reviewing content, so it applies once content is built after v0.
- **Safety issues and complaints are never automated.** Abram handles safety alerts at the start, with a target of **within a few hours**. A **named backup helper** covers his working hours (D46).

## 1. Fully self-serve onboarding (≈3 h, Phase 4, after Phase 3)

- The Telegram bot runs the Test A flow itself: best hour, why they travel, swipes, the 10 "this or that" tasks, context, and read-back.
- **Read-back stays** (Area 1: the user confirms what was heard).
- **Fallbacks:** "type instead" whenever transcription fails; one nudge after 24 h of silence, then stop.
- **Monitoring:** a daily digest of failed extractions to Abram (≈0.5 min per sign-up budgeted), plus the weekly gold-set spot check (Area 1).

## 2. AI support agent with escalation (≈6 h, Phase 4)

| Message type | Who handles it | Target |
|---|---|---|
| How-to, plan questions, "why this stop?" | AI (Claude, same bot) | Immediate |
| Technical problem, payment or refund | **Queue for Abram**; the AI acknowledges and never promises money | Within 2 working days |
| **Safety** (feeling unsafe, harassment, injury, emergency) | **A person, never the AI alone** (D46): an immediate alert to Abram, and to the named backup helper during his working hours. The auto-reply says to call 999 in an emergency and that a person will reply within a few hours | **Within a few hours** |
| **Complaint** about a plan, host, venue or the app | Abram, or the backup helper | Same day |
| Data request (access, deletion) | Abram, logged | Within the UK GDPR one-month limit |

- **Disclosure:** the first support message says it is an AI, and "type *person* to reach Abram" works at any point (CLAUDE.md: disclose AI; EU AI Act Art 50, Area 12).
- **Never proactive with money** (CLAUDE.md): the agent cannot refund, charge or change payments.
- **Test set before launch:** 20 red-team messages, including disguised safety cases. A missed safety escalation blocks release.
- **Cost:** tokens per contact are negligible at Haiku 4.5 prices (`economics/unit-economics.xlsx` → PriceTables).

### Safety cover (D46)

- **Abram's hours:** Abram takes alerts outside work, with a target of within a few hours.
- **Work hours:** the backup helper takes alerts while Abram is at work. Write the hand-over times down, for example weekdays 9:00–17:30.
- **Before the helper takes any alert:**
  - a signed contributors agreement, including confidentiality (D38);
  - access to the alert channel only, not the whole database;
  - a one-page safety playbook, covering what counts as safety, when to tell the user to call 999, what to log, and when to hand back to Abram.
- **Founder hours:** ≈ 1 h. The playbook takes ≈ 0.5 h to review once Claude drafts it, and briefing the helper takes ≈ 0.5 h. This is part of the 6 h build.
- **Log every alert:** time received, time of the first human reply, and who replied. Check the "within a few hours" target monthly.
- **The same rule applies before v0.** In Test C, participants message Abram directly. The consent form now says to call 999 in an emergency and that Abram replies within a few hours. It names no backup, because none can act before the contributors agreement is signed.
- **Model hours:** the workbook counts safety and complaint time as founder time. Some of it will fall to the helper, so the model is conservative. The helper's on-call time is not modelled.

## 3. Content from moments and shot cards (≈5 h, **after v0**, D45)

- **Generator:** an LLM drafts a post from each moment record and shot card (what happens, best time, where to stand).
- **Images:** only Abram's own photos, or Wikimedia Commons files with their attribution. **Never Google 3D Tiles captures** (display only, Area 14).
- **Weekly review batch** (≈1 h a month), then automatic scheduling on **our own channels**:
  - a Telegram channel via the Bot API (Area 8);
  - an Instagram professional account via the Content Publishing API. Limit 100 API-published posts in 24 hours; JPEG only (Meta docs, read 2026-09-26).
- **Community-group posting stays manual.** Groups have their own rules, and minutes and sign-ups per post are a Phase 3 measure (D21).
- **Why after v0:** it brings users in but does not test the core idea. Its only modelled cost is the 1 h a month of review, because community posting stays manual.

## Risks / unknowns

- **The backup helper is the single point of failure during work hours.** If no helper is named by launch, the bot must say the reply may take until the evening.
- **The AI resolution rate (70%) is a guess.** Log it from day one and re-fit the `Automation` tab.
- **Auto-content can drift into landmark lists**, the opposite of the product. The weekly review is the guard.
