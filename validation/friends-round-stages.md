# The friends' round as Stage 1, and a pre-registered Stage 2 (16 Nov 2026)

Abram's review of the audit, part 2 (12 Nov): "I want to know whether people actually prefer a personalised ODYS plan. Not whether the Brain thinks it is better. Not whether a synthetic benchmark says it is better."

- **Stage 1** is the friends' round as planned in `friends-round-plan.md`. It runs on the frozen build and changes nothing in it, read as a usability pilot.
- **Stage 2** is a larger round with strangers. Its hypotheses, outcomes, assumptions, sample size and analysis are fixed here, before any of its data exists.

## Stage 1: the usability pilot (no statistical claims)

**Nothing is added to the app or the round.** The pilot reads what build 91 already collects (`friends-round-plan.md`, "What is collected"), plus one optional thing for Abram to decide: a short debrief chat.

| Abram asked to find | Where it shows up in the round | How it's read |
|---|---|---|
| Confusing questions | Test A's events: where people stop or slow down, by screen; the survey's answers; the "why" text | A list of screens, each with the count of people who stopped there or took over twice the median time |
| Poor recommendations | ratings of 1–2; "fits me" of 1–2 for the personal plan; "not right" corrections on "So far" (D117); Help & safety messages | Each one read in full, with the stop, the person's answers and the plan's reasons side by side |
| Uncomfortable interactions | Help & safety messages; the "why" text; drop-outs after consent or the places | Read in full |
| Unexpected behaviour | the error alerts (no personal data in them); the rehearsal's 25 steps on both phones before invites; testers' messages | An issue log (below) |
| Personal against generic | the pair: choice, both "fits me", "easier", why; the overlap of the two plans | **Counts and quotes only**, no test statistic: for example, "12 of 18 chose the personal plan; the two plans shared 1 stop on average" |
| Whether people understand why places were picked | the "why" answers after the reveal; the debrief chat if Abram runs it | Whether their own words name what the reasons named |

**The optional debrief:**
- A 10-minute call or message exchange with 5 or 6 testers who finished the pair, after their day.
- The fixed questions:
  1. "Which screen made you hesitate?"
  2. "Why do you think it picked [their first stop]?"
  3. "What would have made the plan more useful?"
  4. "Anything that felt uncomfortable?"
- **Abram's decision:** these are interviews outside the app, so he checks they fall within the round's consent. Notes are kept without names, in `validation/raw/` (git-ignored), and are not data in the app.
- Cost: about 1 h of his time.

**The issue log** (`validation/stage1-issues.md`, written after the round):
- Each entry records:
  - what happened;
  - how many testers;
  - which phone;
  - the severity;
  - the fix and its hours.
- Severity levels:
  - **Blocker:** someone couldn't finish, or saw something wrong about money or safety;
  - **Major:** a wrong or poor plan, or a misleading word;
  - **Minor:** friction;
  - **Cosmetic.**
- Blockers and majors go into the next build before Stage 2.

**What Stage 1 never says:**
- that people prefer the personal plan;
- that the model is calibrated;
- that ODYS works for strangers.

At about 20 testers, "7 of 10" happens by chance 17% of the time, and "14 of 20" 6% of the time. A choice share of 60% has a 95% interval of about ±21 points.

**What Stage 1 gives Stage 2:**
- the spread of the paired "fits me" difference, which sets Stage 2's second sample size (below);
- the completion rate, which sets how many installs Stage 2 needs;
- the blockers fixed.

## Stage 2: the pre-registered validation (fixed before any Stage 2 data)

**Who:**
- Adults in or near London **who don't know Abram**, recruited as D109 sets out: app first, posts in travel, hiking and university groups.
- Visitors from abroad are a separate cohort and excluded (D116).
- One pair per person.

**What runs:**
- One build, frozen for the whole of Stage 2. Its commit, its TestFlight and Android build numbers, and the planner's settings are recorded in the manifest before the first invite.
- The blind pair as in build 91: personal against the fixed no-answers plan, random order, the same text format.
- m275's wording changes don't reach the pair, which shows nothing personal.

### Hypotheses

- **H1 (primary):** more than half of people choose the personal plan on the gut choice.
  - P(choose personal) > 0.5.
  - Exact one-sided binomial test, α = 0.05.
- **H2 (key secondary, tested only if H1 passes):** the personal plan "fits me" better than the generic one, by person.
  - The mean of (personal − generic) > 0, on the 1–5 scale.
  - One-sided paired t-test, α = 0.05.
  - The Wilcoxon signed-rank test is reported as a check.
  - Testing H2 only after H1 passes keeps the overall error at 5%.
- **Descriptive, with no test:**
  - "easier to actually do";
  - the overlap between the two plans;
  - for people who use their plan:
    - the share of rated stops Good or better;
    - "worth it" and "do it again";
    - the internal bands' calibration (`evaluate_export.py`, `learning_milestones.py`).

### Sample size

**For H1:** the smallest effect worth acting on is **Abram's decision**. The table gives the exact binomial sizes at 80% power, one-sided α = 0.05, computed for this document.

| If the true share choosing personal is | People who complete the pair | H1 passes if at least |
|---|---|---|
| 0.70 | 42 | 27 |
| 0.68 (the model's own ceiling: `brain-global-readiness.md`) | 51 | 32 |
| **0.65 (recommended design point)** | **76** | **46** |
| 0.60 | 169 | 96 |

**For H2:** n = ((z₀.₉₅ + z₀.₈₀) · σ_d / δ)² + z₀.₉₅² / 2.
- σ_d is the standard deviation of the paired difference, **measured in Stage 1**.
- δ = 0.5 points is the smallest difference worth acting on: a GUESS, for Abram to confirm.
- Examples:

| σ_d | δ | n |
|---|---|---|
| 1.0 | 0.5 | 27 |
| 1.2 | 0.5 | 37 |
| 1.5 | 0.5 | 57 |

**Stage 2's size is the larger of H1's and H2's**, fixed once Stage 1's σ_d is known and written into this file before the first invite.

**Installs needed:** completers divided by the completion rate. At D2's 70%, 76 completers need about **109 installs**. Stage 1's measured rate replaces the 70%.

### Analysis (one, at the planned size; no peeking)

1. Recruiting stops when the planned number has completed the pair. There is no interim test and no stopping on a good run.
2. **Exclusions, fixed now:**
   - testers who skipped the gut choice (from H1);
   - testers who skipped either "fits me" (from H2);
   - visitors from abroad;
   - installs with Abram's or the helper's tester codes.
   - Nothing else. Each exclusion is counted in the report.
3. **H1:** the exact test, with the share and its exact (Clopper–Pearson) 95% interval.
4. **H2:** if H1 passes, the paired test, with the mean difference and its 95% interval.
5. **Sensitivity checks** (reported, not decisive):
   - H1 among pairs that share no stop;
   - H1 by phone;
   - H1 by whether the person had used ODYS before Stage 2.
6. **Reported whatever the result:** a fail is written up as plainly as a pass, with the "why" answers of those who chose the generic plan.
7. **Deviations** from this plan are listed in the report with their reason. **The plan is frozen** by committing this file, with Stage 2's sizes filled in, before the first Stage 2 invite. The commit is the record. A public pre-registration (for example on OSF, free) is Abram's choice.

**Commands:** `testb_report.py` (H1 and H2: the pair, the choice and "fits me" exist already), `evaluate_export.py` and `learning_milestones.py`, all on the export with Stage 2's tester code and start date.

## Hours

| Item | Who | Hours |
|---|---|---|
| Stage 1 read-out and issue log | Claude | 3 |
| Stage 1 optional debrief | Abram | 1 |
| Fixing Stage 1's blockers and majors | Claude | unknown until the round; each costed in the log |
| Stage 2 sizes written in, plan frozen | Claude | 0.5 |
| Stage 2 recruiting and running about 110 installs | Abram | the main cost; set at Checkpoint 3 |
| Stage 2 analysis | Claude | 2 |
