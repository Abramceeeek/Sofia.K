# Post-experience questions: "Was it what you expected?" after the round, and "recommend" deferred (13 Nov 2026, updated 19 Nov; m267, m294)

**Decisions:**
- **Abram, m260:** investigate "Did this experience match what you expected?"; defer "Would you recommend this experience?" until it's shown to add information the existing signals don't. "Do not introduce redundant feedback questions simply to collect more data."
- **Abram, 19 Nov:** **prepare it for after the friends' round**, with three answers: "Better than expected", "About what I expected", "Worse than expected". It "measures the difference between what ODYS promised and what the person experienced".
  - It must be optional, and must never interrupt the planning experience.
  - It is never in the frozen experiment.
  - After the round, it is compared with rating, would bring someone, worth it and would do again, and kept only if it adds something.

**Nothing in this note is built.** It's the design for the first build after the round, and the test that decides whether it stays.

## 1. "Was it what you expected?"

**Why it isn't already measured:**
- The rating (1–5) says **how much they enjoyed** the stop.
- The expectation answer says **whether what ODYS told them matched what they found**: the hours, the price, the crowds, the walk, the feeling the card described.
- A stop can score 3 and be exactly what was described. Or it can score 4 after a queue nobody mentioned. Only this question separates the two.
- It tests the quality standard's fourth perspective, trustworthiness, from the person's side.

**The design (for the first build after the round):**

| | |
|---|---|
| **Where** | On the stop's rating sheet, under the 1–5 stars, as one optional row. Never its own screen, never a reminder, never during planning |
| **Words** | "Was it what you expected?" |
| **Answers** | "Better than expected" · "About what I expected" · "Worse than expected". One tap; skipping is the default, and the sheet closes as it does now |
| **Not asked** | "Why?" or any free text: a text box invites personal detail. Nothing about health, diet or anything sensitive |
| **Stored** | `ratings.expected`: `better` / `as_expected` / `worse` / empty. With the rating, deleted with it, in the export like `would_bring`. No new personal data |
| **Both apps** | iPhone and Android together (CLAUDE.md) |

**With the audit's one tap on what let a stop down** (`post-experience-feedback-proposal.md`, m285; also after the round):
- The sheet never shows more than two optional rows: this one after any rating, and m285's six taps **only after a 1 or 2**.
- If someone taps "Worse than expected" and then m285's "not as described", the second answer says *what* was different. Neither is ever required.
- Built together, they share the sheet's change, the export field work and the screenshots: about 1 h less than building them separately.

**What the read-out shows** (`evaluate_export.py`, from the first build that asks it):
1. **"Worse than expected" by the model's predicted band.** Since m275 the app shows no match words on the branch; the bands stay inside the Brain. "Worse" after a high predicted band is the costly case.
2. **"Worse than expected" by whether the stop's facts had a material open question that day** (m268: unconfirmed hours, an unknown price, no seasonal information). If unverified facts go with "Worse", that is real-user evidence for the uncertainty-aware ranking, which no synthetic benchmark can give.
3. **Its overlap with the existing signals:** rating, would bring someone, worth it, would do again.

**The test that decides whether it stays** (thresholds are GUESSES for Abram to set; read once **30 rated stops have an answer**):
- **It stays if either holds:**
  - **(a) It disagrees with the rating often enough to be new information:** at least 1 in 5 answers differs from what the rating implies. For example, "Worse than expected" on a 4 or 5, or "Better than expected" on a 1 or 2.
  - **(b) It tracks the facts:** "Worse than expected" is at least twice as common on stops with a material open question as on stops without one.
- **It goes if neither holds.** Then it is removed in the next build, and the note says so.
- "Would bring someone", "worth it" and "do again" are read alongside. If any of them already predicts "Worse" as well as the rating does, the question is redundant.

**Hours:** Brain ~1 h (the column, the export, the read-out, tests). iPhone and Android ~2 h. CI screenshots ~0.5 h. **About 3.5 h**, or about 2.5 h more if built with m285's tap row. After the round.

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

**After-9-Nov list:** both items wait for the round (#98 and #99). Abram reaffirmed on 19 Nov that "recommend" stays deferred.
