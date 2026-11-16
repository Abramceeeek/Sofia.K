# The friends' round: plan, procedure and analysis (12 Nov 2026; m265)

The first real-user validation (Abram, m260: "the next meaningful product milestone"). **It runs on the frozen version and changes nothing in it.**
- **The fixed version:** `80a0da3`, TestFlight 91, Android 21 (`friends-round.md`).
- **The analysis plan:** `test-plan.md`, Test B.

This page adds the participant instructions, the procedure, what is collected, how success is judged, the limits, and the analysis.

## Who, and what they're told

- **Participants:** friends and people Abram knows, adults (18+), living in or near London. The aim is about 20 (D127). **They are a first usability group, not strangers:** results are read as direction, not proof (D127, m197).
- **The invite** (a message from Abram, plain words):
  > "I'm testing ODYS, an app that plans a day out around what you enjoy. It takes about 10 minutes to set up. You'll see two plans and pick one; then, if you can, try your plan on a day out and tap a quick rating after each stop. Type the code FRIENDS on the first screen. You can skip any question, and you can delete your data in the app at any time. Your answers help me see whether it's any good, so please be honest, including 'this isn't for me'."
- **Before they start:**
  - the consent screen (`app-2026-10-02`);
  - the privacy notice (`privacy-notice.md`);
  - nothing about the hypotheses, and no hint which plan is personal (the pair is blind).
- **Never asked for:** nationality, health, diet or anything sensitive (CLAUDE.md).

## The procedure

1. **Install:** TestFlight 91 on an iPhone, or the `android-latest` APK (build 21) on Android.
2. **Welcome screen:** type **FRIENDS**.
3. **Onboarding (about 10 minutes):**
   - where they're based;
   - 6 places;
   - 5 "this or that" days;
   - the Test A survey.
4. **The blind pair:**
   - Plan 1 and Plan 2: personal and generic, in random order (stored);
   - the gut choice;
   - "This plan fits me" for each;
   - "Which would be easier to actually do?" (optional);
   - why;
   - then the reveal.
5. **The day (optional; most valuable):** use the chosen plan on a real day out. Rate each stop (1–5). At the end, answer "worth it" and "do it again".
6. **Leaving:** "Delete my data" at any time, or simply stop.

**Abram's part:**
- send the invites and note the start date in the manifest;
- answer Help & safety messages (CLAUDE.md: a person, within a few hours);
- export once a week and at the end, into `validation/raw/`.

**The round ends, with its final export saved, by 29 Nov** (the free database expires on 6 Dec: `decisions/database-before-6-dec.md`).

## What is collected (already in build 91; nothing new)

| Data | Where | Used for |
|---|---|---|
| Onboarding answers, places, this-or-that choices | answers, swipes, conjoint_choices | the person's model; Test A |
| The pair: order, gut choice, "fits me" × 2, "easier", why | plans | **Test B** |
| Ratings after stops (1–5, "bring someone") | ratings | prediction against outcome (`evaluate_export.py`) |
| "Worth it", "do it again" | day_feedback | the money outcome (D127) |
| App events (screens, timings) | events | Test A's time and completion |

**Not collected:**
- names;
- locations (D123: on the phone only);
- food needs;
- anything the frozen build doesn't already ask.

## Success criteria (decided before the data: D2, D127, `test-plan.md`)

| Result | Keep-going signal | How it's read |
|---|---|---|
| **The gut choice** | at least 7 of 10 choose the personal plan | By chance alone this happens 17% of the time (D127). A signal, not proof |
| **"Fits me": personal minus generic, per person** | most differences above 0, with the bootstrap interval reported | Co-primary with the choice (D127) |
| **Overlap with the generic plan** | reported, not judged | When both plans share places, a preference says less |
| **Completion of onboarding** | reported | Test A: where people stop |
| **Ratings on a real day** | descriptive only | Too few stops to judge the model: see below |

## Exploratory against meaningful

- **About 20 friends can show:**
  - whether the app works for real people;
  - where it confuses them;
  - whether the personal plan is preferred often enough to keep going.
- **It cannot show:**
  - that ODYS works for strangers;
  - that the model is calibrated;
  - that the uncertainty-aware ranking helps. That ranking isn't in the frozen build at all.
- **What it can show about that ranking:** whether stops whose facts had a material open question on their day (hours not confirmed, no seasonal information) were rated lower than stops without one (`evaluate_export.py`, m268). That tests the ranking's premise, and starts setting its risk values from real ratings. The ranking itself needs a later comparison where people actually receive its plans.
- **Ratings from a handful of real days are read stop by stop.** `evaluate_export.py` says "exploratory only" below 30 rated stops.
- **Friends are kinder than strangers:** the strangers' round is where the bar applies (`test-plan.md`).

## Known limitations

- Small sample, friendly testers, London only, November weather.
- The generic plan is a fixed no-answers plan, so it isn't the strongest possible rival.
- Only people who use their plan on a real day give ratings.
- The free database must be saved before 6 Dec.
- Build 91 has none of the branch's later work: the offline view, "Why this stop?", the restricted share card and the uncertainty-aware ranking. The round tests the frozen app only.

## The analysis (after the final export)

```text
python brain/scripts/testb_report.py validation/raw/export-<date>.json --code FRIENDS --since <start date>
python brain/scripts/evaluate_export.py validation/raw/export-<date>.json --code FRIENDS --since <start date>
```

1. **Test B:** the choice (with the chance figure), the paired "fits me" difference, the overlap, the cases where the generic plan was chosen and why.
2. **Test A:** completion and time, and where people stopped.
3. **Predictions against outcomes:**
   - stop by stop: the match words against the ratings, and the day answers;
   - calibration only if 30 or more stops are rated.
4. **What people wrote:** the "why" answers and Help & safety messages, read in full.
5. **A short read-out for Abram**, then Checkpoint 3's decision. The raw export stays in `validation/raw/` (git-ignored); only the read-out's text is shared.

**Hours:** Claude ~1.5 h for the read-outs; Abram ~1 h a week during the round.
