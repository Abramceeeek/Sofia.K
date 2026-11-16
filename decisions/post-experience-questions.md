# Post-experience questions: "as expected?" after the round, and "recommend" deferred (13 Nov 2026; m267)

**Decisions (Abram, m260):**
- **Investigate "Did this experience match what you expected?"** It is built **after the friends' round**, outside the frozen Test B build. It must be optional, simple, quick, and separate from anything sensitive.
- **Defer "Would you recommend this experience?"** until it's shown to add information the existing signals don't. "Do not introduce redundant feedback questions simply to collect more data."

Nothing in this note is built. It is the design, and the test that decides.

## 1. "Did this experience match what you expected?"

**Why it isn't already measured:**
- The rating (1–5) says **how much they enjoyed** the stop.
- The expectation answer says **whether what ODYS told them matched what they found**: the hours, the price, the crowds, the walk, the feeling the card promised.
- A stop can score 3 and be exactly as expected ("Worth a try", and it was). Or it can score 4 after a queue nobody mentioned. Only this question separates the two. It tests the quality standard's fourth perspective, trustworthiness, from the person's side (`brain/src/brain/quality.py`).

**The design (proposed):**

| | |
|---|---|
| **Where** | On the stop's rating sheet, under the 1–5 stars, as a second optional line. Never its own screen, and never a reminder |
| **Words** | "Was it what you expected?" |
| **Answers** | "Better" · "About what I expected" · "Worse". One tap; skipping is the default |
| **Not asked** | "Why?" or any follow-up. A free-text box invites personal detail; tick-box reasons can come later if the answers show a pattern worth explaining |
| **Stored** | `ratings.expected`: `better` / `as_expected` / `worse` / empty. With the rating, deleted with it, in the export like `would_bring`. No new personal data |
| **Both apps** | iPhone and Android together (CLAUDE.md) |

**What the read-out would show** (`evaluate_export.py`, after the round's next build):
1. The share of "Worse", by the stop's match words ("A strong match" / "A good match" / "Worth a try"). "Worse" after "A strong match" is the costly case.
2. The share of "Worse" by how its facts were known: checked hours against unknown, a sourced price against an estimate. If unverified facts go with "Worse", that's evidence for the uncertainty-aware ranking.
3. Its overlap with the rating. If "Worse" is almost always a 1 or 2, the question adds little. Then it is dropped, by the same rule as below.

**Hours:** Brain ~1 h (the column, the export, the read-out, tests). iPhone and Android ~2 h. CI screenshots ~0.5 h. **About 3.5 h**, after the round.

## 2. "Would you recommend this experience?": deferred

**What already measures it:**
- **"Would you bring someone here?"** (`would_bring`, per stop): the closest stated signal, about the same place and a person they know.
- **The share card** (D114): a person who shares a rated moment is recommending it, by doing it. The funnel (shared → opened → onboarded) measures it (`GET /v1/admin/referrals`).
- The 1–5 rating, and the day's "worth it" and "do it again".

**The test before it's ever built (Claude's proposal; thresholds are GUESSES for Abram to set):**
1. **First, from data already collected:** after the round, compare `would_bring` with sharing, per stop (both apps send the moment with `share_sent`). If people who'd bring someone also share, the two existing signals agree, and a third stated one is unlikely to add much.
2. **Only if Abram wants more:** a one-off pilot of about 20 people, outside the frozen build, asked both questions on the same stops. "Recommend" earns a place only if **at least 1 in 5 of its answers disagrees** with what the rating (4–5) and `would_bring` together predict. At that point it would be measuring something else (for example, "good for others, not for me").
3. **If not:** it is not added, and the note says so.

**Hours:** step 1 ~0.5 h, inside the round's read-out. Step 2 ~2 h, only if chosen.

**After-9-Nov list:** both items wait for the round (#98 and #99).
