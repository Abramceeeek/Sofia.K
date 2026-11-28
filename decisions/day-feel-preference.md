# "How would you like your days to feel?" (proposal, 24 Nov 2026)

**Decision first:** Abram decided to add an explicit shorter-day preference, **separate from activity pace** (24 Nov: "Someone can enjoy walking and still prefer a short day"), and to keep it as a **separate proposed feature**.
- **Built on the branch (m344):** the Brain honours it when a profile has it.
- **Not built yet:** nobody is asked it. Onboarding and the London gate are unchanged.
- **Abram approves the question and its place in onboarding before it's built in the apps.**

## The question

**How would you like your days to feel?**
- **Relaxed:** fewer experiences, more breathing room.
- **Balanced:** a mixture of experiences and rest. *This is also what an unanswered question means.*
- **Full:** make the most of the available day.

It's an optional profile answer (`day_feel`), changeable in You at any time. It is never inferred from activity, age or anything else.

## What the planner does with it (built, `brain/src/brain/api.py`, tested)

| Answer | Places a day | Extra places to fill the day | Stays |
|---|---|---|---|
| Relaxed | the person's number **minus one** (never fewer than one) | **none** | longer: the top of each place's range (as "a relaxed day", m200) |
| Balanced / unanswered | the person's number | up to 4, strong matches only (m335) | as now |
| Full | the person's number | up to **5**, strong matches only | as now |

Activity pace still sets journeys and strenuous stops (m329, m331). The two answers combine: "gentle and full" means many nearby, easy places; "full-on and relaxed" means fewer, active places with time between.

## The London gate: unchanged until Abram decides
- **G2 still fails** any day ending more than 45 min before the person's end time, whatever they chose. Abram: "Automatically accept early finishes for gentle travellers: No".
- **Proposal for Abram to decide:** for someone who chose **Relaxed**, G2 measures against the day they asked for: their end time, less an hour, with the free time said on the plan ("The rest of the day is yours from 16:30"). The early end stays visible in the gate's report either way.

## To build in the apps (after approval)
- **Where:** one question in onboarding, after pace, and the same choice in You.
- **Wording:** as above, in both apps.
- **The stops-before-the-first-plan count** (D118) goes up by one, or the question goes into "Improve future plans" instead, which is Abram's choice.
- **Hours (GUESS):** Claude ~3 h (both apps, screenshots, tests); Abram ~15 min to check the wording.
