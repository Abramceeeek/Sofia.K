# Stage 2: the sample size, and the analysis agreed before any data (19 Nov 2026; provisionally approved 20 Nov)

Abram's decisions:
- **19 Nov §7:** provisionally 76 completed observations, if the assumptions support it, with the ten points below written down before the larger experiment starts.
- **20 Nov §9:** provisionally approved: 76 completers, 46 to pass, 65% expected, about 109 recruited at 70%.

**76 is the number of people who complete the blind choice, not the number recruited.**

**The friends' round is not statistical proof.** It is a usability run of the same build, read as direction only (D127). Its numbers feed only two inputs here: the completion rate (point 7) and σ_d (H2). They never count towards the 46.

## The record, in one place (Abram, 20 Nov §9)

| | |
|---|---|
| **Test** | one-sided exact binomial test |
| **Unit** | **one independent primary choice per completer:** the first, and only, blind gut choice of each install. The Brain gives one pair per install (point 8) |
| **H₀** | π ≤ 0.5: no preference for the personal plan |
| **H₁** | π > 0.5: the personal plan is preferred |
| **Primary outcome** | the gut choice ("Plan 1 or Plan 2?"), recorded before the reveal: personal or generic |
| **Sample** | **76 completers.** H₀ is rejected when **46 or more** choose the personal plan |
| **False-positive probability** | **0.0423** (exactly P(X ≥ 46 \| n = 76, π = 0.5); the nominal α is 0.05) |
| **Power** | **0.826 at π = 0.65**, the design point. 0.512 at π = 0.60, and 0.971 at π = 0.70 |
| **Dropout** | planning assumption: 70% of installs reach the gut choice, so **109 recruited**. 95 at 80%, 127 at 60%. **The friends' round's measured rate replaces the 70% before recruiting starts** |
| **Recomputed** | 20 Nov, with the command at the end: it prints `46 0.0423 0.826`, and 76 is the first n whose power stays at least 0.80 for ten n in a row |

**Freezing it.** This file, with the final completion rate and size filled in, is committed before the first Stage 2 invite. **Its commit id goes into the Stage 2 manifest.** Any change after that is a deviation, listed in the report with its reason. Until then, the numbers are provisional.

## The ten points

| # | Point | Decision |
|---|---|---|
| 1 | **Primary hypothesis** | H₀: π ≤ 0.5 against H₁: π > 0.5. π is the probability that a participant chooses the personal plan in the blind gut choice ("Plan 1 or Plan 2?", answered before the reveal) |
| 2 | **Null preference rate** | **0.5.** The pair is blind and its order random (stored per person), so with no real preference the choice is a coin flip. Position bias is balanced by the random order and checked (§ Sensitivity) |
| 3 | **Expected preference rate** | **The design point is 0.65.** Its basis:<br>• it's the smallest share worth acting on for Abram (about two people in three preferring ODYS's plan), which is a product judgement, and his to confirm;<br>• the model's own best case is about 0.68 (`brain-global-readiness.md`; simulated people, so an upper bound, not evidence);<br>• Stage 1's observed share is reported but **not** used to choose the design point: it is small, from friends, and would bias the choice towards whatever happened.<br>If Abram's smallest worthwhile share is 0.60, the size becomes 169 |
| 4 | **Significance level** | **α = 0.05**, exact one-sided binomial test. At n = 76 the test rejects when **46 or more** choose the personal plan. Its actual false-positive rate is 0.042, because the binomial is discrete |
| 5 | **Statistical power** | **0.80 at π = 0.65** (the exact power at n = 76 is 0.826). The same design has power 0.51 if the truth is 0.60, 0.93 at 0.68 and 0.97 at 0.70. For 0.90 power at 0.65: 102 completers |
| 6 | **One-sided or two-sided** | **One-sided.** Only "the personal plan is preferred" changes what ODYS does next. A two-sided test at the same power would need 97. A clear preference for the generic plan is reported plainly, as a finding, not hidden by the one-sided test |
| 7 | **Expected dropout** | **The 76 are completers.** Installs needed = 76 ÷ the completion rate up to the gut choice: 95 at 80%, **109 at 70%** (D2's threshold, the planning assumption), 127 at 60%, 152 at 50%. **Stage 1's measured completion rate replaces the 70%** before recruiting starts |
| 8 | **Independence** | **One pair per person.** The Brain gives one pair per install, and testers are asked to do it once and not to compare plans with anyone. Two limits are stated:<br>• one person could install twice on two phones. This is not detected, because invasive device fingerprinting is ruled out (Abram, 12 Nov). The tester code per channel bounds it;<br>• people recruited through someone else's share link may have similar tastes. Their share is reported, and H1 is re-run without them (§ Sensitivity) |
| 9 | **Primary outcome** | **The gut choice**, as recorded before the reveal: personal or generic. **Key secondary (H2):** the paired "this plan fits me" difference (personal − generic, each 1–5). One-sided paired t-test at α = 0.05, **tested only if H1 passes**, so the overall false-positive rate stays at 5%. The Wilcoxon signed-rank test is reported alongside |
| 10 | **Incomplete responses** | **A completed observation is a recorded gut choice.**<br>• People who stop earlier are counted at the step where they stopped (Test A's events), and are not in H1's denominator. **Nothing is imputed.**<br>• **A worst-case bound is reported beside H1:** everyone who saw both plans but didn't choose is counted as choosing the generic plan.<br>• H2 uses people with both "fits me" answers. A missing one excludes them from H2 only |

## H2's size, from Stage 1

n = ((z₀.₉₅ + z₀.₈₀) · σ_d / δ)² + z₀.₉₅² / 2, with δ = 0.5 points (Abram to confirm):

| Stage 1's σ_d | 0.8 | 1.0 | 1.2 | 1.5 |
|---|---|---|---|---|
| Completers needed for H2 | 18 | 27 | 37 | 57 |

**Stage 2's size = the larger of 76 (H1) and H2's.** For any σ_d up to about 1.7, that is 76. H2 needs more only if Stage 1's spread is larger than that.

## Exclusions (fixed now)

- Visitors from abroad: a separate cohort (D116).
- Installs with Abram's, the helper's or the rehearsal's tester codes.
- Anyone in Stage 1 (the friends' round): Stage 2 is strangers.

**Nothing else is excluded.** Each exclusion is counted in the report.

## Sensitivity checks (reported; none can turn a fail into a pass)

1. H1 among pairs whose two plans share no stop. When plans overlap, a choice says less.
2. H1 by which position the personal plan was shown in (Plan 1 or Plan 2). This is the position-bias check.
3. H1 without people who arrived through another tester's share link.
4. H1 by phone (iPhone or Android).
5. The worst-case bound in point 10.

## Rules for running it

- **One build,** frozen for the whole of Stage 2. Its commit, its TestFlight and Android build numbers and its planner settings go into the manifest before the first invite. **The planner is not changed during Stage 2.** That includes the fixed-effort change in `performance-study.md`: it goes in before Stage 2, or after it.
- **No interim test, and no stopping early on a good run.** Recruiting stops when 76 (or the larger H2 number) have completed the pair. That count doesn't depend on the answers, so stopping on it doesn't bias the result.
- **This file, with the final size filled in, is committed before the first Stage 2 invite.** The commit is the record. Any deviation is listed in the report with its reason.

## Commands (all exist today)

```text
python brain/scripts/testb_report.py validation/raw/export-<date>.json --code <Stage 2 code> --since <start>
python brain/scripts/evaluate_export.py validation/raw/export-<date>.json --code <Stage 2 code> --since <start>
python brain/scripts/learning_milestones.py validation/raw/export-<date>.json --code <Stage 2 code> --since <start>
```

**To re-check the numbers above**, run the exact binomial (n from 10 upward, and the first n where the power at π stays ≥ 0.80 for ten values of n in a row):

```text
python3 -c "from math import comb; t=lambda n,k,p: sum(comb(n,i)*p**i*(1-p)**(n-i) for i in range(k,n+1)); k=next(k for k in range(77) if t(76,k,.5)<=.05); print(k, round(t(76,k,.5),4), round(t(76,k,.65),3))"
```

It prints `46 0.0423 0.826`.

## Hours

| Item | Who | Hours |
|---|---|---|
| This document | Claude | done |
| The record above (20 Nov) | Claude | done |
| Filling in Stage 1's σ_d and completion rate | Claude | 0.5, after the friends' round |
| Confirming the 0.65 design point and δ = 0.5 | Abram | 0.25 |
| Recruiting about 110 strangers | Abram | the main cost; set at the checkpoint |
