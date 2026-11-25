# Moderated sessions with six travellers (draft for Abram, 24 Nov 2026)

**Decision first:** six one-to-one sessions of about 40 minutes, each with someone who travels differently, run by Abram on the QA build. They answer one question the synthetic travellers and AI reviews can't: **would a real person trust ODYS enough to follow its plan?**
- **They don't replace Test B.** Test B's blind Plan 1 / Plan 2 comparison stays the formative result (D127). These sessions find where people struggle.
- **They need the QA build** (`decisions/qa-build-path.md`). Day Feel, the one-tap rain swap and the free-time line exist only on the branch. Nothing is uploaded until Abram approves it.
- **Who:** people who aren't in the friends' round, so its testing conditions don't change. Start with people Abram knows. Strangers come only after the ICO fee re-check (D108).
- **Hours (GUESS):**
  - Abram: about 6 h (six sessions of 40 min, plus about 1.5 h to recruit and set up and 1 h to sum up);
  - Claude: about 1 h, to tally the results sheet into a summary, with the quotes kept word for word.

## Who to ask (one of each, so no single style dominates)

| # | Travelling style | Pace | Likely day feel |
|---|---|---|---|
| 1 | Solo, food-led, on a budget | medium | Full |
| 2 | A couple, museums and history | medium | Balanced |
| 3 | A parent planning for children | gentle | Balanced |
| 4 | Someone who wants a quiet day | gentle | Relaxed |
| 5 | Friends, lively, evenings out | full-on | Full |
| 6 | An older traveller, unhurried | gentle | Relaxed |

Ask about pace and day feel before the session only to choose who comes, never to steer what they pick in the app.

## Before the session (5 min)

**Read the consent script, and keep their "yes":**
- *"I'm testing an app I'm building, not you. There are no wrong answers. If something is confusing, that's the app's fault and exactly what I need to see."*
- *"I'll take written notes of what you do and say. I won't record audio or video unless you say yes now; if you do, the recording is deleted once my notes are typed up."* (Guardrail: transcribe, then delete raw recordings.)
- *"Your answers in the app go to ODYS's server, as for anyone using it. You can delete them in the app afterwards (You → Delete my data), and I'll do it with you if you like."*
- *"In an emergency on a real trip, always call 999."*

Use their own phone if the QA build is on it, otherwise Abram's. On the results sheet, note the app's version and build (shown in the app's settings) and the Brain commit (the QA Brain's `/v1/health` `version`, once per session day). The app doesn't show the Brain commit yet.

## The tasks (read each one word for word; don't show where to tap)

| # | Say | Done means |
|---|---|---|
| 1 | "Plan a trip to London that you'd really like to take: your own dates and how long." | A trip is created and its days are planned |
| 2 | "Tell it what you enjoy and how you like your days, as you would for yourself." | Onboarding answered, including how active and how full their days should be |
| 3 | "Have a look at your first full day. Tell me what you think of it as you go." | They've read the day; note their comments |
| 4 | "Pick one place you wouldn't go to, and replace it." | A stop is replaced and the rest of the day is kept |
| 5 | "Imagine it's raining on that day. Change the plan for the rain." | The rain option or a re-plan for rain is used |
| 6 | "How much will this day cost you, and is any of it a guess?" | They find the day's cost and say which prices are estimates |
| 7 | "It's 2 pm and you're tired. Change the rest of the day." | "Re-plan the rest of today" is used, or the day is changed another way |

**Moderating, so nobody is coached:**
- Only say: *"What would you do next?"*, *"What are you looking for?"*, *"What did you expect to happen?"*
- If they're stuck for **2 minutes**, give one hint and mark the task "with a hint". After **5 minutes**, mark it "not done" and move on.
- Don't explain features, defend the app, or agree or disagree with them.
- Time each task from the moment it's read to done, gave up or moved on.

## Afterwards (5 min): the scorecard

Each statement from 1 (strongly disagree) to 5 (strongly agree), read aloud, in this order:
1. The app understood what I enjoy.
2. The trip felt personalised to me.
3. I understood the costs and what was verified.
4. It was easy to make changes.
5. I would trust this plan on a real trip.
6. I would use ODYS for my next trip.
7. I would recommend ODYS to a friend.

Then one open question: **"What confused or disappointed you?"** Write the answer word for word.

## What goes on the results sheet (`results-template.md`)

- For each task: done unaided, done with a hint, or not done; the time taken; what confused them, word for word where possible.
- The seven scores and the open answer.
- **Only what the person did and said.** Abram's own impressions go in a separate column marked as his. No AI-written opinions, and nothing from the synthetic travellers or AI reviews, ever goes into this sheet as customer evidence.

## Reading the six sessions

- **A task more than two of six can't do unaided** is a defect to fix before strangers.
- **Statement 5 ("I would trust this plan") is the headline.** Report all six scores, not just an average: with six people a mean hides too much.
- **Report each person separately, by style.** Six people show where ODYS breaks; they don't measure how many would like it.
