# Phase 3 — Validation

Will strangers finish a conversational onboarding, prefer a plan built from it, use it, and pay? Nothing in Phase 4 is built until this passes (`KICKOFF_PROMPT.md`). Decisions D1–D4, D16, D18, D19, D21 and D23–D26 apply.

## Files

| File | What it is |
|---|---|
| `test-plan.md` | Tests A–D, virality (K), pass thresholds, analysis plan, risks |
| `recruitment-posts.md` | Separate posts for Tests A–C and Test D, the weekend-attendee invitation, and a post tracking table (D21) |
| `interview-script.md` | Word-for-word host script for Test A (Wizard of Oz on Telegram), then Tests B and C |
| `consent-form.md` | Plain-English consent: what's recorded, why, deletion after transcription (D3) |
| `privacy-notice.md` | UK GDPR notice for the study and the Test D waitlist |
| `conjoint/` | The 10 "this or that" tasks (`design.csv`) and the script that makes them |
| `test-d-landing/` | Test D landing page (static HTML): random £4.99 / £9.99 arm, £59.99 annual, waitlist only (D25) |
| `results-sheet.xlsx` | Where every result goes; the Summary tab scores against the thresholds, split by voice and text (D18) |
| `results.md` | *Checkpoint 3, written after the tests* |

## Flow per participant (12 target, 14 recruited)

1. **Recruit** (Post 1 or the weekend-trip invitation).
2. **Consent.**
3. **Test A:** onboarding chat on Telegram, voice or text. 20–30 min, can be spread over a day.
4. **Test B:** two plans, A/B blind. Pick one, rate both.
5. **Test C:** use the plan on a real day. Rate each stop, bring a friend, get a share prompt at the shot-card moment. Follow up for 2 weeks.

**Test D runs separately:** its own post and its own visitors. Study participants are tagged and excluded from Test D rates.

## Before the first participant (checklist)

- [ ] Abram confirms the conjoint attributes (`conjoint/README.md`) and the 16 swipe items (`interview-script.md` §3).
- [ ] At least 1 of the 5 seed moments is written up, for the example shot card (§6).
- [ ] ICO data protection fee: do the self-assessment (search: £52/year for tier 1). Pay if required before collecting data.
- [ ] Set up the Telegram account for the study (a separate account is cleaner); set up the Tally form and GoatCounter (`test-d-landing/README.md`).
- [ ] Put a contact email in the consent form, privacy notice and landing page.
- [ ] Copy `results-sheet.xlsx` to `validation/raw/results.xlsx` and fill in the copy. `validation/raw/` is git-ignored, and the template in the repo stays empty. **Never commit participant data.** Participant IDs P01–P20 and the Test B A/B labels are pre-filled.

## Founder hours (budget 15)

| Step | Est. (h) |
|---|---|
| Review materials; confirm conjoint and swipe items | 2.0 |
| Landing page, form and analytics set-up (Claude writes the code) | 1.0 |
| Recruitment: posts, replies, scheduling (log minutes per post) | 2.0 |
| Test A: run 12 chats (≈20 min of your time each, asynchronous) | 4.0 |
| Transcripts and read-back check (local transcription; Claude drafts the extraction) | 1.0 |
| Test B: generic plan once (0.5) + 12 personalised plans (≈15 min each, LLM-assisted) | 3.5 |
| Test C: follow-ups over 2 weeks and data entry | 2.0 |
| Analysis and `results.md` with Claude | 1.5 |
| **Total** | **≈ 17** |

That is **2 h over budget at 12 participants**, and each extra participant adds ≈ 0.8 h. The biggest single saving is not building plans by hand: the personalised plan is LLM-drafted from the extracted profile, and you only check it.
