# One trip, several people, one shared plan (proposal, 24 Nov 2026)

**Decision first:** build group trips for **people who already know each other** (friends, a couple, a family), in four steps, on top of the group planner that already exists (`brain/src/brain/group.py`, m240–m256). **Stranger matching stays out** (Abram, 24 Nov: "Do not launch stranger matching yet"; `CLAUDE.md`: companion matching is the critical untested assumption). Nothing here changes the friends' round.

**Hours (GUESS):**
- Claude ~35–45 h over four steps.
- Abram ~3 h: decisions and two reviews.
- Plus a DPIA update before any member's answers are stored (step 2).

## What exists today

`group.plan()` already chooses a shared itinerary for several members. Each member has their own tastes, budget, must-sees, rejections, access needs and days present. The rules:

| Requirement (Abram, 24 Nov) | Already there | Added on 24 Nov (m342) |
|---|---|---|
| Individual preference profiles | Each member's own taste model (`Scorer`); members are labels only ("Member A") | — |
| Different budgets | The plan's cost per person fits the **smallest** budget, day by day; unknown prices are never counted as free | — |
| Different activity levels | — | **The slowest stated pace holds for everyone:** with a gentle member, no strenuous stop, and the notes say "split up for that stop" |
| Preference conflicts | **A rejection is a veto.** Each member's first must-see is in, then turns. The choice among the rest uses **Nash welfare**, so one louder member can't take the trip (tested). | — |
| Fairness you can see | Proportionality and envy-freeness measured; each day's highlight **takes turns** ("Day 2 leads with Member B's pick") | **Every stop says who it suits:** "Among Member B's favourites; a good match for Member A and Member C." **Each member's share:** "2 of the 6 stops they're there for are among their favourites." |
| Access | A stated step-free need is a hard rule; unknown access is flagged, or excluded if asked | — |
| Partial attendance | Days present, joining part of a day | — |

**What it doesn't do yet:**
- **It's a prototype on the catalogue.** It picks places and days, but not timed days: no lunch, no journeys, no opening times. That's the job of the timed planner (`dayplan`), which plans for one person.
- **No accounts.** There is no membership, invitation, consent or storage; members exist only for the length of a call (m234).
- **No decisions.** Nobody can propose, approve or ask for a change.

## The design

### 1. People and data (privacy first)
- **A trip has an organiser and members.** Each member joins by an invite link and gives their own consent; joining never shares their install data.
- **A member's preferences stay theirs.** The places they loved or rejected, their budget band, pace and access needs are stored on their own record. Other members see only the shared plan and its "who it suits" lines, by label, never anyone's raw answers or budget.
- **Only what's needed is asked:** a short member onboarding of the 6 swipe places, budget band, pace, the day-feel preference if built (`decisions/day-feel-preference.md`) and access needs.
  - **Never** nationality, religion, health or a diet.
  - Food needs wait for the food DPIA (m323–m325).
- **Deleting a member** removes their answers. The plan keeps only what was decided, re-planned without their weights.

### 2. Planning a group day (joining the two planners)
- **The timed planner takes a group prize.** Each candidate's prize becomes a **weighted sum of members' utilities**, with weights that rise for whoever the trip has served least so far: proportional fairness, the day-by-day equivalent of Nash welfare.
  - Each member's satisfaction is recomputed after each day.
  - The hard rules are the same as today's: vetoes, the smallest budget, the slowest pace, step-free needs, a minimum age for families.
- **Each day still leads with one member's pick** (the turns above). Each stop carries its "who it suits" line, built in m342.
- **Split stops** (later): when no stop suits everyone at a time, offer "split for an hour". Two parallel stops meet again at the next shared stop. The notes already suggest it.

### 3. Decisions and approvals
- **Draft to agreed.** The organiser sees a draft. Each member can:
  - approve a day;
  - **ask for a change** to a stop, which re-uses "Other places for this time" (m336) with the group's prize;
  - reject a stop, which is a veto.
- **A day is agreed** when everyone there has approved it, or when the organiser closes it after a set time. Every change is listed with what it changes (`plan_change`, m336) and who asked, by label.
- **No vote ever moves money** (D39). Bookings and payments stay per person, on the provider's site, as today.

### 4. Safety
- **Friends only:** no discovery of other groups, no profiles of strangers, no matching.
- A shared trip is user-to-user content, so the **Online Safety Act** duties apply (illegal content and the reporting route). "Tell us" on every shared item, and safety alerts go to a person (D46).

## The plan, step by step

| Step | What | Claude | Abram |
|---|---|---|---|
| 1 | **Done (m342):** who each stop suits; each member's share; the slowest pace for everyone. Tested. | 1 h | — |
| 2 | A `TripGroup` with members, invites and consent; members' preferences stored on their own records; DPIA update; deletion. No planning change. | 8–10 h | 1 h (DPIA, wording) |
| 3 | The timed planner's group prize (proportional fairness, hard rules), behind a group trip only; the gate gains a four-friends group traveller (A food markets, B history, C relaxed, D adventure) with its own measures: fairness gap, each member's share, vetoes held | 12–15 h | 1 h (review the examples) |
| 4 | Decisions: approve, ask for a change, reject, closing a day; both apps | 14–18 h | 1 h |

**After step 4,** and only with real friends' groups tested, revisit open trips and companion discovery (after-9-Nov #104).
