# Moderated sessions with six adult testers (for Abram; updated 25 Nov 2026, batch 6)

**Decision first:** six adults, each in a session of about 40 minutes, run by Abram on the QA build (`decisions/qa-build-path.md`). The roles are Abram's (25 Nov). Two sessions are run together, so that friends plan **one trip from their own phones and accounts**. They answer what synthetic travellers and AI reviews can't:
- **would a real person trust ODYS's plan?**
- **can two or three people create a trip together, each add their own preferences, and end with something they all want to do?** (Abram, 25 Nov)

**What these sessions are not:**
- **They don't replace Test B.** Test B's blind Plan 1 / Plan 2 comparison stays the formative result (D127). These sessions find where people struggle.
- **Only the QA build and the QA Brain.** Never the friends' round app, its TestFlight group or the production Brain. Nothing is uploaded or shared until Abram approves it, after the Apple policy check.
- **Who:** adults Abram knows who aren't in the friends' round. Strangers come only after the ICO fee re-check (D108).

**Hours (GUESS):**
- Abram: about 7 h. That is five sessions of 40 min (the friend pair together, at 60 min), about 1.5 h to recruit and set up, 30 min for the deletion steps, and 1 h to sum up.
- Claude: about 1 h, to tally the results into a summary with the quotes kept word for word.

## The six roles (Abram, 25 Nov)

| # | Role | What they do in the app | Pace |
|---|---|---|---|
| P1 | Solo traveller | Plans their own trip | as they say |
| P2 | Couple | Plans one trip for two ("Who's going": 2) | as they say |
| P3 | Parent or family organiser | Plans a family trip with **fictional children** (below) | gentle |
| P4 | Gentle traveller | Plans a quiet trip | gentle |
| P5 | Friend-group organiser | **Starts a shared trip** and sends the code | as they say |
| P6 | Invited friend | **Joins P5's trip** with the code, from their own phone | as they say |

**Rules for choosing and running them:**
- **Fictional children only (P3):** the parent enters made-up ages (for example 8 and 11), never their own children's details. Say: *"Please use made-up ages, not your own children's."* Children are never testers and nothing is collected about real children.
- **P5 and P6 each use their own phone and their own install,** so each is a separate account with their own answers. They sit apart and don't look at each other's screen until the shared plan is made. A third friend may join the same trip if one is free (the Brain holds up to six).
- **Pace and day feel:** ask about them before the session only to choose who comes, never to steer what they pick in the app.

## Before each session (5 min)

**Read the consent script, and note each "yes" on the results sheet** (initials only):
- *"I'm testing an app I'm building, not you. There are no wrong answers. If something is confusing, that's the app's fault and exactly what I need to see."*
- *"I'll take written notes of what you do and say, using a code (P1–P6), not your name."*
- **Separately, and only then:** *"Would you be happy for me to record the screen or audio as well? It's entirely up to you: saying no makes no difference to taking part. If you say yes, the recording is deleted within 7 days, once my notes are typed up."* (Guardrail: transcribe, then delete raw recordings.)
- *"Your answers in the app go to a test server that's separate from the real app. At the end, we'll delete them together in the app (You → Your data → Delete my data). The whole test server is deleted within 30 days of the last session, and my notes use your code, not your name."*
- *"Please don't put your name, phone number or email anywhere in the app, and don't use Help & safety for anything real today: it's a test copy and nobody is watching it."*
- For P5 and P6: *"You'll plan one trip together, each on your own phone. The app asks each of you to agree before your answers help plan it, and asks whether it may name you by a letter (Member A, Member B). Saying no is fine: you'll be counted, not named."*
- *"In an emergency on a real trip, always call 999."*

**On the results sheet, note:**
- the app's version and build (shown in the app's settings);
- the Brain commit (the QA Brain's `/v1/health` `version`, once per session day). The app doesn't show the Brain commit yet.

## The tasks (read each one word for word; don't show where to tap)

**Everyone (P1–P6):**

| # | Say | Done means |
|---|---|---|
| 1 | "Tell it what you enjoy and how you like your days, as you would for yourself." | Onboarding answered, including how active and how full their days should be |
| 2 | "Plan a trip to London that you'd really like to take: your own dates and how long." (P2: "…for the two of you". P3: "…for you and two children; use made-up ages".) | A trip is created and its days are planned |
| 3 | "Have a look at your first full day. Tell me what you think of it as you go." | They've read the day; note their comments |
| 4 | "Pick one place you wouldn't go to, and replace it." | A stop is replaced and the rest of the day is kept |
| 5 | "Imagine it's raining on that day. Change the plan for the rain." | The rain option or a re-plan for rain is used |
| 6 | "How much will this day cost, and is any of it a guess?" (P2, P3: "…for all of you, and for each person?") | They find the day's cost and say which prices are estimates. P2 and P3 also find each person's cost and the total |
| 7 | "It's 2 pm and you're tired. Change the rest of the day." | "Re-plan the rest of today" is used, or the day is changed another way |

**Then P5 and P6, together (about 20 min more):**

| # | Say | Done means |
|---|---|---|
| 8 (P5) | "Start a trip you'll plan together with your friend, and send them what they need to join." | A shared trip is started, P5 agreed, and the code reached P6 (by message, or read out) |
| 9 (P6) | "Your friend has asked you to join their trip. Join it." | P6 joined with the code and agreed on their own phone |
| 10 (P5 or P6) | "Now make the plan for your days together." | The shared days are planned |
| 11 (both) | "Is there something here for each of you? Tell me what you think, and why each place is there." | Note what each says. Did each find something they wanted? Did either feel the other's tastes took over? |
| 12 (P6) | "You've changed your mind. Leave the trip." | P6 left; P5 sees one member fewer |

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

**P5 and P6 also:**

8. The shared plan had something I really wanted to do.
9. My friend's tastes didn't take over the plan.
10. I was comfortable with what the others could see about me.

Then one open question: **"What confused or disappointed you?"** Write the answer word for word.

## Deletion, at the end of every session (Abram's step; the retention process is proposed below)

1. **With the participant, in the app:** You → Your data → Delete my data. This deletes everything on the QA Brain about that install, including their place in any shared trip. If P5 deletes first, the shared trip ends for everyone.
2. **Tick "deleted in the app"** on their results block.
3. **If a recording was made:** delete it once the notes are typed up, within 7 days, and write the date on the sheet.

## Retention and deletion (approved by Abram, 26 Nov; m360)

**These rules hold before the first session, and Abram follows them for every one.**

| Data | Kept | How it's deleted |
|---|---|---|
| Each participant's data in the QA Brain | Until the end of their session | With them, in the app: You → Your data → Delete my data. This removes everything about that install, including their place in a shared trip |
| The QA database (`odys-brain-qa-db`) | **Deleted within 30 days of the final session** | Abram deletes the database in Render. Render's free database also expires 30 days after it's made, so it can't outlive that |
| Raw audio or video recordings | **Deleted within 7 days** | Abram deletes each file once his notes are typed up, and writes the date on the results sheet |
| Research notes and the results sheet | De-identified as soon as possible | Participant codes (P1–P6) and initials only; no names, phone numbers or emails. Anything identifying written on the day is removed when the notes are typed up |
| The consent list (who P1–P6 are) | Until the summary is written (within 30 days of the last session) | Kept apart from the results, then deleted |
| Anonymous aggregate results | May be kept for product research | Counts, scores and de-identified quotes only |

**Conditions (Abram's):**
- **Recording is optional, with its own consent.** It's asked as a separate question after the main consent, and a "no" changes nothing else: the person still takes part. No recording without that yes.
- **The QA Brain and database are separate from production** (`render-qa.yaml`), and the QA apps can't reach the production Brain (`decisions/qa-build-path.md`).
- **Exports and backups:**
  - The QA Brain has **no backup job**. The nightly backup workflow seals the production Brain's database and runs only on `main`.
  - **Render's own backups of a free database: UNVERIFIED.** Abram checks the QA database's page in Render. Any backup there is deleted with the database, or at its own expiry, which he writes down.
  - Any export Abram takes from the QA Brain (`/v1/admin/export`) is a file on his own computer. He deletes it with the QA database, and writes down where it was kept.
- **Fictional child profiles only:** a parent enters made-up ages on "Who's going". No real child's details are ever entered, and children never take part.
- **Participant codes, not names,** in every research report.

## What goes on the results sheet (`results-template.md`)

- **For each task:** done unaided, done with a hint, or not done; the time taken; what confused them, word for word where possible.
- **The scores and the open answer.**
- **Only what the person did and said.** Abram's own impressions go in a separate column marked as his.
- **No AI-written opinions**, and nothing from the synthetic travellers or AI reviews, ever goes into this sheet as customer evidence. Claude's tally keeps participants' words apart from any AI review, under its own heading.

## Reading the six sessions

- **A task more than two of six can't do unaided** is a defect to fix before strangers.
- **For the shared trip (tasks 8–12), one failure is a defect:** there's only one pair.
- **Statement 5 ("I would trust this plan") is the headline.** For the shared trip, statements 8 and 9 are the headline. Report every score, not just an average: with six people a mean hides too much.
- **Report each person separately, by role.** Six people show where ODYS breaks; they don't measure how many would like it.
